"""Daily content takes the share of XP a 2.4-hour 2012 player got (plan Part J item 3).

The reference player is a fisher who starts at Fishing 80, the level Fable's
pace design prices Fish Flingers at, and has trained nothing else and done no
quests. At the default speed 10 with a 240-card world day, the fisher plays the
two Fish Flingers games that each day's tickets allow, spots the week's whole
Penguin Hide and Seek roster and redeems the points for Fishing XP. That is all
the daily and weekly content open to this player: Tears of Guthix needs its
quest, Big Top Bonanza needs level 10 in the performance's skill and Skeletal
Horror is a boss fight. The rest of each day is spent catching sharks, a
rate-limited route, dropping the catch so that no bank trip interrupts it.

A seventh of a Penguin roster cannot be played, so the test plays a whole world
week; the week's share is the one-day share with each weekly allowance divided
by 7. The 2012 player's share is
``daily / (daily + (play time - time on daily content) x catalog hourly rate)``:
the grinding fills what the daily content leaves of the day, as in Fable's
table (its 112,000 XP is 2.24 of the 2.4 hours at 50,000 XP an hour).
"""

import random
from fractions import Fraction

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.fish_flingers_data import FISH_FLINGERS_EVENT_TICKS, FISH_FLINGERS_TICKETS_PER_DAY
from ankiscape.logic.cadence_shadow import resolve_cadence_shadow_rate_pure
from ankiscape.logic.fish_flingers_logic import enter_fish_flingers_pure
from ankiscape.logic.pace.short_timers import card_ticks_pure
from ankiscape.logic.pace.world_clock import (
    CALENDAR_TICKS_PER_DAY,
    DAYS_PER_WEEK,
    DEFAULT_WORLD_DAY_CARDS,
    answered_cards_pure,
    hours_of_play_per_world_day_pure,
    world_day_index_pure,
)
from ankiscape.logic.penguin_hide_and_seek_logic import apply_penguin_command_pure, penguin_view_pure
from tests.pace.test_lump_rewards import _ACTIVITIES, _xp
from tests.pace.test_short_timers import _HostCase

SPEED = 10
TICKS_PER_HOUR = CALENDAR_TICKS_PER_DAY // 24
SHARKS = resolve_cadence_shadow_rate_pure("fishing", "catch_sharks")


def _reference_fisher() -> dict:
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(
        fishing_level=80,
        fishing_exp=float(EXP_TABLE[79]),
        current_fishing="catch_sharks",
        carried_keep_drop={"catch_sharks": "drop"},
    )
    return player


class DailyShareTests(_HostCase):
    def setUp(self):
        super().setUp()
        # addon.random is the process-wide module; the seed must not leak out.
        self.addCleanup(random.setstate, random.getstate())
        random.seed(2012)
        self.addon = self._addon(SPEED, _reference_fisher())

    def _play(self, skill: str, done) -> float:
        """Answer cards on ``skill`` until ``done(player_data)``; return the XP gained."""
        addon = self.addon
        addon._state.current_skill = skill
        before = _xp(addon)
        while not done(self._answer(addon, 3)):
            self.assertEqual(addon._state.current_skill, skill)
        return _xp(addon) - before

    def _command(self, command, *args) -> None:
        player, ok, info = command(self.addon._state.player_data, *args)
        self.assertTrue(ok, info)
        self.addon._state.player_data = player

    def _spot_the_roster(self) -> tuple[float, int]:
        """Spot every penguin of the week, one card each; return the XP redeemed and the cards."""
        addon = self.addon
        addon._state.player_data["current_utility"] = "penguin_hide_and_seek"
        roster = penguin_view_pure(addon._state.player_data)["roster"]
        for row in roster:
            self._command(apply_penguin_command_pure, "select_spy", {"spawn_id": row["id"]})
            self._play(_ACTIVITIES, lambda _player: True)
        before = _xp(addon)
        self._command(apply_penguin_command_pure, "redeem_xp", {"skill_id": "fishing"})
        return _xp(addon) - before, len(roster)

    def test_a_world_week_at_speed_10_gives_daily_content_its_2012_share(self):
        daily, penguins = self._spot_the_roster()
        grinding = 0.0
        for day in range(DAYS_PER_WEEK):
            for _game in range(FISH_FLINGERS_TICKETS_PER_DAY):
                self._command(enter_fish_flingers_pure)
                daily += self._play(_ACTIVITIES, lambda player: not player["fish_flingers"])
            grinding += self._play("Fishing", lambda player, day=day: world_day_index_pure(player) > day)
        self.assertEqual(answered_cards_pure(self.addon._state.player_data), DAYS_PER_WEEK * DEFAULT_WORLD_DAY_CARDS)

        games = DAYS_PER_WEEK * FISH_FLINGERS_TICKETS_PER_DAY
        content_ticks = games * FISH_FLINGERS_EVENT_TICKS + penguins * card_ticks_pure(SPEED)
        play_hours = DAYS_PER_WEEK * hours_of_play_per_world_day_pure(DEFAULT_WORLD_DAY_CARDS, SPEED)
        hourly_rate = Fraction(*SHARKS["source_low_xp_hour"])
        expected_grinding = (play_hours - content_ticks / TICKS_PER_HOUR) * hourly_rate
        # A game ends on the card that crosses its ten minutes, and sharks are caught whole.
        rounding = games * card_ticks_pure(SPEED) / TICKS_PER_HOUR * hourly_rate + Fraction(*SHARKS["source_xp_per_action"])

        def share(grinding_xp: float) -> float:
            return daily / (daily + grinding_xp)

        self.assertGreater(daily, 0)
        self.assertAlmostEqual(
            share(grinding),
            share(expected_grinding),
            delta=share(expected_grinding - rounding) - share(expected_grinding),
            msg=f"daily {daily:.0f} XP, grinding {grinding:.0f} XP, 2012 grinding {expected_grinding:.0f} XP",
        )
