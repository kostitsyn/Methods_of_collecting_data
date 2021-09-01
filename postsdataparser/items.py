# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PostsdataparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    owner = scrapy.Field()
    relation = scrapy.Field()
    login = scrapy.Field()
    name = scrapy.Field()
    avatar = scrapy.Field()
    follower_data = scrapy.Field()

