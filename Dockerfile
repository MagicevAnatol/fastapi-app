# Используем базовый образ Python
FROM python:3.9-alpine
# Установка зависимостей
#RUN apk update && apk add --no-cache \
#    gcc \
#    libc-dev \
#    linux-headers \
#    musl-dev \
#    postgresql-dev

# Установка приложения и его зависимостей
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения внутрь контейнера
COPY . /app

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--reload"]