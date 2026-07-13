# XP/hour provenance ledger — Phase 0

Audit date: 2026-07-13. Cutoff `2012-11-20`, per
`memory-bank/pre-eoc-source-verification-standard.md`.

This is the prerequisite for any cadence work, not documentation written after
it. Sol's phasing puts it at Phase 0 for one reason: **a quoted XP/hour carries
reference conditions, and feeding a rate into a cadence contract without knowing
what is already baked into it double-counts the modifier.** The 2012 F2P Mining
guide quotes iron at 45k/hr *with urns*; base is nearer 37.5k. Contract on 45k,
then grant urn XP at runtime, and the player earns 54k.

Measured by `tools/xp_rate_audit.py`, which grades the **shipped** probability
functions rather than a reimplementation of them.

## The defect, stated precisely

Every gathering and processing skill routes its period-authentic roll through an
invented adapter at `logic_pure.py:388`:

```python
p_review = min(0.95, 0.20 + 0.72 * sqrt(p_source))
```

Its distortion is **proportional to how rare the action is**. Near `p = 1` the
square root is nearly the identity, so the adapter is harmless. As `p → 0` it
inflates without bound: a 7% rock becomes 39%, a 6.3% fish becomes 38%.

In RuneScape, a rare action is the signature of a **money** method, not a
training method — that is *why* Jagex made it rare. So the adapter systematically
promotes exactly the content the period game made unattractive to train.

This is not malicious. It exists so a 7% action doesn't feel miserable in Anki,
and `mining_data.py:442` shows the same instinct — `ratio = 8 / ticks_between_rolls`
folds the pickaxe's roll *cadence* into its *probability*. That is a duration
model in disguise. The honest version is a tick budget, and it needs no invented
constant.

## Results

| Skill | Ordering | Raw p range | Why |
|---|---|---|---|
| **Woodcutting** | **INVERTED** | 9%–100% | Magic logs (9% raw) inflate to 41.6% |
| **Fishing** | **INVERTED** | 6.3%–100% | Rocktail (6.3%) inflates to 38% |
| Mining | consistent* | 7%–100% | *only 2 rows have sourced rates; runite is unquotable |
| Hunter | consistent | 78%–100% | High raw p — the adapter barely bites |
| Cooking | consistent | 91%–100% | Outcome roll (burn), and near-certain anyway |

```
Woodcutting  AnkiScape:  ivy > magic > yew > maple > willow > oak > tree
             reality:    ivy > willow > maple > oak > yew > magic > tree

Fishing      AnkiScape:  rocktail > monkfish > shark > leaping_sturgeon > trout
             reality:    rocktail > trout > monkfish > leaping_sturgeon > shark
```

Magic logs are Woodcutting's **2nd-best** training here and the period record's
**2nd-worst** (17–30k/hr). Sharks are Fishing's **3rd-best** here and the period
record's **worst** — the guide's own words are *"only 20k experience per hour"*.
Yew and magic are the money trees; sharks are the money fish. The adapter made
them the meta.

**Implied R spans 188 to 1,474.** Every method should agree on this number; the
spread is the imbalance. Combat sits at 120 (50 ticks/review), the extreme
outlier in the other direction.

### Correction: there are TWO independent defects, not one

An earlier draft of this ledger claimed the undistorted skills "cluster near
R ≈ 1,000–1,475" and offered that as unplanned corroboration for `R = 1000`.
**That was cherry-picked and it is withdrawn.** Writing the regression test forced
the issue: Hunter implies **R = 281–833**, nowhere near the band.

Hunter's *ordering* is fine — its rolls sit at 78–100%, where the adapter barely
bites, and it passes the inversion test. But it still pays **2–4× too much per
review**, because trap catches carry **dead time**: you lay a trap and wait.
AnkiScape charges one review per catch and ignores the wait entirely.

That is precisely the Thieving stall defect — *already live, in a shipped skill.*

So the two defects are independent and a skill can fail either one alone:

