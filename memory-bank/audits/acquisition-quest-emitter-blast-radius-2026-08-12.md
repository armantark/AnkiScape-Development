# Acquisition triage and quest-emitter blast radius — 2026-08-12

## Scope and outcome

This read-only acquisition slice began from the corrected reachability baseline on
`goal/acquire-2026-08-12`: 1,556 actions, 2,493 reachable items, 103 orphan
inputs, and 102 blocked actions. No product code changed.

The candidate family was Snake hide. The authentic Bush-snake route is inert for
an ordinary player because Tai Bwo Wannai Cleanup requires Jungle Potion, Jungle
Potion requires Druidic Ritual, and both quests stop on un-emitted
`required_actions`. The slice stopped before implementation as required.

## Quest-action emitter count

The live `QUEST_DATA` registry contains 196 playable entries: 194 generated
catalog quests plus two miniquests. It contains:

- 1,096 `required_actions` occurrences, 1,095 distinct strings, across 185
  quests;
- 101 `auto_actions` occurrences, 100 distinct strings;
- zero intersections between required-action and auto-action strings, globally
  or when keyed by quest;
- 783 generated placeholders matching
  `Complete X stage N objective`; and
- 313 hand-authored action occurrences.

Therefore 185 of 196 quests are directly uncompletable through ordinary runtime
progression because each reaches at least one action that no runtime path marks.
The reverse prerequisite closure adds five catalog entries whose own stages have
no required action but whose prerequisites are blocked:

- `hunt_for_surok`;
- `icthlarins_little_helper`;
- `lair_of_tarn_razorlor`;
- `shilo_village`; and
- `smoking_kills`.

The approximate completion impact is therefore 190 of 196 quests. The six not
affected by this specific dependency are `cooks_assistant`,
`diamond_in_the_rough`, `goblin_diplomacy`, `imp_catcher`, `stolen_hearts`, and
`the_knights_sword`. This does not prove that those six are free of other gates.

Of the 185 directly action-blocked quests, 175 first stop at stage 1. Ten first
stop later: `a_souls_bane`, `demon_slayer`, `dragon_slayer`, `family_crest`,
`fight_arena`, `plague_city`, `tai_bwo_wannai_trio`, `temple_of_ikov`,
`vampyre_slayer`, and `witchs_house`.

### Counting method

1. Import the assembled `core.constants.QUEST_DATA`, so catalog overrides and
   miniquests are counted.
2. Enumerate every stage's `required_actions` and `auto_actions`.
3. Classify generated placeholders with
   `^Complete .+ stage [1-9][0-9]* objective$`.
4. Compare required and emitted action IDs globally and quest-scoped.
5. Seed the prerequisite graph with the 185 directly blocked quest IDs and take
   its reverse transitive closure.

The repository's independent coverage audit reports 196 quests, 1,146 stage
rows, 994 rows with action blockers, and 185 quests with action blockers. The
runtime reads quest-scoped action flags in
`logic_pure/logic_pure_quest.py:263-311`, records `auto_actions` only after a
blocker-free stage in `logic_pure/logic_pure_quest.py:1239-1255`, and rejects
progress while any blocker remains in `logic_pure/logic_pure_quest.py:1436-1461`.
The catalog builder creates the placeholder action form at
`tools/build_pre_eoc_quest_catalog.py:2012-2047`.

A positive-control runtime probe used Druidic Ritual stage 1. Without the known
action flag, it returned `Action required: Speak to Sanfew about the ritual
ingredients`; after placing that exact action in
`quest_stage_actions["druidic_ritual"]`, the blocker disappeared. This proves
the probe can observe both states.

## Approximate completion-gated content

These are registered content targets or records, not unique reachable items:

| Category | Completion-gated population tied to action-blocked quests |
| --- | ---: |
| Combat enemies | 15 targets |
| Slayer | 17 families / 21 enemy targets |
| Magic | 56 action or spell targets |
| Explicit skill/activity unlocks | 22 rules / 36 target IDs |
| Completion-only shops | 33 shops |
| Quest-start shops downstream of affected quests | 25 shops / 190 stock rows |
| Dependent quests | 110 quests; 406 prerequisite edges target blocked quests |

Additional directly completion-gated records include nine Agility records, three
Thieving records, one Construction style, one Temple Trekking event, and one
Barrows record.

Two item bounds answer different questions:

- **80 items** is the measured graph correction already established by
  `memory-bank/audits/quest-stage-reachability-truth-2026-08-12.md`: blocked
  quest-stage production reduced the truthful reachable total from 2,573 to
  2,493.
- **398 unique item names** is a definition-level upper bound across the 185
  directly blocked quests: 131 stage-produced names plus 272 final-reward names,
  with five overlapping. It is not a reachability count because other sources
  can overlap and rewards include currency.

