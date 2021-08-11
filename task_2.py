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

    # Получаем текущие значения курса доллара и евро с ресурса mail.ru.
    usd_course = float(soup.find('div', {'class': 'rate__currency'}).text)
    eur_course = float(soup.findAll('div', {'class': 'rate__currency'})[1].text)

    client = MongoClient('127.0.0.1', 27017)
    db = client['database']
    vacancy = db.vacancy

    # Поле reduced_sal - приведенное значение зарплаты в зависимости от валюты.
    result = vacancy.aggregate([
        {
            '$project':
                {
                    '_id': 0,
                    'link_of_vacancy': 1,
                    'salary.min_salary': 1,
                    'salary.max_salary': 1,
                    'salary.currency': 1,
                    'vacancy_name': 1,
                    'reduced_sal':
                        {
                            '$switch':
                                {
                                    'branches': [
                                        {'case': {'$eq': ['$salary.currency', 'руб.']}, 'then': salary},
                                        {'case': {'$eq': ['$salary.currency', 'USD']}, 'then': round(salary/usd_course, 1)},
                                        {'case': {'$eq': ['$salary.currency', 'EUR']}, 'then': round(salary/eur_course, 1)},
                                    ],
                                    'default': 0
                                }
                        },

                    # Здесь и далее в закоментированных строках пытался отфильтровать вакансии непосредственно
                    # в самом запросе через метод $cmp, но безуспешно. Сделал лишь фильтрацию в методе $match по
                    # приведенному значению зарплаты: чтоб она не была меньше 0 (0 устанавливался как значение по
                    # дефолту в методе $switch, если значение salary.currency не соответствовало ни одному из указанных.

                    # 'spam': {'$cmp': ['$reduced_sal', '$salary.min_salary']},
                    # 'eggs': {'$cmp': ['$salary.max_salary', '$reduced_sal']},

                }
        },
        {'$match': {'reduced_sal': {'$not': {'$eq': 0}}}}
        # {'$match': {'$or': [{'spam': {'$gte': 0}}, {'eggs': {'$gte': 0}}]}}
    ])

    # for i in result:
    #     print(i)

    # Отфильтровываем вакансии по требуемому условию: указанная зарплата должна быть меньше
    # минимальной или максимальной зарплаты в вакансии.
    res_list = list()
    for i in result:
        min_salary = i['salary']['min_salary']
        max_salary = i['salary']['max_salary']
        reduced_sal = i['reduced_sal']

        if min_salary and min_salary >= reduced_sal:
            res_list.append(i)
        else:
            if max_salary and max_salary >= reduced_sal:
                res_list.append(i)

    print('Подходящие вакансии:')
    for i in res_list:
        print(f'{i["vacancy_name"]}, зарплата от {i["salary"]["min_salary"]} до '
              f'{i["salary"]["max_salary"]} {i["salary"]["currency"]}, ссылка: {i["link_of_vacancy"]}')


match_salary = int(input('Введите интересующую вас зарплату в рублях: '))
show_match_job_openings(match_salary)
