"""Achievement Diaries through the live add-on: review dispatch and undo.

These load ``__init__.py`` as a package, the way the smoke tests do, so the
review hook and the undo seam under test are the shipped ones. Nothing that
matters is faked: the Crafting review runs its real handler, and the claim runs
through the real ``commit_direct_action``.
"""

from __future__ import annotations

import copy
import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.achievement_diary_data import (
    ACHIEVEMENT_DIARY_CATALOG,
    diary_lamp_claim_id,
)
from ankiscape.logic.achievement_diary_logic import refresh_achievement_diaries_pure


class _FakeCollection:
    def __init__(self) -> None:
        self.entries: list[str] = []

    def add_custom_undo_entry(self, name: str) -> None:
        self.entries.append(name)


class _DummyMW:
    def __init__(self, col):
        self.col = col

    def update_undo_actions(self):
        return None


def _load_addon(name: str):
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package(name)


def _varrock():
    return next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")


def _claim_family():
    return next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "ardougne")


# Shared with the pure diary tests rather than reimplemented here, because a
# local copy that silently skipped the kinds it had never heard of is what made
# a whole tier quietly unfinishable when a new kind arrived.
from tests.test_achievement_diaries import _satisfy  # noqa: E402


class DiaryReviewDispatchTest(unittest.TestCase):
    """A review must advance the diary ledger, not just the skill."""

    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon("ankiscape_diary_review")

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_a_real_crafting_review_credits_a_diary_task(self):
        from ankiscape.core.logic import check_achievements
        from ankiscape.runtime.runtime_actions_production import handle_crafting_answer
        from ankiscape.runtime.runtime_actions_shared import RuntimeActionContext

        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        # One Crafting level short of a real Varrock task, so the review itself
        # is what crosses the line rather than the setup.
        task = next(
            t
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for t in tier.tasks
            if len(t.conditions) == 1
            and t.conditions[0].kind == "skill_level"
            and t.conditions[0].key == "crafting"
            # Above the level the weave itself needs, so the review is what
            # crosses the line rather than the starting state.
            and t.conditions[0].amount > 10
        )
        required = task.conditions[0].amount
        player["crafting_level"] = required - 1
        player["inventory"]["Ball of wool"] = 5
        player["current_craft"] = "weave_strip_of_cloth"

        player = refresh_achievement_diaries_pure(player)[0]
        self.assertNotIn(task.id, player["achievement_diaries"]["completed_tasks"])

        errors: list = []

        def _award(exp_key, amount):
            player[exp_key] = float(player.get(exp_key, 0)) + float(amount)
            return amount

        def _level_up(_skill, data):
            data["crafting_level"] = required

        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda title, message: errors.append((title, message)),
            deactivate_current_skill=lambda: None,
            award_skill_exp=_award,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=_level_up,
            check_achievements=check_achievements,
            save_player_data=lambda: None,
            refresh_skill_availability=lambda: None,
            refresh_skill_availability_partial=lambda *_args: None,
            can_smith_any=lambda: False,
            show_exp=lambda _amount: None,
            show_activity_gain=lambda _message: None,
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda _before: None,
        )

        self.assertTrue(handle_crafting_answer(ctx), errors)
        self.assertIn(
            task.id,
            player["achievement_diaries"]["completed_tasks"],
            "the review path did not advance the diary ledger",
        )
        self.assertTrue(
            any(
                row["kind"] == "achievement" and task.name in row["text"]
                for row in player["review_event_log"]
            ),
            "the emitted achievement toast did not enter the review event log",
        )

    def test_arachnophagia_requires_the_real_spider_cooking_action(self):
        from ankiscape.core.logic import check_achievements, level_up_check
        from ankiscape.runtime.runtime_actions_production import handle_cooking_answer
        from ankiscape.runtime.runtime_actions_shared import RuntimeActionContext

        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.source_id == 197
        )
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update(
            cooking_level=15,
            cooking_exp=2745.0,
            current_cooking="cook_mackerel",
        )
        player["inventory"].update(
            {"Raw mackerel": 1, "Raw spider on stick": 1}
        )
        errors: list = []

        def _award(exp_key, amount):
            player[exp_key] = float(player.get(exp_key, 0)) + float(amount)
            return amount

        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.0,
            show_error_message=lambda title, message: errors.append((title, message)),
            deactivate_current_skill=lambda: None,
            award_skill_exp=_award,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=level_up_check,
            check_achievements=check_achievements,
            save_player_data=lambda: None,
            refresh_skill_availability=lambda: None,
            refresh_skill_availability_partial=lambda *_args: None,
            can_smith_any=lambda: False,
            show_exp=lambda _amount: None,
            show_activity_gain=lambda _message: None,
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda _before: None,
        )

        with patch("ankiscape.core.logic.show_level_up_dialog"):
            self.assertTrue(handle_cooking_answer(ctx), errors)
        self.assertEqual(player["cooking_level"], 16)
        self.assertNotIn(task.id, player["achievement_diaries"]["completed_tasks"])
        self.assertNotIn(
            "cook_spider_on_a_stick",
            player["achievement_progress"]["skills"]["cooking"]["actions"],
        )

        player["current_cooking"] = "cook_spider_on_a_stick"
        self.assertTrue(handle_cooking_answer(ctx), errors)
        self.assertIn(task.id, player["achievement_diaries"]["completed_tasks"])
        self.assertEqual(
            player["achievement_progress"]["skills"]["cooking"]["actions"][
                "cook_spider_on_a_stick"
            ],
            1,
        )

    def test_the_review_hook_leaves_the_old_catalog_sticky(self):
        """Semantics contract: completed achievement names stay put."""
        from ankiscape.core.logic import check_achievements

        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["completed_achievements"] = ["First Steps"]
        check_achievements(player)
        self.assertIn("First Steps", player["completed_achievements"])


