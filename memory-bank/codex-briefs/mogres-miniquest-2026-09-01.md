# Slice brief — the Mogre miniquest and the Mogres combat target

Date: 2026-09-01. Author: the orchestration seat. Consumer: one dispatched
implementation agent.

## 0. Read this first

`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md` is binding. Read it
completely before you edit anything. Nothing in this brief overrides it. If
this brief and the contract disagree, stop and report both texts.

## 1. Why this slice exists

Mogre combat is source-closed and has been since 2026-07-18. It cannot run,
because `data/slayer_data.py:270` gates the `mogres` Slayer family on the
completion ID `skippy_and_the_mogres`, and no quest in the catalog carries that
ID. The result is one blocked family and two Slayer masters that no player can
finish.

The live Slayer audit measures `mogres:combat_target` as the sole remaining
blocker for both `mazchna_achtryn` at 26 of 27 and `vannaka` at 34 of 35. This
slice is the highest measured leverage item on the queue.

## 2. Ownership, which is settled

The owner granted the self-sourcing waiver on 2026-08-31
(`memory-bank/design-thread-queue.md` section 4.22 ruling 2). Either thread may
implement the unit. Whoever reaches it first works it, and neither duplicates
the other's source harvesting.

The orchestration seat rang the Darkan thread doorbell at 2026-09-01 13:53 PDT
and got this answer: no claim, and no dossier. They hold no unit row in any of
their twelve ledgers, no frozen contract, and no pinned source. AnkiScape owns
the unit and its harvesting.

Two consequences for you:

1. Do not ring the doorbell again. The claim check is complete.
2. Their Slayer unit is blocked on the same miniquest, so your pins become
   their starting point. Record every source with its exact dated oldid and a
   stable path in your source audit. A pin that another thread cannot follow
   is a defect of this slice.

## 3. The harvest is already done, and you must not repeat it

`memory-bank/source-audits/slayer-mogre-combat-2026-07-18.md` holds the full
pinned record. Read it completely. It contains the cutoff revisions, the Darkan
combat definition, the exact 128-slot drop table, the lure transaction, and the
asset contract. Do not re-harvest a subject it already pins. Harvest only what
it names as missing.

`memory-bank/codex-briefs/darkan-quest-agent-handoff-2026-07-18.md` states the
miniquest chain the audit calls for.

The pinned revisions, which you cite rather than rediscover:

| Subject | oldid | Timestamp |
| --- | ---: | --- |
| `Mogre` | `6493220` | `2012-10-29T17:57:37Z` |
| `Mogre (lore activity)` | `6070158` | `2012-08-10T03:44:02Z` |
| `Skippy` | `6274860` | `2012-09-21T07:00:52Z` |
| `Fishing explosive` | `6153110` | `2012-08-27T17:08:17Z` |
| `Super fishing explosive` | `6333518` | `2012-10-02T12:50:19Z` |

The cutoff is `2012-11-20T00:00:00Z`. The evidence order in contract section 4
still applies to anything the audit leaves open: Darkan first, then the rev-727
cache, then game-main, then the other on-disk caches, then the wiki as
corroboration.

## 4. What you deliver

Both halves, in one slice. The miniquest alone unblocks nothing measurable, and
the combat target alone creates a permanently locked row.

### 4.1 The miniquest

Add the period Mogre miniquest as quest-owned one-time state with the exact
completion ID `skippy_and_the_mogres`. The chain is short and has no combat:

1. Cooking 20 is required.
2. One Bucket of water sobers Skippy.
3. One Nettle tea is made and given.
4. One Hangover cure is made from Chocolate dust, a Bucket of milk and Snape
   grass, and is given.
5. Completion grants the ability to lure and kill Mogres at Slayer 32.

The cutoff reward list carries no enemy, no ordinary XP reward, and no quest
point. Do not add any of the three. Miniquests award no quest points, which
`Miniquests` oldid `6020341` states outright and which the two existing
miniquest rows already follow.

Follow the two existing miniquest rows rather than inventing a shape:
`HUNT_FOR_SUROK` and `LAIR_OF_TARN_RAZORLOR` in `data/quest_data.py`. Both set
`miniquest=True`, `point_reward=0` and `release_order=9999`. Read
`data/quest_data.py:10532-10538` for the comment that explains why hand-written
miniquest rows join the same ledger, storage and unlock engine.

Reuse, do not reimplement: `data/quest_data.py:6510-6518` already mixes a
Hangover cure from exactly Chocolate dust, a Bucket of milk and Snape grass
with a Pestle and mortar, for Plague City stage 14. Decide from the sources
whether the two cures are the same item or two quest-local items, and record
the reading you chose with its evidence.

