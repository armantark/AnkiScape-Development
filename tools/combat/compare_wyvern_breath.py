"""Compare complete Wyvern bursts with a frozen engine on an authorized host."""

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


BASELINE_SHA256 = "2b5a8a808f688cb179e59f882e58abefb1cb008d00cbca42e771d393d1c10ba8"
ENGINE_PATH = "logic_pure/logic_pure_combat_engine.py"


def cases():
    from tests.test_skeletal_wyvern import PROTECTIVE_SHIELD_IDS, _live_encounter_player

    for shield in PROTECTIVE_SHIELD_IDS:
        yield f"shield:{shield}", _live_encounter_player(equipment={"shield": shield}), (1,), True, 0.999999, 150
    for name, overrides in (
        ("none", {}),
        ("anti-dragon", {"equipment": {"shield": "Anti-dragon shield"}}),
        ("antifire", {"combat_antifire_ticks_remaining": 600}),
        ("super-antifire", {"combat_super_antifire_ticks_remaining": 600}),
    ):
        yield f"unprotected:{name}", _live_encounter_player(**overrides), (1,), True, 0.999999, 500
    for shield, damage in (("", 500), ("Elemental shield", 150)):
        for prayer in ("protect_from_melee", "protect_from_magic"):
            player = _live_encounter_player(
                equipment={"shield": shield}, prayer_level=99,
                combat_prayer_points=990, combat_prayer_uptime="100",
                combat_selected_prayers=[prayer],
            )
            yield f"prayer:{prayer}:shield={shield}", player, (1,), True, 0.999999, damage
    yield "ordinary-control", _live_encounter_player(), (1,), True, 0.0, None
    for shield, damage in (("", 500), ("Elemental shield", 150)):
        player = _live_encounter_player(equipment={"shield": shield})
        yield f"legacy:shield={shield}", player, (7,), False, 0.999999, damage
        yield f"resumed:shield={shield}", player, (1, 1), True, 0.999999, damage


def capture(module, player, chunks, live, roll):
    from ankiscape.core.constants import EQUIPMENT_DATA
    from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
    from tools.combat.compare_kill_rewards import RecordedRandom

    current = deepcopy(player)
    enemies, equipment = deepcopy(COMBAT_ENEMY_DATA), deepcopy(EQUIPMENT_DATA)
    rng, steps = RecordedRandom((roll,) * 100), []
    for ticks in chunks:
        supplied = deepcopy(current)
        result = module.apply_combat_burst_pure(
            current, enemies, equipment, ticks=ticks, live_cadence=live,
            rng=rng.random,
        )
        assert current == supplied and result[1], result
        steps.append((deepcopy(result), rng.snapshot()))
        current = result[0]
    assert enemies == COMBAT_ENEMY_DATA and equipment == EQUIPMENT_DATA, "Burst input mutation."
    return steps


def route_observation(steps):
    results = [step[0][2] for step in steps]
    return {
        "damage": sum(result["enemy_damage"] for result in results),
        "unprotected": sum(result["unprotected_attacks"] for result in results),
        "events": [event for result in results for event in result["enemy_specials"]],
        "remaining": [step[0][0]["combat_encounter"].get("player_attack_ticks_remaining") for step in steps],
        "steps": len(steps), "rng_calls": len(steps[-1][1][2]),
    }


def route_expectation(player, chunks, live, damage):
    shield = str((player.get("equipment", {}) or {}).get("shield", ""))
    events = [] if damage is None else [{
        "kind": "wyvern_breath", "protected": damage == 150,
        "shield_item": shield, "max_hit": damage, "delay_ticks": 5,
    }]
    remaining = [None]
    if live:
        remaining = [3] if damage is None else [8 - index for index in range(len(chunks))]
    return {
        "damage": 1 if damage is None else damage,
        "unprotected": int(damage == 500), "events": events,
        "remaining": remaining, "steps": len(chunks),
        "rng_calls": 5 if damage is None else (3 if live else 4),
    }


def compare(baseline_bytes, output):
    import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
    from ankiscape.logic_pure import logic_pure_combat_engine as candidate

    baseline = types.ModuleType("ankiscape.logic_pure._frozen_wyvern_engine")
    exec(compile(baseline_bytes, "frozen-wyvern-engine.py", "exec"), baseline.__dict__)
    rows = []
    for label, player, chunks, live, roll, damage in cases():
        before = capture(baseline, player, chunks, live, roll)
        after = capture(candidate, player, chunks, live, roll)
        before_bytes = pickle.dumps(before, protocol=4)
        after_bytes = pickle.dumps(after, protocol=4)
        expected = route_expectation(player, chunks, live, damage)
        observed = route_observation(after)
        rows.append({
            "case": label, "equal": before == after,
            "pickle_bytes_equal": before_bytes == after_bytes,
            "route_expected": expected, "route_observed": observed,
            "route_pass": observed == expected,
            "rng_calls": len(after[-1][1][2]),
            "baseline_pickle_base64": base64.b64encode(before_bytes).decode(),
            "candidate_pickle_base64": base64.b64encode(after_bytes).decode(),
        })
        output.write_text(json.dumps({"cases": rows}, indent=2) + "\n")
    return rows


def source_hashes(root, expected):
    actual = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in expected}
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
    inventory_bytes, baseline_bytes = args.inventory.read_bytes(), args.baseline.read_bytes()
    assert hashlib.sha256(inventory_bytes).hexdigest() == args.inventory_sha256, "Inventory hash differs."
    assert hashlib.sha256(baseline_bytes).hexdigest() == BASELINE_SHA256, "Baseline source hash differs."
    expected = json.loads(gzip.decompress(inventory_bytes))
    before = source_hashes(root, expected)
    assert before[ENGINE_PATH] == args.candidate_sha256, "Candidate source hash differs."
    report = {"baseline_sha256": BASELINE_SHA256, "inventory_sha256": args.inventory_sha256, "sources_before": before}
    if args.preflight:
        product_modules = sorted(name for name in sys.modules if name.split(".")[0] in {"ankiscape", "pkg_alias", "tests"})
        assert not product_modules, {"product_modules": product_modules}
        report.update(status="PREFLIGHT_PASS", product_imported=bool(product_modules), product_modules=product_modules)
    else:
        sys.path.insert(0, str(root))
        rows = compare(baseline_bytes, args.output)
        passed = all(row["equal"] and row["pickle_bytes_equal"] and row["route_pass"] for row in rows)
        report.update(cases=rows, status="PASS" if passed else "FAIL")
    report["sources_after"] = source_hashes(root, expected)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] == "FAIL":
        raise SystemExit("Wyvern comparison or route assertions failed.")


if __name__ == "__main__":
    main()
