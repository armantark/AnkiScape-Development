# Pass 16 owner notes: ask-matt route

The owner picked the main flow on 2026-10-15 ("#1, but you can use Codex").
Steps are copied from the ask-matt skill; every step not run keeps a one-line
skip reason.

- [x] 1. **`grill-me`** sharpens the idea by interview and records what it learns in `GLOSSARY.md` and ADRs. Start here whenever you are working in a repository.
  Scope: only the open design points (quest XP lamps, Wicked hood menu); the other notes are defects or carry recorded rulings.
  Done 2026-10-15: one round of four questions; GLOSSARY.md gained "XP lamp" and "XP drop". No ADR: no decision met all three ADR tests.
- [x] 2. **Branch: can you settle every question in conversation?** A question that only running code answers is **ungrillable**: `grill-me` marks it and runs **`prototype`** for it.
  Skip `prototype`: the one ungrillable question, quest filter spacing, is settled by before and after captures in its ticket, and the owner delegated it to Opus 5.5.
- [ ] 3. **Branch: is this a multi-session build?** Yes → **`to-spec`** turns the thread into `memory-bank/specs/<slug>/spec.md`, then **`to-tickets`** cuts it into tracer-bullet tickets beside it, each with its blockers and a status line.
  `to-spec` done 2026-10-15: `spec.md`.
  - [ ] **`implement-spec`** for the whole spec in one run: it reads the tickets as a task graph, runs implementer agents in worktrees on every ready ticket in parallel, lands each on main, and ends with one `review`.
    Repo adaptation: worktrees come from `tools/worktree_guard.py lease`, never raw `treehouse`; each landing goes through `tools/promotion_gate.py`.
  - [ ] Each ticket is claimed, built at the seams and layers the spec names, and reviewed with **`review`**. The last ticket moves the spec directory to `specs/done/`.
  - Skip: **`implement`** per ticket in fresh windows; `implement-spec` covers the same tickets in one run.
  - Skip: **`arena`**; no ticket is a one-shot artifact whose shape is in doubt.
- [ ] 4. **`retro`** closes the loop. After a build, it suggests changes to the agent's environment, not the code.
- Skip: **`split-to-prs`** and **`babysit`**; this solo repo lands on local main through the promotion gate, with no remote PRs.
