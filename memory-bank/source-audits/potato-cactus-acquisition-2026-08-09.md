# Potato cactus acquisition — 2026-08-09

## Scope

This slice closes the ordinary acquisition root for `Potato cactus`, which
already feeds the live Magic potion Herblore chain and existing item consumers.
It adds no new gathering substrate, travel system, persistent location, or
wall-clock respawn model.

## Period evidence

RuneScape Wiki [Potato cactus oldid
6543078](https://runescape.wiki/w/Potato_cactus?oldid=6543078), dated
2012-11-08T16:04:19Z, identifies the item as members-only, tradeable,
non-stackable, and not quest-bound. Its obtaining section states that the
Kalphite Hive has fourteen spawns split across three floors: three on the first
level, seven beside the Kalphite Queen on the second, and four on the
quest-gated third level. It also states that the first-level spawns are in the
south-west Kalphite Soldier room and warns that those soldiers are poisonous.

RuneScape Wiki [Kalphite Hive oldid
6529999](https://runescape.wiki/w/Kalphite_Hive?oldid=6529999), dated
2012-11-03T23:29:19Z, independently confirms three Potato-cactus spawns on the
first level. It states that a rope is installed on the main entrance only on
the first visit and remains there for unlimited later uses. The second rope,
Kalphite Queen room, and Do No Evil passage are not part of the first-level
route.

The period Grand Exchange record [Exchange:Potato cactus oldid
6571111](https://runescape.wiki/w/Exchange:Potato_cactus?oldid=6571111), dated
2012-11-18T04:59:09Z, identifies Potato cactus as item 3138. The existing
Herblore table consumes one Potato cactus when making a level-76 Magic potion.

## AnkiScape translation

`Gather potato cacti` is a zero-XP Utility gathering row. One successful review
represents the ordinary first-level gathering trip and grants the three spawns
stated by both cutoff pages. This follows the existing source-gathering
abstraction: excluded world travel, one-time route setup, and nearby hostile
NPCs are not turned into partial location or ambient-combat systems.

The row inherits the established Utility selector, saved target, review
cadence, telemetry, and answer-undo behavior. It reuses
`summoningitems/potato_cactus.png`, whose source file revision is dated
2010-10-05T01:18:49Z in `assets_provenance.json`. The normalized local sprite is
26×22 pixels with SHA-1 `55901dce9ded294412c005d5bdd76f7480e995b3`.

## Explicit omissions

- No wall-clock ground-spawn respawn timer, banking duration, or persistent
  installed-rope state is modeled.
- The seven second-level spawns and four Do No Evil-gated third-level spawns
  are catalog depth, not part of the baseline route.
- Poison, desert heat, and hostile Kalphites are not converted into ambient
  damage. Combat remains an explicit target family, matching the existing
  source-gathering abstraction.
- Soul Wars gambling, Spirit implings, Familiarisation, and monster drops remain
  alternative sources; none is required to make the ordinary item chain live.
- No placeholder value is introduced. The trip quantity is stated directly by
  two cutoff pages.

## Verification

- Five focused logic, registry, metadata, runtime-undo, and reachability checks
  pass. The established Utility selector passes one focused real offscreen Qt
  interaction test.
- Full plain discovery passes 4,009 tests in 235.698 seconds with 488 expected
  environment skips. Full real offscreen Qt discovery passes the same 4,009
  tests in 595.735 seconds with three intentional skips.
- Documentation audits 546 Markdown and 431 HTML files. Test quality reports
  zero hard issues across 3,974 tests in 181 files. Compilation, JSON, diff,
  and worktree-safety gates pass.
- All 229 Summoning-family sprites are already tightly cropped; the Potato
  cactus sprite's alpha bounds equal its full 26×22 canvas.
- Reachability improves from 1,548 actions / 2,377 reachable items / 137 orphan
  inputs / 148 blocked actions to 1,549 / 2,397 / 124 / 129. The one source row
  therefore recovers 20 item paths and removes 19 blocked actions.
- Manual acceptance is to open Utilities → Gathering, confirm one enabled
  `Gather potato cacti` row with the period sprite and `Processes up to 3`
  tooltip, answer one card while selected, verify three Potato cacti appear,
  and undo the answer to restore the prior inventory.
