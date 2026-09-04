"""Test package and offscreen Qt safety harness for AnkiScape."""

from contextlib import contextmanager
import os
from unittest.mock import patch


_MODAL_ALLOW_DEPTH = 0
_MODAL_PATCHERS = []


def _guard_modal(name, original):
    def _call(*args, **kwargs):
        if _MODAL_ALLOW_DEPTH:
            return original(*args, **kwargs)
        raise AssertionError(
            f"{name} opened a modal in the offscreen Qt test lane; "
            "defer it until after the tested action completes"
        )

    return _call


def install_offscreen_modal_guard() -> None:
    if os.environ.get("QT_QPA_PLATFORM") != "offscreen" or _MODAL_PATCHERS:
        return
    try:
        from aqt.qt import QDialog, QMessageBox  # type: ignore
    except ImportError:
        return

    for owner, name in (
        (QDialog, "exec"),
        (QMessageBox, "information"),
        (QMessageBox, "warning"),
        (QMessageBox, "critical"),
        (QMessageBox, "question"),
    ):
        original = getattr(owner, name)
        patcher = patch.object(
            owner,
            name,
            _guard_modal(f"{owner.__name__}.{name}", original),
        )
        patcher.start()
        _MODAL_PATCHERS.append(patcher)


@contextmanager
def allow_modal_dialogs():
    """Permit guarded modals while a test explicitly closes each dialog."""
    global _MODAL_ALLOW_DEPTH
    _MODAL_ALLOW_DEPTH += 1
    try:
        yield
    finally:
        _MODAL_ALLOW_DEPTH -= 1


install_offscreen_modal_guard()
