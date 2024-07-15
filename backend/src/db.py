from datetime import datetime

import aiohttp
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.orm import Session

from src.authentication import generate_token
from src.config import Config
from src.logger import Logger
from src.orm_model import AuthUser, Devices, Measures
from src.orm_model.base import Base
from src.services.nrmock_service import get_all_measures_info_from_nrmock_service

config = Config()
logger = Logger(__name__)

engine = create_engine(config.DATABASE_URI, echo=False)


async def init_db():
    if config.DEBUG:
        logger.info("drop all tables")
        # Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)
    logger.info("init auth user table")
    init_auth_user_table()
    logger.info("init measures table")
    await init_measures_table()
    logger.info("init fusion model table")
    await init_devices_table()
    logger.info("reflect db")
    reflect_db()


def reflect_db():
    # all tables start with "measures_" prefix
    Base.metadata.reflect(bind=engine)


def init_auth_user_table():
    # AuthUser
    with Session(engine) as session:
        # check user is exist
        statement = select(AuthUser).where(AuthUser.username == config.FIRST_SUPERUSER)
        user = session.execute(statement).scalar_one_or_none()

        if not user:
            # Create a default user
            user = AuthUser(
                username=config.FIRST_SUPERUSER,
                email=config.FIRST_SUPERUSER_EMAIL,
                password=config.FIRST_SUPERUSER_PASSWORD,
                access_token=generate_token(config.FIRST_SUPERUSER, config.SECRETE_KEY),
                is_active=True,
                is_superuser=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            session.add(user)
            session.commit()


async def init_measures_table():
    # check measures data is exist
    with Session(engine) as session:
        statement = select(Measures).limit(1)
        result = session.execute(statement).scalars().all()
        if result:
            logger.info("measures data is exist")
            return

    # Measures
    async with aiohttp.ClientSession() as aiohttp_session:
        measures_info = await get_all_measures_info_from_nrmock_service(
            session=aiohttp_session
        )

    measures = [
        {
            "key": i.get("key"),
            "time": i.get("time"),
            "value": i.get("value"),
            "unit": "",
            "name": i.get("path"),
            "path": i.get("path"),
            "quality": 1,
        }
        for i in measures_info
    ]

    with Session(engine) as session:
        # insert measures
        session.execute(
            insert(Measures),
            measures,
        )
        session.commit()


async def init_devices_table():
    # check fusion model data is exist
    with Session(engine) as session:
        statement = select(Devices).limit(1)
        result = session.execute(statement).scalars().all()
        if result:
            logger.info("fusion model data is exist")
            return

    # FusionModel

    fusion_models = [
        {
            "key": 5000000000000000,
            "path": "/融合/1000kV潇江Ⅰ线/高抗A相/",
            "include": "潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗A相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗A相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗A相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗A相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000001,
            "path": "/融合/1000kV潇江Ⅰ线/高抗B相/",
            "include": "潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗B相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗B相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗B相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗B相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000002,
            "path": "/融合/1000kV潇江Ⅰ线/高抗C相/",
            "include": "潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗C相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗C相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗C相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅰ线AND高抗C相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000003,
            "path": "/融合/1000kV潇江Ⅱ线/高抗A相/",
            "include": "潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗A相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗A相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗A相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗A相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000004,
            "path": "/融合/1000kV潇江Ⅱ线/高抗B相/",
            "include": "潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗B相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗B相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗B相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗B相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000005,
            "path": "/融合/1000kV潇江Ⅱ线/高抗C相/",
            "include": "潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗C相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗C相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗C相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND潇江Ⅱ线AND高抗C相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000006,
            "path": "/融合/1000kV荆潇Ⅰ线/高抗A相/",
            "include": "潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗A相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗A相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗A相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗A相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000007,
            "path": "/融合/1000kV荆潇Ⅰ线/高抗B相/",
            "include": "潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗B相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗B相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗B相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗B相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000008,
            "path": "/融合/1000kV荆潇Ⅰ线/高抗C相/",
            "include": "潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗C相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗C相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗C相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅰ线AND高抗C相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000009,
            "path": "/融合/1000kV荆潇Ⅱ线/高抗A相/",
            "include": "潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗A相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗A相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗A相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗A相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000010,
            "path": "/融合/1000kV荆潇Ⅱ线/高抗B相/",
            "include": "潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗B相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗B相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗B相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗B相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000011,
            "path": "/融合/1000kV荆潇Ⅱ线/高抗C相/",
            "include": "潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗C相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗C相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗C相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND荆潇Ⅱ线AND高抗C相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000012,
            "path": "/融合/#2主变A相/",
            "include": "潇湘站数字特高压Ⅱ区AND#2主变ANDA相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND#2主变ANDA相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND#2主变ANDA相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND#2主变ANDA相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000013,
            "path": "/融合/#2主变B相/",
            "include": "潇湘站数字特高压Ⅱ区AND#2主变ANDB相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND#2主变ANDB相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND#2主变ANDB相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND#2主变ANDB相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000014,
            "path": "/融合/#2主变C相/",
            "include": "潇湘站数字特高压Ⅱ区AND#2主变ANDC相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND#2主变ANDC相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND#2主变ANDC相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND#2主变ANDC相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000015,
            "path": "/融合/#3主变A相/",
            "include": "潇湘站数字特高压Ⅱ区AND#3主变ANDA相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND#3主变ANDA相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND#3主变ANDA相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND#3主变ANDA相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000016,
            "path": "/融合/#3主变B相/",
            "include": "潇湘站数字特高压Ⅱ区AND#3主变ANDB相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND#3主变ANDB相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND#3主变ANDB相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND#3主变ANDB相AND局放",
            "exclude": "红外",
        },
        {
            "key": 5000000000000017,
            "path": "/融合/#3主变C相/",
            "include": "潇湘站数字特高压Ⅱ区AND#3主变ANDC相AND油色谱"
            + " OR 潇湘站数字特高压Ⅱ区AND#3主变ANDC相AND接地电流"
            + " OR 潇湘站数字特高压Ⅱ区AND#3主变ANDC相AND局部放电"
            + " OR 潇湘站数字特高压Ⅱ区AND#3主变ANDC相AND局放",
            "exclude": "红外",
        },
    ]

    with Session(engine) as session:
        # insert measures
        session.execute(
            insert(Devices),
            fusion_models,
        )
        session.commit()
