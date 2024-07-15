from datetime import datetime

from sqlalchemy import (
    ARRAY,
    JSON,
    TEXT,
    BigInteger,
    DateTime,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TrainLogs(Base):
    __tablename__ = "train_logs"

    task_id: Mapped[str] = mapped_column(String, primary_key=True)
    task_name: Mapped[str] = mapped_column(String, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    state: Mapped[str] = mapped_column(String, nullable=True)
    result: Mapped[dict] = mapped_column(JSON, nullable=True)
    error_traceback: Mapped[str] = mapped_column(TEXT, nullable=True)
    args: Mapped[str] = mapped_column(ARRAY(String), nullable=True)
    kwargs: Mapped[str] = mapped_column(JSON, nullable=True)
    runtime: Mapped[int] = mapped_column(Integer, nullable=True)
