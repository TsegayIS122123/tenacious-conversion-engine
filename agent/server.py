"""FastAPI server for all webhooks - Render deployment"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime

# Import handlers
from agent.handlers.email_handler import ResendEmailHandler
from agent.handlers.sms_handler import AfricaTalkingSMSHandler
from agent.handlers.calendar_handler import CalComHandler
from agent.crm.hubspot_crm import HubSpotCRM
from agent.enrichment.signal_pipeline import SignalEnrichmentPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize
app = FastAPI(title="Tenacious Conversion Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers with API keys from env
EMAIL_HANDLER = ResendEmailHandler(api_key=os.getenv("RESEND_API_KEY", "test_key"))
SMS_HANDLER = AfricaTalkingSMSHandler(api_key=os.getenv("AFRICASTALKING_API_KEY", "test_key"))
CALENDAR_HANDLER = CalComHandler(
    api_key=os.getenv("CALCOM_API_KEY", "test_key"),
    event_type_id=int(os.getenv("CALCOM_EVENT_TYPE_ID", "123456"))
)
CRM = HubSpotCRM(api_key=os.getenv("HUBSPOT_API_KEY", "test_key"))
ENRICHMENT = SignalEnrichmentPipeline()

# Connect callbacks: Booking -> CRM update
async def booking_to_crm(email: str, booking_data: dict):
    await CRM.update_from_booking(email, booking_data)

CALENDAR_HANDLER.set_booking_callback(booking_to_crm)

# Connect email replies to enrichment
async def process_email_reply(email_data: dict):
    # Extract company from email
    company_name = email_data.get("from", "").split("@")[-1].split(".")[0]
    enrichment = await ENRICHMENT.enrich_company(company_name)
    await CRM.create_or_update_contact(email_data.get("from"), {
        "company_name": company_name,
        "icp_segment": enrichment["icp_segment"]["segment"],
        "ai_maturity_score": enrichment["ai_maturity"]["score"],
        "competitor_gap": enrichment["competitor_gap"]
    })
    return {"enriched": True}

EMAIL_HANDLER.set_reply_handler(process_email_reply)
SMS_HANDLER.set_reply_handler(lambda x: {"routed": True})

# ============ ENDPOINTS ============

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/webhooks/email")
async def email_webhook(request: Request):
    payload = await request.json()
    result = await EMAIL_HANDLER.handle_webhook(payload)
    return result

@app.post("/webhooks/sms")
async def sms_webhook(request: Request):
    form = await request.form()
    result = await SMS_HANDLER.handle_inbound(dict(form))
    return result

@app.post("/webhooks/calcom")
async def calcom_webhook(request: Request):
    payload = await request.json()
    result = await CALENDAR_HANDLER.handle_webhook(payload)
    return result

@app.post("/send/email")
async def send_test_email(to: str, subject: str, body: str):
    result = await EMAIL_HANDLER.send_email(to, subject, body)
    return result

@app.post("/enrich/{company}")
async def enrich_company(company: str):
    result = await ENRICHMENT.enrich_company(company)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
