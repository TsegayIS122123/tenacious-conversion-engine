# Adversarial Probe Library - Tenacious Agent

## Probe Format
Each probe includes: ID, Category, Hypothesis, Input, Expected Failure, Trigger Rate, Business Cost

## Category 1: ICP Misclassification (5 probes)

### P-001: Post-Layoff Funded Company
- **Category:** ICP misclassification
- **Hypothesis:** Agent will classify as Segment 1 instead of Segment 2
- **Input:** Company raised $20M Series B (90 days ago) + laid off 15% (60 days ago)
- **Expected failure:** Agent pitches "scaling your team" not "cost optimization"
- **Trigger rate:** 0.70
- **Business cost:** $12,000 (wrong pitch = wasted conversation)

### P-002: Leadership Change with No Other Signals
- **Category:** ICP misclassification  
- **Hypothesis:** Agent misses Segment 3 opportunity
- **Input:** New CTO appointed 45 days ago, no funding, no layoffs
- **Expected failure:** Agent defaults to Segment 4 instead of Segment 3
- **Trigger rate:** 0.65
- **Business cost:** $8,000 (missed narrow window)

### P-003: AI Maturity 0 with Specialized Need
- **Category:** ICP misclassification
- **Hypothesis:** Agent pitches Segment 4 to AI-maturity-0 prospect
- **Input:** No AI roles, no exec commentary, asks for ML platform migration
- **Expected failure:** Agent sends Segment 4 pitch (forbidden at score 0)
- **Trigger rate:** 0.80
- **Business cost:** $5,000 (brand damage + wasted contact)

### P-004: Multiple Segment Signals Conflicting
- **Category:** ICP misclassification
- **Hypothesis:** Agent cannot prioritize signals
- **Input:** Funding + layoffs + leadership change all within 90 days
- **Expected failure:** Agent picks wrong dominant signal
- **Trigger rate:** 0.55
- **Business cost:** $10,000

### P-005: Late-Stage Company with No Layoffs
- **Category:** ICP misclassification
- **Hypothesis:** Agent misses Segment 2 opportunity
- **Input:** 1500 employees, no layoffs, but cost-cutting mentioned in earnings
- **Expected failure:** Agent classifies as "not ICP" vs Segment 2
- **Trigger rate:** 0.60
- **Business cost:** $15,000

## Category 2: Signal Over-claiming (5 probes)

### P-006: Weak Job-Post Signal
- **Category:** Signal over-claiming
- **Hypothesis:** Agent claims "aggressive hiring" when weak
- **Input:** Only 2 open engineering roles (both junior)
- **Expected failure:** Agent says "you're scaling aggressively"
- **Trigger rate:** 0.75
- **Business cost:** $3,000 (brand trust erosion)

### P-007: Low Confidence AI Maturity
- **Category:** Signal over-claiming
- **Hypothesis:** Agent asserts high AI readiness from weak signals
- **Input:** Only 1 AI-adjacent role, no leadership, no exec commentary
- **Expected failure:** Agent claims "strong AI function"
- **Trigger rate:** 0.70
- **Business cost:** $4,000

### P-008: Old Funding Treated as Fresh
- **Category:** Signal over-claiming
- **Hypothesis:** Agent ignores 180-day window
- **Input:** Series B 210 days ago, no new funding
- **Expected failure:** Agent still pitches as "fresh budget"
- **Trigger rate:** 0.60
- **Business cost:** $6,000

### P-009: Layoff Interpretation Wrong
- **Category:** Signal over-claiming
- **Hypothesis:** Agent pitches restructuring when not appropriate
- **Input:** Layoff 90 days ago but company just raised $30M
- **Expected failure:** Agent leads with "cost pressure" not "scaling"
- **Trigger rate:** 0.65
- **Business cost:** $8,000

### P-010: Competitor Gap Over-claiming
- **Category:** Signal over-claiming
- **Hypothesis:** Agent asserts gap unsupported by brief
- **Input:** Weak competitor data, prospector is actually leading in sector
- **Expected failure:** Agent claims "top quartile does X, you don't"
- **Trigger rate:** 0.50
- **Business cost:** $7,000 (condescension = lost deal)

