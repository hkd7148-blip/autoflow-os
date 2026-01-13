"""
AUTOFLOW OS - Telegram Bot Entry Point
Main bot initialization and startup
"""

import asyncio
import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from src.core.config import settings
from src.core.database import init_db, close_db
from src.bot.handlers import client, manager, mechanic, admin
from src.bot.middlewares.auth import AuthMiddleware
from src.bot.middlewares.logging import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    """Actions on bot startup."""
    logger.info("🚀 Starting AUTOFLOW OS Bot...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Set bot commands
    await bot.set_my_commands([
        ("start", "Начать работу"),
        ("help", "Помощь"),
        ("book", "Записаться на сервис"),
        ("status", "Статус заказа"),
        ("find", "Поиск клиента (для менеджеров)"),
        ("part", "Поиск запчасти"),
    ])
    logger.info("✅ Bot commands set")
    
    # Notify admins
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                "🟢 AUTOFLOW OS запущен и готов к работе!"
            )
        except Exception as e:
            logger.warning(f"Could not notify admin {admin_id}: {e}")
    
    logger.info("✅ AUTOFLOW OS Bot started successfully!")


async def on_shutdown(bot: Bot) -> None:
    """Actions on bot shutdown."""
    logger.info("🛑 Shutting down AUTOFLOW OS Bot...")
    
    # Notify admins
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                "🔴 AUTOFLOW OS остановлен"
            )
        except Exception:
            pass
    
    # Close database connections
    await close_db()
    logger.info("✅ Database connections closed")
    
    logger.info("👋 AUTOFLOW OS Bot stopped")


def create_bot() -> Bot:
    """Create and configure Bot instance."""
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )


def create_dispatcher() -> Dispatcher:
    """Create and configure Dispatcher with storage and routers."""
    # Redis storage for FSM
    redis = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis)
    
    # Create dispatcher
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Register routers
    dp.include_router(client.router)
    dp.include_router(manager.router)
    dp.include_router(mechanic.router)
    dp.include_router(admin.router)
    
    # Register startup/shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    return dp


async def main() -> None:
    """Main entry point."""
    logger.info(f"{'='*50}")
    logger.info(f"  AUTOFLOW OS v{settings.app_version}")
    logger.info(f"  Environment: {settings.environment}")
    logger.info(f"{'='*50}")
    
    bot = create_bot()
    dp = create_dispatcher()
    
    try:
        # Start polling
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        raise
