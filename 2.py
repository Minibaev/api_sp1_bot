import requests

PRAKTIKUM_TOKEN = 'AQAAAABVM-m8AAYckQPfgqtuGUqzpvIL4lMQyvU'
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
payload = {'from_date': 0}
homework_statuses = requests.get(url, headers=headers, params=payload)
print(homework_statuses.json())
    






