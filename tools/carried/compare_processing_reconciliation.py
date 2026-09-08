"""Compare frozen and candidate carried wrappers after whole-source guards pass."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import types
from unittest.mock import patch

EVIDENCE = Path("memory-bank/evidence/carried-processing-reconciliation-2026-09-07")
BASELINE = "0005e1cb42530706ab9ceb85e5be80ce3a0685f9"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify_sources(root, manifest_path, expected_sha):
    raw = manifest_path.read_bytes()
    if sha(raw) != expected_sha:
        raise ValueError("manifest SHA256 mismatch; product imports not started")
    manifest = json.loads(gzip.decompress(raw))
    if manifest["baseline_commit"] != BASELINE:
        raise ValueError("baseline commit mismatch; product imports not started")
    for name, expected in manifest["files"].items():
        source = root / name
        if not source.is_file() or sha(source.read_bytes()) != expected:
            raise ValueError(f"source mismatch: {name}; product imports not started")
    frozen = gzip.decompress((root / EVIDENCE / "baseline-overlay.py.gz").read_bytes())
    if sha(frozen) != manifest["baseline_overlay_sha256"]:
        raise ValueError("frozen source mismatch; product imports not started")
    return manifest, frozen


def load_wrappers(root, frozen):
    sys.path.insert(0, str(root))
    import pkg_alias  # noqa: F401
    from ankiscape.runtime import runtime_actions_carried_overlay as candidate

    baseline = types.ModuleType("ankiscape.runtime._frozen_carried_overlay")
    baseline.__package__ = "ankiscape.runtime"
    exec(compile(frozen, "<frozen-carried-overlay>", "exec"), baseline.__dict__)
    return baseline, candidate


def context(player, events):
    import dataclasses
    from tests.test_runtime_actions import _context

    ctx = _context(player, random_values=[0.0] * 200)
    for field in dataclasses.fields(ctx):
        callback = getattr(ctx, field.name)
        if callable(callback):
            setattr(ctx, field.name, trace_callback(field.name, callback, player, events))
    return ctx


def trace_callback(name, callback, player, events):
    def observed(*args):
        events.append([name, copy.deepcopy(args), copy.deepcopy(player)])
        result = callback(*args)
        events.append(["return", name, copy.deepcopy(result), copy.deepcopy(player)])
        return result
    return observed


def fake_handler(config, events):
    def handler(ctx):
        events.append(["handler_start", copy.deepcopy(ctx.player_data)])
        ctx.random_random()
        inventory = ctx.player_data["inventory"]
        if config["replace"]:
            inventory = dict(inventory)
        inventory.update(config["after"])
        if config.get("child_cadence"):
            ctx.player_data["cadence_profiles"]["probe"] += 1
        ctx.player_data["inventory"] = inventory
        ctx.check_achievements(ctx.player_data)
        ctx.refresh_skill_availability()
        ctx.save_player_data()
        events.append(["handler_end", copy.deepcopy(ctx.player_data)])
        return config["result"]
    return handler


def fixture_player():
    stock = {"Input": 100, "Tool": 1, "Potion": 10, "Hidden potion": 9, "Alt": 8}
    return {
        "cadence_profiles": {"probe": 0},
        "inventory": stock, "current_fletch": "probe", "fletching_level": 99,
        "completed_achievements": [], "carried_advanced_targets": {"probe": True},
        "carried_primed_targets": {"probe": True},
        "carried_inventory": {"probe": {"Input": 5, "Tool": 1, "Potion": 2, "Zero": 0}},
        "carried_churn": {"probe": 0}, "skilling_bank_run": {},
    }


def run_fixture(module, config):
    player, events = fixture_player(), []
    if config.get("winter"):
        player["inventory"]["Winter storage scroll"] = 1
        player["carried_inventory"]["probe"]["Winter storage scroll"] = 1
        player["carried_churn"]["probe"] = 28
        player["summoning_state"] = {
            "active_follower": {"kind": "familiar", "entity_id": "packyak"},
            "special_move_points_current": 20,
            "target_policies": {"probe": {"winter_storage_priority": ["Input"]}},
        }
    requirements = {"Input": 1}
    presence = {"Tool": 1}
    consumables = {"Potion": 1}
    if config["repeated"]:
        presence["Input"] = 1
        consumables["Input"] = 1

    def admission(ctx, _skill, _target):
        ctx.player_data["cadence_profiles"]["probe"] += 1
        events.append(["cadence_admission", copy.deepcopy(player)])
        return ctx, True

    substitutions = {
        "_admit_live_cadence": admission,
        "_processing_requirements_for": lambda *_args: requirements,
        "_processing_presence_requirements_for": lambda *_args: presence,
        "_skilling_potion_requirement_for": lambda *_args, **_kw: consumables,
        "skilling_potion_items_for_skill": lambda _skill: ("Potion", "Hidden potion", "Absent potion"),
        "FLETCHING_DATA": {"probe": {"material_options": {"Input": ["Input", "Alt", "Absent alt"]}}},
    }
    with patch.multiple(module, **substitutions):
        result = module.run_answer_with_carried_overlay(
            context(player, events), "fletching", fake_handler(config, events)
        )
    assert sum(event[0] == "handler_start" for event in events) == 1
    if config.get("winter"):
        attempted = next(event[1] for event in events if event[0] == "handler_start")
        assert attempted["summoning_state"]["special_move_points_current"] == 8
        assert player["summoning_state"]["special_move_points_current"] == 20
    if config.get("child_cadence"):
        assert player["cadence_profiles"]["probe"] == 2
    return {"result": result, "result_type": type(result).__name__, "player": player, "events": events}


def fixture_cases():
    for replaced in (False, True):
        for label, result, amount in (
            ("partial", True, 3), ("rejected", False, 3),
            ("none_return", None, 3), ("zero_return", 0, 3),
            ("dry", True, 5), ("output_over_input", True, 7),
        ):
            yield f"{label}-replace-{replaced}", {
                "replace": replaced, "result": result, "repeated": True,
                "after": {"Input": amount, "Potion": 0, "Output": 2,
                          "Absent potion": 3, "Absent alt": 4},
            }

    for winter, child in ((True, False), (False, True)):
        yield f"rejection-winter-{winter}-child-cadence-{child}", {
            "replace": True, "result": False, "repeated": False,
            "winter": winter, "child_cadence": child, "after": {"Input": 3},
        }


def real_trip(module):
    from ankiscape.runtime.runtime_actions_production import handle_firemaking_answer

    player = {"inventory": {"Logs": 30}, "firemaking_level": 1, "firemaking_exp": 0,
              "current_firemaking": "logs", "completed_achievements": []}
    events, steps = [], []

    def handler(ctx):
        events.append(["handler_start", copy.deepcopy(player)])
        result = handle_firemaking_answer(ctx)
        events.append(["handler_end", copy.deepcopy(player)])
        return result

    for _ in range(30):
        result = module.run_answer_with_carried_overlay(context(player, events), "firemaking", handler)
        steps.append({"result": result, "player": copy.deepcopy(player)})
    # A comparator must prove that its advertised route actually occurred.
    assert steps[0]["player"]["carried_inventory"]["logs"] == {"Logs": 27}
    assert steps[27]["player"]["inventory"]["Logs"] == 2
    assert steps[28]["player"]["inventory"]["Ashes"] == 28
    assert steps[28]["player"]["carried_inventory"]["logs"] == {"Logs": 2}
    assert steps[29]["player"]["inventory"]["Ashes"] == 29
    return {"steps": steps, "events": events, "player": player}


def advanced_cases():
    # Same recipes/layouts as test_runtime_actions.py, with bank stock for refill.
    yield "thread", "crafting", "leather_leather_gloves", 1, {
        "Leather": 27, "Thread": 5}, {"Leather": 27, "Thread": 1}, "Thread", "Leather gloves", 1
    yield "mould", "crafting", "jewellery_gold_ring", 5, {
        "Gold bar": 3, "Ring mould": 1}, {"Gold bar": 1, "Ring mould": 1}, "Gold bar", "Gold ring", 1
    yield "feathers", "fletching", "headless_arrows", 1, {
        "Arrow shafts": 45, "Blue feather": 45, "Feather": 30}, {
        "Arrow shafts": 15, "Blue feather": 15}, "Blue feather", "Headless arrows", 15


def advanced_trip(module, case):
    from ankiscape.runtime import runtime_actions_production

    label, skill, target, level, stock, layout, depleted, product, batch = case
    selector = {"crafting": "current_craft", "fletching": "current_fletch"}[skill]
    player = {"inventory": dict(stock), selector: target, f"{skill}_level": level,
              f"{skill}_exp": 0, "completed_achievements": [],
              "carried_advanced_targets": {target: True}, "carried_layout": {target: layout}}
    events, steps = [], []
    actual = getattr(runtime_actions_production, f"handle_{skill}_answer")

    def handler(ctx):
        events.append(["handler_start", copy.deepcopy(player)])
        result = actual(ctx)
        events.append(["handler_end", copy.deepcopy(player)])
        return result

    for _ in range(2):
        result = module.run_answer_with_carried_overlay(context(player, events), skill, handler)
        steps.append({"result": result, "player": copy.deepcopy(player)})
    assert steps[0]["player"]["carried_primed_targets"][target]
    assert depleted not in steps[0]["player"]["carried_inventory"].get(target, {})
    assert player["inventory"][product] == 2 * batch
    assert player["inventory"][depleted] == stock[depleted] - 2 * batch
    assert player["agility_last_travel"]["charged_reviews"] == 0
    saves = [event[2] for event in events if event[0] == "save_player_data"]
    assert [state["inventory"][depleted] for state in saves] == [
        stock[depleted] - batch, stock[depleted] - 2 * batch]
    return {"steps": steps, "events": events, "player": player}


def compare(baseline, candidate):
    results = []
    for name, config in fixture_cases():
        before, after = run_fixture(baseline, config), run_fixture(candidate, config)
        results.append({"case": name, "equal": before == after, "baseline": before, "candidate": after})
    before, after = real_trip(baseline), real_trip(candidate)
    results.append({"case": "real-firemaking-trip", "equal": before == after,
                    "baseline": before, "candidate": after})
    for case in advanced_cases():
        before, after = advanced_trip(baseline, case), advanced_trip(candidate, case)
        results.append({"case": f"real-advanced-{case[0]}", "equal": before == after,
                        "baseline": before, "candidate": after})
    return results


def forbid_product_imports(marker):
    class StopProductImports:
        def find_spec(self, fullname, path=None, target=None):
            if fullname == "pkg_alias" or fullname.split(".")[0] == "ankiscape":
                marker.write_text(fullname)
                raise AssertionError("product import attempted during guard-only check")
    sys.meta_path.insert(0, StopProductImports())


def check_canaries(args):
    probe = Path(__file__).resolve()
    manifest = json.loads(gzip.decompress(args.manifest.read_bytes()))
    results = []
    with tempfile.TemporaryDirectory(prefix='carried-guard-canary-') as temporary:
        scratch = Path(temporary)
        first = next(iter(manifest['files']))
        changed = scratch / 'changed'
        source = changed / first
        source.parent.mkdir(parents=True)
        source.write_bytes(b'changed source canary\n')
        missing = scratch / 'missing'
        missing.mkdir()
        for label, root, pin, expected in (
            ('invalid-manifest', args.root, '0' * 64, 'manifest SHA256 mismatch'),
            ('changed-source', changed, args.manifest_sha256, f'source mismatch: {first}'),
            ('missing-source', missing, args.manifest_sha256, f'source mismatch: {first}'),
            ('optimized-interpreter', args.root, args.manifest_sha256,
             'optimized interpreter refused; product imports not started'),
        ):
            output = scratch / f'{label}.json'
            command = [sys.executable, str(probe), '--root', str(root),
                       '--manifest', str(args.manifest), '--manifest-sha256', pin,
                       '--output', str(output), '--guard-only']
            if label == 'optimized-interpreter':
                command.insert(1, '-O')
            process = subprocess.run(command, capture_output=True, text=True, check=False)
            passed = (process.returncode != 0 and expected in process.stderr
                      and not output.exists() and not output.with_suffix('.import').exists())
            if label == 'optimized-interpreter':
                passed = passed and process.stderr.strip() == expected
            results.append({'case': label, 'passed': passed,
                            'returncode': process.returncode, 'stderr': process.stderr})
    args.output.write_text(json.dumps(results, indent=2) + '\n')
    if not all(result['passed'] for result in results):
        raise SystemExit('pre-import stop canary failed; runtime remains prohibited')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--guard-only", action="store_true")
    parser.add_argument("--canaries", action="store_true")
    parser.add_argument("--import-marker", type=Path)
    args = parser.parse_args()
    if args.guard_only:
        forbid_product_imports(args.output.with_suffix(".import"))
    if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
        raise SystemExit("optimized interpreter refused; product imports not started")
    if args.canaries:
        check_canaries(args)
        return
    manifest, frozen = verify_sources(args.root, args.manifest, args.manifest_sha256)
    if args.guard_only:
        args.output.write_text(json.dumps({"guards_passed": True, "product_imports": False}) + "\n")
        return
    if args.import_marker:
        args.import_marker.write_text("product imports begin\n")
    baseline, candidate = load_wrappers(args.root, frozen)
    results = compare(baseline, candidate)
    report = {"manifest_sha256": args.manifest_sha256, "baseline_commit": BASELINE,
              "source_files": len(manifest["files"]), "comparisons": results}
    args.output.write_bytes(gzip.compress((json.dumps(report, indent=2) + "\n").encode(), mtime=0))
    if not all(row["equal"] for row in results):
        raise SystemExit("whole-wrapper differential mismatch; inspect retained output")


if __name__ == "__main__":
    main()
