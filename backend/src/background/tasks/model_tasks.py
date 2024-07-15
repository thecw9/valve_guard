import asyncio
import logging
import pickle
from datetime import datetime

import numpy as np
from celery import Task
from scipy.interpolate import interp1d
from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.sql import insert, select, update
from src.background.celery_app import celery_app
from src.config import Config
from src.db import engine
from src.fd_model import GMM1D
from src.fd_model.gmm import GMM
from src.logger import Logger
from src.orm_model import Devices, Measures, TrainLogs
from src.services import data_service, nrmock_service

config = Config()
logger = Logger(__name__)


class ModelTrainTask(Task):
    def before_start(self, *args, **kwargs):
        super().before_start(*args, **kwargs)
        self.start_time = datetime.now()
        db = Session(engine)
        db.execute(
            insert(TrainLogs),
            [
                {
                    "task_id": self.request.id,
                    "task_name": str(self.name) + " for " + str(self.request.args[0]),
                    "start_time": self.start_time,
                    "args": self.request.args,
                    "kwargs": self.request.kwargs,
                }
            ],
        )
        db.commit()
        db.close()

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        super().after_return(status, retval, task_id, args, kwargs, einfo)
        self.end_time = datetime.now()
        runtime = (self.end_time - self.start_time).total_seconds()
        db = Session(engine)

        # retval is a Exception
        if isinstance(retval, Exception):
            retval = {"error": retval.__class__.__name__ + ": " + str(retval)}
        db.execute(
            update(TrainLogs),
            [
                {
                    "task_id": task_id,
                    "end_time": self.end_time,
                    "state": status,
                    "result": retval,
                    "runtime": runtime,
                }
            ],
        )
        db.commit()
        db.close()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc, task_id, args, kwargs, einfo)
        db = Session(engine)
        db.execute(
            update(TrainLogs),
            [
                {
                    "task_id": task_id,
                    "error_traceback": str(einfo.traceback),
                }
            ],
        )
        db.commit()
        db.close()


def interpolate_data(sensor_data: np.ndarray, target_length: int) -> np.ndarray:
    """Interpolate data"""
    x = np.arange(0, len(sensor_data))
    f = interp1d(x, sensor_data, kind="linear")
    x_new = np.linspace(0, len(sensor_data) - 1, target_length)
    y_new = f(x_new)
    return y_new


@celery_app.task(base=ModelTrainTask)
def train_model(key: int, start_time: datetime, end_time: datetime):
    """Train model"""
    db = Session(engine)

    data = data_service.get_history_data([key], start_time, end_time)
    data = data[key]
    model = GMM1D(config.GMM1D_N_COMPONENTS)

    # get current model version
    measures = db.query(Measures).filter(Measures.key == key).first()
    if not measures:
        logger.error(f"measure not found: {key}")
        raise ValueError(f"measure not found: {key}")
    current_model_version = measures.model_version

    # store trained model
    train_data = np.array(data).reshape(-1, 1)
    if len(train_data) < 2:
        logger.error(f"train data is too small: {len(train_data)}")
        raise ValueError("train data is too small")
    model.fit(train_data)
    print("model trained")
    model_binary = pickle.dumps(model)
    description = model.describe()
    threshold_down = description["threshold_down"]
    threshold_up = description["threshold_up"]

    db.execute(
        update(Measures),
        [
            {
                "key": key,
                "model": model_binary,
                "model_is_trained": True,
                "train_data_total": len(train_data),
                "model_name": model.__class__.__name__,
                "model_version": current_model_version + 1,
                "model_updated_at": datetime.now(),
                "threshold_up": threshold_up,
                "threshold_down": threshold_down,
            }
        ],
    )
    db.commit()

    # diagnose real-time data
    # data = nrmock_service.get_realtime_data_from_nrmock_service([key])
    data = data_service.get_realtime_data([key])
    process_data = []
    for key, value in data.items():
        process_data.append(
            {"key": key, "value": value, "time": datetime.now().isoformat()}
        )
    data = data_service.model_predict(process_data)
    response = data_service.store_measure_alarm_data(data)

    db.close()

    return {
        "status": f"Model trained successfully for measure: {key}",
        "train_data_total": len(train_data),
        "train_data_start_time": str(start_time),
        "train_data_end_time": str(end_time),
    }


@celery_app.task(base=ModelTrainTask)
def train_fusion_model(
    key: int,
    start_time: datetime,
    end_time: datetime,
):
    """Train fusion model"""
    db = Session(engine)

    # get measure keys need to be fused
    device = db.query(Devices).filter(Devices.key == key).first()
    if not device:
        logger.error(f"device not found: {key}")
        raise ValueError(f"device not found: {key}")
    device_key = device.key
    include = device.include
    exclude = device.exclude
    additional_include = device.additional_include
    additional_exclude = device.additional_exclude
    measure_keys = data_service.get_measure_keys(include, exclude)
    if additional_include:
        additional_measure_keys = data_service.get_measure_keys(
            additional_include, additional_exclude
        )
        measure_keys.extend(additional_measure_keys)

    # save measure keys
    device.measure_keys = measure_keys
    db.add(device)
    db.commit()

    # get history data
    data = data_service.get_history_data(measure_keys, start_time, end_time)
    max_length = max([len(data[key]) for key in measure_keys])
    data_list = []
    for key in measure_keys:
        if len(data[key]) == 0:
            logger.error(f"no data found for key: {key}")
            raise ValueError(f"no data found for key: {key}")
        data_list.append(interpolate_data(np.array(data[key]), max_length))
    data = np.array(data_list).T

    # train model
    model = GMM(n_components=3)
    model.fit(data)

    # save model
    data_to_save = {}
    model_binary = pickle.dumps(model)
    device.model = model_binary
    device.train_data_total = len(data)
    device.model_name = model.__class__.__name__
    device.model_version += 1
    device.model_updated_at = datetime.now()
    db.add(device)
    db.commit()

    # diagnose real-time data
    data = data_service.fusion_model_predict([key])
    response = data_service.store_device_alarm_data(data)

    db.close()

    return {"status": f"Model trained successfully for device: {device_key}"}
