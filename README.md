## ✅ Как будет работать:

1. Запускаешь:

```bash
python init_db.py
```

2. Если **SQL Server доступен** → `.env` -> n обновляется: `USE_SQLITE=false` / y обновляется: `USE_SQLITE=true`, и используется `db.sqlite3`.
3. Затем:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## ✅ Обновлённый `README.md` (без `setup.bat` и `setup.ps1`)

```markdown
# AcademyTop

Это Django-проект для [описание проекта, если есть, или просто "учебного проекта"].

---

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <ваш_репозиторий>
cd <папка_проекта>
```

### 2. Установка виртуального окружения и зависимостей

Создайте и активируйте виртуальное окружение:

#### Windows:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

#### Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте копию файла `.env_sample` и переименуйте его в `.env`.  
Заполните переменные в `.env` в соответствии с вашей инфраструктурой (SQL Server или SQLite).

```bash
copy .env_sample .env  # Windows
# или
cp .env_sample .env   # Linux/Mac
```

> ⚠️ **Важно**: Если вы хотите использовать **SQL Server**, убедитесь, что:
> - Сервер доступен и запущен.
> - Пользователь имеет права на создание базы данных.
> - Порт 1433 открыт (или указан другой, если используется Named Instance).
> 
> Если **SQL Server недоступен**, `init_db.py` автоматически переключится на **SQLite**, и обновит `.env`.

---

## 🛠 Установка и запуск

### Запуск инициализации базы данных

Выполните команду, которая:
- Проверит и создаст базу данных (SQL Server или SQLite),
- Автоматически обновит `.env`.

```bash
python init_db.py
```

### Применение миграций

```bash
python manage.py migrate
```

### Создание суперпользователя

```bash
python manage.py createsuperuser
```

### Запуск сервера

```bash
python manage.py runserver
```

---

## 📁 Структура проекта

- `core/` — основной модуль проекта.
- `user/` — расширение модели пользователя (`UserProfile`).
- `init_db.py` — скрипт для проверки и создания БД (SQL Server или SQLite).
- `.env_sample` — пример переменных окружения.
- `requirements.txt` — зависимости.


## 📝 Примечания

- Модель пользователя расширена через `UserProfile`, связанную с `django.contrib.auth.models.User`.
- Используется JWT-аутентификация.
- Проект готов к запуску с минимальными действиями.
- Поддержка автоматического переключения на SQLite при ошибке подключения к SQL Server.