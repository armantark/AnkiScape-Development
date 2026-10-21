"""How a combat burst stops and settles: the status tick that can end it before
either side attacks, the equipment wear, drops and experience it banks, the
kill, death and empty-encounter settlement after it, and the Wilderness ambush
that can follow a burst the player survived."""

from ..data.item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES
from ..data.prayer_data import COMBAT_PRAYERS_BY_ID
from ..logic.inventory_pure import DEFAULT_LOOT_VALUE_THRESHOLD, carried_fold_gains_pure, filter_loot_pure
from .logic_pure_combat_model import (
    _combat_apply_triple_charm_reward,
    _combat_roll_drops,
    _record_combat_observed_drops_pure,
    combat_observed_drop_item_names_pure,
)
from .logic_pure_urns import resolve_prayer_kill_effects_pure
from ..data.equipment_condition_data import EQUIPMENT_CONDITION_DATA
from ..logic.pace.danger_stops import low_lifepoints_without_food_pure
from ..logic.equipment_instance_logic import advance_equipped_condition_pure
from ..logic.warriors_guild_logic import (
    apply_warriors_guild_cyclops_kills_pure,
    apply_warriors_guild_cyclossus_kills_pure,
    sanitize_warriors_guild_state_pure,
)
from .logic_pure_combat_food import _combat_consume_auto_food
from .logic_pure_combat_model import _combat_apply_pvm_death, _combat_apply_wilderness_ambush
from .logic_pure_combat_specials import _combat_death_prayer_damage
from .logic_pure_combat_supplies import (
    _combat_advance_status_effects,
    _combat_consume_antipoison_if_needed,
    _combat_should_auto_flee,
    _combat_bank_run_needed,
    _combat_void_shifter_escape_ready,
)
from .logic_pure_state import COMBAT_PVP_DEATH_KEPT_ITEMS, _non_negative_int, _positive_int


def _combat_advance_status_tick(
    data,
    player_lp,
    max_player_lp,
    rng,
    potions_used,
    food_used,
    status_damage,
    status_expired,
):
    """Advance status effects by one tick, eating after status damage. Returns
    the player's lifepoints and why the burst stops before either side attacks:
    "died", "void_shifter", "auto_flee" or ""."""
    potion_event = _combat_consume_antipoison_if_needed(data)
    if potion_event:
        potions_used.append(potion_event)
    status_result = _combat_advance_status_effects(data, 1, player_lp, max_player_lp)
    player_lp = _non_negative_int(data.get("combat_lifepoints", player_lp), player_lp)
    for effect_name, amount in (status_result.get("damage", {}) or {}).items():
        status_damage[effect_name] = _non_negative_int(status_damage.get(effect_name, 0), 0) + _non_negative_int(amount, 0)
    status_expired.extend(status_result.get("expired", ()) or ())
    if status_result.get("died"):
        return player_lp, "died"
    if status_result.get("damage"):
        player_lp, food_event = _combat_consume_auto_food(data, player_lp, max_player_lp, rng)
        if food_event:
            food_used.append(food_event)
        if _combat_void_shifter_escape_ready(data, player_lp, max_player_lp):
            return player_lp, "void_shifter"
    if _combat_should_auto_flee(data, player_lp, max_player_lp):
        return player_lp, "auto_flee"
    return player_lp, ""


def _combat_drop_ownership_view(data, pending_drops):
    if not pending_drops:
        return data
    ownership_view = dict(data)
    inventory = dict(data.get("inventory", {}) or {})
    for item_name, amount in pending_drops.items():
        inventory[item_name] = _non_negative_int(
            inventory.get(item_name, 0), 0
        ) + _non_negative_int(amount, 0)
    ownership_view["inventory"] = inventory
    return ownership_view


def _combat_pending_bank_view(data, target_id, drops, observed_before):
    """Project kept pending loot into the pack without settling any rewards."""
    overrides = dict(data.get("loot_overrides") or {})
    for item in set(combat_observed_drop_item_names_pure(data, target_id)) - observed_before:
        overrides.setdefault(item, "keep")
    kept, _left = filter_loot_pure(
        drops, ITEM_VALUES, data.get("loot_value_threshold", DEFAULT_LOOT_VALUE_THRESHOLD),
        STACKABLE_ITEM_NAMES, overrides,
    )
    view = dict(_combat_drop_ownership_view(data, kept))
    carried = dict(data.get("carried_inventory") or {})
    carried[target_id] = carried_fold_gains_pure(carried.get(target_id), kept, STACKABLE_ITEM_NAMES)
    view["carried_inventory"] = carried
    return view


