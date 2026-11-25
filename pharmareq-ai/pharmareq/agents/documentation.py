"""Documentation agent (plan section 12): generates the requirement artefacts. Every item stays
linked to its source statement and supporting rule. Output is marked DRAFT until baselined."""
import csv
import io
import json
import re
from collections import defaultdict
from pathlib import Path

from .. import config
from ..schemas import Requirement, Run

AC_TEMPLATES = [
    (r"\bh1\b|schedule|register", ["Given a scheduled drug is dispensed, when the sale is confirmed, then a register entry with patient, prescriber, drug, batch, quantity and date exists.",
                                     "A user cannot complete the sale while a mandatory register field is empty."]),
    (r"expir|recall", ["Given a batch past its expiry date or marked recalled, when a user tries to sell it, then the sale is blocked and the reason is shown.",
                       "Given several valid batches, the batch with the earliest valid expiry is proposed first."]),
    (r"substitut", ["A substitution cannot be saved without pharmacist confirmation; the original drug, substitute and reason are stored."]),
    (r"prescription|prescriber", ["Given a prescription with a missing mandatory field, the system refuses to continue and lists the missing fields.",
                                  "A completed dispensing is linked to its prescription."]),
    (r"retain|retention|delet", ["Given a regulated record inside its retention period, a delete attempt is refused and logged.",
                                  "The retention period is configurable and its value is shown in the record view."]),
    (r"audit|\blogs?\b|trail", ["Given any change to a regulated record, an audit entry with user, time, old value, new value and reason is stored and cannot be edited."]),
    (r"\bgst|invoice|\bbill", ["Given a completed sale, the invoice shows a unique sequential number, GSTIN, HSN, tax rate and tax amount."]),
    (r"access|\broles?\b|login|password|authori", ["Given a user without the required role, the action is denied and the attempt is logged."]),
    (r"alert|notify|reminder", ["Given the alert condition is met, the alert is raised within the agreed time and shown to the named recipient and logged."]),
    (r"report|inspect|export", ["Given a date range, the report lists all matching records and can be exported in the agreed format."]),
    (r"within \d+|seconds?|peak|fast|quick", ["Measured at peak load, the stated percentage of transactions completes within the agreed time (values to be confirmed)."]),
]
CAT_TITLES = {"patient_safety": "Patient safety", "regulatory": "Regulatory", "security": "Security", "privacy": "Privacy", "performance": "Performance",
              "availability": "Availability and reliability", "usability": "Usability", "data_management": "Data management", "integration": "Integration",
              "audit_reporting": "Audit and reporting", "operational": "Operational and maintenance", "business": "Business", "functional": "Functional", "stakeholder": "Stakeholder"}
MODULE_TITLES = {"RX": "Prescription intake and validation", "DSP": "Dispensing", "REG": "Scheduled-drug register", "INV": "Batch, expiry and stock", "BIL": "Billing",
                 "SUP": "Supplier purchase and returns", "AUD": "Audit and inspection", "SEC": "Security and access", "PRV": "Privacy", "GEN": "General"}
