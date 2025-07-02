#!/usr/bin/env python3
"""
GraphQL API для Hello World проекта
"""

import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import graphene
    from graphene import ObjectType, String, Int, Float, Boolean, List as GrapheneList, Field, Mutation, Schema
    GRAPHENE_AVAILABLE = True
except ImportError:
    GRAPHENE_AVAILABLE = False
    logger.warning("graphene не установлен")

try:
    from hello_world import WorldGreeter
    HELLO_WORLD_AVAILABLE = True
except ImportError:
    HELLO_WORLD_AVAILABLE = False
    logger.warning("WorldGreeter недоступен")

try:
    from ai_chatbot import language_bot
    AI_BOT_AVAILABLE = True
except ImportError:
    AI_BOT_AVAILABLE = False
    logger.warning("AI чат-бот недоступен")

try:
    from oauth_service import oauth_service
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    logger.warning("OAuth сервис недоступен")

try:
    from database import get_database_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logger.warning("Database недоступна")

try:
    from translator_service import translator_service
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logger.warning("Translator сервис недоступен")

try:
    from audio_service import audio_service
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning("Audio сервис недоступен")

if not GRAPHENE_AVAILABLE:
    logger.error("GraphQL API недоступен без библиотеки graphene")
    # Создаем заглушки
    class ObjectType: 
        def __init__(self, **kwargs): pass
    class String: 
        def __init__(self, **kwargs): pass
    class Int: 
        def __init__(self, **kwargs): pass
    class Float: 
        def __init__(self, **kwargs): pass
    class Boolean: 
        def __init__(self, **kwargs): pass
    class GrapheneList: 
        def __init__(self, *args, **kwargs): pass
    class Field: 
        def __init__(self, *args, **kwargs): pass
    class Mutation: 
        def __init__(self, **kwargs): pass
        @classmethod
        def Field(cls): return None
    class Schema: 
        def __init__(self, **kwargs): pass
        def execute(self, *args, **kwargs): 
            return type('Result', (), {'data': None, 'errors': [{'message': 'GraphQL not available'}]})()
    def resolve_placeholder(*args, **kwargs):
        return {"error": "GraphQL not available"}

# GraphQL Types
class LanguageType(ObjectType):
    """Тип языка"""
    code = String(description="Код языка (например, 'ru', 'en')")
    name = String(description="Полное название языка")
    greeting = String(description="Приветствие на языке")
    native_name = String(description="Название на родном языке")
    family = String(description="Языковая семья")
    speakers = Int(description="Количество носителей")
    difficulty = Int(description="Сложность изучения (1-10)")

class UserType(ObjectType):
    """Тип пользователя"""
    user_id = String(description="ID пользователя")
    email = String(description="Email пользователя")
    name = String(description="Имя пользователя")
    provider = String(description="OAuth провайдер")
    avatar_url = String(description="URL аватара")
    locale = String(description="Локаль пользователя")
    verified = Boolean(description="Верифицирован ли пользователь")
    created_at = Float(description="Время создания")
    last_login = Float(description="Последний вход")

class ChatMessageType(ObjectType):
    """Тип сообщения в чате"""
    role = String(description="Роль отправителя (user/assistant/system)")
    content = String(description="Содержимое сообщения")
    timestamp = Float(description="Время отправки")
    language = String(description="Язык сообщения")
    confidence = Float(description="Уверенность AI (0-1)")

class LearningSessionType(ObjectType):
    """Тип сессии изучения языка"""
    user_id = String(description="ID пользователя")
    target_language = String(description="Изучаемый язык")
    native_language = String(description="Родной язык")
    level = String(description="Уровень (beginner/intermediate/advanced)")
    progress_score = Int(description="Очки прогресса")
    created_at = Float(description="Время создания сессии")
    last_activity = Float(description="Последняя активность")
    messages = GrapheneList(ChatMessageType, description="История сообщений")

class TranslationType(ObjectType):
    """Тип перевода"""
    original_text = String(description="Исходный текст")
    translated_text = String(description="Переведенный текст")
    source_language = String(description="Исходный язык")
    target_language = String(description="Целевой язык")
    confidence = Float(description="Уверенность перевода")
    provider = String(description="Провайдер перевода")

