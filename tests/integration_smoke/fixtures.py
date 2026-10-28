import json
import unittest
from tests.test_integration_smoke import _install_runtime_fakes, sys


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


class ReviewedProfile(TestIntegrationSmoke):
    """A fresh profile answered through the real review handler, saved as JSON."""

    def _addon(self, name):
        from tests.test_integration_smoke import _DummyCol, _DummyMW, _load_addon_as_package, types

        class _JsonCol(_DummyCol):
            # Anki stores the save as JSON, so only JSON survives a profile reload.
            def set_config(self, key, value):
                super().set_config(key, json.loads(json.dumps(value)))

        addon = _load_addon_as_package(name)
        addon.mw = _DummyMW(_JsonCol({"ankiscape_review_action_multiplier": 1}))
        addon.mw.exp_popup = types.SimpleNamespace(show_text=lambda _text: None)
        sys.modules[f"{name}.core.storage"].mw = addon.mw
        self.errors = []
        addon.show_error_message = lambda title, message: self.errors.append((title, message))
        self.bankstanding_dialogs = []
        addon.ui.show_bankstanding_dialog = self.bankstanding_dialogs.append
        addon._refresh_skill_availability = lambda: None
        return addon

    def _new_save(self, addon, **fields):
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        save = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        save.update(fields)
        addon._state.player_data = save

    def _answer(self, addon):
        from tests.test_integration_smoke import _FakeReviewer

        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
