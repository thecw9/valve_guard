from celery import Task
from src.background.celery_app import celery_app
from src.services import data_service, nrmock_service


class MyTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print("Task failed: {0!r}".format(exc))
        # self.update_state(task_id=task_id, state="FAILURE", meta={"exc": str(exc)})


import time


@celery_app.task(base=MyTask)
def pull_feature():
    data = nrmock_service.get_realtime_feature_data_from_nrmock_service()
    response = data_service.store_realtime_data(data)
    data = data_service.model_predict(data)
    response = data_service.store_measure_alarm_data(data)
    return {
        "status": "success",
        "message": "油色谱数据拉取成功",
    }


@celery_app.task(base=MyTask)
def pull_part_discharge():
    keys_1 = nrmock_service.get_keys_from_nrmock_service(include=["局部放电"])
    keys_2 = nrmock_service.get_keys_from_nrmock_service(include=["局放"])
    keys = keys_1 + keys_2
    data = nrmock_service.get_realtime_data_from_nrmock_service(keys)
    response = data_service.store_realtime_data(data)
    data = data_service.model_predict(data)
    response = data_service.store_measure_alarm_data(data)
    return {
        "status": "success",
        "message": "局放数据拉取成功",
    }


@celery_app.task(base=MyTask)
def pull_iron_core():
    keys = nrmock_service.get_keys_from_nrmock_service(include=["接地", "电流"])
    data = nrmock_service.get_realtime_data_from_nrmock_service(keys)
    response = data_service.store_realtime_data(data)
    data = data_service.model_predict(data)
    response = data_service.store_measure_alarm_data(data)
    return {
        "status": "success",
        "message": "接地电流数据拉取成功",
    }


@celery_app.task(base=MyTask)
def diagnose_all_devices():
    device_keys = data_service.get_all_devices_keys()
    data = data_service.fusion_model_predict(device_keys)
    response = data_service.store_device_alarm_data(data)

    return {
        "status": "success",
        "message": "所有设备诊断成功",
    }
