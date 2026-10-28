"""Ancient Effigies feature: controller, profile lifecycle and Tools action.

The controller works on the add-on's live save through the root module's
``commit_direct_action`` seam, so every inspection, investigation and lamp use
is one whole-state Undo step. The root module is the already loaded package
named by ``core.hooks``; this module never imports it.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Mapping
from typing import Any, NamedTuple

from ..data.ancient_effigies.catalog import LAMP_SKILL_IDS
from ..logic.ancient_effigies import actions, view


ACTION_TITLE = "AnkiScape Ancient Effigies…"
ACTION_OBJECT_NAME = "ancientEffigiesAction"
UNDO_UNAVAILABLE = "Anki could not create an undo entry, so nothing changed."


class ActionResult(NamedTuple):
    ok: bool
    message: str
    info: Mapping[str, Any]


class AncientEffigiesController:
    """Reads live ownership and routes every change through the Undo seam."""

    lamp_skill_ids = LAMP_SKILL_IDS

    def __init__(self, package_name: str) -> None:
        self.package_name = package_name
        self.window = None
        self.action = None

    def addon(self):
        return sys.modules[self.package_name]

    def player_data(self) -> dict[str, Any]:
        return self.addon()._state.player_data

    def rows(self):
        return view.effigy_rows_pure(self.player_data())

    def detail(self, instance_id: str):
        return view.effigy_detail_pure(self.player_data(), instance_id)

    def lamp_confirmation(self, skill_id: str):
        return view.lamp_confirmation_pure(self.player_data(), skill_id)

    def inspect(self, instance_id: str) -> ActionResult:
        """Reveal a request once; a copy already revealed is only read."""
        _preview, ok, info = actions.inspect_effigy_pure(self.player_data(), instance_id)
        if not ok or not info.get("changed"):
            return ActionResult(ok, str(info.get("message", "")), info)
        return self._commit(lambda current: actions.inspect_effigy_pure(current, instance_id))

    def investigate(self, token: Mapping[str, Any], skill_id: str) -> ActionResult:
        return self._commit(
            lambda current: actions.investigate_effigy_pure(current, token, skill_id),
            reward=True,
        )

    def redeem_lamp(self, token: Mapping[str, Any], skill_id: str) -> ActionResult:
        return self._commit(
            lambda current: actions.redeem_lamp_pure(current, token, skill_id),
            reward=True,
        )

    def destroy_lamp(self, token: Mapping[str, Any]) -> ActionResult:
        return self._commit(lambda current: actions.destroy_lamp_pure(current, token))

    def _reward_feedback(self) -> Callable[[], None]:
        """Level-ups, named XP feedback and achievements, as a claimed reward gets."""
        addon = self.addon()
        exp_before = addon._implemented_exp_keys_snapshot()

        def after_apply() -> None:
            addon._show_quest_exp_delta(exp_before)
            addon.check_achievements(addon._state.player_data)

        return after_apply

    def _commit(self, reducer, *, reward: bool = False) -> ActionResult:
        addon = self.addon()
        outcome: dict[str, Any] = {"ok": False, "info": {}}

        def apply_change(current):
            updated, ok, info = reducer(current)
            outcome.update(ok=ok, info=info)
            return updated, ok

        after_apply = self._reward_feedback() if reward else None
        committed = addon.commit_direct_action(apply_change, after_apply=after_apply)
        info = outcome["info"]
        if not committed:
            return ActionResult(False, UNDO_UNAVAILABLE if outcome["ok"] else str(info.get("message", "")), info)
        if reward:
            self._refresh_reward_surfaces(addon)
        return ActionResult(True, str(info.get("message", "")), info)

    @staticmethod
    def _refresh_reward_surfaces(addon) -> None:
        try:
            addon._refresh_skill_availability()
            addon.update_review_hud(addon._state.player_data, addon._state.current_skill)
        except Exception:
            pass

    def open_window(self) -> None:
        from ..ui.ancient_effigies import AncientEffigiesWindow

        if self.window is None:
            self.window = AncientEffigiesWindow(self, parent=self.addon().mw)
        self.window.refresh()
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def window_closed(self, window) -> None:
        if self.window is window:
            self.window = None

    def close_window(self) -> None:
        window, self.window = self.window, None
        if window is not None:
            try:
                window.close()
            except RuntimeError:
                pass

    def _remove_action(self, menu) -> None:
        for existing in list(menu.actions()):
            if existing.objectName() == ACTION_OBJECT_NAME:
                menu.removeAction(existing)
        self.action = None

    def on_profile_loaded(self) -> None:
        """Add the one Tools action, replacing any left by an earlier load."""
        self.close_window()
        menu = self.addon().mw.form.menuTools
        self._remove_action(menu)
        action = menu.addAction(ACTION_TITLE)
        action.setObjectName(ACTION_OBJECT_NAME)
        action.triggered.connect(lambda _checked=False: self.open_window())
        self.action = action

    def on_profile_will_close(self) -> None:
        self.close_window()
        try:
            self._remove_action(self.addon().mw.form.menuTools)
        except (AttributeError, KeyError, RuntimeError):
            self.action = None


_CONTROLLERS: dict[str, AncientEffigiesController] = {}


def controller_for(package_name: str) -> AncientEffigiesController:
    if package_name not in _CONTROLLERS:
        _CONTROLLERS[package_name] = AncientEffigiesController(package_name)
    return _CONTROLLERS[package_name]


def register_profile_hooks(package_name: str, add_hook, gui_hooks) -> None:
    """Register the profile initializer and close handler, once per package.

    Called by ``core.hooks.register_hooks`` only when Anki is available. The
    same bound callbacks are passed every time, so Anki's de-duplicating
    ``addHook`` and the remove-then-append below keep registration idempotent.
    """
    controller = controller_for(package_name)
    try:
        add_hook("profileLoaded", controller.on_profile_loaded)
    except Exception:
        pass
    try:
        closing = gui_hooks.profile_will_close
        if controller.on_profile_will_close in closing:
            closing.remove(controller.on_profile_will_close)
        closing.append(controller.on_profile_will_close)
    except Exception:
        pass
