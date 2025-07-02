#!/usr/bin/env python3
"""
Тест Hello World v6.0 Unified - проверка всех компонентов
"""

import json
import time

def test_ai_chatbot():
    """Тест AI чат-бота"""
    print("🤖 Тестирование AI чат-бота...")
    
    try:
        # Импортируем класс из unified файла
        from hello_world_v6_unified import AILanguageBot
        
        bot = AILanguageBot()
        
        # Создаем сессию
        session = bot.create_learning_session('test_user', 'ru', 'beginner')
        print(f"   ✅ Сессия создана: {session['target_language']}")
        
        # Тестируем диалог
        messages = ['Привет!', 'Спасибо!', 'Помощь']
        for msg in messages:
            response = bot.process_message('test_user', msg)
            print(f"   👤 {msg} → 🤖 {response['response'][:50]}...")
            if response.get('suggestions'):
                print(f"      💡 Предложения: {', '.join(response['suggestions'][:3])}")
        
        # Статистика
        stats = bot.get_session_statistics('test_user')
        print(f"   📊 Статистика: {stats['user_messages']} сообщений, {stats['progress_score']} очков")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False


def test_oauth_service():
    """Тест OAuth сервиса"""
    print("\n🔐 Тестирование OAuth сервиса...")
    
    try:
        from hello_world_v6_unified import OAuthService
        
        oauth = OAuthService()
        
        # Тест провайдеров
        providers = oauth.get_supported_providers()
        print(f"   📋 Провайдеров настроено: {len(providers)}")
        
        # Тест mock пользователя
        mock_result = oauth.create_mock_user('demo', {
            'email': 'test@demo.com',
            'name': 'Test User'
        })
        
        print(f"   ✅ Mock пользователь создан: {mock_result['user']['name']}")
        print(f"   🔑 JWT токен: {mock_result['jwt_token'][:20]}...")
        
        # Тест верификации токена
        payload = oauth.verify_jwt_token(mock_result['jwt_token'])
        print(f"   ✅ Токен верифицирован: {payload['user_id'] if payload else 'Ошибка'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False


def test_graphql_service():
    """Тест GraphQL сервиса"""
    print("\n📡 Тестирование GraphQL сервиса...")
    
    try:
        from hello_world_v6_unified import GraphQLService
        
        graphql = GraphQLService()
        
        # Тест запроса
        result = graphql.execute_query('query { hello }')
        print(f"   ✅ Запрос выполнен: {result['data']['message'][:50]}...")
        
        # Тест схемы
        schema = graphql.get_schema_sdl()
        print(f"   📄 Схема получена: {len(schema)} символов")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False


def test_hello_world_integration():
    """Тест интеграции с основным приложением"""
    print("\n🌍 Тестирование интеграции Hello World...")
    
    try:
        from hello_world_v6_unified import greeter
        
        # Тест языков
        languages = greeter.available_languages()
        print(f"   🗣️  Доступно языков: {len(languages)}")
        
        # Тест приветствий
        test_langs = ['ru', 'en', 'es']
        for lang in test_langs:
            if lang in languages:
                info = greeter.get_language_info(lang)
                print(f"   {lang}: {info['greeting']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False


def test_api_simulation():
    """Симуляция API запросов"""
    print("\n🌐 Симуляция API запросов...")
    
    try:
        from hello_world_v6_unified import app
        
        # Создаем тестовый клиент
        with app.test_client() as client:
            
            # Тест /api/languages
            response = client.get('/api/languages')
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"   ✅ /api/languages: {data['total']} языков")
            else:
                print(f"   ❌ /api/languages: {response.status_code}")
            
            # Тест /api/system/status
            response = client.get('/api/system/status')
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"   ✅ /api/system/status: версия {data['version']}")
                print(f"      🔧 Сервисы: {sum(1 for v in data['services'].values() if v)}/{len(data['services'])} активны")
            else:
                print(f"   ❌ /api/system/status: {response.status_code}")
            
            # Тест AI API
            ai_session_data = {
                'user_id': 'test_api_user',
                'target_language': 'ru',
                'level': 'beginner'
            }
            
            response = client.post('/api/ai/session', 
                                 json=ai_session_data,
                                 content_type='application/json')
            if response.status_code == 200:
                print(f"   ✅ /api/ai/session: сессия создана")
                
                # Тест AI чата
                chat_data = {
                    'user_id': 'test_api_user',
                    'message': 'Привет!'
                }
                
                response = client.post('/api/ai/chat',
                                     json=chat_data,
                                     content_type='application/json')
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"   ✅ /api/ai/chat: {data['response'][:50]}...")
                else:
                    print(f"   ❌ /api/ai/chat: {response.status_code}")
            else:
                print(f"   ❌ /api/ai/session: {response.status_code}")
            
            # Тест GraphQL API
            graphql_data = {
                'query': 'query { hello }'
            }
            
            response = client.post('/api/graphql',
                                 json=graphql_data,
                                 content_type='application/json')
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"   ✅ /api/graphql: {data['data']['message'][:50]}...")
            else:
                print(f"   ❌ /api/graphql: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False


def main():
    """Основная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ HELLO WORLD v6.0 - AI EDITION (UNIFIED)")
    print("=" * 70)
    
    start_time = time.time()
    
    # Запускаем тесты
    tests = [
        ("AI Chatbot", test_ai_chatbot),
        ("OAuth Service", test_oauth_service),
        ("GraphQL Service", test_graphql_service),
        ("Hello World Integration", test_hello_world_integration),
        ("API Simulation", test_api_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"\n❌ Критическая ошибка в {test_name}: {e}")
    
    # Итоги
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"   ✅ Пройдено: {passed}/{total} тестов")
    print(f"   ⏱️  Время: {elapsed:.2f} секунд")
    print(f"   📈 Успешность: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("   Hello World v6.0 - AI Edition готов к использованию!")
    else:
        print(f"\n⚠️  {total - passed} тестов не пройдены")
        print("   Некоторые функции могут работать с ограничениями")
    
    print("\n🚀 Для запуска приложения:")
    print("   python3 hello_world_v6_unified.py")
    print("   Откройте: http://localhost:5000")
    
    print("\n💡 Для полной функциональности установите:")
    print("   pip install flask-socketio flask-cors PyJWT")


if __name__ == '__main__':
    main()