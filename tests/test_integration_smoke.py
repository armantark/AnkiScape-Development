import copy
import dataclasses
import sys
import types
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path

# --- Minimal fakes for Anki runtime ---
class _FakeHooks:
    def __init__(self):
        # Lists emulate VS Code/Anki gui_hooks collections with append/remove
        self.overview_did_refresh = []
        self.overview_will_refresh = []
        self.reviewer_did_show_question = []
        self.reviewer_did_show_answer = []
        self.webview_did_receive_js_message = []
        self.state_did_undo = []

class _FakeReviewer:
    def _answerCard(self, ease):
        return None

class _DummyCol:
    def __init__(self, store=None):
        self._store = dict(store or {})
        self.custom_undo_entries = []
    def get_config(self, key, default=None):
        return self._store.get(key, default)
    def set_config(self, key, value):
        self._store[key] = value
    def add_custom_undo_entry(self, name):
        self.custom_undo_entries.append(name)
        return len(self.custom_undo_entries)

class _DummyMW:
    def __init__(self, col):
        self.col = col
        self.undo_updates = 0
    def update_undo_actions(self):
        self.undo_updates += 1


def _install_runtime_fakes():
    # aqt base module
    aqt = types.ModuleType("aqt")
    aqt.mw = None
    aqt.gui_hooks = _FakeHooks()

    # Give each package load a pristine reviewer class. Add-on wrapping mutates
    # the class method, so reusing _FakeReviewer would nest stale wrappers.
    class _RuntimeReviewer(_FakeReviewer):
        pass

    aqt_reviewer = types.ModuleType("aqt.reviewer")
    aqt_reviewer.Reviewer = _RuntimeReviewer

    # Shadow stale real-Qt imports without unloading their process-global types.
    sys.modules["aqt.qt"] = types.ModuleType("aqt.qt")
    sys.modules["aqt"] = aqt
    sys.modules["aqt.reviewer"] = aqt_reviewer

    # anki.hooks module
    anki_hooks = types.ModuleType("anki.hooks")
    def addHook(_name, _fn):
        # No-op for test; registration is validated by addon behavior below
        return None
    def wrap(old, new, _mode):
        def _wrapped(self, ease):
            return new(self, ease, old)
        return _wrapped
    anki_hooks.addHook = addHook
    anki_hooks.wrap = wrap
    sys.modules["anki.hooks"] = anki_hooks


def _load_addon_as_package(mod_name="ankiscape_integration"):
    # Load top-level __init__.py as a package so relative imports (e.g., .hooks) resolve
    root = Path(__file__).resolve().parents[1]
    init_py = root / "__init__.py"
    loader = SourceFileLoader(mod_name, str(init_py))
    spec = spec_from_loader(mod_name, loader, is_package=True)
    mod = module_from_spec(spec)
    # Package modules need a __path__ so relative imports work
    mod.__path__ = [str(root)]  # type: ignore[attr-defined]
    # Ensure the package is discoverable for relative imports during exec_module
    sys.modules[mod_name] = mod
    loader.exec_module(mod)
    return mod


