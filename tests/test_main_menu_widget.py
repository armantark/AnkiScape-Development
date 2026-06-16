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
    from aqt.qt import QApplication, QDialog, QLabel, QListWidget, QPushButton, QToolButton, QSpinBox, Qt, QTreeWidget, QTreeWidgetItem, QWidget
    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


def _make_player_data() -> dict:
    data: dict = {"inventory": {}}
    for skill in ("mining", "woodcutting", "smithing", "crafting", "fletching", "firemaking"):
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
    pattern = re.compile(r"^(Mining|Woodcutting|Smithing|Crafting|Fletching|Firemaking)(\s+—\s+Lv\s+\d+)?$")
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


def _find_list_with_user_role(dialog: "QDialog", role) -> "QListWidget":
    for lw in dialog.findChildren(QListWidget):
        if any(lw.item(i).data(Qt.ItemDataRole.UserRole) == role for i in range(lw.count())):
            return lw
    raise AssertionError(f"no list widget with user role {role!r}")


def _find_tool_button(dialog: "QDialog", text: str) -> "QToolButton":
    for btn in dialog.findChildren(QToolButton):
        if btn.text() == text:
            return btn
    raise AssertionError(f"no tool button labeled {text!r}")


def _goto_smithing(dialog: "QDialog") -> None:
    """Open Artisan -> Smithing so the unified smith list is rendered."""
    artisan = next(b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan")
    artisan.click()
    QApplication.processEvents()
    skill_list = _find_artisan_skill_list(dialog)
    row = next(
        i for i in range(skill_list.count()) if skill_list.item(i).text() == "Smithing"
    )
    skill_list.setCurrentRow(row)
    QApplication.processEvents()


def _smith_tree_items(tree: "QTreeWidget") -> "list[QTreeWidgetItem]":
    """All items in the Smithing tree (tier parents + recipe children), flattened."""
    items: "list[QTreeWidgetItem]" = []

    def _walk(item: "QTreeWidgetItem") -> None:
        items.append(item)
        for i in range(item.childCount()):
            _walk(item.child(i))

    for i in range(tree.topLevelItemCount()):
        _walk(tree.topLevelItem(i))
    return items


def _find_smith_tree(dialog: "QDialog") -> "QTreeWidget":
    """The Smithing target tree, identified by its stable smelt-bronze recipe id."""
    for tw in dialog.findChildren(QTreeWidget):
        if any(it.data(0, Qt.ItemDataRole.UserRole) == "smelt_bronze_bar" for it in _smith_tree_items(tw)):
            return tw
    raise AssertionError("smith tree (with recipe ids) not found")


def _smith_row(tree: "QTreeWidget", recipe_id: str) -> "QTreeWidgetItem":
    for it in _smith_tree_items(tree):
        if it.data(0, Qt.ItemDataRole.UserRole) == recipe_id:
            return it
    raise AssertionError(f"smith row {recipe_id!r} not found")


def _smith_tier_node(tree: "QTreeWidget", tier: str) -> "QTreeWidgetItem":
    role = f"__tier__:{tier}"
    for i in range(tree.topLevelItemCount()):
        if tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole) == role:
            return tree.topLevelItem(i)
    raise AssertionError(f"smith tier node {tier!r} not found")


def _tree_items(tree: "QTreeWidget") -> "list[QTreeWidgetItem]":
    """All items in a grouped tree (family/tier parents + recipe children)."""
    items: "list[QTreeWidgetItem]" = []

    def _walk(item: "QTreeWidgetItem") -> None:
        items.append(item)
        for i in range(item.childCount()):
            _walk(item.child(i))

    for i in range(tree.topLevelItemCount()):
        _walk(tree.topLevelItem(i))
    return items


def _find_craft_tree(dialog: "QDialog") -> "QTreeWidget":
    """The Crafting target tree, identified by a stable Crafting recipe id."""
    for tw in dialog.findChildren(QTreeWidget):
        if any(it.data(0, Qt.ItemDataRole.UserRole) == "cut_emerald" for it in _tree_items(tw)):
            return tw
    raise AssertionError("craft tree (with recipe ids) not found")


def _craft_row(tree: "QTreeWidget", recipe_id: str) -> "QTreeWidgetItem":
    for it in _tree_items(tree):
        if it.data(0, Qt.ItemDataRole.UserRole) == recipe_id:
            return it
    raise AssertionError(f"craft row {recipe_id!r} not found")


def _craft_family_node(tree: "QTreeWidget", family: str) -> "QTreeWidgetItem":
    role = f"__family__:{family}"
    for i in range(tree.topLevelItemCount()):
        if tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole) == role:
            return tree.topLevelItem(i)
    raise AssertionError(f"craft family node {family!r} not found")


