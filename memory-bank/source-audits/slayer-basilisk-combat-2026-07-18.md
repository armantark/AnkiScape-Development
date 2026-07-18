# Slayer Basilisk Combat closure

Date: 2026-07-18

Status: **the ordinary level-61 Basilisk is executable and advances Vannaka to
20/35.**

## Cutoff identity

RuneScape Wiki `Basilisk`, oldid `6565796`, timestamp
`2012-11-17T10:10:58Z`, establishes:

- combat level 61, 750 lifepoints, Slayer 40, and 75 Slayer XP;
- six-tick melee attacks with a normal maximum hit of 59;
- Vannaka, Sumona, and Chaeldar assignment membership;
- guaranteed Bones; and
- the equipped Mirror-shield requirement even while safespotted.

Without the shield, the page records a 120-LP maximum hit and strong stat
reduction. Protect from Melee blocks the damage but not the stat drain:
<https://runescape.wiki/w/Basilisk?oldid=6565796>.

Literal wikitext was read through the RuneScape Wiki revisions API. The page's
`{{Charm:Basilisk}}` transclusion no longer has recoverable historical template
content, so exact charm distribution remains `source_blocked`.

## Combat reconciliation

Darkan
`data/npcs/combatdefs/uncategorized/basilisk.json`
corroborates 750 LP and maximum hit 59 and supplies Attack 30, Strength 45,
Defence 75, Magic/Ranged 1, and a 59-tick respawn.

Darkan
`src/main/java/com/rs/game/content/skills/slayer/npcs/combat/Basilisk.java`
supplies the smallest surviving unprotected formula: a fixed maximum-LP/10 hit
and one randomly selected combat stat reduced by five. AnkiScape caps that
damage at the period-proven 120 LP and lets Protect from Melee reduce the
damage while the drain still lands. The random stat set is Attack, Defence,
Strength, Ranged, Prayer, and Magic, floored at one.

The exact historical drain magnitude and selection rule remain
`source_blocked`; the Darkan mapping is labeled `abstraction/darkan`, not
claimed as exact 2012 parity. The ordinary shielded attack continues through
the standard accuracy and protection-prayer path.

## Drops and items

Darkan `data/npcs/drops/basilisk.json` supplies three independent tables:

- a 128-slot ordinary table with 127 named slots and one explicit empty slot;
- Mystic hat (light) at 1/512; and
- Basilisk head at 1/2,000.

The ordinary table includes the 35-slot minor-herb roll, five-slot gem roll,
coins, runes, metal equipment, and Adamantite ore. Guaranteed Bones remain
separate. No charm row is fabricated.

The primary 2011Scape `data/cfg/items.yml` item 4109 supplies the light Mystic
hat's Defence-20/Magic-20 requirements and exact bonuses.
`tools/generate_equipment_data.py` owns the row so regeneration is byte-stable.

The same config identifies Basilisk head as non-stackable, untradeable item
7977. Its existing Construction trophy-head registration and image are reused;
the Combat metadata corrects the older generic material defaults rather than
creating a duplicate storage key.

## Runtime mapping

The existing protective-equipment schema now supports the source distinction
between prayer-blockable unprotected damage and an unavoidable stat drain.
Cockatrice retains its existing prayer-bypassing eye-beam behavior. Basilisk's
random-one drain consumes one explicit combat RNG draw per unprotected attack,
so review undo restores the complete LP/stat/RNG outcome atomically.

The Combat picker exposes the shield warning, player-scaled unprotected hit,
three drop tables, and target icon. `tools/audit_slayer_readiness.py` derives
Vannaka at 20/35. Fifteen blockers remain: 14 missing Combat representatives
plus Wilderness-risk behavior for the existing Earth warrior. The incomplete
role remains hidden and unrenormalized. No owner-facing design fork emerged.

## Asset boundary

`combatenemies/basilisk.png`,
`combatitems/mystic_hat_light.png`, and the reused
`constructionitems/basilisk_head.png` use current RuneScape/OSRS Wiki renders.
Their upload timestamps postdate the cutoff, so they are visual-only and are
not cited as historical evidence. Exact URLs, timestamps, and hashes are
recorded in `assets_provenance.json`.

## Verification

Focused pure coverage passes all 321 checks, the real `.venv-qt` offscreen
Combat picker regression passes, and full pure discovery passes all 1,607
tests with 214 declared environment skips. Final generator, quality,
documentation, readiness, provenance, reachability, compilation, diff, and
worktree checks pass. Test quality reports zero hard issues and only the four
preexisting clone groups. The expected reachability debt ledger remains 1,231
actions, now with 1,822 reachable items, 285 orphan inputs, and 311 blocked
actions.

Results:
`memory-bank/status-updates/slayer-basilisk-results-2026-07-18.html`
(<https://12bv7z5x53a2.postplan.dev>).
