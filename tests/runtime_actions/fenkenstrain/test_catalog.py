"""Stable identities, retained stage boundary and reused provenanced artwork."""
import json
from pathlib import Path
import unittest

from . import support as s
from ankiscape.core.constants_parts.skill_assets import MAGIC_SPELL_IMAGES
from ankiscape.core.tool_belt import QUEST_STAGES_NEEDING_HELD_TOOLS
from ankiscape.data.magic_data import MAGIC_TARGETS
from ankiscape.data.quest.stage_overrides.members.later.creature_of_fenkenstrain import (
    CREATURE_OF_FENKENSTRAIN_ITEM_FRAGMENT,
    CREATURE_OF_FENKENSTRAIN_STAGE_ADDITIONS,
    CREATURE_OF_FENKENSTRAIN_STAGE_TWO_TRANSACTION,
)
from ankiscape.data.shop_data import SHOP_VENDOR_ACTIONS, SHOP_COVERAGE_SUMMARY, SHOP_EXTRA_ITEM_DATA
from tests.reachability.live_report import live_reachability_report
from tests.runtime_actions.test_fenkenstrain_opening import OPENING_ACTIONS


class CatalogTest(unittest.TestCase):
    def test_exact_item_identities_flags_and_sources(self):
        definitions = {item.storage_key: item for item in s.ITEM_DEFINITIONS}
        oldids = (6547064, 6174247, 6130186, 6074919, 5691056)
        for (name, item_id), oldid in zip(s.STAGE_ITEM_IDS.items(), oldids):
            with self.subTest(item=name):
                meta = CREATURE_OF_FENKENSTRAIN_ITEM_FRAGMENT[name]
                self.assertEqual(meta["item_id"], item_id)
                self.assertEqual((meta["category"], meta["members"], meta["equipable"], meta["tradeable"], meta["stackable"]),
                                 ("material", True, False, False, False))
                self.assertEqual(set(meta), {"item_id", "category", "members", "equipable", "tradeable", "stackable", "source"})
                self.assertIn(f"oldid={oldid}", meta["source"])
                self.assertIn("build-727/cache-309", meta["source"])
                self.assertEqual((definitions[name].source_item_id, definitions[name].tradeable, definitions[name].stackable),
                                 (item_id, False, False))
        self.assertEqual(definitions["Spade"].source_item_id, 952)
        self.assertNotIn(4198, {item.source_item_id for item in s.ITEM_DEFINITIONS})
        self.assertEqual(SHOP_EXTRA_ITEM_DATA["Pickled brain"]["source_item_id"], 4199)

    def test_opening_journal_stage_count_and_stage_three_stay_intact(self):
        quest = s.QUEST_DATA[s.QUEST_ID]
        opening = next(row for row in quest["stage_requirements"] if row["stage"] == 1)
        self.assertEqual(tuple(opening["auto_actions"]), OPENING_ACTIONS)
        self.assertEqual(quest["stages"], 6)
        # The retained journal is an unchanged catalog input, not rewritten by this slice.
        from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
        original = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == s.QUEST_ID)
        self.assertEqual(quest["journal_stages"], {row["stage"]: tuple(row["journal"]) for row in original["journal_stages"]})
        stage_three = [row for row in quest["stage_requirements"] if row["stage"] == 3]
        self.assertIn("Complete Creature of Fenkenstrain stage 3 objective", stage_three[0]["required_actions"])
        self.assertEqual(QUEST_STAGES_NEEDING_HELD_TOOLS[(s.QUEST_ID, 2)], ("Spade",))
        self.assertNotIn((s.QUEST_ID, 1), QUEST_STAGES_NEEDING_HELD_TOOLS)
        self.assertTrue(set(s.STAGE_ITEM_IDS).isdisjoint(quest["rewards"]))

    def test_stage_net_products_and_reachable_routes(self):
        stage = CREATURE_OF_FENKENSTRAIN_STAGE_ADDITIONS[0]
        self.assertEqual(stage.description, "Dig up the Gardener Ghost's head and combine the castle bookcase amulets.")
        self.assertEqual(dict(stage.required_inventory), {"Spade": 1, "Pickled brain": 1})
        self.assertEqual(dict(stage.produced_inventory), s.STAGE_OUTPUTS)
        self.assertEqual(stage.auto_actions, s.STAGE_TWO_ACTIONS)
        self.assertFalse(any((stage.consumed_inventory, stage.required_tools, stage.variant, stage.required_routes,
                              stage.required_skills, stage.combat_encounters, stage.repeatable_until_consumed)))
        self.assertIn("AnkiScape stage boundary", stage.source)
        report = live_reachability_report()
        for name in s.STAGE_OUTPUTS:
            self.assertEqual(report["routes"][name], f"quest-stage:{s.QUEST_ID}:2")
        self.assertEqual(report["routes"]["Pickled brain"], f"Magic:{s.BRAIN_CAST}")
        self.assertNotIn(f"Shop vendor:{s.ROAVAR}", {row["id"] for row in report["unresolved_actions"]})
        self.assertEqual(len(CREATURE_OF_FENKENSTRAIN_STAGE_TWO_TRANSACTION), 5)
        self.assertEqual(SHOP_COVERAGE_SUMMARY["vendor_action_count"], 5)
        self.assertEqual([rule["quest_id"] for rule in SHOP_VENDOR_ACTIONS[s.ROAVAR]["access"]["rules"]],
                         ["priest_in_peril", s.QUEST_ID])
        self.assertIn("AnkiScape abstraction", SHOP_VENDOR_ACTIONS[s.ROAVAR]["source"])

    def test_spell_retains_telegrab_values_and_icon_provenance(self):
        base, brain = MAGIC_TARGETS["telegrab_wine_of_zamorak"], MAGIC_TARGETS[s.BRAIN_CAST]
        changed = {key for key in base if base[key] != brain[key]}
        self.assertEqual(changed, {"id", "display_name", "outputs", "source"})
        self.assertEqual((brain["display_name"], brain["spellbook"], brain["group"], brain["level"], brain["exp"], brain["action"]),
                         ("Telegrab Pickled brain", "standard", "Pure casts", 33, 43, "produce"))
        self.assertEqual(brain["outputs"], {"Pickled brain": 1})
        self.assertEqual(brain["rune_cost"], {"Air rune": 1, "Law rune": 1})
        for oldid in (6174247, 6535792, 6587753):
            self.assertIn(str(oldid), brain["source"])
        self.assertEqual(MAGIC_SPELL_IMAGES[s.BRAIN_CAST], MAGIC_SPELL_IMAGES["telegrab_wine_of_zamorak"])
        root = Path(__file__).resolve().parents[3]
        icon = Path(MAGIC_SPELL_IMAGES[s.BRAIN_CAST])
        self.assertTrue(icon.is_file())
        provenance = json.loads((root / "assets_provenance.json").read_text())
        self.assertLessEqual(provenance[str(icon.relative_to(root))]["timestamp"], "2012-11-20T23:59:59Z")