class AudioType(ObjectType):
    """Тип аудио"""
    text = String(description="Текст для озвучивания")
    language = String(description="Язык озвучивания")
    audio_url = String(description="URL аудио файла")
    duration = Float(description="Длительность аудио")
    provider = String(description="TTS провайдер")

class StatisticsType(ObjectType):
    """Тип статистики"""
    total_users = Int(description="Общее количество пользователей")
    total_languages = Int(description="Количество поддерживаемых языков")
    total_greetings = Int(description="Общее количество приветствий")
    total_translations = Int(description="Количество переводов")
    active_sessions = Int(description="Активные сессии")
    ai_conversations = Int(description="AI разговоры")

class HealthCheckType(ObjectType):
    """Тип проверки здоровья сервиса"""
    service = String(description="Название сервиса")
    status = String(description="Статус (online/offline/error)")
    version = String(description="Версия")
    uptime = Float(description="Время работы")
    last_check = Float(description="Время последней проверки")

# GraphQL Queries
class Query(ObjectType):
    """Основные запросы GraphQL"""
    
    # Языки и приветствия
    languages = GrapheneList(LanguageType, description="Получить все поддерживаемые языки")
    language = Field(LanguageType, code=String(required=True), description="Получить язык по коду")
    greeting = String(language=String(required=True), description="Получить приветствие на языке")
    random_greeting = Field(LanguageType, description="Получить случайное приветствие")
    
    # Пользователи
    users = GrapheneList(UserType, description="Получить всех пользователей")
    user = Field(UserType, user_id=String(required=True), description="Получить пользователя по ID")
    current_user = Field(UserType, token=String(required=True), description="Получить текущего пользователя по JWT")
    
    # AI чат-бот
    ai_session = Field(LearningSessionType, user_id=String(required=True), 
                      description="Получить сессию изучения языка")
    ai_response = String(user_id=String(required=True), message=String(required=True),
                        target_language=String(), level=String(),
                        description="Получить ответ от AI чат-бота")
    
    # Переводы
    translate = Field(TranslationType, text=String(required=True), 
                     target_language=String(required=True), source_language=String(),
                     description="Перевести текст")
    detect_language = String(text=String(required=True), description="Определить язык текста")
    
    # Аудио
    generate_audio = Field(AudioType, text=String(required=True), language=String(required=True),
                          description="Генерировать аудио для текста")
    
    # Статистика
    statistics = Field(StatisticsType, description="Получить общую статистику")
    health_check = GrapheneList(HealthCheckType, description="Проверить состояние всех сервисов")
    
    # Поиск
    search_languages = GrapheneList(LanguageType, query=String(required=True),
                                  description="Поиск языков по названию")

    def resolve_languages(self, info):
        """Получить все языки"""
        if not HELLO_WORLD_AVAILABLE:
            return []
        
        try:
            greeter = WorldGreeter()
            languages = []
            
            language_data = {
                'ru': {'name': 'Russian', 'native_name': 'Русский', 'family': 'Indo-European', 'speakers': 258000000, 'difficulty': 8},
                'en': {'name': 'English', 'native_name': 'English', 'family': 'Indo-European', 'speakers': 1500000000, 'difficulty': 3},
                'es': {'name': 'Spanish', 'native_name': 'Español', 'family': 'Indo-European', 'speakers': 500000000, 'difficulty': 4},
                'fr': {'name': 'French', 'native_name': 'Français', 'family': 'Indo-European', 'speakers': 280000000, 'difficulty': 5},
                'de': {'name': 'German', 'native_name': 'Deutsch', 'family': 'Indo-European', 'speakers': 130000000, 'difficulty': 6},
                'it': {'name': 'Italian', 'native_name': 'Italiano', 'family': 'Indo-European', 'speakers': 65000000, 'difficulty': 4},
                'pt': {'name': 'Portuguese', 'native_name': 'Português', 'family': 'Indo-European', 'speakers': 260000000, 'difficulty': 4},
                'zh': {'name': 'Chinese', 'native_name': '中文', 'family': 'Sino-Tibetan', 'speakers': 1100000000, 'difficulty': 10},
                'ja': {'name': 'Japanese', 'native_name': '日本語', 'family': 'Japonic', 'speakers': 125000000, 'difficulty': 9},
                'ko': {'name': 'Korean', 'native_name': '한국어', 'family': 'Koreanic', 'speakers': 77000000, 'difficulty': 8},
            }
            
            for code, greeting in greeter.greetings.items():
                data = language_data.get(code, {})
                languages.append(LanguageType(
                    code=code,
                    name=data.get('name', code.upper()),
                    greeting=greeting,
                    native_name=data.get('native_name', data.get('name', code.upper())),
                    family=data.get('family', 'Unknown'),
                    speakers=data.get('speakers', 0),
                    difficulty=data.get('difficulty', 5)
                ))
            
            return languages
            
        except Exception as e:
            logger.error(f"Ошибка получения языков: {e}")
            return []

    def resolve_language(self, info, code):
        """Получить язык по коду"""
        languages = self.resolve_languages(info)
        for lang in languages:
            if lang.code == code:
                return lang
        return None

    def resolve_greeting(self, info, language):
        """Получить приветствие на языке"""
        if not HELLO_WORLD_AVAILABLE:
            return "Hello World service not available"
        
        try:
            greeter = WorldGreeter()
            return greeter.get_greeting(language)
        except Exception as e:
            return f"Error: {str(e)}"

    def resolve_random_greeting(self, info):
        """Получить случайное приветствие"""
        languages = self.resolve_languages(info)
        if languages:
            import random
            return random.choice(languages)
        return None

    def resolve_users(self, info):
        """Получить всех пользователей"""
        if not OAUTH_AVAILABLE:
            return []
        
        try:
            users = []
            for user_id, user_profile in oauth_service.users.items():
                users.append(UserType(
                    user_id=user_profile.user_id,
                    email=user_profile.email,
                    name=user_profile.name,
                    provider=user_profile.provider,
                    avatar_url=user_profile.avatar_url,
                    locale=user_profile.locale,
                    verified=user_profile.verified,
                    created_at=user_profile.created_at,
                    last_login=user_profile.last_login
                ))
            return users
        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            return []

    def resolve_user(self, info, user_id):
        """Получить пользователя по ID"""
        if not OAUTH_AVAILABLE:
            return None
        
        try:
            user_profile = oauth_service.get_user_profile(user_id)
            if user_profile:
                return UserType(
                    user_id=user_profile.user_id,
                    email=user_profile.email,
                    name=user_profile.name,
                    provider=user_profile.provider,
                    avatar_url=user_profile.avatar_url,
                    locale=user_profile.locale,
                    verified=user_profile.verified,
                    created_at=user_profile.created_at,
                    last_login=user_profile.last_login
                )
            return None
        except Exception as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None

    def resolve_current_user(self, info, token):
        """Получить текущего пользователя по JWT токену"""
        if not OAUTH_AVAILABLE:
            return None
        
        try:
            payload = oauth_service.verify_jwt_token(token)
            if payload:
                return self.resolve_user(info, payload['user_id'])
            return None
        except Exception as e:
            logger.error(f"Ошибка верификации токена: {e}")
            return None

    def resolve_ai_session(self, info, user_id):
        """Получить сессию изучения языка"""
        if not AI_BOT_AVAILABLE:
            return None
        
        try:
            for session_id, session in language_bot.sessions.items():
                if session.user_id == user_id:
                    messages = []
                    for msg in session.messages:
                        messages.append(ChatMessageType(
                            role=msg.role,
                            content=msg.content,
                            timestamp=msg.timestamp,
                            language=msg.language,
                            confidence=msg.confidence
                        ))
                    
                    return LearningSessionType(
                        user_id=session.user_id,
                        target_language=session.target_language,
                        native_language=session.native_language,
                        level=session.level,
                        progress_score=session.progress_score,
                        created_at=session.created_at,
                        last_activity=session.last_activity,
                        messages=messages
                    )
            return None
        except Exception as e:
            logger.error(f"Ошибка получения AI сессии: {e}")
            return None

    def resolve_ai_response(self, info, user_id, message, target_language='ru', level='beginner'):
        """Получить ответ от AI чат-бота"""
        if not AI_BOT_AVAILABLE:
            return "AI chatbot not available"
        
        try:
            # Создаем сессию если не существует
            if user_id not in language_bot.sessions:
                language_bot.create_learning_session(user_id, target_language, 'ru', level)
            
            # Получаем ответ
            response = language_bot.process_message(user_id, message)
            return response.get('response', 'No response from AI')
            
        except Exception as e:
            logger.error(f"Ошибка AI ответа: {e}")
            return f"Error: {str(e)}"

    def resolve_translate(self, info, text, target_language, source_language=None):
        """Перевести текст"""
        if not TRANSLATOR_AVAILABLE:
            return TranslationType(
                original_text=text,
                translated_text="Translation service not available",
                source_language=source_language or "unknown",
                target_language=target_language,
                confidence=0.0,
                provider="none"
            )
        
        try:
            result = translator_service.translate_text(text, target_language, source_language)
            return TranslationType(
                original_text=text,
                translated_text=result.get('translated_text', text),
                source_language=result.get('detected_language', source_language or 'unknown'),
                target_language=target_language,
                confidence=result.get('confidence', 0.0),
                provider=result.get('provider', 'unknown')
            )
        except Exception as e:
            logger.error(f"Ошибка перевода: {e}")
            return TranslationType(
                original_text=text,
                translated_text=f"Translation error: {str(e)}",
                source_language=source_language or "unknown",
                target_language=target_language,
                confidence=0.0,
                provider="error"
            )

    def resolve_detect_language(self, info, text):
        """Определить язык текста"""
        if not TRANSLATOR_AVAILABLE:
            return "Language detection not available"
        
        try:
            result = translator_service.detect_language(text)
            return result.get('language', 'unknown')
        except Exception as e:
            logger.error(f"Ошибка определения языка: {e}")
            return "unknown"

    def resolve_generate_audio(self, info, text, language):
        """Генерировать аудио"""
        if not AUDIO_AVAILABLE:
            return AudioType(
                text=text,
                language=language,
                audio_url="",
                duration=0.0,
                provider="none"
            )
        
        try:
            result = audio_service.generate_audio(text, language)
            return AudioType(
                text=text,
                language=language,
                audio_url=result.get('audio_url', ''),
                duration=result.get('duration', 0.0),
                provider=result.get('provider', 'unknown')
            )
        except Exception as e:
            logger.error(f"Ошибка генерации аудио: {e}")
            return AudioType(
                text=text,
                language=language,
                audio_url="",
                duration=0.0,
                provider="error"
            )

    def resolve_statistics(self, info):
        """Получить статистику"""
        stats = StatisticsType(
            total_users=0,
            total_languages=0,
            total_greetings=0,
            total_translations=0,
            active_sessions=0,
            ai_conversations=0
        )
        
        try:
            if OAUTH_AVAILABLE:
                oauth_stats = oauth_service.get_statistics()
                stats.total_users = oauth_stats.get('total_users', 0)
                stats.active_sessions = oauth_stats.get('active_sessions', 0)
            
            if HELLO_WORLD_AVAILABLE:
                greeter = WorldGreeter()
                stats.total_languages = len(greeter.greetings)
                stats.total_greetings = len(greeter.greetings)
            
            if AI_BOT_AVAILABLE:
                stats.ai_conversations = len(language_bot.sessions)
            
            return stats
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return stats

    def resolve_health_check(self, info):
        """Проверить состояние сервисов"""
        services = []
        current_time = time.time()
        
        # Hello World сервис
        services.append(HealthCheckType(
            service="Hello World",
            status="online" if HELLO_WORLD_AVAILABLE else "offline",
            version="6.0",
            uptime=current_time,
            last_check=current_time
        ))
        
        # AI чат-бот
        services.append(HealthCheckType(
            service="AI Chatbot",
            status="online" if AI_BOT_AVAILABLE else "offline",
            version="1.0",
            uptime=current_time,
            last_check=current_time
        ))
        
        # OAuth сервис
        services.append(HealthCheckType(
            service="OAuth",
            status="online" if OAUTH_AVAILABLE else "offline",
            version="1.0",
            uptime=current_time,
            last_check=current_time
        ))
        
        # Translator сервис
        services.append(HealthCheckType(
            service="Translator",
            status="online" if TRANSLATOR_AVAILABLE else "offline",
            version="1.0",
            uptime=current_time,
            last_check=current_time
        ))
        
        # Audio сервис
        services.append(HealthCheckType(
            service="Audio",
            status="online" if AUDIO_AVAILABLE else "offline",
            version="1.0",
            uptime=current_time,
            last_check=current_time
        ))
        
        # Database
        services.append(HealthCheckType(
            service="Database",
            status="online" if DATABASE_AVAILABLE else "offline",
            version="1.0",
            uptime=current_time,
            last_check=current_time
        ))
        
        return services

    def resolve_search_languages(self, info, query):
        """Поиск языков"""
        languages = self.resolve_languages(info)
        query_lower = query.lower()
        
        results = []
        for lang in languages:
            if (query_lower in lang.name.lower() or 
                query_lower in lang.code.lower() or 
                query_lower in lang.native_name.lower()):
                results.append(lang)
        
        return results


