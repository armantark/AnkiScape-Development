# hooks.py - centralized hook registration for AnkiScape
from __future__ import annotations
from typing import Callable, Dict, List, Optional, TypedDict

try:
    from aqt import gui_hooks  # type: ignore
    from anki.hooks import addHook, wrap  # type: ignore
    from aqt.reviewer import Reviewer  # type: ignore
    HAS_ANKI = True
except Exception:
    gui_hooks = None  # type: ignore
    addHook = None  # type: ignore
    wrap = None  # type: ignore
    Reviewer = None  # type: ignore
    HAS_ANKI = False


class HookCallbacks(TypedDict, total=False):
    profile_loaded: List[Callable]
    reviewer_question: List[Callable]
    reviewer_answer: List[Callable]
    answer_wrapper: Callable


_REGISTERED = False


def build_registration_plan(callbacks: HookCallbacks) -> Dict[str, int]:
    """Pure helper: return counts of what would be registered."""
    return {
        "profileLoaded": len(callbacks.get("profile_loaded", [])),
        "reviewer_did_show_question": len(callbacks.get("reviewer_question", [])),
        "reviewer_did_show_answer": len(callbacks.get("reviewer_answer", [])),
        "wrap_reviewer_answerCard": 1 if callbacks.get("answer_wrapper") else 0,
    }


def register_hooks(callbacks: HookCallbacks, *, dry_run: bool = False) -> Dict[str, int]:
    """Register hooks with Anki if available; otherwise return the plan.
    Idempotent: repeated calls after a successful registration will no-op.
    """
    global _REGISTERED
    plan = build_registration_plan(callbacks)

    if dry_run or not HAS_ANKI:
        return plan
    if _REGISTERED:
        return plan

    # profileLoaded hooks
    for cb in callbacks.get("profile_loaded", []):
        try:
            addHook("profileLoaded", cb)
        except Exception:
            pass

    # reviewer show question
    for cb in callbacks.get("reviewer_question", []):
        try:
            gui_hooks.reviewer_did_show_question.append(cb)  # type: ignore[attr-defined]
        except Exception:
            pass

    # reviewer show answer
    for cb in callbacks.get("reviewer_answer", []):
        try:
            gui_hooks.reviewer_did_show_answer.append(cb)  # type: ignore[attr-defined]
        except Exception:
            pass

    # wrap answer
    answer_wrapper = callbacks.get("answer_wrapper")
    if answer_wrapper:
        try:
            Reviewer._answerCard = wrap(Reviewer._answerCard, answer_wrapper, "around")  # type: ignore[attr-defined]
        except Exception:
            pass

    _REGISTERED = True
    return plan
