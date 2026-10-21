import copy
import json
import sys
import types
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest.catalog import (
    _apply_stage_item_name_overrides,
    _catalog_stage_requirements,
)
from ankiscape.data.quest.serializers import _stage_requirement_dict
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
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


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
        for inventory in ({}, sentinels):
            with self.subTest(inventory=inventory):
                player = _player()
                player["inventory"] = dict(inventory)
                player["crafting_exp"] = 123.0
                self.assertEqual(quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA), ())
                after, progressed, completed = _advance(player)
                self.assertTrue(progressed)
                self.assertFalse(completed)
                self.assertEqual(after["quests"][QUEST_ID]["progress"], 3)
                self.assertEqual(after["inventory"], {**inventory, "Clockwork suit": 1})
                self.assertEqual(after["quest_action_proofs"], [SUIT_ACTION])
                self.assertNotIn(RETIRED_ACTION, after["quest_action_proofs"])
                self.assertEqual(after["crafting_exp"], player["crafting_exp"])
                self.assertEqual(player["inventory"], inventory)

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
                self.assertEqual(loaded["inventory"].get("Clockwork suit", 0), 0)
                after, _, _ = _advance(loaded)
                self.assertEqual(after["inventory"].get("Clockwork suit", 0), 0)
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
                           "owner's combined representation"):
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


class TestColdWarSuitRuntime(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_real_review_undo_restores_stage_and_suit(self):
        addon = _load_addon_as_package("ankiscape_cold_war_suit_e2e")
        saved, errors = [], []
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: errors.append((title, message))
        for prior_quantity in (0, 2):
            with self.subTest(prior_quantity=prior_quantity):
                player = _player()
                player["inventory"]["Clockwork suit"] = prior_quantity
                player["quest_action_proofs"] = [BOOK_ACTION, "Existing unrelated proof"]
                prior_proofs = list(player["quest_action_proofs"])
                prior_xp = player["crafting_exp"]
                addon._state.player_data = player
                addon._state.current_skill = "Quests"
                addon._state.review_undo_stack.clear()
                saved.clear()

                _answer_review(addon)

                self.assertEqual(len(saved), 1)
                self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 3)
                self.assertEqual(saved[-1]["inventory"]["Clockwork suit"], prior_quantity + 1)
                self.assertEqual(set(saved[-1]["quest_action_proofs"]), {*prior_proofs, SUIT_ACTION})
                self.assertNotIn(RETIRED_ACTION, saved[-1]["quest_action_proofs"])
                self.assertEqual(saved[-1]["crafting_exp"], prior_xp)

                addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

                self.assertEqual(addon._state.player_data["quests"][QUEST_ID]["progress"], 2)
                self.assertEqual(addon._state.player_data["inventory"]["Clockwork suit"], prior_quantity)
                self.assertEqual(addon._state.player_data["quest_action_proofs"], prior_proofs)
                self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 2)
                self.assertEqual(saved[-1]["inventory"]["Clockwork suit"], prior_quantity)

                _answer_review(addon)

                self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 3)
                self.assertEqual(saved[-1]["inventory"]["Clockwork suit"], prior_quantity + 1)
                self.assertEqual(saved[-1]["quest_action_proofs"].count(SUIT_ACTION), 1)
                self.assertEqual(saved[-1]["crafting_exp"], prior_xp)
        self.assertEqual(errors, [])
