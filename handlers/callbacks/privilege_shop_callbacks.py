from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat

from config import db
from config import daily_reveals, max_daily_reveals

privilege_description = (
    '<b>Привилегии позволяют получить некоторые преимущества:</b>\n'
    f'<u>Премиум</u> – позволяет получать по <i>{daily_reveals} раскрытий</i> раз в день (но не более <i>{max_daily_reveals} раскрытий</i>!)'
)



def privilege_shop(user_id: int, message_id: int=None):
    text = '⚜️ <b>Привилегии</b> ⚜️\n\n' + privilege_description
    keyboard = {
        'inline_keyboard': []
    }


    # Получаем все нужные данные из базы
    try:
        db.open_connection()

        # Получить все данные статусов из таблицы user_statuses
        all_user_statuses = db.get_data('user_statuses')

        # Получить все данные стоимостей из status_prices
        status_prices = db.get_data('status_prices')

    finally:
        db.close_connection()
    
    
    if status_prices is not None:
        # Записи с "available_count" == -1
        not_has_available_count = [item for item in status_prices if item['available_count'] == -1]

        # Количество записей с "available_count" > 0
        count_has_available_count = sum(1 for item in status_prices if item['available_count'] > 0)

        # Добавляем кнопки покупки
        add_buy_buttons(keyboard, all_user_statuses, not_has_available_count)
        
        # Добавляем кнопку перехода в акционный магазин
        if count_has_available_count > 0:
            promo_button = [
                {
                    'text': '⚠️ АКЦИИ ⚠️',
                    'callback_data': 'promo_reveal_shop'
                }
            ]
            # Добавляем кнопку как новую строку в клавиатуру
            keyboard['inline_keyboard'].append(promo_button)

    # Добавляем кнопку назад
    add_back_button(keyboard=keyboard, menu_name='shop')
    

    send_telegram_message(
        user_id=user_id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard if keyboard['inline_keyboard'] else None
    )


def promo_privilege_shop(user_id: int, message_id: int=None):
    text = '⚠️ <b>Привилегии по АКЦИИ</b> ⚠️\n\n' + privilege_description
    keyboard = {
        'inline_keyboard': []
    }


    # Получаем все нужные данные из базы
    try:
        db.open_connection()

        # Получить все данные статусов из таблицы user_statuses
        all_user_statuses = db.get_data('user_statuses')

        # Получить все данные стоимостей из status_prices
        status_prices = db.get_data('status_prices')

    finally:
        db.close_connection()
    
    
    if status_prices is not None:
        # Записи с "available_count" > 0
        has_available_count = [item for item in status_prices if item['available_count'] > 0]

        # Добавляем кнопки покупки
        add_buy_buttons(keyboard, all_user_statuses, has_available_count)

    # Добавляем кнопку назад
    add_back_button(keyboard=keyboard, menu_name='privilege_shop')
    

    send_telegram_message(
        user_id=user_id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard if keyboard['inline_keyboard'] else None
    )





def add_back_button(keyboard, menu_name):
    back_button = [
        {
            'text': '← Назад',
            'callback_data': menu_name
        }
    ]
    # Добавляем кнопку как новую строку в клавиатуру
    keyboard['inline_keyboard'].append(back_button)


def add_buy_buttons(keyboard, all_user_statuses, items):
    if len(items) > 0:
        for item in items:
            status_id = item['user_status_id']
            level = item['lvl']
            duration_days = item['duration_days']
            price = item['price']
            discount = item['discount']

            discounted_price = price * (100 - discount) / 100
            price_text = f'{discounted_price}₽   (-{discount}%)⚠️' if discount > 0 else f'{price}₽'


            status = next((item for item in all_user_statuses if item['id'] == status_id), None)
            display_name = status['display_name']

            button = [
                {
                    'text': f'{display_name} | {duration_days} дн. | {price_text}',
                    'callback_data': f'buy_privilege:{status_id}:{display_name}:{level}:{duration_days}:{discounted_price}'
                }
            ]
            # Добавляем кнопку как новую строку в клавиатуру
            keyboard['inline_keyboard'].append(button)