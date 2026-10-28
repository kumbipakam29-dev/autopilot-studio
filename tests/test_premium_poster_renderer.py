import tempfile
import unittest
from pathlib import Path
from agents.premium_poster_renderer import build_svg, render_poster

class PremiumPosterRendererTests(unittest.TestCase):
    def test_generates_vertical_editable_vector_with_clear_quality_markers(self):
        brief = {"client_name": "Demo Salon", "business_type": "salon", "offer_or_topic": "Glow with confidence", "goal": "Discover a fresh look", "call_to_action": "Book a consultation"}
        svg = build_svg(brief)
        self.assertIn('width="1080" height="1350"', svg)
        self.assertIn('class="headline"', svg)
        self.assertIn("Glow with confidence", svg)
        self.assertIn("VECTOR PREVIEW", svg)
        self.assertIn("Replace abstract artwork with approved client imagery", svg)

    def test_escapes_untrusted_text_and_never_claims_client_ready(self):
        svg = build_svg({"client_name": "A & B <Shop>", "business_type": "auto parts", "offer_or_topic": "Parts < tested >", "call_to_action": "Ask & learn"})
        self.assertIn("A &amp; B &lt;SHOP&gt;", svg)
        self.assertIn("Parts &lt; tested &gt;", svg)
        with tempfile.TemporaryDirectory() as tmp:
            result = render_poster({"client_name": "Demo", "business_type": "retail", "offer_or_topic": "Fresh finds"}, Path(tmp) / "poster.svg")
            self.assertEqual(result["status"], "PROTOTYPE_RENDERED")
            self.assertFalse(result["client_delivery_ready"])
            self.assertTrue(all(result["quality_checks"].values()))

if __name__ == "__main__":
    unittest.main()
