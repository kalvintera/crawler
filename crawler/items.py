# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


# SAFE KD VERSION:
"""import scrapy


class QuoteItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    quote_content = scrapy.Field()
    tags = scrapy.Field()
    author_name = scrapy.Field()
    author_birthday = scrapy.Field()
    author_bornlocation = scrapy.Field()
    author_bio = scrapy.Field()
"""

# TUTORIAL VERSION:
from scrapy.item import Item, Field
from itemloaders.processors import TakeFirst, MapCompose
# deprecated from scrapy.loader.processors import MapCompose, TakeFirst
from datetime import datetime


def remove_quotes(text):
    # strip the unicode quotes
    text = text.strip(u'\u201c'u'\u201d')
    return text


def convert_date(text):
    # convert string March 14, 1879 to Python date
    return datetime.strptime(text, '%B %d, %Y')


def parse_location(text):
    # parse location "in Ulm, Germany"
    # this simply remove "in ", you can further parse city, state, country, etc.
    return text[3:]

# TakeFirst:
# ItemLoader in spider returns a list for each element.
# e.g. author name has one element but is returned as a list [‘Jimi Hendrix’]
# TakeFirst processor takes the first value of the list

# MapCompose enables us to apply multiple processing functions to a field


class QuoteItem(Item):

    # pre-processes input to this field with remove_quotes() function
    url = Field(input_processor=MapCompose(str.strip), output_processor=TakeFirst())
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