# GraphQL Mutations
class CreateAISession(Mutation):
    """Создать сессию изучения языка"""
    
    class Arguments:
        user_id = String(required=True)
        target_language = String(required=True)
        level = String()
    
    session = Field(LearningSessionType)
    success = Boolean()
    error = String()
    
    def mutate(self, info, user_id, target_language, level='beginner'):
        if not AI_BOT_AVAILABLE:
            return CreateAISession(success=False, error="AI chatbot not available")
        
        try:
            session = language_bot.create_learning_session(user_id, target_language, 'ru', level)
            
            messages = []
            for msg in session.messages:
                messages.append(ChatMessageType(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    language=msg.language,
                    confidence=msg.confidence
                ))
            
            session_type = LearningSessionType(
                user_id=session.user_id,
                target_language=session.target_language,
                native_language=session.native_language,
                level=session.level,
                progress_score=session.progress_score,
                created_at=session.created_at,
                last_activity=session.last_activity,
                messages=messages
            )
            
            return CreateAISession(session=session_type, success=True)
            
        except Exception as e:
            logger.error(f"Ошибка создания AI сессии: {e}")
            return CreateAISession(success=False, error=str(e))


class SendAIMessage(Mutation):
    """Отправить сообщение AI чат-боту"""
    
    class Arguments:
        user_id = String(required=True)
        message = String(required=True)
    
    response = String()
    confidence = Float()
    suggestions = GrapheneList(String)
    progress_score = Int()
    success = Boolean()
    error = String()
    
    def mutate(self, info, user_id, message):
        if not AI_BOT_AVAILABLE:
            return SendAIMessage(success=False, error="AI chatbot not available")
        
        try:
            result = language_bot.process_message(user_id, message)
            
            return SendAIMessage(
                response=result.get('response', ''),
                confidence=result.get('confidence', 0.0),
                suggestions=result.get('suggestions', []),
                progress_score=result.get('progress_score', 0),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения AI: {e}")
            return SendAIMessage(success=False, error=str(e))


class Mutation(ObjectType):
    """Мутации GraphQL"""
    create_ai_session = CreateAISession.Field()
    send_ai_message = SendAIMessage.Field()


# Создание схемы GraphQL
if GRAPHENE_AVAILABLE:
    schema = Schema(query=Query, mutation=Mutation)
else:
    schema = None


class GraphQLService:
    """Сервис GraphQL API"""
    
    def __init__(self):
        self.schema = schema
        self.available = GRAPHENE_AVAILABLE
    
    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Выполнить GraphQL запрос"""
        if not self.available:
            return {'errors': [{'message': 'GraphQL not available'}]}
        
        try:
            result = self.schema.execute(query, variables=variables or {})
            
            response = {}
            if result.data:
                response['data'] = result.data
            if result.errors:
                response['errors'] = [{'message': str(error)} for error in result.errors]
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка выполнения GraphQL запроса: {e}")
            return {'errors': [{'message': str(e)}]}
    
    def get_schema_sdl(self) -> str:
        """Получить SDL схемы"""
        if not self.available:
            return "# GraphQL schema not available"
        
        try:
            from graphene.utils.schema_printer import print_schema
            return print_schema(self.schema)
        except Exception as e:
            logger.error(f"Ошибка получения SDL: {e}")
            return f"# Error: {str(e)}"
    
    def introspect(self) -> Dict[str, Any]:
        """Интроспекция схемы"""
        if not self.available:
            return {'error': 'GraphQL not available'}
        
        introspection_query = """
        query IntrospectionQuery {
          __schema {
            types {
              name
              kind
              description
              fields {
                name
                type {
                  name
                  kind
                }
                description
              }
            }
            queryType {
              name
            }
            mutationType {
              name
            }
          }
        }
        """
        
        return self.execute_query(introspection_query)


# Глобальный экземпляр GraphQL сервиса
graphql_service = GraphQLService()


if __name__ == '__main__':
    # Тестирование GraphQL API
    print("📡 Тестирование GraphQL API...")
    
    if not GRAPHENE_AVAILABLE:
        print("❌ graphene не установлен. Установите: pip install graphene")
        print("✅ Тестирование завершено!")
        exit()
    
    service = GraphQLService()
    
    print(f"✅ GraphQL доступен: {service.available}")
    print(f"✅ Hello World: {HELLO_WORLD_AVAILABLE}")
    print(f"✅ AI Chatbot: {AI_BOT_AVAILABLE}")
    print(f"✅ OAuth: {OAUTH_AVAILABLE}")
    print(f"✅ Translator: {TRANSLATOR_AVAILABLE}")
    print(f"✅ Audio: {AUDIO_AVAILABLE}")
    print(f"✅ Database: {DATABASE_AVAILABLE}")
    
    # Тестовые запросы
    test_queries = [
        {
            'name': 'Получить все языки',
            'query': '''
            query {
              languages {
                code
                name
                greeting
                native_name
                speakers
                difficulty
              }
            }
            '''
        },
        {
            'name': 'Получить приветствие',
            'query': '''
            query {
              greeting(language: "ru")
            }
            '''
        },
        {
            'name': 'Случайное приветствие',
            'query': '''
            query {
              randomGreeting {
                code
                name
                greeting
              }
            }
            '''
        },
        {
            'name': 'Статистика',
            'query': '''
            query {
              statistics {
                totalUsers
                totalLanguages
                totalGreetings
                activeSessions
                aiConversations
              }
            }
            '''
        },
        {
            'name': 'Проверка здоровья',
            'query': '''
            query {
              healthCheck {
                service
                status
                version
                uptime
              }
            }
            '''
        },
        {
            'name': 'Поиск языков',
            'query': '''
            query {
              searchLanguages(query: "ru") {
                code
                name
                greeting
              }
            }
            '''
        }
    ]
    
    print(f"\n🧪 Тестирование запросов...")
    for test in test_queries:
        print(f"\n📋 {test['name']}:")
        result = service.execute_query(test['query'])
        
        if 'data' in result:
            print("   ✅ Успешно")
            # Выводим первые несколько строк данных
            data_str = json.dumps(result['data'], indent=2)[:200]
            print(f"   Данные: {data_str}...")
        
        if 'errors' in result:
            print("   ❌ Ошибки:")
            for error in result['errors']:
                print(f"      {error['message']}")
    
    # Тестирование мутаций
    if AI_BOT_AVAILABLE:
        print(f"\n🔄 Тестирование мутаций...")
        
        mutation_query = '''
        mutation {
          createAiSession(userId: "test_user", targetLanguage: "ru", level: "beginner") {
            success
            error
            session {
              userId
              targetLanguage
              level
              progressScore
            }
          }
        }
        '''
        
        result = service.execute_query(mutation_query)
        if 'data' in result:
            print("   ✅ Создание AI сессии успешно")
        else:
            print("   ❌ Ошибка создания AI сессии")
    
    # Интроспекция схемы
    print(f"\n🔍 Интроспекция схемы...")
    introspection = service.introspect()
    if 'data' in introspection:
        schema_info = introspection['data']['__schema']
        print(f"   Типов в схеме: {len(schema_info['types'])}")
        print(f"   Query тип: {schema_info['queryType']['name']}")
        if schema_info['mutationType']:
            print(f"   Mutation тип: {schema_info['mutationType']['name']}")
    
    print(f"\n📄 SDL схемы (первые 500 символов):")
    sdl = service.get_schema_sdl()
    print(sdl[:500] + "...")
    
    print("\n✅ Тестирование GraphQL API завершено!")
    print("\n💡 Примеры использования:")
    print("   1. GraphQL Playground: http://localhost:5000/graphql")
    print("   2. Introspection: query { __schema { types { name } } }")
    print("   3. Простой запрос: query { greeting(language: \"en\") }")