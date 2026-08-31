# Priority-matrix rulings — design thread to harvesting loop

Date: 2026-08-13. Author: the design thread. Consumer: the harvesting-loop
orchestrator and its dispatched agents.

## 1. Goal

This ledger replaces intuition-based work selection in the headless harvesting
loop with one scored formula. The owner approved each ruling below on
2026-08-13. When the loop selects work, the loop must obey this ledger.

## 2. Scope

The matrix governs the headless harvesting loop only: acquisition gaps,
placeholder values, catalog depth, missing content, and shared plumbing.

The matrix does not govern:

- Owner playtest passes (Pass 8, Pass 9, and later passes). The design thread
  orchestrates those directly. A new pass preempts scored work.
- Owner design decisions. Those stay in `memory-bank/design-thread-queue.md`.

## 3. Rulings

1. **R1 — no blocked class.** No item is "blocked". An item is "deferred" with
   a recorded reason. When the evidence order is exhausted and no period data
   exists, the loop must invent the value and register it in
   `memory-bank/placeholder-values.md`.
2. **R2 — score everything.** Every backlog item gets a score. A deferred item
   keeps a DEFERRED tag and its reason, and stays in the ranked list.
3. **R3 — override lane.** Three defect classes go to the front of every
   queue, before all scored work: save corruption, review blockers, and undo
   breakage. A crash without state damage is a normal scored defect.
4. **R4 — the formula.**
   `priority = Reach × StageWeight × Gap × SubstrateBump × EvidenceBump`.
5. **R5 — Reach.** Reach uses the surface tier: review-path surface = 3,
   opt-in activity = 2, endgame-only = 1. Inside one tier, the leverage number
   from `tools/audit_item_reachability.py` (transitive item and action gain)
   sets the order.
6. **R6 — StageWeight.** Early = required level 30 or lower and no quest
   gate, weight 3. Mid = level 31 to 60, or one short quest chain, weight 2.
   Late = level 61 or higher, or a deep chain, weight 1.
7. **R7 — Gap.** Player-visible defect = 3. Absent period mechanic = 2. Live
   mechanic with a placeholder value or a thin catalog = 1. Complete = 0.
8. **R8 — SubstrateBump.** An item that changes behavior in five or more
   families or call sites gets ×2. Count the call sites in code.
9. **R9 — EvidenceBump.** A row whose evidence already sits on local disk
   (the rev-727 cache, the Darkan checkout, other on-disk caches) gets ×1.5.
10. **R10 — slice first.** A large program enters as a family. The loop scores
    and works one atomic slice at a time (one quest, one placeholder row, one
    handler). On equal scores, the smaller slice goes first.
11. **R11 — re-score cadence.** The loop must re-score the ledger at each
    queue audit, after each merged batch.
12. **R12 — relation to the goal text.** This matrix is the concrete form of
    the goal sentence "prioritize shared tooling, player-visible defects,
    readily recoverable period values, registered placeholders, and recorded
    data-depth debt". The goal text does not change. When the two disagree,
    this ledger wins.

## 4. Override lane — current contents

| Item | Evidence | Size |
|---|---|---|
| Cadence kernel raises `ValueError` on an oversized persisted credit | `logic/cadence_kernel.py:243-254`; type sanitization at `:107-127` does not cover valid oversized integers; no recovery test exists | ~10 model-minutes |

Note: the owner reports the in-review lag as fixed. No override entry exists
for it. The loop does not need to act.

## 5. Initial scored ledger — top 10

The design thread scored the visible backlog on 2026-08-13. The factor columns
show the arithmetic. GATE-1 (section 6) governs this table.

| # | Item | R | S | G | Bumps | Score | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Missing quests, per-quest slices | 2 | 3 | 2 | ×1.5 ev | 18 | 167 absent definitions; start with unlock chains (Jungle Potion → Cave horrors); Darkan evidence on disk; order slices by leverage |
| 2 | Bestiary expansion, per-family slices | 2 | 3 | 2 | ×1.5 ev | 18 | Beyond the current 130 enemies; Darkan and cache evidence on disk; order by leverage |
| 3 | Undo-seam migration | 2 | 3 | 1 | ×2 sub | 12 | 30 of 54 `_apply_*_command` handlers bypass `commit_direct_action` (`__init__.py:1010-1064`); one handler per slice |
| 4 | Daily Challenge reward XP | 3 | 3 | 1 | — | 9 | Placeholder `100 × required level`; branch `daily-challenge-xp-depth` holds one live commit of prior work |
| 5 | Quest rewards bypass the one-clue filter | 2 | 1 | 3 | — | 6 | `logic_pure/logic_pure_quest.py:1436-1461` skips the filter in `logic/treasure_trails_logic.py:105-164`; small route-through |
| 6 | rev-727 placeholder harvest, per-row slices | 2 | 2 | 1 | ×1.5 ev | 6 | Register rows with undecoded local evidence; harvest before more invention |
| 7 | Chaeldar readiness families | 2 | 1 | 2 | ×1.5 ev | 6 | Nine families short of 34/34; per-family slices |
| 8 | Evil Tree kindling period art | 2 | 2 | 1 | — | 4 | Last stale row from the tranche-2 art sweep; `assets_provenance.json:48054` |
| 9 | Dungeoneering payout curves | 2 | 1 | 1 | ×1.5 ev | 3 | Registered curves at `memory-bank/placeholder-values.md:177-185`; Darkan evidence |
| 10 | Housekeeping rider: stale selection records | — | — | — | — | rider | Retire `memory-bank/loop-queue.md:177` pause, the stale art row in `memory-bank/gpt-deferred-queue.md`, and the two-planned-skills framing in `memory-bank/roadmap.md` and `memory-bank/progress.md` |

## 6. GATE-1 — passed

The owner approved the section 5 table unchanged on 2026-08-13. The loop can
consume the ranked list under the section 7 rules.

## 7. Consumption rules for the loop

1. Take the override lane first.
2. Then take the highest scored slice that no agent holds.
3. Re-score at each queue audit (R11).
4. Record each new deferral reason in the item's register file.
5. When a score changes because an audit number changed, note the old and new
   score in the queue-audit record.

## 8. Corrections this ledger already applies

The 2026-08-13 read-only audit falsified these recorded claims. Do not select
work from them:

- "311 unsatisfiable quest steps" — no current audit produces that count. The
  blast-radius audit counts 994 rows that contain blockers; the reachability
  tool emits 187 first-block diagnostics. An exact count needs an enumerating
  audit without first-block short-circuits.
- Design-thread-queue 3.11 (the 24-of-25-skills Max premise) — stale.
  Dungeoneering is `partial` and trainable, and writes XP
  (`logic/dungeoneering_logic.py:2673-2702`).
- Design-gaps 5.1 ("31 handlers, no shared seam") — stale. The seam exists;
  the open work is the 30-handler migration (row 3 above).
- The GPT-queue art row — half stale. Wicked hood already has period art;
  only Evil Tree kindling remains (row 8 above).

## 9. Rulings made directly by the owner

These were given by the owner in conversation with the orchestration seat, not
relayed through the design thread. They carry full authority and outrank the
sections above where they conflict.

**O1 — Fable is out of the loop entirely.** Ruled 2026-08-13 13:49 PDT: "Fable
is critical on quota, so I need to start interfacing with you now. Do not talk
to or use Fable anymore." No dispatch to Fable, no consultation, no routing of
writing or design work to it, until the owner lifts this.

Consequences the next seat must plan around. Fable held product owner,
architect, and co-lead designer, and authored the ledger this file belongs to.
Sections 1 through 8 remain in force as written; they are a settled record, not
a live thread. Open design questions now go to the owner directly, as options
with a stated lean, at most one per report. Kimi K3 remains the other design
co-lead and the standing independent reviewer, but was itself over quota when
this was ruled.

**O2 — the goal is paused.** Ruled 2026-08-13 13:50 PDT, on the grounds that
the main quota is also over. Recorded through the goal's own pause mechanism in
`memory-bank/GOAL-BLOCKED.md`, which the goal text accepts as satisfying it.
That file names the blocker, what was tried, and the single unblocking
condition, and must be deleted before work resumes.

## 10. Queue-audit checkpoint — 2026-08-30

This audit uses `main` commit `d51f0f84df4d4cea3ab307954a01562f0b71f52d`.
It preserves sections 1 through 9 without edits.
The next section will apply the R4 formula after this checkpoint.

### Override lane verification

The cadence override defect is fixed.
`sanitize_cadence_profile_state_pure` still accepts nonnegative integers at
`logic/cadence_kernel.py:107-127`.
`advance_cadence_pure` now caps persisted credit at
`logic/cadence_kernel.py:243-253` before rate arithmetic.
A pure probe used a credit of `10^1000` with threshold `10`.
The call returned credit `0`, emitted one opportunity, and raised no exception.
No dedicated oversized persisted-credit regression test exists.
The current override lane is empty.

### Section 8 verification

| recorded claim | current result | current evidence |
| --- | --- | --- |
| `311` unsatisfiable quest steps | Still false. No tracked audit emits this measure. The current fixed point has 148 blocked quest-stage products and 284 unresolved actions. | `tools/audit_item_reachability.py:1950-1965`; `tools/audit_item_reachability.py:2036-2057` |
| Max requires 24 of 25 skills | Still false. Dungeoneering is partial and trainable. Floor completion still returns Dungeoneering XP. | `core/skill_registry.py:300-308`; `logic/dungeoneering_logic.py:2686-2702` |
| 31 direct-action handlers have no shared seam | Still false. A fresh Abstract Syntax Tree scan found 54 handlers, 54 seam calls, and 0 bypasses. | `memory-bank/design-thread-queue.md:1738-1744`; `__init__.py:1020` |
| Wicked hood has art, but Evil Tree kindling does not | Now fully false. Both asset rows and both files exist. | `assets_provenance.json:36954`; `assets_provenance.json:48402`; `woodcuttingitems/evil_tree_kindling.png:1` |

The direct-action correction in section 8 also contains a stale follow-up.
The stated 30-handler migration now has zero open handlers.
The art correction also has no open art row.

### New stale claims found by this audit

