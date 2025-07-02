#!/usr/bin/env python3
"""
Модуль базы данных для хранения истории использования
"""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import os

# Путь к базе данных
DB_PATH = os.environ.get('DATABASE_URL', 'sqlite:///data/hello_world.db').replace('sqlite:///', '')
DB_DIR = os.path.dirname(DB_PATH)

# Создаем директорию для базы данных, если её нет
if DB_DIR and not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)


class DatabaseManager:
    """Менеджер базы данных для Hello World приложения"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа к колонкам по именам
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Инициализация базы данных с созданием таблиц"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица приветствий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS greetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    language_code TEXT NOT NULL,
                    greeting_text TEXT NOT NULL,
                    access_method TEXT NOT NULL, -- 'web', 'cli', 'api'
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_time_ms INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Таблица поисковых запросов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    query TEXT NOT NULL,
                    results_count INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Таблица статистики языков
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS language_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    language_code TEXT NOT NULL,
                    total_requests INTEGER DEFAULT 0,
                    last_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(language_code)
                )
            ''')
            
            # Таблица системных событий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL, -- 'startup', 'error', 'info'
                    message TEXT NOT NULL,
                    data TEXT, -- JSON для дополнительных данных
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Индексы для производительности
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_greetings_language ON greetings(language_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_greetings_timestamp ON greetings(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_searches_timestamp ON searches(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_session ON users(session_id)')
            
            conn.commit()
    
    def get_or_create_user(self, session_id: str, ip_address: str = None, user_agent: str = None) -> int:
        """Получить или создать пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем, существует ли пользователь
            cursor.execute('SELECT id FROM users WHERE session_id = ?', (session_id,))
            user = cursor.fetchone()
            
            if user:
                # Обновляем время последней активности
                cursor.execute(
                    'UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?',
                    (user['id'],)
                )
                conn.commit()
                return user['id']
            else:
                # Создаем нового пользователя
                cursor.execute('''
                    INSERT INTO users (session_id, ip_address, user_agent)
                    VALUES (?, ?, ?)
                ''', (session_id, ip_address, user_agent))
                conn.commit()
                return cursor.lastrowid
    
    def log_greeting(self, user_id: int, language_code: str, greeting_text: str, 
                    access_method: str, response_time_ms: int = None):
        """Записать использование приветствия"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Логируем приветствие
            cursor.execute('''
                INSERT INTO greetings (user_id, language_code, greeting_text, access_method, response_time_ms)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, language_code, greeting_text, access_method, response_time_ms))
            
            # Обновляем статистику языка
            cursor.execute('''
                INSERT OR REPLACE INTO language_stats (language_code, total_requests, last_requested)
                VALUES (?, 
                       COALESCE((SELECT total_requests FROM language_stats WHERE language_code = ?), 0) + 1,
                       CURRENT_TIMESTAMP)
            ''', (language_code, language_code))
            
            conn.commit()
    
    def log_search(self, user_id: int, query: str, results_count: int):
        """Записать поисковый запрос"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO searches (user_id, query, results_count)
                VALUES (?, ?, ?)
            ''', (user_id, query, results_count))
            conn.commit()
    
    def log_system_event(self, event_type: str, message: str, data: Dict[str, Any] = None):
        """Записать системное событие"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            data_json = json.dumps(data) if data else None
            cursor.execute('''
                INSERT INTO system_events (event_type, message, data)
                VALUES (?, ?, ?)
            ''', (event_type, message, data_json))
            conn.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику использования"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Общая статистика
            cursor.execute('SELECT COUNT(*) as total_users FROM users')
            total_users = cursor.fetchone()['total_users']
            
            cursor.execute('SELECT COUNT(*) as total_greetings FROM greetings')
            total_greetings = cursor.fetchone()['total_greetings']
            
            cursor.execute('SELECT COUNT(*) as total_searches FROM searches')
            total_searches = cursor.fetchone()['total_searches']
            
            # Популярные языки
            cursor.execute('''
                SELECT language_code, total_requests 
                FROM language_stats 
                ORDER BY total_requests DESC 
                LIMIT 10
            ''')
            popular_languages = [dict(row) for row in cursor.fetchall()]
            
            # Активность по дням (последние 30 дней)
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM greetings 
                WHERE timestamp > datetime('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            ''')
            daily_activity = [dict(row) for row in cursor.fetchall()]
            
            # Методы доступа
            cursor.execute('''
                SELECT access_method, COUNT(*) as count
                FROM greetings
                GROUP BY access_method
            ''')
            access_methods = [dict(row) for row in cursor.fetchall()]
            
            # Средняя скорость ответа
            cursor.execute('''
                SELECT AVG(response_time_ms) as avg_response_time
                FROM greetings
                WHERE response_time_ms IS NOT NULL
            ''')
            avg_response = cursor.fetchone()
            avg_response_time = avg_response['avg_response_time'] if avg_response else 0
            
            return {
                'total_users': total_users,
                'total_greetings': total_greetings,
                'total_searches': total_searches,
                'popular_languages': popular_languages,
                'daily_activity': daily_activity,
                'access_methods': access_methods,
                'avg_response_time_ms': round(avg_response_time, 2) if avg_response_time else 0,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
    
    def get_user_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить историю пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT g.language_code, g.greeting_text, g.access_method, g.timestamp
                FROM greetings g
                JOIN users u ON g.user_id = u.id
                WHERE u.session_id = ?
                ORDER BY g.timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_popular_searches(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить популярные поисковые запросы"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT query, COUNT(*) as search_count, AVG(results_count) as avg_results
                FROM searches
                GROUP BY query
                ORDER BY search_count DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_data(self, days: int = 90):
        """Очистка старых данных (старше указанного количества дней)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Удаляем старые приветствия
            cursor.execute('''
                DELETE FROM greetings 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            # Удаляем старые поиски
            cursor.execute('''
                DELETE FROM searches 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            # Удаляем неактивных пользователей
            cursor.execute('''
                DELETE FROM users 
                WHERE last_active < datetime('now', '-' || ? || ' days')
                AND id NOT IN (SELECT DISTINCT user_id FROM greetings WHERE user_id IS NOT NULL)
            ''', (days,))
            
            conn.commit()
            
            return {
                'greetings_deleted': cursor.rowcount,
                'cleanup_date': datetime.now(timezone.utc).isoformat()
            }


# Глобальный экземпляр менеджера базы данных
db_manager = DatabaseManager()


if __name__ == '__main__':
    # Тестирование базы данных
    print("🔧 Инициализация базы данных...")
    
    # Создаем тестового пользователя
    user_id = db_manager.get_or_create_user(
        session_id='test_session_123',
        ip_address='127.0.0.1',
        user_agent='Test Browser'
    )
    print(f"✅ Создан пользователь с ID: {user_id}")
    
    # Логируем тестовое приветствие
    db_manager.log_greeting(
        user_id=user_id,
        language_code='ru',
        greeting_text='Привет, мир!',
        access_method='test',
        response_time_ms=15
    )
    print("✅ Записано тестовое приветствие")
    
    # Логируем тестовый поиск
    db_manager.log_search(user_id=user_id, query='русский', results_count=1)
    print("✅ Записан тестовый поиск")
    
    # Получаем статистику
    stats = db_manager.get_statistics()
    print("📊 Статистика базы данных:")
    print(f"   Пользователей: {stats['total_users']}")
    print(f"   Приветствий: {stats['total_greetings']}")
    print(f"   Поисков: {stats['total_searches']}")
    
    print("✅ База данных готова к работе!")