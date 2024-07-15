from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import shlex
from datetime import datetime


def sound_symptons_extract():
    command = "python3 ./feature_symptom/main.py"
    process = subprocess.run(shlex.split(command))
    if process.returncode != 0:
        print("Error in sound_symptons_extract")
    else:
        print("sound_symptons_extract success")


scheduler = BlockingScheduler()

scheduler.add_job(sound_symptons_extract, "interval", seconds=60)
scheduler.start()
