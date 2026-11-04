"""Ending a running minigame session before another activity starts.

Start and an "Add to queue" that starts its entry at once both pass through
``leave_running_activity``, so the player meets the same question either way.
"""

from typing import Any, Callable, NamedTuple, Optional, Union

try:
    from aqt.qt import QMessageBox  # type: ignore
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass


class LeaveRule(NamedTuple):
    """One minigame session that switching activities would end, and how to end it."""

    activity_id: str
    running: Callable[[], Any]
    title: str
    question: Union[str, Callable[[], str]]
    command: Optional[Callable[[str, dict], Any]]
    action: str
    unavailable: str
    error_title: str
    error_default: str
    # Why the session cannot be left at all, such as a No Forfeit duel; empty when it can.
    refusal: Optional[Callable[[], str]] = None


def leave_running_activity(parent, show_error_message, rules, activity_id: str) -> bool:
    """Ask before ending each other running session and end it on Yes; False keeps the player there."""
    return all(
        _leave(rule, parent, show_error_message)
        for rule in rules
        if rule.activity_id != activity_id and rule.running()
    )


def _leave(rule: LeaveRule, parent, show_error_message) -> bool:
    """End one running session after the player agrees; False when he declines or it cannot end."""
    refusal = rule.refusal() if rule.refusal is not None else ""
    if refusal:
        show_error_message(rule.error_title, refusal)
        return False
    question = rule.question() if callable(rule.question) else rule.question
    yes, no = QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No
    if QMessageBox.question(parent, rule.title, question, yes | no, no) != yes:
        return False
    result = rule.command(rule.action, {}) if rule.command is not None else {"ok": False, "message": rule.unavailable}
    if not (result or {}).get("ok", False):
        show_error_message(rule.error_title, str((result or {}).get("message", rule.error_default)))
        return False
    return True
