#!/usr/bin/env python3
"""Evidence-first public listing discovery for data-labeling/microtask work.

This program discovers public leads only. It never signs in, applies, submits work,
bypasses access controls, or sends money. Amounts are retained with their unit;
generic page amounts are not treated as task rates.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

USER_AGENT = "AutoPilotStudioResearchBot/0.1 (public listing discovery; low-rate)"
MAX_BYTES = 1_000_000
TIMEOUT_SECONDS = 12
PER_HOST_DELAY_SECONDS = 1.0
RISK_PATTERNS = {
    "upfront_fee": re.compile(r"\b(upfront|registration|joining|unlock|activation)\s+(fee|payment|deposit)\b|pay\s+(first|to start|to unlock)", re.I),
    "deposit": re.compile(r"\bdeposit\b|\bpay\s+to\s+work\b", re.I),
    "account_rental": re.compile(r"\b(rent|lease|sell|buy)\s+(your\s+)?(account|profile)\b", re.I),
    "credential_request": re.compile(r"\b(?:otp|one.time password|password|seed phrase)\b.{0,45}\b(?:send|share|provide|message|give)\b|\b(?:send|share|provide|message|give)\b.{0,45}\b(?:otp|one.time password|password|seed phrase)\b", re.I),
    "fake_reviews": re.compile(r"\b(fake|paid)\s+reviews?\b|\b5.star review\s+for\s+money\b", re.I),
    "captcha_bypass": re.compile(r"\b(captcha bypass|solve captchas? at scale|bypass captcha)\b", re.I),
    "guaranteed_income": re.compile(r"\bguaranteed\s+(income|earnings|profit)\b", re.I),
}
CURRENCY = re.compile(r"(?:(?:₹|INR\s*|Rs\.?\s*)([0-9][0-9,]*(?:\.[0-9]+)?(?:\s*(?:-|–|to)\s*[0-9][0-9,]*(?:\.[0-9]+)?)?)|\bUSD\s*\$?\s*([0-9]+(?:\.[0-9]+)?(?:\s*(?:-|–|to)\s*[0-9]+(?:\.[0-9]+)?)?)|\$\s*([0-9]+(?:\.[0-9]+)?(?:\s*(?:-|–|to)\s*[0-9]+(?:\.[0-9]+)?)?))", re.I)
UNIT = re.compile(r"\b(per\s+(?:(?:approved|accepted)\s+)?(?:task|recording|hour|hr|minute|batch|project|image|audio|page)|/\s*(?:task|hour|hr|batch|image|page)|each\s+(?:(?:approved|accepted)\s+)?(?:task|recording|image|page)|for\s+\d+\s+(?:tasks|images|minutes|hours|pages|prompts))\b", re.I)
RISK_TEXT_LIMIT = 6000

@dataclass
class Source:
    name: str
    url: str
    category: str
    official: bool = True
    region: str = "Check listing"
    notes: str = "Verify current eligibility and payout terms on the official listing."

@dataclass
class Lead:
    source: str
    category: str
    url: str
    fetched_at: str
    http_status: str
    title: str
    snippet: str
    currency: str
    amount: str
    pay_unit: str
    rate_evidence: str
    evidence_url: str
    risk_flags: str
    status: str
    caveat: str

SOURCES = [
    Source("Karmyug AI Jobs", "https://work.karmyug.in/jobs", "voice/data collection", notes="Public task page; task-specific acceptance/rate must be checked."),
    Source("CrowdGen Project Coffee India", "https://crowdgen.com/coffee-en-in/", "data labeling/AI evaluation", region="India; listing states PC/laptop requirement", notes="Published hourly rate is not per-task pay."),
    Source("Corpshore/Jwuma India", "https://platform.corpshore.ai/india", "data annotation/AI evaluation", region="India listing; verify project"),
    Source("Clickworker", "https://www.clickworker.com/clickworker/", "microtasks/data work", notes="Registration and payout methods can vary by country."),
    Source("TELUS Digital AI Community India", "https://jobs.telusdigital.com/search/cfm5/ai-community/jobs/in/country/india", "AI evaluation", region="India"),
    Source("OneForma Jobs", "https://www.oneforma.com/jobs/", "data collection/annotation", notes="Project and language eligibility vary."),
    Source("Toloka Tolokers", "https://toloka.ai/tolokers/", "microtasks/data labeling", notes="Availability and payout vary by region."),
    Source("Microworkers", "https://www.microworkers.com/", "microtasks", notes="Check task legality and minimum payout."),
    Source("Prolific Participant Help", "https://participant-help.prolific.com/en/articles/445007-who-can-participate-in-studies-on-prolific", "research studies", notes="Study participation must be genuine human participation."),
    Source("uTest India Projects", "https://www.utest.com/projects?country=India&tab=all", "software QA/testing", notes="Specific projects may be invite-only; reject any deposit request."),
    Source("Gitcoin Bounties", "https://gitcoin.co/mechanisms/bounties", "open-source bounties", notes="Check exact bounty terms, skills and payout conditions."),
    Source("YPAI Data Annotator India", "https://freelancer.ypai.ai/jobs/openings/data-annotator-in", "image/video/audio/text annotation", region="India; 18+; project qualification required", notes="Official page advertises typical project pay INR 550-800/hour; only the selected project invitation confirms the actual rate and work availability."),
    Source("YPAI Model Evaluator India", "https://freelancer.ypai.ai/jobs/openings/model-evaluator-in", "AI answer evaluation and fact-checking", region="India; 18+; strong reading comprehension required", notes="Official page advertises typical project pay INR 550-800/hour; application review and project availability are not guaranteed."),
    Source("YPAI Data Collection Contributor India", "https://freelancer.ypai.ai/jobs/openings/data-contributor-in", "audio/video/image/text data collection", region="India; 18+; device/project requirements apply", notes="Official page advertises typical project pay INR 550-800/hour and biweekly payments after approval; check the project's exact offer."),
    Source("HumanSignal AI Training Contributors", "https://onboard.humansignal.com/", "expert AI training and data labeling", region="100+ countries claimed; check India eligibility and skills", notes="Rates are shown to matched eligible contributors; do not assume work or a rate before matching."),
    Source("OpenTrain Python Software Engineering LLM Evaluator", "https://www.opentrain.ai/jobs/python-software-engineering-llm-evaluator--cmub37q18000d0agmbhe9iifm/", "specialist code evaluation", region="India listed among eligible countries; English and relevant Python/software judgment required", notes="Specialist role; posted pay and requirements must be rechecked on the individual listing."),
]

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def strip_html(raw: bytes) -> tuple[str, str]:
    text = raw.decode("utf-8", errors="replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title\s*>", text, re.I | re.S)
    title = html.unescape(re.sub(r"\s+", " ", title_match.group(1))).strip() if title_match else ""
    text = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1\s*>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>|</(?:p|div|li|h[1-6]|tr|section|article)>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return title, text.strip()

def extract_pay_evidence(text: str) -> tuple[str, str, str, str]:
    """Return currency, amount, unit, evidence. Never infer a unit from amount alone."""
    for line in text.splitlines():
        if not re.search(r"\b(pay|paid|payment|earn|earning|reward|compensation|rate|per task|per hour|approved task)\b", line, re.I):
            continue
        m = CURRENCY.search(line)
        u = UNIT.search(line)
        if m and u:
            if m.group(1):
                currency, raw_amount = "INR", m.group(1)
            elif m.group(2):
                currency, raw_amount = "USD", m.group(2)
            else:
                currency, raw_amount = "USD", m.group(3)
            amount = re.sub(r"\s*(?:-|–|to)\s*", "-", raw_amount, flags=re.I).replace(",", "")
            return currency, amount, re.sub(r"\s+", " ", u.group(1)).strip(), line[:500]
    return "", "", "", ""

def fetch_public(url: str) -> tuple[str, str, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return "", "blocked_url", "Only valid HTTPS public sources are allowed."
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                return "", str(response.status), "Non-200 response."
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                return "", "too_large", "Response exceeded size cap."
            return body.decode("utf-8", errors="replace"), str(response.status), ""
    except urllib.error.HTTPError as exc:
        return "", str(exc.code), f"HTTP error {exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return "", "fetch_error", str(exc)[:240]

def find_links(page_url: str, raw_html: str, limit: int = 8) -> list[str]:
    """Prefer task/project detail pages; do not waste crawl budget on account pages."""
    base = urllib.parse.urlparse(page_url)
    found = []
    seen = {page_url}
    excluded_path = re.compile(r"/(?:login|log-in|signin|sign-in|register|signup|sign-up|account|privacy|terms|cookies?)(?:/|$)", re.I)
    for href in re.findall(r"""(?is)<a\b[^>]*?href\s*=\s*["']([^"'#]+)["']""", raw_html):
        full = urllib.parse.urljoin(page_url, html.unescape(href))
        p = urllib.parse.urlparse(full)
        if p.scheme != "https" or p.hostname != base.hostname:
            continue
        path = p.path.lower()
        if p.path.lower().endswith((".pdf", ".png", ".jpg", ".jpeg", ".zip", ".exe", ".apk")):
            continue
        if excluded_path.search(path):
            continue
        if full not in seen:
            seen.add(full)
            found.append(full)
    def priority(url: str) -> tuple[int, int]:
        path = urllib.parse.urlparse(url).path.lower().rstrip("/")
        if re.search(r"/(?:jobs|projects|openings|tasks)/[^/]+$", path):
            score = 100
        elif any(term in path for term in ("/jobs/", "/projects/", "/openings/", "/tasks/")):
            score = 60
        else:
            score = 10
        return (score, -len(path))
    return sorted(found, key=priority, reverse=True)[:max(0, limit)]

def classify_risk(text: str) -> list[str]:
    """Flag risky asks, but do not mistake a platform's explicit anti-scam warning for an offer."""
    sample = text[:RISK_TEXT_LIMIT]
    sentences = re.split(r"(?<=[.!?])\\s+|\\n+", sample)
    flags = set()
    denial = re.compile(
        r"\\b(?:no|never|not|without|don't|do not|doesn't|does not|won't|will not|free)\\b"
        r".{0,90}\\b(?:fee|deposit|upfront|joining|registration|unlock|money|pay|payment|charge)\\b",
        re.I,
    )
    for sentence in sentences:
        # These are clear anti-scam denials such as "we never charge a fee" or
        # "there is no registration fee or deposit"; they should not be quarantined.
        if denial.search(sentence):
            continue
        for name, pattern in RISK_PATTERNS.items():
            if pattern.search(sentence):
                flags.add(name)
    return sorted(flags)

