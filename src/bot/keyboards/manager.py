"""
AUTOFLOW OS - Manager Keyboards
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_client_card_keyboard(client_id: int, show_back: bool = False) -> InlineKeyboardMarkup:
    """Keyboard for client card actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="📋 История заказов", callback_data=f"client_history:{client_id}"),
            InlineKeyboardButton(text="🚛 Автопарк", callback_data=f"client_fleet:{client_id}"),
        ],
        [
            InlineKeyboardButton(text="📞 Позвонить", callback_data=f"client_call:{client_id}"),
            InlineKeyboardButton(text="💬 Написать", callback_data=f"client_message:{client_id}"),
        ],
    ]
    
    if show_back:
        keyboard.append([
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"client_card:{client_id}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_search_results_keyboard(results: list) -> InlineKeyboardMarkup:
    """Keyboard for search results."""
    keyboard = []
    for r in results[:5]:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{r['name']} | {r['phone']}",
                callback_data=f"select_client:{r['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
