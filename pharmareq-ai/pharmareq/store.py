"""Run persistence (SQLite) and the human-approval rules (plan section 16)."""
import sqlite3
import threading

from . import config
from .schemas import Requirement, Run

_lock = threading.Lock()


def _conn():
    c = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    c.execute("CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, created TEXT, project TEXT, payload TEXT)")
    return c


def save_run(run: Run):
    with _lock:
        c = _conn()
        c.execute(
            "INSERT OR REPLACE INTO runs(run_id,created,project,payload) VALUES (?,?,?,?)",
            (run.run_id, run.created, run.project_name, run.model_dump_json()),
        )
        c.commit()
        c.close()


def get_run(run_id: str) -> Run | None:
    c = _conn()
    row = c.execute("SELECT payload FROM runs WHERE run_id=?", (run_id,)).fetchone()
    c.close()
    return Run.model_validate_json(row[0]) if row else None


def list_runs() -> list[dict]:
    c = _conn()
    rows = c.execute("SELECT run_id,created,project FROM runs ORDER BY created DESC LIMIT 50").fetchall()
    c.close()
    return [{"run_id": r[0], "created": r[1], "project": r[2]} for r in rows]


# ---------------------------------------------------------------- approvals
def roles_allowed_for(req: Requirement) -> set[str]:
    """Which roles may accept/reject a requirement. Mandatory-approval categories are stricter."""
    P = config.ROLE_PERMISSIONS
    allowed = set(P["approve_general"])
    cats = set(req.categories)
    if "patient_safety" in cats:
        allowed = set(P["approve_patient_safety"])
    elif "regulatory" in cats:
        allowed = set(P["approve_regulatory"])
    elif cats & {"security", "privacy"}:
        allowed = set(P["approve_security"]) | set(P["approve_regulatory"])
    return allowed


def is_mandatory_approval(req: Requirement) -> bool:
    return bool(set(req.categories) & {"patient_safety", "regulatory", "security", "privacy"}) or req.risk_level in ("High", "Critical")


def can_baseline(run: Run) -> tuple[bool, list[str]]:
    reasons = []
    pending = [r.id for r in run.requirements if r.approval_status == "pending"]
    if pending:
        reasons.append(f"{len(pending)} requirement(s) still pending: {', '.join(pending[:8])}")
    open_conf = [c.id for c in run.conflicts if c.status == "open"]
    if open_conf:
        reasons.append(f"{len(open_conf)} open conflict(s): {', '.join(open_conf)}")
    if run.sdlc:
        missing = [r for r in config.SDLC_SIGNOFF_ROLES if r not in run.sdlc.signoffs]
        if missing:
            reasons.append("SDLC sign-off missing from: " + ", ".join(missing))
    bad = [g for g in run.validation.get("gates", []) if g["status"] == "fail" and g["blocking"]]
    for g in bad:
        reasons.append(f"Validation gate failed: {g['name']}")
    return (not reasons, reasons)
