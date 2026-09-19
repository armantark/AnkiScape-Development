# Fable grill: remove recurring work from AnkiScape

## Goal and current state

Choose the smallest architectural changes that remove repeated diagnosis and coordination work. Keep the implementation goal paused until the owner explicitly resumes it.

The owner requested a one-time papercut cleanup. They then requested this decision record and a prompt for a later grill with Fable. This file does not authorize implementation, a Fable call, a scheduled restart, a push, or a pull request.

The owner's inspiration was a short statement about trace review: repeated lessons should make a single prompt sufficient for a reliable change. The useful test is concrete: **which step disappears for the next caller?** More instructions alone do not meet that test.

Canonical repository:
`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`

Cleanup baseline: `7f736d5c63ca0d301b1789798e75fa2737435f4c`.
Evidence directory: `memory-bank/source-audits/papercut-cleanup-2026-09-18/`.
The cleanup plan is `memory-bank/plans/papercut-cleanup-2026-09-18.md`.
The goal checkpoint is `memory-bank/pause-checkpoint-2026-09-18.md`.

## Decisions in the maintenance change

These decisions remove caller work while they preserve the existing acceptance rules.

| Decision | Step removed | Constraint preserved |
| --- | --- | --- |
| Skip an existing regular asset file before a network lookup. | A caller no longer needs network access to preserve a file. | Forced replacement and dry-run source checks retain their behavior. Unknown source metadata stays unknown. |
| Give the Hunter shared-image map one source owner. | Asset tools no longer maintain a second exclusion list. | Runtime image paths and exported values stay identical. |
| Validate every trim target before any processing. | An invalid path no longer looks like a successful empty batch. | A mixed valid/invalid request changes no files. |
| Put focused selection in the remote runner. | Callers no longer patch private launch functions. | Exact test count, zero skips, mirror lock and unfinished-run reconciliation remain mandatory. Full-suite floors remain unchanged. |
| Report every module-surface mismatch and retain lane diagnostics. | A repair no longer needs repeated full runs just to reveal the next failure. | All digest pins, validators and failure exit codes remain unchanged. |
| Resolve local imported TestCase ancestry statically. | A real test no longer needs a redundant base just to satisfy the audit. | Unknown ancestry fails closed. No product code runs during the audit. |
| Put pool status, duplicate-branch checks and safe returns in the worktree guard. | The operator no longer needs raw pool probes or a manual release checklist. | A gate marker, dirty checkout, uncertain lease or held coordination lock blocks return before detachment. |
| Correct current project guidance. | A new task no longer has to reconcile retired dispatch instructions with the current workflow. | Historical incident records remain intact. The implementation goal stays paused. |

The cleanup does not loosen a rail to make a failing candidate pass. It does not change gameplay or menu design.

## Architecture that slowed this run

### 1. A small logic probe can load the asset catalog

`core/constants_parts/skill_catalog.py:56` enumerates the tree image directory during import. `core/constants.py:160` requires `SHOP_ITEM_IMAGES["Ogre arrow"]` during import.

A historical Magic comparison archive with only Python and JSON could not import the same runtime surface. It needed asset directories too. This is a real dependency cost: a small logic question needs a much larger environment.

Equipment, capes, diaries and shops also refer back into shared logic. Relevant edges are in `logic_pure/logic_pure_equipment.py:270`, `logic/cape_logic.py:291`, `logic/achievement_diary_logic.py:37` and `logic/shop_logic.py:273`. Some imports are lazy. These edges do not prove a current import failure.

**Question for Fable:** Can deterministic catalog construction replace import-time filesystem discovery without a broad rewrite? What must stay observable at the public facade?

### 2. Refactors must preserve function identity metadata

`tools/module_surface.py` records a function's `__module__` and `__qualname__`. A move can preserve outputs while it changes that public surface.

The preserved Magic candidate `a8137bab2566b45e52585c580794a84563241b7e` failed full verification with module-surface mismatches. Focused behavior tests did not establish compatibility. That candidate remains unmerged and outside this cleanup. The exact complete before/after runtime dump is still needed before anyone claims a specific list of functions explains every mismatch.

**Question for Fable:** The existing ruling preserves defining-module identity. What single facade or extraction pattern preserves that contract by default? Do not reopen the ruling or remove pins to accept the pending branch.

### 3. The feedback path has a large minimum cost

Full plain and Qt runs are required. The remote mirror has one owner because a concurrent sync can change files under an active run. That serialization has a purpose.

The previous public runner exposed only full lanes. Focused callers used private wrappers. The maintenance change adds a public focused route and retains full diagnostics. This removes avoidable preparation and repeated diagnosis. It does not establish a faster full suite.

Two focused selections included existing checks for an unavailable optional environment. The runner correctly refused their skips. The accepted selections covered each applicable environment explicitly. This is a selection cost, not a reason to ignore skips.

A fleet complexity hook also inspects large source files. Its cost is separate from product runtime. No hook or threshold changed in this pass.

**Question for Fable:** Which further speed improvement can preserve the same evidence: selective preparation, immutable snapshots, or content-based reuse? Require a measurement and an invalidation rule before choosing a cache or more workers.

### 4. Generated data needs an explicit source identity

The Barcrawl generator now owns its vendor rows. `tests/bar_crawl/test_vendor_actions.py` verifies regeneration, idempotence and preservation of the other catalog fields.

A separate equipment generator accepts an external `game-main` source. Its default path points to a mutable checkout. A later source update can change unrelated generated rows. Existing count pins exposed such drift; the pins did not cause it.

**Question for Fable:** Should generated output record a source revision, a content digest, or an immutable snapshot reference? Define the update operation before adding a new provenance store.

### 5. Current-state prose has multiple owners

