from src.config import Config
from celery.signals import task_failure
from src.logger import Logger
from celery.schedules import crontab


from celery import Celery

config = Config()
logger = Logger(__name__)

celery_app = Celery(
    "tasks",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=[
        "src.background.tasks.model_tasks",
        "src.background.tasks.pull_tasks",
    ],
)

celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    timezone="Asia/Shanghai",
    enable_utc=True,
)


celery_app.conf.beat_schedule = {
    # every 1 minute
    "pull_oil_chromatography": {
        "task": "src.background.tasks.pull_tasks.pull_feature",
        # "schedule": crontab(minute=1),
        "schedule": crontab(hour="*/1"),
    },
    # "pull_part_discharge": {
    #     "task": "src.background.tasks.pull_tasks.pull_part_discharge",
    #     # "schedule": crontab(minute=1),
    #     "schedule": crontab(hour="*/1"),
    # },
    # "pull_iron_core": {
    #     "task": "src.background.tasks.pull_tasks.pull_iron_core",
    #     # "schedule": crontab(minute=1),
    #     "schedule": crontab(hour="*/1"),
    # },
    # "diagnose_all_devices": {
    #     "task": "src.background.tasks.pull_tasks.diagnose_all_devices",
    #     # "schedule": crontab(minute=1),
    #     "schedule": crontab(hour="*/1"),
    # },
}


celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    timezone="Asia/Shanghai",
    enable_utc=True,
)


if __name__ == "__main__":
    celery_app.start()
