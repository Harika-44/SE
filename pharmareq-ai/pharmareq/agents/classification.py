"""Classification agent (plan section 9): multi-label categories, module, ID assignment."""
import re
from collections import defaultdict

from ..schemas import Requirement

CATEGORIES = {
    "patient_safety": r"wrong (?:drug|strength|medicine)|strength|dosage form|interaction|allerg|expir|recall|substitut|verif|double.?check|batch|counsel|illegible|error|mistake|safety|harm|label|quarantin",
    "regulatory": r"schedule|\bh1\b|\bh\b drug|\bx\b|ndps|narcotic|psychotropic|licen[sc]e|inspector|inspection|\blaw\b|legal|regulation|\brules?\b|\bact\b|complian|\bgst|statutory|register|retain|retention|\byears?\b|drug control",
    "security": r"password|login|log in|authenti|authori[sz]|access|\broles?\b|permission|encrypt|\bmfa\b|\botp\b|override|privilege|tamper|unauthori|secur|session|lock",
    "privacy": r"patient (?:data|details|name|record|information)|personal|privacy|confidential|consent|\bmask|anonymi|contact details|phone number|dpdp",
    "performance": r"within \d+|\bseconds?\b|milliseconds?|\bfast|quick|speed|slow|response time|peak|concurrent|throughput|latency|real.?time",
    "availability": r"offline|downtime|uptime|available|availability|backup|restore|power cut|outage|internet|disaster|recover|24x7|24/7|reliab",
    "usability": r"\beasy|simple|user.?friendly|intuitive|screens?\b|\bclicks?\b|training|barcode|scan|shortcut|language|display|font|layout",
    "data_management": r"retain|retention|archive|purge|delet|backup|migrat|import|export|master data|data quality|duplicate|database|history|mandatory field|fields?\b",
    "integration": r"integrat|interface|\bapi\b|tally|\berp\b|hospital|\behr\b|abdm|sync|connect|accounting|printer|scanner|portal|link to",
    "audit_reporting": r"audit|report|inspection|export|print|\blogs?\b|logged|trail|who changed|history|summary|dashboard|statement",
    "operational": r"maintain|support|update|upgrade|monitor|deploy|schedule list|configur|admin|install|handover|rollout",
    "business": r"revenue|profit|cost|margin|loss|customer|discount|credit|turnover|sales|growth|efficien|time saving|stock.?out|wastage|reorder|queue|waiting",
    "functional": r"record|generate|calculate|create|search|print|validat|alert|dispens|bill|\badd\b|update|track|show|display|allow|capture|enter|scan|select|block|flag|notify",
}
NFR_PRIMARY = {"performance", "availability", "security", "privacy", "usability", "operational"}
NFR_TEXT = re.compile(
    r"\b(retain|retention|retained|within \d+|seconds?|minutes?|uptime|availab\w+|backup|encrypt\w*|response time|concurrent|peak|offline|downtime|user.?friendly|easy to|audit trail)\b",
    re.I,
)
MODULES = [
    ("DSP", r"dispens|substitut|counsel|handover|\bsale\b|partial"),
    ("REG", r"\bh1\b|schedule|register|ndps|narcotic|psychotropic|\bx\b drug|scheduled"),
    ("INV", r"stock|batch|expir|inventory|fefo|recall|goods|reorder|shelf"),
    ("BIL", r"\bbill|invoice|\bgst|discount|payment|credit note|price|checkout|counter"),
    ("RX", r"prescription|\brx\b|prescriber|e-prescription"),
    ("SUP", r"supplier|purchase|return|distributor|order"),
    ("AUD", r"audit|inspect|report|trail"),
    ("SEC", r"login|password|access|\broles?\b|encrypt|secur|authenti|override"),
    ("PRV", r"patient data|privacy|consent|personal|confidential"),
]
DEPENDS = {"DSP": ["RX"], "REG": ["DSP"], "BIL": ["DSP"], "AUD": ["REG", "DSP"], "INV": []}
JUSTIFY = {
    "patient_safety": "Reduces the risk of dispensing errors and patient harm.",
    "regulatory": "Supports regulatory compliance and inspection readiness.",
    "security": "Protects regulated records and patient data from misuse.",
    "privacy": "Protects personal data of patients.",
    "performance": "Keeps counter operations fast enough for daily use.",
    "audit_reporting": "Provides evidence for audits and inspections.",
    "business": "Supports pharmacy business efficiency.",
}


def _score(text: str) -> dict[str, int]:
    low = text.lower()
    return {c: len(re.findall(rx, low)) for c, rx in CATEGORIES.items()}


def classify(req: Requirement) -> Requirement:
    scores = _score(req.statement)
    cats = [c for c, s in sorted(scores.items(), key=lambda x: -x[1]) if s > 0 and c not in ("functional", "business")][:4]
    if scores["business"] and (req.source_stakeholder.lower().startswith(("owner", "pharmacy owner", "manager")) or not cats):
        cats.append("business")
    if scores["functional"] or not cats:
        cats.insert(0, "functional") if not (cats and cats[0] in NFR_PRIMARY) else cats.append("functional")
    req.categories = list(dict.fromkeys(cats))
    if {"regulatory", "patient_safety"} & set(req.categories):
        req.priority = "Must"
    mod_scores = {m: len(re.findall(rx, req.statement.lower())) for m, rx in MODULES}
    best = max(mod_scores.values())
    req.module = next((m for m, _ in MODULES if mod_scores[m] == best), "GEN") if best else "GEN"
    if not req.justification:
        req.justification = next((JUSTIFY[c] for c in req.categories if c in JUSTIFY), "Requested by the stakeholder.")
    return req


def req_type(req: Requirement) -> str:
    if NFR_TEXT.search(req.statement):
        return "NFR"
    return "NFR" if req.categories and req.categories[0] in NFR_PRIMARY else "FR"


def assign_ids(reqs: list[Requirement]) -> None:
    counters: dict[str, int] = defaultdict(int)
    for r in reqs:
        key = f"{req_type(r)}-{r.module}"
        counters[key] += 1
        r.id = f"{key}-{counters[key]:03d}"
    first = {}
    for r in reqs:
        first.setdefault(r.module, r.id)
    for r in reqs:
        deps = [first[m] for m in DEPENDS.get(r.module, []) if m in first and first[m] != r.id]
        r.dependencies = deps


def run(reqs: list[Requirement]) -> list[Requirement]:
    for r in reqs:
        classify(r)
    assign_ids(reqs)
    return reqs
