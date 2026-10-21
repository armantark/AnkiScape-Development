"""Real direct-action Undo for an explicitly synthetic ready Elite fixture."""

import copy
import sys
import types
import unittest
from dataclasses import replace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG, DiaryCondition, DiaryTask
from ankiscape.logic.achievement_diary_logic import apply_achievement_diary_command_pure
from tests.test_achievement_diaries_integration import _DummyMW, _FakeCollection, _load_addon
from tests.achievement_diaries.test_period_lamp_rewards import EXPECTED, expected_ids


class PeriodLampUndoTest(unittest.TestCase):
    def setUp(self):
        self.modules = dict(sys.modules)
        self.addon = _load_addon("ankiscape_period_lamp_undo")
        addon = self.addon
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon.save_player_data = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_quest_exp_delta = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        self.collection = _FakeCollection()
        addon.mw = _DummyMW(self.collection)

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self.modules)

    def _synthetic_ready_elite(self, family_id):
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == family_id)
        # A test-only task and lookup, never a change to dormant shipped predicates.
        task = DiaryTask("synthetic_ready_elite", "Synthetic readiness", "Test only",
                         (DiaryCondition("skill_level", "mining", 1),), "test fixture", -1)
        elite = replace(family.tiers[-1], tasks=(task,), designed_task_count=1)
        fixture = replace(family, tiers=family.tiers[:-1] + (elite,))
        data = self.addon._state.player_data
        data["achievement_diaries"]["completed_tasks"] = [task.id]
        data["achievement_diaries"]["claimed_tiers"] = [t.id for t in family.tiers[:-1]]
        data["inventory"][family.tiers[-2].reward_item] = 1
        self.tier_patch = patch.dict("ankiscape.logic.achievement_diary_logic._TIERS_BY_ID", {elite.id: (fixture, elite)})
        self.tier_patch.start()
        self.addCleanup(self.tier_patch.stop)
        return elite

    def _claim(self, tier):
        return self.addon.commit_direct_action(
            lambda current: apply_achievement_diary_command_pure(current, "claim_tier", {"tier_id": tier.id})[:2]
        )

    def _undo(self):
        self.addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))

    def test_one_real_undo_restores_equipment_all_pending_lamps_and_tier_ledger(self):
        tier = self._synthetic_ready_elite("falador")
        previous = "Falador shield 3"
        slot = EQUIPMENT_DATA[previous].slot
        self.addon._state.player_data["inventory"].pop(previous, None)
        self.addon._state.player_data["equipment"][slot] = previous
        before = copy.deepcopy(self.addon._state.player_data)
        self.assertTrue(self._claim(tier))
        after = self.addon._state.player_data
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(self.addon._state.direct_action_undo_stack), 1)
        self.assertEqual(after["equipment"][slot], tier.reward_item)
        self.assertEqual(after["inventory"].get(tier.reward_item, 0), 0)
        self.assertEqual(after["inventory"].get(previous, 0), 0)
        self.assertIn(tier.id, after["achievement_diaries"]["claimed_tiers"])
        for claim_id in expected_ids(tier.id):
            self.assertEqual(after["claims"][claim_id], {"claimed": False})
        self.assertEqual({k: v for k, v in after.items() if k.endswith("_exp")},
                         {k: v for k, v in before.items() if k.endswith("_exp")})
        self._undo()
        self.assertEqual(self.addon._state.player_data, before)
        self.assertEqual(self.addon._state.direct_action_undo_stack, [])

    def test_spending_and_destroying_additional_lamps_undo_without_changing_siblings(self):
        tier = self._synthetic_ready_elite("falador")
        self.assertTrue(self._claim(tier))
        addon = self.addon
        ids = expected_ids(tier.id)
        addon._state.player_data["mining_level"] = 72
        before_spend = copy.deepcopy(addon._state.player_data)
        self.assertTrue(addon.on_claim_reward(ids[1], "mining"))
        self.assertEqual(addon._state.player_data["mining_exp"] - before_spend["mining_exp"], 50000)
        self.assertTrue(addon._state.player_data["claims"][ids[1]]["claimed"])
        for sibling in (ids[0], ids[2], ids[3]):
            self.assertEqual(addon._state.player_data["claims"][sibling], before_spend["claims"][sibling])
        self._undo()
        self.assertEqual(addon._state.player_data, before_spend)
        self.assertTrue(addon.on_destroy_claim(ids[2]))
        self.assertTrue(addon._state.player_data["claims"][ids[2]]["forfeited"])
        for sibling in (ids[0], ids[1], ids[3]):
            self.assertEqual(addon._state.player_data["claims"][sibling], before_spend["claims"][sibling])
        self._undo()
        self.assertEqual(addon._state.player_data, before_spend)
        self._undo()
        self.assertNotIn(tier.id, addon._state.player_data["achievement_diaries"]["claimed_tiers"])
        self.assertFalse(set(ids) & addon._state.player_data["claims"].keys())

    def test_every_elite_claim_is_atomic_and_reports_separate_ordered_lamps(self):
        for family_id in ("ardougne", "falador", "fremennik", "karamja", "morytania", "seers", "varrock"):
            with self.subTest(family_id=family_id):
                self.addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                tier = self._synthetic_ready_elite(family_id)
                data = self.addon._state.player_data
                ids = expected_ids(tier.id)
                # Existing spent/forfeited entries must not be reset on creation.
                data["claims"][ids[-1]] = {"claimed": False, "forfeited": True}
                before = copy.deepcopy(data)
                updated, ok, info = apply_achievement_diary_command_pure(data, "claim_tier", {"tier_id": tier.id})
                self.assertTrue(ok)
                self.assertEqual(data, before)
                self.assertEqual(info["lamp_claim_id"], ids[0])
                self.assertEqual(info["lamp_experience"], EXPECTED[tier.id][0][0])
                self.assertEqual(info["lamp_claim_ids"], ids)
                self.assertEqual(info["lamp_experiences"], tuple(xp for xp, _ in EXPECTED[tier.id]))
                entries = "; ".join(f"{xp:,} XP (level {floor}+)" for xp, floor in EXPECTED[tier.id])
                self.assertIn(f"{len(ids)} reward lamps are waiting in Bank Claims: {entries}.", info["message"])
                self.assertEqual(updated["claims"][ids[-1]], before["claims"][ids[-1]])
                for claim_id in ids[:-1]:
                    self.assertEqual(updated["claims"][claim_id], {"claimed": False})
                self.assertEqual({k: v for k, v in updated.items() if k.endswith("_exp")},
                                 {k: v for k, v in before.items() if k.endswith("_exp")})
                self.tier_patch.stop()
