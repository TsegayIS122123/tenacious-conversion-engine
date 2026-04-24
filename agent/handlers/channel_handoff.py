"""Centralized Channel Handoff Logic - State Machine for Email -> SMS -> Voice"""

import logging
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    VOICE = "voice"

class ChannelHandoffStateMachine:
    """Centralized state machine for channel handoff - not scattered across handlers"""
    
    def __init__(self):
        self.conversation_state = {}  # prospect_id -> state
    
    def get_current_channel(self, prospect_id: str) -> Channel:
        """Determine current active channel for prospect"""
        state = self.conversation_state.get(prospect_id, {})
        return Channel(state.get("current_channel", "email"))
    
    def should_escalate_to_sms(self, prospect: Dict[str, Any]) -> bool:
        """Rule: SMS only after email reply and within scheduling context"""
        conditions = {
            "has_replied_to_email": prospect.get("replied_to_email", False),
            "prefers_sms": prospect.get("prefers_sms", False),
            "is_scheduling_context": prospect.get("last_message_type") == "scheduling_request",
            "not_already_on_sms": self.get_current_channel(prospect.get("id")) != Channel.SMS
        }
        return all([
            conditions["has_replied_to_email"],
            (conditions["prefers_sms"] or conditions["is_scheduling_context"]),
            conditions["not_already_on_sms"]
        ])
    
    def should_escalate_to_voice(self, prospect: Dict[str, Any]) -> bool:
        """Rule: Voice only after SMS engagement and explicit request"""
        conditions = {
            "sms_exchanged": prospect.get("sms_exchanged", False),
            "requested_call": prospect.get("requested_voice_call", False),
            "not_already_on_voice": self.get_current_channel(prospect.get("id")) != Channel.VOICE
        }
        return all(conditions.values())
    
    def transition_channel(self, prospect_id: str, new_channel: Channel, reason: str) -> None:
        """Centralized channel transition logic"""
        if prospect_id not in self.conversation_state:
            self.conversation_state[prospect_id] = {}
        
        old_channel = self.conversation_state[prospect_id].get("current_channel", "email")
        self.conversation_state[prospect_id]["current_channel"] = new_channel.value
        self.conversation_state[prospect_id]["last_transition_at"] = datetime.now().isoformat()
        self.conversation_state[prospect_id]["transition_reason"] = reason
        
        logger.info(f"Channel transition: {prospect_id} {old_channel} -> {new_channel.value} ({reason})")
    
    def record_email_reply(self, prospect_id: str) -> None:
        """Record that prospect replied to email (enables SMS gate)"""
        if prospect_id not in self.conversation_state:
            self.conversation_state[prospect_id] = {}
        self.conversation_state[prospect_id]["replied_to_email"] = True
        self.conversation_state[prospect_id]["first_reply_at"] = datetime.now().isoformat()
        logger.info(f"Email reply recorded for {prospect_id} - SMS now available")
    
    def record_sms_sent(self, prospect_id: str) -> None:
        """Record SMS sent (for voice escalation)"""
        if prospect_id not in self.conversation_state:
            self.conversation_state[prospect_id] = {}
        self.conversation_state[prospect_id]["sms_exchanged"] = True
    
    def get_channel_recommendation(self, prospect: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend next channel based on state machine rules"""
        current = self.get_current_channel(prospect.get("id"))
        
        if current == Channel.EMAIL:
            if self.should_escalate_to_sms(prospect):
                return {"recommend": "sms", "reason": "warm_lead_scheduling", "priority": "high"}
            return {"recommend": "email", "reason": "primary_channel", "priority": "normal"}
        
        elif current == Channel.SMS:
            if self.should_escalate_to_voice(prospect):
                return {"recommend": "voice", "reason": "booking_confirmation", "priority": "high"}
            return {"recommend": "sms", "reason": "scheduling_coordination", "priority": "normal"}
        
        else:
            return {"recommend": "voice", "reason": "discovery_call", "priority": "high"}

# Global instance for centralized access
channel_handoff = ChannelHandoffStateMachine()
