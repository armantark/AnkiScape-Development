import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.injectors import build_reviewer_js, build_overview_js, build_deck_browser_js


class TestJsBridgeContract(unittest.TestCase):
    def test_every_injected_surface_can_open_the_menu(self):
        icon = "data:image/png;base64,xxx"
        surfaces = {
            "reviewer": build_reviewer_js("left", icon),
            "overview": build_overview_js("right", icon),
            "deck_browser": build_deck_browser_js(True, "right", icon),
        }
        for surface, js in surfaces.items():
            with self.subTest(surface):
                self.assertIn("ankiscape_open_menu", js)


if __name__ == "__main__":
    unittest.main()
