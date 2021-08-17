from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import json
from pprint import pprint
import pandas as pd
from pymongo import MongoClient


class MVideoScrapper:
    def __init__(self, section_name):
        self.url = 'https://www.mvideo.ru/?cityId=CityCZ_6273'
        self.section_name = section_name

    def create_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('start-maximized')
        self.driver = webdriver.Chrome(executable_path='./chromedriver_linux64/chromedriver', options=chrome_options)
        self.move_to_url()

    def move_to_url(self):
        self.driver.get(self.url)
        self.close_modal_window()

    def close_modal_window(self):
        close_btn = self.driver.find_element_by_xpath("//span[@data-close]")
        close_btn.click()
        self.move_to_goods_list()

    def move_to_goods_list(self):
        new_goods = self.driver.find_element_by_xpath(f"//h2[contains(text(), 'Новинки')]/ancestor::div[@class='section']")
        actions = ActionChains(self.driver)
        actions.move_to_element(new_goods)
        actions.perform()
        self.upload_all_goods()

    def upload_all_goods(self):
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
        elems = self.driver.find_elements_by_xpath(
            f"//h2[contains(text(), 'Новинки')]/ancestor::div[@class='section']//li//a[@data-product-info and contains(@class, 'tile-picture')]")
        return elems

    def get_data_list(self):
        self.create_chrome_driver()

        data_list = list()
        for elem in self.get_all_goods_elem():
            res_dict = dict()
            data_dict = json.loads(elem.get_attribute('data-product-info'))
            res_dict['price'], res_dict['product_name'], res_dict['product_category'] = \
                data_dict['productPriceLocal'], data_dict['productName'], data_dict['productCategoryName']
            data_list.append(res_dict)
        list_for_write = data_list.copy()
        self.write_in_db(list_for_write)
        return data_list

    def create_db_cursor(self):
        client = MongoClient('127.0.0.1', 27017)
        db = client['database']
        self.db_cursor = db.mvideo_goods

    def write_in_db(self, data_list):
        self.create_db_cursor()
        self.db_cursor.delete_many({})
        self.db_cursor.insert_many(data_list)


if __name__ == '__main__':
    scrapper_obj = MVideoScrapper('Новинки')
    res_list = scrapper_obj.get_data_list()

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    pprint(pd.DataFrame(res_list))


# chrome_options = Options()
# chrome_options.add_argument('start-maximized')
#
# driver = webdriver.Chrome(executable_path='./chromedriver_linux64/chromedriver', options=chrome_options)
#
# driver.get('https://www.mvideo.ru/?cityId=CityCZ_6273')
#
# close_btn = driver.find_element_by_xpath("//span[@data-close]")
# close_btn.click()
#
# new_goods = driver.find_element_by_xpath("//h2[contains(text(), 'Новинки')]/ancestor::div[@class='section']")
# actions = ActionChains(driver)
# actions.move_to_element(new_goods)
# actions.perform()
#
# while True:
#     wait = WebDriverWait(driver, 5)
#     # next_btn = wait.until(EC.element_located_selection_state_to_be((By.XPATH, "//h2[contains(text(), 'Новинки')]/ancestor::div[@class='section']//a[contains(@class, 'next-btn')]")))
#     try:
#         next_btn = driver.find_element_by_xpath("//h2[contains(text(), 'Новинки')]/ancestor::div[@class='section']//a[contains(@class, 'next-btn')]")
#         spam = next_btn.get_attribute('class')
#         wait.until(lambda x: 'disabled' not in next_btn.get_attribute('class'))
#     except TimeoutException:
#         break
#
#     next_btn.click()
#
#
# elems = driver.find_elements_by_xpath("//h2[contains(text(), 'Новинки')]/ancestor::div[@class='section']//li//a[@data-product-info and contains(@class, 'tile-picture')]")
#
# res_list = []
# for i in elems:
#     res_dict = dict()
#     data_dict = json.loads(i.get_attribute('data-product-info'))
#     res_dict['price'], res_dict['product_name'], res_dict['product_category'] = \
#         data_dict['productPriceLocal'], data_dict['productName'], data_dict['productCategoryName']
#     res_list.append(res_dict)


