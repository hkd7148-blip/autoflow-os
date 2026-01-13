"""
AUTOFLOW OS - Reception Service
Business logic for client intake and booking
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BookingData:
    """Data structure for booking."""
    brand: str
    model: str
    problem: str
    phone: str
    slot: str
    client_telegram_id: int
    client_name: str


@dataclass
class Booking:
    """Booking entity."""
    id: int
    order_number: str
    brand: str
    model: str
    problem: str
    phone: str
    scheduled_time: datetime
    status: str
    client_telegram_id: int
    created_at: datetime


class ReceptionService:
    """
    Service for handling client reception operations.
    Part of the RECEPTION module.
    """
    
    @staticmethod
    async def create_booking(data: BookingData) -> Booking:
        """
        Create a new booking/appointment.
        
        Args:
            data: Booking data from the conversation
            
        Returns:
            Created booking with order number
        """
        logger.info(f"Creating booking for {data.client_telegram_id}")
        
        # Generate order number
        order_number = ReceptionService._generate_order_number()
        
        # Parse scheduled time from slot string
        scheduled_time = ReceptionService._parse_slot(data.slot)
        
        # In real app: save to database and sync with 1C
        # booking = await BookingRepository.create(...)
        # await OneCService.create_appointment(booking)
        
        booking = Booking(
            id=1,
            order_number=order_number,
            brand=data.brand,
            model=data.model,
            problem=data.problem,
            phone=data.phone,
            scheduled_time=scheduled_time,
            status="pending",
            client_telegram_id=data.client_telegram_id,
            created_at=datetime.now(),
        )
        
        logger.info(f"Booking created: {order_number}")
        return booking
    
    @staticmethod
    async def get_booking_status(order_number: str) -> Optional[dict]:
        """
        Get booking status by order number.
        
        Args:
            order_number: Order number (e.g., ZN-2025-1234)
            
        Returns:
            Booking status dict or None
        """
        logger.info(f"Checking status for {order_number}")
        
        # In real app: query database and 1C
        # booking = await BookingRepository.get_by_order_number(order_number)
        
        # Mock response
        return {
            "order_number": order_number,
            "status": "in_progress",
            "status_text": "В работе",
            "vehicle": "MAN TGX 18.440",
            "problem": "Диагностика топливной системы",
            "eta": "Сегодня, ~17:00",
            "mechanic": "Иванов А.С.",
        }
    
    @staticmethod
    async def get_available_slots(days: int = 3) -> List[dict]:
        """
        Get available time slots for booking.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of available slots
        """
        slots = []
        now = datetime.now()
        
        for day_offset in range(1, days + 1):
            date = now + timedelta(days=day_offset)
            
            # Skip Sunday
            if date.weekday() == 6:
                continue
            
            # Working hours: 9:00 - 18:00
            for hour in [9, 10, 11, 14, 15, 16, 17]:
                slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                # In real app: check availability in 1C
                # is_available = await OneCService.check_slot(slot_time)
                is_available = True
                
                if is_available:
                    slots.append({
                        "datetime": slot_time,
                        "display": slot_time.strftime("%a, %d.%m в %H:%M"),
                        "available": True,
                    })
        
        return slots
    
    @staticmethod
    async def cancel_booking(order_number: str, reason: str = "") -> bool:
        """
        Cancel a booking.
        
        Args:
            order_number: Order number to cancel
            reason: Cancellation reason
            
        Returns:
            True if cancelled successfully
        """
        logger.info(f"Cancelling booking {order_number}: {reason}")
        
        # In real app: update database and 1C
        # await BookingRepository.cancel(order_number, reason)
        # await OneCService.cancel_appointment(order_number)
        
        return True
    
    @staticmethod
    def _generate_order_number() -> str:
        """Generate unique order number."""
        now = datetime.now()
        # Format: ZN-YYYY-XXXX
        seq = int(now.timestamp()) % 10000
        return f"ZN-{now.year}-{seq:04d}"
    
    @staticmethod
    def _parse_slot(slot_str: str) -> datetime:
        """Parse slot string to datetime."""
        # Simple parser, in real app would be more robust
        now = datetime.now()
        
        if "завтра" in slot_str.lower():
            date = now + timedelta(days=1)
        elif "послезавтра" in slot_str.lower():
            date = now + timedelta(days=2)
        else:
            date = now + timedelta(days=1)
        
        # Extract time if present
        import re
        time_match = re.search(r"(\d{1,2}):(\d{2})", slot_str)
        if time_match:
            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            date = date.replace(hour=hour, minute=minute)
        else:
            date = date.replace(hour=10, minute=0)
        
        return date
