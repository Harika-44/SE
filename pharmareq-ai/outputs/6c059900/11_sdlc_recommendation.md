# SDLC recommendation and project workflow

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

**Recommended:** V-Model with Agile iterations

V-Model with Agile iterations ranks first (87.4%). Best-matching drivers: need for formal verification and evidence 0.85 (target 0.90); regulatory criticality 1.00 (target 0.90); patient-safety impact of failure 1.00 (target 0.90); requirement stability 0.63 (target 0.50). Runner-up: V-Model (87.0%). Rules applied: R1 R7. Final adoption needs approval from the project manager, architect, security lead and compliance officer.

## Ranking

| Model | Score % |
|---|---|
| V-Model with Agile iterations | 87.4 |
| V-Model | 87.0 |
| DevSecOps hybrid (V-Model gates + CI/CD) | 83.3 |
| Spiral | 71.4 |
| DevSecOps | 67.7 |
| Waterfall | 67.6 |
| Agile | 48.3 |

## Derived project factors (0 to 1)

| Factor | Value |
|---|---|
| requirement_stability | 0.63 |
| regulatory_criticality | 1.0 |
| patient_safety_impact | 1.0 |
| security_privacy_risk | 0.9 |
| complexity | 0.65 |
| system_size | 0.49 |
| legacy_dependence | 0.49 |
| change_frequency | 0.2 |
| continuous_delivery_need | 0.4 |
| stakeholder_availability | 0.6 |
| verification_need | 0.85 |
| budget_schedule_pressure | 0.76 |
| uncertainty | 0.63 |

## Rules applied

- R1: patient-safety impact and regulatory criticality are both high -> pure Agile capped at 60 (it does not give validation evidence on its own).
- R7: validated-system expectations -> Waterfall penalised for late verification and slow response to rule changes.

## Sign-offs

| Role | Signed by |
|---|---|
| project_manager | pending |
| architect | pending |
| security | pending |
| compliance_officer | pending |

## Workflow

### Phase 1: Planning and validation plan

**Activities:** Confirm scope: prescription-to-dispensing with scheduled-drug register; Agree roles, tools, risk-based validation plan; Set up requirement baseline and change-control process

**Roles:** Project manager; Compliance officer; Pharmacist (domain lead)

**Deliverables:** Project plan; Validation plan; Stakeholder list

**Security controls:** Access model for project artefacts

**Compliance checkpoints:** Compliance officer confirms applicable rules list

**Entry criteria:** Project mandate

**Exit criteria:** Validation plan signed

**Gate:** G0: plan approved

### Phase 2: Requirements and hazard analysis (V-Model left side)

**Activities:** Elicit and clarify requirements (this tool); Hazard analysis: wrong drug, expired batch, missing register entry; Resolve conflicts and open questions; Map requirements to rules

**Roles:** Business analyst; Pharmacist; Compliance officer

**Deliverables:** SRS; Traceability matrix (draft); Hazard log; Compliance matrix

**Security controls:** Data-classification of patient data

**Compliance checkpoints:** Every regulatory requirement has a cited source; Pharmacist approves safety-critical requirements

**Entry criteria:** Plan signed

**Exit criteria:** No open high-severity conflicts; Mandatory approvals complete

**Gate:** G1: requirement baseline approved

### Phase 3: Architecture and threat modelling (V-Model left side)

**Activities:** Design modules (dispensing, register, inventory, billing); Threat model: unauthorised override, record tampering, data leakage; Define audit-trail and register data model; Interface contracts for legacy systems

**Roles:** Architect; Security lead; Developers

**Deliverables:** Architecture document; Threat model; Data model; Interface specs

**Security controls:** Threat modelling; RBAC design; Encryption design

**Compliance checkpoints:** Design review against compliance matrix

**Entry criteria:** Requirement baseline

**Exit criteria:** Every requirement allocated to a design element

**Gate:** G2: design approved

### Phase 4: Iterative build sprints (Agile)

*Iteration:* 2-3 week sprints inside the validated lifecycle

**Activities:** Implement features in small increments; Peer review of every change; Unit tests alongside code; Each sprint delivers one slice, e.g. H1 register, then expiry alerts; Pharmacist reviews every sprint demo; Requirement changes go through change control and re-trigger affected tests

**Roles:** Developers

**Deliverables:** Source code; Unit tests

**Security controls:** Static analysis (SAST); Dependency and secret scanning

**Compliance checkpoints:** Safety-critical code reviewed by a second developer

**Entry criteria:** Approved design

**Exit criteria:** No critical scan findings

**Gate:** Sprint gate: tests and scans pass

### Phase 5: Verification at each V level

**Activities:** Unit and integration tests; System tests against SRS; Regression suite for dispensing and register

**Roles:** QA engineer; Developers

**Deliverables:** Test reports; Updated traceability matrix

**Security controls:** Security tests of override and access paths

**Compliance checkpoints:** Each requirement linked to a passed test

**Entry criteria:** Build complete

**Exit criteria:** All Must requirements verified

**Gate:** G3: verification complete

### Phase 6: Validation with pharmacists

**Activities:** Dispensing-accuracy test set (including expired, recalled, H1/X cases); Batch-integrity and register-completeness tests; User acceptance testing by a pharmacist; Mock inspection using the generated reports

**Roles:** Pharmacist; QA engineer; Compliance officer

**Deliverables:** Validation report with objective evidence; UAT sign-off

**Security controls:** Penetration or vulnerability test

**Compliance checkpoints:** Mock inspection passed

**Entry criteria:** Verification complete

**Exit criteria:** Pharmacist UAT signed

**Gate:** G4: validation accepted

### Phase 7: Compliance approval and release

**Activities:** Compliance review of evidence pack; Go-live checklist and rollback plan; Training of pharmacy staff

**Roles:** Compliance officer; Project manager; Pharmacy owner

**Deliverables:** Release approval; Training record

**Security controls:** Production access review; Backup and restore verified

**Compliance checkpoints:** Compliance officer approves release

**Entry criteria:** Validation accepted

**Exit criteria:** Approvals recorded in the audit trail

**Gate:** G5: release approved

### Phase 8: Operation and change control

**Activities:** Monitor errors and incidents; Update schedule lists and rules under change control; Re-validate on significant change

**Roles:** Pharmacy owner; Compliance officer; Support team

**Deliverables:** Change records; Incident log

**Security controls:** Log monitoring; Periodic access review

**Compliance checkpoints:** Regulatory-change review each quarter

**Entry criteria:** Released

**Exit criteria:** Change impact assessed and approved

**Gate:** Change gate: impact assessed
