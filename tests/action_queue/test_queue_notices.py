"""Queue changes are visible in the log and HUD while study continues."""
from __future__ import annotations

import types
from unittest.mock import patch

from tests.action_queue.test_queue_reviews import _MINE_IRON, QueueProfile

_PIRATE = {"kind": "quest", "quest_id": "pirates_treasure"}
_RUNE_MYSTERIES = {"kind": "quest", "quest_id": "rune_mysteries"}
_COOKS_ASSISTANT = {"kind": "quest", "quest_id": "cooks_assistant"}
_WILD = {"kind": "combat", "target": "earth_warrior", "combat_action": "attack"}


class QueueNoticeTest(QueueProfile):
    def _notice(self, addon):
        from ankiscape.core.action_queue import queue_notice_view_pure

        return queue_notice_view_pure(addon._state.player_data)

    def _pirate(self, name, *next_entries):
        return self._queue_addon(name, (_PIRATE, None), *next_entries,
                                inventory={"Karamjan rum": 1, "Spade": 1})

    def test_pirates_treasure_continues_with_one_completion_line_and_no_dialog(self):
        addon = self._pirate("ankiscape_queue_pirate_next", (_MINE_IRON, 30))
        for _card in range(3):
            self._answer(addon)
        self.assertTrue(addon._state.player_data["quests"]["pirates_treasure"]["completed"])
        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertEqual((self.errors, self.bankstanding_dialogs), ([], []))
        line = "Pirate's Treasure complete. Next: Mining."
        self.assertEqual(self._log(addon).count(line), 1)
        self.assertEqual(self._notice(addon), line)
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(self._notice(addon), "")

    def test_a_queue_change_from_the_menu_takes_the_line_off_the_hud_and_the_event_log_keeps_it(self):
        from ankiscape.core.action_queue import action_queue_pure, apply_action_queue_command, stop_action

        def remove(addon, position):
            entry = action_queue_pure(addon._state.player_data)["entries"][position]
            return {"position": position, "entry": entry}

        def pause(addon):
            stop_action(addon)
            return {}

        line = "Pirate's Treasure complete. Next: Mining."
        for case, (command, payload_for) in enumerate((
            ("move", lambda addon: {"position": 1, "new_index": 0}),
            ("remove", lambda addon: remove(addon, 0)),
            ("remove", lambda addon: remove(addon, 1)),
            ("add", lambda addon: {"action": _MINE_IRON, "count": 5}),
            ("clear", lambda addon: {}),
            ("resume", pause),
        )):
            with self.subTest(command=command, case=case):
                addon = self._pirate(f"ankiscape_queue_stale_{case}", (_MINE_IRON, 30), (_RUNE_MYSTERIES, None))
                for _card in range(3):
                    self._answer(addon)
                self.assertEqual(self._notice(addon), line)

                self.assertTrue(apply_action_queue_command(addon, command, payload_for(addon))["ok"])

                self.assertEqual(self._notice(addon), "")
                self.assertEqual(self._log(addon).count(line), 1)

    def test_a_refused_change_keeps_the_line_and_undo_brings_it_back(self):
        from ankiscape.core.action_queue import apply_action_queue_command

        line = "Pirate's Treasure complete. Next: Mining."
        addon = self._pirate("ankiscape_queue_stale_undo", (_MINE_IRON, 30), (_RUNE_MYSTERIES, None))
        for _card in range(3):
            self._answer(addon)

        self.assertFalse(apply_action_queue_command(addon, "move", {"position": 1, "new_index": 2})["ok"])
        self.assertEqual(self._notice(addon), line)

        self.assertTrue(apply_action_queue_command(addon, "move", {"position": 1, "new_index": 0})["ok"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(self._notice(addon), line)

    def test_an_entry_a_move_passes_still_shows_its_own_line(self):
        from ankiscape.core.action_queue import apply_action_queue_command

        addon = self._pirate("ankiscape_queue_stale_passes", (_MINE_IRON, 30), (_COOKS_ASSISTANT, None))
        for _card in range(3):
            self._answer(addon)
        addon._state.player_data["quests"]["cooks_assistant"] = {"completed": True}

        self.assertTrue(apply_action_queue_command(addon, "move", {"position": 1, "new_index": 0})["ok"])

        self.assertEqual(self._notice(addon), "Queue: Cook's Assistant stopped · it could not start")

    def test_pirates_treasure_without_a_successor_keeps_the_old_popup(self):
        addon = self._pirate("ankiscape_queue_pirate_last")
        for _card in range(3):
            self._answer(addon)
        self.assertEqual(self.errors, [("Quest complete", "Pirate's Treasure is complete, so questing has been switched off. Open the AnkiScape menu to pick another quest.")])
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")

    def test_a_quest_with_lamps_names_them_after_the_next_entry(self):
        from ankiscape.core.constants import CLAIM_DATA, QUEST_DATA
        from ankiscape.logic_pure.logic_pure import quest_lamps_waiting_text_pure

        quest = "carnillean_rising"
        addon = self._queue_addon("ankiscape_queue_lamp_next", (_MINE_IRON, 30))
        # A saved quest on its last step uses its real rewards and completion handler.
        for key in addon._state.player_data:
            if key.endswith("_level"):
                addon._state.player_data[key] = 99
        addon._state.player_data["quests"].update({qid: {"completed": True} for qid in QUEST_DATA})
        addon._state.player_data["quests"][quest] = {"started": True, "progress": QUEST_DATA[quest]["stages"] - 1}
        addon._state.player_data["current_quest"] = quest
        addon.save_skill("Quests", None)
        self._answer(addon)
        lamps = quest_lamps_waiting_text_pure(addon._state.player_data, quest, CLAIM_DATA)
        self.assertTrue(lamps)
        self.assertEqual(self._notice(addon), f"Carnillean Rising complete. Next: Mining. {lamps}")
        self.assertEqual(self.errors, [])

    def test_a_locked_activity_is_skipped_in_the_same_review_without_a_dialog(self):
        locked = {"kind": "utility", "utility_id": "search_jungle_palm_trees"}
        addon = self._queue_addon("ankiscape_queue_locked_notice", (locked, 1), (_MINE_IRON, 30))
        self._answer(addon)
        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertEqual((self.errors, self.bankstanding_dialogs), ([], []))
        self.assertIn("requires Jungle Potion", self._notice(addon))
        self.assertEqual(len(self._rows(addon)), 1)

    def test_a_wilderness_add_can_be_declined_and_changed_gear_skips_before_start(self):
        from ankiscape.logic.combat_session import confirm_wilderness_combat_risk, reset_wilderness_combat_confirmations

        reset_wilderness_combat_confirmations()
        addon = self._queue_addon("ankiscape_queue_wilderness_notice", (_MINE_IRON, 1))
        captured = []

        def confirm(player_data, action):
            captured.append(dict(action))
            return len(captured) > 1

        with patch.object(addon.ui, "confirm_wilderness_queue_action", side_effect=confirm):
            from ankiscape.core.action_queue import add_to_action_queue
            self.assertEqual(add_to_action_queue(addon, _WILD, 1), "Wilderness entry was not added.")
            self.assertEqual(len(self._rows(addon)), 1)
            fingerprint = addon.runtime_actions.wilderness_combat_risk_fingerprint(
                addon._state.player_data, "earth_warrior", addon.runtime_actions.COMBAT_ENEMY_DATA["earth_warrior"])
            confirm_wilderness_combat_risk(fingerprint)
            self.assertEqual(add_to_action_queue(addon, _WILD, 1), "")
            self.assertEqual(add_to_action_queue(addon, _MINE_IRON, 30), "")
        addon.save_player_data()
        addon.load_player_data()
        addon._state.player_data["equipment"]["weapon"] = "Bronze sword"
        confirm_wilderness_combat_risk(addon.runtime_actions.wilderness_combat_risk_fingerprint(
            addon._state.player_data, "earth_warrior", addon.runtime_actions.COMBAT_ENEMY_DATA["earth_warrior"]))
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertEqual((self.errors, self.bankstanding_dialogs), ([], []))
        self.assertIn("Wilderness equipment risk changed", self._notice(addon))
        self.assertEqual(len(self._rows(addon)), 1)

    def test_a_saved_wilderness_entry_keeps_its_add_time_approval_after_reload(self):
        from ankiscape.core.action_queue import add_to_action_queue
        from ankiscape.logic.combat_session import reset_wilderness_combat_confirmations

        addon = self._queue_addon(
            "ankiscape_queue_wilderness_reload", (_MINE_IRON, 1), attack_level=99,
            strength_level=99, defense_level=99, constitution_level=99, combat_lifepoints=990,
        )
        with patch.object(addon.ui, "confirm_wilderness_queue_action", return_value=True):
            self.assertEqual(add_to_action_queue(addon, _WILD, 100), "")
        addon.save_player_data()
        addon.load_player_data()
        reset_wilderness_combat_confirmations()
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
            self._answer(addon)
        self.assertEqual(addon._state.current_skill, "Combat")
        self.assertEqual((self.errors, self.bankstanding_dialogs), ([], []))

    def test_the_last_counted_entry_logs_done(self):
        addon = self._queue_addon("ankiscape_queue_last_done", (_MINE_IRON, 1))
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
        self.assertEqual(self._log(addon).count("Queue: Mining: Iron done"), 1)
