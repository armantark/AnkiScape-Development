# Slayer Dogs family: Jackal Combat audit — 2026-07-17

## Scope and decision

Admit the ordinary Jackal as the first executable representative of Slayer's
Dogs assignment family. This closes the missing Dogs-family Combat target for
Turael/Spria and Mazchna/Achtryn without claiming that every canine variant is
implemented or that either master pool is ready to ship.

## Period evidence

RuneScape Wiki `Jackal`, oldid `6493724`, timestamp
`2012-10-29T18:51:36Z`:
<https://runescape.wiki/w/Jackal?oldid=6493724>.

The cutoff revision records:

- combat level 21;
- 270 life points;
- Slayer level 1 and 27 Slayer XP;
- Turael and Mazchna assignment membership;
- melee attacks with an approximately 80 LP maximum hit;
- aggression, no poison, and a crush weakness;
- guaranteed Bones; and
- the explicit statement that Jackals count as Dogs for Slayer assignments.

The page's quest-only Jackal bone is not admitted to the ordinary drop table.
That transformation remains owned by the missing `Rag and Bone Man` quest.

## Emulator convergence

Darkan combat definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/jackal.json`

This independently supplies 270 LP, maximum hit 80, melee/stab identity,
Attack 17, Strength 18, Defence 15, Magic/Ranged 1, aggression, and a 59-tick
respawn delay.

Darkan drop definition:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/jackal.json`

This independently supplies the guaranteed item 526, one Bones.

The four-tick attack speed is a labeled compatibility value: the cutoff
revision does not expose the interval, while the surviving current monster row
still records speed 4 and it matches the ordinary Combat cadence used for
source-compatible melee NPCs. No hidden accuracy or defence bonus is invented;
the complete surviving level row drives the shared Combat formula.

## Runtime boundary

`jackal` is an ordinary, directly selectable Combat target. It uses the shared
combat, food, retreat, death, grave, drop, persistence, cadence, and undo paths.
The source maximum hit is declared explicitly rather than replaced by the
generic melee-strength derivation.

This slice certifies one Dogs-family representative only. Slayer assignment
generation remains closed until every family and required consequence in the
selected master's baseline pool is executable.
