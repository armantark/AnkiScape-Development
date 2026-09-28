from __future__ import annotations

from ..core.constants import (
    GLORY_GEM_DROP_CHANCE,
    INCIDENTAL_GEM_DROP_CHANCE,
    INCIDENTAL_GEM_DROP_TABLE,
    MINING_BONUS_ITEM_DATA,
    MINING_PICKAXE_DATA,
    WOODCUTTING_AXE_DATA,
)
from ..logic_pure.logic_pure import (
    best_mining_pickaxe_pure,
    best_woodcutting_axe_pure,
    equipment_bonus_state_pure,
)
from ..data.court_cases_data import COURT_CASES_ACTIVITY_ID
from ..logic.court_cases_logic import apply_court_case_review_pure
from ..data.circus_data import CIRCUS_ACTIVITY_ID
from ..logic.circus_logic import apply_circus_review_pure
from ..data.stronghold_player_safety_data import STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID
from ..logic.stronghold_player_safety_logic import apply_stronghold_player_safety_review_pure
from ..data.treasure_trails_data import TREASURE_TRAILS_ACTIVITY_ID
from ..logic.treasure_trails_logic import apply_treasure_trail_review_pure
from ..data.varrock_museum_data import VARROCK_MUSEUM_ACTIVITY_ID
from ..logic.varrock_museum_logic import apply_varrock_museum_review_pure
from ..data.managing_miscellania_data import MANAGING_MISCELLANIA_ACTIVITY_ID
from ..logic.managing_miscellania_logic import (
    apply_managing_miscellania_review_pure,
    managing_miscellania_view_pure,
)
from ..logic.evil_tree_logic import apply_evil_tree_review_pure
from ..data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from ..logic.big_chinchompa_logic import apply_big_chinchompa_review_pure
from ..data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
from ..logic.shooting_star_logic import apply_shooting_star_review_pure
from ..logic.review_strip_logic import record_review_event_pure
from ..data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID
from ..logic.tears_of_guthix_logic import apply_tears_of_guthix_review_pure
from ..data.enchanted_key_data import ENCHANTED_KEY_ACTIVITY_ID
from ..logic.enchanted_key_logic import apply_enchanted_key_review_pure
from ..data.sorceress_garden_data import SORCERESS_GARDEN_ACTIVITY_ID
from ..logic.sorceress_garden_logic import (
    apply_sorceress_garden_review_pure,
    sorceress_garden_view_pure,
)
from ..data.penguin_hide_and_seek_data import PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID
from ..logic.penguin_hide_and_seek_logic import apply_penguin_review_pure
from ..data.vinesweeper_data import VINESWEEPER_ACTIVITY_ID
from ..logic.vinesweeper_logic import apply_vinesweeper_review_pure
from .runtime_actions_shared import (
    _award_action_xp_rewards,
    _record_action,
    _switch_material_failure_to_bankstanding,
)
from .runtime_actions_context import RuntimeActionContext


def _evil_tree_reward_rolls(ctx: RuntimeActionContext) -> tuple[float, ...]:
    """Only the felling answer draws, so nurture and root answers leave the RNG untouched."""
    state = ctx.player_data.get("evil_tree")
    session = state.get("session") if isinstance(state, dict) else None
    if isinstance(session, dict) and session.get("phase") == "fell":
        return tuple(ctx.random_random() for _ in range(4))
    return ()


def _record_evil_tree_phase(
    ctx: RuntimeActionContext,
    phase: str,
    xp: dict,
    outputs: dict,
) -> None:
    if phase == "nurture":
        _record_action(
            ctx,
            "farming",
            "evil_tree_nurture",
            True,
            expected_success_chance=1.0,
            primary_xp=float(xp.get("Farming", 0.0) or 0.0),
        )
    elif phase == "prepare":
        _record_action(
            ctx,
            "woodcutting",
            "evil_tree_roots",
            True,
            expected_success_chance=1.0,
            output_items=outputs,
            primary_xp=float(xp.get("Woodcutting", 0.0) or 0.0),
        )
    elif phase == "fell":
        _record_action(
            ctx,
            "woodcutting",
            "evil_tree_fell",
            True,
            expected_success_chance=1.0,
            output_items=outputs,
            primary_xp=float(xp.get("Woodcutting", 0.0) or 0.0),
        )
        _record_action(
            ctx,
            "firemaking",
            "evil_tree_kindling",
            True,
            expected_success_chance=1.0,
            primary_xp=float(xp.get("Firemaking", 0.0) or 0.0),
        )


