from datetime import datetime
from typing import Any

import aiohttp
import numpy as np
import requests
from fastapi import HTTPException

from src import Config

config = Config()


def get_measure_keys(
    include: str,
    exclude: str,
) -> list[int]:
    """
    Retrieve measure keys by keyword

    Args:
        include (list[str]): keywords to include
        exclude (list[str]): keywords to exclude

    Returns:
        list[int]: measure keys
    """
    json_input = {
        "include": include,
        "exclude": exclude,
    }
    response = requests.post(
        config.DATA_SERVICE_URL + "/measures-service/info",
        json=json_input,
    )
    result = response.json()
    keys = [item["key"] for item in result["data"]]
    return keys


def get_all_devices_keys() -> list[int]:
    """
    Retrieve all devices keys

    Returns:
        list[int]: devices keys
    """
    json_input = {"include": "", "exclude": ""}
    response = requests.post(
        config.DATA_SERVICE_URL + "/devices-service/info",
        json=json_input,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get devices keys")
    result = response.json()
    keys = [item["key"] for item in result["data"]]
    return keys


def get_history_data(
    keys: list[int],
    start_time: datetime,
    end_time: datetime,
) -> dict[int, list[float]]:
    """
    Retrieve history data from data service

    Args:
        keys (list[int]): measure keys
        start_time (datetime): data start time
        end_time (datetime): data end time

    Returns:
        dict[int, list[float]]: history data with measure key as key and data as value
    """
    iso_start_time = start_time.isoformat()
    iso_end_time = end_time.isoformat()
    json_input = {
        "keys": keys,
        "start_time": iso_start_time,
        "end_time": iso_end_time,
    }
    response = requests.post(
        config.DATA_SERVICE_URL + "/measures-service/history",
        json=json_input,
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail=f"Failed to get history data, {response.json()}"
        )

    result = response.json()
    resp_data = result["data"]

    # TODO: optimize this

    # data = {}
    # for item in resp_data:
    #     key = item["key"]
    #     value = [i["value"] for i in item["data"]]
    #     data[key] = value

    # DONE: optimize this
    data = {item["key"]: [i["value"] for i in item["data"]] for item in resp_data}

    return data


def get_realtime_data(keys: list[int]) -> dict[int, float]:
    """
    Retrieve realtime data from data service

    Args:
        keys (list[int]): measure keys

    Returns:
        dict[int, float]: realtime data with measure key as key and data as value
    """
    input_json = {"keys": keys}
    response = requests.post(
        config.DATA_SERVICE_URL + "/measures-service/realtime",
        json=input_json,
    )
    result = response.json()

    # TODO: optimize this

    # data = {}
    # for item in result["data"]:
    #     key = item["key"]
    #     value = item["value"]
    #     data[key] = value

    # DONE: optimize this
    data = {item["key"]: item["value"] for item in result["data"]}
    return data


def store_realtime_data(data: list[dict]) -> dict:
    """Store realtime data.

    Args:
        data (dict): Realtime data.

    Returns:
        dict: Response data.
    """
    if not config.DATA_SERVICE_URL:
        raise ValueError("DATA_SERVICE_URL is not set.")

    url = config.DATA_SERVICE_URL + "/measures-service/realtime/store"
    response = requests.post(url, json=data).json()

    return response


def model_predict(data: list[dict]) -> list[dict]:
    """
    Model predict.

    Args:
        data (list[dict]): Model predict data. Each item is a dict with keys: key, time, value.

    Returns:
        list[dict]: Model predict result. Each item is a dict with keys: key, time, value, status, type.
    """
    if not config.DATA_SERVICE_URL:
        raise ValueError("DATA_SERVICE_URL is not set.")

    url = config.DATA_SERVICE_URL + "/model-service/predict"
    try:
        response = requests.post(url, json=data).json()
    except Exception as e:
        raise ValueError(str(e))

    if not response["code"] == 200:
        raise ValueError(response["message"])

    return response["data"]


def fusion_model_predict(device_keys: list[int]) -> list[dict[int, Any]]:
    """
    Fusion model predict.

    Args:
        device_keys (int): Device key.

    Returns:
        list[dict]: Fusion model predict result. Each item is a dict with keys: key, time, status, type.
    """
    if not config.DATA_SERVICE_URL:
        raise ValueError("DATA_SERVICE_URL is not set.")

    url = config.DATA_SERVICE_URL + "/fusion-model-service/predict"
    try:
        response = requests.post(url, json={"keys": device_keys}).json()
    except Exception as e:
        raise ValueError(str(e))

    if not response["code"] == 200:
        raise ValueError(response["message"])

    return response["data"]


def store_measure_alarm_data(data: list[dict]) -> None:
    """
    Store measure alarm data.

    Args:
        data (list[dict]): Measure alarm data. Each item is a dict with keys: key, time, value, status.
    """
    if not config.DATA_SERVICE_URL:
        raise ValueError("DATA_SERVICE_URL is not set.")

    url = config.DATA_SERVICE_URL + "/alarm-service/measure/store"
    response = requests.post(url, json=data).json()

    if not response["code"] == 200:
        raise ValueError(response["message"])


def store_device_alarm_data(data: list[dict]) -> None:
    """
    Store device alarm data.

    Args:
        data (list[dict]): Device alarm data. Each item is a dict with keys: key, time, status.
    """
    if not config.DATA_SERVICE_URL:
        raise ValueError("DATA_SERVICE_URL is not set.")

    url = config.DATA_SERVICE_URL + "/alarm-service/device/store"
    response = requests.post(url, json=data).json()

    if not response["code"] == 200:
        raise ValueError(response["message"])


if __name__ == "__main__":
    keys = get_measure_keys("高抗A相", "")
    print(keys)
    data = get_history_data(
        [4222126280998916, 4222126197309444],
        datetime(2021, 6, 1),
        datetime(2031, 6, 2),
    )

    # data = get_realtime_data([4222126280998916, 4222126197309444])
    data = get_realtime_data(keys)
    data_to_predict = []
    for k, v in data.items():
        data_to_predict.append(
            {"key": k, "time": datetime.now().isoformat(), "value": v}
        )

    data = model_predict(data_to_predict)
    store_measure_alarm_data(data)

    keys = get_all_devices_keys()
    print(keys)
