"""Layouts and controls that keep their text whole at the 720 px minimum dialog width.

A QHBoxLayout squeezes labels and buttons below their text width; these wrap
the row instead, and WrappingCheckBox wraps its own text.

None of them uses heightForWidth: a vertical QBoxLayout treats such an item as
rigid, which would stop the flexible list beside them from giving up height.
Each remembers the width it was last given and sizes itself for that width, so
a width change settles after one extra layout pass.

guard_wheel keeps the mouse wheel from changing number boxes and drop-down
lists in an AnkiScape window, so the wheel scrolls the page instead.
"""

from aqt.qt import (  # type: ignore
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QEvent,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QModelIndex,
    QObject,
    QPointF,
    QRect,
    QScrollArea,
    QSize,
    QSizePolicy,
    QStyle,
    QStyleOptionButton,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QStylePainter,
    Qt,
    QTimer,
    QToolTip,
    QVBoxLayout,
    QWheelEvent,
    QWidget,
)


class _RowLayout(QLayout):
    """Item storage and QLayout plumbing; subclasses place the visible items for a width."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._width = None

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def _shown(self):
        return [item for item in self._items if not item.isEmpty()]

    def _gap(self):
        return max(self.spacing(), 0)

    def _place(self, width):
        """(item, rect) for each visible item laid out in `width`, from the origin."""
        raise NotImplementedError

    def _size(self, width, height_width):
        """`width` wide, as tall as the items stack when laid out `height_width` wide."""
        margins = self.contentsMargins()
        placed = self._place(height_width)
        height = max((rect.bottom() + 1 for _item, rect in placed), default=0)
        return QSize(
            width + margins.left() + margins.right(),
            height + margins.top() + margins.bottom(),
        )

    def setGeometry(self, rect):
        super().setGeometry(rect)
        inner = self.contentsRect()
        for item, placed in self._place(inner.width()):
            item.setGeometry(placed.translated(inner.topLeft()))
        if inner.width() != self._width:
            self._width = inner.width()
            self.invalidate()

    def sizeHint(self):
        items = self._shown()
        wide = sum(item.sizeHint().width() for item in items) + self._gap() * max(len(items) - 1, 0)
        return self._size(wide, wide if self._width is None else min(self._width, wide))

    def minimumSize(self):
        floor = max((item.minimumSize().width() for item in self._shown()), default=0)
        return self._size(floor, floor if self._width is None else max(self._width, floor))


def _run_width(items, gap):
    return sum(item.sizeHint().width() for item in items) + gap * max(len(items) - 1, 0)


def _wrap_rows(items, width, gap):
    """Greedy rows of `items`, each row at most `width` wide unless one item alone is wider."""
    rows = [[]]
    for item in items:
        if rows[-1] and _run_width([*rows[-1], item], gap) > width:
            rows.append([])
        rows[-1].append(item)
    return rows


class FlowLayout(_RowLayout):
    """Items left to right, each dropping to the next row when it no longer fits.

    With `fill`, each row's spare width is shared out so rows still span the
    width, as the grid columns did before they could wrap.
    """

    def __init__(self, parent=None, fill=False):
        super().__init__(parent)
        self._fill = fill

    def _place(self, width):
        gap, placed, y = self._gap(), [], 0
        for row in _wrap_rows(self._shown(), width, gap):
            spare = width - _run_width(row, gap)
            extra = spare // len(row) if self._fill and spare > 0 else 0
            x = 0
            for item in row:
                hint = item.sizeHint()
                placed.append((item, QRect(x, y, hint.width() + extra, hint.height())))
                x += hint.width() + extra + gap
            y += max(item.sizeHint().height() for item in row) + gap
        return placed


def _tallest(items):
    return max((item.sizeHint().height() for item in items), default=0)


def _place_run(row, x, y, band, gap):
    """`row` left to right from `x`, each item centred vertically in a band `band` tall at `y`."""
    placed = []
    for item in row:
        hint = item.sizeHint()
        placed.append((item, QRect(x, y + (band - hint.height()) // 2, hint.width(), hint.height())))
        x += hint.width() + gap
    return placed


class LeadRowLayout(_RowLayout):
    """One widget (the lead) takes the spare width; the widgets after it sit at the right edge.

    Widgets before the lead stay left of it. When the lead's minimum width and
    the trailing widgets cannot share a row, the trailing widgets drop below
    in right-aligned rows of their own.
    """

    def __init__(self, parent=None, lead=0):
        super().__init__(parent)
        self._lead = lead

    def _place(self, width):
        items = self._shown()
        if not items:
            return []
        gap = self._gap()
        lead_index = min(self._lead, len(items) - 1)
        before, lead, trailing = items[:lead_index], items[lead_index], items[lead_index + 1 :]
        before_width = _run_width(before, gap) + gap * bool(before)
        trail_width = _run_width(trailing, gap) + gap * bool(trailing)
        one_row = before_width + lead.minimumSize().width() + trail_width <= width
        lead_width = max(width - before_width - trail_width * one_row, 0)
        # A wrapping label's size hint assumes a default width, not the one it gets here.
        lead_height = lead.heightForWidth(lead_width) if lead.hasHeightForWidth() else lead.sizeHint().height()
        row_height = max(lead_height, _tallest(before), _tallest(trailing) * one_row)
        placed = [(lead, QRect(before_width, 0, lead_width, row_height))]
        placed += _place_run(before, 0, 0, row_height, gap)
        y = 0 if one_row else row_height + gap
        for row in [trailing] if one_row else _wrap_rows(trailing, width, gap):
            band = row_height if one_row else _tallest(row)
            placed += _place_run(row, width - _run_width(row, gap), y, band, gap)
            y += band + gap
        return placed


def side_pair(text, widget, label_style):
    """A label just left of `widget`, as one item a FlowLayout can wrap."""
    pair = QWidget()
    layout = QHBoxLayout(pair)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    caption = QLabel(text)
    caption.setStyleSheet(label_style)
    layout.addWidget(caption)
    layout.addWidget(widget)
    return pair


def stacked_pair(text, widget, label_style):
    """A small caption above `widget`, as one item a FlowLayout can wrap."""
    pair = QWidget()
    layout = QVBoxLayout(pair)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    caption = QLabel(text)
    caption.setStyleSheet(label_style)
    layout.addWidget(caption)
    layout.addWidget(widget)
    return pair


def vertical_scroll(widget):
    """Scroll vertically without squeezing the widget below its minimum height."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setWidget(widget)
    return scroll


