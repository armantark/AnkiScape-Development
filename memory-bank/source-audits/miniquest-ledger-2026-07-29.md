# Miniquest ledger and its first two rows — 2026-07-29

Authority: `design-thread-queue.md` section 4.14 item 1 (the answered form of
section 3.23) and `source-audits/bork-loop-2026-07-18.md`.

## What shipped

Miniquests are a flagged category on the existing quest ledger. They use the
same storage, the same unlock engine and the same stage/journal machinery as
the 194 catalog quests; only the Quests tab groups them apart, under a
`Miniquests` heading that appears solely when both groups are on screen.

Exactly two rows exist, the two the owner named:

- `hunt_for_surok` — The Hunt for Surok, which unblocks the parked Bork loop;
- `lair_of_tarn_razorlor` — The Lair of Tarn Razorlor, which lights the
  Dominion Tower's class-H Tarn Razorlor encounter that already gated on this
  exact id.

No catalog sweep was performed. The remaining period miniquests join as content
needs them.

### Why the rows are hand written

`tools/build_pre_eoc_quest_catalog.py` builds from the wiki's quest release
list, and that list carries no miniquests at all. The two rows are therefore
written directly in `data/quest_data.py` from the pinned period record and
appended to `QUESTS`, then passed through the same
`_quest_with_stage_requirements` pass every catalog row takes, so stage counts,
deduplication and the completion sentinel behave identically.

Schema `103` records the change. Miniquests are ordinary quest rows, so the
existing unconditional `_migrate_quest_state` already writes their unstarted
state into every older save; nothing else in the payload moves.

## Pinned period sources

| Fact | Source |
|---|---|
| Miniquests award no quest points | `Miniquests` oldid 6020341, `2012-07-31T15:24:56Z` |
| Hunt for Surok requires What Lies Below | same, plus Darkan `HuntForSurok.kt` and `Miniquest.java` |
| Hunt for Surok stages and journal | Darkan `HuntForSurok.kt` (`completedStage = 5`, six journal lines) |
| Hunt for Surok walkthrough beats | `The Hunt for Surok (miniquest)` oldid 6097199, `2012-08-16T06:21:06Z` |
| Mining 42 to excavate the statue | Darkan `HuntForSurok.kt`; the pinned page lists the same level |
| Bork level 267, 3,000 LP, max hit 254, crush, speed 6 | `Bork` oldid 6565904, `2012-11-17T10:41:40Z`; Darkan `bork (nostats).json` converges on 3,000 / 254 |
| 5,000 Slayer XP on first completion | both of the above, and Darkan's `complete()` |
| Lair of Tarn Razorlor requires Haunted Mine and Slayer 40 | `Miniquests` oldid 6020341 |
| Lair walkthrough, route, traps and two Tarn forms | `Lair of Tarn Razorlor (miniquest)` oldid 6448364, `2012-10-21T06:13:36Z` |
| Tarn level 69, 650 LP, max hit ~190, speed 5, mutant melee+magic then ghost melee | `Tarn` oldid 6448021, `2012-10-21T02:11:04Z` |
| Tarn combat levels 40/80/40 | Darkan `tarn (noanims).json`; `mutant_tarn (nostats) (noanims).json` states none |
| Mutant Tarn attacks solely with melee when approached | `Lair of Tarn Razorlor (miniquest)` oldid 6448364, Strategies section |
| Bork's legion arrives at 2,000 life points, three to nine orks | Darkan `Bork.kt` (`ORK_SUMMON_THRESHOLD_HITPOINTS`, `ORK_SUMMON_MINIMUM`, `ORK_SUMMON_MAXIMUM`) |
| Two level 110 terror dogs join the mutant fight | the pinned lair page; Darkan `terror_dog_(110)` gives 880 LP / 110 max hit |

## Judgements recorded

**Difficulty is `Special` for both.** The catalog's difficulty vocabulary comes
from the release list's `dif` word, and neither miniquest has one. The Surok
page carries a numeric `wdifficulty=4`, but mapping that number onto the word
scale is inference, not a source, so it was not used. `Special` is the value
the catalog already gives its ten out-of-band rows.

**Release order 9999.** The release list assigns no order to miniquests, so
both rows take the catalog's own unknown-order value and sort last inside their
own section. Their release dates remain exact.

**Folded pressure, not extra kills — and the same fold in both fights.** Bork's
three to nine level-70 Ork legions, Surok's periodic 350-damage bolts and the
two level-110 terror dogs are all narration on the encounter rows rather than
resolved attackers. The period supports the fold on both fights: the lair page
says outright that "Tarn Razorlor is the only monster required to be killed"
and adds that a player can manoeuvre the dogs behind Tarn to remove them from
the fight completely, while the Surok page treats the legions as a hazard to be
trapped or outrun. Both combat texts state the fold in the same words, following
the Smoking Kills precedent.

