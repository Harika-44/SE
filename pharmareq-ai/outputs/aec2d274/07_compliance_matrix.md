# Compliance matrix

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

Mappings are candidates found by retrieval. The knowledge base is unverified until a compliance officer checks each entry against the official text.

| Requirement | Statement | Candidate rules (score) | Confidence | Risk | Human review |
|---|---|---|---|---|---|
| FR-RX-001 | We would like e-prescriptions with our registration number and digital signature to be accepted by the pharmacy. | TELEMED-2020 (0.45) | 0.71 | High | no |
| FR-REG-001 | The pharmacy should flag Schedule X drugs on tele-consultation prescriptions for review. | TELEMED-2020 (0.40); DCR-SCHED-X (0.35); DCR-SCHED-H (0.24) | 0.77 | High | no |
| NFR-GEN-001 | Patient details should be available only to authorised staff. | none | 0.6 | Medium | no |
| FR-REG-002 | Schedule H1 drugs must be recorded in a separate register with patient name, prescriber and quantity. | DCR-SCHED-H1 (0.68); DCR-SCHED-H (0.35); ORG-SOP-DISPENSING (0.19) | 0.85 | High | no |
| NFR-REG-001 | The H1 register must be retained for 3 years. | DCR-SCHED-H1 (0.43); DCR-SCHED-X (0.22) | 0.85 | High | yes |
| NFR-BIL-001 | Mandatory fields must be filled in every bill, including prescriber and patient details. | DCR-SCHED-H (0.23); DCR-SCHED-H1 (0.16) | 0.73 | High | yes |
| FR-DSP-001 | The register must not be editable or deletable after the sale. | DCR-LICENCE-PHARMACIST (0.18); DCR-SCHED-H (0.15) | 0.69 | High | no |
| FR-REG-003 | Schedule X drugs need a prescription copy kept by the pharmacy. | DCR-SCHED-X (0.52); DCR-SCHED-H (0.23); TELEMED-2020 (0.22) | 0.77 | High | no |
| FR-INV-001 | Expired stock must be kept apart and never dispensed. | ORG-POL-STOCK (0.21); DCR-EXPIRY-RECALL (0.21) | 0.71 | High | no |
| FR-DSP-002 | The pharmacy must be able to produce purchase and sale records on demand. | DCR-LICENCE-PHARMACIST (0.35); DCR-SCHED-H (0.20) | 0.82 | High | no |
| NFR-BIL-002 | Billing must be fast, customers should not wait at the counter during peak hours. | GST-INVOICE (0.20) | 0.7 | Medium | yes |
| NFR-BIL-003 | The system shall skip optional fields while billing so the cashier can finish quickly. | GAMP5-CSV (0.16) | 0.73 | Medium | yes |
| FR-REG-004 | The software should keep H1 records for 3 years because our consultant told us so. | DCR-SCHED-H1 (0.36); DCR-SCHED-X (0.18) | 0.79 | High | yes |
| FR-INV-002 | The system shall allow the user to see near-expiry stock every Monday. | GAMP5-CSV (0.25); ORG-POL-STOCK (0.15) | 0.8 | High | no |
| FR-BIL-001 | It would be nice to give discounts to regular customers. | GST-INVOICE (0.18) | 0.55 | Low | no |
| FR-BIL-002 | We need GST invoices with proper numbering. | GST-INVOICE (0.29); DCR-LICENCE-PHARMACIST (0.17) | 0.69 | Medium | no |
| NFR-GEN-002 | The system should work even when the internet is down. | GAMP5-CSV (0.21) | 0.68 | Medium | no |
| FR-GEN-001 | We currently use Tally for accounts and want to keep it. | GST-INVOICE (0.25) | 0.66 | Medium | no |
| NFR-SEC-001 | The system should allow the owner to override alerts without a reason. | GAMP5-CSV (0.19) | 0.67 | High | no |
| FR-REG-005 | The system shall record the prescriber name, patient name and batch number before dispensing any Schedule H1 drug. | DCR-SCHED-H1 (0.47); DCR-SCHED-H (0.36); ORG-SOP-DISPENSING (0.21) | 0.91 | High | no |
| FR-REG-006 | The system should keep the H1 register for 2 years. | DCR-SCHED-H1 (0.36); DCR-SCHED-X (0.18) | 0.8 | High | yes |
| FR-INV-003 | Expired batches must never be sold, and the software should pick the batch with the earliest expiry first. | DCR-EXPIRY-RECALL (0.45); ORG-POL-STOCK (0.22); ORG-SOP-DISPENSING (0.17) | 0.91 | High | no |
| FR-INV-004 | We want an alert about expiry soon so that nothing gets wasted. | DCR-EXPIRY-RECALL (0.26); ORG-POL-STOCK (0.17) | 0.66 | High | no |
| FR-DSP-003 | Substitution of a brand with a generic is done by the pharmacist, and the reason should be recorded. | PCI-PPR-2015 (0.48) | 0.83 | High | no |
| FR-DSP-004 | If the prescription is illegible we must call [PERSON] on [PHONE] to confirm before dispensing. | ORG-SOP-DISPENSING (0.33) | 0.8 | High | no |
| FR-RX-002 | The system should recommend the correct dose when the prescription is unclear. | none | 0.68 | Critical | yes |
| FR-DSP-005 | Only a registered pharmacist should be able to confirm dispensing of prescription drugs. | PCI-PPR-2015 (0.30); DCR-SCHED-H (0.26); ORG-SOP-DISPENSING (0.24) | 0.75 | High | no |
| NFR-GEN-003 | The software needs to be user-friendly because our assistants have little training. | none | 0.68 | Low | no |

