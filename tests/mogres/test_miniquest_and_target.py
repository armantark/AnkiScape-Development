import json
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    COMBAT_ENEMY_DATA,
    COOKING_DATA,
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    QUEST_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic.slayer_logic import eligible_slayer_families_pure
from ankiscape.logic_pure.logic_pure import (
    apply_combat_burst_pure,
    apply_cooking_action_pure,
    apply_quest_progress_pure,
    apply_utility_activity_pure,
    combat_target_locked_reasons_pure,
    start_quest_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext
from ankiscape.runtime.runtime_actions_combat import handle_combat_answer
from ankiscape.runtime.runtime_actions_production import handle_quest_answer


QUEST_ID = "skippy_and_the_mogres"
TARGET_ID = "mogre"


def _rng(values):
    values = iter(values)
    return lambda: next(values, 0.0)


def _runtime_context(player_data, calls, random_values=()):
    random_values = iter(random_values)

    def award_skill_exp(exp_key, base_exp):
        player_data[exp_key] = float(player_data.get(exp_key, 0.0) or 0.0) + base_exp
        return base_exp

    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: next(random_values, 0.0),
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda reason=None: calls.setdefault("deactivated", []).append(reason),
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda exp_key, _level_key, base_exp: player_data.__setitem__(
            exp_key, float(player_data.get(exp_key, 0.0) or 0.0) + base_exp
        ),
        level_up_check=lambda _skill, _data: None,
        check_achievements=lambda _data: None,
        save_player_data=lambda: calls.__setitem__("saves", calls.get("saves", 0) + 1),
        refresh_skill_availability=lambda: None,
        show_exp=lambda exp: calls.setdefault("xp", []).append(exp),
        show_activity_gain=lambda text: calls.setdefault("activity", []).append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
        review_action_multiplier=1,
    )


