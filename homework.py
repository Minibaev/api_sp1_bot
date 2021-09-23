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


URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

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
    message = homework.get('reviewer_comment')
    if (status and homework_name) is None:
        return 'Проверять нечего'
    if status == 'reviewing':
        return 'Работу взяли на проверку'
    if status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
        send_message(message)
    elif status == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        send_message(message)
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        response = requests.get(
            URL, headers=headers, params=payload).json()
    except ValueError:
        logging.error('Некорректное значение аргумента.')
        response = {}
    except RequestException:
        logging.error('Ошибка Request')
        response = {}
    return response


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = 0  # int(time.time())
    logger.debug('Бот в работе')
    while True:
        try:
            homework = get_homeworks(current_timestamp).get('homeworks')
            if homework:
                logger.info('Есть новости')
                parse_homework_status(homework)
            time.sleep(5 * 60)
        except Exception as error:
            logger.error(f'Бот упал с ошибкой: {error}')
            time.sleep(5)


if __name__ == '__main__':
    main()