USE_CASES = {
    "RX": ("UC-01", "Validate and accept a prescription", "Pharmacist / pharmacy assistant", "A paper or electronic prescription is presented.",
           ["Capture prescriber, patient and drug details.", "System validates mandatory fields and schedule rules.", "Pharmacist confirms the prescription is valid.", "System attaches the prescription to the sale."],
           ["Prescription incomplete or illegible: refer back to the prescriber and stop.", "E-prescription fails validation: flag for pharmacist review."], "Validated prescription is linked to the pending sale."),
    "DSP": ("UC-02", "Dispense a medicine", "Pharmacist", "A validated prescription (or OTC sale) exists.",
            ["System proposes batches (earliest valid expiry first).", "Pharmacist verifies drug, strength, quantity and batch.", "Pharmacist confirms; stock is reduced.", "Label and invoice are produced."],
            ["Requested drug out of stock: offer a substitution (needs pharmacist approval and a recorded reason).", "Partial supply: record the balance quantity."], "Dispensing is recorded and traceable to batch and prescription."),
    "REG": ("UC-03", "Record a scheduled-drug supply", "Pharmacist", "A Schedule H, H1 or X drug is being dispensed.",
            ["System creates the register entry as part of the dispensing.", "Mandatory fields are checked.", "Entry is locked against deletion and audit-logged."],
            ["Missing mandatory field: sale cannot be completed.", "Correction needed: add a linked correcting entry with a reason."], "Register entry exists and is retained for the required period."),
    "INV": ("UC-04", "Receive stock and manage expiry or recall", "Pharmacist / store keeper", "A supplier delivery or a recall notice arrives.",
            ["Record batch, expiry and quantity against the supplier invoice.", "System flags near-expiry batches.", "On recall, batch is quarantined and the action is recorded."], ["Invoice mismatch: hold the goods and note the discrepancy."], "Stock, batch and expiry data are accurate."),
    "BIL": ("UC-05", "Bill a sale", "Pharmacist / cashier", "Items are dispensed or selected.",
            ["System prices items and applies allowed discounts.", "GST invoice is generated.", "Payment is recorded."], ["Discount above the limit: needs authorisation."], "Invoice is stored and numbered."),
    "AUD": ("UC-06", "Prepare for a drug inspection", "Pharmacy owner / inspector", "An inspection is due or has started.",
            ["Select period and record types.", "System produces register, purchase and sale reports.", "Audit trail is available on request."], ["Missing record found: raise an issue for follow-up."], "Inspector receives complete, consistent records."),
    "SUP": ("UC-07", "Purchase from a supplier and return stock", "Pharmacy owner / store keeper", "Stock is below reorder level or a batch is to be returned.",
            ["Create purchase order.", "Receive goods (UC-04).", "Record returns with credit-note reference."], ["Supplier cannot supply: record and choose an alternative."], "Purchases and returns are recorded."),
}


def add_acceptance_criteria(reqs: list[Requirement]) -> None:
    for r in reqs:
        if r.acceptance_criteria and r.approval_status == "accepted":
            continue
        crit = []
        for rx, acs in AC_TEMPLATES:
            if re.search(rx, r.statement, re.I):
                crit += acs
        crit = list(dict.fromkeys(crit))[:3] or ["The behaviour described in the requirement is demonstrated by a test with recorded evidence.", "A failure of this behaviour is logged."]
        if any(i.kind in ("ambiguity", "incomplete") for i in r.issues):
            crit = [c + " (provisional until the clarification questions are answered)" if k == 0 else c for k, c in enumerate(crit)]
        r.acceptance_criteria = crit


# ---------------------------------------------------------------- helpers
def _esc(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _table(headers, rows) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(_esc(c) for c in row) + " |" for row in rows]
    return "\n".join(out) + "\n"


def _banner(run: Run) -> str:
    if run.status == "baselined":
        return "> **BASELINED** - approved by the authorised roles. Changes need change control.\n"
    return "> **DRAFT** - AI-assisted output. Not approved. Regulatory mappings are candidate mappings for a qualified pharmacist or compliance officer to confirm.\n"


def _active(run: Run):
    return [r for r in run.requirements if r.approval_status != "rejected"]


def _test_id(r: Requirement) -> str:
    return f"TC-{r.id}-01"


