from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from buildgoodsparser import settings
from buildgoodsparser.spiders.leroymerlinru import LeroymerlinruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    search_goods = input('Введите для поиска название товара: ')
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinruSpider, search=search_goods)
    process.start()
