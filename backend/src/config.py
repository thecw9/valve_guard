import abc
import os
from pathlib import Path
from src.logger import Logger

from dotenv import load_dotenv

logger = Logger(__name__)


def is_running_in_docker():
    # Check if the /proc/1/cgroup file exists
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile("/proc/1/cgroup")
        and any("docker" in line for line in open("/proc/1/cgroup"))
    )


current_dir = Path(__file__).parent
if is_running_in_docker():
    logger.info("Running in Docker")
    load_dotenv(dotenv_path=current_dir.parent / ".dockerenv")
else:
    logger.info("Running in Local")
    load_dotenv(dotenv_path=current_dir.parent / ".env")


class Singleton(abc.ABCMeta, type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call method for the singleton metaclass."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractSingleton(abc.ABC, metaclass=Singleton):
    """
    Abstract singleton class for ensuring only one instance of a class.
    """

    pass


class Config(metaclass=Singleton):
    DEBUG = True

    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # Auth Settings
    SECRETE_KEY = "1234567890"
    FIRST_SUPERUSER = "admin"
    FIRST_SUPERUSER_PASSWORD = "admin"
    FIRST_SUPERUSER_EMAIL = "admin@mail.com"

    # NRMOCK Settings
    NRMOCK_SERVICE_URL = os.environ["NRMOCK_SERVICE_URL"]

    # Data Service Settings
    DATA_SERVICE_URL = os.environ["DATA_SERVICE_URL"]

    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    # Signal Point Model Settings
    GMM1D_N_COMPONENTS = 5
    GMM1D_TRAINING_DATA_NUM = 1000

    # alarm
    ALARM_STATUS = {
        "UNKNOWN": 0,
        "NORMAL": 1,
        "WARNING": 2,
        "ALARM": 3,
        "UNCONFIRMED": 4,
    }


class APPState(metaclass=Singleton):
    pass
