# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader.processors import MapCompose, TakeFirst
from datetime import datetime


# TakeFirst:
# ItemLoader in spider returns a list for each element.
# e.g. author name has one element but is returned as a list [‘Jimi Hendrix’]
# TakeFirst processor takes the first value of the list

def check_lang(lang):
    return lang if isinstance(lang, str) and lang in ["DE", "EN"] else None


class ArticleItem(Item):
    url = Field()
    title = Field()
    article = Field()
    pub_date = Field()
    publisher = Field()
    lang = Field(
        # MapCompose takes a list of functions to apply to the value
        # https://docs.scrapy.org/en/latest/_modules/itemloaders/processors.html
        input_processor=MapCompose(check_lang),
        # TakeFirst return the first value not the whole list
        # output_processor=TakeFirst()
        )
"""
class QuoteItem(Item):

    # pre-processes input to this field with remove_quotes() function
    # url = Field(input_processor=MapCompose(str.strip), output_processor=TakeFirst())
    quote_content = Field(
        # MapCompose takes a list of functions to apply to the value
        # https://docs.scrapy.org/en/latest/_modules/itemloaders/processors.html
        input_processor=MapCompose(remove_quotes),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    author_name = Field(input_processor=MapCompose(str.strip), output_processor=TakeFirst())
    author_birthday = Field(input_processor=MapCompose(convert_date), output_processor=TakeFirst())
    author_bornlocation = Field(input_processor=MapCompose(parse_location), output_processor=TakeFirst())
    author_bio = Field(input_processor=MapCompose(str.strip), output_processor=TakeFirst())
    tags = Field()
"""