def wrapped_label(text):
    """A label that wraps at a narrow width instead of clipping."""
    label = QLabel(text)
    label.setWordWrap(True)
    return label


class WrappingCheckBox(QCheckBox):
    """A check box that wraps its text instead of clipping it at a narrow width."""

    def __init__(self, *args):
        super().__init__(*args)
        # The default Minimum policy makes the one-line text width the minimum width.
        policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

    def _text_left(self):
        style = self.style()
        return style.pixelMetric(QStyle.PixelMetric.PM_IndicatorWidth) + style.pixelMetric(
            QStyle.PixelMetric.PM_CheckBoxLabelSpacing
        )

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        text_box = QRect(0, 0, max(width - self._text_left(), 1), 10_000)
        wrapped = self.fontMetrics().boundingRect(text_box, Qt.TextFlag.TextWordWrap, self.text())
        return max(super().sizeHint().height(), wrapped.height() + 4)

    def minimumSizeHint(self):
        longest_word = max((self.fontMetrics().horizontalAdvance(word) for word in self.text().split()), default=0)
        return QSize(self._text_left() + longest_word, super().sizeHint().height())

    def paintEvent(self, _event):
        painter = QStylePainter(self)
        option = QStyleOptionButton()
        self.initStyleOption(option)
        option.text = ""
        painter.drawControl(QStyle.ControlElement.CE_CheckBox, option)
        group = self.palette().currentColorGroup()
        painter.setPen(self.palette().color(group, self.foregroundRole()))
        painter.drawText(
            self.rect().adjusted(self._text_left(), 0, 0, 0),
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignVCenter,
            self.text(),
        )


