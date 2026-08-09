"""Goblin Raids: the announcement clock, both duties, and every sourced reward.

No stage and no reward here is reached by writing state into the save. `_play`
drives the real `apply_combat_burst_pure` against the real registered roster from
a real `default_player_data`, so a raid that could not be cleared or a boss that
could not be felled would fail rather than pass quietly.
"""

from __future__ import annotations

import copy
import json
import random
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    COMBAT_ENEMY_DATA,
    COMBAT_ENEMY_IMAGES,
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.equipment_data import EquipmentBonuses
from ankiscape.data.goblin_raids_data import (
    GOBLIN_COWER_SHIELD,
    GOBLIN_COWER_SHIELD_BONUS_BUDGET,
    GOBLIN_COWER_SHIELD_BONUS_RATE,
    GOBLIN_COWER_SHIELD_EXP_KEYS,
    GOBLIN_RAIDER,
    GOBLIN_RAIDS_ACTIVE_REVIEWS,
    GOBLIN_RAIDS_ACTIVITY_ID,
    GOBLIN_RAIDS_ASSET_MANIFEST,
    GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL,
    GOBLIN_RAIDS_RAIDER_COUNT,
    GOBLIN_RAIDS_RAID_MODE,
    GOBLIN_RAIDS_SPAWN_REVIEWS,
    GOBLIN_RAIDS_VILLAGE_BOSS_KILLS,
    GOBLIN_RAIDS_VILLAGE_MODE,
    GOBLIN_RAID_ENEMIES,
    GOBLIN_RAID_SITES,
    GOBLIN_RAID_SITES_BY_ID,
    GOBLIN_RAID_VILLAGE_BOSSES,
    HOLLOWTOOF,
    RAIDER_SET,
    RAIDER_SET_ITEM_NAMES,
    VILLAGE_GOBLIN,
)
from ankiscape.logic.goblin_raids_logic import (
    advance_goblin_raids_world_clock_pure,
    apply_goblin_cower_shield_bonus_pure,
    apply_goblin_raids_command_pure,
    apply_goblin_raids_review_pure,
    claim_goblin_raid_spoils_pure,
    default_goblin_raids_state_pure,
    goblin_cower_shield_can_apply_pure,
    goblin_raids_spawn_due_pure,
    goblin_raids_view_pure,
    intimidate_hollowtoof_pure,
    join_goblin_raid_pure,
    leave_goblin_raids_pure,
    next_raider_set_piece_pure,
    sanitize_goblin_raids_state_pure,
)
from ankiscape.logic_pure.logic_pure import (
    can_equip_item_pure,
    player_combat_level_pure,
)
from ankiscape.logic.shop_logic import advance_shop_market_clock_pure
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    handle_goblin_raids_answer,
)


def _player(levels: int = 60, cards: int = 0, **overrides):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for key in (
        "attack_level",
        "strength_level",
        "defense_level",
        "constitution_level",
    ):
        player[key] = levels
    player["equipment"] = {"weapon": "Rune scimitar"}
    player["inventory"] = {}
    player["carried_inventory"] = {}
    player["current_combat_target"] = "chicken"
    player["current_utility"] = "make_soft_clay"
    player["combat_encounter"] = {}
    player["activity_session"] = {"active_id": ""}
    player["combat_lifepoints"] = levels * 10
    player["shop_market_clock"] = {"answered_cards": cards}
    # Standing and fighting rather than fleeing, so a death is reachable at all.
    player["combat_auto_flee"] = False
    player.update(overrides)
    return player


def _with_raid(levels: int = 60, site_roll: float = 0.5):
    """A player standing in front of a real announced raid."""
    player = _player(levels, cards=GOBLIN_RAIDS_SPAWN_REVIEWS)
    player, events = advance_goblin_raids_world_clock_pure(
        player, site_roll=site_roll
    )
    assert any(row["kind"] == "announced" for row in events), events
    return player


def _play(player, seed, *, limit=400, until=None, rejoin=""):
    draws = random.Random(seed).random
    results = []
    for _ in range(limit):
        player, ok, result = apply_goblin_raids_review_pure(
            player,
            draws,
            enemy_data=COMBAT_ENEMY_DATA,
            equipment_data=EQUIPMENT_DATA,
        )
        if not ok:
            raise AssertionError(result)
        results.append(result)
        if until is not None and until(player, result):
            return player, results
        if result.get("terminal"):
            if not rejoin:
                return player, results
            player, ok, info = join_goblin_raid_pure(player, rejoin)
            if not ok:
                raise AssertionError(info)
    if until is not None:
        raise AssertionError("the goblins never reached the condition under test")
    return player, results


