"""A resolved world event holds its outcome in the Activities strip briefly.

Removing the floating popups left Big Chinchompa's competence award with no
reviewer-side signal at all: `ui._world_event_rows` listed an event only while it
was active, so the award landed silently and you had to go looking on the
activity card. Shooting Star never had the problem because its post-active
`sprite_available` state keeps it in the strip; this gives the same treatment to
a resolution.

No Qt needed — `_world_event_rows` is the shared projection behind both the strip
and the reviewer badge, so this runs in the default lane.
"""

from __future__ import annotations

import os
import sys
import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ADDON_DIR = os.path.dirname(_THIS_DIR)
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

import ui
from big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from constants import ITEM_DEFINITIONS, ORE_DATA
from storage_pure import default_player_data


_RESULT = (
    "Big Chinchompa ended: 1,200 event points became 48 Competence points."
)


def _resolved_player(answered: int, *, resolved_at: int = 100) -> dict:
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    state = dict(player.get("big_chinchompa") or {})
    state.update({
        "last_resolved_slot_card": resolved_at,
        "last_result": _RESULT,
        "active_event": {},
    })
    player["big_chinchompa"] = state
    player["shop_market_clock"] = {
        "answered_cards": answered,
        "market_tick": answered,
    }
    return player


class WorldEventOutcomeWindowTest(unittest.TestCase):
    def test_the_resolution_card_itself_reports(self):
        """Regression: 0 reviews ago was being read as "never resolved".

        The count was read with `int(view.get(key, -1) or -1)`, and the
        resolution card reports exactly 0, which is falsy — so that idiom
        silenced the single review where the award actually landed.
        """
        rows = ui._world_event_rows(_resolved_player(100))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], BIG_CHINCHOMPA_UTILITY_ID)
        self.assertIn("Competence points", rows[0][1])

    def test_the_outcome_persists_then_clears(self):
        for ago, still_shown in ((0, True), (1, True), (9, True), (10, False), (60, False)):
            with self.subTest(reviews_ago=ago):
                rows = ui._world_event_rows(_resolved_player(100 + ago))
                self.assertEqual(bool(rows), still_shown)

    def test_the_window_matches_the_named_constant(self):
        """Pin the boundary to the constant so the two cannot drift apart."""
        last = ui._WORLD_EVENT_OUTCOME_REVIEWS - 1
        self.assertTrue(ui._world_event_rows(_resolved_player(100 + last)))
        self.assertFalse(
            ui._world_event_rows(
                _resolved_player(100 + ui._WORLD_EVENT_OUTCOME_REVIEWS)
            )
        )

    def test_an_event_that_never_resolved_reports_nothing(self):
        player = _resolved_player(40, resolved_at=0)
        player["big_chinchompa"]["last_result"] = ""
        self.assertEqual(ui._world_event_rows(player), ())

    def test_the_activity_page_suppresses_its_own_row(self):
        """The strip must not repeat what the open card already shows."""
        rows = ui._world_event_rows(
            _resolved_player(102), suppress_id=BIG_CHINCHOMPA_UTILITY_ID
        )
        self.assertEqual(rows, ())


if __name__ == "__main__":
    unittest.main()
