# User stories and acceptance criteria

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

### FR-RX-001
**As a** doctor, **I want** the system to we would like e-prescriptions with our registration number and digital signature to be accepted by the pharmacy, **so that** reduces the risk of dispensing errors and patient harm.

Acceptance criteria:
- Given a prescription with a missing mandatory field, the system refuses to continue and lists the missing fields.
- A completed dispensing is linked to its prescription.

Source: Doctor ("We would like e-prescriptions with our registration number and digital signature to be accepted by the pharmacy.")

### FR-REG-001
**As a** doctor, **I want** the system to the pharmacy should flag Schedule X drugs on tele-consultation prescriptions for review, **so that** supports regulatory compliance and inspection readiness.

Acceptance criteria:
- Given a scheduled drug is dispensed, when the sale is confirmed, then a register entry with patient, prescriber, drug, batch, quantity and date exists.
- A user cannot complete the sale while a mandatory register field is empty.
- Given a prescription with a missing mandatory field, the system refuses to continue and lists the missing fields.

Source: Doctor ("The pharmacy should flag Schedule X drugs on tele-consultation prescriptions for review.")

### FR-REG-002
**As a** inspector, **I want** the system to schedule H1 drugs must be recorded in a separate register with patient name, prescriber and quantity, **so that** supports regulatory compliance and inspection readiness.

Acceptance criteria:
- Given a scheduled drug is dispensed, when the sale is confirmed, then a register entry with patient, prescriber, drug, batch, quantity and date exists.
- A user cannot complete the sale while a mandatory register field is empty.
- Given a prescription with a missing mandatory field, the system refuses to continue and lists the missing fields.

Source: Inspector ("Schedule H1 drugs must be recorded in a separate register with patient name, prescriber and quantity.")

### FR-DSP-001
**As a** inspector, **I want** the system to the register must not be editable or deletable after the sale, **so that** supports regulatory compliance and inspection readiness.

Acceptance criteria:
- Given a scheduled drug is dispensed, when the sale is confirmed, then a register entry with patient, prescriber, drug, batch, quantity and date exists.
- A user cannot complete the sale while a mandatory register field is empty.
- Given a regulated record inside its retention period, a delete attempt is refused and logged.

Source: Inspector ("The register must not be editable or deletable after the sale.")

### FR-REG-003
**As a** inspector, **I want** the system to schedule X drugs need a prescription copy kept by the pharmacy, **so that** supports regulatory compliance and inspection readiness.

Acceptance criteria:
- Given a scheduled drug is dispensed, when the sale is confirmed, then a register entry with patient, prescriber, drug, batch, quantity and date exists.
- A user cannot complete the sale while a mandatory register field is empty.
- Given a prescription with a missing mandatory field, the system refuses to continue and lists the missing fields.

Source: Inspector ("Schedule X drugs need a prescription copy kept by the pharmacy.")

### FR-INV-001
**As a** inspector, **I want** the system to expired stock must be kept apart and never dispensed, **so that** reduces the risk of dispensing errors and patient harm.

Acceptance criteria:
- Given a batch past its expiry date or marked recalled, when a user tries to sell it, then the sale is blocked and the reason is shown.
- Given several valid batches, the batch with the earliest valid expiry is proposed first.

Source: Inspector ("Expired stock must be kept apart and never dispensed.")

### FR-DSP-002
**As a** inspector, **I want** the system to the pharmacy must be able to produce purchase and sale records on demand, **so that** reduces the risk of dispensing errors and patient harm.

Acceptance criteria:
- The behaviour described in the requirement is demonstrated by a test with recorded evidence. (provisional until the clarification questions are answered)
- A failure of this behaviour is logged.

Source: Inspector ("The pharmacy must be able to produce purchase and sale records on demand.")

### FR-REG-004
**As a** owner, **I want** the system to the software should keep H1 records for 3 years because our consultant told us so, **so that** supports regulatory compliance and inspection readiness.

Acceptance criteria:
- Given a scheduled drug is dispensed, when the sale is confirmed, then a register entry with patient, prescriber, drug, batch, quantity and date exists.
- A user cannot complete the sale while a mandatory register field is empty.

Source: Owner ("The software should keep H1 records for 3 years because our consultant told us so.")

### FR-INV-002
**As a** owner, **I want** the system to allow the user to see near-expiry stock every Monday, **so that** reduces the risk of dispensing errors and patient harm.

Acceptance criteria:
- Given a batch past its expiry date or marked recalled, when a user tries to sell it, then the sale is blocked and the reason is shown. (provisional until the clarification questions are answered)
- Given several valid batches, the batch with the earliest valid expiry is proposed first.

Source: Owner ("We need to see near-expiry stock every Monday.")

### FR-BIL-001
**As a** owner, **I want** the system to it would be nice to give discounts to regular customers, **so that** supports pharmacy business efficiency.

Acceptance criteria:
- The behaviour described in the requirement is demonstrated by a test with recorded evidence. (provisional until the clarification questions are answered)
- A failure of this behaviour is logged.

