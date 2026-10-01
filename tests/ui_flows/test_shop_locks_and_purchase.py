"""Offscreen Qt coverage for the Shop tab's locked shops and purchase chip."""

import unittest
from unittest import mock

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPoint, QRect, Qt, QToolButton, QWidget
    from PyQt6.QtTest import QTest


def _shop_rows(selector) -> list[tuple[str, bool]]:
    """(label, dimmed) for each list row; only a dimmed row sets a foreground."""
    return [
        (selector.item(i).text(), selector.item(i).data(Qt.ItemDataRole.ForegroundRole) is not None)
        for i in range(selector.count())
    ]


@unittest.skipUnless(
    _main_menu.HAS_AQT,
    "aqt/PyQt6 not installed (use .venv-qt)",
)
class ShopLocksAndPurchaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        self.fixtures = build_shop_frontend_fixtures()
        self.pd = self.fixtures["fixture_player_data"]
        self.dialog = self.menu._open(self.pd)
        _main_menu._open_shop_tab(self.dialog)
        # The owner's laptop dialog height; see qt-offscreen-screenshots.md.
        self.dialog.show()
        self.dialog.resize(900, 560)
        for _ in range(4):
            QApplication.processEvents()
        self.selector = _main_menu._find_named_list(self.dialog, "shopSelectionList")

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _search(self, text: str) -> None:
        _main_menu._find_named_line_edit(self.dialog, "shopSearchInput").setText(text)
        QApplication.processEvents()

    def _click_tile(self, row_id: str) -> None:
        next(
            tile for tile in self.dialog.findChildren(QToolButton) if tile.property("shopRowId") == row_id
        ).click()
        QApplication.processEvents()

    def _select(self, predicate) -> None:
        item = next(
            self.selector.item(i)
            for i in range(self.selector.count())
            if predicate(self.selector.item(i).data(Qt.ItemDataRole.UserRole) or {})
        )
        self.selector.setCurrentItem(item)
        QApplication.processEvents()

    def test_locked_shops_dim_last_in_list_and_search_and_still_open_read_only(self) -> None:
        from ankiscape.ui.ui_tab_shop_widgets import ROW_SIDE_PADDING

        shops = [
            (label, dimmed)
            for (label, dimmed), payload in zip(
                _shop_rows(self.selector),
                (self.selector.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.selector.count())),
            )
            if payload.get("kind") == "shop"
        ]
        dimmed = [is_dimmed for _label, is_dimmed in shops]
        self.assertEqual(dimmed, sorted(dimmed), "a dimmed shop sits among open ones")
        self.assertIn(("Canifis General Store · Requires Priest in Peril", True), shops)
        # Long reasons wrap inside the list: nothing hides off the right edge,
        # and a wrapped row is laid out at its full height, not over the next.
        viewport_width = self.selector.viewport().width()
        rects = [self.selector.visualItemRect(self.selector.item(i)) for i in range(self.selector.count())]
        self.assertLessEqual(max(rect.right() for rect in rects), viewport_width)
        self.assertEqual([rect.bottom() + 1 for rect in rects[:-1]], [rect.top() for rect in rects[1:]])
        metrics = self.selector.fontMetrics()
        labels = [label for label, _dimmed in _shop_rows(self.selector)]
        longest = max(range(len(labels)), key=lambda i: metrics.horizontalAdvance(labels[i]))
        self.assertGreater(metrics.horizontalAdvance(labels[longest]), viewport_width)
        text_width = viewport_width - 2 * ROW_SIDE_PADDING - self.selector.iconSize().width()
        wrapped = metrics.boundingRect(QRect(0, 0, text_width, 10_000), Qt.TextFlag.TextWordWrap, labels[longest])
        self.assertGreaterEqual(rects[longest].height(), wrapped.height() + 10, "the longest row is elided")

        self._select(lambda payload: payload.get("shop_id") == "canifis_general_store")
        meta = _main_menu._find_named_label(self.dialog, "shopDetailMeta")
        preview = _main_menu._find_named_label(self.dialog, "shopPreviewLabel")
        self.assertIn("Requires Priest in Peril", meta.text())
        self.assertEqual(preview.text(), "Requires Priest in Peril")
        self.assertFalse(_main_menu._find_named_button(self.dialog, "shopTransactionButton").isEnabled())

        self._search("shark")
        results = _shop_rows(self.selector)
        dimmed = [is_dimmed for _label, is_dimmed in results]
        self.assertEqual(dimmed, sorted(dimmed), "a dimmed search row sits among open ones")
        etceteria = next(row for row in results if " · Etceteria Fish · " in row[0])
        self.assertIn(" · Etceteria Fish · Requires The Fremennik Trials · Stock ", etceteria[0])
        self.assertTrue(etceteria[1])

    def test_purchase_chip_shows_under_buy_at_owner_height_then_clears(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        live_view = self.fixtures["normal_coin_stock_shop"]
        live_rows = [row for row in live_view["rows"] if row["can_buy"]]
        self._select(lambda payload: payload.get("shop_id") == live_view["shop_id"])
        self._click_tile(live_rows[0]["id"])
        panel = _main_menu._find_named_widget(self.dialog, "shopTransactionPanel")
        chip = _main_menu._find_named_label(self.dialog, "shopResultChip")
        button = _main_menu._find_named_button(self.dialog, "shopTransactionButton")
        viewport = _main_menu._find_named_widget(self.dialog, "shopLowerScroll").viewport()
        self.assertIs(chip.parentWidget(), panel)
        self.assertFalse(chip.isVisible())
        # The Qty buttons already fail the helper's size-hint check while
        # their text is whole on screen; the chip must add nothing to that.
        defects_without_chip = text_fit_defects(panel)

        button.click()
        QApplication.processEvents()
        self.assertTrue(chip.isVisible())
        self.assertEqual(chip.text(), f"✓ Bought 1 x {live_rows[0]['item_name']}.")
        self.assertGreater(chip.y(), button.mapTo(panel, QPoint(0, 0)).y())
        self.assertTrue(
            viewport.rect().contains(QRect(chip.mapTo(viewport, QPoint(0, 0)), chip.size())),
            "the chip needs scrolling to see at 560 px",
        )
        self.assertEqual(text_fit_defects(panel), defects_without_chip)

        self._click_tile(live_rows[1]["id"])
        self.assertFalse(chip.isVisible(), "a stale result stayed under a different row")

        with mock.patch.object(type(chip), "HOLD_MS", 500):
            button.click()
            QApplication.processEvents()
            self.assertTrue(chip.isVisible())
            QTest.qWait(1500)
        self.assertFalse(chip.isVisible(), "the chip outstayed its hold time")

        # A review elsewhere spent the coins after the preview enabled Buy.
        self.pd["inventory"]["Coins"] = 0
        button.click()
        QApplication.processEvents()
        self.assertTrue(chip.isVisible())
        self.assertRegex(chip.text(), r"^Need \d[\d,]* Coins, you have 0\.$")
        self.assertIn("#f0c75e", chip.styleSheet())
        self.assertEqual(text_fit_defects(panel), defects_without_chip)

    def test_service_chip_confirms_a_vendor_action_beside_its_use_button(self) -> None:
        from ankiscape.data.shop_data import SHOP_VENDOR_ACTIONS

        action_id = self.fixtures["vendor_action_transaction"]["action_id"]
        self._search(SHOP_VENDOR_ACTIONS[action_id]["display_name"])
        self._select(lambda payload: payload.get("id") == action_id)
        chip = _main_menu._find_named_label(self.dialog, "shopServiceResultChip")
        use = _main_menu._find_named_button(self.dialog, "shopServiceUseButton")
        use.click()
        QApplication.processEvents()
        self.assertTrue(chip.isVisibleTo(self.dialog))
        self.assertTrue(chip.text().startswith("✓ Used "), chip.text())
        self.assertIs(chip.parentWidget(), self.dialog.findChild(QWidget, "shopServicesPanel"))


if __name__ == "__main__":
    unittest.main()
