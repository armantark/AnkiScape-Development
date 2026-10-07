import json
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.dungeoneering_data import (
    AMMO_BIND_CAPACITY,
    BIND_LOADOUT_COUNT,
    BIND_SLOTS_BY_LEVEL,
    COAL_BAG_REWARD,
    COLLECTED_BIND_LIMIT,
    COMPLEXITIES_BY_LEVEL,
    DUNGEONEERING_ITEM_IMAGES,
    DUNGEONEERING_REWARDS,
    FLOOR_SIZES_BY_ID,
    FLOOR_THEMES,
    FROZEN_BOSSES,
    FROZEN_BOSS_COMBAT_LEVEL_LADDERS,
    FROZEN_SKILL_DOORS,
    KINSHIP_CLASSES,
    KINSHIP_TIER_COSTS,
    RING_OF_KINSHIP_CLASS_ITEM_IDS,
    RING_OF_KINSHIP_ITEM_ID,
    SALT_IN_THE_WOUND_AMMO_BIND_CAPACITY,
    SKILL_DOOR_FAILURE_CHANCE,
    SKILL_DOOR_FAILURE_DAMAGE_MULTIPLIER,
    SMUGGLER_ITEMS_BY_ID,
    SMUGGLER_SELLBACK_RATE,
    SMUGGLER_STOCK_BANDS,
    SOURCE_REVISIONS,
    STARTER_HERBLORE_CHAIN,
    STARTER_RESOURCE_CHAIN,
    STARTER_SKILL_DOOR_REQUIREMENT,
    STARTER_SMALL_GRAPH_ROOM_COUNT,
    STARTER_SMALL_REVIEW_BUDGET,
)
from ankiscape.data.herblore_data import DUNGEONEERING_HERBLORE_TARGETS
from ankiscape.core.constants import ITEM_DEFINITIONS
from ankiscape.core.skill_registry import get_skill


