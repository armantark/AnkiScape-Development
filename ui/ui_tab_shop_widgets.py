"""Qt-only widgets the Shop tab builds; ui_tab_shop imports them lazily so the
plain lane can still import that module."""

from collections.abc import Callable, Hashable

from aqt.qt import QLabel, QListWidget, QListWidgetItem, QStyledItemDelegate, QStyleOptionViewItem, Qt, QTimer  # type: ignore

# Side padding of a Shop list row; the row stylesheet and the size hint share it.
ROW_SIDE_PADDING = 7

_TONES = {
    True: ("✓ ", "rgba(76,175,80,0.18)", "#4CAF50"),
    False: ("", "rgba(240,199,94,0.22)", "#f0c75e"),
}

_LOCKED_FLAGS = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


def mark_locked(item: QListWidgetItem, dim_color) -> None:
    """Dim a locked row and make it unselectable (ruling 4.29.5): a dim row alone still opened on click."""
    item.setForeground(dim_color)
    item.setFlags(item.flags() & ~_LOCKED_FLAGS)


def is_openable(item: QListWidgetItem | None) -> bool:
    return item is not None and bool(item.flags() & Qt.ItemFlag.ItemIsEnabled)


def restore_current(selector: QListWidget, item: QListWidgetItem | None) -> None:
    """Re-mark the row that was open before a repopulate; a locked row never is."""
    if not is_openable(item):
        return
    selector.blockSignals(True)
    selector.setCurrentItem(item)
    selector.blockSignals(False)


class WrappedRowDelegate(QStyledItemDelegate):
    """Sizes a wrapped list row at the width its text is painted in.

    The stock size hint wraps at a layout width a few pixels wider than the
    painted row and ignores the stylesheet's side padding, so a row that only
    just fits would be elided ("Requires starting The Giant ...") or lose its
    second line instead of wrapping.
    """

    def sizeHint(self, option, index):  # type: ignore[no-untyped-def]
        painted = QStyleOptionViewItem(option)
        painted.rect.setWidth(self.parent().viewport().width() - 2 * ROW_SIDE_PADDING)
        return super().sizeHint(painted, index)


class ShopResultChip(QLabel):
    """The outcome of a buy, sell or service, right under the control that
    made it, because a confirmation below the fold reads as none at all.

    Green with a check mark for success, amber for a refusal.

    It hides after ``HOLD_MS``, or as soon as ``follow()`` sees that the
    selection it reported on (``context()``) has changed, so a stale
    "Bought ..." never sits under a different shop or row.
    """

    HOLD_MS = 4000

    def __init__(self, object_name: str, context: Callable[[], Hashable]) -> None:
        super().__init__("")
        self.setObjectName(object_name)
        self.setWordWrap(True)
        self.setVisible(False)
        self._context = context
        self._shown_for: Hashable = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_result(self, text: str, ok: bool) -> None:
        mark, background, border = _TONES[ok]
        self.setText(mark + text)
        self.setStyleSheet(
            f"QLabel#{self.objectName()} {{ background: {background}; border: 1px solid {border};"
            " border-radius: 6px; padding: 4px 8px; color: palette(text); font-weight: 600; }"
        )
        self._shown_for = self._context()
        self.setVisible(True)
        self._timer.start(self.HOLD_MS)

    def follow(self) -> None:
        if self._context() != self._shown_for:
            self._timer.stop()
            self.hide()
