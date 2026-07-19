import unittest

from livid_farm_logic import (
    advance_livid_farm_wish_effects_pure,
    apply_livid_farm_reviews_pure,
    apply_livid_farm_wish_pure,
    default_livid_farm_state_pure,
    livid_farm_cycle_projection_pure,
    livid_farm_cycles_for_steps_pure,
    livid_farm_locked_reasons_pure,
    livid_farm_wish_rows_pure,
    sanitize_livid_farm_state_pure,
    set_livid_farm_routine_pure,
)
from livid_farm_data import LIVID_FARM_UNLOCKS


def _player(magic_level=99, rune_quantity=100_000):
    inventory = {
        "Astral rune": rune_quantity,
        "Nature rune": rune_quantity,
        "Law rune": rune_quantity,
        "Earth rune": rune_quantity,
        "Water rune": rune_quantity,
        "Cosmic rune": rune_quantity,
        "Mind rune": rune_quantity,
        "Death rune": rune_quantity,
    }
    return {
        "inventory": inventory,
        "equipment": {},
        "quests": {"lunar_diplomacy": {"completed": True}},
        "magic_level": magic_level,
        "agility_level": 60,
        "crafting_level": 60,
        "farming_level": 60,
        "construction_level": 50,
        "livid_farm": default_livid_farm_state_pure(),
    }


