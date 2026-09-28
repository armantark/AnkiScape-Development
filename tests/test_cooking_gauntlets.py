import sys
import unittest

import pkg_alias  # noqa: F401
from tests.test_runtime_actions import _context

from ankiscape.core.constants import COOKING_DATA, EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from ankiscape.logic.cooking_gauntlets_logic import (
    apply_family_gauntlet_conversion_pure,
    cooking_equipment_choice_pure,
    cooking_gauntlets_worn_pure,
    family_gauntlet_recovery_state_pure,
    recover_family_gauntlets_pure,
    reconcile_cooking_equipment_pure,
    set_cooking_equipment_choice_pure,
)
from ankiscape.logic_pure.logic_pure import (
    apply_cooking_action_pure,
    cooking_source_roll_chance_pure,
)
from ankiscape.runtime.runtime_actions import (
    handle_cooking_answer,
    run_answer_with_carried_overlay,
)


def _gloved_cook(target="cook_lobster", level=99):
    return {
        "inventory": {**COOKING_DATA[target]["requirements"], "Cooking gauntlets": 1},
        "equipment": {"hands": "Brawling gloves (cooking)"},
        "cooking_level": level,
        "cooking_exp": 0,
        "current_cooking": target,
        "completed_achievements": [],
    }


class CookingGauntletRuntimeTests(unittest.TestCase):

    def _review(self, player, *, live=True, roll=0.0):
        calls = {"xp": [], "saves": 0, "errors": []}
        ctx = _context(player, calls, random_values=[roll])
        ctx.cadence_live_enabled = live
        self.assertTrue(run_answer_with_carried_overlay(ctx, "cooking", handle_cooking_answer))
        self.assertEqual(calls["errors"], [])
        return calls

    def test_auto_retains_brawling_xp_when_lobster_cannot_burn(self):
        for choice in ("none", "auto"):
            with self.subTest(choice=choice):
                player = _gloved_cook()
                player["cooking_equipment_choices"] = {"cook_lobster": choice}
                calls = self._review(player, roll=0.999)
                self.assertEqual(calls["xp"], [180.0])
                self.assertEqual(player["cooking_exp"], 180.0)
                self.assertEqual(player["equipment"]["hands"], "Brawling gloves (cooking)")
                self.assertEqual(player["inventory"]["Lobster"], 1)
                self.assertEqual(player["inventory"]["Cooking gauntlets"], 1)
                self.assertEqual(player["cooking_equipment_swap"], {})

    def test_auto_retains_gloves_when_gauntlets_do_not_reduce_burns(self):
        for target, level, live in (("cook_shark", 93, True), ("cook_shark", 93, False), ("cook_bass", 99, False)):
            with self.subTest(target=target, live=live):
                player = _gloved_cook(target, level)
                self._review(player, live=live)
                self.assertEqual(player["equipment"]["hands"], "Brawling gloves (cooking)")
                self.assertEqual(player["cooking_exp"], COOKING_DATA[target]["exp"] * 1.5)
                self.assertEqual(player["cooking_equipment_swap"], {})

    def test_auto_prevents_burns_using_the_active_probability_mode(self):
        for target, level, live in (("cook_shark", 94, True), ("cook_shark", 94, False), ("cook_lobster", 99, False)):
            with self.subTest(target=target, live=live):
                player = _gloved_cook(target, level)
                self._review(player, live=live, roll=0.999)
                self.assertEqual(player["equipment"]["hands"], "Cooking gauntlets")
                self.assertEqual(player["cooking_exp"], COOKING_DATA[target]["exp"])
                self.assertEqual(player["inventory"][COOKING_DATA[target]["output_item"]], 1)

    def test_explicit_cooking_policy_still_equips_without_a_burn_benefit(self):
        player = _gloved_cook()
        player["cooking_equipment_choices"] = {"cook_lobster": "cooking"}
        self._review(player)
        self.assertEqual(player["equipment"]["hands"], "Cooking gauntlets")
        self.assertEqual(player["cooking_exp"], 120.0)

    def test_auto_restores_displaced_gloves_when_the_next_target_cannot_burn(self):
        player = _gloved_cook("cook_shark", 99)
        player["inventory"]["Raw lobster"] = 1
        self._review(player, roll=0.999)
        self.assertEqual(player["equipment"]["hands"], "Cooking gauntlets")
        player["current_cooking"] = "cook_lobster"
        calls = self._review(player, roll=0.999)
        self.assertEqual(calls["xp"], [180.0])
        self.assertEqual(player["equipment"]["hands"], "Brawling gloves (cooking)")
        self.assertEqual(player["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(player["cooking_equipment_swap"], {})

    def test_auto_preserves_manually_worn_gauntlets_without_a_burn_benefit(self):
        player = _gloved_cook()
        player["equipment"]["hands"] = "Cooking gauntlets"
        player["inventory"]["Cooking gauntlets"] = 0
        self._review(player)
        self.assertEqual(player["equipment"]["hands"], "Cooking gauntlets")
        self.assertEqual(player["inventory"]["Cooking gauntlets"], 0)
        self.assertEqual(player["cooking_equipment_swap"], {})


class CookingGauntletDirectActionTests(unittest.TestCase):
    """Picking a target or its policy reconciles gloves before any review."""

    def setUp(self):
        from tests.test_integration_smoke import (
            _DummyCol,
            _DummyMW,
            _install_runtime_fakes,
            _load_addon_as_package,
        )

        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_cooking_glove_direct_actions")
        self.menu = {}
        self.addon.ui.show_main_menu = lambda *_args, **kwargs: self.menu.update(kwargs)
        self.addon.mw = _DummyMW(_DummyCol())
        self.addon.save_player_data = lambda: None
        self.addon.update_review_hud = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon._state.current_skill = "Cooking"

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _hands_after(self, target, level, command, *args):
        self.addon._state.player_data = _gloved_cook(target, level)
        self.addon._on_main_menu()
        self.assertTrue(self.menu[command](target, *args))
        return self.addon._state.player_data["equipment"]["hands"]

    def test_auto_keeps_gloves_when_gauntlets_cannot_reduce_burns(self):
        for command, args in (("on_set_cooking", ()), ("on_set_cooking_equipment_choice", ("auto",))):
            with self.subTest(command=command):
                hands = self._hands_after("cook_lobster", 99, command, *args)
                self.assertEqual(hands, "Brawling gloves (cooking)")
                self.assertEqual(self.addon._state.player_data["cooking_equipment_swap"], {})

    def test_auto_equips_gauntlets_when_they_reduce_burns(self):
        self.assertEqual(self._hands_after("cook_shark", 94, "on_set_cooking"), "Cooking gauntlets")


class CookingGauntletDataTests(unittest.TestCase):
    def test_period_no_burn_thresholds_are_exact(self):
        self.assertEqual(
            {
                target_id: COOKING_DATA[target_id]["cooking_gauntlet_no_burn_level"]
                for target_id in (
                    "cook_tuna",
                    "cook_trout",
                    "cook_lobster",
                    "cook_swordfish",
                    "cook_monkfish",
                    "cook_shark",
                    "cook_cavefish",
                    "cook_rocktail",
                )
            },
            {
                "cook_tuna": 63,
                "cook_trout": 50,
                "cook_lobster": 68,
                "cook_swordfish": 81,
                "cook_monkfish": 87,
                "cook_shark": 94,
                "cook_cavefish": 94,
                "cook_rocktail": 94,
            },
        )

    def test_gauntlets_guarantee_threshold_but_not_the_level_below(self):
        shark = COOKING_DATA["cook_shark"]
        self.assertLess(
            cooking_source_roll_chance_pure(
                93, shark, has_cooking_gauntlets=True
            ),
            1.0,
        )
        self.assertEqual(
            cooking_source_roll_chance_pure(
                94, shark, has_cooking_gauntlets=True
            ),
            1.0,
        )

    def test_gauntlets_never_reduce_an_already_better_ordinary_chance(self):
        trout = COOKING_DATA["cook_trout"]
        self.assertEqual(
            cooking_source_roll_chance_pure(
                49, trout, has_cooking_gauntlets=True
            ),
            cooking_source_roll_chance_pure(49, trout),
        )

    def test_action_uses_the_worn_gauntlet_modifier(self):
        shark = COOKING_DATA["cook_shark"]
        roll = 0.999
        plain, xp, processed, output, burned = apply_cooking_action_pure(
            "cook_shark",
            {"Raw shark": 1},
            COOKING_DATA,
            94,
            roll,
            use_source_probability=True,
        )
        self.assertTrue(processed)
        self.assertTrue(burned)
        self.assertEqual(xp, 0)
        self.assertEqual(output, "Burnt shark")
        self.assertEqual(plain["Burnt shark"], 1)

        protected, xp, processed, output, burned = apply_cooking_action_pure(
            "cook_shark",
            {"Raw shark": 1},
            COOKING_DATA,
            94,
            roll,
            use_source_probability=True,
            has_cooking_gauntlets=True,
        )
        self.assertTrue(processed)
        self.assertFalse(burned)
        self.assertEqual(xp, shark["exp"])
        self.assertEqual(output, "Shark")
        self.assertEqual(protected["Shark"], 1)

    def test_all_family_crest_gauntlets_are_registered_equipment(self):
        for item_name, item_id in (
            ("Cooking gauntlets", 775),
            ("Goldsmith gauntlets", 776),
            ("Chaos gauntlets", 777),
            ("Family gauntlets", 778),
        ):
            self.assertEqual(EQUIPMENT_DATA[item_name].slot, "hands")
            self.assertEqual(EQUIPMENT_DATA[item_name].source_item_id, item_id)
            self.assertEqual(EQUIPMENT_DATA[item_name].bonuses.defence_slash, 9)
            self.assertEqual(EQUIPMENT_DATA[item_name].bonuses.melee_strength, 2)


class CookingGauntletLifecycleTests(unittest.TestCase):
    def _player(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        data["quests"]["family_crest"] = {
            "started": True,
            "progress": 16,
            "completed": True,
        }
        return data

    def test_family_conversion_is_free_and_reenchantment_costs_25000(self):
        data = self._player()
        data["inventory"]["Family gauntlets"] = 1
        converted, ok, _message = apply_family_gauntlet_conversion_pure(
            data, "Family gauntlets"
        )
        self.assertTrue(ok)
        self.assertEqual(converted["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(converted["inventory"]["Coins"], data["inventory"]["Coins"])
        self.assertEqual(converted["family_gauntlet_enchantment"], "cooking")

        data = self._player()
        data["inventory"].update({"Goldsmith gauntlets": 1, "Coins": 25_000})
        converted, ok, _message = apply_family_gauntlet_conversion_pure(
            data, "Goldsmith gauntlets"
        )
        self.assertTrue(ok)
        self.assertEqual(converted["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(converted["inventory"]["Coins"], 0)

    def test_reenchantment_refuses_without_payment(self):
        data = self._player()
        data["inventory"].update({"Chaos gauntlets": 1, "Coins": 24_999})
        unchanged, ok, message = apply_family_gauntlet_conversion_pure(
            data, "Chaos gauntlets"
        )
        self.assertFalse(ok)
        self.assertIn("25,000", message)
        self.assertEqual(unchanged["inventory"]["Chaos gauntlets"], 1)

    def test_lost_pair_is_recovered_in_its_remembered_enchantment(self):
        data = self._player()
        data["family_gauntlet_enchantment"] = "cooking"
        state = family_gauntlet_recovery_state_pure(data)
        self.assertTrue(state["enabled"])
        recovered, ok, _message = recover_family_gauntlets_pure(data)
        self.assertTrue(ok)
        self.assertEqual(recovered["inventory"]["Cooking gauntlets"], 1)

        duplicate, ok, _message = recover_family_gauntlets_pure(recovered)
        self.assertFalse(ok)
        self.assertEqual(duplicate["inventory"]["Cooking gauntlets"], 1)

    def test_target_policy_equips_displaces_and_restores_only_its_own_swap(self):
        data = self._player()
        data["inventory"]["Cooking gauntlets"] = 1
        data["equipment"]["hands"] = "Leather gloves"
        equipped = reconcile_cooking_equipment_pure(
            data, "cook_shark", beneficial=True
        )
        self.assertTrue(cooking_gauntlets_worn_pure(equipped))
        self.assertEqual(equipped["inventory"]["Leather gloves"], 1)
        self.assertEqual(
            equipped["cooking_equipment_swap"]["displaced_item"],
            "Leather gloves",
        )

        restored = reconcile_cooking_equipment_pure(
            equipped, "cook_bass", beneficial=False
        )
        self.assertEqual(restored["equipment"]["hands"], "Leather gloves")
        self.assertEqual(restored["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(restored["cooking_equipment_swap"], {})

    def test_advanced_none_does_not_unequip_manually_worn_gauntlets(self):
        data = self._player()
        data["equipment"]["hands"] = "Cooking gauntlets"
        data, ok = set_cooking_equipment_choice_pure(
            data, "cook_shark", "none"
        )
        self.assertTrue(ok)
        self.assertEqual(cooking_equipment_choice_pure(data, "cook_shark"), "none")
        reconciled = reconcile_cooking_equipment_pure(
            data, "cook_shark", beneficial=True
        )
        self.assertEqual(reconciled["equipment"]["hands"], "Cooking gauntlets")
        self.assertEqual(reconciled["cooking_equipment_swap"], {})

    def test_migration_infers_remembered_enchantment_from_owned_pair(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        data["config_version"] = CURRENT_CONFIG_VERSION - 1
        data.pop("family_gauntlet_enchantment", None)
        data["inventory"]["Goldsmith gauntlets"] = 1
        migrated = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["family_gauntlet_enchantment"], "goldsmith")

    def test_migration_repairs_completed_quest_with_no_surviving_pair(self):
        data = self._player()
        data["config_version"] = CURRENT_CONFIG_VERSION - 1
        data.pop("family_gauntlet_enchantment", None)
        migrated = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["family_gauntlet_enchantment"], "family")
        self.assertTrue(family_gauntlet_recovery_state_pure(migrated)["enabled"])


if __name__ == "__main__":
    unittest.main()
