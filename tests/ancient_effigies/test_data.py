"""The settled Ancient Effigies table, its assets and its evidence copies."""

from __future__ import annotations

import hashlib
import json
import os
import re
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, exp_table_for_skill
from ankiscape.core.skill_registry import get_skill
from ankiscape.data.ancient_effigies import catalog
from ankiscape.logic.ancient_effigies import requests
from ankiscape.logic.ancient_effigies.actions import lamp_preview_pure

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_PACKAGE = os.path.join(_ROOT, "data", "ancient_effigies")


def _sha256(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


class StageTableTest(unittest.TestCase):
    def test_stage_rows_are_the_settled_period_values(self):
        self.assertEqual(
            [
                (stage.item_id, stage.name, stage.required_level, stage.reward_xp, stage.output_item_id, stage.output_name)
                for stage in catalog.STAGES
            ],
            [
                (18778, "Starved ancient effigy", 91, 15000, 18779, "Nourished ancient effigy"),
                (18779, "Nourished ancient effigy", 93, 20000, 18780, "Sated ancient effigy"),
                (18780, "Sated ancient effigy", 95, 25000, 18781, "Gorged ancient effigy"),
                (18781, "Gorged ancient effigy", 97, 30000, 18782, "Dragonkin lamp"),
            ],
        )
        self.assertEqual(sum(stage.reward_xp for stage in catalog.STAGES), 90000)

    def test_pairs_keep_their_exact_index_order(self):
        self.assertEqual(
            catalog.SKILL_PAIRS,
            (
                ("crafting", "agility"),
                ("construction", "thieving"),
                ("cooking", "firemaking"),
                ("farming", "fishing"),
                ("fletching", "woodcutting"),
                ("herblore", "hunter"),
                ("smithing", "mining"),
                ("runecrafting", "summoning"),
            ),
        )
        skills = [skill for pair in catalog.SKILL_PAIRS for skill in pair]
        self.assertEqual(len(set(skills)), 16)
        for skill_id in skills:
            self.assertIsNotNone(get_skill(skill_id), skill_id)

    def test_lamp_offers_twenty_five_unique_registry_skills_in_supplying_order(self):
        self.assertEqual(
            catalog.LAMP_SKILL_IDS,
            (
                "attack", "magic", "mining", "woodcutting", "agility", "fletching",
                "thieving", "strength", "ranged", "smithing", "firemaking", "herblore",
                "slayer", "construction", "defense", "prayer", "fishing", "crafting",
                "farming", "hunter", "summoning", "constitution", "dungeoneering",
                "cooking", "runecrafting",
            ),
        )
        self.assertEqual(len(set(catalog.LAMP_SKILL_IDS)), 25)
        for skill_id in catalog.LAMP_SKILL_IDS:
            skill = get_skill(skill_id)
            self.assertIsNotNone(skill, skill_id)
            self.assertEqual(skill.id, skill_id)

    def test_the_catalog_imports_neither_constants_nor_the_registry(self):
        with open(catalog.__file__, encoding="utf-8") as handle:
            source = handle.read()
        imports = re.findall(r"^(?:from|import) [^\n]+", source, flags=re.MULTILINE)
        self.assertIn("from dataclasses import dataclass", set(imports), "the scan reads the catalog's imports")
        self.assertFalse([line for line in imports if "constants" in line or "item_registry" in line], imports)


class LampFormulaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(_HERE, "lamp_xp_rows.json"), encoding="utf-8") as handle:
            cls.table = json.load(handle)

    def test_the_formula_matches_all_120_transcribed_rows(self):
        rows = self.table["experience_by_level"]
        self.assertEqual(sorted(int(level) for level in rows), list(range(1, 121)))
        for level, experience in rows.items():
            self.assertEqual(catalog.dragonkin_lamp_xp(int(level)), experience, level)

    def test_transcription_cites_the_retained_lamp_body(self):
        source = self.table["source"]
        self.assertEqual(
            (source["revision"], source["timestamp_utc"], source["sha256"], source["lines"]),
            ("6350210", "2012-10-05T11:47:40Z", "19be1abf94d1cc11fe2484835bc2f3901594d3aacc4553ad44a24148a7d7ce88", "72-130"),
        )
        self.assertEqual(len(self.table["literal_rows"]), 30)
        self.assertEqual(self.table["literal_rows"][0], {"line": 72, "text": "| 120|| 85,560 ||||90|| 36,090 ||||60|| 10,740 ||||30|| 1,410"})

    def test_contract_examples(self):
        self.assertEqual(
            [catalog.dragonkin_lamp_xp(level) for level in (1, 2, 60, 99, 100, 120)],
            [4, 10, 10740, 48029, 49500, 85560],
        )

    def test_ordinary_skills_read_at_most_level_99(self):
        player = {"attack_exp": exp_table_for_skill("attack")[-1] * 4}
        self.assertEqual(lamp_preview_pure(player, "attack"), (99, 48029))
        self.assertEqual(catalog.lamp_level_cap("attack"), 99)

    def test_dungeoneering_reads_up_to_level_120(self):
        table = exp_table_for_skill("dungeoneering")
        self.assertEqual(lamp_preview_pure({"dungeoneering_exp": table[99]}, "dungeoneering"), (100, 49500))
        self.assertEqual(lamp_preview_pure({"dungeoneering_exp": table[-1] * 2}, "dungeoneering"), (120, 85560))
        self.assertEqual(catalog.lamp_level_cap("dungeoneering"), 120)

    def test_permanent_level_starts_at_one(self):
        self.assertEqual(lamp_preview_pure({}, "attack"), (1, 4))
        self.assertEqual(lamp_preview_pure({"attack_exp": 83}, "attack"), (2, 10))


