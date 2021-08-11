import json
from pymongo import MongoClient


def write_in_db():
    """Записать вакансии из json файла в созданную БД."""

    client = MongoClient('127.0.0.1', 27017)
    db = client['database']
    vacancy = db.vacancy

    with open('data.json') as f:
        data = json.load(f)

        # Очищаем коллекцию от существующих вакансий.
        vacancy.delete_many({})

        # Записываем в БД вакансии из json файла.
        for i in data:
            vacancy.insert_one(i)

        # Проверяем записались ли данные в БД путём их чтения в вывода в консоль.
        for i in vacancy.find({}):
            print(i)


write_in_db()
