"""ui_menu_ctx.py - the shared context the main menu hands to its tab modules.

The expensive main-menu tabs (Shop, Quests, Achievements) are built on first
show instead of on open. Their builders live in ``ui_tab_*.py`` and receive one
of these objects instead of closing over ``show_main_menu``'s locals.

``refreshers`` is how the tabs reach each other. A key is registered when the
owning surface is built, so ``refresh(key)`` on a tab that nobody has opened
yet is a no-op. That is safe rather than lossy because every builder derives
its whole rendered state from ``player_data`` (plus ``selection`` and persisted
config) at build time, so a skipped refresh is deferred work, not lost
information. Two rules keep that true:

1. Refreshers take no data arguments.
2. Anything a callback wants an unbuilt tab to show must be written into
   ``player_data`` or ``selection`` first, then the refresh fired.
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class MainMenuCtx:
    player_data: dict
    dialog: Any
    # ``show_main_menu``'s mutable selection dict (category / skill / active).
    selection: dict
    # The Skills-hub red warning label, shared with Quests.
    warn_label: Any
    on_save_skill: Callable[[str], Any]
    on_check_achievements: Optional[Callable[[dict], Any]] = None
    on_save_player_data: Optional[Callable[[], Any]] = None
    on_set_quest: Optional[Callable[[str], Any]] = None
    on_set_quest_route_choice: Optional[Callable[[str, str], Any]] = None
    # Skill activity commands the Shop tab's reward-shop surfaces relay
    # (Brimhaven ticket redemptions, Agile claims, Pyramid top sales, the
    # Agility cape). The tab forwards payloads unchanged; all rules live in
    # the owning skill's logic.
    on_agility_command: Optional[Callable[[str, dict], Any]] = None
    refreshers: dict = field(default_factory=dict)

    def refresh(self, key: str) -> None:
        fn = self.refreshers.get(key)
        if fn is not None:
            fn()
