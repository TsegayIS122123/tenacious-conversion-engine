"""Complete Cal.com Integration - Referenced from Email and SMS Handlers"""

import logging
import httpx
from typing import Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class CalComHandler:
    """Handles Cal.com booking - referenced from email AND SMS handler code paths"""
    
    def __init__(self, api_key: str, event_type_id: int, base_url: str = "https://api.cal.com/v1"):
        self.api_key = api_key
        self.event_type_id = event_type_id
        self.base_url = base_url
        self.booking_callback = None  # Triggers HubSpot update
        
    def set_booking_callback(self, callback: Callable) -> None:
        """Link to CRM for post-booking updates"""
        self.booking_callback = callback
        logger.info("Booking callback attached to Cal.com integration")
    
    async def generate_booking_link(self, email: str, name: str, start_time: Optional[str] = None) -> Dict[str, Any]:
        """Generate booking link - callable from email AND SMS handlers"""
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
                    "channel": "webhook",
                    "created_at": datetime.now().isoformat()
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/bookings",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=booking_payload
                )
                
                if response.status_code in [200, 201]:
                    booking_data = response.json()
                    logger.info(f"Booking created for {email}: {booking_data.get('uid')}")
                    
                    # Trigger HubSpot update via callback (booking -> CRM)
                    if self.booking_callback:
                        await self.booking_callback(email, {
                            "booking_id": booking_data.get("uid"),
                            "start_time": start_time,
                            "booking_url": booking_data.get("bookingUrl", "")
                        })
                    
                    return {
                        "success": True,
                        "booking_id": booking_data.get("uid"),
                        "booking_url": booking_data.get("bookingUrl"),
                        "message": "Booking link generated"
                    }
                else:
                    logger.error(f"Cal.com API error: {response.text}")
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Booking generation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_confirmation(self, webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle booking confirmation webhook"""
        try:
            event_type = webhook_payload.get("type")
            booking = webhook_payload.get("payload", {})
            
            if event_type == "BOOKING_CREATED":
                attendee = booking.get("attendees", [{}])[0]
                email = attendee.get("email")
                
                # Trigger HubSpot update via callback
                if self.booking_callback:
                    await self.booking_callback(email, {
                        "booking_id": booking.get("uid"),
                        "start_time": booking.get("startTime"),
                        "status": "confirmed"
                    })
                
                logger.info(f"Booking confirmed for {email}")
                return {"status": "confirmed", "booking_id": booking.get("uid")}
            
            return {"status": "ignored", "event_type": event_type}
            
        except Exception as e:
            logger.error(f"Confirmation handling error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def health_check(self) -> bool:
        """Verify Cal.com is configured"""
        return bool(self.api_key and self.api_key != "test_key")
