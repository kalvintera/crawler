# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from itemloaders.processors import MapCompose, TakeFirst
from datetime import datetime


# TakeFirst:
# ItemLoader in spider returns a list for each element.
# e.g. author name has one element but is returned as a list [‘Jimi Hendrix’]
# TakeFirst processor takes the first value of the list

def check_lang(lang):
    # todo: use language module from text analyzer
    return lang if isinstance(lang, str) and lang in ["DE", "EN"] else None


# todo: add fetch_date to ArticleItem
class ArticleItem(Item):
    url = Field()
    title = Field()
    article = Field()
    pub_date = Field()
    fetch_date = Field()
    scrape_date = Field()
    publisher = Field()
    lang = Field(
        # MapCompose takes a list of functions to apply to the value
        # https://docs.scrapy.org/en/latest/_modules/itemloaders/processors.html
        input_processor=MapCompose(check_lang),
        # TakeFirst return the first value not the whole list
        # output_processor=TakeFirst()
        )


class UrlItem(Item):
    url = Field()
    start_url = Field()
    previous_url = Field()
    fetch_date = Field()
    depth = Field()
    retrieved = Field()