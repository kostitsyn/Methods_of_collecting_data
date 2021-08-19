import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D1%84%D0%B0%D0%BD%D1%82%D0%B0%D1%81%D1%82%D0%B8%D0%BA%D0%B0/?stype=0']

    def parse(self, response: HtmlResponse):
        links = response.css('a.cover::attr(href)').getall()
        next_page = response.css('a.pagination-next__text::attr(href)').get()
        if next_page:
            yield response.follow(f'{self.allowed_domains[0]}{next_page}', callback=self.parse)

        for link in links:
            full_link = f'{self.allowed_domains[0]}{link}'
            yield response.follow(full_link, callback=self.book_parse, meta={'link': full_link})


    def book_parse(self, response: HtmlResponse):
        link = response.meta.get('link')
        book_name = None
        authors = None
        base_price = None
        price_with_discount = None
        rating = None
        print()

