from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup as bs


def show_match_job_openings(salary):
    """Вывести вакансии с зарплатой больше переданной суммы."""

    HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                             ' (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

    url = 'https://mail.ru/'

    response = requests.get(url, headers=HEADERS)

    soup = bs(response.text, 'html.parser')

    usd_course = float(soup.find('div', {'class': 'rate__currency'}).text)
    # print(usd_course)

    eur_course = float(soup.findAll('div', {'class': 'rate__currency'})[1].text)
    # print(eur_course)

    client = MongoClient('127.0.0.1', 27017)
    db = client['database']
    vacancy = db.vacancy
    # result = vacancy.find({'$or': [
    #     {'salary.min_salary': {'$gte': salary/usd_course if 'salary.currency' == 'USD' else salary}},
    #     {'salary.max_salary': {'$gte': salary/usd_course if 'salary.currency' == 'USD' else salary}}]})
    result = vacancy.find({})
    res_list = list()
    for i in result:
        if i['salary']['currency'] == 'USD':
            if i['salary']['min_salary'] * usd_course >= salary or i['salary']['max_salary'] * usd_course >= salary:
                res_list.append(i)
                print(i)
        elif i['salary']['currency'] == 'EUR':
            if i['salary']['min_salary'] * eur_course >= salary or i['salary']['max_salary'] * eur_course >= salary:
                res_list.append(i)
                print(i)
        else:
            if i['salary']['min_salary'] >= salary or i['salary']['max_salary'] >= salary:
                res_list.append(i)
                print(i)



match_salary = int(input('Введите интересующую вас зарплату: '))
show_match_job_openings(match_salary)
