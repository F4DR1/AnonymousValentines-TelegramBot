from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, UnsupportedMessageFormat
from telegram import get_bot_info, check_user_interaction

from config import recipients



def messages(message, user_id: int):    
    # Проверяем, есть ли получатель для текущего пользователя
    recipient_id = recipients.get(user_id)
    if not recipient_id:
        send_telegram_message(
            user_id=user_id,
            text=(
                '❌ <b>Не удалось отправить сообщение пользователю!</b>\n'
                '<i>Попробуйте перейти по ссылке пользователя и вновь отправить своё сообщение.</i>'
            )
        )
        return
    
    # Проверяем, взаимодействовал ли получатель с ботом
    if not check_user_interaction(recipient_id):
        send_telegram_message(
            user_id=user_id,
            text=(
                '❌ <b>Не удалось отправить сообщение пользователю!</b>\n'
                'Пользователь никогда не взаимодействовал с ботом.\n'
                '<u><i>Пригласите этого пользователя, чтобы он начал получать анонимные сообщения!</i></u>'
            )
        )
        return


    # Обрабатываем сообщение
    try:
        media_list, single_media = process_media_files(message)
    except UnsupportedMessageFormat as e:
        # Отправляем сообщение об ошибке пользователю
        send_telegram_message(
            user_id=user_id,
            text=(
                '❌ <b>Этот формат сообщения не поддерживается!</b>\n'
                f'<i>Сообщения этого типа не могут быть пересланы.</i>'
            )
        )
        return
    except Exception as e:
        send_telegram_message(
            user_id=user_id,
            text=(
                '❌ <b>Произошла ошибка при обработке сообщения!</b>\n'
                '<i>Пожалуйста, попробуйте отправить сообщение в другом формате.</i>'
            )
        )
        return
    
    
    keyboard = {
        'inline_keyboard': [
            [
                {
                    'text': '✉️ Ответить на сообщение',
                    'callback_data': f'reply_to_message:{user_id}'
                }
            ],
            [
                {
                    'text': '🔍 Узнать кто прислал',
                    'callback_data': f'find_out_id:{user_id}'
                }
            ]
        ]
    }

    send_telegram_message(
        user_id=recipient_id,
        text='💬 <b>Вам пришло анонимное сообщение!</b>'
    )

    # Если есть только текст
    if 'text' in message and not media_list and not single_media:
        send_telegram_message(
            user_id==recipient_id,
            text=message['text'],
            reply_markup=keyboard
        )
    
    # Если есть медиафайлы
    elif media_list:
        # Если есть подпись, добавляем её к первому файлу
        if 'caption' in message:
            media_list[0]['caption'] = message['caption']
        # Отправляем группу медиафайлов
        send_telegram_media_group(
            id=recipient_id,
            media_list=media_list,
            reply_markup=keyboard
        )
    
    # Если есть одиночный медиафайл (voice, sticker, video_note)
    elif single_media:
        send_telegram_media_single(
            id=recipient_id,
            file_id=single_media['file_id'],
            media_type=single_media['type'],
            reply_markup=keyboard
        )
    

    # Удаляем пару отправитель-получатель после отправки
    if user_id in recipients:
        del recipients[user_id]

    # Отправляем сообщение отправителю о доставке сообщения
    send_telegram_message(
        user_id=user_id,
        text='✅ <b>Ваше сообщение успешно доставлено!</b>'
    )
