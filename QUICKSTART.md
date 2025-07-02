# 🚀 Быстрый старт Hello World v5.0

## Простой запуск (Python)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск веб-приложения
python3 web_app.py

# Открыть: http://localhost:5000
```

## Docker запуск (рекомендуется)

```bash
# Запуск всех сервисов
docker-compose up --build

# Доступные адреса:
# Приложение: http://localhost
# Мониторинг: http://localhost:9090
```

## 🧪 Тестирование новых функций

### База данных
```bash
python3 database.py
```

### Аудио сервис
```bash
python3 audio_service.py
```

### Переводчик
```bash
python3 translator_service.py
```

## 🔥 Новые API эндпоинты

### Аудио
```bash
# Получить аудио приветствия на русском
curl http://localhost:5000/api/audio/ru > greeting_ru.wav

# Информация об аудио файле
curl http://localhost:5000/api/audio/info/en
```

### Переводчик
```bash
# Перевести текст
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "source_lang": "en", "target_lang": "ru"}'

# Определить язык
curl -X POST http://localhost:5000/api/translate/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Привет, мир!"}'
```

### Аналитика
```bash
# Статистика системы
curl http://localhost:5000/api/system/status

# История пользователя
curl http://localhost:5000/api/user/history

# Популярные поиски
curl http://localhost:5000/api/popular/searches
```

## 📊 Мониторинг

- **Prometheus**: http://localhost:9090
- **Nginx статус**: http://localhost/nginx_status
- **Системный статус**: http://localhost:5000/api/system/status

## 🔧 Полезные команды

```bash
# Остановить все сервисы
docker-compose down

# Перезапустить только приложение
docker-compose restart hello-world

# Логи приложения
docker-compose logs -f hello-world

# Очистка данных (через API)
curl -X POST http://localhost:5000/api/admin/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
```

## 🎯 Основные возможности v5.0

- ✅ **30 языков** с аудио произношением
- ✅ **Переводчик** с 3 внешними сервисами
- ✅ **База данных** с полной аналитикой
- ✅ **Docker** контейнеризация
- ✅ **Мониторинг** Prometheus + Nginx
- ✅ **API** для всех функций

Enjoy! 🎉