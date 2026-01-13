# API Reference

## Обзор

AUTOFLOW OS предоставляет REST API для интеграции с внешними системами.

**Base URL:** `https://api.autoflow.example.com/v1`

**Формат данных:** JSON

**Аутентификация:** Bearer Token (JWT)

---

## Аутентификация

### Получение токена

```http
POST /auth/token
Content-Type: application/json

{
  "username": "manager@company.com",
  "password": "your_password"
}
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Использование токена

```http
GET /clients
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Обновление токена

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

## Клиенты

### Список клиентов

```http
GET /clients
```

**Параметры запроса:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| page | int | Номер страницы (default: 1) |
| per_page | int | Записей на странице (default: 20, max: 100) |
| search | string | Поиск по имени, телефону, ИНН |
| client_type | string | Фильтр: individual / company |

**Ответ:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "ООО ТрансЛогистика",
      "client_type": "company",
      "phone": "+7 (495) 123-45-67",
      "email": "info@translog.ru",
      "inn": "7712345678",
      "balance": 125000.00,
      "created_at": "2019-03-15T10:30:00Z"
    }
  ],
  "meta": {
    "current_page": 1,
    "per_page": 20,
    "total": 156,
    "total_pages": 8
  }
}
```

---

### Получение клиента

```http
GET /clients/{id}
```

**Ответ:**
```json
{
  "id": 1,
  "name": "ООО ТрансЛогистика",
  "client_type": "company",
  "phone": "+7 (495) 123-45-67",
  "email": "info@translog.ru",
  "inn": "7712345678",
  "kpp": "771201001",
  "address": "г. Москва, ул. Промышленная, 15",
  "balance": 125000.00,
  "tags": ["vip", "постоянный"],
  "vehicles_count": 12,
  "orders_count": 47,
  "average_check": 85000.00,
  "last_visit": "2024-12-12T14:30:00Z",
  "created_at": "2019-03-15T10:30:00Z"
}
```

---

### Создание клиента

```http
POST /clients
Content-Type: application/json

{
  "name": "ИП Иванов И.И.",
  "client_type": "individual",
  "phone": "+7 (999) 888-77-66",
  "email": "ivanov@mail.ru"
}
```

**Ответ:** `201 Created`
```json
{
  "id": 157,
  "name": "ИП Иванов И.И.",
  "client_type": "individual",
  "phone": "+7 (999) 888-77-66",
  "email": "ivanov@mail.ru",
  "created_at": "2025-01-13T15:45:00Z"
}
```

---

### Обновление клиента

```http
PATCH /clients/{id}
Content-Type: application/json

{
  "phone": "+7 (999) 111-22-33",
  "tags": ["vip"]
}
```

**Ответ:** `200 OK`

---

### Автопарк клиента

```http
GET /clients/{id}/vehicles
```

**Ответ:**
```json
{
  "data": [
    {
      "id": 25,
      "brand": "MAN",
      "model": "TGX 18.440",
      "year": 2018,
      "vin": "WMA06XZZ5DW123456",
      "plate_number": "А123БВ777",
      "mileage": 560000
    }
  ]
}
```

---

### История заказов клиента

```http
GET /clients/{id}/orders
```

**Параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| status | string | Фильтр по статусу |
| from_date | date | Дата начала периода |
| to_date | date | Дата окончания периода |

---

## Заказы

### Список заказов

```http
GET /orders
```

**Параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| status | string | pending / in_progress / waiting_parts / ready / completed |
| client_id | int | ID клиента |
| vehicle_id | int | ID автомобиля |
| from_date | date | Дата начала |
| to_date | date | Дата окончания |

**Ответ:**
```json
{
  "data": [
    {
      "id": 1847,
      "order_number": "ZN-2025-1847",
      "client": {
        "id": 1,
        "name": "ООО ТрансЛогистика"
      },
      "vehicle": {
        "id": 25,
        "brand": "MAN",
        "model": "TGX 18.440",
        "plate_number": "А123БВ777"
      },
      "problem": "Двигатель троит, чёрный дым",
      "status": "in_progress",
      "scheduled_at": "2025-01-14T10:00:00Z",
      "total": 185000.00,
      "created_at": "2025-01-13T14:30:00Z"
    }
  ]
}
```

---

### Создание заказа

```http
POST /orders
Content-Type: application/json

{
  "client_id": 1,
  "vehicle_id": 25,
  "problem": "Диагностика топливной системы",
  "scheduled_at": "2025-01-15T10:00:00Z"
}
```

**Ответ:** `201 Created`
```json
{
  "id": 1848,
  "order_number": "ZN-2025-1848",
  "status": "pending",
  "created_at": "2025-01-13T16:00:00Z"
}
```

---

### Обновление статуса заказа

```http
PATCH /orders/{id}/status
Content-Type: application/json

