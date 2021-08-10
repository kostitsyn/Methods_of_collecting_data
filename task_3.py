from pymongo import MongoClient
from main import get_vacancy_list




def check_on_new_vacancy():
    """Добавить в БД только новые вакансии с интернет-ресурсов."""
    client = MongoClient('127.0.0.1', 27017)
    db = client['database']
    vacancy = db.vacancy
    new_vacancy_list = get_vacancy_list('python')
    for i in new_vacancy_list:
        res = vacancy.replace_one({'link_of_vacancy': i['link_of_vacancy']}, i)
        print()


check_on_new_vacancy()
