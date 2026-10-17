"""Geometry probes for visible text in an offscreen Qt widget tree.

Callers must show, resize and pump events before probing, per
.claude/rules/qt-offscreen-screenshots.md: unlaid-out children report stale
geometry, and these probes trust widget geometry, not pixels.
"""

import itertools

from aqt.qt import (
    QAbstractButton,
    QAbstractItemView,
    QAbstractScrollArea,
    QCheckBox,
    QComboBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QModelIndex,
    QPoint,
    QPushButton,
    QRadioButton,
    QRect,
    QSize,
    QStyle,
    QStyleOptionButton,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTreeView,
    Qt,
)

# Controls that draw their text at their size hint and elide or cut it when squeezed.
_HINTED = (QPushButton, QCheckBox, QRadioButton, QComboBox)


def _text_fits(widget) -> bool:
    if isinstance(widget, QCheckBox) and widget.hasHeightForWidth():
        # A check box that wraps its own text needs only its longest word's width.
        return (
            widget.minimumSizeHint().width() <= widget.width()
            and widget.heightForWidth(widget.width()) <= widget.height()
        )
    if isinstance(widget, QPushButton):
        # A push button's size hint adds style margins the text never needs, so
        # measure the style's content rectangle instead.
        option = _button_option(widget)
        contents = widget.style().subElementRect(
            QStyle.SubElement.SE_PushButtonContents,
            option,
            widget,
        )
        text_size = option.fontMetrics.size(Qt.TextFlag.TextShowMnemonic, option.text)
        return text_size.width() <= contents.width() and text_size.height() <= contents.height()
    if isinstance(widget, (QAbstractButton, QComboBox)):
        return widget.sizeHint().width() <= widget.width()
    if widget.wordWrap():
        # A wrapped label's minimum width is its longest word, which wrapping
        # cannot shorten; the height check alone misses that clip.
        return (
            widget.minimumSizeHint().width() <= widget.width()
            and widget.heightForWidth(widget.width()) <= widget.height()
        )
    if widget.textFormat() == Qt.TextFormat.RichText or "<img" in widget.text():
        # A one-line rich label: the metrics below would measure the markup, not what Qt draws.
        hint = widget.sizeHint()
        return hint.width() <= widget.width() and hint.height() <= widget.height()
    metrics = widget.fontMetrics()
    lines = widget.text().splitlines()
    contents = widget.contentsRect()
    return (
        max(metrics.horizontalAdvance(line) for line in lines) <= contents.width()
        and metrics.lineSpacing() * len(lines) <= contents.height()
    )


def _button_option(button) -> QStyleOptionButton:
    # initStyleOption is protected, and PyQt refuses protected calls on widgets
    # Qt created itself, such as a QMessageBox's buttons; this mirrors it.
    option = QStyleOptionButton()
    option.initFrom(button)
    option.text = button.text()
    option.icon = button.icon()
    option.iconSize = button.iconSize()
    feature = QStyleOptionButton.ButtonFeature
    for enabled, flag in (
        (button.isFlat(), feature.Flat),
        (button.menu() is not None, feature.HasMenu),
        (button.autoDefault(), feature.AutoDefaultButton),
        (button.isDefault(), feature.DefaultButton),
    ):
        if enabled:
            option.features |= flag
    return option


def _view_item_option(view) -> QStyleOptionViewItem:
    # The same mirror of the protected initViewItemOption.
    option = QStyleOptionViewItem()
    option.initFrom(view)
    option.widget = view
    metric = view.style().pixelMetric(QStyle.PixelMetric.PM_SmallIconSize, None, view)
    option.decorationSize = view.iconSize() if view.iconSize().isValid() else QSize(metric, metric)
    option.textElideMode = view.textElideMode()
    if view.wordWrap():
        option.features |= QStyleOptionViewItem.ViewItemFeature.WrapText
    return option


def _laid_out_indexes(view, parent=QModelIndex()):
    """Every cell the view lays out: expanded tree branches, shown rows and columns."""
    model = view.model()
    for row in range(model.rowCount(parent)):
        # QAbstractListModel keeps columnCount private, so walk to the first invalid column.
        cells = (model.index(row, column, parent) for column in itertools.count())
        for index in itertools.takewhile(QModelIndex.isValid, cells):
            if view.visualRect(index).width() > 0:
                yield index
        first = model.index(row, 0, parent)
        if isinstance(view, QTreeView) and view.isExpanded(first):
            yield from _laid_out_indexes(view, first)


