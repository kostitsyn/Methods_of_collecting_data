import scrapy
from scrapy.http import HtmlResponse
from buildgoodsparser.items import BuildgoodsparserItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}&family=cdf02310-fc9e-11e9-810b-878d0b27ea5b&suggest=true']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a[data-qa-pagination-item="right"]::attr(href)').get()
        next_page = f'{self.allowed_domains[0]}{next_page}'
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.css('a[data-qa="product-image"]')
        for link in links:
            yield response.follow(link, callback=self.product_parse)

    def product_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=BuildgoodsparserItem(), response=response)
        loader.add_css('name', 'h1::text')
        loader.add_css('photos', "img[slot='thumbs']::attr(src)")
        loader.add_value('url', response.url)
        loader.add_css('price', "uc-pdp-price-view meta[itemprop='price']::attr(content)")
        loader.add_css('characteristics', 'div.def-list__group')
        yield loader.load_item()
