from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    COMBAT_ENEMY_DATA,
    EQUIPMENT_DATA,
    EXTRA_ITEM_IMAGES,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.data.temple_trekking_data import (
    TEMPLE_TREKKING_ACTIVITY_ID,
    TEMPLE_TREKKING_ASSET_MANIFEST,
    TEMPLE_TREKKING_COMBAT_TARGET_ID,
    TEMPLE_TREKKING_COMPANION_XP_THRESHOLDS,
    TEMPLE_TREKKING_EVENTS_BY_ID,
    TEMPLE_TREKKING_REWARDS,
    TEMPLE_TREKKING_TOKEN_ITEMS,
)
from ankiscape.logic.achievement_diary_logic import refresh_achievement_diaries_pure
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.logic.temple_trekking_logic import (
    apply_temple_trekking_command_pure,
    apply_temple_trekking_review_pure,
    default_temple_trekking_state_pure,
    enter_temple_trekking_pure,
    redeem_temple_trekking_token_pure,
    sanitize_temple_trekking_state_pure,
    set_temple_trekking_policy_pure,
    stock_temple_trekking_food_pure,
    temple_trekking_view_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


ROOT = Path(__file__).resolve().parents[1]


def _complete_quest(data, quest_id: str) -> None:
    data.setdefault("quests", {})[quest_id] = {
        "started": True,
        "progress": 99,
        "completed": True,
    }


def _player(*, direction: str = "trek", route: str = "easy", companion: str = ""):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for quest_id in (
        "in_aid_of_the_myreque",
        "the_darkness_of_hallowvale",
        "nature_spirit",
        "legacy_of_seergaze",
    ):
        _complete_quest(data, quest_id)
    for key in (
        "attack_level",
        "strength_level",
        "defense_level",
        "constitution_level",
        "magic_level",
        "ranged_level",
    ):
        data[key] = 99
    data["combat_lifepoints"] = 990
    data["equipment"] = {"weapon": "Abyssal whip"}
    data["inventory"].update(
        {
            "Logs": 100,
            "Knife": 1,
            "Lobster": 100,
            "Silver sickle (b)": 1,
            "Druid pouch": 1,
        }
    )
    payload = {"direction": direction, "route": route}
    if companion:
        payload["companion"] = companion
    data, ok, info = set_temple_trekking_policy_pure(data, payload)
    if not ok:
        raise AssertionError(info)
    return data


def _entered(**kwargs):
    data = _player(**kwargs)
    data, ok, info = apply_temple_trekking_command_pure(data, "prepare_pouch")
    if not ok:
        raise AssertionError(info)
    data, ok, info = enter_temple_trekking_pure(data)
    if not ok:
        raise AssertionError(info)
    return data


def _force_nodes(data, nodes):
    data = copy.deepcopy(data)
    session = data["temple_trekking"]["session"]
    session["nodes"] = list(nodes)
    session["cursor"] = 0
    session["route_history"] = ()
    session["event_stage"] = 0
    session["encounter"] = {}
    session["enemies_remaining"] = 0
    data["combat_encounter"] = {}
    return data


class TempleTrekkingDataSourceAssetTests(unittest.TestCase):
    def test_schema_registries_sources_assets_and_cutoff_uploads(self):
        self.assertGreaterEqual(CURRENT_CONFIG_VERSION, 94)
        self.assertIn(TEMPLE_TREKKING_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        self.assertIn(TEMPLE_TREKKING_COMBAT_TARGET_ID, COMBAT_ENEMY_DATA)
        self.assertEqual(len(TEMPLE_TREKKING_COMPANION_XP_THRESHOLDS), 99)
        self.assertEqual(TEMPLE_TREKKING_COMPANION_XP_THRESHOLDS[-1], 16_000)
        self.assertEqual(
            set(TEMPLE_TREKKING_EVENTS_BY_ID),
            {
                "abidor_crank",
                "bridge",
                "bog",
                "river",
                "campsite",
                "ghasts",
                "swamp_snakes",
                "swamp_creature",
                "vyrewatch",
            },
        )
        source = UTILITY_ACTIVITY_DATA[TEMPLE_TREKKING_ACTIVITY_ID]["source"]
        self.assertIn("oldid=6514712", source)
        self.assertIn("rev-727 enum 5033/5034", source)
        self.assertIn("OpenRS2 cache 309", source)
        for row in TEMPLE_TREKKING_ASSET_MANIFEST:
            self.assertTrue((ROOT / str(row["output_path"])).is_file())
        definitions = {row.storage_key: row for row in ITEM_DEFINITIONS}
        for item in ("Druid pouch", *TEMPLE_TREKKING_TOKEN_ITEMS.values()):
            self.assertIn(item, definitions)
            self.assertTrue(Path(EXTRA_ITEM_IMAGES[item]).is_file())

        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        expected = {
            "activityitems/temple_trekking_token_blue.png": (
                "2008-11-01T01:54:27Z",
                "83ba6672484ba107378a38dc1b6cd96cf6b7b729",
            ),
            "activityitems/temple_trekking_token_yellow.png": (
                "2011-12-05T09:36:53Z",
                "dc525655a897bcee88793fbfa27e1561c2c55210",
            ),
            "activityitems/temple_trekking_token_red.png": (
                "2008-11-01T01:56:40Z",
                "ce76de7c0ed0b57309d0294fc990248ff31c8ea9",
            ),
        }
        for path, (timestamp, sha1) in expected.items():
            self.assertEqual(provenance[path]["timestamp"], timestamp)
            self.assertEqual(provenance[path]["sha1"], sha1)
            self.assertLess(timestamp, "2012-11-20T00:00:00Z")

    def test_cadence_and_generated_diary_rows_use_live_counters(self):
        cadence = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["action_id"] == TEMPLE_TREKKING_ACTIVITY_ID
        )
        self.assertEqual(cadence["review_ticks"], 6)
        self.assertIn("Again advances nothing", cadence["notes"])
        tasks = {
            task.source_id: task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
        }
        expected = {
            952: "temple_trekking.completions.trek_easy_easy",
            964: "temple_trekking.completions.trek_medium_medium",
            965: "temple_trekking.completions.ramble_any",
            983: "temple_trekking.completions.trek_hard_hard",
        }
        for source_id, key in expected.items():
            self.assertEqual(tasks[source_id].conditions[0].kind, "counter")
            self.assertEqual(tasks[source_id].conditions[0].key, key)


class TempleTrekkingPureGraphRewardTests(unittest.TestCase):
    def test_smallest_event_graph_has_live_hybrid_direction_and_quest_edges(self):
        trek = _player(direction="trek")
        trek["quests"].pop("legacy_of_seergaze", None)
        entered, ok, info = enter_temple_trekking_pure(trek)
        self.assertTrue(ok, info)
        for trek_number in range(1, 20):
            entered["temple_trekking"]["treks_started"] = trek_number - 1
            entered["temple_trekking"]["session"] = {}
            entered["activity_session"] = {"active_id": ""}
            entered, ok, info = enter_temple_trekking_pure(entered)
            self.assertTrue(ok, info)
            nodes = entered["temple_trekking"]["session"]["nodes"]
            self.assertNotIn("swamp_creature", nodes)
            self.assertNotIn("vyrewatch", nodes)

        campsite = _force_nodes(_entered(), ("campsite",) * 4)
        campsite["temple_trekking"]["companion_food"] = 1
        fed, ok, result = apply_temple_trekking_review_pure(campsite)
        self.assertTrue(ok, result)
        self.assertEqual(fed["temple_trekking"]["companion_food"], 0)
        self.assertEqual(fed["temple_trekking"]["session"]["cursor"], 1)

        ramble = _player(direction="ramble")
        found_swamp = found_vyre = False
        for _ in range(20):
            ramble, ok, info = enter_temple_trekking_pure(ramble)
            self.assertTrue(ok, info)
            nodes = ramble["temple_trekking"]["session"]["nodes"]
            found_swamp |= "swamp_creature" in nodes
            found_vyre |= "vyrewatch" in nodes
            ramble["temple_trekking"]["session"] = {}
            ramble["activity_session"] = {"active_id": ""}
        self.assertTrue(found_swamp)
        self.assertTrue(found_vyre)

    def test_swamp_creature_uses_two_live_combat_stages(self):
        data = _force_nodes(
            _entered(direction="ramble"),
            ("swamp_creature",) * 4,
        )
        data["temple_trekking"]["session"]["enemies_remaining"] = 2
        saw_second_stage = False
        for _ in range(20):
            session = data["temple_trekking"]["session"]
            session["encounter"] = {
                "target_id": TEMPLE_TREKKING_COMBAT_TARGET_ID,
                "enemy_lifepoints": 1,
            }
            data, ok, result = apply_temple_trekking_review_pure(
                data,
                lambda: 0.0,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)
            session = data["temple_trekking"]["session"]
            if session and session["event_stage"] == 1:
                saw_second_stage = True
                self.assertEqual(session["cursor"], 0)
            if session and session["cursor"] == 1:
                break
        self.assertTrue(saw_second_stage)
        self.assertEqual(data["temple_trekking"]["session"]["cursor"], 1)

    def test_active_route_policy_applies_at_the_next_encounter_boundary(self):
        data = _force_nodes(_entered(route="easy"), ("abidor_crank",) * 4)
        changed, ok, info = set_temple_trekking_policy_pure(data, {"route": "hard"})
        self.assertTrue(ok, info)
        self.assertEqual(changed["temple_trekking"]["session"]["route"], "easy")
        changed, ok, result = apply_temple_trekking_review_pure(changed)
        self.assertTrue(ok, result)
        session = changed["temple_trekking"]["session"]
        self.assertEqual(session["route_history"], ("easy",))
        self.assertEqual(session["route"], "hard")

    def test_direction_change_defaults_companion_and_food_loads_mid_trek(self):
        data = _player()
        changed, ok, info = set_temple_trekking_policy_pure(data, {"direction": "ramble"})
        self.assertTrue(ok, info)
        self.assertEqual(changed["temple_trekking"]["policy"]["companion"], "pazuzu")
        entered, ok, info = enter_temple_trekking_pure(changed)
        self.assertTrue(ok, info)
        stocked, ok, info = stock_temple_trekking_food_pure(entered, 28)
        self.assertTrue(ok, info)
        self.assertEqual(stocked["temple_trekking"]["companion_food"], 28)
        self.assertTrue(temple_trekking_view_pure(stocked)["food_load_enabled"] is False)

    def test_locked_direction_cannot_be_saved_as_the_active_plan(self):
        data = _player()
        data["quests"]["the_darkness_of_hallowvale"]["completed"] = False
        before = copy.deepcopy(data["temple_trekking"]["policy"])
        unchanged, ok, info = set_temple_trekking_policy_pure(
            data, {"direction": "ramble"}
        )
        self.assertFalse(ok)
        self.assertIn("Darkness Of Hallowvale", info["reason"])
        self.assertEqual(unchanged["temple_trekking"]["policy"], before)

    def test_default_locked_direction_does_not_block_saving_other_plan_fields(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        changed, ok, info = set_temple_trekking_policy_pure(
            data,
            {
                "direction": "trek",
                "route": "hard",
                "companion": "dean_vellio",
                "reward": "raw_shark",
            },
        )
        self.assertTrue(ok, info)
        self.assertEqual(changed["temple_trekking"]["policy"]["route"], "hard")
        self.assertEqual(
            changed["temple_trekking"]["policy"]["reward"], "raw_shark"
        )

    def test_route_history_xp_curve_completion_token_and_diary_proof(self):
        data = _force_nodes(_entered(), ("abidor_crank",) * 4)
        for _ in range(4):
            data, ok, result = apply_temple_trekking_review_pure(data)
            self.assertTrue(ok, result)
        self.assertTrue(result["completed"])
        state = data["temple_trekking"]
        self.assertEqual(state["companion_xp"]["dean_vellio"], 4)
        self.assertEqual(state["companion_levels"]["dean_vellio"], 2)
        self.assertEqual(state["completions"]["trek_easy_easy"], 1)
        self.assertEqual(data["inventory"]["Reward token (blue)"], 1)
        refreshed, newly = refresh_achievement_diaries_pure(data)
        self.assertIn("morytania_easy_only_going_forward_we_can_t_find_reverse", newly)
        self.assertIn(
            "morytania_easy_only_going_forward_we_can_t_find_reverse",
            refreshed["achievement_diaries"]["completed_tasks"],
        )

    def test_blue_yellow_and_red_tokens_are_earned_then_redeemed_through_play(self):
        cases = (
            ("easy", "dean_vellio", "blue"),
            ("medium", "jayene_kliyn", "yellow"),
            ("hard", "smiddi_ryak", "red"),
        )
        for route, companion, color in cases:
            with self.subTest(color=color):
                data = _player(route=route, companion=companion)
                data["current_combat_target"] = "abyssal_demon"
                data["carried_inventory"] = {"abyssal_demon": {"Lobster": 28}}
                data, ok, info = apply_temple_trekking_command_pure(
                    data, "stock_food", {"quantity": 28}
                )
                self.assertTrue(ok, info)
                data, ok, info = apply_temple_trekking_command_pure(
                    data, "prepare_pouch"
                )
                self.assertTrue(ok, info)
                data, ok, info = enter_temple_trekking_pure(data)
                self.assertTrue(ok, info)
                self.assertEqual(
                    data["carried_inventory"][TEMPLE_TREKKING_COMBAT_TARGET_ID][
                        "Lobster"
                    ],
                    28,
                )
                for _ in range(500):
                    if data["temple_trekking"]["companion_food"] < 28:
                        data, ok, info = stock_temple_trekking_food_pure(data, 28)
                        self.assertTrue(ok, info)
                    data, ok, result = apply_temple_trekking_review_pure(
                        data,
                        lambda: 0.5,
                        equipment_data=EQUIPMENT_DATA,
                    )
                    self.assertTrue(ok, result)
                    if result.get("terminal"):
                        break
                else:
                    self.fail(f"{route} trek did not terminate")
                self.assertTrue(result.get("completed"), result)
                self.assertEqual(result["token_color"], color)
                self.assertTrue(data["combat_auto_flee"])
                self.assertEqual(
                    data["temple_trekking"]["completions"][
                        f"trek_{route}_{route}"
                    ],
                    1,
                )
                token_item = TEMPLE_TREKKING_TOKEN_ITEMS[color]
                self.assertEqual(data["inventory"][token_item], 1)
                self.assertNotIn(
                    TEMPLE_TREKKING_COMBAT_TARGET_ID,
                    data.get("carried_inventory", {}),
                )
                redeemed, ok, reward = redeem_temple_trekking_token_pure(
                    data, color, "pure_essence", 0.5
                )
                self.assertTrue(ok, reward)
                self.assertEqual(redeemed["inventory"][token_item], 0)
                self.assertGreater(reward["outputs"]["Pure essence"], 0)

    def test_every_reward_row_is_live_for_every_token_tier(self):
        for color, token_item in TEMPLE_TREKKING_TOKEN_ITEMS.items():
            for reward in TEMPLE_TREKKING_REWARDS:
                with self.subTest(color=color, reward=reward.id):
                    data = _player()
                    data["inventory"][token_item] = 1
                    redeemed, ok, result = redeem_temple_trekking_token_pure(
                        data, color, reward.id, 0.5
                    )
                    self.assertTrue(ok, result)
                    self.assertEqual(redeemed["inventory"][token_item], 0)
                    self.assertTrue(result["outputs"])
                    for item, amount in result["outputs"].items():
                        self.assertGreater(amount, 0, item)
                        self.assertEqual(redeemed["inventory"][item], amount)

    def test_again_and_blocked_ghast_are_nonmutating_and_nonterminal(self):
        data = _force_nodes(_entered(), ("ghasts",) * 4)
        data["temple_trekking"]["pouch_charges"] = 0
        before = copy.deepcopy(data)
        unchanged, ok, result = apply_temple_trekking_review_pure(data, productive=False)
        self.assertTrue(ok, result)
        self.assertEqual(unchanged, before)
        blocked, ok, result = apply_temple_trekking_review_pure(data)
        self.assertTrue(ok, result)
        self.assertFalse(result["advanced"])
        self.assertTrue(result["blocked"])
        self.assertIn("charged Druid pouch", result["reason"])
        self.assertEqual(blocked, before)
        view = temple_trekking_view_pure(blocked)
        self.assertTrue(view["active"])
        self.assertEqual(view["review_reasons"], (result["reason"],))


class TempleTrekkingPersistenceRuntimeTests(unittest.TestCase):
    def test_v93_migrates_to_v94_and_interrupted_session_resumes(self):
        old = _force_nodes(_entered(), ("bog",) * 4)
        old["config_version"] = 93
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["activity_session"], {"active_id": TEMPLE_TREKKING_ACTIVITY_ID}
        )
        self.assertTrue(migrated["temple_trekking"]["session"])
        self.assertEqual(migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS), migrated)

    def test_resuming_does_not_refill_a_partially_consumed_carried_pack(self):
        data = _entered()
        data["temple_trekking"]["session"]["previous_combat_target"] = "abyssal_demon"
        data["carried_inventory"] = {
            "abyssal_demon": {"Lobster": 20},
            TEMPLE_TREKKING_COMBAT_TARGET_ID: {"Lobster": 1},
        }
        resumed, ok, info = enter_temple_trekking_pure(data)
        self.assertTrue(ok, info)
        self.assertEqual(
            resumed["carried_inventory"][TEMPLE_TREKKING_COMBAT_TARGET_ID][
                "Lobster"
            ],
            1,
        )

    def test_invalid_interrupted_session_cannot_leave_a_dangling_activity_owner(self):
        old = _player()
        old["config_version"] = 93
        old["temple_trekking"] = {"session": {"nodes": ["not_an_event"]}}
        old["activity_session"] = {"active_id": TEMPLE_TREKKING_ACTIVITY_ID}
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["temple_trekking"]["session"], {})
        self.assertEqual(migrated["activity_session"], {"active_id": ""})

    def test_sanitizer_repairs_corrupt_state_and_exact_xp_curve(self):
        clean = sanitize_temple_trekking_state_pure(
            {
                "policy": {"direction": "sideways", "route": "fatal", "companion": "nobody"},
                "companion_xp": {"dean_vellio": 16_000_000},
                "pouch_charges": 99,
                "companion_food": 99,
                "session": {"nodes": ["not_an_event"]},
            }
        )
        self.assertEqual(clean["policy"]["direction"], "trek")
        self.assertEqual(clean["companion_xp"]["dean_vellio"], 16_000)
        self.assertEqual(clean["companion_levels"]["dean_vellio"], 99)
        self.assertEqual(clean["pouch_charges"], 3)
        self.assertEqual(clean["companion_food"], 28)
        self.assertEqual(clean["session"], {})

        valid_session = copy.deepcopy(_entered()["temple_trekking"]["session"])
        valid_session["route_history"] = "hard"
        repaired = sanitize_temple_trekking_state_pure({"session": valid_session})
        self.assertEqual(repaired["session"]["route_history"], ())

    def test_real_runtime_dispatch_persists_noncombat_review(self):
        player = _force_nodes(_entered(), ("bog",) * 4)
        calls = {"saves": 0, "messages": [], "errors": []}
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda title, message: calls["errors"].append((title, message)),
            deactivate_current_skill=lambda: None,
            award_skill_exp=lambda _key, amount: amount,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
            refresh_skill_availability=lambda: None,
            refresh_skill_availability_partial=lambda *_args: None,
            can_smith_any=lambda: True,
            show_exp=lambda *_args: None,
            show_activity_gain=lambda message: calls["messages"].append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(player["temple_trekking"]["session"]["cursor"], 1)
        telemetry = player["action_telemetry"]["actions"][
            f"utility:{TEMPLE_TREKKING_ACTIVITY_ID}"
        ]
        self.assertEqual(telemetry["attempts"], 1)

        blocked = _force_nodes(_entered(), ("ghasts",) * 4)
        blocked["temple_trekking"]["pouch_charges"] = 0
        calls.update({"saves": 0, "messages": [], "errors": []})
        ctx.player_data = blocked
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 1)
        self.assertIn("charged Druid pouch", calls["messages"][0])
        self.assertEqual(blocked["temple_trekking"]["session"]["cursor"], 0)


