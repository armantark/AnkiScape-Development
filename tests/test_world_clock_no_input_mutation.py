"""Input-immutability net for the per-review world-clock helpers.

The `ensure_*_state_pure` helpers on the review hot path used to open with
`copy.deepcopy(dict(player_data))`, which duplicated the whole save (about
13,600 nodes, 2.07 ms) to rebuild one sub-dict. They now take a shallow
`dict(player_data)` and rely on their `sanitize_*` counterpart to build the
keys they own from scratch.

That is only correct while none of these functions writes through a nested
value it did not rebuild, so the guarantee needs an explicit test rather than
inspection. Every case below asserts both halves of the contract: the input
mapping is untouched, and each owned key comes back as a distinct object so a
later write cannot reach the caller's state.

This test must pass against the deep-copying code as well; if it only passes
after the shallow-copy change, the assertions are wrong.
"""

import copy
import unittest

from constants import ITEM_DEFINITIONS, ORE_DATA
from storage_pure import default_player_data

from big_chinchompa_logic import (
    advance_big_chinchompa_world_clock_pure,
    big_chinchompa_view_pure,
    ensure_big_chinchompa_state_pure,
)
from evil_tree_logic import (
    advance_evil_tree_world_clock_pure,
    ensure_evil_tree_state_pure,
    evil_tree_spawn_due_pure,
    evil_tree_view_pure,
)
from fist_of_guthix_logic import (
    ensure_fist_of_guthix_state_pure,
    fist_of_guthix_view_pure,
)
from grand_exchange_logic import ensure_ge_state_pure
from managing_miscellania_logic import (
    advance_managing_miscellania_world_clock_pure,
)
from shooting_star_logic import (
    advance_shooting_star_world_clock_pure,
    ensure_shooting_star_state_pure,
    shooting_star_view_pure,
)
from shop_logic import advance_shop_market_clock_pure, ensure_shop_state_pure
from summoning_logic import advance_summoning_world_tick_pure
from wicked_hood_logic import (
    advance_wicked_hood_review_day_pure,
    ensure_wicked_hood_state_pure,
)


def _fresh_player() -> dict:
    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


def _mature_player() -> dict:
    """A save carrying the growth-bearing state a real profile accumulates."""
    data = _fresh_player()
    data["shop_market_clock"] = {
        **(data.get("shop_market_clock") or {}),
        "answered_cards": 12_480,
        "market_tick": 12_480,
    }
    data["inventory"] = {"Logs": 4213, "Coins": 1_284_006, "Bones": 77}
    data["toolbelt"] = {
        "woodcutting": ["dragon_hatchet"],
        "mining": ["dragon_pickaxe"],
    }
    for level_key in (
        "woodcutting_level",
        "mining_level",
        "farming_level",
        "firemaking_level",
        "hunter_level",
        "summoning_level",
        "defense_level",
    ):
        if level_key in data:
            data[level_key] = 90
    return data