def _goto_crafting(dialog: "QDialog") -> "QTreeWidget":
    """Open Artisan -> Crafting and return the family-grouped recipe tree."""
    artisan = next(b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan")
    artisan.click()
    QApplication.processEvents()
    skill_list = _find_artisan_skill_list(dialog)
    row = next(
        i for i in range(skill_list.count()) if skill_list.item(i).text() == "Crafting"
    )
    skill_list.setCurrentRow(row)
    QApplication.processEvents()
    return _find_craft_tree(dialog)


def _find_bank_list(dialog: "QDialog") -> "QListWidget":
    """The bank list is the one whose rows carry category headers."""
    for lw in dialog.findChildren(QListWidget):
        for i in range(lw.count()):
            if lw.item(i).data(Qt.ItemDataRole.UserRole) == "__header__":
                return lw
    raise AssertionError("bank list (with category headers) not found")


def _find_gear_list(dialog: "QDialog") -> "QListWidget":
    """The gear panel is the separate (non-striped) list below the inventory."""
    for lw in dialog.findChildren(QListWidget):
        for i in range(lw.count()):
            if lw.item(i).data(Qt.ItemDataRole.UserRole) == "__gear_header__":
                return lw
    raise AssertionError("gear list (toolbelt/equipped) not found")


def _find_equipment_list(dialog: "QDialog") -> "QListWidget":
    """The Equipment tab's worn-slot list, identified by its objectName."""
    for lw in dialog.findChildren(QListWidget):
        if lw.objectName() == "equipmentList":
            return lw
    raise AssertionError("equipment list (worn slots) not found")


def _equip_slot_row(equip_list: "QListWidget", slot_id: str) -> "QListWidgetItem":
    for i in range(equip_list.count()):
        if equip_list.item(i).data(Qt.ItemDataRole.UserRole) == slot_id:
            return equip_list.item(i)
    raise AssertionError(f"equipment slot row {slot_id!r} not found")


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
        # Records recipe IDs the Smithing list persists via on_set_smith so tests
        # can assert selection wiring without real mouse events.
        self._smith_calls: list = []
        # Same seam for the family-grouped Crafting tree (on_set_craft).
        self._craft_calls: list = []
        # Same seam for Utility/Activities selection.
        self._utility_calls: list = []
        # Same seam for Firemaking target selection.
        self._firemaking_calls: list = []

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
            on_set_smith=lambda rid: self._smith_calls.append(rid),
            on_set_craft=lambda rid: self._craft_calls.append(rid),
            on_set_fletch=lambda *a: None,
            on_set_firemaking=lambda target: self._firemaking_calls.append(target),
            on_set_utility=lambda activity: self._utility_calls.append(activity),
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

    def test_firemaking_is_selectable_and_shows_source_backed_target_list(self) -> None:
        pd = _make_player_data()
        pd["firemaking_level"] = 45
        pd["inventory"] = {"Logs": 2, "Oak logs": 1}
        pd["current_firemaking"] = "oak_logs"
        dialog = self._open(pd)
        artisan = next(
            b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan"
        )
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        fm_row = next(
            (i for i in range(skill_list.count()) if skill_list.item(i).text() == "Firemaking"),
            None,
        )
        self.assertIsNotNone(fm_row, "Firemaking is missing from the Artisan skill list")
        skill_list.setCurrentRow(fm_row)
        QApplication.processEvents()

        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Firemaking"),
            f"panel did not switch to Firemaking; still shows {title!r}",
        )
        target_list = _find_list_with_user_role(dialog, "logs")
        logs_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "logs"
        )
        oak_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "oak_logs"
        )
        self.assertEqual(target_list.currentItem().data(Qt.ItemDataRole.UserRole), "oak_logs")
        self.assertIn("Base XP: 40.0", logs_row.toolTip())
        self.assertIn("Input: Logs x1 (you have 2)", logs_row.toolTip())
        self.assertIn("Output: Ashes x1", logs_row.toolTip())
        self.assertIn("Success chance:", logs_row.toolTip())
        self.assertNotIn("FiremakingData.kt", logs_row.toolTip())

        target_list.itemClicked.emit(logs_row)
        QApplication.processEvents()
        self.assertEqual(self._firemaking_calls[-1], "logs")
        self.assertTrue(oak_row.flags() & Qt.ItemFlag.ItemIsEnabled)

    def test_firemaking_locked_or_missing_material_rows_are_inert(self) -> None:
        pd = _make_player_data()
        pd["firemaking_level"] = 1
        pd["inventory"] = {"Logs": 1}
        dialog = self._open(pd)
        artisan = next(
            b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan"
        )
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        fm_row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Firemaking")
        skill_list.setCurrentRow(fm_row)
        QApplication.processEvents()
        target_list = _find_list_with_user_role(dialog, "oak_logs")
        oak_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "oak_logs"
        )

        self.assertFalse(oak_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("Locked due to:", oak_row.toolTip())
        target_list.itemClicked.emit(oak_row)
        QApplication.processEvents()
        self.assertEqual(self._firemaking_calls, [])

    # ---- Smithing parity (unified SMITHING_DATA recipe tree) --------------
    def test_smithing_groups_recipes_by_metal_tier(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Tin ore": 5, "Copper ore": 5, "Bronze bar": 5}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        tier_labels = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__tier__:Bronze", tier_labels)
        self.assertIn("__tier__:Rune", tier_labels)
        # A metal group unifies its smelt bar with the forge items made from it:
        # the Bronze node parents both smelt_bronze_bar and a bronze forge recipe.
        bronze = _smith_tier_node(tree, "Bronze")
        child_ids = {bronze.child(i).data(0, Qt.ItemDataRole.UserRole) for i in range(bronze.childCount())}
        self.assertIn("smelt_bronze_bar", child_ids)
        self.assertIn("forge_bronze_dagger", child_ids)

    def test_smithing_children_sorted_by_level_within_a_metal(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Rune bar": 20}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        rune = _smith_tier_node(tree, "Rune")
        levels = [
            int(re.search(r"\(Lvl (\d+)\)", rune.child(i).text(0)).group(1))
            for i in range(rune.childCount())
        ]
        self.assertEqual(levels, sorted(levels), f"Rune group not level-ordered: {levels}")
        # Sanity: the smelt bar (Lvl 85) leads its level tie ahead of forge rows.
        self.assertEqual(rune.child(0).data(0, Qt.ItemDataRole.UserRole), "smelt_rune_bar")

    def test_smithing_groups_collapsed_by_default_except_current_target(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze bar": 10}
        pd["current_smith"] = "forge_bronze_dagger"  # Bronze tier
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        # The group holding the current target is expanded so the selection shows.
        self.assertTrue(_smith_tier_node(tree, "Bronze").isExpanded())
        # Every other metal group starts collapsed to tame the ~166-row panel.
        self.assertFalse(_smith_tier_node(tree, "Rune").isExpanded())
        self.assertFalse(_smith_tier_node(tree, "Adamant").isExpanded())

    def test_smithing_rows_carry_stable_recipe_ids_not_display_names(self) -> None:
        pd = _make_player_data()
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        roles = [it.data(0, Qt.ItemDataRole.UserRole) for it in _smith_tree_items(tree)]
        self.assertIn("smelt_bronze_bar", roles)
        self.assertIn("forge_rune_platebody", roles)
        # Recipe children store the stable id, never the human display name.
        self.assertNotIn("Bronze bar", roles)
        self.assertNotIn("Rune platebody", roles)

    def test_smithing_locks_rows_for_level_and_for_missing_materials(self) -> None:
        pd = _make_player_data()  # smithing_level 33, empty inventory
        pd["inventory"] = {}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        # Rune platebody (Lvl 99) is above level -> locked with a level reason.
        rune = _smith_row(tree, "forge_rune_platebody")
        self.assertTrue(rune.isDisabled())
        self.assertIn("level 99", rune.toolTip(0))
        # Bronze bar is in-level but there are no ores -> locked with materials.
        bronze = _smith_row(tree, "smelt_bronze_bar")
        self.assertTrue(bronze.isDisabled())
        self.assertIn("materials", bronze.toolTip(0))
        # No hammer/tool gate is ever surfaced (toolbelt is gathering-only).
        self.assertNotIn("hammer", bronze.toolTip(0).lower())

    def test_smithing_tooltip_shows_output_xp_owned_counts_and_no_source(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Iron bar": 1}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        # Iron pickaxe needs 2 Iron bars; the tooltip should reflect output + owned.
        pick = _smith_row(tree, "forge_iron_pickaxe")
        tip = pick.toolTip(0)
        self.assertIn("Output: Iron pickaxe x1", tip)
        self.assertIn("Base XP:", tip)
        self.assertIn("Iron bar x2 (you have 1)", tip)
        # The dev-facing source enum/path was removed from player tooltips.
        self.assertNotIn("Source", tip)
        # Owning only 1 of 2 required bars keeps it locked on materials.
        self.assertTrue(pick.isDisabled())

    def test_smithing_unlocks_with_materials_and_persists_recipe_id(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze bar": 10}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        dagger = _smith_row(tree, "forge_bronze_dagger")
        self.assertFalse(dagger.isDisabled())
        tree.itemClicked.emit(dagger, 0)
        QApplication.processEvents()
        self.assertEqual(self._smith_calls[-1], "forge_bronze_dagger")

    def test_smithing_clicking_a_tier_node_does_not_persist_a_target(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze bar": 10}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        before = list(self._smith_calls)
        tree.itemClicked.emit(_smith_tier_node(tree, "Rune"), 0)
        QApplication.processEvents()
        self.assertEqual(self._smith_calls, before, "tier headers must not set a target")

    def test_smithing_highlights_current_target_on_open(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze bar": 10}
        pd["current_smith"] = "forge_bronze_dagger"
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        current = tree.currentItem()
        self.assertIsNotNone(current)
        self.assertEqual(current.data(0, Qt.ItemDataRole.UserRole), "forge_bronze_dagger")

    def test_smithing_collapse_state_persists_across_reopen(self) -> None:
        # Collapse state is a UI pref persisted in Anki config. mw is None in the
        # headless harness, so inject a tiny dict-backed config to prove the
        # expand -> persist -> reopen-expanded loop actually round-trips.
        import ui

        class _FakeCol:
            def __init__(self) -> None:
                self._cfg: dict = {}

            def get_config(self, key, default=None):
                return self._cfg.get(key, default)

            def set_config(self, key, value):
                self._cfg[key] = value

        # Subclass QWidget so show_main_menu can still parent its QDialog to mw.
        class _FakeMw(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.col = _FakeCol()

        orig_mw = ui.mw
        ui.mw = _FakeMw()
        try:
            pd = _make_player_data()
            pd["inventory"] = {"Bronze bar": 10}
            dialog = self._open(pd)
            _goto_smithing(dialog)
            tree = _find_smith_tree(dialog)
            rune = _smith_tier_node(tree, "Rune")
            self.assertFalse(rune.isExpanded())
            rune.setExpanded(True)  # emits itemExpanded -> persists "Rune"
            QApplication.processEvents()
            self.assertIn("Rune", ui.smith_expanded_tiers())

            # Reopen: the Rune group should now come up expanded from config.
            dialog2 = self._open(pd)
            _goto_smithing(dialog2)
            tree2 = _find_smith_tree(dialog2)
            self.assertTrue(_smith_tier_node(tree2, "Rune").isExpanded())
        finally:
            ui.mw = orig_mw

    # ---- Stats / Bank / HUD registry-driven surfaces ----------------------
    def test_stats_tab_has_fletching_and_shows_its_details(self) -> None:
        btn = _find_tool_button(self.dialog, "Fletching")
        btn.click()
        QApplication.processEvents()
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn("Fletching Stats", labels)
        self.assertIn("Fletching Level:", labels)

    def test_stats_tab_has_firemaking_and_shows_its_details(self) -> None:
        btn = _find_tool_button(self.dialog, "Firemaking")
        btn.click()
        QApplication.processEvents()
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn("Firemaking Stats", labels)
        self.assertIn("Firemaking Level:", labels)

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

    def test_bank_groups_firemaking_logs_and_ashes_with_icons(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Arctic pine logs": 3,
            "Cursed magic logs": 1,
            "Ashes": 2,
        }
        dialog = self._open(pd)
        bank = _find_bank_list(dialog)
        texts = [bank.item(i).text() for i in range(bank.count())]
        for header in ("Logs", "Materials"):
            self.assertIn(header, texts, f"missing bank category header {header!r}")
        self.assertTrue(any(t.startswith("Arctic pine logs x3") for t in texts))
        self.assertTrue(any(t.startswith("Ashes x2") for t in texts))
        ashes_row = next(
            bank.item(i) for i in range(bank.count())
            if bank.item(i).text().startswith("Ashes x")
        )
        self.assertFalse(ashes_row.icon().isNull(), "Ashes row has no icon")

    def test_bank_gear_lives_in_separate_panel_from_striped_inventory(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Logs": 5}
        dialog = self._open(pd)
        bank = _find_bank_list(dialog)
        gear = _find_gear_list(dialog)
        # The gear panel must be a distinct widget from the striped inventory,
        # and must not carry the alternating-row striping.
        self.assertIsNot(gear, bank, "gear shares the inventory list")
        self.assertFalse(gear.alternatingRowColors(), "gear panel is striped")
        bank_texts = [bank.item(i).text() for i in range(bank.count())]
        self.assertNotIn("Toolbelt", bank_texts, "Toolbelt leaked into inventory list")
        gear_texts = [gear.item(i).text() for i in range(gear.count())]
        self.assertIn("Toolbelt", gear_texts, "missing Toolbelt header")
        self.assertTrue(any(t.startswith("Pickaxe: ") for t in gear_texts), f"no pickaxe row in {gear_texts}")
        self.assertTrue(any(t.startswith("Hatchet: ") for t in gear_texts), f"no hatchet row in {gear_texts}")
        # Worn equipment moved to its own tab; the Bank gear strip is toolbelt
        # only now and must not still carry the old "Equipped" placeholder.
        self.assertNotIn("Equipped", gear_texts, "Equipped header leaked into Bank gear strip")
        self.assertNotIn("Nothing equipped yet.", gear_texts)
        pick_row = next(
            gear.item(i) for i in range(gear.count())
            if gear.item(i).text().startswith("Pickaxe: ")
        )
        self.assertFalse(pick_row.icon().isNull(), "pickaxe gear row has no icon")

    # ---- Equipment tab (worn slots, equip/unequip, stat totals) -----------
    def _open_with_equip(self, pd: dict) -> "QDialog":
        """Open the menu with equip/unequip wired to the real pure logic.

        The frontend test seam mirrors what __init__.on_equip_item /
        on_unequip_slot do (run the pure mutation, persist into player_data) so
        the menu -> handler -> refresh contract is exercised end to end without
        Anki's global state.
        """
        from logic_pure import equip_item_pure, unequip_item_pure
        from constants import EQUIPMENT_ITEM_DATA

        def _equip(item_name: str) -> bool:
            inv, equipment, ok = equip_item_pure(
                item_name,
                pd.get("inventory", {}) or {},
                pd.get("equipment", {}) or {},
                EQUIPMENT_ITEM_DATA,
            )
            if ok:
                pd["inventory"] = inv
                pd["equipment"] = equipment
            return ok

        def _unequip(slot: str) -> bool:
            inv, equipment, ok = unequip_item_pure(
                slot,
                pd.get("inventory", {}) or {},
                pd.get("equipment", {}) or {},
            )
            if ok:
                pd["inventory"] = inv
                pd["equipment"] = equipment
            return ok

        self._captured.clear()
        self._ui.show_main_menu(
            player_data=pd,
            current_skill="Mining",
            can_smelt_any_bar=True,
            on_save_skill=lambda *a: None,
            on_set_ore=lambda *a: None,
            on_set_tree=lambda *a: None,
            on_set_bar=lambda *a: None,
            on_set_smith=lambda *a: None,
            on_set_craft=lambda *a: None,
            on_set_fletch=lambda *a: None,
            on_set_utility=lambda *a: None,
            on_equip_item=_equip,
            on_unequip_slot=_unequip,
        )
        self.assertTrue(self._captured, "show_main_menu did not call dialog.exec()")
        return self._captured[-1]

    def test_equipment_tab_renders_all_eleven_slots(self) -> None:
        from constants import EQUIPMENT_SLOTS

        equip_list = _find_equipment_list(self.dialog)
        rendered_slots = {
            equip_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(equip_list.count())
        }
        for slot in EQUIPMENT_SLOTS:
            self.assertIn(slot.id, rendered_slots, f"slot {slot.id!r} not rendered")
        # Empty save -> every slot shows the greyed "(empty)" placeholder.
        empties = [
            equip_list.item(i).text()
            for i in range(equip_list.count())
            if equip_list.item(i).data(Qt.ItemDataRole.UserRole + 1) is None
        ]
        self.assertEqual(len(empties), len(EQUIPMENT_SLOTS))
        self.assertTrue(all("(empty)" in t for t in empties))
        # Slot placeholder art is fetched into equipment_slots/, so empty rows
        # should carry the greyed OSRS slot icon (graceful text-only if absent).
        import ui as _ui
        if _ui.equipment_slot_icon_path("head"):
            head_row = _equip_slot_row(equip_list, "head")
            self.assertFalse(head_row.icon().isNull(), "head slot has no placeholder icon")

    def test_empty_slot_text_is_dark_mode_safe_not_palette_mid(self) -> None:
        # Regression guard for the recurring "greyed text vanishes in dark mode"
        # bug: empty-slot labels must use the dim-text helper (derived from the
        # readable Text role with reduced alpha), never QPalette.Mid (a border
        # role that renders near-black on a dark base).
        import ui as _ui
        from aqt.qt import QPalette

        equip_list = _find_equipment_list(self.dialog)
        head_row = _equip_slot_row(equip_list, "head")
        fg = head_row.foreground().color()
        mid = equip_list.palette().color(QPalette.ColorRole.Mid)
        expected = _ui.dim_text_color(equip_list)
        self.assertEqual(fg.rgba(), expected.rgba(), "empty slot not using dim_text_color")
        self.assertLess(fg.alpha(), 255, "dim text should be semi-transparent")
        self.assertNotEqual(
            (fg.red(), fg.green(), fg.blue(), fg.alpha()),
            (mid.red(), mid.green(), mid.blue(), mid.alpha()),
            "empty slot text fell back to palette(mid) (invisible in dark mode)",
        )

    def test_bronze_item_exposes_enabled_equip(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze platebody": 1}
        dialog = self._open_with_equip(pd)
        menu = dialog._ankiscape_equip_menu_for("Bronze platebody")
        action = menu.actions()[0]
        self.assertEqual(action.text(), "Equip")
        self.assertTrue(action.isEnabled(), "bronze (req 1) Equip should be enabled")

    def test_rune_item_exposes_disabled_equip_with_reason(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Rune platebody": 1}
        dialog = self._open_with_equip(pd)
        menu = dialog._ankiscape_equip_menu_for("Rune platebody")
        action = menu.actions()[0]
        # Defence defaults to level 1, rune needs 40 -> locked with the reason.
        self.assertFalse(action.isEnabled(), "rune Equip should be locked at default combat")
        self.assertIn("Requires level 40 Defense", action.text())

    def test_equipping_moves_item_to_slot_and_out_of_inventory(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze platebody": 1}
        dialog = self._open_with_equip(pd)
        menu = dialog._ankiscape_equip_menu_for("Bronze platebody")
        menu.actions()[0].trigger()
        QApplication.processEvents()
        # Backend state: moved out of inventory into the body slot.
        self.assertEqual(pd["equipment"].get("body"), "Bronze platebody")
        self.assertEqual(pd["inventory"].get("Bronze platebody", 0), 0)
        # Frontend reflects it: the body slot row now names the item.
        equip_list = _find_equipment_list(dialog)
        body_row = _equip_slot_row(equip_list, "body")
        self.assertIn("Bronze platebody", body_row.text())
        self.assertEqual(body_row.data(Qt.ItemDataRole.UserRole + 1), "Bronze platebody")

    def test_unequip_returns_item_to_inventory(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {}
        pd["equipment"] = {"body": "Bronze platebody"}
        dialog = self._open_with_equip(pd)
        equip_list = _find_equipment_list(dialog)
        body_row = _equip_slot_row(equip_list, "body")
        self.assertIn("Bronze platebody", body_row.text())
        menu = dialog._ankiscape_unequip_menu_for("body")
        self.assertIsNotNone(menu, "filled slot should offer an Unequip action")
        menu.actions()[0].trigger()
        QApplication.processEvents()
        self.assertNotIn("body", pd["equipment"])
        self.assertEqual(pd["inventory"].get("Bronze platebody", 0), 1)
        # Slot returns to the greyed placeholder.
        equip_list = _find_equipment_list(dialog)
        self.assertIn("(empty)", _equip_slot_row(equip_list, "body").text())

    def test_empty_slot_offers_no_unequip_menu(self) -> None:
        dialog = self._open_with_equip(_make_player_data())
        self.assertIsNone(dialog._ankiscape_unequip_menu_for("body"))

    def test_equipping_two_hander_clears_shield(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze 2h sword": 1}
        pd["equipment"] = {"shield": "Bronze kiteshield"}
        dialog = self._open_with_equip(pd)
        menu = dialog._ankiscape_equip_menu_for("Bronze 2h sword")
        menu.actions()[0].trigger()
        QApplication.processEvents()
        # 2h occupies the weapon slot and forces the shield off (back to bank).
        self.assertEqual(pd["equipment"].get("weapon"), "Bronze 2h sword")
        self.assertNotIn("shield", pd["equipment"])
        self.assertEqual(pd["inventory"].get("Bronze kiteshield", 0), 1)
        equip_list = _find_equipment_list(dialog)
        self.assertIn("(empty)", _equip_slot_row(equip_list, "shield").text())
        self.assertIn("Bronze 2h sword", _equip_slot_row(equip_list, "weapon").text())

    def test_stat_totals_reflect_worn_set(self) -> None:
        from constants import EQUIPMENT_ITEM_DATA

        pd = _make_player_data()
        pd["equipment"] = {"body": "Bronze platebody", "head": "Bronze full helm"}
        dialog = self._open_with_equip(pd)
        totals = next(
            lbl for lbl in dialog.findChildren(QLabel)
            if lbl.objectName() == "equipmentTotals"
        )
        text = totals.text()
        # Bronze platebody defence_stab 15 + Bronze full helm defence_stab 4 = 19.
        expected = (
            EQUIPMENT_ITEM_DATA["Bronze platebody"]["bonuses"]["defence_stab"]
            + EQUIPMENT_ITEM_DATA["Bronze full helm"]["bonuses"]["defence_stab"]
        )
        self.assertIn(f"Stab +{expected}", text)
        self.assertIn("Defence bonuses", text)

    def test_equippable_bank_row_has_bonus_tooltip(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Rune scimitar": 1}
        dialog = self._open_with_equip(pd)
        bank = _find_bank_list(dialog)
        scim = next(
            bank.item(i) for i in range(bank.count())
            if bank.item(i).text().startswith("Rune scimitar")
        )
        tip = scim.toolTip()
        self.assertIn("Requires level 40 Attack", tip)
        self.assertIn("Attack bonuses", tip)

    def test_hud_recognizes_fletching_as_active_skill(self) -> None:
        hud = self._ui.ReviewHUD(None)
        hud.set_data(_make_player_data(), "Fletching")
        self.assertTrue(
            hud.title_lbl.text().startswith("Fletching"),
            f"HUD did not recognize Fletching; shows {hud.title_lbl.text()!r}",
        )
        self.assertFalse(hud.icon_lbl.pixmap().isNull(), "HUD has no Fletching icon")

    def test_hud_recognizes_firemaking_as_active_skill(self) -> None:
        pd = _make_player_data()
        pd["current_firemaking"] = "logs"
        hud = self._ui.ReviewHUD(None)
        hud.set_data(pd, "Firemaking")
        self.assertTrue(
            hud.title_lbl.text().startswith("Firemaking"),
            f"HUD did not recognize Firemaking; shows {hud.title_lbl.text()!r}",
        )
        self.assertEqual(hud.target_lbl.text(), "Logs")
        self.assertFalse(hud.icon_lbl.pixmap().isNull(), "HUD has no Firemaking icon")

    # ---- Crafting/Utility rework surfaces ---------------------------------
    def _open_utility(self, dialog: "QDialog") -> "QListWidget":
        cat = next(
            b for b in dialog.findChildren(QPushButton) if b.text() == "Utility / Activities"
        )
        cat.click()
        QApplication.processEvents()
        return _find_list_with_item_prefix(dialog, "Make soft clay")

    def test_soft_clay_left_crafting_and_is_now_a_utility_activity(self) -> None:
        # Open Crafting target tree and assert Soft clay is no longer a target.
        tree = _goto_crafting(self.dialog)
        craft_texts = [it.text(0) for it in _tree_items(tree)]
        self.assertFalse(
            any(t.startswith("Soft clay") for t in craft_texts),
            f"Soft clay should not be a Crafting target anymore: {craft_texts}",
        )
        # And it now lives under Utility / Activities.
        utility_list = self._open_utility(self.dialog)
        util_texts = [utility_list.item(i).text() for i in range(utility_list.count())]
        self.assertIn("Make soft clay", util_texts)
        self.assertIn("Gather wool", util_texts)
        self.assertIn("Scavenge chicken feathers", util_texts)

    # ---- Crafting parity (family-grouped CRAFTING_DATA recipe tree) --------
    def test_crafting_groups_recipes_by_family(self) -> None:
        tree = _goto_crafting(self.dialog)
        family_roles = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__family__:gems", family_roles)
        self.assertIn("__family__:jewellery", family_roles)
        # The Gem-cutting family parents the stable cut recipe IDs.
        gems = _craft_family_node(tree, "gems")
        child_ids = {gems.child(i).data(0, Qt.ItemDataRole.UserRole) for i in range(gems.childCount())}
        self.assertIn("cut_emerald", child_ids)
        self.assertIn("cut_sapphire", child_ids)

    def test_crafting_rows_carry_stable_recipe_ids_not_display_names(self) -> None:
        tree = _goto_crafting(self.dialog)
        roles = [it.data(0, Qt.ItemDataRole.UserRole) for it in _tree_items(tree)]
        self.assertIn("jewellery_sapphire_necklace", roles)
        self.assertNotIn("Sapphire necklace", roles)
        # Display-name collisions (e.g. the strung "Dragonstone ammy") are exactly
        # why targets are keyed by stable id, never by output name.
        self.assertIn("jewellery_dragonstone_ammy", roles)
        self.assertIn("string_dragonstone_amulet", roles)

    def test_crafting_children_sorted_by_level_within_a_family(self) -> None:
        tree = _goto_crafting(self.dialog)
        jewellery = _craft_family_node(tree, "jewellery")
        levels = [
            int(re.search(r"\(Lvl (\d+)\)", jewellery.child(i).text(0)).group(1))
            for i in range(jewellery.childCount())
        ]
        self.assertEqual(levels, sorted(levels), f"jewellery not level-ordered: {levels}")

    def test_crafting_dependency_heavy_targets_are_wired_like_any_other(self) -> None:
        # Dragonstone/onyx/hide/glass/battlestaff targets are NOT hidden, NOT
        # special-cased, and carry no distinct tag/label/state. They are simply,
        # emergently un-runnable because the player holds 0 of a material with no
        # source yet — identical to a Sapphire ring with 0 sapphires. The only
        # gate is the normal missing-material check.
        pd = _make_player_data()
        pd["inventory"] = {}
        pd["crafting_level"] = 99
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        for rid in (
            "cut_dragonstone",
            "cut_onyx",
            "jewellery_onyx_amulet",
            "leather_black_dhide_body",
            "glass_beer_glass",
            "battlestaff_water_battlestaff",
        ):
            row = _craft_row(tree, rid)
            # Present and visible, with no special "input-starved"/"coming soon"
            # wording on the row — wired exactly like every other target.
            self.assertNotIn("input-starved", row.text(0).lower(), rid)
            self.assertNotIn("coming soon", row.text(0).lower(), rid)
            # Locked only on materials (level 99 is met), same as any other recipe
            # whose materials you lack.
            self.assertTrue(row.isDisabled(), f"{rid} should be material-gated")
            self.assertIn("materials", row.toolTip(0))
            self.assertNotIn("level", row.toolTip(0).split("Locked due to:")[-1])

    def test_crafting_disabled_row_click_does_not_change_target(self) -> None:
        # Bug fix: itemClicked fires on disabled rows, so clicking a locked target
        # must NOT make it active (otherwise the next review fails with
        # "you don't have X"). Empty inventory locks every craft on materials.
        pd = _make_player_data()
        pd["inventory"] = {}
        pd["crafting_level"] = 99
        pd["current_craft"] = None
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        locked = _craft_row(tree, "cut_dragonstone")
        self.assertTrue(locked.isDisabled())
        before = list(self._craft_calls)
        tree.itemClicked.emit(locked, 0)
        tree.itemActivated.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._craft_calls, before, "locked target must not be selectable")

    def test_smithing_disabled_row_click_does_not_change_target(self) -> None:
        # Same disabled-row click guard on the Smithing tree.
        pd = _make_player_data()
        pd["inventory"] = {}  # no bars -> every smith recipe locked on materials
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        locked = _smith_row(tree, "smelt_bronze_bar")
        self.assertTrue(locked.isDisabled())
        before = list(self._smith_calls)
        tree.itemClicked.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._smith_calls, before, "locked smith target must not be selectable")

    def test_crafting_tooltip_shows_output_xp_and_owned_counts(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Gold bar": 1}  # sapphire necklace needs a bar + sapphire
        pd["crafting_level"] = 99
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        row = _craft_row(tree, "jewellery_sapphire_necklace")
        tip = row.toolTip(0)
        self.assertIn("Output: Sapphire necklace x1", tip)
        self.assertIn("Base XP:", tip)
        self.assertIn("Gold bar x1 (you have 1)", tip)
        self.assertIn("Sapphire x1 (you have 0)", tip)
        self.assertTrue(row.isDisabled())  # missing the sapphire

    def test_crafting_unlocks_with_materials_and_persists_recipe_id(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Gold bar": 5}
        pd["crafting_level"] = 99
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        ring = _craft_row(tree, "jewellery_gold_ring")
        self.assertFalse(ring.isDisabled())
        tree.itemClicked.emit(ring, 0)
        QApplication.processEvents()
        self.assertEqual(self._craft_calls[-1], "jewellery_gold_ring")

    def test_crafting_clicking_a_family_node_does_not_persist_a_target(self) -> None:
        tree = _goto_crafting(self.dialog)
        before = list(self._craft_calls)
        tree.itemClicked.emit(_craft_family_node(tree, "jewellery"), 0)
        QApplication.processEvents()
        self.assertEqual(self._craft_calls, before, "family headers must not set a target")

    def test_crafting_highlights_current_target_and_expands_its_family(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Gold bar": 5}
        pd["current_craft"] = "jewellery_gold_ring"
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        current = tree.currentItem()
        self.assertIsNotNone(current)
        self.assertEqual(current.data(0, Qt.ItemDataRole.UserRole), "jewellery_gold_ring")
        # The family holding the current target opens so the selection is visible.
        self.assertTrue(_craft_family_node(tree, "jewellery").isExpanded())
        # Unrelated families stay collapsed to tame the panel.
        self.assertFalse(_craft_family_node(tree, "gems").isExpanded())

    def test_utility_panel_uses_no_xp_language(self) -> None:
        self._open_utility(self.dialog)
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertTrue(
            any("no XP" in t for t in labels),
            f"Utility panel should state it earns no XP; labels={labels}",
        )

    def test_utility_rows_use_activity_icon_contract(self) -> None:
        utility_list = self._open_utility(self.dialog)
        for i in range(utility_list.count()):
            row = utility_list.item(i)
            self.assertFalse(row.icon().isNull(), f"{row.text()} should have an activity icon")

    def test_feather_scavenging_is_enabled_and_selectable_from_utility(self) -> None:
        utility_list = self._open_utility(self.dialog)
        feather_row = next(
            utility_list.item(i) for i in range(utility_list.count())
            if utility_list.item(i).text() == "Scavenge chicken feathers"
        )

        self.assertTrue(feather_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertFalse(feather_row.icon().isNull())
        self.assertIn("No Crafting XP", feather_row.toolTip())
        self.assertIn("Output: Feather x1", feather_row.toolTip())
        self.assertIn("No materials required", feather_row.toolTip())

        self._utility_calls.clear()
        utility_list.itemClicked.emit(feather_row)
        QApplication.processEvents()

        self.assertEqual(self._utility_calls, ["scavenge_chicken_feathers"])

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

    def test_settings_expose_action_multiplier_under_gameplay(self) -> None:
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn("Gameplay", labels)
        self.assertIn("Actions per review:", labels)
        spins = self.dialog.findChildren(QSpinBox)
        self.assertTrue(spins, "no action multiplier spin box found")
        self.assertEqual(spins[0].minimum(), 1)
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
