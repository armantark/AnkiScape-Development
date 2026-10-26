from tests.test_integration_smoke import _DummyCol, _DummyMW, _FakeReviewer, _load_addon_as_package
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_hud_badges_have_no_qt_placeholders_with_matching_signatures(self):
        # This suite loads the add-on without aqt.qt, so ui.py takes its
        # HAS_QT-false branch. A new Qt widget class without a placeholder
        # breaks the import outright rather than failing an assertion.
        addon = _load_addon_as_package("ankiscape_no_qt_placeholders")
        ui = addon.ui

        self.assertFalse(ui.HAS_QT)
        for name in (
            "ReviewStatusBadge",
            "ReviewFillDrawer",
            "ReviewEventLogDrawer",
            "ReviewBankRunButton",
        ):
            placeholder = getattr(ui, name)
            self.assertTrue(hasattr(placeholder(None), "set_data"), name)

        # The update helpers must stay callable and inert without Qt.
        self.assertIsNone(
            ui.update_review_status_badge({}, lambda _id=None: None, lambda _id=None: None)
        )
        self.assertIsNone(ui.update_review_fill_drawer({}))
        self.assertIsNone(ui.update_review_event_log_drawer({}))
        self.assertIsNone(ui.update_review_bank_run_button({}, "mining"))
        self.assertIsNone(ui.hide_review_status_badge())
        self.assertIsNone(ui.hide_review_fill_drawer())
        self.assertIsNone(ui.hide_review_event_log_drawer())
        self.assertIsNone(ui._DND_BADGE)
        self.assertIsNone(ui._FARMING_BADGE)
        self.assertIsNone(ui._FILL_DRAWER)
        self.assertIsNone(ui._EVENT_LOG_DRAWER)

    def test_hook_flow_and_settings_gating(self):
        addon = _load_addon_as_package()

        # Replace UI/HUD side effects with counters
        calls = {"ensure": 0, "update": 0, "hide": 0, "xp": 0}
        def fake_ensure():
            calls["ensure"] += 1
        def fake_update(_pd=None, _skill=None):
            calls["update"] += 1
        def fake_hide():
            calls["hide"] += 1
        class FakeExpPopup:
            def __init__(self, _mw):
                pass
            def show_exp(self, _n):
                calls["xp"] += 1

        # Patch directly on loaded module (these names are referenced inside __init__.py)
        addon.ensure_review_hud = fake_ensure
        addon.update_review_hud = fake_update
        addon.hide_review_hud = fake_hide
        addon.ExpPopup = FakeExpPopup

        # Provide a dummy mw with default settings ON
        col = _DummyCol(
            {
                "ankiscape_review_hud_enabled": True,
                "ankiscape_floating_xp_enabled": True,
                "ankiscape_popups_enabled": True,
                "ankiscape_floating_enabled": True,
                "ankiscape_floating_position": "right",
            }
        )
        addon.mw = _DummyMW(col)
        # Ensure ui.get_config_bool reads the same mw/col
        try:
            addon.ui.mw = addon.mw  # type: ignore[attr-defined]
        except Exception:
            pass

        # Minimal player state to avoid None paths
        addon._state.player_data = {
            "inventory": {},
            "mining_level": 1,
            "woodcutting_level": 1,
            "smithing_level": 1,
            "crafting_level": 1,
            "fletching_level": 1,
            "mining_exp": 0,
            "woodcutting_exp": 0,
            "smithing_exp": 0,
            "crafting_exp": 0,
            "fletching_exp": 0,
            "current_ore": "Rune essence",
            "current_tree": "",
            "current_smith": "smelt_bronze_bar",
            "current_craft": "",
            "current_fletch": "arrow_shafts",
        }
        addon._state.current_skill = "Mining"

        calls["good_answer"] = 0
        def fake_good_answer(*_args, **_kwargs):
            calls["good_answer"] += 1
        addon.on_good_answer = fake_good_answer

        addon._state.current_skill = "Thieving"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        result = addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(result, "answered")
        self.assertEqual(calls["good_answer"], 1)

        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(calls["good_answer"], 2)

        # Each question/answer surface event refreshes the HUD exactly once.
        before_ensure = calls["ensure"]
        before_update = calls["update"]
        addon._on_rev_show_question()
        addon._on_rev_show_answer()
        self.assertEqual(calls["ensure"] - before_ensure, 2)
        self.assertEqual(calls["update"] - before_update, 2)

        # Floating XP ON => popup shows once
        addon._show_exp(10)
        self.assertEqual(calls["xp"], 1)

        # Disable Experience HUD: subsequent events should not update HUD
        prev_ensure, prev_update = calls["ensure"], calls["update"]
        addon.mw.col.set_config("ankiscape_review_hud_enabled", False)
        addon._on_rev_show_question()
        addon._on_rev_show_answer()
        self.assertEqual(calls["ensure"], prev_ensure)
        self.assertEqual(calls["update"], prev_update)

        # Disable Floating XP: no additional popup
        addon.mw.col.set_config("ankiscape_floating_xp_enabled", False)
        addon._show_exp(5)
        self.assertEqual(calls["xp"], 1)

        # Navigating away hides HUD regardless of setting
        addon._on_overview_did_refresh(overview=None)
        self.assertGreaterEqual(calls["hide"], 1)
