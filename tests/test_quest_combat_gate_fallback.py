from __future__ import annotations

import random
import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure_quest import (
    quest_combat_encounter_ready_pure,
    quest_locked_reasons_pure,
    start_quest_pure,
)
from ankiscape.runtime.runtime_actions import handle_quest_answer
import ankiscape.logic_pure.logic_pure_quest as quest_logic
from tests.test_runtime_actions import _context
from tests.test_combat_quest_gate import _answer_review, _maxed_player_for_quest
from tests.test_integration_smoke import (
    _install_runtime_fakes,
    _load_addon_as_package,
)


EXPLICIT_GATES = {
    ("family_crest", 13, "family_crest_chronozon_170"): 1,
    ("hunt_for_surok", 5, "hunt_for_surok_bork"): 1,
    ("lair_of_tarn_razorlor", 5, "lair_of_tarn_razorlor_mutant_tarn"): 1,
    ("lair_of_tarn_razorlor", 6, "lair_of_tarn_razorlor_tarn_ghost"): 1,
    ("smoking_kills", 2, "smoking_kills_ranged_tomb_guardians"): 85,
    ("smoking_kills", 3, "smoking_kills_ranged_mummy_warrior"): 85,
    ("smoking_kills", 5, "smoking_kills_magic_tomb_guardians"): 85,
    ("smoking_kills", 6, "smoking_kills_magic_mummy_warrior"): 85,
    ("smoking_kills", 9, "smoking_kills_mighty_banshee"): 85,
    ("smoking_kills", 11, "smoking_kills_banshee_mistress"): 85,
}
ENTRY_GATED_QUESTS = ("smoking_kills", "dream_mentor")
SWAN_SONG_ID = "swan_song"
SEA_TROLL_QUEEN_ID = "swan_song_sea_troll_queen"


def _iter_encounters():
    for quest_id, quest in QUEST_DATA.items():
        for requirement in quest.get("stage_requirements", ()) or ():
            stage = requirement.get("stage")
            for encounter in requirement.get("combat_encounters", ()) or ():
                yield quest_id, stage, encounter


def _player_data() -> dict:
    return {}


