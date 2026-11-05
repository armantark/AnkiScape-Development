"""Qt-only widgets the Shop tab builds; ui_tab_shop imports them lazily so the
plain lane can still import that module."""

from collections.abc import Callable, Hashable

from aqt.qt import QEvent, QLabel, QListWidget, QListWidgetItem, QSize, QStyledItemDelegate, QStyleOptionViewItem, Qt, QTimer, QTreeView  # type: ignore

from .ui_first_cell_tree import settle_tree

# Side padding of a Shop list row; the row stylesheet and the size hint share it.
ROW_SIDE_PADDING = 7

_TONES = {
    True: ("✓ ", "rgba(76,175,80,0.18)", "#4CAF50"),
    False: ("", "rgba(240,199,94,0.22)", "#f0c75e"),
}

_LOCKED_FLAGS = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


def _humanize_display(value: object, fallback: str = "") -> str:
    text = str(value or fallback).replace("_", " ").strip()
    # Only the first character changes case: backend ids are snake_case but
    # human fallbacks may carry proper nouns that .capitalize() would eat.
    return text[:1].upper() + text[1:]


def _format_shop_price(value, currency_name: str) -> str:
    if value is None:
        return "N/A"
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return "N/A"
    return f"{amount:,} {currency_name}"


def _shop_selector_label_from_result(result: dict) -> str:
    kind = result.get("kind")
    if kind == "stock":
        price = _format_shop_price(result.get("buy_price"), "Coins")
        stock = f"{int(result.get('current_quantity', 0) or 0):,}/{int(result.get('default_quantity', 0) or 0):,}"
        lock = (
            f" · {_humanize_display(result.get('lock_reason'))}"
            if result.get("lock_reason")
            else ""
        )
        # The wall goes before stock and price so a narrow list still shows it.
        return f"{result.get('item_name')} · {result.get('shop_name')}{lock} · Stock {stock} · {price}"
    label = "Service" if kind == "service" else "Vendor"
    lock = (
        f" · {_humanize_display(result.get('lock_reason'))}"
        if result.get("lock_reason")
        else ""
    )
    price = int(result.get("price", 0) or 0)
    cost = (
        "Free"
        if price == 0
        else f"{price:,} {result.get('currency_item_name', 'Coins')}"
    )
    return (
        f"{label}: {result.get('display_name')} · "
        f"{result.get('provider')}{lock} · {cost}"
    )


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
    """Sizes a wrapped list or tree row at the width its text is painted in.

    The stock size hint wraps at a layout width a few pixels wider than the
    painted row and ignores the stylesheet's side padding, so a row that only
    just fits would be elided ("Requires starting The Giant ...") or lose its
    second line instead of wrapping. A tree row is also indented by its depth.
    """

    def __init__(self, parent, side_padding: int = ROW_SIDE_PADDING) -> None:
        super().__init__(parent)
        self._side_padding = side_padding
        if isinstance(parent, QTreeView):
            # A tree keeps the row heights of its first layout, which ran before
            # the tree had its width; a list re-lays out its rows by itself.
            parent.viewport().installEventFilter(self)

    def eventFilter(self, watched, event):  # type: ignore[no-untyped-def]
        if event.type() == QEvent.Type.Resize and event.size().width() != event.oldSize().width():
            self.parent().scheduleDelayedItemsLayout()
            settle_tree(self.parent())
        return False

    def sizeHint(self, option, index):  # type: ignore[no-untyped-def]
        view = self.parent()
        width = view.viewport().width() - 2 * self._side_padding
        if isinstance(view, QTreeView):
            depth, parent = int(view.rootIsDecorated()), index.parent()
            while parent.isValid():
                depth, parent = depth + 1, parent.parent()
            width -= depth * view.indentation()
        painted = QStyleOptionViewItem(option)
        # Qt wraps only inside a valid rect, and a tree asks with a zero height.
        painted.rect.setSize(QSize(width, max(painted.rect.height(), 1)))
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
