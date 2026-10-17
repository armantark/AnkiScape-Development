"""Quest lamps: announced at completion, fixed-skill lamps pay on Claim, any lamp can be destroyed."""

import copy
import sys
import types
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import CLAIM_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.stronghold_player_safety_data import STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS
from ankiscape.logic.stronghold_player_safety_logic import stronghold_player_safety_view_pure
from ankiscape.logic_pure.logic_pure import apply_claim_pure, apply_destroy_claim_pure, claim_rows_pure, start_quest_pure
from ankiscape.runtime.runtime_actions_quest import handle_quest_answer
from tests.mogres.test_miniquest_and_target import _runtime_context
from tests.test_integration_smoke import _DummyCol, _DummyMW, _install_runtime_fakes, _load_addon_as_package

ELDER_KILN_LAMP = "the_elder_kiln_xp_lamp_1"


def _player_with_completed(*quest_ids):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for quest_id in quest_ids:
        player["quests"][quest_id] = {"started": True, "progress": QUEST_DATA[quest_id]["stages"], "completed": True}
    return player


def _actionable_claim_ids(player):
    return {row["claim_id"] for row in claim_rows_pure(player, CLAIM_DATA) if row["eligible"]}


class QuestCompletionNamesItsLampsTest(unittest.TestCase):
    def test_stolen_hearts_played_through_real_reviews_names_its_three_lamps(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update(start_quest_pure(player, "stolen_hearts", QUEST_DATA)[0])
        player["current_quest"] = "stolen_hearts"
        for skill_id in ("attack", "strength", "defense", "constitution"):
            player[f"{skill_id}_level"] = 40
        calls = {"errors": []}
        ctx = _runtime_context(player, calls, random_values=(0.3,) * 5000)

        reviews = 0
        while not player["quests"]["stolen_hearts"]["completed"] and reviews < 60:
            self.assertTrue(handle_quest_answer(ctx))
            reviews += 1

        self.assertIn("Defeated Mercenary Joe", calls["activity"])
        self.assertEqual(
            calls["errors"],
            [
                (
                    "Quest complete",
                    "Stolen Hearts is complete, so questing has been switched off. "
                    "3 XP lamps (250 XP each) are waiting in Bank Claims. "
                    "Open the AnkiScape menu to pick another quest.",
                )
            ],
        )
        self.assertLessEqual(
            {f"stolen_hearts_xp_lamp_{index}" for index in (1, 2, 3)},
            _actionable_claim_ids(player),
        )


class LampClaimAndDestroyTest(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_quest_lamps_integration")
        self.addon.mw = _DummyMW(_DummyCol())
        self.errors = []
        for name in ("save_player_data", "check_achievements", "_refresh_skill_availability", "update_review_hud", "_show_exp"):
            setattr(self.addon, name, lambda *_args: None)
        self.addon.level_up_check = lambda _skill, _data: None
        self.addon.show_error_message = lambda title, message: self.errors.append((title, message))
        self.addon._state.current_skill = "Mining"

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _undo(self):
        self.addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))

    def test_fixed_skill_lamps_pay_their_skill_with_no_choice(self):
        player = _player_with_completed("stolen_hearts", "myths_of_the_white_lands")
        self.addon._state.player_data = player

        # A fixed lamp pays its own skill even when a stale caller names another.
        for claim_id, exp_key, named_skill in (
            ("stolen_hearts_xp_lamp_2", "agility_exp", None),
            ("stolen_hearts_xp_lamp_3", "thieving_exp", None),
            ("myths_of_the_white_lands_xp_lamp_1", "agility_exp", "attack"),
        ):
            before = float(player.get(exp_key, 0) or 0)
            self.assertTrue(self.addon.on_claim_reward(claim_id, named_skill), claim_id)
            self.assertEqual(float(player[exp_key]) - before, CLAIM_DATA[claim_id]["xp_amount"])
            self.assertNotIn(claim_id, _actionable_claim_ids(player))
        self.assertEqual(player["attack_exp"], 0)
        self.assertEqual(self.errors, [])

    def test_a_choice_lamp_still_needs_a_chosen_skill_when_only_one_qualifies(self):
        player = _player_with_completed("the_elder_kiln")
        player["attack_level"] = 75
        player["strength_level"] = 74

        self.assertEqual(apply_claim_pure(player, ELDER_KILN_LAMP, CLAIM_DATA)[1], False)
        self.assertEqual(apply_claim_pure(player, ELDER_KILN_LAMP, CLAIM_DATA, "strength")[1], False)
        claimed, ok = apply_claim_pure(player, ELDER_KILN_LAMP, CLAIM_DATA, "attack")
        self.assertTrue(ok)
        self.assertEqual(claimed["attack_exp"] - player["attack_exp"], 100_000)

    def test_claim_projection_owns_eligibility_and_fixed_skill_display(self):
        player = _player_with_completed("stolen_hearts", "the_elder_kiln")
        player.update(attack_level=75, strength_level=74)
        rows = {row["claim_id"]: row for row in claim_rows_pure(player, CLAIM_DATA)}
        elder = rows[ELDER_KILN_LAMP]
        self.assertEqual(elder["eligible_skill_ids"], ("attack",))
        self.assertEqual(elder["action_label"], "Choose skill")
        agility = rows["stolen_hearts_xp_lamp_2"]
        self.assertEqual(agility["eligible_skill_ids"], ("agility",))
        self.assertEqual(agility["title"], "Stolen Hearts: Agility lamp (250 XP)")
        self.assertEqual(agility["metadata"], "250 XP · Agility")
        self.assertEqual(agility["action_label"], "Claim")
        self.assertEqual(agility["tooltip"], "Pays Agility.")

    def test_destroy_forfeits_for_good_and_undo_restores_the_lamp(self):
        player = _player_with_completed("stolen_hearts")
        self.addon._state.player_data = player
        initial = copy.deepcopy(player)

        self.assertTrue(self.addon.on_destroy_claim("stolen_hearts_xp_lamp_1"))
        self.assertNotIn("stolen_hearts_xp_lamp_1", _actionable_claim_ids(player))
        self.assertFalse(self.addon.on_claim_reward("stolen_hearts_xp_lamp_1", "attack"))
        self.assertFalse(self.addon.on_destroy_claim("stolen_hearts_xp_lamp_1"))
        self.assertEqual([title for title, _message in self.errors], ["Cannot claim reward", "Cannot destroy lamp"])
        reloaded = migrate_loaded_data(copy.deepcopy(player), ORE_DATA, ITEM_DEFINITIONS)
        self.assertNotIn("stolen_hearts_xp_lamp_1", _actionable_claim_ids(reloaded))
        self.assertIn("stolen_hearts_xp_lamp_2", _actionable_claim_ids(reloaded))

        self._undo()
        self.assertEqual(self.addon._state.player_data, initial)
        self.assertIn("stolen_hearts_xp_lamp_1", _actionable_claim_ids(self.addon._state.player_data))

    def test_destroy_refuses_rewards_that_are_not_waiting_lamps(self):
        player = _player_with_completed()
        self.assertEqual(apply_destroy_claim_pure(player, "tutorial_island_starter_kit", CLAIM_DATA)[1], False)
        self.assertEqual(apply_destroy_claim_pure(player, "stolen_hearts_xp_lamp_1", CLAIM_DATA)[1], False)

    def test_a_destroyed_stronghold_lamp_settles_like_a_claimed_one(self):
        player = _player_with_completed()
        for claim_id in STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS:
            player["claims"][claim_id] = {"claimed": False, "delivered": True}
        player, ok = apply_destroy_claim_pure(player, STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS[0], CLAIM_DATA)
        self.assertTrue(ok)

        view = stronghold_player_safety_view_pure(player)
        self.assertEqual(view["lamps_remaining"], 1)
        self.assertEqual(view["next_lamp_claim_id"], STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS[1])


if __name__ == "__main__":
    unittest.main()
