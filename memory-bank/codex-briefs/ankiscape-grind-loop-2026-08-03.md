# AnkiScape grind loop — run this inside Codex

Date: 2026-08-03. Author: Claude. Reader: a Codex session that runs unattended.

This document tells you how to run a continuous work loop on AnkiScape. You pick
the work, you do the work, you prove the work, you record the work, and then you
start again. The owner is not in the loop.

## 1. The standing goal

This is the owner's goal. It does not change between iterations.

> Finish implementing everything that does not require my design input. If you
> find design gaps, record them clearly so I can pick them up in the design
> thread. Work breadth-first across AnkiScape. Make every settled skill and
> feature family mechanic-complete. Use the smallest readily available,
> period-appropriate data set that exercises all of its mechanics end to end.
>
> A horizontal MVP is not a partial demo. Entry gates, gameplay states,
> policies, failure modes, rewards, persistence, undo, UI, assets, and tests must
> all work.
>
> Harvest enough source data to reach mechanical completion. Where a value needs
> an intense dig, use a registered placeholder instead of a block on the family.
> Mark the placeholder at the value and list it in
> `memory-bank/placeholder-values.md`. Defer exhaustive catalogs, rare-roll
> precision, and other slow data harvesting beyond what mechanical completion
> needs.
>
> A placeholder stands in for a value the period game had and we could not
> recover. It is never permission to invent content the period did not have.
>
> Record genuine design conflicts or blockers for the design thread. Cross
> communicate with the Darkan restoration thread to prevent duplicated work.
>
> If you finish the first breadth and quota remains, move to the next level of
> breadth.

## 2. Repository facts

