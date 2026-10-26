import unittest
from unittest.mock import patch
import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core import constants
from ankiscape.core.constants import ITEM_DEFINITIONS, QUEST_DATA
from tools.audit_item_reachability import _claim_item_sources, _quest_stage_sources, build_reachability_report
from tests.reachability.live_report import live_reachability_report


class TestItemReachabilityAudit(unittest.TestCase):
    def test_wicked_hood_claim_is_reachable_after_rune_mysteries(self):
        report = live_reachability_report()

        self.assertEqual(report["routes"].get("Wicked hood"), "claim:wicked_hood")
        self.assertFalse(
            [
                row
                for row in report["blocked_quest_stage_products"]
                if row["quest_id"] == "rune_mysteries"
            ]
        )

    def test_lost_city_shamus_action_has_a_runtime_emitter(self):
        missing_actions = {
            action
            for row in live_reachability_report()["blocked_quest_stage_products"]
            if row["quest_id"] == "lost_city"
            for action in row["missing_required_actions"]
        }

        self.assertNotIn("Find Shamus in the Lumbridge Swamp tree", missing_actions)

    def test_waterfall_quest_dialogue_and_tomb_actions_have_runtime_emitters(self):
        missing_actions = {
            action
            for row in live_reachability_report()["blocked_quest_stage_products"]
            if row["quest_id"] == "waterfall_quest"
            for action in row["missing_required_actions"]
        }

        self.assertEqual(
            missing_actions,
            set(),
            "Waterfall Quest still blocks on a specific action",
        )

    def test_lost_tribe_has_no_blocked_stage_products(self):
        blocked_quest_ids = {
            row["quest_id"]
            for row in live_reachability_report()["blocked_quest_stage_products"]
        }

        self.assertNotIn("the_lost_tribe", blocked_quest_ids)

    def test_gertrudes_cat_dialogue_actions_have_runtime_emitters(self):
        missing_actions = {
            action
            for row in live_reachability_report()["blocked_quest_stage_products"]
            if row["quest_id"] == "gertrudes_cat"
            for action in row["missing_required_actions"]
        }

        self.assertEqual(
            missing_actions,
            set(),
            "Gertrude's Cat still blocks on a specific action",
        )

    def test_a_souls_bane_rage_action_has_a_runtime_emitter(self):
        missing_actions = {
            action
            for row in live_reachability_report()["blocked_quest_stage_products"]
            if row["quest_id"] == "a_souls_bane"
            for action in row["missing_required_actions"]
        }

        self.assertNotIn("Fill the rage meter with an anger weapon", missing_actions)

    def test_dealing_with_scabaras_bronze_action_has_a_runtime_emitter(self):
        missing_actions = {
            action
            for row in live_reachability_report()["blocked_quest_stage_products"]
            if row["quest_id"] == "dealing_with_scabaras"
            for action in row["missing_required_actions"]
        }

        self.assertNotIn(
            "Prepare bronze equipment for the High Priest's tests",
            missing_actions,
        )

    def test_diamond_in_the_rough_claim_items_require_reachable_quest_and_level_gates(self):
        report = live_reachability_report()

        self.assertEqual(
            {
                item: report["routes"].get(item)
                for item in ("Apmeken mask", "Ankh", "Scabaras mask", "Was")
            },
            {
                "Apmeken mask": "claim:diamond_in_the_rough_apmeken_tomb",
                "Ankh": "claim:diamond_in_the_rough_apmeken_tomb",
                "Scabaras mask": "claim:diamond_in_the_rough_scabaras_tomb",
                "Was": "claim:diamond_in_the_rough_scabaras_tomb",
            },
        )

    def test_the_golem_throne_claim_requires_reachable_chisel_and_hammer(self):
        claim_id = "the_golem_thammarons_throne_gems"
        claim_data = {claim_id: constants.CLAIM_DATA[claim_id]}
        args = (
            claim_data,
            {"the_golem"},
            {"Ruby", "Emerald", "Sapphire"},
            {"runecrafting": 1},
        )

        blocked_sources, blocked_counts = _claim_item_sources(
            *args,
            {"Chisel": 1},
            set(),
        )
        sources, counts = _claim_item_sources(
            *args,
            {"Chisel": 1, "Hammer": 1},
            set(),
        )

        self.assertEqual(blocked_sources, {})
        self.assertEqual(blocked_counts, {})
        self.assertEqual(
            sources,
            {
                "Ruby": {f"claim:{claim_id}"},
                "Emerald": {f"claim:{claim_id}"},
                "Sapphire": {f"claim:{claim_id}"},
            },
        )
        self.assertEqual(counts, {"Ruby": 2, "Emerald": 2, "Sapphire": 2})

    def test_unreachable_claim_level_does_not_seed_item(self):
        constructed_claim = {
            "unreachable_level_item": {
                "claim_type": "skill_reward",
                "items": (("Jade vine seed", 1),),
                "required_quest": "diamond_in_the_rough",
                "xp_amount": 1,
                "skill_options": ("mining",),
                "minimum_level": 100,
            },
        }

        with patch.dict(constants.CLAIM_DATA, constructed_claim):
            report = build_reachability_report()

        self.assertIsNone(report["routes"].get("Jade vine seed"))

    def test_lost_city_branch_and_cinnamon_require_the_real_quest_chain(self):
        registered_items = {
            definition.storage_key for definition in ITEM_DEFINITIONS
        }
        sources, _, action_completable = _quest_stage_sources(
            QUEST_DATA,
            registered_items,
        )
        report = live_reachability_report()

        # The stage actions are emitted now, so the branch is granted by
        # resolving Lost City stage 4 and Cinnamon's real grind resolves with it.
        self.assertNotIn("lost_city", action_completable)
        self.assertNotIn("Dramen branch", sources)
        self.assertEqual(report["routes"].get("Dramen branch"), "quest-stage:lost_city:4")
        self.assertEqual(report["routes"].get("Cinnamon"), "Utility:grind_dramen_branch")
        self.assertNotIn(
            "Utility:grind_dramen_branch",
            {action["id"] for action in report["unresolved_actions"]},
        )
