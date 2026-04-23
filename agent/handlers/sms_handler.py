"""SMS handler using Africa's Talking - Warm leads only"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class AfricaTalkingSMSHandler:
    """Handles SMS with warm-lead gating - never sends cold SMS"""
    
    def __init__(self, api_key: str, username: str = "sandbox", short_code: str = "12345"):
        self.api_key = api_key
        self.username = username
        self.short_code = short_code
        self.base_url = "https://api.sandbox.africastalking.com/version1"
        self.reply_callback = None
        
    def set_reply_handler(self, callback: Callable):
        """Expose interface for downstream consumption"""
        self.reply_callback = callback
    
    def is_warm_lead(self, prospect: Dict[str, Any]) -> bool:
        """Gate SMS: Only for leads who have replied to email"""
        # Channel hierarchy enforcement
        has_replied_to_email = prospect.get("replied_to_email", False)
        prefers_sms = prospect.get("prefers_sms", False)
        is_scheduling_context = prospect.get("context") == "scheduling"
        
        # SMS is SECONDARY channel - only for warm leads
        return has_replied_to_email and (prefers_sms or is_scheduling_context)
    
    async def send_sms(self, to: str, message: str, prospect: Optional[Dict] = None) -> Dict[str, Any]:
        """Send SMS - will reject if prospect is not warm"""
        
        # ENFORCE CHANNEL HIERARCHY
        if prospect and not self.is_warm_lead(prospect):
            logger.warning(f"Rejecting cold SMS to {to} - channel hierarchy violation")
            return {
                "success": False, 
                "error": "Cold SMS not allowed. Use email for first contact.",
                "violation": "channel_hierarchy"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messaging",
                    headers={
                        "ApiKey": f"{self.api_key}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={
                        "username": self.username,
                        "to": to,
                        "message": message,
                        "from": self.short_code
                    },
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    logger.info(f"SMS sent to {to}")
                    return {"success": True, "message_id": response.json().get("SMSMessageData", {}).get("Recipients", [{}])[0].get("messageId")}
                else:
                    logger.error(f"SMS failed: {response.text}")
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"SMS error: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_inbound(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """Handle inbound SMS and route to downstream handler"""
        try:
            sms_data = {
                "from": form_data.get("from", ""),
                "to": form_data.get("to", ""),
                "text": form_data.get("text", ""),
                "date": form_data.get("date", ""),
                "received_at": datetime.now().isoformat()
            }
            
            # Route to downstream handler (not dead-ending)
            if self.reply_callback:
                result = await self.reply_callback(sms_data)
                return {"status": "routed", "result": result}
            
            logger.warning("No downstream handler - message would dead-end")
            return {"status": "no_handler"}
            
        except Exception as e:
            logger.error(f"Inbound SMS error: {e}")
            return {"status": "error", "error": str(e)}
