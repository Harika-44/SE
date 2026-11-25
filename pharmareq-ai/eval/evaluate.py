"""Evaluation harness (plan section 19). Run:  python eval/evaluate.py [--manual-minutes 180]

Measures extraction precision/recall/F1, ambiguity-detection accuracy, conflict-detection recall,
retrieval (citation) hit rate and correctness, scope-guard recall, injection detection, SDLC suitability,
hallucination rate and processing time. Compare against manual analysis by passing your own measured
manual time. Pharmacist satisfaction must be collected with eval/feedback_form.md.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pharmareq.agents import coordinator  # noqa: E402
from pharmareq.cli import load_docs  # noqa: E402
from pharmareq.kb import retriever  # noqa: E402
from pharmareq.schemas import RunRequest  # noqa: E402


def find(run, key):
    k = key.lower()
    return next((r for r in run.requirements if k in r.statement.lower() or k in r.source_quote.lower()), None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual-minutes", type=float, default=None, help="measured time for a human analyst on the same inputs")
    ap.add_argument("--samples", default=str(ROOT / "data" / "samples"))
    a = ap.parse_args()
    gold = json.loads((ROOT / "eval" / "gold.json").read_text())
    run = coordinator.run_pipeline(RunRequest(documents=load_docs([a.samples])), actor="eval")

    G = gold["requirements"]
    matched = [(g, find(run, g["key"])) for g in G]
    tp = sum(1 for _, r in matched if r)
    matched_ids = {r.id for _, r in matched if r}
    fp = [r for r in run.requirements if r.id not in matched_ids]
    neg_hits = [n for n in gold["not_requirements"] if any(n.lower() in r.source_quote.lower() for r in run.requirements)]
    prec = tp / max(1, tp + len(fp))
    rec = tp / len(G)
    f1 = 2 * prec * rec / max(1e-9, prec + rec)

    amb = [(g, r) for g, r in matched if r and "ambiguous" in g]
    amb_ok = sum(1 for g, r in amb if any(i.kind == "ambiguity" for i in r.issues) == g["ambiguous"])
    kb = [(g, r) for g, r in matched if r and g.get("kb")]
    kb_hit = sum(1 for g, r in kb if any(x.kb_id == g["kb"] for x in r.regulations))
    oos = [(g, r) for g, r in matched if r and g.get("out_of_scope")]
    oos_ok = sum(1 for g, r in oos if any(i.kind == "out_of_scope" for i in r.issues))
    cf_found = 0
    for k1, k2 in gold["conflicts"]:
        r1, r2 = find(run, k1), find(run, k2)
        if r1 and r2 and any({r1.id, r2.id} <= set(c.req_ids) and c.kind != "duplicate" for c in run.conflicts):
            cf_found += 1
    ids = {e["id"] for e in retriever.all_entries()}
    cites = [x.kb_id for r in run.requirements for x in r.regulations]
    res = {
        "requirements_extracted": len(run.requirements), "gold_requirements": len(G),
        "extraction_precision": round(prec, 3), "extraction_recall": round(rec, 3), "extraction_f1": round(f1, 3),
        "extracted_not_in_gold (review manually)": [r.statement[:80] for r in fp],
        "non_requirements_wrongly_extracted": neg_hits,
        "ambiguity_detection_accuracy": f"{amb_ok}/{len(amb)}",
        "conflict_detection_recall": f"{cf_found}/{len(gold['conflicts'])}",
        "retrieval_hit_rate (expected rule among cited)": f"{kb_hit}/{len(kb)}",
        "citation_correctness (cited ids exist in KB)": f"{sum(c in ids for c in cites)}/{len(cites)}",
        "clinical_scope_guard_recall": f"{oos_ok}/{len(oos)}",
        "injection_detected": bool(run.security_flags) == gold["injection_expected"],
        "sdlc_recommendation": run.sdlc.recommended, "sdlc_acceptable": run.sdlc.recommended in gold["sdlc_acceptable"],
        "regulatory_control_coverage_pct": run.validation["metrics"]["regulatory_control_coverage_pct"],
        "hallucination_rate_pct (LLM mode only; 0 offline)": run.metrics["hallucination_rate_pct"],
        "processing_ms": run.metrics["ms_total"], "mode": run.mode,
    }
    if a.manual_minutes:
        res["time_saved_pct_vs_manual"] = round(100 * (1 - run.metrics["ms_total"] / 60000 / a.manual_minutes), 2)
    out = ROOT / "eval" / "results.json"
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
