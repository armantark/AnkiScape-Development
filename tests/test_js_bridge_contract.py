import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.injectors import build_reviewer_js, build_overview_js, build_deck_browser_js


class TestJsBridgeContract(unittest.TestCase):
    def test_injected_web_surfaces_can_open_the_menu(self):
        icon = "data:image/png;base64,xxx"
        surfaces = {
            "overview": build_overview_js("right", icon),
            "deck_browser": build_deck_browser_js(True, "right", icon),
        }
        for surface, js in surfaces.items():
            with self.subTest(surface):
                self.assertIn("ankiscape_open_menu", js)

    def test_reviewer_web_surface_only_removes_the_legacy_button(self):
        js = build_reviewer_js("left", "data:image/png;base64,xxx")
        self.assertNotIn("ankiscape_open_menu", js)
        self.assertIn("removeChild(el)", js)


if __name__ == "__main__":
    unittest.main()
