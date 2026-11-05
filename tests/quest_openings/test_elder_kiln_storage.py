"""The saved hatching attempt: defaults, migration, persistence, copies and journal rows."""

import copy
import json
import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.quest_storage import default_quest_side_state
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from ankiscape.data.quest import elder_kiln as source
from ankiscape.data.quest.murder_mystery import LEGACY_OPENING_JOURNAL, OPENING_ACTION
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure
from ankiscape.logic_pure.logic_pure_state import _copy_player_data_with_nested
from ankiscape.logic_pure.quest.elder_kiln_state import (
    copy_elder_kiln_state_pure, default_elder_kiln_state_pure, sanitize_elder_kiln_state_pure,
)
from tests.quest_openings.test_elder_kiln_data import PROOF, QUEST_ID, player
from tests.quest_openings.test_elder_kiln_logic import attempt
from tests.test_storage_runtime import _load_storage_module

KEY = source.STATE_KEY


def saved(data):
    """What Anki's JSON config would hand back."""
    return json.loads(json.dumps(data))


def migrate(data):
    return migrate_loaded_data(saved(data), ORE_DATA, ITEM_DEFINITIONS)


def journal(data):
    return quest_journal_rows_pure(data, QUEST_ID, QUEST_DATA)


class _JsonCollection:
    def __init__(self):
        self.values = {}

    def get_config(self, key, default=None):
        return copy.deepcopy(self.values.get(key, default))

    def set_config(self, key, value):
        self.values[key] = saved(value)

    def remove_config(self, key):
        self.values.pop(key, None)


class DefaultsAndMigrationTest(unittest.TestCase):
    def test_actual_defaults_are_fresh(self):
        first, second = default_quest_side_state(), default_quest_side_state()
        self.assertEqual(first[KEY], default_elder_kiln_state_pure())
        self.assertIsNot(first[KEY], second[KEY])
        self.assertEqual(default_player_data(ORE_DATA, ITEM_DEFINITIONS)[KEY], default_elder_kiln_state_pure())
        # The hatching side state is additive; 126 is main's Witch's House bump, not this change's.
        self.assertEqual(CURRENT_CONFIG_VERSION, 126)

    def test_valid_states_survive_loading_for_every_save_shape(self):
        shapes = {
            "unstarted": (player(), None, default_elder_kiln_state_pure()),
            "opening request": (player(started=True), default_elder_kiln_state_pure(), default_elder_kiln_state_pure()),
            "preparing": (player(started=True), attempt(phase="preparing", progress=0, steps=7), None),
            "active": (player(1, started=True), attempt(heat=63, band=2, progress=41, steps=58, attempt=3,
                                                        ak_phase="warning", ak_remaining=2, jeh_phase="delay", jeh_remaining=9), None),
            "failed": (player(started=True), attempt(phase="failed", progress=0, heat=4), None),
            "later stage": (player(3, started=True), attempt(), None),
            "completed": (player(7, started=True, completed=True), None, default_elder_kiln_state_pure()),
            "hatched with proof": (player(2, started=True, proofs=(PROOF,)), attempt(phase="hatched", progress=100), None),
        }
        for label, (data, state, expected) in shapes.items():
            with self.subTest(save=label):
                if state is None:
                    data.pop(KEY, None)
                else:
                    data[KEY] = state
                loaded = migrate(data)
                self.assertEqual(loaded[KEY], expected or state)
                self.assertEqual(loaded["quests"][QUEST_ID], data["quests"][QUEST_ID])
                self.assertEqual(loaded["quest_action_proofs"], data["quest_action_proofs"])
                self.assertEqual(loaded["config_version"], CURRENT_CONFIG_VERSION)

    def test_malformed_attempts_reset_to_the_request_without_touching_progress_or_proofs(self):
        malformed = {
            "not a mapping": ["active"],
            "boolean heat": attempt(heat=True),
            "float progress": attempt(progress=50.0),
            "text band": attempt(band="1"),
            "unknown phase": attempt(phase="burning"),
            "unknown helper phase": attempt(ak_phase="resting"),
            "helper countdown too long": attempt(ak_phase="warning", ak_remaining=6),
            "mej-ak has no delay": attempt(ak_phase="delay", ak_remaining=3),
            "heat above the gauge": attempt(heat=101),
            "band out of range": attempt(band=4),
            "negative steps": attempt(steps=-1),
            "preparing with progress": attempt(phase="preparing", progress=3),
            "active at zero": attempt(progress=0),
            "active at one hundred": attempt(progress=100),
            "failed with progress": attempt(phase="failed", progress=2),
            "hatched without proof": attempt(phase="hatched", progress=100),
            "request mid-attempt": attempt(phase="request", progress=0, heat=10),
            "live attempt numbered zero": attempt(attempt=0),
            "extra field": dict(attempt(), offline_steps=4),
            "missing field": {key: value for key, value in attempt().items() if key != "steps"},
        }
        for label, raw in malformed.items():
            for progress, proofs in ((1, ()), (4, ())):
                with self.subTest(state=label, progress=progress):
                    data = dict(player(progress, started=True, proofs=proofs), **{KEY: raw})
                    loaded = migrate(data)
                    self.assertEqual(loaded[KEY], default_elder_kiln_state_pure())
                    self.assertEqual(loaded["quests"][QUEST_ID]["progress"], progress)
                    self.assertEqual(loaded["quest_action_proofs"], [])

    def test_advanced_saves_are_neither_rewound_nor_backfilled(self):
        for progress, completed in ((2, False), (5, False), (7, True)):
            with self.subTest(progress=progress):
                loaded = migrate(player(progress, started=True, completed=completed))
                self.assertEqual(loaded["quests"][QUEST_ID], dict(started=True, completed=completed, progress=progress))
                self.assertNotIn(PROOF, loaded["quest_action_proofs"])

    def test_sanitation_returns_a_fresh_dictionary(self):
        raw = attempt()
        clean = sanitize_elder_kiln_state_pure(raw, False)
        self.assertEqual(clean, raw)
        self.assertIsNot(clean, raw)


class PersistenceTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        self.collection = _JsonCollection()
        self.storage = _load_storage_module(self.collection)

    def test_active_attempt_round_trips_exactly_with_no_offline_steps(self):
        state = attempt(heat=63, band=2, progress=41, steps=58, attempt=3,
                        ak_phase="warning", ak_remaining=2, jeh_phase="delay", jeh_remaining=9)
        data = dict(player(1, started=True), **{KEY: state})
        self.storage.save_player_data(data, "Quests")
        first, skill = self.storage.load_player_data()
        self.assertEqual((first[KEY], skill), (state, "Quests"))
        self.storage.save_player_data(first, skill)
        second, _ = self.storage.load_player_data()
        self.assertEqual(second[KEY], state)
        self.assertEqual(second["quests"][QUEST_ID], dict(started=True, completed=False, progress=1))

    def test_hatched_attempt_needs_its_saved_proof(self):
        hatched = attempt(phase="hatched", progress=100)
        for proofs, expected in (((PROOF,), hatched), ((), default_elder_kiln_state_pure())):
            with self.subTest(proofs=proofs):
                self.storage.save_player_data(dict(player(2, started=True, proofs=proofs), **{KEY: hatched}), "Quests")
                loaded, _ = self.storage.load_player_data()
                self.assertEqual(loaded[KEY], expected)
                self.assertEqual(loaded["quests"][QUEST_ID]["progress"], 2)


class CopyTest(unittest.TestCase):
    def test_nested_copy_is_independent(self):
        data = dict(player(1, started=True), **{KEY: attempt()})
        copied = _copy_player_data_with_nested(data)
        self.assertEqual(copied[KEY], data[KEY])
        self.assertIsNot(copied[KEY], data[KEY])
        copied[KEY]["heat"] = 99
        self.assertEqual(data[KEY]["heat"], 30)

    def test_copy_helper_neither_sanitizes_nor_migrates(self):
        raw = attempt(phase="hatched", progress=100)
        copied = copy_elder_kiln_state_pure(raw)
        self.assertEqual(copied, raw)
        self.assertIsNot(copied, raw)
        self.assertEqual(copy_elder_kiln_state_pure(None), default_elder_kiln_state_pure())
        data = dict(player(1, started=True), **{KEY: raw})
        self.assertEqual(_copy_player_data_with_nested(data)["quest_action_proofs"], [])