def _install_quest_combat_mid_rolls(testcase, addon, repeats=2000):
    original_random = addon.random.random
    original_review_multiplier = addon._review_action_multiplier
    rolls = iter((0.5,) * repeats)
    addon.random.random = lambda: next(rolls, 1.0)
    addon._review_action_multiplier = lambda: 10
    testcase.addCleanup(setattr, addon.random, "random", original_random)
    testcase.addCleanup(setattr, addon, "_review_action_multiplier", original_review_multiplier)


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import QUEST_DATA
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest
class TestIntegrationSmoke(unittest.TestCase):
    def setUp(self):
        # Isolate sys.modules pollution between tests
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        # Restore sys.modules to avoid interference with other tests
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _runtime_context(self, addon, *, rolls=(), calls=None):
        from ankiscape.runtime.runtime_actions import RuntimeActionContext

        captured = calls if calls is not None else {"xp": [], "activity": []}
        random_rolls = iter(rolls)
        return RuntimeActionContext(
            player_data=addon._state.player_data,
            random_random=lambda: next(random_rolls, 0.0),
            show_error_message=lambda _title, message: self.fail(message),
            deactivate_current_skill=lambda _reason=None: None,
            award_skill_exp=lambda exp_key, amount: addon._state.player_data.__setitem__(
                exp_key, float(addon._state.player_data.get(exp_key, 0.0) or 0.0) + amount
            ) or amount,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: None,
            refresh_skill_availability=lambda: None,
            show_exp=lambda amount: captured["xp"].append(amount),
            show_activity_gain=lambda text: captured["activity"].append(text),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )

    def test_skill_availability_cache_reuses_results_until_a_real_dependency_changes(self):
        addon = _load_addon_as_package("ankiscape_availability_cache")
        addon._state.player_data = {
            "inventory": {},
            "smithing_level": 1,
            "crafting_level": 1,
            "fletching_level": 1,
            "firemaking_level": 1,
            "hunter_level": 1,
            "cooking_level": 1,
            "runecrafting_level": 1,
            "quests": {},
            "equipment": {},
            "wicked_hood": {},
        }
        refreshes = []
        addon.refresh_skill_availability = lambda *values: refreshes.append(values)
        addon._state.skill_availability_cache_fingerprint = None

        addon._refresh_skill_availability()
        addon._refresh_skill_availability()
        addon._state.player_data["inventory"]["Unrelated profile marker"] = 1
        addon._refresh_skill_availability()

        self.assertEqual(len(refreshes), 1)
        self.assertEqual(len(refreshes[0]), 7)

        addon._state.player_data["inventory"]["Copper ore"] = 1
        addon._refresh_skill_availability()
        self.assertEqual(len(refreshes), 2)

    def test_skill_availability_refresh_uses_boosted_crafting_rules(self):
        addon = _load_addon_as_package("ankiscape_boosted_crafting_availability")
        addon._state.player_data = {
            "inventory": {"Cracked cooking urn (unf)": 3},
            "smithing_level": 1,
            "crafting_level": 1,
            "fletching_level": 1,
            "firemaking_level": 1,
            "hunter_level": 1,
            "cooking_level": 1,
            "runecrafting_level": 1,
            "skilling_current_levels": {"crafting": 2},
            "quests": {},
            "equipment": {},
            "wicked_hood": {},
        }
        refreshes = []
        addon.refresh_skill_availability = lambda *values: refreshes.append(values)
        addon._state.skill_availability_cache_fingerprint = None

        addon._refresh_skill_availability()
        self.assertEqual(len(refreshes), 1)
        self.assertTrue(refreshes[0][1])

        addon._state.player_data["skilling_current_levels"]["crafting"] = 1
        addon._refresh_skill_availability()
        self.assertEqual(len(refreshes), 2)
        self.assertFalse(refreshes[1][1])

    def test_floating_xp_and_activity_results_share_the_event_log_seam(self):
        addon = _load_addon_as_package("ankiscape_event_log_emissions")
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": False}))
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Mining"
        addon._state.player_data = {
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        addon._show_exp(25)
        addon._show_activity_gain("+1 Iron ore")
        addon._show_activity_gain("Bank run — arrived and restocked")

        self.assertEqual(
            [row["kind"] for row in addon._state.player_data["review_event_log"]],
            ["xp", "activity", "activity"],
        )
        self.assertEqual(
            [row["text"] for row in addon._state.player_data["review_event_log"]],
            [
                "+25 XP · Mining",
                "+1 Iron ore",
                "Bank run — arrived and restocked",
            ],
        )

    def test_bankstanding_transition_logs_once_and_defers_the_reasoned_modal(self):
        addon = _load_addon_as_package("ankiscape_bankstanding_transition")
        addon.mw = _DummyMW(_DummyCol())
        addon.update_review_event_log_drawer = lambda _data: None
        addon.update_review_hud = lambda *_args: None
        addon.ui.update_menu_visibility = lambda *_args: None
        popups = []
        gains = []
        rewards = []
        scheduled = []
        sys.modules["aqt.qt"].QTimer = types.SimpleNamespace(
            singleShot=lambda _delay, callback: scheduled.append(callback)
        )
        addon.ui.show_bankstanding_dialog = popups.append
        addon._show_activity_gain = gains.append
        addon._claim_stronghold_reward = lambda: rewards.append("reward")
        addon._state.current_skill = "Utilities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.player_data = {
            "current_utility": "stronghold_of_security",
            "review_event_log": [],
        }
        reason = "Stronghold of Security cleared — claim your reward!"

        runtime_ctx = addon._runtime_action_context()
        runtime_ctx.show_activity_gain(reason)
        runtime_ctx.deactivate_current_skill()
        self.assertFalse(addon._switch_to_bankstanding("A duplicate reason."))

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)
        self.assertEqual(popups, [])
        self.assertEqual(gains, [reason])
        self.assertIn(
            reason,
            addon._state.player_data["review_event_log"][0]["text"],
        )

        addon._prompt_stronghold_reward()
        addon._state.card_turned = False
        addon._state.answer_shown = False
        addon._show_pending_bankstanding_dialog()
        addon._show_pending_review_dialogs()

        self.assertEqual(popups, [])
        self.assertEqual(rewards, [])
        self.assertEqual(len(scheduled), 2)
        scheduled[0]()
        self.assertEqual(popups, [reason])
        self.assertEqual(rewards, [])
        scheduled[1]()
        self.assertEqual(rewards, ["reward"])

    def test_bankstanding_reason_backpatch_updates_the_live_sanitized_log(self):
        from ankiscape.logic.review_strip_logic import sanitize_review_event_log_pure

        addon = _load_addon_as_package("ankiscape_bankstanding_reason_backpatch")
        addon.mw = _DummyMW(_DummyCol())
        addon.update_review_hud = lambda *_args: None
        addon.ui.update_menu_visibility = lambda *_args: None
        addon.show_error_message = lambda *_args: None
        addon._state.current_skill = "Crafting"
        addon._state.player_data = {
            "current_utility": "gather_wool",
            "review_event_log": [],
        }
        runtime_ctx = addon._runtime_action_context()

        runtime_ctx.switch_to_bankstanding()
        detached_entry = addon._state.player_data["review_event_log"][-1]
        addon._state.player_data["review_event_log"] = sanitize_review_event_log_pure(
            addon._state.player_data["review_event_log"]
        )
        live_entry = addon._state.player_data["review_event_log"][-1]
        self.assertIsNot(live_entry, detached_entry)

        reason = "You need 1 Soft clay to craft an Unfired pot."
        runtime_ctx.show_error_message("Out of materials", reason)

        self.assertIn(reason, live_entry["text"])
        self.assertNotIn(reason, detached_entry["text"])

    def test_ge_status_navigation_focuses_or_opens_the_ge_tab(self):
        addon = _load_addon_as_package("ankiscape_ge_status_navigation")
        opened = []
        addon.ui._MAIN_MENU_CTX["open_grand_exchange"] = lambda: opened.append(
            "focused"
        )
        addon.ui.focus_main_menu_if_open = lambda: True
        addon._on_main_menu = lambda **_kwargs: self.fail(
            "an open menu must be reused"
        )

        addon._open_grand_exchange_sheet()
        self.assertEqual(opened, ["focused"])

        addon.ui.focus_main_menu_if_open = lambda: False
        addon._on_main_menu = lambda **kwargs: opened.append(kwargs)
        addon._open_grand_exchange_sheet()
        self.assertEqual(opened[-1], {"initial_global_tab": "Grand Exchange"})

    def test_attack_and_constitution_xp_break_down_in_popup_and_event_log(self):
        addon = _load_addon_as_package("ankiscape_event_log_skill_breakdown")
        popup_text = []
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": True}))
        addon.mw.exp_popup = types.SimpleNamespace(
            show_exp=lambda amount: popup_text.append(amount.display_text)
        )
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "attack_exp": 0.0,
            "constitution_exp": 0.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        addon._begin_review_feedback_context()
        attack = addon._award_skill_exp("attack_exp", 40)
        addon._show_exp(attack)
        constitution = addon._award_skill_exp("constitution_exp", 13.3)
        addon._show_exp(constitution)
        addon._finish_review_feedback_context()

        expected = "Attack +40 XP · Constitution +13 XP"
        self.assertEqual(popup_text, [expected])
        self.assertEqual(addon._state.player_data["review_event_log"][-1]["text"], expected)

    def test_fractional_constitution_xp_is_not_displayed_as_zero(self):
        addon = _load_addon_as_package("ankiscape_fractional_constitution_xp")

        amount = addon._NamedExperience(
            1.599,
            ("Attack", "Constitution"),
            (("Attack", 1.2), ("Constitution", 0.399)),
        )

        self.assertEqual(
            amount.display_text,
            "Attack +1 XP · Constitution +0.4 XP",
        )

    def test_xp_event_is_written_before_its_level_up_event(self):
        addon = _load_addon_as_package("ankiscape_xp_before_level_up")
        addon.mw = _DummyMW(
            _DummyCol(
                {
                    "ankiscape_floating_xp_enabled": False,
                    "ankiscape_popups_enabled": False,
                }
            )
        )
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Attack"
        addon._state.player_data = {
            "attack_level": 1,
            "attack_exp": 82.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }
        addon._core_level_up_check = lambda skill, data: (
            data.__setitem__("attack_level", 2),
            addon._record_review_event(
                "achievement",
                f"{skill} advanced to level 2",
                persist=False,
            ),
        )

        addon._begin_review_feedback_context()
        gained = addon._award_skill_exp("attack_exp", 1.0)
        addon.level_up_check("Attack", addon._state.player_data)
        addon._show_exp(gained)
        addon._finish_review_feedback_context()

        self.assertEqual(addon._state.player_data["attack_level"], 2)
        self.assertEqual(
            [row["text"] for row in addon._state.player_data["review_event_log"]],
            ["+1 XP · Attack", "Attack advanced to level 2"],
        )

    def test_xp_review_keeps_every_activity_event_without_replacing_the_xp_popup(self):
        addon = _load_addon_as_package("ankiscape_event_log_mixed_feedback")
        popup_calls = []
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": True}))
        addon.mw.exp_popup = types.SimpleNamespace(
            show_exp=lambda amount: popup_calls.append(("exp", amount)),
            show_text=lambda text: popup_calls.append(("text", text)),
        )
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "attack_exp": 0.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        addon._begin_review_feedback_context()
        gained = addon._award_skill_exp("attack_exp", 47)
        addon._show_exp(gained)
        addon._show_activity_gain("Defeated Goblin")
        addon._show_activity_gain("Combat switched off to stop you dying")
        addon._finish_review_feedback_context()

        self.assertEqual(
            [row["text"] for row in addon._state.player_data["review_event_log"]],
            [
                "+47 XP · Attack",
                "Defeated Goblin",
                "Combat switched off to stop you dying",
            ],
        )
        self.assertEqual(popup_calls, [("exp", 47.0)])

    def test_review_combat_level_boundary_collapses_multi_skill_gain_to_one_check(self):
        addon = _load_addon_as_package("ankiscape_combat_level_boundary")
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "constitution_level": 10,
            "prayer_level": 1,
            "ranged_level": 1,
            "magic_level": 1,
            "summoning_level": 1,
            "review_event_log": [],
        }
        checks = []
        addon._core_combat_level_up_check = lambda old, data: checks.append(
            (old, addon.player_combat_level_pure(data))
        )

        addon._begin_review_feedback_context()
        addon._state.player_data["attack_level"] = 10
        addon._state.player_data["strength_level"] = 10
        addon._finish_review_feedback_context()

        self.assertEqual(len(checks), 1)
        self.assertLess(checks[0][0], checks[0][1])

    def test_direct_xp_event_uses_the_awarded_skill_not_the_selected_skill(self):
        addon = _load_addon_as_package("ankiscape_direct_event_skill_name")
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": False}))
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Mining"
        addon._state.player_data = {
            "hunter_exp": 0.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        gained = addon._award_skill_exp("hunter_exp", 12)
        addon._show_exp(gained)

        self.assertEqual(
            addon._state.player_data["review_event_log"][-1]["text"],
            "+12 XP · Hunter",
        )

    def test_silent_award_cannot_name_a_later_unrelated_xp_event(self):
        addon = _load_addon_as_package("ankiscape_event_log_no_stale_skill")
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": False}))
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Activities"
        addon._state.player_data = {
            "summoning_exp": 0.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        addon._award_skill_exp("summoning_exp", 25.0)
        addon._show_exp(addon._NamedExperience(80.0, ("Hunter",)))

        self.assertEqual(
            addon._state.player_data["review_event_log"][-1]["text"],
            "+80 XP · Hunter",
        )

    def test_review_undo_rolls_back_the_event_log_atomically(self):
        addon = _load_addon_as_package("ankiscape_event_log_undo")
        addon.save_player_data = lambda: None
        addon._state.player_data = {
            "shop_market_clock": {"answered_cards": 12, "market_tick": 12},
            "review_event_log": [],
        }
        addon._state.current_skill = "Mining"
        addon._state.review_undo_stack.clear()
        before = addon._capture_player_data_snapshot()

        addon._record_review_event("activity", "+1 Iron ore", persist=False)
        addon._remember_review_award_snapshot(before)
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data["review_event_log"], [])

    def test_conquest_review_undo_restores_the_exact_pre_exchange_match(self):
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data
        from ankiscape.logic.conquest_logic import (
            apply_conquest_review_pure,
            enter_conquest_pure,
        )

        addon = _load_addon_as_package("ankiscape_conquest_review_undo")
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
            "ranged_level",
            "magic_level",
            "prayer_level",
        ):
            player[key] = 40
        player["activity_session"] = {"active_id": ""}
        player["combat_encounter"] = {}
        player, ok, info = enter_conquest_pure(player, {}, lambda: 0.25)
        self.assertTrue(ok, info)
        addon._state.player_data = player
        addon._state.current_skill = "Activities"
        addon.save_player_data = lambda: None
        addon.ui.update_menu_visibility = lambda _skill: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.review_undo_stack.clear()
        exact_before = copy.deepcopy(addon._state.player_data)
        snapshot = addon._capture_player_data_snapshot()

        advanced, ok, result = apply_conquest_review_pure(
            addon._state.player_data, lambda: 0.5
        )
        self.assertTrue(ok, result)
        addon._state.player_data.clear()
        addon._state.player_data.update(advanced)
        self.assertNotEqual(addon._state.player_data["conquest"], exact_before["conquest"])
        addon._remember_review_award_snapshot(snapshot)
        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, exact_before)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_direct_leave_command_lands_on_bankstanding_and_undoes_atomically(self):
        # Owner clause 2: a direct command that ends an active activity session
        # must leave the surface on Bankstanding (never "None"), and the
        # transaction undo must restore the former activity whole.
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data
        from ankiscape.logic.conquest_logic import (
            apply_conquest_command_pure,
            enter_conquest_pure,
        )

        addon = _load_addon_as_package("ankiscape_session_clear_bankstanding")
        addon.mw = _DummyMW(_DummyCol())
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
            "ranged_level",
            "magic_level",
            "prayer_level",
        ):
            player[key] = 40
        player["activity_session"] = {"active_id": ""}
        player["combat_encounter"] = {}
        player, ok, info = enter_conquest_pure(player, {}, lambda: 0.25)
        self.assertTrue(ok, info)
        addon._state.player_data = player
        addon._state.current_skill = "Activities"
        addon.save_player_data = lambda: None
        addon.ui.update_menu_visibility = lambda _skill: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.direct_action_undo_stack.clear()

        self.assertTrue(
            addon.commit_direct_action(
                lambda current: apply_conquest_command_pure(
                    current, "resign", {}, lambda: 0.25
                )[:2]
            )
        )

        self.assertEqual(addon._state.player_data["activity_session"], {"active_id": ""})
        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")

        addon._restore_direct_action_snapshot(addon._state.direct_action_undo_stack.pop())

        self.assertEqual(addon._state.player_data["activity_session"], {"active_id": "conquest"})
        self.assertEqual(addon._state.player_data["current_utility"], "conquest")
        self.assertEqual(addon._state.current_skill, "Activities")

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

    def test_fletching_answer_updates_inventory_and_exp(self):
        addon = _load_addon_as_package("ankiscape_fletching_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        addon.on_fletching_answer()

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [5.0])

    def test_firemaking_answer_burns_log_adds_ashes_and_exp(self):
        addon = _load_addon_as_package("ankiscape_firemaking_integration")

        calls = {"save": 0, "xp": [], "achievements": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda data: calls["achievements"].append(data["inventory"].get("Ashes", 0))
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.show_error_message = lambda _title, message: self.fail(message)

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.player_data = {
                "inventory": {"Logs": 1},
                "firemaking_level": 1,
                "firemaking_exp": 0,
                "current_firemaking": "logs",
                "completed_achievements": [],
            }

            addon.on_firemaking_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Ashes"], 1)
        self.assertEqual(
            addon._state.player_data["achievement_progress"]["skills"]["firemaking"]["outputs"]["Ashes"],
            1,
        )
        self.assertAlmostEqual(addon._state.player_data["firemaking_exp"], 40.0)
        self.assertEqual(calls["achievements"], [1])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [40.0])

    def test_fishing_answer_catches_fish_adds_exp_and_hidden_side_exp(self):
        addon = _load_addon_as_package("ankiscape_fishing_integration")

        calls = {"save": 0, "xp": [], "achievements": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda data: calls["achievements"].append(data["inventory"].get("Leaping trout", 0))
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.show_error_message = lambda _title, message: self.fail(message)

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.player_data = {
                "inventory": {"Feather": 1},
                "fishing_level": 48,
                "fishing_exp": 0,
                "strength_level": 15,
                "strength_exp": 0,
                "agility_level": 15,
                "agility_exp": 0,
                "current_fishing": "catch_leaping_fish",
                "completed_achievements": [],
                "unlocked_abilities": ["barbarian_fishing"],
            }

            addon.on_fishing_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Feather"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Leaping trout"], 1)
        self.assertAlmostEqual(addon._state.player_data["fishing_exp"], 50.0)
        self.assertAlmostEqual(addon._state.player_data["strength_exp"], 5.0)
        self.assertAlmostEqual(addon._state.player_data["agility_exp"], 5.0)
        self.assertEqual(calls["achievements"], [1])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [50.0])

    def test_smithing_answer_forges_selected_recipe(self):
        addon = _load_addon_as_package("ankiscape_smithing_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.refresh_skill_availability = lambda *_args, **_kwargs: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Iron bar": 2},
            "smithing_level": 20,
            "smithing_exp": 0,
            "current_smith": "forge_iron_pickaxe",
            "completed_achievements": [],
        }

        addon.on_smithing_answer()

        self.assertEqual(addon._state.player_data["inventory"]["Iron bar"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Iron pickaxe"], 1)
        self.assertAlmostEqual(addon._state.player_data["smithing_exp"], 50.0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [50.0])

    def test_smithing_answer_iron_failure_consumes_ore_without_xp(self):
        addon = _load_addon_as_package("ankiscape_smithing_iron_failure_integration")

        calls = {"save": 0, "xp": [], "gains": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.refresh_skill_availability = lambda *_args, **_kwargs: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Iron ore": 1},
            "smithing_level": 15,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "smelt_iron_bar",
            "completed_achievements": [],
        }

        original_random = addon.random.random
        addon.random.random = lambda: 0.99
        try:
            addon.on_smithing_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Iron ore"], 0)
        self.assertNotIn("Iron bar", addon._state.player_data["inventory"])
        self.assertEqual(addon._state.player_data["smithing_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["gains"], ["The ore was too impure"])
        telemetry = addon._state.player_data["action_telemetry"]["actions"]["smithing:smelt_iron_bar"]
        self.assertEqual(telemetry["failure_kinds"], {"smelt_fail": 1})

    def test_equipment_callbacks_equip_and_unequip_items(self):
        addon = _load_addon_as_package("ankiscape_equipment_callbacks")

        calls = {"save": 0, "errors": []}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.show_error_message = lambda title, message: calls["errors"].append((title, message))
        addon._state.player_data = {
            "inventory": {"Bronze platebody": 1, "Rune platebody": 1},
            "equipment": {},
            "defense_level": 1,
        }

        self.assertTrue(addon.on_equip_item("Bronze platebody"))
        self.assertEqual(addon._state.player_data["inventory"]["Bronze platebody"], 0)
        self.assertEqual(addon._state.player_data["equipment"], {"body": "Bronze platebody"})

        self.assertFalse(addon.on_equip_item("Rune platebody"))
        self.assertEqual(calls["errors"], [("Cannot equip item", "Requires level 40 Defense")])
        self.assertEqual(addon._state.player_data["equipment"], {"body": "Bronze platebody"})

        self.assertTrue(addon.on_unequip_slot("body"))
        self.assertEqual(addon._state.player_data["inventory"]["Bronze platebody"], 1)
        self.assertEqual(addon._state.player_data["equipment"], {})
        self.assertEqual(calls["save"], 2)

    def test_equipment_callbacks_move_degradable_instance_with_the_item(self):
        addon = _load_addon_as_package("ankiscape_equipment_instance_callbacks")
        addon.save_player_data = lambda: None
        addon._state.player_data = {
            "inventory": {"Combat hood 100": 1},
            "equipment": {},
            "defense_level": 20,
            "magic_level": 20,
            "equipment_instances": {
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 80_000,
                    "location": "bank",
                }
            },
            "equipment_instance_next_id": 2,
        }

        self.assertTrue(addon.on_equip_item("Combat hood 100"))
        self.assertEqual(
            addon._state.player_data["equipment_instances"]["equipment-1"]["location"],
            "equipped:head",
        )
        self.assertTrue(addon.on_unequip_slot("head"))
        self.assertEqual(
            addon._state.player_data["equipment_instances"]["equipment-1"]["location"],
            "bank",
        )

    def test_utility_answer_batches_inventory_without_skill_xp(self):
        addon = _load_addon_as_package("ankiscape_utility_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Clay": 3},
            "crafting_exp": 0,
            "current_utility": "make_soft_clay",
            "completed_achievements": [],
        }

        addon.on_utility_answer()

        self.assertEqual(addon._state.player_data["inventory"]["Clay"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Soft clay"], 3)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        # No-XP activities still surface a floating "+N <item>" confirmation so the
        # player knows the review did something despite earning no XP.
        self.assertEqual(calls["gains"], ["+3 Soft clay"])

    def test_wool_gathering_utility_grants_wool_without_skill_xp(self):
        addon = _load_addon_as_package("ankiscape_wool_utility_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {},
            "crafting_exp": 0,
            "current_utility": "gather_wool",
            "completed_achievements": [],
        }

        addon.on_utility_answer()

        self.assertEqual(addon._state.player_data["inventory"]["Wool"], 28)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["+28 Wool"])

    def test_runecrafting_answer_crafts_air_runes_and_awards_exp(self):
        addon = _load_addon_as_package("ankiscape_runecrafting_integration")

        calls = {"save": 0, "xp": [], "achievements": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda data: calls["achievements"].append(data["inventory"].get("Air rune", 0))
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.show_error_message = lambda _title, message: self.fail(message)

        original_random = addon.random.random
        addon.random.random = lambda: 1.0
        try:
            addon._state.player_data = {
                "inventory": {"Rune essence": 30, "Air talisman": 1},
                "equipment": {},
                "runecrafting_level": 1,
                "runecrafting_exp": 0,
                "current_runecrafting": "craft_air_runes",
                "quests": {"rune_mysteries": {"started": True, "progress": 6, "completed": True}},
                "wicked_hood": {"fed_altars": []},
                "runecrafting_pouches": {},
                "item_charges": {},
                "completed_achievements": [],
            }

            addon.on_runecrafting_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Rune essence"], 3)
        self.assertEqual(addon._state.player_data["inventory"]["Air rune"], 27)
        self.assertEqual(
            addon._state.player_data["achievement_progress"]["skills"]["runecrafting"]["outputs"]["Air rune"],
            27,
        )
        self.assertAlmostEqual(addon._state.player_data["runecrafting_exp"], 135.0)
        self.assertEqual(calls["achievements"], [27])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [135.0])

    def test_quest_answer_completes_rune_mysteries_and_switches_off(self):
        addon = _load_addon_as_package("ankiscape_quest_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Research notes": 1},
            "current_quest": "rune_mysteries",
            "quests": {"rune_mysteries": {"started": True, "progress": 5, "completed": False}},
            "quest_action_proofs": ["Return Aubury's research notes to Sedridor"],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "runecrafting_level": 1,
            "runecrafting_exp": 0,
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertTrue(addon._state.player_data["quests"]["rune_mysteries"]["completed"])
        self.assertEqual(addon._state.player_data["quest_points"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Air talisman"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Research notes"], 0)
        self.assertEqual(addon._state.player_data["runecrafting_exp"], 0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Rune Mysteries complete"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest complete")
        self.assertIn("Rune Mysteries is complete", calls["dialogs"][0][1])
        self.assertIn("questing has been switched off", calls["dialogs"][0][1])

    def test_quest_answer_blocks_knights_sword_without_stage_item(self):
        addon = _load_addon_as_package("ankiscape_quest_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "the_knights_sword",
            "quests": {"the_knights_sword": {"started": True, "progress": 2, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "smithing_level": 10,
            "smithing_exp": 0,
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertFalse(addon._state.player_data["quests"]["the_knights_sword"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["the_knights_sword"]["progress"], 2)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["smithing_exp"], 0)
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("Needs Redberry pie x1", calls["dialogs"][0][1])

    def test_quest_answer_progresses_dwarf_cannon_repairs_without_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_dwarf_cannon_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Railing": 6, "Hammer": 1},
            "current_quest": "dwarf_cannon",
            "quests": {"dwarf_cannon": {"started": True, "progress": 2, "completed": False}},
            "quest_points": 0,
            "crafting_exp": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["dwarf_cannon"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["dwarf_cannon"]["progress"], 3)
        self.assertEqual(addon._state.player_data["inventory"]["Railing"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Hammer"], 1)
        self.assertEqual(addon._state.player_data["quest_combat_encounters"], {})
        self.assertEqual(addon._state.player_data["quest_combat_encounter_counts"], {})
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Dwarf Cannon 3/14"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_fishing_contest_pass_emitter(self):
        addon = _load_addon_as_package("ankiscape_fishing_contest_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "fishing_contest",
            "quests": {"fishing_contest": {"started": True, "progress": 1, "completed": False}},
            "quest_points": 0,
            "fishing_exp": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["fishing_contest"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["fishing_contest"]["progress"], 2)
        self.assertEqual(addon._state.player_data["inventory"]["Fishing pass"], 1)
        self.assertEqual(quest_action_proofs_for_quest(addon._state.player_data, "fishing_contest", QUEST_DATA), ("Receive a fishing pass from Austri or Vestri",))
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["fishing_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Fishing Contest 2/7"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_waterfall_book_gate(self):
        addon = _load_addon_as_package("ankiscape_waterfall_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "waterfall_quest",
            "quests": {"waterfall_quest": {"started": True, "progress": 2, "completed": False}},
            "quest_action_proofs": ["Search the Baxtorian bookcase", "Read the Book on Baxtorian"],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["waterfall_quest"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["waterfall_quest"]["progress"], 3)
        self.assertEqual(addon._state.player_data["inventory"]["Book on Baxtorian"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Waterfall Quest 3/6"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_biohazard_pigeon_setup_gate(self):
        addon = _load_addon_as_package("ankiscape_biohazard_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "biohazard",
            "quests": {"biohazard": {"started": True, "progress": 3, "completed": False}},
            "quest_action_proofs": [
                "Ask Jerico about using messenger pigeons",
                "Search Jerico's cupboard for bird feed",
                "Take a pigeon cage from Jerico's house",
            ],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["biohazard"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["biohazard"]["progress"], 4)
        self.assertEqual(addon._state.player_data["inventory"]["Bird feed"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Pigeon cage"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Biohazard 4/14"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_heroes_gerrant_slime_gate(self):
        addon = _load_addon_as_package("ankiscape_heroes_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "heroes_quest",
            "quests": {"heroes_quest": {"started": True, "progress": 2, "completed": False}},
            "quest_action_proofs": ["Ask Gerrant how to catch lava eels"],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["heroes_quest"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["heroes_quest"]["progress"], 3)
        self.assertEqual(addon._state.player_data["inventory"]["Blamish snail slime"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Heroes' Quest 3/13"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_family_crest_caleb_fish_gate(self):
        addon = _load_addon_as_package("ankiscape_family_crest_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {
                "Shrimps": 1,
                "Salmon": 1,
                "Tuna": 1,
                "Bass": 1,
                "Swordfish": 1,
            },
            "current_quest": "family_crest",
            "quests": {"family_crest": {"started": True, "progress": 3, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["family_crest"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["family_crest"]["progress"], 4)
        self.assertEqual(addon._state.player_data["inventory"]["Shrimps"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Swordfish"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Caleb crest"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Family Crest 4/16"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_blocks_witchs_house_mouse_puzzle_without_stage_item(self):
        addon = _load_addon_as_package("ankiscape_witchs_house_mouse_gate_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Magnet": 1},
            "current_quest": "witchs_house",
            "quests": {"witchs_house": {"started": True, "progress": 4, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertFalse(addon._state.player_data["quests"]["witchs_house"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["witchs_house"]["progress"], 4)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("Needs Cheese x1", calls["dialogs"][0][1])
        self.assertNotIn("Use cheese on the mouse hole", calls["dialogs"][0][1])

    def test_quest_answer_blocks_merlins_crystal_wax_without_repellent(self):
        addon = _load_addon_as_package("ankiscape_merlins_crystal_wax_gate_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Bucket": 1},
            "current_quest": "merlins_crystal",
            "quests": {"merlins_crystal": {"started": True, "progress": 4, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertFalse(addon._state.player_data["quests"]["merlins_crystal"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["merlins_crystal"]["progress"], 4)
        self.assertEqual(addon._state.player_data["inventory"]["Bucket"], 1)
        self.assertEqual(addon._state.player_data["inventory"].get("Bucket of wax", 0), 0)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("Needs Insect repellent x1", calls["dialogs"][0][1])

    def test_quest_answer_blocks_fight_arena_statless_combat(self):
        addon = _load_addon_as_package("ankiscape_fight_arena_missing_stats_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Khazard helmet": 1, "Khazard armour": 1, "Khazard cell keys": 1},
            "current_quest": "fight_arena",
            "quests": {"fight_arena": {"started": True, "progress": 8, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 150,
            "strength_level": 150,
            "defense_level": 150,
            "constitution_level": 150,
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertFalse(addon._state.player_data["quests"]["fight_arena"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["fight_arena"]["progress"], 8)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("This fight is not modelled yet (combat stats missing): Khazard ogre level 63", calls["dialogs"][0][1])

    def test_quest_answer_progresses_black_knights_disguise_from_equipment(self):
        addon = _load_addon_as_package("ankiscape_black_knights_stage_integration")

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.level_up_check = lambda _skill, _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "equipment": {"body": "Iron chainbody", "head": "Bronze med helm"},
            "current_quest": "black_knights_fortress",
            "quests": {"black_knights_fortress": {"started": True, "progress": 1, "completed": False}},
            "quest_action_proofs": ["Infiltrate the Black Knights' Fortress"],
            "quest_points": 12,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(addon._state.player_data["quests"]["black_knights_fortress"]["progress"], 2)
        self.assertFalse(addon._state.player_data["quests"]["black_knights_fortress"]["completed"])
        self.assertEqual(addon._state.player_data["quest_points"], 12)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Black Knights' Fortress 2/5"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_consumes_priest_in_peril_essence_at_completion_gate(self):
        addon = _load_addon_as_package("ankiscape_priest_in_peril_essence_integration")

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.level_up_check = lambda _skill, _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Rune essence": 50, "Pure essence": 24},
            "current_quest": "priest_in_peril",
            "quests": {"priest_in_peril": {"started": True, "progress": 8, "completed": False}},
            "quest_points": 0,
            "prayer_exp": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertTrue(addon._state.player_data["quests"]["priest_in_peril"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["priest_in_peril"]["progress"], 9)
        self.assertEqual(addon._state.player_data["inventory"]["Rune essence"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Pure essence"], 24)
        self.assertEqual(addon._state.player_data["inventory"]["Wolfbane dagger"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 1)
        self.assertEqual(addon._state.player_data["prayer_exp"], 1406.0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["dialogs"][0][0], "Quest complete")

    def test_quest_answer_completes_temple_of_ikov_lucien_branch_and_consumes_staff(self):
        addon = _load_addon_as_package("ankiscape_temple_of_ikov_lucien_integration")

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.level_up_check = lambda _skill, _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Staff of armadyl": 1},
            "current_quest": "temple_of_ikov",
            "quests": {"temple_of_ikov": {"started": True, "progress": 10, "completed": False}},
            "quest_route_states": {"temple_of_ikov": ["Side with Lucien"]},
            "quest_action_proofs": ["Give the Staff of Armadyl to Lucien in Varrock"],
            "quest_points": 0,
            "thieving_level": 42,
            "fletching_level": 1,
            "fletching_exp": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertTrue(addon._state.player_data["quests"]["temple_of_ikov"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["temple_of_ikov"]["progress"], 11)
        self.assertEqual(addon._state.player_data["inventory"]["Staff of armadyl"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Shiny key"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 1)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Temple of Ikov complete"])
        self.assertEqual(calls["dialogs"][0][0], "Quest complete")

    def test_quest_answer_resolves_stat_backed_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Stake": 1, "Stake hammer": 1},
            "current_quest": "vampyre_slayer",
            "quests": {"vampyre_slayer": {"started": True, "progress": 3, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 35,
            "constitution_level": 40,
            "prayer_level": 20,
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(addon._state.player_data["quests"]["vampyre_slayer"]["progress"], 3)
        self.assertFalse(addon._state.player_data["quests"]["vampyre_slayer"]["completed"])
        self.assertEqual(addon._state.player_data["quest_combat_encounters"], {"vampyre_slayer": ["vampyre_slayer_count_draynor_37"]})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Count Draynor"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_resolves_shield_of_arrav_route_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_shield_arrav_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "shield_of_arrav",
            "quests": {"shield_of_arrav": {"started": True, "progress": 5, "completed": False}},
            "quest_route_states": {"shield_of_arrav": ["Join the Black Arm Gang"]},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "prayer_level": 1,
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(addon._state.player_data["quests"]["shield_of_arrav"]["progress"], 5)
        self.assertFalse(addon._state.player_data["quests"]["shield_of_arrav"]["completed"])
        self.assertEqual(
            addon._state.player_data["quest_combat_encounters"],
            {"shield_of_arrav": ["shield_of_arrav_weaponsmaster_23"]},
        )
        self.assertEqual(addon._state.player_data["inventory"].get("Weapon store key", 0), 0)
        self.assertEqual(addon._state.player_data["inventory"].get("Phoenix crossbow", 0), 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Weaponsmaster"])
        self.assertEqual(calls["dialogs"], [])

        addon.on_quest_answer()

        self.assertEqual(addon._state.player_data["quests"]["shield_of_arrav"]["progress"], 6)
        self.assertFalse(addon._state.player_data["quests"]["shield_of_arrav"]["completed"])
        self.assertEqual(addon._state.player_data["inventory"]["Weapon store key"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Phoenix crossbow"], 2)
        self.assertEqual(calls["save"], 2)
        self.assertEqual(calls["gains"][-1], "Shield of Arrav 6/12")

    def test_quest_answer_resolves_a_souls_bane_fear_reaper_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_a_souls_bane_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "a_souls_bane",
            "quests": {"a_souls_bane": {"started": True, "progress": 3, "completed": False}},
            "quest_action_proofs": ["Fill the rage meter with an anger weapon"],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 100,
            "strength_level": 100,
            "defense_level": 100,
            "constitution_level": 100,
            "prayer_level": 1,
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(addon._state.player_data["quests"]["a_souls_bane"]["progress"], 3)
        self.assertFalse(addon._state.player_data["quests"]["a_souls_bane"]["completed"])
        self.assertEqual(
            addon._state.player_data["quest_combat_encounter_counts"],
            {"a_souls_bane": {"a_souls_bane_fear_reaper_42": 1}},
        )
        self.assertEqual(addon._state.player_data["quest_combat_encounters"], {})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Fear reaper"])
        self.assertEqual(calls["dialogs"], [])

    def test_stolen_hearts_review_flow_resolves_the_real_mercenary_stage(self):
        addon = _load_addon_as_package("ankiscape_stolen_hearts_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "stolen_hearts",
            "quests": {
                "stolen_hearts": {
                    "started": True,
                    "progress": 3,
                    "completed": False,
                }
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "ranged_level": 99,
            "magic_level": 99,
            "prayer_level": 99,
        }

        for expected_gain in (
            "Defeated Mercenary Joe",
            "Defeated Skulls mercenary",
            "Defeated Skulls mercenary",
        ):
            addon.on_quest_answer()
            self.assertEqual(calls["gains"][-1], expected_gain)
            self.assertEqual(
                addon._state.player_data["quests"]["stolen_hearts"]["progress"],
                3,
            )

        addon.on_quest_answer()

        self.assertEqual(addon._state.player_data["quests"]["stolen_hearts"]["progress"], 4)
        self.assertEqual(addon._state.player_data["inventory"]["Ransom note"], 1)
        self.assertEqual(calls["gains"][-1], "Stolen Hearts 4/6")
        self.assertEqual(calls["save"], 4)
        self.assertEqual(calls["dialogs"], [])

    def test_diamond_in_the_rough_review_flow_resolves_the_sundial_ambush(self):
        addon = _load_addon_as_package("ankiscape_diamond_in_the_rough_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Heavy weight": 1},
            "current_quest": "diamond_in_the_rough",
            "quests": {
                "stolen_hearts": {
                    "started": True,
                    "progress": 6,
                    "completed": True,
                },
                "diamond_in_the_rough": {
                    "started": True,
                    "progress": 2,
                    "completed": False,
                },
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 1,
        }

        for expected_gain in (
            "Defeated Bandit (Diamond in the Rough)",
            "Defeated Bandit (Diamond in the Rough)",
            "Defeated Bandit (Diamond in the Rough)",
            "Defeated Bandit (Diamond in the Rough)",
            "Defeated Bandit (Diamond in the Rough)",
            "Defeated Bandit king",
        ):
            addon.on_quest_answer()
            self.assertEqual(calls["gains"][-1], expected_gain)
            self.assertEqual(
                addon._state.player_data["quests"]["diamond_in_the_rough"]["progress"],
                2,
            )

        addon.on_quest_answer()

        self.assertEqual(
            addon._state.player_data["quests"]["diamond_in_the_rough"]["progress"],
            3,
        )
        self.assertEqual(addon._state.player_data["inventory"]["Sundial gnomon"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Waterskin (4)"], 4)
        self.assertEqual(calls["gains"][-1], "Diamond in the Rough 3/5")
        self.assertEqual(calls["save"], 7)
        self.assertEqual(calls["dialogs"], [])

    def test_icthlarins_little_helper_review_flow_resolves_the_canopic_guardian(self):
        addon = _load_addon_as_package("ankiscape_icthlarins_little_helper_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {
                "Canopic jar": 1,
                "Sphinx's token": 1,
                "Coins": 30,
                "Willow logs": 1,
                "Bucket": 1,
                "Bag of salt": 1,
                "Knife": 1,
            },
            "current_quest": "icthlarins_little_helper",
            "quests": {
                "icthlarins_little_helper": {
                    "started": True,
                    "progress": 3,
                    "completed": False,
                },
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 1,
        }

        addon.on_quest_answer()
        self.assertEqual(calls["gains"][-1], "Icthlarin's Little Helper 4/9")
        self.assertEqual(
            addon._state.player_data["quests"]["icthlarins_little_helper"]["progress"],
            4,
        )
        self.assertEqual(addon._state.player_data["inventory"].get("Canopic jar", 0), 0)
        self.assertEqual(addon._state.player_data["inventory"].get("Sphinx's token", 0), 0)

        addon.on_quest_answer()
        self.assertEqual(calls["gains"][-1], "Defeated Canopic guardian")
        self.assertEqual(
            addon._state.player_data["quests"]["icthlarins_little_helper"]["progress"],
            4,
        )

        addon.on_quest_answer()

        self.assertEqual(
            addon._state.player_data["quests"]["icthlarins_little_helper"]["progress"],
            5,
        )
        self.assertEqual(addon._state.player_data["inventory"]["Canopic jar"], 1)

        addon.on_quest_answer()

        self.assertEqual(
            addon._state.player_data["quests"]["icthlarins_little_helper"]["progress"],
            6,
        )
        self.assertEqual(
            addon._state.player_data["inventory"]["Holy symbol (Icthlarin's Little Helper)"],
            1,
        )
        self.assertEqual(addon._state.player_data["inventory"].get("Bucket", 0), 0)
        self.assertEqual(calls["gains"][-1], "Icthlarin's Little Helper 6/9")
        self.assertEqual(calls["save"], 4)
        self.assertEqual(calls["dialogs"], [])

    def test_smoking_kills_review_flow_resolves_mighty_banshee_and_voice(self):
        addon = _load_addon_as_package("ankiscape_smoking_kills_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Masked earmuffs": 1},
            "current_quest": "smoking_kills",
            "quests": {
                "smoking_kills": {
                    "started": True,
                    "progress": 9,
                    "completed": False,
                },
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "ranged_level": 99,
            "magic_level": 99,
            "prayer_level": 99,
        }

        addon.on_quest_answer()
        self.assertEqual(calls["gains"][-1], "Defeated Mighty banshee")
        self.assertEqual(addon._state.player_data["quests"]["smoking_kills"]["progress"], 9)

        addon.on_quest_answer()

        self.assertEqual(addon._state.player_data["quests"]["smoking_kills"]["progress"], 10)
        self.assertEqual(addon._state.player_data["inventory"]["Banshee voice"], 1)
        self.assertEqual(calls["gains"][-1], "Smoking Kills 10/13")
        self.assertEqual(calls["save"], 2)
        self.assertEqual(calls["dialogs"], [])

    def test_shilo_village_review_flow_resolves_all_nazastarool_forms_then_corpse(self):
        addon = _load_addon_as_package("ankiscape_shilo_village_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Bone key": 1, "Beads of the dead": 1},
            "current_quest": "shilo_village",
            "quests": {
                "shilo_village": {
                    "started": True,
                    "progress": 10,
                    "completed": False,
                },
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 200,
            "strength_level": 200,
            "defense_level": 200,
            "constitution_level": 200,
            "ranged_level": 200,
            "magic_level": 200,
            "prayer_level": 200,
        }

        for display_name in (
            "Nazastarool (Zombie)",
            "Nazastarool (Skeleton)",
            "Nazastarool (Ghost)",
        ):
            addon.on_quest_answer()
            self.assertEqual(calls["gains"][-1], f"Defeated {display_name}")
            self.assertEqual(addon._state.player_data["quests"]["shilo_village"]["progress"], 10)

        addon.on_quest_answer()

        self.assertEqual(addon._state.player_data["quests"]["shilo_village"]["progress"], 11)
        self.assertEqual(addon._state.player_data["inventory"]["Rashiliyia corpse"], 1)
        self.assertEqual(calls["gains"][-1], "Shilo Village 11/12")
        self.assertEqual(calls["save"], 4)
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_completes_holy_grail_final_handoff_and_consumes_grail(self):
        addon = _load_addon_as_package("ankiscape_holy_grail_completion_integration")

        calls = {"save": 0, "gains": [], "dialogs": [], "passes": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.level_up_check = lambda _skill, data: data.__setitem__("defense_level", 33)
        addon.mw = _DummyMW(
            _DummyCol(
                {
                    "ankiscape_popups_enabled": False,
                    "ankiscape_review_action_multiplier": 3,
                    "ankiscape_cadence_kernel": False,
                }
            )
        )
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Holy grail": 1},
            "current_quest": "holy_grail",
            "quests": {"holy_grail": {"started": True, "progress": 10, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }
        original_overlay = addon.runtime_actions.run_answer_with_carried_overlay

        def counted_overlay(*args, **kwargs):
            calls["passes"] += 1
            return original_overlay(*args, **kwargs)

        addon.runtime_actions.run_answer_with_carried_overlay = counted_overlay
        addon._state.exp_awarded = False

        addon.on_good_answer()

        self.assertEqual(calls["passes"], 1)
        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(addon._state.player_data["quests"]["holy_grail"]["progress"], 11)
        self.assertTrue(addon._state.player_data["quests"]["holy_grail"]["completed"])
        self.assertEqual(addon._state.player_data["inventory"]["Holy grail"], 0)
        self.assertEqual(addon._state.player_data["quest_points"], 2)
        self.assertEqual(addon._state.player_data["defense_exp"], 15300.0)
        self.assertGreater(addon._state.player_data["defense_level"], 1)
        self.assertEqual(addon._state.player_data["prayer_exp"], 11000.0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Holy Grail complete"])
        self.assertEqual(
            [title for title, _message in calls["dialogs"]],
            ["Quest complete"],
        )

    def test_utility_opens_bird_nests_without_skill_xp(self):
        addon = _load_addon_as_package("ankiscape_bird_nest_utility_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda _title, message: self.fail(message)

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.player_data = {
                "inventory": {"Bird's nest (seeds)": 1},
                "woodcutting_exp": 0,
                "current_utility": "open_bird_nest",
                "completed_achievements": [],
            }

            addon.on_utility_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Bird's nest (seeds)"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Bird's nest (empty)"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Acorn"], 1)
        self.assertEqual(addon._state.player_data["woodcutting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Opened 1 bird nest"])

    def test_utility_out_of_materials_switches_to_bankstanding_and_warns(self):
        # Material exhaustion warns once, then future cards keep the ordinary
        # market clock moving through the settled no-XP Bankstanding fallback.
        addon = _load_addon_as_package("ankiscape_utility_depleted")
        errors = []
        addon.check_achievements = lambda _d: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _t: self.fail("should not gain when out of materials")
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon._state.current_skill = "Utility / Activities"
        addon._state.player_data = {"inventory": {}, "current_utility": "make_soft_clay", "completed_achievements": []}

        addon.on_utility_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(errors, [])
        self.assertIn("Clay", addon._state.pending_bankstanding_notice["reason"])

    def test_crafting_missing_intermediate_names_material_and_uses_bankstanding(self):
        # "Pot" needs an "Unfired pot", not Soft clay directly. The error must name
        # the actual missing item (so a bank full of Soft clay doesn't look like a
        # bug) and switch future reviews to Bankstanding.
        addon = _load_addon_as_package("ankiscape_craft_depleted")
        errors = []
        addon.check_achievements = lambda _d: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon._state.current_skill = "Crafting"
        addon._state.player_data = {
            "inventory": {"Soft clay": 231},
            "crafting_level": 50,
            "current_craft": "fire_empty_pot",
            "completed_achievements": [],
        }

        addon.on_crafting_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(errors, [])
        self.assertIn("Pot (unfired)", addon._state.pending_bankstanding_notice["reason"])

    def test_changing_target_refreshes_review_hud(self):
        # Switching the active Utility activity (or any target) must push the new
        # state to the in-review HUD immediately, not on the next card.
        addon = _load_addon_as_package("ankiscape_target_hud_refresh")
        calls = {"hud": []}
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda data, skill: calls["hud"].append(skill)
        addon._state.current_skill = "Utility / Activities"
        addon._state.player_data = {"inventory": {}, "current_utility": "gather_flax"}
        addon.mw = _DummyMW(_DummyCol())

        addon._set_value("current_utility", "make_soft_clay")

        self.assertEqual(addon._state.player_data["current_utility"], "make_soft_clay")
        self.assertEqual(calls["hud"], ["Utility / Activities"])

    def test_review_handler_lookup_uses_action_registry_for_skills_and_utility(self):
        addon = _load_addon_as_package("ankiscape_action_dispatch_lookup")

        self.assertIs(addon._registered_answer_handler("Fletching"), addon.runtime_actions.handle_fletching_answer)
        self.assertIs(addon._registered_answer_handler("Firemaking"), addon.runtime_actions.handle_firemaking_answer)
        self.assertIs(addon._registered_answer_handler("Fishing"), addon.runtime_actions.handle_fishing_answer)
        self.assertIs(addon._registered_answer_handler("Utility / Activities"), addon.runtime_actions.handle_utility_answer)
        self.assertIs(addon._registered_answer_handler("Utility"), addon.runtime_actions.handle_utility_answer)
        self.assertIs(addon._registered_answer_handler("Utilities"), addon.runtime_actions.handle_utility_answer)
        self.assertIs(addon._registered_answer_handler("Activities"), addon.runtime_actions.handle_utility_answer)
        self.assertIs(addon._registered_answer_handler("Thieving"), addon.runtime_actions.handle_thieving_answer)

    def test_legacy_combined_no_xp_skill_normalizes_from_its_selected_target(self):
        addon = _load_addon_as_package("ankiscape_legacy_no_xp_surface")
        addon._state.player_data = {"current_utility": "make_soft_clay"}
        self.assertEqual(
            addon._normalize_legacy_utility_skill("Utility / Activities"),
            "Utilities",
        )
        addon._state.player_data["current_utility"] = "livid_farm"
        self.assertEqual(
            addon._normalize_legacy_utility_skill("Utility / Activities"),
            "Activities",
        )
        addon._state.player_data["current_utility"] = "mage_arena_attune:guthix"
        self.assertEqual(
            addon._normalize_legacy_utility_skill("Utility"),
            "Activities",
        )

    def test_can_start_current_action_uses_handler_keyed_readiness_checks(self):
        addon = _load_addon_as_package("ankiscape_action_dispatch_readiness")

        addon._state.current_skill = "Fletching"
        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "current_fletch": "arrow_shafts",
        }
        self.assertTrue(addon._can_start_current_action())

        addon._state.player_data["inventory"] = {}
        self.assertFalse(addon._can_start_current_action())

        addon._state.current_skill = "Firemaking"
        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "firemaking_level": 1,
            "current_firemaking": "logs",
        }
        self.assertTrue(addon._can_start_current_action())

        addon._state.player_data["inventory"] = {}
        self.assertFalse(addon._can_start_current_action())

        addon._state.current_skill = "Fishing"
        addon._state.player_data = {
            "inventory": {"Fishing bait": 1},
            "fishing_level": 5,
            "current_fishing": "catch_sardine_herring",
        }
        self.assertTrue(addon._can_start_current_action())

        addon._state.player_data["inventory"] = {}
        self.assertFalse(addon._can_start_current_action())

        addon._state.current_skill = "Utility"
        addon._state.player_data = {"inventory": {"Clay": 1}, "current_utility": "make_soft_clay"}
        self.assertTrue(addon._can_start_current_action())

        addon._state.player_data = {"inventory": {}, "current_utility": "make_soft_clay"}
        self.assertFalse(addon._can_start_current_action())

    def test_review_action_multiplier_runs_complete_live_cadence_steps(self):
        addon = _load_addon_as_package("ankiscape_review_multiplier_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 2}))
        addon.mw.exp_popup = types.SimpleNamespace(show_exp=lambda exp: calls["xp"].append(exp))

        addon._state.player_data = {
            "inventory": {},
            "woodcutting_level": 1,
            "woodcutting_exp": 0,
            "current_tree": "tree",
            "toolbelt": {"woodcutting": ["bronze_hatchet"]},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.current_skill = "Woodcutting"
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

            addon._state.current_skill = "Fletching"
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon._state.player_data["woodcutting_exp"], 25.0)
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(calls["xp"], [25.0, 5.0])

    def test_thieving_failure_is_one_attempt_under_multiplier_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_thieving_review_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon._state.player_data = {
            "inventory": {},
            "thieving_level": 1,
            "thieving_exp": 0.0,
            "current_thieving": "pickpocket_man",
            "thieving_attempt_count": 0,
            "thieving_success_count": 0,
            "thieving_failure_count": 0,
            "thieving_stunned": False,
            "combat_lifepoints": 100,
            "completed_achievements": [],
        }
        initial_state = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Thieving"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        rolls = iter((0.999, 0.0))
        addon.random.random = lambda: next(rolls)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["thieving_attempt_count"], 1)
        self.assertEqual(addon._state.player_data["thieving_failure_count"], 1)
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 90)
        self.assertTrue(addon._state.player_data["thieving_stunned"])
        self.assertEqual(addon._state.player_data["thieving_exp"], 0.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, initial_state)
        self.assertEqual(addon._state.current_skill, "Thieving")
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_thieving_success_and_stall_cadence_ignore_review_multiplier(self):
        addon = _load_addon_as_package("ankiscape_thieving_multiplier_cap_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon._state.current_skill = "Thieving"

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.player_data = {
                "inventory": {},
                "thieving_level": 50,
                "thieving_exp": 0.0,
                "current_thieving": "pickpocket_man",
                "thieving_attempt_count": 0,
                "thieving_success_count": 0,
                "thieving_failure_count": 0,
                "thieving_stunned": False,
                "combat_lifepoints": 100,
                "completed_achievements": [],
            }
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

            self.assertEqual(addon._state.player_data["thieving_attempt_count"], 1)
            self.assertEqual(addon._state.player_data["thieving_success_count"], 1)
            self.assertEqual(addon._state.player_data["inventory"]["Coins"], 3)
            self.assertEqual(addon._state.player_data["thieving_exp"], 8.0)

            addon._state.player_data = {
                "inventory": {},
                "thieving_level": 50,
                "thieving_exp": 0.0,
                "current_thieving": "stall_silver",
                "thieving_attempt_count": 0,
                "thieving_success_count": 0,
                "thieving_failure_count": 0,
                "thieving_stunned": False,
                "cadence_profiles": {},
                "combat_lifepoints": 100,
                "completed_achievements": [],
            }
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["thieving_attempt_count"], 1)
        self.assertEqual(addon._state.player_data["thieving_success_count"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Silver ore"], 1)
        self.assertEqual(addon._state.player_data["thieving_exp"], 54.0)
        self.assertEqual(
            addon._state.player_data["cadence_profiles"]["thieving:stall_silver"]["assigned_reviews"],
            1,
        )

    def test_wall_safe_failure_consumes_one_multiplied_review_and_undoes_cadence(self):
        addon = _load_addon_as_package("ankiscape_wall_safe_review_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon._state.player_data = {
            "inventory": {},
            "thieving_level": 50,
            "thieving_exp": 0.0,
            "current_thieving": "wall_safe",
            "thieving_attempt_count": 0,
            "thieving_success_count": 0,
            "thieving_failure_count": 0,
            "thieving_stunned": False,
            "cadence_profiles": {},
            "combat_lifepoints": 100,
            "completed_achievements": [],
        }
        initial_state = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Thieving"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        rolls = iter((85 / 255, 0.0))
        addon.random.random = lambda: next(rolls)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["thieving_attempt_count"], 1)
        self.assertEqual(addon._state.player_data["thieving_failure_count"], 1)
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 80)
        self.assertTrue(addon._state.player_data["thieving_stunned"])
        self.assertEqual(
            addon._state.player_data["cadence_profiles"]["thieving:wall_safe"]["assigned_reviews"],
            1,
        )

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, initial_state)
        self.assertEqual(addon._state.current_skill, "Thieving")

    def test_utility_multiplier_runs_wool_gathering_ticks(self):
        addon = _load_addon_as_package("ankiscape_wool_multiplier_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 2}))
        addon.mw.exp_popup = types.SimpleNamespace(show_text=lambda text: calls["gains"].append(text))
        addon._state.player_data = {
            "inventory": {},
            "crafting_exp": 0,
            "current_utility": "gather_wool",
            "completed_achievements": [],
        }

        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Wool"], 56)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["+56 Wool"])

    def test_bankstanding_advances_only_the_normal_review_market_tick(self):
        addon = _load_addon_as_package("ankiscape_bankstanding_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save", calls["save"] + 1
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(
            _DummyCol({"ankiscape_review_action_multiplier": 10})
        )
        addon.mw.exp_popup = types.SimpleNamespace(
            show_text=lambda text: calls["gains"].append(text)
        )
        inventory = {"Coins": 1_000, "Logs": 4}
        addon._state.player_data = {
            "inventory": copy.deepcopy(inventory),
            "current_utility": "bankstanding",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["inventory"], inventory)
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["market_tick"],
            1,
        )
        self.assertEqual(
            addon._state.player_data["ge_market_state"]["last_processed_tick"],
            1,
        )
        # Bankstanding produces nothing by definition, so a review of it is
        # silent; the HUD already reads "idle at the Bank".
        self.assertEqual(calls["gains"], [])

    def test_evil_tree_spawns_on_shared_review_clock_and_undo_restores_world(self):
        addon = _load_addon_as_package("ankiscape_evil_tree_clock_integration")
        from ankiscape_evil_tree_clock_integration.logic.evil_tree_logic import (
            default_evil_tree_state_pure,
        )

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        world_event_gains = []
        addon._show_activity_gain = world_event_gains.append
        addon.check_achievements = lambda *_args: None
        initial = {
            "inventory": {},
            "shop_market_clock": {
                "answered_cards": 19,
                "market_tick": 19,
            },
            "evil_tree": default_evil_tree_state_pure(),
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            addon.random.random = original_random

        event = addon._state.player_data["evil_tree"]["active_event"]
        self.assertEqual(event["tier_id"], "normal")
        self.assertEqual(event["reviews_remaining"], 5)
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["answered_cards"], 20
        )
        # The spawn is silent. These messages ran after the per-review feedback
        # context had closed, so each one became its own floating popup.
        self.assertEqual(world_event_gains, [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(
                    study_queues=True,
                    card=True,
                ),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_big_chinchompa_spawns_on_review_clock_and_undo_restores_world(self):
        addon = _load_addon_as_package(
            "ankiscape_big_chinchompa_clock_integration"
        )
        from ankiscape_big_chinchompa_clock_integration.logic.big_chinchompa_logic import (
            default_big_chinchompa_state_pure,
        )

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        world_event_gains = []
        addon._show_activity_gain = world_event_gains.append
        initial = {
            "inventory": {},
            "shop_market_clock": {
                "answered_cards": 59,
                "market_tick": 59,
            },
            "world_population_profile": "quiet",
            "big_chinchompa": default_big_chinchompa_state_pure(),
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        event = addon._state.player_data["big_chinchompa"]["active_event"]
        self.assertEqual(event["slot_card"], 60)
        self.assertIn("Hunter area", event["location"])
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["answered_cards"],
            60,
        )
        self.assertEqual(world_event_gains, [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(
                    study_queues=True,
                    card=True,
                ),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_shooting_star_spawns_on_review_clock_and_undo_restores_world(self):
        addon = _load_addon_as_package(
            "ankiscape_shooting_star_clock_integration"
        )
        from ankiscape_shooting_star_clock_integration.logic.shooting_star_logic import (
            default_shooting_star_state_pure,
        )

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        world_event_gains = []
        addon._show_activity_gain = world_event_gains.append
        initial = {
            "inventory": {},
            "shop_market_clock": {
                "answered_cards": 19,
                "market_tick": 19,
            },
            "world_population_profile": "normal",
            "shooting_star": default_shooting_star_state_pure(),
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        event = addon._state.player_data["shooting_star"]["active_event"]
        self.assertEqual(event["slot_card"], 20)
        self.assertIn(event["starting_size"], range(1, 10))
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["answered_cards"],
            20,
        )
        self.assertEqual(world_event_gains, [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(
                    study_queues=True,
                    card=True,
                ),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_shooting_star_unminable_review_exit_and_banner_undo_together(self):
        addon = _load_addon_as_package("ankiscape_star_unminable_undo")
        from ankiscape_star_unminable_undo.logic.shooting_star_logic import (
            default_shooting_star_state_pure,
        )

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        refreshed = {"context": 0, "events": 0}
        addon.update_review_context_action_strip = lambda *_args: refreshed.__setitem__(
            "context", refreshed["context"] + 1
        )
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: refreshed.__setitem__(
            "events", refreshed["events"] + 1
        )
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        state = default_shooting_star_state_pure()
        state["active_event"] = {
            "event_id": "shooting-star-20",
            "slot_card": 20,
            "location": "Falador east mine",
            "starting_size": 9,
            "current_size": 9,
            "layer_remaining": 15,
        }
        initial = {
            "current_utility": "shooting_stars",
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "equipment": {},
            "mining_level": 10,
            "mining_exp": 0.0,
            "completed_achievements": [],
            "shop_market_clock": {"answered_cards": 20, "market_tick": 20},
            "shooting_star": state,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(
            addon._state.player_data["shooting_star"]["notice"]["kind"],
            "unminable",
        )
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)
        self.assertEqual(refreshed, {"context": 1, "events": 1})

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.current_skill, "Activities")

    def test_material_exhaustion_falls_back_once_then_bankstands(self):
        addon = _load_addon_as_package(
            "ankiscape_material_fallback_bankstanding_integration"
        )
        calls = {"errors": [], "gains": []}
        modal_order = []
        addon.ui.show_bankstanding_dialog = lambda reason: modal_order.append(
            ("modal", reason)
        )
        finish_feedback = addon._finish_review_feedback_context

        def _finish_feedback():
            modal_order.append(("feedback", "flushed"))
            finish_feedback()

        addon._finish_review_feedback_context = _finish_feedback
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda title, message: calls["errors"].append(
            (title, message)
        )
        addon.mw = _DummyMW(
            _DummyCol({"ankiscape_review_action_multiplier": 1})
        )
        addon.mw.exp_popup = types.SimpleNamespace(
            show_text=lambda text: calls["gains"].append(text)
        )
        addon._state.player_data = {
            "inventory": {"Soft clay": 20},
            "crafting_level": 50,
            "current_craft": "fire_empty_pot",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Crafting"
        addon._state.pending_review_dialogs.append(
            lambda: modal_order.append(("queued", "prompt"))
        )

        for review in range(2):
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease, review=review: modal_order.append(
                    ("answer", review)
                )
                or "answered",
            )

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["gains"], [])
        self.assertEqual(
            [kind for kind, _value in modal_order],
            ["feedback", "answer", "modal", "queued", "feedback", "answer"],
        )
        modal_reasons = [value for kind, value in modal_order if kind == "modal"]
        self.assertEqual(len(modal_reasons), 1)
        self.assertIn("Pot (unfired)", modal_reasons[0])
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["market_tick"],
            2,
        )
        self.assertEqual(
            addon._state.player_data["ge_market_state"]["last_processed_tick"],
            2,
        )

    def test_one_shot_utility_purchase_runs_once_and_switches_off(self):
        # No shipped activity uses deactivate_after_run since the
        # buy_hunter_supplies bridge was retired (its gear is live NPC shop
        # stock), but the runtime one-shot path stays supported; exercise it
        # with an injected activity spec.
        addon = _load_addon_as_package("ankiscape_one_shot_purchase_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 10}))
        addon.mw.exp_popup = types.SimpleNamespace(show_text=lambda text: calls["gains"].append(text))
        addon.UTILITY_ACTIVITY_DATA["one_shot_bundle"] = {
            "display_name": "Buy one-shot bundle",
            "requirements": {"Coins": 500},
            "outputs": {"Bird snare": 1, "Impling jar": 10},
            "batch_size": 1,
            "deactivate_after_run": True,
            "group": "shopping",
            "source": "test fixture",
        }
        addon._state.player_data = {
            "inventory": {"Coins": 500},
            "current_utility": "one_shot_bundle",
            "completed_achievements": [],
        }

        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon.mw.col.get_config("ankiscape_current_skill"), "Utilities")
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Bird snare"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Impling jar"], 10)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Bought one-shot bundle"])

    def test_bad_review_action_multiplier_config_falls_back_to_one_tick(self):
        addon = _load_addon_as_package("ankiscape_bad_review_multiplier_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": "not-a-number"}))
        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 5.0)

    def test_processing_multiplier_stops_when_materials_are_depleted(self):
        addon = _load_addon_as_package("ankiscape_review_multiplier_depletion")

        calls = {"xp": [], "errors": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: calls["errors"].append(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon.mw.exp_popup = types.SimpleNamespace(show_exp=lambda exp: calls["xp"].append(exp))
        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(calls["xp"], [5.0])
        self.assertEqual(calls["errors"], [])

    def test_firemaking_multiplier_stops_when_logs_are_depleted(self):
        addon = _load_addon_as_package("ankiscape_firemaking_multiplier_depletion")

        calls = {"xp": [], "errors": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: calls["errors"].append(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon.mw.exp_popup = types.SimpleNamespace(show_exp=lambda exp: calls["xp"].append(exp))
        addon._state.player_data = {
            "inventory": {"Logs": 2},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Firemaking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Ashes"], 2)
        self.assertAlmostEqual(addon._state.player_data["firemaking_exp"], 80.0)
        self.assertEqual(calls["xp"], [80.0])
        self.assertEqual(calls["errors"], [])

    def test_fishing_multiplier_stops_when_bait_is_depleted(self):
        addon = _load_addon_as_package("ankiscape_fishing_multiplier_depletion")

        calls = {"xp": [], "errors": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: calls["errors"].append(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon.mw.exp_popup = types.SimpleNamespace(show_exp=lambda exp: calls["xp"].append(exp))
        addon._state.player_data = {
            "inventory": {"Fishing bait": 1},
            "fishing_level": 5,
            "fishing_exp": 0,
            "strength_level": 1,
            "agility_level": 1,
            "current_fishing": "catch_sardine_herring",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fishing"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Fishing bait"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Raw sardine"], 1)
        self.assertAlmostEqual(addon._state.player_data["fishing_exp"], 20.0)
        self.assertEqual(calls["xp"], [20.0])
        self.assertEqual(calls["errors"], [])

    def test_undo_after_review_restores_awarded_game_progress(self):
        addon = _load_addon_as_package("ankiscape_undo_integration")

        calls = {"save": 0, "hud": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Logs": 1})
        self.assertEqual(addon._state.player_data["fletching_exp"], 0)
        self.assertEqual(addon._state.player_data["current_fletch"], "arrow_shafts")
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [5.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_prayer_review_reward_and_consumed_bone_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_prayer_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Dragon bones": 1},
            "prayer_level": 1,
            "prayer_exp": 0,
            "current_prayer": "bury_dragon_bones",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Prayer"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Dragon bones"], 0)
        self.assertEqual(addon._state.player_data["prayer_exp"], 72.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data["inventory"], {"Dragon bones": 1})
        self.assertEqual(addon._state.player_data["prayer_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [72.0])

    def test_carried_mining_urn_transition_and_progress_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_urn_undo_integration")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Cracked mining urn (r)": 1},
            "carried_inventory": {"copper": {"Cracked mining urn (r)": 1}},
            "mining_level": 1,
            "mining_exp": 0.0,
            "current_ore": "copper",
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "equipment": {},
            "quests": {},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Mining"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        rolls = iter((0.0, 0.0, 1.0, 0.0))
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Copper ore"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Cracked mining urn"], 1)
        self.assertEqual(addon._state.player_data["active_urn_mining"], "mining_cracked_urn")
        self.assertEqual(addon._state.player_data["urn_progress_mining"], 17.5)
        self.assertEqual(addon._state.player_data["mining_exp"], 17.5)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_living_rock_remains_bundle_persists_and_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_living_rock_remains_integration")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {},
            "mining_level": 73,
            "mining_exp": 0.0,
            "current_ore": "living_rock_remains",
            "toolbelt": {"mining": ["rune_pickaxe"]},
            "equipment": {},
            "quests": {},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Mining"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        rolls = iter((0.0, 0.0, 1.0, 0.0))
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Living minerals"], 5)
        self.assertEqual(addon._state.player_data["mining_exp"], 25.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_bonecrusher_kill_rewards_and_counters_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_bonecrusher_undo_integration")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Bonecrusher": 1},
            "equipment": {},
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 1,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "constitution_exp": 0.0,
            "ranged_exp": 0.0,
            "magic_exp": 0.0,
            "prayer_exp": 0.0,
            "current_combat_target": "chicken",
            "carried_advanced_targets": {"chicken": True},
            "carried_layout": {"chicken": {"Bonecrusher": 1}},
            "combat_attack_style": "aggressive",
            "combat_lifepoints": 990,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {},
            "combat_current_levels": {},
            "combat_status_effects": {},
            "combat_recovery_progress": {},
            "combat_encounter": {},
            "combat_kill_counts": {},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        rolls = iter((0.0, 0.999999, 0.0) * 1000)
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        kills = addon._state.player_data["combat_kill_counts"]["chicken"]
        self.assertGreater(kills, 0)
        self.assertEqual(addon._state.player_data["prayer_exp"], 4.5 * kills)
        self.assertEqual(addon._state.player_data["prayer_bonecrusher_triggers"], kills)
        self.assertEqual(addon._state.player_data["prayer_actions_completed"], kills)
        self.assertNotIn("Bones", addon._state.player_data["inventory"])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_chaos_druid_drop_closes_the_unholy_symbol_crafting_chain(self):
        from ankiscape.core.constants import (
            COMBAT_ENEMY_DATA,
            CRAFTING_DATA,
            EQUIPMENT_DATA,
        )
        from ankiscape.logic_pure.logic_pure import (
            apply_combat_burst_pure,
            apply_crafting_pure,
        )

        enemies = dict(COMBAT_ENEMY_DATA)
        chaos_druid = dict(enemies["chaos_druid"])
        chaos_druid["stats"] = dict(
            chaos_druid["stats"], hitpoints=1, defence=1
        )
        enemies["chaos_druid"] = chaos_druid
        rolls = iter((0.0, 0.999999, 126 / 128))
        player = {
            "inventory": {"Silver bar": 1},
            "equipment": {},
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "current_combat_target": "chaos_druid",
            "combat_attack_style": "aggressive",
            "combat_auto_eat_food": [],
        }

        after_kill, combat_ok, combat_result = apply_combat_burst_pure(
            player,
            enemies,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: next(rolls, 0.5),
            stop_after_first_kill=True,
            allow_bank_run=False,
        )
        after_craft, crafting_xp, craft_ok = apply_crafting_pure(
            "silver_unstrung_emblem",
            after_kill["inventory"],
            CRAFTING_DATA,
        )

        self.assertTrue(combat_ok)
        self.assertEqual(
            combat_result["drops"], {"Bones": 1, "Unholy mould": 1}
        )
        self.assertTrue(craft_ok)
        self.assertEqual(crafting_xp, 50.0)
        self.assertEqual(after_craft["Silver bar"], 0)
        self.assertEqual(after_craft["Unholy mould"], 1)
        self.assertEqual(after_craft["Unstrung emblem"], 1)

    def test_snake_kill_closes_the_snakeskin_tanning_chain(self):
        from ankiscape.core.constants import (
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            UTILITY_ACTIVITY_DATA,
        )
        from ankiscape.logic_pure.logic_pure import (
            apply_combat_burst_pure,
            apply_utility_activity_pure,
        )

        enemies = dict(COMBAT_ENEMY_DATA)
        snake = dict(enemies["bush_snake"])
        snake["stats"] = dict(snake["stats"], hitpoints=1, defence=1)
        enemies["bush_snake"] = snake
        player = {
            "inventory": {"Coins": 15, "Machete": 1},
            "equipment": {},
            "quests": {"jungle_potion": {"completed": True}},
            "woodcutting_level": 10,
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "current_combat_target": "bush_snake",
            "combat_attack_style": "aggressive",
            "combat_auto_eat_food": [],
        }

        after_kill, combat_ok, combat_result = apply_combat_burst_pure(
            player,
            enemies,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: 0.0,
            stop_after_first_kill=True,
            allow_bank_run=False,
        )
        after_tan, _exp, tan_ok, processed = apply_utility_activity_pure(
            "tan_snakeskin",
            after_kill["inventory"],
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(combat_ok)
        self.assertEqual(combat_result["drops"], {"Bones": 1, "Snake hide": 1})
        self.assertTrue(tan_ok)
        self.assertEqual(processed, 1)
        self.assertEqual(after_tan["Snake hide"], 0)
        self.assertEqual(after_tan["Coins"], 0)
        self.assertEqual(after_tan["Snakeskin"], 1)

    def test_snake_hide_combat_review_persists_and_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_snake_hide_review_undo_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        saved_states = []
        addon.save_player_data = lambda: saved_states.append(
            copy.deepcopy(addon._state.player_data)
        )
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.player_data.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
                "current_combat_target": "bush_snake",
                "combat_attack_style": "aggressive",
                "combat_lifepoints": 990,
                "loot_value_threshold": 0,
                "woodcutting_level": 10,
            }
        )
        addon._state.player_data["inventory"]["Machete"] = 1
        addon._state.player_data["quests"]["jungle_potion"] = {
            "started": True,
            "progress": 5,
            "completed": True,
        }
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon._state.review_undo_stack.clear()
        initial = copy.deepcopy(addon._state.player_data)

        combat_runtime = sys.modules[
            f"{addon.__name__}.runtime.runtime_actions_combat"
        ]
        original_enemies = combat_runtime.COMBAT_ENEMY_DATA
        enemies = dict(original_enemies)
        snake = dict(enemies["bush_snake"])
        snake["stats"] = dict(snake["stats"], hitpoints=1, defence=1)
        enemies["bush_snake"] = snake
        original_random = addon.random.random
        combat_runtime.COMBAT_ENEMY_DATA = enemies
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            addon.random.random = original_random
            combat_runtime.COMBAT_ENEMY_DATA = original_enemies

        self.assertGreater(addon._state.player_data["inventory"]["Snake hide"], 0)
        self.assertTrue(
            any(state["inventory"].get("Snake hide", 0) > 0 for state in saved_states)
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_ectoplasmator_kill_rewards_and_counters_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_ectoplasmator_undo_integration")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Ectoplasmator": 1},
            "equipment": {},
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 1,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "constitution_exp": 0.0,
            "ranged_exp": 0.0,
            "magic_exp": 0.0,
            "prayer_exp": 0.0,
            "current_combat_target": "ghost",
            "carried_advanced_targets": {"ghost": True},
            "carried_layout": {"ghost": {"Ectoplasmator": 1}},
            "combat_attack_style": "aggressive",
            "combat_lifepoints": 990,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {},
            "combat_current_levels": {},
            "combat_status_effects": {},
            "combat_recovery_progress": {},
            "combat_encounter": {},
            "combat_kill_counts": {},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_enemy = copy.deepcopy(addon.COMBAT_ENEMY_DATA["ghost"])
        easy_ghost = copy.deepcopy(original_enemy)
        easy_ghost["stats"].update({"hitpoints": 1, "attack": 1, "strength": 1, "defence": 1})
        easy_ghost["drops"] = {"guaranteed": (), "tables": ()}
        addon.COMBAT_ENEMY_DATA["ghost"] = easy_ghost
        rolls = iter((0.0, 0.999999, 0.0) * 1000)
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random
            addon.COMBAT_ENEMY_DATA["ghost"] = original_enemy

        kills = addon._state.player_data["combat_kill_counts"]["ghost"]
        self.assertGreater(kills, 0)
        self.assertEqual(addon._state.player_data["prayer_exp"], 4.5 * kills)
        self.assertEqual(addon._state.player_data["prayer_ectoplasmator_triggers"], kills)
        self.assertEqual(addon._state.player_data["prayer_actions_completed"], kills)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_construction_review_reward_and_consumed_materials_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_construction_undo_integration")
        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Plank": 2, "Rune nails": 2},
            "construction_level": 1, "construction_exp": 0,
            "current_construction": "crude_wooden_chair",
            "house_owned": True, "house_rooms_bought": {"parlour": True, "garden": True},
            "house_servant": "", "house_built_flags": {}, "quests": {},
            "completed_achievements": [],
        }
        addon._state.current_skill = "Construction"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.999999
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random
        self.assertEqual(addon._state.player_data["inventory"]["Plank"], 0)
        self.assertEqual(addon._state.player_data["construction_exp"], 66.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data["inventory"], {"Plank": 2, "Rune nails": 2})
        self.assertEqual(addon._state.player_data["construction_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_undo_after_dragon_sq_shield_assembly_restores_both_halves(self):
        addon = _load_addon_as_package("ankiscape_dragon_sq_shield_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Shield left half": 1, "Shield right half": 1},
            "smithing_level": 60,
            "smithing_exp": 0,
            "current_smith": "repair_dragon_sq_shield",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Smithing"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Shield left half": 0, "Shield right half": 0, "Dragon sq shield": 1})
        self.assertAlmostEqual(addon._state.player_data["smithing_exp"], 70.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data["inventory"], {"Shield left half": 1, "Shield right half": 1})
        self.assertAlmostEqual(addon._state.player_data["smithing_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [70.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_coal_bag_smithing_consumption_rolls_back_on_review_undo(self):
        addon = _load_addon_as_package(
            "ankiscape_coal_bag_smithing_undo_integration"
        )

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save",
            calls["save"] + 1,
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Iron ore": 1},
            "smithing_level": 30,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "smelt_steel_bar",
            "completed_achievements": [],
            "dungeoneering": {
                "coal_bag_owned": True,
                "coal_bag_coal": 2,
            },
        }
        addon._state.current_skill = "Smithing"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        before = copy.deepcopy(addon._state.player_data)
        self.assertTrue(addon.can_smith_any())

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["inventory"]["Iron ore"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Steel bar"], 1)
        self.assertNotIn("Coal", addon._state.player_data["inventory"])
        self.assertEqual(
            addon._state.player_data["dungeoneering"]["coal_bag_coal"],
            0,
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [17.5])
        self.assertGreaterEqual(calls["save"], 2)

    def test_undo_after_coloured_feather_fletching_restores_the_same_colour(self):
        addon = _load_addon_as_package("ankiscape_coloured_feather_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Arrow shafts": 15, "Yellow feather": 15},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "headless_arrows",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Yellow feather"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Headless arrows"], 15)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data["inventory"], {"Arrow shafts": 15, "Yellow feather": 15})
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 0)
        self.assertEqual(calls["xp"], [15.0])

    def test_undo_after_long_kebbit_bolts_restores_spike_and_keeps_chisel(self):
        addon = _load_addon_as_package("ankiscape_long_kebbit_bolt_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Long kebbit spike": 1, "Chisel": 1},
            "fletching_level": 42,
            "fletching_exp": 0,
            "current_fletch": "fletch_long_kebbit_bolts",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Long kebbit spike": 0, "Chisel": 1, "Long kebbit bolts": 6},
        )
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 7.98)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Long kebbit spike": 1, "Chisel": 1},
        )
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 0)
        self.assertEqual(calls["xp"], [7.98])

    def test_successful_noncombat_review_advances_charge_and_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_charge_clock_integration")

        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 2}))
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Logs": 2},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
            "magic_charge_active": True,
            "magic_charge_ticks_remaining": 100,
        }
        initial_state = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertFalse(addon._state.player_data["magic_charge_active"])
        self.assertEqual(addon._state.player_data["magic_charge_ticks_remaining"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 30)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, initial_state)

    def test_successful_noncombat_review_applies_one_safe_combat_recovery_and_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_safe_recovery_integration")

        calls = {"save": 0, "xp": []}
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 2}))
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Logs": 2, "Shark": 30, "Bronze arrows": 10},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
            "constitution_level": 10,
            "combat_attack_style": "ranged_accurate",
            "combat_lifepoints": 20,
            "combat_special_attack_energy": 35,
            "combat_current_levels": {"attack": 2},
            "combat_recovery_progress": {},
            "combat_supply_loadout": {},
            "combat_auto_eat_food": ["Shark"],
            "equipment": {"weapon": "Shortbow"},
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 30)
        self.assertEqual(addon._state.player_data["inventory"]["Shark"], 30)
        self.assertEqual(addon._state.player_data["inventory"]["Bronze arrows"], 10)
        # One leave-combat rest review heals a ceil-share of the missing 80 LP
        # (ceil(80/3) = 27), topping the player to full over three reviews.
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 47)
        self.assertEqual(addon._state.player_data["combat_special_attack_energy"], 45)
        self.assertEqual(addon._state.player_data["combat_current_levels"], {"attack": 2})
        self.assertEqual(addon._state.player_data["combat_recovery_progress"], {"stat_drain_ticks": 50})
        self.assertEqual(
            addon._state.player_data["combat_supply_loadout"],
            {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "finishers": {}, "hazards": {}, "cannonballs": 0},
        )
        self.assertEqual(addon._state.player_data["combat_bank_run"], {"reviews_remaining": 1, "target_id": "chicken"})
        self.assertEqual(addon._state.player_data["combat_last_result"]["reason"], "combat_bank_run")
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Logs": 2, "Shark": 30, "Bronze arrows": 10})
        self.assertEqual(addon._state.player_data["fletching_exp"], 0)
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 20)
        self.assertEqual(addon._state.player_data["combat_special_attack_energy"], 35)
        self.assertEqual(addon._state.player_data["combat_current_levels"], {"attack": 2})
        self.assertEqual(addon._state.player_data["combat_recovery_progress"], {})
        self.assertEqual(addon._state.player_data["combat_supply_loadout"], {})

    def test_death_office_reclaim_callback_consumes_coins_and_saves(self):
        addon = _load_addon_as_package("ankiscape_death_office_reclaim_integration")

        calls = {"save": 0, "errors": [], "achievement_coins": []}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.check_achievements = lambda data: calls["achievement_coins"].append(data["inventory"]["Coins"])
        addon._refresh_skill_availability = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["errors"].append((title, message))

        addon._state.player_data = {
            "inventory": {"Coins": 150},
            "death_office": {"items": ["Bronze sword"], "source": "combat_stacked_grave"},
            "combat_grave": {},
        }

        self.assertTrue(addon.on_reclaim_death_office())
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 50)
        self.assertEqual(addon._state.player_data["inventory"]["Bronze sword"], 1)
        self.assertEqual(addon._state.player_data["death_office"], {})
        self.assertEqual(calls["achievement_coins"], [50])

    def test_equipping_a_melee_weapon_returns_loaded_magic_runes_to_bank(self):
        addon = _load_addon_as_package("ankiscape_combat_weapon_loadout")

        calls = {"save": 0, "hud": 0, "refresh": 0}
        addon.save_player_data = lambda: calls.__setitem__(
            "save", calls["save"] + 1
        )
        addon.check_achievements = lambda _data: None
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__(
            "hud", calls["hud"] + 1
        )
        addon._refresh_skill_availability = lambda: calls.__setitem__(
            "refresh", calls["refresh"] + 1
        )
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "inventory": {
                "Rune scimitar": 1,
                "Air rune": 0,
                "Mind rune": 0,
            },
            "equipment": {"weapon": "Staff"},
            "attack_level": 40,
            "magic_level": 99,
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "wind_strike",
            "combat_pack_mode": "max_output",
            "combat_vengeance": True,
            "combat_supply_loadout": {
                "runes": {"Air rune": 5, "Mind rune": 5}
            },
            "combat_encounter": {},
            "constitution_level": 10,
        }

        self.assertTrue(addon.on_equip_item("Rune scimitar"))

        self.assertEqual(
            addon._state.player_data["equipment"], {"weapon": "Rune scimitar"}
        )
        self.assertEqual(
            addon._state.player_data["combat_supply_loadout"]["runes"], {}
        )
        self.assertEqual(addon._state.player_data["inventory"]["Air rune"], 5)
        self.assertEqual(addon._state.player_data["inventory"]["Mind rune"], 5)
        self.assertEqual(addon._state.player_data["inventory"]["Staff"], 1)
        self.assertEqual(calls, {"save": 1, "hud": 1, "refresh": 1})

    def test_combat_loadout_menu_callbacks_refill_and_unload_supplies(self):
        addon = _load_addon_as_package("ankiscape_combat_loadout_callbacks")

        calls = {
            "save": 0,
            "hud": 0,
            "refresh": 0,
            "achievement_runes": [],
            "activity": [],
        }
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.check_achievements = lambda data: calls["achievement_runes"].append(
            data["inventory"].get("Air rune", 0) + data["inventory"].get("Mind rune", 0)
        )
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon._refresh_skill_availability = lambda: calls.__setitem__("refresh", calls["refresh"] + 1)
        addon._show_activity_gain = lambda message: calls["activity"].append(message)
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "inventory": {"Shark": 30, "Antipoison (2)": 1, "Air rune": 5, "Mind rune": 5, "Fire rune": 5},
            "equipment": {"weapon": "Staff of fire"},
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "fire_strike",
            "combat_auto_eat_food": ["Shark"],
            "combat_supply_loadout": {},
            "combat_pack_mode": "max_safety",  # fill the 28-slot budget with food
            "combat_encounter": {},
            "constitution_level": 10,
        }

        self.assertTrue(addon.on_do_bank_run_now())
        self.assertEqual(
            addon._state.player_data["combat_bank_run"],
            {"reviews_remaining": 2, "target_id": "chicken"},
        )
        addon._state.player_data["combat_bank_run"] = {}
        addon._state.current_skill = "Mining"
        addon._state.player_data["current_ore"] = "coal"
        self.assertTrue(addon.on_do_bank_run_now())
        self.assertEqual(
            addon._state.player_data["skilling_bank_run_requested"], "coal"
        )
        addon._state.player_data.pop("skilling_bank_run_requested", None)
        registry = sys.modules[f"{addon.__name__}.core.skill_registry"]
        for skill in registry.CURRENT_SKILLS:
            if not skill.participates_in_review:
                continue
            if skill.current_target_key:
                addon._state.player_data[skill.current_target_key] = skill.default_target
            addon._state.current_skill = skill.display_name
            self.assertTrue(addon.on_do_bank_run_now(), skill.display_name)
            if skill.review_handler_key == "combat" or skill.id == "slayer":
                self.assertIn("combat_bank_run", addon._state.player_data)
                addon._state.player_data["combat_bank_run"] = {}
            elif skill.review_handler_key in addon.runtime_actions._BANK_RUN_TARGET_KEYS:
                target_key = addon.runtime_actions._BANK_RUN_TARGET_KEYS[
                    skill.review_handler_key
                ]
                expected_target = (
                    addon._state.player_data.get(target_key)
                    if target_key
                    else None
                ) or skill.review_handler_key
                self.assertEqual(
                    addon._state.player_data["skilling_bank_run_requested"],
                    expected_target,
                )
                addon._state.player_data.pop("skilling_bank_run_requested", None)
        for surface in ("Activities", "Utilities", "Quests"):
            addon._state.current_skill = surface
            self.assertTrue(addon.on_do_bank_run_now(), surface)
            self.assertIn("skilling_bank_run_requested", addon._state.player_data)
            addon._state.player_data.pop("skilling_bank_run_requested", None)
        addon._state.current_skill = "Farming"
        self.assertTrue(addon.on_do_bank_run_now())
        self.assertNotIn("skilling_bank_run_requested", addon._state.player_data)
        self.assertEqual(calls["activity"], ["Bank run — arrived and ready"])
        addon._state.current_skill = "Slayer"
        self.assertTrue(addon.on_do_bank_run_now())
        self.assertEqual(
            addon._state.player_data["combat_bank_run"],
            {"reviews_remaining": 2, "target_id": "chicken"},
        )
        addon._state.player_data["combat_bank_run"] = {}
        addon._state.current_skill = "Combat"

        self.assertTrue(addon.on_set_combat_auto_eat_threshold(65))
        self.assertEqual(addon._state.player_data["combat_auto_eat_threshold_percent"], 65)
        self.assertTrue(addon.on_set_combat_auto_eat_food("Lobster"))
        self.assertEqual(addon._state.player_data["combat_auto_eat_food"][0], "Lobster")

        addon._state.player_data["combat_auto_eat_food"] = ["Shark"]
        self.assertTrue(addon.on_refill_combat_loadout())
        self.assertEqual(addon._state.player_data["combat_supply_loadout"]["food"], {"Shark": 20})
        self.assertEqual(addon._state.player_data["combat_supply_loadout"]["potions"], {"Antipoison (2)": 1})
        self.assertEqual(addon._state.player_data["combat_supply_loadout"]["runes"], {"Air rune": 5, "Mind rune": 5})
        self.assertEqual(addon._state.player_data["inventory"]["Shark"], 10)
        self.assertEqual(addon._state.player_data["inventory"]["Antipoison (2)"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Fire rune"], 5)

        self.assertTrue(addon.on_set_combat_pack_mode("max_output"))
        self.assertEqual(
            addon._state.player_data["combat_supply_loadout"]["food"], {"Shark": 8}
        )
        self.assertEqual(calls["achievement_runes"], [0])

        self.assertTrue(addon.on_unload_combat_loadout())
        self.assertEqual(
            addon._state.player_data["combat_supply_loadout"],
            {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "finishers": {}, "hazards": {}, "cannonballs": 0},
        )
        self.assertEqual(addon._state.player_data["inventory"]["Shark"], 30)
        self.assertEqual(addon._state.player_data["inventory"]["Antipoison (2)"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Air rune"], 5)
        self.assertEqual(addon._state.player_data["inventory"]["Mind rune"], 5)
        self.assertEqual(calls["achievement_runes"], [0, 10])
        self.assertGreaterEqual(calls["save"], 5)
        self.assertGreaterEqual(calls["hud"], 4)
        self.assertGreaterEqual(calls["refresh"], 4)

    def test_firemaking_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_firemaking_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        achievements = sys.modules[f"{addon.__name__}.core.constants"].ACHIEVEMENTS
        def complete_first_fire(data):
            if achievements["First Fire"]["condition"](data):
                data["completed_achievements"].append("First Fire")
        addon.check_achievements = complete_first_fire
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Firemaking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"], {"Logs": 0, "Ashes": 1})
        self.assertAlmostEqual(addon._state.player_data["firemaking_exp"], 40.0)
        self.assertEqual(
            addon._state.player_data["achievement_progress"]["skills"]["firemaking"]["outputs"],
            {"Ashes": 1},
        )
        self.assertIn("First Fire", addon._state.player_data["completed_achievements"])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Logs": 1})
        self.assertEqual(addon._state.player_data["firemaking_exp"], 0)
        self.assertNotIn("achievement_progress", addon._state.player_data)
        self.assertEqual(addon._state.player_data["completed_achievements"], [])
        self.assertEqual(addon._state.player_data["current_firemaking"], "logs")
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [40.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_fishing_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_fishing_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Feather": 1},
            "fishing_level": 48,
            "fishing_exp": 0,
            "strength_level": 15,
            "strength_exp": 0,
            "agility_level": 15,
            "agility_exp": 0,
            "current_fishing": "catch_leaping_fish",
            "completed_achievements": [],
            "unlocked_abilities": ["barbarian_fishing"],
        }
        addon._state.current_skill = "Fishing"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"], {"Feather": 0, "Leaping trout": 1})
        self.assertAlmostEqual(addon._state.player_data["fishing_exp"], 50.0)
        self.assertAlmostEqual(addon._state.player_data["strength_exp"], 5.0)
        self.assertAlmostEqual(addon._state.player_data["agility_exp"], 5.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Feather": 1})
        self.assertEqual(addon._state.player_data["fishing_exp"], 0)
        self.assertEqual(addon._state.player_data["strength_exp"], 0)
        self.assertEqual(addon._state.player_data["agility_exp"], 0)
        self.assertEqual(addon._state.player_data["current_fishing"], "catch_leaping_fish")
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [50.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_eucalyptus_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_eucalyptus_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        initial = {
            "inventory": {},
            "woodcutting_level": 58,
            "woodcutting_exp": 0.0,
            "current_tree": "eucalyptus",
            "toolbelt": {"woodcutting": ["rune_hatchet"]},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Woodcutting"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Eucalyptus logs"], 1)
        self.assertEqual(addon._state.player_data["woodcutting_exp"], 165.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [165.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_seaweed_cooking_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_seaweed_cooking_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Seaweed": 1},
            "cooking_level": 1,
            "cooking_exp": 0,
            "current_cooking": "burn_seaweed",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 1.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"], {"Seaweed": 0, "Soda ash": 1})
        self.assertAlmostEqual(addon._state.player_data["cooking_exp"], 1.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Seaweed": 1})
        self.assertEqual(addon._state.player_data["cooking_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [1.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_cooking_gauntlet_auto_equip_and_success_roll_back_with_review(self):
        addon = _load_addon_as_package(
            "ankiscape_cooking_gauntlets_review_undo_integration"
        )
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Raw shark": 1, "Cooking gauntlets": 1},
            "equipment": {"hands": "Leather gloves"},
            "cooking_level": 94,
            "cooking_exp": 0,
            "current_cooking": "cook_shark",
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.999
        try:
            addon.on_answer_card(
                _FakeReviewer(), 4, lambda _self, _ease: "answered"
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(
            addon._state.player_data["equipment"]["hands"], "Cooking gauntlets"
        )
        self.assertEqual(addon._state.player_data["inventory"]["Leather gloves"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Shark"], 1)
        self.assertEqual(addon._state.player_data["cooking_exp"], 210.0)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_lava_eel_cooking_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_lava_eel_cooking_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Raw lava eel": 1},
            "cooking_level": 53,
            "cooking_exp": 0,
            "current_cooking": "cook_lava_eel",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Raw lava eel": 0, "Lava eel": 1})
        self.assertAlmostEqual(addon._state.player_data["cooking_exp"], 30.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Raw lava eel": 1})
        self.assertEqual(addon._state.player_data["cooking_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [30.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_bad_wine_review_outcome_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_bad_wine_undo_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: self.fail(f"bad wine awarded {exp} XP")
        addon._show_activity_gain = lambda _text: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Grapes": 1, "Jug of water": 1},
            "cooking_level": 35,
            "cooking_exp": 0.0,
            "current_cooking": "make_wine",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.61
        try:
            addon.on_answer_card(
                _FakeReviewer(), 4, lambda _self, _ease: "answered"
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Grapes": 0, "Jug of water": 0, "Jug of bad wine": 1},
        )
        self.assertEqual(addon._state.player_data["cooking_exp"], 0.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_barley_malt_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_barley_malt_undo_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: self.fail(f"barley malt awarded {exp} XP")
        addon._show_activity_gain = lambda _text: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Barley": 1},
            "cooking_level": 1,
            "cooking_exp": 0.0,
            "current_cooking": "malt_barley",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Barley": 0, "Barley malt": 1},
        )
        self.assertEqual(addon._state.player_data["cooking_exp"], 0.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_poison_karambwan_burn_rolls_back_on_review_undo(self):
        addon = _load_addon_as_package("ankiscape_poison_karambwan_undo_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: self.fail(f"burnt karambwan awarded {exp} XP")
        addon._show_activity_gain = lambda _text: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Raw karambwan": 1},
            "cooking_level": 1,
            "cooking_exp": 0.0,
            "current_cooking": "cook_poison_karambwan",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
            "quests": {
                "tai_bwo_wannai_trio": {
                    "started": True,
                    "progress": 1,
                    "completed": False,
                }
            },
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 1.0
        try:
            addon.on_answer_card(
                _FakeReviewer(), 4, lambda _self, _ease: "answered"
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Raw karambwan": 0, "Burnt karambwan": 1},
        )
        self.assertEqual(addon._state.player_data["cooking_exp"], 0.0)
        self.assertEqual(addon._state.player_data["cooking_burn_count"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_cheese_wheel_slice_all_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_cheese_wheel_undo_integration")

        calls = {"save": 0, "xp": [], "activity": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._show_activity_gain = lambda text: calls["activity"].append(text)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Cheese wheel": 1},
            "cooking_level": 48,
            "cooking_exp": 0.0,
            "current_cooking": "slice_cheese_wheel",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Cheese wheel": 0, "Cheese": 5},
        )
        self.assertEqual(addon._state.player_data["cooking_exp"], 20.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)
        self.assertEqual(calls["activity"], ["+5 Cheese"])

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Cheese wheel": 1})
        self.assertEqual(addon._state.player_data["cooking_exp"], 0.0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [20.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_super_prayer_mixing_uses_wyvern_bonemeal_and_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_super_prayer_mixing_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        ingredients = {
            "Prayer potion (3)": 1,
            "Wyvern bonemeal": 1,
            "Bonemeal": 5,
        }
        addon._state.player_data = {
            "inventory": ingredients.copy(),
            "herblore_level": 94,
            "herblore_exp": 0,
            "current_herblore": "finished_super_prayer",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Herblore"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Prayer potion (3)"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Wyvern bonemeal"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Bonemeal"], 5)
        self.assertEqual(addon._state.player_data["inventory"]["Super prayer (3)"], 1)
        self.assertEqual(addon._state.player_data["herblore_exp"], 270.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], ingredients)
        self.assertEqual(addon._state.player_data["herblore_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [270.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_overload_mixing_review_reward_and_vials_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_overload_mixing_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        ingredients = {
            "Extreme attack (3)": 1,
            "Extreme strength (3)": 1,
            "Extreme defence (3)": 1,
            "Extreme magic (3)": 1,
            "Extreme ranging (3)": 1,
            "Clean torstol": 1,
        }
        addon._state.player_data = {
            "inventory": ingredients.copy(),
            "herblore_level": 96,
            "herblore_exp": 0,
            "current_herblore": "finished_overload",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Herblore"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Overload (3)"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Vial"], 4)
        self.assertEqual(addon._state.player_data["herblore_exp"], 1000.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], ingredients)
        self.assertEqual(addon._state.player_data["herblore_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [1000.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_shrink_me_quick_mixing_rolls_back_atomically_on_review_undo(self):
        addon = _load_addon_as_package("ankiscape_shrink_me_quick_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        ingredients = {
            "Tarromin potion (unf)": 1,
            "Shrunk ogleroot": 1,
        }
        addon._state.player_data = {
            "inventory": ingredients.copy(),
            "herblore_level": 52,
            "herblore_exp": 0,
            "current_herblore": "finished_shrink_me_quick",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Herblore"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Tarromin potion (unf)"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Shrunk ogleroot"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Shrink-me-quick"], 1)
        self.assertEqual(addon._state.player_data["herblore_exp"], 6.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], ingredients)
        self.assertEqual(addon._state.player_data["herblore_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [6.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_cannonball_review_reward_and_mould_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_cannonball_smithing_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Steel bar": 1, "Ammo mould": 1},
            "smithing_level": 35,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "forge_cannonballs",
            "quests": {"dwarf_cannon": {"completed": True}},
            "completed_achievements": [],
        }
        addon._state.current_skill = "Smithing"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Steel bar": 0, "Ammo mould": 1, "Cannonball": 4})
        self.assertEqual(addon._state.player_data["smithing_exp"], 25.6)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Steel bar": 1, "Ammo mould": 1})
        self.assertEqual(addon._state.player_data["smithing_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [25.6])

    def test_utility_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_utility_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Anchovies": 2},
            "crafting_exp": 0,
            "current_utility": "grind_anchovies",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Anchovies": 0, "Anchovy paste": 2})
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Anchovies": 2})
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_sorceress_garden_trip_and_cross_skill_reward_roll_back_together(self):
        addon = _load_addon_as_package("ankiscape_garden_undo_integration")
        garden_logic = sys.modules[
            "ankiscape_garden_undo_integration.logic.sorceress_garden_logic"
        ]

        calls = {"save": 0}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save", calls["save"] + 1
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _text: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        garden_state = garden_logic.default_sorceress_garden_state_pure()
        garden_state["introduced"] = True
        addon._state.player_data = {
            "inventory": {},
            "current_utility": "sorceress_garden",
            "farming_level": 1,
            "farming_exp": 0.0,
            "thieving_level": 1,
            "thieving_exp": 0.0,
            "quests": {
                "diamond_in_the_rough": {
                    "completed": True,
                }
            },
            "sorceress_garden": garden_state,
            "completed_achievements": [],
        }
        initial = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["inventory"]["Winter sq'irk"], 1)
        self.assertEqual(addon._state.player_data["farming_exp"], 30.0)
        self.assertEqual(
            addon._state.player_data["sorceress_garden"]["successful_trips"],
            1,
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(
                    study_queues=True,
                    card=True,
                ),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_penguin_spy_and_points_roll_back_as_one_review(self):
        addon = _load_addon_as_package("ankiscape_penguin_undo_integration")
        penguin_logic = sys.modules[
            "ankiscape_penguin_undo_integration.logic.penguin_hide_and_seek_logic"
        ]

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save", calls["save"] + 1
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        state = penguin_logic.default_penguin_state_pure()
        player = {
            "inventory": {},
            "equipment": {},
            "quests": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "penguin_hide_and_seek",
            "penguin_hide_and_seek": state,
            "completed_achievements": [],
        }
        spawn_id = penguin_logic.penguin_roster_pure(player)[0]["id"]
        player, ok, _ = penguin_logic.apply_penguin_command_pure(
            player,
            "select_spy",
            {"spawn_id": spawn_id},
        )
        self.assertTrue(ok)
        addon._state.player_data = player
        initial = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["penguin_hide_and_seek"]["points"], 1)
        self.assertIn(
            spawn_id,
            addon._state.player_data["penguin_hide_and_seek"]["spotted_ids"],
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_livid_farm_cycle_and_cross_skill_xp_roll_back_as_one_review(self):
        addon = _load_addon_as_package("ankiscape_livid_farm_undo_integration")

        calls = {"save": 0}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save",
            calls["save"] + 1,
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {
                "Astral rune": 1_000,
                "Nature rune": 1_000,
                "Law rune": 1_000,
                "Earth rune": 1_000,
                "Water rune": 1_000,
            },
            "equipment": {},
            "quests": {"lunar_diplomacy": {"completed": True}},
            "magic_level": 99,
            "agility_level": 60,
            "crafting_level": 60,
            "farming_level": 60,
            "construction_level": 50,
            "magic_exp": 0.0,
            "agility_exp": 0.0,
            "crafting_exp": 0.0,
            "farming_exp": 0.0,
            "construction_exp": 0.0,
            "current_utility": "livid_farm",
            "completed_achievements": [],
        }
        before = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["livid_farm"]["cycles_completed"], 1)
        self.assertEqual(addon._state.player_data["livid_farm"]["produce_points"], 1_580)
        self.assertAlmostEqual(addon._state.player_data["magic_exp"], 3_737.0)
        self.assertAlmostEqual(addon._state.player_data["agility_exp"], 509.1)
        self.assertAlmostEqual(addon._state.player_data["crafting_exp"], 1_080.0)
        self.assertAlmostEqual(addon._state.player_data["farming_exp"], 2_754.0)
        self.assertAlmostEqual(addon._state.player_data["construction_exp"], 546.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_livid_more_planks_world_tick_advances_on_again_and_undo_restores_it(self):
        addon = _load_addon_as_package(
            "ankiscape_livid_wish_world_tick_integration"
        )
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        initial = {
            "inventory": {},
            "livid_farm": {
                "borrowed_power_claimed": True,
                "more_planks_reviews_remaining": 1,
            },
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            1,
            lambda _self, _ease: "answered",
        )

        state = addon._state.player_data["livid_farm"]
        self.assertEqual(state["more_planks_reviews_remaining"], 0)
        self.assertTrue(state["more_planks_active_this_review"])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_livid_wish_purchase_uses_direct_action_undo(self):
        addon = _load_addon_as_package(
            "ankiscape_livid_wish_direct_action_integration"
        )
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Utility / Activities"
        initial = {
            "inventory": {},
            "livid_farm": {
                "borrowed_power_claimed": True,
                "produce_points": 18_000,
            },
        }
        addon._state.player_data = copy.deepcopy(initial)

        result = addon.on_livid_farm_wish("gimme_herbs")

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Grimy kwuarm"], 3)
        self.assertEqual(addon._state.player_data["livid_farm"]["produce_points"], 0)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_livid_protection_wish_flows_into_the_farming_action_surface(self):
        addon = _load_addon_as_package(
            "ankiscape_livid_protection_farming_integration"
        )
        farming_data = sys.modules[f"{addon.__name__}.data.farming_data"]
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Utility / Activities"
        state = {
            "inventory": {
                "Rake": 1,
                "Spade": 1,
                "Oak sapling": 1,
            },
            "farming_level": 99,
            "farming_exp": 0.0,
            "smithing_level": 1,
            "livid_farm": {
                "borrowed_power_claimed": True,
                "produce_points": 37_000,
            },
        }
        state.update(farming_logic.default_farming_state_pure())
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {
                "kind": "plant",
                "patch_id": "lumbridge_tree",
                "crop_id": "oak",
            },
        )
        self.assertTrue(ok)
        addon._state.player_data = state

        purchased = addon.on_livid_farm_wish("protect_patch")
        self.assertTrue(purchased["ok"])
        self.assertEqual(
            addon._state.player_data["inventory"][
                farming_data.LIVID_FARM_PROTECTION_SCROLL
            ],
            1,
        )

        addon._on_main_menu(initial_skill="Farming")
        activated = captured["on_farming_action"](
            "activate_livid_protection",
            {"patch_id": "lumbridge_tree"},
        )

        self.assertTrue(activated["ok"])
        self.assertTrue(
            addon._state.player_data["farm_patches"]["lumbridge_tree"][
                "livid_protected"
            ]
        )
        self.assertEqual(
            addon._state.player_data["farm_livid_protection_uses_remaining"],
            9,
        )
        self.assertNotIn(
            farming_data.LIVID_FARM_PROTECTION_SCROLL,
            addon._state.player_data["inventory"],
        )

    def test_arcane_capacitor_charge_uses_direct_action_undo(self):
        from ankiscape.data.livid_farm_data import (
            ARCANE_CAPACITOR_CHARGED,
            ARCANE_CAPACITOR_UNCHARGED,
        )

        addon = _load_addon_as_package(
            "ankiscape_arcane_capacitor_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Utility / Activities"
        initial = {
            "inventory": {
                ARCANE_CAPACITOR_UNCHARGED: 1,
                "Air rune": 1_000,
                "Earth rune": 1_000,
                "Law rune": 1_000,
            },
            "equipment": {},
            "magic_level": 99,
            "quests": {"lunar_diplomacy": {"completed": True}},
            "livid_farm": {"borrowed_power_claimed": True},
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_livid_farm_command"](
            "charge_capacitor",
            {"spell_id": "teleport_to_house"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["inventory"][ARCANE_CAPACITOR_CHARGED],
            1,
        )
        self.assertEqual(
            addon._state.player_data["livid_farm"]["arcane_capacitor_charges"],
            1_000,
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_leather_thread_consumption_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_leather_thread_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Leather": 1, "Thread": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "leather_leather_gloves",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Crafting"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        self.addCleanup(setattr, addon.random, "random", original_random)

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Leather": 0, "Thread": 0, "Leather gloves": 1})
        self.assertAlmostEqual(addon._state.player_data["crafting_exp"], 13.8)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Leather": 1, "Thread": 1})
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_glassblowing_pipe_requirement_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_glassblowing_pipe_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Molten glass": 1, "Glassblowing pipe": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "glass_beer_glass",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Crafting"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Molten glass": 0, "Glassblowing pipe": 1, "Beer glass": 1})
        self.assertAlmostEqual(addon._state.player_data["crafting_exp"], 17.5)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Molten glass": 1, "Glassblowing pipe": 1})
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_light_source_review_action_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_light_source_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Sapphire lantern (unlit)": 1},
            "firemaking_level": 49,
            "current_utility": "light_sapphire_lantern",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Sapphire lantern (unlit)": 0, "Sapphire lantern (lit)": 1})
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Sapphire lantern (unlit)": 1})
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_lamp_oil_preparation_review_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_lamp_oil_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Bullseye lantern (empty)": 1, "Swamp tar": 1},
            "current_utility": "fill_bullseye_lantern",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Bullseye lantern (empty)": 0, "Swamp tar": 0, "Bullseye lantern (unlit)": 1},
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Bullseye lantern (empty)": 1, "Swamp tar": 1},
        )
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_tanning_review_batches_28_hides_and_rolls_back_on_undo(self):
        # Review-paced conversion: one answered card tans up to 28 hides for
        # 28 coins (1 coin per hide), and Anki undo restores both.
        addon = _load_addon_as_package("ankiscape_tanning_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Cowhide": 30, "Coins": 100},
            "crafting_exp": 0,
            "current_utility": "tan_soft_leather",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Leather"], 28)
        self.assertEqual(addon._state.player_data["inventory"]["Cowhide"], 2)
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 72)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Cowhide": 30, "Coins": 100})
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_source_gathering_actions_roll_back_on_answer_undo(self):
        cases = (
            ("gather_wool", "Wool", 28),
            ("gather_swamp_toads", "Swamp toad", 28),
            ("gather_blue_dragon_scales", "Blue dragon scale", 7),
            ("gather_potato_cacti", "Potato cactus", 3),
            ("gather_black_mushrooms", "Black mushroom", 1),
            ("gather_doogle_leaves", "Doogle leaves", 2),
            ("gather_goblin_mail", "Goblin mail", 3),
        )
        for action_id, output_item, output_qty in cases:
            with self.subTest(action_id=action_id):
                addon = _load_addon_as_package(
                    f"ankiscape_{action_id}_undo_integration"
                )
                calls = {"save": 0}
                addon.check_achievements = lambda _data: None
                addon.save_player_data = lambda: calls.__setitem__(
                    "save",
                    calls["save"] + 1,
                )
                addon.update_review_hud = lambda _data, _skill: None
                addon._refresh_skill_availability = lambda: None
                addon.show_error_message = lambda _title, message: self.fail(message)
                addon._state.player_data = {
                    "inventory": {},
                    "crafting_exp": 0,
                    "current_utility": action_id,
                    "completed_achievements": [],
                }
                addon._state.current_skill = "Utility / Activities"
                addon._state.card_turned = True
                addon._state.answer_shown = True
                addon._state.exp_awarded = False

                addon.on_answer_card(
                    _FakeReviewer(),
                    4,
                    lambda _self, _ease: "answered",
                )

                self.assertEqual(addon._state.player_data["inventory"], {output_item: output_qty})
                self.assertEqual(addon._state.player_data["crafting_exp"], 0)
                self.assertEqual(len(addon._state.review_undo_stack), 1)

                changes = types.SimpleNamespace(
                    operation="Answer Card",
                    changes=types.SimpleNamespace(study_queues=True, card=True),
                )
                addon._on_state_did_undo(changes)

                self.assertEqual(addon._state.player_data["inventory"], {})
                self.assertEqual(addon._state.player_data["crafting_exp"], 0)
                self.assertEqual(addon._state.review_undo_stack, [])
                self.assertGreaterEqual(calls["save"], 2)

    def test_goblin_diplomacy_processing_actions_roll_back_on_answer_undo(self):
        cases = (
            ("aggie_make_red_dye", {"Redberries": 3, "Coins": 5}, "Red dye"),
            ("aggie_make_yellow_dye", {"Onion": 2, "Coins": 5}, "Yellow dye"),
            ("mix_orange_dye", {"Red dye": 1, "Yellow dye": 1}, "Orange dye"),
            ("aggie_make_blue_dye", {"Woad leaf": 2, "Coins": 5}, "Blue dye"),
            ("dye_goblin_mail_orange", {"Goblin mail": 1, "Orange dye": 1}, "Orange goblin mail"),
            ("dye_goblin_mail_blue", {"Goblin mail": 1, "Blue dye": 1}, "Blue goblin mail"),
        )
        for action_id, starting_inventory, output_item in cases:
            with self.subTest(action_id=action_id):
                addon = _load_addon_as_package(
                    f"ankiscape_{action_id}_undo_integration"
                )
                calls = {"save": 0}
                addon.check_achievements = lambda _data: None
                addon.save_player_data = lambda: calls.__setitem__(
                    "save",
                    calls["save"] + 1,
                )
                addon.update_review_hud = lambda _data, _skill: None
                addon._refresh_skill_availability = lambda: None
                addon.show_error_message = lambda _title, message: self.fail(message)
                addon._state.player_data = {
                    "inventory": dict(starting_inventory),
                    "crafting_exp": 0,
                    "current_utility": action_id,
                    "completed_achievements": [],
                }
                addon._state.current_skill = "Utility / Activities"
                addon._state.card_turned = True
                addon._state.answer_shown = True
                addon._state.exp_awarded = False

                addon.on_answer_card(
                    _FakeReviewer(),
                    4,
                    lambda _self, _ease: "answered",
                )

                self.assertEqual(addon._state.player_data["inventory"][output_item], 1)
                for item_name in starting_inventory:
                    self.assertEqual(addon._state.player_data["inventory"][item_name], 0)
                self.assertEqual(addon._state.player_data["crafting_exp"], 0)
                self.assertEqual(len(addon._state.review_undo_stack), 1)

                changes = types.SimpleNamespace(
                    operation="Answer Card",
                    changes=types.SimpleNamespace(study_queues=True, card=True),
                )
                addon._on_state_did_undo(changes)

                self.assertEqual(addon._state.player_data["inventory"], starting_inventory)
                self.assertEqual(addon._state.player_data["crafting_exp"], 0)
                self.assertEqual(addon._state.review_undo_stack, [])
                self.assertGreaterEqual(calls["save"], 2)

    def test_crystal_chest_answer_and_undo_are_atomic(self):
        addon = _load_addon_as_package("ankiscape_crystal_chest_undo_integration")
        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Crystal key": 1},
            "equipment": {},
            "current_utility": "open_crystal_chest",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        addon.random.random = lambda: 0.4
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Crystal key"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Uncut dragonstone"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Crystal key": 1})
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_cure_plant_runtime_cast_and_answer_undo_are_atomic(self):
        addon = _load_addon_as_package("ankiscape_cure_plant_undo_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda xp: calls["xp"].append(xp)
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {
                "Astral rune": 1,
                "Earth rune": 8,
                "Rake": 1,
                "Seed dibber": 1,
                "Potato seed": 3,
            },
            "magic_level": 99,
            "magic_exp": 0.0,
            "current_magic": "cure_plant",
            "quests": {"lunar_diplomacy": {"completed": True}},
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(ok)
        state["farm_patches"]["falador_allotment_north"]["diseased"] = True
        state["farming_spell_patch"] = "falador_allotment_north"
        before = copy.deepcopy(state)
        addon._state.player_data = state
        addon._state.current_skill = "Magic"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertFalse(addon._state.player_data["farm_patches"]["falador_allotment_north"]["diseased"])
        self.assertEqual(addon._state.player_data["inventory"]["Astral rune"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Earth rune"], 0)
        self.assertEqual(addon._state.player_data["magic_exp"], 60.0)
        self.assertEqual(calls["save"], 1)
        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before)

    def test_livid_remote_farm_cast_cures_all_patches_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_livid_remote_farm_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        calls = {"save": 0, "gains": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {
                "Astral rune": 2,
                "Earth rune": 2,
                "Nature rune": 3,
            },
            "magic_level": 99,
            "magic_exp": 0.0,
            "current_magic": "remote_farm",
            "quests": {"lunar_diplomacy": {"completed": True}},
            "livid_farm": {"unlocked_spells": ["remote_farm"]},
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        for patch_id in ("falador_allotment_north", "falador_allotment_south"):
            state["farm_patches"][patch_id].update(
                {
                    "crop_id": "potato",
                    "last_crop_id": "potato",
                    "diseased": True,
                }
            )
        before = copy.deepcopy(state)
        addon._state.player_data = state
        addon._state.current_skill = "Magic"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertFalse(
            addon._state.player_data["farm_patches"]["falador_allotment_north"][
                "diseased"
            ]
        )
        self.assertFalse(
            addon._state.player_data["farm_patches"]["falador_allotment_south"][
                "diseased"
            ]
        )
        self.assertEqual(addon._state.player_data["magic_exp"], 79.0)
        self.assertEqual(
            calls["gains"],
            ["Remote Farm checked 2 active patches and cured 2."],
        )
        self.assertEqual(calls["save"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, before)

    def test_livid_consumer_block_message_is_player_facing(self):
        addon = _load_addon_as_package("ankiscape_livid_block_message_integration")
        calls = {"errors": []}
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = (
            lambda title, message: calls["errors"].append((title, message))
        )
        addon._state.player_data = {
            "inventory": {
                "Astral rune": 3,
                "Blood rune": 3,
                "Body rune": 10,
            },
            "magic_level": 99,
            "current_magic": "disruption_shield",
            "quests": {"lunar_diplomacy": {"completed": True}},
            "livid_farm": {"unlocked_spells": ["disruption_shield"]},
        }
        addon._state.current_skill = "Magic"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(
            calls["errors"],
            [
                (
                    "Magic target unavailable",
                    "Disruption Shield is unavailable: Requires PvP combat. "
                    "Magic has been switched off.",
                )
            ],
        )

    def test_queued_farming_dig_up_preempts_one_review_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_farming_dig_up_undo_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {
                "Rake": 1,
                "Seed dibber": 1,
                "Spade": 1,
                "Redberry seed": 1,
            },
            "farming_level": 99,
            "farming_exp": 0.0,
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "agility_level": 99,
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "champions_bush", "crop_id": "redberry"},
        )
        self.assertTrue(ok)
        state, _ = farming_logic.advance_farm_clock_pure(state, 17, lambda: 1.0)
        state, step_id, _ = farming_logic.add_farm_queue_step_pure(
            state, "dig_up", "champions_bush"
        )
        self.assertIsNotNone(step_id)
        before = copy.deepcopy(state)
        addon._state.player_data = state
        addon._state.current_skill = "Mining"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertIsNone(addon._state.player_data["farm_patches"]["champions_bush"]["crop_id"])
        self.assertEqual(addon._state.player_data["farming_counters"]["dig_ups"], 1)
        self.assertEqual(addon._state.player_data["farm_queue"], [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before)

    def test_queued_white_tree_harvest_preempts_one_review_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_white_tree_undo_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {},
            "farming_level": 25,
            "farming_exp": 0.0,
            "quests": {"garden_of_tranquillity": {"completed": True}},
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state, step_ids = farming_logic.queue_full_run_pure(state)
        self.assertEqual(len(step_ids), 1)
        before = copy.deepcopy(state)
        addon._state.player_data = state
        addon._state.current_skill = "Mining"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["White tree fruit"], 4)
        self.assertEqual(addon._state.player_data["farming_exp"], 48.0)
        self.assertEqual(
            addon._state.player_data["farm_patches"]["varrock_white_tree"]["produce_count"],
            0,
        )
        self.assertEqual(addon._state.player_data["farm_queue"], [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before)

    def test_jade_branch_from_again_waits_for_a_successful_review_and_undoes(self):
        addon = _load_addon_as_package("ankiscape_jade_vine_queue_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {"Secateurs": 1},
            "farming_level": 99,
            "farming_exp": 0.0,
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "agility_level": 99,
            "slayer_level": 99,
            "slayer_exp": 0.0,
            "quests": {"back_to_my_roots": {"completed": True}},
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        record = state["farm_patches"]["handelmort_jade_vine"]
        record.update({
            "crop_id": "jade_vine",
            "last_crop_id": "jade_vine",
            "stage": 6,
            "health_checked": True,
            "jade_state": "prunable",
            "next_regrowth_at": 6,
        })
        addon._state.player_data = state
        addon._state.current_skill = "Mining"

        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "again")
        self.assertEqual(
            addon._state.player_data["farm_patches"]["handelmort_jade_vine"]["produce_count"],
            1,
        )
        self.assertEqual(
            [step["kind"] for step in addon._state.player_data["farm_queue"]],
            ["harvest"],
        )

        before_prune = copy.deepcopy(addon._state.player_data)
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(
            addon._state.player_data["farm_patches"]["handelmort_jade_vine"]["produce_count"],
            0,
        )
        self.assertEqual(addon._state.player_data["farm_queue"], [])
        self.assertEqual(addon._state.player_data["inventory"].get("Jade vine branch", 0), 0)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before_prune)

    def test_jade_seed_claim_is_a_direct_undoable_farming_action(self):
        addon = _load_addon_as_package(
            "ankiscape_jade_vine_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Farming"
        state = {
            "inventory": {},
            "farming_level": 53,
            "farming_exp": 0.0,
            "smithing_level": 1,
            "quests": {"back_to_my_roots": {"completed": True}},
        }
        state.update(addon.logic.farming_logic.default_farming_state_pure())
        addon._state.player_data = copy.deepcopy(state)

        addon._on_main_menu(initial_skill="Farming")
        claimed = captured["on_farming_action"](
            "claim_jade_vine_seed",
            {},
        )

        self.assertTrue(claimed["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Jade vine seed"], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, state)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_willow_full_run_health_checks_then_prunes_on_successive_reviews(self):
        addon = _load_addon_as_package("ankiscape_willow_full_run_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {
                "Rake": 1,
                "Spade": 1,
                "Secateurs": 1,
                "Willow sapling": 2,
            },
            "farming_level": 99,
            "farming_exp": 0.0,
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "agility_level": 99,
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state, ok, _ = farming_logic.set_farm_plan_pure(
            state,
            "lumbridge_tree",
            "willow",
        )
        self.assertTrue(ok)
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {
                "kind": "plant",
                "patch_id": "lumbridge_tree",
                "crop_id": "willow",
            },
        )
        self.assertTrue(ok)
        state, _ = farming_logic.advance_farm_clock_pure(
            state,
            40,
            lambda: 1.0,
        )
        state, step_ids = farming_logic.queue_full_run_pure(state)
        self.assertEqual(len(step_ids), 5)
        addon._state.player_data = state
        addon._state.current_skill = "Mining"

        for _ in range(2):
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )

        patch = addon._state.player_data["farm_patches"]["lumbridge_tree"]
        self.assertTrue(patch["health_checked"])
        self.assertEqual(patch["produce_count"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Willow branch"], 1)
        self.assertEqual(
            [step["kind"] for step in addon._state.player_data["farm_queue"]],
            ["chop", "clear", "plant"],
        )
        self.assertEqual(addon._state.player_data["farming_exp"], 1481.3)

    def test_prayer_composite_selection_persists_once_and_rejection_has_no_side_effects(self):
        addon = _load_addon_as_package("ankiscape_prayer_selection_integration")
        calls = {"save": 0, "hud": 0}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon._state.current_skill = "Prayer"
        target_id = "gilded_altar_dragon_bones"
        addon._state.player_data = {
            "prayer_level": 99,
            "current_prayer": target_id,
            "prayer_gilded_mode": "owned",
            "prayer_gilded_house_search": {"target_id": target_id, "reviews_remaining": 2},
            "prayer_owned_altar_stint": {"target_id": target_id, "burners_lit": 1},
            "house_owned": True,
            "house_rooms_bought": {"chapel": True},
            "house_built_flags": {"guilded_altar": True, "marble_burner": True},
            "inventory": {"Dragon bones": 2},
        }

        self.assertTrue(addon.set_prayer_selection("dragon_bones", "gilded_owned"))
        self.assertEqual(calls, {"save": 1, "hud": 1})
        self.assertEqual(
            addon._state.player_data["prayer_owned_altar_stint"],
            {"target_id": target_id, "burners_lit": 1},
        )
        self.assertEqual(addon._state.player_data["prayer_gilded_house_search"]["reviews_remaining"], 2)

        self.assertTrue(addon.set_prayer_selection("dragon_bones", "gilded_hosted"))
        self.assertEqual(calls, {"save": 2, "hud": 2})
        self.assertEqual(addon._state.player_data["prayer_gilded_mode"], "hosted")
        self.assertEqual(addon._state.player_data["prayer_owned_altar_stint"], {})
        self.assertEqual(addon._state.player_data["prayer_gilded_house_search"], {})

        rejected_state = {"prayer_level": 99, "inventory": {"Dragon bones": 1}}
        addon._state.player_data = copy.deepcopy(rejected_state)
        self.assertFalse(addon.set_prayer_selection("dragon_bones", "gilded_owned"))
        self.assertEqual(addon._state.player_data, rejected_state)
        self.assertEqual(calls, {"save": 2, "hud": 2})

    def test_direct_urn_teleports_use_shared_lifo_undo(self):
        addon = _load_addon_as_package("ankiscape_direct_urn_undo_integration")
        from ankiscape.data.urn_data import URN_TIERS_BY_ID

        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        col = _DummyCol()
        mw = _DummyMW(col)
        addon.mw = mw
        calls = {"save": 0, "hud": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon._state.current_skill = "Mining"
        initial = {
            "inventory": {tier.item_full: 2},
            "carried_inventory": {"copper": {tier.item_full: 2}},
            "current_ore": "copper",
            "mining_level": 1,
            "mining_exp": 0.0,
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.review_undo_stack.append({"sentinel": True})

        self.assertTrue(addon.teleport_training_urn(tier.id))
        self.assertTrue(addon.teleport_training_urn(tier.id))
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action", "AnkiScape direct action"],
        )
        self.assertEqual(mw.undo_updates, 2)
        self.assertEqual(addon._state.player_data["inventory"][tier.item_full], 0)
        self.assertNotIn("copper", addon._state.player_data["carried_inventory"])
        self.assertEqual(addon._state.player_data["mining_exp"], tier.teleport_xp * 2)
        telemetry = addon._state.player_data["action_telemetry"]["actions"][f"mining:teleport_{tier.id}"]
        self.assertEqual((telemetry["attempts"], telemetry["successes"]), (2, 2))
        self.assertEqual(len(addon._state.direct_action_undo_stack), 2)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        undo = types.SimpleNamespace(operation="AnkiScape direct action")
        addon._on_state_did_undo(undo)
        self.assertEqual(addon._state.player_data["inventory"][tier.item_full], 1)
        self.assertEqual(addon._state.player_data["carried_inventory"]["copper"][tier.item_full], 1)
        self.assertEqual(addon._state.player_data["mining_exp"], tier.teleport_xp)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(undo)
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)
        self.assertEqual(calls["xp"], [tier.teleport_xp, tier.teleport_xp])
        self.assertEqual(calls["save"], 4)

    def test_bank_kebab_uses_runtime_rng_and_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_consumable_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Combat"
        initial = {
            "inventory": {"Kebab": 1},
            "constitution_level": 50,
            "combat_lifepoints": 100,
        }
        addon._state.player_data = copy.deepcopy(initial)
        original_random = addon.random.random
        addon.random.random = lambda: 0.5
        self.addCleanup(setattr, addon.random, "random", original_random)

        result = addon.on_consume_item("Kebab")

        self.assertEqual(result["healed"], 50)
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 150)
        self.assertNotIn("Kebab", addon._state.player_data["inventory"])
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_bank_pack_open_all_uses_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_pack_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Herblore"
        initial = {"inventory": {"Vial pack": 2, "Vial": 1}}
        addon._state.player_data = copy.deepcopy(initial)

        result = addon.on_open_item_pack("Vial pack", True)

        self.assertEqual(result["packs_opened"], 2)
        self.assertEqual(addon._state.player_data["inventory"], {"Vial": 101})
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)

    def test_bank_impling_jar_loot_uses_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_impling_jar_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Hunter"
        initial = {
            "inventory": {
                "Butterfly net": 1,
                "Impling jar": 1,
                "Dragon impling jar": 1,
            },
            "hunter_level": 83,
            "quests": {"troll_romance": {"completed": True}},
            "music_log": {"version": 1, "unlocked_tracks": []},
        }
        addon._state.player_data = copy.deepcopy(initial)
        rolls = iter((2_700_000 / 6_700_000, 0.0))
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls)
        self.addCleanup(setattr, addon.random, "random", original_random)

        result = addon.on_open_impling_jar("Dragon impling jar")

        self.assertEqual(result["reward_item"], "Dragon dart tip")
        self.assertEqual(result["reward_quantity"], 105)
        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Butterfly net": 1, "Impling jar": 1, "Dragon dart tip": 105},
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        # The completed quest is pending before the jar opens, so this proves the
        # application path ran the shared music-log refresh during its commit.
        self.assertIn(4, addon._state.player_data["music_log"]["unlocked_tracks"])

        addon._state.current_skill = "Cooking"
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.current_skill, "Hunter")
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_impling_jar_loot_restores_rng_when_undo_registration_fails(self):
        addon = _load_addon_as_package("ankiscape_impling_jar_rng_rollback_integration")

        def _reject_undo(*_args):
            raise RuntimeError

        addon.mw = _DummyMW(types.SimpleNamespace(add_custom_undo_entry=_reject_undo))
        addon._state.player_data = {"inventory": {"Dragon impling jar": 1}}
        before = addon.random.getstate()

        self.assertIsNone(addon.on_open_impling_jar("Dragon impling jar"))
        self.assertEqual(addon._state.player_data, {"inventory": {"Dragon impling jar": 1}})
        self.assertEqual(addon.random.getstate(), before)

    def test_bank_discard_x_preserves_remainder_and_uses_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_discard_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Cooking"
        initial = {"inventory": {"Shrimps": 5}}
        addon._state.player_data = copy.deepcopy(initial)

        self.assertTrue(addon.on_discard_item("Shrimps", 2))
        self.assertEqual(addon._state.player_data["inventory"]["Shrimps"], 3)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_ranging_guild_entry_is_one_direct_action_and_undoes_atomically(self):
        addon = _load_addon_as_package(
            "ankiscape_ranging_guild_direct_action_integration"
        )
        ranging = sys.modules[
            f"{addon.__name__}.logic.ranging_guild_logic"
        ]
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Coins": 200, "Bronze arrows": 0},
            "equipment": {
                "weapon": "Shortbow",
                "ammunition": "Bronze arrows",
            },
            "ranged_level": 40,
            "combat_current_levels": {},
            "ranging_guild": ranging.default_ranging_guild_state_pure(),
            "activity_session": {"active_id": ""},
        }
        addon._state.player_data = copy.deepcopy(initial)

        def enter(current):
            updated, ok, _info = ranging.enter_ranging_guild_pure(current)
            return updated, ok

        self.assertTrue(addon.commit_direct_action(enter))
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Bronze arrows"], 10)
        self.assertEqual(
            addon._state.player_data["activity_session"]["active_id"],
            "ranging_guild",
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_family_gauntlet_conversion_is_one_direct_action_and_undoes_atomically(self):
        addon = _load_addon_as_package(
            "ankiscape_cooking_gauntlets_direct_action_integration"
        )
        gauntlets = sys.modules[
            f"{addon.__name__}.logic.cooking_gauntlets_logic"
        ]
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Cooking"
        initial = {
            "inventory": {
                "Goldsmith gauntlets": 1,
                "Cooking gauntlets": 0,
                "Coins": 25_000,
            },
            "equipment": {},
            "quests": {
                "family_crest": {
                    "started": True,
                    "progress": 16,
                    "completed": True,
                }
            },
        }
        addon._state.player_data = copy.deepcopy(initial)

        def convert(current):
            updated, ok, _message = gauntlets.apply_family_gauntlet_conversion_pure(
                current, "Goldsmith gauntlets"
            )
            return updated, ok

        self.assertTrue(addon.commit_direct_action(convert))
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(
            addon._state.player_data["family_gauntlet_enchantment"], "cooking"
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_cooking_gauntlet_equip_and_unequip_are_direct_action_undo_safe(self):
        addon = _load_addon_as_package(
            "ankiscape_cooking_gauntlets_equipment_undo_integration"
        )
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Cooking gauntlets": 1},
            "equipment": {},
        }
        addon._state.player_data = copy.deepcopy(initial)

        self.assertTrue(addon.on_equip_item("Cooking gauntlets"))
        self.assertEqual(
            addon._state.player_data["equipment"], {"hands": "Cooking gauntlets"}
        )
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)

        equipped = {
            "inventory": {"Cooking gauntlets": 0},
            "equipment": {"hands": "Cooking gauntlets"},
        }
        addon._state.player_data = copy.deepcopy(equipped)
        self.assertTrue(addon.on_unequip_slot("hands"))
        self.assertEqual(addon._state.player_data["inventory"]["Cooking gauntlets"], 1)
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, equipped)

    def test_bank_discard_x_removes_and_undoes_exact_degradable_instance(self):
        addon = _load_addon_as_package("ankiscape_condition_discard_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Combat"
        initial = {
            "inventory": {"Combat hood 100": 2},
            "equipment": {},
            "equipment_instances": {
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 89_000,
                    "location": "bank",
                },
                "equipment-2": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 80_000,
                    "location": "bank",
                },
            },
            "equipment_instance_next_id": 3,
        }
        addon._state.player_data = copy.deepcopy(initial)

        self.assertTrue(addon.on_discard_item("Combat hood 100", 1))
        self.assertEqual(addon._state.player_data["inventory"]["Combat hood 100"], 1)
        self.assertNotIn("equipment-2", addon._state.player_data["equipment_instances"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)

    def test_reward_claim_recomputes_level_before_achievements_and_is_undoable(self):
        addon = _load_addon_as_package("ankiscape_reward_claim_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        initial = {
            "inventory": {},
            "claims": {},
            "quests": {
                "stolen_hearts": {"started": True, "progress": 3, "completed": True},
            },
            "agility_level": 1,
            "agility_exp": 0.0,
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Agility"
        calls = {"levels": [], "achievement_levels": [], "xp": []}

        def _level_up(skill_name, data):
            calls["levels"].append(skill_name)
            data["agility_level"] = addon.calculate_new_level(
                data["agility_exp"], data["agility_level"], addon.EXP_TABLE
            )

        addon.level_up_check = _level_up
        addon.check_achievements = lambda data: calls["achievement_levels"].append(data["agility_level"])
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None

        self.assertTrue(addon.on_claim_reward("stolen_hearts_xp_lamp_2", "agility"))
        self.assertEqual(addon._state.player_data["agility_exp"], 250.0)
        self.assertEqual(addon._state.player_data["agility_level"], 3)
        self.assertEqual(calls, {"levels": ["Agility"], "achievement_levels": [3], "xp": [250.0]})
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(addon.mw.undo_updates, 1)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_stronghold_reward_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_stronghold_reward_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        initial = {
            "inventory": {"Coins": 5},
            "stronghold_of_security": {"step": 4, "completed": True, "boots_choice": None},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Mining"
        addon.ui.show_stronghold_reward_dialog = lambda: "Fancy boots"
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None

        self.assertTrue(addon._claim_stronghold_reward())
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 5 + addon.STRONGHOLD_REWARD_COINS)
        self.assertEqual(addon._state.player_data["inventory"]["Fancy boots"], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(addon.mw.undo_updates, 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_mage_arena_statue_switch_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_mage_arena_cape_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Magic"
        initial = {
            "inventory": {
                "Saradomin cape": 1,
                "Guthix staff": 1,
            },
            "equipment": {},
            "mage_arena": {
                "step": 5,
                "completed": True,
                "alignment": "saradomin",
                "attuned_spells": ["saradomin_strike"],
            },
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None

        addon._on_main_menu()
        apply_action = captured["on_mage_arena_action"]
        self.assertTrue(apply_action("cape", "guthix"))
        self.assertEqual(addon._state.player_data["mage_arena"]["alignment"], "guthix")
        self.assertEqual(addon._state.player_data["inventory"]["Saradomin cape"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Guthix cape"], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_shooting_star_exchange_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_shooting_star_exchange_integration"
        )
        star_logic = sys.modules[
            f"{addon.__name__}.logic.shooting_star_logic"
        ]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(
            kwargs
        )
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Stardust": 200},
            "shop_market_clock": {"answered_cards": 20},
            "world_population_profile": "normal",
            "shooting_star": star_logic.default_shooting_star_state_pure(),
            "smithing_level": 1,
        }
        initial, _ = star_logic.advance_shooting_star_world_clock_pure(
            initial
        )
        initial["shooting_star"]["active_event"].update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_card": 22,
            }
        )
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None

        addon._on_main_menu()
        result = captured["on_shooting_star_command"]("exchange", {})

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Stardust"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 50_002)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_fist_of_guthix_reward_purchase_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_fist_of_guthix_reward_integration"
        )
        fog_logic = sys.modules[f"{addon.__name__}.logic.fist_of_guthix_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "equipment_instances": {},
            "equipment_instance_next_id": 1,
            "fist_of_guthix": fog_logic.default_fist_of_guthix_state_pure(),
            "smithing_level": 1,
        }
        initial["fist_of_guthix"]["tokens"] = 100
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None

        addon._on_main_menu()
        result = captured["on_fist_of_guthix_command"](
            "buy_reward", {"reward_id": "combat_hood"}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Combat hood 100"], 1)
        self.assertEqual(addon._state.player_data["fist_of_guthix"]["tokens"], 50)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_penguin_selection_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_penguin_selection_integration"
        )
        penguin_logic = sys.modules[
            f"{addon.__name__}.logic.penguin_hide_and_seek_logic"
        ]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "quests": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "penguin_hide_and_seek",
            "penguin_hide_and_seek": penguin_logic.default_penguin_state_pure(),
            "completed_achievements": [],
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.check_achievements = lambda *_args: None

        spawn_id = penguin_logic.penguin_roster_pure(initial)[0]["id"]
        addon._on_main_menu()
        result = captured["on_penguin_command"](
            "select_spy",
            {"spawn_id": spawn_id},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["penguin_hide_and_seek"]["selected_id"],
            spawn_id,
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        selected = copy.deepcopy(addon._state.player_data)

        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )
        self.assertIn(
            spawn_id,
            addon._state.player_data["penguin_hide_and_seek"]["spotted_ids"],
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="Answer Card")
        )
        self.assertEqual(addon._state.player_data, selected)
        self.assertEqual(addon._state.review_undo_stack, [])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_penguin_point_redemption_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_penguin_redemption_integration"
        )
        penguin_logic = sys.modules[
            f"{addon.__name__}.logic.penguin_hide_and_seek_logic"
        ]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "penguin_hide_and_seek": penguin_logic.default_penguin_state_pure(),
            "smithing_level": 1,
        }
        initial["penguin_hide_and_seek"]["points"] = 2
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None

        addon._on_main_menu()
        result = captured["on_penguin_command"]("redeem_coins", {})

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 13_000)
        self.assertEqual(addon._state.player_data["penguin_hide_and_seek"]["points"], 0)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_vinesweeper_loaded_addon_review_and_direct_actions_are_undoable(self):
        addon = _load_addon_as_package("ankiscape_vinesweeper_e2e")
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        hooks = sys.modules["aqt"].gui_hooks
        self.assertEqual(len(hooks.state_did_undo), 1)
        undo = hooks.state_did_undo[0]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon.level_up_check = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._review_action_multiplier = lambda: 1
        addon._state.current_skill = "Activities"

        initial = storage.default_player_data(
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        initial["inventory"].update({"Spade": 1, "Coins": 10})
        initial["farming_level"] = 40
        addon._state.player_data = copy.deepcopy(initial)
        addon._on_main_menu()

        entered_result = captured["on_vinesweeper_command"]("enter", {})
        self.assertTrue(entered_result["ok"], entered_result)
        captured["on_set_utility"]("vinesweeper")
        entered = copy.deepcopy(addon._state.player_data)
        self.assertTrue(entered["vinesweeper"]["active"])
        self.assertEqual(entered["vinesweeper"]["flags"], 10)
        self.assertEqual(entered["current_utility"], "vinesweeper")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(addon.mw.undo_updates, 1)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        original_random = addon.random.random
        addon.random.random = lambda: 0.99
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        reviewer = sys.modules["aqt.reviewer"].Reviewer()
        self.assertIsNone(reviewer._answerCard(4))

        earned = copy.deepcopy(addon._state.player_data)
        self.assertEqual(earned["vinesweeper"]["operations"], 1)
        self.assertEqual(earned["vinesweeper"]["rabbits_repulsed"], 1)
        self.assertEqual(earned["vinesweeper"]["points"], 280)
        self.assertEqual(earned["inventory"]["Coins"], 0)
        self.assertEqual(earned["hunter_exp"], 30.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        bought = captured["on_vinesweeper_command"](
            "buy_reward",
            {"reward_id": "cabbage_seed", "quantity": 2},
        )
        self.assertTrue(bought["ok"], bought)
        self.assertEqual(addon._state.player_data["inventory"]["Cabbage seed"], 2)
        self.assertEqual(addon._state.player_data["vinesweeper"]["points"], 260)
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action"] * 2,
        )
        self.assertEqual(addon.mw.undo_updates, 2)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 2)
        undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, earned)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        redeemed = captured["on_vinesweeper_command"](
            "redeem_farming_xp",
            {"points": 280},
        )
        self.assertTrue(redeemed["ok"], redeemed)
        self.assertEqual(addon._state.player_data["vinesweeper"]["points"], 0)
        self.assertEqual(
            addon._state.player_data["farming_exp"],
            earned["farming_exp"] + 280.0,
        )
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action"] * 3,
        )
        self.assertEqual(addon.mw.undo_updates, 3)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 2)
        undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, earned)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, entered)
        self.assertEqual(addon._state.review_undo_stack, [])

        undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_slayer_assignment_roll_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_slayer_assignment_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Combat"
        initial = {
            "inventory": {},
            "quests": {},
            "slayer_level": 1,
            "slayer_exp": 0.0,
            "slayer_assignment": {},
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        original_random = addon.random.random
        rolls = iter((0.0, 0.0))
        addon.random.random = lambda: next(rolls)
        self.addCleanup(setattr, addon.random, "random", original_random)

        addon._on_main_menu()
        result = captured["on_slayer_command"](
            "get_assignment", {"master_id": "turael_spria"}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["slayer_assignment"]["family_id"], "bats")
        self.assertEqual(addon._state.player_data["slayer_assignment"]["remaining"], 15)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_grand_exchange_buy_and_sell_offers_are_direct_bank_run_actions(self):
        addon = _load_addon_as_package(
            "ankiscape_grand_exchange_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Utility / Activities"
        initial = {
            "inventory": {"Coins": 10_000},
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        bank_runs = []

        def request_bank_run(data):
            bank_runs.append(copy.deepcopy(data))
            return copy.deepcopy(data), True, "", False

        addon._request_active_bank_run_state = request_bank_run

        addon._on_main_menu()
        guide_price = int(addon.GE_ITEM_CATALOG["Logs"]["guide_price"])
        payload = {
            "side": "buy",
            "item_name": "Logs",
            "quantity": 1,
            "unit_price": guide_price,
        }
        preview = captured["on_ge_action"]("preview_offer", payload)
        self.assertTrue(preview["ok"])
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(bank_runs, [])

        result = captured["on_ge_action"]("place_offer", payload)
        self.assertTrue(result["ok"])
        self.assertTrue(result["bank_run_triggered"])
        self.assertEqual(len(bank_runs), 1)
        self.assertEqual(
            addon._state.player_data["inventory"]["Coins"],
            10_000 - guide_price,
        )
        self.assertEqual(len(addon._state.player_data["ge_player_orders"]), 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        addon._state.player_data["inventory"]["Logs"] = 2
        sell_initial = copy.deepcopy(addon._state.player_data)
        sell = captured["on_ge_action"](
            "place_offer",
            {
                "side": "sell",
                "item_name": "Logs",
                "quantity": 1,
                "unit_price": guide_price,
            },
        )
        self.assertTrue(sell["ok"])
        self.assertTrue(sell["bank_run_triggered"])
        self.assertEqual(len(bank_runs), 2)
        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, sell_initial)

        settings = captured["on_ge_action"](
            "set_offer_safety",
            {
                "high_value_confirmation": 1_000_000,
                "low_price_percent": 10,
                "high_price_multiplier": 5,
            },
        )
        self.assertTrue(settings["ok"])
        self.assertNotIn("bank_run_triggered", settings)
        self.assertEqual(len(bank_runs), 2)

    def test_combat_current_target_drives_main_menu_carried_pack_callbacks(self):
        addon = _load_addon_as_package("ankiscape_combat_carried_target_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        save_calls = []
        addon.save_player_data = lambda: save_calls.append(copy.deepcopy(addon._state.player_data))
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "current_combat_target": "ghost",
            "current_prayer": "bury_bones",
            "inventory": {"Bonecrusher": 1, "Ectoplasmator": 1},
            "smithing_level": 1,
            "carried_advanced_targets": {"ghost": True},
            "carried_layout": {
                "ghost": {"Bonecrusher": 1},
                "bury_bones": {"Bones": 1},
            },
        }

        addon._on_main_menu()

        captured["on_save_player_data"]()
        self.assertEqual(save_calls, [addon._state.player_data])
        self.assertTrue(captured["carried_pack_target_active"])
        self.assertTrue(captured["carried_advanced_state"])
        cells = captured["get_carried_layout_cells"]()
        self.assertIn(("Bonecrusher", 1), cells)
        self.assertNotIn(("Bones", 1), cells)
        self.assertTrue(captured["on_set_carried_layout_quantity"]("Ectoplasmator", 4))
        self.assertEqual(
            addon._state.player_data["carried_layout"]["ghost"],
            {"Bonecrusher": 1, "Ectoplasmator": 4},
        )
        self.assertIn("Air rune", captured["carried_stackable_names"])

    def test_combat_main_menu_loot_rows_only_include_observed_drops(self):
        addon = _load_addon_as_package("ankiscape_combat_observed_loot_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "current_combat_target": "cyclops",
            "combat_observed_drops": {
                "cyclops": {
                    "Coins": {"times_seen": 1, "quantity_seen": 3},
                },
            },
            "inventory": {},
            "smithing_level": 1,
        }

        addon._on_main_menu()

        row_names = {row["item"] for row in captured["loot_override_rows"]}
        self.assertIn("Coins", row_names)
        self.assertNotIn("Big bones", row_names)

    def test_agility_current_target_projects_auto_food_requirements_and_weight_in_main_menu(self):
        addon = _load_addon_as_package("ankiscape_agility_carried_target_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon._state.current_skill = "Agility"
        addon._state.player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "inventory": {"Shark": 2},
            "equipment": {},
            "combat_auto_eat_food": ["Shark"],
            "smithing_level": 1,
        }

        addon._on_main_menu()

        self.assertTrue(captured["carried_pack_target_active"])
        self.assertFalse(captured["carried_auto_is_combat"])
        summary = captured["get_carried_auto_summary"]()
        self.assertIn("Wilderness Agility Course Auto pack", summary)
        self.assertIn("Food: Shark x2", summary)
        self.assertIn("Weight: 1.2 kg carried", summary)
        self.assertEqual(captured["get_carried_bank_run_summary"](), "Bank run: ready")

    def test_gnome_ball_activity_exposes_its_dangerous_carried_pack_in_main_menu(self):
        addon = _load_addon_as_package("ankiscape_gnome_ball_carried_target_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon._state.current_skill = "Utility / Activities"
        addon._state.player_data = {
            "current_utility": "gnome_ball",
            "inventory": {"Shark": 2},
            "carried_inventory": {"gnome_ball": {"Shark": 2}},
            "smithing_level": 1,
        }

        addon._on_main_menu()

        self.assertTrue(captured["carried_pack_target_active"])
        self.assertEqual(captured["active_carried_target_id"], "gnome_ball")
        self.assertIn("gnome_ball Auto pack", captured["get_carried_auto_summary"]())

    def test_agility_main_menu_summary_ignores_stale_carried_items(self):
        addon = _load_addon_as_package("ankiscape_agility_stale_carried_summary")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon._state.current_skill = "Agility"
        addon._state.player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "inventory": {"Shark": 1},
            "equipment": {},
            "combat_auto_eat_food": ["Shark"],
            "smithing_level": 1,
            "carried_primed_targets": {"wilderness_course": True},
            "carried_inventory": {
                "wilderness_course": {
                    "Shark": 1,
                    "Dragon bones": 20,
                },
            },
        }

        addon._on_main_menu()

        summary = captured["get_carried_auto_summary"]()
        self.assertIn("Food: Shark x1", summary)
        self.assertIn("Weight: 0.6 kg carried", summary)

    def test_fatal_wilderness_lap_ambush_and_carried_pack_roll_back_as_one_review(self):
        addon = _load_addon_as_package("ankiscape_wilderness_agility_undo_integration")
        addon.mw = _DummyMW(_DummyCol())
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _exp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        initial = {
            "current_agility": "wilderness_course",
            "agility_level": 99,
            "agility_exp": 0.0,
            "combat_lifepoints": 100,
            "hitpoints_level": 10,
            "combat_auto_eat_threshold_percent": 40,
            "combat_auto_eat_food": ["Shark"],
            "inventory": {"Shark": 1, "Penance horn": 1},
            "equipment": {"weapon": "Bronze sword"},
            "completed_achievements": [],
            "agility_effect_charges": {"Penance horn": 2},
            "agility_lap_counts": {
                "total": 0,
                "flawless": 0,
                "gnome_advanced_flawless": 0,
                "barbarian_advanced_flawless": 0,
                "agile_legs_unlocked": False,
                "agile_top_unlocked": False,
            },
            "agility_course_state": {
                "target": "wilderness_course",
                "stage": 5,
                "checkpoint": "start",
                "flawless": True,
                "lap_xp_valid": True,
                "requested_item_valid": True,
                "status": "",
            },
            "agility_pit_offer": False,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Agility"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        rolls = iter((0.99, 0.0, 0.005, 0.90) + (0.5,) * 100)
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["agility_exp"], 0.0)
        self.assertEqual(addon._state.player_data["agility_lap_counts"]["total"], 0)
        self.assertEqual(addon._state.player_data["agility_effect_charges"]["Penance horn"], 2)
        self.assertEqual(
            addon._state.player_data["combat_grave"]["source"],
            "agility_wilderness_pker",
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_explicit_pit_reward_choice_is_directly_undoable_with_rng(self):
        addon = _load_addon_as_package("ankiscape_pit_context_direct_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        shown_xp = []
        addon._show_exp = shown_xp.append
        initial = {
            "agility_level": 50,
            "agility_exp": 10.0,
            "agility_activity_state": {
                "pit_reward": {"xp": 100.0, "course": "gnome_normal"}
            },
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Agility"
        addon.random.seed(314159)
        before_rng = addon.random.getstate()

        self.assertTrue(
            addon.resolve_review_context_action("pit_reward", "gamble")
        )

        self.assertNotIn(
            "pit_reward",
            addon._state.player_data["agility_activity_state"],
        )
        self.assertEqual(
            addon._state.player_data["review_context_preferences"]["pit_reward"],
            "gamble",
        )
        self.assertIn(shown_xp[-1], {50.0, 100.0, 200.0})
        self.assertEqual(
            addon._state.player_data["agility_exp"],
            10.0 + shown_xp[-1],
        )
        self.assertNotEqual(addon.random.getstate(), before_rng)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon.random.getstate(), before_rng)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_shooting_star_ready_banner_rejoins_in_one_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_star_notice_direct_integration")
        from ankiscape_star_notice_direct_integration.logic.shooting_star_logic import (
            default_shooting_star_state_pure,
        )

        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        state = default_shooting_star_state_pure()
        state["active_event"] = {
            "event_id": "shooting-star-20",
            "slot_card": 20,
            "location": "Falador east mine",
            "starting_size": 1,
            "current_size": 1,
            "layer_remaining": 1_200,
        }
        state["watched_event_id"] = "shooting-star-20"
        state["notice"] = {
            "kind": "ready",
            "event_id": "shooting-star-20",
            "current_size": 1,
            "required_level": 10,
            "sprite_available": False,
        }
        initial = {
            "current_utility": "bankstanding",
            "mining_level": 10,
            "shooting_star": state,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Woodcutting"

        self.assertTrue(
            addon.resolve_review_context_action("shooting_star_notice", "mine")
        )

        self.assertEqual(addon._state.player_data["current_utility"], "shooting_stars")
        self.assertEqual(addon._state.current_skill, "Activities")
        self.assertEqual(addon._state.player_data["shooting_star"]["notice"], {})
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.current_skill, "Woodcutting")
        self.assertEqual(col.get_config("ankiscape_current_skill"), "Woodcutting")

    def test_explicit_phoenix_egg_choice_is_directly_undoable(self):
        addon = _load_addon_as_package("ankiscape_phoenix_context_direct_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        initial = {
            "inventory": {},
            "summoning_level": 71,
            "summoning_state": {
                "pet_instances": {},
                "pet_next_instance_id": 1,
            },
            "phoenix_lair": {
                "pending_egg": True,
                "runs_completed": 1,
            },
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Activities"

        self.assertTrue(
            addon.resolve_review_context_action("phoenix_egg", "kick")
        )

        self.assertEqual(addon._state.player_data["inventory"]["Cracked phoenix egg"], 1)
        self.assertEqual(
            addon._state.player_data["review_context_preferences"]["phoenix_egg"],
            "kick",
        )
        self.assertFalse(addon._state.player_data["phoenix_lair"]["pending_egg"])
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_answer_advances_before_save_without_copying_the_full_state(self):
        addon = _load_addon_as_package("ankiscape_answer_hot_path_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        events = []
        addon.save_player_data = lambda: events.append("save")
        original_deepcopy = addon.copy.deepcopy

        def reject_full_copy(value, *args, **kwargs):
            if value is addon._state.player_data:
                self.fail("the review-undo snapshot must not deep-copy the full player state")
            return original_deepcopy(value, *args, **kwargs)

        addon.copy.deepcopy = reject_full_copy
        self.addCleanup(setattr, addon.copy, "deepcopy", original_deepcopy)

        result = addon.on_answer_card(
            _FakeReviewer(),
            1,
            lambda _self, _ease: events.append("advance") or "answered",
        )

        self.assertEqual(result, "answered")
        self.assertEqual(events[:2], ["advance", "save"])

    def test_carried_inventory_review_undo_restores_the_exact_save(self):
        addon = _load_addon_as_package("ankiscape_carried_review_undo_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.player_data["inventory"]["Logs"] = 1
        addon._state.player_data["fletching_level"] = 1
        addon._state.player_data["fletching_exp"] = 0.0
        addon._state.player_data["current_fletch"] = "arrow_shafts"
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon._state.review_undo_stack.clear()
        initial = copy.deepcopy(addon._state.player_data)

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertTrue(addon._state.player_data["carried_primed_targets"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, initial)

    def test_level_one_player_catches_polar_kebbit_through_real_kernels(self):
        addon = _load_addon_as_package("ankiscape_polar_tracking_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data
        from ankiscape.logic.shop_logic import apply_shop_buy_pure

        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        ctx = self._runtime_context(addon, rolls=(0.0, 0.0, 0.0, 0.0))
        addon._state.player_data["current_thieving"] = "pickpocket_man"
        self.assertTrue(addon.runtime_actions.handle_thieving_answer(ctx))
        self.assertTrue(addon.runtime_actions.handle_thieving_answer(ctx))
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 4)

        addon._state.player_data, bought = apply_shop_buy_pure(
            addon._state.player_data,
            "alecks_hunter_emporium",
            "alecks_hunter_emporium:7:10150",
            1,
        )
        self.assertTrue(bought["allowed"])
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Noose wand"], 1)

        ctx = dataclasses.replace(ctx, player_data=addon._state.player_data)
        addon._state.player_data["current_hunter"] = "catch_polar_kebbit"
        self.assertTrue(addon.runtime_actions.handle_hunter_answer(ctx))

        self.assertEqual(addon._state.player_data["hunter_level"], 1)
        self.assertEqual(addon._state.player_data["hunter_exp"], 30.0)
        self.assertEqual(addon._state.player_data["inventory"]["Noose wand"], 1)
        # Shattered Heart may replace the first two ordinary outputs with Hunter
        # strange rocks; the Polar kebbit fur is third and always survives.
        self.assertEqual(addon._state.player_data["inventory"]["Polar kebbit fur"], 1)

    def test_level_seventy_player_buys_and_uses_polar_kebbit_quota_ticket(self):
        addon = _load_addon_as_package("ankiscape_polar_quota_integration")
        from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data
        from ankiscape.data.item_values import STACKABLE_ITEM_NAMES
        from ankiscape.logic.big_chinchompa_logic import (
            apply_big_chinchompa_reward_purchase_pure,
            set_hunter_private_ground_pure,
        )
        from ankiscape.logic.inventory_pure import set_carried_layout_quantity_pure

        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.player_data["hunter_level"] = 70
        addon._state.player_data["hunter_exp"] = float(EXP_TABLE[69])
        addon._state.player_data["big_chinchompa"]["competence_points"] = 15
        addon._state.player_data["inventory"]["Noose wand"] = 1

        addon._state.player_data, bought, reward = apply_big_chinchompa_reward_purchase_pure(
            addon._state.player_data,
            "polar_kebbit_ticket",
            exp_table=EXP_TABLE,
        )
        self.assertTrue(bought)
        ticket = "Polar kebbit quota ticket"
        self.assertEqual(reward["item_name"], ticket)
        self.assertEqual(addon._state.player_data["big_chinchompa"]["competence_points"], 0)
        self.assertEqual(addon._state.player_data["inventory"][ticket], 1)

        target = "catch_polar_kebbit"
        layout, configured = set_carried_layout_quantity_pure(
            {}, ticket, 1, STACKABLE_ITEM_NAMES
        )
        self.assertTrue(configured)
        addon._state.player_data["carried_layout"][target] = layout
        addon._state.player_data["carried_advanced_targets"][target] = True
        addon._state.player_data, enabled, result = set_hunter_private_ground_pure(
            addon._state.player_data,
            target,
            True,
        )
        self.assertTrue(enabled)
        self.assertEqual(result["ticket"], ticket)

        calls = {"xp": [], "activity": []}
        ctx = self._runtime_context(addon, rolls=(0.0,), calls=calls)
        addon._state.player_data["current_hunter"] = target
        self.assertTrue(
            addon.runtime_actions.run_answer_with_carried_overlay(
                ctx,
                "hunter",
                addon.runtime_actions.handle_hunter_answer,
            )
        )

        self.assertEqual(addon._state.player_data["hunter_level"], 70)
        self.assertEqual(addon._state.player_data["hunter_exp"], float(EXP_TABLE[69]) + 30.0)
        self.assertEqual(addon._state.player_data["inventory"][ticket], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Polar kebbit fur"], 1)
        self.assertEqual(
            addon._state.player_data["carried_inventory"][target]["Polar kebbit fur"], 1
        )
        self.assertNotIn(ticket, addon._state.player_data["carried_inventory"][target])
        self.assertNotIn(target, addon._state.player_data["hunter_private_ground_targets"])
        self.assertIn(ticket, calls["activity"][-1])

    def test_razor_backed_tracking_review_and_undo_use_the_real_hunter_path(self):
        addon = _load_addon_as_package("ankiscape_razor_tracking_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.player_data["inventory"]["Noose wand"] = 1
        addon._state.player_data["hunter_level"] = 49
        addon._state.player_data["hunter_exp"] = 0.0
        addon._state.player_data["current_hunter"] = "track_razor_backed_kebbit"
        addon._state.current_skill = "Hunter"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon._state.review_undo_stack.clear()
        initial = copy.deepcopy(addon._state.player_data)
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Noose wand"], 1)
        # Shattered Heart may replace up to two ordinary outputs with the
        # target's strange rocks. Long kebbit spike is third in the sourced
        # output order, so the downstream-chain item is always retained.
        self.assertEqual(addon._state.player_data["inventory"]["Long kebbit spike"], 1)
        self.assertEqual(addon._state.player_data["hunter_exp"], 348.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_combat_carried_inventory_review_undo_restores_the_exact_save(self):
        addon = _load_addon_as_package("ankiscape_combat_carried_review_undo_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.player_data.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
                "current_combat_target": "chicken",
                "combat_attack_style": "aggressive",
                "combat_lifepoints": 990,
                "loot_value_threshold": 0,
            }
        )
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon._state.review_undo_stack.clear()
        initial = copy.deepcopy(addon._state.player_data)

        combat_runtime = sys.modules[
            f"{addon.__name__}.runtime.runtime_actions_combat"
        ]
        original_apply_combat_burst = combat_runtime.apply_combat_burst_pure

        def combat_burst_with_kept_loot(data, *_args, **_kwargs):
            updated = dict(data)
            inventory = dict(updated["inventory"])
            inventory["Bones"] = int(inventory.get("Bones", 0) or 0) + 1
            updated["inventory"] = inventory
            return updated, True, {
                "reason": "combat_burst",
                "target_id": "chicken",
                "display_name": "Chicken",
                "drops": {"Bones": 1},
                "xp_rewards": {},
                "kills": 1,
            }

        combat_runtime.apply_combat_burst_pure = combat_burst_with_kept_loot
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            combat_runtime.apply_combat_burst_pure = original_apply_combat_burst

        self.assertTrue(addon._state.player_data["carried_inventory"]["chicken"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, initial)

    def test_review_undo_stack_matches_ankis_thirty_transaction_depth(self):
        addon = _load_addon_as_package("ankiscape_review_undo_cap_integration")
        addon._state.review_undo_stack.clear()
        for value in range(32):
            addon._state.player_data = {"counter": value + 1}
            addon._remember_review_award_snapshot(
                {
                    "player_data": {"counter": value},
                    "current_skill": "None",
                    "random_state": addon.random.getstate(),
                }
            )

        self.assertEqual(addon._MAX_REVIEW_UNDO_SNAPSHOTS, 30)
        self.assertEqual(len(addon._state.review_undo_stack), 30)
        self.assertEqual(addon._state.review_undo_stack[0]["values"]["counter"], 2)

    def test_ignored_pit_reward_resolves_on_next_answer_and_review_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_pit_context_review_integration")
        addon.mw = _DummyMW(_DummyCol())
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        shown_xp = []
        addon._show_exp = shown_xp.append
        initial = {
            "agility_level": 50,
            "agility_exp": 10.0,
            "agility_activity_state": {
                "pit_reward": {"xp": 100.0, "course": "gnome_normal"}
            },
            "review_context_preferences": {"pit_reward": "take_xp"},
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            1,
            lambda _self, _ease: "answered",
        )

        self.assertNotIn(
            "pit_reward",
            addon._state.player_data["agility_activity_state"],
        )
        self.assertEqual(addon._state.player_data["agility_exp"], 110.0)
        self.assertEqual(shown_xp, [100.0])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_unrelated_undo_does_not_consume_review_snapshot(self):
        addon = _load_addon_as_package("ankiscape_unrelated_undo_integration")

        addon.save_player_data = lambda: self.fail("unrelated undo should not save")
        addon._state.player_data = {
            "inventory": {"Logs": 0, "Arrow shafts": 15},
            "fletching_level": 1,
            "fletching_exp": 5.0,
            "current_fletch": "arrow_shafts",
        }
        addon._state.review_undo_stack.append(
            {
                "values": {"inventory": {"Logs": 1}, "fletching_exp": 0},
                "remove": [],
            }
        )

        changes = types.SimpleNamespace(
            operation="Set Due Date",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

    def test_miscellania_day_tick_and_review_undo_share_one_transaction(self):
        addon = _load_addon_as_package("ankiscape_miscellania_clock_integration")
        logic = sys.modules[f"{addon.__name__}.logic.managing_miscellania_logic"]
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        initial = {
            "inventory": {},
            "quests": {"throne_of_miscellania": {"completed": True}},
            "shop_market_clock": {"answered_cards": 239, "market_tick": 239},
        }
        initial.update(logic.default_managing_miscellania_state_pure(239))
        initial["managing_miscellania"]["coffer"] = 500_000
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        state = addon._state.player_data["managing_miscellania"]
        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 240)
        self.assertEqual(state["approval_basis_points"], 9_750)
        self.assertEqual(state["coffer"], 450_000)
        self.assertEqual(state["production_credit"], 975_000)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_wicked_hood_daily_refill_and_review_undo_share_one_transaction(self):
        addon = _load_addon_as_package("ankiscape_wicked_hood_clock_integration")
        hood_logic = sys.modules[f"{addon.__name__}.logic.wicked_hood_logic"]
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        initial = {
            "inventory": {},
            "shop_market_clock": {"answered_cards": 239, "market_tick": 239},
            "wicked_hood": hood_logic.default_wicked_hood_state_pure(0),
        }
        initial["wicked_hood"].update(
            {
                "essence_remaining": 7,
                "rune_withdrawals_remaining": 0,
                "teleports_remaining": 1,
            }
        )
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        hood = addon._state.player_data["wicked_hood"]
        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 240)
        self.assertEqual(hood["allowance_day"], 1)
        self.assertEqual(hood["essence_remaining"], 100)
        self.assertEqual(hood["rune_withdrawals_remaining"], 1)
        self.assertEqual(hood["teleports_remaining"], 2)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_miscellania_direct_command_is_atomic_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_miscellania_command_integration")
        logic = sys.modules[f"{addon.__name__}.logic.managing_miscellania_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Coins": 1_000_000},
            "quests": {"throne_of_miscellania": {"completed": True}},
            "shop_market_clock": {"answered_cards": 0},
            "smithing_level": 1,
        }
        initial.update(logic.default_managing_miscellania_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_managing_miscellania_command"](
            "fund_days", {"days": 7}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["managing_miscellania"]["coffer"], 800_000)
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 200_000)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_court_case_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_court_entry_integration")
        logic = sys.modules[f"{addon.__name__}.logic.court_cases_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "quests": {"kings_ransom": {"completed": True}},
            "attack_level": 65,
            "defense_level": 65,
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "smithing_level": 1,
        }
        initial.update(logic.default_court_cases_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_court_cases_command"](
            "enter", {"role": "prosecution", "automation_mode": "casual"}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["court_cases"]["case_id"], "mugger")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_circus_policy_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_circus_policy_integration")
        logic = sys.modules[f"{addon.__name__}.logic.circus_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "circus": logic.default_circus_state_pure(),
            "inventory": {},
            "quests": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "make_soft_clay",
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_circus_command"](
            "set_policy",
            {
                "performance_id": "magic",
                "automation_mode": "casual",
                "strategy": "max_xp",
            },
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "make_soft_clay")
        self.assertEqual(addon._state.player_data["circus"]["selected_performance"], "magic")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_trouble_brewing_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_trouble_brewing_integration")
        logic = sys.modules[f"{addon.__name__}.logic.trouble_brewing_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "quests": {"cabin_fever": {"completed": True}},
            "cooking_level": 40,
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "smithing_level": 1,
        }
        initial.update(logic.default_trouble_brewing_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_trouble_brewing_command"](
            "enter", {"automation_mode": "advanced", "duty": "sabotage"}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "trouble_brewing")
        self.assertEqual(addon._state.player_data["trouble_brewing"]["duty"], "sabotage")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        addon._state.player_data["trouble_brewing_pieces_of_eight"] = 600
        before_purchase = copy.deepcopy(addon._state.player_data)
        result = captured["on_trouble_brewing_command"](
            "buy_reward", {"reward_id": "phasmatys_flag"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Phasmatys flag"], 1)
        self.assertEqual(addon._state.player_data["trouble_brewing_pieces_of_eight"], 0)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, before_purchase)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        addon._state.player_data["trouble_brewing_pieces_of_eight"] = 2
        before_rum = copy.deepcopy(addon._state.player_data)
        result = captured["on_trouble_brewing_command"](
            "buy_reward", {"reward_id": "red_rum"}
        )
        self.assertTrue(result["ok"])
        purchased_rum = copy.deepcopy(addon._state.player_data)
        result = captured["on_drink_trouble_brewing_rum"]("Red rum")
        self.assertTrue(result["ok"])
        self.assertNotIn("Red rum", addon._state.player_data["inventory"])
        self.assertEqual(result["destination"], "Trouble Brewing")

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, purchased_rum)
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, before_rum)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        addon._state.player_data["trouble_brewing_pieces_of_eight"] = 5_000
        before_clue = copy.deepcopy(addon._state.player_data)
        result = captured["on_trouble_brewing_command"](
            "buy_reward", {"reward_id": "medium_clue"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["inventory"]["Clue scroll (medium)"],
            1,
        )
        self.assertEqual(addon._state.player_data["trouble_brewing_pieces_of_eight"], 0)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, before_clue)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_castle_wars_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_castle_wars_integration")
        logic = sys.modules[f"{addon.__name__}.logic.castle_wars_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "combat_supply_loadout": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "smithing_level": 1,
        }
        initial.update(logic.default_castle_wars_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_castle_wars_command"](
            "enter",
            {"automation_mode": "advanced", "duty": "defend", "team": "zamorak"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "castle_wars")
        self.assertEqual(addon._state.player_data["castle_wars"]["duty"], "defend")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_pest_control_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_pest_control_integration")
        logic = sys.modules[f"{addon.__name__}.logic.pest_control_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "combat_supply_loadout": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 40,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_pest_control_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_pest_control_command"](
            "enter",
            {"automation_mode": "advanced", "lander_id": "novice", "duty": "defend"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "pest_control")
        self.assertEqual(addon._state.player_data["pest_control"]["duty"], "defend")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_conquest_setup_entry_and_resignation_are_direct_undoable_actions(self):
        addon = _load_addon_as_package("ankiscape_conquest_integration")
        logic = sys.modules[f"{addon.__name__}.logic.conquest_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "pest_control_commendations": 0,
            "music_log": {"version": 1, "unlocked_tracks": []},
            "achievement_diaries": {"completed_tasks": []},
            "quests": {},
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 40,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_conquest_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        callback = captured["on_conquest_command"]
        setup = callback(
            "set_policy",
            {"automation_mode": "casual", "doctrine": "aggressive"},
        )
        self.assertTrue(setup["ok"])
        after_setup = copy.deepcopy(addon._state.player_data)
        entered = callback("enter", {})
        self.assertTrue(entered["ok"])
        active = copy.deepcopy(addon._state.player_data)
        resigned = callback("resign", {})
        self.assertTrue(resigned["ok"])
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action"] * 3,
        )

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, active)
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, after_setup)
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_soul_wars_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_soul_wars_integration")
        logic = sys.modules[f"{addon.__name__}.logic.soul_wars_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "combat_supply_loadout": {"food": {}},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 40,
            "slayer_level": 40,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_soul_wars_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_soul_wars_command"](
            "enter",
            {"automation_mode": "advanced", "duty": "defend", "team": "creation"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "soul_wars")
        self.assertEqual(addon._state.player_data["soul_wars"]["duty"], "defend")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_shades_pyre_logs_are_direct_undoable_and_award_firemaking_xp(self):
        addon = _load_addon_as_package("ankiscape_shades_mortton_integration")
        logic = sys.modules[f"{addon.__name__}.logic.shades_of_mortton_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon.level_up_check = lambda *_args: None
        addon._show_exp = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Logs": 1, "Sacred oil (4)": 1},
            "equipment": {},
            "combat_encounter": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "quests": {"shades_of_mortton": {"completed": True}},
            "firemaking_level": 80,
            "firemaking_exp": 0.0,
            "smithing_level": 1,
        }
        initial.update(logic.default_shades_of_mortton_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_shades_of_mortton_command"](
            "make_pyre_logs",
            {"output_name": "Pyre logs"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Pyre logs"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Sacred oil (2)"], 1)
        self.assertEqual(addon._state.player_data["firemaking_exp"], 12.0)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_treasure_trail_read_and_casket_are_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_treasure_trails_e2e")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Casket (easy)": 1},
            "equipment": {},
            "combat_encounter": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "treasure_trail": {},
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_treasure_trails_command"](
            "open_casket", {"tier": "easy"}
        )
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["rewards"])
        self.assertNotIn("Casket (easy)", addon._state.player_data["inventory"])
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_daily_challenge_hand_in_is_direct_and_undoable(self):
        """The whole chain: a loaded add-on, a real hand-in, and one undo."""
        addon = _load_addon_as_package("ankiscape_daily_challenges_e2e")
        data_module = sys.modules[f"{addon.__name__}.data.daily_challenges_data"]
        logic = sys.modules[f"{addon.__name__}.logic.daily_challenges_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        spec = data_module.DAILY_CHALLENGE_DATA["mining_copper_ore"]
        initial = {
            "inventory": {"Copper ore": int(spec["required"])},
            "equipment": {},
            "combat_encounter": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "mining_level": 1,
            "mining_exp": 0.0,
            "smithing_level": 1,
        }
        initial.update(logic.default_daily_challenges_state_pure())
        initial["daily_challenges"] = [
            {
                "instance_id": "mining_copper_ore-1",
                "challenge_id": "mining_copper_ore",
                "day": 1,
                "progress": int(spec["required"]),
                "credited": {"Copper ore": int(spec["required"])},
            }
        ]
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_daily_challenges_command"](
            "claim", {"instance_id": "mining_copper_ore-1"}
        )
        self.assertTrue(result["ok"], result)
        self.assertEqual(addon._state.player_data["daily_challenges"], [])
        self.assertEqual(
            addon._state.player_data["inventory"][data_module.DAILY_CHALLENGE_MYSTERY_BAG_ITEM],
            1,
        )
        self.assertEqual(addon._state.player_data["mining_exp"], float(spec["reward_xp"]))
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_a_review_day_assigns_a_challenge_through_the_loaded_addon(self):
        addon = _load_addon_as_package("ankiscape_daily_challenges_clock")
        logic = sys.modules[f"{addon.__name__}.logic.daily_challenges_logic"]
        data_module = sys.modules[f"{addon.__name__}.data.daily_challenges_data"]
        day = int(data_module.DAILY_CHALLENGE_REVIEW_DAY)
        player = {
            "inventory": {},
            "shop_market_clock": {"answered_cards": day},
            "mining_level": 1,
            "cooking_level": 1,
            "fishing_level": 1,
            "firemaking_level": 1,
            "woodcutting_level": 1,
            "constitution_level": 10,
        }
        player.update(logic.default_daily_challenges_state_pure())

        updated, events = logic.advance_daily_challenges_day_pure(player, lambda: 0.0)

        self.assertEqual(len(events["assigned"]), 1)
        self.assertEqual(updated["daily_challenge_day"], 1)
        self.assertIn(
            "New Daily Challenge", updated["daily_challenge_last_result"]
        )

    def test_tzhaar_fight_pit_entry_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_fight_pit_integration")
        logic = sys.modules[f"{addon.__name__}.logic.tzhaar_fight_pit_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 60,
            "constitution_level": 60,
            "ranged_level": 1,
            "magic_level": 1,
            "prayer_level": 43,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_tzhaar_fight_pit_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_tzhaar_fight_pit_command"](
            "enter", {"policy": "aggressive"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "tzhaar_fight_pit")
        self.assertEqual(addon._state.player_data["tzhaar_fight_pit"]["policy"], "aggressive")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_duel_arena_entry_is_reachable_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_duel_arena_integration")
        logic = sys.modules[f"{addon.__name__}.logic.duel_arena_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Coins": 999},
            "equipment": {},
            "combat_encounter": {},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 60,
            "constitution_level": 60,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 43,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_duel_arena_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_duel_arena_command"]("claim_cap", {})
        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["inventory"]["Duellist's cap (tier 1)"],
            1,
        )
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        result = captured["on_duel_arena_command"](
            "enter",
            {"rule_ids": ["no_food", "no_prayer"]},
        )
        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "duel_arena")
        self.assertEqual(
            addon._state.player_data["duel_arena"]["rule_ids"],
            ("no_food", "no_prayer"),
        )
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 999)
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action", "AnkiScape direct action"],
        )
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_duel_arena_uses_one_exchange_per_review_at_high_multiplier(self):
        addon = _load_addon_as_package("ankiscape_duel_arena_multiplier")
        logic = sys.modules[f"{addon.__name__}.logic.duel_arena_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        player = storage.default_player_data(
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        player, ok, _info = logic.enter_duel_arena_pure(player, ())
        self.assertTrue(ok)
        addon._state.player_data = player
        addon._state.current_skill = "Utility / Activities"
        addon._state.exp_awarded = False
        addon._review_action_multiplier = lambda: 10
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon._state.player_data)

        addon.on_good_answer(before)

        self.assertEqual(addon._state.player_data["duel_arena"]["review"], 1)
        self.assertEqual(addon._state.player_data["duel_arena"]["player_points"], 1)
        self.assertEqual(addon._state.player_data["duel_arena_wins"], 0)

    def test_clan_wars_red_portal_entry_is_reachable_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_clan_wars_integration")
        logic = sys.modules[f"{addon.__name__}.logic.clan_wars_logic"]
        data = sys.modules[f"{addon.__name__}.data.clan_wars_data"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Lobster": 4},
            "equipment": {"weapon": "Mithril scimitar"},
            "carried_inventory": {"chicken": {"Lobster": 4}},
            "combat_encounter": {},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 60,
            "constitution_level": 60,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 43,
            "summoning_level": 1,
            "smithing_level": 1,
            "combat_current_levels": {"attack": 99, "strength": 99},
        }
        initial.update(logic.default_clan_wars_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_clan_wars_command"](
            "set_policy",
            {"mode": data.CLAN_WARS_RED_MODE},
        )
        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["clan_wars_policy"]["mode"],
            data.CLAN_WARS_RED_MODE,
        )
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        result = captured["on_clan_wars_command"](
            "enter",
            {"mode": data.CLAN_WARS_RED_MODE},
        )
        self.assertTrue(result["ok"])
        self.assertTrue(result["boosts_clamped"])
        self.assertEqual(addon._state.player_data["current_utility"], "clan_wars")
        self.assertEqual(
            addon._state.player_data["clan_wars"]["mode"],
            data.CLAN_WARS_RED_MODE,
        )
        # The carried pack follows the player into the portal, which is what
        # the red portal then puts at risk.
        self.assertEqual(
            addon._state.player_data["carried_inventory"][
                data.CLAN_WARS_COMBAT_TARGET_ID
            ],
            {"Lobster": 4},
        )
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_clan_wars_review_advances_once_per_answer_at_high_multiplier(self):
        addon = _load_addon_as_package("ankiscape_clan_wars_multiplier")
        logic = sys.modules[f"{addon.__name__}.logic.clan_wars_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        player = storage.default_player_data(
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        player, ok, _info = logic.enter_clan_wars_pure(player, "white_ffa")
        self.assertTrue(ok)
        addon._state.player_data = player
        addon._state.current_skill = "Utility / Activities"
        addon._state.exp_awarded = False
        addon._review_action_multiplier = lambda: 10
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon._state.player_data)

        addon.on_good_answer(before)

        self.assertEqual(addon._state.player_data["clan_wars"]["review"], 1)

    def test_phoenix_lair_loaded_addon_chain_rewards_daily_charge_and_review_undo(self):
        addon = _load_addon_as_package("ankiscape_phoenix_lair_e2e")
        logic = sys.modules[f"{addon.__name__}.logic.phoenix_lair_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon.level_up_check = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._review_action_multiplier = lambda: 1
        addon._state.current_skill = "Activities"

        initial = storage.default_player_data(
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        initial["quests"]["in_pyre_need"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        initial.update(
            {
                "slayer_level": 99,
                "summoning_level": 99,
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
                "magic_level": 99,
                "ranged_level": 99,
                "combat_lifepoints": 990,
            }
        )
        initial["inventory"].update(
            {"Knife": 1, "Secateurs": 1, "Tinderbox": 1}
        )
        initial["carried_advanced_targets"]["phoenix_lair"] = True
        initial["carried_layout"]["phoenix_lair"] = {
            "Knife": 1,
            "Secateurs": 1,
            "Tinderbox": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)

        def _kill_current_encounter(data, *_args, **_kwargs):
            updated = copy.deepcopy(data)
            updated["combat_encounter"] = {}
            return updated, True, {
                "reason": "combat_burst",
                "killed": True,
                "died": False,
                "fled": False,
                "enemy_lifepoints": 0,
                "xp_rewards": {},
                "drops": {},
            }

        logic.apply_combat_burst_pure = _kill_current_encounter

        addon._on_main_menu()
        entered = captured["on_phoenix_lair_command"]("enter", {})
        self.assertTrue(entered["ok"], entered)
        self.assertEqual(addon._state.player_data["phoenix_lair"]["phase"], "guardians")
        self.assertEqual(
            addon._state.player_data["carried_inventory"]["phoenix_lair"],
            {"Knife": 1, "Secateurs": 1, "Tinderbox": 1},
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_main_menu()
        self.assertTrue(captured["carried_pack_target_active"])
        self.assertEqual(captured["active_carried_target_id"], "phoenix_lair")

        def _answer_review():
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )

        _answer_review()
        self.assertEqual(addon._state.player_data["phoenix_lair"]["phase"], "prepare")
        self.assertEqual(addon._state.player_data["inventory"]["Ashes"], 5)

        _answer_review()
        self.assertEqual(addon._state.player_data["phoenix_lair"]["phase"], "phoenix")
        before_completion = copy.deepcopy(addon._state.player_data)

        _answer_review()
        self.assertFalse(addon._state.player_data["phoenix_lair"]["active"])
        self.assertEqual(addon._state.player_data["inventory"]["Phoenix quill"], 5)
        self.assertEqual(addon._state.player_data["phoenix_lair"]["last_completed_world_day"], 0)
        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 3)
        blocked = captured["on_phoenix_lair_command"]("enter", {})
        self.assertFalse(blocked["ok"])
        self.assertIn("world day", blocked["message"])

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, before_completion)
        self.assertEqual(addon._state.player_data["phoenix_lair"]["phase"], "phoenix")
        self.assertEqual(addon._state.player_data["phoenix_lair"]["last_completed_world_day"], -1)
        self.assertEqual(addon._state.player_data["inventory"].get("Phoenix quill", 0), 0)

    def test_barbarian_assault_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_barbarian_assault_integration")
        logic = sys.modules[f"{addon.__name__}.logic.barbarian_assault_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "combat_supply_loadout": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "smithing_level": 1,
        }
        initial.update(logic.default_barbarian_assault_state_pure())
        initial["barbarian_assault_tutorial_complete"] = True
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_barbarian_assault_command"](
            "enter",
            {"automation_mode": "advanced", "role": "defender"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "barbarian_assault")
        self.assertEqual(addon._state.player_data["barbarian_assault"]["role"], "defender")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_dagannoth_kings_entry_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_dagannoth_kings_integration")
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = storage.default_player_data(
            constants.ORE_DATA, constants.ITEM_DEFINITIONS
        )
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_dagannoth_kings_command"]("enter", {})

        self.assertTrue(result["ok"], result)
        self.assertTrue(addon._state.player_data["dagannoth_kings"]["active"])
        self.assertEqual(
            addon._state.player_data["activity_session"],
            {"active_id": "dagannoth_kings"},
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_stronghold_chest_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_stronghold_safety_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_grave": {},
            "death_office": {},
            "smithing_level": 1,
            "stronghold_player_safety": {
                "version": 2,
                "stage": 3,
                "crevice_unlocked": True,
                "chest_claimed": False,
                "safety_first_emote_unlocked": False,
                "last_result": "Reached the reward passage.",
            },
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_stronghold_player_safety_command"](
            "claim_chest", {}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 10_000)
        self.assertEqual(addon._state.player_data["inventory"]["Safety gloves"], 1)
        for claim_id in result["claim_ids"]:
            self.assertEqual(
                addon._state.player_data["claims"][claim_id],
                {"claimed": False, "delivered": True},
            )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_varrock_museum_kit_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_varrock_museum_integration")
        logic = sys.modules[f"{addon.__name__}.logic.varrock_museum_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "quests": {},
            "smithing_level": 1,
            "varrock_museum": logic.default_varrock_museum_state_pure(),
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_varrock_museum_command"]("take_cleaning_kit", {})

        self.assertTrue(result["ok"])
        self.assertEqual(
            set(addon._state.player_data["inventory"]),
            {"Trowel", "Rock pick", "Specimen brush", "Leather gloves", "Leather boots"},
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_phoenix_lair_entry_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_phoenix_entry_integration")
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = storage.default_player_data(
            constants.ORE_DATA, constants.ITEM_DEFINITIONS
        )
        initial["quests"]["in_pyre_need"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        initial.update(
            {
                "slayer_level": 99,
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
            }
        )
        initial["inventory"].update(
            {"Knife": 1, "Secateurs": 1, "Tinderbox": 1}
        )
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_phoenix_lair_command"]("enter", {})

        self.assertTrue(result["ok"], result)
        self.assertTrue(addon._state.player_data["phoenix_lair"]["active"])
        self.assertEqual(
            addon._state.player_data["activity_session"], {"active_id": "phoenix_lair"}
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_wicked_hood_withdrawal_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_wicked_hood_direct_integration")
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Runecrafting"
        initial = storage.default_player_data(
            constants.ORE_DATA, constants.ITEM_DEFINITIONS
        )
        initial["claims"]["wicked_hood"] = {"claimed": True}
        initial["equipment"]["head"] = "Wicked hood"
        initial["current_runecrafting"] = "craft_air_runes"
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_wicked_hood_command"]("essence", {})

        self.assertTrue(result["ok"], result)
        self.assertEqual(addon._state.player_data["inventory"]["Rune essence"], 28)
        self.assertEqual(
            addon._state.player_data["carried_inventory"]["craft_air_runes"]["Rune essence"],
            28,
        )
        self.assertEqual(addon._state.player_data["wicked_hood"]["essence_remaining"], 72)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_court_case_review_and_world_clock_undo_together(self):
        addon = _load_addon_as_package("ankiscape_court_review_integration")
        logic = sys.modules[f"{addon.__name__}.logic.court_cases_logic"]
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        base = {
            "inventory": {},
            "quests": {"kings_ransom": {"completed": True}},
            "attack_level": 65,
            "attack_exp": 0.0,
            "defense_level": 65,
            "defense_exp": 0.0,
            "shop_market_clock": {"answered_cards": 41, "market_tick": 41},
            "activity_session": {"active_id": ""},
        }
        base.update(logic.default_court_cases_state_pure())
        entered, ok, _info = logic.enter_court_case_pure(base)
        self.assertTrue(ok)
        addon._state.player_data = copy.deepcopy(entered)
        initial = copy.deepcopy(entered)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 3, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 42)
        self.assertEqual(addon._state.player_data["court_cases"]["prep_index"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_combat_strip_bank_button_queues_the_engine_route_and_refreshes(self):
        addon = _load_addon_as_package("ankiscape_combat_strip_bank_run")
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon._state.current_skill = "Combat"
        addon._state.player_data = {"combat_encounter": {}}
        surfaces = []
        addon.update_review_bank_run_button = (
            lambda data, handler, callback, target_id=None: surfaces.append(
                {
                    "handler": handler,
                    "target_id": target_id,
                    "callback": callback,
                    "bank_run": copy.deepcopy(data.get("combat_bank_run")),
                }
            )
        )

        addon._update_review_bank_run_surface()
        committed = surfaces[-1]["callback"]()

        self.assertTrue(committed)
        self.assertEqual(surfaces[0]["handler"], "combat")
        self.assertEqual(surfaces[0]["target_id"], "chicken")
        self.assertEqual(
            addon._state.player_data["combat_bank_run"],
            {"reviews_remaining": 2, "target_id": "chicken"},
        )
        self.assertEqual(surfaces[-1]["bank_run"], addon._state.player_data["combat_bank_run"])
        self.assertEqual(len(addon.mw.col.custom_undo_entries), 1)
        self.assertEqual(addon.mw.undo_updates, 1)

    def test_circus_review_and_world_clock_undo_together(self):
        addon = _load_addon_as_package("ankiscape_circus_review_integration")
        logic = sys.modules[f"{addon.__name__}.logic.circus_logic"]
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon.check_achievements = lambda *_args: None
        addon._state.player_data = {
            "circus": logic.default_circus_state_pure(),
            "inventory": {},
            "quests": {},
            "agility_level": 99,
            "agility_exp": 0.0,
            "shop_market_clock": {"answered_cards": 41, "market_tick": 41},
            "current_utility": "big_top_bonanza",
            "activity_session": {"active_id": ""},
            "completed_achievements": [],
        }
        initial = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 3, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 42)
        self.assertEqual(
            addon._state.player_data["circus"]["session"]["active_performance"],
            "agility",
        )
        self.assertEqual(
            addon._state.player_data["circus"]["session"]["trick_index"],
            1,
        )
        self.assertGreater(addon._state.player_data["agility_exp"], 0.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])


if __name__ == "__main__":
    unittest.main()
