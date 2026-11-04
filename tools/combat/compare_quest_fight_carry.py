"""Paired quest death comparison through the real card dispatcher, on synthetic saves."""

import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import random
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: E402,F401
from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA  # noqa: E402
from ankiscape.core.storage_pure import default_player_data  # noqa: E402
from ankiscape.runtime import runtime_actions_quest  # noqa: E402
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package  # noqa: E402


def quest_chains(walk):
    kills = [row["stage"] for row in walk["trace"]
             if row["action"] == "combat" and row["result"].get("killed")]
    groups = []
    for stage in sorted(set(kills)):
        if groups and groups[-1][-1] + 1 == stage:
            groups[-1].append(stage)
        else:
            groups.append([stage])
    return [(walk["quest_id"], group[0], group[-1]) for group in groups
            if sum(kills.count(stage) for stage in group) >= 2]


def chains(walks):
    return [chain for walk in walks if walk["finished"] for chain in quest_chains(walk)]


def supply_items(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("required_items", "required_inventory", "consumed_inventory", "required_tools"):
                yield from child.items()
            elif isinstance(child, (dict, list, tuple)):
                yield from supply_items(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from supply_items(child)


def player(quest_id, stage, level):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for key in data:
        if key.endswith("_level"):
            data[key] = 99
    for skill in ("attack", "strength", "defense", "constitution"):
        data[f"{skill}_level"] = level
        data[f"{skill}_exp"] = EXP_TABLE[level - 1]
    data["quests"] = {key: dict(started=True, completed=True, progress=quest["stages"])
                      for key, quest in QUEST_DATA.items()}
    data["quests"][quest_id] = dict(started=True, completed=False, progress=stage)
    data["current_quest"] = quest_id
    data["quest_points"] = 1000
    data["inventory"] = {name: max(100, amount * 100) for name, amount in supply_items(QUEST_DATA[quest_id])}
    data["inventory"].update(Coins=10000000, Lobster=1000)
    metal = "Steel" if level < 40 else "Rune"
    data["equipment"] = {"weapon": f"{metal} scimitar", "head": f"{metal} full helm",
                         "body": f"{metal} platebody", "legs": f"{metal} platelegs"}
    data["combat_lifepoints"] = level * 10
    data["combat_prayers_enabled"] = False
    data["combat_auto_eat_food"] = ["Lobster"]
    data["combat_auto_eat_threshold_percent"] = 70
    data["combat_supply_loadout"] = {"food": {"Lobster": 14}}
    data["quest_action_proofs"] = [action for row in QUEST_DATA[quest_id]["stage_requirements"]
                                   if row["stage"] < stage for action in row.get("auto_actions", ())]
    return data


def play(addon, initial, handler, speed, seed, final_stage):
    addon._state.player_data = deepcopy(initial)
    addon._state.current_skill = "Quests"
    addon._review_action_multiplier = lambda: speed
    random.seed(seed)
    quest_id = initial["current_quest"]
    for card in range(1, 1001):
        ctx = addon._runtime_action_context()
        addon._spend_card_on_action(ctx, "quest", handler)
        data = addon._state.player_data
        last = data.get("combat_last_result", {})
        counts = data.get("quest_combat_encounter_counts", {}).get(quest_id, {})
        kills = sum(counts.values())
        if last.get("died") or ctx.card.stop_reason:
            return dict(deaths=int(bool(last.get("died"))), fights=kills + int(not last.get("killed")),
                        kills=kills, cards=card, stop=ctx.card.stop_reason)
        fights = runtime_actions_quest.quest_current_stage_resolvable_combat_blockers_pure(data, quest_id, QUEST_DATA)
        if not fights and data["quests"][quest_id]["progress"] >= final_stage:
            return dict(deaths=0, fights=kills, kills=kills, cards=card, stop="chain_finished")
    raise RuntimeError(f"Quest chain did not finish: {quest_id}, seed {seed}")


def rates(pairs):
    totals = {side: {key: sum(row[side][key] for row in pairs) for key in ("deaths", "fights", "cards")}
              for side in ("off", "on")}
    r_off, r_on = (totals[side]["deaths"] / totals[side]["fights"] for side in ("off", "on"))
    # A seed is reused across the fixed quest/level/speed strata. Pair and
    # cluster by seed so that those correlated runs do not shrink the error.
    residuals = {}
    for row in pairs:
        a, b = row["off"], row["on"]
        seed = row["seed"]
        residuals[seed] = residuals.get(seed, 0) + (
            (b["deaths"] - r_on * b["fights"]) / totals["on"]["fights"]
            - (a["deaths"] - r_off * a["fights"]) / totals["off"]["fights"]
        )
    n = len(residuals)
    se = statistics.stdev(residuals.values()) * n ** 0.5 if n > 1 else 0
    return dict(pairs=len(pairs), seed_clusters=n, off=totals["off"], on=totals["on"], off_rate=r_off, on_rate=r_on,
                difference=r_on - r_off, paired_se=se, passes=r_on - r_off <= 4 * se)


def compare_chain(addon, baseline, quest_id, stage, final_stage, samples):
    pairs = []
    for level in (20, 40, 60):
        initial = player(quest_id, stage, level)
        for speed in (10, 20):
            for seed in range(20261104, 20261104 + samples):
                pair = dict(quest=quest_id, stage=stage, level=level, speed=speed, seed=seed)
                for side, handler in (("off", baseline.handle_quest_answer), ("on", runtime_actions_quest.handle_quest_answer)):
                    pair[side] = play(addon, initial, handler, speed, seed, final_stage)
                pairs.append(pair)
    return pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--walk", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=64)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("ankiscape.runtime.quest_carry_baseline", args.baseline)
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    _install_runtime_fakes()
    addon = _load_addon_as_package("ankiscape_quest_carry_comparison")
    for name in ("save_player_data", "check_achievements", "_refresh_skill_availability", "_show_activity_gain", "_show_exp", "level_up_check"):
        setattr(addon, name, lambda *_args: None)
    addon.show_error_message = lambda title, message: (_ for _ in ()).throw(RuntimeError(f"{title}: {message}"))
    pairs = []
    selected = chains(json.loads(args.walk.read_text()))
    for quest_id, stage, final_stage in selected:
        pairs.extend(compare_chain(addon, baseline, quest_id, stage, final_stage, args.samples))
        args.output.write_text(json.dumps(dict(selected=selected, pairs=pairs), indent=2))
        print(f"{quest_id}:{stage}: {len(pairs)} paired runs", flush=True)
    summary = rates(pairs)
    result = dict(selected=selected, pairs=pairs, summary=summary,
                  per_quest={quest: rates([row for row in pairs if row["quest"] == quest]) for quest in sorted({q for q, _, _ in selected})})
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
