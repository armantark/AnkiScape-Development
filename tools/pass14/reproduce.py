"""Replay both Pass 14 owner incidents against the real offscreen Qt add-on."""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from aqt.qt import QApplication, QLabel, QMainWindow, QPushButton, QTimer
from tests import allow_modal_dialogs
from tests.test_integration_smoke import _DummyCol, _load_addon_as_package


def _load_addon(name: str):
    addon = _load_addon_as_package(name)
    parent = QMainWindow()
    parent.col = _DummyCol(
        {
            "ankiscape_floating_xp_enabled": False,
            "ankiscape_review_hud_enabled": False,
        }
    )
    parent.update_undo_actions = lambda: None
    parent.show()
    parent.resize(900, 560)
    for _ in range(4):
        QApplication.processEvents()
    addon.mw = parent
    addon.ui.mw = parent
    addon.save_player_data = lambda: None
    addon.check_achievements = lambda _data: None
    addon._refresh_skill_availability = lambda: None
    addon._refresh_open_carried_inventory = lambda: None
    addon.update_review_hud = lambda *_args: None
    addon.update_review_status_badge = lambda *_args: None
    addon.update_review_fill_drawer = lambda *_args: None
    addon.update_review_event_log_drawer = lambda *_args: None
    addon._refresh_bank_run_surfaces = lambda: None
    addon._update_review_context_surface = lambda: None
    return addon, parent


def _encounter_reproduction(addon, phase: str) -> dict:
    errors = []
    addon.show_error_message = lambda title, message: errors.append([title, message])
    addon._state.current_skill = "Combat"
    addon._state.player_data = {
        "inventory": {},
        "equipment": {},
        "attack_level": 31,
        "strength_level": 26,
        "defense_level": 21,
        "constitution_level": 28,
        "combat_lifepoints": 280,
        "current_combat_target": "black_bear",
        "combat_action": "attack",
        "combat_attack_style": "aggressive",
        "combat_attack_style_type": "crush",
        "combat_pack_mode": "casual",
    }
    combat = sys.modules[f"{addon.__name__}.logic_pure.logic_pure_combat_engine"]
    data, ok, result = combat.apply_combat_burst_pure(
        addon._state.player_data,
        ticks=1,
        rng=lambda: 0.5,
        live_cadence=True,
    )
    assert ok, result
    addon._state.player_data = data
    encounter_before = dict(data["combat_encounter"])
    assert encounter_before, result
    addon._switch_to_bankstanding(automatic=False)
    encounter_after_leaving = dict(addon._state.player_data["combat_encounter"])
    accepted = addon._set_combat_attack_style(("accurate", "crush"))
    style = addon._state.player_data["combat_attack_style"]
    addon._state.current_skill = "Combat"
    returned, ok, return_result = combat.apply_combat_burst_pure(
        addon._state.player_data,
        ticks=1,
        rng=lambda: 1.0,
        live_cadence=True,
    )
    assert ok, return_result
    encounter_on_return = dict(returned["combat_encounter"])
    enemy_max_lifepoints = int(
        addon.COMBAT_ENEMY_DATA["black_bear"]["stats"]["hitpoints"]
    )
    return_fresh = (
        encounter_on_return.get("enemy_lifepoints") == enemy_max_lifepoints
        and encounter_on_return.get("player_attack_ticks_remaining") == 3
    )
    record = {
        "scenario": "encounter",
        "phase": phase,
        "encounter_before": encounter_before,
        "encounter_after_bankstanding": encounter_after_leaving,
        "style_change_accepted": accepted,
        "style": style,
        "errors": errors,
        "enemy_max_lifepoints": enemy_max_lifepoints,
        "encounter_on_return": encounter_on_return,
        "return_fresh": return_fresh,
    }
    if phase == "before":
        assert not accepted and encounter_after_leaving
        assert errors == [[
            "Cannot change combat method",
            "Finish the active fight before changing combat method.",
        ]]
        assert not return_fresh
    else:
        assert accepted and style == "accurate" and not errors
        assert not encounter_after_leaving
        assert return_fresh
    return record


