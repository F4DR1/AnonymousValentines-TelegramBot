from flask import Flask, request, Response
from config import WEBHOOK_SECRET_TOKEN, WEBHOOK_URL
from handlers import process_message, process_callback_query
from utils import write_log, LogType
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"],  # Базовое ограничение
    storage_uri="memory://"  # Используем память для хранения счетчиков
)

@app.route(WEBHOOK_URL, methods=['POST'])
@limiter.exempt  # Полностью освобождаем webhook от ограничений
def webhook():
    """
    Обработчик webhook-запросов от Telegram
    """
    try:
        # Проверяем секретный токен
        if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != WEBHOOK_SECRET_TOKEN:
            write_log('Получен запрос с неверным секретным токеном', LogType.WARNING)
            return Response(status=200)

        # Проверяем размер данных
        if request.content_length > 1024 * 1024:  # Максимум 1MB
            write_log('Превышен размер данных запроса', LogType.WARNING)
            return Response(status=200)

        # Получаем данные запроса
        try:
            data = request.get_json()
        except Exception as e:
            write_log('Ошибка декодирования JSON', LogType.ERROR)
            return Response(status=200)

        # Проверяем структуру данных
        if not isinstance(data, dict):
            write_log('Некорректная структура данных', LogType.WARNING)
            return Response(status=200)

        # Проверяем, что это сообщение
        if 'message' in data:
            message = data['message']
            process_message(message)

        # Проверяем, что это callback_query
        elif 'callback_query' in data:
            callback_query = data['callback_query']
            process_callback_query(callback_query)

        return Response(status=200)

    except Exception as e:
        write_log(f'Ошибка при обработке webhook-запроса: {str(e)}', LogType.ERROR)
        return Response(status=200)

@app.route('/')
@limiter.limit("10 per minute")  # Ограничение на количество запросов в минуту
def index():
    """
    Обработчик корневого URL
    """
    write_log('Кто-то зашел на сайт', LogType.INFO)

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Сервер</title>
        <meta charset="utf-8">
        <meta name="robots" content="noindex, nofollow">
        <meta http-equiv="X-Content-Type-Options" content="nosniff">
        <meta http-equiv="X-Frame-Options" content="DENY">
        <meta http-equiv="X-XSS-Protection" content="1; mode=block">
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                background-color: #f8f9fa;
            }
            .container {
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                margin-top: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .status {
                color: #28a745;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
            }
            .message {
                text-align: center;
                color: #666;
                font-size: 1.1em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Сервер</h1>
            <p class="status">✅ Система работает</p>
            <p class="message">Сервер функционирует в штатном режиме.</p>
        </div>
    </body>
    </html>
    """

    response = Response(html_content, mimetype='text/html')
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Server'] = 'Server'
    return response

@app.errorhandler(404)
@limiter.limit("5 per minute")  # Ограничение на количество запросов в минуту
def not_found(e):
    """
    Обработчик для несуществующих страниц
    """
    write_log(f'Попытка доступа к несуществующей странице: {request.path}', LogType.WARNING)
    return Response(status=404)

if __name__ == '__main__':
    write_log('Запуск приложения...')
    app.run(host='0.0.0.0', port=5000)