Source: Owner ("It would be nice to give discounts to regular customers.")

### FR-BIL-002
**As a** owner, **I want** the system to we need GST invoices with proper numbering, **so that** supports regulatory compliance and inspection readiness.

Acceptance criteria:
- Given a completed sale, the invoice shows a unique sequential number, GSTIN, HSN, tax rate and tax amount. (provisional until the clarification questions are answered)

Source: Owner ("We need GST invoices with proper numbering.")

### FR-GEN-001
**As a** owner, **I want** the system to we currently use Tally for accounts and want to keep it, **so that** requested by the stakeholder.

Acceptance criteria:
- The behaviour described in the requirement is demonstrated by a test with recorded evidence. (provisional until the clarification questions are answered)
- A failure of this behaviour is logged.

Source: Owner ("We currently use Tally for accounts and want to keep it.")

### FR-REG-005
**As a** pharmacist, **I want** the system to record the prescriber name, patient name and batch number before dispensing any Schedule H1 drug, **so that** supports regulatory compliance and inspection readiness.

Acceptance criteria:
- Given a scheduled drug is dispensed, when the sale is confirmed, then a register entry with patient, prescriber, drug, batch, quantity and date exists.
- A user cannot complete the sale while a mandatory register field is empty.
- Given a prescription with a missing mandatory field, the system refuses to continue and lists the missing fields.

Source: Pharmacist ("We need to record the prescriber name, patient name and batch number before dispensing any Schedule H1 drug.")

### FR-REG-006
**As a** pharmacist, **I want** the system to keep the H1 register for 2 years, **so that** supports regulatory compliance and inspection readiness.

Acceptance criteria:
- Given a scheduled drug is dispensed, when the sale is confirmed, then a register entry with patient, prescriber, drug, batch, quantity and date exists.
- A user cannot complete the sale while a mandatory register field is empty.

Source: Pharmacist ("The system should keep the H1 register for 2 years.")

### FR-INV-003
**As a** pharmacist, **I want** the system to expired batches must never be sold, and the software should pick the batch with the earliest expiry first, **so that** reduces the risk of dispensing errors and patient harm.

Acceptance criteria:
- Given a batch past its expiry date or marked recalled, when a user tries to sell it, then the sale is blocked and the reason is shown.
- Given several valid batches, the batch with the earliest valid expiry is proposed first.

Source: Pharmacist ("Expired batches must never be sold, and the software should pick the batch with the earliest expiry first.")

### FR-INV-004
**As a** pharmacist, **I want** the system to we want an alert about expiry soon so that nothing gets wasted, **so that** reduces the risk of dispensing errors and patient harm.

Acceptance criteria:
- Given a batch past its expiry date or marked recalled, when a user tries to sell it, then the sale is blocked and the reason is shown. (provisional until the clarification questions are answered)
- Given several valid batches, the batch with the earliest valid expiry is proposed first.
- Given the alert condition is met, the alert is raised within the agreed time and shown to the named recipient and logged.

Source: Pharmacist ("We want an alert about expiry soon so that nothing gets wasted.")

### FR-DSP-003
**As a** pharmacist, **I want** the system to substitution of a brand with a generic is done by the pharmacist, and the reason should be recorded, **so that** reduces the risk of dispensing errors and patient harm.

Acceptance criteria:
- A substitution cannot be saved without pharmacist confirmation; the original drug, substitute and reason are stored. (provisional until the clarification questions are answered)

Source: Pharmacist ("Substitution of a brand with a generic is done by the pharmacist, and the reason should be recorded.")

### FR-DSP-004
**As a** pharmacist, **I want** the system to if the prescription is illegible we must call [PERSON] on [PHONE] to confirm before dispensing, **so that** reduces the risk of dispensing errors and patient harm.

Acceptance criteria:
- Given a prescription with a missing mandatory field, the system refuses to continue and lists the missing fields.
- A completed dispensing is linked to its prescription.

Source: Pharmacist ("If the prescription is illegible we must call [PERSON] on [PHONE] to confirm before dispensing.")

### FR-RX-002
**As a** pharmacist, **I want** the system to recommend the correct dose when the prescription is unclear, **so that** requested by the stakeholder.

Acceptance criteria:
- Given a prescription with a missing mandatory field, the system refuses to continue and lists the missing fields.
- A completed dispensing is linked to its prescription.

Source: Pharmacist ("The system should recommend the correct dose when the prescription is unclear.")

### FR-DSP-005
**As a** pharmacist, **I want** the system to only a registered pharmacist should be able to confirm dispensing of prescription drugs, **so that** reduces the risk of dispensing errors and patient harm.

Acceptance criteria:
- Given a scheduled drug is dispensed, when the sale is confirmed, then a register entry with patient, prescriber, drug, batch, quantity and date exists.
- A user cannot complete the sale while a mandatory register field is empty.
- Given a prescription with a missing mandatory field, the system refuses to continue and lists the missing fields.

Source: Pharmacist ("Only a registered pharmacist should be able to confirm dispensing of prescription drugs.")