def make_lead(source: Source, url: str, status: str, raw: str, error: str = "") -> Lead:
    title, body = strip_html(raw.encode("utf-8")) if raw else ("", "")
    cur, amount, unit, evidence = extract_pay_evidence(body)
    risks = classify_risk(body)
    if risks:
        state = "quarantined_risk_review"
    elif status != "200":
        state = "source_unavailable"
    elif cur and unit and evidence:
        state = "rate_evidence_found_verify_current_listing"
    else:
        state = "lead_found_rate_unverified"
    caveats = [source.notes]
    if error: caveats.append(error)
    if not evidence: caveats.append("No task-specific rate evidence extracted; do not assume pay.")
    if status != "200": caveats.append("Fetch status is not success; retry later or open official page manually.")
    return Lead(source.name, source.category, url, utc_now(), status, title, body[:700], cur, amount, unit, evidence, url if evidence else "", ";".join(risks), state, " ".join(caveats))

def scan(sources: Iterable[Source], max_detail_pages: int = 3) -> list[Lead]:
    leads = []
    host_last: dict[str, float] = {}
    for source in sources:
        queue = [source.url]
        visited = set()
        pages = 0
        while queue and pages < 1 + max_detail_pages:
            url = queue.pop(0)
            if url in visited: continue
            visited.add(url)
            host = urllib.parse.urlparse(url).hostname or ""
            wait = PER_HOST_DELAY_SECONDS - (time.monotonic() - host_last.get(host, 0))
            if wait > 0: time.sleep(wait)
            raw, status, error = fetch_public(url)
            host_last[host] = time.monotonic()
            lead = make_lead(source, url, status, raw, error)
            leads.append(lead)
            pages += 1
            if pages == 1 and status == "200" and not lead.risk_flags:
                queue.extend(find_links(url, raw, limit=max_detail_pages))
    return leads

def write_outputs(leads: list[Lead], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "data-labeling-leads.csv"
    json_path = out_dir / "data-labeling-leads.json"
    rows = [asdict(x) for x in leads]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(Lead.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps({"generated_at": utc_now(), "leads": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    return csv_path, json_path

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    leads = scan(SOURCES)
    csv_path, json_path = write_outputs(leads, Path(args.output_dir))
    print(f"Scanned {len(leads)} public page(s); no login or submission performed.")
    print(f"CSV: {csv_path}\nJSON: {json_path}")
    print("A lead is not a verified job, accepted task, or payout.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
