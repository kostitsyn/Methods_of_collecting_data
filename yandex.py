import requests
from lxml import html
from pymongo import MongoClient
import pandas as pd


class YandexScrapper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def run(self):
        """Запустить скраппинг ресурса yandex.ru."""

        self.get_dom_news_list()
        self.fill_news_list()

    def get_response_obj(self, url):
        """Получить объект response."""

        response = requests.get(url, headers=self.headers)
        return response

    def get_dom_obj(self, url):
        """Получить DOM-объект."""

        response = self.get_response_obj(url)
        dom = html.fromstring(response.text)
        return dom

    def get_dom_news_list(self):
        """Получить список ссылок на новости."""

        dom = self.get_dom_obj(self.url)
        # links_list = dom.xpath("//div[contains(@class, 'news-top')]//article[contains(@class, 'mg-card')]//div[@class='mg-card__text' or @class='mg-card__inner']/a/@href")
        dom_news_list = dom.xpath("//div[contains(@class, 'news-top')]//article[contains(@class, 'mg-card')]")
        return dom_news_list

    def fill_news_list(self):
        """Заполнить результирующий список с данными о новостях."""

        dom_news_list = self.get_dom_news_list()
        self.result_news_list = list()
        for item in dom_news_list:
            # dom_item = self.get_dom_obj(link)
            item_dict = self.get_item_dict(item)
            self.result_news_list.append(item_dict)

    def get_news_list(self):
        """Получить результирующий список с данными о новостях."""

        self.run()
        return self.result_news_list

    def get_item_dict(self, item):
        """Получить словарь с данными о конкретной новости."""

        item_dict = dict()

        # name_news = item.xpath("//h1[@class='mg-story__title']/a/text()")
        name_news = item.xpath(".//div[@class='mg-card__text' or @class='mg-card__inner']//a/*/text()")
        item_dict['name_news'] = name_news[0].replace('\xa0', ' ')

        source = item.xpath(".//span[@class='mg-card-source__source']/a/text()")
        item_dict['source'] = source[0]



        date_published = item.xpath(".//div[@class='mg-card-footer__left']//span[contains(@class, 'source__time')]/text()")
        item_dict['date_published'] = date_published[0]

        news_link = item.xpath(".//span[@class='mg-card-source__source']/a/@href")
        item_dict['news_link'] = news_link[0]


        # temp_link = item.xpath(".//div[@class='mg-card__text' or @class='mg-card__inner']//a/@href")[0]
        # spam = self.get_dom_obj(news_link)
        # source = spam.xpath("//div[@class='news-story__head']/a/span[2]/text()")
        # item_dict['source'] = source
        # news_link = spam.xpath("//div[@class='news-story__head']/a/@href")
        # item_dict['news_link'] = news_link

        return item_dict

    def write_in_db(self):
        """Записать собранную информацию в БД."""

        client = MongoClient('127.0.0.1', 27017)
        db = client['database']
        self.news_collection = db.yandex_news
        self.news_collection.delete_many({})
        self.news_collection.insert_many(self.result_news_list)

    def get_database_collection(self):
        """Получить коллекцию БД."""

        return self.news_collection


if __name__ == '__main__':
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                             ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

    url = 'https://yandex.ru/news/'
    print('Запущен скраппинг ресурса yandex.ru/news/...')
    try:
        scrapper_obj = YandexScrapper(url, headers)
        res = scrapper_obj.get_news_list()
        scrapper_obj.write_in_db()

        col = scrapper_obj.get_database_collection()

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('colheader_justify', 'center')

        df = pd.DataFrame(col.find({}))
        df.drop('_id', axis=1, inplace=True)
        print(df)
    except Exception:
        print('Попытка скраппинга потерпела неудачу!')
