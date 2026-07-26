from __future__ import annotations

import copy
import json
import random
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    COMBAT_ENEMY_DATA,
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
from ankiscape.data.clan_wars_data import (
    CLAN_WARS_ACTIVITY_ID,
    CLAN_WARS_COMBAT_TARGET_ID,
    CLAN_WARS_CROSSFIRE_START_REVIEW,
    CLAN_WARS_MAX_REVIEWS,
    CLAN_WARS_MODES,
    CLAN_WARS_PLAYER_CROSSFIRE_DIVISOR,
    CLAN_WARS_PURPLE_MODE,
    CLAN_WARS_RED_BOOST_CAPS,
    CLAN_WARS_RED_MODE,
    CLAN_WARS_WHITE_MODE,
)
from ankiscape.logic.clan_wars_logic import (
    apply_clan_wars_command_pure,
    apply_clan_wars_review_pure,
    clan_wars_view_pure,
    default_clan_wars_state_pure,
    enter_clan_wars_pure,
    leave_clan_wars_pure,
    sanitize_clan_wars_state_pure,
    set_clan_wars_policy_pure,
    teleport_escape_clan_wars_pure,
)
from ankiscape.logic_pure.logic_pure import combat_max_lifepoints_pure
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    handle_utility_answer,
)


ROOT = Path(__file__).resolve().parents[1]

# Every seed below was found by running the real review loop and recording a
# run that reaches the named outcome, so each one is a proof that a player can
# get there rather than a number chosen to make an assertion pass.
WHITE_WIN_SEED = 0
WHITE_LOSS_SEED = 1
WHITE_DRAW_SEED = 12
PURPLE_WIN_SEED = 1
PURPLE_DRAW_SEED = 0
PURPLE_LOSS_SEED = 5
RED_DEATH_SEED = 9
SAFE_DEATH_SEED = 0


def _player(levels: int = 40, weapon: str = "Mithril scimitar", **overrides):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for key in (
        "attack_level",
        "strength_level",
        "defense_level",
        "constitution_level",
    ):
        player[key] = levels
    player["equipment"] = {"weapon": weapon}
    player["inventory"] = {}
    player["carried_inventory"] = {}
    player["current_combat_target"] = "chicken"
    player["current_utility"] = "make_soft_clay"
    player["combat_encounter"] = {}
    player["activity_session"] = {"active_id": ""}
    player["combat_lifepoints"] = levels * 10
    player.update(overrides)
    return player


def _armoured_player(protect_item: bool = False):
    """Three worn pieces plus a four-Lobster carried pack: seven items at risk."""
    player = _player(prayer_level=60)
    player["equipment"] = {
        "weapon": "Mithril scimitar",
        "body": "Mithril platebody",
        "legs": "Mithril platelegs",
    }
    player["inventory"] = {"Lobster": 4}
    player["carried_inventory"] = {"chicken": {"Lobster": 4}}
    if protect_item:
        player["combat_prayer_book"] = "standard"
        player["combat_selected_prayers"] = ["protect_item"]
        player["combat_prayers_enabled"] = True
        player["combat_prayer_uptime"] = "100"
        player["combat_prayer_points"] = 600
    return player


