"""Geometry probes for visible text in an offscreen Qt widget tree.

Callers must show, resize and pump events before probing, per
.claude/rules/qt-offscreen-screenshots.md: unlaid-out children report stale
geometry, and these probes trust widget geometry, not pixels.
"""

from aqt.qt import QAbstractScrollArea, QCheckBox, QComboBox, QLabel, QPoint, QPushButton, QRadioButton, QRect

# Controls that draw their text at their size hint and elide or cut it when squeezed.
_HINTED = (QPushButton, QCheckBox, QRadioButton, QComboBox)


def _text_fits(widget) -> bool:
    if isinstance(widget, _HINTED):
        return widget.sizeHint().width() <= widget.width()
    if widget.wordWrap():
        # A wrapped label's minimum width is its longest word, which wrapping
        # cannot shorten; the height check alone misses that clip.
        return (
            widget.minimumSizeHint().width() <= widget.width()
            and widget.heightForWidth(widget.width()) <= widget.height()
        )
    metrics = widget.fontMetrics()
    lines = widget.text().splitlines()
    contents = widget.contentsRect()
    return (
        max(metrics.horizontalAdvance(line) for line in lines) <= contents.width()
        and metrics.lineSpacing() * len(lines) <= contents.height()
    )


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
    """Name each visible label or control text that is clipped, leaves root, or overlaps another."""
    widgets = _shown_text_widgets(root)
    rects = [QRect(widget.mapTo(root, QPoint(0, 0)), widget.size()) for widget in widgets]
    defects = []
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
