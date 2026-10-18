# Cadence kernel contract

Owner-approved 2026-07-13; reconciled to the live default-on implementation
2026-07-17. This is the canonical foreground cadence contract. The original
Phase 1/Phase 3 rollout records remain historical evidence, not current runtime
status.

Evidence: `memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`.
Decision: `memory-bank/status-updates/archive/2026-07/action-time-model-decision-2026-07-13.html`.
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
   (`__init__.py:391`). All parity claims are defined at multiplier 1. A
   successful card buys `6 × M` game ticks (owner decision 4, 2026-10-15): Combat
   spends them in one engine call, and every other handler takes one six-tick
   kernel step per call until the card is spent or a boundary stops it; ratios are
   preserved. Quests and Dungeoneering keep one stage or room per card at every
   speed, a deliberate divergence because they already outpace 2012 at `M = 1`
   (owner-accepted assumption, 2026-10-15). The speed is a game-speed override
   and is explicitly **not** part of source parity.
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
5. **Ship with a rollback flag**, `ankiscape_cadence_kernel`, beside the review
   multiplier. The live kernel is now the default. Explicit boolean `false`
   restores the legacy handler and RNG order byte-for-byte; missing, true, or
   malformed values use live cadence. Storage migration is **additive only** —
   new keys, nothing rewritten — so rollback leaves save data intact.
6. **Save compatibility is not a constraint.** The owner is the sole alpha tester of
   his own open-source project and accepts that his save's behaviour changes.

## 3. Felt-change contract (what the owner agreed to feel)

- **Skilling follows the route declaration.** `passthrough` and
  `embedded_probability` buy one attempt per kernel step. `rate_limited` may
  instead produce a visible cadence wait: no attempt, failure, resource use, or
  dry-streak change occurred. Source-blocked routes retain their approved legacy
  action unit until compatible evidence exists.
- **Rare actions get genuinely rarer.** Runite falls from 54% to ~14%. This is the
  fix, and it is a real felt nerf. Accepted knowingly.
- **Source-backed admission is level-flat when the source only gives a reference
  training rate.** The exact cited row applies across the route's unlocked
  levels unless a compatible level curve exists. This is a bounded,
  source-visible abstraction and can make a newly unlocked route more generous
  than its real low-level throughput; do not invent a hidden level scaler.
- **Combat feels meaningfully slower per card, and this is unavoidable.** One card
  currently buys 50 ticks (30s); under the kernel it buys ~6 ticks (3.6s), and
  combat XP/card falls ~8×. *Any* design that preserves the current combat feel
  **is** the 8× bug.
- **Combat advances six immediate game ticks per kernel step.** Encounters,
  attack countdowns, enemy LP, prayers, curses, statuses, special regeneration,
  and RNG phase persist between reviews. The player may change preset, flee, or
  swap target between reviews; there is no hidden 50-tick tactical tranche.
  Kill, death, flee, or bank boundaries end the review without starting a second
  enemy.

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

## 5. Live activation status

The staged rollout is complete. `cadence_live.py` owns runtime declarations and
`cadence_coverage.py` fails closed if an implemented handler or selectable route
has no classification.

| Runtime family | Live classification |
|---|---|
| Combat | `combat_ticks`: `6 × M` immediate ticks with continuous encounter state |
| Thieving | Existing exact canary scheduler; no second admission gate; one attempt per card while a stun still costs a whole card |
| Agility | Approved passthrough; one obstacle stage per card while obstacles have no tick time |
| Source-compatible gathering | `rate_limited` exact residual using the conservative lower endpoint of a sourced range |
| Source-compatible Cooking/Firemaking | `embedded_probability`: one authentic attempt and roll, no second gate |
| Exact deterministic artisan rows | `rate_limited` when the runtime conditions match the cited row |
| Source-incompatible or unsourced routes | Approved passthrough behavior with `source_blocked` evidence status |
| Quests | Finite stage progression; one collapsed stage per card at every speed |
| Utility/Activities | One six-tick step per call; a kill, death, flee, wave, round or finished performance ends the card, and a grouped activity never starts a second run in it |
| Farming | Queued steps take the card's first six-tick steps and the selected action the rest; the growth clock stays on the world clock |

Shadow state remains observational history only and is never promoted into
`cadence_profiles`.

### 5.1 Complete coverage matrix

The 2026-07-19 catalog validates 20 implemented handler families and 2,208
declarations: 2,198 selectable foreground routes plus ten handler-level
exemptions or future-attachment rows. `source_blocked` is an evidence status,
not a disabled action: those 212 routes preserve their approved handler behavior
without pretending an incompatible rate is exact.

| Handler | Routes | Live modes |
|---|---:|---|
| Agility | 18 | 18 passthrough |
| Combat | 131 | 131 combat ticks |
| Construction | 544 | 544 passthrough |
| Cooking | 59 | 3 embedded probability; 56 source blocked |
| Crafting | 231 | 177 passthrough; 2 rate limited; 52 source blocked |
| Dungeoneering | 1 | 1 future attachment |
| Farming | 1 | 1 exemption |
| Firemaking | 13 | 1 embedded probability; 12 source blocked |
| Fishing | 19 | 2 rate limited; 17 source blocked |
| Fletching | 96 | 96 passthrough |
| Herblore | 114 | 114 passthrough |
| Hunter | 59 | 4 rate limited; 55 source blocked |
| Magic | 94 | 92 passthrough; 2 rate limited |
| Mining | 18 | 2 rate limited; 16 source blocked |
| Prayer | 61 | 60 passthrough; 1 rate limited |
| Quest | 194 | 194 exemptions |
| Runecrafting | 61 | 61 passthrough |
| Slayer | 1 | 1 future attachment |
| Smithing | 168 | 168 passthrough |
| Summoning | 146 | 146 passthrough |
| Thieving | 38 | 38 passthrough to the existing exact scheduler |
| Utility / Activities | 130 | 130 exemptions |
| Woodcutting | 11 | 7 rate limited; 4 source blocked |

The exact machine-readable rows live in `cadence_coverage.py`; this table is a
dated human-readable projection, not a second authority.

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

- `tests/test_xp_hour_parity.py` grades the live route declarations. It has no
  expected failures: exact source-ready rates, route ordering, residual emission
  counts, and embedded-probability behavior must pass normally.
- A `n/d` contract must admit exactly `n` actions in `d` reviews — assert it.
- With the flag **off**, output and RNG consumption must be **byte-identical** to
  today. Assert this; it is what makes the flag a real escape hatch.
- Whole-addon route coverage must fail when a handler or selectable target lacks
  a declaration.
- Focused live cadence, kernel, parity, combat, runtime, and Summoning tests must
  pass with no cadence skips or expected failures before closure.

### 7.1 Closure evidence — 2026-07-17

- The focused live cadence/kernel/parity/combat/runtime/Summoning/Thieving slice
  passes 363 methods with no skips or expected failures.
- Full core discovery passes all 1,476 methods: 1,275 ordinary passes and 201
  environment skips.
- Full real offscreen Qt discovery passes all 1,476 methods with no skips.
- Documentation, compilation, diff, worktree safety, and test-quality audits
  pass; the quality audit reports zero hard issues across 71 test files.
- The obsolete skipped shadow-integration class and the three XP-parity
  expected failures were removed after replacement live coverage passed.
- Successful Combat answers never mark an encounter disengaged. Again alone
  marks that boundary, and a following successful answer resumes identical
  combat state and RNG phase without granting the failed answer a combat beat.
