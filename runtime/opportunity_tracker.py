#!/usr/bin/env python3
"""Zero-cost opportunity triage for AutoPilot Studio.

Reads a JSON array of opportunities and writes a ranked CSV review queue.
This tool does not scrape websites, log in, contact clients, or submit applications.
Only use sources whose terms permit your collection method.
"""
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

FIELDS = [
    "opportunity_id", "source", "title", "url", "posted_at",
    "payment_text", "eligibility_checked", "fit_score", "risk_flags",
    "status", "approval_required", "notes"
]
ALLOWED_STATUSES = {"new", "needs_verification", "draft_ready", "awaiting_user_approval"}

def score(item):
    points = 0
    flags = []
    title = str(item.get("title", "")).lower()
    description = str(item.get("description", "")).lower()
    url = str(item.get("url", "")).strip()
    source = str(item.get("source", "")).strip()
    if not url.startswith("https://"):
        flags.append("missing_or_non_https_url")
    if not source:
        flags.append("source_missing")
    if not item.get("eligibility_checked", False):
        flags.append("eligibility_not_checked")
    if not item.get("payment_text") or not item.get("payment_verified", False):
        flags.append("payment_not_verified")
    if any(word in title + " " + description for word in ("registration fee", "pay to apply", "deposit required", "crypto deposit")):
        flags.append("possible_upfront_fee")
    if any(word in title + " " + description for word in ("guaranteed income", "instant payout", "no experience earn huge")):
        flags.append("unrealistic_income_claim")
    if any(word in title + " " + description for word in ("social media", "instagram", "content", "caption", "reel", "copywriting")):
        points += 3
    if any(word in title + " " + description for word in ("data labeling", "data annotation", "transcription", "rating task")):
        points += 2
    if item.get("eligibility_checked", False):
        points += 2
    if item.get("payment_verified", False):
        points += 2
    if url.startswith("https://"):
        points += 1
    if flags:
        points -= min(3, len(flags))
    return max(0, min(10, points)), flags

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="runtime/opportunities.json", help="JSON array of opportunity objects")
    parser.add_argument("--output", default="runtime/approval_queue.csv", help="CSV review queue output")
    args = parser.parse_args()
    source_path = Path(args.input)
    if not source_path.exists():
        raise SystemExit(f"Input file not found: {source_path}. Create it as a JSON array; see runtime/README.md.")
    items = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise SystemExit("Input must be a JSON array.")
    rows = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"Item {index} must be an object.")
        fit_score, flags = score(item)
        rows.append({
            "opportunity_id": str(item.get("opportunity_id") or f"opp-{index:04d}"),
            "source": item.get("source", ""),
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "posted_at": item.get("posted_at", ""),
            "payment_text": item.get("payment_text", ""),
            "eligibility_checked": str(bool(item.get("eligibility_checked", False))).lower(),
            "fit_score": fit_score,
            "risk_flags": ";".join(flags),
            "status": "needs_verification" if flags else "awaiting_user_approval",
            "approval_required": "true",
            "notes": item.get("notes", ""),
        })
    rows.sort(key=lambda row: int(row["fit_score"]), reverse=True)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_count": len(items),
        "queue_count": len(rows),
        "needs_verification": sum(r["status"] == "needs_verification" for r in rows),
        "approval_required": True,
        "external_actions_taken": 0,
        "output": str(output_path),
    }, indent=2))

if __name__ == "__main__":
    main()
