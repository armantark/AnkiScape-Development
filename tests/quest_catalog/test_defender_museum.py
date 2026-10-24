"""Defender requires the earned Shield story, independently of quest completion."""

import copy
import tempfile
import unittest
from pathlib import Path

from tests.quest_catalog.defender_museum_fixture import (
    CLAIM_REASON, DEFENDER, LEVELS, PREREQUISITES, SHIELD,
    earned_shield_player, prepare_completion, ready_defender_player, typed_snapshot,
)
from tests.test_storage_runtime import Collection, _load_storage_module
from ankiscape.core.constants import CLAIM_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.shattered_heart_data import SHATTERED_HEART_ROCK_ITEMS
from ankiscape.logic.shattered_heart_logic import apply_shattered_heart_command_pure
from ankiscape.data.varrock_museum_data import QUEST_KUDOS, QUIZ_DISPLAYS, SPECIMEN_DISPLAYS
from ankiscape.logic.varrock_museum_logic import (
    apply_varrock_museum_command_pure, apply_varrock_museum_review_pure, varrock_museum_kudos_pure,
)
from ankiscape.logic_pure.logic_pure import (
    apply_claim_pure, can_start_quest_pure, quest_availability_state_pure, quest_locked_reasons_pure, start_quest_pure,
)


def reasons(player):
    return quest_locked_reasons_pure(player, DEFENDER, QUEST_DATA)


def claim(player):
    updated, ok, info = apply_varrock_museum_command_pure(player, "claim_quest_stories")
    unittest.TestCase().assertTrue(ok, info)
    return updated, info


def _museum_reviews(player, count):
    for _ in range(count):
        player, ok, info = apply_varrock_museum_review_pure(player)
        unittest.TestCase().assertTrue(ok, info)
    return player


def _unrelated_museum_histories():
    """Independent gate-isolation histories using existing transactions."""
    check = unittest.TestCase()
    player = ready_defender_player()
    check.assertEqual(player["inventory"]["Coins"], 600)
    yield "King Roald reward", player

    player = ready_defender_player()
    prepare_completion(player, "rune_mysteries")
    shield = player["quests"].pop(SHIELD)
    player, info = claim(player)
    check.assertEqual(info["quest_ids"], ("rune_mysteries",))
    player["quests"][SHIELD] = shield
    yield "other story", player

    quiz = _museum_reviews(ready_defender_player(), len(QUIZ_DISPLAYS))
    yield "completed quiz", quiz
    rewarded, ok, info = apply_varrock_museum_command_pure(quiz, "claim_orlando_reward")
    check.assertTrue(ok, info)
    yield "Orlando reward", rewarded

    player = ready_defender_player()
    prepare_completion(player, "the_dig_site")
    player["varrock_museum"]["route"] = "cleaning"
    player["equipment"].update(hands="Leather gloves", feet="Leather boots")
    tools = {"Trowel": 1, "Rock pick": 1, "Specimen brush": 1}
    player["inventory"].update(tools)
    player["carried_inventory"]["varrock_museum"] = tools
    specimens = _museum_reviews(player, len(SPECIMEN_DISPLAYS))
    yield "displayed specimens", specimens
    rewarded, ok, info = apply_varrock_museum_command_pure(specimens, "claim_threshold_rewards")
    check.assertTrue(ok, info)
    check.assertEqual(rewarded["varrock_museum"]["threshold_rewards_claimed"], ["kudos_51"])
    yield "milestone reward", rewarded

    player = ready_defender_player()
    # Unrelated rock acquisition is a prepared input, then the real statue transaction runs.
    player["inventory"].update(dict.fromkeys(SHATTERED_HEART_ROCK_ITEMS, 1))
    player, ok, info = apply_shattered_heart_command_pure(player, "add_completed_pairs")
    check.assertTrue(ok, info)
    check.assertEqual(player["shattered_heart"]["statues_completed"], 1)
    yield "completed statue", player

    player = ready_defender_player()
    prepare_completion(player, "one_small_favour")
    yield "waiting lamp", player
    player, ok = apply_claim_pure(player, "one_small_favour_xp_lamp_1", CLAIM_DATA, "attack")
    check.assertTrue(ok)
    check.assertTrue(player["claims"]["one_small_favour_xp_lamp_1"]["claimed"])
    yield "consumed lamp", player
    player, ok = apply_claim_pure(ready_defender_player(), "tutorial_island_starter_kit", CLAIM_DATA)
    check.assertTrue(ok)
    yield "unrelated reward claim", player


