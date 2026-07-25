import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.pet_data import OBTAINABLE_PETS, PETS, PETS_BY_ID
from ankiscape.logic.pet_logic import (
    acquire_pet_pure,
    advance_active_pet_pure,
    let_out_pet_pure,
    release_pet_pure,
    pet_compatible_carried_foods_pure,
    store_active_pet_pure,
)
from ankiscape.logic.summoning_logic import default_summoning_state_pure
from ankiscape.logic.summoning_logic import apply_follower_player_death_pure, summon_familiar_pure


def player(**overrides):
    data = {
        "summoning_level": 99,
        "inventory": {},
        "carried_inventory": {},
        "pet_auto_care": True,
        "summoning_state": default_summoning_state_pure(),
    }
    data.update(overrides)
    return data


class PetLogicTests(unittest.TestCase):
    def test_catalog_has_complete_stable_and_obtainable_boundaries(self):
        self.assertEqual(len(PETS), 47)
        self.assertEqual(len(OBTAINABLE_PETS), 44)
        self.assertEqual(PETS_BY_ID["cat"].stage_count, 3)
        self.assertFalse(PETS_BY_ID["sparkles"].obtainable)
        self.assertTrue(PETS_BY_ID["broav"].release_source_blocked)

    def test_pet_and_familiar_share_one_follower_slot(self):
        acquired, ok, instance_id = acquire_pet_pure(player(), "bulldog")
        self.assertTrue(ok)
        active, ok, _ = let_out_pet_pure(acquired, instance_id)
        self.assertTrue(ok)
        self.assertEqual(
            active["summoning_state"]["active_follower"]["kind"], "pet"
        )

        unchanged, ok, reason = let_out_pet_pure(active, instance_id)
        self.assertFalse(ok)
        self.assertEqual(reason, "follower_slot_occupied")
        self.assertEqual(unchanged, active)

    def test_active_growth_and_hunger_freeze_when_stored(self):
        acquired, ok, instance_id = acquire_pet_pure(player(), "bulldog")
        self.assertTrue(ok)
        active, ok, _ = let_out_pet_pure(acquired, instance_id)
        self.assertTrue(ok)
        advanced, _ = advance_active_pet_pure(active)
        instance = advanced["summoning_state"]["pet_instances"][instance_id]
        self.assertGreater(instance["growth"], 0)
        self.assertGreater(instance["hunger"], 0)

        stored, ok = store_active_pet_pure(advanced)
        self.assertTrue(ok)
        frozen = dict(stored["summoning_state"]["pet_instances"][instance_id])
        unchanged, result = advance_active_pet_pure(stored)
        self.assertIsNone(result["instance_id"])
        self.assertEqual(
            unchanged["summoning_state"]["pet_instances"][instance_id],
            frozen,
        )

    def test_casual_care_consumes_only_active_carried_food(self):
        acquired, ok, instance_id = acquire_pet_pure(
            player(
                inventory={"Bones": 2},
                carried_inventory={
                    "wilderness_course": {"Bones": 1},
                    "inactive_target": {"Bones": 1},
                },
            ),
            "bulldog",
        )
        self.assertTrue(ok)
        active, ok, _ = let_out_pet_pure(acquired, instance_id)
        self.assertTrue(ok)
        active["summoning_state"]["pet_instances"][instance_id]["hunger"] = 72

        fed, result = advance_active_pet_pure(
            active, active_carried_target="wilderness_course"
        )

        self.assertEqual(result["fed_item"], "Bones")
        self.assertEqual(fed["inventory"]["Bones"], 1)
        self.assertEqual(
            fed["carried_inventory"]["wilderness_course"]["Bones"], 0
        )
        self.assertEqual(
            fed["carried_inventory"]["inactive_target"]["Bones"], 1
        )

    def test_source_food_categories_resolve_to_real_inventory_items(self):
        carried = {
            "Raw shark": 1,
            "Shark": 1,
            "Raw beef": 1,
            "Coins": 100,
        }
        self.assertEqual(
            pet_compatible_carried_foods_pure("platypus", carried),
            ("Raw shark",),
        )
        self.assertEqual(
            pet_compatible_carried_foods_pure("cat", carried),
            ("Raw shark", "Shark"),
        )
        self.assertEqual(
            pet_compatible_carried_foods_pure("bulldog", carried),
            ("Raw beef",),
        )

    def test_no_food_safely_returns_pet_before_hunger_loss(self):
        acquired, ok, instance_id = acquire_pet_pure(player(), "bulldog")
        self.assertTrue(ok)
        active, ok, _ = let_out_pet_pure(acquired, instance_id)
        self.assertTrue(ok)
        active["summoning_state"]["pet_instances"][instance_id]["hunger"] = 98

        returned, result = advance_active_pet_pure(active)

        self.assertTrue(result["returned_home"])
        self.assertEqual(returned["summoning_state"]["active_follower"], {})
        instance = returned["summoning_state"]["pet_instances"][instance_id]
        self.assertEqual(instance["location"], "bank")
        self.assertEqual(instance["policy_lapse_reason"], "Out of pet food")

    def test_release_is_blocked_only_where_reacquisition_is_source_blocked(self):
        acquired, ok, broav_id = acquire_pet_pure(player(), "broav")
        self.assertTrue(ok)
        unchanged, ok, reason = release_pet_pure(acquired, broav_id)
        self.assertFalse(ok)
        self.assertEqual(reason, "reacquisition_source_blocked")
        self.assertEqual(unchanged, acquired)

        acquired, ok, bulldog_id = acquire_pet_pure(acquired, "bulldog")
        self.assertTrue(ok)
        released, ok, reason = release_pet_pure(acquired, bulldog_id)
        self.assertTrue(ok)
        self.assertEqual(reason, "released")
        self.assertNotIn(
            bulldog_id, released["summoning_state"]["pet_instances"]
        )

    def test_unsafe_death_destroys_active_and_unprotected_carried_pets_only(self):
        owned, _, active_id = acquire_pet_pure(player(), "bulldog")
        owned, _, carried_id = acquire_pet_pure(
            owned, "dalmatian", location="carried"
        )
        owned, _, protected_id = acquire_pet_pure(
            owned, "greyhound", location="carried"
        )
        owned, _, banked_id = acquire_pet_pure(owned, "labrador")
        owned, _, _ = let_out_pet_pure(owned, active_id)

        died, result = apply_follower_player_death_pure(
            owned, protected_carried_pet_id=protected_id
        )

        instances = died["summoning_state"]["pet_instances"]
        self.assertCountEqual(result["lost_pet_ids"], [active_id, carried_id])
        self.assertNotIn(active_id, instances)
        self.assertNotIn(carried_id, instances)
        self.assertIn(protected_id, instances)
        self.assertIn(banked_id, instances)
        self.assertEqual(died["summoning_state"]["active_follower"], {})

    def test_player_death_ends_familiar_and_creates_separate_cargo_event(self):
        base = player(
            inventory={"Pack yak pouch": 1},
            summoning_state={
                **default_summoning_state_pure(),
                "summoning_points_current": 99,
            },
        )
        active, ok, _ = summon_familiar_pure(base, "packyak")
        self.assertTrue(ok)
        active["summoning_state"]["active_follower"]["storage"] = {"Coal": 2}

        died, result = apply_follower_player_death_pure(active)

        self.assertEqual(result["familiar_id"], "packyak")
        self.assertEqual(result["cargo_event"]["source"], "player_death")
        self.assertEqual(result["cargo_event"]["items"], {"Coal": 2})
        self.assertEqual(died["summoning_state"]["active_follower"], {})


if __name__ == "__main__":
    unittest.main()
