"""Coordinator agent (plan sections 4 and 16): controls the workflow, passes shared context
between agents, enforces approval gates and writes the audit trail."""
import time
import uuid
from collections import Counter
from datetime import datetime, timezone

from .. import audit, config, privacy, store
from ..llm import llm
from ..schemas import Run, RunRequest, SourceDoc
from . import classification, compliance, conflict, documentation, extraction, quality, risk, sdlc, validation
from .extraction import normalise


def _timed(metrics: dict, name: str, fn, *a, **k):
    t = time.perf_counter()
    out = fn(*a, **k)
    metrics[f"ms_{name}"] = round((time.perf_counter() - t) * 1000, 1)
    return out


def _finish(run: Run, actor: str, regenerate_docs: bool = True) -> Run:
    run.validation = validation.validate(run)
    if regenerate_docs:
        run.artifacts = documentation.generate_all(run)
    store.save_run(run)
    return run


def run_pipeline(req: RunRequest, actor: str = "system") -> Run:
    t_all = time.perf_counter()
    run_id = uuid.uuid4().hex[:8]
    m: dict = {}
    audit.log(run_id, actor, "run_started", {"documents": [d.name for d in req.documents], "mode": llm.mode, "model": config.MODEL if llm.enabled else None})

    docs, pii = [], Counter()
    for d in req.documents:
        text, counts = privacy.mask(d.text)
        pii.update(counts)
        docs.append(SourceDoc(name=d.name, stakeholder=d.stakeholder, text=text))
    audit.log(run_id, "privacy", "pii_masked", dict(pii))

    reqs, flags, context, ext = _timed(m, "extraction", extraction.extract, docs)
    audit.log(run_id, "extraction_agent", "requirements_extracted", {**ext, "count": len(reqs), "injection_flags": len(flags)})
    _timed(m, "classification", classification.run, reqs)
    _timed(m, "quality", quality.run, reqs)
    gaps, cstats = _timed(m, "compliance", compliance.analyse, reqs)
    audit.log(run_id, "compliance_agent", "rag_mapping", {k: v for k, v in cstats.items()})
    conflicts = _timed(m, "conflict", conflict.detect, reqs)
    risks = _timed(m, "risk", risk.run, reqs)
    documentation.add_acceptance_criteria(reqs)
    sd = _timed(m, "sdlc", sdlc.recommend, reqs, req.params, conflicts)
    audit.log(run_id, "sdlc_agent", "recommendation", {"recommended": sd.recommended, "ranking": sd.ranking[:3], "rules": [r.split(":")[0] for r in sd.rules_fired]})

    m.update({"context_notes": context, "controls_total": cstats.get("controls_total", 0), "extraction_proposed": ext["proposed"],
              "extraction_dropped_ungrounded": ext["dropped_ungrounded"],
              "hallucination_rate_pct": round(100 * ext["dropped_ungrounded"] / ext["proposed"], 1) if ext["proposed"] else 0.0,
              "llm_calls": llm.calls, "invalid_llm_citations": cstats.get("invalid_llm_citations", 0)})
    run = Run(run_id=run_id, project_name=req.project_name, created=datetime.now(timezone.utc).isoformat(timespec="seconds"), mode=llm.mode, params=req.params, documents=docs,
              requirements=reqs, conflicts=conflicts, gaps=gaps, risks=risks, sdlc=sd, security_flags=flags, pii_masked=dict(pii), metrics=m)
    m["ms_total_before_docs"] = round((time.perf_counter() - t_all) * 1000, 1)
    _finish(run, actor)
    run.metrics["ms_total"] = round((time.perf_counter() - t_all) * 1000, 1)
    store.save_run(run)
    audit.log(run_id, actor, "run_completed", {"requirements": len(reqs), "conflicts": len(conflicts), "gaps": len(gaps), "baseline_ready": run.validation["baseline_ready"]})
    return run


# ------------------------------------------------------------------ human-in-the-loop
def _load(run_id: str) -> Run:
    run = store.get_run(run_id)
    if not run:
        raise LookupError("run not found")
    return run


def _reanalyse(run: Run, changed: set[str]) -> None:
    for r in run.requirements:
        if r.id in changed:
            r.acceptance_criteria = []
            classification.classify(r)
            quality.analyse(r)
    gaps, cstats = compliance.analyse(run.requirements)
    run.gaps = gaps
    run.metrics["controls_total"] = cstats.get("controls_total", 0)
    run.conflicts = conflict.detect(run.requirements, previous=run.conflicts)
    run.risks = risk.run(run.requirements)
    documentation.add_acceptance_criteria(run.requirements)
    old = run.sdlc
    run.sdlc = sdlc.recommend(run.requirements, run.params, run.conflicts)
    if old and old.recommended == run.sdlc.recommended:
        run.sdlc.signoffs = old.signoffs


