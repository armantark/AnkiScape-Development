"""Geometry probes for visible text in an offscreen Qt widget tree.

Callers must show, resize and pump events before probing, per
.claude/rules/qt-offscreen-screenshots.md: unlaid-out children report stale
geometry, and these probes trust widget geometry, not pixels.
"""

from aqt.qt import QLabel, QPoint, QPushButton, QRect, Qt


def _text_fits(widget) -> bool:
    if isinstance(widget, QPushButton):
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


def text_fit_defects(root) -> list[str]:
    """Name each visible label or button text that is clipped, leaves root, or overlaps another."""
    widgets = [
        widget
        for widget in root.findChildren(QLabel) + root.findChildren(QPushButton)
        if widget.text() and widget.isVisibleTo(root)
    ]
    rects = [QRect(widget.mapTo(root, QPoint(0, 0)), widget.size()) for widget in widgets]
    defects = []
    for widget, rect in zip(widgets, rects):
        if not root.rect().contains(rect):
            defects.append(f"{widget.text()!r} at {rect} leaves {root.rect()}")
        if not _text_fits(widget):
            defects.append(f"{widget.text()!r} is clipped in {widget.size()}")
    for index, (left, left_rect) in enumerate(zip(widgets, rects)):
        for right, right_rect in zip(widgets[index + 1 :], rects[index + 1 :]):
            if left_rect.intersects(right_rect):
                defects.append(f"{left.text()!r} overlaps {right.text()!r}")
    return defects
