"""
AUTOFLOW OS - Client Handlers
Handlers for client-facing bot interactions (RECEPTION module)
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from src.bot.keyboards.client import (
    get_main_menu_keyboard,
    get_vehicle_brands_keyboard,
    get_slots_keyboard,
    get_confirmation_keyboard,
)
from src.modules.reception.service import ReceptionService

logger = logging.getLogger(__name__)
router = Router(name="client")


# ============================================
# FSM States for Booking Flow
# ============================================

class BookingStates(StatesGroup):
    """States for the booking conversation flow."""
    waiting_for_brand = State()
    waiting_for_model = State()
    waiting_for_problem = State()
    waiting_for_phone = State()
    waiting_for_slot = State()
    waiting_for_confirmation = State()


# ============================================
# Command Handlers
# ============================================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Handle /start command.
    Welcome message and main menu.
    """
    await state.clear()
    
    user = message.from_user
    logger.info(f"User {user.id} ({user.full_name}) started the bot")
    
    welcome_text = (
        f"👋 Здравствуйте, {user.first_name}!\n\n"
        f"Я — <b>AUTOFLOW</b>, ваш помощник в автосервисе.\n\n"
        f"Я могу помочь вам:\n"
        f"• 📝 Записаться на ремонт\n"
        f"• 🔍 Узнать статус вашего заказа\n"
        f"• 📞 Связаться с менеджером\n\n"
        f"Выберите действие:"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    help_text = (
        "📖 <b>Справка по командам</b>\n\n"
        "/start — Главное меню\n"
        "/book — Записаться на сервис\n"
        "/status — Проверить статус заказа\n"
        "/help — Эта справка\n\n"
        "💬 Также вы можете просто написать мне "
        "о вашей проблеме, и я помогу записаться на ремонт."
    )
    await message.answer(help_text)


@router.message(Command("book"))
async def cmd_book(message: Message, state: FSMContext) -> None:
    """
    Handle /book command.
    Start the booking flow.
    """
    await state.clear()
    
    await message.answer(
        "🚛 <b>Запись на сервис</b>\n\n"
        "Давайте запишем вас на ремонт.\n"
        "Для начала выберите марку вашего грузовика:",
        reply_markup=get_vehicle_brands_keyboard(),
    )
    
    await state.set_state(BookingStates.waiting_for_brand)


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    """
    Handle /status command.
    Check order status.
    """
    await message.answer(
        "🔍 <b>Проверка статуса заказа</b>\n\n"
        "Введите номер заказ-наряда или гос. номер вашего ТС:\n\n"
        "<i>Например: ZN-2024-1234 или А123БВ777</i>"
    )


# ============================================
# Booking Flow Handlers
# ============================================

@router.callback_query(BookingStates.waiting_for_brand, F.data.startswith("brand:"))
async def process_brand_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Process vehicle brand selection."""
    brand = callback.data.split(":")[1]
    await state.update_data(brand=brand)
    
    await callback.message.edit_text(
        f"✅ Марка: <b>{brand}</b>\n\n"
        f"Теперь введите модель вашего грузовика:\n"
        f"<i>Например: TGX 18.440, FH 460, R 450 и т.д.</i>"
    )
    
    await state.set_state(BookingStates.waiting_for_model)
    await callback.answer()


@router.message(BookingStates.waiting_for_model)
async def process_model_input(message: Message, state: FSMContext) -> None:
    """Process vehicle model input."""
    model = message.text.strip()
    await state.update_data(model=model)
    
    data = await state.get_data()
    
    await message.answer(
        f"✅ Автомобиль: <b>{data['brand']} {model}</b>\n\n"
        f"Опишите проблему или симптомы неисправности:\n"
        f"<i>Например: двигатель троит, горит check engine, "
        f"стук в подвеске и т.д.</i>"
    )
    
    await state.set_state(BookingStates.waiting_for_problem)


@router.message(BookingStates.waiting_for_problem)
async def process_problem_input(message: Message, state: FSMContext) -> None:
    """Process problem description input."""
    problem = message.text.strip()
    await state.update_data(problem=problem)
    
    await message.answer(
        "✅ Проблема записана.\n\n"
        "Укажите ваш контактный телефон:\n"
        "<i>Например: +7 999 123-45-67</i>"
    )
    
    await state.set_state(BookingStates.waiting_for_phone)


@router.message(BookingStates.waiting_for_phone)
async def process_phone_input(message: Message, state: FSMContext) -> None:
    """Process phone number input."""
    phone = message.text.strip()
    await state.update_data(phone=phone)
    
    # Generate available slots
    slots = generate_available_slots()
    await state.update_data(available_slots=slots)
    
    data = await state.get_data()
    
    summary = (
        f"📋 <b>Ваша заявка:</b>\n\n"
        f"🚛 Автомобиль: {data['brand']} {data['model']}\n"
        f"🔧 Проблема: {data['problem']}\n"
        f"📞 Телефон: {phone}\n\n"
        f"Выберите удобное время для визита:"
    )
    
    await message.answer(
        summary,
        reply_markup=get_slots_keyboard(slots),
    )
    
    await state.set_state(BookingStates.waiting_for_slot)


@router.callback_query(BookingStates.waiting_for_slot, F.data.startswith("slot:"))
async def process_slot_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Process time slot selection."""
    slot_index = int(callback.data.split(":")[1])
    data = await state.get_data()
    
    selected_slot = data["available_slots"][slot_index]
    await state.update_data(selected_slot=selected_slot)
    
    confirmation_text = (
        f"📝 <b>Подтверждение записи</b>\n\n"
        f"🚛 Автомобиль: {data['brand']} {data['model']}\n"
        f"🔧 Проблема: {data['problem']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📅 Дата и время: <b>{selected_slot}</b>\n\n"
        f"Всё верно?"
    )
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=get_confirmation_keyboard(),
    )
    
    await state.set_state(BookingStates.waiting_for_confirmation)
    await callback.answer()


