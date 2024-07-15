from typing import Dict
import shlex
import re
import subprocess
import json
from io import StringIO
from sqlalchemy import select, and_, or_, insert, update, union_all, column, func
import config
from minio import Minio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from uuid import uuid4
from typing_extensions import Optional
from fastapi import FastAPI, APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from models import Sympton, create_symptom_monthly_table
from database import SessionLocal, engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    Base.metadata.reflect(engine)
    yield
    engine.dispose()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(lifespan=lifespan)
app.title = "Sympton API"


@app.get("/ping")
async def ping():
    return {"code": 200, "message": "success"}


class SymptonQueryParam(BaseModel):
    include: str = "韶山站&声音&通道1 | 韶山站&声音&通道2"
    exclude: Optional[str] = None
    exclude_no_unit: bool = False


@app.post("/sympton/")
async def get_sympton_by_path(
    sympton_query_param: SymptonQueryParam, db=Depends(get_db)
):
    # extract query params
    include = (
        sympton_query_param.include.replace(" ", "")
        .replace("AND", "&")
        .replace("OR", "|")
    )
    exclude = sympton_query_param.exclude
    if exclude:
        exclude = exclude.replace(" ", "").replace("AND", "&").replace("OR", "|")
    exclude_no_unit = sympton_query_param.exclude_no_unit

    # query statement
    statement = select(Sympton)
    if include:
        or_items = []
        for or_item in include.split("|"):
            and_items = []
            for and_item in or_item.split("&"):
                and_items.append(Sympton.path.like(f"%{and_item}%"))
            or_items.append(and_(*and_items))
        statement = statement.where(or_(*or_items))
    if exclude:
        for exclude_item in exclude.split("&"):
            statement = statement.where(~Sympton.path.like(f"%{exclude_item}%"))
    if exclude_no_unit:
        statement = statement.where(Sympton.unit != "")

    # query
    results = db.execute(statement).scalars().all()

    return {
        "code": 200,
        "msg": "success",
        "data": results,
    }


class RealtimeSymptonStoreParam(BaseModel):
    key: str = "test"
    path: str = "test"
    value: float
    timestamp: Optional[datetime] = datetime.now()


@app.post("/sympton/create/")
async def create_sympton(data: list[RealtimeSymptonStoreParam], db=Depends(get_db)):
    if not data:
        return {"code": 400, "msg": "data is empty"}
    symptons_dict = [d.model_dump() for d in data]

    # insert batch data
    try:
        statement = insert(Sympton).values(symptons_dict)
        db.execute(statement)
        db.commit()
    except Exception as e:
        return {"code": 400, "msg": str(e)}

    return {"code": 200, "msg": "success"}


@app.get("/sympton/realtime/")
async def get_realtime_sympton(key: str, db=Depends(get_db)):
    # query statement
    statement = select(Sympton).where(Sympton.key == key)

    # query
    results = db.execute(statement).scalar()

    return {
        "code": 200,
        "msg": "success",
        "data": results,
    }


@app.post("/sympton/store/")
async def store_sympton(data: list[RealtimeSymptonStoreParam], db=Depends(get_db)):
    if not data:
        return {"code": 400, "msg": "data is empty"}
    symptons_dict = [d.model_dump() for d in data]

    # update batch data
    try:
        db.execute(update(Sympton), symptons_dict)
        db.commit()
    except Exception as e:
        return {"code": 400, "msg": str(e)}

    # insert into monthly table
    year = datetime.now().year
    month = datetime.now().month
    table_name = f"symptons_{year}_{month}"
    # check if table exists
    if Base.metadata.tables.get(table_name) is None:
        table = create_symptom_monthly_table(table_name)
        table.create(engine)
    else:
        table = Base.metadata.tables.get(table_name)

    # insert batch data
    try:
        statement = insert(table).values(symptons_dict)
        db.execute(statement)
        db.commit()
    except Exception as e:
        return {"code": 400, "msg": str(e)}

    return {"code": 200, "msg": "success"}


class HistoryDataQueryParam(BaseModel):
    key: str = "test"
    start_time: datetime = datetime.now() - timedelta(days=1)
    end_time: datetime = datetime.now()
    page: Optional[int] = None
    size: Optional[int] = None


@app.post("/sympton/history/")
async def get_sympton_history(
    history_data_query_param: HistoryDataQueryParam, db=Depends(get_db)
):
    # extract query params
    key = history_data_query_param.key
    start_time = history_data_query_param.start_time
    end_time = history_data_query_param.end_time
    page = history_data_query_param.page
    size = history_data_query_param.size

    # get all symptons table
    tables = [
        table
        for table_name, table in Base.metadata.tables.items()
        if table_name.startswith("symptons_")
    ]
    if not tables:
        return {"code": 400, "msg": "no history data"}

    # query statement
    statement = union_all(
        *[
            select(table).where(
                and_(
                    table.c.key == key, table.c.timestamp.between(start_time, end_time)
                )
            )
            for table in tables
        ]
    ).order_by(column("timestamp").desc())
    if page and size:
        statement = statement.limit(size).offset((page - 1) * size)

    # query
    results = db.execute(statement).fetchall()
    results = [r._asdict() for r in results]

    # get total count
    total_statement = select(func.count()).select_from(statement.alias("t"))
    total = db.execute(total_statement).scalar()

    return {
        "code": 200,
        "msg": "success",
        "data": results,
        "total": total,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8050)
