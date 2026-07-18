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
| Pyramid Plunder | Requires level 21 Thieving and access to Sophanem: either `Icthlarin's Little Helper` started or a Pharaoh's sceptre that bypasses that quest route. Rooms require exact Thieving levels `21/31/41/51/61/71/81/91`; the engraved sarcophagus in room eight additionally requires 75 Runecrafting. `Contact!` and `The Feud` benefits are recommendations/unlocks, not entry gates. | Pinned cutoff page `Pyramid Plunder` oldid `6529238` (`2012-11-03T18:18:22Z`) and carried into the focused loop contract. |
| Sorceress's Garden | Requires completion of `Diamond in the Rough`, the one-time Osman/apprentice introduction, and exact seasonal Thieving levels `1/25/45/65`. | Level gates and introduction pinned in `Sorceress's Garden` oldid `6466752` (`2012-10-24T20:04:59Z`). Period documentation leaves the removed-quest migration unresolved; the owner supplied high-confidence firsthand cutoff memory that `Diamond in the Rough` inherited the prerequisite, consistent with the later article. Product gate closed; period-source gap remains explicit. |
| Flash Powder Factory | Requires unboosted level 75 Thieving, level 75 Agility, and level 50 Herblore. A skulled player or one accompanied by a familiar or pet cannot enter. Rogue/Factory top and the other Factory pieces modify the session after entry rather than unlocking it. | Pinned in `Flash Powder Factory` oldid `6559970` (`2012-11-15T19:17:32Z`) and carried into `flash-powder-factory-loop-2026-07-18.md`; hidden rolls remain open. |
| The Pit | An ordinary invitation can trigger only after a completed lap at Gnome basic/advanced, Barbarian basic/advanced, Pyramid, Ape Atoll, Wilderness, Werewolf, or Dorgesh-Kaan. Entry requires free hands and no familiar. Burthorpe, Penguin, non-lap Activities, shortcuts, and incidental actions cannot trigger an ordinary invitation. Skillcape practice is its separate source route. | Pinned in `The Pit` oldid `6551042` (`2012-11-13T04:44:38Z`) and `Talent scout` oldid `6448152` (`2012-10-21T02:21:10Z`), reconciled in `the-pit-loop-2026-07-18.md`. |
| Managing Miscellania | Requires completion of `Throne of Miscellania`. `Royal Trouble` automatically expands the workforce and coffer/salary limits; it is not required for the base Activity. Fremennik-task benefits and flatpack deposits modify management after entry rather than unlocking it. | Pinned in `Managing Miscellania` oldid `6500793` (`2012-10-30T06:29:55Z`) and carried into `managing-miscellania-loop-2026-07-18.md`; exact task/flatpack effects remain in the source harvest. |
| Vinesweeper | Requires a spade, including the tool-belt spade. The Tool-Leprechaun teleport becomes the Activity's direct location transition. An active familiar or pet invokes the shared dismissal confirmation because followers cannot enter. No skill, quest, ticket, or recurrence gate is added. | Pinned in `Vinesweeper` oldid `6288368` (`2012-09-24T04:55:21Z`) and closed in `vinesweeper-loop-2026-07-18.md`; hidden outcome weights remain source-blocked. |
| Big Chinchompa | No level, quest, item, or currency gate is added. The eight moth tiers become eligible at Hunter levels `1/13/26/39/52/65/78/91`; lower Hunter changes the available output rather than hiding the event. Eligibility is twice per 240-card simulated day, and late entry retains only the remaining source-shaped event window. | Pinned in `Big Chinchompa` oldid `6538836` (`2012-11-06T10:56:45Z`) and closed in `big-chinchompa-loop-2026-07-18.md`; hidden server rolls remain source-blocked. |

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
