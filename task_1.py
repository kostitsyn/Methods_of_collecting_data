import requests
from bs4 import BeautifulSoup as bs


class Scrapper:
    def __init__(self, url, search_part_url, headers, params):
        self.url = url
        self.search_part_url = search_part_url
        self.headers = headers
        self.params = params

    def run(self):
        self.create_response_obj()
        self.create_parser_obj()
        self.get_vacancy_elements()

    def create_response_obj(self):
        self.response = requests.get(f'{self.url}{self.search_part_url}',
                                     params=self.params, headers=self.headers)

    def create_parser_obj(self):
        self.soup = bs(self.response.text, 'html.parser')

    def get_vacancy_elements(self):
        vacancy_elements = self.soup.findAll('div', {'class': 'vacancy-serp-item'})
        print(vacancy_elements)

URL = 'https://izhevsk.hh.ru'

SEARCH_PART_URL = '/search/vacancy'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

PARAMS = {
    'clusters': 'true',
    'ored_clusters': 'true',
    'enable_snippets': 'true',
    'st': 'searchVacancy',
    'text': 'python',
    'forceFiltersSaving': 'true',
    'page': '0'
}


response = requests.get(f'{URL}{SEARCH_PART_URL}', params=PARAMS, headers=HEADERS)

scrapper_obj = Scrapper(URL, SEARCH_PART_URL, HEADERS, PARAMS)
scrapper_obj.run()