The reason the fold is uniform here and *not* uniform against the repeatable
Bork loop is the engine, not a second reading of the source. A quest stage
resolves exactly one enemy: `apply_quest_combat_encounter_pure` hands a single
enemy spec to `apply_combat_burst_pure`, which runs the whole battle — the
player's attacks, the enemy's attacks, auto-eat, prayer and death — inside one
500-tick burst. There is no channel for a second attacker, and damage added
after the burst returns would arrive as one lump that skips the auto-eat the
burst just finished simulating; a prototype of exactly that killed a
fully-equipped test player outright. The Bork daily loop is not a quest stage.
It is a Combat context stepped review by review, which is why it can and does
run every ork through `combat_enemy_pressure_attack_pure`.

The consequence is real and worth stating plainly: the one-off miniquest kill of
Bork is easier than the daily repeat kill of the same monster. Closing that gap
needs a supporting-attacker channel inside `apply_combat_burst_pure` itself, so
minions attack on their own speed alongside the boss and inside the same
food-and-prayer simulation. That is an engine change with reach across every
combat context, so it is logged here rather than smuggled into the ledger.

**Tarn's two forms are two encounters.** The source describes a mutant form and
then a ghost form with the same level and life points but melee only; that is
the same shape as Shilo Village's three-form Nazastarool, so it ships as two
ordered encounters rather than one.

**No invented player-combat gate.** `minimum_player_combat` is set to 1 on all
three encounters. The engine otherwise gates an encounter on the enemy's own
level, and a level-267 gate is unreachable — the pre-EOC ceiling is 138. The
period states no combat requirement for either fight: Bork's own Slayer
requirement is level 1, and Tarn's sourced gate is Slayer 40, which is already
a quest requirement. Adding a combat gate would have been an invention.

**Bork's core stats use the settled 72% conversion.** Darkan's Bork row is a
`nostats` file with zeroed combat levels. Copying his composite combat level
267 into Attack, Strength and Defence made him both unhittable and
unsurvivable, exactly the failure the Dominion Tower work already hit with
Nomad. The row therefore reuses the registered
`dominion_tower.unsourced_boss_stat_blocks` conversion — 72% of combat level,
capped at 99 — and the marker names that id. Tarn needs no such fallback
because Darkan carries his real 40/80/40 block.

## Data depth left open

These are recorded gaps, not blockers. Both miniquests complete without them.

1. **The salve amulet chain does not exist.** No `Salve amulet` item is in the
   registry: Haunted Mine's reward is a Crystal-mine key, and its unlock text
   describes crafting the amulet from a salve shard and a ball of wool, which
   was never built. The lair page's "requires the Salve amulet to enter" is
   also contradicted inside the same revision by "wearing Salve amulet is not
   compulsary to start or end this fight", so the entry requirement is not even
   internally settled. The miniquest therefore does not gate on the amulet.
2. **`Tarn's diary` and `Salve amulet (e)` are unlock text, not items.** The
   completion row awards the sourced 5,000 Slayer XP and names both rewards in
   `unlocks` and in the final journal stage. Granting a diary whose only use is
   enchanting an amulet that does not exist would have been inert bank clutter.
   When the salve chain is built, the diary and the enchant become real item
   and equipment rows against this same completion flag.
3. **The Bork daily loop stays parked.** This ledger only makes the miniquest
   completion reachable, which was the first of the two things
   `bork-loop-2026-07-18.md` was waiting on. The recurring daily Bork Combat
   context still waits on the regional Achievement Diary substrate that owns
   the Elite Varrock modifier, and on that page's internally conflicted default
   charm bundle.

## Cross-check of every pinned value (second pass)

Every requirement, stage and reward above was re-read against the pinned
revisions and against Darkan a second time. Nothing in the data moved, because
nothing was wrong. What the pass settled:

**Confirmed exactly.** Bork level 267, 3,000 life points, maximum hit 254,
crush, attack speed 6, released 4 March 2008; Tarn level 69, 650 life points,
maximum hit 190 approximate, attack speed 5, released 22 January 2007, mutant
form melee and magic and ghost form melee only; Tarn's Darkan block 40 / 80 /
40 with `CRUSH_ATT`; the level 110 terror dog at 880 life points and 110
maximum hit; both 5,000 Slayer rewards; the Lair's Haunted Mine plus Slayer 40
gate; Hunt for Surok's What Lies Below gate and Mining 42; all six Surok
journal lines and `completedStage = 5`, which are Darkan's verbatim; the banker
spelled Odovacar, which both Darkan's spawn file and his own wiki page use
against the miniquest list's "Odovokar".