| location | stale claim | current evidence |
| --- | --- | --- |
| Section 5 row 1 | `167` quest definitions are absent. | The generated catalog has 194 rows. Two miniquests make 196 definitions. See `generated/quest_catalog_generated.py:12` and `data/quest_data.py:10844-10914`. |
| Section 5 row 3 | 30 of 54 direct-action handlers bypass the undo seam. | The fresh scan found 0 bypasses. See `memory-bank/design-thread-queue.md:1738-1744`. |
| Section 5 row 5 | Quest rewards skip the one-clue filter. | Quest completion calls the central filter at `logic_pure/logic_pure_quest.py:1530-1537`. |
| Section 5 row 8 | Evil Tree kindling is the last stale art row. | The asset and provenance row exist at `woodcuttingitems/evil_tree_kindling.png:1` and `assets_provenance.json:48402`. |
| Section 5 row 10 | All four housekeeping records remain open. | The pause record is checked at `memory-bank/loop-queue.md:200`. The roadmap uses the current skill model at `memory-bank/roadmap.md:8`. The GPT art row remains stale at `memory-bank/gpt-deferred-queue.md:21`. |

The other section 5 premises still hold at this checkpoint.
`COMBAT_ENEMY_DATA` still records 130 enemies at
`memory-bank/future-work-kanban.md:1374`.
Daily Challenge XP remains registered at
`memory-bank/placeholder-values.md:71`.
The placeholder register has 179 rows.
Chaeldar remains at 25 of 34 families at
`memory-bank/future-work-kanban.md:810`.
The Dungeoneering floor XP curve remains registered at
`memory-bank/placeholder-values.md:191`.

## 11. Re-score after the 2026-08-30 queue audit

### 11.1 Audit frame

This section updates the ledger under R11. Sections 1 through 10 stay unchanged. Their rulings remain authoritative, but later audit facts supersede stale checkpoint facts.

The audit uses code baseline `d51f0f84df4d4cea3ab307954a01562f0b71f52d`. At audit time, `main` was `fa24b0bf4208a6f6b7b3254dbca19b40f9012e94`. The later commit adds two papercut records and changes no score input.

The score formula remains:

```text
priority = Reach × StageWeight × Gap × SubstrateBump × EvidenceBump
```

`DEFERRED` is a status, not a score. Each deferred item keeps its score and one exact reason.

The selection override lane is empty. The oversized cadence credit probe used persisted credit `10^1000`. The kernel clamped it to `threshold_denominator - 1`. The step then emitted one reward and returned credit `0` at threshold `10`. No flashcard-review blocker, save corruption, or undo breakage enters before the scored queue.

### 11.2 Source coverage

The audit read all current queue sources. A source can supply many references but still represent one backlog family.

| Source | Audited units | Treatment |
| --- | ---: | --- |
| Design queue section 3.x and 5.x headings | 58 | Score live implementation work. Exclude owner forks under section 2. |
| Future-work Kanban headings | 53 | Retire 31 closed-only headings. Map 21 active or residual headings below. Merge the diary duplicate into rank 7. |
| Gap backlog status rows | 45 | Map each non-final row to a scored family. Keep final and rejected rows as dispositions. |
| Placeholder register rows | 179 | Keep each live placeholder in the registered-placeholder family unless it has a separate score. |
| Loop queue checklist records | 69 | Retire completed re-walks. Keep the remaining depth work. |
| Breadth tranche rows | 10 | All 10 rows are complete and stay at score 0. |
| Encounter-ranking rows | 14 | Re-measure before selection. Do not reuse stale counts. |
| Diary gate records | 2 | Keep the curation gate and the runtime gate together. |
| Papercut corpus | 1 | Treat the append-only corpus as one source, not one score per entry. |
| Named papercut branches | 3 | Record each branch disposition. |
| **Total source references** | **434** | **All references have a treatment above and a source map below.** |

The requested baseline has 771 papercut entries. At audit time, `main` had 773. This audit does not use the two later records as score inputs.

### 11.3 Current audit fixed point

The current reachability audit reports:

- 1,600 actions.
- 2,217 reachable items.
- 192 orphan inputs.
- 284 unresolved actions.
- 148 unreachable quest-stage products in `blocked_quest_stage_products`.
- 40 completable quests.
- 109 startable quests.
- 196 total quest definitions.

The quest counts come from `_close_quest_reachability` at `tools/audit_item_reachability.py:1950`. The audit does not emit them in `--json` or `--summary` output.

The current quest-stage census reports:

- 701 generated sentinel actions.
- 138 quests with at least one sentinel.
- 132 first-block rows with one sentinel.
- 100 sentinel rows with no missing `required_inventory` item.
- 95 sentinel rows with no additional item, alternative, tool, or combat blocker.

Across all 148 unresolved quest-stage rows, the census reports:

- 44 rows with missing required items.
- 75 missing required-item occurrences.
- 10 rows with missing item alternatives.
- 11 missing alternative groups.
- 2 rows with missing required tools.
- 0 rows with missing required routes.
- 1 row with an unresolved combat encounter.

These numbers replace the older encounter-matrix counts. The older counts are not score inputs.

### 11.4 Section 5 re-score

The following table re-scores every original section 5 row. A score of zero means that the audited defect is complete or its premise is false.

| Original row | Old score | New score | Exact audit fact that changed or retained the score | Disposition |
| --- | ---: | ---: | --- | --- |
| Missing quest definitions | 18 | 0 | The catalog changed from 167 missing definitions to 0. It now has 194 generated quests and 2 miniquests. | COMPLETE. Generated stage work is a different family. |
| All-pre-Evolution-of-Combat bestiary expansion | 18 | 18 | `COMBAT_ENEMY_DATA` changed from the stale card count of 130 to 201 runtime keys. The period roster is still incomplete. This supersedes the stale 130-enemy sentence in section 10. | DEFERRED — select and remeasure one atomic encounter family before implementation. |
| Direct-action undo migration | 12 | 0 | The bypass count changed from 30 to 0. All 54 `_apply_*_command` handlers call `commit_direct_action`. | COMPLETE. |
| Daily Challenge reward XP | 9 | 9 | The `100 × challenge level` fallback remains after the complete local source re-walk. | DEFERRED — no local server or cache table establishes the period payout value. |
| Quest rewards bypass the one-clue rule | 6 | 0 | Quest completion now calls `filter_clue_scroll_outputs_pure` before it grants inventory. | COMPLETE. |
| Generic rev-727 placeholder harvest | 6 | 0 | All cache, interface, item, diary, boss, and named-placeholder re-walks are complete. | COMPLETE as a generic harvest program. Live placeholders keep separate scores. |
| Chaeldar readiness | 6 | 6 | Readiness remains 25 of 34 families. Nine exact families remain absent. | DEFERRED — select one source-backed missing family as the atomic slice. |
| Evil Tree kindling art | 4 | 0 | The missing asset count changed from 1 to 0. The file and provenance record exist. | COMPLETE. |
| Dungeoneering payout curves | 3 | 3 | The live fallback remains. Local code does not establish the period curve. | DEFERRED — local code proves the fallback is live but does not establish the period payout curve. |
| Housekeeping rider | rider | rider | Three of four named records are complete. One stale GPT art queue record remains. | RETAINED as a reduced maintenance rider. It does not enter the scored top ten. |

Five original numeric scores changed: `18 → 0`, `12 → 0`, `6 → 0`, `6 → 0`, and `4 → 0`.

The reachability-check papercut does not enter the score table. It is a maintenance rider like the section 5 row 10 housekeeping rider. Its exact status is `DEFERRED — integration is in progress on goal/promote-reachability-check-2026-08-30`.

### 11.5 Other stale queue claims

The audit also corrected claims outside the original section 5 table.

| Claim | Current fact | Score |
| --- | --- | ---: |
| Quest rewards still grant non-item labels as inventory | Tests cover 47 known non-item reward occurrences across 24 quests. The current reward census has 261 occurrences, 245 distinct name-and-amount pairs, 228 names, and 0 unregistered names. | 0 |
| Four callers own Shattered Heart output eligibility | The shared hook now accepts only tradeable item keys. Two explicit runtime overrides remain and do not own eligibility. | 0 |
| Jungle Potion still needs the accepted stage fix | The repeatable herb searches and the quest-end exemption are both present. | 0 |
| The source audit accepts dead `unittest` selectors | `tools/audit_docs.py` now builds selectors and rejects dangling selectors. The audit passes. | 0 |
| The Kinship analysis packet is absent | The 534-line packet exists and defines owner decisions P1 through P8. Runtime work still needs approval. | 6 |
| The generic local placeholder harvest remains open | The full local re-walk is complete. Only source-limited individual placeholders remain. | 0 |

The complete rows above must not return to the ranked queue unless a new audit reproduces a defect.

### 11.6 Ranked atomic ledger

R10 requires the loop to select an atomic slice. A large program can stay as a family, but the loop must split it before implementation.

