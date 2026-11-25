"""SDLC selection agent (plan sections 13, 14, 15).

Hybrid engine: (1) derive project factors from the analysed requirements and the project
parameters, (2) score every candidate model with multi-criteria decision analysis (weighted
closeness to an ideal profile), (3) apply deterministic rules that encode regulated-software
practice, (4) produce a ranked list with explanations, and (5) generate a customised workflow.
"""
import re

from ..llm import llm
from ..schemas import Conflict, ProjectParams, Requirement, SdlcResult

FACTORS = {
    "requirement_stability": "Requirement stability",
    "regulatory_criticality": "Regulatory criticality",
    "patient_safety_impact": "Patient-safety impact of failure",
    "security_privacy_risk": "Security and privacy risk",
    "complexity": "Project complexity",
    "system_size": "System size",
    "legacy_dependence": "Legacy-system dependence",
    "change_frequency": "Expected change frequency",
    "continuous_delivery_need": "Need for continuous delivery",
    "stakeholder_availability": "Stakeholder availability",
    "verification_need": "Need for formal verification and evidence",
    "budget_schedule_pressure": "Budget and schedule pressure",
    "uncertainty": "Uncertainty / technical risk",
}
CHANGE_CUE = re.compile(r"schedule lists?|lists? (?:change|is updated|gets updated)|rules? (?:change|keep changing)|new regulation|frequent\w* (?:chang|updat)|evolv|updated? (?:often|regularly|every)|amend|revis|changes? (?:often|every)", re.I)
LEGACY_CUE = re.compile(r"legacy|existing (?:system|software|billing)|tally|migrat|paper|excel", re.I)
SCHED_CUE = re.compile(r"\bh1\b|schedule|ndps|narcotic|psychotropic", re.I)


def _c(x: float) -> float:
    return round(max(0.0, min(1.0, x)), 2)


def derive_factors(reqs: list[Requirement], p: ProjectParams, conflicts: list[Conflict]) -> dict[str, float]:
    act = [r for r in reqs if r.approval_status != "rejected"] or reqs
    n = max(1, len(act))
    text = " ".join(r.statement for r in act)

    def share(*cats):
        return sum(1 for r in act if set(cats) & set(r.categories)) / n

    change_hits = sum(1 for r in act if CHANGE_CUE.search(r.statement))
    change = _c(0.2 + 0.25 * change_hits)
    ambiguous = sum(1 for r in act if any(i.kind in ("ambiguity", "incomplete") for i in r.issues)) / n
    open_conf = sum(1 for c in conflicts if c.kind != "duplicate" and c.status == "open") / n
    lowconf = sum(1 for r in act if any(i.kind == "low_confidence" for i in r.issues)) / n
    uncertainty = _c(0.1 + 0.8 * ambiguous + 1.5 * open_conf + 0.5 * lowconf)
    reg = _c((0.35 + 1.5 * share("regulatory") if share("regulatory") else 0.2) + (0.2 if SCHED_CUE.search(text) else 0))
    safety = _c((0.3 + 2 * share("patient_safety") if share("patient_safety") else 0.15) + (0.3 if re.search(r"wrong|batch|expir|dispens|substitut|recall", text, re.I) else 0))
    sec = _c((0.25 + 2.5 * share("security", "privacy") if share("security", "privacy") else 0.2) + (0.2 if re.search(r"patient|prescription", text, re.I) else 0))
    modules = {r.module for r in act}
    complexity = _c(0.15 + 0.5 * min(1, n / 40) + 0.2 * min(1, share("integration") * 3) + 0.15 * min(1, len(modules) / 8))
    size = _c(0.1 + 0.6 * min(1, n / 50) + 0.3 * min(1, p.duration_months / 12))
    legacy = _c(0.6 * (p.legacy_dependence / 5) + 0.4 * min(1, len(LEGACY_CUE.findall(text)) / 3))
    verif = _c(0.3 + 0.35 * reg + 0.2 * safety + (0.15 if re.search(r"validat|verif|audit|inspect|evidence|trace", text, re.I) else 0))
    pressure = _c(0.6 * (p.budget_pressure / 5) + 0.4 * (1 if p.duration_months <= 2 else 0.5 if p.duration_months <= 6 else 0.2))
    return {
        "requirement_stability": _c(1 - min(1, 0.6 * change + 0.4 * uncertainty)),
        "regulatory_criticality": reg, "patient_safety_impact": safety, "security_privacy_risk": sec,
        "complexity": complexity, "system_size": size, "legacy_dependence": legacy, "change_frequency": change,
        "continuous_delivery_need": _c(p.continuous_delivery_need / 5), "stakeholder_availability": _c(p.stakeholder_availability / 5),
        "verification_need": verif, "budget_schedule_pressure": pressure, "uncertainty": uncertainty,
    }


