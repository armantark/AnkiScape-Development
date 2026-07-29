from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    COOKING_DATA,
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
from ankiscape.data.combat_data import COMBAT_FOOD_DATA, CONSUMABLE_DATA
from ankiscape.data.gnome_restaurant_data import (
    GNOME_COCKTAIL_ITEMS,
    GNOME_COCKTAIL_TARGET_IDS,
    GNOME_DISH_ITEMS,
    GNOME_DISH_TARGET_IDS,
    GNOME_RESTAURANT_ACTIVITY_ID,
    GNOME_RESTAURANT_ASSET_MANIFEST,
    GNOME_RESTAURANT_BOX_ITEM,
    GNOME_RESTAURANT_CUSTOMERS,
    GNOME_RESTAURANT_TIPS,
    GNOME_RESTAURANT_TOKEN_ITEM,
    GNOME_RESTAURANT_TOKEN_MEAL_CAP,
    GNOME_RESTAURANT_TOKEN_POINTS,
)
from ankiscape.data.temple_trekking_data import TEMPLE_TREKKING_ACTIVITY_ID
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.logic.gnome_restaurant_logic import (
    apply_gnome_restaurant_command_pure,
    apply_gnome_restaurant_review_pure,
    default_gnome_restaurant_state_pure,
    gnome_restaurant_can_review_pure,
    gnome_restaurant_training_pure,
    gnome_restaurant_view_pure,
    sanitize_gnome_restaurant_state_pure,
)
from ankiscape.logic.temple_trekking_logic import enter_temple_trekking_pure
from ankiscape.logic_pure.logic_pure_consumables import apply_consumable_pure
from ankiscape.runtime.runtime_actions import RuntimeActionContext
from ankiscape.runtime.runtime_actions_utility import handle_utility_answer


ROOT = Path(__file__).resolve().parents[1]
_QUESTS = (
    "troll_romance",
    "fishing_contest",
    "monkey_madness",
    "the_grand_tree",
    "the_giant_dwarf",
)


def _rng(values):
    """A deterministic roll sequence that repeats its last value."""
    remaining = list(values)

    def _next():
        return remaining.pop(0) if len(remaining) > 1 else remaining[0]

    return _next


def _player(*, trained=True, dishes=4, cocktails=4):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["cooking_level"] = 42
    data["magic_level"] = 66
    data["quests"] = {quest: {"completed": True} for quest in _QUESTS}
    if trained:
        actions = {
            f"cooking:{target_id}": {"attempts": 1, "successes": 1}
            for target_id in list(GNOME_DISH_TARGET_IDS)[:dishes]
            + list(GNOME_COCKTAIL_TARGET_IDS)[:cocktails]
        }
        data["action_telemetry"] = {"actions": actions}
    return data


def _hired(**kwargs):
    data = _player(**kwargs)
    data, ok, info = apply_gnome_restaurant_command_pure(data, "open_service")
    if not ok:
        raise AssertionError(info)
    return data


def _on_job(difficulty="easy", rng=None, **kwargs):
    data = _hired(**kwargs)
    data, ok, info = apply_gnome_restaurant_command_pure(
        data, "accept_order", {"difficulty": difficulty}, rng or _rng([0.0])
    )
    if not ok:
        raise AssertionError(info)
    return data


def _deliverable(data):
    data = copy.deepcopy(data)
    data["inventory"][str(data["gnome_restaurant"]["order"]["item"])] = 1
    return data


