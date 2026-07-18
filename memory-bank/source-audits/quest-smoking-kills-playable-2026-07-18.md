# Smoking Kills playable quest closure — 2026-07-18

## Scope and result

`Smoking Kills` is now a complete review-native quest rather than four generated
placeholder rows. Its prerequisite checks, item custody, combats, completion
rewards, Sumona gate, and Slayer-point unlock all run through the ordinary quest
and Slayer systems.

The primary period source is:

- `Smoking Kills`, oldid `6548001`, timestamp
  `2012-11-11T11:00:34Z`;
- generated pinned evidence:
  `quest_catalog_generated.py:23218-23483`; and
- live owner contract:
  `memory-bank/slayer-skill-contract-2026-07-15.md:423-451`.

No owner-level design gap emerged.

## Playable stage ledger

The implementation uses twelve meaningful stage requirements plus the standard
completion journal sentinel:

1. accept Sumona's rescue request and hear Ali Cat's warning while carrying a
   cat and a Catspeak amulet;
2. reach Catolax's tomb, break into the ranged wing, disarm its traps, and
   defeat the grouped four-guardian wave;
3. defeat the first level-54 Mummy Warrior and receive a Ranged path key;
4. use the key and pull the ranged-wing lever;
5. break into the magic wing and defeat its grouped four-guardian wave;
6. defeat the second level-54 Mummy Warrior and receive a Magic path key;
7. use the key, speak to Catolax through a Ghostspeak amulet, and transform one
   Face mask plus one pair of Earmuffs into Masked earmuffs;
8. enter the Pollnivneach well with Masked earmuffs;
9. defeat one Mighty banshee and deterministically receive one Banshee voice;
10. consume the voice at the mystic barrier;
11. defeat the Banshee Mistress with her half-health assassin phase explicitly
    folded into the same battle;
12. hear Catolax's final message and report to Sumona; and
13. close on the ordinary `Quest complete!` journal row.

The two source-permitted tomb orders have no downstream consequence. The live
quest fixes the order as ranged then magic, which keeps both real paths and both
real keys without adding a no-stakes route picker.

Travel, tomb traps, simultaneous guardian respawns, and cutscenes are named
`auto_actions`. They do not use wall-clock time and do not create unclearable
`required_actions` blockers.

## Item custody and equipment

The following local cache identities are certified from
`/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` and Darkan
`developer-information/itemList.txt`:

| Item | Cache ID | Live treatment |
|---|---:|---|
| Ghostspeak amulet | 552 | nontradeable, nonstackable neck equipment |
| Kitten | 1555 | representative nontradeable, nonstackable cat item |
| Catspeak amulet | 4677 | nontradeable, nonstackable neck equipment |
| Ranged path key | 13259 | nontradeable, nonstackable quest item |
| Magic path key | 13260 | nontradeable, nonstackable quest item |
| Banshee voice | 13276 | nontradeable, nonstackable quest item |
| Masked earmuffs | 13277 | nontradeable, nonstackable head equipment |

The raw quest parser called the Restless Ghost reward `Amulet of ghostspeak`,
while its existing playable stages produced `Ghostspeak amulet`. The canonical
reward-name override now resolves both to `Ghostspeak amulet`; this closes the
registry split without migrating or deleting the item already held by existing
saves.

`required_tools` deliberately supplies equipped-or-carried semantics for both
speaking amulets and Masked earmuffs. Masked earmuffs remain required on every
in-well stage, so the player cannot discard them after entering and continue as
though protected.

The exact server-side removal rule for each path key is `source_blocked`. The
live quest consumes each key when its door and lever are resolved. This is a
labeled atomic-custody abstraction that prevents spent quest keys from becoming
permanent bank clutter.

Five period sprites are pinned through the reusable cutoff-aware asset fetcher:

- `questitems/ghostspeak_amulet.png`, file revision timestamp
  `2009-12-26T18:06:32Z`;
- `questitems/ranged_path_key.png`, `2008-06-09T22:25:02Z`;
- `questitems/magic_path_key.png`, `2008-06-24T16:35:38Z`;
- `questitems/banshee_voice.png`, `2011-11-17T19:54:24Z`; and
- `questitems/masked_earmuffs.png`, `2010-04-12T08:35:44Z`.

All are earlier than the `2012-11-20` cutoff and recorded in
`assets_provenance.json`.

## Combat evidence and bounded adapters

### Tomb guardian waves

The pinned infobox describes two sets of two level-10–20 Skeleton Warriors and
two level-10–20 Skeletal Mages. The same revision's walkthrough instead says
each room has two zombies and two skeletons with about 200 LP. Darkan has no
exact quest NPC/stat match.

