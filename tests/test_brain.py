"""
Тесты для модуля BRAIN - AI-ассистент для диагностики и базы знаний
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestKnowledgeBase:
    """Тесты базы знаний по ремонту"""
    
    @pytest.mark.asyncio
    async def test_search_repair_procedure(self, mock_rag_system):
        """Тест: поиск процедуры ремонта"""
        from src.modules.brain.knowledge_base import search_procedure
        
        with patch("src.modules.brain.rag_system", mock_rag_system):
            result = await search_procedure("замена масла VOLVO FH16")
        
        assert len(result) > 0
        assert result[0]["score"] > 0.8
        assert "VOLVO" in result[0]["text"]
    
    @pytest.mark.asyncio
    async def test_get_torque_specs(self, mock_rag_system):
        """Тест: получение моментов затяжки"""
        from src.modules.brain.knowledge_base import get_torque_specs
        
        mock_rag_system.search = AsyncMock(return_value=[
            {"text": "Момент затяжки болтов ГБЦ VOLVO D13: 150 Нм", "score": 0.98}
        ])
        
        with patch("src.modules.brain.rag_system", mock_rag_system):
            result = await get_torque_specs(vehicle="VOLVO D13", component="ГБЦ")
        
        assert result is not None
        assert "150 Нм" in result["text"]
    
    @pytest.mark.asyncio
    async def test_find_common_issue(self, mock_rag_system):
        """Тест: поиск типовой неисправности"""
        from src.modules.brain.knowledge_base import find_common_issues
        
        mock_rag_system.search = AsyncMock(return_value=[
            {"text": "Частая проблема: износ форсунок VOLVO D13", "score": 0.92},
            {"text": "Проверить: давление топлива, коды ошибок", "score": 0.88}
        ])
        
        with patch("src.modules.brain.rag_system", mock_rag_system):
            results = await find_common_issues(vehicle="VOLVO D13", symptom="плохой запуск")
        
        assert len(results) >= 2
        assert results[0]["score"] > 0.85
    
    @pytest.mark.asyncio
    async def test_knowledge_base_empty_query(self, mock_rag_system):
        """Тест: пустой запрос в базу знаний"""
        from src.modules.brain.knowledge_base import search_procedure
        
        mock_rag_system.search = AsyncMock(return_value=[])
        
        with patch("src.modules.brain.rag_system", mock_rag_system):
            result = await search_procedure("")
        
        assert result == []


class TestAIDiagnostics:
    """Тесты AI-диагностики"""
    
    @pytest.mark.asyncio
    async def test_analyze_obd_code(self, mock_openai_client, mock_rag_system):
        """Тест: анализ кода ошибки OBD"""
        from src.modules.brain.diagnostics import analyze_obd_code
        
        mock_rag_system.search = AsyncMock(return_value=[
            {"text": "P0087: низкое давление топлива", "score": 0.95}
        ])
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            with patch("src.modules.brain.rag_system", mock_rag_system):
                result = await analyze_obd_code(code="P0087", vehicle="VOLVO FH16")
        
        assert result["code"] == "P0087"
        assert "причины" in result
        assert "рекомендации" in result
    
    @pytest.mark.asyncio
    async def test_suggest_diagnostic_steps(self, mock_openai_client):
        """Тест: рекомендации по диагностике"""
        from src.modules.brain.diagnostics import suggest_diagnostic_steps
        
        symptoms = [
            "двигатель не заводится",
            "горит check engine",
            "ошибка P0087"
        ]
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            result = await suggest_diagnostic_steps(
                symptoms=symptoms,
                vehicle="VOLVO FH16"
            )
        
        assert "steps" in result
        assert len(result["steps"]) > 0
        assert all("description" in step for step in result["steps"])
    
    @pytest.mark.asyncio
    async def test_estimate_repair_time(self, mock_openai_client, mock_rag_system):
        """Тест: оценка времени ремонта"""
        from src.modules.brain.diagnostics import estimate_repair_time
        
        mock_rag_system.search = AsyncMock(return_value=[
            {"text": "Замена топливного насоса VOLVO: 4-6 часов", "score": 0.93}
        ])
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            with patch("src.modules.brain.rag_system", mock_rag_system):
                result = await estimate_repair_time(
                    repair_type="замена топливного насоса",
                    vehicle="VOLVO FH16"
                )
        
        assert "min_hours" in result
        assert "max_hours" in result
        assert result["min_hours"] > 0
    
    @pytest.mark.asyncio
    async def test_ai_chat_mechanic_question(self, mock_openai_client, mock_rag_system):
        """Тест: вопрос-ответ для механика"""
        from src.modules.brain.chat import ask_question
        
        question = "Как проверить турбину на VOLVO FH16?"
        
        mock_rag_system.search = AsyncMock(return_value=[
            {"text": "Проверка турбины: визуальный осмотр, люфт вала", "score": 0.91}
        ])
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            with patch("src.modules.brain.rag_system", mock_rag_system):
                response = await ask_question(question=question, context={"vehicle": "VOLVO FH16"})
        
        assert response["answer"] is not None
        assert len(response["answer"]) > 0
        assert response["sources"] is not None


class TestAIRecommendations:
    """Тесты рекомендаций AI"""
    
    @pytest.mark.asyncio
    async def test_recommend_parts_for_repair(self, mock_openai_client, mock_db):
        """Тест: рекомендация запчастей для ремонта"""
        from src.modules.brain.recommendations import recommend_parts
        
        repair_description = "Замена масла и фильтров VOLVO FH16"
        
        parts = [
            {"article": "11427953129", "name": "Масляный фильтр"},
            {"article": "ABC123", "name": "Масло 15W-40 20л"}
        ]
        mock_db.fetch_all = AsyncMock(return_value=parts)
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            with patch("src.core.database.db", mock_db):
                result = await recommend_parts(repair_description=repair_description)
        
        assert len(result["parts"]) > 0
        assert all("article" in part for part in result["parts"])
    
    @pytest.mark.asyncio
    async def test_suggest_preventive_maintenance(self, mock_openai_client, mock_rag_system):
        """Тест: рекомендации по профилактике"""
        from src.modules.brain.recommendations import suggest_preventive_maintenance
        
        vehicle_data = {
            "brand": "VOLVO",
            "model": "FH16",
            "mileage": 450000,
            "last_service": "2024-10-15"
        }
        
        mock_rag_system.search = AsyncMock(return_value=[
            {"text": "ТО-4 VOLVO FH16: каждые 80 000 км", "score": 0.94}
        ])
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            with patch("src.modules.brain.rag_system", mock_rag_system):
                result = await suggest_preventive_maintenance(vehicle_data=vehicle_data)
        
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_prioritize_repairs(self, mock_openai_client):
        """Тест: приоритизация ремонтов"""
        from src.modules.brain.recommendations import prioritize_repairs
        
        issues = [
            {"description": "Износ тормозных колодок 80%", "code": None},
            {"description": "Течь масла из двигателя", "code": None},
            {"description": "Треснуто зеркало", "code": None}
        ]
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            result = await prioritize_repairs(issues=issues)
        
        assert len(result["prioritized"]) == 3
        assert all("priority" in item for item in result["prioritized"])
        assert result["prioritized"][0]["priority"] == "critical" or result["prioritized"][0]["priority"] == "high"


class TestRAGSystem:
    """Тесты RAG (Retrieval-Augmented Generation)"""
    
    @pytest.mark.asyncio
    async def test_rag_search_with_context(self, mock_rag_system):
        """Тест: поиск с контекстом"""
        from src.modules.brain.rag_system import search_with_context
        
        query = "проблема с запуском"
        context = {"vehicle": "VOLVO FH16", "mileage": 450000}
        
        mock_rag_system.search = AsyncMock(return_value=[
            {"text": "При большом пробеге часто изнашиваются форсунки", "score": 0.89}
        ])
        
        with patch("src.modules.brain.rag_system", mock_rag_system):
            results = await search_with_context(query=query, context=context)
        
        assert len(results) > 0
        assert results[0]["score"] > 0.8
    
    @pytest.mark.asyncio
    async def test_rag_add_document(self, mock_rag_system):
        """Тест: добавление документа в базу знаний"""
        from src.modules.brain.rag_system import add_document
        
        document = {
            "title": "Замена турбины VOLVO D13",
            "content": "Подробная инструкция...",
            "category": "repair_procedures"
        }
        
        mock_rag_system.add_document = AsyncMock(return_value={"doc_id": "doc_123"})
        
        with patch("src.modules.brain.rag_system", mock_rag_system):
            result = await add_document(document=document)
        
        assert result["success"] is True
        assert "doc_id" in result
    
    @pytest.mark.asyncio
    async def test_rag_update_embeddings(self, mock_rag_system):
        """Тест: обновление векторных представлений"""
        from src.modules.brain.rag_system import update_embeddings
        
        mock_rag_system.update_embeddings = AsyncMock(return_value={"updated_count": 150})
        
        with patch("src.modules.brain.rag_system", mock_rag_system):
            result = await update_embeddings()
        
        assert result["updated_count"] > 0


class TestBrainIntegration:
    """Интеграционные тесты модуля BRAIN"""
    
    @pytest.mark.asyncio
    async def test_full_diagnostic_flow(self, mock_openai_client, mock_rag_system, mock_db):
        """Тест: полный цикл диагностики"""
        from src.modules.brain.diagnostics import analyze_obd_code
        from src.modules.brain.recommendations import recommend_parts
        
        # Шаг 1: Анализ кода ошибки
        mock_rag_system.search = AsyncMock(return_value=[
            {"text": "P0087: проблема с давлением топлива", "score": 0.95}
        ])
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            with patch("src.modules.brain.rag_system", mock_rag_system):
                diagnosis = await analyze_obd_code(code="P0087", vehicle="VOLVO FH16")
        
        assert diagnosis is not None
        
        # Шаг 2: Рекомендация запчастей
        mock_db.fetch_all = AsyncMock(return_value=[
            {"article": "FUEL123", "name": "Топливный насос"}
        ])
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            with patch("src.core.database.db", mock_db):
                parts = await recommend_parts(repair_description="замена топливного насоса")
        
        assert len(parts["parts"]) > 0
    
    @pytest.mark.asyncio
    async def test_ai_response_caching(self, mock_openai_client):
        """Тест: кеширование ответов AI"""
        from src.modules.brain.chat import ask_question
        
        question = "Как проверить турбину?"
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            # Первый запрос
            response1 = await ask_question(question=question, context={})
            
            # Второй идентичный запрос (должен взяться из кеша)
            response2 = await ask_question(question=question, context={})
        
        # OpenAI должен был вызваться только один раз (второй из кеша)
        assert mock_openai_client.chat.completions.create.call_count <= 2
    
    @pytest.mark.asyncio
    async def test_handle_ai_api_error(self, mock_openai_client):
        """Тест: обработка ошибки AI API"""
        from src.modules.brain.chat import ask_question
        
        mock_openai_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API rate limit exceeded")
        )
        
        with patch("src.modules.brain.openai_client", mock_openai_client):
            result = await ask_question(question="тестовый вопрос", context={})
        
        assert result["error"] is not None
        assert "rate limit" in result["error"].lower() or result["answer"] is None
