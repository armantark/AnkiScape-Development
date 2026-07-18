# Slayer Bloodveld Combat closure

Date: 2026-07-18

Status: **ordinary level-76 Bloodveld is executable and advances Vannaka to
18/35.**

## Cutoff identity

RuneScape Wiki `Bloodveld`, oldid `6565794`, timestamp
`2012-11-17T10:08:16Z`, establishes:

- ordinary combat levels 76 and 81, with 1,200/1,340 lifepoints;
- Slayer 50 to kill and 120/134 Slayer XP;
- passive six-tick magic-based melee;
- maximum hits 59/60;
- guaranteed Bones; and
- Vannaka, Sumona, Chaeldar, Duradel, and Kuradal membership.

This slice selects the ordinary level-76 Slayer Tower representative. The
level-81 God Wars variant remains a separately pinned variant rather than a
second indistinguishable picker row:
<https://runescape.wiki/w/Bloodveld?oldid=6565794>.

## Combat and drops

Darkan
`data/npcs/combatdefs/uncategorized/bloodveld/bloodveld_(76).json`
corroborates 1,200 LP and maximum hit 59 and supplies Attack 75, Strength 45,
Defence 30, Magic/Ranged 1, and a 59-tick respawn. Its `attackBonus` is
`MAGIC_ATT`, corroborating the period magic-based-melee description; the
existing shared `magic_melee` channel handles that distinction while Protect
from Melee remains the relevant prayer.

Darkan `data/npcs/drops/bloodveld.json` supplies guaranteed item 526, Bones,
plus 21 weighted ordinary rows at denominator 128. Their weights sum to 123,
so the remaining five slots are preserved explicitly as no additional drop.
The table includes:

- five coin quantities;
- Fire and Blood runes;
- ordinary and bonus Bones/Big bones;
- Steel hatchet, Steel full helm, Steel scimitar, Black boots, Mithril square
  shield, Mithril chainbody, and Rune med helm;
- Meat pizza; and
- Gold ore.

No rare-drop-table, charm, herb, or clue row is fabricated where the pinned
Darkan table does not supply one.

## Black boots

RuneScape Wiki `Black boots`, oldid `6426419`, timestamp
`2012-10-16T06:22:26Z`, establishes item 4125's Defence-10 gate, feet slot,
tradeability, non-stackability, and Bloodveld acquisition:
<https://runescape.wiki/w/Black_boots?oldid=6426419>.

The primary 2011Scape `data/cfg/items.yml` item 4125 supplies Magic attack -3,
Ranged attack -1, and melee defences +7/+8/+9.
`tools/generate_equipment_data.py` owns the row so regeneration is stable.

## Asset boundary

`combatenemies/bloodveld.png` and `combatitems/black_boots.png` use OSRS Wiki
renders. Their upload timestamps postdate the cutoff, so they are visual-only
and are not cited as historical evidence. Exact URLs, timestamps, and hashes
are recorded in `assets_provenance.json`.

## Live mapping

The standard Combat runtime handles the Slayer gate/XP, six-tick pacing,
magic-based-melee defence roll, exact drop selection, inventory capacity, undo,
and death paths. The Combat picker exposes the attack semantics, maximum hit,
complete ordinary table, and target sprite.

`tools/audit_slayer_readiness.py` now derives Vannaka at 18/35. Seventeen
blockers remain: 16 missing Combat representatives plus Wilderness-risk
behavior for the existing Earth warrior. No owner-facing design fork emerged.

## Verification

Focused pure coverage passes all 318 checks, the real offscreen Qt Combat
picker regression passes, and full pure discovery passes all 1,601 tests with
214 declared environment skips. Equipment regeneration is byte-stable, test
quality has zero hard issues and only the four preexisting clone groups, and
documentation, JSON, compilation, readiness, focused reachability, diff, and
worktree-safety checks pass.

Results:
`memory-bank/status-updates/slayer-bloodveld-results-2026-07-18.html`
(<https://k9ynbzcx5a8u.postplan.dev>).
