from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from kombu.exceptions import MessageStateError
from pydantic import BaseModel
from sqlalchemy import Table, and_, insert, or_, select, union_all, update
from sqlalchemy.orm import Session, defer, deferred
from sqlalchemy.sql import column
from sqlalchemy.sql.expression import func
from src.db import engine
from src.dependencies import get_db
from src.orm_model import Measures, create_measures_monthly_table
from src.orm_model.base import Base

from src import Config

router = APIRouter()
config = Config()


class KeySearchParam(BaseModel):
    include: str = "高抗A相&油色谱 | 高抗B相&接地电流"
    exclude: Optional[str] = None
    exclude_no_unit: bool = False


@router.post("/info")
async def get_measures_keys_by_keywords(
    keywords: KeySearchParam,
    db: Session = Depends(get_db),
):
    """Get keys by keywords
    :param keywords: include, exclude
    :return: keys
    """
    include = keywords.include.replace(" ", "").replace("AND", "&").replace("OR", "|")
    exclude = keywords.exclude
    if exclude:
        exclude = exclude.replace(" ", "").replace("AND", "&").replace("OR", "|")
    exclude_no_unit = keywords.exclude_no_unit

    statement = select(Measures).options(defer(Measures.model))
    if include:
        or_list = []
        for or_keyword in include.split("|"):
            and_list = []
            for and_keyword in or_keyword.split("&"):
                and_list.append(Measures.path.like(f"%{and_keyword}%"))
            or_list.append(and_(*and_list))
        statement = statement.where(or_(*or_list))
    if exclude:
        for keyword in exclude.split("&"):
            statement = statement.where(~Measures.path.like(f"%{keyword}%"))
    if exclude_no_unit:
        statement = statement.where(Measures.unit != "")

    results = db.execute(statement).scalars().all()

    return {
        "code": 200,
        "message": "success",
        "addition": {"status_code": config.ALARM_STATUS},
        "data": results,
    }


class MeasuresInfoQueryParam(BaseModel):
    key: int = 4222125033390086


@router.post("/info/detail")
async def get_measures_info_by_key(
    data: MeasuresInfoQueryParam,
    db: Session = Depends(get_db),
):
    """Get measures info by key
    :param key: key
    :return: measures info
    """
    key = data.key

    statement = (
        select(Measures).options(defer(Measures.model)).where(Measures.key == key)
    )
    result = db.execute(statement).scalar()

    if not result:
        raise HTTPException(status_code=404, detail="measures not found")

    return {
        "code": 200,
        "message": "success",
        "data": result,
    }


class RealtimeDataSearchParam(BaseModel):
    keys: list[int] = [4222125033390086, 4222125027229703, 4222125027295239]


@router.post("/realtime")
async def get_realtime_data(keys: RealtimeDataSearchParam, db=Depends(get_db)):
    if not keys.keys:
        raise HTTPException(status_code=400, detail="keys is empty")

    statement = (
        select(Measures)
        .options(defer(Measures.model))
        .where(Measures.key.in_(keys.keys))
    )
    results = db.execute(statement).scalars().all()
    return {
        "code": 200,
        "message": "success",
        "data": results,
    }


class RealtimeDataStoreParam(BaseModel):
    key: int = 4222125033390086
    value: float
    time: Optional[datetime] = datetime.now()
    status: int = config.ALARM_STATUS["UNKNOWN"]


@router.post("/realtime/store")
async def store_realtime_data(
    data: list[RealtimeDataStoreParam], db: Session = Depends(get_db)
):
    if not data:
        raise HTTPException(status_code=400, detail="data is empty")

    data_dict = [d.model_dump() for d in data]

    # update measures table
    db.execute(
        update(Measures),
        data_dict,
    )
    db.commit()

    # insert into realtime table
    year = datetime.now().year
    month = datetime.now().month
    table_name = f"measures_{year}_{month}"
    # check if table exists
    if Base.metadata.tables.get(table_name) is None:
        table = create_measures_monthly_table(table_name)
        table.create(engine)
    else:
        table = Table(table_name, Base.metadata, autoload_with=engine)
        table.create(engine, checkfirst=True)
    db.execute(insert(table), data_dict)
    db.commit()

    return {"code": 200, "message": "Store data success"}


class HistoryDataSearchParam(BaseModel):
    keys: list[int] = [4222125033390086, 4222125027229703, 4222125027295239]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: Optional[int] = None
    size: Optional[int] = None


@router.post("/history")
async def get_measure_history_data(
    data: HistoryDataSearchParam,
    db: Session = Depends(get_db),
):
    if not data.keys:
        raise HTTPException(status_code=400, detail="keys is empty")

    start_time = data.start_time
    end_time = data.end_time
    page = data.page
    size = data.size

    # all measures tables
    tables = [
        table
        for table_name, table in Base.metadata.tables.items()
        if table_name.startswith("measures_")
    ]

    if not tables:
        raise HTTPException(status_code=400, detail="measures tables is empty")

    results = []
    # union all tables
    # TODO: optimize
    for key in data.keys:
        # NOTE: use time or service_time
        statement = union_all(
            *[
                (
                    select(table)
                    .where(table.c.key == key)
                    .where(table.c.service_time.between(start_time, end_time))
                    # .where(table.c.time.between(start_time, end_time))
                    if start_time and end_time
                    else select(table).where(table.c.key == key)
                )
                for table in tables
            ]
        ).order_by(column("service_time").desc())

        # get total count
        total_statement = select(func.count()).select_from(statement.alias("t"))
        total = db.execute(total_statement).scalar()

        # sort by service_time
        statement = statement.order_by(column("service_time").desc())

        if page and size:
            statement = statement.limit(size).offset((page - 1) * size)
        result = db.execute(statement).fetchall()
        result = [r._asdict() for r in result]
        results.append({"key": key, "data": result, "total": total})

    return {
        "code": 200,
        "message": "success",
        "data": results,
    }


class HistoryLatestDataSearchParam(BaseModel):
    keys: list[int] = [4222125033390086, 4222125027229703, 4222125027295239]
    limit: int = 100


@router.post("/history/latest")
async def get_history_latest_num_data(
    data: HistoryLatestDataSearchParam,
    db: Session = Depends(get_db),
):
    if not data.keys:
        raise HTTPException(status_code=400, detail="keys is empty")

    num = data.limit

    # all measures tables
    tables = [
        table
        for table_name, table in Base.metadata.tables.items()
        if table_name.startswith("measures_")
    ]

    if not tables:
        raise HTTPException(status_code=400, detail="measures tables is empty")

    results = []
    # union all tables
    for key in data.keys:
        # NOTE: use time or service_time
        statement = (
            union_all(*[select(table).where(table.c.key == key) for table in tables])
            .order_by(column("service_time").desc())
            .limit(num)
        )
        result = db.execute(statement).fetchall()
        result = [r._asdict() for r in result]
        results.append({"key": key, "total": len(result), "data": result})

    return {
        "code": 200,
        "message": "success",
        "data": results,
    }
