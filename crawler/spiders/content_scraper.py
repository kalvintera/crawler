from scrapy.spiders import Spider
from ..handler_sqlite import Urls, db_connect, create_table
from sqlalchemy.orm import sessionmaker
import trafilatura
from htmldate import find_date
from langdetect import detect
import json
from crawler.items import ArticleItem
from datetime import datetime
import logging

class ContentScraper(Spider):
    name = 'parser'
    start_urls = []
    custom_settings = {"ITEM_PIPELINES": {"crawler.pipelines.SolrPipeline": 300,}}

    def parse(self, response):
        data_str = trafilatura.extract(response.body, json_output=True)
        logging.warning("trafilatura output %s", data_str)
        data = json.loads(data_str)
        date = find_date(response.body, original_date=True) #, outputformat='%Y-%m-%dT00:00:00Z')
        article = ArticleItem()
        article["url"] = data["source"]
        article["title"] = data["title"]
        article["article"] = data["text"]
        article["pub_date"] = datetime.strptime(date, "%Y-%m-%d")
        article["scrape_date"] = datetime.today()
        article["publisher"] = data["source-hostname"]
        article["lang"] = detect(data["excerpt"]).upper()
        yield article


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.start_urls = spider.get_urls_from_db()
        return spider

    def get_urls_from_db(self):
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        start_urls = []
        try:
            url_rows = session.query(Urls).filter(Urls.retrieved.in_((0,))).all()
            for row in url_rows[:2]:
                start_urls += [row.url]
                row.retrieved = 1
            session.commit()

        except:
            session.rollback()
        finally:
            session.close()

        return start_urls
