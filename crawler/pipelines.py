# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd
import os
import re
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from .handler_solr import SolrHandler
from .handler_sqlite import Urls, db_connect, create_table


class URLFilterPipeline(object):
    def __init__(self, filter_=None):
        self.filter = filter_

    @classmethod
    def from_crawler(cls, crawler):
        filter_ = getattr(crawler.spider, "filter_")
        return cls(filter_)

    def process_item(self, item, spider):
        if self.filter is None or re.search(self.filter, item["url"]):
            return item
        else:
            raise DropItem("Pattern [%s] not in url [%s]" % (self.filter, item["url"]))


class SQLitePipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.session = None

    def open_spider(self, spider):
        self.session = self.Session()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        """Save urls in the database
        This method is called for every item pipeline component
        """
        urls = Urls()
        urls.url = item["url"]
        urls.start_url = item["start_url"]
        urls.previous_url = item["previous_url"]
        urls.fetch_date = item["fetch_date"]
        urls.depth = item["depth"]
        urls.retrieved = item["retrieved"]

        try:
            self.session.add(urls)
            self.session.commit()
        except:
            self.session.rollback()
            raise

        return item


class SQLDuplicatedPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.session = None

    def open_spider(self, spider):
        self.session = self.Session()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        exist_url = self.session.query(Urls).filter_by(url=item["url"]).first()
        if exist_url is not None:  # the current quote exists
            raise DropItem("Duplicate url found: %s" % item["url"])
        else:
            return item


class SolrPipeline(object):
    def __init__(self):
        self.solr = SolrHandler()

    def process_item(self, item, spider):
        dic = dict()
        if item["lang"] not in ["DE", "EN"]:
            raise DropItem("Extracted article language %s is not valid." % item["lang"])
        else:
            dic["id"] = item["url"]
            dic["title"] = item["title"]
            dic["article"] = item["article"]
            dic["pub_date"] = self.check_date(item["pub_date"])
            dic["index_date"] = self.check_date(datetime.now())
            dic["publisher"] = item["publisher"]
            self.solr.update(dic, item["lang"])
            return item


    @staticmethod
    def check_date(date):
        if isinstance(date, str):
            try:
                strp = datetime.strptime(date[:19], "%Y-%m-%d %H:%M:%S" if len(date[:19]) == 19 else "%Y-%m-%d")
            except:
                strp = '1900-01-01T00:00:01Z'
            else:
                strp = str(strp).replace(" ", "T") + "Z"
            return strp
        elif isinstance(date, datetime):
            return date.strftime("%Y-%m-%dT%H:%M:%SZ")


class SQLSetRetrievedPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.session = None

    def open_spider(self, spider):
        self.session = self.Session()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        """
        Set flag for retrieved URLs.
        """
        try:
            url_rows = self.session.query(Urls).filter(Urls.url == item["url"]).all()
            for row in url_rows:
                row.retrieved = 1
            self.session.commit()
        except:
            self.session.rollback()
            raise

        return item



class CSVPipeline(object):
    def process_item(self, item, spider):
        """Save orf articles in a CSV file.
        This method is called for every item pipeline component.
        """
        dic = dict()
        for key in item.keys():
            dic[key] = item[key]

        # just for test purposes...
        # opens a csv file, reads it and writes to it, every single time!

        if "news_articles.csv" in os.listdir("."):
            df = pd.read_csv("./resources/news_articles.csv", sep=";")
        else:
            df = pd.DataFrame(columns=dic.keys())

        df = df.append(dic, ignore_index=True)
        df.to_csv("./resources/news_articles.csv", sep=";", index=False)

        return item


# just for test purposes
class CSVDuplicatedPipeline(object):
    def process_item(self, item, spider):
        try:
            df = pd.read_csv("./resources/news_articles.csv", sep=";")
        except Exception as e:
            print("Duplicates Error:", e)
        else:
            df.drop_duplicates(subset="url", keep="first", inplace=True)
            df.to_csv("./resources/news_articles.csv", sep=";", index=False)
        return item