def _play_match(player, mode, seed, *, reviews=CLAN_WARS_MAX_REVIEWS):
    """Run a real match to its terminal review and return (result, player)."""
    draws = random.Random(seed).random
    player, ok, info = enter_clan_wars_pure(player, mode)
    if not ok:
        raise AssertionError(info)
    for _ in range(reviews):
        player, ok, result = apply_clan_wars_review_pure(
            player,
            draws,
            equipment_data=EQUIPMENT_DATA,
        )
        if not ok:
            raise AssertionError(result)
        if result.get("terminal"):
            return result, player
    raise AssertionError("the bounded match never terminated")


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
        check_achievements=lambda _data: calls.__setitem__(
            "achievements", True
        ),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: calls.__setitem__("refresh", True),
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda message: calls["activity"].append(message),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class ClanWarsDataTest(unittest.TestCase):
    def test_both_portals_and_the_team_race_are_registered(self):
        self.assertEqual(
            tuple(mode.id for mode in CLAN_WARS_MODES),
            (CLAN_WARS_WHITE_MODE, CLAN_WARS_RED_MODE, CLAN_WARS_PURPLE_MODE),
        )
        dangerous = [mode for mode in CLAN_WARS_MODES if mode.dangerous]
        self.assertEqual(
            [mode.id for mode in dangerous],
            [CLAN_WARS_RED_MODE],
        )
        # Only the dangerous portal warns, and it must say what is lost.
        for mode in CLAN_WARS_MODES:
            with self.subTest(mode=mode.id):
                self.assertEqual(bool(mode.entry_warning), mode.dangerous)
        self.assertIn("destroyed", dangerous[0].entry_warning)
        self.assertIn("no gravestone", dangerous[0].entry_warning)

    def test_the_red_portal_boost_caps_match_the_sourced_server_formula(self):
        """Darkan `Potions.kt` `checkPVPPotionBoosts`, called on dangerous entry.

        Pinned as literals rather than derived from the constant, so a value
        edited to something plausible still fails here.
        """
        self.assertEqual(
            CLAN_WARS_RED_BOOST_CAPS,
            (
                ("attack", 5, 0.15),
                ("strength", 5, 0.15),
                ("defense", 5, 0.15),
                ("ranged", 5, 0.10),
                ("magic", 5, 0.0),
            ),
        )

    def test_activity_enemy_and_asset_registration(self):
        activity = UTILITY_ACTIVITY_DATA[CLAN_WARS_ACTIVITY_ID]
        self.assertEqual(activity["surface"], "activities")
        self.assertEqual(activity["group"], "minigames")
        self.assertTrue(Path(activity["icon_path"]).is_file())
        enemy = COMBAT_ENEMY_DATA[CLAN_WARS_COMBAT_TARGET_ID]
        # The registry row must carry the same shape every other enemy does,
        # or the combat engine silently reads zeroes off it.
        self.assertEqual(
            set(enemy["stats"]),
            {"attack", "strength", "defence", "hitpoints", "magic", "ranged"},
        )
        self.assertEqual(enemy["attack_style"], "melee")
        provenance = json.loads(
            (ROOT / "assets_provenance.json").read_text(encoding="utf-8")
        )
        self.assertIn("activityicons/clan_wars.png", provenance)
        self.assertLess(
            provenance["activityicons/clan_wars.png"]["timestamp"],
            "2012-11-20T00:00:00Z",
        )


