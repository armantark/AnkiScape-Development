# Pass 7 owner notes: Fable review and main implementation handoff

Date: 2026-08-03  
Authority: the owner's Pass 7 notes in
`/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd`  
Repository: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`  
Execution branch: canonical `main`; do not create a linked worktree and do not push.

## 1. Goal and priority

Pass 7 is the next player-visible priority. Pause the ordinary depth queue while an
item in section 3 can be reproduced and fixed safely. Finish each settled item as an
atomic batch on `main`. Do not reopen settled project contracts.

This brief is also the running handoff. The root Codex task must append Fable findings,
implementation evidence, blockers, and commit hashes to section 8. Do not rewrite the
owner's source notes in section 2.

## 2. Owner source notes

The following text preserves the meaning and order of Pass 7. The screenshot mapping is
from the RTFD attachment order.

1. The event drawer is still above the vanilla answer bar. The owner wants it attached
   directly to the top of the AnkiScape XP box. Determine whether real Anki reparenting
   makes this impossible; the headless harness is not proof.
2. Clicking **Activities** must open the Activities master list, not the last selected
   activity.
3. The live combat bar truncates its target text to `14 k`, which can be mistaken for
   14,000. It must show an unambiguous value.
4. World time belongs in the main AnkiScape menu, not the review XP bar.
5. The review strip elides the `D&D` label.
6. Text in the review strip glitches and is truncated by the **Bank run** button.
7. Big Top Bonanza needs a draggable split between executing and non-executing acts.
   The order sets priority and permits chained acts. The phrase **Arm for next review**
   is ambiguous and must state whether the activity starts.
8. Users must be able to select and copy any number of event-log entries.
9. One Magic spell-casting cash-out granted 970 Magic XP in one review. The event log
   reported `1/10 tricks`, `score 70`, `unlocked Giant's hand`, and failed levitation
   tricks. This XP grant is high priority to reproduce and fix. The log entry is also
   truncated.
10. XP-drop events must appear before their resulting level-up events.
11. The combat target selector still does not match the recorded selector design. Find
    the existing specification before changing it.
12. Equipment point meters need the same life, Prayer, and Summoning orb icons as the
    review strip. Each meter must also show its fill with a bar.
13. Constitution does not appear to be leveling during combat. Verify the XP award and
    XP curve rather than assuming the display alone is wrong.
14. Activities and D&D entries must be alphabetical. Minigames and D&Ds belong under
    **Activities** in the selection column.
15. Song unlocks must not emit `Added to the music log` popups.

### Screenshot evidence

- Review strip, drawer position, `14 k`, and point orbs:
  `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/Pasted Graphic 13.png`
- Elided D&D badge:
  `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic.png`
- Truncated Activities strip:
  `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic 1.png`
- Magic cash-out event log:
  `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic 2.png`
- Full malformed Magic event:
  `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic 3.png`
- Activities selection hierarchy:
  `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd/2__#$!@%!#__Pasted Graphic 4.png`

## 3. Settled implementation queue

Work in this order unless reproduction proves two items share one root cause.

### P0: progression correctness

1. Reproduce the 970-XP Magic cash-out from Balthazar's Big Top Bonanza against the
   real reducer and the owner's persisted-state shape. Trace source XP, cadence scaling,
   accumulated score, unlock handling, event formatting, and undo. Fix the first faulty
   boundary. Do not merely cap the displayed number.
2. Reproduce Constitution progression during ordinary combat. Verify the period XP
   curve, award split, persistence, level calculation, bar state, and event text. Fix a
   confirmed defect only.
3. Ensure XP events are recorded before level-up events caused by that XP. Preserve
   reverse-chronological display semantics after the write order is corrected.

### P1: broken or misleading review-strip behavior

4. Make target progress text unambiguous and resistant to truncation. Never allow a
   clipped unit such as `14 k` to resemble a magnitude abbreviation.
5. Prevent the D&D label and Activities status from eliding under expected real-Anki
   window sizes. Keep **Bank run** usable without covering status text.
6. Make the event log support normal text selection and copy across any number of
   entries. Keep the existing lazy expansion behavior.
7. Remove song-unlock floating popups. Keep the music-log state update and any durable
   event history required by its owning contract.

### P2: deterministic menu routing and organization

8. Clicking the top-level **Activities** entry always opens the master list.
9. Sort entries alphabetically within the Activities and D&D lists. Put Minigames and
   D&Ds under **Activities** in the selection column, as shown by the owner's arrows.
