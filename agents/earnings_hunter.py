#!/usr/bin/env python3
"""Public-source microtask discovery and safe triage. Does not log in or submit work."""
from __future__ import annotations
import argparse, csv, datetime as dt, html, re, sys, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
USER_AGENT = "AutoPilotStudio-EarningsHunter/1.0 (+public page discovery; no login or form submissions)"
MAX_BYTES, TIMEOUT = 450_000, 12

# Official starting points only; each specific job's existence/rate still needs verification.
SOURCES = [
 {"name":"Karmyug AI","url":"https://work.karmyug.in/","type":"AI data tasks / language recording / transcription","region":"India","payout_note":"Check each task's stated rate and approval rules; rate varies."},
 {"name":"TELUS Digital AI Community - India","url":"https://jobs.telusdigital.com/search/cfm5/ai-community/jobs/in/country/india","type":"AI rating / search evaluation / language projects","region":"India","payout_note":"Project/role-specific; read the official listing before applying."},
 {"name":"Clickworker","url":"https://www.clickworker.com/clickworker/","type":"Microtasks / AI data / UHRS when available","region":"Availability varies by country","payout_note":"Confirm country and payout method are supported in the account before working."},
 {"name":"Microworkers","url":"https://www.microworkers.com/","type":"Small online tasks","region":"Availability and task rules vary","payout_note":"KYC and withdrawal threshold apply; never submit fabricated proof."},
 {"name":"Toloka","url":"https://toloka.ai/tolokers/","type":"Data annotation / evaluation tasks","region":"Check current country and project eligibility","payout_note":"Task availability and payment eligibility vary; check current terms."},
 {"name":"OneForma","url":"https://www.oneforma.com/jobs/","type":"Data collection / language / AI projects","region":"Project-specific","payout_note":"Read project rate, qualification, and payment terms before starting."},
 {"name":"CrowdGen by Appen","url":"https://crowdgen.com/","type":"AI data / rating / language projects","region":"Project-specific","payout_note":"Project-specific; verify pay, country eligibility, and payment method."},
 {"name":"Gitcoin / Buidlbox bounty ecosystem","url":"https://gitcoin.co/mechanisms/bounties","type":"Scoped open-source, research, design, and development bounties","region":"Global; wallet/tax/payment terms may apply","payout_note":"Confirm live amount, deadline, acceptance criteria, and payout terms."},
 {"name":"uTest — Project Radar Hindi-English subtitle evaluation","url":"https://www.utest.com/projects/Radar-India","type":"Hindi-English subtitle quality evaluation / paid software testing","region":"India; Hindi-English bilingual ability required for this project","payout_note":"Official project page lists start date Oct 30, 2026 and task/time details; exact payout is not shown in the public excerpt, so confirm in project invitation."},
 {"name":"uTest — India projects board","url":"https://www.utest.com/projects?country=India&tab=all","type":"Software testing / UX studies / functional test cases","region":"India; project-specific qualification and invitation required","payout_note":"Public project board changes frequently; verify exact test cases, payout, and eligibility before accepting."},
 {"name":"UserTest Pro India","url":"https://www.usertestpro.com/get-paid-to-test","type":"Website/app/ads user research and usability studies","region":"India; study-specific screening","payout_note":"Official page advertises studies and weekly rewards via gift card or UPI; amount varies by study and is often above ₹200, so check the displayed payout first."},
 {"name":"Smallest AI Contributor","url":"https://contributor.smallest.ai/","type":"Indian-language audio transcription and voice data quality","region":"Remote; language-specific openings, including Indian languages","payout_note":"Official contributor page describes hourly payment and monthly bank payout; rate and open language roles must be confirmed before doing work."},
 {"name":"Corpshore / Jwuma India AI data work","url":"https://platform.corpshore.ai/india","type":"AI model evaluation / text annotation / transcription / quality assurance","region":"India; language and role qualification required","payout_note":"Official page lists India roles and work types; rate is not assumed and must be confirmed in the offer."},
 {"name":"Prolific participant studies","url":"https://participant-help.prolific.com/en/articles/445007-who-can-participate-in-studies-on-prolific","type":"Research studies and surveys","region":"India appears on the supported-country list; account verification and possible waitlist apply","payout_note":"Study supply varies and India eligibility does not guarantee immediate access; confirm current study pay and payout terms."},
 {"name":"YPAI — Hindi Annotation Roles","url":"https://freelancer.ypai.ai/jobs/hindi/annotation","type":"Hindi AI data annotation role directory","region":"India; remote, with language/project-specific eligibility","payout_note":"Some YPAI role pages list typical project pay around ₹550–₹800/hour; only use the rate shown on the exact role/invitation and verify the rate unit before accepting."},
 {"name":"Perit — Hindi Freelance AI Data Annotator","url":"https://perit.ai/careers/hindi-freelance-transcription","type":"Hindi transcription review and AI data annotation","region":"India; remote; laptop/desktop, headphones and strong Hindi writing required","payout_note":"Official career page says rate is confirmed on application and is per hour of audio output; no numeric rate is assumed.","detail_page":True},
 {"name":"TSMG — Hindi Audio Transcription Specialist","url":"https://jobs.lever.co/tsmg/6a9979b9-3929-4e1d-9689-97926bc65dd5","type":"Hindi audio data collection and transcription","region":"Remote in India; freelance/independent-contractor project terms","payout_note":"Official application says payment is based on validated work completed; confirm the rate and contract terms before accepting.","detail_page":True},
 {"name":"Sigma AI — Hindi, Bengali and English linguistic projects","url":"https://careers.sigma.ai/jobs/8569387-bengali-india-hindi-and-english-linguistic-projects-remote-sigma-ai","type":"Annotation, correction, transcription, evaluation, voice and localization tasks","region":"India; fully remote; apply only for languages genuinely spoken/proven","payout_note":"Recent official listing describes project types but does not state a numeric rate in the public excerpt; confirm rate and payout terms before accepting.","detail_page":True},
 {"name":"Lionbridge — Hindi Transcriber","url":"https://jobs.eu.lever.co/lionbridge/6108498b-2ae3-43cd-8629-7edb52dca516","type":"Hindi transcription and audio annotation","region":"Remote; listing includes India among eligible locations; shift and language requirements apply","payout_note":"Public listing has shown a $10–$16/hour range; verify that the role and range remain active and applicable to India before relying on it.","detail_page":True},
]
TASK_WORDS = re.compile(r"task|job|project|bount|microtask|annotat|transcri|recording|rater|assessor|analyst|evaluator|data collection|label|earn|apply|work from|contributor", re.I)
RISK_WORDS = re.compile(r"pay\s*(?:a|an|the)?\s*(?:deposit|fee|joining fee|registration fee)|upfront\s*(?:payment|fee)|guaranteed\s+income|fake\s+(?:review|rating|proof|account)|buy\s+(?:followers|likes|reviews)|captcha\s*(?:bypass|solver)|otp\s*sharing|share\s+(?:your\s+)?password|crypto\s+deposit|investment\s+required|install\s+an\s+unknown\s+apk", re.I)
RUPEE_AMOUNT = re.compile(r"(?:₹|(?<![A-Za-z])INR\s*|(?<![A-Za-z])Rs\.?\s*)(\d[\d,]*(?:\.\d{1,2})?)", re.I)
FOREIGN_AMOUNT = re.compile(r"(?:\$|USD\s*|€|EUR\s*|£|GBP\s*)(\d[\d,]*(?:\.\d{1,2})?)", re.I)
INR_MIN, INR_MAX = 50.0, 200.0

