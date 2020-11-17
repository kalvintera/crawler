# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd
import os
from datetime import datetime
from .solrhandler import SolrHandler


class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class SolrPipeline(object):
    def __init__(self):
        self.solr = SolrHandler()

    def process_item(self, item, spider):
        dic = dict()
        # for key in dic.keys():
        #    dic[key] = item[key]
        dic["id"] = item["url"]
        dic["title"] = item["title"]
        dic["article"] = item["article"]
        dic["pub_date"] = self.check_date(item["pub_date"])
        dic["publisher"] = item["publisher"]
        self.solr.update(dic, item["lang"])
        return item

    @staticmethod
    def check_date(date):
        date = str(date)
        try:
            strp = datetime.strptime(date, "%Y-%m-%d %H:%M:%S" if len(date) == 19 else "%Y-%m-%d")
        except:
            strp = '1900-01-01T00:00:01Z'
        else:
            strp = str(strp).replace(" ", "T") + "Z"
        return strp


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
            df = pd.read_csv("news_articles.csv", sep=";")
        else:
            df = pd.DataFrame(columns=dic.keys())

        df = df.append(dic, ignore_index=True)
        df.to_csv("news_articles.csv", sep=";", index=False)

        return item


# just for test purposes
class DuplicatedPipeline(object):
    def process_item(self, item, spider):
        try:
            df = pd.read_csv("./news_articles.csv", sep=";")
        except Exception as e:
            print("Duplicates Error:", e)
        else:
            df.drop_duplicates(subset="url", keep="first", inplace=True)
            df.to_csv("./news_articles.csv", sep=";", index=False)
        return item
