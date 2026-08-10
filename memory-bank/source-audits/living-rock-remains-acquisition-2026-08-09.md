# Living rock remains acquisition audit — 2026-08-09

Status: **implemented with one registered hidden-roll placeholder**.
Cutoff: `2012-11-20T00:00:00Z`.

This record supersedes only the implementation wait for Living rock remains in
`gap-grill-decisions-2026-07-10.md` and
`gap-grill-12-mining-provenance-2026-07-10.md`. Shooting Stars and later Living
Rock Caverns data depth remain unchanged.

## Period route

RuneScape Wiki `Living rock remains`, oldid `6556376`, timestamp
`2012-11-15`, pins the focused action row:

- Mining level 73;
- 25 Mining XP;
- a bundle of 5–24 Living minerals; and
- a one-minute custody delay before another player can mine a corpse.

Source: <https://runescape.wiki/w/Living_rock_remains?oldid=6556376>.

RuneScape Wiki `Living Rock Caverns`, oldid `6547876`, timestamp `2012-11-11`,
corroborates the level and XP, states that no quest or other requirement gates
the cavern, and describes both aggressive Living Rock creatures and public
corpse access. It gives a conflicting 5–20 mineral range.

Source: <https://runescape.wiki/w/Living_Rock_Caverns?oldid=6547876>.

The focused, newer remains page supplies the live 5–24 range. One answered
review represents finding an available public corpse and mining it. The period
one-minute custody delay is collapsed into that review; AnkiScape does not use
wall-clock gameplay. A self-killed corpse remains useful but is not an
artificial Combat prerequisite.

## Executable corroboration and hidden rolls

Darkan commit `3e5880517` restores Living Rock Caverns admission and corpse
custody. Its `Ore.LIVING_MINERALS` row independently reconstructs item `15263`,
level 73, 25 XP, a `30/145` success curve, and 5–20 minerals. The focused
cutoff page outranks that reconstruction for visible quantity, while Darkan is
the only executable evidence for the hidden success curve.

The live row therefore registers `mining.living_rock_remains_rolls`:

- success endpoints `30/145`; and
- a uniform inclusive draw across the focused page's `5–24` bundle.

A qualified period Mining routine would replace the hidden success endpoints
and the assumed distribution. Independent period evidence resolving 5–20
against 5–24 would retire the visible-range conflict.

## Item identity and art

OpenRS2 rev-742 pins Living minerals as item `15263`, model `48726`, stackable,
exchangeable, and droppable. The Mining row reuses the existing normalized
cutoff sprite at `fishingitems/living_minerals.png`. Its source revision has
timestamp `2012-10-18T21:54:58Z` and SHA-1
`2d0cabcc9d42634dceec0f7a61992ecb6a6b55fd`; the normalized local 24×15 file
has SHA-1 `a576925c48cafc31928d2698737a0604a4e8bdac`.

## Runtime boundary

The target reuses Mining's level/tool gate, success/failure reducer, carried
pack, cadence, telemetry, Shattered Heart replacement, persistence, and review
undo. The shared Mining output contract now supports an inclusive primary
quantity range and records the actual bundle in telemetry and achievement
progress. Existing single-output and weighted-output rocks remain unchanged.

No new UI pattern was added. The established Mining selector renders one row,
the Living minerals icon, the 5–24 output range, and 25 XP per action.

## Verification boundary

Focused data, pure reducer, runtime telemetry, reachability, loaded-add-on
review/undo, metadata, and real offscreen Qt selector checks exercise the live
route. The reachability graph now routes Living minerals through
`Mining:living_rock_remains`, activating the existing Rocktail input without
claiming a complete Living Rock Caverns danger or creature catalog.

The accepted closure passes 485 focused plain checks and one focused real
offscreen Qt check. Full discovery passes 4,029 tests in both lanes, with 491
expected plain skips and three Qt skips. Documentation passes across 554
Markdown and 431 HTML files; test quality reports zero hard issues across
3,994 methods in 181 files. Compilation, 26 tracked JSON files, placeholder,
asset-normalization, diff, reachability, and worktree audits also pass. Native
Anki interaction is not claimed.
