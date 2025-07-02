#!/usr/bin/env python3
"""
Интерактивная программа приветствия мира с поддержкой множественных языков
"""

import sys
import time
from typing import Dict, List, Optional


class WorldGreeter:
    """Класс для приветствия мира на разных языках"""
    
    def __init__(self):
        self.greetings = {
            'ru': 'Привет, мир!',
            'en': 'Hello, World!',
            'es': 'Hola, Mundo!',
            'fr': 'Bonjour, le monde!',
            'de': 'Hallo, Welt!',
            'it': 'Ciao, mondo!',
            'ja': 'こんにちは、世界！',
            'zh': '你好，世界！',
            'ar': 'مرحبا بالعالم!',
            'hi': 'नमस्ते, दुनिया!',
            'pt': 'Olá, Mundo!',
            'ko': '안녕하세요, 세계!',
            'tr': 'Merhaba, Dünya!',
            'pl': 'Witaj, świecie!',
            'nl': 'Hallo, wereld!',
            'sv': 'Hej, världen!',
            'no': 'Hei, verden!',
            'fi': 'Hei, maailma!',
            'da': 'Hej, verden!',
            'cs': 'Ahoj, světe!',
            'hu': 'Helló, világ!',
            'ro': 'Salut, lume!',
            'bg': 'Здравей, свят!',
            'hr': 'Pozdrav, svijete!',
            'sk': 'Ahoj, svet!',
            'sl': 'Pozdravljen, svet!',
            'et': 'Tere, maailm!',
            'lv': 'Sveika, pasaule!',
            'lt': 'Labas, pasauli!',
            'mt': 'Hello, dinja!'
        }
        
        self.language_names = {
            'ru': 'Русский', 'en': 'English', 'es': 'Español', 'fr': 'Français',
            'de': 'Deutsch', 'it': 'Italiano', 'ja': '日本語', 'zh': '中文',
            'ar': 'العربية', 'hi': 'हिन्दी', 'pt': 'Português', 'ko': '한국어',
            'tr': 'Türkçe', 'pl': 'Polski', 'nl': 'Nederlands', 'sv': 'Svenska',
            'no': 'Norsk', 'fi': 'Suomi', 'da': 'Dansk', 'cs': 'Čeština',
            'hu': 'Magyar', 'ro': 'Română', 'bg': 'Български', 'hr': 'Hrvatski',
            'sk': 'Slovenčina', 'sl': 'Slovenščina', 'et': 'Eesti', 'lv': 'Latviešu',
            'lt': 'Lietuvių', 'mt': 'Malti'
        }
    
    def greet(self, language: str = 'en') -> str:
        """Приветствие на указанном языке"""
        return self.greetings.get(language, self.greetings['en'])
    
    def greet_all(self) -> None:
        """Приветствие на всех доступных языках"""
        print("🌍 === Приветствие мира на всех языках ===")
        for i, (lang, greeting) in enumerate(self.greetings.items(), 1):
            lang_name = self.language_names.get(lang, lang.upper())
            print(f"{i:2d}. {lang.upper()}: {greeting} ({lang_name})")
            if i % 5 == 0:  # Пауза каждые 5 языков
                time.sleep(0.5)
    
    def available_languages(self) -> List[str]:
        """Список доступных языков"""
        return list(self.greetings.keys())
    
    def get_language_info(self, language: str) -> Dict[str, str]:
        """Получить информацию о языке"""
        return {
            'code': language,
            'name': self.language_names.get(language, language.upper()),
            'greeting': self.greetings.get(language, 'Unknown')
        }
    
    def search_language(self, query: str) -> List[str]:
        """Поиск языка по названию или коду"""
        query = query.lower()
        matches = []
        
        for code, name in self.language_names.items():
            if (query in code.lower() or 
                query in name.lower() or 
                query in self.greetings[code].lower()):
                matches.append(code)
        
        return matches


def print_menu() -> None:
    """Показать главное меню"""
    print("\n" + "="*50)
    print("🌍 ИНТЕРАКТИВНОЕ ПРИВЕТСТВИЕ МИРА")
    print("="*50)
    print("1. 👋 Показать все языки")
    print("2. 🎯 Выбрать конкретный язык")
    print("3. 🔍 Найти язык")
    print("4. 🎲 Случайное приветствие")
    print("5. 📊 Статистика")
    print("6. ❓ Справка")
    print("0. 🚪 Выход")
    print("="*50)


