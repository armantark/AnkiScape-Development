"""Layouts and controls that keep their text whole at the 720 px minimum dialog width.

A QHBoxLayout squeezes labels and buttons below their text width; these wrap
the row instead, and WrappingCheckBox wraps its own text.

None of them uses heightForWidth: a vertical QBoxLayout treats such an item as
rigid, which would stop the flexible list beside them from giving up height.
Each remembers the width it was last given and sizes itself for that width, so
a width change settles after one extra layout pass.
"""

from aqt.qt import (  # type: ignore
    QCheckBox,
    QFrame,
    QLabel,
    QLayout,
    QRect,
    QScrollArea,
    QSize,
    QSizePolicy,
    QStyle,
    QStyleOptionButton,
    QStylePainter,
    Qt,
    QVBoxLayout,
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
    """Scroll `widget` vertically only; it keeps the scroll area's width."""
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
