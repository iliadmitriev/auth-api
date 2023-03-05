from psycopg2 import errors
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import select, insert

from helpers.errors import UserAlreadyExists, RecordNotFound, BadRequest


async def init_pg(app):
    engine = await create_async_engine(
        dsn=app['dsn'],
        minsize=10, maxsize=30
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


def setup_db(app, dsn):
    app['dsn'] = dsn
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)


async def create_user(conn, obj, values):
    try:
        result = await conn.execute(
            insert(obj)
            .values(**values)
            .returning(*obj.__table__.columns)
        )
        record = await result.first()
    except errors.UniqueViolation:
        raise UserAlreadyExists('User with this email is already exists')

    return record


async def get_user_by_email(conn, obj, email):
    result = await conn.execute(select([obj]).where(obj.email == email))
    record = await result.first()
    if not record:
        raise RecordNotFound(f'{obj.__name__} with email={email} is not found')
    return record


async def get_objects(conn, obj):
    select_query = select([obj])
    cursor = await conn.execute(select_query)
    records = await cursor.fetchall()
    objs = [dict(p) for p in records]
    return objs


async def insert_object(conn, obj, values):
    try:
        result = await conn.execute(
            insert(obj)
            .values(**values)
            .returning(*obj.__table__.columns)
        )
        record = await result.first()
    except Exception as e:
        raise BadRequest(str(e))
    return record
