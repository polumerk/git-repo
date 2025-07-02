#!/usr/bin/env python3
"""
Hello World v6.0 - AI Edition | UNIFIED VERSION
Объединенная версия всех сервисов с graceful fallbacks
"""

import os
import time
import uuid
import json
import logging
import secrets
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Основные импорты
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for

# Проверка зависимостей с graceful fallbacks
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("⚠️ flask-cors не установлен")

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    print("⚠️ flask-socketio не установлен")

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("⚠️ PyJWT не установлен")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests не установлен")

# Основные сервисы
from hello_world import WorldGreeter

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === AI CHATBOT (INTEGRATED) ===

class AILanguageBot:
    """Интегрированный AI чат-бот"""
    
    def __init__(self):
        self.sessions = {}
        self.language_lessons = {
            'ru': {
                'greetings': ['Привет!', 'Здравствуйте!', 'Добро пожаловать!'],
                'basics': ['Как дела?', 'Меня зовут...', 'Откуда вы?'],
                'phrases': ['Спасибо большое', 'Пожалуйста', 'Извините']
            },
            'en': {
                'greetings': ['Hello!', 'Hi there!', 'Welcome!'],
                'basics': ['How are you?', 'My name is...', 'Where are you from?'],
                'phrases': ['Thank you very much', 'You\'re welcome', 'Excuse me']
            },
            'es': {
                'greetings': ['¡Hola!', '¡Buenos días!', '¡Bienvenido!'],
                'basics': ['¿Cómo estás?', 'Me llamo...', '¿De dónde eres?'],
                'phrases': ['Muchas gracias', 'De nada', 'Disculpe']
            }
        }
        
        self.conversation_starters = {
            'beginner': [
                "Давайте начнем с простых приветствий!",
                "Попробуйте представиться на новом языке!",
                "Как сказать 'спасибо' на изучаемом языке?"
            ],
            'intermediate': [
                "Расскажите о своем дне на изучаемом языке.",
                "Опишите свое любимое место для отдыха.",
                "Какие у вас планы на выходные?"
            ],
            'advanced': [
                "Обсудим текущие события в мире.",
                "Что вы думаете о современных технологиях?",
                "Расскажите об интересной книге."
            ]
        }
    
    def create_learning_session(self, user_id: str, target_language: str, level: str = 'beginner'):
        """Создать сессию изучения"""
        session_data = {
            'user_id': user_id,
            'target_language': target_language,
            'level': level,
            'messages': [],
            'created_at': time.time(),
            'last_activity': time.time(),
            'progress_score': 0,
            'topics_covered': []
        }
        
        # Приветственное сообщение
        welcome_msg = f"Привет! 👋 Я ваш AI помощник для изучения языка {target_language}. Давайте начнем!"
        session_data['messages'].append({
            'role': 'assistant',
            'content': welcome_msg,
            'timestamp': time.time()
        })
        
        self.sessions[user_id] = session_data
        return session_data
    
    def process_message(self, user_id: str, message: str):
        """Обработать сообщение"""
        if user_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[user_id]
        session['last_activity'] = time.time()
        
        # Добавляем сообщение пользователя
        session['messages'].append({
            'role': 'user',
            'content': message,
            'timestamp': time.time()
        })
        
        # Генерируем ответ
        response = self._generate_response(session, message)
        
        # Добавляем ответ бота
        session['messages'].append({
            'role': 'assistant',
            'content': response['content'],
            'timestamp': time.time()
        })
        
        session['progress_score'] += response.get('progress_points', 1)
        
        return {
            'response': response['content'],
            'suggestions': response.get('suggestions', []),
            'progress_score': session['progress_score'],
            'confidence': response.get('confidence', 0.8)
        }
    
    def _generate_response(self, session, user_message):
        """Генерировать ответ"""
        target_lang = session['target_language']
        level = session['level']
        message_lower = user_message.lower()
        
        # Проверяем ключевые слова
        if any(word in message_lower for word in ['привет', 'hello', 'hola']):
            responses = {
                'ru': "Отлично! Вы поздоровались. Теперь попробуйте спросить 'Как дела?'",
                'en': "Great! You said hello. Now try asking 'How are you?'",
                'es': "¡Excelente! Dijiste hola. Ahora intenta preguntar '¿Cómo estás?'"
            }
            
            return {
                'content': responses.get(target_lang, "Good! Now let's learn more phrases."),
                'suggestions': self.language_lessons.get(target_lang, {}).get('basics', []),
                'confidence': 0.8,
                'progress_points': 1
            }
        
        elif any(word in message_lower for word in ['спасибо', 'thank', 'gracias']):
            responses = {
                'ru': "Прекрасно! Вы сказали 'спасибо'. Ответ: 'Пожалуйста!'",
                'en': "Perfect! You said 'thank you'. Response: 'You're welcome!'",
                'es': "¡Perfecto! Dijiste 'gracias'. Respuesta: '¡De nada!'"
            }
            
            return {
                'content': responses.get(target_lang, "Good! You're learning polite expressions."),
                'suggestions': self.language_lessons.get(target_lang, {}).get('phrases', []),
                'confidence': 0.8,
                'progress_points': 1
            }
        
        elif any(word in message_lower for word in ['помощь', 'help', 'ayuda']):
            return {
                'content': "Я помогу вам изучать языки! Просто говорите со мной, и я буду исправлять ошибки и давать советы.",
                'confidence': 1.0,
                'progress_points': 0
            }
        
        else:
            # Общий ответ
            starters = self.conversation_starters.get(level, self.conversation_starters['beginner'])
            random_starter = random.choice(starters)
            
            return {
                'content': f"Интересно! Давайте попробуем: {random_starter}",
                'suggestions': self._get_random_suggestions(target_lang),
                'confidence': 0.6,
                'progress_points': 1
            }
    
    def _get_random_suggestions(self, language):
        """Получить случайные предложения"""
        lessons = self.language_lessons.get(language, {})
        all_phrases = []
        for category in lessons.values():
            all_phrases.extend(category)
        
        return random.sample(all_phrases, min(3, len(all_phrases)))
    
    def get_session_statistics(self, user_id):
        """Получить статистику сессии"""
        if user_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[user_id]
        total_messages = len(session['messages'])
        user_messages = len([m for m in session['messages'] if m['role'] == 'user'])
        
        return {
            'user_id': user_id,
            'target_language': session['target_language'],
            'level': session['level'],
            'progress_score': session['progress_score'],
            'total_messages': total_messages,
            'user_messages': user_messages,
            'session_duration_minutes': round((time.time() - session['created_at']) / 60, 1)
        }


