from handlers.commands import default_commands
from handlers.callbacks import base_callbacks, reveal_shop_callbacks, privilege_shop_callbacks

from payments import create_payment, ProductTypes


def callbacks(callback_data, user_id: int, message_id: int):
    # Переход в магазин
    if callback_data == 'shop':
        default_commands.shop(user_id=user_id, message_id=message_id)
    

    # Переход в магазин раскрытий (без замены сообщения)
    elif callback_data == 'reveal_shop_new':
        reveal_shop_callbacks.reveal_shop(user_id=user_id)
    
    # Переход в магазин раскрытий
    elif callback_data == 'reveal_shop':
        reveal_shop_callbacks.reveal_shop(user_id=user_id, message_id=message_id)
    
    # Переход в акционный магазин раскрытий
    elif callback_data == 'promo_reveal_shop':
        reveal_shop_callbacks.promo_reveal_shop(user_id=user_id, message_id=message_id)


    # Переход в магазин привелегий
    elif callback_data == 'privilege_shop':
        privilege_shop_callbacks.privilege_shop(user_id=user_id, message_id=message_id)
    
    # Переход в акционный магазин привелегий
    elif callback_data == 'promo_privilege_shop':
        privilege_shop_callbacks.promo_privilege_shop(user_id=user_id, message_id=message_id)


    
    # Покупка раскрытий
    elif callback_data.startswith('buy_reveal'):
        # Получаем количество и цену
        _, count, price = callback_data.split(':')
        
        create_payment(
            message_id=message_id,
            amount=price,
            description=f'Покупка {count} шт. раскрытий',
            user_id=user_id,
            product_type=ProductTypes.Reveal.value,
            count=count
        )
    
    # Покупка привилегий
    elif callback_data.startswith('buy_privilege'):
        # Получаем количество и цену
        _, status_id, display_name, lvl, duration_days, price = callback_data.split(':')
        
        create_payment(
            message_id=message_id,
            amount=price,
            description=f'Покупка {display_name} привилегии {lvl} уровня на {duration_days} дн.',
            user_id=user_id,
            product_type=ProductTypes.Privilege.value,
            status_id=status_id,
            lvl=lvl,
            duration_days=duration_days
        )



    # Обработка получения ID отправителя
    elif callback_data.startswith('find_out_id:'):
        # Получаем ID отправителя
        _, sender_id = callback_data.split(':')

        # Получаем информацию о пользователе
        base_callbacks.find_out_id(
            user_id=user_id,
            sender_id=sender_id,
            reply_to_message_id=message_id
        )
        return
    
    # Обработка отправки ответа по ID отправителя
    elif callback_data.startswith('reply_to_message:'):
        # Получаем ID отправителя
        _, sender_id = callback_data.split(':')

        # Отправляем ответное сообщение пользователю
        base_callbacks.reply_to_message(
            user_id=user_id,
            sender_id=sender_id,
            reply_to_message_id=message_id
        )
        return
