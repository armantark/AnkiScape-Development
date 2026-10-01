# Prototype: long locked rows in the flat Skills target list (ruling 4.29.6)

Throwaway. Nothing here is production code.

## Question

On main, a long locked row in a flat Skills target list runs off the right edge
and hides behind a sideways scrollbar. Which row structure should replace that?

The worst real rows, found by opening every flat Skills list at levels 1, 33
and 99:

- Agility: `Dorgesh-Kaan Agility Course (Lvl 80) — Locked: Death To The Dorgeshuun`
  (the longest row that carries a lock reason in its text).
- Fishing: `Catch leaping trout (Lvl 48)/leaping salmon (Lvl 58)/leaping sturgeon (Lvl 70)`
  (the longest locked row of all, 78 characters).

## Run

From the repo root:

```
.venv-qt/bin/python memory-bank/prototypes/flat-target-list-locked-rows/prototype.py
```

It opens the real Skills dialog (Agility, every skill at level 85, no quests
done) at 720 x 560 with a pink switcher pill under it. Click A, B or C, or press
the left and right arrow keys. Each switch prints every locked row and whether it
fits. Options: `--skill fishing`, `--dark`, `--capture` (rewrites the PNGs here).

## Variants

- **A. Wrap the row.** The row keeps its text and wraps onto as many lines as it
  needs. This reuses the width-aware wrapper the Shop list already uses.
- **B. Name line and lock line.** The name is on the first line. Every lock
  reason from the tooltip is on a smaller second line, for example
  `Locked: Death To The Dorgeshuun, Lit torch or another valid alternative`.
  Today the row shows only the first reason.
- **C. Short row.** The row shows only the name. Extra catches fold into
  `+N more` (`Catch leaping trout (Lvl 48) +2 more`). The lock reason stays in
  the row tooltip, and in the Details panel after you click the row. If a short
  row is still too wide for a narrow list, it wraps.

## Screenshots

`<skill>-<variant>-<light|dark>-<width>x560.png`, for Agility and Fishing, at
720 px wide (the dialog minimum) and 900 px wide. Each one is scrolled to the
longest locked row. No variant clips a locked row in any of the 24 PNGs. The
capture checks the row geometry, and each PNG was also checked by eye.

At 720 px wide, some text in the panel header clips on main too:
`Agility — Lv 85` cuts to `Lv 8`, the `Currently training` button shows
`rently train`, and the Talent Scout checkbox loses its last letters. This
prototype did not cause those clips and does not fix them.

## Verdict

**C, picked by the owner on 2026-10-01 (ruling 4.29.8).** A short row keeps
most rows on one line in a list that has only about 124 px of height at 560 px
tall. The lock reason and the extra catches are still in the row tooltip and
the Details panel. The prototype recommended A, which keeps the reason in the
row but makes more rows wrap. Production (`ui/ui_target_search.py`) applies C to
every flat Skills target list. When a short row is still too wide, it wraps
instead of scrolling sideways.
