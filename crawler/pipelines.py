# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd

class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class QuotesPipelineCSV(object):
    def __init__(self):
        self.schema = {"name": "", "bday": None, "born_loc": "", "bio": "", "quote": "", "tags": ""}

    def process_item(self, item, spider):
        """Save quotes in the database
        This method is called for every item pipeline component
        """
        dic = {"name": item["author_name"], "bday": item["author_birthday"], "born_loc": item["author_bornlocation"],
               "bio": item["author_bio"], "quote": item["quote_content"], "tags": item["tags"]}

        # just for test purposes...
        # opens a csv file, reads it and writes to it, every single time!
        try:
            df = pd.read_csv("./quotes.csv", sep=";")

        except:
            df = pd.DataFrame(columns=self.schema.keys())

        finally:
            df = df.append(dic, ignore_index=True)
            df.to_csv("./quotes.csv", sep=";", index=False)

        return item


# just for test purposes
class QuotesDuplicatedPipeline(object):

    def process_item(self, item, spider):
        try:
            df = pd.read_csv("./quotes.csv", sep=";")
        except Exception as e:
            print("Duplicates Error:", e)
        else:
            df.drop_duplicates(subset="quote", keep="first", inplace=True)
            df.to_csv("./quotes.csv", sep=";", index=False)

        return item
