# Pass 20 owner notes: route

The owner invoked `/implement-spec` on 2026-11-04 11:28 with `/to-spec memory-bank/specs/pass20-owner-notes` and `/to-tickets` in its text, after he answered "Ok" to the settled design.

- Grill: done, `grill.md`; `GLOSSARY.md` gained Bank run and Quest wear and a new Action queue entry. No ADR: no decision met all three ADR tests.
- `to-spec`: done, `spec.md`. Skip its seam check: the owner asked for the chain, and the seams are the existing queue, pace and quest layers.
- `to-tickets`: done, 14 tickets from the 8 parts he accepted (parts 1, 2, 5 split at their real blockers). Skip its quiz: he answered it with "Ok" to the split.
- Skip the plan artifact: every decision is settled; the results page compares the outcome with `spec.md`, as Pass 18 did.
- `implement-spec`, repo adaptation as Passes 17 and 18: worktrees come from `tools/worktree_guard.py add`, because `AGENTS.md` forbids direct `treehouse`. Each ticket lands by fast-forward on `goal/pass20-integration`. Main receives the whole branch through `tools/promotion_gate.py`. `land.py` is not used.
- Evidence and reports: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/`.