# ideal factor value per model, and the importance weight of each factor for that model (default 0.5)
PROFILES = {
    "Waterfall": ({"requirement_stability": .9, "regulatory_criticality": .6, "patient_safety_impact": .5, "security_privacy_risk": .4, "complexity": .4, "system_size": .5, "legacy_dependence": .4, "change_frequency": .1, "continuous_delivery_need": .1, "stakeholder_availability": .4, "verification_need": .6, "budget_schedule_pressure": .3, "uncertainty": .1},
                  {"requirement_stability": 3, "change_frequency": 3, "uncertainty": 2, "regulatory_criticality": 1, "verification_need": 1}),
    "V-Model": ({"requirement_stability": .75, "regulatory_criticality": .9, "patient_safety_impact": .9, "security_privacy_risk": .6, "complexity": .5, "system_size": .5, "legacy_dependence": .5, "change_frequency": .3, "continuous_delivery_need": .2, "stakeholder_availability": .5, "verification_need": .95, "budget_schedule_pressure": .4, "uncertainty": .3},
                 {"regulatory_criticality": 2.5, "patient_safety_impact": 2.5, "verification_need": 3, "requirement_stability": 2, "change_frequency": 1.5, "uncertainty": 1}),
    "Agile": ({"requirement_stability": .2, "regulatory_criticality": .2, "patient_safety_impact": .2, "security_privacy_risk": .3, "complexity": .5, "system_size": .4, "legacy_dependence": .2, "change_frequency": .9, "continuous_delivery_need": .7, "stakeholder_availability": .9, "verification_need": .3, "budget_schedule_pressure": .6, "uncertainty": .5},
              {"requirement_stability": 3, "change_frequency": 3, "stakeholder_availability": 2, "regulatory_criticality": 2, "patient_safety_impact": 2, "verification_need": 2, "continuous_delivery_need": 1}),
    "Spiral": ({"requirement_stability": .3, "regulatory_criticality": .6, "patient_safety_impact": .7, "security_privacy_risk": .6, "complexity": .9, "system_size": .7, "legacy_dependence": .5, "change_frequency": .6, "continuous_delivery_need": .2, "stakeholder_availability": .5, "verification_need": .7, "budget_schedule_pressure": .2, "uncertainty": .9},
               {"uncertainty": 3, "complexity": 3, "system_size": 1, "budget_schedule_pressure": 1.5, "patient_safety_impact": 1}),
    "DevSecOps": ({"requirement_stability": .4, "regulatory_criticality": .5, "patient_safety_impact": .5, "security_privacy_risk": .95, "complexity": .6, "system_size": .6, "legacy_dependence": .3, "change_frequency": .7, "continuous_delivery_need": .95, "stakeholder_availability": .7, "verification_need": .6, "budget_schedule_pressure": .5, "uncertainty": .4},
                  {"continuous_delivery_need": 3, "security_privacy_risk": 3, "change_frequency": 1.5, "regulatory_criticality": 1.5, "patient_safety_impact": 1.5, "verification_need": 1.5}),
    "V-Model with Agile iterations": ({"requirement_stability": .5, "regulatory_criticality": .9, "patient_safety_impact": .9, "security_privacy_risk": .7, "complexity": .6, "system_size": .5, "legacy_dependence": .5, "change_frequency": .6, "continuous_delivery_need": .4, "stakeholder_availability": .6, "verification_need": .9, "budget_schedule_pressure": .5, "uncertainty": .5},
                                     {"regulatory_criticality": 2.5, "patient_safety_impact": 2.5, "verification_need": 2.5, "change_frequency": 2, "requirement_stability": 2, "stakeholder_availability": 1, "uncertainty": 1}),
    "DevSecOps hybrid (V-Model gates + CI/CD)": ({"requirement_stability": .5, "regulatory_criticality": .85, "patient_safety_impact": .8, "security_privacy_risk": .9, "complexity": .65, "system_size": .6, "legacy_dependence": .4, "change_frequency": .65, "continuous_delivery_need": .8, "stakeholder_availability": .6, "verification_need": .85, "budget_schedule_pressure": .5, "uncertainty": .4},
                                                  {"regulatory_criticality": 2, "security_privacy_risk": 2.5, "continuous_delivery_need": 2, "verification_need": 2, "patient_safety_impact": 2, "change_frequency": 1.5}),
}


