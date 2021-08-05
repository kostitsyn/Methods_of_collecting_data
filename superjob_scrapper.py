import requests
from bs4 import BeautifulSoup as bs
import json
import re


class SuperjobScrapper:
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
        entities_list = self.soup.findAll('div', {'class': ['Fo44F', 'QiY08', 'LvoDO']})
        return entities_list

    def fill_result_list(self):
        entities_list = self.get_entities_list()
        for entity in entities_list:
            entity_data_dict = self.create_entity_dict(entity)
            self.result_list.append(entity_data_dict)

        self.change_page()

    def change_page(self):
        try:
            update_part_url = self.soup.find('a', {'class': 'f-test-button-dalshe'})['href']
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
        vacancy_name = entity.find('a').text
        return vacancy_name

    def get_salary(self, entity):
        salary_string = entity.find('span', {'class': 'f-test-text-company-item-salary'}).text
        by_agreement = re.match('\D+\s\D+', salary_string)
        if not by_agreement:
            is_interval = re.match('.+ — .+', salary_string)
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
                if str(salary_string).startswith('о'):
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
        link_of_vacancy = entity.find('a')['href']
        return f'{self.url}{link_of_vacancy}'

    def get_site_source(self):
        site_source = self.url.split('//')[1]
        return site_source

    def write_json(self):
        with open('data1.json', 'w') as f:
            json.dump(self.result_list, f, sort_keys=True, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    # profession = input('Введите интересующую профессию: ')
    # params['text'] = profession

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
