# Shilo Village playable quest closure — 2026-07-18

## Scope and result

`Shilo Village` is now a complete review-native quest instead of seven generated
checkpoint buttons. The live chain preserves its prerequisite, skill gates,
quest-item custody and transformations, three-form boss fight, rewards, and
Shilo unlocks through the ordinary quest runtime.

Primary evidence:

- `Shilo Village`, oldid `6389566`, timestamp
  `2012-10-12T11:24:06Z`;
- literal wikitext from the pinned revision, including the explicit optional
  Stone-plaque note and ordered Nazastarool forms;
- Darkan commit `b74c57db6a978de64f83036200ce554f1b908c10`,
  especially
  `src/main/java/com/rs/game/content/quests/shilo_village/ShiloVillage.kt`,
  `MosulDialog.kt`, and
  `src/main/java/com/rs/game/content/quests/TrufitusDialog.kt`; and
- the dated rev-742 OpenRS2 cache from `2012-11-07`.

No owner-level design gap emerged.

## Playable stage ledger

The implementation has eleven meaningful requirements plus the ordinary
completion sentinel:

1. carry Mosol Rei's Wampum belt to Trufitus and accept the search;
2. dig into Ah Za Rhoon with a Spade, consume one supported lit light source
   and one Rope, and enter the temple;
3. search the temple, read both scrolls, recover Zadimus's corpse, and
   automatically preserve the optional saleable Stone-plaque;
4. show the mandatory evidence to Trufitus, bury Zadimus, and receive the Bone
   shard;
5. search Bervirius's Cairn Isle tomb for the Sword pommel, Locating crystal,
   and Bervirius notes;
6. read the notes and show the tomb evidence to Trufitus;
7. use a Chisel to turn the Bone shard into a Bone key and the Sword pommel into
   Bone beads;
8. consume Bronze wire and the Bone beads to make Beads of the dead;
9. use the Locating crystal, Bone key, Beads, and three ordinary Bones to enter
   Rashiliyia's tomb;
10. defeat Nazastarool's level-91 zombie, level-68 skeleton, and level-93 ghost
    forms in order, then receive Rashiliyia's corpse;
11. show the corpse to Trufitus and consume it at Bervirius's dolmen; and
12. close on the ordinary `Quest complete!` journal row.

Travel, dialogue, the loose-rock trap, gallows gas, and tomb navigation are
named `auto_actions`. They remain legible without adding map state, wall-clock
delays, or generated `required_actions` that the player cannot clear.

## Source conflict: the Stone-plaque is optional

The pinned wikitext calls the Stone-plaque optional and says it can be sold
after the quest. Darkan can award it when a Chisel is used on the strange stone,
but its stage-advance condition around `HAS_READ_STONE_PLAQUE` is internally
inverted and cannot override the period page.

The live quest therefore includes the plaque in the collapsed temple-search
review but never requires a Chisel at that stage and never blocks Trufitus's
mandatory evidence handoff on the plaque. This is an explicit AnkiScape
abstraction: the review model preserves the period item without adding a
consequence-free optional-action picker or converting it into a progression
gate. Yanni's post-quest purchase service remains separate future quest/shop
work, so live copy does not promise a sale action that is not yet present.

## Item identities, custody, and assets

Rev-742 confirms these cache identities:

| Item | ID | Live custody |
|---|---:|---|
| Bone shard | 604 | transformed into Bone key |
| Bone key | 605 | retained quest tool |
| Stone-plaque | 606 | optional retained evidence |
| Tattered scroll | 607 | retained evidence |
| Crumpled scroll | 608 | retained evidence |
| Rashiliyia corpse | 609 | consumed at Bervirius's dolmen |
| Zadimus corpse | 610 | consumed at his burial |
| Locating crystal | 611 | retained quest tool |
| Beads of the dead | 616 | retained neck equipment |
| Bone beads | 618 | transformed into Beads of the dead |
| Sword pommel | 623 | transformed into Bone beads |
| Bervirius notes | 624 | retained evidence |
| Wampum belt | 625 | consumed by Trufitus |

All thirteen are nontradeable and nonstackable. Beads of the dead are generated
as neck equipment; the others remain quest items.

The corresponding `questitems/*.png` sprites are pinned in
`assets_provenance.json`. Their historical file revisions range from
`2011-11-17` through `2012-05-25`, all before the `2012-11-20` cutoff. The asset
fetcher must currently run sequentially: concurrent fetch processes race while
rewriting the shared provenance JSON.

## Combat evidence

The pinned revision establishes the three forms and their exact order and
levels: zombie 91, skeleton 68, ghost 93. Darkan's combat definitions supply the
resolver values:

| Form | HP | Attack | Strength | Defence | Max hit |
|---|---:|---:|---:|---:|---:|
| Zombie | 500 | 38 | 30 | 38 | 70 |
| Skeleton | 750 | 38 | 30 | 38 | 120 |
| Ghost | 1,000 | 38 | 30 | 38 | 152 |

All three definitions are melee, crush-based, and aggressive. Their exact
paths are
`data/npcs/combatdefs/uncategorized/nazastarool/nazastarool_(91).json`,
`nazastarool_(68).json`, and `nazastarool_(93).json`.

The quest runtime replaces the generated single placeholder with three ordered
encounters. Stage progress does not advance until all three are defeated; only
then does the next review produce Rashiliyia's corpse.

## Requirements, rewards, and unlocks

The pinned quest row and literal wikitext close:

- `Jungle Potion`;
- Smithing 4;
- Crafting 20;
- Agility 32;
- two quest points; and
- 3,875 Crafting XP.

The completion unlock text preserves Shilo Village access, its Brimhaven cart,
and gem rocks. The existing gem-rock target unlock rule continues to use the
canonical completed-quest state.

## Review and verification

Codex Workflow `64b7499a-9185-49f4-b78b-d5d9bbe89d75` produced one accepted
dependency/runtime final. Its Shilo source leaf exceeded the bounded timeout
without a final; its concrete optional-plaque warning was independently
reproduced from the pinned wikitext and fixed. The leaf's tentative concern
about unresolved boss stats was rejected after direct inspection of all three
Darkan combat definitions.

Focused coverage proves the source contract, every item transformation, the
complete pure quest chain, live review dispatch through all three boss forms,
registry and provenance reachability, Beads equipment generation, and the real
offscreen Qt boss blocker/action surface.

A bounded Fable UI/copy review accepted the stage density, transform chain, and
three-form presentation. Its reproduced findings were fixed: optional-plaque
mechanics and wording now agree, the absent Yanni service is not described as
live, the quest details disclose all mid-quest supplies, Ah Za Rhoon is placed
east of Tai Bwo Wannai rather than east of Karamja, and the rev-742 source is a
real cache path rather than a path/prose hybrid.

The next implementation dependency is not the black-mask drop itself. First
replace Jungle Potion's remaining generated objective buttons, then build Big
Chompy Bird Hunting, Zogre Flesh Eaters, Rum Deal, and Cabin Fever before
activating Mos Le'Harmless, Cave horrors, the 1/512 Black mask drop, Slayer
reward purchases, and the Crafting-55 Slayer helmet.
