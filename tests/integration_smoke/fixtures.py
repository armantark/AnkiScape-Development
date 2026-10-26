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
