"""The production controller through the add-on's whole-state Undo seam, and its hooks."""

from __future__ import annotations

import copy
import random
import sys
import types
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, exp_table_for_skill
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.ancient_effigies.catalog import SKILL_PAIRS, STAGES
from ankiscape.logic.ancient_effigies.custody import INSTANCES_KEY, NEXT_ID_KEY

UNDO = type("Changes", (), {"operation": "AnkiScape direct action"})()
SEED_1 = "00000000000000000000000000000001"
SEED_2 = "00000000000000000000000000000002"


class _Collection:
    """Config store and undo-entry recorder shaped like Anki's collection."""

    def __init__(self, *, accepts=True):
        self.values = {"ankiscape_popups_enabled": False}
        self.entries = []
        self.accepts = accepts

    def get_config(self, key, default=None):
        return self.values.get(key, default)

    def set_config(self, key, value):
        self.values[key] = copy.deepcopy(value)

    def remove_config(self, key):
        self.values.pop(key, None)

    def add_custom_undo_entry(self, name):
        if not self.accepts:
            raise RuntimeError("collection refused the undo entry")
        self.entries.append(name)


class _MW:
    def __init__(self, col):
        self.col = col

    def update_undo_actions(self):
        pass


def load_feature(test, package):
    """Load the real add-on root and return it with its production controller."""
    from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package

    modules = dict(sys.modules)
    random_state = random.getstate()
    test.addCleanup(random.setstate, random_state)
    test.addCleanup(sys.modules.update, modules)
    test.addCleanup(sys.modules.clear)
    _install_runtime_fakes()
    addon = _load_addon_as_package(package)
    collection = _Collection()
    addon.mw = _MW(collection)
    sys.modules[f"{package}.core.storage"].mw = addon.mw
    # Level-up popups read Anki's main window; this profile turns them off.
    sys.modules["aqt"].mw = addon.mw
    feature = sys.modules[f"{package}.runtime.ancient_effigies"]
    return addon, feature, feature.controller_for(package), collection


def owner(**fields):
    """A complete save with two Starved effigies whose requests are known."""
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    top = float(exp_table_for_skill("crafting")[98])
    for skill_id in {skill for pair in SKILL_PAIRS for skill in pair}:
        data.update({f"{skill_id}_level": 99, f"{skill_id}_exp": top})
    data.update(attack_level=1, attack_exp=0)
    data["inventory"]["Starved ancient effigy"] = 2
    data[INSTANCES_KEY] = {
        "ancient-effigy-1": {"item_id": 18778, "location": "bank", "request_seed": SEED_1, "request_step": 0, "pair_index": None},
        "ancient-effigy-2": {"item_id": 18778, "location": "bank", "request_seed": SEED_2, "request_step": 0, "pair_index": None},
    }
    data[NEXT_ID_KEY] = 3
    data.update(fields)
    return data


