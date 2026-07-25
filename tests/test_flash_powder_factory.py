import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.agility_data import AGILITY_TARGETS, AGILITY_TARGETS_BY_ID
from ankiscape.logic.agility_logic import default_agility_state_pure, sanitize_agility_state_pure
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.core.constants import HERBLORE_DATA, UTILITY_ACTIVITY_DATA
from ankiscape.data.flash_powder_factory_data import (
    FLASH_POWDER_FACTORY_ACTIVITY_ID,
    FLASH_POWDER_FACTORY_OUTFIT,
)
from ankiscape.logic.flash_powder_factory_logic import (
    apply_factory_outfit_herblore_bonus_pure,
    apply_flash_powder_factory_review_pure,
    convert_rogue_kit_pure,
    enter_flash_powder_factory_pure,
    flash_powder_factory_view_pure,
    herblore_four_dose_bonus_chance_pure,
    leave_flash_powder_factory_pure,
    redeem_flash_powder_factory_item_pure,
    redeem_flash_powder_factory_xp_pure,
    sanitize_flash_powder_factory_policy_pure,
    sanitize_flash_powder_factory_session_pure,
)
from ankiscape.logic_pure.logic_pure import utility_activity_locked_reasons_pure
from tests.test_integration_smoke import (
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


def _player(**overrides):
    data = default_agility_state_pure()
    data.update(
        {
            "agility_level": 75,
            "thieving_level": 75,
            "herblore_level": 50,
            "inventory": {},
            "equipment": {},
            "activity_session": {"active_id": ""},
            "summoning_state": {"active_follower": {}},
        }
    )
    data.update(overrides)
    return data


def _entered(**overrides):
    data, ok, _info = enter_flash_powder_factory_pure(_player(**overrides))
    if not ok:
        raise AssertionError("test fixture could not enter the Flash Powder Factory")
    return data


class FlashPowderFactoryPureTests(unittest.TestCase):
    def test_activity_registry_owns_factory_while_agility_keeps_its_logic_target(self):
        self.assertIn(FLASH_POWDER_FACTORY_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        self.assertNotIn(
            FLASH_POWDER_FACTORY_ACTIVITY_ID,
            {target.id for target in AGILITY_TARGETS},
        )
        self.assertIn(FLASH_POWDER_FACTORY_ACTIVITY_ID, AGILITY_TARGETS_BY_ID)
        self.assertEqual(
            utility_activity_locked_reasons_pure(
                _player(agility_level=74),
                FLASH_POWDER_FACTORY_ACTIVITY_ID,
                UTILITY_ACTIVITY_DATA,
            ),
            ("Agility 75",),
        )

    def test_entry_enforces_all_period_gates_and_persistent_session_boundary(self):
        for field, value, reason in (
            ("agility_level", 74, "Agility level 75"),
            ("thieving_level", 74, "Thieving level 75"),
            ("herblore_level", 49, "Herblore level 50"),
            ("combat_wilderness_skulled", True, "remove your Wilderness skull"),
        ):
            with self.subTest(field=field):
                _unchanged, ok, info = enter_flash_powder_factory_pure(
                    _player(**{field: value})
                )
                self.assertFalse(ok)
                self.assertIn(reason, info["reason"])

        _unchanged, ok, info = enter_flash_powder_factory_pure(
            _player(activity_session={"active_id": "fight_caves"})
        )
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

    def test_entry_requires_confirmation_and_uses_the_shared_follower_dismissal(self):
        familiar = _player(
            summoning_level=10,
            summoning_state={
                "active_follower": {
                    "kind": "familiar",
                    "entity_id": "spiritwolf",
                    "remaining_reviews": 5,
                    "max_reviews": 5,
                    "storage": {},
                }
            },
        )
        unchanged, ok, info = enter_flash_powder_factory_pure(familiar)
        self.assertFalse(ok)
        self.assertTrue(info["requires_follower_dismissal"])
        self.assertTrue(unchanged["summoning_state"]["active_follower"])

        entered, ok, info = enter_flash_powder_factory_pure(
            familiar,
            confirm_dismiss_follower=True,
        )
        self.assertTrue(ok)
        self.assertEqual(info["dismissed_follower_kind"], "familiar")
        self.assertEqual(entered["summoning_state"]["active_follower"], {})
        self.assertEqual(
            entered["activity_session"],
            {"active_id": FLASH_POWDER_FACTORY_ACTIVITY_ID},
        )

        locked_familiar = dict(familiar)
        locked_familiar["agility_level"] = 74
        unchanged, ok, info = enter_flash_powder_factory_pure(
            locked_familiar,
            confirm_dismiss_follower=True,
        )
        self.assertFalse(ok)
        self.assertIn("Agility level 75", info["reason"])
        self.assertTrue(unchanged["summoning_state"]["active_follower"])

    def test_entry_snapshots_top_and_trousers_benefits(self):
        entered = _entered(
            equipment={"body": "Rogue top", "legs": "Factory trousers"}
        )
        session = entered["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID]
        self.assertEqual(session["total_slots"], 9)
        self.assertEqual(session["catalyst"], 9)
        self.assertEqual(session["apparatus"], 3)
        self.assertEqual(entered["current_utility"], FLASH_POWDER_FACTORY_ACTIVITY_ID)
        self.assertEqual(entered["current_agility"], "burthorpe_course")

    def test_every_productive_review_completes_one_batch_even_on_a_delay(self):
        entered = _entered()
        updated, result = apply_flash_powder_factory_review_pure(
            entered,
            (0.0, 0.0, 0.0, 0.99),
        )
        session = updated["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID]
        self.assertTrue(result["obstacle_failed"])
        self.assertEqual(session["slots_used"], 1)
        self.assertEqual(session["batches"], 1)
        self.assertEqual(session["residue"], 1)
        self.assertEqual(session["catalyst"], 5)
        self.assertGreater(result["score_gain"], 0)

        session["catalyst"] = 0
        detoured, result = apply_flash_powder_factory_review_pure(
            updated,
            (0.99, 0.99, 0.99, 0.99),
        )
        next_session = detoured["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID]
        self.assertTrue(result["catalyst_detour"])
        self.assertEqual(next_session["batches"], 2)
        self.assertEqual(next_session["slots_used"], 2)

    def test_again_consumes_only_an_idle_slot_and_can_close_the_session(self):
        entered = _entered()
        current = entered
        for expected_slot in range(1, 9):
            current, result = apply_flash_powder_factory_review_pure(
                current,
                (),
                productive=False,
            )
            self.assertEqual(result["action_id"], "idle_slot")
            self.assertEqual(result["score_gain"], 0)
            if expected_slot < 8:
                session = current["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID]
                self.assertEqual(session["slots_used"], expected_slot)
                self.assertEqual(session["batches"], 0)
                self.assertEqual(session["residue"], 0)
                self.assertEqual(session["catalyst"], 6)
        self.assertTrue(result["completed_activity"])
        self.assertEqual(result["brianpoints"], 20)
        self.assertNotIn(
            FLASH_POWDER_FACTORY_ACTIVITY_ID,
            current["agility_activity_state"],
        )
        self.assertEqual(current["activity_session"], {"active_id": ""})
        self.assertEqual(
            current["agility_activity_completions"][FLASH_POWDER_FACTORY_ACTIVITY_ID],
            1,
        )

    def test_policy_is_saved_and_casual_keeps_apparatus_behavior_strategy_owned(self):
        self.assertEqual(
            sanitize_flash_powder_factory_policy_pure(
                {
                    "automation_mode": "casual",
                    "strategy": "rogue_equipment",
                    "apparatus_policy": "ignore",
                }
            )["apparatus_policy"],
            "ignore",
        )
        self.assertEqual(
            sanitize_flash_powder_factory_policy_pure(
                {
                    "automation_mode": "advanced",
                    "strategy": "max_points",
                    "apparatus_policy": "opportunistic",
                }
            )["apparatus_policy"],
            "opportunistic",
        )

    def test_apparatus_gain_window_does_not_become_a_loss_at_the_cap(self):
        entered = _entered(
            agility_flash_powder_factory_policy={
                "automation_mode": "advanced",
                "strategy": "balanced",
                "apparatus_policy": "opportunistic",
            }
        )
        session = entered["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID]
        session["apparatus"] = 6
        updated, result = apply_flash_powder_factory_review_pure(
            entered,
            (0.99, 0.99, 0.99, 0.10),
        )
        self.assertEqual(result["apparatus_contest"], "none")
        self.assertEqual(
            updated["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID]["apparatus"],
            6,
        )

    def test_factory_view_does_not_leak_an_unrelated_agility_result(self):
        view = flash_powder_factory_view_pure(
            _player(agility_status="Wilderness course · lap complete")
        )
        self.assertEqual(view["last_result"], "Ready to enter")

    def test_completion_and_early_exit_use_the_period_conversion_cap_and_penalty(self):
        entered = _entered()
        entered["current_agility"] = FLASH_POWDER_FACTORY_ACTIVITY_ID
        session = entered["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID]
        session.update({"slots_used": 7, "batches": 7, "score": 800, "residue": 7})
        completed, result = apply_flash_powder_factory_review_pure(
            entered,
            (0.99, 0.99, 0.99, 0.99),
        )
        self.assertTrue(result["completed_activity"])
        self.assertGreaterEqual(result["brianpoints"], 135)
        self.assertLessEqual(result["brianpoints"], 155)
        self.assertEqual(completed["activity_session"], {"active_id": ""})
        self.assertEqual(completed["current_agility"], "burthorpe_course")

        early = _entered()
        early_session = early["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID]
        early_session.update({"slots_used": 5, "batches": 5, "score": 800, "residue": 5})
        left, ok, info = leave_flash_powder_factory_pure(early)
        self.assertTrue(ok)
        self.assertEqual(info["penalty_percent"], 40)
        self.assertEqual(info["brianpoints"], 81)
        self.assertEqual(left["activity_session"], {"active_id": ""})

        expected_penalties = (50, 50, 50, 50, 50, 40, 26, 0)
        for slots_used, expected in enumerate(expected_penalties):
            with self.subTest(slots_used=slots_used):
                candidate = _entered()
                state = candidate["agility_activity_state"][FLASH_POWDER_FACTORY_ACTIVITY_ID]
                state.update({"slots_used": slots_used, "score": 800})
                _left, ok, info = leave_flash_powder_factory_pure(candidate)
                self.assertTrue(ok)
                self.assertEqual(info["penalty_percent"], expected)

    def test_reward_shop_preserves_exact_lots_skill_rates_and_item_ownership(self):
        player = _player(
            agility_activity_currencies={"brianpoints": 20_000, "circus_audience": 0}
        )
        agility, ok, info = redeem_flash_powder_factory_xp_pure(
            player, "agility", 100
        )
        self.assertTrue(ok)
        self.assertEqual(info["xp"], 9_500.0)
        thieving, ok, info = redeem_flash_powder_factory_xp_pure(
            agility, "thieving", 100
        )
        self.assertTrue(ok)
        self.assertEqual(info["xp"], 12_000.0)

        factory, ok, _info = redeem_flash_powder_factory_item_pure(
            thieving, "Factory mask"
        )
        self.assertTrue(ok)
        unchanged, ok, _info = redeem_flash_powder_factory_item_pure(
            factory, "Factory mask"
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged["inventory"]["Factory mask"], 1)
        kits, ok, _info = redeem_flash_powder_factory_item_pure(factory, "Rogue kit")
        self.assertTrue(ok)
        kits, ok, _info = redeem_flash_powder_factory_item_pure(kits, "Rogue kit")
        self.assertTrue(ok)
        self.assertEqual(kits["inventory"]["Rogue kit"], 2)

        converted, ok, info = convert_rogue_kit_pure(kits, "Rope")
        self.assertTrue(ok)
        self.assertEqual(info["item"], "Rope")
        self.assertEqual(converted["inventory"]["Rogue kit"], 1)
        self.assertEqual(converted["inventory"]["Rope"], 1)
        unchanged, ok, _info = convert_rogue_kit_pure(converted, "Hammer")
        self.assertFalse(ok)
        self.assertEqual(unchanged, converted)

        last_kit = dict(converted)
        last_kit["inventory"] = dict(converted["inventory"])
        last_kit["inventory"]["Rogue kit"] = 1
        converted_last, ok, _info = convert_rogue_kit_pure(last_kit, "Spade")
        self.assertTrue(ok)
        self.assertNotIn("Rogue kit", converted_last["inventory"])

    def test_factory_outfit_applies_three_piece_and_full_set_herblore_effects(self):
        equipment = {
            f"slot_{index}": item
            for index, item in enumerate(sorted(FLASH_POWDER_FACTORY_OUTFIT))
        }
        spec = HERBLORE_DATA["finished_attack_potion"]
        inventory, xp, info = apply_factory_outfit_herblore_bonus_pure(
            "finished_attack_potion",
            {"Attack potion (3)": 1},
            25.0,
            spec,
            equipment,
            0.0,
            HERBLORE_DATA,
        )
        self.assertTrue(info["four_dose"])
        self.assertNotIn("Attack potion (3)", inventory)
        self.assertEqual(inventory["Attack potion (4)"], 1)
        self.assertEqual(xp, 25.0)

        _inventory, xp, info = apply_factory_outfit_herblore_bonus_pure(
            "unf_guam",
            {"Guam potion (unf)": 1},
            0.0,
            HERBLORE_DATA["unf_guam"],
            equipment,
            0.0,
            HERBLORE_DATA,
        )
        self.assertGreater(info["unfinished_xp"], 0.0)
        self.assertEqual(xp, info["unfinished_xp"])

        _inventory, xp, info = apply_factory_outfit_herblore_bonus_pure(
            "unf_spirit_weed",
            {"Spirit weed potion (unf)": 1},
            0.0,
            HERBLORE_DATA["unf_spirit_weed"],
            equipment,
            0.0,
            HERBLORE_DATA,
        )
        self.assertEqual(info["unfinished_xp"], 0.0)
        self.assertEqual(xp, 0.0)

        _inventory, xp, info = apply_factory_outfit_herblore_bonus_pure(
            "synthetic_weapon_poison_plus",
            {"Weapon poison+ (unf)": 1},
            0.0,
            {
                "group": "unf",
                "requirements": {"Cactus spine": 1, "Vial of water": 1},
                "output_item": "Weapon poison+ (unf)",
            },
            equipment,
            0.0,
            HERBLORE_DATA,
        )
        self.assertEqual(info["unfinished_xp"], 8.0)
        self.assertEqual(xp, 8.0)

        overload_inventory, _xp, info = apply_factory_outfit_herblore_bonus_pure(
            "finished_overload",
            {"Overload (3)": 1},
            1_000.0,
            HERBLORE_DATA["finished_overload"],
            equipment,
            0.0,
            HERBLORE_DATA,
        )
        self.assertFalse(info["four_dose"])
        self.assertNotIn("Overload (4)", overload_inventory)

        stacking_equipment = {
            "head": "Factory mask",
            "body": "Factory top",
            "hands": "Factory gloves",
            "legs": "Morytania legs 4",
        }
        self.assertAlmostEqual(
            herblore_four_dose_bonus_chance_pure(
                "finished_prayer_renewal",
                HERBLORE_DATA["finished_prayer_renewal"],
                stacking_equipment,
            ),
            0.30,
        )

    def test_legacy_session_migrates_and_sanitizer_repairs_missing_reservation(self):
        migrated = sanitize_flash_powder_factory_session_pure(
            {
                "total_slots": 8,
                "reviews": 12,
                "deposits": 2,
                "catalyst_charges": 4,
            }
        )
        self.assertEqual(migrated["slots_used"], 4)
        self.assertEqual(migrated["batches"], 2)
        self.assertEqual(migrated["score"], 200)
        repaired = sanitize_agility_state_pure(
            {
                **_player(),
                "activity_session": {"active_id": ""},
                "agility_activity_state": {
                    FLASH_POWDER_FACTORY_ACTIVITY_ID: migrated
                },
            }
        )
        self.assertEqual(
            repaired["activity_session"],
            {"active_id": FLASH_POWDER_FACTORY_ACTIVITY_ID},
        )

    def test_cadence_catalog_declares_one_atomic_factory_circuit(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == FLASH_POWDER_FACTORY_ACTIVITY_ID
        )
        self.assertEqual(row["mode"], "activity_group")
        self.assertIn("one production circuit", row["includes"])


class FlashPowderFactoryHookTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_again_dispatches_one_idle_slot_without_hidden_rng(self):
        addon = _load_addon_as_package("ankiscape_flash_powder_factory_again")
        agility_logic = sys.modules[f"{addon.__name__}.logic.agility_logic"]
        factory_logic = sys.modules[f"{addon.__name__}.logic.flash_powder_factory_logic"]
        player = agility_logic.default_agility_state_pure()
        player.update(
            {
                "agility_level": 75,
                "thieving_level": 75,
                "herblore_level": 50,
                "inventory": {},
                "equipment": {},
                "activity_session": {"active_id": ""},
                "summoning_state": {"active_follower": {}},
            }
        )
        player, ok, _info = factory_logic.enter_flash_powder_factory_pure(player)
        self.assertTrue(ok)
        addon.player_data = player
        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.advance_shop_market_clock_pure = lambda data: dict(data)
        addon.advance_ge_market_tick_pure = lambda data, **_kwargs: (dict(data), {})
        addon.advance_summoning_world_tick_pure = (
            lambda data, **_kwargs: (dict(data), ())
        )
        addon.runtime_actions.advance_farming_clock_for_review = lambda _ctx: {}
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        addon._remember_review_award_snapshot = lambda _before: None
        with patch.object(
            addon.random,
            "random",
            side_effect=AssertionError("Again must not draw Factory RNG"),
        ):
            addon.on_answer_card(
                _FakeReviewer(),
                1,
                lambda _self, _ease: "answered",
            )

        session = addon.player_data["agility_activity_state"][
            FLASH_POWDER_FACTORY_ACTIVITY_ID
        ]
        self.assertEqual(session["slots_used"], 1)
        self.assertEqual(session["batches"], 0)
        self.assertEqual(session["score"], 0)

    def test_good_answer_is_one_slot_under_a_large_review_multiplier(self):
        addon = _load_addon_as_package("ankiscape_flash_powder_factory_multiplier")
        factory_logic = sys.modules[f"{addon.__name__}.logic.flash_powder_factory_logic"]
        player = _player()
        player, ok, _info = factory_logic.enter_flash_powder_factory_pure(player)
        self.assertTrue(ok)
        addon.player_data = player
        addon.current_skill = "Utility / Activities"
        addon.exp_awarded = False
        addon._review_action_multiplier = lambda: 10
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        addon._remember_review_award_snapshot = lambda _before: None
        addon.on_good_answer()
        session = addon.player_data["agility_activity_state"][
            FLASH_POWDER_FACTORY_ACTIVITY_ID
        ]
        self.assertEqual(session["slots_used"], 1)

    def test_legacy_agility_dispatch_uses_the_factory_handler_without_double_loot(self):
        addon = _load_addon_as_package("ankiscape_flash_powder_factory_agility_route")
        factory_logic = sys.modules[f"{addon.__name__}.logic.flash_powder_factory_logic"]
        player = _player(
            agility_flash_powder_factory_policy={
                "automation_mode": "casual",
                "strategy": "rogue_equipment",
                "apparatus_policy": "ignore",
            }
        )
        player, ok, _info = factory_logic.enter_flash_powder_factory_pure(player)
        self.assertTrue(ok)
        player["current_agility"] = FLASH_POWDER_FACTORY_ACTIVITY_ID
        addon.player_data = player
        addon.current_skill = "Agility"
        addon.exp_awarded = False
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        addon._remember_review_award_snapshot = lambda _before: None
        with patch.object(
            addon.random,
            "random",
            side_effect=(0.99, 0.0, 0.999, 0.99),
        ):
            addon.on_good_answer()
        self.assertEqual(addon.player_data["inventory"]["Rogue mask"], 1)


if __name__ == "__main__":
    unittest.main()
