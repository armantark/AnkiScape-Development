# Pass 17 owner notes: ask-matt route

The owner ran `/ask-matt` on 2026-10-26 21:45 ("Can you work on pass 17 here
outside of the loop, in a worktree, then get it on main on the Mac Studio?"),
started `/grill-me` at 21:51, and at 23:08 asked for the rest of the chain in one
run: "You say to-spec but I would rather just call that chain of skills all at
once so I don't have to watch". Steps are copied from the ask-matt skill; every
step not run keeps a one-line skip reason. The loops were paused by the owner at
21:48 ("I have just paused the loops btw").

- [x] 1. **`grill-me`** sharpens the idea by interview and records what it learns in `GLOSSARY.md` and ADRs. Start here whenever you are working in a repository.
  Done 2026-10-26: four rounds, Q1 to Q13, answers in `grill-decisions.md`; GLOSSARY.md gained "Action queue" and "Review HUD". No ADR: no decision met all three ADR tests. Facts came from four read-only Opus fact-finders (`code-facts.md`) and two source harvests (`memory-bank/source-audits/pass17-*.md`). The owner pointed to the game design compendium on the Mac Studio (`~/Desktop/Metafolder/Programming/Game Dev/game-design-compendium`); its pages "Upgrades that replace the core loop", "Wrong lessons", "Realism versus clear navigation" and "Video game literacy" shaped Q10 and Q11.
- [x] 2. **Branch: can you settle every question in conversation?** A question that only running code answers is **ungrillable**: `grill-me` marks it and runs **`prototype`** for it.
  Skip `prototype`: the ungrillable layouts (combat setup panel, queue panel, Resume button) go through the hill-climb loop the owner chose in Q11, inside the build.
- [x] 3. **Branch: is this a multi-session build?** Yes → **`to-spec`** turns the thread into `memory-bank/specs/<slug>/spec.md`, then **`to-tickets`** cuts it into tracer-bullet tickets beside it, each with its blockers and a status line.
  `to-spec` done 2026-10-26: `spec.md`. Skip its seam check with the owner: the owner asked for the chain unattended, and the seams follow the Pass 16 layers he kept.
  `to-tickets` done 2026-10-26: 11 tickets in `tickets/`. Skip its quiz: the owner delegated approval ("I would rather just call that chain of skills all at once so I don't have to watch"); the split is the recommended one.
  Skip the plan artifact: every decision is settled and the owner asked not to watch; the results artifact compares the outcome with `spec.md`.
  - [x] **`implement-spec`** for the whole spec in one run: it reads the tickets as a task graph, runs implementer agents in worktrees on every ready ticket in parallel, lands each on main, and ends with one `review`.
    Repo adaptation (as Pass 16): worktrees come from `tools/worktree_guard.py`, never raw `treehouse`; the pool is full while the paused loops hold all 16 leases, so tickets use `worktree_guard.py add` outside the pool. Each ticket lands by fast-forward on `goal/pass17-integration`, not on main. After the final `review` and the Codex native check (Q13), one `tools/promotion_gate.py run <path> --remote-lanes` and `land` put the branch on main. The Mac Studio's `mbp-main-pull` job then fast-forwards its main.
  - [x] Each ticket is claimed, built at the seams and layers the spec names, and reviewed with **`review`**. The last ticket moves the spec directory to `specs/done/`.
    Done 2026-10-27: 13 tickets (11 planned, 12 and 13 added for gaps the landed tickets found). Hill-climb loops: ticket 02 one round, 04 three rounds, 07 four rounds, each judged by a fresh Haiku 5.5 naive probe and a Kimi K3.1 taste vote (judges.md per round in the evidence folder). Review: GPT-6 Astra (standards, xhigh) and Opus 5.5 (spec), then fix groups D, C, Q; Kimi K3.1 re-review found three new defects (fix group Q2); Kimi final check approved. Native check on GPT-6.1 Terra at xhigh (owner, Q13): run 1 found three defects only native Anki shows (fix group N); run 2 confirmed the layout and then hit a known Qt accessibility crash under computer use; run 3 checks the rest. Gate run 1 failed (two quest-test contexts, a clipped label, a papercut edit), gate run 2 at 631a5e4b1 passed both lanes.
  - Skip: **`implement`** per ticket in fresh windows; `implement-spec` covers the same tickets in one run.
  - Skip: **`arena`**; the shape-sensitive screens use the Q11 hill-climb loop instead.
- [x] 4. **`retro`** closes the loop. After a build, it suggests changes to the agent's environment, not the code.
  Done 2026-10-27: its candidates wait for the owner on the Pass 17 results page; the retro edits nothing itself.
- Skip: **`split-to-prs`** and **`babysit`**; this solo repo lands on local main through the promotion gate, with no remote PRs.
- Skip: **`wayfinder`**; the 11 notes fit one grilling session.
