"""
Тесты для модуля CRM - управление клиентами и поиск
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock


class TestClientSearch:
    """Тесты поиска клиентов"""
    
    @pytest.mark.asyncio
    async def test_search_by_phone(self, mock_db, sample_client):
        """Тест: поиск клиента по номеру телефона"""
        from src.modules.crm.search import search_client_by_phone
        
        mock_db.fetch_one = AsyncMock(return_value=sample_client)
        
        with patch("src.core.database.db", mock_db):
            result = await search_client_by_phone("+79991234567")
        
        assert result is not None
        assert result["phone"] == "+79991234567"
        assert result["name"] == "ООО ТрансЛогистик"
    
    @pytest.mark.asyncio
    async def test_search_by_name(self, mock_db):
        """Тест: поиск клиента по названию компании"""
        from src.modules.crm.search import search_client_by_name
        
        clients = [
            {"id": 1, "name": "ООО ТрансЛогистик"},
            {"id": 2, "name": "ИП Транспортные Решения"}
        ]
        mock_db.fetch_all = AsyncMock(return_value=clients)
        
        with patch("src.core.database.db", mock_db):
            results = await search_client_by_name("Транс")
        
        assert len(results) == 2
        assert all("Транс" in client["name"] for client in results)
    
    @pytest.mark.asyncio
    async def test_search_by_license_plate(self, mock_db, sample_vehicle):
        """Тест: поиск клиента по гос. номеру ТС"""
        from src.modules.crm.search import search_by_license_plate
        
        mock_db.fetch_one = AsyncMock(return_value={
            "vehicle": sample_vehicle,
            "client": {"id": 1, "name": "ООО ТрансЛогистик"}
        })
        
        with patch("src.core.database.db", mock_db):
            result = await search_by_license_plate("А123БВ777")
        
        assert result is not None
        assert result["vehicle"]["license_plate"] == "А123БВ777"
        assert result["client"]["name"] == "ООО ТрансЛогистик"
    
    @pytest.mark.asyncio
    async def test_search_by_vin(self, mock_db, sample_vehicle):
        """Тест: поиск по VIN номеру"""
        from src.modules.crm.search import search_by_vin
        
        mock_db.fetch_one = AsyncMock(return_value=sample_vehicle)
        
        with patch("src.core.database.db", mock_db):
            result = await search_by_vin("YV2A22B60MA123456")
        
        assert result is not None
        assert result["vin"] == "YV2A22B60MA123456"
    
    @pytest.mark.asyncio
    async def test_multi_criteria_search(self, mock_db):
        """Тест: поиск по нескольким критериям"""
        from src.modules.crm.search import multi_search
        
        search_query = {
            "name": "Транс",
            "phone": "999",
            "license_plate": "А123"
        }
        
        mock_db.fetch_all = AsyncMock(return_value=[
            {"id": 1, "name": "ООО ТрансЛогистик", "phone": "+79991234567"}
        ])
        
        with patch("src.core.database.db", mock_db):
            results = await multi_search(search_query)
        
        assert len(results) > 0
        assert results[0]["name"] == "ООО ТрансЛогистик"
    
    @pytest.mark.asyncio
    async def test_search_no_results(self, mock_db):
        """Тест: поиск без результатов"""
        from src.modules.crm.search import search_client_by_name
        
        mock_db.fetch_all = AsyncMock(return_value=[])
        
        with patch("src.core.database.db", mock_db):
            results = await search_client_by_name("НесуществующаяКомпания")
        
        assert results == []


class TestClientHistory:
    """Тесты истории заказов клиента"""
    
    @pytest.mark.asyncio
    async def test_get_client_orders(self, mock_db, sample_order):
        """Тест: получение всех заказов клиента"""
        from src.modules.crm.history import get_client_orders
        
        orders = [sample_order, {**sample_order, "id": 2, "status": "completed"}]
        mock_db.fetch_all = AsyncMock(return_value=orders)
        
        with patch("src.core.database.db", mock_db):
            result = await get_client_orders(client_id=1)
        
        assert len(result) == 2
        assert all(order["client_id"] == 1 for order in result)
    
    @pytest.mark.asyncio
    async def test_filter_orders_by_status(self, mock_db):
        """Тест: фильтрация заказов по статусу"""
        from src.modules.crm.history import get_client_orders
        
        completed_orders = [
            {"id": 1, "status": "completed", "total_amount": 15000},
            {"id": 2, "status": "completed", "total_amount": 20000}
        ]
        mock_db.fetch_all = AsyncMock(return_value=completed_orders)
        
        with patch("src.core.database.db", mock_db):
            result = await get_client_orders(client_id=1, status="completed")
        
        assert len(result) == 2
        assert all(order["status"] == "completed" for order in result)
    
    @pytest.mark.asyncio
    async def test_filter_orders_by_date_range(self, mock_db):
        """Тест: фильтрация по периоду"""
        from src.modules.crm.history import get_orders_in_period
        
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        
        orders = [
            {"id": 1, "created_at": datetime(2025, 1, 10)},
            {"id": 2, "created_at": datetime(2025, 1, 20)}
        ]
        mock_db.fetch_all = AsyncMock(return_value=orders)
        
        with patch("src.core.database.db", mock_db):
            result = await get_orders_in_period(client_id=1, start=start_date, end=end_date)
        
        assert len(result) == 2
        for order in result:
            assert start_date <= order["created_at"] <= end_date
    
    @pytest.mark.asyncio
    async def test_calculate_client_lifetime_value(self, mock_db):
        """Тест: расчёт LTV клиента"""
        from src.modules.crm.analytics import calculate_ltv
        
        orders = [
            {"total_amount": 15000},
            {"total_amount": 20000},
            {"total_amount": 18000}
        ]
        mock_db.fetch_all = AsyncMock(return_value=orders)
        
        with patch("src.core.database.db", mock_db):
            ltv = await calculate_ltv(client_id=1)
        
        assert ltv == 53000
    
    @pytest.mark.asyncio
    async def test_get_last_service_date(self, mock_db):
        """Тест: получение даты последнего обслуживания"""
        from src.modules.crm.history import get_last_service
        
        last_order = {
            "id": 10,
            "completed_at": datetime(2025, 1, 15),
            "service_type": "maintenance"
        }
        mock_db.fetch_one = AsyncMock(return_value=last_order)
        
        with patch("src.core.database.db", mock_db):
            result = await get_last_service(client_id=1)
        
        assert result["completed_at"] == datetime(2025, 1, 15)


class TestClientCard:
    """Тесты карточки клиента"""
    
    @pytest.mark.asyncio
    async def test_get_client_full_info(self, mock_db, sample_client, sample_vehicle):
        """Тест: получение полной информации о клиенте"""
        from src.modules.crm.client_card import get_client_full_info
        
        full_info = {
            "client": sample_client,
            "vehicles": [sample_vehicle],
            "orders_count": 15,
            "total_spent": 250000,
            "last_visit": datetime(2025, 1, 10)
        }
        
        mock_db.fetch_one = AsyncMock(return_value=sample_client)
        mock_db.fetch_all = AsyncMock(side_effect=[[sample_vehicle], [{"count": 15}]])
        
        with patch("src.core.database.db", mock_db):
            result = await get_client_full_info(client_id=1)
        
        assert result["client"]["name"] == "ООО ТрансЛогистик"
        assert len(result["vehicles"]) > 0
    
    @pytest.mark.asyncio
    async def test_add_client_note(self, mock_db):
        """Тест: добавление комментария в карточку"""
        from src.modules.crm.client_card import add_note
        
        note_data = {
            "client_id": 1,
            "author_id": 5,
            "text": "Клиент просит звонить после 15:00",
            "created_at": datetime.now()
        }
        
        mock_db.execute = AsyncMock()
        
        with patch("src.core.database.db", mock_db):
            result = await add_note(note_data)
        
        assert result["success"] is True
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_client_info(self, mock_db):
        """Тест: обновление информации клиента"""
        from src.modules.crm.client_card import update_client
        
        update_data = {
            "phone": "+79997654321",
            "email": "new@email.com"
        }
        
        mock_db.execute = AsyncMock()
        
        with patch("src.core.database.db", mock_db):
            result = await update_client(client_id=1, data=update_data)
        
        assert result["success"] is True


class TestCRMIntegration:
    """Интеграционные тесты модуля CRM"""
    
    @pytest.mark.asyncio
    async def test_search_and_get_history_flow(self, mock_db):
        """Тест: поиск клиента → получение истории"""
        from src.modules.crm.search import search_client_by_phone
        from src.modules.crm.history import get_client_orders
        
        # Поиск клиента
        mock_db.fetch_one = AsyncMock(return_value={"id": 1, "name": "Тест"})
        
        with patch("src.core.database.db", mock_db):
            client = await search_client_by_phone("+79991234567")
        
        assert client is not None
        
        # Получение истории
        mock_db.fetch_all = AsyncMock(return_value=[
            {"id": 1, "status": "completed"},
            {"id": 2, "status": "in_progress"}
        ])
        
        with patch("src.core.database.db", mock_db):
            orders = await get_client_orders(client_id=client["id"])
        
        assert len(orders) == 2
    
    @pytest.mark.asyncio
    async def test_client_not_found_fallback(self, mock_db):
        """Тест: обработка ситуации "клиент не найден" """
        from src.modules.crm.search import search_client_by_phone
        
        mock_db.fetch_one = AsyncMock(return_value=None)
        
        with patch("src.core.database.db", mock_db):
            result = await search_client_by_phone("+79999999999")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(self, mock_db):
        """Тест: параллельные поисковые запросы"""
        import asyncio
        from src.modules.crm.search import search_client_by_name
        
        mock_db.fetch_all = AsyncMock(return_value=[{"id": 1, "name": "Тест"}])
        
        with patch("src.core.database.db", mock_db):
            tasks = [search_client_by_name("Тест") for _ in range(5)]
            results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(len(r) > 0 for r in results)
