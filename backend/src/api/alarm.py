from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Table, insert, select, union_all, update
from sqlalchemy.orm import Session, defer, deferred
from sqlalchemy.sql import column, func
from src.db import engine
from src.dependencies import get_db
from src.orm_model import (
    Devices,
    Measures,
    create_device_alarms_monthly_table,
    create_measure_alarms_monthly_table,
)
from src.orm_model.base import Base

from src import Config

router = APIRouter()
config = Config()


class AlarmStoreParam(BaseModel):
    key: int = 4222125033390086
    time: datetime = datetime.now()
    value: float = 0.0
    status: int = config.ALARM_STATUS["UNKNOWN"]


@router.post("/measure/store")
async def store_alarm_data(data: list[AlarmStoreParam], db: Session = Depends(get_db)):
    if not data:
        return {"code": 200, "message": "alarm data is empty"}

    data_dict = [d.model_dump() for d in data]

    # update measures table
    db.execute(
        update(Measures),
        data_dict,
    )
    db.commit()

    # exclude data with status is UNKNOWN or NORMAL
    data_dict = [
        d
        for d in data_dict
        if d["status"]
        not in [config.ALARM_STATUS["UNKNOWN"], config.ALARM_STATUS["NORMAL"]]
    ]

    if len(data_dict) == 0:
        return {
            "code": 200,
            "message": "Store alarm data success",
            "addition": "No alarm data",
        }

    # insert into alarm table
    year = datetime.now().year
    month = datetime.now().month
    table_name = f"measure_alarm_{year}_{month}"
    # check if table exists
    if Base.metadata.tables.get(table_name) is None:
        print(1)
        table = create_measure_alarms_monthly_table(table_name)
        table.create(engine)
    else:
        table = Table(table_name, Base.metadata, autoload_with=engine)
        table.create(engine, checkfirst=True)
    db.execute(insert(table), data_dict)
    db.commit()

    return {"code": 200, "message": "Store alarm data success"}


class DeviceAlarmStoreParam(BaseModel):
    key: int = 5000000000000000
    time: datetime = datetime.now()
    status: int = config.ALARM_STATUS["UNKNOWN"]


@router.post("/device/store")
async def store_device_alarm_data(
    data: list[DeviceAlarmStoreParam], db: Session = Depends(get_db)
):
    if not data:
        return {"code": 200, "message": "alarm data is empty"}

    data_dict = [d.model_dump() for d in data]

    # update measures table
    db.execute(
        update(Devices),
        data_dict,
    )
    db.commit()

    # exclude data with status is UNKNOWN or NORMAL
    data_dict = [
        d
        for d in data_dict
        if d["status"]
        not in [config.ALARM_STATUS["UNKNOWN"], config.ALARM_STATUS["NORMAL"]]
    ]

    if len(data_dict) == 0:
        return {
            "code": 200,
            "message": "Store alarm data success",
            "addition": "No alarm data",
        }

    # insert into alarm table
    year = datetime.now().year
    month = datetime.now().month
    table_name = f"device_alarm_{year}_{month}"
    # check if table exists
    if Base.metadata.tables.get(table_name) is None:
        table = create_device_alarms_monthly_table(table_name)
        table.create(engine)
    else:
        table = Table(table_name, Base.metadata, autoload_with=engine)
        table.create(engine, checkfirst=True)
    db.execute(insert(table), data_dict)
    db.commit()

    return {"code": 200, "message": "Store alarm data success"}


class HistoryAlarmQueryParam(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: Optional[int] = None
    size: Optional[int] = None


@router.post("/measure/history")
async def get_measure_alarm_history(
    data: HistoryAlarmQueryParam, db: Session = Depends(get_db)
):
    print("---" * 20)
    print("---" * 20)
    start_time = data.start_time
    end_time = data.end_time
    page = data.page
    size = data.size

    # all alarm tables
    tables = [
        table
        for table_name, table in Base.metadata.tables.items()
        if table_name.startswith("measure_alarm_")
    ]

    if not tables:
        raise HTTPException(status_code=400, detail="alarm tables is empty")

    # union all tables
    statement = union_all(
        *[
            (
                select(table, Measures)
                .join(Measures, table.c.key == Measures.key)
                .where(table.c.time.between(start_time, end_time))
                if start_time and end_time
                else select(table).join(Measures, table.c.key == Measures.key)
            )
            for table in tables
        ]
    ).order_by(column("time").desc())

    # tatal count
    total_statement = select(func.count()).select_from(statement.alias("t"))
    total_count = db.execute(total_statement).scalar()

    if page and size:
        statement = statement.limit(size).offset((page - 1) * size)
    results = db.execute(statement).fetchall()

    results = [r._asdict() for r in results]

    # TODO: optimize
    for r in results:
        r["model"] = None

    return {
        "code": 200,
        "message": "success",
        "data": results,
        "total": total_count,
    }


@router.post("/device/history")
async def get_device_alarm_history(
    data: HistoryAlarmQueryParam, db: Session = Depends(get_db)
):
    start_time = data.start_time
    end_time = data.end_time
    page = data.page
    size = data.size

    # all measures tables
    tables = [
        table
        for table_name, table in Base.metadata.tables.items()
        if table_name.startswith("device_alarm_")
    ]

    if not tables:
        raise HTTPException(status_code=400, detail="alarm tables is empty")

    # union all tables
    statement = union_all(
        *[
            (
                select(table, Devices)
                .options(defer(Devices.model))
                .join(Devices, table.c.key == Devices.key)
                .where(table.c.time.between(start_time, end_time))
                if start_time and end_time
                else select(table)
                .options(defer(Devices.model))
                .join(Devices, table.c.key == Devices.key)
            )
            for table in tables
        ]
    ).order_by(column("time").desc())

    # tatal count
    total_statement = select(func.count()).select_from(statement.alias("t"))
    total_count = db.execute(total_statement).scalar()

    if page and size:
        statement = statement.limit(size).offset((page - 1) * size)
    result = db.execute(statement)
    result = [r._asdict() for r in result]

    # TODO: optimize
    for r in result:
        r["model"] = None

    return {
        "code": 200,
        "message": "success",
        "data": result,
        "total": total_count,
    }
