from minio import Minio
from datetime import datetime, timedelta
from minio.error import S3Error
import pytz


def delete_old_objects(minio_client, bucket_name, days):
    try:
        objects_to_delete = []
        retention_period = datetime.now(pytz.utc) - timedelta(days=days)

        # 列出存储桶中的对象
        objects = minio_client.list_objects(bucket_name, recursive=True)
        for obj in objects:
            # 检查对象的创建日期
            if obj.last_modified < retention_period:
                objects_to_delete.append(obj.object_name)

        # 删除过期对象
        for obj_name in objects_to_delete:
            minio_client.remove_object(bucket_name, obj_name)
            print(f"Deleted {obj_name}")

        print(f"Deleted {len(objects_to_delete)} objects older than {days} days.")
    except S3Error as err:
        print(f"Failed to delete objects: {err}")


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

delete_old_objects(minio_client, bucket_name, 1)