Exact component identities and hidden stats therefore remain `source_blocked`.
Each wing is one grouped 800-LP level-20 resolver wave: four roughly 200-LP
guardians represented at the period upper level bound. Ranged and Magic styles
distinguish the two wings. The grouping preserves the meaningful simultaneous
kill gate without inventing a respawn period.

### Mummy Warriors

`Mummy Warrior`, oldid `6573394`, timestamp `2012-11-18T08:16:55Z`, confirms
level 54 but leaves hidden stats blank. The pinned Smoking Kills walkthrough
reports melee and a maximum hit of 80. Darkan NPC candidates `7807` and `7808`
use a clearly incomplete `1 HP / maxHit 1 / passive` combat definition.

Each ordered mummy is therefore a separate level-54 melee encounter with the
sourced max hit 80 and a labeled level-based 540-LP/stat resolver adapter.

### Mighty banshee

`Mighty banshee`, oldid `6530631`, timestamp `2012-11-04T07:29:56Z`, supplies
level 90, 850 LP, aggressive magical melee, raw attack-speed value 6, and an
approximate maximum hit of 90. Darkan independently converges on 850 HP and
maxHit 90 but does not supply the core combat stats.

The live row preserves those sourced values and uses a labeled level-based
adapter only for hidden stats. The historical Banshee voice drop chance is
`source_blocked`; one deterministic quest kill grants the voice so the stage is
reachable without inventing a rate.

### Banshee Mistress and Insectoid Assassins

`Banshee Mistress`, oldid `6529627`, timestamp `2012-11-03T21:31:42Z`, supplies
level 111, 2,220 LP, aggressive melee plus Water Blast, an approximate ordinary
maximum hit of 140, and an acoustic attack up to 130. The pinned quest
walkthrough supplies the half-health transition: four level-141 Insectoid
Assassins join with rapid ranged hits up to 200 and vanish when the Mistress
dies. Darkan converges on the Mistress's 2,220 HP and 140 max hit but flattens
her mixed style; its assassin definition conflicts at maxHit 180.

The assassins are phase hazards, not four required kills. AnkiScape keeps one
level-111 Banshee Mistress encounter, folds the sourced 200-damage phase ceiling
into that battle, and states the abstraction in both journal and combat text.
Hidden combat stats use a labeled level-based adapter.

The quest's sourced player requirement is Combat 85 even though its enemies are
levels 90 and 111. A new optional `minimum_player_combat` encounter configuration
separates the historical NPC level shown to the player from the sourced player
gate. Existing quest encounters retain their prior enemy-level gate unless they
opt into this field.

## Rewards and Slayer boundary

The parser's apparent item rewards were headings and examples from the Slayer
reward catalog, not completion grants:

- Broad arrows x2;
- Broad-tipped bolts x2;
- Runes;
- Slayer Master;
- Slayer helmet; and
- Slayer ring x2.

The live override replaces them with an empty item-reward map. Ordinary
completion grants exactly:

- one quest point; and
- 5,000 Slayer XP.

Completion activates the existing Smoking-Kills-gated Slayer reward surface and
Sumona eligibility. It does not mutate `slayer_points` or
`slayer_qualifying_streak`, so pre-quest tasks do not retroactively award points
and the post-quest qualifying counter begins at zero.

## Review findings and verification

Read-only Codex Workflow
`694e9fd9-5b4f-40b0-9cb5-3379505409cf` produced two accepted Sol-high finals:
the stage/reward ledger and combat-source ledger. Its item/asset leaf exceeded
the bounded timeout, produced no final, and was discarded; the primary
independently reproduced every accepted item and asset fact.

A bounded read-only Fable review approved the twelve-beat density and fixed
ranged-then-magic order. Its concrete findings were integrated:

- no consequence-free quest-choice control;
- no generated item-name casing;
- no required-action deadlocks;
- Masked earmuffs repeated on every in-well stage;
- the assassin phase visible in the journal; and
- a source-backed player-combat requirement distinct from enemy level.

Focused verification:

- 336 quest catalog, pure logic, live integration, and item-registry methods
  passed;
- one real offscreen Qt Smoking Kills boss-surface method passed;
- 16 equipment-generator and combat-debt ledger methods passed after updating
  the exact closed-debt counts;
- compilation, provenance JSON, combat-gap audit, and worktree guard passed; and
- the full core and full real offscreen Qt discovery results are recorded in
  `memory-bank/progress.md` after closure.

