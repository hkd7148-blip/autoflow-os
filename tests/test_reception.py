"""
Тесты для модуля RECEPTION - приём и квалификация клиентов
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock


class TestReceptionQualification:
    """Тесты квалификации клиента"""
    
    @pytest.mark.asyncio
    async def test_start_qualification_dialog(self, mock_bot, mock_message):
        """Тест: начало диалога квалификации"""
        from src.modules.reception.qualification import start_qualification
        
        result = await start_qualification(mock_message.from_user.id)
        
        assert result["status"] == "started"
        assert result["step"] == "vehicle_type"
        assert "questions" in result
    
    @pytest.mark.asyncio
    async def test_collect_vehicle_info(self, mock_db, sample_vehicle):
        """Тест: сбор информации о транспортном средстве"""
        from src.modules.reception.qualification import collect_vehicle_info
        
        vehicle_data = {
            "brand": "VOLVO",
            "model": "FH16",
            "year": 2020,
            "license_plate": "А123БВ777"
        }
        
        result = await collect_vehicle_info(vehicle_data)
        
        assert result["valid"] is True
        assert result["vehicle_type"] == "truck"
        assert result["brand"] == "VOLVO"
    
    @pytest.mark.asyncio
    async def test_invalid_license_plate(self):
        """Тест: невалидный гос. номер"""
        from src.modules.reception.qualification import validate_license_plate
        
        invalid_plates = ["12345", "АБВГД", "A000AA000"]
        
        for plate in invalid_plates:
            result = validate_license_plate(plate)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_problem_categorization(self):
        """Тест: категоризация проблемы"""
        from src.modules.reception.qualification import categorize_problem
        
        test_cases = [
            ("Не заводится двигатель", "critical"),
            ("Замена масла", "routine"),
            ("Странный звук при торможении", "diagnostic")
        ]
        
        for description, expected_category in test_cases:
            result = await categorize_problem(description)
            assert result["category"] == expected_category
            assert result["urgency"] in ["low", "medium", "high", "critical"]


class TestReceptionBooking:
    """Тесты записи на сервис"""
    
    @pytest.mark.asyncio
    async def test_get_available_slots(self, mock_1c_client):
        """Тест: получение доступных слотов"""
        from src.modules.reception.booking import get_available_slots
        
        date = datetime.now().date()
        mock_1c_client.get_schedule = AsyncMock(return_value={
            "slots": [
                {"time": "10:00", "available": True},
                {"time": "12:00", "available": True},
                {"time": "14:00", "available": False}
            ]
        })
        
        with patch("src.integrations.onec.client", mock_1c_client):
            slots = await get_available_slots(date)
        
        assert len(slots) == 2  # только доступные
        assert all(slot["available"] for slot in slots)
    
    @pytest.mark.asyncio
    async def test_create_booking(self, mock_1c_client, sample_client, sample_vehicle):
        """Тест: создание записи"""
        from src.modules.reception.booking import create_booking
        
        booking_data = {
            "client_id": sample_client["id"],
            "vehicle_id": sample_vehicle["id"],
            "scheduled_at": datetime.now() + timedelta(days=1),
            "service_type": "maintenance",
            "description": "Плановое ТО"
        }
        
        mock_1c_client.create_order = AsyncMock(return_value={
            "order_id": "ORD-12345",
            "status": "created"
        })
        
        with patch("src.integrations.onec.client", mock_1c_client):
            result = await create_booking(booking_data)
        
        assert result["success"] is True
        assert "order_id" in result
        assert result["order_id"] == "ORD-12345"
    
    @pytest.mark.asyncio
    async def test_booking_conflict_detection(self, mock_1c_client):
        """Тест: обнаружение конфликта при записи"""
        from src.modules.reception.booking import check_booking_conflict
        
        slot_time = datetime(2025, 1, 20, 10, 0)
        
        mock_1c_client.get_bookings = AsyncMock(return_value=[
            {"scheduled_at": slot_time, "status": "confirmed"}
        ])
        
        with patch("src.integrations.onec.client", mock_1c_client):
            has_conflict = await check_booking_conflict(slot_time)
        
        assert has_conflict is True
    
    @pytest.mark.asyncio
    async def test_send_booking_confirmation(self, mock_sms_client):
        """Тест: отправка подтверждения записи"""
        from src.modules.reception.booking import send_confirmation
        
        booking_info = {
            "client_phone": "+79991234567",
            "scheduled_at": datetime(2025, 1, 20, 10, 0),
            "order_id": "ORD-12345"
        }
        
        with patch("src.integrations.sms.client", mock_sms_client):
            result = await send_confirmation(booking_info)
        
        assert result["status"] == "sent"
        mock_sms_client.send_sms.assert_called_once()


class TestReceptionStatus:
    """Тесты проверки статуса заказ-наряда"""
    
    @pytest.mark.asyncio
    async def test_get_order_status_by_id(self, mock_1c_client, sample_order):
        """Тест: получение статуса по номеру заказ-наряда"""
        from src.modules.reception.status import get_order_status
        
        mock_1c_client.get_order = AsyncMock(return_value=sample_order)
        
        with patch("src.integrations.onec.client", mock_1c_client):
            status = await get_order_status(order_id=sample_order["id"])
        
        assert status["status"] == "in_progress"
        assert status["description"] is not None
    
    @pytest.mark.asyncio
    async def test_get_order_status_by_license_plate(self, mock_1c_client):
        """Тест: получение статуса по гос. номеру"""
        from src.modules.reception.status import get_order_by_license_plate
        
        license_plate = "А123БВ777"
        
        mock_1c_client.find_order_by_vehicle = AsyncMock(return_value={
            "order_id": "ORD-12345",
            "status": "ready",
            "vehicle": {"license_plate": license_plate}
        })
        
        with patch("src.integrations.onec.client", mock_1c_client):
            order = await get_order_by_license_plate(license_plate)
        
        assert order is not None
        assert order["status"] == "ready"
    
    @pytest.mark.asyncio
    async def test_order_not_found(self, mock_1c_client):
        """Тест: заказ-наряд не найден"""
        from src.modules.reception.status import get_order_status
        
        mock_1c_client.get_order = AsyncMock(return_value=None)
        
        with patch("src.integrations.onec.client", mock_1c_client):
            status = await get_order_status(order_id=99999)
        
        assert status is None
    
    @pytest.mark.asyncio
    async def test_format_status_message(self, sample_order):
        """Тест: форматирование сообщения о статусе"""
        from src.modules.reception.status import format_status_message
        
        message = format_status_message(sample_order)
        
        assert "ORD-" in message or str(sample_order["id"]) in message
        assert sample_order["status"] in message
        assert str(sample_order["total_amount"]) in message


class TestReceptionIntegration:
    """Интеграционные тесты модуля RECEPTION"""
    
    @pytest.mark.asyncio
    async def test_full_booking_flow(self, mock_bot, mock_message, mock_1c_client, mock_sms_client):
        """Тест: полный флоу записи от начала до конца"""
        from src.modules.reception.qualification import start_qualification
        from src.modules.reception.booking import create_booking, send_confirmation
        
        # Шаг 1: Квалификация
        qualification = await start_qualification(mock_message.from_user.id)
        assert qualification["status"] == "started"
        
        # Шаг 2: Создание записи
        booking_data = {
            "client_id": 1,
            "vehicle_id": 1,
            "scheduled_at": datetime.now() + timedelta(days=1),
            "service_type": "maintenance"
        }
        
        mock_1c_client.create_order = AsyncMock(return_value={
            "order_id": "ORD-12345",
            "status": "created"
        })
        
        with patch("src.integrations.onec.client", mock_1c_client):
            booking = await create_booking(booking_data)
        
        assert booking["success"] is True
        
        # Шаг 3: Отправка подтверждения
        with patch("src.integrations.sms.client", mock_sms_client):
            confirmation = await send_confirmation({
                "client_phone": "+79991234567",
                "order_id": booking["order_id"]
            })
        
        assert confirmation["status"] == "sent"
    
    @pytest.mark.asyncio
    async def test_handle_booking_error(self, mock_1c_client):
        """Тест: обработка ошибки при записи"""
        from src.modules.reception.booking import create_booking
        
        mock_1c_client.create_order = AsyncMock(side_effect=Exception("1C API недоступен"))
        
        with patch("src.integrations.onec.client", mock_1c_client):
            result = await create_booking({
                "client_id": 1,
                "vehicle_id": 1,
                "scheduled_at": datetime.now()
            })
        
        assert result["success"] is False
        assert "error" in result
