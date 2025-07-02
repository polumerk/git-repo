#!/usr/bin/env python3
"""
Веб-приложение Hello World v6.0 - AI Edition
Интеграция всех новых сервисов: AI чат-бот, WebSocket, OAuth, GraphQL
"""

import os
import time
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import random

# Импорты для новых возможностей v6.0
try:
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit, join_room, leave_room
    from werkzeug.middleware.proxy_fix import ProxyFix
    FLASK_EXTENSIONS_AVAILABLE = True
except ImportError:
    FLASK_EXTENSIONS_AVAILABLE = False
    print("⚠️ Flask расширения не установлены. Основная функциональность доступна.")

# Основные сервисы
from hello_world import WorldGreeter

# Импорт новых сервисов v6.0
try:
    from ai_chatbot import language_bot
    AI_BOT_ENABLED = True
except ImportError:
    print("⚠️ AI чат-бот не подключен")
    AI_BOT_ENABLED = False

try:
    from websocket_service import websocket_manager
    WEBSOCKET_ENABLED = True
except ImportError:
    print("⚠️ WebSocket сервис не подключен")
    WEBSOCKET_ENABLED = False

try:
    from oauth_service import oauth_service
    OAUTH_ENABLED = True
except ImportError:
    print("⚠️ OAuth сервис не подключен")
    OAUTH_ENABLED = False

try:
    from graphql_api import graphql_service
    GRAPHQL_ENABLED = True
except ImportError:
    print("⚠️ GraphQL API не подключен")
    GRAPHQL_ENABLED = False

# Сервисы v5.0
try:
    from database import db_manager
    DATABASE_ENABLED = True
except ImportError:
    print("⚠️ База данных не подключена")
    DATABASE_ENABLED = False

try:
    from audio_service import audio_service
    AUDIO_ENABLED = True
except ImportError:
    print("⚠️ Аудио сервис не подключен")
    AUDIO_ENABLED = False

try:
    from translator_service import translator_service
    TRANSLATOR_ENABLED = True
except ImportError:
    print("⚠️ Сервис переводчика не подключен")
    TRANSLATOR_ENABLED = False

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание Flask приложения
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hello-world-v6-secret-key-2024')

# Настройка CORS для API
if FLASK_EXTENSIONS_AVAILABLE:
    CORS(app, origins=["http://localhost:3000", "http://localhost:8080"])
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Настройка SocketIO
if FLASK_EXTENSIONS_AVAILABLE and WEBSOCKET_ENABLED:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    SOCKETIO_ENABLED = True
else:
    socketio = None
    SOCKETIO_ENABLED = False

# Основные объекты
greeter = WorldGreeter()

# Логирование запуска приложения
if DATABASE_ENABLED:
    db_manager.log_system_event('startup_v6', 'Web application v6.0 started', {
        'ai_bot_enabled': AI_BOT_ENABLED,
        'websocket_enabled': WEBSOCKET_ENABLED,
        'oauth_enabled': OAUTH_ENABLED,
        'graphql_enabled': GRAPHQL_ENABLED,
        'audio_enabled': AUDIO_ENABLED,
        'translator_enabled': TRANSLATOR_ENABLED,
        'features': ['ai_chat', 'realtime_updates', 'oauth_auth', 'graphql_api']
    })


