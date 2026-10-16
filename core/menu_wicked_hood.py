"""Main-menu Wicked hood commands share the direct-action undo transaction."""

from ..logic.wicked_hood_logic import apply_wicked_hood_command_pure


def apply_wicked_hood_command(addon, action_id, payload):
    payload = dict(payload) if isinstance(payload, dict) else {}
    if action_id == "teleport":
        altar_id = str(payload.get("altar_id", "") or "")
        target_id = next(
            (
                candidate
                for candidate, spec in addon.RUNECRAFTING_DATA.items()
                if spec.get("kind") == "standard"
                and spec.get("altar_id") == altar_id
            ),
            "",
        )
        quest_reasons = addon.quest_unlock_locked_reasons_pure(
            addon._state.player_data,
            "runecrafting",
            target_id,
            addon.QUEST_UNLOCK_RULES,
        )
        if quest_reasons:
            payload["locked_reason"] = str(quest_reasons[0])
    info = {}
    pure_ok = True

    def _change(current):
        nonlocal info, pure_ok
        updated, ok, info = apply_wicked_hood_command_pure(
            addon._capture_player_data_snapshot()["player_data"],
            str(action_id),
            payload,
        )
        pure_ok = bool(ok)
        return updated, ok

    def _after_apply():
        if info.get("feed_xp", 0) > 0:
            addon._award_skill_exp("runecrafting_exp", info["feed_xp"], action_skill_id="runecrafting")
            addon.level_up_check("Runecrafting", addon._state.player_data)
        addon.check_achievements(addon._state.player_data)

    committed = addon.commit_direct_action(_change, after_apply=_after_apply)
    if not pure_ok:
        return {
            "ok": False,
            "message": str(info.get("reason", "That Wicked hood action is unavailable.")),
        }
    if not committed:
        return {"ok": False, "message": "Anki could not create an undo entry."}
    addon._refresh_skill_availability()
    if info.get("message"):
        addon._show_activity_gain(str(info["message"]))
    try:
        addon.update_review_hud(addon._state.player_data, addon._state.current_skill)
    except AttributeError:
        pass
    return {"ok": True, **info}
