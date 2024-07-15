from datetime import datetime
from typing import Optional
from sqlalchemy.orm import defer

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Table, insert, select, union_all, update, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import column

from src import Config
from src.db import engine
from src.dependencies import get_db
from src.orm_model import Devices

router = APIRouter()
config = Config()


class KeySearchParam(BaseModel):
    include: str = "高抗A相 | 高抗B相"
    exclude: str = "红外&高抗A相"


@router.post("/info")
async def get_devices_keys_by_keywords(
    keywords: KeySearchParam,
    db: Session = Depends(get_db),
):
    """Get keys by keywords
    :param keywords: include, exclude
    :return: keys
    """
    include = keywords.include.replace(" ", "").replace("AND", "&").replace("OR", "|")
    exclude = keywords.exclude.replace(" ", "").replace("AND", "&").replace("OR", "|")

    statement = select(Devices).options(defer(Devices.model))
    if include:
        or_list = []
        for or_keyword in include.split("|"):
            and_list = []
            for and_keyword in or_keyword.split("&"):
                and_list.append(Devices.path.like(f"%{and_keyword}%"))
            or_list.append(and_(*and_list))
        statement = statement.where(or_(*or_list))
    if exclude:
        for keyword in exclude.split("&"):
            statement = statement.where(~Devices.path.like(f"%{keyword}%"))

    results = db.execute(statement).scalars().all()

    return {
        "code": 200,
        "message": "success",
        "addition": {"status_code": config.ALARM_STATUS},
        "data": results,
    }