def _combat_collect_guild_kill_rewards(data, target_id, rng, pending_drops, guild_rewards):
    if target_id not in {"cyclops", "cyclossus"}:
        return {}
    ownership = _combat_drop_ownership_view(data, pending_drops)
    if target_id == "cyclops":
        rewarded, event = apply_warriors_guild_cyclops_kills_pure(ownership, 1, rng)
        guild_rewards["cyclossus_spawned"] = bool(
            guild_rewards.get("cyclossus_spawned") or event["cyclossus_spawned"]
        )
        guild_rewards["chance"] = event["chance"]
        guild_rewards["cyclossus_chance"] = event["cyclossus_chance"]
    else:
        rewarded, event = apply_warriors_guild_cyclossus_kills_pure(ownership, 1)
        guild_rewards["kills"] = guild_rewards.get("kills", 0) + 1
        guild_rewards["cleared"] = event["cleared"]
    data["warriors_guild"] = rewarded["warriors_guild"]
    defender_drops = event.get("drops", {})
    recorded_drops = guild_rewards.setdefault("drops", {})
    overrides = dict(data.get("loot_overrides") or {})
    for item, amount in defender_drops.items():
        recorded_drops[item] = recorded_drops.get(item, 0) + amount
        overrides[item] = "keep"
    data["loot_overrides"] = overrides
    drops = dict(defender_drops)
    if sanitize_warriors_guild_state_pure(data.get("warriors_guild"))["payment_mode"] == "multi":
        drops["Big bones"] = drops.get("Big bones", 0) + 1
    return drops


def _combat_settle_kill_rewards(data, enemy, target_id, rng, drops, xp_rewards, guild_rewards):
    rolled_drops, refused_clue = _combat_roll_drops(
        enemy,
        rng,
        _combat_drop_ownership_view(data, drops),
        include_clue_refusal=True,
    )
    kill_drops = _combat_apply_triple_charm_reward(data, rolled_drops)
    _record_combat_observed_drops_pure(data, target_id, kill_drops)
    data, kill_drops, passive_prayer_xp, prayer_ticks, _prayer_effects = resolve_prayer_kill_effects_pure(
        data,
        target_id,
        kill_drops,
        bool(data.get("combat_auto_prayer_training")),
    )
    if passive_prayer_xp > 0:
        xp_rewards["prayer_exp"] = float(xp_rewards.get("prayer_exp", 0.0) or 0.0) + passive_prayer_xp
    # Every item source joins this bundle before the kill's continuation check.
    guild_drops = _combat_collect_guild_kill_rewards(data, target_id, rng, drops, guild_rewards)
    for item, amount in guild_drops.items():
        kill_drops[item] = kill_drops.get(item, 0) + amount
    for drop_name, drop_amount in kill_drops.items():
        drops[drop_name] = _non_negative_int(drops.get(drop_name, 0), 0) + _non_negative_int(drop_amount, 0)
    return data, refused_clue, prayer_ticks


def _combat_bank_burst_rewards(data, ticks_elapsed, drops, xp_rewards):
    """Wear the equipped items for the ticks the burst ran, then bank its drops
    and experience. Returns the player data and the equipment wear events."""
    data, condition_events = advance_equipped_condition_pure(
        data, ticks_elapsed, EQUIPMENT_CONDITION_DATA
    )
    inventory = data.get("inventory", {}) or {}
    for item_name, amount in drops.items():
        inventory[item_name] = inventory.get(item_name, 0) + amount
    data["inventory"] = inventory
    for exp_key, amount in xp_rewards.items():
        data[exp_key] = data.get(exp_key, 0.0) + amount
    return data, condition_events