# === OAUTH SERVICE (INTEGRATED) ===

class OAuthService:
    """Интегрированный OAuth сервис"""
    
    def __init__(self):
        self.providers = {}
        self.sessions = {}
        self.users = {}
        self.pending_auth = {}
        self.jwt_secret = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
        
        self._setup_providers()
    
    def _setup_providers(self):
        """Настройка провайдеров"""
        # Google OAuth
        google_id = os.getenv('GOOGLE_CLIENT_ID')
        google_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if google_id and google_secret:
            self.providers['google'] = {
                'client_id': google_id,
                'client_secret': google_secret,
                'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token'
            }
            logger.info("Google OAuth настроен")
    
    def get_supported_providers(self):
        """Получить провайдеров"""
        return [{'name': name, 'available': True} for name in self.providers.keys()]
    
    def get_auth_url(self, provider_name):
        """Получить URL авторизации"""
        if provider_name not in self.providers:
            return {'error': f'Provider {provider_name} not supported'}
        
        state = secrets.token_urlsafe(32)
        self.pending_auth[state] = {
            'provider': provider_name,
            'created_at': time.time()
        }
        
        provider = self.providers[provider_name]
        auth_url = f"{provider['auth_url']}?client_id={provider['client_id']}&state={state}&response_type=code"
        
        return {
            'auth_url': auth_url,
            'state': state,
            'provider': provider_name
        }
    
    def create_mock_user(self, provider, user_data):
        """Создать mock пользователя для демонстрации"""
        user_id = f"{provider}_{int(time.time())}"
        user = {
            'user_id': user_id,
            'provider': provider,
            'email': user_data.get('email', f'user@{provider}.com'),
            'name': user_data.get('name', f'User from {provider}'),
            'avatar_url': user_data.get('avatar_url'),
            'created_at': time.time(),
            'last_login': time.time()
        }
        
        self.users[user_id] = user
        
        # Создаем JWT токен (если доступен)
        if JWT_AVAILABLE:
            payload = {
                'user_id': user_id,
                'provider': provider,
                'exp': int(time.time()) + 3600  # 1 час
            }
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            return {'user': user, 'jwt_token': token}
        
        return {'user': user, 'jwt_token': 'mock_token_' + user_id}
    
    def verify_jwt_token(self, token):
        """Проверить JWT токен"""
        if not JWT_AVAILABLE:
            # Mock verification
            if token.startswith('mock_token_'):
                user_id = token.replace('mock_token_', '')
                return {'user_id': user_id}
            return None
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except:
            return None