- Path: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`
- Branch `main` is the integration branch. This is a solo project, so you can
  merge to `main`.
- Never push to any remote. Never change the git config. Never force push.
- Never use `--no-verify` or any other flag that skips a hook.

### Worktree safety — read this before the first iteration

Anki loads every child folder of `addons21` that contains an `__init__.py`. A
second checkout there becomes a second live copy of the add-on. It duplicates
hooks and serves stale code.

1. Never give `git worktree add` a destination below `addons21`.
2. Create every worktree with this command:

```
python3 tools/worktree_guard.py add <branch> --name <leaf>
```

3. Run `python3 tools/worktree_guard.py audit` before and after each worktree
   change.
4. Never delete a dirty or unmerged worktree. Move it to the safe root instead.

## 3. The loop

Do these steps in order. Then start again at step 1.

1. **Read the queue.** Open `memory-bank/loop-queue.md`. If it does not exist,
   create it from section 5 of this document. Take the top unblocked item.
2. **Check the stop condition.** If `memory-bank/GOAL-BLOCKED.md` exists, stop
   the loop and report. See section 7.
3. **Create a worktree** for the item with the guard command in section 2.
4. **Harvest the source data** the item needs. Obey the evidence order in
   section 4. Stop the harvest at mechanical completion.
5. **Implement the item.** Cover all ten completion elements in section 6.
6. **Write the tests.** Drive the real kernel. Never mock the code under test.
7. **Run both test lanes.** See section 8. Both must be green.
8. **Record the result.** Append to `memory-bank/loop-notes-2026-08.md`, update
   `memory-bank/loop-queue.md`, and add a source audit under
   `memory-bank/source-audits/` for any family that reaches completion.
9. **Commit and merge** the branch into `main`. One item is one merge.
10. **Add any new work you found** to the bottom of the queue. Add any design
    gap to `memory-bank/design-thread-queue.md` instead. Do not implement a
    design gap.

Do one item per iteration. Do not batch several families into one merge.

## 4. Source rules

Search for evidence in this order. Stop at the first source that settles the
value.

1. Darkan
2. The rev-727 cache
3. game-main (this is 2011Scape)
4. The other caches on disk
5. The wiki, as corroboration and as a gap filler for authentic pre-EOC content

Two rules govern what you write down:

- If a value needs an intense dig, register a placeholder. Mark it at the value
  as `PLACEHOLDER(<dotted.key>)` and add a row to
  `memory-bank/placeholder-values.md` with the reason and the thing that would
  retire it.
- Never invent content the period game did not have. A placeholder replaces a
  lost value. It does not authorize a new mechanic, a new item, or a new reward.

The Darkan restoration thread runs in parallel. Before a deep dig into Darkan
data, read `memory-bank/shared-source-harvest-ledger.md` and add your own entry
when you finish. This prevents two threads from harvesting the same table.

## 5. The queue as of 2026-08-03

Copy this into `memory-bank/loop-queue.md` on the first iteration.

1. **Pass 6 item B.15 — skill-selector hybridization.** The brief is
   `memory-bank/codex-briefs/pass6-b15-handoff-2026-08-03.md`. Implement only the
   spec in that brief. The rest is design item D.1.
2. **Design answer 3.25 — guardian coin drops.** Remove the Dungeoneering
   starter Herblore coin cache. Critical-path guardian-room enemies on C5+
   floors split 1,010 coins for players who have Druidic Ritual and Herblore 5.
   Register the amount as `PLACEHOLDER(dungeoneering.starter_guardian_coin_drops)`.
   C1 to C4 floors get none. Keep the natural-floor Herblore chain test green end
   to end. See `memory-bank/design-thread-queue.md` sections 3.25 and 4.14.
3. **The 384-diary-task clause.** See
   `memory-bank/achievement-diary-item-grants-design.md` lines 49 and 287. The
   design calls for 32 tiers of 12 curated tasks each.
4. **Depth work.** Every family in the pre-EOC catalog is at breadth one. Read
   the closing note in `memory-bank/breadth-next-tranche.md`, then take the
   registered placeholders and the recorded data-depth debt in
   `memory-bank/activeContext.md` in order of player visibility.

## 6. What mechanical completion means

An item is not done until all ten of these work:

1. Entry gates
2. Gameplay states
3. Policies, both the casual surface and the advanced editor
4. Failure modes, which include death and abandonment
5. Rewards
6. Persistence, with a schema migration and a repair path
7. Undo, both review undo and direct-action undo
8. The user interface
9. Assets, normalized, with recorded provenance
10. Tests in both lanes

The casual surface must stay small. The pack-mode dial derives most settings.
Full control belongs in the advanced editor. Do not add a checkbox for each new
mechanic.

## 7. When to stop the loop

Write `memory-bank/GOAL-BLOCKED.md` and stop only for a real blocker. Name what
is blocked, what you tried, and the single thing that would unblock it.

These count as blockers:

- Quota exhaustion.
- A decision only the owner can make.
- A missing external dependency.

A preference not to do the work is not a blocker. A hard problem is not a
blocker. Delete the file when the blocker clears.

Do not create status-update HTML artifacts while you run unattended. Write
running notes into the memory bank instead.

## 8. Verification

Run both lanes on every item.

```
/opt/homebrew/bin/python3 run_tests.py
```

```
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python run_tests.py
```

The offscreen lane is the gate. The plain lane skips every Qt widget test, so a
green plain lane proves nothing about the user interface.

The test count must not go down between iterations. Record the count in the loop
notes each time.

### Five failures that shipped before

Check for each one before you merge.

1. **An invented mechanic sold as settled.** Skeletal Horror shipped two weekly
   entries that no source supports.
2. **A test that proves nothing.** A test that stubs the reducer under test stays
   green while the feature cannot work.
3. **An inert row.** A reward gated on a state that no player reaches.
4. **A panel that re-derives a rule the logic layer owns.** Every enable and
   visibility decision belongs in the `*_view_pure` function.
5. **An unmarked reconstruction.** The placeholder register test only sees values
   that carry a `PLACEHOLDER(...)` marker.

### The verification limit of this loop

The project rule is that a verify seat must come from a different model family
than the seat that wrote the code. One Sol pass found four defects that three
Claude passes had missed, and lineage caused the difference.

A Codex-only loop cannot satisfy that rule. Therefore:

1. Verify by execution. Drive the real kernel and the real Qt widgets.
2. Mark every merge in the loop notes as `single-lineage verified`.
3. Keep a running list of those merges so an Opus or Kimi seat can sweep them
   later.

### Two project rules for user-interface work

- `.claude/rules/qt-dark-mode-text.md` — `palette(mid)` is a border role. It
  makes text invisible in dark mode.
- `.claude/rules/qt-offscreen-screenshots.md` — call `show()`, then `resize()`,
  then several `processEvents()` passes before any `grab()`. Trust the geometry
  probes over the pixels.

## 9. Open owner questions

Do not decide these yourself. They are already recorded.

1. Two radio buttons under "Widget Position" are dead: "Under XP bar" and "Right
   of bar". The fix is to delete them. The owner has not authorized this.
2. Pass 6 section C items D.1, D.2 and D.3 belong to the design thread.
