import logging
import os
import time

​import requests
import telegram
from dotenv import load_dotenv
​
load_dotenv()
​
PRAKTIKUM_TOKEN = os.environ.get('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
​
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
requests_timeout = 5 * 60
​
​
bot = telegram.Bot(token=TELEGRAM_TOKEN)
​
logging.basicConfig(
    level=logging.DEBUG,
    filename=os.path.join(os.path.dirname(__file__), 'main.log'),
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)
​
​
def parse_homework_status(homework):
    try:
        homework_name = homework.get('homework_name')
    except Exception as e:
        logging.error(f'Наименование домашки не доступно, ошибка: {e}.')
    status = homework.get('status')
    status_dict = {
        'reviewing': f'Работа "{homework_name}" взята на проверку.',
        'rejected': f'У вас проверили работу "{homework_name}"!\n'
                    f'К сожалению, в работе нашлись ошибки.',
        'approved': f'У вас проверили работу "{homework_name}"!\n'
                    f'Ревьюеру всё понравилось, работа зачтена!',
    }
    try:
        verdict = status_dict[status]
    except Exception as e:
        error_text = f'Ошибка {e}, обнаружен новый статус "{status}".'
        logging.error(error_text)
        bot.send_message(CHAT_ID, error_text)
    return verdict
​
​
def get_homeworks(current_timestamp: int):
    payload = {'from_date': current_timestamp}
    try:
        response = requests.get(url, headers=headers, params=payload).json()
    except Exception as e:
        logging.error(f'Данные json не были получены, ошибка: {e}.')
        raise
    if response.get('error'):
        logging.error(f'json содержит error: {response.get("error")}.')
    if response.get('code'):
        logging.error(f'json содержит code: {response.get("code")}.')
    return response
​
​
def send_message(message: str):
    try:
        bot.send_message(CHAT_ID, message)
        logging.info(f'Отправлено сообщение {message}')
    except Exception as e:
        logging.error(f'Сообщение не отправлено, ошибка: {e}.')
​
​
def main():
    current_timestamp = 0  # int(time.time())
    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            homework = homeworks.get('homeworks')
            if homework != []:
                message = parse_homework_status(homework[0])
                send_message(message)
            time.sleep(requests_timeout)
            current_timestamp = homeworks.get('current_date')
​
        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            bot.send_message(CHAT_ID, f'Бот упал с ошибкой: {e}')
            time.sleep(5)
​
​
if __name__ == '__main__':
    logging.debug('Бот стартовал')
    main()

