import logging
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
