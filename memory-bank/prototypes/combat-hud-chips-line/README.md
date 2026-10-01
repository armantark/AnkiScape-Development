# Prototype: the combat chips line on the review HUD (ruling 4.29.6)

Throwaway. Nothing here is production code.

## Question

On the review HUD combat card, the line `Kills: N · Trains ...` has only 192 px
beside the Bank run button. For the aggressive and controlled styles it does
not fit, so the end of the line is cut off. Which structure should replace it?

The longest real line is the controlled melee style with a four-digit kill
count: `Kills: 1386 · Trains Attack • Strength • Defence • Constitution`. It is
shown with a Slayer task, `Slayer: 4 of 17 left`, because that adds a line to
the same area.

On main, the HUD calculates the trained skills without the equipped weapon, so
every weapon counts as bare fists, and the controlled style can never show its
four skills. The prototype gives the HUD the real equipment table so that the
longest line appears. That is a separate bug, and this prototype does not fix it.

## Run

From the repo root:

```
.venv-qt/bin/python memory-bank/prototypes/combat-hud-chips-line/prototype.py
```

It opens a stand-in reviewer window that contains the real review strip, with
the real HUD at its real 340 x 128 size and a pink switcher pill under it. Click
A, B or C, or press the left and right arrow keys. Each switch prints every
visible text with its position and size, and lists any clipped or overlapping
text. Options: `--style aggressive`, `--no-slayer`, `--dark`, `--capture`
(rewrites the PNGs here).

## Variants

- **A. Wrap beside Bank run.** The chips wrap onto two lines in the same place.
  The Slayer line moves up to the right end of the enemy name line.
- **B. Bank run beside the enemy.** Bank run moves up beside the enemy name and
  health bar. That bar becomes shorter. Under them are two full-width lines:
  `Kills: 1386 · Slayer: 4 of 17 left`, then
  `Trains Attack • Strength • Defence • Constitution`.
- **C. Skill icons.** The line stays where it is, but the trained skills are
  shown as their skill icons. The full sentence is in the tooltip.

## Screenshots

`hud-<controlled|aggressive>-<variant>-<light|dark>.png` shows the card at its
real width, at 2x pixel density. The capture checked every text at both reviewer
sizes (900 x 560 and 1000 x 700). No text clips or overlaps in any of the 12
PNGs, and each PNG was also checked by eye.

## Verdict

**C, picked by the owner on 2026-10-01 (ruling 4.29.8).** Four small icons fit
the 192 px space beside Bank run for every style, in the ordinary fight, a
Slayer-task fight, and a quest fight. The full sentence is in the tooltip. The
prototype recommended B, which keeps every word visible but moves Bank run and
shortens the enemy health bar. Production also fixes the bug described above:
the card now reads the equipped weapon from the same equipment table that the
combat review uses, so the icons match the style's real trained skills.