class TestQuestCombatGateFallback(unittest.TestCase):
    def test_missing_gate_does_not_inherit_an_impossible_enemy_level(self):
        encounter = {
            "encounter_id": "nomad_probe",
            "display_name": "Nomad",
            "level": 699,
            "npc_stats": {
                "hitpoints": 100,
                "attack": 100,
                "strength": 100,
                "defence": 100,
            },
            "npc_configs": {},
        }

        with patch(
            "ankiscape.logic_pure.logic_pure_quest.player_combat_level_pure",
            return_value=80,
        ):
            self.assertEqual(
                quest_combat_encounter_ready_pure(_player_data(), encounter),
                (True, "combat_ready"),
            )

    def test_all_ten_explicit_gates_still_bind_at_their_thresholds(self):
        explicit = {
            (quest_id, stage, encounter["encounter_id"]): encounter
            for quest_id, stage, encounter in _iter_encounters()
            if "minimum_player_combat" in encounter.get("npc_configs", {})
        }
        self.assertEqual(
            {
                key: encounter["npc_configs"]["minimum_player_combat"]
                for key, encounter in explicit.items()
            },
            EXPLICIT_GATES,
        )

        for key, threshold in EXPLICIT_GATES.items():
            encounter = explicit[key]
            with self.subTest(quest_id=key[0], encounter_id=key[2]):
                with patch(
                    "ankiscape.logic_pure.logic_pure_quest.player_combat_level_pure",
                    return_value=threshold - 1,
                ):
                    self.assertEqual(
                        quest_combat_encounter_ready_pure(
                            _player_data(), encounter
                        ),
                        (False, "combat_underpowered"),
                    )
                with patch(
                    "ankiscape.logic_pure.logic_pure_quest.player_combat_level_pure",
                    return_value=threshold,
                ):
                    self.assertEqual(
                        quest_combat_encounter_ready_pure(
                            _player_data(), encounter
                        ),
                        (True, "combat_ready"),
                    )

    def test_catalog_encounters_without_a_gate_never_derive_one_from_npc_level(self):
        ungated = 0
        for quest_id, stage, encounter in _iter_encounters():
            if "minimum_player_combat" in encounter.get("npc_configs", {}):
                continue
            ungated += 1
            ready_encounter = {
                **encounter,
                "npc_stats": {
                    "hitpoints": 1,
                    "attack": 1,
                    "strength": 1,
                    "defence": 1,
                    "magic": 1,
                    "ranged": 1,
                },
            }
            with self.subTest(
                quest_id=quest_id,
                stage=stage,
                encounter_id=encounter.get("encounter_id"),
            ), patch(
                "ankiscape.logic_pure.logic_pure_quest.player_combat_level_pure",
                return_value=1,
            ):
                self.assertEqual(
                    quest_combat_encounter_ready_pure(
                        _player_data(), ready_encounter
                    ),
                    (True, "combat_ready"),
                )
        self.assertEqual(ungated, 283)

    def test_smoking_kills_and_dream_mentor_keep_combat_85_entry_gates(self):
        for quest_id in ENTRY_GATED_QUESTS:
            player = _maxed_player_for_quest(quest_id)
            with self.subTest(quest_id=quest_id), patch(
                "ankiscape.logic_pure.logic_pure_quest.player_combat_level_pure",
                return_value=84,
            ):
                self.assertEqual(
                    quest_locked_reasons_pure(player, quest_id, QUEST_DATA),
                    ("Combat 85",),
                )
                unchanged, started = start_quest_pure(
                    player,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertFalse(started)
                self.assertEqual(unchanged, player)


class TestSourcedQuestCombatReview(unittest.TestCase):
    def test_bone_quest_resumes_at_the_sourced_swamp_rat_after_prior_kills(self):
        quest_id = "rag_and_bone_man"
        encounter_id = "rag_and_bone_man_giant_rat_7"
        player = _maxed_player_for_quest(quest_id)
        player.update(current_quest=quest_id, strength_level=20, attack_level=40, combat_lifepoints=990)
        player["quests"][quest_id] = {"started": True, "progress": 4, "completed": False}
        player["inventory"] = {"Logs": 8}
        prior_kills = [f"rag_and_bone_man_{suffix}" for suffix in (
            "goblin_1", "bear_2", "big_frog_3", "ram_4", "unicorn_5", "monkey_6",
        )]
        player["quest_combat_encounters"] = {quest_id: list(prior_kills)}
        calls = {"xp": [], "saves": 0, "errors": []}
        rng = random.Random(9)
        ctx = _context(player, calls, random_values=(rng.random() for _ in range(10000)))
        ctx.cadence_live_enabled = True
        with patch.object(quest_logic, "apply_combat_burst_pure", wraps=quest_logic.apply_combat_burst_pure) as fight:
            self.assertTrue(handle_quest_answer(ctx))
        enemy = next(iter(fight.call_args.args[1].values()))
        self.assertEqual(enemy["stats"], {"hitpoints": 100, "attack": 6, "strength": 5, "defence": 2})
        for _ in range(100):
            if encounter_id in player["quest_combat_encounters"][quest_id]:
                break
            self.assertTrue(handle_quest_answer(ctx))
        self.assertIn(encounter_id, player["quest_combat_encounters"][quest_id])
        self.assertEqual(calls["activity"][-1], "Defeated Giant rat")
        self.assertTrue(set(prior_kills) <= set(player["quest_combat_encounters"][quest_id]))
        self.assertEqual(player["quests"][quest_id]["progress"], 4)
        self.assertFalse(calls["errors"])

    def test_bone_quest_bear_uses_source_stats_resumes_and_records_the_kill(self):
        quest_id = "rag_and_bone_man"
        encounter_id = "rag_and_bone_man_bear_2"
        player = _maxed_player_for_quest(quest_id)
        player.update(current_quest=quest_id, strength_level=20, attack_level=40, combat_lifepoints=990)
        player["quests"][quest_id] = {"started": True, "progress": 4, "completed": False}
        player["inventory"] = {"Logs": 8}
        player["current_combat_target"] = "chicken"
        player["combat_encounter"] = {"target_id": "chicken", "enemy_lifepoints": 7}
        calls = {"xp": [], "saves": 0, "errors": []}
        rng = random.Random(9)
        ctx = _context(player, calls, random_values=(rng.random() for _ in range(10000)))
        ctx.cadence_live_enabled = True
        with patch.object(quest_logic, "apply_combat_burst_pure", wraps=quest_logic.apply_combat_burst_pure) as fight:
            self.assertTrue(handle_quest_answer(ctx))
        enemy = next(iter(fight.call_args.args[1].values()))
        self.assertEqual(enemy["stats"], {"hitpoints": 250, "attack": 15, "strength": 16, "defence": 13})
        remaining = player["quest_combat_active_encounters"][quest_id][encounter_id]
        self.assertGreater(remaining, 0)
        self.assertLess(remaining, 250)
        self.assertTrue(handle_quest_answer(ctx))
        result = player["combat_last_result"]
        self.assertEqual(result["enemy_lifepoints"], remaining - result["player_damage"])
        for _ in range(100):
            if encounter_id in player.get("quest_combat_encounters", {}).get(quest_id, ()):
                break
            self.assertTrue(handle_quest_answer(ctx))
        self.assertIn(encounter_id, player["quest_combat_encounters"][quest_id])
        self.assertEqual(calls["activity"][-1], "Defeated Bear")
        self.assertEqual(player["quests"][quest_id]["progress"], 4)
        self.assertEqual(player["current_combat_target"], "chicken")
        self.assertEqual(player["combat_encounter"], {"target_id": "chicken", "enemy_lifepoints": 7})
        self.assertFalse(calls["errors"])


class TestQuestCombatGateReviewFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_review_resolves_the_previously_impossible_sea_troll_queen(self):
        addon = _load_addon_as_package("ankiscape_quest_combat_fallback_e2e")
        errors = []
        gains = []
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: gains.append(text)
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: errors.append(
            (title, message)
        )

        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for skill_id in (
            "attack",
            "defense",
            "strength",
            "constitution",
            "prayer",
            "ranged",
            "magic",
            "summoning",
        ):
            player[f"{skill_id}_level"] = 80
        player.update(
            current_quest=SWAN_SONG_ID,
            quest_combat_active_encounters={
                SWAN_SONG_ID: {SEA_TROLL_QUEEN_ID: 1}
            },
            combat_lifepoints=800,
        )
        player["quests"][SWAN_SONG_ID] = {
            "started": True,
            "progress": 5,
            "completed": False,
        }
        addon._state.player_data = player
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            _answer_review(addon)
        finally:
            addon.random.random = original_random

        self.assertIn(
            SEA_TROLL_QUEEN_ID,
            addon._state.player_data["quest_combat_encounters"][SWAN_SONG_ID],
        )
        self.assertEqual(
            addon._state.player_data["quests"][SWAN_SONG_ID]["progress"],
            5,
        )
        self.assertEqual(gains[-1], "Defeated Sea Troll Queen")
        self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()