class ItemRegistryTest(unittest.TestCase):
    def test_five_definitions_carry_attested_identity_and_flags(self):
        by_key = {}
        for item in ITEM_DEFINITIONS:
            by_key.setdefault(item.storage_key, []).append(item)
        expected = {
            "Starved ancient effigy": (18778, catalog.EFFIGY_ASSET_PATH),
            "Nourished ancient effigy": (18779, catalog.EFFIGY_ASSET_PATH),
            "Sated ancient effigy": (18780, catalog.EFFIGY_ASSET_PATH),
            "Gorged ancient effigy": (18781, catalog.EFFIGY_ASSET_PATH),
            "Dragonkin lamp": (18782, catalog.LAMP_ASSET_PATH),
        }
        for name, (item_id, asset_path) in expected.items():
            with self.subTest(name=name):
                self.assertEqual(len(by_key[name]), 1, "no duplicate definition")
                item = by_key[name][0]
                self.assertEqual(item.source_item_id, item_id)
                self.assertEqual(item.asset_path, asset_path)
                self.assertTrue(os.path.exists(item.asset_path))
                self.assertFalse(item.stackable)
                self.assertFalse(item.tradeable)
                self.assertIsNone(item.equipment_slot)
                self.assertIn("oldid", item.source)
                self.assertEqual(item.base_exp, 0.0, "stage XP is not generic training XP")

    def test_existing_starved_definition_keeps_its_id_and_position(self):
        ids = [item.id for item in ITEM_DEFINITIONS]
        self.assertEqual(ids.count("material_starved_ancient_effigy"), 1)
        starved_at = ids.index("material_starved_ancient_effigy")
        self.assertLess(starved_at, ids.index("material_nourished_ancient_effigy"))
        self.assertEqual(
            ids[-4:],
            [
                "material_nourished_ancient_effigy",
                "material_sated_ancient_effigy",
                "material_gorged_ancient_effigy",
                "material_dragonkin_lamp",
            ],
        )


