"""Compare complete Vampyre bursts against the frozen engine after source guards."""

import argparse
import base64
from copy import deepcopy
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import subprocess
import sys
import tempfile
import types

EVIDENCE = Path("memory-bank/evidence/combat-vampyre-bite-2026-09-07")
BASELINE_COMMIT = "7e19aadf16dc223d87669f064114c8ef1a9c4a85"
BASELINE_SHA256 = "486a532d00d4e5693894b77a022ef83a32e03f55e841c2ff92ab12fc7e9ad2d4"
BASELINE_STORED_SHA256 = "bf8ba8cb7c2eb12379ea703e1c3264abf6c3bfc9425497552030ec12311b2055"


def source_guard(root, inventory, inventory_sha256):
    raw = inventory.read_bytes()
    if hashlib.sha256(raw).hexdigest() != inventory_sha256:
        raise ValueError("Inventory hash differs; product imports not started.")
    expected = json.loads(gzip.decompress(raw))
    actual = {}
    for name, pin in expected.items():
        source = root / name
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != pin:
            raise ValueError(f"Source differs: {name}; product imports not started.")
        actual[name] = pin
    stored = (root / EVIDENCE / "baseline-engine.py.gz").read_bytes()
    if hashlib.sha256(stored).hexdigest() != BASELINE_STORED_SHA256:
        raise ValueError("Stored baseline hash differs; product imports not started.")
    baseline = gzip.decompress(stored)
    if hashlib.sha256(baseline).hexdigest() != BASELINE_SHA256:
        raise ValueError("Baseline source hash differs; product imports not started.")
    return actual, baseline


def bite_cases():
    from tests.combat.test_vampyre_bite import vampyre_player

    for label, bite_roll in (("miss", 0.125), ("invalid-value", "invalid"), ("invalid-type", None)):
        yield label, vampyre_player(), (1,), True, (0.0, 0.999999, bite_roll), {
            "bites": 0, "healing": 0, "drains": {}, "enemy_lp": 300,
        }
    for label, skill_roll, skill in (
        ("hit", 0.0, "attack"), ("second-skill", 0.05, "strength"),
        ("low-skill", -1.0, "attack"), ("high-skill", 1.0, "summoning"),
        ("invalid-skill-value", "invalid", "attack"), ("invalid-skill-type", None, "attack"),
    ):
        yield label, vampyre_player(summoning_level=10), (1,), True, (0.0, 0.999999, 0.0, skill_roll), {
            "bites": 1, "healing": 20, "drains": {skill: 1}, "enemy_lp": 320,
        }
    for label, enemy_lp, damage_roll, attack_level, healing in (
        ("drain-floor", 300, 0.999999, 1, 20),
        ("missing-lp-cap", 399, 0.999999, 10, 1),
        ("full-lp-cap", 400, 0.999999, 10, 0),
        ("damage-cap", 300, 0.0, 10, 1),
    ):
        yield label, vampyre_player(enemy_lp, attack_level=attack_level), (1,), True, (
            0.0, damage_roll, 0.0, 0.0,
        ), {"bites": 1, "healing": healing, "drains": {} if attack_level == 1 else {"attack": 1},
            "enemy_lp": enemy_lp + healing}
    yield "resumed-live", vampyre_player(), (1, 6), True, (0.0, 0.999999, 0.0, 0.0) * 2, {
        "bites": 2, "healing": 40, "drains": {"attack": 2}, "enemy_lp": 340,
    }
    yield "legacy", vampyre_player(), (7,), False, (0.999999, 0.999999, 0.0, 0.999999, 0.0, 0.0), {
        "bites": 1, "healing": 20, "drains": {"attack": 1}, "enemy_lp": 320,
    }
    reflected = vampyre_player(
        5, combat_attack_style="magic_standard", current_combat_spell="wind_strike",
        equipment={"weapon": "Staff of air"}, combat_vengeance=True,
        combat_spellbook_swap="vengeance", combat_supply_loadout={"runes": {"Mind rune": 10}},
        quests={"priest_in_peril": {"completed": True}, "lunar_diplomacy": {"completed": True}},
    )
    reflected["combat_encounter"].update(
        spellbook_swap_paid=True, vengeance_pending=True, vengeance_cast_paid=True,
    )
    yield "reflection-before-bite", reflected, (1,), True, (0.0, 0.999999), {
        "bites": 0, "healing": 0, "drains": {}, "kills": 1,
    }


