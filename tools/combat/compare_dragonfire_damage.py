"""Compare ordinary dragonfire bursts with the frozen P5 engine."""

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


BASELINE_SHA256 = "9b1265b5600971f8a6927773d5e840595fa1864ccb3459979471d5b3522db585"
ENGINE_PATH = "logic_pure/logic_pure_combat_engine.py"
SPECIALS_PATH = "logic_pure/logic_pure_combat_specials.py"


def _player(**overrides):
    from tests.test_combat_logic import _player as combat_player

    player = combat_player(
        current_combat_target="green_dragon_test",
        constitution_level=99,
        combat_lifepoints=990,
        combat_auto_flee=False,
    )
    player.update(overrides)
    return player


def _enemy_data():
    from ankiscape.data.combat_data import COMBAT_ENEMY_DATA

    return {
        "green_dragon_test": {
            **COMBAT_ENEMY_DATA["green_dragon"],
            "wilderness_risk": {},
            "attack_speed": 1,
        }
    }


def cases():
    tier_cases = (
        ("none", {}, 500),
        ("shield", {"equipment": {"shield": "Anti-dragon shield"}}, 50),
        (
            "protect-magic",
            {
                "prayer_level": 99,
                "combat_prayer_points": 990,
                "combat_prayer_uptime": "100",
                "combat_selected_prayers": ["protect_from_magic"],
            },
            50,
        ),
        (
            "antifire-and-shield",
            {
                "equipment": {"shield": "Anti-dragon shield"},
                "combat_antifire_ticks_remaining": 600,
            },
            0,
        ),
        ("super-antifire", {"combat_super_antifire_ticks_remaining": 600}, 0),
    )
    for label, overrides, expected_damage in tier_cases:
        yield (
            f"tier:{label}",
            _player(**overrides),
            2,
            (1.0, 0.0, 0.999999),
            {
                "ok": True,
                "dragonfire_attacks": 1,
                "dragonfire_damage": expected_damage,
                "enemy_damage": expected_damage,
                "player_lifepoints": 990 - expected_damage,
                "rng_calls": 4,
            },
        )
    for label, roll, expected_damage in (
        ("negative", -1.0, 0),
        ("zero", 0.0, 0),
        ("middle", 0.5, 250),
        ("upper-inside", 0.999999, 500),
        ("upper-clamped", 1.0, 500),
        ("invalid", "invalid", 0),
    ):
        yield (
            f"roll:{label}",
            _player(),
            2,
            (1.0, 0.0, roll),
            {
                "ok": True,
                "dragonfire_attacks": 1,
                "dragonfire_damage": expected_damage,
                "enemy_damage": expected_damage,
                "player_lifepoints": 990 - expected_damage,
                "rng_calls": 4,
            },
        )
    yield (
        "expiry:auto-refresh",
        _player(
            equipment={"shield": "Anti-dragon shield"},
            combat_antifire_ticks_remaining=2,
            combat_supply_loadout={"potions": {"Antifire (4)": 1}},
        ),
        4,
        (1.0, 0.0, 0.0, 0.0, 0.0),
        {
            "ok": True,
            "potions_used": [
                {"item": "Antifire (4)", "effect": "antifire", "ticks": 600}
            ],
            "remaining_antifire": 598,
            "potions": {"Antifire (3)": 1},
        },
    )


def capture(module, player, ticks, prefix):
    from ankiscape.core.constants import EQUIPMENT_DATA
    from tools.combat.compare_kill_rewards import RecordedRandom

    current = deepcopy(player)
    enemies = _enemy_data()
    equipment = deepcopy(EQUIPMENT_DATA)
    supplied_player = deepcopy(current)
    supplied_enemies = deepcopy(enemies)
    supplied_equipment = deepcopy(equipment)
    rng = RecordedRandom(prefix)
    result = module.apply_combat_burst_pure(
        current,
        enemies,
        equipment,
        ticks=ticks,
        rng=rng.random,
    )
    assert current == supplied_player, "The burst mutated the supplied player."
    assert enemies == supplied_enemies, "The burst mutated the supplied enemies."
    assert equipment == supplied_equipment, "The burst mutated the supplied equipment."
    return deepcopy(result), rng.snapshot()


