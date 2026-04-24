# Failure Taxonomy - Tenacious Agent

## Overview
Analysis of 32 adversarial probes across 9 categories with observed trigger rates and business impact.

## Category 1: ICP Misclassification (5 probes, 66% avg trigger rate)

### Observed Patterns
- Agent over-indexes on funding signal when multiple signals conflict
- Leadership change signal often missed without supporting signals
- Segment 4 incorrectly pitched to AI-maturity-0 prospects

### Root Causes
- Signal weighting logic favors funding > leadership > layoffs
- No conflict resolution when signals point to different segments
- AI maturity score not checked before Segment 4 pitch

### Business Impact: $50,000 total across category

## Category 2: Signal Over-claiming (5 probes, 64% avg trigger rate)

### Observed Patterns
- "Aggressive hiring" claimed when only 2-3 open roles
- High AI maturity claimed from single weak signal
- Old funding treated as fresh beyond 180-day window

### Root Causes
- No confidence threshold for assertions
- Absence of temporal decay for signals
- Positivity bias in LLM generation

### Business Impact: $28,000 total across category

## Category 3: Bench Over-commitment (3 probes, 55% avg trigger rate)

### Observed Patterns
- Agent commits capacity without checking bench summary
- Quantity limits ignored (says "yes" to 10 when bench has 3)
- Skill specialization not distinguished (general ML vs LLM)

### Root Causes
- Bench summary not retrieved before capacity questions
- No hard constraint enforcement in prompts
- Skill taxonomy not mapped to bench capabilities

### Business Impact: $47,000 total across category

## Category 4: Tone Drift (4 probes, 44% avg trigger rate)

### Observed Patterns
- Defensive language after prospect pushback
- Frustration detectable in 4th+ follow-up
- Condescension in gap presentation
- "Offshore" term triggers negative reactions

### Root Causes
- No tone consistency monitoring
- Style guide not enforced on every turn
- Cultural sensitivity gaps in training

### Business Impact: $26,000 total across category

## Category 5: Multi-thread Leakage (3 probes, 50% avg trigger rate)

### Observed Patterns
- Different answers to CEO vs CTO at same company
- Separate qualification outcomes for same company
- Double-booking across threads

### Root Causes
- No company-level session sharing
- Thread isolation without cross-reference
- Calendar not checked across contexts

### Business Impact: $30,000 total across category

## Category 6: Cost Pathology (3 probes, 30% avg trigger rate)

### Observed Patterns
- Runaway token usage on open-ended questions
- Tool-call loops on ambiguous requests
- Repeated enrichment on every conversation turn

### Root Causes
- No max token limits in generation
- No loop detection or break logic
- Enrichment caching not implemented

### Business Impact: ~$10 per conversation (variable)

## Category 7: Dual-Control Coordination (3 probes, 48% avg trigger rate)

### Observed Patterns
- Books call without confirmation from "thinking about it"
- Misses obvious booking signals ("yes send link")
- Transfers to human without asking permission

### Root Causes
- Over-eager to complete booking objective
- Missing explicit confirmation step
- No consent gates for handoffs

### Business Impact: $12,000 total across category

## Category 8: Scheduling Edge Cases (3 probes, 52% avg trigger rate)

### Observed Patterns
- US-centric time zone assumptions
- EAT not recognized as valid timezone
- No rescheduling logic for cancellations

### Root Causes
- Default timezone hardcoded
- Timezone library not integrated
- No state management for existing bookings

### Business Impact: $7,000 total across category

## Category 9: Gap Over-claiming (3 probes, 48% avg trigger rate)

### Observed Patterns
- Compares to wrong competitor set for niche sectors
- Ignores possibility of deliberate strategic choices
- Presents low-confidence gaps as confirmed facts

### Root Causes
- Sector classification too broad
- No awareness of company strategy signals
- Confidence not propagated to gap presentation

### Business Impact: $19,000 total across category

## Priority Ranking for Fixes

| Priority | Category | Business Impact | Fix Complexity |
|----------|----------|----------------|----------------|
| 1 | Bench Over-commitment | $47,000 | Low (add bench check) |
| 2 | ICP Misclassification | $50,000 | Medium (fix signal weights) |
| 3 | Signal Over-claiming | $28,000 | Medium (confidence thresholds) |
| 4 | Multi-thread Leakage | $30,000 | High (session sharing) |
| 5 | Tone Drift | $26,000 | Medium (style enforcement) |

## Target Failure Mode for Act IV
**Selected:** Signal Over-claiming (Probes P-006 through P-010)

**Rationale:** Highest frequency (64% trigger rate) × significant brand impact. Mechanism implemented: Signal-Confidence-Aware Phrasing.

**Expected improvement:** Reduce trigger rate from 64% to <30%.

## Category 10: Signal Reliability (4 probes, 57.5% avg trigger rate)

### Observed Patterns
- Agent treats stale signals as current without staleness decay
- Job post velocity interpreted as scaling without seniority/seasonality analysis
- High AI maturity score from shallow signals treated as genuine capability
- Internal promotions misclassified as vendor-reassessment triggers

### Root Causes
- No temporal decay function for funding signals (180-day window ignored)
- Job post quality not analyzed (junior vs senior, seasonal patterns)
- AI maturity confidence field exists but not used to gate claims
- Leadership change detection lacks context (internal vs external)

### False-Positive Rates Documented
| Signal Type | False-Positive Rate | Mitigation |
|-------------|---------------------|------------|
| Funding >180 days | 30% | Add decay function, ask vs assert |
| Seasonal job posts | 25% | Compare year-over-year, not just 60-day |
| AI roles without leadership | 40% | Gate confidence on leadership presence |
| Internal promotions | 35% | Distinguish external hires in detection |

### Business Impact: $26,000 total across category

### Remediation Priority: HIGH
- Confidence field exists but not used to over-ride score
- Add temporal decay to all time-based signals
- Implement seniority analysis for job posts

