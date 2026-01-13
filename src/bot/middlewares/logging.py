"""
AUTOFLOW OS - Logging Middleware
"""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging all incoming updates.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Log incoming event
        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                f"Message from {user.id} ({user.full_name}): "
                f"{event.text[:50] if event.text else '[non-text]'}"
            )
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                f"Callback from {user.id} ({user.full_name}): {event.data}"
            )
        
        # Process handler
        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            logger.exception(f"Error handling event: {e}")
            raise
