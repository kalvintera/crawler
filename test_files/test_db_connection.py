from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import sessionmaker
import os


Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine('sqlite:///./resources/database_urls.db')


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



engine = db_connect()
create_table(engine)
Session = sessionmaker(bind=engine)

from datetime import datetime

session = Session()
# session.query(MyUserClass).filter(MyUserClass.id.in_((123,456))).all()
try:
    urls = session.query(Urls.url, Urls.retrieved).filter(Urls.retrieved.in_((0,))).all()
except:
    session.rollback()
else:
    print(len(urls))
    print(urls[250].url, urls[250].retrieved)

session.query(Urls).filter(Urls.url.in_(tuple(url for url, _ in urls[:2]))).update({"retrieved":1})

urls = session.query(Urls.url, Urls.retrieved).filter(Urls.retrieved == 1).all()
print(urls)

urls[0].retrieved += 1

test = session.query(Urls).filter(Urls.retrieved == 1).all()
start_urls = []
for url in test[:2]:
    start_urls += [url.url]
    url.retrieved = 0
session.commit()
session.close()
test = [url for url, _ in urls[:2]]
print(tuple(url for url, _ in urls[:2]))


#################### check start urls
start_urls = []
try:
    url_rows = session.query(Urls).filter(Urls.retrieved.in_((0,))).all()
    for row in url_rows[:2]:
        start_urls += [row.url]
        url.retrieved = 1
    session.commit()

except:
    session.rollback()
else:
    print(len(urls))
    print(urls[250].url, urls[250].retrieved)
finally:
    session.close()

###################### check retrieved url

url_rows = session.query(Urls).filter(Urls.url == "https://burgenland.orf.at/stories/3077961/").all()
for row in url_rows:
    row.retrieved = 1
    print(row.url)
session.commit()




row = session.query(Urls).filter(Urls.url == "https://www.thinkers.ai/terms-of-use/").first()
row.use_case