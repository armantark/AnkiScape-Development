import unittest

import pkg_alias  # noqa: F401

from ankiscape.core.constants import CRAFTING_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from ankiscape.data.combat_data import CONSUMABLE_DATA
from ankiscape.data.potion_data import POTION_FAMILIES
from ankiscape.logic.skilling_boost_logic import (
    advance_skilling_temporary_levels_pure,
    set_skilling_potion_target_enabled_pure,
    skilling_effective_level_pure,
    skilling_target_level_available_pure,
)
from ankiscape.logic_pure.logic_pure import (
    advance_temporary_effects_pure,
    apply_consumable_pure,
    crafting_target_locked_reasons_pure,
)
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    handle_crafting_answer,
    handle_fletching_answer,
    run_answer_with_carried_overlay,
)


def _context(player_data):
    messages = []

    def award(exp_key, xp):
        player_data[exp_key] = float(player_data.get(exp_key, 0) or 0) + xp
        return xp

    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: 0.0,
        show_error_message=lambda title, text: messages.append((title, text)),
        deactivate_current_skill=lambda _reason=None: None,
        award_skill_exp=award,
        award_hidden_skill_exp=lambda exp_key, _level_key, xp: award(exp_key, xp),
        level_up_check=lambda *_args: None,
        check_achievements=lambda *_args: None,
        save_player_data=lambda: None,
        refresh_skill_availability=lambda: None,
        show_exp=lambda *_args: None,
        show_activity_gain=messages.append,
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda *_args: None,
    ), messages


