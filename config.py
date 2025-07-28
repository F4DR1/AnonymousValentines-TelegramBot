import os
from dotenv import load_dotenv
import logging

from database.SQLiteDB import SQLiteDB


# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Хранит имя пользователя бота
bot_username = ''

# Хранит для каждого пользователя (его id) другого пользователя (другой id), которому первый хочет отправить сообщение
recipients = {}

db = SQLiteDB()


# Серверный адрес
SERVER_URL = os.getenv('SERVER_URL')

# URL вебхука
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# URL вебхука ЮKassa
YOOKASSA_WEBHOOK_URL = os.getenv('YOOKASSA_WEBHOOK_URL')
TEST_YOOKASSA_WEBHOOK_URL = os.getenv('TEST_YOOKASSA_WEBHOOK_URL')


# Путь к базе
DATABASE_URL = os.getenv('DATABASE_URL')


# Токен бота
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Секретный токен для webhook
WEBHOOK_SECRET_TOKEN = os.getenv('WEBHOOK_SECRET_TOKEN')



IS_TEST_PAYMENTS = True

# Магазин ЮKassa
YOOKASSA_ID = os.getenv('YOOKASSA_ID')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')

# Тестовый магазин ЮKassa
TEST_YOOKASSA_ID = os.getenv('TEST_YOOKASSA_ID')
TEST_YOOKASSA_SECRET_KEY = os.getenv('TEST_YOOKASSA_SECRET_KEY')



# Файл, хранящий дату последнего запуска бота
LAST_DATE_FILE = os.getenv('LAST_DATE_FILE')
daily_reveals = 5
max_daily_reveals = 20

# Проверяем наличие необходимых переменных окружения
if not SERVER_URL or not WEBHOOK_URL or not WEBHOOK_URL:
    raise ValueError("Необходимо указать SERVER_URL, WEBHOOK_URL, DATABASE_URL в файле .env")
if not TOKEN or not WEBHOOK_SECRET_TOKEN:
    raise ValueError("Необходимо указать TELEGRAM_BOT_TOKEN и WEBHOOK_SECRET_TOKEN в файле .env")
