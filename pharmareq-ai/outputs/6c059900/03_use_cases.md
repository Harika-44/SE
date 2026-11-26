# Use cases

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

## UC-01 Validate and accept a prescription

- **Actor:** Pharmacist / pharmacy assistant
- **Precondition:** A paper or electronic prescription is presented.
- **Postcondition:** Validated prescription is linked to the pending sale.
- **Related requirements:** FR-RX-001, FR-RX-002

**Main flow**

1. Capture prescriber, patient and drug details.
2. System validates mandatory fields and schedule rules.
3. Pharmacist confirms the prescription is valid.
4. System attaches the prescription to the sale.

**Alternate flows**

- Prescription incomplete or illegible: refer back to the prescriber and stop.
- E-prescription fails validation: flag for pharmacist review.

## UC-02 Dispense a medicine

- **Actor:** Pharmacist
- **Precondition:** A validated prescription (or OTC sale) exists.
- **Postcondition:** Dispensing is recorded and traceable to batch and prescription.
- **Related requirements:** FR-DSP-001, FR-DSP-002, FR-DSP-003, FR-DSP-004, FR-DSP-005

**Main flow**

1. System proposes batches (earliest valid expiry first).
2. Pharmacist verifies drug, strength, quantity and batch.
3. Pharmacist confirms; stock is reduced.
4. Label and invoice are produced.

**Alternate flows**

- Requested drug out of stock: offer a substitution (needs pharmacist approval and a recorded reason).
- Partial supply: record the balance quantity.

## UC-03 Record a scheduled-drug supply

- **Actor:** Pharmacist
- **Precondition:** A Schedule H, H1 or X drug is being dispensed.
- **Postcondition:** Register entry exists and is retained for the required period.
- **Related requirements:** FR-REG-001, FR-REG-002, NFR-REG-001, FR-REG-003, FR-REG-004, FR-REG-005, FR-REG-006

**Main flow**

1. System creates the register entry as part of the dispensing.
2. Mandatory fields are checked.
3. Entry is locked against deletion and audit-logged.

**Alternate flows**

- Missing mandatory field: sale cannot be completed.
- Correction needed: add a linked correcting entry with a reason.

## UC-04 Receive stock and manage expiry or recall

- **Actor:** Pharmacist / store keeper
- **Precondition:** A supplier delivery or a recall notice arrives.
- **Postcondition:** Stock, batch and expiry data are accurate.
- **Related requirements:** FR-INV-001, FR-INV-002, FR-INV-003, FR-INV-004

**Main flow**

1. Record batch, expiry and quantity against the supplier invoice.
2. System flags near-expiry batches.
3. On recall, batch is quarantined and the action is recorded.

**Alternate flows**

- Invoice mismatch: hold the goods and note the discrepancy.

## UC-05 Bill a sale

- **Actor:** Pharmacist / cashier
- **Precondition:** Items are dispensed or selected.
- **Postcondition:** Invoice is stored and numbered.
- **Related requirements:** NFR-BIL-001, NFR-BIL-002, NFR-BIL-003, FR-BIL-001, FR-BIL-002

**Main flow**

1. System prices items and applies allowed discounts.
2. GST invoice is generated.
3. Payment is recorded.

**Alternate flows**

- Discount above the limit: needs authorisation.
