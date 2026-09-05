# Dispatcher shared state restructure — 2026-09-05

Status: the state implementation and expanded per-consumer coverage are complete.
Independent review found no blocking code defect. Full candidate verification
lanes and native reviewer acceptance remain pending. This record must not be read as final acceptance.

## Authority and boundary

The owner chose option 1 in
`memory-bank/handoffs/design-to-impl-rulings-2026-08-13.md` section 57. Sections
53, 53.1, and 58 require an explicit shared state owner, real behavior tests for
changed dispatchers, and a real reviewer pass on the MacBook Pro. The rejected
root-globals rebinding and module-assignment proxy patterns remain prohibited.

This unit changes state access. It does not move dispatcher functions. The later
pure relocation must prove its own body and public-surface equivalence after
this state boundary lands.

Base: `ffb846d6631e4b73731f6573dd8d7c0e77e439db`.
Branch: `goal/dispatcher-state-2026-09-05`.
The agent works in the guarded pool slot 3, outside `addons21`.

## State owner

`runtime/dispatcher_state.py` holds one `DispatcherState` instance. Root imports
it as `_state`. All readers and writers access its fields directly. No scalar
aliases, module proxies, global dictionary replacement, or callable rebinding
are present.

The 13 fields are `player_data`, `current_skill`, `answer_shown`, `card_turned`,
`exp_awarded`, `review_undo_stack`, `direct_action_undo_stack`,
`review_feedback_context`, `review_feedback_initial_xp`,
`review_feedback_flushing`, `pending_bankstanding_notice`,
`pending_review_dialogs`, and `skill_availability_cache_fingerprint`.

The player save remains unset until profile load supplies it. Each stack and
dialog queue has its own factory. `load_player_data` can replace the save and
selected skill together; each new action context reads that current save.
Immutable limits, configuration keys, and derived catalog requirement sets stay
in root. No production caller outside root imports or directly accesses a
retired root state attribute. `RuntimeActionContext` continues to receive the
save explicitly.

Production source contains no root reload call. The live `profileLoaded` hooks
still call `load_player_data` and `initialize_skill`. This unit does not add a
reload compatibility mechanism.

## Fresh scope measurements

Measurements from this draft, rather than the historical 109-body/56-file
estimate:

| Measurement | Value |
| --- | ---: |
| State-consuming named function bodies, excluding nested-body double counts | 191 |
| Additional state-consuming lambda bodies | 4 |
| Named bodies at root module scope | 89 |
| Migrated test files | 53 |
| Migrated test attribute accesses | 2,858 |
| Migrated assignments or deletions | 914 |
| Root lines before | 6,249 |
| Root lines after | 6,221 |
| New state owner lines | 28 |

The migration preserves the complete AST of every existing affected test after
reversing only `addon._state.<field>` access to its former root attribute. It
also preserves all root function and class ASTs after reversing the explicit
state accesses and removing the retired `global` declarations. No existing test
assertion was removed or relaxed. Python symbol-table analysis also checks all
204 affected lexical scopes, including comprehension scopes: each original
state name resolved globally, and every replacement `_state` reference resolves
globally. None is a local, parameter, or closure binding. These are structural
preservation checks; they do not replace executing the changed paths.

The root public surface intentionally loses the four initialized scalar names
`answer_shown`, `card_turned`, `current_skill`, and `exp_awarded`. `player_data`
was absent until profile load. The unrelated `DeferredAchievementDialogs`
class remains an explicit root re-export. The driver will compare the complete
MBP baseline and candidate dumps before any authorized root digest update.

## Behavioral evidence plan

`tests/runtime_actions/test_dispatcher_state.py` adds four focused cases:

1. Two successive profile loads replace the save seen by new action contexts
   and persistence, including legacy Utility selection normalization.
2. Real Firemaking review hooks award one action, persist, reject a duplicate
   award, and undo the complete save and random state through the shared owner.
3. A direct action commits the selected skill and save, then restores both
   through the actual undo dispatcher.
4. Bankstanding and completion dialog queues drain once through the root
   dispatcher after the lower state owner receives their values.

All 53 migrated test modules remain in the focused set, alongside the existing
runtime action suite and the new state suite. The existing real review cases
cover skills, Farming priority, named activities, world clocks, quests, reward
flows, material refusals, and undo.

`tools/dispatcher/state_coverage.py` runs exact unittest module names and writes
a JSON map from each state-consuming function to the test cases that executed
its state-access lines. It reports unexecuted functions explicitly. The first MBP map reports 50 of 195 callable bodies without an executed
state-access line; those gaps remain open. A function call by itself is not completion
proof; the behavioral assertion in each mapped test remains the evidence.

Manual acceptance on the MBP must exercise a real review answer, changed
activity/skill selection, persistence, and Undo. The driver owns the test-host
mirror until explicit transfer and independently arranges Computer Use.

## Checks completed in the local leased tree

- Inverse-AST preservation check: passes root function/class bodies and all 53
  migrated test modules, excluding only state access and `global` declarations.
