import sys
import types
import unittest


class FakeQWidget:
    def __init__(self, parent=None):
        self._parent = parent
        self._children = []
        if parent is not None and hasattr(parent, "_children"):
            parent._children.append(self)
        self._hidden = False
        self._deleted = False
        self._raised = False
        self._properties = {}

    # Qt-like API surface used in ui.py
    def setParent(self, p):
        if self._parent is not None and hasattr(self._parent, "_children") and self in self._parent._children:
            self._parent._children.remove(self)
        self._parent = p
        if p is not None and hasattr(p, "_children"):
            p._children.append(self)

    def parent(self):
        return self._parent

    def objectName(self):
        return getattr(self, "_object_name", "")

    def hide(self):
        self._hidden = True

    def setVisible(self, visible):
        self._hidden = not visible

    def setProperty(self, name, value):
        self._properties[name] = value

    def deleteLater(self):
        self._deleted = True

    def raise_(self):
        self._raised = True


class FakeHUD(FakeQWidget):
    created = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._object_name = "AnkiScapeReviewHUD"
        FakeHUD.created += 1


class FakeStrip(FakeQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._object_name = "AnkiScapeReviewStrip"
        self.sync_calls = 0

    def sync_children(self):
        self.sync_calls += 1


class FakeMainWindow(FakeQWidget):
    def __init__(self):
        super().__init__(None)
        self.find_children_calls = 0

    def width(self):
        return 800

    def height(self):
        return 600

    # Minimal findChildren(type, optional name)
    def findChildren(self, _typ, name=None):
        self.find_children_calls += 1
        out = []
        for c in list(self._children):
            try:
                if name is None or c.objectName() == name:
                    out.append(c)
            except Exception:
                pass
        return out


class FakeQApplication:
    top_level = []
    top_level_calls = 0

    @classmethod
    def topLevelWidgets(cls):
        cls.top_level_calls += 1
        return list(cls.top_level)


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
class TestHUDSingletonAndCleanup(unittest.TestCase):
    def setUp(self):
        # Import target module
        from ankiscape.ui import ui as _ui
        self.ui = _ui
        # Backup
        self._bak_HAS_QT = _ui.HAS_QT
        self._bak_mw = _ui.mw
        self._bak_REVIEW_HUD = getattr(_ui, "_REVIEW_HUD", None)
        self._bak_REVIEW_STRIP = getattr(_ui, "_REVIEW_STRIP", None)
        self._bak_DND_BADGE = getattr(_ui, "_DND_BADGE", None)
        self._bak_FARMING_BADGE = getattr(_ui, "_FARMING_BADGE", None)
        self._bak_SHOOTING_STAR_NOTICE_BAND = getattr(
            _ui,
            "_SHOOTING_STAR_NOTICE_BAND",
            None,
        )
        self._bak_BANK_RUN_BUTTON = getattr(_ui, "_BANK_RUN_BUTTON", None)
        self._bak_MAIN_MENU_BUTTON = getattr(_ui, "_MAIN_MENU_BUTTON", None)
        self._bak_REVIEW_CONTEXT_STRIP = getattr(_ui, "_REVIEW_CONTEXT_STRIP", None)
        self._bak_FILL_DRAWER = getattr(_ui, "_FILL_DRAWER", None)
        self._bak_EVENT_LOG_DRAWER = getattr(_ui, "_EVENT_LOG_DRAWER", None)
        self._bak_cleanup_done = getattr(_ui, "_REVIEW_WIDGET_CLEANUP_DONE", False)
        self._bak_ReviewHUD = getattr(_ui, "ReviewHUD", None)
        # Install fake Qt into sys.modules where ui._cleanup_extra_huds imports from
        self.fake_qt = types.ModuleType("aqt.qt")
        self.fake_qt.QApplication = FakeQApplication
        self.fake_qt.QWidget = FakeQWidget
        sys.modules["aqt.qt"] = self.fake_qt
        # Prepare mw and fakes
        self.mw = FakeMainWindow()
        _ui.mw = self.mw
        _ui.HAS_QT = True
        _ui._REVIEW_HUD = None
        _ui._REVIEW_STRIP = FakeStrip(self.mw)
        _ui._DND_BADGE = FakeQWidget(_ui._REVIEW_STRIP)
        _ui._FARMING_BADGE = FakeQWidget(_ui._REVIEW_STRIP)
        _ui._SHOOTING_STAR_NOTICE_BAND = FakeQWidget(_ui._REVIEW_STRIP)
        _ui._BANK_RUN_BUTTON = FakeQWidget(_ui._REVIEW_STRIP)
        _ui._MAIN_MENU_BUTTON = FakeQWidget(_ui._REVIEW_STRIP)
        _ui._REVIEW_CONTEXT_STRIP = FakeQWidget(self.mw)
        _ui._FILL_DRAWER = FakeQWidget(self.mw)
        _ui._EVENT_LOG_DRAWER = FakeQWidget(self.mw)
        _ui._REVIEW_WIDGET_CLEANUP_DONE = False
        _ui.ReviewHUD = FakeHUD  # ensure construction doesn't require real Qt
        # Prepare stray top-level HUD and duplicate child HUD
        self.stray_top = FakeHUD(None)
        FakeQApplication.top_level = [self.stray_top]
        self.dup_child = FakeHUD(self.mw)

    def tearDown(self):
        # Restore
        self.ui.HAS_QT = self._bak_HAS_QT
        self.ui.mw = self._bak_mw
        self.ui._REVIEW_HUD = self._bak_REVIEW_HUD
        self.ui._REVIEW_STRIP = self._bak_REVIEW_STRIP
        self.ui._DND_BADGE = self._bak_DND_BADGE
        self.ui._FARMING_BADGE = self._bak_FARMING_BADGE
        self.ui._SHOOTING_STAR_NOTICE_BAND = self._bak_SHOOTING_STAR_NOTICE_BAND
        self.ui._BANK_RUN_BUTTON = self._bak_BANK_RUN_BUTTON
        self.ui._MAIN_MENU_BUTTON = self._bak_MAIN_MENU_BUTTON
        self.ui._REVIEW_CONTEXT_STRIP = self._bak_REVIEW_CONTEXT_STRIP
        self.ui._FILL_DRAWER = self._bak_FILL_DRAWER
        self.ui._EVENT_LOG_DRAWER = self._bak_EVENT_LOG_DRAWER
        self.ui._REVIEW_WIDGET_CLEANUP_DONE = self._bak_cleanup_done
        if self._bak_ReviewHUD is not None:
            self.ui.ReviewHUD = self._bak_ReviewHUD
        # Clean fake Qt
        try:
            del sys.modules["aqt.qt"]
        except Exception:
            pass
        FakeHUD.created = 0
        FakeQApplication.top_level = []
        FakeQApplication.top_level_calls = 0

    def test_ensure_review_hud_cleans_duplicates_and_singleton(self):
        # Call ensure twice; should create exactly one new HUD and clean duplicates
        baseline = FakeHUD.created  # accounts for the two pre-created fakes in setUp
        self.ui.ensure_review_hud()
        self.ui.ensure_review_hud()
        hud = self.ui._REVIEW_HUD
        self.assertIsNotNone(hud, "HUD should be created")
        self.assertIs(
            hud.parent(),
            self.ui._REVIEW_STRIP,
            "HUD should be parented to the fixed strip",
        )
        self.assertIs(self.ui._REVIEW_STRIP.parent(), self.mw)
        self.assertEqual(
            FakeHUD.created - baseline,
            1,
            "Only one new HUD instance should be created by ensure() calls",
        )
        # Duplicates should be cleaned
        self.assertTrue(self.stray_top._hidden and self.stray_top._deleted, "Stray top-level HUD should be removed")
        self.assertTrue(self.dup_child._hidden and self.dup_child._deleted, "Duplicate child HUD should be removed")
        self.assertEqual(
            self.ui._REVIEW_STRIP.sync_calls,
            2,
            "Each ensure should verify the strip's stable child order",
        )

    def test_surface_refreshes_do_not_rescan_the_qt_tree(self):
        original_sync = self.ui._sync_review_drawer_stacking
        self.ui._sync_review_drawer_stacking = lambda _drawer: None
        self.addCleanup(
            setattr,
            self.ui,
            "_sync_review_drawer_stacking",
            original_sync,
        )
        self.ui.ensure_review_hud()

        for _event in ("show answer", "next card"):
            self.mw.find_children_calls = 0
            FakeQApplication.top_level_calls = 0
            self.ui.ensure_review_hud()
            self.ui.ensure_review_hud()
            self.ui.ensure_review_context_action_strip()
            self.ui.ensure_review_context_action_strip()
            self.ui.ensure_review_status_badge()
            self.ui.ensure_review_status_badge()
            self.ui.ensure_review_fill_drawer()
            self.ui.ensure_review_event_log_drawer()
            self.ui.ensure_review_strip()
            traversals = (
                self.mw.find_children_calls + FakeQApplication.top_level_calls
            )
            self.assertLessEqual(traversals, 2)


if __name__ == "__main__":
    unittest.main()
