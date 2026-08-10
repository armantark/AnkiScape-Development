# Darkan quest handoff: Emerald lens — 2026-08-09

## Goal

Add the Emerald lens to the Lunar Diplomacy ship checkpoint. Do not add a
generic item source.

## Context

AnkiScape already has the downstream item actions:

- `data/crafting_data.py` combines `Bullseye lantern (empty)` and
  `Emerald lens` into `Emerald lantern (unlit)`.
- `data/firemaking_data.py` lights item 9064 into item 9065.

The Emerald lens has no live source. This blocks three existing item states and
three actions in the AnkiScape reachability graph.

## Source facts

RuneScape Wiki `Emerald lens`, oldid `6202817`, timestamp
`2012-09-06T12:37:59Z`, states these facts:

- The item is a non-tradeable Lunar Diplomacy quest item.
- The Cabin Boy gives the item to the player.
- The player uses it on a Bullseye lantern or its frame.

Source: <https://runescape.wiki/w/Emerald_lens?oldid=6202817>.

RuneScape Wiki `Lunar Diplomacy`, oldid `6569662`, timestamp
`2012-11-17T22:55:10Z`, gives the exact sequence:

1. The player finds the Cabin Boy during the ship investigation.
2. The Cabin Boy gives a special lantern and lens.
3. The player makes and lights the Emerald lantern.
4. The player uses the lantern to find and remove five symbols.

Source: <https://runescape.wiki/w/Lunar_Diplomacy?oldid=6569662>.

OpenRS2 revision 742 pins these IDs:

| ID | Item |
| ---: | --- |
| 9064 | Emerald lantern, unlit, `Light` |
| 9065 | Emerald lantern, lit, `Extinguish` |
| 9066 | Emerald lens, non-stackable and non-exchangeable |

## Required Darkan result

1. Put the lens grant at the ship-investigation checkpoint before Lunar Isle.
2. Preserve the source lantern grant at the same checkpoint.
3. Require the Emerald-lantern sequence before the player clears the symbols.
4. Preserve item recovery if the player loses a required quest item.
5. Record the exact quest-state variables and cache IDs that Darkan uses.

Do not treat the Emerald lens as a final quest reward. Do not add it to a shop,
drop table, or repeatable generic action.

## Verification

Prove the first grant, loss recovery, lens conversion, lantern lighting, and
symbol checkpoint. Report the exact files and tests. State any omitted quest
state that remains unavailable.
