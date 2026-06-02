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
    from aqt.qt import QApplication, QDialog, QLabel, QListWidget, QPushButton, QToolButton, QDoubleSpinBox, Qt
    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


def _make_player_data() -> dict:
    data: dict = {"inventory": {}}
    for skill in ("mining", "woodcutting", "smithing", "crafting"):
        data[f"{skill}_level"] = 33
        data[f"{skill}_exp"] = 1000.0
    # Real saves are seeded with a bound starter tool per gathering skill; without
    # it every tree/rock would lock on "no usable hatchet/pickaxe" and those rows
    # couldn't be exercised. Mirror that seed so Woodcutting and Mining rows unlock.
    data["toolbelt"] = {"woodcutting": ["bronze_hatchet"], "mining": ["bronze_pickaxe"]}
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
            on_set_utility=lambda *a: None,
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
            "Logs": 5,
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

    # ---- Crafting/Utility rework surfaces ---------------------------------
    def _open_utility(self, dialog: "QDialog") -> "QListWidget":
        cat = next(
            b for b in dialog.findChildren(QPushButton) if b.text() == "Utility / Activities"
        )
        cat.click()
        QApplication.processEvents()
        return _find_list_with_item_prefix(dialog, "Make soft clay")

    def test_soft_clay_left_crafting_and_is_now_a_utility_activity(self) -> None:
        # Open Crafting target list and assert Soft clay is no longer a target.
        artisan = next(b for b in self.dialog.findChildren(QPushButton) if b.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(self.dialog)
        craft_row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Crafting")
        skill_list.setCurrentRow(craft_row)
        QApplication.processEvents()
        craft_list = _find_list_with_item_prefix(self.dialog, "Pot ")
        craft_texts = [craft_list.item(i).text() for i in range(craft_list.count())]
        self.assertFalse(
            any(t.startswith("Soft clay") for t in craft_texts),
            f"Soft clay should not be a Crafting target anymore: {craft_texts}",
        )
        # And it now lives under Utility / Activities.
        utility_list = self._open_utility(self.dialog)
        util_texts = [utility_list.item(i).text() for i in range(utility_list.count())]
        self.assertIn("Make soft clay", util_texts)
        self.assertIn("Gather wool", util_texts)

    def test_utility_panel_uses_no_xp_language(self) -> None:
        self._open_utility(self.dialog)
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertTrue(
            any("no XP" in t for t in labels),
            f"Utility panel should state it earns no XP; labels={labels}",
        )

    def test_hud_shows_utility_activity_without_xp(self) -> None:
        hud = self._ui.ReviewHUD(None)
        pd = _make_player_data()
        pd["current_utility"] = "gather_flax"
        hud.set_data(pd, "Utility / Activities")
        self.assertEqual(hud.title_lbl.text(), "Utility / Activities")
        self.assertIn("no XP", hud.sub_lbl.text())

    def test_scraped_sprites_are_pretrimmed_on_disk(self) -> None:
        # Sprites are trimmed to their opaque box at build time (tools/trim_icons.py)
        # so the UI can use a plain QIcon(path) with no runtime cropping. Verify the
        # asset itself is tight: a padded 64x64 sprite would defeat that contract.
        import os as _os
        from aqt.qt import QImage
        flax = _os.path.join(self._ui.current_dir, "crafteditems", "flax.png")
        if not _os.path.exists(flax):
            self.skipTest("flax sprite not present")
        img = QImage(flax)
        self.assertFalse(img.isNull())
        self.assertLess(max(img.width(), img.height()), 64,
                        "flax sprite is not pre-trimmed; run tools/trim_icons.py")

    def test_settings_expose_xp_multiplier_under_gameplay(self) -> None:
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn("Gameplay", labels)
        self.assertIn("XP multiplier:", labels)
        spins = self.dialog.findChildren(QDoubleSpinBox)
        self.assertTrue(spins, "no XP multiplier spin box found")
        self.assertGreaterEqual(spins[0].maximum(), 1.0)

    # ---- Woodcutting 2011Scape parity frontend ----------------------------
    def _open_woodcutting(self, dialog: "QDialog") -> "QListWidget":
        skill_list = _find_skill_list(dialog)
        wc_row = next(
            i for i in range(skill_list.count()) if skill_list.item(i).text() == "Woodcutting"
        )
        skill_list.setCurrentRow(wc_row)
        QApplication.processEvents()
        return _find_list_with_item_prefix(dialog, "Oak ")

    def _wc_row(self, tree_list: "QListWidget", prefix: str) -> "QListWidgetItem":
        return next(
            tree_list.item(i) for i in range(tree_list.count())
            if tree_list.item(i).text().startswith(prefix)
        )

    def test_woodcutting_list_shows_friendly_names_not_stable_ids(self) -> None:
        tree_list = self._open_woodcutting(self.dialog)
        texts = [tree_list.item(i).text() for i in range(tree_list.count())]
        # Friendly display names, not raw IDs like "oak"/"tree".
        self.assertTrue(any(t.startswith("Oak (Lvl 15)") for t in texts), texts)
        self.assertTrue(any(t.startswith("Tree (Lvl 1)") for t in texts), texts)
        self.assertFalse(any(t == "oak" or t == "tree" for t in texts), texts)

    def test_woodcutting_ivy_marked_xp_only_no_logs(self) -> None:
        tree_list = self._open_woodcutting(self.dialog)
        ivy = self._wc_row(tree_list, "Ivy ")
        self.assertIn("XP only", ivy.text())
        self.assertIn("produces no logs", ivy.toolTip())

    def test_woodcutting_tooltip_shows_output_and_best_hatchet(self) -> None:
        tree_list = self._open_woodcutting(self.dialog)
        oak = self._wc_row(tree_list, "Oak ")
        tip = oak.toolTip()
        self.assertIn("Oak logs", tip)
        self.assertIn("Bronze hatchet", tip)  # seeded toolbelt is the best usable

    def test_woodcutting_high_level_tree_locked_with_level_reason(self) -> None:
        tree_list = self._open_woodcutting(self.dialog)
        magic = self._wc_row(tree_list, "Magic ")  # level 75, player is 33
        self.assertFalse(
            bool(magic.flags() & Qt.ItemFlag.ItemIsEnabled),
            "Magic should be locked at level 33",
        )
        self.assertIn("level 75", magic.toolTip())

    def test_woodcutting_locks_all_trees_when_no_usable_hatchet(self) -> None:
        pd = _make_player_data()
        pd["toolbelt"] = {"woodcutting": []}  # no bound tool, no hatchet item
        dialog = self._open(pd)
        tree_list = self._open_woodcutting(dialog)
        tree = self._wc_row(tree_list, "Tree ")
        self.assertFalse(
            bool(tree.flags() & Qt.ItemFlag.ItemIsEnabled),
            "Tree should lock without a usable hatchet",
        )
        self.assertIn("no usable hatchet", tree.toolTip())

    # ---- Mining 2011Scape parity frontend ---------------------------------
    def _open_mining(self, dialog: "QDialog") -> "QListWidget":
        skill_list = _find_skill_list(dialog)
        mining_row = next(
            i for i in range(skill_list.count()) if skill_list.item(i).text() == "Mining"
        )
        skill_list.setCurrentRow(mining_row)
        QApplication.processEvents()
        # Copper is a stable, always-present low-level rock row.
        return _find_list_with_item_prefix(dialog, "Copper ")

    def _ore_row(self, ore_list: "QListWidget", prefix: str) -> "QListWidgetItem":
        return next(
            ore_list.item(i) for i in range(ore_list.count())
            if ore_list.item(i).text().startswith(prefix)
        )

    def test_mining_list_shows_friendly_names_not_stable_ids(self) -> None:
        ore_list = self._open_mining(self.dialog)
        texts = [ore_list.item(i).text() for i in range(ore_list.count())]
        # Friendly display names, not raw IDs like "rune_essence"/"coal".
        self.assertTrue(any(t.startswith("Copper (Lvl 1)") for t in texts), texts)
        self.assertTrue(any(t.startswith("Coal (Lvl 30)") for t in texts), texts)
        self.assertFalse(any(t in ("rune_essence", "coal", "copper") for t in texts), texts)

    def test_mining_tooltip_shows_output_and_best_pickaxe(self) -> None:
        ore_list = self._open_mining(self.dialog)
        copper = self._ore_row(ore_list, "Copper ")
        tip = copper.toolTip()
        self.assertIn("Copper ore", tip)
        self.assertIn("Bronze pickaxe", tip)  # seeded toolbelt is the best usable

    def test_mining_essence_row_labels_pure_essence_upgrade(self) -> None:
        ore_list = self._open_mining(self.dialog)
        essence = self._ore_row(ore_list, "Rune essence ")
        self.assertIn("Pure essence", essence.text())
        self.assertIn("Pure essence", essence.toolTip())

    def test_mining_variable_output_rocks_are_labeled(self) -> None:
        ore_list = self._open_mining(self.dialog)
        for name, sample in (
            ("Sandstone ", "Sandstone (1kg)"),
            ("Granite ", "Granite (500g)"),
            ("Gem rocks ", "Uncut opal"),
        ):
            row = self._ore_row(ore_list, name)
            self.assertIn("variable output", row.text(), f"{name!r} not labelled variable")
            self.assertIn(sample, row.toolTip(), f"{name!r} tooltip missing {sample!r}")

    def test_mining_high_level_rock_locked_with_level_reason(self) -> None:
        ore_list = self._open_mining(self.dialog)
        runite = self._ore_row(ore_list, "Runite ")  # level 85, player is 33
        self.assertFalse(
            bool(runite.flags() & Qt.ItemFlag.ItemIsEnabled),
            "Runite should be locked at level 33",
        )
        self.assertIn("level 85", runite.toolTip())

    def test_mining_locks_all_rocks_when_no_usable_pickaxe(self) -> None:
        pd = _make_player_data()
        pd["toolbelt"] = {"mining": []}  # no bound tool, no pickaxe item
        dialog = self._open(pd)
        ore_list = self._open_mining(dialog)
        copper = self._ore_row(ore_list, "Copper ")
        self.assertFalse(
            bool(copper.flags() & Qt.ItemFlag.ItemIsEnabled),
            "Copper should lock without a usable pickaxe",
        )
        self.assertIn("no usable pickaxe", copper.toolTip())

    def test_mining_rows_render_icons_including_variable_rocks(self) -> None:
        # Icons were fetched by tools/fetch_mining_assets.py. Ordinary rocks use
        # their output_item art; variable rocks fall back to the first weighted
        # output (Gem rocks -> Uncut opal, sourced from GEM_IMAGES).
        ore_list = self._open_mining(self.dialog)
        for prefix in ("Copper ", "Blurite ", "Sandstone ", "Granite ", "Gem rocks "):
            row = self._ore_row(ore_list, prefix)
            self.assertFalse(row.icon().isNull(), f"{prefix!r} row has no icon")

    def test_mining_coal_tooltip_mentions_concentrated_deferral(self) -> None:
        ore_list = self._open_mining(self.dialog)
        coal = self._ore_row(ore_list, "Coal ")
        self.assertIn("Concentrated coal", coal.toolTip())
        self.assertIn("deferred", coal.toolTip())

    def test_open_bird_nests_is_a_visible_no_xp_utility_activity(self) -> None:
        utility_list = self._open_utility(self.dialog)
        texts = [utility_list.item(i).text() for i in range(utility_list.count())]
        self.assertIn("Open bird nests", texts)
        nest = next(
            utility_list.item(i) for i in range(utility_list.count())
            if utility_list.item(i).text() == "Open bird nests"
        )
        self.assertIn("No XP", nest.toolTip())
        self.assertIn("bird nest", nest.toolTip().lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