def _flush_review_dialogs(addon) -> dict:
    dialog = {}

    def _capture_and_accept() -> None:
        modal = QApplication.activeModalWidget()
        if modal is None:
            return
        dialog.update(
            {
                "window_title": modal.windowTitle(),
                "size": [modal.width(), modal.height()],
                "labels": [label.text() for label in modal.findChildren(QLabel)],
                "buttons": [button.text() for button in modal.findChildren(QPushButton)],
            }
        )
        modal.accept()

    addon._show_pending_review_dialogs()
    QTimer.singleShot(0, _capture_and_accept)
    with allow_modal_dialogs():
        for _ in range(4):
            QApplication.processEvents()

    return dialog


def _slayer_reproduction(addon, phase: str) -> dict:
    storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
    constants = sys.modules[f"{addon.__name__}.core.constants"]
    player_data = storage.default_player_data(
        addon.ORE_DATA, constants.ITEM_DEFINITIONS
    )
    player_data.update(
        {
            "current_combat_target": "black_bear",
            "combat_action": "attack",
            "combat_attack_style": "aggressive",
            "combat_attack_style_type": "crush",
            "combat_lifepoints": 990,
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "slayer_level": 99,
            "slayer_assignment": {
                "master_id": "turael_spria",
                "family_id": "bears",
                "initial_count": 17,
                "remaining": 1,
            },
            "combat_encounter": {
                "target_id": "black_bear",
                "enemy_lifepoints": 1,
                "player_attack_ticks_remaining": 0,
                "enemy_attack_ticks_remaining": 99,
                "curse_attack_count": 0,
                "magic_effects_applied": [],
                "spell_enemy_attack_factor": 1.0,
                "spell_enemy_defence_factor": 1.0,
            },
        }
    )
    addon._state.current_skill = "Combat"
    addon._state.player_data = player_data
    addon._state.pending_review_dialogs.clear()
    rolls = itertools.cycle((0.0, 0.999999))
    original_random = addon.random.random
    addon.random.random = lambda: next(rolls)
    try:
        addon._begin_review_feedback_context()
        try:
            progressed = addon.runtime_actions.handle_combat_answer(
                addon._runtime_action_context()
            )
        finally:
            addon._finish_review_feedback_context()
    finally:
        addon.random.random = original_random

    assignment = dict(addon._state.player_data["slayer_assignment"])
    queued_before_flush = len(addon._state.pending_review_dialogs)
    dialog = _flush_review_dialogs(addon)

    activity_events = [
        str(row.get("text", ""))
        for row in addon._state.player_data.get("review_event_log", ())
        if row.get("kind") == "activity"
    ]
    record = {
        "scenario": "slayer",
        "phase": phase,
        "review_progressed": progressed,
        "assignment_after_final_kill": assignment,
        "slayer_tasks_completed": addon._state.player_data["slayer_tasks_completed"],
        "activity_events": activity_events,
        "queued_completion_dialogs_before_flush": queued_before_flush,
        "completion_dialog": dialog,
        "combat_action_after_dialog": addon._state.current_skill,
    }
    assert progressed
    assert assignment["remaining"] == 0 and assignment["completed"]
    assert addon._state.player_data["slayer_tasks_completed"] == 1
    assert any("Slayer assignment complete" in text for text in activity_events)
    assert addon._state.current_skill == "Combat"
    if phase == "before":
        assert queued_before_flush == 0 and not dialog
    else:
        assert queued_before_flush == 1
        assert dialog["window_title"] == "Slayer assignment complete"
        assert (
            "You have defeated 17 bears. See a Slayer master for a new assignment."
            in dialog["labels"]
        )
        assert "OK" in dialog["buttons"]
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenario", choices=("encounter", "slayer"), default="encounter"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expect", choices=("before", "after"), required=True)
    args = parser.parse_args()
    app = QApplication.instance() or QApplication([])
    addon, parent = _load_addon(f"ankiscape_pass14_{args.scenario}_{args.expect}")
    try:
        record = (
            _encounter_reproduction(addon, args.expect)
            if args.scenario == "encounter"
            else _slayer_reproduction(addon, args.expect)
        )
        record["qt_platform"] = app.platformName()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps(record, indent=2))
    finally:
        parent.close()
        parent.deleteLater()
        for _ in range(4):
            QApplication.processEvents()


if __name__ == '__main__':
    main()
