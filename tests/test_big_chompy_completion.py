import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    QUEST_DATA,
    QUEST_UNLOCK_RULES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.chompy_hunting_data import (
    BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE,
    BIG_CHOMPY_BIRD_HUNTING_WIKI_SOURCE,
    CHOMPY_HUNTING_ACTIVITY_ID,
    CHOMPY_HUNTING_SOURCE,
    DARKAN_REV,
    RAW_CHOMPY_WIKI_SOURCE,
)
from ankiscape.logic_pure.logic_pure_production import (
    apply_utility_activity_pure,
    utility_activity_locked_reasons_pure,
)
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_locked_reasons_pure,
    start_quest_pure,
)
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest
from tests.test_integration_smoke import (
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)
from tools.audit_item_reachability import build_reachability_report


QUEST_ID = "big_chompy_bird_hunting"
STAGE_ACTIONS = (
    "Fletch ogre arrows from achey logs, feathers, and wolfbone arrowtips, then give six arrows to Rantz",
    "Retrieve the ogre bellows, fill them with swamp gas, inflate swamp toads, and place the bait for Rantz",
    "Lure and kill a Chompy bird with an ogre bow and ogre arrows, pluck it, take the raw chompy to Rantz, gather the three seasonings from Rantz, Fycie and Bugs, then spit-roast the seasoned chompy for him",
)


def _ready_big_chompy_player(*, include_stage_items=True, include_hunting_ammo=False):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(
        cooking_level=30,
        fletching_level=5,
        ranged_level=30,
        attack_level=30,
        strength_level=30,
        defense_level=30,
        constitution_level=30,
    )
    player["quest_combat_config"] = {"resolver_enabled": True}
    if include_stage_items:
        player["inventory"].update({"Feather": 1, "Wolf bones": 6})
    if include_hunting_ammo:
        player["inventory"]["Ogre arrow"] = 1
    player, started = start_quest_pure(player, QUEST_ID, QUEST_DATA)
    if not started:
        raise AssertionError("Big Chompy Bird Hunting fixture could not start the quest")
    return player


def _answer_review(addon):
    addon.card_turned = True
    addon.answer_shown = True
    addon.exp_awarded = False
    addon.on_answer_card(
        _FakeReviewer(),
        4,
        lambda _self, _ease: "answered",
    )


