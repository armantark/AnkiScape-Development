"""Player poison timing from the selected non-beta period revisions.

Antipoison 5606640:22 (2012-05-13) supports 150 ticks, with the unresolved
Herblore 6569702:71 (2012-11-17) conflict of 300 ticks. Super antipoison
5819437:22 (2012-06-24) supports 600 ticks. Both remain provisional pending
independent period corroboration. Poison (historical) 5979526:6,8,10
(2012-07-23) supplies 30-tick hits and two-life-point decay. The owner's
2026-10-21 decisions exclude the terminal 10-point hit and preserve saved
countdowns and sources while applying the corrected damage immediately.
"""

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)

import json
import unittest

from ankiscape.data.pyramid_plunder_data import PYRAMID_PLUNDER_ACTIVITY_ID
from ankiscape.logic.pyramid_plunder_logic import (
    apply_pyramid_plunder_review_pure,
    enter_pyramid_plunder_pure,
    pyramid_plunder_view_pure,
)
from ankiscape.logic_pure.logic_pure_combat_model import sanitize_combat_state_pure
from ankiscape.logic_pure.logic_pure_combat_supplies import (
    _combat_advance_status_effects,
    _combat_consume_antipoison_if_needed,
    apply_combat_poison_effect_pure,
    combat_poison_damage_for_ticks_pure,
    combat_poison_ticks_for_initial_damage_pure,
    combat_status_summary_pure,
)
from tests.test_combat_logic import _player


