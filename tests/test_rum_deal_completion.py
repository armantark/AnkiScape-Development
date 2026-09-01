import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA, QUEST_DATA
from ankiscape.data.quest_data import QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID
from ankiscape.data.rum_deal_data import RUM_DEAL_STAGE_SOURCE
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_locked_reasons_pure,
    start_quest_pure,
)
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest
from tests.test_combat_quest_gate import _answer_review, _maxed_player_for_quest
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


QUEST_ID = "rum_deal"
STAGE_CLEANUPS = QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID[QUEST_ID]
# Frozen oracle: /Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/rum-deal-target-contract.json, quest_route.
STAGE_ACTIONS = (
    "Accept Pirate Pete's offer, reach Braindeath Island, receive the Blindweed seed, and rake and plant the surviving patch",
    "Wait 4 minutes 35 seconds, harvest the Blindweed, add it to the hopper, then collect and add stagnant water",
    "Catch and pressurise five sea creatures, bless the wrench with at least 470 current Prayer points without draining them, then defeat the Evil spirit",
    "Defeat a Fever spider while wearing Slayer gloves, add its body to the hopper, give the swill to Captain Donnie, and report to Captain Braindeath",
)


def _combat_ready_rum_deal_player(*, slayer_gloves=False) -> dict:
    player = _maxed_player_for_quest(QUEST_ID)
    player["quest_combat_config"] = {"resolver_enabled": True}
    player["inventory"]["Shark"] = 28
    player["combat_supply_loadout"]["food"] = {"Shark": 28}
    if slayer_gloves:
        player["equipment"]["hands"] = "Slayer gloves"
    return player


class TestRumDealStageContract(unittest.TestCase):
    def test_all_stage_sentinels_are_replaced_by_the_frozen_route(self):
        stage_rows = QUEST_DATA[QUEST_ID]["stage_requirements"]
        self.assertEqual(len(stage_rows), 4)
        rows = {row["stage"]: row for row in stage_rows}
        self.assertEqual(set(rows), set(range(1, 5)))
        self.assertEqual(
            tuple(rows[stage]["required_actions"] for stage in range(1, 5)),
            ((), (), (), ()),
        )
        self.assertEqual(
            tuple(rows[stage]["auto_actions"][0] for stage in range(1, 5)),
            STAGE_ACTIONS,
        )
        self.assertEqual(
            tuple(rows[stage]["required_inventory"] for stage in range(1, 5)),
            ({}, {}, {}, {}),
        )
        self.assertEqual(
            tuple(rows[stage]["required_tools"] for stage in range(1, 5)),
            ({}, {}, {}, {"Slayer gloves": 1}),
        )
        self.assertEqual(
            tuple(cleanup.remove_required_actions for cleanup in STAGE_CLEANUPS),
            tuple(
                (f"Complete Rum Deal stage {stage} objective",)
                for stage in range(1, 5)
            ),
        )
        self.assertEqual(
            {rows[stage]["source"] for stage in range(1, 5)},
            {RUM_DEAL_STAGE_SOURCE},
        )
        self.assertEqual(
            tuple(
                tuple(
                    encounter["encounter_id"]
                    for encounter in rows[stage]["combat_encounters"]
                )
                for stage in range(1, 5)
            ),
            ((), (), ("rum_deal_evil_spirit_150",), ("rum_deal_fever_spider_49",)),
        )
        self.assertEqual(rows[3]["combat_encounters"][0]["guaranteed_drops"], {})
        self.assertEqual(
            rows[4]["combat_encounters"][0]["guaranteed_drops"],
            {"Fever spider body": 1},
        )
        self.assertEqual(
            QUEST_DATA[QUEST_ID]["xp_rewards"],
            (
                {"skill_id": "farming", "amount": 7000.0},
                {"skill_id": "fishing", "amount": 7000.0},
                {"skill_id": "prayer", "amount": 7000.0},
            ),
        )
        self.assertEqual(
            QUEST_DATA[QUEST_ID]["rewards"],
            {"Fishbowl and net": 1, "Holy wrench": 1},
        )