class TestBigChompyStageContract(unittest.TestCase):
    def test_all_live_stage_requirements_replace_generated_sentinels(self):
        rows = {
            row["stage"]: row
            for row in QUEST_DATA[QUEST_ID]["stage_requirements"]
        }

        self.assertEqual(set(rows), {1, 2, 3})
        self.assertEqual(
            tuple(rows[stage]["required_actions"] for stage in range(1, 4)),
            ((), (), ()),
        )
        self.assertEqual(
            tuple(rows[stage]["auto_actions"][0] for stage in range(1, 4)),
            STAGE_ACTIONS,
        )
        self.assertEqual(
            {rows[stage]["source"] for stage in range(1, 4)},
            {BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE},
        )
        self.assertIn(BIG_CHOMPY_BIRD_HUNTING_WIKI_SOURCE, CHOMPY_HUNTING_SOURCE)
        self.assertIn(RAW_CHOMPY_WIKI_SOURCE, CHOMPY_HUNTING_SOURCE)
        self.assertIn(DARKAN_REV, CHOMPY_HUNTING_SOURCE)

    def test_hunting_requires_the_completed_quest_bow_and_arrows(self):
        spec = UTILITY_ACTIVITY_DATA[CHOMPY_HUNTING_ACTIVITY_ID]
        self.assertEqual(spec["requirements"], {"Ogre arrow": 1})
        self.assertEqual(spec["required_item_options"], (("Ogre bow",),))
        self.assertNotIn("icon_item", spec)
        self.assertTrue(
            UTILITY_ITEM_IMAGES["Raw chompy"].endswith(
                "/cookingitems/raw_chompy.png"
            )
        )
        ogre_arrow = next(
            item for item in ITEM_DEFINITIONS if item.storage_key == "Ogre arrow"
        )
        self.assertTrue(ogre_arrow.asset_path.endswith("/shopitems/ogre_arrow.png"))
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"].update({"Ogre bow": 1, "Ogre arrow": 1})

        self.assertEqual(
            utility_activity_locked_reasons_pure(
                player,
                CHOMPY_HUNTING_ACTIVITY_ID,
                UTILITY_ACTIVITY_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Big Chompy Bird Hunting",),
        )
        player["quests"][QUEST_ID] = {
            "started": True,
            "progress": QUEST_DATA[QUEST_ID]["stages"] + 1,
            "completed": True,
        }
        del player["inventory"]["Ogre arrow"]
        self.assertEqual(
            utility_activity_locked_reasons_pure(
                player,
                CHOMPY_HUNTING_ACTIVITY_ID,
                UTILITY_ACTIVITY_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("materials",),
        )

        player["inventory"]["Ogre arrow"] = 1
        inventory, _exp, applied, processed = apply_utility_activity_pure(
            CHOMPY_HUNTING_ACTIVITY_ID,
            player["inventory"],
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(applied)
        self.assertEqual(processed, 1)
        self.assertEqual(inventory["Raw chompy"], 1)
        self.assertEqual(inventory["Ogre bow"], 1)
        self.assertEqual(inventory["Ogre arrow"], 0)


class TestBigChompyPureFlow(unittest.TestCase):
    def test_pure_flow_enforces_levels_items_and_combat_before_completion(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(
            quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA),
            ("Cooking 30", "Fletching 5", "Ranged 30"),
        )
        player = _ready_big_chompy_player(include_stage_items=False)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(
                player,
                QUEST_ID,
                QUEST_DATA,
            ),
            ("Needs Feather x1", "Needs Wolf bones x6"),
        )

        player["inventory"].update({"Feather": 1, "Wolf bones": 6})
        player, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(progressed)
        self.assertFalse(completed)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 2)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(
                player,
                QUEST_ID,
                QUEST_DATA,
            ),
            ("Battle required: Chompy bird level 6",),
        )

        player, resolved, result = apply_quest_combat_encounter_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
            rng=lambda: 0.0,
            equipment_data=EQUIPMENT_DATA,
        )
        self.assertTrue(resolved)
        self.assertEqual(result["reason"], "combat_resolved")

        player, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(progressed)
        self.assertFalse(completed)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
        player, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )

        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertTrue(player["quests"][QUEST_ID]["completed"])
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 4)
        self.assertEqual(quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA), STAGE_ACTIONS)
        self.assertEqual(player["quest_points"], 2)
        self.assertEqual(player["cooking_exp"], 1470.0)
        self.assertEqual(player["fletching_exp"], 262.0)
        self.assertEqual(player["ranged_exp"], 735.0)
        self.assertEqual(player["inventory"]["Ogre bow"], 1)

    def test_reachability_closes_the_chompy_and_wild_pie_routes(self):
        report = build_reachability_report()

        self.assertEqual(
            report["routes"].get("Raw chompy"),
            "Utility:hunt_chompy_birds",
        )
        self.assertEqual(
            report["routes"].get("Raw wild pie"),
            "Utility:assemble_wild_pie",
        )
        self.assertEqual(
            report["routes"].get("Wild pie"),
            "Cooking:cook_wild_pie",
        )
        self.assertNotIn(
            QUEST_ID,
            {
                row["quest_id"]
                for row in report["blocked_quest_stage_products"]
            },
        )


class TestBigChompyProductFlow(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_reviews_complete_the_quest_then_hunt_one_raw_chompy(self):
        addon = _load_addon_as_package("ankiscape_big_chompy_e2e")
        calls = {"gains": [], "dialogs": [], "saves": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "saves",
            calls["saves"] + 1,
        )
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append(
            (title, message)
        )
        addon.player_data = _ready_big_chompy_player(include_hunting_ammo=True)
        addon.current_skill = "Quests"
        addon._REVIEW_UNDO_STACK.clear()

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            for review_count in range(1, 9):
                _answer_review(addon)
                if addon.player_data["quests"][QUEST_ID]["completed"]:
                    break
        finally:
            addon.random.random = original_random

        self.assertLess(review_count, 8)
        self.assertTrue(addon.player_data["quests"][QUEST_ID]["completed"])
        self.assertEqual(
            quest_action_proofs_for_quest(addon.player_data, QUEST_ID, QUEST_DATA),
            STAGE_ACTIONS,
        )
        self.assertEqual(addon.player_data["inventory"]["Ogre bow"], 1)
        self.assertEqual(calls["dialogs"][-1][0], "Quest complete")
        self.assertIn(
            "Big Chompy Bird Hunting is complete",
            calls["dialogs"][-1][1],
        )

        addon.current_skill = "Utility / Activities"
        addon.player_data["current_utility"] = CHOMPY_HUNTING_ACTIVITY_ID
        _answer_review(addon)

        self.assertEqual(addon.player_data["inventory"]["Raw chompy"], 1)
        self.assertEqual(addon.player_data["inventory"]["Ogre bow"], 1)
        self.assertEqual(addon.player_data["inventory"]["Ogre arrow"], 0)
        self.assertEqual(calls["gains"][-1], "+1 Raw chompy")
        self.assertGreaterEqual(calls["saves"], review_count + 1)

        _answer_review(addon)
        self.assertEqual(calls["dialogs"][-1][0], "Out of materials")
        self.assertIn("Ogre arrow", calls["dialogs"][-1][1])


if __name__ == "__main__":
    unittest.main()
