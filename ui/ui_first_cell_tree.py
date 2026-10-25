"""A multi-column tree that looks and acts row-selected while selecting one cell per row.

Qt 6.11's macOS accessibility bridge frees a table's cell interfaces while it
builds the element for one selected cell, then reads the next selected cell of
the same row. Any accessibility client that asked a multi-column tree for its
selected children (computer-use tools, window managers, VoiceOver) crashed
Anki that way. With only the first cell of a row in the selection model, that
loop has one cell to read. The row keeps its look because every cell of a row
whose first cell is selected is painted selected, and keyboard and mouse still
move by whole rows.
"""

try:
    from aqt.qt import (  # type: ignore
        QAbstractItemView,
        QItemSelectionModel,
        QRect,
        QRegion,
        QStyle,
        QStyleOptionViewItem,
        QTreeWidget,
        Qt,
    )

    _ROW_SPAN = QItemSelectionModel.SelectionFlag.Rows | QItemSelectionModel.SelectionFlag.Columns
except Exception:  # pragma: no cover - non-Qt environment keeps imports safe
    QTreeWidget = object  # type: ignore[misc,assignment]


class FirstCellSelectionTree(QTreeWidget):
    """Keeps QTreeWidget's own selection model, so its item signals and isSelected() stay intact.

    Replacing the selection model would detach currentItemChanged,
    itemSelectionChanged and QTreeWidgetItem.isSelected(), which QTreeWidget
    binds to the model it creates; every override here only narrows what that
    model is asked to select.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Pinned, not inherited: row behavior gives the full-row hover and
        # selection painting, and only single selection keeps one selected
        # cell (the other modes let Ctrl+A select every cell past setSelection).
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def selectionCommand(self, index, event=None):
        # Qt's toggle commands must inspect the selected first cell, even when
        # the current cell is in another column of the same row.
        first = index.siblingAtColumn(0) if index.isValid() else index
        command = super().selectionCommand(first, event) & ~_ROW_SPAN
        if getattr(self, "_keyboard_selection", False) and index.isValid():
            # Selection keys and keyboard search select the current cell directly,
            # bypassing setSelection. Wait until Qt updates the current index
            # so selection listeners see the intended item as current, too.
            self._pending_keyboard_selection = (first, command)
            return QItemSelectionModel.SelectionFlag.NoUpdate
        return command

    def keyPressEvent(self, event):
        # macOS moves the current index only when navigation's selection
        # command is nonempty. Returning NoUpdate for arrows would move the
        # highlight alone and leave currentItemChanged consumers on the old
        # row. Space and Select bypass setSelection and need this deferral;
        # keyboardSearch handles its own direct selection below.
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Select):
            self._run_keyboard_selection(super().keyPressEvent, event)
        else:
            super().keyPressEvent(event)

    def keyboardSearch(self, search):
        self._run_keyboard_selection(super().keyboardSearch, search)

    def _run_keyboard_selection(self, handler, value):
        if getattr(self, "_keyboard_selection", False):
            return handler(value)
        self._keyboard_selection = True
        self._pending_keyboard_selection = None
        try:
            handler(value)
            # Space or a search match may leave the current index unchanged.
            self._select_keyboard_cell()
        finally:
            self._keyboard_selection = False

    def _select_keyboard_cell(self):
        pending = self._pending_keyboard_selection
        self._pending_keyboard_selection = None
        if pending is not None:
            self.selectionModel().select(*pending)

    def currentChanged(self, current, previous):
        if getattr(self, "_keyboard_selection", False):
            self._select_keyboard_cell()
        super().currentChanged(current, previous)

    def setSelection(self, rect, command):
        rect = rect.normalized()
        first_column = QRect(
            self.columnViewportPosition(0), rect.top(), self.columnWidth(0), rect.height()
        )
        super().setSelection(first_column, command & ~_ROW_SPAN)

    def moveCursor(self, cursorAction, modifiers):
        index = super().moveCursor(cursorAction, modifiers)
        return index.siblingAtColumn(0) if index.isValid() else index

    def drawRow(self, painter, option, index):
        if self.selectionModel().isSelected(index.siblingAtColumn(0)):
            option = QStyleOptionViewItem(option)
            option.state |= QStyle.StateFlag.State_Selected
        super().drawRow(painter, option, index)

    def visualRegionForSelection(self, selection):
        region = QRegion()
        width = self.viewport().width()
        for index in selection.indexes():
            cell = self.visualRect(index)
            region = region.united(QRect(0, cell.top(), width, cell.height()))
        return region
