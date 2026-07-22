import unittest
import os

from stronghold_player_safety_data import (
    COCKROACH_SOLDIER_TARGET_ID,
    SAFETY_GLOVES_ITEM,
    cockroach_soldier_enemy_as_dict,
    stronghold_player_safety_equipment_data_as_dict,
)
from stronghold_player_safety_logic import (
    apply_stronghold_player_safety_command_pure,
    apply_stronghold_player_safety_review_pure,
    sanitize_stronghold_player_safety_state_pure,
    stronghold_player_safety_view_pure,
)


def _player():
    return {
        "inventory": {},
        "equipment": {},
        "combat_grave": {},
        "death_office": {},
        "agility_exp": 0.0,
    }


def _reach_chest(player):
    for _ in range(3):
        player, ok, result = apply_stronghold_player_safety_review_pure(player)
        if not ok:
            raise AssertionError(result)
    return player


class StrongholdPlayerSafetyPureTest(unittest.TestCase):
    def test_cadence_and_registry_expose_the_complete_landmark_boundary(self):
        from cadence_coverage import cadence_coverage_rows_pure
        from constants import (
            COMBAT_ENEMY_IMAGES,
            ITEM_DEFINITIONS,
            UTILITY_ACTIVITY_DATA,
        )

        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["action_id"] == "stronghold_player_safety"
        )
        self.assertEqual(row["mode"], "activity_group")
        self.assertEqual(row["source_status"], "sourced_with_disclosed_translation")
        self.assertIn("no wall-clock input", row["source_reason"])

        activity = UTILITY_ACTIVITY_DATA["stronghold_player_safety"]
        self.assertEqual(activity["group"], "landmarks")
        self.assertTrue(os.path.exists(activity["icon_path"]))
        items = {item.storage_key: item for item in ITEM_DEFINITIONS}
        self.assertEqual(items[SAFETY_GLOVES_ITEM].source_item_id, 12629)
        self.assertTrue(os.path.exists(items[SAFETY_GLOVES_ITEM].asset_path))
        self.assertTrue(os.path.exists(COMBAT_ENEMY_IMAGES[COCKROACH_SOLDIER_TARGET_ID]))

    def test_state_repair_clamps_route_and_derived_unlocks(self):
        state = sanitize_stronghold_player_safety_state_pure(
            {
                "stage": 99,
                "crevice_unlocked": False,
                "chest_claimed": True,
                "lamps_remaining": 99,
            }
        )
        self.assertEqual(state["stage"], 3)
        self.assertTrue(state["crevice_unlocked"])
        self.assertTrue(state["chest_claimed"])
        self.assertEqual(state["lamps_remaining"], 2)

        early = sanitize_stronghold_player_safety_state_pure(
            {"stage": 0, "crevice_unlocked": True, "chest_claimed": True}
        )
        self.assertFalse(early["crevice_unlocked"])
        self.assertFalse(early["chest_claimed"])

    def test_three_landmarks_unlock_the_chest_and_crevice(self):
        player = _player()
        for expected_action in (
            "poster_tunnel",
            "lever_and_rope",
            "reward_passage",
        ):
            player, ok, result = apply_stronghold_player_safety_review_pure(player)
            self.assertTrue(ok, result)
            self.assertEqual(result["action_id"], expected_action)
        view = stronghold_player_safety_view_pure(player)
        self.assertTrue(view["crevice_unlocked"])
        self.assertTrue(view["can_claim_chest"])
        self.assertFalse(view["can_review"])
        unchanged, ok, result = apply_stronghold_player_safety_review_pure(player)
        self.assertFalse(ok)
        self.assertEqual(unchanged, player)
        self.assertIn("complete", result["reason"])

    def test_chest_is_atomic_and_one_time(self):
        player = _reach_chest(_player())
        player, ok, result = apply_stronghold_player_safety_command_pure(
            player, "claim_chest"
        )
        self.assertTrue(ok, result)
        self.assertEqual(player["inventory"]["Coins"], 10_000)
        self.assertEqual(player["inventory"][SAFETY_GLOVES_ITEM], 1)
        self.assertEqual(player["stronghold_player_safety"]["lamps_remaining"], 2)
        self.assertTrue(
            player["stronghold_player_safety"]["safety_first_emote_unlocked"]
        )
        unchanged, ok, result = apply_stronghold_player_safety_command_pure(
            player, "claim_chest"
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged, player)
        self.assertIn("already claimed", result["reason"])

    def test_two_lamps_each_grant_500_xp_to_a_trainable_skill(self):
        player = _reach_chest(_player())
        player, ok, _result = apply_stronghold_player_safety_command_pure(
            player, "claim_chest"
        )
        self.assertTrue(ok)
        for expected_total in (500.0, 1000.0):
            player, ok, result = apply_stronghold_player_safety_command_pure(
                player, "claim_lamp", {"skill_id": "agility"}
            )
            self.assertTrue(ok, result)
            self.assertEqual(player["agility_exp"], expected_total)
        unchanged, ok, result = apply_stronghold_player_safety_command_pure(
            player, "claim_lamp", {"skill_id": "agility"}
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged, player)
        self.assertIn("No Stronghold XP lamp", result["reason"])

    def test_lamp_rejects_non_trainable_or_unknown_skills(self):
        player = _reach_chest(_player())
        player, ok, _result = apply_stronghold_player_safety_command_pure(
            player, "claim_chest"
        )
        self.assertTrue(ok)
        for skill_id in ("dungeoneering", "not_a_skill"):
            with self.subTest(skill_id=skill_id):
                unchanged, ok, result = apply_stronghold_player_safety_command_pure(
                    player, "claim_lamp", {"skill_id": skill_id}
                )
                self.assertFalse(ok)
                self.assertEqual(unchanged, player)
                self.assertIn("trainable", result["reason"])

    def test_gloves_reclaim_respects_every_owned_location(self):
        player = _reach_chest(_player())
        player, ok, _result = apply_stronghold_player_safety_command_pure(
            player, "claim_chest"
        )
        self.assertTrue(ok)
        player["inventory"].pop(SAFETY_GLOVES_ITEM)

        for location, value in (
            ("equipment", {"hands": SAFETY_GLOVES_ITEM}),
            ("combat_grave", {"items": [SAFETY_GLOVES_ITEM]}),
            ("death_office", {"items": [SAFETY_GLOVES_ITEM]}),
        ):
            with self.subTest(location=location):
                owned = dict(player)
                owned[location] = value
                unchanged, ok, result = apply_stronghold_player_safety_command_pure(
                    owned, "reclaim_gloves"
                )
                self.assertFalse(ok)
                self.assertEqual(unchanged, owned)
                self.assertIn("still own", result["reason"])

        player, ok, result = apply_stronghold_player_safety_command_pure(
            player, "reclaim_gloves"
        )
        self.assertTrue(ok, result)
        self.assertEqual(player["inventory"][SAFETY_GLOVES_ITEM], 1)

    def test_soldier_fight_requires_the_room_and_an_open_combat_slot(self):
        player = _player()
        unchanged, ok, result = apply_stronghold_player_safety_command_pure(
            player, "start_soldier_fight"
        )
        self.assertFalse(ok)
        self.assertNotIn("combat_encounter", unchanged)
        self.assertEqual(unchanged["inventory"], player["inventory"])
        self.assertIn("soldier room", result["reason"])

        for _ in range(2):
            player, ok, _result = apply_stronghold_player_safety_review_pure(player)
            self.assertTrue(ok)
        player, ok, result = apply_stronghold_player_safety_command_pure(
            player, "start_soldier_fight"
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["switch_skill"], "Combat")
        self.assertEqual(player["current_combat_target"], COCKROACH_SOLDIER_TARGET_ID)
        self.assertEqual(player["combat_encounter"]["enemy_lifepoints"], 960)
        self.assertFalse(stronghold_player_safety_view_pure(player)["can_fight_soldier"])

    def test_soldier_fight_cannot_overlap_a_persistent_activity(self):
        player = _player()
        for _ in range(2):
            player, ok, _result = apply_stronghold_player_safety_review_pure(player)
            self.assertTrue(ok)
        player["activity_session"] = {"active_id": "barbarian_assault"}
        self.assertFalse(
            stronghold_player_safety_view_pure(player)["can_fight_soldier"]
        )
        updated, ok, result = apply_stronghold_player_safety_command_pure(
            player, "start_soldier_fight"
        )
        self.assertFalse(ok)
        self.assertNotIn("combat_encounter", updated)
        self.assertIn("persistent activity", result["reason"])

    def test_period_enemy_and_glove_rows_disclose_their_boundaries(self):
        enemy = cockroach_soldier_enemy_as_dict()
        self.assertEqual(enemy["level"], 83)
        self.assertEqual(enemy["stats"]["hitpoints"], 960)
        self.assertEqual(enemy["attack_speed"], 6)
        self.assertEqual(enemy["max_hit"], 110)
        self.assertTrue(enemy["encounter_only"])
        self.assertEqual(enemy["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("source_blocked", enemy["source_status"])

        gloves = stronghold_player_safety_equipment_data_as_dict()[
            SAFETY_GLOVES_ITEM
        ]
        self.assertEqual(gloves.source_item_id, 12629)
        self.assertEqual(gloves.slot, "hands")
        self.assertEqual(gloves.bonuses.defence_stab, 1)
        self.assertEqual(gloves.bonuses.defence_slash, 2)
        self.assertEqual(gloves.bonuses.defence_crush, 2)
        self.assertEqual(gloves.bonuses.defence_magic, 1)
        self.assertEqual(gloves.bonuses.defence_ranged, 2)
        self.assertIn("Summoning defence", gloves.source_status)

    def test_started_soldier_encounter_enters_live_combat_without_catalog_access(self):
        from constants import COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
        from logic_pure import apply_combat_burst_pure, combat_target_locked_reasons_pure
        from storage_pure import default_player_data

        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for _ in range(2):
            player, ok, _result = apply_stronghold_player_safety_review_pure(player)
            self.assertTrue(ok)
        player, ok, result = apply_stronghold_player_safety_command_pure(
            player, "start_soldier_fight"
        )
        self.assertTrue(ok, result)
        self.assertEqual(
            combat_target_locked_reasons_pure(
                player,
                COCKROACH_SOLDIER_TARGET_ID,
                COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            ),
            (),
        )
        updated, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=6,
            rng=lambda: 0.5,
            live_cadence=True,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["target_id"], COCKROACH_SOLDIER_TARGET_ID)
        self.assertEqual(
            updated["combat_encounter"]["target_id"],
            COCKROACH_SOLDIER_TARGET_ID,
        )


if __name__ == "__main__":
    unittest.main()
