import logging
from enum import Enum



# Имя файла с логами
LOGS_FILE_NAME = 'bot.log'

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_FILE_NAME),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



class LogType(Enum):
    INFO = 'Запись'
    ERROR = 'Ошибка'
    WARNING = 'Попытка взлома'
    CRITICAL = 'Критическая ошибка'



def write_log(
    message,
    log_type: LogType = LogType.INFO
):
    """
    Функция для записи логов в файл

    :param message: сообщение для записи
    :param log_type: тип записи (по умолчанию INFO)
    """
    match log_type:
        case LogType.INFO:
            logging.info(message)
        case LogType.ERROR:
            logging.error(message)
        case LogType.WARNING:
            logging.warning(message)
        case LogType.CRITICAL:
            logging.critical(message)
        case _:
            raise ValueError(f'Неизвестный тип лога: {log_type}')
