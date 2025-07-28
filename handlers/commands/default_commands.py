from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat

from config import bot_username, recipients, db
from utils import write_log, LogType



def help(user_id: int):
    text = (
        '💬 <b>Список доступных команд:</b>\n'
        '<i>/start</i> — получить личную ссылку\n'
        '<i>/help</i> — получить помощь'
        '<i>/shop</i> — перейти в магазин'
    )
    send_telegram_message(
        user_id=user_id,
        text=text
    )


def shop(user_id: int, message_id: int=None):
    text = (
        '🛒 <b>Магазин</b> 🛒\n\n'
        'Здесь вы можете преобрести раскрытия и привилегии.'
    )

    message_id_text = '' if message_id is None else f':{message_id}'
    keyboard = {
        'inline_keyboard': [
            [
                {
                    'text': '🔍 Раскрытия 🔎',
                    'callback_data': f'reveal_shop{message_id_text}'
                }
            ],
            [
                {
                    'text': '⚜️ Привелегии ⚜️',
                    'callback_data': f'privilege_shop{message_id_text}'
                }
            ]
        ]
    }

    send_telegram_message(
        user_id=user_id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard
    )


def start(message, command: str, user_id: int):
    # Проверяем наличие параметра start в URL
    if 'entities' in message and any(entity.get('type') == 'bot_command' for entity in message['entities']):
        # Ищем параметр start в тексте сообщения
        start_param = message['text'].split(' ')[1] if len(message['text'].split()) > 1 else None
        if start_param:
            try:
                # Получаем ID получателя из параметра ссылки
                recipient_id = int(start_param)
                if (recipient_id == user_id):
                    send_telegram_message(
                        user_id=user_id,
                        text=f'<b>Вы не можете отправить сообщение самому себе!</b>'
                    )
                    return
                    
                recipients[user_id] = recipient_id  # Заносим в словарь ID получателя
                send_telegram_message(
                    user_id=user_id, 
                    text=(
                        '🌐 <b>Здесь вы можете отправить анонимное сообщение человеку, который опубликовал эту ссылку!</b>\n\n'
                        'Отправьте мне всё, что хочешь ему передать, и он сразу же получит твоё сообщение.\n\n'
                        'Отправить можно что угодно!\n'
                        '⚠️ <b>Все сообщения анонимны!</b>'
                    )
                )
                return
            
            except ValueError:
                write_log(f'Ошибка при обработке параметра команды {command}: {start_param}', LogType.ERROR)
                send_telegram_message(
                    user_id=user_id, 
                    text=(
                        '❌ <b>Не удалось распознать ID получателя.</b>\n'
                        '<i>Попробуйте перейти по ссылке ещё раз.</i>'
                    )
                )
                return
    
    # Отправляем сообщение с личный ссылкой пользователя
    try:
        if bot_username:
            personal_link = f'https://t.me/{bot_username}?start={user_id}'
            write_log(f'Сформирована персональная ссылка для пользователя {user_id}: {personal_link}')
            send_telegram_message(
                user_id=user_id, 
                text=(
                    '🌐 <b>Начни получать анонимные сообщения прямо сейчас!</b>\n\n'
                    'Твоя личная ссылка:\n'
                    f'👉 <code>{personal_link}</code>\n'
                    '<i><u>(нажмите на ссылку, чтобы скопировать её)</u></i>\n\n'
                    '💬 <i>Поделись этой ссылкой 👆 с друзьями или в своих соцсетях/блоге, чтобы начать получать анонимные сообщения!</i>'
                )
            )
        else:
            send_telegram_message(
                user_id=user_id, 
                text=(
                    '❌ <b>Не удалось сформировать персональную ссылку.</b>\n'
                    'Пожалуйста, попробуйте снова.'
                )
            )
    
    except Exception as e:
        write_log(f'Ошибка при получении информации о боте для пользователя {user_id}: {str(e)}', LogType.ERROR)
        send_telegram_message(
            user_id=user_id,
            text=(
                '❌ <b>Не удалось сформировать персональную ссылку.</b>\n'
                'Пожалуйста, попробуйте снова.'
            )
        )