## Control gaps (no requirement covers the control)

| Rule | Control | Suggested requirement (for the analyst to consider) | Severity |
|---|---|---|---|
| DCR-SCHED-H | Block sale of Schedule H drugs without a valid prescription | The system shall not allow a Schedule H drug to be dispensed unless a valid prescription is attached to the sale. | high |
| DCR-SCHED-X | Record every Schedule X supply | The system shall record every Schedule X supply in the scheduled-drug register. | high |
| NDPS-1985 | Accurate stock and supply records for NDPS substances | The system shall keep an accurate stock and supply record for NDPS substances and support inspection reports. | high |
| DCR-EXPIRY-RECALL | Quarantine recalled batches and record the action | The system shall allow a batch to be marked recalled, quarantine its stock and record the action. | high |
| DPDP-2023 | Collect only needed patient data, for a stated purpose | The system shall collect only the patient data needed for dispensing and record the purpose and consent status. | high |
| DPDP-2023 | Protect personal data (access control, encryption, masking) | The system shall protect patient and prescription data with role-based access, encryption in transit and at rest, and masking in non-clinical views. | high |
| DPDP-2023 | Detect and report personal-data breaches | The system shall log access to patient data and support breach investigation and notification. | high |
| WHO-DATA-INTEGRITY | Audit trail with user, time and reason for every record change | The system shall keep an audit trail (user, timestamp, old value, new value, reason) for every change to dispensing, stock and register records. | medium |
| ISO-27001-AC | Role-based access with least privilege | The system shall enforce role-based access control with least privilege for pharmacist, assistant, owner and auditor roles. | medium |
| ISO-27001-AC | Authenticated sessions; stronger authentication for privileged actions | The system shall authenticate every user and require stronger authentication (for example OTP) for privileged actions such as overrides. | medium |
| GAMP5-CSV | Requirements traceable to tests and evidence | Each approved requirement shall be traceable to at least one test case and its validation evidence. | medium |
| ORG-SOP-DISPENSING | Record partial supply and balance quantity | The system shall record partial dispensing with the balance quantity still owed. | medium |
| ORG-POL-STOCK | Goods receipt records batch and expiry | The system shall record batch number, expiry date and quantity for every goods receipt against the supplier invoice. | medium |
