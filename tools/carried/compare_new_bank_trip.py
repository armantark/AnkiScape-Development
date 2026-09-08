"""Compare complete carried overlays against the frozen new-trip baseline."""

import argparse
import base64
import copy
import dataclasses
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import sys
from unittest.mock import patch

EVIDENCE = Path("memory-bank/evidence/carried-new-bank-trip-2026-09-08")
BASELINE = "6dacde5486c72e73ca170c039bf8207dec22ac81"


def source_guard(root, inventory, expected_sha):
    raw = inventory.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError("Inventory differs; product imports not started.")
    manifest = json.loads(gzip.decompress(raw))
    if manifest["baseline_commit"] != BASELINE:
        raise ValueError("Baseline commit differs; product imports not started.")
    for name, expected in manifest["files"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Source differs: {name}; product imports not started.")
    frozen = gzip.decompress((root / EVIDENCE / "baseline-overlay.py.gz").read_bytes())
    if hashlib.sha256(frozen).hexdigest() != manifest["baseline_overlay_sha256"]:
        raise ValueError("Baseline source differs; product imports not started.")
    return manifest, frozen


def trip_cases():
    for label, changes, expected in (
        ("moving", {}, {"cost": 1, "handler_calls": 0, "rng_calls": 1}),
        ("partial-credit", {"agility_run_energy_credit_pct": 50},
         {"cost": 1, "handler_calls": 0, "rng_calls": 1, "credit": 0}),
        ("waived", {"agility_run_energy_credit_pct": 100},
         {"cost": 0, "handler_calls": 1, "rng_calls": 1, "credit": 0}),
        ("waived-rejected", {"agility_run_energy_credit_pct": 100},
         {"cost": 0, "handler_calls": 1, "rng_calls": 1, "credit": 0, "result": False}),
        ("not-due", {"carried_churn": {"copper_ore": 0}},
         {"cost": None, "handler_calls": 1, "rng_calls": 1}),
        ("active-trip", {"skilling_bank_run": {"target_id": "copper_ore",
                                               "reviews_remaining": 3, "reviews_total": 3}},
         {"cost": None, "handler_calls": 0, "rng_calls": 0}),
    ):
        player = {"inventory": {"Coal": 28}, "current_ore": "copper_ore", "agility_level": 1,
                  "carried_inventory": {"copper_ore": {"Coal": 28}},
                  "carried_churn": {"copper_ore": 28}}
        player.update(changes)
        yield label, "mining", player, expected
    from ankiscape.logic.wicked_hood_logic import default_wicked_hood_state_pure

    for teleport, cost in ((False, 20), (True, 10)):
        hood = default_wicked_hood_state_pure()
        hood.update(fed_altars=["air"], pending_altar_teleport="air" if teleport else "")
        player = {"inventory": {"Rune essence": 56}, "equipment": {"head": "Wicked hood"},
                  "current_runecrafting": "craft_air_runes", "runecrafting_level": 1,
                  "agility_level": 1, "carried_inventory": {"craft_air_runes": {"Rune essence": 28}},
                  "carried_churn": {"craft_air_runes": 28},
                  "carried_primed_targets": {"craft_air_runes": True}, "skilling_bank_run": {},
                  "wicked_hood": hood, "shop_market_clock": {"answered_cards": 0}}
        yield f"altar-teleport-{teleport}", "runecrafting", player, {
            "cost": cost, "teleported": teleport, "handler_calls": 0, "rng_calls": 1,
            "phase_ids": ["return", "bank"] if teleport else ["return", "bank", "outbound"],
        }


def recorded_context(player, events, rng):
    from tests.test_runtime_actions import _context
    from tools.carried.compare_processing_reconciliation import trace_callback

    ctx = _context(player)
    ctx.random_random = rng.random
    for field in dataclasses.fields(ctx):
        callback = getattr(ctx, field.name)
        if callable(callback):
            setattr(ctx, field.name, trace_callback(field.name, callback, player, events))
    return ctx


def capture_trip(module, skill, supplied, expected):
    from tools.combat.compare_kill_rewards import RecordedRandom

    player, events = copy.deepcopy(supplied), []
    rng = RecordedRandom((0.0,))
    ctx = recorded_context(player, events, rng)

    def handler(action_ctx):
        events.append(["handler_start", copy.deepcopy(player)])
        action_ctx.random_random()
        inventory = dict(action_ctx.player_data.get("inventory", {}))
        inventory["Coal"] = inventory.get("Coal", 0) + 1
        action_ctx.player_data["inventory"] = inventory
        action_ctx.check_achievements(action_ctx.player_data)
        action_ctx.refresh_skill_availability()
        action_ctx.save_player_data()
        result = expected.get("result", True)
        events.append(["handler_end", result, copy.deepcopy(player)])
        return result

    result = module.run_answer_with_carried_overlay(ctx, skill, handler)
    travel = player.get("agility_last_travel", {})
    observed = {"cost": travel.get("charged_reviews"), "result": result,
                "handler_calls": sum(event[0] == "handler_start" for event in events),
                "rng_calls": len(rng.draws), "credit": player.get("agility_run_energy_credit_pct"),
                "teleported": travel.get("outbound_teleport_used"),
                "phase_ids": [phase["id"] for phase in player.get("skilling_bank_run", {}).get("route_phases", [])]}
    return {"result": result, "player": player, "events": events, "rng": rng.snapshot(),
            "player_identity_preserved": ctx.player_data is player}, observed


def capture_rollback(module):
    from tools.carried import compare_processing_reconciliation as existing
    from tools.combat.compare_kill_rewards import RecordedRandom

    rng = RecordedRandom((0.0,))
    config = {"replace": True, "result": False, "repeated": False,
              "winter": True, "child_cadence": False, "after": {"Input": 3}}
    with patch.object(existing, "context", lambda player, events: recorded_context(player, events, rng)):
        captured = existing.run_fixture(module, config)
    captured["rng"] = rng.snapshot()
    return captured


def retain_case(output, rows, label, before, after, route_pass, expected, observed):
    before_bytes, after_bytes = pickle.dumps(before, protocol=4), pickle.dumps(after, protocol=4)
    rows.append({"case": label, "equal": before == after,
                 "pickle_bytes_equal": before_bytes == after_bytes,
                 "route_pass": route_pass, "expected": expected, "observed": observed,
                 "baseline_pickle_base64": base64.b64encode(before_bytes).decode(),
                 "candidate_pickle_base64": base64.b64encode(after_bytes).decode()})
    output.write_bytes(gzip.compress((json.dumps({"cases": rows}, indent=2) + "\n").encode(), mtime=0))


def compare(root, frozen, output):
    from tools.carried.compare_processing_reconciliation import load_wrappers

    baseline, candidate = load_wrappers(root, frozen)
    rows = []
    for label, skill, player, expected in trip_cases():
        before, baseline_observed = capture_trip(baseline, skill, player, expected)
        after, observed = capture_trip(candidate, skill, player, expected)
        route_pass = (all(observed[key] == value for key, value in expected.items())
                      and baseline_observed == observed and after["player_identity_preserved"])
        retain_case(output, rows, label, before, after, route_pass, expected, observed)
    before, after = capture_rollback(baseline), capture_rollback(candidate)
    observed = {"result": after["result"],
                "special_points": after["player"]["summoning_state"]["special_move_points_current"]}
    expected = {"result": False, "special_points": 20}
    retain_case(output, rows, "winter-storage-rejection", before, after,
                observed == expected, expected, observed)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--inventory-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if sys.flags.optimize or "PYTHONOPTIMIZE" in os.environ:
        raise SystemExit("Optimized interpreter refused; product imports not started.")
    root = Path(__file__).resolve().parents[2]
    manifest, frozen = source_guard(root, args.inventory, args.inventory_sha256)
    report = {"baseline_commit": BASELINE, "inventory_sha256": args.inventory_sha256,
              "sources_before": manifest["files"]}
    if args.preflight:
        imported = [name for name in sys.modules if name.split(".")[0] in {"ankiscape", "pkg_alias", "tests"}]
        if imported:
            raise RuntimeError(f"Product modules already loaded: {imported}")
        report.update(status="PREFLIGHT_PASS", product_imported=False)
    else:
        sys.path.insert(0, str(root))
        rows = compare(root, frozen, args.output)
        passed = all(row["equal"] and row["pickle_bytes_equal"] and row["route_pass"] for row in rows)
        report.update(cases=rows, status="PASS" if passed else "FAIL")
    report["sources_after"] = source_guard(root, args.inventory, args.inventory_sha256)[0]["files"]
    args.output.write_bytes(gzip.compress((json.dumps(report, indent=2) + "\n").encode(), mtime=0))
    if report["status"] == "FAIL":
        raise SystemExit("Whole overlay comparison or route proof failed.")


if __name__ == "__main__":
    main()