# === WEBSOCKET MANAGER (INTEGRATED) ===

class WebSocketManager:
    """Интегрированный WebSocket менеджер"""
    
    def __init__(self):
        self.connected_users = {}
        self.message_history = {}
    
    def get_statistics(self):
        """Получить статистику"""
        return {
            'connected_users': len(self.connected_users),
            'total_messages': sum(len(history) for history in self.message_history.values()),
            'available': SOCKETIO_AVAILABLE
        }


# === GRAPHQL SERVICE (INTEGRATED) ===

class GraphQLService:
    """Интегрированный GraphQL сервис"""
    
    def __init__(self):
        self.available = False  # Упрощенная версия
    
    def execute_query(self, query, variables=None):
        """Выполнить запрос"""
        return {
            'data': {
                'message': 'GraphQL service available in simplified mode',
                'query': query[:100] + '...' if len(query) > 100 else query
            }
        }
    
    def get_schema_sdl(self):
        """Получить схему"""
        return "# Simplified GraphQL Schema\ntype Query { hello: String }"


# === FLASK APPLICATION ===

# Создаем Flask приложение
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hello-world-v6-unified-key')

# Настройка CORS
if CORS_AVAILABLE:
    CORS(app, origins=["*"])

# Настройка SocketIO
if SOCKETIO_AVAILABLE:
    socketio = SocketIO(app, cors_allowed_origins="*")
else:
    socketio = None

# Инициализация сервисов
greeter = WorldGreeter()
ai_bot = AILanguageBot()
oauth_service = OAuthService()
websocket_manager = WebSocketManager()
graphql_service = GraphQLService()

logger.info("Hello World v6.0 Unified - все сервисы инициализированы")


# === UTILITY FUNCTIONS ===

def get_or_create_user():
    """Получить или создать пользователя"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


def get_current_user_from_token():
    """Получить пользователя из токена"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = request.args.get('token', '')
    
    if token:
        payload = oauth_service.verify_jwt_token(token)
        if payload:
            return oauth_service.users.get(payload['user_id'])
    
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
        response.headers['X-Version'] = "6.0-unified"
    return response


# === ROUTES ===