def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()

def get_host(url: str) -> str:
    return (urllib.parse.urlparse(url).hostname or "").lower()

def allowed_same_site_url(url: str, base_url: str) -> bool:
    parsed = urllib.parse.urlparse(urllib.parse.urljoin(base_url, url))
    base_host, host = get_host(base_url), (parsed.hostname or "").lower()
    bad_ext = (".pdf", ".doc", ".docx", ".zip", ".png", ".jpg", ".jpeg")
    return parsed.scheme == "https" and bool(host) and (host == base_host or host.endswith("." + base_host)) and not parsed.path.lower().endswith(bad_ext)

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts, self.text_parts, self.links = [], [], []
        self.in_title, self.anchor_href, self.anchor_text, self.skip_depth = False, None, [], 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title": self.in_title = True
        if tag in {"script", "style", "noscript", "svg"}: self.skip_depth += 1
        if tag == "a" and attrs.get("href"):
            self.anchor_href, self.anchor_text = attrs["href"], []
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth: self.skip_depth -= 1
        if tag == "a" and self.anchor_href:
            label = clean_text(" ".join(self.anchor_text))
            if label: self.links.append((label, self.anchor_href))
            self.anchor_href, self.anchor_text = None, []
    def handle_data(self, data):
        if self.skip_depth: return
        value = clean_text(data)
        if not value: return
        self.text_parts.append(value)
        if self.in_title: self.title_parts.append(value)
        if self.anchor_href: self.anchor_text.append(value)

