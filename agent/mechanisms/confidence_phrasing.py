"""Signal-Confidence-Aware Phrasing Mechanism

This mechanism adjusts agent language based on signal confidence levels.
Low confidence + high score = ask, not assert.
"""

from typing import Dict, Any, List
from enum import Enum

class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SignalConfidencePhraser:
    """Adjusts language based on signal confidence"""
    
    def __init__(self):
        self.confidence_thresholds = {
            "high": 0.7,
            "medium": 0.4,
            "low": 0.0
        }
    
    def format_hiring_signal(self, signal_type: str, value: Any, confidence: str) -> str:
        """Format a hiring signal with confidence-aware phrasing"""
        
        if confidence == "high":
            return self._assertive_phrasing(signal_type, value)
        elif confidence == "medium":
            return self._balanced_phrasing(signal_type, value)
        else:
            return self._exploratory_phrasing(signal_type, value)
    
    def _assertive_phrasing(self, signal_type: str, value: Any) -> str:
        """High confidence - can assert facts"""
        templates = {
            "job_velocity": f"Your engineering roles have increased {value}x in 60 days - you're scaling aggressively.",
            "funding": f"You closed ${value}M in funding recently - fresh budget for scaling.",
            "ai_maturity": f"Your AI function is mature, with {value} dedicated roles.",
            "layoffs": f"Your recent restructuring indicates cost optimization focus.",
            "leadership": f"New {value} leadership creates natural vendor reassessment window."
        }
        return templates.get(signal_type, f"We identified {value} (high confidence)")
    
    def _balanced_phrasing(self, signal_type: str, value: Any) -> str:
        """Medium confidence - state what was found, not what it means"""
        templates = {
            "job_velocity": f"We noticed {value} open engineering positions. Are you expanding your team?",
            "funding": f"Our data shows a funding event. Is budget available for new initiatives?",
            "ai_maturity": f"We found signals of AI activity. How mature is your AI function?",
            "layoffs": f"Public data indicates a recent layoff. Is cost optimization a priority?",
            "leadership": f"We detected a leadership change. Are you reviewing vendor relationships?"
        }
        return templates.get(signal_type, f"We found {value} - would you like to discuss?")
    
    def _exploratory_phrasing(self, signal_type: str, value: Any) -> str:
        """Low confidence - ask, don't assert"""
        templates = {
            "job_velocity": f"We see some open roles. What's your hiring velocity like right now?",
            "funding": f"Have you had any recent funding events we should know about?",
            "ai_maturity": f"Are you investing in AI capabilities at this stage?",
            "layoffs": f"Has your team size changed recently?",
            "leadership": f"Have there been recent leadership changes on your engineering team?"
        }
        return templates.get(signal_type, f"Could you share more about {signal_type}?")
    
    def format_ai_maturity_score(self, score: int, confidence: str) -> str:
        """Format AI maturity score with appropriate certainty"""
        
        if confidence == "high":
            if score >= 2:
                return f"Your AI maturity score is {score}/3 - you have an active AI function."
            else:
                return f"Your AI maturity score is {score}/3 - early stage is normal."
        elif confidence == "medium":
            return f"Based on available signals, your AI maturity appears to be {score}/3. Does that match your internal assessment?"
        else:
            return f"Our signals suggest AI maturity around {score}/3, but we'd love to hear your actual priorities."
    
    def format_competitor_gap(self, gap: str, confidence: str) -> str:
        """Format competitor gap without sounding condescending"""
        
        if confidence == "high":
            return f"Here's an observation: {gap}"
        elif confidence == "medium":
            return f"One area worth exploring: {gap}"
        else:
            return f"Based on limited public data, you might want to consider {gap}. But we could be wrong - what's your perspective?"
    
    def should_abstain(self, signal_confidence: Dict[str, str]) -> bool:
        """Determine if agent should abstain from making claims"""
        low_confidence_signals = [k for k, v in signal_confidence.items() if v == "low"]
        
        # If more than 2 signals are low confidence, send exploratory email
        return len(low_confidence_signals) > 2
    
    def generate_exploratory_email(self, company_name: str) -> str:
        """Generate exploratory email when confidence is too low for segment-specific pitch"""
        return f"""Subject: Quick question about {company_name}

Hi there,

Our research on {company_name} has revealed some interesting signals, but we want to be honest about the limitations of public data.

Rather than make claims we can't fully verify, we'd rather ask: what are your current priorities for engineering and AI?

If there's a fit, we can share how we've helped similar companies. If not, no problem - we appreciate your time.

Best,
Tenacious Research
"""
