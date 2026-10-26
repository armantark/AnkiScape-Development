"""Offscreen Qt behavior tests for the Skills-hub navigation in ``show_main_menu``.

Why this exists: iterating on the menu by restarting Anki is slow and blind.
This harness builds the *real* dialog headlessly (QT_QPA_PLATFORM=offscreen)
against a pip-installed ``aqt`` and drives the widgets directly, so a broken
"click skill -> panel updates" contract fails here in milliseconds instead of
being discovered by hand after a restart.

Run with the Qt venv:
    source .venv-qt/bin/activate
    QT_QPA_PLATFORM=offscreen python run_tests.py tests.main_menu
"""
from __future__ import annotations

import copy
import os
import re
import sys
import unittest
from dataclasses import replace
from functools import cached_property
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ADDON_DIR = os.path.dirname(_THIS_DIR)
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

try:
    import aqt  # noqa: F401
    from aqt.qt import QApplication, QAbstractItemView, QCheckBox, QColor, QComboBox, QDialog, QEvent, QLabel, QLineEdit, QListWidget, QMainWindow, QMenu, QMessageBox, QObject, QPalette, QPoint, QPushButton, QIcon, QImage, QProgressBar, QScrollArea, QSize, QStackedWidget, QTabWidget, QTimer, QToolButton, QTextBrowser, QSpinBox, Qt, QTreeWidget, QTreeWidgetItem, QWidget, QModelIndex
    from PyQt6.QtTest import QSignalSpy, QTest
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


def _find_bank_grid(dialog: "QDialog") -> "QWidget":
    bank_grid = dialog.findChild(QWidget, "bankGrid")
    if bank_grid is None:
        _open_bank_tab(dialog)
        bank_grid = dialog.findChild(QWidget, "bankGrid")
    if bank_grid is not None:
        return bank_grid
    raise AssertionError("Bank item grid not found")


def _bank_grid_buttons(dialog: "QDialog") -> list["QToolButton"]:
    grid = _find_bank_grid(dialog)
    return [
        button
        for button in grid.findChildren(QToolButton)
        if button.objectName().startswith("bankGridItem::")
    ]


def _bank_grid_button(dialog: "QDialog", item_name: str) -> "QToolButton":
    button = _find_bank_grid(dialog).findChild(
        QToolButton, f"bankGridItem::{item_name}"
    )
    if button is None:
        raise AssertionError(f"Bank grid item {item_name!r} not found")
    return button


def _bank_grid_texts(dialog: "QDialog") -> list[str]:
    grid = _find_bank_grid(dialog)
    texts = [
        label.text().strip("— ")
        for label in grid.findChildren(QLabel)
        if label.objectName().startswith("bankCategoryHeader::")
        or label.objectName() == "bankGridEmpty"
    ]
    texts.extend(
        f"{button.property('bankItemName')} x{int(button.property('bankQuantity'))}"
        for button in _bank_grid_buttons(dialog)
    )
    return texts


def _find_gear_list(dialog: "QDialog") -> "QListWidget":
    """The gear panel is the separate (non-striped) list below the inventory."""
    gear_list = dialog.findChild(QListWidget, "gearList")
    if gear_list is None:
        _open_bank_tab(dialog)
        gear_list = dialog.findChild(QListWidget, "gearList")
    if gear_list is not None:
        return gear_list
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


def _open_reward_target(dialog: "QDialog", target_id: str) -> "QWidget":
    _open_shop_tab(dialog)
    rewards = _find_named_list(dialog, "rewardShopTargetList")
    item = next(
        rewards.item(index)
        for index in range(rewards.count())
        if (
            isinstance(rewards.item(index).data(Qt.ItemDataRole.UserRole), dict)
            and rewards.item(index).data(Qt.ItemDataRole.UserRole).get("target_id")
            == target_id
        )
    )
    rewards.setCurrentItem(item)
    QApplication.processEvents()
    page = dialog.findChild(QWidget, f"rewardShopPage_{target_id}")
    if page is None:
        raise AssertionError(f"reward target {target_id!r} has no page")
    return page


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


def _open_collections_tab(dialog: "QDialog") -> None:
    """Mandatory before touching deferred Collections widgets."""
    tabs = _find_main_tabs(dialog)
    index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Collections")
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
    if tabs.currentIndex() == index and dialog.findChild(QWidget, "bankGrid") is None:
        tabs.setCurrentIndex(0)
        QApplication.processEvents()
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


class _FakeCol:
    """A dict-backed profile config, for tests that persist menu preferences."""

    def __init__(self) -> None:
        self._cfg: dict = {}
        # Settings suggests a world-day length from an empty review log.
        self.sched = SimpleNamespace(day_cutoff=0)
        self.db = SimpleNamespace(all=lambda *_query: [])

    def get_config(self, key, default=None):
        return self._cfg.get(key, default)

    def set_config(self, key, value):
        self._cfg[key] = value


if __name__ == "__main__":
    unittest.main(verbosity=2)
