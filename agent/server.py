"""FastAPI Server - Centralized Wiring of All Integrations"""

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime

from agent.handlers.email_handler import ResendEmailHandler
from agent.handlers.sms_handler import AfricaTalkingSMSHandler
from agent.handlers.calendar_handler import CalComHandler
from agent.handlers.channel_handoff import channel_handoff
from agent.crm.hubspot_crm import HubSpotCRM
from agent.enrichment.signal_pipeline import SignalEnrichmentPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize all integrations
EMAIL_HANDLER = ResendEmailHandler(
    api_key=os.getenv("RESEND_API_KEY", "test_key"),
    from_email=os.getenv("RESEND_FROM_EMAIL", "hello@tenacious.com")
)

SMS_HANDLER = AfricaTalkingSMSHandler(
    api_key=os.getenv("AFRICASTALKING_API_KEY", "test_key"),
    username=os.getenv("AFRICASTALKING_USERNAME", "sandbox"),
    short_code=os.getenv("AFRICASTALKING_SHORT_CODE", "12345")
)

CALENDAR_HANDLER = CalComHandler(
    api_key=os.getenv("CALCOM_API_KEY", "test_key"),
    event_type_id=int(os.getenv("CALCOM_EVENT_TYPE_ID", "123456"))
)

CRM = HubSpotCRM(api_key=os.getenv("HUBSPOT_API_KEY", "test_key"))
ENRICHMENT = SignalEnrichmentPipeline()

# Connect callbacks (centralized wiring)
async def booking_to_crm(email: str, booking_data: dict):
    """Callback: Cal.com booking -> HubSpot update"""
    await CRM.update_from_booking(email, booking_data)

CALENDAR_HANDLER.set_booking_callback(booking_to_crm)

async def email_reply_to_crm(email_data: dict):
    """Callback: Email reply -> enrichment + CRM update"""
    company_name = email_data.get("from", "").split("@")[-1].split(".")[0]
    enrichment = await ENRICHMENT.enrich_company(company_name)
    
    # Record email reply in channel handoff (enables SMS)
    channel_handoff.record_email_reply(email_data.get("prospect_id", company_name))
    
    await CRM.create_or_update_contact(email_data.get("from"), {
        "company_name": company_name,
        "icp_segment": enrichment.get("icp_segment", {}).get("segment"),
        "ai_maturity_score": enrichment.get("ai_maturity", {}).get("score"),
        "competitor_gap": enrichment.get("competitor_gap", {})
    })
    return {"enriched": True}

EMAIL_HANDLER.set_reply_handler(email_reply_to_crm)
SMS_HANDLER.set_reply_handler(lambda x: {"routed": True})

# FastAPI App
app = FastAPI(title="Tenacious Conversion Engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "integrations": {
            "email": EMAIL_HANDLER.api_key != "test_key",
            "sms": SMS_HANDLER.api_key != "test_key",
            "crm": CRM.api_key != "test_key",
            "calendar": CALENDAR_HANDLER.api_key != "test_key"
        }
    }

@app.post("/webhooks/email")
async def email_webhook(request: Request):
    payload = await request.json()
    return await EMAIL_HANDLER.handle_webhook(payload)

@app.post("/webhooks/sms")
async def sms_webhook(request: Request):
    form = await request.form()
    return await SMS_HANDLER.handle_inbound(dict(form))

@app.post("/webhooks/calcom")
async def calcom_webhook(request: Request):
    payload = await request.json()
    return await CALENDAR_HANDLER.handle_confirmation(payload)

@app.post("/send/email")
async def send_email(to: str, subject: str, body: str):
    return await EMAIL_HANDLER.send_email(to, subject, body)

@app.post("/send/sms")
async def send_sms(to: str, message: str, prospect_id: str):
    prospect = {"id": prospect_id, "replied_to_email": True}
    return await SMS_HANDLER.send_sms(to, message, prospect)

@app.post("/booking/create")
async def create_booking(email: str, name: str):
    return await CALENDAR_HANDLER.generate_booking_link(email, name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
