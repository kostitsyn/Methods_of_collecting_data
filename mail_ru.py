from lxml import html
import requests


class MailRuScrapper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def run(self):
        self.get_items()

    def get_response_obj(self, url):
        response = requests.get(url, headers=self.headers)
        return response

    def get_dom_obj(self, url):
        response = self.get_response_obj(url)
        dom = html.fromstring(response.text)
        return dom

    def get_news_links(self):
        dom = self.get_dom_obj(self.url)
        links = dom.xpath("//a[contains(@class, 'js-topnews__item')]/@href")
        return links

    def fill_news_list(self):
        links = self.get_news_links()
        # for link in links:


    def create_item_dict(self, dom_item):
        item_dict = dict()
        source = dom_item.xpath("//div[@class='cols__inner']//a[contains(@class, 'breadcrumbs__link')]/span/text()")
        item_dict['source'] = source
        name_news = dom_item.xpath("//div[contains(@class, 'meta-speakable-title')]//h1/text()")
        item_dict['name_news'] = name_news
        date_published = dom_item.xpath("//div[@class='cols__inner']//span[@datetime]/@datetime")
        item_dict['date_published'] = date_published
        return item_dict



if __name__ == '__main__':
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                             ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

    url = 'https://news.mail.ru/'
    scrapper_obj = MailRuScrapper(url, headers)
    scrapper_obj.run()
