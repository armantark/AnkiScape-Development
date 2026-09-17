from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    EXTRA_ITEM_IMAGES,
    FLETCHING_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.data.ranging_guild_data import (
    RANGING_GUILD_ACTIVITY_ID,
    RANGING_GUILD_BANDS,
    RANGING_GUILD_REWARDS,
    RANGING_GUILD_TICKET_ITEM,
)
from ankiscape.logic.grand_exchange_logic import (
    advance_ge_market_tick_pure,
    collect_ge_offer_pure,
    place_ge_offer_pure,
)
from ankiscape.logic.ranging_guild_logic import (
    apply_ranging_guild_review_pure,
    claim_ranging_guild_tickets_pure,
    enter_ranging_guild_pure,
    purchase_ranging_guild_reward_pure,
    ranging_guild_outcome_pure,
    sanitize_ranging_guild_state_pure,
)
from ankiscape.logic.achievement_diary_logic import refresh_achievement_diaries_pure
from ankiscape.logic.cadence_coverage import (
    SINGLE_TICK_UTILITY_IDS,
    cadence_coverage_rows_pure,
)
from ankiscape.logic.review_strip_logic import activity_trained_skills_pure
from ankiscape.logic_pure.logic_pure import apply_fletching_pure
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


ROOT = Path(__file__).resolve().parents[1]


def _player(*, ranged_level: int = 40, coins: int = 200):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["ranged_level"] = ranged_level
    data["ranged_exp"] = 0.0
    data["inventory"]["Coins"] = coins
    data["inventory"]["Bronze arrows"] = 0
    data["equipment"] = {
        "weapon": "Shortbow",
        "ammunition": "Bronze arrows",
    }
    return data


def _entered():
    data, ok, info = enter_ranging_guild_pure(_player())
    if not ok:
        raise AssertionError(info)
    return data


def _context(player_data, calls, rolls):
    values = iter(rolls)
    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: next(values),
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda _reason=None: calls.__setitem__("deactivated", True),
        award_skill_exp=lambda _key, amount: amount,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda *_args: None,
        check_achievements=lambda *_args: None,
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: None,
        show_exp=lambda amount: calls["xp"].append(float(amount)),
        show_activity_gain=lambda message: calls["activity"].append(str(message)),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda *_args: None,
    )


class RangingGuildDataAndAssetTests(unittest.TestCase):
    def test_period_bands_and_six_exchange_rows_are_exact(self):
        self.assertEqual(
            [(row.id, row.score, row.ranged_xp) for row in RANGING_GUILD_BANDS],
            [
                ("miss", 0, 0.0),
                ("black", 10, 5.0),
                ("blue", 20, 10.0),
                ("red", 30, 15.0),
                ("yellow", 50, 25.0),
                ("bullseye", 100, 50.0),
            ],
        )
        self.assertEqual(
            [(row.item_name, row.quantity, row.ticket_cost) for row in RANGING_GUILD_REWARDS],
            [
                ("Barb bolttips", 30, 114),
                ("Studded body", 1, 51),
                ("Rune arrows", 50, 1020),
                ("Coif", 1, 12),
                ("Green d'hide body", 1, 856),
                ("Adamant javelin", 20, 292),
            ],
        )

    def test_activity_and_ticket_are_registered_with_normalized_art(self):
        activity = UTILITY_ACTIVITY_DATA[RANGING_GUILD_ACTIVITY_ID]
        self.assertEqual(activity["surface"], "activities")
        icon = Path(str(activity["icon_path"]))
        self.assertTrue(icon.is_file())
        self.assertEqual(EXTRA_ITEM_IMAGES[RANGING_GUILD_TICKET_ITEM], str(icon))
        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        ticket = definitions[RANGING_GUILD_TICKET_ITEM]
        self.assertEqual(ticket.source_item_id, 1464)
        self.assertTrue(ticket.stackable)
        self.assertTrue(ticket.tradeable)
        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        self.assertLessEqual(
            int(provenance["activityicons/ranging_guild.png"]["size"]),
            64 * 64 * 4,
        )

    def test_one_review_is_one_shot_and_the_review_strip_trains_ranged(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == RANGING_GUILD_ACTIVITY_ID
        )
        self.assertEqual(row["mode"], "activity_group")
        self.assertIn("Never foreground-multiplied", row["multiplier_behavior"])
        self.assertIn(RANGING_GUILD_ACTIVITY_ID, SINGLE_TICK_UTILITY_IDS)
        self.assertEqual(
            activity_trained_skills_pure({}, RANGING_GUILD_ACTIVITY_ID),
            ("Ranged",),
        )


