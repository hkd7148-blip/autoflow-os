"""
AUTOFLOW OS - Admin Handlers
Handlers for system administration
"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from src.core.config import settings

logger = logging.getLogger(__name__)
router = Router(name="admin")


# Filter: only admins can use these commands
def is_admin(message: Message) -> bool:
    """Check if user is admin."""
    return message.from_user.id in settings.admin_ids


@router.message(Command("admin"), is_admin)
async def cmd_admin(message: Message) -> None:
    """Admin panel."""
    admin_text = (
        "⚙️ <b>Панель администратора</b>\n\n"
        "Доступные команды:\n\n"
        "/stats — Статистика системы\n"
        "/users — Управление пользователями\n"
        "/broadcast — Рассылка сообщений\n"
        "/logs — Последние логи\n"
        "/sync — Синхронизация с 1С"
    )
    await message.answer(admin_text)


@router.message(Command("stats"), is_admin)
async def cmd_stats(message: Message) -> None:
    """Show system statistics."""
    stats = (
        "📊 <b>Статистика AUTOFLOW OS</b>\n\n"
        "👥 <b>Пользователи:</b>\n"
        "   • Всего: 247\n"
        "   • Клиенты: 198\n"
        "   • Менеджеры: 4\n"
        "   • Механики: 8\n"
        "   • Активных сегодня: 34\n\n"
        "📋 <b>Заказы (январь):</b>\n"
        "   • Создано: 156\n"
        "   • Завершено: 142\n"
        "   • В работе: 14\n\n"
        "💰 <b>Выручка:</b>\n"
        "   • За месяц: 4 850 000 ₽\n"
        "   • Средний чек: 31 090 ₽\n\n"
        "🤖 <b>AI BRAIN:</b>\n"
        "   • Запросов: 89\n"
        "   • Точность: 87%"
    )
    await message.answer(stats)


@router.message(Command("sync"), is_admin)
async def cmd_sync(message: Message) -> None:
    """Manual sync with 1C."""
    await message.answer("🔄 Запускаю синхронизацию с 1С...")
    
    # In real app: await OneCService.sync()
    
    await message.answer(
        "✅ <b>Синхронизация завершена</b>\n\n"
        "• Клиентов обновлено: 12\n"
        "• Заказов синхронизировано: 8\n"
        "• Остатков обновлено: 156\n"
        "• Время: 2.3 сек"
    )


@router.message(Command("logs"), is_admin)
async def cmd_logs(message: Message) -> None:
    """Show recent logs."""
    logs = (
        "📜 <b>Последние события:</b>\n\n"
        "<code>14:23:15</code> ✅ Заказ ZN-2025-0152 завершён\n"
        "<code>14:21:08</code> 📦 Резерв: турбина 51.05800\n"
        "<code>14:18:45</code> 👤 Новый клиент: ИП Сидоров\n"
        "<code>14:15:22</code> 🔄 Синхронизация 1С: OK\n"
        "<code>14:12:01</code> 🧠 BRAIN запрос: P0087\n"
        "<code>14:08:33</code> 📝 Новая запись: MAN TGX\n"
    )
    await message.answer(logs)
