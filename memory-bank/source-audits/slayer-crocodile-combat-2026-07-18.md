# Slayer Crocodile Combat closure

Date: 2026-07-18

Status: **the ordinary level-63 River Elid Crocodile is executable and advances
Vannaka to 21/35.**

## Cutoff identity

RuneScape Wiki `Crocodile`, oldid `6529105`, timestamp
`2012-11-03T16:42:54Z`, distinguishes two ordinary forms:

- level 63, 630 LP, 62 Slayer XP, maximum hit 67, guaranteed Bones, and no
  other drops; and
- level 89, 720 LP, 72 Slayer XP, maximum hit 88, guaranteed Big bones, rare
  long/curved bones, and a far-eastern marsh route without desert heat.

The page records Slayer 10, Vannaka membership, five-tick melee, and states that
most Crocodiles occupy desert-heat areas where a water source is required:
<https://runescape.wiki/w/Crocodile?oldid=6529105>.

This slice selects the level-63 River Elid representative. It is the
source-minimal Vannaka family row and preserves the task's distinctive
desert-supply pressure. The level-89 marsh variant remains a separate pinned
identity rather than a cosmetically duplicated picker row.

## Combat and drop reconciliation

Darkan
`data/npcs/combatdefs/uncategorized/crocodile/crocodile_(63).json`
supplies Attack 53, Strength 54, Defence 54, Magic/Ranged 1, a 59-tick respawn,
and corroborates 630 LP. Its 60-LP maximum conflicts with the period page's
explicit 67, so the period value wins.

Darkan's name-level `data/npcs/drops/crocodile.json` grants both Bones and Big
bones unconditionally because it merges the level-63 and level-89 identities.
That merged row is rejected. The level-63 implementation follows the cutoff
page exactly: one guaranteed Bones and no other table.

## Desert heat

The target reuses the live Desert-lizard hazard contract:

- a filled Waterskin dose is required to start;
- one dose is consumed per damaging Combat review;
- partial doses and the empty skin are preserved;
- up to eight filled skins may be loaded; and
- banking, death, and review undo remain atomic.

The historical requirement and dose preservation are exact. One dose per
damaging review remains the existing labeled review-native abstraction; no
wall clock is introduced.

`desert_context=True` is the live readiness proof for the Vannaka family. This
is derived from the actual hazard-bearing target rather than a prose waiver.

## Asset boundary

`combatenemies/crocodile.png` uses a current RuneScape Wiki render. Its upload
timestamp postdates the cutoff, so it is visual-only and is not cited as
historical evidence. The exact URL, timestamp, and hash are recorded in
`assets_provenance.json`.

## Live mapping

The standard Combat runtime handles Slayer gate/XP, five-tick pacing, melee
accuracy/prayer, the exact guaranteed drop, desert supply loading/consumption,
food, retreat, death, and undo. The picker exposes the water requirement,
67-LP maximum hit, Bones-only table, and target icon.

`tools/audit_slayer_readiness.py` derives Vannaka at 21/35. Fourteen blockers
remain: 13 missing Combat representatives plus Wilderness-risk behavior for
the existing Earth warrior. The incomplete role remains hidden and
unrenormalized. No owner-facing design fork emerged.

## Verification

Focused pure coverage passes all 263 checks and the real `.venv-qt` offscreen
Combat picker regression passes. Full pure discovery passes all 1,608 tests
with 214 declared environment skips. Final quality, documentation, readiness,
provenance, reachability, compilation, diff, and worktree checks are recorded
with the results artifact. Test quality reports zero hard issues and only the
four preexisting clone groups. The expected reachability debt ledger remains
1,231 actions, 1,822 reachable items, 285 orphan inputs, and 311 blocked
actions.

Results:
`memory-bank/status-updates/slayer-crocodile-results-2026-07-18.html`
(<https://kjy22255e4a6.postplan.dev>).
