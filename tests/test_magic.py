import json
import os
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.core.constants import (
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    MAGIC_DATA,
    MAGIC_ITEM_IMAGES,
    MAGIC_SPELL_IMAGES,
    ORE_DATA,
)
from ankiscape.logic_pure.logic_pure import (
    MAGIC_CHARGE_DURATION_TICKS,
    MAGE_ARENA_GOD_DATA,
    apply_mage_arena_cape_action_pure,
    apply_magic_action_pure,
    apply_mage_arena_step_pure,
    attune_mage_arena_spell_pure,
    advance_temporary_effects_pure,
    can_equip_item_pure,
    charged_god_spell_max_hit_bonus_pure,
    combat_target_preview_pure,
    combat_magic_preset_locked_reasons_pure,
    default_combat_state_pure,
    effective_magic_rune_cost_pure,
    equip_item_pure,
    magic_target_locked_reasons_pure,
    save_combat_preset_pure,
    set_mage_arena_alignment_pure,
    set_combat_pack_mode_pure,
)
from ankiscape.logic.farming_logic import default_farming_state_pure, execute_farm_field_step_pure, set_farm_plan_pure
from ankiscape.data.magic_data import CHARGE_WIKI, COMBAT_MAGIC_ADDITIONS, MAGIC_TARGETS
from ankiscape.data.livid_farm_data import (
    ARCANE_CAPACITOR_CHARGED,
    ARCANE_CAPACITOR_UNCHARGED,
)
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    answer_handler_for_key,
    handle_magic_answer,
    handle_utility_answer,
)
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from ankiscape.core.target_metadata import magic_target_rows


def _quest_state(*completed):
    return {quest: {"completed": True} for quest in completed}


def _context(player_data, calls):
    def award(exp_key, xp):
        player_data[exp_key] = float(player_data.get(exp_key, 0) or 0) + xp
        return xp

    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: 0.0,
        show_error_message=lambda title, text: calls["errors"].append((title, text)),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=award,
        award_hidden_skill_exp=lambda exp_key, _level_key, xp: award(exp_key, xp),
        level_up_check=lambda *_args: None,
        check_achievements=lambda *_args: None,
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: None,
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda xp: calls["shown_xp"].append(xp),
        show_activity_gain=lambda text: calls.setdefault("activity", []).append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda *_args: None,
    )


