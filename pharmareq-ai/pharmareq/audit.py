"""Tamper-evident audit trail (plan sections 17 and 20).

Every prompt, retrieved evidence item, agent decision, approval and generated artifact is
appended to a hash chain: each row's hash covers the previous row's hash, so editing or
deleting any past row breaks verification.
"""
import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timezone

from . import config

_lock = threading.Lock()


def _conn():
    c = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    c.execute(
        """CREATE TABLE IF NOT EXISTS audit(
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, run_id TEXT, actor TEXT,
            action TEXT, payload TEXT, prev_hash TEXT, hash TEXT)"""
    )
    return c


def _digest(prev, ts, run_id, actor, action, payload):
    return hashlib.sha256("|".join([prev, ts, run_id or "", actor, action, payload]).encode()).hexdigest()


def log(run_id: str | None, actor: str, action: str, payload: dict | None = None) -> str:
    payload_s = json.dumps(payload or {}, sort_keys=True, default=str)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _lock:
        c = _conn()
        row = c.execute("SELECT hash FROM audit ORDER BY id DESC LIMIT 1").fetchone()
        prev = row[0] if row else "GENESIS"
        h = _digest(prev, ts, run_id, actor, action, payload_s)
        c.execute(
            "INSERT INTO audit(ts,run_id,actor,action,payload,prev_hash,hash) VALUES (?,?,?,?,?,?,?)",
            (ts, run_id, actor, action, payload_s, prev, h),
        )
        c.commit()
        c.close()
    return h


def entries(run_id: str | None = None, limit: int = 500) -> list[dict]:
    c = _conn()
    q = "SELECT id,ts,run_id,actor,action,payload,hash FROM audit"
    args: tuple = ()
    if run_id:
        q += " WHERE run_id=?"
        args = (run_id,)
    q += " ORDER BY id DESC LIMIT ?"
    rows = c.execute(q, args + (limit,)).fetchall()
    c.close()
    keys = ["id", "ts", "run_id", "actor", "action", "payload", "hash"]
    return [dict(zip(keys, r)) for r in reversed(rows)]


def verify() -> dict:
    """Recompute the whole chain. Returns {ok, checked, broken_at}."""
    c = _conn()
    rows = c.execute("SELECT id,ts,run_id,actor,action,payload,prev_hash,hash FROM audit ORDER BY id").fetchall()
    c.close()
    prev = "GENESIS"
    for (i, ts, run_id, actor, action, payload, prev_hash, h) in rows:
        if prev_hash != prev or _digest(prev, ts, run_id, actor, action, payload) != h:
            return {"ok": False, "checked": i, "broken_at": i}
        prev = h
    return {"ok": True, "checked": len(rows), "broken_at": None}
