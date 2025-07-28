import os
from dotenv import load_dotenv
import logging

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

# Словарь для хранения ID получателей
recipients = {}

# Список пользователь с полным доступом
FULL_ACCESS_USERS = []  # Сделать хранение через базу

# Серверный адрес
SERVER_URL = os.getenv('SERVER_URL')

# URL вебхука
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Токен бота
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Секретный токен для webhook
WEBHOOK_SECRET_TOKEN = os.getenv('WEBHOOK_SECRET_TOKEN')

# Проверяем наличие необходимых переменных окружения
if not SERVER_URL or not WEBHOOK_URL:
    raise ValueError("Необходимо указать SERVER_URL и WEBHOOK_URL в файле .env")
if not TOKEN or not WEBHOOK_SECRET_TOKEN:
    raise ValueError("Необходимо указать TELEGRAM_BOT_TOKEN и WEBHOOK_SECRET_TOKEN в файле .env")
