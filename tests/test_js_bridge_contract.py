import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.injectors import build_reviewer_js, build_overview_js, build_deck_browser_js
from tests.js_dom.fixture import DomTestCase, ICON


class TestJsBridgeContract(DomTestCase):
    def test_injected_web_surfaces_can_open_the_menu(self):
        surfaces = {
            "overview": build_overview_js("right", ICON),
            "deck_browser": build_deck_browser_js(True, "right", ICON),
        }
        for surface, js in surfaces.items():
            with self.subTest(surface):
                self.load_body("")
                self.js(js)
                self.js(js)
                self.assert_menu_click()
                self.assertEqual(self.js("document.querySelector('#ankiscape-btn img').src"), ICON)

    def test_reviewer_web_surface_only_removes_the_legacy_button(self):
        self.load_body('<main id="card">Question</main><div id="ankiscape-float"><a id="ankiscape-btn"></a></div>')
        js = build_reviewer_js("left", ICON)
        self.js(js)
        self.js(js)
        self.assertIsNone(self.js("document.getElementById('ankiscape-float')"))
        self.assertEqual(self.js("document.querySelectorAll('#ankiscape-btn').length"), 0)
        self.assertEqual(self.js("document.getElementById('card').outerHTML"), '<main id="card">Question</main>')
        self.assertEqual(self.js("commands"), [])


if __name__ == "__main__":
    unittest.main()