def interactive_language_selection(greeter: WorldGreeter) -> None:
    """Интерактивный выбор языка"""
    languages = greeter.available_languages()
    
    print(f"\n📋 Доступно {len(languages)} языков:")
    print("-" * 40)
    
    # Показать языки в колонках
    for i in range(0, len(languages), 3):
        row = []
        for j in range(3):
            if i + j < len(languages):
                lang = languages[i + j]
                name = greeter.language_names.get(lang, lang.upper())
                row.append(f"{lang:3s} - {name:15s}")
        print("  ".join(row))
    
    print("-" * 40)
    
    while True:
        choice = input("\n🎯 Введите код языка (или 'menu' для возврата): ").strip().lower()
        
        if choice == 'menu':
            break
        elif choice in languages:
            info = greeter.get_language_info(choice)
            print(f"\n🎉 {info['greeting']}")
            print(f"📝 Язык: {info['name']} ({info['code'].upper()})")
        else:
            print(f"❌ Язык '{choice}' не найден. Попробуйте еще раз.")


def search_languages(greeter: WorldGreeter) -> None:
    """Поиск языков"""
    query = input("\n🔍 Введите поисковый запрос: ").strip()
    
    if not query:
        print("❌ Пустой запрос!")
        return
    
    matches = greeter.search_language(query)
    
    if matches:
        print(f"\n✅ Найдено {len(matches)} совпадений для '{query}':")
        for lang in matches:
            info = greeter.get_language_info(lang)
            print(f"  • {info['code'].upper()}: {info['greeting']} ({info['name']})")
    else:
        print(f"❌ Ничего не найдено для '{query}'")


def random_greeting(greeter: WorldGreeter) -> None:
    """Случайное приветствие"""
    import random
    
    lang = random.choice(greeter.available_languages())
    info = greeter.get_language_info(lang)
    
    print(f"\n🎲 Случайное приветствие:")
    print(f"🎉 {info['greeting']}")
    print(f"📝 Язык: {info['name']} ({info['code'].upper()})")


def show_statistics(greeter: WorldGreeter) -> None:
    """Показать статистику"""
    languages = greeter.available_languages()
    
    print(f"\n📊 СТАТИСТИКА ПРОЕКТА")
    print("-" * 30)
    print(f"🌍 Всего языков: {len(languages)}")
    print(f"🎯 Самый длинный код: {max(languages, key=len)}")
    print(f"🎯 Самый короткий код: {min(languages, key=len)}")
    
    # Статистика по приветствиям
    greetings = list(greeter.greetings.values())
    avg_length = sum(len(g) for g in greetings) / len(greetings)
    print(f"📏 Средняя длина приветствия: {avg_length:.1f} символов")
    
    longest_greeting = max(greetings, key=len)
    shortest_greeting = min(greetings, key=len)
    print(f"📏 Самое длинное: '{longest_greeting}'")
    print(f"📏 Самое короткое: '{shortest_greeting}'")


def show_help() -> None:
    """Показать справку"""
    print(f"\n❓ СПРАВКА")
    print("-" * 30)
    print("🌍 Эта программа умеет приветствовать мир на 30 языках!")
    print("📋 Выберите пункт меню для навигации")
    print("🎯 Коды языков - это стандартные ISO 639-1 коды")
    print("🔍 Поиск работает по кодам, названиям и текстам приветствий")
    print("🎲 Случайное приветствие выбирает язык автоматически")
    print("📊 Статистика показывает интересные факты о проекте")


def run_original_demo(greeter: WorldGreeter) -> None:
    """Запуск оригинальной демонстрации"""
    print("🔄 Запуск оригинальной демонстрации...\n")
    
    # Оригинальные приветствия
    print("hello")
    print("Hello all")
    print()
    
    # Приветствие на русском
    print("🌍 Добро пожаловать в улучшенную программу приветствия!")
    print(greeter.greet('ru'))


def main() -> None:
    """Основная функция с интерактивным меню"""
    greeter = WorldGreeter()
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            run_original_demo(greeter)
            return
        elif sys.argv[1] == '--all':
            greeter.greet_all()
            return
        elif sys.argv[1] in greeter.available_languages():
            info = greeter.get_language_info(sys.argv[1])
            print(f"{info['greeting']} ({info['name']})")
            return
    
    # Интерактивный режим
    run_original_demo(greeter)
    
    while True:
        print_menu()
        choice = input("\n🎯 Выберите пункт меню: ").strip()
        
        if choice == '0':
            print("\n👋 До свидания! Goodbye! Auf Wiedersehen! Au revoir!")
            break
        elif choice == '1':
            greeter.greet_all()
        elif choice == '2':
            interactive_language_selection(greeter)
        elif choice == '3':
            search_languages(greeter)
        elif choice == '4':
            random_greeting(greeter)
        elif choice == '5':
            show_statistics(greeter)
        elif choice == '6':
            show_help()
        else:
            print("❌ Неверный выбор! Попробуйте еще раз.")
        
        input("\n⏸️  Нажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
