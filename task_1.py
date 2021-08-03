import requests
import json

url = 'https://api.github.com/users/kostitsyn/repos'

accept_header = 'application/vnd.github.v3+json'

headers = {
    'Accept': accept_header,
}

response = requests.get(url, headers=headers)
j_data = response.json()

#  Выводим список репозиториев для конкретного пользователя
print(f'Список репозиториев пользователя {j_data[1].get("owner").get("login")}:\n')
for i in j_data:
    print(i['name'])

# Сохраняем данные в файле repositories.json
with open('repositories.json', 'w') as f:
    json.dump(j_data, f, sort_keys=True, indent=4)