| Defect | Breaks | Cause | Victims |
|---|---|---|---|
| **Invented adapter** | *ordering* | `0.20 + 0.72·√p` inflates rare actions | Woodcutting, Fishing (Mining directionally) |
| **Unmodelled dead time** | *rate* | one review per action, regardless of the wait | Hunter (traps), Thieving stalls (respawn), Combat (30s burst) |

A skill can pass the ordering test and still be badly wrong on rate. Hunter is the
proof, and it is the reason the ordering test alone is not a sufficient gate.

What survives of the corroboration claim, stated honestly: among skills with
*neither* defect, Mining/iron implies 1,035, Cooking 1,359–1,410 and Firemaking
1,474. That is consistent with `R = 1000` and inconsistent with combat's 120, but
it is three data points, not a cluster, and it must not be sold as more.

## Cooking and Firemaking are a different bug

They call the same adapter, but their roll decides an **outcome** — does the food
burn, does the log light — not a **rate**. The adapter still distorts them: it
makes the player burn less than the period record. That is a real defect with a
real fix, but it is not the cadence defect and must not be repaired by the same
mechanism. Graded separately; excluded from the R spread.

## Overflow ledger (methods exceeding 1,000 actions/hour)

These cannot fit one action per review at `R = 1000` and must declare an explicit
`cap_one_action`. Validation must fail if a new one appears without it.

| Method | Actions/hr | Note |
|---|---|---|
| Cooking: shark / monkfish / lobster / tuna | 1,250–1,267 | Cooking is fast; the whole skill overflows |
| Firemaking: magic logs | 1,200 | Guide states 1,200 logs/hr outright |
| Mining: iron | 1,071 | Powermining, after stripping urns |
| Woodcutting: oak | 1,000 | Exactly at the line |
| Thieving: vegetable stall | 1,800 | The fastest sourced action in the game |
| Thieving: baker's stall | 1,440 | |

The overflow list was never "two Thieving stalls." It is a standing property of
the fastest content in several skills, and `R` cannot be chosen to eliminate it
without dragging the whole game's pace down by ~1.8×.

## source_blocked — no pre-cutoff rate exists

Recorded, not filled. Absence is a finding.

- **Mining:** copper, tin, coal, mithril, adamantite, **runite**. No guide quotes
  a runite XP/hour *at all* — it appears only as a money method (300–600k coins/hr).
  A runite cadence contract cannot be derived from these pages.
- **Hunter:** grenwalls, pawyas (the page's own `{{cleanup}}` tag flags the gap),
  dragon impling XP/hour (XP/catch known, rate never stated).
- **Cooking:** karambwan (absent from both pinned revisions), rocktail-with-urns
  (the urn table stops at sharks).
- **Fishing:** cavefish XP/hour, lobster XP/hour (only a comparative phrase), and
  an unambiguous tuna/swordfish base rate.

## Flagged ambiguities — recorded, never resolved by averaging

1. **Rocktail (Fishing).** The 48k/hr quote folds urns in and cannot be
   decomposed. Indicative only; must not set a cadence contract.
2. **Magic logs (Firemaking).** The *same revision* states XP/log as both `303.8`
   (body + bonfire table) and `308.8` (header table). Not averaged. `303.8` used;
   the discrepancy stands on the record.
3. **Tuna/swordfish (Fishing).** The 45k/hr figure sits immediately after a
   swordfish-gloves discussion; whether gloves are assumed is unclear.
4. **Black warlock (Hunter).** The guide's 140k/hr is **barehand** catching
   (650 XP/catch, level 95). AnkiScape's `catch_black_warlock` is the butterfly-**net**
   variant at 54 XP. Grading one against the other produced a phantom inversion on
   the first run. Barehand butterfly catching is **not implemented** — a content gap
   for the kanban, not a balance defect. This is the reference-conditions trap in
   its purest form, and it is why this ledger exists.

## Content gaps surfaced incidentally

- Barehand butterfly catching (Hunter 95) — the period game's best Hunter XP at
  140k/hr, and entirely absent from AnkiScape.