| Rank | Atomic slice or family gate | R | S | G | R8 | R9 | Score | Status and exact reason |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | The Lost Tribe generated stage-1 objective | 2 | 3 | 3 | 1 | 1 | 18 | READY for source harvesting. It gates 13 prerequisite descendants. No exact local stage-1 implementation source was found. |
| 2 | Gertrude's Cat Doogle-leaf acquisition | 2 | 3 | 3 | 1 | 1 | 18 | READY for source harvesting. It gates 12 prerequisite descendants. Local evidence proves use and identity, but no acquisition-route source was found. |
| 3 | Fight Arena Khazard ogre resolver stats | 2 | 3 | 3 | 1 | 1 | 18 | DEFERRED — no authentic resolver-ready stat block exists in the inspected local evidence. |
| 4 | All-pre-Evolution-of-Combat bestiary family | 2 | 3 | 2 | 1 | 1.5 | 18 | DEFERRED — select and remeasure one atomic encounter family before implementation. |
| 5 | Mogres master-certification slice | 2 | 2 | 2 | 1 | 1.5 | 12 | READY. One family raises both Mazchna and Vannaka readiness. |
| 6 | Snake hide acquisition route | 2 | 2 | 3 | 1 | 1 | 12 | READY for a sourced route. Two tanning actions consume the item, and no producer exists. |
| 7 | Achievement Diary curation and wiring gate | 2 | 2 | 2 | 1 | 1.5 | 12 | DEFERRED — owner spot-check remains pending, and the generator mapping prerequisite must be fixed before wiring. |
| 8 | Skill-mechanics residual family | 2 | 3 | 2 | 1 | 1 | 12 | READY to split. Start with `rc-method-selection`. Section 11.9 keeps exact deferrals for the other members. |
| 9 | Daily Challenge reward XP | 3 | 3 | 1 | 1 | 1 | 9 | DEFERRED — no local server or cache table establishes the period payout value. |
| 10 | Later quest-specific actions behind generated sentinels | 2 | 1 | 3 | 1 | 1.5 | 9 | DEFERRED — clear and remeasure the earlier generated stage before selecting a hidden action. |
| 11 | Fancy boots and Fighter boots period art | 2 | 3 | 1 | 1 | 1.5 | 9 | DEFERRED — owner approval for generated replacement art remains pending. |
| 12 | Herblore secondary acquisition remainder | 2 | 1 | 3 | 1 | 1 | 6 | DEFERRED — split one source-backed secondary after the complete Rune shard chain. |
| 13 | Frost dragon bone route | 2 | 1 | 3 | 1 | 1 | 6 | DEFERRED — no period source maps the identified bone to an authentic acquisition route. |
| 14 | Glacor boot component identities | 2 | 1 | 3 | 1 | 1 | 6 | DEFERRED — no inspected local source identifies the three authentic component items. |
| 15 | Chaeldar missing-family gate | 2 | 1 | 2 | 1 | 1.5 | 6 | DEFERRED — select one source-backed family from the nine missing families. |
| 16 | Kinship party simulation | 2 | 1 | 2 | 1 | 1.5 | 6 | DEFERRED — owner approval is required for P1 through P8. No current call-site count earns R8. |
| 17 | Registered source-limited placeholders | 2 | 2 | 1 | 1 | 1 | 4 | DEFERRED — the complete local re-walk found no authoritative replacement value. Score one row again when new evidence exists. |
| 18 | Explicit quest eligibility predicates | 2 | 1 | 2 | 1 | 1 | 4 | DEFERRED — build an atomic predicate census before implementation. |
| 19 | Dungeoneering payout curves | 2 | 1 | 1 | 1 | 1.5 | 3 | DEFERRED — local code proves the fallback is live but does not establish the period payout curve. |
| 20 | Later Slayer master readiness family | 1 | 1 | 2 | 1 | 1 | 2 | DEFERRED — select and remeasure one atomic missing family shared by Sumona and Duradel. |

The bestiary and skill-mechanics rows are family gates. They keep a score under R2. They cannot enter implementation until R10 yields one atomic slice.

The top ten are ranks 1 through 10 in this table. On equal scores, the smaller slice goes first under R10. Within equal-size slices, prerequisite leverage sets the order.

### 11.7 Exact candidate evidence

The generated-sentinel candidates with the largest prerequisite reach are:

- The Lost Tribe: 13 descendants.
- Underground Pass: 12 descendants.
- Recipe for Disaster: Another Cook's Quest: 12 descendants.
- Regicide: 11 descendants.

The item or tool candidates with the largest prerequisite reach are:

- Gertrude's Cat: 12 descendants.
- Recipe for Disaster: Another Cook's Quest: 12 descendants.
- Creature of Fenkenstrain: 10 descendants.

The only current unresolved combat encounter is Fight Arena stage 8, `fight_arena_khazard_ogre_63`. The two missing required tools are Holy Grail stage 5 `Excalibur` and Smoking Kills stage 1 `Catspeak amulet`.

Slayer readiness is:

- Turael and Spria: 23 of 23.
- Mazchna and Achtryn: 26 of 27.
- Vannaka: 34 of 35.
- Chaeldar: 25 of 34.
- Sumona: 20 of 37.
- Duradel and Lapalok: 15 of 35.

Mogres is the shared next family for Mazchna and Vannaka. Chaeldar still lacks Fever spiders, Fungal magi, Grifolapines, Grifolaroos, Jungle strykewyrms, Kurasks, Trolls, Vyrewatch, and Warped tortoises.

Sumona lacks 17 families. Duradel and Lapalok lack 20. Rank 20 requires a new atomic census before the loop selects one shared family.

The diary generator rotates source skill types 17, 18, and 19. The correct targets are Firemaking 11, Woodcutting 8, and Fletching 9. The current wrong map is at `tools/generate_achievement_diary_data.py:556-582`.

The harvest has 33 affected rows and 34 affected requirements. Source ID 982 has both type 18 and type 19. The diary ledger contains 25 of those 33 rows. The eight rows outside the ledger are source IDs 110, 199, 200, 246, 247, 250, 357, and 962.

The read-only Darkan authorities are `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/achievements/AchievementDef.java:216-244` and `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/model/entity/player/Skills.java:77-78`. The generator fix exists on `goal/diary-skill-rotation-2026-08-30` but is not in this audit baseline.

Two verification seams can cause false negatives:

- `data.combat_data.COMBAT_ENEMY_DATA` has 197 base keys. `core/constants.py:818` adds four bone-source enemies with `COMBAT_ENEMY_DATA.update(bone_source_enemies_as_dict())`. Count the exported runtime registry to get 201.
- `root_orphan_leverage` and `--rank-roots` do not compute quest descendants. Follow the transitive `required_quests[].quest_id` graph to reproduce the descendant counts above.

### 11.8 Deferred register

Use these exact reasons until an audit changes the underlying fact.

| Item | Exact deferral reason |
| --- | --- |
| Fight Arena Khazard ogre resolver stats | No authentic resolver-ready stat block exists in the inspected local evidence. |
| All-pre-Evolution-of-Combat bestiary family | Select and remeasure one atomic encounter family before implementation. |
| Achievement Diary curation and wiring gate | Owner spot-check remains pending, and the generator mapping prerequisite must be fixed before wiring. |
| Daily Challenge reward XP | No local server or cache table establishes the period payout value. |
| Later quest-specific actions | Clear and remeasure the earlier generated stage before selecting a hidden action. |
| Fancy boots and Fighter boots period art | Owner approval for generated replacement art remains pending. |
| Herblore secondary acquisition remainder | Split one source-backed secondary after the complete Rune shard chain. |
| Frost dragon bone route | No period source maps the identified bone to an authentic acquisition route. |
| Glacor boot component identities | No inspected local source identifies the three authentic component items. |
| Chaeldar missing-family gate | Select one source-backed family from the nine missing families. |
| Kinship party simulation | Owner approval is required for P1 through P8. |
| Registered source-limited placeholders | The complete local re-walk found no authoritative replacement value. Score one row again when new evidence exists. |
| Explicit quest eligibility predicates | Build an atomic predicate census before implementation. |
| Dungeoneering payout curves | Local code proves the fallback is live but does not establish the period payout curve. |
| Later Slayer master readiness family | Select and remeasure one atomic missing family shared by Sumona and Duradel. |

The queue uses no `blocked` status.

### 11.9 Source map and accounting

The source census has no unscored in-scope implementation item.

The 45 gap-backlog rows have 29 final or rejected dispositions and 16 non-final records. The exact non-final map is:

| Group | Exact non-final IDs | Disposition |
| --- | --- | --- |
| Hunter source residuals | `hunter-tracking-pitfall-snare`, `hunter-grenwall-herb-table` | Rank 8, score 12. DEFERRED — exact selectors, rates, or reward distributions remain unrecovered after the Darkan reconciliation. |
| Hunter Farming dependency | `hunter-habitat-jadinko` | Rank 8, score 12. DEFERRED — the Farming runtime and persistent habitat configuration do not exist. |
| Runecrafting source residuals | `rc-runespan`, `rc-abyss`, `rc-zmi-gop-wickedhood` | Rank 8, score 12. DEFERRED — period session mechanics, route rates, or exact output rolls remain unrecovered. |
| Runecrafting method selection | `rc-method-selection` | Rank 8, score 12. READY — the owner ruling is settled; select one current unlocked-method slice. |
| Firemaking source residuals | `fm-bonfires`, `fm-pyres-beacons` | Rank 8, score 12. DEFERRED — exact odds, reward rolls, or timers remain unreconciled. |
| Firemaking owner decision | `fm-barbarian-bow-lighting` | OUT OF SCOPE under section 2 until the owner decides the representation. |
| Smithing residuals | `smith-artisan-burial`, `smith-blastfurnace-goldsmith` | Rank 8, score 12. DEFERRED — exact pipe timing and the remaining Darkan mechanics are unresolved. |
| Herblore residual | `herb-overload-sanfew` | Rank 8, score 12. DEFERRED — Sanfew stages, poison application, and combat-potion runtime work remain. |
| Woodcutting residual | `wc-arctic-euc-cursed` | Rank 8, score 12. DEFERRED — Cursed Magic requires the absent Spirit of Summer quest substrate. |
| Mining residual | `mine-lrc-stars` | Rank 8, score 12. DEFERRED — the Living mineral yield conflict of 5–20 versus 5–24 remains unresolved. |
| Fishing residual | `fish-trawler-flingers` | Rank 8, score 12. DEFERRED — the Daemonheim session and temporary inventory do not exist. |

The 53 future-work headings have 31 complete-only headings, 21 active or residual headings, and one merged diary duplicate. The active or residual map is:

| Active or residual Kanban card | Disposition |
| --- | --- |
| Existing-skill parity ledger | Ranks 5, 8, 15, 19, and 20. |
| Slayer | Ranks 5, 15, and 20. |
| Summoning | Rank 8. |
| Dungeoneering depth | Ranks 8, 17, and 19. |
| Quest-by-quest fidelity across the complete definition catalog | Ranks 1, 2, 3, 10, and 18. |
| Complete pre-Evolution-of-Combat bestiary | Rank 4. |
| Large special methods and activities | Ranks 8 and 16. |
| Missing skill server behavior | Rank 8. |
| Fancy and fighter boots have no art | Rank 11. |
| Whole-save deep-copy convention | Score 0. The sweep classified the 44 retained sites as deliberate. |
| Shared modular list search and filters | Score 0 for the shared substrate. The Slayer filter residual is DEFERRED — it waits on the Slayer runtime delivered by ranks 5, 15, and 20. |
| In-product help and mechanics reference | Score 0. The card records implementation and review as closed. |
| Activities, minigames, D&Ds, and reward shops | Ranks 8 and 16. |
| Bosses and instanced Combat | Ranks 3 and 4. |
| Acquisition and item/equipment completeness | Ranks 2, 6, 12, 13, and 14. |
| Achievement diaries, clues, collections, and one-time content | Ranks 7, 8, and 10. |
| Random events and timed world content | OUT OF SCOPE under section 2 while owner design decisions remain open. |
| Road to Restoration comparator | OUT OF SCOPE under section 2 while owner adopt, adapt, or reject decisions remain open. |
| Grand Exchange | Score 0. The card records full closure. |
| Level 1-99 time and economy balance | Ranks 17 and 19 for source-limited values. |
| Release readiness | OUT OF SCOPE under section 2 as owner playtest and external-release work. |

