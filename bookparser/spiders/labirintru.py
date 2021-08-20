import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem
from bookparser.params import find_keyword


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = [f'https://www.labirint.ru/search/{find_keyword}/?stype=0']

    def parse(self, response: HtmlResponse):
        links = response.css('a.cover::attr(href)').getall()
        next_page = response.css('a.pagination-next__text::attr(href)').get()
        if next_page:
            yield response.follow(f'{self.allowed_domains[0]}{next_page}', callback=self.parse)

        for link in links:
            yield response.follow(link, callback=self.book_parse, meta={'link': f'{self.allowed_domains[0]}{link}'})


    def book_parse(self, response: HtmlResponse):
        item_link = response.meta.get('link')
        item_book_name = response.css('h1::text').get()
        item_authors = response.css('a[data-event-label="author"]::text').getall() or \
                  response.css('a[data-event-label="translator"]::text').getall()
        item_base_price = response.css('span.buying-priceold-val-number::text').get() or \
                     response.css('span.buying-price-val-number::text').get()
        item_price_with_discount = response.css('span.buying-pricenew-val-number::text').get()
        item_rating = response.css('#rate::text').get()
        yield BookparserItem(link=item_link, book_name=item_book_name, authors=item_authors,
                             base_price=item_base_price, price_with_discount=item_price_with_discount,
                             rating=item_rating)
