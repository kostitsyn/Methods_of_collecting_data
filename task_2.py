import json
import pandas as pd
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


class MVideoScrapper:
    """Скраппер новых товаров в интернет-магазине МВидео."""

    def __init__(self):
        self.url = 'https://www.mvideo.ru/?cityId=CityCZ_6273'

    def create_chrome_driver(self):
        """Создать драйвер библиотеки Selenium для браузера Chrome."""

        chrome_options = Options()
        chrome_options.add_argument('start-maximized')
        self.driver = webdriver.Chrome(executable_path='./chromedriver_linux64/chromedriver', options=chrome_options)
        self.move_to_url()

    def move_to_url(self):
        """Перейти по указанному url."""

        self.driver.get(self.url)
        self.close_modal_window()

    def close_modal_window(self):
        """Закрыть модальное окно всплывающее при открытии страницы."""

        close_btn = self.driver.find_element_by_xpath("//span[@data-close]")
        close_btn.click()
        self.move_to_goods_list()

    def move_to_goods_list(self):
        """Перейти (пролистать вниз) к разделу новых товаров."""

        new_goods = self.driver.find_element_by_xpath(f"//h2[contains(text(), 'Новинки')]/ancestor::div[@class='section']")
        actions = ActionChains(self.driver)
        actions.move_to_element(new_goods)
        actions.perform()
        self.upload_all_goods()

    def upload_all_goods(self):
        """Загрузить все элементы новых товаров путем нажатия на стрелку промотки вправо."""

        while True:
            wait = WebDriverWait(self.driver, 5)
            try:
                next_btn = self.driver.find_element_by_xpath(
                    f"//h2[contains(text(), 'Новинки')]/ancestor::div[@class='section']//a[contains(@class, 'next-btn')]")
                wait.until(lambda x: 'disabled' not in next_btn.get_attribute('class'))
            except TimeoutException:
                break
            next_btn.click()

    def get_all_goods_elem(self):
        """Получить все элементы новых товаров."""

        elems = self.driver.find_elements_by_xpath(
            f"//h2[contains(text(), 'Новинки')]/ancestor::div[@class='section']//li//a[@data-product-info and contains(@class, 'tile-picture')]")
        return elems

    def get_data_list(self):
        """Получить список данных о товарах."""

        self.create_chrome_driver()

        data_list = list()
        for elem in self.get_all_goods_elem():
            res_dict = dict()
            data_dict = json.loads(elem.get_attribute('data-product-info'))
            res_dict['price'], res_dict['product_name'], res_dict['product_category'] = \
                data_dict['productPriceLocal'], data_dict['productName'], data_dict['productCategoryName']
            data_list.append(res_dict)
        self.write_in_db(data_list)
        return data_list

    def create_db_cursor(self):
        """Создать курсор для записи в БД."""

        client = MongoClient('127.0.0.1', 27017)
        db = client['database']
        db_cursor = db.mvideo_goods
        return db_cursor

    def write_in_db(self, data_list):
        """Записать данные в БД."""

        db_cursor = self.create_db_cursor()
        db_cursor.delete_many({})
        db_cursor.insert_many(data_list)


if __name__ == '__main__':
    scrapper_obj = MVideoScrapper()
    res_list = scrapper_obj.get_data_list()

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    df = pd.DataFrame(res_list).drop('_id', 1)

    print(df)
