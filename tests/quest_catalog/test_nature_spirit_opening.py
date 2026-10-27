"""Drezel's commission uses earned prerequisite owners and one opening transaction."""

import copy
import json
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest_data import QUESTS_BY_ID, quests_as_dict
from ankiscape.data.quest.serializers import _stage_requirement_dict
from ankiscape.data.quest.stage_overrides.members.later.nature_spirit import (
    _STAGE_REQUIREMENT_REPLACEMENTS_BY_ID,
)
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic.inventory_pure import carried_slots_used
from ankiscape.logic.shop_logic import apply_shop_buy_pure
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_combat_encounter_pure, apply_quest_progress_pure,
    quest_journal_rows_pure, quest_locked_reasons_pure, start_quest_pure,
)
from ankiscape.runtime.runtime_actions import handle_mining_answer
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest
from tests.test_runtime_actions import _context

QUEST_ID = "nature_spirit"
PIES = ("Meat pie", "Apple pie")
TALK = "Talk to Drezel who is located in the passageway between Silvarea and Morytania."
RECEIPT = "Receive three Meat pies and three Apple pies from Drezel."
COMMISSION = (
    "Speak to Drezel in the passage beneath Paterdomus.",
    "Drezel asks me to find his friend Filliman Tarlock, a druid living in Mort Myre to the south.",
    "He warns that ghasts can rot my food and hurt me if I run out.",
    "His commission includes three whole Meat pies and three whole Apple pies for the journey. I can use the food myself; I do not have to deliver it to Filliman.",
    "I should have my Ghostspeak amulet ready to speak with Filliman. If I have lost it, Father Urhney in Lumbridge Swamp can replace it.",
)


def pie_balances(player):
    return tuple(player["inventory"].get(name, 0) for name in PIES)


def _start(testcase, player, quest_id):
    updated, ok = start_quest_pure(player, quest_id, QUEST_DATA)
    testcase.assertTrue(ok, quest_id)
    return updated


def _stage(testcase, player, quest_id, completed=False):
    updated, ok, done = apply_quest_progress_pure(player, quest_id, QUEST_DATA)
    testcase.assertTrue(ok, (quest_id, player["quests"][quest_id]))
    testcase.assertEqual(done, completed)
    return updated


def _fight(testcase, player, quest_id, encounter):
    updated, ok, result = apply_quest_combat_encounter_pure(
        player, quest_id, QUEST_DATA, encounter,
        ticks=500, rng=lambda: 0.5, equipment_data=EQUIPMENT_DATA,
        stop_after_first_kill=True,
    )
    testcase.assertTrue(ok, result)
    testcase.assertTrue(result["killed"], result)
    return updated


def _earn_rune_mysteries(testcase, player):
    quest_id = "rune_mysteries"
    player = _start(testcase, player, quest_id)
    testcase.assertEqual(player["inventory"]["Air talisman"], 1)
    player = _stage(testcase, player, quest_id)
    testcase.assertEqual(player["inventory"]["Air talisman"], 0)
    testcase.assertEqual(player["inventory"]["Research package"], 1)
    player = _stage(testcase, player, quest_id)
    player = _stage(testcase, player, quest_id)
    testcase.assertEqual(player["inventory"]["Research package"], 0)
    testcase.assertEqual(player["inventory"]["Research notes"], 1)
    player = _stage(testcase, player, quest_id)
    player = _stage(testcase, player, quest_id, completed=True)
    testcase.assertEqual(player["inventory"]["Research notes"], 0)
    return player


def _acquire_bucket_and_essence(testcase, player):
    coins_before = player["inventory"]["Coins"]
    buckets_before = player["inventory"].get("Bucket", 0)
    player, result = apply_shop_buy_pure(
        player, "alices_farming_shop", "alices_farming_shop:8:1925", 1,
    )
    testcase.assertTrue(result["allowed"], result)
    testcase.assertEqual(player["inventory"]["Coins"], coins_before - 2)
    testcase.assertEqual(player["inventory"]["Bucket"], buckets_before + 1)
    testcase.assertTrue(player["quests"]["rune_mysteries"]["completed"])
    testcase.assertLess(player["mining_level"], 30)
    testcase.assertEqual(player["inventory"].get("Rune essence", 0), 0)
    player["current_ore"] = "rune_essence"
    ctx = _context(player, random_values=(0.0,) * 1000)
    for _ in range(100):
        testcase.assertTrue(handle_mining_answer(ctx))
        if player["inventory"].get("Rune essence", 0) >= 50:
            break
    testcase.assertEqual(player["inventory"]["Rune essence"], 50)
    testcase.assertEqual(player["inventory"].get("Pure essence", 0), 0)
    testcase.assertLess(player["mining_level"], 30)
    return player


