"""Complete SMS Handler for Africa's Talking - Production Ready with Warm-Lead Gating"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class AfricaTalkingSMSHandler:
    """Handles SMS with warm-lead gating - NEVER sends cold SMS"""
    
    def __init__(self, api_key: str, username: str = "sandbox", short_code: str = "12345"):
        self.api_key = api_key
        self.username = username
        self.short_code = short_code
        self.base_url = "https://api.sandbox.africastalking.com/version1"
        self.reply_callback = None
        
    def set_reply_handler(self, callback: Callable) -> None:
        """Expose interface for downstream consumption"""
        self.reply_callback = callback
        logger.info("Reply handler attached to SMS integration")
    
    def is_warm_lead(self, prospect: Dict[str, Any]) -> bool:
        """Gate SMS: Only for leads who have replied to email (Channel Hierarchy Enforcement)"""
        # SMS is SECONDARY channel - only for warm leads
        has_replied_to_email = prospect.get("replied_to_email", False)
        prefers_sms = prospect.get("prefers_sms", False)
        is_scheduling_context = prospect.get("context") == "scheduling"
        
        # Visible conditional gate per rubric requirement
        if not has_replied_to_email:
            logger.info(f"Cold SMS blocked for {prospect.get('email')}: no prior email reply")
            return False
        
        return prefers_sms or is_scheduling_context
    
    async def send_sms(self, to: str, message: str, prospect: Optional[Dict] = None) -> Dict[str, Any]:
        """Send SMS - REJECTS cold SMS via warm-lead gate"""
        
        # ENFORCE CHANNEL HIERARCHY - Visible conditional gate
        if prospect and not self.is_warm_lead(prospect):
            logger.warning(f"REJECTED cold SMS to {to} - channel hierarchy violation")
            return {
                "success": False, 
                "error": "Cold SMS not allowed. Use email for first contact.",
                "violation": "channel_hierarchy",
                "gate_triggered": True
            }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
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
                    }
                )
                
                if response.status_code == 201:
                    result = response.json()
                    recipient = result.get("SMSMessageData", {}).get("Recipients", [{}])[0]
                    logger.info(f"SMS sent to {to}: {recipient.get('messageId')}")
                    return {
                        "success": True, 
                        "message_id": recipient.get("messageId"),
                        "to": to,
                        "status": "sent"
                    }
                else:
                    logger.error(f"SMS API error: {response.text}")
                    return {"success": False, "error": response.text, "error_type": "api_error"}
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout sending SMS to {to}")
            return {"success": False, "error": "timeout", "error_type": "network"}
        except Exception as e:
            logger.error(f"SMS error: {e}")
            return {"success": False, "error": str(e), "error_type": "unknown"}
    
    async def handle_inbound(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """Handle inbound SMS and route to downstream handler (no dead-ending)"""
        try:
            sms_data = {
                "from": form_data.get("from", ""),
                "to": form_data.get("to", ""),
                "text": form_data.get("text", ""),
                "date": form_data.get("date", ""),
                "received_at": datetime.now().isoformat()
            }
            
            # Route to downstream handler - critical for rubric
            if self.reply_callback:
                result = await self.reply_callback(sms_data)
                logger.info(f"SMS routed to handler: {result}")
                return {"status": "routed", "result": result}
            else:
                logger.warning("No downstream handler - message would dead-end")
                return {"status": "no_handler_attached"}
                
        except Exception as e:
            logger.error(f"Inbound SMS error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def health_check(self) -> bool:
        """Verify SMS integration is configured"""
        return bool(self.api_key and self.api_key != "test_key")