def route_observation(captured):
    result, rng_state = captured
    player, ok, summary = result
    return {
        "ok": ok,
        "dragonfire_attacks": summary["dragonfire_attacks"],
        "dragonfire_damage": summary["dragonfire_damage"],
        "enemy_damage": summary["enemy_damage"],
        "player_lifepoints": player["combat_lifepoints"],
        "potions_used": list(summary["potions_used"]),
        "remaining_antifire": player.get("combat_antifire_ticks_remaining", 0),
        "potions": (player.get("combat_supply_loadout", {}) or {}).get("potions", {}),
        "rng_calls": len(rng_state[2]),
        "rng_draws": list(rng_state[2]),
    }


def compare(baseline_bytes, output):
    import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
    from ankiscape.logic_pure import logic_pure_combat_engine as candidate

    baseline = types.ModuleType("ankiscape.logic_pure._frozen_dragonfire_engine")
    exec(
        compile(baseline_bytes, "frozen-dragonfire-engine.py", "exec"),
        baseline.__dict__,
    )
    rows = []
    for label, player, ticks, prefix, expected in cases():
        before = capture(baseline, player, ticks, prefix)
        after = capture(candidate, player, ticks, prefix)
        before_bytes = pickle.dumps(before, protocol=4)
        after_bytes = pickle.dumps(after, protocol=4)
        observed = route_observation(after)
        row = {
            "case": label,
            "equal": before == after,
            "pickle_bytes_equal": before_bytes == after_bytes,
            "route_expected": expected,
            "route_observed": observed,
            "route_pass": all(observed[key] == value for key, value in expected.items()),
            "baseline_pickle_base64": base64.b64encode(before_bytes).decode(),
            "candidate_pickle_base64": base64.b64encode(after_bytes).decode(),
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
    parser.add_argument("--candidate-engine-sha256", required=True)
    parser.add_argument("--candidate-specials-sha256", required=True)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--inventory-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    inventory_bytes = args.inventory.read_bytes()
    baseline_bytes = args.baseline.read_bytes()
    assert hashlib.sha256(inventory_bytes).hexdigest() == args.inventory_sha256, (
        "Inventory hash differs."
    )
    assert hashlib.sha256(baseline_bytes).hexdigest() == BASELINE_SHA256, (
        "Baseline source hash differs."
    )
    expected = json.loads(gzip.decompress(inventory_bytes))
    before = source_hashes(root, expected)
    assert before[ENGINE_PATH] == args.candidate_engine_sha256, (
        "Candidate engine source hash differs."
    )
    assert before[SPECIALS_PATH] == args.candidate_specials_sha256, (
        "Candidate specials source hash differs."
    )
    report = {
        "baseline_sha256": BASELINE_SHA256,
        "inventory_sha256": args.inventory_sha256,
        "sources_before": before,
    }
    if args.preflight:
        product_modules = sorted(
            name
            for name in sys.modules
            if name.split(".")[0] in {"ankiscape", "pkg_alias", "tests"}
        )
        assert not product_modules, {"product_modules": product_modules}
        report.update(
            status="PREFLIGHT_PASS",
            product_imported=bool(product_modules),
            product_modules=product_modules,
        )
    else:
        sys.path.insert(0, str(root))
        rows = compare(baseline_bytes, args.output)
        passed = all(
            row["equal"] and row["pickle_bytes_equal"] and row["route_pass"]
            for row in rows
        )
        report.update(cases=rows, status="PASS" if passed else "FAIL")
    report["sources_after"] = source_hashes(root, expected)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] == "FAIL":
        raise SystemExit("Dragonfire comparison or route assertions failed.")


if __name__ == "__main__":
    main()
