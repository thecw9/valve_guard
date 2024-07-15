from typing import Dict
import shlex
import re
import subprocess
from sympton_utils import get_all_symptoms, get_realtime_symptoms
from download_and_run import download_and_run
import json
from io import StringIO
from sqlalchemy import select, and_, or_, insert, update, union_all, column, func
import config
from minio import Minio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from uuid import uuid4
from typing_extensions import Optional
from fastapi import (
    Body,
    FastAPI,
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from pydantic import BaseModel
from database import db, model_info_collection, predict_result_collection

app = FastAPI()
app.title = "Model API"

all_symptoms = get_all_symptoms()
print(all_symptoms)
try:
    model_info_collection.create_index("key", unique=True)
    model_info_collection.insert_many(all_symptoms)
except Exception as e:
    print(e)


class TrainModelParams(BaseModel):
    key: str = "ShaoShang.Pole1Low.Sound.Channel1.ImpulseFactor"
    name: str = "gmm"
    start_time: Optional[datetime] = datetime.now() - timedelta(days=1)
    end_time: Optional[datetime] = datetime.now()


@app.post("/model/train/")
async def train_model(
    train_model_params: TrainModelParams = Body(...),
):
    minio_client = Minio(
        config.MINIO_ENDPOINT,
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        secure=False,
    )
    bucket_name = config.BUCKET_NAME

    # save model to minio
    if train_model_params.name == "gmm":
        train_model_file = "./fd_models/gmm.py"
        predict_model_file = "./fd_models/gmm.py"
        train_args = f"--key {train_model_params.key} --mode train"
        predict_args = f"--key {train_model_params.key} --mode predict"
        if train_model_params.start_time and train_model_params.end_time:
            train_args += f" --start_time {train_model_params.start_time.isoformat()}"
            train_args += f" --end_time {train_model_params.end_time.isoformat()}"
    else:
        return {"code": 400, "msg": "model_name not supported"}

    train_model_file_object_name = f"models/{train_model_params.key}/{uuid4()}.py"
    predict_model_file_object_name = f"models/{train_model_params.key}/{uuid4()}.py"
    try:
        minio_client.fput_object(
            bucket_name, train_model_file_object_name, train_model_file
        )
        minio_client.fput_object(
            bucket_name, predict_model_file_object_name, predict_model_file
        )
    except Exception as e:
        return {"code": 400, "msg": str(e)}

    # train model
    process = download_and_run(
        bucket_name=bucket_name,
        object_name=train_model_file_object_name,
        params_command_str=train_args,
    )
    pattern = r"\{.*?\}"
    try:
        res = re.findall(pattern, process.stdout)[-1]
    except Exception:
        return {"code": 400, "msg": f"train model failed: {process.stderr}"}
    res = res.replace("'", '"')
    res = json.loads(res)

    # update model info in database
    model_info_collection.update_one(
        {"key": train_model_params.key},
        {
            "$set": {
                "name": train_model_params.name,
                "train_model_file": train_model_file_object_name,
                "predict_model_file": predict_model_file_object_name,
                "train_args": train_args,
                "predict_args": predict_args,
                "current_status": res.get("status"),
                "time": datetime.now(),
                "model_train_stdout": process.stdout,
                "model_train_stderr": process.stderr,
            }
        },
        upsert=True,
    )


class UpdateArgsParam(BaseModel):
    key: str = "ShaoShang.Pole1Low.Sound.Channel1.ImpulseFactor"
    train_args: str = (
        "--key ShaoShang.Pole1Low.Sound.Channel1.ImpulseFactor --mode train"
    )
    predict_args: str = (
        "--key ShaoShang.Pole1Low.Sound.Channel1.ImpulseFactor --mode predict"
    )


@app.post("/model/update_args/")
async def update_args(update_args_param: UpdateArgsParam = Body(...)):
    key = update_args_param.key
    train_args = update_args_param.train_args
    predict_args = update_args_param.predict_args

    # retrain model
    bucket_name = config.BUCKET_NAME
    model_info = model_info_collection.find_one({"key": key})
    if not model_info:
        return {"code": 400, "msg": f"model {key} not found"}
    train_model_file_object_name = model_info["train_model_file"]
    process = download_and_run(
        bucket_name=bucket_name,
        object_name=train_model_file_object_name,
        params_command_str=train_args,
    )
    pattern = r"\{.*?\}"
    try:
        res = re.findall(pattern, process.stdout)[-1]
    except Exception:
        return {"code": 400, "msg": f"train model failed: {process.stderr}"}
    res = res.replace("'", '"')
    res = json.loads(res)

    # update model info in database
    model_info_collection.update_one(
        {"key": key},
        {
            "$set": {
                "train_args": train_args,
                "predict_args": predict_args,
                "current_status": res.get("status"),
                "time": datetime.now(),
                "model_train_stdout": process.stdout,
                "model_train_stderr": process.stderr,
            }
        },
        upsert=True,
    )


class ModelQueryParam(BaseModel):
    include: str = "韶山站&声音&通道1 | 韶山站&声音&通道2"
    exclude: Optional[str] = None


@app.post("/model/info")
async def get_model_info(model_query_param: ModelQueryParam = Body(...)):
    include = model_query_param.include
    exclude = model_query_param.exclude
    include = (
        model_query_param.include.replace(" ", "")
        .replace("AND", "&")
        .replace("OR", "|")
    )
    exclude = model_query_param.exclude
    if exclude:
        exclude = exclude.replace(" ", "").replace("AND", "&").replace("OR", "|")

    query = {}
    if include:
        or_items = []
        for item in include.split("|"):
            and_items = []
            for sub_item in item.split("&"):
                and_items.append({"path": {"$regex": sub_item}})
            or_items.append({"$and": and_items})
        query["$or"] = or_items
    if exclude:
        and_items = []
        for item in exclude.split("&"):
            and_items.append({"path": {"$not": {"$regex": item}}})
        query["$and"] = and_items

    model_info = model_info_collection.find(query)
    model_info = [{**item, "_id": str(item["_id"])} for item in model_info]
    print(list(model_info))
    return {
        "code": 200,
        "msg": "success",
        "data": list(model_info),
    }


@app.get("/model/info/{key}")
async def get_model_info_by_key(key: str):
    model_info = model_info_collection.find_one({"key": key})
    if not model_info:
        return {"code": 400, "msg": "model not found"}
    model_info["_id"] = str(model_info["_id"])
    return {"code": 200, "msg": "success", "data": model_info}


# predict
@app.post("/model/predict/")
async def predict_model(key: str = "ShaoShang.Pole1Low.Sound.Channel1.ImpulseFactor"):
    # query model info in database
    model_info = model_info_collection.find_one({"key": key})
    if not model_info:
        return {"code": 400, "msg": "model not found"}
    print(model_info)
    if model_info.get("predict_model_file") is None:
        return {"code": 400, "msg": "model not trained yet"}

    bucket_name = config.BUCKET_NAME
    process = download_and_run(
        bucket_name=bucket_name,
        object_name=model_info["predict_model_file"],
        params_command_str=model_info["predict_args"]
        + f" --value {get_realtime_symptoms(key)}",
    )
    if process.returncode != 0:
        return {"code": 400, "msg": f"predict model failed: {process.stderr}"}
    pattern = r"\{.*?\}"
    try:
        res = re.findall(pattern, process.stdout)[-1]
    except Exception:
        return {"code": 400, "msg": f"train model failed: {process.stderr}"}
    res = res.replace("'", '"')
    res = json.loads(res)

    # save predict result to database
    predict_result_collection.insert_one(
        {
            "key": key,
            "time": datetime.now(),
            "status": res.get("status"),
            "predict_result": res,
            "predict_model_stdout": process.stdout,
            "predict_model_stderr": process.stderr,
        }
    )

    # update model info in database
    model_info_collection.update_one(
        {"key": key},
        {
            "$set": {
                "current_status": res.get("status"),
                "time": datetime.now(),
            }
        },
    )

    return {"code": 200, "msg": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8054)
