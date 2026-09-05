import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA, QUEST_DATA
from ankiscape.data.quest_data import QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID
from ankiscape.data.zogre_flesh_eaters_data import ZOGRE_FLESH_EATERS_STAGE_SOURCE
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_locked_reasons_pure,
    start_quest_pure,
)
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest
from tests.test_combat_quest_gate import (
    _answer_review,
    _low_combat_zogre_player,
    _zogre_player,
)
from tests.test_integration_smoke import (
    _install_runtime_fakes,
    _load_addon_as_package,
)


QUEST_ID = "zogre_flesh_eaters"
STAGE_CLEANUPS = QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID[QUEST_ID]
# Frozen route oracle:
# /Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/zogre-flesh-eaters-target-contract.json
STAGE_ACTIONS = (
    "Speak to the ogre guard, open Jiggig's barricade, and enter the tomb",
    "Defeat the crypt zombie, recover the tomb evidence, show it in Yanille, and search Sithik's room",
    "Draw and sign an accurate portrait of Sithik, then present the complete evidence to Zavistic Rarve for the strange potion",
    "Drug Sithik's tea, leave and return after his transformation, then interrogate him about the disease and brutal arrows",
    "Report Sithik's confession to Grish, receive the ogre gate key and bow knowledge, and return to the tomb",
    "Open the stone doors, defeat Slash Bash, recover the ogre artefact, and return it to Grish",
)


def _combat_ready_zogre_player() -> dict:
    player = _zogre_player(combat_level=99)
    player["inventory"]["Shark"] = 28
    player["combat_supply_loadout"]["food"] = {"Shark": 28}
    return player


class TestZogreFleshEatersStageContract(unittest.TestCase):
    def test_all_stage_sentinels_and_optional_item_gates_are_gone(self):
        stage_rows = QUEST_DATA[QUEST_ID]["stage_requirements"]
        self.assertEqual(len(stage_rows), 6)
        rows = {row["stage"]: row for row in stage_rows}
        self.assertEqual(set(rows), set(range(1, 7)))
        self.assertEqual(
            tuple(rows[stage]["required_actions"] for stage in range(1, 7)),
            ((), (), (), (), (), ()),
        )
        self.assertEqual(
            tuple(rows[stage]["auto_actions"][0] for stage in range(1, 7)),
            STAGE_ACTIONS,
        )
        self.assertTrue(
            all(not rows[stage]["required_inventory"] for stage in range(1, 7))
        )
        self.assertEqual(
            tuple(cleanup.remove_required_actions for cleanup in STAGE_CLEANUPS),
            tuple(
                (f"Complete Zogre Flesh Eaters stage {stage} objective",)
                for stage in range(1, 7)
            ),
        )
        self.assertEqual(
            {rows[stage]["source"] for stage in range(1, 7)},
            {ZOGRE_FLESH_EATERS_STAGE_SOURCE},
        )
        self.assertEqual(
            tuple(
                tuple(
                    encounter["encounter_id"]
                    for encounter in rows[stage]["combat_encounters"]
                )
                for stage in range(1, 7)
            ),
            (
                (),
                ("zogre_flesh_eaters_zombie_39",),
                (),
                (),
                (),
                ("zogre_flesh_eaters_slash_bash_111",),
            ),
        )
        self.assertEqual(
            rows[2]["combat_encounters"][0]["guaranteed_drops"],
            {"Ruined backpack": 1},
        )
        self.assertEqual(
            rows[6]["combat_encounters"][0]["guaranteed_drops"],
            {"Zogre bones": 2, "Ourg bones": 3, "Ogre artefact": 1},
        )
        self.assertEqual(
            QUEST_DATA[QUEST_ID]["xp_rewards"],
            (
                {"skill_id": "fletching", "amount": 2000.0},
                {"skill_id": "herblore", "amount": 2000.0},
                {"skill_id": "ranged", "amount": 2000.0},
            ),
        )


