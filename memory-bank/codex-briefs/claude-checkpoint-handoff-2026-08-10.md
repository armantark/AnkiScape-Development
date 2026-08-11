# Claude handoff: clean AnkiScape checkpoint

Copy the complete prompt below into the Claude task.

```xml
<role>
Take custody of the canonical AnkiScape checkout. Use the repository and its
Memory Bank as the source of truth.
</role>

<goal>
Continue only the new task that the owner gives with this handoff. If the owner
gives no new task, verify the checkpoint and stop. Do not restart the paused
autonomous goal.
</goal>

<checkout>
/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork
</checkout>

<authority>
Read these files before you plan or edit:

1. AGENTS.md
2. memory-bank/projectbrief.md
3. memory-bank/productContext.md
4. memory-bank/activeContext.md
5. memory-bank/systemPatterns.md
6. memory-bank/techContext.md
7. memory-bank/progress.md
8. memory-bank/codex-briefs/goal-pause-handoff-2026-08-10.md

Use the newest Memory Bank record when two records disagree. Verify the live
Git state before you trust the handoff.
</authority>

<checkpoint>
Codex closed the resumed implementation interval at commit fb8735af. The
canonical branch was main and the checkout was clean. Main was 522 commits
ahead of origin. Nothing was pushed.

The interval audit covered 52 prior commits and 35 grouped slices after Pass 8.
No slice has missing implementation in a linked worktree. All linked worktrees
were clean. The only non-ancestor branch had the same stable patch ID as work
already in main.

The complete plain suite passed 4,053 tests with 494 expected skips. The complete
offscreen Qt suite passed 4,053 tests with three expected skips. Documentation,
test quality, compilation, tracked JSON, placeholder, asset, diff, reachability,
and worktree checks passed.

The reachability audit records 102 orphan inputs and 101 blocked actions. These
are explicit source or dependency depth. They are not partial implementation.
</checkpoint>

<scope>
Preserve the 35 closed items in
memory-bank/codex-briefs/goal-pause-handoff-2026-08-10.md. Reopen one only when
you reproduce a concrete defect.

Preserve concurrent dirty changes if the live checkout is no longer clean.
Do not overwrite another agent's work. Do not create a linked worktree below
addons21. Do not push to a remote.

The autonomous goal remains paused. A later explicit owner instruction to
continue, or a goal-state change, overrides this pause.
</scope>

<design_state>
No new owner or Fable design question arose during the resumed interval.

Two older Pass 7 interface questions remain in this packet:
memory-bank/codex-briefs/pass7-owner-fable-co-ideation-handoff-2026-08-03.md

They concern the Big Top execution queue and the Equipment point-meter layout.
They predate the resumed interval. Use that packet only when the owner asks to
resolve those designs. Do not implement them before the owner settles them.
</design_state>

<execution>
For a new implementation task, inspect the owning contract and current code.
Make the smallest complete change. Do the relevant focused checks and required
repository checks. Update the Memory Bank. Commit the complete attributable
change on the authorized branch.

For a review, design, or explanation task, inspect and report. Do not change
product code unless the owner also asks for a change.
</execution>

<stop_rules>
Stop when the owner gives no new task after the checkpoint check. Stop on a
real authority conflict, another-writer collision, or an owner-only decision.
Record a blocker with exact evidence. Do not invent a design to clear it.
</stop_rules>

<required_output>
Report the live branch and commit, the files changed, the checks completed, and
any exact blocker. State whether the checkout is clean. State that nothing was
pushed unless the owner explicitly requested a push.
</required_output>
```