The remaining source families map as follows:

- All 58 design-queue headings map to a score-0 correction, ranks 1 through 20, or an owner decision under section 2. Audit and incident records do not create duplicate work.
- The 179 placeholder rows map to rank 17 unless this ledger names a separate row.
- The 69 loop records have 66 checked records and 3 open records. Two open records describe the same rank-13 Frost dragon item. The last open record is this matrix update.
- All 10 breadth-tranche rows are complete and stay at score 0.
- Thirteen encounter rows supply candidate evidence for the ranked ledger. The diary encounter row merges into rank 7.
- Both diary gate records merge into rank 7.
- The papercut corpus remains one append-only source unit. It does not become one score per entry.
- Two named papercut branches are complete. The reachability-check branch is a maintenance rider and stays outside the scored top ten.
- Owner decisions and owner playtest passes stay outside the matrix under section 2.
- Rejected claims keep their source disposition. They do not receive a live implementation score.
- Complete claims stay at score 0. They do not enter the top ten.

The Achievement Diary row keeps an implementation score because R2 requires one. Its owner gate changes only the status. The Kinship row uses the same rule.

### 11.10 Maintenance instructions

After each merged batch, do these steps in order:

1. Check the R3 override lane first.
2. Run the current audits and record their exact counts.
3. Re-score every live row with the formula in section 3.
4. Give R8 only when one atomic change affects at least five families or call sites.
5. Give R9 only when the evidence for that repair already exists on local disk.
6. Split a family into one atomic slice before implementation.
7. Record one exact reason for each `DEFERRED` row.
8. Keep complete work at score 0.
9. Append a new dated score audit. Do not edit this section or sections 1 through 10.
10. Run `/opt/homebrew/bin/python3 tools/audit_docs.py` before promotion.

The ledger outranks old queue prose when the two sources disagree. A later audit can change a score only when it records the exact fact that changed.

## 12. Selection corrections found while working section 11 — 2026-08-30

These corrections come from implementing section 11's ranked rows. They change how a
later loop must read that table. Sections 1 through 11 stay unchanged.

### 12.1 Sentinel scores understate the work, because the audit truncates at the first blocker

`tools/audit_item_reachability.py` reports only each quest's EARLIEST blocked stage.
A later stage can hold its own generated sentinel that the report never shows.

Rank 1 scored 18 because The Lost Tribe "gates 13 prerequisite descendants". The
stage-1 sentinel is now replaced with the source-backed requirement and is live in
zero places, yet the quest stays blocked: stage 2 holds its own sentinel. Completable
quests did not move. Blocked stage rows fell from 148 to 146.

Rule for the next loop: never treat a sentinel row's descendant count as the closure
value of one slice. Enumerate every blocked stage of that quest first, then score the
whole chain, or score only the single stage the slice can actually clear.

### 12.2 Rank 8's premise is false; do not start with `rc-method-selection`

Rank 8 says "READY to split. Start with `rc-method-selection`." That row is settled
design, but its selectable set does not exist. No Abyss, Ourania/ZMI, or Runespan
route ships, so a method selector would offer one ordinary route. Building it now
would add an abstraction over nothing.

`rc-method-selection` becomes real only after at least one further Runecrafting method
lands. Those methods are `rc-abyss`, `rc-zmi-gop-wickedhood` (ZMI residual), and
`rc-runespan`, all recorded source-blocked in `memory-bank/gap-backlog.json`.

### 12.3 New lead: `Orange goblin mail` gates a quest chain

Restoring The Lost Tribe's true prerequisites exposed a dependency that first-blocker
truncation had hidden. Goblin Diplomacy is blocked at stage 1 on the missing item
`Orange goblin mail`. Goblin Diplomacy gates The Lost Tribe, which gates descendants.

This is why startable quests moved from 114 to 113. The old count was inflated by
generated prerequisite data that named the wrong gates; the new count is the honest
one. `Orange goblin mail` is an acquisition candidate with real chain leverage and did
not appear in section 11 because the audit never reported it.

### 12.4 Reviewer seating during this pass

Kimi K3 returned HTTP 403 `You've reached your weekly (7-day) usage limit` on every
attempt. Fable stays barred under section 9 ruling O1 and design-queue entry 4.18; the
owner has not been asked to lift it for the current goal. Opus covered the diary slice.
GLM 5.3 Flash covered the Doogle leaves and Lost Tribe slices and found one real
order-coupled assertion. From `2026-08-30 14:03` the Claude plan is also exhausted, so
no Opus seat remains until it resets.

### 12.5 Rank 5 is not READY; Mogres is dependency-blocked and the two threads disagree

Section 11.6 rank 5 says the Mogres master-certification slice is READY. It is not.
`tools/audit_slayer_readiness.py` reports `mogres:combat_target` as the single
remaining blocker for two masters at once:

```
mazchna_achtryn: blocked, hidden, 26/27 families ready
vannaka: blocked, hidden, 34/35 families ready
```

Adding that combat target would certify both masters in the audit while leaving the
family permanently unplayable. `data/slayer_data.py:266-270` declares the family with
`required_quest_id="skippy_and_the_mogres"`, and `logic/slayer_logic.py:79` gates the
family on that quest being complete. The id appears nowhere in `data/quest_data.py`.
`memory-bank/future-work-kanban.md:1065` already records the correct disposition: keep
the Mogre work marked `DEPENDENCY: QUEST` and do not advance readiness with a
permanently locked partial target.

A doorbell to the 2012scape design thread on 2026-08-30 returned three facts. First,
`skippy_and_the_mogres` is not planned, not in progress, and not inventoried in any of
their twelve ledgers; they call it an unrecorded coverage gap and are surfacing it to
the owner. Second, they hold no pinned evidence for it, so an AnkiScape harvest would
duplicate nothing. Third, they cannot rule on whether AnkiScape may self-source the
miniquest, because their R25 bars that seat from goal-scoped design decisions.

This is a recorded contract conflict. Their `quest_implementation_lane` is
`ankiscape_external`, which reads as quest work belonging to this thread, while this
thread's own kanban line 1065 forbids it. Only the owner can resolve it. Rank 5 is
DEFERRED with that exact reason until he does.

### 12.6 The real remaining debt is 700 generated stage sentinels across 138 quests

A direct census of `QUESTS_BY_ID` stage requirements, counting stages whose
`required_actions` match `Complete <Quest> stage <N> objective`, gives 138 quests
holding 700 sentinel stages. The per-quest distribution is 2 quests with one sentinel
stage, 1 with two, 26 with three, 20 with four, 40 with five, 19 with six, 22 with
seven, 2 with eight, and 6 with nine.

Section 12.1 said never to score a sentinel row by its descendant count. This census
is the constructive form of that rule. Score a quest by its full sentinel-stage count,
because the audit shows only the earliest one:

| Quest | Sentinel stages | Of total stages |
| --- | ---: | ---: |
| `big_chompy_bird_hunting` | 3 | 4 |
| `the_lost_tribe` | 4 | 6 |
| `death_to_the_dorgeshuun` | 5 | 7 |
| `dream_mentor` | 5 | 6 |
| `zogre_flesh_eaters` | 6 | 7 |

### 12.7 The 39 root orphans are not an implementation queue

The top five root orphans by leverage do not need new acquisition data. Each already
has a modelled producer, and each is unreachable only because a quest in front of it
holds a sentinel. Measured on `2df4709c`:

| Root orphan | Items it unlocks | Modelled producer | Real blocker |
| --- | ---: | --- | --- |
| `Ogre coffin key` | 9 | Zogre bone source, `data/bone_sources_data.py:71-75` | `zogre_flesh_eaters` stage 1 sentinel, itself behind `big_chompy_bird_hunting` |
| `Wergali seed` | 8 | Molanisk drop, `data/combat_data.py:3201-3225`; Vinesweeper reward | `death_to_the_dorgeshuun` stage 1 sentinel |
| `Raw chompy` | 3 | Chompy bird drop in the read-only Darkan tree | `big_chompy_bird_hunting` stage 1 sentinel |
| `Shaikahan bones` | 2 | Shaikahan bone source, `data/bone_sources_data.py:80-83` | `tai_bwo_wannai_trio` stage 2, missing `Raw karambwan` |
| `Astral rune shards` | 2 | Astral rune on anvil, Darkan `DreamMentor.kt:402-411` | `dream_mentor` stage 1 sentinel |

One hypothesis was tested and rejected. The reachability audit imports
`ankiscape.data.combat_data` rather than the runtime registry, which looked like it
would hide the four bone-source enemies. It does not: `core/constants.py` mutates that
dict in place, `constants.COMBAT_ENEMY_DATA is combat_data.COMBAT_ENEMY_DATA` is
`True`, and both expose 202 keys including `zogre`, `jogre`, `shaikahan` and
`frost_dragon`. The audit is correct. The items really are unreachable.

The consequence for selection is that acquisition work and quest-sentinel work are the
same queue. Clearing sentinels is the higher-leverage half of it.

### 12.8 Orchestration corrections from this pass

A dispatched reviewer with a read-only brief used stash-based comparisons inside the
worktree that its author was concurrently running both test lanes in. Both trees
finished clean and the final lanes ran afterwards, so no result was lost, but the
runs during that window are contaminated. A worktree has exactly one writer. Give a
reviewer the canonical checkout and two commit shas, never the author's worktree.

A second reviewer ran `tools/audit_asset_cutoff.py` against a read-only mandate, which
performs network lookups and rewrote an `updated_at` timestamp in
`memory-bank/source-audits/post-cutoff-asset-revisions-2026-08-21.json`. It restored
the file, and `git diff` confirmed byte identity afterwards. Name that tool as
forbidden in every read-only brief.

### 12.9 Decisions parked for the owner

1. Whether AnkiScape may self-source the `skippy_and_the_mogres` miniquest, given the
   conflict recorded in section 12.5. Unblocking it certifies two Slayer masters.
