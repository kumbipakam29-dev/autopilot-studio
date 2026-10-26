#!/usr/bin/env python3
"""Small dependency-free preflight checks for the static business website."""
from html.parser import HTMLParser
from pathlib import Path
import sys

SITE = Path("website/index.html")

class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.hrefs = []
        self.errors = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a":
            href = attrs.get("href", "")
            self.hrefs.append(href)
            self.links.append((href, attrs.get("aria-label", "")))

def main():
    if not SITE.is_file():
        print(f"ERROR: missing {SITE}")
        return 1
    html = SITE.read_text(encoding="utf-8")
    parser = Checker()
    parser.feed(html)
    parser.close()
    errors = []
    if "<!doctype html>" not in html.lower():
        errors.append("missing HTML5 doctype")
    if '<html lang="' not in html.lower():
        errors.append("html lang attribute is required")
    if "<title>" not in html.lower() or "</title>" not in html.lower():
        errors.append("page title is required")
    if 'href="mailto:"' in html or "href='mailto:'" in html:
        errors.append("empty mailto link: configure a real business email before publishing")
    for href, _ in parser.links:
        if not href.strip():
            errors.append("empty anchor href found")
        elif href.startswith("#") and href != "#" and href[1:] not in parser.ids:
            errors.append(f"anchor target does not exist: {href}")
    for placeholder in ("YOUR_EMAIL", "YOUR_PHONE", "REPLACE_ME", "example.com"):
        if placeholder.lower() in html.lower():
            errors.append(f"placeholder remains in website: {placeholder}")
    if errors:
        print("Website QA FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Website QA passed: {SITE}, {len(parser.links)} links checked.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
