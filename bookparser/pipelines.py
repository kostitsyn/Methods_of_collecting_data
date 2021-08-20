# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class BookparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongo_base = client['books']

    def process_item(self, item, spider):
        if spider.name == 'labirintru':
            item = self.process_labirint(item)
        else:
            item = self.process_book24(item)
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_labirint(self, item):
        item_name_list = item['book_name'].strip().split(': ')
        item['book_name'] = ' '.join(item_name_list[1:]) if len(item_name_list) > 2 else item_name_list[-1]
        item['base_price'] = float(item['base_price'])
        item['price_with_discount'] = float(item['price_with_discount']) if item['price_with_discount'] else None
        item['rating'] = float(item['rating'])
        return item

    def process_book24(self, item):
        item_name_list = item['book_name'].strip().split(': ')
        item['book_name'] = ' '.join(item_name_list[1:]) if len(item_name_list) > 2 else item_name_list[-1]
        item['authors'] = [i.strip() for i in item['authors']]
        try:
            item['base_price'] = float(item['base_price'])
        except ValueError:
            item['base_price'] = float(re.findall('\s+(\d+).+', item['base_price'])[0])
        item['price_with_discount'] = float(item['price_with_discount']) if item['price_with_discount'] else None
        item['rating'] = float(item['rating'])
        return item
