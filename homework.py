import logging
import os
import time

import requests

from dotenv import load_dotenv

import telegram
from http import HTTPStatus

import exceptions


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(messages)s'
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream='sys.stdout')
logger.addHandler(handler)


def check_tokens():
    '''Проверяем, что есть все токены.'''
    logger.debug('Проверяем, что есть все токены.')
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot, message):
    '''Отправка сообщения в телеграмм.'''
    try:
        logger.debug(f'Успешная отправка сообщения в телеграмм: {message}.')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError as error:
        logger.error(f'Сбой при отправке сообщения в телеграм: {message}.')
        raise exceptions.SendMessages(error)


def get_api_answer(timestamp):
    '''Запрос к эндпоинту API-сервиса.'''
    logger.info('Запрос к эндпоинту API-сервиса.')
    timestamp = timestamp or int(time.time())
    payload = {'from_date': timestamp}

    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException:
        logger.error('URL недоступен.')
        raise exceptions.URLNotAvailable('URL недоступен.')
    if response.status_code != HTTPStatus.OK:
        logger.error('Код ответа от сервера не 200.')
        raise exceptions.StatusCode('Код ответа от сервера не 200ю')
    return response.json()


def check_response(response):
    '''
    Проверяем ответ API на соответствие документации.
    '''
    logger.info('Проверяем ответ API на соответствие документации.')

    if type(response) is not dict:
        logger.error(
            'В ответе API структура данных не соответствует ожиданиям.'
        )
        raise TypeError(
            'В ответе API структура данных не соответствует ожиданиям.'
        )

    if not response:
        logger.error('Пустой словарь.')
        raise exceptions.EmptyResponse('Пустой словарь.')

    if 'homeworks' not in response:
        logger.error('Нет ключа "homeworks"')
        raise exceptions.HomeworksNotInResponse('Нет ключа "homeworks"')

    homework = response['homeworks']

    if type(homework) is not list:
        logger.error('Данные приходят не в виде списка.')
        raise TypeError(
            'Данные приходят не в виде списка.'
        )
    return homework


def parse_status(homework):
    '''
    Извлекаем информацию о домашней работе.
    '''
    logger.debug('Извлекаем информацию о домашней работе.')

    if 'homework_name' not in homework:
        logger.error('нет ключа "homework_name"')
        raise KeyError('нет ключа "homework_name"')

    if not homework['homework_name']:
        logger.error('Нет значения по ключу "homework_name"')
        raise KeyError('Нет значения по ключу "homework_name"')

    if 'status' not in homework:
        logger.error('нет ключа "status"')
        raise KeyError('нет ключа "status"')

    if not homework['status']:
        logger.error('Нет значения по ключу "status"')
        raise KeyError('Нет значения по ключу "status"')

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError:
        logger.error('Нет статуса в HOMEWORK_VERDICTS')
        raise exceptions.NoKeyInDict('Нет статуса в HOMEWORK_VERDICTS')

    logger.info(
        f'Изменился статус проверки работы "{homework_name}". {verdict}'
    )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    '''Основная логика работы бота.'''
    if not check_tokens():
        logger.critical('Отсутствуют одна или несколько переменных окружения.')
        raise KeyError('Отсутствуют одна или несколько переменных окружения.')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework_list = check_response(response)
            try:
                homework = homework_list[0]
            except IndexError:
                logger.critical('Нет новых заданий на проверке.')
                raise exceptions.NoNewHomework(
                    'Нет новых заданий на проверке.'
                )
            homework = homework_list[0]
            message = parse_status(homework)
            current_timestamp = response.get('current_date')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.critical(
                f'Уведомление об ошибке отправлено в чат {message}'
            )
        send_message(bot, message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
