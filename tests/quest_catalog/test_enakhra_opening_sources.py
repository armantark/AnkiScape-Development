"""Offline source qualification, icons, truthful journal and durable custody."""

import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import struct
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, QUEST_DATA, QUEST_ITEM_IMAGES, ORE_IMAGES
from ankiscape.data.quest.enakhra_opening import (
    QUEST_ID, MASS_KEY, SANDSTONE, BLOCK_ID, BLOCK, BASE_ID, BASE, CHISEL_ID, COAL_ID,
    FLAT_GROUND_ID, ENAKHRA_OPENING_ITEMS, SOURCES, SOURCE_CUTOFF, TRANSACTION_SOURCES,
    RETAINED_BINDINGS, OWNER_DECISIONS, QUALIFICATION_NOTES, SPLIT_OUTPUTS,
    SPLIT_ADDITIONAL_XP, CHISEL_ADDITIONAL_XP, PROOFS, NOTICES,
)
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure
from ankiscape.logic_pure.quest.enakhra import (
    enakhra_opening_phase_pure, enakhra_opening_next_action_pure, migrate_enakhra_opening_state,
    LEGACY_JOURNAL,
)
from tests.quest_catalog.test_enakhra_opening import _player, _route, _reload, _progress

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "data/quest/enakhra_assets"
EXPECTED_SOURCE_HASHES = {
    "W1": "8e38947f97cd8d94b2446d3280f6438fa7a355d6aa05d6a921867d925328d2af",
    "A1": "b1993f2098788a804d423aaec1791dfc0a037e3e3958f87f609451194bd961f0",
    "W2": "d06babba0f7e7fa9386fae5363c94a27788dada2500c04a4cb381f41db9cc7c0",
    "W3": "8f0443ceb6a765d121c648871cface311af7d8b7d76ae3785a8887e2c64744f0",
    "W4": "e50a402fa71b141975db5f2c90721d1ddfa526e90d60622dcc562cb8924c28bc",
    "W5": "340b0e30355790d0b1bee40787034ff63ec1d5954bdeb7bf7729bfd5418eccbe",
    "D1": "77a3bc5489edbff215bf74856e5ebddc73edb475c9e6562fd0996ecd0996103c",
    "D2": "e44bfb1ec2da2c7a2286fda08180baee815d9148f56e74e614c11694b802a38f",
    "D3": "ee961adb7d51f3a5105ebe62b852f319f191433cfd9bc7b89bce1d8c36b975ad",
    "D4": "a346b7cd9c6d4c80d6dcc9d5d4996ccdca3ffa59849f74d3da5cba5c2b9aa9ea",
}
ICON_EXPECTATIONS = (
    (BLOCK, "sandstone_32kg.png", (22, 32), "2011-11-28T04:56:48Z",
     "aa5c5dbe949a45096e2026d2273fdcba0c1fb8de0c3a104746b0d6eb947456a6",
     "212c4b77437b0e0654688bd8d628b7a220c33eb2",
     "https://runescape.wiki/images/archive/20140502064153%21Sandstone_%2832kg%29.png?4ae18"),
    (BASE, "sandstone_base.png", (18, 30), "2011-11-28T04:57:09Z",
     "1059362d0467e2b4827765d163e400305a13e3e99fe2b0598bcc21ec0430e075",
     "f0616a40c74786d5f10075b6325d345ad123ff81",
     "https://runescape.wiki/images/archive/20140502064146%21Sandstone_base.png?1e683"),
)


def _journal(player):
    return quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)


