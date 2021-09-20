import os
import time
import requests
from telegram import Bot

from telegram.ext import Updater

from dotenv import load_dotenv
import logging

from logging.handlers import RotatingFileHandler


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
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
    homework_name = homework_name.split('.')[0]
    status = homework.get('status')
    if status != 'approved':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(URL, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    current_timestamp = int(time.time())
    message = get_homeworks(
        current_timestamp).get('homeworks')[0].get('reviewer_comment')
    return bot.send_message(CHAT_ID, message)


def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # Начальное значение timestamp
    logger.debug('Успешно')
    while True:
        try:
            response_before = get_homeworks(
                current_timestamp).get('homeworks')[0]
            time.sleep(5 * 60)  # Опрашивать раз в пять минут
            response_after = get_homeworks(
                current_timestamp).get('homeworks')[0]
            if response_after != response_before:
                logger.info('Есть новости')
                return parse_homework_status()

        except Exception as error:
            logger.error('Бот упал с ошибкой')
            print(f'Бот упал с ошибкой: {error}')
            time.sleep(5)

        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
