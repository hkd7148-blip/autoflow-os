"""
Тесты для Telegram bot handlers
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


class TestClientHandlers:
    """Тесты обработчиков для клиентов"""
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_bot, mock_message):
        """Тест: команда /start"""
        from src.bot.handlers.client import handle_start
        
        await handle_start(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Добро пожаловать" in call_args or "AUTOFLOW" in call_args
    
    @pytest.mark.asyncio
    async def test_book_service_command(self, mock_bot, mock_message):
        """Тест: начало процесса записи"""
        from src.bot.handlers.client import handle_booking_start
        
        await handle_booking_start(mock_message)
        
        mock_message.answer.assert_called_once()
        # Проверяем что началась квалификация
        call_args = mock_message.answer.call_args
        assert call_args is not None
    
    @pytest.mark.asyncio
    async def test_check_status_command(self, mock_bot, mock_message, mock_1c_client):
        """Тест: проверка статуса заказ-наряда"""
        from src.bot.handlers.client import handle_check_status
        
        mock_message.text = "ORD-12345"
        mock_1c_client.get_order = AsyncMock(return_value={
            "order_id": "ORD-12345",
            "status": "in_progress",
            "description": "Замена масла"
        })
        
        with patch("src.integrations.onec.client", mock_1c_client):
            await handle_check_status(mock_message)
        
        mock_message.answer.assert_called_once()
        response = mock_message.answer.call_args[0][0]
        assert "ORD-12345" in response or "progress" in response.lower()
    
    @pytest.mark.asyncio
    async def test_callback_booking_confirm(self, mock_bot, mock_callback_query, mock_1c_client):
        """Тест: подтверждение записи через callback"""
        from src.bot.handlers.client import handle_booking_confirm
        
        mock_callback_query.data = "confirm_booking:2025-01-20:10:00"
        mock_1c_client.create_order = AsyncMock(return_value={"order_id": "ORD-999"})
        
        with patch("src.integrations.onec.client", mock_1c_client):
            await handle_booking_confirm(mock_callback_query)
        
        mock_callback_query.answer.assert_called_once()
        mock_callback_query.message.answer.assert_called()


class TestManagerHandlers:
    """Тесты обработчиков для менеджеров"""
    
    @pytest.mark.asyncio
    async def test_search_client_command(self, mock_bot, mock_message, mock_db):
        """Тест: поиск клиента менеджером"""
        from src.bot.handlers.manager import handle_search_client
        
        mock_message.text = "+79991234567"
        mock_db.fetch_one = AsyncMock(return_value={
            "id": 1,
            "name": "ООО ТрансЛогистик",
            "phone": "+79991234567"
        })
        
        with patch("src.core.database.db", mock_db):
            await handle_search_client(mock_message)
        
        mock_message.answer.assert_called_once()
        response = mock_message.answer.call_args[0][0]
        assert "ТрансЛогистик" in response
    
    @pytest.mark.asyncio
    async def test_get_client_history(self, mock_bot, mock_callback_query, mock_db):
        """Тест: запрос истории клиента"""
        from src.bot.handlers.manager import handle_client_history
        
        mock_callback_query.data = "client_history:1"
        mock_db.fetch_all = AsyncMock(return_value=[
            {"id": 1, "status": "completed", "total_amount": 15000},
            {"id": 2, "status": "in_progress", "total_amount": 20000}
        ])
        
        with patch("src.core.database.db", mock_db):
            await handle_client_history(mock_callback_query)
        
        mock_callback_query.message.answer.assert_called()


class TestMechanicHandlers:
    """Тесты обработчиков для механиков"""
    
    @pytest.mark.asyncio
    async def test_search_part_command(self, mock_bot, mock_message, mock_db):
        """Тест: поиск запчасти механиком"""
        from src.bot.handlers.mechanic import handle_search_part
        
        mock_message.text = "11427953129"
        mock_db.fetch_one = AsyncMock(return_value={
            "article": "11427953129",
            "name": "Масляный фильтр",
            "quantity": 25,
            "price": 850
        })
        
        with patch("src.core.database.db", mock_db):
            await handle_search_part(mock_message)
        
        mock_message.answer.assert_called_once()
        response = mock_message.answer.call_args[0][0]
        assert "11427953129" in response
        assert "фильтр" in response.lower()
    
    @pytest.mark.asyncio
    async def test_ask_brain_question(self, mock_bot, mock_message, mock_openai_client, mock_rag_system):
        """Тест: вопрос к AI-ассистенту"""
        from src.bot.handlers.mechanic import handle_brain_question
        
        mock_message.text = "Как проверить турбину VOLVO?"
        mock_rag_system.search = AsyncMock(return_value=[
            {"text": "Проверка турбины: визуальный осмотр люфта", "score": 0.91}
        ])
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            with patch("src.modules.brain.rag_system", mock_rag_system):
                await handle_brain_question(mock_message)
        
        mock_message.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_part_availability(self, mock_bot, mock_callback_query, mock_db):
        """Тест: проверка наличия запчасти"""
        from src.bot.handlers.mechanic import handle_check_availability
        
        mock_callback_query.data = "check_part:11427953129"
        mock_db.fetch_one = AsyncMock(return_value={"quantity": 25, "warehouse": "Основной"})
        
        with patch("src.core.database.db", mock_db):
            await handle_check_availability(mock_callback_query)
        
        mock_callback_query.answer.assert_called()
        mock_callback_query.message.answer.assert_called()


class TestAdminHandlers:
    """Тесты обработчиков для администратора"""
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, mock_bot, mock_message, mock_db):
        """Тест: получение статистики"""
        from src.bot.handlers.admin import handle_statistics
        
        mock_db.fetch_one = AsyncMock(side_effect=[
            {"total_orders": 150},
            {"revenue": 2500000},
            {"active_clients": 85}
        ])
        
        with patch("src.core.database.db", mock_db):
            await handle_statistics(mock_message)
        
        mock_message.answer.assert_called_once()
        response = mock_message.answer.call_args[0][0]
        assert "150" in response or "orders" in response.lower()
    
    @pytest.mark.asyncio
    async def test_export_report(self, mock_bot, mock_callback_query, mock_db):
        """Тест: экспорт отчёта"""
        from src.bot.handlers.admin import handle_export_report
        
        mock_callback_query.data = "export:monthly:2025-01"
        mock_db.fetch_all = AsyncMock(return_value=[
            {"date": "2025-01-10", "revenue": 85000},
            {"date": "2025-01-11", "revenue": 92000}
        ])
        
        with patch("src.core.database.db", mock_db):
            await handle_export_report(mock_callback_query)
        
        mock_callback_query.message.answer.assert_called()


class TestMiddlewares:
    """Тесты middleware"""
    
    @pytest.mark.asyncio
    async def test_auth_middleware_authorized(self, mock_message, mock_db):
        """Тест: авторизованный пользователь"""
        from src.bot.middlewares.auth import AuthMiddleware
        
        mock_db.fetch_one = AsyncMock(return_value={
            "telegram_id": 123456789,
            "role": "client",
            "is_active": True
        })
        
        middleware = AuthMiddleware()
        handler = AsyncMock()
        
        with patch("src.core.database.db", mock_db):
            await middleware(handler, mock_message, {})
        
        handler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_auth_middleware_unauthorized(self, mock_message, mock_db):
        """Тест: неавторизованный пользователь"""
        from src.bot.middlewares.auth import AuthMiddleware
        
        mock_db.fetch_one = AsyncMock(return_value=None)
        
        middleware = AuthMiddleware()
        handler = AsyncMock()
        
        with patch("src.core.database.db", mock_db):
            await middleware(handler, mock_message, {})
        
        # Handler не должен вызваться для неавторизованного пользователя
        handler.assert_not_called()
        mock_message.answer.assert_called()
    
    @pytest.mark.asyncio
    async def test_logging_middleware(self, mock_message):
        """Тест: логирование запросов"""
        from src.bot.middlewares.logging import LoggingMiddleware
        
        middleware = LoggingMiddleware()
        handler = AsyncMock()
        
        await middleware(handler, mock_message, {})
        
        handler.assert_called_once()


class TestKeyboards:
    """Тесты клавиатур"""
    
    def test_main_menu_keyboard(self):
        """Тест: главное меню"""
        from src.bot.keyboards import get_main_menu
        
        keyboard = get_main_menu(role="client")
        
        assert keyboard is not None
        assert hasattr(keyboard, "inline_keyboard")
        assert len(keyboard.inline_keyboard) > 0
    
    def test_booking_slots_keyboard(self):
        """Тест: клавиатура выбора времени"""
        from src.bot.keyboards import get_booking_slots_keyboard
        
        slots = [
            {"time": "10:00", "available": True},
            {"time": "12:00", "available": True},
            {"time": "14:00", "available": False}
        ]
        
        keyboard = get_booking_slots_keyboard(slots, date="2025-01-20")
        
        assert keyboard is not None
        # Должны быть только доступные слоты
        assert len(keyboard.inline_keyboard) >= 2


class TestBotIntegration:
    """Интеграционные тесты бота"""
    
    @pytest.mark.asyncio
    async def test_full_booking_flow_via_bot(
        self, mock_bot, mock_message, mock_callback_query, mock_1c_client, mock_sms_client
    ):
        """Тест: полный флоу записи через бота"""
        from src.bot.handlers.client import handle_booking_start, handle_booking_confirm
        
        # Шаг 1: Начало записи
        await handle_booking_start(mock_message)
        assert mock_message.answer.called
        
        # Шаг 2: Подтверждение записи
        mock_callback_query.data = "confirm_booking:2025-01-20:10:00"
        mock_1c_client.create_order = AsyncMock(return_value={
            "order_id": "ORD-12345",
            "status": "created"
        })
        
        with patch("src.integrations.onec.client", mock_1c_client):
            with patch("src.integrations.sms.client", mock_sms_client):
                await handle_booking_confirm(mock_callback_query)
        
        # Проверяем что SMS отправлен
        mock_sms_client.send_sms.assert_called()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_handlers(self, mock_bot, mock_message, mock_db):
        """Тест: обработка ошибок в хендлерах"""
        from src.bot.handlers.manager import handle_search_client
        
        mock_db.fetch_one = AsyncMock(side_effect=Exception("Database connection error"))
        
        with patch("src.core.database.db", mock_db):
            await handle_search_client(mock_message)
        
        # Должно быть сообщение об ошибке пользователю
        mock_message.answer.assert_called()
        response = mock_message.answer.call_args[0][0]
        assert "ошибк" in response.lower() or "error" in response.lower()
