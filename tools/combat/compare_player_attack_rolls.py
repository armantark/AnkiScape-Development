"""Compare full bursts against the frozen player-roll baseline on an authorized host."""

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
from unittest.mock import patch


BASELINE_SHA256 = "486a532d00d4e5693894b77a022ef83a32e03f55e841c2ff92ab12fc7e9ad2d4"
ENGINE_PATH = "logic_pure/logic_pure_combat_engine.py"


def cases():
    from tests.combat.test_player_attack_rolls import charge_player, drain_player, guild_player

    for combat_class, skill in (("melee", "attack"), ("ranged", "ranged"), ("magic", "magic")):
        expected = {"combat_class": combat_class, "drained": False}
        yield f"initial:{combat_class}", drain_player(combat_class), (1,), False, (0.999999,) * 50, expected
        for live, chunks in ((False, (19,)), (True, (7, 12))):
            expected = {"combat_class": combat_class, "drained": True, skill + "_drained": True}
            yield f"drain:{combat_class}:live={live}", drain_player(combat_class), chunks, live, (0.999999,) * 50, expected
    yield "rng-seeded:melee", drain_player("melee"), (9,), False, (), {"combat_class": "melee", "attack_drained": True}
    for blocked in (False, True):
        prayers = ("protect_from_magic",) if blocked else ()
        expected = {"combat_class": "magic", "unprotected": True, "drained": not blocked}
        yield f"spectre:blocked={blocked}", drain_player("magic", "aberrant_spectre", prayers), (13,), False, (0.999999,) * 50, expected
    yield "basilisk:prayer-still-drains", drain_player("magic", prayers=("protect_from_melee",)), (19,), False, (0.999999,) * 50, {"combat_class": "magic", "magic_drained": True, "enemy_damage": 0}
    for prayer in ("eagle_eye", "rigour"):
        expected = {"combat_class": "ranged", "ranged_drained": True, prayer: True}
        yield f"ranged-prayer:{prayer}", drain_player("ranged", prayers=(prayer,)), (19,), False, (0.999999,) * 50, expected
    for active, maximum in ((False, 20), (True, 30)):
        expected = {"combat_class": "magic", "spell_id": "saradomin_strike", "first_max": maximum, "last_max": maximum, "drained": False}
        yield f"charge:{active}", charge_player(active), (1,), False, (0.0, 0.999999), expected
    yield "charge:after-drain", charge_player(True), (19,), False, (0.999999,) * 50, {"combat_class": "magic", "magic_drained": True, "first_max": 30, "last_max": 30}
    for payment in ("single", "multi"):
        yield f"guild:{payment}", guild_player(payment), (1,), False, (0.0, 0.999999), {"combat_class": "melee", "guild_calls": 1, "drained": False}


def capture(module, player, chunks, live, prefix, combat_class):
    from ankiscape.core.constants import EQUIPMENT_DATA
    from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
    from tools.combat.compare_kill_rewards import RecordedRandom

    current, enemies, equipment = deepcopy(player), deepcopy(COMBAT_ENEMY_DATA), deepcopy(EQUIPMENT_DATA)
    formula_name = {"melee": "_combat_melee_max_hit_old_hp", "ranged": "_combat_ranged_max_hit_old_hp", "magic": "_combat_magic_max_hit_old_hp"}[combat_class]
    original, maxima, steps, rng = getattr(module, formula_name), [], [], RecordedRandom(prefix)

    initial_rng_state = rng.getstate()

    def record_max(*args):
        value = original(*args)
        maxima.append(value)
        return value

    with patch.object(module, formula_name, side_effect=record_max), patch.object(module, "warriors_guild_cyclops_damage_multiplier_pure", wraps=module.warriors_guild_cyclops_damage_multiplier_pure) as guild:
        for ticks in chunks:
            supplied = deepcopy(current)
            result = module.apply_combat_burst_pure(current, enemies, equipment, ticks=ticks, live_cadence=live, rng=rng.random)
            assert current == supplied and result[1], result
            steps.append((deepcopy(result), rng.snapshot(), list(maxima), guild.call_count))
            current = result[0]
    if not prefix:
        assert rng.getstate() != initial_rng_state and rng.draws, "Seeded RNG route was not reached."
    assert enemies == COMBAT_ENEMY_DATA and equipment == EQUIPMENT_DATA, "Burst input mutation."
    return steps


def route_observation(steps):
    results = [step[0][2] for step in steps]
    last = results[-1]
    drains = {skill for result in results for skill, amount in result["stat_drains"].items() if amount > 0}
    prayers = {prayer for result in results for prayer in result["prayers"]}
    return {
        "combat_class": last["combat_class"], "spell_id": last["spell_id"],
        "drained": bool(drains), "attack_drained": "attack" in drains,
        "ranged_drained": "ranged" in drains, "magic_drained": "magic" in drains,
        "unprotected": any(result["unprotected_attacks"] > 0 for result in results),
        "enemy_damage": sum(result["enemy_damage"] for result in results),
        "rigour": "rigour" in prayers, "eagle_eye": "eagle_eye" in prayers,
        "first_max": steps[-1][2][0], "last_max": steps[-1][2][-1],
        "guild_calls": steps[-1][3],
    }


def compare(baseline_bytes, output):
    import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
    from ankiscape.logic_pure import logic_pure_combat_engine as candidate

    baseline = types.ModuleType("ankiscape.logic_pure._frozen_player_attack_engine")
    exec(compile(baseline_bytes, "frozen-player-attack-engine.py", "exec"), baseline.__dict__)
    rows = []
    for label, player, chunks, live, prefix, expected in cases():
        before = capture(baseline, player, chunks, live, prefix, expected["combat_class"])
        after = capture(candidate, player, chunks, live, prefix, expected["combat_class"])
        observed = route_observation(after)
        row = {
            "case": label, "equal": before == after,
            "route_expected": expected, "route_observed": observed,
            "route_pass": all(observed[key] == value for key, value in expected.items()),
            "rng_calls": len(after[-1][1][2]),
            "baseline_pickle_base64": base64.b64encode(pickle.dumps(before, protocol=4)).decode(),
            "candidate_pickle_base64": base64.b64encode(pickle.dumps(after, protocol=4)).decode(),
        }
        rows.append(row)
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
        report.update(status="PREFLIGHT_PASS", product_imported=False)
    else:
        sys.path.insert(0, str(root))
        rows = compare(baseline_bytes, args.output)
        report.update(cases=rows, status="PASS" if all(row["equal"] and row["route_pass"] for row in rows) else "FAIL")
    report["sources_after"] = source_hashes(root, expected)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] == "FAIL":
        raise SystemExit("Player attack comparison or route assertions failed.")


if __name__ == "__main__":
    main()