**Prayer 43 was considered and left out.** Darkan's `Miniquest.java` enum gates
The Hunt for Surok on Mining 42 *and* Prayer 43, and Darkan is normally the
primary source. It was not followed here because the pinned Surok page carries
the same two numbers and annotates the Prayer one "recommended along with a
high combat level but not needed to complete the quest", and because the pinned
`Miniquests` list gives the requirement as What Lies Below alone. Darkan's line
reads as that same wiki table copied without its qualifier. AnkiScape's
`required_skills` is a hard start gate, so honouring it would lock a miniquest
the period says is open.

**Slayer 44 was considered and left out.** It appears only in the Surok page's
requirement block, in neither the miniquest list nor Darkan, and Bork's own
page gives his Slayer requirement as level 1. Nothing on the route must be
killed, so no Slayer-gated monster is load bearing.

**Mining 42 was kept even though it can never bind.** Slayer 44 and Mining 42
sit side by side and unannotated in the same requirements block of the Surok
page, and one was kept while the other was dropped, so the asymmetry needs its
reason on the record. Mining 42 is not a judgement call about that block at all:
it is corroborated by Darkan's `HuntForSurok.kt`, which spends it on the statue,
and stage 1 of this ledger spends it the same way. Slayer 44 has no second
source and no use on the route. The kept row is admittedly inert today, because
`What Lies Below` already demands Mining 42 and is a hard prerequisite, so a
player who can start the miniquest necessarily has the level. Two facts that
happen to agree are still two facts, and the miniquest's own stated requirement
belongs on its own row: if the prerequisite quest's requirements are ever
corrected, this gate keeps holding on its own evidence. Prayer 43 is the third
number in the same block; it was dropped for the separate, stronger reason that
the page itself annotates it "not needed to complete the quest".

**Darkan's Bork level 107 is post-cutoff.** His handler's `combatText` says
"Bork (level 107)" and his rewards text says 1,500 Slayer XP per daily kill.
Both are Evolution of Combat figures. The pre-cutoff record gives 267 and
250 XP (500 with the Varrock elite tasks), so the wiki wins on these two and
Darkan is used only for the life points, maximum hit and journal text, which
agree.

**Mutant Tarn's stat block is the ghost's, and it is marked as a placeholder.**
Darkan's `mutant_tarn (nostats) (noanims).json` is a `nostats` row with zeroed
combat levels and no `attackBonus`, so both encounters take the 40 / 80 / 40
block and `CRUSH_ATT` from his `tarn (noanims).json` file. The two forms share a
level, life-point total, maximum hit and attack speed in the period record, so
this is the same body twice rather than an invented second one. It is still a
substitution, and the first pass shipped it unmarked while Bork's identical
`nostats` gap carried a `PLACEHOLDER` marker. That asymmetry is fixed: the
mutant row now carries `PLACEHOLDER(lair_of_tarn_razorlor.mutant_tarn_stat_block)`
and its `npc_stats_source` names both files, the one the numbers came from and
the one that has none.

**Mutant Tarn fights melee, and the prose now says so.** The `Tarn` infobox
reads `attack style = Melee and magic` for the mutant form, and the first pass
repeated that in the encounter text while `npc_configs` set `attack_style` to
melee — so the player was promised an attack the fight could not deliver. The
same pinned revision settles it in the lair page's strategy section: "He can
attack with both melee and magic, but attacks solely with melee if approached."
Every AnkiScape battle is an approached battle, so the melee-only reading is the
period's own, not merely Darkan's, and the encounter text now states the
infobox, the strategy line and the conclusion together. This is why Darkan's
`MELEE` file wins rather than being overridden by the infobox.

**Two labels remain inference, and are marked as such.** `difficulty` is
`Special` for both rows and the Lair's `length` is `Short`; the Lair page
carries no quest-details infobox at all, and neither page carries a difficulty
word. Surok's `Short to Medium` is the catalog spelling of his page's
"Short-Medium".

## Verification

`tests/test_miniquest_ledger.py` covers the flag round-trip and its UI
grouping, both miniquests driven end to end through `start_quest_pure`,
`apply_quest_progress_pure` and `apply_quest_combat_encounter_pure`, and the
schema 103 migration from a v101 save in both directions.

The Dominion Tower gate is covered through the tower's own reducers rather than
its private helper: `dominion_tower_available_encounters_pure` and
`dominion_tower_view_pure` are read before and after the Lair miniquest is
driven to completion, and the same test asserts that the tower's
`completed_quests` count — the entry gate, which reads only the tower's 38
quests — does not move when a miniquest completes. A second test walks
`DOMINION_TOWER_GLOVE_SETS` to hold section 3.23's claim that no reward set
ever contained this boss.