class TestLividFarmLogic(unittest.TestCase):
    def test_entry_uses_unboosted_levels(self):
        player = _player(magic_level=69)
        player["combat_current_levels"] = {"magic": 99}

        self.assertEqual(
            livid_farm_locked_reasons_pure(player),
            ("Magic 70",),
        )

    def test_complete_level_70_cycle_matches_reduced_source_model(self):
        player = _player(magic_level=70)

        projection = livid_farm_cycle_projection_pure(player)

        self.assertEqual(projection["points"], 940)
        self.assertEqual(
            projection["rune_cost"],
            {
                "Astral rune": 97,
                "Earth rune": 535,
                "Nature rune": 43,
                "Water rune": 20,
                "Law rune": 6,
            },
        )
        self.assertAlmostEqual(projection["xp_rewards"]["magic"], 900.0)
        self.assertAlmostEqual(projection["xp_rewards"]["farming"], 2754.0)
        self.assertAlmostEqual(projection["xp_rewards"]["construction"], 546.0)
        self.assertAlmostEqual(projection["xp_rewards"]["crafting"], 1080.0)
        self.assertAlmostEqual(projection["xp_rewards"]["agility"], 509.1)

    def test_conserve_omits_duties_below_effective_magic(self):
        player = _player(magic_level=70)
        updated, ok, _info = set_livid_farm_routine_pure(
            player,
            "conserve",
        )
        self.assertTrue(ok)

        projection = livid_farm_cycle_projection_pure(updated)

        self.assertEqual(projection["points"], 300)
        self.assertEqual(
            projection["rune_cost"],
            {"Astral rune": 15, "Earth rune": 120},
        )
        self.assertEqual(
            projection["xp_rewards"],
            {"magic": 900.0, "farming": 1377.0},
        )

    def test_staff_substitutions_apply_to_the_whole_cycle(self):
        player = _player()
        player["equipment"] = {"weapon": "Staff of earth"}

        projection = livid_farm_cycle_projection_pure(player)

        self.assertNotIn("Earth rune", projection["rune_cost"])
        self.assertEqual(projection["rune_cost"]["Astral rune"], 97)

    def test_five_reviews_emit_one_one_one_one_two_cycles(self):
        player = _player()
        emitted = []
        for _review in range(5):
            player, ok, result = apply_livid_farm_reviews_pure(player)
            self.assertTrue(ok)
            emitted.append(result["cycles"])

        self.assertEqual(emitted, [1, 1, 1, 1, 2])
        self.assertEqual(player["livid_farm"]["cadence_credit"], 0)
        self.assertEqual(player["livid_farm"]["cycles_completed"], 6)
        self.assertEqual(player["livid_farm"]["produce_points"], 9_480)

    def test_multiplier_advances_exact_review_steps(self):
        player = _player()

        player, ok, result = apply_livid_farm_reviews_pure(
            player,
            successful_steps=5,
        )

        self.assertTrue(ok)
        self.assertEqual(result["cycles"], 6)
        self.assertEqual(player["livid_farm"]["cadence_credit"], 0)
        self.assertAlmostEqual(result["xp_rewards"]["magic"], 22_422.0)

    def test_review_is_atomic_when_two_cycle_emission_is_underfunded(self):
        player = _player(rune_quantity=0)
        projection = livid_farm_cycle_projection_pure(player)
        player["inventory"] = dict(projection["rune_cost"])
        player["livid_farm"]["cadence_credit"] = 4
        before_inventory = dict(player["inventory"])
        before_state = dict(player["livid_farm"])

        updated, ok, result = apply_livid_farm_reviews_pure(player)

        self.assertFalse(ok)
        self.assertEqual(result["requested_cycles"], 2)
        self.assertEqual(updated["inventory"], before_inventory)
        self.assertEqual(updated["livid_farm"], before_state)

    def test_distraction_fallback_occurs_once_per_twelve_cycles(self):
        player = _player()
        player["livid_farm"]["distraction_credit"] = 11

        updated, ok, result = apply_livid_farm_reviews_pure(
            player,
            rng=lambda: 0.0,
        )

        self.assertTrue(ok)
        self.assertEqual(len(result["distractions"]), 1)
        self.assertEqual(result["distractions"][0]["id"], "sick_ibis")
        self.assertTrue(result["distractions"][0]["completed"])
        self.assertEqual(updated["livid_farm"]["distraction_credit"], 0)
        self.assertAlmostEqual(result["xp_rewards"]["magic"], 3_798.0)

    def test_borrowed_power_claim_spends_capstone_cost_and_keeps_overshoot(self):
        player = _player()
        player["livid_farm"].update(
            {
                "lifetime_produce_points": 849_000,
                "produce_points": 849_000,
                "unlocked_spells": [
                    unlock_id
                    for unlock_id, _name, threshold in LIVID_FARM_UNLOCKS
                    if threshold < 850_000
                ],
            }
        )

        updated, ok, result = apply_livid_farm_reviews_pure(player)

        self.assertTrue(ok)
        self.assertEqual(
            [row["id"] for row in result["new_unlocks"]],
            ["borrowed_power"],
        )
        self.assertEqual(updated["livid_farm"]["lifetime_produce_points"], 850_580)
        self.assertEqual(updated["livid_farm"]["produce_points"], 580)
        self.assertTrue(updated["livid_farm"]["borrowed_power_claimed"])

    def test_state_sanitizer_clamps_enums_residuals_and_wallet(self):
        state = sanitize_livid_farm_state_pure(
            {
                "farm_routine": "invalid",
                "cadence_credit": 12,
                "distraction_credit": 25,
                "cycles_completed": -3,
                "produce_points": 999_999,
                "borrowed_power_claimed": True,
                "unlocked_spells": ["borrowed_power", "future_spell"],
            }
        )

        self.assertEqual(state["farm_routine"], "complete")
        self.assertEqual(state["cadence_credit"], 2)
        self.assertEqual(state["distraction_credit"], 1)
        self.assertEqual(state["cycles_completed"], 0)
        self.assertEqual(state["produce_points"], 850_000)
        self.assertEqual(
            state["unlocked_spells"],
            [unlock_id for unlock_id, _name, _threshold in LIVID_FARM_UNLOCKS],
        )

    def test_cadence_helper_is_exact_for_bulk_steps(self):
        self.assertEqual(livid_farm_cycles_for_steps_pure(0, 5), (6, 0))
        self.assertEqual(livid_farm_cycles_for_steps_pure(4, 1), (2, 0))

    def test_wish_rows_keep_source_and_dependency_blocks_visible(self):
        player = _player()
        player["livid_farm"].update(
            {"borrowed_power_claimed": True, "produce_points": 850_000}
        )

        rows = {row["id"]: row for row in livid_farm_wish_rows_pure(player)}

        self.assertFalse(rows["vial_my_herbs"]["enabled"])
        self.assertIn("clean herb", rows["vial_my_herbs"]["locked_reason"])
        self.assertFalse(rows["rain_seeds"]["enabled"])
        self.assertEqual(rows["rain_seeds"]["status"], "source_blocked")
        self.assertFalse(rows["arcane_capacitor"]["enabled"])
        self.assertEqual(
            rows["arcane_capacitor"]["status"],
            "dependency_blocked",
        )

    def test_vial_my_herbs_transforms_only_carried_eligible_herbs_with_cap(self):
        player = _player()
        player["livid_farm"].update(
            {"borrowed_power_claimed": True, "produce_points": 20_000}
        )
        player["inventory"].update(
            {
                "Clean guam": 70,
                "Clean erzille": 2,
                "Clean sagewort": 4,
                "Cave nightshade": 3,
            }
        )
        player["carried_inventory"] = {
            "livid_farm": {
                "Clean guam": 60,
                "Clean erzille": 2,
                "Clean sagewort": 4,
                "Cave nightshade": 3,
            }
        }

        updated, ok, result = apply_livid_farm_wish_pure(
            player,
            "vial_my_herbs",
        )

        self.assertTrue(ok)
        self.assertEqual(result["outputs"], {
            "Guam potion (unf)": 50,
            "Erzille potion (unf)": 2,
        })
        self.assertEqual(updated["inventory"]["Clean guam"], 20)
        self.assertNotIn("Clean erzille", updated["inventory"])
        self.assertEqual(updated["inventory"]["Clean sagewort"], 4)
        self.assertEqual(updated["inventory"]["Cave nightshade"], 3)
        carried = updated["carried_inventory"]["livid_farm"]
        self.assertEqual(carried["Clean guam"], 10)
        self.assertEqual(carried["Guam potion (unf)"], 50)
        self.assertEqual(
            updated["livid_farm"]["produce_points"],
            14_500,
        )

    def test_lunar_lumber_chunking_matches_one_full_batch(self):
        def convert(chunks):
            player = _player()
            player["livid_farm"].update(
                {"borrowed_power_claimed": True, "produce_points": 850_000}
            )
            totals = {}
            for amount in chunks:
                player["inventory"]["Lunar lumber"] = amount
                player["carried_inventory"] = {
                    "livid_farm": {"Lunar lumber": amount}
                }
                player, ok, result = apply_livid_farm_wish_pure(
                    player,
                    "lunar_lumber",
                )
                self.assertTrue(ok)
                self.assertTrue(all(result["outputs"].values()))
                self.assertTrue(
                    all(quantity > 0 for quantity in player["inventory"].values())
                )
                self.assertTrue(
                    all(
                        quantity > 0
                        for quantity in player.get(
                            "carried_inventory", {}
                        ).get("livid_farm", {}).values()
                    )
                )
                for item_name, quantity in result["outputs"].items():
                    totals[item_name] = totals.get(item_name, 0) + quantity
            return totals, player["livid_farm"]["lunar_lumber_residual"]

        whole, whole_residual = convert([28])
        chunked, chunked_residual = convert([1] * 28)

        self.assertEqual(chunked, whole)
        self.assertEqual(whole["Astral rune"], 25)
        self.assertEqual(whole["Nature rune"], 10)
        self.assertEqual(whole_residual, 0)
        self.assertEqual(chunked_residual, 0)

    def test_inventory_wishes_spend_atomically_and_preserve_exact_bundles(self):
        player = _player()
        player["livid_farm"].update(
            {"borrowed_power_claimed": True, "produce_points": 73_000}
        )

        herbs, ok, herb_result = apply_livid_farm_wish_pure(
            player,
            "gimme_herbs",
        )
        self.assertTrue(ok)
        self.assertEqual(
            herb_result["outputs"],
            {
                "Grimy kwuarm": 3,
                "Grimy irit": 3,
                "Grimy cadantine": 2,
                "Grimy avantoe": 2,
                "Grimy lantadyme": 1,
            },
        )
        seeds, ok, seed_result = apply_livid_farm_wish_pure(
            herbs,
            "awesome_seeds",
        )
        self.assertTrue(ok)
        self.assertEqual(
            seed_result["outputs"],
            {
                "Ranarr seed": 4,
                "Watermelon seed": 4,
                "Curry tree seed": 6,
                "Pineapple seed": 2,
                "Papaya tree seed": 2,
                "Willow seed": 4,
            },
        )
        self.assertEqual(seeds["livid_farm"]["produce_points"], 0)

        unchanged, ok, reason = apply_livid_farm_wish_pure(
            seeds,
            "gimme_herbs",
        )
        self.assertFalse(ok)
        self.assertEqual(reason["reason"], "locked")
        self.assertEqual(unchanged, seeds)

    def test_more_planks_uses_ten_answered_card_world_ticks(self):
        player = _player()
        player["livid_farm"].update(
            {"borrowed_power_claimed": True, "produce_points": 18_000}
        )
        player, ok, _ = apply_livid_farm_wish_pure(player, "more_planks")
        self.assertTrue(ok)

        for remaining in range(9, -1, -1):
            player = advance_livid_farm_wish_effects_pure(player)
            self.assertTrue(
                player["livid_farm"]["more_planks_active_this_review"]
            )
            self.assertEqual(
                player["livid_farm"]["more_planks_reviews_remaining"],
                remaining,
            )
        player = advance_livid_farm_wish_effects_pure(player)
        self.assertFalse(
            player["livid_farm"]["more_planks_active_this_review"]
        )


if __name__ == "__main__":
    unittest.main()
