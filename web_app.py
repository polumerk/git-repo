#!/usr/bin/env python3
"""
Веб-интерфейс для программы приветствия мира
"""

from flask import Flask, render_template, request, jsonify
import random
from hello_world import WorldGreeter

app = Flask(__name__)
greeter = WorldGreeter()


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
    if language not in greeter.available_languages():
        return jsonify({'error': 'Language not found'}), 404
    
    info = greeter.get_language_info(language)
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
        results.append(info)
    
    return jsonify({
        'query': query,
        'results': results,
        'total': len(results)
    })


@app.route('/api/random')
def api_random():
    """API для случайного приветствия"""
    lang_code = random.choice(greeter.available_languages())
    info = greeter.get_language_info(lang_code)
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
        'shortest_greeting': min(greetings, key=len)
    }
    
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)