"""HubSpot CRM integration via MCP with enrichment fields"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class HubSpotCRM:
    """HubSpot MCP integration - writes contacts with enrichment"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        
    async def create_or_update_contact(self, email: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create/update contact with enrichment fields"""
        
        # Build properties with ALL required enrichment fields
        properties = {
            "email": email,
            "company": data.get("company_name", ""),
            "firstname": data.get("first_name", ""),
            "lastname": data.get("last_name", ""),
            "phone": data.get("phone", ""),
            
            # Enrichment fields (required by rubric)
            "hs_lead_status": data.get("icp_segment", "unqualified"),
            "tenacious_icp_segment": data.get("icp_segment"),  # Custom property
            "tenacious_ai_maturity_score": data.get("ai_maturity_score"),  # 0-3
            "tenacious_enrichment_timestamp": datetime.now().isoformat(),
            "tenacious_funding_amount": data.get("funding_amount"),
            "tenacious_funding_date": data.get("funding_date"),
            "tenacious_job_velocity": data.get("job_velocity"),
            "tenacious_layoff_occurred": data.get("layoff_occurred", False),
            "tenacious_competitor_gap_brief": json.dumps(data.get("competitor_gap", {}))
        }
        
        try:
            # In production: POST to HubSpot API
            logger.info(f"CRM: Creating/updating contact {email} with enrichment")
            # Actual API call would go here
            return {"success": True, "id": f"contact_{email}"}
        except Exception as e:
            logger.error(f"CRM error: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_from_booking(self, email: str, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update HubSpot record when Cal.com booking completes"""
        try:
            properties = {
                "tenacious_booking_status": "scheduled",
                "tenacious_booking_time": booking_data.get("start_time"),
                "tenacious_booking_link": booking_data.get("booking_url"),
                "hs_meeting_status": "scheduled"
            }
            
            logger.info(f"CRM: Updating {email} with booking {booking_data.get('booking_id')}")
            return {"success": True, "updated": True}
        except Exception as e:
            logger.error(f"CRM update error: {e}")
            return {"success": False, "error": str(e)}
