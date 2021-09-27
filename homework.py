import os
import time
import requests
from requests import RequestException
from telegram import Bot

from dotenv import load_dotenv
import logging

from logging.handlers import RotatingFileHandler


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

bot = Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(level=logging.DEBUG,
                    filename='main.log',
                    filemode='a',
                    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'my_logger.log', maxBytes=50000000, backupCount=5
)
logger.addHandler(handler)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if homework_name is None or status is None:
        return 'Проверять нечего'
    if status == 'reviewing':
        return 'Работу взяли на проверку'
    if status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif status == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    payload = {'from_date': current_timestamp}
    response = {}
    try:
        response = requests.get(
            URL, headers=headers, params=payload).json()
    except ValueError:
        logging.error('Некорректное значение аргумента.')
    except RequestException:
        logging.error('Ошибка Request')
    return response


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = 0  # int(time.time())
    logger.debug('Бот в работе')
    while True:
        try:
            homework_list = get_homeworks(current_timestamp).get('homeworks')
            if homework_list:
                homework = homework_list[0]
                logger.info('Есть новости')
                message = parse_homework_status(homework)
                send_message(message)
            time.sleep(5 * 60)
            current_timestamp = homework.get('current_date')
        except Exception as error:
            logger.error(f'Бот упал с ошибкой: {error}')
            time.sleep(5)


if __name__ == '__main__':
    main()