try:
    from aqt.qt import QApplication, QColor, QPalette
    from ankiscape.ui.temple_trekking_panel import HAS_QT, TempleTrekkingPanel
except Exception:
    QApplication = None
    HAS_QT = False
    TempleTrekkingPanel = None


@unittest.skipUnless(HAS_QT, "Qt lane only")
class TempleTrekkingQtPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
        cls.app.setPalette(palette)

    def test_dark_560_point_panel_follows_every_pure_view_flag(self):
        player = _entered()
        panel = TempleTrekkingPanel(
            player,
            on_command=lambda *_args: {"ok": True},
            on_select=lambda _activity: True,
        )
        panel.show()
        panel.resize(760, 560)
        for _ in range(4):
            QApplication.processEvents()
        view = temple_trekking_view_pure(player)
        self.assertLessEqual(panel.sizeHint().height(), 560)
        self.assertLessEqual(panel.layout().minimumSize().height(), 560)
        self.assertEqual(panel.primary_button.isEnabled(), view["primary_enabled"])
        self.assertEqual(panel.direction_combo.isEnabled(), view["direction_control_enabled"])
        self.assertEqual(panel.route_combo.isEnabled(), view["route_control_enabled"])
        self.assertEqual(panel.companion_combo.isEnabled(), view["companion_control_enabled"])
        self.assertEqual(panel.reward_combo.isEnabled(), view["reward_control_enabled"])
        self.assertEqual(panel.abandon_button.isVisible(), view["abandon_visible"])
        self.assertEqual(panel.food_button.isEnabled(), view["food_load_enabled"])
        self.assertEqual(panel.pouch_button.isEnabled(), view["pouch_prepare_enabled"])
        self.assertEqual(panel.redeem_button.isEnabled(), view["redeem_enabled"])
        self.assertEqual(
            panel.companion_health.value(), view["companion_lifepoints"]
        )
        self.assertTrue(panel.companion_health.isVisible())
        panel.close()

    def test_active_block_reason_is_rendered_without_view_owned_rules_in_qt(self):
        player = _force_nodes(_entered(), ("ghasts",) * 4)
        player["temple_trekking"]["pouch_charges"] = 0
        panel = TempleTrekkingPanel(player, on_command=lambda *_args: {"ok": True})
        panel.show()
        for _ in range(4):
            QApplication.processEvents()
        self.assertTrue(panel.requirements.isVisible())
        self.assertIn("charged Druid pouch", panel.requirements.text())
        panel.close()

    def test_locked_direction_rows_are_disabled_from_the_pure_view_flag(self):
        player = _player()
        player["quests"]["the_darkness_of_hallowvale"]["completed"] = False
        panel = TempleTrekkingPanel(player, on_command=lambda *_args: {"ok": True})
        panel.show()
        for _ in range(4):
            QApplication.processEvents()
        ramble_index = panel.direction_combo.findData("ramble")
        self.assertGreaterEqual(ramble_index, 0)
        self.assertFalse(panel.direction_combo.model().item(ramble_index).isEnabled())
        panel.close()


if __name__ == "__main__":
    unittest.main()
