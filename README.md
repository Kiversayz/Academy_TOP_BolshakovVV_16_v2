# AcademyTop
## 🚀 Установка

```bash
pip install -r requirements.txt
```
Создайте `.env` из `.env_sample` и укажите настройки БД:
```bash
cp .env_sample .env
```

## 🛠 Запуск
Создание БД, миграции и суперпользователь:
```bash
make setup
```
Запуск сервера:
```bash
make runserver
```
## 📌 Команды

| Команда | Описание |
|--------|----------|
| `make setup` | Подготовка проекта |
| `make migrate` | Применить миграции |
| `make runserver` | Запустить сервер |
```