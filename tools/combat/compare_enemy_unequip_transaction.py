"""Compare whole bursts with the frozen enemy-unequip baseline.

``--preflight`` verifies every source pin and stops before product imports.
"""

import argparse
import base64
from copy import deepcopy
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import sys
import types


BASELINE_SHA256 = "486a532d00d4e5693894b77a022ef83a32e03f55e841c2ff92ab12fc7e9ad2d4"
BASELINE_STORED_SHA256 = "cc43ce15c3b14734bd2c39fdfc4516a5f6f386ddc7e163ef6627ed1d60bdffd7"
ENGINE_PATH = "logic_pure/logic_pure_combat_engine.py"


def cases():
    from tests.combat.test_enemy_unequip_transaction import chaos_player

    resume = {
        "target_id": "chaos_elemental",
        "enemy_lifepoints": 2400,
        "player_attack_ticks_remaining": 99,
        "enemy_attack_ticks_remaining": 0,
    }
    yield (
        "weapon:live-resume",
        chaos_player(equipment={"weapon": "Bronze sword"}, combat_encounter=resume),
        (1, 4),
        True,
        {"item": "Bronze sword", "slot": "weapon"},
    )
    yield (
        "sorted-fallback:legacy",
        chaos_player(
            equipment={
                "shield": "Anti-dragon shield",
                "neck": "Amulet of power",
            }
        ),
        (6,),
        False,
        {"item": "Amulet of power", "slot": "neck"},
    )
    yield (
        "empty:legacy",
        chaos_player(equipment={"weapon": "", "head": None}),
        (6,),
        False,
        {"item": "", "slot": ""},
    )
    yield (
        "condition:live-resume",
        chaos_player(
            equipment={"head": "Combat hood 100"},
            equipment_instances={
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 72_001,
                    "location": "equipped:head",
                    "last_slot": "head",
                }
            },
            equipment_instance_next_id=2,
            combat_encounter=resume,
        ),
        (1,),
        True,
        {"item": "Combat hood 100", "slot": "head", "condition": 72_001},
    )


def capture(function, player, chunks, live):
    from ankiscape.core.constants import EQUIPMENT_DATA
    from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
    from tools.combat.compare_kill_rewards import RecordedRandom

    current = deepcopy(player)
    enemies = deepcopy(COMBAT_ENEMY_DATA)
    equipment = deepcopy(EQUIPMENT_DATA)
    rng = RecordedRandom((0.12,) * 100)
    steps = []
    for ticks in chunks:
        supplied = deepcopy(current)
        result = function(
            current,
            enemies,
            equipment,
            ticks=ticks,
            rng=rng.random,
            live_cadence=live,
        )
        assert current == supplied, "The burst mutated the supplied player."
        assert result[1], result
        steps.append((deepcopy(result), rng.snapshot()))
        current = result[0]
    assert enemies == COMBAT_ENEMY_DATA, "The burst mutated enemy data."
    assert equipment == EQUIPMENT_DATA, "The burst mutated equipment data."
    assert rng.draws, "The combat burst did not consume RNG."
    return steps


def route_observation(steps, initial_player):
    first_result = steps[0][0][2]
    final_player = steps[-1][0][0]
    event = first_result["enemy_specials"][0]
    item = event["item"]
    initial_inventory = initial_player.get("inventory", {})
    initial_carried = initial_player.get("carried_inventory", {}).get(
        "chaos_elemental", {}
    )
    instance = final_player.get("equipment_instances", {}).get("equipment-1", {})
    return {
        "item": item,
        "slot": event["slot"],
        "equipment_removed": not item or event["slot"] not in final_player["equipment"],
        "bank_delta": (
            final_player["inventory"].get(item, 0) - initial_inventory.get(item, 0)
            if item
            else 0
        ),
        "pack_delta": (
            final_player["carried_inventory"]["chaos_elemental"].get(item, 0)
            - initial_carried.get(item, 0)
            if item
            else 0
        ),
        "condition": instance.get("condition"),
        "instance_location": instance.get("location", ""),
        "encounter_target": final_player.get("combat_encounter", {}).get(
            "target_id", ""
        ),
    }


