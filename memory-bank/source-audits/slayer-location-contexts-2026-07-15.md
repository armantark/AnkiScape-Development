# Slayer location-context reconnaissance — 2026-07-15

Status: **Kuradal's Dungeon and ferocious-ring period behavior pinned; broader
Slayer-area registry remains open**.
Cutoff: `2012-11-20T00:00:00Z`.

## Primary period revisions

- RuneScape Wiki, `Kuradal's Dungeon`, oldid `6516655`, timestamp
  `2012-11-01T19:53:54Z`:
  <https://runescape.wiki/w/Kuradal%27s_Dungeon?oldid=6516655>.
- RuneScape Wiki, `Ferocious ring`, oldid `6547685`, timestamp
  `2012-11-11T04:20:35Z`:
  <https://runescape.wiki/w/Ferocious_ring?oldid=6547685>.

Both historical wikitext revisions were read through the MediaWiki revisions
API. They predate the cutoff and supersede modern summaries where the mechanic
changed presentation.

## Period dungeon rules

- Entry requires a current Kuradal assignment for a monster present in the
  dungeon. The player may attack only the assigned monster and only until the
  task completes.
- Kuradal requires 75 Slayer and 110 Combat before assigning her tasks.
- Dwarf multicannons are forbidden in the dungeon.
- The period monster roster is hellhounds, greater demons, blue dragons,
  gargoyles, abyssal demons, dark beasts, iron dragons, and steel dragons.
- Every monster in the dungeon can drop a ferocious ring, with monster-specific
  rarity labels in the ring revision. Exact roll denominators remain open.
- The source lists 86- and 90-Agility shortcuts. They are not separate Slayer
  training actions; their route-value treatment belongs to the cross-skill
  Agility/Slayer context audit.

## Period ferocious-ring rules

- The ring has five teleport charges, each taking the player to Kuradal.
- While worn in Kuradal's Dungeon, every successful hit receives a fixed
  **+40 life points** after the Slayer-helmet/black-mask boost. A miss receives
  no bonus. The period rule is not the modern shorthand `+4% damage`.
- While worn in the dungeon, falling below 10% of maximum life points while
  remaining above zero triggers its ring-of-life effect. The encounter ends
  safely and the ring is destroyed regardless of remaining charges. A lethal
  hit that crosses directly to zero still kills the player.
- Spending the fifth charge makes the ring disappear, so no zero-charge passive
  item remains.
- Multiple rings may be owned; partially charged rings can be combined through
  the period Murky Matt operation. Combining reduces the number of independent
  emergency saves because the entire triggering ring is destroyed.

## AnkiScape mapping

Under Owner decision 14, `Kuradal's Dungeon` is a target-local Combat context,
not global player location. Its task, master, level, monster-roster, cannon, and
equipment rules bind to the encounter. Purely duplicate appearances elsewhere
do not become new targets.

The five charged teleports use the same mapless transport seam as Owner decision
11: one charge erases the abstract run-energy cost of entering the eligible
Kuradal context. The fixed +40 successful-hit modifier is applied inside each
atomic Combat burst. The emergency effect atomically destroys the worn ring,
ends the encounter as a retreat, and avoids grave/death processing; it consumes
no extra review because it is a reactive source effect. All of those mutations
roll back with review undo.

The first four charge states require distinct item identities or charge data;
the fifth teleport removes the item. Charge combining is an instantaneous,
review-free inventory operation with its own manual undo record.

## Remaining context audit

Before implementation closes, enumerate every cutoff-live Slayer area and keep
a separate context only where source mechanics differ. Reconcile at least access
gates, task-only attack rules, protection/equipment effects, cannon rules,
context-specific drops, dangerous-area risk, trip-energy inputs, shortcuts, and
ring destinations. Exact values without qualifying evidence remain
`source_blocked`; absence of a number does not erase an attested mechanic.
