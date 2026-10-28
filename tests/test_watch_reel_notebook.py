"""Static safeguards for the experimental AI watch-reel notebook.

These tests validate notebook structure and cost/quality gates only. They do not
claim that the AI model ran or that any generated video is visually acceptable.
"""
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "WATCH_PREMIUM_REEL_RENDER.ipynb"


class WatchReelNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        cls.cells = cls.notebook.get("cells", [])
        cls.code = [
            "".join(cell.get("source", []))
            for cell in cls.cells
            if cell.get("cell_type") == "code"
        ]
        cls.markdown = "\n".join(
            "".join(cell.get("source", []))
            for cell in cls.cells
            if cell.get("cell_type") == "markdown"
        )

    def test_notebook_is_valid_v4_with_code(self):
        self.assertEqual(self.notebook.get("nbformat"), 4)
        self.assertGreaterEqual(len(self.code), 3)

    def test_gpu_gate_fails_closed_without_paid_fallback(self):
        setup = self.code[0]
        self.assertIn("nvidia-smi", setup)
        self.assertIn("torch.cuda.is_available()", setup)
        self.assertIn("do not pay", setup.lower())
        self.assertIn("raise RuntimeError", setup)

    def test_four_distinct_motion_shots_are_configured(self):
        generation = self.code[1]
        for marker in ("01_macro", "02_exploded", "03_wrist", "04_hero"):
            self.assertIn(marker, generation)
        self.assertIn("for name,prompt in shots", generation)
        self.assertIn("--frame_num", generation)
        self.assertIn("Negative prompt", generation)

    def test_output_is_built_from_generated_video_not_stills(self):
        assembly = self.code[2]
        self.assertIn("ffmpeg", assembly)
        self.assertIn("concat", assembly)
        self.assertIn("files.download(final)", assembly)
        self.assertNotIn("ImageSequenceClip", assembly)

    def test_human_quality_gate_prevents_automatic_success_claim(self):
        self.assertIn("Do not call the reel successful", self.markdown)
        self.assertIn("visual review", self.markdown.lower())
        self.assertIn("flicker", self.markdown.lower())
        self.assertIn("motion prototype", self.markdown.lower())


if __name__ == "__main__":
    unittest.main()
