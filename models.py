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
    email = Column('email', String(100), nullable=False, index=True, unique=True)
    password = Column('password', String(200))
    is_active = Column('is_active', Boolean(), default=False)
    is_superuser = Column('is_superuser', Boolean(), default=False)
    created = Column('created', DateTime(timezone=True), server_default=func.now())
    last_login = Column('last_login', DateTime(timezone=True))
