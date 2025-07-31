from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat

from config import recipients
from utils import write_log, LogType
from database import data

from handlers.commands import default_commands



def commands(message, user_id: int):
    # Удаляем пользователя из словаря получателей
    # (Если вдруг пользователь забыл про отправку сообщения и пошёл заниматься своими делами, а после что-то написал)
    if user_id in recipients:
        del recipients[user_id]


    # Получаем пользовательские статус и дату его окончания
    user_status, _ = data.get_access(user_id=user_id)

    premium_access = bool(user_status[data.StatusAccesses.PREMIUM.value])
    unlimited_reveal_access = bool(user_status[data.StatusAccesses.UNLIMITED_REVEAL.value])
    admin_access = bool(user_status[data.StatusAccesses.ADMIN.value])
    owner_access = bool(user_status[data.StatusAccesses.OWNER.value])

    command = message['text'].split()[0].lower()

    result = default(message=message, command=command, user_id=user_id)


    if not result:
        send_telegram_message(
            user_id=user_id,
            text=f'Команды {command} не существует...'
        )


def default(message, command: str, user_id: int):
    match command:
        case '/start':
            default_commands.start(message=message, command=command, user_id=user_id)
        case '/help':
            default_commands.help(user_id=user_id)
        case '/shop':
            default_commands.shop(user_id=user_id)
        case _:
            return False
    return True
