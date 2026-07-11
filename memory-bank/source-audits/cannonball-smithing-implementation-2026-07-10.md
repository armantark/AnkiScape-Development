# Cannonball Smithing implementation audit — 2026-07-10

## Scope

This audit closes only the cannonball sub-slice of the broader Blast Furnace / Goldsmith gauntlets / cannonballs backlog family. Blast Furnace routing, fees, coal savings, and Goldsmith-gauntlet XP remain source-gated and unimplemented.

## Pinned pre-EOC evidence

- RuneScape Wiki revision: `https://runescape.wiki/w/Cannonball?oldid=6541276` (7 November 2012).
- The archived page requires level 35 Smithing and completion of Dwarf Cannon.
- One Steel bar is used with an Ammo mould to make four Cannonballs.
- The action awards 25.6 Smithing XP per Steel bar.
- The 2012 cache item configuration corroborates Cannonball item ID `2` and Ammo mould item ID `4`.

## Implemented contract

- `forge_cannonballs` is a distinct furnace-process target, not an anvil-forging or ordinary bar-smelting row.
- Each review consumes one Steel bar, produces four Cannonballs, and awards 25.6 Smithing XP.
- Dwarf Cannon completion is an authentic target lock and is enforced both when selecting and resolving the action.
- Ammo mould is a presence-only tool. Casual mode checks banked ownership; Advanced mode requires it in the target's carried layout and retains it after processing.
- The target row exposes the quest requirement, mould requirement, output quantity, and source-backed icon.
- Review undo restores the Steel bar and XP and removes the four Cannonballs while preserving the mould.

## Exclusions

No Blast Furnace or Goldsmith-gauntlet values were inferred from the cannonball evidence. Those mechanics remain blocked pending separately pinned pre-EOC evidence and the high-fidelity Darkan pass.

