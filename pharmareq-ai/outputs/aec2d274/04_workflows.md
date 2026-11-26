# Process workflows

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

## Prescription to dispensing

```mermaid
flowchart TD
  A[Prescription presented] --> B{Complete and valid?}
  B -- no --> C[Refer back to prescriber]
  B -- yes --> D[Capture prescriber, patient, drug]
  D --> E{Scheduled drug H / H1 / X?}
  E -- yes --> F[Create register entry and keep prescription copy as required]
  E -- no --> G[Select batch - earliest valid expiry]
  F --> G
  G --> H[Pharmacist verifies drug, strength, quantity, batch]
  H --> I[Dispense, label, bill]
  I --> J[Audit entry written]
```

## Goods receipt to stock

```mermaid
flowchart TD
  A[Supplier delivery] --> B[Check against invoice]
  B --> C[Record batch, expiry, quantity]
  C --> D[Stock available - FEFO]
  D --> E{Near expiry or recalled?}
  E -- near expiry --> F[Alert owner]
  E -- recalled --> G[Quarantine and record action]
  E -- no --> H[Normal dispensing]
```
