"""Compare frozen and candidate enemy attack maths on the authorised test host.

--preflight verifies the complete listed source inventory without product imports.
"""

import argparse
import base64
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import pickle
import sys


BASELINE_SHA256 = "30377177ba69e1aa112a8d8b384cfd205d6d593133821bdbf74ce85fbcd323f6"
ENGINE_PATH = "logic_pure/logic_pure_combat_engine.py"


def source_hashes(root, inventory):
    with gzip.open(inventory, "rt") as source:
        expected = json.load(source)
    actual = {
        path: hashlib.sha256((root / path).read_bytes()).hexdigest()
        for path in sorted(expected)
    }
    assert actual == expected, "Source inventory differs."
    return actual


def attack_cases():
    from ankiscape.core.constants import EQUIPMENT_DATA
    from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
    from tests.combat.test_enemy_attack_rolls import (
        attack_fixture, draining_fixture, weakening_fixture,
    )
    from tests.test_combat_logic import _player

    for style in ("melee", "ranged", "magic", "magic_melee"):
        yield f"initial:{style}", *attack_fixture(style), (1,), False, (0.999999,)
    for style in ("ranged", "magic_melee"):
        fixture = attack_fixture(
            "ranged", attack_style_by_player_class={"melee": "magic"},
            attack_table=[{"kind": "attack", "style": style, "weight": 1}],
        )
        yield f"override:{style}", *fixture, (5,), True, (0.0, 0.0, 0.75) * 2
    for kind in ("teleport", "unequip"):
        fixture = attack_fixture(
            attack_table=[{"kind": kind, "weight": 1, "player_delay_ticks": 5}]
        )
        yield f"early-exit:{kind}", *fixture, (5,), True, (0.0,)
    for label, style, fields in (
        ("lifepoints", "magic", {"max_hit": 70}),
        ("old-hp", "magic", {"max_hit_old_hp": 7}),
        ("derived-ranged", "ranged", {"strength": 1, "ranged": 99}),
        ("derived-melee", "melee", {"strength": 99, "ranged": 1}),
    ):
        yield f"max-hit:{label}", *attack_fixture(style, **fields), (9,), False, (0.0, 0.75) * 10
    for active in (False, True):
        yield f"weakening:{active}", *weakening_fixture(active), (9,), True, (0.0, 0.5) * 3
    for ticks in (1, 2):
        yield f"defence-drain:{ticks}", *draining_fixture(), (ticks,), True, (0.0, 0.5, 0.0, 0.0) * 2
    player, enemies, equipment = attack_fixture(max_hit=40)
    player.update(
        prayer_level=99, combat_prayer_points=990, combat_prayer_book="curses",
        combat_selected_prayers=["leech_attack", "leech_defence"],
        combat_prayer_uptime="100",
        quests={"the_temple_at_senntisten": {"completed": True}},
    )
    player["combat_encounter"].update(curse_attack_count=7, spell_enemy_attack_factor=0.6)
    for chunks in ((9,), (3, 6)):
        yield f"live-curse-spell:{chunks}", player, enemies, equipment, chunks, True, ()
    player, enemies, equipment = attack_fixture(max_hit=40, attack_speed=1)
    player.update(
        prayer_level=99, combat_prayer_points=1, combat_prayer_drain_counter=31.0,
        combat_selected_prayers=["steel_skin"], combat_prayer_uptime="100",
    )
    for chunks in ((3,), (1, 1, 1)):
        yield f"live-prayer-depletion:{chunks}", player, enemies, equipment, chunks, True, (0.5,) * 10
    dragon = {
        "green_dragon_test": {
            **COMBAT_ENEMY_DATA["green_dragon"],
            "wilderness_risk": {}, "attack_speed": 1,
        }
    }
    player = _player(
        current_combat_target="green_dragon_test", constitution_level=99,
        combat_lifepoints=990, combat_auto_flee=False,
    )
    yield "bypass:dragonfire", player, dragon, EQUIPMENT_DATA, (2,), False, (1.0, 0.0, 0.999999)
    player = _player(
        current_combat_target="skeletal_wyvern", slayer_level=72,
        attack_level=1, strength_level=1, defense_level=99,
        constitution_level=99, combat_lifepoints=990, combat_auto_flee=False,
        equipment={"shield": "Elemental shield"},
        combat_encounter={
            "target_id": "skeletal_wyvern", "enemy_lifepoints": 2000,
            "player_attack_ticks_remaining": 0, "enemy_attack_ticks_remaining": 0,
        },
    )
    yield "bypass:wyvern", player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, (1,), True, (0.999999,) * 3


def capture(function, player, enemies, equipment, chunks, live, prefix):
    from tools.combat.compare_kill_rewards import RecordedRandom

    current = deepcopy(player)
    supplied_enemies, supplied_equipment = deepcopy(enemies), deepcopy(equipment)
    rng = RecordedRandom(prefix)
    steps = []
    for ticks in chunks:
        original = deepcopy(current)
        result = function(
            current, supplied_enemies, supplied_equipment,
            ticks=ticks, live_cadence=live, rng=rng.random,
        )
        assert current == original, "The burst mutated the supplied player."
        assert result[1], result
        steps.append((deepcopy(result), rng.snapshot()))
        current = result[0]
    assert supplied_enemies == enemies, "The burst mutated the supplied enemies."
    assert supplied_equipment == equipment, "The burst mutated the supplied equipment."
    return steps


def compare(baseline_path, output):
    import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
    from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure

    spec = importlib.util.spec_from_file_location(
        "ankiscape.logic_pure._frozen_enemy_attack_engine", baseline_path
    )
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    rows = []
    for label, *case in attack_cases():
        before = capture(baseline.apply_combat_burst_pure, *case)
        after = capture(apply_combat_burst_pure, *case)
        row = {
            "case": label, "equal": before == after,
            "steps": len(after), "rng_calls": len(after[-1][1][2]),
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
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    before = source_hashes(root, args.inventory)
    assert hashlib.sha256(args.baseline.read_bytes()).hexdigest() == BASELINE_SHA256, "Baseline source hash differs."
    assert before[ENGINE_PATH] == args.candidate_sha256, "Candidate source hash differs."
    report = {"baseline_sha256": BASELINE_SHA256, "sources_before": before}
    if args.preflight:
        report.update(status="PREFLIGHT_PASS", product_imported=False)
    else:
        sys.path.insert(0, str(root))
        rows = compare(args.baseline, args.output)
        report.update(cases=rows, status="PASS" if all(row["equal"] for row in rows) else "FAIL")
    report["sources_after"] = source_hashes(root, args.inventory)
    assert report["sources_after"] == before, "Sources changed during comparison."
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] == "FAIL":
        raise SystemExit("Combat enemy attack comparison differed; inspect the retained cases.")


if __name__ == "__main__":
    main()
