import logging
from config import TOKEN
import requests
from enum import Enum

# # Настройка логирования (добавляем перед определением функции)
# logging.basicConfig(
#     filename='logs.log',
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

class LogType(Enum):
    INFO = 'Запись'
    ERROR = 'Ошибка'
    WARNING = 'Попытка взлома'
    CRITICAL = 'Критическая ошибка'

def write_log(message, log_type=LogType.INFO):
    """
    Функция для записи логов в файл
    message: сообщение для записи
    log_type: тип записи (по умолчанию INFO)
    """
    if log_type == LogType.INFO:
        logging.info(message)
    elif log_type == LogType.ERROR:
        logging.error(message)
    elif log_type == LogType.WARNING:
        logging.warning(message)
    elif log_type == LogType.CRITICAL:
        logging.critical(message)
    else:
        raise ValueError(f'Неизвестный тип лога: {log_type}')

def check_user_interaction(user_id):
    """
    Проверяет, взаимодействовал ли пользователь с ботом
    user_id: ID пользователя для проверки
    Возвращает True, если пользователь взаимодействовал с ботом, False в противном случае
    """
    try:
        # Пробуем получить информацию о чате с пользователем
        url = f'https://api.telegram.org/bot{TOKEN}/getChat'
        params = {
            'chat_id': user_id
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if '400' in str(e):  # 400 Bad Request означает, что пользователь не взаимодействовал с ботом
            return False
        raise ValueError(f'Ошибка при проверке пользователя: {str(e)}')

def get_user_info(user_id):
    """
    Получает информацию о пользователе
    user_id: ID пользователя для получения информации
    Возвращает информацию о пользователе
    """
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/getChat'
        params = {
            'chat_id': user_id
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("ok"):
            return data["result"]  # Возвращаем данные о пользователе
        return None  # Если API ответил, но данных нет, возвращаем None
    except requests.exceptions.RequestException as e:
        if '400' in str(e):  # 400 Bad Request означает, что пользователь не взаимодействовал с ботом
            return None
        raise ValueError(f'Ошибка при получении информации о пользователе: {str(e)}')
