#/bin/bash

celery -A src.background.celery_app worker --concurrency=1000 -P eventlet --loglevel=info 
