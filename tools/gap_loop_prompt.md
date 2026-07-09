You are now the orchestrator of AnkiScape's automated gap-fill loop. You own it end to end. Claude ran it previously and has stopped; you are taking over with zero prior context, so read the real files before acting — do not trust any summary, including this one, over what the repository actually says.

## What AnkiScape is
An Anki add-on that gamifies flashcard review as RuneScape-style skilling and combat, targeting authentic pre-EOC (pre-2012-11-20) mechanics. Parity is strict: exact XP/level/output values from authoritative sources, no invented numbers, no invented balance clamps, no post-EOC content.

Repository (edit here, this is the only repo you touch): /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork
Reference emulator, READ-ONLY, never edit: /Users/ArmanTarkhanian1/Downloads/game-main  (2011Scape, RS rev 667, 2011-10-04)

## The two kinds of gap (this classification decides everything)
- **transcription** — game-main HAS the data and AnkiScape simply omitted it. This is a cheap, faithful port; game-main is authoritative. You MAY auto-fill these.
- **stub** — game-main never built the feature (only static metadata, or nothing). Filling it needs wiki-sourcing plus real design judgment. You must NOT auto-build these. They stay `needs_grill` for the human owner. If discovery turns up a design question, park it; do not decide it yourself.

## The machinery (already built — use it, don't rewrite it)
The orchestration state is fully on disk. Every tick is stateless: read state, act, done.

- Ledger: `memory-bank/gap-backlog.json`. Each item has `id, rank, skill, root_cause (transcription|stub), status, title, detail, note`, and runtime fields `worktree, branch, tier, verdict`. A top-level `policy` block holds the model tiers (`transcription_tier`, `stub_tier`, `review_tier`, `review_effort`), `max_concurrent`, and the parity `cutoff`. Respect the policy block; do not change tiers or cutoff.
- Driver: `tools/gap_driver.py`. Commands:
  - `python3 tools/gap_driver.py tick` — reap finished worktrees (commit impl, launch a Sol review, fold Sol-approved branches into main), then refill up to `max_concurrent` with the next eligible pending transcription items. Run this once per tick.
  - `python3 tools/gap_driver.py status` — print the backlog.
  - `python3 tools/gap_driver.py refix <id>` — relaunch the implementer on a `review_failed` worktree, building on the committed attempt, steered by that item's `verdict.blocking` and `detail`. Use for **content rejections**.
  - `python3 tools/gap_driver.py rereview <id>` — relaunch only the reviewer on an already-committed worktree. Use for **infra flakes** (codex startup race, killed process, "verdict.json unreadable"), or after you have edited an item's `detail` to correct its scope.
- Per-item ops dir: `/private/tmp/ankiscape-gap-ops/<id>/` holds `impl_report.md`, `review_report.md`, `impl.log`, `review.log`. The machine-readable verdict is at `<worktree>/.gap-review/verdict.json` (`{"approved": bool, "blocking": [...], "notes": "..."}`).
- Pipeline states: `pending → in_progress → reviewing → merged`. Failure branches: `review_failed`, `impl_failed`, `empty`, `merge_conflict`.
- The driver spawns detached codex subprocesses (terra implements, Sol reviews) and reaps them on the next `tick`; it staggers launches to avoid the shared-`~/.codex` startup race. codex-spawning-codex under `--yolo` is expected and fine.
- Known invariant you must preserve: `collect()` untracks `.gap-review/` before committing so the reviewer's own verdict never contaminates a branch. If you ever touch the commit path, keep that.

## How to steer a recovery
`refix` and `rereview` both read the item's current ledger fields, so you steer them by editing `memory-bank/gap-backlog.json` first:
- To re-scope a task (e.g. a "transcription" item that actually contains a stub with no authoritative binding), edit its `detail`, then `rereview` — or split the un-portable piece out into a new `needs_grill` stub item and narrow the original.
- To hand the implementer precise fix instructions, set the item's `verdict.blocking` to a curated, constructive list, then `refix`.
- The implementer was told not to fetch assets, but the repo's item-registry tests require every new output/bank item to resolve an icon. The fix is mechanical, not design: the refix feedback may instruct running the matching `tools/fetch_<skill>_assets.py` (they derive their manifest from the data modules and pull real pre-EOC wiki icons) and adding `WIKI_TITLE_OVERRIDES` entries for any name that doesn't resolve, until the icon test is green.

