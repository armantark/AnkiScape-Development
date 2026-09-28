"""runtime_actions_context.py - split out of runtime_actions.py; see that module's header."""

from __future__ import annotations

from dataclasses import dataclass

from typing import Any, Callable, Optional


@dataclass
class RuntimeActionContext:
    player_data: dict[str, Any]
    random_random: Callable[[], float]
    show_error_message: Callable[[str, str], None]
    deactivate_current_skill: Callable[..., None]
    award_skill_exp: Callable[[str, float], float]
    award_hidden_skill_exp: Callable[[str, str, float], None]
    level_up_check: Callable[[str, dict[str, Any]], None]
    check_achievements: Callable[[dict[str, Any]], None]
    save_player_data: Callable[[], None]
    refresh_skill_availability: Callable[[], None]
    show_exp: Callable[[float], None]
    show_activity_gain: Callable[[str], None]
    implemented_exp_keys_snapshot: Callable[[], dict[str, float]]
    show_quest_exp_delta: Callable[[dict[str, float]], None]
    review_action_multiplier: int = 1
    cadence_shadow_enabled: bool = False
    cadence_live_enabled: bool = False
    cadence_forced_opportunity: bool = False
    # Fired once when the Stronghold of Security is finished, so the UI can pop
    # the boot-choice reward dialog. Optional so older call sites keep working.
    prompt_stronghold_reward: Optional[Callable[[], None]] = None
    # Fired when a review is refused because the player is near death with no
    # food and nothing bankable to fetch. The UI asks whether to leave; the
    # handler has already stopped the review either way.
    prompt_near_death: Optional[Callable[[str], None]] = None
    prompt_slayer_completion: Optional[Callable[[int, str], None]] = None
    switch_to_bankstanding: Optional[Callable[..., None]] = None
    select_review_action: Optional[Callable[[str], bool]] = None
    refresh_carried_inventory: Optional[Callable[[], None]] = None
