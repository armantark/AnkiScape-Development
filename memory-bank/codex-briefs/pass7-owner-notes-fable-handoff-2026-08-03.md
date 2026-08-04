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
