# Slayer Wall beast Combat audit — 2026-07-18

Status: **source closed for the ordinary level-49 representative**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Executable boundary

Admit the ordinary level-49 Wall beast as the executable representative for
Mazchna/Achtryn's Wall beasts assignment family. The Combat picker represents a
deliberate fight, not cave navigation, so the separate 110–180-LP
walking-past grab is not fired by selecting the target.

## Period evidence

RuneScape Wiki `Wall beast`, oldid `6079584`, timestamp
`2012-08-11T23:52:21Z`:
<https://runescape.wiki/w/Wall_beast?oldid=6079584>.

The cutoff revision records:

- Combat 49, 1,050 life points, Slayer 35, 105 Slayer XP, and Mazchna
  assignment membership;
- melee combat, a 44-LP maximum hit with the correct helmet, aggression,
  poison immunity, and no guaranteed drop;
- a Spiny helmet or equivalent as a literal requirement to **start** fighting;
- permission to swap to a Black mask, focus sight, or hexcrest once the Wall
  beast has discovered the protected player; and
- the need to re-equip a qualifying helmet after each battle.

The live runtime therefore uses a start-only head-slot gate. It deliberately
does not reuse the Banshee/Cockatrice `protective_equipment` channel, which
would incorrectly apply a consequence on every enemy attack. A started
encounter remains legal after the player swaps helmets. Once that beast dies,
the same review cannot chain into a fresh spawn without the helmet.

The period page names Spiny helmet, Spiked helmet, Slayer helmet, and Full
slayer helmet as equivalents. Only the source-backed `Spiny helmet` identity is
currently executable as an ordinary equipment item. The other equivalents
must be added to this tuple when their own acquisition/equipment routes become
live; accepting name-only placeholders would violate the item-registry
contract.

The cutoff revision does not state attack speed. The modern page reports a
four-tick attack and its update history records no attack-rate change. The
runtime admits four ticks as a stable lower-tier source fill rather than
inventing a new cadence.

## Emulator reconciliation

Darkan combat definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/wall_beast (noanims).json`

It supplies a 39-tick respawn, 1,050 life points, melee style, aggressive
behavior, and Attack 30, Strength 30, Defence 16, Magic 1, and Ranged 1. Its
40-LP maximum hit conflicts with the cutoff page's explicit 44-LP value, so
the period page controls that field.

Darkan drop definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/wall_beast.json`

The thirty mutually exclusive probability rows reconcile losslessly to a
100,000-slot table:

- thirteen rows at `3229/50000` become 6,458 slots each;
- three rows at `583/12500` become 4,664 slots each;
- six rows at `31/10000` become 310 slots each;
- eight rows at `23/100000` remain 23 slots each; and
- ten slots remain empty.

Repeated one-Bones rows are consolidated to 12,985 slots so the tooltip does
not repeat an identical reward. All other item identities and quantities stay
distinct. Cache IDs 4544 and 4089 resolve to the existing canonical
AnkiScape identities `Bullseye lantern (unf)` and `Mystic hat`; no duplicate
items are introduced. IDs 217, 221, and 2485 resolve to `Grimy dwarf weed`,
`Eye of newt`, and `Grimy lantadyme`. Every table output already exists in the
live item registry.

## Asset and runtime contract

The target image uses the `2011-11-30T12:36:55Z` revision of
`Wall beast icon.png`, fetched through the cutoff-aware asset pipeline.

The existing Combat selection, encounter persistence, death/grave, Slayer
credit, drop, achievement, persistence, and review-undo paths remain
authoritative. The source-backed poison immunity suppresses the extra poison
damage from already-live Ancient Smoke spells. Player weapon poison remains
outside the executable Combat contract.

No owner design decision is required.
