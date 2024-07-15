#/bin/bash

export PYTHONPATH=:$PWD

python ./src/worker_pre_start.py

celery -A src.background.celery_app beat -l info
