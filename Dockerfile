# Многоэтапная сборка для оптимизации размера образа
FROM python:3.11-slim as builder

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Финальная стадия
FROM python:3.11-slim

# Создание пользователя для безопасности
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    espeak-ng \
    espeak-ng-data \
    && rm -rf /var/lib/apt/lists/*

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создание рабочей директории
WORKDIR /app

# Копирование исходного кода
COPY . .

# Создание директории для базы данных
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Переключение на непривилегированного пользователя
USER appuser

# Открытие порта для веб-приложения
EXPOSE 5000

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/statistics || exit 1

# Команда по умолчанию
CMD ["python", "web_app.py"]