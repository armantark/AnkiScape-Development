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
    from aqt.qt import QApplication, QCheckBox, QComboBox, QDialog, QLabel, QLineEdit, QListWidget, QPushButton, QIcon, QImage, QTabWidget, QToolButton, QSpinBox, Qt, QTreeWidget, QTreeWidgetItem, QWidget
    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


def _make_player_data() -> dict:
    from quest_data import default_quest_states

    data: dict = {"inventory": {}}
    for skill in ("mining", "woodcutting", "fishing", "hunter", "smithing", "crafting", "fletching", "firemaking", "cooking", "runecrafting"):
        data[f"{skill}_level"] = 33
        data[f"{skill}_exp"] = 1000.0
    # Real saves are seeded with a bound starter tool per gathering skill; without
    # it every tree/rock would lock on "no usable hatchet/pickaxe" and those rows
    # couldn't be exercised. Mirror that seed so Woodcutting and Mining rows unlock.
    data["toolbelt"] = {"woodcutting": ["bronze_hatchet"], "mining": ["bronze_pickaxe"]}
    data["equipment"] = {}
    data["current_hunter"] = "catch_crimson_swift"
    data["current_runecrafting"] = "craft_air_runes"
    data["current_quest"] = "rune_mysteries"
    data["quests"] = default_quest_states()
    data["quest_points"] = 0
    data["claims"] = {"wicked_hood": {"claimed": False}}
    data["wicked_hood"] = {"fed_altars": []}
    data["runecrafting_pouches"] = {}
    data["item_charges"] = {}
    return data


def _panel_title(dialog: "QDialog") -> str:
    """Return the text of the Skills-hub panel header, if present.

    The header is the QLabel styled bold/large that reads e.g. "Woodcutting — Lv 33".
    """
    pattern = re.compile(r"^(Mining|Woodcutting|Fishing|Hunter|Smithing|Crafting|Fletching|Firemaking|Cooking|Runecrafting)(\s+—\s+Lv\s+\d+)?$")
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


def _icon_pixels(icon: "QIcon") -> bytes:
    image = icon.pixmap(28, 28).toImage().convertToFormat(QImage.Format.Format_ARGB32)
    bits = image.bits()
    bits.setsize(image.sizeInBytes())
    return bytes(bits)


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


def _find_tree_with_user_role(dialog: "QDialog", role) -> "QTreeWidget":
    for tw in dialog.findChildren(QTreeWidget):
        if any(it.data(0, Qt.ItemDataRole.UserRole) == role for it in _smith_tree_items(tw)):
            return tw
    raise AssertionError(f"no tree widget with user role {role!r}")


def _tree_row(tree: "QTreeWidget", role) -> "QTreeWidgetItem":
    for it in _smith_tree_items(tree):
        if it.data(0, Qt.ItemDataRole.UserRole) == role:
            return it
    raise AssertionError(f"tree row {role!r} not found")


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


def _find_fletching_tree(dialog: "QDialog") -> "QTreeWidget":
    """The Fletching target tree, identified by stable source-backed target ids."""
    for tw in dialog.findChildren(QTreeWidget):
        if any(it.data(0, Qt.ItemDataRole.UserRole) == "arrow_shafts" for it in _tree_items(tw)):
            return tw
    raise AssertionError("fletching tree (with target ids) not found")


def _fletching_row(tree: "QTreeWidget", target_id: str) -> "QTreeWidgetItem":
    for it in _tree_items(tree):
        if it.data(0, Qt.ItemDataRole.UserRole) == target_id:
            return it
    raise AssertionError(f"fletching row {target_id!r} not found")


def _fletching_group_node(tree: "QTreeWidget", group: str) -> "QTreeWidgetItem":
    role = f"__fletching_group__:{group}"
    for i in range(tree.topLevelItemCount()):
        if tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole) == role:
            return tree.topLevelItem(i)
    raise AssertionError(f"fletching group node {group!r} not found")


def _find_hunter_tree(dialog: "QDialog") -> "QTreeWidget":
    for tw in dialog.findChildren(QTreeWidget):
        if any(it.data(0, Qt.ItemDataRole.UserRole) == "catch_crimson_swift" for it in _tree_items(tw)):
            return tw
    raise AssertionError("hunter tree (with target ids) not found")


def _hunter_row(tree: "QTreeWidget", target_id: str) -> "QTreeWidgetItem":
    for it in _tree_items(tree):
        if it.data(0, Qt.ItemDataRole.UserRole) == target_id:
            return it
    raise AssertionError(f"hunter row {target_id!r} not found")


def _hunter_group_node(tree: "QTreeWidget", group: str) -> "QTreeWidgetItem":
    role = f"__hunter_group__:{group}"
    for i in range(tree.topLevelItemCount()):
        if tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole) == role:
            return tree.topLevelItem(i)
    raise AssertionError(f"hunter group node {group!r} not found")


def _goto_hunter(dialog: "QDialog") -> "QTreeWidget":
    skill_list = _find_skill_list(dialog)
    row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Hunter")
    skill_list.setCurrentRow(row)
    QApplication.processEvents()
    return _find_hunter_tree(dialog)


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


def _find_cooking_tree(dialog: "QDialog") -> "QTreeWidget":
    for tw in dialog.findChildren(QTreeWidget):
        if any(it.data(0, Qt.ItemDataRole.UserRole) == "cook_shrimps" for it in _tree_items(tw)):
            return tw
    raise AssertionError("cooking tree (with target ids) not found")


def _cooking_row(tree: "QTreeWidget", target_id: str) -> "QTreeWidgetItem":
    for it in _tree_items(tree):
        if it.data(0, Qt.ItemDataRole.UserRole) == target_id:
            return it
    raise AssertionError(f"cooking row {target_id!r} not found")


def _cooking_family_node(tree: "QTreeWidget", family: str) -> "QTreeWidgetItem":
    role = f"__cooking_family__:{family}"
    for i in range(tree.topLevelItemCount()):
        if tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole) == role:
            return tree.topLevelItem(i)
    raise AssertionError(f"cooking family node {family!r} not found")


