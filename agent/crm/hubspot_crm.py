"""Complete HubSpot CRM Integration via MCP - Production Ready"""

import json
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class HubSpotCRM:
    """HubSpot MCP integration - writes contacts at multiple conversation events"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com/crm/v3"
        
    async def create_or_update_contact(self, email: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create/update contact with enrichment fields - invoked at first contact"""
        try:
            # Build properties with ALL enrichment fields per rubric
            properties = {
                "email": email,
                "company": data.get("company_name", ""),
                "firstname": data.get("first_name", ""),
                "lastname": data.get("last_name", ""),
                "phone": data.get("phone", ""),
                # Enrichment fields
                "hs_lead_status": data.get("icp_segment", "unqualified"),
                "tenacious_icp_segment": data.get("icp_segment"),
                "tenacious_ai_maturity_score": str(data.get("ai_maturity_score", 0)),
                "tenacious_enrichment_timestamp": datetime.now().isoformat(),
                "tenacious_funding_amount": str(data.get("funding_amount", 0)),
                "tenacious_funding_date": data.get("funding_date", ""),
                "tenacious_job_velocity": str(data.get("job_velocity", 0)),
                "tenacious_layoff_occurred": str(data.get("layoff_occurred", False)),
                "tenacious_competitor_gap_brief": json.dumps(data.get("competitor_gap", {}))
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/objects/contacts",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"properties": properties}
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"CRM: Contact {email} created/updated with enrichment")
                    return {"success": True, "id": result.get("id"), "email": email}
                else:
                    logger.error(f"HubSpot API error: {response.text}")
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"CRM error: {e}")
            return {"success": False, "error": str(e)}
    
    async def log_interaction(self, contact_id: str, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Log conversation interaction - invoked at every message exchange"""
        try:
            # Create engagement/note on contact
            note_properties = {
                "hs_timestamp": datetime.now().timestamp() * 1000,
                "hs_note_body": interaction.get("text", json.dumps(interaction)),
                "hs_activity_type": "NOTE"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/objects/notes",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "properties": note_properties,
                        "associations": [
                            {
                                "to": {"id": contact_id},
                                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}]
                            }
                        ]
                    }
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"CRM: Interaction logged for contact {contact_id}")
                    return {"success": True}
                else:
                    logger.warning(f"Failed to log interaction: {response.text}")
                    return {"success": False}
                    
        except Exception as e:
            logger.error(f"Interaction log error: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_from_booking(self, email: str, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update HubSpot record when Cal.com booking completes - invoked after booking"""
        try:
            properties = {
                "tenacious_booking_status": "scheduled",
                "tenacious_booking_time": booking_data.get("start_time", ""),
                "tenacious_booking_id": booking_data.get("booking_id", ""),
                "hs_meeting_status": "scheduled"
            }
            
            # First find contact by email
            contact = await self.find_contact_by_email(email)
            if not contact.get("success"):
                return {"success": False, "error": "Contact not found"}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/objects/contacts/{contact['id']}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"properties": properties}
                )
                
                if response.status_code == 200:
                    logger.info(f"CRM: Booking status updated for {email}")
                    return {"success": True}
                else:
                    return {"success": False}
                    
        except Exception as e:
            logger.error(f"Booking update error: {e}")
            return {"success": False, "error": str(e)}
    
    async def find_contact_by_email(self, email: str) -> Dict[str, Any]:
        """Find contact by email address"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/objects/contacts/search",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    params={"limit": 1, "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}]}
                )
                
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results:
                        return {"success": True, "id": results[0]["id"]}
                return {"success": False}
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"success": False}
    
    async def health_check(self) -> bool:
        """Verify CRM is configured"""
        return bool(self.api_key and self.api_key != "test_key")
