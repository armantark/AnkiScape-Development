#!/usr/bin/env python3
"""Render ready and active TzHaar Fight Pit surfaces for visual QA."""

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
from tzhaar_fight_pit_logic import (
    apply_tzhaar_fight_pit_command_pure,
    default_tzhaar_fight_pit_state_pure,
)


def _player() -> dict:
    player = _make_player_data()
    player.update(default_tzhaar_fight_pit_state_pure())
    player.update(
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
    return player


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    def command(action_id, payload):
        updated, ok, info = apply_tzhaar_fight_pit_command_pure(
            player, action_id, payload
        )
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, "message": info.get("reason", ""), **info}

    dialog = case._open(
        player,
        current_skill="Activities",
        on_tzhaar_fight_pit_command=command,
    )
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "tzhaar_fight_pit")
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
        methodName="test_tzhaar_fight_pit_detail_routes_policy_entry_and_active_state"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    ready_card = _show_card(case, _player(), width, height)
    ready_path = output_dir / "tzhaar-fight-pit-ready.png"
    if not ready_card.grab().save(str(ready_path)):
        raise RuntimeError(f"Could not save {ready_path}")
    ready_card.close()

    active, ok, info = apply_tzhaar_fight_pit_command_pure(
        _player(), "enter", {"policy": "aggressive"}
    )
    if not ok:
        raise RuntimeError(str(info))
    active["tzhaar_fight_pit"]["review"] = 7
    active["tzhaar_fight_pit"]["pending_tokkul"] = 92
    active["tzhaar_fight_pit"]["roster"] = active["tzhaar_fight_pit"]["roster"][:2]
    active["tzhaar_fight_pit"]["engaged_opponent_id"] = (
        active["tzhaar_fight_pit"]["roster"][0]["opponent_id"]
    )
    active_card = _show_card(case, active, width, height)
    active_path = output_dir / "tzhaar-fight-pit-active.png"
    if not active_card.grab().save(str(active_path)):
        raise RuntimeError(f"Could not save {active_path}")
    active_card.close()

    case.tearDown()
    return ready_path, active_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-tzhaar-fight-pit-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

