"""A left-to-right layout that wraps whole widgets onto new lines.

Qt has no flow layout, and a rich-text label breaks a line after every inline
image, which split a tool belt icon from its name; wrapping whole widgets
keeps each icon and name together at any width.
"""

try:
    from aqt.qt import QLayout, QPoint, QRect, QSize, Qt  # type: ignore
except Exception:  # pragma: no cover - non-Qt environment keeps imports safe
    QLayout = object  # type: ignore[misc,assignment]


class FlowLayout(QLayout):
    def __init__(self, parent=None, h_spacing: int = 10, v_spacing: int = 4):
        super().__init__(parent)
        self._items: list = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item) -> None:  # noqa: N802 - Qt override
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):  # noqa: N802 - Qt override
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index: int):  # noqa: N802 - Qt override
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):  # noqa: N802 - Qt override
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:  # noqa: N802 - Qt override
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802 - Qt override
        return self._arrange(QRect(0, 0, width, 0), move=False)

    def setGeometry(self, rect) -> None:  # noqa: N802 - Qt override
        super().setGeometry(rect)
        self._arrange(rect, move=True)

    def sizeHint(self):  # noqa: N802 - Qt override
        return self.minimumSize()

    def minimumSize(self):  # noqa: N802 - Qt override
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        return size + QSize(margins.left() + margins.right(), margins.top() + margins.bottom())

    def _lines(self, width: int) -> list:
        """(item, size hint) pairs grouped into the lines they wrap into at `width`."""
        lines, x = [[]], 0
        for item in self._items:
            hint = item.sizeHint()
            if lines[-1] and x + hint.width() > width:
                lines.append([])
                x = 0
            lines[-1].append((item, hint))
            x += hint.width() + self._h_spacing
        return lines

    def _arrange(self, rect, move: bool) -> int:
        margins = self.contentsMargins()
        area = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        y = area.y()
        for line in self._lines(area.width()):
            line_height = max((hint.height() for _item, hint in line), default=0)
            x = area.x()
            for item, hint in line if move else ():
                # Centred on its line, so a check box's text lines up with the taller combo beside it.
                item.setGeometry(QRect(QPoint(x, y + (line_height - hint.height()) // 2), hint))
                x += hint.width() + self._h_spacing
            y += line_height + self._v_spacing
        return y - self._v_spacing - rect.y() + margins.bottom()
