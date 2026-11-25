# Data and interface requirements

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

## Core data entities (proposed)

| Entity | Key attributes |
|---|---|
| Prescription | prescription id, date, prescriber (name, registration no.), patient reference, drugs, quantity, e-prescription flag, scanned copy |
| Patient | name, age/sex, contact (masked in non-clinical views), consent status |
| Drug | name, strength, form, schedule (H/H1/X/NDPS/none), HSN, MRP |
| Batch | batch no., expiry date, quantity on hand, supplier, status (valid/near-expiry/expired/recalled) |
| DispenseTransaction | prescription, drug, batch, quantity, pharmacist, timestamp, substitution reason |
| ScheduledRegisterEntry | transaction, patient, prescriber, drug, batch, quantity, date, correction-of reference |
| Invoice | number (sequential), GSTIN, HSN, tax rate/amount, discount, authoriser |
| Supplier / Purchase | supplier, invoice, goods-receipt lines, returns, credit-note reference |
| AuditEvent | user, role, action, object, old/new value, reason, timestamp, hash |

## Data-management requirements from stakeholders

| ID | Requirement |
|---|---|
| NFR-REG-001 | The H1 register must be retained for 3 years. |
| NFR-BIL-001 | Mandatory fields must be filled in every bill, including prescriber and patient details. |
| FR-DSP-001 | The register must not be editable or deletable after the sale. |
| NFR-BIL-003 | The system shall skip optional fields while billing so the cashier can finish quickly. |

## Interface requirements from stakeholders

| ID | Requirement |
|---|---|
| FR-GEN-001 | We currently use Tally for accounts and want to keep it. |
