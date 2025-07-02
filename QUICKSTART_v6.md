# 🚀 Hello World v6.0 - AI Edition | Быстрый старт

Добро пожаловать в Hello World v6.0 - AI Edition! Это руководство поможет вам быстро запустить все новые возможности.

## 🎯 Что нового в v6.0

- 🤖 **AI чат-бот** для изучения языков
- ⚡ **WebSocket** real-time коммуникация
- 🔐 **OAuth** аутентификация (Google, GitHub, VK)
- 📡 **GraphQL API** для гибких запросов
- 🎯 **Персонализированное** изучение языков

## ⚡ Быстрый запуск

### 1. Клонируйте репозиторий

```bash
git clone <repository_url>
cd hello-world-project
```

### 2. Установите зависимости

```bash
# Python зависимости
pip install -r requirements.txt

# Или создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. Запустите приложение

```bash
# Запуск с полной интеграцией v6.0
python3 web_app_v6.py
```

### 4. Откройте браузер

- **Главная страница**: http://localhost:5000
- **AI чат**: http://localhost:5000/chat
- **GraphQL Playground**: http://localhost:5000/api/graphql

## 🔧 Настройка сервисов

### OAuth аутентификация (опционально)

```bash
# Переменные окружения
export GOOGLE_CLIENT_ID="your_google_client_id"
export GOOGLE_CLIENT_SECRET="your_google_client_secret"
export GITHUB_CLIENT_ID="your_github_client_id"
export GITHUB_CLIENT_SECRET="your_github_client_secret"
export JWT_SECRET="your_secure_jwt_secret"
```

### OpenAI API (опционально)

```bash
# Для улучшенного AI опыта
export OPENAI_API_KEY="your_openai_api_key"
```

## 🧪 Тестирование компонентов

### 1. AI чат-бот

```bash
python3 ai_chatbot.py

# Вывод:
# 🤖 Тестирование AI чат-бота...
# ✅ Создана сессия изучения русского языка
# 💬 Тестовый диалог...
```

### 2. WebSocket сервис

```bash
python3 websocket_service.py

# Подключение: ws://localhost:8765
```

### 3. OAuth сервис

```bash
python3 oauth_service.py

# Тестирование OAuth конфигурации
```

### 4. GraphQL API

```bash
python3 graphql_api.py

# Тестирование GraphQL запросов
```

## 🌐 Использование новых API

### AI чат-бот API

```javascript
// Создать сессию изучения
const response = await fetch('/api/ai/session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user123',
    target_language: 'ru',
    level: 'beginner'
  })
});

// Отправить сообщение AI
const chatResponse = await fetch('/api/ai/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user123',
    message: 'Привет!'
  })
});
```

### WebSocket real-time чат

```javascript
const socket = io('http://localhost:5000');

// Присоединиться к AI чату
socket.emit('join_ai_chat', {
  user_id: 'user123',
  target_language: 'ru',
  level: 'beginner'
});

// Отправить сообщение AI
socket.emit('ai_message', {
  user_id: 'user123',
  message: 'Как дела?'
});

// Получить ответ AI
socket.on('ai_response', (data) => {
  console.log('AI ответ:', data.bot_response);
  console.log('Предложения:', data.suggestions);
  console.log('Прогресс:', data.progress_score);
});
```

### GraphQL запросы

```javascript
// Простой GraphQL запрос
const query = `
  query {
    languages {
      code
      name
      greeting
      difficulty
    }
    statistics {
      totalUsers
      aiConversations
    }
  }
`;

const response = await fetch('/api/graphql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query })
});
```

### OAuth аутентификация

```javascript
// Получить список провайдеров
const providers = await fetch('/api/auth/providers').then(r => r.json());

// Начать OAuth flow
window.location.href = '/api/auth/google';

// После успешной авторизации получить информацию о пользователе
const user = await fetch('/api/auth/me', {
  headers: { 'Authorization': `Bearer ${jwt_token}` }
}).then(r => r.json());
```

## 📊 Мониторинг и статистика

### Статус системы

```bash
curl http://localhost:5000/api/system/status
```

### Комплексная статистика

```bash
curl http://localhost:5000/api/statistics/comprehensive
```

## 🔨 Разработка

### Структура файлов v6.0

```
.
├── ai_chatbot.py        # 🤖 AI чат-бот
├── websocket_service.py # ⚡ WebSocket сервис
├── oauth_service.py     # 🔐 OAuth аутентификация
├── graphql_api.py       # 📡 GraphQL API
├── web_app_v6.py       # 🌐 Интегрированное веб-приложение
└── requirements.txt     # 📦 Обновленные зависимости
```

### Добавление новых языков

```python
# В hello_world.py добавьте новый язык
greetings = {
    # ... существующие языки
    'new_lang': 'New Language Greeting'
}
```

### Расширение AI бота

```python
# В ai_chatbot.py добавьте новые уроки
language_lessons = {
    'new_lang': {
        'greetings': ['Hello!', 'Hi!'],
        'basics': ['How are you?', 'My name is...'],
        'phrases': ['Thank you', 'Please', 'Excuse me']
    }
}
```

## 🐛 Устранение неполадок

### AI чат-бот не отвечает

```bash
# Проверьте доступность сервиса
python3 -c "from ai_chatbot import language_bot; print('AI bot available:', bool(language_bot))"
```

### WebSocket не подключается

```bash
# Проверьте порт 8765
netstat -an | grep 8765

# Или запустите отдельно
python3 websocket_service.py
```

### OAuth ошибки

```bash
# Проверьте переменные окружения
echo $GOOGLE_CLIENT_ID
echo $GITHUB_CLIENT_ID

# Проверьте настройки OAuth приложений в консолях разработчика
```

### GraphQL ошибки

```bash
# Проверьте установку graphene
pip install graphene

# Тест GraphQL сервиса
python3 graphql_api.py
```

## 🚀 Полезные команды

### Запуск всех сервисов отдельно

```bash
# Терминал 1: AI чат-бот
python3 ai_chatbot.py

# Терминал 2: WebSocket
python3 websocket_service.py

# Терминал 3: OAuth сервис
python3 oauth_service.py

# Терминал 4: GraphQL API
python3 graphql_api.py

# Терминал 5: Веб-приложение
python3 web_app_v6.py
```

### Тестирование API

```bash
# Проверить все языки
curl http://localhost:5000/api/languages

# AI чат-бот сессия
curl -X POST http://localhost:5000/api/ai/session \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","target_language":"ru"}'

# GraphQL запрос
curl -X POST http://localhost:5000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { greeting(language: \"ru\") }"}'
```

## 🎉 Поздравляем!

Теперь у вас запущен Hello World v6.0 - AI Edition со всеми новыми возможностями:

- ✅ AI чат-бот для изучения языков
- ✅ Real-time WebSocket коммуникация
- ✅ OAuth аутентификация
- ✅ GraphQL API
- ✅ Персонализированное обучение

Изучайте языки с помощью AI, подключайтесь через OAuth, используйте flexible GraphQL запросы и наслаждайтесь real-time интерфейсом!

## 📚 Дополнительные ресурсы

- **Полная документация**: README.md
- **API документация**: http://localhost:5000/api/graphql (GraphQL Playground)
- **Исходный код**: Все файлы с комментариями
- **Примеры использования**: В каждом файле есть секция `if __name__ == '__main__'`

Удачного изучения языков! 🌍🤖✨