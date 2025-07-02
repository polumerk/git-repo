# 🌍 Hello World Project

Интерактивная программа приветствия мира с поддержкой 30 языков, веб-интерфейсом и полным набором тестов.

## 📝 Описание

Этот проект демонстрирует современные концепции разработки на Python:
- **Объектно-ориентированное программирование** (класс `WorldGreeter`)
- **Интерактивный консольный интерфейс** с меню навигации
- **Веб-приложение** на Flask с REST API
- **Полное покрытие тестами** (unittest)
- **Поиск и фильтрация** языков
- **Статистика** проекта
- **Многоязычная поддержка** (30 языков)

## 🚀 Способы запуска

### Консольное приложение

```bash
# Интерактивный режим
python3 hello_world.py

# Демонстрация
python3 hello_world.py --demo

# Показать все языки
python3 hello_world.py --all

# Приветствие на конкретном языке
python3 hello_world.py ru
```

### Веб-приложение

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить веб-сервер (все сервисы)
python3 web_app.py

# Открыть браузер: http://localhost:5000
```

### Docker (рекомендуется)

```bash
# Собрать и запустить все сервисы
docker-compose up --build

# Открыть браузер: http://localhost
# Prometheus: http://localhost:9090
```

### Только основное приложение (Docker)

```bash
# Собрать образ
docker build -t hello-world .

# Запустить контейнер
docker run -p 5000:5000 -v $(pwd)/data:/app/data hello-world
```

### Тесты

```bash
# Запустить все тесты
python3 test_hello_world.py

# Запустить с подробным выводом
python3 -m unittest test_hello_world -v
```

## ✨ Функциональность

### Консольный интерфейс
- **Интерактивное меню** с навигацией
- **Поиск языков** по коду, названию или тексту приветствия
- **Случайное приветствие**
- **Статистика проекта**
- **Интерактивный выбор языка**

### Веб-интерфейс
- **Современный responsive дизайн**
- **REST API** для всех функций
- **Живой поиск** с автодополнением
- **Интерактивные карточки** языков
- **Анимации и эффекты**

### Класс WorldGreeter
- `greet(language)` - приветствие на конкретном языке
- `greet_all()` - приветствие на всех языках
- `available_languages()` - список доступных языков
- `get_language_info(language)` - информация о языке
- `search_language(query)` - поиск языков

## 🗣️ Поддерживаемые языки (30)

### Европейские языки
- 🇷🇺 Русский (ru) - 🇺🇸 Английский (en) - 🇪🇸 Испанский (es) - 🇫🇷 Французский (fr)
- 🇩🇪 Немецкий (de) - 🇮🇹 Итальянский (it) - 🇵🇱 Польский (pl) - 🇳🇱 Голландский (nl)
- 🇸🇪 Шведский (sv) - 🇳🇴 Норвежский (no) - 🇫🇮 Финский (fi) - 🇩🇰 Датский (da)
- 🇨🇿 Чешский (cs) - 🇭🇺 Венгерский (hu) - 🇷🇴 Румынский (ro) - 🇧🇬 Болгарский (bg)
- 🇭🇷 Хорватский (hr) - 🇸🇰 Словацкий (sk) - 🇸🇮 Словенский (sl) - 🇪🇪 Эстонский (et)
- 🇱🇻 Латышский (lv) - 🇱🇹 Литовский (lt) - 🇲🇹 Мальтийский (mt)

### Азиатские языки
- 🇯🇵 Японский (ja) - 🇨🇳 Китайский (zh) - 🇰🇷 Корейский (ko) - 🇮🇳 Хинди (hi)

### Другие языки
- 🇵🇹 Португальский (pt) - 🇹🇷 Турецкий (tr) - 🇸🇦 Арабский (ar)

## 📁 Структура проекта

```
.
├── hello_world.py        # Основная программа с интерактивным интерфейсом
├── web_app.py           # Flask веб-приложение и REST API
├── test_hello_world.py  # Полный набор тестов
├── requirements.txt     # Зависимости проекта
├── README.md           # Документация проекта
├── templates/          # HTML шаблоны для веб-интерфейса
│   └── index.html     # Главная страница веб-приложения
└── .git/              # Git репозиторий
```

## 🔧 Требования

### Минимальные
- **Python 3.7+** (для type hints)
- **Flask 2.3.3** (для веб-интерфейса)
- **requests 2.31.0** (для переводчика)

### Опциональные (для полной функциональности)
- **Docker & Docker Compose** (рекомендуется)
- **espeak-ng** (для аудио произношения)
- **festival** (альтернативный TTS)
- **sox** (для обработки аудио)

### Установка зависимостей

```bash
# Python зависимости
pip install -r requirements.txt

# Системные зависимости (Ubuntu/Debian)
sudo apt-get install espeak-ng festival sox

