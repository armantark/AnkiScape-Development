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


class FakeMainWindow(FakeQWidget):
    def __init__(self):
        super().__init__(None)

    def width(self):
        return 800

    def height(self):
        return 600

    # Minimal findChildren(type, name)
    def findChildren(self, _typ, name):
        out = []
        for c in list(self._children):
            try:
                if c.objectName() == name:
                    out.append(c)
            except Exception:
                pass
        return out


class FakeQApplication:
    top_level = []

    @classmethod
    def topLevelWidgets(cls):
        return list(cls.top_level)


class TestHUDSingletonAndCleanup(unittest.TestCase):
    def setUp(self):
        # Import target module
        import ui as _ui
        self.ui = _ui
        # Backup
        self._bak_HAS_QT = _ui.HAS_QT
        self._bak_mw = _ui.mw
        self._bak_REVIEW_HUD = getattr(_ui, "_REVIEW_HUD", None)
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
        if self._bak_ReviewHUD is not None:
            self.ui.ReviewHUD = self._bak_ReviewHUD
        # Clean fake Qt
        try:
            del sys.modules["aqt.qt"]
        except Exception:
            pass
        FakeHUD.created = 0
        FakeQApplication.top_level = []

    def test_ensure_review_hud_cleans_duplicates_and_singleton(self):
        # Call ensure twice; should create exactly one new HUD and clean duplicates
        baseline = FakeHUD.created  # accounts for the two pre-created fakes in setUp
        self.ui.ensure_review_hud()
        self.ui.ensure_review_hud()
        hud = self.ui._REVIEW_HUD
        self.assertIsNotNone(hud, "HUD should be created")
        self.assertIs(hud.parent(), self.mw, "HUD should be parented to mw")
        self.assertEqual(
            FakeHUD.created - baseline,
            1,
            "Only one new HUD instance should be created by ensure() calls",
        )
        # Duplicates should be cleaned
        self.assertTrue(self.stray_top._hidden and self.stray_top._deleted, "Stray top-level HUD should be removed")
        self.assertTrue(self.dup_child._hidden and self.dup_child._deleted, "Duplicate child HUD should be removed")
        # raise_ should have been called to keep HUD on top of its parent
        self.assertTrue(hud._raised, "HUD should be raised on ensure")


if __name__ == "__main__":
    unittest.main()
