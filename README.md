# Итоговый проект клон Твиттера

## Цель проекта:
При наличии фронтэнда, прописать бэкэнд приложения с рабочим функционалом.

## Технологии
Основные технологии использованные в проекте:
### FastAPI: 
FastAPI - это современный, быстрый веб-фреймворк для создания API на Python.
### PostgreSQL: 
PostgreSQL - мощная реляционная база данных с открытым исходным кодом.

### Nginx: 
Nginx - это высокопроизводительный веб-сервер и прокси-сервер

## Использование
Для работы понадобится файл .env в котором будут окружения которые нужно добавить перед запуском контейнеров.
```.env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=clone_tweeter_db
DB_USER=postgres
DB_PASS=postgres
SECRET_KEY=YourSecretKey

```
Запустите docker-compose:
```bash
docker compose up -d
```
Откройте браузер и перейдите по адресу http://localhost

## Структура проекта
1. main.py: Основной файл приложения, который содержит конфигурацию FastAPI и запускает сервер.
2. db/: Папка с файлами, отвечающими за взаимодействие с базой данных, а так же модели базы данных.
3. routes/: Папка с файлами, содержащими маршруты API.
4. schemas/: Папка с файлами, описывающими схемы ответа.
5. static/: Папка со статическими файлами, такими как изображения, CSS, JS и т.д.
6. tests/: Папка с модулями тестирования.

## Тестирование
Для тестирования проекта используется pytest
```bash
pip install pytest
```
Проведение тестов:
```bash
pytest tests/
```