class DefenderMuseumTest(unittest.TestCase):
    def assert_locked_unchanged(self, player, expected):
        before = typed_snapshot(copy.deepcopy(player))
        self.assertEqual(reasons(player), expected)
        self.assertEqual(quest_availability_state_pure(player, DEFENDER, QUEST_DATA), "locked")
        self.assertFalse(can_start_quest_pure(player, DEFENDER, QUEST_DATA))
        updated, ok = start_quest_pure(player, DEFENDER, QUEST_DATA)
        self.assertFalse(ok)
        self.assertEqual(typed_snapshot(updated), before)
        self.assertEqual(typed_snapshot(player), before)

    def test_prerequisite_extraction_preserves_malformed_rows_fallbacks_and_order(self):
        player = {"quests": {"done": {"completed": True}}, "inventory": {}}
        catalog = {
            DEFENDER: {
                "required_quests": (None, {}, {"quest_id": 7},
                                    {"quest_id": "unimplemented_quest"},
                                    {"quest_id": "known", "display_name": ""},
                                    {"quest_id": "done", "display_name": "Done"},
                                    {"quest_id": "known", "display_name": "Known again"}),
                "required_quest_points": 2, "required_items": {"Hammer": 1},
            },
            "unimplemented_quest": "malformed implementation", "known": {}, "done": {},
        }
        before = typed_snapshot(copy.deepcopy(player))
        self.assertEqual(quest_locked_reasons_pure(player, DEFENDER, catalog), (
            "Unimplemented Quest (not implemented)", "Known", "Known again",
            "2 quest points", "Hammer x1", CLAIM_REASON,
        ))
        self.assertEqual(typed_snapshot(player), before)

    def test_earned_shield_completion_without_claim_refuses(self):
        player = ready_defender_player()
        self.assertTrue(player["quests"][SHIELD]["completed"])
        self.assert_locked_unchanged(player, (CLAIM_REASON,))

    def test_existing_minas_claim_clears_only_this_gate(self):
        player = ready_defender_player()
        before = copy.deepcopy(player)
        updated, info = claim(player)
        self.assertEqual(info["quest_ids"], (SHIELD,))
        self.assertEqual(info["kudos"], 5)
        self.assertEqual(varrock_museum_kudos_pure(updated) - varrock_museum_kudos_pure(player), 5)
        self.assertEqual(updated["varrock_museum"]["quest_stories_claimed"].count(SHIELD), 1)
        self.assertEqual(reasons(updated), ())
        # Full non-museum equality includes both quests, deeds, XP, QP and every inventory view.
        self.assertEqual(typed_snapshot(player), typed_snapshot(before))
        self.assertEqual(typed_snapshot({k: v for k, v in updated.items() if k != "varrock_museum"}),
                         typed_snapshot({k: v for k, v in before.items() if k != "varrock_museum"}))
        self.assertFalse(updated["quests"][DEFENDER]["started"])
        self.assertFalse(updated["quests"][DEFENDER]["completed"])
        started, ok = start_quest_pure(updated, DEFENDER, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(started["quests"][DEFENDER]["started"])

    def test_unrelated_kudos_and_rewards_do_not_clear_claim_gate(self):
        for kind, player in _unrelated_museum_histories():
            with self.subTest(kind=kind):
                self.assertGreater(varrock_museum_kudos_pure(player), 5)
                self.assert_locked_unchanged(player, (CLAIM_REASON,))

    def test_uncompleted_shield_is_not_claimable(self):
        for other_ready in (False, True):
            with self.subTest(other_ready=other_ready):
                player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                if other_ready:
                    prepare_completion(player, "rune_mysteries")
                updated, ok, info = apply_varrock_museum_command_pure(player, "claim_quest_stories")
                self.assertEqual(ok, other_ready)
                if other_ready:
                    self.assertEqual(info["quest_ids"], ("rune_mysteries",))
                else:
                    self.assertEqual(info["reason"], "No completed quest stories are ready for Minas.")
                self.assertNotIn(SHIELD, updated["varrock_museum"]["quest_stories_claimed"])
                self.assertIn(CLAIM_REASON, reasons(updated))

    def test_batching_and_repeat_claims_remain_ordinary(self):
        player = earned_shield_player()
        prepare_completion(player, "rune_mysteries")
        updated, info = claim(player)
        self.assertEqual(info["quest_ids"], ("rune_mysteries", SHIELD))
        awards = {row["id"]: row["kudos"] for row in QUEST_KUDOS}
        self.assertEqual(awards[SHIELD], 5)
        self.assertEqual(info["kudos"], sum(awards[q] for q in info["quest_ids"]))
        self.assertEqual(varrock_museum_kudos_pure(updated), 10)
        repeated, ok, info = apply_varrock_museum_command_pure(updated, "claim_quest_stories")
        self.assertFalse(ok)
        self.assertEqual(info["reason"], "No completed quest stories are ready for Minas.")
        self.assertEqual(typed_snapshot(repeated), typed_snapshot(updated))
        prepare_completion(updated, "making_history")
        later, info = claim(updated)
        self.assertEqual(info["quest_ids"], ("making_history",))
        self.assertEqual(info["kudos"], awards["making_history"])
        self.assertEqual(later["varrock_museum"]["quest_stories_claimed"].count(SHIELD), 1)
        self.assertEqual(varrock_museum_kudos_pure(later), 15)

    def test_all_other_defender_gates_survive_the_claim(self):
        claimed, _info = claim(ready_defender_player())
        for quest_id, name in PREREQUISITES:
            with self.subTest(quest=quest_id):
                player = copy.deepcopy(claimed)
                player["quests"].pop(quest_id)
                self.assert_locked_unchanged(player, (name,))
        for skill, level in LEVELS:
            with self.subTest(skill=skill):
                player = copy.deepcopy(claimed)
                player[f"{skill}_level"] = level - 1
                self.assert_locked_unchanged(player, (f"{skill.title()} {level}",))

    def test_started_and_completed_defender_preserve_progress(self):
        for completed in (False, True):
            with self.subTest(completed=completed):
                player = legacy_defender_player(completed)
                before = typed_snapshot(copy.deepcopy(player))
                self.assertEqual(reasons(player), ("completed",) if completed else ())
                self.assertEqual(can_start_quest_pure(player, DEFENDER, QUEST_DATA), not completed)
                updated, ok = start_quest_pure(player, DEFENDER, QUEST_DATA)
                self.assertEqual(ok, not completed)
                self.assertEqual(typed_snapshot(updated["quests"]), typed_snapshot(player["quests"]))
                self.assertNotIn("varrock_museum", player)
                self.assertNotIn("varrock_museum", updated)
                self.assertEqual(typed_snapshot(player), before)
                if completed:
                    self.assertEqual(typed_snapshot(updated), before)
                else:
                    self.assertEqual(updated["current_quest"], DEFENDER)
                    expected = {**player, "current_quest": DEFENDER}
                    self.assertEqual(typed_snapshot(updated), typed_snapshot(expected))

    def test_eligibility_inspection_does_not_normalize_the_save(self):
        cases = (
            (None, False), ("legacy", False), ([], False),
            ({"quest_stories_claimed": SHIELD}, False),
            ({"quest_stories_claimed": {SHIELD: True}}, False),
            ({"quest_stories_claimed": ("Shield of Arrav",)}, False),
            ({"quest_stories_claimed": ["rune_mysteries"]}, False),
            ({"quest_stories_claimed": (SHIELD,)}, True),
            ({"quest_stories_claimed": [SHIELD]}, True),
        )
        absent = ready_defender_player()
        absent.pop("varrock_museum")
        self.assert_locked_unchanged(absent, (CLAIM_REASON,))
        for raw, valid in cases:
            with self.subTest(raw=raw):
                player = ready_defender_player()
                player["varrock_museum"] = raw
                before = typed_snapshot(copy.deepcopy(player))
                self.assertEqual(reasons(player), () if valid else (CLAIM_REASON,))
                self.assertEqual(can_start_quest_pure(player, DEFENDER, QUEST_DATA), valid)
                self.assertEqual(quest_availability_state_pure(player, DEFENDER, QUEST_DATA),
                                 "can_start" if valid else "locked")
                self.assertEqual(typed_snapshot(player), before)


def legacy_defender_player(completed):
    player = ready_defender_player()
    player.pop("varrock_museum")
    player["quests"][DEFENDER] = {
        "started": True, "completed": completed,
        "progress": QUEST_DATA[DEFENDER]["stages"] if completed else 3,
    }
    # Prepared historical progress is preserved, never inferred as a museum claim.
    player["quest_action_proofs"].extend((
        "Complete Defender of Varrock stage 1 objective",
        "Complete Defender of Varrock stage 2 objective",
    ))
    player["quest_action_proofs"].sort()
    player["inventory"]["Coins"] = 1234
    return player


@unittest.skipIf(Collection is None, "Anki runtime is not installed")
class DefenderMuseumPersistenceTest(unittest.TestCase):
    def reopen(self, player, transform=None):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "collection.anki2")
            collection = Collection(path)
            try:
                storage = _load_storage_module(collection)
                # The Garden isolation fixture also triggers its historical farm setup.
                # Normalize both passes before recording command expectations.
                for _ in range(2):
                    storage.save_player_data(player, "Mining")
                    player, skill = storage.load_player_data()
                storage.save_player_data(player, skill)
                if transform:
                    player, _info = transform(player)
                storage.save_player_data(player, skill)
                expected = copy.deepcopy(player)
            finally:
                collection.close()
            reopened = Collection(path)
            try:
                storage = _load_storage_module(reopened)
                loaded, skill = storage.load_player_data()
                self.assertEqual(skill, "Mining")
                self.assertEqual(typed_snapshot(loaded), typed_snapshot(expected))
                return loaded
            finally:
                reopened.close()

    def test_real_collection_unclaimed_completion_stays_locked(self):
        loaded = self.reopen(ready_defender_player())
        self.assertTrue(loaded["quests"][SHIELD]["completed"])
        self.assertEqual(reasons(loaded), (CLAIM_REASON,))
        self.assertFalse(can_start_quest_pure(loaded, DEFENDER, QUEST_DATA))

    def test_real_collection_earned_claim_retains_identity_kudos_and_eligibility(self):
        player = ready_defender_player()
        kudos = varrock_museum_kudos_pure(player)
        loaded = self.reopen(player, claim)
        self.assertEqual(loaded["varrock_museum"]["quest_stories_claimed"].count(SHIELD), 1)
        self.assertEqual(varrock_museum_kudos_pure(loaded), kudos + 5)
        self.assertEqual(reasons(loaded), ())
        self.assertTrue(can_start_quest_pure(loaded, DEFENDER, QUEST_DATA))
        self.assertFalse(loaded["quests"][DEFENDER]["started"])

    def test_real_collection_legacy_progress_has_no_claim_backfill(self):
        for completed in (False, True):
            with self.subTest(completed=completed):
                player = legacy_defender_player(completed)
                loaded = self.reopen(player)
                self.assertEqual(loaded["quests"][DEFENDER], player["quests"][DEFENDER])
                self.assertEqual(loaded["quest_action_proofs"], player["quest_action_proofs"])
                self.assertEqual(loaded["inventory"]["Coins"], 1234)
                self.assertNotIn(SHIELD, loaded["varrock_museum"]["quest_stories_claimed"])
                self.assertEqual(loaded["quests"][DEFENDER]["completed"], completed)
                self.assertEqual(reasons(loaded), ("completed",) if completed else ())