# Или через Docker (все уже включено)
docker-compose up --build
```

## 📈 История разработки

- **v1.0** (2024): Простая программа "Hello World"
- **v1.1** (2024): Исправлена синтаксическая ошибка
- **v2.0** (2024): Добавлены класс WorldGreeter и 8 языков
- **v3.0** (2024): Расширено до 30 языков, добавлена интерактивность
- **v4.0** (2024): Веб-интерфейс, REST API, полное покрытие тестами
- **v5.0** (2025): **🆕 Enterprise-ready** - База данных, аудио, переводчик, Docker, мониторинг

## 🎯 Реализованные функции

- ✅ Добавить больше языков (30 языков)
- ✅ Интерактивный выбор языка
- ✅ Веб-интерфейс
- ✅ Тесты

## 🔮 Реализованные в v5.0 функции

- ✅ **Docker контейнеризация** - полная поддержка контейнеров с multi-stage build
- ✅ **База данных для хранения истории** - SQLite с полной аналитикой
- ✅ **Аудио произношение приветствий** - TTS с поддержкой espeak/festival/SoX
- ✅ **Интеграция с переводчиками** - поддержка MyMemory, LibreTranslate, Google
- ✅ **Многопользовательский режим** - сессии, логирование, персональная история
- ✅ **Мониторинг и аналитика** - Prometheus, Nginx, Redis, расширенная статистика

## 🚀 Новые возможности v5.0

### 🐳 Docker & DevOps
- **Dockerfile** с multi-stage build для оптимизации
- **docker-compose.yml** с Redis, Nginx, Prometheus
- **Nginx** конфигурация с load balancing и кэшированием
- **Prometheus** мониторинг с метриками производительности

### 💾 База данных
- **SQLite** база с 5 таблицами: пользователи, приветствия, поиски, статистика, события
- **Автоматическое логирование** всех действий пользователей
- **Аналитика**: популярные языки, активность по дням, средняя скорость ответа
- **Очистка данных** с настраиваемым периодом хранения

### 🔊 Аудио сервис
- **Text-to-Speech** с поддержкой 21 языка
- **Несколько TTS движков**: espeak, Festival, SoX (с fallback)
- **Кэширование аудио** файлов для быстрого доступа
- **API эндпоинты** для получения и воспроизведения аудио

### 🌐 Переводчик
- **3 внешних сервиса**: MyMemory, LibreTranslate, Google Translate
- **Автоматическое определение языка** с heuristic fallback
- **Кэширование переводов** в памяти для скорости
- **Retry стратегия** и обработка ошибок

### 📊 Расширенная аналитика
- **Пользовательская статистика**: история, персональные метрики
- **Системная статистика**: uptime, доступность сервисов, производительность
- **Популярные запросы** и тренды использования
- **Real-time мониторинг** через REST API

## 📁 Обновленная структура v5.0

```
.
├── hello_world.py        # Основная программа (v4.0)
├── web_app.py           # Веб-приложение (v5.0 - обновлено)
├── database.py          # 🆕 База данных и аналитика
├── audio_service.py     # 🆕 TTS и аудио сервис
├── translator_service.py # 🆕 Многосервисный переводчик
├── test_hello_world.py  # Тесты (v4.0)
├── requirements.txt     # Зависимости (обновлено)
├── Dockerfile          # 🆕 Docker образ
├── docker-compose.yml  # 🆕 Оркестрация сервисов
├── .dockerignore       # 🆕 Docker игнор
├── nginx.conf          # 🆕 Nginx конфигурация
├── monitoring/         # 🆕 Мониторинг
│   └── prometheus.yml  # Prometheus конфигурация
├── templates/          # HTML шаблоны
│   └── index.html     # Веб-интерфейс
├── data/              # 🆕 База данных
├── audio/             # 🆕 Аудио файлы
└── README.md          # Документация
```

## ✅ **Реализованные возможности v6.0 - AI Edition**

- [x] **🤖 AI чат-бот** для интерактивного изучения языков
- [x] **⚡ WebSocket поддержка** для real-time обновлений и чата
- [x] **🔐 OAuth аутентификация** (Google, GitHub, VK)
- [x] **📡 GraphQL API** для гибких запросов данных
- [x] **🎯 Умное изучение языков** с персонализацией
- [x] **📊 Расширенная аналитика** прогресса пользователей
- [x] **🌐 Modern Web API** с поддержкой всех сервисов

## 🚀 Новые возможности v6.0 - AI Edition

### 🤖 **AI Language Learning Bot**
- **Интерактивные диалоги** на 30+ языках с адаптивным уровнем сложности
- **Умные ответы** с fallback режимом (работает без OpenAI API)
- **Система прогресса** с достижениями и рекомендациями
- **Исправление ошибок** с конструктивной обратной связью
- **Адаптация под уровень**: beginner, intermediate, advanced

### ⚡ **Real-time WebSocket Communication**
- **Мгновенные ответы** AI чат-бота без перезагрузки страницы
- **Live-обновления** статуса пользователей и индикаторы набора
- **Многопользовательские чат-комнаты** с автоматическим управлением
- **Graceful Reconnection** при потере соединения
- **Event-driven архитектура** для масштабируемости

### 🔐 **OAuth Authentication System**
- **Поддержка провайдеров**: Google, GitHub, VK
- **JWT токены** с автоматическим refresh и безопасным хранением
- **Защищенные API эндпоинты** с middleware авторизации
- **Профили пользователей** с аватарами и метаданными
- **CSRF protection** и secure state management

### 📡 **GraphQL API**
- **Flexible queries** с поддержкой всех сервисов
- **Type-safe schema** с comprehensive introspection
- **Mutations** для создания AI сессий и отправки сообщений
- **Real-time subscriptions** (в планах)
- **GraphQL Playground** для разработки и тестирования

### 🎯 **Enhanced User Experience**
- **Персонализированное обучение** на основе истории пользователя
- **Интеллектуальные рекомендации** следующих тем для изучения
- **Система достижений** с прогрессом и мотивацией
- **Cross-service интеграция** всех v5.0 + v6.0 возможностей

## 📁 Обновленная структура v6.0

```
.
├── hello_world.py        # Основная программа (v4.0)
├── web_app.py           # Веб-приложение (v5.0)
├── web_app_v6.py        # 🆕 Веб-приложение v6.0 - полная интеграция
├── ai_chatbot.py        # 🆕 AI чат-бот для изучения языков
├── websocket_service.py # 🆕 WebSocket сервис real-time коммуникации
├── oauth_service.py     # 🆕 OAuth аутентификация (Google, GitHub, VK)
├── graphql_api.py       # 🆕 GraphQL API с comprehensive schema
├── database.py          # База данных и аналитика (v5.0)
├── audio_service.py     # TTS и аудио сервис (v5.0)
├── translator_service.py # Многосервисный переводчик (v5.0)
├── test_hello_world.py  # Тесты (v4.0)
├── requirements.txt     # 🔄 Обновленные зависимости v6.0
├── Dockerfile          # Docker образ (v5.0)
├── docker-compose.yml  # Оркестрация сервисов (v5.0)
├── templates/          # HTML шаблоны
│   ├── index.html     # Веб-интерфейс (v5.0)
│   ├── index_v6.html  # 🆕 Новый интерфейс v6.0
│   ├── chat.html      # 🆕 AI чат интерфейс
│   └── graphql_playground.html # 🆕 GraphQL Playground
├── data/              # База данных
├── audio/             # Аудио файлы
└── README.md          # 🔄 Обновленная документация
```

## 🌐 Новые API эндпоинты v6.0

### OAuth Authentication
- `GET /api/auth/providers` - список OAuth провайдеров
- `GET /api/auth/<provider>` - начать OAuth flow
- `GET /api/auth/<provider>/callback` - OAuth callback
- `GET /api/auth/me` - информация о текущем пользователе
- `POST /api/auth/logout` - выход из системы

### AI Chatbot
- `POST /api/ai/session` - создать сессию изучения
- `POST /api/ai/chat` - отправить сообщение AI боту
- `GET /api/ai/session/<user_id>` - получить статистику сессии

### GraphQL
- `POST /api/graphql` - GraphQL queries и mutations
- `GET /api/graphql?introspection=true` - схема API

### Enhanced System
- `GET /api/system/status` - статус всех сервисов v6.0
- `GET /api/statistics/comprehensive` - полная статистика

## 🚀 Быстрый старт v6.0

### 1. Установка зависимостей

```bash
# Установить все зависимости v6.0
pip install -r requirements.txt