def compare(baseline_bytes, output):
    import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
    from ankiscape.logic_pure import logic_pure_combat_engine as candidate

    baseline = types.ModuleType("ankiscape.logic_pure._frozen_enemy_unequip_engine")
    baseline.__package__ = "ankiscape.logic_pure"
    exec(compile(baseline_bytes, "frozen-enemy-unequip-engine.py", "exec"), baseline.__dict__)
    rows = []
    for label, player, chunks, live, expected in cases():
        before = capture(baseline.apply_combat_burst_pure, player, chunks, live)
        after = capture(candidate.apply_combat_burst_pure, player, chunks, live)
        observed = route_observation(after, player)
        route_pass = (
            observed["item"] == expected["item"]
            and observed["slot"] == expected["slot"]
            and observed["equipment_removed"]
            and (not expected["item"] or observed["bank_delta"] >= 1)
            and (not expected["item"] or observed["pack_delta"] >= 1)
            and (
                "condition" not in expected
                or (
                    observed["condition"] == expected["condition"]
                    and observed["instance_location"] == "bank"
                )
            )
            and (not live or observed["encounter_target"] == "chaos_elemental")
        )
        row = {
            "case": label,
            "equal": before == after,
            "route_expected": expected,
            "route_observed": observed,
            "route_pass": route_pass,
            "rng_calls": len(after[-1][1][2]),
            "baseline_pickle_base64": base64.b64encode(
                pickle.dumps(before, protocol=4)
            ).decode(),
            "candidate_pickle_base64": base64.b64encode(
                pickle.dumps(after, protocol=4)
            ).decode(),
        }
        rows.append(row)
        output.write_text(json.dumps({"cases": rows}, indent=2) + "\n")
    return rows


def source_hashes(root, expected):
    actual = {
        path: hashlib.sha256((root / path).read_bytes()).hexdigest()
        for path in expected
    }
    assert actual == expected, "Source inventory differs."
    return actual


def main():
    if sys.flags.optimize or "PYTHONOPTIMIZE" in os.environ:
        raise SystemExit("Refusing to run with optimizations; the pins are assertions.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--inventory-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    inventory_bytes = args.inventory.read_bytes()
    baseline_stored = args.baseline.read_bytes()
    assert hashlib.sha256(inventory_bytes).hexdigest() == args.inventory_sha256, (
        "Inventory hash differs."
    )
    assert hashlib.sha256(baseline_stored).hexdigest() == BASELINE_STORED_SHA256, (
        "Stored baseline hash differs."
    )
    baseline_bytes = gzip.decompress(baseline_stored)
    assert hashlib.sha256(baseline_bytes).hexdigest() == BASELINE_SHA256, (
        "Baseline source hash differs."
    )
    expected = json.loads(gzip.decompress(inventory_bytes))
    before = source_hashes(root, expected)
    assert before[ENGINE_PATH] == args.candidate_sha256, "Candidate source hash differs."
    report = {
        "baseline_sha256": BASELINE_SHA256,
        "inventory_sha256": args.inventory_sha256,
        "sources_before": before,
    }
    if args.preflight:
        report.update(status="PREFLIGHT_PASS", product_imported=False)
    else:
        sys.path.insert(0, str(root))
        rows = compare(baseline_bytes, args.output)
        report.update(
            cases=rows,
            status=(
                "PASS"
                if all(row["equal"] and row["route_pass"] for row in rows)
                else "FAIL"
            ),
        )
    report["sources_after"] = source_hashes(root, expected)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] == "FAIL":
        raise SystemExit("Enemy unequip comparison or route assertions failed.")


if __name__ == "__main__":
    main()