class JournalTest(unittest.TestCase):
    def _opening_lines(self, state, progress=1):
        data = dict(player(progress, started=True), **{KEY: state})
        before = copy.deepcopy(data)
        rows = journal(data)
        self.assertEqual(data, before)
        return rows[0]

    def test_opening_rows_follow_the_saved_attempt(self):
        cases = (
            (default_elder_kiln_state_pure(), (source.BEFORE_OFFER_COPY,)),
            (attempt(phase="preparing", progress=0), (source.AFTER_OFFER_COPY, source.INSTRUCTIONS_COPY)),
            (attempt(), (source.AFTER_OFFER_COPY, source.INSTRUCTIONS_COPY)),
            (attempt(phase="failed", progress=0),
             (source.AFTER_OFFER_COPY, source.INSTRUCTIONS_COPY, source.FAILURE_COPY)),
            (attempt(phase="hatched", progress=100), (source.BEFORE_OFFER_COPY,)),
        )
        for state, lines in cases:
            for progress in (0, 1):
                with self.subTest(phase=state["phase"], progress=progress):
                    row = self._opening_lines(state, progress)
                    self.assertEqual(row["lines"], lines)
                    self.assertEqual((row["completed"], row["current"]), (False, True))

    def test_proof_shows_the_outcome_with_ordinary_flags(self):
        hatched = attempt(phase="hatched", progress=100)
        for progress, flags in ((1, (False, True)), (2, (True, False))):
            with self.subTest(progress=progress):
                rows = journal(dict(player(progress, started=True, proofs=(PROOF,)), **{KEY: hatched}))
                self.assertEqual(rows[0]["lines"], (source.SUCCESS_COPY,))
                self.assertEqual((rows[0]["completed"], rows[0]["current"]), flags)

    def test_advanced_saves_without_proof_show_only_the_legacy_line(self):
        for progress, completed in ((2, False), (4, False), (7, True)):
            with self.subTest(progress=progress):
                data = player(progress, started=True, completed=completed)
                before = copy.deepcopy(data)
                rows = journal(data)
                self.assertEqual(data, before)
                self.assertEqual(rows[0], dict(stage=1, lines=(source.LEGACY_COPY,), completed=False, current=False))
                self.assertEqual([row["stage"] for row in rows], list(range(1, min(progress, 6) + 1)))
                self.assertEqual(rows[1]["lines"], QUEST_DATA[QUEST_ID]["journal_stages"][2])
                self.assertEqual(rows[1]["completed"], completed or progress > 2)

    def test_other_quests_keep_their_journal_transformations(self):
        cold = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        cold["quests"]["cold_war"] = dict(started=True, completed=False, progress=1)
        cold["cold_war_greeting"] = ["Shiver", "Bow", "Flap"]
        cold_rows = quest_journal_rows_pure(cold, "cold_war", QUEST_DATA)
        self.assertEqual(cold_rows[0]["lines"][-1], "Penguin greeting: Shiver → Bow → Flap (automatic).")
        mystery = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        mystery["quests"]["murder_mystery"] = dict(started=True, completed=False, progress=3)
        mystery_rows = quest_journal_rows_pure(mystery, "murder_mystery", QUEST_DATA)
        self.assertEqual(mystery_rows[0], dict(stage=1, lines=LEGACY_OPENING_JOURNAL, completed=False, current=False))
        mystery["quest_action_proofs"] = [OPENING_ACTION]
        proven_rows = quest_journal_rows_pure(mystery, "murder_mystery", QUEST_DATA)
        self.assertEqual(proven_rows[0]["lines"], QUEST_DATA["murder_mystery"]["journal_stages"][1])
        self.assertTrue(proven_rows[0]["completed"])


if __name__ == "__main__":
    unittest.main()
