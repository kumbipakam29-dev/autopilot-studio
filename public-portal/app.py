"""Safety-first public chat API for AutoPilot Studio."""
from collections import defaultdict, deque
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hmac
import os
from pathlib import Path
import re
import sqlite3
from time import monotonic
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("AUTOPILOT_APPROVAL_DB", "/tmp/autopilot-approval-queue.sqlite3"))
APPROVAL_TOKEN_ENV = "AUTOPILOT_APPROVAL_TOKEN"
APPROVAL_RETENTION_DAYS = 7

app = FastAPI(title="AutoPilot Studio Public Agent Portal", version="0.2.0",
              docs_url=None, redoc_url=None, openapi_url=None)

AGENT_REGISTRY = [
    {"id": "caption-agent", "version": "0.2.0", "task": "caption", "status": "available",
     "execution_mode": "deterministic-template", "external_actions": False},
    {"id": "reel_script-agent", "version": "0.2.0", "task": "reel_script", "status": "available",
     "execution_mode": "deterministic-template", "external_actions": False},
    {"id": "content_calendar-agent", "version": "0.2.0", "task": "content_calendar", "status": "available",
     "execution_mode": "deterministic-template", "external_actions": False},
    {"id": "public_summary-agent", "version": "0.2.0", "task": "public_summary", "status": "limited",
     "execution_mode": "brief-only-no-live-research", "external_actions": False},
]
MAX_REQUESTS_PER_MINUTE = 20
RATE_WINDOW_SECONDS = 60
_request_times: dict[str, deque[float]] = defaultdict(deque)

APPROVAL_TERMS = re.compile(
    r"\b(publish|post it|post this|upload|deploy|send|dm|direct message|email|text|"
    r"buy|purchase|pay|change password|change account|delete|remove repository|"
    r"transfer money|submit|apply for me|book|connect account|share publicly|invite)\b",
    re.IGNORECASE,
)
SECRET_PATTERNS = [
    (re.compile(r"(?i)\b(password|passcode|api[_ -]?key|access[_ -]?token|secret)\s*[:=]\s*\S+"),
     r"\1=[REDACTED]"),
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[EMAIL REDACTED]"),
    (re.compile(r"(?<!\d)(?:\+?\d[\d ()-]{8,}\d)(?!\d)"), "[PHONE REDACTED]"),
]

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    task: Literal["auto", "caption", "reel_script", "content_calendar", "public_summary"] = "auto"

class ChatResponse(BaseModel):
    status: Literal["completed", "needs_approval", "unsupported"]
    task_id: str
    agent: str
    message: str
    result: str | None = None

class ApprovalDecision(BaseModel):
    decision: Literal["approved_for_manual_review", "rejected"]

