import os
from dotenv import load_dotenv

from yookassa import Configuration as yooConfiguration

from database.SQLiteDB import SQLiteDB

from utils import write_log



# Загружаем переменные окружения из .env файла
load_dotenv()



# Серверный адрес, URL вебхука и секретный токен вебхука
SERVER_URL = os.getenv('SERVER_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_SECRET_TOKEN = os.getenv('WEBHOOK_SECRET_TOKEN')

# Токен бота
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')



# ID магазина, секретный ключ и URL вебхука ЮKassa
IS_TEST_PAYMENTS = True
if not IS_TEST_PAYMENTS:
    YOOKASSA_ID = os.getenv('YOOKASSA_ID')
    YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')
    YOOKASSA_WEBHOOK_URL = os.getenv('YOOKASSA_WEBHOOK_URL')
else:
    YOOKASSA_ID = os.getenv('TEST_YOOKASSA_ID')
    YOOKASSA_SECRET_KEY = os.getenv('TEST_YOOKASSA_SECRET_KEY')
    YOOKASSA_WEBHOOK_URL = os.getenv('TEST_YOOKASSA_WEBHOOK_URL')



# Путь к базе
DATABASE_FILE = os.getenv('DATABASE_FILE')
db = SQLiteDB(DATABASE_FILE)

# Файл, хранящий дату последнего запуска бота
LAST_DATE_FILE = os.getenv('LAST_DATE_FILE')



# Хранит для каждого пользователя (его id) другого пользователя (другой id), которому первый хочет отправить сообщение
recipients = {}

# Значения для работы
daily_reveals = 5  # Сколько раскрытий в день выдавать премиумам
max_daily_reveals = 20  # Ограничение счёта раскрытий для дневной выдачи раскрытий премиумам



# Проверяем наличие необходимых переменных окружения
if not SERVER_URL or not WEBHOOK_URL or not WEBHOOK_URL:
    raise ValueError('Необходимо указать SERVER_URL, WEBHOOK_URL, DATABASE_URL в файле .env')
if not TOKEN or not WEBHOOK_SECRET_TOKEN:
    raise ValueError('Необходимо указать TELEGRAM_BOT_TOKEN и WEBHOOK_SECRET_TOKEN в файле .env')
if not YOOKASSA_ID or not YOOKASSA_SECRET_KEY:
    if not IS_TEST_PAYMENTS:
        raise ValueError('Необходимо указать YOOKASSA_ID и YOOKASSA_SECRET_KEY в файле .env')
    else:
        raise ValueError('Необходимо указать TEST_YOOKASSA_ID и TEST_YOOKASSA_SECRET_KEY в файле .env')
