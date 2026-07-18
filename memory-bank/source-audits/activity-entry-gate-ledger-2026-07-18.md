# Activity Entry and Eligibility Gate Ledger

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **design coverage ledger; source conflicts and incomplete rows remain
explicit implementation blockers for those exact gates, not reasons to omit
the activities.**

## Gate policy

Every Activity, minigame, and D&D contract must record its source-owned entry,
unlock, item, currency, and recurrence gates. Implementation must enforce them
through the ordinary level, quest, inventory/equipment, wallet, and
answered-card-calendar facts already owned by AnkiScape. A dependency that is
not yet implemented remains an implicit gate and begins working automatically
when its real completion fact exists; it does not become a permanent
placeholder toggle or a visually disabled row that later needs cleanup.

Travel narration and source setup dialogue do not become gates unless they
change eligibility or consume a real resource. Recommended equipment is not an
entry requirement. A source conflict is written as `source_blocked`; it is
never silently replaced by a convenient modern rule.

## Recently grilled activities

| Activity | Entry and eligibility contract | Evidence state |
|---|---|---|
| Gnome Restaurant | The delivery service opens only after the one-time tutorial checklist records player production of the four prescribed dishes and four prescribed cocktails. Easy/hard customer-specific requirements remain part of assignment eligibility. | Structure pinned in `gnome-restaurant-delivery-loop-2026-07-17.md`; exact tutorial recipes, customer requirements, and corroboration remain open. |
| Penguin Hide and Seek | The base weekly roster is available without inventing a quest gate. `Cold War`, `Hunt for Red Raktuber`, and `Some Like It Cold` plus its `Desert Treasure` progress and ring-of-visibility requirement add their sourced point upgrades and extra agents. Weekly eligibility uses the answered-card calendar. | Pinned in `penguin-hide-and-seek-loop-2026-07-17.md`; independent corroboration and full roster harvest remain open. |
| Shattered Heart | Qualifying skill actions may produce rocks while collection is enabled. The optional collection bag must be obtained and carried to catch rocks without ordinary inventory replacement. Only placement of the final pair is weekly gated. | Pinned in `shattered-heart-loop-2026-07-17.md`; exact qualifying actions and roll rates remain open. |
| Big Top Bonanza | Magic, Ranged, and Agility performances are base weekly entries. `The Firemaker's Curse` unlocks the two Firemaking performances; `Some Like It Cold` unlocks the Thieving performance. Suggested trick levels affect performance outcomes but are not hard entry gates. | Pinned in `circus-performance-loop-2026-07-17.md`; trick tables and success/score model remain open. |
| Gnome Ball | Members-only dangerous activity. The pinned activity page states no level, quest, item, or currency entry requirement; the carried-gnomeball rule gates only whether another reward ball is issued. | Period structure pinned in `gnome-ball-loop-2026-07-17.md`; independent gate corroboration and equipment restrictions remain open. |
| Werewolf Skullball | Requires level 25 Agility, completion of `Creature of Fenkenstrain`, and an equipped Ring of Charos. | Pinned in `werewolf-skullball-loop-2026-07-17.md`; independent corroboration remains open. |
| Fishing Trawler | Requires level 15 Fishing. Swamp paste, rope, and reusable bailing buckets gate the duties the player can perform, not boarding itself. | Pinned in `fishing-trawler-computation-reconciliation-2026-07-17.md`; complete supply acquisition and independent gate corroboration remain open. |
| Fish Flingers | Requires one stored entry ticket. There is no level, quest, or item requirement. The source grants two tickets per source day, stores at most ten, and allows extra ticket acquisition; AnkiScape must translate the daily grant through its answered-card calendar rather than wall time. | Pinned in `fish-flingers-loop-2026-07-17.md`; exact calendar conversion and extra-ticket routes still need their implementation audit. |
| Pyramid Plunder | Requires level 21 Thieving and access to Sophanem: either `Icthlarin's Little Helper` started or a Pharaoh's sceptre that bypasses that quest route. Rooms require exact Thieving levels `21/31/41/51/61/71/81/91`; the engraved sarcophagus in room eight additionally requires 75 Runecrafting. `Contact!` and `The Feud` benefits are recommendations/unlocks, not entry gates. | Pinned cutoff page `Pyramid Plunder` oldid `6529238` (`2012-11-03T18:18:22Z`); the focused loop must be updated to carry the Sophanem and engraved-sarcophagus gates into implementation. |
| Sorceress's Garden | Seasonal gardens require exact Thieving levels `1/25/45/65`. Starting the activity also requires the one-time Osman/apprentice introduction state. The cutoff quest gate is `source_blocked`: `Prince Ali Rescue` oldid `6564887` records Garden access as a reward but also records that the quest was removed on `2012-09-26`; the Garden's cutoff page and its `2012-09-27` talk question do not resolve whether the replacement quests inherited the requirement. | Level gates and introduction pinned in `Sorceress's Garden` oldid `6466752` (`2012-10-24T20:04:59Z`). Talk oldid `6307582` (`2012-09-27T20:26:25Z`) records the unresolved migration question. A `Diamond in the Rough` requirement first appears in the wiki article after the cutoff and cannot independently close parity. |

## Implementation acceptance

For each activity implementation:

1. the Activity is absent from the selectable target list until its real entry
   facts are satisfied, unless the source explicitly exposes a visible locked
   entry;
2. optional unlocks appear automatically when their real quest/item facts
   become true;
3. a consumed ticket, item, or recurrence allowance is part of the same atomic
   delta as starting or completing the activity;
4. undo restores every gate resource and eligibility fact changed by that
   delta; and
5. tests cover the locked boundary, the first eligible boundary, optional
   unlock emergence, resource consumption, and undo without duplicating
   trivial catalog assertions.

This ledger is the cross-activity checklist. Each focused source audit remains
the authority for the activity's full loop and rewards.
