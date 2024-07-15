import requests
from datetime import datetime, timedelta


def get_data(url, key, start_time, end_time):
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
    data = [i["value"] for i in data["data"]]
    return data


if __name__ == "__main__":
    url = "http://127.0.0.1:8050/sympton/history/"
    key = "test"
    end_time = datetime.now().isoformat()
    start_time = (datetime.now() - timedelta(days=30)).isoformat()
    data = get_data(url, key, start_time, end_time)
    print(data)
