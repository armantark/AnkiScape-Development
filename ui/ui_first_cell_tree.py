"""Trees that Qt 6.11's macOS accessibility bridge cannot crash.

That bridge (QTBUG-149612, fixed upstream after 6.11) frees a tree's
accessible interface, with every cell interface it caches, whenever it builds
the element for a cell that a client resolved only through a row or column
frame. Any accessibility client (computer-use tools, window managers,
VoiceOver) reads those frames, so two Qt paths free a cell they still use:

- Asking a multi-column tree for its selected children: the bridge reads the
  next selected cell of a row after building the element for the first.
  FirstCellSelectionTree keeps only the first cell of a row in the selection
  model, so that loop has one cell to read. The row keeps its look because
  every cell of a row whose first cell is selected is painted selected, and
  keyboard and mouse still move by whole rows.
- Laying out a tree a client has read: the layout resets the tree's cells,
  and the bridge builds an element for each cell it deletes. A tree lays
  itself out lazily, so a client that reads a tree just shown runs that layout
  itself and the reset follows its read. show_settled runs the layout and its
  reset before control returns to the event loop. A tree that leaves the
  screen is emptied before it is detached, because detaching restyles it and
  a restyle lays it out again; emptying resets the model, which invalidates
  the cells first, and the bridge builds no element for an invalid cell. A
  tree that reorders or hides rows on screen (a list search) takes every row
  out first for the same reason, then puts them back and runs settle_tree.
"""

try:
    from aqt.qt import (  # type: ignore
        QAbstractItemView,
        QCoreApplication,
        QEvent,
        QItemSelectionModel,
        QRect,
        QPoint,
        QRegion,
        QStyle,
        QStyleOptionViewItem,
        QTreeView,
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


def show_settled(widget) -> None:
    """Show ``widget`` with every tree in it laid out and its accessibility reset already run."""
    widget.show()
    for tree in widget.findChildren(QTreeView):
        settle_tree(tree)


def settle_tree(tree) -> None:
    """Lay out ``tree`` and run the accessibility reset that layout queues, before control returns to the event loop."""
    tree.executeDelayedItemsLayout()
    QCoreApplication.sendPostedEvents(tree, QEvent.Type.MetaCall)


class WholeRowTree(QTreeWidget):
    """Keep the last visible row whole, including when wrapped rows change height."""

    def updateGeometries(self):
        super().updateGeometries()
        available = self.viewport().height() + self.viewportMargins().bottom()
        index = self.indexAt(QPoint(self.viewport().width() // 2, 0))
        bottom = 0
        while index.isValid():
            rect = self.visualRect(index)
            if rect.bottom() >= available:
                break
            bottom = rect.bottom() + 1
            index = self.indexBelow(index)
        margin = available - bottom if index.isValid() and bottom else 0
        if margin != self.viewportMargins().bottom():
            self.setViewportMargins(0, 0, 0, margin)