The larger finding is that the blast radius extends beyond quest products.
Every combat enemy, activity, spell, shop, skill target, or later quest gated on
completion is also inert when its upstream quest cannot finish.

## Snake-hide route and stop gate

Period sources establish:

- `Snake hide?oldid=6009794`, lead and Dropping monsters sections: Bush snakes
  drop Snake hide, always, quantity 1–5.
- `Bush snake?oldid=6352282`, infobox and 100% Drops section: combat level 35,
  250 life points, melee, maximum hit 38, Stab weakness, Bones ×1, and Snake
  hide ×1–5 always.
- `Tai Bwo Wannai Cleanup?oldid=6539724`, lead, Preparation, Cutting the jungle,
  and Killing threats sections: Jungle Potion completion, a machete, Woodcutting
  10/20/35 by jungle density, and Bush snake as a threat that drops Snake hide.
- `Jungle Potion?oldid=6555418`, walkthrough and reward sections: the quest
  route itself.

The Bush-snake oldid carries a page-level `{{beta}}` marker. Its drop quantity is
independently corroborated by the in-period Snake-hide oldid, so the 1–5 value
does not rely on that marked page alone.

Darkan's
`data/npcs/drops/bush_snake.json` gives item 6287 exactly 1–1. Per-file
`git log -- data/npcs/drops/bush_snake.json` shows one supplying commit,
`c6fbe036b1743f4dd6067ec178332c69c3708856` (`Initial commit`). The Darkan
restoration thread independently confirmed that this is a genuine original
Darkan-versus-period divergence, not a reconstruction artifact. The dated period
wiki range wins: future implementation must model an always drop with quantity
1–5, not Darkan's fixed one and not a name-wide generic Snake table.

The live blocker probe confirms:

- Druidic Ritual stages 1–3 require un-emitted hand-authored actions; and
- Jungle Potion stages 1–4 require un-emitted generated placeholder actions.

`runtime/runtime_actions_production.py:1298-1389` deactivates Questing and rejects
progress when these stage blocker reasons exist. Consequently an ordinary
level-one-start player cannot complete Jungle Potion and cannot enter Tai Bwo
Wannai Cleanup. Adding Bush snake alone would create an inert acquisition route,
so no product implementation, tests, mutation run, or full test lanes were
started.

## Darkan evidence handling

Reusable rules were added to
`memory-bank/pre-eoc-source-verification-standard.md`:

1. Exclude all 85 tracked
   `src/main/java/com/rs/web/*AuditProbe.kt` files unconditionally. They are audit
   instrumentation and circular evidence by construction. A positive-control
   listing found `TaiBwoWannaiCleanupAuditProbe.kt` inside that exact set.
2. For every other Darkan file, inspect `git log -- <path>` rather than applying
   a recency cutoff. Upstream refactors can be recent; restoration commits are
   unit-scoped.
3. When a restored unit has a frozen contract under
   `memory-bank/audit/reports/`, use that contract as the authority on proof,
   inference, and deferrals. The completed unit set reported by the restoration
   thread is Crucible 425, Dominion Tower 426, Duel Arena 427, and Fist of Guthix
   428. This AnkiScape worktree does not contain those external reports, so this
   slice records the rule without claiming it read them.
4. Record the section that supports each wiki claim. Trivia, update-history,
   scam, exploit, and glitch material is historical or unclear unless separately
   proved. Check page-level markers such as `{{beta}}`.

The restoration thread also independently confirmed a second genuine divergence:
Darkan's original `Silver.java` uses Crafting 20 for the demonic sigil while the
period wiki differs. As with Bush snake, the period source wins and the departure
must be explicit.

## Search discipline

A durable positive-control rule was also added to
`memory-bank/pre-eoc-source-verification-standard.md`: a negative query is not
evidence of absence until the same probe has demonstrated a known hit. Until
then, report only that the search with the stated parameters did not find the
target.

The rule records seven concrete false negatives from one day: a nonexistent
reachability key, `getattr` against dict-form quest combat drops, branch-name
globs that could not match `breadth`, `5,000` versus `5000`, the wrong Gradle
property name, insufficient `find -maxdepth`, and an unquoted path with spaces
that resolved to the wrong sibling tree.

## Follow-up acquisition-family corrections

### Four Jadinko Hunter secondaries

The four Habitat secondaries are distinct from the completed Juju-vine branch.
Running `python3 tools/audit_item_reachability.py --json` inside the read-only
`goal/vines-2026-08-11` worktree at `508a8aa2907fbede5754283e5404271c78058f57`
left all four as root orphans: Corrupt vine, Guthix vine, Shadow vine, and Plant
teeth. The audit, rather than a name search, is authoritative because inherited
item definitions and recipe consumers can contain a name without adding an
acquisition route.