class DungeoneeringDataTests(unittest.TestCase):
    def test_phase_c_item_art_is_period_pinned_with_provenance(self):
        root = Path(__file__).resolve().parents[1]
        provenance = json.loads(
            (root / "assets_provenance.json").read_text(encoding="utf-8")
        )
        expected = {
            "Ring of kinship": (
                "2010-09-18T03:48:18Z",
                "bea3e2c288332d3a0fc90f083861aab543b36aa2",
            ),
            "Coal bag": (
                "2010-09-18T04:20:22Z",
                "9963825b60920a01c7aae0a761ddbce02ab5aef6",
            ),
        }
        for item_name, (timestamp, sha1) in expected.items():
            with self.subTest(item_name=item_name):
                asset_path = DUNGEONEERING_ITEM_IMAGES[item_name]
                self.assertTrue((root / asset_path).is_file())
                self.assertEqual(provenance[asset_path]["timestamp"], timestamp)
                self.assertEqual(provenance[asset_path]["sha1"], sha1)

        ring = next(
            item
            for item in ITEM_DEFINITIONS
            if item.display_name == "Ring of kinship"
        )
        self.assertEqual(ring.category, "tool")
        self.assertIsNone(ring.equipment_slot)

    def test_pinned_period_revisions_cover_every_starter_table(self):
        expected = {
            "dungeoneering": (6579699, "2012-11-19T02:31:37Z"),
            "floors": (6542025, "2012-11-08T00:49:39Z"),
            "prestige": (6516987, "2012-11-01T21:57:13Z"),
            "complexity": (6555542, "2012-11-14T19:37:17Z"),
            "kinship_classes": (6521933, "2012-11-03T01:29:00Z"),
            "coal_bag": (6283103, "2012-09-22T22:36:07Z"),
            "bosses": (6398065, "2012-10-14T01:46:52Z"),
            "doors": (6325508, "2012-09-30T17:22:57Z"),
            "fishing": (5812989, "2012-06-23T16:17:51Z"),
            "cooking": (6457563, "2012-10-23T01:30:20Z"),
            "herblore": (6555616, "2012-11-14T20:45:41Z"),
            "rewards": (6297239, "2012-09-25T21:01:33Z"),
            "smuggler": (6564954, "2012-11-17T04:36:56Z"),
        }
        for source_id, revision in expected.items():
            with self.subTest(source_id=source_id):
                self.assertEqual(SOURCE_REVISIONS[source_id], revision)

    def test_floor_complexity_and_bind_tables_match_the_period_rows(self):
        self.assertEqual(
            [
                (
                    theme.id,
                    theme.first_floor,
                    theme.last_floor,
                    theme.minimum_level,
                    theme.maximum_level,
                )
                for theme in FLOOR_THEMES
            ],
            [
                ("frozen", 1, 11, 1, 21),
                ("abandoned_i", 12, 17, 23, 33),
                ("furnished", 18, 29, 35, 57),
                ("abandoned_ii", 30, 35, 59, 69),
                ("occult", 36, 47, 71, 93),
                ("warped", 48, 60, 95, 119),
            ],
        )
        self.assertEqual(
            {
                size_id: (size.grid_width, size.grid_height, size.maximum_rooms)
                for size_id, size in FLOOR_SIZES_BY_ID.items()
            },
            {"small": (4, 4, 16), "medium": (4, 8, 32), "large": (8, 8, 64)},
        )
        self.assertEqual(
            [COMPLEXITIES_BY_LEVEL[level].xp_penalty_percent for level in range(1, 7)],
            [50, 45, 40, 35, 30, 0],
        )
        self.assertTrue(COMPLEXITIES_BY_LEVEL[1].forced_guide_mode)
        self.assertFalse(COMPLEXITIES_BY_LEVEL[1].skill_doors)
        self.assertTrue(COMPLEXITIES_BY_LEVEL[6].skill_doors)
        self.assertEqual(SKILL_DOOR_FAILURE_CHANCE, 0.11)
        self.assertEqual(SKILL_DOOR_FAILURE_DAMAGE_MULTIPLIER, 4)
        self.assertEqual(BIND_SLOTS_BY_LEVEL, ((1, 1), (20, 2), (50, 3), (90, 4), (120, 5)))
        self.assertEqual(COLLECTED_BIND_LIMIT, 10)
        self.assertEqual(BIND_LOADOUT_COUNT, 3)
        self.assertEqual((AMMO_BIND_CAPACITY, SALT_IN_THE_WOUND_AMMO_BIND_CAPACITY), (125, 225))
        self.assertEqual(
            (STARTER_SMALL_REVIEW_BUDGET, STARTER_SMALL_GRAPH_ROOM_COUNT),
            (8, 10),
        )
        self.assertEqual(STARTER_SKILL_DOOR_REQUIREMENT, 1)

    def test_kinship_boss_and_reward_tables_are_complete_for_the_starter(self):
        self.assertEqual(
            [kinship_class.display_name for kinship_class in KINSHIP_CLASSES],
            [
                "Tank",
                "Tactician",
                "Berserker",
                "Sniper",
                "Keen-eye",
                "Desperado",
                "Blazer",
                "Blaster",
                "Blitzer",
                "Medic",
                "Gatherer",
                "Artisan",
            ],
        )
        self.assertTrue(all(len(kinship_class.tier_values_percent) == 10 for kinship_class in KINSHIP_CLASSES))
        self.assertEqual(KINSHIP_TIER_COSTS, (135, 175, 335, 660, 1360, 3400, 6800, 18750, 58600, 233000))
        self.assertEqual(RING_OF_KINSHIP_ITEM_ID, 15707)
        self.assertEqual(set(RING_OF_KINSHIP_CLASS_ITEM_IDS.values()), set(range(18817, 18829)))
        self.assertEqual(
            [(boss.minimum_level, boss.first_floor, boss.last_floor) for boss in FROZEN_BOSSES],
            [(1, 1, 11), (1, 1, 11), (1, 1, 11), (5, 3, 11), (11, 6, 11), (17, 9, 11)],
        )
        self.assertEqual(
            (
                COAL_BAG_REWARD.token_cost,
                COAL_BAG_REWARD.dungeoneering_level,
                COAL_BAG_REWARD.other_skill_requirements,
                COAL_BAG_REWARD.source_item_id,
            ),
            (4000, 35, (("Mining", 35),), 18339),
        )
        self.assertTrue(COAL_BAG_REWARD.fully_functional)

    def test_reward_catalog_matches_all_42_sourced_cost_and_gate_rows(self):
        expected = (
            ("dungeoneering_xp_lamp", 1, 0, ()),
            ("gem_bag", 2000, 25, ()),
            ("coal_bag", 4000, 35, (("Mining", 35),)),
            ("arcane_pulse_necklace", 6500, 30, ()),
            ("twisted_bird_skull_necklace", 8500, 30, ()),
            ("scroll_of_life", 10000, 25, ()),
            ("longbow_sight", 10000, 45, ()),
            ("law_staff", 10000, 45, (("Magic", 45),)),
            ("nature_staff", 12500, 53, (("Magic", 53),)),
            ("arcane_blast_necklace", 15500, 50, ()),
            ("split_dragontooth_necklace", 17000, 60, ()),
            ("scroll_of_cleansing", 20000, 49, ()),
            ("scroll_of_efficiency", 20000, 55, ()),
            ("arcane_stream_necklace", 30500, 70, ()),
            ("bonecrusher", 34000, 21, ()),
            ("herbicide", 34000, 21, ()),
            ("demon_horn_necklace", 35000, 90, ()),
            ("amulet_of_zealots", 40000, 48, ()),
            ("gravite_rapier", 40000, 45, ()),
            ("gravite_longsword", 40000, 45, ()),
            ("gravite_two_handed_sword", 40000, 45, ()),
            ("gravite_staff", 40000, 45, ()),
            ("gravite_shortbow", 40000, 45, ()),
            (
                "magical_blastbox",
                40000,
                30,
                (("Magic", 30), ("Runecrafting", 30)),
            ),
            ("tome_of_frost", 43000, 48, ()),
            ("anti_poison_totem", 44000, 60, ()),
            ("spirit_cape", 45000, 50, ()),
            ("mercenarys_gloves", 48500, 73, ()),
            ("ring_of_vigour", 50000, 62, ()),
            (
                "celestial_surgebox",
                65000,
                70,
                (("Magic", 70), ("Runecrafting", 70)),
            ),
            ("sneakerpeeper", 85000, 80, ()),
            ("scroll_of_renewal", 107000, 65, ()),
            ("scroll_of_rigour", 140000, 74, ()),
            ("scroll_of_augury", 153000, 77, ()),
            ("chaotic_rapier", 200000, 80, ()),
            ("chaotic_longsword", 200000, 80, ()),
            ("chaotic_maul", 200000, 80, ()),
            ("chaotic_staff", 200000, 80, ()),
            ("chaotic_crossbow", 200000, 80, ()),
            ("chaotic_kiteshield", 200000, 80, ()),
            ("eagle_eye_kiteshield", 200000, 80, ()),
            ("farseer_kiteshield", 200000, 80, ()),
        )

        self.assertEqual(
            tuple(
                (
                    reward.id,
                    reward.token_cost,
                    reward.dungeoneering_level,
                    reward.other_skill_requirements,
                )
                for reward in DUNGEONEERING_REWARDS
            ),
            expected,
        )
        self.assertEqual(
            [reward.id for reward in DUNGEONEERING_REWARDS if reward.fully_functional],
            ["coal_bag"],
        )

    def test_starter_resource_and_herblore_chains_are_period_shaped(self):
        dungeoneering_herblore_by_id = {
            target.id: target for target in DUNGEONEERING_HERBLORE_TARGETS
        }
        self.assertEqual(
            [(step.level, step.xp, step.output) for step in STARTER_RESOURCE_CHAIN],
            [(1, 9.0, ("Raw heim crab", 1)), (1, 22.0, ("Heim crab", 1))],
        )
        self.assertEqual(
            [step.existing_target_id for step in STARTER_HERBLORE_CHAIN],
            ["clean_valerian", "unf_valerian", "finished_weak_ranged"],
        )
        self.assertEqual(
            [(step.level, step.xp) for step in STARTER_HERBLORE_CHAIN],
            [(4, 3.2), (4, 0.0), (5, 34.0)],
        )
        self.assertTrue(all(step.minimum_complexity >= 5 for step in STARTER_HERBLORE_CHAIN))
        for step in STARTER_HERBLORE_CHAIN:
            with self.subTest(step=step.id):
                existing = dungeoneering_herblore_by_id[step.existing_target_id]
                self.assertEqual((existing.level, existing.exp), (step.level, step.xp))

    def test_frozen_doors_boss_ladders_and_smuggler_bands_match_the_harvest(self):
        self.assertEqual(
            [(door.skill_id, door.frozen_object_id) for door in FROZEN_SKILL_DOORS],
            [
                ("runecrafting", 50278),
                ("strength", 50272),
                ("mining", 50305),
                ("firemaking", 50314),
                ("magic", 50329),
                ("prayer", 50332),
                ("woodcutting", 50317),
                ("smithing", 50308),
                ("crafting", 50299),
            ],
        )
        self.assertEqual(
            FROZEN_BOSS_COMBAT_LEVEL_LADDERS["gluttonous_behemoth"],
            (5, 25, 41, 63, 91, 132, 170, 199, 238, 278, 299, 334, 362, 389, 437, 476, 518),
        )
        self.assertEqual(
            FROZEN_BOSS_COMBAT_LEVEL_LADDERS["tokash_bloodchiller"],
            (8, 22, 49, 67, 104, 127, 159, 188, 216, 255, 292, 355, 408, 442, 477, 512),
        )
        self.assertEqual(
            [SMUGGLER_STOCK_BANDS[level].source_row_count for level in range(1, 7)],
            [0, 4, 19, 26, 86, 86],
        )
        self.assertEqual(len(SMUGGLER_ITEMS_BY_ID), 86)
        self.assertEqual(
            SMUGGLER_STOCK_BANDS[2].item_ids,
            ("raw_heim_crab", "tangle_gum_branches", "feather", "antipoison"),
        )
        self.assertEqual(
            SMUGGLER_STOCK_BANDS[3].item_ids[:10],
            (
                "novite_ore",
                "bathus_ore",
                "marmaros_ore",
                "raw_heim_crab",
                "raw_red_eye",
                "raw_dusk_eel",
                "tangle_gum_branches",
                "seeping_elm_branches",
                "blood_spindle_branches",
                "rune_essence",
            ),
        )
        self.assertEqual(
            (SMUGGLER_ITEMS_BY_ID["novite_ore"].source_item_id, SMUGGLER_ITEMS_BY_ID["novite_ore"].buy_price),
            (17630, 525),
        )
        self.assertEqual(
            {
                item_id: SMUGGLER_ITEMS_BY_ID[item_id].buy_price
                for item_id in (
                    "raw_heim_crab",
                    "tangle_gum_branches",
                    "feather",
                    "antipoison",
                    "valerian_seed",
                    "void_dust",
                    "vial",
                )
            },
            {
                "raw_heim_crab": 200,
                "tangle_gum_branches": 225,
                "feather": 6,
                "antipoison": 200,
                "valerian_seed": 3000,
                "void_dust": 1000,
                "vial": 10,
            },
        )
        self.assertEqual(SMUGGLER_ITEMS_BY_ID["novite_rapier"].equipment_slot, "weapon")
        self.assertEqual(SMUGGLER_ITEMS_BY_ID["novite_kiteshield"].equipment_slot, "shield")
        self.assertTrue(SMUGGLER_ITEMS_BY_ID["novite_arrows"].ammo_bind)
        self.assertEqual(SMUGGLER_SELLBACK_RATE, 0.30)

    def test_skill_is_trainable_without_claiming_the_floor_surface_is_complete(self):
        skill = get_skill("dungeoneering")
        self.assertIsNotNone(skill)
        self.assertTrue(skill.trainable)
        self.assertTrue(skill.implemented)
        self.assertTrue(skill.participates_in_review)
        self.assertEqual(skill.review_handler_key, "dungeoneering")
        self.assertEqual(skill.surface_state, "partial")


if __name__ == "__main__":
    unittest.main()
