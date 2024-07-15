from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.orm import Session
from src.authentication import generate_token
from src.dependencies import get_db
from src.orm_model import AuthUser

from src import Config

config = Config()
router = APIRouter()


@router.post("/access_token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(AuthUser).filter(AuthUser.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # check password
    if not user.password == form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # check is_active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # get token
    access_token = user.access_token

    # return token
    return {"code": 200, "message": "success", "data": {"token": access_token}}


class UserAdd(BaseModel):
    username: str
    password: str
    email: str
    is_active: bool = True
    is_superuser: bool = False


@router.post("/user/add")
async def add_user(user: UserAdd, db: Session = Depends(get_db)):
    # check user exist
    statement = select(AuthUser).where(AuthUser.username == user.username)
    result = db.execute(statement).first()
    if result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist",
        )

    # add user
    statement = insert(AuthUser).values(
        username=user.username,
        password=user.password,
        access_token=generate_token(user.username, config.SECRETE_KEY),
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
    )
    db.execute(statement)
    db.commit()

    # return
    return {"code": 200, "message": "success", "data": None}


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10


@router.post("/user/list")
async def list_user(pagination: PaginationParams, db: Session = Depends(get_db)):
    # get user list
    statement = (
        select(AuthUser)
        .limit(pagination.size)
        .offset((pagination.page - 1) * pagination.size)
    )
    result = db.execute(statement).scalars().all()

    # get total
    statement = select(func.count(AuthUser.id))
    total = db.execute(statement).scalar()

    # return
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": result,
            "total": total,
        },
    }


@router.post("/user/delete/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    # check user exist
    statement = select(AuthUser).where(AuthUser.id == user_id)
    result = db.execute(statement).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not exist",
        )

    # delete user
    statement = delete(AuthUser).where(AuthUser.id == user_id)
    db.execute(statement)
    db.commit()

    # return
    return {"code": 200, "message": "success", "data": None}


class UserUpdate(BaseModel):
    id: int
    username: str
    password: str
    email: str
    is_active: bool = True
    is_superuser: bool = False


@router.post("/user/update")
async def update_user(user: UserUpdate, db: Session = Depends(get_db)):
    # check user exist
    statement = select(AuthUser).where(AuthUser.id == user.id)
    result = db.execute(statement).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not exist",
        )

    # update user
    statement = (
        update(AuthUser)
        .where(AuthUser.id == user.id)
        .values(
            username=user.username,
            password=user.password,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
    )
    db.execute(statement)
    db.commit()

    # return
    return {"code": 200, "message": "success", "data": None}


class UserSearch(BaseModel):
    sub_str: str
    page: int = 1
    size: int = 10


@router.post("/user/search")
async def search_user(user: UserSearch, db: Session = Depends(get_db)):
    # get user list
    statement = (
        select(AuthUser)
        .where(AuthUser.username.like(f"%{user.sub_str}%"))
        .limit(user.size)
        .offset((user.page - 1) * user.size)
    )
    result = db.execute(statement).scalars().all()

    # get total
    statement = select(func.count(AuthUser.id)).where(
        AuthUser.username.like(f"%{user.sub_str}%")
    )
    total = db.execute(statement).scalar()

    # return
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": result,
            "total": total,
        },
    }
