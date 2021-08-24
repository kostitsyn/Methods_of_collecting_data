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
        next_page = response.css('a[data-qa-pagination-item="right"]').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.css('a[data-qa="product-image"]')
        for link in links:
            yield response.follow(link, callback=self.product_parse)

    def product_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=BuildgoodsparserItem(), response=response)
        loader.add_css('name', 'uc-pdp-section-vlimited strong::text')
        loader.add_css('photos', "img[slot='thumbs']::attr(src)")
        loader.add_css('params', 'div.def-list__group')
        loader.add_value('url', response.url)
        loader.add_css('price', "uc-pdp-price-view meta[itemprop='price']::attr(content)")
        yield loader.load_item()


# https://leroymerlin.ru/product/keramogranit-estima-st011-30x30-sm-1-53-m-cvet-seryy-84709060/
# https://leroymerlin.ru/product/keramogranit-estima-st011-30x30-sm-153-m-cvet-seryy-84709060/