10. Move simulated world time to the main menu. Do not show it in the review XP bar.
    Never use wall-clock time for gameplay.

### P3: owner-specified UI completion after Fable review

11. Add life, Prayer, and Summoning orb icons and fill bars to the Equipment point
    meters. Reuse the normalized assets and sizing contract already used by the review
    strip.
12. Reconcile the combat target selector with its existing recorded specification.
    Treat the newest Memory Bank record as authority. Stop and report a real conflict;
    do not invent a replacement selector contract.
13. Implement the Big Top Bonanza executing/non-executing draggable priority UI after
    Fable settles the compact interaction and labels. The runtime must have one atomic
    activity state. Two buttons must not start the same activity twice.

## 4. Fable review questions

Use one bounded Fable review through Codex Workflows before section 3, P3. Give Fable
the six Pass 7 screenshots, the relevant existing UI contracts, and live screenshots
from the MacBook Pro. Ask for concrete notes, not a replacement product specification.
The root task records the faithful result in section 8.

Fable must answer:

1. What is the smallest legible layout for the three Equipment point meters that uses
   the existing orbs and fill bars without increasing panel clutter?
2. What compact labels and drag affordance make Big Top Bonanza's executing queue,
   inactive acts, priority, and start state unambiguous?
3. After the root finds the recorded combat-target selector contract, does the proposed
   implementation match its hierarchy, density, selected state, and locked state?
4. Do the corrected review strip and event drawer remain legible at the owner's normal
   Anki window size without covering card material or changing the vanilla answer bar?

Fable does not edit product code or commit. The root task owns synthesis, changes,
tests, and commits.

## 5. Disposable evidence question

Use disposable evidence only for this falsifiable question:

> Can a real Anki window attach the translucent event drawer to the top edge of the
> native AnkiScape XP box while leaving the vanilla answer bar unchanged?

This is a T2 UI question. A focused source read comes first. If the parent and layout
ownership remain uncertain, use one isolated probe outside the shipped tree and a real
Anki session on the MacBook Pro. Record the widget parents, geometry, screenshots, and
whether the tested path actually ran. Stop after one layout probe and one fallback
probe. Delete probe code. Promote only the finding, the minimal production change, and
useful regression coverage.

If both probes fail, preserve the current safe layout and record the exact Qt or Anki
constraint in section 8. Do not call a headless harness result equivalent to real Anki.

## 6. Agentic loop contract

The objective is the count of section 3 items that reach one of these auditable states:
`verified and committed`, `design blocked`, `external blocked`, or `not a defect with
reproduction evidence`.

Run one inner-loop batch at a time:

1. Freeze the live `main` baseline and record `HEAD`, checkout status, and guard output.
2. Select one attributable item or one shared root cause.
3. Reproduce it before changing product code when practical.
4. Implement the smallest coherent fix.
5. Use a separate checker context through Codex Workflows.
6. Run targeted pure, integration, end-to-end, offscreen Qt, and real-Anki checks that
   apply to the batch.
7. Keep or revert from verifier evidence. Append the result to section 8.
8. Commit the accepted batch on `main`, then repeat without waiting for the owner.

Use Codex Workflows for independent, bounded investigation and review leaves. The root
task is the only fixer, integrator, verifier, and committer. Do not add an outer loop
unless three consecutive batches make no material progress for the same diagnosed
reason. An outer loop may change the search method, never project authority or scope.

Stop for a dirty-tree collision with another writer, a contract conflict, a missing
external dependency, a safety failure, or a genuine owner decision. Do not stop merely
because an item is difficult.

## 7. Verification and safety

1. Work directly in the canonical checkout on `main`. Do not create a linked worktree.
2. Before every batch, require a clean or attributable tree and run:

```
python3 tools/worktree_guard.py audit
```

3. Preserve concurrent changes. If another writer touches `main` during a batch, stop
   before editing or committing and record the collision in section 8.
4. Run targeted tests first. Then run both repository lanes before closure:

```
/opt/homebrew/bin/python3 run_tests.py
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python run_tests.py
```

5. For every UI batch, use the MacBook Pro connection and test in native Anki. Follow
   the established connection notes in `memory-bank/pass5-triage-2026-07-31.md`. Capture
   the normal window size, the open menu or drawer, and the unchanged vanilla answer
   bar. Offscreen Qt is additional evidence, not a substitute.