2. Whether ruling O1 and design-queue entry 4.18, which bar the Fable seat, survive
   into the current goal. The `QA: FABLE BLOCKED` label at
   `memory-bank/future-work-kanban.md:1758` stays accurate while they stand.
3. The Achievement Diary curation ledger spot-check, gate 2 of section 5.21. Gate 1
   passed. Until gate 2 clears, 0 of 34 diary tiers are claimable.

### 12.10 Two corrections to section 12.7, and the recorded quest order to follow

Section 12.7 lists the `dream_mentor` sentinel as the blocker for `Astral rune shards`.
That is true but incomplete. The merged and approved backlog item at
`memory-bank/gap-backlog.json:697-724` says verbatim "do not add acquisition, XP,
Combat, or Prayer behavior" and repeats that the shipped work "adds no acquisition".
The item is therefore scope-excluded as well as sentinel-blocked. Do not select it.

`Ogre coffin key` carries a second, separate restriction. Its selector weights are a
registered source-blocked placeholder, and
`memory-bank/handoffs/orchestration-handoff-2026-08-19.md:117-121` states that
"Placeholder retirement is NOT open work". Clearing the `zogre_flesh_eaters` sentinels
makes the key obtainable; it does not license touching those weights.

The queue order is already recorded and this thread must follow it rather than
re-derive one. `memory-bank/future-work-kanban.md:1104-1110` and
`memory-bank/progress.md:5090-5092` both give the same sequence: repair Jungle Potion's
generated stage buttons, then Big Chompy Bird Hunting, Zogre Flesh Eaters, Rum Deal and
Cabin Fever, and only then the Mos Le'Harmless, Cave horror, Black mask and
Slayer-helmet runtime.

Jungle Potion is done. A direct census of its stage requirements on `fed8f00a` finds
zero sentinel stages of six. The remaining members, with the sentinel-stage counts that
section 12.6 requires for honest scoring:

| Quest | Sentinel stages | Of total | What clearing it reaches |
| --- | ---: | ---: | --- |
| `big_chompy_bird_hunting` | 3 | 4 | `Raw chompy`, 3 items |
| `zogre_flesh_eaters` | 6 | 7 | `Ogre coffin key`, 9 items |
| `rum_deal` | 4 | 5 | Slayer-helmet route |
| `cabin_fever` | 3 | 5 | Slayer-helmet route |

The Lost Tribe is not in that sequence, and it is being worked first because its four
sentinel stages gate 13 quest descendants, which is more leverage than any row above.
After it lands, take Big Chompy Bird Hunting and follow the recorded order.

### 12.11 "Gates N descendants" is not a leverage number, and this pass proved it twice

Section 11.6 ranked The Lost Tribe first because it "gates 13 prerequisite
descendants". Section 12.1 already warned that a sentinel row's descendant count is
not the closure value of one slice. This pass produced the measurement that settles it.

Clearing all four remaining Lost Tribe sentinels made the quest itself completable and
moved nothing else. Measured across the change:

| Measure | Before | After |
| --- | ---: | ---: |
| `completable_quests` | 44 | 45 |
| `reachable_item_count` | 2243 | 2244 |
| `seed_item_count` | 1177 | 1179 |
| Blocked stage rows | 145 | 144 |
| `the_lost_tribe` blocked | yes | no |

The single added completable quest is The Lost Tribe. All 13 descendants stay blocked,
because each holds its own sentinel stages. The 13 is a dependency-graph fact about
what sits behind the quest, not an unlock any one slice delivers.

The scoring rule that follows is narrow and mechanical. Score a quest slice by its own
sentinel-stage count and by the items its own stages produce. Treat a descendant count
as reach only when every intervening quest is already sentinel-free. Under that rule
the section 12.6 census table is the queue, and the descendant column in section 11.7
is background rather than score.

### 12.12 Follow-on leads from the Lost Tribe pass

These quest-local items are named by the Darkan source and have no faithful AnkiScape
acquisition contract. None of them blocks the quest, because the stages that use them
now carry auto actions instead of item requirements. They are leads in the same sense
`Orange goblin mail` was a lead, and they are recorded here so a later pass does not
rediscover them:

- Brooch, item `5008`
- Goblin symbol book, item `5009`
- Sigmund's key, item `5010`
- Silverware, item `5011`
- Peace treaty, item `5012`
- The seven H.A.M. outfit pieces, items `4298`, `4300`, `4302`, `4304`, `4306`,
  `4308` and `4310`

One reachability side effect is worth keeping. Lumbridge Swamp Caves became reachable,
and The Lost Tribe is now the preferred source for `Ring of life`.

## 13. Six quests are permanently unstartable, and the audit does not know it — 2026-08-31

### 13.1 The defect

`core/skill_registry.py` treats `combat` as a skill CATEGORY, not a `SkillDefinition`.
The individual combat skills are registered but carry `trainable=False`, because the
player trains them through Combat rather than through a skill hub.

A quest that requires a `combat` level therefore hits
`logic_pure/logic_pure_quest.py:146`:

```python
if skill is None or not skill.trainable:
    return f"{label} {level_required} (not implemented)"
```

That blocker is permanent. No player at any level can clear it, so `start_quest_pure`
refuses forever. Six quests carry such a requirement:

| Quest | Required combat level |
| --- | ---: |
| `dream_mentor` | 85 |
| `grim_tales` | 100 |
| `legends_quest` | 75 |
| `smoking_kills` | 85 |
| `underground_pass` | 79 |
| `zogre_flesh_eaters` | 89 |

AnkiScape already computes the value the requirement wants.
`logic_pure/logic_pure_combat_engine.py:2864` defines `player_combat_level_pure`, which
derives the combat level from Attack, Strength, Defence, Constitution, Prayer, Ranged,
Magic and Summoning. The quest blocker path simply has no case that reaches it.

### 13.2 The instrument does not see the defect

`tools/audit_item_reachability.py:943-948` builds the `startable` set from
`required_quests` and `required_quest_points` only:

```python
startable = {
    quest_id
    for quest_id, quest in quest_data.items()
    if _required_quest_ids(quest) <= completed
    and int(quest.get("required_quest_points", 0) or 0) <= quest_points
}
```

It never consults `required_skills`. So the audit reports these six quests as startable
and credits every route behind them, while the runtime denies all of them.

### 13.3 What it cost this pass, and a correction on the record

The Big Chompy slice measured `reachable_item_count` rising by 13. Only four of those
are real: `Ogre bow`, `Raw chompy`, `Raw wild pie` and `Wild pie`. The other nine are
the Zogre bone family, credited because the audit believes `zogre_flesh_eaters` becomes
startable once Big Chompy completes.

The orchestrator verified `data/bone_sources_data.py:143-145`, saw
`row["quest_gate_state"] = "started"`, and concluded the cascade was genuine. That was
one level too shallow: the gate is correct, and the quest behind it can never be
started. An independent reviewer found the real blocker. Of the two root orphans this
pass cleared, `Raw chompy` is real and `Ogre coffin key` is not.

Section 12.7 named `zogre_flesh_eaters` stage sentinels as the blocker for
`Ogre coffin key`. That is now known to be the second blocker, not the first. The first
is the unstartable combat requirement recorded here.

### 13.4 The slice this implies, and why it ranks above the remaining quest queue

Fix the requirement resolution so a `combat` requirement compares against
`player_combat_level_pure`, and fix the audit's `startable` filter so it accounts for
skill requirements. That is one coherent slice in shared substrate. It converts six
quests from permanently unstartable to genuinely gated, and it stops the reachability
report over-crediting every route behind them.

It outranks the remaining rows of the section 12.10 queue because those rows are quest
data depth, while this is a player-visible defect in shared substrate and a correction
to a measuring instrument. The goal sentence puts shared tooling and player-visible
defects ahead of recorded data-depth debt.

Take it before Zogre Flesh Eaters. Clearing that quest's six sentinels while it stays
unstartable would deliver nothing.

### 13.5 The same registry gap strands 10,000 experience points on a second path

The combat-requirement fix in section 13.4 covers quest ENTRY. A reviewer found that the
identical registry gap also destroys a quest REWARD, on a different code path.

`generated/quest_catalog_generated.py:19446` gives The Fremennik Isles an experience
reward row of `{'skill_id': 'combat', 'amount': 10000.0}`.
`_apply_quest_xp_rewards` at `logic_pure/logic_pure_quest.py:1596-1607` resolves
`get_skill("combat")` to `None`, falls back to the experience key `combat_exp`, finds it
is not a trainable experience key, and parks the amount in
`pending_skill_exp_rewards`.

That parking lot exists so an award survives until a planned skill is implemented, and
`core/storage_pure.py:1041-1097` preserves unrecognised keys indefinitely. But `combat`
is a category and will never gain a `SkillDefinition`, so the award is stranded forever.
Measured on a fresh player completing the quest: `pending: {'combat_exp': 10000.0}`,
`woodcutting_exp` correctly `+10000`, `attack_exp` `+0`.

An independent census of every experience-reward row across all live quests found
exactly one such row, so this is a single-row defect:

```
xp_reward rows naming an unresolvable or untrainable skill: 1
  ('the_fremennik_isles', 'combat', 10000.0)
```

### 13.6 Why 13.5 is not simply the next slice

The mechanical repair is small. Deciding where 10,000 combat experience points LAND is
not, and it splits into a sourcing question and a possible interface question.

Source the period award first. If the period record awards the experience to one named
combat skill, the fix is a data correction and this thread can take it outright. If the
period record lets the player choose the skill, then AnkiScape needs a chooser, and a
new chooser is an interface change. The project rule is that an existing interface does
not change without the owner's explicit approval, and that a new interface needs a
frontend-taste review before promotion.

Recommended order: harvest the period source as its own small step, then either
implement the data correction directly or bring the owner one question with the two
options and a lean. Do not guess a skill split; a silently wrong destination for 10,000
experience points is worse than the current stranding, because stranding is at least
recoverable from the pending record.

### 13.7 The class-elimination pin this pass adds

Both halves of this defect were invisible for as long as they existed, because
`"Combat 89 (not implemented)"` reads as a deliberate statement rather than a bug, and
neither the runtime nor the audit complains. Another prose rule would not have caught
it.

The combat-gate slice therefore carries a data pin: every `skill_id` in any
`required_skills` row of `QUEST_DATA`, including stage-level rows, must either resolve
to a trainable `SkillDefinition` or be exactly `"combat"`. It fails loudly on a seventh
combat quest with a typo, on a new pseudo-skill id, and on the capitalised spelling
`"Combat"` that would otherwise skip the new branch. It also makes the reachability
audit's idealised-player assumption explicit rather than accidental.

