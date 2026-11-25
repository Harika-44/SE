"""Quality-analysis + clarification agent (plan sections 7 and 10).

Detects ambiguity, incompleteness, untestable wording, missing source and undefined
terms, and turns each finding into a concrete clarification question for the stakeholder.
"""
import re

from ..llm import llm
from ..schemas import Issue, Requirement

# (regex, issue kind, message, question)
VAGUE = [
    (r"\b(soon|quickly|fast|promptly|real.?time|immediately|asap)\b", "What is the measurable limit (for example seconds, or % of transactions within N seconds)?"),
    (r"\b(user.?friendly|easy|simple|intuitive|convenient)\b", "How should 'ease of use' be judged (for example a new assistant completes a sale in under N minutes after M minutes of training)?"),
    (r"\b(appropriate|suitable|proper|adequate|reasonable|as needed|if needed|if required)\b", "What exactly counts as 'appropriate' here, and who decides?"),
    (r"\b(etc|and so on|and more|things like|such as)\b", "Can you list every item that is meant by the open-ended list?"),
    (r"\b(some|several|many|few|large|small|lots of|a lot|enough)\b", "What number or range do you mean?"),
    (r"\b(regularly|periodically|frequently|often|occasionally)\b", "How often exactly (daily, weekly, per event)?"),
    (r"\b(good|better|best|robust|efficient|flexible|secure|reliable|smooth|seamless)\b", "What observable behaviour or measure would show this is achieved?"),
]
SPECIAL_QUESTIONS = [
    (r"expir", r"\b(soon|near|upcoming)\b", "How many days before expiry should the alert trigger, who receives it, and does it differ for scheduled drugs?"),
]
# (trigger regex, "must also contain" regex, message, question)
INCOMPLETE = [
    (r"\bretain|retention|keep|store", r"\b\d+\s*(day|week|month|year)s?\b", "Retention period is not stated.", "For how long must these records be kept, and which rule or policy sets that period?"),
    (r"\balert|notify|notification|reminder", r"\b(when|if|within|before|after|\d+)\b", "Alert trigger is not stated.", "What event or threshold triggers the alert, and who receives it?"),
    (r"\breport", r"\b(daily|weekly|monthly|yearly|per|format|pdf|csv|excel|on demand)\b", "Report frequency/format is not stated.", "How often is the report needed, in what format, and for whom?"),
    (r"\bintegrat|interface|sync", r"\b(tally|erp|api|csv|hl7|fhir|his|portal|system|software)\b", "Integration target is not named.", "Which external system, data format and direction of exchange are meant?"),
    (r"\bback.?up|restore", r"\b(daily|hourly|weekly|rpo|rto|\d+)\b", "Backup/restore objectives are not stated.", "How much data loss (RPO) and downtime (RTO) is acceptable?"),
    (r"\boverride", r"\b(reason|record|log|pharmacist|authori|approval|owner)\b", "Override rules are incomplete.", "Who may override, must a reason be recorded, and is a second approval needed?"),
    (r"\bdiscount", r"\b(%|percent|limit|maximum|max|owner|approval|authori)\b", "Discount limits/authorisation not stated.", "What is the maximum discount and who must authorise it?"),
    (r"\bsubstitut", r"\b(consent|prescriber|approval|pharmacist|equivalent|same|reason)\b", "Substitution rules are incomplete.", "Under what conditions is substitution allowed, who approves it, and is prescriber/patient consent needed?"),
    (r"\bcontrolled|scheduled drugs?|restricted drugs?", r"\b(h1|h\b|x\b|ndps|schedule [hx]1?)\b", "Which drug schedules are meant is not stated.", "Which schedules (H, H1, X, NDPS) does this apply to?"),
    (r"\b(?:to|shall|should|must|be)\s+(?:be\s+)?(?:record|captur|log)\w*", r"\b(prescriber|patient|batch|quantity|date|drug|name|user|time|field|detail)\b", "Record contents are not stated.", "Which fields must each record contain?"),
]
UNTESTABLE = re.compile(r"\b(always|never|100\s*%|all errors|zero (?:errors|defects)|any situation|completely|totally|every possible)\b", re.I)
ACRONYM = re.compile(r"\b[A-Z]{2,6}\d?\b")
KNOWN_ACRONYMS = {
    "FEFO", "GST", "GSTIN", "HSN", "NDPS", "OTC", "SKU", "PCI", "MFA", "OTP", "RBAC", "UPI", "SRS", "API", "ERP", "PDF", "CSV",
    "HL7", "FHIR", "HIS", "EHR", "ABDM", "UI", "UX", "ID", "SOP", "RX", "H1", "DPDP", "MRP", "QR", "SMS", "PC", "IT", "AI",
    "UAT", "UHID", "MRN", "NMC", "CDSCO", "EOD", "FIFO", "RPO", "RTO", "PAN", "TB", "OK", "CEO", "US", "OCR", "POS", "XML", "JSON",
}
ACTOR = re.compile(r"\b(system|software|app|pharmacist|owner|manager|admin|inspector|auditor|assistant|staff|user|patient|doctor|prescriber|supplier|clerk|cashier)\b", re.I)
SEVERITY_BY_KIND = {"ambiguity": "medium", "incomplete": "medium", "untestable": "low", "missing_source": "high", "undefined_term": "low"}


