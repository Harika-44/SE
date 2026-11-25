# PharmaReq AI

Agentic AI for requirement gathering, analysis and SDLC selection in pharmacy dispensing and inventory compliance.
Implements the project plan: a multi-agent system that interviews stakeholders, extracts and classifies requirements,
detects ambiguity and conflicts, maps requirements to pharmacy rules with citations (retrieval-grounded), scores risk,
recommends an SDLC model with a customised workflow, generates the SRS and traceability artefacts, and keeps humans
in control through approval gates and a tamper-evident audit trail.

It runs **fully offline** (no API key, no cost). If you set `ANTHROPIC_API_KEY`, Claude is also used for extraction,
question phrasing, rule-relevance judgement and SDLC explanation. Every LLM answer is validated first, and the
system falls back to the offline rules if anything fails.

> **Important.** The regulation knowledge base (`pharmareq/kb/regulations.json`) contains short *paraphrased summaries*
> written for a student prototype. Every entry is marked `verified: false`. Before you quote any rule in a report,
> check it against the official text and have a pharmacist or compliance officer confirm it. The system gives candidate
> mappings only: no legal determinations, no clinical advice.

## 1. Install

Requirements: **Python 3.10 or newer** and `pip`. Nothing else (no database server; it uses SQLite from the standard library).

```bash
# 1. unzip the project and open a terminal in the folder
cd pharmareq-ai

# 2. create a virtual environment
python -m venv .venv

# 3. activate it
#    Windows (PowerShell):   .venv\Scripts\Activate.ps1
#    Windows (cmd):          .venv\Scripts\activate.bat
#    macOS / Linux:          source .venv/bin/activate

# 4. install dependencies
pip install -r requirements.txt
```

On Windows you may need `py` instead of `python`. If PowerShell blocks activation, run
`Set-ExecutionPolicy -Scope Process Bypass` first.

### Optional: use Claude as well

```bash
cp .env.example .env          # Windows: copy .env.example .env
# edit .env and set ANTHROPIC_API_KEY=your-key
```
Leave the key empty (or set `PHARMAREQ_MODE=offline`) to stay fully offline. The header of the web UI shows the current mode.
Use only synthetic or anonymised data: the system masks names, phones, emails, Aadhaar/PAN-like numbers and patient IDs before any
LLM call, but treat that as a safety net.

## 2. Run

### Web UI (recommended)
```bash
python -m pharmareq.cli serve
```
Open <http://127.0.0.1:8000>.

1. Click **Load samples** (four synthetic stakeholder documents), then **Analyse requirements**.
2. Walk the tabs: **Requirements**, **Questions** (clarification questions), **Conflicts**, **Compliance** (citations and control gaps),
   **Risks**, **SDLC** (ranking, factors, rules, workflow, sign-offs), **Validation** (gates and metrics), **Files**, **Audit**.
3. Use **Interview** to run an adaptive interview and send the transcript back as an input document.
4. Switch the "Signed in as" user to try the approval gates. Accepting a regulatory requirement needs a pharmacist or compliance
   officer; patient-safety needs a pharmacist; security/privacy needs security or architect. Resolve conflicts, collect the four SDLC
   sign-offs (project manager, architect, security, compliance officer), accept all requirements, then **Baseline** as the project manager.

Demo users (in `config/users.json`; the API key is sent as `X-API-Key`): `analyst-key`, `pharmacist-key`, `compliance-key`,
`pm-key`, `architect-key`, `security-key`. API docs: <http://127.0.0.1:8000/docs>.

### Command line
```bash
python -m pharmareq.cli run data/samples                 # analyse a folder of .txt files
python -m pharmareq.cli run my_notes.txt --months 4 --availability 2
python -m pharmareq.cli interview --role Pharmacist --out my_interview.txt
python -m pharmareq.cli verify-audit                     # check the audit hash chain
```
Input files are plain text. Optional first line `# Stakeholder: Drug Inspector`. Speaker labels such as
`Ravi (Pharmacist): ...` or `Inspector: ...` set the stakeholder per line.

