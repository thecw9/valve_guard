from fastapi import APIRouter, Depends
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import Session
from src.dependencies import get_db
from sqlalchemy import delete, select
from src.orm_model import TrainLogs
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class TrainLogQuery(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: Optional[int] = None
    size: Optional[int] = None


@router.post("/list")
async def get_all_train_logs(
    param: TrainLogQuery,
    db: Session = Depends(get_db),
):
    """Get all train logs."""
    start_time = param.start_time
    end_time = param.end_time
    page = param.page
    size = param.size

    statement = select(TrainLogs)

    if start_time is not None:
        statement = statement.where(TrainLogs.start_time >= start_time)
    if end_time is not None:
        statement = statement.where(TrainLogs.end_time <= end_time)

    # get total
    total_statement = select(func.count(TrainLogs.task_id)).select_from(TrainLogs)
    total = db.execute(total_statement).scalar()

    # sort by start_time
    statement = statement.order_by(TrainLogs.start_time.desc())

    if page is not None and size is not None:
        statement = statement.offset((page - 1) * size).limit(size)

    result = db.execute(statement).scalars().all()

    return {
        "code": 200,
        "message": "success",
        "data": result,
        "total": total,
    }


@router.post("/delete-all")
async def delete_train_logs(
    db: Session = Depends(get_db),
):
    """Delete all train logs."""
    statement = delete(TrainLogs)
    db.execute(statement)
    db.commit()

    return {
        "code": 200,
        "message": "success",
    }
