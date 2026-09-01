from __future__ import annotations

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


def _resolver_player() -> dict:
    return {"quest_combat_config": {"resolver_enabled": True}}


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
                quest_combat_encounter_ready_pure(_resolver_player(), encounter),
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
                            _resolver_player(), encounter
                        ),
                        (False, "combat_underpowered"),
                    )
                with patch(
                    "ankiscape.logic_pure.logic_pure_quest.player_combat_level_pure",
                    return_value=threshold,
                ):
                    self.assertEqual(
                        quest_combat_encounter_ready_pure(
                            _resolver_player(), encounter
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
                        _resolver_player(), ready_encounter
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
            quest_combat_config={"resolver_enabled": True},
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
        addon.player_data = player
        addon.current_skill = "Quests"
        addon._REVIEW_UNDO_STACK.clear()

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            _answer_review(addon)
        finally:
            addon.random.random = original_random

        self.assertIn(
            SEA_TROLL_QUEEN_ID,
            addon.player_data["quest_combat_encounters"][SWAN_SONG_ID],
        )
        self.assertEqual(
            addon.player_data["quests"][SWAN_SONG_ID]["progress"],
            5,
        )
        self.assertEqual(gains[-1], "Defeated Sea Troll Queen")
        self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()
