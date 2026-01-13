"""
AUTOFLOW OS - Mechanic Keyboards
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_part_keyboard(part_id: str) -> InlineKeyboardMarkup:
    """Keyboard for part actions."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Зарезервировать", callback_data=f"reserve_part:{part_id}"),
        ],
        [
            InlineKeyboardButton(text="🔄 Показать аналоги", callback_data=f"show_analogs:{part_id}"),
        ],
        [
            InlineKeyboardButton(text="📦 Заказать поставщику", callback_data=f"order_part:{part_id}"),
        ],
    ])


def get_diagnostic_keyboard(error_code: str) -> InlineKeyboardMarkup:
    """Keyboard for diagnostic results."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📖 Инструкция по замене ТНВД",
                callback_data=f"instruction:fuel_pump"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📦 Заказать ТНВД со склада",
                callback_data=f"order_part_diag:ТНВД"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔍 Ещё диагностика",
                callback_data=f"more_diag:{error_code}"
            ),
        ],
    ])