class AssetAndEvidenceTest(unittest.TestCase):
    def test_both_images_are_the_verified_originals(self):
        self.assertEqual(_sha256(catalog.EFFIGY_ASSET_PATH), "c9440cab86a55e6169c9f6bf26c8220b96ff48b8451d2a3e4bd25217f7d564f2")
        self.assertEqual(_sha256(catalog.LAMP_ASSET_PATH), "f99260fb6c82e144c2179d62465804d3193e3a37838b81d025acd65c98caf522")
        self.assertEqual(catalog.EFFIGY_ASSET_SHA256, _sha256(catalog.EFFIGY_ASSET_PATH))
        self.assertEqual(catalog.LAMP_ASSET_SHA256, _sha256(catalog.LAMP_ASSET_PATH))

    def test_provenance_binds_every_stage_and_the_lamp(self):
        with open(os.path.join(_PACKAGE, "assets", "provenance.json"), encoding="utf-8") as handle:
            manifest = json.load(handle)
        by_id = {row["item_id"]: row for row in manifest}
        self.assertEqual(sorted(by_id), [18778, 18779, 18780, 18781, 18782])
        for item_id in catalog.STAGE_ITEM_IDS:
            asset = by_id[item_id]["asset"]
            self.assertEqual(asset["timestamp"], "2011-11-17T09:49:30Z")
            self.assertEqual(asset["sha256"], catalog.EFFIGY_ASSET_SHA256)
            self.assertIn("period_image_binding", by_id[item_id])
        lamp = by_id[18782]["asset"]
        self.assertEqual(lamp["timestamp"], "2011-11-20T06:50:54Z")
        self.assertEqual(lamp["sha256"], catalog.LAMP_ASSET_SHA256)

    def test_source_rows_quote_the_copied_evidence_literally(self):
        with open(os.path.join(catalog.EVIDENCE_DIR, "source-lines.md"), encoding="utf-8") as handle:
            source_lines = handle.read()
        with open(os.path.join(catalog.EVIDENCE_DIR, "source-register.json"), encoding="utf-8") as handle:
            register = json.load(handle)
        self.assertTrue(catalog.EVIDENCE_ORIGINAL_ROOT.endswith("1520-ancient-effigies-own-level-progression"))
        for source in catalog.SOURCES:
            with self.subTest(source=source.source_id):
                entry = register[source.source_id]
                self.assertEqual(source.saved_path, entry["saved"])
                self.assertEqual(source.sha256, entry["sha256"])
                self.assertEqual(source.timestamp_utc, entry["timestamp"])
                self.assertEqual(source.url, entry["url"])
                for number, text in source.lines:
                    self.assertIn(f"{number}: {text}", source_lines)


class PlaceholderTest(unittest.TestCase):
    def test_weights_are_marked_and_registered(self):
        self.assertEqual(requests.INITIAL_PAIR_WEIGHTS, (1, 1, 1, 1, 1, 1, 1, 1))
        self.assertEqual(requests.NEXT_PAIR_WEIGHTS, (1, 1, 1, 1, 1, 1, 1))
        with open(requests.__file__, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        initial = lines.index("INITIAL_PAIR_WEIGHTS = (1, 1, 1, 1, 1, 1, 1, 1)")
        following = lines.index("NEXT_PAIR_WEIGHTS = (1, 1, 1, 1, 1, 1, 1)")
        self.assertTrue(lines[initial - 1].startswith("# PLACEHOLDER(ancient_effigies.initial_pair_weights): "))
        self.assertTrue(lines[following - 1].startswith("# PLACEHOLDER(ancient_effigies.next_pair_weights): "))
        with open(os.path.join(_ROOT, "memory-bank", "placeholder-values.md"), encoding="utf-8") as handle:
            register = handle.read()
        for marker in ("ancient_effigies.initial_pair_weights", "ancient_effigies.next_pair_weights"):
            rows = [line for line in register.splitlines() if line.startswith(f"| `{marker}` |")]
            self.assertEqual(len(rows), 1, marker)
            self.assertIn("2026-10-24", rows[0])
            self.assertIn("pre-2012-11-20", rows[0])


if __name__ == "__main__":
    unittest.main()
