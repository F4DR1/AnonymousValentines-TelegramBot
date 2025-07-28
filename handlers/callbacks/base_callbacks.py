from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat
from telegram import get_bot_info, check_user_interaction, get_user_info

from config import recipients, db
from utils import write_log, LogType
from database import data



def find_out_id(user_id: int, sender_id: int):
    # Получаем пользовательские статус
    user_status, _ = data.get_access(user_id=user_id)
    
    
    # Проверка на наличие доступа получения ID отправителя
    unlimited_reveal_access = bool(user_status[data.StatusAccesses.UNLIMITED_REVEAL.value])
    if not unlimited_reveal_access:
        try:
            db.open_connection()

            # Получить данные раскрытий пользователя из users, где id = user_id
            users_reveals = db.get_data('users', columns=['reveal_count'], where_clause='id = ?', where_params=[user_id])
            user_reveal_count = users_reveals[0] if users_reveals else 0

        finally:
            db.close_connection()
    

    # Получаем информацию о пользователе
    try:
        if unlimited_reveal_access or user_reveal_count > 0:
            sender_user_info = get_user_info(sender_id)
            sender_username = sender_user_info.get('username')
            
            # # Добавляем username только если он есть
            # if sender_username:
            #     username_link = f'@{sender_username}'
            # else:
            #     username_link = '<i><u>Отсутствует</u></i>'
            
            # Добавляем ссылку на профиль
            profile_link = f'<a href="tg://user?id={sender_id}">Открыть профиль</a>'


            # Вычитываем одно раскрытие (если у пользователя нет безлимитного раскрытия)
            if not unlimited_reveal_access:
                try:
                    db.open_connection()

                    # Изменить значение раскрытий
                    db.save_data(
                        table='users',
                        data={'reveal_count': user_reveal_count - 1},
                        where_clause='id = ?',
                        where_params=[user_id]
                    )

                finally:
                    db.close_connection()
            
            # Отправляем сообщение с информацией о пользователе
            send_telegram_message(
                user_id=user_id,
                text=(
                    '🌐 <b>Отправитель:</b>\n\n'
                    # f'Имя пользователя: {username_link}\n'
                    f'Ссылка на профиль: {profile_link}\n\n'
                    '<i><u>(по каким-то причинам ссылка на профиль может не работать)</u></i>'
                )
            )
            return
        else:
            send_telegram_message(
                user_id=user_id,
                text='❌ <b>У вас нет <i>раскрытий</i>!</b>',
                reply_markup={
                    'inline_keyboard': [
                        [
                            {
                                'text': '🛒 Перейти в магазин',
                                'callback_data': f'reveal_shop'
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


def reply_to_message(user_id: int, sender_id: int):
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
        )
    )
    return
