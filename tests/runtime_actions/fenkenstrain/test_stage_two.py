"""The stage commits a private, ordered item transaction exactly once."""
import copy
import unittest
from unittest.mock import patch

from . import support as s
from ankiscape.logic_pure.quest import stage_items
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_blocker_reasons_pure


class StageTwoTest(unittest.TestCase):
    def _assert_stage_review(self, player):
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        advanced, events = s._proof_events(lambda: s.handle_quest_answer(s._context(player, calls)))
        self.assertTrue(advanced)
        self.assertEqual(s._delta(before, player), s.STAGE_OUTPUTS)
        self.assertEqual(events, [("quest_stage", f"{s.QUEST_ID}:{action}") for action in s.STAGE_TWO_ACTIONS]
                         + [("quest", s.QUEST_ID)])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(player["quests"][s.QUEST_ID], {"started": True, "progress": 3, "completed": False})
        self.assertEqual(player["quest_points"], before["quest_points"])
        self.assertEqual({k: v for k, v in player.items() if k.endswith("_exp")},
                         {k: v for k, v in before.items() if k.endswith("_exp")})
        old_records = before.get("action_telemetry", {}).get("actions", {}).get(f"quest:{s.QUEST_ID}", {}).get("successes", 0)
        self.assertEqual(player["action_telemetry"]["actions"][f"quest:{s.QUEST_ID}"]["successes"], old_records + 1)
        self.assertEqual(player["inventory"].get("Ring of Charos", 0), 0)
        self.assertEqual(player.get("achievement_diaries"), before.get("achievement_diaries"))
        self.assertEqual(s._brain_casts(player), s._brain_casts(before))

    def _assert_earned_opening(self, player):
        for quest in ("rune_mysteries", "the_restless_ghost", "priest_in_peril"):
            self.assertTrue(player["quests"][quest]["completed"])
            self.assertGreater(player["action_telemetry"]["actions"][f"quest:{quest}"]["successes"], 0)
        self.assertEqual(player["quests"][s.QUEST_ID]["progress"], 2)
        self.assertEqual(player["inventory"]["Ghostspeak amulet"], 1)
        self.assertEqual(player["inventory"]["Rune essence"], 0)
        self.assertEqual(player["inventory"]["Spade"], 1)
        self.assertTrue(all(player["inventory"].get(name, 0) == 0 for name in s.STAGE_ITEM_IDS))

    def test_shop_route_earns_prerequisites_and_finishes_once(self):
        player = s._ordinary_stage_two()
        self._assert_earned_opening(player)
        s._collect(player, s.handle_thieving_answer, "Coins", 103)
        before = copy.deepcopy(player)
        s._commit(player, s.apply_shop_vendor_action_pure(player, s.ROAVAR))
        self.assertEqual(s._delta(before, player), s.BRAIN_PURCHASE)
        self.assertEqual(s._brain_casts(player), 0)
        self._assert_stage_review(player)
        self._assert_later_refused(player)

    def test_telegrab_route_earns_prerequisites_and_finishes_once(self):
        player = s._ordinary_stage_two()
        self._assert_earned_opening(player)
        s._collect(player, s.handle_thieving_answer, "Coins", 448)
        for row in (s.AIR_ROW, s.LAW_ROW):
            s._buy(player, row)
        player["current_magic"] = s.BRAIN_CAST
        before = copy.deepcopy(player)
        self.assertTrue(s.handle_magic_answer(s._context(player)))
        self.assertEqual(s._delta(before, player), {"Air rune": -1, "Law rune": -1, "Pickled brain": 1})
        self.assertEqual(player["magic_exp"] - before["magic_exp"], 43)
        self.assertEqual(s._brain_casts(player), 1)
        self._assert_stage_review(player)
        self._assert_later_refused(player)

    def test_spade_and_brain_refusals_are_atomic(self):
        for inventory, belt, reason in (
            ({"Pickled brain": 1}, False, "Needs Spade x1"),
            ({"Pickled brain": 1}, True, "Needs Spade x1"),
            ({"Spade": 1}, True, "Needs Pickled brain x1"),
        ):
            with self.subTest(inventory=inventory, belt=belt):
                player = s._at_stage_two(**inventory)
                # Spade is always on the ordinary belt; neither missing case carries it.
                self.assertEqual(player["inventory"].get("Spade", 0), inventory.get("Spade", 0))
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertIn(reason, quest_current_stage_blocker_reasons_pure(player, s.QUEST_ID, s.QUEST_DATA))
                self.assertFalse(s.handle_quest_answer(s._context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)
                self.assertFalse(stage_items.apply_fenkenstrain_stage_two_items_pure(player))
                self.assertEqual(player, before)

    def test_amulet_steps_debit_exactly_once(self):
        player = s._at_stage_two(Spade=1, **{"Pickled brain": 1, "Marble amulet": 4, "Obsidian amulet": 7})
        before = copy.deepcopy(player)
        # Observe every private inventory write, including both intermediate debits.
        snapshots = []

        class TracedInventory(dict):
            def __setitem__(self, name, quantity):
                super().__setitem__(name, quantity)
                snapshots.append(dict(self))
        with patch.object(stage_items, "dict", TracedInventory, create=True):
            self.assertTrue(stage_items.apply_fenkenstrain_stage_two_items_pure(player))
        expected = dict(before["inventory"])
        for snapshot, (name, delta) in zip(snapshots, (
            ("Decapitated head", 1), ("Marble amulet", 1), ("Obsidian amulet", 1),
            ("Marble amulet", -1), ("Obsidian amulet", -1), ("Star amulet", 1),
        )):
            expected[name] = expected.get(name, 0) + delta
            self.assertEqual(snapshot, expected)
        self.assertEqual(len(snapshots), 6)
        self.assertEqual(s._delta(before, player), s.STAGE_OUTPUTS)
        self.assertEqual(player["quests"], before["quests"])
        # A failure after the dig and bookcases cannot expose partial inventory or proofs.
        broken = (*stage_items.CREATURE_OF_FENKENSTRAIN_STAGE_TWO_TRANSACTION[:-1],
                  {"required_inventory": (("Unavailable item", 1),), "consumed_inventory": (), "produced_inventory": ()})
        untouched = copy.deepcopy(before)
        with patch.object(stage_items, "CREATURE_OF_FENKENSTRAIN_STAGE_TWO_TRANSACTION", broken):
            self.assertFalse(stage_items.apply_fenkenstrain_stage_two_items_pure(untouched))
        self.assertEqual(untouched, before)
        self._assert_later_step_refusals(before)
        self._assert_stage_review(player)
        self.assertEqual((player["inventory"]["Marble amulet"], player["inventory"]["Obsidian amulet"]), (4, 7))

    def _assert_later_step_refusals(self, before):
        for step in (
            {"required_inventory": (), "consumed_inventory": (("Marble amulet", 100),), "produced_inventory": ()},
            {"required_inventory": (("Marble amulet", 5),), "consumed_inventory": (), "produced_inventory": ()},
        ):
            untouched = copy.deepcopy(before)
            transaction = (*stage_items.CREATURE_OF_FENKENSTRAIN_STAGE_TWO_TRANSACTION, step)
            with patch.object(stage_items, "CREATURE_OF_FENKENSTRAIN_STAGE_TWO_TRANSACTION", transaction):
                self.assertFalse(stage_items.apply_fenkenstrain_stage_two_items_pure(untouched))
            self.assertEqual(untouched, before)

    def _assert_later_refused(self, player):
        before = copy.deepcopy(player)
        for _ in range(2):
            result, events = s._proof_events(lambda: s.handle_quest_answer(s._context(player)))
            self.assertFalse(result)
            self.assertEqual(events, [])
            self.assertEqual(player, before)
        self.assertIn("Complete Creature of Fenkenstrain stage 3 objective",
                      " ".join(quest_current_stage_blocker_reasons_pure(player, s.QUEST_ID, s.QUEST_DATA)))

    def test_later_stage_stays_blocked(self):
        player = s._at_stage_two(Spade=1, Coins=70, **{"Pickled brain": 1, "Air rune": 3, "Law rune": 3})
        self._assert_stage_review(player)
        self._assert_later_refused(player)
