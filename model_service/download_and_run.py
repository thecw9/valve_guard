from typing import Optional
from minio import Minio
import json
from pprint import pprint
import re
from io import BytesIO, StringIO
import shlex
import subprocess

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


def download_and_run(bucket_name, object_name, params_command_str: str = ""):
    model_file_bytes = minio_client.get_object(
        bucket_name=bucket_name, object_name=object_name
    )
    model_file_io = StringIO(model_file_bytes.read().decode("utf-8"))
    model_file_io.seek(0)
    model_file_bytes.close()
    model_file_bytes.release_conn()

    command = ["python3", "-c", model_file_io.read()] + shlex.split(params_command_str)

    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    return process


if __name__ == "__main__":
    object_name = "models/test/aa545f95-ee1e-4b05-a686-cb37d38eb9d3.py"
    download_and_run(
        "valve-guard", object_name=object_name, params={"key": "tst", "mode": "train"}
    )
