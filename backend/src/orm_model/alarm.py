from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Table,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from src.config import Config

from .base import Base
from .devices import Devices
from .measures import Measures

config = Config()


def create_measure_alarms_monthly_table(table_name: str) -> Table:
    return Table(
        table_name,
        Base.metadata,
        Column(
            "key",
            BigInteger,
            nullable=False,
            doc="主键",
            primary_key=True,
        ),
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
        Column("status", Integer, nullable=False, doc="告警状态"),
        Column("type", Integer, nullable=True, doc="0: 单测点告警, 1: 融合告警"),
    )


def create_device_alarms_monthly_table(table_name: str) -> Table:
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
        Column("status", Integer, nullable=False, doc="告警状态"),
        Column("type", Integer, nullable=True, doc="0: 单测点告警, 1: 融合告警"),
    )


# def create_measure_alarms_monthly_table(table_name: str) -> Table:
#     return Table(
#         table_name,
#         Base.metadata,
#         Column(
#             "key",
#             BigInteger,
#             ForeignKey(Measures.key),
#             nullable=False,
#             doc="告警测点Key",
#         ),
#         Column("time", DateTime, nullable=False, doc="告警时间"),
#         Column("status", Integer, nullable=False, doc="告警状态"),
#         Column("value", Float, nullable=True, doc="告警值"),
#         Column("type", Integer, nullable=True, doc="0: 单测点告警, 1: 融合告警"),
#     )
#
#
# def create_device_alarms_monthly_table(table_name: str) -> Table:
#     return Table(
#         table_name,
#         Base.metadata,
#         Column(
#             "key",
#             BigInteger,
#             ForeignKey(Devices.key),
#             nullable=False,
#             doc="告警设备Key",
#         ),
#         Column("time", DateTime, nullable=False, doc="告警时间"),
#         Column("status", Integer, nullable=False, doc="告警状态"),
#         Column("value", Float, nullable=True, doc="告警值"),
#         Column("type", Integer, nullable=True, doc="0: 单设备告警, 1: 融合告警"),
#     )
