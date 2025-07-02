#!/usr/bin/env python3
"""
Веб-интерфейс для программы приветствия мира с полным функционалом
"""

import os
import time
import uuid
from flask import Flask, render_template, request, jsonify, send_file, session
import random
from hello_world import WorldGreeter

# Импортируем новые сервисы
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

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hello-world-secret-key-2024')
greeter = WorldGreeter()

# Логирование запуска приложения
if DATABASE_ENABLED:
    db_manager.log_system_event('startup', 'Web application started', {
        'audio_enabled': AUDIO_ENABLED,
        'translator_enabled': TRANSLATOR_ENABLED,
        'features': ['database', 'web_interface']
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


@app.before_request
def before_request():
    """Выполняется перед каждым запросом"""
    request.start_time = time.time()
    request.user_id = get_or_create_user()


@app.after_request
def after_request(response):
    """Выполняется после каждого запроса"""
    if hasattr(request, 'start_time'):
        response_time = (time.time() - request.start_time) * 1000
        response.headers['X-Response-Time'] = f"{response_time:.2f}ms"
    return response


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


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


@app.route('/api/search')
def api_search():
    """API для поиска языков"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    matches = greeter.search_language(query)
    results = []
    
    for lang_code in matches:
        info = greeter.get_language_info(lang_code)
        if AUDIO_ENABLED:
            info['audio_url'] = f'/api/audio/{lang_code}'
        results.append(info)
    
    # Логируем поиск
    if DATABASE_ENABLED and request.user_id:
        db_manager.log_search(
            user_id=request.user_id,
            query=query,
            results_count=len(results)
        )
    
    return jsonify({
        'query': query,
        'results': results,
        'total': len(results)
    })


@app.route('/api/random')
def api_random():
    """API для случайного приветствия"""
    start_time = time.time()
    lang_code = random.choice(greeter.available_languages())
    info = greeter.get_language_info(lang_code)
    
    # Логируем использование
    if DATABASE_ENABLED and request.user_id:
        response_time = int((time.time() - start_time) * 1000)
        db_manager.log_greeting(
            user_id=request.user_id,
            language_code=lang_code,
            greeting_text=info['greeting'],
            access_method='api_random',
            response_time_ms=response_time
        )
    
    if AUDIO_ENABLED:
        info['audio_url'] = f'/api/audio/{lang_code}'
    
    return jsonify(info)


@app.route('/api/statistics')
def api_statistics():
    """API для статистики"""
    languages = greeter.available_languages()
    greetings = list(greeter.greetings.values())
    
    stats = {
        'total_languages': len(languages),
        'longest_code': max(languages, key=len),
        'shortest_code': min(languages, key=len),
        'average_greeting_length': sum(len(g) for g in greetings) / len(greetings),
        'longest_greeting': max(greetings, key=len),
        'shortest_greeting': min(greetings, key=len),
        'features': {
            'database': DATABASE_ENABLED,
            'audio': AUDIO_ENABLED,
            'translator': TRANSLATOR_ENABLED
        }
    }
    
    # Добавляем статистику из базы данных
    if DATABASE_ENABLED:
        db_stats = db_manager.get_statistics()
        stats['database_stats'] = db_stats
    
    return jsonify(stats)


# === НОВЫЕ API ЭНДПОИНТЫ ===

@app.route('/api/audio/<language>')
def api_audio(language):
    """API для получения аудио приветствия"""
    if not AUDIO_ENABLED:
        return jsonify({'error': 'Audio service not available'}), 503
    
    if language not in greeter.available_languages():
        return jsonify({'error': 'Language not found'}), 404
    
    info = greeter.get_language_info(language)
    
    try:
        audio_path = audio_service.generate_audio(info['greeting'], language)
        
        if audio_path and os.path.exists(audio_path):
            return send_file(
                audio_path,
                mimetype='audio/wav',
                as_attachment=False,
                download_name=f"greeting_{language}.wav"
            )
        else:
            return jsonify({'error': 'Could not generate audio'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Audio generation failed: {str(e)}'}), 500


@app.route('/api/audio/info/<language>')
def api_audio_info(language):
    """API для получения информации об аудио файле"""
    if not AUDIO_ENABLED:
        return jsonify({'error': 'Audio service not available'}), 503
    
    if language not in greeter.available_languages():
        return jsonify({'error': 'Language not found'}), 404
    
    info = greeter.get_language_info(language)
    audio_path = audio_service.generate_audio(info['greeting'], language)
    
    if audio_path:
        audio_info = audio_service.get_audio_info(audio_path)
        return jsonify(audio_info)
    else:
        return jsonify({'error': 'Audio file not found'}), 404


@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API для перевода текста"""
    if not TRANSLATOR_ENABLED:
        return jsonify({'error': 'Translator service not available'}), 503
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    
    text = data.get('text', '').strip()
    source_lang = data.get('source_lang', 'auto')
    target_lang = data.get('target_lang', 'en')
    service = data.get('service')  # Опциональный предпочитаемый сервис
    
    if not text:
        return jsonify({'error': 'Text parameter required'}), 400
    
    # Определяем язык, если нужно
    if source_lang == 'auto':
        detection = translator_service.detect_language(text)
        source_lang = detection.get('detected_language', 'en')
    
    # Переводим
    result = translator_service.translate_text(text, source_lang, target_lang, service)
    
    return jsonify(result)


@app.route('/api/translate/detect', methods=['POST'])
def api_detect_language():
    """API для определения языка текста"""
    if not TRANSLATOR_ENABLED:
        return jsonify({'error': 'Translator service not available'}), 503
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Text parameter required'}), 400
    
    result = translator_service.detect_language(text)
    return jsonify(result)


@app.route('/api/translate/services')
def api_translate_services():
    """API для получения информации о сервисах перевода"""
    if not TRANSLATOR_ENABLED:
        return jsonify({'error': 'Translator service not available'}), 503
    
    services_status = translator_service.test_services()
    supported_languages = translator_service.get_supported_languages()
    cache_stats = translator_service.get_cache_stats()
    
    return jsonify({
        'services': services_status,
        'supported_languages': supported_languages,
        'cache_stats': cache_stats
    })


@app.route('/api/user/history')
def api_user_history():
    """API для получения истории пользователя"""
    if not DATABASE_ENABLED:
        return jsonify({'error': 'Database not available'}), 503
    
    if not request.user_id:
        return jsonify({'error': 'User session not found'}), 404
    
    limit = request.args.get('limit', 50, type=int)
    history = db_manager.get_user_history(session['session_id'], limit)
    
    return jsonify({
        'history': history,
        'total': len(history)
    })


@app.route('/api/popular/searches')
def api_popular_searches():
    """API для получения популярных поисковых запросов"""
    if not DATABASE_ENABLED:
        return jsonify({'error': 'Database not available'}), 503
    
    limit = request.args.get('limit', 20, type=int)
    popular = db_manager.get_popular_searches(limit)
    
    return jsonify({
        'popular_searches': popular,
        'total': len(popular)
    })


@app.route('/api/system/status')
def api_system_status():
    """API для получения статуса системы"""
    status = {
        'services': {
            'database': DATABASE_ENABLED,
            'audio': AUDIO_ENABLED,
            'translator': TRANSLATOR_ENABLED
        },
        'uptime': time.time() - app.start_time if hasattr(app, 'start_time') else 0,
        'version': '4.0.0',
        'features': [
            'web_interface', 'rest_api', 'multi_language',
            'interactive_console', 'comprehensive_tests'
        ]
    }
    
    if AUDIO_ENABLED:
        status['audio_engines'] = audio_service.test_tts_engines()
    
    if TRANSLATOR_ENABLED:
        status['translation_services'] = {
            name: info['available'] 
            for name, info in translator_service.test_services().items()
        }
    
    return jsonify(status)


@app.route('/api/admin/cleanup', methods=['POST'])
def api_admin_cleanup():
    """API для очистки старых данных (только для админов)"""
    # В реальном приложении здесь должна быть аутентификация
    results = {}
    
    if DATABASE_ENABLED:
        days = request.json.get('days', 90) if request.json else 90
        cleanup_result = db_manager.cleanup_old_data(days)
        results['database'] = cleanup_result
    
    if AUDIO_ENABLED:
        days = request.json.get('audio_days', 30) if request.json else 30
        audio_cleanup = audio_service.cleanup_old_audio(days)
        results['audio'] = audio_cleanup
    
    return jsonify(results)


if __name__ == '__main__':
    # Устанавливаем время старта приложения
    app.start_time = time.time()
    
    # Создаем необходимые директории
    os.makedirs('data', exist_ok=True)
    os.makedirs('audio', exist_ok=True)
    
    print("🚀 Запуск Hello World веб-приложения v4.0")
    print(f"📊 Включенные сервисы:")
    print(f"   Database: {'✅' if DATABASE_ENABLED else '❌'}")
    print(f"   Audio: {'✅' if AUDIO_ENABLED else '❌'}")
    print(f"   Translator: {'✅' if TRANSLATOR_ENABLED else '❌'}")
    print(f"🌐 Сервер доступен по адресу: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)