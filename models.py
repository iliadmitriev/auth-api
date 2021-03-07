from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean
)

Base = declarative_base()
metadata = MetaData()


class User(Base):
    __tablename__ = 'user'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    username = Column('firstname', String(100))
    password = Column('firstname', String(200))
    is_active = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
