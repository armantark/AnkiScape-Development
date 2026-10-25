"""Opening data and preservation of the existing later quest contract."""

import copy
import hashlib
import json
from pathlib import Path
import struct
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, QUEST_DATA, QUEST_ITEM_IMAGES
from ankiscape.data.quest.contract import QuestStage, QuestStageRequirement
from ankiscape.data.quest.elemental_workshop_iii import (
    QUEST_ID, RAGGED_BOOK, ACQUIRE_PROOF, READ_PROOF, ACQUIRE_EVENT, READ_EVENT,
    OPENING_JOURNAL, OPENING_SOURCE, PREPARATION_SOURCE, PREPARATION_JOURNAL,
    RAGGED_BOOK_ITEMS, compose_opening,
)
from ankiscape.data.quest.reward_items import quest_reward_items_as_dict
from ankiscape.data.quest_action_proof_data import QUEST_ACTION_PROOF_RULES
from ankiscape.logic_pure.quest_action_proofs import quest_action_proofs_after_event_pure


class OpeningCatalogTest(unittest.TestCase):
    def test_exact_opening_requirement_and_journal(self):
        quest = QUEST_DATA[QUEST_ID]
        row = quest["stage_requirements"][0]
        self.assertEqual(row, dict(
            stage=1, description="Search the bookcase in Seers' Village chapel and read the Ragged book.",
            variant="", required_inventory={}, required_inventory_options=(), consumed_inventory={},
            consumed_inventory_options=(), produced_inventory={}, repeatable_until_consumed=False,
            required_skills=(), required_tools={}, required_actions=(READ_PROOF,), auto_actions=(),
            required_routes=(), combat_encounters=(), source=OPENING_SOURCE,
        ))
        self.assertIn("6448817:53", row["source"])
        self.assertIn("20120825005143", row["source"])
        self.assertEqual(quest["journal_stages"][1], (
            "Search the bookcase in Seers' Village chapel to obtain the Ragged book, then read it.",
        ))
        self.assertEqual(quest["journal_stages"][1], OPENING_JOURNAL)
        self.assertEqual(quest["stages"], 8)

    def test_exact_pending_preparation_instructions(self):
        self.assertEqual(QUEST_DATA[QUEST_ID]["journal_stages"][2], (
            "Next, take the Ragged book into the workshop through the odd-looking wall in the anvil house.",
            "Workshop access needs the Battered key, a Knife to recover it, or a Steel key ring containing that key.",
            "For the later preparation, use a Pickaxe and Hammer, obtain 3 elemental ores, and use 12 Coal to smelt 3 elemental bars. A toolbelt Hammer works.",
            "After reading the Ragged book, use one Soft clay with it to make a Key mould. Use one elemental bar with the mould to make the Ragged elemental key.",
            "Prime the remaining two bars; do not make mind bars. Unlock the Body door before working the puzzle.",
        ))
        self.assertEqual(QUEST_DATA[QUEST_ID]["journal_stages"][2], PREPARATION_JOURNAL)
        self.assertIn("before entry", PREPARATION_SOURCE)
        self.assertIn("after workshop entry", PREPARATION_SOURCE)

    def test_later_requirements_rewards_and_prerequisites_match_baseline(self):
        baseline = json.loads(Path(__file__).with_name("later_contract.json").read_text())
        quest = json.loads(json.dumps(QUEST_DATA[QUEST_ID]))
        self.assertEqual(quest["stage_requirements"][1:], baseline.pop("stage_requirements"))
        for key, value in baseline.items():
            self.assertEqual(quest[key], value, key)
        encounters = [e for r in quest["stage_requirements"] for e in r["combat_encounters"]]
        self.assertEqual([(e["display_name"], e["level"], e["quantity"]) for e in encounters],
                         [("Earth Elemental", 35, 3)])

    def test_composition_is_read_only_idempotent_and_preserves_row_identity(self):
        requirements = (QuestStageRequirement(1, "old"), QuestStageRequirement(6, "later"))
        journal = (QuestStage(1, ("old",)), QuestStage(2, ("old",)), QuestStage(3, ("later",)))
        before = copy.deepcopy((requirements, journal))
        composed = compose_opening(QUEST_ID, requirements, journal)
        self.assertEqual((requirements, journal), before)
        self.assertIs(composed[0][1], requirements[1])
        self.assertIs(composed[1][2], journal[2])
        self.assertEqual(compose_opening(QUEST_ID, *composed), composed)
        self.assertEqual(compose_opening("elemental_workshop_ii", requirements, journal), before)

    def test_only_the_two_service_events_emit_the_new_proofs(self):
        for event, proof in ((ACQUIRE_EVENT, ACQUIRE_PROOF), (READ_EVENT, READ_PROOF)):
            self.assertEqual(QUEST_ACTION_PROOF_RULES[event], ((), (proof,)))
            self.assertEqual(quest_action_proofs_after_event_pure([], *event), [proof])
        for event in (("quest", QUEST_ID), ("quest_stage", f"{QUEST_ID}:Find and read the Ragged book in the workshop")):
            self.assertEqual(quest_action_proofs_after_event_pure([], *event), [])

    def test_registered_exact_book_metadata_and_historical_asset(self):
        metadata = quest_reward_items_as_dict()[RAGGED_BOOK]
        self.assertEqual(metadata, RAGGED_BOOK_ITEMS[RAGGED_BOOK])
        self.assertEqual((metadata["item_id"], metadata["model_id"]), (18685, 57485))
        self.assertEqual(metadata["category"], "material")
        self.assertIs(metadata["stackable"], False)
        self.assertIs(metadata["tradeable"], False)
        self.assertEqual(metadata["inventory_options"], ("Read", None, None, None, "Destroy"))
        item = next(item for item in ITEM_DEFINITIONS if item.storage_key == RAGGED_BOOK)
        self.assertEqual(item.source_item_id, 18685)
        self.assertFalse(item.tradeable)
        self.assertFalse(item.stackable)
        self.assertEqual(item.asset_path, QUEST_ITEM_IMAGES[RAGGED_BOOK])
        path = Path(QUEST_ITEM_IMAGES[RAGGED_BOOK])
        self.assertEqual(path, Path(__file__).resolve().parents[2] / "data/quest/assets/ragged_book.png")
        body = path.read_bytes()
        self.assertEqual(len(body), 1571)
        self.assertEqual(struct.unpack(">II", body[16:24]), (27, 29))
        self.assertEqual(hashlib.sha256(body).hexdigest(),
                         "3338ce6ee9e4dd732f0796cd61d605d330f291c710dfab5f008c966853e2e192")
        provenance = json.loads(path.with_suffix(".provenance.json").read_text())
        self.assertEqual(provenance["saved_path"], "data/quest/assets/ragged_book.png")
        self.assertEqual(provenance["timestamp"], "2010-05-25T17:01:07Z")
        self.assertEqual(provenance["sha1"], "8f638edba734c9165dd6338f52378790aa76f46f")
        self.assertEqual(provenance["license_string"], "not stated by inspected imageinfo; Jagex game image")

    def test_source_packet_retains_conflicts_and_unsupported_claims(self):
        path = Path(__file__).resolve().parents[2] / "data/quest/elemental_workshop_iii_sources.json"
        packet = json.loads(path.read_text())
        self.assertEqual(packet["source_index"]["TI"]["utc_date"],
                         "2012-08-25T00:51:43Z; guide last updated 2012-06-25 (time not stated)")
        records = {r["id"]: r for r in packet["assertions"]}
        for key in ("G3-tradeability-conflict", "G3-later-slashed-conflict", "G2-after-opening"):
            self.assertIn(key, records)
        opening = records["G1-search"]["citations"][0]["original_lines"]
        self.assertEqual(opening[-1]["number"], 53)
        self.assertIn("Read the book.", opening[-1]["text"])
        self.assertIn("Hidden server read bits", packet["not_stated"])

    def test_workshop_ii_retains_exam_centre_hidden_scroll_and_beaten_book(self):
        row = QUEST_DATA["elemental_workshop_ii"]["stage_requirements"][0]
        self.assertEqual(row["auto_actions"], ("Find the Beaten book in the Exam Centre and read its hidden scroll",))
        self.assertEqual(row["produced_inventory"], {"Beaten book": 1})
        self.assertNotIn("Slashed book", row["produced_inventory"])
        self.assertFalse(any("slash" in a.lower() for a in row["auto_actions"]))