# ---------------------------------------------------------------- documents
def srs(run: Run) -> str:
    act = _active(run)
    L = [f"# Software Requirements Specification - {run.project_name}\n", _banner(run), f"Run `{run.run_id}` - generated {run.created}\n",
         "## 1. Introduction\n", "Purpose: define the requirements for pharmacy dispensing and inventory-compliance software, focused on the prescription-to-dispensing workflow with scheduled-drug record keeping.\n",
         "This document was produced from stakeholder inputs by the PharmaReq AI agents. Patient data in the inputs was masked before processing.\n"]
    stk = defaultdict(int)
    for r in act:
        stk[r.source_stakeholder] += 1
    L += ["## 2. Stakeholders and sources\n", _table(["Stakeholder", "Requirements raised"], sorted(stk.items())), "## 3. Overall description\n"]
    notes = run.metrics.get("context_notes", [])
    L.append("Context statements captured from the inputs:\n\n" + ("\n".join(f"- {_esc(n)}" for n in notes) if notes else "- None captured.") + "\n")
    L.append("## 4. Functional requirements\n")
    by_mod = defaultdict(list)
    for r in act:
        if r.id.startswith("FR"):
            by_mod[r.module].append(r)
    for mod, rs in by_mod.items():
        L += [f"### {MODULE_TITLES.get(mod, mod)}\n", _table(["ID", "Requirement", "Priority", "Risk", "Source", "Status"], [(r.id, r.statement, r.priority, r.risk_level, r.source_stakeholder, r.approval_status) for r in rs])]
    L.append("## 5. Non-functional requirements\n")
    nfr = [r for r in act if r.id.startswith("NFR")]
    if nfr:
        L.append(_table(["ID", "Requirement", "Categories", "Priority", "Risk", "Source", "Status"], [(r.id, r.statement, ", ".join(CAT_TITLES.get(c, c) for c in r.categories), r.priority, r.risk_level, r.source_stakeholder, r.approval_status) for r in nfr]))
    else:
        L.append("None captured.\n")
    L += ["## 6. Regulatory and policy mapping (candidate)\n"]
    regs = [(r.id, x.kb_id, x.title, "yes" if x.verified else "NO - verify", x.rationale) for r in act for x in r.regulations]
    L.append(_table(["Requirement", "KB entry", "Title", "Verified", "Why matched"], regs) if regs else "No mappings.\n")
    L += ["## 7. Open items\n", f"- Clarification questions: {sum(1 for r in act for i in r.issues if i.question)} (see `10_open_issues.md`)\n- Conflicts: {len(run.conflicts)}\n- Control gaps: {len(run.gaps)}\n",
          "## 8. Approval status\n", _table(["Status", "Count"], [(s, sum(1 for r in run.requirements if r.approval_status == s)) for s in ("accepted", "pending", "rejected")])]
    rej = [r for r in run.requirements if r.approval_status == "rejected"]
    if rej:
        L += ["## Appendix A. Rejected requirements\n", _table(["ID", "Statement"], [(r.id, r.statement) for r in rej])]
    return "\n".join(L)


def user_stories(run: Run) -> str:
    L = ["# User stories and acceptance criteria\n", _banner(run)]
    for r in _active(run):
        if not r.id.startswith("FR"):
            continue
        role = r.source_stakeholder if r.source_stakeholder.lower() not in ("unknown", "") else "user"
        action = re.sub(r"^(the system )?(shall|should|must)\s+", "", r.statement.rstrip("."), flags=re.I)
        L.append(f"### {r.id}\n**As a** {role.lower()}, **I want** the system to {action[:1].lower() + action[1:]}, **so that** {r.justification[:1].lower() + r.justification[1:].rstrip('.')}.\n")
        L.append("Acceptance criteria:\n" + "\n".join(f"- {c}" for c in r.acceptance_criteria) + f"\n\nSource: {r.source_stakeholder} (\"{_esc(r.source_quote[:140])}\")\n")
    return "\n".join(L)


def use_cases(run: Run) -> str:
    L = ["# Use cases\n", _banner(run)]
    mods = {r.module for r in _active(run)}
    for mod, uc in USE_CASES.items():
        if mod not in mods:
            continue
        uid, name, actor, pre, flow, alt, post = uc
        refs = [r.id for r in _active(run) if r.module == mod]
        L += [f"## {uid} {name}\n", f"- **Actor:** {actor}\n- **Precondition:** {pre}\n- **Postcondition:** {post}\n- **Related requirements:** {', '.join(refs)}\n", "**Main flow**\n"]
        L += [f"{n}. {s}" for n, s in enumerate(flow, 1)]
        L += ["", "**Alternate flows**\n"] + [f"- {a}" for a in alt] + [""]
    return "\n".join(L)


def workflows(run: Run) -> str:
    return f"""# Process workflows

{_banner(run)}
## Prescription to dispensing

```mermaid
flowchart TD
  A[Prescription presented] --> B{{Complete and valid?}}
  B -- no --> C[Refer back to prescriber]
  B -- yes --> D[Capture prescriber, patient, drug]
  D --> E{{Scheduled drug H / H1 / X?}}
  E -- yes --> F[Create register entry and keep prescription copy as required]
  E -- no --> G[Select batch - earliest valid expiry]
  F --> G
  G --> H[Pharmacist verifies drug, strength, quantity, batch]
  H --> I[Dispense, label, bill]
  I --> J[Audit entry written]
```

## Goods receipt to stock

```mermaid
flowchart TD
  A[Supplier delivery] --> B[Check against invoice]
  B --> C[Record batch, expiry, quantity]
  C --> D[Stock available - FEFO]
  D --> E{{Near expiry or recalled?}}
  E -- near expiry --> F[Alert owner]
  E -- recalled --> G[Quarantine and record action]
  E -- no --> H[Normal dispensing]
```
"""


