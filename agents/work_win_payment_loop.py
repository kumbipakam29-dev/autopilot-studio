#!/usr/bin/env python3
"""Review-first opportunity -> action -> acceptance -> owner-confirmed payment loop."""
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, json, os, sqlite3, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agents import earnings_hunter  # noqa: E402

DEFAULT_OUTPUT = ROOT / "output"
DEFAULT_LEDGER = ROOT / "runtime" / "work_win_payment.sqlite3"
TOOL_REGISTRY = ROOT / "agents" / "tool_registry.json"
ALL_STATUSES = {"new","reviewed","shortlisted","application_ready","applied_by_user","task_started_by_user","submitted_by_user","accepted","rejected","not_eligible","paused","quarantined","paid"}
OWNER_UPDATE_STATUSES = ALL_STATUSES - {"paid","new","quarantined"}
CLIENT_REQUIRED = {"business_name","business_type","observation"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def stable_lead_id(source: str, url: str) -> str:
    return hashlib.sha256((source.strip() + "|" + url.strip()).encode("utf-8")).hexdigest()[:12].upper()


def get_ledger_path(value: str | None = None) -> Path:
    configured = value or os.environ.get("AUTOPILOT_PAYMENT_LEDGER")
    return Path(configured).expanduser() if configured else DEFAULT_LEDGER


def init_ledger(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS leads (
            lead_id TEXT PRIMARY KEY, source TEXT NOT NULL, title TEXT NOT NULL, url TEXT NOT NULL,
            region_or_eligibility TEXT NOT NULL DEFAULT '', task_type TEXT NOT NULL DEFAULT '',
            public_amount_text TEXT NOT NULL DEFAULT '', currency TEXT NOT NULL DEFAULT '',
            payment_signal TEXT NOT NULL DEFAULT '', triage_score INTEGER NOT NULL DEFAULT 0,
            triage_status TEXT NOT NULL DEFAULT 'LEAD_ONLY', public_detail_evidence TEXT NOT NULL DEFAULT '',
            workflow_status TEXT NOT NULL DEFAULT 'new', next_action TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL, last_seen_at TEXT NOT NULL,
            last_note TEXT NOT NULL DEFAULT '')""")
        db.execute("""CREATE TABLE IF NOT EXISTS cycles (
            cycle_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT NOT NULL,
            mode TEXT NOT NULL, candidate_count INTEGER NOT NULL, quarantined_count INTEGER NOT NULL,
            status TEXT NOT NULL)""")
        db.execute("""CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY, lead_id TEXT NOT NULL, amount_inr REAL NOT NULL CHECK(amount_inr > 0),
            method TEXT NOT NULL, evidence_note TEXT NOT NULL, owner_confirmed INTEGER NOT NULL CHECK(owner_confirmed = 1),
            confirmed_at TEXT NOT NULL, FOREIGN KEY(lead_id) REFERENCES leads(lead_id))""")
        db.commit()


def next_action(status: str, triage_status: str, amount: str) -> str:
    if status == "paid":
        return "Owner confirmed the credit; retain private proof in your own payment app."
    if status == "quarantined" or "QUARANTINE" in triage_status:
        return "STOP: risk signal detected. Do not apply, pay, or share credentials; inspect manually."
    if status in {"new","reviewed"}:
        return ("Open the official URL and confirm current role, rate unit, eligibility, deadline, acceptance criteria and payout."
                if amount else "Lead only: open the official URL and confirm a real task is currently available.")
    if status == "shortlisted": return "Check all terms and prepare your own truthful application if eligible."
    if status == "application_ready": return "Draft/checklist ready; owner must review and submit personally."
    if status == "applied_by_user": return "Check the official account/email for the response and record it honestly."
    if status == "task_started_by_user": return "Follow the official rubric; keep evidence private and local."
    if status == "submitted_by_user": return "Wait for quality review; do not mark accepted or paid without evidence."
    if status == "accepted": return "Check payout schedule/threshold and confirm the actual credit before payment entry."
    if status == "rejected": return "Review the provider's reason; appeal only through the official channel if appropriate."
    if status == "not_eligible": return "Do not misrepresent identity, location, language or qualifications; move on."
    if status == "paused": return "Paused by owner; no action until reviewed."
    return "Review official source and decide manually."


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_opportunities(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Opportunity output not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def import_opportunities(csv_path: Path, db_path: Path) -> tuple[int, int]:
    init_ledger(db_path)
    now, imported, quarantined = utc_now(), 0, 0
    with sqlite3.connect(db_path) as db:
        for row in read_opportunities(csv_path):
            source = (row.get("source") or "unknown source").strip()
            url = (row.get("url") or "").strip()
            if not url.startswith("https://"): continue
            title = (row.get("title") or source + " public lead").strip()[:240]
            lead_id = stable_lead_id(source, url)
            triage = (row.get("triage_status") or "LEAD_ONLY").strip()
            risky = "QUARANTINE" in triage
            quarantined += int(risky)
            try: score = int(float((row.get("triage_score") or "0").strip()))
            except ValueError: score = 0
            old = db.execute("SELECT workflow_status,created_at FROM leads WHERE lead_id=?", (lead_id,)).fetchone()
            status = ("paid" if old[0] == "paid" else ("quarantined" if risky else old[0])) if old else ("quarantined" if risky else "new")
            created = old[1] if old else now
            amount = (row.get("public_amount_text") or "").strip()
            db.execute("""INSERT INTO leads(
                lead_id,source,title,url,region_or_eligibility,task_type,public_amount_text,currency,payment_signal,
                triage_score,triage_status,public_detail_evidence,workflow_status,next_action,created_at,updated_at,last_seen_at,last_note
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(lead_id) DO UPDATE SET
                source=excluded.source,title=excluded.title,url=excluded.url,
                region_or_eligibility=excluded.region_or_eligibility,task_type=excluded.task_type,
                public_amount_text=excluded.public_amount_text,currency=excluded.currency,
                payment_signal=excluded.payment_signal,triage_score=excluded.triage_score,
                triage_status=excluded.triage_status,public_detail_evidence=excluded.public_detail_evidence,
                workflow_status=excluded.workflow_status,next_action=excluded.next_action,
                updated_at=excluded.updated_at,last_seen_at=excluded.last_seen_at""",
                (lead_id,source,title,url,(row.get("region_or_eligibility") or "")[:300],
                 (row.get("task_type") or "")[:300],amount,(row.get("currency") or "")[:60],
                 (row.get("payment_signal") or "")[:120],score,triage[:120],
                 (row.get("public_detail_evidence") or "")[:1000],status,next_action(status,triage,amount),
                 created,now,now,""))
            imported += 1
        db.commit()
    return imported, quarantined


def load_queue(db_path: Path) -> list[dict[str, Any]]:
    with sqlite3.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("""SELECT lead_id,source,title,url,region_or_eligibility,task_type,public_amount_text,
            currency,payment_signal,triage_score,triage_status,workflow_status,next_action,last_seen_at
            FROM leads ORDER BY CASE WHEN workflow_status='quarantined' THEN 1
            WHEN workflow_status='paid' THEN 2 ELSE 0 END, triage_score DESC,last_seen_at DESC""").fetchall()
    return [dict(row) for row in rows]


def build_reports(outdir: Path, rows: list[dict[str, Any]], cycle_id: str, mode: str,
                  imported: int, quarantined: int) -> tuple[Path, Path]:
    fields = ["lead_id","source","title","url","region_or_eligibility","task_type","public_amount_text",
              "currency","payment_signal","triage_score","triage_status","workflow_status","next_action","last_seen_at"]
    queue_path, report_path = outdir/"work_win_payment_queue.csv", outdir/"work_win_payment_report.md"
    write_csv(queue_path, rows, fields)
    actionable = [r for r in rows if r["workflow_status"] not in {"quarantined","paid"}][:20]
    lines = [
        "# AutoPilot Studio — Work → Win → Payment loop", "",
        f"- Cycle ID: {cycle_id}", f"- Mode: {mode}", f"- Leads imported/refreshed: {imported}",
        f"- Risk-quarantined leads in this cycle: {quarantined}", f"- Total leads in local ledger: {len(rows)}",
        f"- Actionable leads: {sum(r['workflow_status'] not in {'quarantined','paid'} for r in rows)}", "",
        "This loop scans public pages and prepares next actions only. It does not log into accounts, apply, submit work, send messages, publish, or initiate payments.", "",
        "## Prioritized next actions", ""
    ]
    if not actionable: lines += ["No actionable leads in the board. Run a fresh scan or add a user-reviewed public-business prospect CSV.", ""]
    for i, row in enumerate(actionable, 1):
        lines += [f"### {i}. {row['title']}", f"- Lead ID: {row['lead_id']} | Source: {row['source']}",
            f"- Public rate evidence: {row['public_amount_text'] or 'not found'} ({row['currency'] or 'currency not stated'})",
            f"- Status: {row['workflow_status']} | Triage: {row['triage_status']}",
            f"- Eligibility signal: {row['region_or_eligibility'] or 'not established'}",
            f"- Official URL: {row['url']}", f"- Next action: {row['next_action']}", ""]
    lines += [
        "## Payment truth standard", "",
        "A listing, application, completed task, dashboard estimate, invoice, or payout announcement is not a payment. The payment-confirm command requires the owner to confirm the actual credit. This creates an owner-confirmed record only; it does not independently connect to or verify bank/UPI/payment accounts.", "",
        "## Safety and privacy", "",
        "- Never pay joining/deposit/unlock fees or fake location, identity, voice, qualifications, answers or proof.",
        "- Keep passwords, OTPs, ID scans, bank/UPI details, payment screenshots, client/customer personal data and tokens out of the repo and artifacts.",
        "- Recheck official terms, country/language eligibility, rate unit, acceptance criteria, payout threshold and payout route before working.",
        "- Outreach drafts are not sent. External publishing, submissions, purchases and money transfers are disabled.", "",
        "## Local ledger", "",
        "The SQLite ledger is stored at runtime/work_win_payment.sqlite3 by default (or AUTOPILOT_PAYMENT_LEDGER). The CI runner is ephemeral; the database is intentionally not included in artifacts. The CSV/Markdown artifact contains the public-source action board only.", ""
    ]
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return queue_path, report_path


def run_cycle(limit: int = 30, offline: bool = False, ledger_path: Path | None = None,
              output_dir: Path | None = None) -> dict[str, Any]:
    if not 1 <= limit <= 200: raise ValueError("limit must be between 1 and 200")
    db_path, outdir = ledger_path or get_ledger_path(), output_dir or DEFAULT_OUTPUT
    init_ledger(db_path)
    outdir.mkdir(parents=True, exist_ok=True)
    started, old_out = utc_now(), earnings_hunter.OUT
    earnings_hunter.OUT = outdir
    try:
        opportunity_path = earnings_hunter.run_hunt(offline=offline, limit=limit)
    finally:
        earnings_hunter.OUT = old_out
    imported, quarantined = import_opportunities(Path(opportunity_path), db_path)
    cycle_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S-UTC")
    mode = "offline-test" if offline else "live-public-page-scan"
    rows = load_queue(db_path)
    queue, report = build_reports(outdir, rows, cycle_id, mode, imported, quarantined)
    with sqlite3.connect(db_path) as db:
        db.execute("INSERT INTO cycles VALUES(?,?,?,?,?,?,?)",
                   (cycle_id,started,utc_now(),mode,imported,quarantined,"completed"))
        db.commit()
    return {"status":"completed","cycle_id":cycle_id,"mode":mode,"imported_or_refreshed":imported,
            "quarantined":quarantined,"total_leads_in_ledger":len(rows),"queue_csv":str(queue),
            "report_md":str(report),"database_path":str(db_path),"database_upload_allowed":False}


def update_lead_status(lead_id: str, status: str, note: str = "", ledger_path: Path | None = None) -> dict[str, Any]:
    if status not in OWNER_UPDATE_STATUSES:
        raise ValueError("Status is not allowed here; use payment-confirm for paid. New/quarantined statuses cannot be overridden.")
    path = ledger_path or get_ledger_path()
    init_ledger(path)
    with sqlite3.connect(path) as db:
        row = db.execute("SELECT triage_status,public_amount_text FROM leads WHERE lead_id=?", (lead_id,)).fetchone()
        if not row: raise ValueError(f"Unknown lead_id: {lead_id}")
        if "QUARANTINE" in (row[0] or ""): raise ValueError("Lead is quarantined; risk flags cannot be bypassed by a status update.")
        db.execute("UPDATE leads SET workflow_status=?,next_action=?,last_note=?,updated_at=? WHERE lead_id=?",
            (status,next_action(status,row[0],row[1]),note.strip()[:300],utc_now(),lead_id))
        db.commit()
    return {"status":status,"lead_id":lead_id,"external_action_executed":False,
            "note":"Owner-recorded status only. No application, submission, message or payment was executed."}


def confirm_payment(lead_id: str, amount_inr: float, method: str, evidence_note: str,
                    confirm_received: bool, ledger_path: Path | None = None) -> dict[str, Any]:
    if not confirm_received: raise ValueError("Payment not recorded. Pass --confirm-received only after checking the actual credit.")
    if amount_inr <= 0: raise ValueError("amount-inr must be greater than zero")
    if method not in {"UPI","bank_transfer","PayPal","Wise","other"}: raise ValueError("Unsupported payment method label")
    if not evidence_note.strip(): raise ValueError("Provide a brief note about when you checked the credit; do not include transaction credentials.")
    path = ledger_path or get_ledger_path()
    init_ledger(path)
    with sqlite3.connect(path) as db:
        if not db.execute("SELECT 1 FROM leads WHERE lead_id=?", (lead_id,)).fetchone():
            raise ValueError(f"Unknown lead_id: {lead_id}")
        now = utc_now()
        payment_id = "PAY-" + hashlib.sha256(f"{lead_id}|{amount_inr:.2f}|{now}".encode()).hexdigest()[:12].upper()
        db.execute("INSERT INTO payments VALUES(?,?,?,?,?,1,?)",
            (payment_id,lead_id,amount_inr,method,evidence_note.strip()[:300],now))
        db.execute("UPDATE leads SET workflow_status='paid',next_action=?,updated_at=?,last_note=? WHERE lead_id=?",
            (next_action("paid","", ""),now,"Owner-confirmed credit; not independently verified.",lead_id))
        db.commit()
    return {"status":"paid_owner_confirmed","payment_id":payment_id,"lead_id":lead_id,
            "amount_inr":round(amount_inr,2),"method":method,"independently_verified":False,
            "note":"Owner-confirmed record only; no bank, UPI or payment account was inspected."}


def get_status(ledger_path: Path | None = None) -> dict[str, Any]:
    path = ledger_path or get_ledger_path()
    init_ledger(path)
    with sqlite3.connect(path) as db:
        counts = {r[0]:r[1] for r in db.execute("SELECT workflow_status,COUNT(*) FROM leads GROUP BY workflow_status")}
        total = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        cycles = db.execute("SELECT COUNT(*) FROM cycles").fetchone()[0]
        payments = db.execute("SELECT COUNT(*),COALESCE(SUM(amount_inr),0) FROM payments WHERE owner_confirmed=1").fetchone()
        latest = db.execute("SELECT cycle_id,finished_at,mode,status,candidate_count FROM cycles ORDER BY finished_at DESC LIMIT 1").fetchone()
    registry = json.loads(TOOL_REGISTRY.read_text(encoding="utf-8"))
    tools = registry.get("tools", [])
    return {"status":"ready","registered_tools":len(tools),
        "implemented_tools":sum(1 for t in tools if str(t.get("status","")).startswith("implemented")),
        "disabled_side_effect_tools":sum(1 for t in tools if t.get("side_effects") and t.get("status")=="disabled"),
        "leads_total":total,"lead_status_counts":counts,"cycles_recorded":cycles,
        "owner_confirmed_payments_count":payments[0],"owner_confirmed_payments_total_inr":round(payments[1],2),
        "payment_independent_verification":False,
        "latest_cycle":({"cycle_id":latest[0],"finished_at":latest[1],"mode":latest[2],"status":latest[3],"candidate_count":latest[4]} if latest else None),
        "ledger_path":str(path),"database_upload_allowed":False}


def draft_client_pitches(input_csv: Path, output_dir: Path | None = None) -> dict[str, Any]:
    if not input_csv.exists(): raise FileNotFoundError(f"Prospect CSV not found: {input_csv}")
    outdir = output_dir or DEFAULT_OUTPUT
    outdir.mkdir(parents=True, exist_ok=True)
    with input_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = CLIENT_REQUIRED - set(reader.fieldnames or [])
        if missing: raise ValueError(f"Prospect CSV missing columns: {sorted(missing)}")
        prospects = list(reader)
    drafts, skipped = [], []
    for row in prospects:
        name, kind = (row.get("business_name") or "").strip()[:120], (row.get("business_type") or "").strip()[:80]
        observation, profile = (row.get("observation") or "").strip()[:350], (row.get("public_profile_url") or "").strip()[:500]
        idea = (row.get("recommended_idea") or "").strip()[:240]
        if not name or not kind or not observation:
            skipped.append({"business_name":name or "(unnamed row)","reason":"missing business name/type/observation"}); continue
        if profile and not profile.startswith("https://"):
            skipped.append({"business_name":name,"reason":"profile URL must be public HTTPS or blank"}); continue
        idea = idea or f"a 7-day content plan for {kind.lower()} with helpful tips, behind-the-scenes content and a clear enquiry CTA"
        message = (f"Hi {name} team — I came across your public page and noticed {observation}. I run AutoPilot Digital Studio and am testing a small social-content starter for {kind.lower()} businesses: 3 post concepts/captions, one 14–20 second Reel script, and a 7-day content calendar. One idea could be: {idea}. The introductory test quote is ₹499, with one revision; you keep control of publishing. Would a sample idea be useful? No worries if not.")
        drafts.append({"business_name":name,"public_profile_url":profile,"message_draft":message})
    path = outdir / "client_outreach_drafts.md"
    lines = ["# AutoPilot Digital Studio — client outreach drafts","",
        "DRAFT ONLY. No message has been sent. Validate each public observation and check channel rules before using it.",""]
    for item in drafts:
        lines += [f"## {item['business_name']}",f"- Public profile: {item['public_profile_url'] or 'not supplied'}",
            "- Status: DRAFT_ONLY_NOT_SENT","",item["message_draft"],""]
    lines += ["## Safety","",
        "Do not bulk-send, scrape personal data, or follow up repeatedly after no reply/opt-out. ₹499 is an experimental quote, not a validated market average. Label portfolio examples SPEC; never invent client names, testimonials or results.",""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"status":"completed","draft_count":len(drafts),"skipped_count":len(skipped),
            "output":str(path),"messages_sent":0,"skipped":skipped}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    cycle = sub.add_parser("cycle", help="scan public work pages and update local review board")
    cycle.add_argument("--limit", type=int, default=30); cycle.add_argument("--offline", action="store_true")
    cycle.add_argument("--ledger"); cycle.add_argument("--output-dir")
    status = sub.add_parser("status", help="show safe counts and owner-confirmed payment total")
    status.add_argument("--ledger")
    update = sub.add_parser("update", help="record owner action; this does not execute it")
    update.add_argument("--lead-id", required=True); update.add_argument("--status", choices=sorted(OWNER_UPDATE_STATUSES), required=True)
    update.add_argument("--note", default=""); update.add_argument("--ledger")
    payment = sub.add_parser("payment-confirm", help="record an owner-confirmed actual credit")
    payment.add_argument("--lead-id", required=True); payment.add_argument("--amount-inr", type=float, required=True)
    payment.add_argument("--method", choices=["UPI","bank_transfer","PayPal","Wise","other"], required=True)
    payment.add_argument("--evidence-note", required=True); payment.add_argument("--confirm-received", action="store_true", required=True)
    payment.add_argument("--ledger")
    pitches = sub.add_parser("draft-client-pitches", help="draft but never send personalized outreach from a business-level CSV")
    pitches.add_argument("--input", required=True); pitches.add_argument("--output-dir")
    args = parser.parse_args()
    try:
        if args.command == "cycle":
            result = run_cycle(args.limit,args.offline,Path(args.ledger) if args.ledger else None,Path(args.output_dir) if args.output_dir else None)
        elif args.command == "status":
            result = get_status(Path(args.ledger) if args.ledger else None)
        elif args.command == "update":
            result = update_lead_status(args.lead_id,args.status,args.note,Path(args.ledger) if args.ledger else None)
        elif args.command == "payment-confirm":
            result = confirm_payment(args.lead_id,args.amount_inr,args.method,args.evidence_note,args.confirm_received,Path(args.ledger) if args.ledger else None)
        else:
            result = draft_client_pitches(Path(args.input),Path(args.output_dir) if args.output_dir else None)
    except (OSError,ValueError,sqlite3.Error) as exc:
        print(json.dumps({"status":"failed","error":str(exc)},indent=2),file=sys.stderr); return 1
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
