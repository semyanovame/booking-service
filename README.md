```markdown
# Booking Service — бронирование переговорных комнат

REST API и веб-интерфейс для коворкинга. JWT, роли admin/user, PostgreSQL, Docker

## Запуск

```bash
git clone https://github.com/semyanovame/booking-service.git
cd booking-service
docker-compose up -d
```

Открыть: http://localhost:8000

## Пользователи

| Логин | Пароль | Роль |
|-------|--------|------|
| admin | admin123 | Администратор |
| user | user123 | Сотрудник |

## Возможности

- Вход по JWT, регистрация
- Просмотр комнат и слотов на любую дату
- Бронирование и отмена
- Нельзя забронировать занятое или прошлое
- Видно, кто занял слот
- Админ: все брони, статистика, добавление и удаление комнат

## API

| Метод | URL | Доступ |
|-------|-----|--------|
| POST | /api/login | Все |
| POST | /api/auth/register | Все |
| GET | /api/rooms-ui | Все |
| POST | /api/book | Все |
| DELETE | /api/book/{id} | Владелец / админ |
| GET | /api/my | Все |
| GET | /api/bookings/all | Админ |
| POST | /api/add-room | Админ |
| DELETE | /api/room/{id} | Админ |
| GET | /api/stats | Админ |

## Технологии

Python 3.11 · FastAPI · PostgreSQL 15 · SQLAlchemy · JWT · bcrypt · Poetry · Docker

## Тесты

```bash
docker-compose exec app poetry run pytest
```

16 тестов: auth, rooms, bookings, permissions

## Структура

```
app/
├── main.py
├── config.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── dependencies.py
└── routers/
tests/
Dockerfile
docker-compose.yml
pyproject.toml
```
```