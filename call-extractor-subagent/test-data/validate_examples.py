#!/usr/bin/env python3
"""Contract test for call-extractor outputs.
Checks that each example output conforms to the subagent's schema, and that
the edge-case (short) call is correctly flagged low-confidence.
Run: python3 test-data/validate_examples.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "..", "examples")

SCHEMA = {
    "meta": ["source_file", "call_id", "call_url", "extraction_date", "call_date",
             "call_duration_minutes", "call_language", "call_scope", "rep", "confidence_overall"],
    "account": ["name", "segment", "segment_confidence", "region", "region_confidence", "country", "description"],
    "products": ["mentioned", "primary_focus", "multi_product"],
    "switching_forces": ["push", "pull", "anxiety", "habit", "trigger_event",
                         "push_verbatim", "pull_verbatim", "anxiety_verbatim"],
    "competitors": ["named", "context"],
    "deal_signals": ["stage_hint", "urgency", "blockers_mentioned", "next_steps_mentioned"],
}
SEGMENTS = {"SaaS / Software", "E-commerce / Retail", "Gaming", "Media / Streaming",
            "Fintech", "Healthtech", "Enterprise IT", "Other"}

def check(rec, name):
    errs = []
    for section, keys in SCHEMA.items():
        if section not in rec:
            errs.append(f"missing section '{section}'"); continue
        for k in keys:
            if k not in rec[section]:
                errs.append(f"{section}.{k} missing")
    for lst in ["use_cases", "pain_points"]:
        if not isinstance(rec.get(lst), list):
            errs.append(f"{lst} must be a list")
    if rec.get("account", {}).get("segment") not in SEGMENTS | {None}:
        errs.append(f"invalid segment '{rec['account'].get('segment')}'")
    # verbatim quotes must be non-empty strings when present
    for uc in rec.get("use_cases", []):
        if uc.get("verbatim_quote") in (None, ""):
            errs.append("use_case has empty verbatim_quote")
    return errs

def main():
    failures = 0
    for f in sorted(os.listdir(EX)):
        if not f.endswith(".output.json"):
            continue
        rec = json.load(open(os.path.join(EX, f)))
        errs = check(rec, f)
        conf = rec["meta"]["confidence_overall"]
        dur = rec["meta"]["call_duration_minutes"]
        # edge-case rule: short calls (<3 min) must be low confidence with no use cases
        if dur < 3.0:
            if conf >= 0.3: errs.append(f"short call not flagged low-confidence (conf={conf})")
            if rec.get("use_cases"): errs.append("short call should have no use_cases")
        status = "PASS" if not errs else "FAIL"
        if errs: failures += 1
        print(f"[{status}] {f}  (conf={conf}, dur={dur}m)")
        for e in errs:
            print(f"        - {e}")
    print("\n" + ("ALL CONTRACT CHECKS PASSED" if failures == 0 else f"{failures} file(s) FAILED"))
    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    main()
