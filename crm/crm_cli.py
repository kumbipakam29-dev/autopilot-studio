#!/usr/bin/env python3
"""Local-first, no-network CRM for AutoPilot Studio. Standard library only."""
import argparse
import csv
import sqlite3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DB = ROOT / "autopilot_crm.sqlite3"
STAGES = ("new", "researched", "audited", "draft_ready", "approved_to_contact",
          "contacted", "replied", "meeting", "proposal", "client",
          "not_a_fit", "do_not_contact", "lost")
FIELDS = (
    "business_name", "category", "city_area", "source_name", "source_url",
    "public_contact_channel", "contact_value", "work_description", "observed_need",
    "evidence_url", "verified_date", "offer_primary", "offer_custom", "language",
    "tone", "stage", "next_action", "follow_up_date", "outreach_status", "response",
    "quoted_price", "payment_verified", "client_work", "do_not_contact", "notes"
)
SCHEMA = """CREATE TABLE IF NOT EXISTS leads (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 business_name TEXT NOT NULL, category TEXT DEFAULT '', city_area TEXT DEFAULT '',
 source_name TEXT DEFAULT '', source_url TEXT DEFAULT '', public_contact_channel TEXT DEFAULT '',
 contact_value TEXT DEFAULT '', work_description TEXT DEFAULT '', observed_need TEXT DEFAULT '',
 evidence_url TEXT DEFAULT '', verified_date TEXT DEFAULT '', offer_primary TEXT DEFAULT '',
 offer_custom TEXT DEFAULT '', language TEXT DEFAULT 'English', tone TEXT DEFAULT 'friendly',
 stage TEXT DEFAULT 'new', next_action TEXT DEFAULT 'Verify official profile and recent content',
 follow_up_date TEXT DEFAULT '', outreach_status TEXT DEFAULT 'not drafted', response TEXT DEFAULT '',
 quoted_price TEXT DEFAULT '', payment_verified TEXT DEFAULT 'no', client_work TEXT DEFAULT '',
 do_not_contact TEXT DEFAULT 'no', notes TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 updated_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(business_name, source_url)
);
CREATE TABLE IF NOT EXISTS draft_log (
 id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id INTEGER NOT NULL, draft_text TEXT NOT NULL,
 language TEXT DEFAULT '', tone TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(lead_id) REFERENCES leads(id)
);"""

def connect():
    ROOT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(SCHEMA)
    return con

def clean(v):
    return "" if v is None else str(v).strip()

def add_record(con, row):
    payload = {f: clean(row.get(f)) for f in FIELDS}
    payload["business_name"] = clean(row.get("business_name"))
    if not payload["business_name"]:
        raise ValueError("business_name is required")
    payload["stage"] = payload["stage"] or "new"
    if payload["stage"] not in STAGES:
        raise ValueError("stage must be one of: " + ", ".join(STAGES))
    payload["language"] = payload["language"] or "English"
    payload["tone"] = payload["tone"] or "friendly"
    payload["payment_verified"] = payload["payment_verified"] or "no"
    payload["do_not_contact"] = payload["do_not_contact"] or "no"
    columns = ", ".join(FIELDS)
    marks = ", ".join("?" for _ in FIELDS)
    updates = ", ".join(f"{f}=excluded.{f}" for f in FIELDS if f not in ("business_name", "source_url"))
    con.execute(
        f"INSERT INTO leads ({columns}) VALUES ({marks}) "
        f"ON CONFLICT(business_name, source_url) DO UPDATE SET {updates}, updated_at=CURRENT_TIMESTAMP",
        [payload[f] for f in FIELDS])
    found = con.execute("SELECT id FROM leads WHERE business_name=? AND source_url=?",
                        (payload["business_name"], payload["source_url"])).fetchone()
    return found["id"]

def cmd_init(_):
    with connect():
        print(f"CRM initialized: {DB}")
        print("Database is local. Do not upload it to GitHub.")

def cmd_add(args):
    row = {k: getattr(args, k, "") for k in FIELDS}
    row["business_name"] = args.business
    with connect() as con:
        lead_id = add_record(con, row)
    print(f"Saved lead #{lead_id}: {args.business}")

def cmd_import(args):
    count = 0
    with open(args.csv_file, newline="", encoding="utf-8-sig") as f, connect() as con:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "business_name" not in reader.fieldnames:
            raise SystemExit("CSV must contain a business_name column.")
        for row in reader:
            if not clean(row.get("business_name")):
                continue
            add_record(con, row)
            count += 1
    print(f"Imported/updated {count} rows. Verify sources before outreach.")

def cmd_list(args):
    with connect() as con:
        if args.stage:
            rows = con.execute("SELECT id,business_name,category,city_area,stage,offer_primary,source_url FROM leads WHERE stage=? ORDER BY id", (args.stage,))
        else:
            rows = con.execute("SELECT id,business_name,category,city_area,stage,offer_primary,source_url FROM leads ORDER BY id")
        print("ID | BUSINESS | CATEGORY | AREA | STAGE | OFFER | SOURCE")
        for r in rows:
            print(" | ".join(clean(r[k]).replace("|", "/") for k in r.keys()))

