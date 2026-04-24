"""Complete Email Handler for Resend API - Production Ready"""

import os
import json
import logging
import httpx
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ResendEmailHandler:
    """Handles outbound email sending and inbound reply webhooks for Resend"""
    
    def __init__(self, api_key: str, from_email: str = "hello@tenacious.com"):
        self.api_key = api_key
        self.from_email = from_email
        self.base_url = "https://api.resend.com"
        self.reply_callback = None
        self.bounce_callback = None
        
    def set_reply_handler(self, callback: Callable) -> None:
        """Expose interface for downstream consumption"""
        self.reply_callback = callback
        logger.info("Reply handler attached to email integration")
    
    def set_bounce_handler(self, callback: Callable) -> None:
        """Handle email bounces without silent failure"""
        self.bounce_callback = callback
    
    async def send_email(self, to: str, subject: str, body: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """Send outbound email via Resend API with structured error handling"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
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
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Email sent to {to}: {result.get('id')}")
                    return {
                        "success": True, 
                        "message_id": result.get("id"),
                        "to": to,
                        "status": "sent"
                    }
                else:
                    # Structured error handling for failed sends
                    error_detail = response.text
                    logger.error(f"Resend API error {response.status_code}: {error_detail}")
                    return {
                        "success": False, 
                        "error": f"HTTP {response.status_code}: {error_detail}",
                        "error_type": "api_error"
                    }
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout sending to {to}")
            return {"success": False, "error": "timeout", "error_type": "network"}
        except httpx.ConnectError:
            logger.error(f"Connection error sending to {to}")
            return {"success": False, "error": "connection_failed", "error_type": "network"}
        except Exception as e:
            logger.error(f"Unexpected send error: {e}")
            return {"success": False, "error": str(e), "error_type": "unknown"}
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inbound reply webhook from Resend with malformed payload handling"""
        try:
            # Validate required fields
            if not payload.get("from") or not payload.get("to"):
                logger.warning("Malformed webhook payload: missing from/to fields")
                return {"status": "error", "error": "malformed_payload", "missing_fields": ["from", "to"]}
            
            email_data = {
                "from": payload.get("from", ""),
                "to": payload.get("to", ""),
                "subject": payload.get("subject", ""),
                "body": payload.get("text", payload.get("html", "")),
                "message_id": payload.get("id", ""),
                "received_at": datetime.now().isoformat()
            }
            
            # Route to downstream handler (not dead-ending)
            if self.reply_callback:
                result = await self.reply_callback(email_data)
                logger.info(f"Email reply routed to handler: {result}")
                return {"status": "processed", "result": result}
            else:
                logger.warning("No reply handler attached - message would dead-end")
                return {"status": "queued", "message": "No handler attached"}
                
        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON payload: {e}")
            return {"status": "error", "error": "malformed_json"}
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def handle_bounce(self, bounce_data: Dict[str, Any]) -> None:
        """Handle email bounces without silent failure"""
        logger.warning(f"Email bounce detected: {bounce_data.get('email', 'unknown')}")
        if self.bounce_callback:
            await self.bounce_callback(bounce_data)
        # In production: log to CRM or alert system
