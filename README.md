# Auth System

## О проекте

Это backend-приложение на `FastAPI`, в котором я реализовал собственную систему аутентификации и авторизации.

Основная цель проекта — показать работу:
- регистрации и входа пользователя;
- серверных сессий;
- мягкого удаления аккаунта;
- ролевой модели доступа;
- API для управления ролями и правами;
- защищенных ресурсов с корректными ответами `401` и `403`.

---

## Что реализовано

### Аутентификация
- регистрация пользователя;
- login по `email` и `password`;
- logout;
- хранение активных сессий в БД;
- идентификация пользователя по токену в заголовке `Authorization: Bearer <token>`

### Работа с текущим пользователем
- получение информации о себе;
- обновление данных профиля;
- мягкое удаление аккаунта;
- автоматическая деактивация сессий после удаления.

### Авторизация
- доступ к endpoint-ам проверяется через роли и права;
- если пользователь не определен, возвращается `401 Unauthorized`;
- если пользователь определен, но у него нет нужного права, возвращается `403 Forbidden`.

### Управление доступом
- просмотр списка ролей;
- просмотр списка прав;
- назначение роли пользователю;
- назначение прав для роли.

### Mock resources
Для демонстрации системы доступа добавлены защищенные mock endpoints:
- `/resources/documents`
- `/resources/reports`
- `/resources/admin-panel`

---

## Как устроена модель доступа

В проекте используется `RBAC` (`Role-Based Access Control`).

Логика такая:
- у пользователя может быть одна или несколько ролей;
- у каждой роли есть набор прав;
- право описывается парой:
  - `resource`
  - `action`

Примеры:
- `documents:read`
- `reports:read`
- `roles:manage`
- `permissions:manage`

Когда пользователь обращается к защищенному endpoint-у:
1. система определяет его по токену сессии;
2. получает его роли;
3. получает права этих ролей;
4. проверяет, есть ли нужные права;
5. если прав нет, возвращается `403 Forbidden`.

---

## Структура базы данных

### `users`
Таблица пользователей.

Основные поля:
- `email`
- `password_hash`
- `last_name`
- `first_name`
- `middle_name`
- `status`
- `created_at`
- `updated_at`
- `deleted_at`

Для мягкого удаления используется поле `status`, а также `deleted_at`.

### `roles`
Таблица ролей.

В проекте используются роли:
- `admin`
- `user`

### `permissions`
Таблица прав.

Каждое permission задается парой:
- `resource`
- `action`

### `user_roles`
Связующая таблица между пользователями и ролями.

### `role_permissions`
Связующая таблица между ролями и правами.

### `sessions`
Таблица активных сессий пользователей.

Хранит:
- `user_id`
- `token`
- `is_active`
- `expires_at`
- `created_at`

---

## Тестовые данные

После запуска seed.py в базе появляются:

### Роли
- `admin`
- `user`

### Права
- `users:read`
- `users:update`
- `documents:read`
- `reports:read`
- `roles:manage`
- `permissions:manage`

### Назначения
- роль `admin` получает все права;
- роль `user` получает:
  - `users:update`
  - `documents:read`

### Тестовые пользователи
- `admin@example.com / admin123`
- `user@example.com / user1234`

---

## Структура проекта

```text
app/
├── api/
│   ├── admin.py
│   ├── auth.py
│   ├── deps.py
│   ├── resources.py
│   └── users.py
├── core/
│   ├── config.py
│   ├── database.py
│   └── security.py
├── db/
│   └── seed.py
├── models/
│   ├── permission.py
│   ├── role.py
│   ├── session.py
│   └── user.py
├── schemas/
│   ├── auth.py
│   ├── permission.py
│   ├── role.py
│   └── user.py
└── main.py
```


### Как запустить проект

#### 1. Клонировать репозиторий

```bash
git clone https://github.com/egor-git-dev/auth_system
cd auth_system
```

---

#### 2. Создать и активировать виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # Linux / MacOS
venv\Scripts\activate   # Windows
```

---

#### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

---

#### 4. Создать файл `.env`

Пример:

```env
APP_NAME=Auth System
DEBUG=true
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/auth_system
SECRET_KEY=change_me_to_random_secret
SESSION_EXPIRE_MINUTES=60
```
Пример также есть в файле `.env.example` в корне проекта.

---

#### 5. Создать базу данных

```bash
psql -U postgres -h localhost -c "CREATE DATABASE auth_system;"
```

---

#### 6. Применить миграции

```bash
alembic upgrade head
```

---

#### 7. Заполнить базу тестовыми данными

```bash
python -m app.db.seed
```

---

#### 8. Запустить сервер

```bash
uvicorn app.main:app --reload
```

---

#### 9. Открыть Swagger UI

```
http://127.0.0.1:8000/docs
```

---

## Основные endpoint-ы

### Auth

```http
POST /auth/register
POST /auth/login
POST /auth/logout
```

---

### Users

```http
GET    /users/me
PATCH  /users/me
DELETE /users/me
```

---

### Admin

```http
GET  /admin/roles
GET  /admin/permissions
POST /admin/users/{user_id}/roles
POST /admin/roles/{role_id}/permissions
```

---

### Resources

```http
GET /resources/documents
GET /resources/reports
GET /resources/admin-panel
```
