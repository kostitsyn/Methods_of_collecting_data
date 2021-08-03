import requests
import json
import os
token = os.environ.get("GITHUB_TOKEN")

# url = 'https://api.github.com/users/repos'
# url = 'https://api.github.com/user'
# url = 'https://api.github.com/events'
url = 'https://api.github.com/users/kostitsyn/repos'
# url = 'https://api.github.com/user/repos'

spam = 'application/vnd.github.v3+json'

headers = {
    'Accept': spam,
}

username = 'kostitsyn'
password = '6YUJDKlose3830overLOAD'

params = {
    username: password
}

response = requests.get(url, headers=headers)
# print(response.status_code)
# print(response.text)
j_data = response.json()
#  Выводим список репозиториев для конкретного пользователя
print(f'Список репозиториев пользователя {j_data[1].get("owner").get("login")}:\n')
# print(json.dumps(j_data, indent=4))
for i in j_data:
    print(i['name'])

# Сохраняем данные в файле repositories.json
with open('repositories.json', 'w') as f:
    json.dump(j_data, f, sort_keys=True, indent=4)

