"""
AUTOFLOW OS - Mechanic Handlers
Handlers for mechanic operations (WAREHOUSE + BRAIN modules)
"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.bot.keyboards.mechanic import get_part_keyboard, get_diagnostic_keyboard

logger = logging.getLogger(__name__)
router = Router(name="mechanic")


# ============================================
# Parts Search (WAREHOUSE)
# ============================================

@router.message(Command("part"))
async def cmd_search_part(message: Message) -> None:
    """
    Handle /part command.
    Search for spare parts in warehouse.
    """
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "📦 <b>Поиск запчастей</b>\n\n"
            "Укажите артикул или название:\n"
            "<code>/part 51.05800-7684</code>\n"
            "<code>/part турбина MAN</code>\n"
            "<code>/part фильтр воздушный Volvo</code>"
        )
        return
    
    query = parts[1].strip()
    logger.info(f"Mechanic {message.from_user.id} searching part: {query}")
    
    # Mock search result
    # In real app: result = await WarehouseService.search_parts(query)
    
    part_info = (
        "🔍 <b>Найдена запчасть:</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 <b>Турбокомпрессор MAN D2676</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔖 Артикул: <code>51.05800-7684</code>\n"
        "🏭 Производитель: MAN Original\n\n"
        "📍 <b>Наличие:</b>\n"
        "   • Склад основной: <b>2 шт</b> ✅\n"
        "   • Склад запасной: 0 шт\n"
        "   • В пути: 1 шт (ETA: 20.01)\n\n"
        "💰 <b>Цена:</b> 185 000 ₽\n\n"
        "🔄 <b>Аналоги в наличии:</b>\n"
        "   • BorgWarner 53299887131 — 156 000 ₽ (1 шт)\n"
        "   • Holset HX55W — 142 000 ₽ (3 шт)"
    )
    
    await message.answer(
        part_info,
        reply_markup=get_part_keyboard(part_id="51058007684"),
    )


@router.callback_query(F.data.startswith("reserve_part:"))
async def reserve_part(callback: CallbackQuery) -> None:
    """Reserve a part for work order."""
    part_id = callback.data.split(":")[1]
    
    await callback.message.edit_text(
        callback.message.text + "\n\n"
        "✅ <b>Запчасть зарезервирована!</b>\n"
        "Резерв действует 24 часа.",
    )
    await callback.answer("Зарезервировано!")
    
    logger.info(f"Part {part_id} reserved by {callback.from_user.id}")


@router.callback_query(F.data.startswith("show_analogs:"))
async def show_part_analogs(callback: CallbackQuery) -> None:
    """Show part analogs/alternatives."""
    part_id = callback.data.split(":")[1]
    
    analogs = (
        "🔄 <b>Аналоги для 51.05800-7684</b>\n\n"
        "1️⃣ <b>BorgWarner 53299887131</b>\n"
        "   💰 156 000 ₽ | 📦 1 шт\n"
        "   ⭐ Рекомендуется\n\n"
        "2️⃣ <b>Holset HX55W</b>\n"
        "   💰 142 000 ₽ | 📦 3 шт\n"
        "   ✅ Хорошее качество\n\n"
        "3️⃣ <b>Garrett GT4294</b>\n"
        "   💰 168 000 ₽ | 📦 0 шт\n"
        "   ⏳ Под заказ: 5-7 дней"
    )
    
    await callback.message.edit_text(analogs)
    await callback.answer()


# ============================================
# AI Diagnostics (BRAIN)
# ============================================

@router.message(Command("diag"))
async def cmd_diagnose(message: Message) -> None:
    """
    Handle /diag command.
    AI-powered diagnostics assistance.
    """
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "🧠 <b>AI-диагностика</b>\n\n"
            "Опишите симптомы или укажите код ошибки:\n"
            "<code>/diag P0087</code>\n"
            "<code>/diag MAN TGX двигатель троит</code>\n"
            "<code>/diag Volvo горит check engine</code>"
        )
        return
    
    query = parts[1].strip()
    logger.info(f"Diagnostic query from {message.from_user.id}: {query}")
    
    # Check if it's an error code
    if query.upper().startswith("P") and len(query) == 5:
        await handle_error_code(message, query.upper())
    else:
        await handle_symptom_description(message, query)


async def handle_error_code(message: Message, code: str) -> None:
    """Handle OBD error code lookup."""
    
    # Mock AI response
    # In real app: response = await BrainService.analyze_error_code(code)
    
    diagnosis = (
        f"🔍 <b>Анализирую код {code}...</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ <b>{code}</b> — Низкое давление\n"
        "   в топливной рампе\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 <b>Вероятные причины:</b>\n\n"
        "1. 🔴 <b>85%</b> — ТНВД\n"
        "   <i>Износ плунжерной пары</i>\n\n"
        "2. 🟠 <b>60%</b> — Регулятор давления\n"
        "   <i>Заклинивание или утечка</i>\n\n"
        "3. 🟡 <b>40%</b> — Топливный фильтр\n"
        "   <i>Засорение</i>\n\n"
        "4. 🟢 <b>20%</b> — Форсунки\n"
        "   <i>Утечка обратки</i>\n\n"
        "🔧 <b>Рекомендуемая диагностика:</b>\n\n"
        "1. Проверить давление в рампе\n"
        "   манометром (норма: 1600-1800 bar)\n\n"
        "2. Проверить производительность\n"
        "   ТНВД на стенде\n\n"
        "3. Осмотреть топливные магистрали\n"
        "   на предмет утечек\n\n"
        "📋 <b>Из истории сервиса:</b>\n"
        f"   <i>За год 3 случая {code} на MAN TGX —\n"
        "   во всех случаях причина в ТНВД.</i>"
    )
    
    await message.answer(
        diagnosis,
        reply_markup=get_diagnostic_keyboard(code),
    )


async def handle_symptom_description(message: Message, description: str) -> None:
    """Handle symptom-based diagnosis."""
    
    diagnosis = (
        "🔍 <b>Анализирую описание...</b>\n\n"
        f"<i>\"{description}\"</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔧 <b>Предварительный анализ:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Симптомы указывают на возможные\n"
        "проблемы с топливной системой.\n\n"
        "<b>Рекомендуется:</b>\n"
        "1. Подключить диагностический сканер\n"
        "2. Считать коды ошибок\n"
        "3. Проверить давление топлива\n\n"
        "💡 <i>Уточните код ошибки для более\n"
        "точной диагностики.</i>"
    )
    
    await message.answer(diagnosis)


@router.callback_query(F.data.startswith("order_part_diag:"))
async def order_part_from_diagnostic(callback: CallbackQuery) -> None:
    """Order part recommended by diagnostics."""
    part = callback.data.split(":")[1]
    
    await callback.answer(f"Переход к заказу {part}...")
    await callback.message.answer(
        f"📦 Для заказа запчасти используйте:\n"
        f"<code>/part {part}</code>"
    )
