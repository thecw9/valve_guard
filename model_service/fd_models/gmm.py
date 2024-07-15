from sys import implementation
import numpy as np
import pickle
import matplotlib.pyplot as plt

from minio import Minio
from io import BytesIO
import argparse
from pyod.models.gmm import GMM
from sklearn.utils import check_array
from sklearn.ensemble import IsolationForest
from sklearn.utils.validation import check_is_fitted
import requests
from datetime import datetime, timedelta


parser = argparse.ArgumentParser()
parser.add_argument(
    "--key", type=str, default="ShaoShang.Pole1Low.Sound.Channel0.PeakFactorDeviation"
)
parser.add_argument("--value", type=float, default=0.0)
parser.add_argument("--mode", type=str, default="train")
parser.add_argument(
    "--start_time", type=str, default=(datetime.now() - timedelta(days=3)).isoformat()
)
parser.add_argument("--end_time", type=str, default=datetime.now().isoformat())
parser.add_argument("--n_components", type=int, default=1)
parser.add_argument("--contamination", type=float, default=0.03)

args = parser.parse_args()

print("Arguments:")
print("  key:", args.key)
print("  value:", args.value)
print("  mode:", args.mode)
print("  start_time:", args.start_time)
print("  end_time:", args.end_time)
print("  n_components:", args.n_components)
print("  contamination:", args.contamination)


minio_endpoint = "127.0.0.1:9000"
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "valve-guard"
minio_client = Minio(
    minio_endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=False,
)


def get_data(url: str, key: str, start_time: str, end_time: str) -> list:
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


def check_model_exist(bucket_name, pkl_object_name):
    try:
        minio_client.stat_object(bucket_name, pkl_object_name)
        return True
    except Exception:
        return False


def save_model(model, bucket_name, pkl_object_name):
    f = BytesIO()
    np.save(f, pickle.dumps(model))
    f.seek(0)
    minio_client.put_object(
        bucket_name=bucket_name,
        object_name=pkl_object_name,
        data=f,
        length=f.getbuffer().nbytes,
    )
    f.close()


def load_model(bucket_name, pkl_object_name):
    model_bytes = minio_client.get_object(
        bucket_name=bucket_name, object_name=pkl_object_name
    )
    model_bytes_downloaded = BytesIO(model_bytes.read())
    model_bytes_downloaded.seek(0)
    model = pickle.loads(np.load(model_bytes_downloaded))
    return model


url = "http://127.0.0.1:8050/sympton/history/"


class Model:
    def __init__(self):
        pass

    def load_data(self):
        self.train_data = get_data(
            url=url,
            key=args.key,
            start_time=args.start_time,
            end_time=args.end_time,
        )
        self.train_data = np.array(self.train_data).reshape(
            -1, 1
        )  # shape = (n_samples, 1)

    def train(self):
        self.load_data()
        self.model = GMM(n_components=args.n_components)
        self.model.fit(self.train_data)

        self.plot()
        self.find_threshold()

    def score_threshold(self):
        x = np.array(self.train_data)
        y = self.model.decision_function(x)
        if y is not None:
            threshold = np.percentile(y, 100 * (1 - args.contamination))
            score_threshold = threshold
            return score_threshold

    def find_threshold(self):
        data = np.sort(self.train_data, axis=0)
        score = self.model.decision_function(data)
        score_threshold = self.score_threshold()
        for i in range(len(data)):
            if score is not None:
                if score[i] < score_threshold:
                    self.up_threshold = data[i]
        for i in range(len(data) - 1, -1, -1):
            if score is not None:
                if score[i] < score_threshold:
                    self.down_threshold = data[i]
        if np.all(self.train_data == self.train_data[0][0]):
            self.up_threshold = self.train_data[0] + 1e-6
            self.down_threshold = self.train_data[0] - 1e-6
        print(f"up_threshold: {self.up_threshold}")
        print(f"down_threshold: {self.down_threshold}")

    def plot(self):
        x = np.array(self.train_data)
        x = np.sort(x, axis=0)
        y = self.model.decision_function(x)
        threshold = self.score_threshold()
        data_points = np.hstack((x, np.zeros_like(x)))
        plt.plot(x, y)
        plt.scatter(data_points[:, 0], data_points[:, 1], color="r")
        plt.axhline(y=threshold, color="r", linestyle="--")
        plt.show()

    def predict(self, data):
        check_is_fitted(self.model)
        score = self.model.decision_function(np.array(data).reshape(-1, 1))
        if score is not None:
            score = score[0]
            if score < self.score_threshold():
                return 0
            else:
                return 1


if __name__ == "__main__":
    model = Model()
    pkl_object_name = f"models/{args.key}/model.pkl"
    if args.mode == "train":
        model.train()
        save_model(model, bucket_name, pkl_object_name)
    else:
        model = load_model(bucket_name, pkl_object_name)

    score = model.model.decision_function(np.array(args.value).reshape(-1, 1))

    print(
        {
            "key": args.key,
            "status": model.predict(args.value),
            "up_threshold": float(model.up_threshold[0]),
            "down_threshold": float(model.down_threshold[0]),
            "msg": f"Up threshold is {model.up_threshold[0]}, down threshold is {model.down_threshold[0]}",
            "start_time": args.start_time,
            "end_time": args.end_time,
        }
    )
