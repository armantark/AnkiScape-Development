# Cadence kernel contract

Owner-approved 2026-07-13. Supersedes nothing; it is the first implementation of
the XP/hour invariant recorded on the balance kanban card.

Evidence: `memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`.
Decision: `memory-bank/status-updates/action-time-model-decision-2026-07-13.html`.
Measurement: `tools/xp_rate_audit.py`. Gate: `tests/test_xp_hour_parity.py`.

## 1. The problem, in one line

RuneScape was balanced in XP per **hour**; AnkiScape pays XP per **review**. Every
skill currently invents its own private exchange rate between the two, and nobody
coordinated them. Mining behaves as ~1,000 reviews per game-hour, Combat *declares*
120, Woodcutting's magic logs behave as 188. That disagreement is the bug.

## 2. Owner-settled decisions

1. **`R = 1000`.** One balancing-hour costs 1,000 reviews. It is a **correctness
   constant, not a taste knob** — it is what makes XP/hour ratios come out right.
   Triangulated three independent ways: the sourced 3.6s blackjack cycle; the
   overflow-cap argument; and deterministic artisan actions read straight off the
   period record (gilded altar 913/hr, dragonhide 1,000/hr, High Alchemy 1,200/hr —
   the last stated outright by the 2012 page). `R = 1800` has no support.
2. **Pace is the player's, via the existing `ankiscape_review_action_multiplier`**
   (`__init__.py:136`). All parity claims are defined at multiplier 1. `M > 1`
   executes M complete kernel steps; ratios are preserved. It is a game-speed
   override and is explicitly **not** part of source parity.
3. **The `0.20 + 0.72·√p` adapter is a BUG, not a feature.** It was intended to
   make the no-Grand-Exchange ironman experience less miserable (you must mine your
   own runite for runite gear). But it fixes *acquisition* by inflating *XP*, and
   that is why five skills inverted. The two concerns get decoupled:
   - **XP** rides the authentic roll, at the authentic cadence.
   - **Acquisition** gets item-side levers only — Varrock armour's extra ore (no
     extra XP; already in `mining_data.py` as `varrock_armour_tier`), pickaxe roll
     cadence, mining/smelting urns, the Blast Furnace's halved coal. **Never** by
     inflating XP again.
   - Measured cost of honesty: a full rune set (18 bars = 18 runite + 144 coal)
     goes from ~198 reviews to ~400 at Mining 85. Four days of ordinary reviewing.
     Accepted.
4. **Identity.** AnkiScape is *based on* pre-EOC, not a parity emulator, and that is
   fine — **but "our own identity" defends divergences we chose, not divergences
   that happened to us.** No location layer, review-paced actions and the 240-card
   day are chosen. Runite out-earning iron is an accident. Keep the first, fix the
   second. Deliberate divergences get written down; accidental ones get fixed.
5. **Ship behind a config flag**, `ankiscape_cadence_kernel`, beside the review
   multiplier. **Off = today's behaviour byte-for-byte.** On = the new model. The
   owner A/B tests it in his own save. Storage migration is **additive only** — new
   keys, nothing rewritten — so flipping back leaves nothing broken.
6. **Save compatibility is not a constraint.** The owner is the sole alpha tester of
   his own open-source project and accepts that his save's behaviour changes.

## 3. Felt-change contract (what the owner agreed to feel)

- **Skilling: one review = one discrete action or attempt, unchanged.** You answer a
  card, you swing the pickaxe, you get an ore or you don't. Stalls add "the stall is
  bare", which is the same shape as a failed mining roll and has existed since launch.
- **Rare actions get genuinely rarer.** Runite falls from 54% to ~14%. This is the
  fix, and it is a real felt nerf. Accepted knowingly.
- **Combat feels meaningfully slower per card, and this is unavoidable.** One card
  currently buys 50 ticks (30s); under the kernel it buys ~6 ticks (3.6s), and
  combat XP/card falls ~8×. *Any* design that preserves the current combat feel
  **is** the 8× bug.
- **Combat's reaction cadence does NOT change.** The tactical decision point stays at
  50 ticks — preset, flee, target swap on the same rhythm. Auto-eat and auto-flee run
  inside the tranche. The player is never forced to click more often than today. This
  is the thing the 30-second burst was protecting and it is preserved.

## 4. The kernel

A scheduler between "a card was answered" and "the skill acts". One place answers
*"does this card produce an action, and how much game time did it buy?"* — from
sourced rates, instead of each skill inventing its own answer.

```
successful Anki review
        |
        +-- world/economy clock (240 cards = 1 day)   <- unchanged, separate
        |
        +-- foreground action admission (THE KERNEL)
                |
                +-- passthrough            one attempt per review (today's behaviour)
                +-- rate_limited           deterministic fractional admission
                +-- embedded_probability   legacy: probability already folds in cadence;
                |                          the kernel must NOT gate it again
                +-- combat_ticks           review advances a rational tick budget
```

A cadence step occurs **only** on an eligible *successful* answer, matching the
existing dispatch distinction at `__init__.py:1403`. Failed answers still advance the
world clock but never the foreground cadence.

### 4.1 Deriving a rate — never reconstruct it

```
actions_per_hour   = sourced_XP_per_hour / XP_per_action        # both pinned to 2012
actions_per_review = actions_per_hour / R
```

For a method with an authentic success probability `p`, calibrate against **expected
XP per opportunity**, not per success, or the rate is suppressed twice:

```
expected_xp_per_attempt = p * xp_per_success
attempt_frequency       = sourced_XP_per_hour / expected_xp_per_attempt / R
```