class ControllerUndoTest(unittest.TestCase):
    def setUp(self):
        self.addon, self.feature, self.controller, self.collection = load_feature(self, "ankiscape_effigy_runtime")
        self.addon._state.player_data = owner()
        self.addon._state.current_skill = "Crafting"
        # A loaded profile has already been through one ordinary save.
        self.addon.save_player_data()
        random.seed(1520)

    def snapshot(self):
        return copy.deepcopy(self.addon._state.player_data), self.addon._state.current_skill, random.getstate()

    def undo(self):
        self.addon._on_state_did_undo(UNDO)

    def assertUndoRestores(self, before, action):
        result = action()
        self.assertTrue(result.ok, result.message)
        after = self.snapshot()
        self.undo()
        self.assertEqual(self.snapshot(), before)
        replay = action()
        self.assertTrue(replay.ok, replay.message)
        self.assertEqual(self.snapshot()[:2], after[:2], "replay reproduces the same pair, output and reward")
        self.assertEqual(replay.info, result.info)
        return result

    def test_inspection_survives_undo_and_unrelated_rng_use(self):
        before = self.snapshot()
        entries = len(self.collection.entries)
        self.assertUndoRestores(before, lambda: self.controller.inspect("ancient-effigy-1"))
        pair = self.addon._state.player_data[INSTANCES_KEY]["ancient-effigy-1"]["pair_index"]
        self.assertEqual(pair, 2)
        self.assertEqual(len(self.collection.entries), entries + 2)
        self.undo()
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(self.addon.commit_direct_action(lambda current: ({**current, "noise": random.random()}, True)))
        self.assertTrue(self.controller.inspect("ancient-effigy-1").ok)
        self.assertEqual(self.addon._state.player_data[INSTANCES_KEY]["ancient-effigy-1"]["pair_index"], pair)
        entries = len(self.collection.entries)
        result = self.controller.inspect("ancient-effigy-1")
        self.assertTrue(result.ok)
        self.assertEqual(len(self.collection.entries), entries, "a repeated inspection is a read, not another Undo step")

    def test_four_transformations_and_redemption_undo_and_replay(self):
        self.assertTrue(self.controller.inspect("ancient-effigy-1").ok)
        sibling = copy.deepcopy(self.addon._state.player_data[INSTANCES_KEY]["ancient-effigy-2"])
        requested = []
        for stage in STAGES:
            xp, output = stage.reward_xp, stage.output_item_id
            with self.subTest(stage=stage.name):
                detail = self.controller.detail("ancient-effigy-1")
                self.assertEqual(detail["name"], stage.name)
                skill_id = detail["choices"][0]["skill_id"]
                requested.append(skill_id)
                before = self.snapshot()
                exp_before = before[0][f"{skill_id}_exp"]
                result = self.assertUndoRestores(before, lambda: self.controller.investigate(detail["token"], skill_id))
                live = self.addon._state.player_data
                self.assertEqual(live[f"{skill_id}_exp"] - exp_before, xp)
                self.assertEqual(live[INSTANCES_KEY]["ancient-effigy-1"]["item_id"], output)
                self.assertEqual(live[INSTANCES_KEY]["ancient-effigy-2"], sibling)
                self.assertEqual(result.info["xp"], xp)
        self.assertEqual(requested, ["cooking", "construction", "herblore", "farming"])
        self.assertEqual(self.addon._state.player_data[INSTANCES_KEY]["ancient-effigy-1"]["location"], "held")
        self.assertEqual(self.addon._state.player_data["inventory"]["Starved ancient effigy"], 1)
        self.assertNotIn("Dragonkin lamp", self.addon._state.player_data["inventory"])
        token = self.controller.detail("ancient-effigy-1")["token"]
        before = self.snapshot()
        result = self.assertUndoRestores(before, lambda: self.controller.redeem_lamp(token, "attack"))
        self.assertEqual((result.info["level"], result.info["xp"]), (1, 4))
        self.assertEqual(self.addon._state.player_data["attack_exp"], 4)
        self.assertNotIn("ancient-effigy-1", self.addon._state.player_data[INSTANCES_KEY])
        repeated = self.controller.redeem_lamp(token, "attack")
        self.assertFalse(repeated.ok)
        self.assertIn("changed", repeated.message)
        self.assertEqual(self.addon._state.player_data["attack_exp"], 4)

    def test_destruction_undo_and_replay(self):
        data = self.addon._state.player_data
        data[INSTANCES_KEY]["ancient-effigy-3"] = {"item_id": 18782, "location": "held", "request_seed": SEED_1, "request_step": 3, "pair_index": None}
        data[NEXT_ID_KEY] = 4
        token = self.controller.detail("ancient-effigy-3")["token"]
        before = self.snapshot()
        self.assertUndoRestores(before, lambda: self.controller.destroy_lamp(token))
        self.assertNotIn("ancient-effigy-3", self.addon._state.player_data[INSTANCES_KEY])
        self.assertEqual(self.addon._state.player_data["attack_exp"], 0)

    def test_rewards_update_levels_feedback_and_achievements_without_training_bonuses(self):
        from ankiscape.data.goblin_raids_data import GOBLIN_COWER_SHIELD

        data = self.addon._state.player_data
        cooking_exp = float(exp_table_for_skill("cooking")[91]) - 1000
        data["cooking_exp"] = cooking_exp
        data["cooking_level"] = 91
        data["equipment"] = {**data.get("equipment", {}), "shield": GOBLIN_COWER_SHIELD}
        data["goblin_raids"] = {**data.get("goblin_raids", {}), "cower_shield_bonus_remaining": 1000.0}
        self.collection.values["ankiscape_review_action_multiplier"] = 10
        self.assertTrue(self.addon.goblin_cower_shield_can_apply_pure(data, "attack_exp"), "a training bonus is live")
        checks = []
        original_check = self.addon.check_achievements
        self.addon.check_achievements = lambda player: checks.append(player is self.addon._state.player_data) or original_check(player)
        self.assertTrue(self.controller.inspect("ancient-effigy-1").ok)
        token = self.controller.detail("ancient-effigy-1")["token"]
        result = self.controller.investigate(token, "cooking")
        self.assertTrue(result.ok, result.message)
        live = self.addon._state.player_data
        self.assertEqual(live["cooking_exp"], cooking_exp + 15000)
        self.assertEqual(live["cooking_level"], 92)
        self.assertEqual(checks, [True])
        events = [row["text"] for row in live["review_event_log"]]
        self.assertIn("+15000 XP · Cooking", events)
        self.assertIn("Cooking advanced to level 92", events)
        live[INSTANCES_KEY]["ancient-effigy-9"] = {"item_id": 18782, "location": "held", "request_seed": SEED_1, "request_step": 3, "pair_index": None}
        live[NEXT_ID_KEY] = 10
        redeemed = self.controller.redeem_lamp(self.controller.detail("ancient-effigy-9")["token"], "attack")
        self.assertTrue(redeemed.ok)
        self.assertEqual(live["attack_exp"], 4, "no cower-shield or multiplier bonus")
        self.assertEqual(live["goblin_raids"]["cower_shield_bonus_remaining"], 1000.0)
        self.assertEqual(checks, [True, True])

    def test_refusal_and_refused_undo_entry_write_nothing(self):
        self.assertTrue(self.controller.inspect("ancient-effigy-1").ok)
        token = self.controller.detail("ancient-effigy-1")["token"]
        before = self.snapshot()
        live = self.addon._state.player_data
        refused = self.controller.investigate(token, "mining")
        self.assertFalse(refused.ok)
        self.assertIs(self.addon._state.player_data, live)
        self.assertEqual(self.snapshot(), before)
        self.collection.accepts = False
        unavailable = self.controller.investigate(token, "cooking")
        self.assertFalse(unavailable.ok)
        self.assertEqual(unavailable.message, self.feature.UNDO_UNAVAILABLE)
        self.assertEqual(self.snapshot(), before)

    def test_save_and_after_apply_failures_roll_back(self):
        self.assertTrue(self.controller.inspect("ancient-effigy-1").ok)
        token = self.controller.detail("ancient-effigy-1")["token"]
        before = self.snapshot()
        original_save = self.addon.save_player_data

        def failing_save():
            raise RuntimeError("disk full")

        self.addon.save_player_data = failing_save
        with self.assertRaises(RuntimeError):
            self.controller.investigate(token, "cooking")
        self.assertEqual(self.snapshot(), before)
        self.addon.save_player_data = original_save

        def failing_check(_player):
            raise ValueError("achievement failure")

        self.addon.check_achievements = failing_check
        with self.assertRaises(ValueError):
            self.controller.investigate(token, "cooking")
        self.assertEqual(self.snapshot(), before)

    def test_the_ordinary_save_gives_an_earned_count_its_identity(self):
        data = self.addon._state.player_data
        data["inventory"]["Starved ancient effigy"] = 3
        self.addon.save_player_data()
        self.assertEqual(sorted(data[INSTANCES_KEY]), ["ancient-effigy-1", "ancient-effigy-2", "ancient-effigy-3"])
        stored = self.collection.values["ankiscape_player_data"]
        self.assertEqual(stored[INSTANCES_KEY], data[INSTANCES_KEY])


