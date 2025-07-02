#!/usr/bin/env python3
"""
Тесты для программы приветствия мира
"""

import unittest
import sys
import io
from unittest.mock import patch, MagicMock
from hello_world import WorldGreeter


class TestWorldGreeter(unittest.TestCase):
    """Тесты для класса WorldGreeter"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.greeter = WorldGreeter()
    
    def test_init(self):
        """Тест инициализации класса"""
        self.assertIsInstance(self.greeter.greetings, dict)
        self.assertIsInstance(self.greeter.language_names, dict)
        self.assertGreater(len(self.greeter.greetings), 0)
        self.assertGreater(len(self.greeter.language_names), 0)
    
    def test_greet_default(self):
        """Тест приветствия по умолчанию (английский)"""
        result = self.greeter.greet()
        self.assertEqual(result, "Hello, World!")
    
    def test_greet_specific_language(self):
        """Тест приветствия на конкретном языке"""
        # Тест русского
        result = self.greeter.greet('ru')
        self.assertEqual(result, "Привет, мир!")
        
        # Тест испанского
        result = self.greeter.greet('es')
        self.assertEqual(result, "Hola, Mundo!")
    
    def test_greet_unknown_language(self):
        """Тест приветствия на неизвестном языке"""
        result = self.greeter.greet('unknown')
        self.assertEqual(result, "Hello, World!")  # Должен вернуть английский по умолчанию
    
    def test_available_languages(self):
        """Тест получения списка доступных языков"""
        languages = self.greeter.available_languages()
        self.assertIsInstance(languages, list)
        self.assertGreater(len(languages), 25)  # Проверяем, что языков больше 25
        self.assertIn('ru', languages)
        self.assertIn('en', languages)
        self.assertIn('es', languages)
    
    def test_get_language_info(self):
        """Тест получения информации о языке"""
        info = self.greeter.get_language_info('ru')
        expected = {
            'code': 'ru',
            'name': 'Русский',
            'greeting': 'Привет, мир!'
        }
        self.assertEqual(info, expected)
    
    def test_get_language_info_unknown(self):
        """Тест получения информации о неизвестном языке"""
        info = self.greeter.get_language_info('unknown')
        self.assertEqual(info['code'], 'unknown')
        self.assertEqual(info['name'], 'UNKNOWN')
        self.assertEqual(info['greeting'], 'Unknown')
    
    def test_search_language_by_code(self):
        """Тест поиска языка по коду"""
        matches = self.greeter.search_language('ru')
        self.assertIn('ru', matches)
    
    def test_search_language_by_name(self):
        """Тест поиска языка по названию"""
        matches = self.greeter.search_language('english')
        self.assertIn('en', matches)
        
        matches = self.greeter.search_language('русский')
        self.assertIn('ru', matches)
    
    def test_search_language_by_greeting(self):
        """Тест поиска языка по тексту приветствия"""
        matches = self.greeter.search_language('hello')
        self.assertIn('en', matches)
        
        matches = self.greeter.search_language('привет')
        self.assertIn('ru', matches)
    
    def test_search_language_no_matches(self):
        """Тест поиска с отсутствующими результатами"""
        matches = self.greeter.search_language('xyz123')
        self.assertEqual(matches, [])
    
    def test_greet_all_output(self):
        """Тест вывода всех приветствий"""
        # Перехватываем stdout
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            with patch('time.sleep'):  # Мокаем sleep для ускорения теста
                self.greeter.greet_all()
        
        output = captured_output.getvalue()
        self.assertIn('Приветствие мира на всех языках', output)
        self.assertIn('Привет, мир!', output)
        self.assertIn('Hello, World!', output)
    
    def test_language_count(self):
        """Тест количества языков"""
        # Проверяем, что языков действительно 30
        self.assertEqual(len(self.greeter.greetings), 30)
        self.assertEqual(len(self.greeter.language_names), 30)
    
    def test_all_languages_have_names(self):
        """Тест того, что у всех языков есть названия"""
        for lang_code in self.greeter.greetings.keys():
            self.assertIn(lang_code, self.greeter.language_names)
    
    def test_greetings_not_empty(self):
        """Тест того, что все приветствия не пустые"""
        for greeting in self.greeter.greetings.values():
            self.assertIsInstance(greeting, str)
            self.assertGreater(len(greeting.strip()), 0)
    
    def test_language_codes_format(self):
        """Тест формата кодов языков"""
        for lang_code in self.greeter.greetings.keys():
            self.assertIsInstance(lang_code, str)
            self.assertGreater(len(lang_code), 1)
            self.assertLessEqual(len(lang_code), 3)
            self.assertEqual(lang_code, lang_code.lower())


class TestHelperFunctions(unittest.TestCase):
    """Тесты для вспомогательных функций"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.greeter = WorldGreeter()
    
    @patch('builtins.print')
    def test_print_menu(self, mock_print):
        """Тест вывода меню"""
        from hello_world import print_menu
        print_menu()
        # Проверяем, что print был вызван
        self.assertTrue(mock_print.called)
    
    @patch('builtins.print')
    def test_show_help(self, mock_print):
        """Тест вывода справки"""
        from hello_world import show_help
        show_help()
        self.assertTrue(mock_print.called)
    
    @patch('builtins.print')
    def test_show_statistics(self, mock_print):
        """Тест вывода статистики"""
        from hello_world import show_statistics
        show_statistics(self.greeter)
        self.assertTrue(mock_print.called)
    
    @patch('builtins.print')
    @patch('random.choice')
    def test_random_greeting(self, mock_choice, mock_print):
        """Тест случайного приветствия"""
        from hello_world import random_greeting
        
        # Мокаем выбор языка
        mock_choice.return_value = 'ru'
        random_greeting(self.greeter)
        
        self.assertTrue(mock_print.called)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.greeter = WorldGreeter()
    
    def test_workflow_search_and_greet(self):
        """Тест рабочего процесса: поиск языка и приветствие"""
        # Ищем язык
        matches = self.greeter.search_language('русский')
        self.assertIn('ru', matches)
        
        # Получаем приветствие
        greeting = self.greeter.greet('ru')
        self.assertEqual(greeting, 'Привет, мир!')
        
        # Получаем информацию
        info = self.greeter.get_language_info('ru')
        self.assertEqual(info['name'], 'Русский')
    
    def test_all_languages_searchable(self):
        """Тест того, что все языки можно найти"""
        for lang_code in self.greeter.available_languages():
            # Поиск по коду
            matches = self.greeter.search_language(lang_code)
            self.assertIn(lang_code, matches)
            
            # Получение информации
            info = self.greeter.get_language_info(lang_code)
            self.assertEqual(info['code'], lang_code)


