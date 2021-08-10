import json

from hh.hh_scrapper import HhScrapper
from sj.superjob_scrapper import SuperjobScrapper


def get_vacancy_list(profession):
    HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                            ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}


    # Скраппим hh.ru
    hh_url = 'https://hh.ru'

    hh_search_part_url = '/search/vacancy'

    hh_params = {
        'area': '1',
        'fromSearchLine': 'true',
        'st': 'searchVacancy',
        'text': profession,
        'items_on_page': '20'
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



    res_list = hh_obj.result_list

    res_list.extend(sj_obj.result_list)
    return res_list


def write_json(res_list):
    """# Записываеть данные в общий файл data.json"""
    with open('data.json', 'w') as f:
        json.dump(res_list, f, sort_keys=True, indent=4, ensure_ascii=False)

    print('Скраппинг данных успешно завершен!')


if __name__ == '__main__':
    profession = input('Введите интересующую профессию: ')
    print('Запущен скраппинг интернет-ресурсов, ждите')
    res_list = get_vacancy_list(profession)
    write_json(res_list)
