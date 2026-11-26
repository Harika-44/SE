# Software Requirements Specification - PharmaReq Demo

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

Run `8972a882` - generated 2026-11-26T17:23:11+00:00

## 1. Introduction

Purpose: define the requirements for pharmacy dispensing and inventory-compliance software, focused on the prescription-to-dispensing workflow with scheduled-drug record keeping.

This document was produced from stakeholder inputs by the PharmaReq AI agents. Patient data in the inputs was masked before processing.

## 2. Stakeholders and sources

| Stakeholder | Requirements raised |
|---|---|
| Pharmacist | 1 |

## 3. Overall description

Context statements captured from the inputs:

- None captured.

## 4. Functional requirements

## 5. Non-functional requirements

| ID | Requirement | Categories | Priority | Risk | Source | Status |
|---|---|---|---|---|---|---|
| NFR-SEC-001 | The system must require two-factor authentication for all pharmacist logins. | Security, Patient safety | Must | High | Pharmacist | accepted |

## 6. Regulatory and policy mapping (candidate)

| Requirement | KB entry | Title | Verified | Why matched |
|---|---|---|---|---|
| NFR-SEC-001 | ISO-27001-AC | Information security controls - access control, logging, secure operation | NO - verify | Matched terms: authentication, login |

## 7. Open items

- Clarification questions: 0 (see `10_open_issues.md`)
- Conflicts: 0
- Control gaps: 15

## 8. Approval status

| Status | Count |
|---|---|
| accepted | 1 |
| pending | 0 |
| rejected | 1 |

## Appendix A. Rejected requirements

| ID | Statement |
|---|---|
| FR-REG-001 | Schedule H1 sales must be logged with patient name and prescriber details. |
