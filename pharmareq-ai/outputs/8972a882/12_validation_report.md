# Validation report

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

**Baseline ready:** no

## Gates

| Gate | Name | Status | Blocking | Detail |
|---|---|---|---|---|
| V1 | Every requirement has a source | pass | yes | OK |
| V2 | Every requirement has acceptance criteria | pass | yes | OK |
| V3 | Regulatory / safety requirements cite a source | pass | yes | OK |
| V4 | No open conflicts | pass | yes | OK |
| V5 | Duplicates reviewed | pass | no | OK |
| V6 | No unresolved high-severity issues | pass | yes | OK |
| V7 | Mandatory human approvals complete | pass | yes | OK |
| V8 | Regulatory control gaps decided | warn | no | 15 control gap(s): add a requirement or record why not applicable |
| V9 | SDLC selection signed off | fail | yes | Awaiting: project_manager, architect, security, compliance_officer |

## Metrics

| Metric | Value |
|---|---|
| requirements_active | 1 |
| completeness_pct | 100.0 |
| ambiguous_pct | 0.0 |
| regulatory_control_coverage_pct | 16.7 |
| traceability_coverage_pct | 100.0 |
| avg_confidence | 0.78 |
| open_conflicts | 0 |
| low_confidence_escalations | 0 |

## Processing metrics

| Metric | Value |
|---|---|
| ms_extraction | 517.6 |
| ms_classification | 12.5 |
| ms_quality | 6.2 |
| ms_compliance | 122.8 |
| ms_conflict | 0.6 |
| ms_risk | 4.3 |
| ms_sdlc | 113.9 |
| controls_total | 18 |
| extraction_proposed | 2 |
| extraction_dropped_ungrounded | 0 |
| hallucination_rate_pct | 0.0 |
| llm_calls | 3 |
| invalid_llm_citations | 0 |
| ms_total | 924.0 |
