"""Offscreen Qt behavior tests for the Skills-hub navigation in ``show_main_menu``.

Why this exists: iterating on the menu by restarting Anki is slow and blind.
This harness builds the *real* dialog headlessly (QT_QPA_PLATFORM=offscreen)
against a pip-installed ``aqt`` and drives the widgets directly, so a broken
"click skill -> panel updates" contract fails here in milliseconds instead of
being discovered by hand after a restart.

Run with the Qt venv:
    source .venv-qt/bin/activate
    QT_QPA_PLATFORM=offscreen python tests/test_main_menu_widget.py
"""
from __future__ import annotations

import os
import re
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ADDON_DIR = os.path.dirname(_THIS_DIR)
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

try:
    import aqt  # noqa: F401
    from aqt.qt import QApplication, QDialog, QLabel, QListWidget, QPushButton, QToolButton, Qt
    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


def _make_player_data() -> dict:
    data: dict = {"inventory": {}}
    for skill in ("mining", "woodcutting", "smithing", "crafting"):
        data[f"{skill}_level"] = 33
        data[f"{skill}_exp"] = 1000.0
    return data


def _panel_title(dialog: "QDialog") -> str:
    """Return the text of the Skills-hub panel header, if present.

    The header is the QLabel styled bold/large that reads e.g. "Woodcutting — Lv 33".
    """
    pattern = re.compile(r"^(Mining|Woodcutting|Smithing|Crafting|Fletching)(\s+—\s+Lv\s+\d+)?$")
    for lbl in dialog.findChildren(QLabel):
        text = lbl.text()
        if pattern.match(text):
            return text
    return ""


def _find_skill_list(dialog: "QDialog") -> "QListWidget":
    """Return the QListWidget that holds the skill rows (not target/bank lists).

    Skill rows are plain display names; target rows contain "(Lvl N)" markers.
    """
    for lw in dialog.findChildren(QListWidget):
        texts = [lw.item(i).text() for i in range(lw.count())]
        if "Mining" in texts and "Woodcutting" in texts:
            return lw
    raise AssertionError("skill list widget not found")


def _find_artisan_skill_list(dialog: "QDialog") -> "QListWidget":
    for lw in dialog.findChildren(QListWidget):
        texts = [lw.item(i).text() for i in range(lw.count())]
        if "Smithing" in texts and "Crafting" in texts:
            return lw
    raise AssertionError("artisan skill list widget not found")


def _find_list_with_item_prefix(dialog: "QDialog", prefix: str) -> "QListWidget":
    for lw in dialog.findChildren(QListWidget):
        if any(lw.item(i).text().startswith(prefix) for i in range(lw.count())):
            return lw
    raise AssertionError(f"no list widget with an item starting {prefix!r}")


def _find_tool_button(dialog: "QDialog", text: str) -> "QToolButton":
    for btn in dialog.findChildren(QToolButton):
        if btn.text() == text:
            return btn
    raise AssertionError(f"no tool button labeled {text!r}")


