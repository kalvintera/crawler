from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings


Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


class Urls(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    url = Column('url', Text())
    start_url = Column("start_url", Text())
    previous_url = Column("previous_url", Text())
    fetch_date = Column("fetch_date", DateTime)
    depth = Column("depth", Integer)
    retrieved = Column("retrieved", Integer)
    indexed = Column("indexed", Integer)
    cookies = Column("cookies", Integer)
    use_case = Column("use_case", Text())
