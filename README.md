# Дипломный проект "Python-разработчик: расширенный курс"
**Backend-приложение для автоматизации закупок**

Backend-приложение для автоматизации закупок — это сервис на Django Rest Framework (DRF), предназначенный для управления товарами, заказами и взаимодействия между клиентами и поставщиками через REST API.

## Основные функции
- ✅ Управление товарами и заказами
- ✅ REST API для интеграции с фронтендом и мобильными приложениями
- ✅ Админ-панель Django с улучшенным интерфейсом
- ✅ Асинхронные задачи (Celery) для отправки email и обработки импорта
- ✅ Документирование API (Swagger/Redoc)
- ✅ Мониторинг ошибок (Sentry)

## Запуск приложения (без Redis)

### Требования
- Docker и docker-compose
- Файл `.env` с настройками (пример ниже)

### 1. Настройка окружения
Создайте файл `.env` в корне проекта:
```init
# PostgreSQL
PG_DB=name BD
PG_USER=posgres
PG_PASSWORD=your_password

# Email (Gmail пример)
EMAIL_HOST=your.gmail.com
EMAIL_PORT=...
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

2. Запуск контейнеров
```
docker-compose -f docker-compose.yaml up -d --build
```
3. Создание суперпользователя
```
docker-compose exec app python manage.py createsuperuser
```

Доступные сервисы

- Сервис	URL
- REST API	http://localhost:8000/api/v1/
- Админка	http://localhost:8000/admin/
- Документация (Swagger)	http://localhost:8000/api/schema/swagger-ui/
- Мониторинг Celery	http://localhost:5555/


🛠️ Технологии

- Python 3.10+
- Django + DRF
- PostgreSQL
- Celery + Redis (асинхронные задачи)
- Docker (контейнеризация)
- Swagger/Redoc (документация API)


📧 Контакты
Автор: [Анастасия]
Email: [nesfox@mail.ru]

