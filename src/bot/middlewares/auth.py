"""
AUTOFLOW OS - Authentication Middleware
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from src.core.config import settings


class AuthMiddleware(BaseMiddleware):
    """
    Middleware for user authentication and role detection.
    Adds user role to handler data.
    """
    
    # Mock database of users and roles
    # In production, this would query the database
    MOCK_ROLES: Dict[int, str] = {
        # Add your test user IDs here
    }
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Get user from event
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if user:
            # Determine user role
            role = await self._get_user_role(user.id)
            data["user_role"] = role
            data["user_id"] = user.id
            data["is_admin"] = user.id in settings.admin_ids
        
        return await handler(event, data)
    
    async def _get_user_role(self, user_id: int) -> str:
        """
        Determine user role based on user_id.
        
        Roles:
        - admin: System administrator
        - manager: Service manager (CRM access)
        - mechanic: Mechanic (WAREHOUSE + BRAIN access)
        - client: Regular client (RECEPTION access)
        """
        # Check if admin
        if user_id in settings.admin_ids:
            return "admin"
        
        # Check mock roles
        if user_id in self.MOCK_ROLES:
            return self.MOCK_ROLES[user_id]
        
        # In real app: query database
        # role = await UserRepository.get_role(user_id)
        
        # Default to client
        return "client"
