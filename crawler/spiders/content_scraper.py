from scrapy.spiders import Spider
from ..handler_sqlite import Urls, db_connect, create_table
from sqlalchemy.orm import sessionmaker
import trafilatura
from htmldate import find_date
from langdetect import detect
import json
from crawler.items import ArticleItem
from scrapy.utils.log import configure_logging
import logging
from datetime import datetime

class ContentScraper(Spider):
    name = 'content_scraper'
    start_urls = []
    custom_settings = {"ITEM_PIPELINES": {"crawler.pipelines.FromSQLtoSolrPipeline": 200,
                                          "crawler.pipelines.SolrPipeline": 300,
                                          "crawler.pipelines.SQLSetIndexedPipeline": 400,
                                          }}
    configure_logging(install_root_handler=False)
    logging.basicConfig(
            filename=f'logs/log_crawler_{datetime.now()}.txt',
            format='%(levelname)s: %(message)s',
            level=logging.DEBUG
        )

    def parse(self, response):
        data_str = trafilatura.extract(response.body, json_output=True)
        logging.warning("trafilatura output %s", data_str)
        data = json.loads(data_str)
        date = find_date(response.body, original_date=True)  #, outputformat='%Y-%m-%dT00:00:00Z')
        article = ArticleItem()
        article["url"] = data["source"] or response.url
        article["title"] = data["title"]
        article["article"] = data["text"]
        article["pub_date"] = date  # datetime.strptime(date, "%Y-%m-%d")
        article["publisher"] = data["source-hostname"] or data["sitename"] or "not extraced"
        article["use_case"] = ""
        article["lang"] = self.get_lang(data)
        yield article

    @staticmethod
    def get_lang(data):
        if isinstance(data["excerpt"], str) and len(data["excerpt"]) >= 150:
            text = data["excerpt"]
        elif isinstance(data["text"], str) and len(data["text"]) >= 150:
            text = data["text"]
        elif isinstance(data["title"], str) and len(data["text"]) >= 5:
            text = data["title"]
        else:
            return None
        return detect(text[:150]).upper()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        n_urls = kwargs.get("n_urls", 500)
        spider.start_urls = spider.get_urls_from_db(n_urls)
        return spider

    def get_urls_from_db(self, n_urls=500):
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        start_urls = []
        try:
            url_rows = session.query(Urls).filter(Urls.retrieved.in_((0,))).all()
            for row in url_rows:
                row.retrieved = 1
                start_urls += [row.url]
                # take 500 rows
                if len(start_urls) >= n_urls:
                    break
            session.commit()

        except:
            session.rollback()
        finally:
            session.close()

        return start_urls
