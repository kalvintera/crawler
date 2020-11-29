from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine('sqlite:///resources/database_urls.db')


def create_table(engine):
    Base.metadata.create_all(engine)


class Urls(Base):
    __tablename__ = "urls"

    id = Column("id", Integer, primary_key=True)
    url = Column('url', Text())
    start_url = Column("start_url", Text())
    previous_url = Column("previous_url", Text())
    fetch_date = Column("fetch_date", DateTime)
    depth = Column("depth", Integer)
    html = Column("html", Text())
    
    


engine = db_connect()
create_table(engine)
Session = sessionmaker(bind=engine)

from datetime import datetime

session = Session()
urls = Urls()
urls.url = "www.testaa.kd"
urls.start_url = "start.com"
urls.previous_url = "prev.com"
urls.fetch_date = datetime.today()#"1986-12-22 14:25:50"
urls.depth = 0
urls.html = "html body dummy"

try:
    session.add(urls)
    session.commit()

except:
    session.rollback()
    raise

finally:
    session.close()