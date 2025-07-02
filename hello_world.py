#!/usr/bin/env python3
"""
Простая программа приветствия мира
"""

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
            'zh': '你好，世界！'
        }
    
    def greet(self, language='en'):
        """Приветствие на указанном языке"""
        return self.greetings.get(language, self.greetings['en'])
    
    def greet_all(self):
        """Приветствие на всех доступных языках"""
        print("=== Приветствие мира на разных языках ===")
        for lang, greeting in self.greetings.items():
            print(f"{lang.upper()}: {greeting}")
    
    def available_languages(self):
        """Показать доступные языки"""
        return list(self.greetings.keys())


def main():
    """Основная функция"""
    greeter = WorldGreeter()
    
    # Оригинальные приветствия
    print("hello")
    print("Hello all")
    print()
    
    # Новая функциональность
    print("🌍 Добро пожаловать в улучшенную программу приветствия!")
    print()
    
    # Приветствие на русском
    print(greeter.greet('ru'))
    
    # Приветствие на всех языках
    print()
    greeter.greet_all()
    
    print()
    print(f"📋 Доступные языки: {', '.join(greeter.available_languages())}")


if __name__ == "__main__":
    main()
