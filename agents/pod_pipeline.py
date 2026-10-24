#!/usr/bin/env python3
"""Zero-cost, review-first POD pipeline. Standard-library only; never publishes listings."""
from __future__ import annotations
import argparse, csv, datetime as dt, json, re, sys, urllib.error, urllib.parse, urllib.request, xml.etree.ElementTree as ET, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "src" / "podData.js"
OUTPUT_DIR = ROOT / "output"
CONCEPT_RE = re.compile(r'\{id:"POD-\d{3}".*?\}', re.DOTALL)
FIELD_RE = re.compile(r'(\w+):"((?:\\.|[^"\\])*)"')
IP_TERMS = (
    r"\bdisney\b", r"\bmarvel\b", r"\bpokemon\b", r"\bpok[eé]mon\b",
    r"\bnintendo\b", r"\bstar wars\b", r"\bharry potter\b", r"\bbarbie\b",
    r"\bhello kitty\b", r"\bsanrio\b", r"\btaylor swift\b", r"\bnike\b",
    r"\badidas\b", r"\bnasa\b", r"\blego\b", r"\bminecraft\b",
    r"\bfortnite\b", r"\bnfl\b", r"\bnba\b",
)
IP_RE = re.compile("|".join(IP_TERMS), re.IGNORECASE)
STOP_WORDS = {"the", "and", "for", "with", "from", "this", "that", "your", "into", "are", "was", "were", "you", "our", "their", "have", "has", "its", "not", "all", "more", "one", "new", "how", "what", "when", "where", "why", "who", "will", "today", "live", "latest", "news", "2026"}

def parse_concepts(source: str) -> list[dict[str, str]]:
    """Parse the app concept library without duplicating the catalogue."""
    concepts = []
    for block in CONCEPT_RE.findall(source):
        concept = {}
        for key, raw_value in FIELD_RE.findall(block):
            try:
                concept[key] = json.loads('"' + raw_value + '"')
            except json.JSONDecodeError:
                concept[key] = raw_value
        if concept.get("id") and concept.get("title") and concept.get("prompt"):
            concepts.append(concept)
    return concepts

