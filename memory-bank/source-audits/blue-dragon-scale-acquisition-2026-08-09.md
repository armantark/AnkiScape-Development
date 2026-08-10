# Blue dragon scale acquisition — 2026-08-09

## Scope

This slice closes the ordinary acquisition root for `Blue dragon scale`, which
already feeds the live `Dragon scale dust` grind and the Weapon poison and
Antifire Herblore recipes. It adds no new gathering substrate, travel system,
or wall-clock respawn model.

## Period evidence

RuneScape Wiki [Blue dragon scale oldid
6169064](https://runescape.wiki/w/Blue_dragon_scale?oldid=6169064), dated
2012-08-31T09:15:03Z, states that the item is members-only, tradeable,
non-stackable, and not quest-bound. Its acquisition section gives two Taverley
Dungeon locations:

- seven ground spawns in the ordinary blue-dragon enclosure, reachable with a
  Dusty key or the level-70 Agility pipe;
- twelve ground spawns in the level-60 Dungeoneering resource dungeon inside
  that enclosure.

The same revision states that a pestle and mortar converts the scale into
`Dragon scale dust`, which is used for Weapon poison and Antifire potions.
AnkiScape's existing grind and Herblore rows already implement those 1:1 and
recipe transitions. The period Grand Exchange records generated from cutoff
item data identify `Blue dragon scale` as item 243 and `Dragon scale dust` as
item 241.

## AnkiScape translation

`Gather blue dragon scales` is a zero-XP Utility gathering row. One successful
review represents the ordinary Dusty-key enclosure route and grants the seven
spawns stated by the cutoff page. The Dusty key is readily obtainable without
a quest or skill requirement; excluded world travel and door geometry are not
turned into an inert key-acquisition subsystem. The level-60 Dungeoneering
resource dungeon remains an optional higher-yield route, not the baseline.

The row reuses the established no-material gathering path, including selector
metadata, persistence, review cadence, telemetry, and answer undo. It uses
distinct tightly cropped period sprites:

- `herbloreitems/blue_dragon_scale.png`, file revision
  2010-04-28T16:12:41Z, SHA-1
  `e7316f6605d27670a299afc51b82d98d95e3097b`;
- `herbloreitems/dragon_scale_dust.png`, file revision
  2011-11-20T06:43:43Z, SHA-1
  `251a67fb242b749fd1a260dc0ae724eda2786d73`.

## Explicit omissions

- No wall-clock ground-spawn respawn timer or banking duration is modeled.
- The optional resource-dungeon route and Ancient-ranger drop are catalog
  depth; neither is needed to make the ordinary acquisition chain live.
- The nearby dragon danger is not converted into ambient damage. The selected
  action represents collecting the ground spawns through the ordinary route,
  while Combat remains an explicit target family.
- No placeholder value is introduced: the baseline trip quantity is stated
  directly by the cutoff page.

## Verification

- Focused logic, registry, metadata, runtime undo, and reachability coverage
  passes 314 tests. The established Utility selector passes one focused real
  offscreen Qt test.
- Full plain discovery passes 4,006 tests in 268.677 seconds with 488 expected
  environment skips. Full real offscreen Qt discovery passes the same 4,006
  tests in 614.418 seconds with three intentional skips.
- Both sprites are tightly cropped; the Herblore asset family reports zero
  files requiring normalization.
- Reachability improves to 1,548 actions, 2,377 reachable items, 137 orphan
  inputs, and 148 blocked actions. The one acquisition row therefore closes 23
  downstream item paths and 31 blocked actions through the existing grind and
  Herblore graph.
- Native Anki inspection was attempted first by display name and then by bundle
  id `net.ankiweb.launcher`; Computer Use returned exact error
  `Computer Use server error -10005: timeoutReached` both times. Native
  interaction is not claimed. Manual acceptance is to open Utility → Gathering,
  confirm one enabled `Gather blue dragon scales` row with the scale sprite and
  `Processes up to 7` tooltip, answer one card while selected, verify seven
  scales appear, and undo the answer to restore the prior inventory.
