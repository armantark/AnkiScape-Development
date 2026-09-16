"""Compare Keep settlement through the full frozen carried overlay."""

import argparse
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

EVIDENCE = Path("memory-bank/evidence/carried-keep-settlement-2026-09-08")
BASELINE = "1bf2cfe2fa77cea2bb24528c6844d7473b1c2d12"


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


def cases():
    for label, count, gain, result, blessing, drop in (
        ("keep-uncapped", 27, 2, True, False, False),
        ("keep-dry", 1, 0, True, False, False),
        ("keep-rejected", 1, 2, False, False, False),
        ("keep-none-result", 1, 2, None, False, False),
        ("blessing-full", 28, 2, True, True, False),
        ("blessing-partial", 27, 2, True, True, False),
        ("drop", 1, 2, True, False, True),
    ):
        player = {"inventory": {"Logs": 100}, "current_tree": "tree",
                  "woodcutting_level": 99, "agility_level": 1,
                  "carried_inventory": {"tree": {"Logs": count}},
                  "carried_churn": {"tree": count}, "skilling_bank_run": {},
                  "carried_keep_drop": {"tree": "drop"} if drop else {},
                  "evil_tree": {"blessing_reviews_remaining": 2 if blessing else 0}}
        yield label, player, gain, result


def capture(module, supplied, gain, result):
    from tools.carried.compare_new_bank_trip import recorded_context
    from tools.combat.compare_kill_rewards import RecordedRandom

    player, events = copy.deepcopy(supplied), []
    rng = RecordedRandom((0.0,))
    ctx = recorded_context(player, events, rng)

    def handler(action_ctx):
        events.append(["handler_start", copy.deepcopy(player)])
        action_ctx.random_random()
        player["inventory"]["Logs"] += gain
        action_ctx.check_achievements(player)
        action_ctx.refresh_skill_availability()
        action_ctx.save_player_data()
        events.append(["handler_end", result, copy.deepcopy(player)])
        return result

    with patch.object(module, "_admit_live_cadence", side_effect=lambda ctx, *_: (ctx, True)):
        returned = module.run_answer_with_carried_overlay(ctx, "woodcutting", handler)
    return {"result": returned, "player": player, "events": events,
            "rng": rng.snapshot(), "player_identity_preserved": ctx.player_data is player}


def capture_urn(module, drop):
    from tests.test_urns import UrnRuntimeOverlayTest, _context, handle_mining_answer
    from tools.carried.compare_processing_reconciliation import trace_callback
    import dataclasses

    player = UrnRuntimeOverlayTest._mining_player(drop=drop)
    events = []
    ctx = _context(player, (0.0, 0.0, 1.0, 0.0))
    for field in dataclasses.fields(ctx):
        callback = getattr(ctx, field.name)
        if callable(callback):
            setattr(ctx, field.name, trace_callback(field.name, callback, player, events))
    returned = module.run_answer_with_carried_overlay(ctx, "mining", handle_mining_answer)
    return {"result": returned, "player": player, "events": events,
            "player_identity_preserved": ctx.player_data is player}


def compare(root, frozen, output):
    from tools.carried.compare_processing_reconciliation import load_wrappers
    from tools.carried.compare_new_bank_trip import retain_case

    baseline, candidate = load_wrappers(root, frozen)
    rows = []
    for label, player, gain, result in cases():
        before = capture(baseline, player, gain, result)
        after = capture(candidate, player, gain, result)
        observed = {"result": after["result"],
                    "handler_calls": sum(event[0] == "handler_start" for event in after["events"]),
                    "identity": after["player_identity_preserved"],
                    "overflow_gain": sum(event[0] == "show_activity_gain" for event in after["events"])}
        expected = {"result": result, "handler_calls": 1, "identity": True,
                    "overflow_gain": int(label in {"blessing-full", "blessing-partial"})}
        if label == "drop":
            observed.update(bank_logs=after["player"]["inventory"].get("Logs"),
                            carried_logs=after["player"]["carried_inventory"]["tree"].get("Logs"),
                            churn=after["player"]["carried_churn"].get("tree"))
            expected.update(bank_logs=100, carried_logs=1, churn=1)
        retain_case(output, rows, label, before, after, observed == expected, expected, observed)
    for drop in (False, True):
        before, after = capture_urn(baseline, drop), capture_urn(candidate, drop)
        observed = {"result": after["result"],
                    "urn": after["player"]["inventory"].get("Cracked mining urn"),
                    "ore": after["player"]["inventory"].get("Copper ore", 0)}
        expected = {"result": True, "urn": 1, "ore": 0 if drop else 1}
        retain_case(output, rows, f"urn-drop-{drop}", before, after,
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
