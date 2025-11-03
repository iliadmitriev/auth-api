from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from helpers.errors import UserAlreadyExists, RecordNotFound, BadRequest


async def init_pg(app):
    engine = create_async_engine(
        app['dsn'],
        pool_size=10,
        max_overflow=20
    )
    app['engine'] = engine
    app['db_session'] = async_sessionmaker(engine, expire_on_commit=False)


async def close_pg(app):
    if 'engine' in app:
        await app['engine'].dispose()


def setup_db(app, dsn):
    app['dsn'] = dsn
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)


async def create_user(session, obj, values):
    try:
        stmt = insert(obj).values(**values).returning(*obj.__table__.columns)
        result = await session.execute(stmt)
        record = result.first()
        await session.commit()
        return record
    except IntegrityError:
        await session.rollback()
        raise UserAlreadyExists('User with this email already exists')


async def get_user_by_email(session, obj, email):
    stmt = select(obj).where(obj.email == email)
    result = await session.execute(stmt)
    record = result.scalar_one_or_none()
    if not record:
        raise RecordNotFound(f'{obj.__name__} with email={email} is not found')
    return record


async def get_objects(session, obj):
    stmt = select(obj)
    result = await session.execute(stmt)
    records = result.scalars().all()
    return records


async def insert_object(session, obj, values):
    try:
        stmt = insert(obj).values(**values).returning(*obj.__table__.columns)
        result = await session.execute(stmt)
        record = result.first()
        await session.commit()
        return record
    except Exception as e:
        await session.rollback()
        raise BadRequest(str(e))
