from enum import Enum
from datetime import datetime, timedelta

from yookassa import Payment

from config import bot_username, db
from utils import write_log, LogType

from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat


class ProductTypes(Enum):
    Reveal = 1
    Privilege = 2



def create_payment(amount: int, description: str, user_id: int, product_type: int, count: int, status_id: int, lvl: int, duration_days: int):
    match product_type:
        case ProductTypes.Reveal:
            metadata = {
                'user_id': user_id,
                'product_type': product_type,
                'count': count
            }
        case ProductTypes.Privilege:
            metadata = {
                'user_id': user_id,
                'product_type': product_type,
                'status_id': status_id,
                'lvl': lvl,
                'duration_days': duration_days
            }

    payment = Payment.create({
        'amount': {
            'value': amount,
            'currency': 'RUB'
        },
        'capture': True,
        'confirmation': {
            'type': 'redirect',
            'return_url': f'https://t.me/{bot_username}'
        },
        'description': description,
        'metadata': metadata  # Добавляем метаданные (все нужные данные для дальнейшей обработки платежа)
    })
    return payment.confirmation.confirmation_url  # Ссылка для оплаты



def payment_processing(data):
    event = data.get('event')
        
    # Обработка успешного платежа
    if event == 'payment.succeeded':
        payment = data['object']

        # Данные для обработки платежа
        metadata = payment.get('metadata', {})
        

        amount = payment['amount']['value']
        user_id = metadata.get('user_id')

        write_log(f'Успешный платеж {amount} RUB от user_id={user_id}', LogType.INFO)


        product_type = metadata.get('product_type')
        match product_type:
            case ProductTypes.Reveal:
                count = metadata.get('count')
                try:
                    db.open_connection()

                    write_log(f'Выдаём user_id={user_id} раскрытия в кол-ве: {count} шт.', LogType.INFO)

                    # Получить данные раскрытий пользователя из users, где id = user_id
                    users_reveals = db.get_data('users', columns=['reveal_count'], where_clause='id = ?', where_params=[user_id])
                    user_reveal_count = users_reveals[0] if users_reveals else 0

                    new_user_reveal_count = user_reveal_count + count

                    # Изменить значение раскрытий
                    db.save_data(
                        table='users',
                        data={'reveal_count': new_user_reveal_count},
                        where_clause='id = ?',
                        where_params=[user_id]
                    )

                    send_telegram_message(
                        user_id=user_id,
                        text=f'✅ Покупка <u>{count} раскрытий</u> прошла успешно!\n\nТекущий баланс раскрытий: <i>{new_user_reveal_count} шт.</i>'
                    )
                    
                    write_log(f'Было выдано user_id={user_id} раскрытия в кол-ве: {count} шт. Было: {user_reveal_count}; стало: {new_user_reveal_count}', LogType.INFO)

                finally:
                    db.close_connection()
            
            case ProductTypes.Privilege:
                status_id = metadata.get('status_id')
                lvl = metadata.get('lvl')
                duration_days = metadata.get('duration_days')
                status_end_date = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d')
                try:
                    db.open_connection()

                    write_log(f'Выдаём user_id={user_id} статус status_id={status_id} lvl={lvl} на duration_days={duration_days} до {status_end_date} числа', LogType.INFO)

                    # Получить все данные статусов из таблицы user_statuses
                    all_user_statuses = db.get_data('user_statuses')
                    status = next((item for item in all_user_statuses if item['id'] == status_id), None)
                    display_name = status['display_name']

                    # Изменить значение раскрытий
                    db.save_data(
                        table='users',
                        data={'user_status_id': status_id, 'user_status_lvl': lvl, 'user_status_end_date': status_end_date},
                        where_clause='id = ?',
                        where_params=[user_id]
                    )

                    send_telegram_message(
                        user_id=user_id,
                        text=f'✅ Покупка привилегии <u>{display_name}</u> на <u>{duration_days} дн.</u> прошла успешно! Дата окончания действия привилегии: {status_end_date}'
                    )
                    
                    write_log(f'Было выдано user_id={user_id} статус status_id={status_id} lvl={lvl} на duration_days={duration_days} до {status_end_date} числа', LogType.INFO)

                finally:
                    db.close_connection()



def test_payment_processing(data):
    event = data.get('event')
        
    # Обработка успешного платежа
    if event == 'payment.succeeded':
        payment = data['object']

        # Данные для обработки платежа
        metadata = payment.get('metadata', {})
        

        amount = payment['amount']['value']
        user_id = metadata.get('user_id')

        write_log(f'Успешный тестовый платеж {amount} RUB от user_id={user_id}', LogType.INFO)


        product_type = metadata.get('product_type')
        match product_type:
            case ProductTypes.Reveal:
                count = metadata.get('count')
                send_telegram_message(
                    user_id=user_id,
                    text=f'✅ Тестовая покупка <u>{count} раскрытий</u> прошла успешно!'
                )
            
            case ProductTypes.Privilege:
                status_id = metadata.get('status_id')
                lvl = metadata.get('lvl')
                duration_days = metadata.get('duration_days')
                status_end_date = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d')
                send_telegram_message(
                    user_id=user_id,
                    text=f'✅ Тестовая покупка привилегии <u>{status_id}</u> на <u>{duration_days} дн.</u> прошла успешно! Дата окончания действия привилегии: {status_end_date}'
                )