def capture(function, player, chunks, live, prefix):
    from ankiscape.core.constants import EQUIPMENT_DATA
    from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
    from tools.combat.compare_kill_rewards import RecordedRandom

    current = deepcopy(player)
    enemies, equipment = deepcopy(COMBAT_ENEMY_DATA), deepcopy(EQUIPMENT_DATA)
    rng = RecordedRandom(prefix)
    steps = []
    for ticks in chunks:
        supplied = deepcopy(current)
        result = function(current, enemies, equipment, ticks=ticks, rng=rng.random, live_cadence=live)
        steps.append({"return": deepcopy(result), "rng": rng.snapshot(),
                      "input_unchanged": current == supplied})
        current = result[0]
    return {"steps": steps, "catalogs_unchanged": enemies == COMBAT_ENEMY_DATA and equipment == EQUIPMENT_DATA}


def route_observation(captured):
    results = [step["return"][2] for step in captured["steps"]]
    drains = {}
    for result in results:
        for skill, amount in result["stat_drains"].items():
            drains[skill] = drains.get(skill, 0) + amount
    return {
        "bites": sum(result["vampyre_bites"] for result in results),
        "healing": sum(result["vampyre_bite_healing"] for result in results),
        "drains": drains, "enemy_lp": results[-1]["enemy_lifepoints"],
        "kills": sum(result["kills"] for result in results),
    }


def compare(baseline_bytes, output):
    import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
    from ankiscape.logic_pure import logic_pure_combat_engine as candidate

    baseline = types.ModuleType("ankiscape.logic_pure._frozen_vampyre_bite_engine")
    baseline.__package__ = "ankiscape.logic_pure"
    exec(compile(baseline_bytes, "<frozen-vampyre-bite-engine>", "exec"), baseline.__dict__)
    rows = []
    for label, player, chunks, live, prefix, expected in bite_cases():
        before = capture(baseline.apply_combat_burst_pure, player, chunks, live, prefix)
        after = capture(candidate.apply_combat_burst_pure, player, chunks, live, prefix)
        observed = route_observation(after)
        steps = after["steps"]
        draws = steps[-1]["rng"][2]
        passed = (
            all(observed[key] == value for key, value in expected.items())
            and tuple(draws[:len(prefix)]) == prefix
            and (label == "reflection-before-bite" or len(draws) == len(prefix))
            and all(step["return"][1] and step["input_unchanged"] for step in steps)
            and after["catalogs_unchanged"]
        )
        before_pickle = pickle.dumps(before, protocol=4)
        after_pickle = pickle.dumps(after, protocol=4)
        rows.append({
            "case": label, "equal": before == after and before_pickle == after_pickle, "route_pass": passed,
            "expected": expected, "observed": observed, "rng_calls": len(draws),
            "baseline_pickle_base64": base64.b64encode(before_pickle).decode(),
            "candidate_pickle_base64": base64.b64encode(after_pickle).decode(),
        })
        output.write_bytes(gzip.compress((json.dumps({"cases": rows}, indent=2) + "\n").encode(), mtime=0))
    return rows


def forbid_product_imports(marker):
    class StopProductImports:
        def find_spec(self, fullname, path=None, _target=None):
            if fullname == "pkg_alias" or fullname.split(".")[0] in ("ankiscape", "tests"):
                marker.write_text(fullname)
                raise RuntimeError("Product import attempted during preflight.")
    sys.meta_path.insert(0, StopProductImports())