def _connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            task_id TEXT PRIMARY KEY,
            message TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN
                ('pending_approval','approved_for_manual_review','rejected')),
            created_at TEXT NOT NULL,
            reviewed_at TEXT
        )
    """)
    conn.commit()
    return conn

@contextmanager
def _db():
    conn = _connect_db()
    try:
        yield conn
    finally:
        conn.close()

def _cleanup_expired(conn):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=APPROVAL_RETENTION_DAYS)).isoformat()
    conn.execute("DELETE FROM approvals WHERE created_at < ?", (cutoff,))
    conn.commit()

def _redact(message: str) -> str:
    clean = message[:2000]
    for pattern, replacement in SECRET_PATTERNS:
        clean = pattern.sub(replacement, clean)
    return clean

def _enqueue_approval(task_id: str, message: str) -> None:
    with _db() as conn:
        _cleanup_expired(conn)
        conn.execute(
            "INSERT INTO approvals(task_id,message,status,created_at) VALUES(?,?,?,?)",
            (task_id, _redact(message), "pending_approval", datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()

def _require_approval_token(token: str | None) -> None:
    expected = os.environ.get(APPROVAL_TOKEN_ENV, "")
    if not expected:
        raise HTTPException(status_code=503, detail="Approval administration is disabled until a server token is configured.")
    if not token or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Invalid approval token.")

def _rate_limit_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"

def _check_rate_limit(request: Request) -> None:
    now = monotonic()
    bucket = _request_times[_rate_limit_key(request)]
    while bucket and now - bucket[0] >= RATE_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit reached. Please wait a minute.")
    bucket.append(now)

def _draft(task: str, message: str) -> str | None:
    brief = message.strip()
    if task == "caption":
        return (f"Draft caption for: {brief}\n\nSmall steps make a real difference. ✨ Tell us what you’re working on, "
                "and save this post for later.\n\n#SmallBusiness #ContentIdeas #SocialMediaMarketing")
    if task == "reel_script":
        return (f"14–20 second Reel concept — {brief}\n0–3s: Hook: “Need a simpler way to do this?”\n"
                "3–8s: Show the common problem in one clear shot.\n8–15s: Demonstrate one practical tip or solution.\n"
                "15–20s: CTA: “Save this and tell us what you want next.”")
    if task == "content_calendar":
        return (f"7-day starter calendar for: {brief}\nDay 1: Introduce the business and its purpose\n"
                "Day 2: One useful tip\nDay 3: Behind-the-scenes concept\nDay 4: Frequently asked question\n"
                "Day 5: Product/service explainer\nDay 6: Community question or poll\n"
                "Day 7: Weekly recap and gentle enquiry CTA\nThese are draft ideas, not published posts.")
    if task == "public_summary":
        return ("Public-research summary task received. This MVP has no web crawler or external research connection enabled, "
                f"so it cannot verify current facts. Research brief to investigate: {brief}")
    return None

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")

app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")

@app.get("/api/agents")
def agents():
    return {"agents": AGENT_REGISTRY, "count": len(AGENT_REGISTRY)}

@app.get("/api/health")
def health():
    return {"status": "ok", "version": app.version, "mode": "prototype-no-external-actions",
            "approval_storage": "sqlite-with-configurable-path"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request):
    _check_rate_limit(request)
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Please enter a message.")
    task_id = f"APS-{uuid4().hex[:12].upper()}"
    if APPROVAL_TERMS.search(message):
        _enqueue_approval(task_id, message)
        return ChatResponse(status="needs_approval", task_id=task_id, agent="approval-gate",
            message=("This request may publish, send, upload, deploy, purchase, submit, modify an account, or delete something. "
                     "It has not been executed. It is stored for human review only; approval does not execute it."))
    task = payload.task
    if task == "auto":
        lower = message.lower()
        if any(word in lower for word in ("caption", "instagram post", "social post")):
            task = "caption"
        elif any(word in lower for word in ("reel", "short video", "video script")):
            task = "reel_script"
        elif any(word in lower for word in ("calendar", "7-day plan", "weekly content")):
            task = "content_calendar"
        elif any(word in lower for word in ("summarize public", "research brief", "public information")):
            task = "public_summary"
        else:
            return ChatResponse(status="unsupported", task_id=task_id, agent="router",
                message="This prototype supports draft captions, short Reel scripts, 7-day content calendars, and public-research briefs.")
    result = _draft(task, message)
    if result is None:
        return ChatResponse(status="unsupported", task_id=task_id, agent="router",
                            message="That task is not in the approved low-risk task registry.")
    return ChatResponse(status="completed", task_id=task_id, agent=f"{task}-agent",
                        message="Draft generated locally. Nothing has been published or sent.", result=result)

@app.get("/api/approvals")
def list_approvals(x_approval_token: str | None = Header(default=None)):
    _require_approval_token(x_approval_token)
    with _connect_db() as conn:
        _cleanup_expired(conn)
        rows = conn.execute(
            "SELECT task_id,message,status,created_at,reviewed_at FROM approvals ORDER BY created_at DESC LIMIT 100"
        ).fetchall()
    return {"approvals": [dict(row) for row in rows], "count": len(rows),
            "note": "Review decisions never execute external actions."}

@app.post("/api/approvals/{task_id}/decision")
def decide_approval(task_id: str, decision: ApprovalDecision,
                    x_approval_token: str | None = Header(default=None)):
    _require_approval_token(x_approval_token)
    reviewed_at = datetime.now(timezone.utc).isoformat()
    with _connect_db() as conn:
        _cleanup_expired(conn)
        cursor = conn.execute(
            "UPDATE approvals SET status=?, reviewed_at=? WHERE task_id=? AND status='pending_approval'",
            (decision.decision, reviewed_at, task_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            exists = conn.execute("SELECT 1 FROM approvals WHERE task_id=?", (task_id,)).fetchone()
            if not exists:
                raise HTTPException(status_code=404, detail="Approval request not found or expired.")
            raise HTTPException(status_code=409, detail="Approval request has already been reviewed.")
    return {"task_id": task_id, "status": decision.decision,
            "executed": False, "message": "Decision recorded; no external action was executed."}
