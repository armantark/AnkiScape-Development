import os
import unittest

from constants import ITEM_DEFINITIONS, MAGIC_DATA, MAGIC_ITEM_IMAGES, ORE_DATA
from logic_pure import (
    apply_magic_action_pure,
    apply_mage_arena_step_pure,
    combat_magic_preset_locked_reasons_pure,
    default_combat_state_pure,
    effective_magic_rune_cost_pure,
    magic_target_locked_reasons_pure,
    save_combat_preset_pure,
    set_combat_pack_mode_pure,
)
from farming_logic import default_farming_state_pure, execute_farm_field_step_pure, set_farm_plan_pure
from magic_data import COMBAT_MAGIC_ADDITIONS, MAGIC_TARGETS
from runtime_actions import RuntimeActionContext, answer_handler_for_key, handle_magic_answer
from storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from target_metadata import magic_target_rows


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
        self.assertEqual(len(MAGIC_TARGETS), 94)
        self.assertEqual(len(MAGIC_TARGETS), len(set(MAGIC_TARGETS)))
        books = {row["spellbook"] for row in MAGIC_TARGETS.values()}
        self.assertEqual(books, {"standard", "ancient", "lunar"})
        ancient_combat = [spell for spell in COMBAT_MAGIC_ADDITIONS if spell.spellbook == "ancient"]
        self.assertEqual(len(ancient_combat), 20)
        self.assertEqual({spell.id for spell in ancient_combat if spell.id.startswith("miasmic_")}, {
            "miasmic_rush", "miasmic_burst", "miasmic_blitz", "miasmic_barrage",
        })

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
        safe = set_combat_pack_mode_pure(data, "max_safety")
        self.assertEqual(safe["combat_pack_mode"], "max_safety")
        self.assertTrue(safe["combat_dream_thrift"])
        self.assertIn("protect_from_melee", safe["combat_selected_prayers"])

    def test_mage_arena_is_a_five_review_landmark(self):
        data = {"magic_level": 60, "mage_arena": {"step": 0, "completed": False}}
        for step in range(1, 6):
            data, ok, info = apply_mage_arena_step_pure(data)
            self.assertTrue(ok)
            self.assertEqual(info["step"], step)
        self.assertTrue(data["mage_arena"]["completed"])

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
        self.assertEqual(len(MAGIC_ITEM_IMAGES), 130)
        for path in MAGIC_ITEM_IMAGES.values():
            self.assertTrue(os.path.exists(path), path)


if __name__ == "__main__":
    unittest.main()