- Retired root state import/access census: zero remaining imports and zero
  direct `addon` or `self.addon` attribute reads, writes, or deletions.
- Documentation audit: `Audited 653 Markdown and 445 HTML files.` followed by
  `Documentation audit passed.`
- Test-quality audit: `4697 tests across 247 files`, `hard issues: 0`, and
  `structural clone candidates: 31 groups`.
- Worktree guard: `Worktree layout safe:` for the canonical checkout and the
  linked root at the sibling `Anki2/ankiscape_worktrees` directory.
- `git diff --check`: passes.

No behavioral tests have run locally. No pin has changed, and no commit exists.

## MBP focused evidence

The corrected state-owner suite passes `Ran 4 tests in 1.466s` and `OK`. The
first attempt failed its uncontrolled Firemaking roll; the exact failure is in
the pending papercut record. The corrected case forces a successful roll while
advancing the real RNG, asserts that the RNG changed, then verifies undo restores
it. The XP feedback dispatcher and level-up dispatcher both run normally.

The serial migrated/runtime set passes `Ran 860 tests in 208.124s` and
`OK (skipped=1)`. The run directory is
`/Users/armantarkhanian/ankiscape-remote-test-host/reports/dispatcher-state-68f927ed031a`.
Its map is
`/Users/armantarkhanian/ankiscape-remote-test-host/reports/dispatcher-state-focused-2026-09-05.json`.
The trace reports `Unexecuted functions: 50/195`. These require real behavior
assertions; a green focused suite alone does not close the state restructure.

## Pre-existing root-surface instrument blocker

The unchanged baseline mirror emits root surface digest
`0b3438dd0b3be393071081533c3123ddf9bbce7b9b3b53384a778a3c7397da90` under
package basename `repo`. The candidate emits
`215a01149ceb49a0d6df2ffdc8e74973f81161a5bd3f0d68bf2bba7450544ce0`.
The candidate payload is byte-identical to that baseline after removal of
exactly the four scalar records named above. Environment metadata and the
digest footer are outside the tool's hashed payload.

Both root-surface tests skip in the normal remote mirror even when invoked by
the external Qt interpreter: `Qt interpreter is not installed` and
`root initializer requires aqt; use the offscreen Qt interpreter`. The explicit
probe reports `Ran 2 tests in 0.249s` and `OK (skipped=2)`. The remote runner uses
an external Qt environment, but the test discovers it only at
`ROOT/.venv-qt/bin/python`; that mirror-local path is absent.

A separate disposable baseline probe contains the exact tracked archive of
`ffb846d6631e4b73731f6573dd8d7c0e77e439db`, under canonical basename
`ankiscape_fork`, with the existing Qt environment exposed at the expected
symlink. Its path is
`/Users/armantarkhanian/ankiscape-remote-test-host/surface-probe-2026-09-05-ec7b6e61/ankiscape_fork`.
The existing root Qt test runs there and fails: `Ran 1 test in 1.315s`,
`FAILED (failures=1)`. The measured baseline digest is
`fa36126b7ddff3d7d7d6582f80a12000d811533689fe3330e4e3864bb8641732`, while the
unchanged pin is
`2625d3d2bb6110c0faee0a33863cf1bf8e921fe0591460eed25d071bec85e26d`.
Directory naming alone therefore does not reproduce the pin. The driver owns
this separate instrument repair. No test, baseline, or audit was weakened to
make the state conversion pass.

## Expanded state workflow coverage

The expanded state module passes on the MacBook: `Ran 11 tests in 3.470s`, `OK`, with no skips. The module executes 14 real activity command subcases and checks the changed activity state, persisted save, shared runtime context, and exact direct-action undo. Further cases cover reward XP and consumed-input rollback, skill/target selection, carried preferences and live inventory reads, house purchases and policies, quest choices, tool conversion, hidden XP, and queued near-death confirmation. The terminal level-up dialog is captured by the fixture; the real XP and level-up dispatchers still execute.

The first expanded runs found fixture errors only. Exact errors and fixes are preserved in `memory-bank/pending/dispatcher-state-papercuts-2026-09-05.md`. The new full state-access trace passes: `Ran 867 tests in 218.956s`, `OK (skipped=1)`, `Unexecuted functions: 0/195`. It recorded 561 of 631 state-access lines, so this is per-consumer execution evidence, not all-branch coverage. The exact skipped test is `tests.test_achievement_diary_ledger_wiring.CurationLedgerRuntimeExecutionTest.test_real_blood_altar_tablet_checks_diary_before_next_teleport`, with reason `Great Orb item 13 is held in memory-bank/pending/gop-achievement-check-2026-09-01.patch pending the owner's ruling.` The report is preserved in `memory-bank/source-audits/evidence/dispatcher-state-2026-09-05/state-access-coverage.json.gz`; its manifest records source hashes, report hashes, measured counts, and the remote origin `/Users/armantarkhanian/ankiscape-remote-test-host/reports/dispatcher-state-trace-7f1356a980/coverage.json`. No production runtime change was needed for the expanded coverage.

