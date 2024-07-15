#/bin/bash

celery -A src.background.celery_app flower --loglevel=info
