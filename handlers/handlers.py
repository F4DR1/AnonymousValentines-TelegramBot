import datetime
from urllib.parse import quote

from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat
from telegram import get_bot_info, check_user_interaction, get_user_info

from config import recipients
from utils import write_log, LogType
from database import data

from handlers.messages.messages import messages
from handlers.commands.commands import commands
from handlers.callbacks.callbacks import callbacks

def process_message(message):
    """
    Обрабатывает входящее сообщение
    :param message: сообщение от пользователя
    """
    try:
        # Не даём пользоваться ботом в группах
        if message['chat']['type'] != 'private':
            # Игнорируем сообщения из групповых чатов
            chat_id = message['chat']['id']  # Получаем ID чата
            send_telegram_message(
                user_id=chat_id,
                text=f'Бот работает только в личных сообщениях!'
            )
            return



        # Получаем ID пользователя
        user_id = message['from']['id']
        user_message_id = message['message_id']

        # Получаем пользовательские статус и дату его окончания
        user_status, user_status_end_date = data.get_access(user_id=user_id)


        # Если у пользователя нет стандартного доступа (пользователь заблокирован)
        if not bool(user_status[data.StatusAccesses.DEFAULT.value]):
            date_obj = datetime.strptime(user_status_end_date, "%Y-%m-%d")
            block_end = date_obj.strftime("%d.%m.%Y")
            send_telegram_message(
                user_id=user_id,
                text=(
                    '⚠️ <b>Вы были заблокированы в нашем боте!</b> ⚠️\n'
                    f'Блокировка продлится до: <i>{block_end}</i>'
                )
            )
            return
        
        # Если у пользователя есть стандартный доступ
        else:
            if 'text' in message and message['text'].startswith('/'):
                commands(message=message, user_id=user_id)  # Если это команда
            else:
                messages(message=message, user_id=user_id, reply_to_message=user_message_id)  # Если любое другое сообщение
    
    except Exception as e:
        write_log(f'Ошибка при обработке message: {str(e)}', LogType.ERROR)
        send_telegram_message(
            user_id=user_id,
            text=(
                '⚠️ <b>Не удалось отправить сообщение</b>\n'
                'Попробуйте снова... Если ошибка повторится - свяжитесь с разработчиком.'
            )
        )


def process_callback_query(callback_query):
    """
    Обрабатывает callback_query
    callback_query: callback_query от пользователя
    """
    try:
        # Получаем ID пользователя
        user_id = callback_query['from']['id']
        message_id = callback_query['message']['message_id']
        
        # Удаляем пользователя из словаря получателей
        if user_id in recipients:
            del recipients[user_id]

        callback_data = callback_query['data']
        callbacks(
            callback_data=callback_data,
            user_id=user_id,
            message_id=message_id
        )
    
    except Exception as e:
        write_log(f'Ошибка при обработке callback_query: {str(e)}', LogType.ERROR)