class PoisonPeriodTimingTest(unittest.TestCase):
    def test_each_dose_cures_and_grants_selected_duration(self):
        cases = (
            ("Antipoison (4)", 150, "Antipoison (3)"),
            ("Antipoison (3)", 150, "Antipoison (2)"),
            ("Antipoison (2)", 150, "Antipoison (1)"),
            ("Antipoison (1)", 150, "Vial"),
            ("Super antipoison (4)", 600, "Super antipoison (3)"),
            ("Super antipoison (3)", 600, "Super antipoison (2)"),
            ("Super antipoison (2)", 600, "Super antipoison (1)"),
            ("Super antipoison (1)", 600, "Vial"),
        )
        for item, duration, replacement in cases:
            with self.subTest(item=item):
                player = _player(
                    combat_supply_loadout={"potions": {item: 1}},
                    combat_status_effects={"poison": {"ticks_left": 10, "tick_progress": 29}},
                )
                event = _combat_consume_antipoison_if_needed(player)
                self.assertEqual(event, {
                    "item": item, "replacement": replacement,
                    "effect": "poison_cure", "immunity_ticks": duration,
                })
                self.assertNotIn("poison", player["combat_status_effects"])
                self.assertEqual(player["combat_status_effects"]["poison_immunity"]["ticks_left"], duration)
                self.assertEqual(combat_status_summary_pure(player), f"Poison immune: {duration} ticks")
                self.assertEqual(player["combat_supply_loadout"]["potions"],
                                 {} if replacement == "Vial" else {replacement: 1})
                self.assertEqual(player["inventory"], {"Vial": 1} if replacement == "Vial" else {})
                # No second dose is consumed after curing the poison.
                snapshot = json.loads(json.dumps(player))
                self.assertIsNone(_combat_consume_antipoison_if_needed(player))
                self.assertEqual(player, snapshot)

    def test_immunity_expires_at_selected_tick(self):
        for item, duration, penultimate in (
            ("Antipoison (4)", 150, 149),
            ("Super antipoison (4)", 600, 599),
        ):
            with self.subTest(item=item):
                player = _player(
                    combat_supply_loadout={"potions": {item: 1}},
                    combat_status_effects={"poison": {"ticks_left": 10}},
                )
                self.assertEqual(_combat_consume_antipoison_if_needed(player)["immunity_ticks"], duration)
                player["combat_supply_loadout"]["potions"] = {}
                result = _combat_advance_status_effects(player, penultimate)
                self.assertEqual(result["expired"], ())
                self.assertEqual(player["combat_status_effects"]["poison_immunity"]["ticks_left"], 1)
                self.assertEqual(combat_status_summary_pure(player), "Poison immune: 1 ticks")
                protected = json.loads(json.dumps(player))
                blocked, applied, reason = apply_combat_poison_effect_pure(player, 3)
                self.assertFalse(applied)
                self.assertEqual(reason, "poison immune")
                self.assertNotIn("poison", blocked["combat_status_effects"])
                self.assertEqual(blocked["inventory"], {})
                self.assertEqual(blocked["combat_supply_loadout"]["potions"], {})
                self.assertEqual(player, protected)
                result = _combat_advance_status_effects(player, 1)
                self.assertEqual(result["expired"], ("poison_immunity",))
                self.assertNotIn("poison_immunity", player["combat_status_effects"])
                self.assertEqual(combat_status_summary_pure(player), "")
                poisoned, applied, reason = apply_combat_poison_effect_pure(player, 3)
                self.assertTrue(applied, reason)
                self.assertEqual(poisoned["combat_status_effects"]["poison"]["ticks_left"], 10)

    def test_poison_first_hit_decay_and_terminal_boundary(self):
        player, applied, reason = apply_combat_poison_effect_pure(
            _player(constitution_level=99, combat_lifepoints=990), 3,
        )
        self.assertTrue(applied, reason)
        self.assertEqual(player["combat_status_effects"]["poison"]["ticks_left"], 10)
        self.assertEqual(combat_status_summary_pure(player), "Poisoned: 30 LP in 30 ticks")
        result = _combat_advance_status_effects(player, 29)
        self.assertEqual(result["damage"], {})
        self.assertEqual(player["combat_lifepoints"], 990)
        self.assertEqual(combat_status_summary_pure(player), "Poisoned: 30 LP in 1 ticks")
        result = _combat_advance_status_effects(player, 1)
        self.assertEqual(result["damage"], {"poison": 30})
        self.assertEqual(result["expired"], ())
        self.assertEqual(combat_status_summary_pure(player), "Poisoned: 28 LP in 30 ticks")
        for damage, summary in (
            (28, "Poisoned: 26 LP in 30 ticks"),
            (26, "Poisoned: 24 LP in 30 ticks"),
            (24, "Poisoned: 22 LP in 30 ticks"),
            (22, "Poisoned: 20 LP in 30 ticks"),
            (20, "Poisoned: 18 LP in 30 ticks"),
            (18, "Poisoned: 16 LP in 30 ticks"),
            (16, "Poisoned: 14 LP in 30 ticks"),
            (14, "Poisoned: 12 LP in 30 ticks"),
            (12, ""),
        ):
            with self.subTest(damage=damage):
                result = _combat_advance_status_effects(player, 30)
                self.assertEqual(result["damage"], {"poison": damage})
                self.assertEqual(combat_status_summary_pure(player), summary)
                self.assertEqual(result["expired"], ("poison",) if damage == 12 else ())
        self.assertNotIn("poison", player["combat_status_effects"])
        self.assertEqual(player["combat_lifepoints"], 780)
        result = _combat_advance_status_effects(player, 30)
        self.assertEqual(result["damage"], {})
        self.assertEqual(result["expired"], ())
        self.assertEqual(player["combat_lifepoints"], 780)

    def test_cave_crawler_curve_and_batched_advancement(self):
        player, applied, reason = apply_combat_poison_effect_pure(_player(), 8)
        self.assertTrue(applied, reason)
        self.assertEqual(player["combat_status_effects"]["poison"]["ticks_left"], 35)
        self.assertEqual(combat_poison_ticks_for_initial_damage_pure(8), 35)
        expected = (
            80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50,
            48, 46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18,
            16, 14, 12,
        )
        sequential = json.loads(json.dumps(player))
        batched = json.loads(json.dumps(player))
        # Explicit max LP keeps the entire 1,610-LP curve above the death boundary.
        sequential["combat_lifepoints"] = batched["combat_lifepoints"] = 5000
        damage = []
        for expected_hit in expected:
            result = _combat_advance_status_effects(sequential, 30, max_lifepoints=5000)
            damage.append(result["damage"]["poison"])
            self.assertEqual(result["damage"], {"poison": expected_hit})
            self.assertEqual(result["expired"], ("poison",) if expected_hit == 12 else ())
        result = _combat_advance_status_effects(batched, 1050, max_lifepoints=5000)
        self.assertEqual(tuple(damage), expected)
        self.assertEqual(sum(damage), 1610)
        self.assertEqual(result["damage"], {"poison": 1610})
        self.assertEqual(result["expired"], ("poison",))
        self.assertEqual(sequential["combat_lifepoints"], 3390)
        self.assertEqual(sequential, batched)
        self.assertNotIn("poison", batched["combat_status_effects"])

    def test_invalid_and_terminal_only_inputs_do_not_apply_poison(self):
        for initial in (0, -1, "nonnumeric", 1):
            with self.subTest(initial=initial):
                self.assertEqual(combat_poison_ticks_for_initial_damage_pure(initial), 0)
                player, applied, reason = apply_combat_poison_effect_pure(_player(), initial)
                self.assertFalse(applied)
                self.assertEqual(reason, "invalid poison damage")
                self.assertNotIn("poison", player["combat_status_effects"])
        for remaining in (0, -1, "nonnumeric", None):
            with self.subTest(remaining=remaining):
                self.assertEqual(combat_poison_damage_for_ticks_pure(remaining), 0)
        self.assertEqual(combat_poison_ticks_for_initial_damage_pure(2), 5)
        player, applied, reason = apply_combat_poison_effect_pure(_player(), 2)
        self.assertTrue(applied, reason)
        self.assertEqual(player["combat_status_effects"]["poison"]["ticks_left"], 5)
        self.assertEqual(combat_status_summary_pure(player), "Poisoned: 20 LP in 30 ticks")

    def test_saved_poison_keeps_countdowns_and_uses_new_damage(self):
        legacy_source = "/legacy/poison/Poison.kt"
        saved = _player(combat_status_effects={"poison": {
            "ticks_left": 11, "tick_progress": 29, "source": legacy_source,
        }})
        loaded = json.loads(json.dumps(saved))
        original = json.loads(json.dumps(loaded))
        sanitized = sanitize_combat_state_pure(loaded)
        self.assertEqual(loaded, original)
        self.assertEqual(sanitized["combat_status_effects"], original["combat_status_effects"])
        loaded.update(sanitized)
        self.assertEqual(combat_status_summary_pure(loaded), "Poisoned: 32 LP in 1 ticks")
        result = _combat_advance_status_effects(loaded, 1)
        self.assertEqual(result["damage"], {"poison": 32})
        self.assertEqual(loaded["combat_lifepoints"], 68)
        self.assertEqual(loaded["combat_status_effects"]["poison"], {
            "ticks_left": 10, "tick_progress": 0, "source": legacy_source,
        })
        self.assertEqual(combat_status_summary_pure(loaded), "Poisoned: 30 LP in 30 ticks")
        saved["combat_status_effects"]["poison"] = {
            "ticks_left": 36, "tick_progress": 0, "source": legacy_source,
        }
        loaded = json.loads(json.dumps(saved))
        loaded.update(sanitize_combat_state_pure(loaded))
        self.assertEqual(loaded["combat_status_effects"], saved["combat_status_effects"])
        self.assertEqual(combat_status_summary_pure(loaded), "Poisoned: 82 LP in 30 ticks")
        # Stronger saved poison is preserved, and applying new poison is pure too.
        for input_player, expected_applied in ((loaded, False), (_player(), True)):
            original = json.loads(json.dumps(input_player))
            _updated, applied, _reason = apply_combat_poison_effect_pure(input_player, 3)
            self.assertEqual(applied, expected_applied)
            self.assertEqual(input_player, original)
        missing_source = _player(combat_status_effects={"poison": {"ticks_left": 11}})
        sanitized = sanitize_combat_state_pure(missing_source)
        self.assertEqual(sanitized["combat_status_effects"]["poison"]["source"],
                         "https://runescape.wiki/w/index.php?title=Poison_(historical)&oldid=5979526")

    def test_saved_immunity_keeps_remaining_duration(self):
        for duration, after_review in ((1500, 1450), (6000, 5950)):
            with self.subTest(duration=duration):
                saved = _player(
                    combat_supply_loadout={"potions": {"Antipoison (1)": 1}},
                    combat_status_effects={"poison_immunity": {
                        "ticks_left": duration, "source": "/legacy/PotionType.kt",
                    }},
                )
                loaded = json.loads(json.dumps(saved))
                loaded.update(sanitize_combat_state_pure(loaded))
                self.assertEqual(loaded["combat_status_effects"], saved["combat_status_effects"])
                result = _combat_advance_status_effects(loaded, 50)
                self.assertEqual(result["expired"], ())
                self.assertEqual(loaded["combat_status_effects"]["poison_immunity"], {
                    "ticks_left": after_review, "source": "/legacy/PotionType.kt",
                })
                protected, applied, reason = apply_combat_poison_effect_pure(loaded, 3)
                self.assertFalse(applied)
                self.assertEqual(reason, "poison immune")
                self.assertIsNone(_combat_consume_antipoison_if_needed(protected))
                self.assertEqual(protected["combat_supply_loadout"]["potions"], {"Antipoison (1)": 1})
                self.assertEqual(protected["inventory"], {})
                self.assertEqual(protected["combat_status_effects"], loaded["combat_status_effects"])

    def test_pyramid_consumes_both_families_from_shared_data(self):
        for item, duration, replacement in (
            ("Antipoison (4)", 150, "Antipoison (3)"),
            ("Super antipoison (4)", 600, "Super antipoison (3)"),
        ):
            with self.subTest(item=item):
                player = _player(
                    thieving_level=91, constitution_level=99, combat_lifepoints=990,
                    quests={"icthlarins_little_helper": {"started": True}},
                    pyramid_plunder_priority="balanced", inventory={item: 1},
                )
                entered, ok, info = enter_pyramid_plunder_pure(player)
                self.assertTrue(ok, info)
                self.assertEqual(info["pack"], {item: 1})
                updated, result = apply_pyramid_plunder_review_pure(entered, lambda: 0.0)
                self.assertEqual(result["xp"]["thieving"], 50.0)
                self.assertEqual(result["hazards"][0]["source"], "pyramid_plunder_scarab")
                self.assertEqual(result["hazards"][0]["poison"], 38)
                self.assertEqual(result["hazards"][0]["antipoison"], item)
                self.assertNotIn("poison", updated["combat_status_effects"])
                self.assertEqual(updated["combat_status_effects"]["poison_immunity"]["ticks_left"], duration)
                self.assertEqual(pyramid_plunder_view_pure(updated)["poison_immunity_ticks"], duration)
                self.assertEqual(updated["inventory"][item], 0)
                self.assertEqual(updated["inventory"][replacement], 1)
                self.assertEqual(updated["carried_inventory"][PYRAMID_PLUNDER_ACTIVITY_ID], {replacement: 1})
        player["inventory"] = {"Antipoison (4)": 1, "Super antipoison (4)": 1}
        entered, ok, info = enter_pyramid_plunder_pure(player)
        self.assertTrue(ok, info)
        self.assertEqual(info["pack"], {"Super antipoison (4)": 1})
        updated, result = apply_pyramid_plunder_review_pure(entered, lambda: 0.0)
        self.assertEqual(result["hazards"][0]["antipoison"], "Super antipoison (4)")
        self.assertEqual(updated["inventory"]["Antipoison (4)"], 1)
        self.assertEqual(updated["combat_status_effects"]["poison_immunity"]["ticks_left"], 600)
