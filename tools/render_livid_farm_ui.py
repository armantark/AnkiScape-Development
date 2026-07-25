#!/usr/bin/env python3
"""Render the live Livid Farm Utility panel for visual review."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QColor, QPalette, QWidget  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.livid_farm_data import (
    ARCANE_CAPACITOR_CHARGED,
    ARCANE_CAPACITOR_UNCHARGED,
    LIVID_FARM_UNLOCKS,
)
from ankiscape.data.farming_data import (
    LIVID_FARM_ALLOTMENT_PATCH_ID,
    LIVID_FARM_PROTECTION_SCROLL,
)
from ankiscape.logic.farming_logic import (
    activate_livid_farm_allotment_pure,
    execute_farm_field_step_pure,
)
from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _open_equipment_tab,
)


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


def render(output_dir: Path) -> tuple[Path, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(methodName="test_livid_farm_panel_exposes_progress_and_persists_routine")
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())
    player_data = _make_player_data()
    player_data.update(
        {
            "magic_level": 99,
            "agility_level": 60,
            "crafting_level": 60,
            "farming_level": 60,
            "construction_level": 50,
            "current_utility": "livid_farm",
        }
    )
    player_data["quests"]["lunar_diplomacy"] = {"completed": True}
    player_data["livid_farm"] = {
        "farm_routine": "complete",
        "produce_points": 73_000,
        "lifetime_produce_points": 923_000,
        "cycles_completed": 584,
        "borrowed_power_claimed": True,
        "more_planks_reviews_remaining": 7,
        "unlocked_spells": tuple(
            unlock_id
            for unlock_id, _name, _threshold in LIVID_FARM_UNLOCKS
        ),
    }
    for rune_name in (
        "Air rune",
        "Astral rune",
        "Blood rune",
        "Nature rune",
        "Law rune",
        "Earth rune",
        "Water rune",
    ):
        player_data["inventory"][rune_name] = 20_000
    player_data["inventory"][ARCANE_CAPACITOR_UNCHARGED] = 1

    dialog = case._open(player_data)
    case._open_utility(dialog)
    dialog.show()

    paths = []
    for width, height, suffix in (
        (1100, 650, "wide"),
        (900, 560, "laptop"),
    ):
        dialog.resize(width, height)
        for _ in range(8):
            app.processEvents()
        path = output_dir / f"livid-farm-{suffix}.png"
        if not dialog.grab().save(str(path)):
            raise RuntimeError(f"Could not save {path}")
        paths.append(path)
    dialog.close()

    player_data["inventory"].pop(ARCANE_CAPACITOR_UNCHARGED, None)
    player_data["equipment"] = {
        "weapon": "Staff of air",
        "neck": ARCANE_CAPACITOR_CHARGED,
    }
    player_data["combat_attack_style"] = "magic_standard"
    player_data["current_combat_spell"] = "wind_strike"
    player_data["livid_farm"].update(
        {
            "arcane_capacitor_spell": "wind_wave",
            "arcane_capacitor_charges": 742,
        }
    )
    combat_dialog = case._open(player_data, current_skill="Combat")
    _open_equipment_tab(combat_dialog)
    combat_dialog.resize(900, 560)
    combat_dialog.show()
    for _ in range(8):
        app.processEvents()
    combat_path = output_dir / "borrowed-power-combat.png"
    if not combat_dialog.grab().save(str(combat_path)):
        raise RuntimeError(f"Could not save {combat_path}")
    paths.append(combat_path)
    combat_dialog.close()

    farming_data = _make_player_data()
    farming_data["farming_level"] = 99
    farming_data["inventory"].update(
        {
            "Rake": 1,
            "Spade": 1,
            "Seed dibber": 1,
            "Oak sapling": 1,
            LIVID_FARM_PROTECTION_SCROLL: 1,
        }
    )
    farming_data, active, _ = activate_livid_farm_allotment_pure(
        farming_data
    )
    if not active:
        raise RuntimeError("Could not activate the Livid Farm allotment")
    farming_data, planted, _ = execute_farm_field_step_pure(
        farming_data,
        {
            "kind": "plant",
            "patch_id": "lumbridge_tree",
            "crop_id": "oak",
        },
    )
    if not planted:
        raise RuntimeError("Could not plant the Livid protection preview tree")

    for patch_id, suffix in (
        (LIVID_FARM_ALLOTMENT_PATCH_ID, "one-use-patch"),
        ("lumbridge_tree", "protection-scroll"),
    ):
        farming_dialog = case._open(
            farming_data,
            initial_skill="Farming",
            initial_farming_patch_id=patch_id,
        )
        farming_dialog.show()
        for width, height, size_suffix in (
            (1000, 700, ""),
            (900, 560, "-laptop"),
        ):
            farming_dialog.resize(width, height)
            for _ in range(8):
                app.processEvents()
            farming_panel = farming_dialog.findChild(
                QWidget,
                "farmingSkillPanel",
            )
            focus_patch = getattr(
                farming_panel,
                "_ankiscape_focus_farming_patch",
                None,
            )
            if focus_patch is not None:
                focus_patch(patch_id)
                for _ in range(8):
                    app.processEvents()
            farming_path = (
                output_dir / f"farming-{suffix}{size_suffix}.png"
            )
            if not farming_dialog.grab().save(str(farming_path)):
                raise RuntimeError(f"Could not save {farming_path}")
            paths.append(farming_path)
        farming_dialog.close()

    case.tearDown()
    return tuple(paths)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-livid-farm-ui"),
    )
    args = parser.parse_args()
    for path in render(args.output_dir):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
