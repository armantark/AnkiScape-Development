#!/usr/bin/env python3
"""Probe the carried-overlay routes that broad generated scenarios missed.

Run from the repository root:

    PYTHONHASHSEED=0 python3 -B tools/carried/probe_overlay_routes.py
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import importlib
import json
import os
import sys
import types
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
OVERLAY_SOURCE = ROOT / "runtime" / "runtime_actions_carried_overlay.py"
LAYOUT_SELECTION = "    carried_materials = view if view else layout if advanced else {}"
VIEW_ONLY_SELECTION = "    carried_materials = view"


def _load_view_only_mutant():
    source = OVERLAY_SOURCE.read_text(encoding="utf-8")
    if source.count(LAYOUT_SELECTION) != 1:
        raise RuntimeError("carried-material selection seam changed")
    source = source.replace(LAYOUT_SELECTION, VIEW_ONLY_SELECTION)
    name = "ankiscape.runtime._probe_view_only_carried_overlay"
    module = types.ModuleType(name)
    module.__package__ = "ankiscape.runtime"
    sys.modules[name] = module
    exec(compile(source, str(OVERLAY_SOURCE), "exec"), module.__dict__)  # noqa: S102
    return module


def _runtime_context(player: dict, calls: dict):
    from tests.test_runtime_actions import _context

    return _context(player, calls)


def _capture_fletching(module) -> dict:
    from ankiscape.runtime.runtime_actions_production import handle_fletching_answer

    target = "headless_arrows"
    player = {
        "inventory": {"Arrow shafts": 30, "Feather": 30, "Blue feather": 30},
        "fletching_level": 1,
        "fletching_exp": 0,
        "current_fletch": target,
        "completed_achievements": [],
        "carried_inventory": {},
        "carried_advanced_targets": {target: True},
        "carried_layout": {target: {"Arrow shafts": 15, "Blue feather": 15}},
    }
    calls = {"xp": [], "saves": 0, "errors": []}
    result = module.run_answer_with_carried_overlay(
        _runtime_context(player, calls), "fletching", handle_fletching_answer
    )
    inventory = player["inventory"]
    return {
        "result": result,
        "arrow_shafts": inventory.get("Arrow shafts", 0),
        "ordinary_feathers": inventory.get("Feather", 0),
        "blue_feathers": inventory.get("Blue feather", 0),
        "headless_arrows": inventory.get("Headless arrows", 0),
        "carried_view": (player.get("carried_inventory") or {}).get(target, {}),
        "errors": calls["errors"],
    }


def _capture_crafting_potion(module) -> dict:
    from ankiscape.logic.skilling_boost_logic import skilling_effective_level_pure
    from ankiscape.runtime.runtime_actions_production import handle_crafting_answer

    target = "form_clay_ring_unfired"
    player = {
        "crafting_level": 1,
        "crafting_exp": 0.0,
        "current_craft": target,
        "inventory": {
            "Soft clay": 6,
            "Ring mould": 1,
            "Crafting potion (3)": 1,
        },
        "skilling_potion_targets": {"crafting": {target: True}},
        "carried_inventory": {},
        "carried_layout": {
            target: {
                "Soft clay": 6,
                "Ring mould": 1,
                "Crafting potion (3)": 1,
            }
        },
        "carried_churn": {},
        "carried_advanced_targets": {target: True},
        "carried_primed_targets": {target: True},
        "skilling_bank_run": {},
        "equipment": {},
        "completed_achievements": [],
    }
    calls = {"xp": [], "saves": 0, "errors": []}
    result = module.run_answer_with_carried_overlay(
        _runtime_context(player, calls), "crafting", handle_crafting_answer
    )
    inventory = player["inventory"]
    carried = (player.get("carried_inventory") or {}).get(target, {})
    return {
        "result": result,
        "effective_level": skilling_effective_level_pure(player, "crafting"),
        "soft_clay": inventory.get("Soft clay", 0),
        "output": inventory.get("Clay ring (unfired)", 0),
        "bank_lower_dose": inventory.get("Crafting potion (2)", 0),
        "carried_lower_dose": carried.get("Crafting potion (2)", 0),
        "errors": calls["errors"],
    }


def _maple_player() -> dict:
    from ankiscape.logic.cadence_kernel import default_cadence_profile_state_pure

    from tests.runtime_actions.test_winter_storage_rollback import _player

    player = _player("maple")
    del player["current_thieving"]
    carried = {"Maple logs": 27, "Winter storage scroll": 1}
    player.update(
        current_tree="maple",
        woodcutting_level=99,
        toolbelt={"woodcutting": []},
        equipment={},
        inventory=dict(carried),
        carried_inventory={"maple": dict(carried)},
        cadence_profiles={
            "woodcutting:maple": default_cadence_profile_state_pure(
                opening_ready=True
            )
        },
    )
    player["summoning_state"]["target_policies"]["maple"][
        "winter_storage_priority"
    ] = ["Maple logs"]
    return player


def _without_cadence(player: dict) -> dict:
    comparable = copy.deepcopy(player)
    comparable.pop("cadence_profiles", None)
    return comparable


def _capture_gathering_rejection(module) -> dict:
    from ankiscape.runtime.runtime_actions_gathering import handle_woodcutting_answer

    from tests.test_thieving import _context

    player = _maple_player()
    before = copy.deepcopy(player)
    ctx, _calls = _context(player)
    saves: list[dict] = []
    handler_entries: list[dict] = []
    ctx = dataclasses.replace(
        ctx,
        cadence_live_enabled=True,
        save_player_data=lambda: saves.append(copy.deepcopy(player)),
    )

    def handler(action_ctx):
        handler_entries.append(copy.deepcopy(player))
        return handle_woodcutting_answer(action_ctx)

    result = module.run_answer_with_carried_overlay(ctx, "woodcutting", handler)
    attempted = handler_entries[0] if handler_entries else {}
    attempted_state = attempted.get("summoning_state", {})
    return {
        "result": result,
        "handler_calls": len(handler_entries),
        "admission_changed": (
            attempted.get("cadence_profiles") != before.get("cadence_profiles")
        ),
        "attempted_scrolls": attempted.get("inventory", {}).get(
            "Winter storage scroll"
        ),
        "attempted_carried_logs": (
            attempted.get("carried_inventory", {})
            .get("maple", {})
            .get("Maple logs")
        ),
        "attempted_points": attempted_state.get("special_move_points_current"),
        "winter_storage_spent": (
            attempted.get("inventory", {}).get("Winter storage scroll") == 0
            and attempted.get("carried_inventory", {})
            .get("maple", {})
            .get("Maple logs")
            == 26
            and attempted_state.get("special_move_points_current") == 48
        ),
        "cadence_restored": (
            player.get("cadence_profiles") == before.get("cadence_profiles")
        ),
        "other_state_restored": _without_cadence(player) == _without_cadence(before),
        "final_save_restored": len(saves) == 1 and saves[-1] == player,
    }


def _capture_processing_rejection(module) -> dict:
    from tools.carried import compare_processing_reconciliation as fixtures
    from tools.carried.compare_new_bank_trip import capture_rollback

    expected = fixtures.fixture_player()
    expected["inventory"]["Winter storage scroll"] = 1
    expected["carried_inventory"]["probe"]["Winter storage scroll"] = 1
    expected["carried_churn"]["probe"] = 28
    expected["summoning_state"] = {
        "active_follower": {"kind": "familiar", "entity_id": "packyak"},
        "special_move_points_current": 20,
        "target_policies": {"probe": {"winter_storage_priority": ["Input"]}},
    }

    captured = capture_rollback(module)
    player = captured["player"]
    saves = [
        event[2]
        for event in captured["events"]
        if event[0] == "save_player_data"
    ]
    return {
        "result": captured["result"],
        "cadence_restored": (
            player.get("cadence_profiles") == expected.get("cadence_profiles")
        ),
        "stock_restored": player.get("inventory") == expected.get("inventory"),
        "carried_restored": (
            player.get("carried_inventory") == expected.get("carried_inventory")
            and player.get("carried_churn") == expected.get("carried_churn")
        ),
        "points_restored": (
            player.get("summoning_state", {}).get("special_move_points_current")
            == 20
        ),
        "xp_restored": player.get("summoning_exp", 0.0) == 0.0,
        "final_save_restored": len(saves) == 1 and saves[-1] == player,
    }


def _expected_routes(routes: dict[str, dict]) -> dict[str, bool]:
    return {
        "custom_coloured_feather": routes["custom_coloured_feather"]
        == {
            "result": True,
            "arrow_shafts": 15,
            "ordinary_feathers": 30,
            "blue_feathers": 15,
            "headless_arrows": 15,
            "carried_view": {},
            "errors": [],
        },
        "custom_crafting_potion": routes["custom_crafting_potion"]
        == {
            "result": True,
            "effective_level": 4,
            "soft_clay": 5,
            "output": 1,
            "bank_lower_dose": 1,
            "carried_lower_dose": 1,
            "errors": [],
        },
        "gathering_winter_storage_rejection": (
            routes["gathering_winter_storage_rejection"]["result"] is False
            and routes["gathering_winter_storage_rejection"]["handler_calls"] == 1
            and routes["gathering_winter_storage_rejection"]["admission_changed"]
            and routes["gathering_winter_storage_rejection"]["winter_storage_spent"]
            and routes["gathering_winter_storage_rejection"]["cadence_restored"]
            and routes["gathering_winter_storage_rejection"]["other_state_restored"]
            and routes["gathering_winter_storage_rejection"]["final_save_restored"]
        ),
        "processing_winter_storage_rejection": (
            routes["processing_winter_storage_rejection"]["result"] is False
            and all(
                routes["processing_winter_storage_rejection"][key]
                for key in (
                    "cadence_restored",
                    "stock_restored",
                    "carried_restored",
                    "points_restored",
                    "xp_restored",
                    "final_save_restored",
                )
            )
        ),
    }


def probe() -> dict:
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("run the probe with PYTHONHASHSEED=0")

    sys.path.insert(0, str(ROOT))
    importlib.import_module("pkg_alias")
    from ankiscape.runtime import runtime_actions_carried_overlay as overlay

    routes = {
        "custom_coloured_feather": _capture_fletching(overlay),
        "custom_crafting_potion": _capture_crafting_potion(overlay),
        "gathering_winter_storage_rejection": _capture_gathering_rejection(
            overlay
        ),
        "processing_winter_storage_rejection": _capture_processing_rejection(
            overlay
        ),
    }
    route_checks = _expected_routes(routes)

    view_only = _load_view_only_mutant()
    view_only_observations = {
        "custom_coloured_feather": _capture_fletching(view_only),
        "custom_crafting_potion": _capture_crafting_potion(view_only),
    }
    layout_canary = all(
        routes[name] != view_only_observations[name]
        for name in view_only_observations
    )

    with patch.object(
        overlay._CadenceAdmission,
        "restore_after_rejection",
        lambda _self: None,
    ):
        cadence_mutant = _capture_gathering_rejection(overlay)
    cadence_canary = (
        cadence_mutant["admission_changed"]
        and cadence_mutant["winter_storage_spent"]
        and cadence_mutant["other_state_restored"]
        and not cadence_mutant["cadence_restored"]
    )

    checks = {
        **route_checks,
        "view_only_layout_selection_canary": layout_canary,
        "gathering_cadence_restore_canary": cadence_canary,
    }
    return {
        "routes": routes,
        "canaries": {
            "view_only_layout_selection": view_only_observations,
            "gathering_without_cadence_restore": cadence_mutant,
        },
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = probe()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
