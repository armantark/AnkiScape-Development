"""Compare complete enemy-poison bursts with the frozen canonical engine."""

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


BASELINE_COMMIT = "1bf2cfe2fa77cea2bb24528c6844d7473b1c2d12"
BASELINE_SHA256 = "934f0bccbdd7a11a0bde6df361d6355c0c339c2daf69e51d98b5b933952e4c49"
BASELINE_STORED_SHA256 = "334b2c069598e4e7f35ffdf555ac2e142b2b447b45d56b5924bad2134a348728"
BASELINE_SPECIALS_SHA256 = "3b74a4720bbc3135b1c87df910999d69607f0f41b67f4dbf126de4f60910b619"
BASELINE_SPECIALS_STORED_SHA256 = "a54bdebc535564774cdaa7ce7a15128e9217f759cb067f04bc39865fc34f478e"
ENGINE_PATH = "logic_pure/logic_pure_combat_engine.py"
SPECIALS_PATH = "logic_pure/logic_pure_combat_specials.py"
TEST_PATH = "tests/combat/test_enemy_poison_application.py"


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
    evidence = root / "memory-bank/evidence/combat-enemy-poison-2026-09-08"
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
    from tests.combat.test_enemy_poison_application import enemy_poison_cases

    yield from enemy_poison_cases()


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
    _updated, ok, result = captured["return"]
    draws = captured["rng"][2]
    return {
        "ok": ok,
        "status_applied": result["status_applied"],
        "potion_items": [event["item"] for event in result["potions_used"]],
        "rng_calls": len(draws),
        "rng_draws": list(draws),
    }


def compare(baseline_bytes):
    import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
    from ankiscape.logic_pure import logic_pure_combat_engine as candidate

    baseline = types.ModuleType("ankiscape.logic_pure._frozen_enemy_poison_application_engine")
    baseline.__package__ = "ankiscape.logic_pure"
    exec(
        compile(baseline_bytes, "<frozen-enemy-poison-engine>", "exec"),
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
            "rng_calls": len(prefix),
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
        rows = compare(baseline)
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
        raise SystemExit("Enemy-poison comparison or route assertions failed.")


if __name__ == "__main__":
    main()
