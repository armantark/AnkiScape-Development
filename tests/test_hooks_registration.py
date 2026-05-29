import unittest

from hooks import build_registration_plan, register_hooks


class TestHooksRegistration(unittest.TestCase):
    def test_build_plan_counts(self):
        plan = build_registration_plan(
            {
                "profile_loaded": [lambda: None, lambda: None],
                "reviewer_question": [lambda *_: None],
                "reviewer_answer": [lambda *_: None, lambda *_: None],
                "answer_wrapper": lambda self, ease, _old: _old(self, ease),
            }
        )
        self.assertEqual(plan["profileLoaded"], 2)
        self.assertEqual(plan["reviewer_did_show_question"], 1)
        self.assertEqual(plan["reviewer_did_show_answer"], 2)
        self.assertEqual(plan["wrap_reviewer_answerCard"], 1)

    def test_register_hooks_dry_run(self):
        plan = register_hooks(
            {
                "profile_loaded": [lambda: None],
                "reviewer_question": [lambda *_: None],
                "reviewer_answer": [lambda *_: None],
                "answer_wrapper": lambda self, ease, _old: _old(self, ease),
            },
            dry_run=True,
        )
        # Should return a plan and not crash in non-Anki env
        self.assertIn("profileLoaded", plan)
        self.assertIn("reviewer_did_show_question", plan)
        self.assertIn("reviewer_did_show_answer", plan)
        self.assertIn("wrap_reviewer_answerCard", plan)


if __name__ == "__main__":
    unittest.main()
