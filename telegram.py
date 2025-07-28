import requests
from config import TOKEN, WEBHOOK_SECRET_TOKEN
from utils import write_log, LogType

class UnsupportedMessageFormat(Exception):
    """Исключение для неподдерживаемых форматов сообщений"""
    def __init__(self, message_type):
        self.message_type = message_type
        super().__init__(f'Неподдерживаемый формат сообщения: {message_type}')

def process_media_files(message):
    """
    Обрабатывает медиафайлы из сообщения
    message: сообщение от пользователя
    Возвращает список медиафайлов и отдельные медиафайлы
    """
    # Список поддерживаемых форматов
    supported_formats = {
        'text', 'photo', 'video', 'document', 'audio', 'animation',
        'voice', 'sticker', 'video_note'
    }

    # Проверяем, является ли формат сообщения поддерживаемым
    message_type = next((key for key in supported_formats if key in message), None)
    if message_type is None:
        # Если формат не поддерживается, получаем тип сообщения
        unsupported_type = next((key for key in message.keys() if key not in {'chat', 'from', 'message_id', 'date'}), None)
        if unsupported_type:
            raise UnsupportedMessageFormat(unsupported_type)


    media_list = []
    single_media = None

    # Обрабатываем фото
    if 'photo' in message:
        for photo in message['photo']:
            media_list.append({
                'type': 'photo',
                'media': photo['file_id']
            })

    # Обрабатываем видео
    if 'video' in message:
        video = message['video']
        media_list.append({
            'type': 'video',
            'media': video['file_id']
        })

    # Обрабатываем документ
    if 'document' in message:
        document = message['document']
        media_list.append({
            'type': 'document',
            'media': document['file_id']
        })

    # Обрабатываем аудио
    if 'audio' in message:
        audio = message['audio']
        media_list.append({
            'type': 'audio',
            'media': audio['file_id']
        })

    # Обрабатываем анимацию
    if 'animation' in message:
        animation = message['animation']
        media_list.append({
            'type': 'animation',
            'media': animation['file_id']
        })

    # Обрабатываем голосовое сообщение
    if 'voice' in message:
        voice = message['voice']
        single_media = {
            'type': 'voice',
            'file_id': voice['file_id']
        }

    # Обрабатываем стикер
    if 'sticker' in message:
        sticker = message['sticker']
        single_media = {
            'type': 'sticker',
            'file_id': sticker['file_id']
        }

    # Обрабатываем видеосообщение
    if 'video_note' in message:
        video_note = message['video_note']
        single_media = {
            'type': 'video_note',
            'file_id': video_note['file_id']
        }

    return media_list, single_media

def send_telegram_message(id, text, reply_markup=None):
    """
    Функция для отправки текстового сообщения в Telegram
    id: ID пользователя для отправки сообщения
    text: текст сообщения
    """
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
        params = {
            'chat_id': id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            params['reply_markup'] = reply_markup
        response = requests.post(url, json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ValueError(f'Ошибка отправки сообщения: {str(e)}')

def send_telegram_media_single(id, file_id, media_type, reply_markup=None):
    """
    Функция для отправки одиночного медиафайла в Telegram
    id: ID пользователя для отправки сообщения
    file_id: ID файла в Telegram
    media_type: тип медиафайла ('voice', 'sticker', 'video_note')
    """
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/send{media_type.capitalize()}'
        params = {
            'chat_id': id,
            media_type: file_id
        }
        if reply_markup:
            params['reply_markup'] = reply_markup
        response = requests.post(url, json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ValueError(f'Ошибка отправки медиафайла: {str(e)}')

def send_telegram_media_group(id, media_list, reply_markup=None):
    """
    Функция для отправки группы медиафайлов в Telegram
    id: ID пользователя для отправки сообщения
    media_list: список медиафайлов в формате [{'type': 'photo', 'media': file_id, 'caption': caption}, ...]
    """
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/sendMediaGroup'
        params = {
            'chat_id': id,
            'media': media_list
        }
        if reply_markup:
            params['reply_markup'] = reply_markup
        response = requests.post(url, json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ValueError(f'Ошибка отправки группы медиафайлов: {str(e)}')

def get_bot_info():
    """
    Получает информацию о боте
    Возвращает словарь с информацией о боте или None в случае ошибки
    """
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/getMe'
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        if result.get('ok'):
            return result['result']
        else:
            write_log(f'Ошибка получения информации о боте: {result.get("description")}', LogType.ERROR)
            return None
    except Exception as e:
        write_log(f'Ошибка при получении информации о боте: {str(e)}', LogType.ERROR)
        return None