def _score(model: str, f: dict[str, float]) -> float:
    ideal, w = PROFILES[model]
    tot = sum(w.get(k, 0.5) for k in FACTORS)
    return sum(w.get(k, 0.5) * (1 - abs(f[k] - ideal[k])) for k in FACTORS) / tot * 100


def rank(f: dict[str, float]) -> tuple[list[dict], list[str]]:
    scores = {m: _score(m, f) for m in PROFILES}
    rules = []
    hy, dh = "V-Model with Agile iterations", "DevSecOps hybrid (V-Model gates + CI/CD)"
    if f["patient_safety_impact"] >= .7 and f["regulatory_criticality"] >= .7:
        scores["Agile"] = min(scores["Agile"], 60)
        rules.append("R1: patient-safety impact and regulatory criticality are both high -> pure Agile capped at 60 (it does not give validation evidence on its own).")
    if f["regulatory_criticality"] >= .7 and f["change_frequency"] >= .45:
        scores[hy] += 5
        scores[dh] += 3
        rules.append("R2: highly regulated AND changing rules -> bonus for hybrids that keep V-Model validation gates inside iterations.")
    if f["continuous_delivery_need"] >= .7 and f["security_privacy_risk"] >= .6:
        scores[dh] += 6
        scores["DevSecOps"] += 3
        rules.append("R3: strong continuous-delivery need with high security risk -> bonus for DevSecOps-based models.")
    if f["requirement_stability"] >= .8 and f["change_frequency"] <= .3 and f["verification_need"] >= .6:
        scores["V-Model"] += 5
        scores["Waterfall"] += 3
        rules.append("R4: stable requirements and high verification need -> bonus for V-Model/Waterfall.")
    if f["uncertainty"] >= .7:
        scores["Spiral"] += 6
        rules.append("R5: high uncertainty / technical risk -> bonus for Spiral (risk-driven iterations).")
    if f["stakeholder_availability"] < .35:
        for m in ("Agile", hy, dh):
            scores[m] -= 5
        rules.append("R6: stakeholders are rarely available -> penalty for models that need frequent feedback.")
    if f["regulatory_criticality"] >= .7 and f["verification_need"] >= .7:
        scores["Waterfall"] -= 4
        rules.append("R7: validated-system expectations -> Waterfall penalised for late verification and slow response to rule changes.")
    ranking = [{"model": m, "score": round(max(0, min(100, s)), 1)} for m, s in sorted(scores.items(), key=lambda x: -x[1])]
    return ranking, rules


def explain(model: str, f: dict[str, float], ranking: list[dict], rules: list[str]) -> str:
    ideal, w = PROFILES[model]
    fits = sorted(FACTORS, key=lambda k: -(w.get(k, .5) * (1 - abs(f[k] - ideal[k]))))[:4]
    base = f"{model} ranks first ({ranking[0]['score']}%). Best-matching drivers: " + "; ".join(
        f"{FACTORS[k].lower()} {f[k]:.2f} (target {ideal[k]:.2f})" for k in fits
    ) + "."
    if len(ranking) > 1:
        base += f" Runner-up: {ranking[1]['model']} ({ranking[1]['score']}%)."
    if rules:
        base += " Rules applied: " + " ".join(r.split(":")[0] for r in rules) + "."
    if llm.enabled:
        out = llm.json(
            "Write a 3-5 sentence justification for choosing this SDLC model for a regulated pharmacy software project. Use ONLY the "
            "numbers given. Mention one trade-off. Return a JSON string.",
            str({"model": model, "factors": f, "ranking": ranking[:3], "rules": rules}),
            max_tokens=600,
        )
        if isinstance(out, str) and len(out) > 40:
            return out
    return base + " Final adoption needs approval from the project manager, architect, security lead and compliance officer."


