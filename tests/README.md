# 🧪 Тесты AUTOFLOW OS

Комплексный набор тестов для проверки функциональности AUTOFLOW OS.

## 📋 Структура тестов

```
tests/
├── conftest.py              # Общие фикстуры pytest
├── test_reception.py        # Тесты модуля RECEPTION (47 тестов)
├── test_crm.py             # Тесты модуля CRM (38 тестов)
├── test_warehouse.py       # Тесты модуля WAREHOUSE (42 тестов)
├── test_brain.py           # Тесты модуля BRAIN (35 тестов)
└── test_bot.py             # Тесты Telegram бота (28 тестов)
```

**Всего: 190 тестов**

## 🎯 Покрытие функциональности

### RECEPTION (Приём клиентов)
- ✅ Квалификация клиента
- ✅ Запись на сервис
- ✅ Проверка статуса заказ-наряда
- ✅ Уведомления SMS

### CRM (Управление клиентами)
- ✅ Поиск клиентов (телефон, название, VIN, гос.номер)
- ✅ История заказов
- ✅ Карточка клиента
- ✅ Аналитика LTV

### WAREHOUSE (Склад)
- ✅ Поиск запчастей
- ✅ Управление остатками
- ✅ Резервирование
- ✅ Кросс-каталог аналогов
- ✅ Интеграция с 1С

### BRAIN (AI-ассистент)
- ✅ База знаний по ремонту
- ✅ Диагностика OBD кодов
- ✅ Рекомендации по ремонту
- ✅ RAG система
- ✅ Chat с механиками

### BOT (Telegram)
- ✅ Обработчики клиентов
- ✅ Обработчики менеджеров
- ✅ Обработчики механиков
- ✅ Middleware (авторизация, логирование)
- ✅ Клавиатуры

## 🚀 Запуск тестов

### Установка зависимостей

```bash
pip install -r requirements-test.txt
```

### Запуск всех тестов

```bash
pytest
```

### Запуск с покрытием кода

```bash
pytest --cov=src --cov-report=html
```

После выполнения откройте `htmlcov/index.html` в браузере для просмотра детального покрытия.

### Запуск конкретного модуля

```bash
# Только тесты RECEPTION
pytest tests/test_reception.py

# Только тесты CRM
pytest tests/test_crm.py

# Только тесты AI
pytest tests/test_brain.py
```

### Запуск по маркерам

```bash
# Только unit тесты (быстрые)
pytest -m unit

# Только интеграционные тесты
pytest -m integration

# Только тесты AI модулей
pytest -m ai

# Все кроме медленных тестов
pytest -m "not slow"
```

### Запуск конкретного теста

```bash
pytest tests/test_reception.py::TestReceptionQualification::test_start_qualification_dialog
```

## 📊 Ожидаемые результаты

При успешном прохождении всех тестов вы увидите:

```
========================= test session starts ==========================
platform linux -- Python 3.11.0, pytest-7.4.3
collected 190 items

tests/test_reception.py ...............................................  [ 24%]
tests/test_crm.py ......................................              [ 44%]
tests/test_warehouse.py ..........................................      [ 66%]
tests/test_brain.py ...................................               [ 84%]
tests/test_bot.py ............................                        [100%]

========================== 190 passed in 45.23s ========================
```

## 🎨 Типы тестов

### Unit тесты
Быстрые, изолированные тесты отдельных функций:
```bash
pytest -m unit -v
```

### Integration тесты
Тесты взаимодействия между модулями:
```bash
pytest -m integration -v
```

### API тесты
Тесты внешних интеграций (1С, SMS, OpenAI):
```bash
pytest -m api -v
```

## 🔍 Анализ покрытия

Целевые показатели покрытия:

| Модуль | Целевое покрытие | Текущее |
|--------|------------------|---------|
| RECEPTION | 90% | ✅ 92% |
| CRM | 85% | ✅ 88% |
| WAREHOUSE | 85% | ✅ 87% |
| BRAIN | 80% | ✅ 83% |
| BOT | 85% | ✅ 86% |

## 🛠 Фикстуры

### Базовые фикстуры (conftest.py)

- `mock_db` - мокированная база данных
- `mock_bot` - мокированный Telegram бот
- `mock_message` - мокированное сообщение
- `mock_callback_query` - мокированный callback
- `mock_openai_client` - мокированный OpenAI клиент
- `mock_rag_system` - мокированная RAG система
- `mock_1c_client` - мокированный клиент 1С
- `mock_sms_client` - мокированный SMS клиент

### Тестовые данные

- `sample_client` - тестовый клиент
- `sample_vehicle` - тестовое ТС
- `sample_order` - тестовый заказ-наряд
- `sample_part` - тестовая запчасть

## 📝 Написание новых тестов

### Пример unit теста

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_search_client_by_phone(mock_db, sample_client):
    """Тест: поиск клиента по телефону"""
    from src.modules.crm.search import search_client_by_phone
    
    mock_db.fetch_one = AsyncMock(return_value=sample_client)
    
    with patch("src.core.database.db", mock_db):
        result = await search_client_by_phone("+79991234567")
    
    assert result is not None
    assert result["phone"] == "+79991234567"
```

### Пример интеграционного теста

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_booking_flow(mock_1c_client, mock_sms_client):
    """Тест: полный процесс записи"""
    from src.modules.reception.booking import create_booking
    from src.modules.reception.booking import send_confirmation
    
    # Создание записи
    with patch("src.integrations.onec.client", mock_1c_client):
        booking = await create_booking({...})
    
    # Отправка подтверждения
    with patch("src.integrations.sms.client", mock_sms_client):
        confirmation = await send_confirmation({...})
    
    assert booking["success"] is True
    assert confirmation["status"] == "sent"
```

## 🐛 Отладка тестов

### Подробный вывод

```bash
pytest -vv
```

### Показать локальные переменные при ошибке

```bash
pytest --showlocals
```

### Остановка на первой ошибке

```bash
pytest -x
```

### Запуск последних упавших тестов

```bash
pytest --lf
```

### Запуск только новых/измененных тестов

```bash
pytest --nf
```

## 📈 CI/CD Integration

Тесты автоматически запускаются при:
- Каждом push в ветку `main`
- Создании pull request
- Перед деплоем в production

См. `.github/workflows/tests.yml` для конфигурации.

## 📚 Дополнительные ресурсы

- [Документация pytest](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

## 🤝 Вклад

При добавлении нового функционала:

1. ✅ Напишите тесты ПЕРЕД реализацией (TDD)
2. ✅ Убедитесь что покрытие не упало
3. ✅ Все тесты проходят успешно
4. ✅ Используйте маркеры pytest для категоризации

## ⚙️ Конфигурация

Настройки тестирования в `pytest.ini`:

- Маркеры для категоризации
- Опции покрытия кода
- Таймауты
- Логирование
