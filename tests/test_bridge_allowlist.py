import unittest

from injectors import should_force_pass_through

class TestBridgeAllowlist(unittest.TestCase):
    def test_allows_nav_and_study_messages(self):
        allowed = [
            "open:decks",
            "open:add",
            "decks",
            "add",
            "browse",
            "stats",
            "sync",
            "Study",
            "study",
            "review",
            "start",
            "studyNow",
            "review-now",
            "start-review",
        ]
        for msg in allowed:
            self.assertTrue(should_force_pass_through(msg), msg)

    def test_rejects_unrelated_messages(self):
        blocked = [
            None,
            123,
            "ankiscape_open_menu",
            "ankiscape_log:hello",
            "hello world",
        ]
        for msg in blocked:
            self.assertFalse(should_force_pass_through(msg), str(msg))

if __name__ == "__main__":
    unittest.main()
