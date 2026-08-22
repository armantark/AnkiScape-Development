# Achievement Diary: clause-by-clause completion record

## Supersession — 2026-08-03

The 2026-07-27 conclusion that 384 regional rows were unreachable is historical
and no longer governs implementation. The newer owner-settled curation contract
in `memory-bank/achievement-diary-item-grants-design.md` explicitly permits
same-family task redistribution plus one to three generic progression anchors
per tier. The catalog now has eight regional families × four tiers × twelve
rows = 384.

The implementation preserves each authentic task's original-tier durable ID
and records any curated destination in its source note. Twenty-two remaining
slots are visibly flagged `curation_anchor`; every one reuses an exact
skill-level requirement recovered from the same family, and no tier exceeds
three. All 422 prior catalog task IDs remain. The 67 authentic tasks whose live
deed telemetry is still absent remain honest unavailable rows and do not receive
invented completion predicates. This section supersedes D1 and "Why 384 is
unreachable" below; the rest of the dated audit remains useful history.

Date: 2026-07-27. Supersedes the diary sections of
`pass3-audit-2026-07-26.md`, which measured the family before this work.

`main` stands at 3,169 tests, green in both lanes. The family ships **310 tasks**
across 8 families, 34 tiers and pools, and **8 condition kinds**.

## The sixteen design-contract clauses

| # | Clause | Verdict | Proof |
| --- | --- | --- | --- |
| D1 | Eight families, four tiers, 384 regional tasks | **NOT MET** | 310 ship. See "Why 384 is unreachable" below. |
| D2 | Burthorpe/Taverley set with its starter-equipment reward | **MET** | `test_burthorpe_claim_grants_its_starter_equipment_reward` |
| D3 | Miscellaneous pool with sourced coin rewards | **MET** | 30/30 paid through real handlers; ordinal growth proven |
| D4 | Ready to Claim, taskmaster portrait, one-click claim | **MET** | `test_every_ready_claim_taskmaster_portrait_matches_its_family` |
| D5 | Sequential claiming across tiers | **MET** | later tiers refused until predecessors claimed |
| D6 | One atomic claim grants item plus lamp | **MET** | 32/32 with exact item and lamp deltas |
| D7 | A tier upgrade replaces its predecessor | **MET** | no duplication in bank or worn slots |
| D8 | Taskmaster state, gold seal, one-time presentation | **MET** | second acknowledgement refused |
| D9 | One pinned task, held at the top | **MET** | pin, replace, clear, undo |
| D10 | Cabinet with shared search and filters | **MET** | backend and offscreen UI |
| D11 | Fabricated rows gone from player-facing surfaces | **MET** | all 171 prior task ids retained underneath |
| D12 | Every skillcape, trim and keepsake | **NOT MET** | 24 of 25. Dungeoneering blocked; see below. |
| D13 | Equipped skillcape sets effective level 100 | **MET** | moves 49 roll paths, measured, not 1 |
| D14 | Milestone capes wearable with an all-skills gate | **MET** | woven by the real Crafting handler, then equipped |
| D15 | Quest point, Max, Completionist, Veteran capes | **NOT MET** | all four obtainable; the Max gate counts 24 skills |
| D16 | Music Log with the 350-task unlock | **MET** | every track has a row; the unreachable one is labelled latent |

Thirteen met, three not.

## Why 384 is unreachable

The period catalog holds 534 tasks. 310 ship. The rest were **deliberately
omitted, not missed**: they have no predicate AnkiScape can evaluate, and a task
no predicate can satisfy is a row that can never complete.

A nine-agent survey re-derived the omitted list from Darkan and classified every
one. Only two new condition kinds survived scrutiny — `any_of` for a task with
several valid routes, and `derived_value` for computed totals such as museum
Kudos — and together they recovered 6 tasks. Everything else needs telemetry the
game does not record, or depends on geography, emotes and inventory choreography
that the contract's own curation rules say to drop, or rests on content that does
not exist.

384 was therefore never reachable at full fidelity. Closing the remainder means
recording new telemetry, which is a product decision rather than a harvest.

## Why D12 and D15 are blocked rather than unfinished

Nothing in the shipped runtime writes Dungeoneering experience, so no save reaches
99 in it. Shipping its skillcape would create a row no player can buy, which is
the exact defect this programme spent two days removing. The period row stays
complete in `SKILLCAPES` and joins the shipped list automatically when the skill
exists.

The same gap blocks D15's 25-skill Max gate. Enforcing the period's 25 today would
make Max, Completionist **and all nine milestone capes** permanently unobtainable,
so the gate stays registry-derived and the shortfall is stated aloud through
`latent_cutoff_skills_pure()`. Design fork 3.11 records the choice.

## What the independent verification changed

Every part of this family was written by Claude models, so a Sol pass verified it
by driving the real logic. It found six defects that the building agents had
reported as passing, and disproved one claim outright:

1. Burthorpe's claim was inert — it granted nothing and printed a message with a
   hole where the item name belonged.
2. Losing Quest point cape eligibility did nothing; the cape stayed worn and
   re-equippable.
3. The Music Log rendered twelve rows and dropped 179, so its one latent track was
   invisible rather than labelled.
4. The Dungeoneering cape and the 25-skill Max gate were absent.
5. The claim that a worn skillcape moves one roll was **false**: it moves 49.
   Darkan interpolates on `level / 99.0` without clamping, so the success tables
   do not all saturate at 99. Hunter alone carries 43.
6. 149 numeric thresholds carried no citation, no placeholder marker and no
   abstraction comment. Classified: 16 sourced, 140 AnkiScape abstractions, 0
   placeholders. None is period content.

Two of the fix instructions were themselves wrong and were resolved toward the
source instead: Burthorpe's reward is a set kit from Major Nigel Corothers rather
than per-task rewards, and enforcing the 25-skill gate would have broken three
cape families.

## The defect class that keeps recurring

Three times this week, "absent from the source I checked" was recorded as "does
not exist": Spria's chathead, the Burthorpe roster, and eighteen task rows dropped
because their requirements were missing from one enum. Each time the complete
history or a second source had the answer.

A fourth instance shipped inside a test: two files carried a cut-down condition
evaluator that silently skipped kinds it did not recognise, so an entire Varrock
tier became unfinishable the moment `derived_value` arrived and the tests still
passed. They now use the strict helper, which raises on an unknown kind.
