#!/usr/bin/env python3
"""
AI чат-бот для интерактивного изучения языков
"""

import os
import json
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI не установлен. Используется fallback режим.")

# Попытка импорта других AI библиотек
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

@dataclass
class ChatMessage:
    """Структура сообщения в чате"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float
    language: Optional[str] = None
    confidence: Optional[float] = None

@dataclass
class LearningSession:
    """Сессия изучения языка"""
    user_id: str
    target_language: str
    native_language: str
    level: str  # 'beginner', 'intermediate', 'advanced'
    messages: List[ChatMessage]
    created_at: float
    last_activity: float
    topics_covered: List[str]
    progress_score: int = 0

class AILanguageBot:
    """AI чат-бот для изучения языков"""
    
    def __init__(self):
        self.openai_client = None
        self.sessions: Dict[str, LearningSession] = {}
        self.setup_ai_clients()
        
        # Предопределенные ответы и уроки
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
            },
            'fr': {
                'greetings': ['Bonjour!', 'Salut!', 'Bienvenue!'],
                'basics': ['Comment allez-vous?', 'Je m\'appelle...', 'D\'où venez-vous?'],
                'phrases': ['Merci beaucoup', 'De rien', 'Excusez-moi']
            }
        }
        
        self.conversation_starters = {
            'beginner': [
                "Давайте начнем с простых приветствий! Скажите 'привет' на изучаемом языке.",
                "Попробуйте представиться на новом языке!",
                "Как сказать 'спасибо' на языке, который вы изучаете?"
            ],
            'intermediate': [
                "Расскажите о своем дне на изучаемом языке.",
                "Опишите свое любимое место для отдыха.",
                "Какие у вас планы на выходные?"
            ],
            'advanced': [
                "Обсудим текущие события в мире.",
                "Что вы думаете о современных технологиях?",
                "Расскажите об интересной книге, которую вы читали."
            ]
        }
    
    def setup_ai_clients(self):
        """Настройка AI клиентов"""
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    openai.api_key = api_key
                    self.openai_client = openai
                    logger.info("OpenAI API настроен успешно")
                except Exception as e:
                    logger.error(f"Ошибка настройки OpenAI: {e}")
            else:
                logger.warning("OPENAI_API_KEY не найден в переменных среды")
    
    def create_learning_session(self, user_id: str, target_language: str, 
                              native_language: str = 'ru', level: str = 'beginner') -> LearningSession:
        """Создать новую сессию изучения"""
        session = LearningSession(
            user_id=user_id,
            target_language=target_language,
            native_language=native_language,
            level=level,
            messages=[],
            created_at=time.time(),
            last_activity=time.time(),
            topics_covered=[]
        )
        
        # Приветственное сообщение от бота
        welcome_msg = self._generate_welcome_message(target_language, level)
        session.messages.append(ChatMessage(
            role='assistant',
            content=welcome_msg,
            timestamp=time.time(),
            language=target_language
        ))
        
        self.sessions[user_id] = session
        logger.info(f"Создана новая сессия изучения {target_language} для пользователя {user_id}")
        return session
    
    def _generate_welcome_message(self, target_language: str, level: str) -> str:
        """Генерировать приветственное сообщение"""
        welcome_templates = {
            'ru': {
                'beginner': "Привет! 👋 Я ваш AI помощник для изучения русского языка. Давайте начнем с простых фраз!",
                'intermediate': "Здравствуйте! Готовы практиковать русский язык? Попробуем более сложные диалоги!",
                'advanced': "Добро пожаловать! Давайте обсудим интересные темы на русском языке."
            },
            'en': {
                'beginner': "Hello! 👋 I'm your AI assistant for learning English. Let's start with simple phrases!",
                'intermediate': "Hi there! Ready to practice English? Let's try more complex conversations!",
                'advanced': "Welcome! Let's discuss interesting topics in English."
            },
            'es': {
                'beginner': "¡Hola! 👋 Soy tu asistente AI para aprender español. ¡Empecemos con frases simples!",
                'intermediate': "¡Hola! ¿Listo para practicar español? ¡Intentemos conversaciones más complejas!",
                'advanced': "¡Bienvenido! Discutamos temas interesantes en español."
            }
        }
        
        return welcome_templates.get(target_language, {}).get(level, 
            f"Welcome to your {target_language} learning session!")
    
    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Обработать сообщение пользователя"""
        if user_id not in self.sessions:
            return {'error': 'Session not found. Please start a new learning session.'}
        
        session = self.sessions[user_id]
        session.last_activity = time.time()
        
        # Добавляем сообщение пользователя
        user_msg = ChatMessage(
            role='user',
            content=message,
            timestamp=time.time()
        )
        session.messages.append(user_msg)
        
        # Генерируем ответ
        try:
            response = self._generate_response(session, message)
            
            # Добавляем ответ бота
            bot_msg = ChatMessage(
                role='assistant',
                content=response['content'],
                timestamp=time.time(),
                language=session.target_language,
                confidence=response.get('confidence', 0.8)
            )
            session.messages.append(bot_msg)
            
            # Обновляем прогресс
            session.progress_score += response.get('progress_points', 1)
            
            return {
                'response': response['content'],
                'confidence': response.get('confidence', 0.8),
                'suggestions': response.get('suggestions', []),
                'corrections': response.get('corrections', []),
                'progress_score': session.progress_score,
                'next_topic': response.get('next_topic')
            }
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            return {
                'response': "Извините, произошла ошибка. Попробуйте еще раз.",
                'error': str(e)
            }
    
    def _generate_response(self, session: LearningSession, user_message: str) -> Dict[str, Any]:
        """Генерировать ответ на сообщение пользователя"""
        
        # Сначала пробуем OpenAI
        if self.openai_client:
            try:
                return self._generate_openai_response(session, user_message)
            except Exception as e:
                logger.warning(f"OpenAI недоступен: {e}")
        
        # Fallback: используем предопределенные ответы
        return self._generate_fallback_response(session, user_message)
    
    def _generate_openai_response(self, session: LearningSession, user_message: str) -> Dict[str, Any]:
        """Генерировать ответ через OpenAI"""
        
        # Создаем контекст для AI
        system_prompt = f"""
        Вы - AI помощник для изучения {session.target_language} языка.
        Уровень ученика: {session.level}
        Родной язык: {session.native_language}
        
        Ваши задачи:
        1. Отвечайте на {session.target_language} языке (с переводом если нужно)
        2. Исправляйте ошибки мягко и конструктивно
        3. Предлагайте новые слова и фразы
        4. Поддерживайте мотивацию ученика
        5. Адаптируйте сложность под уровень
        
        Формат ответа: JSON с полями: content, suggestions, corrections, confidence, progress_points
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Пытаемся парсить JSON ответ
            try:
                parsed_response = json.loads(ai_response)
                return parsed_response
            except json.JSONDecodeError:
                # Если не JSON, возвращаем как обычный текст
                return {
                    'content': ai_response,
                    'confidence': 0.9,
                    'progress_points': 2
                }
                
        except Exception as e:
            logger.error(f"Ошибка OpenAI API: {e}")
            raise
    
    def _generate_fallback_response(self, session: LearningSession, user_message: str) -> Dict[str, Any]:
        """Генерировать fallback ответ без AI"""
        
        target_lang = session.target_language
        level = session.level
        message_lower = user_message.lower()
        
        # Проверяем ключевые слова и даем соответствующие ответы
        if any(word in message_lower for word in ['привет', 'hello', 'hola', 'bonjour']):
            responses = {
                'ru': "Отлично! Вы поздоровались. Теперь попробуйте спросить 'Как дела?' - 'Как дела?'",
                'en': "Great! You said hello. Now try asking 'How are you?' - 'How are you?'",
                'es': "¡Excelente! Dijiste hola. Ahora intenta preguntar '¿Cómo estás?' - '¿Cómo estás?'",
                'fr': "Parfait! Vous avez dit bonjour. Maintenant essayez de demander 'Comment allez-vous?'"
            }
            
            return {
                'content': responses.get(target_lang, "Good! Now let's learn more phrases."),
                'suggestions': self.language_lessons.get(target_lang, {}).get('basics', []),
                'confidence': 0.8,
                'progress_points': 1
            }
        
        elif any(word in message_lower for word in ['спасибо', 'thank', 'gracias', 'merci']):
            responses = {
                'ru': "Прекрасно! Вы сказали 'спасибо'. Ответ: 'Пожалуйста!' или 'Не за что!'",
                'en': "Perfect! You said 'thank you'. Response: 'You're welcome!' or 'No problem!'",
                'es': "¡Perfecto! Dijiste 'gracias'. Respuesta: '¡De nada!' o '¡No hay de qué!'",
                'fr': "Parfait! Vous avez dit 'merci'. Réponse: 'De rien!' ou 'Je vous en prie!'"
            }
            
            return {
                'content': responses.get(target_lang, "Good! You're learning polite expressions."),
                'suggestions': self.language_lessons.get(target_lang, {}).get('phrases', []),
                'confidence': 0.8,
                'progress_points': 1
            }
        
        elif any(word in message_lower for word in ['помощь', 'help', 'ayuda', 'aide']):
            help_responses = {
                'ru': """
                Я помогу вам изучать русский язык! Вот что я умею:
                📚 Обучение базовым фразам
                ✅ Исправление ошибок  
                💡 Предложения новых слов
                🎯 Адаптация под ваш уровень
                
                Просто пишите мне на русском языке, и я буду помогать!
                """,
                'en': """
                I'll help you learn English! Here's what I can do:
                📚 Teaching basic phrases
                ✅ Correcting mistakes
                💡 Suggesting new words
                🎯 Adapting to your level
                
                Just write to me in English, and I'll help you improve!
                """
            }
            
            return {
                'content': help_responses.get(target_lang, "I'm here to help you learn! Just start talking to me."),
                'confidence': 1.0,
                'progress_points': 0
            }
        
        else:
            # Общий ответ с предложением новой темы
            starters = self.conversation_starters.get(level, self.conversation_starters['beginner'])
            random_starter = random.choice(starters)
            
            responses = {
                'ru': f"Интересно! Давайте попробуем что-то новое: {random_starter}",
                'en': f"Interesting! Let's try something new: {random_starter}",
                'es': f"¡Interesante! Probemos algo nuevo: {random_starter}",
                'fr': f"Intéressant! Essayons quelque chose de nouveau: {random_starter}"
            }
            
            return {
                'content': responses.get(target_lang, f"Let's try: {random_starter}"),
                'suggestions': self._get_random_suggestions(target_lang),
                'confidence': 0.6,
                'progress_points': 1,
                'next_topic': random_starter
            }
    
    def _get_random_suggestions(self, language: str) -> List[str]:
        """Получить случайные предложения для языка"""
        lessons = self.language_lessons.get(language, {})
        all_phrases = []
        for category in lessons.values():
            all_phrases.extend(category)
        
        return random.sample(all_phrases, min(3, len(all_phrases)))
    
    def get_session_statistics(self, user_id: str) -> Dict[str, Any]:
        """Получить статистику сессии"""
        if user_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[user_id]
        
        total_messages = len(session.messages)
        user_messages = len([m for m in session.messages if m.role == 'user'])
        session_duration = time.time() - session.created_at
        
        return {
            'user_id': user_id,
            'target_language': session.target_language,
            'level': session.level,
            'progress_score': session.progress_score,
            'total_messages': total_messages,
            'user_messages': user_messages,
            'session_duration_minutes': round(session_duration / 60, 1),
            'topics_covered': session.topics_covered,
            'last_activity': session.last_activity,
            'messages_per_minute': round(user_messages / (session_duration / 60), 2) if session_duration > 60 else 0
        }
    
    def get_learning_progress(self, user_id: str) -> Dict[str, Any]:
        """Получить прогресс изучения"""
        if user_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[user_id]
        
        # Анализируем прогресс
        level_thresholds = {'beginner': 50, 'intermediate': 100, 'advanced': 200}
        current_threshold = level_thresholds.get(session.level, 50)
        
        progress_percentage = min(100, (session.progress_score / current_threshold) * 100)
        
        return {
            'current_level': session.level,
            'progress_score': session.progress_score,
            'progress_percentage': round(progress_percentage, 1),
            'next_level_threshold': current_threshold,
            'can_level_up': session.progress_score >= current_threshold,
            'achievements': self._get_achievements(session),
            'recommendations': self._get_recommendations(session)
        }
    
    def _get_achievements(self, session: LearningSession) -> List[str]:
        """Получить достижения пользователя"""
        achievements = []
        
        if session.progress_score >= 10:
            achievements.append("🎯 Первые шаги - 10 очков!")
        if session.progress_score >= 25:
            achievements.append("🔥 На разогреве - 25 очков!")
        if session.progress_score >= 50:
            achievements.append("⭐ Уверенный старт - 50 очков!")
        if len(session.messages) >= 20:
            achievements.append("💬 Болтун - 20 сообщений!")
        if len(set(session.topics_covered)) >= 3:
            achievements.append("🌟 Исследователь - 3 темы!")
        
        return achievements
    
    def _get_recommendations(self, session: LearningSession) -> List[str]:
        """Получить рекомендации для изучения"""
        recommendations = []
        
        if session.progress_score < 20:
            recommendations.append("Попробуйте больше простых фраз для начала")
        elif session.progress_score < 50:
            recommendations.append("Отлично! Переходите к более сложным выражениям")
        else:
            recommendations.append("Вы делаете отличные успехи! Попробуйте обсуждать темы")
        
        if len(session.messages) < 10:
            recommendations.append("Практикуйтесь чаще - регулярность очень важна!")
        
        return recommendations
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Очистка старых сессий"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        old_sessions = [
            user_id for user_id, session in self.sessions.items()
            if session.last_activity < cutoff_time
        ]
        
        for user_id in old_sessions:
            del self.sessions[user_id]
            logger.info(f"Удалена старая сессия для пользователя {user_id}")
        
        return len(old_sessions)


# Глобальный экземпляр бота
language_bot = AILanguageBot()


if __name__ == '__main__':
    # Тестирование AI бота
    print("🤖 Тестирование AI чат-бота...")
    
    # Создаем тестовую сессию
    bot = AILanguageBot()
    session = bot.create_learning_session('test_user', 'ru', 'en', 'beginner')
    print(f"✅ Создана сессия изучения русского языка")
    
    # Тестируем диалог
    test_messages = [
        "Hello!",
        "Привет!",
        "Как дела?",
        "Спасибо большое!",
        "помощь"
    ]
    
    print("\n💬 Тестовый диалог:")
    for msg in test_messages:
        print(f"\n👤 Пользователь: {msg}")
        response = bot.process_message('test_user', msg)
        print(f"🤖 Бот: {response['response']}")
        
        if 'suggestions' in response and response['suggestions']:
            print(f"💡 Предложения: {', '.join(response['suggestions'])}")
    
    # Статистика сессии
    print("\n📊 Статистика сессии:")
    stats = bot.get_session_statistics('test_user')
    for key, value in stats.items():
        if key != 'error':
            print(f"   {key}: {value}")
    
    # Прогресс изучения
    print("\n📈 Прогресс изучения:")
    progress = bot.get_learning_progress('test_user')
    for key, value in progress.items():
        if key != 'error':
            print(f"   {key}: {value}")
    
    print("\n✅ Тестирование завершено!")