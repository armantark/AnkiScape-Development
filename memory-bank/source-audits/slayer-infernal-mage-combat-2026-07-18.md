# Slayer Infernal Mage Combat closure

Date: 2026-07-18

Status: **the ordinary level-66 Infernal Mage is executable and advances
Vannaka to 19/35.**

## Cutoff identity

RuneScape Wiki `Infernal Mage`, oldid `6446423`, timestamp
`2012-10-20T01:07:22Z`, establishes:

- combat level 66, 600 lifepoints, Slayer 45, and 60 Slayer XP;
- Magic attacks at six-tick speed with a maximum hit of 89;
- guaranteed Bones;
- rare dark mystic and Lava battlestaff drops; and
- Vannaka and Chaeldar assignment membership.

Source:
<https://runescape.wiki/w/Infernal_Mage?oldid=6446423>.

## Combat and drops

Darkan
`data/npcs/combatdefs/uncategorized/infernal_mage.json`
corroborates the source combat identity and supplies Attack 1, Strength 1,
Defence 60, Magic 75, Ranged 1, and a 59-tick respawn.

Darkan `data/npcs/drops/infernal_mage.json` supplies four independent tables:

- guaranteed Bones;
- a 128-slot ordinary table with 107 named slots and 21 explicit empty slots;
- dark Mystic boots and dark Mystic hat as separate 1/512 rolls; and
- Lava battlestaff as a separate 1/1,000 roll.

Keeping the three non-guaranteed rolls independent allows the rare equipment
to accompany an ordinary table result, matching the source shape. No charm
distribution is recoverable from the pinned table or cutoff page, so charm
rates remain `source_blocked` rather than invented.

## Rare equipment

RuneScape Wiki `Lava battlestaff`, oldid `6037449`, timestamp
`2012-08-04T17:33:29Z`, establishes item 3053's Attack-30 and Magic-30 gates,
five-tick weapon speed, bonuses, and Infernal Mage acquisition:
<https://runescape.wiki/w/Lava_battlestaff?oldid=6037449>.

RuneScape Wiki `Mystic hat`, oldid `5971728`, timestamp
`2012-07-22T01:55:15Z`, establishes the dark hat variant, Defence-20 and
Magic-40 gates, bonuses, and Infernal Mage acquisition:
<https://runescape.wiki/w/Mystic_hat?oldid=5971728>.

RuneScape Wiki `Mystic boots`, oldid `6315992`, timestamp
`2012-09-28T21:49:58Z`, establishes the dark boots variant, Defence-20 and
Magic-20 gates, bonuses, and Infernal Mage acquisition:
<https://runescape.wiki/w/Mystic_boots?oldid=6315992>.

The matching 2011Scape equipment blocks provide the exact bonus vectors.
`tools/generate_equipment_data.py` owns all three rows so regeneration remains
byte-stable.

## Asset boundary

`combatenemies/infernal_mage.png`,
`combatitems/lava_battlestaff.png`,
`combatitems/mystic_hat_dark.png`, and
`combatitems/mystic_boots_dark.png` use OSRS Wiki renders. Their upload
timestamps postdate the cutoff, so they are visual-only and are not cited as
historical evidence. Exact URLs, timestamps, and hashes are recorded in
`assets_provenance.json`.

## Live mapping

The standard Combat runtime handles the Slayer gate/XP, Magic defence roll,
six-tick pacing, four independent drop selections, inventory capacity, undo,
and death paths. The Combat picker exposes Magic attacks, maximum hit, all
four table denominators, the rare equipment, and the target sprite.

`tools/audit_slayer_readiness.py` derives Vannaka at 19/35. Sixteen blockers
remain: 15 missing Combat representatives plus Wilderness-risk behavior for
the existing Earth warrior. The incomplete role stays hidden and its
assignment weights are not renormalized. No owner-facing design fork emerged.

## Verification

Focused pure coverage passes all 321 checks, the real offscreen Qt Combat
picker regression passes, and both ordinary and offscreen full discovery pass
all 1,604 tests with 214 declared environment skips. Equipment regeneration is
byte-stable. Test quality reports zero hard issues and only the four preexisting
clone groups; documentation, JSON, compilation, readiness, diff, and
worktree-safety checks pass. The expected reachability debt ledger remains
1,231 actions, now with 1,820 reachable items, 285 orphan inputs, and 311
blocked actions.

Results:
`memory-bank/status-updates/slayer-infernal-mage-results-2026-07-18.html`
(<https://6zhziqqts1l7.postplan.dev>).
