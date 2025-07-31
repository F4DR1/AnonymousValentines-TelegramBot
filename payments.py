from enum import Enum
from decimal import Decimal
from datetime import datetime, timedelta
import uuid
from yookassa import Payment, Configuration

from config import db, YOOKASSA_ID, YOOKASSA_SECRET_KEY
from utils import write_log, LogType

from telegram import get_bot_info, send_telegram_message



class ProductTypes(Enum):
    Reveal = 1
    Privilege = 2


def set_yookassa_configuration():
    Configuration.configure(YOOKASSA_ID, YOOKASSA_SECRET_KEY)

def valid_amount(amount: str):
    """
    Производит валидацию суммы к формату float.
    """
    try:
        amount_dec = Decimal(amount)

        # Нормализуем до 2 знаков (100 → 100.00)
        normalized_amount = amount_dec.quantize(Decimal('0.00'))
        
        # Проверка диапазона (0.01 - 1_000_000 RUB)
        if not (Decimal('0.01') <= normalized_amount <= Decimal('1000000.00')):
            raise ValueError('Сумма должна быть от 0.01 до 1 000 000 RUB')
        
        # Используем normalized_amount для платежа
        return float(normalized_amount)
    
    except Exception as e:
        write_log(f'Не удалось валидировать сумму для платежа', LogType.ERROR)
        raise



def create_payment(
    amount: str,
    description: str,
    user_id: int,
    product_type: int,
    count: int = None,
    status_id: int = None,
    lvl: int = None,
    duration_days: int = None,
    message_id: int = None
):
    """
    Создает платеж в ЮKassa и возвращает URL для оплаты.
    В случае ошибки отправляет сообщение в Telegram.
    """
    try:
        if product_type is None:
            raise ValueError('Не был указан тип продукта!!!')
        
        metadata = {
            'user_id': user_id,
            'product_type': product_type
        }
        match product_type:
            case ProductTypes.Reveal.value:
                if count is None:
                    raise ValueError(f'Одно из обязательных значений пусто: count={count}')
                
                metadata.update({
                    'count': count
                })
            case ProductTypes.Privilege.value:
                if status_id is None or lvl is None or duration_days is None:
                    raise ValueError(f'Одно из обязательных значений пусто: status_id={status_id}; lvl={lvl}; duration_days={duration_days}')
                
                metadata.update({
                    'status_id': status_id,
                    'lvl': lvl,
                    'duration_days': duration_days
                })


        bot_info = get_bot_info()
        if not bot_info or not bot_info.get('username'):
            raise ValueError('Не удалось получить имя пользователя бота...')
        
        bot_username = bot_info.get('username')
        set_yookassa_configuration()
        payment = Payment.create({
            'amount': {
                'value': valid_amount(amount=amount),
                'currency': 'RUB'
            },
            'confirmation': {
                'type': 'redirect',
                'return_url': f'https://t.me/{bot_username}'
            },
            'capture': True,
            'description': description,
            'metadata': metadata  # Добавляем метаданные (все нужные данные для дальнейшей обработки платежа)
        }, uuid.uuid4())
        payment_url = payment.confirmation.confirmation_url  # Ссылка для оплаты
        send_telegram_message(
            user_id=user_id,
            text=description,
            message_id=message_id,
            reply_markup={
                'inline_keyboard': [
                    [
                        {
                            'text': 'Оплатить',
                            'url': payment_url
                        }
                    ]
                ]
            }
        )
    
    except Exception as e:
        write_log(f'Ошибка при оплате для пользователя {user_id}: {str(e)}', LogType.ERROR)
        send_telegram_message(
            user_id=user_id,
            text=(
                '❌ <b>Не удалось сформировать ссылку для оплаты.</b>\n'
                'Пожалуйста, попробуйте позже...'
            )
        )
    




def payment_processing(request_json, is_test_mode):
    set_yookassa_configuration()

    # Получаем информацию о платеже (проверка на всякий случай)
    payment_data = request_json.get('object')
    payment_id = payment_data.get('id')
    finded_payment = Payment.find_one(payment_id)

    # Статус платежа
    match finded_payment['status']:
        # Обработка успешного платежа
        case 'succeeded':
            if not is_test_mode:
                combat_payment_succeeded(payment_data=payment_data)
            else:
                test_payment_succeeded(payment_data=payment_data)



def combat_payment_succeeded(payment_data):
    # Данные для обработки платежа
    metadata = payment_data.get('metadata', {})
    

    amount = payment_data['amount']['value']
    user_id = int(metadata.get('user_id'))

    write_log(f'Успешный платеж {amount} RUB от user_id={user_id}', LogType.INFO)

    
    try:
        db.open_connection()

        product_type = int(metadata.get('product_type'))
        match product_type:
            case ProductTypes.Reveal.value:
                count = int(metadata.get('count'))

                write_log(f'[ПОКУПКА] Выдаём user_id={user_id} раскрытия в кол-ве: {count} шт.', LogType.INFO)

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
                    text=f'✅ Покупка <i>{count} шт. раскрытий</i> прошла успешно!\n\nТекущий баланс раскрытий: <i>{new_user_reveal_count} шт.</i>'
                )
                
                write_log(f'[ПОКУПКА] Было выдано user_id={user_id} раскрытия в кол-ве: {count} шт. Было: {user_reveal_count}; стало: {new_user_reveal_count}', LogType.INFO)
            
            case ProductTypes.Privilege.value:
                status_id = int(metadata.get('status_id'))
                lvl = int(metadata.get('lvl'))
                duration_days = int(metadata.get('duration_days'))
                status_end_date = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d')
                
                date_obj = datetime.strptime(status_end_date, "%Y-%m-%d")
                privilege_end = date_obj.strftime("%d.%m.%Y")

                write_log(f'[ПОКУПКА] Выдаём user_id={user_id} статус status_id={status_id} lvl={lvl} на duration_days={duration_days} до {privilege_end} числа', LogType.INFO)

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
                    text=f'✅ Покупка привилегии <i>{display_name}</i> на <i>{duration_days} дн.</i> прошла успешно! Дата окончания действия привилегии: {privilege_end}'
                )
                
                write_log(f'[ПОКУПКА] Было выдано user_id={user_id} статус status_id={status_id} lvl={lvl} на duration_days={duration_days} до {privilege_end} числа', LogType.INFO)

    finally:
        db.close_connection()

def test_payment_succeeded(payment_data):
    # Данные для обработки платежа
    metadata = payment_data.get('metadata', {})
    

    amount = payment_data['amount']['value']
    user_id = int(metadata.get('user_id'))

    write_log(f'Успешный тестовый платеж amount={amount} RUB от user_id={user_id}', LogType.INFO)


    product_type = int(metadata.get('product_type'))
    match product_type:
        case ProductTypes.Reveal.value:
            count = int(metadata.get('count'))
            send_telegram_message(
                user_id=user_id,
                text=f'✅ Тестовая покупка {count} шт. раскрытий прошла успешно!'
            )
        
        case ProductTypes.Privilege.value:
            status_id = int(metadata.get('status_id'))
            lvl = int(metadata.get('lvl'))
            duration_days = int(metadata.get('duration_days'))
            status_end_date = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d')
            send_telegram_message(
                user_id=user_id,
                text=f'✅ Тестовая покупка привилегии {status_id} {lvl} уровня на {duration_days} дн. до {status_end_date} прошла успешно!'
            )
