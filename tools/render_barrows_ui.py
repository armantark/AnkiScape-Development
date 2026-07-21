#!/usr/bin/env python3
"""Render the mechanic-complete Barrows activity card."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QWidget  # type: ignore

from barrows_logic import default_barrows_state_pure
from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data, _utility_row
from tools.render_big_chinchompa_ui import _dark_palette


def _active_player_data() -> dict:
    player_data = _make_player_data()
    state = default_barrows_state_pure()
    state.update(
        {
            "active": True,
            "automation_mode": "advanced",
            "phase": "tunnels",
            "available_brothers": [
                "ahrim",
                "dharok",
                "guthan",
                "karil",
                "torag",
                "verac",
                "akrisae",
            ],
            "hidden_brother": "ahrim",
            "slain_brothers": ["dharok", "guthan", "karil", "torag", "verac"],
            "start_room": 0,
            "current_room": 3,
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
            "revealed_rooms": [0, 3, 4, 6],
            "selected_room": 4,
            "tunnel_kill_count": 4,
            "active_encounter": {
                "kind": "creature",
                "enemy_id": "giant_crypt_spider",
                "lifepoints": 520,
                "encounter": {
                    "target_id": "barrows",
                    "enemy_lifepoints": 520,
                },
                "protected_class": "melee",
                "protection_damage": 0,
            },
            "last_result": "Room 4 · Giant crypt spider: 520 LP",
        }
    )
    player_data.update(
        {
            "current_utility": "barrows",
            "barrows": state,
            "activity_session": {"active_id": "barrows"},
            "equipment_instances": {
                "equipment-7": {
                    "family_id": "barrows_verac",
                    "item_name": "Verac's flail 50",
                    "condition": 45_000,
                    "location": "bank",
                }
            },
            "equipment_instance_next_id": 8,
        }
    )
    player_data["inventory"]["Coins"] = 500_000
    player_data["inventory"]["Verac's flail 50"] = 1
    return player_data


def render(output_path: Path, *, width: int = 900, height: int = 620) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName=(
            "test_barrows_card_enters_selects_repairs_and_suspends_without_nested_scroll"
        )
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    dialog = case._open(_active_player_data())
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "barrows")
    tree.setCurrentItem(row)
    tree.itemActivated.emit(row, 0)
    dialog.show()
    dialog.resize(width, height)
    for _ in range(10):
        app.processEvents()
    panel = dialog.findChild(QWidget, "barrowsPanel")
    if panel is None or not panel.isVisible():
        raise RuntimeError("Barrows panel was not rendered")
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
        default=Path("/tmp/ankiscape-barrows-ui.png"),
    )
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=620)
    args = parser.parse_args()
    print(render(args.output, width=args.width, height=args.height))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
