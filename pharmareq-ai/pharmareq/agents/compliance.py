"""Compliance agent (plan sections 6 and 11).

Retrieval-grounded mapping of each requirement to knowledge-base entries, with citations,
confidence, and escalation. It never makes legal determinations and never specifies
clinical logic: it only proposes *candidate* mappings for a pharmacist / compliance officer.
"""
import re

from .. import config
from ..kb import retriever
from ..llm import llm
from ..schemas import Gap, Issue, RegRef, Requirement
from ..text_utils import tokens

CLINICAL = re.compile(
    r"\b(recommend\w*\s+(?:a\s+|the\s+|an\s+)?(?:correct\s+|right\s+|suitable\s+)?(?:dose|dosage|drug|medicine|treatment|alternative)|suggest\w*\s+(?:a\s+)?(?:dose|dosage|medicine|drug)|"
    r"diagnos\w+|decide\w*\s+(?:the\s+)?(?:dose|dosage)|correct dose|calculate\w*\s+(?:the\s+)?dos\w+|interaction advice|clinical decision|contraindicat\w+)\b",
    re.I,
)
LEGAL = re.compile(r"\b(legal opinion|legally (?:valid|binding) decision|decide (?:if|whether) .{0,30}(?:legal|lawful)|determine .{0,20}legality)\b", re.I)
CORE = {"DCR-SCHED-H", "DCR-SCHED-H1", "DCR-SCHED-X", "DCR-LICENCE-PHARMACIST", "PCI-PPR-2015", "WHO-DATA-INTEGRITY", "DPDP-2023", "ISO-27001-AC"}
OPTIONAL_MODULES = {"DCR-EXPIRY-RECALL": {"INV"}, "ORG-POL-STOCK": {"INV", "SUP"}, "GST-INVOICE": {"BIL"}, "TELE-2020": {"RX"}, "TELEMED-2020": {"RX"}, "NDPS-1985": {"REG"}, "ORG-SOP-DISPENSING": {"DSP"}, "GAMP5-CSV": set()}
REG_PREFIX = ("DCR", "NDPS", "GST", "TELE", "PCI")


def _rationale(req: Requirement, entry: dict) -> str:
    q = set(tokens(req.statement))
    kw = set()
    for k in entry["keywords"]:
        kw |= set(tokens(k))
    hit = sorted(q & (kw | set(tokens(entry["title"]))))[:6]
    return ("Matched terms: " + ", ".join(hit)) if hit else "Weak lexical match - needs human review."


def _llm_rationales(reqs: list[Requirement], cands: dict[str, list[tuple[dict, float]]]) -> dict | None:
    if not llm.enabled:
        return None
    payload = [
        {"id": r.id, "statement": r.statement, "candidates": [{"kb_id": e["id"], "summary": e["summary"]} for e, _ in cands[r.id]]}
        for r in reqs
        if cands[r.id]
    ][:40]
    if not payload:
        return {}
    out = llm.json(
        "For each requirement decide which candidate regulation summaries are genuinely relevant. Use ONLY the provided summaries; do not "
        "invent rules, clause numbers or periods. Do not make legal determinations. Return a JSON list of "
        "{\"id\": str, \"kb_id\": str, \"relevant\": bool, \"rationale\": str (one sentence, grounded in the summary)}.",
        str(payload),
        max_tokens=3500,
    )
    return {(o.get("id"), o.get("kb_id")): o for o in out if isinstance(o, dict)} if isinstance(out, list) else None


def analyse(reqs: list[Requirement]) -> tuple[list[Gap], dict]:
    stats = {"cited": 0, "invalid_llm_citations": 0, "escalated": 0}
    active = [r for r in reqs if r.approval_status != "rejected"]
    cands = {r.id: retriever.retrieve(r.statement) for r in reqs}
    judged = _llm_rationales(reqs, cands)
    for r in reqs:
        r.regulations = []
        r.issues = [i for i in r.issues if i.kind not in ("out_of_scope",) and not (i.kind == "low_confidence")]
        for entry, score in cands[r.id]:
            rationale = _rationale(r, entry)
            if judged is not None:
                j = judged.get((r.id, entry["id"]))
                if j is None:
                    stats["invalid_llm_citations"] += 0  # model skipped it: keep lexical mapping
                elif not j.get("relevant", True):
                    continue
                else:
                    rationale = str(j.get("rationale", rationale))[:300]
            r.regulations.append(
                RegRef(kb_id=entry["id"], title=entry["title"], source=entry["source"], jurisdiction=entry["jurisdiction"],
                       effective_date=entry["effective_date"], version=entry["version"], verified=entry["verified"], score=score, rationale=rationale)
            )
            stats["cited"] += 1
        best = max((x.score for x in r.regulations), default=0.0)
        if r.regulations:
            r.confidence = round(min(0.95, 0.7 * r.confidence + 0.3 * min(1.0, best * 2.5) + 0.05), 2)
            if best >= 0.3:
                if any(x.kb_id.startswith(REG_PREFIX) for x in r.regulations) and "regulatory" not in r.categories:
                    r.categories.append("regulatory")
                if any(x.kb_id.startswith("DPDP") for x in r.regulations) and "privacy" not in r.categories:
                    r.categories.append("privacy")
        if "regulatory" in r.categories:
            r.priority = "Must"
            if not r.regulations:
                r.confidence = round(max(0.2, r.confidence - 0.15), 2)
                r.issues.append(Issue(kind="low_confidence", severity="high",
                                      message="Regulatory requirement with no supporting source retrieved.",
                                      question="Which rule, schedule or policy does this requirement come from?"))
                r.needs_human = True
                stats["escalated"] += 1
        if CLINICAL.search(r.statement):
            if "patient_safety" not in r.categories:
                r.categories.append("patient_safety")
            r.issues.append(Issue(kind="out_of_scope", severity="high",
                                  message="Clinical decision support: this tool does not define clinical logic (doses, interactions, treatment). "
                                          "Treat as a separate regulated feature that needs a qualified pharmacist and a validated drug database."))
            r.needs_human = True
        if LEGAL.search(r.statement):
            r.issues.append(Issue(kind="out_of_scope", severity="high", message="Requires a legal determination; route to the compliance/legal officer. This tool does not decide legality."))
            r.needs_human = True
        if r.confidence < config.LOW_CONFIDENCE:
            r.needs_human = True
    gaps, total = coverage_gaps(active, cands)
    stats["controls_total"] = total
    return gaps, stats


def coverage_gaps(active: list[Requirement], cands) -> tuple[list[Gap], int]:
    modules = {r.module for r in active}
    retrieved = {e["id"] for r in active for e, _ in cands.get(r.id, [])}
    gaps, total = [], 0
    for entry in retriever.all_entries():
        in_scope = entry["id"] in CORE or entry["id"] in retrieved or bool(OPTIONAL_MODULES.get(entry["id"], set()) & modules)
        if not in_scope:
            continue
        for ctl in entry["controls"]:
            total += 1
            if not any(retriever.control_matches(ctl, r.statement) for r in active):
                gaps.append(Gap(kb_id=entry["id"], control=ctl["id"], description=ctl["description"], suggested_requirement=ctl["suggested"],
                                severity="high" if entry["id"].startswith(("DCR", "NDPS", "DPDP")) else "medium"))
    return gaps, total
