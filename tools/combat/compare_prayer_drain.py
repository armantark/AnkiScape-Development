"""Compare complete prayer-drain bursts with the frozen canonical engine."""

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


BASELINE_COMMIT = "6dacde5486c72e73ca170c039bf8207dec22ac81"
BASELINE_SHA256 = "5f641672a316655fa63a25ce9ea5d24a80645f362f338df1929a8808a253936b"
BASELINE_STORED_SHA256 = "1e3f72610e12711057b32af3e07bfbdb41be10b17228036750ff390fdadd90b6"
BASELINE_SPECIALS_SHA256 = "b165f3f63f1de2fbffeec9c0ee79df498c1614f05872ed7e911e7b86fd5601ca"
BASELINE_SPECIALS_STORED_SHA256 = "5f950f453fca4a5c98a064f4d30f22a7072a42079de662fdf75185eceb805330"
ENGINE_PATH = "logic_pure/logic_pure_combat_engine.py"
SPECIALS_PATH = "logic_pure/logic_pure_combat_specials.py"
TEST_PATH = "tests/combat/test_prayer_drain.py"


def source_guard(root, inventory, inventory_sha256):
    inventory_bytes = inventory.read_bytes()
    if hashlib.sha256(inventory_bytes).hexdigest() != inventory_sha256:
        raise ValueError("Inventory hash differs; product imports not started.")
    expected = json.loads(gzip.decompress(inventory_bytes))
    for required in (ENGINE_PATH, SPECIALS_PATH, TEST_PATH):
        if required not in expected:
            raise ValueError(f"Inventory omits {required}; product imports not started.")
    actual = {}
    for name, pin in expected.items():
        source = root / name
        if not source.is_file():
            raise ValueError(f"Source missing: {name}; product imports not started.")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != pin:
            raise ValueError(f"Source differs: {name}; product imports not started.")
        actual[name] = digest
    evidence = root / "memory-bank/evidence/combat-prayer-drain-2026-09-08"
    baseline_path = evidence / "baseline-engine.py.gz"
    stored = baseline_path.read_bytes()
    if hashlib.sha256(stored).hexdigest() != BASELINE_STORED_SHA256:
        raise ValueError("Stored baseline hash differs; product imports not started.")
    baseline = gzip.decompress(stored)
    if hashlib.sha256(baseline).hexdigest() != BASELINE_SHA256:
        raise ValueError("Baseline source hash differs; product imports not started.")
    stored_specials = (evidence / "baseline-specials.py.gz").read_bytes()
    if hashlib.sha256(stored_specials).hexdigest() != BASELINE_SPECIALS_STORED_SHA256:
        raise ValueError("Stored specials baseline differs; product imports not started.")
    if hashlib.sha256(gzip.decompress(stored_specials)).hexdigest() != BASELINE_SPECIALS_SHA256:
        raise ValueError("Specials baseline source differs; product imports not started.")
    return actual, baseline


def cases():
    from tests.combat.test_prayer_drain import prayer_drain_fixture

    player, enemies = prayer_drain_fixture()
    enemies["prayer_drain_test"].pop("prayer_drain_base")
    yield "disabled:missing", player, enemies, (0.0, 0.999999), {
        "enemy_prayer_drain": 0,
        "prayer_points_after": 50,
        "enemy_damage": 0,
        "player_lifepoints": 990,
        "rng_calls": 2,
    }
    for label, base in (("invalid", "invalid"), ("negative", -10), ("zero", 0)):
        player, enemies = prayer_drain_fixture(base=base)
        yield f"disabled:{label}", player, enemies, (0.0, 0.999999), {
            "enemy_prayer_drain": 0,
            "prayer_points_after": 50,
            "enemy_damage": 0,
            "player_lifepoints": 990,
            "rng_calls": 2,
        }
    player, enemies = prayer_drain_fixture(damage_scaled=False)
    yield "enabled:base-only", player, enemies, (0.0, 0.999999), {
        "enemy_prayer_drain": 10,
        "prayer_points_after": 40,
        "enemy_damage": 0,
        "player_lifepoints": 990,
        "rng_calls": 2,
    }
    player, enemies = prayer_drain_fixture()
    yield "enabled:raw-damage-before-protection", player, enemies, (0.0, 0.999999), {
        "enemy_prayer_drain": 40,
        "prayer_points_after": 10,
        "enemy_damage": 0,
        "player_lifepoints": 990,
        "rng_calls": 2,
    }
    player, enemies = prayer_drain_fixture(prayer_points=12)
    yield "enabled:available-points-cap", player, enemies, (0.0, 0.999999), {
        "enemy_prayer_drain": 12,
        "prayer_points_after": 0,
        "enemy_damage": 0,
        "player_lifepoints": 990,
        "rng_calls": 2,
    }
    player, enemies = prayer_drain_fixture(prayer_points=0)
    yield "enabled:zero-available", player, enemies, (0.0, 0.999999), {
        "enemy_prayer_drain": 0,
        "prayer_points_after": 0,
        "enemy_damage": 30,
        "player_lifepoints": 960,
        "rng_calls": 2,
    }
    player, enemies = prayer_drain_fixture()
    yield "enabled:missed-hit", player, enemies, (1.0,), {
        "enemy_prayer_drain": 10,
        "prayer_points_after": 40,
        "enemy_damage": 0,
        "player_lifepoints": 990,
        "rng_calls": 1,
    }