class RangingGuildPureMechanicsTests(unittest.TestCase):
    def test_entry_is_atomic_and_accepts_a_temporary_ranged_boost(self):
        low = _player(ranged_level=39)
        unchanged, ok, info = enter_ranging_guild_pure(low)
        self.assertFalse(ok, info)
        self.assertEqual(unchanged, low)
        low["combat_current_levels"] = {"ranged": 40}
        entered, ok, info = enter_ranging_guild_pure(low)
        self.assertTrue(ok, info)
        self.assertEqual(entered["inventory"]["Coins"], 0)
        self.assertEqual(entered["inventory"]["Bronze arrows"], 10)
        self.assertEqual(entered["activity_session"]["active_id"], RANGING_GUILD_ACTIVITY_ID)

    def test_entry_requires_a_bronze_capable_bow_and_equipped_ammo(self):
        data = _player()
        data["equipment"] = {"weapon": "Bronze sword"}
        unchanged, ok, info = enter_ranging_guild_pure(data)
        self.assertFalse(ok)
        self.assertIn("bow", info["reason"])
        self.assertEqual(unchanged["inventory"]["Coins"], 200)

    def test_source_blocked_resolver_has_stable_boundaries_and_accurate_bonus(self):
        data = _player(ranged_level=40)
        data["combat_attack_style"] = "ranged_rapid"
        self.assertEqual(ranging_guild_outcome_pure(data, 0.125)[0], "miss")
        data["combat_attack_style"] = "ranged_accurate"
        self.assertEqual(ranging_guild_outcome_pure(data, 0.125)[0], "black")
        self.assertEqual(ranging_guild_outcome_pure(data, 0.999999)[0], "bullseye")

    def test_each_review_consumes_one_arrow_and_tenth_waits_for_one_claim(self):
        data = _entered()
        results = []
        for _ in range(10):
            data, ok, result = apply_ranging_guild_review_pure(data, lambda: 0.999999)
            self.assertTrue(ok, result)
            results.append(result)
        self.assertEqual(data["inventory"]["Bronze arrows"], 0)
        self.assertEqual(data["ranging_guild"]["score"], 1_000)
        self.assertTrue(data["ranging_guild"]["pending_claim"])
        self.assertEqual(data["activity_session"]["active_id"], "")
        self.assertFalse(results[-2]["terminal"])
        self.assertTrue(results[-1]["terminal"])
        claimed, ok, result = claim_ranging_guild_tickets_pure(data)
        self.assertTrue(ok, result)
        self.assertEqual(claimed["inventory"][RANGING_GUILD_TICKET_ITEM], 100)
        replayed, ok, _ = claim_ranging_guild_tickets_pure(claimed)
        self.assertFalse(ok)
        self.assertEqual(replayed, claimed)

    def test_earned_tickets_can_be_traded_and_spent_on_guild_rewards(self):
        ticket_name = RANGING_GUILD_TICKET_ITEM
        item_spec = GE_ITEM_CATALOG[ticket_name]
        self.assertEqual(item_spec["source_item_id"], 1464)
        self.assertEqual(item_spec["buy_limit"], 5_000)
        self.assertEqual(item_spec["guide_price"], 25)
        self.assertEqual(item_spec["guide_price_source"], "cache_value_fallback")

        data, ok, result = enter_ranging_guild_pure(_player(coins=1_000))
        self.assertTrue(ok, result)
        for _ in range(10):
            data, ok, result = apply_ranging_guild_review_pure(data, lambda: 0.999999)
            self.assertTrue(ok, result)
        data, ok, result = claim_ranging_guild_tickets_pure(data)
        self.assertTrue(ok, result)
        self.assertEqual(data["inventory"][ticket_name], 100)

        for side, ticket_balance in (("sell", 99), ("buy", 100)):
            with self.subTest(side=side):
                data, result = place_ge_offer_pure(
                    data,
                    side=side,
                    item_name=ticket_name,
                    quantity=1,
                    unit_price=25,
                    item_spec=item_spec,
                    confirmed=True,
                )
                self.assertTrue(result["ok"], result)
                order_id = result["order"]["id"]
                clock = data["shop_market_clock"]
                clock["market_tick"] += 1
                clock["answered_cards"] += 1
                data, result = advance_ge_market_tick_pure(
                    data,
                    item_catalog=GE_ITEM_CATALOG,
                    random_draw=lambda: 0.0,
                )
                self.assertEqual(len(result["fills"]), 1, result)
                coins_before_collection = data["inventory"]["Coins"]
                data, result = collect_ge_offer_pure(data, order_id)
                self.assertTrue(result["ok"], result)
                self.assertGreaterEqual(result["coins"], 1 if side == "sell" else 0)
                self.assertEqual(data["inventory"]["Coins"], coins_before_collection + result["coins"])
                self.assertEqual(result["items"], 1 if side == "buy" else 0)
                self.assertEqual(data["inventory"][ticket_name], ticket_balance)
                self.assertEqual(data["ge_player_orders"], [])

        previous_coifs = data["inventory"].get("Coif", 0)
        data, ok, result = purchase_ranging_guild_reward_pure(data, "coif")
        self.assertTrue(ok, result)
        self.assertEqual(data["inventory"][ticket_name], 88)
        self.assertEqual(data["inventory"]["Coif"], previous_coifs + 1)

    def test_hati_paws_double_only_exact_activity_ranged_xp(self):
        data = _entered()
        data["equipment"]["hands"] = "Hati paws"
        advanced, ok, result = apply_ranging_guild_review_pure(data, lambda: 0.999999)
        self.assertTrue(ok, result)
        self.assertEqual(result["ranged_xp"], 100.0)
        self.assertTrue(result["hati_paws_doubled"])
        self.assertEqual(advanced.get("constitution_exp", 0), data.get("constitution_exp", 0))

    def test_again_does_not_consume_or_advance(self):
        data = _entered()
        unchanged, ok, result = apply_ranging_guild_review_pure(data, productive=False)
        self.assertTrue(ok, result)
        self.assertFalse(result["advanced"])
        self.assertEqual(unchanged, data)

    def test_every_reward_purchase_is_atomic(self):
        for reward in RANGING_GUILD_REWARDS:
            with self.subTest(reward=reward.id):
                data = _player()
                data["inventory"][RANGING_GUILD_TICKET_ITEM] = reward.ticket_cost
                bought, ok, info = purchase_ranging_guild_reward_pure(data, reward.id)
                self.assertTrue(ok, info)
                self.assertEqual(bought["inventory"][RANGING_GUILD_TICKET_ITEM], 0)
                self.assertEqual(bought["inventory"][reward.item_name], reward.quantity)
                blocked = _player()
                before = copy.deepcopy(blocked)
                blocked, ok, _ = purchase_ranging_guild_reward_pure(blocked, reward.id)
                self.assertFalse(ok)
                self.assertEqual(blocked, before)

    def test_barb_bolttip_reward_reaches_existing_fletching_mechanic(self):
        data = _player()
        data["inventory"].update(
            {RANGING_GUILD_TICKET_ITEM: 114, "Bronze bolts": 10}
        )
        data, ok, info = purchase_ranging_guild_reward_pure(data, "barb_bolttips")
        self.assertTrue(ok, info)
        inventory, xp, produced = apply_fletching_pure(
            "tip_barbed_bolts", data["inventory"], FLETCHING_DATA
        )
        self.assertEqual((xp, produced), (95.0, True))
        self.assertEqual(inventory["Barbed bolts"], 10)
        self.assertEqual(inventory["Barb bolttips"], 20)

    def test_ranging_guild_diary_tasks_follow_tickets_and_exchange_not_level(self):
        data = _player()
        refreshed, newly = refresh_achievement_diaries_pure(data)
        self.assertNotIn("seers_medium_arch_archer", newly)
        self.assertNotIn("seers_medium_what_no_cuddly_toy", newly)
        refreshed["inventory"][RANGING_GUILD_TICKET_ITEM] = 1_001
        refreshed, newly = refresh_achievement_diaries_pure(refreshed)
        self.assertIn("seers_medium_arch_archer", newly)
        refreshed, ok, info = purchase_ranging_guild_reward_pure(refreshed, "coif")
        self.assertTrue(ok, info)
        refreshed, newly = refresh_achievement_diaries_pure(refreshed)
        self.assertIn("seers_medium_what_no_cuddly_toy", newly)

    def test_migration_preserves_active_and_pending_sessions(self):
        active = _player()
        active["ranging_guild"] = {
            "active": True,
            "shots_fired": 4,
            "score": 170,
            "competitions_started": 1,
        }
        active["activity_session"] = {"active_id": RANGING_GUILD_ACTIVITY_ID}
        migrated = migrate_loaded_data(active, ORE_DATA, ITEM_DEFINITIONS)
        self.assertTrue(migrated["ranging_guild"]["active"])
        self.assertEqual(migrated["ranging_guild"]["shots_fired"], 4)
        self.assertEqual(migrated["activity_session"]["active_id"], RANGING_GUILD_ACTIVITY_ID)
        pending = sanitize_ranging_guild_state_pure(
            {"active": True, "pending_claim": True, "score": 550}
        )
        self.assertFalse(pending["active"])
        self.assertEqual(pending["shots_fired"], 10)
        self.assertEqual(pending["score"], 550)