class MogreDataContractTest(unittest.TestCase):
    def test_miniquest_and_nettle_route_preserve_the_pinned_contract(self):
        quest = QUEST_DATA[QUEST_ID]
        self.assertTrue(quest["miniquest"])
        self.assertEqual(quest["point_reward"], 0)
        self.assertEqual(quest["rewards"], {})
        self.assertEqual(quest["xp_rewards"], ())
        self.assertEqual(quest["required_skills"], ({"skill_id": "cooking", "display_name": "Cooking", "level": 20},))
        self.assertEqual(
            tuple(row["auto_actions"] for row in quest["stage_requirements"]),
            (
                ("Sober Skippy with a bucket of water",),
                ("Pick nettles near Draynor Village jail while wearing leather gloves",),
                ("Give Skippy the hot nettle tea",),
                ("Mix Skippy's hangover cure with chocolate dust, milk and snape grass",),
                ("Give Skippy the hangover cure",),
            ),
        )
        self.assertEqual(quest["stage_requirements"][1]["required_tools"], {"Leather gloves": 1})
        self.assertFalse(
            any(
                action.startswith("Complete Mogre stage")
                for row in quest["stage_requirements"]
                for action in row["required_actions"]
            )
        )

        prep = UTILITY_ACTIVITY_DATA["prepare_nettle_water"]
        self.assertEqual(prep["requirements"], {"Bowl of water": 1, "Nettles": 1})
        self.assertEqual(prep["output_item"], "Nettle-water")
        tea = COOKING_DATA["cook_nettle_tea"]
        self.assertEqual((tea["level"], tea["exp"]), (20, 61.0))
        self.assertTrue(tea["source_always_succeeds"])
        self.assertEqual((tea["raw_item"], tea["cooked_item"]), ("Nettle-water", "Nettle tea"))

    def test_mogre_uses_the_exact_main_and_tertiary_tables(self):
        mogre = COMBAT_ENEMY_DATA[TARGET_ID]
        self.assertEqual(
            (mogre["level"], mogre["required_slayer_level"], mogre["slayer_xp"]),
            (60, 32, 48.0),
        )
        self.assertEqual(mogre["quest_gate"], QUEST_ID)
        self.assertEqual(mogre["lure"], {"item": "Fishing explosive", "consumed": True})
        self.assertIs(mogre["poison_immune"], True)
        self.assertEqual(
            mogre["stats"],
            {"hitpoints": 480, "attack": 58, "strength": 55, "defence": 48, "magic": 1, "ranged": 1},
        )
        self.assertEqual(mogre["drops"]["guaranteed"], (("Big bones", 1),))
        ordinary, tertiary = mogre["drops"]["tables"]
        self.assertEqual(ordinary["total"], 128)
        self.assertEqual(sum(row["slots"] for row in ordinary["slots"]), 128)
        self.assertEqual(tertiary["total"], 100000)
        self.assertEqual(sum(row["slots"] for row in tertiary["slots"]), 100000)
        common_seeds = ordinary["slots"][2]["table"]
        self.assertEqual(common_seeds["total"], 1000)
        self.assertEqual(sum(row["slots"] for row in common_seeds["slots"]), 1000)
        registered = {row.storage_key for row in ITEM_DEFINITIONS}
        self.assertEqual(
            {row.get("item") for row in common_seeds["slots"] if row.get("item")} - registered,
            set(),
        )
        self.assertEqual(
            {row.get("item") for row in ordinary["slots"] if row.get("item")} - registered,
            set(),
        )
        self.assertEqual(
            {row.get("item") for row in tertiary["slots"] if row.get("item")} - registered,
            set(),
        )

    def test_completed_miniquest_exposes_mogres_to_both_ready_masters(self):
        completed = {QUEST_ID: {"completed": True}}
        mazchna = eligible_slayer_families_pure(
            {
                "slayer_level": 99,
                "combat_level": 126,
                "quests": {"priest_in_peril": {"completed": True}, **completed},
            },
            "mazchna_achtryn",
        )
        vannaka = eligible_slayer_families_pure(
            {"slayer_level": 99, "combat_level": 126, "quests": completed},
            "vannaka",
        )
        self.assertIn("mogres", {family.id for family in mazchna})
        self.assertIn("mogres", {family.id for family in vannaka})

    def test_all_new_items_have_pinned_icons_and_canonical_flags(self):
        rows = {row.storage_key: row for row in ITEM_DEFINITIONS}
        expected = {
            "Nettles": (4241, False, False),
            "Nettle-water": (4237, False, False),
            "Nettle tea": (4239, False, False),
            "Hangover cure": (1504, False, False),
            "Mudskipper hat": (6665, False, False),
            "Flippers": (6666, False, False),
        }
        for name, (item_id, stackable, tradeable) in expected.items():
            with self.subTest(item=name):
                row = rows[name]
                self.assertEqual((row.source_item_id, row.stackable, row.tradeable), (item_id, stackable, tradeable))
                self.assertTrue(Path(row.asset_path).is_file())

        root = Path(__file__).resolve().parents[2]
        provenance = json.loads((root / "assets_provenance.json").read_text())
        self.assertEqual(provenance["combatenemies/mogre.png"]["timestamp"], "2011-11-26T04:39:41Z")
        self.assertEqual(provenance["combatitems/mudskipper_hat.png"]["timestamp"], "2011-11-26T09:07:28Z")
        self.assertEqual(provenance["combatitems/flippers.png"]["timestamp"], "2011-11-21T04:53:57Z")
        self.assertEqual(provenance["cookingitems/nettle_tea.png"]["timestamp"], "2011-11-26T12:52:37Z")


