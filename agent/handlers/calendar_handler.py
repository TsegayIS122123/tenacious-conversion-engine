"""Cal.com booking handler - callable from agent"""

import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CalComHandler:
    """Handles Cal.com booking creation"""
    
    def __init__(self, api_key: str, event_type_id: int, base_url: str = "https://api.cal.com/v1"):
        self.api_key = api_key
        self.event_type_id = event_type_id
        self.base_url = base_url
        self.booking_callback = None  # To trigger HubSpot update
        
    def set_booking_callback(self, callback):
        """Link to CRM for post-booking updates"""
        self.booking_callback = callback
    
    async def create_booking(self, email: str, name: str, start_time: Optional[str] = None) -> Dict[str, Any]:
        """Create Cal.com booking - callable from agent codebase"""
        try:
            booking_payload = {
                "eventTypeId": self.event_type_id,
                "attendee": {
                    "email": email,
                    "name": name,
                    "timeZone": "UTC"
                },
                "start": start_time or datetime.now().isoformat(),
                "metadata": {
                    "source": "tenacious_agent",
                    "created_at": datetime.now().isoformat()
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/bookings",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=booking_payload,
                    timeout=30.0
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    booking_data = response.json()
                    logger.info(f"Booking created for {email}: {booking_data.get('uid')}")
                    
                    # Trigger HubSpot update via callback if attached
                    if self.booking_callback:
                        await self.booking_callback(email, {
                            "booking_id": booking_data.get("uid"),
                            "start_time": start_time,
                            "booking_url": booking_data.get("bookingUrl", "")
                        })
                    
                    return {"success": True, "booking_id": booking_data.get("uid"), "url": booking_data.get("bookingUrl")}
                else:
                    logger.error(f"Booking failed: {response.text}")
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Booking error: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Cal.com webhook events"""
        try:
            event = payload.get("type")
            booking = payload.get("payload", {})
            
            if event == "BOOKING_CREATED":
                attendee = booking.get("attendees", [{}])[0]
                email = attendee.get("email")
                
                # Trigger HubSpot update via callback
                if self.booking_callback:
                    await self.booking_callback(email, {
                        "booking_id": booking.get("uid"),
                        "start_time": booking.get("startTime"),
                        "status": "completed"
                    })
                
                return {"status": "processed", "event": event}
            
            return {"status": "ignored", "event": event}
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return {"status": "error", "error": str(e)}
