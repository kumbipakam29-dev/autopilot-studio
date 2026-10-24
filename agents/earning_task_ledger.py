#!/usr/bin/env python3
"""Local-first task ledger. Records user-confirmed task stages; never moves money."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

STAGES = [
    "discovered", "current_listing_verified", "eligibility_check", "applied",
    "qualification", "approved", "work_in_progress", "submitted",
    "accepted", "rejected", "payout_pending", "paid"
]
TERMINAL = {"paid", "rejected"}

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def load(path: Path):
    if not path.exists(): return {"version": 1, "tasks": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("tasks"), list):
        raise ValueError("Unsupported ledger schema")
    return data

def add_task(data, task_id, title, url, currency="", amount="", unit="unknown"):
    if any(t["task_id"] == task_id for t in data["tasks"]):
        raise ValueError("task_id already exists")
    data["tasks"].append({
        "task_id": task_id, "title": title, "url": url, "currency": currency,
        "posted_amount": amount, "pay_unit": unit, "stage": "discovered",
        "created_at": now(), "updated_at": now(), "minutes_spent": 0,
        "accepted_amount": "", "payout_received_amount": "", "payout_confirmed_by_user": False,
        "notes": "Lead only; not income until accepted and payout confirmed."
    })

def update_stage(data, task_id, stage, minutes=None, accepted_amount=None, payout_amount=None, payout_confirmed=False):
    if stage not in STAGES: raise ValueError("Invalid stage")
    task = next((t for t in data["tasks"] if t["task_id"] == task_id), None)
    if task is None: raise ValueError("Unknown task_id")
    current = task["stage"]
    if current in TERMINAL and current != stage: raise ValueError("Cannot change a terminal task stage")
    if stage == "paid" and not payout_confirmed:
        raise ValueError("Mark paid only after user confirms credit in their payment app")
    if stage == "accepted" and accepted_amount is None:
        raise ValueError("Accepted task needs a confirmed accepted amount")
    if minutes is not None:
        if minutes < 0: raise ValueError("minutes cannot be negative")
        task["minutes_spent"] += minutes
    if accepted_amount is not None: task["accepted_amount"] = str(accepted_amount)
    if payout_amount is not None: task["payout_received_amount"] = str(payout_amount)
    if stage == "paid":
        task["payout_confirmed_by_user"] = True
        task["payout_confirmed_at"] = now()
    task["stage"] = stage
    task["updated_at"] = now()

def save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", default="output/task-ledger.json")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("task_id"); a.add_argument("title"); a.add_argument("url")
    a.add_argument("--currency", default=""); a.add_argument("--amount", default=""); a.add_argument("--unit", default="unknown")
    u = sub.add_parser("update"); u.add_argument("task_id"); u.add_argument("stage", choices=STAGES)
    u.add_argument("--minutes", type=int); u.add_argument("--accepted-amount"); u.add_argument("--payout-amount")
    u.add_argument("--confirm-payout", action="store_true")
    args = p.parse_args(); path = Path(args.ledger); data = load(path)
    if args.cmd == "add":
        add_task(data, args.task_id, args.title, args.url, args.currency, args.amount, args.unit)
    else:
        update_stage(data, args.task_id, args.stage, args.minutes, args.accepted_amount, args.payout_amount, args.confirm_payout)
    save(path, data); print(f"Saved {len(data['tasks'])} task(s) to {path}; this does not submit work or transfer funds.")
if __name__ == "__main__": main()