class SkillingBoostLogicTest(unittest.TestCase):
    def test_period_container_ids_do_not_collide(self):
        self.assertEqual(
            POTION_FAMILIES["Crafting potion"]["doses"],
            {1: 14844, 2: 14842, 3: 14840, 4: 14838},
        )
        self.assertEqual(
            POTION_FAMILIES["Fletching potion"]["flask_doses"],
            {1: 23481, 2: 23479, 3: 23477, 4: 23475, 5: 23473, 6: 23471},
        )
        ids = []
        for spec in POTION_FAMILIES.values():
            ids.extend(spec.get("doses", {}).values())
            ids.extend(spec.get("flask_doses", {}).values())
        self.assertEqual(len(ids), len(set(ids)))

    def test_manual_drink_applies_exact_plus_three_and_replaces_dose(self):
        updated, result = apply_consumable_pure(
            {
                "crafting_level": 50,
                "inventory": {"Crafting potion (3)": 1},
            },
            "Crafting potion (3)",
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(result["boosts"], {"crafting": 3})
        self.assertEqual(skilling_effective_level_pure(updated, "crafting"), 53)
        self.assertEqual(updated["inventory"], {"Crafting potion (2)": 1})

    def test_review_clock_restores_one_level_per_hundred_ticks(self):
        boosted = {
            "crafting_level": 50,
            "skilling_current_levels": {"crafting": 53},
            "skilling_level_decay_ticks": 0,
        }
        halfway = advance_temporary_effects_pure(boosted, 50)
        self.assertEqual(skilling_effective_level_pure(halfway, "crafting"), 53)
        self.assertEqual(halfway["skilling_level_decay_ticks"], 50)
        restored = advance_temporary_effects_pure(halfway, 50)
        self.assertEqual(skilling_effective_level_pure(restored, "crafting"), 52)
        self.assertEqual(restored["skilling_level_decay_ticks"], 0)

    def test_target_policy_unlocks_only_the_sourced_three_level_window(self):
        target = "form_clay_ring_unfired"
        player = {
            "crafting_level": 1,
            "inventory": {"Soft clay": 1, "Crafting potion (3)": 1},
        }
        self.assertIn(
            "level 4",
            crafting_target_locked_reasons_pure(player, target, CRAFTING_DATA),
        )
        enabled, ok = set_skilling_potion_target_enabled_pure(
            player, "crafting", target, True
        )
        self.assertTrue(ok)
        self.assertNotIn(
            "level 4",
            crafting_target_locked_reasons_pure(enabled, target, CRAFTING_DATA),
        )
        self.assertFalse(
            skilling_target_level_available_pure(
                enabled, "crafting", target, 5
            )
        )

    def test_carried_overlay_keeps_lower_dose_in_pack_and_redoses_on_decay(self):
        target = "form_clay_ring_unfired"
        player = {
            "crafting_level": 1,
            "crafting_exp": 0.0,
            "current_craft": target,
            "inventory": {
                "Soft clay": 6,
                "Ring mould": 1,
                "Crafting potion (3)": 1,
            },
            "skilling_potion_targets": {"crafting": {target: True}},
            "carried_inventory": {},
            "carried_layout": {},
            "carried_churn": {},
            "carried_advanced_targets": {},
            "carried_primed_targets": {},
            "skilling_bank_run": {},
            "equipment": {},
        }
        ctx, messages = _context(player)
        self.assertTrue(
            run_answer_with_carried_overlay(
                ctx, "crafting", handle_crafting_answer
            )
        )
        self.assertEqual(skilling_effective_level_pure(player, "crafting"), 4)
        self.assertEqual(player["inventory"].get("Crafting potion (2)"), 1)
        self.assertEqual(
            player["carried_inventory"][target].get("Crafting potion (2)"), 1
        )
        self.assertTrue(any("Drank Crafting potion (3)" in str(m) for m in messages))

        player.update(advance_skilling_temporary_levels_pure(player, 50))
        self.assertTrue(
            run_answer_with_carried_overlay(
                ctx, "crafting", handle_crafting_answer
            )
        )
        self.assertEqual(player["inventory"].get("Crafting potion (2)"), 1)

        player.update(advance_skilling_temporary_levels_pure(player, 50))
        self.assertTrue(
            run_answer_with_carried_overlay(
                ctx, "crafting", handle_crafting_answer
            )
        )
        self.assertEqual(player["inventory"].get("Crafting potion (1)"), 1)
        self.assertEqual(
            player["carried_inventory"][target].get("Crafting potion (1)"), 1
        )

    def test_auto_drink_preserves_spare_carried_bottles(self):
        cases = (
            ("crafting", "current_craft", "form_clay_ring_unfired", 1,
             {"Soft clay": 6, "Ring mould": 1}, "Clay ring (unfired)", handle_crafting_answer),
            ("fletching", "current_fletch", "shortbow_u", 2,
             {"Logs": 6}, "Shortbow (u)", handle_fletching_answer),
        )
        for skill, target_key, target, level, materials, output, handler in cases:
            for doses in (3, 1):
                with self.subTest(skill=skill, doses=doses):
                    potion = f"{skill.title()} potion ({doses})"
                    leaves = f"{skill.title()} potion (2)" if doses == 3 else "Vial"
                    packed = {**materials, potion: 2}
                    player = {
                        f"{skill}_level": level,
                        target_key: target,
                        "inventory": dict(packed),
                        "skilling_potion_targets": {skill: {target: True}},
                        "carried_inventory": {target: dict(packed)},
                        "carried_layout": {target: dict(packed)},
                        "carried_advanced_targets": {target: True},
                        "carried_primed_targets": {target: True},
                    }
                    ctx, _messages = _context(player)

                    self.assertTrue(run_answer_with_carried_overlay(ctx, skill, handler))

                    self.assertEqual(player["inventory"].get(output), 1)
                    self.assertEqual(skilling_effective_level_pure(player, skill), level + 3)
                    self.assertEqual(player["inventory"].get(potion), 1)
                    self.assertEqual(player["inventory"].get(leaves), 1)
                    carried = player["carried_inventory"][target]
                    self.assertEqual(carried.get(potion, 0), 1)
                    self.assertEqual(carried.get(leaves), 1)

    def test_pack_without_its_potion_restocks_it_from_the_bank_before_crafting(self):
        target = "form_clay_ring_unfired"
        player = {
            "crafting_level": 1,
            "crafting_exp": 0.0,
            "current_craft": target,
            "inventory": {
                "Soft clay": 6,
                "Ring mould": 1,
                "Crafting potion (3)": 1,
            },
            "skilling_potion_targets": {"crafting": {target: True}},
            "carried_inventory": {target: {"Soft clay": 6}},
            "carried_layout": {},
            "carried_churn": {},
            "carried_advanced_targets": {},
            "carried_primed_targets": {target: True},
            "skilling_bank_run": {},
            "equipment": {},
        }
        ctx, _messages = _context(player)

        self.assertTrue(
            run_answer_with_carried_overlay(
                ctx, "crafting", handle_crafting_answer
            )
        )
        self.assertEqual(player["inventory"].get("Clay ring (unfired)"), 1)
        self.assertEqual(player["inventory"].get("Crafting potion (2)"), 1)
        self.assertEqual(
            player["carried_inventory"][target].get("Crafting potion (2)"), 1
        )

    def test_missing_materials_do_not_waste_a_configured_potion_dose(self):
        target = "form_clay_ring_unfired"
        player = {
            "crafting_level": 1,
            "crafting_exp": 0.0,
            "current_craft": target,
            "inventory": {"Crafting potion (3)": 1},
            "skilling_potion_targets": {"crafting": {target: True}},
        }
        ctx, _messages = _context(player)

        self.assertFalse(handle_crafting_answer(ctx))
        self.assertEqual(player["inventory"], {"Crafting potion (3)": 1})
        self.assertEqual(skilling_effective_level_pure(player, "crafting"), 1)

    def test_advanced_layout_cannot_drink_a_banked_potion_it_does_not_carry(self):
        target = "form_clay_ring_unfired"
        player = {
            "crafting_level": 1,
            "crafting_exp": 0.0,
            "current_craft": target,
            "inventory": {
                "Soft clay": 6,
                "Ring mould": 1,
                "Crafting potion (3)": 1,
            },
            "skilling_potion_targets": {"crafting": {target: True}},
            "carried_inventory": {},
            "carried_layout": {
                target: {"Soft clay": 6, "Ring mould": 1}
            },
            "carried_churn": {},
            "carried_advanced_targets": {target: True},
            "carried_primed_targets": {},
            "skilling_bank_run": {},
            "equipment": {},
        }
        ctx, _messages = _context(player)

        self.assertFalse(
            run_answer_with_carried_overlay(
                ctx, "crafting", handle_crafting_answer
            )
        )
        self.assertEqual(player["inventory"].get("Crafting potion (3)"), 1)
        self.assertEqual(skilling_effective_level_pure(player, "crafting"), 1)

    def test_advanced_target_stays_locked_until_layout_carries_the_potion(self):
        target = "form_clay_ring_unfired"
        player = {
            "crafting_level": 1,
            "inventory": {
                "Soft clay": 6,
                "Ring mould": 1,
                "Crafting potion (3)": 1,
            },
            "skilling_potion_targets": {"crafting": {target: True}},
            "carried_advanced_targets": {target: True},
            "carried_layout": {target: {"Soft clay": 6, "Ring mould": 1}},
        }
        self.assertFalse(
            skilling_target_level_available_pure(
                player, "crafting", target, 4
            )
        )
        player["carried_layout"][target]["Crafting potion (3)"] = 1
        self.assertTrue(
            skilling_target_level_available_pure(
                player, "crafting", target, 4
            )
        )

    def test_storage_migration_sanitizes_temporary_levels_and_policies(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 112,
                "crafting_level": 50,
                "skilling_current_levels": {
                    "crafting": 53,
                    "bogus": 99,
                },
                "skilling_level_decay_ticks": 150,
                "skilling_potion_targets": {
                    "crafting": {"form_clay_ring_unfired": 1},
                    "bogus": {"x": True},
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["skilling_current_levels"], {"crafting": 53})
        self.assertEqual(migrated["skilling_level_decay_ticks"], 99)
        self.assertEqual(
            migrated["skilling_potion_targets"],
            {"crafting": {"form_clay_ring_unfired": True}},
        )

    def test_every_new_skilling_container_is_bank_drinkable(self):
        for item_name in (
            "Crafting potion (1)",
            "Crafting flask (6)",
            "Fletching potion (1)",
            "Fletching flask (6)",
        ):
            self.assertIn(item_name, CONSUMABLE_DATA)
            self.assertEqual(CONSUMABLE_DATA[item_name]["strategy"], "flat_skill")


if __name__ == "__main__":
    unittest.main()
