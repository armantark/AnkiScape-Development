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

    def test_reviewer_hud_right_offsets_button_beside_the_bar(self):
        # The hud-right branch places the button right of the centered HUD,
        # vertically level with it.
        self.assertIn("translateX(270px)", build_reviewer_js("hud-right", ICON))
        self.assertIn("wrap.style.bottom = '72px'", build_reviewer_js("hud-right", ICON))
        # __POS__ must have resolved to hud-right (the runtime comparisons use it).
        self.assertIn("('hud-right' === 'left')", build_reviewer_js("hud-right", ICON))

    def test_reviewer_unknown_position_falls_back_to_hud_right(self):
        # An unrecognized/stale config value must resolve to the new default,
        # not a screen corner.
        self.assertIn("('hud-right' === 'left')", build_reviewer_js("bogus", ICON))
        # A still-valid corner value is left untouched.
        self.assertIn("('right' === 'left')", build_reviewer_js("right", ICON))

if __name__ == "__main__":
    unittest.main()