class MogreMiniquestFlowTest(unittest.TestCase):
    def test_real_reducers_make_the_tea_and_complete_the_miniquest(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["cooking_level"] = 20
        player["inventory"].update(
            {
                "Bucket of water": 1,
                "Bowl of water": 1,
                "Chocolate dust": 1,
                "Bucket of milk": 1,
                "Snape grass": 1,
                "Pestle and mortar": 1,
                "Leather gloves": 1,
            }
        )
        player, started = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(started)

        player, ok, completed = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed)
        inventory, xp, ok, processed = apply_utility_activity_pure(
            "pick_nettles", player["inventory"], UTILITY_ACTIVITY_DATA
        )
        self.assertEqual((xp, ok, processed), (0, True, 1))
        player["inventory"] = inventory
        player, ok, completed = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(player["inventory"]["Nettles"], 0)

        # Stage 2 consumed the picked Nettles; the tea Skippy drinks needs a
        # second pick, and the repeatable gather row makes that possible.
        inventory, xp, ok, processed = apply_utility_activity_pure(
            "pick_nettles", player["inventory"], UTILITY_ACTIVITY_DATA
        )
        self.assertEqual((xp, ok, processed), (0, True, 1))
        player["inventory"] = inventory
        inventory, xp, ok, processed = apply_utility_activity_pure(
            "prepare_nettle_water", player["inventory"], UTILITY_ACTIVITY_DATA
        )
        self.assertEqual((xp, ok, processed), (0, True, 1))
        inventory, xp, ok, output, failed = apply_cooking_action_pure(
            "cook_nettle_tea", inventory, COOKING_DATA, 20, 0.999, use_source_probability=True
        )
        self.assertEqual((xp, ok, output, failed), (61.0, True, "Nettle tea", False))
        player["inventory"] = inventory

        for completed_now in (False, False, True):
            player, ok, completed = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
            self.assertTrue(ok)
            self.assertEqual(completed, completed_now)
        self.assertTrue(player["quests"][QUEST_ID]["completed"])
        self.assertEqual(player["quest_points"], 0)
        self.assertEqual(player["inventory"].get("Hangover cure", 0), 0)

    def test_runtime_quest_handler_reaches_the_same_completion_state(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update({"current_quest": QUEST_ID, "cooking_level": 20})
        player["inventory"].update(
            {
                "Bucket of water": 1,
                "Nettles": 1,
                "Nettle tea": 1,
                "Chocolate dust": 1,
                "Bucket of milk": 1,
                "Snape grass": 1,
                "Pestle and mortar": 1,
                "Leather gloves": 1,
            }
        )
        calls = {"errors": [], "saves": 0}
        ctx = _runtime_context(player, calls)
        for _ in range(5):
            self.assertTrue(handle_quest_answer(ctx), calls)
        self.assertTrue(player["quests"][QUEST_ID]["completed"])
        self.assertEqual(player["quest_points"], 0)
        self.assertEqual(calls["saves"], 5)


class MogreLureTransactionTest(unittest.TestCase):
    def _ready_player(self, explosives=1):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update(
            {
                "current_combat_target": TARGET_ID,
                "slayer_level": 32,
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
                "combat_lifepoints": 990,
            }
        )
        player["quests"][QUEST_ID] = {"started": True, "progress": 6, "completed": True}
        player["inventory"]["Fishing explosive"] = explosives
        return player

    def test_blocked_starts_consume_nothing(self):
        player = self._ready_player()
        player["slayer_level"] = 31
        before = dict(player["inventory"])
        out, ok, result = apply_combat_burst_pure(
            player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0, 0.0])
        )
        self.assertFalse(ok)
        self.assertIn("Slayer level 32", result["locked_reasons"])
        self.assertEqual(out["inventory"], before)

    def test_one_explosive_starts_exactly_one_persistent_mogre(self):
        player = self._ready_player()
        out, ok, result = apply_combat_burst_pure(
            player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0, 0.0])
        )
        self.assertTrue(ok, result)
        self.assertEqual(out["inventory"]["Fishing explosive"], 0)
        self.assertEqual(out["combat_encounter"]["target_id"], TARGET_ID)
        self.assertEqual(combat_target_locked_reasons_pure(out, TARGET_ID, COMBAT_ENEMY_DATA), ())

        out["combat_encounter"]["enemy_lifepoints"] = 1
        killed, ok, result = apply_combat_burst_pure(
            out,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.0, 0.0]),
            allow_bank_run=False,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["kills"], 1)
        self.assertEqual(killed["combat_encounter"], {})
        self.assertEqual(killed["inventory"]["Fishing explosive"], 0)

        blocked, ok, result = apply_combat_burst_pure(
            killed, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=_rng([0.0])
        )
        self.assertFalse(ok)
        self.assertIn("Fishing explosive x1 to lure a Mogre", result["locked_reasons"])
        self.assertEqual(blocked["inventory"]["Fishing explosive"], 0)

    def test_real_combat_handler_consumes_the_lure_atomically(self):
        player = self._ready_player()
        calls = {"errors": [], "saves": 0}
        self.assertTrue(
            handle_combat_answer(_runtime_context(player, calls, (0.0, 0.0))),
            calls,
        )
        self.assertEqual(player["inventory"]["Fishing explosive"], 0)
        self.assertLessEqual(player["combat_last_result"]["kills"], 1)
        self.assertEqual(calls["saves"], 1)


if __name__ == "__main__":
    unittest.main()