def _earn_restless_ghost(testcase, player):
    quest_id = "the_restless_ghost"
    player = _start(testcase, player, quest_id)
    player = _stage(testcase, player, quest_id)
    testcase.assertEqual(player["inventory"]["Ghostspeak amulet"], 1)
    player = _stage(testcase, player, quest_id)
    player = _stage(testcase, player, quest_id)
    testcase.assertEqual(player["inventory"]["Muddy skull"], 1)
    player = _fight(testcase, player, quest_id, "the_restless_ghost_skeleton_warlock")
    testcase.assertEqual(player["inventory"]["Muddy skull"], 1)
    player = _stage(testcase, player, quest_id, completed=True)
    testcase.assertEqual(player["inventory"]["Muddy skull"], 0)
    testcase.assertEqual(player["inventory"]["Ghostspeak amulet"], 1)
    return player


def _earn_priest_in_peril(testcase, player):
    quest_id = "priest_in_peril"
    player = _start(testcase, player, quest_id)
    player = _stage(testcase, player, quest_id)  # temple door
    player = _fight(testcase, player, quest_id, "priest_in_peril_temple_guardian_dog_30")
    player = _stage(testcase, player, quest_id)
    player = _stage(testcase, player, quest_id)  # report
    player = _stage(testcase, player, quest_id)  # imprisoned Drezel
    testcase.assertEqual(player["inventory"].get("Golden key", 0), 0)
    player = _fight(testcase, player, quest_id, "priest_in_peril_monk_of_zamorak_30")
    testcase.assertEqual(player["inventory"]["Golden key"], 1)
    player = _stage(testcase, player, quest_id)
    player = _stage(testcase, player, quest_id)  # monument/cell
    testcase.assertEqual(player["inventory"]["Golden key"], 0)
    testcase.assertEqual(player["inventory"]["Bucket"], 1)
    player = _stage(testcase, player, quest_id)  # coffin
    testcase.assertEqual(player["inventory"]["Rune essence"], 50)
    player = _stage(testcase, player, quest_id, completed=True)
    testcase.assertEqual(player["inventory"]["Rune essence"], 0)
    return player


def earned_prerequisite_player(testcase):
    """Qualify existing executable routes, without settling historical combat conflicts."""
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    # Synthetic ordinary starting resources, not claimed as earned gameplay.
    for skill in ("attack", "strength", "defense", "constitution", "ranged", "magic", "prayer", "crafting"):
        player[f"{skill}_level"] = 99
    player["combat_lifepoints"] = 990
    player["equipment"].update(weapon="Rune sword", shield="Rune kiteshield")
    player["inventory"].update({"Coins": 2, "Bronze pickaxe": 1})
    player = _earn_rune_mysteries(testcase, player)
    player = _acquire_bucket_and_essence(testcase, player)
    player = _earn_restless_ghost(testcase, player)
    player = _earn_priest_in_peril(testcase, player)
    testcase.assertFalse(player["quests"][QUEST_ID]["started"])
    testcase.assertEqual(quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA), ())
    testcase.assertEqual(pie_balances(player), (0, 0))
    return player


def _opening(testcase, player):
    return _stage(testcase, player, QUEST_ID)


def _project_and_reload(testcase, player):
    before = copy.deepcopy(player)
    rows = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
    if rows:
        testcase.assertEqual(rows[0]["lines"], COMMISSION)
    loaded = migrate_loaded_data(json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS)
    testcase.assertEqual(pie_balances(loaded), pie_balances(before))
    testcase.assertEqual(loaded["quests"][QUEST_ID], before["quests"][QUEST_ID])
    testcase.assertEqual(loaded["quest_action_proofs"], before["quest_action_proofs"])
    testcase.assertEqual(player, before)
    return loaded


