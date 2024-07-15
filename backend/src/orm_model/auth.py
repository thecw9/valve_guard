from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AuthUser(Base):
    __tablename__ = "auth_user"

    id: Mapped[int] = mapped_column(primary_key=True, doc="主键")
    username: Mapped[str] = mapped_column(String, unique=True, index=True, doc="用户名")
    password: Mapped[str] = mapped_column(String, doc="密码")
    access_token: Mapped[str] = mapped_column(String, doc="访问令牌")
    email: Mapped[str] = mapped_column(String, doc="邮箱")
    is_active: Mapped[bool] = mapped_column(default=True, doc="是否激活")
    is_superuser: Mapped[bool] = mapped_column(default=False, doc="是否超级用户")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, doc="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, doc="更新时间"
    )

    def __repr__(self):
        return f"<User {self.username}>"
