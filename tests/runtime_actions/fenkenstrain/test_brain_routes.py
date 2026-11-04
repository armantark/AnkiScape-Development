"""Roavar's purchase and successful target-specific Telegrab are separate writers."""
import copy
import unittest

from . import support as s
from ankiscape.logic_pure.logic_pure_magic import magic_target_locked_reasons_pure


class BrainRoutesTest(unittest.TestCase):
    def _assert_roavar_refuses(self, player, reason):
        before = copy.deepcopy(player)
        preview = s.preview_shop_vendor_action_pure(player, s.ROAVAR, 12)
        updated, result = s.apply_shop_vendor_action_pure(player, s.ROAVAR, 12)
        self.assertEqual((preview["allowed"], preview["reason"]), (False, reason))
        self.assertEqual((result["allowed"], result["reason"]), (False, reason))
        self.assertEqual(player, before)
        self.assertEqual(updated, before)

    def _assert_no_cast(self, player):
        self.assertEqual(s._brain_casts(player), 0)
        self.assertNotIn(s.BRAIN_CAST, player.get("achievement_progress", {}).get("skills", {}).get("magic", {}).get("actions", {}))

    def test_roavar_price_and_quantities(self):
        self._assert_roavar_refuses(s._at_stage_two(Coins=49), "missing_requirements")
        for coins in (50, 100):
            for quantity in (1, 12):
                with self.subTest(coins=coins, quantity=quantity):
                    player = s._at_stage_two(Coins=coins)
                    before = copy.deepcopy(player)
                    preview = s.preview_shop_vendor_action_pure(player, s.ROAVAR, quantity)
                    (updated, result), events = s._proof_events(lambda: s.apply_shop_vendor_action_pure(player, s.ROAVAR, quantity))
                    self.assertEqual((preview["quantity"], result["quantity"], result["total_price"]), (1, 1, 50))
                    self.assertEqual(player, before)
                    self.assertEqual(s._delta(before, updated), s.BRAIN_PURCHASE)
                    self.assertEqual(events, [("shop_vendor_action", s.ROAVAR)])
                    self.assertEqual(updated["quests"], before["quests"])
                    self.assertEqual(updated["quest_action_proofs"], before["quest_action_proofs"])
                    event = updated["shop_events"][-1]
                    self.assertEqual({k: event[k] for k in ("type", "service_id", "quantity", "total_price", "inventory_delta", "stock_delta", "inverse")},
                                     {"type": "vendor_action", "service_id": s.ROAVAR, "quantity": 1, "total_price": 50,
                                      "inventory_delta": s.BRAIN_PURCHASE, "stock_delta": {},
                                      "inverse": {"inventory_delta": {"Coins": 50, "Pickled brain": -1}, "stock_set": {}}})
                    self._assert_no_cast(updated)

    def test_roavar_access_before_at_after_interview(self):
        for progress in (0, 1, 2, 3):
            for priest_completed in (False, True):
                with self.subTest(progress=progress, priest_completed=priest_completed):
                    player = s._at_stage_two(Coins=50)
                    player["quests"][s.QUEST_ID] = {"started": progress > 0, "progress": progress, "completed": False}
                    player["quests"]["priest_in_peril"]["completed"] = priest_completed
                    if not priest_completed:
                        self._assert_roavar_refuses(player, "Requires Priest in Peril")
                    elif progress < 2:
                        self._assert_roavar_refuses(player, "Requires Creature of Fenkenstrain stage 2")
                    else:
                        self.assertTrue(s.preview_shop_vendor_action_pure(player, s.ROAVAR)["allowed"])
                        self.assertTrue(s.apply_shop_vendor_action_pure(player, s.ROAVAR)[1]["allowed"])
        # Commit must recheck an eligibility preview invalidated by intervening state.
        player = s._at_stage_two(Coins=50)
        self.assertTrue(s.preview_shop_vendor_action_pure(player, s.ROAVAR)["allowed"])
        player["quests"][s.QUEST_ID]["progress"] = 1
        self._assert_roavar_refuses(player, "Requires Creature of Fenkenstrain stage 2")
        player["quests"][s.QUEST_ID] = s._completed(s.QUEST_ID)
        self.assertTrue(s.apply_shop_vendor_action_pure(player, s.ROAVAR)[1]["allowed"])

    def test_roavar_held_brain_refuses_and_rollback_restores(self):
        for route in ("magic", "shop"):
            with self.subTest(route=route):
                player = s._at_stage_two(Coins=100, **{"Air rune": 1, "Law rune": 1})
                self.assertTrue(s.preview_shop_vendor_action_pure(player, s.ROAVAR)["allowed"])
                if route == "magic":
                    player["current_magic"] = s.BRAIN_CAST
                    self.assertTrue(s.handle_magic_answer(s._context(player)))
                else:
                    s._commit(player, s.apply_shop_vendor_action_pure(player, s.ROAVAR))
                self._assert_roavar_refuses(player, "already_held")
        bought = copy.deepcopy(player)
        s._commit(player, s.rollback_shop_event_pure(player, player["shop_events"][-1]["event_id"]))
        self.assertEqual(s._delta(bought, player), {"Coins": 50, "Pickled brain": -1})
        self.assertTrue(s.preview_shop_vendor_action_pure(player, s.ROAVAR)["allowed"])
        s._commit(player, s.apply_shop_vendor_action_pure(player, s.ROAVAR))
        self.assertEqual(player["inventory"], bought["inventory"])

    def test_telegrab_level_runes_xp_and_staff_substitution(self):
        for missing in ("magic_level", "Air rune", "Law rune"):
            with self.subTest(missing=missing):
                player = s._at_stage_two(**{"Air rune": 1, "Law rune": 1})
                player["current_magic"] = s.BRAIN_CAST
                (player if missing == "magic_level" else player["inventory"])[missing] = 32 if missing == "magic_level" else 0
                before = copy.deepcopy(player)
                self.assertTrue(magic_target_locked_reasons_pure(player, s.BRAIN_CAST, s.MAGIC_DATA))
                self.assertFalse(s.handle_magic_answer(s._context(player)))
                self.assertEqual(player, before)
                self._assert_no_cast(player)
        for staff in ("none", "owned", "equipped"):
            with self.subTest(staff=staff):
                player = s._at_stage_two(**{"Air rune": 1 if staff == "none" else 0, "Law rune": 1})
                if staff == "owned":
                    player["inventory"]["Staff of air"] = 1
                if staff == "equipped":
                    player["equipment"]["weapon"] = "Staff of air"
                player["current_magic"] = s.BRAIN_CAST
                before = copy.deepcopy(player)
                self.assertEqual(magic_target_locked_reasons_pure(player, s.BRAIN_CAST, s.MAGIC_DATA), ())
                self.assertTrue(s.handle_magic_answer(s._context(player)))
                expected = {"Law rune": -1, "Pickled brain": 1}
                if staff == "none":
                    expected["Air rune"] = -1
                self.assertEqual(s._delta(before, player), expected)
                self.assertEqual(player["magic_exp"] - before["magic_exp"], 43)
                self.assertEqual(player["equipment"], before["equipment"])
                self.assertEqual(s._brain_casts(player), 1)
                self.assertEqual(player["achievement_progress"]["skills"]["magic"]["actions"][s.BRAIN_CAST], 1)

    def test_failed_unrelated_and_possession_routes_have_no_brain_cast_deed(self):
        for target in (s.BRAIN_CAST, "telegrab_wine_of_zamorak", "telegrab_ancestral_key"):
            with self.subTest(target=target):
                player = s._at_stage_two(Spade=1, **{"Air rune": 1, "Law rune": int(target != s.BRAIN_CAST)})
                player["current_magic"] = target
                self.assertEqual(s.handle_magic_answer(s._context(player)), target != s.BRAIN_CAST)
                self._assert_no_cast(player)
        player = s._at_stage_two(Coins=50, Spade=1)
        s._commit(player, s.apply_shop_vendor_action_pure(player, s.ROAVAR))
        self._assert_no_cast(player)
        self.assertTrue(s.handle_quest_answer(s._context(player)))
        self._assert_no_cast(player)
        self._assert_no_cast(s._at_stage_two(**{"Pickled brain": 1}))

    def test_spell_quest_ungated_and_repeat_casts(self):
        for progress in (0, 1, 2, 3, 6):
            with self.subTest(progress=progress):
                player = s._at_stage_two(**{"Air rune": 2, "Law rune": 2})
                player["quests"] = {s.QUEST_ID: {"started": progress > 0, "progress": progress, "completed": progress == 6}}
                player["current_magic"] = s.BRAIN_CAST
                before = copy.deepcopy(player)
                for count in (1, 2):
                    self.assertTrue(s.handle_magic_answer(s._context(player)))
                    self.assertEqual(s._brain_casts(player), count)
                    self.assertEqual(player["achievement_progress"]["skills"]["magic"]["actions"][s.BRAIN_CAST], count)
                self.assertEqual(s._delta(before, player), {"Air rune": -2, "Law rune": -2, "Pickled brain": 2})
                self.assertEqual(player["magic_exp"] - before["magic_exp"], 86)
                self.assertEqual(player["quests"], before["quests"])
