"""Safe, zero-dependency runtime for registered AutoPilot Studio agents.

This is a local task runner for implemented deterministic handlers, not a fleet
of 500 always-on AI workers. Unknown/unimplemented agents return blocked.
External actions are never executed; sensitive requests are approval-gated.
"""
from __future__ import annotations
import json
import re
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "agents" / "registry.json"
DEFAULT_LEDGER = ROOT / "runtime" / "run_ledger.sqlite3"
SENSITIVE = re.compile(r"\b(publish|post now|send|dm|email this|buy|purchase|pay|payment|delete|deploy|submit application|trade|transfer funds|change password|change security)\b", re.I)

def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    agents = data.get("agents", [])
    ids = [a.get("id") for a in agents]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate agent IDs in registry")
    return data

def _caption(task: str, inputs: dict[str, Any]) -> dict[str, Any]:
    business = str(inputs.get("business", "your business")).strip()[:120]
    offer = str(inputs.get("offer", "our latest offer")).strip()[:240]
    audience = str(inputs.get("audience", "local customers")).strip()[:120]
    caption = f"{business}: {offer}. Made for {audience}.\n\nWhat would you like to know? Message the business directly for details."
    return {"deliverable_type": "caption_draft", "content": caption, "requires_human_review": True}

def _reel(task: str, inputs: dict[str, Any]) -> dict[str, Any]:
    topic = str(inputs.get("topic", "introducing your business")).strip()[:180]
    return {"deliverable_type":"reel_script_draft","duration_seconds":"14-20","scenes":[
        {"time":"0-3s","visual":"Show the problem or most eye-catching product","voiceover":topic},
        {"time":"3-8s","visual":"Show 2-3 useful details or benefits","voiceover":"Here is what makes this worth a closer look."},
        {"time":"8-15s","visual":"Demonstrate the product or service in action","voiceover":"Keep it clear, specific, and honest."},
        {"time":"15-20s","visual":"Brand name and simple call to action","voiceover":"Save this for later or contact us to learn more."}],
        "requires_human_review":True}

def _content_calendar(task: str, inputs: dict[str, Any]) -> dict[str, Any]:
    topics = ["Introduce the business","Answer a common customer question","Show the process","Share a practical tip","Feature a product or service","Behind the scenes","Invite questions or bookings"]
    return {"deliverable_type":"7_day_calendar","days":[{"day":i+1,"theme":topic,"format":["image post","short reel","carousel"][i%3],"status":"draft"} for i,topic in enumerate(topics)],"requires_human_review":True}

def _website_audit(task: str, inputs: dict[str, Any]) -> dict[str, Any]:
    url = str(inputs.get("url","")).strip()[:500]
    return {"deliverable_type":"website_audit_checklist","target_url":url or None,"checks":[
        {"check":"Mobile layout","status":"not_checked","note":"Inspect on a phone; no live crawl was performed."},
        {"check":"Contact and booking path","status":"not_checked","note":"Confirm a visitor can find a working contact method."},
        {"check":"Page titles and descriptions","status":"not_checked","note":"Review each important page for unique, accurate metadata."},
        {"check":"Loading and broken links","status":"not_checked","note":"Run an approved browser/performance check before reporting findings."},
        {"check":"Trust and accessibility","status":"not_checked","note":"Check readable contrast, clear pricing, and accurate claims."}],
        "notice":"Checklist only; no claim that the website was visited or audited."}

def _job_alert(task: str, inputs: dict[str, Any]) -> dict[str, Any]:
    role = str(inputs.get("role","entry-level remote work")).strip()[:120]
    return {"deliverable_type":"job_search_filter","target_role":role,"filters":["official employer/careers source","country and eligibility","posted date","pay unit and payout method","no joining/deposit fee","application deadline"],"status":"no_live_search_connector","notice":"No jobs were fetched; connect an approved source before presenting live listings."}

HANDLERS = {
    "APS-SOCIAL-GROWTH-121": _caption,
    "APS-SOCIAL-GROWTH-122": _reel,
    "APS-AUTOMATION-SERVICE-128": _content_calendar,
    "APS-LEAD-GENERATION-016": _website_audit,
    "APS-MONITORING-ALERTS-008": _job_alert,
}

def init_ledger(path: Path = DEFAULT_LEDGER) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY, agent_id TEXT NOT NULL, agent_version TEXT NOT NULL,
            model_version TEXT NOT NULL, status TEXT NOT NULL, task TEXT NOT NULL,
            created_at REAL NOT NULL, finished_at REAL, result_json TEXT, error TEXT,
            code_commit TEXT, requires_approval INTEGER NOT NULL DEFAULT 0)""")
        db.execute("""CREATE TABLE IF NOT EXISTS approvals (
            approval_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, action TEXT NOT NULL,
            status TEXT NOT NULL, created_at REAL NOT NULL)""")

def run_task(agent_id: str, task: str, inputs: dict[str, Any] | None = None,
             registry_path: Path = REGISTRY_PATH, ledger_path: Path = DEFAULT_LEDGER,
             code_commit: str | None = None) -> dict[str, Any]:
    inputs = inputs or {}
    registry = load_registry(registry_path)
    agent = next((a for a in registry["agents"] if a["id"] == agent_id), None)
    run_id = str(uuid.uuid4())
    if not agent:
        return {"run_id":run_id,"agent_id":agent_id,"status":"blocked","reason":"unknown_agent_id"}
    init_ledger(ledger_path)
    needs_approval = bool(SENSITIVE.search(task))
    status = "awaiting_approval" if needs_approval else ("ready" if agent_id in HANDLERS else "blocked")
    result = None
    error = None
    if not needs_approval and agent_id in HANDLERS:
        try:
            result = HANDLERS[agent_id](task, inputs)
            status = "completed"
        except Exception as exc:
            status, error = "failed", type(exc).__name__
    elif not needs_approval:
        error = "handler_not_implemented"
    now = time.time()
    with sqlite3.connect(ledger_path) as db:
        db.execute("INSERT INTO runs(run_id,agent_id,agent_version,model_version,status,task,created_at,finished_at,result_json,error,code_commit,requires_approval) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
          (run_id,agent_id,agent.get("agent_version","unknown"),agent.get("model_version","unknown"),status,task[:2000],now,now,json.dumps(result,ensure_ascii=False) if result is not None else None,error,code_commit,int(needs_approval)))
        if needs_approval:
            db.execute("INSERT INTO approvals(approval_id,run_id,action,status,created_at) VALUES(?,?,?,?,?)",
                       (str(uuid.uuid4()),run_id,task[:240],"pending",now))
    return {"run_id":run_id,"agent_id":agent_id,"agent_version":agent.get("agent_version"),"model_version":agent.get("model_version"),"status":status,"requires_approval":needs_approval,"result":result,"error":error}

def get_status(ledger_path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    registry = load_registry()
    counts = {s:0 for s in ["planned","ready","running","blocked","failed"]}
    for agent in registry["agents"]:
        state = agent.get("execution_status","planned")
        counts[state] = counts.get(state,0)+1
    counts["registered"] = len(registry["agents"])
    recent = []
    if ledger_path.exists():
        with sqlite3.connect(ledger_path) as db:
            db.row_factory = sqlite3.Row
            recent = [dict(row) for row in db.execute("SELECT run_id,agent_id,agent_version,model_version,status,created_at,finished_at,error FROM runs ORDER BY created_at DESC LIMIT 20")]
    return {"registry_counts":counts,"implemented_handlers":sorted(HANDLERS),"recent_runs":recent}
