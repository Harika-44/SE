from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pharmareq import audit, privacy
from pharmareq.agents import coordinator, sdlc
from pharmareq.api import app
from pharmareq.cli import load_docs
from pharmareq.kb import retriever
from pharmareq.schemas import ProjectParams, RunRequest

SAMPLES = Path(__file__).resolve().parent.parent / "data" / "samples"
client = TestClient(app)
H = lambda k: {"X-API-Key": k}


@pytest.fixture(scope="module")
def run():
    return coordinator.run_pipeline(RunRequest(documents=load_docs([str(SAMPLES)])), actor="test")


def test_pii_masking():
    t, c = privacy.mask("Call Dr. Mehta on 9876543210 or mehta@x.in, Aadhaar 1234 5678 9012")
    assert "9876543210" not in t and "mehta@x.in" not in t and "Mehta" not in t and "1234 5678" not in t
    assert c["PHONE"] == 1 and c["EMAIL"] == 1 and c["AADHAAR"] == 1


def test_injection_is_flagged_and_not_extracted(run):
    assert run.security_flags
    assert not any("mark all requirements" in r.statement.lower() for r in run.requirements)


def test_h1_retrieval():
    top = retriever.retrieve("Schedule H1 drugs must be recorded in a separate register")[0][0]["id"]
    assert top == "DCR-SCHED-H1"


def test_requirements_have_trace_fields(run):
    assert len(run.requirements) >= 20
    for r in run.requirements:
        assert r.source_quote and r.acceptance_criteria and r.categories and r.id[:2] in ("FR", "NF")


def test_numeric_conflict_found(run):
    assert any(c.kind == "numeric" for c in run.conflicts)


def test_owner_vs_inspector_conflict_found(run):
    assert any(c.kind in ("tension", "contradiction") for c in run.conflicts)


def test_clinical_advice_escalated(run):
    r = next(r for r in run.requirements if "correct dose" in r.statement.lower())
    assert any(i.kind == "out_of_scope" for i in r.issues) and r.needs_human


def test_all_citations_exist_in_kb(run):
    ids = {e["id"] for e in retriever.all_entries()}
    assert all(x.kb_id in ids for r in run.requirements for x in r.regulations)


def test_sdlc_regulated_project_prefers_validated_hybrid(run):
    assert run.sdlc.recommended in ("V-Model with Agile iterations", "V-Model")
    assert run.sdlc.ranking[0]["score"] >= run.sdlc.ranking[-1]["score"]


def test_sdlc_pure_agile_for_unregulated_changing_project():
    f = {k: 0.3 for k in sdlc.FACTORS}
    f.update(regulatory_criticality=0.1, patient_safety_impact=0.1, requirement_stability=0.1, change_frequency=0.9, stakeholder_availability=0.9, verification_need=0.2)
    assert sdlc.rank(f)[0][0]["model"] == "Agile"


def test_artifacts_written(run):
    from pharmareq import config
    out = Path(config.OUTPUT_DIR) / run.run_id
    for name in ("01_SRS.md", "08_traceability_matrix.csv", "11_sdlc_recommendation.md", "run.json"):
        assert (out / name).exists()
    assert "DRAFT" in (out / "01_SRS.md").read_text()


def test_audit_chain_and_tamper_detection(run):
    import sqlite3
    from pharmareq import config
    assert audit.verify()["ok"]
    c = sqlite3.connect(config.DB_PATH)
    c.execute("UPDATE audit SET payload='{}' WHERE id=2")
    c.commit(); c.close()
    assert not audit.verify()["ok"]


def test_rbac_and_baseline_gates():
    docs = [d.model_dump() for d in load_docs([str(SAMPLES)])]
    r = client.post("/api/runs", json={"documents": docs}, headers=H("analyst-key"))
    assert r.status_code == 200
    rid = r.json()["run_id"]
    assert client.post("/api/runs", json={"documents": docs}, headers=H("pharmacist-key")).status_code == 403
    assert client.get("/api/runs").status_code == 401
    reg = next(q for q in r.json()["requirements"] if "regulatory" in q["categories"] and q["issues"] == [])
    # analyst may not approve a regulatory requirement
    assert client.post(f"/api/runs/{rid}/requirements/{reg['id']}/decision", json={"decision": "accept"}, headers=H("analyst-key")).status_code == 403
    assert client.post(f"/api/runs/{rid}/requirements/{reg['id']}/decision", json={"decision": "accept"}, headers=H("pharmacist-key")).status_code == 200
    # baseline is blocked while items are pending / conflicts open
    b = client.post(f"/api/runs/{rid}/baseline", headers=H("pm-key"))
    assert b.status_code == 400 and "Cannot baseline" in b.json()["detail"]
    assert client.post(f"/api/runs/{rid}/baseline", headers=H("analyst-key")).status_code == 403


def test_interview_adapts():
    from pharmareq.agents import interview
    s = interview.start("Pharmacist")
    nxt = interview.answer(s["session_id"], "We want it fast")
    assert nxt["followup"] is True
    nxt = interview.answer(s["session_id"], "Within 5 seconds at peak. We run a retail pharmacy.")
    assert not nxt["done"]
