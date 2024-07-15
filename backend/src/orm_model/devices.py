from datetime import datetime
from src import Config

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

config = Config()


class Devices(Base):
    __tablename__ = "devices"

    key: Mapped[int] = mapped_column(BigInteger, primary_key=True, doc="主键")
    time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, doc="时间"
    )
    status: Mapped[int] = mapped_column(
        Integer, default=config.ALARM_STATUS["UNKNOWN"], doc="状态"
    )
    include: Mapped[str] = mapped_column(TEXT, nullable=True, doc="包含")
    exclude: Mapped[str] = mapped_column(TEXT, nullable=True, doc="排除")
    additional_include: Mapped[str] = mapped_column(TEXT, nullable=True, doc="额外包含")
    additional_exclude: Mapped[str] = mapped_column(TEXT, nullable=True, doc="额外排除")
    measure_keys: Mapped[list[int]] = mapped_column(
        ARRAY(BigInteger), nullable=True, doc="测点主键"
    )
    model: Mapped[bytes] = mapped_column(LargeBinary, nullable=True, doc="模型")
    train_data: Mapped[dict] = mapped_column(JSON, nullable=True, doc="训练数据")
    train_data_total: Mapped[int] = mapped_column(
        Integer, nullable=True, doc="训练数据总数"
    )
    model_version: Mapped[int] = mapped_column(Integer, default=0, doc="模型版本")
    model_name: Mapped[str] = mapped_column(String(255), nullable=True, doc="模型名称")
    path: Mapped[str] = mapped_column(String(255), nullable=False, doc="路径")
    model_description: Mapped[str] = mapped_column(
        String(255), nullable=True, doc="模型描述"
    )
    model_created: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, doc="创建时间"
    )
    model_updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, doc="更新时间"
    )