6. Use normalized assets with recorded provenance. Do not add visual assets without an
   asset-size and reachability check.
7. Commit each accepted batch atomically. Never push, skip hooks, use destructive Git,
   or change Git configuration.

## 8. Running Fable and implementation notes

Append new entries. Do not edit earlier entries.

### 2026-08-03 — owner handoff created

- Source: Pass 7 in `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd`.
- Baseline at handoff: `main` at `9035c1a4`; checkout clean; worktree guard passed.
- Fable review: pending.
- Implementation: pending.
- Blockers: none known.

### 2026-08-03 — owner task intake and external-review blocker

- Intake baseline: canonical `main` at `f23c00deb8ff93b5a977036026c772da2e539328`;
  checkout clean; worktree guard passed.
- P0 root-side reproduction began from the real Circus and Combat reducers. The
  period Circus table and its regression test both identify `970.0` as the base XP
  for the first Magic trick, so the reported number is not by itself evidence of a
  multiplier defect. Constitution already has runtime coverage proving ordinary
  Combat mutates `constitution_exp`; the remaining owner report still requires a
  persisted-state, curve, level, bar, event-order, and undo trace before verdict.
- Codex Workflows launch was rejected by the external approval gate because the
  bounded worker manifests would send repository and Memory Bank content to model
  services. No worker ran and no repository content was sent by that launch.
- Blocker: explicit owner approval for that external-model data flow is required
  before the mandatory independent checker and the single bounded Fable review can
  run. Root-side read-only investigation can continue, but no Pass 7 repair can
  satisfy the section 6 acceptance gate while this blocker remains.

### 2026-08-03 — external approval granted; Fable review parked for quota

- The owner approved the Codex Workflows external-model data flow.
- The first two Codex-only P0 investigation leaves ran but exceeded their bounded
  tool-output budgets. No worker edited the repository. Their partial evidence must
  be inspected before a narrower checker run.
- The owner explicitly prohibited Fable and Kimi use until their quotas recover.
  The required Fable product review is therefore parked, not waived.
- The owner-facing co-ideation brief is
  `memory-bank/codex-briefs/pass7-owner-fable-co-ideation-handoff-2026-08-03.md`.
  It asks only about the unresolved Big Top execution queue and Equipment meter
  presentation. It does not reopen settled Pass 7 requirements.

### 2026-08-03 — P0 progression batch verified

- Batch baseline: canonical `main` at
  `cbbfeaa17afb21eb7061922694d26aa607c84a54`; the checkout contained only this
  batch's attributable files and the worktree guard passed.
- Magic cash-out verdict: not a defect. The owner's exact level-9 `max_xp`
  Circus state and rolls reproduce one successful trick, `970.0` Magic XP,
  score `70`, the Giant's hand unlock, and three named failed levitation tricks.
  The 970 value is the period source XP band. No cap or multiplier change was
  made.
- Constitution root cause: AnkiScape started the skill at level 10 with zero
  total XP, then applied the standard XP curve. Pinned `Constitution` oldid
  `6462802` and `Experience` oldid `6545135` establish level 10 at 1,154 total
  XP and level 11 at 1,358. Schema 111 now starts new saves at level 10 plus
  1,154 XP and adds the missing 1,154 baseline once to older saves. The owner's
  `353.883075` earned XP becomes `1,507.883075` total and level 11.
- Runtime correction: Combat no longer writes the calculated level before the
  standard level-up gate sees the old level. Positive sub-one XP is rendered
  with one decimal, so Constitution `0.399` appears as `0.4 XP` instead of
  `0 XP`.
- Event-order correction: each pending XP delta is written before the level-up
  event it causes. The final aggregate popup does not write a duplicate XP row.
- Source evidence is in
  `memory-bank/source-audits/constitution-starting-xp-curve-2026-08-03.md`.
- Verification: 434 targeted pure/runtime/integration tests passed in 80.682
  seconds. The relevant offscreen Qt strip and popup set passed 32 tests in
  1.146 seconds. Codex Workflows run
  `00cab046-6b0b-4af6-a25c-dc8b7ade3fd4` returned `PASS` from the frozen diff
  packet. Earlier checker runs exhausted declared evidence budgets and returned
  no verdict; they made no edits and were not counted as acceptance evidence.
