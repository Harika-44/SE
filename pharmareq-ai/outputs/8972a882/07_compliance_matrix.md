# Compliance matrix

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

Mappings are candidates found by retrieval. The knowledge base is unverified until a compliance officer checks each entry against the official text.

| Requirement | Statement | Candidate rules (score) | Confidence | Risk | Human review |
|---|---|---|---|---|---|
| NFR-SEC-001 | The system must require two-factor authentication for all pharmacist logins. | ISO-27001-AC (0.23) | 0.78 | High | no |

## Control gaps (no requirement covers the control)

| Rule | Control | Suggested requirement (for the analyst to consider) | Severity |
|---|---|---|---|
| DCR-SCHED-H | Block sale of Schedule H drugs without a valid prescription | The system shall not allow a Schedule H drug to be dispensed unless a valid prescription is attached to the sale. | high |
| DCR-SCHED-H1 | Maintain a separate Schedule H1 register entry for each supply | The system shall create a Schedule H1 register entry (patient, prescriber, drug, batch, quantity, date) for every H1 dispensing. | high |
| DCR-SCHED-H1 | Retain H1 records for the legally required period | The system shall retain Schedule H1 register entries for the legally required period (to be confirmed by the compliance officer) and prevent their deletion. | high |
| DCR-SCHED-X | Retain a copy of the prescription for Schedule X supply | The system shall store a copy of the prescription for every Schedule X supply and link it to the register entry. | high |
| DCR-SCHED-X | Record every Schedule X supply | The system shall record every Schedule X supply in the scheduled-drug register. | high |
| NDPS-1985 | Accurate stock and supply records for NDPS substances | The system shall keep an accurate stock and supply record for NDPS substances and support inspection reports. | high |
| DCR-LICENCE-PHARMACIST | Produce purchase/sale records for the inspector | The system shall produce purchase, sale and scheduled-drug records on demand for a drug inspector. | high |
| PCI-PPR-2015 | Pharmacist verification step before handing over the drug | The system shall require an explicit pharmacist verification step (drug, strength, quantity, batch) before a dispensing is completed. | medium |
| PCI-PPR-2015 | Record every substitution with reason | The system shall record every drug substitution with the original drug, the substitute, the reason and the approving pharmacist. | medium |
| DPDP-2023 | Collect only needed patient data, for a stated purpose | The system shall collect only the patient data needed for dispensing and record the purpose and consent status. | high |
| DPDP-2023 | Protect personal data (access control, encryption, masking) | The system shall protect patient and prescription data with role-based access, encryption in transit and at rest, and masking in non-clinical views. | high |
| DPDP-2023 | Detect and report personal-data breaches | The system shall log access to patient data and support breach investigation and notification. | high |
| WHO-DATA-INTEGRITY | Audit trail with user, time and reason for every record change | The system shall keep an audit trail (user, timestamp, old value, new value, reason) for every change to dispensing, stock and register records. | medium |
| WHO-DATA-INTEGRITY | Prevent deletion or silent overwrite of regulated records | The system shall prevent deletion of regulated records; corrections shall be added as new entries that reference the original. | medium |
| ISO-27001-AC | Role-based access with least privilege | The system shall enforce role-based access control with least privilege for pharmacist, assistant, owner and auditor roles. | medium |