class MagicDataAndMechanicsTest(unittest.TestCase):
    def test_charge_source_pin_is_the_spell_not_the_unrelated_prayer_page(self):
        self.assertEqual(
            CHARGE_WIKI,
            "RuneScape Wiki Charge (spell) oldid=6593039 (2012-11-20)",
        )

    def test_charge_uses_review_driven_ticks_and_expires_cleanly(self):
        advanced = advance_temporary_effects_pure(
            {
                "magic_charge_active": True,
                "magic_charge_ticks_remaining": MAGIC_CHARGE_DURATION_TICKS,
            },
            action_ticks=2,
        )
        self.assertEqual(
            advanced["magic_charge_ticks_remaining"],
            MAGIC_CHARGE_DURATION_TICKS - 100,
        )
        self.assertTrue(advanced["magic_charge_active"])

        expired = advance_temporary_effects_pure(
            {
                "magic_charge_active": True,
                "magic_charge_ticks_remaining": 50,
            },
            action_ticks=1,
        )
        self.assertEqual(expired["magic_charge_ticks_remaining"], 0)
        self.assertFalse(expired["magic_charge_active"])

    def test_casting_charge_installs_a_fresh_full_duration(self):
        data = {
            "magic_level": 99,
            "mage_arena": {"completed": True},
            "inventory": {"Air rune": 3, "Fire rune": 3, "Blood rune": 3},
            "magic_charge_active": True,
            "magic_charge_ticks_remaining": 50,
        }

        result, _xp, _secondary, _outputs, ok, _message = apply_magic_action_pure(
            data, "charge", MAGIC_DATA, {}
        )

        self.assertTrue(ok)
        self.assertTrue(result["magic_charge_active"])
        self.assertEqual(
            result["magic_charge_ticks_remaining"],
            MAGIC_CHARGE_DURATION_TICKS,
        )

    def test_dragonstone_enchants_consume_the_exact_crafting_output_names(self):
        expected = {
            "enchant_dragonstone_ring": "Dragonstone ring",
            "enchant_dragonstone_necklace": "Dragon necklace",
            "enchant_dragonstone_amulet": "Dragonstone ammy",
            "enchant_dragonstone_bracelet": "Dragon bracelet",
        }
        for target_id, item_name in expected.items():
            with self.subTest(target_id=target_id):
                self.assertEqual(MAGIC_DATA[target_id]["requirements"], {item_name: 1})

    def test_digsite_pendant_enchant_requires_the_museum_discovery(self):
        runes = {"Cosmic rune": 1, "Fire rune": 5}
        player = {
            "magic_level": 99,
            "inventory": {**runes, "Ruby necklace": 1},
        }
        reason = "Learn Digsite-pendant enchanting at Varrock Museum"
        self.assertIn(
            reason,
            magic_target_locked_reasons_pure(
                player, "enchant_ruby_necklace", MAGIC_DATA, {}
            ),
        )
        player["varrock_museum"] = {"digsite_pendant_unlocked": True}
        self.assertEqual(
            magic_target_locked_reasons_pure(
                player, "enchant_ruby_necklace", MAGIC_DATA, {}
            ),
            (),
        )

    def test_enchant_amulet_requires_the_strung_item_identity(self):
        runes = {"Cosmic rune": 1, "Water rune": 1}
        unstrung = {
            "magic_level": 99,
            "inventory": {**runes, "Sapphire amulet (u)": 1},
        }
        self.assertIn(
            "Sapphire amulet x1",
            magic_target_locked_reasons_pure(
                unstrung, "enchant_sapphire_amulet", MAGIC_DATA, {}
            ),
        )
        strung = {
            "magic_level": 99,
            "inventory": {**runes, "Sapphire amulet": 1},
        }
        self.assertEqual(
            magic_target_locked_reasons_pure(
                strung, "enchant_sapphire_amulet", MAGIC_DATA, {}
            ),
            (),
        )

    def test_three_books_and_stable_ids_are_complete(self):
        self.assertEqual(len(MAGIC_TARGETS), 114)
        self.assertEqual(len(MAGIC_TARGETS), len(set(MAGIC_TARGETS)))
        books = {row["spellbook"] for row in MAGIC_TARGETS.values()}
        self.assertEqual(books, {"standard", "ancient", "lunar"})
        ancient_combat = [spell for spell in COMBAT_MAGIC_ADDITIONS if spell.spellbook == "ancient"]
        self.assertEqual(len(ancient_combat), 20)
        self.assertEqual({spell.id for spell in ancient_combat if spell.id.startswith("miasmic_")}, {
            "miasmic_rush", "miasmic_burst", "miasmic_blitz", "miasmic_barrage",
        })

    def test_borrowed_power_noncombat_rows_reuse_native_actions(self):
        expected = {
            "borrowed_telegrab_wine_of_zamorak": "produce",
            "borrowed_teleport_to_house": "pure",
            "borrowed_high_alchemy": "alchemy",
            "borrowed_bones_to_peaches": "bones_conversion",
        }
        for target_id, action in expected.items():
            with self.subTest(target_id=target_id):
                spec = MAGIC_TARGETS[target_id]
                self.assertEqual(spec["level"], 99)
                self.assertEqual(spec["spellbook"], "lunar")
                self.assertEqual(spec["group"], "Borrowed Power")
                self.assertEqual(spec["rune_cost"], {"Astral rune": 3})
                self.assertEqual(spec["action"], action)

    def test_borrowed_high_alchemy_uses_native_value_and_one_capacitor_charge(self):
        player = {
            "magic_level": 99,
            "magic_alchemy_item": "Logs",
            "inventory": {"Astral rune": 3, "Logs": 1},
            "equipment": {"neck": ARCANE_CAPACITOR_CHARGED},
            "quests": {"lunar_diplomacy": {"completed": True}},
            "livid_farm": {
                "borrowed_power_claimed": True,
                "arcane_capacitor_spell": "high_alchemy",
                "arcane_capacitor_charges": 2,
            },
        }

        result, xp, _secondary, outputs, ok, _message = (
            apply_magic_action_pure(
                player,
                "borrowed_high_alchemy",
                MAGIC_DATA,
                {"Logs": 100},
            )
        )

        self.assertTrue(ok)
        self.assertEqual(xp, 65.0)
        self.assertEqual(outputs, {"Coins": 60})
        self.assertEqual(result["inventory"]["Astral rune"], 0)
        self.assertEqual(result["inventory"]["Logs"], 0)
        self.assertEqual(
            result["livid_farm"]["arcane_capacitor_charges"],
            1,
        )
        self.assertEqual(
            result["equipment"]["neck"],
            ARCANE_CAPACITOR_CHARGED,
        )

    def test_borrowed_power_requires_matching_equipped_capacitor(self):
        player = {
            "magic_level": 99,
            "magic_alchemy_item": "Logs",
            "inventory": {"Astral rune": 3, "Logs": 1},
            "equipment": {},
            "quests": {"lunar_diplomacy": {"completed": True}},
            "livid_farm": {
                "borrowed_power_claimed": True,
                "arcane_capacitor_spell": "teleport_to_house",
                "arcane_capacitor_charges": 1_000,
            },
        }

        reasons = magic_target_locked_reasons_pure(
            player,
            "borrowed_high_alchemy",
            MAGIC_DATA,
            {"Logs": 100},
        )

        self.assertIn("Equip the charged Arcane capacitor", reasons)
        self.assertIn("Charge the capacitor with this spell", reasons)

    def test_arcane_capacitor_equipment_rows_preserve_period_stats(self):
        uncharged = EQUIPMENT_DATA[ARCANE_CAPACITOR_UNCHARGED]
        charged = EQUIPMENT_DATA[ARCANE_CAPACITOR_CHARGED]

        self.assertEqual(uncharged.slot, "neck")
        self.assertEqual(uncharged.bonuses.attack_magic, 0)
        self.assertEqual(charged.slot, "neck")
        self.assertEqual(charged.bonuses.attack_magic, 10)
        self.assertEqual(charged.source_item_id, 21514)

    def test_livid_spell_rows_pin_exact_period_levels_xp_and_runes(self):
        expected = {
            "south_falador_teleport": (72, 70, {"Astral rune": 2, "Law rune": 1, "Air rune": 2}),
            "repair_rune_pouch": (75, 75, {"Astral rune": 2, "Law rune": 1, "Cosmic rune": 1}),
            "north_ardougne_teleport": (76, 76, {"Astral rune": 2, "Law rune": 1, "Water rune": 5}),
            "remote_farm": (78, 79, {"Astral rune": 2, "Earth rune": 2, "Nature rune": 3}),
            "spiritualise_food": (80, 81, {"Astral rune": 2, "Cosmic rune": 3, "Body rune": 5}),
            "make_soft_leather": (83, 87, {"Astral rune": 2, "Fire rune": 2, "Body rune": 2}),
            "disruption_shield": (90, 97, {"Astral rune": 3, "Blood rune": 3, "Body rune": 10}),
            "vengeance_group": (95, 120, {"Astral rune": 4, "Death rune": 3, "Earth rune": 11}),
            "teleport_to_trollheim": (92, 101, {"Astral rune": 3, "Law rune": 3, "Water rune": 10}),
            "group_teleport_to_trollheim": (93, 102, {"Astral rune": 3, "Law rune": 3, "Water rune": 20}),
        }
        for target_id, (level, xp, runes) in expected.items():
            with self.subTest(target_id=target_id):
                spec = MAGIC_TARGETS[target_id]
                self.assertEqual((spec["level"], spec["exp"]), (level, float(xp)))
                self.assertEqual(spec["rune_cost"], runes)
                expected_unlock = (
                    "make_leather"
                    if target_id == "make_soft_leather"
                    else target_id
                )
                self.assertEqual(spec["livid_unlock"], expected_unlock)

    def test_make_leather_exposes_every_supported_period_output(self):
        expected = {
            "make_soft_leather": ("Cowhide", "Leather"),
            "make_hard_leather": ("Cowhide", "Hard leather"),
            "make_snakeskin": ("Snake hide", "Snakeskin"),
            "make_green_dragon_leather": (
                "Green dragonhide",
                "Green dragon leather",
            ),
            "make_blue_dragon_leather": (
                "Blue dragonhide",
                "Blue dragon leather",
            ),
            "make_red_dragon_leather": (
                "Red dragonhide",
                "Red dragon leather",
            ),
            "make_black_dragon_leather": (
                "Black dragonhide",
                "Black dragon leather",
            ),
        }
        for target_id, pair in expected.items():
            with self.subTest(target_id=target_id):
                spec = MAGIC_TARGETS[target_id]
                self.assertEqual(
                    (spec["leather_input"], spec["leather_output"]),
                    pair,
                )
                self.assertEqual(spec["livid_unlock"], "make_leather")
        self.assertNotIn("make_royal_dragon_leather", MAGIC_TARGETS)

    def test_livid_unlock_gate_and_unavailable_consumers_are_explicit(self):
        base = {
            "magic_level": 99,
            "quests": _quest_state(
                "lunar_diplomacy",
                "dream_mentor",
                "my_arms_big_adventure",
            ),
            "inventory": {
                "Astral rune": 100,
                "Law rune": 100,
                "Cosmic rune": 100,
                "Body rune": 100,
                "Blood rune": 100,
                "Death rune": 100,
                "Earth rune": 100,
                "Water rune": 100,
            },
        }
        self.assertIn(
            "Unlock at Livid Farm",
            magic_target_locked_reasons_pure(
                base,
                "south_falador_teleport",
                MAGIC_DATA,
                {},
            ),
        )
        for target_id in (
            "repair_rune_pouch",
            "spiritualise_food",
            "disruption_shield",
            "vengeance_group",
            "group_teleport_to_trollheim",
        ):
            with self.subTest(target_id=target_id):
                player = {
                    **base,
                    "livid_farm": {"unlocked_spells": [target_id]},
                }
                reason = MAGIC_DATA[target_id]["consumer_unavailable"]
                self.assertIn(
                    reason,
                    magic_target_locked_reasons_pure(
                        player,
                        target_id,
                        MAGIC_DATA,
                        {},
                    ),
                )
                unchanged, xp, secondary, outputs, ok, _ = apply_magic_action_pure(
                    player,
                    target_id,
                    MAGIC_DATA,
                    {},
                )
                self.assertFalse(ok)
                self.assertEqual((xp, secondary, outputs), (0.0, {}, {}))
                self.assertEqual(unchanged, player)

    def test_source_ready_livid_spells_use_existing_skill_substrates(self):
        quests = _quest_state(
            "lunar_diplomacy",
            "dream_mentor",
            "my_arms_big_adventure",
        )
        unlocked = [
            "south_falador_teleport",
            "north_ardougne_teleport",
            "remote_farm",
            "make_leather",
            "teleport_to_trollheim",
        ]
        teleports = {
            "south_falador_teleport": "South Falador gate",
            "north_ardougne_teleport": "North of East Ardougne bank",
        }
        for target_id, destination in teleports.items():
            spec = MAGIC_DATA[target_id]
            player = {
                "magic_level": 99,
                "quests": quests,
                "livid_farm": {"unlocked_spells": unlocked},
                "inventory": dict(spec["rune_cost"]),
            }
            result, xp, _secondary, _outputs, ok, _ = apply_magic_action_pure(
                player,
                target_id,
                MAGIC_DATA,
                {},
            )
            self.assertTrue(ok)
            self.assertEqual(xp, spec["exp"])
            self.assertEqual(result["magic_last_teleport"]["destination"], destination)

        farm = {
            "magic_level": 99,
            "quests": quests,
            "livid_farm": {"unlocked_spells": unlocked},
            "inventory": {
                "Astral rune": 2,
                "Earth rune": 2,
                "Nature rune": 3,
            },
        }
        farm.update(default_farming_state_pure())
        farm["farm_patches"]["falador_allotment_north"].update(
            {"crop_id": "potato", "last_crop_id": "potato", "diseased": True}
        )
        farm["farm_patches"]["falador_allotment_south"].update(
            {"crop_id": "potato", "last_crop_id": "potato", "diseased": True}
        )
        remote, xp, _secondary, _outputs, ok, _ = apply_magic_action_pure(
            farm,
            "remote_farm",
            MAGIC_DATA,
            {},
        )
        self.assertTrue(ok)
        self.assertEqual(xp, 79.0)
        self.assertEqual(remote["magic_last_remote_farm"]["cured_count"], 2)
        self.assertFalse(
            remote["farm_patches"]["falador_allotment_north"]["diseased"]
        )
        self.assertFalse(
            remote["farm_patches"]["falador_allotment_south"]["diseased"]
        )

        leather = {
            "magic_level": 99,
            "quests": quests,
            "livid_farm": {"unlocked_spells": unlocked},
            "inventory": {
                "Astral rune": 2,
                "Fire rune": 2,
                "Body rune": 2,
                "Black dragonhide": 7,
            },
        }
        tanned, xp, _secondary, outputs, ok, _ = apply_magic_action_pure(
            leather,
            "make_black_dragon_leather",
            MAGIC_DATA,
            {},
        )
        self.assertTrue(ok)
        self.assertEqual(xp, 87.0)
        self.assertEqual(outputs, {"Black dragon leather": 5})
        self.assertEqual(tanned["inventory"]["Black dragonhide"], 2)

        trollheim_spec = MAGIC_DATA["teleport_to_trollheim"]
        trollheim = {
            "magic_level": 99,
            "quests": quests,
            "livid_farm": {"unlocked_spells": unlocked},
            "inventory": dict(trollheim_spec["rune_cost"]),
        }
        focused, xp, _secondary, _outputs, ok, _ = apply_magic_action_pure(
            trollheim,
            "teleport_to_trollheim",
            MAGIC_DATA,
            {},
        )
        self.assertTrue(ok)
        self.assertEqual(xp, 101.0)
        self.assertEqual(focused["farming_spell_patch"], "trollheim_herb")
        self.assertEqual(
            focused["magic_last_teleport"]["destination"],
            "Troll Stronghold herb patch",
        )

    def test_elemental_staff_waives_only_covered_runes(self):
        cost = effective_magic_rune_cost_pure(
            {"inventory": {"Staff of fire": 1}},
            {"Fire rune": 5, "Air rune": 3, "Nature rune": 1},
        )
        self.assertEqual(cost, {"Air rune": 3, "Nature rune": 1})

    def test_high_alchemy_consumes_item_and_uses_cache_fraction(self):
        data = {
            "magic_level": 99,
            "inventory": {"Nature rune": 1, "Fire rune": 5, "Rune platebody": 1},
            "magic_alchemy_item": "Rune platebody",
        }
        result, xp, secondary, outputs, ok, _message = apply_magic_action_pure(
            data, "high_alchemy", MAGIC_DATA, {"Rune platebody": 64000}
        )
        self.assertTrue(ok)
        self.assertEqual(xp, 65)
        self.assertEqual(secondary, {})
        self.assertEqual(outputs, {"Coins": 38400})
        self.assertEqual(result["inventory"]["Rune platebody"], 0)

    def test_superheat_requires_smithing_level_and_awards_both_xp_types(self):
        data = {"magic_level": 99, "smithing_level": 69, "inventory": {"Nature rune": 1, "Fire rune": 4, "Adamantite ore": 1, "Coal": 6}}
        self.assertIn("Smithing level 70", magic_target_locked_reasons_pure(data, "superheat_adamant_bar", MAGIC_DATA, {}))
        data["smithing_level"] = 70
        result, xp, secondary, outputs, ok, _ = apply_magic_action_pure(data, "superheat_adamant_bar", MAGIC_DATA, {})
        self.assertTrue(ok)
        self.assertEqual((xp, secondary, outputs), (53.0, {"smithing": 37.5}, {"Adamant bar": 1}))
        self.assertEqual(result["inventory"]["Coal"], 0)

    def test_lunar_batch_and_single_item_semantics(self):
        base = {"magic_level": 99, "quests": _quest_state("lunar_diplomacy"), "inventory": {"Astral rune": 10, "Fire rune": 50, "Water rune": 50, "Uncooked apple pie": 3}}
        baked, _xp, secondary, outputs, ok, _ = apply_magic_action_pure(base, "bake_pie", MAGIC_DATA, {})
        self.assertTrue(ok)
        self.assertEqual(baked["inventory"]["Uncooked apple pie"], 2)
        self.assertEqual((secondary, outputs), ({"cooking": 130.0}, {"Apple pie": 1}))

        humid = {"magic_level": 99, "quests": _quest_state("lunar_diplomacy", "dream_mentor"), "inventory": {"Astral rune": 1, "Fire rune": 1, "Water rune": 3, "Bucket": 2, "Jug": 3}}
        filled, _xp, _secondary, outputs, ok, _ = apply_magic_action_pure(humid, "humidify", MAGIC_DATA, {})
        self.assertTrue(ok)
        self.assertEqual(outputs, {"Bucket of water": 2, "Jug of water": 3})
        self.assertEqual(filled["inventory"]["Bucket"], 0)

        glass_data = {
            "magic_level": 99,
            "quests": _quest_state("lunar_diplomacy"),
            "inventory": {
                "Astral rune": 2, "Air rune": 10, "Fire rune": 6,
                "Bucket of sand": 3, "Seaweed": 3,
            },
        }
        rolls = iter((0.10, 0.29, 0.30))
        glass, _xp, secondary, outputs, ok, _ = apply_magic_action_pure(
            glass_data, "superglass_make", MAGIC_DATA, {}, lambda: next(rolls)
        )
        self.assertTrue(ok)
        self.assertEqual(outputs, {"Molten glass": 5})
        self.assertEqual(secondary, {"crafting": 30.0})
        self.assertEqual(glass["inventory"]["Bucket of sand"], 0)
        self.assertNotIn("Bucket", outputs)

        string_data = {
            "magic_level": 99,
            "quests": _quest_state("lunar_diplomacy"),
            "inventory": {
                "Astral rune": 4,
                "Earth rune": 20,
                "Water rune": 10,
                "Gold amulet (u)": 2,
                "Sapphire amulet (u)": 1,
            },
        }
        strung, _xp, secondary, outputs, ok, _ = apply_magic_action_pure(
            string_data, "string_jewellery", MAGIC_DATA, {}
        )
        self.assertTrue(ok)
        self.assertEqual(secondary, {"crafting": 12.0})
        self.assertEqual(outputs, {"Gold amulet": 2, "Sapphire amulet": 1})
        self.assertEqual(strung["inventory"]["Gold amulet (u)"], 0)
        self.assertEqual(strung["inventory"]["Sapphire amulet (u)"], 0)
        unchanged, xp, secondary, outputs, ok, _ = apply_magic_action_pure(
            strung, "string_jewellery", MAGIC_DATA, {}
        )
        self.assertFalse(ok)
        self.assertEqual((xp, secondary, outputs), (0.0, {}, {}))
        self.assertEqual(unchanged, strung)

    def test_farming_spells_validate_before_spending_and_apply_atomically(self):
        base = {
            "magic_level": 99,
            "quests": _quest_state("lunar_diplomacy"),
            "inventory": {
                "Astral rune": 4,
                "Earth rune": 23,
                "Nature rune": 2,
                "Rake": 1,
                "Seed dibber": 1,
                "Potato seed": 6,
            },
        }
        base.update(default_farming_state_pure())
        original_runes = {key: base["inventory"][key] for key in ("Astral rune", "Earth rune", "Nature rune")}
        unchanged, xp, _secondary, _outputs, ok, _ = apply_magic_action_pure(base, "cure_plant", MAGIC_DATA, {})
        self.assertFalse(ok)
        self.assertEqual(xp, 0.0)
        self.assertEqual({key: unchanged["inventory"][key] for key in original_runes}, original_runes)

        planted, planted_ok, _ = execute_farm_field_step_pure(
            base,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(planted_ok)
        planted["farm_patches"]["falador_allotment_north"]["diseased"] = True
        planted["farming_spell_patch"] = "falador_allotment_north"
        cured, xp, _secondary, _outputs, ok, _ = apply_magic_action_pure(planted, "cure_plant", MAGIC_DATA, {})
        self.assertTrue(ok)
        self.assertEqual(xp, 60.0)
        self.assertFalse(cured["farm_patches"]["falador_allotment_north"]["diseased"])
        self.assertEqual(cured["inventory"]["Astral rune"], 3)
        self.assertEqual(cured["inventory"]["Earth rune"], 15)

        planned, plan_ok, _ = set_farm_plan_pure(cured, "falador_allotment_south", "potato")
        self.assertTrue(plan_ok)
        planned["farming_spell_patch"] = "falador_allotment_south"
        fertile, xp, _secondary, _outputs, ok, _ = apply_magic_action_pure(planned, "fertile_soil", MAGIC_DATA, {})
        self.assertTrue(ok)
        self.assertEqual(xp, 87.0)
        plan = fertile["farm_plans"]["falador_allotment_south"]
        self.assertEqual(plan["compost_tier"], "supercompost")
        self.assertTrue(plan["fertile_soil_applied"])
        self.assertEqual(fertile["inventory"]["Astral rune"], 0)
        self.assertEqual(fertile["inventory"]["Nature rune"], 0)
        self.assertEqual(fertile["inventory"]["Earth rune"], 0)

        planted_fertile, planted_ok, _ = execute_farm_field_step_pure(
            fertile,
            {"kind": "plant", "patch_id": "falador_allotment_south", "crop_id": "potato"},
        )
        self.assertTrue(planted_ok)
        self.assertEqual(planted_fertile["farm_patches"]["falador_allotment_south"]["compost_tier"], "supercompost")
        self.assertFalse(planted_fertile["farm_plans"]["falador_allotment_south"]["fertile_soil_applied"])

    def test_more_planks_wish_adds_one_extra_output_only_on_its_roll(self):
        base = {
            "magic_level": 99,
            "quests": _quest_state("dream_mentor"),
            "inventory": {
                "Astral rune": 4,
                "Nature rune": 2,
                "Earth rune": 30,
                "Coins": 140,
                "Logs": 2,
            },
            "livid_farm": {"more_planks_active_this_review": True},
        }

        doubled, _xp, _secondary, outputs, ok, _ = apply_magic_action_pure(
            base,
            "plank_make_logs",
            MAGIC_DATA,
            {},
            random_random=lambda: 0.099,
        )
        self.assertTrue(ok)
        self.assertEqual(outputs, {"Plank": 2})
        self.assertEqual(doubled["inventory"]["Plank"], 2)

        ordinary, _xp, _secondary, outputs, ok, _ = apply_magic_action_pure(
            base,
            "plank_make_logs",
            MAGIC_DATA,
            {},
            random_random=lambda: 0.10,
        )
        self.assertTrue(ok)
        self.assertEqual(outputs, {"Plank": 1})
        self.assertEqual(ordinary["inventory"]["Plank"], 1)

    def test_quest_gate_and_disabled_metadata_row_block_selection(self):
        player = {"magic_level": 99, "inventory": {"Law rune": 2, "Blood rune": 1}}
        reasons = magic_target_locked_reasons_pure(player, "kharyrll_teleport", MAGIC_DATA, {})
        self.assertIn("Desert Treasure", reasons)
        rows = magic_target_rows(player, MAGIC_DATA, MAGIC_ITEM_IMAGES, "low_alchemy", {})
        row = next(row for row in rows if row.target_id == "kharyrll_teleport")
        self.assertFalse(row.enabled)

    def test_combat_preset_mixing_and_one_swap_exception(self):
        data = default_combat_state_pure()
        data.update({
            "magic_level": 99,
            "equipment": {"weapon": "Staff of air"},
            "current_combat_spell": "ice_barrage",
            "combat_vengeance": True,
            "quests": _quest_state("desert_treasure", "lunar_diplomacy"),
            "inventory": {"Astral rune": 3, "Cosmic rune": 2, "Law rune": 1},
        })
        self.assertEqual(combat_magic_preset_locked_reasons_pure(data), ("Preset mixes spellbooks",))
        data["combat_spellbook_swap"] = "vengeance"
        self.assertEqual(combat_magic_preset_locked_reasons_pure(data), ())

    def test_casual_dial_derives_protection_and_dream(self):
        data = default_combat_state_pure()
        data.update({"prayer_level": 99, "magic_level": 99, "quests": _quest_state("dream_mentor"), "current_combat_target": "chicken"})
        safe, ok, reason = set_combat_pack_mode_pure(data, "max_safety")
        self.assertTrue(ok, reason)
        self.assertEqual(safe["combat_pack_mode"], "max_safety")
        self.assertTrue(safe["combat_dream_thrift"])
        self.assertIn("protect_from_melee", safe["combat_selected_prayers"])

    def test_casual_dial_preserves_an_eligible_manual_dream_toggle(self):
        data = default_combat_state_pure()
        data.update(
            {
                "magic_level": 79,
                "quests": _quest_state("dream_mentor"),
                "current_combat_target": "chicken",
                "combat_dream_thrift": True,
            }
        )

        for mode in ("balanced", "max_output"):
            with self.subTest(mode=mode):
                changed, ok, reason = set_combat_pack_mode_pure(data, mode)
                self.assertTrue(ok, reason)
                self.assertTrue(changed["combat_dream_thrift"])

    def test_casual_dial_never_auto_selects_locked_dream(self):
        data = default_combat_state_pure()
        data.update(
            {
                "magic_level": 1,
                "constitution_level": 10,
                "combat_lifepoints": 42,
                "current_combat_target": "chicken",
                "combat_dream_thrift": True,
            }
        )

        safe, safe_ok, safe_reason = set_combat_pack_mode_pure(data, "max_safety")
        output, output_ok, output_reason = set_combat_pack_mode_pure(safe, "max_output")

        self.assertTrue(safe_ok, safe_reason)
        self.assertTrue(output_ok, output_reason)
        self.assertFalse(safe["combat_dream_thrift"])
        self.assertFalse(output["combat_dream_thrift"])
        self.assertEqual(combat_magic_preset_locked_reasons_pure(output), ())

    def test_mage_arena_is_a_five_review_landmark(self):
        data = {
            "magic_level": 60,
            "inventory": {},
            "equipment": {},
            "mage_arena": {"step": 0, "completed": False},
        }
        for step in range(1, 5):
            data, ok, info = apply_mage_arena_step_pure(data)
            self.assertTrue(ok)
            self.assertEqual(info["step"], step)

        blocked, ok, info = apply_mage_arena_step_pure(data)
        self.assertFalse(ok)
        self.assertEqual(info["reason"], "mage_arena_alignment_required")
        self.assertEqual(blocked, data)

        data, ok, _ = set_mage_arena_alignment_pure(data, "guthix")
        self.assertTrue(ok)
        data, ok, info = apply_mage_arena_step_pure(data)
        self.assertTrue(ok)
        self.assertEqual(info["step"], 5)
        self.assertTrue(data["mage_arena"]["completed"])
        self.assertEqual(data["mage_arena"]["alignment"], "guthix")
        self.assertEqual(data["mage_arena"]["attuned_spells"], ["claws_of_guthix"])
        self.assertEqual(data["inventory"]["Guthix cape"], 1)
        self.assertEqual(data["inventory"]["Guthix staff"], 1)

    def test_mage_arena_attunement_requires_the_matching_staff_and_cape_actions_enforce_one_cape(self):
        data = {
            "magic_level": 99,
            "inventory": {"Saradomin cape": 2, "Guthix cape": 1},
            "equipment": {"cape": "Zamorak cape"},
            "mage_arena": {
                "step": 5,
                "completed": True,
                "alignment": "saradomin",
                "attuned_spells": ["saradomin_strike"],
            },
        }
        unchanged, ok, info = attune_mage_arena_spell_pure(data, "zamorak")
        self.assertFalse(ok)
        self.assertEqual(info["reason"], "missing_staff")
        self.assertEqual(
            unchanged["mage_arena"]["attuned_spells"],
            data["mage_arena"]["attuned_spells"],
        )
        self.assertNotIn("Zamorak staff", data["inventory"])

        data["inventory"]["Zamorak staff"] = 1
        attuned, ok, info = attune_mage_arena_spell_pure(data, "zamorak")
        self.assertTrue(ok)
        self.assertEqual(info["spell_id"], "flames_of_zamorak")
        self.assertEqual(
            attuned["mage_arena"]["attuned_spells"],
            ["saradomin_strike", "flames_of_zamorak"],
        )

        switched, ok, info = apply_mage_arena_cape_action_pure(attuned, "guthix")
        self.assertTrue(ok)
        self.assertEqual(info["cape"], "Guthix cape")
        self.assertNotIn("cape", switched["equipment"])
        self.assertEqual(switched["inventory"]["Saradomin cape"], 0)
        self.assertEqual(switched["inventory"]["Zamorak cape"], 0)
        self.assertEqual(switched["inventory"]["Guthix cape"], 1)
        self.assertNotIn(
            "claws_of_guthix",
            switched["mage_arena"]["attuned_spells"],
        )

    def test_legacy_mage_arena_claim_preserves_the_original_free_loadout(self):
        legacy = {
            "inventory": {},
            "equipment": {},
            "mage_arena": {"step": 5, "completed": True},
        }
        claimed, ok, info = apply_mage_arena_cape_action_pure(legacy, "zamorak")
        self.assertTrue(ok)
        self.assertEqual(info["reason"], "legacy_alignment_claimed")
        self.assertEqual(claimed["inventory"]["Zamorak cape"], 1)
        self.assertEqual(claimed["inventory"]["Zamorak staff"], 1)
        self.assertEqual(
            claimed["mage_arena"]["attuned_spells"],
            ["flames_of_zamorak"],
        )

        migrated = migrate_loaded_data(
            {
                "config_version": 39,
                "mage_arena": {
                    "step": 5,
                    "completed": True,
                    "alignment": "saradomin",
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(
            migrated["mage_arena"]["attuned_spells"],
            ["saradomin_strike"],
        )

    def test_god_spell_attunement_and_charge_bonus_require_the_matching_loadout(self):
        state = {
            "magic_level": 99,
            "mage_arena": {
                "step": 5,
                "completed": True,
                "alignment": "saradomin",
                "attuned_spells": ["saradomin_strike"],
            },
            "magic_charge_active": True,
            "magic_charge_ticks_remaining": 700,
            "equipment": {
                "cape": "Saradomin cape",
                "weapon": "Saradomin staff",
            },
            "inventory": {},
        }
        self.assertEqual(
            charged_god_spell_max_hit_bonus_pure(state, "saradomin_strike"),
            10,
        )

        wrong_cape = {**state, "equipment": {**state["equipment"], "cape": "Guthix cape"}}
        self.assertEqual(
            charged_god_spell_max_hit_bonus_pure(wrong_cape, "saradomin_strike"),
            0,
        )
        for god_id, row in MAGE_ARENA_GOD_DATA.items():
            with self.subTest(god_id=god_id):
                self.assertIn(
                    row["spell_id"],
                    {spell.id for spell in COMBAT_MAGIC_ADDITIONS},
                )

    def test_god_loadout_equip_guard_and_combat_preview_apply_charge(self):
        player = {
            "inventory": {"Guthix cape": 1},
            "equipment": {"weapon": "Saradomin staff"},
            "magic_level": 99,
        }
        ok, reason = can_equip_item_pure("Guthix cape", EQUIPMENT_DATA, player)
        self.assertFalse(ok)
        self.assertIn("Saradomin staff", reason)
        inventory, equipment, equipped = equip_item_pure(
            "Guthix cape",
            player["inventory"],
            player["equipment"],
            EQUIPMENT_DATA,
        )
        self.assertFalse(equipped)
        self.assertEqual(inventory, player["inventory"])
        self.assertEqual(equipment, player["equipment"])

        combat_player = {
            "inventory": {"Air rune": 4, "Fire rune": 2, "Blood rune": 2},
            "equipment": {
                "weapon": "Saradomin staff",
                "cape": "Saradomin cape",
            },
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "ranged_level": 99,
            "magic_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "saradomin_strike",
            "combat_supply_loadout": {},
            "combat_encounter": {},
            "combat_status_effects": {},
            "combat_auto_eat_food": [],
            "mage_arena": {
                "step": 5,
                "completed": True,
                "alignment": "saradomin",
                "attuned_spells": ["saradomin_strike"],
            },
            "magic_charge_active": True,
            "magic_charge_ticks_remaining": 700,
        }
        charged = combat_target_preview_pure(
            combat_player,
            "chicken",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )
        self.assertEqual(charged["state"], "Ready")
        self.assertEqual(charged["player_max_hit"], 300)
        uncharged = combat_target_preview_pure(
            {**combat_player, "magic_charge_active": False},
            "chicken",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )
        self.assertEqual(uncharged["player_max_hit"], 200)

    def test_mage_arena_attunement_runtime_consumes_exactly_one_review(self):
        player = {
            "current_utility": "mage_arena_attune:guthix",
            "inventory": {"Guthix staff": 1},
            "equipment": {},
            "completed_achievements": [],
            "mage_arena": {
                "step": 5,
                "completed": True,
                "alignment": "saradomin",
                "attuned_spells": ["saradomin_strike"],
            },
        }
        calls = {"errors": [], "saves": 0, "shown_xp": []}
        self.assertTrue(handle_utility_answer(_context(player, calls)))
        self.assertIn("claws_of_guthix", player["mage_arena"]["attuned_spells"])
        self.assertEqual(calls["saves"], 1)
        self.assertTrue(calls["deactivated"])

    def test_v30_migration_preserves_combat_trained_magic_xp_and_extends_presets(self):
        migrated = migrate_loaded_data({
            "config_version": 29,
            "magic_level": 73,
            "magic_exp": 1000000.0,
            "combat_presets": {"Bossing": {"combat_pack_mode": "compact"}},
            "inventory": {"Unknown future item": 7},
        }, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual((migrated["magic_level"], migrated["magic_exp"]), (73, 1000000.0))
        self.assertEqual(migrated["inventory"]["Unknown future item"], 7)
        self.assertIn("combat_spellbook_swap", migrated["combat_presets"]["Bossing"])

    def test_runtime_handler_is_registered_and_mutates_one_undoable_state(self):
        player = {"magic_level": 99, "magic_exp": 0.0, "current_magic": "varrock_teleport", "inventory": {"Air rune": 3, "Fire rune": 1, "Law rune": 1}, "completed_achievements": []}
        calls = {"errors": [], "saves": 0, "shown_xp": []}
        self.assertIs(answer_handler_for_key("magic"), handle_magic_answer)
        self.assertTrue(handle_magic_answer(_context(player, calls)))
        self.assertEqual(player["magic_exp"], 35.0)
        self.assertEqual(player["magic_actions_completed"], 1)
        self.assertEqual(calls["saves"], 1)

    def test_superheat_output_credit_belongs_to_magic_not_smithing(self):
        player = {
            "magic_level": 99,
            "magic_exp": 0.0,
            "smithing_level": 70,
            "smithing_exp": 0.0,
            "current_magic": "superheat_adamant_bar",
            "inventory": {
                "Nature rune": 1,
                "Fire rune": 4,
                "Adamantite ore": 1,
                "Coal": 6,
            },
            "completed_achievements": [],
        }
        calls = {"errors": [], "saves": 0, "shown_xp": []}

        self.assertTrue(handle_magic_answer(_context(player, calls)))

        skills = player["achievement_progress"]["skills"]
        self.assertEqual(skills["magic"]["outputs"], {"Adamant bar": 1})
        self.assertNotIn("smithing", skills)

    def test_named_presets_capture_new_magic_fields(self):
        data = default_combat_state_pure()
        data.update({"current_combat_spell": "fire_surge", "combat_vengeance": True, "combat_dream_thrift": True, "combat_spellbook_swap": "vengeance"})
        saved, ok = save_combat_preset_pure(data, "Magic")
        self.assertTrue(ok)
        self.assertEqual(saved["combat_presets"]["Magic"]["current_combat_spell"], "fire_surge")
        self.assertEqual(saved["combat_presets"]["Magic"]["combat_spellbook_swap"], "vengeance")

    def test_existing_strung_amulet_inventory_and_equipment_survive_load(self):
        migrated = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "inventory": {"Gold amulet": 2},
                "equipment": {"neck": "Gold amulet"},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["inventory"]["Gold amulet"], 2)
        self.assertEqual(migrated["equipment"]["neck"], "Gold amulet")

    def test_every_magic_manifest_asset_exists(self):
        self.assertEqual(len(MAGIC_ITEM_IMAGES), 139)
        for path in MAGIC_ITEM_IMAGES.values():
            self.assertTrue(os.path.exists(path), path)

    def test_every_magic_target_uses_a_provenanced_spell_icon(self):
        root = Path(__file__).resolve().parents[1]
        provenance = json.loads(
            (root / "assets_provenance.json").read_text(encoding="utf-8")
        )
        visual_fallback_sources = {
            "mobilising_armies_teleport": "rs3-fandom-visual-fallback",
            "tan_leather": "osrs-visual-fallback",
            "magic_imbue": "osrs-visual-fallback",
            "cure_plant": "osrs-visual-fallback",
            "fertile_soil": "osrs-visual-fallback",
            "borrowed_telegrab_wine_of_zamorak": (
                "rs3-fandom-visual-fallback"
            ),
            "borrowed_teleport_to_house": (
                "rs3-fandom-visual-fallback"
            ),
            "borrowed_high_alchemy": "rs3-fandom-visual-fallback",
            "borrowed_bones_to_peaches": (
                "rs3-fandom-visual-fallback"
            ),
        }
        self.assertEqual(set(MAGIC_SPELL_IMAGES), set(MAGIC_DATA))
        rows = magic_target_rows(
            {"magic_level": 99, "inventory": {}},
            MAGIC_DATA,
            MAGIC_ITEM_IMAGES,
            "low_alchemy",
            {},
            MAGIC_SPELL_IMAGES,
        )
        self.assertEqual(len(rows), len(MAGIC_DATA))
        for row in rows:
            with self.subTest(target=row.target_id):
                path = Path(MAGIC_SPELL_IMAGES[row.target_id])
                self.assertTrue(path.is_file())
                self.assertEqual(row.icon_path, str(path))
                asset = provenance[str(path.relative_to(root))]
                if row.target_id in visual_fallback_sources:
                    self.assertEqual(
                        asset["source_wiki"],
                        visual_fallback_sources[row.target_id],
                    )
                else:
                    self.assertIn(
                        asset["source_wiki"],
                        {"rs3-period", "rs3-fandom-period"},
                    )
                    self.assertLessEqual(
                        asset["timestamp"],
                        "2012-11-20T23:59:59Z",
                    )


if __name__ == "__main__":
    unittest.main()
