import aiopg.sa
from exceptions import UserAlreadyExists, RecordNotFound
from sqlalchemy.sql import select, update, insert, delete
from psycopg2 import errors


async def init_pg(app):
    engine = await aiopg.sa.create_engine(
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
    except errors.UniqueViolation as e:
        raise UserAlreadyExists('User with this email is already exists')

    return record


async def get_user_by_email(conn, obj, email):
    result = await conn.execute(select([obj]).where(obj.email == email))
    record = await result.first()
    if not record:
        raise RecordNotFound(f'{obj.__name__} with email={email} is not found')
    return record