**Never** reconstruct a rate from respawn seconds when the sourced XP/hour exists.
That discards better data. (An earlier proposal to use `min(1, action_seconds /
respawn_seconds)` was rejected for exactly this reason.)

### 4.2 Deterministic residual scheduler — never a lottery

Integer/rational arithmetic only. **Never persist floating-point progress.** A
180-second restock is a refractory period, not a coin flip; a memoryless roll with
the same mean produces droughts and lucky doubles that never existed.

Immutable per profile: `increment_numerator`, `threshold_denominator`,
`cadence_version`, `overflow_policy`.
Persisted per player: `credit`, `opening_ready`, `assigned_reviews`,
`opportunities_emitted`, `cadence_version`.

For frequency `n/d`, one active review does:

```
if opening_ready:            # RuneScape stalls begin stocked
    opening_ready = False
    emit one opportunity
else:
    credit += n
    if credit >= d:
        credit -= d
        emit one opportunity
    else:
        emit no opportunity  # a "cadence_wait", NOT an attempt failure
```

`if`, not `while` — base frequencies cannot exceed 1. Overflowing methods must first
be converted to an explicitly approved capped `1/1` rate (§4.3).

Worked: gem stall at `20.25/1000 = 81/4000`. Each review adds 81; threshold 4,000.
Across every 81 opportunities the scheduler emits 31 intervals of 50 reviews and 50
of 49 — ordering falls out of the residual, no hand-authored pattern.

### 4.3 Overflow ledger

Methods exceeding 1,000 actions/hour cannot fit one action per review and must
declare `cap_one_action`. **Validation fails if a new overflow appears without one.**
If caps proliferate beyond this list, reopen `R` rather than letting caps become the
model.

| Method | Actions/hr |
|---|---|
| Thieving: vegetable stall | 1,800 |
| Thieving: baker's stall | 1,440 |
| Cooking: shark / monkfish / lobster / tuna | 1,250–1,267 |
| Firemaking: magic logs | 1,200 |
| Mining: iron (powermining) | 1,071 |
| Woodcutting: oak | 1,000 |

### 4.4 Switching, locks, and undo

- **Only the active route advances. Inactive routes freeze completely.** Switching
  away preserves `credit` exactly; switching back resumes it. Round-robin switching
  yields a weighted average of route rates, **never their sum**.
- Selection is snapshotted at answer start; a UI change mid-answer applies to the
  next card.
- **Resource lock** = "the stall is bare, but you are free". **Actor lock** = "you are
  still committed to this fight".
- Permanent preconditions (level, quest, tool, inventory space) are checked *before*
  advancing cadence. Expected unavailability (an empty stall) *is* the action and
  does advance it.
- Cadence state, XP, loot, risk consequences and telemetry are **one review
  transaction**. Anki undo restores all of them.

### 4.5 Telemetry

Three distinct outcomes, never conflated: `cadence_wait` (no attempt occurred),
`attempt_failure` (an authentic attempt failed), `success_with_risk`. Cadence waits
must not inflate dry-streak statistics.

## 5. Phase plan (Sol's ordering; combat LAST)

Each phase is independently shippable and leaves the game consistent.

| # | Phase | Size | Notes |
|---|---|---|---|
| 0 | Rate provenance + overflow ledger | M | **DONE** — ledger, audit tool, tests |
| 1 | Dormant kernel + storage schema + config flag | M | Nothing routed through it. No behaviour change. |
| 2 | **Thieving as the greenfield canary** | L | Unshipped ⇒ no save migration, no regression surface |
| 3 | Shadow mode on the adapter skills | S–M | Compute proposed vs current, mutate nothing |
| 4 | Mining migration | L | Remove `ratio × sqrt` |
| 5 | WC, Fishing, Hunter, Cooking, Firemaking | M–L ea. | One per release |
| 6 | Combat engine split | L | Highest risk. Last, not first. |

**Combat is last by design.** Its 8× over-reward is the worst bug in the game, but it
has the most tangled call boundaries, and the kernel must prove itself on Thieving
and live gathering first. Deferring the *migration* is safe; deferring the
*architecture* is not — which is why the kernel cannot wait.

## 6. Do-not-double-apply

The single most dangerous failure mode. A rate contract and a probability gate must
never both apply.

- `rate_limited`: the successful-action rate is authoritative. Do **not** then apply a
  success roll, the square-root adapter, a depletion cooldown, or a banking delay
  already inside the quoted rate.
- `embedded_probability`: today's shipped gathering behaviour. Admit one attempt per
  review; apply **no** kernel gate. This is the legacy mode and it preserves current
  behaviour exactly.
- These are **alternatives, not layers.**
- Every sourced rate declares what is baked into it (`tools/sourced_xp_rates.py`).
  The F2P Mining guide quotes iron at 45k/hr **with urns**; contract on that and grant
  urn XP again and the player earns 54k.
- Bank-run reviews (`runtime_actions.py:490`) must not be charged when the sourced
  rate already includes banking or dropping.

## 7. Verification

- `tests/test_xp_hour_parity.py` carries three `expectedFailure`s. When a migration
  is correct, unittest reports an **unexpected success**, which *fails the suite* and
  forces the marker's removal. The bug cannot be silently left behind.
- A `n/d` contract must admit exactly `n` actions in `d` reviews — assert it.
- With the flag **off**, output and RNG consumption must be **byte-identical** to
  today. Assert this; it is what makes the flag a real escape hatch.
- Full baseline: 1,198 tests green.