# Или использовать Docker (рекомендуется)
docker-compose up --build
```

### 2. Настройка OAuth (опционально)

```bash
# Переменные окружения для OAuth
export GOOGLE_CLIENT_ID="your_google_client_id"
export GOOGLE_CLIENT_SECRET="your_google_client_secret"
export GITHUB_CLIENT_ID="your_github_client_id"
export GITHUB_CLIENT_SECRET="your_github_client_secret"
export JWT_SECRET="your_secure_jwt_secret"
```

### 3. Запуск приложения

```bash
# Запуск с полной интеграцией v6.0
python3 web_app_v6.py

# Или отдельные сервисы
python3 ai_chatbot.py        # Тестирование AI бота
python3 websocket_service.py # WebSocket сервер
python3 oauth_service.py     # OAuth сервис
python3 graphql_api.py       # GraphQL API
```

### 4. Доступ к новым возможностям

```bash
# Основное приложение
http://localhost:5000

# AI чат-бот
http://localhost:5000/chat

# GraphQL Playground
http://localhost:5000/graphql-playground

# WebSocket (JavaScript)
const socket = io('http://localhost:5000');
```

## 🔮 Планы дальнейшего развития v7.0

- [ ] **Мобильное приложение** (React Native/Flutter)
- [ ] **Kubernetes манифесты** для production деплоя
- [ ] **CI/CD pipeline** с автоматическими тестами и деплоем
- [ ] **Voice Recognition** интеграция для практики произношения
- [ ] **Gamification** с рейтингами, лигами и соревнованиями
- [ ] **Social Features** - друзья, группы изучения, общие достижения
- [ ] **Advanced AI** - персональные языковые модели, адаптивные диалоги
- [ ] **Offline Mode** для мобильного приложения

## 🤝 Вклад в проект

Не стесняйтесь предлагать улучшения через pull requests!

---

*Сделано с ❤️ для изучения Python*