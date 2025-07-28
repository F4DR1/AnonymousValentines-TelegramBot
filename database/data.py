import os
from datetime import datetime
from enum import Enum

from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat

from config import db, LAST_DATE_FILE
from config import daily_reveals, max_daily_reveals



class Status(Enum):
    DEFAULT = 'default'
    BLOCKED = 'blocked'
    PREMIUM = 'premium'
    TRUSTED = 'trusted'
    ADMIN = 'admin'
    OWNER = 'owner'

class StatusAccesses(Enum):
    DEFAULT = 'default_access'
    PREMIUM = 'premium_access'
    UNLIMITED_REVEAL = 'unlimited_reveal_access'
    ADMIN = 'admin_access'
    OWNER = 'owner_access'



def get_all_data(user_id: int):
    # Получаем все нужные данные из базы
    try:
        db.open_connection()


        # Получить все данные статусов из таблицы user_statuses
        all_user_statuses = db.get_data('user_statuses')


        # Получить все данные пользователя из users, где id = user_id
        users = db.get_data('users', where_clause='id = ?', where_params=[user_id])
        user = users[0] if users else None


        # Проверка наличия данных пользователя
        if user is None:
            # Создаём user
            user = {
                'id': user_id,
                'reveal_count': 0,
                'user_status_id': 1
            }

            # Вызов метода записи user в базу в таблицу users
            db.save_data(table='users', data={'id': user['id'], 'reveal_count': user['reveal_count'], 'user_status_id': user['user_status_id']})

    finally:
        db.close_connection()
        return (user, all_user_statuses)


def get_access(user_id: int):
    user, all_user_statuses = get_all_data(user_id=user_id)
    
    # Находим статус с нужным id из all_user_statuses
    status = next((status for status in all_user_statuses if status['id'] == user['user_status_id']), None)
    if status:
        return (status, user['user_status_end_date'])
    else:
        status = next((status for status in all_user_statuses if status['name'] == Status.DEFAULT.value))
        return (status,)




def daily():
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Проверяем, есть ли файл с датой
    if os.path.exists(LAST_DATE_FILE):
        with open(LAST_DATE_FILE, 'r', encoding='utf-8') as f:
            last_date_str = f.read().strip()
    else:
        last_date_str = None

    # Дата в файле отличается от сегодняшней - вызываем ежедневные методы
    if last_date_str != today_str:
        give_daily_reveals  # Выдаём ежедневную валюту

        # Записываем сегодняшнюю дату
        with open(LAST_DATE_FILE, 'w', encoding='utf-8') as f:
            f.write(today_str)


def give_daily_reveals():
    try:
        db.open_connection()


        # Получить id дефолтного статуса
        all_user_statuses = db.get_data('user_statuses')
        premium_status = next((item for item in all_user_statuses if item['name'] == Status.DEFAULT.value), None)
        if premium_status is not None:
            premium_status_id = premium_status['id']
        else:
            premium_status_id = 1


        # Получить все данные пользователей из users, где user_status_id = premium_status_id
        users = db.get_data('users', where_clause='user_status_id != ?', where_params=[premium_status_id])

        # Выдаём всем премиумам раскрытия
        for user in users:
            user_reveal_count = user['reveal_count']
            
            gived_reveals = 0
            
            # Если на балансе раскрытий меньше, чем максимум раскрытий для премиума
            if user_reveal_count < max_daily_reveals:
                # Новое количество раскрытий
                new_user_reveal_count = user_reveal_count + daily_reveals
                if new_user_reveal_count > max_daily_reveals:
                    new_user_reveal_count = max_daily_reveals
                
                gived_reveals = new_user_reveal_count - user_reveal_count
                user['reveal_count'] = new_user_reveal_count

                # Вызов метода записи user в базу в таблицу users
                db.save_data(table='users', data={'id': user['id'], 'reveal_count': user['reveal_count'], 'user_status_id': user['user_status_id']})
            
            # Сообщаем пользователю о начислении
            send_telegram_message(
                user_id=user['id'],
                text=(
                    '⚜️ <b>Ежедневные раскрытия</b> ⚜️\n'
                    f'Сегодня вы получили <u>{gived_reveals} раскрытий</u>\n'
                    f'Текущее количество раскрытий: <i>{user['reveal_count']} шт.</i>\n\n'
                    f'💬 <i>Учтите, что если у вас больше <u>{max_daily_reveals} раскрытий</u>, то вам ничего не выдастся!</i>'
                )
            )

    finally:
        db.close_connection()

        


def update_statuses():
    try:
        db.open_connection()


        # Получить id дефолтного статуса
        all_user_statuses = db.get_data('user_statuses')
        default_status = next((item for item in all_user_statuses if item['name'] == Status.DEFAULT.value), None)
        if default_status is not None:
            default_status_id = default_status['id']
        else:
            default_status_id = 1


        # Получить все данные пользователей из users, где user_status_id = default_status_id
        users = db.get_data('users', where_clause='user_status_id != ?', where_params=[default_status_id])
        

        # Обновляем статусы
        if users is not None:
            for user in users:
                # Дата и время окончания статуса
                user_status_end_date_str = user['user_status_end_date']
                end_date = datetime.strptime(user_status_end_date_str, '%Y-%m-%d %H:%M:%S')

                # Текущие дата и время
                now = datetime.now()

                # Если вышел срок - сбрасываем
                if now > end_date:
                    user['user_status_id'] = default_status_id
                    user_status_end_date_str = None

                    # Вызов метода записи user в базу в таблицу users
                    db.save_data(table='users', data={'id': user['id'], 'reveal_count': user['reveal_count'], 'user_status_id': user['user_status_id']})

                    # Сообщаем пользователю об окончании привилегии
                    send_telegram_message(
                        user_id=user['id'],
                        text='🕙 <b>Время действия привилегии истекло!</b>\n',
                        reply_markup={
                            'inline_keyboard': [
                                [
                                    {
                                        'text': '🛒 Перейти в магазин',
                                        'callback_data': f'privilege_shop'
                                    }
                                ]
                            ]
                        }
                    )

    finally:
        db.close_connection()
