import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem
from bookparser.params import find_keyword


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    start_urls = [f'https://book24.ru/search/?q={find_keyword}']
    num_page = 1

    def parse(self, response: HtmlResponse):
        links = response.css('a.product-card__image-link::attr(href)').getall()
        if links:
            if self.num_page == 1:
                next_page = self.start_urls[0]
            else:
                next_page = response.url.split('/')
                next_page.insert(3, f'page-{self.num_page}')
                next_page = '/'.join(next_page)
            self.num_page += 1
            yield response.follow(next_page, callback=self.parse)
        for link in links:
            yield response.follow(link, callback=self.book_parse, meta={'link': f'{self.allowed_domains[0]}{link}'})

    def book_parse(self, response: HtmlResponse):
        item_link = response.meta.get('link')
        item_book_name = response.css('h1::text').get()
        item_authors = response.xpath("//h2[contains(text(), 'Характеристики')]/..//li[contains(@class, item-holder)][1]//a/text()").getall()

        discount = response.css('span.product-sidebar-price__discount')
        if discount:
            item_base_price = response.css('span.product-sidebar-price__price-old::text').get()
            item_price_with_discount = response.css('meta[itemprop=price]::attr(content)').get()
        else:
            item_base_price = response.css('meta[itemprop=price]::attr(content)').get()
            item_price_with_discount = None
        item_rating = response.css('meta[itemprop=ratingValue]::attr(content)').get()
        yield BookparserItem(link=item_link, book_name=item_book_name, authors=item_authors,
                             base_price=item_base_price, price_with_discount=item_price_with_discount,
                             rating=item_rating)