Old dispatch instructions and paused-work status survived in current guidance. This pass corrects the current documents and preserves the historical records.

**Question for Fable:** Which current facts should have one machine-readable owner, and which facts belong in prose? Require removal of a duplicate update step. Do not create another ledger that also needs manual updates.

## What happened in the Union Alpha trial

The source is the historical trial record in `memory-bank/progress.md`, under “Union Alpha trial — 2026-09-16, Barcrawl slice”. This cleanup inspected that record and current source. It did not repeat the trial or benchmark the model.

| Reported obstacle | What the evidence supports | Present disposition |
| --- | --- | --- |
| Order-independent collection looked impossible. | The engine already checks every required action at `logic_pure/logic_pure_quest.py:787`. The orchestrator's separate-stage brief added confusion. | Model and orchestration mistake. No new quest engine is needed. |
| Vendor rows went into generated output by hand. | Regeneration could erase the feature. The generator now owns the rows, with a preservation test. | Real ownership hazard, already repaired. |
| A proof requirement crossed into Scorpion Catcher. | It violated the quest-local contract. Commit `2dcc9eee` removed that coupling. | Orchestrator design mistake, already repaired. |
| Focused tests passed while full tests failed. | Focused coverage did not establish complete acceptance. Full gates caught the regressions. | Keep full gates. Do not call focused evidence sufficient. |
| A lane exceeded its time limit. | The historical record attributes the failure to use of the slower host. | Execution-route mistake. Historical timing is not a current benchmark. |
| Agents claimed nonexistent steering or waited for nonexistent reviewers. | The trial record reports fabricated coordination. | Model provenance failure. It is not a product architecture defect. |

The generator hazard and environment cost deserve architectural attention. The invented blockers do not justify additional product abstractions.

## A tool failure found during this cleanup

The Claude resolver stalled before model launch on a large inline review packet. Its Bash whitespace-removal check consumed CPU before the quota preflight. A bounded canary reproduced the slow check; a regex check on the same bytes completed promptly.

A short prompt with scoped read-only repository access bypassed the slow path and started the review. This was a shell-wrapper defect, not slow model reasoning or an AnkiScape architecture limitation. The wrapper lives outside this repository. It was found while verifying the repairs, so the one-level scope rule leaves its code unchanged. The exact incident and canary are retained in the cleanup evidence.

## Limits that remain

- Native journal refresh and navigation design decisions remain with the owner. This cleanup does not reopen settled menu styling.
- The shared native reviewer path still lacks acceptance bound to the exact loaded revision. Offscreen success does not settle native behavior.
- External service, quota, network and source-availability incidents cannot be erased by a local patch. The inventory identifies them separately.
- Operator mistakes include guessed paths, oversized tool output and inaccurate initial diagnoses. The cleanup records these candidly. A new rule is not evidence that the mistake cannot recur.
- Magic extraction and the rest of the implementation queue remain paused. Preserve the P8 candidate and its dirty P6 predecessor.

## Verification and acceptance record

The frozen inventory covers 2333 recorded entries from 17 source files, grouped into 180 cause groups. These are recorded entries, not unique incidents. The disposition report identifies 14 repaired groups, 35 earlier repairs, 83 operator-error groups, 21 external blockers, 25 design decisions and 2 paused-feature groups.

The early source candidate passed both full runtime lanes. Its documentation audit then refused a nested test-module selector in the review notes. The exact original report and failure log are preserved. The readable command now uses the equivalent file-path selector. The final review also added conditional-import rejection cases and normalized qualified branch names before lease checks.

Root verified the final repairs with inert tooling regressions and an exact-count MacBook Qt run, including the real target-level-order widget methods. The evidence index is `memory-bank/source-audits/papercut-cleanup-2026-09-18/final-verification.md`.

This file freezes before final promotion. The acceptance authority is the full-gate receipt for canonical HEAD, in the shared Git directory under `ankiscape-promotion-evidence`. An earlier lane pass or focused result does not accept a different commit. The guarded landing refuses an incomplete receipt or a candidate that does not contain current main.

## Copy this prompt into Fable

```text
<context>
We are reviewing how to simplify AnkiScape after a one-time papercut cleanup. The implementation goal is paused. Do not resume it, schedule a restart, edit source, install tools, push, or create a pull request. This is a design grill with the owner.

Read /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/handoffs/fable-grill-papercuts-2026-09-19.md. Read its source references before treating a claim as established. The full incident inventory and evidence are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/papercut-cleanup-2026-09-18/.
</context>

<goal>
Grill me on the few architectural choices that would remove the most recurring work. Use this test: after reviewing traces and refining the tools, the next change should need fewer steps and less supervision. Prefer deletion, one source of truth and small stable interfaces. Do not substitute more rules, extra layers or a broad rewrite for a demonstrated improvement.
</goal>

<method>
Start with the highest-impact unresolved choice. Ask one short question at a time. Explain the observed cost, the smallest viable alternatives and your recommendation in plain language. I do not read generated code. Separate owner decisions from facts that you can verify yourself. Keep settled gameplay and UI decisions settled. Challenge my assumptions when evidence warrants it. If evidence cannot distinguish alternatives, propose the smallest reversible experiment and state what result would decide.
</method>

<constraints>
Preserve full source and merged-tree verification, fixed thresholds, pinned behavior, exact evidence provenance, one owner per mutable test mirror and safe worktree placement. Treat historical Union Alpha behavior as historical evidence. Do not infer an engine limitation from a model's report. Do not invoke another model or message another task.
</constraints>

<output>
During the grill, maintain a concise decision list in the conversation. For each settled choice, record the problem, selected approach, rejected alternative and reason, the caller step removed, affected contract and proof needed. Finish with an ordered implementation handoff and unresolved owner choices. Do not implement the handoff.
</output>
```
