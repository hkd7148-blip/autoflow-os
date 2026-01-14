"""
Конфигурация pytest для тестирования AUTOFLOW OS
"""
import pytest
import asyncio
from datetime import datetime
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

# ============= Фикстуры для базы данных =============

@pytest.fixture
def mock_db():
    """Мокированная база данных"""
    db = MagicMock()
    db.execute = AsyncMock()
    db.fetch_one = AsyncMock()
    db.fetch_all = AsyncMock()
    db.commit = AsyncMock()
    return db

@pytest.fixture
def sample_client():
    """Тестовый клиент"""
    return {
        "id": 1,
        "telegram_id": 123456789,
        "name": "ООО ТрансЛогистик",
        "phone": "+79991234567",
        "email": "info@translogistic.ru",
        "created_at": datetime(2025, 1, 1, 10, 0, 0)
    }

@pytest.fixture
def sample_vehicle():
    """Тестовое транспортное средство"""
    return {
        "id": 1,
        "client_id": 1,
        "brand": "VOLVO",
        "model": "FH16",
        "year": 2020,
        "vin": "YV2A22B60MA123456",
        "license_plate": "А123БВ777",
        "mileage": 150000
    }

@pytest.fixture
def sample_order():
    """Тестовый заказ-наряд"""
    return {
        "id": 1,
        "client_id": 1,
        "vehicle_id": 1,
        "status": "in_progress",
        "description": "Замена масла и фильтров",
        "created_at": datetime(2025, 1, 10, 9, 0, 0),
        "scheduled_at": datetime(2025, 1, 15, 10, 0, 0),
        "total_amount": 15000.00
    }

@pytest.fixture
def sample_part():
    """Тестовая запчасть"""
    return {
        "id": 1,
        "article": "11427953129",
        "name": "Масляный фильтр",
        "brand": "MANN",
        "quantity": 25,
        "price": 850.00,
        "warehouse": "Основной склад"
    }

# ============= Фикстуры для Telegram бота =============

@pytest.fixture
def mock_bot():
    """Мокированный Telegram бот"""
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    bot.answer_callback_query = AsyncMock()
    bot.edit_message_text = AsyncMock()
    return bot

@pytest.fixture
def mock_message():
    """Мокированное сообщение Telegram"""
    message = MagicMock()
    message.from_user.id = 123456789
    message.from_user.username = "test_user"
    message.text = "/start"
    message.chat.id = 123456789
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message

@pytest.fixture
def mock_callback_query():
    """Мокированный callback query"""
    callback = MagicMock()
    callback.from_user.id = 123456789
    callback.data = "test_callback"
    callback.message = MagicMock()
    callback.message.chat.id = 123456789
    callback.answer = AsyncMock()
    return callback

# ============= Фикстуры для AI модулей =============

@pytest.fixture
def mock_openai_client():
    """Мокированный OpenAI клиент"""
    client = AsyncMock()
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "Тестовый ответ AI"
    client.chat.completions.create = AsyncMock(return_value=response)
    return client

@pytest.fixture
def mock_rag_system():
    """Мокированная RAG система"""
    rag = MagicMock()
    rag.search = AsyncMock(return_value=[
        {"text": "Замена масла VOLVO FH16: каждые 40 000 км", "score": 0.95},
        {"text": "Рекомендуемое масло: 15W-40", "score": 0.87}
    ])
    return rag

# ============= Фикстуры для интеграций =============

@pytest.fixture
def mock_1c_client():
    """Мокированный клиент 1С"""
    client = AsyncMock()
    client.get_client = AsyncMock(return_value={"id": 1, "name": "Тест Клиент"})
    client.create_order = AsyncMock(return_value={"order_id": "ORD-001"})
    client.get_part_availability = AsyncMock(return_value={"available": True, "quantity": 10})
    return client

@pytest.fixture
def mock_sms_client():
    """Мокированный SMS клиент"""
    client = AsyncMock()
    client.send_sms = AsyncMock(return_value={"status": "sent", "message_id": "12345"})
    return client

# ============= Event loop для async тестов =============

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создаёт event loop для async тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# ============= Переменные окружения =============

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Устанавливает переменные окружения для тестов"""
    monkeypatch.setenv("BOT_TOKEN", "test_token_123")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test_db")
    monkeypatch.setenv("ONEC_API_URL", "http://localhost:8080/api")
    monkeypatch.setenv("ONEC_API_USER", "test_user")
    monkeypatch.setenv("ONEC_API_PASSWORD", "test_password")
