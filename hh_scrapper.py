import requests
from bs4 import BeautifulSoup as bs
import json
import re


class HhScrapper:
    def __init__(self, url, search_part_url, headers, params):
        self.url = url
        self.search_part_url = search_part_url
        self.headers = headers
        self.params = params
        self.result_list = []

    def run(self):
        self.create_response_obj()
        self.create_parser_obj()
        self.fill_result_list()

    def create_response_obj(self):
        self.response = requests.get(f'{self.url}{self.search_part_url}',
                                     params=self.params, headers=self.headers)

    def create_parser_obj(self):
        self.soup = bs(self.response.text, 'html.parser')

    def get_entities_list(self):
        entities_list = self.soup.findAll('div', {'class': 'vacancy-serp-item'})
        return entities_list

    def fill_result_list(self):
        entities_list = self.get_entities_list()
        for entity in entities_list:
            entity_data_dict = self.create_entity_dict(entity)
            self.result_list.append(entity_data_dict)

        self.change_page()

    def change_page(self):
        try:
            update_part_url = self.soup.find('a', {'data-qa': 'pager-next'})['href']
        except TypeError:
            self.write_json()
        else:
            self.response = requests.get(f'{self.url}{update_part_url}', headers=self.headers)
            self.create_parser_obj()
            self.fill_result_list()

    def create_entity_dict(self, entity):
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
        vacancy_name = entity.find('a', {'class': 'bloko-link'}).text
        return vacancy_name

    def get_salary(self, entity):
        salary_elem = entity.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        if salary_elem:
            salary_string = entity.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).text
            is_interval = re.match('^\d', salary_string)
            if is_interval:
                min_salary = int(''.join(re.findall('(^\d+)\s(\d*)', salary_string)[0]))
                max_salary = int(''.join(re.findall('–\s(\d+)\s(\d*)', salary_string)[0]))
                currency = re.findall('\s(\D+\.?)$', salary_string)[0]
            else:
                if str(salary_string).startswith('о'):
                    min_salary = int(''.join(re.findall('\s(\d+)\s(\d*)', salary_string)[0]))
                    max_salary = None
                    currency = re.findall('\s(\D+\.?)$', salary_string)[0]
                else:
                    min_salary = None
                    max_salary = int(''.join(re.findall('\s(\d+)\s(\d*)', salary_string)[0]))
                    currency = re.findall('\s(\D+\.?)$', salary_string)[0]
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
        link_of_vacancy = entity.find('a', {'class': 'bloko-link'})['href']
        return link_of_vacancy

    def get_site_source(self):
        site_source = self.url.split('//')[1]
        return site_source

    def write_json(self):
        with open('data.json', 'w') as f:
            json.dump(self.result_list, f, sort_keys=True, indent=4, ensure_ascii=False)


URL = 'https://hh.ru'

SEARCH_PART_URL = '/search/vacancy'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

params = {
    'area': '1',
    'fromSearchLine': 'true',
    'st': 'searchVacancy',
    'text': 'python',
}
