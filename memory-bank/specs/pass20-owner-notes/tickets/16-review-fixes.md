# 16: Review fixes preserve danger stops, recovery time and equipment

**What to build:** The owner's review-fix dispatch: stop live quest combat at danger; repeat the paired deaths gate with danger stops in both arms; spend successful-card ticks on grave travel after debt; recover only eligible time per queue segment; restore quest equipment through normal slot conflicts; remove retired review-duration constants; correct the contradictory queue, cadence and Agility documentation; keep level labels together and shorten the Grand Exchange search hint.

**Status:** built; native target-row and Grand Exchange copy check waits for the orchestrator

- [x] Reproduce all four reported behavioral defects at real handlers before fixing them.
- [x] Stop a non-killing quest danger tick immediately, preserving result and tick accounting.
- [x] Paired deaths gate passes with the shared danger stop active for both arms.
- [x] Again leaves a selected grave walk unchanged; successful answers pay debt first and resume work with the remainder, without travel debt; unclaimed expiry still advances on Again.
- [x] Queue recovery spends only each eligible segment's ticks; Bankstanding and stepped Utility retain their recovery rules.
- [x] Returning a two-handed weapon banks a shield equipped during the swap and conserves the affected items.
- [x] Remove retired constants and imports/re-exports, update contradictory documentation and remove the extra blank line.
- [x] Target level tags use nonbreaking spaces; Grand Exchange search has no ellipsis; light/dark default-size and 560-point PNGs pass text-fit checks.
- [ ] Native look at target labels and Grand Exchange search: orchestrator-owned verification.

Evidence and synthetic capture scripts: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/evidence/16/`. The final report records focused checks, audits and the whole-suite job on the final commit. Scabaras supply work and the known native session-bootstrap failures are outside this ticket.