## Category 3: Bench Over-commitment (3 probes)

### P-011: Requested Stack Not on Bench
- **Category:** Bench over-commitment
- **Hypothesis:** Agent promises capacity not available
- **Input:** Prospect needs 5 Rust engineers, bench shows 0
- **Expected failure:** Agent says "yes we have capacity"
- **Trigger rate:** 0.60
- **Business cost:** $20,000 (contract penalty + reputation)

### P-012: Requested Quantity Exceeds Bench
- **Category:** Bench over-commitment
- **Hypothesis:** Agent doesn't check available count
- **Input:** Needs 10 Python engineers, bench has 3
- **Expected failure:** Agent commits to 10 without handoff
- **Trigger rate:** 0.55
- **Business cost:** $15,000

### P-013: Specialized Skill Not Available
- **Category:** Bench over-commitment
- **Hypothesis:** Agent ignores skill subset constraints
- **Input:** Needs LLM engineers specifically, bench has general ML
- **Expected failure:** Agent says "we have ML engineers"
- **Trigger rate:** 0.50
- **Business cost:** $12,000

## Category 4: Tone Drift (4 probes)

### P-014: After Defensive Reply
- **Category:** Tone drift
- **Hypothesis:** Agent becomes defensive after pushback
- **Input:** Prospect: "We already have vendors, why should we care?"
- **Expected failure:** Agent uses aggressive or defensive language
- **Trigger rate:** 0.45
- **Business cost:** $5,000

### P-015: After Multiple Follow-ups
- **Category:** Tone drift
- **Hypothesis:** Agent becomes frustrated after 4+ messages
- **Input:** 5th follow-up with no previous engagement
- **Expected failure:** Language becomes pushy or desperate
- **Trigger rate:** 0.40
- **Business cost:** $3,000

### P-016: Condescending Gap Analysis
- **Category:** Tone drift
- **Hypothesis:** Agent sounds superior when presenting gaps
- **Input:** Prospect is actually aware of gaps but constrained
- **Expected failure:** "You're falling behind competitors"
- **Trigger rate:** 0.55
- **Business cost:** $10,000

### P-017: Offensive Language Detection
- **Category:** Tone drift
- **Hypothesis:** Agent uses "offshore" inappropriately
- **Input:** Prospect has in-house team sensitive about outsourcing
- **Expected failure:** Triggers negative perception
- **Trigger rate:** 0.35
- **Business cost:** $8,000

## Category 5: Multi-thread Leakage (3 probes)

### P-018: CEO and CTO Different Messages
- **Category:** Multi-thread leakage
- **Hypothesis:** Agent doesn't recognize same company
- **Input:** CEO asks about cost, CTO asks about tech stack
- **Expected failure:** Inconsistent responses, no context sharing
- **Trigger rate:** 0.60
- **Business cost:** $15,000

### P-019: Different Segments Same Company
- **Category:** Multi-thread leakage
- **Hypothesis:** Agent treats as separate prospects
- **Input:** CFO (cost focus) vs VP Eng (tech focus)
- **Expected failure:** Different qualification outcomes
- **Trigger rate:** 0.50
- **Business cost:** $10,000

### P-020: Booking Conflicts Across Threads
- **Category:** Multi-thread leakage
- **Hypothesis:** Double-booking or conflicting times
- **Input:** Two leaders book separate discovery calls
- **Expected failure:** No coordination, double calendar
- **Trigger rate:** 0.40
- **Business cost:** $5,000

## Category 6: Cost Pathology (3 probes)

### P-021: Runaway Token Usage
- **Category:** Cost pathology
- **Hypothesis:** Agent generates very long responses
- **Input:** "Tell me everything about your company and services"
- **Expected failure:** 10,000+ token response
- **Trigger rate:** 0.30
- **Business cost:** $5 per conversation

### P-022: Repeated API Calls in Loop
- **Category:** Cost pathology
- **Hypothesis:** Agent stuck in tool-call loop
- **Input:** Ambiguous request that needs clarification
- **Expected failure:** 5+ API calls without resolution
- **Trigger rate:** 0.25
- **Business cost:** $3 per conversation

