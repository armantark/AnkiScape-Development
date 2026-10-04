"""Profile replacement and reviewer transactions share one explicit state owner."""

import copy
import sys
import types
import unittest

from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)
from ankiscape.core.constants import ITEM_DEFINITIONS


class DispatcherStateTest(unittest.TestCase):
    def setUp(self):
        self.original_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_dispatcher_state_test")
        self.state_module = sys.modules[
            f"{self.addon.__name__}.runtime.dispatcher_state"
        ]
        self.state = self.state_module.state
        self.addon.mw = _DummyMW(
            _DummyCol({"ankiscape_floating_xp_enabled": False})
        )
        self.addon.update_review_hud = lambda _data, _skill: None
        self.level_dialogs = []
        sys.modules[f"{self.addon.__name__}.core.logic"].show_level_up_dialog = (
            lambda skill, previous, current: self.level_dialogs.append((skill, previous, current))
        )
        self.saved = []
        self.addon.storage_save_player_data = lambda data, skill: self.saved.append(
            (copy.deepcopy(data), skill)
        )

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def test_profile_load_replaces_the_save_seen_by_contexts_and_persistence(self):
        self.assertFalse(hasattr(self.state, "player_data"))
        previous = {"inventory": {"Clay": 1}, "current_utility": "make_soft_clay"}
        self.addon.storage_load_player_data = lambda: (previous, "Utility")
        self.addon.load_player_data()
        self.assertIs(self.addon._runtime_action_context().player_data, previous)
        self.assertEqual(self.state.current_skill, "Utilities")

        replacement = {"inventory": {"Logs": 2}, "current_firemaking": "logs"}
        self.addon.storage_load_player_data = lambda: (replacement, "Firemaking")
        self.addon.load_player_data()
        self.assertIs(self.state.player_data, replacement)
        self.assertIs(self.addon._runtime_action_context().player_data, replacement)
        self.addon.save_player_data()
        self.assertEqual(self.saved[-1], (replacement, "Firemaking"))
        self.assertEqual(previous["inventory"], {"Clay": 1})

    def test_review_hooks_earn_once_and_undo_the_shared_save(self):
        self.state.player_data = {
            "inventory": {"Logs": 2},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        self.state.current_skill = "Firemaking"
        self.addon.check_achievements = lambda _data: None
        self.addon.show_error_message = lambda _title, message: self.fail(message)
        self.addon.save_player_data()
        before = copy.deepcopy(self.state.player_data)
        original_random = self.addon.random.getstate()
        self.addCleanup(self.addon.random.setstate, original_random)
        random_roll = self.addon.random.random

        def successful_roll():
            random_roll()
            return 0.0

        self.addon.random.random = successful_roll
        self.addCleanup(setattr, self.addon.random, "random", random_roll)

        self.addon.on_card_did_show(None)
        self.assertTrue(self.state.card_turned)
        self.assertFalse(self.state.answer_shown)
        self.addon.on_show_answer(None)
        self.assertTrue(self.state.answer_shown)
        result = self.addon.on_answer_card(
            _FakeReviewer(), 4, lambda _reviewer, _ease: "answered"
        )
        self.assertEqual(result, "answered")
        self.assertEqual(self.state.player_data["inventory"], {"Logs": 1, "Ashes": 1})
        self.assertEqual(self.state.player_data["firemaking_exp"], 40.0)
        self.assertEqual(
            [row["text"] for row in self.state.player_data["review_event_log"] if row["kind"] == "xp"],
            ["+40 XP · Firemaking"],
        )
        self.assertEqual(len(self.state.review_undo_stack), 1)
        self.assertFalse(self.state.card_turned)
        self.assertFalse(self.state.answer_shown)
        self.assertIsNone(self.state.review_feedback_context)
        self.assertFalse(self.state.review_feedback_flushing)
        self.assertEqual(self.saved[-1][0], self.state.player_data)
        self.assertNotEqual(self.addon.random.getstate(), original_random)

        after = copy.deepcopy(self.state.player_data)
        self.state.exp_awarded = True
        self.addon.on_good_answer()
        self.assertEqual(self.state.player_data, after)
        self.assertEqual(len(self.state.review_undo_stack), 1)

        self.addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(self.state.player_data, before)
        self.assertEqual(self.state.review_undo_stack, [])
        self.assertEqual(self.addon.random.getstate(), original_random)
        self.assertEqual(self.saved[-1], (before, "Firemaking"))

    def test_rejected_answer_keeps_the_final_log_for_one_paid_retry(self):
        self.state.player_data = {
            "inventory": {"Logs": 1},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        self.state.current_skill = "Firemaking"
        popups = []
        # A burn that completes an achievement queues its popup until the
        # answer is accepted, as the deferred achievement check does in Qt.
        self.addon.check_achievements = lambda _data: self.state.pending_review_dialogs.append(
            lambda: popups.append("achievement")
        )
        self.addon.show_error_message = lambda _title, message: self.fail(message)
        self.addon.save_player_data()
        before = copy.deepcopy(self.state.player_data)
        original_random = self.addon.random.getstate()
        self.addCleanup(self.addon.random.setstate, original_random)
        random_roll = self.addon.random.random

        def successful_roll():
            random_roll()
            return 0.0

        def reject(_reviewer, _ease):
            raise RuntimeError("Anki rejected the answer")

        self.addon.random.random = successful_roll
        self.addCleanup(setattr, self.addon.random, "random", random_roll)
        self.addon.on_card_did_show(None)
        self.addon.on_show_answer(None)

        with self.assertRaisesRegex(RuntimeError, "rejected"):
            self.addon.on_answer_card(types.SimpleNamespace(state="answer"), 4, reject)
        self.assertEqual(self.state.player_data, before)
        self.assertEqual(self.saved[-1], (before, "Firemaking"))
        self.assertEqual(self.addon.random.getstate(), original_random)
        self.assertEqual(self.state.review_undo_stack, [])
        self.assertEqual(self.state.pending_review_dialogs, [])

        # Anki leaves the card on its answer side, so the same press retries.
        self.assertEqual(
            self.addon.on_answer_card(_FakeReviewer(), 4, lambda *_args: "answered"),
            "answered",
        )
        self.assertEqual(self.state.player_data["firemaking_exp"], 40.0)
        self.assertEqual(self.state.player_data["inventory"].get("Logs", 0), 0)
        self.assertEqual(self.state.player_data["inventory"]["Ashes"], 1)
        self.assertEqual(self.saved[-1][0], self.state.player_data)
        self.assertEqual(popups, ["achievement"])
        self.assertEqual(len(self.state.review_undo_stack), 1)
        self.addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(self.state.player_data, before)
        self.assertEqual(self.addon.random.getstate(), original_random)

    def test_vetoed_answer_keeps_the_final_log_for_one_paid_retry(self):
        self.state.player_data = {
            "inventory": {"Logs": 1},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        self.state.current_skill = "Firemaking"
        self.addon.check_achievements = lambda _data: None
        self.addon.save_player_data()
        before = copy.deepcopy(self.state.player_data)
        original_random = self.addon.random.getstate()
        self.addCleanup(self.addon.random.setstate, original_random)
        random_roll = self.addon.random.random

        def successful_roll():
            random_roll()
            return 0.0

        def accept(reviewer, _ease):
            reviewer.state = "transition"
            return "answered"

        self.addon.random.random = successful_roll
        self.addCleanup(setattr, self.addon.random, "random", random_roll)
        # A reviewer_will_answer_card veto returns before Anki leaves the answer side.
        reviewer = types.SimpleNamespace(state="answer")
        self.addon.on_card_did_show(None)
        self.addon.on_show_answer(None)
        self.assertIsNone(self.addon.on_answer_card(reviewer, 4, lambda *_args: None))
        self.assertEqual(self.state.player_data, before)
        self.assertEqual(self.saved[-1], (before, "Firemaking"))
        self.assertEqual(self.addon.random.getstate(), original_random)
        self.assertEqual(self.state.review_undo_stack, [])

        self.assertEqual(self.addon.on_answer_card(reviewer, 4, accept), "answered")
        self.assertEqual(self.state.player_data["firemaking_exp"], 40.0)
        self.assertEqual(self.state.player_data["inventory"].get("Logs", 0), 0)
        self.assertEqual(self.state.player_data["inventory"]["Ashes"], 1)
        self.assertEqual(self.saved[-1][0], self.state.player_data)
        self.assertEqual(len(self.state.review_undo_stack), 1)

    def test_rejected_answer_out_of_logs_leaves_no_stale_bankstanding_notice(self):
        self.state.player_data = {
            "inventory": {},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        self.state.current_skill = "Firemaking"
        self.addon.check_achievements = lambda _data: None
        notices = []
        self.addon.ui.show_bankstanding_dialog = notices.append
        self.addCleanup(self.addon.random.setstate, self.addon.random.getstate())
        random_roll = self.addon.random.random
        self.addon.random.random = lambda: random_roll() * 0.0
        self.addCleanup(setattr, self.addon.random, "random", random_roll)

        def reject(_reviewer, _ease):
            raise RuntimeError("Anki rejected the answer")

        self.addon.on_card_did_show(None)
        self.addon.on_show_answer(None)
        with self.assertRaisesRegex(RuntimeError, "rejected"):
            self.addon.on_answer_card(types.SimpleNamespace(state="answer"), 4, reject)
        self.assertEqual(self.state.current_skill, "Firemaking")
        self.assertEqual(self.addon.mw.col.get_config("ankiscape_current_skill"), "Firemaking")

        # The player fetches a log, then presses the same answer again.
        self.addon.commit_direct_action(
            lambda current: ({**current, "inventory": {"Logs": 1}}, True)
        )
        self.addon.on_answer_card(_FakeReviewer(), 4, lambda *_args: "answered")
        self.assertEqual(self.state.player_data["inventory"].get("Logs", 0), 0)
        self.assertEqual(self.state.player_data["firemaking_exp"], 40.0)
        self.assertEqual(notices, [])

    def test_answer_failing_after_anki_leaves_the_answer_side_is_not_re_armed(self):
        self.state.player_data = {
            "inventory": {"Logs": 1},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        self.state.current_skill = "Firemaking"
        self.addon.check_achievements = lambda _data: None
        self.addCleanup(self.addon.random.setstate, self.addon.random.getstate())
        random_roll = self.addon.random.random
        self.addon.random.random = lambda: random_roll() * 0.0
        self.addCleanup(setattr, self.addon.random, "random", random_roll)

        def launch_fails(reviewer, _ease):
            # Anki's reviewer moves to "transition" before it starts the answer op.
            reviewer.state = "transition"
            raise RuntimeError("answer op failed after the transition")

        reviewer = types.SimpleNamespace(state="answer")
        self.addon.on_card_did_show(None)
        self.addon.on_show_answer(None)
        with self.assertRaisesRegex(RuntimeError, "after the transition"):
            self.addon.on_answer_card(reviewer, 4, launch_fails)
        after_failure = copy.deepcopy(self.state.player_data)
        undo_depth = len(self.state.review_undo_stack)
        self.assertEqual(after_failure["inventory"].get("Logs", 0), 0)

        # Anki ignores presses outside its answer side, so they must not pay.
        self.addon.on_answer_card(reviewer, 4, lambda *_args: None)
        self.assertEqual(self.state.player_data, after_failure)
        self.assertEqual(len(self.state.review_undo_stack), undo_depth)

    def test_direct_selection_and_undo_publish_the_shared_skill_and_save(self):
        self.state.player_data = {"inventory": {}, "current_utility": "bankstanding"}
        self.state.current_skill = "Utilities"
        self.addon.save_player_data()
        before = copy.deepcopy(self.state.player_data)
        self.assertTrue(
            self.addon.commit_direct_action(
                lambda current: ({**current, "current_firemaking": "logs"}, True),
                selected_skill="Firemaking",
            )
        )
        self.assertEqual(self.state.current_skill, "Firemaking")
        self.assertEqual(self.saved[-1][1], "Firemaking")
        self.assertEqual(self.state.player_data["current_firemaking"], "logs")
        self.assertEqual(len(self.state.direct_action_undo_stack), 1)

        self.addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(self.state.current_skill, "Utilities")
        self.assertEqual(self.state.player_data, before)
        self.assertEqual(self.state.direct_action_undo_stack, [])
        self.assertEqual(self.saved[-1], (before, "Utilities"))

    def test_lower_state_notice_queue_drains_once_through_the_dispatcher(self):
        self.state.player_data = {"current_utility": "make_soft_clay"}
        self.state.current_skill = "Utilities"
        notices = []
        self.addon.ui.show_bankstanding_dialog = notices.append
        self.assertTrue(self.addon._switch_to_bankstanding("Clay ran out."))
        self.assertEqual(self.state.player_data["current_utility"], "bankstanding")
        self.assertEqual(self.state.pending_bankstanding_notice["reason"], "Clay ran out.")
        self.addon._show_pending_bankstanding_dialog()
        self.addon._show_pending_bankstanding_dialog()
        self.assertEqual(notices, ["Clay ran out."])
        self.assertIsNone(self.state.pending_bankstanding_notice)

        completed = []
        self.state.pending_review_dialogs.append(lambda: completed.append("achievement"))
        self.addon._show_pending_review_dialogs()
        self.addon._show_pending_review_dialogs()
        self.assertEqual(completed, ["achievement"])
        self.assertEqual(self.state.pending_review_dialogs, [])

    def _menu(self, player, skill="Activities"):
        self.state.player_data = player
        self.state.current_skill = skill
        captured = {}
        self.addon.ui.show_main_menu = lambda *_args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu()
        return captured

    def test_activity_commands_publish_real_changes_and_undo_the_saved_profile(self):
        from tests import (
            test_bork, test_crucible, test_dominion_tower, test_enchanted_key,
            test_fish_flingers, test_gnome_restaurant, test_goblin_raids,
            test_mage_training_arena, test_mobilising_armies, test_ranging_guild,
            test_skeletal_horror, test_tears_of_guthix, test_temple_trekking,
        )
        from ankiscape.core.storage_pure import default_player_data

        cases = (
            ("bork", test_bork._player(), "enter", {}, "bork"),
            ("skeletal_horror", test_skeletal_horror._unlocked(), "enter", {}, "skeletal_horror"),
            ("tears_of_guthix", test_tears_of_guthix._player(), "enter", {}, "tears_of_guthix"),
            ("enchanted_key", test_enchanted_key._player(), "select_site", {"site_id": test_enchanted_key.ENCHANTED_KEY_SITE_IDS[0]}, "enchanted_key"),
            ("fish_flingers", test_fish_flingers._player(), "enter_fish_flingers", {}, "fish_flingers"),
            ("dungeoneering", default_player_data(self.addon.ORE_DATA, ITEM_DEFINITIONS), "enter", {}, "dungeoneering"),
            ("mage_training_arena", test_mage_training_arena._player(), "enter", {}, "mage_training_arena"),
            ("ranging_guild", test_ranging_guild._player(), "enter", {}, "ranging_guild"),
            ("dominion_tower", test_dominion_tower._player(*test_dominion_tower._twenty_quests()), "talk_to_face", {}, "dominion_tower"),
            ("temple_trekking", test_temple_trekking._player(), "prepare_pouch", {}, "temple_trekking"),
            ("mobilising_armies", test_mobilising_armies._mustered(), "enter", {}, "mobilising_armies"),
            ("gnome_restaurant", test_gnome_restaurant._player(), "open_service", {}, "gnome_restaurant"),
            ("crucible", test_crucible._player(), "enter", {}, "crucible"),
            ("goblin_raids", test_goblin_raids._with_raid(), "join", {"mode": test_goblin_raids.GOBLIN_RAIDS_RAID_MODE}, "goblin_raids"),
        )
        self.addon.check_achievements = lambda _data: None
        self.addon.show_error_message = lambda _title, message: self.fail(message)
        original_random = self.addon.random.getstate()
        self.addCleanup(self.addon.random.setstate, original_random)
        for activity, player, command, payload, changed_key in cases:
            with self.subTest(activity=activity):
                self.state.direct_action_undo_stack.clear()
                menu = self._menu(player)
                self.addon.save_player_data()
                before = copy.deepcopy(self.state.player_data)
                result = menu[f"on_{activity}_command"](command, payload)
                self.assertTrue(result["ok"], result)
                self.assertNotEqual(self.state.player_data.get(changed_key), before.get(changed_key))
                self.assertIs(self.addon._runtime_action_context().player_data, self.state.player_data)
                self.assertEqual(self.saved[-1][0], self.state.player_data)
                self.assertEqual(len(self.state.direct_action_undo_stack), 1)
                self.addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
                self.assertEqual(self.state.player_data, before)
                self.assertEqual(self.saved[-1], (before, "Activities"))
                self.assertEqual(self.state.direct_action_undo_stack, [])

    def test_reward_commands_award_once_and_undo_xp_and_consumed_rewards(self):
        from tests import test_shattered_heart, test_troll_invasion

        rocks = test_shattered_heart._player()
        rocks.update(agility_level=50, agility_exp=12_345.0)
        test_shattered_heart._give_pair(rocks, "agility")
        book = test_troll_invasion._player(troll_invasion_reward_fractions=[1.0])
        book["inventory"]["Troll Invasion reward book"] = 1
        self.addon.check_achievements = lambda _data: None
        for activity, player, command, payload in (
            ("shattered_heart", rocks, "add_completed_pairs", {}),
            ("troll_invasion", book, "redeem_book", {"skill_id": "agility"}),
        ):
            with self.subTest(activity=activity):
                menu = self._menu(player)
                self.addon.save_player_data()
                before = copy.deepcopy(player)
                result = menu[f"on_{activity}_command"](command, payload)
                self.assertTrue(result["ok"], result)
                self.assertGreater(result["awarded_xp"], 0)
                self.assertEqual(self.state.player_data["agility_exp"], before["agility_exp"] + result["awarded_xp"])
                self.assertNotEqual(self.state.player_data["inventory"], before["inventory"])
                self.assertEqual(self.saved[-1][0], self.state.player_data)
                self.addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
                self.assertEqual(self.state.player_data, before)
                self.assertEqual(self.saved[-1][0], before)

    def test_failed_reward_book_keeps_the_book_for_a_retry_and_a_harmless_undo(self):
        from tests import test_troll_invasion

        book_name = "Troll Invasion reward book"
        record_save = self.addon.storage_save_player_data
        failed_saves = []

        def fail_level_up(_skill, _data):
            raise RuntimeError("level-up dialog failed")

        def fail_one_save(data, skill):
            if not failed_saves:
                failed_saves.append(skill)
                raise RuntimeError("database is locked")
            record_save(data, skill)

        self.addon.check_achievements = lambda _data: None
        for name, fault in (
            ("level_up_check", fail_level_up),
            ("storage_save_player_data", fail_one_save),
        ):
            with self.subTest(fault=name):
                self.addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": False}))
                book = test_troll_invasion._player(troll_invasion_reward_fractions=[1.0])
                book["inventory"][book_name] = 1
                menu = self._menu(book)
                self.addon.save_player_data()
                untouched = copy.deepcopy(book)
                # An earlier action proves the failed attempt's undo entry
                # cannot reach past itself and take back unrelated work.
                self.addon.commit_direct_action(
                    lambda current: ({**current, "world_population_profile": "busy"}, True)
                )
                before = copy.deepcopy(self.state.player_data)
                random_before = self.addon.random.getstate()
                refreshes = self.addon.mw.undo_updates
                original = getattr(self.addon, name)
                setattr(self.addon, name, fault)
                with self.assertRaises(RuntimeError):
                    menu["on_troll_invasion_command"]("redeem_book", {"skill_id": "agility"})
                setattr(self.addon, name, original)
                self.assertEqual(self.state.player_data, before)
                self.assertEqual(self.saved[-1][0], before)
                self.assertEqual(self.addon.random.getstate(), random_before)
                # The failed attempt's Anki entry stays, so the Undo menu must show it.
                self.assertGreater(self.addon.mw.undo_updates, refreshes)

                result = menu["on_troll_invasion_command"]("redeem_book", {"skill_id": "agility"})
                self.assertTrue(result["ok"], result)
                self.assertEqual(
                    self.state.player_data["agility_exp"],
                    before["agility_exp"] + result["awarded_xp"],
                )
                self.assertEqual(self.state.player_data["inventory"].get(book_name, 0), 0)
                self.assertEqual(self.saved[-1][0], self.state.player_data)
                self.assertEqual(
                    len(self.state.direct_action_undo_stack),
                    len(self.addon.mw.col.custom_undo_entries),
                )
                for _entry in ("retry", "failed attempt"):
                    self.addon._on_state_did_undo(
                        types.SimpleNamespace(operation="AnkiScape direct action")
                    )
                    self.assertEqual(self.state.player_data, before)
                    self.assertEqual(self.saved[-1][0], before)
                self.addon._on_state_did_undo(
                    types.SimpleNamespace(operation="AnkiScape direct action")
                )
                self.assertEqual(self.state.player_data, untouched)
                self.assertEqual(self.state.direct_action_undo_stack, [])

    def test_reward_whose_skill_key_stays_locked_keeps_the_stored_book(self):
        from tests import test_troll_invasion

        class DBError(Exception):
            pass

        book_name = "Troll Invasion reward book"
        collection = self.addon.mw.col
        locked = []

        def json_config(key, value):
            if locked and key == "ankiscape_current_skill":
                raise DBError("database is locked")
            collection._store[key] = copy.deepcopy(value)

        collection.set_config = json_config
        storage = sys.modules[f"{self.addon.__name__}.core.storage"]
        storage.mw = self.addon.mw
        self.addon.storage_save_player_data = storage.save_player_data
        self.addon.check_achievements = lambda _data: None
        book = test_troll_invasion._player(troll_invasion_reward_fractions=[1.0])
        book["inventory"][book_name] = 1
        menu = self._menu(book)
        self.addon.save_player_data()
        before = copy.deepcopy(self.state.player_data)
        # The profile row saves, then the skill row keeps failing.
        locked.append(True)
        for _attempt in ("first press", "retry while locked"):
            with self.assertRaises(DBError):
                menu["on_troll_invasion_command"]("redeem_book", {"skill_id": "agility"})
            self.assertEqual(self.state.player_data, before)
            self.assertEqual(collection.get_config("ankiscape_player_data"), before)

        locked.clear()
        result = menu["on_troll_invasion_command"]("redeem_book", {"skill_id": "agility"})
        self.assertTrue(result["ok"], result)
        stored = collection.get_config("ankiscape_player_data")
        self.assertEqual(stored["inventory"].get(book_name, 0), 0)
        self.assertEqual(stored["agility_exp"], before["agility_exp"] + result["awarded_xp"])
        self.addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(collection.get_config("ankiscape_player_data"), before)

    def test_selection_dialogs_persist_the_shared_targets_and_skill(self):
        self.state.player_data = {}
        self.addon.mw.col.set_config("ankiscape_current_skill", "Utility")
        self.addon.initialize_skill()
        self.assertEqual(self.state.current_skill, "Utilities")
        self.assertEqual(self.addon.mw.col.get_config("ankiscape_current_skill"), "Utilities")
        self.addon.ui.show_skill_selection_dialog = lambda *_args: "Mining"
        self.addon.show_skill_selection()
        self.assertEqual(self.state.current_skill, "Mining")
        self.assertEqual(self.addon.mw.col.get_config("ankiscape_current_skill"), "Mining")
        cases = (
            (self.addon.ui, "show_bar_selection_dialog", "show_bar_selection", "current_bar", "Bronze bar"),
            (self.addon, "show_tree_selection_dialog", "show_tree_selection", "current_tree", "tree"),
            (self.addon, "show_ore_selection_dialog", "show_ore_selection", "current_ore", "copper"),
        )
        for owner, dialog, callback, field, selection in cases:
            with self.subTest(field=field):
                setattr(owner, dialog, lambda selection=selection, **_kwargs: selection)
                getattr(self.addon, callback)()
                self.assertEqual(self.state.player_data[field], selection)
                self.assertEqual(self.saved[-1][0][field], selection)
        self.assertEqual(self.state.player_data["current_smith"], "smelt_bronze_bar")

    def test_carried_menu_callbacks_read_live_state_and_save_preferences(self):
        menu = self._menu({"inventory": {}, "current_ore": "copper"}, "Mining")
        target = menu["active_carried_target_id"]
        self.assertIsNotNone(target)
        menu["on_set_carried_keep_drop"](True)
        menu["on_set_carried_advanced"](True)
        menu["on_set_loot_override"]("Bones", "leave")
        self.assertEqual(self.state.player_data["carried_keep_drop"], {target: "drop"})
        self.assertEqual(self.state.player_data["carried_advanced_targets"], {target: True})
        self.assertEqual(self.saved[-1][0]["loot_overrides"], {"Bones": "leave"})
        self.assertTrue(menu["on_set_carried_layout_quantity"]("Copper ore", 2))
        self.state.player_data["carried_inventory"] = {target: {"Copper ore": 3}}
        self.assertEqual(menu["get_carried_inventory_items"](), (("Copper ore", 3),))
        menu["on_clear_carried_layout"]()
        self.assertNotIn(target, self.saved[-1][0]["carried_layout"])
        menu["on_set_carried_keep_drop"](False)
        menu["on_set_carried_advanced"](False)
        menu["on_set_loot_override"]("Bones", "auto")
        self.assertEqual(self.state.player_data["carried_keep_drop"], {})
        self.assertEqual(self.state.player_data["carried_advanced_targets"], {})
        self.assertEqual(self.state.player_data["loot_overrides"], {})

    def test_house_purchases_and_training_policies_use_the_current_profile(self):
        from ankiscape.core.storage_pure import default_player_data

        player = default_player_data(self.addon.ORE_DATA, ITEM_DEFINITIONS)
        player.update(construction_level=99, inventory={"Coins": 600_000})
        self.addon.check_achievements = lambda _data: None
        menu = self._menu(player, "Construction")
        self.assertTrue(menu["on_purchase_house"]())
        self.assertTrue(menu["on_purchase_room"]("bedroom"))
        self.assertTrue(menu["on_hire_servant"]("butler"))
        self.assertTrue(menu["on_set_house_style"]("whitewashed_stone"))
        self.assertTrue(self.state.player_data["house_owned"])
        self.assertTrue(self.state.player_data["house_rooms_bought"]["bedroom"])
        self.assertEqual(self.state.player_data["house_servant"], "butler")
        self.assertEqual(self.state.player_data["house_style"], "whitewashed_stone")
        self.assertLess(self.state.player_data["inventory"]["Coins"], 600_000)
        self.assertEqual(self.saved[-1][0], self.state.player_data)
        self.assertTrue(menu["on_hire_servant"](""))
        self.assertEqual(self.saved[-1][0]["house_servant"], "")
        craft = "form_pot_unfired"
        self.assertTrue(menu["on_set_skilling_potion_target"]("crafting", craft, True))
        self.assertEqual(self.state.player_data["skilling_potion_targets"], {"crafting": {craft: True}})
        self.assertEqual(self.state.player_data["current_craft"], craft)
        cooking = "cook_shrimps"
        self.assertTrue(menu["on_set_cooking"](cooking))
        self.assertEqual(self.saved[-1][0]["current_cooking"], cooking)
        self.state.player_data["farming_level"] = 37
        self.state.player_data["farming_exp"] = 27_473.0
        projection = menu["get_farming_projection"]()
        self.assertEqual((projection["level"], projection["xp"]), (37, 27_473.0))
        result = menu["on_achievement_diary_command"]("pin_task", {"task_id": "lumbridge_easy_iron_on"})
        self.assertTrue(result["ok"], result)
        self.assertEqual(self.saved[-1][0]["achievement_diaries"]["pinned_task"], "lumbridge_easy_iron_on")

    def test_tools_quest_choices_and_hidden_xp_share_the_profile_save(self):
        from ankiscape.core.storage_pure import default_player_data

        self.state.player_data = default_player_data(self.addon.ORE_DATA, ITEM_DEFINITIONS)
        self.state.current_skill = "Mining"
        self.state.player_data["toolbelt"] = {}
        self.state.player_data["inventory"].update({"Bronze pickaxe": 1, "Rogue kit": 1, "Clay": 1})
        self.assertTrue(self.addon.on_attach_tool("Bronze pickaxe"))
        self.assertNotIn("Bronze pickaxe", self.state.player_data["inventory"])
        self.assertTrue(self.state.player_data["toolbelt"])
        self.addon.save_player_data()
        before = copy.deepcopy(self.state.player_data)
        self.assertIsNotNone(self.addon.on_convert_rogue_kit("Chisel"))
        self.assertEqual(self.state.player_data["inventory"]["Chisel"], before["inventory"].get("Chisel", 0) + 1)
        self.addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(self.state.player_data, before)
        self.assertTrue(self.addon.create_soft_clay())
        self.assertEqual(self.state.player_data["inventory"]["Soft clay"], 1)
        self.addon._award_hidden_skill_exp("dungeoneering_exp", "dungeoneering_level", 100)
        self.assertEqual(self.state.player_data["dungeoneering_exp"], 100)
        self.assertEqual(self.state.player_data["dungeoneering_level"], 2)
        self.assertTrue(self.addon.on_set_quest("hazeel_cult"))
        self.assertTrue(self.addon.on_set_quest_route_choice("hazeel_cult", "Side with Hazeel's cult"))
        self.assertEqual(self.saved[-1][0]["quest_route_states"]["hazeel_cult"], ["Side with Hazeel's cult"])
        self.assertTrue(self.addon._set_combat_prayer_config("pin_target_preset", True))
        target = str(self.state.player_data.get("current_combat_target", ""))
        self.assertEqual(self.saved[-1][0]["combat_target_presets"][target], "Default")

    def test_prayer_settings_keep_target_overrides_and_quest_gates_in_the_save(self):
        from ankiscape.core.storage_pure import default_player_data

        self.state.player_data = default_player_data(self.addon.ORE_DATA, ITEM_DEFINITIONS)
        self.state.current_skill = "Combat"
        target = str(self.state.player_data.get("current_combat_target", ""))
        set_prayer_config = self.addon._set_combat_prayer_config

        self.assertTrue(set_prayer_config("target_override", ("combat_prayer_uptime", True)))
        self.assertTrue(set_prayer_config("combat_prayer_uptime", "70"))
        self.assertEqual(self.saved[-1][0]["combat_target_overrides"][target]["combat_prayer_uptime"], "70")
        self.assertTrue(set_prayer_config("apply_preset", "Default"))
        self.assertEqual(self.saved[-1][0]["combat_prayer_uptime"], "70")

        self.assertTrue(set_prayer_config("combat_prayer_book", "curses"))
        self.assertEqual(self.saved[-1][0]["combat_prayer_book"], "standard")
        self.state.player_data["quests"] = {"the_temple_at_senntisten": {"completed": True}}
        self.assertTrue(set_prayer_config("combat_prayer_book", "curses"))
        self.assertEqual(self.saved[-1][0]["combat_prayer_book"], "curses")

    def test_no_xp_review_combines_repeated_activity_results_into_one_popup(self):
        popup_texts = []
        self.addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": True}))
        self.addon.mw.exp_popup = types.SimpleNamespace(show_text=popup_texts.append)
        self.state.player_data = {"inventory": {}, "review_event_log": []}
        self.state.current_skill = "Utilities"
        reviews = (
            (("+2 Soft clay", "+3 Soft clay"), "+5 Soft clay"),
            (("Opened 1 bird nest", "Opened 2 bird nests"), "Opened 3 bird nests"),
            (("+2 Soft clay", "Opened 1 bird nest"), "Opened 1 bird nest"),
        )

        for messages, _popup in reviews:
            self.addon._begin_review_feedback_context()
            for message in messages:
                self.addon._show_activity_gain(message)
            self.addon._finish_review_feedback_context()

        self.assertEqual(popup_texts, [popup for _messages, popup in reviews])

    def test_near_death_confirmation_runs_after_the_review_and_saves_leaving(self):
        from enum import IntFlag

        class Buttons(IntFlag):
            Yes = 1
            No = 2

        prompts = []
        sys.modules["aqt.qt"].QMessageBox = types.SimpleNamespace(
            StandardButton=Buttons,
            question=lambda *_args: prompts.append("asked") or Buttons.Yes,
        )
        self.state.player_data = {"inventory": {}, "combat_encounter": {"enemy_id": "goblin"}}
        self.state.current_skill = "Combat"
        self.addon._prompt_near_death("combat")
        self.assertEqual(prompts, [])
        self.assertEqual(self.state.player_data["combat_encounter"], {"enemy_id": "goblin"})
        self.addon._show_pending_review_dialogs()
        self.assertEqual(prompts, ["asked"])
        self.assertEqual(self.state.player_data["combat_encounter"], {})
        self.assertEqual(self.saved[-1][0]["combat_encounter"], {})
        self.addon._show_pending_review_dialogs()
        self.assertEqual(prompts, ["asked"])
