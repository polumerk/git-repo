#!/usr/bin/env python3
"""
Сервис генерации аудио произношения приветствий
"""

import os
import hashlib
import subprocess
import tempfile
from typing import Dict, Optional, Tuple
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Директория для хранения аудио файлов
AUDIO_DIR = Path(os.environ.get('AUDIO_DIR', 'audio'))
AUDIO_DIR.mkdir(exist_ok=True)


class AudioService:
    """Сервис для генерации и кэширования аудио произношения"""
    
    def __init__(self):
        self.audio_dir = AUDIO_DIR
        self.supported_languages = {
            'ru': {'voice': 'ru', 'speed': 150, 'pitch': 50},
            'en': {'voice': 'en', 'speed': 150, 'pitch': 50},
            'es': {'voice': 'es', 'speed': 150, 'pitch': 50},
            'fr': {'voice': 'fr', 'speed': 150, 'pitch': 50},
            'de': {'voice': 'de', 'speed': 150, 'pitch': 50},
            'it': {'voice': 'it', 'speed': 150, 'pitch': 50},
            'pt': {'voice': 'pt', 'speed': 150, 'pitch': 50},
            'pl': {'voice': 'pl', 'speed': 150, 'pitch': 50},
            'nl': {'voice': 'nl', 'speed': 150, 'pitch': 50},
            'sv': {'voice': 'sv', 'speed': 150, 'pitch': 50},
            'no': {'voice': 'no', 'speed': 150, 'pitch': 50},
            'da': {'voice': 'da', 'speed': 150, 'pitch': 50},
            'fi': {'voice': 'fi', 'speed': 150, 'pitch': 50},
            'cs': {'voice': 'cs', 'speed': 150, 'pitch': 50},
            'hu': {'voice': 'hu', 'speed': 150, 'pitch': 50},
            'tr': {'voice': 'tr', 'speed': 150, 'pitch': 50},
            'zh': {'voice': 'zh', 'speed': 140, 'pitch': 45},
            'ja': {'voice': 'ja', 'speed': 140, 'pitch': 45},
            'ko': {'voice': 'ko', 'speed': 145, 'pitch': 50},
            'ar': {'voice': 'ar', 'speed': 140, 'pitch': 50},
            'hi': {'voice': 'hi', 'speed': 145, 'pitch': 50},
        }
    
    def _generate_filename(self, text: str, language: str) -> str:
        """Генерировать имя файла на основе хеша текста и языка"""
        text_hash = hashlib.md5(f"{text}_{language}".encode()).hexdigest()
        return f"{language}_{text_hash}.wav"
    
    def _check_espeak_availability(self) -> bool:
        """Проверить доступность espeak"""
        try:
            result = subprocess.run(['espeak', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _generate_with_espeak(self, text: str, language: str, output_path: str) -> bool:
        """Генерировать аудио с помощью espeak"""
        if not self._check_espeak_availability():
            logger.warning("espeak не доступен")
            return False
        
        try:
            lang_config = self.supported_languages.get(language, self.supported_languages['en'])
            voice = lang_config['voice']
            speed = lang_config['speed']
            pitch = lang_config['pitch']
            
            # Команда для espeak
            cmd = [
                'espeak',
                '-v', voice,
                '-s', str(speed),
                '-p', str(pitch),
                '-w', output_path,
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Аудио сгенерировано с espeak: {output_path}")
                return True
            else:
                logger.error(f"Ошибка espeak: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Таймаут при генерации аудио с espeak")
            return False
        except Exception as e:
            logger.error(f"Ошибка при генерации аудио с espeak: {e}")
            return False
    
    def _generate_with_festival(self, text: str, language: str, output_path: str) -> bool:
        """Генерировать аудио с помощью Festival (альтернативный движок)"""
        try:
            # Создаем временный текстовый файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                temp_text_file = f.name
            
            # Генерируем WAV файл через Festival
            cmd = [
                'festival',
                '--batch',
                '--language', 'english' if language == 'en' else 'english',  # Festival ограничен
                '--eval', f'(tts_file "{temp_text_file}" nil)',
                '--eval', f'(utt.save.wave (car (last (first *current-voice*))) "{output_path}")'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Удаляем временный файл
            os.unlink(temp_text_file)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Аудио сгенерировано с Festival: {output_path}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при генерации аудио с Festival: {e}")
            return False
    
    def _create_simple_beep(self, output_path: str) -> bool:
        """Создать простой звуковой сигнал как fallback"""
        try:
            # Генерируем простой WAV файл с помощью SoX (если доступен)
            cmd = [
                'sox', '-n', output_path,
                'synth', '0.5', 'sine', '800',
                'vol', '0.3'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"Создан простой звуковой сигнал: {output_path}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при создании звукового сигнала: {e}")
            return False
    
    def generate_audio(self, text: str, language: str) -> Optional[str]:
        """
        Генерировать аудио файл для текста на указанном языке
        
        Returns:
            str: Путь к аудио файлу или None при ошибке
        """
        if not text.strip():
            return None
        
        # Генерируем имя файла
        filename = self._generate_filename(text, language)
        output_path = self.audio_dir / filename
        
        # Проверяем, существует ли уже файл
        if output_path.exists():
            logger.info(f"Аудио файл уже существует: {output_path}")
            return str(output_path)
        
        # Пробуем разные движки генерации
        success = False
        
        # 1. Пробуем espeak (основной)
        if self._generate_with_espeak(text, language, str(output_path)):
            success = True
        # 2. Пробуем Festival (альтернативный)
        elif self._generate_with_festival(text, language, str(output_path)):
            success = True
        # 3. Создаем простой звуковой сигнал (fallback)
        elif self._create_simple_beep(str(output_path)):
            success = True
            logger.warning(f"Использован fallback звук для: {text}")
        
        if success and output_path.exists():
            return str(output_path)
        else:
            logger.error(f"Не удалось сгенерировать аудио для: {text}")
            return None
    
    def get_audio_info(self, audio_path: str) -> Dict[str, any]:
        """Получить информацию об аудио файле"""
        try:
            if not os.path.exists(audio_path):
                return {'error': 'Файл не найден'}
            
            # Получаем размер файла
            file_size = os.path.getsize(audio_path)
            
            # Пытаемся получить длительность с помощью soxi (из SoX)
            try:
                result = subprocess.run(['soxi', '-D', audio_path], 
                                      capture_output=True, text=True, timeout=5)
                duration = float(result.stdout.strip()) if result.returncode == 0 else None
            except:
                duration = None
            
            return {
                'path': audio_path,
                'size_bytes': file_size,
                'size_kb': round(file_size / 1024, 2),
                'duration_seconds': duration,
                'exists': True
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup_old_audio(self, max_age_days: int = 30) -> Dict[str, int]:
        """Очистка старых аудио файлов"""
        import time
        
        deleted_count = 0
        total_size_freed = 0
        current_time = time.time()
        
        try:
            for audio_file in self.audio_dir.glob('*.wav'):
                file_age_days = (current_time - audio_file.stat().st_mtime) / (24 * 3600)
                
                if file_age_days > max_age_days:
                    file_size = audio_file.stat().st_size
                    audio_file.unlink()
                    deleted_count += 1
                    total_size_freed += file_size
                    logger.info(f"Удален старый аудио файл: {audio_file}")
            
            return {
                'deleted_files': deleted_count,
                'freed_bytes': total_size_freed,
                'freed_mb': round(total_size_freed / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Ошибка при очистке аудио файлов: {e}")
            return {'error': str(e)}
    
    def get_supported_languages(self) -> Dict[str, Dict[str, any]]:
        """Получить список поддерживаемых языков"""
        return {
            code: {
                'voice': config['voice'],
                'speed': config['speed'],
                'pitch': config['pitch'],
                'available': True
            }
            for code, config in self.supported_languages.items()
        }
    
    def test_tts_engines(self) -> Dict[str, bool]:
        """Тестировать доступность TTS движков"""
        engines = {}
        
        # Тест espeak
        engines['espeak'] = self._check_espeak_availability()
        
        # Тест Festival
        try:
            result = subprocess.run(['festival', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            engines['festival'] = result.returncode == 0
        except:
            engines['festival'] = False
        
        # Тест SoX
        try:
            result = subprocess.run(['sox', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            engines['sox'] = result.returncode == 0
        except:
            engines['sox'] = False
        
        return engines


# Глобальный экземпляр сервиса
audio_service = AudioService()


if __name__ == '__main__':
    # Тестирование аудио сервиса
    print("🔊 Тестирование аудио сервиса...")
    
    # Проверяем доступные движки
    engines = audio_service.test_tts_engines()
    print("🔧 Доступные TTS движки:")
    for engine, available in engines.items():
        status = "✅" if available else "❌"
        print(f"   {status} {engine}")
    
    # Тестируем генерацию аудио
    test_cases = [
        ("Hello, World!", "en"),
        ("Привет, мир!", "ru"),
        ("Hola, Mundo!", "es"),
    ]
    
    print("\n🎵 Тестирование генерации аудио:")
    for text, lang in test_cases:
        audio_path = audio_service.generate_audio(text, lang)
        if audio_path:
            info = audio_service.get_audio_info(audio_path)
            print(f"   ✅ {lang}: {text} -> {info.get('size_kb', 0)} KB")
        else:
            print(f"   ❌ {lang}: {text} -> Ошибка генерации")
    
    # Показываем статистику
    supported = audio_service.get_supported_languages()
    print(f"\n📊 Поддерживается языков: {len(supported)}")
    
    print("✅ Тестирование завершено!")