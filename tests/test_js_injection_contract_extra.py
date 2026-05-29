import unittest

from injectors import (
    build_reviewer_js,
    build_overview_js,
    build_deck_browser_js,
)

ICON = "data:image/png;base64,TEST"

class TestJSInjectionContractExtra(unittest.TestCase):
    def test_reviewer_pointer_events_and_hover(self):
        js = build_reviewer_js("right", ICON)
        self.assertIn("wrap.style.pointerEvents = 'none'", js)
        self.assertIn("btn.style.pointerEvents = 'auto'", js)
        self.assertIn("mouseenter", js)
        self.assertIn("mouseleave", js)

    def test_overview_pointer_events_and_hover(self):
        js = build_overview_js("left", ICON)
        self.assertIn("wrap.style.pointerEvents = 'none'", js)
        self.assertIn("btn.style.pointerEvents = 'auto'", js)
        self.assertIn("mouseenter", js)
        self.assertIn("mouseleave", js)

    def test_deck_browser_pointer_events_present(self):
        js = build_deck_browser_js(True, "right", ICON)
        # Floating wrapper should not capture events
        self.assertIn("wrap.style.pointerEvents = 'none'", js)
        # The created anchor/button should handle them
        self.assertIn("a.style.pointerEvents = 'auto'", js)
        # Hover handlers exist
        self.assertIn("mouseenter", js)
        self.assertIn("mouseleave", js)

if __name__ == "__main__":
    unittest.main()
