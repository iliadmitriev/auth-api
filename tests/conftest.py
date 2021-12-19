import pathlib
import secrets
import sys

import psycopg2
import pytest
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine

from app.settings import dsn, conf, redis_location
from models.users import Base

BASE_PATH = pathlib.Path(__file__).parent.parent
sys.path.append(BASE_PATH)


def create_test_db():
    test_db_name = f'test_{secrets.token_hex(nbytes=10)}'
    con = psycopg2.connect(dsn=dsn)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute(sql.SQL("CREATE DATABASE {}").format(
        sql.Identifier(test_db_name))
    )
    cur.close()
    return test_db_name


def drop_test_db(test_db_name):

    con = psycopg2.connect(dsn=dsn)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    try:
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
            sql.Identifier(test_db_name))
        )
    except psycopg2.errors.ObjectInUse:
        pass
    finally:
        cur.close()



def setup_test_db_dsn():
    test_db = create_test_db()
    test_db_dsn = f'{conf["engine"]}://{conf["user"]}:{conf["password"]}'\
        f'@{conf["host"]}:{conf["port"]}/{test_db}'
    return test_db_dsn, test_db


def create_and_migrate_test_db_dsn():
    test_db_dsn, test_db = setup_test_db_dsn()
    engine = create_engine(test_db_dsn)
    Base.metadata.create_all(engine)
    return test_db_dsn, test_db


@pytest.fixture(scope='class')
def get_dsn(request):
    test_dsn, test_db = create_and_migrate_test_db_dsn()
    request.cls.dsn = test_dsn
    request.cls.redis_location = redis_location
    yield test_dsn
    drop_test_db(test_db)
