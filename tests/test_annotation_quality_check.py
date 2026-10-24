import csv, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agents"))
import annotation_quality_check as qa

class AnnotationQualityTests(unittest.TestCase):
    def row(self, rid="R1"):
        return {"record_id":rid, "text":"My invoice contains a duplicate charge.", "intent":"billing",
                "sentiment":"negative", "priority":"high", "label_rationale":"Mentions a duplicate invoice charge."}
    def write(self, folder, rows, headers=None):
        p=Path(folder)/"test.csv"; fields=headers or list(qa.REQUIRED_FIELDS)
        with p.open("w", newline="", encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
        return p
    def test_valid_csv(self):
        with tempfile.TemporaryDirectory() as t:
            r=qa.validate_csv(self.write(t,[self.row()]))
            self.assertTrue(r["valid"]); self.assertEqual(r["rows_checked"],1)
    def test_duplicate_id_fails(self):
        with tempfile.TemporaryDirectory() as t:
            r=qa.validate_csv(self.write(t,[self.row(),self.row()]))
            self.assertFalse(r["valid"]); self.assertIn("Duplicate record_id", " ".join(e["message"] for e in r["errors"]))
    def test_invalid_label_fails(self):
        row=self.row(); row["intent"]="refund-ish"
        with tempfile.TemporaryDirectory() as t:
            r=qa.validate_csv(self.write(t,[row]))
            self.assertFalse(r["valid"]); self.assertTrue(any(e["field"]=="intent" for e in r["errors"]))
    def test_blank_text_fails(self):
        row=self.row(); row["text"]=""
        with tempfile.TemporaryDirectory() as t:
            r=qa.validate_csv(self.write(t,[row]))
            self.assertFalse(r["valid"]); self.assertTrue(any(e["field"]=="text" for e in r["errors"]))
    def test_missing_columns_fails(self):
        with tempfile.TemporaryDirectory() as t:
            r=qa.validate_csv(self.write(t,[],headers=["record_id","text"]))
            self.assertFalse(r["valid"]); self.assertEqual(r["errors"][0]["field"],"header")

if __name__=="__main__": unittest.main()