- This was a progression/event-order batch, not a widget geometry batch. Native
  MacBook Pro review-strip evidence remains mandatory for the P1 UI batches.
- Fable and Kimi remained unused as directed.
- Accepted implementation commit: `d12b731a484ed3f1cc089545bdcab5dcf542f2d0`.

### 2026-08-03 — P1 review-strip batch verified

- Batch baseline: canonical `main` at
  `50418d901b46dbf6d0e56c4b37e758aba469e0ec`; the checkout contained only this
  batch's attributable files and the worktree guard passed before and after the
  native check.
- Reproduction: focused tests first failed for the elided 82-pixel D&D seat,
  Shooting Stars status wider than its 177-pixel label, the ambiguous combat
  count suffix, the per-row event widgets that could not select across entries,
  and music tracks entering the popup list.
- Review-strip fix: the D&D seat now reserves 118 pixels; the HUD places its
  status chips and action in one bottom row, which gives the Activities status
  the full upper row; **Bank run** uses its native size and stays at the lower
  right. Combat progress starts with the complete labeled count, for example
  `Kills: 0`, before any trailing text that may clip.
- Event-log fix: one `QTextBrowser` owns all visible escaped and tone-colored
  rows. Normal document selection and copy can cross any number of rows. The
  existing 10-row lazy limit and **Show more** expansion remain.
- Music-popup fix: music tracks and diary tasks both remain in durable event
  history, but only diary tasks enter the popup list and call the achievement
  dialog.
- Automated verification: the focused offscreen Qt strip suite passed 31 tests.
  The focused pure, integration, music, and end-to-end set passed 238 tests.
  Narrow 667-by-602 strip geometry, the vanilla answer-bar position, and card
  non-overlap also passed. `git diff --check` passed.
- Native verification used the owner's MBP Codex connection and the disposable
  Anki base at `/tmp/ankiscape-probe2/anki-base`. The owner set the normal
  window to 712 by 987 pixels. Final captures prove the complete D&D label,
  unchanged vanilla answer bar, strip below the bar, no card-content overlap,
  full `Shooting Stars · awaiting an active star` status, usable **Bank run**,
  and the complete `Kills: 0` prefix. Event-log Command+A and Command+C copied
  two distinct rows. No music-log popup appeared naturally.
- Native evidence is on the MBP under
  `/tmp/ankiscape-pass7-p1-codex-connection/`: `report.md`,
  `01-reviewer.png`, `03-activities.png`, and `04-event-log.png`.
- Codex Workflows run `ccc097ff-3f60-4b1d-a8da-1af0ce21580f` returned `PASS`
  for all four frozen acceptance requirements and proposed no simplification.
  Earlier bounded investigation leaves exceeded their evidence budgets and made
  no edits; checker run `cc93632f-aa27-4576-a985-b6074c9e076f` correctly
  withheld a verdict until native evidence existed.
- Fable and Kimi remained unused as directed. The parked owner-facing Fable
  brief remains the only pending Fable artifact.
- Accepted implementation commit: `222f815210c12e7a966db28747d853f53e268ea4`.

### 2026-08-03 — P2 Activities routing and world-time batch verified

- Batch baseline: canonical `main` at
  `65af3bbdf15a14bbb7b8716b97d3ab4114d27dec`; the checkout contained only this
  batch's attributable files and the worktree guard passed before and after the
  native check.
- Reproduction: five focused tests first failed because the reviewer still
  showed the simulated clock, the main menu did not show it, Minigames was not
  alphabetical, opening Activities restored a saved detail, and clicking the
  top-level Activities entry from a deep-linked detail did not return to the
  master list.
- Routing fix: a top-level Activities selection now always renders the master
  tree. Explicit deep links and activated activity rows still open the named
  detail. Saved activity state is not cleared by returning to the master list.
- List fix: Minigames and Distractions and Diversions remain group headers under
  Activities, and each group's children now render in case-insensitive
  alphabetical order.
- Clock fix: simulated world time moved from the review strip to the main-menu
  status row. It continues to use only the answered-review projection of one
  hour per ten reviews and never reads the computer wall clock.
- Automated verification: the complete focused offscreen UI run passed 411
  tests in 177.711 seconds. The focused pure, integration, and end-to-end run
  passed 214 tests in 130.024 seconds. `git diff --check` passed.