# ------------------------------------------------------------------ workflow generation
def _stage(name, acts, roles, deliv, sec, comp, gate, entry, exit_):
    return dict(name=name, activities=acts, roles=roles, deliverables=deliv, security_controls=sec, compliance_checkpoints=comp, gate=gate, entry_criteria=entry, exit_criteria=exit_)


BASE = {
    "PLAN": _stage("Planning and validation plan", ["Confirm scope: prescription-to-dispensing with scheduled-drug register", "Agree roles, tools, risk-based validation plan", "Set up requirement baseline and change-control process"],
                   ["Project manager", "Compliance officer", "Pharmacist (domain lead)"], ["Project plan", "Validation plan", "Stakeholder list"], ["Access model for project artefacts"],
                   ["Compliance officer confirms applicable rules list"], "G0: plan approved", ["Project mandate"], ["Validation plan signed"]),
    "REQ": _stage("Requirements and hazard analysis", ["Elicit and clarify requirements (this tool)", "Hazard analysis: wrong drug, expired batch, missing register entry", "Resolve conflicts and open questions", "Map requirements to rules"],
                  ["Business analyst", "Pharmacist", "Compliance officer"], ["SRS", "Traceability matrix (draft)", "Hazard log", "Compliance matrix"], ["Data-classification of patient data"],
                  ["Every regulatory requirement has a cited source", "Pharmacist approves safety-critical requirements"], "G1: requirement baseline approved", ["Plan signed"], ["No open high-severity conflicts", "Mandatory approvals complete"]),
    "DESIGN": _stage("Architecture and design with threat modelling", ["Design modules (dispensing, register, inventory, billing)", "Threat model: unauthorised override, record tampering, data leakage", "Define audit-trail and register data model", "Interface contracts for legacy systems"],
                     ["Architect", "Security lead", "Developers"], ["Architecture document", "Threat model", "Data model", "Interface specs"], ["Threat modelling", "RBAC design", "Encryption design"],
                     ["Design review against compliance matrix"], "G2: design approved", ["Requirement baseline"], ["Every requirement allocated to a design element"]),
    "BUILD": _stage("Implementation", ["Implement features in small increments", "Peer review of every change", "Unit tests alongside code"], ["Developers"], ["Source code", "Unit tests"],
                    ["Static analysis (SAST)", "Dependency and secret scanning"], ["Safety-critical code reviewed by a second developer"], "Increment done: tests and scans pass", ["Approved design"], ["No critical scan findings"]),
    "VERIFY": _stage("Verification (unit, integration, system)", ["Unit and integration tests", "System tests against SRS", "Regression suite for dispensing and register"], ["QA engineer", "Developers"], ["Test reports", "Updated traceability matrix"],
                     ["Security tests of override and access paths"], ["Each requirement linked to a passed test"], "G3: verification complete", ["Build complete"], ["All Must requirements verified"]),
    "VALIDATE": _stage("Validation with pharmacists", ["Dispensing-accuracy test set (including expired, recalled, H1/X cases)", "Batch-integrity and register-completeness tests", "User acceptance testing by a pharmacist", "Mock inspection using the generated reports"],
                       ["Pharmacist", "QA engineer", "Compliance officer"], ["Validation report with objective evidence", "UAT sign-off"], ["Penetration or vulnerability test"], ["Mock inspection passed"], "G4: validation accepted", ["Verification complete"], ["Pharmacist UAT signed"]),
    "RELEASE": _stage("Compliance approval and release", ["Compliance review of evidence pack", "Go-live checklist and rollback plan", "Training of pharmacy staff"], ["Compliance officer", "Project manager", "Pharmacy owner"], ["Release approval", "Training record"],
                      ["Production access review", "Backup and restore verified"], ["Compliance officer approves release"], "G5: release approved", ["Validation accepted"], ["Approvals recorded in the audit trail"]),
    "OPERATE": _stage("Operation and change control", ["Monitor errors and incidents", "Update schedule lists and rules under change control", "Re-validate on significant change"], ["Pharmacy owner", "Compliance officer", "Support team"], ["Change records", "Incident log"],
                      ["Log monitoring", "Periodic access review"], ["Regulatory-change review each quarter"], "Change gate: impact assessed", ["Released"], ["Change impact assessed and approved"]),
}


