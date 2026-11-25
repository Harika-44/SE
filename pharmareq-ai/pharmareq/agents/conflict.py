"""Conflict-detection agent (plan section 10): duplicates, numeric mismatches, contradictions,
and stakeholder tensions (for example owner wants speed, inspector wants mandatory fields)."""
import re

from ..schemas import Conflict, Issue, Requirement
from ..text_utils import TfIdf, tokens

NUM = re.compile(r"(\d+(?:\.\d+)?)\s*(second|minute|hour|day|week|month|year|%|percent)s?", re.I)
RELAX = re.compile(r"\b(skip|bypass|without|waive|ignore|optional|not (?:be )?(?:required|needed|mandatory)|no need|not necessary)\b", re.I)
RESTRICT = re.compile(r"\b(mandatory|compulsory|required|cannot|can't|prevent|block|never|not allow\w*|must (?:be )?(?:filled|entered|recorded|captured))\b", re.I)
SPEED = re.compile(r"\b(fast|quick\w*|speed\w*|minimal clicks|without delay|queue|waiting|within \d+ seconds?)\b", re.I)
CONTROL = re.compile(r"\b(mandatory|compulsory|verif\w*|validat\w*|double.?check|must (?:be )?(?:filled|entered|recorded|captured)|required fields?)\b", re.I)
ANCHORS = {"bill", "dispens", "sale", "record", "field", "prescription", "counter", "check", "step", "entry", "drug"}
GENERIC = {"system", "shall", "pharmacist", "user", "pharmacy", "drug", "record", "requir", "retain", "year", "month", "day", "week", "hour", "minute", "second"}

OPTIONS = {
    "duplicate": ["Merge into one requirement and keep the strongest wording.", "Keep both as separate requirements if their scope really differs."],
    "numeric": ["Confirm the correct value with the compliance officer against the official rule.", "Use the stricter value until it is confirmed, and record the assumption."],
    "contradiction": ["Ask the stakeholders to agree one rule.", "Allow the exception only with pharmacist authorisation and a recorded reason."],
    "tension": ["Keep the mandatory control and reduce data-entry effort (defaults, scanning, auto-fill).", "Set a measurable speed target and verify it in a usability test."],
}


def _topic(text: str) -> set[str]:
    return {t for t in tokens(text) if not t.isdigit() and t not in GENERIC and len(t) > 2}


def _all(text: str) -> set[str]:
    return {t for t in tokens(text) if not t.isdigit() and t not in ("system", "software", "shall")}


def _nums(text: str):
    return [(float(v), u.lower().rstrip("s").replace("percent", "%")) for v, u in NUM.findall(text)]


def detect(reqs: list[Requirement], previous: list[Conflict] | None = None) -> list[Conflict]:
    for r in reqs:
        r.issues = [i for i in r.issues if i.kind not in ("conflict", "duplicate")]
    prev = {(frozenset(c.req_ids), c.kind): c for c in (previous or [])}
    if len(reqs) < 2:
        return []
    index = TfIdf([r.statement for r in reqs])
    found: dict[frozenset, Conflict] = {}

    def add(a: Requirement, b: Requirement, kind: str, desc: str, sev: str):
        key = frozenset((a.id, b.id))
        rank = ["duplicate", "tension", "contradiction", "numeric"]
        if key in found and rank.index(found[key].kind) >= rank.index(kind):
            return
        found[key] = Conflict(id="", kind=kind, req_ids=sorted(key), description=desc, severity=sev, resolution_options=OPTIONS[kind])

    for i in range(len(reqs)):
        for j in range(i + 1, len(reqs)):
            a, b = reqs[i], reqs[j]
            shared = _topic(a.statement) & _topic(b.statement)
            na, nb = _nums(a.statement), _nums(b.statement)
            sim = index.pair_sim(i, j)
            if len(_all(a.statement) & _all(b.statement)) >= 3 and na and nb:
                diff = [(x, y) for x, ua in na for y, ub in nb if ua == ub and x != y]
                if diff:
                    add(a, b, "numeric", f"{a.id} says {diff[0][0]:g} but {b.id} says {diff[0][1]:g} for the same subject ({', '.join(sorted(_all(a.statement) & _all(b.statement) - {'year','month','day'})[:4])}).", "high")
                    continue
            if len(shared) >= 2 and ((RELAX.search(a.statement) and RESTRICT.search(b.statement)) or (RELAX.search(b.statement) and RESTRICT.search(a.statement))):
                add(a, b, "contradiction", f"One requirement relaxes a rule that the other makes mandatory ({', '.join(sorted(shared)[:4])}).", "high")
                continue
            anchors = (set(tokens(a.statement)) & set(tokens(b.statement))) & ANCHORS
            if anchors and a.source_stakeholder != b.source_stakeholder and (
                (SPEED.search(a.statement) and CONTROL.search(b.statement)) or (SPEED.search(b.statement) and CONTROL.search(a.statement))
            ):
                add(a, b, "tension", f"Speed expectation ({a.source_stakeholder if SPEED.search(a.statement) else b.source_stakeholder}) vs control expectation ({b.source_stakeholder if SPEED.search(a.statement) else a.source_stakeholder}) on the same workflow.", "medium")
                continue
            if sim >= 0.70:
                who = "different stakeholders" if a.source_stakeholder != b.source_stakeholder else "the same stakeholder"
                add(a, b, "duplicate", f"Near-duplicate wording from {who} (similarity {sim:.2f}).", "low")

    conflicts = []
    for n, c in enumerate(sorted(found.values(), key=lambda c: c.req_ids), 1):
        c.id = f"CF-{n:03d}"
        old = prev.get((frozenset(c.req_ids), c.kind))
        if old and old.status == "resolved":
            c.status, c.resolution_note = "resolved", old.resolution_note
        conflicts.append(c)
        for rid in c.req_ids:
            r = next(x for x in reqs if x.id == rid)
            kind = "duplicate" if c.kind == "duplicate" else "conflict"
            r.issues.append(
                Issue(kind=kind, message=f"{c.id} ({c.kind}): {c.description}", severity=c.severity, related=[x for x in c.req_ids if x != rid],
                      question="Which wording or value is correct?" if kind == "conflict" else None)
            )
            if kind == "conflict":
                r.needs_human = True
    return conflicts
