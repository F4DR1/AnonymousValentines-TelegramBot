from decimal import Decimal

from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat

from handlers.commands import default_commands
from handlers.callbacks import base_callbacks, reveal_shop_callbacks, privilege_shop_callbacks

from payments import create_payment, ProductTypes


def callbacks(callback_data, user_id: int):
    # Переход в магазин
    if callback_data.startswith('shop'):
        # Получаем ID сообщения
        parts = callback_data.split(':')
        message_id = parts[1] if len(parts) == 2 else None

        # Открываем магазин раскрытий
        default_commands.shop(user_id=user_id, message_id=message_id)
    

    # Переход в магазин раскрытий
    elif callback_data.startswith('reveal_shop'):
        # Получаем ID сообщения
        parts = callback_data.split(':')
        message_id = parts[1] if len(parts) == 2 else None

        # Открываем магазин раскрытий
        reveal_shop_callbacks.reveal_shop(user_id=user_id, message_id=message_id)
    
    # Переход в акционный магазин раскрытий
    elif callback_data.startswith('promo_reveal_shop'):
        # Получаем ID сообщения
        parts = callback_data.split(':')
        message_id = parts[1] if len(parts) == 2 else None

        # Открываем акционный магазин раскрытий
        reveal_shop_callbacks.promo_reveal_shop(user_id=user_id, message_id=message_id)


    # Переход в магазин привелегий
    elif callback_data.startswith('privilege_shop'):
        # Получаем ID сообщения
        parts = callback_data.split(':')
        message_id = parts[1] if len(parts) == 2 else None

        # Открываем магазин привелегий
        privilege_shop_callbacks.privilege_shop(user_id=user_id, can_go_back=message_id)
    
    # Переход в акционный магазин привелегий
    elif callback_data.startswith('promo_privilege_shop'):
        # Получаем ID сообщения
        parts = callback_data.split(':')
        message_id = parts[1] if len(parts) == 2 else None

        # Открываем акционный магазин привелегий
        privilege_shop_callbacks.promo_privilege_shop(user_id=user_id, can_go_back=message_id)


    
    # Покупка раскрытий
    elif callback_data.startswith('buy_reveal'):
        # Получаем количество и цену
        _, count, price = callback_data.split(':')
        
        payment_url = create_payment(
            amount=Decimal(price),
            description=f'Покупка {count} раскрытий',
            product_type=ProductTypes.Reveal,
            count=count
        )
        send_telegram_message(
            user_id=user_id,
            text=f'Оплатите [по ссылке]({payment_url})'
        )
    
    # Покупка привилегий
    elif callback_data.startswith('buy_privilege'):
        # Получаем количество и цену
        _, status_id, display_name, lvl, duration_days, price = callback_data.split(':')
        
        payment_url = create_payment(
            amount=Decimal(price),
            description=f'Покупка {display_name} привилегии {lvl} уровня на {duration_days} дн.',
            product_type=ProductTypes.Privilege,
            status_id=status_id,
            lvl=lvl,
            duration_days=duration_days
        )
        send_telegram_message(
            user_id=user_id,
            text=f'Оплатите [по ссылке]({payment_url})'
        )



    # Обработка получения ID отправителя
    elif callback_data.startswith('find_out_id:'):
        # Получаем ID отправителя
        _, sender_id = callback_data.split(':')

        # Получаем информацию о пользователе
        base_callbacks.find_out_id(user_id=user_id, sender_id=sender_id)
        return
    
    # Обработка отправки ответа по ID отправителя
    elif callback_data.startswith('reply_to_message:'):
        # Получаем ID отправителя
        _, sender_id = callback_data.split(':')

        # Отправляем ответное сообщение пользователю
        base_callbacks.reply_to_message(user_id=user_id, sender_id=sender_id)
        return