A matching pin over `xp_rewards` rows belongs with the 13.5 fix, not before it, because
the one offending row must land somewhere first.

### 13.8 Reviewer seating from 2026-08-31 07:35, and two orchestration corrections

The Anthropic plan reached its day limit at `claude 39/39 OVER` with the next block
`+12h24m`. Kimi remains over with the next block `+14h35m`. Fable stays barred under
section 9 ruling O1 and design-queue entry 4.18. The GPT plan reset to `codex 11/80`.

Every slice this pass was authored by Sol, so the required cross-lineage reviewer must
not be a GPT model. Until the Anthropic block returns, the only available cross-lineage
seat is GLM 5.3 Flash, which draws on no plan but is recorded as never a sole reviewer.
Any slice needing code review should therefore wait for the Anthropic reset, or be
paired with GLM plus a deep orchestrator verification and that limitation recorded on
the slice.

Work that produces no code needs no such seat. That is why the next dispatched unit is
the section 13.5 source harvest rather than an implementation slice.

Two orchestration mistakes from this pass, both the orchestrator's:

1. The orchestrator rebased `goal/combat-quest-gate-2026-08-31` onto a newer main while
   its author was still running. The author correctly restored the base its brief named,
   and the promotion gate failed with `Gate failed: HEAD moved from df8765b8dd3ed18e4667ce2ecff4a47b7e662d79 to f67d6d78b99d4d7bf0b9ab9fd5c6936267898e1c`.
   The gate did its job. The rule that was broken is the ordinary one: a branch has
   exactly one writer, and the author holds it until it reports. Rebase after the final
   report, never during.

2. Stopping a running promotion gate leaves its marker behind. The next run recovered by
   itself with `Stale promotion gate marker: it recorded gate PID 51985 ... Removing .git/ankiscape-promotion-gates/b9f88f4293584cfc961085e014cfac96.json`,
   so nothing was lost, but a stopped gate should be expected to leave that trace.

## 14. The reachability audit models one point-reward minigame and misses the rest — 2026-08-31

### 14.1 The gap, and how large it actually is

`tools/audit_item_reachability.py` models Fist of Guthix as a point economy. It creates a
synthetic match node that produces the currency and one buy node per reward:

```
1530:    fog_match_key = "Activity:fist_of_guthix:match"
1541:    for reward_id, reward in fist_of_guthix_data.FIST_OF_GUTHIX_REWARDS.items():
1548:        buy_key = f"Activity:fist_of_guthix:buy:{reward_id}"
```

No other point-reward minigame is modelled. A reference count against the audit source
gives zero for `vinesweeper`, `stealing_creation`, `pest_control`, `barbarian_assault`,
`castle_wars`, `soul_wars`, `duel_arena`, `mobilising_armies`, `conquest` and
`trouble_brewing`, while `fist_of_guthix` scores 8.

This failure runs the OPPOSITE way to the one in section 13. There the audit
over-credited routes the player could not run. Here it under-credits rewards the player
can buy, which sends acquisition work at items that are already obtainable. That is what
the section 12.7 census was half-seeing.

The gap is real but far smaller than the reference count suggests. Measured on
`ba2ee961` against the live report's 179 orphan inputs and 37 root orphans, by testing
which orphaned item names each data file actually mentions:

| Minigame data file | Orphan inputs named | Root orphans named |
| --- | ---: | ---: |
| `vinesweeper` | 5 | 5 |
| `trouble_brewing` | 1 | 0 |
| the other eight | 0 | 0 |

The union across all ten files is six orphan inputs. Vinesweeper carries essentially the
whole effect, and its five root orphans are `Wergali seed` and the four Compost potion
doses. `Wergali seed` is currently the single highest-leverage root orphan at 8
transitive items and 9 unblocked actions.

### 14.2 The slice this implies

Model Vinesweeper's point economy the way Fist of Guthix is already modelled: one
synthetic match node producing points, one buy node per reward in `VINESWEEPER_REWARDS`
at `data/vinesweeper_data.py:39-55`, priced by each row's `point_price`. The activity
carries `"requirements": {}` at `:123-131` and no quest gate, so nothing else gates it.

Two things the implementing pass must establish rather than assume. First, whether the
audit can express point EARNING at all for this activity, because a buy node is useless
if no node produces the currency; follow whatever the Fist of Guthix match node does.
Second, whether each seed the table sells is genuinely obtainable in play, so that this
fix does not repeat section 13 in the opposite direction by crediting a shop the player
cannot reach.

Expect the orphan and root-orphan counts to fall and every pinned baseline to move.
Re-measure them; do not carry any number forward from this section.

Trouble Brewing names one orphan input and no root orphan, so it is a separate, much
smaller follow-on rather than part of this slice. The remaining eight minigames name no
orphaned item at all, so modelling them would change no current number and is not
work this queue should schedule.

### 14.3 Review coverage on the Fremennik slice, and the rule for the Vinesweeper one

The Fremennik lamp slice `93197a3d` landed with ONE agent reviewer, GLM 5.3 Flash, rather
than the usual two. The Anthropic and Kimi plans were both past their day limit. The
project's routing rule records GLM as never a sole reviewer, so this is a recorded
deviation, not a precedent.

Three things made it acceptable for that slice specifically. It changed data only, with
no runtime, no interface and no instrument touched. It reused a contract that already
had a worked precedent in the same table, `CARNILLEAN_RISING_ID`, also at `quantity=2`.
And the orchestrator independently probed the two claims that mattered rather than
reading the report:

```
claims generated: 2
   the_fremennik_isles_xp_lamp_1 | type xp_lamp | amount 10000 | options ('attack', 'strength', 'defense', 'constitution') | min 1
   the_fremennik_isles_xp_lamp_2 | type xp_lamp | amount 10000 | options ('attack', 'strength', 'defense', 'constitution') | min 1
```

and confirmed the defect closed, `pending after: {}` against the pre-fix
`pending: {'combat_exp': 10000.0}`, with `construction_exp 5000.0`, `crafting_exp
5000.0` and `woodcutting_exp 10000.0` all paid. The reviewer additionally verified by
AST extraction that the reformatted 25-element Carnillean option tuple is
element-for-element identical to the original.

The Vinesweeper slice in section 14.2 does NOT get the same treatment. It changes
`tools/audit_item_reachability.py`, which every pinned baseline and the whole priority
queue derive from. A wrong instrument change corrupts every later decision silently, and
this is exactly where a second independent reviewer earns its cost.

Rule for that slice: author and gate it now, then hold it unmerged until a second
cross-lineage reviewer is available. It is not an accepted slice until then, so holding
it does not violate the completion condition. The Anthropic block returns at
approximately `+11h20m` from `2026-08-31 08:39`.

One structural friction worth the owner's attention rather than a fix from this seat.
`data/quest_data.py` stands at 12,686 lines against the `slop_gate.py` cap of 1,000, so
it is permanently over. Every quest data change must therefore fund itself by
compressing unrelated code elsewhere in the file. Three consecutive slices did exactly
that, and each time the compression showed up as diff noise on code the change did not
otherwise touch. The structural answer is to split the file; that is a decision for the
owner, not something this seat should do unilaterally.

## 15. Corrections from the fresh queue audit — 2026-08-31

A read-only audit re-derived every open entry from the live tree rather than from this
file. It found four of this ledger's own figures stale. The code wins; the figures below
replace the earlier ones.

### 15.1 Section 12.9 decision 2 was never open

Section 12.9 listed "whether ruling O1 and design-queue entry 4.18 survive into the
current goal" as a decision waiting on the owner. It is not waiting. The owner ruled it
directly to this seat on 2026-08-23, and the ruling is recorded verbatim at
`memory-bank/design-thread-queue.md:1567-1584`:

> "Do not ever use fable again during this goal."

The same entry already prescribes what to do when no other reviewer seat is free:

> If none is available, record the slice as quota-blocked rather than seating Fable or
> accepting a same-lineage review.

So the Vinesweeper hold in section 14.3 is not an improvised judgement; it is the
owner's own instruction applied. Two owner decisions remain genuinely open, not three:
the Mogres self-sourcing waiver in section 12.5, and the Achievement Diary spot-check,
gate 2 of section 5.21.

### 15.2 Three counts in this ledger are stale

| Figure | This ledger said | Live measurement on `dc358d2c` |
| --- | ---: | ---: |
| Generated stage sentinels | 700 | 693 |
| Quests holding at least one sentinel | 138 | 136 |
| Registered placeholder rows | 179 | 181 |

The sentinel drop is this pass's own work landing: `the_lost_tribe` and
`big_chompy_bird_hunting` both now measure zero. Use 693 and 136 for scoring. The ten
heaviest quests are `desert_treasure`, `do_no_evil`, `garden_of_tranquillity`,
`mournings_end_part_ii`, `ritual_of_the_mahjarrat` and `the_darkness_of_hallowvale` at
nine each, `monkey_madness` and `rat_catchers` at eight, and `a_clockwork_syringe` and
`a_tail_of_two_cats` at seven.

### 15.3 Two ranked rows are complete, and their prose is stale

Rank 11, Fancy boots and Fighter boots period art, is shipped; the registrations are at
`core/constants.py:2272-2285` and `:2817-2846`, so the owner-approval sentence beside it
no longer applies. The `mine-lrc-stars` leaf is shipped as the 5 to 24 Living-mineral
route, so the former 5 to 20 conflict is closed.

### 15.4 The housekeeping rider was half stale, not wholly stale

The audit reported the blocked-family note on the period-art provenance sweep row of
`memory-bank/gpt-deferred-queue.md` as stale in full. It is stale in half. Checking the
provenance file directly:

- `runecraftingitems/wicked_hood.png` is pinned to `2011-10-17T18:06:33Z`, before the
  cutoff, so Wicked hood is genuinely cleared.
- `woodcuttingitems/evil_tree_kindling.png` is pinned to `2020-11-24T10:56:22Z`, after
  the cutoff, so Evil Tree still blocks that sweep.

The row is narrowed rather than deleted. Deleting it would have destroyed a true record,
which is why a reported stale entry gets checked against the data before it is removed.

### 15.5 Where the queue stands