The family splits into two dependency stages:

1. Shadow jadinko at Hunter 71 is a noose-wand tracking catch that yields one
   Shadow vine. Diseased jadinko at Hunter 78 is another noose-wand tracking
   catch and yields one Corrupt vine.
2. Corrupt vine feeds the existing level-54 Juju hunter potion recipe. Cannibal
   jadinko at Hunter 75 and Guthix jadinko at Hunter 81 are Marasamaw-plant
   catches whose attraction state depends on that potion; they yield one Plant
   teeth and one Guthix vine respectively.

The exact period rows are:

- Shadow jadinko oldid `6045371` (`2012-08-05T13:46:52Z`), lead and infobox:
  level 71, Noose wand, 475 Hunter XP, Shadow vine, and `a chance at some seeds`;
  attraction is a red vine blossom plus abandoned-house habitat.
- Diseased jadinko oldid `6062055` (`2012-08-08T19:07:00Z`), lead and infobox:
  level 78, Noose wand, 580.5 Hunter XP, Corrupt vine, and `a chance at some
  seeds`; attraction is a Boneyard plus banana tree.
- Cannibal jadinko oldid `5976665` (`2012-07-22T15:21:18Z`), lead and infobox:
  level 75, Marasamaw plant, 475 Hunter XP, Plant teeth, and `a chance at vine
  bush seeds`; attraction is green vine blossom, kalferberry bush, tall grass,
  and Juju hunter potion.
- Guthix jadinko oldid `6167443` (`2012-08-30T23:12:19Z`), lead and infobox:
  level 81, Marasamaw plant, 600 Hunter XP, Guthix vine, and `a chance at some
  seeds`. Its preferences change every week and the shared god-Jadinko
  environment is personal to the player; only Juju-hunter treatment of the vine
  flower remains constant.

Herblore Habitat oldid `6513740` (`2012-10-31T21:20:32Z`), Jadinkos tables,
labels these wanted rewards `Primary drop` and states that box-trap bait is
optional. The item infoboxes' Withered-vine bait field therefore does not make
bait a consumed acquisition prerequisite.

Therefore Shadow vine and Corrupt vine are upstream of the Juju dependency,
while Plant teeth and Guthix vine are downstream. The route is not quest-gated:
the pinned Herblore Habitat source states that the area has no quest requirement
or entrance-level requirement, and Papa Mambo's live shop row supplies the
Marasamaw plant without a quest, quest start, or other requirement. The live
slice follows the established Common-jadinko convention and treats each
persistent Habitat configuration as source-backed route context rather than a
per-catch consumable. This avoids falsely consuming a Juju dose or crop setup on
every catch while keeping all four fixed primary-output routes playable.

The gate-absence check used a positive control rather than trusting an empty
search. Darkan's `BoxHunterType.java` represents the known-gated Ferret with
`List.of(Quest.EAGLES_PEAK)`, while the Cannibal and Guthix rows carry null quest
and Slayer requirements. The imported AnkiScape gate function likewise reports
`("Eagles' Peak",)` for `catch_ferret` and no lock for an ungated Hunter target.
This proves that the probe can detect a real Hunter gate before its empty result
is used as evidence for the Jadinko rows.

The four cache identities are independently present in revision 742: Corrupt
vine `19979`, Plant teeth `19975`, Shadow vine `19977`, and Guthix vine `19982`.
All four are stackable and non-exchangeable. Their identities and item flags are
registered on the live Hunter outputs.

The implementation follows the accepted Common-jadinko abstraction: persistent
Habitat configurations are source-backed route context, not per-catch consumed
requirements. Tracking uses the reusable Noose wand; box trapping uses the
reusable Marasamaw plant. Hidden catch probabilities use registered placeholder
`hunter.herblore_habitat_success_curves` (`rate1=128`, `rate99=256`) because the
period pages expose no qualified success curve. Bonus seed rolls remain omitted;
they are not required to make these four fixed primary outputs live.

Darkan's fixed-primary-drop files corroborate quantity one and each have a real
pre-fleet supplying history: `data/npcs/drops/hunter/hunter_jadinko_shadow.json`,
`hunter_jadinko_diseased.json`, `hunter_jadinko_cannibal.json`, and
`hunter_jadinko_guthix.json` all come from commit
`087e34d11b59b1d81a6c8aadbf6150a7689c6f4c` (`2022-03-01`, `Herblore habitat
and several other rate optimizations (#193)`). The newer
`src/main/java/com/rs/game/content/minigames/herblorehabitat/JadinkoType.kt`
and `HerbloreHabitat.kt` are restoration-era files, so the period oldids above
supply the visible values; the reconstructed files only corroborate the route
shape and expose the personalised weekly god-environment state that a future
implementation must not replace with a fixed default.

