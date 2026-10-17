# Pass 16 owner notes: ask-matt route

The owner picked the main flow on 2026-10-15 ("#1, but you can use Codex").
Steps are copied from the ask-matt skill; every step not run keeps a one-line
skip reason.

- [x] 1. **`grill-me`** sharpens the idea by interview and records what it learns in `GLOSSARY.md` and ADRs. Start here whenever you are working in a repository.
  Scope: only the open design points (quest XP lamps, Wicked hood menu); the other notes are defects or carry recorded rulings.
  Done 2026-10-15: one round of four questions; GLOSSARY.md gained "XP lamp" and "XP drop". No ADR: no decision met all three ADR tests.
- [x] 2. **Branch: can you settle every question in conversation?** A question that only running code answers is **ungrillable**: `grill-me` marks it and runs **`prototype`** for it.
  Skip `prototype`: the one ungrillable question, quest filter spacing, is settled by before and after captures in its ticket, and the owner delegated it to Opus 5.5.
- [x] 3. **Branch: is this a multi-session build?** Yes → **`to-spec`** turns the thread into `memory-bank/specs/<slug>/spec.md`, then **`to-tickets`** cuts it into tracer-bullet tickets beside it, each with its blockers and a status line.
  `to-spec` done 2026-10-15: `spec.md`.
  `to-tickets` done 2026-10-15: 12 tickets in `tickets/`, approved by the owner as proposed. They sit in `tickets/` because `ready.py` reads only that folder.
  - [x] **`implement-spec`** for the whole spec in one run: it reads the tickets as a task graph, runs implementer agents in worktrees on every ready ticket in parallel, lands each on main, and ends with one `review`.
    Repo adaptation: worktrees come from `tools/worktree_guard.py lease`, never raw `treehouse`. Each ticket lands by fast-forward on the integration branch `goal/pass16-integration`, not on main, because main moves only through `tools/promotion_gate.py` and one full gate costs about 25 minutes of the shared MacBook mirror. After the final `review`, one gate with `--remote-lanes` lands the integration branch on main.
  - [x] Each ticket is claimed, built at the seams and layers the spec names, and reviewed with **`review`**. The last ticket moves the spec directory to `specs/done/`.
    Landed on main at `4a9d0931` on 2026-10-16 after one gate failure on a stale test pin. 11 tickets done, ticket 04 built and waiting for the owner's look in Anki, so the spec stays open. Three review rounds (standards on GPT-6 Astra; spec on Opus 5.5, then Kimi K3 with the UI taste review) and two fix rounds.
  - Skip: **`implement`** per ticket in fresh windows; `implement-spec` covers the same tickets in one run.
  - Skip: **`arena`**; no ticket is a one-shot artifact whose shape is in doubt.
- [x] 4. **`retro`** closes the loop. After a build, it suggests changes to the agent's environment, not the code.
  Done 2026-10-16: five candidates, each with a recommended answer, wait for the owner on the results page `memory-bank/status-updates/pass16-results-2026-10-16.html`; the retro edits nothing itself.
  Owner answers 2026-10-16, all as proposed: pool reclaim, text-fit rows, UI save-read test and hook cache are built; the owner audited the to-tickets line, applied in fleet 390d065.
- Skip: **`split-to-prs`** and **`babysit`**; this solo repo lands on local main through the promotion gate, with no remote PRs.
