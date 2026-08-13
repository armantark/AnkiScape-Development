# Acquisition triage and quest-emitter blast radius — 2026-08-12

## Scope and outcome

The acquisition program began from the corrected reachability baseline on
`goal/acquire-2026-08-12`: 1,556 actions, 2,493 reachable items, 103 orphan
inputs, and 102 blocked actions. Its initial Snake-hide triage was read-only: the
authentic Bush-snake route is inert for an ordinary player because Tai Bwo
Wannai Cleanup requires Jungle Potion, Jungle Potion requires Druidic Ritual,
and both quests stop on un-emitted `required_actions`.

A later Hunter slice proved that the program as a whole was not blocked. Commit
`16375023` shipped four Jadinko routes, moving the live graph to 1,560 actions,
2,497 reachable items, 99 orphan inputs, and 102 blocked actions.

## Improved branch-relative reachability baseline — 2026-08-13

Reachability figures are branch-relative. Quoting a figure without naming the
exact tree on which it was measured is meaningless.

| Tree | Actions | Reachable items | Orphan inputs | Blocked actions | Seed items |
| --- | ---: | ---: | ---: | ---: | ---: |
| `main` at `1cf43931` | 1,556 | 2,573 | 102 | 101 | 1,448 |
| `goal/acquire-2026-08-12` at `2cfac317` | 1,568 | 2,509 | 97 | 100 | 1,367 |
| `goal/reachability-truth-2026-08-13`, based on that acquire tip | 1,568 | 2,248 | 100 | 103 | 1,099 |

The improved baseline removes quest-stage products after the first missing
required action or registered unsatisfiable combat encounter, completion rewards
from quests blocked by those gates, and start inventory from quests that cannot
start. It propagates failed prerequisites and the 12 available quest points to a
fixed point, so Dragon Slayer remains below its 32-point start gate. The 100
orphans split into 54 root and 46 cascade. The three newly orphaned quest rewards
are exactly Blood talisman, Jade vine seed, and Magic secateurs.

This is strictly better than 2,509, but it is not a corrected acquisition count.
It can be too high and too low at the same time. Goblin Diplomacy is classified
completable even though stages 1 and 2 consume unreachable Orange and Blue goblin
mail (`data/quest_data.py:6648-6666`), because required and consumed inventory,
tools, item alternatives, and routes are outside this model. Shield of Arrav is
a concrete route example: stage 4 requires joining one gang, but route state is
not evaluated, so a route-gated stage can still leave later products and rewards
eligible if its actions otherwise pass. Conversely, variant handling can
over-block a quest when one impossible branch sets the quest-wide flag even if
another branch could finish.

Owner decision for the later coordinated gate model: either (A) count only a
route proved complete across actions, routes, combat, and variants, or (B) keep
separate optimistic and proven route totals. This audit records the fork without
choosing it.

The combat invariant now reconciles the two facts the tool already held: an
unsatisfiable registered encounter blocks both its stage products and quest
completion rewards. The earlier model could know the encounter was blocked and
still call the quest completable, the same contradiction as knowing a stage was
blocked while counting later stages. A synthetic regression pins both outputs.
The current six-quest set and all acceptance totals remain unchanged: four quests
have no encounters, and every registered encounter in Diamond in the Rough and
Stolen Hearts passes the existing predicate.

The predicate is narrower than its name suggests. Encounters with no registered
`guaranteed_drops` hit the early `continue` and never enter
`blocked_combat_products`, so they cannot currently block completion. Required
and consumed inventory, tools, item alternatives, and `required_routes` are also
unmodelled.

Only three live quests have variant rows: Shield of Arrav, Heroes' Quest, and
Temple of Ikov. All three already fail on common or mandatory required-action
stages before their branch choices, so the new persistent hard-stop introduces
no current-data variant regression. The latent variant model is nevertheless
wrong in both directions: one impossible branch can reject a quest globally,
while later mandatory rows pool emitted actions from mutually exclusive branches.

The recommended eventual design is one stage-satisfiability predicate inside a
quest-progression fixed point integrated with item reachability: evaluate actions,
inventory and tool alternatives, routes, combat, and variant-local state per
path, then accept a quest when any one complete path survives. Layering one
action-only exception and then one combat-only exception is the mechanism by
which this file keeps acquiring partial gates while appearing more complete.
That redesign has no verified target count and belongs in a separate slice rather
than being improvised here.