def decide(run_id: str, req_id: str, decision: str, user: dict, note: str = "", new_statement: str | None = None) -> Run:
    run = _load(run_id)
    if run.status == "baselined":
        raise RuntimeError("Run is baselined; raise a change request (new run) instead of editing.")
    req = next((r for r in run.requirements if r.id == req_id), None)
    if not req:
        raise LookupError("requirement not found")
    role = user["role"]
    if decision in ("accept", "reject"):
        if role not in store.roles_allowed_for(req):
            raise PermissionError(f"Role '{role}' may not {decision} this requirement; allowed: {', '.join(sorted(store.roles_allowed_for(req)))}")
        if decision == "accept":
            if any(c.status == "open" and c.kind != "duplicate" and req_id in c.req_ids for c in run.conflicts):
                raise ValueError("Resolve the open conflict involving this requirement first.")
            high = [i for i in req.issues if i.severity == "high" and i.kind != "conflict"]
            if high and len(note.strip()) < 10:
                raise ValueError("This requirement has unresolved high-severity issues: modify it, or accept with a waiver note (10+ characters) explaining why.")
            req.waiver_note = note.strip() or None if high else None
            req.approval_status, req.approved_by = "accepted", user["name"]
        else:
            req.approval_status, req.approved_by = "rejected", user["name"]
        audit.log(run_id, user["name"], f"requirement_{decision}ed", {"id": req_id, "role": role, "note": note})
    elif decision in ("modify", "regenerate"):
        if role not in (store.roles_allowed_for(req) | config.ROLE_PERMISSIONS["approve_general"]):
            raise PermissionError(f"Role '{role}' may not change this requirement")
        if decision == "modify":
            if not new_statement or len(new_statement.strip()) < 8:
                raise ValueError("new_statement is required")
            old = req.statement
            req.statement = normalise(new_statement)
            audit.log(run_id, user["name"], "requirement_modified", {"id": req_id, "old": old, "new": req.statement, "note": note})
        else:
            audit.log(run_id, user["name"], "requirement_regenerated", {"id": req_id})
        req.approval_status, req.approved_by, req.waiver_note = "pending", None, None
        _reanalyse(run, {req_id})
    else:
        raise ValueError("decision must be accept, reject, modify or regenerate")
    return _finish(run, user["name"])


def resolve_conflict(run_id: str, conflict_id: str, user: dict, note: str, action: str = "keep") -> Run:
    run = _load(run_id)
    if run.status == "baselined":
        raise RuntimeError("Run is baselined.")
    if user["role"] not in config.ROLE_PERMISSIONS["resolve_conflict"]:
        raise PermissionError("Role may not resolve conflicts")
    if len(note.strip()) < 10:
        raise ValueError("A resolution note (10+ characters) is required")
    c = next((x for x in run.conflicts if x.id == conflict_id), None)
    if not c:
        raise LookupError("conflict not found")
    c.status, c.resolution_note = "resolved", note.strip()
    if action == "merge" and c.kind == "duplicate" and len(c.req_ids) == 2:
        dup = next(r for r in run.requirements if r.id == c.req_ids[1])
        dup.approval_status, dup.approved_by = "rejected", user["name"]
    audit.log(run_id, user["name"], "conflict_resolved", {"id": conflict_id, "action": action, "note": note})
    return _finish(run, user["name"])


def sdlc_signoff(run_id: str, user: dict) -> Run:
    run = _load(run_id)
    if run.status == "baselined":
        raise RuntimeError("Run is baselined.")
    if user["role"] not in config.SDLC_SIGNOFF_ROLES:
        raise PermissionError(f"Only {', '.join(config.SDLC_SIGNOFF_ROLES)} may sign off the SDLC selection")
    run.sdlc.signoffs[user["role"]] = user["name"]
    audit.log(run_id, user["name"], "sdlc_signoff", {"role": user["role"], "model": run.sdlc.recommended})
    return _finish(run, user["name"])


def baseline(run_id: str, user: dict) -> Run:
    run = _load(run_id)
    if user["role"] not in config.ROLE_PERMISSIONS["baseline"]:
        raise PermissionError("Only the project manager may baseline")
    run.validation = validation.validate(run)
    ok, reasons = store.can_baseline(run)
    if not ok:
        raise ValueError("Cannot baseline: " + " | ".join(reasons))
    run.status = "baselined"
    audit.log(run_id, user["name"], "baselined", {"requirements": len(run.requirements)})
    return _finish(run, user["name"])