The stage actions must be real. A generated `Complete <Quest> stage <N>
objective` sentinel is a defect, not a deliverable.

### 4.2 The combat target and its lure

`memory-bank/source-audits/slayer-mogre-combat-2026-07-18.md` section
"Asset and runtime contract" states the action exactly: verify the miniquest,
Slayer 32, and one Fishing explosive; consume exactly one explosive; then start
one ordinary persistent Combat encounter. A blocked start consumes nothing.
Only one Mogre exists at a time.

Use Darkan's exact 128-slot table for the ordinary roll. Do not invent weights
for the wiki's qualitative rows. Big bones stay a separate guaranteed row.
`Mogre bone` stays quest-context loot and never becomes an ordinary drop.

Validate the `common_seeds` expansion against the live seed registry.

### 4.3 The items and assets this pulls in

The audit names Mudskipper hat and Flippers as needing canonical item rows and
pre-cutoff icons. Neither string appears in `data/` today. Every other direct
output already has a canonical identity, and cache item `6664`, the Fishing
explosive, is already in the period Slayer shops at 60 coins.

Register every item you add. An unregistered granted or dropped item leaves a
permanent iconless, valueless, unsellable Bank row, which this project has
shipped five times and now counts as a known defect class.

**Gate.** If an asset has no pre-cutoff revision you can pin, stop at that
point and report it. Do not invent an icon, and do not ship an item row whose
icon you could not source. A gate you stop at is a success state.

The Super fishing explosive stays out of scope. It is a Herblore and quest
acquisition dependency, and Rubium is not live. Record it, do not build it.

## 5. Prohibitions that apply to this workspace

Forward every one of these to any child agent you spawn.

- Do not delete any worktree. The safe root holds dozens of merged one-shot
  worktrees and their removal awaits the owner's word. This is an owner gate.
- Do not change an existing user interface without explicit owner approval. A
  new surface that belongs to this work is allowed, and it needs a
  frontend-taste review before promotion. Say in your report whether any user
  interface changed.
- Do not commit to `main`. Only the orchestration seat merges to `main`.
- Do not push to any remote. Do not change git config.
- Do not weaken a test, an audit, or a pinned baseline so your work can pass.
  Fix the code, or record the blocker.
- Do not ask another agent session to rule on a conflict. The orchestration
  seat that dispatched you is your only escalation route.
- Do not register an unmarked reconstruction. A recovered period value that
  stays unrecovered goes in the placeholder register with a `PLACEHOLDER(...)`
  marker.

## 6. Your worktree

Branch `goal/skippy-mogres-2026-09-01` already exists and holds zero commits of
its own. It is an ancestor of `main`. Its worktree is clean at
`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/skippy-mogres-2026-09-01`.

1. Run `python3 tools/worktree_guard.py audit` from the canonical checkout.
2. Change to that worktree.
3. Run `git merge --ff-only main` to bring the branch to `3831b12b`.
4. Do all work there, and commit there.
5. Run the guard audit again at the end.

Do not create a second worktree for this slice. Do not call `treehouse`
directly.

## 7. Verification

**Promotion gate.** The orchestration seat re-runs both lanes on the merged
tree. Run the plain lane only, and say in your report that you did so:

```
/opt/homebrew/bin/python3 run_tests.py
```

Run the cheap neighbour check for every shared file you touch, as contract
section 6 requires, plus your own focused tests.

Also run, and report the exact output of:

```
python3 tools/audit_docs.py
python3 tools/audit_test_quality.py
python3 tools/audit_item_reachability.py
python3 tools/worktree_guard.py audit
git diff --check
```

Prove the behavior by driving the real kernel, not by importing the module. The
five shipped failure modes in contract section 5 all reached a merged family,
and four of them survived three review passes.

Measure the reachability numbers before and after your change. The baseline on
`3831b12b` is:

```
1663 actions; 2343 reachable items; 163 orphan inputs; 249 blocked actions
generated stage sentinels: 680 across 133 quests; placeholder register: 181 rows
```

Also measure, before and after, the two Slayer master readiness counts:
`mazchna_achtryn` at 26 of 27, and `vannaka` at 34 of 35.

## 8. Your report

Write a source audit at
`memory-bank/source-audits/mogre-miniquest-and-target-2026-09-01.md`. Update
`memory-bank/activeContext.md` and `memory-bank/progress.md`. Append a
timestamped line to `memory-bank/papercuts.md` for every piece of friction you
hit, in the moment.

Report exact numbers, identifiers, paths and error strings verbatim. Re-measure
every number at the moment you write the report. State plainly what you did not
do and why. Reporting a lane as green when you did not run it is the worst
outcome available to you.
