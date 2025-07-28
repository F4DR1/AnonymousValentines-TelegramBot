import requests

from config import TOKEN, WEBHOOK_SECRET_TOKEN, SERVER_URL, WEBHOOK_URL
from utils import write_log, LogType



def setup_webhook(webhook_url):
    """
    Настраивает webhook для бота
    webhook_url: URL вашего сервера (например, https://ваш-домен.com/tg_bot)
    """
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/setWebhook'
        params = {
            'url': webhook_url,
            'secret_token': WEBHOOK_SECRET_TOKEN,  # Указываем секретный токен
            'allowed_updates': ['message']  # Получаем только сообщения
        }
        write_log('Параметры запроса сформированы', LogType.INFO)
        write_log(f'URL: {url}', LogType.INFO)
        write_log(f'Webhook URL: {webhook_url}', LogType.INFO)
        
        response = requests.post(url, data=params)
        write_log('response = requests.post(url, data=params)', LogType.INFO)
        
        # Добавляем логирование ответа
        write_log(f'Response status: {response.status_code}', LogType.INFO)
        write_log(f'Response text: {response.text}', LogType.INFO)
        
        response.raise_for_status()
        write_log('response.raise_for_status()', LogType.INFO)
        
        result = response.json()
        write_log('result = response.json()', LogType.INFO)
        
        if result.get('ok'):
            write_log(f'Webhook успешно настроен на {webhook_url}', LogType.INFO)
            return True
        else:
            write_log(f'Ошибка настройки webhook: {result.get("description")}', LogType.ERROR)
            return False
    except Exception as e:
        write_log(f'Ошибка при настройке webhook: {str(e)}', LogType.ERROR)
        return False


def check_and_setup_webhook(current_webhook):
    """
    Проверяет, настроен ли вебхук, и настраивает его при необходимости.
    """
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/getWebhookInfo'
        response = requests.get(url)  # request - не из Flask, а из requests
        response.raise_for_status()
        data = response.json()

        # Проверяем, настроен ли вебхук
        installed_webhook = data.get('result', {}).get('url', '')
        if installed_webhook != current_webhook:
            write_log('Вебхук отсутствует или устарел. Обновляем...')
            setup_webhook(current_webhook)
        else:
            write_log('Вебхук уже настроен корректно.')

    except Exception as e:
        write_log(f'Ошибка при проверке вебхука...', LogType.ERROR)



if __name__ == '__main__':
    current_webhook = f'{SERVER_URL}{WEBHOOK_URL}'
    check_and_setup_webhook(current_webhook)