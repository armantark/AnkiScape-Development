# Resume here — parked 2026-07-25 on quota

Status: **parked mid-run.** All three model subscriptions passed their daily share,
so both workflows were stopped and their work committed where it stood.

## 1. State of the three trees

| tree | branch | head | state |
| --- | --- | --- | --- |
| `addons21/ankiscape_fork` | `main` | `935f8090` | **clean and green**, 2,735 tests. Safe to play on. |
| `ankiscape_worktrees/ham-pass` | `families/run3` | `711a87c8` | Duel Arena complete; Clan Wars work in progress, unverified |
| `ankiscape_worktrees/batch-a` | `families/batch-a` | `4f823768` | Skeletal Horror work in progress, unverified |

Nothing unfinished is on `main`. Anki loads the live directory, and it holds only
completed, verified work.

## 2. What the two work-in-progress commits are

They exist so the work survives a stray checkout. Neither is a claim that anything
passes; neither was verified.

- `711a87c8` — Clan Wars: data module, logic module, panel, asset fetcher, plus
  runtime and UI wiring. **Scrutinise the red portal first.** A red-portal death
  must leave `combat_grave` and `death_office` both empty. Reusing
  `_combat_apply_pvm_death` unchanged silently reverses the owner's decision,
  because every other part of that path is correct.
- `4f823768` — Skeletal Horror, first family of its batch.

## 3. Not started

Daily Challenges, Treasure Trails (both owner-unblocked and briefed), Tears of
Guthix, Enchanted Key. The briefs are in the two workflow scripts under
`.claude/projects/.../workflows/scripts/`; both support `resumeFromRunId`, so
completed agents replay from cache instead of re-running.

## 4. Where the goal stands

Eight families reached breadth level one today, plus Duel Arena unverified. The
frontier put 33 below breadth one at the start.

Remaining, roughly: two families blocked only on art (Evil Tree, Wicked hood),
which the owner's rule defers; about nineteen not yet started; and Bork, which is
**dependency-blocked rather than source-blocked** — it needs the `Hunt for Surok`
miniquest and the regional Achievement Diary substrate, neither of which exists.

`memory-bank/breadth-next-tranche.md` has the ordering and the reasoning.

## 5. One decision waiting

None open in `design-thread-queue.md`. Gnome Restaurant's presentation fork will
become answerable once its data surface exists, and belongs in the queue then as a
concrete choice rather than an abstract one now.

## 6. Three failures worth carrying forward

Each shipped **and survived a verification pass** before being caught. Every future
brief should name them:

1. An **inert row** — a reward gated on a state no player could reach, in a family
   reported complete.
2. An **invention documented as settled** — a value nothing read, under a name that
   already meant something else in its own audit, written into that audit by the
   same change that added the code.
3. A **test that pinned the defect** — asserting a sourced medal was *absent*,
   which kept it unearnable through a full review.

`tests/test_placeholder_register.py` now guards against the second. The first and
third still depend on the verifier constructing player state through real paths
rather than trusting reports.
