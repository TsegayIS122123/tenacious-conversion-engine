# -*- coding: utf-8 -*-
"""FastAPI backend for Tenacious Agent"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tenacious Conversion Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": True,
        "services": {
            "email": "configured",
            "sms": "configured",
            "crm": "stub",
            "calendar": "stub"
        }
    }

@app.post("/webhooks/email")
async def email_webhook(request: Request):
    try:
        body = await request.json()
        logger.info(f"Email received from: {body.get('from', 'unknown')}")
        return {"status": "received", "message": "Email processed"}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/webhooks/sms")
async def sms_webhook(request: Request):
    try:
        form_data = await request.form()
        logger.info(f"SMS from: {form_data.get('from', 'unknown')}")
        return {"status": "received", "message": "SMS processed"}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/webhooks/calcom")
async def calcom_webhook(request: Request):
    try:
        body = await request.json()
        logger.info(f"Booking received: {body.get('title', 'unknown')}")
        return {"status": "recorded", "message": "Booking recorded"}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