class RangingGuildRuntimeTests(unittest.TestCase):
    def test_runtime_dispatches_ten_shots_updates_xp_and_deactivates(self):
        player = _entered()
        player["current_utility"] = RANGING_GUILD_ACTIVITY_ID
        calls = {"errors": [], "saves": 0, "xp": [], "activity": [], "deactivated": False}
        ctx = _context(player, calls, (0.999999,) * 10)
        for _ in range(10):
            self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 10)
        self.assertEqual(sum(calls["xp"]), 500.0)
        self.assertEqual(player["ranged_exp"], 500.0)
        self.assertTrue(calls["deactivated"])
        self.assertTrue(player["ranging_guild"]["pending_claim"])
        telemetry = player["action_telemetry"]["actions"]["utility:ranging_guild"]
        self.assertEqual(telemetry["attempts"], 10)


try:
    from aqt.qt import QApplication, QComboBox
    from ankiscape.ui.ranging_guild_panel import HAS_QT, RangingGuildPanel
except Exception:
    QApplication = None
    QComboBox = None
    HAS_QT = False
    RangingGuildPanel = None


@unittest.skipUnless(HAS_QT, "Qt lane only")
class RangingGuildQtPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_panel_is_compact_and_exposes_live_entry_claim_and_shop_states(self):
        data = _player()
        calls = []

        def command(action_id, payload):
            calls.append((action_id, dict(payload)))
            if action_id == "enter":
                updated, ok, info = enter_ranging_guild_pure(data)
            elif action_id == "claim":
                updated, ok, info = claim_ranging_guild_tickets_pure(data)
            else:
                updated, ok, info = purchase_ranging_guild_reward_pure(
                    data, str(payload.get("reward_id", ""))
                )
            if ok:
                data.clear()
                data.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        panel = RangingGuildPanel(data, on_command=command)
        panel.show()
        panel.resize(760, 560)
        for _ in range(4):
            QApplication.processEvents()
        self.assertLessEqual(panel.sizeHint().height(), 560)
        self.assertEqual(panel.primary_button.text(), "Enter competition")
        combo = panel.findChild(QComboBox, "rangingGuildRewardCombo")
        self.assertFalse(combo.itemIcon(0).isNull())
        panel.primary_button.click()
        QApplication.processEvents()
        self.assertEqual(calls[-1][0], "enter")
        self.assertEqual(panel.primary_button.text(), "Select for reviews")
        data["ranging_guild"].update(
            {"active": False, "pending_claim": True, "shots_fired": 10, "score": 550}
        )
        data["activity_session"] = {"active_id": ""}
        panel.refresh()
        self.assertEqual(panel.primary_button.text(), "Claim 55 tickets")
        panel.primary_button.click()
        QApplication.processEvents()
        self.assertEqual(data["inventory"][RANGING_GUILD_TICKET_ITEM], 55)
        self.assertEqual(panel.ticket_wallet.text(), "Archery tickets: 55")
        panel.close()


if __name__ == "__main__":
    unittest.main()
