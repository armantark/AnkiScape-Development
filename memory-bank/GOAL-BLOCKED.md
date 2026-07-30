# Goal blocked — one diary clause and one parked reshape, 2026-07-30

**Status.** Every family in the pre-EOC catalog is at breadth one: the
overnight run merged Dungeoneering phase C, Conquest, the miniquest ledger,
Bork, and the Tarn corrections, with the sixteen-activity cadence class fix
and the disproven Slayer off-task lead alongside. Two blockers remain.

## Blocker 0 — the 3.25 guardian-drop reshape is parked on quota

**What is blocked.** One settled, owner-answered change: moving the
Dungeoneering starter Herblore funding from the placeholder coin cache to
placeholder guardian-room coin drops (design answers 4.14 item 2 / 3.25).
The cache variant ships and works; this is mechanism fidelity, not a
missing mechanic.

**What I tried.** Two codex CLI runs; both were killed externally with a
clean tree. All three subscriptions are now at or over their day lines, and
the task would finish before any next block lands.

**The single thing that would unblock it.** The next codex block (~8h). The
exact brief and resume command are in
`~/.local/state/quota-guard/parked.md`.

## Blocker 1 — D1: 384 regional tasks

**What is blocked.** 326 tasks ship. The contract asks for 384.

**What I tried.** The source harvest first took the catalog from 171 to 304. The
`any_of` and `derived_value` pass raised it to 310. The approved expansion then
added five condition kinds over existing save state and four contract-limited
telemetry tasks, reaching 326 without replacing a shipped task or exceeding a
regional tier's twelve-task budget.

**Why it stops here.** The remaining tasks need state outside the approved narrow
ledger extension: geography, emotes, inventory choreography, unimplemented enemy
or vendor routes, or wider mechanic-specific telemetry. Inventing predicates for
them would ship rows that cannot complete or that no longer describe the source
deed.

**The single thing that would unblock it.** Implement the missing authentic game
routes and their own durable event seams. The owner has answered the product
question about narrow existing-ledger keys; the remaining gap is implementation
breadth, not an unresolved telemetry policy.

---

**Delete this file** when the regional diary catalog reaches its 384-task
contract.
