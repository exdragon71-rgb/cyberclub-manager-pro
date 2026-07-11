# CyberClub Manager Pro

Продвинутая система управления для компьютерного клуба.

## Статус проекта

Проект находится в разработке.

На данный момент создан базовый backend на FastAPI.

## Планируемые возможности

- Учёт товаров
- Ревизия
- Долги сотрудников
- Лотерейные призы
- Смены
- Журнал действий
- Отчёты
- Роли пользователей
- PostgreSQL
- Интеграция с LightShell
- Экспорт в Google Sheets и Excel

## Стек

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### База данных

- PostgreSQL

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

### Инфраструктура

- Git
- GitHub
- Docker Compose

## Запуск backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Документация API

После запуска backend открой в браузере:

```text
http://127.0.0.1:8000/docs
```