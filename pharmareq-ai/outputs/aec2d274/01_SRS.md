# Software Requirements Specification - PharmaReq Demo

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

Run `aec2d274` - generated 2026-11-26T18:04:56+00:00

## 1. Introduction

Purpose: define the requirements for pharmacy dispensing and inventory-compliance software, focused on the prescription-to-dispensing workflow with scheduled-drug record keeping.

This document was produced from stakeholder inputs by the PharmaReq AI agents. Patient data in the inputs was masked before processing.

## 2. Stakeholders and sources

| Stakeholder | Requirements raised |
|---|---|
| Doctor | 3 |
| Inspector | 7 |
| Owner | 9 |
| Pharmacist | 9 |

## 3. Overall description

Context statements captured from the inputs:

- Pharmacist: Currently we write the H1 register by hand in a notebook.

## 4. Functional requirements

### Prescription intake and validation

| ID | Requirement | Priority | Risk | Source | Status |
|---|---|---|---|---|---|
| FR-RX-001 | We would like e-prescriptions with our registration number and digital signature to be accepted by the pharmacy. | Must | High | Doctor | pending |
| FR-RX-002 | The system should recommend the correct dose when the prescription is unclear. | Should | Critical | Pharmacist | pending |

### Scheduled-drug register

| ID | Requirement | Priority | Risk | Source | Status |
|---|---|---|---|---|---|
| FR-REG-001 | The pharmacy should flag Schedule X drugs on tele-consultation prescriptions for review. | Must | High | Doctor | pending |
| FR-REG-002 | Schedule H1 drugs must be recorded in a separate register with patient name, prescriber and quantity. | Must | High | Inspector | pending |
| FR-REG-003 | Schedule X drugs need a prescription copy kept by the pharmacy. | Must | High | Inspector | pending |
| FR-REG-004 | The software should keep H1 records for 3 years because our consultant told us so. | Must | High | Owner | pending |
| FR-REG-005 | The system shall record the prescriber name, patient name and batch number before dispensing any Schedule H1 drug. | Must | High | Pharmacist | pending |
| FR-REG-006 | The system should keep the H1 register for 2 years. | Must | High | Pharmacist | pending |

### Dispensing

| ID | Requirement | Priority | Risk | Source | Status |
|---|---|---|---|---|---|
| FR-DSP-001 | The register must not be editable or deletable after the sale. | Must | High | Inspector | pending |
| FR-DSP-002 | The pharmacy must be able to produce purchase and sale records on demand. | Must | High | Inspector | pending |
| FR-DSP-003 | Substitution of a brand with a generic is done by the pharmacist, and the reason should be recorded. | Must | High | Pharmacist | pending |
| FR-DSP-004 | If the prescription is illegible we must call [PERSON] on [PHONE] to confirm before dispensing. | Must | High | Pharmacist | pending |
| FR-DSP-005 | Only a registered pharmacist should be able to confirm dispensing of prescription drugs. | Must | High | Pharmacist | pending |

### Batch, expiry and stock

| ID | Requirement | Priority | Risk | Source | Status |
|---|---|---|---|---|---|
| FR-INV-001 | Expired stock must be kept apart and never dispensed. | Must | High | Inspector | pending |
| FR-INV-002 | The system shall allow the user to see near-expiry stock every Monday. | Must | High | Owner | pending |
| FR-INV-003 | Expired batches must never be sold, and the software should pick the batch with the earliest expiry first. | Must | High | Pharmacist | pending |
| FR-INV-004 | We want an alert about expiry soon so that nothing gets wasted. | Must | High | Pharmacist | pending |

### Billing

| ID | Requirement | Priority | Risk | Source | Status |
|---|---|---|---|---|---|
| FR-BIL-001 | It would be nice to give discounts to regular customers. | Could | Low | Owner | pending |
| FR-BIL-002 | We need GST invoices with proper numbering. | Must | Medium | Owner | pending |

### General

| ID | Requirement | Priority | Risk | Source | Status |
|---|---|---|---|---|---|
| FR-GEN-001 | We currently use Tally for accounts and want to keep it. | Should | Medium | Owner | pending |

## 5. Non-functional requirements

| ID | Requirement | Categories | Priority | Risk | Source | Status |
|---|---|---|---|---|---|---|
| NFR-GEN-001 | Patient details should be available only to authorised staff. | Security, Privacy, Availability and reliability | Should | Medium | Doctor | pending |
| NFR-REG-001 | The H1 register must be retained for 3 years. | Regulatory, Data management | Must | High | Inspector | pending |
| NFR-BIL-001 | Mandatory fields must be filled in every bill, including prescriber and patient details. | Privacy, Data management, Functional | Must | High | Inspector | pending |
| NFR-BIL-002 | Billing must be fast, customers should not wait at the counter during peak hours. | Performance, Business, Functional | Must | Medium | Owner | pending |
| NFR-BIL-003 | The system shall skip optional fields while billing so the cashier can finish quickly. | Performance, Data management, Functional | Should | Medium | Owner | pending |
| NFR-GEN-002 | The system should work even when the internet is down. | Availability and reliability | Should | Medium | Owner | pending |
| NFR-SEC-001 | The system should allow the owner to override alerts without a reason. | Security, Functional | Should | High | Owner | pending |
| NFR-GEN-003 | The software needs to be user-friendly because our assistants have little training. | Usability | Should | Low | Pharmacist | pending |

