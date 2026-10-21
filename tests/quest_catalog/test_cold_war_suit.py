import copy
import json
import sys
import unittest
from itertools import product

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest.catalog import (
    _apply_stage_item_name_overrides,
    _catalog_stage_requirements,
)
from ankiscape.data.quest.serializers import _stage_requirement_dict
from ankiscape.data.quest.cold_war import COLD_WAR_SUIT_BACKFILL_KEY
from ankiscape.logic.cold_war_suit_logic import migrate_cold_war_suit_pure
from ankiscape.generated.item_values_generated import ITEM_VALUES_GENERATED
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic.bank_layout_logic import (
    bank_sections_pure,
    reconcile_bank_layout_for_player_pure,
)
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure,
    quest_current_stage_blockers_pure,
    quest_journal_rows_pure,
    quest_locked_reasons_pure,
    start_quest_pure,
)
from tests.reachability.live_report import live_reachability_report
from tests.test_combat_quest_gate import _answer_review
from tests.runtime_actions.test_cold_war_greeting import (
    PLAYER_KEY, RECOVERY_KEY, SKILL_KEY, review_session,
)
from tests.test_cold_war_greeting import GREETING, SAMPLER
from tests.test_storage_runtime import _LegacyTextCollection, _load_storage_module
from types import SimpleNamespace
from unittest.mock import patch


QUEST_ID = "cold_war"
BOOK_ACTION = "Receive the Clockwork book from Larry"
SUIT_ACTION = "Receive the Clockwork suit and test the penguin disguise with Larry"
RETIRED_ACTION = "Build the clockwork penguin on a crafting table 3"
GENERATED_QUEST = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)


def _player(stage=2):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for skill in GENERATED_QUEST["required_skills"]:
        player[f"{skill['skill_id']}_level"] = skill["level"]
    player["inventory"] = {}
    player["quest_action_proofs"] = []
    player["quests"][QUEST_ID] = {"started": True, "progress": stage, "completed": False}
    player["current_quest"] = QUEST_ID
    return player


def _advance(player):
    return apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)


