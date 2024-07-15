from apscheduler.schedulers.blocking import BlockingScheduler
import requests
from datetime import datetime
from sympton_utils import get_all_symptoms

all_symptoms = get_all_symptoms()


def predict_one(key):
    url = f"http://127.0.0.1:8054/model/predict/?key={key}"
    headers = {"accept": "application/json"}
    print(f"Predicting for sympton: {key}")
    response = requests.post(url, headers=headers)
    data = response.json()
    if data["code"] != 200:
        print(f"Prediction failed for sympton: {key}, error: {data['msg']}")


def predict_all():
    for sympton in all_symptoms:
        key = sympton["key"]
        predict_one(key)


scheduler = BlockingScheduler()

scheduler.add_job(predict_all, "interval", seconds=60)
scheduler.start()
