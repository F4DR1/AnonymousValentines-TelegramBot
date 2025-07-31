from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat

from config import db



def reveal_shop(user_id: int, message_id: int=None):
    text = '🔍 <b>Текущий курс раскрытий</b> 🔎'
    keyboard = {
        'inline_keyboard': []
    }


    # Получаем все нужные данные из базы
    try:
        db.open_connection()

        # Получить все данные стоимостей из reveal_prices
        reveal_prices = db.get_data('reveal_prices')

    finally:
        db.close_connection()
    

    if reveal_prices is not None:
        # Записи с "available_count" == -1
        not_has_available_count = [item for item in reveal_prices if item['available_count'] == -1]

        # Количество записей с "available_count" > 0
        count_has_available_count = sum(1 for item in reveal_prices if item['available_count'] > 0)

        # Добавляем кнопки покупки
        add_buy_buttons(keyboard, not_has_available_count)

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


def promo_reveal_shop(user_id: int, message_id: int=None):
    text = '⚠️ <b>Раскрытия по АКЦИИ</b> ⚠️'
    keyboard = {
        'inline_keyboard': []
    }


    # Получаем все нужные данные из базы
    try:
        db.open_connection()

        # Получить все данные стоимостей из reveal_prices
        reveal_prices = db.get_data('reveal_prices')

    finally:
        db.close_connection()
    

    if reveal_prices is not None:
        # Записи с "available_count" > 0
        has_available_count = [item for item in reveal_prices if item['available_count'] > 0]

        # Добавляем кнопки покупки
        add_buy_buttons(keyboard, has_available_count)

    # Добавляем кнопку назад
    add_back_button(keyboard=keyboard, menu_name='reveal_shop')


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


def add_buy_buttons(keyboard, items):
    if len(items) > 0:
        for item in items:
            reveal_count = item['reveal_count']
            price = item['price']
            discount = item['discount']

            discounted_price = price * (100 - discount) / 100
            price_text = f'{discounted_price}₽   (-{discount}%)⚠️' if discount > 0 else f'{price}₽'

            button = [
                {
                    'text': f'{reveal_count} шт. | {price_text}',
                    'callback_data': f'buy_reveal:{reveal_count}:{discounted_price}'
                }
            ]
            # Добавляем кнопку как новую строку в клавиатуру
            keyboard['inline_keyboard'].append(button)
