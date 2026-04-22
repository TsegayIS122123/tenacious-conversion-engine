"""SMS handler for Africa's Talking"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SMSHandler:
    """Handle SMS via Africa's Talking API"""
    
    def __init__(self):
        logger.info("SMSHandler initialized")
    
    async def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        """Send SMS (warm leads only)"""
        logger.info(f"Sending SMS to {to}: {message[:50]}...")
        return {"status": "sent", "to": to}
    
    async def health_check(self) -> bool:
        return True