## Stage-satisfiability closure — 2026-08-13

The audit now uses one stage predicate for required and consumed inventory,
required tools, item alternatives, required actions, route state, and combat.
Combat is evaluated even when an encounter has no registered guaranteed drop.
Rows are partitioned into shared and variant branches before traversal, evaluated
in stage order, and a quest is accepted when at least one branch completes.

The closure is joint: ordinary actions can unlock quest stages, quest stages and
rewards can unlock ordinary actions, and the process repeats to stability.
Mutually exclusive branches are evaluated as separate world states; only items
reachable in every branch-selection scenario enter the global acquisition graph.
A choice route becomes available at its declared choice stage, never at quest
start. Quantity gates distinguish repeatable acquisition routes from finite
one-shot supplies, consume finite supplies between stages, and preserve the
runtime's required-option tool semantics versus consumed-option inventory
semantics.

The final pinned baseline is unchanged at 1,568 actions, 2,248 reachable items,
100 orphan inputs, 103 blocked actions, and 1,099 seed items. An independent
throwaway implementation recomputed the same five figures. The isolated current-
data effects of the five reviewed defects are all zero on those aggregate figures:
fixed-point closure, quantity accounting, branch-product isolation, route timing,
and diagnostic deduplication each leave the five totals unchanged when toggled
alone. That cancellation-free result is not evidence the defects were harmless;
synthetic reproductions show each decision error directly, and the repaired
invariants prevent future data additions from silently moving the graph in the
wrong direction.

Five quests change from the former action-only verdict to blocked:

- `goblin_diplomacy`: stage 1 needs unreachable `Orange goblin mail`; Goblin
  Diplomacy is correctly uncompletable. Stage 2 also needs unreachable `Blue
  goblin mail`.
- `icthlarins_little_helper`: its inventory/tool path is not satisfiable from
  the acquisition graph.
- `shilo_village`: its stage requirements are not jointly satisfiable.
- `smoking_kills`: its item and cat-alternative gates are not satisfiable.
- `the_knights_sword`: its required inventory path is not satisfiable.

The Shield of Arrav duplicate diagnostic review finding reproduced before the
repair: the real build emitted two byte-identical stage-one rows. Those rows
appeared only in `blocked_quest_stage_products`; the blocked-actions figure is
computed from unresolved ordinary actions and remained 103. The branch traversal
now deduplicates the diagnostic, and the real build emits exactly one row.

Remaining deliberate model limits are narrower than the previous quantity-free
model. Repeatable supply proves arbitrary quantity but does not model time or
currency cost; finite supply tracks known initial and quest-local counts but does
not solve arbitrary inventory allocation between independent quests. Exact-state
equipped items and toolbelt substitutions are represented only by direct item
names plus the runtime-compatible Pickaxe/Hatchet/Axe family checks; arbitrary
equipment slots and future toolbelt families remain unmodelled. Free-form routes
without an explicit quest choice remain blocked because no route emitter exists.

Five correctness defects survived a focused green suite because the tests shared
the implementation's mental model: no cross-quest reward chain, no finite-count
counterexample, no mutually exclusive product consumer, no late-choice route,
and no real duplicate-diagnostic assertion. Each reviewer reproduction is now a
permanent synthetic regression, and the Shield of Arrav live case asserts one
stage-one diagnostic row.

Measured efficiency work remains deliberately declined. Rebuilding branch
metadata costs about 80 ms per report, and repeated focused report builds cost
about 0.5 seconds. Caching either would add invalidation state around a
correctness-sensitive fixed point for no material user benefit.

The maintenance rule is: everything that decides or feeds satisfiability gets one
implementation, while reporting may only describe the retained decision. Similar
parsers are not interchangeable: item records, alternative mappings, quantities,
and tool semantics require distinct normalization.

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

### Closed gate: Dragon-impling tips

Dragon arrowtips and Dragon dart tip now have a filled-jar Loot action. The live
Hunter path can reach Hunter 83 from ordinary level-one targets, buy Impling
jars and nets from live shops, catch either Dragon-impling target, consume one
empty jar, and produce one Dragon impling jar.

