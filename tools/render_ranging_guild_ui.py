#!/usr/bin/env python3
"""Render the ready and claimable Ranging Guild surfaces for visual QA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

import pkg_alias  # noqa: F401
from ankiscape.logic.ranging_guild_logic import (
    apply_ranging_guild_command_pure,
    default_ranging_guild_state_pure,
)
from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data, _utility_row
from tools.render_big_chinchompa_ui import _dark_palette


def _player(*, claimable: bool = False) -> dict:
    player = _make_player_data()
    player["ranged_level"] = 70
    player["inventory"]["Coins"] = 2_000
    player["inventory"]["Bronze arrows"] = 25
    player["inventory"]["Archery ticket"] = 86
    player["equipment"] = {
        "weapon": "Magic shortbow",
        "ammunition": "Bronze arrows",
    }
    player["ranging_guild"] = default_ranging_guild_state_pure()
    if claimable:
        player["ranging_guild"].update(
            {
                "pending_claim": True,
                "shots_fired": 10,
                "score": 550,
                "competitions_started": 4,
                "competitions_completed": 4,
                "last_outcome": "yellow",
                "last_result": (
                    "Yellow: +50 score, +25 Ranged XP. "
                    "Final score 550; claim 55 tickets."
                ),
            }
        )
    return player


def _show(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    def command(action_id, payload):
        updated, ok, info = apply_ranging_guild_command_pure(player, action_id, payload)
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, "message": info.get("reason", ""), **info}

    dialog = case._open(
        player,
        current_skill="Activities",
        on_ranging_guild_command=command,
    )
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "ranging_guild")
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
        methodName="test_ranging_guild_activity_page_enters_claims_and_buys_reward"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    paths = []
    for name, player in (("ready", _player()), ("claimable", _player(claimable=True))):
        dialog = _show(case, player, width, height)
        path = output_dir / f"ranging-guild-{name}.png"
        if not dialog.grab().save(str(path)):
            raise RuntimeError(f"Could not save {path}")
        dialog.close()
        paths.append(path)
    case.tearDown()
    return tuple(paths)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-ranging-guild-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
