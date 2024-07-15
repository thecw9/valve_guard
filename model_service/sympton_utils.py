import requests
from datetime import datetime, timedelta


def get_all_symptoms():
    url = f"http://127.0.0.1:8050/sympton"
    data = {"include": "", "exclude": ""}
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["msg"])
    return data["data"]


def get_history_data(key, start_time, end_time):
    url = "http://127.0.0.1:8050/sympton/history/"
    response = requests.post(
        url,
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={
            "key": key,
            "start_time": start_time,
            "end_time": end_time,
        },
    )
    data = response.json()
    if data["code"] != 200:
        raise Exception(data["msg"])
    data = [i["value"] for i in data["data"]]
    return data


def get_realtime_symptoms(key: str):
    url = f"http://127.0.0.1:8050/sympton/realtime/?key={key}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    data = response.json()
    if data["code"] != 200:
        raise Exception(data["msg"])

    return data["data"]["value"]


if __name__ == "__main__":
    key = "test"
    end_time = datetime.now().isoformat()
    start_time = (datetime.now() - timedelta(days=30)).isoformat()
    data = get_history_data(key, start_time, end_time)
    print(data)

    realtime_data = get_realtime_symptoms(key)
    print(realtime_data)
