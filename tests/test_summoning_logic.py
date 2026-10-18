import copy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.summoning_data import SUMMONING_POUCHES_BY_ID
from ankiscape.logic.pace.short_timers import STEP_TICKS
from ankiscape.logic.pace.summoning_clock import (
    BUNYIP_HEAL_LIFEPOINTS,
    BUNYIP_HEAL_TICKS,
    CARGO_RECLAIM_TICKS,
    RENEWAL_WINDOW_TICKS,
    SPECIAL_MOVE_RECHARGE_POINTS,
    SPECIAL_MOVE_RECHARGE_TICKS,
    familiar_lifetime_ticks,
)
from ankiscape.logic.summoning_logic import (
    FAMILIARISATION_ACTIVITY_ID,
    FAMILIARISATION_COOLDOWN_REVIEWS,
    FAMILIARISATION_INGREDIENT_REWARD_ROWS,
    SPECIAL_MOVE_POINTS_MAX,
    advance_summoning_world_tick_pure,
    apply_familiarisation_segment_pure,
    claim_familiarisation_reward_pure,
    apply_summoning_training_action_pure,
    default_summoning_state_pure,
    dismiss_familiar_pure,
    familiar_effective_roll_level_pure,
    familiar_storage_transfer_pure,
    reclaim_familiar_cargo_pure,
    renew_familiar_pure,
    sanitize_summoning_state_pure,
    start_familiarisation_pure,
    set_winter_storage_priority_pure,
    summon_familiar_pure,
    summoning_action_locked_reasons_pure,
    use_familiar_special_pure,
)
from ankiscape.core.constants import ORE_DATA
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data


def player(**overrides):
    data = {
        "summoning_level": 99,
        "summoning_exp": 0,
        "inventory": {},
        "summoning_state": default_summoning_state_pure(),
        "activity_session": {"active_id": ""},
    }
    data["summoning_state"]["summoning_points_current"] = 99
    data.update(overrides)
    return data


