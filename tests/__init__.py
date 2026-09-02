"""Test package and offscreen Qt safety harness for AnkiScape."""

from contextlib import contextmanager
import os
from unittest.mock import patch


_MODAL_PATCHERS = []


def _reject_modal(name):
    def _raise(*_args, **_kwargs):
        raise AssertionError(
            f"{name} opened a modal in the offscreen Qt test lane; "
            "defer it until after the tested action completes"
        )

    return _raise


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
        patcher = patch.object(
            owner,
            name,
            _reject_modal(f"{owner.__name__}.{name}"),
        )
        patcher.start()
        _MODAL_PATCHERS.append(patcher)


@contextmanager
def allow_modal_dialogs():
    """Restore modal entry points for tests that explicitly close each dialog."""
    for patcher in reversed(_MODAL_PATCHERS):
        patcher.stop()
    try:
        yield
    finally:
        for patcher in _MODAL_PATCHERS:
            patcher.start()


install_offscreen_modal_guard()
