# Используем базовый образ Python
FROM python:3.9

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем исходный код приложения внутрь контейнера
COPY . .

# Команда для запуска приложения
CMD ["python", "main.py"]