class SummoningLogicTests(unittest.TestCase):
    def test_infuse_pouch_consumes_exact_source_recipe(self):
        data = player(
            inventory={
                "Pouch": 2,
                "Spirit shards": 20,
                "Gold charm": 2,
                "Wolf bones": 2,
            }
        )

        updated, ok, result = apply_summoning_training_action_pure(
            data, "infuse_spiritwolf"
        )

        self.assertTrue(ok)
        self.assertEqual(result["xp"], 4.8)
        self.assertEqual(updated["inventory"]["Pouch"], 1)
        self.assertEqual(updated["inventory"]["Spirit shards"], 13)
        self.assertEqual(updated["inventory"]["Gold charm"], 1)
        self.assertEqual(updated["inventory"]["Wolf bones"], 1)
        self.assertEqual(updated["inventory"]["Spirit wolf pouch"], 1)
        self.assertEqual(data["inventory"]["Pouch"], 2)

    def test_alternative_tertiary_uses_one_stocked_hide(self):
        data = player(
            inventory={
                "Pouch": 1,
                "Spirit shards": 120,
                "Crimson charm": 1,
                "Snake hide (swamp)": 1,
            }
        )

        updated, ok, result = apply_summoning_training_action_pure(
            data, "infuse_spiritcobra"
        )

        self.assertTrue(ok)
        self.assertEqual(
            result["requirements"]["Snake hide (swamp)"], 1
        )
        self.assertNotIn("Snake hide", result["requirements"])
        self.assertEqual(updated["inventory"]["Snake hide (swamp)"], 0)
        self.assertEqual(updated["inventory"]["Spirit cobra pouch"], 1)

    def test_locked_training_is_conservation_safe(self):
        data = player(
            inventory={
                "Pouch": 1,
                "Spirit shards": 6,
                "Gold charm": 1,
                "Wolf bones": 1,
            }
        )

        reasons = summoning_action_locked_reasons_pure(
            data, "infuse_spiritwolf"
        )
        updated, ok, result = apply_summoning_training_action_pure(
            data, "infuse_spiritwolf"
        )

        self.assertIn("Missing Spirit shards", reasons)
        self.assertFalse(ok)
        self.assertEqual(result["reason"], "locked")
        self.assertEqual(updated, data)

    def test_shared_scroll_conversion_consumes_one_valid_pouch(self):
        data = player(inventory={"Void spinner pouch": 1})

        updated, ok, result = apply_summoning_training_action_pure(
            data, "scroll_calltoarms"
        )

        self.assertTrue(ok)
        self.assertEqual(result["requirements"], {"Void spinner pouch": 1})
        self.assertEqual(updated["inventory"]["Void spinner pouch"], 0)
        self.assertEqual(updated["inventory"]["Call to arms scroll"], 10)

    def test_summon_spends_pouch_and_points_but_zero_points_does_not_expire(self):
        data = player(
            inventory={"Spirit wolf pouch": 1},
            summoning_state={
                **default_summoning_state_pure(),
                "summoning_points_current": 1,
            },
        )

        active, ok, result = summon_familiar_pure(data, "spiritwolf")

        self.assertTrue(ok)
        self.assertEqual(result["summon_xp"], 0.1)
        self.assertEqual(active["inventory"]["Spirit wolf pouch"], 0)
        state = active["summoning_state"]
        self.assertEqual(state["summoning_points_current"], 0)
        self.assertEqual(state["active_follower"]["remaining_ticks"], 600)

        advanced, tick = advance_summoning_world_tick_pure(active)
        self.assertIsNone(tick["expired_familiar"])
        self.assertEqual(
            advanced["summoning_state"]["active_follower"]["remaining_ticks"],
            600 - STEP_TICKS,
        )
        self.assertEqual(
            advanced["summoning_state"]["summoning_points_current"], 0
        )

    def test_familiar_point_drain_totals_exact_source_amount_per_lifetime(self):
        pouch = SUMMONING_POUCHES_BY_ID["packyak"]
        data = player(inventory={pouch.pouch_name: 1})

        current, ok, _ = summon_familiar_pure(data, pouch.id)
        self.assertTrue(ok)
        after_summon = current["summoning_state"]["summoning_points_current"]
        for _ in range(-(-familiar_lifetime_ticks(pouch) // STEP_TICKS)):
            current, _ = advance_summoning_world_tick_pure(current)

        self.assertEqual(
            after_summon
            - current["summoning_state"]["summoning_points_current"],
            pouch.level - pouch.summoning_point_cost,
        )
        self.assertEqual(
            current["summoning_state"]["active_follower"],
            {},
        )

    def test_zero_summoning_points_advances_drain_phase_without_debt(self):
        pouch = SUMMONING_POUCHES_BY_ID["packyak"]
        data = player(inventory={pouch.pouch_name: 1})
        current, ok, _ = summon_familiar_pure(data, pouch.id)
        self.assertTrue(ok)
        current["summoning_state"]["summoning_points_current"] = 0

        drain_per_card = STEP_TICKS * (pouch.level - pouch.summoning_point_cost)
        for _ in range(11):
            current, _ = advance_summoning_world_tick_pure(current)
        follower = current["summoning_state"]["active_follower"]
        self.assertEqual(
            follower["summoning_point_drain_residual"],
            (11 * drain_per_card) % familiar_lifetime_ticks(pouch),
        )

        current["summoning_state"]["summoning_points_current"] = 99
        current, _ = advance_summoning_world_tick_pure(current)
        self.assertEqual(
            current["summoning_state"]["summoning_points_current"],
            98,
        )

    def test_renewal_is_gated_and_preserves_cargo(self):
        pouch = SUMMONING_POUCHES_BY_ID["packyak"]
        data = player(inventory={"Pack yak pouch": 2})
        active, ok, _ = summon_familiar_pure(data, "packyak")
        self.assertTrue(ok)
        active["summoning_state"]["active_follower"]["storage"] = {"Raw shark": 3}

        unchanged, ok, result = renew_familiar_pure(active)
        self.assertFalse(ok)
        self.assertEqual(result["reason"], "too_early")
        self.assertEqual(unchanged, active)

        active["summoning_state"]["active_follower"]["remaining_ticks"] = RENEWAL_WINDOW_TICKS
        active["summoning_state"]["active_follower"][
            "summoning_point_drain_residual"
        ] = familiar_lifetime_ticks(pouch) - 1
        renewed, ok, result = renew_familiar_pure(active)
        self.assertTrue(ok)
        self.assertEqual(result["reason"], "renewed")
        follower = renewed["summoning_state"]["active_follower"]
        self.assertEqual(follower["remaining_ticks"], familiar_lifetime_ticks(pouch))
        self.assertEqual(follower["summoning_point_drain_residual"], 0)
        self.assertEqual(follower["storage"], {"Raw shark": 3})
        self.assertEqual(renewed["inventory"]["Pack yak pouch"], 0)

    def test_bob_storage_is_separate_and_inaccessible_during_combat(self):
        data = player(inventory={"Pack yak pouch": 1, "Raw shark": 4})
        active, ok, _ = summon_familiar_pure(data, "packyak")
        self.assertTrue(ok)

        unchanged, ok = familiar_storage_transfer_pure(
            active, "Raw shark", 2, to_familiar=True, in_combat=True
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged, active)

        stored, ok = familiar_storage_transfer_pure(
            active, "Raw shark", 2, to_familiar=True
        )
        self.assertTrue(ok)
        self.assertEqual(stored["inventory"]["Raw shark"], 2)
        self.assertEqual(
            stored["summoning_state"]["active_follower"]["storage"],
            {"Raw shark": 2},
        )

    def test_bob_capacity_counts_each_nonstackable_and_enforces_essence_roles(self):
        data = player(inventory={"Thorny snail pouch": 1, "Raw shark": 4})
        active, ok, _ = summon_familiar_pure(data, "thornysnail")
        self.assertTrue(ok)

        unchanged, ok = familiar_storage_transfer_pure(
            active, "Raw shark", 4, to_familiar=True
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged, active)

        stored, ok = familiar_storage_transfer_pure(
            active, "Raw shark", 3, to_familiar=True
        )
        self.assertTrue(ok)
        self.assertEqual(
            stored["summoning_state"]["active_follower"]["storage"],
            {"Raw shark": 3},
        )

        abyssal_data = player(
            inventory={
                "Abyssal parasite pouch": 1,
                "Rune essence": 8,
                "Coal": 1,
            }
        )
        abyssal, ok, _ = summon_familiar_pure(abyssal_data, "abyssalparasite")
        self.assertTrue(ok)
        _, ok = familiar_storage_transfer_pure(
            abyssal, "Coal", 1, to_familiar=True
        )
        self.assertFalse(ok)
        _, ok = familiar_storage_transfer_pure(
            abyssal, "Rune essence", 8, to_familiar=True
        )
        self.assertFalse(ok)
        stored, ok = familiar_storage_transfer_pure(
            abyssal, "Rune essence", 7, to_familiar=True
        )
        self.assertTrue(ok)
        self.assertEqual(
            stored["summoning_state"]["active_follower"]["storage"],
            {"Rune essence": 7},
        )

    def test_expiry_creates_independent_reclaim_event(self):
        data = player(inventory={"Pack yak pouch": 1, "Raw shark": 2})
        active, ok, _ = summon_familiar_pure(data, "packyak")
        self.assertTrue(ok)
        active["summoning_state"]["active_follower"]["remaining_ticks"] = STEP_TICKS
        active["summoning_state"]["active_follower"]["storage"] = {"Raw shark": 2}

        expired, result = advance_summoning_world_tick_pure(active)

        self.assertEqual(result["expired_familiar"], "packyak")
        self.assertEqual(
            result["expired_cargo_event"]["remaining_ticks"],
            CARGO_RECLAIM_TICKS,
        )
        self.assertEqual(expired["summoning_state"]["active_follower"], {})
        event = expired["summoning_state"]["cargo_events"][0]
        self.assertEqual(event["items"], {"Raw shark": 2})

        reclaimed, ok, items = reclaim_familiar_cargo_pure(
            expired, event["event_id"]
        )
        self.assertTrue(ok)
        self.assertEqual(items, {"Raw shark": 2})
        self.assertEqual(reclaimed["inventory"]["Raw shark"], 4)
        self.assertEqual(reclaimed["summoning_state"]["cargo_events"], [])

    def test_each_cargo_deadline_expires_without_touching_other_events(self):
        state = default_summoning_state_pure()
        state["cargo_events"] = [
            {
                "event_id": 1,
                "familiar_id": "packyak",
                "items": {"Raw shark": 1},
                "remaining_ticks": STEP_TICKS,
                "source": "expiry",
            },
            {
                "event_id": 2,
                "familiar_id": "wartortoise",
                "items": {"Coal": 2},
                "remaining_ticks": 3 * STEP_TICKS,
                "source": "dismissal",
            },
        ]
        state["cargo_next_event_id"] = 3

        updated, result = advance_summoning_world_tick_pure(
            player(summoning_state=state)
        )

        self.assertEqual(
            [event["event_id"] for event in result["lost_cargo_events"]], [1]
        )
        retained = updated["summoning_state"]["cargo_events"]
        self.assertEqual(retained[0]["event_id"], 2)
        self.assertEqual(retained[0]["remaining_ticks"], 2 * STEP_TICKS)

    def test_dismissal_does_not_refund_pouch_and_drops_storage(self):
        data = player(inventory={"War tortoise pouch": 1})
        active, ok, _ = summon_familiar_pure(data, "wartortoise")
        self.assertTrue(ok)
        active["summoning_state"]["active_follower"]["storage"] = {"Coal": 2}

        dismissed, ok, result = dismiss_familiar_pure(active)

        self.assertTrue(ok)
        self.assertEqual(dismissed["inventory"]["War tortoise pouch"], 0)
        self.assertEqual(result["cargo_event"]["items"], {"Coal": 2})

    def test_familiarisation_is_four_success_persistent_session(self):
        started, ok = start_familiarisation_pure(player())
        self.assertTrue(ok)
        self.assertEqual(
            started["activity_session"],
            {"active_id": FAMILIARISATION_ACTIVITY_ID},
        )
        activity = started["summoning_state"]["familiarisation"]
        self.assertEqual(
            activity["cooldown_reviews_remaining"],
            FAMILIARISATION_COOLDOWN_REVIEWS,
        )

        current = started
        outcomes = (False, True, False, True, True, False, True)
        successes = 0
        for successful in outcomes:
            successes += int(successful)
            current, ok, result = apply_familiarisation_segment_pure(
                current, successful_answer=successful
            )
            self.assertTrue(ok)
            self.assertEqual(result["segments"], successes)
            self.assertEqual(result["raw_shards"], successes * 15)
            self.assertEqual(result["ended"], successes == 4)
            self.assertNotIn("focus", result)
            self.assertNotIn("focus", current["summoning_state"]["familiarisation"])
        self.assertTrue(result["ended"])
        self.assertEqual(result["segments"], 4)
        self.assertEqual(result["raw_shards"], 60)
        self.assertTrue(
            current["summoning_state"]["familiarisation"]["awaiting_reward"]
        )
        self.assertEqual(
            current["activity_session"],
            {"active_id": FAMILIARISATION_ACTIVITY_ID},
        )

    def test_familiarisation_respects_shared_activity_ownership(self):
        unchanged, ok = start_familiarisation_pure(
            player(activity_session={"active_id": "pest_control"})
        )

        self.assertFalse(ok)
        self.assertEqual(
            unchanged["activity_session"], {"active_id": "pest_control"}
        )

        started, ok = start_familiarisation_pure(player())
        self.assertTrue(ok)
        started["activity_session"] = {"active_id": "pest_control"}
        unchanged, result = advance_summoning_world_tick_pure(
            started, successful_answer=True
        )
        self.assertEqual(
            result["familiarisation"], {"reason": "activity_conflict"}
        )
        self.assertEqual(
            unchanged["summoning_state"]["familiarisation"]["segments"], 0
        )
        self.assertEqual(
            unchanged["activity_session"], {"active_id": "pest_control"}
        )

    def test_migration_removes_focus_and_discounts_only_unearned_active_segments(self):
        for version in (CURRENT_CONFIG_VERSION - 1, CURRENT_CONFIG_VERSION):
            for active in (False, True):
                with self.subTest(version=version, active=active):
                    data = default_player_data(ORE_DATA)
                    data["config_version"] = version
                    data["activity_session"] = {"active_id": FAMILIARISATION_ACTIVITY_ID}
                    data["summoning_state"]["familiarisation"].update(
                        active=active, segments=3, raw_shards=15, focus=0,
                        awaiting_reward=not active, cooldown_reviews_remaining=42,
                        reward_sequence=7,
                    )
                    before = copy.deepcopy(data)
                    migrated = migrate_loaded_data(data, ORE_DATA)
                    state = migrated["summoning_state"]["familiarisation"]
                    self.assertNotIn("focus", state)
                    self.assertEqual(state["active"], active)
                    self.assertEqual(state["segments"], 1 if active else 3)
                    self.assertEqual(state["raw_shards"], 15)
                    self.assertEqual(state["awaiting_reward"], not active)
                    self.assertEqual(state["cooldown_reviews_remaining"], 42)
                    self.assertEqual(state["reward_sequence"], 7)
                    self.assertEqual(migrate_loaded_data(migrated, ORE_DATA), migrated)
                    self.assertEqual(data, before)
                    if active:
                        for _answer in range(3):
                            migrated, ok, result = apply_familiarisation_segment_pure(
                                migrated, successful_answer=True
                            )
                            self.assertTrue(ok, result)
                        self.assertTrue(result["ended"])
                        self.assertEqual(result["raw_shards"], 60)

    def test_familiarisation_notification_has_segments_and_shards_without_focus(self):
        from ankiscape.logic.review_strip_logic import dnd_notification_rows_pure

        data, ok = start_familiarisation_pure(player())
        self.assertTrue(ok)
        self.assertEqual(
            dnd_notification_rows_pure(data, activity_ids=(FAMILIARISATION_ACTIVITY_ID,)),
            ((FAMILIARISATION_ACTIVITY_ID, "0/4 segments · 0/60 shards"),),
        )

    def test_world_tick_advances_familiarisation_only_on_success(self):
        started, ok = start_familiarisation_pure(player())
        self.assertTrue(ok)

        success, result = advance_summoning_world_tick_pure(
            started, successful_answer=True
        )
        self.assertEqual(result["familiarisation"]["segments"], 1)
        self.assertEqual(result["familiarisation"]["raw_shards"], 15)
        self.assertNotIn("focus", result["familiarisation"])

        again, result = advance_summoning_world_tick_pure(
            success, successful_answer=False
        )
        self.assertEqual(result["familiarisation"]["segments"], 1)
        self.assertEqual(result["familiarisation"]["raw_shards"], 15)
        self.assertNotIn("focus", result["familiarisation"])

    def test_familiarisation_rewards_are_immediate_scaled_and_duplicate_safe(self):
        started, ok = start_familiarisation_pure(player())
        self.assertTrue(ok)
        current = started
        for _ in range(4):
            current, ok, _ = apply_familiarisation_segment_pure(
                current, successful_answer=True
            )
            self.assertTrue(ok)

        charmed, ok, result = claim_familiarisation_reward_pure(
            current, "triple_charms"
        )

        self.assertTrue(ok)
        self.assertEqual(result["raw_shards"], 60)
        self.assertEqual(result["ticks"], 4_000)
        self.assertEqual(
            charmed["summoning_state"]["triple_charm_ticks_remaining"], 4_000
        )
        self.assertEqual(charmed["activity_session"], {"active_id": ""})
        unchanged, ok, result = claim_familiarisation_reward_pure(
            charmed, "triple_charms"
        )
        self.assertFalse(ok)
        self.assertEqual(result["reason"], "reward_unavailable")
        self.assertEqual(unchanged, charmed)

    def test_familiarisation_ingredient_box_uses_period_observed_tiers(self):
        self.assertEqual(
            FAMILIARISATION_INGREDIENT_REWARD_ROWS,
            (
                {
                    "minimum_level": 1,
                    "source_shards": 40,
                    "items": {"Raw rabbit": 27, "Raw beef": 42},
                },
                {
                    "minimum_level": 48,
                    "source_shards": 60,
                    "items": {"Raw shark": 19, "Goat horn dust": 22},
                },
            ),
        )
        low = player(summoning_level=1)
        low["summoning_state"]["familiarisation"].update(
            {"awaiting_reward": True, "raw_shards": 40}
        )
        low["activity_session"] = {"active_id": FAMILIARISATION_ACTIVITY_ID}
        low_reward, ok, result = claim_familiarisation_reward_pure(
            low, "ingredients"
        )
        self.assertTrue(ok)
        self.assertEqual(
            result["ingredients"], {"Raw rabbit": 27, "Raw beef": 42}
        )
        self.assertEqual(low_reward["activity_session"], {"active_id": ""})

        high = player(summoning_level=48)
        high["summoning_state"]["familiarisation"].update(
            {"awaiting_reward": True, "raw_shards": 60}
        )
        high_reward, ok, result = claim_familiarisation_reward_pure(
            high, "ingredients"
        )
        self.assertTrue(ok)
        self.assertEqual(
            result["ingredients"], {"Raw shark": 19, "Goat horn dust": 22}
        )
        self.assertEqual(high_reward["inventory"]["Raw shark"], 19)

    def test_familiarisation_ingredient_box_scales_anchor_by_shards(self):
        partial = player(summoning_level=1)
        partial["summoning_state"]["familiarisation"].update(
            {"awaiting_reward": True, "raw_shards": 15}
        )

        updated, ok, result = claim_familiarisation_reward_pure(
            partial, "ingredients"
        )

        self.assertTrue(ok)
        self.assertEqual(
            result["ingredients"], {"Raw rabbit": 10, "Raw beef": 15}
        )
        self.assertEqual(
            updated["inventory"], {"Raw rabbit": 10, "Raw beef": 15}
        )

    def test_bunyip_passive_healing_uses_exact_answer_tick_residual(self):
        data = player(
            constitution_level=50,
            combat_lifepoints=100,
        )
        data["summoning_state"]["active_follower"] = {
            "kind": "familiar",
            "entity_id": "bunyip",
            "remaining_reviews": 10,
            "max_reviews": 10,
            "lifepoints": 4000,
            "max_lifepoints": 4000,
            "storage": {},
        }

        current = data
        healing = []
        for _ in range(9):
            current, result = advance_summoning_world_tick_pure(
                current, successful_answer=False
            )
            healing.append(result["passive_healing"])

        self.assertEqual(
            healing,
            [
                0,
                0,
                0,
                0,
                BUNYIP_HEAL_LIFEPOINTS,
                0,
                0,
                0,
                BUNYIP_HEAL_LIFEPOINTS,
            ],
        )
        self.assertEqual(current["combat_lifepoints"], 140)
        self.assertEqual(
            current["summoning_state"]["active_follower"][
                "bunyip_heal_residual"
            ],
            (9 * STEP_TICKS) % BUNYIP_HEAL_TICKS,
        )

    def test_special_move_recharge_uses_global_exact_answer_tick_residual(self):
        data = player()
        data["summoning_state"]["special_move_points_current"] = 0

        current = data
        points = []
        for _ in range(9):
            current, _ = advance_summoning_world_tick_pure(
                current, successful_answer=False
            )
            points.append(
                current["summoning_state"]["special_move_points_current"]
            )

        self.assertEqual(
            points,
            [0] * 8 + [SPECIAL_MOVE_RECHARGE_POINTS],
        )
        self.assertEqual(
            current["summoning_state"]["special_move_recharge_residual"],
            (9 * STEP_TICKS) % SPECIAL_MOVE_RECHARGE_TICKS,
        )

    def test_familiar_invisible_boosts_change_roll_level_not_base_state(self):
        data = player()
        data["summoning_state"]["active_follower"] = {
            "kind": "familiar",
            "entity_id": "lavatitan",
        }

        self.assertEqual(
            familiar_effective_roll_level_pure(data, "mining", 82), 92
        )
        self.assertEqual(
            familiar_effective_roll_level_pure(data, "firemaking", 80), 90
        )
        self.assertEqual(
            familiar_effective_roll_level_pure(data, "hunter", 82), 82
        )
        self.assertNotIn("mining_level", data)

    def test_ingredient_reward_uses_period_observed_scaled_bundle(self):
        data = player()
        data["summoning_state"]["familiarisation"].update(
            {"awaiting_reward": True, "raw_shards": 30}
        )

        rewarded, ok, result = claim_familiarisation_reward_pure(
            data, "ingredients"
        )

        self.assertTrue(ok)
        self.assertEqual(
            result["ingredients"],
            {"Raw shark": 9, "Goat horn dust": 11},
        )
        for item_name, amount in result["ingredients"].items():
            self.assertEqual(rewarded["inventory"][item_name], amount)

    def test_special_costs_commit_only_after_effect_succeeds(self):
        pouch = SUMMONING_POUCHES_BY_ID["packyak"]
        data = player(
            inventory={"Pack yak pouch": 1, pouch.scroll_name: 1}
        )
        active, ok, _ = summon_familiar_pure(data, pouch.id)
        self.assertTrue(ok)

        def reject(candidate, _pouch):
            candidate["inventory"]["Raw shark"] = 99
            return candidate, False, {"reason": "no_target"}

        unchanged, ok, _ = use_familiar_special_pure(active, reject)
        self.assertFalse(ok)
        self.assertEqual(unchanged, active)

        def accept(candidate, _pouch):
            candidate["inventory"]["Raw shark"] = 1
            return candidate, True, {"reason": "banked"}

        used, ok, result = use_familiar_special_pure(active, accept)
        self.assertTrue(ok)
        self.assertEqual(result["reason"], "banked")
        self.assertEqual(used["inventory"][pouch.scroll_name], 0)
        self.assertEqual(
            used["summoning_state"]["special_move_points_current"],
            SPECIAL_MOVE_POINTS_MAX - pouch.special_points,
        )

    def test_winter_storage_priority_must_name_a_real_carried_item(self):
        data = player(
            carried_inventory={
                "chicken": {"Bones": 2, "Winter storage scroll": 1}
            }
        )
        unchanged, ok = set_winter_storage_priority_pure(
            data, "chicken", "Raw chicken"
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged, data)

        updated, ok = set_winter_storage_priority_pure(
            data, "chicken", "Bones"
        )
        self.assertTrue(ok)
        self.assertEqual(
            updated["summoning_state"]["target_policies"]["chicken"][
                "winter_storage_priority"
            ],
            ["Bones"],
        )
        self.assertEqual(
            updated["summoning_state"]["target_policies"]["chicken"][
                "winter_storage_threshold_free_slots"
            ],
            0,
        )

        data["carried_advanced_targets"] = {"chicken": True}
        advanced, ok = set_winter_storage_priority_pure(
            data, "chicken", "Bones", 3
        )
        self.assertTrue(ok)
        self.assertEqual(
            advanced["summoning_state"]["target_policies"]["chicken"][
                "winter_storage_threshold_free_slots"
            ],
            3,
        )

    def test_sanitizer_clamps_points_and_drops_duplicate_cargo_ids(self):
        raw = {
            "summoning_points_current": 999,
            "special_move_points_current": -5,
            "cargo_events": [
                {
                    "event_id": 4,
                    "familiar_id": "packyak",
                    "items": {"Coal": 2},
                    "remaining_reviews": 2,
                    "source": "expiry",
                },
                {
                    "event_id": 4,
                    "familiar_id": "packyak",
                    "items": {"Coal": 99},
                    "remaining_reviews": 2,
                    "source": "expiry",
                },
            ],
        }

        clean = sanitize_summoning_state_pure(raw, summoning_level=10)

        self.assertEqual(clean["summoning_points_current"], 10)
        self.assertEqual(clean["special_move_points_current"], 0)
        self.assertEqual(clean["special_move_recharge_residual"], 0)
        self.assertEqual(len(clean["cargo_events"]), 1)
        self.assertEqual(clean["cargo_next_event_id"], 5)

    def test_sanitizer_preserves_structured_event_log_entries(self):
        raw = {
            "event_log": [
                {
                    "kind": "unsafe_player_death",
                    "lost_pet_ids": ["pet-1"],
                    "familiar_id": "packyak",
                }
            ]
        }

        clean = sanitize_summoning_state_pure(raw, summoning_level=99)

        self.assertEqual(
            clean["event_log"],
            [
                {
                    "kind": "unsafe_player_death",
                    "lost_pet_ids": ["pet-1"],
                    "familiar_id": "packyak",
                }
            ],
        )

    def test_summoning_storage_default_and_migration_are_idempotent(self):
        default = default_player_data(ORE_DATA)
        self.assertEqual(default["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(default["current_summoning"], "infuse_spiritwolf")
        self.assertEqual(
            default["summoning_state"]["special_move_points_current"], 60
        )
        self.assertTrue(default["pet_auto_care"])

        migrated = migrate_loaded_data(
            {
                "config_version": 40,
                "summoning_level": 12,
                "summoning_exp": 400,
                "current_summoning": "not-a-target",
                "summoning_state": {
                    "summoning_points_current": 999,
                    "special_move_points_current": 12,
                },
            },
            ORE_DATA,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["current_summoning"], "infuse_spiritwolf")
        self.assertEqual(
            migrated["summoning_state"]["summoning_points_current"], 12
        )
        self.assertTrue(migrated["pet_auto_care"])
        self.assertEqual(
            migrate_loaded_data(migrated, ORE_DATA),
            migrated,
        )


if __name__ == "__main__":
    unittest.main()