class _Signal:
    def __init__(self):
        self.slots = []

    def connect(self, slot):
        self.slots.append(slot)

    def emit(self, *args):
        for slot in list(self.slots):
            slot(*args)


class _Action:
    def __init__(self, title):
        self.title = title
        self.name = ""
        self.triggered = _Signal()

    def setObjectName(self, name):  # noqa: N802 (Qt shape)
        self.name = name

    def objectName(self):  # noqa: N802 (Qt shape)
        return self.name


class _Menu:
    def __init__(self):
        self._actions = []

    def actions(self):
        return list(self._actions)

    def addAction(self, title):  # noqa: N802 (Qt shape)
        action = _Action(title)
        self._actions.append(action)
        return action

    def removeAction(self, action):  # noqa: N802 (Qt shape)
        self._actions.remove(action)


class _LegacyHooks:
    """anki.hooks.addHook semantics: one list per name, no duplicate callbacks."""

    def __init__(self):
        self.hooks = {}

    def addHook(self, name, callback):  # noqa: N802 (Anki shape)
        bucket = self.hooks.setdefault(name, [])
        if callback not in bucket:
            bucket.append(callback)

    def run(self, name):
        for callback in list(self.hooks.get(name, [])):
            callback()


class FeatureHookTest(unittest.TestCase):
    def setUp(self):
        self.addon, self.feature, self.controller, _collection = load_feature(self, "ankiscape_effigy_hooks")
        self.menu = _Menu()
        self.addon.mw.form = types.SimpleNamespace(menuTools=self.menu)
        self.legacy = _LegacyHooks()
        self.gui = types.SimpleNamespace(profile_will_close=[])
        self.opened = []
        test = self

        class _Window:
            def __init__(self, controller, parent=None):
                test.opened.append((controller, parent))
                self.closed = False

            def refresh(self):
                pass

            def show(self):
                pass

            def raise_(self):
                pass

            def activateWindow(self):  # noqa: N802 (Qt shape)
                pass

            def close(self):
                self.closed = True

        sys.modules[f"{self.addon.__name__}.ui.ancient_effigies"] = types.SimpleNamespace(AncientEffigiesWindow=_Window)

    def tools_actions(self):
        return [action for action in self.menu.actions() if action.objectName() == self.feature.ACTION_OBJECT_NAME]

    def test_register_hooks_adds_one_idempotent_initializer_and_close_handler(self):
        hooks = sys.modules[f"{self.addon.__name__}.core.hooks"]
        hooks._REGISTERED = False
        hooks.addHook = self.legacy.addHook
        hooks.gui_hooks = types.SimpleNamespace(
            profile_will_close=self.gui.profile_will_close,
            reviewer_did_show_question=[], reviewer_did_show_answer=[], state_did_undo=[],
        )
        plan = hooks.register_hooks({"profile_loaded": [lambda: None]})
        self.assertEqual(plan["profileLoaded"], 2)
        self.assertEqual(len(self.legacy.hooks["profileLoaded"]), 2)
        self.feature.register_profile_hooks(self.addon.__name__, self.legacy.addHook, self.gui)
        self.feature.register_profile_hooks(self.addon.__name__, self.legacy.addHook, self.gui)
        self.assertEqual(len(self.legacy.hooks["profileLoaded"]), 2)
        self.assertEqual(self.gui.profile_will_close, [self.controller.on_profile_will_close])
        self.assertEqual(hooks.register_hooks({"profile_loaded": []}, dry_run=True)["profileLoaded"], 1)

    def test_profile_load_adds_one_tools_action_that_opens_the_window(self):
        self.feature.register_profile_hooks(self.addon.__name__, self.legacy.addHook, self.gui)
        self.legacy.run("profileLoaded")
        self.legacy.run("profileLoaded")
        actions = self.tools_actions()
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].title, "AnkiScape Ancient Effigies…")
        actions[0].triggered.emit(False)
        self.assertEqual(self.opened, [(self.controller, self.addon.mw)])
        actions[0].triggered.emit(False)
        self.assertEqual(len(self.opened), 1, "an open window is reused")

    def test_reload_replaces_the_previous_action(self):
        self.feature.register_profile_hooks(self.addon.__name__, self.legacy.addHook, self.gui)
        self.legacy.run("profileLoaded")
        stale = self.tools_actions()[0]
        self.feature._CONTROLLERS.clear()
        self.feature.register_profile_hooks(self.addon.__name__, self.legacy.addHook, self.gui)
        self.legacy.run("profileLoaded")
        actions = self.tools_actions()
        self.assertEqual(len(actions), 1)
        self.assertIsNot(actions[0], stale)

    def test_profile_close_closes_the_window_and_clears_references(self):
        self.feature.register_profile_hooks(self.addon.__name__, self.legacy.addHook, self.gui)
        self.legacy.run("profileLoaded")
        self.tools_actions()[0].triggered.emit(False)
        window = self.controller.window
        for callback in list(self.gui.profile_will_close):
            callback()
        self.assertTrue(window.closed)
        self.assertIsNone(self.controller.window)
        self.assertIsNone(self.controller.action)
        self.assertEqual(self.tools_actions(), [])


if __name__ == "__main__":
    unittest.main()