class DiaryUndoSeamTest(unittest.TestCase):
    """Criterion 5: undo at every mutation boundary."""

    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon("ankiscape_diary_undo")
        self.addon.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.saves: list[bool] = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _ready_to_claim(self):
        player = self.addon.player_data
        tier = _claim_family().tiers[0]
        for task in tier.tasks:
            _satisfy(player, task)
        updated = refresh_achievement_diaries_pure(player)[0]
        player.clear()
        player.update(updated)
        return tier

    def test_a_claim_is_one_undoable_operation(self):
        from ankiscape.logic.achievement_diary_logic import (
            apply_achievement_diary_command_pure,
        )

        addon = self.addon
        tier = self._ready_to_claim()
        before = copy.deepcopy(dict(addon.player_data))
        depth = len(addon._DIRECT_ACTION_UNDO_STACK)

        committed = addon.commit_direct_action(
            lambda current: apply_achievement_diary_command_pure(
                current, "claim_tier", {"tier_id": tier.id, "lamp_skill": "mining"}
            )[:2]
        )

        self.assertTrue(committed)
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), depth + 1)
        self.assertEqual(len(self.saves), 1)
        self.assertEqual(addon.player_data["inventory"].get("Ardougne cloak 1"), 1)

        restored = addon._DIRECT_ACTION_UNDO_STACK[-1]["player_data"]
        self.assertEqual(
            restored["achievement_diaries"]["claimed_tiers"],
            before["achievement_diaries"]["claimed_tiers"],
            "the snapshot did not capture the pre-claim ledger",
        )
        self.assertFalse(restored["inventory"].get("Ardougne cloak 1"))

    def test_one_undo_restores_the_item_pending_lamp_and_ledger_together(self):
        from ankiscape.logic.achievement_diary_logic import (
            apply_achievement_diary_command_pure,
        )
        from ankiscape.logic_pure.logic_pure_claims import claim_locked_reasons_pure

        addon = self.addon
        tier = self._ready_to_claim()
        before = copy.deepcopy(dict(addon.player_data))
        claim_id = diary_lamp_claim_id(tier.id)

        addon.commit_direct_action(
            lambda current: apply_achievement_diary_command_pure(
                current, "claim_tier", {"tier_id": tier.id}
            )[:2]
        )
        self.assertEqual(addon.player_data["mining_exp"], before["mining_exp"])
        self.assertEqual(
            claim_locked_reasons_pure(addon.player_data, claim_id, addon.CLAIM_DATA),
            (),
        )

        snapshot = addon._DIRECT_ACTION_UNDO_STACK.pop()["player_data"]
        addon.player_data.clear()
        addon.player_data.update(snapshot)

        self.assertFalse(addon.player_data["inventory"].get("Ardougne cloak 1"))
        self.assertEqual(addon.player_data["mining_exp"], before["mining_exp"])
        self.assertEqual(addon.player_data["achievement_diaries"]["claimed_tiers"], [])
        self.assertEqual(
            claim_locked_reasons_pure(addon.player_data, claim_id, addon.CLAIM_DATA),
            ("diary tier",),
        )

    def test_spending_the_bank_lamp_is_an_undoable_direct_action(self):
        from ankiscape.logic.achievement_diary_logic import (
            apply_achievement_diary_command_pure,
        )

        addon = self.addon
        tier = self._ready_to_claim()
        claim_id = diary_lamp_claim_id(tier.id)
        addon.commit_direct_action(
            lambda current: apply_achievement_diary_command_pure(
                current, "claim_tier", {"tier_id": tier.id}
            )[:2]
        )
        before_spend = copy.deepcopy(dict(addon.player_data))
        depth = len(addon._DIRECT_ACTION_UNDO_STACK)

        self.assertTrue(addon.on_claim_reward(claim_id, "mining"))

        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), depth + 1)
        self.assertEqual(
            addon.player_data["mining_exp"] - before_spend["mining_exp"],
            float(tier.lamp.experience),
        )
        self.assertTrue(addon.player_data["claims"][claim_id]["claimed"])

        snapshot = addon._DIRECT_ACTION_UNDO_STACK.pop()["player_data"]
        addon.player_data.clear()
        addon.player_data.update(snapshot)
        self.assertEqual(addon.player_data["mining_exp"], before_spend["mining_exp"])
        self.assertFalse(addon.player_data["claims"][claim_id]["claimed"])
        self.assertIn(tier.id, addon.player_data["achievement_diaries"]["claimed_tiers"])
        self.assertEqual(addon.player_data["inventory"].get(tier.reward_item), 1)

    def test_a_refused_claim_writes_nothing(self):
        from ankiscape.logic.achievement_diary_logic import (
            apply_achievement_diary_command_pure,
        )

        addon = self.addon
        baseline = copy.deepcopy(dict(addon.player_data))
        committed = addon.commit_direct_action(
            lambda current: apply_achievement_diary_command_pure(
                current, "claim_tier", {"tier_id": _varrock().tiers[0].id}
            )[:2]
        )
        self.assertFalse(committed)
        self.assertEqual(dict(addon.player_data), baseline)
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(self.saves, [])

    def test_a_pin_is_undoable_too(self):
        from ankiscape.logic.achievement_diary_logic import (
            apply_achievement_diary_command_pure,
        )

        addon = self.addon
        task = _varrock().tiers[0].tasks[0]
        committed = addon.commit_direct_action(
            lambda current: apply_achievement_diary_command_pure(
                current, "pin_task", {"task_id": task.id}
            )[:2]
        )
        self.assertTrue(committed)
        self.assertEqual(
            addon.player_data["achievement_diaries"]["pinned_task"], task.id
        )
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])

    def test_the_claimed_item_is_wearable_after_the_committed_claim(self):
        """No inert rewards: the thing the seam grants can actually be worn."""
        from ankiscape.logic.achievement_diary_logic import (
            apply_achievement_diary_command_pure,
        )
        from ankiscape.logic_pure.logic_pure_equipment import (
            can_equip_item_pure,
            equip_item_pure,
        )

        addon = self.addon
        tier = self._ready_to_claim()
        addon.commit_direct_action(
            lambda current: apply_achievement_diary_command_pure(
                current, "claim_tier", {"tier_id": tier.id, "lamp_skill": "mining"}
            )[:2]
        )
        allowed, reason = can_equip_item_pure(
            tier.reward_item, EQUIPMENT_DATA, addon.player_data
        )
        self.assertTrue(allowed, reason)
        _inventory, equipment, worn = equip_item_pure(
            tier.reward_item,
            addon.player_data["inventory"],
            addon.player_data["equipment"],
            EQUIPMENT_DATA,
        )
        self.assertTrue(worn)
        self.assertIn(tier.reward_item, equipment.values())


if __name__ == "__main__":
    unittest.main()