def _combat_settle_burst_outcome(
    data,
    target_id,
    kills,
    died,
    fled,
    player_lp,
    max_player_lp,
    enemy_lp,
    enemy_max_lp,
    selected_prayers,
    finisher,
    rng,
    *,
    live_cadence,
    safe_death,
    no_grave,
    enemy,
):
    """Record the burst's kills, then settle a death or drop an encounter that
    has nothing to carry. Returns the player's lifepoints, the death-prayer
    damage dealt to the enemy, and whether the caller carries the encounter."""
    # Chaining means a single burst can defeat several enemies and still end in
    # a partial survivor or a death, so kills, death, and the carried encounter
    # are independent rather than mutually exclusive branches.
    if kills > 0:
        kill_counts = dict(data.get("combat_kill_counts", {}) or {})
        kill_counts[target_id] = _positive_int(kill_counts.get(target_id, 0), 0) + kills
        data["combat_kill_counts"] = kill_counts
    if not died:
        # No partial progress to carry: the player fled, nothing was fought, or the
        # burst ended right after a kill respawned a fresh full-LP enemy.
        if fled or enemy_lp <= 0 or (enemy_lp >= enemy_max_lp and not live_cadence):
            data["combat_encounter"] = {}
            return player_lp, 0, False
        return player_lp, 0, True
    death_burst = 0
    if "wrath" in selected_prayers or "retribution" in selected_prayers:
        # Death prayers cap with allow_automatic=False, so they never count as
        # an automatic finisher.
        death_burst, _automatic_finisher = _combat_death_prayer_damage(
            data, selected_prayers, finisher, enemy_lp, rng
        )
    if safe_death:
        data["combat_encounter"] = {}
        data["combat_status_effects"] = {}
        return max_player_lp, death_burst, False
    kept_items = enemy.get("pvp_death_kept_items", COMBAT_PVP_DEATH_KEPT_ITEMS)
    player_lp = _combat_apply_pvm_death(
        data, max_player_lp, no_grave=no_grave, kept_items=kept_items
    )
    return player_lp, death_burst, False


def _combat_settle_wilderness_ambush(
    data,
    enemy,
    player_lp,
    max_player_lp,
    rng,
    equipment_risk,
    food_used,
):
    """Roll the enemy's Wilderness ambush. Returns the ambush record, the
    player's lifepoints and whether the ambush killed them."""
    ambush = _combat_apply_wilderness_ambush(
        data, enemy, player_lp, max_player_lp, rng, equipment_risk
    )
    if not (ambush and ambush.get("triggered")):
        return ambush, player_lp, False
    food_event = ambush.get("food_used")
    if food_event:
        food_used.append(food_event)
    if ambush.get("died"):
        return ambush, max_player_lp, True
    return ambush, _non_negative_int(ambush.get("lifepoints_after", player_lp), player_lp), False


def _combat_tick_stop_reason(data, live_cadence, lifepoints, maximum, prayer_points, prayers, poison_before, requested_prayer_uptime):
    if not live_cadence:
        return ""
    if low_lifepoints_without_food_pure(data, lifepoints, maximum):
        return "fled" if data.get("combat_auto_flee", True) else "low_lp_no_food"
    if not poison_before and (data.get("combat_status_effects") or {}).get("poison"):
        return "poison_started"
    if prayer_points <= 0 and requested_prayer_uptime > 0 and any(COMBAT_PRAYERS_BY_ID[prayer].drain > 0 for prayer in prayers):
        return "prayer_empty"
    return ""


def _combat_result_stop_reason(reason, died, fled, familiar_escape, out_of_ammo, out_of_runes, live_cadence):
    if reason:
        return reason
    stops = (
        (out_of_ammo, "out_of_ammo"), (out_of_runes, "out_of_runes"),
        (familiar_escape, "void_shifter"), (died and live_cadence, "died"),
        (fled, "fled" if live_cadence else "auto_flee"),
    )
    return next((name for stopped, name in stops if stopped), "")


def _combat_kill_boundary_stop(data, live_cadence, kills, limit, allow_bank_run, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data, lifepoints, maximum, prayer_points, prayers, poison_before, died, pending_drops, observed_before, requested_prayer_uptime):
    """Settle a kill's danger, task and bank boundaries; return reason and flee."""
    if not live_cadence:
        return "", False
    if died:
        return "died", False
    danger = _combat_tick_stop_reason(data, live_cadence, lifepoints, maximum, prayer_points, prayers, poison_before, requested_prayer_uptime)
    if danger:
        return danger, danger == "fled"
    if limit is not None and kills >= limit:
        return "slayer_task_complete", False
    if allow_bank_run and _combat_bank_run_needed(_combat_pending_bank_view(data, target_id, pending_drops, observed_before), target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data):
        return "bank_trip", False
    return "", False
