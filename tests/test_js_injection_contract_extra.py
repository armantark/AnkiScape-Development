import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.injectors import (
    build_reviewer_js,
    build_overview_js,
    build_deck_browser_js,
)
from tests.js_dom.fixture import DomTestCase, ICON


class TestJSInjectionContractExtra(DomTestCase):
    def test_reviewer_removes_the_old_floating_menu_button(self):
        self.load_body('<div id="ankiscape-float"><a id="ankiscape-btn"><img></a></div>')
        self.js(build_reviewer_js("hud-right", ICON))
        self.assertEqual(self.js("document.querySelectorAll('#ankiscape-float, #ankiscape-btn, img').length"), 0)
        self.assertEqual(self.js("commands"), [])

    def test_overview_pointer_events_and_hover(self):
        self.assert_pointer_and_hover(build_overview_js("left", ICON))

    def test_deck_browser_pointer_events_present(self):
        self.assert_pointer_and_hover(build_deck_browser_js(True, "right", ICON))

    def test_reviewer_position_no_longer_changes_the_removal_contract(self):
        self.assertEqual(build_reviewer_js("hud-right", ICON), build_reviewer_js("bogus", ICON))
        for position in ("hud-right", "bogus"):
            with self.subTest(position=position):
                self.load_body('<main id="card">Answer</main><div id="ankiscape-float"></div>')
                self.js(build_reviewer_js(position, ICON))
                self.assertEqual(self.js("document.querySelectorAll('#ankiscape-float').length"), 0)
                self.js(build_reviewer_js(position, ICON))
                self.assertEqual(self.js("document.getElementById('card').textContent"), "Answer")
                self.assertEqual(self.js("commands"), [])

    def test_deck_browser_inserts_at_each_supported_anchor(self):
        anchors = (
            '<nav><a>Get Shared</a><button id="last">Import</button><span id="tail"></span></nav>',
            '<nav><a>Decks</a><button id="last">Sync</button><span id="tail"></span></nav>',
            '<nav class="links"><span id="last"></span></nav>',
            '<nav id="links"><span id="last"></span></nav>',
        )
        for body in anchors:
            with self.subTest(body=body):
                self.load_body(body)
                js = build_deck_browser_js(True, "left", ICON)
                self.js(js)
                self.js(js)
                self.assertEqual(self.js("document.getElementById('last').nextElementSibling.id"), "ankiscape-btn")
                self.assertEqual(self.js("document.querySelectorAll('#ankiscape-float').length"), 0)
                self.assert_menu_click()

    def test_deck_browser_without_an_anchor_respects_disabled_floating(self):
        self.js(build_deck_browser_js(False, "right", ICON))
        self.assertEqual(self.js("document.querySelectorAll('#ankiscape-float, #ankiscape-btn').length"), 0)
        self.assertEqual(self.js("commands"), [])
        self.js(build_deck_browser_js(True, "right", ICON))
        self.assertEqual(self.js("document.querySelectorAll('#ankiscape-float').length"), 1)
        self.assert_menu_click()


if __name__ == "__main__":
    unittest.main()
