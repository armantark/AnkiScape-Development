---
name: design-progress-report
description: Builds the AnkiScape design progress report, an HTML page showing which owner-grilled designs and approved contracts are built, partly built, blocked or not started, with evidence per design. Use when the owner asks how much of the grilled designs is built, or for a big-picture progress update.
targets:
  - '*'
---
# Design progress report

One page answers "how much of what I settled is in the game": a row per owner decision, each with a status and cited evidence, charted by status, by family and by landing week, plus a searchable, filterable table. The 2026-09-23 page (157 designs) is the reference build.

## Sources

A source records an owner decision: a grill, a ruling, a relitigation, a supersession or an owner-approved contract. All live in `memory-bank/`:

- `design-thread-queue.md`: resolved rulings (open decisions there are not rows until settled).
- `*-contract-*.md`, `*-design*.md`, `*-grill*.md`, `*-decisions-*.md`, `*-relitigation-*.md`, `*-supersession-*.md`, and dated decision records such as `jev-fit-decision-2026-09-23.md`.
- `handoffs/design-to-impl-rulings-*.md` and `handoffs/*grill*.md`.
- Any other dated record whose opening says the owner settled or superseded something; `simulation-time-boundary-2026-07-16.md`, `achievement-diaries-2026-07-26.md` and `capes-and-music-log-2026-07-27.md` were sources on 2026-09-23.

A file whose opening says it is superseded, a design seed (`*-seed*.md`) or an implementation note (`design-gaps-*implementation*.md`) is evidence at most; the superseding file carries the decision. List files added since the last report with `git log --diff-filter=A --name-only --format= --since=<last report date> -- memory-bank/`.

## Statuses

Every row cites evidence: a commit on main, or a Memory Bank file and line (`memory-bank/<file>.md:<line>`). No evidence means `unverified`, never a guess. `build.py` refuses any other status without evidence.

| Status | Page label | Meaning |
| --- | --- | --- |
| `implemented` | Built | The behaviour is live on main. |
| `partial` | Partly built | Some is live; `remaining` names the rest in plain words. |
| `blocked` | Blocked | Nothing, or the remaining core, can move until something outside the work arrives. Set `blocker`. |
| `deferred` | Deferred depth | Settled, base live or accepted, remaining data depth queued behind higher priorities. |
| `not_started` | Not started | Settled, unblocked, no implementation found. |
| `rejected` | Ruled out | The grill ruled it out; counted, needs no work. |
| `unverified` | Unverified | Evidence missing or contradictory; `remaining` says why. |

Blocker kinds: `source` (period data missing), `owner` (needs an owner decision), `dependency` (waits for another system), `integration` (fails a fixed gate or has no clean boundary). A live design whose remainder is owner-excluded UI or source-blocked values is `partial`. A design live except for the programme-wide native reviewer pass is `implemented`. A process rule is `implemented` when tooling or docs encode it and it is followed; otherwise judge it like any design.

## Families

Exactly one of: Skills; Activities & minigames; Combat & bosses; Economy & shops; Quests & diaries; Interface & help; Core systems; Tooling & process. Core systems covers the review clock, time, simulation budget, inventory and carry, save and undo.

## Row schema

One JSON object per line:

```json
{"id": "<short-kebab-id>", "name": "<plain gameplay name, under 70 characters>", "date": "<YYYY-MM-DD settled>", "family": "<family>", "source": "memory-bank/<file>.md § <section>", "status": "<status>", "blocker": "<blocker kind or null>", "remaining": "<one plain sentence, empty when implemented>", "evidence": "<commit hashes on main and/or memory-bank/<file>.md:<line>>", "landed": "<YYYY-MM-DD of the landing commit on main, or null>", "summary": "<one plain sentence on what the design does for the player>"}
```

Text carries no ellipses; the page shows every string in full.

## Steps

1. **Split.** Assign every source file to exactly one of at most five classification agents, by source group. A large ledger (`design-thread-queue.md`, `gap-grill-decisions-2026-07-10.md`) gets an agent to itself; the rest group by family, with the `handoffs/` rulings and the newest decision records together. The 2026-09-23 split gave 20, 28, 24, 51 and 51 rows. Done when the union of the groups equals the source list.
2. **Classify.** Dispatch the agents in parallel with [classifier-brief.md](classifier-brief.md), its `{repo}`, `{skill}`, `{sources}` and `{out}` filled per group, each writing `rows-<group>.jsonl` to a scratch folder outside the repo, such as `Anki2/ankiscape_worktrees/.orchestrator/design-progress-<date>/`. Done when every agent reports, every file parses, and every path a report lists as Unlisted is either classified or ruled out as a source.
3. **Dedup and supersede.** Read the rows across groups and write `rows-final.jsonl`:
   - The same design found in two groups keeps one row.
   - A later ruling that replaces an earlier one keeps only the later row (the Grand Exchange slot-count supersession replaced the six-offer-slot row).
   - A grill whose many sub-rules would skew family counts collapses to one row per decision group, with the merged evidence and the sub-rule names in the summary (the Jev grill's guard rules became one Built row, its candidate uses one Ruled out row).

   Done when no two rows describe the same decision and `build.py` accepts the file.
4. **Build.** Run from the checkout whose main the page names:

   ```bash
   python3 <skill-dir>/scripts/build.py <scratch>/rows-final.jsonl --out <page>.html --repo <checkout>
   ```

   It rejects unknown statuses or families, duplicate ids and uncited rows, and prints the count per status. Name the page `design-progress-<YYYY-MM-DD>.html`.
5. **Publish.** Follow the `status-artifact` skill for placement, pre-flight, opening in Zen and Postplan hosting. Page and chart changes go through `status-artifact` for layout and `dataviz` for chart form and colour; keep both light and dark mode, event listeners rather than inline handlers, no network requests, and full text without truncation.
