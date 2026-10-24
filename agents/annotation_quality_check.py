#!/usr/bin/env python3
"""Validate a text-labeling CSV schema with deterministic, offline checks."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ("record_id", "text", "intent", "sentiment", "priority", "label_rationale")
ALLOWED_LABELS = {
    "intent": {"billing", "technical_support", "account_access", "delivery", "product_question", "refund_request", "praise", "other"},
    "sentiment": {"positive", "neutral", "negative"},
    "priority": {"low", "normal", "high"},
}

def validate_csv(path: Path) -> dict[str, Any]:
    report = {"input_file": str(path), "valid": False, "rows_checked": 0, "error_count": 0,
              "warning_count": 0, "errors": [], "warnings": [], "label_counts": {},
              "note": "Schema QA only: a human must still verify semantic label correctness against the client rubric."}
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            missing = [field for field in REQUIRED_FIELDS if field not in headers]
            if missing:
                report["errors"].append({"row": 1, "field": "header", "message": "Missing columns: " + ", ".join(missing)})
                report["error_count"] += 1
                return report
            seen = set()
            counts = {field: Counter() for field in ALLOWED_LABELS}
            for row_num, row in enumerate(reader, 2):
                report["rows_checked"] += 1
                for field in REQUIRED_FIELDS:
                    if not (row.get(field) or "").strip():
                        report["errors"].append({"row": row_num, "field": field, "message": "Required value is blank"})
                        report["error_count"] += 1
                record_id = (row.get("record_id") or "").strip()
                if record_id and record_id in seen:
                    report["errors"].append({"row": row_num, "field": "record_id", "message": f"Duplicate record_id: {record_id}"})
                    report["error_count"] += 1
                if record_id:
                    seen.add(record_id)
                for field, allowed in ALLOWED_LABELS.items():
                    value = (row.get(field) or "").strip().lower()
                    if value:
                        counts[field][value] += 1
                        if value not in allowed:
                            report["errors"].append({"row": row_num, "field": field, "message": f"Invalid label '{value}'"})
                            report["error_count"] += 1
                rationale = (row.get("label_rationale") or "").strip()
                if rationale and len(rationale) < 8:
                    report["warnings"].append({"row": row_num, "field": "label_rationale", "message": "Rationale may be too short"})
                    report["warning_count"] += 1
            report["label_counts"] = {field: dict(values) for field, values in counts.items()}
            if report["rows_checked"] == 0:
                report["warnings"].append({"row": 2, "field": "data", "message": "No data rows"})
                report["warning_count"] += 1
            report["valid"] = report["error_count"] == 0
    except (OSError, UnicodeError, csv.Error) as exc:
        report["errors"].append({"row": 0, "field": "file", "message": f"Could not read CSV: {exc}"})
        report["error_count"] += 1
    return report

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    result = validate_csv(args.input)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