def fetch_public_page(url: str, require_same_path: bool = False) -> tuple[str | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            if get_host(response.geturl()) != get_host(url): return None, "redirected to different host; skipped"
            if require_same_path:
                requested_path = urllib.parse.urlparse(url).path.rstrip("/") or "/"
                final_path = urllib.parse.urlparse(response.geturl()).path.rstrip("/") or "/"
                if final_path != requested_path: return None, "redirected to different path; skipped"
            ctype = response.headers.get("Content-Type", "").lower()
            if "text/html" not in ctype and "application/xhtml+xml" not in ctype: return None, "not HTML; skipped"
            data = response.read(MAX_BYTES + 1)[:MAX_BYTES]
            return data.decode(response.headers.get_content_charset() or "utf-8", errors="replace"), "fetched"
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return None, f"unavailable ({type(exc).__name__})"

def extract_amount(text: str) -> tuple[str, str, str]:
    rupee_matches, foreign_matches = RUPEE_AMOUNT.findall(text), list(FOREIGN_AMOUNT.finditer(text))
    if rupee_matches:
        values = []
        seen = set()
        for raw in rupee_matches:
            try:
                value = float(raw.replace(",", ""))
            except ValueError:
                continue
            if value not in seen:
                values.append(value)
                seen.add(value)
        if values:
            in_range = [v for v in values if INR_MIN <= v <= INR_MAX]
            return "INR", ", ".join(f"₹{v:g}" for v in values[:4]), "TARGET_RANGE_MATCH" if in_range else "INR_AMOUNT_OUTSIDE_TARGET"
    if foreign_matches:
        # Keep the currency marker; a bare "150" is not sufficient evidence of USD/EUR.
        amounts = []
        for match in foreign_matches:
            label = clean_text(match.group(0))
            if label and label not in amounts:
                amounts.append(label)
        return "FOREIGN_CURRENCY_UNCONVERTED", ", ".join(amounts[:4]), "CURRENCY_CONVERSION_AND_PAYOUT_CHECK_REQUIRED"
    return "", "", "NO_PUBLIC_AMOUNT_FOUND"

def score_candidate(title: str, snippet: str, source_name: str, source_region: str):
    joined = clean_text(f"{title} {snippet}")
    risk = RISK_WORDS.search(joined)
    currency, amount, signal = extract_amount(joined)
    score, reasons = 0, []
    if currency == "INR" and signal == "TARGET_RANGE_MATCH": score += 40; reasons.append("explicit INR amount in target range")
    elif currency == "INR": score += 20; reasons.append("explicit INR amount")
    elif currency == "FOREIGN_CURRENCY_UNCONVERTED": score += 8; reasons.append("foreign amount found; not converted")
    if TASK_WORDS.search(joined): score += 12; reasons.append("task/work wording")
    if "India" in source_region or re.search(r"\bIndia\b|\bIN\b", joined): score += 10; reasons.append("India relevance signal")
    if source_name: score += 8; reasons.append("curated official source")
    if risk: score -= 100; reasons.append("risk phrase detected; quarantine")
    status = "QUARANTINE_RISK_REVIEW" if risk else ("AMOUNT_FOUND_REVIEW_TERMS" if amount else "NO_PUBLIC_AMOUNT_FOUND")
    return score, amount, currency, signal, status + (" — " + "; ".join(reasons) if reasons else "")

def make_candidate(source, title, url, snippet, page_status, kind):
    score, amount, currency, signal, note = score_candidate(title, snippet, source["name"], source["region"])
    if page_status != "fetched": score -= 5
    status = "QUARANTINE_RISK_REVIEW" if "QUARANTINE_RISK_REVIEW" in note else ("REVIEW_TERMS" if amount else "LEAD_ONLY")
    return {
      "discovered_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "source":source["name"],
      "candidate_type":kind,"title":clean_text(title)[:180],"url":url,"region_or_eligibility":source["region"],
      "task_type":source["type"],"public_amount_text":amount,"currency":currency,"payment_signal":signal,
      "triage_score":str(score),"triage_status":status,"score_notes":note,"payout_or_eligibility_note":source["payout_note"],
      "page_fetch_status":page_status,"required_next_step":"Open official page; confirm current task, rate, eligibility, deadline and payout before deciding manually.",
      "automation_status":"DISCOVERY_ONLY_NO_LOGIN_NO_SUBMISSION"}

def relevant_detail_facts(parser):
    # Use the main page's leading content only. Job boards often append unrelated
    # recommendation cards with high hourly rates; do not attach those to this task.
    raw_text = clean_text(" ".join(parser.text_parts))
    stop = re.search(r"\b(?:similar projects|related projects|recommended projects|more projects|you may also like|related opportunities|similar jobs|recommended jobs|related listings|featured jobs|other projects|you might also be interested)\b", raw_text, re.I)
    if stop:
        raw_text = raw_text[:stop.start()]
    raw_text = raw_text[:1200]
    fact_pattern = re.compile(r"(₹|INR|Rs\.?|\$|USD|€|EUR|£|GBP|per\s+(?:approved\s+)?(?:task|recording|image|minute|hour)|payment|payout|paid|rate|reward|compensation|eligib|India|resident|country|deadline|minimum|qualification|weekly|monthly)", re.I)
    facts = []
    # Keep a limited number of unique task facts in page order.
    for sentence in re.split(r"(?<=[.!?])\s+|\s{2,}", raw_text):
        cleaned = clean_text(sentence)
        if cleaned and fact_pattern.search(cleaned) and cleaned not in facts:
            facts.append(cleaned)
        if len(facts) >= 12:
            break
    return " ".join(facts)[:900]

def eligibility_evidence(text):
    snippets = re.findall(r"[^.!?\n]{0,80}(?:India|Indian|resident|residents|country|eligible|eligibility|location|remote|worldwide|US only|United States|language requirement)[^.!?\n]{0,100}", text, re.I)
    return clean_text(" | ".join(snippets[:5]))[:700]

def is_task_detail_path(url):
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lower().rstrip("/")
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 2 and parsed.hostname and parsed.hostname.lower().endswith("lever.co"):
        return True
    if len(parts) < 2:
        return False
    if parts[0] in {"jobs", "projects", "careers", "job", "role"}:
        return parts[-1] not in {"", "index", "careers", "jobs", "projects", "openings"}
    return False


def task_link_priority(label, url):
    text = clean_text(label + " " + urllib.parse.urlparse(url).path).lower()
    score = 0
    preferred = ("hindi", "india", "indian", "local maps", "local search", "online-data-labeling", "search-evaluation", "language", "translation", "bilingual", "recording", "transcription", "ai-evaluation", "data-labeling", "speech", "annotat", "evaluator")
    excluded = ("physician", "clinical", "ehr-cases", "doctor", "las-vegas", "nevada", "3d-home-capture", "overnight-home-video", "us-only")
    score += sum(18 for phrase in preferred if phrase in text)
    score -= sum(100 for phrase in excluded if phrase in text)
    if "/jobs/" in urllib.parse.urlparse(url).path.lower() or "/projects/" in urllib.parse.urlparse(url).path.lower():
        score += 5
    if label.strip().lower() == "apply":
        score -= 2
    return score

def discover_source(source, offline=False):
    base = make_candidate(source, source["name"] + " — official starting point", source["url"], source["type"], "offline mode", "PLATFORM_LEAD")
    if offline:
        return [base], {"source":source["name"],"fetch_status":"offline mode","candidate_links_extracted":"0","detail_pages_checked":"0"}
    body, status = fetch_public_page(source["url"], require_same_path=bool(source.get("detail_page")))
    if not body:
        base["page_fetch_status"] = status
        base["triage_score"] = str(int(base["triage_score"])-5)
        return [base], {"source":source["name"],"fetch_status":status,"candidate_links_extracted":"0","detail_pages_checked":"0"}
    parser = PageParser()
    try: parser.feed(body)
    except Exception: pass
    page_title = clean_text(" ".join(parser.title_parts)) or source["name"] + " public page"
    if source.get("detail_page"):
        facts = relevant_detail_facts(parser)
        row = make_candidate(source, page_title, source["url"], facts or source["type"], status, "TASK_DETAIL_PAGE")
        row["task_type"] = page_title or source["type"]
        row["region_or_eligibility"] = eligibility_evidence(facts) or source["region"]
        row["public_detail_evidence"] = facts
        row["eligibility_evidence"] = eligibility_evidence(facts)
        rows = [row]
    else:
        rows = [make_candidate(source, page_title, source["url"], source["type"], status, "OFFICIAL_PAGE_SCAN")]
    # Prioritize likely India/language/data tasks and avoid spending the small fetch budget on visibly US-only or credential-gated specialties.
    ordered_links = sorted(parser.links, key=lambda item: task_link_priority(item[0], urllib.parse.urljoin(source["url"], item[1])), reverse=True)
    seen, count, detail_count = {source["url"]}, 0, 0
    for label, href in ordered_links:
        url = urllib.parse.urljoin(source["url"], href)
        parsed = urllib.parse.urlparse(url)
        if not allowed_same_site_url(url, source["url"]): continue
        url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", parsed.query, ""))
        if url in seen or len(seen) >= 60 or not TASK_WORDS.search(label): continue
        seen.add(url)
        is_detail = is_task_detail_path(url)
        detail_body, detail_status = (None, "not attempted")
        if is_detail and detail_count < 5:
            detail_body, detail_status = fetch_public_page(url, require_same_path=True)
            detail_count += 1
        if detail_body:
            detail_parser = PageParser()
            try: detail_parser.feed(detail_body)
            except Exception: pass
            detail_title = clean_text(" ".join(detail_parser.title_parts))
            facts = relevant_detail_facts(detail_parser)
            title = clean_text(label + (" — " + detail_title if detail_title and detail_title.lower() not in label.lower() else ""))[:240]
            row = make_candidate(source, title, url, facts or label, detail_status, "TASK_DETAIL_PAGE")
            row["task_type"] = detail_title or label
            row["region_or_eligibility"] = eligibility_evidence(facts) or "Not established on this page; verify role-specific eligibility"
            row["public_detail_evidence"] = facts
            row["eligibility_evidence"] = eligibility_evidence(facts)
            rows.append(row)
        else:
            row = make_candidate(source, label, url, label, status if not is_detail else detail_status, "SAME_SITE_LINK_LEAD")
            row["region_or_eligibility"] = "Not established on this link; verify role-specific eligibility"
            row["public_detail_evidence"] = ""
            row["eligibility_evidence"] = ""
            rows.append(row)
        count += 1
    return rows, {"source":source["name"],"fetch_status":status,"candidate_links_extracted":str(count),"detail_pages_checked":str(detail_count)}

def write_csv(path, rows, columns):
    with path.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=columns,extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)