class EnakhraSourcesTest(unittest.TestCase):
    def test_metadata_preserves_cutoff_literal_units_and_reconstruction_limits(self):
        self.assertEqual({row["id"]: row["sha256"] for row in SOURCES}, EXPECTED_SOURCE_HASHES)
        cutoff = datetime.fromisoformat(SOURCE_CUTOFF)
        for source in SOURCES:
            self.assertTrue(source["title"])
            self.assertTrue(source["url"])
            self.assertTrue(source["revision"])
            self.assertTrue(source["body_path"].endswith(Path(source["file"]).name))
            self.assertTrue(source["excerpts"])
            self.assertEqual(datetime.fromisoformat(source["timestamp_utc"]) < cutoff, source["historical_witness"])
        by_id = {row["id"]: row for row in SOURCES}
        self.assertIn("5K", dict(by_id["A1"]["excerpts"])[264])
        self.assertIn("mine with 45 mining", dict(by_id["W1"]["excerpts"])[38])
        self.assertIn("Talk to him again", dict(by_id["W1"]["excerpts"])[60])
        self.assertEqual(set(TRANSACTION_SOURCES), set(PROOFS))
        for action in PROOFS:
            self.assertTrue(TRANSACTION_SOURCES[action])
        self.assertTrue(all("canonical_path" in by_id[key] for key in ("D1", "D2", "D3", "D4")))
        notes = " ".join(QUALIFICATION_NOTES)
        for text in ("not independent historical", "free slots", "historical zero", "further talk", "replacement", "Mining 35"):
            self.assertIn(text, notes)
        self.assertEqual(RETAINED_BINDINGS[-1]["lineage"]["baseline_world_commit"], "f48cfc6b67af91ae4af175e6f672da28aa4f371b")
        self.assertIn("no quest behavior was recovered", RETAINED_BINDINGS[-1]["lineage"]["evidence_boundaries"]["game_main_revision_667"])
        self.assertEqual(len(RETAINED_BINDINGS), 3)
        self.assertEqual(OWNER_DECISIONS[-1][0], "2026-10-24 09:44 PDT")

    def test_five_provisional_values_are_marked_and_registered_with_replacement_evidence(self):
        register = (ROOT / "memory-bank/placeholder-values.md").read_text()
        source = (ROOT / "data/quest/enakhra_opening.py").read_text()
        values = {"split_10kg_outputs": "((6975, 2),)", "split_5kg_outputs": "((6973, 2), (6971, 1))",
                  "split_2kg_outputs": "((6971, 2),)", "split_xp": "0.0 additional XP", "chisel_xp": "0.0 additional XP"}
        for key, value in values.items():
            identifier = "quests.enakhras_lament." + key
            self.assertIn("# PLACEHOLDER(" + identifier + ")", source)
            row, = [line for line in register.splitlines() if "`" + identifier + "`" in line]
            self.assertIn(value, row)
            self.assertIn("2026-10-24", row)
            self.assertIn("independently qualified pre-cutoff", row)
            self.assertIn("Supplying reconstruction", row)
        self.assertEqual((SPLIT_ADDITIONAL_XP, CHISEL_ADDITIONAL_XP), (0.0, 0.0))
        self.assertEqual(SPLIT_OUTPUTS, {6977: ((6975, 2),), 6975: ((6973, 2), (6971, 1)), 6973: ((6971, 2),)})

    def test_numeric_identities_flags_and_distinct_registry_bindings(self):
        self.assertEqual(SANDSTONE, {6971: ("Sandstone (1kg)", 1), 6973: ("Sandstone (2kg)", 2),
                                     6975: ("Sandstone (5kg)", 5), 6977: ("Sandstone (10kg)", 10)})
        self.assertEqual((CHISEL_ID, COAL_ID, FLAT_GROUND_ID), (1755, 453, 10954))
        items = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for name, item_id in ((BLOCK, BLOCK_ID), (BASE, BASE_ID)):
            spec = ENAKHRA_OPENING_ITEMS[name]
            item = items[name]
            self.assertEqual(spec["category"], "material")
            self.assertFalse(spec["stackable"])
            self.assertFalse(spec["tradeable"])
            self.assertNotIn("equipment_slot", spec)
            self.assertEqual(item.source_item_id, item_id)
            self.assertIsNone(item.equipment_slot)
            self.assertEqual(item.category, "material")
            self.assertFalse(item.stackable)
            self.assertFalse(item.tradeable)
            self.assertIn("oldid=", spec["source"])
            self.assertNotIn(name, QUEST_DATA[QUEST_ID]["rewards"])
        self.assertEqual((BLOCK_ID, BASE_ID), (6986, 6988))
        self.assertNotEqual(items[BLOCK].id, items[BASE].id)

    def test_exact_historical_pngs_dimensions_receipts_and_late_asset_override(self):
        provenance = json.loads((ASSETS / "provenance.json").read_text())
        items = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for name, filename, dimensions, timestamp, sha256, sha1, url in ICON_EXPECTATIONS:
            data = (ASSETS / filename).read_bytes()
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", data[16:24]), dimensions)
            self.assertEqual(hashlib.sha256(data).hexdigest(), sha256)
            self.assertEqual(hashlib.sha1(data).hexdigest(), sha1)
            record = provenance[filename]
            self.assertEqual(record["dimensions"], list(dimensions))
            self.assertEqual(record["upload_timestamp_utc"], timestamp)
            self.assertEqual(record["retrieval_url"], url)
            self.assertEqual(record["sha256"], sha256)
            self.assertEqual(record["sha1"], sha1)
            self.assertIn("File:Sandstone", record["file_page_url"])
            self.assertTrue(record["receipt_reference"].endswith("icon-download-receipt.json"))
            self.assertIn("icon-history.json", record["history_receipt_reference"])
            self.assertEqual(Path(QUEST_ITEM_IMAGES[name]), ASSETS / filename)
            self.assertEqual(Path(items[name].asset_path), ASSETS / filename)
        for size in (1, 2, 5, 10):
            name = f"Sandstone ({size}kg)"
            self.assertEqual(Path(ORE_IMAGES[name]).name, f"sandstone_{size}kg.png")
            self.assertTrue(Path(ORE_IMAGES[name]).is_file())
            self.assertEqual(items[name].asset_path, ORE_IMAGES[name])