def data_and_interfaces(run: Run) -> str:
    ent = [("Prescription", "prescription id, date, prescriber (name, registration no.), patient reference, drugs, quantity, e-prescription flag, scanned copy"),
           ("Patient", "name, age/sex, contact (masked in non-clinical views), consent status"), ("Drug", "name, strength, form, schedule (H/H1/X/NDPS/none), HSN, MRP"),
           ("Batch", "batch no., expiry date, quantity on hand, supplier, status (valid/near-expiry/expired/recalled)"), ("DispenseTransaction", "prescription, drug, batch, quantity, pharmacist, timestamp, substitution reason"),
           ("ScheduledRegisterEntry", "transaction, patient, prescriber, drug, batch, quantity, date, correction-of reference"), ("Invoice", "number (sequential), GSTIN, HSN, tax rate/amount, discount, authoriser"),
           ("Supplier / Purchase", "supplier, invoice, goods-receipt lines, returns, credit-note reference"), ("AuditEvent", "user, role, action, object, old/new value, reason, timestamp, hash")]
    dm = [r for r in _active(run) if set(r.categories) & {"data_management"}]
    it = [r for r in _active(run) if "integration" in r.categories]
    return "\n".join(["# Data and interface requirements\n", _banner(run), "## Core data entities (proposed)\n", _table(["Entity", "Key attributes"], ent),
                      "## Data-management requirements from stakeholders\n", _table(["ID", "Requirement"], [(r.id, r.statement) for r in dm]) if dm else "None captured.\n",
                      "## Interface requirements from stakeholders\n", _table(["ID", "Requirement"], [(r.id, r.statement) for r in it]) if it else "None captured.\n"])


def risk_register(run: Run) -> str:
    return "\n".join(["# Risk and threat register\n", _banner(run), _table(["ID", "Risk", "Category", "L", "I", "Score", "Rating", "Mitigation", "Verification", "Requirements"],
                      [(x.id, x.title, x.category, x.likelihood, x.impact, x.score, x.rating, x.mitigation, x.verification, ", ".join(x.req_ids) or "platform") for x in run.risks])])


def compliance_matrix(run: Run) -> str:
    rows = [(r.id, r.statement, "; ".join(f"{x.kb_id} ({x.score:.2f})" for x in r.regulations) or "none", r.confidence, r.risk_level, "yes" if r.needs_human else "no") for r in _active(run)]
    L = ["# Compliance matrix\n", _banner(run), "Mappings are candidates found by retrieval. The knowledge base is unverified until a compliance officer checks each entry against the official text.\n",
         _table(["Requirement", "Statement", "Candidate rules (score)", "Confidence", "Risk", "Human review"], rows), "## Control gaps (no requirement covers the control)\n"]
    L.append(_table(["Rule", "Control", "Suggested requirement (for the analyst to consider)", "Severity"], [(g.kb_id, g.description, g.suggested_requirement, g.severity) for g in run.gaps]) if run.gaps else "No gaps found.\n")
    return "\n".join(L)


def traceability(run: Run) -> list[list]:
    rows = [["requirement_id", "statement", "source_stakeholder", "source_doc", "source_quote", "categories", "rules", "risk_level", "acceptance_criteria", "test_case", "approval_status"]]
    for r in _active(run):
        rows.append([r.id, r.statement, r.source_stakeholder, r.source_doc, r.source_quote, ";".join(r.categories), ";".join(x.kb_id for x in r.regulations), r.risk_level, " || ".join(r.acceptance_criteria), _test_id(r), r.approval_status])
    return rows


def assumptions(run: Run) -> str:
    deps = [(r.id, ", ".join(r.dependencies)) for r in _active(run) if r.dependencies]
    ass = [(r.id, a) for r in _active(run) for a in r.assumptions]
    return "\n".join(["# Assumptions and dependencies\n", _banner(run), "## Assumptions\n",
                      _table(["Requirement", "Assumption"], ass) if ass else "None recorded by the agents. The analyst should add assumptions made during clarification.\n",
                      "## Dependencies (derived from workflow order)\n", _table(["Requirement", "Depends on"], deps) if deps else "None.\n",
                      "## Standing assumptions of this prototype\n", "- Only synthetic or anonymised data is used.\n- Knowledge-base rules are unverified summaries until checked.\n- Retention periods are not decided by this tool.\n"])


