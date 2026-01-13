"""
AUTOFLOW OS - Client Keyboards
Inline and reply keyboards for client interactions
"""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard for clients."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Записаться на сервис", callback_data="action:book"),
        ],
        [
            InlineKeyboardButton(text="🔍 Статус заказа", callback_data="action:status"),
        ],
        [
            InlineKeyboardButton(text="📞 Связаться с менеджером", callback_data="action:contact"),
        ],
    ])


def get_vehicle_brands_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with supported vehicle brands."""
    brands = [
        ("MAN", "brand:MAN"),
        ("Volvo", "brand:Volvo"),
        ("Scania", "brand:Scania"),
        ("DAF", "brand:DAF"),
        ("Mercedes", "brand:Mercedes"),
        ("Iveco", "brand:Iveco"),
        ("Renault", "brand:Renault"),
        ("КАМАЗ", "brand:KAMAZ"),
    ]
    
    # Create 2-column layout
    keyboard = []
    for i in range(0, len(brands), 2):
        row = [InlineKeyboardButton(text=b[0], callback_data=b[1]) for b in brands[i:i+2]]
        keyboard.append(row)
    
    # Add cancel button
    keyboard.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_booking")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_slots_keyboard(slots: list[str]) -> InlineKeyboardMarkup:
    """Keyboard with available time slots."""
    keyboard = []
    
    for i, slot in enumerate(slots):
        keyboard.append([
            InlineKeyboardButton(text=f"📅 {slot}", callback_data=f"slot:{i}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_booking")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Confirmation keyboard for booking."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking"),
        ],
        [
            InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_booking"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking"),
        ],
    ])


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard for phone number sharing."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
