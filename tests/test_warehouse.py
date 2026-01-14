"""
Тесты для модуля WAREHOUSE - управление складом запчастей
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock


class TestPartSearch:
    """Тесты поиска запчастей"""
    
    @pytest.mark.asyncio
    async def test_search_by_article(self, mock_db, sample_part):
        """Тест: поиск запчасти по артикулу"""
        from src.modules.warehouse.search import search_by_article
        
        mock_db.fetch_one = AsyncMock(return_value=sample_part)
        
        with patch("src.core.database.db", mock_db):
            result = await search_by_article("11427953129")
        
        assert result is not None
        assert result["article"] == "11427953129"
        assert result["name"] == "Масляный фильтр"
    
    @pytest.mark.asyncio
    async def test_search_by_name(self, mock_db):
        """Тест: поиск по названию"""
        from src.modules.warehouse.search import search_by_name
        
        parts = [
            {"id": 1, "name": "Масляный фильтр MANN", "quantity": 10},
            {"id": 2, "name": "Масляный фильтр BOSCH", "quantity": 5}
        ]
        mock_db.fetch_all = AsyncMock(return_value=parts)
        
        with patch("src.core.database.db", mock_db):
            results = await search_by_name("Масляный фильтр")
        
        assert len(results) == 2
        assert all("фильтр" in part["name"].lower() for part in results)
    
    @pytest.mark.asyncio
    async def test_search_by_vehicle_brand(self, mock_db):
        """Тест: поиск запчастей для конкретной марки"""
        from src.modules.warehouse.search import search_by_vehicle
        
        volvo_parts = [
            {"id": 1, "name": "Тормозные колодки", "compatible_brands": ["VOLVO"]},
            {"id": 2, "name": "Воздушный фильтр", "compatible_brands": ["VOLVO", "SCANIA"]}
        ]
        mock_db.fetch_all = AsyncMock(return_value=volvo_parts)
        
        with patch("src.core.database.db", mock_db):
            results = await search_by_vehicle(brand="VOLVO", model="FH16")
        
        assert len(results) > 0
        assert all("VOLVO" in part["compatible_brands"] for part in results)
    
    @pytest.mark.asyncio
    async def test_cross_reference_search(self, mock_db):
        """Тест: поиск по кросс-номеру (аналоги)"""
        from src.modules.warehouse.cross_catalog import find_analogs
        
        analogs = [
            {"article": "11427953129", "brand": "MANN", "price": 850},
            {"article": "OX123D", "brand": "MAHLE", "price": 920},
            {"article": "HU719/7x", "brand": "MANN", "price": 880}
        ]
        mock_db.fetch_all = AsyncMock(return_value=analogs)
        
        with patch("src.core.database.db", mock_db):
            results = await find_analogs("11427953129")
        
        assert len(results) >= 2
        assert all(part["article"] != "11427953129" for part in results[1:])


class TestInventory:
    """Тесты управления остатками"""
    
    @pytest.mark.asyncio
    async def test_check_availability(self, mock_db, sample_part):
        """Тест: проверка наличия на складе"""
        from src.modules.warehouse.inventory import check_availability
        
        mock_db.fetch_one = AsyncMock(return_value=sample_part)
        
        with patch("src.core.database.db", mock_db):
            result = await check_availability(part_id=1)
        
        assert result["available"] is True
        assert result["quantity"] == 25
    
    @pytest.mark.asyncio
    async def test_reserve_part(self, mock_db):
        """Тест: резервирование запчасти"""
        from src.modules.warehouse.inventory import reserve_part
        
        mock_db.execute = AsyncMock()
        mock_db.fetch_one = AsyncMock(return_value={"quantity": 25})
        
        with patch("src.core.database.db", mock_db):
            result = await reserve_part(part_id=1, quantity=3, order_id="ORD-001")
        
        assert result["success"] is True
        assert result["reserved_quantity"] == 3
    
    @pytest.mark.asyncio
    async def test_reserve_insufficient_stock(self, mock_db):
        """Тест: попытка резервирования при недостатке товара"""
        from src.modules.warehouse.inventory import reserve_part
        
        mock_db.fetch_one = AsyncMock(return_value={"quantity": 2})
        
        with patch("src.core.database.db", mock_db):
            result = await reserve_part(part_id=1, quantity=5, order_id="ORD-001")
        
        assert result["success"] is False
        assert "insufficient" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_release_reservation(self, mock_db):
        """Тест: снятие резерва"""
        from src.modules.warehouse.inventory import release_reservation
        
        mock_db.execute = AsyncMock()
        
        with patch("src.core.database.db", mock_db):
            result = await release_reservation(order_id="ORD-001")
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_get_low_stock_items(self, mock_db):
        """Тест: получение товаров с низким остатком"""
        from src.modules.warehouse.inventory import get_low_stock_items
        
        low_stock = [
            {"id": 1, "name": "Тормозные колодки", "quantity": 2, "min_quantity": 5},
            {"id": 2, "name": "Масло 10W-40", "quantity": 3, "min_quantity": 10}
        ]
        mock_db.fetch_all = AsyncMock(return_value=low_stock)
        
        with patch("src.core.database.db", mock_db):
            results = await get_low_stock_items(threshold=5)
        
        assert len(results) == 2
        assert all(item["quantity"] < item["min_quantity"] for item in results)
    
    @pytest.mark.asyncio
    async def test_update_stock_after_delivery(self, mock_db):
        """Тест: обновление остатков после поступления"""
        from src.modules.warehouse.inventory import update_stock
        
        mock_db.execute = AsyncMock()
        
        with patch("src.core.database.db", mock_db):
            result = await update_stock(part_id=1, quantity_change=+50, reason="delivery")
        
        assert result["success"] is True
        mock_db.execute.assert_called_once()


class TestWarehouseIntegration:
    """Тесты интеграции с 1С"""
    
    @pytest.mark.asyncio
    async def test_sync_inventory_with_1c(self, mock_1c_client, mock_db):
        """Тест: синхронизация остатков с 1С"""
        from src.modules.warehouse.sync import sync_inventory
        
        inventory_1c = [
            {"article": "11427953129", "quantity": 30, "price": 850},
            {"article": "OX123D", "quantity": 15, "price": 920}
        ]
        mock_1c_client.get_inventory = AsyncMock(return_value=inventory_1c)
        mock_db.execute = AsyncMock()
        
        with patch("src.integrations.onec.client", mock_1c_client):
            with patch("src.core.database.db", mock_db):
                result = await sync_inventory()
        
        assert result["synced_count"] == 2
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_fetch_prices_from_1c(self, mock_1c_client):
        """Тест: получение актуальных цен из 1С"""
        from src.modules.warehouse.pricing import fetch_current_prices
        
        prices = [
            {"article": "11427953129", "price": 850, "discount": 0},
            {"article": "OX123D", "price": 920, "discount": 10}
        ]
        mock_1c_client.get_prices = AsyncMock(return_value=prices)
        
        with patch("src.integrations.onec.client", mock_1c_client):
            result = await fetch_current_prices(["11427953129", "OX123D"])
        
        assert len(result) == 2
        assert result[0]["price"] == 850
    
    @pytest.mark.asyncio
    async def test_create_order_to_supplier(self, mock_1c_client):
        """Тест: создание заказа поставщику"""
        from src.modules.warehouse.procurement import create_supplier_order
        
        order_items = [
            {"article": "11427953129", "quantity": 20},
            {"article": "OX123D", "quantity": 10}
        ]
        
        mock_1c_client.create_supplier_order = AsyncMock(return_value={
            "order_id": "PO-12345",
            "status": "created"
        })
        
        with patch("src.integrations.onec.client", mock_1c_client):
            result = await create_supplier_order(items=order_items, supplier_id="SUP-01")
        
        assert result["success"] is True
        assert "order_id" in result


class TestCrossCatalog:
    """Тесты кросс-каталога аналогов"""
    
    @pytest.mark.asyncio
    async def test_find_cheaper_analog(self, mock_db):
        """Тест: поиск более дешёвого аналога"""
        from src.modules.warehouse.cross_catalog import find_cheaper_analog
        
        analogs = [
            {"article": "11427953129", "brand": "MANN", "price": 850, "quality": "OEM"},
            {"article": "OX123D", "brand": "MAHLE", "price": 720, "quality": "OEM"},
            {"article": "FL1234", "brand": "FILTRON", "price": 550, "quality": "Aftermarket"}
        ]
        mock_db.fetch_all = AsyncMock(return_value=analogs)
        
        with patch("src.core.database.db", mock_db):
            result = await find_cheaper_analog("11427953129", max_price=800)
        
        assert result is not None
        assert result["price"] < 800
    
    @pytest.mark.asyncio
    async def test_filter_by_quality(self, mock_db):
        """Тест: фильтрация аналогов по качеству"""
        from src.modules.warehouse.cross_catalog import find_analogs
        
        analogs = [
            {"article": "A1", "quality": "OEM"},
            {"article": "A2", "quality": "OEM"},
            {"article": "A3", "quality": "Aftermarket"}
        ]
        mock_db.fetch_all = AsyncMock(return_value=analogs)
        
        with patch("src.core.database.db", mock_db):
            results = await find_analogs("11427953129", quality_filter="OEM")
        
        assert len(results) == 2
        assert all(part["quality"] == "OEM" for part in results)


class TestWarehouseAnalytics:
    """Тесты аналитики склада"""
    
    @pytest.mark.asyncio
    async def test_calculate_turnover_rate(self, mock_db):
        """Тест: расчёт оборачиваемости товаров"""
        from src.modules.warehouse.analytics import calculate_turnover
        
        sales_data = [
            {"part_id": 1, "quantity_sold": 50, "period_days": 30},
        ]
        inventory_data = {"part_id": 1, "avg_quantity": 25}
        
        mock_db.fetch_all = AsyncMock(return_value=sales_data)
        mock_db.fetch_one = AsyncMock(return_value=inventory_data)
        
        with patch("src.core.database.db", mock_db):
            turnover = await calculate_turnover(part_id=1, period_days=30)
        
        assert turnover > 0
        assert turnover == pytest.approx(2.0, rel=0.1)  # 50/25 = 2
    
    @pytest.mark.asyncio
    async def test_identify_dead_stock(self, mock_db):
        """Тест: выявление неликвидных товаров"""
        from src.modules.warehouse.analytics import identify_dead_stock
        
        dead_stock = [
            {"part_id": 5, "name": "Старый фильтр", "last_sold": datetime(2023, 6, 1)},
            {"part_id": 12, "name": "Редкая деталь", "last_sold": datetime(2023, 3, 15)}
        ]
        mock_db.fetch_all = AsyncMock(return_value=dead_stock)
        
        with patch("src.core.database.db", mock_db):
            results = await identify_dead_stock(days_threshold=180)
        
        assert len(results) == 2
        for item in results:
            assert (datetime.now() - item["last_sold"]).days > 180