class _ResizeHook(QObject):
    def __init__(self, widget, callback):
        super().__init__(widget)
        self._callback = callback
        widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Resize:
            self._callback()
        return False


def on_resize(widget, callback):
    """Calls callback, with the new size already set, on each resize of widget for as long as it lives."""
    _ResizeHook(widget, callback)


def set_equipment_scroll_body(scroll, follower, gear, pets):
    """Keep the existing vertical order, with one scrollbar for the whole body.

    A fixed follower panel can exceed a short window when Pets expands. Let
    Equipment's existing scrollbar reach it as well as the gear below it.
    """
    body = QWidget()
    layout = QVBoxLayout(body)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addWidget(follower)
    layout.addWidget(gear, 1)
    scroll.setWidget(body)
    # Wide gear can still scroll sideways; it must not widen Pets off screen.
    on_resize(scroll.viewport(), lambda: follower.setMaximumWidth(scroll.viewport().width()))
    _CurrentRowScrollHook(scroll, pets)


class _CurrentRowScrollHook(QObject):
    """Keep keyboard-selected pets visible through Equipment's viewport."""

    def __init__(self, scroll, tree):
        super().__init__(scroll)
        self._tree = tree
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._reveal)
        tree.currentItemChanged.connect(self._queue)
        tree.installEventFilter(self)
        # A manual scroll toward the actions takes precedence over selection.
        scroll.verticalScrollBar().valueChanged.connect(self._timer.stop)
        on_resize(scroll.viewport(), self._queue)

    def eventFilter(self, watched, event):
        # Home/End can reveal the same current item without a change signal.
        if event.type() in (QEvent.Type.KeyPress, QEvent.Type.Show):
            self._queue()
        return False

    def _queue(self):
        # Wait for Qt's own item scrolling and the surrounding layout to settle.
        self._timer.start(0)

    def _reveal(self):
        tree, scroll = self._tree, self.parent()
        if not tree.isVisible():
            return
        if not tree.currentIndex().isValid():
            scroll.ensureWidgetVisible(tree, 0, 0)
            return
        row = tree.visualRect(tree.currentIndex())
        if row.top() < 0 or row.bottom() >= tree.viewport().height():
            hint = tree.ScrollHint.PositionAtTop if row.top() < 0 else tree.ScrollHint.PositionAtBottom
            horizontal = tree.horizontalScrollBar().value()
            tree.scrollTo(tree.currentIndex(), hint)
            tree.horizontalScrollBar().setValue(horizontal)
            row = tree.visualRect(tree.currentIndex())
        center = tree.viewport().mapTo(scroll.widget(), row.center())
        scroll.ensureVisible(center.x(), center.y(), 0, row.height() // 2 + 1)


class ElidedTipDelegate(QStyledItemDelegate):
    """Shows a cell's whole text as its tooltip while the cell is too narrow for it and elides it."""

    def helpEvent(self, event, view, option, index):
        if event.type() == QEvent.Type.ToolTip and self.sizeHint(option, index).width() > option.rect.width():
            QToolTip.showText(event.globalPos(), index.data(), view, option.rect)
            return True
        return super().helpEvent(event, view, option, index)


class _WrappedLastColumn(QStyledItemDelegate):
    def __init__(self, tree, minimum_chars):
        super().__init__(tree)
        self._column = tree.columnCount() - 1
        self._minimum_chars = minimum_chars
        tree.header().sectionResized.connect(self._section_resized)
        on_resize(tree.viewport(), self._stretch)

    def minimum_width(self):
        return self._minimum_chars * self.parent().fontMetrics().averageCharWidth()

    def _stretch(self):
        tree = self.parent()
        others = sum(tree.columnWidth(column) for column in range(self._column))
        tree.setColumnWidth(self._column, max(self.minimum_width(), tree.viewport().width() - others))

    def _section_resized(self, column, _old_size, new_size):
        if column == self._column:
            # Header dragging and resizeSection bypass _stretch. Restore the
            # readable floor before asking Qt to calculate the wrapped rows.
            minimum = self.minimum_width()
            if new_size < minimum:
                self.parent().setColumnWidth(column, minimum)
                return
            self.sizeHintChanged.emit(QModelIndex())
        else:
            self._stretch()

    def sizeHint(self, option, index):
        # Qt's style wraps only inside a valid rect, and the view passes a height of -1.
        tree = self.parent()
        painted = QStyleOptionViewItem(option)
        painted.rect = QRect(0, 0, tree.columnWidth(index.column()), tree.viewport().height())
        return super().sizeHint(painted, index)


def wrap_last_column(tree, minimum_chars):
    """Wraps a tree's last column in the room its other columns leave, but never in fewer than minimum_chars.

    The floor counts average characters of the tree's font, so at a large font
    the other columns cannot squeeze the text to a word per line; the tree
    scrolls sideways instead, which is why the column stretches here and not as
    a stretched last section, whose floor is the header's minimum for every
    column. The floor also keeps a wrapped row a few lines tall, so the tree
    keeps scrolling by item and its scrollbar is unchanged. QTreeView asks for
    row heights with an unset width, so the delegate sizes each wrapped cell at
    the column's width and relays the rows out when it changes.
    """
    tree.setWordWrap(True)
    tree.header().setStretchLastSection(False)
    tree.setItemDelegateForColumn(tree.columnCount() - 1, _WrappedLastColumn(tree, minimum_chars))


_WHEEL_GUARDED = "ankiscapeWheelGuard"


class _WheelGuard(QObject):
    """Refuses the wheel on number boxes and drop-down lists inside windows marked by guard_wheel.

    It is installed on the application because a wheel event reaches the box
    itself, never its window. The mark keeps Anki's own windows untouched. Anki's
    Fusion style lets the wheel change a drop-down list (only the native macOS
    style does not), so lists are covered with the number boxes.
    """

    def eventFilter(self, watched, event):
        if event.type() != QEvent.Type.Wheel or not isinstance(watched, (QAbstractSpinBox, QComboBox)):
            return False
        owner = watched
        while owner is not None and not owner.property(_WHEEL_GUARDED):
            owner = owner.parent()
        if owner is None:
            return False
        # Qt does not offer a sent wheel event to the parent widgets once the
        # box ignores it, so each ancestor gets a copy here until the scroll
        # area's viewport takes it.
        scrolled = False
        page = watched.parentWidget()
        while page is not None and not scrolled:
            scrolled = _offer_wheel(page, event)
            page = page.parentWidget()
        event.setAccepted(scrolled)
        return True


def _offer_wheel(widget, event):
    """Sends `widget` a copy of a wheel event, positioned in its own coordinates; True when it took it."""
    copy = QWheelEvent(
        QPointF(widget.mapFromGlobal(event.globalPosition().toPoint())),
        event.globalPosition(),
        event.pixelDelta(),
        event.angleDelta(),
        event.buttons(),
        event.modifiers(),
        event.phase(),
        event.inverted(),
    )
    QApplication.sendEvent(widget, copy)
    return copy.isAccepted()


_wheel_guard = None


def guard_wheel(window):
    """Marks `window`, and every window and widget it owns, as a place where the wheel never edits a value."""
    global _wheel_guard
    if _wheel_guard is None:
        _wheel_guard = _WheelGuard()
    window.setProperty(_WHEEL_GUARDED, True)
    QApplication.instance().installEventFilter(_wheel_guard)
    return window