class EnakhraJournalAndMigrationTest(unittest.TestCase):
    def test_every_phase_projects_without_mutation_and_only_records_performed_deeds(self):
        snapshots = _route(_player())
        for player in snapshots:
            before = copy.deepcopy(player)
            row = _journal(player)[0]
            self.assertEqual(player, before)
            lines = row["lines"]
            text = " ".join(lines)
            self.assertNotIn("I have mined", text)
            self.assertNotIn("take one from the rock", text)
            for action in ("offer_help", "chisel_base", "talk_after_base", "place_base"):
                self.assertEqual(NOTICES[action] in lines, PROOFS[action] in player["quest_action_proofs"])
            self.assertIn(f"Sandstone given to Lazim: {player[MASS_KEY]}/32 kg.", lines)
            if row["current"]:
                self.assertEqual(lines[:3], QUEST_DATA[QUEST_ID]["journal_stages"][1][:3])
                self.assertIn("Supply 32 kg of sandstone to Lazim. Bring sandstone, or mine it in the quarry at Mining 35.", lines)
                self.assertIn("Mine 1 coal if you did not bring one; it is needed later.", lines)
            else:
                self.assertTrue(row["completed"])
                self.assertNotIn("Bring sandstone", text)
                self.assertNotIn("Mine 1 coal", text)
                self.assertNotIn("Supply 32 kg", text)
                self.assertNotIn("Before you begin", text)
        for stage in ("offer_help", "supply", "chisel_base", "talk_after_base", "place_base"):
            player = next(p for p in snapshots if enakhra_opening_phase_pure(p) == stage)
            self.assertIn({"offer_help": "Offer to help Lazim.", "supply": "Supply the remaining sandstone to Lazim.",
                           "chisel_base": "Chisel Lazim's 32kg sandstone block into a base.",
                           "talk_after_base": "Talk to Lazim again about the sandstone base.",
                           "place_base": "Place the base on the flat ground beside Lazim."}[stage], _journal(player)[0]["lines"])

    def test_mining_sentences_require_genuine_global_proofs_without_attributing_stock(self):
        player = _route(_player())[-1]
        for proof, sentence in (("Mine sandstone", "I have mined sandstone."), ("Mine coal", "I have mined coal.")):
            player["quest_action_proofs"].append(proof)
            self.assertIn(sentence, _journal(player)[0]["lines"])
        text = " ".join(_journal(player)[0]["lines"])
        self.assertNotIn("mined 32", text)
        self.assertNotIn("Gave Lazim", text)
        self.assertIn("Sandstone given to Lazim: 32/32 kg.", text)

    def test_neutral_legacy_later_and_completed_rows_never_backfill(self):
        for progress, completed in ((2, False), (5, False), (7, True)):
            player = _player(progress, inventory={BLOCK: 1, BASE: 1})
            player["quests"][QUEST_ID]["completed"] = completed
            before = copy.deepcopy(player)
            row = _journal(player)[0]
            self.assertEqual(row, dict(stage=1, current=False, completed=False, lines=LEGACY_JOURNAL))
            self.assertEqual(player, before)
            loaded = _reload(player)
            for key in ("inventory", "quests", "quest_points", "quest_action_proofs"):
                self.assertEqual(loaded[key], before[key] if key != "inventory" else _reload(before)[key])
            self.assertIsNone(enakhra_opening_next_action_pure(loaded))
            later = _journal(loaded)[1:]
            for row in later:
                self.assertEqual(row["lines"], QUEST_DATA[QUEST_ID]["journal_stages"][row["stage"]])

    def test_json_reload_after_every_action_preserves_custody_proofs_and_prevents_duplicates(self):
        snapshots = _route(_player(inventory={"Sandstone (10kg)": 4}))
        for index, player in enumerate(snapshots[1:], 1):
            loaded = _reload(player)
            self.assertEqual(loaded[MASS_KEY], player[MASS_KEY])
            self.assertEqual(loaded["quests"], player["quests"])
            self.assertEqual(loaded["quest_action_proofs"], player["quest_action_proofs"])
            self.assertEqual(_journal(loaded), _journal(player))
            for name in (*[name for name, _ in SANDSTONE.values()], BLOCK, BASE, "Chisel"):
                self.assertEqual(loaded["inventory"].get(name, 0), player["inventory"].get(name, 0))
            self.assertEqual(_reload(loaded), loaded)
            if index + 1 < len(snapshots):
                replayed, ok, _ = _progress(loaded)
                expected = snapshots[index + 1]
                self.assertTrue(ok)
                self.assertEqual(replayed[MASS_KEY], expected[MASS_KEY])
                self.assertEqual(replayed["quest_action_proofs"], expected["quest_action_proofs"])
                self.assertEqual(replayed["inventory"].get(BLOCK, 0), expected["inventory"].get(BLOCK, 0))
                self.assertEqual(replayed["inventory"].get(BASE, 0), expected["inventory"].get(BASE, 0))

    def test_mass_sanitation_is_unconditional_additive_and_grants_nothing(self):
        for raw in (False, True, -1, 33, "32", 12.5, [], {}, None):
            player = _player()
            player[MASS_KEY] = raw
            before = copy.deepcopy(player)
            migrate_enakhra_opening_state(player)
            self.assertEqual(player, dict(before, **{MASS_KEY: 0}))
            loaded = _reload(before)
            self.assertEqual(loaded[MASS_KEY], 0)
            self.assertEqual(loaded["quest_action_proofs"], [])
            self.assertEqual(loaded["quests"], before["quests"])
            self.assertEqual(loaded["inventory"].get(BLOCK, 0), 0)
            self.assertEqual(loaded["inventory"].get(BASE, 0), 0)
        for raw in range(33):
            player = _player()
            player[MASS_KEY] = raw
            self.assertEqual(_reload(player)[MASS_KEY], raw)
        player = _player()
        del player[MASS_KEY]
        self.assertEqual(_reload(player)[MASS_KEY], 0)