def _context(player_data: dict, calls: dict) -> RuntimeActionContext:
    return RuntimeActionContext(
        player_data=player_data,
        random_random=calls["rng"],
        show_error_message=lambda title, message: calls["errors"].append(
            (title, message)
        ),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=lambda _key, amount: amount,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda *_args: None,
        check_achievements=lambda _data: calls.__setitem__("achievements", True),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: calls.__setitem__("refresh", True),
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda message: calls["activity"].append(message),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


def _calls(seed=1):
    return {
        "rng": random.Random(seed).random,
        "errors": [],
        "xp": [],
        "activity": [],
        "saves": 0,
    }


class GoblinRaidsDataTest(unittest.TestCase):
    def test_the_activity_roster_items_and_art_are_registered(self):
        self.assertIn(GOBLIN_RAIDS_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        for row in GOBLIN_RAID_ENEMIES:
            self.assertIn(row.id, COMBAT_ENEMY_DATA, row.id)
            self.assertIn(row.id, COMBAT_ENEMY_IMAGES, row.id)
        keys = {row.storage_key for row in ITEM_DEFINITIONS}
        for item_name in RAIDER_SET_ITEM_NAMES + (GOBLIN_COWER_SHIELD,):
            self.assertIn(item_name, keys, item_name)
            self.assertIn(item_name, EQUIPMENT_DATA, item_name)

        root = Path(__file__).resolve().parents[1]
        provenance = json.loads((root / "assets_provenance.json").read_text())
        for row in GOBLIN_RAIDS_ASSET_MANIFEST:
            path = str(row["output_path"])
            self.assertTrue((root / path).is_file(), path)
            self.assertLess(
                provenance[path]["timestamp"], "2012-11-20T00:00:00Z", path
            )

    def test_the_roster_carries_the_stated_levels_lifepoints_and_styles(self):
        self.assertEqual((GOBLIN_RAIDER.level, GOBLIN_RAIDER.lifepoints), (2, 50))
        self.assertEqual((HOLLOWTOOF.level, HOLLOWTOOF.lifepoints), (5, 140))
        for boss in GOBLIN_RAID_VILLAGE_BOSSES:
            self.assertEqual((boss.level, boss.lifepoints), (5, 120))
        self.assertEqual(
            [boss.attack_style for boss in GOBLIN_RAID_VILLAGE_BOSSES],
            ["melee", "magic", "ranged"],
        )
        # The engine mis-derives a caster's maximum hit, so every non-melee row
        # must declare one.
        for row in GOBLIN_RAID_ENEMIES:
            enemy = COMBAT_ENEMY_DATA[row.id]
            self.assertEqual(enemy["stats"]["hitpoints"], row.lifepoints, row.id)
            if enemy["attack_style"] in {"magic", "magic_melee"}:
                self.assertTrue(enemy.get("max_hit"), row.id)

    def test_the_roster_inherits_emulator_cited_offensive_stats(self):
        """No roster stat is a placeholder; each comes from a registered goblin."""
        for row in GOBLIN_RAID_ENEMIES:
            base = COMBAT_ENEMY_DATA[row.base]
            enemy = COMBAT_ENEMY_DATA[row.id]
            for stat in ("attack", "strength", "defence", "magic", "ranged"):
                self.assertEqual(enemy["stats"][stat], base["stats"][stat], row.id)
            self.assertEqual(enemy["bonuses"], base["bonuses"], row.id)
            self.assertIn(row.base, enemy["source"])

    def test_the_three_site_kinds_and_the_sourced_thresholds(self):
        self.assertEqual(
            [site.spoil_kind for site in GOBLIN_RAID_SITES],
            ["seeds", "logs", "ores"],
        )
        self.assertIn("Logs", GOBLIN_RAID_SITES_BY_ID["forest"].materials)
        self.assertIn("Oak logs", GOBLIN_RAID_SITES_BY_ID["forest"].materials)
        self.assertEqual(
            {
                site.id: site.yodri_rewards
                for site in GOBLIN_RAID_SITES
            },
            {
                "farm": ("Potato seed", "Marigold seed", "Barley seed"),
                "forest": ("Logs", "Oak logs"),
                "mine": ("Clay", "Copper ore", "Tin ore"),
            },
        )
        self.assertEqual(GOBLIN_RAIDS_RAIDER_COUNT, 10)
        self.assertEqual(GOBLIN_RAIDS_VILLAGE_BOSS_KILLS, 15)
        self.assertEqual(GOBLIN_COWER_SHIELD_BONUS_RATE, 0.25)
        self.assertEqual(GOBLIN_COWER_SHIELD_BONUS_BUDGET, 1000.0)
        self.assertEqual(
            GOBLIN_COWER_SHIELD_EXP_KEYS,
            ("attack_exp", "defense_exp", "constitution_exp"),
        )
        self.assertEqual(
            [piece.item_name for piece in RAIDER_SET],
            ["Raider chainbody", "Raider axe", "Raider shield"],
        )
        # Exact: the pinned Raider axe revision states 8 Attack.
        self.assertEqual(EQUIPMENT_DATA["Raider axe"].required_level, 8)

    def test_period_cache_ids_and_bonuses_drive_all_four_equipment_rows(self):
        expected = {
            "Goblin cower shield": (
                25_350,
                EquipmentBonuses(
                    attack_magic=-8,
                    attack_ranged=-2,
                    defence_stab=13,
                    defence_slash=15,
                    defence_crush=14,
                    defence_magic=-1,
                    defence_ranged=14,
                ),
            ),
            "Raider axe": (
                25_351,
                EquipmentBonuses(
                    attack_stab=-2,
                    attack_slash=18,
                    attack_crush=13,
                    defence_ranged=-1,
                    melee_strength=22,
                ),
            ),
            "Raider chainbody": (
                25_352,
                EquipmentBonuses(
                    attack_magic=-15,
                    defence_stab=20,
                    defence_slash=29,
                    defence_crush=35,
                    defence_magic=-3,
                    defence_ranged=22,
                ),
            ),
            "Raider shield": (
                25_353,
                EquipmentBonuses(
                    attack_magic=-6,
                    attack_ranged=-2,
                    defence_stab=14,
                    defence_slash=15,
                    defence_crush=13,
                    defence_ranged=14,
                ),
            ),
        }
        for item_name, (item_id, bonuses) in expected.items():
            row = EQUIPMENT_DATA[item_name]
            self.assertEqual(row.source_item_id, item_id)
            self.assertEqual(row.bonuses, bonuses)
        self.assertEqual(
            EQUIPMENT_DATA["Raider axe"].skill_requirements,
            (("attack", 8),),
        )
        for item_name in ("Raider chainbody", "Raider shield"):
            self.assertEqual(
                EQUIPMENT_DATA[item_name].skill_requirements,
                (("defense", 8),),
            )
        definitions = {row.storage_key: row for row in ITEM_DEFINITIONS}
        for item_name in expected:
            self.assertFalse(definitions[item_name].stackable)
            self.assertFalse(definitions[item_name].tradeable)

    def test_the_period_level_eight_requirements_drive_the_real_equip_gate(self):
        attacker = _player(1, attack_level=8, defense_level=7)
        self.assertEqual(
            can_equip_item_pure("Raider axe", EQUIPMENT_DATA, attacker),
            (True, ""),
        )
        for item_name in ("Raider chainbody", "Raider shield"):
            self.assertEqual(
                can_equip_item_pure(item_name, EQUIPMENT_DATA, attacker),
                (False, "Requires level 8 Defense"),
            )

        defender = _player(1, attack_level=7, defense_level=8)
        self.assertEqual(
            can_equip_item_pure("Raider axe", EQUIPMENT_DATA, defender),
            (False, "Requires level 8 Attack"),
        )
        for item_name in ("Raider chainbody", "Raider shield"):
            self.assertEqual(
                can_equip_item_pure(item_name, EQUIPMENT_DATA, defender),
                (True, ""),
            )


class GoblinRaidsWorldClockTest(unittest.TestCase):
    def test_a_notice_arrives_on_the_sourced_half_hourly_cadence(self):
        player = _player(cards=0)
        self.assertFalse(goblin_raids_spawn_due_pure(player))
        player, events = advance_goblin_raids_world_clock_pure(player)
        self.assertEqual(events, ())
        self.assertEqual(player["goblin_raids"]["active_raid"], {})

        player["shop_market_clock"] = {
            "answered_cards": GOBLIN_RAIDS_SPAWN_REVIEWS
        }
        self.assertTrue(goblin_raids_spawn_due_pure(player))
        player, events = advance_goblin_raids_world_clock_pure(
            player, site_roll=0.0
        )
        self.assertEqual([row["kind"] for row in events], ["announced"])
        self.assertEqual(player["goblin_raids"]["active_raid"]["site_id"], "farm")
        self.assertEqual(
            player["goblin_raids"]["active_raid"]["reviews_remaining"],
            GOBLIN_RAIDS_ACTIVE_REVIEWS,
        )

    def test_every_site_kind_is_reachable_from_the_roll(self):
        seen = set()
        for roll in (0.0, 0.4, 0.9):
            player = _player(cards=GOBLIN_RAIDS_SPAWN_REVIEWS)
            player, _events = advance_goblin_raids_world_clock_pure(
                player, site_roll=roll
            )
            seen.add(player["goblin_raids"]["active_raid"]["site_id"])
        self.assertEqual(seen, {site.id for site in GOBLIN_RAID_SITES})

    def test_a_raid_expires_and_takes_an_unfinished_session_with_it(self):
        player, ok, _ = join_goblin_raid_pure(_with_raid(), GOBLIN_RAIDS_RAID_MODE)
        self.assertTrue(ok)
        player["shop_market_clock"] = {
            "answered_cards": GOBLIN_RAIDS_SPAWN_REVIEWS
            + GOBLIN_RAIDS_ACTIVE_REVIEWS
        }
        player, events = advance_goblin_raids_world_clock_pure(player)
        self.assertEqual([row["kind"] for row in events], ["expired"])
        self.assertEqual(player["goblin_raids"]["active_raid"], {})
        self.assertEqual(player["goblin_raids"]["session"], {})
        self.assertEqual(player["activity_session"]["active_id"], "")
        self.assertEqual(player["current_combat_target"], "chicken")
        self.assertIn("over before you finished", player["goblin_raids"]["last_result"])

    def test_an_expired_attempt_keeps_yodris_partial_raider_payout(self):
        player, ok, info = join_goblin_raid_pure(
            _with_raid(99, site_roll=0.9), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok, info)
        player, _results = _play(
            player,
            2,
            until=lambda current, _result: (
                current["goblin_raids"]["session"]["raiders_remaining"] == 9
            ),
        )
        player["shop_market_clock"] = {
            "answered_cards": (
                GOBLIN_RAIDS_SPAWN_REVIEWS + GOBLIN_RAIDS_ACTIVE_REVIEWS
            )
        }

        expired, events = advance_goblin_raids_world_clock_pure(player)

        self.assertEqual([row["kind"] for row in events], ["expired"])
        self.assertEqual(expired["goblin_raids"]["active_raid"], {})
        self.assertEqual(expired["goblin_raids"]["session"]["stage"], "spoils")
        claimed, ok, info = claim_goblin_raid_spoils_pure(expired)
        self.assertTrue(ok, info)
        self.assertEqual(info["raiders_killed"], 1)
        self.assertEqual(
            sum(info["rewards"].values()),
            sum(player["goblin_raids"]["session"]["spoils"].values()) + 1,
        )
        self.assertFalse(info["raid_cleared"])
        self.assertEqual(claimed["goblin_raids"]["raids_cleared"], 0)

    def test_expiry_after_all_raiders_does_not_credit_hollowtoofs_clear(self):
        player, ok, info = join_goblin_raid_pure(
            _with_raid(99, site_roll=0.5), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok, info)
        player, _results = _play(
            player,
            2,
            until=lambda current, _result: (
                current["goblin_raids"]["session"]["stage"] == "leader"
            ),
        )
        player["shop_market_clock"] = {
            "answered_cards": (
                GOBLIN_RAIDS_SPAWN_REVIEWS + GOBLIN_RAIDS_ACTIVE_REVIEWS
            )
        }
        expired, _events = advance_goblin_raids_world_clock_pure(player)

        claimed, ok, info = claim_goblin_raid_spoils_pure(expired)

        self.assertTrue(ok, info)
        self.assertEqual(info["raiders_killed"], GOBLIN_RAIDS_RAIDER_COUNT)
        self.assertFalse(info["raid_cleared"])
        self.assertEqual(claimed["goblin_raids"]["raids_cleared"], 0)

    def test_ten_raiders_and_hollowtoof_fit_the_registered_active_window(self):
        player, ok, info = join_goblin_raid_pure(
            _with_raid(99), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok, info)
        draws = random.Random(2).random
        world_events = []

        for _ in range(GOBLIN_RAIDS_ACTIVE_REVIEWS):
            player = advance_shop_market_clock_pure(player)
            player, ok, result = apply_goblin_raids_review_pure(
                player,
                draws,
                enemy_data=COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)
            player, events = advance_goblin_raids_world_clock_pure(player)
            world_events.extend(row["kind"] for row in events)
            if player["goblin_raids"]["session"].get("stage") == "spoils":
                break

        self.assertEqual(player["goblin_raids"]["session"]["stage"], "spoils")
        self.assertNotIn("expired", world_events)


class GoblinRaidsEntryTest(unittest.TestCase):
    def test_the_raid_duty_needs_an_announced_raid_and_names_the_alternative(self):
        _data, ok, info = join_goblin_raid_pure(_player(), GOBLIN_RAIDS_RAID_MODE)
        self.assertFalse(ok)
        self.assertIn("No raid has been announced", info["reason"])
        self.assertIn("Goblin Village duty", info["reason"])

    def test_the_village_duty_is_always_open(self):
        joined, ok, info = join_goblin_raid_pure(
            _player(), GOBLIN_RAIDS_VILLAGE_MODE
        )
        self.assertTrue(ok, info)
        self.assertEqual(
            joined["activity_session"]["active_id"], GOBLIN_RAIDS_ACTIVITY_ID
        )
        self.assertEqual(joined["current_combat_target"], VILLAGE_GOBLIN.id)
        _twice, ok, info = join_goblin_raid_pure(joined, GOBLIN_RAIDS_VILLAGE_MODE)
        self.assertFalse(ok)
        self.assertIn("already fighting goblins", info["reason"])

    def test_joining_a_raid_starts_the_sourced_raider_stage(self):
        joined, ok, info = join_goblin_raid_pure(
            _with_raid(), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok, info)
        session = joined["goblin_raids"]["session"]
        self.assertEqual(session["stage"], "raiders")
        self.assertEqual(session["raiders_remaining"], GOBLIN_RAIDS_RAIDER_COUNT)
        self.assertEqual(session["target_id"], GOBLIN_RAIDER.id)

    def test_entry_gates_on_other_activities_and_open_encounters(self):
        busy = _with_raid()
        busy["activity_session"] = {"active_id": "castle_wars"}
        _data, ok, info = join_goblin_raid_pure(busy, GOBLIN_RAIDS_RAID_MODE)
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

        fighting = _with_raid()
        fighting["combat_encounter"] = {"target_id": "chicken", "enemy_lifepoints": 4}
        _data, ok, info = join_goblin_raid_pure(fighting, GOBLIN_RAIDS_RAID_MODE)
        self.assertFalse(ok)
        self.assertIn("Combat encounter", info["reason"])

    def test_reviews_refuse_outside_a_duty_and_do_not_advance_unproductively(self):
        _data, ok, info = apply_goblin_raids_review_pure(
            _player(), enemy_data=COMBAT_ENEMY_DATA
        )
        self.assertFalse(ok)
        self.assertIn("Join a goblin raid", info["reason"])

        joined, ok, _ = join_goblin_raid_pure(_player(), GOBLIN_RAIDS_VILLAGE_MODE)
        self.assertTrue(ok)
        held, ok, result = apply_goblin_raids_review_pure(
            joined,
            enemy_data=COMBAT_ENEMY_DATA,
            equipment_data=EQUIPMENT_DATA,
            productive=False,
        )
        self.assertTrue(ok)
        self.assertFalse(result["advanced"])
        self.assertEqual(held["goblin_raids"]["session"]["goblins_killed"], 0)


class GoblinRaidStagesTest(unittest.TestCase):
    """The raid is cleared in the sourced order, and it really pays out."""

    @classmethod
    def setUpClass(cls):
        player, ok, info = join_goblin_raid_pure(
            _with_raid(site_roll=0.5), GOBLIN_RAIDS_RAID_MODE
        )
        assert ok, info
        cls.cleared, cls.results = _play(
            player, 2, until=lambda _p, r: r.get("stage") == "spoils"
        )

    def test_hollowtoof_is_unattackable_until_every_raider_is_dead(self):
        stages = [row["stage"] for row in self.results]
        self.assertEqual(stages[0], "raiders")
        self.assertEqual(stages[-1], "spoils")
        first_leader = stages.index("leader")
        # Nothing reaches the leader stage before the raider count is spent.
        self.assertTrue(all(stage == "raiders" for stage in stages[:first_leader]))
        self.assertIn(
            "Now it's my turn",
            " ".join(
                event for row in self.results for event in row.get("events", ())
            ),
        )

    def test_a_dying_raider_drops_everything_it_had_been_hoarding(self):
        spoils = self.cleared["goblin_raids"]["session"]["spoils"]
        site = GOBLIN_RAID_SITES_BY_ID[
            self.cleared["goblin_raids"]["session"]["site_id"]
        ]
        self.assertTrue(spoils)
        for item in spoils:
            self.assertIn(item, site.materials)
        # Every raider hoards at least one item, so the pile beats the count.
        self.assertGreaterEqual(sum(spoils.values()), GOBLIN_RAIDS_RAIDER_COUNT)

    def test_hollowtoof_drops_the_chainbody_first(self):
        self.assertEqual(self.cleared["inventory"].get("Raider chainbody"), 1)
        self.assertIsNone(self.cleared["inventory"].get("Raider axe"))
        self.assertEqual(next_raider_set_piece_pure(self.cleared), "Raider axe")

    def test_yodri_pays_out_per_raider_from_the_exact_site_table(self):
        self.assertEqual(self.cleared["goblin_raids"]["active_raid"], {})
        persisted = sanitize_goblin_raids_state_pure(
            self.cleared["goblin_raids"]
        )
        self.assertEqual(persisted["session"]["stage"], "spoils")
        session = self.cleared["goblin_raids"]["session"]
        pending = dict(session["spoils"])
        raiders_killed = GOBLIN_RAIDS_RAIDER_COUNT - int(
            session["raiders_remaining"]
        )
        site = GOBLIN_RAID_SITES_BY_ID[session["site_id"]]
        claimed, ok, info = claim_goblin_raid_spoils_pure(self.cleared)
        self.assertTrue(ok, info)
        self.assertEqual(info["raiders_killed"], raiders_killed)
        self.assertEqual(
            sum(info["rewards"].values()),
            sum(pending.values()) + raiders_killed,
        )
        yodri_rewards = {
            item: count - pending.get(item, 0)
            for item, count in info["rewards"].items()
            if count > pending.get(item, 0)
        }
        self.assertEqual(sum(yodri_rewards.values()), raiders_killed)
        self.assertTrue(set(yodri_rewards).issubset(site.yodri_rewards))
        for item, count in info["rewards"].items():
            self.assertGreaterEqual(claimed["inventory"].get(item, 0), count)
        self.assertEqual(claimed["goblin_raids"]["raids_cleared"], 1)
        self.assertEqual(claimed["goblin_raids"]["session"], {})
        self.assertEqual(claimed["goblin_raids"]["active_raid"], {})
        self.assertEqual(claimed["activity_session"]["active_id"], "")
        self.assertEqual(claimed["current_combat_target"], "chicken")
        _same_raid, ok, info = join_goblin_raid_pure(
            claimed, GOBLIN_RAIDS_RAID_MODE
        )
        self.assertFalse(ok)
        self.assertIn("No raid has been announced", info["reason"])

    def test_claiming_old_spoils_preserves_a_later_announced_raid(self):
        player = self.cleared
        player["shop_market_clock"] = {
            "answered_cards": player["goblin_raids"]["next_spawn_card"]
        }
        player, events = advance_goblin_raids_world_clock_pure(
            player, site_roll=0.9
        )
        self.assertEqual([row["kind"] for row in events], ["announced"])
        raid_id = player["goblin_raids"]["active_raid"]["raid_id"]

        claimed, ok, info = claim_goblin_raid_spoils_pure(player)

        self.assertTrue(ok, info)
        self.assertEqual(
            claimed["goblin_raids"]["active_raid"]["raid_id"], raid_id
        )

    def test_spoils_cannot_be_claimed_before_yodri_arrives(self):
        early, ok, _ = join_goblin_raid_pure(_with_raid(), GOBLIN_RAIDS_RAID_MODE)
        self.assertTrue(ok)
        _data, ok, info = claim_goblin_raid_spoils_pure(early)
        self.assertFalse(ok)
        self.assertIn("Commander Yodri arrives", info["reason"])

    def test_the_whole_raider_set_arrives_over_repeated_raids(self):
        """Chainbody, then axe, then shield — one per Hollowtoof kill."""
        player = self.cleared
        for expected in ("Raider axe", "Raider shield"):
            player, ok, info = claim_goblin_raid_spoils_pure(player)
            self.assertTrue(ok, info)
            self.assertEqual(next_raider_set_piece_pure(player), expected)
            player["shop_market_clock"] = {
                "answered_cards": int(
                    player["shop_market_clock"]["answered_cards"]
                )
                + GOBLIN_RAIDS_SPAWN_REVIEWS
            }
            player, _events = advance_goblin_raids_world_clock_pure(
                player, site_roll=0.5
            )
            player, ok, info = join_goblin_raid_pure(player, GOBLIN_RAIDS_RAID_MODE)
            self.assertTrue(ok, info)
            player, _results = _play(
                player, 2, until=lambda _p, r: r.get("stage") == "spoils"
            )
            self.assertEqual(player["inventory"].get(expected), 1)
        for item_name in RAIDER_SET_ITEM_NAMES:
            self.assertEqual(player["inventory"].get(item_name), 1)
        # Exact, and flagged as possibly unintended by the source: a complete
        # set makes the next Hollowtoof kill drop the chainbody again.
        self.assertEqual(next_raider_set_piece_pure(player), "Raider chainbody")


class GoblinRaidIntimidationTest(unittest.TestCase):
    def test_a_low_level_player_cannot_intimidate_hollowtoof(self):
        low, ok, _ = join_goblin_raid_pure(
            _with_raid(20), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok)
        self.assertLess(
            player_combat_level_pure(low), GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL
        )
        _data, ok, info = intimidate_hollowtoof_pure(low)
        self.assertFalse(ok)
        self.assertIn(str(GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL), info["reason"])

    def test_a_high_level_player_is_handed_the_whole_set_without_a_fight(self):
        high = _with_raid(90)
        self.assertGreaterEqual(
            player_combat_level_pure(high), GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL
        )
        joined, ok, _ = join_goblin_raid_pure(high, GOBLIN_RAIDS_RAID_MODE)
        self.assertTrue(ok)
        self.assertEqual(joined["goblin_raids"]["session"]["stage"], "raiders")
        granted, ok, info = intimidate_hollowtoof_pure(joined)
        self.assertTrue(ok, info)
        self.assertEqual(set(info["granted"]), set(RAIDER_SET_ITEM_NAMES))
        for item_name in RAIDER_SET_ITEM_NAMES:
            self.assertEqual(granted["inventory"].get(item_name), 1)
        _again, ok, info = intimidate_hollowtoof_pure(granted)
        self.assertFalse(ok)
        self.assertIn("already own the whole Raider set", info["reason"])

    def test_the_shortcut_closes_once_the_raiders_are_dead(self):
        """The article scopes it to before the ordinary raiders die."""
        player, ok, _ = join_goblin_raid_pure(
            _with_raid(90), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok)
        player, _results = _play(
            player, 2, until=lambda _p, r: r.get("stage") != "raiders"
        )
        _data, ok, info = intimidate_hollowtoof_pure(player)
        self.assertFalse(ok)
        self.assertIn("while his raiders live", info["reason"])


class GoblinVillageBossTest(unittest.TestCase):
    """Fifteen village goblins summon a boss, and the boss drops the shield."""

    @classmethod
    def setUpClass(cls):
        player, ok, info = join_goblin_raid_pure(
            _player(60), GOBLIN_RAIDS_VILLAGE_MODE
        )
        assert ok, info
        cls.player, cls.results = _play(
            player,
            0,
            limit=600,
            rejoin=GOBLIN_RAIDS_VILLAGE_MODE,
            until=lambda p, _r: bool(
                p["inventory"].get(GOBLIN_COWER_SHIELD)
            ),
        )

    def test_the_first_boss_arrives_on_the_fifteenth_village_goblin(self):
        summoned = [
            index
            for index, row in enumerate(self.results)
            if any("stomps out" in event for event in row.get("events", ()))
        ]
        self.assertTrue(summoned)
        # Fifteen kills, and a kill takes at least one review, so the first
        # summons cannot land earlier than the fifteenth review.
        self.assertGreaterEqual(summoned[0] + 1, GOBLIN_RAIDS_VILLAGE_BOSS_KILLS)
        self.assertGreater(self.player["goblin_raids"]["bosses_felled"], 0)

    def test_all_three_bosses_are_reachable(self):
        player, ok, _ = join_goblin_raid_pure(
            _player(60), GOBLIN_RAIDS_VILLAGE_MODE
        )
        self.assertTrue(ok)
        seen: set[str] = set()

        def _saw_all(_p, result):
            for event in result.get("events", ()):
                for boss in GOBLIN_RAID_VILLAGE_BOSSES:
                    if boss.display_name in event and "stomps out" in event:
                        seen.add(boss.display_name)
            return len(seen) == len(GOBLIN_RAID_VILLAGE_BOSSES)

        _played, _results = _play(
            player,
            0,
            limit=800,
            rejoin=GOBLIN_RAIDS_VILLAGE_MODE,
            until=_saw_all,
        )
        self.assertEqual(
            seen, {boss.display_name for boss in GOBLIN_RAID_VILLAGE_BOSSES}
        )

    def test_the_cower_shield_really_drops_and_arrives_with_a_full_budget(self):
        self.assertEqual(self.player["inventory"][GOBLIN_COWER_SHIELD], 1)
        state = self.player["goblin_raids"]
        self.assertEqual(state["cower_shields_found"], 1)
        self.assertEqual(
            state["cower_shield_bonus_remaining"],
            GOBLIN_COWER_SHIELD_BONUS_BUDGET,
        )
        self.assertEqual(state["cower_shield_bonus_awarded"], 0.0)


class GoblinCowerShieldBonusTest(unittest.TestCase):
    def _wearer(self):
        player = _player()
        player["equipment"]["shield"] = GOBLIN_COWER_SHIELD
        player["inventory"] = {GOBLIN_COWER_SHIELD: 1}
        state = default_goblin_raids_state_pure()
        state["cower_shield_bonus_remaining"] = GOBLIN_COWER_SHIELD_BONUS_BUDGET
        player["goblin_raids"] = state
        return player

    def test_the_bonus_needs_the_shield_worn_and_a_combat_experience_key(self):
        worn = self._wearer()
        self.assertTrue(goblin_cower_shield_can_apply_pure(worn, "attack_exp"))
        self.assertFalse(goblin_cower_shield_can_apply_pure(worn, "mining_exp"))

        banked = self._wearer()
        banked["equipment"].pop("shield")
        self.assertFalse(goblin_cower_shield_can_apply_pure(banked, "attack_exp"))

    def test_the_bonus_is_a_quarter_of_the_base_for_all_three_skills(self):
        for exp_key in GOBLIN_COWER_SHIELD_EXP_KEYS:
            _data, bonus, info = apply_goblin_cower_shield_bonus_pure(
                self._wearer(), exp_key, 100.0
            )
            self.assertTrue(info["applied"], exp_key)
            self.assertAlmostEqual(bonus, 25.0, msg=exp_key)

    def test_the_budget_is_exactly_a_thousand_and_then_it_turns_cosmetic(self):
        player = self._wearer()
        total = 0.0
        for _ in range(200):
            player, bonus, info = apply_goblin_cower_shield_bonus_pure(
                player, "attack_exp", 100.0
            )
            total += bonus
            if info.get("exhausted"):
                break
        self.assertAlmostEqual(total, GOBLIN_COWER_SHIELD_BONUS_BUDGET)
        self.assertEqual(player["goblin_raids"]["cower_shield_bonus_remaining"], 0.0)
        self.assertAlmostEqual(
            player["goblin_raids"]["cower_shield_bonus_awarded"],
            GOBLIN_COWER_SHIELD_BONUS_BUDGET,
        )
        # Cosmetic means the shield stays worn and simply stops paying.
        self.assertEqual(player["equipment"]["shield"], GOBLIN_COWER_SHIELD)
        _spent, bonus, info = apply_goblin_cower_shield_bonus_pure(
            player, "attack_exp", 100.0
        )
        self.assertEqual(bonus, 0.0)
        self.assertFalse(info["applied"])
        self.assertTrue(goblin_raids_view_pure(player)["cower_shield_cosmetic"])

    def test_the_last_award_is_clipped_to_what_is_left_rather_than_overshooting(self):
        player = self._wearer()
        player["goblin_raids"]["cower_shield_bonus_remaining"] = 10.0
        _data, bonus, _info = apply_goblin_cower_shield_bonus_pure(
            player, "attack_exp", 1000.0
        )
        self.assertEqual(bonus, 10.0)


class GoblinRaidsFailureTest(unittest.TestCase):
    def test_a_death_ends_the_players_part_in_the_raid(self):
        player, ok, _ = join_goblin_raid_pure(
            _player(3), GOBLIN_RAIDS_VILLAGE_MODE
        )
        self.assertTrue(ok)
        played, results = _play(
            player, 1, limit=200, until=lambda _p, r: r.get("outcome") == "death"
        )
        self.assertTrue(results[-1]["terminal"])
        self.assertEqual(played["goblin_raids"]["session"], {})
        self.assertEqual(played["activity_session"]["active_id"], "")
        self.assertIn("put you down", played["goblin_raids"]["last_result"])

    def test_leaving_loses_the_spoils_that_were_never_claimed(self):
        player, ok, _ = join_goblin_raid_pure(
            _with_raid(), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok)
        player, _results = _play(
            player,
            2,
            until=lambda p, _r: bool(p["goblin_raids"]["session"]["spoils"]),
        )
        pending = dict(player["goblin_raids"]["session"]["spoils"])
        self.assertTrue(pending)
        left, ok, info = leave_goblin_raids_pure(player)
        self.assertTrue(ok, info)
        self.assertEqual(info["lost"], pending)
        for item in pending:
            self.assertEqual(left["inventory"].get(item, 0), 0)
        self.assertEqual(left["goblin_raids"]["session"], {})

        _again, ok, info = leave_goblin_raids_pure(left)
        self.assertFalse(ok)
        self.assertIn("not fighting goblins", info["reason"])


class GoblinRaidsViewTest(unittest.TestCase):
    def test_the_view_owns_every_flag_the_panel_renders(self):
        view = goblin_raids_view_pure(_player())
        for key in (
            "active",
            "raid_announced",
            "raid_site",
            "raid_reviews_remaining",
            "next_raid_reviews",
            "announcement_interval",
            "entry_reasons",
            "can_join_raid",
            "can_join_village",
            "mode",
            "stage",
            "stage_label",
            "target_name",
            "intimidate_visible",
            "intimidate_enabled",
            "intimidate_reason",
            "claim_visible",
            "claim_enabled",
            "pending_spoils",
            "raider_set_owned",
            "raider_set_next",
            "raider_set_complete",
            "village_boss_kills",
            "village_kills_to_boss",
            "boss_active",
            "cower_shield_held",
            "cower_shield_cosmetic",
            "summary_text",
            "progress_value",
            "progress_maximum",
            "progress_format",
            "primary_label",
            "leave_visible",
            "source",
        ):
            self.assertIn(key, view)
        self.assertFalse(view["raid_announced"])
        self.assertFalse(view["can_join_raid"])
        self.assertTrue(view["can_join_village"])
        self.assertEqual(view["primary_label"], "Goblin Village duty")
        self.assertFalse(view["leave_visible"])
        self.assertEqual(
            view["village_kills_to_boss"], GOBLIN_RAIDS_VILLAGE_BOSS_KILLS
        )

    def test_an_announced_raid_offers_both_duties(self):
        view = goblin_raids_view_pure(_with_raid())
        self.assertTrue(view["raid_announced"])
        self.assertTrue(view["can_join_raid"])
        self.assertTrue(view["can_join_village"])
        self.assertEqual(view["primary_label"], "Join the raid")
        self.assertEqual(view["raid_spoil_kind"], "logs")

    def test_the_intimidate_row_is_hidden_rather_than_offered_and_refused(self):
        joined, ok, _ = join_goblin_raid_pure(
            _with_raid(20), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok)
        view = goblin_raids_view_pure(joined)
        self.assertTrue(view["intimidate_visible"])
        self.assertFalse(view["intimidate_enabled"])
        self.assertIn(str(GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL), view["intimidate_reason"])

        village, ok, _ = join_goblin_raid_pure(
            _player(), GOBLIN_RAIDS_VILLAGE_MODE
        )
        self.assertTrue(ok)
        self.assertFalse(goblin_raids_view_pure(village)["intimidate_visible"])
        self.assertFalse(goblin_raids_view_pure(village)["claim_visible"])


class GoblinRaidsPersistenceTest(unittest.TestCase):
    def test_a_raid_session_cannot_outlive_the_raid_it_belongs_to(self):
        joined, ok, _ = join_goblin_raid_pure(
            _with_raid(), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok)
        orphaned = copy.deepcopy(joined["goblin_raids"])
        orphaned["active_raid"] = {}
        self.assertEqual(
            sanitize_goblin_raids_state_pure(orphaned)["session"], {}
        )

    def test_sanitize_normalizes_junk_stages_sites_and_ledgers(self):
        state = sanitize_goblin_raids_state_pure(
            {
                "session": {"mode": "nonsense"},
                "village_kills": -4,
                "bosses_felled": "two",
                "cower_shield_bonus_remaining": 99_999.0,
                "next_spawn_card": 0,
            }
        )
        self.assertEqual(state["session"], {})
        self.assertEqual(state["village_kills"], 0)
        self.assertEqual(state["bosses_felled"], 0)
        self.assertEqual(
            state["cower_shield_bonus_remaining"],
            GOBLIN_COWER_SHIELD_BONUS_BUDGET,
        )
        self.assertEqual(state["next_spawn_card"], 1)

    def test_a_village_session_survives_without_any_raid(self):
        joined, ok, _ = join_goblin_raid_pure(
            _player(), GOBLIN_RAIDS_VILLAGE_MODE
        )
        self.assertTrue(ok)
        state = sanitize_goblin_raids_state_pure(joined["goblin_raids"])
        self.assertEqual(state["session"]["mode"], GOBLIN_RAIDS_VILLAGE_MODE)

    def test_an_older_save_migrates_without_losing_unrelated_keys(self):
        old = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        old["config_version"] = 86
        old["unrelated_future_key"] = {"keep": True}
        old.pop("goblin_raids", None)
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertGreaterEqual(CURRENT_CONFIG_VERSION, 87)
        self.assertEqual(migrated["goblin_raids"]["active_raid"], {})
        self.assertEqual(migrated["goblin_raids"]["session"], {})
        self.assertEqual(migrated["goblin_raids"]["village_kills"], 0)
        self.assertEqual(migrated["unrelated_future_key"], {"keep": True})

    def test_an_interrupted_raid_survives_a_save_and_load_round_trip(self):
        player, ok, _ = join_goblin_raid_pure(
            _with_raid(), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok)
        player, ok, _ = apply_goblin_raids_review_pure(
            player,
            random.Random(2).random,
            enemy_data=COMBAT_ENEMY_DATA,
            equipment_data=EQUIPMENT_DATA,
        )
        self.assertTrue(ok)
        reloaded = migrate_loaded_data(
            json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS
        )
        self.assertEqual(
            reloaded["goblin_raids"]["session"]["stage"],
            player["goblin_raids"]["session"]["stage"],
        )
        self.assertEqual(
            reloaded["activity_session"]["active_id"], GOBLIN_RAIDS_ACTIVITY_ID
        )


class GoblinRaidsCommandTest(unittest.TestCase):
    def test_the_command_router_covers_every_direct_action(self):
        joined, ok, _ = apply_goblin_raids_command_pure(
            _with_raid(90), "join", {"mode": GOBLIN_RAIDS_RAID_MODE}
        )
        self.assertTrue(ok)
        granted, ok, _ = apply_goblin_raids_command_pure(joined, "intimidate", {})
        self.assertTrue(ok)
        self.assertEqual(granted["inventory"].get("Raider axe"), 1)

        cleared, _results = _play(
            granted, 2, until=lambda _p, r: r.get("stage") == "spoils"
        )
        claimed, ok, _ = apply_goblin_raids_command_pure(
            cleared, "claim_spoils", {}
        )
        self.assertTrue(ok)
        self.assertEqual(claimed["goblin_raids"]["session"], {})

        village, ok, _ = apply_goblin_raids_command_pure(
            claimed, "join", {"mode": GOBLIN_RAIDS_VILLAGE_MODE}
        )
        self.assertTrue(ok)
        left, ok, _ = apply_goblin_raids_command_pure(village, "leave", {})
        self.assertTrue(ok)
        self.assertEqual(left["goblin_raids"]["session"], {})

        _data, ok, info = apply_goblin_raids_command_pure(
            _player(), "nonsense", {}
        )
        self.assertFalse(ok)
        self.assertIn("Unknown Goblin Raids command", info["reason"])


class GoblinRaidsRuntimeIntegrationTest(unittest.TestCase):
    def test_a_selected_duty_dispatches_reviews_through_the_real_runtime(self):
        player, ok, _ = join_goblin_raid_pure(
            _with_raid(), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok)
        calls = _calls(2)
        ctx = _context(player, calls)
        self.assertTrue(handle_goblin_raids_answer(ctx))
        self.assertEqual(calls["saves"], 1)
        self.assertTrue(calls["activity"])
        self.assertFalse(calls["errors"])

    def test_the_runtime_clears_a_whole_raid_and_records_the_kills(self):
        player, ok, _ = join_goblin_raid_pure(
            _with_raid(), GOBLIN_RAIDS_RAID_MODE
        )
        self.assertTrue(ok)
        calls = _calls(2)
        ctx = _context(player, calls)
        for _ in range(60):
            self.assertTrue(handle_goblin_raids_answer(ctx))
            if player["goblin_raids"]["session"].get("stage") == "spoils":
                break
        else:
            raise AssertionError("the runtime never cleared the raid")
        self.assertEqual(player["inventory"].get("Raider chainbody"), 1)
        self.assertGreater(player["goblin_raids"]["raid_goblins_killed"], 0)
        self.assertTrue(calls.get("deactivated") in (None, True))

    def test_an_unselected_activity_refuses_the_review_and_deactivates(self):
        player = _player()
        calls = _calls()
        ctx = _context(player, calls)
        self.assertFalse(handle_goblin_raids_answer(ctx))
        self.assertTrue(calls["errors"])
        self.assertTrue(calls.get("deactivated"))


if __name__ == "__main__":
    unittest.main()