def _goto_cooking(dialog: "QDialog") -> "QTreeWidget":
    artisan = next(b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan")
    artisan.click()
    QApplication.processEvents()
    skill_list = _find_artisan_skill_list(dialog)
    row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Cooking")
    skill_list.setCurrentRow(row)
    QApplication.processEvents()
    return _find_cooking_tree(dialog)


def _find_runecrafting_tree(dialog: "QDialog") -> "QTreeWidget":
    for tw in dialog.findChildren(QTreeWidget):
        if any(it.data(0, Qt.ItemDataRole.UserRole) == "craft_air_runes" for it in _tree_items(tw)):
            return tw
    raise AssertionError("runecrafting tree (with target ids) not found")


def _runecrafting_row(tree: "QTreeWidget", target_id: str) -> "QTreeWidgetItem":
    for it in _tree_items(tree):
        if it.data(0, Qt.ItemDataRole.UserRole) == target_id:
            return it
    raise AssertionError(f"runecrafting row {target_id!r} not found")


def _goto_runecrafting(dialog: "QDialog") -> "QTreeWidget":
    artisan = next(b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan")
    artisan.click()
    QApplication.processEvents()
    skill_list = _find_artisan_skill_list(dialog)
    row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Runecrafting")
    skill_list.setCurrentRow(row)
    QApplication.processEvents()
    return _find_runecrafting_tree(dialog)


def _find_utility_tree(dialog: "QDialog") -> "QTreeWidget":
    for tw in dialog.findChildren(QTreeWidget):
        if any(it.data(0, Qt.ItemDataRole.UserRole) == "make_soft_clay" for it in _tree_items(tw)):
            return tw
    raise AssertionError("utility tree (with activity ids) not found")


def _utility_row(tree: "QTreeWidget", activity_id: str) -> "QTreeWidgetItem":
    for it in _tree_items(tree):
        if it.data(0, Qt.ItemDataRole.UserRole) == activity_id:
            return it
    raise AssertionError(f"utility row {activity_id!r} not found")


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


def _find_named_widget(dialog: "QDialog", object_name: str) -> "QWidget":
    for widget in dialog.findChildren(QWidget):
        if widget.objectName() == object_name:
            return widget
    raise AssertionError(f"widget {object_name!r} not found")


def _find_named_label(dialog: "QDialog", object_name: str) -> "QLabel":
    for label in dialog.findChildren(QLabel):
        if label.objectName() == object_name:
            return label
    raise AssertionError(f"label {object_name!r} not found")


def _find_named_list(dialog: "QDialog", object_name: str) -> "QListWidget":
    for lw in dialog.findChildren(QListWidget):
        if lw.objectName() == object_name:
            return lw
    raise AssertionError(f"list {object_name!r} not found")


def _find_named_button(dialog: "QDialog", object_name: str) -> "QPushButton":
    for button in dialog.findChildren(QPushButton):
        if button.objectName() == object_name:
            return button
    raise AssertionError(f"button {object_name!r} not found")


def _find_named_line_edit(dialog: "QDialog", object_name: str) -> "QLineEdit":
    for line_edit in dialog.findChildren(QLineEdit):
        if line_edit.objectName() == object_name:
            return line_edit
    raise AssertionError(f"line edit {object_name!r} not found")


def _find_main_tabs(dialog: "QDialog") -> "QTabWidget":
    for tabs in dialog.findChildren(QTabWidget):
        labels = [tabs.tabText(i) for i in range(tabs.count())]
        if "Skills" in labels and "Shop" in labels and "Bank" in labels:
            return tabs
    raise AssertionError("main tab widget not found")


def _open_shop_tab(dialog: "QDialog") -> None:
    tabs = _find_main_tabs(dialog)
    index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Shop")
    tabs.setCurrentIndex(index)
    QApplication.processEvents()


def _open_bank_tab(dialog: "QDialog") -> None:
    tabs = _find_main_tabs(dialog)
    index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Bank")
    tabs.setCurrentIndex(index)
    QApplication.processEvents()


def _open_equipment_tab(dialog: "QDialog") -> None:
    tabs = _find_main_tabs(dialog)
    index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Equipment")
    tabs.setCurrentIndex(index)
    QApplication.processEvents()


def _open_first_shop(dialog: "QDialog") -> None:
    """Browse-first Shop tab: no shop opens until one is clicked."""
    selector = _find_named_list(dialog, "shopSelectionList")
    selector.setCurrentItem(selector.item(0))
    QApplication.processEvents()


def _list_texts(list_widget: "QListWidget") -> list[str]:
    return [list_widget.item(i).text() for i in range(list_widget.count())]


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
        # Same seam for Fishing target selection.
        self._fishing_calls: list = []
        # Same seam for Hunter target selection.
        self._hunter_calls: list = []
        # Same seam for Cooking target selection.
        self._cooking_calls: list = []
        # Same seam for Runecrafting target selection.
        self._runecrafting_calls: list = []
        # Same seams for Combat target/style/spell selection.
        self._combat_calls: list = []
        self._combat_style_calls: list = []
        self._combat_spell_calls: list = []
        self._combat_threshold_calls: list = []
        self._combat_food_calls: list = []
        self._combat_refill_calls: list = []
        self._combat_unload_calls: list = []
        self._death_office_calls: list = []
        # Quests and Bank Claims are review-adjacent but not levelled skills.
        self._quest_calls: list = []
        self._quest_choice_calls: list = []
        self._claim_calls: list = []
        # Seam for the Stronghold of Security landmark's "claim reward" click.
        self._stronghold_claim_calls: list = []

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

    def _open(self, player_data: dict, current_skill: str = "Mining", **extra) -> "QDialog":
        self._ui.show_main_menu(
            **extra,
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
            on_set_fishing=lambda target: self._fishing_calls.append(target),
            on_set_hunter=lambda target: self._hunter_calls.append(target),
            on_set_cooking=lambda target: self._cooking_calls.append(target),
            on_set_runecrafting=lambda target: self._runecrafting_calls.append(target),
            on_set_utility=lambda activity: self._utility_calls.append(activity),
            on_set_combat=lambda target: self._combat_calls.append(target),
            on_set_combat_style=lambda style: self._combat_style_calls.append(style),
            on_set_combat_spell=lambda spell: self._combat_spell_calls.append(spell),
            on_set_combat_auto_eat_threshold=lambda threshold: self._combat_threshold_calls.append(threshold),
            on_set_combat_auto_eat_food=lambda food: self._combat_food_calls.append(food),
            on_refill_combat_loadout=lambda: self._combat_refill_calls.append(True) or True,
            on_unload_combat_loadout=lambda: self._combat_unload_calls.append(True) or True,
            on_reclaim_death_office=lambda: self._death_office_calls.append(True) or True,
            on_set_quest=lambda quest_id: self._quest_calls.append(quest_id),
            on_set_quest_route_choice=lambda quest_id, route_id: self._quest_choice_calls.append((quest_id, route_id)) or True,
            on_claim_reward=lambda claim_id, selected_skill_id=None: self._claim_calls.append((claim_id, selected_skill_id)) or True,
            on_claim_stronghold_reward=lambda: self._stronghold_claim_calls.append(True) or True,
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

    def test_bank_carried_inventory_panel_is_present_and_collapsible(self) -> None:
        summary = self.dialog.findChild(QLabel, "carriedInventorySummary")
        self.assertIsNotNone(summary)
        self.assertIn("bank run", summary.text().lower())

        # The loot-threshold spinner moved to the Equipment tab's combat controls;
        # the Bank keeps a pointer to it instead.
        self.assertIsNone(self.dialog.findChild(QSpinBox, "carriedLootThresholdSpin"))
        self.assertIsNotNone(self.dialog.findChild(QSpinBox, "combatLootThresholdSpin"))
        self.assertIsNotNone(self.dialog.findChild(QLabel, "carriedEquipmentPointer"))
        # No packing-mode dropdown: skilling packs are inferred, not player-picked.
        self.assertIsNone(self.dialog.findChild(QComboBox, "carriedPackModeCombo"))

        header = self.dialog.findChild(QPushButton, "carriedInventoryHeader")
        self.assertIsNotNone(header)
        self.assertTrue(header.isCheckable())
        body = summary.parentWidget()  # carried_summary lives directly on carried_body
        # Collapsed by default; toggling the header reveals the body. Use
        # isVisibleTo (local intent) since the Bank tab itself may be inactive.
        self.assertFalse(body.isVisibleTo(body.parentWidget()))
        self.assertIn("▸", header.text())
        header.setChecked(True)
        QApplication.processEvents()
        self.assertTrue(body.isVisibleTo(body.parentWidget()))
        self.assertIn("▾", header.text())

    def test_carried_keep_drop_toggle_present_for_gathering_and_wired(self) -> None:
        from aqt.qt import QCheckBox

        calls: list = []
        dialog = self._open(
            _make_player_data(),
            carried_keep_drop_state="keep",
            on_set_carried_keep_drop=lambda drop: calls.append(drop),
        )
        check = dialog.findChild(QCheckBox, "carriedKeepDropCheck")
        self.assertIsNotNone(check, "Keep/Drop toggle missing when a gathering target is active")
        self.assertFalse(check.isChecked())  # default keep
        check.setChecked(True)
        QApplication.processEvents()
        self.assertEqual(calls[-1], True)  # toggling to drop calls back with True
        dialog.deleteLater()

    def test_per_drop_loot_override_pill_present_and_wired(self) -> None:
        from aqt.qt import QCheckBox, QPushButton, QWidget

        calls: list = []
        rows = (
            {"item": "Bones", "mode": "keep"},
            {"item": "Raw chicken", "mode": "auto"},
        )
        dialog = self._open(
            _make_player_data(),
            loot_override_rows=rows,
            on_set_loot_override=lambda item, mode: calls.append((item, mode)),
        )
        # The per-drop overrides now live in the Combat setup panel (Equipment tab)
        # as icon cells with a binary Keep | Drop pill, behind an Advanced
        # disclosure. Neither segment lit means "Auto" (follow the value threshold).
        grid = dialog.findChild(QWidget, "combatLootOverrideGrid")
        self.assertIsNotNone(grid, "per-drop override grid missing")
        bones_keep = dialog.findChild(QPushButton, "lootOverrideKeep::Bones")
        bones_drop = dialog.findChild(QPushButton, "lootOverrideDrop::Bones")
        self.assertIsNotNone(bones_keep, "per-drop Keep segment missing")
        self.assertIsNotNone(bones_drop, "per-drop Drop segment missing")
        # Clicking Drop on a saved-Keep drop switches it to Leave and fires back.
        bones_drop.click()
        QApplication.processEvents()
        self.assertIn(("Bones", "leave"), calls)
        # Clicking the already-lit Drop segment again clears back to Auto.
        bones_drop.click()
        QApplication.processEvents()
        self.assertEqual(calls[-1], ("Bones", "auto"))

        # The simple "keep everything" toggle bulk-applies keep via the same callback.
        keep_all = dialog.findChild(QCheckBox, "combatLootKeepAllCheck")
        self.assertIsNotNone(keep_all)
        keep_all.setChecked(True)
        QApplication.processEvents()
        self.assertIn(("Raw chicken", "keep"), calls)
        dialog.deleteLater()

    def test_carried_keep_drop_toggle_absent_without_gathering_target(self) -> None:
        from aqt.qt import QCheckBox

        dialog = self._open(_make_player_data(), carried_keep_drop_state=None)
        self.assertIsNone(dialog.findChild(QCheckBox, "carriedKeepDropCheck"))
        dialog.deleteLater()

    def test_carried_layout_grid_present_wired_and_never_geometrically_compressed(self) -> None:
        # Regression guard: a plain QWidget housing 28 fixed-size cell buttons
        # defaults to a Preferred size policy, which a parent QVBoxLayout can
        # compress under space pressure -- silently clipping the grid down to a
        # sliver even though every cell reports its correct fixed size. Assert
        # actual Qt geometry (not a screenshot) so this can't regress unnoticed.
        from aqt.qt import QPushButton, QWidget

        add_calls: list = []
        clear_calls: list = []
        advanced_calls: list = []

        def get_cells():
            return tuple([("Iron ore", 1)] * 5 + [("Air rune", 5000)] + [(None, 0)] * 22)

        dialog = self._open(
            _make_player_data(),
            carried_pack_target_active=True,
            on_set_carried_advanced=lambda v: advanced_calls.append(v),
            carried_advanced_state=True,
            get_carried_layout_cells=get_cells,
            on_add_to_carried_layout=lambda name, delta: add_calls.append((name, delta)),
            on_clear_carried_layout=lambda: clear_calls.append(True),
        )
        # Layouts don't activate offscreen until the dialog is actually shown
        # (see .claude/rules/qt-offscreen-screenshots.md) -- without this, every
        # cell's geometry reads back as a stale (0, 0), masking the very
        # compression bug this test exists to catch.
        dialog.show()
        dialog.resize(560, 640)
        for _ in range(6):
            QApplication.processEvents()
        # The 28-slot editor now lives on the Equipment tab, always reachable.
        _open_equipment_tab(dialog)
        for _ in range(6):
            QApplication.processEvents()

        # The Auto|Custom segmented pill replaced the old advanced checkbox.
        # Custom mode is active (carried_advanced_state=True), so the manual
        # grid is the visible view.
        auto_btn = dialog.findChild(QPushButton, "carriedModeAuto")
        custom_btn = dialog.findChild(QPushButton, "carriedModeCustom")
        self.assertIsNotNone(auto_btn)
        self.assertIsNotNone(custom_btn)
        self.assertTrue(custom_btn.isChecked())

        grid = dialog.findChild(QWidget, "carriedLayoutGrid")
        self.assertIsNotNone(grid, "carried layout grid missing")
        self.assertTrue(grid.isVisibleTo(grid.window()))

        # All 28 cells exist and sit at their real, uncompressed geometry.
        cells = [dialog.findChild(QPushButton, f"carriedLayoutCell::{i}") for i in range(28)]
        self.assertTrue(all(cell is not None for cell in cells))
        # The container's actual size must equal its own sizeHint -- if a parent
        # layout compressed it, these would diverge (the bug this test guards).
        self.assertEqual(grid.size(), grid.sizeHint())
        for cell in cells:
            self.assertEqual(cell.size().width(), 44)
            self.assertEqual(cell.size().height(), 44)
        # Row 6 (the last of 7 rows) must be positioned below row 0, not clipped
        # into the same pixels -- the concrete symptom of the compression bug.
        self.assertGreater(cells[27].geometry().y(), cells[0].geometry().y() + 200)

        # Clicking a filled cell removes one unit via the callback.
        cells[0].click()
        QApplication.processEvents()
        self.assertIn(("Iron ore", -1), add_calls)

        # Switching to Auto hides the grid and fires the callback.
        auto_btn.click()
        QApplication.processEvents()
        self.assertFalse(grid.isVisibleTo(grid.window()))
        self.assertIn(False, advanced_calls)

        # Clear button fires its callback.
        custom_btn.click()
        QApplication.processEvents()
        clear_btn = dialog.findChild(QPushButton, "carriedLayoutClearButton")
        self.assertIsNotNone(clear_btn)
        clear_btn.click()
        QApplication.processEvents()
        self.assertEqual(clear_calls, [True])
        dialog.deleteLater()

    def test_combat_supply_mode_dropdown_present_and_wired(self) -> None:
        from aqt.qt import QComboBox

        calls: list = []
        player = _make_player_data()
        player["combat_pack_mode"] = "balanced"
        dialog = self._open(
            player,
            current_skill="Combat",
            on_set_combat_pack_mode=lambda mode: calls.append(mode),
        )
        combo = dialog.findChild(QComboBox, "combatPackModeCombo")
        self.assertIsNotNone(combo, "combat supply-mode dropdown missing")
        self.assertEqual(
            [combo.itemData(i) for i in range(combo.count())],
            ["balanced", "max_output", "max_safety"],
        )
        self.assertEqual(combo.currentData(), "balanced")
        combo.setCurrentIndex(combo.findData("max_output"))
        QApplication.processEvents()
        self.assertIn("max_output", calls)
        dialog.deleteLater()

    def test_carried_layout_grid_reachable_without_an_active_pack_target(self) -> None:
        from aqt.qt import QPushButton, QWidget

        # Regression: the advanced editor used to disappear entirely when no pack
        # target was active. It now lives on the Equipment tab and is always
        # available so players can arrange their carried pack at any time.
        dialog = self._open(_make_player_data(), carried_pack_target_active=False)
        self.assertIsNotNone(dialog.findChild(QPushButton, "carriedModeAuto"))
        self.assertIsNotNone(dialog.findChild(QPushButton, "carriedModeCustom"))
        self.assertIsNotNone(dialog.findChild(QWidget, "carriedLayoutGrid"))
        dialog.deleteLater()

    def test_shop_tab_renders_and_keeps_hidden_reward_shops_out_of_browse_and_search(self) -> None:
        from shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        hidden_name = fixtures["hidden_reward_shop"]["display_name"]
        dialog = self._open(fixtures["fixture_player_data"])
        _open_shop_tab(dialog)

        selector = _find_named_list(dialog, "shopSelectionList")
        self.assertTrue(selector.count(), "shop selector did not render visible shops")
        self.assertFalse(any(hidden_name in text for text in _list_texts(selector)))

        search = _find_named_line_edit(dialog, "shopSearchInput")
        search.setText("Stardust")
        QApplication.processEvents()
        self.assertFalse(any(hidden_name in text for text in _list_texts(selector)))
        self.assertIn("No visible shop", selector.item(0).text())

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn("Services / Vendor Actions", labels)

    def test_shop_opens_browse_first_and_detail_is_collapsible(self) -> None:
        from shop_fixtures import build_shop_frontend_fixtures
        from shop_logic import shop_view_model_pure

        fixtures = build_shop_frontend_fixtures()
        player_data = fixtures["fixture_player_data"]
        dialog = self._open(player_data)
        _open_shop_tab(dialog)

        shell = dialog.findChild(QWidget, "shopDetailShell")
        selector = _find_named_list(dialog, "shopSelectionList")
        title = _find_named_label(dialog, "shopDetailTitle")

        # No default shop: the detail panel stays closed until a shop is clicked.
        self.assertIsNotNone(shell)
        self.assertFalse(shell.isVisibleTo(dialog))
        self.assertIsNone(selector.currentItem())

        _open_first_shop(dialog)
        first_payload = selector.item(0).data(Qt.ItemDataRole.UserRole)
        self.assertEqual(first_payload.get("kind"), "shop")
        opened_view = shop_view_model_pure(player_data, first_payload["shop_id"])
        self.assertTrue(shell.isVisibleTo(dialog))
        self.assertEqual(title.text(), opened_view["display_name"])
        buy_button = _find_named_button(dialog, "shopTransactionButton")
        self.assertTrue(buy_button.isEnabled(), _find_named_label(dialog, "shopPreviewLabel").text())

        # Shops never advertise the global services; those belong to providers.
        services_panel = dialog.findChild(QWidget, "shopServicesPanel")
        self.assertIsNotNone(services_panel)
        self.assertFalse(services_panel.isVisibleTo(dialog))

        # The collapse control returns the space to the shop list.
        collapse = next(
            button for button in dialog.findChildren(QToolButton)
            if button.objectName() == "shopDetailCollapseButton"
        )
        collapse.click()
        QApplication.processEvents()
        self.assertFalse(shell.isVisibleTo(dialog))
        self.assertIsNone(selector.currentItem())

    def test_shop_icons_render_for_stock_search_sell_and_services(self) -> None:
        from shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        dialog = self._open(fixtures["fixture_player_data"])
        _open_shop_tab(dialog)
        _open_first_shop(dialog)

        stock_buttons = [
            button for button in dialog.findChildren(QToolButton)
            if button.property("shopRowId")
        ]
        self.assertTrue(any(not button.icon().isNull() for button in stock_buttons), "live stock tiles should use item icons")
        self.assertTrue(
            any(button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextUnderIcon for button in stock_buttons),
            "stock tile icons should render above the text",
        )

        sell_list = _find_named_list(dialog, "shopSellInventoryList")
        beer_item = next(
            sell_list.item(i)
            for i in range(sell_list.count())
            if sell_list.item(i).data(Qt.ItemDataRole.UserRole) == "Beer"
        )
        self.assertFalse(beer_item.icon().isNull(), "sell rows should use inventory item icons")

        search = _find_named_line_edit(dialog, "shopSearchInput")
        search.setText("Erzille seed")
        QApplication.processEvents()
        selector = _find_named_list(dialog, "shopSelectionList")
        seed_item = next(
            selector.item(i)
            for i in range(selector.count())
            if "Erzille seed" in selector.item(i).text()
        )
        self.assertFalse(seed_item.icon().isNull(), "item-first search rows should use shop item icons")

        service_list = _find_named_list(dialog, "shopServiceList")
        kebab_item = next(
            service_list.item(i)
            for i in range(service_list.count())
            if "kebab" in service_list.item(i).text().lower()
        )
        self.assertFalse(kebab_item.icon().isNull(), "vendor rows should use output item icons")

    def test_shop_preview_uses_current_player_currency_state(self) -> None:
        from shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        pd["inventory"]["Coins"] = 0
        dialog = self._open(pd)
        _open_shop_tab(dialog)
        _open_first_shop(dialog)

        meta = _find_named_label(dialog, "shopDetailMeta")
        preview = _find_named_label(dialog, "shopPreviewLabel")
        buy_button = _find_named_button(dialog, "shopTransactionButton")

        self.assertIn("Coins: 0 owned", meta.text())
        self.assertIn("Need", preview.text())
        self.assertIn("you have 0", preview.text())
        self.assertFalse(buy_button.isEnabled())

    def test_shop_locked_currency_search_shows_backend_reason_and_disables_buy(self) -> None:
        from shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        locked_view = fixtures["locked_read_only_shop"]
        locked_row = locked_view["rows"][0]
        dialog = self._open(fixtures["fixture_player_data"])
        _open_shop_tab(dialog)

        search = _find_named_line_edit(dialog, "shopSearchInput")
        search.setText(locked_row["item_name"])
        QApplication.processEvents()
        selector = _find_named_list(dialog, "shopSelectionList")
        locked_item = None
        for index in range(selector.count()):
            item = selector.item(index)
            payload = item.data(Qt.ItemDataRole.UserRole)
            if (
                isinstance(payload, dict)
                and payload.get("kind") == "stock"
                and payload.get("shop_id") == locked_view["shop_id"]
                and payload.get("row_id") == locked_row["id"]
            ):
                locked_item = item
                break
        self.assertIsNotNone(locked_item, "locked search did not render stock-source comparison rows")
        selector.setCurrentItem(locked_item)
        QApplication.processEvents()

        preview = _find_named_label(dialog, "shopPreviewLabel")
        button = _find_named_button(dialog, "shopTransactionButton")
        self.assertIn("currency_not_implemented", preview.text())
        self.assertFalse(button.isEnabled())

    def test_shop_live_stock_buy_updates_inventory_and_history(self) -> None:
        from shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        live_view = fixtures["normal_coin_stock_shop"]
        live_row = next(row for row in live_view["rows"] if row["can_buy"])
        dialog = self._open(pd)
        _open_shop_tab(dialog)

        search = _find_named_line_edit(dialog, "shopSearchInput")
        search.setText(live_row["item_name"])
        QApplication.processEvents()
        selector = _find_named_list(dialog, "shopSelectionList")
        target = None
        for index in range(selector.count()):
            item = selector.item(index)
            payload = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(payload, dict) and payload.get("shop_id") == live_view["shop_id"] and payload.get("row_id") == live_row["id"]:
                target = item
                break
        self.assertIsNotNone(target, "live stock row was not selectable from item search")
        selector.setCurrentItem(target)
        QApplication.processEvents()

        before_item = pd["inventory"].get(live_row["item_name"], 0)
        before_coins = pd["inventory"]["Coins"]
        button = _find_named_button(dialog, "shopTransactionButton")
        self.assertTrue(button.isEnabled(), _find_named_label(dialog, "shopPreviewLabel").text())
        button.click()
        QApplication.processEvents()

        self.assertEqual(pd["inventory"].get(live_row["item_name"], 0), before_item + 1)
        self.assertEqual(pd["inventory"]["Coins"], before_coins - int(live_row["buy_price"]))
        history_texts = _list_texts(_find_named_list(dialog, "shopLocalHistoryList"))
        self.assertTrue(any(text.startswith("Bought 1 x") for text in history_texts), history_texts)

    def test_shop_general_store_sell_creates_temporary_stock(self) -> None:
        from shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        general_shop_id = fixtures["player_sold_stock"]["shop_id"]
        dialog = self._open(pd)
        _open_shop_tab(dialog)

        selector = _find_named_list(dialog, "shopSelectionList")
        general_item = None
        for index in range(selector.count()):
            item = selector.item(index)
            payload = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(payload, dict) and payload.get("shop_id") == general_shop_id:
                general_item = item
                break
        self.assertIsNotNone(general_item, "visible general store was not present in browsing")
        selector.setCurrentItem(general_item)
        QApplication.processEvents()

        mode_tabs = dialog.findChild(QTabWidget, "shopModeTabs")
        self.assertIsNotNone(mode_tabs)
        mode_tabs.setCurrentIndex(1)
        QApplication.processEvents()
        sell_list = _find_named_list(dialog, "shopSellInventoryList")
        beer_item = next(
            sell_list.item(i)
            for i in range(sell_list.count())
            if sell_list.item(i).data(Qt.ItemDataRole.UserRole) == "Beer"
        )
        sell_list.setCurrentItem(beer_item)
        QApplication.processEvents()
        before_beer = pd["inventory"]["Beer"]
        before_coins = pd["inventory"]["Coins"]
        button = _find_named_button(dialog, "shopTransactionButton")
        self.assertTrue(button.isEnabled(), _find_named_label(dialog, "shopPreviewLabel").text())
        button.click()
        QApplication.processEvents()

        self.assertEqual(pd["inventory"]["Beer"], before_beer - 1)
        self.assertGreater(pd["inventory"]["Coins"], before_coins)
        mode_tabs.setCurrentIndex(0)
        QApplication.processEvents()
        stock_buttons = [
            button for button in dialog.findChildren(QToolButton)
            if button.property("shopRowId") and "Beer" in button.text()
        ]
        self.assertTrue(stock_buttons, "player-sold Beer did not appear as temporary shop stock")

    def test_shop_service_providers_browse_as_their_own_selector_entries(self) -> None:
        from shop_fixtures import build_shop_frontend_fixtures
        from shop_data import SHOP_VENDOR_ACTIONS

        fixtures = build_shop_frontend_fixtures()
        action_id = fixtures["vendor_action_transaction"]["action_id"]
        provider = str(SHOP_VENDOR_ACTIONS[action_id]["provider"])
        dialog = self._open(fixtures["fixture_player_data"])
        _open_shop_tab(dialog)

        selector = _find_named_list(dialog, "shopSelectionList")
        provider_item = None
        for index in range(selector.count()):
            payload = selector.item(index).data(Qt.ItemDataRole.UserRole)
            if isinstance(payload, dict) and payload.get("kind") == "provider" and payload.get("provider") == provider:
                provider_item = selector.item(index)
                break
        self.assertIsNotNone(provider_item, f"provider row for {provider!r} missing from browse list")
        selector.setCurrentItem(provider_item)
        QApplication.processEvents()

        # Provider mode shows only that provider's services; the shop-only
        # panels (stock/transaction) stay hidden.
        title = _find_named_label(dialog, "shopDetailTitle")
        self.assertEqual(title.text(), provider)
        services_panel = dialog.findChild(QWidget, "shopServicesPanel")
        self.assertTrue(services_panel.isVisibleTo(dialog))
        mode_tabs = dialog.findChild(QTabWidget, "shopModeTabs")
        self.assertFalse(mode_tabs.isVisibleTo(dialog))
        service_list = _find_named_list(dialog, "shopServiceList")
        for index in range(service_list.count()):
            payload = service_list.item(index).data(Qt.ItemDataRole.UserRole)
            self.assertIsInstance(payload, dict)
            source_kind = payload.get("kind")
            row_id = payload.get("id")
            self.assertEqual(source_kind, "vendor_action")
            self.assertEqual(str(SHOP_VENDOR_ACTIONS[row_id]["provider"]), provider)

    def test_shop_service_and_vendor_actions_apply_and_feed_global_history(self) -> None:
        from shop_fixtures import build_shop_frontend_fixtures
        from shop_data import SHOP_VENDOR_ACTIONS

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        vendor_action_id = fixtures["vendor_action_transaction"]["action_id"]
        dialog = self._open(pd)
        _open_shop_tab(dialog)

        service_list = _find_named_list(dialog, "shopServiceList")

        def _select_service_row(row_id: str) -> None:
            for index in range(service_list.count()):
                item = service_list.item(index)
                payload = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(payload, dict) and payload.get("id") == row_id:
                    service_list.setCurrentItem(item)
                    QApplication.processEvents()
                    return
            raise AssertionError(f"service/vendor row {row_id!r} not found")

        _select_service_row("bartender_sell_beer_glass")
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        before_glass = pd["inventory"]["Beer glass"]
        before_coins = pd["inventory"]["Coins"]
        self.assertTrue(use_button.isEnabled(), _find_named_label(dialog, "shopServicePreviewLabel").text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Beer glass"], before_glass - 1)
        self.assertGreater(pd["inventory"]["Coins"], before_coins)

        service_list = _find_named_list(dialog, "shopServiceList")
        _select_service_row(vendor_action_id)
        vendor_output = SHOP_VENDOR_ACTIONS[vendor_action_id]["outputs"][0]
        vendor_output_name = vendor_output["item_name"]
        vendor_output_quantity = int(vendor_output["quantity"])
        before_vendor_output = pd["inventory"].get(vendor_output_name, 0)
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), _find_named_label(dialog, "shopServicePreviewLabel").text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"].get(vendor_output_name, 0), before_vendor_output + vendor_output_quantity)

        global_button = _find_named_button(dialog, "shopGlobalHistoryButton")
        global_button.click()
        QApplication.processEvents()
        global_history = _find_named_list(dialog, "shopGlobalHistoryList")
        history_texts = _list_texts(global_history)
        self.assertTrue(any("Completed" in text for text in history_texts), history_texts)

    def test_achievement_tab_renders_metadata_counts_and_completed_rows(self) -> None:
        pd = _make_player_data()
        pd["completed_achievements"] = ["First Steps", "Rune Mysteries"]
        dialog = self._open(pd)
        labels = [label.text() for label in dialog.findChildren(QLabel)]

        self.assertTrue(
            any(text.startswith("Easy") and "2/40 completed" in text for text in labels),
            "Easy achievement count did not use metadata grouping",
        )
        self.assertIn("First Steps", labels)
        self.assertIn("Rune Mysteries", labels)
        self.assertIn("Completed: 2/120 (1.7%)", labels)

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

    def test_combat_is_selectable_and_shows_simple_enemy_targets(self) -> None:
        pd = _make_player_data()
        pd["current_combat_target"] = "seagull"
        dialog = self._open(pd, current_skill="Combat")

        tree = _find_tree_with_user_role(dialog, "seagull")
        cow_calf = _tree_row(tree, "cow_calf")
        ram = _tree_row(tree, "ram")
        spider = _tree_row(tree, "spider")
        giant_spider = _tree_row(tree, "giant_spider")
        goblin_unarmed = _tree_row(tree, "goblin_level_2_unarmed")
        goblin_armed = _tree_row(tree, "goblin_level_2_armed")
        goblin_level_11 = _tree_row(tree, "goblin_level_11")
        farmer = _tree_row(tree, "farmer")
        highwayman = _tree_row(tree, "highwayman")
        barbarian_level_10 = _tree_row(tree, "barbarian_level_10")
        seagull = _tree_row(tree, "seagull")

        self.assertEqual(cow_calf.text(0), "Cow calf (Lvl 2)")
        self.assertIn("Cowhide", cow_calf.toolTip(0))
        self.assertEqual(ram.text(0), "Ram (Lvl 2)")
        self.assertEqual(spider.text(0), "Spider (Lvl 1)")
        self.assertIn("Gold charm x1 (5/200)", spider.toolTip(0))
        self.assertEqual(giant_spider.text(0), "Giant spider (Lvl 2)")
        self.assertIn("Air rune x4-6 (7/48)", giant_spider.toolTip(0))
        self.assertIn("Staff of air", giant_spider.toolTip(0))
        self.assertEqual(goblin_unarmed.text(0), "Goblin (unarmed) (Lvl 2)")
        self.assertIn("Bronze spear x1 (32/1024)", goblin_unarmed.toolTip(0))
        self.assertEqual(goblin_armed.text(0), "Goblin (armed) (Lvl 2)")
        self.assertIn("armed id", goblin_armed.toolTip(0))
        self.assertEqual(goblin_level_11.text(0), "Goblin (Lvl 11)")
        self.assertIn("Bronze javelin x5 (2/128)", goblin_level_11.toolTip(0))
        self.assertIn("Minor herb table (2/128)", goblin_level_11.toolTip(0))
        self.assertEqual(farmer.text(0), "Farmer (Lvl 7)")
        self.assertIn("Allotment seed table (27/128)", farmer.toolTip(0))
        self.assertEqual(highwayman.text(0), "Highwayman (Lvl 5)")
        self.assertIn("Cape x1", highwayman.toolTip(0))
        self.assertIn("Iron bolts x2-12 (1/20)", highwayman.toolTip(0))
        self.assertEqual(barbarian_level_10.text(0), "Barbarian (Lvl 10)")
        self.assertIn("Enemy LP: 180/180", barbarian_level_10.toolTip(0))
        self.assertIn("Law rune x2 (8/1024)", barbarian_level_10.toolTip(0))
        self.assertIn("barbarian_2hsword_lvl_10.plugin.kts", barbarian_level_10.toolTip(0))
        self.assertEqual(seagull.text(0), "Seagull (Lvl 2)")
        self.assertIn("seagull_level_2.plugin.kts", seagull.toolTip(0))
        self.assertEqual(tree.currentItem().data(0, Qt.ItemDataRole.UserRole), "seagull")

    def test_combat_sidebar_hides_combat_only_stat_skills(self) -> None:
        combat_button = next(b for b in self.dialog.findChildren(QPushButton) if b.text() == "Combat")
        combat_button.click()
        QApplication.processEvents()

        skill_list = next(
            lw for lw in self.dialog.findChildren(QListWidget)
            if any(lw.item(i).text() == "Combat" for i in range(lw.count()))
        )
        texts = [skill_list.item(i).text() for i in range(skill_list.count())]
        self.assertEqual(texts, ["Combat", "Magic", "Prayer", "Summoning"])
        for hidden in ("Attack", "Constitution", "Defense", "Ranged", "Strength"):
            self.assertNotIn(hidden, texts)

    def test_combat_death_possible_target_requires_confirmation(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_lifepoints": 20,
                "constitution_level": 10,
                "inventory": {},
                "combat_auto_eat_food": ["Shark"],
                "combat_supply_loadout": {},
            }
        )
        dialog = self._open(pd, current_skill="Combat")

        tree = _find_tree_with_user_role(dialog, "barbarian_level_10")
        barbarian = _tree_row(tree, "barbarian_level_10")
        original_question = self._ui.QMessageBox.question
        questions = []
        try:
            def _deny(*args, **kwargs):  # type: ignore[no-untyped-def]
                questions.append(args)
                return self._ui.QMessageBox.StandardButton.No

            self._ui.QMessageBox.question = _deny
            tree.itemClicked.emit(barbarian, 0)
            QApplication.processEvents()
            self.assertEqual(self._combat_calls, [])
            self.assertEqual(questions[0][1], "Confirm dangerous combat")
            self.assertIn("Death possible", questions[0][2])

            self._ui.QMessageBox.question = lambda *a, **k: self._ui.QMessageBox.StandardButton.Yes
            tree.itemClicked.emit(barbarian, 0)
            QApplication.processEvents()
            self.assertEqual(self._combat_calls[-1], "barbarian_level_10")
        finally:
            self._ui.QMessageBox.question = original_question

    def test_combat_derives_style_from_equipment_and_exposes_spell_on_equipment_tab(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "magic_standard",
                "current_combat_spell": "wind_strike",
                "magic_level": 10,
                "inventory": {"Air rune": 5, "Mind rune": 5},
                "equipment": {"weapon": "Staff"},
                "combat_supply_loadout": {"runes": {"Air rune": 1, "Mind rune": 1}},
            }
        )
        dialog = self._open(pd, current_skill="Combat")

        style_combo = dialog.findChild(QComboBox, "combatStyleCombo")
        spell_combo = dialog.findChild(QComboBox, "combatSpellCombo")
        mode_label = dialog.findChild(QLabel, "combatModeLabel")
        self.assertIsNone(style_combo)
        self.assertIsNotNone(spell_combo)
        self.assertIsNotNone(mode_label)
        self.assertIn("Magic", mode_label.text())
        self.assertEqual(spell_combo.currentData(), "wind_strike")
        self.assertEqual(spell_combo.currentText(), "Wind Strike")
        for spell_id in ("water_strike", "earth_strike", "fire_strike", "wind_bolt", "fire_blast", "fire_wave"):
            self.assertGreaterEqual(spell_combo.findData(spell_id), 0)

        tree = _find_tree_with_user_role(dialog, "chicken")
        chicken = _tree_row(tree, "chicken")
        self.assertIn("Spell: Wind Strike", chicken.toolTip(0))
        self.assertIn("Rune: Air rune x1; 1 loaded + 5 bank", chicken.toolTip(0))

        fire_index = spell_combo.findData("fire_strike")
        spell_combo.setCurrentIndex(fire_index)
        QApplication.processEvents()
        self.assertEqual(self._combat_spell_calls[-1], "fire_strike")

        fire_wave_index = spell_combo.findData("fire_wave")
        spell_combo.setCurrentIndex(fire_wave_index)
        QApplication.processEvents()
        self.assertEqual(self._combat_spell_calls[-1], "fire_wave")

    def test_ranged_weapon_exposes_attack_style_selector_and_wires_it(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "ranged_accurate",
                "equipment": {"weapon": "Shortbow"},
                "ranged_level": 20,
            }
        )
        dialog = self._open(pd, current_skill="Combat")

        style_combo = dialog.findChild(QComboBox, "combatStyleCombo")
        self.assertIsNotNone(style_combo, "ranged weapon should expose an attack-style selector")
        # Only ranged styles are offered (never melee/magic).
        # Ranged combo data is a (weapon_style, style_type) pair; ranged has no
        # per-hit stab/slash/crush choice, so style_type is always "auto".
        ids = [style_combo.itemData(i) for i in range(style_combo.count())]
        self.assertEqual(
            ids,
            [
                ("ranged_accurate", "auto"),
                ("ranged_rapid", "auto"),
                ("ranged_longrange", "auto"),
            ],
        )
        self.assertEqual(style_combo.currentData(), ("ranged_accurate", "auto"))
        # Selecting a style persists it via on_set_combat_style.
        style_combo.setCurrentIndex(ids.index(("ranged_rapid", "auto")))
        QApplication.processEvents()
        self.assertEqual(self._combat_style_calls[-1], ("ranged_rapid", "auto"))

    def test_melee_weapon_style_selector_offers_only_melee_styles(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "aggressive",
                "equipment": {"weapon": "Bronze longsword"},
            }
        )
        dialog = self._open(pd, current_skill="Combat")

        style_combo = dialog.findChild(QComboBox, "combatStyleCombo")
        self.assertIsNotNone(style_combo)
        # A longsword's four slots each carry their own attack type; the combo
        # data is a (weapon_style, style_type) pair per slot.
        ids = [style_combo.itemData(i) for i in range(style_combo.count())]
        self.assertEqual(
            ids,
            [
                ("accurate", "slash"),
                ("aggressive", "slash"),
                ("controlled", "stab"),
                ("defensive", "slash"),
            ],
        )
        self.assertEqual(style_combo.currentData(), ("aggressive", "slash"))
        style_combo.setCurrentIndex(ids.index(("defensive", "slash")))
        QApplication.processEvents()
        self.assertEqual(self._combat_style_calls[-1], ("defensive", "slash"))

    def test_combat_exposes_loadout_controls(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_auto_eat_threshold_percent": 55,
                "combat_auto_eat_food": ["Lobster", "Shrimps"],
                "combat_supply_loadout": {
                    "food": {"Lobster": 3},
                    "potions": {"Antipoison (1)": 1},
                    "ammo": {"Bronze arrows": 10},
                    "runes": {"Air rune": 5, "Mind rune": 5},
                },
            }
        )
        dialog = self._open(pd, current_skill="Combat")

        # The supply-mode summary and bank-run status moved into the carried-pack
        # section's Auto view; Refill was removed (supplies auto-refill at bank
        # runs) and Unload became a plain "Clear inventory" button.
        threshold_spin = dialog.findChild(QSpinBox, "combatAutoEatThresholdSpin")
        summary_label = dialog.findChild(QLabel, "combatLoadoutSummaryLabel")
        bank_run_label = dialog.findChild(QLabel, "combatBankRunLabel")
        clear_button = dialog.findChild(QPushButton, "combatClearInventoryButton")

        self.assertIsNotNone(threshold_spin)
        self.assertIsNone(dialog.findChild(QComboBox, "combatFoodCombo"))
        self.assertIsNotNone(summary_label)
        self.assertIsNotNone(bank_run_label)
        self.assertIsNotNone(clear_button)
        self.assertIsNone(dialog.findChild(QPushButton, "combatRefillLoadoutButton"))
        self.assertEqual(threshold_spin.value(), 55)
        self.assertIn("Food: 3 loaded", summary_label.text())
        self.assertIn("Potions: Antipoison (1) x1", summary_label.text())
        self.assertIn("Ammo: Bronze arrows x10", summary_label.text())
        self.assertIn("Runes: Air rune x5, Mind rune x5", summary_label.text())
        self.assertIn("ready", bank_run_label.text())

        threshold_spin.setValue(60)
        QApplication.processEvents()
        self.assertEqual(self._combat_threshold_calls[-1], 60)

        clear_button.click()
        QApplication.processEvents()
        self.assertEqual(self._combat_unload_calls, [True])

    def test_fishing_is_selectable_and_shows_output_first_target_list(self) -> None:
        pd = _make_player_data()
        pd["fishing_level"] = 48
        pd["strength_level"] = 15
        pd["agility_level"] = 15
        pd["inventory"] = {"Fishing bait": 2, "Feather": 1}
        pd["current_fishing"] = "catch_sardine_herring"
        dialog = self._open(pd)

        skill_list = _find_skill_list(dialog)
        fishing_row = next(
            (i for i in range(skill_list.count()) if skill_list.item(i).text() == "Fishing"),
            None,
        )
        self.assertIsNotNone(fishing_row, "Fishing is missing from the Gathering skill list")
        skill_list.setCurrentRow(fishing_row)
        QApplication.processEvents()

        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Fishing"),
            f"panel did not switch to Fishing; still shows {title!r}",
        )
        target_list = _find_list_with_user_role(dialog, "catch_sardine_herring")
        sardine_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_sardine_herring"
        )
        mackerel_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_mackerel_cod_bass"
        )
        crayfish_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_crayfish"
        )

        self.assertTrue(crayfish_row.text().startswith("Catch crayfish"))
        self.assertEqual(sardine_row.text(), "Catch sardine (Lvl 5)/herring (Lvl 10)")
        self.assertEqual(mackerel_row.text(), "Catch mackerel (Lvl 16)/cod (Lvl 23)/bass (Lvl 46)")
        tip = sardine_row.toolTip()
        self.assertIn("Outputs: Raw sardine", tip)
        self.assertIn("Raw herring", tip)
        self.assertIn("Base XP: 20-30 per catch", tip)
        self.assertIn("Materials: Fishing bait x1 (you have 2)", tip)
        self.assertNotIn("rod", tip.lower())
        self.assertNotIn("net", tip.lower())
        self.assertNotIn("harpoon", tip.lower())

        target_list.itemClicked.emit(crayfish_row)
        QApplication.processEvents()
        self.assertEqual(self._fishing_calls[-1], "catch_crayfish")

    def test_fishing_locked_rows_are_inert_and_explain_material_or_side_gate(self) -> None:
        pd = _make_player_data()
        pd["fishing_level"] = 48
        pd["strength_level"] = 1
        pd["agility_level"] = 1
        pd["inventory"] = {}
        dialog = self._open(pd)

        skill_list = _find_skill_list(dialog)
        fishing_row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Fishing")
        skill_list.setCurrentRow(fishing_row)
        QApplication.processEvents()
        target_list = _find_list_with_user_role(dialog, "catch_sardine_herring")
        bait_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_sardine_herring"
        )
        leaping_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_leaping_fish"
        )

        self.assertFalse(bait_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("materials", bait_row.toolTip())
        self.assertFalse(leaping_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("side levels", leaping_row.toolTip())
        target_list.itemClicked.emit(bait_row)
        target_list.itemClicked.emit(leaping_row)
        QApplication.processEvents()
        self.assertEqual(self._fishing_calls, [])

    def test_hunter_is_selectable_and_shows_grouped_source_targets(self) -> None:
        pd = _make_player_data()
        pd["hunter_level"] = 99
        pd["inventory"] = {"Logs": 1, "Impling jar": 1}
        pd["current_hunter"] = "catch_wild_kebbit"
        dialog = self._open(pd)
        tree = _goto_hunter(dialog)

        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Hunter"),
            f"panel did not switch to Hunter; still shows {title!r}",
        )
        group_roles = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__hunter_group__:bird_snaring", group_roles)
        self.assertIn("__hunter_group__:deadfall", group_roles)
        self.assertIn("__hunter_group__:impling_world", group_roles)
        self.assertEqual(_hunter_group_node(tree, "deadfall").text(0), "Deadfall  (4)")

        wild = _hunter_row(tree, "catch_wild_kebbit")
        ferret = _hunter_row(tree, "catch_ferret")
        pirate = _hunter_row(tree, "catch_pirate_impling_world")
        self.assertIs(wild, tree.currentItem())
        self.assertFalse(wild.isDisabled())
        self.assertFalse(wild.icon(0).isNull(), "Hunter target row has no icon")
        self.assertIn("Outputs: Bones x1, Kebbit claws x1", wild.toolTip(0))
        self.assertIn("Base XP: 128.0 per successful catch", wild.toolTip(0))
        self.assertIn("Success chance:", wild.toolTip(0))
        self.assertIn("Logs x1 (you have 1)", wild.toolTip(0))
        self.assertTrue(ferret.isDisabled())
        self.assertIn("Eagles' Peak", ferret.toolTip(0))
        self.assertTrue(pirate.isDisabled())
        self.assertIn("Rocking Out", pirate.toolTip(0))

        before = list(self._hunter_calls)
        tree.itemClicked.emit(ferret, 0)
        QApplication.processEvents()
        self.assertEqual(self._hunter_calls, before, "quest-locked hunter target must not be selectable")

        tree.itemClicked.emit(wild, 0)
        QApplication.processEvents()
        self.assertEqual(self._hunter_calls[-1], "catch_wild_kebbit")

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

    def test_fletching_is_selectable_and_shows_grouped_target_tree(self) -> None:
        pd = _make_player_data()
        pd["fletching_level"] = 99
        pd["inventory"] = {"Logs": 1, "Headless arrows": 15, "Broad arrow heads": 15}
        pd["current_fletch"] = "arrow_shafts"
        dialog = self._open(pd)

        artisan = next(b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        fletch_row = next(
            (i for i in range(skill_list.count()) if skill_list.item(i).text() == "Fletching"),
            None,
        )
        self.assertIsNotNone(fletch_row, "Fletching is missing from the Artisan skill list")
        skill_list.setCurrentRow(fletch_row)
        QApplication.processEvents()
        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Fletching"),
            f"panel did not switch to Fletching; still shows {title!r}",
        )
        tree = _find_fletching_tree(dialog)
        self.assertEqual(_fletching_group_node(tree, "whittling").text(0), "Whittling  (20)")
        self.assertIs(_fletching_row(tree, "arrow_shafts"), tree.currentItem())
        self.assertFalse(_fletching_row(tree, "arrow_shafts").isDisabled())
        broad = _fletching_row(tree, "broad_arrows")
        self.assertTrue(broad.isDisabled())
        self.assertIn("Broad Fletching", broad.toolTip(0))

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

    def test_firemaking_region_quest_locks_are_inert(self) -> None:
        pd = _make_player_data()
        pd["firemaking_level"] = 99
        pd["inventory"] = {"Arctic pine logs": 1}
        pd["current_firemaking"] = "arctic_pine_logs"
        dialog = self._open(pd)
        artisan = next(b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        fm_row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Firemaking")
        skill_list.setCurrentRow(fm_row)
        QApplication.processEvents()
        target_list = _find_list_with_user_role(dialog, "arctic_pine_logs")
        arctic_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "arctic_pine_logs"
        )

        self.assertFalse(arctic_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("The Fremennik Isles", arctic_row.toolTip())
        target_list.itemClicked.emit(arctic_row)
        QApplication.processEvents()
        self.assertEqual(self._firemaking_calls, [])

        pd["quests"]["the_fremennik_isles"] = {"started": True, "progress": 6, "completed": True}
        unlocked_dialog = self._open(pd)
        artisan = next(b for b in unlocked_dialog.findChildren(QPushButton) if b.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        unlocked_skill_list = _find_artisan_skill_list(unlocked_dialog)
        unlocked_fm_row = next(i for i in range(unlocked_skill_list.count()) if unlocked_skill_list.item(i).text() == "Firemaking")
        unlocked_skill_list.setCurrentRow(unlocked_fm_row)
        QApplication.processEvents()
        unlocked_list = _find_list_with_user_role(unlocked_dialog, "arctic_pine_logs")
        unlocked_arctic = next(
            unlocked_list.item(i) for i in range(unlocked_list.count())
            if unlocked_list.item(i).data(Qt.ItemDataRole.UserRole) == "arctic_pine_logs"
        )
        self.assertTrue(unlocked_arctic.flags() & Qt.ItemFlag.ItemIsEnabled)

    def test_cooking_is_selectable_and_shows_grouped_source_targets(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 33
        pd["inventory"] = {"Raw shrimps": 2}
        pd["current_cooking"] = "cook_shrimps"
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)
        skill_list = _find_artisan_skill_list(dialog)
        cooking_item = next(
            skill_list.item(i)
            for i in range(skill_list.count())
            if skill_list.item(i).text() == "Cooking"
        )
        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Cooking"),
            f"panel did not switch to Cooking; still shows {title!r}",
        )
        self.assertFalse(cooking_item.icon().isNull(), "Cooking skill row has no icon")
        self.assertEqual(
            _icon_pixels(cooking_item.icon()),
            _icon_pixels(QIcon(self._ui.skill_icon_path_for("Cooking"))),
            "Cooking skill row did not use icon/cooking_icon.png",
        )
        self.assertNotEqual(
            _icon_pixels(cooking_item.icon()),
            _icon_pixels(QIcon(os.path.join(_ADDON_DIR, "icon", "achievement_icon.png"))),
            "Cooking skill row fell back to the achievement icon",
        )

        family_roles = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__cooking_family__:fish", family_roles)
        self.assertIn("__cooking_family__:pies", family_roles)

        shrimps = _cooking_row(tree, "cook_shrimps")
        shark = _cooking_row(tree, "cook_shark")
        self.assertFalse(shrimps.isDisabled())
        self.assertFalse(shrimps.icon(0).isNull(), "Cooking target row has no icon")
        self.assertIn("Success output: Shrimps x1", shrimps.toolTip(0))
        self.assertIn("Burn output: Burnt shrimp x1, no XP", shrimps.toolTip(0))
        self.assertIn("Success chance:", shrimps.toolTip(0))
        self.assertTrue(shark.isDisabled())
        self.assertIn("Locked due to:", shark.toolTip(0))

        tree.itemClicked.emit(shrimps, 0)
        QApplication.processEvents()
        self.assertEqual(self._cooking_calls[-1], "cook_shrimps")
        self.assertTrue(_cooking_family_node(tree, "fish").isExpanded())

    def test_cooking_locked_rows_are_inert(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 1
        pd["inventory"] = {"Raw beef": 1}
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)
        locked = _cooking_row(tree, "cook_shrimps")
        self.assertTrue(locked.isDisabled())
        before = list(self._cooking_calls)
        tree.itemClicked.emit(locked, 0)
        tree.itemActivated.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._cooking_calls, before, "locked cooking target must not be selectable")

    def test_lava_eel_row_uses_existing_quest_asset_and_never_burns(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 53
        pd["inventory"] = {"Raw lava eel": 1}
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)

        lava_eel = _cooking_row(tree, "cook_lava_eel")
        self.assertFalse(lava_eel.isDisabled())
        self.assertFalse(lava_eel.icon(0).isNull())
        self.assertIn("Cannot burn or fail.", lava_eel.toolTip(0))
        self.assertIn("Success chance: 100%", lava_eel.toolTip(0))

    def test_cooking_region_quest_locks_are_inert(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 99
        pd["inventory"] = {"Slimy eel": 1, "Raw yak meat": 1}
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)

        slimy_eel = _cooking_row(tree, "cook_slimy_eel")
        yak = _cooking_row(tree, "cook_yak")
        self.assertTrue(slimy_eel.isDisabled())
        self.assertIn("Priest in Peril", slimy_eel.toolTip(0))
        self.assertTrue(yak.isDisabled())
        self.assertIn("The Fremennik Isles", yak.toolTip(0))

        before = list(self._cooking_calls)
        tree.itemClicked.emit(slimy_eel, 0)
        tree.itemActivated.emit(yak, 0)
        QApplication.processEvents()
        self.assertEqual(self._cooking_calls, before, "quest-locked cooking rows must not be selectable")

        pd["quests"]["priest_in_peril"] = {"started": True, "progress": 6, "completed": True}
        pd["quests"]["the_fremennik_isles"] = {"started": True, "progress": 6, "completed": True}
        unlocked_dialog = self._open(pd)
        unlocked_tree = _goto_cooking(unlocked_dialog)
        self.assertFalse(_cooking_row(unlocked_tree, "cook_slimy_eel").isDisabled())
        self.assertFalse(_cooking_row(unlocked_tree, "cook_yak").isDisabled())

    def test_runecrafting_is_selectable_and_shows_grouped_targets(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 23
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        pd["inventory"] = {
            "Rune essence": 31,
            "Air talisman": 1,
            "Pure essence": 26,
            "Fire rune": 26,
            "Fire talisman": 1,
        }
        pd["equipment"] = {"head": "Earth tiara"}
        dialog = self._open(pd)
        tree = _goto_runecrafting(dialog)

        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Runecrafting"),
            f"panel did not switch to Runecrafting; still shows {title!r}",
        )
        group_roles = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__runecrafting_group__:standard", group_roles)
        self.assertIn("__runecrafting_group__:combination", group_roles)
        self.assertIn("__runecrafting_group__:tiara", group_roles)
        self.assertIn("__runecrafting_group__:hood", group_roles)

        air = _runecrafting_row(tree, "craft_air_runes")
        lava = _runecrafting_row(tree, "combo_lava_at_earth")
        blood = _runecrafting_row(tree, "craft_blood_runes")
        self.assertFalse(air.isDisabled())
        self.assertFalse(lava.isDisabled())
        self.assertTrue(blood.isDisabled())
        self.assertFalse(air.icon(0).isNull(), "Runecrafting target row has no icon")
        self.assertIn("Output: Air rune", air.toolTip(0))
        self.assertIn("Pure essence", lava.toolTip(0))
        self.assertIn("Locked due to:", blood.toolTip(0))

        tree.itemClicked.emit(air, 0)
        QApplication.processEvents()
        self.assertEqual(self._runecrafting_calls[-1], "craft_air_runes")

    def test_runecrafting_locked_rows_are_inert(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 1
        pd["inventory"] = {"Rune essence": 28}
        dialog = self._open(pd)
        tree = _goto_runecrafting(dialog)
        air = _runecrafting_row(tree, "craft_air_runes")

        self.assertTrue(air.isDisabled())
        self.assertIn("Rune Mysteries", air.toolTip(0))
        before = list(self._runecrafting_calls)
        tree.itemClicked.emit(air, 0)
        tree.itemActivated.emit(air, 0)
        QApplication.processEvents()
        self.assertEqual(self._runecrafting_calls, before, "locked runecrafting target must not be selectable")

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

    def test_stats_tab_has_fishing_and_shows_its_details(self) -> None:
        btn = _find_tool_button(self.dialog, "Fishing")
        btn.click()
        QApplication.processEvents()
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn("Fishing Stats", labels)
        self.assertIn("Fishing Level:", labels)

    def test_stats_tab_has_runecrafting_and_shows_its_details(self) -> None:
        btn = _find_tool_button(self.dialog, "Runecrafting")
        btn.click()
        QApplication.processEvents()
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn("Runecrafting Stats", labels)
        self.assertIn("Runecrafting Level:", labels)

    def test_quests_tab_starts_rune_mysteries_via_quest_action(self) -> None:
        pd = _make_player_data()
        pd["quests"]["rune_mysteries"] = {"started": False, "progress": 0, "completed": False}
        dialog = self._open(pd)
        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Rune Mysteries", labels)
        self.assertIn("Quest points: 0", labels)

        start_btn = dialog.findChild(QPushButton, "questAction_rune_mysteries")
        self.assertIsNotNone(start_btn)
        start_btn.click()
        QApplication.processEvents()
        self.assertEqual(self._quest_calls[-1], "rune_mysteries")
        self.assertEqual(start_btn.text(), "Currently active")
        self.assertFalse(start_btn.isEnabled())

    def test_quests_tab_defaults_release_sort_and_collapses_completed_journals(self) -> None:
        pd = _make_player_data()
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        dialog = self._open(pd)

        sort_combo = dialog.findChild(QComboBox, "questSortCombo")
        self.assertIsNotNone(sort_combo)
        self.assertEqual(sort_combo.currentText(), "Release Order")
        self.assertIn("Difficulty", [sort_combo.itemText(i) for i in range(sort_combo.count())])
        self.assertIn("Length", [sort_combo.itemText(i) for i in range(sort_combo.count())])
        quest_cards = [
            widget for widget in dialog.findChildren(QWidget)
            if widget.objectName().startswith("questCard_")
        ]
        self.assertGreaterEqual(len(quest_cards), 194)

        body = dialog.findChild(QWidget, "questBody_rune_mysteries")
        toggle = dialog.findChild(QPushButton, "questToggle_rune_mysteries")
        self.assertIsNotNone(body)
        self.assertIsNotNone(toggle)
        self.assertTrue(body.isHidden())
        toggle.click()
        QApplication.processEvents()
        self.assertFalse(body.isHidden())

    def test_quests_tab_filters_completed_and_unable_to_start_cards(self) -> None:
        pd = _make_player_data()
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        dialog = self._open(pd)

        hide_completed = dialog.findChild(QCheckBox, "questHideCompletedCheck")
        hide_locked = dialog.findChild(QCheckBox, "questHideLockedCheck")
        summary = dialog.findChild(QLabel, "questFilterSummaryLabel")
        self.assertIsNotNone(hide_completed)
        self.assertIsNotNone(hide_locked)
        self.assertIsNotNone(summary)
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_rune_mysteries"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_lost_city"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))

        hide_completed.setChecked(True)
        QApplication.processEvents()
        self.assertIsNone(dialog.findChild(QWidget, "questCard_rune_mysteries"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_lost_city"))

        hide_locked.setChecked(True)
        QApplication.processEvents()
        self.assertIsNone(dialog.findChild(QWidget, "questCard_lost_city"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))
        self.assertRegex(summary.text(), r"^Showing \d+/194$")

    def test_quests_tab_shows_stage_blockers_without_hiding_started_quests(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "the_knights_sword"
        pd["quests"]["the_knights_sword"] = {"started": True, "progress": 2, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Needs Redberry pie x1", labels)
        action = dialog.findChild(QPushButton, "questAction_the_knights_sword")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Redberry pie x1", action.toolTip())

        hide_locked = dialog.findChild(QCheckBox, "questHideLockedCheck")
        self.assertIsNotNone(hide_locked)
        hide_locked.setChecked(True)
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_the_knights_sword"))

    def test_quests_tab_shows_shield_of_arrav_route_branch_blockers(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "shield_of_arrav"
        pd["quests"]["shield_of_arrav"] = {"started": True, "progress": 4, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Choose path: Phoenix Gang or Black Arm Gang"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_shield_of_arrav")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Phoenix Gang", action.toolTip())
        phoenix = dialog.findChild(QPushButton, "questChoice_shield_of_arrav_join_the_phoenix_gang")
        black_arm = dialog.findChild(QPushButton, "questChoice_shield_of_arrav_join_the_black_arm_gang")
        self.assertIsNotNone(phoenix)
        self.assertIsNotNone(black_arm)
        self.assertEqual(phoenix.text(), "Phoenix Gang")
        self.assertEqual(black_arm.text(), "Black Arm Gang")
        black_arm.click()
        QApplication.processEvents()
        self.assertEqual(self._quest_choice_calls[-1], ("shield_of_arrav", "Join the Black Arm Gang"))

    def test_quests_tab_shows_shield_black_arm_contextual_contact_combat_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "shield_of_arrav"
        pd["quests"]["shield_of_arrav"] = {"started": True, "progress": 5, "completed": False}
        pd["quest_route_states"] = {"shield_of_arrav": ["Join the Black Arm Gang"]}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertTrue(all("Needs Weapon store key" not in label for label in labels))
        action = dialog.findChild(QPushButton, "questAction_shield_of_arrav")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertNotIn("Needs Weapon store key", action.toolTip())
        self.assertNotIn("Phoenix Gang partner", action.toolTip())
        self.assertNotIn("Use the weapon store key", action.toolTip())
        self.assertIn("Weaponsmaster level 23", action.toolTip())

    def test_quests_tab_shows_hazeel_side_choice_before_start(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "hazeel_cult"
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Choose path: Ceril Carnillean or Hazeel's cult", labels)
        action = dialog.findChild(QPushButton, "questAction_hazeel_cult")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Hazeel's cult", action.toolTip())
        cult = dialog.findChild(QPushButton, "questChoice_hazeel_cult_side_with_hazeel_s_cult")
        self.assertIsNotNone(cult)
        self.assertEqual(cult.text(), "Hazeel's cult")
        cult.click()
        QApplication.processEvents()
        self.assertEqual(self._quest_choice_calls[-1], ("hazeel_cult", "Side with Hazeel's cult"))

    def test_quests_tab_shows_demon_slayer_item_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "demon_slayer"
        pd["quests"]["demon_slayer"] = {"started": True, "progress": 3, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Bucket of water x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_demon_slayer")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Bucket of water x1", action.toolTip())

    def test_quests_tab_shows_ernest_machine_part_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "ernest_the_chicken"
        pd["quests"]["ernest_the_chicken"] = {"started": True, "progress": 3, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Fish food x1, Needs Poison x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_ernest_the_chicken")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Fish food x1", action.toolTip())

    def test_quests_tab_shows_dragon_slayer_oracle_item_option_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Wizard's mind bomb": 1,
            "Silk": 1,
            "Bowl (unfired)": 1,
        }
        pd["current_quest"] = "dragon_slayer"
        pd["quests"]["dragon_slayer"] = {"started": True, "progress": 8, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Crayfish cage x1 or Lobster pot x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_dragon_slayer")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Crayfish cage x1 or Lobster pot x1", action.toolTip())

    def test_quests_tab_shows_fishing_contest_current_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Fishing rod": 1}
        pd["current_quest"] = "fishing_contest"
        pd["quests"]["fishing_contest"] = {"started": True, "progress": 4, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Needs Red vine worm x1 or Fishing bait x1, "
            "Action required: Catch the winning giant carp"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_fishing_contest")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Catch the winning giant carp", action.toolTip())

    def test_quests_tab_shows_sheep_herder_produced_bones_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Sheep feed": 1, "Plague jacket": 1, "Plague trousers": 1, "Cattleprod": 1}
        pd["current_quest"] = "sheep_herder"
        pd["quests"]["sheep_herder"] = {"started": True, "progress": 4, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Herd and poison the red sheep, "
            "Action required: Herd and poison the green sheep, "
            "Action required: Herd and poison the blue sheep, +2 more"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_sheep_herder")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Action required: Herd and poison the red sheep", action.toolTip())
        self.assertIn("+2 more", action.toolTip())

    def test_quests_tab_shows_plague_city_hangover_cure_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bucket of milk": 1}
        pd["current_quest"] = "plague_city"
        pd["quests"]["plague_city"] = {"started": True, "progress": 14, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Needs Chocolate dust x1, Needs Snape grass x1, "
            "Needs Pestle and mortar, +1 more"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_plague_city")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Chocolate dust x1", action.toolTip())
        self.assertIn("+1 more", action.toolTip())

    def test_quests_tab_shows_biohazard_guidor_disguise_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Liquid honey": 1,
            "Ethenea": 1,
            "Sulphuric broline": 1,
            "Plague sample": 1,
            "Touch paper": 1,
        }
        pd["current_quest"] = "biohazard"
        pd["quests"]["biohazard"] = {"started": True, "progress": 11, "completed": False}
        pd["quest_route_states"] = {
            "biohazard": ["Reach Guidor's house without Varrock guards confiscating the vials"]
        }
        pd["quest_stage_actions"] = {
            "biohazard": [
                "Give sulphuric broline to Hops",
                "Give ethenea to Da Vinci",
                "Give liquid honey to Chancy",
                "Collect the sulphuric broline from Hops in Varrock",
                "Collect the ethenea from Da Vinci in Varrock",
                "Collect the liquid honey from Chancy in Varrock",
                "Enter Guidor's room wearing priest gowns",
                "Give Guidor the vials, plague sample, and touch paper",
            ]
        }
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Needs Priest gown x2", labels)
        action = dialog.findChild(QPushButton, "questAction_biohazard")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Priest gown x2", action.toolTip())

    def test_quests_tab_shows_heroes_black_arm_disguise_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Id papers": 1}
        pd["equipment"] = {"head": "Black full helm", "body": "Black platebody"}
        pd["current_quest"] = "heroes_quest"
        pd["quests"]["heroes_quest"] = {"started": True, "progress": 10, "completed": False}
        pd["quest_route_states"] = {"heroes_quest": ["Join the Black Arm Gang"]}
        pd["quest_stage_actions"] = {
            "heroes_quest": ["Show the Id papers to Garv", "Search Scarface Pete's candlestick chest"]
        }
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Needs Black platelegs", labels)
        action = dialog.findChild(QPushButton, "questAction_heroes_quest")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Black platelegs", action.toolTip())

    def test_quests_tab_shows_family_crest_jewellery_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Perfect gold bar": 2,
            "Ruby": 1,
            "Ring mould": 1,
            "Necklace mould": 1,
        }
        pd["current_quest"] = "family_crest"
        pd["quests"]["family_crest"] = {"started": True, "progress": 10, "completed": False}
        pd["quest_stage_actions"] = {
            "family_crest": ["Craft the perfect ruby ring and perfect ruby necklace"]
        }
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Needs Ruby x2", labels)
        action = dialog.findChild(QPushButton, "questAction_family_crest")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Ruby x2", action.toolTip())

    def test_quests_tab_shows_temple_of_ikov_fire_warrior_bow_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Ice arrows": 1}
        pd["current_quest"] = "temple_of_ikov"
        pd["quests"]["temple_of_ikov"] = {"started": True, "progress": 7, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected_prefix = "Blocked: Needs Yew shortbow x1 or Yew longbow x1"
        self.assertTrue(
            any(label.startswith(expected_prefix) for label in labels),
            f"Expected Temple bow blocker in labels: {labels}",
        )
        action = dialog.findChild(QPushButton, "questAction_temple_of_ikov")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Yew shortbow x1", action.toolTip())

    def test_quests_tab_shows_holy_grail_excalibur_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Magic whistle": 1}
        pd["current_quest"] = "holy_grail"
        pd["quests"]["holy_grail"] = {"started": True, "progress": 5, "completed": False}
        pd["quest_route_states"] = {"holy_grail": ["Reach the Fisher Realm crossing at the six stone heads"]}
        pd["quest_stage_actions"] = {"holy_grail": ["Blow the Magic whistle at the six stone heads"]}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertTrue(
            any(label.startswith("Blocked: Needs Excalibur") for label in labels),
            f"Expected Holy Grail Excalibur blocker in labels: {labels}",
        )
        action = dialog.findChild(QPushButton, "questAction_holy_grail")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Excalibur", action.toolTip())

    def test_quests_tab_allows_resolver_ready_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Stake": 1, "Stake hammer": 1}
        pd["current_quest"] = "vampyre_slayer"
        pd["quests"]["vampyre_slayer"] = {"started": True, "progress": 3, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 40
        pd["strength_level"] = 40
        pd["defense_level"] = 35
        pd["constitution_level"] = 40
        pd["prayer_level"] = 20
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Count Draynor level 37"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_vampyre_slayer")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("vampyre_slayer", self._quest_calls)

    def test_quests_tab_shows_cooks_assistant_container_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "cooks_assistant"
        pd["quests"]["cooks_assistant"] = {"started": True, "progress": 1, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertNotIn(
            "Blocked: Needs Top-quality milk x1, Needs Extra fine flour x1, Needs Super large egg x1",
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_cooks_assistant")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        dialog.close()
        pd = _make_player_data()
        pd["current_quest"] = "cooks_assistant"
        pd["quests"]["cooks_assistant"] = {"started": True, "progress": 2, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn(
            "Blocked: Needs Bucket x1",
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_cooks_assistant")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Bucket x1", action.toolTip())

    def test_quests_tab_shows_witchs_house_mouse_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Magnet": 1}
        pd["current_quest"] = "witchs_house"
        pd["quests"]["witchs_house"] = {"started": True, "progress": 4, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Needs Cheese x1, "
            "Action required: Use cheese on the mouse hole and attach the magnet to the mouse"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_witchs_house")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Needs Cheese x1", action.toolTip())
        self.assertIn("Use cheese on the mouse hole", action.toolTip())

    def test_quests_tab_shows_merlins_crystal_wax_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bucket": 1}
        pd["current_quest"] = "merlins_crystal"
        pd["quests"]["merlins_crystal"] = {"started": True, "progress": 4, "completed": False}
        pd["quest_stage_actions"] = {
            "merlins_crystal": ["Question Morgan Le Faye about Excalibur and the binding words"]
        }
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Insect repellent x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_merlins_crystal")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Insect repellent x1", action.toolTip())

    def test_quests_tab_allows_demon_slayer_source_backed_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Silverlight": 1}
        pd["current_quest"] = "demon_slayer"
        pd["quests"]["demon_slayer"] = {"started": True, "progress": 7, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 30
        pd["strength_level"] = 30
        pd["defense_level"] = 30
        pd["constitution_level"] = 30
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Delrith level 27"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_demon_slayer")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("demon_slayer", self._quest_calls)

    def test_quests_tab_allows_merlins_crystal_mordred_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "merlins_crystal"
        pd["quests"]["merlins_crystal"] = {"started": True, "progress": 3, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 50
        pd["strength_level"] = 50
        pd["defense_level"] = 50
        pd["constitution_level"] = 50
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Sir Mordred level 39"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_merlins_crystal")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("merlins_crystal", self._quest_calls)

    def test_quests_tab_allows_dragon_slayer_elvarg_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Anti-dragon shield": 1}
        pd["current_quest"] = "dragon_slayer"
        pd["quests"]["dragon_slayer"] = {"started": True, "progress": 14, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 99
        pd["strength_level"] = 99
        pd["defense_level"] = 99
        pd["constitution_level"] = 99
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Elvarg level 83"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_dragon_slayer")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("dragon_slayer", self._quest_calls)

    def test_quests_tab_allows_identical_source_generated_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "elemental_workshop_i"
        pd["inventory"].update({"Thread": 1, "Leather": 1})
        pd["quests"]["elemental_workshop_i"] = {"started": True, "progress": 2, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 40
        pd["strength_level"] = 40
        pd["defense_level"] = 40
        pd["constitution_level"] = 40
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete Elemental Workshop I stage 2 objective, "
            "Battle required: Earth Elemental level 35"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_elemental_workshop_i")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("elemental_workshop_i", self._quest_calls)

    def test_quests_tab_allows_beast_fallback_ranged_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "toktz_ket_dill"
        pd["quests"]["toktz_ket_dill"] = {"started": True, "progress": 6, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 50
        pd["strength_level"] = 50
        pd["defense_level"] = 50
        pd["constitution_level"] = 50
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete TokTz-Ket-Dill stage 6 objective, "
            "Combat stats required before battle support can resolve: TokTz-Ket-Dill level 100, "
            "Battle required: Lava monster level 47 x2, +1 more"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_toktz_ket_dill")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("toktz_ket_dill", self._quest_calls)

    def test_quests_tab_allows_no_combat_levels_beast_stat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "forgiveness_of_a_chaos_dwarf"
        pd["quests"]["forgiveness_of_a_chaos_dwarf"] = {"started": True, "progress": 4, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 80
        pd["strength_level"] = 80
        pd["defense_level"] = 80
        pd["constitution_level"] = 80
        pd["prayer_level"] = 80
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Chaos dwarf hand cannoneer level 100"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_forgiveness_of_a_chaos_dwarf")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("forgiveness_of_a_chaos_dwarf", self._quest_calls)

    def test_quests_tab_shows_remaining_combat_quantity_after_partial_resolution(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "toktz_ket_dill"
        pd["quests"]["toktz_ket_dill"] = {"started": True, "progress": 6, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["quest_combat_encounter_counts"] = {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 1}}
        pd["attack_level"] = 50
        pd["strength_level"] = 50
        pd["defense_level"] = 50
        pd["constitution_level"] = 50
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete TokTz-Ket-Dill stage 6 objective, "
            "Combat stats required before battle support can resolve: TokTz-Ket-Dill level 100, "
            "Battle required: Lava monster level 47, +1 more"
        )
        self.assertIn(expected, labels)

    def test_quests_tab_keeps_historical_metadata_only_combat_rows_blocked(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "fight_arena"
        pd["quests"]["fight_arena"] = {"started": True, "progress": 8, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 150
        pd["strength_level"] = 150
        pd["defense_level"] = 150
        pd["constitution_level"] = 150
        pd["prayer_level"] = 150
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Combat stats required before battle support can resolve: Khazard ogre level 63"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_fight_arena")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())

    def test_quests_tab_allows_fight_arena_bouncer_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "fight_arena"
        pd["quests"]["fight_arena"] = {"started": True, "progress": 10, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["quest_combat_encounters"] = {
            "fight_arena": ["fight_arena_khazard_ogre_63", "fight_arena_khazard_scorpion_44"]
        }
        pd["attack_level"] = 150
        pd["strength_level"] = 150
        pd["defense_level"] = 150
        pd["constitution_level"] = 150
        pd["prayer_level"] = 150
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Bouncer level 137"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_fight_arena")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

    def test_quests_tab_allows_witchs_house_form_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "witchs_house"
        pd["quests"]["witchs_house"] = {"started": True, "progress": 9, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 60
        pd["strength_level"] = 60
        pd["defense_level"] = 60
        pd["constitution_level"] = 60
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Battle required: Witch's experiment (Skavid form) level 19, "
            "Battle required: Witch's experiment (Spider form) level 30, "
            "Battle required: Witch's experiment (Bear form) level 42, +1 more"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_witchs_house")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("witchs_house", self._quest_calls)

    def test_quests_tab_allows_style_aware_magic_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "another_slice_of_h_a_m"
        pd["quests"]["another_slice_of_h_a_m"] = {"started": True, "progress": 4, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["quest_combat_encounters"] = {"another_slice_of_h_a_m": ["another_slice_of_h_a_m_sigmund_64"]}
        pd["attack_level"] = 40
        pd["strength_level"] = 40
        pd["defense_level"] = 40
        pd["constitution_level"] = 40
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete Another Slice of H.A.M. stage 4 objective, "
            "Battle required: H.A.M. mage level 30, "
            "Battle required: H.A.M. ranger level 30"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_another_slice_of_h_a_m")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("another_slice_of_h_a_m", self._quest_calls)

    def test_quests_tab_shows_split_golem_combat_gates(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "spirits_of_the_elid"
        pd["quests"]["spirits_of_the_elid"] = {"started": True, "progress": 4, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 90
        pd["strength_level"] = 90
        pd["defense_level"] = 90
        pd["constitution_level"] = 90
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete Spirits of the Elid stage 4 objective, "
            "Battle required: Black golem level 75, "
            "Battle required: White golem level 75, +1 more"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_spirits_of_the_elid")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("spirits_of_the_elid", self._quest_calls)

    def test_quests_tab_shows_a_souls_bane_split_combat_gates(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "a_souls_bane"
        pd["quests"]["a_souls_bane"] = {"started": True, "progress": 3, "completed": False}
        pd["quest_stage_actions"] = {"a_souls_bane": ["Fill the rage meter with an anger weapon"]}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 100
        pd["strength_level"] = 100
        pd["defense_level"] = 100
        pd["constitution_level"] = 100
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Battle required: Fear reaper level 42 x5, "
            "Battle required: Confusion beast level 43 x5, "
            "Battle required: Hopeless creature level 40 x3"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_a_souls_bane")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("a_souls_bane", self._quest_calls)

    def test_quests_tab_allows_conflict_overridden_dad_combat_gate_selection(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Coins": 12}
        pd["current_quest"] = "troll_stronghold"
        pd["quests"]["troll_stronghold"] = {"started": True, "progress": 2, "completed": False}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["quest_combat_encounters"] = {
            "troll_stronghold": ["troll_stronghold_twig_troll_71", "troll_stronghold_troll_general_171"]
        }
        pd["attack_level"] = 100
        pd["strength_level"] = 100
        pd["defense_level"] = 100
        pd["constitution_level"] = 100
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = (
            "Blocked: Action required: Complete Troll Stronghold stage 2 objective, "
            "Battle required: Dad level 101"
        )
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_troll_stronghold")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("troll_stronghold", self._quest_calls)

    def test_quests_tab_allows_source_backed_focused_combat_override(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "the_restless_ghost"
        pd["inventory"]["Muddy skull"] = 1
        pd["quests"]["the_restless_ghost"] = {"started": True, "progress": 4, "completed": False}
        pd["quest_stage_actions"] = {"the_restless_ghost": ["Return the muddy skull to the ghost's coffin"]}
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 20
        pd["strength_level"] = 20
        pd["defense_level"] = 20
        pd["constitution_level"] = 20
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Skeleton warlock level 11"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_the_restless_ghost")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("the_restless_ghost", self._quest_calls)

    def test_quests_tab_shows_required_action_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "the_restless_ghost"
        pd["quests"]["the_restless_ghost"] = {"started": True, "progress": 1, "completed": False}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Action required: Receive the ghostspeak amulet from Father Urhney"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_the_restless_ghost")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Receive the ghostspeak amulet", action.toolTip())

    def test_quests_tab_vampyre_slayer_easy_items_are_not_prestart_requirements(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "vampyre_slayer"
        pd["quests"]["vampyre_slayer"] = {"started": True, "progress": 1, "completed": False}
        dialog = self._open(pd)

        card = dialog.findChild(QWidget, "questCard_vampyre_slayer")
        self.assertIsNotNone(card)
        labels = [lbl.text() for lbl in card.findChildren(QLabel)]
        self.assertFalse(any(text.startswith("Blocked:") for text in labels))
        self.assertFalse(any(text.startswith("Requires:") for text in labels))

    def test_quests_tab_shows_priest_in_peril_essence_stage_blocker(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "priest_in_peril"
        pd["quests"]["priest_in_peril"] = {"started": True, "progress": 8, "completed": False}
        pd["inventory"] = {"Pure essence": 24}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Rune essence x50 or Pure essence x25"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_priest_in_peril")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Pure essence x25", action.toolTip())

    def test_quests_tab_lists_stage_items_before_knights_sword_start(self) -> None:
        pd = _make_player_data()
        pd["mining_level"] = 10
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn(
            "Requires: Mining 10, Used during quest: Redberry pie x1, Blurite ore x1, Iron bar x2",
            labels,
        )

    def test_quests_tab_filters_by_catalog_metadata(self) -> None:
        dialog = self._open(_make_player_data())

        access_filter = dialog.findChild(QComboBox, "questAccessFilterCombo")
        difficulty_filter = dialog.findChild(QComboBox, "questDifficultyFilterCombo")
        length_filter = dialog.findChild(QComboBox, "questLengthFilterCombo")
        timeline_filter = dialog.findChild(QComboBox, "questTimelineFilterCombo")
        self.assertIsNotNone(access_filter)
        self.assertIsNotNone(difficulty_filter)
        self.assertIsNotNone(length_filter)
        self.assertIsNotNone(timeline_filter)
        self.assertIn("Members quests", [access_filter.itemText(i) for i in range(access_filter.count())])
        self.assertIn("Grandmaster", [difficulty_filter.itemText(i) for i in range(difficulty_filter.count())])
        self.assertIn("Long", [length_filter.itemText(i) for i in range(length_filter.count())])
        self.assertIn("Fifth Age", [timeline_filter.itemText(i) for i in range(timeline_filter.count())])

        access_filter.setCurrentText("Free quests")
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))
        self.assertIsNone(dialog.findChild(QWidget, "questCard_lost_city"))

        access_filter.setCurrentText("All access")
        difficulty_filter.setCurrentText("Grandmaster")
        QApplication.processEvents()
        self.assertIsNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_while_guthix_sleeps"))

    def test_bank_claims_expose_eligible_wicked_hood_claim(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 1
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("Wicked hood x1", labels)
        self.assertIn("Ready to claim", labels)
        self.assertTrue(any("locked reward" in label for label in labels), labels)
        self.assertIsNotNone(_find_named_widget(dialog, "bankClaimsScrollArea"))
        metadata = _find_named_label(dialog, "bankClaimMetadata")
        self.assertNotIn("palette(mid)", metadata.styleSheet())
        claim_btn = next(
            btn for btn in dialog.findChildren(QPushButton)
            if btn.text() == "Claim"
        )
        self.assertTrue(claim_btn.isEnabled())
        claim_btn.click()
        QApplication.processEvents()
        self.assertEqual(self._claim_calls[-1], ("wicked_hood", None))

    def test_bank_death_office_reclaim_row_uses_combat_office_state(self) -> None:
        pd = _make_player_data()
        pd["inventory"]["Coins"] = 250
        pd["death_office"] = {"items": ["Bronze sword", "Cape"], "source": "combat_stacked_grave"}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Death's Office", labels)
        self.assertIn("2 reclaimed gear items", labels)
        self.assertIn("Cost: 200 Coins · Bank: 250 Coins", labels)
        row = _find_named_widget(dialog, "deathOfficeRow")
        self.assertIsNotNone(row)
        reclaim_btn = dialog.findChild(QPushButton, "deathOfficeReclaimAction")
        self.assertIsNotNone(reclaim_btn)
        self.assertTrue(reclaim_btn.isEnabled())
        reclaim_btn.click()
        QApplication.processEvents()
        self.assertEqual(self._death_office_calls, [True])

    def test_bank_claims_expose_tutorial_starter_kit_bundle(self) -> None:
        pd = _make_player_data()
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("Tutorial Island starter kit", labels)
        self.assertTrue(
            any(label.startswith("11 item stacks - Bronze sword x1, Wooden shield x1, Shortbow x1") for label in labels),
            labels,
        )
        metadata = _find_named_label(dialog, "bankClaimMetadata")
        self.assertIn("Tinderbox x1", metadata.toolTip())
        claim_btn = next(
            btn for btn in dialog.findChildren(QPushButton)
            if btn.text() == "Claim"
        )
        claim_btn.click()
        QApplication.processEvents()
        self.assertEqual(self._claim_calls[-1], ("tutorial_island_starter_kit", None))

    def test_bank_claims_collapse_locked_rows_into_summary(self) -> None:
        pd = _make_player_data()
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("Tutorial Island starter kit", labels)
        self.assertNotIn("Wicked hood x1", labels)
        self.assertTrue(any("locked reward" in label for label in labels), labels)
        summary = _find_named_label(dialog, "bankClaimsLockedSummary")
        self.assertIn("Wicked hood requires: Rune Mysteries.", summary.text())
        self.assertNotIn("palette(mid)", summary.styleSheet())
        self.assertIn("Wicked hood: Rune Mysteries", summary.toolTip())
        self.assertEqual(
            len([w for w in dialog.findChildren(QWidget) if w.objectName() == "bankClaimRow"]),
            1,
            "only actionable claims should render as individual action rows",
        )

    def test_bank_claims_inbox_is_capped_above_inventory(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Logs": 5}
        original_claim_data = self._ui.CLAIM_DATA
        self._ui.CLAIM_DATA = {
            f"test_claim_{i}": {
                "display_name": f"Test reward {i}",
                "claim_type": "item",
                "item_name": f"Test reward {i}",
                "quantity": 1,
            }
            for i in range(5)
        }
        try:
            dialog = self._open(pd)
        finally:
            self._ui.CLAIM_DATA = original_claim_data

        claim_rows = [w for w in dialog.findChildren(QWidget) if w.objectName() == "bankClaimRow"]
        self.assertEqual(len(claim_rows), 5)
        scroll = _find_named_widget(dialog, "bankClaimsScrollArea")
        claims_box = _find_named_widget(dialog, "bankClaimsBox")
        self.assertLessEqual(scroll.maximumHeight(), 160)
        self.assertLessEqual(claims_box.maximumHeight(), 210)
        self.assertIsNot(_find_bank_list(dialog), _find_gear_list(dialog))

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

    def test_bank_groups_fish_and_bait_with_icons(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Raw crayfish": 3,
            "Raw shark": 1,
            "Fishing bait": 12,
        }
        dialog = self._open(pd)
        bank = _find_bank_list(dialog)
        texts = [bank.item(i).text() for i in range(bank.count())]
        for header in ("Fish", "Materials"):
            self.assertIn(header, texts, f"missing bank category header {header!r}")
        self.assertTrue(any(t.startswith("Raw crayfish x3") for t in texts))
        self.assertTrue(any(t.startswith("Fishing bait x12") for t in texts))
        crayfish_row = next(
            bank.item(i) for i in range(bank.count())
            if bank.item(i).text().startswith("Raw crayfish x")
        )
        bait_row = next(
            bank.item(i) for i in range(bank.count())
            if bank.item(i).text().startswith("Fishing bait x")
        )
        self.assertFalse(crayfish_row.icon().isNull(), "Raw crayfish row has no icon")
        self.assertFalse(bait_row.icon().isNull(), "Fishing bait row has no icon")

    def test_bank_groups_runecrafting_items_with_icons(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Air rune": 120,
            "Air talisman": 1,
            "Small pouch": 1,
            "Binding necklace": 1,
            "Wicked hood": 1,
        }
        dialog = self._open(pd)
        bank = _find_bank_list(dialog)
        texts = [bank.item(i).text() for i in range(bank.count())]
        self.assertIn("Runecrafting", texts)
        for item_name in ("Air rune", "Air talisman", "Small pouch", "Binding necklace", "Wicked hood"):
            self.assertTrue(any(t.startswith(f"{item_name} x") for t in texts), f"{item_name} missing from bank")
            row = next(
                bank.item(i) for i in range(bank.count())
                if bank.item(i).text().startswith(f"{item_name} x")
            )
            self.assertFalse(row.icon().isNull(), f"{item_name} row has no icon")

    def test_bank_offers_drink_action_for_consumables(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Beer": 2}
        pd["strength_level"] = 50
        pd["attack_level"] = 60
        pd["combat_lifepoints"] = 30
        consumed: list[str] = []

        def _consume(item_name: str):
            from logic_pure import apply_consumable_pure
            new_data, result = apply_consumable_pure(pd, item_name)
            if result.get("allowed"):
                pd.clear()
                pd.update(new_data)
                consumed.append(item_name)
                return result
            return None

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
            on_set_firemaking=lambda *a: None,
            on_set_fishing=lambda *a: None,
            on_set_cooking=lambda *a: None,
            on_set_utility=lambda *a: None,
            on_discard_item=lambda *a: True,
            on_consume_item=_consume,
        )
        dialog = self._captured[-1]
        menu = dialog._ankiscape_equip_menu_for("Beer")
        drink = next(a for a in menu.actions() if a.text() == "Drink Beer")
        self.assertTrue(drink.isEnabled())

        original_info = self._ui.QMessageBox.information
        self._ui.QMessageBox.information = lambda *a, **k: None
        try:
            drink.trigger()
            QApplication.processEvents()
        finally:
            self._ui.QMessageBox.information = original_info

        self.assertEqual(consumed, ["Beer"])
        self.assertEqual(pd["inventory"]["Beer"], 1)
        self.assertEqual(pd["combat_current_levels"], {"strength": 52, "attack": 56})

    def test_bank_groups_food_with_icons_and_discard_all_confirmation(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Shrimps": 3}
        discards: list[str] = []

        def _discard(item_name: str) -> bool:
            discards.append(item_name)
            pd["inventory"][item_name] = 0
            return True

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
            on_set_firemaking=lambda *a: None,
            on_set_fishing=lambda *a: None,
            on_set_cooking=lambda *a: None,
            on_set_utility=lambda *a: None,
            on_discard_item=_discard,
        )
        dialog = self._captured[-1]
        bank = _find_bank_list(dialog)
        texts = [bank.item(i).text() for i in range(bank.count())]
        self.assertIn("Food", texts)
        self.assertTrue(any(t.startswith("Shrimps x3") for t in texts))
        shrimp_row = next(
            bank.item(i) for i in range(bank.count())
            if bank.item(i).text().startswith("Shrimps x")
        )
        self.assertFalse(shrimp_row.icon().isNull(), "Shrimps row has no icon")

        menu = dialog._ankiscape_equip_menu_for("Shrimps")
        action = menu.actions()[0]
        self.assertEqual(action.text(), "Discard all (3)")
        self.assertTrue(action.isEnabled())

        original_question = self._ui.QMessageBox.question
        self._ui.QMessageBox.question = lambda *a, **k: self._ui.QMessageBox.StandardButton.Yes
        try:
            action.trigger()
            QApplication.processEvents()
        finally:
            self._ui.QMessageBox.question = original_question
        self.assertEqual(discards, ["Shrimps"])
        self.assertEqual(pd["inventory"]["Shrimps"], 0)

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
            on_set_fishing=lambda *a: None,
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

    def test_equipping_weapon_refreshes_equipment_combat_mode(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "combat_attack_style": "accurate",
                "inventory": {"Shortbow": 1},
                "ranged_level": 1,
            }
        )
        dialog = self._open_with_equip(pd)
        mode_label = dialog.findChild(QLabel, "combatModeLabel")
        self.assertIsNotNone(mode_label)
        self.assertIn("Accurate", mode_label.text())

        menu = dialog._ankiscape_equip_menu_for("Shortbow")
        action = next(action for action in menu.actions() if action.text() == "Equip")
        action.trigger()
        QApplication.processEvents()

        self.assertEqual(pd["equipment"], {"weapon": "Shortbow"})
        self.assertIn("Ranged Accurate", mode_label.text())

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

    def test_hud_recognizes_fishing_as_active_skill(self) -> None:
        pd = _make_player_data()
        pd["current_fishing"] = "catch_crayfish"
        hud = self._ui.ReviewHUD(None)
        hud.set_data(pd, "Fishing")
        self.assertTrue(
            hud.title_lbl.text().startswith("Fishing"),
            f"HUD did not recognize Fishing; shows {hud.title_lbl.text()!r}",
        )
        self.assertEqual(hud.target_lbl.text(), "Catch crayfish")
        self.assertFalse(hud.icon_lbl.pixmap().isNull(), "HUD has no Fishing icon")

    def test_hud_recognizes_cooking_as_active_skill(self) -> None:
        pd = _make_player_data()
        pd["current_cooking"] = "cook_shrimps"
        hud = self._ui.ReviewHUD(None)
        hud.set_data(pd, "Cooking")
        self.assertTrue(
            hud.title_lbl.text().startswith("Cooking"),
            f"HUD did not recognize Cooking; shows {hud.title_lbl.text()!r}",
        )
        self.assertEqual(hud.target_lbl.text(), "Cook raw shrimps")
        self.assertFalse(hud.icon_lbl.pixmap().isNull(), "HUD has no Cooking icon")

    # ---- Crafting/Utility rework surfaces ---------------------------------
    def _open_utility(self, dialog: "QDialog") -> "QTreeWidget":
        cat = next(
            b for b in dialog.findChildren(QPushButton) if b.text() == "Utility / Activities"
        )
        cat.click()
        QApplication.processEvents()
        return _find_utility_tree(dialog)

    def test_soft_clay_left_crafting_and_is_now_a_utility_activity(self) -> None:
        # Open Crafting target tree and assert Soft clay is no longer a target.
        tree = _goto_crafting(self.dialog)
        craft_texts = [it.text(0) for it in _tree_items(tree)]
        self.assertFalse(
            any(t.startswith("Soft clay") for t in craft_texts),
            f"Soft clay should not be a Crafting target anymore: {craft_texts}",
        )
        # And it now lives under Utility / Activities.
        utility_tree = self._open_utility(self.dialog)
        util_texts = [it.text(0) for it in _tree_items(utility_tree)]
        self.assertIn("Make soft clay", util_texts)
        self.assertIn("Gather wool", util_texts)
        self.assertIn("Gather grain", util_texts)
        self.assertIn("Make bread dough", util_texts)
        # Retired 2026-07-06: outputs are live NPC shop stock now.
        self.assertNotIn("Scavenge chicken feathers", util_texts)
        self.assertNotIn("Gather fishing bait", util_texts)
        self.assertNotIn("Buy Hunter supplies", util_texts)

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
        utility_tree = self._open_utility(self.dialog)
        for row in _tree_items(utility_tree):
            role = row.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(role, str) and role.startswith("__utility_group__"):
                continue
            self.assertFalse(row.icon(0).isNull(), f"{row.text(0)} should have an activity icon")

    def test_wool_gathering_is_enabled_and_selectable_from_utility(self) -> None:
        # gather_wool stands in for the retired scavenge_chicken_feathers
        # bridge (feathers are live NPC shop stock now).
        utility_tree = self._open_utility(self.dialog)
        wool_row = _utility_row(utility_tree, "gather_wool")

        self.assertTrue(wool_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertFalse(wool_row.icon(0).isNull())
        self.assertIn("No skill XP", wool_row.toolTip(0))
        self.assertIn("Output: Wool x1", wool_row.toolTip(0))
        self.assertIn("No materials required", wool_row.toolTip(0))

        self._utility_calls.clear()
        utility_tree.itemClicked.emit(wool_row, 0)
        QApplication.processEvents()

        self.assertEqual(self._utility_calls, ["gather_wool"])

    def test_stronghold_landmark_row_selects_activity_when_unfinished(self) -> None:
        pd = _make_player_data()
        pd["stronghold_of_security"] = {"step": 1, "completed": False, "boots_choice": None}
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)

        row = _utility_row(utility_tree, "stronghold_of_security")
        self.assertTrue(row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("1/4", row.text(0))
        self.assertFalse(row.icon(0).isNull())

        self._utility_calls.clear()
        utility_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._utility_calls, ["stronghold_of_security"])
        self.assertEqual(self._stronghold_claim_calls, [])

    def test_stronghold_landmark_row_claims_reward_when_completed_unclaimed(self) -> None:
        pd = _make_player_data()
        pd["stronghold_of_security"] = {"step": 4, "completed": True, "boots_choice": None}
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)

        row = _utility_row(utility_tree, "stronghold_of_security")
        self.assertIn("Claim", row.text(0))

        self._utility_calls.clear()
        utility_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        # A completed-but-unclaimed landmark opens the reward dialog rather than
        # (re)selecting the activity.
        self.assertEqual(self._stronghold_claim_calls, [True])
        self.assertEqual(self._utility_calls, [])

    def test_stronghold_landmark_row_is_inert_once_claimed(self) -> None:
        pd = _make_player_data()
        pd["stronghold_of_security"] = {"step": 4, "completed": True, "boots_choice": "Fancy boots"}
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)

        row = _utility_row(utility_tree, "stronghold_of_security")
        self.assertFalse(row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("Fancy boots", row.text(0))

        utility_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._stronghold_claim_calls, [])
        self.assertEqual(self._utility_calls, [])

    def test_utility_region_quest_locks_are_inert(self) -> None:
        pd = _make_player_data()
        pd["current_utility"] = "gather_lean_snails"
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)

        snails = _utility_row(utility_tree, "gather_lean_snails")
        self.assertFalse(snails.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("Priest in Peril", snails.toolTip(0))

        before = list(self._utility_calls)
        utility_tree.itemClicked.emit(snails, 0)
        QApplication.processEvents()
        self.assertEqual(self._utility_calls, before, "quest-locked utility rows must not be selectable")

        pd["quests"]["priest_in_peril"] = {"started": True, "progress": 6, "completed": True}
        unlocked_dialog = self._open(pd)
        unlocked_tree = self._open_utility(unlocked_dialog)
        self.assertTrue(_utility_row(unlocked_tree, "gather_lean_snails").flags() & Qt.ItemFlag.ItemIsEnabled)

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

    def test_mining_rows_include_concentrated_coal(self) -> None:
        ore_list = self._open_mining(self.dialog)
        concentrated_coal = self._ore_row(ore_list, "Concentrated coal ")
        self.assertIn("Mining level 77", concentrated_coal.toolTip())
        self.assertIn("Output: Coal x1", concentrated_coal.toolTip())
        self.assertIn("does not model rock depletion", concentrated_coal.toolTip())

    def test_open_bird_nests_is_a_visible_no_xp_utility_activity(self) -> None:
        utility_tree = self._open_utility(self.dialog)
        texts = [it.text(0) for it in _tree_items(utility_tree)]
        self.assertIn("Open bird nests", texts)
        nest = _utility_row(utility_tree, "open_bird_nest")
        self.assertIn("No XP", nest.toolTip(0))
        self.assertIn("bird nest", nest.toolTip(0).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