def _add(req: Requirement, kind, message, question=None, severity=None):
    if any(i.kind == kind and i.message == message for i in req.issues):
        return
    req.issues.append(Issue(kind=kind, message=message, question=question, severity=severity or SEVERITY_BY_KIND.get(kind, "medium")))


def vague_matches(text: str) -> list[tuple[str, str]]:
    """Reused by the interview agent. Returns [(matched word, question)]."""
    out = []
    for rx, q in VAGUE:
        m = re.search(rx, text, re.I)
        if m:
            out.append((m.group(0), q))
    return out


def analyse(req: Requirement) -> Requirement:
    # drop issues from a previous analysis of the same kinds so re-analysis stays idempotent
    req.issues = [i for i in req.issues if i.kind not in SEVERITY_BY_KIND and i.kind != "low_confidence"]
    text = req.statement
    special_done = False
    for trig, vague, q in SPECIAL_QUESTIONS:
        if re.search(trig, text, re.I) and re.search(vague, text, re.I):
            _add(req, "ambiguity", "Vague expiry wording ('soon'/'near').", q)
            special_done = True
    for word, q in vague_matches(text):
        if special_done and word.lower() in ("soon", "near"):
            continue
        _add(req, "ambiguity", f"Vague term '{word}'.", q)
    for trig, must, msg, q in INCOMPLETE:
        if re.search(trig, text, re.I) and not re.search(must, text, re.I):
            _add(req, "incomplete", msg, q)
    if UNTESTABLE.search(text):
        _add(req, "untestable", "Absolute wording cannot be verified by a test.", "Which concrete situations must this cover, and what is the acceptable exception handling?")
    if re.search(r"\b(able to|allow\w*|can|capable)\b", text, re.I) and not ACTOR.search(text):
        _add(req, "incomplete", "No actor is named.", "Who performs this action or receives its result?")
    if not req.source_quote.strip() or not req.source_stakeholder.strip():
        _add(req, "missing_source", "Source quote or stakeholder is missing.", "Who asked for this and in which document?")
    for ac in ACRONYM.findall(text):
        if ac not in KNOWN_ACRONYMS and not re.fullmatch(r"[HX]\d?", ac):
            _add(req, "undefined_term", f"Term '{ac}' is not in the glossary.", f"What does '{ac}' stand for in your pharmacy?")
    return req


def refine_questions(reqs: list[Requirement]) -> None:
    """LLM mode only: make questions context-aware. Falls back silently."""
    if not llm.enabled:
        return
    items = [(r.id, i) for r in reqs for i in r.issues if i.question]
    if not items:
        return
    payload = [{"i": n, "requirement": next(r.statement for r in reqs if r.id == rid), "issue": it.message, "question": it.question} for n, (rid, it) in enumerate(items[:40])]
    out = llm.json(
        "Rewrite each clarification question so it is specific to its requirement, short, and answerable by a pharmacy stakeholder. "
        "Do not add facts. Return JSON list of {\"i\": int, \"question\": str}.",
        str(payload),
    )
    if isinstance(out, list):
        for o in out:
            try:
                items[int(o["i"])][1].question = str(o["question"])[:300]
            except Exception:
                continue


def run(reqs: list[Requirement]) -> list[Requirement]:
    for r in reqs:
        analyse(r)
    refine_questions(reqs)
    return reqs


def clarification_list(reqs: list[Requirement]) -> list[dict]:
    seen, out = set(), []
    for r in reqs:
        for i in r.issues:
            if i.question and (r.id, i.question) not in seen:
                seen.add((r.id, i.question))
                out.append({"req_id": r.id, "stakeholder": r.source_stakeholder, "issue": i.message, "question": i.question, "severity": i.severity})
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(out, key=lambda x: order[x["severity"]])