def count_verified_target_rate_rows(candidates):
    # A generic platform homepage mentioning a rupee amount is not a paid task offer.
    # Count only a specific detail page with visible evidence for that exact task.
    return sum(
        r.get("candidate_type") == "TASK_DETAIL_PAGE"
        and r.get("payment_signal") == "TARGET_RANGE_MATCH"
        and r.get("triage_status") == "REVIEW_TERMS"
        and bool(r.get("public_detail_evidence"))
        and bool(RUPEE_AMOUNT.search(r.get("public_detail_evidence", "")))
        for r in candidates
    )

def count_detail_pages_with_public_pay(candidates):
    # Count only specific task-detail pages whose own visible text contains a currency amount.
    # Do not count broad career boards, authored payout notes, or parent-page estimates.
    return sum(
        r.get("candidate_type") == "TASK_DETAIL_PAGE"
        and r.get("triage_status") == "REVIEW_TERMS"
        and bool(r.get("public_detail_evidence"))
        and r.get("payment_signal") not in {"NO_PUBLIC_AMOUNT_FOUND", ""}
        for r in candidates
    )

def run_hunt(offline=False, limit=30):
    OUT.mkdir(parents=True,exist_ok=True)
    candidates, source_report = [], []
    for source in SOURCES:
        try:
            rows, report = discover_source(source,offline)
            candidates.extend(rows); source_report.append(report)
        except Exception as exc:
            source_report.append({"source":source["name"],"fetch_status":f"error ({type(exc).__name__})","candidate_links_extracted":"0"})
    candidates.sort(key=lambda r:(r["triage_status"]!="QUARANTINE_RISK_REVIEW",int(r["triage_score"])),reverse=True)
    candidates = candidates[:max(1,min(200,limit))]
    run_id=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S-UTC")
    columns=["discovered_at_utc","source","candidate_type","title","url","region_or_eligibility","task_type","public_amount_text","currency","payment_signal","triage_score","triage_status","score_notes","payout_or_eligibility_note","page_fetch_status","public_detail_evidence","eligibility_evidence","required_next_step","automation_status"]
    write_csv(OUT/"earnings_opportunities.csv",candidates,columns)
    write_csv(OUT/"source_status.csv",source_report,["source","fetch_status","candidate_links_extracted"])
    tracker_cols=["candidate_url","source","task_title","status","claimed_rate","actual_time_minutes","proof_link_or_note","approval_status","amount_earned_inr","payout_received_inr","next_follow_up"]
    tracker=[{"candidate_url":r["url"],"source":r["source"],"task_title":r["title"],"status":"NEW_NOT_STARTED","claimed_rate":r["public_amount_text"],"actual_time_minutes":"","proof_link_or_note":"","approval_status":"NOT_SUBMITTED","amount_earned_inr":"","payout_received_inr":"","next_follow_up":"Verify eligibility and task terms before starting."} for r in candidates if r["triage_status"]!="QUARANTINE_RISK_REVIEW"]
    write_csv(OUT/"earnings_tracker_template.csv",tracker,tracker_cols)
    target_hits=count_verified_target_rate_rows(candidates)
    detail_pay_hits=count_detail_pages_with_public_pay(candidates)
    with (OUT/"earnings_hunt_report.md").open("w",encoding="utf-8") as f:
        f.write(f"# AutoPilot Studio — Earnings Hunter Run\n\n- Run ID: {run_id}\n- Official starting points checked: {len(SOURCES)}\n- Candidate rows emitted: {len(candidates)}\n- Specific task-detail pages with visible public pay/rate evidence: {detail_pay_hits}\n- Specific task-detail pages with public INR amount in ₹50–₹200: {target_hits}\n- Mode: {'offline test run' if offline else 'public-page discovery'}\n\n")
        f.write("## How ranking works\n\nExplicit public INR amounts in ₹50–₹200 get a boost. India relevance and task wording may add points. Foreign currency is not silently converted. Risk phrases (deposits, fake reviews/proofs, credential sharing, captcha bypass, risky APK installation) are quarantined.\n\n")
        f.write("## Important limits\n\nA platform link is a lead, not proof a specific task is open, that you are eligible, or that it will pay. This workflow only fetches public HTML pages. It does not create accounts, log in, click claim/apply, submit surveys, solve CAPTCHAs, fake proof, upload work, or initiate payouts. A provider decides eligibility, acceptance and payment. No income or first-payment guarantee. Keep identity documents, passwords, OTPs and payment details out of the tracker.\n\n## Public page scan\n\n")
        for item in source_report: f.write(f"- {item['source']}: {item['fetch_status']}; same-site task/job links extracted: {item['candidate_links_extracted']}\n")
        f.write("\n## Output files\n\n- earnings_opportunities.csv — ranked leads and source evidence.\n- source_status.csv — public page fetch status.\n- earnings_tracker_template.csv — local tracking template for actual work and payout.\n")
    print(f"source_count={len(SOURCES)}")
    print(f"candidate_rows={len(candidates)}")
    print(f"target_range_public_amount_rows={target_hits}")
    print(f"specific_task_detail_pages_with_public_pay={detail_pay_hits}")
    print(f"report={OUT/'earnings_hunt_report.md'}")
    return OUT/"earnings_opportunities.csv"

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline",action="store_true",help="Skip network access for tests")
    parser.add_argument("--limit",type=int,default=30,help="Maximum candidate rows, 1..200")
    args=parser.parse_args()
    try: run_hunt(args.offline,args.limit); return 0
    except (OSError,RuntimeError,ValueError) as exc:
        print(f"earnings_hunt_failed: {exc}",file=sys.stderr); return 1

if __name__=="__main__": raise SystemExit(main())
