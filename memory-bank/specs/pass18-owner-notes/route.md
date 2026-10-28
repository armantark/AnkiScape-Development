# Pass 18 owner notes: ask-matt route

The owner ran `/ask-matt` on 2026-10-27 22:58 ("Alright boyo, I got Pass 18.
... Same rules apply, get it on main on the Mac Studio when you're done"),
started `/grill-me` at 23:14, and confirmed the settled design at 23:55
("Lgtm") after the summary that ended "If you say yes, I run to-spec,
to-tickets and implement-spec as one unattended chain." The Sol loops run
during this pass (AnkiScape since before the pass; Darkan restarted at the
owner's word at 23:48). Steps are copied from the ask-matt skill; every step
not run keeps a one-line skip reason.

- [x] 1. **`grill-me`** sharpens the idea by interview and records what it learns in `GLOSSARY.md` and ADRs. Start here whenever you are working in a repository.
  Done 2026-10-27: three rounds, Q1 to Q12, answers in `grill-decisions.md`; GLOSSARY.md gained "Supply step" and the queue rules in "Action queue". No ADR: no decision met all three ADR tests. Facts came from three read-only Opus fact-finders and two GPT-6.1 Sol harvests (`code-facts.md`, `memory-bank/source-audits/pass18-woad-dyes-goblin-diplomacy-2026-10-27.md`, `/Users/armantarkhanian/Code/ankiscape-pass18/facts/E-quest-supply-steps.md`), and two native looks in real Anki by GPT-6.1 Terra, the second seeded with a copy of the owner's save.
- [x] 2. **Branch: can you settle every question in conversation?** A question that only running code answers is **ungrillable**: `grill-me` marks it and runs **`prototype`** for it.
  Skip `prototype`: the only ungrillable question, how the add highlight feels, is settled by the native looks inside ticket 03; the owner ruled out the hill-climb loop (Q10).
- [x] 3. **Branch: is this a multi-session build?** Yes → **`to-spec`** turns the thread into `memory-bank/specs/<slug>/spec.md`, then **`to-tickets`** cuts it into tracer-bullet tickets beside it, each with its blockers and a status line.
  `to-spec` done 2026-10-28: `spec.md`. Skip its seam check with the owner: the owner asked for the chain unattended, and the seams are the Pass 17 layers plus the native looks he asked for.
  `to-tickets` done 2026-10-28: 10 tickets in `tickets/`. Skip its quiz: the owner delegated approval with "Lgtm" to a summary that named the unattended chain.
  Skip the plan artifact: every decision is settled and the owner is not watching; the results artifact compares the outcome with `spec.md`.
  - [ ] **`implement-spec`** for the whole spec in one run: it reads the tickets as a task graph, runs implementer agents in worktrees on every ready ticket in parallel, lands each on main, and ends with one `review`.
    Repo adaptation (as Pass 17): worktrees come from `tools/worktree_guard.py add`, never raw `treehouse`, because the running Sol loop holds the pooled leases. Each ticket lands by fast-forward on `goal/pass18-integration`, not on main. The full plain and Qt lanes run through `tools/run_remote_tests.py` on its test mirror after landings, queued behind the loop's own runs. Native looks run through `/Users/armantarkhanian/Code/ankiscape-pass18/native/run_native.sh` with GPT-6.1 Terra, each after the loop's native lane frees the GUI. After the final `review`, the Kimi taste review and the final native check, one `tools/promotion_gate.py run <path> --remote-lanes` and `land` put the branch on main; the Mac Studio's `mbp-main-pull` job then fast-forwards its main.
  - [ ] Each ticket is claimed, built at the seams and layers the spec names, and reviewed with **`review`**. The last ticket moves the spec directory to `specs/done/`.
  - Skip: **`implement`** per ticket in fresh windows; `implement-spec` covers the same tickets in one run.
  - Skip: **`arena`**; no ticket's shape is open after the grill.
- [ ] 4. **`retro`** closes the loop. After a build, it suggests changes to the agent's environment, not the code.
- [ ] After landing: one harvest brief per other quest in the quest audit, into the AnkiScape loop's `harvest-briefs` folder (Q12).
- Skip: **`split-to-prs`** and **`babysit`**; this solo repo lands on local main through the promotion gate, with no remote PRs.
- Skip: **`wayfinder`**; the nine notes fit one grilling session.
