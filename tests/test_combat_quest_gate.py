from __future__ import annotations

import copy
import random
import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.skill_registry import get_skill, trainable_skill_definitions
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure import equip_item_pure
from ankiscape.logic_pure.logic_pure_combat_engine import player_combat_level_pure
import ankiscape.logic_pure.logic_pure_quest as quest_logic
from ankiscape.runtime.runtime_actions import handle_quest_answer
from ankiscape.logic_pure.logic_pure_quest import (
    quest_locked_reasons_pure,
    start_quest_pure,
)
from tests.test_integration_smoke import (
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)
from tests.test_runtime_actions import _context, _quest_combat_mid_rolls


QUEST_ID = "zogre_flesh_eaters"
COMBAT_STAT_IDS = (
    "attack",
    "defense",
    "strength",
    "constitution",
    "prayer",
    "ranged",
    "magic",
    "summoning",
)
AFFECTED_QUEST_IDS = (
    "dream_mentor",
    "grim_tales",
    "legends_quest",
    "smoking_kills",
    "underground_pass",
    "zogre_flesh_eaters",
)


def _combat_requirement(level: int = 89) -> dict:
    return {
        "required_skills": (
            {"skill_id": "combat", "display_name": "Combat", "level": level},
        ),
    }


def _delrith_player(**overrides) -> dict:
    player = {
        "inventory": {},
        "equipment": {"weapon": "Silverlight"},
        "current_quest": "demon_slayer",
        "quests": {"demon_slayer": {"started": True, "progress": 7, "completed": False}},
        "quest_points": 0,
        "pending_skill_exp_rewards": {},
        "completed_achievements": [],
        "attack_level": 10,
        "strength_level": 10,
        "defense_level": 10,
        "constitution_level": 20,
        "combat_lifepoints": 200,
    }
    player.update(overrides)
    return player


def _live_quest_review(player: dict, calls: dict, random_values) -> bool:
    ctx = _context(player, calls, random_values=random_values)
    ctx.cadence_live_enabled = True
    return handle_quest_answer(ctx)


def _set_all_combat_stats(player: dict, level: int) -> None:
    for skill_id in COMBAT_STAT_IDS:
        player[f"{skill_id}_level"] = level


def _complete_prerequisites(player: dict, quest_id: str) -> None:
    for requirement in QUEST_DATA[quest_id].get("required_quests", ()):
        prerequisite_id = requirement["quest_id"]
        player["quests"][prerequisite_id] = {
            "started": True,
            "progress": QUEST_DATA[prerequisite_id]["stages"] + 1,
            "completed": True,
        }


def _maxed_player_for_quest(quest_id: str) -> dict:
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for skill in trainable_skill_definitions():
        player[skill.level_key] = 120 if skill.id == "dungeoneering" else 99
    _set_all_combat_stats(player, 99)
    _complete_prerequisites(player, quest_id)
    player["quest_points"] = 1_000
    return player


def _zogre_player(*, combat_level: int) -> dict:
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    _set_all_combat_stats(player, combat_level)
    player.update(
        fletching_level=30,
        herblore_level=8,
        smithing_level=4,
    )
    _complete_prerequisites(player, QUEST_ID)
    return player


def _low_combat_zogre_player() -> dict:
    player = _zogre_player(combat_level=1)
    player.update(
        constitution_level=10,
        prayer_level=40,
        ranged_level=30,
        strength_level=20,
    )
    return player


def _answer_review(addon) -> None:
    addon._state.card_turned = True
    addon._state.answer_shown = True
    addon._state.exp_awarded = False
    addon.on_answer_card(
        _FakeReviewer(),
        4,
        lambda _self, _ease: "answered",
    )


