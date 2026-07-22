#!/usr/bin/env python3
"""Render one real Skills-hub panel for repeatable visual review."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import (  # type: ignore
    QAbstractItemView,
    QApplication,
    QColor,
    QListWidget,
    QPalette,
    QPushButton,
    QToolButton,
    Qt,
    QTreeWidget,
    QTreeWidgetItem,
)

from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data
from wicked_hood_logic import apply_wicked_hood_command_pure


def _dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(238, 238, 238))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.Text, QColor(238, 238, 238))
    palette.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(238, 238, 238))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(55, 130, 70))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    return palette


def _light_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(28, 28, 28))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(242, 242, 242))
    palette.setColor(QPalette.ColorRole.Text, QColor(28, 28, 28))
    palette.setColor(QPalette.ColorRole.Button, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(28, 28, 28))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(74, 143, 84))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    return palette


def _inventory(values: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        item_name, separator, raw_count = value.rpartition("=")
        if not separator or not item_name:
            raise ValueError(f"Inventory entry must be ITEM=COUNT: {value!r}")
        result[item_name] = max(int(raw_count), 0)
    return result


def _tree_items(tree: QTreeWidget) -> list[QTreeWidgetItem]:
    items: list[QTreeWidgetItem] = []

    def visit(item: QTreeWidgetItem) -> None:
        items.append(item)
        for index in range(item.childCount()):
            visit(item.child(index))

    for index in range(tree.topLevelItemCount()):
        visit(tree.topLevelItem(index))
    return items


def render(args: argparse.Namespace) -> Path:
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(methodName="test_fletching_is_selectable_and_shows_grouped_target_tree")
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(
        _dark_palette() if args.theme == "dark" else _light_palette()
    )

    player_data = _make_player_data()
    if args.skill:
        player_data[f"{args.skill.casefold()}_level"] = args.level
    player_data["inventory"].update(_inventory(args.inventory))
    for quest_id in args.complete_quest:
        player_data.setdefault("quests", {}).setdefault(quest_id, {})[
            "completed"
        ] = True
    if args.target_key and args.target_id:
        player_data[args.target_key] = args.target_id
    if args.claim_wicked_hood:
        player_data.setdefault("claims", {})["wicked_hood"] = {"claimed": True}
        player_data.setdefault("inventory", {})["Wicked hood"] = 1
    if args.equip_wicked_hood:
        player_data.setdefault("equipment", {})["head"] = "Wicked hood"
    if args.feed_altar:
        player_data.setdefault("wicked_hood", {})["fed_altars"] = sorted(
            set(args.feed_altar)
        )

    def _wicked_hood_command(action_id: str, payload: dict) -> dict:
        updated, ok, info = apply_wicked_hood_command_pure(
            player_data, action_id, payload
        )
        if ok:
            player_data.clear()
            player_data.update(updated)
        return {
            "ok": ok,
            "message": str(info.get("message", info.get("reason", ""))),
            **info,
        }

    dialog = case._open(
        player_data,
        on_wicked_hood_command=_wicked_hood_command,
    )
    category = next(
        (
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == args.category
        ),
        None,
    )
    if category is None:
        raise RuntimeError(f"Category button {args.category!r} was not found")
    category.click()
    app.processEvents()

    if args.skill:
        skill_list = next(
            (
                widget
                for widget in dialog.findChildren(QListWidget)
                if widget.isVisibleTo(dialog)
                and any(
                    widget.item(index).text() == args.skill
                    for index in range(widget.count())
                )
            ),
            None,
        )
        if skill_list is None:
            raise RuntimeError(f"Skill row {args.skill!r} was not found")
        skill_row = next(
            index
            for index in range(skill_list.count())
            if skill_list.item(index).text() == args.skill
        )
        skill_list.setCurrentRow(skill_row)
        skill_list.itemClicked.emit(skill_list.item(skill_row))
        app.processEvents()

    if args.target_id:
        target_selected = False
        for tree in dialog.findChildren(QTreeWidget):
            target_item = next(
                (
                    item
                    for item in _tree_items(tree)
                    if item.data(0, Qt.ItemDataRole.UserRole) == args.target_id
                ),
                None,
            )
            if target_item is None:
                continue
            parent = target_item.parent()
            while parent is not None:
                parent.setExpanded(True)
                parent = parent.parent()
            tree.setCurrentItem(target_item)
            tree.scrollToItem(
                target_item,
                QAbstractItemView.ScrollHint.PositionAtCenter,
            )
            target_selected = True
            break
        if not target_selected:
            for item_list in dialog.findChildren(QListWidget):
                target_row = next(
                    (
                        index
                        for index in range(item_list.count())
                        if item_list.item(index).data(Qt.ItemDataRole.UserRole)
                        == args.target_id
                    ),
                    None,
                )
                if target_row is None:
                    continue
                item_list.setCurrentRow(target_row)
                item_list.scrollToItem(
                    item_list.item(target_row),
                    QAbstractItemView.ScrollHint.PositionAtCenter,
                )
                target_selected = True
                break
        if not target_selected:
            raise RuntimeError(f"Target row {args.target_id!r} was not found")

    dialog.show()
    dialog.resize(args.width, args.height)
    for _ in range(8):
        app.processEvents()
    if args.open_details:
        details = dialog.findChild(QToolButton, "targetDetailsToggle")
        if details is None or not details.isVisibleTo(dialog):
            raise RuntimeError("The selected skill has no visible target Details control")
        details.click()
        for _ in range(4):
            app.processEvents()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not dialog.grab().save(str(args.output)):
        raise RuntimeError(f"Could not save {args.output}")
    dialog.close()
    case.tearDown()
    return args.output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill")
    parser.add_argument("--category", required=True)
    parser.add_argument("--level", type=int, default=99)
    parser.add_argument("--target-key")
    parser.add_argument("--target-id")
    parser.add_argument("--inventory", action="append", default=[])
    parser.add_argument("--complete-quest", action="append", default=[])
    parser.add_argument("--claim-wicked-hood", action="store_true")
    parser.add_argument("--equip-wicked-hood", action="store_true")
    parser.add_argument("--feed-altar", action="append", default=[])
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=560)
    parser.add_argument("--theme", choices=("dark", "light"), default="dark")
    parser.add_argument("--open-details", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(render(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
