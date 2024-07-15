import aiohttp
import requests
from src import Config
from fastapi import HTTPException

config = Config()


async def get_all_measures_info_from_nrmock_service(
    session: aiohttp.ClientSession,
) -> list[dict]:
    try:
        resp = await session.get(config.NRMOCK_SERVICE_URL + "/feature")
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    if resp.status != 200:
        raise HTTPException(status_code=resp.status, detail=await resp.text())
    data = await resp.json()
    return data["data"]


def get_realtime_feature_data_from_nrmock_service():
    if not config.NRMOCK_SERVICE_URL:
        raise ValueError("NRMOCK_SERVICE_URL is not set.")
    url = config.NRMOCK_SERVICE_URL + "/feature"
    response = requests.get(url)
    response = response.json()
    return response["data"]


def get_keys_from_nrmock_service(
    include: list[str], exclude: list[str] = []
) -> list[int]:
    """Get keys from the API.

    Args:
        include (list[str]): List of keys to include.
        exclude (list[str], optional): List of keys to exclude. Defaults to [].

    Returns:
        list[int]: List of keys.
    """
    if not config.NRMOCK_SERVICE_URL:
        raise ValueError("NRMOCK_SERVICE_URL is not set.")

    url = config.NRMOCK_SERVICE_URL + "/nrmock-service/keys"
    params = {"include": include, "exclude": exclude}
    response = requests.post(url, json=params)
    response = response.json()
    keys = [d["id"] for d in response["data"]]

    return keys


def get_realtime_data_from_nrmock_service(keys: list[int]) -> list[dict]:
    """Get realtime data by key.

    Args:
        key (int): Key of the data.

    Returns:
        dict: Realtime data.
    """
    if not config.NRMOCK_SERVICE_URL:
        raise ValueError("NRMOCK_SERVICE_URL is not set.")

    url = config.NRMOCK_SERVICE_URL + "/nrmock-service/realtime/mock"
    str_keys = [str(k) for k in keys]
    params = {"keys": str_keys}
    response = requests.post(url, json=params).json()
    data = [
        {
            "key": d["attr_oid"],
            "value": d["fvalue"],
            "time": d["attr_time"],
        }
        for d in response["data"]
    ]

    return data


if __name__ == "__main__":
    keys = get_keys_from_nrmock_service(include=["高抗A相", "油色谱"])
    print(keys)

    data = get_realtime_data_from_nrmock_service(keys)
    from pprint import pprint

    pprint(data)
