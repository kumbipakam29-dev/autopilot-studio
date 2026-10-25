"""Minimal public chat API for AutoPilot Studio.

Only deterministic, low-risk draft tasks run automatically. Sensitive requests
are queued for human approval and never executed by this service.
"""
from collections import defaultdict, deque
from pathlib import Path
from time import monotonic
from typing import Literal
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="AutoPilot Studio Public Agent Portal",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

MAX_REQUESTS_PER_MINUTE = 20
RATE_WINDOW_SECONDS = 60
_request_times: dict[str, deque[float]] = defaultdict(deque)
_approval_queue: list[dict] = []  # Prototype only; volatile and not a durable queue.
APPROVAL_TERMS = re.compile(
    r"\b(publish|post it|send message|dm |direct message|buy|purchase|pay|"
    r"change password|change account|delete|remove repository|transfer money|"
    r"submit application|apply for me|email this|text this)\b",
    re.IGNORECASE,
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    task: Literal["auto", "caption", "reel_script", "content_calendar", "public_summary"] = "auto"


class ChatResponse(BaseModel):
    status: Literal["completed", "needs_approval", "unsupported"]
    task_id: str
    agent: str
    message: str
    result: str | None = None


def _rate_limit_key(request: Request) -> str:
    # Use the direct peer only; never trust arbitrary X-Forwarded-For input.
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
        return (
            f"Draft caption for: {brief}\n\n"
            "Small steps make a real difference. ✨ Tell us what you’re working on, "
            "and save this post for later.\n\n"
            "#SmallBusiness #ContentIdeas #SocialMediaMarketing"
        )
    if task == "reel_script":
        return (
            f"14–20 second Reel concept — {brief}\n"
            "0–3s: Hook: “Need a simpler way to do this?”\n"
            "3–8s: Show the common problem in one clear shot.\n"
            "8–15s: Demonstrate one practical tip or solution.\n"
            "15–20s: CTA: “Save this and tell us what you want next.”"
        )
    if task == "content_calendar":
        return (
            f"7-day starter calendar for: {brief}\n"
            "Day 1: Introduce the business and its purpose\n"
            "Day 2: One useful tip\n"
            "Day 3: Behind-the-scenes concept\n"
            "Day 4: Frequently asked question\n"
            "Day 5: Product/service explainer\n"
            "Day 6: Community question or poll\n"
            "Day 7: Weekly recap and gentle enquiry CTA\n"
            "These are draft ideas, not published posts."
        )
    if task == "public_summary":
        return (
            "Public-research summary task received. This MVP has no web crawler or "
            "external research connection enabled, so it cannot verify current facts. "
            f"Research brief to investigate: {brief}"
        )
    return None


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": app.version, "mode": "prototype-no-external-actions"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request):
    _check_rate_limit(request)
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Please enter a message.")

    task_id = f"APS-{int(monotonic() * 1000)}"
    if APPROVAL_TERMS.search(message):
        _approval_queue.append({
            "task_id": task_id,
            "message": message[:2000],
            "status": "pending_approval",
        })
        return ChatResponse(
            status="needs_approval",
            task_id=task_id,
            agent="approval-gate",
            message=(
                "This request could publish, send, purchase, submit, modify an account, "
                "or delete something. It has not been executed. Human review is required."
            ),
        )

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
            return ChatResponse(
                status="unsupported",
                task_id=task_id,
                agent="router",
                message=(
                    "This prototype supports draft captions, short Reel scripts, "
                    "7-day content calendars, and public-research briefs. Choose one "
                    "of these tasks; unsupported requests are not executed."
                ),
            )

    result = _draft(task, message)
    if result is None:
        return ChatResponse(
            status="unsupported",
            task_id=task_id,
            agent="router",
            message="That task is not in the approved low-risk task registry.",
        )
    return ChatResponse(
        status="completed",
        task_id=task_id,
        agent=f"{task}-agent",
        message="Draft generated locally. Nothing has been published or sent.",
        result=result,
    )
