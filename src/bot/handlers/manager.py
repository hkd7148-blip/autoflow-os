"""
AUTOFLOW OS - Manager Handlers
Handlers for manager operations (CRM module)
"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.bot.keyboards.manager import get_client_card_keyboard, get_search_results_keyboard

logger = logging.getLogger(__name__)
router = Router(name="manager")


# ============================================
# Client Search
# ============================================

@router.message(Command("find"))
async def cmd_find_client(message: Message) -> None:
    """
    Handle /find command.
    Search for clients in CRM.
    """
    # Extract search query
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "🔍 <b>Поиск клиента</b>\n\n"
            "Укажите критерий поиска:\n"
            "<code>/find Иванов</code> — по ФИО\n"
            "<code>/find +7999</code> — по телефону\n"
            "<code>/find А123БВ</code> — по гос. номеру\n"
            "<code>/find 7712345678</code> — по ИНН"
        )
        return
    
    query = parts[1].strip()
    logger.info(f"Manager {message.from_user.id} searching for: {query}")
    
    # Mock search results
    # In real app: results = await CRMService.search_clients(query)
    
    # Example found client
    client_card = (
        "🔍 <b>Найден 1 клиент:</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏢 <b>ООО «ТрансЛогистика»</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📞 +7 (495) 123-45-67\n"
        "📧 info@translog.ru\n"
        "🏷 <i>VIP-клиент | С 2019 года</i>\n\n"
        "🚛 <b>Автопарк:</b> 12 единиц\n"
        "   • MAN TGX — 5 шт\n"
        "   • Volvo FH — 4 шт\n"
        "   • Scania R — 3 шт\n\n"
        "📊 <b>Статистика:</b>\n"
        "   • Заказов всего: 47\n"
        "   • Средний чек: 85 000 ₽\n"
        "   • Последний визит: 12.01.2025\n\n"
        "💰 <b>Баланс:</b> +125 000 ₽"
    )
    
    await message.answer(
        client_card,
        reply_markup=get_client_card_keyboard(client_id=12345),
    )


@router.callback_query(F.data.startswith("client_history:"))
async def show_client_history(callback: CallbackQuery) -> None:
    """Show client's order history."""
    client_id = callback.data.split(":")[1]
    
    history = (
        "📋 <b>История заказов</b>\n\n"
        "1️⃣ <b>ZN-2025-0147</b> | 12.01.2025\n"
        "   MAN TGX А123БВ777\n"
        "   Замена турбины | 185 000 ₽\n"
        "   ✅ Завершён\n\n"
        "2️⃣ <b>ZN-2024-0891</b> | 28.11.2024\n"
        "   Volvo FH В456ГД777\n"
        "   ТО + замена масла | 45 000 ₽\n"
        "   ✅ Завершён\n\n"
        "3️⃣ <b>ZN-2024-0654</b> | 15.09.2024\n"
        "   Scania R Е789ЖЗ777\n"
        "   Диагностика АКПП | 12 000 ₽\n"
        "   ✅ Завершён"
    )
    
    await callback.message.edit_text(
        history,
        reply_markup=get_client_card_keyboard(client_id=client_id, show_back=True),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("client_fleet:"))
async def show_client_fleet(callback: CallbackQuery) -> None:
    """Show client's vehicle fleet."""
    client_id = callback.data.split(":")[1]
    
    fleet = (
        "🚛 <b>Автопарк клиента</b>\n\n"
        "1️⃣ <b>MAN TGX 18.440</b>\n"
        "   Гос. номер: А123БВ777\n"
        "   VIN: WMA06XZZ5DW123456\n"
        "   Год: 2018 | Пробег: 560 000 км\n\n"
        "2️⃣ <b>Volvo FH 460</b>\n"
        "   Гос. номер: В456ГД777\n"
        "   VIN: YV2RT40A5DB654321\n"
        "   Год: 2019 | Пробег: 420 000 км\n\n"
        "3️⃣ <b>Scania R 450</b>\n"
        "   Гос. номер: Е789ЖЗ777\n"
        "   VIN: XLER4X20005789012\n"
        "   Год: 2020 | Пробег: 310 000 км"
    )
    
    await callback.message.edit_text(
        fleet,
        reply_markup=get_client_card_keyboard(client_id=client_id, show_back=True),
    )
    await callback.answer()


# ============================================
# Active Orders
# ============================================

@router.message(Command("orders"))
async def cmd_active_orders(message: Message) -> None:
    """Show active orders for manager."""
    orders = (
        "📋 <b>Активные заказы</b>\n\n"
        "🔴 <b>ZN-2025-0152</b> | Ожидает запчасть\n"
        "   MAN TGX | ООО «Логистик»\n"
        "   Замена ТНВД\n\n"
        "🟡 <b>ZN-2025-0151</b> | В работе\n"
        "   Volvo FH | ИП Петров\n"
        "   Диагностика + ТО\n\n"
        "🟢 <b>ZN-2025-0150</b> | Готов к выдаче\n"
        "   Scania R | ООО «ТрансЛогистика»\n"
        "   Замена тормозных колодок\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Всего активных: 3"
    )
    
    await message.answer(orders)
