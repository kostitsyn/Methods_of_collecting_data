import json

from hh.hh_scrapper import HhScrapper
from sj.superjob_scrapper import SuperjobScrapper


HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                        ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

profession = input('Введите интересующую профессию: ')
print('Запущен скраппинг интернет-ресурсов, ждите')

# Скраппим hh.ru
hh_url = 'https://hh.ru'

hh_search_part_url = '/search/vacancy'

hh_params = {
    'area': '1',
    'fromSearchLine': 'true',
    'st': 'searchVacancy',
    'text': profession,
}

hh_obj = HhScrapper(hh_url, hh_search_part_url, HEADERS, hh_params)
hh_obj.run()


# Скраппим superjob.ru
sj_url = 'https://www.superjob.ru'

sj_search_part_url = '/vacancy/search/'

sj_params = {
    'keywords': profession,
    'geo%5Bt%5D%5B0%5D': '4'
}

sj_obj = SuperjobScrapper(sj_url, sj_search_part_url, HEADERS, sj_params)
sj_obj.run()


# Записываем данные в общий файл data.json
res_list = hh_obj.result_list

res_list.extend(sj_obj.result_list)

with open('data.json', 'w') as f:
    json.dump(res_list, f, sort_keys=True, indent=4, ensure_ascii=False)

print('Скраппинг данных успешно завершен!')
