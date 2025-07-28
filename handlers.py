from config import recipients, TOKEN
from utils import write_log, check_user_interaction, get_user_info, LogType
from telegram import process_media_files, send_telegram_message, send_telegram_media_single, send_telegram_media_group, get_bot_info, UnsupportedMessageFormat
from urllib.parse import quote

def process_message(message):
    """
    Обрабатывает входящее сообщение
    message: сообщение от пользователя
    """
    try:
        # Не даём пользоваться ботом в группах
        if message['chat']['type'] != 'private':
            # Игнорируем сообщения из групповых чатов
            chat_id = message['chat']['id']  # Получаем ID чата
            send_telegram_message(chat_id, f'Бот работает только в личных сообщениях!')
            return

        # Получаем ID пользователя
        user_id = message['from']['id']

        # Проверяем, является ли сообщение командой
        if 'text' in message and message['text'].startswith('/'):
            command = message['text'].split()[0].lower()

            # Команда /start
            if command == '/start':
                # Проверяем наличие параметра start в URL
                if 'entities' in message and any(entity.get('type') == 'bot_command' for entity in message['entities']):
                    # Ищем параметр start в тексте сообщения
                    start_param = message['text'].split(' ')[1] if len(message['text'].split()) > 1 else None
                    if start_param:
                        try:
                            # Получаем ID получателя из параметра ссылки
                            recipient_id = int(start_param)
                            if (recipient_id == user_id):
                                send_telegram_message(user_id, f'<b>Вы не можете отправить сообщение самому себе!</b>')
                                return
                                
                            recipients[user_id] = recipient_id  # Заносим в словарь ID получателя
                            send_telegram_message(user_id, 
                                (
                                    '🌐 <b>Здесь вы можете отправить анонимное сообщение человеку, который опубликовал эту ссылку!</b>\n\n'
                                    'Отправьте мне всё, что хочешь ему передать, и он сразу же получит твоё сообщение.\n\n'
                                    'Отправить можно что угодно!\n'
                                    '⚠️ <b>Все сообщения анонимны!</b>'
                                )
                            )
                            return
                        
                        except ValueError:
                            write_log(f'Ошибка при обработке параметра команды {command}: {start_param}', LogType.ERROR)
                            send_telegram_message(user_id, 
                                (
                                    '❌ <b>Не удалось распознать ID получателя.</b>\n'
                                    '<i>Попробуйте перейти по ссылке ещё раз.</i>'
                                )
                            )
                            return
                
                # Отправляем сообщение с личный ссылкой пользователя
                try:
                    write_log(f'Получение информации о боте для пользователя {user_id}')
                    bot_info = get_bot_info()
                    if bot_info:
                        bot_username = bot_info['username']
                        personal_link = f'https://t.me/{bot_username}?start={user_id}'
                        write_log(f'Сформирована персональная ссылка для пользователя {user_id}: {personal_link}')
                        send_telegram_message(user_id, 
                            (
                                '🌐 <b>Начни получать анонимные сообщения прямо сейчас!</b>\n\n'
                                'Твоя личная ссылка:\n'
                                f'👉 <code>{personal_link}</code>\n'
                                '<i><u>(нажмите на ссылку, чтобы скопировать её)</u></i>\n\n'
                                '💬 <i>Поделись этой ссылкой 👆 с друзьями или в своих соцсетях/блоге, чтобы начать получать анонимные сообщения!</i>'
                            )
                        )
                    else:
                        write_log(f'Ошибка при получении информации о боте', LogType.ERROR)
                        send_telegram_message(user_id, 
                            (
                                '❌ <b>Не удалось сформировать персональную ссылку.</b>\n'
                                'Пожалуйста, попробуйте снова.'
                            )
                        )
                
                except Exception as e:
                    write_log(f'Ошибка при получении информации о боте для пользователя {user_id}: {str(e)}', LogType.ERROR)
                    send_telegram_message(user_id,
                        (
                            '❌ <b>Не удалось сформировать персональную ссылку.</b>\n'
                            'Пожалуйста, попробуйте снова.'
                        )
                    )
                return
            
            # Команда /cancel
            elif command == '/cancel':
                # Удаляем пользователя из словаря получателей
                if user_id in recipients:
                    del recipients[user_id]
                
                send_telegram_message(user_id, 
                    (
                        '✅ <b>Отправка сообщения отменена.</b>'
                    )
                )
                return
            
            # Команда /help
            elif command == '/help':
                send_telegram_message(user_id, 
                    (
                        '💬 <b>Список доступных команд:</b>\n\n'
                        '<b>/cancel</b> — получить личную ссылку\n'
                        '<b>/cancel</b> — отменить отправку сообщения\n'
                        '<b>/help</b> — получить помощь'
                    )
                )
                return
            
            # Любая другая команда
            else:
                send_telegram_message(user_id, f'Команды {command} не существует...')
                return

        # Если это не команда, то обрабатываем присланные сообщения
        else:
            # Проверяем, есть ли получатель для текущего пользователя
            recipient_id = recipients.get(user_id)
            if not recipient_id:
                send_telegram_message(user_id,
                    (
                        '❌ <b>Не удалось отправить сообщение пользователю!</b>\n'
                        '<i>Попробуйте перейти по ссылке пользователя и вновь отправить своё сообщение.</i>'
                    )
                )
                return
            
            # Проверяем, взаимодействовал ли получатель с ботом
            if not check_user_interaction(recipient_id):
                send_telegram_message(user_id,
                    (
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
                send_telegram_message(user_id,
                    (
                        '❌ <b>Этот формат сообщения не поддерживается!</b>\n'
                        f'<i>Сообщения этого типа не могут быть пересланы.</i>'
                    )
                )
                return
            except Exception as e:
                send_telegram_message(user_id,
                    (
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
                recipient_id,
                '💬 <b>Вам пришло анонимное сообщение!</b>'
            )

            # Если есть только текст
            if 'text' in message and not media_list and not single_media:
                send_telegram_message(
                    recipient_id,
                    message['text'],
                    keyboard
                )
            
            # Если есть медиафайлы
            elif media_list:
                # Если есть подпись, добавляем её к первому файлу
                if 'caption' in message:
                    media_list[0]['caption'] = message['caption']
                # Отправляем группу медиафайлов
                send_telegram_media_group(
                    recipient_id,
                    media_list,
                    keyboard
                )
            
            # Если есть одиночный медиафайл (voice, sticker, video_note)
            elif single_media:
                send_telegram_media_single(
                    recipient_id,
                    single_media['file_id'],
                    single_media['type'],
                    keyboard
                )
            

            # Удаляем пару отправитель-получатель после отправки
            if user_id in recipients:
                del recipients[user_id]

            # Отправляем сообщение отправителю о доставке сообщения
            send_telegram_message(user_id, '✅ <b>Ваше сообщение успешно доставлено!</b>')
    
    except Exception as e:
        write_log(f'Ошибка при обработке message: {str(e)}', LogType.ERROR)
        send_telegram_message(user_id,
            (
                '⚠️ <b>Не удалось отправить сообщение</b>\n'
                'Попробуйте снова... Если ошибка повторится - свяжитесь с разработчиком.'
            )
        )

def process_callback_query(callback_query):
    """
    Обрабатывает callback_query
    callback_query: callback_query от пользователя
    """
    try:
        callback_data = callback_query['data']
        
        # Получаем ID пользователя
        user_id = callback_query['from']['id']

        # Обработка получения ID отправителя
        if callback_data.startswith('find_out_id:'):
            # Проверка на наличие доступа получения ID отправителя


            # Получаем ID отправителя
            _, sender_id = callback_data.split(":")

            # Получаем информацию о пользователе
            try:
                sender_user_info = get_user_info(sender_id)
                sender_username = sender_user_info.get('username')
                
                # Добавляем username только если он есть
                if sender_username:
                    username_link = f'@{sender_username}'
                else:
                    username_link = '<i><u>Отсутствует</u></i>'
                
                # Добавляем ссылку на профиль
                profile_link = f'<u><a href="tg://user?id={sender_id}">Открыть профиль</a></u>'
                
                # Отправляем сообщение с информацией о пользователе
                send_telegram_message(user_id,
                    (
                        '🌐 <b>Отправитель:</b>\n\n'
                        f'Имя пользователя: {username_link}\n'
                        f'Ссылка на профиль: {profile_link}\n'
                        '<i><u>(по каким-то причинам может не работать)</u></i>'
                    )
                )
                return
            
            except Exception as e:
                write_log(f'Ошибка при получении информации о пользователе: {str(e)}', LogType.ERROR)
                send_telegram_message(user_id, '❌ <b>Не удалось получить информацию об отправителе</b>')
        
        # Обработка отправки ответа по ID отправителя
        elif callback_data.startswith('reply_to_message:'):
            # Получаем ID отправителя
            _, sender_id = callback_data.split(":")

            # Удаляем пользователя из словаря получателей
            if user_id in recipients:
                del recipients[user_id]
            recipients[user_id] = sender_id  # Заносим в словарь ID получателя

            # Отправляем сообщение с информацией об отправке сообщения пользователю
            send_telegram_message(
                user_id, 
                (
                    '🌐 <b>Здесь вы можете отправить анонимное сообщение человеку, который опубликовал эту ссылку!</b>\n\n'
                    'Отправьте мне всё, что хочешь ему передать, и он сразу же получит твоё сообщение.\n\n'
                    'Отправить можно что угодно!\n'
                    '⚠️ <b>Все сообщения анонимны!</b>'
                )
            )
            return
    
    except Exception as e:
        write_log(f'Ошибка при обработке callback_query: {str(e)}', LogType.ERROR)
