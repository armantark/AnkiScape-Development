"""Magic's real answer path keeps the reason that ends a card early."""

from unittest.mock import patch

from tests.pace.test_short_timers import _HostCase
from tests.test_combat_logic import _player


class MagicContinuationStopTests(_HostCase):
    def test_running_card_keeps_out_of_runes_after_the_last_cast(self):
        player = _player(magic_level=99, magic_exp=0.0, current_magic="low_alchemy",
                         magic_alchemy_item="Logs",
                         inventory={"Fire rune": 3, "Nature rune": 1, "Logs": 2})
        addon = self._addon(10, player)
        addon._state.current_skill = "Magic"
        contexts = []
        spend = addon._spend_card_on_action

        def record(ctx, key, handler):
            contexts.append(ctx)
            return spend(ctx, key, handler)

        with patch.object(addon, "_spend_card_on_action", record):
            after = self._answer(addon, 3)
        self.assertEqual(after["magic_actions_completed"], 1)
        self.assertEqual(after["magic_exp"], 31.0)
        self.assertEqual(after["inventory"].get("Nature rune", 0), 0)
        self.assertEqual(after["inventory"]["Logs"], 1)
        self.assertEqual(contexts[-1].card.ticks_remaining, 54)
        self.assertEqual(contexts[-1].card.stop_reason, "out_of_runes")
