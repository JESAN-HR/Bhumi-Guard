"""Measure labeled synthetic rule agreement, separately from extraction."""

import json, time
from pathlib import Path
from backend.app.fixtures import scenarios
from backend.app.rules import analyze

rows = []
start = time.perf_counter()
for s in scenarios():
    outcome, findings = analyze(
        s["fields"], s["holding"], s["transfers"], s["mutation"], ["DEMO-RECORDS"]
    )
    actual = sorted(f["code"] for f in findings)
    rows.append(
        {
            "scenario": s["id"],
            "expected": sorted(s["expected"]),
            "actual": actual,
            "match": actual == sorted(s["expected"]),
            "outcome": outcome,
        }
    )
result = {
    "dataset": "22 labeled synthetic cases, hand-authored expected rule codes",
    "rule_version": "1.0",
    "cases": len(rows),
    "matched": sum(r["match"] for r in rows),
    "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
    "extraction_evaluated": False,
    "limitation": "Synthetic agreement is not evidence of nationwide accuracy or extraction performance.",
    "results": rows,
}
Path("docs/rule-evaluation.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print(json.dumps({k: v for k, v in result.items() if k != "results"}, indent=2))
