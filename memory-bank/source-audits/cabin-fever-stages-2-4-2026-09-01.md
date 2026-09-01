# Cabin Fever stages 2–4 source audit — 2026-09-01

## Scope

This audit replaces the three generated `Complete Cabin Fever stage N
objective` requirements that blocked stages `2`, `3`, and `4`. Each sentinel is
removed through `remove_required_actions` and replaced by a same-stage action
mapped from the frozen Cabin Fever contract. The slice also reconciles the
completion unlock list with that contract and applies the missing Cabin Fever
gate to Fever spider Slayer assignments. It does not add quest-item custody
nodes, combat encounters, combat drops, placeholder values, or user-interface
code.

No source was harvested, revised, or repinned.

## Frozen evidence ownership

The controlling contract is the already-frozen Darkan dossier:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/cabin-fever-target-contract.json`

Its baseline world commit is
`2f27fcac31e1724f1f871598cc0c8c263e03707c`, its baseline world tree is
`bf13de394d44134f0ae39a7372f69e39764598ca`, and its verdict ceiling is exactly
`PARTIAL[source_blocked]`.

The complete pinned source set used by this slice is:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/cabin-fever-build727-oldid-5870979.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/cabin-fever-final-preeoc-oldid-6533785.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/cabin-fever-transcript-history.json`

The transcript-history record confirms that neither transcript title has a
pre-cutoff revision. The earliest full transcript is comparator-only, so this
slice makes no exact dialogue, choice, cutscene, camera, animation, sound,
music, or presentation claim.

## Read-only executable corroboration

A mixed-extension search under the read-only Darkan quest tree found the Cabin
Fever implementation in Kotlin:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/cabin_fever/CabinFever.kt`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/cabin_fever/CabinFeverState.kt`

`CabinFeverState.kt:7-23` fixes the quest-item identities, including `Rope`
`7155`, `Fuse` `7109`, `Repair plank` `7148`, `Tacks` `7150`, `Plunder` `7143`,
`Cannon barrel` `7145`, `Ramrod` `7120`, `Gunpowder` `7108`, `Canister` `7149`,
`Cannon balls` `7147`, and `Book o' piracy` `7144`. `CabinFever.kt:31-39`
orders the journal from enemy-cannon sabotage through hull repair, ten plunder,
cannon repair, one canister hit, and three cannonball hits.

The executable transactions corroborate the contract: one rope is consumed per
swing (`CabinFever.kt:116-123`); lockers bound replacement supplies to unfinished
work (`:125-157`); fuse sabotage retains the tinderbox (`:159-167`); each of
three hull repairs consumes two planks, ten tacks, and one paste (`:170-191`);
ten plunder are consumed once (`:194-205`); and the cannon enforces barrel
repair, gunpowder-ramrod-payload-fuse loading, cleaning, one canister hit, and
three cannonball hits (`:208-283`). Completion applies exactly the three
`7,000` XP awards and one Book o' piracy (`:286-293`), while the completed
travel endpoint is Mos Le'Harmless (`:324-329`).

## Stage mapping

The frozen contract's route fields align with the existing four-row AnkiScape
journal as follows:

| AnkiScape stage | Frozen route fields | Source-backed action | Mandatory fight |
| ---: | --- | --- | --- |
| `1` | Existing start and Port Phasmatys travel cleanup | Reach the Port Phasmatys charter route. | None |
| `2` | `enemy_cannon`, `hull_repair` | Swing between the ships, consuming one quest rope per swing, disable the enemy cannon with one fuse and a retained tinderbox, then repair exactly three hull holes with two repair planks, ten tacks, and one swamp paste each. | None |
| `3` | `plunder` | Steal exactly ten plunder from the enemy hold and store it once aboard The Adventurous. | None |
| `4` | `cannon_repair`, `canister_and_cannonballs`, `completion` | Repair the broken cannon with one barrel, load every shot in gunpowder-ramrod-payload-fuse order, then score one canister hit and three cannonball hits with the retained tinderbox, cleaning between shots. | None |

The assembled catalog contains exactly four requirement rows with stage set
`{1, 2, 3, 4}`. Stages `2`, `3`, and `4` contain no required-action sentinel,
external inventory gate, required tool, or combat encounter.

## Quest-item custody boundary

The frozen contract treats the route materials as quest-local supplies and
ordered transactions:

- each ship swing consumes one quest rope;
- enemy sabotage attaches and lights one fuse while retaining the tinderbox;
- exactly three hull holes each consume two repair planks, ten tacks, and one
  swamp paste, for six planks, thirty tacks, and three paste in total;
- exactly ten plunder are collected and consumed once by The Adventurous's
  storage;
- one cannon barrel repairs the cannon;
- each shot is loaded in gunpowder, ramrod, payload, and fuse order;
- one valid canister hit advances the route;
- three valid cannonball hits sink the enemy ship;
- the ramrod cleans the cannon between shots, and misuse requires a replacement
  barrel.

AnkiScape has no quest-local acquisition and custody model for this chain. The
slice therefore records the exact transactions in automatic stage actions
rather than inventing external item sources or making globally obtained generic
items stand in for shipboard quest supplies. The frozen continuity contract
expressly treats a correctly prepared shot as a hit because the historical hit
rolls remain source-blocked.

The exact item-model follow-on identities are `Rope` (`7155`), `Fuse` (`7109`),
`Repair plank` (`7148`), `Tacks` (`7150`), `Plunder` (`7143`), `Cannon barrel`
(`7145`), `Ramrod` (`7120`), `Gunpowder` (`7108`), `Canister` (`7149`), and
`Cannon balls` (`7147`). Generic `Rope`, `Swamp paste`, and `Cannonball` already
have global routes, but those routes do not prove the quest's bounded locker,
hold, loading, cleaning, and replay rules.

