"""Dark-mode-safe dimmed text colors, shared by every AnkiScape panel.

RECURRING BUG, READ BEFORE STYLING TEXT: ``palette(mid)`` / ``QPalette.Mid`` is
a *frame/border* role, NOT a text role. In dark mode it resolves to a near-black
grey, so using it as a text/foreground color makes the text invisible on the
dark base (greyed/disabled rows "vanish"). It has bitten the Skills-hub buttons,
the Smithing locked rows, and the Equipment empty slots. Never use palette(mid)
(or QPalette.Mid) for text. For dimmed-but-legible text use the helpers below,
which derive the color from the theme's actual Text role and just drop the
alpha — guaranteed contrast in BOTH light and dark themes. (palette(mid) is fine
for borders/frames, which is its intended role.)
"""

try:
    from aqt.qt import QApplication, QColor, QPalette  # type: ignore
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass


def dim_text_color(widget=None, alpha=150) -> "QColor":
    """A dimmed-but-readable text QColor that works in light AND dark themes.

    Use for greyed/placeholder/disabled-row text (e.g. ``setForeground(...)``).
    """
    palette = widget.palette() if widget is not None else QApplication.palette()
    color = QColor(palette.color(QPalette.ColorRole.Text))
    color.setAlpha(alpha)
    return color


def dim_text_css(widget=None, alpha=150) -> str:
    """``rgba(...)`` form of :func:`dim_text_color` for Qt stylesheets.

    Stylesheets can't reference a dimmed text role (the stylesheet ``palette()``
    function only exposes solid roles, and ``mid`` is the trap we're avoiding), so
    bake an explicit rgba string from the live palette instead.
    """
    c = dim_text_color(widget, alpha)
    return f"rgba({c.red()}, {c.green()}, {c.blue()}, {c.alphaF():.2f})"
