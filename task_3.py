import json
from pymongo import MongoClient
from main import get_vacancy_list


def check_on_new_vacancy():
    """Добавить в БД только новые вакансии."""

    client = MongoClient('127.0.0.1', 27017)
    db = client['database']
    vacancy = db.vacancy
    search_word = vacancy.find({})[0]['link_of_vacancy'].split('query=')[1]
    print(f'Запущен поиск новых вакансий по профессии: "{search_word}"')
    new_vacancy_list = get_vacancy_list(search_word)

    counter = 0
    for i in new_vacancy_list:
        res = vacancy.update_one({'link_of_vacancy': i['link_of_vacancy']}, {'$set': i})
        if not res.matched_count:
            vacancy.insert_one(i)
            counter += 1
    print(f'Поиск завершен, добавлено {counter} новых вакансий')


check_on_new_vacancy()
