# Slayer Rockslug and Gargoyle Combat reconciliation — 2026-07-17

Status: **runtime-complete pending closure verification**.
Cutoff: `2012-11-20T00:00:00Z`.

## Evidence and conflict policy

Direct cutoff pages determine identity, Slayer gates, finishing items, finishing
windows, consumption, and target-specific behavior:

- `Rock slug`, oldid `6530509`, timestamp `2012-11-04T05:20:18Z`:
  <https://runescape.wiki/w/Rock_slug?oldid=6530509>.
- `Gargoyle`, oldid `6579781`, timestamp `2012-11-19T03:45:52Z`:
  <https://runescape.wiki/w/Gargoyle?oldid=6579781>.

The local 2011Scape plugins and Darkan data reconstruct exact Combat and drop
rows:

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/rockslug_lvl_29.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/gargoyle_lvl_111.plugin.kts`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/rockslug.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/gargoyle.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/rockslug.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/gargoyle.json`

Where reconstruction conflicts with a direct cutoff page, the cutoff page wins.
This changes 2011Scape's Rockslug `50` finishing threshold to `39`, its Gargoyle
`100` threshold to `89`, and its Gargoyle attack speed `4` to the cutoff
infobox's `6`. Darkan's respawn value `59` is retained. The Darkan ordinary
drop rows are used because they preserve cutoff-listed Rune essence for
Rockslug and Mithril bars for Gargoyle. The 2011Scape charm tables are separate
Summoning-era rolls.

## Rockslug

The live row is level 29, Slayer 20, 270 LP, maximum hit 41, Attack 22,
Strength 27, Defence 27, and 27 Slayer XP. The 2011Scape plugin supplies attack
speed 4 and crush style.

The cutoff page establishes:

- Bag of salt is consumed on a successful finishing blow at 1–39 LP.
- Early use consumes the bag without effect.
- Ordinary damage cannot kill the target.
- At 10 LP the Rockslug becomes frozen and cannot move or retaliate, even if
  later restored above 10 LP.

AnkiScape keeps the existing misclick-safe rule: the manual action is disabled
outside the valid window, so it does not expose the source's waste-only early
use. Lethal damage holds the target at 1 LP until a manual finisher or the
400-point quick-finisher unlock succeeds. The frozen state is represented by a
data-driven retaliation stop at 10 LP; it does not use wall-clock state.

The live drop model has one exact 100,000-slot Darkan selector containing all
20 accepted rows, with seven empty slots, plus the separately sourced
2011Scape charm selector. It includes Rune essence and excludes unsupported
qualitative-only rarities whose exact runtime probability is not available.

## Gargoyle

The live row is level 111, Slayer 75, 1,050 LP, maximum hit 119, Attack 75,
Strength 105, Defence 107, Magic 1, Ranged 1, and 105 Slayer XP. The cutoff
infobox supplies attack speed 6. Reconstruction supplies the four 20-point
stab/slash/magic/ranged defence bonuses and Darkan's 59-tick respawn.

The cutoff page establishes:

- A Rock hammer finishes the target below 90 LP.
- The hammer is reusable.
- The manual Smash action is available within the finishing window.
- The 400-point quick-finisher still requires the hammer.
- Gargoyles restore about 20 LP per five seconds.

Regeneration is represented as the exact gameplay-tick equivalent `12/5` LP
per 0.6-second tick. The integer residual persists across review boundaries,
so two adjacent Combat reviews equal one combined tick slice. No wall clock is
read. Manual and automatic finishers retain the one loaded non-stackable Rock
hammer.

The live drop model has one exact 512-slot Darkan selector containing the 21
item rows, the 5/128 gem-table branch, and one empty slot, plus the separately
sourced 2011Scape charm selector. The Kuradal's-Dungeon-only Ferocious ring is
explicitly absent from this ordinary target. This preserves the existing
context-specific exclusion rather than leaking the ring globally.

The initial independent-row interpretation was incorrect. Both corrected
selectors follow the executable loader proven in
`slayer-darkan-drop-selector-correction-2026-07-18.md`.

## Assets and UI

Both 48px target images come from cutoff-era RuneScape Wiki icon files:

- `Rock slug icon.png`, current source revision timestamp
  `2011-11-27T19:21:04Z`.
- `Gargoyle icon.png`, source file history includes the live
  `2011-01-28T23:53:48Z` revision.

`tools/fetch_combat_enemy_assets.py` now prefers the RuneScape Wiki before the
OSRS Wiki for Combat targets. This prevents an OSRS file with the same title
from silently replacing a period RuneScape asset.

The existing Combat selector exposes the target, icon, source level gate,
finishing window, loaded item count, and manual action. Its action tooltip now
distinguishes consumable finishers from reusable tools.

## Remaining boundary

Rockslug and Gargoyle are complete qualifying Combat variants and can satisfy
their family dependencies when a master pool is eventually certified. This
does not expose or renormalize an incomplete Slayer master. Mutated zygomite is
the remaining ordinary finishing-blow family without a reconciled live target.
