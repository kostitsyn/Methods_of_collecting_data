import json
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from pymongo import MongoClient


class MailRuScrapper:
    """Скраппер входящих писем на mail.ru."""

    def __init__(self):
        self.url = "https://e.mail.ru/inbox/?back=1"

    def create_chrome_driver(self):
        """Создать драйвер библиотеки Selenium для браузера Chrome."""

        chrome_options = Options()
        chrome_options.add_argument("start-maximized")
        self.driver = webdriver.Chrome(executable_path='./chromedriver_linux64/chromedriver', options=chrome_options)

    def create_wait_obj(self):
        """Создать объект ожидания класса WebDriverWait."""

        self.wait = WebDriverWait(self.driver, 10)

    def move_to_url(self, url):
        """Перейти по указанному url."""
        self.driver.get(url)

    def login(self):
        """Пройти авторизацию на сайте."""

        with open('secret.json') as f:
            data = json.load(f)

        login = data.get('login')
        password = data.get('password')

        account_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        account_field.send_keys(login)
        account_field.submit()

        password_field = self.wait.until(EC.element_to_be_clickable((By.NAME, 'password')))
        password_field.send_keys(password)
        password_field.submit()
        self.create_links_list()

    def create_links_list(self):
        """Создать список ссылок писем."""

        links_list = list()
        is_finished = False
        counter = 0

        while True:

        # Вариант с ограничением для проверки работоспособности
        # while counter < 1:
            try:
                letters_link = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'llc')]")))
                actions = ActionChains(self.driver)

                if counter == 0:
                    for i in letters_link:

                    # Вариант с ограничением для проверки работоспособности
                    # for i in letters_link[:10]:
                        link = i.get_attribute('href')
                        links_list.append(link)
                elif counter == 1:
                    for i in letters_link[23:]:
                        link = i.get_attribute('href')
                        links_list.append(link)
                else:
                    for i in letters_link[24:]:
                        link = i.get_attribute('href')
                        if link in links_list:
                            is_finished = True
                            break
                        links_list.append(link)
                if is_finished:
                    break

                actions.move_to_element(letters_link[-1])
                actions.perform()
                counter += 1
            except StaleElementReferenceException:
                pass
            except TimeoutException:
                break
        self.create_data_list(links_list)

    def create_data_list(self, links_list):
        """Создать список с требуемыми данными о письмах."""

        self.data_list = list()
        for link in links_list:
            self.move_to_url(link)
            item_dict = self.get_item_dict()
            self.data_list.append(item_dict)
        self.write_in_db()

    def get_item_dict(self):
        """Получить словарь с данными текущего письма."""

        item_dict = dict()

        sender = self.wait.until(EC.presence_of_element_located
                                 ((By.XPATH, "//div[@class='letter__author']/span[@class='letter-contact']"))).text
        item_dict['sender'] = sender

        date_sending = self.driver.find_element_by_class_name('letter__date').text
        item_dict['date_sending'] = date_sending

        title_of_letter = self.driver.find_element_by_class_name('thread__subject').text
        item_dict['title_of_letter'] = title_of_letter

        text_of_letter = self.driver.find_elements_by_xpath("//div[@class='letter__body']/descendant::*")
        text_str = ''
        for i in text_of_letter:
            item_text = i.text.replace('\n', ' ')
            if not item_text:
                continue
            text_str = f'{text_str} {item_text}'
        item_dict['text_of_letter'] = text_str
        return item_dict

    def create_db_cursor(self):
        """Создать курсор для записи в БД."""

        client = MongoClient('127.0.0.1', 27017)
        db = client['database']
        db_cursor = db.mailru_letters
        return db_cursor

    def write_in_db(self):
        """Записать данные в БД."""

        db_cursor = self.create_db_cursor()
        db_cursor.delete_many({})
        db_cursor.insert_many(self.data_list)

    def get_data_list(self):
        """Получить список с требуемыми данными о письмах."""

        self.create_chrome_driver()
        self.create_wait_obj()
        self.move_to_url(self.url)
        self.login()
        return self.data_list


if __name__ == '__main__':
    scrapper_obj = MailRuScrapper()

    res_list = scrapper_obj.get_data_list()

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', 5)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 70)

    df = pd.DataFrame(res_list).drop('_id', 1)

    print(df)
