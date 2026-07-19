# Dungeoneering Product Decision — Deferred

> **Superseded 2026-07-18:** the session model is now owner-ratified in
> `dungeoneering-design-contract-2026-07-18.md`, which answers the six
> questions below. The Herblore quarantine holds until that contract's
> runtime exists.

## Current Boundary

Dungeoneering is not an overworld Herblore source. The ordinary Herblore catalog therefore excludes all 54 Daemonheim-only targets transcribed from the local source: nine clean herbs, nine unfinished potions, and 36 tiered finished potions. Their source rows and item identities remain registered for save compatibility, but no normal review action can select or process them.

The isolated herb families are sagewort (the source/runtime id retains the `sagawort` spelling), featherfoil, valerian, aloe, wormwood leaf, magebane, winter's grip, lycopus, and buckthorn.

## Why This Is Not Just Another Skill Row

Daemonheim uses a temporary closed economy. Adding its herbs to the persistent Bank and ordinary Herblore loop erases the defining boundary between dungeon-session resources and overworld items. A valid Dungeoneering implementation must decide the session model before any of those targets return to a player-facing catalog.

## Questions for the Future Dungeoneering Contract

1. What starts, advances, completes, and abandons a dungeon session in review terms?
2. Which inventory, equipment, and skill boosts are temporary, and what—if anything—can cross the session boundary?
3. How are floor complexity, party assumptions, rooms, keys, combat, and skilling gates represented without building a world simulator?
4. How are Dungeoneering XP, tokens, rewards, and persistent unlocks separated from temporary floor loot?
5. Does Herblore appear as a floor-local action family inside the Dungeoneering surface, or through a shared session-scoped action engine?
6. How do undo, target switching, save/load, and interrupted reviews restore an in-progress dungeon atomically?

Until those questions are closed, `DUNGEONEERING_HERBLORE_TARGETS` is source evidence and compatibility data only—not live gameplay.
