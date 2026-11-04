"""Fixed play-time costs for Combat travel and recovery."""

from ..agility_travel import agility_travel_profile_pure, apply_run_energy_credit_pure

# PLACEHOLDER(combat.bank_trip_ticks): owner-set estimate, no period trip duration.
COMBAT_BANK_RUN_TICKS = 100
COMBAT_REST_TICKS = 180
COMBAT_GRAVE_WALK_TICKS = 300


def combat_bank_trip_ticks_pure(data, target_id):
    carried = dict((data.get("carried_inventory", {}).get(target_id) or {}))
    for supplies in (data.get("combat_supply_loadout") or {}).values():
        if isinstance(supplies, dict):
            for item, amount in supplies.items():
                carried[item] = carried.get(item, 0) + amount
    profile = agility_travel_profile_pure(
        "combat", target_id, data.get("agility_level", 1),
        carried, data.get("equipment", {}),
    )
    profile, used = apply_run_energy_credit_pure(profile, data.get("agility_run_energy_credit_pct", 0))
    if used:
        data["agility_run_energy_credit_pct"] = 0
    # Tick resolution is deterministic: trips do not perturb combat's RNG stream.
    return round(COMBAT_BANK_RUN_TICKS * profile.adjusted_reviews)


def advance_combat_rest_pure(data, max_lp, ticks, rapid_heal=1.0):
    current = max(0, int(data.get("combat_lifepoints", max_lp)))
    remaining = max(0, int(data.get("combat_rest_ticks_remaining", COMBAT_REST_TICKS)))
    if "combat_rest_reviews" in data:
        remaining = ticks
    resting = min(ticks, remaining)
    missing = max(0, max_lp - current)
    heal = -(-missing * resting // remaining) if remaining else 0
    natural_ticks = int(data.get("combat_natural_recovery_ticks", 0)) + ticks - resting
    natural_heal, residual = divmod(natural_ticks, 10)
    heal += int(natural_heal * max(1.0, rapid_heal))
    data["combat_natural_recovery_ticks"] = residual
    data["combat_lifepoints"] = min(max_lp, current + heal) if current <= max_lp else max(max_lp, current - 100)
    data["combat_rest_ticks_remaining"] = remaining - resting
    data.pop("combat_rest_reviews", None)