- Native verification used the owner's MBP Codex connection and the disposable
  Anki base at `/tmp/ankiscape-probe2/anki-base`. At the owner's 712-by-987
  reviewer size, the strip had no world clock, the vanilla answer bar was
  unchanged, and card content did not overlap. The main menu showed
  `World time: 12:00 PM` for zero answered reviews while the wall clock was
  about 7:07 PM. Clan Wars detail returned to the Activities master tree on a
  top-level Activities click, and a later Shooting Stars row click still
  opened the detail. Full native traversal proved 29 alphabetical Minigames
  and 17 alphabetical Distractions and Diversions entries.
- Native evidence is on the MBP under
  `/tmp/ankiscape-pass7-p2-codex-connection/`, including `report.md` and 12
  numbered screenshots.
- Codex Workflows run `3452c9ca-5e43-4bd0-a19e-c65969a19dba` returned `PASS`
  for all four frozen acceptance requirements and proposed no simplification.
  Earlier read-only investigation run `14dce081-994f-4b6d-ad76-c702cb77a998`
  exhausted its evidence budgets, returned no verdict, and made no edits.
- Fable and Kimi remained unused as directed. The parked owner-facing Fable
  brief remains the only pending Fable artifact.
- Accepted implementation commit: `129f9a016b4b0317d44e1f3468ecb051f52b562b`.

### 2026-08-03 — P3 Combat selector batch verified; two design items parked

- Batch baseline: canonical `main` at
  `37310366f44031a8a64dbc78cc07be57556a0786`; the checkout contained only this
  batch's attributable `ui/ui.py` and `tests/test_main_menu_widget.py` changes,
  and the worktree guard passed before native verification.
- Reproduction: a new offscreen Qt regression opened Combat with the saved
  `seagull` target and first failed because its current row remained outside the
  viewport after the dialog was shown.
- Selector fix: after the live Combat tree is mounted, a zero-delay Qt callback
  centers its saved/current row. The callback ignores an obsolete rebuilt tree
  and safely returns if Qt deleted the widget before the deferred call runs.
- Durable regression coverage also pins the existing D.1 contract: 30-pixel
  alternating rows, one transient selection, expanded current group, green and
  bold persistent current state, no blue selection on restore, a dim locked
  Wall beast with `Slayer level 35`, and level-ascending children in every
  group.
- Automated verification: the five focused selector tests passed. The complete
  main-menu Qt module passed 381 tests in 120.885 seconds, and the review-strip
  module passed 31 tests in 0.895 seconds. The test-quality audit found 3,777
  tests across 173 files, zero hard issues, and 19 pre-existing clone groups.
  `git diff --check` passed; no assets changed.
- Native verification used the owner's regular MBP Codex connection and the
  disposable Anki base at `/tmp/ankiscape-probe2/anki-base`. The deployment
  hashes matched the accepted P2 source and this P3 source exactly. At a
  1280-by-752 menu, search and keyboard navigation changed only the transient
  selection; activation moved the persistent target. Reopening Combat centered
  `Black bear (Lvl 19)` with green/bold current styling. `Wall beast` was dim
  with the exact `Slayer level 35` reason. At the owner's 712-by-987 reviewer
  size, the vanilla **Edit / Show Answer / More** bar remained unchanged and
  card content did not overlap the add-on strip.
- Native evidence is on the MBP under
  `/tmp/ankiscape-pass7-p3-selector-codex-connection/`, including `report.md`
  and the numbered selector and reviewer screenshots.
- Codex Workflows checker run `808ee8a2-7993-4e41-adb2-144cfd002b56`
  returned `PASS` for all four frozen acceptance requirements. Exploratory run
  `02eefa05-e686-4fde-9e39-eb03fcd6d6d0` exhausted its processed-token budget
  and returned no verdict. Initial checker launch
  `0b67e05b-f792-44b5-8a25-fc372dd1465c` failed before model startup because
  `/tmp` was not a trusted repository. Neither failed run edited files or
  counts as acceptance evidence.
- Equipment point-meter layout and the Big Top executing/non-executing priority
  UI remain design-blocked. Their runtime and visual contracts require the
  owner/Fable co-ideation recorded in
  `memory-bank/codex-briefs/pass7-owner-fable-co-ideation-handoff-2026-08-03.md`.
  Implementing either now would invent unsettled interaction details. This is a
  recorded contract stop, not a request to reopen any settled Pass 7 design.
- Fable and Kimi remained unused as directed. The parked Markdown brief is the
  only pending external-review artifact.