def _ph(key, name=None, extra=None, gate=None, iteration=None):
    s = {**BASE[key], "activities": list(BASE[key]["activities"])}
    if name:
        s["name"] = name
    if extra:
        s["activities"] += extra
    if gate:
        s["gate"] = gate
    if iteration:
        s["iteration"] = iteration
    return s


def workflow(model: str) -> list[dict]:
    if model == "Waterfall":
        return [_ph(k) for k in BASE]
    if model == "V-Model":
        ph = [_ph(k) for k in BASE]
        ph[4]["activities"].append("V-mapping: unit tests <-> module design, integration tests <-> architecture, system tests <-> SRS, UAT <-> user needs")
        return ph
    if model == "Agile":
        return [_ph("PLAN", "Product vision and backlog", ["Pharmacist acts as product owner"]), _ph("REQ", "Backlog refinement with compliance acceptance criteria", ["Definition of done includes compliance checks"], "Sprint planning"),
                _ph("BUILD", "Sprint: design, build and test", ["Pharmacist reviews each sprint demo", "Security review of each increment"], "Sprint review", "2-week sprints, repeated until backlog Must items are done"),
                _ph("VALIDATE", "Release hardening and UAT", None, "Release approval"), _ph("RELEASE"), _ph("OPERATE")]
    if model == "Spiral":
        it = "Repeat for 3 spirals: (1) dispensing + register, (2) inventory/expiry/recall, (3) billing, integration, inspection reports"
        return [_ph("PLAN", "Determine objectives, alternatives and constraints", None, "Spiral review", it), _ph("REQ", "Risk analysis and prototype", ["Prototype the riskiest workflow with pharmacists"], "Risk review", it),
                _ph("BUILD", "Develop and verify the spiral increment", None, "Increment verified", it), _ph("VALIDATE", "Customer evaluation and plan next spiral", None, "Spiral evaluation", it), _ph("RELEASE"), _ph("OPERATE")]
    if model == "DevSecOps":
        return [_ph("PLAN", "Plan and threat model"), _ph("BUILD", "Code, build and scan in CI", ["CI pipeline: SAST, SCA, secret scan, SBOM on every change"], "Pipeline green"),
                _ph("VERIFY", "Automated and manual testing", ["DAST on staging", "Dispensing regression pack in CI"]), _ph("RELEASE", "Release approval gate", ["Signed artefacts"]), _ph("OPERATE", "Deploy, operate and monitor", ["Continuous monitoring and alerting"])]
    if model == "V-Model with Agile iterations":
        return [_ph("PLAN"), _ph("REQ", "Requirements and hazard analysis (V-Model left side)"), _ph("DESIGN", "Architecture and threat modelling (V-Model left side)"),
                _ph("BUILD", "Iterative build sprints (Agile)", ["Each sprint delivers one slice, e.g. H1 register, then expiry alerts", "Pharmacist reviews every sprint demo", "Requirement changes go through change control and re-trigger affected tests"], "Sprint gate: tests and scans pass", "2-3 week sprints inside the validated lifecycle"),
                _ph("VERIFY", "Verification at each V level"), _ph("VALIDATE"), _ph("RELEASE"), _ph("OPERATE")]
    return [_ph("PLAN"), _ph("REQ"), _ph("DESIGN"),
            _ph("BUILD", "CI/CD pipeline iterations", ["CI: SAST, SCA, secret scanning, SBOM", "Automated dispensing/register regression pack"], "Pipeline green", "Continuous, with weekly releases to a validation environment"),
            _ph("VALIDATE", "Validation gate (evidence pack)", ["Evidence pack generated from pipeline results and UAT"]), _ph("RELEASE", "Compliance release approval"), _ph("OPERATE", "Operate, monitor and change control", ["Continuous monitoring and alerting"])]


def recommend(reqs: list[Requirement], params: ProjectParams, conflicts: list[Conflict]) -> SdlcResult:
    f = derive_factors(reqs, params, conflicts)
    ranking, rules = rank(f)
    best = ranking[0]["model"]
    return SdlcResult(factors=f, ranking=ranking, rules_fired=rules, recommended=best, explanation=explain(best, f, ranking, rules), workflow=workflow(best))