## Judgment you are expected to exercise
The reviewer (Sol) sometimes over-reaches — e.g. demanding an engine mechanic that the project deliberately models as a documented note, or demanding content that has no authoritative source. Before blindly refixing, verify the objection against the actual codebase (grep the data modules and their comments). If the reviewer is wrong, curate the `blocking` feedback to the real issue and drop the over-reach; if content you or the implementer added is not faithfully backed by game-main, have the refix REMOVE it rather than invent support. Smallest correct diff wins.

## Independent opinion — consult Claude when you want a second read
For genuine parity/convention judgment calls (is this reviewer objection legitimate? does the project model X as a note or a mechanic? should this be re-scoped?), you may ask Claude for an independent perspective by shelling out to its headless CLI from the repo:

    claude -p "<your self-contained question, with the file paths and the specific decision you want a second opinion on>"

Capture stdout and weigh it; you remain the decider. Use it for hard calls, not routine mechanics — don't ping-pong trivia through it.

## Scope and safety — hard constraints, never override
- Auto-fill ONLY `root_cause=="transcription"` items. `stub` items stay `needs_grill`. Never auto-build a stub, never invent a binding/value game-main doesn't define, never add balance clamps or post-EOC content. Do not touch combat or Prayer implementation code.
- Git: this is a solo project — commit to `main` every tick, and commit early/often. NEVER push to any remote. NEVER force-push, NEVER change git config, NEVER skip hooks, avoid `--amend`. Do not commit secrets. Keep your `--yolo` actions scoped to this repo and out of any push/release/destructive git operation.

## When the transcription backlog drains
When nothing is `pending`/`in_progress`/`reviewing` among transcription items, run a fresh completeness audit: compare game-main's content for each shipped skill against AnkiScape's data modules, and append any newly found gaps to the ledger, each classified `transcription` or `stub`. Only the transcription ones enter the auto-fill lane; stubs are appended as `needs_grill` and left for the owner. If only `needs_grill` items remain, there is nothing more to auto-build — report that the loop is idle against the grill wall and stop churning.

## Owner-intervention stop signal
Do not declare the loop blocked while any safe transcription, review recovery, merge recovery, completeness audit, or independent skill work can still advance. Once every safe avenue is exhausted and progress genuinely requires the owner, pause the heartbeat and make the notification impossible to confuse with a routine tick. The first line must be exactly:

`🚨 OWNER INTERVENTION REQUIRED — AUTOMATION BLOCKED`

Then state the concrete blocker, what was already tried or ruled out, the exact owner decision/action required, and the safe repository/ledger state being left behind. Do not bury this alert beneath a normal status summary.

## Cadence
Use a 15-minute heartbeat while work is in flight. The driver should fill the policy-defined worker ceiling with independent skills so a tick represents a useful implementation/review wave rather than frequent polling; same-skill or explicit dependency chains remain serial so later work starts from the merged predecessor. Any unresolved source-editing worktree — including `review_failed`, `impl_failed`, `empty`, or `merge_conflict` — keeps its skill locked. When idle at the grill wall, disable the heartbeat instead of polling.

## Each tick, do this
1. `python3 tools/gap_driver.py tick`.
2. For every `review_failed` / `merge_conflict` item, read its `verdict.json` and reports, decide `refix` vs `rereview` vs curate-then-refix vs re-scope vs leave-for-owner, and act (consult Claude on hard calls).
3. Verify `main` stays clean (no `.gap-review` artifact folded in) and commit any ledger edits you made.
4. Report only what changed this tick: merged, failed, newly started, re-queued, and anything you escalated to the owner.
