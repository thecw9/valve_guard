import os
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def is_running_in_docker():
    # Check if the /proc/1/cgroup file exists
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile("/proc/1/cgroup")
        and any("docker" in line for line in open("/proc/1/cgroup"))
    )


current_dir = Path(__file__)
if is_running_in_docker():
    load_dotenv(dotenv_path=current_dir.parent / ".dockerenv")
else:
    load_dotenv(dotenv_path=current_dir.parent / ".env")

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