class TestZogreFleshEatersPureFlow(unittest.TestCase):
    def _resolve_current_fight(self, player, expected_name):
        for _burst in range(20):
            player, resolved, result = apply_quest_combat_encounter_pure(
                player,
                QUEST_ID,
                QUEST_DATA,
                rng=lambda: 0.0,
                equipment_data=EQUIPMENT_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(resolved)
            if result["reason"] == "combat_resolved":
                break
        else:
            self.fail(f"{expected_name} did not resolve within 20 combat bursts")
        self.assertEqual(result["display_name"], expected_name)
        return player

    def test_level_and_combat_gates_lead_to_completion(self):
        low_player = _low_combat_zogre_player()
        self.assertEqual(
            quest_locked_reasons_pure(low_player, QUEST_ID, QUEST_DATA),
            ("Combat 89",),
        )

        player, started = start_quest_pure(
            _combat_ready_zogre_player(),
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(started)
        player, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(progressed)
        self.assertFalse(completed)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 2)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player, QUEST_ID, QUEST_DATA),
            ("Battle required: Zombie level 39",),
        )
        self.assertEqual(
            quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA),
            STAGE_ACTIONS[:1],
        )

        player = self._resolve_current_fight(player, "Zombie")
        self.assertEqual(player["inventory"]["Ruined backpack"], 1)

        for expected_progress in (3, 4, 5, 6):
            player, progressed, completed = apply_quest_progress_pure(
                player,
                QUEST_ID,
                QUEST_DATA,
            )
            self.assertTrue(progressed)
            self.assertFalse(completed)
            self.assertEqual(player["quests"][QUEST_ID]["progress"], expected_progress)

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player, QUEST_ID, QUEST_DATA),
            ("Battle required: Slash Bash level 111",),
        )
        self.assertEqual(
            quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA),
            STAGE_ACTIONS[:5],
        )
        player = self._resolve_current_fight(player, "Slash Bash")
        self.assertEqual(player["inventory"]["Zogre bones"], 2)
        self.assertEqual(player["inventory"]["Ourg bones"], 3)
        self.assertEqual(player["inventory"]["Ogre artefact"], 1)

        player, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertTrue(player["quests"][QUEST_ID]["completed"])
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 7)
        self.assertEqual(
            quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA),
            STAGE_ACTIONS,
        )
        self.assertEqual(player["quest_points"], 1)
        self.assertEqual(player["inventory"]["Black prism"], 1)
        self.assertEqual(player["inventory"]["Relicym's balm"], 0)
        self.assertEqual(player["inventory"]["Ogre artefact"], 1)
        self.assertEqual(player["fletching_exp"], 2000.0)
        self.assertEqual(player["herblore_exp"], 2000.0)
        self.assertEqual(player["ranged_exp"], 2000.0)
        self.assertEqual(player["prayer_exp"], 0.0)


class TestZogreFleshEatersProductFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_successful_review_answers_complete_the_quest(self):
        addon = _load_addon_as_package("ankiscape_zogre_flesh_eaters_e2e")
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
        addon._state.player_data = _combat_ready_zogre_player()
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()

        self.assertTrue(addon.on_set_quest(QUEST_ID), calls["dialogs"])
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            for review_count in range(1, 31):
                _answer_review(addon)
                if addon._state.player_data["quests"][QUEST_ID]["completed"]:
                    break
            else:
                self.fail("Zogre Flesh Eaters did not complete within 30 reviews")
        finally:
            addon.random.random = original_random

        self.assertTrue(addon._state.player_data["quests"][QUEST_ID]["completed"])
        self.assertEqual(
            quest_action_proofs_for_quest(addon._state.player_data, QUEST_ID, addon.QUEST_DATA),
            STAGE_ACTIONS,
        )
        self.assertEqual(addon._state.player_data["inventory"]["Black prism"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Relicym's balm"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Ruined backpack"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Zogre bones"], 2)
        self.assertEqual(addon._state.player_data["inventory"]["Ourg bones"], 3)
        self.assertEqual(addon._state.player_data["inventory"]["Ogre artefact"], 1)
        self.assertEqual(addon._state.player_data["fletching_exp"], 2000.0)
        self.assertEqual(addon._state.player_data["herblore_exp"], 2000.0)
        self.assertEqual(addon._state.player_data["ranged_exp"], 2000.0)
        self.assertEqual(addon._state.player_data["prayer_exp"], 0.0)
        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(calls["gains"][-1], "Zogre Flesh Eaters complete")
        self.assertEqual(calls["dialogs"][-1][0], "Quest complete")
        self.assertIn("Zogre Flesh Eaters is complete", calls["dialogs"][-1][1])
        self.assertGreaterEqual(calls["saves"], review_count)


if __name__ == "__main__":
    unittest.main()
