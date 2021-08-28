# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from scrapy.pipelines.images import ImagesPipeline


class PostsdataparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client['data_profiles']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            pass
        return item


class PostsavatarPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['avatar']:
            try:
                yield scrapy.Request(item['avatar'])
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if results:
            item['avatar'] = results[0][1] if results[0][0] else None
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        new_path = f'/{item["login"]}.jpg'
        return new_path


# Запрос к БД, возвращающий подписчиков указанного пользователя.
#db.instagram.find({'owner': 'nicky_izh', 'relation': 'follower'})

# Запрос к БД, возвращающий на кого подписан указанный пользователь.
#db.instagram.find({'owner': 'vanyaman1', 'relation': 'following'})