class TestRumDealPureFlow(unittest.TestCase):
    def _resolve_current_fight(self, player, expected_name):
        for _burst in range(30):
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
            self.fail(f"{expected_name} did not resolve within 30 combat bursts")
        self.assertEqual(result["display_name"], expected_name)
        return player

    def test_level_and_slayer_glove_gates_lead_to_completion(self):
        low_player = _combat_ready_rum_deal_player()
        low_player["prayer_level"] = 46
        self.assertEqual(
            quest_locked_reasons_pure(low_player, QUEST_ID, QUEST_DATA),
            ("Prayer 47",),
        )

        player, started = start_quest_pure(
            _combat_ready_rum_deal_player(),
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(started)

        for expected_progress in (2, 3):
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
            ("Battle required: Evil spirit level 150",),
        )
        self.assertEqual(
            quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA),
            STAGE_ACTIONS[:2],
        )
        player = self._resolve_current_fight(player, "Evil spirit")
        player, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(progressed)
        self.assertFalse(completed)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 4)

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player, QUEST_ID, QUEST_DATA),
            ("Needs Slayer gloves", "Battle required: Fever spider level 49"),
        )
        self.assertEqual(
            quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA),
            STAGE_ACTIONS[:3],
        )
        player["equipment"]["hands"] = "Slayer gloves"
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player, QUEST_ID, QUEST_DATA),
            ("Battle required: Fever spider level 49",),
        )
        player = self._resolve_current_fight(player, "Fever spider")
        self.assertEqual(player["inventory"]["Fever spider body"], 1)

        player, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertTrue(player["quests"][QUEST_ID]["completed"])
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 5)
        self.assertEqual(
            quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA),
            STAGE_ACTIONS,
        )
        self.assertEqual(player["quest_points"], 1002)
        self.assertEqual(player["inventory"]["Fever spider body"], 1)
        self.assertEqual(player["inventory"]["Fishbowl and net"], 1)
        self.assertEqual(player["inventory"]["Holy wrench"], 1)
        self.assertEqual(player["farming_exp"], 7000.0)
        self.assertEqual(player["fishing_exp"], 7000.0)
        self.assertEqual(player["prayer_exp"], 7000.0)
        self.assertEqual(player["slayer_exp"], 0.0)


class TestRumDealProductFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_successful_review_answers_complete_the_loaded_quest(self):
        addon = _load_addon_as_package("ankiscape_rum_deal_e2e")
        stage_rows = addon.QUEST_DATA[QUEST_ID]["stage_requirements"]
        self.assertEqual(len(stage_rows), 4)
        self.assertEqual({row["stage"] for row in stage_rows}, set(range(1, 5)))

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
        addon.player_data = _combat_ready_rum_deal_player(slayer_gloves=True)
        addon.current_skill = "Quests"
        addon._REVIEW_UNDO_STACK.clear()

        self.assertTrue(addon.on_set_quest(QUEST_ID), calls["dialogs"])
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            for review_count in range(1, 41):
                _answer_review(addon)
                if addon.player_data["quests"][QUEST_ID]["completed"]:
                    break
            else:
                self.fail("Rum Deal did not complete within 40 reviews")
        finally:
            addon.random.random = original_random

        self.assertTrue(addon.player_data["quests"][QUEST_ID]["completed"])
        self.assertEqual(
            quest_action_proofs_for_quest(
                addon.player_data,
                QUEST_ID,
                addon.QUEST_DATA,
            ),
            STAGE_ACTIONS,
        )
        # The frozen contract's quest_route.fever_spider line says the hopper consumes the body once; this retained residue is the open gap.
        self.assertEqual(addon.player_data["inventory"]["Fever spider body"], 1)
        self.assertEqual(addon.player_data["inventory"]["Fishbowl and net"], 1)
        self.assertEqual(addon.player_data["inventory"]["Holy wrench"], 1)
        self.assertEqual(addon.player_data["farming_exp"], 7000.0)
        self.assertEqual(addon.player_data["fishing_exp"], 7000.0)
        self.assertEqual(addon.player_data["prayer_exp"], 7000.0)
        self.assertEqual(addon.current_skill, "Utilities")
        self.assertEqual(calls["gains"][-1], "Rum Deal complete")
        self.assertEqual(calls["dialogs"][-1][0], "Quest complete")
        self.assertIn("Rum Deal is complete", calls["dialogs"][-1][1])
        self.assertGreaterEqual(calls["saves"], review_count)


if __name__ == "__main__":
    unittest.main()
