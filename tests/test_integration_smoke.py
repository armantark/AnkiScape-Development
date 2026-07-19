import copy
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
        self.assertEqual(calls["good_answer"], 1)

        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(calls["good_answer"], 2)

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
        self.assertEqual(
            addon.player_data["achievement_progress"]["skills"]["firemaking"]["outputs"]["Ashes"],
            1,
        )
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
        self.assertEqual(
            addon.player_data["achievement_progress"]["skills"]["runecrafting"]["outputs"]["Air rune"],
            27,
        )
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
        addon.level_up_check = lambda _skill, _data: None
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
        self.assertEqual(addon.player_data["prayer_exp"], 1406.0)
        self.assertEqual(addon.player_data["pending_skill_exp_rewards"], {})
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {},
            "current_quest": "stolen_hearts",
            "quests": {
                "stolen_hearts": {
                    "started": True,
                    "progress": 3,
                    "completed": False,
                }
            },
            "quest_combat_config": {"resolver_enabled": True},
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
                addon.player_data["quests"]["stolen_hearts"]["progress"],
                3,
            )

        addon.on_quest_answer()

        self.assertEqual(addon.player_data["quests"]["stolen_hearts"]["progress"], 4)
        self.assertEqual(addon.player_data["inventory"]["Ransom note"], 1)
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
        addon.current_skill = "Quests"
        addon.player_data = {
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
            "quest_combat_config": {"resolver_enabled": True},
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
                addon.player_data["quests"]["diamond_in_the_rough"]["progress"],
                2,
            )

        addon.on_quest_answer()

        self.assertEqual(
            addon.player_data["quests"]["diamond_in_the_rough"]["progress"],
            3,
        )
        self.assertEqual(addon.player_data["inventory"]["Sundial gnomon"], 1)
        self.assertEqual(addon.player_data["inventory"]["Waterskin (4)"], 4)
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
        addon.current_skill = "Quests"
        addon.player_data = {
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
            "quest_combat_config": {"resolver_enabled": True},
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
            addon.player_data["quests"]["icthlarins_little_helper"]["progress"],
            4,
        )
        self.assertEqual(addon.player_data["inventory"].get("Canopic jar", 0), 0)
        self.assertEqual(addon.player_data["inventory"].get("Sphinx's token", 0), 0)

        addon.on_quest_answer()
        self.assertEqual(calls["gains"][-1], "Defeated Canopic guardian")
        self.assertEqual(
            addon.player_data["quests"]["icthlarins_little_helper"]["progress"],
            4,
        )

        addon.on_quest_answer()

        self.assertEqual(
            addon.player_data["quests"]["icthlarins_little_helper"]["progress"],
            5,
        )
        self.assertEqual(addon.player_data["inventory"]["Canopic jar"], 1)

        addon.on_quest_answer()

        self.assertEqual(
            addon.player_data["quests"]["icthlarins_little_helper"]["progress"],
            6,
        )
        self.assertEqual(
            addon.player_data["inventory"]["Holy symbol (Icthlarin's Little Helper)"],
            1,
        )
        self.assertEqual(addon.player_data["inventory"].get("Bucket", 0), 0)
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Masked earmuffs": 1},
            "current_quest": "smoking_kills",
            "quests": {
                "smoking_kills": {
                    "started": True,
                    "progress": 9,
                    "completed": False,
                },
            },
            "quest_combat_config": {"resolver_enabled": True},
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
        self.assertEqual(addon.player_data["quests"]["smoking_kills"]["progress"], 9)

        addon.on_quest_answer()

        self.assertEqual(addon.player_data["quests"]["smoking_kills"]["progress"], 10)
        self.assertEqual(addon.player_data["inventory"]["Banshee voice"], 1)
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
        addon.current_skill = "Quests"
        addon.player_data = {
            "inventory": {"Bone key": 1, "Beads of the dead": 1},
            "current_quest": "shilo_village",
            "quests": {
                "shilo_village": {
                    "started": True,
                    "progress": 10,
                    "completed": False,
                },
            },
            "quest_combat_config": {"resolver_enabled": True},
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
            self.assertEqual(addon.player_data["quests"]["shilo_village"]["progress"], 10)

        addon.on_quest_answer()

        self.assertEqual(addon.player_data["quests"]["shilo_village"]["progress"], 11)
        self.assertEqual(addon.player_data["inventory"]["Rashiliyia corpse"], 1)
        self.assertEqual(calls["gains"][-1], "Shilo Village 11/12")
        self.assertEqual(calls["save"], 4)
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
        self.assertEqual(addon.player_data["prayer_exp"], 11000.0)
        self.assertEqual(addon.player_data["pending_skill_exp_rewards"], {})
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
        addon.current_skill = "Utility / Activities"
        addon.player_data = {"inventory": {}, "current_utility": "make_soft_clay", "completed_achievements": []}

        addon.on_utility_answer()

        self.assertEqual(addon.current_skill, "Utility / Activities")
        self.assertEqual(addon.player_data["current_utility"], "bankstanding")
        self.assertEqual(len(errors), 1)
        self.assertIn("Bankstanding", errors[0][1])
        self.assertIn("Clay", errors[0][1])

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
        addon.current_skill = "Crafting"
        addon.player_data = {
            "inventory": {"Soft clay": 231},
            "crafting_level": 50,
            "current_craft": "fire_empty_pot",
            "completed_achievements": [],
        }

        addon.on_crafting_answer()

        self.assertEqual(addon.current_skill, "Utility / Activities")
        self.assertEqual(addon.player_data["current_utility"], "bankstanding")
        self.assertEqual(len(errors), 1)
        self.assertIn("Pot (unfired)", errors[0][1])
        self.assertIn("Bankstanding", errors[0][1])

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
        self.assertIs(addon._registered_answer_handler("Thieving"), addon.runtime_actions.handle_thieving_answer)

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
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon.player_data["woodcutting_exp"], 25.0)
        self.assertAlmostEqual(addon.player_data["fletching_exp"], 5.0)
        self.assertEqual(calls["xp"], [25.0, 5.0])

    def test_thieving_failure_is_one_attempt_under_multiplier_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_thieving_review_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_farming_hud_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon.player_data = {
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
        initial_state = copy.deepcopy(addon.player_data)
        addon.current_skill = "Thieving"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        original_random = addon.random.random
        rolls = iter((0.999, 0.0))
        addon.random.random = lambda: next(rolls)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["thieving_attempt_count"], 1)
        self.assertEqual(addon.player_data["thieving_failure_count"], 1)
        self.assertEqual(addon.player_data["combat_lifepoints"], 90)
        self.assertTrue(addon.player_data["thieving_stunned"])
        self.assertEqual(addon.player_data["thieving_exp"], 0.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon.player_data, initial_state)
        self.assertEqual(addon.current_skill, "Thieving")
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])

    def test_thieving_success_and_stall_cadence_ignore_review_multiplier(self):
        addon = _load_addon_as_package("ankiscape_thieving_multiplier_cap_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_farming_hud_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon.current_skill = "Thieving"

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.player_data = {
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
            addon.card_turned = True
            addon.answer_shown = True
            addon.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

            self.assertEqual(addon.player_data["thieving_attempt_count"], 1)
            self.assertEqual(addon.player_data["thieving_success_count"], 1)
            self.assertEqual(addon.player_data["inventory"]["Coins"], 3)
            self.assertEqual(addon.player_data["thieving_exp"], 8.0)

            addon.player_data = {
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
            addon.card_turned = True
            addon.answer_shown = True
            addon.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["thieving_attempt_count"], 1)
        self.assertEqual(addon.player_data["thieving_success_count"], 1)
        self.assertEqual(addon.player_data["inventory"]["Silver ore"], 1)
        self.assertEqual(addon.player_data["thieving_exp"], 54.0)
        self.assertEqual(
            addon.player_data["cadence_profiles"]["thieving:stall_silver"]["assigned_reviews"],
            1,
        )

    def test_wall_safe_failure_consumes_one_multiplied_review_and_undoes_cadence(self):
        addon = _load_addon_as_package("ankiscape_wall_safe_review_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_farming_hud_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon.player_data = {
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
        initial_state = copy.deepcopy(addon.player_data)
        addon.current_skill = "Thieving"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        original_random = addon.random.random
        rolls = iter((85 / 255, 0.0))
        addon.random.random = lambda: next(rolls)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["thieving_attempt_count"], 1)
        self.assertEqual(addon.player_data["thieving_failure_count"], 1)
        self.assertEqual(addon.player_data["combat_lifepoints"], 80)
        self.assertTrue(addon.player_data["thieving_stunned"])
        self.assertEqual(
            addon.player_data["cadence_profiles"]["thieving:wall_safe"]["assigned_reviews"],
            1,
        )

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon.player_data, initial_state)
        self.assertEqual(addon.current_skill, "Thieving")

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
        addon.player_data = {
            "inventory": copy.deepcopy(inventory),
            "current_utility": "bankstanding",
            "completed_achievements": [],
        }
        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon.player_data["inventory"], inventory)
        self.assertEqual(
            addon.player_data["shop_market_clock"]["market_tick"],
            1,
        )
        self.assertEqual(
            addon.player_data["ge_market_state"]["last_processed_tick"],
            1,
        )
        self.assertEqual(calls["gains"], [
            "Bankstanding — no XP gained."
        ])

    def test_material_exhaustion_falls_back_once_then_bankstands(self):
        addon = _load_addon_as_package(
            "ankiscape_material_fallback_bankstanding_integration"
        )
        calls = {"errors": [], "gains": []}
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
        addon.player_data = {
            "inventory": {"Soft clay": 20},
            "crafting_level": 50,
            "current_craft": "fire_empty_pot",
            "completed_achievements": [],
        }
        addon.current_skill = "Crafting"

        for _review in range(2):
            addon.card_turned = True
            addon.answer_shown = True
            addon.exp_awarded = False
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )

        self.assertEqual(addon.current_skill, "Utility / Activities")
        self.assertEqual(addon.player_data["current_utility"], "bankstanding")
        self.assertEqual(len(calls["errors"]), 1)
        self.assertIn("Bankstanding", calls["errors"][0][1])
        self.assertEqual(
            calls["gains"],
            ["Bankstanding — no XP gained."],
        )
        self.assertEqual(
            addon.player_data["shop_market_clock"]["market_tick"],
            2,
        )
        self.assertEqual(
            addon.player_data["ge_market_state"]["last_processed_tick"],
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
        addon.player_data = {
            "inventory": {"Dragon bones": 1},
            "prayer_level": 1,
            "prayer_exp": 0,
            "current_prayer": "bury_dragon_bones",
            "completed_achievements": [],
        }
        addon.current_skill = "Prayer"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Dragon bones"], 0)
        self.assertEqual(addon.player_data["prayer_exp"], 72.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon.player_data["inventory"], {"Dragon bones": 1})
        self.assertEqual(addon.player_data["prayer_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
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
        addon.player_data = copy.deepcopy(initial)
        addon.current_skill = "Mining"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        rolls = iter((0.0, 0.0, 1.0, 0.0))
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"]["Copper ore"], 1)
        self.assertEqual(addon.player_data["inventory"]["Cracked mining urn"], 1)
        self.assertEqual(addon.player_data["active_urn_mining"], "mining_cracked_urn")
        self.assertEqual(addon.player_data["urn_progress_mining"], 17.5)
        self.assertEqual(addon.player_data["mining_exp"], 17.5)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])

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
        addon.player_data = copy.deepcopy(initial)
        addon.current_skill = "Combat"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        rolls = iter((0.0, 0.999999, 0.0) * 1000)
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        kills = addon.player_data["combat_kill_counts"]["chicken"]
        self.assertGreater(kills, 0)
        self.assertEqual(addon.player_data["prayer_exp"], 4.5 * kills)
        self.assertEqual(addon.player_data["prayer_bonecrusher_triggers"], kills)
        self.assertEqual(addon.player_data["prayer_actions_completed"], kills)
        self.assertNotIn("Bones", addon.player_data["inventory"])
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])

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
        addon.player_data = copy.deepcopy(initial)
        addon.current_skill = "Combat"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

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

        kills = addon.player_data["combat_kill_counts"]["ghost"]
        self.assertGreater(kills, 0)
        self.assertEqual(addon.player_data["prayer_exp"], 4.5 * kills)
        self.assertEqual(addon.player_data["prayer_ectoplasmator_triggers"], kills)
        self.assertEqual(addon.player_data["prayer_actions_completed"], kills)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])

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
        addon.player_data = {
            "inventory": {"Plank": 2, "Rune nails": 2},
            "construction_level": 1, "construction_exp": 0,
            "current_construction": "crude_wooden_chair",
            "house_owned": True, "house_rooms_bought": {"parlour": True, "garden": True},
            "house_servant": "", "house_built_flags": {}, "quests": {},
            "completed_achievements": [],
        }
        addon.current_skill = "Construction"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.999999
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random
        self.assertEqual(addon.player_data["inventory"]["Plank"], 0)
        self.assertEqual(addon.player_data["construction_exp"], 66.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon.player_data["inventory"], {"Plank": 2, "Rune nails": 2})
        self.assertEqual(addon.player_data["construction_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])

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
        addon.player_data = {
            "inventory": {"Logs": 2},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
            "magic_charge_active": True,
            "magic_charge_ticks_remaining": 100,
        }
        initial_state = copy.deepcopy(addon.player_data)
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertFalse(addon.player_data["magic_charge_active"])
        self.assertEqual(addon.player_data["magic_charge_ticks_remaining"], 0)
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 30)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon.player_data, initial_state)

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
            {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "finishers": {}, "hazards": {}, "cannonballs": 0},
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

        calls = {"save": 0, "errors": [], "achievement_coins": []}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.check_achievements = lambda data: calls["achievement_coins"].append(data["inventory"]["Coins"])
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
        self.assertEqual(calls["achievement_coins"], [50])

    def test_combat_loadout_menu_callbacks_refill_and_unload_supplies(self):
        addon = _load_addon_as_package("ankiscape_combat_loadout_callbacks")

        calls = {"save": 0, "hud": 0, "refresh": 0, "achievement_runes": []}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.check_achievements = lambda data: calls["achievement_runes"].append(
            data["inventory"].get("Air rune", 0) + data["inventory"].get("Mind rune", 0)
        )
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
            {"food": {}, "potions": {}, "stat_potions": {}, "ammo": {}, "runes": {}, "finishers": {}, "hazards": {}, "cannonballs": 0},
        )
        self.assertEqual(addon.player_data["inventory"]["Shark"], 30)
        self.assertEqual(addon.player_data["inventory"]["Antipoison (2)"], 1)
        self.assertEqual(addon.player_data["inventory"]["Air rune"], 5)
        self.assertEqual(addon.player_data["inventory"]["Mind rune"], 5)
        self.assertEqual(calls["achievement_runes"], [10])
        self.assertGreaterEqual(calls["save"], 4)
        self.assertGreaterEqual(calls["hud"], 4)
        self.assertGreaterEqual(calls["refresh"], 4)

    def test_firemaking_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_firemaking_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        achievements = sys.modules[f"{addon.__name__}.constants"].ACHIEVEMENTS
        def complete_first_fire(data):
            if achievements["First Fire"]["condition"](data):
                data["completed_achievements"].append("First Fire")
        addon.check_achievements = complete_first_fire
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
        self.assertEqual(
            addon.player_data["achievement_progress"]["skills"]["firemaking"]["outputs"],
            {"Ashes": 1},
        )
        self.assertIn("First Fire", addon.player_data["completed_achievements"])
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Logs": 1})
        self.assertEqual(addon.player_data["firemaking_exp"], 0)
        self.assertNotIn("achievement_progress", addon.player_data)
        self.assertEqual(addon.player_data["completed_achievements"], [])
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

        addon.player_data = {
            "inventory": {"Cheese wheel": 1},
            "cooking_level": 48,
            "cooking_exp": 0.0,
            "current_cooking": "slice_cheese_wheel",
            "completed_achievements": [],
        }
        addon.current_skill = "Cooking"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

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
            addon.player_data["inventory"],
            {"Cheese wheel": 0, "Cheese": 5},
        )
        self.assertEqual(addon.player_data["cooking_exp"], 20.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)
        self.assertEqual(calls["activity"], ["+5 Cheese"])

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Cheese wheel": 1})
        self.assertEqual(addon.player_data["cooking_exp"], 0.0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
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
        addon.player_data = {
            "inventory": ingredients.copy(),
            "herblore_level": 94,
            "herblore_exp": 0,
            "current_herblore": "finished_super_prayer",
            "completed_achievements": [],
        }
        addon.current_skill = "Herblore"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Prayer potion (3)"], 0)
        self.assertEqual(addon.player_data["inventory"]["Wyvern bonemeal"], 0)
        self.assertEqual(addon.player_data["inventory"]["Bonemeal"], 5)
        self.assertEqual(addon.player_data["inventory"]["Super prayer (3)"], 1)
        self.assertEqual(addon.player_data["herblore_exp"], 270.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], ingredients)
        self.assertEqual(addon.player_data["herblore_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
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
        addon.player_data = {
            "inventory": ingredients.copy(),
            "herblore_level": 52,
            "herblore_exp": 0,
            "current_herblore": "finished_shrink_me_quick",
            "completed_achievements": [],
        }
        addon.current_skill = "Herblore"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Tarromin potion (unf)"], 0)
        self.assertEqual(addon.player_data["inventory"]["Shrunk ogleroot"], 0)
        self.assertEqual(addon.player_data["inventory"]["Shrink-me-quick"], 1)
        self.assertEqual(addon.player_data["herblore_exp"], 6.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], ingredients)
        self.assertEqual(addon.player_data["herblore_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
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
        addon.player_data = {
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
        before = copy.deepcopy(addon.player_data)
        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon.player_data["livid_farm"]["cycles_completed"], 1)
        self.assertEqual(addon.player_data["livid_farm"]["produce_points"], 1_580)
        self.assertAlmostEqual(addon.player_data["magic_exp"], 3_737.0)
        self.assertAlmostEqual(addon.player_data["agility_exp"], 509.1)
        self.assertAlmostEqual(addon.player_data["crafting_exp"], 1_080.0)
        self.assertAlmostEqual(addon.player_data["farming_exp"], 2_754.0)
        self.assertAlmostEqual(addon.player_data["construction_exp"], 546.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data, before)
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

    def test_lamp_oil_preparation_review_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_lamp_oil_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.player_data = {
            "inventory": {"Bullseye lantern (empty)": 1, "Swamp tar": 1},
            "current_utility": "fill_bullseye_lantern",
            "completed_achievements": [],
        }
        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(
            addon.player_data["inventory"],
            {"Bullseye lantern (empty)": 0, "Swamp tar": 0, "Bullseye lantern (unlit)": 1},
        )
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(
            addon.player_data["inventory"],
            {"Bullseye lantern (empty)": 1, "Swamp tar": 1},
        )
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

    def test_cure_plant_runtime_cast_and_answer_undo_are_atomic(self):
        addon = _load_addon_as_package("ankiscape_cure_plant_undo_integration")
        farming_logic = sys.modules[f"{addon.__name__}.farming_logic"]
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
        addon.player_data = state
        addon.current_skill = "Magic"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertFalse(addon.player_data["farm_patches"]["falador_allotment_north"]["diseased"])
        self.assertEqual(addon.player_data["inventory"]["Astral rune"], 0)
        self.assertEqual(addon.player_data["inventory"]["Earth rune"], 0)
        self.assertEqual(addon.player_data["magic_exp"], 60.0)
        self.assertEqual(calls["save"], 1)
        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon.player_data, before)

    def test_queued_farming_dig_up_preempts_one_review_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_farming_dig_up_undo_integration")
        farming_logic = sys.modules[f"{addon.__name__}.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_farming_hud_badge = lambda *_args: None
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
        addon.player_data = state
        addon.current_skill = "Mining"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertIsNone(addon.player_data["farm_patches"]["champions_bush"]["crop_id"])
        self.assertEqual(addon.player_data["farming_counters"]["dig_ups"], 1)
        self.assertEqual(addon.player_data["farm_queue"], [])
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon.player_data, before)

    def test_queued_white_tree_harvest_preempts_one_review_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_white_tree_undo_integration")
        farming_logic = sys.modules[f"{addon.__name__}.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_farming_hud_badge = lambda *_args: None
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
        addon.player_data = state
        addon.current_skill = "Mining"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["White tree fruit"], 4)
        self.assertEqual(addon.player_data["farming_exp"], 48.0)
        self.assertEqual(
            addon.player_data["farm_patches"]["varrock_white_tree"]["produce_count"],
            0,
        )
        self.assertEqual(addon.player_data["farm_queue"], [])
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon.player_data, before)

    def test_prayer_composite_selection_persists_once_and_rejection_has_no_side_effects(self):
        addon = _load_addon_as_package("ankiscape_prayer_selection_integration")
        calls = {"save": 0, "hud": 0}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon.current_skill = "Prayer"
        target_id = "gilded_altar_dragon_bones"
        addon.player_data = {
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
            addon.player_data["prayer_owned_altar_stint"],
            {"target_id": target_id, "burners_lit": 1},
        )
        self.assertEqual(addon.player_data["prayer_gilded_house_search"]["reviews_remaining"], 2)

        self.assertTrue(addon.set_prayer_selection("dragon_bones", "gilded_hosted"))
        self.assertEqual(calls, {"save": 2, "hud": 2})
        self.assertEqual(addon.player_data["prayer_gilded_mode"], "hosted")
        self.assertEqual(addon.player_data["prayer_owned_altar_stint"], {})
        self.assertEqual(addon.player_data["prayer_gilded_house_search"], {})

        rejected_state = {"prayer_level": 99, "inventory": {"Dragon bones": 1}}
        addon.player_data = copy.deepcopy(rejected_state)
        self.assertFalse(addon.set_prayer_selection("dragon_bones", "gilded_owned"))
        self.assertEqual(addon.player_data, rejected_state)
        self.assertEqual(calls, {"save": 2, "hud": 2})

    def test_direct_urn_teleports_use_separate_custom_lifo_undo(self):
        addon = _load_addon_as_package("ankiscape_direct_urn_undo_integration")
        from urn_data import URN_TIERS_BY_ID

        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        col = _DummyCol()
        mw = _DummyMW(col)
        addon.mw = mw
        calls = {"save": 0, "hud": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon.update_farming_hud_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.current_skill = "Mining"
        initial = {
            "inventory": {tier.item_full: 2},
            "carried_inventory": {"copper": {tier.item_full: 2}},
            "current_ore": "copper",
            "mining_level": 1,
            "mining_exp": 0.0,
            "completed_achievements": [],
        }
        addon.player_data = copy.deepcopy(initial)
        addon._REVIEW_UNDO_STACK.append({"sentinel": True})

        self.assertTrue(addon.teleport_training_urn(tier.id))
        self.assertTrue(addon.teleport_training_urn(tier.id))
        self.assertEqual(col.custom_undo_entries, ["Teleport training urn", "Teleport training urn"])
        self.assertEqual(mw.undo_updates, 2)
        self.assertEqual(addon.player_data["inventory"][tier.item_full], 0)
        self.assertNotIn("copper", addon.player_data["carried_inventory"])
        self.assertEqual(addon.player_data["mining_exp"], tier.teleport_xp * 2)
        telemetry = addon.player_data["action_telemetry"]["actions"][f"mining:teleport_{tier.id}"]
        self.assertEqual((telemetry["attempts"], telemetry["successes"]), (2, 2))
        self.assertEqual(len(addon._URN_TELEPORT_UNDO_STACK), 2)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        undo = types.SimpleNamespace(operation="Teleport training urn")
        addon._on_state_did_undo(undo)
        self.assertEqual(addon.player_data["inventory"][tier.item_full], 1)
        self.assertEqual(addon.player_data["carried_inventory"]["copper"][tier.item_full], 1)
        self.assertEqual(addon.player_data["mining_exp"], tier.teleport_xp)
        self.assertEqual(len(addon._URN_TELEPORT_UNDO_STACK), 1)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(undo)
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._URN_TELEPORT_UNDO_STACK, [])
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)
        self.assertEqual(calls["xp"], [tier.teleport_xp, tier.teleport_xp])
        self.assertEqual(calls["save"], 4)

    def test_bank_kebab_uses_runtime_rng_and_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_consumable_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.current_skill = "Combat"
        initial = {
            "inventory": {"Kebab": 1},
            "constitution_level": 50,
            "combat_lifepoints": 100,
        }
        addon.player_data = copy.deepcopy(initial)
        original_random = addon.random.random
        addon.random.random = lambda: 0.5
        self.addCleanup(setattr, addon.random, "random", original_random)

        result = addon.on_consume_item("Kebab")

        self.assertEqual(result["healed"], 50)
        self.assertEqual(addon.player_data["combat_lifepoints"], 150)
        self.assertNotIn("Kebab", addon.player_data["inventory"])
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_bank_pack_open_all_uses_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_pack_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.current_skill = "Herblore"
        initial = {"inventory": {"Vial pack": 2, "Vial": 1}}
        addon.player_data = copy.deepcopy(initial)

        result = addon.on_open_item_pack("Vial pack", True)

        self.assertEqual(result["packs_opened"], 2)
        self.assertEqual(addon.player_data["inventory"], {"Vial": 101})
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon.player_data, initial)

    def test_bank_discard_x_preserves_remainder_and_uses_direct_action_undo(self):
        addon = _load_addon_as_package("ankiscape_discard_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.current_skill = "Cooking"
        initial = {"inventory": {"Shrimps": 5}}
        addon.player_data = copy.deepcopy(initial)

        self.assertTrue(addon.on_discard_item("Shrimps", 2))
        self.assertEqual(addon.player_data["inventory"]["Shrimps"], 3)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

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
        addon.player_data = copy.deepcopy(initial)
        addon.current_skill = "Agility"
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
        self.assertEqual(addon.player_data["agility_exp"], 250.0)
        self.assertEqual(addon.player_data["agility_level"], 3)
        self.assertEqual(calls, {"levels": ["Agility"], "achievement_levels": [3], "xp": [250.0]})
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(addon.mw.undo_updates, 1)
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_stronghold_reward_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_stronghold_reward_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        initial = {
            "inventory": {"Coins": 5},
            "stronghold_of_security": {"step": 4, "completed": True, "boots_choice": None},
            "completed_achievements": [],
        }
        addon.player_data = copy.deepcopy(initial)
        addon.current_skill = "Mining"
        addon.ui.show_stronghold_reward_dialog = lambda: "Fancy boots"
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None

        self.assertTrue(addon._claim_stronghold_reward())
        self.assertEqual(addon.player_data["inventory"]["Coins"], 5 + addon.STRONGHOLD_REWARD_COINS)
        self.assertEqual(addon.player_data["inventory"]["Fancy boots"], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(addon.mw.undo_updates, 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_mage_arena_statue_switch_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_mage_arena_cape_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.current_skill = "Magic"
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
        addon.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None

        addon._on_main_menu()
        apply_action = captured["on_mage_arena_action"]
        self.assertTrue(apply_action("cape", "guthix"))
        self.assertEqual(addon.player_data["mage_arena"]["alignment"], "guthix")
        self.assertEqual(addon.player_data["inventory"]["Saradomin cape"], 0)
        self.assertEqual(addon.player_data["inventory"]["Guthix cape"], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_slayer_assignment_roll_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_slayer_assignment_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.current_skill = "Combat"
        initial = {
            "inventory": {},
            "quests": {},
            "slayer_level": 1,
            "slayer_exp": 0.0,
            "slayer_assignment": {},
            "smithing_level": 1,
        }
        addon.player_data = copy.deepcopy(initial)
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
        self.assertEqual(addon.player_data["slayer_assignment"]["family_id"], "bats")
        self.assertEqual(addon.player_data["slayer_assignment"]["remaining"], 15)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_grand_exchange_offer_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_grand_exchange_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.current_skill = "Utility / Activities"
        initial = {
            "inventory": {"Coins": 10_000},
            "smithing_level": 1,
        }
        addon.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None

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
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

        result = captured["on_ge_action"]("place_offer", payload)
        self.assertTrue(result["ok"])
        self.assertEqual(
            addon.player_data["inventory"]["Coins"],
            10_000 - guide_price,
        )
        self.assertEqual(len(addon.player_data["ge_player_orders"]), 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_combat_current_target_drives_main_menu_carried_pack_callbacks(self):
        addon = _load_addon_as_package("ankiscape_combat_carried_target_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        save_calls = []
        addon.save_player_data = lambda: save_calls.append(copy.deepcopy(addon.player_data))
        addon.current_skill = "Combat"
        addon.player_data = {
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
        self.assertEqual(save_calls, [addon.player_data])
        self.assertTrue(captured["carried_pack_target_active"])
        self.assertTrue(captured["carried_advanced_state"])
        cells = captured["get_carried_layout_cells"]()
        self.assertIn(("Bonecrusher", 1), cells)
        self.assertNotIn(("Bones", 1), cells)
        self.assertTrue(captured["on_set_carried_layout_quantity"]("Ectoplasmator", 4))
        self.assertEqual(
            addon.player_data["carried_layout"]["ghost"],
            {"Bonecrusher": 1, "Ectoplasmator": 4},
        )
        self.assertIn("Air rune", captured["carried_stackable_names"])

    def test_agility_current_target_projects_auto_food_requirements_and_weight_in_main_menu(self):
        addon = _load_addon_as_package("ankiscape_agility_carried_target_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon.current_skill = "Agility"
        addon.player_data = {
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

    def test_agility_main_menu_summary_ignores_stale_carried_items(self):
        addon = _load_addon_as_package("ankiscape_agility_stale_carried_summary")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon.current_skill = "Agility"
        addon.player_data = {
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
        addon.player_data = copy.deepcopy(initial)
        addon.current_skill = "Agility"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        rolls = iter((0.99, 0.0, 0.005, 0.90) + (0.5,) * 100)
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["agility_exp"], 0.0)
        self.assertEqual(addon.player_data["agility_lap_counts"]["total"], 0)
        self.assertEqual(addon.player_data["agility_effect_charges"]["Penance horn"], 2)
        self.assertEqual(
            addon.player_data["combat_grave"]["source"],
            "agility_wilderness_pker",
        )
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])

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
        addon.player_data = copy.deepcopy(initial)
        addon.current_skill = "Agility"
        addon.random.seed(314159)
        before_rng = addon.random.getstate()

        self.assertTrue(
            addon.resolve_review_context_action("pit_reward", "gamble")
        )

        self.assertNotIn(
            "pit_reward",
            addon.player_data["agility_activity_state"],
        )
        self.assertEqual(
            addon.player_data["review_context_preferences"]["pit_reward"],
            "gamble",
        )
        self.assertIn(shown_xp[-1], {50.0, 100.0, 200.0})
        self.assertEqual(
            addon.player_data["agility_exp"],
            10.0 + shown_xp[-1],
        )
        self.assertNotEqual(addon.random.getstate(), before_rng)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon.random.getstate(), before_rng)
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

    def test_ignored_pit_reward_resolves_on_next_answer_and_review_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_pit_context_review_integration")
        addon.mw = _DummyMW(_DummyCol())
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_farming_hud_badge = lambda *_args: None
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
        addon.player_data = copy.deepcopy(initial)
        addon.current_skill = "None"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            1,
            lambda _self, _ease: "answered",
        )

        self.assertNotIn(
            "pit_reward",
            addon.player_data["agility_activity_state"],
        )
        self.assertEqual(addon.player_data["agility_exp"], 110.0)
        self.assertEqual(shown_xp, [100.0])
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])

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
            operation="Set Due Date",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertEqual(addon.player_data["fletching_exp"], 5.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)


if __name__ == "__main__":
    unittest.main()