The corrected quest-gate probe iterates all 28 `QUEST_UNLOCK_RULES` and calls
`hunter_target_locked_reasons_pure`. It finds exactly one `catch_ferret` rule and
returns `("Eagles' Peak",)` as the positive control. It finds exactly one row
for each tested Baby/Dragon target and returns no quest lock for
`catch_baby_impling_puro_puro`, `catch_dragon_impling_puro_puro`, or
`catch_dragon_impling_world`. Darkan's separate Puro-Puro entry check permits
entry unless the player carries a Magic box; it has no quest condition. Darkan's
catch handler independently gates Pirate implings behind Rocking Out but not
Dragon implings. The quest gate is therefore clear.

Revision-742 cache item `11256` exposes `Loot`; the pinned period Wiki revision
`6151109` enumerates the Dragon-impling rewards; and Darkan's original
`dragon_impling.json` at commit
`c6fbe036b1743f4dd6067ec178332c69c3708856` supplies probabilities and quantity
ranges. The action keeps source-enumerated rewards that have live AnkiScape item
identities, reserves omitted probability as an empty registered-result row, and
does not renormalise the table. Darkan's defective finished-ammunition rows
`11212` and `11230` are excluded. The generic registry and pure opener can host
other filled jars, but only Dragon has a source-audited table in this slice.

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

| Metric | Before jar action | After jar action | Change |
| --- | ---: | ---: | ---: |
| Actions | 1,561 | 1,562 | +1 |
| Reachable items | 2,498 | 2,503 | +5 |
| Orphan inputs | 99 | 97 | -2 |
| Blocked actions | 102 | 100 | -2 |

The new `Item action:loot:Dragon impling jar` action makes Dragon arrowtips and
Dragon dart tip newly reachable; both disappear from the orphan set. Their live
Fletching consumers then make Dragon arrows and Dragon darts reachable. The loot
action also makes Amulet of glory reachable because it had no prior producer,
while Dragon longsword, Dragon bolt tips, Dragon bolts, Dragon bones,
Dragonstone, Magic seed, Dragonstone ammy, Snapdragon seed, Summer pie, and
Death tiara already had routes. The Hunter jar route remains
`Hunter:catch_dragon_impling_puro_puro`.

Nine of the eleven candidate roots remain blocked. The dominant cause is still
the missing production quest-action emitter: 185 of 196 quests are directly
action-blocked, and prerequisite closure raises the approximate impact to 190
of 196. Outside that common cause:

- the Spider-on-stick chain still needs a Jungle spider carcass producer, a
  thatching-spar Skewer-stick source, and consumption that returns the stick;
- Relicym's balm shop access remains circular without the un-emitted Zogre Flesh
  Eaters progression that first supplies balm and unlocks Uglug; and
- Curly root still needs its Jadinko-Lair curly-vine Woodcutting producer rather
  than only the existing Firemaking consumer.

A deliberate mutation changed the Shadow route to emit `Mutated shadow vine`.
`test_hunter_handler_runs_the_jadinko_secondary_routes_end_to_end` failed on the
exact inventory mismatch, then passed after restoration. The Dragon-jar slice
also mutated `Dragon dart tip` to `Dragon dart tip MUTATION`; the ordinary-player
integration test failed on that exact reward mismatch and passed after
restoration. A later correctness review fixed the sourced rare-row weights,
restored registered Dragon bolt tips, Dragonstone ammy, and Death tiara rewards,
and added RNG rollback when undo registration fails. The final plain lane passes
4,072 tests with 497 expected skips in 329.278 seconds. The final offscreen Qt
lane passes all 4,072 tests with three expected skips in 716.844 seconds.

Ordinary tool supply is live: Noose wands cost 4 Coins in Aleck's, Ayleth's, and
Nardah Hunter shops; Papa Mambo's Shop stocks 30 Marasamaw plants at 38 Coins.
The routes require normal skill progression and those reusable tools. The
sixteen emitter-blocked roots remain untouched. The Dragon-impling pair now uses
the general jar-opening reward path. The Spider chain still needs producers for
both Spider carcass and Skewer stick plus the authentic returned-stick
transformation.
