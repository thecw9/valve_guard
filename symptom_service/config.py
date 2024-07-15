import os
from pathlib import Path
from dotenv import load_dotenv


def is_running_in_docker():
    # Check if the /proc/1/cgroup file exists
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile("/proc/1/cgroup")
        and any("docker" in line for line in open("/proc/1/cgroup"))
    )


if is_running_in_docker():
    SQLALCHEMY_DATABASE_URL = (
        "postgresql://postgres:postgres@valve_guard_symptom_service_db:5432/valve_guard"
    )
    MINIO_ENDPOINT = "host.docker.internal:9000"
else:
    SQLALCHEMY_DATABASE_URL = (
        "postgresql://postgres:postgres@127.0.0.1:5432/valve_guard"
    )
    MINIO_ENDPOINT = "127.0.0.1:9000"

MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "valve-guard"
