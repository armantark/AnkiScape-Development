---
root: false
targets:
  - '*'
description: Dark-mode-safe text colors for the Qt UI (never use palette(mid) for text)
globs:
  - ui.py
cursor:
  alwaysApply: false
  description: Dark-mode-safe text colors for the Qt UI (never use palette(mid) for text)
  globs:
    - ui.py
---
# Qt text colors must survive dark mode

`palette(mid)` / `QPalette.Mid` is a **frame/border** role, not a text role. In
dark mode it resolves to a near-black grey, so using it as a **text/foreground**
color makes the text invisible on the dark base. This has recurred on the
Skills-hub buttons, Smithing locked rows, and Equipment empty slots — do not
reintroduce it.

For dimmed-but-legible text (greyed / placeholder / disabled rows), use the
helpers in `ui.py`, which derive the color from the theme's actual `Text` role
and just drop the alpha, so contrast holds in **both** light and dark themes.

```python
# ❌ BAD — invisible in dark mode
item.setForeground(widget.palette().color(QPalette.ColorRole.Mid))
w.setStyleSheet("QTreeWidget::item:disabled { color: palette(mid); }")
label.setStyleSheet("color: palette(mid);")

# ✅ GOOD — legible in both themes
item.setForeground(dim_text_color(widget))
w.setStyleSheet(f"QTreeWidget::item:disabled {{ color: {dim_text_css(w)}; }}")
label.setStyleSheet(f"color: {dim_text_css(label)};")
```

`palette(mid)` is fine for **borders/frames** (`border: 1px solid palette(mid)`).
Prefer `palette(text)` / `palette(base)` pairings over `buttonText`/`button` for
button labels (the button face renders light on macOS dark mode and washes out
text). When in doubt, verify a change in dark mode, not just light.