def cmd_update(args):
    if args.field == "stage" and args.value not in STAGES:
        raise SystemExit("Invalid stage: " + ", ".join(STAGES))
    with connect() as con:
        cur = con.execute(f"UPDATE leads SET {args.field}=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (args.value, args.id))
        if not cur.rowcount:
            raise SystemExit(f"No lead found with ID {args.id}")
    print(f"Updated lead #{args.id}: {args.field}")

def cmd_show(args):
    with connect() as con:
        r = con.execute("SELECT * FROM leads WHERE id=?", (args.id,)).fetchone()
        if not r:
            raise SystemExit(f"No lead found with ID {args.id}")
        for k in r.keys():
            print(f"{k}: {clean(r[k])}")

def make_draft(r, offer, language, tone, cta):
    name = clean(r["business_name"])
    category = clean(r["category"]) or "business"
    area = clean(r["city_area"])
    work = clean(r["work_description"])
    observed = clean(r["observed_need"])
    evidence = clean(r["evidence_url"] or r["source_url"])
    location = f" in {area}" if area else ""
    personalization = observed if observed else (f"I saw your public page about {work}." if work else f"I came across your public {category} business page.")
    if language.lower() in ("hinglish", "hindi"):
        body = (f"Namaste {name} ji! {personalization}\n\n"
                f"AutoPilot Digital Studio ki taraf se ek idea: {offer}.\n"
                "Main ideas ko aapke actual services aur brand voice ke hisaab se customize karunga—koi guaranteed result claim nahi.\n\n"
                f"{cta or 'Kya main aapke business ke liye ek sample content idea share karun?'}\n\n"
                "Dhanyavaad,\nAutoPilot Digital Studio")
    else:
        body = (f"Hello {name},\n\n{personalization} I’m reaching out with one relevant content idea for your {category}{location}.\n\n"
                f"I run AutoPilot Digital Studio and would like to offer: {offer}.\n"
                "I’d tailor the work to your services and brand voice, without promising unverified results.\n\n"
                f"{cta or 'Would it be useful if I shared one tailored sample idea before discussing any package?'}\n\n"
                "Regards,\nAutoPilot Digital Studio")
    if tone.lower() == "formal":
        body = body.replace("Hello ", "Dear ")
    if evidence:
        body += f"\n\nReference reviewed: {evidence}"
    return body

def cmd_draft(args):
    with connect() as con:
        r = con.execute("SELECT * FROM leads WHERE id=?", (args.id,)).fetchone()
        if not r:
            raise SystemExit(f"No lead found with ID {args.id}")
        if clean(r["do_not_contact"]).lower() in ("yes", "true", "1"):
            raise SystemExit("Blocked: this lead is marked do_not_contact.")
        offer = args.offer or clean(r["offer_custom"]) or clean(r["offer_primary"]) or "a tailored social-media content package"
        language = args.language or clean(r["language"]) or "English"
        tone = args.tone or clean(r["tone"]) or "friendly"
        draft = make_draft(r, offer, language, tone, args.cta or "")
        con.execute("INSERT INTO draft_log(lead_id,draft_text,language,tone) VALUES(?,?,?,?)",
                    (args.id, draft, language, tone))
        con.execute("UPDATE leads SET outreach_status='draft ready', stage=CASE WHEN stage='new' THEN 'draft_ready' ELSE stage END, updated_at=CURRENT_TIMESTAMP WHERE id=?", (args.id,))
    print("UNSENT DRAFT — review facts, channel and permission before sending.\n")
    print(draft)

def build_parser():
    p = argparse.ArgumentParser(description="AutoPilot Studio local CRM (no scraping or sending)")
    sub = p.add_subparsers(required=True)
    x = sub.add_parser("init", help="initialize local SQLite database")
    x.set_defaults(func=cmd_init)
    x = sub.add_parser("add", help="add one lead")
    x.add_argument("--business", required=True)
    for field in FIELDS:
        if field != "business_name":
            x.add_argument("--" + field.replace("_", "-"), dest=field, default=None)
    x.set_defaults(func=cmd_add)
    x = sub.add_parser("import-csv", help="import a permitted CSV")
    x.add_argument("csv_file")
    x.set_defaults(func=cmd_import)
    x = sub.add_parser("list", help="list leads")
    x.add_argument("--stage", choices=STAGES)
    x.set_defaults(func=cmd_list)
    x = sub.add_parser("show", help="show one lead")
    x.add_argument("id", type=int)
    x.set_defaults(func=cmd_show)
    x = sub.add_parser("update", help="update a field")
    x.add_argument("id", type=int)
    x.add_argument("field", choices=FIELDS)
    x.add_argument("value")
    x.set_defaults(func=cmd_update)
    x = sub.add_parser("draft", help="generate a customized unsent draft")
    x.add_argument("id", type=int)
    x.add_argument("--offer")
    x.add_argument("--language", choices=("English", "Hinglish", "Hindi"))
    x.add_argument("--tone", choices=("friendly", "professional", "formal"))
    x.add_argument("--cta")
    x.set_defaults(func=cmd_draft)
    return p

if __name__ == "__main__":
    args = build_parser().parse_args()
    try:
        args.func(args)
    except (sqlite3.Error, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