def capture(function, player, enemies, prefix):
    from ankiscape.core.constants import EQUIPMENT_DATA
    from tools.combat.compare_kill_rewards import RecordedRandom

    supplied_player = deepcopy(player)
    supplied_enemies = deepcopy(enemies)
    supplied_equipment = deepcopy(EQUIPMENT_DATA)
    rng = RecordedRandom(prefix)
    result = function(
        supplied_player,
        supplied_enemies,
        supplied_equipment,
        ticks=1,
        live_cadence=True,
        rng=rng.random,
    )
    return {
        "return": deepcopy(result),
        "rng": rng.snapshot(),
        "inputs_unchanged": {
            "player": supplied_player == player,
            "enemies": supplied_enemies == enemies,
            "equipment": supplied_equipment == EQUIPMENT_DATA,
        },
    }


def route_observation(captured):
    updated, ok, result = captured["return"]
    draws = captured["rng"][2]
    return {
        "ok": ok,
        "enemy_prayer_drain": result["enemy_prayer_drain"],
        "prayer_points_after": result["prayer_points_after"],
        "stored_prayer_points": updated["combat_prayer_points"],
        "enemy_damage": result["enemy_damage"],
        "player_lifepoints": result["player_lifepoints"],
        "rng_calls": len(draws),
        "rng_draws": list(draws),
    }


def compare(baseline_bytes, output):
    import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
    from ankiscape.logic_pure import logic_pure_combat_engine as candidate

    baseline = types.ModuleType("ankiscape.logic_pure._frozen_prayer_drain_engine")
    baseline.__package__ = "ankiscape.logic_pure"
    exec(
        compile(baseline_bytes, "<frozen-prayer-drain-engine>", "exec"),
        baseline.__dict__,
    )
    rows = []
    for label, player, enemies, prefix, expected in cases():
        before = capture(baseline.apply_combat_burst_pure, player, enemies, prefix)
        after = capture(candidate.apply_combat_burst_pure, player, enemies, prefix)
        before_bytes = pickle.dumps(before, protocol=4)
        after_bytes = pickle.dumps(after, protocol=4)
        observed = route_observation(after)
        expected = {
            **expected,
            "ok": True,
            "stored_prayer_points": expected["prayer_points_after"],
            "rng_draws": list(prefix),
        }
        rows.append(
            {
                "case": label,
                "equal": before == after,
                "pickle_bytes_equal": before_bytes == after_bytes,
                "route_expected": expected,
                "route_observed": observed,
                "route_pass": observed == expected,
                "inputs_unchanged": after["inputs_unchanged"],
                "baseline_pickle_base64": base64.b64encode(before_bytes).decode(),
                "candidate_pickle_base64": base64.b64encode(after_bytes).decode(),
            }
        )
        output.write_text(json.dumps({"cases": rows}, indent=2) + "\n")
    return rows


def main():
    if sys.flags.optimize or "PYTHONOPTIMIZE" in os.environ:
        raise SystemExit("Optimized interpreter refused; product imports not started.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--inventory-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    sources, baseline = source_guard(args.root, args.inventory, args.inventory_sha256)
    report = {
        "baseline_commit": BASELINE_COMMIT,
        "baseline_sha256": BASELINE_SHA256,
        "inventory_sha256": args.inventory_sha256,
        "sources_before": sources,
    }
    if args.preflight:
        product_modules = sorted(
            name
            for name in sys.modules
            if name == "pkg_alias" or name.split(".")[0] in {"ankiscape", "tests"}
        )
        if product_modules:
            raise RuntimeError(f"Product imported during preflight: {product_modules}")
        report.update(
            status="PREFLIGHT_PASS",
            product_imported=False,
            product_modules=product_modules,
        )
    else:
        sys.path.insert(0, str(args.root))
        rows = compare(baseline, args.output)
        report.update(
            cases=rows,
            status=(
                "PASS"
                if all(
                    row["equal"]
                    and row["pickle_bytes_equal"]
                    and row["route_pass"]
                    and all(row["inputs_unchanged"].values())
                    for row in rows
                )
                else "FAIL"
            ),
        )
    report["sources_after"], _ = source_guard(
        args.root, args.inventory, args.inventory_sha256
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] == "FAIL":
        raise SystemExit("Prayer-drain comparison or route assertions failed.")


if __name__ == "__main__":
    main()
