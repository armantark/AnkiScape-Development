import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic_pure.logic_pure import advance_temporary_effects_pure
from ankiscape.data.shooting_star_data import (
    SHOOTING_STAR_LEGACY_LOCATION_ALIASES,
    SHOOTING_STAR_LOCATIONS,
    SHOOTING_STAR_ORE_BONUS_TICKS,
    SHOOTING_STAR_STARDUST_CAP,
)
from ankiscape.logic.shooting_star_logic import (
    advance_shooting_star_world_clock_pure,
    apply_shooting_star_join_pure,
    apply_shooting_star_notice_action_pure,
    apply_shooting_star_exchange_pure,
    apply_shooting_star_review_pure,
    default_shooting_star_state_pure,
    ensure_shooting_star_state_pure,
    shooting_star_notice_view_pure,
    shooting_star_view_pure,
)


def _player(*, answered=20, mining_level=99):
    return {
        "shop_market_clock": {
            "version": 1,
            "answered_cards": answered,
            "market_tick": answered,
        },
        "mining_level": mining_level,
        "mining_exp": 0.0,
        "inventory": {},
        "shooting_star": default_shooting_star_state_pure(),
    }


class TestShootingStarLogic(unittest.TestCase):
    def test_cutoff_crash_site_catalog_is_complete_and_legacy_names_repair(self):
        self.assertEqual(
            SHOOTING_STAR_LOCATIONS,
            (
                "Crafting Guild mining site",
                "Falador east bank",
                "Rimmington mining site",
                "Falador mining site",
                "Karamja north-western mining site",
                "Brimhaven mining site",
                "South Crandor mining site",
                "Karamja mining site",
                "Shilo Village mining site",
                "Keldagrim entrance mining site",
                "Jatizso mine",
                "Lunar Isle mine",
                "Managing Miscellania mining site",
                "Central Fremennik Isles mining site",
                "Rellekka mining site",
                "Legends' Guild mining site",
                "South-east Ardougne mining site",
                "Coal Trucks",
                "Yanille Bank",
                "Fight Arena mining site",
                "Al Kharid bank",
                "Al Kharid mining site",
                "Duel Arena bank chest",
                "Uzer mining site",
                "Nardah mining site",
                "Nardah bank",
                "Western desert mining site",
                "South-east Varrock mining site",
                "Lumbridge Swamp training mining site",
                "South-west Varrock mining site",
                "Varrock east bank",
                "Burgh de Rott Bank",
                "Canifis Bank",
                "Gnome Stronghold Bank",
                "Lletya bank",
                "Piscatoris mining site",
                "Bandit camp mining site",
                "Mage Arena bank",
                "Pirates' Hideout mining site",
                "North Edgeville mining site",
                "Lava Maze runite mining site",
                "Southern wilderness mining site",
                "Wilderness Volcano",
            ),
        )

        player, _events = advance_shooting_star_world_clock_pure(_player())
        event = player["shooting_star"]["active_event"]
        for legacy, canonical in SHOOTING_STAR_LEGACY_LOCATION_ALIASES.items():
            player["shooting_star"]["active_event"] = {**event, "location": legacy}
            repaired = ensure_shooting_star_state_pure(player)
            self.assertEqual(
                repaired["shooting_star"]["active_event"]["location"],
                canonical,
            )

    def test_join_refuses_a_too_large_star_and_clears_selection(self):
        player, _ = advance_shooting_star_world_clock_pure(
            _player(mining_level=10)
        )
        player["shooting_star"]["active_event"].update(
            {"starting_size": 9, "current_size": 9, "layer_remaining": 15}
        )
        player["current_utility"] = "shooting_stars"

        stopped, ok, info = apply_shooting_star_join_pure(player)

        self.assertFalse(ok)
        self.assertTrue(info["unminable"])
        self.assertEqual(stopped["current_utility"], "bankstanding")
        self.assertEqual(
            shooting_star_notice_view_pure(stopped)["label"],
            "Star unminable at your level",
        )

    def test_review_clock_spawns_a_period_layer_and_reports_next_star(self):
        waiting = _player(answered=19)
        waiting["shooting_star"]["last_slot_tick"] = 0
        waiting, events = advance_shooting_star_world_clock_pure(waiting)
        self.assertEqual(events, ())
        self.assertEqual(shooting_star_view_pure(waiting, speed=100)["next_reviews"], 1)

        waiting["shop_market_clock"]["answered_cards"] = 20
        active, events = advance_shooting_star_world_clock_pure(waiting)
        self.assertEqual(events[0]["kind"], "spawned")
        view = shooting_star_view_pure(active)
        self.assertTrue(view["active"])
        self.assertIn(view["current_size"], range(1, 10))
        self.assertEqual(view["required_level"], view["current_size"] * 10)

    def test_legacy_preferences_do_not_control_the_next_star(self):
        player = _player(answered=20)
        player["shooting_star"].update(
            {"automation_mode": "advanced", "preferred_sizes": [2, 4]}
        )
        player, _ = advance_shooting_star_world_clock_pure(player)
        state = player["shooting_star"]
        self.assertNotIn("automation_mode", state)
        self.assertNotIn("preferred_sizes", state)
        self.assertNotIn(
            shooting_star_view_pure(player)["starting_size"],
            {2, 4},
        )

    def test_otherwise_identical_events_keep_seeded_population_fuzziness(self):
        base, _ = advance_shooting_star_world_clock_pure(_player(answered=20))
        removed = []
        for seed in (123, 456):
            player = {
                **base,
                "shop_market_clock": {
                    "answered_cards": 21,
                    "market_tick": 21,
                },
                "shooting_star": {
                    **base["shooting_star"],
                    "active_event": {
                        **base["shooting_star"]["active_event"],
                        "seed": seed,
                        "crowd_dust_removed": 0,
                    },
                },
            }
            advanced, _ = advance_shooting_star_world_clock_pure(player)
            removed.append(
                advanced["shooting_star"]["active_event"][
                    "crowd_dust_removed"
                ]
            )
        self.assertNotEqual(removed[0], removed[1])

    def test_tag_requires_no_pickaxe_but_only_the_first_attempt(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        event = player["shooting_star"]["active_event"]
        event["tag_candidate"] = True
        event["crowd_dust_removed"] = 0

        tagged, ok, result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=False,
        )
        self.assertTrue(ok)
        self.assertTrue(result["tag_only"])
        self.assertEqual(result["tag_xp"], 75 * 99)

        _same, ok, result = apply_shooting_star_review_pure(
            tagged,
            has_usable_pickaxe=False,
        )
        self.assertFalse(ok)
        self.assertIn("pickaxe", result["reason"])

    def test_inaccessible_layer_stops_instead_of_waiting(self):
        player, _ = advance_shooting_star_world_clock_pure(
            _player(mining_level=10)
        )
        event = player["shooting_star"]["active_event"]
        event["current_size"] = 9
        event["starting_size"] = 9
        event["layer_remaining"] = 15
        player["shooting_star"]["active_event"] = event

        stopped, ok, result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )
        self.assertTrue(ok)
        self.assertTrue(result["unminable"])
        self.assertEqual(result["required_level"], 90)
        self.assertEqual(stopped["inventory"].get("Stardust", 0), 0)
        self.assertEqual(stopped["current_utility"], "bankstanding")
        self.assertEqual(
            shooting_star_notice_view_pure(stopped)["kind"],
            "unminable",
        )

    def test_inaccessible_first_attempt_keeps_the_first_finder_tag(self):
        player, _ = advance_shooting_star_world_clock_pure(
            _player(mining_level=10)
        )
        event = player["shooting_star"]["active_event"]
        event.update(
            {
                "current_size": 9,
                "starting_size": 9,
                "layer_remaining": 15,
                "player_attempted": False,
                "tag_candidate": True,
                "crowd_dust_removed": 0,
            }
        )
        player["shooting_star"]["active_event"] = event

        stopped, ok, result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )

        self.assertTrue(ok)
        self.assertEqual(result["tag_xp"], 750.0)
        self.assertEqual(result["mining_xp"], 750.0)
        self.assertTrue(
            stopped["shooting_star"]["active_event"]["player_attempted"]
        )
        self.assertTrue(stopped["shooting_star"]["active_event"]["tag_awarded"])

    def test_watched_star_raises_ready_notice_without_rejoining(self):
        player, _ = advance_shooting_star_world_clock_pure(
            _player(mining_level=10)
        )
        event = player["shooting_star"]["active_event"]
        event.update({"current_size": 2, "starting_size": 2, "layer_remaining": 5})
        player["shooting_star"]["active_event"] = event
        player["current_utility"] = "shooting_stars"
        player["activity_session"] = {"active_id": "shooting_stars"}
        stopped, ok, _result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )
        self.assertTrue(ok)
        stopped["current_utility"] = "evil_tree"

        watched, ok, info = apply_shooting_star_notice_action_pure(
            stopped,
            "watch",
        )
        self.assertTrue(ok)
        self.assertTrue(info["watching"])
        self.assertFalse(shooting_star_notice_view_pure(watched)["visible"])

        watched["shooting_star"]["active_event"].update(
            {"current_size": 1, "layer_remaining": 10}
        )
        ready, _events = advance_shooting_star_world_clock_pure(watched)
        notice = shooting_star_notice_view_pure(ready)
        self.assertEqual(notice["kind"], "ready")
        self.assertEqual(notice["actions"], ({"id": "mine", "label": "Mine star"},))
        self.assertEqual(ready["current_utility"], "evil_tree")

        dismissed, ok, _info = apply_shooting_star_notice_action_pure(
            ready,
            "dismiss",
        )
        self.assertTrue(ok)
        self.assertFalse(shooting_star_notice_view_pure(dismissed)["visible"])
        self.assertEqual(dismissed["shooting_star"]["watched_event_id"], "")

    def test_watched_star_sprite_raises_the_same_manual_rejoin_action(self):
        player, _ = advance_shooting_star_world_clock_pure(
            _player(mining_level=10)
        )
        event = player["shooting_star"]["active_event"]
        event.update({"current_size": 2, "starting_size": 2, "layer_remaining": 5})
        player["shooting_star"]["active_event"] = event
        player["current_utility"] = "shooting_stars"
        stopped, ok, _result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )
        self.assertTrue(ok)
        watched, ok, _info = apply_shooting_star_notice_action_pure(
            stopped,
            "watch",
        )
        self.assertTrue(ok)
        watched["shooting_star"]["active_event"].update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_tick": 13_200,
            }
        )

        ready, _events = advance_shooting_star_world_clock_pure(watched)
        notice = shooting_star_notice_view_pure(ready)

        self.assertEqual(notice["label"], "Star sprite available")
        self.assertEqual(notice["actions"], ({"id": "mine", "label": "Mine star"},))

    def test_ready_notice_clears_when_the_watched_star_expires(self):
        player, _ = advance_shooting_star_world_clock_pure(
            _player(answered=20, mining_level=10)
        )
        event = player["shooting_star"]["active_event"]
        event.update({"current_size": 2, "starting_size": 2, "layer_remaining": 5})
        player["shooting_star"]["active_event"] = event
        player["current_utility"] = "shooting_stars"
        stopped, ok, _result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )
        self.assertTrue(ok)
        watched, ok, _info = apply_shooting_star_notice_action_pure(
            stopped,
            "watch",
        )
        self.assertTrue(ok)
        watched["shooting_star"]["active_event"].update(
            {"current_size": 1, "layer_remaining": 10}
        )
        ready, _events = advance_shooting_star_world_clock_pure(watched)
        self.assertTrue(shooting_star_notice_view_pure(ready)["visible"])

        ready["shop_market_clock"]["answered_cards"] = 40
        expired, _events = advance_shooting_star_world_clock_pure(ready)

        self.assertFalse(shooting_star_notice_view_pure(expired)["visible"])
        self.assertEqual(expired["shooting_star"]["watched_event_id"], "")

    def test_dust_cap_does_not_stop_layer_xp_or_depletion(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        player["inventory"]["Stardust"] = SHOOTING_STAR_STARDUST_CAP
        before = player["shooting_star"]["active_event"]["layer_remaining"]
        updated, ok, result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )
        self.assertTrue(ok)
        self.assertGreater(result["dust_xp"], 0)
        self.assertEqual(result["dust_added"], 0)
        self.assertEqual(
            updated["shooting_star"]["active_event"]["layer_remaining"],
            before - 1,
        )

    def test_final_dust_releases_sprite_and_manual_exchange_scales_rewards(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        event = player["shooting_star"]["active_event"]
        event.update(
            {
                "starting_size": 1,
                "current_size": 1,
                "layer_remaining": 1,
                "total_mass": 1_200,
                "crowd_dust_removed": 1_199,
                "player_dust_mined": 0,
            }
        )
        player["shooting_star"]["active_event"] = event
        player["inventory"]["Stardust"] = 99

        released, ok, result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )
        self.assertTrue(ok)
        self.assertTrue(result["sprite_released"])
        self.assertTrue(shooting_star_view_pure(released)["can_exchange"])

        exchanged, ok, reward = apply_shooting_star_exchange_pure(released)
        self.assertTrue(ok)
        self.assertEqual(reward["dust"], 100)
        self.assertEqual(reward["rewards"]["Cosmic rune"], 76)
        self.assertEqual(reward["rewards"]["Astral rune"], 26)
        self.assertEqual(reward["rewards"]["Gold ore"], 10)
        self.assertEqual(reward["rewards"]["Coins"], 25_001)
        self.assertEqual(exchanged["inventory"]["Stardust"], 0)
        self.assertEqual(
            exchanged["shooting_star"]["ore_bonus_ticks_remaining"],
            SHOOTING_STAR_ORE_BONUS_TICKS,
        )

    def test_sprite_expiry_preserves_dust_for_a_later_star(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        event = player["shooting_star"]["active_event"]
        event.update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_tick": 13_200,
            }
        )
        player["shooting_star"]["active_event"] = event
        player["inventory"]["Stardust"] = 50
        player["shop_market_clock"]["answered_cards"] = 22

        expired, events = advance_shooting_star_world_clock_pure(player)
        self.assertEqual(events[0]["reason"], "sprite_expired")
        self.assertEqual(expired["inventory"]["Stardust"], 50)
        self.assertEqual(expired["shooting_star"]["active_event"], {})

    def test_released_sprite_does_not_repeat_its_world_event(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        event = player["shooting_star"]["active_event"]
        event.update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_tick": 13_200,
            }
        )
        player["shooting_star"]["active_event"] = event
        player["shop_market_clock"]["answered_cards"] = 21

        still_released, events = advance_shooting_star_world_clock_pure(player)
        self.assertEqual(events, ())
        self.assertTrue(
            still_released["shooting_star"]["active_event"]["sprite_released"]
        )

    def test_corrupt_zero_size_event_is_repaired_before_mining(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        player["shooting_star"]["active_event"]["current_size"] = 0
        repaired = ensure_shooting_star_state_pure(player)
        self.assertEqual(
            repaired["shooting_star"]["active_event"]["current_size"],
            repaired["shooting_star"]["active_event"]["starting_size"],
        )

    def test_ore_bonus_uses_the_shared_review_tick_clock(self):
        player = _player()
        player["shooting_star"]["ore_bonus_ticks_remaining"] = 1_500

        advanced = advance_temporary_effects_pure(
            player,
            elapsed_ticks=50,
        )

        self.assertEqual(
            advanced["shooting_star"]["ore_bonus_ticks_remaining"],
            1_450,
        )
        self.assertEqual(
            player["shooting_star"]["ore_bonus_ticks_remaining"],
            1_500,
        )


if __name__ == "__main__":
    unittest.main()
