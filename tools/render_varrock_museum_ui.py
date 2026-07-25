#!/usr/bin/env python3
"""Render quiz and specimen-cleaning Varrock Museum surfaces for visual QA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data, _utility_row
from tools.render_fishing_trawler_ui import _dark_palette
import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.varrock_museum_logic import apply_varrock_museum_command_pure


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    def command(action_id, payload):
        updated, ok, info = apply_varrock_museum_command_pure(
            player, action_id, payload
        )
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, "message": info.get("reason", ""), **info}

    dialog = case._open(
        player,
        current_skill="Activities",
        on_varrock_museum_command=command,
    )
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "varrock_museum")
    tree.setCurrentItem(row)
    tree.itemActivated.emit(row, 0)
    dialog.show()
    dialog.resize(width, height)
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    for _ in range(8):
        app.processEvents()
    return dialog


def render(output_dir: Path, *, width: int = 1200, height: int = 760) -> tuple[Path, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName="test_varrock_museum_landmark_card_routes_claims_and_kit"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    quiz = _make_player_data()
    quiz["varrock_museum"] = {
        "route": "quiz",
        "quiz_completed": ["Lizard", "Battle tortoise", "Dragon"],
        "quest_stories_claimed": ["demon_slayer", "rune_mysteries"],
        "last_result": "Completed the Dragon display · +2 Kudos",
    }
    quiz_card = _show_card(case, quiz, width, height)
    quiz_path = output_dir / "varrock-museum-quiz.png"
    if not quiz_card.grab().save(str(quiz_path)):
        raise RuntimeError(f"Could not save {quiz_path}")
    quiz_card.close()

    cleaning = _make_player_data()
    cleaning["quests"]["the_dig_site"] = {"completed": True}
    cleaning["equipment"] = {"hands": "Leather gloves", "feet": "Leather boots"}
    cleaning["inventory"].update(
        {"Trowel": 1, "Rock pick": 1, "Specimen brush": 1}
    )
    cleaning["carried_inventory"] = {
        "varrock_museum": {"Trowel": 1, "Rock pick": 1, "Specimen brush": 1}
    }
    cleaning["varrock_museum"] = {
        "route": "cleaning",
        "specimens_displayed": ["pottery", "old_symbol", "ancient_symbol"],
        "last_result": "Cleaned Ancient symbol and filled case 37 · +10 Kudos",
    }
    cleaning_card = _show_card(case, cleaning, width, height)
    cleaning_path = output_dir / "varrock-museum-cleaning.png"
    if not cleaning_card.grab().save(str(cleaning_path)):
        raise RuntimeError(f"Could not save {cleaning_path}")
    cleaning_card.close()

    case.tearDown()
    return quiz_path, cleaning_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-varrock-museum-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
