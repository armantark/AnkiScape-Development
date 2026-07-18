# Slayer Pyrefiend Combat audit — 2026-07-18

Status: **source closed for the ordinary level-43 representative**.
Cutoff: `2012-11-20T00:00:00Z`.

## Executable boundary

Admit NPC ids 1633–1636 as one ordinary level-43 Pyrefiend Combat target.
The level-48 God Wars variant, Soul Wars-only behavior, Daemonheim forms,
Revenant pyrefiend, and pyrelord familiar remain distinct content. They are not
silently folded into this row.

This one ordinary representative is sufficient for the current
Mazchna/Achtryn family-readiness bar. It does not claim that every qualifying
Pyrefiend variant has been implemented.

## Period evidence

RuneScape Wiki `Pyrefiend`, oldid `6565806`, timestamp
`2012-11-17T10:17:32Z`:
<https://runescape.wiki/w/Pyrefiend?oldid=6565806>.

The cutoff revision records for the ordinary form:

- Combat 43, 450 life points, Slayer 30, and 45 Slayer XP;
- a 44-LP maximum hit;
- non-aggressive and non-poisonous behavior;
- a magic-based melee attack whose accuracy rolls against Magic defence while
  Protect from Melee, rather than Protect from Magic, is the relevant prayer;
- Water-spell, Silverlight, Darklight, and stab weaknesses;
- assignment membership for Achtryn and Vannaka; and
- guaranteed Impious ashes.

The source also lists a level-48 God Wars form with 480 life points, 48 Slayer
XP, and a 50-LP maximum hit. That is the explicit excluded variant, not a
conflicting value for the selected target.

Revision-742 cache identity was checked with
`tools/query_openrs2_cache_definitions.sh`. NPC ids 1633, 1634, 1635, and 1636
are all named `Pyrefiend` with an Attack option. Other returned ids belong to
the excluded contexts above.

## Emulator reconciliation

game-main ordinary definition:

`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/demons/pyrefiend_lvl_43.plugin.kts`

It supplies:

- NPC ids 1633–1636;
- four-tick attacks and a 15-tick respawn;
- 450 life points, Attack 52, Strength 30, Defence 22, Magic 1, and Ranged 1;
- +10 stab/slash/crush/ranged defence, neutral Magic defence;
- `MAGIC_MELEE`;
- Slayer 30 and 45 Slayer XP; and
- a complete 128-slot ordinary drop table plus guaranteed Impious ashes.

The combat formula proves that `MAGIC_MELEE` is not ordinary Magic. In
`MeleeCombatFormula.kt`, its attack roll remains melee/Attack-based, the target
uses `MagicCombatFormula.getDefenceRoll`, Protect from Melee prevents the hit,
and the source selects the stab attack-bonus slot.

The period page supplies the explicit 44-LP maximum hit that the emulator row
does not encode. No numeric value is invented.

## Drop and item boundary

The live target uses game-main's exact 128-slot table:

- Steel hatchet 4, Steel full helm 4, Mithril chainbody 2, Staff of fire 3,
  Steel boots 1, and Adamant med helm 1;
- Fire rune 30 at 21 slots and 60 at 8, Chaos rune 12 at 5, and Death rune 3
  at 3;
- Coins 10/40/120/200/450 at 7/24/20/10/2 slots;
- Gold ore 8 and Jug of wine 2; and
- the shared gem table at 3 slots.

Steel boots item 4123 is independently present in the revision-742 cache with
a Wear option. game-main `data/cfg/items.yml` supplies its feet slot, Defence
5 gate, and exact equipment bonuses. It therefore enters the normal equipment
and item registries rather than becoming a name-only drop.

The Pyrefiend target image is the pre-cutoff `2011-12-11T01:47:45Z`
`Pyrefiend.png` file revision. The Steel-boots item sprite is the canonical
classic sprite fetched from the Old School RuneScape wiki; its current file
revision is not period evidence. The revision-742 cache item identity and
game-main equipment row, rather than the sprite upload timestamp, establish the
pre-EOC item contract.

Current wiki rarity-only rows that lack source-era numeric rates are not
fabricated. Soul fragments remain Soul Wars-only and are excluded.

## Runtime contract

- `magic_melee` attacks use the enemy's Attack stat and stab attack bonus.
- The player resists with Magic defence.
- Protect from Melee and the Casual max-safety prayer selector treat the
  attack as melee.
- The source's explicit maximum hit remains authoritative.
- The target otherwise reuses shared Combat food, death, grave, drop, Prayer
  ash, cadence, persistence, Slayer task-credit, and undo paths.

No owner design decision is required.