Of 41 classified entries, exactly two are unblocked and workable: rank 18's read-only
predicate census, measured at 146 predicate rows carrying 488 skill requirements across
145 quests, and the housekeeping row corrected in 15.4. Sixteen are source-blocked, six
dependency-blocked, five owner-blocked, four quota-blocked, three deferred data depth,
and five complete.

One accepted slice is unmerged: `goal/vinesweeper-audit-2026-08-31`, commit `e5dd136a`,
gated green on all eight checks with `remote_lanes: true`, held for the second reviewer
under section 4.18's instruction. Its measured leverage is `Wergali seed: +8 items;
+9 actions`.

## 16. The rank 18 predicate census, and the two systemic blockers it measured — 2026-08-31

Rank 18 asked for an atomic predicate census before any behavioural work. It is done.
It is also the most useful artefact of this pass, because it replaces the queue's
item-by-item guesswork with two measured systemic numbers.

### 16.1 What the catalog contains

196 quests and 1,130 stage-requirement rows. The predicate inventory, measured live:

| Scope | Predicate | Rows | Atomic entries |
| --- | --- | ---: | ---: |
| Quest | `required_quests` | 113 | 465 |
| Quest | `required_skills` | 144 | 485 |
| Quest | `required_quest_points` | 6 | 6 |
| Stage | `required_inventory` | 229 | 612 |
| Stage | `consumed_inventory` | 137 | 199 |
| Stage | `required_inventory_options` | 59 | 245 |
| Stage | `required_tools` | 154 | 211 |
| Stage | `required_actions` | 693 | 704 |
| Stage | `required_routes` | 28 | 28 |
| Stage | `combat_encounters` | 143 | 293 |

### 16.2 What is clean

No skill id fails to resolve. No level exceeds its ceiling, measured as 99 for every
trainable skill except Dungeoneering at 120, and 138 for derived combat. No prerequisite
quest id is unknown, and no prerequisite cycle exists. All 196 quests are reachable in
the prerequisite closure. Quest points obtainable total 333, and the largest gate is
`while_guthix_sleeps` at 270. All 28 route gates have a timely choice.

Two apparent problems were checked and are not problems. Thirteen quests repeat a lower
skill level than a prerequisite already demands, which is redundant rather than
contradictory. Thirteen stages both require and consume the same item, which the code
handles correctly by checking possession at `logic_pure/logic_pure_quest.py:770-777`
before consuming at `:1327-1345`.

### 16.3 Blocker one: 704 action predicates that nothing can emit

Every `required_actions` entry is impassable, not just the generated ones. The
structural proof is that `_mark_quest_stage_actions` at
`logic_pure/logic_pure_quest.py:1334` is the only writer of `quest_stage_actions`, and
it emits a stage's `auto_actions` only after that stage already has no blockers. A
catalog-wide ordered comparison found zero cases where a required action matches an
earlier `auto_actions` value in the same quest.

693 are the generated sentinels. The other **11 are hand-written strings**, which this
ledger has never recorded and which no earlier pass noticed:

| Quest | Stage | Required action |
| --- | ---: | --- |
| `mournings_end_part_i` | 3 | Have Oronwen repair the mourner trousers |
| `mournings_end_part_i` | 5 | Use the rotten apple to sabotage the mourner food stores |
| `spirits_of_the_elid` | 2 | Cast Telegrab for the water channel puzzle |
| `enakhras_lament` | 5 | Cast Crumble Undead during the boneguard fight |
| `in_aid_of_the_myreque` | 6 | Enchant sapphire for the Myreque preparations |
| `the_eyes_of_glouphrie` | 3 | Collect a bucket of sap from an evergreen tree |
| `cold_war` | 2 | Build the clockwork penguin on a crafting table 3 |
| `the_fremennik_isles` | 5 | Cure and stitch yak-hide armour |
| `the_fremennik_isles` | 5 | Make a Fremennik round shield |
| `legacy_of_seergaze` | 5 | Cast Enchant Level 2 Jewellery for the emerald preparations |
| `do_no_evil` | 3 | Recover an m'amulet mould before making the monkeyspeak amulet |

### 16.4 Blocker two: the quest combat gate defaults to the enemy's own level

`logic_pure/logic_pure_quest.py:690-696` reads:

```python
minimum_player_combat = _positive_int(
    _quest_combat_configs(encounter).get("minimum_player_combat", encounter_level),
    encounter_level,
)
...
if minimum_player_combat > 0 and player_level < minimum_player_combat:
    return False, "combat_underpowered"
