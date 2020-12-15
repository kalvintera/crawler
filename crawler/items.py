# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from itemloaders.processors import MapCompose, TakeFirst
from datetime import datetime



# MapCompose takes a list of functions to apply to the value
# https://docs.scrapy.org/en/latest/_modules/itemloaders/processors.html

# TakeFirst:
# ItemLoader in spider returns a list for each element.
# e.g. author name has one element but is returned as a list [‘Jimi Hendrix’]
# TakeFirst processor takes the first value of the list

class ArticleItem(Item):
    url = Field(output_processor=TakeFirst())
    title = Field()
    article = Field()
    pub_date = Field(output_processor=TakeFirst())
    publisher = Field(output_processor=TakeFirst())
    use_case = Field(output_processor=TakeFirst())
    lang = Field()

    # bla = Field(
        # MapCompose takes a list of functions to apply to the value
        # https://docs.scrapy.org/en/latest/_modules/itemloaders/processors.html
        # input_processor=MapCompose(check_lang),
        # TakeFirst return the first value not the whole list
        # output_processor=TakeFirst()
   #     )


class UrlItem(Item):
    url = Field()
    start_url = Field()
    previous_url = Field()
    fetch_date = Field()
    depth = Field()
    retrieved = Field()
    indexed = Field()
    use_case = Field(output_processor=TakeFirst())
    cookies = Field()