def _find_bank_list(dialog: "QDialog") -> "QListWidget":
    """The bank list is the one whose rows carry category headers."""
    for lw in dialog.findChildren(QListWidget):
        for i in range(lw.count()):
            if lw.item(i).data(Qt.ItemDataRole.UserRole) == "__header__":
                return lw
    raise AssertionError("bank list (with category headers) not found")


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(unittest.TestCase):
    app: "QApplication"
    dialog: "QDialog"

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        import ui

        self._captured: list = []

        # Stop exec() from blocking; capture the live dialog so we can drive it.
        def _fake_exec(self_dialog):  # type: ignore[no-untyped-def]
            self._captured.append(self_dialog)
            return 0

        self._orig_exec = QDialog.exec
        QDialog.exec = _fake_exec  # type: ignore[assignment,method-assign]

        # Developer mode on so the registry surfaces every category/skill.
        self._orig_cfg = ui.get_config_bool
        ui.get_config_bool = lambda key, default=True: (
            True if key == "ankiscape_developer_mode" else default
        )

        self._ui = ui
        self.dialog = self._open(_make_player_data(), current_skill="Mining")

    def _open(self, player_data: dict, current_skill: str = "Mining") -> "QDialog":
        self._ui.show_main_menu(
            player_data=player_data,
            current_skill=current_skill,
            can_smelt_any_bar=True,
            on_save_skill=lambda *a: None,
            on_set_ore=lambda *a: None,
            on_set_tree=lambda *a: None,
            on_set_bar=lambda *a: None,
            on_set_craft=lambda *a: None,
            on_set_fletch=lambda *a: None,
        )
        self.assertTrue(self._captured, "show_main_menu did not call dialog.exec()")
        return self._captured[-1]

    def tearDown(self) -> None:
        QDialog.exec = self._orig_exec  # type: ignore[assignment,method-assign]
        self._ui.get_config_bool = self._orig_cfg
        self.dialog.deleteLater()

    def test_initial_panel_shows_a_gathering_skill(self) -> None:
        title = _panel_title(self.dialog)
        self.assertTrue(title.startswith("Mining"), f"unexpected initial panel: {title!r}")

    def test_selecting_woodcutting_updates_panel(self) -> None:
        skill_list = _find_skill_list(self.dialog)
        wc_row = next(
            i for i in range(skill_list.count())
            if skill_list.item(i).text() == "Woodcutting"
        )
        skill_list.setCurrentRow(wc_row)
        QApplication.processEvents()
        title = _panel_title(self.dialog)
        self.assertTrue(
            title.startswith("Woodcutting"),
            f"panel did not switch to Woodcutting; still shows {title!r}",
        )

    def test_switching_category_then_selecting_crafting_updates_panel(self) -> None:
        # The user reported the same stale-panel bug under Artisan -> Crafting,
        # so exercise the cross-category path too, not just the first category.
        artisan = next(
            b for b in self.dialog.findChildren(QPushButton) if b.text() == "Artisan"
        )
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(self.dialog)
        craft_row = next(
            i for i in range(skill_list.count())
            if skill_list.item(i).text() == "Crafting"
        )
        skill_list.setCurrentRow(craft_row)
        QApplication.processEvents()
        title = _panel_title(self.dialog)
        self.assertTrue(
            title.startswith("Crafting"),
            f"panel did not switch to Crafting; still shows {title!r}",
        )

    def test_fletching_is_selectable_and_shows_its_target_list(self) -> None:
        # Fletching's frontend handoff: it must appear under Artisan, switch the
        # panel, and render its fletch targets (e.g. Arrow shafts).
        artisan = next(
            b for b in self.dialog.findChildren(QPushButton) if b.text() == "Artisan"
        )
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(self.dialog)
        fletch_row = next(
            (i for i in range(skill_list.count()) if skill_list.item(i).text() == "Fletching"),
            None,
        )
        self.assertIsNotNone(fletch_row, "Fletching is missing from the Artisan skill list")
        skill_list.setCurrentRow(fletch_row)
        QApplication.processEvents()
        title = _panel_title(self.dialog)
        self.assertTrue(
            title.startswith("Fletching"),
            f"panel did not switch to Fletching; still shows {title!r}",
        )
        target_list = _find_list_with_item_prefix(self.dialog, "Arrow shafts")
        self.assertIsNotNone(target_list)

    # ---- Stats / Bank / HUD registry-driven surfaces ----------------------
    def test_stats_tab_has_fletching_and_shows_its_details(self) -> None:
        btn = _find_tool_button(self.dialog, "Fletching")
        btn.click()
        QApplication.processEvents()
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn("Fletching Stats", labels)
        self.assertIn("Fletching Level:", labels)

    def test_bank_groups_fletched_and_material_items_with_icons(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Tree": 5,
            "Bronze bar": 2,
            "Arrow shafts": 30,
            "Feather": 50,
            "Bronze arrowtips": 15,
        }
        dialog = self._open(pd)
        bank = _find_bank_list(dialog)
        texts = [bank.item(i).text() for i in range(bank.count())]
        for header in ("Logs", "Bars", "Fletched", "Materials"):
            self.assertIn(header, texts, f"missing bank category header {header!r}")
        self.assertTrue(any(t.startswith("Arrow shafts x30") for t in texts))
        self.assertTrue(any(t.startswith("Feather x50") for t in texts))
        # Registered fletched item should carry an icon from its ItemDefinition.
        arrow_row = next(
            bank.item(i) for i in range(bank.count())
            if bank.item(i).text().startswith("Arrow shafts x")
        )
        self.assertFalse(arrow_row.icon().isNull(), "Arrow shafts row has no icon")

    def test_hud_recognizes_fletching_as_active_skill(self) -> None:
        hud = self._ui.ReviewHUD(None)
        hud.set_data(_make_player_data(), "Fletching")
        self.assertTrue(
            hud.title_lbl.text().startswith("Fletching"),
            f"HUD did not recognize Fletching; shows {hud.title_lbl.text()!r}",
        )
        self.assertFalse(hud.icon_lbl.pixmap().isNull(), "HUD has no Fletching icon")


if __name__ == "__main__":
    unittest.main(verbosity=2)
