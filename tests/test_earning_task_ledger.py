import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agents"))
import earning_task_ledger as ledger

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.data={"version":1,"tasks":[]}
        ledger.add_task(self.data,"T1","Demo label task","https://example.org/job", "INR","100","per task")
    def test_discovered_is_not_income(self):
        t=self.data["tasks"][0]
        self.assertEqual(t["stage"],"discovered")
        self.assertFalse(t["payout_confirmed_by_user"])
        self.assertEqual(t["payout_received_amount"],"")
    def test_paid_requires_confirmation(self):
        with self.assertRaises(ValueError):
            ledger.update_stage(self.data,"T1","paid")
    def test_accepted_requires_amount(self):
        with self.assertRaises(ValueError):
            ledger.update_stage(self.data,"T1","accepted")
    def test_user_confirmed_paid_stage(self):
        ledger.update_stage(self.data,"T1","paid",payout_amount="100",payout_confirmed=True)
        self.assertTrue(self.data["tasks"][0]["payout_confirmed_by_user"])
        self.assertEqual(self.data["tasks"][0]["payout_received_amount"],"100")
    def test_minutes_accumulate(self):
        ledger.update_stage(self.data,"T1","eligibility_check",minutes=5)
        ledger.update_stage(self.data,"T1","applied",minutes=7)
        self.assertEqual(self.data["tasks"][0]["minutes_spent"],12)
    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            ledger.add_task(self.data,"T1","Duplicate","https://example.org")
    def test_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"; ledger.save(path,self.data)
            loaded=ledger.load(path)
            self.assertEqual(loaded["tasks"][0]["task_id"],"T1")

if __name__ == "__main__": unittest.main()