class ClanWarsPureTest(unittest.TestCase):
    def test_policy_saves_every_portal_and_refuses_unknown_and_mid_match(self):
        original = _player()
        for mode in CLAN_WARS_MODES:
            with self.subTest(mode=mode.id):
                updated, ok, _ = set_clan_wars_policy_pure(original, mode.id)
                self.assertTrue(ok)
                self.assertEqual(
                    updated["clan_wars_policy"], {"mode": mode.id}
                )
        self.assertEqual(
            original["clan_wars_policy"]["mode"], CLAN_WARS_WHITE_MODE
        )

        _, ok, result = set_clan_wars_policy_pure(original, "gold_portal")
        self.assertFalse(ok)
        self.assertIn("Unknown", result["reason"])

        active, ok, _ = enter_clan_wars_pure(original, CLAN_WARS_RED_MODE)
        self.assertTrue(ok)
        _, ok, result = set_clan_wars_policy_pure(active, CLAN_WARS_WHITE_MODE)
        self.assertFalse(ok)
        self.assertIn("Finish or leave", result["reason"])

    def test_entry_gates_on_other_activities_and_open_encounters(self):
        busy = _player()
        busy["activity_session"] = {"active_id": "soul_wars"}
        _, ok, result = enter_clan_wars_pure(busy, CLAN_WARS_WHITE_MODE)
        self.assertFalse(ok)
        self.assertIn("persistent activity", result["reason"])

        fighting = _player()
        fighting["combat_encounter"] = {"target_id": "chicken"}
        _, ok, result = enter_clan_wars_pure(fighting, CLAN_WARS_WHITE_MODE)
        self.assertFalse(ok)
        self.assertIn("Combat encounter", result["reason"])

        entered, ok, _ = enter_clan_wars_pure(_player(), CLAN_WARS_WHITE_MODE)
        self.assertTrue(ok)
        _, ok, result = enter_clan_wars_pure(entered, CLAN_WARS_WHITE_MODE)
        self.assertFalse(ok)
        self.assertIn("already active", result["reason"])

    def test_entry_carries_the_pack_and_restores_the_previous_target_on_leave(self):
        player = _player()
        player["carried_inventory"] = {"chicken": {"Lobster": 3}}
        player["inventory"] = {"Lobster": 3}
        entered, ok, _ = enter_clan_wars_pure(player, CLAN_WARS_WHITE_MODE)
        self.assertTrue(ok)
        self.assertEqual(
            entered["carried_inventory"][CLAN_WARS_COMBAT_TARGET_ID],
            {"Lobster": 3},
        )
        self.assertEqual(
            entered["current_combat_target"], CLAN_WARS_COMBAT_TARGET_ID
        )
        self.assertEqual(entered["current_utility"], CLAN_WARS_ACTIVITY_ID)
        self.assertEqual(
            entered["activity_session"]["active_id"], CLAN_WARS_ACTIVITY_ID
        )

        left, ok, result = leave_clan_wars_pure(entered)
        self.assertTrue(ok)
        self.assertEqual(result["outcome"], "exit")
        self.assertEqual(left["clan_wars"], {})
        self.assertEqual(left["clan_wars_exits"], 1)
        self.assertEqual(left["current_combat_target"], "chicken")
        self.assertEqual(left["activity_session"]["active_id"], "")
        self.assertNotIn(
            CLAN_WARS_COMBAT_TARGET_ID, left["carried_inventory"]
        )
        # Leaving is not a loss: the pack is still banked.
        self.assertEqual(left["inventory"]["Lobster"], 3)

        _, ok, result = leave_clan_wars_pure(_player())
        self.assertFalse(ok)
        self.assertIn("No Clan Wars match", result["reason"])

    def test_red_portal_clamps_boosts_and_the_other_portals_do_not(self):
        boosted = _player()
        boosted["combat_current_levels"] = {
            "attack": 99,
            "strength": 99,
            "defense": 99,
            "ranged": 99,
            "magic": 99,
        }
        red, ok, result = enter_clan_wars_pure(boosted, CLAN_WARS_RED_MODE)
        self.assertTrue(ok)
        self.assertTrue(result["boosts_clamped"])
        self.assertIn("super-potion caps", result["message"])
        for skill_id, flat, multiplier in CLAN_WARS_RED_BOOST_CAPS:
            with self.subTest(skill=skill_id):
                base_key = (
                    "defense_level"
                    if skill_id == "defense"
                    else f"{skill_id}_level"
                )
                base = boosted[base_key]
                self.assertEqual(
                    red["combat_current_levels"][skill_id],
                    base + flat + int(base * multiplier),
                )

        white, ok, result = enter_clan_wars_pure(boosted, CLAN_WARS_WHITE_MODE)
        self.assertTrue(ok)
        self.assertFalse(result["boosts_clamped"])
        self.assertEqual(white["combat_current_levels"]["attack"], 99)

    def test_teleport_escape_works_outside_the_red_portal_and_is_refused_inside(self):
        for mode in CLAN_WARS_MODES:
            entered, ok, _ = enter_clan_wars_pure(_player(), mode.id)
            self.assertTrue(ok)
            escaped, ok, result = teleport_escape_clan_wars_pure(entered)
            with self.subTest(mode=mode.id):
                if mode.dangerous:
                    self.assertFalse(ok)
                    self.assertIn("forbidden", result["reason"])
                    self.assertTrue(escaped["clan_wars"])
                else:
                    self.assertTrue(ok)
                    self.assertEqual(escaped["clan_wars"], {})

        _, ok, result = teleport_escape_clan_wars_pure(_player())
        self.assertFalse(ok)
        self.assertIn("No Clan Wars match", result["reason"])

    def test_reviews_refuse_outside_a_match_and_do_not_advance_when_unproductive(self):
        unchanged, ok, result = apply_clan_wars_review_pure(_player())
        self.assertFalse(ok)
        self.assertIn("Enter a Clan Wars portal", result["reason"])

        entered, ok, _ = enter_clan_wars_pure(_player(), CLAN_WARS_WHITE_MODE)
        self.assertTrue(ok)
        unchanged, ok, result = apply_clan_wars_review_pure(
            entered,
            productive=False,
        )
        self.assertTrue(ok)
        self.assertFalse(result["advanced"])
        self.assertEqual(unchanged["clan_wars"]["review"], 0)

    def test_crossfire_wears_the_player_down_but_never_lands_the_killing_blow(self):
        """The red portal must have exactly one death path: the combat burst."""
        player, ok, _ = enter_clan_wars_pure(_player(), CLAN_WARS_RED_MODE)
        self.assertTrue(ok)
        maximum = combat_max_lifepoints_pure(player)
        expected = max(1, maximum // CLAN_WARS_PLAYER_CROSSFIRE_DIVISOR)
        seen = []
        for review in range(CLAN_WARS_MAX_REVIEWS):
            # A one-lifepoint player proves the floor: crossfire may not kill.
            player["combat_lifepoints"] = 1
            player, ok, result = apply_clan_wars_review_pure(
                player,
                lambda: 1.0,  # every attack misses, so only crossfire moves LP
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok)
            seen.append(result["crossfire_damage"])
            if result.get("terminal"):
                break
        self.assertEqual(
            seen[:CLAN_WARS_CROSSFIRE_START_REVIEW],
            [0] * CLAN_WARS_CROSSFIRE_START_REVIEW,
        )
        self.assertTrue(all(value == 0 for value in seen[CLAN_WARS_CROSSFIRE_START_REVIEW:]))
        self.assertEqual(player["clan_wars_deaths"], 0)

        # From full lifepoints the same reviews do land the disclosed chip.
        healthy, ok, _ = enter_clan_wars_pure(_player(), CLAN_WARS_RED_MODE)
        self.assertTrue(ok)
        healthy["clan_wars"]["review"] = CLAN_WARS_CROSSFIRE_START_REVIEW
        healthy, ok, result = apply_clan_wars_review_pure(
            healthy,
            lambda: 1.0,
            equipment_data=EQUIPMENT_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(result["crossfire_damage"], expected)

    def test_every_free_for_all_outcome_is_reachable_through_real_play(self):
        expected = {
            WHITE_WIN_SEED: "win",
            WHITE_LOSS_SEED: "loss",
            WHITE_DRAW_SEED: "draw",
        }
        for seed, outcome in expected.items():
            with self.subTest(seed=seed):
                player = _player(levels=70, weapon="Rune scimitar")
                player["inventory"] = {"Lobster": 12}
                player["carried_inventory"] = {"chicken": {"Lobster": 12}}
                result, played = _play_match(
                    player, CLAN_WARS_WHITE_MODE, seed
                )
                self.assertEqual(result["outcome"], outcome)
                self.assertEqual(played[f"clan_wars_{outcome}es"
                                        if outcome == "loss"
                                        else f"clan_wars_{outcome}s"], 1)
                self.assertEqual(played["clan_wars_matches"], 1)
                self.assertEqual(played["clan_wars"], {})
                self.assertEqual(played["activity_session"]["active_id"], "")

    def test_every_team_race_outcome_is_reachable_through_real_play(self):
        expected = {
            PURPLE_WIN_SEED: "win",
            PURPLE_DRAW_SEED: "draw",
            PURPLE_LOSS_SEED: "loss",
        }
        for seed, outcome in expected.items():
            with self.subTest(seed=seed):
                player = _player(levels=70, weapon="Rune scimitar")
                player["inventory"] = {"Lobster": 12}
                player["carried_inventory"] = {"chicken": {"Lobster": 12}}
                result, _played = _play_match(
                    player, CLAN_WARS_PURPLE_MODE, seed
                )
                self.assertEqual(result["outcome"], outcome)
                self.assertIn("Team race", result["message"])

    def test_the_red_portal_can_also_be_survived_and_won(self):
        """Its danger must be a risk, not a certainty."""
        expected = {
            WHITE_WIN_SEED: "win",
            WHITE_LOSS_SEED: "loss",
            WHITE_DRAW_SEED: "draw",
        }
        for seed, outcome in expected.items():
            with self.subTest(seed=seed):
                player = _player(levels=70, weapon="Rune scimitar")
                player["inventory"] = {"Lobster": 12}
                player["carried_inventory"] = {"chicken": {"Lobster": 12}}
                result, played = _play_match(player, CLAN_WARS_RED_MODE, seed)
                self.assertEqual(result["outcome"], outcome)
                self.assertEqual(played["clan_wars_deaths"], 0)
                self.assertEqual(played["clan_wars_items_destroyed"], 0)
                self.assertEqual(played["equipment"], {"weapon": "Rune scimitar"})

    def test_kills_score_and_pay_real_combat_experience(self):
        player = _player(levels=70, weapon="Rune scimitar")
        result, played = _play_match(player, CLAN_WARS_WHITE_MODE, WHITE_WIN_SEED)
        self.assertGreater(result["player_score"], 0)
        self.assertGreater(played["clan_wars_kills"], 0)
        self.assertGreater(played["attack_exp"], 0)
        self.assertGreater(played["constitution_exp"], 0)

    def test_a_safe_portal_death_costs_a_point_and_keeps_every_item(self):
        player = _player()
        player["inventory"] = {"Lobster": 12}
        player["carried_inventory"] = {"chicken": {"Lobster": 12}}
        before = copy.deepcopy(player["equipment"])
        _result, played = _play_match(
            player, CLAN_WARS_WHITE_MODE, SAFE_DEATH_SEED
        )
        self.assertGreater(played["clan_wars_deaths"], 0)
        self.assertEqual(played["equipment"], before)
        self.assertEqual(played["inventory"]["Lobster"], 12)
        self.assertEqual(played["combat_grave"], {})
        self.assertEqual(played["death_office"], {})
        self.assertEqual(played["clan_wars_items_destroyed"], 0)


class ClanWarsRedPortalItemLossTest(unittest.TestCase):
    """The red portal is the owner's one non-negotiable Clan Wars decision.

    Whatever a red-portal death does not keep is gone: `_combat_apply_pvm_death`
    otherwise always writes a gravestone and pushes an older grave into Death's
    Office, which would hand every item back and silently reverse the decision.
    The grave and Death's Office assertions here fail if that safety net is
    restored. What the death *keeps* is a separate, sourced question:
    `sendPVPItemsOnDeath` keeps three items unskulled, four with Protect Item.
    """

    def test_a_red_portal_death_keeps_three_and_leaves_no_grave_or_death_office(self):
        result, played = _play_match(
            _armoured_player(), CLAN_WARS_RED_MODE, RED_DEATH_SEED
        )
        self.assertEqual(played["clan_wars_deaths"], 1)
        self.assertEqual(played["combat_grave"], {})
        self.assertEqual(played["death_office"], {})
        # Three kept, and the rest are gone rather than merely unrecoverable.
        self.assertEqual(
            played["equipment"],
            {
                "weapon": "Mithril scimitar",
                "body": "Mithril platebody",
                "legs": "Mithril platelegs",
            },
        )
        self.assertEqual(played["inventory"].get("Lobster", 0), 0)
        self.assertEqual(result["destroyed_items"], 4)
        self.assertEqual(played["clan_wars_items_destroyed"], 4)
        self.assertEqual(result["outcome"], "loss")
        self.assertIn("nothing was recoverable", result["message"])

    def test_protect_item_keeps_a_fourth_item_and_still_leaves_no_grave(self):
        result, played = _play_match(
            _armoured_player(protect_item=True),
            CLAN_WARS_RED_MODE,
            RED_DEATH_SEED,
        )
        self.assertEqual(played["clan_wars_deaths"], 1)
        self.assertEqual(
            played["equipment"],
            {
                "weapon": "Mithril scimitar",
                "body": "Mithril platebody",
                "legs": "Mithril platelegs",
            },
        )
        self.assertEqual(played["inventory"].get("Lobster", 0), 1)
        self.assertEqual(result["destroyed_items"], 3)
        self.assertEqual(played["combat_grave"], {})
        self.assertEqual(played["death_office"], {})

    def test_a_second_red_death_never_stacks_a_grave_into_death_office(self):
        """The stacking branch is where a restored safety net would resurface."""
        first = _armoured_player()
        _result, played = _play_match(first, CLAN_WARS_RED_MODE, RED_DEATH_SEED)
        self.assertEqual(played["combat_grave"], {})

        played["equipment"] = {
            "weapon": "Mithril scimitar",
            "body": "Mithril platebody",
            "legs": "Mithril platelegs",
        }
        played["inventory"] = {"Lobster": 4}
        played["carried_inventory"] = {"chicken": {"Lobster": 4}}
        played["current_combat_target"] = "chicken"
        played["combat_lifepoints"] = combat_max_lifepoints_pure(played)
        _result, twice = _play_match(played, CLAN_WARS_RED_MODE, RED_DEATH_SEED)
        self.assertEqual(twice["clan_wars_deaths"], 2)
        self.assertEqual(twice["clan_wars_items_destroyed"], 8)
        self.assertEqual(twice["combat_grave"], {})
        self.assertEqual(twice["death_office"], {})


class ClanWarsViewTest(unittest.TestCase):
    def test_the_view_owns_every_flag_the_panel_renders(self):
        idle = clan_wars_view_pure(_player())
        self.assertFalse(idle["active"])
        self.assertTrue(idle["can_enter"])
        self.assertEqual(idle["primary_label"], "Enter portal")
        self.assertTrue(idle["primary_enabled"])
        self.assertTrue(idle["mode_controls_enabled"])
        self.assertFalse(idle["leave_visible"])
        self.assertFalse(idle["teleport_escape_visible"])
        self.assertEqual(idle["status_label"], "SAFE")
        self.assertEqual(idle["entry_warning"], "")
        self.assertEqual(len(idle["mode_options"]), len(CLAN_WARS_MODES))
        self.assertTrue(all(row["selectable"] for row in idle["mode_options"]))

        red_planned = clan_wars_view_pure(
            set_clan_wars_policy_pure(_player(), CLAN_WARS_RED_MODE)[0]
        )
        self.assertTrue(red_planned["dangerous"])
        self.assertFalse(red_planned["safe_death"])
        self.assertEqual(red_planned["status_label"], "DANGEROUS")
        self.assertIn("destroyed", red_planned["entry_warning"])

        entered, ok, _ = enter_clan_wars_pure(_player(), CLAN_WARS_RED_MODE)
        self.assertTrue(ok)
        active = clan_wars_view_pure(entered)
        self.assertTrue(active["active"])
        self.assertFalse(active["can_enter"])
        self.assertFalse(active["mode_controls_enabled"])
        self.assertEqual(active["status_label"], "ACTIVE · DANGEROUS")
        self.assertTrue(active["leave_visible"])
        self.assertTrue(active["teleport_escape_visible"])
        self.assertFalse(active["teleport_escape_allowed"])
        self.assertIn("forbidden", active["teleport_escape_reason"])
        self.assertFalse(active["extreme_potions_allowed"])
        # Mid-match the only offered portal is the one being fought, which is
        # exactly what set_clan_wars_policy_pure will still accept.
        self.assertEqual(
            [row["id"] for row in active["mode_options"] if row["selectable"]],
            [CLAN_WARS_RED_MODE],
        )
        self.assertEqual(active["primary_label"], "Selected for reviews")
        self.assertFalse(active["primary_enabled"])
        self.assertEqual(active["progress_maximum"], CLAN_WARS_MAX_REVIEWS)

    def test_the_view_reports_why_entry_is_locked(self):
        busy = _player()
        busy["activity_session"] = {"active_id": "soul_wars"}
        view = clan_wars_view_pure(busy)
        self.assertFalse(view["can_enter"])
        self.assertIn(
            "Finish the active persistent activity.", view["entry_reasons"]
        )
        # A locked surface must not advertise an entry warning it cannot honour.
        self.assertEqual(view["entry_warning"], "")

    def test_a_safe_portal_view_permits_teleport_escape(self):
        entered, ok, _ = enter_clan_wars_pure(_player(), CLAN_WARS_PURPLE_MODE)
        self.assertTrue(ok)
        view = clan_wars_view_pure(entered)
        self.assertTrue(view["teleport_escape_allowed"])
        self.assertEqual(view["teleport_escape_reason"], "")
        self.assertEqual(view["status_label"], "ACTIVE · SAFE")


class ClanWarsPersistenceTest(unittest.TestCase):
    def test_sanitize_drops_a_session_owned_by_another_activity(self):
        entered, ok, _ = enter_clan_wars_pure(_player(), CLAN_WARS_RED_MODE)
        self.assertTrue(ok)
        entered["activity_session"] = {"active_id": "soul_wars"}
        self.assertEqual(sanitize_clan_wars_state_pure(entered)["clan_wars"], {})

    def test_sanitize_normalizes_unknown_modes_and_negative_ledgers(self):
        state = sanitize_clan_wars_state_pure(
            {
                "clan_wars_policy": {"mode": "gold_portal"},
                "clan_wars_wins": -4,
                "clan_wars_kills": "12",
                "clan_wars": {"mode": CLAN_WARS_RED_MODE},
            }
        )
        self.assertEqual(
            state["clan_wars_policy"]["mode"], CLAN_WARS_WHITE_MODE
        )
        self.assertEqual(state["clan_wars_wins"], 0)
        self.assertEqual(state["clan_wars_kills"], 12)
        # A session with no opponent cannot be resumed, so it is discarded.
        self.assertEqual(state["clan_wars"], {})

    def test_an_older_save_migrates_without_losing_unrelated_keys(self):
        old = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        old["config_version"] = 82
        old["unrelated_future_key"] = {"keep": True}
        for key in default_clan_wars_state_pure():
            old.pop(key, None)
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["clan_wars"], {})
        self.assertEqual(
            migrated["clan_wars_policy"], {"mode": CLAN_WARS_WHITE_MODE}
        )
        self.assertEqual(migrated["clan_wars_items_destroyed"], 0)
        self.assertEqual(migrated["unrelated_future_key"], {"keep": True})

    def test_an_interrupted_match_survives_a_save_and_load_round_trip(self):
        entered, ok, _ = enter_clan_wars_pure(_player(), CLAN_WARS_RED_MODE)
        self.assertTrue(ok)
        entered, ok, _ = apply_clan_wars_review_pure(
            entered,
            random.Random(RED_DEATH_SEED).random,
            equipment_data=EQUIPMENT_DATA,
        )
        self.assertTrue(ok)
        reloaded = migrate_loaded_data(
            json.loads(json.dumps(entered)), ORE_DATA, ITEM_DEFINITIONS
        )
        self.assertEqual(reloaded["clan_wars"]["mode"], CLAN_WARS_RED_MODE)
        self.assertEqual(reloaded["clan_wars"]["review"], 1)
        self.assertEqual(
            reloaded["activity_session"]["active_id"], CLAN_WARS_ACTIVITY_ID
        )


class ClanWarsCommandTest(unittest.TestCase):
    def test_the_command_router_covers_every_direct_action(self):
        player = _player()
        planned, ok, _ = apply_clan_wars_command_pure(
            player, "set_policy", {"mode": CLAN_WARS_PURPLE_MODE}
        )
        self.assertTrue(ok)
        self.assertEqual(
            planned["clan_wars_policy"]["mode"], CLAN_WARS_PURPLE_MODE
        )

        entered, ok, _ = apply_clan_wars_command_pure(planned, "enter", {})
        self.assertTrue(ok)
        self.assertEqual(entered["clan_wars"]["mode"], CLAN_WARS_PURPLE_MODE)

        escaped, ok, _ = apply_clan_wars_command_pure(
            entered, "teleport_escape", {}
        )
        self.assertTrue(ok)
        self.assertEqual(escaped["clan_wars"], {})

        entered, ok, _ = apply_clan_wars_command_pure(
            planned, "enter", {"mode": CLAN_WARS_RED_MODE}
        )
        self.assertTrue(ok)
        left, ok, _ = apply_clan_wars_command_pure(entered, "leave", {})
        self.assertTrue(ok)
        self.assertEqual(left["clan_wars"], {})

        _, ok, result = apply_clan_wars_command_pure(player, "detonate", {})
        self.assertFalse(ok)
        self.assertIn("Unknown", result["reason"])


class ClanWarsRuntimeIntegrationTest(unittest.TestCase):
    def test_a_selected_match_dispatches_reviews_and_settles_through_the_runtime(self):
        player = _player(levels=70, weapon="Rune scimitar")
        player, ok, _ = enter_clan_wars_pure(player, CLAN_WARS_WHITE_MODE)
        self.assertTrue(ok)
        calls = {
            "errors": [],
            "activity": [],
            "xp": [],
            "saves": 0,
            "deactivated": False,
            "rng": random.Random(WHITE_WIN_SEED).random,
        }
        context = _context(player, calls)
        for _ in range(CLAN_WARS_MAX_REVIEWS):
            self.assertTrue(handle_utility_answer(context))
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], CLAN_WARS_MAX_REVIEWS)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(player["clan_wars_wins"], 1)
        self.assertEqual(player["clan_wars"], {})
        self.assertIn("Free-for-all win", calls["activity"][-1])
        telemetry = player["action_telemetry"]["actions"]
        self.assertEqual(
            telemetry[f"utility:{CLAN_WARS_ACTIVITY_ID}"]["attempts"],
            CLAN_WARS_MAX_REVIEWS,
        )

    def test_the_runtime_records_a_red_death_as_a_dangerous_failure(self):
        player, ok, _ = enter_clan_wars_pure(
            _armoured_player(), CLAN_WARS_RED_MODE
        )
        self.assertTrue(ok)
        calls = {
            "errors": [],
            "activity": [],
            "xp": [],
            "saves": 0,
            "deactivated": False,
            "rng": random.Random(RED_DEATH_SEED).random,
        }
        context = _context(player, calls)
        for _ in range(CLAN_WARS_MAX_REVIEWS):
            handle_utility_answer(context)
            if not player["clan_wars"]:
                break
        self.assertEqual(player["clan_wars_deaths"], 1)
        self.assertEqual(player["combat_grave"], {})
        self.assertEqual(player["death_office"], {})
        self.assertEqual(player["inventory"].get("Lobster", 0), 0)
        self.assertTrue(calls["deactivated"])
        telemetry = player["action_telemetry"]["actions"][
            f"utility:{CLAN_WARS_ACTIVITY_ID}"
        ]
        self.assertEqual(
            telemetry["failure_kinds"]["dangerous_death"],
            1,
        )

    def test_an_unselected_activity_refuses_the_review_and_deactivates(self):
        player = _player()
        calls = {
            "errors": [],
            "activity": [],
            "xp": [],
            "saves": 0,
            "deactivated": False,
            "rng": random.Random(0).random,
        }
        player["current_utility"] = CLAN_WARS_ACTIVITY_ID
        context = _context(player, calls)
        self.assertFalse(handle_utility_answer(context))
        self.assertTrue(calls["deactivated"])
        self.assertIn("Clan Wars unavailable", calls["errors"][0][0])


if __name__ == "__main__":
    unittest.main()
