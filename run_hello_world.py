#!/usr/bin/env python3
"""
🚀 Hello World Launcher - Запуск любой версии проекта
Поддерживает версии: v1.0 - v6.0 (unified)
"""

import os
import sys
import subprocess
import time

def show_banner():
    """Показать баннер"""
    print("🌍" * 20)
    print("🚀 HELLO WORLD PROJECT LAUNCHER")
    print("🌍" * 20)
    print("Добро пожаловать! Выберите версию для запуска:")
    print()

def show_versions():
    """Показать доступные версии"""
    versions = {
        '1': {
            'name': 'v1.0 - Basic Hello World',
            'file': 'hello_world.py',
            'description': 'Простой класс WorldGreeter с 30 языками'
        },
        '2': {
            'name': 'v5.0 - Enterprise Edition', 
            'file': 'web_app.py',
            'description': 'Полное web-приложение с базой данных, аудио, переводчиком'
        },
        '3': {
            'name': 'v6.0 - AI Edition (Unified) 🤖',
            'file': 'hello_world_v6_unified.py',
            'description': 'Все v6.0 сервисы в одном файле + AI чат-бот'
        },
        '4': {
            'name': 'v6.0 - AI Edition (Microservices) 🔧',
            'file': 'web_app_v6.py',
            'description': 'Микросервисная архитектура со всеми компонентами'
        },
        '5': {
            'name': 'Test Suite 🧪',
            'file': 'test_v6_unified.py',
            'description': 'Полное тестирование unified версии'
        }
    }
    
    for key, version in versions.items():
        status = "✅" if os.path.exists(version['file']) else "❌"
        print(f"{key}. {status} {version['name']}")
        print(f"   📁 {version['file']}")
        print(f"   📋 {version['description']}")
        print()
    
    return versions

def check_dependencies():
    """Проверить зависимости"""
    print("🔍 Проверка зависимостей...")
    
    deps = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'flask_socketio': 'Flask-SocketIO', 
        'jwt': 'PyJWT',
        'requests': 'requests'
    }
    
    installed = []
    missing = []
    
    for module, name in deps.items():
        try:
            __import__(module)
            installed.append(name)
        except ImportError:
            missing.append(name)
    
    print(f"✅ Установлено: {', '.join(installed)}")
    if missing:
        print(f"⚠️  Отсутствует: {', '.join(missing)}")
        print("💡 Для полной функциональности установите:")
        print(f"   pip install {' '.join(missing)}")
    else:
        print("🎉 Все зависимости установлены!")
    
    print()

def run_version(version_info):
    """Запустить выбранную версию"""
    file_name = version_info['file']
    
    if not os.path.exists(file_name):
        print(f"❌ Файл {file_name} не найден!")
        return False
    
    print(f"🚀 Запуск {version_info['name']}...")
    print(f"📁 Файл: {file_name}")
    print("=" * 50)
    
    try:
        if file_name.endswith('.py'):
            # Запуск Python файла
            result = subprocess.run([sys.executable, file_name], 
                                  capture_output=False, 
                                  text=True)
            return result.returncode == 0
        else:
            print(f"❌ Неизвестный тип файла: {file_name}")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️ Остановлено пользователем")
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return False

def show_quick_info():
    """Показать быструю информацию"""
    print("ℹ️ БЫСТРАЯ СПРАВКА:")
    print()
    print("🔥 Рекомендуем для начала:")
    print("   → Вариант 3: Hello World v6.0 - AI Edition (Unified)")
    print("   → Это самая стабильная и функциональная версия")
    print()
    print("🌐 После запуска откройте в браузере:")
    print("   → http://localhost:5000 - главная страница")
    print("   → http://localhost:5000/chat - AI чат")
    print()
    print("🆘 Если что-то не работает:")
    print("   → Проверьте, что Flask установлен: pip install flask")
    print("   → Убедитесь, что порт 5000 свободен")
    print()

def main():
    """Главная функция"""
    show_banner()
    
    # Проверяем зависимости
    check_dependencies()
    
    # Показываем версии
    versions = show_versions()
    
    # Быстрая справка
    show_quick_info()
    
    # Цикл выбора
    while True:
        try:
            print("👉 Введите номер версии (1-5) или 'q' для выхода:")
            choice = input(">>> ").strip().lower()
            
            if choice == 'q' or choice == 'quit' or choice == 'exit':
                print("👋 До свидания!")
                break
            
            if choice in versions:
                version_info = versions[choice]
                print(f"\n🎯 Выбрано: {version_info['name']}")
                
                # Подтверждение
                confirm = input("Запустить? (y/n): ").strip().lower()
                if confirm in ['y', 'yes', 'да', 'д', '']:
                    success = run_version(version_info)
                    
                    if success:
                        print(f"\n✅ {version_info['name']} завершен успешно")
                    else:
                        print(f"\n❌ Ошибка при запуске {version_info['name']}")
                    
                    print("\n" + "="*50)
                    print("Хотите запустить что-то еще?")
                else:
                    print("❌ Отменено")
            else:
                print("❌ Неверный выбор. Введите число от 1 до 5 или 'q'")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except EOFError:
            print("\n\n👋 До свидания!")
            break

if __name__ == '__main__':
    main()