```

When an encounter carries no explicit `minimum_player_combat`, the requirement falls
back to the ENEMY's combat level. So killing the level 699 Nomad requires the player to
be combat 699, against an attainable maximum of 138. A live count finds **66 encounters
above level 138**, and the census measured 64 of them as permanently `combat_underpowered`,
plus 91 permanently `combat_missing_stats`, giving 131 impossible encounter predicates
across 60 quests.

**This is a known defect with a settled convention, not an open design question.** A
handoff of 2026-08-12 already stated it plainly at
`memory-bank/handoffs/claude-handoff-2026-08-12-overnight.md:72`:

> The default value for `minimum_player_combat` is very likely wrong for quest combat.
> It uses the enemy's level. In the period game, the player fights Nial during Glorious
> Memories regardless of level.

and `memory-bank/audits/quest-stage-reachability-truth-2026-08-12.md:334` recorded the
same for Nial Swiftfling. The convention already exists too:
`memory-bank/source-audits/miniquest-ledger-2026-07-29.md:101` records "**No invented
player-combat gate.** `minimum_player_combat` is set to 1 on all", and the field was
introduced by the Smoking Kills work precisely to carry SOURCED gates, at levels 90 and
111, per `memory-bank/source-audits/quest-smoking-kills-playable-2026-07-18.md:149`.

So the fix direction is already settled: absence of an explicit value means no gate, not
a gate at the enemy's level. An orchestrator probe of the resolved catalog found zero
encounters carrying an explicit `minimum_player_combat`, which does not match the
Smoking Kills record; the implementing pass must resolve that discrepancy against the
data before changing the fallback.

### 16.5 Measured leverage, by controlled rerun rather than assertion

The census did not assert leverage; it measured it by changing one predicate family at a
time in a copied catalog and rerunning the audit:

| Rank | Family | Completable quests | Reachable items |
| ---: | --- | --- | --- |
| 1 | The 704 unemittable action predicates | 46 → 79, so +33 | 2,257 → 2,315, so +58 |
| 2 | The 131 impossible combat predicates, after family 1 clears | 79 → 102, so +23 | 2,315 → 2,354, so +39 |

The 153 item, tool and option gates with no route were deliberately NOT scored, because
each can be downstream of the two families above. That restraint is correct and is the
lesson of section 12.1 finally applied at the right level.

These two numbers now govern the queue. Every remaining acquisition row is small next to
them, and the combat-gate fix is one change to one fallback rather than 131 data edits.

### 16.6 Guard coverage, which is where the next defect will hide

Two catalog-wide pins exist: `required_skills` in `tests/test_combat_quest_gate.py:113-122`
and `xp_rewards` in `tests/test_fremennik_isles_lamps.py:76-84`. Everything else is
unguarded: `required_quests`, `required_quest_points`, quest `required_items`, stage
`required_inventory`, `consumed_inventory`, both option fields, `required_tools`,
`required_actions`, `auto_actions`, `required_routes` and `combat_encounters`.

### 16.7 Correction to sections 13.2 and 13.4

Those sections proposed fixing the reachability audit's `startable` filter to consider
`required_skills`. That work is NOT needed and should not be scheduled. Three
independent measurements agree that no quest skill requirement exceeds what the audit's
idealised maxed player attains: 485 skill requirements, zero blockers, against a derived
combat ceiling of 138 versus a maximum requirement of 100. The audit was correct; only
the runtime was wrong, and that half is merged as `5c4eb06c`. A later queue pass
classified this as remaining work; it is complete.

### 16.8 Blocker one is one missing bridge, not 704 data edits

An investigation of the eleven hand-written action requirements found the structural
reason they cannot pass, and it applies to all 704.

`logic_pure/logic_pure_quest.py:841-850` gates a stage until the action string appears
under `quest_stage_actions[quest_id]`. The only non-test writer is
`_mark_quest_stage_actions` at `:1328-1345`, and it runs only after the current stage
already has no blockers. So a required action can never be satisfied by anything the
quest system itself emits.

The decisive finding is what happens when the mechanic DOES exist elsewhere. Existing
Crafting and Magic actions record telemetry, not quest-stage proofs:
`runtime/runtime_actions_production.py:500-543` and
`runtime/runtime_actions_magic.py:417-499`. **Nothing bridges a performed runtime action
to a quest-stage proof.** An enchant the player really casts leaves no mark the quest
gate can see.

That reframes the whole family. The measured +33 completable quests and +58 items from
section 16.5 are not behind 704 separate data repairs. They are behind one missing
mechanism plus per-quest wiring.

A second structural limit sits beside it. The lookup is quest-LOCAL. Mourning's End
Part I stage 5 requires "Use the rotten apple to sabotage the mourner food stores", and
Biohazard already models exactly that: it produces `Rotten apple` at
`data/quest_data.py:6603-6615` and emits its own action at `:6616-6630`. Biohazard is a
recorded prerequisite of Mourning's End Part I. The proof exists and the dependent quest
cannot see it, because proofs do not cross quest boundaries.

### 16.9 The eleven, classified by what they would actually need

| Required action | Shape | Evidence |
| --- | --- | --- |
| `mournings_end_part_i` 5, rotten apple | Already modelled, blocked only by the quest-local lookup | Biohazard `data/quest_data.py:6603-6630` |
| `the_fremennik_isles` 5, cure and stitch yak-hide armour | Existing contract, one gap | Recipes `leather_yakhide_armour_10824` and `leather_yakhide_armour` exist at `data/crafting_data.py:281-282`; the tanning list at `:373-381` omits yak hide |
| `the_fremennik_isles` 5, Fremennik round shield | Existing `CraftingRecipe` contract | Registry and execution at `data/crafting_data.py:434-456` and `logic_pure/logic_pure_production.py:221-245` |
| `in_aid_of_the_myreque` 6, enchant sapphire | Existing Magic target contract | `enchant_sapphire_ring` and siblings, `data/magic_data.py:332-348` |
| `legacy_of_seergaze` 5, Enchant Level 2 Jewellery | Existing Magic target contract | Emerald tier at `data/magic_data.py:335` |
| `spirits_of_the_elid` 2, Telegrab | Existing contract, but the text is wrong | `telegrab_wine_of_zamorak` at `data/magic_data.py:392-397` is Wine-specific. The source journal says Telegrab the Ancestral key at `generated/quest_catalog_generated.py:13720-13726`; the water-channel steps are later at `:13733-13741`. The requirement conflates two guide steps |
| `mournings_end_part_i` 3, Oronwen repair | Needs new mechanics | No NPC interaction id exists |
| `cold_war` 2, clockwork penguin | Needs new mechanics | No `Clockwork penguin` target or `Crafting table 3` station exists |
| `enakhras_lament` 5, Crumble Undead on the boneguard | Needs new mechanics | Spell `crumble_undead` exists at `data/magic_data.py:528-546`, but stage 5 has `combat_encounters: ()` at `generated/quest_catalog_generated.py:14180-14187`, and the undead test at `logic_pure/logic_pure_combat_model.py:2503-2506` matches only names containing skeleton, zombie, ghost, shade or undead, not Boneguard |
| `the_eyes_of_glouphrie` 3, bucket of sap | Needs new mechanics | No evergreen-sap action; the former pseudo-tool was removed per `memory-bank/source-audits/quest-generated-pseudo-item-cleanup-2026-06-23.md:25-29` |
| `do_no_evil` 3, m'amulet mould | Needs new mechanics | No registry for Do No Evil; the similar Monkey Madness auto action at `data/quest_data.py:8735-8743` belongs to a quest Do No Evil does not require |

So of eleven: one is already modelled, five ride existing contracts with at most a small
data gap, and five need genuinely new mechanics. None is a simple string edit, and all
eleven still need the bridge from 16.8 before any of them can pass.

### 16.10 Why the Vinesweeper slice is still held

`d3365324` is gated green on all eight checks with `remote_lanes: true`, for the second
time, after its one review finding was resolved. It has a full cross-lineage review from
GLM 5.3 Flash, which went deeper than expected: AST-level assertion comparison,
independent arithmetic on the probe figure, and runtime tracing of every link.

It stays unmerged anyway, because section 14.3 recorded that an instrument change gets
two reviewers and the Anthropic block returns in roughly eight hours. The hold now rests
on that rule rather than on any doubt about the slice. Recording the distinction matters:
a rail that bends the moment waiting becomes inconvenient is not a rail.

### 16.11 Retraction: section 16.4 called the combat-gate fix settled, and it is not

Section 16.4 stated that "the fix direction is already settled: absence of an explicit
value means no gate, not a gate at the enemy's level." **That is wrong and is retracted.**
A source investigation established the opposite, and two of that section's supporting
figures were also wrong.

**The probe was wrong.** `minimum_player_combat` is nested, not a top-level encounter
key. The correct path is
`QUEST_DATA[qid]["stage_requirements"][*]["combat_encounters"][*]["npc_configs"]["minimum_player_combat"]`,
declared at `data/quest_data.py:1057-1069` and read at
`logic_pure/logic_pure_quest.py:525-527`. Re-probed with the correct key, **10
encounters set it explicitly**, not zero:

| Quest, stage | Encounter | NPC level | `minimum_player_combat` |
| --- | --- | ---: | ---: |
| `family_crest` 13 | `family_crest_chronozon_170` | 170 | 1 |
| `hunt_for_surok` 5 | `hunt_for_surok_bork` | 267 | 1 |
| `lair_of_tarn_razorlor` 5 | `lair_of_tarn_razorlor_mutant_tarn` | 69 | 1 |
| `lair_of_tarn_razorlor` 6 | `lair_of_tarn_razorlor_tarn_ghost` | 69 | 1 |
| `smoking_kills` 2, 3, 5, 6, 9, 11 | six encounters, NPC levels 20 to 111 | | 85 |

**The Smoking Kills figures were wrong too.** Section 16.4 said that quest carries
sourced gates "at levels 90 and 111". Those are NPC levels. The sourced PLAYER gate is
85, and all six encounters carry 85.

**The enemy-level fallback is deliberate, not an oversight.**
`memory-bank/source-audits/quest-smoking-kills-playable-2026-07-18.md:148-152` records
the field's introduction and states plainly:

> Existing quest encounters retain their prior enemy-level gate unless they opt into
> this field.

**The convention is narrower than section 16.4 claimed.** The miniquest ledger's "No
invented player-combat gate" sentence applies to three named encounters, Bork and Tarn's
two forms, and establishes only that an explicit `1` is the correct way to record a
period-sourced ABSENCE of a gate. It is not a global rule that every encounter should
read 1.

**Neither 2026-08-12 document recorded a decision.** The handoff at
`memory-bank/handoffs/claude-handoff-2026-08-12-overnight.md:70-74` is explicit that its
conclusion is provisional:

> Correct the default for quest encounters only after period sourcing for each
> encounter.

So changing the fallback is not settled implementation. It is either an owner decision
that reverses a recorded design choice, or a per-encounter sourcing programme across 131
predicates. Section 16.5's measured leverage of +23 completable quests and +39 items
stands; the route to it does not.

### 16.12 The period evidence, which is now gathered for three quests

The investigation pinned three pre-cutoff revisions with `curl` and read the raw
wikitext. None documents a required aggregate player Combat level:

- Nomad's Requiem, `oldid=6386610`, `2012-10-11T19:13:29Z`. Constitution 76 and "very
  high (85+) stats" appear under **Recommended**. The level 699 Nomad is a fight, not a
  gate.
- The Void Stares Back, `oldid=6549183`, `2012-11-12T07:10:29Z`. Hard unboostable
  requirements exist for Magic 80, Attack 78, Strength 78 and Defence 10, but no
  aggregate Combat level. The level 599 Pest Queen is a fight, not a gate.
- Glorious Memories, `oldid=6354777`, `2012-10-05T19:59:44Z`. It states a functional
  capability, "Be able to defeat a level 156 opponent who attacks with Melee and Ranged",
  which is prose, not a numeric threshold.

The read-only Darkan server agrees in shape. It gates exactly two quests on aggregate
player combat, both at 85 and both at quest ENTRY rather than per encounter: Smoking
Kills at `SmokingKills.kt:76-89` and Dream Mentor at `DreamMentor.kt:250-261`. A search
across both `.java` and `.kt` found no generic per-encounter gate keyed to the NPC's own
level.

So the period record supports entry-level gates on specific quests and does not support
deriving a player gate from an enemy's level. That is the evidence an owner decision
would rest on, and it is now assembled.

### 16.13 The eleven, re-classified on better evidence

A second investigation found item-level evidence the first missed, and where they
disagree the better-evidenced reading wins:

- `do_no_evil` 3, m'amulet mould: **already modelled**. The item is purchasable, shop
  `hamabs_crafting_emporium`, row `hamabs_crafting_emporium:3:4020`, item id `4020`,
  price 10, at `data/shop_data.py:19`. The first pass reported no registry exists.
- `enakhras_lament` 5, Crumble Undead: **already modelled** as a spell. `crumble_undead`
  is a standard Magic 39 spell with effect `undead_only` at `data/magic_data.py:528-535`,
  merged into combat data at `data/combat_data.py:780-782`. The encounter itself is still
  missing.
- `cold_war` 2, clockwork penguin: `crafting_table_3` DOES exist in `CONSTRUCTION_DATA`
  at `data/construction_data.py:21`, level 34, `Molten glass x2`. What is missing is a
  station action, not the furniture.
- `the_fremennik_isles` 5, round shield: `CONSTRUCTION_DATA["round_shield"]` exists but
  is a level 66 dining-room furnishing from `Oak plank x2`, not the quest item. Do not
  reuse it.

The unchanged conclusion, and the one that governs, is section 16.8's: every one of the
eleven stays blocked regardless of classification, because no runtime path writes
`quest_stage_actions`. An already-modelled mechanic is not a passable requirement.

### 16.14 How much of the game is actually playable today

An earlier census reported zero quest-point gates above the obtainable total, measuring
against the theoretical 333. That is correct in principle and misleading in practice,
because most of those points sit behind quests the action blocker makes uncompletable.

Measured against what is genuinely reachable today, on `2d5bae77`:

```
action-free quests: 60 of 196
closure size: 53 | quest points obtainable: 101
total theoretical points: 333
```

So a player can finish 53 quests and earn 101 quest points, against a catalog of 196 and
333. That closure ignores item and combat blockers, so it is an optimistic ceiling; the
reachability audit's 46 completable quests is the honest figure with those included.

Two quest-point gates sit above the real ceiling as a CONSEQUENCE of the action blocker,
not as defects of their own:

| Quest | Requires | Source |
| --- | ---: | --- |
| `recipe_for_disaster_defeating_the_culinaromancer` | 176 | `generated/quest_catalog_generated.py:15610` |
| `while_guthix_sleeps` | 270 | `generated/quest_catalog_generated.py:24633` |

One quest sits exactly on the boundary. `swan_song` requires 101 and exactly 101 are
obtainable, so a single point fewer would block it too. Record that, because any change
touching quest rewards can silently take it out.

Do not open these as separate work. They close when the action family closes.

### 16.15 The item gaps that are NOT downstream of the action blocker

Section 16.5 declined to score the 153 route-less item predicates because each could sit
behind the action family. A later pass split them, and that split is the useful form:
**34 stage rows in quests that have no unemittable action of their own.** These are the
only item gaps that are independently workable, and they cluster in early quests:

`heroes_quest` carries 7 of them, `holy_grail` 5, `ernest_the_chicken` 4,
`merlins_crystal` 3, `pirates_treasure` 3, `rune_mysteries` 2, and one each in
`a_fairy_tale_i_growing_pains`, `cooks_assistant`, `dealing_with_scabaras`,
`nature_spirit`, `priest_in_peril`, `tai_bwo_wannai_trio`, `the_fremennik_trials`,
`the_restless_ghost` and `vampyre_slayer`.

The remaining 69 sit inside action-gated quests and create no distinct path to a
completable quest, so scoring them would repeat the section 12.1 error.

The three `Pickaxe`, `Hatchet` and `Axe` aliases were correctly excluded as false
positives, because the evaluator accepts a toolbelt or equipped match for those at
`logic_pure/logic_pure_quest.py:485-512`.
