# Validation report

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

**Baseline ready:** no

## Gates

| Gate | Name | Status | Blocking | Detail |
|---|---|---|---|---|
| V1 | Every requirement has a source | pass | yes | OK |
| V2 | Every requirement has acceptance criteria | pass | yes | OK |
| V3 | Regulatory / safety requirements cite a source | fail | yes | No citation (accept with a waiver note or add a source): FR-RX-002 |
| V4 | No open conflicts | fail | yes | Open: CF-001, CF-002, CF-003, CF-004 |
| V5 | Duplicates reviewed | pass | no | OK |
| V6 | No unresolved high-severity issues | fail | yes | Needs clarification or a waiver note: FR-RX-002 |
| V7 | Mandatory human approvals complete | fail | yes | 22 awaiting approval |
| V8 | Regulatory control gaps decided | warn | no | 13 control gap(s): add a requirement or record why not applicable |
| V9 | SDLC selection signed off | fail | yes | Awaiting: project_manager, architect, security, compliance_officer |

## Metrics

| Metric | Value |
|---|---|
| requirements_active | 28 |
| completeness_pct | 100.0 |
| ambiguous_pct | 42.9 |
| regulatory_control_coverage_pct | 53.6 |
| traceability_coverage_pct | 100.0 |
| avg_confidence | 0.74 |
| open_conflicts | 4 |
| low_confidence_escalations | 7 |

## Processing metrics

| Metric | Value |
|---|---|
| ms_extraction | 668.6 |
| ms_classification | 12.6 |
| ms_quality | 365.7 |
| ms_compliance | 295.3 |
| ms_conflict | 33.1 |
| ms_risk | 3.8 |
| ms_sdlc | 331.4 |
| controls_total | 28 |
| extraction_proposed | 28 |
| extraction_dropped_ungrounded | 0 |
| hallucination_rate_pct | 0.0 |
| llm_calls | 4 |
| invalid_llm_citations | 0 |