class TestColdWarSuit(unittest.TestCase):
    def test_opening_reaches_suit_stage_without_crafting_supplies(self):
        player = _player(1)
        player["quests"][QUEST_ID] = {"started": False, "progress": 0, "completed": False}
        # The catalog normalizes the generated Steel nail name to Steel nails.
        player["inventory"] = {"Oak plank": 10, "Steel nails": 10, "Spade": 1}
        player, started = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(started)
        self.assertEqual(quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA), ())

        missing = copy.deepcopy(player)
        missing["inventory"]["Oak plank"] = 9
        blockers = quest_current_stage_blockers_pure(missing, QUEST_ID, QUEST_DATA)
        self.assertEqual([row["item_name"] for row in blockers], ["Oak plank"])
        blocked, progressed, completed = _advance(missing)
        self.assertFalse(progressed)
        self.assertFalse(completed)
        self.assertEqual(blocked, missing)
        self.assertEqual(blocked["quest_action_proofs"], [])
        self.assertEqual(blocked["inventory"].get("Clockwork suit", 0), 0)

        after, progressed, completed = _advance(player)
        self.assertTrue(progressed)
        self.assertFalse(completed)
        self.assertEqual(after["quests"][QUEST_ID]["progress"], 2)
        self.assertEqual(after["quest_action_proofs"], [BOOK_ACTION])
        # The original lookout supplies and tool were not consumed by this stage.
        self.assertEqual(after["inventory"], player["inventory"])
        self.assertNotIn("Clockwork book", after["inventory"])
        self.assertNotIn("Clockwork suit", after["inventory"])

    def test_stage_two_grants_one_suit_without_manufacture(self):
        sentinels = {"Plank": 7, "Silk": 8, "Steel bar": 9, "Clockwork": 10,
                     "Clockwork mechanism": 11}
        for inventory in ({}, sentinels, {**sentinels, "Clockwork suit": 2}):
            with self.subTest(inventory=inventory):
                player = _player()
                player["inventory"] = dict(inventory)
                player["crafting_exp"] = 123.0
                before = copy.deepcopy(player)
                self.assertEqual(quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA), ())
                after, progressed, completed = _advance(player)
                self.assertTrue(progressed)
                self.assertFalse(completed)
                self.assertEqual(after["quests"][QUEST_ID]["progress"], 3)
                self.assertEqual(after["inventory"], {**inventory, "Clockwork suit": inventory.get("Clockwork suit", 0) + 1})
                self.assertEqual(after["quest_action_proofs"], [SUIT_ACTION])
                self.assertNotIn(RETIRED_ACTION, after["quest_action_proofs"])
                self.assertEqual(after["crafting_exp"], player["crafting_exp"])
                self.assertEqual(player, before)

    def test_suit_grant_does_not_repeat(self):
        for prior_quantity in (0, 2):
            with self.subTest(prior_quantity=prior_quantity):
                player = _player()
                player["inventory"]["Clockwork suit"] = prior_quantity
                # Reopening at stage 2 must not grant until an eligible review.
                player = migrate_loaded_data(json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS)
                self.assertEqual(player["inventory"].get("Clockwork suit", 0), prior_quantity)
                self.assertEqual(player["quests"][QUEST_ID]["progress"], 2)
                after, progressed, _ = _advance(player)
                self.assertTrue(progressed)
                self.assertEqual(after["inventory"]["Clockwork suit"], prior_quantity + 1)
                after = migrate_loaded_data(json.loads(json.dumps(after)), ORE_DATA, ITEM_DEFINITIONS)
                reopened, started = start_quest_pure(after, QUEST_ID, QUEST_DATA)
                self.assertTrue(started)
                self.assertEqual(reopened["inventory"]["Clockwork suit"], prior_quantity + 1)
                for _ in range(2):
                    reopened, progressed, _ = _advance(reopened)
                    self.assertFalse(progressed)  # Stage 3 retains unrelated blockers.
                    self.assertEqual(reopened["inventory"]["Clockwork suit"], prior_quantity + 1)
                    self.assertEqual(reopened["quest_action_proofs"].count(SUIT_ACTION), 1)

        # Stage advancement owns the grant; an existing proof is not a grant ledger.
        player = _player()
        player["quest_action_proofs"] = [SUIT_ACTION]
        after, progressed, _ = _advance(player)
        self.assertTrue(progressed)
        self.assertEqual(after["inventory"]["Clockwork suit"], 1)
        self.assertEqual(after["quest_action_proofs"], [SUIT_ACTION])

        # Losing the Bank item after stage 2 must not trigger a replacement.
        after["inventory"].pop("Clockwork suit")
        loaded = migrate_loaded_data(json.loads(json.dumps(after)), ORE_DATA, ITEM_DEFINITIONS)
        unchanged, progressed, _ = _advance(loaded)
        self.assertFalse(progressed)
        self.assertEqual(unchanged["inventory"].get("Clockwork suit", 0), 0)
        self.assertEqual(unchanged["quests"][QUEST_ID]["progress"], 3)
        self.assertEqual(unchanged["quest_action_proofs"], [SUIT_ACTION])

        for stage in range(3, 8):
            with self.subTest(existing_save_stage=stage):
                player = _player(stage)
                if stage == 7:
                    player["quests"][QUEST_ID]["completed"] = True
                loaded = migrate_loaded_data(json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS)
                self.assertEqual(loaded["inventory"].get("Clockwork suit", 0), 1)
                self.assertIs(loaded["cold_war_suit_backfill_checked"], True)
                after, _, _ = _advance(loaded)
                self.assertEqual(after["inventory"].get("Clockwork suit", 0), 1)
                self.assertNotIn(SUIT_ACTION, after["quest_action_proofs"])

    def test_suit_registry_bank_and_reload(self):
        definitions = [item for item in ITEM_DEFINITIONS if item.storage_key == "Clockwork suit"]
        self.assertEqual(len(definitions), 1)
        item = definitions[0]
        self.assertEqual(item.id, "material_clockwork_suit")
        self.assertEqual(item.category, "material")
        self.assertIs(item.stackable, False)
        self.assertIs(item.tradeable, False)
        self.assertIsNone(item.source_item_id)
        self.assertIsNone(item.equipment_slot)
        self.assertIsNone(item.asset_path)
        self.assertEqual(ITEM_VALUES_GENERATED["Clockwork suit"], 1)
        for provenance in ("oldid=6424777", "OpenRS2 cache 544/build 742", "10595", "10596",
                           "owner decision 2026-10-20 19:00 PDT: combined bankable suit"):
            self.assertIn(provenance, item.source)

        player, progressed, _ = _advance(_player())
        self.assertTrue(progressed)
        player = reconcile_bank_layout_for_player_pure(player)
        sections = bank_sections_pure(player["bank_layout"], player["inventory"], "main", "manual",
                                      auto_categories=False, values=ITEM_VALUES_GENERATED)
        self.assertEqual([(row["name"], row["quantity"], row["value"])
                          for section in sections for row in section["items"]],
                         [("Clockwork suit", 1, 1)])
        loaded = migrate_loaded_data(json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(loaded["inventory"]["Clockwork suit"], 1)
        self.assertEqual(loaded["quests"][QUEST_ID]["progress"], 3)
        self.assertEqual(loaded["quest_action_proofs"], [SUIT_ACTION])
        self.assertEqual(loaded["bank_layout"]["items"]["Clockwork suit"],
                         player["bank_layout"]["items"]["Clockwork suit"])

    def test_disguise_never_requires_or_changes_equipment_or_suit(self):
        gear = {"weapon": "Bronze sword", "shield": "Wooden shield", "cape": "Red cape"}
        player = _player()
        player["equipment"] = dict(gear)
        player["carried_inventory"] = {"chicken": {"Lobster": 3}}
        after, progressed, _ = _advance(player)
        self.assertTrue(progressed)
        self.assertEqual(after["equipment"], gear)
        self.assertEqual(after["carried_inventory"], player["carried_inventory"])
        self.assertEqual(after["inventory"], {"Clockwork suit": 1})

        for stage in range(3, 7):
            with self.subTest(stage=stage):
                bare = _player(stage)
                blockers = quest_current_stage_blockers_pure(bare, QUEST_ID, QUEST_DATA)
                self.assertTrue(blockers)
                self.assertIn(f"Complete Cold War stage {stage} objective",
                              {row.get("action_id") for row in blockers})
                dressed = copy.deepcopy(bare)
                dressed["inventory"].update({"Clockwork suit": 2, "Clockwork book": 1})
                dressed["equipment"] = dict(gear)
                dressed["carried_inventory"] = {"chicken": {"Clockwork suit": 1, "Clockwork book": 1}}
                self.assertEqual(quest_current_stage_blockers_pure(dressed, QUEST_ID, QUEST_DATA), blockers)
                unchanged, progressed, _ = _advance(dressed)
                self.assertFalse(progressed)
                self.assertEqual(unchanged, dressed)

    def test_suit_is_reachable_from_stage_two_without_finishing_cold_war(self):
        report = live_reachability_report()

        self.assertEqual(report["routes"].get("Clockwork suit"), "quest-stage:cold_war:2")
        self.assertIn(SUIT_ACTION, report["earned_quest_action_proofs"])
        self.assertNotIn(RETIRED_ACTION, report["earned_quest_action_proofs"])
        self.assertFalse(any(
            "Clockwork suit" in row["products"]
            for row in report["blocked_quest_stage_products"]
        ))

    def test_activated_ring_still_advances_after_suit_grant(self):
        player, progressed, _ = _advance(_player())
        self.assertTrue(progressed)
        player["equipment"] = {"ring": "Ring of charos (a)"}
        player["quest_action_proofs"].append("Complete Cold War stage 3 objective")
        self.assertEqual(quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA), ())

        after, progressed, completed = _advance(player)

        self.assertTrue(progressed)
        self.assertFalse(completed)
        self.assertEqual(after["quests"][QUEST_ID]["progress"], 4)
        self.assertEqual(after["inventory"], {"Clockwork suit": 1})
        self.assertEqual(after["equipment"], player["equipment"])
        self.assertEqual(after["quest_action_proofs"].count(SUIT_ACTION), 1)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)

    def test_journal_and_unlocks_match_automatic_suit_flow(self):
        # Contract replacements are keyed by original paragraph indexes. All
        # surrounding prose (including greetings and passwords) must survive.
        edits = {
            (1, 5): (
                ("by creating a penguin clockwork suit.", "by using a penguin clockwork suit."),
                ("He gives you a book filled with instructions on how to make one.",
                 "Larry gives you the Clockwork book. You do not need to read or carry it; "
                 "the suit is supplied automatically during the next stage."),
            ),
            (2, 2): ((" after finishing the suit", ""),),
            (2, 3): (("Free your hands and cape and talk to Larry. He casts a magic spell, "
                      "causing the player to shrink and enter the penguin suit!",
                      "Larry handles your penguin disguise automatically; your equipment stays in place."),),
            (3, 0): (("Exit the enclosure and speak to Larry to get out of the suit.",
                      "Exit the enclosure; your disguise changes automatically."),),
            (3, 1): (("; use the 'tuxedo-time' option with him.",
                      ". Your penguin disguise is handled automatically."),),
            (3, 3): (("Re-tuxedo before entering the penguin enclosure and speak to the penguin again.",
                      "Your penguin disguise changes automatically when you enter the enclosure. "
                      "Speak to the penguin again."),),
            (4, 0): ((" and penguin suit up!", ". Your penguin disguise is handled automatically."),),
            (4, 3): (("Wear the penguin disguise again and head north-west",
                      "Your penguin disguise changes automatically. Head north-west"),),
            (5, 3): (("Have Larry put you back into the suit and return to the outpost",
                      "Your disguise changes automatically. Return to the outpost"),),
            (6, 2): (("The penguins in the room take your suit, and you are teleported to a cage "
                      "filled with Icelords.",
                      "Your disguise is exposed, and you are teleported to a cage filled with Icelords."),),
        }
        whole_paragraphs = {
            (2, 0): "Completing this stage grants one Clockwork suit to your Bank automatically. "
                    "Crafting materials, a crafting table, and reading or carrying the Clockwork "
                    "book are not required. Disguise changes are handled automatically.",
            (5, 1): "Disguise changes are automatic. The Clockwork suit remains in your Bank.",
        }
        expected = {}
        for stage in GENERATED_QUEST["journal_stages"]:
            number = stage["stage"]
            paragraphs = []
            for index, original in enumerate(stage["journal"]):
                if (number, index) == (2, 1):
                    continue
                paragraph = whole_paragraphs.get((number, index), original)
                for old, new in edits.get((number, index), ()):
                    self.assertEqual(paragraph.count(old), 1)
                    paragraph = paragraph.replace(old, new)
                paragraphs.append(paragraph)
            expected[number] = tuple(paragraphs)
        self.assertEqual(QUEST_DATA[QUEST_ID]["journal_stages"], expected)
        rows = quest_journal_rows_pure(_player(6), QUEST_ID, QUEST_DATA)
        self.assertEqual({row["stage"]: row["lines"] for row in rows}, expected)
        text = " ".join(line for lines in expected.values() for line in lines)
        for retired in ("To make a clockwork suit:", "Crafting Table 3", "Free your hands and cape",
                        "tuxedo-time", "Re-tuxedo", "penguin suit up!", "Wear the penguin disguise again",
                        "un-equip the penguin suit", "Have Larry put you back into the suit",
                        "The penguins in the room take your suit"):
            self.assertNotIn(retired, text)
        self.assertEqual(QUEST_DATA[QUEST_ID]["unlocks"], (
            "Penguin disguise changes are handled automatically during Cold War.",
            "Ability to use the Penguin Agility Course",
            "Ability to contact Larry through the NPC Contact spell.",
        ))
        original_rows = _apply_stage_item_name_overrides(
            _catalog_stage_requirements(GENERATED_QUEST["stage_requirements"])
        )
        self.assertEqual(QUEST_DATA[QUEST_ID]["stage_requirements"][2:],
                         tuple(_stage_requirement_dict(row) for row in original_rows if row.stage >= 3))

    def test_existing_quest_boundaries_are_preserved(self):
        quest = QUEST_DATA[QUEST_ID]
        self.assertEqual(len(quest["stage_requirements"]), 6)
        self.assertEqual(len(quest["journal_stages"]), 6)
        # Catalog normalization reserves a seventh progress value for completion.
        self.assertEqual(quest["stages"], GENERATED_QUEST["stages"] + 1)
        self.assertEqual(quest["required_skills"], GENERATED_QUEST["required_skills"])
        self.assertEqual(tuple((row["skill_id"], row["level"]) for row in quest["required_skills"]),
                         (("agility", 30), ("construction", 34), ("crafting", 30),
                          ("hunter", 10), ("thieving", 15)))
        self.assertEqual(quest["point_reward"], 1)
        self.assertEqual(quest["xp_rewards"], (
            {"skill_id": "agility", "amount": 5000.0},
            {"skill_id": "construction", "amount": 1500.0},
            {"skill_id": "crafting", "amount": 2000.0},
        ))
        self.assertEqual(quest["rewards"], {})
        self.assertEqual(quest["combat"], GENERATED_QUEST["combat"])
        encounter = quest["stage_requirements"][4]["combat_encounters"][0]
        self.assertEqual((encounter["encounter_id"], encounter["level"], encounter["quantity"]),
                         ("cold_war_icelord_51", 51, 1))
        self.assertTrue(any(row["kind"].startswith("combat")
                            for row in quest_current_stage_blockers_pure(_player(5), QUEST_ID, QUEST_DATA)))
        player = _player(1)
        player["quests"][QUEST_ID]["started"] = False
        player["crafting_level"] = 29
        self.assertIn("Crafting 30", quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA))
        unchanged, started = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertFalse(started)
        self.assertEqual(unchanged, player)

    def test_completion_does_not_grant_another_suit(self):
        player, progressed, _ = _advance(_player())
        self.assertTrue(progressed)
        player["quests"][QUEST_ID]["progress"] = 6
        player["inventory"].update({"Leather": 1, "Mahogany plank": 1})
        player["quest_action_proofs"].append("Complete Cold War stage 6 objective")
        before = copy.deepcopy(player)
        after, progressed, completed = _advance(player)
        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertEqual(after["quests"][QUEST_ID], dict(started=True, completed=True, progress=7))
        self.assertEqual(after["inventory"], before["inventory"])
        self.assertEqual(after["quest_points"], before["quest_points"] + 1)
        self.assertEqual(after["crafting_exp"], before["crafting_exp"] + 2000)
        self.assertEqual(after["construction_exp"], before["construction_exp"] + 1500)
        self.assertEqual(after["agility_exp"], before["agility_exp"] + 5000)
        loaded = migrate_loaded_data(json.loads(json.dumps(after)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(loaded["inventory"]["Clockwork suit"], 1)
        after_again, progressed, completed = _advance(loaded)
        self.assertFalse(progressed)
        self.assertFalse(completed)
        self.assertEqual(after_again["inventory"]["Clockwork suit"], 1)


class TestColdWarSuitBackfill(unittest.TestCase):
    def test_default_marker_is_false(self):
        self.assertIs(default_player_data(ORE_DATA, ITEM_DEFINITIONS)[COLD_WAR_SUIT_BACKFILL_KEY], False)

    def test_eligibility_quantities_and_exact_boolean_marker(self):
        states = (
            (False, False, 0, False), (False, False, 99, False),
            (True, False, 0, False), (True, False, 1, False), (True, False, 2, False),
            (True, False, 3, True), (True, False, 6, True),
            (False, True, 0, True), (False, True, 7, True),
        )
        for state, marker, quantity in product(
            states, ("missing", False, True, 1, "true", None),
            ("missing", 0, 2, "3", -1, "bad", True),
        ):
            started, completed, progress, eligible = state
            with self.subTest(state=(started, completed, progress), marker=marker, quantity=quantity):
                data = {
                    "quests": {QUEST_ID: dict(started=started, completed=completed, progress=progress)},
                    "inventory": {"Unrelated": {"nested": [1]}},
                    "carried_inventory": {"chicken": {"Clockwork suit": 99}},
                    "quest_action_proofs": ["Unrelated proof"],
                    "equipment": {"cape": "Red cape"}, "cold_war_greeting": list(GREETING),
                    "crafting_exp": 123, "quest_points": 4,
                }
                if marker != "missing":
                    data[COLD_WAR_SUIT_BACKFILL_KEY] = marker
                if quantity != "missing":
                    data["inventory"]["Clockwork suit"] = quantity
                original_inventory = data["inventory"]
                before = copy.deepcopy(data)
                expected = copy.deepcopy(data)
                expected[COLD_WAR_SUIT_BACKFILL_KEY] = marker is True or eligible
                grant = eligible and marker is not True and quantity not in (2, "3")
                if grant:
                    expected["inventory"]["Clockwork suit"] = 1
                migrate_cold_war_suit_pure(data)
                self.assertEqual(data, expected)
                self.assertEqual(original_inventory, before["inventory"])
                if grant:
                    self.assertIsNot(data["inventory"], original_inventory)
                else:
                    self.assertIs(data["inventory"], original_inventory)

    def test_missing_and_malformed_inventory_and_receipt_proof(self):
        for inventory in ("missing", None, [], "invalid"):
            for proof in (False, True):
                with self.subTest(inventory=inventory, receipt_proof=proof):
                    data = {"quests": {QUEST_ID: dict(started=True, progress=3, completed=False)},
                            "quest_action_proofs": [SUIT_ACTION] if proof else []}
                    if inventory != "missing":
                        data["inventory"] = inventory
                    expected = copy.deepcopy(data)
                    expected[COLD_WAR_SUIT_BACKFILL_KEY] = True
                    if not proof:
                        expected["inventory"] = {"Clockwork suit": 1}
                    migrate_cold_war_suit_pure(data)
                    self.assertEqual(data, expected)

    def test_migration_is_one_time_after_json_reload_and_removal(self):
        old = _player(3)
        old.pop(COLD_WAR_SUIT_BACKFILL_KEY)
        repaired = migrate_loaded_data(json.loads(json.dumps(old)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(repaired["inventory"]["Clockwork suit"], 1)
        self.assertIs(repaired[COLD_WAR_SUIT_BACKFILL_KEY], True)
        self.assertEqual(repaired["quest_action_proofs"], [])
        reopened = migrate_loaded_data(json.loads(json.dumps(repaired)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(reopened, repaired)
        reopened["inventory"].pop("Clockwork suit")
        removed = migrate_loaded_data(json.loads(json.dumps(reopened)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(removed["inventory"].get("Clockwork suit", 0), 0)
        self.assertIs(removed[COLD_WAR_SUIT_BACKFILL_KEY], True)

        # A normal stage receipt protects removal even before the first load.
        delivered, progressed, _ = _advance(_player())
        self.assertTrue(progressed)
        self.assertIs(delivered[COLD_WAR_SUIT_BACKFILL_KEY], False)
        delivered["inventory"].pop("Clockwork suit")
        removed = migrate_loaded_data(json.loads(json.dumps(delivered)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(removed["inventory"].get("Clockwork suit", 0), 0)
        self.assertIs(removed[COLD_WAR_SUIT_BACKFILL_KEY], True)
        self.assertEqual(removed["quest_action_proofs"], [SUIT_ACTION])


class TestColdWarSuitStorage(unittest.TestCase):
    def setUp(self):
        original_modules = dict(sys.modules)
        self.addCleanup(sys.modules.update, original_modules)
        self.addCleanup(sys.modules.clear)

    def _raw(self, version=125):
        return {
            "config_version": version,
            "quests": {QUEST_ID: dict(started=True, completed=False, progress=3)},
            "cold_war_greeting": list(GREETING),
            "inventory": {"Unknown legacy item": 2, "oak_logs": 5},
            "quest_action_proofs": ["Untouched proof"],
            "unknown": {"nested": [1, {"keep": True}]},
            "equipment": {"cape": "Red cape"}, "quest_points": 3, "crafting_exp": 123,
        }

    def _collection(self, raw, key=PLAYER_KEY, legacy=False):
        collection = _LegacyTextCollection()
        collection.legacy_row = legacy
        collection.values = {key: raw, SKILL_KEY: "Hunter", "other_config": {"keep": [7]}}
        return collection

    def test_targeted_patch_coalesces_repairs_preserves_raw_and_reopens_without_write(self):
        for version, key, greeting, quantity in product(
            (1, 125), (PLAYER_KEY, RECOVERY_KEY), (False, True), (None, 0, 2),
        ):
            with self.subTest(version=version, key=key, greeting=greeting, quantity=quantity):
                raw = self._raw(version)
                if not greeting:
                    raw.pop("cold_war_greeting")
                if quantity is not None:
                    raw["inventory"]["Clockwork suit"] = quantity
                before = copy.deepcopy(raw)
                expected = copy.deepcopy(raw)
                expected["cold_war_greeting"] = list(GREETING)
                expected[COLD_WAR_SUIT_BACKFILL_KEY] = True
                if quantity != 2:
                    expected["inventory"]["Clockwork suit"] = 1
                collection = self._collection(raw, key)
                storage = _load_storage_module(collection)
                with patch(SAMPLER, return_value=list(GREETING)) as sample, patch.object(
                    collection, "set_config", wraps=collection.set_config,
                ) as save:
                    loaded, skill = storage.load_player_data()
                    self.assertEqual(raw, before)
                    self.assertEqual(skill, "Hunter")
                    self.assertEqual(loaded["inventory"]["Clockwork suit"], quantity or 1)
                    self.assertEqual(collection.values, {
                        PLAYER_KEY: expected, SKILL_KEY: "Hunter", "other_config": {"keep": [7]},
                    })
                    save.assert_called_once_with(PLAYER_KEY, expected)
                    self.assertEqual(sample.call_count, 0 if greeting else 1)
                    persisted = collection.values[PLAYER_KEY]
                    self.assertIsNot(loaded["inventory"], persisted["inventory"])
                    self.assertIsNot(loaded["cold_war_greeting"], persisted["cold_war_greeting"])
                    self.assertIsNot(loaded["unknown"], persisted["unknown"])
                    self.assertIsNot(raw["unknown"], persisted["unknown"])
                    self.assertEqual(storage.load_player_data(), (loaded, skill))
                    save.assert_called_once()
                    # Also protect suits owned before the check from later replacement.
                    persisted["inventory"].pop("Clockwork suit")
                    removed, _ = storage.load_player_data()
                    self.assertEqual(removed["inventory"].get("Clockwork suit", 0), 0)
                    save.assert_called_once()

    def test_missing_and_malformed_raw_inventory_persist_only_granted_suit(self):
        for inventory in ("missing", None, [], "invalid"):
            with self.subTest(inventory=inventory):
                raw = self._raw()
                if inventory == "missing":
                    raw.pop("inventory")
                else:
                    raw["inventory"] = inventory
                before = copy.deepcopy(raw)
                expected = {**before, COLD_WAR_SUIT_BACKFILL_KEY: True, "inventory": {"Clockwork suit": 1}}
                collection = self._collection(raw)
                storage = _load_storage_module(collection)
                with patch.object(collection, "set_config", wraps=collection.set_config) as save:
                    loaded, _ = storage.load_player_data()
                    self.assertEqual(loaded["inventory"]["Clockwork suit"], 1)
                    self.assertEqual(raw, before)
                    save.assert_called_once_with(PLAYER_KEY, expected)
                    storage.load_player_data()
                    save.assert_called_once()

    def test_invalid_boolean_quantity_is_persisted_as_one_integer_suit(self):
        raw = self._raw()
        raw["inventory"]["Clockwork suit"] = True
        collection = self._collection(raw)
        storage = _load_storage_module(collection)
        with patch.object(collection, "set_config", wraps=collection.set_config) as save:
            storage.load_player_data()
            expected = {**raw, COLD_WAR_SUIT_BACKFILL_KEY: True,
                        "inventory": {**raw["inventory"], "Clockwork suit": 1}}
            save.assert_called_once_with(PLAYER_KEY, expected)
            self.assertIs(type(collection.values[PLAYER_KEY]["inventory"]["Clockwork suit"]), int)
            storage.load_player_data()
            save.assert_called_once()

    def test_receipt_and_checked_marker_prevent_replacement_and_earlier_saves_wait(self):
        for mode in ("proof", "checked", "earlier", "unstarted"):
            with self.subTest(mode=mode):
                raw = self._raw()
                if mode == "proof":
                    raw["quest_action_proofs"].append(SUIT_ACTION)
                elif mode == "checked":
                    raw[COLD_WAR_SUIT_BACKFILL_KEY] = True
                elif mode == "earlier":
                    raw["quests"][QUEST_ID]["progress"] = 2
                else:
                    raw["quests"][QUEST_ID] = dict(started=False, completed=False, progress=99)
                    raw.pop("cold_war_greeting")
                before = copy.deepcopy(raw)
                collection = self._collection(raw)
                storage = _load_storage_module(collection)
                with patch.object(collection, "set_config", wraps=collection.set_config) as save:
                    loaded, _ = storage.load_player_data()
                    self.assertEqual(loaded["inventory"].get("Clockwork suit", 0), 0)
                    if mode == "proof":
                        save.assert_called_once_with(PLAYER_KEY, {**before, COLD_WAR_SUIT_BACKFILL_KEY: True})
                    else:
                        save.assert_not_called()
                    self.assertEqual(storage.load_player_data()[0], loaded)
                    self.assertEqual(save.call_count, int(mode == "proof"))

    def test_legacy_text_repair_and_persistence_failures(self):
        raw = self._raw(1)
        raw.pop("cold_war_greeting")
        before = copy.deepcopy(raw)
        expected = {**before, "cold_war_greeting": list(GREETING),
                    COLD_WAR_SUIT_BACKFILL_KEY: True,
                    "inventory": {**before["inventory"], "Clockwork suit": 1}}
        collection = self._collection(raw, legacy=True)
        storage = _load_storage_module(collection)
        with patch(SAMPLER, return_value=list(GREETING)), patch.object(
            collection, "set_config", wraps=collection.set_config,
        ) as save:
            loaded, skill = storage.load_player_data()
            self.assertEqual(save.call_count, 3)
            self.assertEqual([call.args for call in save.call_args_list], [
                (PLAYER_KEY, expected), (RECOVERY_KEY, expected), (PLAYER_KEY, expected),
            ])
            self.assertFalse(collection.legacy_row)
            self.assertNotIn(RECOVERY_KEY, collection.values)
            self.assertEqual(collection.values[PLAYER_KEY], expected)
            self.assertEqual(raw, before)
            self.assertEqual(storage.load_player_data(), (loaded, skill))
            self.assertEqual(save.call_count, 3)

        # A load cannot succeed until the targeted repair is durable.
        for key in (PLAYER_KEY, RECOVERY_KEY):
            collection = self._collection(copy.deepcopy(before), key)
            storage = _load_storage_module(collection)
            unchanged = copy.deepcopy(collection.values)
            with patch(SAMPLER, return_value=list(GREETING)), patch.object(
                collection, "set_config", side_effect=RuntimeError("persist failed"),
            ):
                with self.assertRaisesRegex(RuntimeError, "persist failed"):
                    storage.load_player_data()
            self.assertEqual(collection.values, unchanged)


class TestColdWarSuitRuntime(unittest.TestCase):
    def test_real_review_undo_restores_stage_suit_proofs_and_backfill_marker(self):
        for prior_quantity in (0, 2):
            with self.subTest(prior_quantity=prior_quantity), review_session() as (addon, collection, errors):
                player = _player()
                player["inventory"]["Clockwork suit"] = prior_quantity
                player["quest_action_proofs"] = [BOOK_ACTION, "Existing unrelated proof"]
                player["cold_war_greeting"] = list(GREETING)
                addon._state.player_data = player
                addon._state.current_skill = "Quests"
                addon.check_achievements(player)
                addon.save_player_data()
                before = copy.deepcopy(addon._state.player_data)
                before_store = copy.deepcopy(collection._store)
                _answer_review(addon)
                saved = collection._store[PLAYER_KEY]
                self.assertEqual(saved["quests"][QUEST_ID]["progress"], 3)
                self.assertEqual(saved["inventory"]["Clockwork suit"], prior_quantity + 1)
                self.assertEqual(set(saved["quest_action_proofs"]), {*before["quest_action_proofs"], SUIT_ACTION})
                self.assertNotIn(RETIRED_ACTION, saved["quest_action_proofs"])
                self.assertEqual(saved["crafting_exp"], before["crafting_exp"])
                self.assertIs(saved[COLD_WAR_SUIT_BACKFILL_KEY], False)

                addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))

                self.assertEqual(addon._state.player_data, before)
                self.assertEqual(collection._store, before_store)
                self.assertEqual(addon._state.review_undo_stack, [])
                _answer_review(addon)
                saved = collection._store[PLAYER_KEY]
                self.assertEqual(saved["quests"][QUEST_ID]["progress"], 3)
                self.assertEqual(saved["inventory"]["Clockwork suit"], prior_quantity + 1)
                self.assertEqual(saved["quest_action_proofs"].count(SUIT_ACTION), 1)
                self.assertIs(saved[COLD_WAR_SUIT_BACKFILL_KEY], False)
                addon.load_player_data()
                self.assertEqual(addon._state.player_data["inventory"]["Clockwork suit"], prior_quantity + 1)
                self.assertIs(collection._store[PLAYER_KEY][COLD_WAR_SUIT_BACKFILL_KEY], True)
                persisted = copy.deepcopy(collection._store)
                addon.load_player_data()
                self.assertEqual(collection._store, persisted)
                self.assertEqual(errors, [])
