# Test Quality Standard

## Purpose

The suite is a regression instrument, not a test-count target. Prefer one test
with named `subTest` scenarios when setup, exercised behavior, and assertions
are the same. Keep separate methods when they protect different branches,
fixtures, layers, or expected-failure contracts.

## Mechanical Gate

Run:

```bash
/opt/homebrew/bin/python3 tools/audit_test_quality.py
```

`tools/audit_test_quality.py` fails on:

- module-level `test_*` functions that `unittest` discovery ignores;
- `test_*` methods outside a `unittest.TestCase` class;
- tests with no assertion or assertion-helper call;
- literal membership checks against text read directly from a file, because
  source spelling does not prove executable behavior;
- identical method bodies inside the same test class.

The audit reports constant-normalized structural clones for human review but
does not fail them automatically. Similar test bodies can still be legitimate
when constants select different production branches, fixtures change the
system under test, or one method is an intentional `expectedFailure` contract.

## Verification

Use the Homebrew Python for the pure suite because the system Python is too old
for the repository's type syntax:

```bash
/opt/homebrew/bin/python3 run_tests.py
```

Use the shared Qt virtual environment for real offscreen discovery:

```bash
QT_QPA_PLATFORM=offscreen \
  '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.venv-qt/bin/python' \
  -m unittest discover -s tests
```

Report executed methods, ordinary passes, skips, and expected failures
separately. Never describe `Ran N tests` as `N passing` when the total includes
skips or expected failures.

### Behavioral proof

A green suite is necessary but does not prove that a gameplay family works. A
verification pass must construct state through real gameplay paths from a fresh
default save, drive the production runtime kernel, and reach every reward through
a real path. Do not mock, stub, hand-feed, or delete a production function or
state field that belongs to the system under test. The verifier must list any
such substitutions because they are likely places for defects to hide.

This rule follows three families that stayed green while mechanically broken:

- Skeletal Horror mocked `apply_combat_burst_pure` in every mechanics test, so
  the suite proved wiring but not that the boss could be fought.
- Clan Wars ended every match nil-nil at combat levels 10 through 99, leaving
  wins, losses, kills, deaths, and the red-portal consequence unreachable.
- Fish Flingers asserted that a sourced medal was absent and kept it unearnable
  through a full review.

Ask whether each test proves the source contract or merely restates the current
implementation. Confirm that a purpose-written regression test fails against the
unfixed implementation before accepting it as load-bearing.

### Mutation proof

Run mutation proofs from a linked worktree created or leased through
`tools/worktree_guard.py`, never an rsync copy under `/tmp`, whose resolved
`/private/tmp` paths fail unrelated tests. Preview the affected selection with
`run_tests.py --count`, confirm it is green, then run the identical selection
against the mutant through the probe, which restores the source bytes before it
exits and exits 0 only when the selection went red:

```
/opt/homebrew/bin/python3 tools/maintenance/run_mutation_probe.py logic_pure/logic_pure_combat_model.py /tmp/combat_model_mutant.py -- /opt/homebrew/bin/python3 run_tests.py test_state_repair
```

An affected behavior test must fail; path-identity, missing-asset, or unrelated
failures are invalid red evidence. Full-suite release gates are separate and are
not rerun for each mutant. After an uncatchable stop, recover the source from the
backup path the probe printed first.

### Independent, cross-lineage review

Pair an author with a verifier from a different model lineage. The rule is
symmetric, not provider-specific. The verifier must rerun the relevant lane and
drive the real logic rather than accept the author's counts or review the same
reasoning from source alone.

On 2026-07-26, Claude agents built and merged nine families. All nine breadth
criteria were reported green, and three Claude verification passes found nothing.
One Sol pass then found four shipped defects:

- Tears of Guthix counted a visit's own payout toward the next visit's
  100,000-experience requirement.
- Abandoning a Treasure Trail rerolled it instead of resuming it.
- Skeletal Horror resolved death as safe, kept every item, and wrote no grave,
  contradicting both of its audits.
- Clan Wars destroyed all seven carried items although its audit said three were
  kept.

Two of those defects were protected by tests that stubbed the code they claimed
to test. By 2026-07-30 the same cross-lineage pattern had found defects in five
consecutive passes: the nine-family batch, four newest families, miniquest work,
Conquest cycles, and the B2 closeout.

