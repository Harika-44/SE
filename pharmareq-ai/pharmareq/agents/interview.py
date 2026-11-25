"""Stakeholder interaction agent (plan section 7): adaptive interviews instead of a fixed
questionnaire. It picks the next uncovered topic for the stakeholder's role, skips topics
the stakeholder already covered, and asks a follow-up when an answer is vague."""
import re
import uuid

from . import quality

# id, role set ('*' = everyone), question, coverage regex
TOPICS = [
    ("objectives", {"*"}, "What kind of pharmacy is this (retail, hospital, e-pharmacy) and what do you want the software to achieve?", r"retail|hospital|e-?pharmacy|goal|objective|achieve"),
    ("users", {"pharmacist", "owner", "pharmacy owner", "manager"}, "Who uses the system at the counter, and what should each role be allowed to do?", r"role|assistant|cashier|permission|allowed to"),
    ("workflow", {"pharmacist", "assistant", "pharmacy assistant"}, "Walk me through what happens from the moment a prescription arrives until the medicine is handed over.", r"workflow|first|then|after that|step"),
    ("rx_intake", {"pharmacist", "doctor", "prescriber"}, "How do prescriptions arrive (handwritten, printed, e-prescription) and what must be checked before you accept one?", r"handwritten|printed|e-?prescription|prescriber|registration|signature"),
    ("rules", {"pharmacist"}, "Which rules apply to substitution, partial supply and refills?", r"substitut|partial|refill|generic"),
    ("exceptions", {"pharmacist"}, "What do you do when a prescription is illegible, a drug is out of stock, a batch has expired, or an alert appears?", r"illegible|out of stock|expired|alert|exception"),
    ("scheduled", {"pharmacist", "inspector", "drug inspector", "owner", "pharmacy owner", "compliance officer"}, "Which scheduled drugs (H, H1, X, NDPS) do you handle, and what is recorded for each supply?", r"\bh1\b|schedule|ndps|narcotic|register"),
    ("retention", {"pharmacist", "inspector", "drug inspector", "owner", "pharmacy owner", "compliance officer"}, "How long do you keep each type of record, and which rule sets that period?", r"retain|keep .* (?:year|month)|retention|\d+\s*years?"),
    ("authority", {"owner", "pharmacy owner", "pharmacist", "inspector", "drug inspector"}, "Who may override an alert or correct a record, and must they give a reason?", r"override|authori|approve|reason|correct"),
    ("patient_data", {"pharmacist", "owner", "pharmacy owner", "doctor"}, "Which patient details do you collect, why, and who may see them?", r"patient (?:name|detail|data)|contact|consent|privacy"),
    ("billing", {"owner", "pharmacy owner", "pharmacist"}, "How are bills, discounts and GST handled today, and what slows billing at peak hours?", r"\bbill|discount|\bgst|invoice|peak"),
    ("audit", {"inspector", "drug inspector", "owner", "pharmacy owner", "auditor", "compliance officer"}, "What do inspectors or auditors ask to see, and how quickly must you produce it?", r"inspect|audit|report|produce|show"),
    ("performance", {"owner", "pharmacy owner", "pharmacist"}, "What is acceptable speed at the counter at peak time, and what must still work when the internet or power fails?", r"seconds?|offline|power|internet|downtime|speed"),
    ("integration", {"owner", "pharmacy owner", "doctor", "manager"}, "Which existing billing, inventory or hospital systems must this software work with?", r"tally|erp|integrat|existing|hospital|software"),
    ("constraints", {"owner", "pharmacy owner", "manager"}, "What budget, deadline and compliance constraints must we respect?", r"budget|deadline|month|constraint|cost"),
]
SESSIONS: dict[str, dict] = {}


def _topics_for(role: str):
    r = role.lower().strip()
    return [t for t in TOPICS if "*" in t[1] or r in t[1]] or [t for t in TOPICS if "*" in t[1] or "pharmacist" in t[1]]


def start(role: str) -> dict:
    sid = uuid.uuid4().hex[:8]
    s = {"id": sid, "role": role.strip().title() or "Stakeholder", "covered": set(), "turns": [], "current": None, "followed_up": set()}
    SESSIONS[sid] = s
    return _next(s)


def _next(s: dict) -> dict:
    todo = [t for t in _topics_for(s["role"]) if t[0] not in s["covered"]]
    if not todo:
        s["current"] = None
        return {"session_id": s["id"], "done": True, "question": "Thank you - that covers the main topics. You can now submit this interview as a source document.", "remaining": 0, "transcript": transcript(s)}
    s["current"] = todo[0]
    return {"session_id": s["id"], "done": False, "question": todo[0][2], "topic": todo[0][0], "remaining": len(todo), "transcript": transcript(s)}


def answer(session_id: str, text: str) -> dict:
    s = SESSIONS.get(session_id)
    if not s:
        raise LookupError("unknown interview session")
    cur = s["current"]
    s["turns"].append((cur[2] if cur else "", text))
    if cur:
        s["covered"].add(cur[0])
    for t in _topics_for(s["role"]):  # adaptive: skip topics already answered in passing
        if re.search(t[3], text, re.I):
            s["covered"].add(t[0])
    vague = quality.vague_matches(text)
    if vague and cur and cur[0] not in s["followed_up"]:
        s["followed_up"].add(cur[0])
        word, q = vague[0]
        s["covered"].discard(cur[0])
        return {"session_id": s["id"], "done": False, "question": f"You said '{word}'. {q}", "topic": cur[0], "remaining": len([t for t in _topics_for(s["role"]) if t[0] not in s["covered"]]), "transcript": transcript(s), "followup": True}
    return _next(s)


def transcript(s: dict) -> str:
    return "\n".join(f"{s['role']}: {a}" for _, a in s["turns"])
