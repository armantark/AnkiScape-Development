"""Test package and offscreen Qt safety harness for AnkiScape."""

from contextlib import contextmanager
import os
from unittest.mock import patch


_MODAL_PATCHERS = []
# The allow depth lives on QDialog itself, not in this module: pytest can
# import the test package twice, and both copies must see one counter.
_ALLOW_ATTR = "_ankiscape_modal_allow_depth"


def _guard_modal(name, original, owner):
    def _call(*args, **kwargs):
        if getattr(owner, _ALLOW_ATTR, 0):
            return original(*args, **kwargs)
        raise AssertionError(
            f"{name} opened a modal in the offscreen Qt test lane; "
            "defer it until after the tested action completes"
        )

    _call._ankiscape_modal_guard = True
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
        if getattr(original, "_ankiscape_modal_guard", False):
            continue
        patcher = patch.object(
            owner,
            name,
            _guard_modal(f"{owner.__name__}.{name}", original, QDialog),
        )
        patcher.start()
        _MODAL_PATCHERS.append(patcher)


@contextmanager
def allow_modal_dialogs():
    """Permit guarded modals while a test explicitly closes each dialog."""
    from aqt.qt import QDialog  # type: ignore

    setattr(QDialog, _ALLOW_ATTR, getattr(QDialog, _ALLOW_ATTR, 0) + 1)
    try:
        yield
    finally:
        setattr(QDialog, _ALLOW_ATTR, getattr(QDialog, _ALLOW_ATTR, 0) - 1)


install_offscreen_modal_guard()