class TestCommandLineInterface(unittest.TestCase):
    """Тесты интерфейса командной строки"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.original_argv = sys.argv.copy()
    
    def tearDown(self):
        """Очистка после тестов"""
        sys.argv = self.original_argv
    
    @patch('builtins.print')
    def test_command_line_demo(self, mock_print):
        """Тест режима демонстрации"""
        sys.argv = ['hello_world.py', '--demo']
        
        from hello_world import main
        with patch('hello_world.run_original_demo') as mock_demo:
            try:
                main()
            except SystemExit:
                pass
            mock_demo.assert_called_once()
    
    @patch('builtins.print')
    def test_command_line_all(self, mock_print):
        """Тест показа всех языков через командную строку"""
        sys.argv = ['hello_world.py', '--all']
        
        from hello_world import main
        with patch.object(WorldGreeter, 'greet_all') as mock_greet_all:
            try:
                main()
            except SystemExit:
                pass
            mock_greet_all.assert_called_once()
    
    def test_command_line_specific_language(self):
        """Тест приветствия на конкретном языке через командную строку"""
        sys.argv = ['hello_world.py', 'ru']
        
        from hello_world import main
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            try:
                main()
            except SystemExit:
                pass
        
        output = captured_output.getvalue()
        # Проверяем, что вывод содержит русское приветствие
        self.assertIn('Привет, мир!', output)


class TestPerformance(unittest.TestCase):
    """Тесты производительности"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.greeter = WorldGreeter()
    
    def test_search_performance(self):
        """Тест производительности поиска"""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            self.greeter.search_language('hello')
        end_time = time.time()
        
        # Поиск должен быть быстрым (менее 1 секунды для 1000 поисков)
        self.assertLess(end_time - start_time, 1.0)
    
    def test_greet_performance(self):
        """Тест производительности приветствий"""
        import time
        
        start_time = time.time()
        for _ in range(10000):
            self.greeter.greet('ru')
        end_time = time.time()
        
        # Приветствие должно быть очень быстрым
        self.assertLess(end_time - start_time, 0.1)


if __name__ == '__main__':
    # Запуск тестов с подробным выводом
    unittest.main(verbosity=2)