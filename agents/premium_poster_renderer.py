"""Create a crisp, editable SVG poster prototype without paid services or dependencies.

This is a layout/rendering prototype, not a finished client asset: it uses abstract
vector shapes and supplied brief text, never fabricated product photography.
"""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path

PALETTES = {
    "salon": ("#100F18", "#E8B5C5", "#FFF4F7", "#C987A2"),
    "auto parts": ("#101820", "#F4B942", "#F4F7FA", "#3C819B"),
    "retail": ("#14251E", "#D5F08A", "#F7F8EE", "#78A58A"),
    "cafe": ("#211711", "#E8B56C", "#FFF3DF", "#98634A"),
    "restaurant": ("#211711", "#E8B56C", "#FFF3DF", "#98634A"),
}

def _text(value: str) -> str:
    return html.escape(str(value), quote=True)

def build_svg(brief: dict) -> str:
    client = str(brief.get("client_name", "YOUR BRAND")).strip() or "YOUR BRAND"
    business = str(brief.get("business_type", "local service")).lower()
    palette_key = next((key for key in PALETTES if key in business), "local service")
    bg, accent, paper, secondary = PALETTES.get(palette_key, ("#111827", "#9DECF3", "#F8FAFC", "#64748B"))
    topic = str(brief.get("offer_or_topic", "A better experience")).strip() or "A better experience"
    goal = str(brief.get("goal", "Discover the difference")).strip() or "Discover the difference"
    cta = str(brief.get("call_to_action", "GET IN TOUCH")).strip() or "GET IN TOUCH"
    # Split into authored lines instead of shrinking text until it becomes unreadable.
    words = topic.split()
    lines, line = [], ""
    for word in words:
        if len(line + " " + word) > 19 and line:
            lines.append(line); line = word
        else:
            line = (line + " " + word).strip()
    if line: lines.append(line)
    lines = lines[:3] or ["A better", "experience"]
    headline = "\n".join(f'<text x="76" y="{430+i*86}" class="headline">{_text(part)}</text>' for i, part in enumerate(lines))
    safe_client = _text(client.upper())
    safe_goal = _text(goal[:90])
    safe_cta = _text(cta.upper()[:42])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350" role="img" aria-labelledby="title desc">
<title id="title">{safe_client} campaign poster concept</title><desc id="desc">Editable vector poster prototype. Replace abstract artwork with approved client imagery before delivery.</desc>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{bg}"/><stop offset="1" stop-color="#263044"/></linearGradient><radialGradient id="glow"><stop stop-color="{accent}" stop-opacity=".55"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient></defs>
<style>.brand{{font:700 27px Arial,sans-serif;letter-spacing:4px;fill:{paper}}}.eyebrow{{font:700 17px Arial,sans-serif;letter-spacing:5px;fill:{accent}}}.headline{{font:800 76px Arial,sans-serif;letter-spacing:-2px;fill:{paper}}}.body{{font:400 25px Arial,sans-serif;fill:{paper}}}.cta{{font:700 20px Arial,sans-serif;letter-spacing:3px;fill:{bg}}}.small{{font:400 16px Arial,sans-serif;letter-spacing:2px;fill:{paper};opacity:.75}}</style>
<rect width="1080" height="1350" fill="url(#bg)"/><circle cx="835" cy="330" r="390" fill="url(#glow)"/><circle cx="840" cy="330" r="235" fill="none" stroke="{accent}" stroke-width="2" opacity=".8"/><circle cx="840" cy="330" r="185" fill="none" stroke="{paper}" stroke-width="1" opacity=".35"/><path d="M620 120 L1010 510 M720 90 L1035 405 M610 220 L950 560" stroke="{accent}" stroke-width="2" opacity=".45"/>
<text x="76" y="95" class="brand">{safe_client}</text><text x="76" y="250" class="eyebrow">MADE FOR YOUR NEXT MOVE</text>{headline}
<text x="78" y="{470+len(lines)*86}" class="body">{safe_goal}</text><rect x="76" y="1030" width="360" height="74" rx="3" fill="{accent}"/><text x="104" y="1076" class="cta">{safe_cta}</text><path d="M76 1155 H1004" stroke="{paper}" stroke-width="1" opacity=".35"/><text x="76" y="1205" class="small">CAMPAIGN CONCEPT / VECTOR PREVIEW</text><text x="76" y="1240" class="small">Replace abstract artwork with approved brand assets.</text><text x="1004" y="1290" text-anchor="end" class="small">1080 × 1350</text></svg>'''

def render_poster(brief: dict, output: str | Path) -> dict:
    svg = build_svg(brief)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return {"status": "PROTOTYPE_RENDERED", "format": "SVG", "width": 1080, "height": 1350,
            "editable_vector_text": True, "uses_approved_client_photography": False,
            "client_delivery_ready": False, "output": str(path), "quality_checks": {
                "has_viewbox": 'viewBox="0 0 1080 1350"' in svg,
                "has_accessible_title": "<title" in svg,
                "has_cta": "class=\"cta\"" in svg,
                "explicitly_marks_concept": "VECTOR PREVIEW" in svg,
            }}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
    result = render_poster(brief, args.output)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if all(result["quality_checks"].values()) else 1

if __name__ == "__main__":
    raise SystemExit(main())
