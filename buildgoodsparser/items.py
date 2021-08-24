# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from bs4 import BeautifulSoup as bs

def get_price(value):
    try:
        return float(value)
    except:
        return value

def increase_photo_size(value):
    link_with_big_size = value.replace('w_82', 'w_1200').replace('h_82', 'h_1200')
    return link_with_big_size

def handle_params(value):
    soup = bs(value, 'html.parser')
    key = soup.find('dt', {'class': 'def-list__term'}).text
    value = soup.find('dd', {'class': 'def-list__definition'}).text.strip()
    my_dict = {key: value}
    return my_dict

class BuildgoodsparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(increase_photo_size))
    params = scrapy.Field(input_processor=MapCompose(handle_params))
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(get_price), output_processor=TakeFirst())
    _id = scrapy.Field()
