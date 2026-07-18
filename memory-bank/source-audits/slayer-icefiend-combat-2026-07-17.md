# Slayer Icefiend Combat audit — 2026-07-17

## Scope and decision

Admit the ordinary Ice Mountain level-13 Icefiend as the executable
representative of Slayer's Icefiends family. The God Wars, Ghorrock,
Temple-at-Senntisten, melting-quest, Revenant, and Daemonheim forms remain
distinct variants and are not silently folded into this target.

## Cutoff evidence wins the identity conflicts

RuneScape Wiki `Icefiend`, oldid `6419875`, timestamp
`2012-10-15T11:42:05Z`:
<https://runescape.wiki/w/Icefiend?oldid=6419875>.

The ordinary variant records:

- combat level 13;
- 150 life points;
- Slayer level 1 and 15 Slayer XP;
- Turael assignment membership;
- passive, non-poisonous melee combat;
- an approximately 20 LP maximum hit;
- Fire-spell and crush weaknesses; and
- guaranteed Impious ashes.

The same revision explicitly separates level 17/18 God Wars, level 132
Ghorrock, melting, and Daemonheim forms. Only the ordinary level-13 form
certifies this slice.

## Emulator reconciliation

game-main:

`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/demons/icefiend_level_13.plugin.kts`

This supplies NPC 7715, four-tick attacks, 15-tick respawn, 150 LP, Attack 10,
Strength 10, Defence 12, zero defence bonuses, the guaranteed Impious ashes,
and a complete 128-slot ordinary drop table. Its `MAGIC_MELEE` style conflicts
with the cutoff page and Darkan, and its 7 Slayer XP conflicts with the cutoff
15. The cutoff values win both conflicts.

Darkan:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/icefiend/icefiend_(13).json`

The exact level-13 ids 7714–7716 independently converge on 150 LP, 20 maximum
hit, melee combat, Attack 10, Strength 10, Defence 12, and passive aggression
state. Its 29-tick respawn conflicts with game-main's explicit ordinary plugin;
AnkiScape retains the game-main 15-tick row used by the rest of this drop and
combat definition.

The Darkan level-18/37/63/88/128/132/160 definitions are different variants.
They do not overwrite the selected ordinary target.

## Runtime and drop boundary

The live target uses the shared Combat, drop, Prayer-ash, food, death, grave,
persistence, cadence, and undo paths. Its 20 LP maximum hit is explicit rather
than derived from Strength.

The implemented main table is game-main's exact 128-slot table. It contains the
sourced ordinary equipment, ammunition, food, rune, ore/bar, and Water-talisman
rows plus its 51-slot nothing branch. Broader rarity-only cutoff rows remain
audit evidence rather than being assigned fabricated numeric weights.

This family slice does not expose a Slayer master or assignment roll. The
Turael/Spria role remains closed until every baseline family and required
protective/finisher consequence is executable.