Generated files land in `outputs/<run-id>/`:

| File | Content |
|---|---|
| `01_SRS.md` | Software Requirements Specification |
| `02_user_stories.md` | User stories with acceptance criteria |
| `03_use_cases.md`, `04_workflows.md` | Use cases and Mermaid process diagrams |
| `05_data_and_interfaces.md` | Data entities, data and interface requirements |
| `06_risk_register.md` | Hazard, security and AI-platform risks (likelihood x impact) |
| `07_compliance_matrix.md` | Requirement-to-rule mapping and control gaps |
| `08_traceability_matrix.csv` | Source -> requirement -> rule -> risk -> acceptance criteria -> test ID |
| `09_assumptions_dependencies.md`, `10_open_issues.md` | Registers and clarification questions |
| `11_sdlc_recommendation.md` | Ranked models, factors, rules, workflow with gates |
| `12_validation_report.md`, `run.json` | Gate results, metrics, full machine-readable run |

All artefacts say **DRAFT** until the project manager baselines the run.

## 3. Test and evaluate
```bash
python -m pytest -q tests          # 14 tests: masking, injection, retrieval, conflicts, scope guard, SDLC, RBAC, audit tamper detection
python eval/evaluate.py --manual-minutes 180
```
`eval/gold.json` is a starter gold set written for the sample documents, so scores near 1.0 only show that nothing regressed. For your
report, have a pharmacist re-annotate and extend it, measure your own manual time for `--manual-minutes`, and use
`eval/feedback_form.md` for satisfaction scores.

## 4. How the plan maps to the code

| Plan section | Where |
|---|---|
| 4 Multi-agent architecture, coordinator | `agents/coordinator.py` (pipeline, approvals, re-analysis, baseline) |
| 5 Knowledge base | `kb/regulations.json`, `kb/retriever.py` (source, jurisdiction, effective date, version, verified flag) |
| 6 Retrieval-grounded generation | `agents/compliance.py` (retrieve, cite, confidence, escalate), grounding check in `agents/extraction.py` |
| 7 Adaptive conversations | `agents/interview.py` |
| 8-9 Extract, structure, classify | `agents/extraction.py`, `agents/classification.py` (14 categories, multi-label, FR/NFR-module-number IDs) |
| 10 Quality, clarification, conflicts | `agents/quality.py`, `agents/conflict.py` |
| 11 Compliance, safety, security | `agents/compliance.py`, `agents/risk.py` (scope guard: no clinical advice or legal decisions) |
| 12 Artefacts | `agents/documentation.py` |
| 13-15 SDLC selection and workflow | `agents/sdlc.py` (13 factors, weighted scoring, 7 rules, 7 models, phase/role/gate workflow) |
| 16 Human-in-the-loop | `store.py`, `agents/coordinator.py` (accept, reject, modify, regenerate; role-restricted) |
| 17 Security | `privacy.py` (masking, injection screening), `api.py` (RBAC), `audit.py` |
| 19 Evaluation | `eval/`, `agents/validation.py` metrics |
| 20 Audit | `audit.py` (hash-chained log of prompts counts, evidence, decisions, approvals) |

## 5. Known limits (be upfront about these in your report)

* Offline extraction is cue-word based; it will miss implicit requirements and can over-extract. Claude mode is better at this, and its output is checked against the source text.
* Retrieval is TF-IDF over 16 summary entries, not a vector database. Swap `kb/retriever.py` for Chroma/pgvector if you grow the corpus.
* Not built (designed only): multi-factor authentication, TLS termination, encryption at rest (SQLite file is plain; use SQLCipher or disk encryption), the standalone safety/security and approval agents as separate processes (their logic lives in the compliance, risk and coordinator modules), hospital indent-and-issue and e-pharmacy modules.
* Retention periods and rule details in the knowledge base are unverified; the tool never decides them.
* Authentication is demo-grade (static API keys).