### Fallback gate: Dragon-impling tips

Dragon arrowtips and Dragon dart tip remain root orphans. The live Hunter path
can reach Hunter 83 from ordinary level-one targets, buy Impling jars and nets
from live shops, catch either Dragon-impling target, consume one empty jar, and
produce one Dragon impling jar. Positive controls show the same gate probe
accepting the level-one Crimson swift and rejecting Baby/Dragon implings below
their required levels.

The route stops after the catch. Dragon impling jar appears in neither
`ITEM_PACK_DATA` nor `CONSUMABLE_DATA`; the bank UI exposes `Open` only for the
former, and the consumable path returns `not_a_consumable` for the latter. No
live reward table or handler opens the jar, so the audit correctly reports no
producer for either tip. Implementing the pair would first require a general
impling-jar opening/reward mechanism, not merely two acquisition rows.

### Fallback gate: Spider carcass chain

The live transformation framework exists, but both roots and the requested
return mechanic are absent. `Utility:skewer_spider_on_a_stick` consumes one
Spider carcass and one Skewer stick for one Raw spider on stick;
`Cooking:cook_spider_on_a_stick` then consumes the raw item at Cooking 16 for
one `Spider on stick`. The final spelling has no second `a`.

The audit reports Spider carcass and Skewer stick as separate root orphans and
Raw spider on stick as their cascade orphan. The level-one Spider combat target
is attainable, but its live drop table has charms only and no carcass. No live
shop, combat, quest, gathering, or activity source produces either root. The
skewer transform declares no Skewer-stick byproduct, and the generic utility
runtime therefore consumes it permanently. Grand Tree Groceries independently
sells the finished Spider on stick, but that bypass does not make the requested
carcass-to-raw-to-cooked chain or returned-stick loop live.

Positive controls distinguish the absence from a broken probe: zero-input
`Gather swamp toads` is reachable and executable at level one, while Dramen
branch remains correctly blocked behind its unavailable quest-stage action.
Thus the Spider family would require two acquisition producers plus a corrected
return transformation, not a narrow one-root slice.

### Crab-family correction

Fresh crab claw and Fresh crab shell have authentic producers. The producer is
a distinct Crab NPC, not the Mogre table checked in the earlier triage: the
period evidence is Crab oldids `4905238`, `5906508`, and `6522171`, and Darkan
combat definitions for NPCs `3424` and `3421` predate the fleet instrumentation.
The family is nevertheless inert because its combat gate requires partial
completion of `recipe_for_disaster_freeing_pirate_pete`, whose three stage
actions have no emitter. The earlier conclusion (blocked) stands, but the stated
reason (no pinned producer) was wrong.

The existing quest-gated `dagannoth` and `cave_horror` enemies may have the same
pre-existing defect: a completion check can point at an uncompletable quest.
That suspicion is recorded for the future emitter pass; this slice did not
investigate or change either enemy.

## Reachability and verification

| Metric | Before | After | Change |
| --- | ---: | ---: | ---: |
| Actions | 1,556 | 1,560 | +4 |
| Reachable items | 2,493 | 2,497 | +4 |
| Orphan inputs | 103 | 99 | -4 |
| Blocked actions | 102 | 102 | 0 |

The four new actions are `Hunter:track_shadow_jadinko`,
`Hunter:track_diseased_jadinko`, `Hunter:catch_cannibal_jadinko`, and
`Hunter:catch_guthix_jadinko`. They make exactly Shadow vine, Corrupt vine,
Plant teeth, and Guthix vine newly reachable; each disappears from the orphan
set. Existing Herblore consumers now receive authentic producers.

A deliberate mutation changed the Shadow route to emit `Mutated shadow vine`.
`test_hunter_handler_runs_the_jadinko_secondary_routes_end_to_end` failed on the
exact inventory mismatch, then passed after restoration. Focused pure, runtime,
registry, asset, and placeholder checks pass six tests. Full plain discovery
passes 4,061 tests with 496 expected skips. The real offscreen Qt corpus passes
all 4,061 tests with three expected skips when split into independent processes;
the monolithic process exceeded the ten-minute command cap without a terminal
failure. The four processes covered 723, 722, 1,727, and 889 tests.

Ordinary tool supply is live: Noose wands cost 4 Coins in Aleck's, Ayleth's, and
Nardah Hunter shops; Papa Mambo's Shop stocks 30 Marasamaw plants at 38 Coins.
The routes require normal skill progression and those reusable tools. The
sixteen emitter-blocked roots remain untouched. The Dragon-impling pair still
needs a general jar-opening reward path. The Spider chain still needs producers
for both Spider carcass and Skewer stick plus the authentic returned-stick
transformation.
