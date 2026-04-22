"""Main Tenacious Agent orchestrator."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from agent.config import settings
from agent.enrichment.pipeline import EnrichmentPipeline
from agent.handlers.email import EmailHandler
from agent.handlers.sms import SMSHandler
from agent.crm.hubspot import HubSpotCRM

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TenaciousAgent:
    """Main orchestration class for Tenacious Conversion Engine."""
    
    def __init__(self):
        """Initialize agent with all handlers."""
        self.enrichment = EnrichmentPipeline()
        self.email_handler = EmailHandler()
        self.sms_handler = SMSHandler()
        self.crm = HubSpotCRM()
        
        logger.info("Tenacious Agent initialized (Development Mode: %s)", 
                   settings.is_development)
    
    async def process_inbound_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process inbound email reply."""
        logger.info("Processing inbound email from %s", email_data.get('from_email'))
        
        # Extract prospect identifier
        prospect_id = email_data.get('prospect_id')
        
        # Load or create prospect in CRM
        prospect = await self.crm.get_or_create_prospect(prospect_id, email_data)
        
        # Run enrichment if not already done
        if not prospect.get('enriched_at'):
            brief = await self.enrichment.enrich_company(prospect['company_name'])
            await self.crm.update_with_enrichment(prospect['id'], brief)
        else:
            brief = prospect.get('enrichment_brief', {})
        
        # Generate response using LLM
        response = await self._generate_response(
            prospect=prospect,
            brief=brief,
            user_message=email_data.get('body'),
            conversation_history=prospect.get('history', [])
        )
        
        # Send reply
        await self.email_handler.send_reply(
            to_email=prospect['email'],
            subject=self._generate_subject(prospect),
            body=response
        )
        
        # Log to CRM
        await self.crm.log_interaction(prospect['id'], response)
        
        return {
            'status': 'success',
            'prospect_id': prospect['id'],
            'response_sent': True
        }
    
    async def _generate_response(self, prospect, brief, user_message, conversation_history):
        """Generate agent response using LLM."""
        # Placeholder - will implement with actual LLM call
        # This uses OpenRouter via LangChain
        from langchain_openai import ChatOpenAI
        from langchain.schema import SystemMessage, HumanMessage
        
        llm = ChatOpenAI(
            base_url=settings.openrouter.base_url,
            api_key=settings.openrouter.api_key.get_secret_value(),
            model=settings.openrouter.model_dev,
            temperature=settings.openrouter.temperature
        )
        
        system_prompt = self._build_system_prompt(brief)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await llm.ainvoke(messages)
        return response.content
    
    def _build_system_prompt(self, brief: Dict[str, Any]) -> str:
        """Build system prompt with Tenacious voice and brief."""
        return f"""You are a sales development agent for Tenacious Consulting, a B2B talent outsourcing and consulting firm.

Hiring Signal Brief for this prospect:
{brief}

Tenacious Voice Guidelines:
- Professional, consultative, not pushy
- Ground every claim in the hiring signal brief
- Never over-claim or assert confidence on weak signals
- Focus on value: "here's what we've seen work for companies like yours"

Current ICP segments to consider:
1. Recently funded Series A/B (fresh budget, scaling need)
2. Mid-market restructuring (cost pressure, post-layoff)
3. Leadership transition (new CTO/VP Eng, vendor reassessment)
4. Specialized capability gap (specific AI/ML need)

Respond helpfully, ask qualifying questions, and work toward booking a discovery call.
"""
    
    def _generate_subject(self, prospect: Dict[str, Any]) -> str:
        """Generate email subject line."""
        # Simple placeholder
        return f"Re: {prospect.get('company_name', 'Tenacious')} - follow up"
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all integrations."""
        checks = {
            'email': await self.email_handler.health_check(),
            'sms': await self.sms_handler.health_check(),
            'crm': await self.crm.health_check(),
            'enrichment': await self.enrichment.health_check()
        }
        
        return {
            'status': 'healthy' if all(checks.values()) else 'degraded',
            'checks': checks,
            'mode': 'development' if settings.is_development else 'production'
        }
