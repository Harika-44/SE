"""REST API + web UI. Demo authentication: an API key in the X-API-Key header maps to a user and
role (config/users.json). MFA, TLS and encryption at rest are NOT implemented in the prototype."""
from pathlib import Path
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from . import __version__, audit, config, store
from .agents import coordinator, interview, quality
from .llm import llm
from .schemas import RunRequest, SourceDoc

app = FastAPI(title="PharmaReq AI", version=__version__)
WEB = Path(__file__).parent / "web"
SAMPLES = Path(config.ROOT) / "data" / "samples"


def user(x_api_key: str | None = Header(default=None)) -> dict:
    u = config.USERS.get(x_api_key or "")
    if not u:
        raise HTTPException(401, "Missing or invalid X-API-Key")
    return u


def _call(fn, *a, **k):
    try:
        return fn(*a, **k)
    except PermissionError as e:
        raise HTTPException(403, str(e))
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(409, str(e))


class Decision(BaseModel):
    decision: str  # accept|reject|modify|regenerate
    note: str = ""
    new_statement: str | None = None


class Resolve(BaseModel):
    note: str
    action: str = "keep"  # keep|merge


class Answer(BaseModel):
    session_id: str
    answer: str


class Start(BaseModel):
    role: str


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": __version__, "mode": llm.mode, "model": config.MODEL if llm.enabled else None,
            "users": [{"key": k, "name": v["name"], "role": v["role"]} for k, v in config.USERS.items()]}


@app.get("/api/samples")
def samples():
    out = []
    for p in sorted(SAMPLES.glob("*.txt")):
        t = p.read_text()
        first = t.splitlines()[0] if t else ""
        st = first.split(":", 1)[1].strip() if first.lower().startswith("# stakeholder") else p.stem
        out.append({"name": p.name, "stakeholder": st, "text": t})
    return out


@app.post("/api/runs")
def create_run(req: RunRequest, u: dict = Depends(user)):
    if u["role"] not in config.ROLE_PERMISSIONS["run_pipeline"]:
        raise HTTPException(403, "Only analyst or project_manager may start a run")
    if not req.documents or not any(d.text.strip() for d in req.documents):
        raise HTTPException(400, "Provide at least one document with text")
    return coordinator.run_pipeline(req, u["name"])


@app.get("/api/runs")
def runs(u: dict = Depends(user)):
    return store.list_runs()


@app.get("/api/runs/{run_id}")
def get_run(run_id: str, u: dict = Depends(user)):
    r = store.get_run(run_id)
    if not r:
        raise HTTPException(404, "run not found")
    d = r.model_dump()
    d["clarifications"] = quality.clarification_list(r.requirements)
    d["baseline_blockers"] = store.can_baseline(r)[1]
    d["allowed_roles"] = {q.id: sorted(store.roles_allowed_for(q)) for q in r.requirements}
    d["mandatory"] = {q.id: store.is_mandatory_approval(q) for q in r.requirements}
    return d


@app.post("/api/runs/{run_id}/requirements/{req_id}/decision")
def decision(run_id: str, req_id: str, body: Decision, u: dict = Depends(user)):
    return _call(coordinator.decide, run_id, req_id, body.decision, u, body.note, body.new_statement)


@app.post("/api/runs/{run_id}/conflicts/{cid}/resolve")
def resolve(run_id: str, cid: str, body: Resolve, u: dict = Depends(user)):
    return _call(coordinator.resolve_conflict, run_id, cid, u, body.note, body.action)


@app.post("/api/runs/{run_id}/sdlc/signoff")
def signoff(run_id: str, u: dict = Depends(user)):
    return _call(coordinator.sdlc_signoff, run_id, u)


@app.post("/api/runs/{run_id}/baseline")
def baseline(run_id: str, u: dict = Depends(user)):
    return _call(coordinator.baseline, run_id, u)


_ARTIFACT_MEDIA_TYPES = {
    ".md": "text/markdown",
    ".csv": "text/csv",
    ".json": "application/json",
}


def _artifact_files(run_id: str):
    """Return validated generated files for a stored run, confined to its output folder."""
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(404, "run not found")

    root = Path(config.OUTPUT_DIR).resolve()
    run_dir = (root / run_id).resolve()
    if run_dir.parent != root or not run_dir.is_dir():
        raise HTTPException(404, "artifact directory not found")

    files = []
    for name in run.artifacts:
        # Generated artifacts are flat files; accept only the documented formats.
        if Path(name).name != name or Path(name).suffix.lower() not in _ARTIFACT_MEDIA_TYPES:
            continue
        path = (run_dir / name).resolve()
        if path.parent == run_dir and path.is_file():
            files.append((name, path))
    return run_dir, files


@app.get("/api/runs/{run_id}/artifacts/download-all")
def download_all_artifacts(run_id: str, u: dict = Depends(user)):
    """Download this run's generated Markdown, CSV, and JSON documents as a ZIP."""
    _, files = _artifact_files(run_id)
    if not files:
        raise HTTPException(404, "no generated artifacts found")

    archive = BytesIO()
    with ZipFile(archive, mode="w", compression=ZIP_DEFLATED) as zf:
        for name, path in files:
            zf.write(path, arcname=name)
    archive.seek(0)
    return StreamingResponse(
        archive,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{run_id}_documents.zip"'},
    )


@app.get("/api/runs/{run_id}/artifacts/{name}")
def artifact(run_id: str, name: str, u: dict = Depends(user)):
    _, files = _artifact_files(run_id)
    artifact_map = dict(files)
    # Restrict requests to the exact artifact list stored with the run and reject paths.
    if Path(name).name != name or name not in artifact_map:
        raise HTTPException(404, "artifact not found")
    path = artifact_map[name]
    return FileResponse(
        path,
        media_type=_ARTIFACT_MEDIA_TYPES[path.suffix.lower()],
        filename=name,
        content_disposition_type="attachment",
    )


@app.get("/api/runs/{run_id}/audit")
def run_audit(run_id: str, u: dict = Depends(user)):
    return audit.entries(run_id)


@app.get("/api/audit/verify")
def audit_verify(u: dict = Depends(user)):
    return audit.verify()


@app.post("/api/interview/start")
def interview_start(body: Start, u: dict = Depends(user)):
    return interview.start(body.role)


@app.post("/api/interview/answer")
def interview_answer(body: Answer, u: dict = Depends(user)):
    return _call(interview.answer, body.session_id, body.answer)