def get_or_create_user():
    """Получить или создать пользователя для текущей сессии"""
    if DATABASE_ENABLED:
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        user_id = db_manager.get_or_create_user(
            session_id=session['session_id'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        return user_id
    return None


def get_current_user_from_token():
    """Получить текущего пользователя из OAuth токена"""
    if not OAUTH_ENABLED:
        return None
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = request.args.get('token', '')
    
    if token:
        payload = oauth_service.verify_jwt_token(token)
        if payload:
            return oauth_service.get_user_profile(payload['user_id'])
    
    return None


@app.before_request
def before_request():
    """Выполняется перед каждым запросом"""
    request.start_time = time.time()
    request.user_id = get_or_create_user()
    request.oauth_user = get_current_user_from_token()


@app.after_request
def after_request(response):
    """Выполняется после каждого запроса"""
    if hasattr(request, 'start_time'):
        response_time = (time.time() - request.start_time) * 1000
        response.headers['X-Response-Time'] = f"{response_time:.2f}ms"
        response.headers['X-Version'] = "6.0"
    return response


# === ОСНОВНЫЕ МАРШРУТЫ ===

@app.route('/')
def index():
    """Главная страница с новым интерфейсом v6.0"""
    features = {
        'ai_chatbot': AI_BOT_ENABLED,
        'websocket': SOCKETIO_ENABLED,
        'oauth': OAUTH_ENABLED,
        'graphql': GRAPHQL_ENABLED,
        'audio': AUDIO_ENABLED,
        'translator': TRANSLATOR_ENABLED
    }
    
    return render_template('index_v6.html', features=features)


@app.route('/chat')
def chat_page():
    """Страница AI чат-бота"""
    if not AI_BOT_ENABLED:
        return render_template('error.html', 
                             message="AI чат-бот недоступен"), 503
    
    return render_template('chat.html')


@app.route('/graphql-playground')
def graphql_playground():
    """GraphQL Playground"""
    if not GRAPHQL_ENABLED:
        return render_template('error.html', 
                             message="GraphQL API недоступен"), 503
    
    return render_template('graphql_playground.html')


# === API v6.0 ===

# Существующие API эндпоинты (из v5.0)
@app.route('/api/languages')
def api_languages():
    """API для получения списка языков"""
    languages = []
    for code in greeter.available_languages():
        info = greeter.get_language_info(code)
        languages.append(info)
    
    return jsonify({
        'languages': languages,
        'total': len(languages)
    })


@app.route('/api/greet/<language>')
def api_greet(language):
    """API для получения приветствия на конкретном языке"""
    start_time = time.time()
    
    if language not in greeter.available_languages():
        return jsonify({'error': 'Language not found'}), 404
    
    info = greeter.get_language_info(language)
    
    # Логируем использование
    if DATABASE_ENABLED and request.user_id:
        response_time = int((time.time() - start_time) * 1000)
        db_manager.log_greeting(
            user_id=request.user_id,
            language_code=language,
            greeting_text=info['greeting'],
            access_method='api',
            response_time_ms=response_time
        )
    
    # Добавляем ссылку на аудио если доступно
    if AUDIO_ENABLED:
        info['audio_available'] = True
        info['audio_url'] = f'/api/audio/{language}'
    
    return jsonify(info)


# === НОВЫЕ API v6.0 ===

# OAuth API
@app.route('/api/auth/providers')
def api_auth_providers():
    """Получить список OAuth провайдеров"""
    if not OAUTH_ENABLED:
        return jsonify({'error': 'OAuth not available'}), 503
    
    providers = oauth_service.get_supported_providers()
    return jsonify({'providers': providers})


@app.route('/api/auth/<provider>')
def api_auth_start(provider):
    """Начать OAuth аутентификацию"""
    if not OAUTH_ENABLED:
        return jsonify({'error': 'OAuth not available'}), 503
    
    auth_data = oauth_service.get_auth_url(provider)
    if 'error' in auth_data:
        return jsonify(auth_data), 400
    
    return jsonify(auth_data)


@app.route('/api/auth/<provider>/callback')
def api_auth_callback(provider):
    """Callback для OAuth аутентификации"""
    if not OAUTH_ENABLED:
        return jsonify({'error': 'OAuth not available'}), 503
    
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state:
        return jsonify({'error': 'Missing code or state parameter'}), 400
    
    result = oauth_service.handle_callback(provider, code, state)
    
    if result.get('success'):
        # Перенаправляем на главную страницу с токеном
        return redirect(f"/?token={result['jwt_token']}")
    else:
        return jsonify(result), 400


@app.route('/api/auth/me')
def api_auth_me():
    """Получить информацию о текущем пользователе"""
    if not OAUTH_ENABLED:
        return jsonify({'error': 'OAuth not available'}), 503
    
    if request.oauth_user:
        return jsonify({
            'user_id': request.oauth_user.user_id,
            'email': request.oauth_user.email,
            'name': request.oauth_user.name,
            'provider': request.oauth_user.provider,
            'avatar_url': request.oauth_user.avatar_url,
            'verified': request.oauth_user.verified
        })
    else:
        return jsonify({'error': 'Not authenticated'}), 401


@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    """Выйти из системы"""
    if not OAUTH_ENABLED:
        return jsonify({'error': 'OAuth not available'}), 503
    
    # Здесь можно добавить логику выхода из системы
    return jsonify({'success': True, 'message': 'Logged out'})


# AI Chatbot API
@app.route('/api/ai/session', methods=['POST'])
def api_ai_create_session():
    """Создать сессию AI чат-бота"""
    if not AI_BOT_ENABLED:
        return jsonify({'error': 'AI chatbot not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id', f'user_{int(time.time())}')
    target_language = data.get('target_language', 'ru')
    level = data.get('level', 'beginner')
    
    try:
        session = language_bot.create_learning_session(user_id, target_language, 'ru', level)
        
        return jsonify({
            'success': True,
            'session_id': user_id,
            'target_language': session.target_language,
            'level': session.level,
            'progress_score': session.progress_score
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/chat', methods=['POST'])
def api_ai_chat():
    """Отправить сообщение AI чат-боту"""
    if not AI_BOT_ENABLED:
        return jsonify({'error': 'AI chatbot not available'}), 503
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({'error': 'user_id and message required'}), 400
    
    try:
        response = language_bot.process_message(user_id, message)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/session/<user_id>')
def api_ai_get_session(user_id):
    """Получить сессию AI чат-бота"""
    if not AI_BOT_ENABLED:
        return jsonify({'error': 'AI chatbot not available'}), 503
    
    try:
        stats = language_bot.get_session_statistics(user_id)
        progress = language_bot.get_learning_progress(user_id)
        
        return jsonify({
            'statistics': stats,
            'progress': progress
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# GraphQL API
@app.route('/api/graphql', methods=['POST'])
def api_graphql():
    """GraphQL endpoint"""
    if not GRAPHQL_ENABLED:
        return jsonify({'error': 'GraphQL not available'}), 503
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    
    query = data.get('query')
    variables = data.get('variables')
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        result = graphql_service.execute_query(query, variables)
        return jsonify(result)
    except Exception as e:
        return jsonify({'errors': [{'message': str(e)}]}), 500


@app.route('/api/graphql', methods=['GET'])
def api_graphql_schema():
    """Получить GraphQL схему"""
    if not GRAPHQL_ENABLED:
        return jsonify({'error': 'GraphQL not available'}), 503
    
    if request.args.get('introspection'):
        introspection = graphql_service.introspect()
        return jsonify(introspection)
    else:
        sdl = graphql_service.get_schema_sdl()
        return sdl, 200, {'Content-Type': 'text/plain'}


# WebSocket для real-time чата
if SOCKETIO_ENABLED:
    @socketio.on('connect')
    def handle_connect():
        """Подключение пользователя"""
        logger.info(f"Пользователь подключился: {request.sid}")
        emit('status', {'message': 'Подключен к real-time чату!'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Отключение пользователя"""
        logger.info(f"Пользователь отключился: {request.sid}")
    
    @socketio.on('join_ai_chat')
    def handle_join_ai_chat(data):
        """Присоединиться к AI чату"""
        user_id = data.get('user_id')
        target_language = data.get('target_language', 'ru')
        level = data.get('level', 'beginner')
        
        if AI_BOT_ENABLED and user_id:
            # Создаем сессию если не существует
            if user_id not in language_bot.sessions:
                language_bot.create_learning_session(user_id, target_language, 'ru', level)
            
            join_room(f"ai_chat_{user_id}")
            emit('ai_chat_joined', {
                'user_id': user_id,
                'target_language': target_language,
                'level': level,
                'message': 'Присоединились к AI чату!'
            })
        else:
            emit('error', {'message': 'AI чат недоступен'})
    
    @socketio.on('ai_message')
    def handle_ai_message(data):
        """Обработать сообщение для AI"""
        user_id = data.get('user_id')
        message = data.get('message')
        
        if AI_BOT_ENABLED and user_id and message:
            try:
                # Отправляем индикатор набора
                emit('ai_typing', {'is_typing': True}, room=f"ai_chat_{user_id}")
                
                # Получаем ответ от AI
                response = language_bot.process_message(user_id, message)
                
                # Отправляем ответ
                emit('ai_response', {
                    'user_message': message,
                    'bot_response': response.get('response', ''),
                    'suggestions': response.get('suggestions', []),
                    'progress_score': response.get('progress_score', 0),
                    'confidence': response.get('confidence', 0.8)
                }, room=f"ai_chat_{user_id}")
                
                # Убираем индикатор набора
                emit('ai_typing', {'is_typing': False}, room=f"ai_chat_{user_id}")
                
            except Exception as e:
                emit('error', {'message': f'Ошибка AI: {str(e)}'}, room=f"ai_chat_{user_id}")
        else:
            emit('error', {'message': 'Неверные данные'})


# Статистика и мониторинг
@app.route('/api/system/status')
def api_system_status():
    """Статус всех сервисов v6.0"""
    status = {
        'version': '6.0.0',
        'uptime': time.time() - app.start_time if hasattr(app, 'start_time') else 0,
        'services': {
            'hello_world': True,
            'ai_chatbot': AI_BOT_ENABLED,
            'websocket': SOCKETIO_ENABLED,
            'oauth': OAUTH_ENABLED,
            'graphql': GRAPHQL_ENABLED,
            'database': DATABASE_ENABLED,
            'audio': AUDIO_ENABLED,
            'translator': TRANSLATOR_ENABLED
        },
        'features': [
            'ai_language_learning', 'real_time_chat', 'oauth_authentication',
            'graphql_api', 'multi_language_support', 'audio_pronunciation',
            'translation_services', 'user_analytics'
        ]
    }
    
    # Статистика сервисов
    if AI_BOT_ENABLED:
        status['ai_statistics'] = {
            'active_sessions': len(language_bot.sessions),
            'total_messages': sum(len(s.messages) for s in language_bot.sessions.values())
        }
    
    if OAUTH_ENABLED:
        oauth_stats = oauth_service.get_statistics()
        status['oauth_statistics'] = oauth_stats
    
    if WEBSOCKET_ENABLED:
        ws_stats = websocket_manager.get_statistics()
        status['websocket_statistics'] = ws_stats
    
    return jsonify(status)


@app.route('/api/statistics/comprehensive')
def api_comprehensive_statistics():
    """Комплексная статистика v6.0"""
    stats = {
        'timestamp': time.time(),
        'version': '6.0.0'
    }
    
    # Базовая статистика
    languages = greeter.available_languages()
    stats['basic'] = {
        'total_languages': len(languages),
        'total_greetings': len(greeter.greetings)
    }
    
    # Статистика AI
    if AI_BOT_ENABLED:
        stats['ai'] = {
            'active_sessions': len(language_bot.sessions),
            'total_conversations': sum(len(s.messages) for s in language_bot.sessions.values()),
            'average_progress': sum(s.progress_score for s in language_bot.sessions.values()) / max(1, len(language_bot.sessions))
        }
    
    # Статистика OAuth
    if OAUTH_ENABLED:
        stats['oauth'] = oauth_service.get_statistics()
    
    # Статистика WebSocket
    if WEBSOCKET_ENABLED:
        stats['websocket'] = websocket_manager.get_statistics()
    
    # Статистика GraphQL
    if GRAPHQL_ENABLED:
        stats['graphql'] = {
            'available': True,
            'endpoints': ['query', 'mutation', 'introspection']
        }
    
    # Статистика базы данных
    if DATABASE_ENABLED:
        stats['database'] = db_manager.get_statistics()
    
    return jsonify(stats)


# === ОБРАБОТКА ОШИБОК ===

@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибок"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('error.html', message="Страница не найдена"), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибок"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('error.html', message="Внутренняя ошибка сервера"), 500


if __name__ == '__main__':
    # Устанавливаем время старта приложения
    app.start_time = time.time()
    
    # Создаем необходимые директории
    os.makedirs('data', exist_ok=True)
    os.makedirs('audio', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Запуск Hello World веб-приложения v6.0 - AI Edition")
    print(f"📊 Статус сервисов:")
    print(f"   🤖 AI Chatbot: {'✅' if AI_BOT_ENABLED else '❌'}")
    print(f"   ⚡ WebSocket: {'✅' if SOCKETIO_ENABLED else '❌'}")
    print(f"   🔐 OAuth: {'✅' if OAUTH_ENABLED else '❌'}")
    print(f"   📡 GraphQL: {'✅' if GRAPHQL_ENABLED else '❌'}")
    print(f"   🗄️  Database: {'✅' if DATABASE_ENABLED else '❌'}")
    print(f"   🔊 Audio: {'✅' if AUDIO_ENABLED else '❌'}")
    print(f"   🌐 Translator: {'✅' if TRANSLATOR_ENABLED else '❌'}")
    
    print(f"\n🌟 Новые возможности v6.0:")
    print(f"   • AI-powered language learning")
    print(f"   • Real-time WebSocket communication")
    print(f"   • OAuth authentication (Google, GitHub, VK)")
    print(f"   • GraphQL API for flexible queries")
    print(f"   • Enhanced user experience")
    
    print(f"\n🌐 Доступные эндпоинты:")
    print(f"   Main App: http://localhost:5000")
    print(f"   AI Chat: http://localhost:5000/chat")
    print(f"   GraphQL: http://localhost:5000/api/graphql")
    print(f"   API Status: http://localhost:5000/api/system/status")
    
    # Запуск с SocketIO если доступен
    if SOCKETIO_ENABLED:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    else:
        app.run(debug=True, host='0.0.0.0', port=5000)