The reverse direction produced the same result on 2026-08-19. Opus reviewed six
Sol-authored re-land slices and caught a Crafting predicate that disagreed with
the menu-build path, a Smithing disabled state that vanished on re-render because
it read a boolean captured at menu-open, and a save-destroying Jungle Potion
soft-lock. In the last defect, a Shattered Heart strange rock replaced the clean
herb produced by a quest step, making the quest permanently unfinishable in
`1 - 0.99**5 = 4.9%` of playthroughs and blocking Shilo Village plus thirteen
exclusive items. One test hand-fed a boolean from a different pure function than
production used. The other called `player_data.pop("shattered_heart", None)`,
deleting exactly the state that triggered the bug.

### Qt lane and harness fidelity

The plain lane, `/opt/homebrew/bin/python3 run_tests.py`, has no `aqt`. Widget
tests guarded by `skipUnless(HAS_AQT, ...)` therefore skip, so the plain lane is
a smoke check and cannot authorize a UI landing. The shared offscreen Qt command
above is the UI gate. Its `.venv-qt` lives in the canonical checkout, not in each
worktree, so worktree runs must use the displayed absolute interpreter path.
Treat an increased plain-lane skip count as evidence that relevant tests may not
have executed.

Parent-sensitive Qt fixes also require a production-shaped harness. Anki's
`AnkiQt` is a `QMainWindow`. It creates `bottomWeb = BottomWebView(self)` and then
calls `self.form.centralwidget.setLayout(self.mainLayout)` at
`aqt/main.py:966-978`, which reparents `bottomWeb` into
`mw.form.centralwidget`. AnkiScape drawers remain parented to `mw`, so a drawer is
a sibling of `centralwidget`, not a sibling of `bottomWeb`, and paints above
children inside the central widget.

`tests/test_review_strip.py` once installed `mainLayout` directly on the object
used as `mw`, collapsing those parents. That harness made `stackUnder`, sibling
index ordering, and `mapTo` coordinate fixes pass while doing nothing in Anki. On
2026-08-01, a purpose-written sibling-stacking test was green for an event-log
z-order fix that was completely inert in production. Tests for parent-sensitive
behavior must reproduce the `QMainWindow` plus `centralwidget` split and must fail
against the unfixed implementation.

### Historical checker and report failures

Ox Alpha was retired permanently on 2026-08-26. Its incidents remain useful as
reviewer doctrine, not as live routing instructions.

On 2026-08-21, Ox Alpha and Opus reviewed the same herb/vine merge from an
identical brief. Ox Alpha returned `accept` with zero findings after correctly
checking every named claim: the asset ruling, all seven reachability fields, 45
targets, and 182 placeholder markers. Opus returned `accept_with_findings` with
three findings. The substantive confirmed defect changed seven vine items from
`(True, 'hunter')` to `(False, 'material')`, a behavior present on neither parent.
The general lesson is that a checker can confirm enumerated claims without being
a finder of unprompted defects. A bounded checker does not replace a reviewer
whose job is to inspect the full diff for changes nobody requested.

The same day's 24 undo-seam migrations showed that a completion report is not a
reliable index of the committed tree. One slice left a deliberate mutation in an
unrelated handler and reported completion with a focused green test. Its changed
hunks were at 2214-2215 while its assigned range was 2795-2833. Another shipped a
refusal-path test that could not kill an unconditional
`return updated, True` mutant, so the seam committed a change that the pure
function refused while telling the player it failed. An unrelated orchestration
seat independently reported: "ox-alpha contracts and commit messages assert
probes, rows, and counts that do not exist in the committed tree."

Verify completion claims against the tree: compare changed line ranges with the
assigned range, run the shared suite for every edited file, and reapply the exact
reported mutant instead of trusting a claimed mutation proof.

## Manual Playtesting

The owner plays the real save from level 1 at normal review pace and does not
create development saves for late-game checks. On 2026-07-11, the Construction
12-step smoke test was rejected as unreachable: "I currently would have level 1
so there's no way for me to reliably test that".

Manual test instructions must lead with low-level checks such as rung-zero
purchases, level-1 targets, and visible UI presence or gating. Cover level 60+
and other late-game behavior with pure and offscreen Qt tests instead of
assigning it as owner-run manual verification.
