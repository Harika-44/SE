"""Validation agent (plan section 10, 12, 16): completeness, consistency, evidence checks and
baseline gates. A gate marked blocking must pass before a requirement baseline can be approved."""
from .. import config, store
from ..schemas import Run


def _gate(gates, gid, name, ok, detail, blocking=True, warn=False):
    gates.append({"id": gid, "name": name, "status": "pass" if ok else ("warn" if warn else "fail"), "detail": detail, "blocking": blocking and not warn})


def validate(run: Run) -> dict:
    act = [r for r in run.requirements if r.approval_status != "rejected"]
    n = max(1, len(act))
    gates: list[dict] = []
    waived = lambda r: bool(r.waiver_note)

    bad = [r.id for r in act if not r.source_quote.strip() or not r.source_stakeholder.strip()]
    _gate(gates, "V1", "Every requirement has a source", not bad, "OK" if not bad else f"Missing source: {', '.join(bad[:8])}")

    noac = [r.id for r in act if not r.acceptance_criteria]
    _gate(gates, "V2", "Every requirement has acceptance criteria", not noac, "OK" if not noac else f"Missing: {', '.join(noac[:8])}")

    uncited = [r.id for r in act if ({"regulatory", "patient_safety"} & set(r.categories)) and not r.regulations and not waived(r)]
    _gate(gates, "V3", "Regulatory / safety requirements cite a source", not uncited, "OK" if not uncited else f"No citation (accept with a waiver note or add a source): {', '.join(uncited[:8])}")

    open_conf = [c.id for c in run.conflicts if c.kind != "duplicate" and c.status == "open"]
    _gate(gates, "V4", "No open conflicts", not open_conf, "OK" if not open_conf else f"Open: {', '.join(open_conf)}")

    open_dups = [c.id for c in run.conflicts if c.kind == "duplicate" and c.status == "open"]
    _gate(gates, "V5", "Duplicates reviewed", not open_dups, "OK" if not open_dups else f"{len(open_dups)} duplicate pair(s) to merge or keep", blocking=False, warn=True)

    high = [r.id for r in act if any(i.severity == "high" and i.kind not in ("conflict",) for i in r.issues) and not waived(r)]
    _gate(gates, "V6", "No unresolved high-severity issues", not high, "OK" if not high else f"Needs clarification or a waiver note: {', '.join(high[:8])}")

    pend = [r.id for r in act if store.is_mandatory_approval(r) and r.approval_status != "accepted"]
    _gate(gates, "V7", "Mandatory human approvals complete", not pend, "OK" if not pend else f"{len(pend)} awaiting approval")

    _gate(gates, "V8", "Regulatory control gaps decided", not run.gaps, "OK" if not run.gaps else f"{len(run.gaps)} control gap(s): add a requirement or record why not applicable", blocking=False, warn=True)

    miss = [r for r in config.SDLC_SIGNOFF_ROLES if not (run.sdlc and r in run.sdlc.signoffs)]
    _gate(gates, "V9", "SDLC selection signed off", not miss, "OK" if not miss else "Awaiting: " + ", ".join(miss))

    amb = sum(1 for r in act if any(i.kind in ("ambiguity", "incomplete", "undefined_term") for i in r.issues)) / n
    complete = sum(1 for r in act if r.source_quote and r.categories and r.acceptance_criteria and r.risk_level) / n
    total_controls = run.metrics.get("controls_total", 0)
    covered = (1 - len(run.gaps) / total_controls) if total_controls else 1.0
    trace = sum(1 for r in act if r.source_quote and r.acceptance_criteria) / n
    metrics = {
        "requirements_active": len(act), "completeness_pct": round(100 * complete, 1), "ambiguous_pct": round(100 * amb, 1),
        "regulatory_control_coverage_pct": round(100 * covered, 1), "traceability_coverage_pct": round(100 * trace, 1),
        "avg_confidence": round(sum(r.confidence for r in act) / n, 2), "open_conflicts": len(open_conf),
        "low_confidence_escalations": sum(1 for r in act if r.needs_human),
    }
    blocking_fail = [g for g in gates if g["status"] == "fail" and g["blocking"]]
    return {"gates": gates, "metrics": metrics, "baseline_ready": not blocking_fail}
