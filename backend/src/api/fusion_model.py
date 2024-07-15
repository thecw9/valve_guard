import asyncio
import logging
import pickle
from datetime import datetime

import numpy as np
from celery import Task
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from scipy.interpolate import interp1d
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import insert, select, update
from src.background.celery_app import celery_app
from src.background.tasks.model_tasks import train_fusion_model
from src.config import Config
from src.db import engine
from src.dependencies import get_db
from src.fd_model import GMM1D
from src.fd_model.gmm import GMM
from src.logger import Logger
from src.orm_model import Devices, Measures, TrainLogs
from src.services import data_service, nrmock_service
from src.utils import get_realtime_data

from src import logger

router = APIRouter()
config = Config()
logger = Logger(__name__)


# train model
class TrainModelParams(BaseModel):
    keys: list[int] = [5000000000000000, 5000000000000001, 5000000000000002]
    start_time: datetime = datetime(2021, 1, 1)
    end_time: datetime = datetime.now()


@router.post("/train")
async def train_fusion_model_background(
    params: TrainModelParams,
    db: Session = Depends(get_db),
):
    """Train model"""
    keys = params.keys
    start_time = params.start_time
    end_time = params.end_time
    print(params)

    for key in keys:
        print(key)
        train_fusion_model.delay(key, start_time, end_time)

    return {"code": 200, "message": "Model training started"}


class PredictParams(BaseModel):
    keys: list[int] = [5000000000000000, 5000000000000001, 5000000000000002]


@router.post("/predict")
async def predict_fusion_model(
    params: PredictParams,
    db: Session = Depends(get_db),
):
    """
    Predict
    """
    # TODO: need to optimize
    return_data = []
    model_not_exist = []
    for key in params.keys:
        # get device by key
        device = db.execute(
            select(Devices).where(Devices.key == key)
        ).scalar_one_or_none()
        if not device:
            continue

        # get data
        if not device.measure_keys:
            return_data.append(
                {
                    "key": key,
                    "time": datetime.now(),
                    "status": config.ALARM_STATUS["UNKNOWN"],
                    "type": 1,
                }
            )
            continue
        data = get_realtime_data(device.measure_keys, db)
        data = [data[key] for key in device.measure_keys]
        data = np.array(data)

        # load model
        if not device.model:
            model_not_exist.append(key)
            return_data.append(
                {
                    "key": key,
                    "time": datetime.now(),
                    "status": config.ALARM_STATUS["UNKNOWN"],
                    "type": 1,
                }
            )
            continue
        model = pickle.loads(device.model)
        data = data.reshape(1, -1)
        predict_result = model.predict(data)
        status = (
            config.ALARM_STATUS["NORMAL"]
            if predict_result[0] == 0
            else config.ALARM_STATUS["ALARM"]
        )
        return_data.append(
            {
                "key": key,
                "time": datetime.now(),
                "status": status,
                "type": 1,
            }
        )
    if model_not_exist:
        logger.warning(f"Flowing model not exist: {model_not_exist}")

    return {
        "code": 200,
        "message": "Predict success",
        "data": return_data,
    }
