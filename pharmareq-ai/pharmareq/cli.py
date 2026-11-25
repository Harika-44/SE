"""Command line: python -m pharmareq.cli <run|serve|interview|verify-audit> ..."""
import argparse
import sys
from pathlib import Path

from . import audit, config
from .schemas import ProjectParams, RunRequest, SourceDoc


def load_docs(paths: list[str]) -> list[SourceDoc]:
    files = []
    for p in paths:
        pp = Path(p)
        files += sorted(pp.glob("*.txt")) if pp.is_dir() else [pp]
    docs = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        first = text.splitlines()[0] if text else ""
        stakeholder = first.split(":", 1)[1].strip() if first.lower().startswith("# stakeholder") else f.stem.replace("_", " ").title()
        docs.append(SourceDoc(name=f.name, stakeholder=stakeholder, text=text))
    return docs


def cmd_run(a):
    from .agents import coordinator
    from .llm import llm

    docs = load_docs(a.paths)
    if not docs:
        sys.exit("No input documents found.")
    params = ProjectParams(duration_months=a.months, team_size=a.team, stakeholder_availability=a.availability,
                           legacy_dependence=a.legacy, continuous_delivery_need=a.cd, budget_pressure=a.budget)
    run = coordinator.run_pipeline(RunRequest(project_name=a.name, documents=docs, params=params), actor="cli")
    print(f"Mode: {llm.mode}")
    print(f"Run {run.run_id}: {len(run.requirements)} requirements, {len(run.conflicts)} conflicts, {len(run.gaps)} control gaps")
    print(f"SDLC recommendation: {run.sdlc.recommended} ({run.sdlc.ranking[0]['score']}%)")
    for f in run.security_flags:
        print("SECURITY FLAG:", f)
    print(f"Baseline ready: {run.validation['baseline_ready']} (needs human approvals - use the web UI)")
    print(f"Artifacts: {Path(config.OUTPUT_DIR) / run.run_id}")


def cmd_serve(a):
    import uvicorn

    uvicorn.run("pharmareq.api:app", host=a.host, port=a.port, reload=False)


def cmd_interview(a):
    from .agents import interview

    step = interview.start(a.role)
    sid = step["session_id"]
    while not step["done"]:
        ans = input(f"\n{step['question']}\n> ").strip()
        if ans.lower() in ("quit", "exit"):
            break
        step = interview.answer(sid, ans)
    text = interview.transcript(interview.SESSIONS[sid])
    out = Path(a.out)
    out.write_text(f"# Stakeholder: {a.role}\n{text}\n", encoding="utf-8")
    print(f"\nTranscript saved to {out}. Feed it to: python -m pharmareq.cli run {out}")


def cmd_verify(_):
    r = audit.verify()
    print(r)
    sys.exit(0 if r["ok"] else 1)


def main():
    ap = argparse.ArgumentParser(prog="pharmareq")
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run", help="analyse stakeholder documents")
    r.add_argument("paths", nargs="+", help="files or folders of .txt stakeholder documents")
    r.add_argument("--name", default="PharmaReq Demo")
    r.add_argument("--months", type=float, default=2)
    r.add_argument("--team", type=int, default=4)
    r.add_argument("--availability", type=int, default=3, help="stakeholder availability 1-5")
    r.add_argument("--legacy", type=int, default=3, help="legacy dependence 1-5")
    r.add_argument("--cd", type=int, default=2, help="continuous delivery need 1-5")
    r.add_argument("--budget", type=int, default=3, help="budget pressure 1-5")
    r.set_defaults(fn=cmd_run)
    s = sp.add_parser("serve", help="start web UI + API")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.set_defaults(fn=cmd_serve)
    i = sp.add_parser("interview", help="adaptive interview in the terminal")
    i.add_argument("--role", default="Pharmacist")
    i.add_argument("--out", default="interview.txt")
    i.set_defaults(fn=cmd_interview)
    v = sp.add_parser("verify-audit", help="verify the audit hash chain")
    v.set_defaults(fn=cmd_verify)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
