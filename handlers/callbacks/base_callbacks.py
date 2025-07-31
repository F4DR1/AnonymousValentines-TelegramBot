from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat
from telegram import get_bot_info, check_user_interaction, get_user_info

from config import recipients, db
from utils import write_log, LogType
from database import data



def find_out_id(user_id: int, sender_id: int, reply_to_message_id: int):
    # Получаем пользовательские статус
    user_status, _ = data.get_access(user_id=user_id)
    
    
    # Проверка на наличие доступа получения ID отправителя
    try:
        unlimited_reveal_access = bool(user_status[data.StatusAccesses.UNLIMITED_REVEAL.value])
        if not unlimited_reveal_access:
            db.open_connection()

            # Получить данные раскрытий пользователя из users, где id = user_id
            users_reveals = db.get_data(
                table='users',
                columns=[
                    'reveal_count'
                ],
                where_clause='id = ?',
                where_params=(user_id,)
            )
            user_reveal_count = users_reveals[0]['reveal_count'] if users_reveals else 0

            db.close_connection()
    
        # Получаем информацию о пользователе
        if unlimited_reveal_access or user_reveal_count > 0:
            sender_user_info = get_user_info(sender_id)
            sender_username = sender_user_info.get('username')
            
            # Добавляем username только если он есть
            link = f'@{sender_username}' if sender_username else f'<u><a href="tg://user?id={sender_id}">Открыть профиль</a></u>'

            # Вычитываем одно раскрытие (если у пользователя нет безлимитного раскрытия)
            if not unlimited_reveal_access:
                try:
                    db.open_connection()

                    new_user_reveal_count = user_reveal_count - 1

                    # Изменить значение раскрытий
                    db.save_data(
                        table='users',
                        data={
                            'reveal_count': new_user_reveal_count
                        },
                        where_clause='id = ?',
                        where_params=(user_id,)
                    )

                    # Отправляем сообщение с информацией о пользователе
                    send_telegram_message(
                        user_id=user_id,
                        text=(
                            f'🌐 <b>Отправитель:</b> {link}\n\nРаскрытий осталось: <i>{new_user_reveal_count} шт.</i>'
                        ),
                        reply_to_message_id=reply_to_message_id
                    )
                    return

                finally:
                    db.close_connection()
        
        else:
            send_telegram_message(
                user_id=user_id,
                text='❌ <b>У вас нет <i>раскрытий</i>!</b>',
                reply_to_message_id=reply_to_message_id,
                reply_markup={
                    'inline_keyboard': [
                        [
                            {
                                'text': '🛒 Перейти в магазин',
                                'callback_data': f'reveal_shop_new'
                            }
                        ]
                    ]
                }
            )
    
    except Exception as e:
        write_log(f'Ошибка при получении информации о пользователе: {str(e)}', LogType.ERROR)
        send_telegram_message(
            user_id=user_id,
            text='❌ <b>Не удалось получить информацию об отправителе</b>'
        )


def reply_to_message(user_id: int, sender_id: int, reply_to_message_id: int):
    # Заносим в словарь ID получателя
    recipients[user_id] = sender_id

    # Отправляем сообщение пользователю, что он может ответить на сообщение
    send_telegram_message(
        user_id=user_id,
        text=(
            '🌐 <b>Здесь вы можете отправить анонимное сообщение человеку, который опубликовал эту ссылку!</b>\n\n'
            'Отправьте мне всё, что хочешь ему передать, и он сразу же получит твоё сообщение.\n\n'
            'Отправить можно что угодно!\n'
            '⚠️ <b>Все сообщения анонимны!</b>'
        ),
        reply_to_message_id=reply_to_message_id
    )
    return