@router.callback_query(BookingStates.waiting_for_confirmation, F.data == "confirm_booking")
async def process_booking_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    """Process booking confirmation."""
    data = await state.get_data()
    
    # Here would be actual booking logic via ReceptionService
    # order_number = await ReceptionService.create_booking(data)
    order_number = f"ZN-2025-{callback.from_user.id % 10000:04d}"
    
    success_text = (
        f"✅ <b>Запись успешно создана!</b>\n\n"
        f"📋 Номер заказ-наряда: <code>{order_number}</code>\n"
        f"📅 Дата: {data['selected_slot']}\n"
        f"📍 Адрес: ул. Промышленная, 15\n\n"
        f"За час до визита я пришлю вам напоминание.\n\n"
        f"Хорошего дня! 🚛"
    )
    
    await callback.message.edit_text(success_text)
    await state.clear()
    await callback.answer("Запись создана!")
    
    logger.info(
        f"Booking created: {order_number} for user {callback.from_user.id}"
    )


@router.callback_query(BookingStates.waiting_for_confirmation, F.data == "cancel_booking")
async def process_booking_cancellation(callback: CallbackQuery, state: FSMContext) -> None:
    """Process booking cancellation."""
    await callback.message.edit_text(
        "❌ Запись отменена.\n\n"
        "Если хотите начать заново, используйте команду /book"
    )
    await state.clear()
    await callback.answer("Запись отменена")


# ============================================
# Helper Functions
# ============================================

def generate_available_slots() -> list[str]:
    """Generate available time slots for the next few days."""
    slots = []
    now = datetime.now()
    
    # Generate slots for the next 3 days
    for day_offset in range(1, 4):
        date = now + timedelta(days=day_offset)
        day_name = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][date.weekday()]
        
        # Skip Sunday
        if date.weekday() == 6:
            continue
        
        # Morning and afternoon slots
        for hour in [9, 10, 14, 16]:
            slot = f"{day_name}, {date.strftime('%d.%m')} в {hour}:00"
            slots.append(slot)
    
    return slots[:6]  # Return max 6 slots


# ============================================
# Fallback Handler
# ============================================

@router.message(F.text)
async def handle_text_message(message: Message, state: FSMContext) -> None:
    """
    Handle any text message not caught by other handlers.
    Basic NLU to understand user intent.
    """
    text = message.text.lower()
    
    # Simple intent detection
    if any(word in text for word in ["запис", "ремонт", "сервис", "записаться"]):
        await cmd_book(message, state)
    elif any(word in text for word in ["статус", "заказ", "готов"]):
        await cmd_status(message)
    elif any(word in text for word in ["привет", "здравств", "добрый"]):
        await cmd_start(message, state)
    else:
        await message.answer(
            "🤔 Не совсем понял вас.\n\n"
            "Попробуйте:\n"
            "• /book — записаться на сервис\n"
            "• /status — узнать статус заказа\n"
            "• /help — справка по командам"
        )
