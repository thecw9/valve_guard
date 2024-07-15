import requests
from datetime import datetime
import json
from typing import List, Dict


def create_sympton(server, data: List[Dict]):
    url = f"http://{server}/sympton/create/"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()


def store_sympton(server, data: List[Dict]):
    url = f"http://{server}/sympton/store/"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()


if __name__ == "__main__":
    # 示例调用
    data = [
        {
            "key": "test2",
            "path": "test",
            "value": 0,
            "timestamp": datetime.now().isoformat(),
        }
    ]

    server = "127.0.0.1:8050"

    response = create_sympton(server, data)
    print(response)

    response = store_sympton(server, data)
    print(response)
