"""Risk-analysis agent (plan sections 10, 11, 12): per-requirement risk level and a
threat/hazard register with likelihood x impact scoring."""
import re

from ..schemas import RiskItem, Requirement

CAT_WEIGHT = {"patient_safety": 5, "regulatory": 4, "security": 4, "privacy": 4, "audit_reporting": 3, "data_management": 3,
              "integration": 3, "availability": 3, "performance": 2, "usability": 1, "operational": 2, "business": 1, "functional": 1}
BUMP = re.compile(r"wrong|batch|expir|recall|schedule|\bh1\b|\bx\b|narcotic|psychotropic|substitut|override|delet", re.I)


def level(score: int) -> str:
    return "Critical" if score >= 7 else "High" if score >= 5 else "Medium" if score >= 3 else "Low"


def assess_requirement(r: Requirement) -> None:
    s = max((CAT_WEIGHT.get(c, 1) for c in r.categories), default=1)
    if BUMP.search(r.statement):
        s += 1
    if any(i.kind == "conflict" for i in r.issues):
        s += 1
    if any(i.kind == "out_of_scope" for i in r.issues):
        s += 2
    r.risk_score = s
    r.risk_level = level(s)


# id, title, category, trigger regex (on joined statements), L, I, mitigation, verification
TEMPLATES = [
    ("HZ-01", "Wrong drug, strength or quantity dispensed", "patient_safety", r"dispens|substitut|prescription|strength|label", 3, 5,
     "Mandatory pharmacist verification step; barcode/batch check; substitution recorded with reason.", "Dispensing-accuracy test set; pharmacist UAT."),
    ("HZ-02", "Expired or recalled batch sold", "patient_safety", r"expir|recall|batch|fefo", 3, 5,
     "Block sale of expired/recalled batches; FEFO picking; recall quarantine workflow.", "Batch-integrity and expiry boundary tests."),
    ("RG-01", "Incomplete or missing scheduled-drug register entry (inspection finding)", "regulatory", r"h1|schedule|register|ndps|narcotic|psychotropic", 3, 4,
     "Register entry is created atomically with the sale; mandatory fields enforced.", "Register completeness test; mock inspection."),
    ("RG-02", "Regulated records edited or deleted without trace", "regulatory", r"register|record|delet|edit|audit|retain|retention", 2, 4,
     "No deletion; corrections as new linked entries; hash-chained audit trail.", "Tamper test; audit-trail review."),
    ("RG-03", "Schedule lists or rules change and software is out of date", "regulatory", r"schedule|rule|regulation|updat|change|list", 3, 3,
     "Configurable schedule lists with versioning and an owner for change control.", "Change-control drill: update list, verify behaviour."),
    ("SC-01", "Unauthorised access to patient or prescription data", "security", r"patient|prescription|access|role|login|password|data", 3, 4,
     "RBAC, least privilege, MFA for privileged actions, encryption, access logging.", "Access-control tests; threat model review."),
    ("SC-02", "Unauthorised override of a safety or compliance control", "security", r"override|bypass|skip|waive", 2, 4,
     "Override needs authorised role, recorded reason and audit entry.", "Negative tests for override paths."),
    ("PV-01", "Personal data used beyond purpose / not minimised", "privacy", r"patient|personal|consent|contact|privacy", 2, 3,
     "Collect minimum data; purpose and consent recorded; masking in non-clinical views.", "Privacy review; data-flow check."),
    ("PF-01", "Peak-hour billing slowdown causes queues and workarounds", "performance", r"bill|fast|quick|peak|queue|second|speed", 3, 2,
     "Performance target; keep mandatory fields few and auto-filled where possible.", "Load test at peak; usability timing test."),
    ("AV-01", "Downtime or connectivity loss stops dispensing", "availability", r"offline|downtime|available|backup|internet|power", 3, 3,
     "Offline-capable counter mode and tested backup/restore.", "Failover and restore drill."),
    ("IN-01", "Integration with legacy billing/inventory corrupts data", "integration", r"integrat|tally|erp|legacy|import|export|interface|sync", 3, 3,
     "Defined interface contract, reconciliation report, staged cut-over.", "Integration and reconciliation tests."),
]
PLATFORM_RISKS = [
    ("AI-01", "LLM hallucination invents a requirement or a rule", "ai_platform", 3, 4, "Grounding check on every proposal (verbatim quote), RAG citations, confidence scores, human approval.", "Hallucination-rate metric in evaluation."),
    ("AI-02", "Prompt injection through uploaded stakeholder documents", "ai_platform", 2, 4, "Input screening, untrusted-text delimiters, JSON-only outputs, no tool access for agents.", "Injection test document in the sample set."),
    ("AI-03", "Sensitive data sent to an LLM", "ai_platform", 2, 4, "PII masking before any LLM call; synthetic data only in the prototype.", "Masking unit tests."),
    ("AI-04", "Outdated or wrong regulatory text in the knowledge base", "ai_platform", 3, 4, "Versioned KB, 'verified' flag, official source check before use, regulator-facing claims need human sign-off.", "KB review checklist before each release."),
    ("AI-05", "Over-trust: AI output treated as legal or clinical advice", "ai_platform", 2, 5, "Scope guard, 'candidate mapping' wording, mandatory approvals by qualified roles.", "Approval-gate tests."),
]


def build_register(reqs: list[Requirement]) -> list[RiskItem]:
    active = [r for r in reqs if r.approval_status != "rejected"]
    items = []
    for rid, title, cat, rx, L, I, mit, ver in TEMPLATES:
        linked = [r.id for r in active if re.search(rx, r.statement, re.I)]
        if linked:
            items.append(RiskItem(id=rid, title=title, category=cat, likelihood=L, impact=I, score=L * I, rating=_rating(L * I), mitigation=mit, verification=ver, req_ids=linked))
    for rid, title, cat, L, I, mit, ver in PLATFORM_RISKS:
        items.append(RiskItem(id=rid, title=title, category=cat, likelihood=L, impact=I, score=L * I, rating=_rating(L * I), mitigation=mit, verification=ver, req_ids=[]))
    return sorted(items, key=lambda x: -x.score)


def _rating(score: int) -> str:
    return "Critical" if score >= 15 else "High" if score >= 10 else "Medium" if score >= 5 else "Low"


def run(reqs: list[Requirement]) -> list[RiskItem]:
    for r in reqs:
        assess_requirement(r)
    return build_register(reqs)