class GnomeRestaurantDataSourceAssetTests(unittest.TestCase):
    def test_schema_registries_recipes_and_cutoff_uploads(self):
        self.assertEqual(
            default_player_data(ORE_DATA, ITEM_DEFINITIONS)["config_version"],
            CURRENT_CONFIG_VERSION,
        )
        self.assertIn(GNOME_RESTAURANT_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        self.assertEqual(
            UTILITY_ACTIVITY_DATA[GNOME_RESTAURANT_ACTIVITY_ID]["surface"], "activities"
        )
        self.assertIn(
            "oldid=6491107",
            UTILITY_ACTIVITY_DATA[GNOME_RESTAURANT_ACTIVITY_ID]["source"],
        )
        self.assertEqual(len(GNOME_DISH_ITEMS), 13)
        self.assertEqual(len(GNOME_COCKTAIL_ITEMS), 7)
        self.assertEqual(
            sum(1 for row in GNOME_RESTAURANT_CUSTOMERS if row.difficulty == "easy"), 19
        )
        self.assertEqual(
            sum(1 for row in GNOME_RESTAURANT_CUSTOMERS if row.difficulty == "hard"), 20
        )

        # Exact Cooking rows: level, XP, and the union of both assembly stages.
        toad = COOKING_DATA["bake_toad_crunchies"]
        self.assertEqual(toad["level"], 10)
        self.assertEqual(toad["exp"], 100.0)
        self.assertEqual(
            toad["requirements"],
            {
                "Gianne dough": 1,
                "Crunchy tray": 1,
                "Toad's legs": 2,
                "Gnome spice": 1,
                "Equa leaves": 1,
            },
        )
        self.assertEqual(toad["burnt_item"], "Burnt crunchies")
        self.assertEqual(COOKING_DATA["bake_chocolate_bomb"]["exp"], 190.0)
        self.assertEqual(COOKING_DATA["bake_worm_batta"]["exp"], 154.0)
        blast = COOKING_DATA["mix_fruit_blast"]
        self.assertEqual(blast["level"], 6)
        self.assertTrue(blast["source_always_succeeds"])
        self.assertEqual(blast["requirements"]["Cocktail glass"], 1)
        self.assertEqual(blast["byproducts"], {"Cocktail shaker": 1})

        definitions = {row.storage_key for row in ITEM_DEFINITIONS}
        for item in (
            *GNOME_DISH_ITEMS,
            *GNOME_COCKTAIL_ITEMS,
            GNOME_RESTAURANT_TOKEN_ITEM,
            GNOME_RESTAURANT_BOX_ITEM,
            *(row.item for row in GNOME_RESTAURANT_TIPS),
        ):
            self.assertIn(item, definitions, item)
        for row in GNOME_RESTAURANT_ASSET_MANIFEST:
            self.assertTrue((ROOT / str(row["output_path"])).is_file(), row)
            item_name = str(row["item_name"])
            if str(row["output_path"]).startswith("activityitems/"):
                self.assertTrue(Path(EXTRA_ITEM_IMAGES[item_name]).is_file())
        self.assertTrue(
            Path(
                str(UTILITY_ACTIVITY_DATA[GNOME_RESTAURANT_ACTIVITY_ID]["icon_path"])
            ).is_file()
        )

        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        for row in GNOME_RESTAURANT_ASSET_MANIFEST:
            timestamp = provenance[str(row["output_path"])]["timestamp"]
            self.assertLess(timestamp, "2012-11-20T00:00:00Z", row)

    def test_food_and_cocktail_effects_are_live(self):
        for item in GNOME_DISH_ITEMS:
            self.assertIn(item, COMBAT_FOOD_DATA, item)
            self.assertNotIn(item, CONSUMABLE_DATA, item)
        self.assertEqual(COMBAT_FOOD_DATA["Toad crunchies"]["heal_lifepoints"], 120)
        self.assertEqual(
            COMBAT_FOOD_DATA["Tangled toads' legs"]["heal_lifepoints"], 150
        )
        for item in GNOME_COCKTAIL_ITEMS:
            self.assertIn(item, CONSUMABLE_DATA, item)
            self.assertNotIn(item, COMBAT_FOOD_DATA, item)

        player = _player()
        player["inventory"]["Wizard blizzard"] = 1
        player["combat_lifepoints"] = 10
        updated, result = apply_consumable_pure(player, "Wizard blizzard")
        self.assertTrue(result["allowed"])
        self.assertEqual(result["healed"], 50)
        self.assertEqual(result["boosts"], {"strength": 6})
        self.assertEqual(result["drains"], {"attack": 4})
        self.assertEqual(updated["inventory"].get("Cocktail glass"), 1)
        self.assertNotIn("Wizard blizzard", updated["inventory"])

    def test_cadence_row_states_the_delivery_translation(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["action_id"] == GNOME_RESTAURANT_ACTIVITY_ID
        )
        self.assertEqual(row["source_status"], "sourced_with_disclosed_translation")
        self.assertIn("never destroys it", row["notes"])


class GnomeRestaurantEntryAndOrderTests(unittest.TestCase):
    def test_the_gate_reads_durable_cooking_production_only(self):
        blank = _player(trained=False)
        self.assertFalse(gnome_restaurant_training_pure(blank)["complete"])
        view = gnome_restaurant_view_pure(blank)
        self.assertFalse(view["can_open"])
        self.assertIn("4 gnome dishes", view["entry_reasons"][0])
        _updated, ok, info = apply_gnome_restaurant_command_pure(blank, "open_service")
        self.assertFalse(ok)
        self.assertIn("Prepare", info["reason"])

        short = _player(dishes=4, cocktails=3)
        self.assertFalse(gnome_restaurant_training_pure(short)["complete"])
        self.assertFalse(gnome_restaurant_view_pure(short)["can_open"])

        # Nothing but production history opens the door, and it counts Cooking done
        # long before the player ever walked into the Grand Tree.
        ready = _player()
        self.assertTrue(gnome_restaurant_view_pure(ready)["can_open"])
        hired, ok, info = apply_gnome_restaurant_command_pure(ready, "open_service")
        self.assertTrue(ok, info)
        self.assertEqual(hired["inventory"][GNOME_RESTAURANT_BOX_ITEM], 1)
        self.assertEqual(hired["inventory"]["Gianne dough"], 100)
        self.assertTrue(hired["gnome_restaurant"]["service_open"])

    def test_hard_declines_wait_a_review_and_easy_declines_do_not(self):
        data = _on_job("hard")
        data["shop_market_clock"] = {"answered_cards": 40}
        declined, ok, info = apply_gnome_restaurant_command_pure(
            data, "decline_order", {}, _rng([0.0])
        )
        self.assertTrue(ok, info)
        self.assertEqual(declined["gnome_restaurant"]["hard_decline_ready_card"], 41)
        self.assertEqual(declined["gnome_restaurant"]["order"], {})
        blocked = gnome_restaurant_view_pure(declined)["difficulty_options"][1]
        self.assertFalse(blocked["accept_enabled"])
        self.assertIn("hold another hard job", blocked["accept_reason"])

        declined["shop_market_clock"] = {"answered_cards": 41}
        again, ok, info = apply_gnome_restaurant_command_pure(
            declined, "accept_order", {"difficulty": "hard"}, _rng([0.0])
        )
        self.assertTrue(ok, info)

        easy = _on_job("easy")
        swapped, ok, info = apply_gnome_restaurant_command_pure(
            easy, "decline_order", {}, _rng([0.3])
        )
        self.assertTrue(ok, info)
        self.assertEqual(swapped["gnome_restaurant"]["hard_decline_ready_card"], 0)
        self.assertTrue(swapped["gnome_restaurant"]["order"])

    def test_accepting_a_job_cannot_steal_a_temple_trekking_session(self):
        data = _hired()
        data["quests"]["in_aid_of_the_myreque"] = {
            "started": True,
            "progress": 99,
            "completed": True,
        }
        data, ok, info = enter_temple_trekking_pure(data)
        self.assertTrue(ok, info)
        self.assertEqual(
            data["activity_session"]["active_id"], TEMPLE_TREKKING_ACTIVITY_ID
        )
        trek = copy.deepcopy(data["temple_trekking"]["session"])

        option = gnome_restaurant_view_pure(data)["difficulty_options"][0]
        self.assertFalse(option["accept_enabled"])
        self.assertEqual(
            option["accept_reason"], "Finish the active persistent activity."
        )
        blocked, ok, info = apply_gnome_restaurant_command_pure(
            data, "accept_order", {"difficulty": "easy"}, _rng([0.0])
        )
        self.assertFalse(ok)
        self.assertEqual(info["reason"], "Finish the active persistent activity.")
        self.assertEqual(blocked["gnome_restaurant"]["order"], {})
        self.assertEqual(
            blocked["activity_session"]["active_id"], TEMPLE_TREKKING_ACTIVITY_ID
        )
        self.assertEqual(blocked["temple_trekking"]["session"], trek)

        reloaded = migrate_loaded_data(blocked, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(reloaded["temple_trekking"]["session"], trek)

    def test_unreachable_hard_customers_never_enter_the_pool(self):
        data = _hired()
        data["quests"] = {}
        data["magic_level"] = 1
        reached = set()
        for roll in [index / 40 for index in range(40)]:
            ordered, ok, info = apply_gnome_restaurant_command_pure(
                data, "accept_order", {"difficulty": "hard"}, _rng([roll])
            )
            self.assertTrue(ok, info)
            reached.add(str(ordered["gnome_restaurant"]["order"]["customer"]))
        for locked in (
            "brambickle",
            "captain_ninto",
            "garkor",
            "glo_caranock",
            "professor_manglethorp",
            "professor_imblewyn",
        ):
            self.assertNotIn(locked, reached)
        self.assertIn("captain_daerkin", reached)


class GnomeRestaurantDeliveryRewardTests(unittest.TestCase):
    def test_again_spends_the_window_without_destroying_the_order(self):
        data = _deliverable(_on_job("hard"))
        before = copy.deepcopy(data["gnome_restaurant"]["order"])
        self.assertEqual(before["minutes_left"], 11)
        updated, ok, result = apply_gnome_restaurant_review_pure(
            data, _rng([0.0]), productive=False
        )
        self.assertTrue(ok, result)
        self.assertFalse(result["advanced"])
        order = updated["gnome_restaurant"]["order"]
        self.assertEqual(order["minutes_left"], 5)
        self.assertEqual(order["item"], before["item"])
        self.assertEqual(order["customer"], before["customer"])
        self.assertEqual(updated["gnome_restaurant"]["points"], 0)

        twice, ok, _result = apply_gnome_restaurant_review_pure(
            updated, _rng([0.0]), productive=False
        )
        self.assertTrue(ok)
        self.assertEqual(twice["gnome_restaurant"]["order"]["minutes_left"], 0)
        self.assertTrue(twice["gnome_restaurant"]["order"])

    def test_a_delivery_needs_the_food_and_pays_source_points(self):
        data = _on_job("easy")
        self.assertFalse(gnome_restaurant_can_review_pure(data))
        _updated, ok, result = apply_gnome_restaurant_review_pure(data, _rng([0.0]))
        self.assertFalse(ok)
        self.assertIn("Cook or bank", result["reason"])

        ready = _deliverable(data)
        self.assertTrue(gnome_restaurant_can_review_pure(ready))
        item = str(ready["gnome_restaurant"]["order"]["item"])
        updated, ok, result = apply_gnome_restaurant_review_pure(ready, _rng([0.0]))
        self.assertTrue(ok, result)
        self.assertEqual(result["points_gained"], 1)
        self.assertNotIn(item, updated["inventory"])
        self.assertEqual(updated["gnome_restaurant"]["deliveries"]["easy"], 1)
        # The delivering review also takes the next job, so the loop needs no
        # direct action between deliveries.
        self.assertTrue(updated["gnome_restaurant"]["order"])

        hard = _deliverable(_on_job("hard"))
        updated, ok, result = apply_gnome_restaurant_review_pure(hard, _rng([0.0]))
        self.assertTrue(ok, result)
        self.assertEqual(result["points_gained"], 3)

    def test_easy_tips_scale_with_the_window_and_stay_in_the_sourced_range(self):
        punctual = _deliverable(_on_job("easy"))
        updated, ok, result = apply_gnome_restaurant_review_pure(punctual, _rng([0.999]))
        self.assertTrue(ok, result)
        self.assertEqual(result["tip_items"], {"Coins": 500})

        late, _ok, _result = apply_gnome_restaurant_review_pure(
            _deliverable(_on_job("easy")), _rng([0.0]), productive=False
        )
        updated, ok, result = apply_gnome_restaurant_review_pure(
            _deliverable(late), _rng([0.999])
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["tip_items"], {"Coins": 10})

    def test_every_hard_tip_row_is_reachable_through_a_real_delivery(self):
        seen = {}
        customer_count = len(GNOME_RESTAURANT_CUSTOMERS)
        for customer_index in range(customer_count):
            for punctual in (True, False):
                for tip_roll in [index / 40 for index in range(40)]:
                    data = _hired()
                    data, ok, _info = apply_gnome_restaurant_command_pure(
                        data,
                        "accept_order",
                        {"difficulty": "hard"},
                        _rng([customer_index / customer_count]),
                    )
                    self.assertTrue(ok)
                    if not punctual:
                        # Two Again answers spend the whole eleven-minute window,
                        # which is what pushes the tip out of the good group.
                        for _beat in range(2):
                            data, ok, _result = apply_gnome_restaurant_review_pure(
                                data, _rng([0.0]), productive=False
                            )
                            self.assertTrue(ok)
                    data = _deliverable(data)
                    customer = str(data["gnome_restaurant"]["order"]["customer"])
                    _updated, ok, result = apply_gnome_restaurant_review_pure(
                        data, _rng([0.5, tip_roll, tip_roll, 0.0])
                    )
                    self.assertTrue(ok, result)
                    self.assertEqual(result["good_tip"], punctual)
                    seen.setdefault(result["tip_id"], set()).add(customer)
        self.assertEqual(set(seen), {row.id for row in GNOME_RESTAURANT_TIPS})
        # The customer-locked rows only ever come from the gnomes the source names.
        self.assertEqual(seen["gnome_scarf"], {"captain_ninto", "captain_daerkin"})
        self.assertEqual(seen["snake_charm"], {"wingstone"})
        self.assertEqual(seen["raw_oomlie"], {"penwie"})
        self.assertEqual(seen["gold_ore"], {"professor_manglethorp"})
        self.assertEqual(
            seen["pure_essence"], {"professor_imblewyn", "professor_onglewip"}
        )

    def test_first_reward_threshold_grants_only_the_token(self):
        data = _on_job("hard")
        data["gnome_restaurant"]["points"] = 9
        data = _deliverable(data)
        data, ok, result = apply_gnome_restaurant_review_pure(data, _rng([0.5]))
        self.assertTrue(ok, result)
        self.assertEqual(data["gnome_restaurant"]["points"], 12)
        self.assertTrue(result["token_granted"])
        self.assertEqual(data["inventory"][GNOME_RESTAURANT_TOKEN_ITEM], 1)
        self.assertEqual(data["gnome_restaurant"]["token_meals"], 0)

        data["gnome_restaurant"]["points"] = 21
        data = _deliverable(data)
        data, ok, result = apply_gnome_restaurant_review_pure(data, _rng([0.5]))
        self.assertTrue(ok, result)
        self.assertEqual(data["gnome_restaurant"]["points"], 24)
        self.assertFalse(result["token_granted"])
        self.assertEqual(data["gnome_restaurant"]["token_meals"], 1)

    def test_twelve_points_pay_a_token_and_each_twelve_more_bank_a_meal(self):
        data = _on_job("hard")
        granted_at = 0
        for delivery in range(1, 45):
            data = _deliverable(data)
            data, ok, result = apply_gnome_restaurant_review_pure(data, _rng([0.5]))
            self.assertTrue(ok, result)
            if result["token_granted"]:
                granted_at = delivery
        state = data["gnome_restaurant"]
        self.assertEqual(granted_at, 4)  # 4 hard deliveries = 12 points
        self.assertEqual(data["inventory"][GNOME_RESTAURANT_TOKEN_ITEM], 1)
        self.assertEqual(state["token_meals"], GNOME_RESTAURANT_TOKEN_MEAL_CAP)
        self.assertGreaterEqual(state["points"], GNOME_RESTAURANT_TOKEN_POINTS * 10)

        activated, ok, result = apply_gnome_restaurant_command_pure(
            data, "activate_token", {}, _rng([0.05])
        )
        self.assertTrue(ok, result)
        self.assertEqual(sum(result["delivered"].values()), 10)
        self.assertEqual(activated["gnome_restaurant"]["token_meals"], 0)
        for item in result["delivered"]:
            self.assertIn(item, GNOME_DISH_ITEMS + GNOME_COCKTAIL_ITEMS)

        # A lost token is replaced free and keeps the meals it had banked.
        lost = copy.deepcopy(data)
        lost["inventory"].pop(GNOME_RESTAURANT_TOKEN_ITEM)
        view = gnome_restaurant_view_pure(lost)
        self.assertTrue(view["token_reclaim_enabled"])
        replaced, ok, result = apply_gnome_restaurant_command_pure(lost, "reclaim_token")
        self.assertTrue(ok, result)
        self.assertEqual(replaced["inventory"][GNOME_RESTAURANT_TOKEN_ITEM], 1)
        self.assertEqual(
            replaced["gnome_restaurant"]["token_meals"], GNOME_RESTAURANT_TOKEN_MEAL_CAP
        )

    def test_token_cannot_be_activated_without_the_token_or_a_banked_meal(self):
        data = _on_job("easy")
        _updated, ok, info = apply_gnome_restaurant_command_pure(
            data, "activate_token", {}, _rng([0.0])
        )
        self.assertFalse(ok)
        self.assertIn("Reclaim the Reward token", info["reason"])
        data["inventory"][GNOME_RESTAURANT_TOKEN_ITEM] = 1
        _updated, ok, info = apply_gnome_restaurant_command_pure(
            data, "activate_token", {}, _rng([0.0])
        )
        self.assertFalse(ok)
        self.assertIn("no meals", info["reason"])


class GnomeRestaurantPersistenceRuntimeTests(unittest.TestCase):
    def test_migration_adds_the_ledger_and_repairs_a_corrupt_order(self):
        legacy = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        legacy.pop("gnome_restaurant")
        legacy["config_version"] = CURRENT_CONFIG_VERSION - 1
        migrated = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(
            migrated["gnome_restaurant"], default_gnome_restaurant_state_pure()
        )

        corrupt = sanitize_gnome_restaurant_state_pure(
            {
                "points": -5,
                "token_meals": 99,
                "difficulty_policy": "impossible",
                "order": {"difficulty": "easy", "customer": "garkor", "item": "Shark"},
            }
        )
        self.assertEqual(corrupt["points"], 0)
        self.assertEqual(corrupt["token_meals"], GNOME_RESTAURANT_TOKEN_MEAL_CAP)
        self.assertEqual(corrupt["difficulty_policy"], "easy")
        self.assertEqual(corrupt["order"], {})

    def test_an_outstanding_order_owns_the_activity_session_after_a_reload(self):
        data = _on_job("hard")
        self.assertEqual(
            data["activity_session"]["active_id"], GNOME_RESTAURANT_ACTIVITY_ID
        )
        reloaded = migrate_loaded_data(
            copy.deepcopy(data), ORE_DATA, ITEM_DEFINITIONS
        )
        self.assertTrue(reloaded["gnome_restaurant"]["order"])

        stolen = copy.deepcopy(data)
        stolen["activity_session"] = {"active_id": "temple_trekking"}
        repaired = migrate_loaded_data(stolen, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(repaired["gnome_restaurant"]["order"], {})

    def test_real_runtime_dispatch_delivers_and_persists(self):
        player = _deliverable(_on_job("easy"))
        calls = {"saves": 0, "messages": [], "errors": []}
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda title, message: calls["errors"].append(
                (title, message)
            ),
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
        self.assertEqual(player["gnome_restaurant"]["points"], 1)
        self.assertIn("Delivered", calls["messages"][0])
        telemetry = player["action_telemetry"]["actions"][
            f"utility:{GNOME_RESTAURANT_ACTIVITY_ID}"
        ]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertTrue(telemetry["outputs"])


try:
    from aqt.qt import QApplication, QColor, QPalette
    from ankiscape.ui.gnome_restaurant_panel import GnomeRestaurantPanel, HAS_QT
except Exception:
    QApplication = None
    HAS_QT = False
    GnomeRestaurantPanel = None


@unittest.skipUnless(HAS_QT, "Qt lane only")
class GnomeRestaurantQtPanelTests(unittest.TestCase):
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
        player = _deliverable(_on_job("hard"))
        panel = GnomeRestaurantPanel(
            player,
            on_command=lambda *_args: {"ok": True},
            on_select=lambda _activity: True,
        )
        panel.show()
        panel.resize(760, 560)
        for _ in range(4):
            QApplication.processEvents()
        view = gnome_restaurant_view_pure(player)
        self.assertLessEqual(panel.sizeHint().height(), 560)
        self.assertLessEqual(panel.layout().minimumSize().height(), 560)
        self.assertEqual(panel.primary_button.isEnabled(), view["primary_enabled"])
        self.assertEqual(panel.decline_button.isEnabled(), view["decline_enabled"])
        self.assertEqual(panel.leave_button.isVisible(), view["leave_visible"])
        self.assertEqual(panel.token_button.isEnabled(), view["token_activate_enabled"])
        self.assertEqual(
            panel.reclaim_button.isVisible(), view["token_reclaim_enabled"]
        )
        self.assertEqual(
            panel.difficulty_combo.isEnabled(), view["policy_controls_enabled"]
        )
        self.assertTrue(panel.window_bar.isVisible())
        self.assertEqual(panel.window_bar.value(), view["order_minutes_left"])
        self.assertEqual(panel.status_chip.text(), "ON A JOB")
        panel.close()

    def test_the_locked_gate_renders_the_view_reason_without_deriving_it(self):
        panel = GnomeRestaurantPanel(
            _player(trained=False), on_command=lambda *_args: {"ok": True}
        )
        panel.show()
        for _ in range(4):
            QApplication.processEvents()
        self.assertTrue(panel.requirements.isVisible())
        self.assertIn("gnome dishes", panel.requirements.text())
        self.assertFalse(panel.window_bar.isVisible())
        self.assertEqual(panel.status_chip.text(), "CLOSED")
        panel.close()

    def test_a_missing_dish_blocks_reviews_and_says_so(self):
        panel = GnomeRestaurantPanel(
            _on_job("easy"), on_command=lambda *_args: {"ok": True}
        )
        panel.show()
        for _ in range(4):
            QApplication.processEvents()
        self.assertTrue(panel.requirements.isVisible())
        self.assertIn("Cook or bank", panel.requirements.text())
        panel.close()


if __name__ == "__main__":
    unittest.main()
