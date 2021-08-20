# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserItem(scrapy.Item):
    # define the fields for your item here like:
    link = scrapy.Field()
    book_name = scrapy.Field()
    authors = scrapy.Field()
    base_price = scrapy.Field()
    price_with_discount = scrapy.Field()
    rating = scrapy.Field()
    _id = scrapy.Field()
    pass
