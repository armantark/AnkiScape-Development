# Slayer Jungle horror Combat closure

Date: 2026-07-18

Status: **the ordinary level-70 Jungle horror is executable and advances
Vannaka to 23/35.**

## Cutoff identity

RuneScape Wiki `Jungle horror`, oldid `6534099`, timestamp
`2012-11-04T17:52:15Z`, establishes:

- level 70, 450 LP, 45 Slayer XP, and Vannaka membership;
- six-tick melee with an 84-LP maximum hit;
- guaranteed Bones; and
- the Mos Le'Harmless location reached after Cabin Fever.

Source:
<https://runescape.wiki/w/Jungle_horror?oldid=6534099>.

Mos Le'Harmless access is represented by the already-live Cabin Fever
completion gate. This slice adds no quest definition or stage and therefore
does not overlap the Darkan quest-parity thread.

## Combat and drops

Darkan
`data/npcs/combatdefs/uncategorized/jungle_horror.json`
corroborates 450 LP and maximum hit 84 and supplies Attack 70, Strength 70,
Defence 55, Magic/Ranged 1, and a 59-tick respawn.

Darkan `data/npcs/drops/jungle_horror.json` supplies one guaranteed Bones row
and 32 weighted ordinary rows:

- ten common rows at 1,679/20,000, including Nature runes, iron equipment,
  seeds, fruit, and logs;
- seven uncommon rows at 999/50,000;
- Iron ore at 93/50,000; and
- fourteen rare rows at 31/25,000.

The initial implementation incorrectly treated those 32 JSON rows as
independent hit-or-empty rolls. Darkan's executable `DropList` instead sorts
all nonzero `DropTable` rates into adjacent intervals and makes one random
selection across the list. The corrected exact common denominator is 100,000:
the ten common rows each occupy 8,395 slots, the seven uncommon rows 1,998
each, Iron ore 186, the fourteen rare rows 124 each, and 142 slots yield no
ordinary drop. The rate-zero Bones row remains guaranteed and separate.

The cutoff page exposes qualitative charm drops but the exact period
distribution was not recovered. Charm rolls remain `source_blocked` rather
than invented.

## Asset boundary

`combatenemies/jungle_horror.png` uses a current RuneScape Wiki render. It is
visual-only and is not cited as historical evidence. Exact URL, timestamp, and
hash are recorded in `assets_provenance.json`.

## Live mapping

The standard Combat runtime handles the Cabin Fever gate, Slayer XP, six-tick
melee, the one 100,000-slot ordinary selector, guaranteed Bones, inventory capacity, food,
retreat, death, and undo. The picker exposes the route lock, 84-LP maximum hit,
drop probabilities, and target icon.

`tools/audit_slayer_readiness.py` derives Vannaka at 23/35. Twelve blockers
remain: 11 missing Combat representatives plus Wilderness-risk behavior for
the existing Earth warrior. The incomplete role remains hidden and
unrenormalized. No owner-facing design fork emerged.

## Verification

The original bounded review did not inspect Darkan's Java loader and therefore
missed the JSON-semantics defect. The cross-target correction is independently
regression-tested and documented in
`slayer-darkan-drop-selector-correction-2026-07-18.md`. Full discovery and final quality, documentation, readiness,
provenance, reachability, compilation, diff, and worktree checks are recorded
with the results artifact. Full pure discovery passes all 1,610 tests with 214
declared environment skips. Test quality reports zero hard issues and only the
four preexisting clone groups. The expected reachability debt ledger now
contains 1,231 actions, 1,823 reachable items, 285 orphan inputs, and 311
blocked actions; the one-item increase is the newly reachable Jungle horror
sprite-backed target output.

Results:
`memory-bank/status-updates/slayer-jungle-horror-results-2026-07-18.html`
(<https://7s9qx4vwmhao.postplan.dev>).
