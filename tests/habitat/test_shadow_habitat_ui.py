"""The ordinary Shop service at laptop height in light and Fusion dark."""

import copy
import unittest

import pkg_alias  # noqa: F401
from tests.main_menu import fixtures as _main_menu
from tests import test_main_menu_widget as _main_menu_helpers
from tests.habitat.fixtures import CollectionFacade
from tests.test_storage_runtime import _load_storage_module
from tests.habitat.fixtures import setup_state, established_state, TARGET

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QColor, QPalette, Qt, QWidget

SERVICE = "papa_mambo_build_abandoned_house"


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ShadowHabitatServiceFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.old_palette = QApplication.palette()
        self.old_style = QApplication.style().objectName()
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self):
        self.menu.tearDown()
        QApplication.setStyle(self.old_style)
        QApplication.setPalette(self.old_palette)

    def _assert_service_flow(self, dark):
        QApplication.setStyle("Fusion")
        palette = QApplication.style().standardPalette()
        if dark:
            for role, color in (
                (QPalette.ColorRole.Window, "#282828"),
                (QPalette.ColorRole.Base, "#181818"),
                (QPalette.ColorRole.AlternateBase, "#303030"),
                (QPalette.ColorRole.Button, "#303030"),
                (QPalette.ColorRole.Text, "#eeeeee"),
                (QPalette.ColorRole.WindowText, "#eeeeee"),
                (QPalette.ColorRole.ButtonText, "#eeeeee"),
                (QPalette.ColorRole.Mid, "#080808"),
                (QPalette.ColorRole.Highlight, "#2a82da"),
                (QPalette.ColorRole.HighlightedText, "#ffffff"),
            ):
                palette.setColor(role, QColor(color))
        QApplication.setPalette(palette)
        collection = CollectionFacade()
        storage = _load_storage_module(collection)
        data = {"inventory": {"Coins": 57000}, "construction_level": 1, "habitat_feature": "boneyard"}
        saves = []

        def save():
            storage.save_player_data(data, "Hunter")
            saves.append(copy.deepcopy(data))

        dialog = self.menu._open(data, on_save_player_data=save)
        _main_menu_helpers._open_shop_tab(dialog)
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(4):
            QApplication.processEvents()
        search = _main_menu_helpers._find_named_line_edit(dialog, "shopSearchInput")
        search.setText("Abandoned house")
        QApplication.processEvents()
        selector = _main_menu_helpers._find_named_list(dialog, "shopSelectionList")
        row = next(selector.item(i) for i in range(selector.count()) if (selector.item(i).data(Qt.ItemDataRole.UserRole) or {}).get("id") == SERVICE)
        self.assertIn("Build Abandoned house", row.text())
        selector.setCurrentItem(row)
        for _ in range(4):
            QApplication.processEvents()
        preview = _main_menu_helpers._find_named_label(dialog, "shopServicePreviewLabel")
        use = _main_menu_helpers._find_named_button(dialog, "shopServiceUseButton")
        panel = dialog.findChild(QWidget, "shopServicesPanel")
        self.assertTrue(panel.isVisibleTo(dialog))
        self.assertTrue(use.isEnabled())
        self.assertIn("57,000 Coins", preview.text())
        self.assertIsNone(data.get("shop_events"))
        self.assertEqual(data["habitat_feature"], "boneyard")
        # Inspect live geometry only after show/resize/event processing.
        self.assertEqual(dialog.height(), 560)
        self.assertGreater(preview.width(), 0)
        self.assertGreaterEqual(preview.height(), preview.heightForWidth(preview.width()))
        self.assertGreater(use.height(), 0)
        self.assertFalse(use.geometry().intersects(preview.geometry()))
        use.click()
        QApplication.processEvents()
        self.assertEqual(data["inventory"]["Coins"], 0)
        self.assertEqual(data["habitat_feature"], "abandoned_house")
        self.assertEqual(len(data["shop_events"]), 1)
        self.assertEqual(len(saves), 1)
        loaded, skill = storage.load_player_data()
        self.assertEqual(skill, "Hunter")
        self.assertEqual(loaded["inventory"]["Coins"], 0)
        self.assertEqual(loaded["habitat_feature"], "abandoned_house")
        self.assertIn("already built", preview.text())
        self.assertFalse(use.isEnabled())
        before = copy.deepcopy(data)
        # A stale signal still runs the real purchase callback and must deny.
        use.clicked.emit()
        QApplication.processEvents()
        self.assertEqual(data, before)
        self.assertEqual(len(saves), 1)

    def test_light_search_preview_purchase_persistence_and_duplicate_denial(self):
        self._assert_service_flow(False)

    def test_fusion_dark_search_preview_purchase_persistence_and_duplicate_denial(self):
        self._assert_service_flow(True)

    def _assert_selection_flow(self, data, enabled):
        data["current_hunter"] = "catch_common_jadinko"
        before = copy.deepcopy(data)
        dialog = self.menu._open(data)
        tree = _main_menu_helpers._goto_hunter(dialog)
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(4):
            QApplication.processEvents()
        for key in ("farm_patches", "inventory", "habitat_feature", "farming_exp"):
            self.assertEqual(data.get(key), before.get(key))
        before = copy.deepcopy(data)
        row = _main_menu_helpers._hunter_row(tree, TARGET)
        self.assertEqual(row.isDisabled(), not enabled)
        calls = list(self.menu._hunter_calls)
        tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        expected = calls + [TARGET] if enabled else calls
        self.assertEqual(self.menu._hunter_calls, expected)
        if enabled:
            before["current_hunter"] = TARGET
        self.assertEqual(data, before)
        self.assertEqual(dialog.height(), 560)
        return row

    def test_resource_blocked_shadow_row_cannot_change_selection(self):
        data = setup_state()
        data["inventory"]["Red blossom seed"] = 0
        row = self._assert_selection_flow(data, False)
        self.assertIn("missing seeds or compost", row.toolTip(0))

    def test_executable_shadow_setup_selects_without_mutation(self):
        self._assert_selection_flow(setup_state(), True)

    def test_ready_shadow_setup_enables_normal_selection(self):
        data = established_state()
        data["inventory"]["Red blossom seed"] = 0
        data["farming_level"] = 1
        data["construction_level"] = 1
        self._assert_selection_flow(data, True)
