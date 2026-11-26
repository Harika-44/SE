# Risk and threat register

> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.

| ID | Risk | Category | L | I | Score | Rating | Mitigation | Verification | Requirements |
|---|---|---|---|---|---|---|---|---|---|
| RG-01 | Incomplete or missing scheduled-drug register entry (inspection finding) | regulatory | 3 | 4 | 12 | High | Register entry is created atomically with the sale; mandatory fields enforced. | Register completeness test; mock inspection. | FR-REG-001 |
| SC-01 | Unauthorised access to patient or prescription data | security | 3 | 4 | 12 | High | RBAC, least privilege, MFA for privileged actions, encryption, access logging. | Access-control tests; threat model review. | NFR-SEC-001, FR-REG-001 |
| AI-01 | LLM hallucination invents a requirement or a rule | ai_platform | 3 | 4 | 12 | High | Grounding check on every proposal (verbatim quote), RAG citations, confidence scores, human approval. | Hallucination-rate metric in evaluation. | platform |
| AI-04 | Outdated or wrong regulatory text in the knowledge base | ai_platform | 3 | 4 | 12 | High | Versioned KB, 'verified' flag, official source check before use, regulator-facing claims need human sign-off. | KB review checklist before each release. | platform |
| AI-05 | Over-trust: AI output treated as legal or clinical advice | ai_platform | 2 | 5 | 10 | High | Scope guard, 'candidate mapping' wording, mandatory approvals by qualified roles. | Approval-gate tests. | platform |
| RG-03 | Schedule lists or rules change and software is out of date | regulatory | 3 | 3 | 9 | Medium | Configurable schedule lists with versioning and an owner for change control. | Change-control drill: update list, verify behaviour. | FR-REG-001 |
| AI-02 | Prompt injection through uploaded stakeholder documents | ai_platform | 2 | 4 | 8 | Medium | Input screening, untrusted-text delimiters, JSON-only outputs, no tool access for agents. | Injection test document in the sample set. | platform |
| AI-03 | Sensitive data sent to an LLM | ai_platform | 2 | 4 | 8 | Medium | PII masking before any LLM call; synthetic data only in the prototype. | Masking unit tests. | platform |
| PV-01 | Personal data used beyond purpose / not minimised | privacy | 2 | 3 | 6 | Medium | Collect minimum data; purpose and consent recorded; masking in non-clinical views. | Privacy review; data-flow check. | FR-REG-001 |