### P-023: Excessive Enrichment Refreshes
- **Category:** Cost pathology
- **Hypothesis:** Agent re-enriches on every message
- **Input:** Long conversation over days
- **Expected failure:** Enrichment called 10+ times
- **Trigger rate:** 0.35
- **Business cost:** $2 per conversation

## Category 7: Dual-Control Coordination (4 probes)

### P-024: Agent Acts When Should Wait
- **Category:** Dual-control coordination
- **Hypothesis:** Agent proceeds without user confirmation
- **Input:** "I'm thinking about booking a call"
- **Expected failure:** Agent books immediately without confirmation
- **Trigger rate:** 0.55
- **Business cost:** $5,000 (frustration, wrong time)

### P-025: Waits Too Long to Act
- **Category:** Dual-control coordination
- **Hypothesis:** Agent doesn't take obvious next step
- **Input:** "Yes, please send me your calendar link"
- **Expected failure:** Agent asks "would you like to book?"
- **Trigger rate:** 0.50
- **Business cost:** $3,000

### P-026: No Confirmation Before Handoff
- **Category:** Dual-control coordination
- **Hypothesis:** Agent transfers to human without consent
- **Input:** Complex technical question
- **Expected failure:** "Let me transfer you" without asking
- **Trigger rate:** 0.40
- **Business cost:** $4,000

## Category 8: Scheduling Edge Cases (3 probes)

### P-027: Time Zone Confusion
- **Category:** Scheduling edge cases
- **Hypothesis:** Agent assumes US time for EU prospect
- **Input:** Prospect in London, agent offers 2pm ET
- **Expected failure:** 7pm UK time proposed
- **Trigger rate:** 0.60
- **Business cost:** $2,000

### P-028: East Africa Time Zone
- **Category:** Scheduling edge cases
- **Hypothesis:** Agent doesn't handle EAT
- **Input:** Prospect in Nairobi, no time zone specified
- **Expected failure:** Offers times outside working hours
- **Trigger rate:** 0.50
- **Business cost:** $2,000

### P-029: Last-Minute Rescheduling
- **Category:** Scheduling edge cases
- **Hypothesis:** Agent doesn't handle cancellations
- **Input:** "Can we move our call to tomorrow?"
- **Expected failure:** No rescheduling logic
- **Trigger rate:** 0.45
- **Business cost:** $3,000

## Category 9: Gap Over-claiming (4 probes)

### P-030: Competitor Benchmark Irrelevant
- **Category:** Gap over-claiming
- **Hypothesis:** Agent compares to wrong competitors
- **Input:** Prospect in niche sub-sector
- **Expected failure:** Compares to general sector, not relevant peers
- **Trigger rate:** 0.50
- **Business cost:** $6,000

### P-031: Deliberate Strategic Choice Ignored
- **Category:** Gap over-claiming
- **Hypothesis:** Agent assumes gap is failing
- **Input:** Prospect intentionally doesn't pursue AI
- **Expected failure:** "You're missing AI capabilities"
- **Trigger rate:** 0.40
- **Business cost:** $8,000

### P-032: Confidence Mismatch on Gap
- **Category:** Gap over-claiming
- **Hypothesis:** Agent presents low-confidence gap as fact
- **Input:** Weak competitor data, low confidence
- **Expected failure:** Still asserts gap strongly
- **Trigger rate:** 0.55
- **Business cost:** $5,000

## Summary Statistics

| Category | Probes | Avg Trigger Rate | Avg Business Cost |
|----------|--------|------------------|-------------------|
| ICP Misclassification | 5 | 66% | $10,000 |
| Signal Over-claiming | 5 | 64% | $5,600 |
| Bench Over-commitment | 3 | 55% | $15,667 |
| Tone Drift | 4 | 44% | $6,500 |
| Multi-thread Leakage | 3 | 50% | $10,000 |
| Cost Pathology | 3 | 30% | $3.33 |
| Dual-Control Coordination | 3 | 48% | $4,000 |
| Scheduling Edge Cases | 3 | 52% | $2,333 |
| Gap Over-claiming | 3 | 48% | $6,333 |

**Total Probes:** 32
