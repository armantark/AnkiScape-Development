import copy
import random
import sys
import types
import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic import grand_exchange_logic as ge
from tests.test_integration_smoke import (
    _DummyCol, _DummyMW, _FakeReviewer, _install_runtime_fakes, _load_addon_as_package,
)
from tests.grand_exchange.test_sell_demand import SPEC, player, place, tick, pool


class DemandReviewTests(unittest.TestCase):
    def setUp(self):
        self.original_modules = dict(sys.modules)
        self.python_rng = random.getstate()

    def tearDown(self):
        random.setstate(self.python_rng)
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def _answer(self, addon):
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

    def _assert_replay(self, *, recovering):
        _install_runtime_fakes()
        addon = _load_addon_as_package("ankiscape_demand_review_" + str(recovering))
        addon.mw = _DummyMW(_DummyCol())
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _exp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        logic = sys.modules[f"{addon.__name__}.logic.grand_exchange_logic"]
        initial = place(player(), 1000)
        start = 31 if recovering else 7
        initial["shop_market_clock"] = {"answered_cards": 7, "market_tick": start}
        initial["world_clock"] = {"day": 0, "day_start_card": 0, "day_length": 240,
                                  "in_day_ticks": (start + 1) * 600 - 6}
        initial["completed_achievements"] = []
        initial["ge_market_state"]["last_processed_tick"] = start
        initial["ge_market_state"]["items"]["Logs"] = {
            "anchor_price": 100, "guide_price": 100, "last_processed_tick": start,
            "shock_cooldown_until_tick": 1000,
            "sell_demand": {"capacity": 10, "credit": 0 if recovering else 2390,
                            "last_tick": 8 if recovering else 7},
        }
        # Persisted market RNG, with no injected draws, must replay its cursor.
        addon.advance_ge_market_tick_pure = lambda data, **_kwargs: logic.advance_ge_market_tick_pure(
            data, item_catalog={"Logs": SPEC})
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        python_before = random.getstate()
        self._answer(addon)
        first = copy.deepcopy(addon._state.player_data)
        rng_after = random.getstate()
        self.assertEqual(first["shop_market_clock"]["market_tick"], start + 1)
        order = first["ge_player_orders"][0]
        self.assertEqual(order["completed_quantity"], 1 if recovering else 10)
        self.assertEqual(order["escrow_items"], 999 if recovering else 990)
        self.assertEqual(pool(first)["credit"], 0)
        self.assertEqual(pool(first)["last_tick"], start + 1)
        self.assertEqual(len(first["ge_fill_log"]), 1)
        self.assertGreater(first["ge_market_state"]["rng_cursor"], 0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(random.getstate(), python_before)
        self.assertEqual(addon._state.review_undo_stack, [])
        self._answer(addon)
        self.assertEqual(addon._state.player_data, first)
        self.assertEqual(random.getstate(), rng_after)

    def test_sell_exhaustion_undo_reanswer_restores_complete_transaction(self):
        self._assert_replay(recovering=False)

    def test_sell_recovery_undo_reanswer_restores_complete_transaction(self):
        self._assert_replay(recovering=True)

    def test_patient_recovery_sale_retains_price_edge(self):
        data = player()
        data["ge_market_state"]["last_processed_tick"] = 19
        data["shop_market_clock"]["market_tick"] = 19
        data["ge_market_state"]["items"]["Logs"] = {
            "anchor_price": 100, "guide_price": 100, "last_processed_tick": 19,
            "shock_start_tick": 0, "shock_end_tick": 40, "shock_peak_bps": -4000,
            "sell_demand": {"capacity": 10, "credit": 2400, "last_tick": 19},
        }
        # Controlled negative shock is independent of the ±1,500 bps player cap.
        data = place(place(data, 1, side="buy"), 1, side="sell")
        data, probe = tick(data, 20, draw=lambda: 0.0)
        buy, sell = probe["fills"]
        self.assertLess(data["ge_market_state"]["items"]["Logs"]["current_shock_bps"], -1500)
        self.assertGreater(buy["price_improvement"], 0)
        self.assertGreater(sell["price_improvement"], 0)
        data, _ = ge.collect_all_ge_offers_pure(data)
        data = place(data, 9, side="buy")
        data, accumulated = tick(data, 21, draw=iter((.5, .5, 0, .999, 0)).__next__)
        self.assertEqual(sum(fill["quantity"] for fill in accumulated["fills"]), 9)
        self.assertLessEqual(data["ge_buy_limit_usage"]["Logs"]["bought"], SPEC["buy_limit"])
        data, _ = ge.collect_all_ge_offers_pure(data)
        # Same nine units and starting save; compare immediate sale to patient holding.
        offered = place(data, 9)
        immediate, now = tick(offered, 22, draw=iter((.5, .5, 0, .999, 0)).__next__)
        # No offers during recovery, so demand/price remain lazy until relevant.
        held, _ = tick(data, 260, draw=lambda: .5)
        held = place(held, 9)
        patient, later = tick(held, 261, draw=iter((.5, .5, 0, .999, 0)).__next__)
        self.assertEqual(sum(fill["quantity"] for fill in now["fills"]), 9)
        self.assertEqual(sum(fill["quantity"] for fill in later["fills"]), 9)
        self.assertGreater(later["fills"][0]["unit_price"], now["fills"][0]["unit_price"])
        self.assertGreater(later["fills"][0]["price_improvement"], 0)
        self.assertGreater(sum(fill["quantity"] * fill["unit_price"] for fill in later["fills"]),
                           sum(fill["quantity"] * fill["unit_price"] for fill in now["fills"]))
        self.assertEqual(patient["inventory"]["Logs"], immediate["inventory"]["Logs"])
        # This chosen shock/recovery path demonstrates an edge, not a random-market profit target.
