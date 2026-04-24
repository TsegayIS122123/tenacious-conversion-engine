"""Complete AI Maturity Scoring System - All 6 Signal Inputs"""

import logging
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class SignalWeight(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class AIInputSignals:
    """All 6 required signal inputs per rubric"""
    # High weight signals
    ai_adjacent_open_roles: int = 0  # ML engineer, applied scientist, LLM engineer, AI product manager
    named_ai_ml_leadership: bool = False  # Head of AI, VP Data, Chief Scientist
    
    # Medium weight signals
    public_github_org_activity: bool = False  # Recent commits on AI repos
    executive_commentary: bool = False  # CEO/CTO naming AI as strategic
    
    # Low weight signals
    modern_data_ml_stack: bool = False  # dbt, Snowflake, Databricks, Weights & Biases
    strategic_communications: bool = False  # Annual reports, fundraising press positioning AI

class AIMaturityScorer:
    """Returns integer 0-3 with per-signal justification and confidence field"""
    
    # Weights matching challenge specification
    SIGNAL_WEIGHTS = {
        "ai_adjacent_open_roles": SignalWeight.HIGH,
        "named_ai_ml_leadership": SignalWeight.HIGH,
        "public_github_org_activity": SignalWeight.MEDIUM,
        "executive_commentary": SignalWeight.MEDIUM,
        "modern_data_ml_stack": SignalWeight.LOW,
        "strategic_communications": SignalWeight.LOW
    }
    
    # Point values per weight (rubric-aligned)
    WEIGHT_POINTS = {
        SignalWeight.HIGH: 2,
        SignalWeight.MEDIUM: 1,
        SignalWeight.LOW: 0.5
    }
    
    def score(self, signals: AIInputSignals) -> Dict[str, Any]:
        """Return score 0-3 with justification and confidence"""
        
        points = 0.0
        justifications = []
        high_weight_signals_present = 0
        total_high_weight = 0
        
        # AI adjacent open roles (HIGH weight)
        if signals.ai_adjacent_open_roles >= 5:
            points += 2
            justifications.append(f"AI-adjacent open roles: {signals.ai_adjacent_open_roles} (HIGH weight, +2)")
            high_weight_signals_present += 1
        elif signals.ai_adjacent_open_roles >= 2:
            points += 1
            justifications.append(f"AI-adjacent open roles: {signals.ai_adjacent_open_roles} (HIGH weight, +1)")
            high_weight_signals_present += 1
        elif signals.ai_adjacent_open_roles >= 1:
            points += 0.5
            justifications.append(f"AI-adjacent open roles: {signals.ai_adjacent_open_roles} (HIGH weight, +0.5)")
            high_weight_signals_present += 1
        else:
            justifications.append("AI-adjacent open roles: none found (HIGH weight, 0)")
        total_high_weight += 1
        
        # Named AI/ML leadership (HIGH weight)
        if signals.named_ai_ml_leadership:
            points += 2
            justifications.append("Named AI/ML leadership present (HIGH weight, +2)")
            high_weight_signals_present += 1
        else:
            justifications.append("Named AI/ML leadership: not found (HIGH weight, 0)")
        total_high_weight += 1
        
        # Public GitHub activity (MEDIUM weight)
        if signals.public_github_org_activity:
            points += 1
            justifications.append("Public GitHub AI activity present (MEDIUM weight, +1)")
        else:
            justifications.append("Public GitHub AI activity: not detected (MEDIUM weight, 0 - absence not proof)")
        
        # Executive commentary (MEDIUM weight)
        if signals.executive_commentary:
            points += 1
            justifications.append("Executive AI commentary present (MEDIUM weight, +1)")
        else:
            justifications.append("Executive AI commentary: not found (MEDIUM weight, 0)")
        
        # Modern data/ML stack (LOW weight)
        if signals.modern_data_ml_stack:
            points += 0.5
            justifications.append("Modern data/ML stack detected (LOW weight, +0.5)")
        else:
            justifications.append("Modern data/ML stack: not detected (LOW weight, 0)")
        
        # Strategic communications (LOW weight)
        if signals.strategic_communications:
            points += 0.5
            justifications.append("Strategic AI communications present (LOW weight, +0.5)")
        else:
            justifications.append("Strategic AI communications: not found (LOW weight, 0)")
        
        # Convert points to 0-3 integer score
        if points >= 5:
            score = 3
        elif points >= 3:
            score = 2
        elif points >= 1:
            score = 1
        else:
            score = 0
        
        # Calculate confidence field (separate from score)
        # High confidence: 2+ high-weight signals present
        # Medium confidence: 1 high-weight signal with medium-weight support
        # Low confidence: 0 high-weight signals or only low-weight signals
        if high_weight_signals_present >= 2:
            confidence = "high"
        elif high_weight_signals_present == 1 and points >= 2:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Silent company handling
        silent_company_note = ""
        if points == 0:
            silent_company_note = "No public AI signals detected. Note: Absence of public signals does not prove absence of AI activity - many companies keep AI work private."
        
        return {
            "score": score,
            "confidence": confidence,
            "total_points": round(points, 1),
            "justifications": justifications,
            "silent_company_note": silent_company_note,
            "signal_summary": {
                "ai_adjacent_open_roles": signals.ai_adjacent_open_roles,
                "named_ai_ml_leadership": signals.named_ai_ml_leadership,
                "public_github_org_activity": signals.public_github_org_activity,
                "executive_commentary": signals.executive_commentary,
                "modern_data_ml_stack": signals.modern_data_ml_stack,
                "strategic_communications": signals.strategic_communications
            }
        }

# Example usage for testing
if __name__ == "__main__":
    scorer = AIMaturityScorer()
    
    # Test case: Strong AI company
    strong = AIInputSignals(
        ai_adjacent_open_roles=8,
        named_ai_ml_leadership=True,
        public_github_org_activity=True,
        executive_commentary=True,
        modern_data_ml_stack=True,
        strategic_communications=True
    )
    print("Strong AI company:", scorer.score(strong))
    
    # Test case: Silent company
    silent = AIInputSignals()
    print("Silent company:", scorer.score(silent))