def _cell_text_clipped(view, option, index) -> bool:
    """Measure the text in the rectangle the style paints it in.

    A delegate's size hint is no proof: QStyleSheetStyle wraps the hint's text
    at the full cell width and adds the stylesheet padding afterwards, while
    painting wraps inside the padding (see WrappedRowDelegate).
    """
    cell = QStyleOptionViewItem(option)
    cell.rect = view.visualRect(index)
    # Only a Python-created delegate may call the protected initStyleOption.
    QStyledItemDelegate().initStyleOption(cell, index)
    style = view.style()
    text_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, cell, view)
    width = text_rect.width() - 2 * (style.pixelMetric(QStyle.PixelMetric.PM_FocusFrameHMargin, cell, view) + 1)
    wraps = cell.features & QStyleOptionViewItem.ViewItemFeature.WrapText
    flags = Qt.TextFlag.TextWordWrap if wraps else Qt.TextFlag.TextSingleLine
    needed = cell.fontMetrics.boundingRect(QRect(0, 0, width, 1 << 20), flags, cell.text)
    return needed.width() > width or needed.height() > text_rect.height()


def _item_view_defects(root) -> list[str]:
    """Name each tree, list or table cell whose text its cell cuts short.

    Rows scrolled out of view count too: a column is as wide for them as for
    the rows on screen.
    """
    defects = []
    for view in root.findChildren(QAbstractItemView):
        if isinstance(view, QHeaderView) or not view.isVisibleTo(root):
            continue
        option = _view_item_option(view)
        for index in _laid_out_indexes(view):
            if _cell_text_clipped(view, option, index):
                defects.append(f"row {index.data()!r} is clipped in {view.visualRect(index).size()}")
    return defects


def _scrolled_out(widget, root) -> bool:
    """True when a scroller inside root has scrolled the widget out of its viewport.

    That text is reached by scrolling, not clipped; callers check a nested
    scroller's horizontal range themselves.
    """
    ancestor = widget.parentWidget()
    while ancestor is not None and ancestor is not root:
        area = ancestor.parentWidget()
        if isinstance(area, QAbstractScrollArea) and area.viewport() is ancestor:
            if not ancestor.rect().contains(QRect(widget.mapTo(ancestor, QPoint(0, 0)), widget.size())):
                return True
        ancestor = area
    return False


def _text(widget) -> str:
    return widget.currentText() if isinstance(widget, QComboBox) else widget.text()


def _shown_text_widgets(root) -> list:
    widgets = [widget for kind in (QLabel, *_HINTED) for widget in root.findChildren(kind)]
    return [widget for widget in widgets if _text(widget) and widget.isVisibleTo(root) and not _scrolled_out(widget, root)]


def text_fit_defects(root) -> list[str]:
    """Name each visible label, control or item-view row whose text is clipped, leaves root, or overlaps another."""
    widgets = _shown_text_widgets(root)
    rects = [QRect(widget.mapTo(root, QPoint(0, 0)), widget.size()) for widget in widgets]
    defects = _item_view_defects(root)
    for widget, rect in zip(widgets, rects):
        if not root.rect().contains(rect):
            defects.append(f"{_text(widget)!r} at {rect} leaves {root.rect()}")
        if not _text_fits(widget):
            defects.append(f"{_text(widget)!r} is clipped in {widget.size()}")
    for index, (left, left_rect) in enumerate(zip(widgets, rects)):
        for right, right_rect in zip(widgets[index + 1 :], rects[index + 1 :]):
            if left_rect.intersects(right_rect):
                defects.append(f"{_text(left)!r} overlaps {_text(right)!r}")
    return defects


def clipped_text_defects(root) -> list[str]:
    """Name each visible control whose text is cut off: labels, buttons, check boxes and search placeholders."""
    controls = [
        widget
        for widget in root.findChildren(QLabel) + root.findChildren(QAbstractButton)
        if widget.text() and widget.isVisibleTo(root)
    ]
    defects = [f"{widget.text()!r} is clipped in {widget.size()}" for widget in controls if not _text_fits(widget)]
    # The 10 px side padding and 1 px border of the search field's stylesheet.
    defects += [
        f"placeholder {edit.placeholderText()!r} is clipped in {edit.size()}"
        for edit in root.findChildren(QLineEdit)
        if edit.isVisibleTo(root) and edit.fontMetrics().horizontalAdvance(edit.placeholderText()) + 22 > edit.width()
    ]
    return defects