def open_issues(run: Run) -> str:
    q = [(r.id, r.source_stakeholder, i.severity, i.message, i.question) for r in _active(run) for i in r.issues if i.question]
    cf = [(c.id, c.kind, ", ".join(c.req_ids), c.description, c.status) for c in run.conflicts]
    esc = [(r.id, "; ".join(i.message for i in r.issues if i.kind in ("low_confidence", "out_of_scope"))) for r in _active(run) if any(i.kind in ("low_confidence", "out_of_scope") for i in r.issues)]
    L = ["# Open issues\n", _banner(run), "## Clarification questions\n", _table(["Requirement", "Ask", "Severity", "Issue", "Question"], q) if q else "None.\n",
         "## Conflicts and duplicates\n", _table(["ID", "Kind", "Requirements", "Description", "Status"], cf) if cf else "None.\n",
         "## Escalations to humans\n", _table(["Requirement", "Reason"], esc) if esc else "None.\n"]
    if run.security_flags:
        L += ["## Security flags in inputs\n"] + [f"- {_esc(f)}" for f in run.security_flags]
    return "\n".join(L)


def sdlc_doc(run: Run) -> str:
    s = run.sdlc
    if not s:
        return "# SDLC recommendation\n\nNot available.\n"
    L = ["# SDLC recommendation and project workflow\n", _banner(run), f"**Recommended:** {s.recommended}\n", s.explanation + "\n", "## Ranking\n", _table(["Model", "Score %"], [(x["model"], x["score"]) for x in s.ranking]),
         "## Derived project factors (0 to 1)\n", _table(["Factor", "Value"], list(s.factors.items())), "## Rules applied\n", "\n".join(f"- {r}" for r in s.rules_fired) or "None.", "\n## Sign-offs\n",
         _table(["Role", "Signed by"], [(r, s.signoffs.get(r, "pending")) for r in config.SDLC_SIGNOFF_ROLES]), "## Workflow\n"]
    for n, p in enumerate(s.workflow, 1):
        L.append(f"### Phase {n}: {p['name']}\n")
        if p.get("iteration"):
            L.append(f"*Iteration:* {p['iteration']}\n")
        for k, t in (("activities", "Activities"), ("roles", "Roles"), ("deliverables", "Deliverables"), ("security_controls", "Security controls"), ("compliance_checkpoints", "Compliance checkpoints"), ("entry_criteria", "Entry criteria"), ("exit_criteria", "Exit criteria")):
            L.append(f"**{t}:** " + "; ".join(p[k]) + "\n")
        L.append(f"**Gate:** {p['gate']}\n")
    return "\n".join(L)


def validation_doc(run: Run) -> str:
    v = run.validation
    return "\n".join(["# Validation report\n", _banner(run), f"**Baseline ready:** {'yes' if v.get('baseline_ready') else 'no'}\n", "## Gates\n",
                      _table(["Gate", "Name", "Status", "Blocking", "Detail"], [(g["id"], g["name"], g["status"], "yes" if g["blocking"] else "no", g["detail"]) for g in v.get("gates", [])]),
                      "## Metrics\n", _table(["Metric", "Value"], list(v.get("metrics", {}).items())), "## Processing metrics\n", _table(["Metric", "Value"], [(k, x) for k, x in run.metrics.items() if k != "context_notes"])])


def generate_all(run: Run) -> list[str]:
    out = Path(config.OUTPUT_DIR) / run.run_id
    out.mkdir(parents=True, exist_ok=True)
    files = {"01_SRS.md": srs(run), "02_user_stories.md": user_stories(run), "03_use_cases.md": use_cases(run), "04_workflows.md": workflows(run),
             "05_data_and_interfaces.md": data_and_interfaces(run), "06_risk_register.md": risk_register(run), "07_compliance_matrix.md": compliance_matrix(run),
             "09_assumptions_dependencies.md": assumptions(run), "10_open_issues.md": open_issues(run), "11_sdlc_recommendation.md": sdlc_doc(run), "12_validation_report.md": validation_doc(run)}
    trace = traceability(run)
    buf = io.StringIO()
    csv.writer(buf).writerows(trace)
    files["08_traceability_matrix.csv"] = buf.getvalue()
    files["run.json"] = run.model_dump_json(indent=2)
    files["index.md"] = f"# {run.project_name} - run {run.run_id}\n\n" + _banner(run) + "\n" + "\n".join(f"- [{n}]({n})" for n in sorted(files))
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8")
    return sorted(files)
