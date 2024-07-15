from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    Interval,
    LargeBinary,
    String,
    Table,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from src import Config

from .base import Base

config = Config()


class Measures(Base):
    __tablename__ = "measures"

    key: Mapped[int] = mapped_column(BigInteger, primary_key=True, doc="主键")
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False, doc="时间")
    service_time: Mapped[datetime] = mapped_column(
        DateTime,
        doc="业务时间",
        default=datetime.now,
        onupdate=datetime.now,
    )
    value: Mapped[float] = mapped_column(Float, nullable=True, doc="值")
    unit: Mapped[str] = mapped_column(String(255), nullable=True, doc="单位")
    name: Mapped[str] = mapped_column(String(255), nullable=True, doc="名称")
    path: Mapped[str] = mapped_column(String(255), nullable=True, doc="路径")
    quality: Mapped[int] = mapped_column(Integer, nullable=True, doc="质量")

    model: Mapped[bytes] = mapped_column(LargeBinary, nullable=True, doc="模型")
    model_is_trained: Mapped[bool] = mapped_column(
        Boolean, nullable=True, default=False, doc="是否训练"
    )
    train_data_start_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, doc="训练数据开始时间"
    )
    train_data_end_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, doc="训练数据结束时间"
    )
    train_data_total: Mapped[int] = mapped_column(
        Integer, nullable=True, doc="训练数据总数"
    )
    model_version: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        doc="模型版本",
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=True, doc="模型名称")
    model_description: Mapped[str] = mapped_column(
        String(255), nullable=True, doc="模型描述"
    )
    model_created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, doc="创建时间"
    )
    model_updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, doc="更新时间"
    )

    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="状态",
        default=config.ALARM_STATUS["UNKNOWN"],
    )
    probability: Mapped[float] = mapped_column(Float, nullable=True, doc="概率")
    threshold: Mapped[float] = mapped_column(Float, nullable=True, doc="概率阈值")
    threshold_up: Mapped[float] = mapped_column(Float, nullable=True)
    threshold_down: Mapped[float] = mapped_column(Float, nullable=True)


def create_measures_monthly_table(table_name: str) -> Table:
    return Table(
        table_name,
        Base.metadata,
        Column("key", BigInteger, nullable=False, doc="主键", primary_key=True),
        Column("time", DateTime, nullable=False, doc="时间"),
        Column("value", Float, nullable=True, doc="值"),
        Column(
            "service_time",
            DateTime,
            nullable=True,
            primary_key=True,
            server_default=func.now(),
            doc="业务时间",
        ),
    )
