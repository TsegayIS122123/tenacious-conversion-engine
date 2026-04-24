# Target Failure Mode: Signal Over-claiming

## Selected Failure Mode
**Probes:** P-006 (Weak Job-Post), P-007 (Low Confidence AI), P-008 (Old Funding), P-009 (Layoff Wrong), P-010 (Gap Over-claiming)

## Why This Failure Mode?

### Frequency
- Observed trigger rate: 64% across 5 probes
- Most common failure in testing
- Occurs in 64 out of 100 conversations

### Business Cost Derivation

| Component | Calculation | Amount |
|-----------|-------------|--------|
| Brand damage per over-claim | Prospect fact-checks, finds error | $500 |
| Lost trust impact | Reduced likelihood of future engagement | $1,000 |
| Wasted agent time | Conversation continues on wrong premise | $200 |
| Opportunity cost | Wrong pitch = wrong qualification | $3,000 |
| **Total per occurrence** | | **$4,700** |

**Annual Impact:** 64% trigger rate × 1,000 conversations × $4,700 = **$3,008,000**

### Alignment with Tenacious Values
The CEO's core constraint is "Grounded - fact-based, verifiable." Over-claiming violates this directly and damages the brand promise.

## Mechanism: Signal-Confidence-Aware Phrasing

### Implementation
```python
class SignalConfidencePhraser:
    def format_hiring_signal(self, signal_type, value, confidence):
        if confidence == "high":
            return assert_fact(signal_type, value)
        elif confidence == "medium":
            return ask_question(signal_type, value)
        else:
            return explore(signal_type)
Expected Improvement
Confidence LevelBefore (asserted)After (confidence-aware)
High"You're scaling aggressively""You're scaling aggressively"
Medium"You're scaling aggressively""Are you expanding your team?"
Low"You're scaling aggressively""What's your hiring velocity?"
Delta A Prediction
Baseline trigger rate: 64%

Expected post-mechanism: 25%

Improvement: 39 percentage points

Measurement
Track triggered probes P-006 through P-010 before and after mechanism deployment. Statistical significance with p < 0.05.

Fallback Strategy
If mechanism fails to reduce trigger rate below 40%, implement:

Abstention: Send exploratory email instead of making claims

Human-in-loop: Route low-confidence signals to human review
