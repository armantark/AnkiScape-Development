from __future__ import annotations

import copy
import json
import random
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    EQUIPMENT_DATA,
    EXTRA_ITEM_DATA,
    EXTRA_ITEM_IMAGES,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.item_registry import item_definitions_by_storage_key
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.item_values import ITEM_VALUES
from ankiscape.data.mobilising_armies_data import (
    MOBILISING_ARMIES_ACTIVITY_ID,
    MOBILISING_ARMIES_ASSET_MANIFEST,
    MOBILISING_ARMIES_END_ELIMINATION_PCT,
    MOBILISING_ARMIES_END_LOSS_PCT,
    MOBILISING_ARMIES_END_PRIMARY_PCT,
    MOBILISING_ARMIES_FLOOR_IDS,
    MOBILISING_ARMIES_FLOORS,
    MOBILISING_ARMIES_FORMATION_RANKS,
    MOBILISING_ARMIES_IMBUE_RINGS,
    MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP,
    MOBILISING_ARMIES_LOCATORS,
    MOBILISING_ARMIES_PREFIXES,
    MOBILISING_ARMIES_QUEST_KITS,
    MOBILISING_ARMIES_RANK_ACTION_MINIMUM,
    MOBILISING_ARMIES_RANK_HOURLY_CAP,
    MOBILISING_ARMIES_RESCUE_STEAL_PER_ORDER,
    MOBILISING_ARMIES_SCENARIO_BEATS,
    MOBILISING_ARMIES_SCENARIOS,
    MOBILISING_ARMIES_SCENARIOS_BY_ID,
    MOBILISING_ARMIES_SPECIAL_UNIT_CAP,
    MOBILISING_ARMIES_SPECIAL_UNIT_IDS,
    MOBILISING_ARMIES_SPOILS,
    MOBILISING_ARMIES_SQUAD_CONTRACT_CAP,
    MOBILISING_ARMIES_SQUAD_CREDIT_COST,
    MOBILISING_ARMIES_SQUAD_IDS,
    MOBILISING_ARMIES_SQUADS,
    MOBILISING_ARMIES_SQUADS_REQUIRED,
    MOBILISING_ARMIES_UNIFORMS,
    mobilising_armies_investment_credits_pure,
    mobilising_armies_rank_band_pure,
    mobilising_armies_reward_credits_pure,
)
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.logic.mobilising_armies_logic import (
    _REWARD_COSTS,
    apply_mobilising_armies_command_pure,
    apply_mobilising_armies_review_pure,
    default_mobilising_armies_state_pure,
    mobilising_armies_view_pure,
    sanitize_mobilising_armies_state_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


ROOT = Path(__file__).resolve().parents[1]
# 5,000 Adamant bars is 645,000 credits' worth, which is more than the wallet
# cap, so every test starts able to fill the wallet and stake the maximum.
_STAKE_ITEM = "Adamant bar"
_STAKE_QUANTITY = 5_000


def _command(data, action_id, payload=None, *, rng=None):
    updated, ok, info = apply_mobilising_armies_command_pure(
        data,
        action_id,
        payload or {},
        rng if rng is not None else (lambda: 0.5),
        item_values=ITEM_VALUES,
    )
    if not ok:
        raise AssertionError(f"{action_id}: {info}")
    return updated, info


def _player(*, rank=0, played=(), reward_credits=0):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["inventory"] = {_STAKE_ITEM: _STAKE_QUANTITY}
    data["mobilising_armies_rank"] = rank
    data["mobilising_armies_scenarios_played"] = list(played)
    data["mobilising_armies_reward_credits"] = reward_credits
    return data


def _mustered(*, squad="light_elf", rank=0, played=(), specials=(), **policy):
    data = _player(rank=rank, played=played)
    data, _info = _command(
        data, "invest", {"item_name": _STAKE_ITEM, "quantity": _STAKE_QUANTITY}
    )
    data, _info = _command(
        data, "recruit", {"squad": squad, "quantity": MOBILISING_ARMIES_SQUADS_REQUIRED}
    )
    for unit in specials:
        data, _info = _command(data, "buy_special_unit", {"unit": unit, "quantity": 1})
    band = mobilising_armies_rank_band_pure(rank)
    payload = {"investment": band.maximum_investment, **policy}
    data, _info = _command(data, "set_policy", payload)
    return data


def _entered(*, seed=0, **kwargs):
    data = _mustered(**kwargs)
    rng = random.Random(seed).random
    data, info = _command(data, "enter", rng=rng)
    return data, rng, info


def _play(data, rng, *, productive=True, beats=None):
    """Run the scenario to its terminal beat and return (data, last result)."""
    limit = beats if beats is not None else MOBILISING_ARMIES_SCENARIO_BEATS + 2
    result = {}
    for _index in range(limit):
        data, ok, result = apply_mobilising_armies_review_pure(
            data, rng, productive=productive
        )
        if not ok:
            raise AssertionError(result)
        if result.get("terminal"):
            return data, result
    return data, result


class MobilisingArmiesSourceAndAssetTests(unittest.TestCase):
    def test_investment_formula_reproduces_seven_period_credit_figures(self):
        # Mobilising Armies/Investments oldid=6538687 lists the credits each item
        # earns. The article separately states the rule as ((low alch)/2)+1. If
        # our low-alchemy derivation is right, the rule must reproduce the table.
        for item_name, credits in (
            ("Adamant bar", 129),
            ("Adamant bolts", 12),
            ("Adamant javelin", 50),
            ("Agility potion (4)", 41),
            ("Air rune", 4),
            ("Amulet of fury", 40_401),
            ("Amulet of glory", 3_526),
        ):
            with self.subTest(item_name):
                self.assertEqual(
                    mobilising_armies_investment_credits_pure(ITEM_VALUES[item_name]),
                    credits,
                )

    def test_reward_credit_formula_matches_the_period_expression(self):
        # 100 + max[0, timeBonus + killCountBonus + investment * rankModifier *
        # endConditionModifier / 10000], kill bonus = kills * 70.
        self.assertEqual(
            mobilising_armies_reward_credits_pure(
                beats_survived=3,
                kills=10,
                investment=20_000,
                rank_modifier_pct=150,
                end_condition_pct=150,
            ),
            100 + (3 - 2) * 40 + 700 + 20_000 * 150 * 150 // 10_000,
        )
        # The max[0, ...] clamp is real: a fast death cannot drive the payout
        # below the flat hundred.
        self.assertEqual(
            mobilising_armies_reward_credits_pure(
                beats_survived=0,
                kills=0,
                investment=0,
                rank_modifier_pct=110,
                end_condition_pct=100,
            ),
            100,
        )

    def test_rank_bands_and_formation_gates_are_the_period_tables(self):
        for rank, prefix, investment, modifier in (
            (0, "Junior Cadet", 10_000, 110),
            (99, "Junior Cadet", 10_000, 110),
            (100, "Sergeant", 12_500, 120),
            (200, "Commander", 15_000, 130),
            (300, "War-Chief", 17_500, 140),
            (400, "", 20_000, 150),
            (9_999, "", 20_000, 150),
        ):
            band = mobilising_armies_rank_band_pure(rank)
            self.assertEqual(
                (band.prefix, band.maximum_investment, band.reward_modifier_pct),
                (prefix, investment, modifier),
            )
        self.assertEqual(
            MOBILISING_ARMIES_FORMATION_RANKS,
            {
                "wedge": 0,
                "wall": 0,
                "flank": 0,
                "eager": 51,
                "spread": 101,
                "lefty": 201,
                "righty": 201,
                "block": 301,
                "grid": 401,
            },
        )

    def test_squad_roster_and_scenario_chain_are_the_period_tables(self):
        self.assertEqual(
            {
                (squad.race, squad.squad_class): (
                    squad.combat_level,
                    squad.lifepoints,
                    squad.discipline,
                )
                for squad in MOBILISING_ARMIES_SQUADS
            },
            {
                ("elf", "light"): (225, 4_800, 60),
                ("elf", "heavy"): (350, 9_600, 110),
                ("dwarf", "light"): (175, 5_300, 60),
                ("dwarf", "heavy"): (350, 10_100, 60),
                ("goblin", "light"): (175, 4_800, 110),
                ("goblin", "heavy"): (400, 9_600, 60),
            },
        )
        self.assertEqual(
            [(row.id, row.unlocked_by, row.objective_target) for row in MOBILISING_ARMIES_SCENARIOS],
            [
                ("conflict", "", 10),
                ("siege", "conflict", 100),
                ("hoard", "siege", 100_000),
                ("rescue", "hoard", 28),
            ],
        )

    def test_every_registry_row_and_asset_exists_with_pre_cutoff_provenance(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        owned = (
            [kit.item_name for kit in MOBILISING_ARMIES_QUEST_KITS]
            + [locator.item_name for locator in MOBILISING_ARMIES_LOCATORS]
            + [piece.item_name for piece in MOBILISING_ARMIES_UNIFORMS]
            + [ring.item_name for ring in MOBILISING_ARMIES_IMBUE_RINGS]
        )
        for item_name in owned:
            with self.subTest(item_name):
                self.assertIn(item_name, by_storage_key)
                self.assertIn(item_name, EXTRA_ITEM_IMAGES)
                self.assertTrue(Path(EXTRA_ITEM_IMAGES[item_name]).exists())
        # Uniform pieces and imbued rings must be real equipment, and every base
        # ring the shop consumes must already be a registry item.
        for piece in MOBILISING_ARMIES_UNIFORMS:
            self.assertEqual(EQUIPMENT_DATA[piece.item_name].slot, piece.slot)
        for ring in MOBILISING_ARMIES_IMBUE_RINGS:
            self.assertIn(ring.base_item, by_storage_key)
            self.assertEqual(EQUIPMENT_DATA[ring.item_name].slot, "ring")
        # Exact game-main bonus blocks, spot-checked at both ends of the ladder.
        self.assertEqual(EQUIPMENT_DATA["Gold ring (i)"].bonuses.defence_stab, 1)
        self.assertEqual(EQUIPMENT_DATA["Onyx ring (i)"].bonuses.attack_crush, 6)
        self.assertEqual(EQUIPMENT_DATA["Serjeant top"].bonuses.attack_crush, 0)
        # Every spoils row must be a real item the player can then use.
        for floor_id, rows in MOBILISING_ARMIES_SPOILS.items():
            for item_name, quantity in rows:
                with self.subTest(floor=floor_id, item=item_name):
                    self.assertIn(item_name, by_storage_key)
                    self.assertGreater(quantity, 0)
        # Every quest-kit content row must be a real item too.
        for kit in MOBILISING_ARMIES_QUEST_KITS:
            for content in kit.contents:
                self.assertIn(content, by_storage_key, kit.item_name)

        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        for row in MOBILISING_ARMIES_ASSET_MANIFEST:
            output_path = str(row["output_path"])
            with self.subTest(output_path):
                self.assertTrue((ROOT / output_path).exists())
                self.assertIn(output_path, provenance)
                self.assertLess(
                    str(provenance[output_path]["timestamp"]), "2012-11-20T00:00:00Z"
                )

    def test_the_teleport_spell_is_castable_rather_than_locked_behind_a_phantom_quest(self):
        from ankiscape.core.constants import MAGIC_DATA, QUEST_DATA

        spell = MAGIC_DATA["mobilising_armies_teleport"]
        # Neither SpellbookData.kt nor the pinned article gives this spell a
        # quest requirement, and the id it used to name is not a quest at all,
        # so the gate made the spell permanently uncastable.
        self.assertIsNone(spell["quest_gate"])
        self.assertNotIn("mobilising_armies", QUEST_DATA)
        self.assertEqual(spell["level"], 10)
        self.assertEqual(
            spell["rune_cost"], {"Air rune": 1, "Water rune": 1, "Law rune": 1}
        )

    def test_activity_registers_with_a_disclosed_cadence_row(self):
        self.assertIn(MOBILISING_ARMIES_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        spec = UTILITY_ACTIVITY_DATA[MOBILISING_ARMIES_ACTIVITY_ID]
        self.assertEqual(spec["group"], "minigames")
        self.assertIn("oldid=6514352", spec["source"])
        self.assertTrue(Path(spec["icon_path"]).exists())
        rows = [
            row
            for row in cadence_coverage_rows_pure()
            if row["action_id"] == MOBILISING_ARMIES_ACTIVITY_ID
        ]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_status"], "sourced_with_disclosed_translation")


class MobilisingArmiesGateTests(unittest.TestCase):
    def test_entry_needs_ten_squads_and_names_the_shortfall(self):
        data = _player()
        view = mobilising_armies_view_pure(data)
        self.assertFalse(view["can_enter"])
        self.assertIn("Recruit 10 more mercenary squads.", view["entry_reasons"])
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "enter", {}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("Recruit 10", info["reason"])

    def test_squad_contracts_are_capped_at_ten_and_cost_a_hundred_each(self):
        data = _player()
        data, _info = _command(
            data, "invest", {"item_name": _STAKE_ITEM, "quantity": _STAKE_QUANTITY}
        )
        before = data["mobilising_armies_investment_credits"]
        data, info = _command(data, "recruit", {"squad": "heavy_dwarf", "quantity": 25})
        self.assertEqual(info["quantity"], MOBILISING_ARMIES_SQUAD_CONTRACT_CAP)
        self.assertEqual(
            before - data["mobilising_armies_investment_credits"],
            MOBILISING_ARMIES_SQUAD_CONTRACT_CAP * MOBILISING_ARMIES_SQUAD_CREDIT_COST,
        )
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "recruit", {"squad": "light_elf", "quantity": 1}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("already hold 10", info["reason"])

    def test_special_units_are_capped_at_five(self):
        data = _player()
        data, _info = _command(
            data, "invest", {"item_name": _STAKE_ITEM, "quantity": _STAKE_QUANTITY}
        )
        for unit in MOBILISING_ARMIES_SPECIAL_UNIT_IDS:
            data, _info = _command(data, "buy_special_unit", {"unit": unit, "quantity": 1})
        self.assertEqual(
            sum(data["mobilising_armies_special_units"].values()),
            MOBILISING_ARMIES_SPECIAL_UNIT_CAP,
        )
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "buy_special_unit", {"unit": "glider", "quantity": 1}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("already hold 5", info["reason"])

    def test_investment_wallet_caps_at_five_hundred_thousand(self):
        data = _player()
        data["inventory"] = {"Amulet of fury": 100}
        data, _info = _command(
            data, "invest", {"item_name": "Amulet of fury", "quantity": 100}
        )
        self.assertEqual(
            data["mobilising_armies_investment_credits"],
            MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP,
        )
        # Only the items the wallet could pay for were taken.
        self.assertGreater(data["inventory"]["Amulet of fury"], 0)
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data,
            "invest",
            {"item_name": "Amulet of fury", "quantity": 1},
            lambda: 0.5,
            item_values=ITEM_VALUES,
        )
        self.assertFalse(ok)
        self.assertIn("wallet is full", info["reason"])

    def test_junior_cadet_mal_refuses_a_worthless_item(self):
        data = _player()
        data["inventory"]["Bones"] = 10
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "invest", {"item_name": "Bones", "quantity": 1}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("will not take Bones", info["reason"])

    def test_scenario_chain_and_formations_unlock_only_as_the_source_says(self):
        data = _player()
        for scenario_id, needs in (
            ("siege", "Conflict"),
            ("hoard", "Siege"),
            ("rescue", "Hoard"),
        ):
            _updated, ok, info = apply_mobilising_armies_command_pure(
                data, "set_policy", {"scenario": scenario_id}, lambda: 0.5
            )
            self.assertFalse(ok, scenario_id)
            self.assertIn(needs, info["reason"])
        data["mobilising_armies_scenarios_played"] = ["conflict"]
        data, _info = _command(data, "set_policy", {"scenario": "siege"})
        self.assertEqual(data["mobilising_armies_policy"]["scenario"], "siege")

        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "set_policy", {"formation": "grid"}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("rank 401", info["reason"])
        data["mobilising_armies_rank"] = 401
        data, _info = _command(data, "set_policy", {"formation": "grid"})
        self.assertEqual(data["mobilising_armies_policy"]["formation"], "grid")
        view = mobilising_armies_view_pure(data)
        self.assertTrue(
            all(row["unlocked"] for row in view["formation_options"])
        )

    def test_the_rank_band_caps_the_stake(self):
        data = _player()
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "set_policy", {"investment": 12_500}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("10,000", info["reason"])
        data["mobilising_armies_rank"] = 100
        data, _info = _command(data, "set_policy", {"investment": 12_500})
        self.assertEqual(data["mobilising_armies_policy"]["investment"], 12_500)


class MobilisingArmiesScenarioTests(unittest.TestCase):
    def test_entering_stakes_the_credits_and_claims_the_activity_session(self):
        mustered = _mustered()
        before = mustered["mobilising_armies_investment_credits"]
        data, _rng, info = _entered()
        self.assertEqual(
            data["mobilising_armies_investment_credits"], before - 10_000
        )
        self.assertEqual(
            data["activity_session"], {"active_id": MOBILISING_ARMIES_ACTIVITY_ID}
        )
        session = data["mobilising_armies"]
        self.assertEqual(len(session["squads"]), MOBILISING_ARMIES_SQUADS_REQUIRED)
        self.assertEqual(len(session["rivals"]), MOBILISING_ARMIES_SQUADS_REQUIRED)
        # Contracts moved into the battle, so the tent is empty until squads
        # come home.
        self.assertEqual(data["mobilising_armies_squads"], {})
        self.assertIn("orders remain", info["message"])

    def test_a_review_outside_a_scenario_is_refused(self):
        data = _mustered()
        _updated, ok, info = apply_mobilising_armies_review_pure(
            data, lambda: 0.5, productive=True
        )
        self.assertFalse(ok)
        self.assertIn("Enter a Mobilising Armies scenario", info["reason"])

    def test_every_scenario_reaches_its_own_primary_objective_win(self):
        wins = {}
        for scenario_id, played in (
            ("conflict", ()),
            ("siege", ("conflict",)),
            ("hoard", ("conflict", "siege")),
            ("rescue", ("conflict", "siege", "hoard")),
        ):
            for squad in MOBILISING_ARMIES_SQUAD_IDS:
                for seed in range(6):
                    data, rng, _info = _entered(
                        seed=seed,
                        squad=squad,
                        played=played,
                        scenario=scenario_id,
                        order="objective",
                    )
                    data, result = _play(data, rng)
                    if result["outcome"] == "win":
                        wins[scenario_id] = result
                        break
                if scenario_id in wins:
                    break
        self.assertEqual(sorted(wins), ["conflict", "hoard", "rescue", "siege"])
        for scenario_id, result in wins.items():
            with self.subTest(scenario_id):
                self.assertEqual(
                    result["end_condition_pct"], MOBILISING_ARMIES_END_PRIMARY_PCT
                )
                self.assertGreater(result["reward_credits"], 0)

    def test_eliminating_the_rivals_in_a_non_conflict_scenario_pays_the_kill_modifier(self):
        # Siege states the two modifiers explicitly: 150% for the wall, 120% for
        # killing everyone. Goblins beat elves, so an all-goblin army can clear
        # the field before the catapult is ready.
        for seed in range(12):
            data, rng, _info = _entered(
                seed=seed, squad="heavy_goblin", played=("conflict",),
                scenario="siege", order="attack",
            )
            if data["mobilising_armies"]["rivals"][0]["id"] not in {
                "light_elf",
                "heavy_elf",
            }:
                continue
            data, result = _play(data, rng)
            if result["outcome"] == "win":
                self.assertEqual(
                    result["end_condition_pct"], MOBILISING_ARMIES_END_ELIMINATION_PCT
                )
                self.assertEqual(data["mobilising_armies"], {})
                return
        self.skipTest("no elf rival drawn in twelve seeds")

    def test_losing_every_squad_ends_the_scenario_at_the_loss_modifier(self):
        for seed in range(12):
            data, rng, _info = _entered(
                seed=seed, squad="light_elf", scenario="conflict", order="explore"
            )
            data, result = _play(data, rng)
            if result["outcome"] == "loss":
                self.assertEqual(
                    result["end_condition_pct"], MOBILISING_ARMIES_END_LOSS_PCT
                )
                self.assertEqual(data["activity_session"], {"active_id": ""})
                return
        self.skipTest("no loss in twelve seeds")

    def test_an_idle_army_never_earns_rank_however_the_scenario_ends(self):
        outcomes = set()
        for squad in MOBILISING_ARMIES_SQUAD_IDS:
            for seed in range(3):
                data, rng, _info = _entered(seed=seed, squad=squad, scenario="conflict")
                data, result = _play(data, rng, productive=False)
                outcomes.add(result["outcome"])
                # Again spends the beat without issuing an order, so the sourced
                # ten-order rank threshold is never met.
                self.assertFalse(result["rank_eligible"])
                self.assertEqual(result["rank_gained"], 0)
                self.assertEqual(data["mobilising_armies_rank"], 0)
                self.assertEqual(int(data["mobilising_armies_games_played"]), 1)
        # Standing still either runs the clock out or gets the army wiped; both
        # are reachable and neither pays rank.
        self.assertTrue(outcomes <= {"timeout", "loss"})
        self.assertEqual(outcomes, {"timeout", "loss"})

    def test_explore_orders_do_not_count_toward_rank(self):
        data = _mustered(
            squad="heavy_dwarf", scenario="conflict", order="explore"
        )
        rng = lambda: 0.0
        data, _info = _command(data, "enter", rng=rng)
        results = []
        for beat in range(MOBILISING_ARMIES_SCENARIO_BEATS):
            if beat == 7:
                data = migrate_loaded_data(
                    json.loads(json.dumps(data)), ORE_DATA, ITEM_DEFINITIONS
                )
            data, ok, result = apply_mobilising_armies_review_pure(
                data, rng, productive=True
            )
            self.assertTrue(ok, result)
            self.assertEqual(result["order"], "explore")
            results.append(result)
            if result.get("terminal"):
                break

        self.assertEqual(len(results), MOBILISING_ARMIES_SCENARIO_BEATS)
        self.assertEqual(results[-1]["outcome"], "timeout")
        self.assertFalse(results[-1]["rank_eligible"])
        self.assertEqual(results[-1]["rank_gained"], 0)
        self.assertEqual(data["mobilising_armies_rank"], 0)

    def test_a_scenario_that_runs_its_clock_out_pays_the_participation_rank(self):
        for squad in MOBILISING_ARMIES_SQUAD_IDS:
            for seed in range(6):
                data, rng, _info = _entered(
                    seed=seed, squad=squad, scenario="conflict", order="attack"
                )
                data, result = _play(data, rng)
                if result["outcome"] == "timeout":
                    # Exact: "In the event that time runs out, all players
                    # receive +1 rank."
                    self.assertEqual(result["rank_gained"], 1)
                    self.assertTrue(result["rank_eligible"])
                    self.assertEqual(data["mobilising_armies_rank"], 1)
                    self.assertEqual(
                        data["mobilising_armies_scenarios_played"], ["conflict"]
                    )
                    return
        self.fail("no timeout reachable, so the timeout rank rule is untested")

    def test_ten_orders_are_required_before_any_rank_is_paid(self):
        data, rng, _info = _entered(scenario="hoard", played=("conflict", "siege"), order="objective")
        for _index in range(MOBILISING_ARMIES_RANK_ACTION_MINIMUM - 1):
            data, ok, result = apply_mobilising_armies_review_pure(
                data, rng, productive=True
            )
            self.assertTrue(ok, result)
            self.assertFalse(result.get("terminal"), result)
        self.assertFalse(mobilising_armies_view_pure(data)["rank_eligible"])
        data, ok, result = apply_mobilising_armies_review_pure(data, rng, productive=True)
        self.assertTrue(ok, result)
        if not result.get("terminal"):
            self.assertTrue(mobilising_armies_view_pure(data)["rank_eligible"])

    def test_forfeiting_pays_neither_rank_nor_credits_and_does_not_unlock_the_next_scenario(self):
        data, rng, _info = _entered(scenario="conflict", order="attack")
        for _index in range(MOBILISING_ARMIES_SCENARIO_BEATS - 2):
            data, ok, result = apply_mobilising_armies_review_pure(
                data, rng, productive=True
            )
            self.assertTrue(ok, result)
            if result.get("terminal"):
                self.skipTest("scenario ended before the forfeit could be tested")
        data, info = _command(data, "forfeit")
        self.assertEqual(info["outcome"], "forfeit")
        self.assertEqual(info["rank_gained"], 0)
        self.assertEqual(info["reward_credits"], 0)
        self.assertEqual(data["mobilising_armies_reward_credits"], 0)
        self.assertEqual(data["mobilising_armies_scenarios_played"], [])
        self.assertEqual(data["activity_session"], {"active_id": ""})

    def test_the_hourly_rank_cap_stops_further_rank_but_not_credits(self):
        data, rng, _info = _entered(scenario="conflict", order="attack")
        data["mobilising_armies_rank_window"] = {
            "beats": 1,
            "points": MOBILISING_ARMIES_RANK_HOURLY_CAP,
        }
        data, result = _play(data, rng)
        self.assertEqual(result["rank_gained"], 0)
        self.assertEqual(data["mobilising_armies_rank"], 0)
        self.assertGreater(result["reward_credits"], 0)
        self.assertEqual(
            mobilising_armies_view_pure(data)["rank_points_left_this_window"], 0
        )

    def test_surviving_squads_come_home_and_the_dead_must_be_re_recruited(self):
        seen_losses = False
        for squad in MOBILISING_ARMIES_SQUAD_IDS:
            for seed in range(3):
                data, rng, _info = _entered(
                    seed=seed, squad=squad, scenario="conflict", order="attack"
                )
                for _index in range(MOBILISING_ARMIES_SCENARIO_BEATS + 2):
                    session_before = copy.deepcopy(data["mobilising_armies"])
                    data, ok, result = apply_mobilising_armies_review_pure(
                        data, rng, productive=True
                    )
                    self.assertTrue(ok, result)
                    if result.get("terminal"):
                        break
                alive = sum(
                    1
                    for row in session_before["squads"]
                    if int(row["lifepoints"]) > 0
                )
                returned = sum(data["mobilising_armies_squads"].values())
                # Survivors are back on contract; the fallen are gone, and the
                # count only ever goes down, never up.
                self.assertLessEqual(returned, alive)
                self.assertLessEqual(returned, MOBILISING_ARMIES_SQUADS_REQUIRED)
                if returned < MOBILISING_ARMIES_SQUADS_REQUIRED:
                    seen_losses = True
                    view = mobilising_armies_view_pure(data)
                    self.assertFalse(view["can_enter"])
                    self.assertTrue(
                        any("Recruit" in reason for reason in view["entry_reasons"])
                    )
        self.assertTrue(seen_losses, "no scenario ever cost a squad")

    def test_exploring_yields_only_the_acting_race_treasure(self):
        by_race = {}
        for squad_id in MOBILISING_ARMIES_SQUAD_IDS:
            race = next(s.race for s in MOBILISING_ARMIES_SQUADS if s.id == squad_id)
            for seed in range(8):
                data, rng, _info = _entered(
                    seed=seed, squad=squad_id, scenario="conflict", order="explore"
                )
                before = dict(data["inventory"])
                data, ok, result = apply_mobilising_armies_review_pure(
                    data, rng, productive=True
                )
                self.assertTrue(ok, result)
                if result.get("loot"):
                    by_race.setdefault(race, set()).add(str(result["loot"]))
                    gained = data["inventory"][str(result["loot"])] - before.get(
                        str(result["loot"]), 0
                    )
                    self.assertEqual(gained, 1)
        from ankiscape.data.mobilising_armies_data import MOBILISING_ARMIES_EXPLORE_LOOT

        self.assertEqual(sorted(by_race), ["dwarf", "elf", "goblin"])
        for race, found in by_race.items():
            self.assertTrue(found <= set(MOBILISING_ARMIES_EXPLORE_LOOT[race]), race)

    def test_every_special_unit_resolves_its_own_sourced_effect(self):
        data, rng, _info = _entered(
            specials=MOBILISING_ARMIES_SPECIAL_UNIT_IDS,
            scenario="conflict",
            order="attack",
        )
        self.assertEqual(
            sum(data["mobilising_armies"]["special_units"].values()),
            MOBILISING_ARMIES_SPECIAL_UNIT_CAP,
        )
        seen = {}
        for unit in MOBILISING_ARMIES_SPECIAL_UNIT_IDS:
            rival_before = sum(
                int(row["lifepoints"]) for row in data["mobilising_armies"]["rivals"]
            )
            own_before = sum(
                int(row["lifepoints"]) for row in data["mobilising_armies"]["squads"]
            )
            data, info = _command(data, "deploy", {"unit": unit}, rng=rng)
            session = data["mobilising_armies"]
            rival_after = sum(int(row["lifepoints"]) for row in session["rivals"])
            own_after = sum(int(row["lifepoints"]) for row in session["squads"])
            seen[unit] = info
            if unit in {"chompa", "cannon"}:
                self.assertLess(rival_after, rival_before, unit)
                self.assertLess(own_after, own_before, unit)  # friendly fire is real
            elif unit == "glider":
                self.assertLess(rival_after, rival_before)
                self.assertEqual(own_after, own_before)  # the Glider spares your own
            elif unit == "distractor":
                self.assertGreater(int(session["stalled"]), 0)
            else:
                self.assertGreater(int(session["shielded"]), 0)
        self.assertEqual(sorted(seen), sorted(MOBILISING_ARMIES_SPECIAL_UNIT_IDS))
        self.assertEqual(data["mobilising_armies"]["special_units"], {})
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "deploy", {"unit": "glider"}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("brought no", info["reason"])

    def test_a_distractor_stalls_the_next_order_for_both_sides(self):
        data, rng, _info = _entered(
            specials=("distractor",), scenario="conflict", order="attack"
        )
        data, _info = _command(data, "deploy", {"unit": "distractor"}, rng=rng)
        commands_before = int(data["mobilising_armies"]["commands"])
        data, ok, result = apply_mobilising_armies_review_pure(data, rng, productive=True)
        self.assertTrue(ok, result)
        self.assertEqual(result["order"], "stalled")
        self.assertEqual(int(data["mobilising_armies"]["commands"]), commands_before)

    def test_a_barricade_blocks_the_rival_beat_entirely(self):
        data, rng, _info = _entered(
            specials=("barricade",), scenario="hoard", played=("conflict", "siege"),
            order="objective",
        )
        data, _info = _command(data, "deploy", {"unit": "barricade"}, rng=rng)
        rival_before = int(data["mobilising_armies"]["opponent_objective"])
        data, ok, result = apply_mobilising_armies_review_pure(data, rng, productive=True)
        self.assertTrue(ok, result)
        self.assertEqual(result["opponent"], "blocked")
        self.assertEqual(
            int(data["mobilising_armies"]["opponent_objective"]), rival_before
        )

    def test_the_siege_catapult_and_the_direct_assault_are_both_real_routes(self):
        catapult, _rng, _info = _entered(
            played=("conflict",), scenario="siege", order="objective",
            siege_route="catapult",
        )
        rng = random.Random(0).random
        parts_seen = []
        for _index in range(5):
            catapult, ok, result = apply_mobilising_armies_review_pure(
                catapult, rng, productive=True
            )
            self.assertTrue(ok, result)
            parts_seen.append(result.get("progress"))
        self.assertEqual(parts_seen.count("catapult_part"), 4)
        self.assertIn("catapult_rock", parts_seen)
        self.assertEqual(int(catapult["mobilising_armies"]["objective"]), 0)

        assault, rng, _info = _entered(
            played=("conflict",), scenario="siege", order="objective",
            siege_route="assault",
        )
        own_before = sum(
            int(row["lifepoints"]) for row in assault["mobilising_armies"]["squads"]
        )
        assault, ok, result = apply_mobilising_armies_review_pure(
            assault, rng, productive=True
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["progress"], "assault")
        self.assertGreater(int(assault["mobilising_armies"]["objective"]), 0)
        # The castle's towers punish a direct assault, which is the whole reason
        # the catapult exists.
        self.assertLess(
            sum(int(row["lifepoints"]) for row in assault["mobilising_armies"]["squads"]),
            own_before,
        )

    def test_hoard_gold_moves_by_the_three_exact_period_amounts(self):
        data, rng, _info = _entered(
            squad="heavy_goblin", played=("conflict", "siege"), scenario="hoard",
            order="attack",
        )
        session = data["mobilising_armies"]
        session["rivals"] = [
            {"id": "light_elf", "lifepoints": 1} for _index in range(10)
        ]
        data, ok, result = apply_mobilising_armies_review_pure(data, rng, productive=True)
        self.assertTrue(ok, result)
        self.assertTrue(result["killed"])
        self.assertEqual(result["gold_gained"], 2_500)

    def test_rescue_steals_tzhaar_out_of_the_rival_lander(self):
        data, rng, _info = _entered(
            squad="heavy_goblin", played=("conflict", "siege", "hoard"),
            scenario="rescue", order="attack",
        )
        data["mobilising_armies"]["opponent_objective"] = 10
        data, ok, result = apply_mobilising_armies_review_pure(data, rng, productive=True)
        self.assertTrue(ok, result)
        rescue = MOBILISING_ARMIES_SCENARIOS_BY_ID["rescue"]
        self.assertEqual(result["stolen"], MOBILISING_ARMIES_RESCUE_STEAL_PER_ORDER)
        self.assertEqual(
            int(data["mobilising_armies"]["objective"]),
            MOBILISING_ARMIES_RESCUE_STEAL_PER_ORDER,
        )
        # The steal comes straight out of the rival's stock; the rival then
        # rescues on its own beat, so the net is the steal minus that beat.
        self.assertEqual(
            int(data["mobilising_armies"]["opponent_objective"]),
            10 - MOBILISING_ARMIES_RESCUE_STEAL_PER_ORDER + rescue.opponent_per_beat,
        )


class MobilisingArmiesOfficerTowerTests(unittest.TestCase):
    def test_every_reward_row_is_bought_through_a_real_path(self):
        data = _player(rank=400, reward_credits=10_000_000)
        data["inventory"] = {ring.base_item: 1 for ring in MOBILISING_ARMIES_IMBUE_RINGS}
        spent = 0
        for item_name, (_floor, cost, _refund) in sorted(_REWARD_COSTS.items()):
            with self.subTest(item_name):
                data, info = _command(data, "buy_reward", {"item_name": item_name})
                self.assertEqual(info["cost"], cost)
                self.assertEqual(data["inventory"][item_name], 1)
                spent += cost
        self.assertEqual(
            data["mobilising_armies_reward_credits"], 10_000_000 - spent
        )
        # Imbuing consumes the base ring, which is the acquisition route the
        # source describes.
        for ring in MOBILISING_ARMIES_IMBUE_RINGS:
            self.assertNotIn(ring.base_item, data["inventory"])

    def test_imbuing_without_the_base_ring_is_refused(self):
        data = _player(rank=400, reward_credits=10_000_000)
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "buy_reward", {"item_name": "Onyx ring (i)"}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("Bring a Onyx ring", info["reason"])

    def test_each_floor_is_locked_until_its_own_rank(self):
        for floor in MOBILISING_ARMIES_FLOORS:
            if not floor.minimum_rank:
                continue
            data = _player(rank=floor.minimum_rank - 1, reward_credits=10_000_000)
            row = next(
                item
                for item, (floor_id, _cost, _refund) in _REWARD_COSTS.items()
                if floor_id == floor.id
            )
            _updated, ok, info = apply_mobilising_armies_command_pure(
                data, "buy_reward", {"item_name": row}, lambda: 0.5
            )
            self.assertFalse(ok, floor.id)
            self.assertIn(f"rank {floor.minimum_rank}", info["reason"])
            _updated, ok, info = apply_mobilising_armies_command_pure(
                data, "roll_spoils", {"floor": floor.id}, lambda: 0.5
            )
            self.assertFalse(ok, floor.id)
            view = mobilising_armies_view_pure(data)
            self.assertFalse(
                next(r for r in view["floor_options"] if r["id"] == floor.id)["unlocked"]
            )

    def test_refund_rates_are_eighty_percent_for_gear_and_full_for_uniforms(self):
        data = _player(rank=400, reward_credits=10_000_000)
        for kit in MOBILISING_ARMIES_QUEST_KITS:
            data, _info = _command(data, "buy_reward", {"item_name": kit.item_name})
            before = data["mobilising_armies_reward_credits"]
            data, info = _command(data, "refund_reward", {"item_name": kit.item_name})
            self.assertEqual(info["refund"], kit.credit_cost * 80 // 100)
            self.assertEqual(data["mobilising_armies_reward_credits"], before + info["refund"])
            self.assertNotIn(kit.item_name, data["inventory"])
        for locator in MOBILISING_ARMIES_LOCATORS:
            data, _info = _command(data, "buy_reward", {"item_name": locator.item_name})
            data, info = _command(data, "refund_reward", {"item_name": locator.item_name})
            self.assertEqual(info["refund"], locator.credit_cost * 80 // 100)
        for piece in MOBILISING_ARMIES_UNIFORMS:
            data, _info = _command(data, "buy_reward", {"item_name": piece.item_name})
            data, info = _command(data, "refund_reward", {"item_name": piece.item_name})
            self.assertEqual(info["refund"], piece.credit_cost)
        # The sources give no refund rate for imbued rings, so none is offered.
        data["inventory"]["Gold ring"] = 1
        data, _info = _command(data, "buy_reward", {"item_name": "Gold ring (i)"})
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "refund_reward", {"item_name": "Gold ring (i)"}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("cannot be refunded", info["reason"])

    def test_spoils_of_war_offers_five_and_sells_three_at_the_floor_price(self):
        data = _player(rank=400, reward_credits=10_000_000)
        for floor in MOBILISING_ARMIES_FLOORS:
            with self.subTest(floor.id):
                data, info = _command(
                    data, "roll_spoils", {"floor": floor.id}, rng=random.Random(3).random
                )
                offered = list(info["items"])
                self.assertEqual(len(offered), 5)
                self.assertEqual(len(set(offered)), 5)
                before = data["mobilising_armies_reward_credits"]
                held_before = dict(data["inventory"])
                data, info = _command(data, "claim_spoils", {"items": offered[:3]})
                self.assertEqual(info["cost"], floor.spoils_cost)
                self.assertEqual(
                    data["mobilising_armies_reward_credits"], before - floor.spoils_cost
                )
                expected = dict(MOBILISING_ARMIES_SPOILS[floor.id])
                for item_name in offered[:3]:
                    self.assertEqual(
                        data["inventory"][item_name] - held_before.get(item_name, 0),
                        expected[item_name],
                    )
                # The stall clears, so the next claim needs a fresh look.
                self.assertEqual(data["mobilising_armies_spoils_offer"], {})

    def test_spoils_cannot_be_claimed_off_a_stall_that_is_not_laid_out(self):
        data = _player(rank=400, reward_credits=10_000_000)
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "claim_spoils", {"items": ["Tin ore", "Coal", "Coins"]}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("Look over a Spoils of War stall", info["reason"])
        data, info = _command(data, "roll_spoils", {"floor": "basement"})
        offered = list(info["items"])
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "claim_spoils", {"items": offered[:2]}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("exactly 3", info["reason"])
        absent = next(
            item
            for item, _quantity in MOBILISING_ARMIES_SPOILS["basement"]
            if item not in offered
        )
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "claim_spoils", {"items": [absent, *offered[:2]]}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("not on this stall", info["reason"])

    def test_every_locator_tier_relocates_a_real_gathering_target(self):
        data = _player(rank=400, reward_credits=10_000_000)
        from ankiscape.core.constants import FISHING_DATA, TREE_DATA

        for locator in MOBILISING_ARMIES_LOCATORS:
            data, _info = _command(data, "buy_reward", {"item_name": locator.item_name})
            for skill, table, key in (
                ("mining", ORE_DATA, "current_ore"),
                ("woodcutting", TREE_DATA, "current_tree"),
                ("fishing", FISHING_DATA, "current_fishing"),
            ):
                seen = set()
                for seed in range(24):
                    moved, info = _command(
                        data,
                        "use_locator",
                        {"item_name": locator.item_name, "skill": skill},
                        rng=random.Random(seed).random,
                    )
                    self.assertIn(moved[key], table)
                    seen.add(moved[key])
                    # Locators are devices, not consumables.
                    self.assertEqual(moved["inventory"][locator.item_name], 1)
                expected = {
                    "mining": locator.ore_targets,
                    "woodcutting": locator.tree_targets,
                    "fishing": locator.fishing_targets,
                }[skill]
                self.assertTrue(seen <= set(expected), (locator.item_name, skill))
        _updated, ok, info = apply_mobilising_armies_command_pure(
            data, "use_locator", {"item_name": "Superior locator", "skill": "cooking"}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("resource kind", info["reason"])

    def test_every_quest_kit_empties_its_exact_period_contents(self):
        data = _player(rank=400, reward_credits=10_000_000)
        for kit in MOBILISING_ARMIES_QUEST_KITS:
            with self.subTest(kit.item_name):
                data, _info = _command(data, "buy_reward", {"item_name": kit.item_name})
                before = dict(data["inventory"])
                data, info = _command(
                    data, "open_quest_kit", {"item_name": kit.item_name}
                )
                self.assertEqual(tuple(info["contents"]), kit.contents)
                self.assertNotIn(kit.item_name, data["inventory"])
                for content in kit.contents:
                    self.assertEqual(
                        data["inventory"][content] - before.get(content, 0), 1
                    )
        self.assertIn("Steel pickaxe", MOBILISING_ARMIES_QUEST_KITS[3].contents)
        self.assertNotIn("Bronze pickaxe", MOBILISING_ARMIES_QUEST_KITS[3].contents)

    def test_prefixes_unlock_floor_by_floor(self):
        for floor in MOBILISING_ARMIES_FLOORS:
            data = _player(rank=floor.minimum_rank)
            data, info = _command(data, "set_prefix", {"prefix": floor.prefix})
            self.assertEqual(data["mobilising_armies_prefix"], floor.prefix)
            locked = [
                row.prefix
                for row in MOBILISING_ARMIES_FLOORS
                if row.minimum_rank > floor.minimum_rank
            ]
            for prefix in locked:
                _updated, ok, _info = apply_mobilising_armies_command_pure(
                    data, "set_prefix", {"prefix": prefix}, lambda: 0.5
                )
                self.assertFalse(ok, prefix)
        self.assertEqual(
            MOBILISING_ARMIES_PREFIXES,
            ("Junior Cadet", "Serjeant", "Commander", "War-Chief"),
        )


class MobilisingArmiesPersistenceRuntimeTests(unittest.TestCase):
    def test_v94_migrates_to_the_current_version_and_resumes_an_interrupted_scenario(self):
        old, _rng, _info = _entered(scenario="conflict")
        old["config_version"] = 94
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["activity_session"], {"active_id": MOBILISING_ARMIES_ACTIVITY_ID}
        )
        self.assertTrue(migrated["mobilising_armies"]["squads"])
        self.assertEqual(
            migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS), migrated
        )

    def test_a_pre_family_save_gains_every_default_without_losing_anything(self):
        old = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for key in default_mobilising_armies_state_pure():
            old.pop(key, None)
        old["config_version"] = 94
        old["inventory"] = {"Coal": 7}
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        for key, value in default_mobilising_armies_state_pure().items():
            self.assertEqual(migrated[key], value, key)
        self.assertEqual(migrated["inventory"]["Coal"], 7)

    def test_a_corrupt_session_cannot_leave_a_dangling_activity_owner(self):
        old = _player()
        old["config_version"] = 94
        old["mobilising_armies"] = {"scenario": "not_a_scenario", "squads": [{"id": "x"}]}
        old["activity_session"] = {"active_id": MOBILISING_ARMIES_ACTIVITY_ID}
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["mobilising_armies"], {})
        self.assertEqual(migrated["activity_session"], {"active_id": ""})

    def test_another_activity_holding_the_session_clears_our_scenario(self):
        data, _rng, _info = _entered()
        data["activity_session"] = {"active_id": "soul_wars"}
        self.assertEqual(sanitize_mobilising_armies_state_pure(data)["mobilising_armies"], {})

    def test_the_sanitizer_repairs_out_of_range_and_unknown_state(self):
        clean = sanitize_mobilising_armies_state_pure(
            {
                "mobilising_armies_policy": {
                    "scenario": "sideways",
                    "formation": "phalanx",
                    "order": "nap",
                    "siege_route": "tunnel",
                    "squad": "orcs",
                    "locator_skill": "cooking",
                    "investment": 10 ** 12,
                },
                "mobilising_armies_investment_credits": 10 ** 12,
                "mobilising_armies_squads": {"light_elf": 400, "heavy_elf": 400},
                "mobilising_armies_special_units": {"glider": 99, "cannon": 99},
                "mobilising_armies_scenarios_played": ["rescue", "nope", "conflict"],
                "mobilising_armies_prefix": "Supreme Overlord",
                "mobilising_armies_rank_window": {"beats": 10 ** 9, "points": 10 ** 9},
                "mobilising_armies_spoils_offer": {"floor": "attic", "items": ["Gold"]},
            }
        )
        policy = clean["mobilising_armies_policy"]
        self.assertEqual(policy["scenario"], "conflict")
        self.assertEqual(policy["formation"], "wedge")
        self.assertEqual(policy["order"], "objective")
        self.assertEqual(policy["squad"], "light_elf")
        self.assertEqual(policy["locator_skill"], "mining")
        self.assertEqual(policy["investment"], MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP)
        self.assertEqual(
            clean["mobilising_armies_investment_credits"],
            MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP,
        )
        self.assertEqual(
            sum(clean["mobilising_armies_squads"].values()),
            MOBILISING_ARMIES_SQUAD_CONTRACT_CAP,
        )
        self.assertEqual(
            sum(clean["mobilising_armies_special_units"].values()),
            MOBILISING_ARMIES_SPECIAL_UNIT_CAP,
        )
        self.assertEqual(
            clean["mobilising_armies_scenarios_played"], ["conflict", "rescue"]
        )
        self.assertEqual(clean["mobilising_armies_prefix"], "")
        self.assertEqual(
            clean["mobilising_armies_rank_window"],
            {"beats": 36, "points": MOBILISING_ARMIES_RANK_HOURLY_CAP},
        )
        self.assertEqual(clean["mobilising_armies_spoils_offer"], {})

    def test_an_unknown_command_changes_nothing(self):
        data, _rng, _info = _entered()
        before = copy.deepcopy(data)
        updated, ok, info = apply_mobilising_armies_command_pure(
            data, "sound_the_retreat", {}, lambda: 0.5
        )
        self.assertFalse(ok)
        self.assertIn("Unknown", info["reason"])
        self.assertEqual(updated, before)
        self.assertEqual(data, before)

    def test_no_pure_entry_point_mutates_its_input(self):
        data, rng, _info = _entered(specials=("glider",), scenario="conflict", order="attack")
        for action_id, payload in (
            ("set_policy", {"order": "explore"}),
            ("deploy", {"unit": "glider"}),
            ("forfeit", {}),
        ):
            snapshot = copy.deepcopy(data)
            apply_mobilising_armies_command_pure(
                data, action_id, payload, lambda: 0.5, item_values=ITEM_VALUES
            )
            self.assertEqual(data, snapshot, action_id)
        snapshot = copy.deepcopy(data)
        apply_mobilising_armies_review_pure(data, rng, productive=True)
        self.assertEqual(data, snapshot)

    def test_real_runtime_dispatch_persists_one_order_and_records_telemetry(self):
        player, _rng, _info = _entered(scenario="conflict", order="attack")
        player["current_utility"] = MOBILISING_ARMIES_ACTIVITY_ID
        calls = {"saves": 0, "messages": [], "errors": []}
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda title, message: calls["errors"].append((title, message)),
            deactivate_current_skill=lambda: None,
            award_skill_exp=lambda _key, amount: amount,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
            refresh_skill_availability=lambda: None,
            show_exp=lambda *_args: None,
            show_activity_gain=lambda message: calls["messages"].append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(int(player["mobilising_armies"]["beat"]), 1)
        self.assertEqual(int(player["mobilising_armies"]["commands"]), 1)
        telemetry = player["action_telemetry"]["actions"][
            f"utility:{MOBILISING_ARMIES_ACTIVITY_ID}"
        ]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertTrue(calls["messages"])

        idle, _rng, _info = _entered(seed=1, scenario="conflict", order="attack")
        idle["current_utility"] = MOBILISING_ARMIES_ACTIVITY_ID
        ctx.player_data = idle
        calls.update({"saves": 0, "messages": [], "errors": []})
        from ankiscape.runtime.runtime_actions import handle_mobilising_armies_answer

        self.assertTrue(handle_mobilising_armies_answer(ctx, productive=False))
        self.assertEqual(calls["errors"], [])
        self.assertEqual(int(idle["mobilising_armies"]["beat"]), 1)
        self.assertEqual(int(idle["mobilising_armies"]["commands"]), 0)

    def test_a_review_outside_a_scenario_reports_an_error_through_the_runtime(self):
        player = _mustered()
        player["current_utility"] = MOBILISING_ARMIES_ACTIVITY_ID
        calls = {"errors": []}
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda title, message: calls["errors"].append((title, message)),
            deactivate_current_skill=lambda: None,
            award_skill_exp=lambda _key, amount: amount,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: None,
            refresh_skill_availability=lambda: None,
            show_exp=lambda *_args: None,
            show_activity_gain=lambda *_args: None,
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        from ankiscape.runtime.runtime_actions import handle_mobilising_armies_answer

        self.assertFalse(handle_mobilising_armies_answer(ctx))
        self.assertEqual(len(calls["errors"]), 1)
        self.assertIn("Mobilising Armies", calls["errors"][0][0])


try:
    from aqt.qt import QApplication, QColor, QPalette
    from ankiscape.ui.mobilising_armies_panel import HAS_QT, MobilisingArmiesPanel
except Exception:
    QApplication = None
    HAS_QT = False
    MobilisingArmiesPanel = None


@unittest.skipUnless(HAS_QT, "Qt lane only")
class MobilisingArmiesQtPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
        cls.app.setPalette(palette)

    def _panel(self, player):
        panel = MobilisingArmiesPanel(
            player,
            on_command=lambda *_args: {"ok": True},
            on_select=lambda _activity: True,
        )
        panel.show()
        panel.resize(760, 560)
        for _index in range(4):
            QApplication.processEvents()
        return panel

    def test_the_panel_fits_560_logical_points_idle_and_in_battle(self):
        # The idle state is the tall one: every gate reason and both shop rows
        # are visible before a scenario starts.
        for label, player in (
            ("idle", _player()),
            ("active", _entered(specials=("glider",), scenario="conflict")[0]),
        ):
            with self.subTest(label):
                panel = self._panel(player)
                self.assertLessEqual(panel.sizeHint().height(), 560)
                self.assertLessEqual(panel.layout().minimumSize().height(), 560)
                panel.close()

    def test_dark_560_point_panel_follows_every_pure_view_flag(self):
        player, _rng, _info = _entered(specials=("glider",), scenario="conflict", order="attack")
        panel = self._panel(player)
        view = mobilising_armies_view_pure(player)
        self.assertLessEqual(panel.layout().minimumSize().height(), 560)
        self.assertEqual(panel.primary_button.isEnabled(), view["primary_enabled"])
        self.assertEqual(panel.forfeit_button.isVisible(), view["forfeit_visible"])
        self.assertEqual(
            panel.route_combo.isEnabled(), view["siege_route_control_enabled"]
        )
        self.assertFalse(panel.investment_spin.isEnabled())  # locked mid-battle
        self.assertEqual(
            panel.objective_bar.value(), min(view["objective_target"], view["objective"])
        )
        self.assertEqual(panel.objective_bar.maximum(), view["objective_target"])
        self.assertIn("IN BATTLE", panel.status_chip.text())
        self.assertIn("investment", panel.wallets.text())
        panel.close()

    def test_locked_scenarios_formations_and_floors_are_disabled_from_view_flags(self):
        player = _player()
        panel = self._panel(player)
        view = mobilising_armies_view_pure(player)
        for row in view["scenario_options"]:
            index = panel.scenario_combo.findData(row["id"])
            self.assertGreaterEqual(index, 0, row["id"])
            self.assertEqual(
                panel.scenario_combo.model().item(index).isEnabled(),
                row["unlocked"],
                row["id"],
            )
        for row in view["formation_options"]:
            index = panel.formation_combo.findData(row["id"])
            self.assertEqual(
                panel.formation_combo.model().item(index).isEnabled(), row["unlocked"]
            )
        for row in view["floor_options"]:
            index = panel.floor_combo.findData(row["id"])
            self.assertEqual(
                panel.floor_combo.model().item(index).isEnabled(), row["unlocked"]
            )
        self.assertTrue(panel.requirements.isVisible())
        self.assertIn("Recruit 10", panel.requirements.text())
        self.assertFalse(panel.deploy_button.isEnabled())
        self.assertFalse(panel.claim_button.isEnabled())
        panel.close()

    def test_no_reward_row_is_inert_once_it_is_actually_affordable(self):
        player = _player(rank=400, reward_credits=10_000_000)
        player["inventory"] = {
            ring.base_item: 1 for ring in MOBILISING_ARMIES_IMBUE_RINGS
        }
        panel = self._panel(player)
        view = mobilising_armies_view_pure(player)
        for row in view["reward_options"]:
            index = panel.reward_combo.findData(row["item"])
            self.assertGreaterEqual(index, 0, row["item"])
            panel.reward_combo.setCurrentIndex(index)
            panel.refresh()
            self.assertTrue(row["affordable"], row["item"])
            self.assertTrue(panel.buy_button.isEnabled(), row["item"])
        panel.close()

    def test_the_spoils_stall_renders_the_rolled_offer(self):
        player = _player(rank=400, reward_credits=10_000_000)
        player, _info = _command(
            player, "roll_spoils", {"floor": "second"}, rng=random.Random(1).random
        )
        panel = self._panel(player)
        view = mobilising_armies_view_pure(player)
        for row in view["spoils_offer"]:
            self.assertIn(str(row["item"]), panel.spoils_label.text())
        self.assertEqual(panel.claim_button.isEnabled(), view["spoils_claim_enabled"])
        panel.close()


if __name__ == "__main__":
    unittest.main()