class TestCombatQuestRequirementResolution(unittest.TestCase):
    def test_quest_required_skill_ids_are_trainable_or_combat(self):
        for quest_id, quest in QUEST_DATA.items():
            for row in (quest, *quest.get("stage_requirements", ())):
                for requirement in row.get("required_skills", ()):
                    skill_id = requirement.get("skill_id")
                    skill = get_skill(skill_id) if isinstance(skill_id, str) else None
                    self.assertTrue(
                        skill_id == "combat" or (skill is not None and skill.trainable),
                        f"{quest_id}: invalid required skill id {skill_id!r}",
                    )

    def test_combat_requirement_boundaries_use_the_derived_combat_level(self):
        quest_data = {"combat_gate": _combat_requirement()}
        cases = (
            (63, 87, ("Combat 89",)),
            (64, 89, ()),
            (65, 90, ()),
        )

        for stat_level, expected_combat, expected_reasons in cases:
            with self.subTest(stat_level=stat_level):
                player = {}
                _set_all_combat_stats(player, stat_level)
                self.assertEqual(player_combat_level_pure(player), expected_combat)
                self.assertEqual(
                    quest_locked_reasons_pure(player, "combat_gate", quest_data),
                    expected_reasons,
                )

    def test_genuinely_unimplemented_skill_keeps_the_sentinel(self):
        quest_data = {
            "unknown_gate": {
                "required_skills": (
                    {
                        "skill_id": "unimplemented_skill",
                        "display_name": "Unimplemented Skill",
                        "level": 5,
                    },
                ),
            }
        }

        self.assertEqual(
            quest_locked_reasons_pure({}, "unknown_gate", quest_data),
            ("Unimplemented Skill 5 (not implemented)",),
        )