## Encounters and guaranteed drops

No Cabin Fever stage action requires the player to kill an enemy. The frozen
contract leaves exact pirate aggression, combat rolls, positioning, respawn
timing, and multicombat behavior source-blocked. The assembled quest had no
Cabin Fever combat encounter before this slice and still has none afterward.
Consequently, there is no boss, no quest combat drop, and no
`guaranteed_drops` row to add or relocate.

Because Cabin Fever needs no encounter relocation, the byte-identical
`relocate_combat_encounters` functions in `data/zogre_flesh_eaters_data.py` and
`data/rum_deal_data.py` remain untouched. No third copy or shared registry was
introduced.

## Completion rewards and unlocks

The frozen contract states that completion grants exactly:

- `2` quest points;
- `7,000` Smithing XP;
- `7,000` Crafting XP;
- `7,000` Agility XP;
- one retained `Book o' piracy`;
- Mos Le'Harmless travel;
- Fever spider Slayer assignments;
- Cave horror Slayer assignments;
- Jungle horror Slayer assignments.

The two Squeal of Fortune spins are explicitly excluded. The existing quest
point, XP, and item-reward rows already matched the contract and remain
unchanged. `Book o' piracy` is present in `ITEM_DEFINITIONS`, so this slice
introduces no granted-but-unregistered item.

The generated unlock replacement previously included `Charter Ship prices are
halved.` and omitted the Fever spider and Jungle horror assignment unlocks. The
frozen completion list now controls the four catalog unlock strings. Cave and
Jungle horror families already carried the Cabin Fever quest gate. Fever
spiders did not; their family now requires `cabin_fever`, and a focused runtime
predicate test proves the assignment is blocked before completion and unlocked
afterward. The exact charter-discount implementation remains source-blocked and
is not claimed as a completion unlock by this slice.

A shown-dialog offscreen Qt check expanded Cabin Fever in the real Quests tab
after layouts activated. At `1280×752` and `900×560`, the complete four-part
Unlocks label rendered on one line with no ellipsis or horizontal overflow. No
user-interface code changed.

## Sentinel translation and test oracle

Each of the three new cleanup rows removes its exact generated sentinel through
`remove_required_actions`. This is required because automatic actions are
recorded only after the current stage passes its blockers; adding an automatic
action without removing the sentinel would leave Cabin Fever impassable.

The focused action oracle in `tests/test_cabin_fever_completion.py` transcribes
stage actions as literals and cites the frozen contract path and route fields.
It does not derive expected strings from the cleanup table under test. Unit
coverage pins the four-row count, stage set, source paths, prerequisite quests,
skill levels, empty encounter distribution, exact rewards, unlocks, and item
registration. Pure integration coverage exercises a real skill gate, all four
stage transitions, durable action proofs, completion XP, quest points, and the
full inventory delta. The end-to-end test reads the dynamically loaded add-on's
own catalog, asserts both row count and stage set, and drives the real
`on_answer_card()` review-answer entry point to completion.

The measured completion inventory delta is exactly:

- `Book o' piracy ×1`.

The starting `Coins ×3,500` and `Tinderbox ×1` remain unchanged. No quest-local
material is silently granted or retained by the generic stage engine.

## Reachability measurement

The baseline was measured from branch parent
`590348dff7811e913ae1cc629e50aac9777b4b7d`; the result was measured from the
corrected implementation tree.

| Measure | Before | After |
| --- | ---: | ---: |
| `action_count` | `1663` | `1663` |
| `reachable_item_count` | `2304` | `2343` |
| `orphan_input_count` | `165` | `163` |
| `root_orphan_count` | `32` | `31` |
| `cascade_orphan_count` | `133` | `132` |
| `unresolved_action_count` | `252` | `249` |
| `seed_item_count` | `1219` | `1230` |
| blocked quest-stage rows | `137` | `136` |
| `completable_quest_count` | `53` | `54` |

Before the repair, `cabin_fever` had one blocked row at stage `2`, missing
`Complete Cabin Fever stage 2 objective`. After the repair, it has no blocked
row and is the one newly completable quest.

The closure contains thirty-nine newly reachable registered item routes, but
this slice directly produces only `Book o' piracy -> quest:cabin_fever`. The
other thirty-eight are existing descendant combat, shop, Farming, and Trouble
Brewing routes whose pre-existing Cabin Fever gates can now pass. They are
measured in the global pins but are not claimed as direct outputs of this
slice.

## Verification

The explicit quest-catalog module passes all `37` tests. Both required full
lanes are green:

```text
Ran 4611 tests in 885.390s
OK (skipped=515)
```

```text
Ran 4611 tests in 1158.408s
OK (skipped=3)
```

The plain and Qt runs each created and returned their temporary guarded test
worktree after the unittest summary.

## Follow-on leads

The quest-local custody model remains the direct follow-on. It must represent
bounded locker recovery, one-rope-per-swing consumption, fuse attachment and
lighting, exact hull-material consumption, ten-plunder storage and leave loss,
cannon break and replacement, ordered loading, cleaning between shots, and
one-shot completion without inventing global acquisition routes.

The source-blocked exact swing failure chance, run-energy loss, equipment
behavior, pirate combat behavior, plunder respawn timing, shot hit rolls,
positioning, inventory-full messages, and charter-discount implementation remain
outside this stage-sentinel slice. No placeholder was registered for any of
them.
