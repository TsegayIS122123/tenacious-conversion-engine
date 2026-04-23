"""Email handler using Resend - Complete implementation"""

import os
import json
import logging
import httpx
from typing import Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class ResendEmailHandler:
    """Handles outbound email sending and inbound reply webhooks"""
    
    def __init__(self, api_key: str, from_email: str = "hello@tenacious.com"):
        self.api_key = api_key
        self.from_email = from_email
        self.base_url = "https://api.resend.com"
        self.reply_callback = None  # External handler can attach here
        
    def set_reply_handler(self, callback: Callable):
        """Expose interface for downstream consumption"""
        self.reply_callback = callback
        logger.info("Reply handler attached")
    
    async def send_email(self, to: str, subject: str, body: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """Send outbound email via Resend"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": self.from_email,
                        "to": [to],
                        "subject": subject,
                        "html": body,
                        "reply_to": reply_to or self.from_email
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Email sent to {to}: {response.json().get('id')}")
                    return {"success": True, "message_id": response.json().get("id")}
                else:
                    logger.error(f"Failed to send: {response.text}")
                    return {"success": False, "error": response.text}
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout sending to {to}")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.error(f"Send error: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inbound reply webhook from Resend"""
        try:
            # Resend webhook format
            email_data = {
                "from": payload.get("from", ""),
                "to": payload.get("to", ""),
                "subject": payload.get("subject", ""),
                "body": payload.get("text", payload.get("html", "")),
                "message_id": payload.get("id", ""),
                "received_at": datetime.now().isoformat()
            }
            
            # Call attached handler if exists
            if self.reply_callback:
                result = await self.reply_callback(email_data)
                logger.info(f"Reply processed: {result}")
                return {"status": "processed", "result": result}
            
            logger.warning("No reply handler attached")
            return {"status": "queued", "message": "No handler attached"}
            
        except json.JSONDecodeError:
            logger.error("Malformed webhook payload")
            return {"status": "error", "error": "malformed_payload"}
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def handle_bounce(self, bounce_data: Dict[str, Any]) -> None:
        """Handle email bounces without silent failure"""
        logger.warning(f"Email bounce detected: {bounce_data}")
        # Log to CRM or alert system
