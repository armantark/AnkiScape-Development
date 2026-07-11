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
    def get_config(self, key, default=None):
        return self._store.get(key, default)
    def set_config(self, key, value):
        self._store[key] = value

class _DummyMW:
    def __init__(self, col):
        self.col = col


def _install_runtime_fakes():
    # aqt base module
    aqt = types.ModuleType("aqt")
    aqt.mw = None
    aqt.gui_hooks = _FakeHooks()

    # aqt.reviewer submodule
    aqt_reviewer = types.ModuleType("aqt.reviewer")
    aqt_reviewer.Reviewer = _FakeReviewer

    # DO NOT provide aqt.qt so ui.py falls back to HAS_QT = False
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


class TestIntegrationSmoke(unittest.TestCase):
    def setUp(self):
        # Isolate sys.modules pollution between tests
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        # Restore sys.modules to avoid interference with other tests
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

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
        addon.player_data = {
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
        addon.current_skill = "Mining"

        calls["good_answer"] = 0
        def fake_good_answer():
            calls["good_answer"] += 1
        addon.on_good_answer = fake_good_answer

        addon.current_skill = "Thieving"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        result = addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(result, "answered")
        self.assertEqual(calls["good_answer"], 0)

        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(calls["good_answer"], 1)

        # With Experience HUD ON, both question/answer events should ensure+update
        addon._on_rev_show_question()
        addon._on_rev_show_answer()
        self.assertGreaterEqual(calls["ensure"], 1)
        self.assertGreaterEqual(calls["update"], 2)

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

        addon.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        addon.on_fletching_answer()

        self.assertEqual(addon.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon.player_data["fletching_exp"], 5.0)
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
            addon.player_data = {
                "inventory": {"Logs": 1},
                "firemaking_level": 1,
                "firemaking_exp": 0,
                "current_firemaking": "logs",
                "completed_achievements": [],
            }

            addon.on_firemaking_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon.player_data["inventory"]["Ashes"], 1)
        self.assertAlmostEqual(addon.player_data["firemaking_exp"], 40.0)
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
            addon.player_data = {
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

        self.assertEqual(addon.player_data["inventory"]["Feather"], 0)
        self.assertEqual(addon.player_data["inventory"]["Leaping trout"], 1)
        self.assertAlmostEqual(addon.player_data["fishing_exp"], 50.0)
        self.assertAlmostEqual(addon.player_data["strength_exp"], 5.0)
        self.assertAlmostEqual(addon.player_data["agility_exp"], 5.0)
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

        addon.player_data = {
            "inventory": {"Iron bar": 2},
            "smithing_level": 20,
            "smithing_exp": 0,
            "current_smith": "forge_iron_pickaxe",
            "completed_achievements": [],
        }

        addon.on_smithing_answer()

        self.assertEqual(addon.player_data["inventory"]["Iron bar"], 0)
        self.assertEqual(addon.player_data["inventory"]["Iron pickaxe"], 1)
        self.assertAlmostEqual(addon.player_data["smithing_exp"], 50.0)
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

        addon.player_data = {
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

        self.assertEqual(addon.player_data["inventory"]["Iron ore"], 0)
        self.assertNotIn("Iron bar", addon.player_data["inventory"])
        self.assertEqual(addon.player_data["smithing_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["gains"], ["The ore was too impure"])
        telemetry = addon.player_data["action_telemetry"]["actions"]["smithing:smelt_iron_bar"]
        self.assertEqual(telemetry["failure_kinds"], {"smelt_fail": 1})

    def test_equipment_callbacks_equip_and_unequip_items(self):
        addon = _load_addon_as_package("ankiscape_equipment_callbacks")

        calls = {"save": 0, "errors": []}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.show_error_message = lambda title, message: calls["errors"].append((title, message))
        addon.player_data = {
            "inventory": {"Bronze platebody": 1, "Rune platebody": 1},
            "equipment": {},
            "defense_level": 1,
        }

        self.assertTrue(addon.on_equip_item("Bronze platebody"))
        self.assertEqual(addon.player_data["inventory"]["Bronze platebody"], 0)
        self.assertEqual(addon.player_data["equipment"], {"body": "Bronze platebody"})

        self.assertFalse(addon.on_equip_item("Rune platebody"))
        self.assertEqual(calls["errors"], [("Cannot equip item", "Requires level 40 Defense")])
        self.assertEqual(addon.player_data["equipment"], {"body": "Bronze platebody"})

        self.assertTrue(addon.on_unequip_slot("body"))
        self.assertEqual(addon.player_data["inventory"]["Bronze platebody"], 1)
        self.assertEqual(addon.player_data["equipment"], {})
        self.assertEqual(calls["save"], 2)

    def test_utility_answer_batches_inventory_without_skill_xp(self):
        addon = _load_addon_as_package("ankiscape_utility_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon.player_data = {
            "inventory": {"Clay": 3},
            "crafting_exp": 0,
            "current_utility": "make_soft_clay",
            "completed_achievements": [],
        }

        addon.on_utility_answer()

        self.assertEqual(addon.player_data["inventory"]["Clay"], 0)
        self.assertEqual(addon.player_data["inventory"]["Soft clay"], 3)
        self.assertEqual(addon.player_data["crafting_exp"], 0)
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

        addon.player_data = {
            "inventory": {},
            "crafting_exp": 0,
            "current_utility": "gather_wool",
            "completed_achievements": [],
        }

        addon.on_utility_answer()

        self.assertEqual(addon.player_data["inventory"]["Wool"], 28)
        self.assertEqual(addon.player_data["crafting_exp"], 0)
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
            addon.player_data = {
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

        self.assertEqual(addon.player_data["inventory"]["Rune essence"], 3)
        self.assertEqual(addon.player_data["inventory"]["Air rune"], 27)
        self.assertAlmostEqual(addon.player_data["runecrafting_exp"], 135.0)
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Research notes": 1},
            "current_quest": "rune_mysteries",
            "quests": {"rune_mysteries": {"started": True, "progress": 5, "completed": False}},
            "quest_stage_actions": {"rune_mysteries": ["Return Aubury's research notes to Sedridor"]},
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

        self.assertEqual(addon.current_skill, "None")
        self.assertTrue(addon.player_data["quests"]["rune_mysteries"]["completed"])
        self.assertEqual(addon.player_data["quest_points"], 1)
        self.assertEqual(addon.player_data["inventory"]["Air talisman"], 1)
        self.assertEqual(addon.player_data["inventory"]["Research notes"], 0)
        self.assertEqual(addon.player_data["runecrafting_exp"], 0)
        self.assertEqual(addon.player_data["pending_skill_exp_rewards"], {})
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
        addon.current_skill = "Quests"
        addon.player_data = {
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

        self.assertEqual(addon.current_skill, "None")
        self.assertFalse(addon.player_data["quests"]["the_knights_sword"]["completed"])
        self.assertEqual(addon.player_data["quests"]["the_knights_sword"]["progress"], 2)
        self.assertEqual(addon.player_data["quest_points"], 0)
        self.assertEqual(addon.player_data["smithing_exp"], 0)
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
        addon.current_skill = "Quests"
        addon.player_data = {
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

        self.assertEqual(addon.current_skill, "Quests")
        self.assertFalse(addon.player_data["quests"]["dwarf_cannon"]["completed"])
        self.assertEqual(addon.player_data["quests"]["dwarf_cannon"]["progress"], 3)
        self.assertEqual(addon.player_data["inventory"]["Railing"], 0)
        self.assertEqual(addon.player_data["inventory"]["Hammer"], 1)
        self.assertEqual(addon.player_data["quest_combat_encounters"], {})
        self.assertEqual(addon.player_data["quest_combat_encounter_counts"], {})
        self.assertEqual(addon.player_data["quest_points"], 0)
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Dwarf Cannon 3/14"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_fishing_contest_pass_gate(self):
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "fishing_contest",
            "quests": {"fishing_contest": {"started": True, "progress": 1, "completed": False}},
            "quest_stage_actions": {
                "fishing_contest": ["Receive a fishing pass from Austri or Vestri"]
            },
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

        self.assertEqual(addon.current_skill, "Quests")
        self.assertFalse(addon.player_data["quests"]["fishing_contest"]["completed"])
        self.assertEqual(addon.player_data["quests"]["fishing_contest"]["progress"], 2)
        self.assertEqual(addon.player_data["inventory"]["Fishing pass"], 1)
        self.assertEqual(addon.player_data["quest_points"], 0)
        self.assertEqual(addon.player_data["fishing_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Fishing Contest 2/7"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_sheep_herder_feed_gate(self):
        addon = _load_addon_as_package("ankiscape_sheep_herder_stage_integration")

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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "sheep_herder",
            "quests": {"sheep_herder": {"started": True, "progress": 1, "completed": False}},
            "quest_stage_actions": {
                "sheep_herder": ["Accept poisoned sheep feed from Councillor Halgrive"]
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertFalse(addon.player_data["quests"]["sheep_herder"]["completed"])
        self.assertEqual(addon.player_data["quests"]["sheep_herder"]["progress"], 2)
        self.assertEqual(addon.player_data["inventory"]["Sheep feed"], 1)
        self.assertEqual(addon.player_data["quest_points"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Sheep Herder 2/6"])
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "waterfall_quest",
            "quests": {"waterfall_quest": {"started": True, "progress": 2, "completed": False}},
            "quest_stage_actions": {"waterfall_quest": ["Search the Baxtorian bookcase", "Read the Book on Baxtorian"]},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertFalse(addon.player_data["quests"]["waterfall_quest"]["completed"])
        self.assertEqual(addon.player_data["quests"]["waterfall_quest"]["progress"], 3)
        self.assertEqual(addon.player_data["inventory"]["Book on Baxtorian"], 1)
        self.assertEqual(addon.player_data["quest_points"], 0)
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "biohazard",
            "quests": {"biohazard": {"started": True, "progress": 3, "completed": False}},
            "quest_stage_actions": {
                "biohazard": [
                    "Ask Jerico about using messenger pigeons",
                    "Search Jerico's cupboard for bird feed",
                    "Take a pigeon cage from Jerico's house",
                ]
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertFalse(addon.player_data["quests"]["biohazard"]["completed"])
        self.assertEqual(addon.player_data["quests"]["biohazard"]["progress"], 4)
        self.assertEqual(addon.player_data["inventory"]["Bird feed"], 1)
        self.assertEqual(addon.player_data["inventory"]["Pigeon cage"], 1)
        self.assertEqual(addon.player_data["quest_points"], 0)
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "heroes_quest",
            "quests": {"heroes_quest": {"started": True, "progress": 2, "completed": False}},
            "quest_stage_actions": {"heroes_quest": ["Ask Gerrant how to catch lava eels"]},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertFalse(addon.player_data["quests"]["heroes_quest"]["completed"])
        self.assertEqual(addon.player_data["quests"]["heroes_quest"]["progress"], 3)
        self.assertEqual(addon.player_data["inventory"]["Blamish snail slime"], 1)
        self.assertEqual(addon.player_data["quest_points"], 0)
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
        addon.current_skill = "Quests"
        addon.player_data = {
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

        self.assertEqual(addon.current_skill, "Quests")
        self.assertFalse(addon.player_data["quests"]["family_crest"]["completed"])
        self.assertEqual(addon.player_data["quests"]["family_crest"]["progress"], 4)
        self.assertEqual(addon.player_data["inventory"]["Shrimps"], 0)
        self.assertEqual(addon.player_data["inventory"]["Swordfish"], 0)
        self.assertEqual(addon.player_data["inventory"]["Caleb crest"], 1)
        self.assertEqual(addon.player_data["quest_points"], 0)
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
        addon.current_skill = "Quests"
        addon.player_data = {
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

        self.assertEqual(addon.current_skill, "None")
        self.assertFalse(addon.player_data["quests"]["witchs_house"]["completed"])
        self.assertEqual(addon.player_data["quests"]["witchs_house"]["progress"], 4)
        self.assertEqual(addon.player_data["quest_points"], 0)
        self.assertEqual(addon.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("Needs Cheese x1", calls["dialogs"][0][1])
        self.assertIn("Use cheese on the mouse hole", calls["dialogs"][0][1])

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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Bucket": 1},
            "current_quest": "merlins_crystal",
            "quests": {"merlins_crystal": {"started": True, "progress": 4, "completed": False}},
            "quest_stage_actions": {
                "merlins_crystal": ["Question Morgan Le Faye about Excalibur and the binding words"]
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "None")
        self.assertFalse(addon.player_data["quests"]["merlins_crystal"]["completed"])
        self.assertEqual(addon.player_data["quests"]["merlins_crystal"]["progress"], 4)
        self.assertEqual(addon.player_data["inventory"]["Bucket"], 1)
        self.assertEqual(addon.player_data["inventory"].get("Bucket of wax", 0), 0)
        self.assertEqual(addon.player_data["quest_points"], 0)
        self.assertEqual(addon.player_data["pending_skill_exp_rewards"], {})
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Khazard helmet": 1, "Khazard armour": 1, "Khazard cell keys": 1},
            "current_quest": "fight_arena",
            "quests": {"fight_arena": {"started": True, "progress": 8, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
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

        self.assertEqual(addon.current_skill, "None")
        self.assertFalse(addon.player_data["quests"]["fight_arena"]["completed"])
        self.assertEqual(addon.player_data["quests"]["fight_arena"]["progress"], 8)
        self.assertEqual(addon.player_data["quest_points"], 0)
        self.assertEqual(addon.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("Combat stats required before battle support can resolve: Khazard ogre level 63", calls["dialogs"][0][1])

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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "equipment": {"body": "Iron chainbody", "head": "Bronze med helm"},
            "current_quest": "black_knights_fortress",
            "quests": {"black_knights_fortress": {"started": True, "progress": 1, "completed": False}},
            "quest_stage_actions": {"black_knights_fortress": ["Infiltrate the Black Knights' Fortress"]},
            "quest_points": 12,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["black_knights_fortress"]["progress"], 2)
        self.assertFalse(addon.player_data["quests"]["black_knights_fortress"]["completed"])
        self.assertEqual(addon.player_data["quest_points"], 12)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Black Knights' Fortress 2/5"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_consumes_priest_in_peril_essence_at_completion_gate(self):
        addon = _load_addon_as_package("ankiscape_priest_in_peril_essence_integration")

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon.current_skill = "Quests"
        addon.player_data = {
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

        self.assertTrue(addon.player_data["quests"]["priest_in_peril"]["completed"])
        self.assertEqual(addon.player_data["quests"]["priest_in_peril"]["progress"], 9)
        self.assertEqual(addon.player_data["inventory"]["Rune essence"], 0)
        self.assertEqual(addon.player_data["inventory"]["Pure essence"], 24)
        self.assertEqual(addon.player_data["inventory"]["Wolfbane dagger"], 1)
        self.assertEqual(addon.player_data["quest_points"], 1)
        self.assertEqual(addon.player_data["pending_skill_exp_rewards"], {"prayer_exp": 1406.0})
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Staff of armadyl": 1},
            "current_quest": "temple_of_ikov",
            "quests": {"temple_of_ikov": {"started": True, "progress": 10, "completed": False}},
            "quest_route_states": {"temple_of_ikov": ["Side with Lucien"]},
            "quest_stage_actions": {"temple_of_ikov": ["Give the Staff of Armadyl to Lucien in Varrock"]},
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

        self.assertEqual(addon.current_skill, "None")
        self.assertTrue(addon.player_data["quests"]["temple_of_ikov"]["completed"])
        self.assertEqual(addon.player_data["quests"]["temple_of_ikov"]["progress"], 11)
        self.assertEqual(addon.player_data["inventory"]["Staff of armadyl"], 0)
        self.assertEqual(addon.player_data["inventory"]["Shiny key"], 1)
        self.assertEqual(addon.player_data["quest_points"], 1)
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Stake": 1, "Stake hammer": 1},
            "current_quest": "vampyre_slayer",
            "quests": {"vampyre_slayer": {"started": True, "progress": 3, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
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

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["vampyre_slayer"]["progress"], 3)
        self.assertFalse(addon.player_data["quests"]["vampyre_slayer"]["completed"])
        self.assertEqual(addon.player_data["quest_combat_encounters"], {"vampyre_slayer": ["vampyre_slayer_count_draynor_37"]})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Count Draynor"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_resolves_source_backed_demon_slayer_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_darkan_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Silverlight": 1},
            "current_quest": "demon_slayer",
            "quests": {"demon_slayer": {"started": True, "progress": 7, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 30,
            "strength_level": 30,
            "defense_level": 30,
            "constitution_level": 30,
            "prayer_level": 1,
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["demon_slayer"]["progress"], 7)
        self.assertFalse(addon.player_data["quests"]["demon_slayer"]["completed"])
        self.assertEqual(addon.player_data["quest_combat_encounters"], {"demon_slayer": ["demon_slayer_delrith_27"]})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Delrith"])
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "shield_of_arrav",
            "quests": {"shield_of_arrav": {"started": True, "progress": 5, "completed": False}},
            "quest_route_states": {"shield_of_arrav": ["Join the Black Arm Gang"]},
            "quest_combat_config": {"resolver_enabled": True},
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

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["shield_of_arrav"]["progress"], 5)
        self.assertFalse(addon.player_data["quests"]["shield_of_arrav"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounters"],
            {"shield_of_arrav": ["shield_of_arrav_weaponsmaster_23"]},
        )
        self.assertEqual(addon.player_data["inventory"].get("Weapon store key", 0), 0)
        self.assertEqual(addon.player_data["inventory"].get("Phoenix crossbow", 0), 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Weaponsmaster"])
        self.assertEqual(calls["dialogs"], [])

        addon.on_quest_answer()

        self.assertEqual(addon.player_data["quests"]["shield_of_arrav"]["progress"], 6)
        self.assertFalse(addon.player_data["quests"]["shield_of_arrav"]["completed"])
        self.assertEqual(addon.player_data["inventory"]["Weapon store key"], 1)
        self.assertEqual(addon.player_data["inventory"]["Phoenix crossbow"], 2)
        self.assertEqual(calls["save"], 2)
        self.assertEqual(calls["gains"][-1], "Shield of Arrav 6/12")

    def test_quest_answer_resolves_style_aware_magic_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_style_aware_magic_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "another_slice_of_h_a_m",
            "quests": {"another_slice_of_h_a_m": {"started": True, "progress": 4, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_combat_encounters": {"another_slice_of_h_a_m": ["another_slice_of_h_a_m_sigmund_64"]},
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

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["another_slice_of_h_a_m"]["progress"], 4)
        self.assertFalse(addon.player_data["quests"]["another_slice_of_h_a_m"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounters"],
            {
                "another_slice_of_h_a_m": [
                    "another_slice_of_h_a_m_h_a_m_mage_30",
                    "another_slice_of_h_a_m_sigmund_64",
                ]
            },
        )
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated H.A.M. mage"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_resolves_split_golem_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_split_golem_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "spirits_of_the_elid",
            "quests": {"spirits_of_the_elid": {"started": True, "progress": 4, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 90,
            "strength_level": 90,
            "defense_level": 90,
            "constitution_level": 90,
            "prayer_level": 1,
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["spirits_of_the_elid"]["progress"], 4)
        self.assertFalse(addon.player_data["quests"]["spirits_of_the_elid"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounters"],
            {"spirits_of_the_elid": ["spirits_of_the_elid_black_golem_75"]},
        )
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Black golem"])
        self.assertEqual(calls["dialogs"], [])

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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "a_souls_bane",
            "quests": {"a_souls_bane": {"started": True, "progress": 3, "completed": False}},
            "quest_stage_actions": {"a_souls_bane": ["Fill the rage meter with an anger weapon"]},
            "quest_combat_config": {"resolver_enabled": True},
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

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["a_souls_bane"]["progress"], 3)
        self.assertFalse(addon.player_data["quests"]["a_souls_bane"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounter_counts"],
            {"a_souls_bane": {"a_souls_bane_fear_reaper_42": 1}},
        )
        self.assertEqual(addon.player_data["quest_combat_encounters"], {})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Fear reaper"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_resolves_identical_source_generated_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_identical_source_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Thread": 1, "Leather": 1},
            "current_quest": "elemental_workshop_i",
            "quests": {"elemental_workshop_i": {"started": True, "progress": 2, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
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

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["elemental_workshop_i"]["progress"], 2)
        self.assertFalse(addon.player_data["quests"]["elemental_workshop_i"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounters"],
            {"elemental_workshop_i": ["elemental_workshop_i_earth_elemental_35"]},
        )
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Earth Elemental"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_resolves_beast_fallback_ranged_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_beast_fallback_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "toktz_ket_dill",
            "quests": {"toktz_ket_dill": {"started": True, "progress": 6, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 50,
            "strength_level": 50,
            "defense_level": 50,
            "constitution_level": 50,
            "prayer_level": 1,
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["toktz_ket_dill"]["progress"], 6)
        self.assertFalse(addon.player_data["quests"]["toktz_ket_dill"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounter_counts"],
            {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 1}},
        )
        self.assertEqual(addon.player_data["quest_combat_encounters"], {})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Lava monster"])
        self.assertEqual(calls["dialogs"], [])

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["toktz_ket_dill"]["progress"], 6)
        self.assertFalse(addon.player_data["quests"]["toktz_ket_dill"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounters"],
            {"toktz_ket_dill": ["toktz_ket_dill_lava_monster_47"]},
        )
        self.assertEqual(
            addon.player_data["quest_combat_encounter_counts"],
            {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 2}},
        )
        self.assertEqual(calls["save"], 2)
        self.assertEqual(calls["gains"], ["Defeated Lava monster", "Defeated Lava monster"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_resolves_no_combat_levels_beast_stat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_no_combat_levels_beast_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "forgiveness_of_a_chaos_dwarf",
            "quests": {"forgiveness_of_a_chaos_dwarf": {"started": True, "progress": 4, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "constitution_level": 80,
            "prayer_level": 80,
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["forgiveness_of_a_chaos_dwarf"]["progress"], 4)
        self.assertFalse(addon.player_data["quests"]["forgiveness_of_a_chaos_dwarf"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounters"],
            {"forgiveness_of_a_chaos_dwarf": ["forgiveness_of_a_chaos_dwarf_chaos_dwarf_hand_cannoneer_100"]},
        )
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Chaos dwarf hand cannoneer"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_resolves_witchs_house_first_form_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_witchs_house_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "witchs_house",
            "quests": {"witchs_house": {"started": True, "progress": 9, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 60,
            "constitution_level": 60,
            "prayer_level": 1,
        }

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["witchs_house"]["progress"], 9)
        self.assertFalse(addon.player_data["quests"]["witchs_house"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounters"],
            {"witchs_house": ["witchs_house_witchs_experiment_first_form"]},
        )
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Witch's experiment (Skavid form)"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_resolves_conflict_overridden_dad_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_conflict_override_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Coins": 12},
            "current_quest": "troll_stronghold",
            "quests": {"troll_stronghold": {"started": True, "progress": 2, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_combat_encounters": {
                "troll_stronghold": ["troll_stronghold_twig_troll_71", "troll_stronghold_troll_general_171"]
            },
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

        self.assertEqual(addon.current_skill, "Quests")
        self.assertEqual(addon.player_data["quests"]["troll_stronghold"]["progress"], 2)
        self.assertFalse(addon.player_data["quests"]["troll_stronghold"]["completed"])
        self.assertEqual(
            addon.player_data["quest_combat_encounters"],
            {
                "troll_stronghold": [
                    "troll_stronghold_dad_101",
                    "troll_stronghold_troll_general_171",
                    "troll_stronghold_twig_troll_71",
                ]
            },
        )
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Dad"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_completes_holy_grail_final_handoff_and_consumes_grail(self):
        addon = _load_addon_as_package("ankiscape_holy_grail_completion_integration")

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.level_up_check = lambda _skill, data: data.__setitem__("defense_level", 33)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_popups_enabled": False}))
        addon.current_skill = "Quests"
        addon.player_data = {
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

        addon.on_quest_answer()

        self.assertEqual(addon.current_skill, "None")
        self.assertEqual(addon.player_data["quests"]["holy_grail"]["progress"], 11)
        self.assertTrue(addon.player_data["quests"]["holy_grail"]["completed"])
        self.assertEqual(addon.player_data["inventory"]["Holy grail"], 0)
        self.assertEqual(addon.player_data["quest_points"], 2)
        self.assertEqual(addon.player_data["defense_exp"], 15300.0)
        self.assertGreater(addon.player_data["defense_level"], 1)
        self.assertEqual(
            addon.player_data["pending_skill_exp_rewards"],
            {"prayer_exp": 11000.0},
        )
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Holy Grail complete"])
        self.assertEqual(calls["dialogs"][0][0], "Quest complete")

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
            addon.player_data = {
                "inventory": {"Bird's nest (seeds)": 1},
                "woodcutting_exp": 0,
                "current_utility": "open_bird_nest",
                "completed_achievements": [],
            }

            addon.on_utility_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"]["Bird's nest (seeds)"], 0)
        self.assertEqual(addon.player_data["inventory"]["Bird's nest (empty)"], 1)
        self.assertEqual(addon.player_data["inventory"]["Acorn"], 1)
        self.assertEqual(addon.player_data["woodcutting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Opened 1 bird nest"])

    def test_utility_out_of_materials_switches_off_and_warns(self):
        # Running a Utility activity with no materials must warn once and switch
        # the active skill off (current_skill -> "None") so it stops nagging on
        # every card; the player re-picks from the menu to resume.
        addon = _load_addon_as_package("ankiscape_utility_depleted")
        errors = []
        addon.check_achievements = lambda _d: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _t: self.fail("should not gain when out of materials")
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon.current_skill = "Utility / Activities"
        addon.player_data = {"inventory": {}, "current_utility": "make_soft_clay", "completed_achievements": []}

        addon.on_utility_answer()

        self.assertEqual(addon.current_skill, "None")
        self.assertEqual(len(errors), 1)
        self.assertIn("switched off", errors[0][1])
        self.assertIn("Clay", errors[0][1])

    def test_crafting_missing_intermediate_names_material_and_switches_off(self):
        # "Pot" needs an "Unfired pot", not Soft clay directly. The error must name
        # the actual missing item (so a bank full of Soft clay doesn't look like a
        # bug) and switch Crafting off.
        addon = _load_addon_as_package("ankiscape_craft_depleted")
        errors = []
        addon.check_achievements = lambda _d: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon.current_skill = "Crafting"
        addon.player_data = {
            "inventory": {"Soft clay": 231},
            "crafting_level": 50,
            "current_craft": "fire_empty_pot",
            "completed_achievements": [],
        }

        addon.on_crafting_answer()

        self.assertEqual(addon.current_skill, "None")
        self.assertEqual(len(errors), 1)
        self.assertIn("Pot (unfired)", errors[0][1])
        self.assertIn("switched off", errors[0][1])

    def test_changing_target_refreshes_review_hud(self):
        # Switching the active Utility activity (or any target) must push the new
        # state to the in-review HUD immediately, not on the next card.
        addon = _load_addon_as_package("ankiscape_target_hud_refresh")
        calls = {"hud": []}
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda data, skill: calls["hud"].append(skill)
        addon.current_skill = "Utility / Activities"
        addon.player_data = {"inventory": {}, "current_utility": "gather_flax"}

        addon._set_value("current_utility", "make_soft_clay")

        self.assertEqual(addon.player_data["current_utility"], "make_soft_clay")
        self.assertEqual(calls["hud"], ["Utility / Activities"])

    def test_review_handler_lookup_uses_action_registry_for_skills_and_utility(self):
        addon = _load_addon_as_package("ankiscape_action_dispatch_lookup")

        self.assertIs(addon._registered_answer_handler("Fletching"), addon.runtime_actions.handle_fletching_answer)
        self.assertIs(addon._registered_answer_handler("Firemaking"), addon.runtime_actions.handle_firemaking_answer)
        self.assertIs(addon._registered_answer_handler("Fishing"), addon.runtime_actions.handle_fishing_answer)
        self.assertIs(addon._registered_answer_handler("Utility / Activities"), addon.runtime_actions.handle_utility_answer)
        self.assertIs(addon._registered_answer_handler("Utility"), addon.runtime_actions.handle_utility_answer)
        self.assertIsNone(addon._registered_answer_handler("Thieving"))

    def test_can_start_current_action_uses_handler_keyed_readiness_checks(self):
        addon = _load_addon_as_package("ankiscape_action_dispatch_readiness")

        addon.current_skill = "Fletching"
        addon.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "current_fletch": "arrow_shafts",
        }
        self.assertTrue(addon._can_start_current_action())

        addon.player_data["inventory"] = {}
        self.assertFalse(addon._can_start_current_action())

        addon.current_skill = "Firemaking"
        addon.player_data = {
            "inventory": {"Logs": 1},
            "firemaking_level": 1,
            "current_firemaking": "logs",
        }
        self.assertTrue(addon._can_start_current_action())

        addon.player_data["inventory"] = {}
        self.assertFalse(addon._can_start_current_action())

        addon.current_skill = "Fishing"
        addon.player_data = {
            "inventory": {"Fishing bait": 1},
            "fishing_level": 5,
            "current_fishing": "catch_sardine_herring",
        }
        self.assertTrue(addon._can_start_current_action())

        addon.player_data["inventory"] = {}
        self.assertFalse(addon._can_start_current_action())

        addon.current_skill = "Utility"
        addon.player_data = {"inventory": {"Clay": 1}, "current_utility": "make_soft_clay"}
        self.assertTrue(addon._can_start_current_action())

        addon.player_data = {"inventory": {}, "current_utility": "make_soft_clay"}
        self.assertFalse(addon._can_start_current_action())

    def test_review_action_multiplier_runs_gathering_and_processing_ticks(self):
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

        addon.player_data = {
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
            addon.current_skill = "Woodcutting"
            addon.card_turned = True
            addon.answer_shown = True
            addon.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

            addon.current_skill = "Fletching"
            addon.card_turned = True
            addon.answer_shown = True
            addon.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 30)
        self.assertAlmostEqual(addon.player_data["woodcutting_exp"], 50.0)
        self.assertAlmostEqual(addon.player_data["fletching_exp"], 10.0)
        self.assertEqual(calls["xp"], [50.0, 10.0])

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
        addon.player_data = {
            "inventory": {},
            "crafting_exp": 0,
            "current_utility": "gather_wool",
            "completed_achievements": [],
        }

        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Wool"], 56)
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 2)
        self.assertEqual(calls["gains"], ["+56 Wool"])

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
        addon.player_data = {
            "inventory": {"Coins": 500},
            "current_utility": "one_shot_bundle",
            "completed_achievements": [],
        }

        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.current_skill, "None")
        self.assertEqual(addon.mw.col.get_config("ankiscape_current_skill"), "None")
        self.assertEqual(addon.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon.player_data["inventory"]["Bird snare"], 1)
        self.assertEqual(addon.player_data["inventory"]["Impling jar"], 10)
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
        addon.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertAlmostEqual(addon.player_data["fletching_exp"], 5.0)

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
        addon.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon.player_data["fletching_exp"], 5.0)
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
        addon.player_data = {
            "inventory": {"Logs": 2},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        addon.current_skill = "Firemaking"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon.player_data["inventory"]["Ashes"], 2)
        self.assertAlmostEqual(addon.player_data["firemaking_exp"], 80.0)
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
        addon.player_data = {
            "inventory": {"Fishing bait": 1},
            "fishing_level": 5,
            "fishing_exp": 0,
            "strength_level": 1,
            "agility_level": 1,
            "current_fishing": "catch_sardine_herring",
            "completed_achievements": [],
        }
        addon.current_skill = "Fishing"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"]["Fishing bait"], 0)
        self.assertEqual(addon.player_data["inventory"]["Raw sardine"], 1)
        self.assertAlmostEqual(addon.player_data["fishing_exp"], 20.0)
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

        addon.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon.player_data["fletching_exp"], 5.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Logs": 1})
        self.assertEqual(addon.player_data["fletching_exp"], 0)
        self.assertEqual(addon.player_data["current_fletch"], "arrow_shafts")
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertEqual(calls["xp"], [5.0])
        self.assertGreaterEqual(calls["save"], 2)

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
        addon.player_data = {
            "inventory": {"Shield left half": 1, "Shield right half": 1},
            "smithing_level": 60,
            "smithing_exp": 0,
            "current_smith": "repair_dragon_sq_shield",
            "completed_achievements": [],
        }
        addon.current_skill = "Smithing"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"], {"Shield left half": 0, "Shield right half": 0, "Dragon sq shield": 1})
        self.assertAlmostEqual(addon.player_data["smithing_exp"], 70.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon.player_data["inventory"], {"Shield left half": 1, "Shield right half": 1})
        self.assertAlmostEqual(addon.player_data["smithing_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertEqual(calls["xp"], [70.0])
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
        addon.player_data = {
            "inventory": {"Arrow shafts": 15, "Yellow feather": 15},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "headless_arrows",
            "completed_achievements": [],
        }
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Yellow feather"], 0)
        self.assertEqual(addon.player_data["inventory"]["Headless arrows"], 15)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon.player_data["inventory"], {"Arrow shafts": 15, "Yellow feather": 15})
        self.assertAlmostEqual(addon.player_data["fletching_exp"], 0)
        self.assertEqual(calls["xp"], [15.0])

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

        addon.player_data = {
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
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 30)
        self.assertEqual(addon.player_data["inventory"]["Shark"], 30)
        self.assertEqual(addon.player_data["inventory"]["Bronze arrows"], 10)
        # One leave-combat rest review heals a ceil-share of the missing 80 LP
        # (ceil(80/3) = 27), topping the player to full over three reviews.
        self.assertEqual(addon.player_data["combat_lifepoints"], 47)
        self.assertEqual(addon.player_data["combat_special_attack_energy"], 45)
        self.assertEqual(addon.player_data["combat_current_levels"], {"attack": 2})
        self.assertEqual(addon.player_data["combat_recovery_progress"], {"stat_drain_ticks": 50})
        self.assertEqual(
            addon.player_data["combat_supply_loadout"],
            {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "cannonballs": 0},
        )
        self.assertEqual(addon.player_data["combat_bank_run"], {"reviews_remaining": 1, "target_id": "chicken"})
        self.assertEqual(addon.player_data["combat_last_result"]["reason"], "combat_bank_run")
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Logs": 2, "Shark": 30, "Bronze arrows": 10})
        self.assertEqual(addon.player_data["fletching_exp"], 0)
        self.assertEqual(addon.player_data["combat_lifepoints"], 20)
        self.assertEqual(addon.player_data["combat_special_attack_energy"], 35)
        self.assertEqual(addon.player_data["combat_current_levels"], {"attack": 2})
        self.assertEqual(addon.player_data["combat_recovery_progress"], {})
        self.assertEqual(addon.player_data["combat_supply_loadout"], {})

    def test_death_office_reclaim_callback_consumes_coins_and_saves(self):
        addon = _load_addon_as_package("ankiscape_death_office_reclaim_integration")

        calls = {"save": 0, "errors": []}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["errors"].append((title, message))

        addon.player_data = {
            "inventory": {"Coins": 150},
            "death_office": {"items": ["Bronze sword"], "source": "combat_stacked_grave"},
            "combat_grave": {},
        }

        self.assertTrue(addon.on_reclaim_death_office())
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(addon.player_data["inventory"]["Coins"], 50)
        self.assertEqual(addon.player_data["inventory"]["Bronze sword"], 1)
        self.assertEqual(addon.player_data["death_office"], {})

    def test_combat_loadout_menu_callbacks_refill_and_unload_supplies(self):
        addon = _load_addon_as_package("ankiscape_combat_loadout_callbacks")

        calls = {"save": 0, "hud": 0, "refresh": 0}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon._refresh_skill_availability = lambda: calls.__setitem__("refresh", calls["refresh"] + 1)
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.current_skill = "Combat"
        addon.player_data = {
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

        self.assertTrue(addon.on_set_combat_auto_eat_threshold(65))
        self.assertEqual(addon.player_data["combat_auto_eat_threshold_percent"], 65)
        self.assertTrue(addon.on_set_combat_auto_eat_food("Lobster"))
        self.assertEqual(addon.player_data["combat_auto_eat_food"][0], "Lobster")

        addon.player_data["combat_auto_eat_food"] = ["Shark"]
        self.assertTrue(addon.on_refill_combat_loadout())
        self.assertEqual(addon.player_data["combat_supply_loadout"]["food"], {"Shark": 20})
        self.assertEqual(addon.player_data["combat_supply_loadout"]["potions"], {"Antipoison (2)": 1})
        self.assertEqual(addon.player_data["combat_supply_loadout"]["runes"], {"Air rune": 5, "Mind rune": 5})
        self.assertEqual(addon.player_data["inventory"]["Shark"], 10)
        self.assertEqual(addon.player_data["inventory"]["Antipoison (2)"], 0)
        self.assertEqual(addon.player_data["inventory"]["Fire rune"], 5)

        self.assertTrue(addon.on_unload_combat_loadout())
        self.assertEqual(
            addon.player_data["combat_supply_loadout"],
            {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "cannonballs": 0},
        )
        self.assertEqual(addon.player_data["inventory"]["Shark"], 30)
        self.assertEqual(addon.player_data["inventory"]["Antipoison (2)"], 1)
        self.assertEqual(addon.player_data["inventory"]["Air rune"], 5)
        self.assertEqual(addon.player_data["inventory"]["Mind rune"], 5)
        self.assertGreaterEqual(calls["save"], 4)
        self.assertGreaterEqual(calls["hud"], 4)
        self.assertGreaterEqual(calls["refresh"], 4)

    def test_firemaking_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_firemaking_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon.player_data = {
            "inventory": {"Logs": 1},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        addon.current_skill = "Firemaking"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"], {"Logs": 0, "Ashes": 1})
        self.assertAlmostEqual(addon.player_data["firemaking_exp"], 40.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Logs": 1})
        self.assertEqual(addon.player_data["firemaking_exp"], 0)
        self.assertEqual(addon.player_data["current_firemaking"], "logs")
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
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

        addon.player_data = {
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
        addon.current_skill = "Fishing"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"], {"Feather": 0, "Leaping trout": 1})
        self.assertAlmostEqual(addon.player_data["fishing_exp"], 50.0)
        self.assertAlmostEqual(addon.player_data["strength_exp"], 5.0)
        self.assertAlmostEqual(addon.player_data["agility_exp"], 5.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Feather": 1})
        self.assertEqual(addon.player_data["fishing_exp"], 0)
        self.assertEqual(addon.player_data["strength_exp"], 0)
        self.assertEqual(addon.player_data["agility_exp"], 0)
        self.assertEqual(addon.player_data["current_fishing"], "catch_leaping_fish")
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertEqual(calls["xp"], [50.0])
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

        addon.player_data = {
            "inventory": {"Seaweed": 1},
            "cooking_level": 1,
            "cooking_exp": 0,
            "current_cooking": "burn_seaweed",
            "completed_achievements": [],
        }
        addon.current_skill = "Cooking"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 1.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"], {"Seaweed": 0, "Soda ash": 1})
        self.assertAlmostEqual(addon.player_data["cooking_exp"], 1.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Seaweed": 1})
        self.assertEqual(addon.player_data["cooking_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertEqual(calls["xp"], [1.0])
        self.assertGreaterEqual(calls["save"], 2)

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

        addon.player_data = {
            "inventory": {"Raw lava eel": 1},
            "cooking_level": 53,
            "cooking_exp": 0,
            "current_cooking": "cook_lava_eel",
            "completed_achievements": [],
        }
        addon.current_skill = "Cooking"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"], {"Raw lava eel": 0, "Lava eel": 1})
        self.assertAlmostEqual(addon.player_data["cooking_exp"], 30.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Raw lava eel": 1})
        self.assertEqual(addon.player_data["cooking_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertEqual(calls["xp"], [30.0])
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
        addon.player_data = {
            "inventory": ingredients.copy(),
            "herblore_level": 96,
            "herblore_exp": 0,
            "current_herblore": "finished_overload",
            "completed_achievements": [],
        }
        addon.current_skill = "Herblore"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Overload (3)"], 1)
        self.assertEqual(addon.player_data["inventory"]["Vial"], 4)
        self.assertEqual(addon.player_data["herblore_exp"], 1000.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], ingredients)
        self.assertEqual(addon.player_data["herblore_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertEqual(calls["xp"], [1000.0])
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
        addon._refresh_smithing_and_crafting_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon.player_data = {
            "inventory": {"Steel bar": 1, "Ammo mould": 1},
            "smithing_level": 35,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "forge_cannonballs",
            "quests": {"dwarf_cannon": {"completed": True}},
            "completed_achievements": [],
        }
        addon.current_skill = "Smithing"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"], {"Steel bar": 0, "Ammo mould": 1, "Cannonball": 4})
        self.assertEqual(addon.player_data["smithing_exp"], 25.6)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Steel bar": 1, "Ammo mould": 1})
        self.assertEqual(addon.player_data["smithing_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertEqual(calls["xp"], [25.6])

    def test_utility_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_utility_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.player_data = {
            "inventory": {"Anchovies": 2},
            "crafting_exp": 0,
            "current_utility": "grind_anchovies",
            "completed_achievements": [],
        }
        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"], {"Anchovies": 0, "Anchovy paste": 2})
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Anchovies": 2})
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_leather_thread_consumption_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_leather_thread_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.player_data = {
            "inventory": {"Leather": 1, "Thread": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "leather_leather_gloves",
            "completed_achievements": [],
        }
        addon.current_skill = "Crafting"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        self.addCleanup(setattr, addon.random, "random", original_random)

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"], {"Leather": 0, "Thread": 0, "Leather gloves": 1})
        self.assertAlmostEqual(addon.player_data["crafting_exp"], 13.8)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Leather": 1, "Thread": 1})
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_glassblowing_pipe_requirement_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_glassblowing_pipe_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.player_data = {
            "inventory": {"Molten glass": 1, "Glassblowing pipe": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "glass_beer_glass",
            "completed_achievements": [],
        }
        addon.current_skill = "Crafting"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"], {"Molten glass": 0, "Glassblowing pipe": 1, "Beer glass": 1})
        self.assertAlmostEqual(addon.player_data["crafting_exp"], 17.5)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Molten glass": 1, "Glassblowing pipe": 1})
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_unfired_clay_ring_mould_requirement_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_unfired_clay_ring_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.player_data = {
            "inventory": {"Soft clay": 1, "Ring mould": 1},
            "crafting_level": 4,
            "crafting_exp": 0,
            "current_craft": "form_clay_ring_unfired",
            "completed_achievements": [],
        }
        addon.current_skill = "Crafting"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(
            addon.player_data["inventory"], {"Soft clay": 0, "Ring mould": 1, "Clay ring (unfired)": 1}
        )
        self.assertAlmostEqual(addon.player_data["crafting_exp"], 11.3)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Soft clay": 1, "Ring mould": 1})
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_light_source_review_action_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_light_source_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.player_data = {
            "inventory": {"Sapphire lantern (unlit)": 1},
            "firemaking_level": 49,
            "current_utility": "light_sapphire_lantern",
            "completed_achievements": [],
        }
        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"], {"Sapphire lantern (unlit)": 0, "Sapphire lantern (lit)": 1})
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Sapphire lantern (unlit)": 1})
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
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
        addon.player_data = {
            "inventory": {"Cowhide": 30, "Coins": 100},
            "crafting_exp": 0,
            "current_utility": "tan_soft_leather",
            "completed_achievements": [],
        }
        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Leather"], 28)
        self.assertEqual(addon.player_data["inventory"]["Cowhide"], 2)
        self.assertEqual(addon.player_data["inventory"]["Coins"], 72)
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Cowhide": 30, "Coins": 100})
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_wool_gathering_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_wool_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.player_data = {
            "inventory": {},
            "crafting_exp": 0,
            "current_utility": "gather_wool",
            "completed_achievements": [],
        }
        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"], {"Wool": 28})
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {})
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_unrelated_undo_does_not_consume_review_snapshot(self):
        addon = _load_addon_as_package("ankiscape_unrelated_undo_integration")

        addon.save_player_data = lambda: self.fail("unrelated undo should not save")
        addon.player_data = {
            "inventory": {"Logs": 0, "Arrow shafts": 15},
            "fletching_level": 1,
            "fletching_exp": 5.0,
            "current_fletch": "arrow_shafts",
        }
        addon._REVIEW_UNDO_STACK.append(
            {
                "values": {"inventory": {"Logs": 1}, "fletching_exp": 0},
                "remove": [],
            }
        )

        changes = types.SimpleNamespace(
            operation="Edit Note",
            changes=types.SimpleNamespace(study_queues=False, card=False),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertEqual(addon.player_data["fletching_exp"], 5.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)


if __name__ == "__main__":
    unittest.main()
