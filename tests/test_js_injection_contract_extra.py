import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.injectors import (
    build_reviewer_js,
    build_overview_js,
    build_deck_browser_js,
)

ICON = "data:image/png;base64,TEST"

class TestJSInjectionContractExtra(unittest.TestCase):
    def test_reviewer_removes_the_old_floating_menu_button(self):
        js = build_reviewer_js("hud-right", ICON)
        self.assertIn("document.getElementById('ankiscape-float')", js)
        self.assertIn("removeChild(el)", js)
        self.assertNotIn("ankiscape-btn", js)
        self.assertNotIn(ICON, js)

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

    def test_reviewer_position_no_longer_changes_the_removal_contract(self):
        self.assertEqual(
            build_reviewer_js("hud-right", ICON),
            build_reviewer_js("bogus", ICON),
        )

if __name__ == "__main__":
    unittest.main()