# (label, call, owned_keys) — owned_keys are the save keys the function is
# entitled to rewrite, and must therefore come back as new objects.
_CASES = (
    (
        "ensure_evil_tree_state_pure",
        lambda d: ensure_evil_tree_state_pure(d),
        ("evil_tree",),
    ),
    (
        "ensure_big_chinchompa_state_pure",
        lambda d: ensure_big_chinchompa_state_pure(d),
        ("big_chinchompa", "world_population_profile"),
    ),
    (
        "ensure_shooting_star_state_pure",
        lambda d: ensure_shooting_star_state_pure(d),
        ("shooting_star", "world_population_profile"),
    ),
    (
        "ensure_fist_of_guthix_state_pure",
        lambda d: ensure_fist_of_guthix_state_pure(d),
        ("fist_of_guthix",),
    ),
    (
        "ensure_shop_state_pure",
        lambda d: ensure_shop_state_pure(d),
        ("shop_market_clock", "shop_stock_state", "shop_events"),
    ),
    (
        "ensure_wicked_hood_state_pure",
        lambda d: ensure_wicked_hood_state_pure(d),
        ("wicked_hood",),
    ),
    (
        "ensure_ge_state_pure",
        lambda d: ensure_ge_state_pure(d),
        ("ge_market_state", "ge_player_orders", "inventory"),
    ),
    (
        "evil_tree_view_pure",
        lambda d: evil_tree_view_pure(d, has_usable_hatchet=True),
        (),
    ),
    ("big_chinchompa_view_pure", lambda d: big_chinchompa_view_pure(d), ()),
    (
        "shooting_star_view_pure",
        lambda d: shooting_star_view_pure(d, has_usable_pickaxe=True),
        (),
    ),
    ("fist_of_guthix_view_pure", lambda d: fist_of_guthix_view_pure(d), ()),
    ("evil_tree_spawn_due_pure", lambda d: evil_tree_spawn_due_pure(d), ()),
    (
        "advance_evil_tree_world_clock_pure",
        lambda d: advance_evil_tree_world_clock_pure(d),
        ("evil_tree",),
    ),
    (
        "advance_big_chinchompa_world_clock_pure",
        lambda d: advance_big_chinchompa_world_clock_pure(d),
        ("big_chinchompa",),
    ),
    (
        "advance_shooting_star_world_clock_pure",
        lambda d: advance_shooting_star_world_clock_pure(d),
        ("shooting_star",),
    ),
    (
        "advance_shop_market_clock_pure",
        lambda d: advance_shop_market_clock_pure(d),
        ("shop_market_clock",),
    ),
    (
        "advance_wicked_hood_review_day_pure",
        lambda d: advance_wicked_hood_review_day_pure(d),
        ("wicked_hood",),
    ),
    (
        "advance_managing_miscellania_world_clock_pure",
        lambda d: advance_managing_miscellania_world_clock_pure(d),
        ("managing_miscellania",),
    ),
    (
        "advance_summoning_world_tick_pure",
        lambda d: advance_summoning_world_tick_pure(
            d,
            successful_answer=True,
            active_carried_target=None,
        ),
        (),
    ),
)


def _result_mapping(returned):
    """Normalize the (data, events) tuple these helpers variously return."""
    if isinstance(returned, tuple):
        returned = returned[0]
    return returned if isinstance(returned, dict) else None


class TestWorldClockDoesNotMutateInput(unittest.TestCase):
    def test_input_save_is_never_mutated(self):
        for label, call, _owned in _CASES:
            for fixture_name, fixture in (
                ("fresh", _fresh_player),
                ("mature", _mature_player),
            ):
                with self.subTest(function=label, save=fixture_name):
                    player = fixture()
                    baseline = copy.deepcopy(player)
                    call(player)
                    self.assertEqual(
                        player,
                        baseline,
                        f"{label} mutated the save it was given",
                    )

    def test_owned_keys_come_back_as_new_objects(self):
        for label, call, owned in _CASES:
            if not owned:
                continue
            for fixture_name, fixture in (
                ("fresh", _fresh_player),
                ("mature", _mature_player),
            ):
                with self.subTest(function=label, save=fixture_name):
                    player = fixture()
                    result = _result_mapping(call(player))
                    self.assertIsNotNone(
                        result, f"{label} returned no save mapping"
                    )
                    for key in owned:
                        if key not in player or not isinstance(
                            player[key], (dict, list)
                        ):
                            continue
                        self.assertIsNot(
                            result[key],
                            player[key],
                            f"{label} returned the caller's own {key!r} object, "
                            "so a later write would reach the live save",
                        )

    def test_writing_through_the_result_cannot_reach_the_input(self):
        """The failure mode shallow copying could introduce, stated directly."""
        for label, call, owned in _CASES:
            if not owned:
                continue
            for key in owned:
                with self.subTest(function=label, key=key):
                    player = _mature_player()
                    if not isinstance(player.get(key), dict):
                        continue
                    baseline = copy.deepcopy(player[key])
                    result = _result_mapping(call(player))
                    if result is None or not isinstance(result.get(key), dict):
                        continue
                    result[key]["_aliasing_probe"] = "written"
                    self.assertEqual(
                        player[key],
                        baseline,
                        f"{label} left {key!r} aliased to the caller's save",
                    )


if __name__ == "__main__":
    unittest.main()
