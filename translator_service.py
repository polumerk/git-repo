#!/usr/bin/env python3
"""
Сервис интеграции с переводчиками
"""

import json
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Кэш переводов в памяти (в реальном приложении лучше использовать Redis)
TRANSLATION_CACHE = {}


class TranslatorService:
    """Сервис для работы с различными переводчиками"""
    
    def __init__(self):
        self.session = self._create_session()
        self.supported_services = {
            'libre': {'name': 'LibreTranslate', 'url': 'https://libretranslate.com', 'free': True},
            'mymemory': {'name': 'MyMemory', 'url': 'https://api.mymemory.translated.net', 'free': True},
            'google_free': {'name': 'Google Translate (Free)', 'url': 'https://translate.googleapis.com', 'free': True},
        }
        
        # Маппинг языков для разных сервисов
        self.language_mapping = {
            'libre': {
                'ru': 'ru', 'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de',
                'it': 'it', 'pt': 'pt', 'pl': 'pl', 'nl': 'nl', 'sv': 'sv',
                'no': 'no', 'da': 'da', 'fi': 'fi', 'cs': 'cs', 'hu': 'hu',
                'tr': 'tr', 'zh': 'zh', 'ja': 'ja', 'ko': 'ko', 'ar': 'ar',
                'hi': 'hi'
            },
            'mymemory': {
                'ru': 'ru-RU', 'en': 'en-US', 'es': 'es-ES', 'fr': 'fr-FR',
                'de': 'de-DE', 'it': 'it-IT', 'pt': 'pt-PT', 'pl': 'pl-PL',
                'nl': 'nl-NL', 'sv': 'sv-SE', 'da': 'da-DK', 'fi': 'fi-FI',
                'cs': 'cs-CZ', 'hu': 'hu-HU', 'tr': 'tr-TR', 'zh': 'zh-CN',
                'ja': 'ja-JP', 'ko': 'ko-KR', 'ar': 'ar-SA', 'hi': 'hi-IN'
            }
        }
    
    def _create_session(self) -> requests.Session:
        """Создать сессию с retry стратегией"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Устанавливаем timeout и headers
        session.headers.update({
            'User-Agent': 'HelloWorld-App/1.0 (Educational Purpose)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        return session
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str, service: str) -> str:
        """Генерировать ключ кэша"""
        content = f"{text}_{source_lang}_{target_lang}_{service}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Получить перевод из кэша"""
        return TRANSLATION_CACHE.get(cache_key)
    
    def _save_to_cache(self, cache_key: str, translation_data: Dict):
        """Сохранить перевод в кэш"""
        translation_data['cached_at'] = time.time()
        TRANSLATION_CACHE[cache_key] = translation_data
        
        # Ограничиваем размер кэша
        if len(TRANSLATION_CACHE) > 1000:
            # Удаляем самые старые записи
            oldest_keys = sorted(TRANSLATION_CACHE.keys(), 
                               key=lambda k: TRANSLATION_CACHE[k].get('cached_at', 0))[:100]
            for key in oldest_keys:
                del TRANSLATION_CACHE[key]
    
    def _translate_with_libretranslate(self, text: str, source_lang: str, target_lang: str) -> Optional[Dict]:
        """Перевод через LibreTranslate"""
        try:
            # Маппинг языков
            source = self.language_mapping['libre'].get(source_lang, source_lang)
            target = self.language_mapping['libre'].get(target_lang, target_lang)
            
            # Пробуем несколько публичных инстансов LibreTranslate
            instances = [
                'https://libretranslate.com/translate',
                'https://translate.argosopentech.com/translate',
                'https://libretranslate.de/translate'
            ]
            
            for instance_url in instances:
                try:
                    data = {
                        'q': text,
                        'source': source,
                        'target': target,
                        'format': 'text'
                    }
                    
                    response = self.session.post(instance_url, json=data, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            'translated_text': result.get('translatedText', ''),
                            'service': 'libretranslate',
                            'confidence': 0.8,  # Примерная оценка
                            'instance': instance_url
                        }
                        
                except Exception as e:
                    logger.warning(f"LibreTranslate instance {instance_url} failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка LibreTranslate: {e}")
            return None
    
    def _translate_with_mymemory(self, text: str, source_lang: str, target_lang: str) -> Optional[Dict]:
        """Перевод через MyMemory"""
        try:
            # Маппинг языков
            source = self.language_mapping['mymemory'].get(source_lang, f"{source_lang}-{source_lang.upper()}")
            target = self.language_mapping['mymemory'].get(target_lang, f"{target_lang}-{target_lang.upper()}")
            
            url = 'https://api.mymemory.translated.net/get'
            params = {
                'q': text,
                'langpair': f'{source}|{target}',
                'de': 'hello@world.app'  # Email для идентификации
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('responseStatus') == 200:
                    translated_text = result.get('responseData', {}).get('translatedText', '')
                    match_quality = result.get('responseData', {}).get('match', 0)
                    
                    return {
                        'translated_text': translated_text,
                        'service': 'mymemory',
                        'confidence': match_quality / 100.0 if match_quality else 0.5,
                        'matches': len(result.get('matches', []))
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка MyMemory: {e}")
            return None
    
    def _translate_with_google_free(self, text: str, source_lang: str, target_lang: str) -> Optional[Dict]:
        """Простой перевод через публичный Google Translate (без API ключа)"""
        try:
            # Это упрощенный метод через веб-интерфейс Google Translate
            # В реальном приложении лучше использовать официальный API
            
            from urllib.parse import quote
            import re
            
            # Формируем URL для Google Translate
            text_encoded = quote(text)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={text_encoded}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Google возвращает JavaScript массив, парсим его
                result = response.json()
                
                if result and len(result) > 0 and result[0]:
                    translated_text = ''.join([item[0] for item in result[0] if item[0]])
                    
                    return {
                        'translated_text': translated_text,
                        'service': 'google_free',
                        'confidence': 0.9,  # Google обычно качественный
                        'detected_source': result[2] if len(result) > 2 else source_lang
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка Google Free: {e}")
            return None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str, 
                      preferred_service: str = None) -> Dict:
        """
        Перевести текст с одного языка на другой
        
        Args:
            text: Текст для перевода
            source_lang: Исходный язык (ISO 639-1)
            target_lang: Целевой язык (ISO 639-1)
            preferred_service: Предпочитаемый сервис
        
        Returns:
            Dict с результатом перевода
        """
        if not text.strip():
            return {'error': 'Пустой текст'}
        
        if source_lang == target_lang:
            return {
                'original_text': text,
                'translated_text': text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'service': 'no_translation_needed',
                'confidence': 1.0
            }
        
        # Проверяем кэш
        cache_key = self._get_cache_key(text, source_lang, target_lang, preferred_service or 'any')
        cached_result = self._get_from_cache(cache_key)
        
        if cached_result:
            cached_result['from_cache'] = True
            return cached_result
        
        # Определяем порядок сервисов
        services = ['mymemory', 'libretranslate', 'google_free']
        if preferred_service and preferred_service in services:
            services = [preferred_service] + [s for s in services if s != preferred_service]
        
        # Пробуем сервисы по очереди
        for service in services:
            try:
                result = None
                
                if service == 'libretranslate':
                    result = self._translate_with_libretranslate(text, source_lang, target_lang)
                elif service == 'mymemory':
                    result = self._translate_with_mymemory(text, source_lang, target_lang)
                elif service == 'google_free':
                    result = self._translate_with_google_free(text, source_lang, target_lang)
                
                if result and result.get('translated_text'):
                    # Добавляем метаданные
                    result.update({
                        'original_text': text,
                        'source_lang': source_lang,
                        'target_lang': target_lang,
                        'timestamp': time.time(),
                        'from_cache': False
                    })
                    
                    # Сохраняем в кэш
                    self._save_to_cache(cache_key, result.copy())
                    
                    logger.info(f"Успешный перевод через {service}: {text[:50]}...")
                    return result
                    
            except Exception as e:
                logger.error(f"Ошибка сервиса {service}: {e}")
                continue
        
        # Если все сервисы не сработали
        return {
            'error': 'Не удалось перевести текст',
            'original_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'attempted_services': services
        }
    
    def detect_language(self, text: str) -> Dict:
        """Определить язык текста"""
        try:
            # Пробуем через MyMemory
            url = 'https://api.mymemory.translated.net/get'
            params = {
                'q': text[:100],  # Первые 100 символов
                'langpair': 'auto|en'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('responseStatus') == 200:
                    detected = result.get('responseData', {}).get('detectedLanguage', '')
                    
                    if detected:
                        # Преобразуем в ISO 639-1 формат
                        lang_code = detected.split('-')[0].lower()
                        
                        return {
                            'detected_language': lang_code,
                            'confidence': 0.8,
                            'service': 'mymemory',
                            'full_code': detected
                        }
            
            # Fallback: простая эвристика по символам
            return self._detect_language_heuristic(text)
            
        except Exception as e:
            logger.error(f"Ошибка определения языка: {e}")
            return self._detect_language_heuristic(text)
    
    def _detect_language_heuristic(self, text: str) -> Dict:
        """Простое определение языка по символам"""
        text_lower = text.lower()
        
        # Проверяем характерные символы
        if any(ord(char) >= 0x0400 and ord(char) <= 0x04FF for char in text):
            return {'detected_language': 'ru', 'confidence': 0.7, 'service': 'heuristic'}
        elif any(ord(char) >= 0x4E00 and ord(char) <= 0x9FFF for char in text):
            return {'detected_language': 'zh', 'confidence': 0.7, 'service': 'heuristic'}
        elif any(ord(char) >= 0x3040 and ord(char) <= 0x309F for char in text):
            return {'detected_language': 'ja', 'confidence': 0.7, 'service': 'heuristic'}
        elif any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in text):
            return {'detected_language': 'ar', 'confidence': 0.7, 'service': 'heuristic'}
        
        # Проверяем частые слова
        common_words = {
            'en': ['hello', 'world', 'the', 'and', 'or', 'but', 'is', 'are'],
            'es': ['hola', 'mundo', 'el', 'la', 'y', 'o', 'pero', 'es'],
            'fr': ['bonjour', 'monde', 'le', 'la', 'et', 'ou', 'mais', 'est'],
            'de': ['hallo', 'welt', 'der', 'die', 'das', 'und', 'oder', 'ist'],
            'it': ['ciao', 'mondo', 'il', 'la', 'e', 'o', 'ma', 'è'],
        }
        
        for lang, words in common_words.items():
            if any(word in text_lower for word in words):
                return {'detected_language': lang, 'confidence': 0.6, 'service': 'heuristic'}
        
        # По умолчанию английский
        return {'detected_language': 'en', 'confidence': 0.3, 'service': 'heuristic'}
    
    def get_supported_languages(self) -> Dict[str, Dict]:
        """Получить поддерживаемые языки для перевода"""
        languages = {}
        
        for service, mapping in self.language_mapping.items():
            for code in mapping.keys():
                if code not in languages:
                    languages[code] = {'services': []}
                languages[code]['services'].append(service)
        
        return languages
    
    def test_services(self) -> Dict[str, Dict]:
        """Тестировать доступность сервисов перевода"""
        results = {}
        
        test_text = "Hello, World!"
        
        for service in self.supported_services.keys():
            try:
                start_time = time.time()
                
                if service == 'libretranslate':
                    result = self._translate_with_libretranslate(test_text, 'en', 'es')
                elif service == 'mymemory':
                    result = self._translate_with_mymemory(test_text, 'en', 'es')
                elif service == 'google_free':
                    result = self._translate_with_google_free(test_text, 'en', 'es')
                else:
                    result = None
                
                response_time = time.time() - start_time
                
                results[service] = {
                    'available': result is not None and bool(result.get('translated_text')),
                    'response_time': round(response_time, 3),
                    'test_result': result.get('translated_text', '') if result else None,
                    'error': None if result else 'No response'
                }
                
            except Exception as e:
                results[service] = {
                    'available': False,
                    'response_time': None,
                    'test_result': None,
                    'error': str(e)
                }
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Получить статистику кэша"""
        return {
            'total_entries': len(TRANSLATION_CACHE),
            'memory_usage_mb': sum(len(str(v)) for v in TRANSLATION_CACHE.values()) / (1024 * 1024),
            'oldest_entry': min(v.get('cached_at', time.time()) for v in TRANSLATION_CACHE.values()) if TRANSLATION_CACHE else None,
            'newest_entry': max(v.get('cached_at', 0) for v in TRANSLATION_CACHE.values()) if TRANSLATION_CACHE else None
        }


# Глобальный экземпляр сервиса
translator_service = TranslatorService()


if __name__ == '__main__':
    # Тестирование сервиса переводчика
    print("🌐 Тестирование сервиса переводчика...")
    
    # Тестируем доступность сервисов
    print("\n🔧 Тестирование доступности сервисов:")
    service_tests = translator_service.test_services()
    for service, result in service_tests.items():
        status = "✅" if result['available'] else "❌"
        time_info = f" ({result['response_time']}s)" if result['response_time'] else ""
        print(f"   {status} {service}{time_info}")
        if result['test_result']:
            print(f"      Перевод: '{result['test_result']}'")
    
    # Тестируем переводы
    print("\n🔄 Тестирование переводов:")
    test_cases = [
        ("Hello, World!", "en", "ru"),
        ("Привет, мир!", "ru", "en"),
        ("Hola, Mundo!", "es", "fr"),
    ]
    
    for text, source, target in test_cases:
        result = translator_service.translate_text(text, source, target)
        if 'error' not in result:
            print(f"   ✅ {source}→{target}: {text} → {result['translated_text']}")
            print(f"      Сервис: {result['service']}, уверенность: {result['confidence']}")
        else:
            print(f"   ❌ {source}→{target}: {result['error']}")
    
    # Тестируем определение языка
    print("\n🔍 Тестирование определения языка:")
    detection_tests = [
        "Hello, how are you?",
        "Привет, как дела?", 
        "Bonjour, comment allez-vous?",
        "Hola, ¿cómo estás?"
    ]
    
    for text in detection_tests:
        result = translator_service.detect_language(text)
        print(f"   '{text}' → {result['detected_language']} (уверенность: {result['confidence']})")
    
    # Статистика
    supported = translator_service.get_supported_languages()
    cache_stats = translator_service.get_cache_stats()
    
    print(f"\n📊 Статистика:")
    print(f"   Поддерживаемых языков: {len(supported)}")
    print(f"   Записей в кэше: {cache_stats['total_entries']}")
    
    print("✅ Тестирование завершено!")