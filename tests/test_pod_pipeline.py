import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agents" / "pod_pipeline.py"
SPEC = importlib.util.spec_from_file_location("pod_pipeline", SCRIPT)
pod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(pod)

SAMPLE_JS = r'''
export const POD_CONCEPTS = [
  {id:"POD-001",niche:"Chai culture",market:"India",product:"Mug",audience:"Tea drinkers",title:"Chai Time — Mug",keywords:"chai lover mug, tea gift, Indian chai",concept:"Cup with steam.",prompt:"Original tea cup art, no brand."},
  {id:"POD-002",niche:"Book lovers",market:"Global",product:"T-shirt",audience:"Readers",title:"One More Chapter",keywords:"book lover shirt, reading gift",concept:"Book and moon.",prompt:"Original book artwork."}
];
'''

class PodPipelineTests(unittest.TestCase):
    def test_parse_concepts(self):
        concepts = pod.parse_concepts(SAMPLE_JS)
        self.assertEqual(len(concepts), 2)
        self.assertEqual(concepts[0]["id"], "POD-001")
        self.assertEqual(concepts[0]["niche"], "Chai culture")

    def test_listing_drafts_require_review(self):
        drafts = pod.build_listing_drafts(pod.parse_concepts(SAMPLE_JS))
        self.assertEqual(len(drafts), 2)
        self.assertEqual(drafts[0]["publication_status"], "HUMAN_REVIEW_REQUIRED")
        self.assertLessEqual(int(drafts[0]["tag_count"]), 13)

    def test_trend_match_does_not_claim_sales(self):
        trends = [{"term": "chai tea", "approx_traffic": "1K+", "published_at": "", "source_url": "fixture"}]
        rows = pod.match_trends(trends, pod.parse_concepts(SAMPLE_JS))
        self.assertEqual(len(rows), 1)
        self.assertIn("POSSIBLE", rows[0]["relevance"])
        self.assertIn("not sales intent", rows[0]["risk_note"])

    def test_ip_term_is_excluded_from_automatic_match(self):
        trends = [{"term": "Disney", "approx_traffic": "", "published_at": "", "source_url": "fixture"}]
        rows = pod.match_trends(trends, pod.parse_concepts(SAMPLE_JS))
        self.assertEqual(rows[0]["relevance"], "EXCLUDE_IP_OR_BRAND_RISK")
        self.assertEqual(rows[0]["matched_concept_ids"], "")

    def test_rss_parser(self):
        xml = """<?xml version="1.0"?>
        <rss xmlns:ht="https://trends.google.com/trending/rss"><channel>
          <item><title>chai tea</title><pubDate>Sat, 24 Oct 2026 00:00:00 GMT</pubDate>
            <ht:approx_traffic>2K+</ht:approx_traffic></item>
        </channel></rss>"""
        rows = pod.parse_trends_xml(xml, "https://example.test/rss")
        self.assertEqual(rows[0]["term"], "chai tea")
        self.assertEqual(rows[0]["approx_traffic"], "2K+")

if __name__ == "__main__":
    unittest.main()
