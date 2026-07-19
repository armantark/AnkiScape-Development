# Darkan quest handoff: Royal Trouble sea-snake access

Date: 2026-07-18  
Owner: Darkan quest-parity thread  
Consumer: Combat / Slayer Sea snakes

## Why this note exists

The ordinary Sea Snake Hatchling and Sea Snake Young are now playable Combat
targets. Their period pages place them in the Miscellania and Etceteria dungeon
and show that dungeon permission is granted during Royal Trouble, before quest
completion.

Combat deliberately uses the conservative `royal_trouble` completion gate
today. It did not add a parallel quest-stage interpretation because the Darkan
thread owns real 2012 quest parity.

## Requested quest-owned output

When Royal Trouble parity is finalized, expose one stable, persisted semantic
state meaning:

> The player has received permission to enter the Miscellania and Etceteria
> dungeon during Royal Trouble.

The exact quest step and storage shape remain Darkan-owned. Please document the
state in the quest contract and provide a stable query or named state that
other systems can consume without depending on generated stage numbers.

## Consumer follow-up

After that state lands, Combat should allow both sea-snake targets when either:

1. the dungeon-permission state is true; or
2. Royal Trouble is complete.

The mid-quest Sea Snake Young poison value is 78 LP; the completed-quest value
is 68 LP. AnkiScape's integer old-scale poison channel can represent these only
as 80 LP and 70 LP respectively, so any stage-aware follow-up must retain that
visible bounded abstraction.

Period evidence:

- <https://runescape.wiki/w/Sea_Snake_Young?oldid=5936978>
- <https://runescape.wiki/w/Miscellania_and_Etceteria_dungeon?oldid=6436494>

No other quest or Combat work is requested by this handoff.