@app.route('/')
def index():
    """Главная страница"""
    features = {
        'ai_chatbot': True,
        'websocket': SOCKETIO_AVAILABLE,
        'oauth': len(oauth_service.providers) > 0,
        'graphql': True,
        'cors': CORS_AVAILABLE,
        'jwt': JWT_AVAILABLE
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hello World v6.0 - AI Edition</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .hero {{ text-align: center; margin-bottom: 40px; }}
            .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .feature {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; }}
            .feature.available {{ border-color: #4CAF50; background-color: #f9fff9; }}
            .feature.unavailable {{ border-color: #f44336; background-color: #fff9f9; }}
            .api-demo {{ margin-top: 40px; padding: 20px; background-color: #f5f5f5; border-radius: 8px; }}
            button {{ padding: 10px 20px; margin: 5px; cursor: pointer; }}
            .demo-result {{ margin-top: 10px; padding: 10px; background-color: white; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>🌍 Hello World v6.0 - AI Edition</h1>
                <p>Объединенная версия со всеми новыми возможностями</p>
                <p><strong>Статус:</strong> Все базовые сервисы работают | Запущено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="features">
                <div class="feature {'available' if features['ai_chatbot'] else 'unavailable'}">
                    <h3>🤖 AI Чат-бот</h3>
                    <p>Интерактивное изучение языков с AI помощником</p>
                    <p><strong>Статус:</strong> {'✅ Работает' if features['ai_chatbot'] else '❌ Недоступен'}</p>
                    <a href="/chat">Открыть чат</a>
                </div>
                
                <div class="feature {'available' if features['websocket'] else 'unavailable'}">
                    <h3>⚡ WebSocket</h3>
                    <p>Real-time коммуникация и мгновенные обновления</p>
                    <p><strong>Статус:</strong> {'✅ Работает' if features['websocket'] else '❌ Требует flask-socketio'}</p>
                </div>
                
                <div class="feature {'available' if features['oauth'] else 'unavailable'}">
                    <h3>🔐 OAuth</h3>
                    <p>Безопасная аутентификация через внешние провайдеры</p>
                    <p><strong>Статус:</strong> {'✅ Настроен' if features['oauth'] else '❌ Требует настройки'}</p>
                </div>
                
                <div class="feature {'available' if features['graphql'] else 'unavailable'}">
                    <h3>📡 GraphQL</h3>
                    <p>Гибкие запросы данных через современный API</p>
                    <p><strong>Статус:</strong> {'✅ Упрощенная версия' if features['graphql'] else '❌ Недоступен'}</p>
                    <a href="/api/graphql">Открыть API</a>
                </div>
            </div>
            
            <div class="api-demo">
                <h3>🧪 Демонстрация API v6.0</h3>
                <button onclick="testLanguages()">Получить языки</button>
                <button onclick="testAIChat()">Тест AI чата</button>
                <button onclick="testGraphQL()">Тест GraphQL</button>
                <button onclick="testStatus()">Статус системы</button>
                <div id="demo-result" class="demo-result"></div>
            </div>
        </div>
        
        <script>
            async function testLanguages() {{
                try {{
                    const response = await fetch('/api/languages');
                    const data = await response.json();
                    document.getElementById('demo-result').innerHTML = 
                        '<h4>Языки (' + data.total + '):</h4><pre>' + 
                        JSON.stringify(data.languages.slice(0, 5), null, 2) + '</pre>';
                }} catch (e) {{
                    document.getElementById('demo-result').innerHTML = '<p style="color: red;">Ошибка: ' + e.message + '</p>';
                }}
            }}
            
            async function testAIChat() {{
                try {{
                    const sessionResponse = await fetch('/api/ai/session', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{user_id: 'demo_user', target_language: 'ru', level: 'beginner'}})
                    }});
                    const sessionData = await sessionResponse.json();
                    
                    const chatResponse = await fetch('/api/ai/chat', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{user_id: 'demo_user', message: 'Привет!'}})
                    }});
                    const chatData = await chatResponse.json();
                    
                    document.getElementById('demo-result').innerHTML = 
                        '<h4>AI Чат:</h4><pre>' + JSON.stringify(chatData, null, 2) + '</pre>';
                }} catch (e) {{
                    document.getElementById('demo-result').innerHTML = '<p style="color: red;">Ошибка: ' + e.message + '</p>';
                }}
            }}
            
            async function testGraphQL() {{
                try {{
                    const response = await fetch('/api/graphql', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{query: 'query {{ hello }}'}})
                    }});
                    const data = await response.json();
                    document.getElementById('demo-result').innerHTML = 
                        '<h4>GraphQL:</h4><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }} catch (e) {{
                    document.getElementById('demo-result').innerHTML = '<p style="color: red;">Ошибка: ' + e.message + '</p>';
                }}
            }}
            
            async function testStatus() {{
                try {{
                    const response = await fetch('/api/system/status');
                    const data = await response.json();
                    document.getElementById('demo-result').innerHTML = 
                        '<h4>Статус системы:</h4><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }} catch (e) {{
                    document.getElementById('demo-result').innerHTML = '<p style="color: red;">Ошибка: ' + e.message + '</p>';
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return html_content


@app.route('/chat')
def chat_page():
    """Страница AI чата"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Чат - Hello World v6.0</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            .chat-container { max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .chat-header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
            .chat-messages { height: 400px; overflow-y: auto; padding: 20px; }
            .message { margin-bottom: 15px; }
            .message.user { text-align: right; }
            .message.bot { text-align: left; }
            .message-content { display: inline-block; padding: 10px 15px; border-radius: 20px; max-width: 70%; }
            .message.user .message-content { background-color: #007bff; color: white; }
            .message.bot .message-content { background-color: #e9ecef; color: #333; }
            .chat-input { display: flex; padding: 20px; border-top: 1px solid #ddd; }
            .chat-input input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; margin-right: 10px; }
            .chat-input button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 20px; cursor: pointer; }
            .suggestions { padding: 10px 20px; background-color: #f8f9fa; border-top: 1px solid #ddd; }
            .suggestion { display: inline-block; margin: 5px; padding: 5px 10px; background-color: #e9ecef; border-radius: 15px; cursor: pointer; font-size: 14px; }
            .stats { padding: 20px; background-color: #f8f9fa; text-align: center; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h2>🤖 AI Языковой Помощник</h2>
                <p>Изучайте языки в интерактивном режиме</p>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message bot">
                    <div class="message-content">
                        Привет! 👋 Я ваш AI помощник для изучения языков. Выберите язык и уровень, затем начните диалог!
                    </div>
                </div>
            </div>
            
            <div class="suggestions" id="suggestions">
                <span class="suggestion" onclick="sendMessage('Привет!')">Привет!</span>
                <span class="suggestion" onclick="sendMessage('Hello!')">Hello!</span>
                <span class="suggestion" onclick="sendMessage('¡Hola!')">¡Hola!</span>
                <span class="suggestion" onclick="sendMessage('Помощь')">Помощь</span>
            </div>
            
            <div class="chat-input">
                <select id="language-select" style="margin-right: 10px; padding: 10px;">
                    <option value="ru">Русский</option>
                    <option value="en">English</option>
                    <option value="es">Español</option>
                </select>
                <select id="level-select" style="margin-right: 10px; padding: 10px;">
                    <option value="beginner">Начинающий</option>
                    <option value="intermediate">Средний</option>
                    <option value="advanced">Продвинутый</option>
                </select>
                <input type="text" id="message-input" placeholder="Введите сообщение..." onkeypress="if(event.key=='Enter') sendMessage()">
                <button onclick="sendMessage()">Отправить</button>
            </div>
            
            <div class="stats" id="stats">
                <small>Прогресс: 0 очков | Сообщений: 0</small>
            </div>
        </div>
        
        <script>
            let currentUserId = 'user_' + Date.now();
            let messageCount = 0;
            let progressScore = 0;
            
            async function initializeSession() {
                const language = document.getElementById('language-select').value;
                const level = document.getElementById('level-select').value;
                
                try {
                    const response = await fetch('/api/ai/session', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            user_id: currentUserId,
                            target_language: language,
                            level: level
                        })
                    });
                    const data = await response.json();
                    console.log('Session initialized:', data);
                } catch (error) {
                    console.error('Error initializing session:', error);
                }
            }
            
            async function sendMessage(text) {
                const messageInput = document.getElementById('message-input');
                const message = text || messageInput.value.trim();
                
                if (!message) return;
                
                // Показать сообщение пользователя
                addMessage(message, 'user');
                messageInput.value = '';
                messageCount++;
                
                try {
                    const response = await fetch('/api/ai/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            user_id: currentUserId,
                            message: message
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.error) {
                        addMessage('Ошибка: ' + data.error, 'bot');
                    } else {
                        addMessage(data.response, 'bot');
                        progressScore = data.progress_score || progressScore + 1;
                        updateSuggestions(data.suggestions || []);
                        updateStats();
                    }
                } catch (error) {
                    addMessage('Ошибка соединения: ' + error.message, 'bot');
                }
            }
            
            function addMessage(content, sender) {
                const messagesContainer = document.getElementById('chat-messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + sender;
                messageDiv.innerHTML = '<div class="message-content">' + content + '</div>';
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            function updateSuggestions(suggestions) {
                const suggestionsContainer = document.getElementById('suggestions');
                if (suggestions.length > 0) {
                    suggestionsContainer.innerHTML = suggestions.map(s => 
                        '<span class="suggestion" onclick="sendMessage(\'' + s + '\')">' + s + '</span>'
                    ).join('');
                }
            }
            
            function updateStats() {
                document.getElementById('stats').innerHTML = 
                    '<small>Прогресс: ' + progressScore + ' очков | Сообщений: ' + messageCount + '</small>';
            }
            
            // Инициализация
            document.addEventListener('DOMContentLoaded', function() {
                initializeSession();
                document.getElementById('language-select').addEventListener('change', initializeSession);
                document.getElementById('level-select').addEventListener('change', initializeSession);
            });
        </script>
    </body>
    </html>
    """
    
    return html_content


# === API ROUTES ===

# Основные API (из v5.0)
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
    """API для получения приветствия"""
    if language not in greeter.available_languages():
        return jsonify({'error': 'Language not found'}), 404
    
    info = greeter.get_language_info(language)
    return jsonify(info)


# AI Chatbot API
@app.route('/api/ai/session', methods=['POST'])
def api_ai_create_session():
    """Создать AI сессию"""
    data = request.get_json() or {}
    user_id = data.get('user_id', f'user_{int(time.time())}')
    target_language = data.get('target_language', 'ru')
    level = data.get('level', 'beginner')
    
    try:
        session_data = ai_bot.create_learning_session(user_id, target_language, level)
        return jsonify({
            'success': True,
            'session_id': user_id,
            'target_language': session_data['target_language'],
            'level': session_data['level']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/chat', methods=['POST'])
def api_ai_chat():
    """AI чат"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({'error': 'user_id and message required'}), 400
    
    try:
        response = ai_bot.process_message(user_id, message)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/session/<user_id>')
def api_ai_get_session(user_id):
    """Получить AI сессию"""
    try:
        stats = ai_bot.get_session_statistics(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# OAuth API
@app.route('/api/auth/providers')
def api_auth_providers():
    """Провайдеры OAuth"""
    providers = oauth_service.get_supported_providers()
    return jsonify({'providers': providers})


@app.route('/api/auth/<provider>')
def api_auth_start(provider):
    """Начать OAuth"""
    auth_data = oauth_service.get_auth_url(provider)
    return jsonify(auth_data)


@app.route('/api/auth/demo/<provider>')
def api_auth_demo(provider):
    """Демо OAuth (создает mock пользователя)"""
    mock_data = {
        'email': f'demo@{provider}.com',
        'name': f'Demo User from {provider}',
        'avatar_url': f'https://via.placeholder.com/64?text={provider[0].upper()}'
    }
    
    result = oauth_service.create_mock_user(provider, mock_data)
    return jsonify(result)


# GraphQL API
@app.route('/api/graphql', methods=['POST'])
def api_graphql():
    """GraphQL endpoint"""
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
    """GraphQL схема"""
    sdl = graphql_service.get_schema_sdl()
    return sdl, 200, {'Content-Type': 'text/plain'}


# System API
@app.route('/api/system/status')
def api_system_status():
    """Статус системы v6.0"""
    status = {
        'version': '6.0-unified',
        'uptime': time.time() - app.start_time if hasattr(app, 'start_time') else 0,
        'services': {
            'hello_world': True,
            'ai_chatbot': True,
            'websocket': SOCKETIO_AVAILABLE,
            'oauth': len(oauth_service.providers) > 0,
            'graphql': True,
            'cors': CORS_AVAILABLE,
            'jwt': JWT_AVAILABLE,
            'requests': REQUESTS_AVAILABLE
        },
        'statistics': {
            'ai_sessions': len(ai_bot.sessions),
            'oauth_users': len(oauth_service.users),
            'languages_supported': len(greeter.available_languages())
        },
        'features': [
            'ai_language_learning',
            'real_time_chat' if SOCKETIO_AVAILABLE else 'basic_chat',
            'oauth_authentication' if len(oauth_service.providers) > 0 else 'demo_auth',
            'graphql_api',
            'multi_language_support'
        ]
    }
    
    return jsonify(status)


# WebSocket events (если доступно)
if socketio:
    @socketio.on('connect')
    def handle_connect():
        """WebSocket подключение"""
        logger.info(f"WebSocket подключение: {request.sid}")
        emit('status', {'message': 'Подключен к Hello World v6.0!'})
    
    @socketio.on('ai_message')
    def handle_ai_message(data):
        """WebSocket AI сообщение"""
        user_id = data.get('user_id', 'ws_user')
        message = data.get('message', '')
        
        if message:
            try:
                response = ai_bot.process_message(user_id, message)
                emit('ai_response', response)
            except Exception as e:
                emit('error', {'message': str(e)})


# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(error):
    """404 ошибка"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return f"<h1>404 - Страница не найдена</h1><p><a href='/'>Вернуться на главную</a></p>", 404


@app.errorhandler(500)
def internal_error(error):
    """500 ошибка"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return f"<h1>500 - Внутренняя ошибка</h1><p><a href='/'>Вернуться на главную</a></p>", 500


# === MAIN ===

if __name__ == '__main__':
    # Время старта
    app.start_time = time.time()
    
    # Создаем директории
    os.makedirs('data', exist_ok=True)
    
    print("🚀 Запуск Hello World v6.0 - AI Edition (Unified)")
    print("=" * 60)
    print(f"📊 Статус сервисов:")
    print(f"   🤖 AI Chatbot: ✅ Встроен")
    print(f"   ⚡ WebSocket: {'✅ Активен' if SOCKETIO_AVAILABLE else '❌ Требует flask-socketio'}")
    print(f"   🔐 OAuth: {'✅ Настроен' if len(oauth_service.providers) > 0 else '⚠️ Нужна настройка'}")
    print(f"   📡 GraphQL: ✅ Упрощенная версия")
    print(f"   🌐 CORS: {'✅ Активен' if CORS_AVAILABLE else '❌ Требует flask-cors'}")
    print(f"   🔑 JWT: {'✅ Активен' if JWT_AVAILABLE else '❌ Требует PyJWT'}")
    print(f"   📦 Requests: {'✅ Активен' if REQUESTS_AVAILABLE else '❌ Требует requests'}")
    
    print(f"\n🌟 Возможности v6.0:")
    print(f"   • AI-powered language learning (✅ работает)")
    print(f"   • Interactive chat interface (✅ работает)")
    print(f"   • Multi-service integration (✅ работает)")
    print(f"   • Graceful degradation (✅ работает)")
    print(f"   • Modern web API (✅ работает)")
    
    print(f"\n🌐 Доступные эндпоинты:")
    print(f"   Main App: http://localhost:5000")
    print(f"   AI Chat: http://localhost:5000/chat")
    print(f"   API Status: http://localhost:5000/api/system/status")
    print(f"   Languages: http://localhost:5000/api/languages")
    print(f"   GraphQL: http://localhost:5000/api/graphql")
    
    print(f"\n💡 Для полной функциональности установите:")
    if not SOCKETIO_AVAILABLE:
        print(f"   pip install flask-socketio")
    if not CORS_AVAILABLE:
        print(f"   pip install flask-cors")
    if not JWT_AVAILABLE:
        print(f"   pip install PyJWT")
    if not REQUESTS_AVAILABLE:
        print(f"   pip install requests")
    
    print("=" * 60)
    
    # Запуск
    if socketio:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    else:
        app.run(debug=True, host='0.0.0.0', port=5000)