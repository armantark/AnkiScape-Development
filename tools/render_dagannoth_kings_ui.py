#!/usr/bin/env python3
"""Render the persistent Dagannoth Kings activity card."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QWidget  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.dagannoth_kings_data import DAGANNOTH_KINGS_ENEMY_DATA
from ankiscape.logic.dagannoth_kings_logic import (
    default_dagannoth_kings_state_pure,
)
from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _utility_row,
)
from tools.render_big_chinchompa_ui import _dark_palette


def _active_player_data() -> dict:
    player_data = _make_player_data()
    state = default_dagannoth_kings_state_pure()
    state.update(
        {
            "active": True,
            "automation_mode": "advanced",
            "engaged_enemy_id": "dagannoth_supreme",
            "trip_kills": 4,
            "total_kills": 17,
            "kill_counts": {
                "dagannoth_prime": 5,
                "dagannoth_supreme": 6,
                "dagannoth_rex": 6,
            },
            "trips": 3,
            "last_result": (
                "Dagannoth Supreme: 1,420/2,560 LP · roster pressure 86 LP"
            ),
            "roster": [
                {
                    "enemy_id": "dagannoth_prime",
                    "lifepoints": 0,
                    "respawn_ticks": 24,
                    "encounter": {},
                },
                {
                    "enemy_id": "dagannoth_supreme",
                    "lifepoints": 1_420,
                    "respawn_ticks": 0,
                    "encounter": {
                        "target_id": "dagannoth_supreme",
                        "enemy_lifepoints": 1_420,
                    },
                },
                {
                    "enemy_id": "dagannoth_rex",
                    "lifepoints": DAGANNOTH_KINGS_ENEMY_DATA["dagannoth_rex"]["stats"][
                        "hitpoints"
                    ],
                    "respawn_ticks": 0,
                    "encounter": {
                        "target_id": "dagannoth_rex",
                        "enemy_lifepoints": DAGANNOTH_KINGS_ENEMY_DATA[
                            "dagannoth_rex"
                        ]["stats"]["hitpoints"],
                    },
                },
            ],
        }
    )
    player_data.update(
        {
            "current_utility": "dagannoth_kings",
            "dagannoth_kings": state,
            "activity_session": {"active_id": "dagannoth_kings"},
        }
    )
    return player_data


def render(output_path: Path, *, width: int = 900, height: int = 560) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName=(
            "test_dagannoth_kings_card_uses_period_icons_and_persistent_room_controls"
        )
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    dialog = case._open(_active_player_data())
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "dagannoth_kings")
    tree.setCurrentItem(row)
    tree.itemActivated.emit(row, 0)
    dialog.show()
    dialog.resize(width, height)
    for _ in range(10):
        app.processEvents()
    panel = dialog.findChild(QWidget, "dagannothKingsPanel")
    if panel is None or not panel.isVisible():
        raise RuntimeError("Dagannoth Kings panel was not rendered")
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
        default=Path("/tmp/ankiscape-dagannoth-kings-ui.png"),
    )
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=560)
    args = parser.parse_args()
    print(render(args.output, width=args.width, height=args.height))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
