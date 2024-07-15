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

from database import Base


class Sympton(Base):
    __tablename__ = "symptons"

    key: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    path: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    value: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    unit: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f"<Sympton {self.name}>"


def create_symptom_monthly_table(table_name: str) -> Table:
    table = Table(
        table_name,
        Base.metadata,
        Column("key", String, primary_key=True, index=True),
        Column("path", String),
        Column("timestamp", DateTime, primary_key=True, server_default=func.now()),
        Column("value", Float, nullable=False),
    )
    return table