## 6. Regulatory and policy mapping (candidate)

| Requirement | KB entry | Title | Verified | Why matched |
|---|---|---|---|---|
| FR-RX-001 | TELEMED-2020 | Telemedicine Practice Guidelines, 2020 - e-prescriptions | NO - verify | Matched terms: digital, e-prescription, number, registration, signature |
| FR-REG-001 | TELEMED-2020 | Telemedicine Practice Guidelines, 2020 - e-prescriptions | NO - verify | Matched terms: prescription, schedule, tele-consultation, x |
| FR-REG-001 | DCR-SCHED-X | Drugs and Cosmetics Rules - Schedule X drugs (psychotropic, stricter control) | NO - verify | Matched terms: drug, prescription, schedule, x |
| FR-REG-001 | DCR-SCHED-H | Drugs and Cosmetics Rules, 1945 - Schedule H drugs (sale on prescription) | NO - verify | Matched terms: drug, prescription, schedule |
| FR-REG-002 | DCR-SCHED-H1 | Drugs and Cosmetics Rules - Schedule H1 drugs (separate register) | NO - verify | Matched terms: drug, h1, name, patient, prescriber, quantity |
| FR-REG-002 | DCR-SCHED-H | Drugs and Cosmetics Rules, 1945 - Schedule H drugs (sale on prescription) | NO - verify | Matched terms: drug, name, patient, prescriber, record, schedule |
| FR-REG-002 | ORG-SOP-DISPENSING | Organisation SOP (synthetic example) - dispensing checklist | NO - verify | Matched terms: quantity |
| NFR-REG-001 | DCR-SCHED-H1 | Drugs and Cosmetics Rules - Schedule H1 drugs (separate register) | NO - verify | Matched terms: h1, record, retain, year |
| NFR-REG-001 | DCR-SCHED-X | Drugs and Cosmetics Rules - Schedule X drugs (psychotropic, stricter control) | NO - verify | Matched terms: retain, year |
| NFR-BIL-001 | DCR-SCHED-H | Drugs and Cosmetics Rules, 1945 - Schedule H drugs (sale on prescription) | NO - verify | Matched terms: patient, prescriber |
| NFR-BIL-001 | DCR-SCHED-H1 | Drugs and Cosmetics Rules - Schedule H1 drugs (separate register) | NO - verify | Matched terms: patient, prescriber |
| FR-DSP-001 | DCR-LICENCE-PHARMACIST | Retail sale licence conditions - supervision by a registered pharmacist, purchase and sale records | NO - verify | Matched terms: record, sale |
| FR-DSP-001 | DCR-SCHED-H | Drugs and Cosmetics Rules, 1945 - Schedule H drugs (sale on prescription) | NO - verify | Matched terms: record, sale |
| FR-REG-003 | DCR-SCHED-X | Drugs and Cosmetics Rules - Schedule X drugs (psychotropic, stricter control) | NO - verify | Matched terms: copy, drug, prescription, schedule, x |
| FR-REG-003 | DCR-SCHED-H | Drugs and Cosmetics Rules, 1945 - Schedule H drugs (sale on prescription) | NO - verify | Matched terms: drug, prescription, schedule |
| FR-REG-003 | TELEMED-2020 | Telemedicine Practice Guidelines, 2020 - e-prescriptions | NO - verify | Matched terms: prescription, schedule, x |
| FR-INV-001 | ORG-POL-STOCK | Organisation policy (synthetic example) - stock, batch and supplier returns | NO - verify | Matched terms: expir, stock |
| FR-INV-001 | DCR-EXPIRY-RECALL | Expired, substandard and recalled drugs - no sale, segregation, recall handling | NO - verify | Matched terms: expir |
| FR-DSP-002 | DCR-LICENCE-PHARMACIST | Retail sale licence conditions - supervision by a registered pharmacist, purchase and sale records | NO - verify | Matched terms: purchase, record, sale |
| FR-DSP-002 | DCR-SCHED-H | Drugs and Cosmetics Rules, 1945 - Schedule H drugs (sale on prescription) | NO - verify | Matched terms: record, sale |
| NFR-BIL-002 | GST-INVOICE | GST invoicing and record keeping for pharmacy sales | NO - verify | Matched terms: bill |
| NFR-BIL-003 | GAMP5-CSV | Computerised system validation - risk-based, lifecycle approach | NO - verify | Matched terms: system |
| FR-REG-004 | DCR-SCHED-H1 | Drugs and Cosmetics Rules - Schedule H1 drugs (separate register) | NO - verify | Matched terms: h1, record, retain, year |
| FR-REG-004 | DCR-SCHED-X | Drugs and Cosmetics Rules - Schedule X drugs (psychotropic, stricter control) | NO - verify | Matched terms: retain, year |
| FR-INV-002 | GAMP5-CSV | Computerised system validation - risk-based, lifecycle approach | NO - verify | Matched terms: system, user |
| FR-INV-002 | ORG-POL-STOCK | Organisation policy (synthetic example) - stock, batch and supplier returns | NO - verify | Matched terms: stock |
| FR-BIL-001 | GST-INVOICE | GST invoicing and record keeping for pharmacy sales | NO - verify | Matched terms: discount |
| FR-BIL-002 | GST-INVOICE | GST invoicing and record keeping for pharmacy sales | NO - verify | Matched terms: gst, invoic, number |
| FR-BIL-002 | DCR-LICENCE-PHARMACIST | Retail sale licence conditions - supervision by a registered pharmacist, purchase and sale records | NO - verify | Matched terms: number |
| NFR-GEN-002 | GAMP5-CSV | Computerised system validation - risk-based, lifecycle approach | NO - verify | Matched terms: system |
| FR-GEN-001 | GST-INVOICE | GST invoicing and record keeping for pharmacy sales | NO - verify | Matched terms: account, retain |
| NFR-SEC-001 | GAMP5-CSV | Computerised system validation - risk-based, lifecycle approach | NO - verify | Matched terms: system |
| FR-REG-005 | DCR-SCHED-H1 | Drugs and Cosmetics Rules - Schedule H1 drugs (separate register) | NO - verify | Matched terms: batch, drug, h1, name, patient, prescriber |
| FR-REG-005 | DCR-SCHED-H | Drugs and Cosmetics Rules, 1945 - Schedule H drugs (sale on prescription) | NO - verify | Matched terms: dispens, drug, name, patient, prescriber, record |
| FR-REG-005 | ORG-SOP-DISPENSING | Organisation SOP (synthetic example) - dispensing checklist | NO - verify | Matched terms: batch, dispens |
| FR-REG-006 | DCR-SCHED-H1 | Drugs and Cosmetics Rules - Schedule H1 drugs (separate register) | NO - verify | Matched terms: h1, record, retain, year |
| FR-REG-006 | DCR-SCHED-X | Drugs and Cosmetics Rules - Schedule X drugs (psychotropic, stricter control) | NO - verify | Matched terms: retain, year |
| FR-INV-003 | DCR-EXPIRY-RECALL | Expired, substandard and recalled drugs - no sale, segregation, recall handling | NO - verify | Matched terms: batch, expir, first, sale |
| FR-INV-003 | ORG-POL-STOCK | Organisation policy (synthetic example) - stock, batch and supplier returns | NO - verify | Matched terms: batch, expir |
| FR-INV-003 | ORG-SOP-DISPENSING | Organisation SOP (synthetic example) - dispensing checklist | NO - verify | Matched terms: batch, expir |
| FR-INV-004 | DCR-EXPIRY-RECALL | Expired, substandard and recalled drugs - no sale, segregation, recall handling | NO - verify | Matched terms: expir |
| FR-INV-004 | ORG-POL-STOCK | Organisation policy (synthetic example) - stock, batch and supplier returns | NO - verify | Matched terms: expir |
| FR-DSP-003 | PCI-PPR-2015 | Pharmacy Practice Regulations, 2015 - pharmacist duties in dispensing | NO - verify | Matched terms: brand, generic, pharmacist, substitution |
| FR-DSP-004 | ORG-SOP-DISPENSING | Organisation SOP (synthetic example) - dispensing checklist | NO - verify | Matched terms: dispens, illegible, prescription |
| FR-DSP-005 | PCI-PPR-2015 | Pharmacy Practice Regulations, 2015 - pharmacist duties in dispensing | NO - verify | Matched terms: dispens, pharmacist, prescription |
| FR-DSP-005 | DCR-SCHED-H | Drugs and Cosmetics Rules, 1945 - Schedule H drugs (sale on prescription) | NO - verify | Matched terms: dispens, drug, prescription, record |
| FR-DSP-005 | ORG-SOP-DISPENSING | Organisation SOP (synthetic example) - dispensing checklist | NO - verify | Matched terms: dispens, prescription |

## 7. Open items

- Clarification questions: 24 (see `10_open_issues.md`)
- Conflicts: 4
- Control gaps: 13

## 8. Approval status

| Status | Count |
|---|---|
| accepted | 0 |
| pending | 28 |
| rejected | 0 |
