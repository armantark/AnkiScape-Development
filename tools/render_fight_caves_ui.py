#!/usr/bin/env python3
"""Render the mechanic-complete Fight Caves activity card."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QWidget  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.fight_caves_logic import default_fight_caves_state_pure
from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _utility_row,
)
from tools.render_big_chinchompa_ui import _dark_palette


def _active_jad_player_data() -> dict:
    player_data = _make_player_data()
    state = default_fight_caves_state_pure()
    state.update(
        {
            "active": True,
            "wave": 63,
            "automation_mode": "advanced",
            "engaged_instance_id": "fight-caves-1",
            "next_instance_id": 6,
            "healer_generation": 1,
            "jad_next_style": "magic",
            "last_result": "Wave 63 · TzTok-Jad: 1,180 LP · four Yt-HurKot joined Jad",
            "roster": [
                {
                    "instance_id": "fight-caves-1",
                    "enemy_id": "tztok_jad",
                    "lifepoints": 1_180,
                    "encounter": {
                        "target_id": "fight_caves",
                        "enemy_lifepoints": 1_180,
                    },
                    "heal_counter": 0,
                },
                *(
                    {
                        "instance_id": f"fight-caves-{index}",
                        "enemy_id": "yt_hurkot",
                        "lifepoints": 600,
                        "encounter": {
                            "target_id": "fight_caves",
                            "enemy_lifepoints": 600,
                        },
                        "heal_counter": 0,
                    }
                    for index in range(2, 6)
                ),
            ],
        }
    )
    player_data.update(
        {
            "current_utility": "fight_caves",
            "fight_caves": state,
            "activity_session": {"active_id": "fight_caves"},
        }
    )
    return player_data


def render(output_path: Path, *, width: int = 900, height: int = 560) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName=(
            "test_fight_caves_card_enters_targets_and_leaves_without_nested_scroll"
        )
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    dialog = case._open(_active_jad_player_data())
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "fight_caves")
    tree.setCurrentItem(row)
    tree.itemActivated.emit(row, 0)
    dialog.show()
    dialog.resize(width, height)
    for _ in range(10):
        app.processEvents()
    panel = dialog.findChild(QWidget, "fightCavesPanel")
    if panel is None or not panel.isVisible():
        raise RuntimeError("Fight Caves panel was not rendered")
    if not dialog.grab().save(str(output_path)):
        raise RuntimeError(f"Could not save {output_path}")
    dialog.close()
    case.tearDown()
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/ankiscape-fight-caves-ui.png"),
    )
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=560)
    args = parser.parse_args()
    print(render(args.output, width=args.width, height=args.height))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