def _evil_tree_gain_message(result: dict, phase: str, xp: dict, outputs: dict) -> str:
    xp_text = " · ".join(
        f"+{float(amount):,.6g} {skill_name} XP"
        for skill_name, amount in xp.items()
    )
    if result.get("completed") and result.get("partial"):
        return f"Nurtured {result['tier_name']} · {xp_text} · nurture-only visit complete"
    if result.get("completed"):
        reward_text = ", ".join(
            f"{int(amount):,} {item_name}"
            for item_name, amount in outputs.items()
        )
        return (
            f"Felled {result['tier_name']} · {xp_text} · {reward_text} · "
            f"blessing {int(result.get('blessing_reviews', 0))} reviews"
        )
    if phase == "nurture":
        return f"Nurtured {result['tier_name']} · {xp_text} · next: chop roots"
    return f"Prepared {result['tier_name']} · {xp_text} · next: fell and burn"


def _handle_evil_tree_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    woodcutting_level = int(player_data.get("woodcutting_level", 1) or 1)
    has_hatchet = best_woodcutting_axe_pure(
        woodcutting_level,
        player_data.get("inventory", {}),
        player_data.get("toolbelt", {}),
        WOODCUTTING_AXE_DATA,
    ) is not None
    updated, ok, result = apply_evil_tree_review_pure(
        player_data,
        has_usable_hatchet=has_hatchet,
        reward_rolls=_evil_tree_reward_rolls(ctx),
    )
    if not ok:
        ctx.show_error_message(
            "Evil Tree unavailable",
            str(result.get("reason", "This Evil Tree can no longer be trained.")),
        )
        ctx.deactivate_current_skill()
        return False

    player_data.clear()
    player_data.update(updated)
    phase = str(result.get("phase", ""))
    xp = result.get("xp", {}) or {}
    outputs = result.get("outputs", {}) or {}
    _record_evil_tree_phase(ctx, phase, xp, outputs)

    for skill_name in xp:
        ctx.level_up_check(str(skill_name), player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.show_activity_gain(_evil_tree_gain_message(result, phase, xp, outputs))

    if result.get("completed"):
        _switch_material_failure_to_bankstanding(ctx)
    return True


def _handle_big_chinchompa_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_big_chinchompa_review_pure(
        ctx.player_data,
        circuits=max(1, int(ctx.review_action_multiplier or 1)),
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Big Chinchompa unavailable",
            str(result.get("reason", "No Big Chinchompa event is active.")),
        )
        return False

    ctx.player_data.clear()
    ctx.player_data.update(updated)
    hunter_xp = float(result.get("hunter_xp", 0.0) or 0.0)
    _record_action(
        ctx,
        "utility",
        BIG_CHINCHOMPA_UTILITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=hunter_xp,
        shattered_heart_skill_id="hunter",
    )
    gained = _award_action_xp_rewards(
        ctx,
        ({"skill_id": "hunter", "amount": hunter_xp},),
        "hunter",
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(gained)
    point_text = (
        "point cap reached"
        if result.get("personal_cap_reached")
        else f"+{int(result.get('event_points', 0) or 0)} event points"
    )
    ctx.show_activity_gain(
        f"Released {int(result.get('moths', 0) or 0)} "
        f"{str(result.get('tier_name', 'soporith moth')).lower()}s · "
        f"{point_text} · {float(result.get('fullness_percent', 0.0)):.0f}% full"
    )
    return True


def _end_unminable_star_visit(
    ctx: RuntimeActionContext,
    result: dict,
    mining_xp: float,
) -> None:
    _record_action(
        ctx,
        "mining",
        SHOOTING_STAR_ACTIVITY_ID,
        False,
        expected_success_chance=1.0,
        failure_kind="unminable_layer",
        primary_xp=mining_xp,
    )
    if mining_xp > 0:
        gained = ctx.award_skill_exp("mining_exp", mining_xp)
        ctx.level_up_check("Mining", ctx.player_data)
        ctx.check_achievements(ctx.player_data)
        ctx.show_exp(gained)
    ctx.deactivate_current_skill(
        str(result.get("event_log_text", "Star unminable at your level"))
    )
    ctx.save_player_data()
    ctx.refresh_skill_availability()


def _announce_star_mining(
    ctx: RuntimeActionContext,
    result: dict,
    mining_xp: float,
    dust_added: int,
    gem: str,
) -> None:
    if result.get("tag_only"):
        ctx.show_activity_gain(
            f"First-finder tag · +{mining_xp:,.6g} Mining XP · "
            "bring a pickaxe to mine stardust"
        )
        ctx.deactivate_current_skill()
        return
    parts = [
        f"Mined size {int(result.get('mined_size', 0))} stardust",
        f"+{mining_xp:,.6g} Mining XP",
    ]
    if result.get("tag_xp"):
        parts.append("first-finder tag")
    if dust_added:
        parts.append(
            f"{int(result.get('dust_total', 0))}/200 stardust"
        )
    elif result.get("dust_cap_reached"):
        parts.append("stardust cap reached; XP continues")
    if gem:
        parts.append(f"+1 {gem}")
    if result.get("sprite_released"):
        parts.append("Star sprite released")
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(" · ".join(parts))


def _handle_shooting_star_answer(ctx: RuntimeActionContext) -> bool:
    mining_level = int(ctx.player_data.get("mining_level", 1) or 1)
    pickaxe = best_mining_pickaxe_pure(
        mining_level,
        ctx.player_data.get("inventory", {}),
        ctx.player_data.get("toolbelt", {}),
        MINING_PICKAXE_DATA,
    )
    bonus_state = equipment_bonus_state_pure(
        ctx.player_data.get("equipment", {}) or {},
        MINING_BONUS_ITEM_DATA,
    )
    gem_chance = (
        GLORY_GEM_DROP_CHANCE
        if bonus_state["has_glory"]
        else INCIDENTAL_GEM_DROP_CHANCE
    )
    updated, ok, result = apply_shooting_star_review_pure(
        ctx.player_data,
        has_usable_pickaxe=pickaxe is not None,
        gem_roll=ctx.random_random(),
        gem_pick_roll=ctx.random_random(),
        gem_drop_chance=gem_chance,
        gem_drop_table=INCIDENTAL_GEM_DROP_TABLE,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Shooting Star unavailable",
            str(result.get("reason", "No mineable Shooting Star is active.")),
        )
        return False

    ctx.player_data.clear()
    ctx.player_data.update(updated)
    mining_xp = float(result.get("mining_xp", 0.0) or 0.0)
    if result.get("unminable"):
        _end_unminable_star_visit(ctx, result, mining_xp)
        return True

    outputs: dict[str, int] = {}
    dust_added = int(result.get("dust_added", 0) or 0)
    if dust_added > 0:
        outputs["Stardust"] = dust_added
    gem = str(result.get("gem", "") or "")
    if gem:
        outputs[gem] = outputs.get(gem, 0) + 1
    _record_action(
        ctx,
        "mining",
        SHOOTING_STAR_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        output_items=outputs,
        primary_xp=mining_xp,
    )
    gained = ctx.award_skill_exp("mining_exp", mining_xp)
    ctx.level_up_check("Mining", ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    _announce_star_mining(ctx, result, mining_xp, dust_added, gem)
    return True


def _handle_tears_of_guthix_answer(ctx: RuntimeActionContext) -> bool:
    """One answered card is one collection beat; the multiplier repeats beats."""
    updated, ok, result = apply_tears_of_guthix_review_pure(
        ctx.player_data,
        ctx.random_random,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Tears of Guthix unavailable",
            str(result.get("reason", "Enter Juna's cavern before collecting.")),
        )
        return False
    for _ in range(max(1, int(ctx.review_action_multiplier or 1)) - 1):
        if result.get("completed"):
            break
        updated, repeated_ok, repeated = apply_tears_of_guthix_review_pure(
            updated,
            ctx.random_random,
        )
        if not repeated_ok:
            break
        result = repeated
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        TEARS_OF_GUTHIX_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=total_xp,
    )
    if result.get("reward_skill_name"):
        ctx.level_up_check(str(result["reward_skill_name"]), ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "Tears collected")))
    return True