The root-surface prerequisite is a separate driver-owned slice, `goal/remote-surface-guard-2026-09-05`; its source, test, and evidence changes remain isolated from this branch. State acceptance requires that prerequisite to pass both branch and post-merge full gates first.

The frozen migration proof is preserved in `memory-bank/source-audits/evidence/dispatcher-state-2026-09-05/migration-proof.json`. It includes both verification programs, their successful output, the exact base commit, and all 53 existing test files with their baseline Git blobs and current content hashes. The inverse AST check permits only the 13 explicit state-access substitutions and removal of their `global` declarations. It proves that every root function/class body and every complete existing test module is otherwise unchanged. The symbol-table check proves all 204 affected scopes resolve the imported singleton globally, including closures and comprehensions. The trace source hashes match the frozen root, state owner, new tests, and tracer.


## Independent review disposition

The driver obtained an independent Opus review on 2026-09-05. The reviewer read
the frozen product diff and reported that the restructure is correct and
minimal, with no blocking code defect. The reviewer did not execute tests.
All five findings are resolved as follows:

1. **Root surface pin:** acceptance remains blocked until the driver lands the
   instrument prerequisite and compares the complete candidate Qt payload with
   the corrected baseline. Only the four authorized scalar removals may differ.
   The root test and its pin remain unchanged in this tree.
2. **State identity:** `DispatcherState` now uses `eq=False`. The singleton is an
   identity-owned runtime object, not a save-value comparison object. Its
   intentionally unset `player_data` makes `dataclasses.asdict` fail before
   profile load. `dataclasses.replace(state)` creates a new state with
   `player_data` still unset; supplying that field to `replace` raises
   `TypeError` because it is excluded from initialization. These serialization
   and copy APIs are unsupported and are not called for this state. The driver
   verified this behavior from the Python 3.14 standard-library source.
3. **Explicit re-export:** the proposed extra comment is rejected. The existing
   `DeferredAchievementDialogs as DeferredAchievementDialogs` form is the
   standard explicit re-export, and the root surface test protects that name.
4. **Trace identity:** callable identities now include their source line, and
   code lookup uses the function name plus the first decorator line. Duplicate
   nested names remain separate. Comprehension trace frames use the owning
   state-access line. A bounded synthetic runtime test covers decorated
   duplicate names, a deferred generator, and a lambda. It awaits execution on
   the MacBook with the final focused rerun. The previous 195/195 result remains
   valid for its recorded source: the reviewer found no decorated state bodies
   in root. The revised utility and state-owner hashes require fresh evidence.
5. **Random fixture:** the proposed comment-only change is rejected. The
   existing patch advances the real RNG, forces the successful action roll,
   and restores the callable and RNG with registered cleanup. These unittest
   runs are serial; no concurrent test observes the temporary patch.

The review delta changes no root dispatcher, existing test assertion, UI, or
surface pin. Runtime evidence quoted above describes the recorded pre-review
source hashes. Final acceptance requires the revised focused run and the
full/native gates owned by the driver.

Local static checks after the review delta pass: both migration proof programs,
compilation of the changed Python files, and `git diff --check`. The documentation
audit reports `Audited 653 Markdown and 445 HTML files.` and passes. The test-quality
scan reports `4697 tests across 247 files`, `hard issues: 0`, and 31 clone groups.
No behavioral test ran locally.

The normal commit hook required two utility-only adjustments: the tracer test
lives at `tests/runtime_actions/test_dispatcher_state_coverage.py`, and the
state-access survey summarizes its own per-function execution report. The
report fields and behavioral test remain unchanged. No hook was bypassed.


## Final delta review closure

The independent bounded Opus delta review completed with exit 0 on 2026-09-05.
It found no blocking delta defect and required no code change. It accepted the
state identity setting, decorated-function trace lookup, distinct nested
function identities, and the synthetic regression test. The driver also
accepted the unchanged test's move into the existing runtime-actions package
and the extraction of per-function report summarization. This closes the
review findings for author draft `307002127772a6031fae3815a1c17716086fb72d`.

The review is static only. An AST inspection of that draft's root initializer
measured 729 `_state` attribute nodes on 631 distinct source lines. It found
zero state-access lines shared by multiple callable scopes and zero state
attribute accesses outside callable bodies. A separate inspection found none
in function defaults, decorators, or annotations. The review's unverified
textual count of 696 is not used as a measured result.

The tracer still supports one owning scope per state-access source line and
does not record module-scope state access. These limits do not apply to the
inspected root source. They remain explicit limits; no speculative machinery
or extra tests were added to expand the supported input.

Fresh MacBook execution of the revised state owner, tracer, and synthetic test
remains required. Instrument integration, complete Qt proof of the four root
record removals before any authorized digest update, candidate and post-merge
full gates, offscreen smoke, and the real native reviewer pass remain open.
The native initialization canary's exit 71, `Operation not permitted`, is under
separate diagnosis; no native acceptance or dispatcher diagnosis follows from
that failure alone. No product test ran during this review-closure pass.
