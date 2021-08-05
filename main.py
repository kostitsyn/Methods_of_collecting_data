from hh_scrapper import HhScrapper
from superjob_scrapper import SuperjobScrapper

if __name__ == '__main__':
    HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                            ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

    profession = input('Введите интересующую профессию: ')


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

