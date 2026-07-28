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

import copy
import os
import re
import sys
import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ADDON_DIR = os.path.dirname(_THIS_DIR)
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

try:
    import aqt  # noqa: F401
    from aqt.qt import QApplication, QAbstractItemView, QCheckBox, QColor, QComboBox, QDialog, QEvent, QLabel, QLineEdit, QListWidget, QMainWindow, QMessageBox, QPalette, QPushButton, QIcon, QImage, QProgressBar, QScrollArea, QStackedWidget, QTabWidget, QToolButton, QTextBrowser, QSpinBox, Qt, QTreeWidget, QTreeWidgetItem, QWidget
    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
def _make_player_data() -> dict:
    from ankiscape.data.quest_data import default_quest_states

    data: dict = {"inventory": {}}
    for skill in ("mining", "woodcutting", "farming", "fishing", "hunter", "smithing", "crafting", "fletching", "firemaking", "cooking", "runecrafting", "prayer", "magic", "thieving", "agility", "summoning", "slayer"):
        data[f"{skill}_level"] = 33
        data[f"{skill}_exp"] = 1000.0
    # Real saves are seeded with a bound starter tool per gathering skill; without
    # it every tree/rock would lock on "no usable hatchet/pickaxe" and those rows
    # couldn't be exercised. Mirror that seed so Woodcutting and Mining rows unlock.
    data["toolbelt"] = {"woodcutting": ["bronze_hatchet"], "mining": ["bronze_pickaxe"]}
    data["equipment"] = {}
    data["current_hunter"] = "catch_crimson_swift"
    data["current_runecrafting"] = "craft_air_runes"
    data["current_thieving"] = "pickpocket_man"
    data["current_agility"] = "burthorpe_course"
    data["current_summoning"] = "infuse_spiritwolf"
    data["thieving_fight_back_when_caught"] = False
    data["current_quest"] = "rune_mysteries"
    data["quests"] = default_quest_states()
    data["quest_points"] = 0
    data["claims"] = {"wicked_hood": {"claimed": False}}
    data["wicked_hood"] = {"fed_altars": []}
    data["runecrafting_pouches"] = {}
    data["item_charges"] = {}
    data["combat_presets"] = {"Default": {}}
    data["combat_active_preset"] = "Default"
    data["combat_prayer_book"] = "standard"
    data["combat_selected_prayers"] = []
    data["combat_prayer_uptime"] = "off"
    data["combat_target_presets"] = {}
    data["combat_target_overrides"] = {}
    return data


def _panel_title(dialog: "QDialog") -> str:
    """Return the text of the Skills-hub panel header, if present.

    The header is the QLabel styled bold/large that reads e.g. "Woodcutting — Lv 33".
    """
    pattern = re.compile(r"^(Mining|Woodcutting|Fishing|Hunter|Smithing|Crafting|Fletching|Firemaking|Cooking|Runecrafting|Agility|Summoning|Slayer)(\s+—\s+Lv\s+\d+)?$")
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


def _find_stats_button(dialog: "QDialog", skill_id: str) -> "QToolButton":
    button = dialog.findChild(QToolButton, f"statsSkillButton_{skill_id}")
    if button is None:
        raise AssertionError(f"no Stats button for {skill_id!r}")
    return button


def _icon_pixels(icon: "QIcon", size: int = 28) -> bytes:
    image = icon.pixmap(size, size).toImage().convertToFormat(QImage.Format.Format_ARGB32)
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


def _open_challenges_tab(dialog: "QDialog") -> None:
    tabs = _find_main_tabs(dialog)
    index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Challenges")
    tabs.setCurrentIndex(index)
    QApplication.processEvents()


def _open_quests_tab(dialog: "QDialog") -> None:
    """Mandatory before touching quest widgets: the Quests tab is built on first
    show, so without this its widgets simply do not exist yet."""
    tabs = _find_main_tabs(dialog)
    index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Quests")
    tabs.setCurrentIndex(index)
    QApplication.processEvents()


def _expand_quest_card(dialog: "QDialog", quest_id: str) -> None:
    """Expand one quest card's journal.

    Journal bodies are filled on first expand, so a collapsed card holds no
    journal labels until its toggle is clicked.
    """
    toggle = dialog.findChild(QPushButton, f"questToggle_{quest_id}")
    body = dialog.findChild(QWidget, f"questBody_{quest_id}")
    if toggle is None or body is None:
        raise AssertionError(f"quest card {quest_id!r} not found")
    if body.isHidden():
        toggle.click()
        QApplication.processEvents()


def _open_achievements_tab(dialog: "QDialog") -> None:
    """Mandatory before touching achievement widgets (built on first show)."""
    tabs = _find_main_tabs(dialog)
    index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Achievements")
    tabs.setCurrentIndex(index)
    QApplication.processEvents()


def _open_ge_tab(dialog: "QDialog") -> None:
    tabs = _find_main_tabs(dialog)
    index = next(
        i for i in range(tabs.count()) if tabs.tabText(i) == "Grand Exchange"
    )
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
        from ankiscape.ui import ui
        from ankiscape.logic.combat_session import reset_wilderness_combat_confirmations

        reset_wilderness_combat_confirmations()
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
        self._herblore_calls: list = []
        # Same seams for Combat target/style/spell selection.
        self._combat_calls: list = []
        self._combat_action_calls: list = []
        self._combat_style_calls: list = []
        self._combat_spell_calls: list = []
        self._combat_threshold_calls: list = []
        self._combat_food_calls: list = []
        self._combat_refill_calls: list = []
        self._combat_unload_calls: list = []
        self._prayer_calls: list = []
        self._magic_calls: list = []
        self._construction_calls: list = []
        self._thieving_calls: list = []
        self._agility_calls: list = []
        self._summoning_calls: list = []
        self._slayer_command_calls: list = []
        self._agility_command_calls: list = []
        self._warriors_guild_calls: list = []
        self._livid_farm_calls: list = []
        self._big_chinchompa_calls: list = []
        self._shooting_star_calls: list = []
        self._fist_of_guthix_calls: list = []
        self._sorceress_garden_calls: list = []
        self._penguin_calls: list = []
        self._vinesweeper_calls: list = []
        self._fight_caves_calls: list = []
        self._phoenix_lair_calls: list = []
        self._skeletal_horror_calls: list = []
        self._tears_of_guthix_calls: list = []
        self._enchanted_key_calls: list = []
        self._barrows_calls: list = []
        self._stealing_creation_calls: list = []
        self._fish_flingers_calls: list = []
        self._fishing_trawler_calls: list = []
        self._great_orb_project_calls: list = []
        self._managing_miscellania_calls: list = []
        self._thieving_fight_back_calls: list = []
        self._farming_calls: list = []
        self._mage_arena_calls: list = []
        self._magic_alch_calls: list = []
        self._farming_spell_patch_calls: list = []
        self._prayer_config_calls: list = []
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
        from ankiscape.data.construction_data import HOUSE_STYLE_DATA, ROOM_DATA, SERVANT_DATA
        from ankiscape.core.constants import PRAYER_DATA
        from ankiscape.logic_pure.logic_pure import (
            apply_prayer_selection_pure,
            purchase_house_option_pure,
            purchase_house_pure,
            sanitize_prayer_selection_pure,
            unload_combat_supply_loadout_pure,
        )

        def _set_prayer_config(key, value):
            self._prayer_config_calls.append((key, value))
            if key not in {"apply_preset", "save_preset", "pin_target_preset", "target_override"}:
                player_data[key] = value
                player_data["combat_selected_prayers"] = list(
                    sanitize_prayer_selection_pure(player_data, player_data.get("combat_selected_prayers", ()))
                )
            return True

        def _set_prayer_selection(material_id, ui_method_id):
            self._prayer_calls.append((material_id, ui_method_id))
            updated, ok, _reasons = apply_prayer_selection_pure(
                player_data,
                material_id,
                ui_method_id,
                PRAYER_DATA,
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        def _farming_projection():
            from ankiscape.logic.farming_logic import farming_frontend_projection_pure
            return farming_frontend_projection_pure(player_data)

        def _farming_action(action_id, payload):
            from ankiscape.logic.farming_logic import apply_farming_frontend_action_pure
            self._farming_calls.append((action_id, dict(payload)))
            updated, ok, message = apply_farming_frontend_action_pure(player_data, action_id, payload)
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": message}

        def _set_thieving_fight_back(enabled):
            enabled = bool(enabled)
            self._thieving_fight_back_calls.append(enabled)
            player_data["thieving_fight_back_when_caught"] = enabled
            return True

        def _set_target(key, calls, target):
            calls.append(target)
            player_data[key] = target
            return True

        def _unload_combat_loadout():
            self._combat_unload_calls.append(True)
            updated, ok, _reason = unload_combat_supply_loadout_pure(player_data)
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        def _apply_house_result(result):
            updated, ok = result
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        def _agility_command(action_id, payload):
            from ankiscape.logic.agility_logic import apply_agility_command_pure

            self._agility_command_calls.append((action_id, dict(payload)))
            updated, result = apply_agility_command_pure(player_data, action_id, payload, roll=0.5)
            if result.get("allowed"):
                player_data.clear()
                player_data.update(updated)
            return {"ok": bool(result.get("allowed")), **result}

        def _slayer_command(action_id, payload):
            from ankiscape.logic.slayer_logic import get_slayer_assignment_pure

            self._slayer_command_calls.append((action_id, dict(payload)))
            if action_id == "set_combat_filter":
                player_data["slayer_combat_filter"] = bool(
                    payload.get("enabled", False)
                )
                return {
                    "ok": True,
                    "combat_filter": player_data["slayer_combat_filter"],
                }
            rolls = iter((0.0, 0.0))
            updated, ok, info = get_slayer_assignment_pure(
                player_data,
                master_id=str(payload.get("master_id", "turael_spria")),
                rng=lambda: next(rolls),
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, **info}

        def _warriors_guild_command(action_id, payload):
            from ankiscape.logic.warriors_guild_logic import (
                enter_warriors_guild_cyclops_room_pure,
                leave_warriors_guild_cyclops_room_pure,
                set_warriors_guild_policy_pure,
                show_warriors_guild_defender_pure,
            )

            self._warriors_guild_calls.append((action_id, dict(payload)))
            if action_id == "set_policy":
                result = set_warriors_guild_policy_pure(
                    player_data,
                    automation_mode=payload.get("automation_mode"),
                    payment_mode=payload.get("payment_mode"),
                    single_token=payload.get("single_token"),
                )
            elif action_id == "enter_room":
                result = enter_warriors_guild_cyclops_room_pure(player_data)
            elif action_id == "leave_room":
                result = leave_warriors_guild_cyclops_room_pure(player_data)
            else:
                result = show_warriors_guild_defender_pure(player_data)
            updated, ok, info = result
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("message", info.get("reason", ""))}

        def _livid_farm_command(action_id, payload):
            from ankiscape.logic.livid_farm_logic import (
                apply_arcane_capacitor_charge_pure,
                apply_arcane_capacitor_remove_charge_pure,
                apply_livid_farm_wish_pure,
                set_livid_farm_routine_pure,
            )

            self._livid_farm_calls.append((action_id, dict(payload)))
            if action_id == "set_routine":
                updated, ok, info = set_livid_farm_routine_pure(
                    player_data,
                    payload.get("routine"),
                )
            elif action_id == "buy_wish":
                updated, ok, info = apply_livid_farm_wish_pure(
                    player_data,
                    payload.get("wish_id"),
                )
            elif action_id == "charge_capacitor":
                updated, ok, info = apply_arcane_capacitor_charge_pure(
                    player_data,
                    payload.get("spell_id"),
                )
            elif action_id == "remove_capacitor_charge":
                updated, ok, info = (
                    apply_arcane_capacitor_remove_charge_pure(
                        player_data
                    )
                )
            else:
                return {"ok": False, "message": "Unknown command"}
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {
                "ok": ok,
                "message": info.get("message", info.get("reason", "")),
                **info,
            }

        def _big_chinchompa_command(action_id, payload):
            from ankiscape.logic.big_chinchompa_logic import (
                apply_big_chinchompa_reward_purchase_pure,
                set_hunter_private_ground_pure,
            )

            self._big_chinchompa_calls.append((action_id, dict(payload)))
            if action_id == "set_private_ground":
                updated, ok, info = set_hunter_private_ground_pure(
                    player_data,
                    payload.get("target_id", ""),
                    bool(payload.get("enabled", False)),
                )
            elif action_id == "buy_reward":
                updated, ok, info = (
                    apply_big_chinchompa_reward_purchase_pure(
                        player_data, payload.get("reward_id", "")
                    )
                )
            else:
                return {"ok": False, "message": "Unknown command"}
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {
                "ok": ok,
                "message": info.get("message", info.get("reason", "")),
                **info,
            }

        def _shooting_star_command(action_id, payload):
            from ankiscape.logic.shooting_star_logic import (
                apply_shooting_star_exchange_pure,
            )

            self._shooting_star_calls.append((action_id, dict(payload)))
            if action_id == "exchange":
                updated, ok, info = apply_shooting_star_exchange_pure(
                    player_data
                )
            else:
                return {"ok": False, "message": "Unknown command"}
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {
                "ok": ok,
                "message": info.get("reason", ""),
                **info,
            }

        def _fist_of_guthix_command(action_id, payload):
            from ankiscape.logic.fist_of_guthix_logic import apply_fist_of_guthix_command_pure

            self._fist_of_guthix_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_fist_of_guthix_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _sorceress_garden_command(action_id, payload):
            from ankiscape.logic.sorceress_garden_logic import apply_sorceress_garden_command_pure

            self._sorceress_garden_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_sorceress_garden_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _penguin_command(action_id, payload):
            from ankiscape.logic.penguin_hide_and_seek_logic import apply_penguin_command_pure

            self._penguin_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_penguin_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _vinesweeper_command(action_id, payload):
            from ankiscape.logic.vinesweeper_logic import apply_vinesweeper_command_pure

            self._vinesweeper_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_vinesweeper_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _fight_caves_command(action_id, payload):
            from ankiscape.logic.fight_caves_logic import apply_fight_caves_command_pure

            self._fight_caves_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_fight_caves_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _phoenix_lair_command(action_id, payload):
            from ankiscape.logic.phoenix_lair_logic import apply_phoenix_lair_command_pure

            self._phoenix_lair_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_phoenix_lair_command_pure(
                player_data, action_id, payload, rng=lambda: 0.5
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _skeletal_horror_command(action_id, payload):
            from ankiscape.logic.skeletal_horror_logic import (
                apply_skeletal_horror_command_pure,
            )

            self._skeletal_horror_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_skeletal_horror_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _enchanted_key_command(action_id, payload):
            from ankiscape.logic.enchanted_key_logic import (
                apply_enchanted_key_command_pure,
            )

            self._enchanted_key_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_enchanted_key_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _tears_of_guthix_command(action_id, payload):
            from ankiscape.logic.tears_of_guthix_logic import (
                apply_tears_of_guthix_command_pure,
            )

            self._tears_of_guthix_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_tears_of_guthix_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _barrows_command(action_id, payload):
            from ankiscape.logic.barrows_logic import apply_barrows_command_pure

            self._barrows_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_barrows_command_pure(
                player_data, action_id, payload, rng=lambda: 0.5
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _stealing_creation_command(action_id, payload):
            from ankiscape.logic.stealing_creation_logic import apply_stealing_creation_command_pure

            self._stealing_creation_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_stealing_creation_command_pure(
                player_data, action_id, payload, rng=lambda: 0.5
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _fish_flingers_command(action_id, payload):
            from ankiscape.logic.fish_flingers_logic import apply_fish_flingers_command_pure

            self._fish_flingers_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_fish_flingers_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _fishing_trawler_command(action_id, payload):
            from ankiscape.logic.fishing_trawler_logic import apply_fishing_trawler_command_pure

            self._fishing_trawler_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_fishing_trawler_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _great_orb_project_command(action_id, payload):
            from ankiscape.logic.great_orb_project_logic import apply_great_orb_project_command_pure

            self._great_orb_project_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_great_orb_project_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _managing_miscellania_command(action_id, payload):
            from ankiscape.logic.managing_miscellania_logic import apply_managing_miscellania_command_pure

            self._managing_miscellania_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_managing_miscellania_command_pure(
                player_data, action_id, payload
            )
            if ok:
                player_data.clear()
                player_data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def _mage_arena_action(action_id, god_id):
            from ankiscape.logic_pure.logic_pure import (
                apply_mage_arena_cape_action_pure,
                set_mage_arena_alignment_pure,
            )

            self._mage_arena_calls.append((action_id, god_id))
            action = (
                set_mage_arena_alignment_pure
                if action_id == "select_alignment"
                else apply_mage_arena_cape_action_pure
            )
            updated, ok, _info = action(player_data, god_id)
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        def _hire_servant(servant_id):
            if not servant_id:
                player_data["house_servant"] = ""
                return True
            return _apply_house_result(
                purchase_house_option_pure(
                    player_data, servant_id, SERVANT_DATA, kind="servant"
                )
            )

        save_skill_callback = extra.pop("on_save_skill", lambda *a: None)
        self._ui.show_main_menu(
            **extra,
            player_data=player_data,
            current_skill=current_skill,
            can_smelt_any_bar=True,
            on_save_skill=save_skill_callback,
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
            on_set_herblore=lambda target: _set_target(
                "current_herblore", self._herblore_calls, target
            ),
            on_set_thieving=lambda target: _set_target("current_thieving", self._thieving_calls, target),
            on_set_thieving_fight_back=_set_thieving_fight_back,
            on_set_agility=lambda target: _set_target("current_agility", self._agility_calls, target),
            on_set_summoning=lambda target: _set_target(
                "current_summoning", self._summoning_calls, target
            ),
            on_slayer_command=_slayer_command,
            on_agility_command=_agility_command,
            on_warriors_guild_command=_warriors_guild_command,
            on_livid_farm_command=_livid_farm_command,
            on_big_chinchompa_command=_big_chinchompa_command,
            on_shooting_star_command=_shooting_star_command,
            on_fist_of_guthix_command=_fist_of_guthix_command,
            on_sorceress_garden_command=_sorceress_garden_command,
            on_penguin_command=_penguin_command,
            on_vinesweeper_command=_vinesweeper_command,
            on_fight_caves_command=_fight_caves_command,
            on_phoenix_lair_command=_phoenix_lair_command,
            on_skeletal_horror_command=_skeletal_horror_command,
            on_tears_of_guthix_command=_tears_of_guthix_command,
            on_enchanted_key_command=_enchanted_key_command,
            on_barrows_command=_barrows_command,
            on_stealing_creation_command=_stealing_creation_command,
            on_fish_flingers_command=_fish_flingers_command,
            on_fishing_trawler_command=_fishing_trawler_command,
            on_great_orb_project_command=_great_orb_project_command,
            on_managing_miscellania_command=_managing_miscellania_command,
            on_set_prayer_selection=_set_prayer_selection,
            on_set_magic=lambda target: _set_target("current_magic", self._magic_calls, target),
            on_set_construction=lambda target: _set_target("current_construction", self._construction_calls, target),
            on_purchase_house=lambda: _apply_house_result(purchase_house_pure(player_data)),
            on_purchase_room=lambda room_id: _apply_house_result(
                purchase_house_option_pure(player_data, room_id, ROOM_DATA, kind="room")
            ),
            on_hire_servant=_hire_servant,
            on_set_house_style=lambda style_id: _apply_house_result(
                purchase_house_option_pure(player_data, style_id, HOUSE_STYLE_DATA, kind="style")
            ),
            on_set_magic_alchemy_item=lambda item: _set_target("magic_alchemy_item", self._magic_alch_calls, item),
            on_set_farming_spell_patch=lambda patch: _set_target("farming_spell_patch", self._farming_spell_patch_calls, patch),
            on_set_utility=lambda activity: self._utility_calls.append(activity),
            on_set_combat=lambda target: self._combat_calls.append(target),
            on_set_combat_action=lambda action: self._combat_action_calls.append(action),
            on_set_combat_style=lambda style: self._combat_style_calls.append(style),
            on_set_combat_spell=lambda spell: self._combat_spell_calls.append(spell),
            on_set_combat_auto_eat_threshold=lambda threshold: self._combat_threshold_calls.append(threshold),
            on_set_combat_auto_eat_food=lambda food: self._combat_food_calls.append(food),
            on_set_combat_prayer_config=_set_prayer_config,
            on_refill_combat_loadout=lambda: self._combat_refill_calls.append(True) or True,
            on_unload_combat_loadout=_unload_combat_loadout,
            on_reclaim_death_office=lambda: self._death_office_calls.append(True) or True,
            on_set_quest=lambda quest_id: self._quest_calls.append(quest_id),
            on_set_quest_route_choice=lambda quest_id, route_id: self._quest_choice_calls.append((quest_id, route_id)) or True,
            on_claim_reward=lambda claim_id, selected_skill_id=None: self._claim_calls.append((claim_id, selected_skill_id)) or True,
            on_claim_stronghold_reward=lambda: self._stronghold_claim_calls.append(True) or True,
            on_mage_arena_action=_mage_arena_action,
            get_farming_projection=_farming_projection,
            on_farming_action=_farming_action,
        )
        self.assertTrue(self._captured, "show_main_menu did not call dialog.exec()")
        return self._captured[-1]

    def tearDown(self) -> None:
        QDialog.exec = self._orig_exec  # type: ignore[assignment,method-assign]
        self._ui.get_config_bool = self._orig_cfg
        for dialog in self._captured:
            try:
                dialog.deleteLater()
            except RuntimeError:
                pass
        QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def test_initial_panel_shows_a_gathering_skill(self) -> None:
        title = _panel_title(self.dialog)
        self.assertTrue(title.startswith("Mining"), f"unexpected initial panel: {title!r}")

    def test_global_tabs_use_unique_semantic_icons(self) -> None:
        tabs = _find_main_tabs(self.dialog)
        expected = {
            "Skills": "skills_icon.png",
            "Shop": "shop_icon.png",
            "Grand Exchange": "grand_exchange_icon.png",
            "Quests": "quest_icon.png",
            "Bank": "bank_icon.png",
            "Equipment": "equipment_icon.png",
            "Stats": "stats_icon.png",
            "Challenges": "challenges_icon.png",
            "Achievements": "achievement_icon.png",
            "Settings": "settings_icon.png",
        }
        rendered = {}
        for index in range(tabs.count()):
            label = tabs.tabText(index)
            icon = tabs.tabIcon(index)
            self.assertFalse(icon.isNull(), f"{label} has no tab icon")
            self.assertEqual(
                _icon_pixels(icon),
                _icon_pixels(
                    QIcon(os.path.join(_ADDON_DIR, "icon", expected[label]))
                ),
            )
            rendered[label] = _icon_pixels(icon)
        self.assertEqual(len(set(rendered.values())), len(expected))

    def test_contextual_help_maps_every_primary_tab_without_changing_page(self) -> None:
        expected_titles = {
            "Skills": "Skills and training",
            "Shop": "NPC shops",
            "Grand Exchange": "Grand Exchange",
            "Quests": "Quests",
            "Bank": "Bank and inventory actions",
            "Equipment": "Equipment and familiars",
            "Stats": "Stats",
            "Challenges": "Daily Challenges",
            "Achievements": "Achievements",
            "Settings": "Settings",
        }
        tabs = _find_main_tabs(self.dialog)
        button = self.dialog.findChild(QToolButton, "mainMenuHelpButton")
        panel = _find_named_widget(self.dialog, "helpCenterPanel")
        topic_title = _find_named_label(self.dialog, "helpTopicTitle")
        self.assertIsNotNone(button)
        self.assertTrue(panel.isHidden())
        original_width = self.dialog.width()

        for index in range(tabs.count()):
            with self.subTest(tab=tabs.tabText(index)):
                tabs.setCurrentIndex(index)
                QApplication.processEvents()
                selected_index = tabs.currentIndex()
                button.click()
                QApplication.processEvents()

                self.assertFalse(panel.isHidden())
                self.assertEqual(tabs.currentIndex(), selected_index)
                self.assertEqual(
                    topic_title.text(),
                    expected_titles[tabs.tabText(index)],
                )
                self.assertEqual(
                    button.toolTip(),
                    f"Help for {tabs.tabText(index)} (F1)",
                )

        self.assertGreaterEqual(self.dialog.width(), original_width)
        self.assertTrue(button.shortcut().toString())
        self.dialog.findChild(QToolButton, "helpCloseButton").click()
        QApplication.processEvents()
        self.assertTrue(panel.isHidden())
        self.assertEqual(self.dialog.width(), original_width)

    def test_help_search_escape_empty_state_and_topic_navigation(self) -> None:
        from aqt.qt import QKeyEvent, QTextBrowser, QUrl

        _find_main_tabs(self.dialog).setCurrentIndex(0)
        self.dialog.findChild(QToolButton, "mainMenuHelpButton").click()
        QApplication.processEvents()

        search = _find_named_line_edit(self.dialog, "helpSearch")
        topic_list = _find_named_list(self.dialog, "helpTopicList")
        empty = _find_named_label(self.dialog, "helpEmptyState")
        search.setText("familiar duration")
        QApplication.processEvents()
        self.assertEqual(
            set(_list_texts(topic_list)),
            {"Simulated time", "Summoning and familiars"},
        )
        topic_list.itemClicked.emit(topic_list.item(0))
        QApplication.processEvents()
        self.assertEqual(search.text(), "familiar duration")
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Simulated time",
        )
        self.assertEqual(
            _find_named_label(self.dialog, "helpSearchSummary").text(),
            "",
        )
        self.dialog.findChild(QToolButton, "helpBackButton").click()
        QApplication.processEvents()
        self.assertEqual(search.text(), "familiar duration")
        self.assertEqual(set(_list_texts(topic_list)), {"Simulated time", "Summoning and familiars"})
        self.dialog.findChild(QToolButton, "helpForwardButton").click()
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Simulated time",
        )
        self.dialog.findChild(QToolButton, "helpBackButton").click()
        QApplication.processEvents()

        search.setText("definitely-not-help-content")
        QApplication.processEvents()
        self.assertTrue(topic_list.isHidden())
        self.assertFalse(empty.isHidden())
        self.assertIn("No help topics match", empty.text())

        escape = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(search, escape)
        QApplication.processEvents()
        self.assertEqual(search.text(), "")
        panel = _find_named_widget(self.dialog, "helpCenterPanel")
        self.assertIs(panel.results_stack.currentWidget(), topic_list)
        self.assertIn("Using AnkiScape", _list_texts(topic_list))

        self.dialog.show()
        search.setFocus()
        QApplication.processEvents()
        down = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Down,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(search, down)
        QApplication.processEvents()
        self.assertEqual(topic_list.currentRow(), 0)
        self.assertIs(QApplication.focusWidget(), topic_list)

        panel.open_topic("skills")
        body = self.dialog.findChild(QTextBrowser, "helpTopicBody")
        body.anchorClicked.emit(QUrl("help:automation"))
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Casual and Advanced automation",
        )
        self.dialog.findChild(QToolButton, "helpBackButton").click()
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Skills and training",
        )
        self.dialog.findChild(QToolButton, "helpForwardButton").click()
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Casual and Advanced automation",
        )

        search.setFocus()
        rejected: list[bool] = []
        self.dialog.rejected.connect(lambda: rejected.append(True))
        QApplication.sendEvent(search, escape)
        QApplication.processEvents()
        self.assertTrue(panel.isHidden())
        self.assertEqual(rejected, [])

    def test_help_drawer_clamps_right_edge_to_the_available_screen(self) -> None:
        screen = self.dialog.screen() or QApplication.primaryScreen()
        self.assertIsNotNone(screen)
        available = screen.availableGeometry()
        self.dialog.resize(720, 540)
        self.dialog.move(available.right() - 40, available.top())

        self.dialog.findChild(QToolButton, "mainMenuHelpButton").click()
        QApplication.processEvents()

        self.assertGreaterEqual(self.dialog.x(), available.left())
        self.assertLessEqual(
            self.dialog.x() + self.dialog.width() - 1,
            available.right(),
        )

    def test_help_missing_topic_falls_back_home_or_fails_visibly_in_developer_mode(self) -> None:
        panel = _find_named_widget(self.dialog, "helpCenterPanel")
        title = _find_named_label(self.dialog, "helpTopicTitle")

        self.assertFalse(panel.open_topic("does-not-exist"))
        self.assertEqual(title.text(), "Broken Help reference")
        self.assertIn(
            "Unknown help topic",
            self.dialog.findChild(QTextBrowser, "helpTopicBody").toPlainText(),
        )

        panel._developer_mode = False
        self.assertTrue(panel.open_topic("does-not-exist"))
        self.assertEqual(title.text(), "Using AnkiScape")

    def test_help_dim_text_uses_the_dark_theme_text_role(self) -> None:
        original_palette = QApplication.palette()
        dark = QPalette(original_palette)
        dark.setColor(QPalette.ColorRole.Base, QColor(24, 24, 24))
        dark.setColor(QPalette.ColorRole.Text, QColor(238, 238, 238))
        dark.setColor(QPalette.ColorRole.Mid, QColor(8, 8, 8))
        QApplication.setPalette(dark)
        try:
            dialog = self._open(_make_player_data())
            dialog.findChild(QToolButton, "mainMenuHelpButton").click()
            QApplication.processEvents()
            empty = _find_named_label(dialog, "helpEmptyState")
            self.assertIn("rgba(238, 238, 238", empty.styleSheet())
            self.assertNotIn("color: palette(mid)", empty.styleSheet())
            dialog.deleteLater()
        finally:
            QApplication.setPalette(original_palette)

    def _goto_slayer(self, dialog: "QDialog") -> None:
        next(
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == "Support"
        ).click()
        QApplication.processEvents()
        skill_list = next(
            widget
            for widget in dialog.findChildren(QListWidget)
            if "Slayer" in _list_texts(widget)
        )
        row = _list_texts(skill_list).index("Slayer")
        skill_list.setCurrentRow(row)
        QApplication.processEvents()

    def test_slayer_is_management_only_and_exposes_three_live_tabs(self) -> None:
        dialog = self._open(_make_player_data())
        self._goto_slayer(dialog)

        self.assertEqual(_panel_title(dialog), "Slayer — Lv 33")
        self.assertFalse(
            any(
                button.isVisible()
                and button.text() in {"Train this skill", "Currently training"}
                for button in dialog.findChildren(QPushButton)
            )
        )
        tabs = dialog.findChild(QTabWidget, "slayerManagementTabs")
        self.assertIsNotNone(tabs)
        self.assertEqual(
            [tabs.tabText(index) for index in range(tabs.count())],
            ["Assignment", "Masters", "Rewards"],
        )
        self.assertIsNotNone(dialog.findChild(QLabel, "slayerAssignmentEmptyState"))

        tabs.setCurrentIndex(2)
        QApplication.processEvents()
        lock = dialog.findChild(QLabel, "slayerRewardsSmokingKillsLock")
        self.assertIsNotNone(lock)
        self.assertIn("Complete Smoking Kills", lock.text())

        # The master gets a chathead so the player can tell who is speaking.
        tabs.setCurrentIndex(1)
        QApplication.processEvents()
        chathead = dialog.findChild(QLabel, "slayerMasterChathead")
        self.assertIsNotNone(chathead)
        self.assertIsNotNone(chathead.pixmap())
        self.assertFalse(chathead.pixmap().isNull())

    def test_slayer_master_card_matches_turael_or_spria(self) -> None:
        for completed, display_name, filename in (
            (False, "Turael", "turael_chathead.png"),
            (True, "Spria", "spria_chathead.png"),
        ):
            with self.subTest(display_name=display_name):
                data = _make_player_data()
                data["quests"]["while_guthix_sleeps"] = {
                    "started": completed,
                    "progress": 1 if completed else 0,
                    "completed": completed,
                }
                dialog = self._open(data)
                self._goto_slayer(dialog)
                tabs = dialog.findChild(QTabWidget, "slayerManagementTabs")
                tabs.setCurrentIndex(1)
                QApplication.processEvents()

                chathead = dialog.findChild(QLabel, "slayerMasterChathead")
                self.assertTrue(
                    any(label.text() == display_name for label in dialog.findChildren(QLabel))
                )
                self.assertIsNotNone(chathead.pixmap())
                expected = self._ui._pixel_path_icon(
                    os.path.join(self._ui.current_dir, "activityicons", filename), 48
                )
                self.assertIsNotNone(expected)
                self.assertEqual(
                    _icon_pixels(QIcon(chathead.pixmap()), 48),
                    _icon_pixels(expected, 48),
                )

    def test_slayer_assignment_chathead_matches_every_displayable_master(self) -> None:
        from ankiscape.data.slayer_data import (
            CHAELDAR_MASTER,
            DURADEL_MASTER,
            MAZCHNA_MASTER,
            SLAYER_MASTERS_BY_ID,
            SUMONA_MASTER,
            TURAEL_MASTER,
            VANNAKA_MASTER,
        )

        cases = (
            (TURAEL_MASTER, {}, "Turael", "turael_chathead.png"),
            (
                TURAEL_MASTER,
                {"started": True, "progress": 1, "completed": True},
                "Spria",
                "spria_chathead.png",
            ),
            (MAZCHNA_MASTER, {}, "Mazchna", "mazchna_chathead.png"),
            (
                MAZCHNA_MASTER,
                {"started": True, "progress": 1, "completed": False},
                "Achtryn",
                "achtryn_chathead.png",
            ),
            (VANNAKA_MASTER, {}, "Vannaka", "vannaka_chathead.png"),
            (CHAELDAR_MASTER, {}, "Chaeldar", "chaeldar_chathead.png"),
            (SUMONA_MASTER, {}, "Sumona", "sumona_chathead.png"),
            (DURADEL_MASTER, {}, "Duradel", "duradel_chathead.png"),
            (
                DURADEL_MASTER,
                {"started": True, "progress": 1, "completed": True},
                "Lapalok",
                "lapalok_chathead.png",
            ),
        )
        for master, wgs_state, display_name, filename in cases:
            with self.subTest(display_name=display_name):
                data = _make_player_data()
                if wgs_state:
                    data["quests"]["while_guthix_sleeps"] = wgs_state
                data["slayer_assignment"] = {
                    "master_id": master.id,
                    "family_id": master.assignments[0].id,
                    "initial_count": 1,
                    "remaining": 1,
                }
                live_master = replace(master, runtime_enabled=True)
                with patch.dict(
                    SLAYER_MASTERS_BY_ID, {master.id: live_master}
                ):
                    dialog = self._open(data)
                    self._goto_slayer(dialog)

                chathead = dialog.findChild(QLabel, "slayerAssignmentChathead")
                progress = dialog.findChild(QLabel, "slayerAssignmentProgress")
                self.assertIn(f"assigned by {display_name}", progress.text())
                self.assertIsNotNone(chathead.pixmap())
                expected = self._ui._pixel_path_icon(
                    os.path.join(self._ui.current_dir, "activityicons", filename), 48
                )
                self.assertIsNotNone(expected)
                self.assertEqual(
                    _icon_pixels(QIcon(chathead.pixmap()), 48),
                    _icon_pixels(expected, 48),
                )

    def test_slayer_assignment_without_period_art_has_no_fallback_face(self) -> None:
        from ankiscape.data.slayer_data import SLAYER_MASTERS_BY_ID, TURAEL_MASTER

        data = _make_player_data()
        data["slayer_assignment"] = {
            "master_id": "turael_spria",
            "family_id": "bats",
            "initial_count": 1,
            "remaining": 1,
        }
        without_art = replace(TURAEL_MASTER, chathead_asset_path="")
        with patch.dict(SLAYER_MASTERS_BY_ID, {TURAEL_MASTER.id: without_art}):
            dialog = self._open(data)
            self._goto_slayer(dialog)

        chathead = dialog.findChild(QLabel, "slayerAssignmentChathead")
        progress = dialog.findChild(QLabel, "slayerAssignmentProgress")
        self.assertIn("assigned by Turael", progress.text())
        self.assertTrue(chathead.pixmap() is None or chathead.pixmap().isNull())

    def test_slayer_assignment_action_rerenders_as_active_task(self) -> None:
        dialog = self._open(_make_player_data())
        self._goto_slayer(dialog)

        dialog.findChild(QPushButton, "slayerGetAssignmentButton").click()
        QApplication.processEvents()

        self.assertEqual(
            self._slayer_command_calls[-1],
            ("get_assignment", {"master_id": "turael_spria"}),
        )
        progress = dialog.findChild(QLabel, "slayerAssignmentProgress")
        self.assertIsNotNone(progress)
        self.assertIn("remaining", progress.text())
        self.assertIsNotNone(dialog.findChild(QPushButton, "slayerOpenCombatButton"))

    def test_slayer_open_in_combat_enables_and_composes_task_filter(self) -> None:
        data = _make_player_data()
        data["slayer_assignment"] = {
            "master_id": "turael_spria",
            "family_id": "bats",
            "initial_count": 15,
            "remaining": 15,
        }
        dialog = self._open(data)
        self._goto_slayer(dialog)

        dialog.findChild(QPushButton, "slayerOpenCombatButton").click()
        QApplication.processEvents()

        checkbox = dialog.findChild(QCheckBox, "slayerTaskOnlyCheckBox")
        self.assertIsNotNone(checkbox)
        self.assertTrue(checkbox.isChecked())
        self.assertEqual(
            self._slayer_command_calls[-1],
            ("set_combat_filter", {"enabled": True}),
        )
        tree = dialog.findChild(QTreeWidget, "combatTargetTree")
        roles = {
            item.data(0, Qt.ItemDataRole.UserRole)
            for item in _tree_items(tree)
        }
        self.assertIn("giant_bat", roles)
        self.assertNotIn("black_bear", roles)
        giant_bat = next(
            item
            for item in _tree_items(tree)
            if item.data(0, Qt.ItemDataRole.UserRole) == "giant_bat"
        )
        self.assertIsNotNone(giant_bat.parent())
        self.assertTrue(giant_bat.parent().isExpanded())
        from ankiscape.core.constants import COMBAT_ENEMY_IMAGES

        self.assertEqual(
            _icon_pixels(giant_bat.icon(0)),
            _icon_pixels(
                self._ui._pixel_path_icon(
                    COMBAT_ENEMY_IMAGES["giant_bat"],
                    28,
                )
            ),
        )

    def test_slayer_task_filter_empty_state_explains_recovery(self) -> None:
        data = _make_player_data()
        data["slayer_combat_filter"] = True
        dialog = self._open(data, current_skill="Combat")

        tree = dialog.findChild(QTreeWidget, "combatTargetTree")
        self.assertIsNotNone(tree)
        empty_rows = [
            item.text(0)
            for item in _tree_items(tree)
            if not item.data(0, Qt.ItemDataRole.UserRole)
        ]
        self.assertTrue(
            any(
                "Untick the filter" in text and "get a new task" in text
                for text in empty_rows
            )
        )

    def test_main_menu_dialog_is_deleted_when_closed(self) -> None:
        self.assertTrue(
            self.dialog.testAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        )

    def test_profile_reload_replaces_the_existing_menu_and_callback(self) -> None:
        original_mw = self._ui.mw
        window = QMainWindow()
        window.form = SimpleNamespace(menubar=window.menuBar())
        calls = []
        try:
            self._ui.mw = window
            self._ui.create_menu(lambda: calls.append("first"))
            menu = self._ui.create_menu(lambda: calls.append("second"))

            self.assertEqual(
                [action.text() for action in window.menuBar().actions()],
                ["AnkiScape"],
            )
            menu.actions()[0].trigger()
            self.assertEqual(calls, ["second"])
        finally:
            self._ui.mw = original_mw
            window.deleteLater()

    def test_thieving_support_panel_metadata_selection_lock_and_casual_toggle(self) -> None:
        from ankiscape.core.target_metadata import thieving_target_rows

        targets = {
            "pickpocket_man": {
                "display_name": "Man",
                "level": 1,
                "xp": 8,
                "group": "pickpocketing",
                "coins": 3,
            },
            "vegetable_stall": {
                "display_name": "Vegetable stall",
                "level": 2,
                "xp": 10,
                "group": "stalls",
            },
            "wall_safe": {
                "display_name": "Wall safe",
                "level": 50,
                "xp": 70,
                "group": "safes",
            },
            "blackjack_menaphite_thug": {
                "display_name": "Menaphite thug",
                "level": 65,
                "xp": 137.5,
                "group": "blackjacking",
                "quest_gate": "the_feud",
                "quest_gate_label": "The Feud",
            },
        }
        player_data = _make_player_data()
        player_data["thieving_level"] = 10
        player_data["current_thieving"] = "pickpocket_man"

        rows = thieving_target_rows(player_data, targets, {}, "pickpocket_man")
        self.assertEqual(
            [row.group for row in rows],
            ["pickpocketing", "stalls", "safes", "blackjacking"],
        )
        self.assertTrue(rows[0].current)
        self.assertTrue(rows[1].enabled)
        self.assertFalse(rows[2].enabled)
        self.assertIn("Locked: Thieving level 50", rows[2].label)
        self.assertIn("Locked due to: Thieving level 50", rows[2].tooltip)

        previous = {
            "targets": self._ui.THIEVING_TARGETS,
            "labels": self._ui.THIEVING_GROUP_LABELS,
            "order": self._ui.THIEVING_GROUP_ORDER,
            "default": self._ui.DEFAULT_THIEVING_TARGET,
            "images": self._ui.THIEVING_ITEM_IMAGES,
        }
        dialog = None
        try:
            self._ui.THIEVING_TARGETS = targets
            self._ui.THIEVING_GROUP_LABELS = {
                "pickpocketing": "Pickpocketing",
                "stalls": "Stalls",
                "safes": "Safes",
                "blackjacking": "Blackjacking",
            }
            self._ui.THIEVING_GROUP_ORDER = (
                "pickpocketing",
                "stalls",
                "safes",
                "blackjacking",
            )
            self._ui.DEFAULT_THIEVING_TARGET = "pickpocket_man"
            self._ui.THIEVING_ITEM_IMAGES = {}

            dialog = self._open(player_data, current_skill="Thieving")
            dialog.show()
            QApplication.processEvents()
            support = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Support")
            self.assertTrue(support.isVisible())
            skill_list = next(
                widget
                for widget in dialog.findChildren(QListWidget)
                if "Thieving" in [widget.item(i).text() for i in range(widget.count())]
            )
            self.assertTrue(any(skill_list.item(i).text() == "Thieving" for i in range(skill_list.count())))

            tree = dialog.findChild(QTreeWidget, "thievingTargetTree")
            self.assertIsNotNone(tree)
            self.assertEqual(
                [tree.topLevelItem(i).text(0).split("  (")[0] for i in range(tree.topLevelItemCount())],
                ["Pickpocketing", "Stalls", "Safes", "Blackjacking"],
            )
            self.assertEqual(
                tree.currentItem().data(0, Qt.ItemDataRole.UserRole),
                "pickpocket_man",
            )

            locked = next(
                item for item in _tree_items(tree)
                if item.data(0, Qt.ItemDataRole.UserRole) == "wall_safe"
            )
            self.assertTrue(locked.isDisabled())
            before = list(self._thieving_calls)
            tree.itemClicked.emit(locked, 0)
            tree.itemActivated.emit(locked, 0)
            QApplication.processEvents()
            self.assertEqual(self._thieving_calls, before)

            stall = next(
                item for item in _tree_items(tree)
                if item.data(0, Qt.ItemDataRole.UserRole) == "vegetable_stall"
            )
            self.assertFalse(stall.isDisabled())
            tree.itemClicked.emit(stall, 0)
            QApplication.processEvents()
            self.assertEqual(self._thieving_calls[-1], "vegetable_stall")

            fight_back = dialog.findChild(QCheckBox, "thievingFightBackCheck")
            self.assertFalse(fight_back.isChecked())
            fight_back.click()
            QApplication.processEvents()
            self.assertEqual(self._thieving_fight_back_calls[-1], True)
            self.assertTrue(player_data["thieving_fight_back_when_caught"])
        finally:
            self._ui.THIEVING_TARGETS = previous["targets"]
            self._ui.THIEVING_GROUP_LABELS = previous["labels"]
            self._ui.THIEVING_GROUP_ORDER = previous["order"]
            self._ui.DEFAULT_THIEVING_TARGET = previous["default"]
            self._ui.THIEVING_ITEM_IMAGES = previous["images"]
            if dialog is not None:
                dialog.deleteLater()

    def test_thieving_live_npc_rows_render_portraits_instead_of_loot_icons(self) -> None:
        from ankiscape.data.thieving_data import THIEVING_NPC_TARGET_IDS

        player_data = _make_player_data()
        player_data["thieving_level"] = 99
        player_data["current_thieving"] = "pickpocket_man"
        dialog = self._open(player_data, current_skill="Thieving")
        try:
            tree = dialog.findChild(QTreeWidget, "thievingTargetTree")
            rows = {
                item.data(0, Qt.ItemDataRole.UserRole): item
                for item in _tree_items(tree)
            }
            self.assertEqual(
                set(THIEVING_NPC_TARGET_IDS),
                {target_id for target_id in THIEVING_NPC_TARGET_IDS if target_id in rows},
            )
            for target_id in THIEVING_NPC_TARGET_IDS:
                self.assertFalse(rows[target_id].icon(0).isNull(), target_id)
                self.assertEqual(
                    self._ui.THIEVING_ITEM_IMAGES[target_id],
                    self._ui.THIEVING_NPC_IMAGES[target_id],
                )
        finally:
            dialog.deleteLater()

    def test_grave_banner_renders_live_recovery_state_and_disappears_after_reclaim(self) -> None:
        from ankiscape.logic_pure.logic_pure import (
            advance_combat_grave_review_pure,
            start_combat_grave_walk_pure,
        )

        player_data = _make_player_data()
        player_data.update({
            "combat_grave": {
                "items": ["Bronze sword", "Shark"],
                "reviews_remaining": 5,
                "source": "agility_failure",
                "loadout": {"weapon": "Bronze sword"},
            },
            "death_office": {
                "items": ["Wooden shield"],
                "source": "combat_stacked_grave",
            },
        })

        def start_walk():
            updated, ok = start_combat_grave_walk_pure(player_data)
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        player_data["combat_grave"]["travel_reviews"] = 1
        dialog = self._open(
            player_data,
            current_skill="Agility",
            on_start_grave_walk=start_walk,
        )
        try:
            dialog.show()
            QApplication.processEvents()
            banner = dialog.findChild(QPushButton, "graveRecoveryBanner")
            self.assertIsNotNone(banner)
            self.assertTrue(banner.isVisibleTo(dialog))
            self.assertIn("Gravestone: 2 items", banner.text())
            self.assertIn("expires after 5 more reviews", banner.text())
            self.assertIn("click to walk back", banner.text())
            self.assertIn("Death's Office: 1 items", banner.text())
            self.assertIn("reclaim for 100 coins", banner.text())
            self.assertIn("palette(text)", banner.styleSheet())
            self.assertNotIn("color: palette(mid)", banner.styleSheet().lower())
            self.assertTrue(banner.isEnabled())
            banner.click()
            QApplication.processEvents()
            self.assertEqual(player_data["combat_grave"]["walk_reviews_remaining"], 1)
        finally:
            dialog.deleteLater()

        player_data["death_office"] = {}
        updated = advance_combat_grave_review_pure(player_data)
        player_data.clear()
        player_data.update(updated)
        reclaimed_dialog = self._open(player_data, current_skill="Agility")
        try:
            reclaimed_dialog.show()
            QApplication.processEvents()
            banner = reclaimed_dialog.findChild(QPushButton, "graveRecoveryBanner")
            self.assertIsNotNone(banner)
            self.assertFalse(banner.isVisibleTo(reclaimed_dialog))
        finally:
            reclaimed_dialog.deleteLater()

    def test_agility_panel_renders_grouped_targets_locks_icon_and_commands(self) -> None:
        player_data = _make_player_data()
        player_data["agility_level"] = 1
        player_data["current_agility"] = "burthorpe_course"
        dialog = self._open(player_data, current_skill="Agility")
        try:
            dialog.show()
            QApplication.processEvents()
            self.assertEqual(_panel_title(dialog), "Agility — Lv 1")

            panel = dialog.findChild(QWidget, "agilitySkillPanel")
            tree = dialog.findChild(QTreeWidget, "agilityTargetTree")
            self.assertIsNotNone(panel)
            self.assertIsNotNone(tree)
            self.assertEqual(
                [tree.topLevelItem(i).text(0).split("  (")[0] for i in range(tree.topLevelItemCount())],
                ["Courses", "Activities"],
            )
            self.assertEqual(tree.currentItem().data(0, Qt.ItemDataRole.UserRole), "burthorpe_course")

            locked = _tree_row(tree, "gnome_advanced")
            self.assertTrue(locked.isDisabled())
            before = list(self._agility_calls)
            tree.itemClicked.emit(locked, 0)
            QApplication.processEvents()
            self.assertEqual(self._agility_calls, before)

            gnome = _tree_row(tree, "gnome_normal")
            self.assertFalse(gnome.isDisabled())
            tree.itemClicked.emit(gnome, 0)
            QApplication.processEvents()
            self.assertEqual(self._agility_calls[-1], "gnome_normal")

            skill_list = next(
                widget
                for widget in dialog.findChildren(QListWidget)
                if "Agility" in [widget.item(i).text() for i in range(widget.count())]
            )
            agility_item = next(
                skill_list.item(i) for i in range(skill_list.count())
                if skill_list.item(i).text() == "Agility"
            )
            self.assertFalse(agility_item.icon().isNull())
            self.assertIsNotNone(dialog.findChild(QLabel, "agilityStatusLine"))
            self.assertIsNotNone(dialog.findChild(QLabel, "agilityBenefitsLine"))
            # The control row is an activity-only surface: on a course the
            # panel has no command buttons at all. Shop purchases, ticket
            # redemptions and aura activation live in the Shop and Equipment
            # tabs now.
            controls = dialog.findChild(QWidget, "agilityRewardControls")
            self.assertTrue(controls is None or not controls.isVisibleTo(dialog))
            self.assertEqual(
                [
                    button.objectName()
                    for button in dialog.findChildren(QPushButton)
                    if button.objectName().startswith("agilityCommand::")
                ],
                [],
            )
            danger_auto_stop = dialog.findChild(
                QCheckBox, "activityDangerAutoStopCheckBox"
            )
            self.assertIsNotNone(danger_auto_stop)
            self.assertTrue(danger_auto_stop.isChecked())
            self.assertIn("AnkiScape safety option", danger_auto_stop.toolTip())
            danger_auto_stop.click()
            QApplication.processEvents()
            self.assertEqual(
                self._agility_command_calls[-1],
                ("set_activity_auto_stop", {"enabled": False}),
            )
            self.assertFalse(player_data["activity_auto_stop_on_danger"])

            auto_accept = dialog.findChild(
                QCheckBox, "agilityPitAutoAcceptCheckBox"
            )
            self.assertIsNotNone(auto_accept)
            self.assertTrue(auto_accept.isChecked())
            auto_accept.click()
            QApplication.processEvents()
            self.assertEqual(
                self._agility_command_calls[-1],
                ("set_pit_auto_accept", {"enabled": False}),
            )
            self.assertFalse(player_data["agility_pit_auto_accept"])
            self.assertFalse(
                any(
                    button.text() in {"Claim Pit XP", "Gamble Pit XP"}
                    for button in dialog.findChildren(QPushButton)
                )
            )

            self.assertIsNone(
                dialog.findChild(
                    QPushButton,
                    "agilityCommand::activate_agility_cape",
                )
            )
            # While the selected target is an activity, the row appears with
            # that activity's verbs. The Pit is invitation-gated, so drive it
            # through the pending-offer flow rather than forcing state.
            player_data["agility_level"] = 99
            player_data["agility_pit_offer"] = True
            player_data["agility_pit_origin_course"] = "burthorpe_course"
            player_data["inventory"] = {"Toy mouse": 1}
            player_data["equipment"] = {}
            accept_dialog = self._open(player_data, current_skill="Agility")
            try:
                accept = accept_dialog.findChild(QPushButton, "agilityPitAcceptButton")
                self.assertIsNotNone(accept)
                accept.click()
                QApplication.processEvents()
                self.assertEqual(player_data["current_agility"], "the_pit")

                controls = accept_dialog.findChild(QWidget, "agilityRewardControls")
                self.assertIsNotNone(controls)
                self.assertTrue(controls.isVisibleTo(accept_dialog))
                toy_button = accept_dialog.findChild(QPushButton, "agilityCommand::wind_toy_mouse")
                self.assertIsNotNone(toy_button)
                toy_button.click()
                QApplication.processEvents()
                self.assertEqual(self._agility_command_calls[-1], ("wind_toy_mouse", {}))
                leave_button = accept_dialog.findChild(QPushButton, "agilityCommand::abandon")
                self.assertIsNotNone(leave_button)
                self.assertEqual(leave_button.text(), "Leave The Pit")
            finally:
                accept_dialog.deleteLater()
            for label in (
                dialog.findChild(QLabel, "agilityStatusLine"),
                dialog.findChild(QLabel, "agilityBenefitsLine"),
            ):
                self.assertIn("palette(text)", label.styleSheet())
                self.assertNotIn("palette(mid)", label.styleSheet().lower())
        finally:
            dialog.deleteLater()

    def test_agility_panel_accepts_or_declines_pending_talent_scout_offer(self) -> None:
        player_data = _make_player_data()
        player_data.update(
            {
                "agility_level": 99,
                "current_agility": "gnome_normal",
                "agility_pit_offer": True,
                "agility_pit_origin_course": "gnome_normal",
                "agility_pit_auto_accept": False,
                "equipment": {"weapon": "Dragon longsword"},
            }
        )
        dialog = self._open(player_data, current_skill="Agility")

        invitation = dialog.findChild(QWidget, "agilityPitInvitationRow")
        self.assertIsNotNone(invitation)
        accept = dialog.findChild(QPushButton, "agilityPitAcceptButton")
        self.assertIsNotNone(accept)
        accept.click()
        QApplication.processEvents()

        self.assertEqual(
            self._agility_command_calls[-1],
            ("accept_pit_offer", {}),
        )
        self.assertEqual(player_data["current_agility"], "the_pit")
        self.assertEqual(player_data["inventory"]["Dragon longsword"], 1)

        declined_data = _make_player_data()
        declined_data.update(
            {
                "agility_level": 99,
                "current_agility": "gnome_normal",
                "agility_pit_offer": True,
                "agility_pit_origin_course": "gnome_normal",
                "agility_pit_auto_accept": False,
            }
        )
        declined_dialog = self._open(declined_data, current_skill="Agility")
        decline = declined_dialog.findChild(
            QPushButton, "agilityPitDeclineButton"
        )
        self.assertIsNotNone(decline)
        decline.click()
        QApplication.processEvents()

        self.assertEqual(
            self._agility_command_calls[-1],
            ("decline_pit_offer", {}),
        )
        self.assertFalse(declined_data["agility_pit_offer"])
        self.assertIsNone(
            declined_dialog.findChild(QWidget, "agilityPitInvitationRow")
        )

    def test_review_context_strip_is_compact_interactive_and_hides_when_empty(self) -> None:
        parent = QMainWindow()
        parent.resize(900, 620)
        parent.show()
        strip = self._ui.ReviewContextActionStrip(parent)
        calls = []
        strip.set_data(
            {
                "active": {
                    "family_id": "pit_reward",
                    "label": "Pit reward",
                    "detail": "320 Agility XP",
                    "options": (
                        {"id": "take_xp", "label": "Take XP"},
                        {"id": "gamble", "label": "Gamble"},
                    ),
                    "default_option": "take_xp",
                    "remembered_option": None,
                },
                "queued_count": 2,
            },
            lambda family_id, option_id: calls.append((family_id, option_id)),
        )
        QApplication.processEvents()

        self.assertTrue(strip.isVisible())
        self.assertLessEqual(
            len(strip.findChildren(QPushButton)),
            3,
        )
        take = strip.findChild(
            QPushButton, "reviewContextAction::pit_reward::take_xp"
        )
        gamble = strip.findChild(
            QPushButton, "reviewContextAction::pit_reward::gamble"
        )
        self.assertIsNotNone(take)
        self.assertIsNotNone(gamble)
        self.assertIn("Pit reward", take.accessibleName())
        self.assertIn("automatic on next answer", take.accessibleName())
        self.assertTrue(take.property("safeOption"))
        self.assertFalse(bool(gamble.property("safeOption")))
        self.assertNotEqual(take.focusPolicy(), Qt.FocusPolicy.NoFocus)
        self.assertIn("next card", take.toolTip())
        self.assertIn("2x, 1x, or 0.5x", gamble.toolTip())
        queue_badge = strip.findChild(QLabel, "reviewContextQueueBadge")
        self.assertTrue(queue_badge.isVisible())
        self.assertEqual(queue_badge.text(), "+2")
        self.assertEqual(
            queue_badge.accessibleName(),
            "Queued reviewer decisions",
        )
        gamble.click()
        QApplication.processEvents()
        self.assertEqual(calls, [("pit_reward", "gamble")])
        self.assertGreaterEqual(strip.x(), 8)
        self.assertGreaterEqual(strip.y(), 8)

        strip.set_data({"active": None, "queued_count": 0})
        QApplication.processEvents()
        self.assertFalse(strip.isVisible())
        strip.deleteLater()
        parent.deleteLater()

    def test_farming_sheet_is_openable_without_train_button_or_target_prompt(self) -> None:
        farming_dialog = self._open(_make_player_data(), current_skill="Mining", initial_skill="Farming")
        farming_dialog.show()
        farming_dialog.resize(900, 560)
        for _ in range(6):
            QApplication.processEvents()
        panel = farming_dialog.findChild(QWidget, "farmingSkillPanel")
        self.assertIsNotNone(panel)
        self.assertIsNotNone(farming_dialog.findChild(QWidget, "farmingFarmSheet"))
        self.assertEqual(len([widget for widget in farming_dialog.findChildren(QWidget) if widget.objectName().startswith("farmingPatchCard::")]), 52)
        self.assertEqual(len([widget for widget in farming_dialog.findChildren(QLabel) if widget.objectName().startswith("farmingPatchVisual::")]), 52)
        self.assertEqual(len([widget for widget in farming_dialog.findChildren(QLabel) if widget.objectName().startswith("farmingCompostBinVisual::")]), 6)
        self.assertFalse(any(button.text() in {"Train this skill", "Currently training"} and button.isVisible() for button in farming_dialog.findChildren(QPushButton)))
        self.assertFalse(any(label.text() == "Select a target" and label.isVisible() for label in farming_dialog.findChildren(QLabel)))
        self.assertLessEqual(farming_dialog.minimumHeight(), 560)
        scroll = farming_dialog.findChild(QWidget, "farmingFarmScroll")
        self.assertGreater(scroll.height(), 0)
        self.assertIsNone(
            farming_dialog.findChild(
                QComboBox,
                "farmingPatchCropCombo::varrock_white_tree",
            )
        )
        white_tree_summary = farming_dialog.findChild(
            QLabel,
            "farmingPatchSummary::varrock_white_tree",
        )
        self.assertEqual(
            white_tree_summary.text(),
            "White Tree · Requires Garden of Tranquillity.",
        )
        white_tree_current = farming_dialog.findChild(
            QLabel,
            "farmingPatchCurrent::varrock_white_tree",
        )
        self.assertEqual(
            white_tree_current.text(),
            "Current: Locked",
        )

    def test_farming_livid_allotment_identifies_its_one_use_lifecycle(self) -> None:
        player_data = _make_player_data()
        player_data["farm_livid_patch_active"] = True
        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        QApplication.processEvents()

        summary = dialog.findChild(
            QLabel,
            "farmingPatchSummary::livid_farm_allotment",
        )
        self.assertIsNotNone(summary)
        self.assertIn("one-use", summary.text())
        dialog.deleteLater()

    def test_farming_jade_vine_policy_and_seed_recovery_are_visible_direct_actions(self) -> None:
        player_data = _make_player_data()
        player_data["quests"]["back_to_my_roots"] = {"completed": True}
        player_data["farming_level"] = 53
        player_data["inventory"]["Jade vine seed"] = 0
        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(
            QToolButton, "farmingLocationToggle::ardougne"
        ).click()
        QApplication.processEvents()
        dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::handelmort_jade_vine",
        ).click()
        QApplication.processEvents()
        policy = dialog.findChild(
            QComboBox,
            "farmingJadeVinePolicyCombo::handelmort_jade_vine",
        )
        status = dialog.findChild(
            QLabel,
            "farmingJadeVineStatus::handelmort_jade_vine",
        )
        claim = dialog.findChild(
            QPushButton,
            "farmingJadeVineClaimSeed::handelmort_jade_vine",
        )
        self.assertIsNotNone(policy)
        self.assertEqual(policy.count(), 3)
        self.assertIn("Keep tame", status.text())
        self.assertTrue(claim.isEnabled())

        policy.setCurrentIndex(policy.findData("train_slayer"))
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(player_data["farm_jade_vine_policy"], "train_slayer")
        claim = dialog.findChild(
            QPushButton,
            "farmingJadeVineClaimSeed::handelmort_jade_vine",
        )
        claim.click()
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(player_data["inventory"]["Jade vine seed"], 1)
        dialog.deleteLater()

    def test_farming_jade_vine_horacio_payment_is_disclosed_and_confirmed(self) -> None:
        from ankiscape.logic.farming_logic import default_farming_state_pure

        player_data = _make_player_data()
        player_data.update(default_farming_state_pure())
        player_data["quests"]["back_to_my_roots"] = {"completed": True}
        player_data["farming_level"] = 53
        player_data["inventory"].update({
            "Coconut": 5,
            "Watermelon": 5,
        })
        player_data["farm_patches"]["handelmort_jade_vine"].update({
            "crop_id": "jade_vine",
            "last_crop_id": "jade_vine",
            "stage": 6,
            "health_checked": True,
            "jade_state": "prunable",
            "produce_count": 0,
            "next_regrowth_at": 60,
            "plan": {
                "crop_id": "jade_vine",
                "compost_tier": "none",
                "protection_intent": False,
                "watering_intent": False,
                "cure_intent": True,
                "cure_route_preference": "item_first",
            },
        })
        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingLocationToggle::ardougne").click()
        QApplication.processEvents()
        dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::handelmort_jade_vine",
        ).click()
        QApplication.processEvents()
        policy = dialog.findChild(
            QComboBox,
            "farmingJadeVinePolicyCombo::handelmort_jade_vine",
        )
        self.assertIn("5 coconuts + 5 watermelons", policy.itemText(2))

        original_question = self._ui.QMessageBox.question
        try:
            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.No
            )
            policy.setCurrentIndex(policy.findData("train_farming"))
            QApplication.processEvents()
            self.assertEqual(player_data["farm_jade_vine_policy"], "keep_tame")
            self.assertEqual(player_data["inventory"]["Coconut"], 5)

            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.Yes
            )
            policy.setCurrentIndex(policy.findData("train_farming"))
            for _ in range(5):
                QApplication.processEvents()
            self.assertEqual(player_data["farm_jade_vine_policy"], "train_farming")
            self.assertEqual(player_data["inventory"]["Coconut"], 0)
            self.assertEqual(player_data["inventory"]["Watermelon"], 0)
            self.assertIsNone(
                player_data["farm_patches"]["handelmort_jade_vine"]["crop_id"]
            )
        finally:
            self._ui.QMessageBox.question = original_question
            dialog.deleteLater()

    def test_farming_willow_branch_action_is_visible_enabled_and_queueable(
        self,
    ) -> None:
        from ankiscape.logic.farming_logic import (
            advance_farm_clock_pure,
            default_farming_state_pure,
            execute_farm_field_step_pure,
        )

        player_data = _make_player_data()
        player_data["farming_level"] = 99
        player_data.update(default_farming_state_pure())
        player_data["inventory"] = {
            "Rake": 1,
            "Spade": 1,
            "Magic secateurs": 1,
            "Willow sapling": 1,
        }
        player_data, ok, _ = execute_farm_field_step_pure(
            player_data,
            {
                "kind": "plant",
                "patch_id": "lumbridge_tree",
                "crop_id": "willow",
            },
        )
        self.assertTrue(ok)
        player_data, _ = advance_farm_clock_pure(
            player_data, 40, lambda: 1.0
        )
        player_data, ok, _ = execute_farm_field_step_pure(
            player_data,
            {"kind": "check_health", "patch_id": "lumbridge_tree"},
        )
        self.assertTrue(ok)
        player_data, _ = advance_farm_clock_pure(
            player_data, 5, lambda: 1.0
        )

        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        location = dialog.findChild(
            QToolButton,
            "farmingLocationToggle::lumbridge",
        )
        if not location.isChecked():
            location.click()
            QApplication.processEvents()
        expand = dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::lumbridge_tree",
        )
        if not expand.isChecked():
            expand.click()
            QApplication.processEvents()

        branch = dialog.findChild(
            QPushButton,
            "farmingPatchBranchButton::lumbridge_tree",
        )
        primary = dialog.findChild(
            QPushButton,
            "farmingPatchPrimaryAction::lumbridge_tree",
        )
        self.assertIsNotNone(branch)
        self.assertTrue(branch.isVisible())
        self.assertTrue(branch.isEnabled())
        self.assertEqual(branch.text(), "Queue prune 6 branches")
        self.assertEqual(primary.text(), "Queue chop")
        scroll = dialog.findChild(QScrollArea, "farmingFarmScroll")
        self.assertIsNotNone(scroll)
        scroll.ensureWidgetVisible(branch)
        for _ in range(3):
            QApplication.processEvents()
        branch_top = branch.mapTo(
            scroll.viewport(),
            branch.rect().topLeft(),
        ).y()
        branch_bottom = branch.mapTo(
            scroll.viewport(),
            branch.rect().bottomLeft(),
        ).y()
        self.assertGreaterEqual(branch_top, 0)
        self.assertLess(branch_bottom, scroll.viewport().height())

        branch.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(
            self._farming_calls[-1],
            (
                "queue_action",
                {
                    "patch_id": "lumbridge_tree",
                    "kind": "harvest",
                    "details": {},
                },
            ),
        )
        self.assertEqual(
            player_data["farm_queue"][0]["kind"],
            "harvest",
        )
        dialog.deleteLater()

    def test_farming_plan_change_calls_unified_callback_immediately(self) -> None:
        farming_dialog = self._open(_make_player_data(), current_skill="Mining", initial_skill="Farming")
        farming_dialog.show()
        for _ in range(4):
            QApplication.processEvents()
        combo = farming_dialog.findChild(QComboBox, "farmingPatchCropCombo::falador_allotment_north")
        self.assertIsNotNone(combo)
        potato = combo.findData("potato")
        self.assertGreaterEqual(potato, 0)
        combo.setCurrentIndex(potato)
        QApplication.processEvents()
        self.assertTrue(self._farming_calls)
        action_id, payload = self._farming_calls[-1]
        self.assertEqual(action_id, "set_plan")
        self.assertEqual(payload["patch_id"], "falador_allotment_north")
        self.assertEqual(payload["crop_id"], "potato")

    def test_farming_sheet_can_activate_owned_juju_potion(self) -> None:
        player_data = _make_player_data()
        player_data["inventory"] = {"Juju farming potion (3)": 1}
        farming_dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        farming_dialog.show()
        for _ in range(4):
            QApplication.processEvents()

        activate = farming_dialog.findChild(QPushButton, "farmingActivateJujuButton")
        self.assertIsNotNone(activate)
        self.assertTrue(activate.isEnabled())
        self.assertIn("(3)", activate.text())
        activate.click()
        QApplication.processEvents()

        self.assertEqual(
            self._farming_calls[-1],
            ("activate_juju_farming_potion", {"item_name": "Juju farming potion (3)"}),
        )
        self.assertEqual(player_data["inventory"].get("Juju farming potion (3)", 0), 0)
        self.assertEqual(player_data["inventory"]["Juju farming potion (2)"], 1)
        self.assertGreater(player_data["farm_juju_active_until"], 0)

    def test_farming_stats_selector_is_present_but_farming_is_not_review_active(self) -> None:
        farming_button = _find_stats_button(self.dialog, "farming")
        self.assertEqual(
            farming_button.accessibleName(),
            "Farming, current level 33, base level 33",
        )
        skill_list = _find_skill_list(self.dialog)
        farming_item = next(skill_list.item(i) for i in range(skill_list.count()) if skill_list.item(i).text() == "Farming")
        self.assertTrue(bool(farming_item.flags() & Qt.ItemFlag.ItemIsEnabled))

    def test_farming_sheet_geometry_is_stable_at_default_and_laptop_heights_in_dark_mode(self) -> None:
        old_palette = QApplication.palette()
        old_style = QApplication.style().objectName()
        dark = QPalette()
        dark.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        dark.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        dark.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
        dark.setColor(QPalette.ColorRole.ButtonText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Mid, QColor(95, 95, 95))
        QApplication.setStyle("Fusion")
        QApplication.setPalette(dark)
        dialog = None
        try:
            dialog = self._open(_make_player_data(), current_skill="Mining", initial_skill="Farming")
            dialog.show()
            for _ in range(6):
                QApplication.processEvents()
            scroll = dialog.findChild(QWidget, "farmingFarmScroll")
            sheet = dialog.findChild(QWidget, "farmingFarmSheet")
            self.assertGreater(dialog.height(), 0)
            self.assertGreater(scroll.viewport().height(), 0)
            self.assertGreater(sheet.height(), scroll.viewport().height())
            self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)

            dialog.resize(900, 560)
            for _ in range(6):
                QApplication.processEvents()
            self.assertEqual((dialog.width(), dialog.height()), (900, 560))
            self.assertLessEqual(dialog.minimumHeight(), 560)
            self.assertGreater(scroll.viewport().height(), 0)
            self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
            text = dialog.palette().color(QPalette.ColorRole.Text)
            base = dialog.palette().color(QPalette.ColorRole.Base)
            self.assertGreater(text.lightness(), base.lightness())
        finally:
            if dialog is not None:
                dialog.deleteLater()
            QApplication.setPalette(old_palette)
            QApplication.setStyle(old_style)

    def test_farming_location_and_patch_details_use_progressive_disclosure(self) -> None:
        dialog = self._open(_make_player_data(), current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        location = dialog.findChild(QToolButton, "farmingLocationToggle::falador")
        card = dialog.findChild(QWidget, "farmingPatchCard::falador_allotment_north")
        expand = dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north")
        details = dialog.findChild(QWidget, "farmingPatchDetails::falador_allotment_north")
        self.assertFalse(location.isChecked())
        self.assertFalse(card.isVisible())
        self.assertFalse(details.isVisible())

        location.click()
        for _ in range(3):
            QApplication.processEvents()
        self.assertTrue(location.isChecked())
        self.assertTrue(card.isVisible())
        self.assertFalse(details.isVisible())
        expand.click()
        for _ in range(3):
            QApplication.processEvents()
        self.assertTrue(expand.isChecked())
        self.assertTrue(details.isVisible())
        dialog.deleteLater()

    def test_disabled_farming_controls_cannot_mutate_state(self) -> None:
        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {"Rake": 1, "Seed dibber": 1, "Potato seed": 2}
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        location = dialog.findChild(QToolButton, "farmingLocationToggle::falador")
        location.click()
        QApplication.processEvents()
        expand = dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north")
        expand.click()
        QApplication.processEvents()
        combo = dialog.findChild(QComboBox, "farmingPatchCropCombo::falador_allotment_north")
        watermelon_index = combo.findData("watermelon")
        self.assertGreaterEqual(watermelon_index, 0)
        self.assertFalse(combo.model().item(watermelon_index).isEnabled())
        before = dict(player_data.get("farm_plans", {}))
        combo.setCurrentIndex(watermelon_index)
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(player_data.get("farm_plans", {}), before)
        self.assertIsNone(player_data.get("farm_plans", {}).get("falador_allotment_north"))
        dialog.deleteLater()

    def test_farming_plan_and_queue_actions_refresh_the_visible_sheet_immediately(self) -> None:
        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 6}
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingLocationToggle::falador").click()
        QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north").click()
        QApplication.processEvents()
        combo = dialog.findChild(QComboBox, "farmingPatchCropCombo::falador_allotment_north")
        combo.setCurrentIndex(combo.findData("potato"))
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(player_data["farm_plans"]["falador_allotment_north"]["crop_id"], "potato")
        summary = dialog.findChild(QLabel, "farmingPatchSummary::falador_allotment_north")
        primary = dialog.findChild(QPushButton, "farmingPatchPrimaryAction::falador_allotment_north")
        self.assertIn("Empty", summary.text())
        self.assertEqual(primary.text(), "Queue plant")
        self.assertTrue(primary.isEnabled())

        primary.click()
        for _ in range(5):
            QApplication.processEvents()
        queue = dialog.findChild(QListWidget, "farmingQueueList")
        summary = dialog.findChild(QLabel, "farmingSummaryLabel")
        self.assertEqual(queue.count(), 1)
        self.assertIn("1 queued", summary.text())
        self.assertEqual(queue.item(0).data(Qt.ItemDataRole.UserRole), "farm_step_00000001")
        dialog.deleteLater()

    def test_farming_protection_checkbox_defers_payment_until_full_run(self) -> None:
        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {
            "Rake": 1,
            "Seed dibber": 1,
            "Spade": 1,
            "Potato seed": 3,
            "Compost": 2,
        }
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingLocationToggle::falador").click()
        QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north").click()
        QApplication.processEvents()
        combo = dialog.findChild(QComboBox, "farmingPatchCropCombo::falador_allotment_north")
        combo.setCurrentIndex(combo.findData("potato"))
        for _ in range(4):
            QApplication.processEvents()
        protect = dialog.findChild(QCheckBox, "farmingPatchProtectionCheck::falador_allotment_north")
        protect.setChecked(True)
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(self._farming_calls[-1][0], "set_plan")
        self.assertTrue(self._farming_calls[-1][1]["protection_intent"])
        self.assertEqual(player_data["inventory"]["Compost"], 2)
        self.assertFalse(player_data["farm_plans"]["falador_allotment_north"]["protection_paid"])
        full_run = dialog.findChild(QPushButton, "farmingQueueFullRunButton")
        self.assertTrue(full_run.isEnabled())
        full_run.click()
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(player_data["inventory"]["Compost"], 0)
        self.assertFalse(player_data["farm_plans"]["falador_allotment_north"]["protection_paid"])
        self.assertTrue(player_data["farm_queue"][0]["protection_paid"])
        self.assertEqual(player_data["farm_queue"][0]["protection_payment"], {"Compost": 2})
        protect = dialog.findChild(QCheckBox, "farmingPatchProtectionCheck::falador_allotment_north")
        self.assertTrue(protect.isChecked())
        self.assertTrue(protect.isEnabled())
        dialog.deleteLater()

    def test_farming_cure_preference_is_a_compact_saved_toggle(self) -> None:
        from ankiscape.logic.farming_logic import CURE_PLANT_SPELL_FIRST, set_farm_plan_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 99
        planned, ok, _ = set_farm_plan_pure(
            player_data,
            "falador_allotment_north",
            "potato",
        )
        self.assertTrue(ok)
        player_data.clear()
        player_data.update(planned)
        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingLocationToggle::falador").click()
        QApplication.processEvents()
        dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::falador_allotment_north",
        ).click()
        QApplication.processEvents()

        combo = dialog.findChild(
            QComboBox,
            "farmingPatchCurePreferenceCombo::falador_allotment_north",
        )
        self.assertEqual(combo.count(), 2)
        self.assertEqual(combo.itemText(0), "Plant cure first")
        self.assertEqual(combo.itemText(1), "Cure Plant first")
        combo.setCurrentIndex(combo.findData(CURE_PLANT_SPELL_FIRST))
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(
            player_data["farm_plans"]["falador_allotment_north"][
                "cure_route_preference"
            ],
            CURE_PLANT_SPELL_FIRST,
        )
        self.assertEqual(
            self._farming_calls[-1][1]["cure_route_preference"],
            CURE_PLANT_SPELL_FIRST,
        )
        dialog.deleteLater()

    def test_farming_preset_row_applies_plans_without_queuing(self) -> None:
        from ankiscape.logic.farming_logic import save_farm_preset_pure, set_farm_plan_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 99
        planned, ok, _ = set_farm_plan_pure(
            player_data,
            "falador_allotment_north",
            "potato",
            watering_intent=False,
            cure_intent=True,
        )
        self.assertTrue(ok)
        saved, ok, _ = save_farm_preset_pure(
            planned, "Morning run", ("falador_allotment_north",)
        )
        self.assertTrue(ok)
        preset_id = saved["farm_selected_preset"]
        changed, ok, _ = set_farm_plan_pure(
            saved, "falador_allotment_north", "onion"
        )
        self.assertTrue(ok)
        player_data.clear()
        player_data.update(changed)

        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        for _ in range(5):
            QApplication.processEvents()

        preset = dialog.findChild(QComboBox, "farmingPresetCombo")
        modified = dialog.findChild(QLabel, "farmingPresetModifiedLabel")
        apply_button = dialog.findChild(QPushButton, "farmingPresetApplyButton")
        manage = dialog.findChild(QToolButton, "farmingPresetManageButton")
        self.assertEqual(preset.currentData(), preset_id)
        self.assertEqual(modified.text(), "modified")
        self.assertTrue(apply_button.isEnabled())
        self.assertIsNotNone(manage.menu())
        self.assertEqual(player_data["farm_queue"], [])

        apply_button.click()
        for _ in range(5):
            QApplication.processEvents()

        self.assertEqual(
            player_data["farm_plans"]["falador_allotment_north"]["crop_id"],
            "potato",
        )
        self.assertEqual(player_data["farm_queue"], [])
        self.assertEqual(
            dialog.findChild(QLabel, "farmingPresetModifiedLabel").text(),
            "",
        )
        dialog.deleteLater()

    def test_farming_compost_bin_selects_an_available_input_and_gates_fill_by_selection(self) -> None:
        player_data = _make_player_data()
        player_data["inventory"] = {"Potato": 15}
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        combo = dialog.findChild(QComboBox, "farmingCompostBinInputCombo::falador_bin")
        fill = dialog.findChild(QPushButton, "farmingCompostBinFillButton::falador_bin")
        self.assertEqual(combo.currentData(), "Potato")
        self.assertTrue(fill.isEnabled())

        barley_index = combo.findData("Barley")
        self.assertGreaterEqual(barley_index, 0)
        combo.setCurrentIndex(barley_index)
        QApplication.processEvents()
        self.assertFalse(fill.isEnabled())
        combo.setCurrentIndex(combo.findData("Potato"))
        QApplication.processEvents()
        self.assertTrue(fill.isEnabled())
        fill.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(player_data["inventory"]["Potato"], 0)
        self.assertEqual(player_data["farm_compost_bins"]["falador_bin"]["status"], "filling")
        dialog.deleteLater()

    def test_farming_livid_scroll_button_activates_and_reports_remaining_uses(self) -> None:
        from ankiscape.data.farming_data import LIVID_FARM_PROTECTION_SCROLL
        from ankiscape.logic.farming_logic import execute_farm_field_step_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 99
        player_data["inventory"] = {
            "Rake": 1,
            "Spade": 1,
            "Oak sapling": 1,
            LIVID_FARM_PROTECTION_SCROLL: 1,
        }
        updated, ok, _ = execute_farm_field_step_pure(
            player_data,
            {
                "kind": "plant",
                "patch_id": "lumbridge_tree",
                "crop_id": "oak",
            },
        )
        self.assertTrue(ok)
        player_data.clear()
        player_data.update(updated)

        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        location = dialog.findChild(
            QToolButton,
            "farmingLocationToggle::lumbridge",
        )
        if not location.isChecked():
            location.click()
            QApplication.processEvents()
        expand = dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::lumbridge_tree",
        )
        if not expand.isChecked():
            expand.click()
            QApplication.processEvents()

        button = dialog.findChild(
            QPushButton,
            "farmingPatchLividProtectionButton::lumbridge_tree",
        )
        self.assertIsNotNone(button)
        self.assertTrue(button.isEnabled())
        self.assertGreaterEqual(button.width(), button.sizeHint().width())
        self.assertIn("next nine plantings", button.toolTip())
        button.click()
        for _ in range(5):
            QApplication.processEvents()

        self.assertTrue(
            player_data["farm_patches"]["lumbridge_tree"]["livid_protected"]
        )
        self.assertEqual(
            player_data["farm_livid_protection_uses_remaining"],
            9,
        )
        status = dialog.findChild(QLabel, "farmingLividProtectionStatus")
        self.assertTrue(status.isVisible())
        self.assertIn("Oak", status.text())
        self.assertIn("9 plantings left", status.text())
        current = dialog.findChild(
            QLabel,
            "farmingPatchCurrent::lumbridge_tree",
        )
        self.assertIn("Protection: Livid scroll", current.text())
        refreshed = dialog.findChild(
            QPushButton,
            "farmingPatchLividProtectionButton::lumbridge_tree",
        )
        self.assertFalse(refreshed.isEnabled())
        dialog.deleteLater()

    def test_farming_patch_actions_keep_readable_widths_at_supported_dialog_sizes(self) -> None:
        from ankiscape.logic.farming_logic import set_farm_plan_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {
            "Rake": 1,
            "Seed dibber": 1,
            "Spade": 1,
            "Potato seed": 3,
            "Compost": 2,
        }
        updated, ok, _ = set_farm_plan_pure(player_data, "falador_allotment_north", "potato")
        self.assertTrue(ok)
        player_data.clear()
        player_data.update(updated)
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        for width, height in ((720, 540), (900, 560)):
            dialog.resize(width, height)
            for _ in range(5):
                QApplication.processEvents()
            self.assertEqual((dialog.width(), dialog.height()), (width, height))
            location = dialog.findChild(QToolButton, "farmingLocationToggle::falador")
            if not location.isChecked():
                location.click()
                QApplication.processEvents()
            expand = dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north")
            if not expand.isChecked():
                expand.click()
                QApplication.processEvents()
            buttons = [
                dialog.findChild(QPushButton, "farmingPatchPlanButton::falador_allotment_north"),
                dialog.findChild(QPushButton, "farmingPatchPrimaryAction::falador_allotment_north"),
                dialog.findChild(QPushButton, "farmingPatchHarvestReplantButton::falador_allotment_north"),
            ]
            for button in buttons:
                self.assertIsNotNone(button)
                self.assertGreaterEqual(button.width(), button.sizeHint().width())
        dialog.deleteLater()

    def test_farming_queue_selection_reorder_remove_clear_and_full_run(self) -> None:
        from ankiscape.logic.farming_logic import set_farm_plan_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 6}
        for patch_id in ("falador_allotment_north", "falador_allotment_south"):
            updated, ok, _ = set_farm_plan_pure(player_data, patch_id, "potato")
            self.assertTrue(ok)
            player_data.clear()
            player_data.update(updated)
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        full_run = dialog.findChild(QPushButton, "farmingQueueFullRunButton")
        self.assertTrue(full_run.isEnabled())
        full_run.click()
        for _ in range(5):
            QApplication.processEvents()
        queue = dialog.findChild(QListWidget, "farmingQueueList")
        self.assertEqual(queue.count(), 2)
        first_id = queue.item(0).data(Qt.ItemDataRole.UserRole)
        second_id = queue.item(1).data(Qt.ItemDataRole.UserRole)
        queue.setCurrentRow(1)
        QApplication.processEvents()
        up = dialog.findChild(QPushButton, "farmingQueueMoveUpButton")
        self.assertTrue(up.isEnabled())
        up.click()
        for _ in range(4):
            QApplication.processEvents()
        queue = dialog.findChild(QListWidget, "farmingQueueList")
        self.assertEqual(queue.item(0).data(Qt.ItemDataRole.UserRole), second_id)
        self.assertEqual(queue.item(1).data(Qt.ItemDataRole.UserRole), first_id)

        queue.setCurrentRow(0)
        QApplication.processEvents()
        dialog.findChild(QPushButton, "farmingQueueRemoveButton").click()
        for _ in range(4):
            QApplication.processEvents()
        queue = dialog.findChild(QListWidget, "farmingQueueList")
        self.assertEqual(queue.count(), 1)
        self.assertEqual(queue.item(0).data(Qt.ItemDataRole.UserRole), first_id)
        dialog.findChild(QPushButton, "farmingQueueClearButton").click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(dialog.findChild(QListWidget, "farmingQueueList").count(), 0)
        self.assertEqual(player_data["farm_queue"], [])
        dialog.deleteLater()

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

    def test_bank_carried_summary_counts_stackable_quantities_as_one_slot(self) -> None:
        player_data = _make_player_data()
        player_data["carried_inventory"] = {
            "combat_target": {"Air rune": 5000, "Lobster": 2}
        }
        dialog = self._open(
            player_data,
            carried_stackable_names=frozenset({"Air rune"}),
        )

        summary = dialog.findChild(QLabel, "carriedInventorySummary")
        self.assertIsNotNone(summary)
        self.assertIn("3 slot(s) held", summary.text())
        dialog.deleteLater()

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

        quantity_calls: list = []
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
            on_set_carried_layout_quantity=lambda name, quantity: quantity_calls.append(
                (name, quantity)
            ),
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

        # Clicking a filled cell edits its absolute quantity via the callback.
        original_get_int = self._ui.QInputDialog.getInt
        self._ui.QInputDialog.getInt = lambda *a, **k: (7, True)
        try:
            cells[0].click()
            QApplication.processEvents()
        finally:
            self._ui.QInputDialog.getInt = original_get_int
        self.assertIn(("Iron ore", 7), quantity_calls)

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
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

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
        self.assertIn("Services", labels)

    def test_grand_exchange_tab_renders_period_six_slots_and_routes_an_offer(self) -> None:
        from ankiscape.logic.grand_exchange_logic import (
            GE_SLOT_COUNT,
            apply_ge_frontend_action_pure,
            ge_frontend_projection_pure,
        )

        player = _make_player_data()
        player["inventory"] = {"Coins": 10_000, "Logs": 20}
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            },
            "Coal": {
                "guide_price": 200,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "ore",
            },
        }
        calls = []

        def projection():
            return ge_frontend_projection_pure(player, item_catalog=catalog)

        def action(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated, info = apply_ge_frontend_action_pure(
                player,
                action_id,
                payload,
                item_catalog=catalog,
            )
            if info.get("ok") and action_id != "preview_offer":
                player.clear()
                player.update(updated)
            return {**info, "projection": projection()}

        dialog = self._open(
            player,
            get_ge_projection=projection,
            on_ge_action=action,
        )
        _open_ge_tab(dialog)

        slots = [
            dialog.findChild(QToolButton, f"geOfferSlot{index}")
            for index in range(1, GE_SLOT_COUNT + 1)
        ]
        self.assertTrue(all(slot is not None for slot in slots))
        slots_grid = dialog.findChild(QWidget, "geOfferSlots").layout()
        self.assertEqual(
            [
                slots_grid.getItemPosition(slots_grid.indexOf(slot))[:2]
                for slot in slots
            ],
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)],
        )
        self.assertIsNone(
            dialog.findChild(QToolButton, f"geOfferSlot{GE_SLOT_COUNT + 1}")
        )
        self.assertIsNone(
            dialog.findChild(QPushButton, "gePriceMinus20Button")
        )
        self.assertIsNone(
            dialog.findChild(QPushButton, "gePricePlus20Button")
        )
        self.assertTrue(all("Empty offer" in slot.text() for slot in slots))
        self.assertEqual(
            dialog.findChild(QLabel, "geCoinBalanceLabel").text(),
            "10,000 Coins",
        )
        self.assertIn(
            "guide price",
            dialog.findChild(QSpinBox, "geLowPricePercentSpin").toolTip(),
        )
        self.assertIn(
            "guide price",
            dialog.findChild(QSpinBox, "geHighPriceMultiplierSpin").toolTip(),
        )

        dialog.findChild(QToolButton, "geOfferSafetyToggle").click()
        dialog.findChild(QSpinBox, "geHighValueConfirmationSpin").setValue(
            500_000
        )
        dialog.findChild(QSpinBox, "geLowPricePercentSpin").setValue(20)
        dialog.findChild(QSpinBox, "geHighPriceMultiplierSpin").setValue(5)
        dialog.findChild(QPushButton, "geApplyOfferSafetyButton").click()
        QApplication.processEvents()
        self.assertEqual(
            player["ge_settings"],
            {
                "high_value_confirmation": 500_000,
                "low_price_multiplier": 0.2,
                "high_price_multiplier": 5.0,
            },
        )

        item_list = dialog.findChild(QListWidget, "geItemList")
        self.assertIsNotNone(item_list)
        self.assertEqual(item_list.count(), 2)
        self.assertTrue(all("Coins" in text for text in _list_texts(item_list)))
        search = dialog.findChild(QLineEdit, "geItemSearchInput")
        search.setText("no such exchange item")
        QApplication.processEvents()
        self.assertEqual(
            item_list.item(0).text(),
            "No exchangeable items match your search.",
        )
        search.clear()
        QApplication.processEvents()
        logs_row = next(
            index
            for index in range(item_list.count())
            if item_list.item(index).data(Qt.ItemDataRole.UserRole)["item_name"]
            == "Logs"
        )
        item_list.setCurrentRow(logs_row)
        QApplication.processEvents()
        self.assertIn(
            "Buy limit per 40 cards: 25,000",
            dialog.findChild(QLabel, "geSelectedItemMeta").text(),
        )
        dialog.findChild(QPushButton, "gePricePlus5Button").click()
        self.assertEqual(
            dialog.findChild(QSpinBox, "geOfferPriceSpin").value(),
            105,
        )
        dialog.findChild(QPushButton, "geSubmitOfferButton").click()
        QApplication.processEvents()

        self.assertEqual(
            [action_id for action_id, _payload in calls[-2:]],
            ["preview_offer", "place_offer"],
        )
        self.assertIn("BUY · Logs", slots[0].text())
        self.assertEqual(player["inventory"]["Coins"], 9_895)

        slots[0].click()
        dialog.findChild(QPushButton, "geEditOfferButton").click()
        dialog.findChild(QSpinBox, "geOfferQuantitySpin").setValue(2)
        dialog.findChild(QPushButton, "gePriceMinus5Button").click()
        dialog.findChild(QPushButton, "geSubmitOfferButton").click()
        QApplication.processEvents()

        self.assertEqual(calls[-1][0], "edit_offer")
        self.assertEqual(
            player["ge_player_orders"][0]["remaining_quantity"],
            2,
        )
        # -5% compounds off the price showing in the spin box (105 from the
        # earlier +5%), not off the guide price. 105 * 95 / 100 truncates to 99,
        # so a round trip does NOT return to the guide price of 100 — that is
        # the period client's behaviour, and the Guide button is the exact reset
        # it provides for precisely this reason.
        self.assertEqual(
            player["ge_player_orders"][0]["submitted_unit_price"],
            99,
        )
        self.assertIn("0/2 filled", slots[0].text())

        coal_row = next(
            index
            for index in range(item_list.count())
            if item_list.item(index).data(Qt.ItemDataRole.UserRole)["item_name"]
            == "Coal"
        )
        item_list.setCurrentRow(coal_row)
        QApplication.processEvents()
        self.assertFalse(slots[0].isChecked())
        self.assertFalse(
            dialog.findChild(QPushButton, "geCancelOfferButton").isEnabled()
        )
        self.assertIn(
            "Select an occupied slot",
            dialog.findChild(QLabel, "geOrderDetailLabel").text(),
        )

        side = dialog.findChild(QComboBox, "geOfferSideCombo")
        side.setCurrentIndex(side.findData("sell"))
        QApplication.processEvents()
        self.assertEqual(item_list.count(), 1)
        self.assertEqual(
            item_list.item(0).data(Qt.ItemDataRole.UserRole)["item_name"],
            "Logs",
        )
        dialog.deleteLater()

    def test_grand_exchange_empty_sell_side_names_the_owned_item_state(self) -> None:
        from ankiscape.logic.grand_exchange_logic import ge_frontend_projection_pure

        player = _make_player_data()
        player["inventory"] = {"Coins": 1_000}
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            }
        }
        dialog = self._open(
            player,
            get_ge_projection=lambda: ge_frontend_projection_pure(
                player,
                item_catalog=catalog,
            ),
            on_ge_action=lambda _action_id, _payload: {"ok": False},
        )
        _open_ge_tab(dialog)

        side = dialog.findChild(QComboBox, "geOfferSideCombo")
        side.setCurrentIndex(side.findData("sell"))
        QApplication.processEvents()

        item_list = dialog.findChild(QListWidget, "geItemList")
        self.assertEqual(item_list.count(), 1)
        self.assertEqual(
            item_list.item(0).text(),
            "You own nothing exchangeable to sell.",
        )
        dialog.deleteLater()

    def test_grand_exchange_sell_all_and_bank_quantities_and_compounding_nudges(
        self,
    ) -> None:
        from ankiscape.logic.grand_exchange_logic import ge_frontend_projection_pure

        player = _make_player_data()
        player["inventory"] = {"Coins": 10_000, "Logs": 137}
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            },
            "Coal": {
                "guide_price": 200,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "ore",
            },
        }
        dialog = self._open(
            player,
            get_ge_projection=lambda: ge_frontend_projection_pure(
                player,
                item_catalog=catalog,
            ),
            on_ge_action=lambda _action_id, _payload: {"ok": True},
        )
        _open_ge_tab(dialog)

        item_list = dialog.findChild(QListWidget, "geItemList")
        texts = _list_texts(item_list)
        # The Bank tab's bare x{n} token, and nothing at all for unowned rows.
        self.assertTrue(any(text.endswith("·  x137") for text in texts))
        self.assertFalse(any("x0" in text for text in texts))

        sell_all = dialog.findChild(QPushButton, "geSellAllButton")
        quantity = dialog.findChild(QSpinBox, "geOfferQuantitySpin")
        price = dialog.findChild(QSpinBox, "geOfferPriceSpin")
        # isHidden rather than isVisible: the test dialog is never shown.
        self.assertTrue(sell_all.isHidden())

        side = dialog.findChild(QComboBox, "geOfferSideCombo")
        side.setCurrentIndex(side.findData("sell"))
        QApplication.processEvents()
        self.assertFalse(sell_all.isHidden())

        logs_row = next(
            index
            for index in range(item_list.count())
            if item_list.item(index).data(Qt.ItemDataRole.UserRole)["item_name"]
            == "Logs"
        )
        item_list.setCurrentRow(logs_row)
        QApplication.processEvents()
        self.assertEqual(quantity.value(), 1)
        sell_all.click()
        self.assertEqual(quantity.value(), 137)
        self.assertIn(
            "Bank: 137",
            dialog.findChild(QLabel, "geSelectedItemMeta").text(),
        )

        # Regression: the nudges used to recompute from the guide price, so a
        # second click never moved the price.
        plus = dialog.findChild(QPushButton, "gePricePlus5Button")
        self.assertEqual(price.value(), 100)
        plus.click()
        self.assertEqual(price.value(), 105)
        plus.click()
        self.assertEqual(price.value(), 110)
        dialog.findChild(QPushButton, "geGuidePriceButton").click()
        self.assertEqual(price.value(), 100)

        # At a few gp the percentage truncates to no movement, so the period
        # script's forced one-coin step is what keeps the button live.
        price.setValue(1)
        plus.click()
        self.assertEqual(price.value(), 2)
        minus = dialog.findChild(QPushButton, "gePriceMinus5Button")
        minus.click()
        self.assertEqual(price.value(), 1)
        minus.click()
        self.assertEqual(price.value(), 1)

        # Truncation toward zero, not round-to-nearest. These two prices are
        # where the distinction shows: round-half-up gives 35 and 20. The
        # arithmetic is client script 4112, recovered by disassembly — see
        # memory-bank/source-audits/ge-offer-price-controls-2026-07-24.md.
        price.setValue(33)
        plus.click()
        self.assertEqual(price.value(), 34)
        price.setValue(21)
        minus.click()
        self.assertEqual(price.value(), 19)

        # The up-button saturates past the period overflow boundary rather than
        # wrapping. The spin box ceiling is the same 32-bit maximum.
        price.setValue(2_045_222_521)
        plus.click()
        self.assertEqual(price.value(), 2_147_483_647)
        dialog.deleteLater()

    def test_grand_exchange_fill_log_colours_partial_and_completed_rows(self) -> None:
        from aqt.qt import QColor
        from ankiscape.logic.grand_exchange_logic import ge_frontend_projection_pure

        player = _make_player_data()
        player["inventory"] = {"Coins": 10_000}
        player["shop_market_clock"] = {"answered_cards": 12, "market_tick": 12}
        player["ge_fill_log"] = [
            {
                "card": 10,
                "side": "sell",
                "item_name": "Logs",
                "completed_quantity": 3,
                "original_quantity": 10,
            },
            {
                "card": 12,
                "side": "buy",
                "item_name": "Coal",
                "completed_quantity": 5,
                "original_quantity": 5,
            },
        ]
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            }
        }
        dialog = self._open(
            player,
            get_ge_projection=lambda: ge_frontend_projection_pure(
                player,
                item_catalog=catalog,
            ),
            on_ge_action=lambda _action_id, _payload: {"ok": True},
        )
        _open_ge_tab(dialog)

        toggle = dialog.findChild(QToolButton, "geFillLogToggle")
        log_list = dialog.findChild(QListWidget, "geFillLogList")
        self.assertEqual(toggle.text(), "Recent fills (2)")
        self.assertTrue(log_list.isHidden())
        toggle.click()
        QApplication.processEvents()
        self.assertFalse(log_list.isHidden())

        # Newest first, and "cards ago" rather than wall time.
        self.assertEqual(
            _list_texts(log_list),
            ["Now: Coal - 5/5 bought", "2 cards ago: Logs - 3/10 sold"],
        )
        completed = log_list.item(0).foreground().color()
        partial = log_list.item(1).foreground().color()
        self.assertIn(completed, (QColor("#3f6e1e"), QColor("#85c54b")))
        self.assertIn(partial, (QColor("#8a6100"), QColor("#e0b341")))
        self.assertNotEqual(completed, partial)
        dialog.deleteLater()

    def test_grand_exchange_ironman_toggle_locks_only_offer_creation(self) -> None:
        from ankiscape.logic.grand_exchange_logic import (
            apply_ge_frontend_action_pure,
            ge_frontend_projection_pure,
        )

        player = _make_player_data()
        player["inventory"] = {"Coins": 1_000}
        catalog = {
            "Logs": {
                "guide_price": 100,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            }
        }
        calls = []

        def projection():
            return ge_frontend_projection_pure(player, item_catalog=catalog)

        def action(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated, info = apply_ge_frontend_action_pure(
                player,
                action_id,
                payload,
                item_catalog=catalog,
            )
            if info.get("ok"):
                player.clear()
                player.update(updated)
            return {**info, "projection": projection()}

        dialog = self._open(
            player,
            get_ge_projection=projection,
            on_ge_action=action,
        )
        _open_ge_tab(dialog)

        toggle = dialog.findChild(QCheckBox, "geIronmanToggle")
        toggle.setChecked(True)
        QApplication.processEvents()

        self.assertEqual(calls[-1], ("set_ironman", {"enabled": True}))
        self.assertTrue(player["ironman_mode"])
        self.assertFalse(dialog.findChild(QListWidget, "geItemList").isEnabled())
        self.assertFalse(dialog.findChild(QWidget, "geOfferEditor").isEnabled())
        self.assertTrue(toggle.isEnabled())
        self.assertIn(
            "Ironman mode",
            dialog.findChild(QLabel, "geStatusLabel").text(),
        )
        dialog.deleteLater()

    def test_shop_opens_browse_first_and_detail_is_collapsible(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures
        from ankiscape.logic.shop_logic import shop_view_model_pure

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
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

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
        search.setText("Red blossom seed")
        QApplication.processEvents()
        selector = _find_named_list(dialog, "shopSelectionList")
        seed_item = next(
            selector.item(i)
            for i in range(selector.count())
            if "Red blossom seed" in selector.item(i).text()
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
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

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
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

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
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        live_view = fixtures["normal_coin_stock_shop"]
        live_row = next(row for row in live_view["rows"] if row["can_buy"])
        saved = []
        achievement_checks = []
        dialog = self._open(
            pd,
            on_check_achievements=lambda data: achievement_checks.append(copy.deepcopy(data["inventory"])),
            on_save_player_data=lambda: saved.append(copy.deepcopy(pd)),
        )
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
        self.assertEqual(len(saved), 1)
        self.assertEqual(achievement_checks, [pd["inventory"]])
        self.assertEqual(saved[0]["inventory"], pd["inventory"])
        self.assertEqual(saved[0]["shop_events"], pd["shop_events"])

    def test_shop_general_store_sell_creates_temporary_stock(self) -> None:
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures

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
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures
        from ankiscape.data.shop_data import SHOP_VENDOR_ACTIONS

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
        from ankiscape.logic.shop_fixtures import build_shop_frontend_fixtures
        from ankiscape.data.shop_data import SHOP_SERVICES, SHOP_VENDOR_ACTIONS

        fixtures = build_shop_frontend_fixtures()
        pd = fixtures["fixture_player_data"]
        pd["inventory"].update({"Agility potion (1)": 4, "Agility potion (3)": 4})
        pd["inventory"].update(
            {
                "Potion flask": 1,
                "Attack potion (3)": 2,
                "Attack flask (2)": 1,
            }
        )
        pd["quests"] = {
            "as_a_first_resort": {"completed": True}
        }
        pd["summoning_level"] = 99
        pd["fletching_exp"] = 1234.5
        pd["inventory"]["Pack yak pouch"] = 3
        pd["inventory"]["Long kebbit spike"] = 2
        vendor_action_id = fixtures["vendor_action_transaction"]["action_id"]
        dialog = self._open(pd)
        _open_shop_tab(dialog)

        selector = _find_named_list(dialog, "shopSelectionList")
        service_list = _find_named_list(dialog, "shopServiceList")

        def _select_service_row(row_id: str) -> QListWidgetItem:
            source = SHOP_SERVICES if row_id in SHOP_SERVICES else SHOP_VENDOR_ACTIONS
            provider = str(source[row_id]["provider"])
            provider_item = next(
                selector.item(index)
                for index in range(selector.count())
                if (
                    isinstance(selector.item(index).data(Qt.ItemDataRole.UserRole), dict)
                    and selector.item(index).data(Qt.ItemDataRole.UserRole).get("kind") == "provider"
                    and selector.item(index).data(Qt.ItemDataRole.UserRole).get("provider") == provider
                )
            )
            selector.setCurrentItem(provider_item)
            QApplication.processEvents()
            for index in range(service_list.count()):
                item = service_list.item(index)
                payload = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(payload, dict) and payload.get("id") == row_id:
                    service_list.setCurrentItem(item)
                    QApplication.processEvents()
                    return item
            raise AssertionError(f"service/vendor row {row_id!r} not found")

        bob_item = _select_service_row("bob_barter_decant_four")
        self.assertFalse(bob_item.icon().isNull())
        dose_spin = dialog.findChild(QSpinBox, "shopServiceQuantitySpin")
        self.assertIsNotNone(dose_spin)
        self.assertTrue(dose_spin.isVisibleTo(dialog))
        self.assertEqual((dose_spin.minimum(), dose_spin.maximum()), (2, 4))
        dose_spin.setValue(3)
        QApplication.processEvents()
        preview_label = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("16 doses", preview_label.text())
        self.assertIn("3-dose vials", preview_label.text())
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview_label.text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Agility potion (1)"], 1)
        self.assertEqual(pd["inventory"]["Agility potion (3)"], 5)
        self.assertEqual(pd["inventory"].get("Agility potion (4)", 0), 0)
        self.assertEqual(pd["inventory"]["Vial"], 2)

        teplin_fill = _select_service_row("teplin_fill_potion_flasks")
        self.assertFalse(teplin_fill.icon().isNull())
        self.assertIn("Free", teplin_fill.text())
        self.assertNotIn("+ 0 Coins", teplin_fill.text())
        self.assertEqual(service_list.maximumHeight(), 96)
        self.assertFalse(dose_spin.isVisibleTo(dialog))
        preview_label = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("6 doses", preview_label.text())
        self.assertIn("1 empty Potion flask", preview_label.text())
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview_label.text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Potion flask"], 0)
        self.assertEqual(pd["inventory"]["Attack potion (3)"], 0)
        self.assertEqual(pd["inventory"]["Attack flask (2)"], 1)
        self.assertEqual(pd["inventory"]["Attack flask (6)"], 1)
        self.assertEqual(pd["inventory"]["Vial"], 4)

        teplin_decant = _select_service_row(
            "teplin_decant_flasks_to_vials"
        )
        self.assertFalse(teplin_decant.icon().isNull())
        self.assertFalse(dose_spin.isVisibleTo(dialog))
        preview_label = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("2 doses", preview_label.text())
        self.assertIn("1 vial for free", preview_label.text())
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview_label.text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Attack flask (2)"], 0)
        self.assertEqual(pd["inventory"]["Attack flask (6)"], 1)
        self.assertEqual(pd["inventory"]["Attack potion (2)"], 1)

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

        _select_service_row("bogrog_exchange_packyak")
        dose_spin = dialog.findChild(QSpinBox, "shopServiceQuantitySpin")
        self.assertTrue(dose_spin.isVisibleTo(dialog))
        dose_spin.setValue(2)
        QApplication.processEvents()
        before_shards = pd["inventory"].get("Spirit shards", 0)
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(
            use_button.isEnabled(),
            _find_named_label(dialog, "shopServicePreviewLabel").text(),
        )
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Pack yak pouch"], 1)
        self.assertEqual(
            pd["inventory"]["Spirit shards"],
            before_shards + (2 * 148),
        )

        leon_item = _select_service_row("leon_fletch_long_kebbit_bolts")
        self.assertFalse(leon_item.icon().isNull())
        self.assertNotIn("Service:", leon_item.text())
        self.assertNotIn("· Leon", leon_item.text())
        self.assertIn(
            "1 × Long kebbit spike + 40 Coins → 6 × Long kebbit bolts",
            leon_item.text(),
        )
        quantity_spin = dialog.findChild(QSpinBox, "shopServiceQuantitySpin")
        self.assertTrue(quantity_spin.isVisibleTo(dialog))
        quantity_spin.setValue(2)
        QApplication.processEvents()
        preview_label = _find_named_label(dialog, "shopServicePreviewLabel")
        self.assertIn("80 Coins", preview_label.text())
        self.assertIn(
            "Long kebbit spike: 2 owned, 2 needed",
            preview_label.text(),
        )
        before_coins = pd["inventory"]["Coins"]
        before_fletching_exp = pd["fletching_exp"]
        use_button = _find_named_button(dialog, "shopServiceUseButton")
        self.assertTrue(use_button.isEnabled(), preview_label.text())
        use_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Coins"], before_coins - 80)
        self.assertEqual(pd["inventory"]["Long kebbit spike"], 0)
        self.assertEqual(pd["inventory"]["Long kebbit bolts"], 12)
        self.assertEqual(pd["fletching_exp"], before_fletching_exp)

        global_button = _find_named_button(dialog, "shopGlobalHistoryButton")
        global_button.click()
        QApplication.processEvents()
        global_history = _find_named_list(dialog, "shopGlobalHistoryList")
        history_texts = _list_texts(global_history)
        self.assertTrue(any("Completed" in text for text in history_texts), history_texts)

        search = dialog.findChild(QLineEdit, "shopSearchInput")
        search.setText("Teplin")
        QApplication.processEvents()
        search_rows = _list_texts(
            _find_named_list(dialog, "shopSelectionList")
        )
        self.assertEqual(len(search_rows), 2)
        self.assertTrue(all("Free" in text for text in search_rows))
        self.assertTrue(all("0 Coins" not in text for text in search_rows))

    def test_achievement_tab_renders_the_cabinet_not_the_fabricated_list(self) -> None:
        """The tab is the Achievement Cabinet now.

        It used to render 168 fabricated skill-progression rows in four invented
        difficulty buckets, under a completion percentage whose denominator moved
        whenever an achievement was added — the figure the semantics contract
        forbids diary gear from consuming. This asserts the replacement: real
        regional families, real tier rewards, and no percentage anywhere.
        """
        pd = _make_player_data()
        pd["completed_achievements"] = ["First Steps", "Rune Mysteries"]
        dialog = self._open(pd)
        _open_achievements_tab(dialog)
        labels = [label.text() for label in dialog.findChildren(QLabel)]

        self.assertIn("Achievement Cabinet", labels)
        self.assertTrue(
            any(text.startswith("Varrock") for text in labels),
            "the Cabinet did not render its regional families",
        )
        self.assertTrue(
            any("Varrock armour 1" in text for text in labels),
            "the Easy Varrock tier did not name the item it hands over",
        )
        self.assertTrue(
            any(re.fullmatch(r"\d+/\d+ tasks", text) for text in labels),
            "the Cabinet did not show its fixed-denominator task total",
        )
        self.assertFalse(
            [text for text in labels if "%" in text and "Completed:" in text],
            "a moving-denominator completion percentage is back on the tab",
        )
        self.assertNotIn(
            "First Steps",
            labels,
            "a fabricated achievement row is still rendered",
        )

    def test_expensive_tabs_are_unbuilt_until_shown(self) -> None:
        """Regression guard for the deferred build: opening the menu must not
        construct the Shop, Quests or Achievements pages, while the tab that is
        actually visible (Skills) is fully rendered."""
        dialog = self._open(_make_player_data())
        tabs = _find_main_tabs(dialog)
        for label in ("Shop", "Quests", "Achievements"):
            index = next(i for i in range(tabs.count()) if tabs.tabText(i) == label)
            page = tabs.widget(index)
            self.assertEqual(
                len(page.findChildren(QLabel)),
                0,
                f"{label} tab was built before it was shown",
            )
        self.assertTrue(_panel_title(dialog).startswith("Mining"))

    def test_refresh_of_unbuilt_tab_is_a_noop_and_later_build_shows_live_state(self) -> None:
        """A cross-tab refresh aimed at a tab nobody opened must not raise, and
        the state written in the meantime must appear once the tab is built."""
        pd = _make_player_data()
        pd["quest_points"] = 0
        dialog = self._open(pd)
        ctx = dialog._ankiscape_menu_ctx

        pd["quest_points"] = 7
        ctx.refresh("quests")
        ctx.refresh("shop")
        ctx.refresh("no_such_surface")

        _open_quests_tab(dialog)
        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn("Quest points: 7", labels)
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))

        _open_shop_tab(dialog)
        self.assertTrue(_list_texts(_find_named_list(dialog, "shopSelectionList")))

        # Both surfaces register their refresher once built, so a later refresh
        # reaches them instead of being dropped.
        self.assertIn("quests", ctx.refreshers)
        self.assertIn("shop", ctx.refreshers)
        ctx.refresh("quests")
        ctx.refresh("shop")
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_cooks_assistant"))

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
        pd["inventory"]["Waterskin (4)"] = 1
        pd["current_combat_target"] = "seagull"
        pd["slayer_level"] = 65
        pd["equipment"]["head"] = "Face mask"
        pd["equipment"]["shield"] = "Lit bug lantern"
        pd["equipment"]["feet"] = "Insulated boots"
        pd["quests"]["ernest_the_chicken"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["royal_trouble"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["olafs_quest"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["inventory"]["Spade"] = 1
        pd["quests"]["death_to_the_dorgeshuun"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["inventory"]["Slayer bell"] = 1
        pd["inventory"]["Lit torch"] = 1
        pd["equipment"]["weapon"] = "Leaf-bladed spear"
        pd["quests"]["priest_in_peril"] = {
            "started": True,
            "progress": 9,
            "completed": True,
        }
        pd["quests"]["lost_city"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["cabin_fever"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["legends_quest"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["regicide"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
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
        ogre = _tree_row(tree, "ogre")
        jackal = _tree_row(tree, "jackal")
        goat = _tree_row(tree, "goat")
        icefiend = _tree_row(tree, "icefiend")
        pyrefiend = _tree_row(tree, "pyrefiend")
        jelly = _tree_row(tree, "jelly")
        bloodveld = _tree_row(tree, "bloodveld")
        infernal_mage = _tree_row(tree, "infernal_mage")
        dust_devil = _tree_row(tree, "dust_devil")
        green_dragon = _tree_row(tree, "green_dragon")
        harpie_bug_swarm = _tree_row(tree, "harpie_bug_swarm")
        killerwatt = _tree_row(tree, "killerwatt")
        sea_snake_hatchling = _tree_row(tree, "sea_snake_hatchling")
        sea_snake_young = _tree_row(tree, "sea_snake_young")
        brine_rat = _tree_row(tree, "brine_rat")
        molanisk = _tree_row(tree, "molanisk")
        turoth = _tree_row(tree, "turoth")
        fire_giant = _tree_row(tree, "fire_giant")
        blue_dragon = _tree_row(tree, "blue_dragon")
        baby_blue_dragon = _tree_row(tree, "baby_blue_dragon")
        bronze_dragon = _tree_row(tree, "bronze_dragon")
        iron_dragon = _tree_row(tree, "iron_dragon")
        steel_dragon = _tree_row(tree, "steel_dragon")
        red_dragon = _tree_row(tree, "red_dragon")
        black_dragon = _tree_row(tree, "black_dragon")
        baby_red_dragon = _tree_row(tree, "baby_red_dragon")
        cave_horror = _tree_row(tree, "cave_horror")
        dagannoth = _tree_row(tree, "dagannoth")
        dagannoth_melee = _tree_row(tree, "dagannoth_level_92")
        elf_warrior = _tree_row(tree, "elf_warrior")
        elf_warrior_melee = _tree_row(tree, "elf_warrior_level_108")
        aberrant_spectre = _tree_row(tree, "aberrant_spectre")
        basilisk = _tree_row(tree, "basilisk")
        crocodile = _tree_row(tree, "crocodile")
        otherworldly_being = _tree_row(tree, "otherworldly_being")
        jungle_horror = _tree_row(tree, "jungle_horror")
        shadow_warrior = _tree_row(tree, "shadow_warrior")
        kalphite_soldier = _tree_row(tree, "kalphite_soldier")
        wall_beast = _tree_row(tree, "wall_beast")
        vampyre = _tree_row(tree, "vampyre")
        banshee = _tree_row(tree, "banshee")
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
        self.assertEqual(goat.text(0), "Goat (Lvl 23)")
        self.assertIn("Enemy max hit: 47 LP", goat.toolTip(0))
        self.assertIn("Desert goat horn x1", goat.toolTip(0))
        self.assertIn(
            "Desert heat: 1 Waterskin dose per Combat review",
            goat.toolTip(0),
        )
        self.assertFalse(goat.icon(0).isNull())
        self.assertIn("Iron bolts x2-12 (1/20)", highwayman.toolTip(0))
        self.assertEqual(barbarian_level_10.text(0), "Barbarian (Lvl 10)")
        self.assertIn("Enemy LP: 180/180", barbarian_level_10.toolTip(0))
        self.assertIn("Law rune x2 (8/1024)", barbarian_level_10.toolTip(0))
        self.assertIn("barbarian_2hsword_lvl_10.plugin.kts", barbarian_level_10.toolTip(0))
        self.assertEqual(ogre.text(0), "Ogre (Lvl 53)")
        self.assertIn("Ogre common seed table (19/128)", ogre.toolTip(0))
        self.assertIn("Big bones x1", ogre.toolTip(0))
        self.assertFalse(ogre.icon(0).isNull())
        self.assertEqual(jackal.text(0), "Jackal (Lvl 21)")
        self.assertIn("Enemy LP: 270/270", jackal.toolTip(0))
        self.assertIn("Enemy max hit: 80 LP", jackal.toolTip(0))
        self.assertFalse(jackal.icon(0).isNull())
        self.assertEqual(icefiend.text(0), "Icefiend (Lvl 13)")
        self.assertIn("Impious ashes x1", icefiend.toolTip(0))
        self.assertIn("Enemy max hit: 20 LP", icefiend.toolTip(0))
        self.assertFalse(icefiend.icon(0).isNull())
        self.assertEqual(pyrefiend.text(0), "Pyrefiend (Lvl 43)")
        self.assertIn("Enemy attack: Magic-based melee", pyrefiend.toolTip(0))
        self.assertIn("Enemy max hit: 44 LP", pyrefiend.toolTip(0))
        self.assertIn("Steel boots x1 (1/128)", pyrefiend.toolTip(0))
        self.assertFalse(pyrefiend.icon(0).isNull())
        self.assertEqual(jelly.text(0), "Jelly (Lvl 78)")
        self.assertIn("Enemy attack: Magic-based melee", jelly.toolTip(0))
        self.assertIn("Enemy max hit: 60 LP", jelly.toolTip(0))
        self.assertIn("Mithril boots x1 (1/128)", jelly.toolTip(0))
        self.assertFalse(jelly.icon(0).isNull())
        self.assertEqual(bloodveld.text(0), "Bloodveld (Lvl 76)")
        self.assertIn("Enemy attack: Magic-based melee", bloodveld.toolTip(0))
        self.assertIn("Enemy max hit: 59 LP", bloodveld.toolTip(0))
        self.assertIn("Black boots x1 (1/128)", bloodveld.toolTip(0))
        self.assertFalse(bloodveld.icon(0).isNull())
        self.assertEqual(infernal_mage.text(0), "Infernal Mage (Lvl 66)")
        self.assertIn("Enemy attack: Magic", infernal_mage.toolTip(0))
        self.assertIn("Enemy max hit: 89 LP", infernal_mage.toolTip(0))
        self.assertIn(
            "Mystic boots (dark) x1 (125/64000)", infernal_mage.toolTip(0)
        )
        self.assertIn(
            "Lava battlestaff x1 (64/64000)", infernal_mage.toolTip(0)
        )
        self.assertFalse(infernal_mage.icon(0).isNull())
        self.assertEqual(dust_devil.text(0), "Dust devil (Lvl 93)")
        self.assertIn("Enemy max hit: 90 LP", dust_devil.toolTip(0))
        self.assertIn("Dragon chainbody x1 (1/32768)", dust_devil.toolTip(0))
        self.assertIn("Crimson charm x1 (115/606)", dust_devil.toolTip(0))
        self.assertFalse(dust_devil.icon(0).isNull())
        self.assertEqual(green_dragon.text(0), "Green dragon (Lvl 79)")
        self.assertIn("Dragonfire: None protection", green_dragon.toolTip(0))
        self.assertIn("Dragon bones x1", green_dragon.toolTip(0))
        self.assertFalse(green_dragon.icon(0).isNull())
        self.assertEqual(
            harpie_bug_swarm.text(0), "Harpie Bug Swarm (Lvl 46)"
        )
        self.assertIn(
            "Gold ore x1 (10514/100000)", harpie_bug_swarm.toolTip(0)
        )
        self.assertIn(
            "Green charm x1 (11/202)", harpie_bug_swarm.toolTip(0)
        )
        self.assertFalse(harpie_bug_swarm.icon(0).isNull())
        self.assertEqual(killerwatt.text(0), "Killerwatt (Lvl 71)")
        self.assertIn("Impious ashes x1", killerwatt.toolTip(0))
        self.assertIn("Gold charm x1 (41/303)", killerwatt.toolTip(0))
        self.assertFalse(killerwatt.icon(0).isNull())
        self.assertEqual(
            sea_snake_hatchling.text(0), "Sea Snake Hatchling (Lvl 62)"
        )
        self.assertIn("Casket x1 (11700/13000)", sea_snake_hatchling.toolTip(0))
        self.assertFalse(sea_snake_hatchling.icon(0).isNull())
        self.assertEqual(sea_snake_young.text(0), "Sea Snake Young (Lvl 90)")
        self.assertIn("Coins x44 (60/128)", sea_snake_young.toolTip(0))
        self.assertFalse(sea_snake_young.icon(0).isNull())
        self.assertEqual(brine_rat.text(0), "Brine rat (Lvl 70)")
        self.assertIn("Brine sabre x1 (1/512)", brine_rat.toolTip(0))
        self.assertIn("Gold charm x1 (133/606)", brine_rat.toolTip(0))
        self.assertFalse(brine_rat.icon(0).isNull())
        self.assertEqual(molanisk.text(0), "Molanisk (Lvl 51)")
        self.assertIn("Mole claw x1 (207/100000)", molanisk.toolTip(0))
        self.assertIn("Clue scroll (easy) x1 (1/128)", molanisk.toolTip(0))
        self.assertFalse(molanisk.icon(0).isNull())
        self.assertEqual(turoth.text(0), "Turoth (Lvl 83)")
        self.assertIn(
            "Leaf-bladed sword x1 (169/100000)",
            turoth.toolTip(0),
        )
        self.assertIn("Green charm x1 (214/1212)", turoth.toolTip(0))
        self.assertFalse(turoth.icon(0).isNull())
        self.assertEqual(fire_giant.text(0), "Fire giant (Lvl 86)")
        self.assertIn("Enemy max hit: 116 LP", fire_giant.toolTip(0))
        self.assertIn("Big bones x1", fire_giant.toolTip(0))
        self.assertIn("Gold charm x1 (207/404)", fire_giant.toolTip(0))
        self.assertFalse(fire_giant.icon(0).isNull())
        self.assertEqual(blue_dragon.text(0), "Blue dragon (Lvl 111)")
        self.assertIn("Enemy max hit: 500 LP", blue_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", blue_dragon.toolTip(0))
        self.assertIn("Blue dragon egg x1 (1/2000)", blue_dragon.toolTip(0))
        self.assertIn("Gold charm x1 (15/404)", blue_dragon.toolTip(0))
        self.assertFalse(blue_dragon.icon(0).isNull())
        self.assertEqual(baby_blue_dragon.text(0), "Baby blue dragon (Lvl 48)")
        self.assertIn("Baby dragon bones x1", baby_blue_dragon.toolTip(0))
        self.assertNotIn("Dragonfire:", baby_blue_dragon.toolTip(0))
        self.assertFalse(baby_blue_dragon.icon(0).isNull())
        self.assertEqual(bronze_dragon.text(0), "Bronze dragon (Lvl 131)")
        self.assertIn("Enemy max hit: 500 LP", bronze_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", bronze_dragon.toolTip(0))
        self.assertIn("Bronze bar x5", bronze_dragon.toolTip(0))
        self.assertIn("Dragon plateskirt x1 (1/2048)", bronze_dragon.toolTip(0))
        self.assertIn("Clue scroll (elite) x1 (1/500)", bronze_dragon.toolTip(0))
        self.assertFalse(bronze_dragon.icon(0).isNull())
        self.assertEqual(iron_dragon.text(0), "Iron dragon (Lvl 189)")
        self.assertIn("Enemy max hit: 500 LP", iron_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", iron_dragon.toolTip(0))
        self.assertIn("Iron bar x5", iron_dragon.toolTip(0))
        self.assertIn("Dragon plateskirt x1 (1/1024)", iron_dragon.toolTip(0))
        self.assertIn("Draconic visage x1 (1/10000)", iron_dragon.toolTip(0))
        self.assertIn("Green charm x2 (282/1212)", iron_dragon.toolTip(0))
        self.assertFalse(iron_dragon.icon(0).isNull())
        self.assertEqual(steel_dragon.text(0), "Steel dragon (Lvl 246)")
        self.assertIn("Enemy max hit: 500 LP", steel_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", steel_dragon.toolTip(0))
        self.assertIn("Steel bar x5", steel_dragon.toolTip(0))
        self.assertIn("Coins x650 (5/128)", steel_dragon.toolTip(0))
        self.assertIn("Dragon plateskirt x1 (1/512)", steel_dragon.toolTip(0))
        self.assertIn("Green charm x3 (308/1212)", steel_dragon.toolTip(0))
        self.assertFalse(steel_dragon.icon(0).isNull())
        self.assertEqual(red_dragon.text(0), "Red dragon (Lvl 152)")
        self.assertIn("Enemy max hit: 500 LP", red_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", red_dragon.toolTip(0))
        self.assertIn("Red dragonhide x1", red_dragon.toolTip(0))
        self.assertIn("Red dragon egg x1 (1/2000)", red_dragon.toolTip(0))
        self.assertIn("Green charm x1 (385/1212)", red_dragon.toolTip(0))
        self.assertFalse(red_dragon.icon(0).isNull())
        self.assertEqual(black_dragon.text(0), "Black dragon (Lvl 227)")
        self.assertIn("Enemy max hit: 500 LP", black_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", black_dragon.toolTip(0))
        self.assertIn("Black dragonhide x1", black_dragon.toolTip(0))
        self.assertIn("Black dragon egg x1 (1/2000)", black_dragon.toolTip(0))
        self.assertIn("Draconic visage x1 (1/10000)", black_dragon.toolTip(0))
        self.assertIn("Gold charm x3 (42/1212)", black_dragon.toolTip(0))
        self.assertFalse(black_dragon.icon(0).isNull())
        self.assertEqual(baby_red_dragon.text(0), "Baby red dragon (Lvl 48)")
        self.assertIn("Enemy max hit: 54 LP", baby_red_dragon.toolTip(0))
        self.assertIn("Baby dragon bones x1", baby_red_dragon.toolTip(0))
        self.assertNotIn("Dragonfire:", baby_red_dragon.toolTip(0))
        self.assertFalse(baby_red_dragon.icon(0).isNull())
        self.assertEqual(cave_horror.text(0), "Cave horror (Lvl 80)")
        self.assertIn("Enemy attack: Magic-based melee", cave_horror.toolTip(0))
        self.assertIn("Enemy max hit: 87 LP", cave_horror.toolTip(0))
        self.assertIn("Missing a Witchwood icon", cave_horror.toolTip(0))
        self.assertIn("Black mask (10) x1 (1/512)", cave_horror.toolTip(0))
        self.assertIn("Crimson charm x1 (136/1212)", cave_horror.toolTip(0))
        self.assertFalse(cave_horror.icon(0).isNull())
        self.assertEqual(dagannoth.text(0), "Dagannoth (ranged) (Lvl 74)")
        self.assertIn("Enemy attack: Ranged", dagannoth.toolTip(0))
        self.assertIn("Pearl bolt tips x12 (25/1100)", dagannoth.toolTip(0))
        self.assertIn("Crimson charm x1 (212/1212)", dagannoth.toolTip(0))
        self.assertFalse(dagannoth.icon(0).isNull())
        self.assertEqual(
            dagannoth_melee.text(0), "Dagannoth (melee) (Lvl 92)"
        )
        self.assertIn("Enemy attack: Melee", dagannoth_melee.toolTip(0))
        self.assertIn("Clue scroll (medium) x1 (1/128)", dagannoth_melee.toolTip(0))
        self.assertFalse(dagannoth_melee.icon(0).isNull())
        self.assertEqual(
            elf_warrior.text(0), "Elf warrior (ranged) (Lvl 90)"
        )
        self.assertIn(
            "Crystal teleport seed x1 (25/128)", elf_warrior.toolTip(0)
        )
        self.assertIn("Green charm x1 (227/1212)", elf_warrior.toolTip(0))
        self.assertFalse(elf_warrior.icon(0).isNull())
        self.assertEqual(
            elf_warrior_melee.text(0), "Elf warrior (melee) (Lvl 108)"
        )
        self.assertIn("Enemy attack: Melee", elf_warrior_melee.toolTip(0))
        self.assertIn(
            "Clue scroll (hard) x1 (1/128)", elf_warrior_melee.toolTip(0)
        )
        self.assertFalse(elf_warrior_melee.icon(0).isNull())
        self.assertEqual(
            aberrant_spectre.text(0), "Aberrant spectre (Lvl 96)"
        )
        self.assertIn("Enemy max hit: 10 LP", aberrant_spectre.toolTip(0))
        self.assertIn("Missing Nose peg", aberrant_spectre.toolTip(0))
        self.assertIn(
            "Mystic robe bottom (dark) x1 (1/512)",
            aberrant_spectre.toolTip(0),
        )
        self.assertIn("Gold charm x1 (97/1212)", aberrant_spectre.toolTip(0))
        self.assertFalse(aberrant_spectre.icon(0).isNull())
        self.assertEqual(basilisk.text(0), "Basilisk (Lvl 61)")
        self.assertIn("Enemy max hit: 10 LP", basilisk.toolTip(0))
        self.assertIn("Missing Mirror shield", basilisk.toolTip(0))
        self.assertIn(
            "Mystic hat (light) x1 (125/64000)", basilisk.toolTip(0)
        )
        self.assertIn("Basilisk head x1 (32/64000)", basilisk.toolTip(0))
        self.assertFalse(basilisk.icon(0).isNull())
        self.assertEqual(crocodile.text(0), "Crocodile (Lvl 63)")
        self.assertIn("Enemy max hit: 67 LP", crocodile.toolTip(0))
        self.assertIn("Bones x1", crocodile.toolTip(0))
        self.assertIn(
            "Desert heat: 1 Waterskin dose per Combat review",
            crocodile.toolTip(0),
        )
        self.assertFalse(crocodile.icon(0).isNull())
        self.assertEqual(
            otherworldly_being.text(0), "Otherworldly being (Lvl 64)"
        )
        self.assertIn("Enemy max hit: 70 LP", otherworldly_being.toolTip(0))
        self.assertIn("Minor herb table (10/128)", otherworldly_being.toolTip(0))
        self.assertIn("Rune mace x1 (1/128)", otherworldly_being.toolTip(0))
        self.assertFalse(otherworldly_being.icon(0).isNull())
        self.assertEqual(jungle_horror.text(0), "Jungle horror (Lvl 70)")
        self.assertIn("Enemy max hit: 84 LP", jungle_horror.toolTip(0))
        self.assertIn(
            "Iron warhammer x1 (8395/100000)", jungle_horror.toolTip(0)
        )
        self.assertFalse(jungle_horror.icon(0).isNull())
        self.assertEqual(shadow_warrior.text(0), "Shadow warrior (Lvl 48)")
        self.assertIn("Enemy max hit: 65 LP", shadow_warrior.toolTip(0))
        self.assertIn("Adamant spear x1 (1/128)", shadow_warrior.toolTip(0))
        self.assertIn("Crimson charm x1 (44/606)", shadow_warrior.toolTip(0))
        self.assertFalse(shadow_warrior.icon(0).isNull())
        self.assertEqual(kalphite_soldier.text(0), "Kalphite Soldier (Lvl 85)")
        self.assertIn("Enemy max hit: 80 LP", kalphite_soldier.toolTip(0))
        self.assertIn(
            "Poison: 50 LP initial · 40% attack chance",
            kalphite_soldier.toolTip(0),
        )
        self.assertIn("Rune chainbody x1 (1/128)", kalphite_soldier.toolTip(0))
        self.assertFalse(kalphite_soldier.icon(0).isNull())
        self.assertEqual(wall_beast.text(0), "Wall beast (Lvl 49)")
        self.assertIn(
            "Equip a Spiny helmet to start fighting Wall beasts",
            wall_beast.toolTip(0),
        )
        self.assertFalse(wall_beast.icon(0).isNull())
        self.assertEqual(vampyre.text(0), "Vampyre (Lvl 61)")
        self.assertIn("Vampyre dust x1", vampyre.toolTip(0))
        self.assertIn(
            "Weakness: Holy symbol not equipped · enemy accuracy -20% · max hit -20%",
            vampyre.toolTip(0),
        )
        self.assertFalse(vampyre.icon(0).isNull())
        self.assertEqual(banshee.text(0), "Banshee (Lvl 23)")
        self.assertIn("Missing Earmuffs", banshee.toolTip(0))
        self.assertIn("Enemy max hit: 10 LP", banshee.toolTip(0))
        self.assertEqual(seagull.text(0), "Seagull (Lvl 2)")
        self.assertIn("seagull_level_2.plugin.kts", seagull.toolTip(0))
        self.assertEqual(tree.currentItem().data(0, Qt.ItemDataRole.UserRole), "seagull")

    def test_combat_search_filters_without_changing_or_activating_the_saved_target(self) -> None:
        from aqt.qt import QEvent, QKeyEvent

        pd = _make_player_data()
        pd["current_combat_target"] = "seagull"
        dialog = self._open(pd, current_skill="Combat")
        search = _find_named_line_edit(dialog, "combatTargetSearchInput")

        search.setText("cockatrice mirror")
        QApplication.processEvents()
        tree = dialog.findChild(QTreeWidget, "combatTargetTree")
        visible_roles = {
            item.data(0, Qt.ItemDataRole.UserRole)
            for item in _tree_items(tree)
        }
        self.assertEqual(
            visible_roles,
            {"__combat_group__:Slayer", "cockatrice"},
        )
        self.assertEqual(pd["current_combat_target"], "seagull")
        self.assertEqual(self._combat_calls, [])
        self.assertIsNone(tree.currentItem())
        self.assertTrue(tree.topLevelItem(0).isExpanded())

        search.setText("definitely-not-a-target")
        QApplication.processEvents()
        tree = dialog.findChild(QTreeWidget, "combatTargetTree")
        empty = tree.topLevelItem(0)
        self.assertEqual(empty.text(0), "No combat targets match this search.")
        self.assertFalse(empty.flags() & Qt.ItemFlag.ItemIsEnabled)
        tree.itemActivated.emit(empty, 0)
        QApplication.processEvents()
        self.assertEqual(self._combat_calls, [])

        escape = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(search, escape)
        QApplication.processEvents()
        self.assertEqual(search.text(), "")
        tree = dialog.findChild(QTreeWidget, "combatTargetTree")
        self.assertEqual(
            tree.currentItem().data(0, Qt.ItemDataRole.UserRole),
            "seagull",
        )
        self.assertEqual(pd["current_combat_target"], "seagull")
        dialog.deleteLater()

    def test_combat_finisher_action_only_enables_in_the_source_lp_window(self) -> None:
        ordinary = _make_player_data()
        ordinary["current_combat_target"] = "chicken"
        ordinary_dialog = self._open(ordinary, current_skill="Combat")
        ordinary_combo = ordinary_dialog.findChild(QComboBox, "combatActionCombo")
        self.assertIsNotNone(ordinary_combo)
        self.assertTrue(ordinary_combo.parentWidget().isHidden())

        blocked = _make_player_data()
        blocked.update(
            {
                "current_combat_target": "desert_lizard",
                "slayer_level": 99,
                "combat_encounter": {
                    "target_id": "desert_lizard",
                    "enemy_lifepoints": 31,
                },
                "combat_supply_loadout": {
                    "finishers": {"Ice cooler": 1},
                    "hazards": {"Waterskin (4)": 1},
                },
            }
        )
        blocked_dialog = self._open(blocked, current_skill="Combat")
        blocked_combo = blocked_dialog.findChild(QComboBox, "combatActionCombo")
        self.assertFalse(blocked_combo.parentWidget().isHidden())
        self.assertFalse(blocked_combo.model().item(1).isEnabled())

        ready = _make_player_data()
        ready.update(
            {
                "current_combat_target": "desert_lizard",
                "slayer_level": 99,
                "combat_encounter": {
                    "target_id": "desert_lizard",
                    "enemy_lifepoints": 30,
                },
                "combat_supply_loadout": {
                    "finishers": {"Ice cooler": 1},
                    "hazards": {"Waterskin (4)": 1},
                },
            }
        )
        ready_dialog = self._open(ready, current_skill="Combat")
        combo = ready_dialog.findChild(QComboBox, "combatActionCombo")

        self.assertFalse(combo.parentWidget().isHidden())
        self.assertEqual(
            [combo.itemData(index) for index in range(combo.count())],
            ["attack", "finisher"],
        )
        self.assertEqual(combo.itemText(1), "Use Ice cooler")
        self.assertTrue(combo.model().item(1).isEnabled())
        tree = _find_tree_with_user_role(ready_dialog, "desert_lizard")
        lizard = _tree_row(tree, "desert_lizard")
        self.assertFalse(lizard.icon(0).isNull())
        self.assertIn("Finisher: Use Ice cooler at 1–30 LP", lizard.toolTip(0))
        self.assertIn(
            "Desert heat: 1 Waterskin dose per Combat review",
            lizard.toolTip(0),
        )
        combo.setCurrentIndex(1)
        QApplication.processEvents()
        self.assertEqual(self._combat_action_calls[-1], "finisher")

        reusable = _make_player_data()
        reusable.update(
            {
                "current_combat_target": "gargoyle",
                "slayer_level": 99,
                "combat_encounter": {
                    "target_id": "gargoyle",
                    "enemy_lifepoints": 89,
                },
                "combat_supply_loadout": {
                    "finishers": {"Rock hammer": 1},
                },
            }
        )
        reusable_dialog = self._open(reusable, current_skill="Combat")
        reusable_combo = reusable_dialog.findChild(QComboBox, "combatActionCombo")
        self.assertEqual(reusable_combo.itemText(1), "Smash with Rock hammer")
        self.assertTrue(reusable_combo.model().item(1).isEnabled())
        self.assertIn(
            "reusable Rock hammer",
            reusable_combo.model().item(1).toolTip(),
        )
        gargoyle_tree = _find_tree_with_user_role(reusable_dialog, "gargoyle")
        self.assertFalse(_tree_row(gargoyle_tree, "gargoyle").icon(0).isNull())

        charged = _make_player_data()
        charged.update(
            {
                "current_combat_target": "mutated_zygomite_level_74",
                "slayer_level": 57,
                "quests": {"lost_city": {"completed": True}},
                "combat_encounter": {
                    "target_id": "mutated_zygomite_level_74",
                    "enemy_lifepoints": 19,
                },
                "combat_supply_loadout": {
                    "finishers": {
                        "Fungicide spray 6": 1,
                        "Fungicide": 1,
                    },
                },
            }
        )
        charged_dialog = self._open(charged, current_skill="Combat")
        charged_combo = charged_dialog.findChild(QComboBox, "combatActionCombo")
        self.assertEqual(charged_combo.itemText(1), "Spray with fungicide")
        self.assertTrue(charged_combo.model().item(1).isEnabled())
        self.assertIn(
            "Spends one Fungicide spray charge",
            charged_combo.model().item(1).toolTip(),
        )
        charged_tree = _find_tree_with_user_role(
            charged_dialog, "mutated_zygomite_level_74"
        )
        zygomite_74 = _tree_row(charged_tree, "mutated_zygomite_level_74")
        zygomite_86 = _tree_row(charged_tree, "mutated_zygomite_level_86")
        self.assertFalse(zygomite_74.icon(0).isNull())
        self.assertFalse(zygomite_86.icon(0).isNull())
        self.assertIn("6 spray charges + 1 canister reloads", zygomite_74.toolTip(0))
        self.assertIn("Encounter: Pick the fungi", zygomite_74.toolTip(0))

        ordinary_dialog.deleteLater()
        blocked_dialog.deleteLater()
        ready_dialog.deleteLater()
        reusable_dialog.deleteLater()
        charged_dialog.deleteLater()

    def test_combat_sidebar_hides_combat_only_stat_skills(self) -> None:
        from ankiscape.ui import ui

        combat_button = next(b for b in self.dialog.findChildren(QPushButton) if b.text() == "Combat")
        combat_button.click()
        QApplication.processEvents()

        skill_list = next(
            lw for lw in self.dialog.findChildren(QListWidget)
            if any(lw.item(i).text() == "Combat" for i in range(lw.count()))
        )
        texts = [skill_list.item(i).text() for i in range(skill_list.count())]
        self.assertEqual(texts, ["Combat", "Prayer", "Magic", "Summoning"])
        combat_item = next(
            skill_list.item(i)
            for i in range(skill_list.count())
            if skill_list.item(i).text() == "Combat"
        )
        self.assertEqual(
            _icon_pixels(combat_item.icon()),
            _icon_pixels(
                QIcon(
                    os.path.join(_ADDON_DIR, "icon", "combat_icon.png")
                )
            ),
        )
        for hidden in ("Attack", "Constitution", "Defense", "Ranged", "Strength"):
            self.assertNotIn(hidden, texts)

    def test_combat_xp_bars_use_each_combat_skill_icon(self) -> None:
        dialog = self._open(_make_player_data(), current_skill="Combat")
        expected = {
            "Attack": "attack_icon.png",
            "Strength": "strength_icon.png",
            "Defence": "defense_icon.png",
            "Ranged": "ranged_icon.png",
            "Magic": "magic_icon.png",
            "Constitution": "constitution_icon.png",
        }
        rendered = {}
        for skill, filename in expected.items():
            label = dialog.findChild(
                QLabel, f"combatXpIcon{skill.replace(' ', '')}"
            )
            self.assertIsNotNone(label)
            self.assertIsNotNone(label.pixmap())
            icon = QIcon(label.pixmap())
            self.assertEqual(
                self._ui.skill_icon_path_for(skill),
                os.path.join(_ADDON_DIR, "icon", filename),
            )
            rendered[skill] = _icon_pixels(icon)
        self.assertEqual(len(set(rendered.values())), len(expected))

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

    def test_wilderness_combat_confirmation_is_cached_for_the_session_risk_set(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "constitution_level": 99,
                "combat_lifepoints": 990,
                "equipment": {
                    "weapon": "Rune sword",
                    "body": "Rune platebody",
                    "head": "Rune full helm",
                    "shield": "Iron kiteshield",
                },
            }
        )
        dialog = self._open(pd, current_skill="Combat")
        tree = _find_tree_with_user_role(dialog, "earth_warrior")
        earth_warrior = _tree_row(tree, "earth_warrior")
        original_question = self._ui.QMessageBox.question
        questions = []
        try:
            def _accept(*args, **kwargs):  # type: ignore[no-untyped-def]
                questions.append(args)
                return self._ui.QMessageBox.StandardButton.Yes

            self._ui.QMessageBox.question = _accept
            tree.itemClicked.emit(earth_warrior, 0)
            tree.itemClicked.emit(earth_warrior, 0)
            QApplication.processEvents()

            self.assertEqual(len(questions), 1)
            self.assertEqual(questions[0][1], "Confirm Wilderness combat")
            self.assertIn("creates no grave", questions[0][2])
            self.assertEqual(
                self._combat_calls[-2:],
                ["earth_warrior", "earth_warrior"],
            )
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

    def test_combat_exposes_bound_borrowed_power_as_one_manual_cast(self) -> None:
        from ankiscape.data.livid_farm_data import ARCANE_CAPACITOR_CHARGED

        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "magic_standard",
                "current_combat_spell": "wind_strike",
                "magic_level": 99,
                "equipment": {
                    "weapon": "Staff of air",
                    "neck": ARCANE_CAPACITOR_CHARGED,
                },
                "livid_farm": {
                    "borrowed_power_claimed": True,
                    "arcane_capacitor_spell": "wind_wave",
                    "arcane_capacitor_charges": 12,
                },
            }
        )
        dialog = self._open(pd, current_skill="Combat")
        _open_equipment_tab(dialog)
        dialog.show()
        QApplication.processEvents()

        row = dialog.findChild(QWidget, "combatBorrowedPowerRow")
        spell = dialog.findChild(QLabel, "combatBorrowedPowerSpell")
        button = dialog.findChild(QPushButton, "combatBorrowedPowerButton")
        self.assertTrue(row.isVisible())
        self.assertEqual(
            spell.text(),
            "Borrowed Power · Wind Wave · 12 charges",
        )
        self.assertEqual(button.text(), "Cast once next review")
        self.assertEqual(
            button.geometry().left(),
            spell.geometry().left(),
        )

        button.click()
        QApplication.processEvents()

        self.assertEqual(
            self._prayer_config_calls[-1],
            ("combat_borrowed_power_spell", "wind_wave"),
        )
        self.assertEqual(pd["combat_borrowed_power_spell"], "wind_wave")
        self.assertEqual(button.text(), "One cast armed")

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
                "inventory": {"Fire rune": 100},
                "current_combat_target": "chicken",
                "combat_auto_eat_threshold_percent": 55,
                "combat_auto_eat_food": ["Lobster", "Shrimps"],
                "combat_supply_loadout": {
                    "food": {"Lobster": 3},
                    "potions": {"Antipoison (1)": 1},
                    "ammo": {"Bronze arrows": 10},
                    "runes": {"Air rune": 5, "Mind rune": 5, "Fire rune": 50},
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
        _open_bank_tab(dialog)
        bank = _find_list_with_item_prefix(dialog, "Fire rune x100")
        self.assertTrue(any(text.startswith("Fire rune x100") for text in _list_texts(bank)))

        threshold_spin.setValue(60)
        QApplication.processEvents()
        self.assertEqual(self._combat_threshold_calls[-1], 60)

        clear_button.click()
        QApplication.processEvents()
        self.assertEqual(self._combat_unload_calls, [True])
        bank = _find_list_with_item_prefix(dialog, "Fire rune x150")
        self.assertTrue(any(text.startswith("Fire rune x150") for text in _list_texts(bank)))

    def test_agility_auto_pack_summary_replaces_combat_only_controls(self) -> None:
        from aqt.qt import QLabel, QPushButton, QComboBox

        dialog = self._open(
            _make_player_data(),
            current_skill="Agility",
            get_carried_auto_summary=lambda: (
                "Wilderness Agility Course Auto pack · 28/28 slots\n"
                "Food: Shark x28\nRequirements: ready\n"
                "Weight: 16.8 kg carried · 16.8 kg effective"
            ),
            get_carried_bank_run_summary=lambda: "Bank run: ready",
            carried_auto_is_combat=False,
        )
        dialog.show()
        _open_equipment_tab(dialog)
        QApplication.processEvents()

        summary = dialog.findChild(QLabel, "combatLoadoutSummaryLabel")
        bank_run = dialog.findChild(QLabel, "combatBankRunLabel")
        supply_mode = dialog.findChild(QComboBox, "combatPackModeCombo")
        clear_button = dialog.findChild(QPushButton, "combatClearInventoryButton")
        self.assertIn("Food: Shark x28", summary.text())
        self.assertIn("Weight: 16.8 kg carried", summary.text())
        self.assertEqual(bank_run.text(), "Bank run: ready")
        self.assertFalse(supply_mode.isVisibleTo(dialog))
        self.assertFalse(clear_button.isVisibleTo(dialog))
        dialog.deleteLater()

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
        self.assertIn("Base XP: 128 per successful catch", wild.toolTip(0))
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
        pd["inventory"] = {
            "Logs": 1,
            "Headless arrows": 15,
            "Broad arrow heads": 15,
            "Long kebbit spike": 1,
            "Chisel": 1,
        }
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
        long_kebbit = _fletching_row(tree, "fletch_long_kebbit_bolts")
        self.assertFalse(long_kebbit.isDisabled())
        self.assertIn("Long kebbit spike x1", long_kebbit.toolTip(0))
        self.assertIn("Chisel x1", long_kebbit.toolTip(0))

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
        self.assertIn("Base XP: 40", logs_row.toolTip())
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

    def test_target_details_are_optional_live_and_provenance_free(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 33
        pd["inventory"] = {"Raw shrimps": 2, "Raw beef": 1}
        pd["current_cooking"] = "cook_shrimps"
        dialog = self._open(pd, current_skill="Cooking")
        dialog.show()
        QApplication.processEvents()

        tree = _goto_cooking(dialog)
        toggle = dialog.findChild(QToolButton, "targetDetailsToggle")
        panel = dialog.findChild(QWidget, "targetDetailsPanel")
        title = dialog.findChild(QLabel, "targetDetailsTitle")
        body = dialog.findChild(QLabel, "targetDetailsBody")
        details_scroll = dialog.findChild(QScrollArea, "targetDetailsScroll")

        self.assertTrue(toggle.isVisibleTo(dialog))
        self.assertFalse(panel.isVisibleTo(dialog))
        self.assertEqual(details_scroll.maximumHeight(), 190)
        self.assertEqual(title.text(), "Cook raw shrimps (Lvl 1)")
        self.assertIn("Success output: Shrimps x1", body.text())
        self.assertIn("Success chance:", body.text())
        self.assertNotIn("Source:", body.text())

        toggle.click()
        QApplication.processEvents()
        self.assertTrue(panel.isVisibleTo(dialog))
        self.assertEqual(toggle.arrowType(), Qt.ArrowType.DownArrow)

        beef = _cooking_row(tree, "cook_beef")
        tree.setCurrentItem(beef)
        QApplication.processEvents()
        self.assertEqual(title.text(), "Cook raw beef (Lvl 1)")
        self.assertIn("Success output: Cooked meat x1", body.text())
        self.assertTrue(panel.isVisibleTo(dialog))

        calls_before_locked_click = list(self._cooking_calls)
        shark = _cooking_row(tree, "cook_shark")
        tree.itemClicked.emit(shark, 0)
        QApplication.processEvents()
        self.assertEqual(title.text(), "Cook raw shark (Lvl 80)")
        self.assertIn("Locked due to:", body.text())
        self.assertEqual(self._cooking_calls, calls_before_locked_click)

        self._ui._MAIN_MENU_CTX["open_farming"]()
        QApplication.processEvents()
        farming_panel = dialog.findChild(QWidget, "targetDetailsPanel")
        self.assertFalse(farming_panel.isVisibleTo(dialog))
        dialog.deleteLater()

    def test_flat_target_details_use_the_current_registry_row(self) -> None:
        pd = _make_player_data()
        pd["mining_level"] = 33
        pd["current_ore"] = "copper"
        dialog = self._open(pd, current_skill="Mining")
        dialog.show()
        QApplication.processEvents()

        toggle = dialog.findChild(QToolButton, "targetDetailsToggle")
        title = dialog.findChild(QLabel, "targetDetailsTitle")
        body = dialog.findChild(QLabel, "targetDetailsBody")

        self.assertTrue(toggle.isVisibleTo(dialog))
        self.assertIn("Copper", title.text())
        self.assertIn("Output: Copper ore x1", body.text())
        self.assertIn("Best usable pickaxe: Bronze pickaxe", body.text())
        self.assertNotIn("Source:", body.text())

        ore_list = _find_list_with_user_role(dialog, "copper")
        runite = next(
            ore_list.item(index)
            for index in range(ore_list.count())
            if ore_list.item(index).data(Qt.ItemDataRole.UserRole) == "runite"
        )
        ore_list.itemClicked.emit(runite)
        QApplication.processEvents()
        self.assertIn("Runite", title.text())
        self.assertIn("Locked due to:", body.text())
        dialog.deleteLater()

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

    def test_cheese_wheel_rows_explain_slice_all_and_use_period_art(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 48
        pd["inventory"] = {
            "Bucket of milk": 1,
            "Pat of butter": 1,
            "Cheese wheel": 1,
        }
        pd["current_cooking"] = "slice_cheese_wheel"
        dialog = self._open(pd)
        tree = _goto_cooking(dialog)

        dairy = _cooking_family_node(tree, "dairy")
        self.assertEqual(dairy.text(0), "Dairy  (3)")
        slice_row = _cooking_row(tree, "slice_cheese_wheel")
        self.assertFalse(slice_row.isDisabled())
        self.assertFalse(slice_row.icon(0).isNull())
        self.assertEqual(
            tree.selectionMode(),
            QAbstractItemView.SelectionMode.NoSelection,
        )
        self.assertTrue(slice_row.font(0).bold())
        self.assertIn(
            "Success output: Cheese x5-35 (one Slice-all action)",
            slice_row.toolTip(0),
        )
        self.assertIn("Base XP: 4 per slice", slice_row.toolTip(0))
        milk_row = _cooking_row(tree, "churn_milk_cheese_wheel")
        self.assertIn("Also returns: Bucket x1", milk_row.toolTip(0))

        tree.itemClicked.emit(slice_row, 0)
        QApplication.processEvents()
        self.assertEqual(self._cooking_calls[-1], "slice_cheese_wheel")

    def test_overload_row_has_rs_wiki_icon_inputs_and_vial_byproduct(self) -> None:
        pd = _make_player_data()
        pd["herblore_level"] = 96
        pd["current_herblore"] = "finished_overload"
        pd["inventory"] = {
            "Extreme attack (3)": 1,
            "Extreme strength (3)": 1,
            "Extreme defence (3)": 1,
            "Extreme magic (3)": 1,
            "Extreme ranging (3)": 1,
            "Clean torstol": 1,
        }
        dialog = self._open(pd, current_skill="Herblore")
        artisan = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        herblore_row = next(
            index for index in range(skill_list.count()) if skill_list.item(index).text() == "Herblore"
        )
        skill_list.setCurrentRow(herblore_row)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "finished_overload")
        overload = _tree_row(tree, "finished_overload")

        self.assertFalse(overload.isDisabled())
        self.assertFalse(overload.icon(0).isNull())
        self.assertIn("Base XP: 1000", overload.toolTip(0))
        self.assertIn("Byproduct: Vial x4", overload.toolTip(0))
        self.assertIn("Extreme ranging (3) x1", overload.toolTip(0))

    def test_herblore_uses_its_skill_icon_and_icons_every_overworld_action(self) -> None:
        pd = _make_player_data()
        pd["herblore_level"] = 99
        pd["current_herblore"] = "clean_guam"
        dialog = self._open(pd, current_skill="Herblore")
        artisan = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        herblore_item = next(
            skill_list.item(index)
            for index in range(skill_list.count())
            if skill_list.item(index).text() == "Herblore"
        )
        skill_list.setCurrentItem(herblore_item)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "clean_guam")
        clean_group = _tree_row(tree, "__herblore_group__:clean")
        unf_group = _tree_row(tree, "__herblore_group__:unf")
        finished_group = _tree_row(tree, "__herblore_group__:finished")

        self.assertFalse(herblore_item.icon().isNull())
        self.assertEqual(
            _icon_pixels(herblore_item.icon()),
            _icon_pixels(QIcon(self._ui.skill_icon_path_for("Herblore"))),
        )
        self.assertNotEqual(
            _icon_pixels(herblore_item.icon()),
            _icon_pixels(QIcon(os.path.join(_ADDON_DIR, "icon", "achievement_icon.png"))),
        )
        self.assertEqual(clean_group.childCount(), 22)
        self.assertEqual(unf_group.childCount(), 22)
        self.assertEqual(finished_group.childCount(), 70)
        action_rows = [
            item
            for item in _smith_tree_items(tree)
            if not str(item.data(0, Qt.ItemDataRole.UserRole)).startswith("__herblore_group__:")
        ]
        self.assertEqual(len(action_rows), 114)
        self.assertTrue(all(not item.icon(0).isNull() for item in action_rows))
        self.assertNotIn(
            "clean_sagawort",
            {item.data(0, Qt.ItemDataRole.UserRole) for item in _smith_tree_items(tree)},
        )

    def test_shrink_me_quick_row_exposes_recipe_lock_icon_and_selection(self) -> None:
        pd = _make_player_data()
        pd["herblore_level"] = 52
        pd["current_herblore"] = "clean_guam"
        dialog = self._open(pd, current_skill="Herblore")
        artisan = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        herblore_item = next(
            skill_list.item(index)
            for index in range(skill_list.count())
            if skill_list.item(index).text() == "Herblore"
        )
        skill_list.setCurrentItem(herblore_item)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "finished_shrink_me_quick")
        row = _tree_row(tree, "finished_shrink_me_quick")

        self.assertTrue(row.isDisabled())
        self.assertFalse(row.icon(0).isNull())
        self.assertIn("Base XP: 6", row.toolTip(0))
        self.assertIn("Tarromin potion (unf) x1", row.toolTip(0))
        self.assertIn("Shrunk ogleroot x1", row.toolTip(0))

        before = list(self._herblore_calls)
        tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._herblore_calls, before)

        pd["inventory"] = {
            "Tarromin potion (unf)": 1,
            "Shrunk ogleroot": 1,
        }
        dialog = self._open(pd, current_skill="Herblore")
        artisan = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        herblore_item = next(
            skill_list.item(index)
            for index in range(skill_list.count())
            if skill_list.item(index).text() == "Herblore"
        )
        skill_list.setCurrentItem(herblore_item)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "finished_shrink_me_quick")
        row = _tree_row(tree, "finished_shrink_me_quick")
        self.assertFalse(row.isDisabled())

        tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._herblore_calls[-1], "finished_shrink_me_quick")

    def test_summoning_uses_canonical_icon_and_complete_surface_target_tree(self) -> None:
        pd = _make_player_data()
        pd["summoning_level"] = 99
        pd["inventory"] = {
            "Pouch": 1,
            "Spirit shards": 7,
            "Gold charm": 1,
            "Wolf bones": 1,
        }
        dialog = self._open(pd, current_skill="Summoning")
        skill_list = next(
            widget
            for widget in dialog.findChildren(QListWidget)
            if "Summoning" in [
                widget.item(index).text() for index in range(widget.count())
            ]
        )
        summoning_item = next(
            skill_list.item(index)
            for index in range(skill_list.count())
            if skill_list.item(index).text() == "Summoning"
        )
        skill_list.setCurrentItem(summoning_item)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "infuse_spiritwolf")
        infuse_group = _tree_row(
            tree, "__summoning_group__:Infuse pouches"
        )
        scroll_group = _tree_row(
            tree, "__summoning_group__:Create scrolls"
        )

        self.assertFalse(summoning_item.icon().isNull())
        self.assertEqual(
            _icon_pixels(summoning_item.icon()),
            _icon_pixels(QIcon(self._ui.skill_icon_path_for("Summoning"))),
        )
        self.assertEqual(infuse_group.childCount(), 78)
        self.assertEqual(scroll_group.childCount(), 67)
        rows = [
            item
            for item in _smith_tree_items(tree)
            if not str(
                item.data(0, Qt.ItemDataRole.UserRole)
            ).startswith("__summoning_group__:")
        ]
        self.assertEqual(len(rows), 145)
        self.assertTrue(all(not item.icon(0).isNull() for item in rows))

    def test_equipment_follower_panel_projects_familiars_and_complete_pet_log(self) -> None:
        from ankiscape.logic.summoning_logic import default_summoning_state_pure, summon_familiar_pure

        pd = _make_player_data()
        pd["summoning_level"] = 99
        pd["inventory"] = {"Spirit wolf pouch": 1}
        pd["summoning_state"] = default_summoning_state_pure()
        calls = []

        def command(action_id, payload):
            calls.append((action_id, dict(payload)))
            if action_id != "summon":
                return {"ok": False}
            updated, ok, info = summon_familiar_pure(
                pd, str(payload.get("familiar_id", ""))
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, **info}

        dialog = self._open(
            pd,
            current_skill="Summoning",
            on_summoning_command=command,
        )
        dialog.show()
        _open_equipment_tab(dialog)
        QApplication.processEvents()

        panel = dialog.findChild(QWidget, "summoningFollowerPanel")
        summary = dialog.findChild(QLabel, "summoningFollowerSummary")
        picker = dialog.findChild(QComboBox, "summoningFamiliarPicker")
        summon = dialog.findChild(QPushButton, "summoningSummonButton")
        pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
        self.assertIsNotNone(panel)
        self.assertEqual(summary.text(), "No follower active.")
        self.assertEqual(pets.topLevelItemCount(), 44)

        picker.setCurrentIndex(picker.findData("spiritwolf"))
        summon.click()
        QApplication.processEvents()

        self.assertEqual(calls, [("summon", {"familiar_id": "spiritwolf"})])
        self.assertIn("Spirit wolf", summary.text())
        self.assertIn("review(s) remain", summary.text())
        self.assertIsNone(
            panel.findChild(
                QPushButton, "summoningStartFamiliarisationButton"
            )
        )
        dialog.deleteLater()

    def test_pets_surface_hatches_banked_phoenix_eggs_at_level_72(self) -> None:
        from ankiscape.logic.pet_logic import hatch_phoenix_egg_pure
        from ankiscape.logic.summoning_logic import default_summoning_state_pure

        pd = _make_player_data()
        pd["summoning_level"] = 72
        pd["inventory"] = {"Phoenix egg": 1, "Cracked phoenix egg": 1}
        pd["summoning_state"] = default_summoning_state_pure()
        calls = []

        def command(action_id, payload):
            calls.append((action_id, dict(payload)))
            if action_id != "hatch_phoenix_egg":
                return {"ok": False}
            updated, ok, info = hatch_phoenix_egg_pure(
                pd, str(payload.get("item_name", ""))
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "instance_id": info if ok else "", "reason": info}

        dialog = self._open(
            pd,
            current_skill="Summoning",
            on_summoning_command=command,
        )
        dialog.show()
        _open_equipment_tab(dialog)
        QApplication.processEvents()

        toggle = dialog.findChild(QPushButton, "summoningPetsToggle")
        row = dialog.findChild(QWidget, "summoningPhoenixEggRow")
        label = dialog.findChild(QLabel, "summoningPhoenixEggLabel")
        cute = dialog.findChild(QPushButton, "summoningHatchCutePhoenixButton")
        mean = dialog.findChild(QPushButton, "summoningHatchMeanPhoenixButton")
        toggle.click()
        QApplication.processEvents()
        self.assertFalse(row.isHidden())
        self.assertEqual(label.text(), "Phoenix eggs")
        self.assertEqual(cute.text(), "Hatch Cute · 1")
        self.assertEqual(mean.text(), "Hatch Mean · 1")
        self.assertIn("Phoenix egg", cute.toolTip())
        self.assertIn("Cracked phoenix egg", mean.toolTip())

        cute.click()
        QApplication.processEvents()
        self.assertEqual(
            calls[-1],
            ("hatch_phoenix_egg", {"item_name": "Phoenix egg"}),
        )
        self.assertEqual(pd["inventory"]["Phoenix egg"], 0)
        self.assertEqual(cute.text(), "Hatch Cute · 0")
        self.assertTrue(
            any(
                instance["pet_id"] == "cute_phoenix_eggling"
                for instance in pd["summoning_state"]["pet_instances"].values()
            )
        )
        dialog.deleteLater()

    def test_pets_surface_explains_phoenix_egg_level_gate_inline(self) -> None:
        from ankiscape.logic.summoning_logic import default_summoning_state_pure

        pd = _make_player_data()
        pd["summoning_level"] = 71
        pd["inventory"] = {"Phoenix egg": 1}
        pd["summoning_state"] = default_summoning_state_pure()
        dialog = self._open(pd, current_skill="Summoning")
        dialog.show()
        _open_equipment_tab(dialog)
        toggle = dialog.findChild(QPushButton, "summoningPetsToggle")
        toggle.click()
        QApplication.processEvents()

        label = dialog.findChild(QLabel, "summoningPhoenixEggLabel")
        cute = dialog.findChild(QPushButton, "summoningHatchCutePhoenixButton")
        self.assertEqual(label.text(), "Phoenix eggs · needs Summoning 72")
        self.assertFalse(cute.isEnabled())
        dialog.deleteLater()

    def test_familiarisation_lives_in_activities_and_runs_its_session(self) -> None:
        from ankiscape.logic.summoning_logic import (
            default_summoning_state_pure,
            start_familiarisation_pure,
        )

        pd = _make_player_data()
        pd["current_utility"] = "bankstanding"
        pd["summoning_state"] = default_summoning_state_pure()
        calls = []

        def command(action_id, payload):
            calls.append((action_id, dict(payload)))
            if action_id != "start_familiarisation":
                return {"ok": False}
            updated, ok = start_familiarisation_pure(pd)
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_summoning_command=command,
        )
        dialog.show()
        tree = self._open_activities(dialog)
        row = _utility_row(tree, "familiarisation")
        tree.setCurrentItem(row)
        tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "familiarisationPanel")
        start = _find_named_button(
            dialog, "summoningStartFamiliarisationButton"
        )
        self.assertTrue(panel.isVisible())
        self.assertEqual(pd["current_utility"], "bankstanding")

        start.click()
        QApplication.processEvents()
        self.assertEqual(calls, [("start_familiarisation", {})])
        self.assertTrue(
            pd["summoning_state"]["familiarisation"]["active"]
        )
        self.assertIn(
            "0/4 segments",
            _find_named_label(dialog, "familiarisationSummary").text(),
        )
        dialog.deleteLater()

    def test_pack_yak_panel_exposes_target_priority_and_advanced_threshold(self) -> None:
        pd = _make_player_data()
        pd["summoning_level"] = 99
        pd["carried_inventory"] = {
            "copper": {"Copper ore": 4, "Winter storage scroll": 2}
        }
        pd["summoning_state"] = {
            "summoning_points_current": 99,
            "special_move_points_current": 60,
            "active_follower": {
                "kind": "familiar",
                "entity_id": "packyak",
                "remaining_reviews": 10,
                "max_reviews": 10,
                "lifepoints": 7100,
                "max_lifepoints": 7100,
                "storage": {},
            },
            "target_policies": {
                "copper": {
                    "winter_storage_priority": ["Copper ore"],
                    "winter_storage_threshold_free_slots": 3,
                }
            },
        }
        calls = []
        dialog = self._open(
            pd,
            current_skill="Mining",
            active_carried_target_id="copper",
            carried_pack_target_active=True,
            carried_advanced_state=True,
            on_summoning_command=lambda action_id, payload: calls.append(
                (action_id, dict(payload))
            )
            or {"ok": True},
        )
        dialog.show()
        _open_equipment_tab(dialog)
        QApplication.processEvents()

        row = dialog.findChild(QWidget, "summoningWinterStorageRow")
        picker = dialog.findChild(QComboBox, "summoningWinterStoragePicker")
        threshold = dialog.findChild(
            QSpinBox, "summoningWinterStorageThreshold"
        )
        save = dialog.findChild(
            QPushButton, "summoningWinterStorageSetButton"
        )
        self.assertFalse(row.isHidden())
        self.assertEqual(picker.currentData(), "Copper ore")
        self.assertFalse(threshold.isHidden())
        self.assertEqual(threshold.value(), 3)

        threshold.setValue(2)
        save.click()
        QApplication.processEvents()
        self.assertEqual(
            calls,
            [
                (
                    "set_winter_storage_priority",
                    {
                        "target_id": "copper",
                        "item_name": "Copper ore",
                        "threshold_free_slots": 2,
                    },
                )
            ],
        )
        dialog.deleteLater()

    def test_cannonball_row_shows_quest_gate_mould_and_icon(self) -> None:
        pd = _make_player_data()
        pd["smithing_level"] = 35
        pd["current_smith"] = "forge_cannonballs"
        pd["inventory"] = {"Steel bar": 1, "Ammo mould": 1}
        pd["quests"]["dwarf_cannon"] = {"completed": True}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        row = _smith_row(_find_smith_tree(dialog), "forge_cannonballs")

        self.assertFalse(row.isDisabled())
        self.assertFalse(row.icon(0).isNull())
        self.assertIn("Output: Cannonball x4", row.toolTip(0))
        self.assertIn("Required tools:", row.toolTip(0))
        self.assertIn("Ammo mould x1", row.toolTip(0))

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

    def test_wicked_hood_card_exposes_live_allowances_and_manual_actions(self) -> None:
        from ankiscape.logic.wicked_hood_logic import apply_wicked_hood_command_pure

        pd = _make_player_data()
        pd["runecrafting_level"] = 1
        pd["quests"]["rune_mysteries"] = {
            "started": True,
            "progress": 6,
            "completed": True,
        }
        pd["claims"]["wicked_hood"] = {"claimed": True}
        pd["equipment"] = {"head": "Wicked hood"}
        pd["wicked_hood"] = {
            "fed_altars": ["air"],
            "allowance_day": 0,
            "essence_remaining": 100,
            "rune_withdrawals_remaining": 1,
            "teleports_remaining": 2,
        }
        calls = []

        def _hood_command(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated, ok, info = apply_wicked_hood_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("message", info.get("reason", "")), **info}

        dialog = self._open(pd, on_wicked_hood_command=_hood_command)
        _goto_runecrafting(dialog)

        card = dialog.findChild(QWidget, "wickedHoodCard")
        remaining = dialog.findChild(QLabel, "wickedHoodRemainingLabel")
        essence = dialog.findChild(QPushButton, "wickedHoodEssenceButton")
        rune_combo = dialog.findChild(QComboBox, "wickedHoodRuneCombo")
        teleport = dialog.findChild(QPushButton, "wickedHoodTeleportButton")
        self.assertIsNotNone(card)
        self.assertEqual(
            remaining.text(),
            "100/100 essence · 1/1 rune withdrawals · 2/2 teleports",
        )
        self.assertTrue(essence.isEnabled())
        self.assertEqual(rune_combo.currentData(), "air")
        self.assertTrue(teleport.isEnabled())

        essence.click()
        QApplication.processEvents()

        self.assertEqual(calls[-1], ("essence", {}))
        self.assertEqual(pd["carried_inventory"]["craft_air_runes"]["Rune essence"], 28)
        refreshed = dialog.findChild(QLabel, "wickedHoodRemainingLabel")
        self.assertEqual(
            refreshed.text(),
            "72/100 essence · 1/1 rune withdrawals · 2/2 teleports",
        )
        feedback = dialog.findChild(QLabel, "wickedHoodFeedbackLabel")
        self.assertEqual(feedback.text(), "Withdrew 28 Rune essence.")

        teleport = dialog.findChild(QPushButton, "wickedHoodTeleportButton")
        teleport.click()
        QApplication.processEvents()
        guidance = dialog.findChild(QLabel, "wickedHoodGuidanceLabel")
        teleport_choice = dialog.findChild(QComboBox, "wickedHoodTeleportCombo")
        self.assertIn("Queued for Air altar", guidance.text())
        self.assertEqual(teleport_choice.currentData(), "air")
        self.assertFalse(teleport_choice.isEnabled())
        self.assertFalse(
            dialog.findChild(QPushButton, "wickedHoodTeleportButton").isEnabled()
        )

    def test_wicked_hood_card_labels_exhausted_allowances(self) -> None:
        pd = _make_player_data()
        pd["claims"]["wicked_hood"] = {"claimed": True}
        pd["equipment"] = {"head": "Wicked hood"}
        pd["wicked_hood"] = {
            "fed_altars": ["air"],
            "allowance_day": 0,
            "essence_remaining": 0,
            "rune_withdrawals_remaining": 0,
            "teleports_remaining": 0,
        }
        dialog = self._open(pd, on_wicked_hood_command=lambda *_args: {})
        _goto_runecrafting(dialog)

        guidance = dialog.findChild(QLabel, "wickedHoodGuidanceLabel")
        self.assertEqual(
            guidance.text(),
            "Allowances exhausted · refills every 240 answered cards",
        )

    def test_wicked_hood_card_hides_before_claim(self) -> None:
        pd = _make_player_data()

        dialog = self._open(pd)
        _goto_runecrafting(dialog)

        card = dialog.findChild(QWidget, "wickedHoodCard")
        self.assertIsNotNone(card)
        self.assertTrue(card.isHidden())

    def test_wicked_hood_teleport_exposes_selected_altar_level_gate(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 1
        pd["claims"]["wicked_hood"] = {"claimed": True}
        pd["equipment"] = {"head": "Wicked hood"}
        pd["wicked_hood"] = {
            "fed_altars": ["nature"],
            "allowance_day": 0,
            "essence_remaining": 100,
            "rune_withdrawals_remaining": 1,
            "teleports_remaining": 2,
        }

        dialog = self._open(pd, on_wicked_hood_command=lambda *_args: {})
        _goto_runecrafting(dialog)

        choice = dialog.findChild(QComboBox, "wickedHoodTeleportCombo")
        button = dialog.findChild(QPushButton, "wickedHoodTeleportButton")
        self.assertEqual(choice.currentData(), "nature")
        self.assertIn("Lv 44", choice.currentText())
        self.assertFalse(button.isEnabled())
        self.assertEqual(button.toolTip(), "Requires level 44 Runecrafting.")

    def test_wicked_hood_actions_fit_the_narrow_skills_panel(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 99
        pd["claims"]["wicked_hood"] = {"claimed": True}
        pd["equipment"] = {"head": "Wicked hood"}
        pd["wicked_hood"] = {
            "fed_altars": ["air", "nature"],
            "allowance_day": 0,
            "essence_remaining": 100,
            "rune_withdrawals_remaining": 1,
            "teleports_remaining": 2,
        }
        dialog = self._open(pd, on_wicked_hood_command=lambda *_args: {})
        dialog.resize(820, 620)
        _goto_runecrafting(dialog)
        QApplication.processEvents()

        card = dialog.findChild(QWidget, "wickedHoodCard")
        remaining = dialog.findChild(QLabel, "wickedHoodRemainingLabel")
        buttons = [
            dialog.findChild(QPushButton, "wickedHoodEssenceButton"),
            dialog.findChild(QPushButton, "wickedHoodRunesButton"),
            dialog.findChild(QPushButton, "wickedHoodTeleportButton"),
        ]
        self.assertLessEqual(remaining.geometry().right(), card.rect().right())
        for button in buttons:
            self.assertGreaterEqual(button.width(), button.sizeHint().width(), button.text())

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

    def test_flat_target_lists_mark_the_current_target(self) -> None:
        # The flat lists (Mining/Woodcutting/Firemaking/Fishing) lost their
        # visible current-target mark: QStyle's legacy selection rect renders
        # as a near-white wash under alternatingRowColors, so the row is
        # marked with the grouped tree's green brush instead.
        for skill, key, target in (
            ("Mining", "current_ore", "rune_essence"),
            ("Woodcutting", "current_tree", "tree"),
        ):
            pd = _make_player_data()
            pd[key] = target
            dialog = self._open(pd, current_skill=skill)
            try:
                dialog.show()
                QApplication.processEvents()
                target_list = next(
                    widget
                    for widget in dialog.findChildren(QListWidget)
                    if any("(Lvl" in widget.item(i).text() for i in range(widget.count()))
                )
                current = target_list.currentItem()
                self.assertIsNotNone(current, skill)
                self.assertEqual(
                    current.data(Qt.ItemDataRole.UserRole), target, skill
                )
                self.assertEqual(
                    current.background().color().getRgb()[:3], (76, 175, 80), skill
                )
                self.assertTrue(current.font().bold(), skill)
            finally:
                dialog.deleteLater()

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
        from ankiscape.ui import ui

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
    def test_stats_tab_shows_registered_skill_details(self) -> None:
        for skill_id, skill_name in (
            ("fletching", "Fletching"),
            ("firemaking", "Firemaking"),
            ("fishing", "Fishing"),
            ("runecrafting", "Runecrafting"),
        ):
            with self.subTest(skill=skill_name):
                dialog = self._open(_make_player_data(), current_skill="Mining")
                try:
                    _find_stats_button(dialog, skill_id).click()
                    QApplication.processEvents()
                    labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
                    self.assertIn(f"{skill_name} Stats", labels)
                    self.assertIn("Current / Base Level:", labels)
                finally:
                    dialog.deleteLater()

    def test_stats_tab_uses_period_three_column_grid_with_dungeoneering(self) -> None:
        stats_grid = self.dialog.findChild(QWidget, "statsSkillGrid")
        selector_scroll = self.dialog.findChild(QScrollArea, "statsSkillSelectorScroll")
        total_level = self.dialog.findChild(QLabel, "statsTotalLevel")
        self.assertIsNotNone(stats_grid)
        self.assertIsNotNone(selector_scroll)
        self.assertIsNotNone(total_level)
        self.assertEqual(selector_scroll.horizontalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        buttons = [
            button
            for button in stats_grid.findChildren(QToolButton)
            if button.objectName().startswith("statsSkillButton_")
        ]
        self.assertEqual(len(buttons), 25)
        positions = {
            button.accessibleName().split(",", 1)[0]: stats_grid.layout().getItemPosition(
                stats_grid.layout().indexOf(button)
            )[:2]
            for button in buttons
        }
        self.assertEqual(positions["Attack"], (0, 0))
        self.assertEqual(positions["Constitution"], (0, 1))
        self.assertEqual(positions["Mining"], (0, 2))
        self.assertEqual(positions["Summoning"], (7, 2))
        self.assertEqual(positions["Dungeoneering"], (8, 0))
        self.assertEqual(total_level.text(), "Total level: 569")

        dungeoneering = _find_stats_button(self.dialog, "dungeoneering")
        self.assertFalse(dungeoneering.icon().isNull())
        dungeoneering.click()
        QApplication.processEvents()
        labels = [label.text() for label in self.dialog.findChildren(QLabel)]
        self.assertIn("Dungeoneering Stats", labels)
        self.assertIn("Current / Base Level:", labels)
        progress_bar = self.dialog.findChild(QProgressBar, "statsSkillProgress")
        metrics = self.dialog.findChild(QWidget, "statsSkillMetrics")
        self.assertIsNotNone(progress_bar)
        self.assertIsNotNone(metrics)
        self.assertEqual(progress_bar.maximumWidth(), 320)
        self.assertEqual(metrics.maximumWidth(), 520)

    def test_stats_grid_shows_live_current_level_over_base_level(self) -> None:
        player_data = _make_player_data()
        player_data["combat_current_levels"] = {
            "attack": 40,
            "strength": 29,
        }
        player_data["agility_effective_boost"] = 5
        player_data["agility_boost_actions_remaining"] = 4
        dialog = self._open(player_data)
        try:
            self.assertEqual(_find_stats_button(dialog, "attack").text(), "40 / 1")
            self.assertEqual(_find_stats_button(dialog, "strength").text(), "29 / 1")
            self.assertEqual(_find_stats_button(dialog, "agility").text(), "38 / 33")
            self.assertEqual(_find_stats_button(dialog, "mining").text(), "33 / 33")
            _find_stats_button(dialog, "attack").click()
            QApplication.processEvents()
            labels = [label.text() for label in dialog.findChildren(QLabel)]
            self.assertIn("Current / Base Level:", labels)
            self.assertIn("40 / 1", labels)
        finally:
            dialog.deleteLater()

    def test_quests_tab_starts_rune_mysteries_via_quest_action(self) -> None:
        pd = _make_player_data()
        pd["quests"]["rune_mysteries"] = {"started": False, "progress": 0, "completed": False}
        dialog = self._open(pd)
        _open_quests_tab(dialog)
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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Needs Insect repellent x1"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_merlins_crystal")
        self.assertIsNotNone(action)
        self.assertFalse(action.isEnabled())
        self.assertIn("Insect repellent x1", action.toolTip())

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
        _open_quests_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        expected = "Blocked: Battle required: Sir Mordred level 39"
        self.assertIn(expected, labels)
        action = dialog.findChild(QPushButton, "questAction_merlins_crystal")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())

        action.click()
        QApplication.processEvents()
        self.assertIn("merlins_crystal", self._quest_calls)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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

    def test_quests_tab_allows_stolen_hearts_mercenary_stage_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "stolen_hearts"
        pd["quests"]["stolen_hearts"] = {
            "started": True,
            "progress": 3,
            "completed": False,
        }
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 99
        pd["strength_level"] = 99
        pd["defense_level"] = 99
        pd["constitution_level"] = 99
        pd["ranged_level"] = 99
        pd["magic_level"] = 99
        pd["prayer_level"] = 99
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn(
            (
                "Blocked: Battle required: Mercenary Joe level 2, "
                "Battle required: Skulls mercenary level 2 x2"
            ),
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_stolen_hearts")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Stolen Hearts stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("stolen_hearts", self._quest_calls)

    def test_quests_tab_allows_diamond_in_the_rough_ambush_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "diamond_in_the_rough"
        pd["inventory"] = {"Heavy weight": 1}
        pd["quests"]["stolen_hearts"] = {
            "started": True,
            "progress": 6,
            "completed": True,
        }
        pd["quests"]["diamond_in_the_rough"] = {
            "started": True,
            "progress": 2,
            "completed": False,
        }
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 99
        pd["strength_level"] = 99
        pd["defense_level"] = 99
        pd["constitution_level"] = 99
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn(
            (
                "Blocked: Battle required: Bandit (Diamond in the Rough) level 2 x5, "
                "Battle required: Bandit king level 3"
            ),
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_diamond_in_the_rough")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Diamond in the Rough stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("diamond_in_the_rough", self._quest_calls)

    def test_quests_tab_allows_icthlarins_canopic_guardian_selection(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "icthlarins_little_helper"
        pd["inventory"] = {}
        pd["quests"]["icthlarins_little_helper"] = {
            "started": True,
            "progress": 4,
            "completed": False,
        }
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 99
        pd["strength_level"] = 99
        pd["defense_level"] = 99
        pd["constitution_level"] = 99
        dialog = self._open(pd)
        _open_quests_tab(dialog)

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Battle required: Canopic guardian level 81", labels)
        action = dialog.findChild(QPushButton, "questAction_icthlarins_little_helper")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Icthlarin's Little Helper stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("icthlarins_little_helper", self._quest_calls)

    def test_quests_tab_surfaces_smoking_kills_boss_at_quest_combat_requirement(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "smoking_kills"
        pd["inventory"] = {"Masked earmuffs": 1}
        pd["quests"]["smoking_kills"] = {
            "started": True,
            "progress": 11,
            "completed": False,
        }
        pd["quest_combat_config"] = {"resolver_enabled": True}
        pd["attack_level"] = 74
        pd["strength_level"] = 74
        pd["defense_level"] = 74
        pd["constitution_level"] = 74
        pd["ranged_level"] = 1
        pd["magic_level"] = 1
        pd["prayer_level"] = 1
        pd["summoning_level"] = 1
        dialog = self._open(pd)
        _open_quests_tab(dialog)
        _expand_quest_card(dialog, "smoking_kills")

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn("Blocked: Battle required: Banshee Mistress level 111", labels)
        self.assertIn(
            "At half health the Banshee Mistress calls four level 141 Insectoid Assassins into the same battle.",
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_smoking_kills")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Smoking Kills stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("smoking_kills", self._quest_calls)

    def test_quests_tab_surfaces_shilo_village_three_form_boss_chain(self) -> None:
        pd = _make_player_data()
        pd["current_quest"] = "shilo_village"
        pd["inventory"] = {"Bone key": 1, "Beads of the dead": 1}
        pd["quests"]["shilo_village"] = {
            "started": True,
            "progress": 10,
            "completed": False,
        }
        pd["quest_combat_config"] = {"resolver_enabled": True}
        for level_key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
            "ranged_level",
            "magic_level",
            "prayer_level",
        ):
            pd[level_key] = 200
        dialog = self._open(pd)
        _open_quests_tab(dialog)
        _expand_quest_card(dialog, "shilo_village")

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        combat_status = next(label for label in labels if label.startswith("Blocked: Battle required: Nazastarool"))
        for encounter_text in (
            "Nazastarool (Zombie) level 91",
            "Nazastarool (Skeleton) level 68",
            "Nazastarool (Ghost) level 93",
        ):
            self.assertIn(encounter_text, combat_status)
        self.assertIn(
            "Nazastarool will return as a zombie, skeleton, and ghost before yielding Rashiliyia's corpse.",
            labels,
        )
        action = dialog.findChild(QPushButton, "questAction_shilo_village")
        self.assertIsNotNone(action)
        self.assertTrue(action.isEnabled())
        self.assertNotIn("Complete Shilo Village stage", action.toolTip())

        action.click()
        QApplication.processEvents()
        self.assertIn("shilo_village", self._quest_calls)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)

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
        _open_quests_tab(dialog)
        _expand_quest_card(dialog, "the_knights_sword")

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn(
            "Requires: Mining 10, Used during quest: Redberry pie x1, Blurite ore x1, Iron bar x2",
            labels,
        )

    def test_quests_tab_filters_by_catalog_metadata(self) -> None:
        dialog = self._open(_make_player_data())
        _open_quests_tab(dialog)

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

    def test_quest_search_composes_with_filters_and_has_shared_empty_state(self) -> None:
        dialog = self._open(_make_player_data())
        _open_quests_tab(dialog)
        search = _find_named_line_edit(dialog, "questSearchInput")
        summary = dialog.findChild(QLabel, "questFilterSummaryLabel")

        search.setText("while_guthix_sleeps")
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QWidget, "questCard_while_guthix_sleeps"))
        self.assertEqual(summary.text(), "Showing 1/194")

        hide_locked = dialog.findChild(QCheckBox, "questHideLockedCheck")
        hide_locked.setChecked(True)
        QApplication.processEvents()
        self.assertEqual(summary.text(), "Showing 0/194")
        self.assertIsNotNone(dialog.findChild(QLabel, "questEmptyFilterLabel"))

        hide_locked.setChecked(False)
        search.clear()
        QApplication.processEvents()
        self.assertEqual(summary.text(), "Showing 194/194")
        dialog.deleteLater()

    def test_bank_claims_expose_eligible_wicked_hood_claim(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 1
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("Wicked hood x1", labels)
        self.assertIn("Ready to claim", labels)
        # Locked claims are not rendered at all: a reward the player cannot
        # claim is not actionable information on the Bank tab.
        self.assertFalse(any("locked reward" in label for label in labels), labels)
        self.assertEqual(
            [lbl for lbl in dialog.findChildren(QLabel)
             if lbl.objectName() == "bankClaimsLockedSummary"],
            [],
        )
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

    def test_bank_claims_hide_locked_rows_entirely(self) -> None:
        pd = _make_player_data()
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("Tutorial Island starter kit", labels)
        self.assertNotIn("Wicked hood x1", labels)
        # The old summary named one arbitrary locked reward and counted the
        # rest as "N more hidden", which the player could not act on.
        self.assertFalse(any("locked reward" in label for label in labels), labels)
        self.assertEqual(
            [lbl for lbl in dialog.findChildren(QLabel)
             if lbl.objectName() == "bankClaimsLockedSummary"],
            [],
        )
        self.assertEqual(
            len([w for w in dialog.findChildren(QWidget) if w.objectName() == "bankClaimRow"]),
            1,
            "only actionable claims should render as individual action rows",
        )

    def test_bank_claims_locked_only_save_reads_as_caught_up(self) -> None:
        # Removing the locked summary left this save rendering a bare "Bank
        # Claims" header with nothing under it.
        pd = _make_player_data()
        pd.setdefault("claims", {})["tutorial_island_starter_kit"] = {"claimed": True}
        dialog = self._open(pd)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("All Bank Claims caught up.", labels)
        self.assertEqual(
            [w for w in dialog.findChildren(QWidget) if w.objectName() == "bankClaimRow"],
            [],
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

    def test_bank_search_filters_rows_and_categories_without_mutating_state(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Logs": 5,
            "Bronze bar": 2,
            "Arrow shafts": 30,
            "Feather": 50,
            "Bronze arrowtips": 15,
        }
        original_inventory = dict(pd["inventory"])
        dialog = self._open(pd)
        bank = _find_bank_list(dialog)
        search = _find_named_line_edit(dialog, "bankSearchInput")
        summary = _find_named_label(dialog, "bankSearchInputSummary")

        search.setText("arrow shafts")
        QApplication.processEvents()
        texts = [bank.item(i).text() for i in range(bank.count())]
        self.assertIn("Fletched", texts)
        self.assertIn("Arrow shafts x30", texts)
        self.assertNotIn("Logs", texts)
        self.assertNotIn("Bronze bar x2", texts)
        self.assertEqual(summary.text(), "Showing 1/5")
        self.assertEqual(pd["inventory"], original_inventory)

        search.setText("materials")
        QApplication.processEvents()
        texts = [bank.item(i).text() for i in range(bank.count())]
        self.assertIn("Materials", texts)
        self.assertIn("Feather x50", texts)
        self.assertNotIn("Arrow shafts x30", texts)

        search.setText("nothing-here")
        QApplication.processEvents()
        self.assertEqual(bank.count(), 1)
        self.assertEqual(bank.item(0).text(), "No Bank items match your search.")
        self.assertEqual(summary.text(), "Showing 0/5")

        search.clear()
        QApplication.processEvents()
        texts = [bank.item(i).text() for i in range(bank.count())]
        self.assertIn("Logs x5", texts)
        self.assertIn("Arrow shafts x30", texts)
        self.assertEqual(summary.text(), "Showing 5/5")
        self.assertEqual(pd["inventory"], original_inventory)

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
            from ankiscape.logic_pure.logic_pure import apply_consumable_pure
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

    def test_bank_uses_edible_verb_and_opens_all_supply_packs(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Summer pie": 1, "Vial pack": 2}
        opened: list[tuple[str, bool]] = []

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
            on_consume_item=lambda *_args: None,
            on_open_item_pack=lambda item_name, open_all: opened.append((item_name, open_all)) or True,
        )
        dialog = self._captured[-1]

        pie_menu = dialog._ankiscape_equip_menu_for("Summer pie")
        self.assertTrue(any(action.text() == "Eat Summer pie" for action in pie_menu.actions()))

        pack_menu = dialog._ankiscape_equip_menu_for("Vial pack")
        open_all = next(action for action in pack_menu.actions() if action.text() == "Open all (2)")
        self.assertEqual(open_all.toolTip(), "Receive 100 Vial.")
        open_all.trigger()
        QApplication.processEvents()
        self.assertEqual(opened, [("Vial pack", True)])

    def test_bank_converts_a_rogue_kit_to_any_period_tool(self) -> None:
        from ankiscape.logic.flash_powder_factory_logic import convert_rogue_kit_pure

        pd = _make_player_data()
        pd["inventory"] = {"Rogue kit": 2}
        converted: list[str] = []

        def _convert(output_item: str) -> bool:
            updated, ok, _info = convert_rogue_kit_pure(pd, output_item)
            if ok:
                pd.clear()
                pd.update(updated)
                converted.append(output_item)
            return ok

        dialog = self._open(pd, on_convert_rogue_kit=_convert)
        menu = dialog._ankiscape_equip_menu_for("Rogue kit")
        convert_action = next(
            action for action in menu.actions()
            if action.text() == "Convert Rogue kit to"
        )
        convert_menu = convert_action.menu()
        self.assertIsNotNone(convert_menu)
        self.assertEqual(
            [action.text() for action in convert_menu.actions()],
            ["Chisel", "Rope", "Tinderbox", "Spade"],
        )
        next(
            action for action in convert_menu.actions() if action.text() == "Rope"
        ).trigger()
        QApplication.processEvents()
        self.assertEqual(converted, ["Rope"])
        self.assertEqual(pd["inventory"]["Rogue kit"], 1)
        self.assertEqual(pd["inventory"]["Rope"], 1)

    def test_full_urn_bank_action_uses_stable_id_order_and_refreshes_immediately(self) -> None:
        from ankiscape.logic_pure.logic_pure import teleport_full_urn_pure
        from ankiscape.data.urn_data import URN_TIERS_BY_ID

        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        pd = _make_player_data()
        pd["mining_level"] = 1
        pd["mining_exp"] = 0.0
        pd.update(
            {
                "inventory": {tier.item_full: 1},
                "current_ore": "copper",
                "carried_inventory": {"copper": {tier.item_full: 1}},
            }
        )
        teleports: list[str] = []

        def _teleport(urn_id: str) -> bool:
            updated, _xp, ok, _skill_id = teleport_full_urn_pure(pd, urn_id)
            if ok:
                updated["mining_exp"] = tier.teleport_xp
                updated["mining_level"] = 2
                pd.clear()
                pd.update(updated)
                teleports.append(urn_id)
            return ok

        dialog = self._open(
            pd,
            current_skill="Mining",
            carried_pack_target_active=True,
            carried_advanced_state=True,
            on_set_carried_advanced=lambda _enabled: None,
            on_set_carried_layout_quantity=lambda _name, _quantity: True,
            on_teleport_training_urn=_teleport,
            on_discard_item=lambda _item, _quantity: True,
        )
        bank = _find_bank_list(dialog)
        row = next(
            bank.item(i)
            for i in range(bank.count())
            if bank.item(i).data(Qt.ItemDataRole.UserRole) == tier.item_full
        )
        self.assertEqual(row.data(Qt.ItemDataRole.UserRole + 1), tier.id)
        self.assertIn(f"{tier.teleport_xp:g} Mining XP", row.toolTip())
        self.assertIn("Ready in the carried pack", row.toolTip())
        self.assertEqual(_panel_title(dialog), "Mining — Lv 1")

        menu = dialog._ankiscape_equip_menu_for(tier.item_full)
        actions = [action for action in menu.actions() if not action.isSeparator()]
        self.assertEqual(
            [action.text() for action in actions],
            ["Teleport urn", "Set carried quantity…", "Discard X…"],
        )
        teleport = actions[0]
        self.assertEqual(teleport.objectName(), "teleportTrainingUrnAction")
        self.assertEqual(teleport.data(), tier.id)
        self.assertTrue(teleport.isEnabled())
        teleport.trigger()
        for _ in range(4):
            QApplication.processEvents()

        self.assertEqual(teleports, [tier.id])
        self.assertEqual(pd["mining_level"], 2)
        self.assertEqual(_panel_title(dialog), "Mining — Lv 2")
        self.assertFalse(
            any(
                bank.item(i).data(Qt.ItemDataRole.UserRole) == tier.item_full
                for i in range(bank.count())
            )
        )
        dialog.deleteLater()

    def test_urn_teleport_eligibility_and_passives_stay_non_equipment(self) -> None:
        from ankiscape.data.urn_data import URN_TIERS_BY_ID

        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        pd = _make_player_data()
        pd.update(
            {
                "inventory": {
                    tier.item_full: 1,
                    tier.item_r: 1,
                    "Bonecrusher": 1,
                    "Ectoplasmator": 1,
                },
                "current_ore": "copper",
                "carried_inventory": {"tin": {tier.item_full: 1}},
            }
        )
        dialog = self._open(
            pd,
            current_skill="Mining",
            on_teleport_training_urn=lambda _urn_id: True,
            on_discard_item=lambda _item, _quantity: True,
        )
        full_menu = dialog._ankiscape_equip_menu_for(tier.item_full)
        teleport = next(action for action in full_menu.actions() if action.text() == "Teleport urn")
        self.assertFalse(teleport.isEnabled())
        self.assertIn("current Mining target", teleport.toolTip())

        runed_menu = dialog._ankiscape_equip_menu_for(tier.item_r)
        self.assertNotIn("Teleport urn", [action.text() for action in runed_menu.actions()])

        bank = _find_bank_list(dialog)
        for passive in ("Bonecrusher", "Ectoplasmator"):
            row = next(
                bank.item(i)
                for i in range(bank.count())
                if bank.item(i).data(Qt.ItemDataRole.UserRole) == passive
            )
            self.assertFalse(row.icon().isNull(), f"{passive} row has no icon")
            menu = dialog._ankiscape_equip_menu_for(passive)
            self.assertFalse(any(action.text().startswith("Equip") for action in menu.actions()))
        dialog.deleteLater()

    def test_bank_groups_food_with_icons_and_discard_x_prompt(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Shrimps": 3}
        discards: list[tuple[str, int]] = []

        def _discard(item_name: str, quantity: int) -> bool:
            discards.append((item_name, quantity))
            pd["inventory"][item_name] -= quantity
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
        self.assertEqual(action.text(), "Discard X…")
        self.assertTrue(action.isEnabled())

        original_get_int = self._ui.QInputDialog.getInt
        self._ui.QInputDialog.getInt = lambda *a, **k: (2, True)
        try:
            action.trigger()
            QApplication.processEvents()
        finally:
            self._ui.QInputDialog.getInt = original_get_int
        self.assertEqual(discards, [("Shrimps", 2)])
        self.assertEqual(pd["inventory"]["Shrimps"], 1)

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
        from ankiscape.logic_pure.logic_pure import equip_item_pure, unequip_item_pure
        from ankiscape.core.constants import EQUIPMENT_ITEM_DATA

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
        from ankiscape.core.constants import EQUIPMENT_SLOTS

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
        from ankiscape.ui import ui as _ui
        if _ui.equipment_slot_icon_path("head"):
            head_row = _equip_slot_row(equip_list, "head")
            self.assertFalse(head_row.icon().isNull(), "head slot has no placeholder icon")

    def test_empty_slot_text_is_dark_mode_safe_not_palette_mid(self) -> None:
        # Regression guard for the recurring "greyed text vanishes in dark mode"
        # bug: empty-slot labels must use the dim-text helper (derived from the
        # readable Text role with reduced alpha), never QPalette.Mid (a border
        # role that renders near-black on a dark base).
        from ankiscape.ui import ui as _ui
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

    def test_equipping_and_removing_capacitor_refreshes_borrowed_power_row(self) -> None:
        from ankiscape.data.livid_farm_data import ARCANE_CAPACITOR_CHARGED

        pd = _make_player_data()
        pd.update(
            {
                "combat_attack_style": "magic_standard",
                "magic_level": 99,
                "inventory": {ARCANE_CAPACITOR_CHARGED: 1},
                "equipment": {"weapon": "Staff of air"},
                "livid_farm": {
                    "borrowed_power_claimed": True,
                    "arcane_capacitor_spell": "wind_wave",
                    "arcane_capacitor_charges": 12,
                },
            }
        )
        dialog = self._open_with_equip(pd)
        _open_equipment_tab(dialog)
        dialog.show()
        QApplication.processEvents()
        row = dialog.findChild(QWidget, "combatBorrowedPowerRow")
        self.assertFalse(row.isVisible())

        equip_menu = dialog._ankiscape_equip_menu_for(
            ARCANE_CAPACITOR_CHARGED
        )
        equip_menu.actions()[0].trigger()
        QApplication.processEvents()

        self.assertTrue(row.isVisible())
        self.assertIn("12 charges", row.findChild(QLabel).text())

        unequip_menu = dialog._ankiscape_unequip_menu_for("neck")
        self.assertIsNotNone(unequip_menu)
        unequip_menu.actions()[0].trigger()
        QApplication.processEvents()
        self.assertFalse(row.isVisible())

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
        from ankiscape.core.constants import EQUIPMENT_ITEM_DATA

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
        self.assertTrue(
            hud.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        )
        hud.set_data(_make_player_data(), "Fletching")
        self.assertTrue(
            hud.title_lbl.text().startswith("Fletching"),
            f"HUD did not recognize Fletching; shows {hud.title_lbl.text()!r}",
        )
        self.assertFalse(hud.icon_lbl.pixmap().isNull(), "HUD has no Fletching icon")

    def test_hud_recognizes_targeted_skills(self) -> None:
        cases = (
            ("Firemaking", "current_firemaking", "logs", "Logs"),
            ("Fishing", "current_fishing", "catch_crayfish", "Catch crayfish"),
            ("Cooking", "current_cooking", "cook_shrimps", "Cook raw shrimps"),
        )
        for skill, target_key, target_id, target_label in cases:
            with self.subTest(skill):
                pd = _make_player_data()
                pd[target_key] = target_id
                hud = self._ui.ReviewHUD(None)
                hud.set_data(pd, skill)
                self.assertTrue(
                    hud.title_lbl.text().startswith(skill),
                    f"HUD did not recognize {skill}; shows {hud.title_lbl.text()!r}",
                )
                self.assertEqual(hud.target_lbl.text(), target_label)
                self.assertFalse(hud.icon_lbl.pixmap().isNull(), f"HUD has no {skill} icon")

    # ---- Crafting/Utility rework surfaces ---------------------------------
    def _open_no_xp_surface(
        self, dialog: "QDialog", surface_name: str
    ) -> "QTreeWidget":
        cat = next(
            b for b in dialog.findChildren(QPushButton) if b.text() == surface_name
        )
        cat.click()
        QApplication.processEvents()
        expected_target = (
            "livid_farm" if surface_name == "Activities" else "make_soft_clay"
        )
        for tree in dialog.findChildren(QTreeWidget):
            if any(
                item.data(0, Qt.ItemDataRole.UserRole) == expected_target
                for item in _tree_items(tree)
            ):
                return tree
        raise AssertionError(
            f"{surface_name} tree with {expected_target!r} was not found"
        )

    def _open_utility(self, dialog: "QDialog") -> "QTreeWidget":
        return self._open_no_xp_surface(dialog, "Utilities")

    def _open_activities(self, dialog: "QDialog") -> "QTreeWidget":
        return self._open_no_xp_surface(dialog, "Activities")

    def test_soft_clay_left_crafting_and_is_now_a_utility_activity(self) -> None:
        # Open Crafting target tree and assert Soft clay is no longer a target.
        tree = _goto_crafting(self.dialog)
        craft_texts = [it.text(0) for it in _tree_items(tree)]
        self.assertFalse(
            any(t.startswith("Soft clay") for t in craft_texts),
            f"Soft clay should not be a Crafting target anymore: {craft_texts}",
        )
        # And it now lives under Utilities, not Activities.
        utility_tree = self._open_utility(self.dialog)
        skill_column_label = _find_named_widget(
            self.dialog, "skillColumnLabel"
        )
        self.assertEqual(skill_column_label.text(), "Selection")
        skill_list = _find_named_widget(self.dialog, "skillListWidget")
        utility_icon = skill_list.item(0).icon()
        util_texts = [it.text(0) for it in _tree_items(utility_tree)]
        self.assertIn("Make soft clay", util_texts)
        self.assertIn("Gather wool", util_texts)
        self.assertIn("Gather grain", util_texts)
        self.assertIn("Make bread dough", util_texts)
        self.assertIn("Bankstanding", util_texts)
        economy = next(
            item
            for item in _tree_items(utility_tree)
            if item.data(0, Qt.ItemDataRole.UserRole)
            == "__utility_group__:economy"
        )
        self.assertIn(
            "Bankstanding",
            [economy.child(index).text(0) for index in range(economy.childCount())],
        )
        # Retired 2026-07-06: outputs are live NPC shop stock now.
        self.assertNotIn("Scavenge chicken feathers", util_texts)
        self.assertNotIn("Gather fishing bait", util_texts)
        self.assertNotIn("Buy Hunter supplies", util_texts)
        activities_tree = self._open_activities(self.dialog)
        activity_icon = skill_list.item(0).icon()
        self.assertFalse(utility_icon.isNull())
        self.assertFalse(activity_icon.isNull())
        self.assertNotEqual(utility_icon.cacheKey(), activity_icon.cacheKey())
        activity_texts = [it.text(0) for it in _tree_items(activities_tree)]
        self.assertNotIn("Make soft clay", activity_texts)
        self.assertIn("Livid Farm", activity_texts)
        # Group headers carry their activity count, like every other hub tree.
        self.assertTrue(
            any(t.startswith("Minigames  (") for t in activity_texts),
            activity_texts,
        )
        self.assertTrue(
            any(
                t.startswith("Distractions and Diversions  (")
                for t in activity_texts
            ),
            activity_texts,
        )
        self.assertNotIn("Activities / minigames  (2)", activity_texts)
        minigames = _utility_row(
            activities_tree, "__utility_group__:minigames"
        )
        dnds = _utility_row(
            activities_tree,
            "__utility_group__:distractions_and_diversions",
        )
        self.assertFalse(minigames.icon(0).isNull())
        self.assertFalse(dnds.icon(0).isNull())
        self.assertNotEqual(
            _icon_pixels(minigames.icon(0)),
            _icon_pixels(dnds.icon(0)),
        )
        self.assertEqual(
            {
                minigames.child(index).data(
                    0, Qt.ItemDataRole.UserRole
                )
                for index in range(minigames.childCount())
            },
            {
                "fist_of_guthix",
                "sorceress_garden",
                "livid_farm",
                "vinesweeper",
                "fight_caves",
                "stealing_creation",
                "barrows",
                "flash_powder_factory",
                "pyramid_plunder",
                "werewolf_skullball",
                "gnome_ball",
                "fishing_trawler",
                "great_orb_project",
                "trouble_brewing",
                "castle_wars",
                "pest_control",
                "barbarian_assault",
                "soul_wars",
                "shades_of_mortton",
                "tzhaar_fight_pit",
                "duel_arena",
                "clan_wars",
                "crucible",
            },
        )
        self.assertEqual(
            {
                dnds.child(index).data(0, Qt.ItemDataRole.UserRole)
                for index in range(dnds.childCount())
            },
            {
                "big_chinchompa",
                "familiarisation",
                "penguin_hide_and_seek",
                "shooting_stars",
                "court_cases",
                "big_top_bonanza",
                "fish_flingers",
                "phoenix_lair",
                "skeletal_horror",
                "tears_of_guthix",
                "enchanted_key",
                "goblin_raids",
                "troll_invasion",
                "shattered_heart",
                "treasure_trail",
            },
        )
        self.assertTrue(
            any(text.startswith("Warriors' Guild") for text in activity_texts)
        )

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
        pd["inventory"] = {"Gold bar": 5, "Ring mould": 1}
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
        pd["inventory"] = {"Gold bar": 5, "Ring mould": 1}
        pd["crafting_level"] = 99
        pd["current_craft"] = "jewellery_gold_ring"
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        current = tree.currentItem()
        self.assertIsNotNone(current)
        self.assertEqual(current.data(0, Qt.ItemDataRole.UserRole), "jewellery_gold_ring")
        self.assertEqual(
            current.background(0).color(),
            QColor(76, 175, 80, 76),
        )
        # The family holding the current target opens so the selection is visible.
        self.assertTrue(_craft_family_node(tree, "jewellery").isExpanded())
        # Unrelated families stay collapsed to tame the panel.
        self.assertFalse(_craft_family_node(tree, "gems").isExpanded())

    def test_activities_panel_describes_rewards_and_no_xp_rows_truthfully(self) -> None:
        utility_tree = self._open_activities(self.dialog)
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn(
            "Activities contain D&Ds, minigames, and landmarks. Each row states its rewards.",
            labels,
        )
        livid_row = _utility_row(utility_tree, "livid_farm")
        self.assertIn(
            "exactly six cycles per five successful reviews",
            livid_row.toolTip(0),
        )
        selected_colors = re.findall(
            r"QTreeWidget::(?:item|branch):selected \{ background: (#[0-9a-f]{6});",
            utility_tree.styleSheet(),
        )
        self.assertEqual(len(selected_colors), 2)
        self.assertEqual(selected_colors[0], selected_colors[1])

    def test_live_theme_controls_use_palette_text_and_style_the_review_link(self) -> None:
        utility_button = next(
            button
            for button in self.dialog.findChildren(QPushButton)
            if button.text() == "Utilities"
        )
        utility_button.click()
        QApplication.processEvents()
        self.assertIn("color: palette(text)", utility_button.styleSheet())

        stop_button = next(
            button
            for button in self.dialog.findChildren(QPushButton)
            if button.text() == "Stop training"
        )
        self.assertIn("color: palette(text)", stop_button.styleSheet())

        review_link = next(
            label
            for label in self.dialog.findChildren(QLabel)
            if "ankiweb.net/shared/review" in label.text()
        )
        self.assertIn('style="color:#4CAF50;', review_link.text())

    def test_bankstanding_describes_an_idle_no_op_without_fake_output(self) -> None:
        pd = _make_player_data()
        pd["current_utility"] = "bankstanding"
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)

        row = _utility_row(utility_tree, "bankstanding")
        self.assertIn("Nothing is produced or consumed", row.toolTip(0))
        self.assertNotIn("Output: Bankstanding", row.toolTip(0))

        hud = self._ui.ReviewHUD(None)
        hud.set_data(pd, "Utility / Activities")
        self.assertIn("idle at the Bank", hud.sub_lbl.text())
        self.assertNotIn("material prep", hud.sub_lbl.text())

    def test_evil_tree_panel_reports_countdown_and_selects_active_event(self) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        pd = _make_player_data()
        pd["shop_market_clock"] = {"answered_cards": 0}
        pd["evil_tree"] = default_evil_tree_state_pure()
        countdown_dialog = self._open(pd)
        self._open_activities(countdown_dialog)
        self.assertEqual(
            _find_named_label(countdown_dialog, "evilTreeStatusChip").text(),
            "Next in 20 reviews",
        )
        self.assertFalse(
            _find_named_button(
                countdown_dialog, "evilTreeSelectButton"
            ).isEnabled()
        )
        due = copy.deepcopy(pd)
        due["shop_market_clock"]["answered_cards"] = 100
        due_dialog = self._open(due)
        self._open_activities(due_dialog)
        self.assertEqual(
            _find_named_label(due_dialog, "evilTreeStatusChip").text(),
            "Next review",
        )

        pd["shop_market_clock"]["answered_cards"] = 20
        active, _ = advance_evil_tree_world_clock_pure(pd)
        pd.clear()
        pd.update(active)
        active_dialog = self._open(pd)
        utility_tree = self._open_activities(active_dialog)
        button = _find_named_button(active_dialog, "evilTreeSelectButton")
        self.assertEqual(button.text(), "Select full event")
        self.assertTrue(button.isEnabled())
        self.assertIn(
            "Nurture → Prepare → Fell",
            _find_named_label(active_dialog, "evilTreeDetail").text(),
        )

        button.click()
        QApplication.processEvents()
        self.assertEqual(self._utility_calls[-1], "evil_tree")
        self.assertEqual(pd["current_utility"], "evil_tree")
        self.assertEqual(button.text(), "Selected for reviews")
        self.assertFalse(button.isEnabled())
        utility_tree = self._open_utility(active_dialog)
        bankstanding = _utility_row(utility_tree, "bankstanding")
        utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "bankstanding")
        self._open_activities(active_dialog)
        button = _find_named_button(active_dialog, "evilTreeSelectButton")
        self.assertEqual(button.text(), "Select full event")
        self.assertTrue(button.isEnabled())

    def test_evil_tree_panel_makes_nurture_only_gate_explicit(self) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "woodcutting_level": 1,
                "firemaking_level": 1,
                "farming_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "evil_tree": default_evil_tree_state_pure(),
            }
        )
        active, _ = advance_evil_tree_world_clock_pure(
            pd, tier_roll=0.8, location_roll=0.0
        )
        pd.clear()
        pd.update(active)
        dialog = self._open(pd)
        self._open_activities(dialog)

        button = _find_named_button(dialog, "evilTreeSelectButton")
        detail = _find_named_label(dialog, "evilTreeDetail").text()
        self.assertEqual(button.text(), "Select nurture only")
        self.assertTrue(button.isEnabled())
        self.assertIn("cannot fell", detail)
        self.assertIn("75 Woodcutting", detail)
        self.assertIn("75 Firemaking", detail)

    def test_evil_tree_panel_disables_daily_limit_with_reason(self) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "shop_market_clock": {"answered_cards": 20},
                "evil_tree": default_evil_tree_state_pure(),
            }
        )
        active, _ = advance_evil_tree_world_clock_pure(pd)
        active["evil_tree"]["participations_today"] = 2
        dialog = self._open(active)
        self._open_activities(dialog)

        button = _find_named_button(dialog, "evilTreeSelectButton")
        self.assertEqual(button.text(), "Unavailable")
        self.assertFalse(button.isEnabled())
        self.assertIn(
            "Two Evil Tree interactions used this review day",
            _find_named_label(dialog, "evilTreeDetail").text(),
        )

    def test_activities_world_events_strip_summarizes_evil_tree_and_star(
        self,
    ) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "evil_tree": default_evil_tree_state_pure(),
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_evil_tree_world_clock_pure(pd)
        active["evil_tree"]["blessing_reviews_remaining"] = 2
        active["evil_tree"]["blessing_tier"] = "normal"
        active, _ = advance_shooting_star_world_clock_pure(active)
        dialog = self._open(active)
        activity_tree = self._open_activities(dialog)

        strip = _find_named_widget(dialog, "activityWorldEventsStrip")
        body = _find_named_label(dialog, "activityWorldEventsBody")
        self.assertTrue(strip.isVisibleTo(dialog))
        self.assertIn("evil tree", body.text().lower())
        self.assertIn("Evil Tree blessing · 2 reviews left", body.text())
        self.assertIn("Shooting Star size", body.text())

        # Opening a card suppresses that card's own row, so the strip never
        # duplicates the detail already on screen.
        star_row = _utility_row(activity_tree, "shooting_stars")
        activity_tree.itemActivated.emit(star_row, 0)
        QApplication.processEvents()
        self.assertNotIn("Shooting Star size", body.text())
        self.assertIn("evil tree", body.text().lower())
        self.assertIn("Evil Tree blessing · 2 reviews left", body.text())

    def test_activities_world_events_strip_hidden_when_no_event(self) -> None:
        dialog = self._open(_make_player_data())
        self._open_activities(dialog)

        strip = _find_named_widget(dialog, "activityWorldEventsStrip")
        self.assertFalse(strip.isVisibleTo(dialog))

    def test_review_hud_omits_evil_tree_world_notices(self) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "evil_tree",
                "shop_market_clock": {"answered_cards": 20},
                "evil_tree": default_evil_tree_state_pure(),
            }
        )
        active, _ = advance_evil_tree_world_clock_pure(pd)
        active["evil_tree"]["blessing_reviews_remaining"] = 2
        active["evil_tree"]["blessing_tier"] = "normal"
        hud = self._ui.ReviewHUD(None)

        hud.set_data(active, "Utility / Activities")

        notice = hud.findChild(QLabel, "reviewWorldNotice")
        self.assertFalse(notice.isVisible())
        self.assertNotIn("evil tree", notice.text())
        self.assertNotIn("Evil Tree blessing", notice.text())
        # The projection itself must survive: the subtitle branch reads it.
        self.assertIn("Nurture phase", hud.sub_lbl.text())

        active["evil_tree"]["active_event"] = {}
        active["evil_tree"]["session"] = {}
        hud.set_data(active, "Utility / Activities")
        self.assertIn("awaiting an active tree", hud.sub_lbl.text())

    def test_big_chinchompa_panel_selects_event_and_runs_reward_shop(self) -> None:
        from ankiscape.logic.big_chinchompa_logic import (
            advance_big_chinchompa_world_clock_pure,
            default_big_chinchompa_state_pure,
        )
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "hunter_level": 99,
                "shop_market_clock": {"answered_cards": 60},
                "big_chinchompa": default_big_chinchompa_state_pure(),
                "evil_tree": default_evil_tree_state_pure(),
            }
        )
        pd["big_chinchompa"]["competence_points"] = 100
        active, _ = advance_evil_tree_world_clock_pure(pd)
        active, _ = advance_big_chinchompa_world_clock_pure(active)
        pd.clear()
        pd.update(active)
        dialog = self._open(pd)
        utility_tree = self._open_activities(dialog)

        status = _find_named_label(dialog, "bigChinchompaStatusChip")
        button = _find_named_button(dialog, "bigChinchompaSelectButton")
        fullness = _find_named_widget(dialog, "bigChinchompaFullness")
        self.assertIn("source min left", status.text())
        self.assertEqual(button.text(), "Select active event")
        self.assertFalse(fullness.isHidden())

        button.click()
        QApplication.processEvents()
        self.assertEqual(self._utility_calls[-1], "big_chinchompa")
        self.assertEqual(pd["current_utility"], "big_chinchompa")
        self.assertEqual(button.text(), "Selected for reviews")

        evil_button = _find_named_button(dialog, "evilTreeSelectButton")
        self.assertTrue(evil_button.isEnabled())
        evil_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "evil_tree")
        self.assertEqual(button.text(), "Select active event")
        self.assertTrue(button.isEnabled())

        button.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "big_chinchompa")

        self.assertIsNone(
            dialog.findChild(QComboBox, "bigChinchompaPopulationProfile")
        )

        buy = _find_named_button(dialog, "bigChinchompaRewardBuyButton")
        self.assertTrue(buy.isEnabled())
        self.assertIn("4 Competence", buy.toolTip())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Swamp lizard quota ticket"], 1)
        self.assertEqual(pd["big_chinchompa"]["competence_points"], 96)

        utility_tree = self._open_utility(dialog)
        bankstanding = _utility_row(utility_tree, "bankstanding")
        utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self._open_activities(dialog)
        button = _find_named_button(dialog, "bigChinchompaSelectButton")
        self.assertEqual(button.text(), "Select active event")

    def test_activity_details_replace_the_activity_tree(self) -> None:
        from ankiscape.logic.big_chinchompa_logic import (
            advance_big_chinchompa_world_clock_pure,
            default_big_chinchompa_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "hunter_level": 99,
                "current_utility": "big_chinchompa",
                "shop_market_clock": {"answered_cards": 60},
                "big_chinchompa": default_big_chinchompa_state_pure(),
            }
        )
        pd, _ = advance_big_chinchompa_world_clock_pure(pd)
        dialog = self._open(pd)
        self._open_activities(dialog)
        dialog.resize(1000, 560)
        dialog.show()
        for _ in range(8):
            QApplication.processEvents()

        details_stack = _find_named_widget(
            dialog, "utilityActivityDetailsStack"
        )
        activity_tree = _find_named_widget(dialog, "utilityActivityTree")
        choose_another = _find_named_button(
            dialog, "activityChooseAnotherButton"
        )
        big_panel = _find_named_widget(dialog, "bigChinchompaPanel")
        self.assertIsInstance(details_stack, QStackedWidget)
        self.assertEqual(details_stack.currentWidget(), big_panel)
        self.assertTrue(details_stack.isVisible())
        self.assertTrue(choose_another.isVisible())
        self.assertFalse(activity_tree.isVisible())
        self.assertGreaterEqual(activity_tree.minimumHeight(), 140)
        surface_layout = activity_tree.parentWidget().layout()
        self.assertLess(
            surface_layout.indexOf(details_stack),
            surface_layout.indexOf(activity_tree),
        )
        visible_rows = [
            child
            for child in big_panel.findChildren(
                QWidget,
                options=Qt.FindChildOption.FindDirectChildrenOnly,
            )
            if child.isVisible()
        ]
        self.assertTrue(visible_rows)
        self.assertLessEqual(
            max(child.geometry().bottom() for child in visible_rows),
            big_panel.contentsRect().bottom(),
        )

        original_height = details_stack.height()
        big_detail = _find_named_label(dialog, "bigChinchompaDetail")
        big_detail.setMinimumHeight(big_detail.sizeHint().height() + 40)
        reward_combo = dialog.findChild(
            QComboBox, "bigChinchompaRewardCombo"
        )
        reward_combo.setCurrentIndex(1)
        QApplication.processEvents()
        self.assertGreater(details_stack.height(), original_height)

        choose_another.click()
        QApplication.processEvents()
        self.assertFalse(details_stack.isVisible())
        self.assertFalse(choose_another.isVisible())
        self.assertTrue(activity_tree.isVisible())

    def test_activity_picker_scrolls_and_remembers_collapsed_groups(self) -> None:
        # The picker used to page one category at a time with a fixed height,
        # which pushed long categories off-window. It now scrolls like every
        # other grouped tree in the hub and persists per-category collapses.
        from ankiscape.ui import ui

        class _FakeCol:
            def __init__(self) -> None:
                self._cfg: dict = {}

            def get_config(self, key, default=None):
                return self._cfg.get(key, default)

            def set_config(self, key, value):
                self._cfg[key] = value

        class _FakeMw(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.col = _FakeCol()

        orig_mw = ui.mw
        ui.mw = _FakeMw()
        try:
            pd = _make_player_data()
            pd["current_utility"] = "fist_of_guthix"
            dialog = self._open(pd)
            activity_tree = self._open_activities(dialog)
            dialog.show()
            dialog.resize(900, 560)
            for _ in range(8):
                QApplication.processEvents()

            _find_named_button(dialog, "activityChooseAnotherButton").click()
            for _ in range(8):
                QApplication.processEvents()

            top_levels = [
                activity_tree.topLevelItem(index)
                for index in range(activity_tree.topLevelItemCount())
            ]
            self.assertEqual(len(top_levels), 4)
            self.assertFalse([item for item in top_levels if item.isHidden()])

            # Scrolling, not a fixed height: the tree keeps Qt's default max
            # height and grows a scrollbar instead of the dialog.
            self.assertEqual(
                activity_tree.verticalScrollBarPolicy(),
                Qt.ScrollBarPolicy.ScrollBarAsNeeded,
            )
            self.assertGreater(
                activity_tree.maximumHeight(), activity_tree.minimumHeight()
            )
            self.assertGreater(
                activity_tree.verticalScrollBar().maximum(), 0
            )
            tree_bottom = activity_tree.mapTo(
                dialog, activity_tree.rect().bottomRight()
            ).y()
            self.assertLessEqual(tree_bottom, dialog.contentsRect().bottom())

            current = activity_tree.currentItem()
            self.assertEqual(
                current.data(0, Qt.ItemDataRole.UserRole), "fist_of_guthix"
            )
            self.assertTrue(
                activity_tree.viewport().rect().contains(
                    activity_tree.visualItemRect(current).center()
                )
            )

            by_group = {
                item.data(0, Qt.ItemDataRole.UserRole): item
                for item in top_levels
            }
            for group in ("minigames", "distractions_and_diversions"):
                header = by_group[f"__utility_group__:{group}"]
                header.setExpanded(False)
                QApplication.processEvents()
                # The old pager re-expanded the visible category on collapse.
                self.assertFalse(header.isExpanded())
            self.assertEqual(
                ui.mw.col.get_config("ankiscape_activity_collapsed_groups"),
                ["distractions_and_diversions", "minigames"],
            )

            dialog2 = self._open(pd)
            tree2 = self._open_activities(dialog2)
            expanded = {
                item.data(0, Qt.ItemDataRole.UserRole): item.isExpanded()
                for item in (
                    tree2.topLevelItem(index)
                    for index in range(tree2.topLevelItemCount())
                )
            }
            self.assertFalse(
                expanded["__utility_group__:distractions_and_diversions"]
            )
            self.assertTrue(expanded["__utility_group__:warriors_guild"])
            self.assertTrue(expanded["__utility_group__:landmarks"])
            # Minigames holds the current activity, so the selection wins over
            # the remembered collapse and the active row stays reachable.
            self.assertTrue(expanded["__utility_group__:minigames"])
        finally:
            ui.mw = orig_mw

    def test_shooting_star_panel_selects_and_exchanges_without_spawn_controls(self) -> None:
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_shooting_star_world_clock_pure(pd)
        pd.clear()
        pd.update(active)
        dialog = self._open(pd)
        self._open_activities(dialog)

        status = _find_named_label(dialog, "shootingStarStatusChip")
        select = _find_named_button(dialog, "shootingStarSelectButton")
        self.assertTrue(status.text().startswith("Size "))
        self.assertEqual(select.text(), "Select active star")
        self.assertTrue(select.isEnabled())

        select.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "shooting_stars")
        self.assertEqual(self._utility_calls[-1], "shooting_stars")
        self.assertEqual(select.text(), "Selected for reviews")

        for object_name in (
            "shootingStarAutomationMode",
            "shootingStarMinimumSize",
            "shootingStarMaximumSize",
            "shootingStarPopulationProfile",
        ):
            self.assertIsNone(dialog.findChild(QComboBox, object_name))

        event = pd["shooting_star"]["active_event"]
        event.update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_card": 22,
            }
        )
        pd["inventory"]["Stardust"] = 200
        reward_dialog = self._open(pd)
        self._open_activities(reward_dialog)
        exchange = _find_named_button(
            reward_dialog, "shootingStarExchangeButton"
        )
        self.assertTrue(exchange.isEnabled())
        exchange.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Cosmic rune"], 152)
        self.assertEqual(pd["inventory"]["Astral rune"], 52)
        self.assertEqual(pd["inventory"]["Gold ore"], 20)
        self.assertEqual(pd["inventory"]["Coins"], 50_002)
        self.assertEqual(pd["inventory"]["Stardust"], 0)
        self.assertEqual(
            pd["shooting_star"]["ore_bonus_ticks_remaining"], 1_500
        )

    def test_fist_of_guthix_card_tutorial_policy_live_state_and_shop(self) -> None:
        from ankiscape.logic.fist_of_guthix_logic import (
            default_fist_of_guthix_state_pure,
            start_fist_of_guthix_match_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "fist_of_guthix": default_fist_of_guthix_state_pure(),
                "equipment_instances": {},
                "equipment_instance_next_id": 1,
            }
        )
        pd["fist_of_guthix"]["tokens"] = 100
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        fog_row = _utility_row(activity_tree, "fist_of_guthix")
        activity_tree.setCurrentItem(fog_row)
        activity_tree.itemActivated.emit(fog_row, 0)
        QApplication.processEvents()

        details = _find_named_widget(dialog, "utilityActivityDetailsStack")
        panel = _find_named_widget(dialog, "fistOfGuthixPanel")
        primary = _find_named_button(dialog, "fistOfGuthixPrimaryButton")
        self.assertEqual(details.currentWidget(), panel)
        self.assertEqual(primary.text(), "Talk to Fiara")
        self.assertFalse(panel.findChild(QProgressBar, "fistOfGuthixChargeProgress").isVisible())

        primary.click()
        QApplication.processEvents()
        self.assertTrue(pd["fist_of_guthix"]["tutorial_complete"])
        self.assertEqual(primary.text(), "Selected for reviews")
        self.assertEqual(pd["current_utility"], "fist_of_guthix")
        self.assertEqual(self._utility_calls[-1], "fist_of_guthix")

        mode = dialog.findChild(QComboBox, "fistOfGuthixAutomationMode")
        stance = dialog.findChild(QComboBox, "fistOfGuthixStance")
        mode.setCurrentIndex(mode.findData("advanced"))
        stance.setCurrentIndex(stance.findData("centre"))
        QApplication.processEvents()
        self.assertEqual(pd["fist_of_guthix"]["automation_mode"], "advanced")
        self.assertEqual(pd["fist_of_guthix"]["selected_stance"], "centre")

        shop_toggle = dialog.findChild(QToolButton, "fistOfGuthixShopToggle")
        shop_toggle.click()
        QApplication.processEvents()
        shop = _find_named_widget(dialog, "fistOfGuthixShop")
        self.assertFalse(shop.isHidden())
        buy = _find_named_button(dialog, "fistOfGuthixBuyButton")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Combat hood 100"], 1)

        active, ok, _ = start_fist_of_guthix_match_pure(
            pd, iter((0.3, 0.5, 0.2, 0.8, 0.1)).__next__
        )
        self.assertTrue(ok)
        match = active["fist_of_guthix"]["active_match"]
        match["first_player_role"] = "hunted"
        match["player_role"] = "hunted"
        match["player_stance"] = "centre"
        match["player_charges"] = 1_240
        pd.clear()
        pd.update(active)
        live_dialog = self._open(pd)
        live_tree = self._open_activities(live_dialog)
        live_fog_row = _utility_row(live_tree, "fist_of_guthix")
        live_tree.setCurrentItem(live_fog_row)
        live_tree.itemActivated.emit(live_fog_row, 0)
        QApplication.processEvents()
        status = _find_named_label(live_dialog, "fistOfGuthixStatusChip")
        charge = live_dialog.findChild(
            QProgressBar, "fistOfGuthixChargeProgress"
        )
        self.assertEqual(status.text(), "HUNTED · ROUND 1/2")
        self.assertFalse(charge.isHidden())
        self.assertEqual(charge.value(), 1_240)
        self.assertIsNone(panel.findChild(QScrollArea))

    def test_sorceress_garden_card_introduction_gates_and_compact_policies(self) -> None:
        from ankiscape.logic.sorceress_garden_logic import default_sorceress_garden_state_pure

        pd = _make_player_data()
        pd["thieving_level"] = 65
        pd["quests"]["diamond_in_the_rough"]["completed"] = True
        pd["sorceress_garden"] = default_sorceress_garden_state_pure()
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "sorceress_garden")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        details = _find_named_widget(dialog, "utilityActivityDetailsStack")
        panel = _find_named_widget(dialog, "sorceressGardenPanel")
        primary = _find_named_button(dialog, "sorceressGardenPrimaryButton")
        self.assertEqual(details.currentWidget(), panel)
        self.assertEqual(primary.text(), "Talk to Osman")
        self.assertIsNone(panel.findChild(QScrollArea))

        primary.click()
        QApplication.processEvents()
        self.assertTrue(pd["sorceress_garden"]["introduced"])
        season = panel.findChild(QComboBox, "sorceressGardenSeason")
        harvest = panel.findChild(QComboBox, "sorceressGardenHarvest")
        juice = panel.findChild(QComboBox, "sorceressGardenJuice")
        season.setCurrentIndex(season.findData("summer"))
        harvest.setCurrentIndex(harvest.findData("alternate"))
        juice.setCurrentIndex(juice.findData("keep"))
        QApplication.processEvents()
        self.assertEqual(pd["sorceress_garden"]["season_id"], "summer")
        self.assertEqual(pd["sorceress_garden"]["harvest_mode"], "alternate")
        self.assertEqual(pd["sorceress_garden"]["juice_mode"], "keep")

        harvest.setCurrentIndex(harvest.findData("herbs"))
        QApplication.processEvents()
        self.assertFalse(juice.isHidden())
        self.assertFalse(juice.isEnabled())
        harvest.setCurrentIndex(harvest.findData("alternate"))
        QApplication.processEvents()
        self.assertTrue(juice.isEnabled())

        primary.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "sorceress_garden")
        self.assertEqual(self._utility_calls[-1], "sorceress_garden")
        self.assertEqual(primary.text(), "Selected for reviews")

    def test_penguin_card_keeps_bank_only_visibility_ring_locked(self) -> None:
        from ankiscape.logic.penguin_hide_and_seek_logic import default_penguin_state_pure

        pd = _make_player_data()
        pd["shop_market_clock"] = {"answered_cards": 0}
        pd["penguin_hide_and_seek"] = default_penguin_state_pure()
        pd["quests"] = {
            "some_like_it_cold": {"completed": True},
            "desert_treasure": {"started": True},
        }
        pd["inventory"]["Ring of visibility"] = 1

        bank_dialog = self._open(pd)
        bank_tree = self._open_activities(bank_dialog)
        bank_tree.setCurrentItem(
            _utility_row(bank_tree, "penguin_hide_and_seek")
        )
        QApplication.processEvents()
        bank_panel = _find_named_widget(bank_dialog, "penguinHideAndSeekPanel")
        bank_roster = bank_panel.findChild(QComboBox, "penguinHideAndSeekRoster")
        bank_detail = _find_named_label(bank_dialog, "penguinHideAndSeekDetail")
        self.assertEqual(bank_roster.count(), 10)
        self.assertIn("Invisible penguin locked", bank_detail.text())

        pd["carried_inventory"] = {
            "penguin_hide_and_seek": {"Ring of visibility": 1}
        }
        carried_dialog = self._open(pd)
        carried_tree = self._open_activities(carried_dialog)
        carried_tree.setCurrentItem(
            _utility_row(carried_tree, "penguin_hide_and_seek")
        )
        QApplication.processEvents()
        carried_panel = _find_named_widget(
            carried_dialog,
            "penguinHideAndSeekPanel",
        )
        carried_roster = carried_panel.findChild(
            QComboBox,
            "penguinHideAndSeekRoster",
        )
        carried_detail = _find_named_label(
            carried_dialog,
            "penguinHideAndSeekDetail",
        )
        self.assertEqual(carried_roster.count(), 11)
        self.assertIn("Invisible penguin active", carried_detail.text())

        pd["carried_inventory"] = {}
        pd["equipment"]["ring"] = "Ring of visibility"
        equipped_dialog = self._open(pd)
        equipped_tree = self._open_activities(equipped_dialog)
        equipped_tree.setCurrentItem(
            _utility_row(equipped_tree, "penguin_hide_and_seek")
        )
        QApplication.processEvents()
        equipped_panel = _find_named_widget(
            equipped_dialog,
            "penguinHideAndSeekPanel",
        )
        equipped_roster = equipped_panel.findChild(
            QComboBox,
            "penguinHideAndSeekRoster",
        )
        equipped_detail = _find_named_label(
            equipped_dialog,
            "penguinHideAndSeekDetail",
        )
        self.assertEqual(equipped_roster.count(), 11)
        self.assertIn("Invisible penguin active", equipped_detail.text())

    def test_penguin_selection_cancelled_by_activity_conflict_is_not_saved(self) -> None:
        from ankiscape.logic.gnome_ball_logic import enter_gnome_ball_pure

        pd = _make_player_data()
        pd.update({"equipment": {}, "activity_session": {"active_id": ""}})
        pd, ok, _info = enter_gnome_ball_pure(pd)
        self.assertTrue(ok)
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        activity_tree.setCurrentItem(
            _utility_row(activity_tree, "penguin_hide_and_seek")
        )
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "penguinHideAndSeekPanel")
        primary = _find_named_button(dialog, "penguinHideAndSeekPrimaryButton")
        calls_before = len(self._penguin_calls)
        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            primary.click()
        QApplication.processEvents()

        self.assertEqual(len(self._penguin_calls), calls_before)
        self.assertEqual(pd["current_utility"], "gnome_ball")
        self.assertTrue(pd["gnome_ball"])
        self.assertEqual(
            pd.get("penguin_hide_and_seek", {}).get("selected_id", ""),
            "",
        )

    def test_penguin_card_selects_spy_and_redeems_points_without_scroll(self) -> None:
        from ankiscape.logic.penguin_hide_and_seek_logic import default_penguin_state_pure

        pd = _make_player_data()
        pd["shop_market_clock"] = {"answered_cards": 0}
        pd["penguin_hide_and_seek"] = default_penguin_state_pure()
        pd["penguin_hide_and_seek"]["points"] = 2
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        activity_tree.setCurrentItem(
            _utility_row(activity_tree, "penguin_hide_and_seek")
        )
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "penguinHideAndSeekPanel")
        roster = panel.findChild(QComboBox, "penguinHideAndSeekRoster")
        primary = _find_named_button(dialog, "penguinHideAndSeekPrimaryButton")
        redeem_coins = _find_named_button(dialog, "penguinRedeemCoinsButton")
        status = _find_named_label(dialog, "penguinHideAndSeekStatusChip")
        self.assertEqual(roster.count(), 10)
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertEqual(status.toolTip(), "Answered-card week 1")

        selected_id = str(roster.currentData())
        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._penguin_calls[-1],
            ("select_spy", {"spawn_id": selected_id}),
        )
        self.assertEqual(pd["current_utility"], "penguin_hide_and_seek")
        self.assertEqual(self._utility_calls[-1], "penguin_hide_and_seek")
        self.assertEqual(primary.text(), "Selected for next review")
        self.assertEqual(status.text(), "ACTIVE")

        next_index = 1 if roster.currentIndex() == 0 else 0
        next_id = str(roster.itemData(next_index))
        roster.setCurrentIndex(next_index)
        QApplication.processEvents()
        self.assertEqual(str(roster.currentData()), next_id)
        self.assertEqual(primary.text(), "Select for next review")
        self.assertEqual(primary.accessibleName(), primary.text())

        redeem_coins.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Coins"], 13_000)
        self.assertEqual(pd["penguin_hide_and_seek"]["points"], 0)
        self.assertFalse(redeem_coins.isEnabled())
        self.assertTrue(
            panel.findChild(QComboBox, "penguinRewardSkill").isEnabled()
        )
        self.assertNotIn("0 points for 0 coins", redeem_coins.toolTip())

        dialog.resize(900, 560)
        for _ in range(6):
            QApplication.processEvents()
        panel_bottom = panel.mapTo(
            dialog,
            panel.rect().bottomRight(),
        ).y()
        self.assertLessEqual(panel_bottom, dialog.contentsRect().bottom())

    def test_vinesweeper_card_enters_buys_real_rewards_and_redeems_xp(self) -> None:
        from ankiscape.logic.vinesweeper_logic import default_vinesweeper_state_pure

        pd = _make_player_data()
        pd["inventory"]["Spade"] = 1
        pd["farming_level"] = 40
        farming_exp_before = float(pd["farming_exp"])
        pd["vinesweeper"] = default_vinesweeper_state_pure()
        pd["vinesweeper"]["points"] = 200
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        vinesweeper_row = _utility_row(activity_tree, "vinesweeper")
        activity_tree.setCurrentItem(vinesweeper_row)
        activity_tree.itemActivated.emit(vinesweeper_row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "vinesweeperPanel")
        status = _find_named_label(dialog, "vinesweeperStatusChip")
        primary = _find_named_button(dialog, "vinesweeperPrimaryButton")
        reward = panel.findChild(QComboBox, "vinesweeperRewardCombo")
        quantity = panel.findChild(QSpinBox, "vinesweeperRewardQuantity")
        buy = _find_named_button(dialog, "vinesweeperBuyRewardButton")
        redeem = _find_named_button(dialog, "vinesweeperRedeemXpButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertEqual(reward.count(), 46)
        self.assertEqual(reward.accessibleName(), "Vinesweeper reward")
        self.assertEqual(quantity.accessibleName(), "Reward quantity")

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._vinesweeper_calls[-1], ("enter", {}))
        self.assertEqual(pd["current_utility"], "vinesweeper")
        self.assertEqual(self._utility_calls[-1], "vinesweeper")
        self.assertEqual(pd["vinesweeper"]["flags"], 10)
        self.assertEqual(status.text(), "ACTIVE")
        self.assertEqual(primary.accessibleName(), "Leave Winkin's Farm")

        pd["vinesweeper"]["flags"] = 7
        flag_index = reward.findData("flag")
        reward.setCurrentIndex(flag_index)
        quantity.setValue(10)
        QApplication.processEvents()
        self.assertTrue(buy.isEnabled())
        self.assertEqual(buy.text(), "Buy · 150 pt")
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["vinesweeper"]["flags"], 10)
        self.assertEqual(pd["vinesweeper"]["points"], 50)

        cabbage_index = reward.findData("cabbage_seed")
        reward.setCurrentIndex(cabbage_index)
        quantity.setValue(2)
        QApplication.processEvents()
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Cabbage seed"], 2)
        self.assertEqual(pd["vinesweeper"]["points"], 30)

        redeem.click()
        QApplication.processEvents()
        self.assertEqual(pd["vinesweeper"]["points"], 0)
        self.assertEqual(pd["farming_exp"], farming_exp_before + 30.0)
        self.assertFalse(redeem.isEnabled())

    def test_fight_caves_card_enters_targets_and_leaves_without_nested_scroll(self) -> None:
        from ankiscape.logic.fight_caves_logic import default_fight_caves_state_pure

        pd = _make_player_data()
        pd["fight_caves"] = default_fight_caves_state_pure()
        pd["activity_session"] = {"active_id": ""}
        pd["combat_encounter"] = {}
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "fight_caves")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "fightCavesPanel")
        status = _find_named_label(dialog, "fightCavesStatusChip")
        summary = _find_named_label(dialog, "fightCavesSummary")
        telegraph = _find_named_label(dialog, "fightCavesJadTelegraph")
        primary = _find_named_button(dialog, "fightCavesPrimaryButton")
        leave = _find_named_button(dialog, "fightCavesLeaveButton")
        roster = panel.findChild(QListWidget, "fightCavesRoster")
        mode = panel.findChild(QComboBox, "fightCavesModeCombo")
        target = panel.findChild(QComboBox, "fightCavesTargetCombo")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertTrue(telegraph.isHidden())
        self.assertTrue(leave.isHidden())
        self.assertEqual(roster.accessibleName(), "Fight Cave wave roster")
        self.assertEqual(roster.focusPolicy(), Qt.FocusPolicy.TabFocus)

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._fight_caves_calls[-1], ("enter", {}))
        self.assertTrue(pd["fight_caves"]["active"])
        self.assertEqual(pd["current_utility"], "fight_caves")
        self.assertEqual(self._utility_calls[-1], "fight_caves")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertIn("Wave 1/63", summary.text())
        self.assertEqual(roster.count(), 1)
        self.assertIn("Tz-Kih", roster.item(0).text())
        self.assertFalse(leave.isHidden())
        self.assertEqual(leave.text(), "Leave · claim 0 TokKul")

        advanced_index = mode.findData("advanced")
        mode.setCurrentIndex(advanced_index)
        QApplication.processEvents()
        self.assertEqual(
            self._fight_caves_calls[-1],
            ("set_mode", {"automation_mode": "advanced"}),
        )
        self.assertTrue(target.isEnabled())
        self.assertEqual(target.count(), 1)
        self.assertEqual(target.accessibleName(), "Fight Cave engaged target")

        pd["fight_caves"]["wave"] = 59
        pd["fight_caves"]["engaged_instance_id"] = ""
        pd["fight_caves"]["next_instance_id"] = 8
        pd["fight_caves"]["roster"] = []
        for index, enemy_id, lifepoints in (
            (1, "ket_zek", 1600),
            (2, "yt_mejkot", 800),
            (3, "tok_xil", 400),
            (4, "tz_kek_small", 100),
            (5, "tz_kek_small", 100),
            (6, "tz_kek_small", 100),
            (7, "tz_kek_small", 100),
        ):
            pd["fight_caves"]["roster"].append(
                {
                    "instance_id": f"fight-caves-{index}",
                    "enemy_id": enemy_id,
                    "lifepoints": lifepoints,
                    "encounter": {
                        "target_id": "fight_caves",
                        "enemy_lifepoints": lifepoints,
                    },
                    "heal_counter": 0,
                }
            )
        mode.setCurrentIndex(mode.findData("casual"))
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(6):
            QApplication.processEvents()
        self.assertEqual(roster.count(), 7)
        self.assertEqual(roster.verticalScrollBar().maximum(), 0)
        engaged_rows = [
            roster.item(index).text()
            for index in range(roster.count())
            if roster.item(index).text().startswith("▶")
        ]
        self.assertEqual(len(engaged_rows), 1)
        self.assertIn("Tok-Xil", engaged_rows[0])

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertTrue(pd["fight_caves"]["active"])
        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(self._fight_caves_calls[-1], ("leave", {}))
        self.assertFalse(pd["fight_caves"]["active"])
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

        dialog.show()
        dialog.resize(900, 560)
        for _ in range(8):
            QApplication.processEvents()
        choose_another = _find_named_button(
            dialog, "activityChooseAnotherButton"
        )
        self.assertTrue(panel.isVisible())
        self.assertTrue(choose_another.isVisible())
        self.assertFalse(activity_tree.isVisible())
        choose_another.click()
        QApplication.processEvents()
        self.assertFalse(panel.isVisible())
        self.assertFalse(choose_another.isVisible())
        self.assertTrue(activity_tree.isVisible())
        tree_bottom = activity_tree.mapTo(
            dialog, activity_tree.rect().bottomRight()
        ).y()
        self.assertLessEqual(tree_bottom, dialog.contentsRect().bottom())

    def test_phoenix_lair_card_is_compact_period_art_and_abandonment_is_confirmed(self) -> None:
        from ankiscape.logic.phoenix_lair_logic import default_phoenix_lair_state_pure

        pd = _make_player_data()
        pd["phoenix_lair"] = default_phoenix_lair_state_pure()
        pd["activity_session"] = {"active_id": ""}
        pd["combat_encounter"] = {}
        pd["quests"]["in_pyre_need"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["slayer_level"] = 99
        pd["inventory"].update({"Knife": 1, "Secateurs": 1, "Tinderbox": 1})
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "phoenix_lair")
        self.assertFalse(row.icon(0).isNull())
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "phoenixLairPanel")
        icon = panel.findChild(QLabel, "phoenixLairIcon")
        status = _find_named_label(dialog, "phoenixLairStatusChip")
        summary = _find_named_label(dialog, "phoenixLairSummary")
        mechanics = _find_named_label(dialog, "phoenixLairMechanics")
        primary = _find_named_button(dialog, "phoenixLairPrimaryButton")
        leave = _find_named_button(dialog, "phoenixLairLeaveButton")
        progress = panel.findChild(QProgressBar, "phoenixLairProgress")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertIsNotNone(icon.pixmap())
        self.assertFalse(icon.pixmap().isNull())
        self.assertEqual(icon.width(), 28)
        self.assertEqual(status.text(), "READY")
        self.assertIn("non-resumable dangerous PvM", summary.text())
        self.assertIn("Phoenix egg: 1 in 1,000 per completion", summary.text())
        self.assertNotIn("abstraction", summary.text())
        self.assertIn("compressed", mechanics.text())
        self.assertTrue(leave.isHidden())

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._phoenix_lair_calls[-1], ("enter", {}))
        self.assertTrue(pd["phoenix_lair"]["active"])
        self.assertEqual(pd["current_utility"], "phoenix_lair")
        self.assertEqual(status.text(), "GUARDIAN FRONT")
        self.assertTrue(progress.isVisible() or not dialog.isVisible())
        self.assertIn("next attack:", summary.text())
        self.assertFalse(leave.isHidden())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertTrue(pd["phoenix_lair"]["active"])
        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(self._phoenix_lair_calls[-1], ("leave", {}))
        self.assertFalse(pd["phoenix_lair"]["active"])
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

    def test_skeletal_horror_card_unlocks_enters_and_fits_a_dark_laptop_view(self) -> None:
        from ankiscape.logic.skeletal_horror_logic import (
            default_skeletal_horror_state_pure,
        )

        original_palette = QApplication.palette()
        original_style = QApplication.style().objectName()
        dark = QPalette(original_palette)
        dark.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        dark.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
        dark.setColor(QPalette.ColorRole.ButtonText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Mid, QColor(95, 95, 95))
        QApplication.setStyle("Fusion")
        QApplication.setPalette(dark)
        dialog = None
        try:
            pd = _make_player_data()
            pd["skeletal_horror"] = default_skeletal_horror_state_pure()
            pd["activity_session"] = {"active_id": ""}
            pd["combat_encounter"] = {}
            for quest_id in ("rag_and_bone_man", "fur_n_seek"):
                pd["quests"][quest_id] = {
                    "started": True,
                    "progress": 1,
                    "completed": True,
                }
            pd["slayer_level"] = 99
            dialog = self._open(pd)
            dialog.show()
            dialog.resize(900, 560)
            for _ in range(4):
                QApplication.processEvents()

            activity_tree = self._open_activities(dialog)
            row = _utility_row(activity_tree, "skeletal_horror")
            self.assertFalse(row.icon(0).isNull())
            activity_tree.setCurrentItem(row)
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()

            panel = _find_named_widget(dialog, "skeletalHorrorPanel")
            icon = panel.findChild(QLabel, "skeletalHorrorIcon")
            status = _find_named_label(dialog, "skeletalHorrorStatusChip")
            summary = _find_named_label(dialog, "skeletalHorrorSummary")
            rag_wish = _find_named_button(
                dialog, "skeletalHorrorRagWishButton"
            )
            fur_wish = _find_named_button(
                dialog, "skeletalHorrorFurWishButton"
            )
            primary = _find_named_button(
                dialog, "skeletalHorrorPrimaryButton"
            )
            leave = _find_named_button(dialog, "skeletalHorrorLeaveButton")
            progress = panel.findChild(QProgressBar, "skeletalHorrorProgress")
            self.assertIsNone(panel.findChild(QScrollArea))
            self.assertIsNotNone(icon.pixmap())
            self.assertFalse(icon.pixmap().isNull())
            self.assertEqual(status.text(), "LOCKED")
            self.assertIn("wish list", summary.text())
            self.assertTrue(rag_wish.isEnabled())
            self.assertTrue(fur_wish.isEnabled())

            rag_wish.click()
            fur_wish.click()
            QApplication.processEvents()
            self.assertEqual(
                [call[0] for call in self._skeletal_horror_calls[-2:]],
                ["complete_rag_wish_list", "complete_fur_wish_list"],
            )
            self.assertEqual(status.text(), "FIRST FIGHT READY")

            primary.click()
            QApplication.processEvents()
            self.assertEqual(self._skeletal_horror_calls[-1], ("enter", {}))
            self.assertTrue(pd["skeletal_horror"]["active"])
            self.assertEqual(pd["current_utility"], "skeletal_horror")
            self.assertEqual(status.text(), "LEVEL 320")
            self.assertEqual(progress.value(), 3500)
            self.assertFalse(leave.isHidden())
            self.assertLessEqual(
                panel.mapTo(dialog, panel.rect().bottomRight()).y(),
                dialog.contentsRect().bottom(),
            )
        finally:
            if dialog is not None:
                dialog.deleteLater()
            QApplication.setPalette(original_palette)
            QApplication.setStyle(original_style)

    def test_skeletal_horror_wish_list_buttons_follow_the_view_not_a_panel_rule(
        self,
    ) -> None:
        """The panel must render the gate the logic layer owns, never re-derive
        it; a panel-side copy of the Slayer wall drifts without any test
        noticing."""
        from ankiscape.data.skeletal_horror_data import (
            SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL,
        )
        from ankiscape.logic.skeletal_horror_logic import (
            default_skeletal_horror_state_pure,
            skeletal_horror_view_pure,
        )

        dialog = None
        try:
            pd = _make_player_data()
            pd["skeletal_horror"] = default_skeletal_horror_state_pure()
            pd["activity_session"] = {"active_id": ""}
            for quest_id in ("rag_and_bone_man", "fur_n_seek"):
                pd["quests"][quest_id] = {
                    "started": True,
                    "progress": 1,
                    "completed": True,
                }
            pd["slayer_level"] = SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL - 1
            dialog = self._open(pd)
            activity_tree = self._open_activities(dialog)
            row = _utility_row(activity_tree, "skeletal_horror")
            activity_tree.setCurrentItem(row)
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()

            rag_wish = _find_named_button(dialog, "skeletalHorrorRagWishButton")
            fur_wish = _find_named_button(dialog, "skeletalHorrorFurWishButton")
            view = skeletal_horror_view_pure(pd)
            self.assertEqual(rag_wish.isEnabled(), view["rag_wish_list_ready"])
            self.assertEqual(fur_wish.isEnabled(), view["fur_wish_list_ready"])
            self.assertTrue(rag_wish.isEnabled())
            self.assertFalse(fur_wish.isEnabled())
        finally:
            if dialog is not None:
                dialog.deleteLater()

    def test_tears_of_guthix_card_renders_the_view_flags_and_enters(self) -> None:
        """The panel must render the gates the view owns, never re-derive them."""
        from ankiscape.data.tears_of_guthix_data import (
            ORNATE_BOWL_CRAFTING_LEVEL,
            ORNATE_BOWL_MINING_LEVEL,
            ORNATE_BOWL_TOOL,
        )
        from ankiscape.logic.tears_of_guthix_logic import (
            default_tears_of_guthix_state_pure,
            tears_of_guthix_view_pure,
        )

        dialog = None
        try:
            pd = _make_player_data()
            pd["tears_of_guthix"] = default_tears_of_guthix_state_pure()
            pd["activity_session"] = {"active_id": ""}
            pd["quest_points"] = 44
            dialog = self._open(pd)
            activity_tree = self._open_activities(dialog)
            row = _utility_row(activity_tree, "tears_of_guthix")
            self.assertFalse(row.icon(0).isNull())
            activity_tree.setCurrentItem(row)
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()

            panel = _find_named_widget(dialog, "tearsOfGuthixPanel")
            icon = panel.findChild(QLabel, "tearsOfGuthixIcon")
            status = _find_named_label(dialog, "tearsOfGuthixStatusChip")
            summary = _find_named_label(dialog, "tearsOfGuthixSummary")
            ornate = _find_named_button(dialog, "tearsOfGuthixOrnateButton")
            primary = _find_named_button(dialog, "tearsOfGuthixPrimaryButton")
            leave = _find_named_button(dialog, "tearsOfGuthixLeaveButton")
            progress = panel.findChild(QProgressBar, "tearsOfGuthixProgress")

            self.assertIsNotNone(icon.pixmap())
            self.assertFalse(icon.pixmap().isNull())
            self.assertEqual(status.text(), "LOCKED")
            self.assertIn("Tears of Guthix quest", summary.text())
            view = tears_of_guthix_view_pure(pd)
            self.assertEqual(primary.isEnabled(), view["enter_enabled"])
            self.assertEqual(ornate.isEnabled(), view["craft_ornate_enabled"])
            self.assertFalse(primary.isEnabled())
            self.assertTrue(leave.isHidden())
            self.assertTrue(progress.isHidden())

            pd["quests"]["tears_of_guthix"] = {
                "started": True,
                "progress": 3,
                "completed": True,
            }
            pd["mining_level"] = ORNATE_BOWL_MINING_LEVEL
            pd["crafting_level"] = ORNATE_BOWL_CRAFTING_LEVEL
            pd["inventory"][ORNATE_BOWL_TOOL] = 1
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()
            self.assertEqual(status.text(), "FIRST VISIT READY")
            self.assertTrue(primary.isEnabled())
            self.assertTrue(ornate.isEnabled())

            ornate.click()
            QApplication.processEvents()
            self.assertEqual(
                self._tears_of_guthix_calls[-1], ("craft_ornate_bowl", {})
            )
            self.assertTrue(pd["tears_of_guthix"]["ornate_bowl"])
            self.assertTrue(ornate.isHidden())

            primary.click()
            QApplication.processEvents()
            self.assertEqual(self._tears_of_guthix_calls[-1], ("enter", {}))
            self.assertTrue(pd["tears_of_guthix"]["active"])
            self.assertEqual(pd["current_utility"], "tears_of_guthix")
            self.assertEqual(status.text(), "0 TEARS")
            self.assertFalse(progress.isHidden())
            self.assertFalse(leave.isHidden())
        finally:
            if dialog is not None:
                dialog.deleteLater()

    def test_enchanted_key_card_renders_the_view_flags_and_selects_a_site(self) -> None:
        """The panel must render the gates the view owns, never re-derive them."""
        from ankiscape.data.enchanted_key_data import (
            ENCHANTED_KEY_ITEM,
            ENCHANTED_KEY_SITE_IDS,
            ENCHANTED_KEY_SPADE,
        )
        from ankiscape.logic.enchanted_key_logic import (
            default_enchanted_key_state_pure,
            enchanted_key_view_pure,
        )

        dialog = None
        try:
            pd = _make_player_data()
            pd["enchanted_key"] = default_enchanted_key_state_pure()
            pd["activity_session"] = {"active_id": ""}
            dialog = self._open(pd)
            activity_tree = self._open_activities(dialog)
            row = _utility_row(activity_tree, "enchanted_key")
            self.assertFalse(row.icon(0).isNull())
            activity_tree.setCurrentItem(row)
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()

            panel = _find_named_widget(dialog, "enchantedKeyPanel")
            icon = panel.findChild(QLabel, "enchantedKeyIcon")
            status = _find_named_label(dialog, "enchantedKeyStatusChip")
            summary = _find_named_label(dialog, "enchantedKeySummary")
            roster = panel.findChild(QComboBox, "enchantedKeyRoster")
            primary = _find_named_button(dialog, "enchantedKeyPrimaryButton")
            replace = _find_named_button(dialog, "enchantedKeyReplaceButton")

            self.assertIsNotNone(icon.pixmap())
            self.assertFalse(icon.pixmap().isNull())
            self.assertEqual(status.text(), "LOCKED")
            self.assertIn("Making History", summary.text())
            self.assertEqual(roster.count(), len(ENCHANTED_KEY_SITE_IDS))
            self.assertFalse(primary.isEnabled())
            self.assertTrue(replace.isHidden())

            pd["quests"]["making_history"] = {
                "started": True,
                "progress": 4,
                "completed": True,
            }
            pd["inventory"][ENCHANTED_KEY_ITEM] = 1
            pd["inventory"][ENCHANTED_KEY_SPADE] = 1
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()
            view = enchanted_key_view_pure(pd)
            self.assertEqual(status.text(), f"{len(ENCHANTED_KEY_SITE_IDS)} LEFT")
            self.assertIn(str(roster.currentData()), view["selectable_site_ids"])
            self.assertTrue(primary.isEnabled())

            chosen = str(roster.currentData())
            primary.click()
            QApplication.processEvents()
            self.assertEqual(
                self._enchanted_key_calls[-1],
                ("select_site", {"site_id": chosen}),
            )
            self.assertEqual(pd["enchanted_key"]["selected_site_id"], chosen)
            self.assertTrue(enchanted_key_view_pure(pd)["can_review"])
        finally:
            if dialog is not None:
                dialog.deleteLater()

    def test_phoenix_lair_advanced_mode_names_the_carried_pack_gate(self) -> None:
        from ankiscape.logic.phoenix_lair_logic import default_phoenix_lair_state_pure

        pd = _make_player_data()
        pd["phoenix_lair"] = default_phoenix_lair_state_pure()
        pd["activity_session"] = {"active_id": ""}
        pd["combat_encounter"] = {}
        pd["quests"]["in_pyre_need"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["slayer_level"] = 99
        pd["inventory"].update({"Knife": 1, "Secateurs": 1, "Tinderbox": 1})
        pd["carried_advanced_targets"] = {"phoenix_lair": True}
        pd["carried_layout"] = {
            "phoenix_lair": {
                "Knife": 1,
                "Secateurs": 1,
            }
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "phoenix_lair")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        status = _find_named_label(dialog, "phoenixLairStatusChip")
        summary = _find_named_label(dialog, "phoenixLairSummary")
        primary = _find_named_button(dialog, "phoenixLairPrimaryButton")
        self.assertEqual(status.text(), "LOCKED")
        self.assertIn("Tinderbox in carried pack or toolbelt", summary.text())
        self.assertNotIn("Bank or toolbelt", summary.text())
        self.assertFalse(primary.isEnabled())

    def test_barrows_card_enters_selects_repairs_and_suspends_without_nested_scroll(self) -> None:
        from ankiscape.logic.barrows_logic import default_barrows_state_pure

        pd = _make_player_data()
        pd["barrows"] = default_barrows_state_pure()
        pd["activity_session"] = {"active_id": ""}
        pd["combat_encounter"] = {}
        pd["inventory"]["Coins"] = 500_000
        pd["inventory"]["Verac's flail 50"] = 1
        pd["equipment_instances"] = {
            "equipment-7": {
                "family_id": "barrows_verac",
                "item_name": "Verac's flail 50",
                "condition": 45_000,
                "location": "bank",
            }
        }
        pd["equipment_instance_next_id"] = 8
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "barrows")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "barrowsPanel")
        status = _find_named_label(dialog, "barrowsStatusChip")
        summary = _find_named_label(dialog, "barrowsSummary")
        primary = _find_named_button(dialog, "barrowsPrimaryButton")
        leave = _find_named_button(dialog, "barrowsLeaveButton")
        mode = panel.findChild(QComboBox, "barrowsModeCombo")
        brother = panel.findChild(QComboBox, "barrowsBrotherCombo")
        repair = panel.findChild(QComboBox, "barrowsRepairCombo")
        repair_button = _find_named_button(dialog, "barrowsRepairButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("dangerous death", summary.text())
        self.assertTrue(leave.isHidden())
        self.assertEqual(repair.count(), 1)

        repair_button.click()
        QApplication.processEvents()
        self.assertEqual(self._barrows_calls[-1][0], "repair")
        self.assertEqual(pd["inventory"]["Verac's flail"], 1)

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._barrows_calls[-1], ("enter", {}))
        self.assertEqual(pd["current_utility"], "barrows")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertFalse(leave.isHidden())

        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertEqual(
            self._barrows_calls[-1],
            ("set_mode", {"automation_mode": "advanced"}),
        )
        self.assertFalse(brother.isHidden())
        self.assertGreater(brother.count(), 1)
        brother.setCurrentIndex(1)
        QApplication.processEvents()
        self.assertEqual(self._barrows_calls[-1][0], "select_brother")

        pd["barrows"].update(
            {
                "phase": "tunnels",
                "surface_queue": [],
                "selected_brother": "",
                "start_room": 0,
                "current_room": 0,
                "usable_edges": [
                    "0-1",
                    "0-3",
                    "1-2",
                    "2-5",
                    "3-4",
                    "5-8",
                    "6-7",
                    "7-8",
                ],
                "revealed_rooms": [0, 1, 3, 4],
            }
        )
        mode.setCurrentIndex(mode.findData("casual"))
        QApplication.processEvents()
        room_buttons = [
            _find_named_button(dialog, f"barrowsRoom{room}Button")
            for room in range(9)
        ]
        self.assertTrue(all(not button.isHidden() for button in room_buttons))
        self.assertTrue(any(button.text() == "?" for button in room_buttons))

        leave.click()
        QApplication.processEvents()
        self.assertEqual(self._barrows_calls[-1], ("leave", {}))
        self.assertEqual(status.text(), "SUSPENDED")
        self.assertTrue(pd["barrows"]["suspended"])

    def test_flash_powder_factory_card_enters_configures_rewards_and_cashes_out_without_nested_scroll(self) -> None:
        from ankiscape.logic.agility_logic import default_agility_state_pure

        pd = _make_player_data()
        pd.update(default_agility_state_pure())
        pd.update(
            {
                "agility_level": 99,
                "thieving_level": 99,
                "herblore_level": 99,
                "current_utility": "flash_powder_factory",
                "activity_session": {"active_id": ""},
                "summoning_state": {"active_follower": {}},
            }
        )
        pd["agility_activity_currencies"]["brianpoints"] = 5_000
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "flash_powder_factory")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "flashPowderFactoryPanel")
        status = _find_named_label(dialog, "flashPowderFactoryStatusChip")
        summary = _find_named_label(dialog, "flashPowderFactorySummary")
        primary = _find_named_button(dialog, "flashPowderFactoryPrimaryButton")
        leave = _find_named_button(dialog, "flashPowderFactoryLeaveButton")
        mode = panel.findChild(QComboBox, "flashPowderFactoryModeCombo")
        strategy = panel.findChild(QComboBox, "flashPowderFactoryStrategyCombo")
        apparatus = panel.findChild(QComboBox, "flashPowderFactoryApparatusCombo")
        rewards = panel.findChild(QComboBox, "flashPowderFactoryRewardCombo")
        buy = _find_named_button(dialog, "flashPowderFactoryRewardButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("Eight circuits", summary.text())
        self.assertTrue(leave.isHidden())

        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("enter_flash_powder_factory", {}),
        )
        self.assertEqual(pd["current_utility"], "flash_powder_factory")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertEqual(primary.text(), "Selected for reviews")
        self.assertFalse(leave.isHidden())

        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertFalse(apparatus.isHidden())
        strategy.setCurrentIndex(strategy.findData("rogue_equipment"))
        apparatus.setCurrentIndex(apparatus.findData("opportunistic"))
        QApplication.processEvents()
        self.assertEqual(
            pd["agility_flash_powder_factory_policy"]["strategy"],
            "rogue_equipment",
        )
        self.assertEqual(
            pd["agility_flash_powder_factory_policy"]["apparatus_policy"],
            "opportunistic",
        )

        rewards.setCurrentIndex(rewards.findData("Rogue kit"))
        QApplication.processEvents()
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Rogue kit"], 1)

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_flash_powder_factory", {}),
        )
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

    def test_pyramid_plunder_card_configures_enters_and_leaves_without_nested_scroll(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "thieving_level": 91,
                "strength_level": 99,
                "runecrafting_level": 99,
                "current_utility": "pyramid_plunder",
                "activity_session": {"active_id": ""},
                "carried_inventory": {},
                "carried_layout": {},
                "carried_advanced_targets": {},
                "pyramid_plunder": {},
                "pyramid_plunder_priority": "max_xp",
                "pyramid_plunder_runs_completed": 0,
                "pyramid_plunder_last_result": "Ready to enter",
            }
        )
        pd["quests"]["icthlarins_little_helper"] = {
            "started": True,
            "completed": False,
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "pyramid_plunder")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "pyramidPlunderPanel")
        status = _find_named_label(dialog, "pyramidPlunderStatusChip")
        summary = _find_named_label(dialog, "pyramidPlunderSummary")
        primary = _find_named_button(dialog, "pyramidPlunderPrimaryButton")
        leave = _find_named_button(dialog, "pyramidPlunderLeaveButton")
        priority = panel.findChild(QComboBox, "pyramidPlunderPriorityCombo")
        priority_label = _find_named_label(
            dialog,
            "pyramidPlunderPriorityLabel",
        )
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("Rooms 1–8", summary.text())
        self.assertEqual(priority_label.text(), "Priority")
        self.assertTrue(leave.isHidden())

        priority.setCurrentIndex(priority.findData("treasure"))
        QApplication.processEvents()
        self.assertEqual(pd["pyramid_plunder_priority"], "treasure")
        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("enter_pyramid_plunder", {}),
        )
        self.assertEqual(pd["current_utility"], "pyramid_plunder")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertEqual(primary.text(), "Selected for reviews")
        self.assertFalse(leave.isHidden())
        self.assertFalse(priority.isEnabled())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_pyramid_plunder", {}),
        )
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

    def test_pyramid_plunder_failed_entry_preserves_current_selection(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "thieving_level": 91,
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "carried_inventory": {},
                "carried_layout": {},
                "carried_advanced_targets": {},
            }
        )
        pd["quests"]["icthlarins_little_helper"] = {
            "started": True,
            "completed": False,
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "pyramid_plunder")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        primary = _find_named_button(dialog, "pyramidPlunderPrimaryButton")
        pd["quests"]["icthlarins_little_helper"] = {
            "started": False,
            "completed": False,
        }
        with patch.object(self._ui, "show_error_message"):
            primary.click()
            QApplication.processEvents()

        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd.get("pyramid_plunder", {}), {})

    def test_werewolf_skullball_card_configures_enters_and_leaves_without_nested_scroll(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 25,
                "equipment": {"ring": "Ring of Charos"},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        pd["quests"]["creature_of_fenkenstrain"] = {
            "started": True,
            "completed": True,
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "werewolf_skullball")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "werewolfSkullballPanel")
        status = _find_named_label(dialog, "werewolfSkullballStatusChip")
        summary = _find_named_label(dialog, "werewolfSkullballSummary")
        primary = _find_named_button(dialog, "werewolfSkullballPrimaryButton")
        leave = _find_named_button(dialog, "werewolfSkullballLeaveButton")
        mode = panel.findChild(QComboBox, "werewolfSkullballModeCombo")
        route = panel.findChild(QComboBox, "werewolfSkullballRouteCombo")
        plan = panel.findChild(QLineEdit, "werewolfSkullballPlanEdit")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("10 goals", summary.text())
        self.assertTrue(plan.isHidden())
        self.assertTrue(leave.isHidden())

        route.setCurrentIndex(route.findData("fast"))
        QApplication.processEvents()
        self.assertEqual(pd["werewolf_skullball_policy"]["route"], "fast")
        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertFalse(plan.isHidden())
        with patch.object(self._ui, "show_error_message"):
            plan.setText("T X S")
            plan.editingFinished.emit()
            QApplication.processEvents()
        self.assertEqual(plan.text(), "T X S")
        self.assertEqual(mode.currentData(), "advanced")
        plan.setText(" ".join(("T",) * 31))
        plan.editingFinished.emit()
        QApplication.processEvents()
        self.assertIn("742 Agility XP", summary.text())
        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            [call[0] for call in self._agility_command_calls[-2:]],
            ["set_werewolf_skullball_policy", "enter_werewolf_skullball"],
        )
        self.assertEqual(pd["current_utility"], "werewolf_skullball")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertEqual(primary.text(), "Selected for reviews")
        self.assertFalse(leave.isHidden())
        self.assertFalse(mode.isEnabled())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_werewolf_skullball", {}),
        )
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

    def test_werewolf_skullball_failed_entry_preserves_current_selection(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 25,
                "equipment": {"ring": "Ring of Charos"},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        pd["quests"]["creature_of_fenkenstrain"] = {
            "started": True,
            "completed": True,
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "werewolf_skullball")
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        primary = _find_named_button(dialog, "werewolfSkullballPrimaryButton")
        pd["equipment"] = {}
        with patch.object(self._ui, "show_error_message"):
            primary.click()
            QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd.get("werewolf_skullball", {}), {})

    def test_locked_werewolf_skullball_row_opens_requirement_card_in_real_qt(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 1,
                "equipment": {},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "werewolf_skullball")
        self.assertFalse(row.isDisabled())
        activity_tree.setCurrentItem(row)
        activity_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()

        status = _find_named_label(dialog, "werewolfSkullballStatusChip")
        summary = _find_named_label(dialog, "werewolfSkullballSummary")
        primary = _find_named_button(dialog, "werewolfSkullballPrimaryButton")
        self.assertEqual(status.text(), "LOCKED")
        self.assertIn("Agility level 25", summary.text())
        self.assertIn("Creature of Fenkenstrain", summary.text())
        self.assertIn("equip a Ring of Charos", summary.text())
        self.assertFalse(primary.isEnabled())
        self.assertEqual(pd["current_utility"], "bankstanding")

    def test_switching_from_werewolf_skullball_requires_and_honours_leave_confirmation(self) -> None:
        from ankiscape.logic.werewolf_skullball_logic import enter_werewolf_skullball_pure

        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 25,
                "equipment": {"ring": "Ring of Charos"},
                "activity_session": {"active_id": ""},
            }
        )
        pd["quests"]["creature_of_fenkenstrain"] = {
            "started": True,
            "completed": True,
        }
        pd, ok, _info = enter_werewolf_skullball_pure(pd)
        self.assertTrue(ok)
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)
        bankstanding = _utility_row(utility_tree, "bankstanding")

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "werewolf_skullball")
        self.assertTrue(pd["werewolf_skullball"])

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_werewolf_skullball", {}),
        )
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd["werewolf_skullball"], {})

    def test_gnome_ball_card_enters_and_leaves_without_nested_scroll(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "equipment": {},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "gnome_ball")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "gnomeBallPanel")
        status = _find_named_label(dialog, "gnomeBallStatusChip")
        summary = _find_named_label(dialog, "gnomeBallSummary")
        primary = _find_named_button(dialog, "gnomeBallPrimaryButton")
        bank_reward = _find_named_button(dialog, "gnomeBallBankRewardButton")
        leave = _find_named_button(dialog, "gnomeBallLeaveButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("52 Agility + 52 Ranged XP", summary.text())
        self.assertIn("tackle risk", summary.text())
        ready_status_style = status.styleSheet()
        self.assertTrue(bank_reward.isHidden())
        self.assertTrue(leave.isHidden())

        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("enter_gnome_ball", {}),
        )
        self.assertEqual(pd["current_utility"], "gnome_ball")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertNotEqual(status.styleSheet(), ready_status_style)
        self.assertEqual(primary.text(), "Selected for reviews")
        self.assertIn("Beat 1/3", summary.text())
        self.assertFalse(leave.isHidden())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_gnome_ball", {}),
        )
        self.assertEqual(status.text(), "READY")
        self.assertIn("Left Gnome Ball", summary.text())
        self.assertTrue(leave.isHidden())

    def test_gnome_ball_card_banks_the_carried_referee_reward(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "gnome_ball",
                "activity_session": {"active_id": ""},
                "gnome_ball": {},
                "gnome_ball_runs_completed": 1,
                "inventory": {"Gnomeball": 2},
                "carried_inventory": {"gnome_ball": {"Gnomeball": 1}},
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "gnome_ball")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        summary = _find_named_label(dialog, "gnomeBallSummary")
        bank_reward = _find_named_button(dialog, "gnomeBallBankRewardButton")
        self.assertIn("Gnomeball carried", summary.text())
        self.assertFalse(bank_reward.isHidden())

        bank_reward.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("bank_gnomeball_reward", {}),
        )
        self.assertEqual(pd["inventory"]["Gnomeball"], 2)
        self.assertNotIn(
            "Gnomeball",
            pd.get("carried_inventory", {}).get("gnome_ball", {}),
        )
        self.assertIn("another can be awarded", summary.text())
        self.assertTrue(bank_reward.isHidden())

    def test_locked_gnome_ball_row_opens_weapon_requirement_card(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "equipment": {"weapon": "Bronze sword"},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "gnome_ball")
        self.assertFalse(row.isDisabled())
        activity_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()

        status = _find_named_label(dialog, "gnomeBallStatusChip")
        summary = _find_named_label(dialog, "gnomeBallSummary")
        primary = _find_named_button(dialog, "gnomeBallPrimaryButton")
        self.assertEqual(status.text(), "LOCKED")
        self.assertIn("only a Gnomeball is allowed", summary.text())
        self.assertFalse(primary.isEnabled())
        self.assertEqual(pd["current_utility"], "bankstanding")

    def test_fish_flingers_card_enters_shops_and_leaves_without_nested_scroll(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "shop_market_clock": {"answered_cards": 0, "market_tick": 0},
                "fish_flingers_tokens": 140,
                "fish_flingers_medals": 0,
                "fish_flingers_last_ticket_day": -1,
            }
        )
        dialog = self._open(pd)
        dialog.show()
        dialog.resize(720, 560)
        for _ in range(3):
            QApplication.processEvents()
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "fish_flingers")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "fishFlingersPanel")
        summary = _find_named_label(dialog, "fishFlingersSummary")
        currency = _find_named_label(dialog, "fishFlingersCurrencyChip")
        primary = _find_named_button(dialog, "fishFlingersPrimaryButton")
        leave = _find_named_button(dialog, "fishFlingersLeaveButton")
        progress = panel.findChild(QProgressBar, "fishFlingersProgress")
        reward = panel.findChild(QComboBox, "fishFlingersRewardCombo")
        buy = _find_named_button(dialog, "fishFlingersBuyButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertIn("READY · 2 tickets", currency.text())
        self.assertIn("Six successful reviews", summary.text())
        self.assertNotIn("claim", summary.text())
        self.assertTrue(progress.isHidden())
        self.assertEqual(reward.currentData(), "fishing_hat")
        self.assertEqual(
            reward.sizeAdjustPolicy(),
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon,
        )
        self.assertTrue(buy.isEnabled())
        basic_index = reward.findData("basic_tackle_box")
        self.assertIn("upgrade Beginner's tackle box", reward.itemText(basic_index))

        buy.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fish_flingers_calls[-1],
            ("buy_fish_flingers_reward", {"reward_id": "fishing_hat"}),
        )
        self.assertEqual(pd["inventory"]["Fishing hat"], 1)
        self.assertIn("0 tokens", currency.text())
        self.assertIn("Requires 140 Fishing tokens", buy.toolTip())

        primary.click()
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(
            self._fish_flingers_calls[-1],
            ("enter_fish_flingers", {}),
        )
        self.assertEqual(pd["current_utility"], "fish_flingers")
        self.assertEqual(primary.text(), "Selected for reviews")
        self.assertIn("ACTIVE", currency.text())
        self.assertIn("Bass at Lake", summary.text())
        self.assertIn("stock 24/24 (100%, Rich)", summary.text())
        self.assertIn("rotation 1/6", summary.text())
        self.assertIn("communal pressure 3 stock per review", summary.text())
        self.assertIn("palette(text)", summary.styleSheet())
        self.assertGreaterEqual(summary.height(), summary.sizeHint().height())
        self.assertLessEqual(panel.width(), dialog.width())
        self.assertEqual(progress.format(), "%v of 6 landed")
        self.assertFalse(progress.isHidden())
        self.assertFalse(leave.isHidden())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fish_flingers_calls[-1],
            ("leave_fish_flingers", {}),
        )
        self.assertTrue(leave.isHidden())
        self.assertIn("forfeited", summary.text())

    def test_fishing_trawler_card_saves_plan_boards_and_returns_supplies_on_leave(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "fishing_level": 81,
                "inventory": {
                    **pd["inventory"],
                    "Swamp paste": 60,
                    "Rope": 4,
                    "Bailing bucket": 1,
                },
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "fishing_trawler")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "fishingTrawlerPanel")
        summary = _find_named_label(dialog, "fishingTrawlerSummary")
        status = _find_named_label(dialog, "fishingTrawlerStatusChip")
        mode = panel.findChild(QComboBox, "fishingTrawlerModeCombo")
        priority = panel.findChild(QComboBox, "fishingTrawlerPriorityCombo")
        paste = panel.findChild(QSpinBox, "fishingTrawlerPasteSpin")
        rope = panel.findChild(QSpinBox, "fishingTrawlerRopeSpin")
        bucket = panel.findChild(QSpinBox, "fishingTrawlerBucketsSpin")
        save = _find_named_button(dialog, "fishingTrawlerSavePlanButton")
        primary = _find_named_button(dialog, "fishingTrawlerPrimaryButton")
        leave = _find_named_button(dialog, "fishingTrawlerLeaveButton")
        water = panel.findChild(QProgressBar, "fishingTrawlerWater")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "DOCKED · 0 landed · 0 sunk")
        self.assertIn("Ten useful duties", summary.text())
        self.assertTrue(water.isHidden())

        mode.setCurrentIndex(mode.findData("advanced"))
        priority.setCurrentIndex(priority.findData("catch_first"))
        paste.setValue(20)
        rope.setValue(2)
        bucket.setValue(1)
        save.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fishing_trawler_calls[-1],
            (
                "set_fishing_trawler_policy",
                {
                    "automation_mode": "advanced",
                    "priority": "catch_first",
                    "layout": {
                        "Swamp paste": 20,
                        "Rope": 2,
                        "Bailing bucket": 1,
                    },
                },
            ),
        )

        # Boarding atomically persists the visible plan, even when the user
        # changed it after the last explicit Save.
        paste.setValue(30)

        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fishing_trawler_calls[-1],
            (
                "enter_fishing_trawler",
                {
                    "automation_mode": "advanced",
                    "priority": "catch_first",
                    "layout": {
                        "Swamp paste": 30,
                        "Rope": 2,
                        "Bailing bucket": 1,
                    },
                },
            ),
        )
        self.assertEqual(pd["current_utility"], "fishing_trawler")
        self.assertEqual(primary.text(), "Selected for reviews")
        self.assertIn("AT SEA", status.text())
        self.assertFalse(water.isHidden())
        self.assertFalse(mode.isEnabled())
        self.assertFalse(save.isEnabled())
        self.assertEqual(pd["inventory"]["Swamp paste"], 30)

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fishing_trawler_calls[-1],
            ("leave_fishing_trawler", {}),
        )
        self.assertTrue(leave.isHidden())
        self.assertEqual(pd["inventory"]["Swamp paste"], 60)
        self.assertIn("haul forfeited", summary.text())

    def test_fishing_trawler_level_gate_is_visible_without_hover(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "fishing_level": 14,
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "fishing_trawler")
        self.assertFalse(row.isDisabled())
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()
        status = _find_named_label(dialog, "fishingTrawlerStatusChip")
        summary = _find_named_label(dialog, "fishingTrawlerSummary")
        primary = _find_named_button(dialog, "fishingTrawlerPrimaryButton")
        self.assertEqual(status.text(), "LOCKED · 0 landed · 0 sunk")
        self.assertIn("Requires level 15 Fishing", summary.text())
        self.assertFalse(primary.isEnabled())

    def test_great_orb_project_card_saves_buys_enters_and_leaves(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "runecrafting_level": 50,
                "great_orb_project": {
                    "tokens": 200,
                    "games_completed": 0,
                    "games_won": 0,
                    "automation_mode": "casual",
                    "doctrine": "balanced",
                    "crafting_policy": "craft_each_round",
                    "active": {},
                },
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "great_orb_project")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "greatOrbProjectPanel")
        status = _find_named_label(dialog, "greatOrbProjectStatusChip")
        summary = _find_named_label(dialog, "greatOrbProjectSummary")
        mode = panel.findChild(QComboBox, "greatOrbProjectModeCombo")
        doctrine = panel.findChild(QComboBox, "greatOrbProjectDoctrineCombo")
        crafting = panel.findChild(QComboBox, "greatOrbProjectCraftingCombo")
        reward = panel.findChild(QComboBox, "greatOrbProjectRewardCombo")
        quantity = panel.findChild(QSpinBox, "greatOrbProjectRewardQuantity")
        progress = panel.findChild(QProgressBar, "greatOrbProjectProgress")
        currency = _find_named_label(dialog, "greatOrbProjectCurrencyLabel")
        save = _find_named_button(dialog, "greatOrbProjectSaveButton")
        buy = _find_named_button(dialog, "greatOrbProjectBuyButton")
        primary = _find_named_button(dialog, "greatOrbProjectPrimaryButton")
        leave = _find_named_button(dialog, "greatOrbProjectLeaveButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertIn("GUILD · 0/0 matches won", status.text())
        self.assertEqual(currency.text(), "200 tokens")
        self.assertIn("Eight altar rounds", summary.text())
        self.assertTrue(progress.isHidden())
        self.assertGreaterEqual(reward.findData("elemental_talisman"), 0)
        reward.setCurrentIndex(reward.findData("omni_talisman"))
        QApplication.processEvents()
        self.assertEqual(buy.text(), "Claim")
        self.assertFalse(buy.isEnabled())
        self.assertIn("Show Elriss", buy.toolTip())

        mode.setCurrentIndex(mode.findData("advanced"))
        doctrine.setCurrentIndex(doctrine.findData("repel"))
        crafting.setCurrentIndex(crafting.findData("save_for_nature"))
        save.click()
        QApplication.processEvents()
        self.assertEqual(
            self._great_orb_project_calls[-1],
            (
                "set_great_orb_project_policy",
                {
                    "automation_mode": "advanced",
                    "doctrine": "repel",
                    "crafting_policy": "save_for_nature",
                },
            ),
        )

        reward.setCurrentIndex(reward.findData("pure_essence"))
        quantity.setValue(25)
        buy.click()
        QApplication.processEvents()
        self.assertEqual(
            self._great_orb_project_calls[-1],
            (
                "buy_great_orb_project_reward",
                {"reward_id": "pure_essence", "quantity": 25},
            ),
        )
        self.assertEqual(pd["inventory"]["Pure essence"], 25)
        self.assertEqual(currency.text(), "175 tokens")

        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._great_orb_project_calls[-1],
            (
                "enter_great_orb_project",
                {
                    "automation_mode": "advanced",
                    "doctrine": "repel",
                    "crafting_policy": "save_for_nature",
                },
            ),
        )
        self.assertEqual(pd["current_utility"], "great_orb_project")
        self.assertIn("IN MATCH", status.text())
        self.assertIn("Round 1/8", summary.text())
        self.assertEqual(progress.value(), 1)
        self.assertFalse(progress.isHidden())
        self.assertTrue(panel.findChild(QWidget, "greatOrbProjectPolicy").isHidden())
        self.assertFalse(leave.isHidden())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._great_orb_project_calls[-1],
            ("leave_great_orb_project", {}),
        )
        self.assertTrue(leave.isHidden())
        self.assertIn("pending tokens forfeited", summary.text())

    def test_great_orb_project_level_gate_is_visible_without_hover(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "runecrafting_level": 49,
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "great_orb_project")
        self.assertFalse(row.isDisabled())
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()
        status = _find_named_label(dialog, "greatOrbProjectStatusChip")
        summary = _find_named_label(dialog, "greatOrbProjectSummary")
        primary = _find_named_button(dialog, "greatOrbProjectPrimaryButton")
        self.assertIn("LOCKED", status.text())
        self.assertIn("Requires level 50 Runecrafting", summary.text())
        self.assertFalse(primary.isEnabled())

    def test_managing_miscellania_card_funds_allocates_collects_and_selects(self) -> None:
        from ankiscape.logic.managing_miscellania_logic import default_managing_miscellania_state_pure

        pd = _make_player_data()
        pd.update(default_managing_miscellania_state_pure())
        pd.update(
            {
                "current_utility": "bankstanding",
                "woodcutting_level": 45,
                "inventory": {"Coins": 1_000_000},
                "shop_market_clock": {"answered_cards": 0},
            }
        )
        pd["quests"]["throne_of_miscellania"] = {"completed": True}
        pd["managing_miscellania"]["approval_basis_points"] = 9_900
        pd["managing_miscellania"]["production_credit"] = 1_000_000
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "managing_miscellania")
        self.assertFalse(row.isDisabled())
        self.assertFalse(row.icon(0).isNull())
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "managingMiscellaniaPanel")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertFalse(
            panel.findChild(QLabel, "managingMiscellaniaIcon").pixmap().isNull()
        )
        approval = panel.findChild(QProgressBar, "managingMiscellaniaApproval")
        chore = panel.findChild(QComboBox, "managingMiscellaniaApprovalChore")
        clock = panel.findChild(QLabel, "managingMiscellaniaClock")
        summary = panel.findChild(QLabel, "managingMiscellaniaSummary")
        preview = panel.findChild(QLabel, "managingMiscellaniaPreview")
        self.assertEqual(approval.value(), 9_900)
        self.assertEqual(chore.count(), 1)
        self.assertEqual(chore.currentData(), "chop_maple")
        self.assertIn("240 reviews", clock.text())
        self.assertIn("2.5% per day", clock.text())
        self.assertIn("Unclaimed production follows", summary.text())

        fund = _find_named_button(dialog, "managingMiscellaniaFund7Button")
        self.assertEqual(fund.text(), "7 days · +800,000")
        fund.click()
        QApplication.processEvents()
        self.assertEqual(pd["managing_miscellania"]["coffer"], 800_000)
        self.assertEqual(pd["inventory"]["Coins"], 200_000)

        wood = panel.findChild(QSpinBox, "managingMiscellaniaWorkers_wood")
        _find_named_button(dialog, "managingMiscellaniaMax_wood").click()
        QApplication.processEvents()
        self.assertEqual(wood.value(), 10)
        self.assertEqual(pd["managing_miscellania"]["allocations"]["wood"], 10)
        self.assertEqual(
            panel.findChild(QLabel, "managingMiscellaniaPips_wood").text(),
            "●" * 10,
        )
        self.assertEqual(
            _find_named_label(dialog, "managingMiscellaniaStatusChip").text(),
            "FULLY ASSIGNED",
        )
        self.assertIn("Maple logs ×892", preview.text())

        collect = _find_named_button(dialog, "managingMiscellaniaCollectButton")
        self.assertTrue(collect.isEnabled())
        collect.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Maple logs"], 892)
        self.assertEqual(pd["inventory"]["Bird's nest (seeds)"], 8)
        self.assertIn("0.00 full-output days", preview.text())

        select = _find_named_button(dialog, "managingMiscellaniaSelectButton")
        select.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "managing_miscellania")
        self.assertEqual(select.text(), "Selected for reviews")

        activity_tree = _find_named_widget(dialog, "utilityActivityTree")
        landmark_groups = [
            item
            for item in (
                activity_tree.topLevelItem(index)
                for index in range(activity_tree.topLevelItemCount())
            )
            if item.data(0, Qt.ItemDataRole.UserRole)
            == "__utility_group__:landmarks"
        ]
        self.assertEqual(len(landmark_groups), 1)

        dialog.resize(1000, 560)
        dialog.show()
        for _ in range(8):
            QApplication.processEvents()
        visible_children = [
            child
            for child in panel.findChildren(
                QWidget,
                options=Qt.FindChildOption.FindDirectChildrenOnly,
            )
            if child.isVisible()
        ]
        self.assertTrue(visible_children)
        self.assertLessEqual(
            max(child.geometry().bottom() for child in visible_children),
            panel.contentsRect().bottom(),
        )

    def test_managing_miscellania_quest_gate_is_visible_without_hover(self) -> None:
        from ankiscape.logic.managing_miscellania_logic import default_managing_miscellania_state_pure

        pd = _make_player_data()
        pd.update(default_managing_miscellania_state_pure())
        pd["current_utility"] = "bankstanding"
        pd["quests"]["throne_of_miscellania"] = {"completed": False}
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "managing_miscellania")
        self.assertFalse(row.isDisabled())
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        self.assertEqual(
            _find_named_label(dialog, "managingMiscellaniaStatusChip").text(),
            "LOCKED",
        )
        self.assertIn(
            "Requires Throne of Miscellania",
            _find_named_label(dialog, "managingMiscellaniaSummary").text(),
        )
        self.assertIn(
            "Horizontal catalog: Mining, Maple, and Hardwood",
            _find_named_label(dialog, "managingMiscellaniaSummary").text(),
        )
        panel = _find_named_widget(dialog, "managingMiscellaniaPanel")
        self.assertFalse(
            _find_named_widget(dialog, "managingMiscellaniaCoffer").isVisible()
        )
        self.assertFalse(
            _find_named_button(dialog, "managingMiscellaniaDepositButton").isEnabled()
        )
        self.assertFalse(
            _find_named_button(dialog, "managingMiscellaniaSelectButton").isEnabled()
        )
        dialog.resize(1186, 768)
        dialog.show()
        for _ in range(8):
            QApplication.processEvents()
        visible_children = [
            child
            for child in panel.findChildren(
                QWidget,
                options=Qt.FindChildOption.FindDirectChildrenOnly,
            )
            if child.isVisible()
        ]
        self.assertTrue(visible_children)
        self.assertLessEqual(
            max(child.geometry().bottom() for child in visible_children),
            panel.contentsRect().bottom(),
        )

    def test_switching_from_gnome_ball_requires_and_honours_leave_confirmation(self) -> None:
        from ankiscape.logic.gnome_ball_logic import enter_gnome_ball_pure

        pd = _make_player_data()
        pd.update({"equipment": {}, "activity_session": {"active_id": ""}})
        pd, ok, _info = enter_gnome_ball_pure(pd)
        self.assertTrue(ok)
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)
        bankstanding = _utility_row(utility_tree, "bankstanding")

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "gnome_ball")
        self.assertTrue(pd["gnome_ball"])

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_gnome_ball", {}),
        )
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd["gnome_ball"], {})

    def test_switching_from_flash_powder_factory_requires_and_honours_cashout_confirmation(self) -> None:
        from ankiscape.logic.agility_logic import default_agility_state_pure
        from ankiscape.logic.flash_powder_factory_logic import enter_flash_powder_factory_pure

        pd = _make_player_data()
        pd.update(default_agility_state_pure())
        pd.update(
            {
                "agility_level": 99,
                "thieving_level": 99,
                "herblore_level": 99,
                "activity_session": {"active_id": ""},
                "summoning_state": {"active_follower": {}},
            }
        )
        pd, ok, _info = enter_flash_powder_factory_pure(pd)
        self.assertTrue(ok)
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)
        bankstanding = _utility_row(utility_tree, "bankstanding")

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "flash_powder_factory")
        self.assertIn(
            "flash_powder_factory",
            pd["agility_activity_state"],
        )

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_flash_powder_factory", {}),
        )
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertNotIn(
            "flash_powder_factory",
            pd["agility_activity_state"],
        )

    def test_switching_from_pyramid_plunder_requires_and_honours_bank_confirmation(self) -> None:
        from ankiscape.logic.pyramid_plunder_logic import enter_pyramid_plunder_pure

        pd = _make_player_data()
        pd.update(
            {
                "thieving_level": 91,
                "activity_session": {"active_id": ""},
                "carried_inventory": {},
                "carried_layout": {},
                "carried_advanced_targets": {},
            }
        )
        pd["quests"]["icthlarins_little_helper"] = {
            "started": True,
            "completed": False,
        }
        pd, ok, _info = enter_pyramid_plunder_pure(pd)
        self.assertTrue(ok)
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)
        bankstanding = _utility_row(utility_tree, "bankstanding")

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "pyramid_plunder")
        self.assertTrue(pd["pyramid_plunder"])

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_pyramid_plunder", {}),
        )
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd["pyramid_plunder"], {})

    def test_stealing_creation_card_exposes_session_policy_and_reward_tools(self) -> None:
        from ankiscape.logic.stealing_creation_logic import default_stealing_creation_state_pure

        pd = _make_player_data()
        pd.update(
            {
                "attack_level": 80,
                "defense_level": 80,
                "woodcutting_level": 80,
                "construction_level": 80,
                "stealing_creation": default_stealing_creation_state_pure(),
                "activity_session": {"active_id": ""},
            }
        )
        pd["stealing_creation"]["points"] = 40
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "stealing_creation")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "stealingCreationPanel")
        status = _find_named_label(dialog, "stealingCreationStatusChip")
        summary = _find_named_label(dialog, "stealingCreationSummary")
        primary = _find_named_button(dialog, "stealingCreationPrimaryButton")
        leave = _find_named_button(dialog, "stealingCreationLeaveButton")
        mode = panel.findChild(QComboBox, "stealingCreationModeCombo")
        duty = panel.findChild(QComboBox, "stealingCreationDutyCombo")
        method = panel.findChild(QComboBox, "stealingCreationGatherMethodCombo")
        clay_class = panel.findChild(QComboBox, "stealingCreationClassCombo")
        recipe = panel.findChild(QComboBox, "stealingCreationRecipeCombo")
        form = panel.findChild(QComboBox, "stealingCreationRewardFormCombo")
        morphic = _find_named_button(dialog, "stealingCreationMorphicButton")
        volatile = _find_named_button(dialog, "stealingCreationVolatileButton")
        active_tool = panel.findChild(QComboBox, "stealingCreationActiveToolCombo")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("40 reward points", summary.text())
        self.assertTrue(leave.isHidden())
        self.assertEqual(duty.currentText(), "Automatic duty rotation")
        self.assertTrue(method.currentText().startswith("Automatic route · "))
        self.assertTrue(clay_class.currentText().startswith("Automatic · Class "))
        self.assertEqual(recipe.currentText(), "Automatic kiln loadout")
        self.assertEqual(method.currentData(), "chop")
        self.assertEqual(clay_class.currentData(), 5)
        self.assertEqual(recipe.currentData(), "scimitar")

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._stealing_creation_calls[-1], ("enter", {}))
        self.assertEqual(pd["current_utility"], "stealing_creation")
        self.assertEqual(self._utility_calls[-1], "stealing_creation")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertIn("Review 0/20", summary.text())
        self.assertFalse(leave.isHidden())

        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertTrue(duty.isEnabled())
        duty.setCurrentIndex(duty.findData("process"))
        method.setCurrentIndex(method.findData("mine"))
        clay_class.setCurrentIndex(clay_class.findData(3))
        recipe.setCurrentIndex(recipe.findData("platebody"))
        QApplication.processEvents()
        action_id, payload = self._stealing_creation_calls[-1]
        self.assertEqual(action_id, "set_policy")
        self.assertEqual(payload["selected_duty"], "process")
        self.assertEqual(payload["selected_gather_method"], "mine")
        self.assertEqual(payload["selected_class"], 3)
        self.assertEqual(payload["selected_recipe"], "platebody")

        form.setCurrentIndex(form.findData("needle"))
        morphic.click()
        QApplication.processEvents()
        self.assertEqual(self._stealing_creation_calls[-1][0], "buy_tool")
        self.assertEqual(pd["inventory"]["Proto-tool"], 1)
        self.assertEqual(pd["stealing_creation"]["points"], 20)
        self.assertEqual(active_tool.findData("morphic") >= 0, True)

        volatile.click()
        QApplication.processEvents()
        self.assertEqual(self._stealing_creation_calls[-1][0], "buy_tool")
        self.assertEqual(pd["inventory"]["Volatile clay tool"], 1)
        self.assertEqual(pd["stealing_creation"]["points"], 0)
        self.assertEqual(pd["stealing_creation"]["active_reward_tool"], "volatile")

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(self._stealing_creation_calls[-1], ("leave", {}))
        self.assertFalse(pd["stealing_creation"]["active_session"])
        self.assertEqual(status.text(), "READY")

        dialog.show()
        dialog.resize(900, 560)
        for _ in range(8):
            QApplication.processEvents()
        self.assertTrue(panel.isVisible())
        self.assertLessEqual(
            panel.mapTo(dialog, panel.rect().bottomRight()).y(),
            dialog.contentsRect().bottom(),
        )

    def test_activities_show_only_the_selected_rich_detail_card(self) -> None:
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "shooting_stars",
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_shooting_star_world_clock_pure(pd)
        dialog = self._open(active)
        activity_tree = self._open_activities(dialog)
        dialog.show()
        QApplication.processEvents()

        star_panel = _find_named_widget(dialog, "shootingStarPanel")
        big_panel = _find_named_widget(dialog, "bigChinchompaPanel")
        evil_panel = _find_named_widget(dialog, "evilTreePanel")
        self.assertTrue(star_panel.isVisible())
        self.assertFalse(big_panel.isVisible())
        self.assertFalse(evil_panel.isVisible())

        big_row = _utility_row(activity_tree, "big_chinchompa")
        activity_tree.setCurrentItem(big_row)
        activity_tree.itemActivated.emit(big_row, 0)
        QApplication.processEvents()
        self.assertFalse(star_panel.isVisible())
        self.assertTrue(big_panel.isVisible())
        self.assertFalse(evil_panel.isVisible())

    def test_review_hud_omits_shooting_star_world_notices(self) -> None:
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "shooting_stars",
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_shooting_star_world_clock_pure(pd)
        hud = self._ui.ReviewHUD(None)
        hud.set_data(active, "Activities")
        notice = hud.findChild(QLabel, "reviewWorldNotice")
        self.assertFalse(notice.isVisible())
        self.assertNotIn("Shooting Star size", notice.text())
        # The projection itself must survive: the subtitle branch reads it.
        self.assertIn("stardust", hud.sub_lbl.text())

        event = active["shooting_star"]["active_event"]
        event.update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_card": 22,
            }
        )
        hud.set_data(active, "Activities")
        self.assertNotIn("Star sprite", notice.text())
        self.assertIn("ready for exchange", hud.sub_lbl.text())

    def test_review_hud_surfaces_active_fist_of_guthix_match(self) -> None:
        from ankiscape.logic.fist_of_guthix_logic import (
            default_fist_of_guthix_state_pure,
            start_fist_of_guthix_match_pure,
        )

        pd = _make_player_data()
        pd["current_utility"] = "fist_of_guthix"
        pd["fist_of_guthix"] = default_fist_of_guthix_state_pure()
        pd["fist_of_guthix"]["tutorial_complete"] = True
        active, ok, _ = start_fist_of_guthix_match_pure(
            pd, iter((0.3, 0.5, 0.2, 0.8, 0.1)).__next__
        )
        self.assertTrue(ok)
        match = active["fist_of_guthix"]["active_match"]
        match["player_charges"] = 1_240
        match["opponent_charges"] = 760
        hud = self._ui.ReviewHUD(None)

        hud.set_data(active, "Activities")

        notice = hud.findChild(QLabel, "reviewWorldNotice")
        self.assertTrue(notice.isVisible())
        self.assertIn("Fist of Guthix round 1/2", notice.text())
        self.assertIn("1,240–760 charges", notice.text())
        self.assertIn("Round 1/2", hud.sub_lbl.text())

    def test_hunter_private_ground_control_uses_carried_ticket_count(self) -> None:
        ticket = "Swamp lizard quota ticket"
        pd = _make_player_data()
        pd.update(
            {
                "hunter_level": 99,
                "current_hunter": "catch_swamp_lizard",
                "carried_inventory": {
                    "catch_swamp_lizard": {ticket: 2},
                },
                "hunter_private_ground_targets": [],
            }
        )
        pd["inventory"][ticket] = 2
        dialog = self._open(pd)
        _goto_hunter(dialog)

        control = dialog.findChild(QCheckBox, "hunterPrivateGroundCheck")
        hint = _find_named_label(dialog, "hunterPrivateGroundHint")
        self.assertFalse(control.isHidden())
        self.assertTrue(control.isEnabled())
        self.assertIn("2 carried", control.text())
        self.assertIn("only after a successful catch", hint.text())

        control.setChecked(True)
        QApplication.processEvents()
        self.assertEqual(
            pd["hunter_private_ground_targets"],
            ["catch_swamp_lizard"],
        )
        self.assertEqual(
            self._big_chinchompa_calls[-1],
            (
                "set_private_ground",
                {"target_id": "catch_swamp_lizard", "enabled": True},
            ),
        )

        pd["carried_inventory"]["catch_swamp_lizard"] = {}
        empty_dialog = self._open(pd)
        _goto_hunter(empty_dialog)
        configured_without_tickets = empty_dialog.findChild(
            QCheckBox, "hunterPrivateGroundCheck"
        )
        self.assertTrue(configured_without_tickets.isChecked())
        self.assertTrue(
            configured_without_tickets.isEnabled(),
            "A configured target must remain possible to uncheck after tickets run out.",
        )

    def test_review_hud_omits_big_chinchompa_world_notice(self) -> None:
        from ankiscape.logic.big_chinchompa_logic import (
            advance_big_chinchompa_world_clock_pure,
            default_big_chinchompa_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "big_chinchompa",
                "shop_market_clock": {"answered_cards": 60},
                "big_chinchompa": default_big_chinchompa_state_pure(),
            }
        )
        active, _ = advance_big_chinchompa_world_clock_pure(pd)
        hud = self._ui.ReviewHUD(None)

        hud.set_data(active, "Utility / Activities")

        # The reviewer overlay keeps in-progress session counters only; the
        # world event now reads on the D&D badge and the Activities strip.
        notice = hud.findChild(QLabel, "reviewWorldNotice")
        self.assertFalse(notice.isVisible())
        self.assertNotIn("Big Chinchompa", notice.text())
        # The projection itself must survive: the subtitle branch reads it.
        self.assertIn("soporith moth", hud.sub_lbl.text())
        rows = self._ui._world_event_rows(active)
        self.assertTrue(
            any(
                activity_id == "big_chinchompa" and "source min left" in text
                for activity_id, text in rows
            ),
            rows,
        )

    def test_distraction_badge_route_opens_the_named_activity_card(self) -> None:
        # The reviewer D&D badge calls this ctx entry; without it the badge
        # click would land the player on the Skills tab with no card open.
        from ankiscape.logic.big_chinchompa_logic import (
            advance_big_chinchompa_world_clock_pure,
            default_big_chinchompa_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "shop_market_clock": {"answered_cards": 60},
                "big_chinchompa": default_big_chinchompa_state_pure(),
            }
        )
        active, _ = advance_big_chinchompa_world_clock_pure(pd)
        pd.update(active)
        dialog = self._open(pd)

        navigate = self._ui._MAIN_MENU_CTX.get("open_activity")
        self.assertTrue(callable(navigate))
        navigate("big_chinchompa")
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "bigChinchompaPanel")
        stack = _find_named_widget(dialog, "utilityActivityDetailsStack")
        self.assertFalse(stack.isHidden())
        self.assertIs(stack.currentWidget(), panel)
        strip = _find_named_widget(dialog, "activityWorldEventsStrip")
        # The open card already shows this event in full, so the strip drops it.
        self.assertTrue(strip.isHidden())

        # No id means "show me the list", where the strip is at the top. The
        # panel is rebuilt, so every live detail stack must be hidden.
        navigate(None)
        QApplication.processEvents()
        self.assertEqual(
            [
                w for w in dialog.findChildren(QStackedWidget)
                if w.objectName() == "utilityActivityDetailsStack" and not w.isHidden()
            ],
            [],
        )
        self.assertTrue(
            any(
                "Big Chinchompa" in lbl.text()
                for lbl in dialog.findChildren(QLabel)
                if lbl.objectName() == "activityWorldEventsBody"
            ),
            "the hub list must keep the event on its world-events strip",
        )

    def test_utility_rows_use_activity_icon_contract(self) -> None:
        utility_tree = self._open_utility(self.dialog)
        for row in _tree_items(utility_tree):
            role = row.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(role, str) and role.startswith("__utility_group__"):
                continue
            self.assertFalse(row.icon(0).isNull(), f"{row.text(0)} should have an activity icon")

    def test_warriors_guild_panel_exposes_tokens_policy_and_room_state(self) -> None:
        pd = _make_player_data()
        pd["attack_level"] = 99
        pd["strength_level"] = 99
        pd["current_utility"] = "warriors_guild_animated_armour"
        pd["inventory"].update(
            {
                "Rune full helm": 1,
                "Rune platebody": 1,
                "Rune platelegs": 1,
            }
        )
        dialog = self._open(pd)
        utility_tree = self._open_activities(dialog)
        dialog.show()
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "warriorsGuildPanel")
        self.assertTrue(panel.isVisible())
        token_label = _find_named_label(dialog, "warriorsGuildTokenBalances")
        self.assertIn("Combat 0", token_label.text())
        self.assertIn("Balance 0", token_label.text())
        room_button = _find_named_button(dialog, "warriorsGuildRoomButton")
        self.assertFalse(room_button.isEnabled())
        self.assertIn("Need 30 of every", room_button.toolTip())

        for activity_id in (
            "warriors_guild_animated_armour",
            "warriors_guild_attack_dummy",
            "warriors_guild_catapult",
            "warriors_guild_shot_put",
            "warriors_guild_keg_balance",
        ):
            self.assertFalse(
                _utility_row(utility_tree, activity_id).icon(0).isNull(),
                activity_id,
            )

        automation = _find_named_widget(dialog, "warriorsGuildAutomationMode")
        self.assertIsInstance(automation, QComboBox)
        automation.setCurrentIndex(automation.findData("advanced"))
        QApplication.processEvents()
        self.assertEqual(
            self._warriors_guild_calls[-1][0],
            "set_policy",
        )
        self.assertEqual(pd["warriors_guild"]["automation_mode"], "advanced")
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        show_button = _find_named_button(
            dialog,
            "warriorsGuildShowDefender",
        )
        self.assertGreaterEqual(
            show_button.width(),
            show_button.sizeHint().width(),
        )
        next_label = _find_named_label(dialog, "warriorsGuildNextDefender")
        self.assertGreaterEqual(
            next_label.width(),
            next_label.sizeHint().width(),
        )

    def test_livid_farm_panel_exposes_progress_and_persists_routine(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "magic_level": 99,
                "agility_level": 60,
                "crafting_level": 60,
                "farming_level": 60,
                "construction_level": 50,
                "current_utility": "livid_farm",
            }
        )
        pd["quests"]["lunar_diplomacy"] = {"completed": True}
        pd["livid_farm"] = {
            "farm_routine": "complete",
            "produce_points": 227_900,
            "lifetime_produce_points": 227_900,
            "cycles_completed": 8,
            "unlocked_spells": [
                "south_falador_teleport",
                "repair_rune_pouch",
                "north_ardougne_teleport",
            ],
        }
        dialog = self._open(pd)
        utility_tree = self._open_activities(dialog)
        dialog.show()
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "lividFarmPanel")
        self.assertTrue(panel.isVisible())
        status = _find_named_label(dialog, "lividFarmStatus")
        self.assertIn("227,900 banked", status.text())
        self.assertIn("8 cycles", status.text())
        progress = _find_named_widget(dialog, "lividFarmUnlockProgress")
        self.assertEqual(progress.maximum(), 87_360)
        self.assertEqual(progress.value(), 780)
        self.assertIn("Next: Remote Farm", progress.format())
        self.assertIn("text-align: center", progress.styleSheet())
        row = _utility_row(utility_tree, "livid_farm")
        self.assertFalse(row.icon(0).isNull())

        routine = _find_named_widget(dialog, "lividFarmRoutine")
        self.assertIsInstance(routine, QComboBox)
        routine.setCurrentIndex(routine.findData("conserve"))
        QApplication.processEvents()

        self.assertEqual(
            self._livid_farm_calls[-1],
            ("set_routine", {"routine": "conserve"}),
        )
        self.assertEqual(pd["livid_farm"]["farm_routine"], "conserve")

    def test_livid_farm_wish_surface_is_compact_honest_and_actionable(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "magic_level": 99,
                "agility_level": 60,
                "crafting_level": 60,
                "farming_level": 60,
                "construction_level": 50,
                "current_utility": "livid_farm",
            }
        )
        pd["quests"]["lunar_diplomacy"] = {"completed": True}
        pd["livid_farm"] = {
            "borrowed_power_claimed": True,
            "produce_points": 73_000,
            "lifetime_produce_points": 900_000,
            "unlocked_spells": ["borrowed_power"],
        }
        dialog = self._open(pd)
        self._open_activities(dialog)
        dialog.show()
        QApplication.processEvents()

        picker = _find_named_widget(dialog, "lividFarmWishPicker")
        button = _find_named_widget(dialog, "lividFarmWishButton")
        status = _find_named_label(dialog, "lividFarmStatus")
        panel = _find_named_widget(dialog, "lividFarmPanel")
        self.assertIsInstance(picker, QComboBox)
        self.assertEqual(picker.count(), 10)
        self.assertTrue(button.isVisible())
        dialog.resize(900, 560)
        for _ in range(8):
            QApplication.processEvents()
        button_right = button.mapTo(
            panel,
            button.rect().bottomRight(),
        ).x()
        self.assertLessEqual(button_right, panel.contentsRect().right())
        button_bottom = button.mapTo(
            panel,
            button.rect().bottomRight(),
        ).y()
        self.assertLessEqual(button_bottom, panel.contentsRect().bottom())
        self.assertGreaterEqual(button.height(), 28)
        self.assertGreaterEqual(picker.height(), 28)

        blocked_index = picker.findData("rain_seeds")
        picker.setCurrentIndex(blocked_index)
        QApplication.processEvents()
        self.assertFalse(button.isEnabled())
        self.assertIn("not sourced", status.text())
        self.assertIsNotNone(
            picker.itemData(
                blocked_index,
                Qt.ItemDataRole.ForegroundRole,
            )
        )

        ready_index = picker.findData("gimme_herbs")
        picker.setCurrentIndex(ready_index)
        QApplication.processEvents()
        self.assertTrue(button.isEnabled())
        self.assertIn("18,000", button.text())
        button.click()
        QApplication.processEvents()

        self.assertEqual(
            self._livid_farm_calls[-1],
            ("buy_wish", {"wish_id": "gimme_herbs"}),
        )
        self.assertEqual(pd["inventory"]["Grimy kwuarm"], 3)
        self.assertEqual(pd["livid_farm"]["produce_points"], 55_000)

    def test_livid_farm_capacitor_surface_charges_and_removes_atomically(self) -> None:
        from ankiscape.data.livid_farm_data import (
            ARCANE_CAPACITOR_CHARGED,
            ARCANE_CAPACITOR_UNCHARGED,
        )

        pd = _make_player_data()
        pd.update(
            {
                "magic_level": 98,
                "agility_level": 60,
                "crafting_level": 60,
                "farming_level": 60,
                "construction_level": 50,
                "current_utility": "livid_farm",
            }
        )
        pd["quests"]["lunar_diplomacy"] = {"completed": True}
        pd["inventory"].update(
            {
                ARCANE_CAPACITOR_UNCHARGED: 1,
                "Air rune": 1_000,
                "Earth rune": 1_000,
                "Law rune": 1_000,
            }
        )
        pd["livid_farm"] = {
            "borrowed_power_claimed": True,
            "produce_points": 0,
            "unlocked_spells": ["borrowed_power"],
        }
        dialog = self._open(pd)
        self._open_activities(dialog)
        dialog.show()
        QApplication.processEvents()

        row = _find_named_widget(dialog, "lividFarmCapacitorRow")
        status = _find_named_label(dialog, "lividFarmCapacitorStatus")
        picker = _find_named_widget(dialog, "lividFarmCapacitorSpell")
        charge = _find_named_widget(dialog, "lividFarmCapacitorCharge")
        remove = _find_named_widget(dialog, "lividFarmCapacitorRemove")
        self.assertTrue(row.isVisible())
        self.assertEqual(status.text(), "Capacitor · Uncharged")
        house_index = picker.findData("teleport_to_house")
        self.assertGreaterEqual(house_index, 0)
        picker.setCurrentIndex(house_index)
        QApplication.processEvents()
        self.assertFalse(charge.isEnabled())
        self.assertEqual(charge.toolTip(), "Requires Magic level 99.")

        pd["magic_level"] = 99
        picker.setCurrentIndex((house_index + 1) % picker.count())
        picker.setCurrentIndex(house_index)
        QApplication.processEvents()
        self.assertTrue(charge.isEnabled())
        self.assertEqual(charge.toolTip(), "")

        charge.click()
        QApplication.processEvents()

        self.assertEqual(
            self._livid_farm_calls[-1],
            (
                "charge_capacitor",
                {"spell_id": "teleport_to_house"},
            ),
        )
        self.assertEqual(pd["inventory"][ARCANE_CAPACITOR_CHARGED], 1)
        self.assertNotIn(ARCANE_CAPACITOR_UNCHARGED, pd["inventory"])
        self.assertEqual(status.text(), "Capacitor · 1,000")
        self.assertIn("1,000 charges remaining", status.toolTip())
        self.assertTrue(remove.isEnabled())

        calls_before_cancel = len(self._livid_farm_calls)
        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            remove.click()
        QApplication.processEvents()
        self.assertEqual(len(self._livid_farm_calls), calls_before_cancel)
        self.assertEqual(pd["inventory"][ARCANE_CAPACITOR_CHARGED], 1)

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            remove.click()
        QApplication.processEvents()

        self.assertEqual(
            self._livid_farm_calls[-1],
            ("remove_capacitor_charge", {}),
        )
        self.assertNotIn(ARCANE_CAPACITOR_CHARGED, pd["inventory"])
        self.assertEqual(pd["inventory"]["Air rune"], 1_000)
        self.assertEqual(pd["inventory"]["Earth rune"], 1_000)
        self.assertEqual(pd["inventory"]["Law rune"], 1_000)

    def test_source_gathering_rows_are_enabled_and_selectable_from_utility(self) -> None:
        # gather_wool stands in for the retired scavenge_chicken_feathers
        # bridge (feathers are live NPC shop stock now).
        utility_tree = self._open_utility(self.dialog)
        self._utility_calls.clear()
        for action_id, output_item in (
            ("gather_wool", "Wool"),
            ("gather_swamp_toads", "Swamp toad"),
        ):
            with self.subTest(action_id=action_id):
                row = _utility_row(utility_tree, action_id)
                self.assertTrue(row.flags() & Qt.ItemFlag.ItemIsEnabled)
                self.assertFalse(row.icon(0).isNull())
                self.assertIn("No skill XP", row.toolTip(0))
                self.assertIn(f"Output: {output_item} x1", row.toolTip(0))
                self.assertIn("No materials required", row.toolTip(0))
                utility_tree.itemClicked.emit(row, 0)
                QApplication.processEvents()

        self.assertEqual(
            self._utility_calls,
            ["gather_wool", "gather_swamp_toads"],
        )

    def test_stronghold_landmark_row_selects_activity_when_unfinished(self) -> None:
        pd = _make_player_data()
        pd["stronghold_of_security"] = {"step": 1, "completed": False, "boots_choice": None}
        dialog = self._open(pd)
        utility_tree = self._open_activities(dialog)

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
        utility_tree = self._open_activities(dialog)

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
        utility_tree = self._open_activities(dialog)

        row = _utility_row(utility_tree, "stronghold_of_security")
        self.assertFalse(row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("Fancy boots", row.text(0))

        utility_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._stronghold_claim_calls, [])
        self.assertEqual(self._utility_calls, [])

    def test_mage_arena_alignment_and_attunement_rows_use_their_distinct_actions(self) -> None:
        pending = _make_player_data()
        pending["magic_level"] = 60
        pending["mage_arena"] = {
            "step": 4,
            "completed": False,
            "alignment": "",
            "attuned_spells": [],
        }
        pending_dialog = self._open(pending)
        pending_tree = self._open_activities(pending_dialog)
        alignment = _utility_row(
            pending_tree,
            "__mage_alignment__:guthix",
        )
        pending_tree.itemClicked.emit(alignment, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._mage_arena_calls[-1],
            ("select_alignment", "guthix"),
        )
        self.assertEqual(pending["mage_arena"]["alignment"], "guthix")
        self.assertEqual(self._utility_calls[-1], "mage_arena")

        completed = _make_player_data()
        completed["magic_level"] = 99
        completed["inventory"] = {"Guthix staff": 1}
        completed["mage_arena"] = {
            "step": 5,
            "completed": True,
            "alignment": "saradomin",
            "attuned_spells": ["saradomin_strike"],
        }
        completed_dialog = self._open(completed)
        completed_tree = self._open_activities(completed_dialog)
        attune = _utility_row(completed_tree, "mage_arena_attune:guthix")
        self.assertTrue(attune.flags() & Qt.ItemFlag.ItemIsEnabled)
        completed_tree.itemClicked.emit(attune, 0)
        QApplication.processEvents()
        self.assertEqual(self._utility_calls[-1], "mage_arena_attune:guthix")

        switch = _utility_row(completed_tree, "__mage_cape__:guthix")
        completed_tree.itemClicked.emit(switch, 0)
        QApplication.processEvents()
        self.assertEqual(self._mage_arena_calls[-1], ("cape", "guthix"))
        self.assertEqual(completed["mage_arena"]["alignment"], "guthix")
        self.assertNotIn(
            "claws_of_guthix",
            completed["mage_arena"]["attuned_spells"],
        )

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

    def test_hud_labels_legacy_no_xp_selection_with_its_real_surface(self) -> None:
        hud = self._ui.ReviewHUD(None)
        pd = _make_player_data()
        pd["current_utility"] = "gather_flax"
        hud.set_data(pd, "Utility / Activities")
        # The title carries the surface, so a "(no XP)" tail only restated it.
        self.assertEqual(hud.title_lbl.text(), "Utilities")
        self.assertEqual(hud.sub_lbl.text(), "Gather flax")

        pd["current_utility"] = "livid_farm"
        hud.set_data(pd, "Utility / Activities")
        self.assertEqual(hud.title_lbl.text(), "Activities")

        # Bankstanding keeps its qualifier: "deliberately not training" is not
        # implied by the title.
        pd["current_utility"] = "bankstanding"
        hud.set_data(pd, "Utility / Activities")
        self.assertEqual(hud.sub_lbl.text(), "Bankstanding • idle at the Bank")

    def test_hud_names_the_landmark_it_is_bound_to(self) -> None:
        # Landmarks live outside UTILITY_ACTIVITY_DATA, so the spec lookup is
        # empty and the subtitle used to read the literal "Material prep" — the
        # owner screenshotted exactly that while running Stronghold of Security.
        # Step-counter landmarks also carry their progress, which is the other
        # half of the same report ("no indication as to what I'm actually
        # doing"); the attunement has no counter, so it carries none.
        hud = self._ui.ReviewHUD(None)
        pd = _make_player_data()
        for activity_key, expected, wants_bar in (
            ("stronghold_of_security", "Stronghold of Security • 0/4", True),
            ("knight_waves", "Knight Waves Training Ground • 0/8", True),
            ("mage_arena", "Mage Arena • 0/5", True),
            ("mage_arena_attune:saradomin", "Mage Arena attunement", False),
        ):
            with self.subTest(activity=activity_key):
                pd["current_utility"] = activity_key
                hud.set_data(pd, "Utility / Activities")
                self.assertEqual(hud.sub_lbl.text(), expected)
                self.assertNotIn("Material prep", hud.sub_lbl.text())
                self.assertEqual(hud.progress.isVisible(), wants_bar)

    def test_hud_carries_no_grand_exchange_notice(self) -> None:
        # The collect reminder now lives on the Grand Exchange tab as a
        # collapsible fill log; the HUD line was removed with it.
        hud = self._ui.ReviewHUD(None)
        pd = _make_player_data()
        pd["ge_player_orders"] = [{"collectible_coins": 0, "collectible_items": 1}]

        hud.set_data(pd, "Mining")

        self.assertIsNone(hud.findChild(QLabel, "geOfferNotice"))

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

    def test_woodcutting_split_row_uses_material_gate_and_period_icon(self) -> None:
        pd = _make_player_data()
        pd["woodcutting_level"] = 54
        pd["inventory"] = {"Arctic pine logs": 1}
        pd["toolbelt"] = {"woodcutting": []}
        pd["quests"]["the_fremennik_isles"] = {"started": True}
        dialog = self._open(pd)
        tree_list = self._open_woodcutting(dialog)
        split = self._wc_row(tree_list, "Split Arctic pine logs ")
        self.assertTrue(bool(split.flags() & Qt.ItemFlag.ItemIsEnabled))
        self.assertIn("Arctic pine logs x1 (you have 1)", split.toolTip())
        self.assertNotIn("hatchet", split.toolTip().lower())
        self.assertFalse(split.icon().isNull())
        self.assertIn(
            "Select what to Chop or Split",
            [label.text() for label in dialog.findChildren(QLabel)],
        )

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

    def test_prayer_tree_groups_methods_and_locked_rows_ignore_clicks(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {}
        dialog = self._open(pd, current_skill="Prayer")
        tree = next(
            tree for tree in dialog.findChildren(QTreeWidget)
            if any(
                str(tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)).startswith("__prayer_group__:")
                for i in range(tree.topLevelItemCount())
            )
        )
        groups = [tree.topLevelItem(i).text(0).split("  (")[0] for i in range(tree.topLevelItemCount())]
        self.assertEqual(groups, ["Bury", "Scatter", "Ectofuntus", "Gilded altar"])
        bury = tree.topLevelItem(0)
        bones = next(bury.child(i) for i in range(bury.childCount()) if bury.child(i).data(0, Qt.ItemDataRole.UserRole) == "bury_bones")
        self.assertTrue(bones.isDisabled())
        before = list(self._prayer_calls)
        tree.itemClicked.emit(bones, 0)
        QApplication.processEvents()
        self.assertEqual(self._prayer_calls, before)

    def test_prayer_unlocked_row_selects_by_stable_target_id(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bones": 1}
        dialog = self._open(pd, current_skill="Prayer")
        tree = next(
            tree for tree in dialog.findChildren(QTreeWidget)
            if tree.findItems("Bones — 4.5 XP", Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive, 0)
        )
        row = tree.findItems("Bones — 4.5 XP", Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive, 0)[0]
        self.assertFalse(row.isDisabled())
        tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._prayer_calls[-1], ("bones", "base"))
        self.assertEqual(pd["current_prayer"], "bury_bones")

    def test_prayer_gilded_mode_rates_rows_and_readiness_refresh_live(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "prayer_level": 99,
                "current_prayer": "gilded_altar_dragon_bones",
                "prayer_gilded_mode": "hosted",
                "prayer_owned_altar_stint": {},
                "prayer_gilded_house_search": {},
                "house_owned": True,
                "house_rooms_bought": {"chapel": True},
                "house_built_flags": {"guilded_altar": True},
                "inventory": {"Dragon bones": 3, "Clean marrentill": 2},
            }
        )
        dialog = self._open(pd, current_skill="Mining")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(6):
            QApplication.processEvents()
        next(button for button in dialog.findChildren(QPushButton) if button.text() == "Combat").click()
        for _ in range(4):
            QApplication.processEvents()
        skill_list = next(
            widget
            for widget in dialog.findChildren(QListWidget)
            if {"Combat", "Prayer"}.issubset({widget.item(i).text() for i in range(widget.count())})
        )
        prayer_row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Prayer")
        skill_list.setCurrentRow(prayer_row)
        for _ in range(6):
            QApplication.processEvents()

        mode_label = dialog.findChild(QLabel, "prayerGildedModeLabel")
        mode = dialog.findChild(QComboBox, "prayerGildedModeCombo")
        self.assertEqual(mode_label.text(), "Gilded altar mode")
        self.assertEqual(mode.itemText(mode.findData("hosted")), "Hosted - 350% XP")
        self.assertEqual(mode.itemText(mode.findData("owned")), "Owned - 250% XP (0/2 burners)")
        self.assertEqual(mode.currentData(), "hosted")

        mode.setCurrentIndex(mode.findData("owned"))
        for _ in range(6):
            QApplication.processEvents()
        self.assertEqual(self._prayer_calls[-1], ("dragon_bones", "gilded_owned"))
        self.assertEqual(pd["prayer_gilded_mode"], "owned")
        mode = dialog.findChild(QComboBox, "prayerGildedModeCombo")
        tree = dialog.findChild(QTreeWidget, "prayerTargetTree")
        row = _tree_row(tree, "gilded_altar_dragon_bones")
        self.assertEqual(mode.currentData(), "owned")
        self.assertEqual(row.text(0), "Dragon bones — 180 XP")
        self.assertIn("Owned · 250% XP · 0/2 burners", row.toolTip(0))
        self.assertIn("none required (0 burners)", row.toolTip(0))
        self.assertFalse(row.isDisabled())
        self.assertTrue(dialog.findChild(QPushButton, "prayerTrainButton").isEnabled())

        pd["house_built_flags"]["marble_burner"] = True
        mode.setCurrentIndex(mode.findData("hosted"))
        for _ in range(6):
            QApplication.processEvents()
        mode = dialog.findChild(QComboBox, "prayerGildedModeCombo")
        self.assertEqual(mode.itemText(mode.findData("owned")), "Owned - 300% XP (1/2 burners)")

        pd["house_built_flags"]["mahogany_burner"] = True
        mode.setCurrentIndex(mode.findData("owned"))
        for _ in range(6):
            QApplication.processEvents()
        mode = dialog.findChild(QComboBox, "prayerGildedModeCombo")
        tree = dialog.findChild(QTreeWidget, "prayerTargetTree")
        row = _tree_row(tree, "gilded_altar_dragon_bones")
        self.assertEqual(mode.currentData(), "owned")
        self.assertEqual(mode.currentText(), "Owned - 350% XP (2/2 burners)")
        self.assertEqual(row.text(0), "Dragon bones — 252 XP")
        self.assertIn("Clean marrentill x2", row.toolTip(0))

        for width, height in ((720, 540), (900, 560)):
            dialog.resize(width, height)
            for _ in range(6):
                QApplication.processEvents()
            panel = dialog.findChild(QWidget, "prayerSkillPanel")
            tree = dialog.findChild(QTreeWidget, "prayerTargetTree")
            self.assertGreater(panel.height(), 0)
            self.assertGreater(tree.viewport().height(), 0)
            self.assertEqual(tree.horizontalScrollBar().maximum(), 0)
        dialog.deleteLater()

    def test_magic_surface_has_bank_alchemy_picker_and_locked_click_guard(self) -> None:
        from ankiscape.core.constants import MAGIC_SPELL_IMAGES

        pd = _make_player_data()
        pd["magic_level"] = 99
        pd["inventory"] = {"Rune platebody": 1, "Air rune": 3, "Fire rune": 1, "Law rune": 1}
        pd["farming_spell_patch"] = "falador_allotment_north"
        dialog = self._open(pd, current_skill="Magic")
        picker = dialog.findChild(QComboBox, "magicAlchemyItemCombo")
        farming_picker = dialog.findChild(QComboBox, "magicFarmingPatchCombo")
        tree = dialog.findChild(QTreeWidget, "magicTargetTree")
        self.assertIsNotNone(picker)
        self.assertIsNotNone(farming_picker)
        self.assertIsNotNone(tree)
        self.assertGreaterEqual(picker.findData("Rune platebody"), 0)
        self.assertEqual(farming_picker.currentData(), "falador_allotment_north")
        self.assertEqual(farming_picker.count(), 53)
        low_alchemy = _tree_row(tree, "low_alchemy")
        self.assertFalse(low_alchemy.icon(0).isNull())
        self.assertEqual(
            _icon_pixels(low_alchemy.icon(0)),
            _icon_pixels(
                self._ui._pixel_path_icon(
                    MAGIC_SPELL_IMAGES["low_alchemy"],
                    28,
                )
            ),
        )
        farming_picker.setCurrentIndex(farming_picker.findData("falador_allotment_south"))
        QApplication.processEvents()
        self.assertEqual(self._farming_spell_patch_calls[-1], "falador_allotment_south")
        locked = next(
            item for item in _tree_items(tree)
            if item.data(0, Qt.ItemDataRole.UserRole) == "kharyrll_teleport"
        )
        self.assertTrue(locked.isDisabled())
        before = list(self._magic_calls)
        tree.itemClicked.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._magic_calls, before)

    def test_magic_alchemy_picker_refreshes_target_readiness(self) -> None:
        pd = _make_player_data()
        pd.update({
            "magic_level": 99,
            "inventory": {"Rune platebody": 1, "Fire rune": 3, "Nature rune": 1},
            "magic_alchemy_item": "",
        })
        dialog = self._open(pd, current_skill="Magic")
        tree = dialog.findChild(QTreeWidget, "magicTargetTree")
        self.assertTrue(_tree_row(tree, "low_alchemy").isDisabled())

        picker = dialog.findChild(QComboBox, "magicAlchemyItemCombo")
        picker.setCurrentIndex(picker.findData("Rune platebody"))
        QApplication.processEvents()

        tree = dialog.findChild(QTreeWidget, "magicTargetTree")
        self.assertFalse(_tree_row(tree, "low_alchemy").isDisabled())

    def test_magic_surface_projects_livid_unlocks_and_real_consumer_blocks(self) -> None:
        pd = _make_player_data()
        pd.update({
            "magic_level": 99,
            "current_magic": "make_black_dragon_leather",
            "inventory": {
                "Astral rune": 100,
                "Law rune": 100,
                "Cosmic rune": 100,
                "Air rune": 100,
                "Water rune": 100,
                "Earth rune": 100,
                "Nature rune": 100,
                "Fire rune": 100,
                "Body rune": 100,
                "Black dragonhide": 5,
            },
            "quests": {
                "lunar_diplomacy": {"completed": True},
                "dream_mentor": {"completed": True},
                "my_arms_big_adventure": {"completed": True},
            },
            "livid_farm": {
                "unlocked_spells": [
                    "south_falador_teleport",
                    "repair_rune_pouch",
                    "north_ardougne_teleport",
                    "remote_farm",
                    "spiritualise_food",
                    "make_leather",
                ],
            },
        })
        dialog = self._open(pd, current_skill="Magic")
        tree = dialog.findChild(QTreeWidget, "magicTargetTree")

        self.assertFalse(_tree_row(tree, "south_falador_teleport").isDisabled())
        self.assertFalse(_tree_row(tree, "remote_farm").isDisabled())
        self.assertFalse(
            _tree_row(tree, "make_black_dragon_leather").isDisabled()
        )
        repair = _tree_row(tree, "repair_rune_pouch")
        spiritualise = _tree_row(tree, "spiritualise_food")
        self.assertTrue(repair.isDisabled())
        self.assertTrue(spiritualise.isDisabled())
        self.assertIn(
            "Pouch strengthening is not available yet",
            repair.toolTip(0),
        )
        self.assertIn(
            "Familiar food effects are not available yet",
            spiritualise.toolTip(0),
        )
        self.assertIn(
            "Destination: South Falador gate",
            _tree_row(tree, "south_falador_teleport").toolTip(0),
        )

        dialog.show()
        dialog.resize(720, 540)
        for _ in range(6):
            QApplication.processEvents()
        leather_row = _tree_row(tree, "make_black_dragon_leather")
        self.assertIn("Input: Black dragonhide x1–5", leather_row.toolTip(0))
        self.assertFalse(leather_row.icon(0).isNull())
        self.assertGreater(tree.viewport().height(), 0)
        self.assertEqual(tree.horizontalScrollBar().maximum(), 0)

    def test_construction_house_sheet_and_locked_click_guard(self) -> None:
        pd = _make_player_data()
        pd.update({
            "construction_level": 99, "construction_exp": 0,
            "house_owned": True, "house_rooms_bought": {"garden": True, "parlour": True},
            "house_servant": "", "house_built_flags": {}, "house_style": "basic_wood",
            "current_construction": "crude_wooden_chair", "inventory": {},
        })
        dialog = self._open(pd, current_skill="Construction")
        self.assertIsNotNone(dialog.findChild(QLabel, "constructionHouseSummary"))
        self.assertIsNotNone(dialog.findChild(QWidget, "constructionHouseRoomView"))
        tree = dialog.findChild(QTreeWidget, "constructionTargetTree")
        self.assertIsNotNone(tree)
        locked = next(item for item in _tree_items(tree) if item.data(0, Qt.ItemDataRole.UserRole) == "crude_wooden_chair")
        self.assertTrue(locked.isDisabled())
        before = list(self._construction_calls)
        tree.itemClicked.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._construction_calls, before)

    def test_construction_house_purchase_refreshes_the_sheet(self) -> None:
        pd = _make_player_data()
        pd.update({
            "construction_level": 99,
            "house_owned": False,
            "house_rooms_bought": {},
            "inventory": {"Coins": 1_000},
        })
        dialog = self._open(pd, current_skill="Construction")
        dialog.findChild(QPushButton, "constructionPurchaseHouseButton").click()
        QApplication.processEvents()

        self.assertTrue(pd["house_owned"])
        self.assertIsNone(dialog.findChild(QPushButton, "constructionPurchaseHouseButton"))
        self.assertIn("House · 2 rooms", dialog.findChild(QLabel, "constructionHouseSummary").text())

    def test_agility_reward_shops_report_failures_and_expose_every_ticket_bundle(self) -> None:
        # The ticket redemptions and the skillcape purchase moved from the
        # Agility panel's button grid to the Shop tab's reward-shops area; the
        # same commands run, now with a labelled home.
        pd = _make_player_data()
        pd["agility_level"] = 1
        dialog = self._open(pd, current_skill="Agility")
        dialog.show()
        QApplication.processEvents()
        _open_shop_tab(dialog)
        QApplication.processEvents()

        panel = dialog.findChild(QWidget, "shopAgilityRewardsPanel")
        self.assertIsNotNone(panel)
        labels = {button.text() for button in panel.findChildren(QPushButton)}
        for tickets in (1, 10, 25, 100, 1000):
            self.assertIn(f"Redeem {tickets} ticket{'s' if tickets != 1 else ''} for XP", labels)

        dialog.findChild(QPushButton, "shopAgilityCapeButton").click()
        QApplication.processEvents()
        status = dialog.findChild(QLabel, "shopAgilityRewardStatus")
        self.assertIsNotNone(status)
        self.assertEqual(status.text(), "Requires level 99 Agility")

    def test_agility_reward_shops_drive_every_relocated_row(self) -> None:
        # Each row that left the Agility panel is reachable from its new home
        # and forwards its exact command payload.
        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 99,
                "inventory": {
                    "Coins": 200_000,
                    "Agility arena ticket": 1_000,
                    "Pyramid top": 1,
                },
                "agility_lap_counts": {
                    "agile_top_unlocked": True,
                    "agile_legs_unlocked": True,
                },
            }
        )
        dialog = self._open(pd, current_skill="Agility")
        dialog.show()
        QApplication.processEvents()
        _open_shop_tab(dialog)
        QApplication.processEvents()

        panel = dialog.findChild(QWidget, "shopAgilityRewardsPanel")
        by_text = {
            button.text(): button for button in panel.findChildren(QPushButton)
        }

        cases = [
            ("Redeem 10 tickets for XP", ("redeem_brimhaven_xp", {"tickets": 10})),
            ("Toadflax (3 tickets)", ("redeem_brimhaven_item", {"tickets": 3})),
            ("Wergali (5 tickets)", ("redeem_brimhaven_item", {"tickets": 5})),
            ("Snapdragon (10 tickets)", ("redeem_brimhaven_item", {"tickets": 10})),
            ("Pirate's hook (800 tickets)", ("redeem_brimhaven_item", {"tickets": 800})),
            ("Claim Agile top", ("claim_agile_piece", {"piece": "Agile top"})),
            ("Claim Agile legs", ("claim_agile_piece", {"piece": "Agile legs"})),
            ("Agility cape · 99,000 coins", ("purchase_agility_cape", {})),
            ("Pyramid top · 1,000 coins", ("sell_pyramid_top", {"count": 1})),
        ]
        for label, expected_call in cases:
            button = by_text.get(label)
            self.assertIsNotNone(button, f"missing shop row: {label}")
            button.click()
            QApplication.processEvents()
            self.assertEqual(self._agility_command_calls[-1], expected_call, label)

        self.assertIn("Agile top", pd["inventory"])
        self.assertIn("Agility cape", pd["inventory"])
        self.assertEqual(pd["inventory"].get("Pyramid top", 0), 0)

    def test_surefooted_aura_activates_from_the_equipment_tab(self) -> None:
        # Auras have a cooldown, so they keep a control — in their own
        # inventory inside the Equipment tab, not on the skill panel.
        pd = _make_player_data()
        pd["inventory"] = {"Surefooted aura": 1}
        dialog = self._open(pd, current_skill="Agility")
        dialog.show()
        QApplication.processEvents()
        tabs = _find_main_tabs(dialog)
        index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Equipment")
        tabs.setCurrentIndex(index)
        QApplication.processEvents()

        panel = dialog.findChild(QWidget, "equipmentAuraPanel")
        self.assertIsNotNone(panel)
        self.assertTrue(panel.isVisibleTo(dialog))
        activate = dialog.findChild(QPushButton, "equipmentAuraActivateButton")
        self.assertIsNotNone(activate)
        self.assertTrue(activate.isEnabled())
        activate.click()
        QApplication.processEvents()

        self.assertEqual(
            self._agility_command_calls[-1], ("activate_surefooted", {})
        )
        charges = pd.get("agility_effect_charges", {})
        self.assertEqual(charges.get("surefooted_reviews"), 333)
        # The row rebuilds from the view: cooling down, so no second activation.
        activate = dialog.findChild(QPushButton, "equipmentAuraActivateButton")
        self.assertFalse(activate.isEnabled())

        # Without an aura the inventory stays out of the way entirely.
        pd2 = _make_player_data()
        dialog2 = self._open(pd2, current_skill="Agility")
        dialog2.show()
        QApplication.processEvents()
        tabs2 = _find_main_tabs(dialog2)
        tabs2.setCurrentIndex(
            next(i for i in range(tabs2.count()) if tabs2.tabText(i) == "Equipment")
        )
        QApplication.processEvents()
        panel2 = dialog2.findChild(QWidget, "equipmentAuraPanel")
        self.assertIsNotNone(panel2)
        self.assertFalse(panel2.isVisibleTo(dialog2))
        dialog2.deleteLater()

    def test_switching_from_brimhaven_ends_the_paid_stint(self) -> None:
        pd = _make_player_data()
        pd.update({
            "agility_level": 99,
            "current_agility": "brimhaven_arena",
            "agility_activity_state": {
                "brimhaven": {"stint_active": True, "activated": True}
            },
        })
        dialog = self._open(pd, current_skill="Agility")
        tree = dialog.findChild(QTreeWidget, "agilityTargetTree")
        tree.itemClicked.emit(_tree_row(tree, "burthorpe_course"), 0)
        QApplication.processEvents()

        self.assertEqual(pd["current_agility"], "burthorpe_course")
        self.assertNotIn("brimhaven", pd.get("agility_activity_state", {}))
        self.assertEqual(self._agility_command_calls[-1][0], "abandon")

    def test_stopping_agility_ends_the_brimhaven_stint(self) -> None:
        pd = _make_player_data()
        pd.update({
            "agility_level": 99,
            "current_agility": "brimhaven_arena",
            "agility_activity_state": {"brimhaven": {"stint_active": True}},
        })
        dialog = self._open(pd, current_skill="Agility")
        next(
            button for button in dialog.findChildren(QPushButton)
            if button.text() == "Stop training"
        ).click()
        QApplication.processEvents()

        self.assertNotIn("brimhaven", pd.get("agility_activity_state", {}))
        self.assertEqual(self._agility_command_calls[-1][0], "abandon")

    def test_thieving_target_change_refreshes_train_readiness(self) -> None:
        pd = _make_player_data()
        pd.update({"thieving_level": 1, "current_thieving": "wall_safe"})
        dialog = self._open(pd, current_skill="Mining")
        dialog.show()
        QApplication.processEvents()
        next(
            button for button in dialog.findChildren(QPushButton)
            if button.text() == "Support"
        ).click()
        QApplication.processEvents()
        skill_list = next(
            widget for widget in dialog.findChildren(QListWidget)
            if "Thieving" in [widget.item(i).text() for i in range(widget.count())]
        )
        skill_list.setCurrentRow(next(
            i for i in range(skill_list.count())
            if skill_list.item(i).text() == "Thieving"
        ))
        QApplication.processEvents()
        train = next(
            button for button in dialog.findChildren(QPushButton)
            if button.text() == "Train this skill" and button.isVisible()
        )
        self.assertFalse(train.isEnabled())

        tree = dialog.findChild(QTreeWidget, "thievingTargetTree")
        tree.itemClicked.emit(_tree_row(tree, "pickpocket_man"), 0)
        QApplication.processEvents()

        train = next(
            button for button in dialog.findChildren(QPushButton)
            if button.text() == "Train this skill" and button.isVisible()
        )
        self.assertTrue(train.isEnabled())

    def test_combat_magic_casual_controls_and_advanced_disclosure_fit_short_dialog(self) -> None:
        pd = _make_player_data()
        pd["equipment"] = {"weapon": "Staff of air"}
        dialog = self._open(pd)
        _open_equipment_tab(dialog)
        dialog.resize(900, 560)
        dialog.show()
        QApplication.processEvents()
        casual = dialog.findChild(QWidget, "combatMagicCasualControls")
        autocast = dialog.findChild(QComboBox, "combatSpellCombo")
        advanced_toggle = dialog.findChild(QToolButton, "combatAdvancedPresetToggle")
        advanced = dialog.findChild(QWidget, "combatAdvancedPresetPanel")
        self.assertTrue(casual.isVisible())
        self.assertTrue(autocast.isVisible())
        self.assertFalse(advanced.isVisible())
        advanced_toggle.click()
        QApplication.processEvents()
        self.assertTrue(advanced.isVisible())
        self.assertLessEqual(advanced_toggle.geometry().bottom(), dialog.height())
        self.assertIsNotNone(dialog.findChild(QCheckBox, "combatVengeanceCheck"))
        self.assertIsNotNone(dialog.findChild(QComboBox, "combatSpellbookSwapCombo"))

    def test_combat_prayer_controls_show_preset_picker_and_gate_curses(self) -> None:
        dialog = self._open(_make_player_data())
        preset = dialog.findChild(QComboBox, "combatPresetCombo")
        book = dialog.findChild(QComboBox, "combatPrayerBookCombo")
        self.assertIsNotNone(preset)
        self.assertEqual([preset.itemText(i) for i in range(preset.count())], ["Default"])
        curses_index = book.findData("curses")
        self.assertFalse(book.model().item(curses_index).isEnabled())
        self.assertIsNotNone(dialog.findChild(QPushButton, "combatSavePresetButton"))
        self.assertIsNotNone(dialog.findChild(QCheckBox, "combatPinPresetCheck"))

    def test_piety_gate_copy_names_and_enforces_defence_70(self) -> None:
        pd = _make_player_data()
        pd["prayer_level"] = 99
        pd["defense_level"] = 69
        pd["knight_waves"] = {"completed": True}
        dialog = self._open(pd)
        piety = dialog.findChild(QCheckBox, "combatPrayerCheck::piety")
        self.assertIsNotNone(piety)
        self.assertIn("70 Defence", piety.text())
        self.assertIn("70 Defence", piety.toolTip())
        self.assertFalse(piety.isEnabled())

        pd["defense_level"] = 70
        unlocked_dialog = self._open(pd)
        unlocked = unlocked_dialog.findChild(QCheckBox, "combatPrayerCheck::piety")
        self.assertTrue(unlocked.isEnabled())

    def test_chivalry_gate_copy_names_knight_waves(self) -> None:
        pd = _make_player_data()
        pd["prayer_level"] = 99
        pd["defense_level"] = 99
        pd["knight_waves"] = {"completed": False}
        dialog = self._open(pd)
        chivalry = dialog.findChild(QCheckBox, "combatPrayerCheck::chivalry")
        self.assertIsNotNone(chivalry)
        self.assertFalse(chivalry.isEnabled())
        self.assertIn("Knight Waves completion", chivalry.toolTip())

    def test_combat_prayer_checkbox_conflicts_are_reflected_in_widgets(self) -> None:
        pd = _make_player_data()
        pd["prayer_level"] = 99
        pd["knight_waves"] = {"completed": True}
        dialog = self._open(pd)
        clarity = dialog.findChild(QCheckBox, "combatPrayerCheck::clarity_of_thought")
        strength = dialog.findChild(QCheckBox, "combatPrayerCheck::burst_of_strength")
        eagle = dialog.findChild(QCheckBox, "combatPrayerCheck::eagle_eye")
        clarity.click()
        strength.click()
        eagle.click()
        QApplication.processEvents()
        checked = {check.objectName() for check in (clarity, strength, eagle) if check.isChecked()}
        self.assertEqual(checked, {"combatPrayerCheck::eagle_eye"})

    def test_court_cases_detail_is_compact_and_advanced_discloses_one_choice(self) -> None:
        from ankiscape.logic.court_cases_logic import (
            apply_court_case_review_pure,
            apply_court_cases_command_pure,
        )

        pd = _make_player_data()
        pd["quests"]["kings_ransom"] = {"completed": True}
        pd["attack_level"] = 65
        pd["defense_level"] = 65
        pd["current_utility"] = "court_cases"
        command_calls = []

        def court_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_court_cases_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_court_cases_command=court_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "court_cases"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "courtCasesPanel")
            if widget.isVisible()
        )
        icon = panel.findChild(QLabel, "courtCasesIcon")
        primary = panel.findChild(QPushButton, "courtCasesPrimaryButton")
        choice = panel.findChild(QComboBox, "courtCasesTrialChoiceCombo")
        self.assertTrue(panel.isVisible())
        self.assertEqual(icon.size().width(), 28)
        self.assertFalse(icon.pixmap().isNull())
        self.assertEqual(primary.text(), "Take the case")
        self.assertFalse(choice.isVisible())
        primary.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["court_cases"]["case_id"], "mugger")
        self.assertEqual(pd["current_utility"], "court_cases")
        dialog.close()

        advanced = _make_player_data()
        advanced["quests"]["kings_ransom"] = {"completed": True}
        advanced["attack_level"] = 65
        advanced["defense_level"] = 65
        advanced, ok, _ = apply_court_cases_command_pure(
            advanced,
            "enter",
            {"role": "defence", "automation_mode": "advanced"},
        )
        self.assertTrue(ok)
        for _ in range(4):
            advanced, _ = apply_court_case_review_pure(advanced)

        def advanced_command(action_id, payload):
            nonlocal advanced
            updated, action_ok, info = apply_court_cases_command_pure(
                advanced, action_id, payload
            )
            if action_ok:
                advanced.clear()
                advanced.update(updated)
            return {
                "ok": action_ok,
                "message": info.get("reason", ""),
                **info,
            }

        advanced_dialog = self._open(
            advanced,
            current_skill="Activities",
            on_court_cases_command=advanced_command,
        )
        advanced_dialog.show()
        QApplication.processEvents()
        advanced_tree = self._open_activities(advanced_dialog)
        advanced_item = next(
            row
            for row in _tree_items(advanced_tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "court_cases"
        )
        advanced_tree.itemClicked.emit(advanced_item, 0)
        QApplication.processEvents()
        advanced_panel = next(
            widget
            for widget in advanced_dialog.findChildren(QWidget, "courtCasesPanel")
            if widget.isVisible()
        )
        advanced_choice = advanced_panel.findChild(
            QComboBox, "courtCasesTrialChoiceCombo"
        )
        self.assertTrue(advanced_choice.isVisible())
        self.assertEqual(advanced_choice.count(), 3)
        self.assertEqual(
            advanced_choice.accessibleName(), "Next courtroom action"
        )

    def test_circus_detail_arms_a_performance_and_exposes_advanced_routine(self) -> None:
        from ankiscape.logic.circus_logic import apply_circus_command_pure

        pd = _make_player_data()
        pd["current_utility"] = "big_top_bonanza"
        command_calls = []

        def circus_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_circus_command_pure(pd, action_id, payload)
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_circus_command=circus_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "big_top_bonanza"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "circusPanel")
            if widget.isVisible()
        )
        icon = panel.findChild(QLabel, "circusIcon")
        performance = panel.findChild(QComboBox, "circusPerformanceCombo")
        strategy = panel.findChild(QComboBox, "circusStrategyCombo")
        mode = panel.findChild(QComboBox, "circusAutomationMode")
        primary = panel.findChild(QPushButton, "circusPrimaryButton")
        edit = panel.findChild(QPushButton, "circusEditRoutineButton")
        status = panel.findChild(QLabel, "circusStatusChip")
        reward_icons = [
            widget
            for widget in panel.findChildren(QLabel)
            if widget.objectName().startswith("circusRewardIcon::")
        ]

        self.assertEqual(icon.size().width(), 28)
        self.assertFalse(icon.pixmap().isNull())
        self.assertEqual(performance.count(), 6)
        self.assertIn(
            "locked",
            performance.itemText(performance.findData("fire_breathing")),
        )
        self.assertEqual(len(reward_icons), 5)
        self.assertTrue(all(not widget.pixmap().isNull() for widget in reward_icons))
        self.assertTrue(panel.findChild(QWidget, "circusReward::acrobat").isVisible())
        self.assertFalse(panel.findChild(QWidget, "circusReward::firemaker").isVisible())
        self.assertFalse(edit.isVisible())
        self.assertEqual(status.text(), "3 left this answered-card week")

        performance.setCurrentIndex(performance.findData("fire_breathing"))
        QApplication.processEvents()
        self.assertFalse(panel.findChild(QWidget, "circusReward::acrobat").isVisible())
        self.assertTrue(panel.findChild(QWidget, "circusReward::firemaker").isVisible())

        performance.setCurrentIndex(performance.findData("magic"))
        strategy.setCurrentIndex(strategy.findData("max_xp"))
        primary.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "set_policy")
        self.assertEqual(pd["circus"]["selected_performance"], "magic")
        self.assertEqual(pd["circus"]["strategies"]["magic"], "max_xp")

        pd["circus"]["used_week_by_performance"]["magic"] = 0
        performance.setCurrentIndex(performance.findData("agility"))
        performance.setCurrentIndex(performance.findData("magic"))
        QApplication.processEvents()
        self.assertIn("done this week", performance.currentText())
        self.assertFalse(primary.isEnabled())
        self.assertFalse(panel.findChild(QPushButton, "circusAbandonButton").isEnabled())

        performance.setCurrentIndex(performance.findData("agility"))
        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertTrue(edit.isVisible())
        before_dialog_count = len(self._captured)
        edit.click()
        QApplication.processEvents()
        self.assertEqual(len(self._captured), before_dialog_count + 1)
        routine_dialog = self._captured[-1]
        routine_combos = [
            combo
            for combo in routine_dialog.findChildren(QComboBox)
            if combo.objectName().startswith("circusRoutineTrick::")
        ]
        self.assertEqual(len(routine_combos), 10)
        self.assertEqual(routine_combos[0].findData(""), -1)
        self.assertGreaterEqual(routine_combos[1].findData(""), 0)
        dialog.close()

    def test_trouble_brewing_detail_enters_selects_and_buys_reward(self) -> None:
        from ankiscape.logic.trouble_brewing_logic import apply_trouble_brewing_command_pure

        pd = _make_player_data()
        pd["cooking_level"] = 40
        pd["quests"]["cabin_fever"]["completed"] = True
        pd["trouble_brewing_pieces_of_eight"] = 50
        command_calls = []

        def trouble_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_trouble_brewing_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_trouble_brewing_command=trouble_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "trouble_brewing"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "troubleBrewingPanel")
            if widget.isVisible()
        )
        icon = panel.findChild(QLabel, "troubleBrewingIcon")
        mode = panel.findChild(QComboBox, "troubleBrewingModeCombo")
        duty = panel.findChild(QComboBox, "troubleBrewingDutyCombo")
        primary = panel.findChild(QPushButton, "troubleBrewingPrimaryButton")
        progress = panel.findChild(QProgressBar, "troubleBrewingProgress")

        self.assertFalse(icon.pixmap().isNull())
        self.assertFalse(progress.isVisible())
        self.assertFalse(duty.isEnabled())
        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertTrue(duty.isEnabled())
        duty.setCurrentIndex(duty.findData("sabotage"))
        primary.click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "trouble_brewing")
        self.assertEqual(pd["trouble_brewing"]["duty"], "sabotage")
        self.assertTrue(progress.isVisible())
        self.assertEqual(primary.text(), "Selected for reviews")
        self.assertFalse(panel.findChild(QWidget, "troubleBrewingSavePlanButton").isEnabled())

        pd["trouble_brewing"] = {}
        pd["activity_session"] = {"active_id": ""}
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        buy = panel.findChild(QPushButton, "troubleBrewingBuyButton")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "buy_reward")
        self.assertEqual(pd["inventory"]["Blue tricorn hat"], 1)
        self.assertEqual(pd["trouble_brewing_pieces_of_eight"], 0)
        dialog.close()

    def test_castle_wars_detail_shop_plan_and_siege_actions_are_live(self) -> None:
        from ankiscape.data.castle_wars_data import CASTLE_WARS_BALLISTA_PARTS
        from ankiscape.logic.castle_wars_logic import apply_castle_wars_command_pure

        pd = _make_player_data()
        pd["castle_wars_tickets"] = 20
        pd["castle_wars_games_played"] = 500
        for item_name in CASTLE_WARS_BALLISTA_PARTS:
            pd["inventory"][item_name] = 1
        pd["inventory"]["Ballista ammo"] = 2
        pd["inventory"]["Castlewars chinchompa"] = 1
        command_calls = []

        def castle_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_castle_wars_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_castle_wars_command=castle_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "castle_wars"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "castleWarsPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "castleWarsIcon").pixmap().isNull())
        self.assertFalse(panel.findChild(QProgressBar, "castleWarsProgress").isVisible())

        before_dialogs = len(self._captured)
        panel.findChild(QPushButton, "castleWarsShopButton").click()
        QApplication.processEvents()
        self.assertEqual(len(self._captured), before_dialogs + 1)
        shop = self._captured[-1]
        reward = shop.findChild(QComboBox, "castleWarsRewardCombo")
        buy = shop.findChild(QPushButton, "castleWarsBuyButton")
        self.assertEqual(reward.currentData(), "basic_body")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Basic decorative platebody"], 1)
        self.assertEqual(pd["castle_wars_tickets"], 12)

        mode = panel.findChild(QComboBox, "castleWarsModeCombo")
        duty = panel.findChild(QComboBox, "castleWarsDutyCombo")
        team = panel.findChild(QComboBox, "castleWarsTeamCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        duty.setCurrentIndex(duty.findData("defend"))
        team.setCurrentIndex(team.findData("zamorak"))
        panel.findChild(QPushButton, "castleWarsPrimaryButton").click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "castle_wars")
        self.assertEqual(pd["castle_wars"]["duty"], "defend")
        self.assertEqual(pd["castle_wars"]["team"], "zamorak")
        self.assertTrue(panel.findChild(QProgressBar, "castleWarsProgress").isVisible())
        ballista = panel.findChild(QPushButton, "castleWarsBallistaButton")
        chinchompa = panel.findChild(QPushButton, "castleWarsChinchompaButton")
        self.assertTrue(ballista.isEnabled())
        self.assertTrue(chinchompa.isEnabled())
        ballista.click()
        chinchompa.click()
        QApplication.processEvents()
        self.assertTrue(pd["castle_wars"]["ballista_deployed"])
        self.assertEqual(pd["inventory"]["Castlewars chinchompa"], 0)
        dialog.close()

    def test_pest_control_detail_plan_shop_and_active_state_are_live(self) -> None:
        from ankiscape.logic.pest_control_logic import apply_pest_control_command_pure

        pd = _make_player_data()
        pd.update(
            {
                "attack_level": 40,
                "strength_level": 40,
                "defense_level": 40,
                "constitution_level": 40,
                "ranged_level": 40,
                "magic_level": 40,
                "prayer_level": 40,
                "summoning_level": 1,
                "pest_control_commendations": 20,
            }
        )
        command_calls = []

        def pest_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_pest_control_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_pest_control_command=pest_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "pest_control"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "pestControlPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "pestControlIcon").pixmap().isNull())
        self.assertFalse(panel.findChild(QProgressBar, "pestControlProgress").isVisible())

        buy = panel.findChild(QPushButton, "pestControlBuySealButton")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Void seal (8)"], 1)
        self.assertEqual(pd["pest_control_commendations"], 10)

        mode = panel.findChild(QComboBox, "pestControlModeCombo")
        lander = panel.findChild(QComboBox, "pestControlLanderCombo")
        duty = panel.findChild(QComboBox, "pestControlDutyCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        lander.setCurrentIndex(lander.findData("novice"))
        duty.setCurrentIndex(duty.findData("defend"))
        panel.findChild(QPushButton, "pestControlPrimaryButton").click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "pest_control")
        self.assertEqual(pd["pest_control"]["duty"], "defend")
        self.assertTrue(panel.findChild(QProgressBar, "pestControlProgress").isVisible())
        dialog.close()

    def test_soul_wars_detail_plan_shop_and_active_state_are_live(self) -> None:
        from ankiscape.logic.soul_wars_logic import apply_soul_wars_command_pure

        pd = _make_player_data()
        pd.update(
            {
                "attack_level": 40,
                "strength_level": 40,
                "defense_level": 40,
                "constitution_level": 40,
                "ranged_level": 40,
                "magic_level": 40,
                "prayer_level": 40,
                "slayer_level": 40,
                "summoning_level": 1,
                "combat_supply_loadout": {"food": {}},
                "soul_wars_zeal": 30,
            }
        )
        command_calls = []

        def soul_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_soul_wars_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_soul_wars_command=soul_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "soul_wars"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "soulWarsPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "soulWarsIcon").pixmap().isNull())
        progress = panel.findChild(QProgressBar, "soulWarsProgress")
        self.assertFalse(progress.isVisible())

        reward = panel.findChild(QComboBox, "soulWarsRewardCombo")
        buy = panel.findChild(QPushButton, "soulWarsBuyCharmsButton")
        self.assertEqual(reward.currentData(), "Gold charm")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "buy_charms")
        self.assertGreater(pd["inventory"]["Gold charm"], 0)
        self.assertEqual(pd["soul_wars_zeal"], 26)

        mode = panel.findChild(QComboBox, "soulWarsModeCombo")
        team = panel.findChild(QComboBox, "soulWarsTeamCombo")
        duty = panel.findChild(QComboBox, "soulWarsDutyCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        team.setCurrentIndex(team.findData("creation"))
        duty.setCurrentIndex(duty.findData("defend"))
        panel.findChild(QPushButton, "soulWarsPrimaryButton").click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "soul_wars")
        self.assertEqual(pd["soul_wars"]["team"], "creation")
        self.assertEqual(pd["soul_wars"]["duty"], "defend")
        self.assertTrue(progress.isVisible())
        dialog.close()

    def test_shades_of_mortton_detail_routes_plan_and_direct_actions(self) -> None:
        from ankiscape.logic.shades_of_mortton_logic import (
            apply_shades_of_mortton_command_pure,
            default_shades_of_mortton_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_shades_of_mortton_state_pure())
        pd.update(
            {
                "quests": {"shades_of_mortton": {"completed": True}},
                "firemaking_level": 80,
                "inventory": {
                    "Logs": 1,
                    "Sacred oil (4)": 1,
                    "Olive oil (4)": 1,
                    "Bronze key red": 1,
                    "Tinderbox": 1,
                },
            }
        )
        command_calls = []

        def mortton_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_shades_of_mortton_command_pure(
                pd,
                action_id,
                payload,
                rng=lambda: 0.0,
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_shades_of_mortton_command=mortton_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "shades_of_mortton"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "shadesOfMorttonPanel")
            if widget.isVisible()
        )
        self.assertFalse(
            panel.findChild(QLabel, "shadesOfMorttonIcon").pixmap().isNull()
        )
        pyre_combo = panel.findChild(QComboBox, "shadesOfMorttonPyreLogsCombo")
        self.assertFalse(pyre_combo.itemIcon(0).isNull())
        panel.findChild(QPushButton, "shadesOfMorttonMakePyreLogsButton").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "make_pyre_logs")
        self.assertEqual(pd["inventory"]["Pyre logs"], 1)

        key_combo = panel.findChild(QComboBox, "shadesOfMorttonKeyCombo")
        key_combo.setCurrentIndex(key_combo.findData("Bronze key red"))
        panel.findChild(QPushButton, "shadesOfMorttonOpenChestButton").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "open_bronze_chest")
        self.assertEqual(pd["shades_of_mortton_chests_opened"], 1)

        mode = panel.findChild(QComboBox, "shadesOfMorttonModeCombo")
        duty = panel.findChild(QComboBox, "shadesOfMorttonDutyCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        duty.setCurrentIndex(duty.findData("combat"))
        panel.findChild(QPushButton, "shadesOfMorttonPrimaryButton").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "shades_of_mortton")
        self.assertEqual(pd["shades_of_mortton_policy"]["duty"], "combat")

        pd["shades_of_mortton"].update(
            {"temple_repair": 99, "sanctity_tenths": 110, "altar_lit": False}
        )
        panel.findChild(QPushButton, "shadesOfMorttonSavePlanButton").click()
        QApplication.processEvents()
        light = panel.findChild(QPushButton, "shadesOfMorttonLightAltarButton")
        self.assertTrue(light.isEnabled())
        light.click()
        QApplication.processEvents()
        self.assertTrue(pd["shades_of_mortton"]["altar_lit"])
        dialog.close()

    def test_treasure_trails_card_reads_a_clue_and_opens_the_casket(self) -> None:
        from ankiscape.logic.treasure_trails_logic import (
            apply_treasure_trails_command_pure,
            default_treasure_trails_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_treasure_trails_state_pure())
        pd["inventory"] = {"Clue scroll (easy)": 1}
        pd["equipment"] = {}
        pd["activity_session"] = {"active_id": ""}
        command_calls = []

        def trails_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_treasure_trails_command_pure(
                pd, action_id, payload, lambda: 0.0
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_treasure_trails_command=trails_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "treasure_trail"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "treasureTrailsPanel")
            if widget.isVisible()
        )
        read_button = panel.findChild(QPushButton, "treasureTrailsPrimary")
        self.assertTrue(read_button.isEnabled())
        read_button.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("read", {"tier": "easy"}))
        self.assertIn(
            "Following an easy trail",
            panel.findChild(QLabel, "treasureTrailsSummary").text(),
        )
        self.assertFalse(read_button.isEnabled())

        # Finish the trail outside the panel, the way ordinary reviews would.
        from ankiscape.logic.treasure_trails_logic import (
            apply_treasure_trail_review_pure,
        )

        while pd["treasure_trail"]:
            updated, ok, _result = apply_treasure_trail_review_pure(pd)
            self.assertTrue(ok)
            pd.clear()
            pd.update(updated)
        # Leave the card and come back, the way a player does after reviewing.
        casket = panel.findChild(QPushButton, "treasureTrailsCasket")
        dialog.findChild(QPushButton, "activityChooseAnotherButton").click()
        QApplication.processEvents()
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        self.assertTrue(casket.isEnabled())
        casket.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "open_casket")
        self.assertNotIn("Casket (easy)", pd["inventory"])
        self.assertFalse(casket.isEnabled())
        dialog.close()

    def test_a_higher_tier_clue_shows_a_reason_instead_of_doing_nothing(self) -> None:
        from ankiscape.logic.treasure_trails_logic import (
            default_treasure_trails_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_treasure_trails_state_pure())
        pd["inventory"] = {"Clue scroll (hard)": 1}
        pd["equipment"] = {}
        pd["activity_session"] = {"active_id": ""}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_treasure_trails_command=lambda *_args: {"ok": True},
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "treasure_trail"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "treasureTrailsPanel")
            if widget.isVisible()
        )
        self.assertFalse(
            panel.findChild(QPushButton, "treasureTrailsPrimary").isEnabled()
        )
        self.assertIn(
            "not built yet", panel.findChild(QLabel, "treasureTrailsStep").text()
        )
        self.assertIn(
            "already have a clue scroll",
            panel.findChild(QLabel, "treasureTrailsSummary").text(),
        )
        dialog.close()

    def test_challenges_tab_renders_the_queue_and_routes_every_command(self) -> None:
        from ankiscape.data.daily_challenges_data import (
            DAILY_CHALLENGE_ACTIVE_LIMIT,
            DAILY_CHALLENGE_DATA,
        )
        from ankiscape.logic.daily_challenges_logic import (
            apply_daily_challenges_command_pure,
            default_daily_challenges_state_pure,
        )

        spec = DAILY_CHALLENGE_DATA["mining_copper_ore"]
        pd = _make_player_data()
        pd.update(default_daily_challenges_state_pure())
        pd["mining_level"] = 99
        pd["mining_exp"] = 0.0
        pd["inventory"] = {"Copper ore": int(spec["required"])}
        pd["daily_challenges"] = [
            {
                "instance_id": "mining_copper_ore-1",
                "challenge_id": "mining_copper_ore",
                "day": 1,
                "progress": int(spec["required"]),
                "credited": {"Copper ore": int(spec["required"])},
            }
        ]
        command_calls = []

        def challenges_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_daily_challenges_command_pure(
                pd, action_id, payload, {"Copper ore": 8}
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Mining",
            on_daily_challenges_command=challenges_command,
        )
        dialog.show()
        QApplication.processEvents()
        _open_challenges_tab(dialog)
        page = dialog.findChild(QWidget, "challengesTab")
        summary = page.findChild(QLabel, "challengeSummaryLabel")
        self.assertIn(f"1/{DAILY_CHALLENGE_ACTIVE_LIMIT} slots", summary.text())

        tree = page.findChild(QTreeWidget, "challengeTree")
        self.assertEqual(tree.topLevelItemCount(), 1)
        self.assertEqual(
            tree.topLevelItem(0).text(2), f"{int(spec['required'])}/{int(spec['required'])}"
        )

        page.findChild(QPushButton, "challengePinButton").click()
        QApplication.processEvents()
        self.assertEqual(
            command_calls[-1], ("pin", {"instance_id": "mining_copper_ore-1"})
        )
        self.assertIn("(pinned)", tree.topLevelItem(0).text(0))

        claim = page.findChild(QPushButton, "challengeClaimButton")
        self.assertTrue(claim.isEnabled())
        claim.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "claim")
        self.assertEqual(tree.topLevelItemCount(), 0)
        self.assertEqual(pd["mining_exp"], float(spec["reward_xp"]))

        bag = page.findChild(QPushButton, "challengeBagButton")
        self.assertTrue(bag.isEnabled())
        bag.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "open_bag")
        self.assertEqual(pd["inventory"]["Coins"], int(spec["required"]) * 8)
        self.assertFalse(bag.isEnabled())
        dialog.close()

    def test_a_finished_hand_in_without_its_items_shows_the_reason_and_stays_disabled(self) -> None:
        from ankiscape.data.daily_challenges_data import DAILY_CHALLENGE_DATA
        from ankiscape.logic.daily_challenges_logic import (
            default_daily_challenges_state_pure,
        )

        spec = DAILY_CHALLENGE_DATA["cooking_chicken"]
        pd = _make_player_data()
        pd.update(default_daily_challenges_state_pure())
        pd["inventory"] = {}
        pd["daily_challenges"] = [
            {
                "instance_id": "cooking_chicken-1",
                "challenge_id": "cooking_chicken",
                "day": 1,
                "progress": int(spec["required"]),
                "credited": {"Cooked chicken": int(spec["required"])},
            }
        ]

        dialog = self._open(
            pd,
            current_skill="Mining",
            on_daily_challenges_command=lambda *_args: {"ok": True},
        )
        dialog.show()
        QApplication.processEvents()
        _open_challenges_tab(dialog)
        page = dialog.findChild(QWidget, "challengesTab")
        claim = page.findChild(QPushButton, "challengeClaimButton")
        self.assertFalse(claim.isEnabled())
        self.assertIn("3 Cooked chicken", claim.toolTip())
        dialog.close()

    def test_tzhaar_fight_pit_detail_routes_policy_entry_and_active_state(self) -> None:
        from ankiscape.logic.tzhaar_fight_pit_logic import (
            apply_tzhaar_fight_pit_command_pure,
            default_tzhaar_fight_pit_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_tzhaar_fight_pit_state_pure())
        pd.update(
            {
                "attack_level": 60,
                "strength_level": 60,
                "defense_level": 60,
                "constitution_level": 60,
                "current_combat_target": "chicken",
                "combat_encounter": {},
                "activity_session": {"active_id": ""},
            }
        )
        command_calls = []

        def fight_pit_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_tzhaar_fight_pit_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_tzhaar_fight_pit_command=fight_pit_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "tzhaar_fight_pit"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "fightPitPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "fightPitIcon").pixmap().isNull())
        policy = panel.findChild(QComboBox, "fightPitPolicy")
        policy.setCurrentIndex(policy.findData("aggressive"))
        panel.findChild(QPushButton, "fightPitSavePlan").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("set_policy", {"policy": "aggressive"}))
        panel.findChild(QPushButton, "fightPitPrimary").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "tzhaar_fight_pit")
        self.assertEqual(pd["tzhaar_fight_pit"]["policy"], "aggressive")
        self.assertIn("3 rivals remain", panel.findChild(QLabel, "fightPitSummary").text())
        dialog.close()

    def test_duel_arena_detail_configures_rules_and_shows_active_and_result_state(self) -> None:
        from ankiscape.logic.duel_arena_logic import (
            apply_duel_arena_command_pure,
            apply_duel_arena_review_pure,
            default_duel_arena_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_duel_arena_state_pure())
        pd.update(
            {
                "attack_level": 60,
                "strength_level": 60,
                "defense_level": 60,
                "constitution_level": 60,
                "ranged_level": 40,
                "magic_level": 40,
                "prayer_level": 43,
                "summoning_level": 1,
                "current_combat_target": "chicken",
                "combat_encounter": {},
                "activity_session": {"active_id": ""},
            }
        )
        command_calls = []

        def duel_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_duel_arena_command_pure(
                pd,
                action_id,
                payload,
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def open_panel():
            dialog = self._open(
                pd,
                current_skill="Activities",
                on_duel_arena_command=duel_command,
            )
            dialog.show()
            QApplication.processEvents()
            tree = self._open_activities(dialog)
            item = next(
                row
                for row in _tree_items(tree)
                if row.data(0, Qt.ItemDataRole.UserRole) == "duel_arena"
            )
            tree.itemClicked.emit(item, 0)
            QApplication.processEvents()
            panel = next(
                widget
                for widget in dialog.findChildren(QWidget, "duelArenaPanel")
                if widget.isVisible()
            )
            return dialog, panel

        dialog, panel = open_panel()
        self.assertFalse(panel.findChild(QLabel, "duelArenaIcon").pixmap().isNull())
        cap_claim = panel.findChild(QPushButton, "duelArenaClaimCap")
        self.assertTrue(cap_claim.isVisible())
        cap_claim.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "claim_cap")
        self.assertEqual(pd["inventory"]["Duellist's cap (tier 1)"], 1)
        self.assertFalse(cap_claim.isVisible())
        checks = panel.findChildren(QCheckBox)
        self.assertEqual(
            len([check for check in checks if check.objectName().startswith("duelArenaRule_")]),
            11,
        )
        panel.findChild(QCheckBox, "duelArenaRule_no_food").setChecked(True)
        panel.findChild(QCheckBox, "duelArenaRule_no_prayer").setChecked(True)
        panel.findChild(QCheckBox, "duelArenaRule_no_forfeit").setChecked(True)
        panel.findChild(QPushButton, "duelArenaSaveRules").click()
        QApplication.processEvents()
        self.assertEqual(
            command_calls[-1],
            (
                "set_rules",
                {"rule_ids": ["no_forfeit", "no_food", "no_prayer"]},
            ),
        )
        panel.findChild(QPushButton, "duelArenaPrimary").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "duel_arena")
        self.assertIn(
            "score 0-0",
            panel.findChild(QLabel, "duelArenaSummary").text(),
        )
        self.assertEqual(
            panel.findChild(QLabel, "duelArenaStatusChip").text(),
            "DUEL ACTIVE",
        )
        self.assertFalse(
            panel.findChild(QPushButton, "duelArenaAbandon").isVisible()
        )
        dialog.close()

        for _ in range(3):
            updated, ok, result = apply_duel_arena_review_pure(pd, lambda: 0.0)
            self.assertTrue(ok)
            pd.clear()
            pd.update(updated)
        self.assertEqual(result["outcome"], "win")

        result_dialog, result_panel = open_panel()
        self.assertIn(
            "Duel won",
            result_panel.findChild(QLabel, "duelArenaSummary").text(),
        )
        self.assertIn(
            "1 wins",
            result_panel.findChild(QLabel, "duelArenaCapProgress").text(),
        )
        result_dialog.close()

    def test_clan_wars_detail_offers_both_portals_and_warns_before_the_red_one(self) -> None:
        from ankiscape.data.clan_wars_data import (
            CLAN_WARS_MODES,
            CLAN_WARS_RED_MODE,
            CLAN_WARS_WHITE_MODE,
        )
        from ankiscape.logic.clan_wars_logic import (
            apply_clan_wars_command_pure,
            default_clan_wars_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_clan_wars_state_pure())
        pd.update(
            {
                "attack_level": 60,
                "strength_level": 60,
                "defense_level": 60,
                "constitution_level": 60,
                "prayer_level": 43,
                "current_combat_target": "chicken",
                "combat_encounter": {},
                "activity_session": {"active_id": ""},
            }
        )
        command_calls = []

        def clan_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_clan_wars_command_pure(
                pd,
                action_id,
                payload,
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def open_panel():
            dialog = self._open(
                pd,
                current_skill="Activities",
                on_clan_wars_command=clan_command,
            )
            dialog.show()
            QApplication.processEvents()
            tree = self._open_activities(dialog)
            item = next(
                row
                for row in _tree_items(tree)
                if row.data(0, Qt.ItemDataRole.UserRole) == "clan_wars"
            )
            tree.itemClicked.emit(item, 0)
            QApplication.processEvents()
            panel = next(
                widget
                for widget in dialog.findChildren(QWidget, "clanWarsPanel")
                if widget.isVisible()
            )
            return dialog, panel

        dialog, panel = open_panel()
        self.assertFalse(panel.findChild(QLabel, "clanWarsIcon").pixmap().isNull())
        combo = panel.findChild(QComboBox, "clanWarsModeCombo")
        self.assertEqual(combo.count(), len(CLAN_WARS_MODES))
        self.assertEqual(combo.currentData(), CLAN_WARS_WHITE_MODE)
        status = panel.findChild(QLabel, "clanWarsStatusChip")
        warning = panel.findChild(QLabel, "clanWarsWarning")
        self.assertEqual(status.text(), "SAFE")
        self.assertFalse(warning.isVisible())

        combo.setCurrentIndex(combo.findData(CLAN_WARS_RED_MODE))
        QApplication.processEvents()
        self.assertEqual(status.text(), "DANGEROUS")
        self.assertTrue(warning.isVisible())
        self.assertIn("destroyed", warning.text())

        # Declining the red-portal confirmation must not enter anything.
        original_question = self._ui.QMessageBox.question
        try:
            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.No
            )
            panel.findChild(QPushButton, "clanWarsPrimaryButton").click()
            QApplication.processEvents()
            self.assertEqual(command_calls, [])
            self.assertEqual(pd["clan_wars"], {})

            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.Yes
            )
            panel.findChild(QPushButton, "clanWarsPrimaryButton").click()
            QApplication.processEvents()
        finally:
            self._ui.QMessageBox.question = original_question
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["clan_wars"]["mode"], CLAN_WARS_RED_MODE)
        dialog.close()

        active_dialog, active_panel = open_panel()
        self.assertEqual(
            active_panel.findChild(QLabel, "clanWarsStatusChip").text(),
            "ACTIVE · DANGEROUS",
        )
        # The dangerous portal forbids teleport escape, and the panel must show
        # that lock rather than deciding it for itself.
        teleport = active_panel.findChild(QPushButton, "clanWarsTeleportButton")
        self.assertTrue(teleport.isVisible())
        self.assertFalse(teleport.isEnabled())
        self.assertIn("forbidden", teleport.toolTip())
        self.assertTrue(
            active_panel.findChild(QPushButton, "clanWarsLeaveButton").isVisible()
        )
        active_combo = active_panel.findChild(QComboBox, "clanWarsModeCombo")
        self.assertEqual(active_combo.count(), 1)
        self.assertFalse(active_combo.isEnabled())
        progress = active_panel.findChild(QProgressBar, "clanWarsProgress")
        self.assertEqual(progress.value(), 0)
        self.assertIn("successful reviews", progress.format())
        active_dialog.close()

    def test_shattered_heart_card_claims_the_real_bag_and_updates_policy(self) -> None:
        from ankiscape.data.shattered_heart_data import SHATTERED_HEART_BAG_ITEM
        from ankiscape.logic.shattered_heart_logic import (
            apply_shattered_heart_command_pure,
            default_shattered_heart_state_pure,
        )

        pd = _make_player_data()
        pd["shattered_heart"] = default_shattered_heart_state_pure()
        pd["shop_market_clock"] = {"answered_cards": 0}
        pd["house_owned"] = False
        pd["house_rooms_bought"] = {}
        command_calls = []

        def shattered_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_shattered_heart_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_shattered_heart_command=shattered_command,
        )
        dialog.show()
        dialog.resize(760, 560)
        for _ in range(4):
            QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "shattered_heart"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "shatteredHeartPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "shatteredHeartIcon").pixmap().isNull())
        panel.findChild(QPushButton, "shatteredHeartClaimBagButton").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "claim_bag")
        self.assertEqual(pd["inventory"][SHATTERED_HEART_BAG_ITEM], 1)
        self.assertTrue(
            panel.findChild(QPushButton, "shatteredHeartDestroyBagButton").isVisible()
        )
        discard = panel.findChild(QCheckBox, "shatteredHeartAutoDiscardCheck")
        discard.setChecked(True)
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("set_auto_discard", {"enabled": True}))
        self.assertTrue(pd["shattered_heart"]["auto_discard"])
        self.assertLessEqual(panel.sizeHint().height(), 560)
        dialog.close()

    def test_barbarian_assault_tutorial_shop_plan_and_active_state_are_live(self) -> None:
        from ankiscape.logic.barbarian_assault_logic import apply_barbarian_assault_command_pure

        pd = _make_player_data()
        pd["barbarian_assault_points"] = {
            role_id: 100
            for role_id in ("attacker", "collector", "defender", "healer")
        }
        command_calls = []

        def barbarian_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_barbarian_assault_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_barbarian_assault_command=barbarian_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "barbarian_assault"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "barbarianAssaultPanel")
            if widget.isVisible()
        )
        self.assertFalse(
            panel.findChild(QLabel, "barbarianAssaultIcon").pixmap().isNull()
        )
        progress = panel.findChild(QProgressBar, "barbarianAssaultProgress")
        self.assertFalse(progress.isVisible())

        tutorial = panel.findChild(QPushButton, "barbarianAssaultTutorialButton")
        self.assertTrue(tutorial.isVisible())
        tutorial.click()
        QApplication.processEvents()
        self.assertTrue(pd["barbarian_assault_tutorial_complete"])

        buy = panel.findChild(QPushButton, "barbarianAssaultBuyBootsButton")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Runner boots"], 1)
        self.assertEqual(set(pd["barbarian_assault_points"].values()), {0})

        mode = panel.findChild(QComboBox, "barbarianAssaultModeCombo")
        role = panel.findChild(QComboBox, "barbarianAssaultRoleCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        role.setCurrentIndex(role.findData("defender"))
        panel.findChild(QPushButton, "barbarianAssaultPrimaryButton").click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "barbarian_assault")
        self.assertEqual(pd["barbarian_assault"]["role"], "defender")
        self.assertTrue(progress.isVisible())
        dialog.close()

    def test_stronghold_player_safety_chest_lamp_and_combat_entry_are_live(self) -> None:
        from aqt.qt import QInputDialog
        from ankiscape.logic.stronghold_player_safety_logic import (
            apply_stronghold_player_safety_command_pure,
        )

        pd = _make_player_data()
        pd["stronghold_player_safety"] = {
            "version": 1,
            "stage": 3,
            "crevice_unlocked": True,
            "chest_claimed": False,
            "lamps_remaining": 0,
            "safety_first_emote_unlocked": False,
            "last_result": "Reached the reward passage.",
        }

        def stronghold_command(action_id, payload):
            updated, ok, info = apply_stronghold_player_safety_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        saved_skills = []
        dialog = self._open(
            pd,
            current_skill="Activities",
            on_stronghold_player_safety_command=stronghold_command,
            on_save_skill=saved_skills.append,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole)
            == "stronghold_player_safety"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(
                QWidget, "strongholdPlayerSafetyPanel"
            )
            if widget.isVisible()
        )
        self.assertFalse(
            panel.findChild(QLabel, "strongholdPlayerSafetyIcon").pixmap().isNull()
        )
        self.assertEqual(
            panel.findChild(QProgressBar, "strongholdPlayerSafetyProgress").value(),
            3,
        )
        fight = panel.findChild(QPushButton, "strongholdPlayerSafetyFightButton")
        self.assertTrue(fight.isVisible())
        self.assertTrue(fight.isEnabled())

        panel.findChild(QPushButton, "strongholdPlayerSafetyClaimButton").click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Coins"], 10_000)
        self.assertEqual(pd["inventory"]["Safety gloves"], 1)
        lamp = panel.findChild(QPushButton, "strongholdPlayerSafetyLampButton")
        self.assertEqual(lamp.text(), "Use 500-XP lamp (2)")
        with patch.object(
            QInputDialog,
            "getItem",
            return_value=("Agility", True),
        ):
            lamp.click()
        QApplication.processEvents()
        self.assertEqual(pd["agility_exp"], 1500.0)
        self.assertEqual(lamp.text(), "Use 500-XP lamp (1)")
        fight.click()
        QApplication.processEvents()
        self.assertEqual(saved_skills, ["Combat"])
        self.assertEqual(pd["current_combat_target"], "cockroach_soldier")
        self.assertEqual(pd["combat_encounter"]["enemy_lifepoints"], 960)

    def test_varrock_museum_landmark_card_routes_claims_and_kit(self) -> None:
        from ankiscape.logic.varrock_museum_logic import apply_varrock_museum_command_pure

        pd = _make_player_data()

        def museum_command(action_id, payload):
            updated, ok, info = apply_varrock_museum_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_varrock_museum_command=museum_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "varrock_museum"
        )
        self.assertEqual(
            item.parent().data(0, Qt.ItemDataRole.UserRole),
            "__utility_group__:landmarks",
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "varrockMuseumPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "varrockMuseumIcon").pixmap().isNull())
        self.assertIn("0/183 Kudos", panel.findChild(QLabel, "varrockMuseumSummary").text())

        route = panel.findChild(QComboBox, "varrockMuseumRouteCombo")
        route.setCurrentIndex(route.findData("cleaning"))
        QApplication.processEvents()
        self.assertEqual(pd["varrock_museum"]["route"], "cleaning")
        self.assertIn(
            "complete The Dig Site",
            panel.findChild(QLabel, "varrockMuseumNote").text(),
        )

        panel.findChild(QPushButton, "varrockMuseumKitButton").click()
        QApplication.processEvents()
        self.assertEqual(
            set(pd["inventory"]),
            {"Trowel", "Rock pick", "Specimen brush", "Leather gloves", "Leather boots"},
        )

        route.setCurrentIndex(route.findData("quiz"))
        QApplication.processEvents()
        panel.findChild(QPushButton, "varrockMuseumPrimaryButton").click()
        QApplication.processEvents()
        self.assertEqual(self._utility_calls[-1], "varrock_museum")
        dialog.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
