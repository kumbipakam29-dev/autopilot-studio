import unittest

from app import APPROVAL_TERMS, _draft


class DraftTaskTests(unittest.TestCase):
    def test_caption_task_returns_draft(self):
        result = _draft("caption", "a local cafe weekend special")
        self.assertIn("local cafe weekend special", result)
        self.assertIn("#SmallBusiness", result)

    def test_reel_task_has_requested_timing(self):
        result = _draft("reel_script", "home cleaning service")
        self.assertIn("14–20 second Reel concept", result)
        self.assertIn("0–3s", result)
        self.assertIn("15–20s", result)

    def test_calendar_states_not_published(self):
        result = _draft("content_calendar", "a bakery")
        self.assertIn("Day 7", result)
        self.assertIn("not published", result)

    def test_unknown_task_is_not_executed(self):
        self.assertIsNone(_draft("shell", "run a command"))

    def test_sensitive_actions_are_flagged(self):
        self.assertRegex("please publish this", APPROVAL_TERMS)
        self.assertRegex("send message to customer", APPROVAL_TERMS)
        self.assertRegex("delete the repository", APPROVAL_TERMS)

    def test_normal_draft_request_is_not_sensitive(self):
        self.assertIsNone(APPROVAL_TERMS.search("write a caption for a bakery"))


if __name__ == "__main__":
    unittest.main()
