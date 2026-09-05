import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import CLAIM_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.skill_registry import get_skill
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure_claims import apply_claim_pure, claim_rows_pure
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


QUEST_ID = "the_fremennik_isles"
CLAIM_IDS = (
    "the_fremennik_isles_xp_lamp_1",
    "the_fremennik_isles_xp_lamp_2",
)
SKILL_OPTIONS = ("attack", "strength", "defense", "constitution")


def _final_stage_player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["quests"][QUEST_ID] = {
        "started": True,
        "progress": QUEST_DATA[QUEST_ID]["stages"],
        "completed": False,
    }
    player["current_quest"] = QUEST_ID
    return player


def _answer_review(addon):
    addon._state.card_turned = True
    addon._state.answer_shown = True
    addon._state.exp_awarded = False
    addon.on_answer_card(
        _FakeReviewer(),
        4,
        lambda _self, _ease: "answered",
    )


class TestFremennikIslesLampContract(unittest.TestCase):
    def test_reward_data_replaces_combat_xp_with_two_independent_choices(self):
        quest = QUEST_DATA[QUEST_ID]

        self.assertEqual(
            quest["xp_rewards"],
            (
                {"skill_id": "construction", "amount": 5000},
                {"skill_id": "crafting", "amount": 5000},
                {"skill_id": "woodcutting", "amount": 10000},
            ),
        )
        self.assertEqual(len(quest["lamp_rewards"]), 1)
        lamp = quest["lamp_rewards"][0]
        self.assertEqual(lamp["amount"], 10000)
        self.assertEqual(lamp["skill_options"], SKILL_OPTIONS)
        self.assertEqual(lamp["minimum_level"], 1)
        self.assertEqual(lamp["quantity"], 2)
        self.assertEqual(
            tuple(
                claim_id
                for claim_id, claim in CLAIM_DATA.items()
                if claim.get("required_quest") == QUEST_ID
                and claim.get("claim_type") == "xp_lamp"
            ),
            CLAIM_IDS,
        )

    def test_every_quest_xp_reward_uses_a_trainable_skill(self):
        for quest_id, quest in QUEST_DATA.items():
            for reward in quest.get("xp_rewards", ()):
                skill_id = reward.get("skill_id")
                skill = get_skill(skill_id) if isinstance(skill_id, str) else None
                self.assertTrue(
                    skill is not None and skill.trainable,
                    f"{quest_id}: invalid XP reward skill id {skill_id!r}",
                )

    def test_claims_accept_the_same_allowed_skill_twice_and_refuse_other_skills(self):
        player = _final_stage_player()
        player["quests"][QUEST_ID]["completed"] = True

        unchanged, ok = apply_claim_pure(player, CLAIM_IDS[0], CLAIM_DATA, "magic")
        self.assertFalse(ok)
        self.assertIs(unchanged, player)

        player, ok = apply_claim_pure(player, CLAIM_IDS[0], CLAIM_DATA, "attack")
        self.assertTrue(ok)
        self.assertEqual(player["attack_exp"], 10000)
        player, ok = apply_claim_pure(player, CLAIM_IDS[1], CLAIM_DATA, "attack")
        self.assertTrue(ok)
        self.assertEqual(player["attack_exp"], 20000)
        self.assertTrue(all(player["claims"][claim_id]["claimed"] for claim_id in CLAIM_IDS))


class TestFremennikIslesLampProductFlow(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_review_completion_exposes_and_applies_both_real_claims(self):
        addon = _load_addon_as_package("ankiscape_fremennik_isles_lamps_e2e")
        addon.mw = _DummyMW(_DummyCol())
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda _title, _message: None
        addon._state.player_data = _final_stage_player()
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()
        addon._state.direct_action_undo_stack.clear()

        before = {row["claim_id"]: row for row in claim_rows_pure(addon._state.player_data, CLAIM_DATA)}
        self.assertTrue(all(not before[claim_id]["eligible"] for claim_id in CLAIM_IDS))

        _answer_review(addon)

        self.assertTrue(addon._state.player_data["quests"][QUEST_ID]["completed"])
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(addon._state.player_data["construction_exp"], 5000)
        self.assertEqual(addon._state.player_data["crafting_exp"], 5000)
        self.assertEqual(addon._state.player_data["woodcutting_exp"], 10000)
        after = {row["claim_id"]: row for row in claim_rows_pure(addon._state.player_data, CLAIM_DATA)}
        self.assertTrue(all(after[claim_id]["eligible"] for claim_id in CLAIM_IDS))

        self.assertTrue(addon.on_claim_reward(CLAIM_IDS[0], "strength"))
        self.assertEqual(addon._state.player_data["strength_exp"], 10000)
        self.assertTrue(addon.on_claim_reward(CLAIM_IDS[1], "strength"))
        self.assertEqual(addon._state.player_data["strength_exp"], 20000)


if __name__ == "__main__":
    unittest.main()
