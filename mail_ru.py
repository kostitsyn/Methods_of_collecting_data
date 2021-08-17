import requests
from lxml import html
from pymongo import MongoClient
import pandas as pd

class MailRuScrapper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def run(self):
        """Запустить скраппинг ресурса mail.ru."""

        self.get_news_links_list()
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

    def get_news_links_list(self):
        """Получить список ссылок на новости."""

        dom = self.get_dom_obj(self.url)
        links_list = dom.xpath("//a[contains(@class, 'js-topnews__item')]/@href")
        return links_list

    def fill_news_list(self):
        """Заполнить результирующий список с данными о новостях."""

        links_list = self.get_news_links_list()
        self.result_news_list = list()
        for link in links_list:
            dom_item = self.get_dom_obj(link)
            item_dict = self.get_item_dict(dom_item)
            item_dict['news_link'] = link
            self.result_news_list.append(item_dict)

    def get_news_list(self):
        """Получить результирующий список с данными о новостях."""

        self.run()
        return self.result_news_list

    def get_item_dict(self, dom_item):
        """Получить словарь с данными о конкретной новости."""

        item_dict = dict()
        source = dom_item.xpath("//div[@class='cols__inner']//a[contains(@class, 'breadcrumbs__link')]/span/text()")
        item_dict['source'] = source[0]
        name_news = dom_item.xpath("//div[contains(@class, 'hdr_collapse')]//h1/text()")
        item_dict['name_news'] = name_news[0]
        date_published = dom_item.xpath("//div[@class='cols__inner']//span[@datetime]/@datetime")
        item_dict['date_published'] = date_published[0]
        return item_dict

    def write_in_db(self):
        """Записать собранную информацию в БД."""

        client = MongoClient('127.0.0.1', 27017)
        db = client['database']
        self.news_collection = db.mail_news
        self.news_collection.delete_many({})
        self.news_collection.insert_many(self.result_news_list)

    def get_database_collection(self):
        """Получить коллекцию БД."""

        return self.news_collection


if __name__ == '__main__':
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                             ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

    url = 'https://news.mail.ru/'
    print('Запущен скраппинг ресурса news.mail.ru...')
    try:
        scrapper_obj = MailRuScrapper(url, headers)
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
