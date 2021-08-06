import requests
from bs4 import BeautifulSoup as bs
import json
import re


class SuperjobScrapper:
    """Скраппер ресурса superjob.ru"""

    def __init__(self, url, search_part_url, headers, params):
        self.url = url
        self.search_part_url = search_part_url
        self.headers = headers
        self.params = params
        self.result_list = []

    def run(self):
        """Запуск работы скраппера."""

        self.create_response_obj()
        self.create_parser_obj()
        self.fill_result_list()

    def create_response_obj(self):
        """Создать объект Response метода GET библиотеки requests."""

        self.response = requests.get(f'{self.url}{self.search_part_url}',
                                     params=self.params, headers=self.headers)

    def create_parser_obj(self):
        """Создать объект класса BeautifulSoup."""

        self.soup = bs(self.response.text, 'html.parser')

    def get_entities_list(self):
        """Получить список с сущностями."""

        entities_list = self.soup.findAll('div', {'class': 'f-test-vacancy-item'})
        return entities_list

    def fill_result_list(self):
        """Заполнить результирующий список с данными вакансий."""

        entities_list = self.get_entities_list()
        for entity in entities_list:
            entity_data_dict = self.create_vacancy_dict(entity)
            self.result_list.append(entity_data_dict)

        self.change_page()

    def change_page(self):
        """Сменить страницу с вакансиями."""

        try:
            update_part_url = self.soup.find('a', {'class': 'f-test-button-dalshe'})['href']
        except TypeError:
            self.write_json()
        else:
            self.response = requests.get(f'{self.url}{update_part_url}', headers=self.headers)
            self.create_parser_obj()
            self.fill_result_list()

    def create_vacancy_dict(self, entity):
        """Создать словарь с данными текущей вакансии."""

        entity_dict = dict()

        vacancy_name = self.get_vacancy_name(entity)
        entity_dict['vacancy_name'] = vacancy_name

        salary_data_dict = self.get_salary(entity)
        entity_dict['salary'] = salary_data_dict

        link_of_vacancy = self.get_link_of_vacancy(entity)
        entity_dict['link_of_vacancy'] = link_of_vacancy

        site_source = self.get_site_source()
        entity_dict['site_source'] = site_source

        return entity_dict

    def get_vacancy_name(self, entity):
        """Получить название вакансии."""

        vacancy_name = entity.find('a').text
        return vacancy_name

    def get_salary(self, entity):
        """Получить данные о зарплате: минимальная, максимальная, в какой валюте."""

        salary_string = entity.find('span', {'class': 'f-test-text-company-item-salary'}).text
        by_agreement = re.match('\D+\s\D+', salary_string)
        if not by_agreement:
            is_interval = re.match('.+\s—\s.*', salary_string)
            if is_interval:
                min_salary = int(''.join(re.findall('(^\d+)\s(\d*)', salary_string)[0]))
                max_salary = int(''.join(re.findall('—\s(\d+)\s(\d*)', salary_string)[0]))
                currency = re.findall('\s(\D+\.)', salary_string)[0]
            else:
                is_fixed_salary = re.match('^\d', salary_string)
                if is_fixed_salary:
                    min_salary = int(''.join(re.findall('^(\d+)\s(\d*)', salary_string)[0]))
                    max_salary = min_salary
                    currency = re.findall('\s(\D+\.)', salary_string)[0]
                elif str(salary_string).startswith('о'):
                    min_salary = int(''.join(re.findall('\s(\d+)\s(\d*)', salary_string)[0]))
                    max_salary = None
                    currency = re.findall('\s(\D+\.)', salary_string)[0]
                else:
                    min_salary = None
                    max_salary = int(''.join(re.findall('\s(\d+)\s(\d*)', salary_string)[0]))
                    currency = re.findall('\s(\D+\.)', salary_string)[0]
        else:
            min_salary = None
            max_salary = None
            currency = None
        salary_data_dict = {
            'min_salary': min_salary,
            'max_salary': max_salary,
            'currency': currency
        }
        return salary_data_dict

    def get_link_of_vacancy(self, entity):
        """Получить ссылку на вакансию."""

        link_of_vacancy = entity.find('a')['href']
        return f'{self.url}{link_of_vacancy}'

    def get_site_source(self):
        """Получить источник ресурса из которого взята вакансия."""

        site_source = self.url.split('//')[1]
        return site_source

    def write_json(self):
        """Записать результирующий список с данными вакансий в json файл."""

        with open('sj/sj_data.json', 'w') as f:
            json.dump(self.result_list, f, sort_keys=True, indent=4, ensure_ascii=False)


# Для отладки скраппера.
if __name__ == '__main__':

    sj_url = 'https://www.superjob.ru'

    sj_search_part_url = '/vacancy/search/'

    sj_params = {
        'keywords': 'python',
        'geo%5Bt%5D%5B0%5D': '4'
    }
    HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
              ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}
    sj_obj = SuperjobScrapper(sj_url, sj_search_part_url, HEADERS, sj_params)
    sj_obj.run()