def _handle_enchanted_key_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_enchanted_key_review_pure(
        ctx.player_data,
        ctx.random_random,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Enchanted key unavailable",
            str(result.get("reason", "Choose a treasure site to search first.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        str(result.get("site_id", ENCHANTED_KEY_ACTIVITY_ID)),
        True,
        expected_success_chance=1.0,
        output_items=(
            {name: int(quantity) for name, quantity in result.get("rewards", ())}
            if result.get("dug")
            else None
        ),
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "You feel the key.")))
    return True


def _handle_sorceress_garden_answer(ctx: RuntimeActionContext) -> bool:
    view = sorceress_garden_view_pure(ctx.player_data)
    harvest = str(view.get("harvest_mode", "fruit"))
    if harvest == "alternate":
        harvest = str(view.get("alternate_next", "fruit"))
    herb_rolls = (
        (ctx.random_random(), ctx.random_random())
        if harvest == "herbs"
        else ()
    )
    updated, result = apply_sorceress_garden_review_pure(
        ctx.player_data,
        herb_rolls,
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Sorceress's Garden locked",
            "Requires " + ", ".join(result.get("locked_reasons", ())),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    farming_xp = float(result.get("farming_xp", 0.0) or 0.0)
    thieving_xp = float(result.get("thieving_xp", 0.0) or 0.0)
    gained = ctx.award_skill_exp("farming_exp", farming_xp)
    ctx.level_up_check("Farming", ctx.player_data)
    if thieving_xp > 0:
        ctx.award_skill_exp("thieving_exp", thieving_xp)
        ctx.level_up_check("Thieving", ctx.player_data)
    _record_action(
        ctx,
        "farming",
        str(result.get("action_id", SORCERESS_GARDEN_ACTIVITY_ID)),
        True,
        expected_success_chance=1.0,
        output_items=dict(result.get("outputs", {}) or {}),
        primary_xp=farming_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Garden trip complete")))
    return True


def _handle_penguin_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_penguin_review_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Penguin Hide and Seek unavailable",
            str(result.get("reason", "Select an unspotted penguin first.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        str(result.get("action_id", PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID)),
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("status", "Penguin spied")))
    return True


def _handle_vinesweeper_answer(ctx: RuntimeActionContext) -> bool:
    operations = max(1, int(ctx.review_action_multiplier or 1))
    updated, result = apply_vinesweeper_review_pure(
        ctx.player_data,
        tuple(ctx.random_random() for _ in range(operations)),
        operations=operations,
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Vinesweeper unavailable",
            str(result.get("reason", "Enter Winkin's Farm before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    hunter_xp = float(result.get("hunter_xp", 0.0) or 0.0)
    gained = 0.0
    if hunter_xp > 0:
        gained = ctx.award_skill_exp("hunter_exp", hunter_xp)
        ctx.level_up_check("Hunter", ctx.player_data)
    completed = int(result.get("completed_operations", 0) or 0)
    if completed:
        _record_action(
            ctx,
            "utility",
            VINESWEEPER_ACTIVITY_ID,
            True,
            expected_success_chance=1.0,
            primary_xp=hunter_xp,
        )
    if result.get("paused"):
        ctx.deactivate_current_skill()
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(
        str(result.get("status", "Vinesweeper operation complete"))
    )
    return True


def _handle_court_cases_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_court_case_review_pure(ctx.player_data)
    if not result.get("allowed"):
        ctx.show_error_message(
            "Court Cases awaiting a choice",
            str(result.get("reason", "Open a court case before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = 0.0
    xp_skill = str(result.get("xp_skill", ""))
    if base_xp > 0 and xp_skill in {"attack", "defense"}:
        gained = ctx.award_skill_exp(f"{xp_skill}_exp", base_xp)
        ctx.level_up_check(
            "Attack" if xp_skill == "attack" else "Defence",
            ctx.player_data,
        )
    _record_action(
        ctx,
        "utility",
        COURT_CASES_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=float(
            result.get("expected_success_chance", 1.0) or 0.0
        ),
        output_items={
            str(item): int(amount)
            for item, amount in dict(result.get("rewards") or {}).items()
        },
        primary_xp=base_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Court case advanced")))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_circus_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_circus_review_pure(
        ctx.player_data,
        (ctx.random_random(),),
    )
    if not result.get("allowed"):
        ctx.show_error_message(
            "Big Top Bonanza unavailable",
            str(result.get("reason", "Choose an available Circus performance.")),
        )
        return False
    for event_text in (result.get("trick_event"), result.get("summary_event")):
        if event_text:
            updated = record_review_event_pure(updated, "activity", str(event_text))
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    skill_id = str(result.get("skill_id", ""))
    skill_rows = {
        "magic": ("magic_exp", "Magic"),
        "ranged": ("ranged_exp", "Ranged"),
        "agility": ("agility_exp", "Agility"),
        "firemaking": ("firemaking_exp", "Firemaking"),
        "thieving": ("thieving_exp", "Thieving"),
    }
    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = 0.0
    if base_xp > 0 and skill_id in skill_rows:
        exp_key, display_name = skill_rows[skill_id]
        gained = ctx.award_skill_exp(exp_key, base_xp)
        ctx.level_up_check(display_name, ctx.player_data)
    _record_action(
        ctx,
        "utility",
        CIRCUS_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=float(
            result.get("expected_success_chance", 0.0) or 0.0
        ),
        output_items={
            str(item): int(amount)
            for item, amount in dict(result.get("outputs") or {}).items()
        },
        primary_xp=base_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Circus performance resolved")))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_varrock_museum_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_varrock_museum_review_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Varrock Museum unavailable",
            str(result.get("reason", "Choose an unfinished museum route.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        VARROCK_MUSEUM_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("status") or "Varrock Museum landmark completed")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_stronghold_player_safety_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_stronghold_player_safety_review_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Stronghold of Player Safety unavailable",
            str(result.get("reason", "Choose an unfinished Stronghold landmark.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("status") or "Stronghold landmark completed")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_managing_miscellania_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_managing_miscellania_review_pure(ctx.player_data)
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Managing Miscellania unavailable",
            str(result.get("reason", "No approval work is available.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = ctx.award_skill_exp("woodcutting_exp", base_xp)
    ctx.level_up_check("Woodcutting", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        MANAGING_MISCELLANIA_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=base_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Kingdom approval increased")))
    if not managing_miscellania_view_pure(ctx.player_data).get("can_train", False):
        ctx.deactivate_current_skill()
    return True


def handle_treasure_trail_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_treasure_trail_review_pure(
        ctx.player_data, ctx.random_random
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Treasure Trails unavailable",
            str(result.get("reason", "Read a clue scroll before following a trail.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    # A blocked emote step is a real period stall, not a completed beat, so it
    # is recorded as a failure rather than silently counted as progress.
    _record_action(
        ctx,
        "utility",
        TREASURE_TRAILS_ACTIVITY_ID,
        not result.get("blocked"),
        expected_success_chance=1.0,
        failure_kind="emote_gear_missing" if result.get("blocked") else None,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("message") or "Treasure Trail step resolved"))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


_handle_evil_tree_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_big_chinchompa_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_shooting_star_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_tears_of_guthix_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_enchanted_key_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_sorceress_garden_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_penguin_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_vinesweeper_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_court_cases_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_circus_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_varrock_museum_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_stronghold_player_safety_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_managing_miscellania_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_treasure_trail_answer.__module__ = f"{__package__}.runtime_actions_activities"