{
  "status": "in_progress",
  "comment": "Начата диагностика"
}
```

---

## Запчасти

### Поиск запчастей

```http
GET /parts/search
```

**Параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| q | string | Поисковый запрос (артикул, название) |
| brand | string | Фильтр по бренду |
| in_stock | bool | Только в наличии |

**Пример:**
```http
GET /parts/search?q=51.05800-7684&in_stock=true
```

**Ответ:**
```json
{
  "data": [
    {
      "id": 4521,
      "article": "51.05800-7684",
      "name": "Турбокомпрессор MAN D2676",
      "brand": "MAN",
      "oem": "51.05800-7684",
      "price": 185000.00,
      "stock": {
        "warehouse_main": 2,
        "warehouse_reserve": 0,
        "in_transit": 1,
        "eta": "2025-01-20"
      },
      "analogs": [
        {
          "article": "53299887131",
          "brand": "BorgWarner",
          "price": 156000.00,
          "stock": 1
        }
      ]
    }
  ]
}
```

---

### Резервирование запчасти

```http
POST /parts/{id}/reserve
Content-Type: application/json

{
  "order_id": 1847,
  "quantity": 1
}
```

**Ответ:**
```json
{
  "reservation_id": 892,
  "part_id": 4521,
  "order_id": 1847,
  "quantity": 1,
  "expires_at": "2025-01-14T16:00:00Z"
}
```

---

### Отмена резерва

```http
DELETE /parts/reservations/{reservation_id}
```

---

## Диагностика (BRAIN)

### Анализ кода ошибки

```http
POST /brain/analyze
Content-Type: application/json

{
  "error_code": "P0087",
  "vehicle_brand": "MAN",
  "vehicle_model": "TGX"
}
```

**Ответ:**
```json
{
  "error_code": "P0087",
  "description": "Низкое давление в топливной рампе",
  "system": "Топливная система",
  "causes": [
    {
      "cause": "ТНВД (износ плунжерной пары)",
      "probability": 85,
      "related_parts": ["51.05800-7684"]
    },
    {
      "cause": "Регулятор давления топлива",
      "probability": 60
    },
    {
      "cause": "Топливный фильтр",
      "probability": 40
    }
  ],
  "recommendations": [
    "Проверить давление в рампе манометром (норма: 1600-1800 bar)",
    "Проверить производительность ТНВД на стенде"
  ],
  "similar_cases": 3,
  "confidence": 0.92
}
```

---

## Аналитика

### Дашборд

```http
GET /analytics/dashboard
```

**Параметры:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| period | string | today / week / month / year |
| branch_id | int | ID филиала (опционально) |

**Ответ:**
```json
{
  "period": "month",
  "orders": {
    "total": 156,
    "completed": 142,
    "in_progress": 14,
    "change": 12.5
  },
  "revenue": {
    "total": 4850000.00,
    "average_check": 31090.00,
    "change": 8.3
  },
  "clients": {
    "new": 23,
    "returning": 89,
    "nps": 8.2
  },
  "workload": {
    "posts_utilization": 78.5,
    "mechanics_utilization": 82.0
  }
}
```

---

## Коды ошибок

| Код | Описание |
|-----|----------|
| 400 | Bad Request — Некорректные параметры |
| 401 | Unauthorized — Требуется аутентификация |
| 403 | Forbidden — Недостаточно прав |
| 404 | Not Found — Ресурс не найден |
| 422 | Unprocessable Entity — Ошибка валидации |
| 429 | Too Many Requests — Превышен лимит запросов |
| 500 | Internal Server Error — Внутренняя ошибка |

**Формат ошибки:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Поле phone обязательно для заполнения",
    "details": {
      "field": "phone",
      "constraint": "required"
    }
  }
}
```

---

## Rate Limits

| Эндпоинт | Лимит |
|----------|-------|
| /auth/* | 10 запросов/минуту |
| /brain/* | 30 запросов/минуту |
| Остальные | 100 запросов/минуту |

При превышении возвращается `429 Too Many Requests` с заголовком:
```
Retry-After: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705158000
```

---

## Webhooks

### Настройка

```http
POST /webhooks
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["order.created", "order.status_changed"],
  "secret": "your_webhook_secret"
}
```

### События

| Событие | Описание |
|---------|----------|
| order.created | Создан новый заказ |
| order.status_changed | Изменён статус заказа |
| order.completed | Заказ завершён |
| client.created | Создан новый клиент |
| part.low_stock | Низкий остаток запчасти |

### Формат payload

```json
{
  "event": "order.status_changed",
  "timestamp": "2025-01-13T16:30:00Z",
  "data": {
    "order_id": 1847,
    "order_number": "ZN-2025-1847",
    "old_status": "pending",
    "new_status": "in_progress"
  }
}
```

### Проверка подписи

```
X-Webhook-Signature: sha256=abc123...
```

Подпись вычисляется как HMAC-SHA256 от тела запроса с использованием secret.