def check_canaries(args):
    raw = args.inventory.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.inventory_sha256:
        raise ValueError("Inventory hash differs; canary inputs not trusted.")
    expected = json.loads(gzip.decompress(raw))
    first = next(iter(expected))
    results = []
    with tempfile.TemporaryDirectory(prefix="vampyre-source-canaries-") as temporary:
        scratch = Path(temporary)
        changed, missing = scratch / "changed", scratch / "missing"
        missing.mkdir()
        source = changed / first
        source.parent.mkdir(parents=True)
        source.write_bytes(b"changed source canary\n")
        for label, root, pin, message in (
            ("inventory", args.root, "0" * 64, "Inventory hash differs"),
            ("changed-source", changed, args.inventory_sha256, f"Source differs: {first}"),
            ("missing-source", missing, args.inventory_sha256, f"Source differs: {first}"),
            ("optimized", args.root, args.inventory_sha256, "Optimized interpreter refused; product imports not started."),
            ("optimization-environment", args.root, args.inventory_sha256, "Optimized interpreter refused; product imports not started."),
        ):
            output = scratch / f"{label}.json"
            command = [sys.executable, str(Path(__file__).resolve()), "--root", str(root),
                       "--inventory", str(args.inventory), "--inventory-sha256", pin,
                       "--output", str(output), "--preflight"]
            if label == "optimized":
                command.insert(1, "-O")
            environment = None
            if label == "optimization-environment":
                environment = {**os.environ, "PYTHONOPTIMIZE": "0"}
                wrapper = ("import runpy,sys; print('optimization_flags=' + str(sys.flags.optimize)); "
                           "sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0], run_name='__main__')")
                command = [command[0], "-c", wrapper, *command[1:]]
            process = subprocess.run(command, capture_output=True, text=True, check=False, env=environment)
            passed = (process.returncode != 0 and message in process.stderr
                      and not output.exists() and not output.with_suffix(".import").exists())
            if label in ("optimized", "optimization-environment"):
                passed = passed and process.stderr.strip() == message
            if label == "optimization-environment":
                passed = passed and process.stdout.strip() == "optimization_flags=0"
            results.append({"case": label, "passed": passed, "returncode": process.returncode,
                            "stdout": process.stdout, "stderr": process.stderr})
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    if not all(row["passed"] for row in results):
        raise SystemExit("Pre-import canary failed; runtime remains prohibited.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--inventory-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--canaries", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        forbid_product_imports(args.output.with_suffix(".import"))
    if sys.flags.optimize or "PYTHONOPTIMIZE" in os.environ:
        raise SystemExit("Optimized interpreter refused; product imports not started.")
    if args.canaries:
        check_canaries(args)
        return
    sources, baseline = source_guard(args.root, args.inventory, args.inventory_sha256)
    report = {"baseline_commit": BASELINE_COMMIT, "baseline_sha256": BASELINE_SHA256,
              "inventory_sha256": args.inventory_sha256, "sources_before": sources}
    if args.preflight:
        product_imported = args.output.with_suffix(".import").exists()
        if product_imported:
            raise RuntimeError("Product import sentinel exists; preflight refused.")
        report.update(status="PREFLIGHT_PASS", product_imported=product_imported)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        return
    sys.path.insert(0, str(args.root))
    rows = compare(baseline, args.output)
    report.update(cases=rows, status="PASS" if all(row["equal"] and row["route_pass"] for row in rows) else "FAIL")
    report["sources_after"], _ = source_guard(args.root, args.inventory, args.inventory_sha256)
    args.output.write_bytes(gzip.compress((json.dumps(report, indent=2) + "\n").encode(), mtime=0))
    if report["status"] == "FAIL":
        raise SystemExit("Complete burst comparison or route proof failed.")


if __name__ == "__main__":
    main()
