# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class BuildgoodsparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client['buildgoods']

    def process_item(self, item, spider):
        item = self.process_leroymerlinru(item)
        collection = self.db[spider.name]
        collection.insert_one(item)
        return item

    def process_leroymerlinru(self, item):

        item['params'] = {i.keys[0]: i.values[0] for i in item['params']}
        return item


class BuildgoodsPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        spam = super().file_path(request, response=None, info=None, item=None)
        spam1 = spam.split('/')
        name = item['name']
        spam2 = '/'.join(spam1.insert(1, name))
        return spam2