def fetch_trends_xml(region: str, timeout: int = 12) -> tuple[str | None, str]:
    """Fetch public Google Trends RSS; gracefully degrade if unavailable."""
    url = "https://trends.google.com/trending/rss?geo=" + urllib.parse.quote(region)
    request = urllib.request.Request(url, headers={"User-Agent": "AutoPilotStudio-PODResearch/1.0 (public RSS reader)"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read(2_000_000)
            if response.status != 200:
                return None, f"unavailable (HTTP {response.status})"
            return payload.decode("utf-8", errors="replace"), url
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, f"unavailable ({type(exc).__name__}); evergreen concepts used"
    except Exception as exc:
        return None, f"unavailable ({type(exc).__name__}); evergreen concepts used"

def parse_trends_xml(xml_text: str, source_url: str) -> list[dict[str, str]]:
    """Extract public trend labels/metadata, not full article text."""
    root = ET.fromstring(xml_text)
    rows = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        traffic = ""
        for node in item.iter():
            if node.tag.rsplit("}", 1)[-1] == "approx_traffic":
                traffic = (node.text or "").strip()
                break
        rows.append({"term": title, "approx_traffic": traffic, "published_at": (item.findtext("pubDate") or "").strip(), "source_url": source_url})
    return rows

def words(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 2 and token not in STOP_WORDS}

def match_trends(trends: list[dict[str, str]], concepts: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for trend in trends:
        term = trend["term"]
        high_risk = bool(IP_RE.search(term))
        term_words = words(term)
        matches = []
        if term_words and not high_risk:
            for concept in concepts:
                vocabulary = words(" ".join([concept.get("niche", ""), concept.get("keywords", ""), concept.get("audience", "")]))
                overlap = term_words & vocabulary
                if overlap and len(overlap) / max(1, len(term_words)) >= 0.5:
                    matches.append(concept["id"])
        if high_risk:
            relevance, note = "EXCLUDE_IP_OR_BRAND_RISK", "Potential brand/franchise/person term; do not reuse in art or listing."
        elif matches:
            relevance, note = "POSSIBLE_NICHE_OVERLAP_REVIEW", "Idea signal only; trend popularity is not sales intent or proof of demand."
        else:
            relevance, note = "NO_CONFIDENT_MATCH", "No confident match to existing niches; no automatic design change."
        rows.append({**trend, "matched_concept_ids": ";".join(matches), "relevance": relevance, "risk_note": note})
    return rows

def make_tags(keywords: str) -> list[str]:
    tags, seen = [], set()
    for part in keywords.split(","):
        tag = re.sub(r"\s+", " ", part.strip().lower())
        if tag and len(tag) <= 20 and tag not in seen:
            tags.append(tag)
            seen.add(tag)
        if len(tags) == 13:
            break
    return tags

def build_listing_drafts(concepts: list[dict[str, str]]) -> list[dict[str, str]]:
    drafts = []
    for concept in concepts:
        listing_text = " ".join([concept.get("title", ""), concept.get("keywords", "")])
        flags = []
        if IP_RE.search(listing_text):
            flags.append("POSSIBLE_BRAND_OR_IP_TERM")
        if len(concept.get("title", "")) > 140:
            flags.append("TITLE_OVER_140_CHARS")
        if not concept.get("prompt", "").strip():
            flags.append("MISSING_ART_BRIEF")
        tags = make_tags(concept.get("keywords", ""))
        description = (
            f"Concept: {concept.get('concept', '').strip()} "
            "This is a draft based on an original design brief, not a verified trend or sales claim. "
            "Check finished artwork, trademark/copyright risks, product fit, and the platform's current rules before publishing."
        )
        drafts.append({
            "concept_id": concept.get("id", ""), "niche": concept.get("niche", ""),
            "market_hypothesis": concept.get("market", ""), "product_idea": concept.get("product", ""),
            "listing_title_draft": concept.get("title", ""), "description_draft": description,
            "tags_pipe_separated": " | ".join(tags), "tag_count": str(len(tags)),
            "art_prompt_brief": concept.get("prompt", ""), "metadata_check": "PASS" if not flags else "FLAG",
            "risk_flags": ";".join(flags), "publication_status": "HUMAN_REVIEW_REQUIRED",
        })
    return drafts

def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def run_pipeline(region: str = "IN", limit: int = 25, offline: bool = False) -> Path:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Concept source not found: {SOURCE_FILE}")
    concepts = parse_concepts(SOURCE_FILE.read_text(encoding="utf-8"))
    if not concepts:
        raise RuntimeError("Could not parse POD concepts from src/podData.js")
    concepts = concepts[:max(1, min(25, limit))]
    trend_source = "offline mode; RSS not requested"
    trends = []
    if not offline:
        xml_text, trend_source = fetch_trends_xml(region.upper())
        if xml_text:
            try:
                trends = parse_trends_xml(xml_text, trend_source)
            except ET.ParseError:
                trend_source = "unavailable (invalid RSS XML); evergreen concepts used"
    trend_rows = match_trends(trends, concepts)
    drafts = build_listing_drafts(concepts)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S-UTC")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "trend_research.csv", trend_rows, ["term", "approx_traffic", "published_at", "source_url", "matched_concept_ids", "relevance", "risk_note"])
    write_csv(OUTPUT_DIR / "listing_drafts.csv", drafts, ["concept_id", "niche", "market_hypothesis", "product_idea", "listing_title_draft", "description_draft", "tags_pipe_separated", "tag_count", "art_prompt_brief", "metadata_check", "risk_flags", "publication_status"])
    review_rows = [{
        "concept_id": row["concept_id"], "listing_title_draft": row["listing_title_draft"],
        "metadata_check": row["metadata_check"], "risk_flags": row["risk_flags"],
        "artwork_visual_review": "PENDING", "trademark_and_copyright_review": "PENDING",
        "platform_policy_review": "PENDING", "approved_to_publish": "NO",
    } for row in drafts]
    write_csv(OUTPUT_DIR / "review_queue.csv", review_rows, ["concept_id", "listing_title_draft", "metadata_check", "risk_flags", "artwork_visual_review", "trademark_and_copyright_review", "platform_policy_review", "approved_to_publish"])
    matched = sum(row["relevance"] == "POSSIBLE_NICHE_OVERLAP_REVIEW" for row in trend_rows)
    excluded = sum(row["relevance"] == "EXCLUDE_IP_OR_BRAND_RISK" for row in trend_rows)
    report = f"""# AutoPilot Studio POD Agent Run

- Run ID: {run_id}
- Region requested: {region.upper()}
- Concept briefs processed: **{len(concepts)}**
- Public trend entries read: **{len(trend_rows)}**
- Possible niche overlaps requiring review: **{matched}**
- Trend terms excluded by a small brand/IP heuristic: **{excluded}**
- Trend source: {trend_source}
- Listing drafts with human approval required: **{len(drafts)}**

## What ran

1. Loaded concepts from the app's existing src/podData.js library.
2. Tried to read the public Google Trends RSS feed for the selected region (unless offline mode was selected).
3. Matched trend terms conservatively against niche/keyword vocabulary.
4. Created listing-copy/tag drafts and a separate review queue.
5. Wrote CSV outputs and a ZIP bundle for download.

## Important limits

- A trend is an attention signal, **not evidence of product demand, conversions, or likely sales**.
- Keyword overlap and brand-name matching are heuristics, not a trademark search or legal opinion.
- This stage does **not** generate AI artwork, verify image pixels/transparency/DPI, log in to a marketplace, create a listing, or publish anything.
- Every row is marked HUMAN_REVIEW_REQUIRED; the queue defaults approved_to_publish to NO.
- If the RSS source fails, the pipeline still creates evergreen draft outputs and records the failure instead of pretending live trend research succeeded.

## Files

- trend_research.csv: trend labels and match notes (empty when no trend data could be fetched).
- listing_drafts.csv: title/description/tag suggestions and each concept's existing art brief.
- review_queue.csv: explicit human-review gates.
"""
    (OUTPUT_DIR / "report.md").write_text(report, encoding="utf-8")
    bundle = OUTPUT_DIR / "pod-agent-bundle.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in ("trend_research.csv", "listing_drafts.csv", "review_queue.csv", "report.md"):
            archive.write(OUTPUT_DIR / name, arcname=name)
    print(f"concepts_processed={len(concepts)}")
    print(f"trend_entries={len(trend_rows)}")
    print(f"trend_source={trend_source}")
    print(f"outputs={OUTPUT_DIR}")
    print(f"bundle={bundle}")
    return bundle

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="IN", choices=("IN", "US", "GB"))
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--offline", action="store_true", help="Skip RSS fetch (used for tests)")
    args = parser.parse_args()
    try:
        run_pipeline(args.region, args.limit, args.offline)
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"pipeline_failed: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