class TestCombatQuestStartIntegration(unittest.TestCase):
    def test_low_combat_is_blocked_and_combat_89_starts_zogre_flesh_eaters(self):
        low_player = _low_combat_zogre_player()
        self.assertLess(player_combat_level_pure(low_player), 89)
        self.assertEqual(
            quest_locked_reasons_pure(low_player, QUEST_ID, QUEST_DATA),
            ("Combat 89",),
        )
        unchanged, started = start_quest_pure(low_player, QUEST_ID, QUEST_DATA)
        self.assertFalse(started)
        self.assertEqual(unchanged, low_player)

        ready_player = _zogre_player(combat_level=64)
        self.assertEqual(player_combat_level_pure(ready_player), 89)
        started_player, started = start_quest_pure(
            ready_player,
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(started)
        self.assertTrue(started_player["quests"][QUEST_ID]["started"])
        self.assertFalse(started_player["quests"][QUEST_ID]["completed"])

    def test_all_six_combat_quest_requirements_are_startable_when_met(self):
        for quest_id in AFFECTED_QUEST_IDS:
            with self.subTest(quest_id=quest_id):
                player = _maxed_player_for_quest(quest_id)
                started_player, started = start_quest_pure(
                    player,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertTrue(
                    started,
                    quest_locked_reasons_pure(player, quest_id, QUEST_DATA),
                )
                self.assertTrue(started_player["quests"][quest_id]["started"])


class TestCombatQuestProductFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_starting_zogre_unlocks_the_coffin_chain_before_quest_completion(self):
        addon = _load_addon_as_package("ankiscape_combat_quest_gate_e2e")
        errors = []
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: errors.append(
            (title, message)
        )
        addon._state.player_data = _zogre_player(combat_level=64)
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()

        self.assertTrue(addon.on_set_quest(QUEST_ID), errors)
        self.assertEqual(addon._state.player_data["current_quest"], QUEST_ID)
        self.assertTrue(addon._state.player_data["quests"][QUEST_ID]["started"])
        self.assertEqual(addon._state.player_data["quests"][QUEST_ID]["progress"], 0)
        self.assertFalse(addon._state.player_data["quests"][QUEST_ID]["completed"])

        addon._state.player_data.update(
            current_combat_target="zogre",
            combat_attack_style="aggressive",
            combat_lifepoints=640,
            combat_auto_flee=False,
            combat_supply_loadout={},
            combat_encounter={},
            combat_kill_counts={},
        )
        addon._state.current_skill = "Combat"
        combat_runtime = sys.modules[
            f"{addon.__name__}.runtime.runtime_actions_combat"
        ]
        original_enemies = combat_runtime.COMBAT_ENEMY_DATA
        enemies = dict(original_enemies)
        zogre = copy.deepcopy(enemies["zogre"])
        zogre["stats"].update(
            hitpoints=1,
            attack=1,
            strength=1,
            defence=1,
        )
        enemies["zogre"] = zogre
        original_random = addon.random.random
        combat_runtime.COMBAT_ENEMY_DATA = enemies
        addon.random.random = lambda: 0.0
        try:
            _answer_review(addon)
        finally:
            addon.random.random = original_random
            combat_runtime.COMBAT_ENEMY_DATA = original_enemies

        inventory = addon._state.player_data["inventory"]
        self.assertGreaterEqual(inventory.get("Ogre coffin key", 0), 1)
        self.assertGreaterEqual(inventory.get("Zogre bones", 0), 1)
        self.assertEqual(addon._state.player_data["quests"][QUEST_ID]["progress"], 0)
        self.assertFalse(addon._state.player_data["quests"][QUEST_ID]["completed"])

        self.assertFalse(errors)


class TestCombatQuestRuntime(unittest.TestCase):
    def test_quest_answer_runs_delrith_as_persistent_shared_combat(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Silverlight"},
            "current_combat_target": "chicken",
            "combat_encounter": {"target_id": "chicken", "enemy_lifepoints": 10},
            "current_quest": "demon_slayer",
            "quests": {"demon_slayer": {"started": True, "progress": 7, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "constitution_level": 10,
            "prayer_level": 20,
            "combat_lifepoints": 100,
            "combat_prayer_points": 200,
            "combat_prayer_uptime": "100",
            "combat_selected_prayers": ["burst_of_strength"],
            "combat_supply_loadout": {"food": {"Shrimps": 10}},
            "combat_auto_eat_threshold_percent": 80,
        }
        first_rng = random.Random(2)

        self.assertTrue(
            handle_quest_answer(
                _context(
                    player_data,
                    calls,
                    random_values=(first_rng.random() for _ in range(1000)),
                )
            )
        )

        first_result = player_data["combat_last_result"]
        first_player_lifepoints = player_data["combat_lifepoints"]
        first_remaining = player_data["quest_combat_active_encounters"]["demon_slayer"][
            "demon_slayer_delrith_27"
        ]
        self.assertGreater(first_remaining, 0)
        self.assertLess(first_remaining, 70)
        self.assertEqual(first_result["weapon"], "Silverlight")
        self.assertTrue(first_result["food_used"])
        self.assertEqual(first_result["prayers"], ("burst_of_strength",))
        self.assertEqual(first_result["prayer_uptime"], 1.0)
        self.assertLess(first_result["prayer_points_after"], first_result["prayer_points_before"])
        self.assertLess(first_player_lifepoints, 100)
        second_review_starting_lifepoints = []
        apply_combat_burst = quest_logic.apply_combat_burst_pure

        def capture_starting_lifepoints(combat_player_data, *args, **kwargs):
            second_review_starting_lifepoints.append(combat_player_data["combat_lifepoints"])
            return apply_combat_burst(combat_player_data, *args, **kwargs)

        with patch.object(
            quest_logic,
            "apply_combat_burst_pure",
            side_effect=capture_starting_lifepoints,
        ):
            self.assertTrue(
                handle_quest_answer(
                    _context(player_data, calls, random_values=(0.1,) * 1000)
                )
            )
        second_result = player_data["combat_last_result"]
        second_remaining = player_data["quest_combat_active_encounters"]["demon_slayer"][
            "demon_slayer_delrith_27"
        ]
        self.assertEqual(second_remaining, first_remaining - second_result["player_damage"])
        self.assertEqual(second_review_starting_lifepoints, [first_player_lifepoints])

        self.assertTrue(
            handle_quest_answer(
                _context(player_data, calls, random_values=(0.2,) * 1000)
            )
        )
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {"demon_slayer": ["demon_slayer_delrith_27"]},
        )
        self.assertEqual(player_data["quest_combat_active_encounters"], {})
        self.assertEqual(player_data["current_combat_target"], "chicken")
        self.assertEqual(
            player_data["combat_encounter"],
            {"target_id": "chicken", "enemy_lifepoints": 10},
        )
        self.assertEqual(calls["saves"], 3)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"][-1], "Defeated Delrith")

    def test_quest_answer_reports_the_resolver_outcome_when_delrith_wins(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Silverlight"},
            "current_quest": "demon_slayer",
            "quests": {"demon_slayer": {"started": True, "progress": 7, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "constitution_level": 10,
            "prayer_level": 1,
            "combat_lifepoints": 100,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertFalse(player_data["quests"]["demon_slayer"]["completed"])
        self.assertEqual(player_data["quest_combat_encounters"], {})
        self.assertEqual(player_data["combat_grave"]["items"], ["Silverlight"])
        self.assertEqual(player_data["combat_grave"]["source"], "combat_death")
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["☠ YOU DIED — killed by Delrith; gear moved to grave"])

    def test_live_pacing_fights_delrith_one_combat_slice_per_review(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = _delrith_player()
        rng = random.Random(1)
        reviews = []
        while "demon_slayer" not in player_data.get("quest_combat_encounters", {}):
            self.assertLess(len(reviews), 30)
            self.assertTrue(
                _live_quest_review(player_data, calls, (rng.random() for _ in range(1000)))
            )
            reviews.append(player_data["combat_last_result"])

        self.assertGreater(len(reviews), 2)
        self.assertTrue(all(result["ticks_elapsed"] <= 6 for result in reviews))
        self.assertEqual(len(calls["activity"]), len(reviews))
        for text, result in zip(calls["activity"], reviews[:-1]):
            self.assertEqual(
                text,
                f"Delrith: {result['player_damage']} damage dealt, {result['enemy_lifepoints']} LP left",
            )
        self.assertEqual(calls["activity"][-1], "Defeated Delrith")
        self.assertEqual(player_data["quest_combat_encounter"], {})
        self.assertEqual(calls["errors"], [])

    def test_live_quest_fight_carries_attack_clocks_between_reviews(self):
        # Rolls of 0.0 land every swing for 1 LP, so hits landed count
        # Silverlight's five-tick swings: six across five six-tick reviews.
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = _delrith_player(
            attack_level=1, strength_level=1, defense_level=1, constitution_level=50, combat_lifepoints=500
        )
        hits = []
        for _review in range(5):
            self.assertTrue(_live_quest_review(player_data, calls, (0.0,) * 1000))
            hits.append(player_data["combat_last_result"]["player_hits_landed"])

        self.assertEqual(hits, [2, 1, 1, 1, 1])

    def test_delrith_needs_silverlight_wielded_not_carried(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = _delrith_player(inventory={"Silverlight": 1}, equipment={"weapon": "Bronze sword"})

        self.assertFalse(_live_quest_review(player_data, calls, ()))

        title, message = calls["errors"][0]
        self.assertEqual(title, "Quest blocked")
        self.assertIn("Wield Silverlight to damage Delrith", message)
        self.assertTrue(calls["deactivated"])
        self.assertNotIn("combat_last_result", player_data)

        inventory, equipment, ok = equip_item_pure(
            "Silverlight", player_data["inventory"], player_data["equipment"], EQUIPMENT_DATA
        )
        self.assertTrue(ok)
        player_data.update(inventory=inventory, equipment=equipment)
        self.assertTrue(_live_quest_review(player_data, calls, (0.5,) * 1000))
        self.assertEqual(player_data["combat_last_result"]["weapon"], "Silverlight")
        self.assertEqual(inventory["Bronze sword"], 1)


if __name__ == "__main__":
    unittest.main()
