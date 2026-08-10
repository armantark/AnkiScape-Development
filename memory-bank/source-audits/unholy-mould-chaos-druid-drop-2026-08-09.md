# Unholy mould Chaos-druid drop audit — 2026-08-09

## Scope and verdict

This slice closes the ordinary acquisition route for `Unholy mould`. The item
and complete unholy-symbol Crafting chain already existed, but the only mould
image was an incorrect reuse of the Holy mould sprite and no live action
supplied the item.

**Verdict:** Chaos druids drop one Unholy mould on one slot of their 128-slot
ordinary table. The established Combat path now supplies the mould, and the
existing level-17 Crafting recipe preserves it as a reusable tool while it
consumes one Silver bar. No placeholder or new interaction pattern is needed.

## Period evidence

### Chaos-druid drop

- RuneScape Wiki `Chaos druid`, oldid `6381798`, timestamp
  `2012-10-10T23:46:25Z`:
  <https://runescape.wiki/w/Chaos_druid?oldid=6381798>.
- The cutoff monster table pins combat level 13, 200 life points, guaranteed
  Bones, and one Unholy mould at `Rare` rarity.
- Darkan commit `9a6db4df8d12a743d0318bcd524462512e838ff3`, file
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/chaos_druid.json`,
  independently reconstructs item `1594`, quantity one, at `1/128`. Its table
  accounts for 96 occupied slots, leaving 32 empty slots.

### Item identity and use

- RuneScape Wiki `Unholy mould`, oldid `6088663`, timestamp
  `2012-08-14T01:36:26Z`:
  <https://runescape.wiki/w/Unholy_mould?oldid=6088663>.
- The cutoff item page pins the mould as non-tradeable, non-stackable, usable
  with a Silver bar at a furnace, and a rare Chaos-druid drop. It separately
  records the Spirit of Scorpius route after Observatory Quest.
- OpenRS2 revision 742, dated `2012-11-07`, identifies item `1594` as
  `Unholy mould`, model `2673`, non-stackable and non-exchangeable, with
  `Add-to-toolbelt` and `drop` options. The exact query was:

```text
tools/query_openrs2_cache.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache' --id 1594
```

## Product translation

- The existing Chaos-druid main table remains exactly 128 slots. One empty
  slot becomes `Unholy mould ×1`, reducing its empty span from 33 to 32.
- The row reuses the complete Combat target, kill, loot, carried inventory,
  persistence, telemetry, and answer-undo mechanics.
- The existing `silver_unstrung_emblem` Crafting recipe consumes one Silver
  bar, awards 50 XP, produces one Unstrung emblem, and preserves the mould as
  a required reusable tool.
- The graph changes from 1,551 actions / 2,425 reachable items / 110 orphan
  inputs / 110 blocked actions to 1,551 / 2,428 / 108 / 108. The three newly
  reachable states are Unholy mould, Unstrung emblem, and Unholy symbol.

## Asset correction

`crafteditems/unholy_mould.png` is the tightly cropped source-period sprite:

- source upload timestamp: `2011-11-30T05:37:48Z`
- source SHA-1: `6eaa27aad298f1e472a9b38f15d3d4063e9f1af5`
- normalized dimensions: 31×27 pixels
- archive URL:
  <https://runescape.wiki/images/archive/20140502072859%21Unholy_mould.png?e24f9>

The item registry and Bank now use this sprite instead of the visually and
semantically incorrect `holy_mould.png` fallback.

## Explicit omissions

- The Spirit of Scorpius quest reward remains owned by the Observatory Quest
  lane. It is an alternate acquisition route, not a dependency of the monster
  drop.
- Other monster sources remain catalog depth.
- This slice does not change the existing Chaos-druid combat formula or its
  other reconstructed drops.
- The source period permits adding the mould to the toolbelt. The existing
  required-item model preserves it during Crafting; a generic mould-toolbelt
  expansion is separate shared-system depth.

## Acceptance contract

- The Chaos-druid table must still sum to 128 slots and must roll one mould on
  its sourced slot.
- A real Combat burst must be able to produce the mould, and the real Crafting
  reducer must then produce an Unstrung emblem without consuming the mould.
- Reachability must name `combat:chaos_druid` and remove the mould and its
  existing downstream chain from orphan debt.
- The item registry and real offscreen Qt Bank must render the distinct period
  mould sprite.
- Focused Combat, Crafting integration, registry, reachability, asset, and Qt
  checks plus both full discovery lanes must pass before closure.
