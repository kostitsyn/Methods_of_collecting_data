import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.http import HtmlResponse
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=python']

    def parse(self, response: HtmlResponse):
        yield SeleniumRequest(url=self.start_urls[0],
                              callback=self.parse_result,
                              wait_time=10,
                              wait_until=EC.element_to_be_clickable((By.XPATH, "//a[@data-qa='vacancy-serp__vacancy-title']")))

    def parse_result(self, response: HtmlResponse):
        links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']")
        print()
