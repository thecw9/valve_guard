import pickle
from datetime import datetime

import numpy as np
from src import logger
from src.logger import Logger
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import Config
from src.dependencies import get_db
from src.background.tasks.model_tasks import train_model
from src.orm_model import Measures

router = APIRouter()
config = Config()
logger = Logger(__name__)


# train model
class TrainModelParams(BaseModel):
    keys: list[int] = [4222125033390086, 4222125027229703, 4222125027295239]
    start_time: datetime = datetime(2021, 1, 1)
    end_time: datetime = datetime.now()


@router.post("/train")
async def train_model_background(
    params: TrainModelParams,
):
    """Train model"""
    keys = params.keys
    start_time = params.start_time
    end_time = params.end_time

    for key in keys:
        train_model.delay(key, start_time, end_time)

    return {"code": 200, "message": "Model training started", "data": None}


class TrainModelParams(BaseModel):
    start_time: datetime = datetime(2021, 1, 1)
    end_time: datetime = datetime.now()


@router.post("/train/all")
async def train_all_model_background(
    params: TrainModelParams,
    db: Session = Depends(get_db),
):
    """Train all model"""
    start_time = params.start_time
    end_time = params.end_time

    statement = select(Measures)
    result = db.execute(statement).scalars().all()
    keys = [item.key for item in result]
    for key in keys:
        train_model.delay(key, start_time, end_time)

    return {"code": 200, "message": "All model training started", "data": None}


# predict
class PredictParams(BaseModel):
    key: int = 4222125033390086
    value: float = 0.1
    time: datetime = datetime.now()


@router.post("/predict")
async def predict(
    input_data: list[PredictParams],
    db: Session = Depends(get_db),
):
    """Predict"""
    data = []
    model_not_found = []
    # TODO: need to optimize
    for param in input_data:
        key = param.key
        value = param.value
        time = param.time

        statement = select(Measures).where(Measures.key == key)
        result = db.execute(statement).scalars().first()
        if not result or not result.model:
            model_not_found.append(key)
            data.append(
                {
                    "key": key,
                    "value": value,
                    "time": time,
                    "status": config.ALARM_STATUS["UNKNOWN"],
                    "type": 0,
                }
            )
            continue
        model = pickle.loads(result.model)
        prob = model.predict_proba(np.array(value).reshape(-1, 1))
        threshold = model.threshold_ if hasattr(model, "threshold_") else None
        status = model.predict(np.array(value).reshape(-1, 1))
        status = (
            config.ALARM_STATUS["NORMAL"]
            if status[0] == 0
            else config.ALARM_STATUS["ALARM"]
        )
        data.append(
            {
                "key": key,
                "value": value,
                "time": time,
                "status": np.squeeze(status).tolist(),
                "type": 0,
            }
        )

    if model_not_found:
        logger.info(f"Flowing models not found: {model_not_found}")
    return {
        "code": 200,
        "message": "success",
        "data": data,
    }


# describe model
class ModelDescribeParams(BaseModel):
    key: int = 4222125033390086


@router.post("/describe")
async def describe_model(
    params: ModelDescribeParams,
    db: Session = Depends(get_db),
):
    """Describe model"""
    key = params.key

    statement = select(Measures).where(Measures.key == key)
    result = db.execute(statement).scalars().first()
    if not result or not result.model:
        raise HTTPException(status_code=404, detail="model not found")
    model = pickle.loads(result.model)
    description = model.describe()
    data = {
        "key": key,
        "description": description,
    }

    return {
        "code": 200,
        "message": "success",
        "data": data,
    }