class NatureSpiritOpeningTest(unittest.TestCase):
    def test_composed_commission_and_whole_pie_identity(self):
        quest = quests_as_dict()[QUEST_ID]
        self.assertEqual(quest, QUEST_DATA[QUEST_ID])
        row = quest["stage_requirements"][0]
        self.assertEqual(row["description"], "Accept Drezel's commission to find Filliman Tarlock and receive three Meat pies and three Apple pies.")
        self.assertEqual(row["produced_inventory"], {"Meat pie": 3, "Apple pie": 3})
        self.assertEqual(row["auto_actions"], (TALK, RECEIPT))
        self.assertIn("6555508", row["source"])
        self.assertIn("6283910", row["source"])
        self.assertFalse(row["repeatable_until_consumed"])
        for field in ("required_inventory", "required_inventory_options", "required_skills", "required_tools", "required_actions", "required_routes", "combat_encounters", "consumed_inventory", "consumed_inventory_options"):
            self.assertFalse(row[field], field)
        self.assertEqual(quest["journal_stages"][1], COMMISSION)
        original = next(q for q in PRE_EOC_QUEST_CATALOG if q["id"] == QUEST_ID)
        self.assertEqual(tuple((r["item_name"], r["quantity"]) for r in original["item_rewards"]), (("Apple pie", 3),))
        for journal in original["journal_stages"][1:]:
            self.assertEqual(quest["journal_stages"][journal["stage"]], tuple(journal["journal"]))
        authored = _STAGE_REQUIREMENT_REPLACEMENTS_BY_ID[QUEST_ID]
        self.assertEqual(quest["stage_requirements"][1:], tuple(_stage_requirement_dict(r) for r in authored[1:]))
        self.assertEqual(quest["stages"], 7)
        self.assertEqual(tuple(r["quest_id"] for r in quest["required_quests"]), ("priest_in_peril", "the_restless_ghost"))
        self.assertEqual(quest["required_skills"], ())
        self.assertEqual(quest["requirements"], ("Priest in Peril", "The Restless Ghost"))
        self.assertEqual(quest["rewards"], {})
        self.assertEqual(QUESTS_BY_ID[QUEST_ID].rewards, ())
        for field in ("xp_rewards", "point_reward", "unlocks"):
            self.assertEqual(quest[field], original[field], field)
        self.assertEqual(QUEST_DATA["let_them_eat_pie"]["rewards"]["Meat pie"], 5)
        self._assert_registered_items()

    def _assert_registered_items(self):
        items = {i.storage_key: i for i in ITEM_DEFINITIONS}
        for name, source_id, asset in (("Meat pie", 2327, "meat_pie.png"), ("Apple pie", 2323, "apple_pie.png")):
            self.assertEqual(items[name].source_item_id, source_id)
            self.assertFalse(items[name].stackable)
            self.assertTrue(items[name].asset_path.endswith("cookingitems/" + asset))
        self.assertTrue(items["Ghostspeak amulet"].asset_path.endswith("questitems/ghostspeak_amulet.png"))

    def test_earned_prerequisites_admit_one_complete_opening(self):
        player = earned_prerequisite_player(self)
        before = copy.deepcopy(player)
        after = _opening(self, player)
        self.assertEqual(player, before)
        self.assertEqual(pie_balances(after), (3, 3))
        self.assertEqual(after["quests"][QUEST_ID], dict(started=True, progress=2, completed=False))
        self.assertEqual(set(after["quest_action_proofs"]) - set(before["quest_action_proofs"]), {TALK, RECEIPT})
        self.assertEqual(after["quest_points"], before["quest_points"])
        for key in ("equipment", "quest_combat_encounters", "quest_combat_encounter_counts", "unlocked_abilities"):
            self.assertEqual(after.get(key), before.get(key), key)
        for key in before:
            if key.endswith("_exp"):
                self.assertEqual(after[key], before[key], key)
        expected_inventory = dict(before["inventory"])
        expected_inventory.update({"Meat pie": 3, "Apple pie": 3})
        self.assertEqual(after["inventory"], expected_inventory)

    def test_missing_prerequisites_refuse_without_transaction_changes(self):
        # Synthetic refusal boundaries are deliberately not earned-route evidence.
        for completed in ((), ("priest_in_peril",), ("the_restless_ghost",)):
            for incomplete_started in (False, True):
                with self.subTest(completed=completed, started=incomplete_started):
                    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                    for qid in ("priest_in_peril", "the_restless_ghost"):
                        player["quests"][qid] = dict(started=incomplete_started or qid in completed, progress=1, completed=qid in completed)
                    expected = tuple(QUEST_DATA[q]["display_name"] for q in ("priest_in_peril", "the_restless_ghost") if q not in completed)
                    self.assertEqual(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA), expected)
                    before = copy.deepcopy(player)
                    refused, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
                    self.assertFalse(ok)
                    self.assertEqual(refused, before)
                    refused, ok, done = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
                    self.assertFalse(ok)
                    self.assertFalse(done)
                    self.assertEqual(refused, before)
                    self.assertEqual(player, before)

    def test_opening_increments_existing_balances_without_amulet_gate(self):
        earned = earned_prerequisite_player(self)
        for balances in ((0, 0), (2, 5)):
            player = copy.deepcopy(earned)
            player["inventory"].update(zip(PIES, balances))
            player["inventory"].pop("Ghostspeak amulet")  # synthetic loss
            player["quest_action_proofs"].append("unrelated proof")
            before = copy.deepcopy(player)
            after = _opening(self, player)
            self.assertEqual(pie_balances(after), tuple(n + 3 for n in balances))
            self.assertNotIn("Ghostspeak amulet", after["inventory"])
            for key in ("equipment", "carried_inventory", "carried_layout", "combat_supply_loadout"):
                self.assertEqual(after.get(key), before.get(key))
            self.assertIn("unrelated proof", after["quest_action_proofs"])

    def test_full_carried_pack_keeps_bank_supply_atomic(self):
        player = earned_prerequisite_player(self)
        player["inventory"]["Logs"] = 28
        player["carried_inventory"] = {"woodcutting": {"Logs": 28}}
        player["carried_layout"] = copy.deepcopy(player["carried_inventory"])
        player["inventory"]["Trout"] = 1
        player["combat_supply_loadout"]["food"] = {"Trout": 1}
        player["skilling_bank_run"] = {"target_id": "normal", "reviews_remaining": 2}
        stackable = {i.storage_key for i in ITEM_DEFINITIONS if i.stackable}
        self.assertEqual(carried_slots_used(player["carried_inventory"]["woodcutting"], stackable), 28)
        before = copy.deepcopy(player)
        after = _opening(self, player)
        self.assertEqual(pie_balances(after), (3, 3))
        for key in before:
            if key.startswith(("carried_", "food_", "skilling_bank_run", "combat_supply_loadout")):
                self.assertEqual(after[key], before[key], key)
        self.assertEqual(player, before)

    def test_reselection_subsequent_review_and_loss_do_not_refill(self):
        player = _start(self, earned_prerequisite_player(self), QUEST_ID)
        self.assertEqual(pie_balances(player), (0, 0))
        self.assertNotIn(RECEIPT, player["quest_action_proofs"])
        player = _opening(self, player)
        player = _start(self, player, QUEST_ID)
        player = _stage(self, player, QUEST_ID)  # travel, no refill
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
        self.assertEqual(pie_balances(player), (3, 3))
        player = _project_and_reload(self, player)
        self.assertEqual(player["quest_action_proofs"].count(RECEIPT), 1)
        player["inventory"].update({"Meat pie": 0, "Apple pie": 0})  # synthetic loss
        player = _start(self, player, QUEST_ID)
        player = _stage(self, player, QUEST_ID)
        self.assertEqual(pie_balances(player), (0, 0))
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 4)

    def test_legacy_opening_and_advanced_saves_follow_owner_answer(self):
        earned = earned_prerequisite_player(self)
        for started, progress, completed in ((False, 0, False), (True, 0, False), (True, 1, False), (True, 2, False), (True, 6, False), (True, 7, True)):
            with self.subTest(started=started, progress=progress, completed=completed):
                player = copy.deepcopy(earned)
                player["quests"][QUEST_ID] = dict(started=started, progress=progress, completed=completed)
                player["inventory"].update({"Meat pie": 2, "Apple pie": 5})
                if started:
                    player["quest_action_proofs"] = sorted(set(player["quest_action_proofs"]) | {TALK})
                # Already-started admission is preserved, even with lost prerequisite flags.
                if started and progress <= 1:
                    player["quests"]["priest_in_peril"]["completed"] = False
                player = _project_and_reload(self, player)
                self.assertNotIn(RECEIPT, player["quest_action_proofs"])
                if progress <= 1:
                    after = _opening(self, player)
                    self.assertEqual(pie_balances(after), (5, 8))
                    self.assertIn(RECEIPT, after["quest_action_proofs"])
                    self.assertEqual(after["quests"][QUEST_ID]["progress"], 2)
                else:
                    selected = _start(self, player, QUEST_ID) if not completed else player
                    self.assertEqual(selected["inventory"], player["inventory"])
                    self.assertEqual(selected["quest_action_proofs"], player["quest_action_proofs"])
                    self.assertEqual(selected["quests"][QUEST_ID], player["quests"][QUEST_ID])

    def test_completion_grants_no_fresh_pies(self):
        # Synthetic final-stage consumer boundary, not earned later gameplay.
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"][QUEST_ID] = dict(started=True, progress=7, completed=False)
        player["inventory"].update({"Meat pie": 2, "Apple pie": 5})
        quest = QUEST_DATA[QUEST_ID]
        before = copy.deepcopy(player)
        after = _stage(self, player, QUEST_ID, completed=True)
        self.assertEqual(pie_balances(after), (2, 5))
        self.assertEqual(after["inventory"], before["inventory"])
        self.assertEqual(after["quest_points"] - before["quest_points"], quest["point_reward"])
        for reward in quest["xp_rewards"]:
            key = reward["skill_id"] + "_exp"
            self.assertEqual(after[key] - before[key], reward["amount"])
        self.assertTrue(after["quests"][QUEST_ID]["completed"])
        self.assertNotIn(RECEIPT, after["quest_action_proofs"])
        original = next(q for q in PRE_EOC_QUEST_CATALOG if q["id"] == QUEST_ID)
        self.assertEqual(quest["unlocks"], original["unlocks"])
        self.assertEqual(player, before)
