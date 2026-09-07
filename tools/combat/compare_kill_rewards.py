"""Compare the frozen combat burst with the candidate on identical reward cases.

Run only on the authorised test host. --preflight hashes source without imports.
"""

import argparse
import base64
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import pickle
import random
import sys


BASELINE_SHA256 = "221d5f5f3ee439e2be1bc06c76cf6a585b52b5eab621a2f86a74addb411c52f7"
ENGINE_PATH = "logic_pure/logic_pure_combat_engine.py"


class RecordedRandom(random.Random):
    def __init__(self, prefix):
        super().__init__(20260905)
        self.prefix = tuple(prefix)
        self.draws = []

    def random(self):
        position = len(self.draws)
        value = self.prefix[position] if position < len(self.prefix) else super().random()
        self.draws.append(value)
        return value

    def snapshot(self):
        return self.getstate(), self.prefix, tuple(self.draws)


def source_hashes(root):
    inventory = root / "memory-bank/evidence/combat-kill-reward-settlement-2026-09-05/preflight.json.gz"
    with gzip.open(inventory, "rt") as source:
        paths = json.load(source)["sources_before"]
    return {
        path: hashlib.sha256((root / path).read_bytes()).hexdigest()
        for path in sorted(paths)
    }


def reward_cases():
    from tests.combat.test_kill_rewards import _reflection_enemy, _reflection_player, _reward_enemy
    from tests.test_combat_logic import _player

    for reflected, live, prayer, held_clue, charms in itertools.product((False, True), repeat=5):
        player = _reflection_player() if reflected else _player()
        enemy = _reflection_enemy() if reflected else _reward_enemy()
        target_id = player["current_combat_target"]
        player["combat_auto_prayer_training"] = prayer
        player["summoning_state"] = {"triple_charm_reviews_remaining": int(charms) * 2}
        player["inventory"] = {"Clue scroll (hard)": 1} if held_clue else {}
        options = {"ticks": 2 if reflected else 50, "live_cadence": live}
        prefix = (0.999999, 0.0, 0.999999) if reflected else (0.5,) * 200
        label = f"reflected={reflected},live={live},prayer={prayer},held_clue={held_clue},charms={charms}"
        yield label, player, {target_id: enemy}, options, prefix


def capture(function, player, enemies, options, prefix, equipment):
    supplied_player = deepcopy(player)
    rng = RecordedRandom(prefix)
    result = function(
        supplied_player, deepcopy(enemies), deepcopy(equipment), rng=rng.random, **options
    )
    assert supplied_player == player, "The burst mutated the supplied player."
    assert result[1] and result[2]["kills"] > 0, result
    return result, rng.snapshot()


def compare(baseline_path, output):
    import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
    from ankiscape.core.constants import EQUIPMENT_DATA
    from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure

    spec = importlib.util.spec_from_file_location(
        "ankiscape.logic_pure._frozen_reward_engine", baseline_path
    )
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    rows = []
    for label, player, enemies, options, prefix in reward_cases():
        before = capture(baseline.apply_combat_burst_pure, player, enemies, options, prefix, EQUIPMENT_DATA)
        after = capture(apply_combat_burst_pure, player, enemies, options, prefix, EQUIPMENT_DATA)
        row = {
            "case": label,
            "equal": before == after,
            "kills": after[0][2]["kills"],
            "rng_calls": len(after[1][2]),
            "baseline_pickle_base64": base64.b64encode(pickle.dumps(before, protocol=4)).decode(),
            "candidate_pickle_base64": base64.b64encode(pickle.dumps(after, protocol=4)).decode(),
        }
        rows.append(row)
        output.write_text(json.dumps({"cases": rows}, indent=2) + "\n")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    before = source_hashes(root)
    assert hashlib.sha256(args.baseline.read_bytes()).hexdigest() == BASELINE_SHA256
    assert before[ENGINE_PATH] == args.candidate_sha256
    report = {"baseline_sha256": BASELINE_SHA256, "sources_before": before}
    if args.preflight:
        report.update(status="PREFLIGHT_PASS", product_imported=False)
    else:
        sys.path.insert(0, str(root))
        rows = compare(args.baseline, args.output)
        report.update(cases=rows, status="PASS" if all(row["equal"] for row in rows) else "FAIL")
    report["sources_after"] = source_hashes(root)
    assert report["sources_after"] == before, "Sources changed during comparison."
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] == "FAIL":
        raise SystemExit("Combat reward comparison differed; inspect the retained cases.")


if __name__ == "__main__":
    main()
