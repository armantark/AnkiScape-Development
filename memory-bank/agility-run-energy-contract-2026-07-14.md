# Agility run-energy model — design contract (2026-07-14)

Status: **design locked, harvest pending.** This is the durable record of an owner
grill that ran across one session. Numbers marked "invented" are deliberate AnkiScape
abstractions, labelled as such per the project rule ("never invent a value" means never
pass an invention off as period-authentic — it does not forbid a clearly-labelled
game-design abstraction, of which AnkiScape already ships several: one review = one
action, the 240-review day).

## The problem this solves

Agility in RuneScape pays off spatially: run energy (walk less) and shortcuts. AnkiScape
has no map, no movement, no run-energy concept. Sol's three-round review concluded Agility
already has a dense unlock graph (multi-pickpocket tiers, leaping-fish gates, the Herblore
Habitat patch, quests) so it is worth training — but it had no *throughput* identity. The
owner wanted a run-energy analog. This contract is that analog.

## The mechanic

AnkiScape already charges a discrete, tunable "bank run": when the 28-slot carried pack
fills (gathering) or cannot supply a recipe (processing), a review tick is spent banking
instead of acting (`inventory_pure.py:363` `carried_bank_run_gate_pure`, sole skilling
caller `runtime_actions.py:613`; combat has its own two-review gate at
`logic_pure.py:3779`). That spent review **is** the walk to the bank.

**Agility gives a level-scaled chance/degree of reducing that bank-run cost.** Higher
Agility = you ran the trip instead of walking it. Sourced XP/hour rates are never touched.

### Hard implementation rule (from Sol's regression pass)

> Agility waives the review *cost*. It must never skip the bank *transaction*.

On a successful Agility roll the code still repacks, refills, materialises urns
(`runtime_actions.py:516`), deposits, and resets churn exactly as today — it just does not
charge a review for it. Flipping `act=True` without repacking makes processing act on an
empty pack (`runtime_actions.py:618` only repacks in the `not act` branch), silently drops
an urn charge, and immediately re-triggers churn. Combat must run its full
restock/altar/deposit transaction (`logic_pure.py:3687`) or it proceeds with no supplies
and loops. Roll only when a cost unit is actually due, or RNG streams (Fishing/Hunter/
gem/nest/Thieving/combat) drift.

## Trip cost is derived, not flat (owner decision)

The current flat `SKILLING_BANK_RUN_REVIEWS = 1` (one review per 28 actions, a made-up
3.6% overhead) is wrong in both directions: ~0 for Fletching (you stand on the bank) and
huge for Runecrafting (the walk is the whole skill). **Replace it with a per-skill trip
cost derived from the already-sourced XP/hour:** `reviews_per_action = R/actions_per_hour −
1` where `R = 1000` (`cadence_kernel.py:15`). Fractional costs resolve through the kernel's
existing `Fraction` residual scheduler (a 2.5-review trip alternates 2 and 3; no floats).

This also fixes a latent double-count: the sourced XP/hour already contains the guide
author's banking time, and the dormant cadence kernel will pace to that rate. The bank run
must *be* the kernel's dead time, not a second parallel one. (Kernel is dormant today so
this has not bitten yet.)

Where no sourced rate exists yet, the trip cost is `source_blocked` and the skill parks —
consistent with the rest of the project.

## Walk-vs-stand tier table (owner-ratified, per-skill, optimal-route assumption)

Owner ruling: assume the optimal period route including free teleports — one verdict per
skill, ~13 flags, no per-target checkbox hell. The verdict reflects what the trip actually
was in 2012.

| Handler | Tier | Reduction @99 | Why |
|---|---|---|---|
| Runecrafting | strong | (see cap) | The bank-to-altar run IS the method; Abyss vs foot is the whole story |
| Prayer | strong, **capped 50%** | 50% | Gilded altar / Ectofuntus are genuine journeys; owner: 99 ≠ free |
| Woodcutting | weak | ~+10–15% band | Walk to bank, only when keep mode is on |
| Mining | weak | " | Walk to bank (Living Rock's on-site pulley would be `none`, but per-skill) |
| Fishing | weak | " | Walk to bank |
| Hunter | weak | " | Roaming for supplies/deposits; traps themselves cluster |
| Smithing | weak | " | Back-and-forth to furnace/anvil |
| Crafting | weak | " | Method-dependent; resolved to weak under per-skill ruling |
| Cooking | marginal | small | Basically at the bank |
| Firemaking | marginal | small | Basically at the bank |
| Fletching | none | 0 | You stand on the bank chest |
| Herblore | none | 0 | You stand on the bank chest |
| Combat | weak, **restock unaffected** | ~+10–15% band | Mostly short walks; the supply refill + altar restore still cost their reviews |

## Magnitude (owner decision + empirical bound)

The run-energy *magnitude* is confirmed **un-sourceable**: the RC recon
(`source-audits/runecrafting-recon-2026-07-14.md`) found no period Abyss Nature XP/hour
anywhere (exhaustive scan back to 2010). So the slope is invented — but **bounded by real
data**: same level, same 43 essence, two different Nature routes gave **5,800 vs 11,600
XP/hour**, a 2× spread from route/walk choice alone. Run energy is only one ingredient of a
good route, so the Agility effect must be a fraction of 2×.

**Owner decision: at 99 Agility a walk-heavy skill beats its sourced rate by ~+10–15%**,
treating the sourced rate as a mid-level fixed point (not a ceiling, not the full 2×). RC
99 ≈ 13k against its 11,600 anchor. Prayer is capped harder at 50% cost reduction.

Curve shape (Sol's form): `reduction(L) = c_tier · (L−1)/98`, rolled/applied only when a
bank cost is actually due. Bags still help (they raise N; effects are sub-additive), which
is why the curve stays well below 100%.

## Runecrafting sourcing (recon done)

RC is **not** blocked for a base rate. Shippable anchor: **Nature Edgeville → fairy ring →
glory-return, 11,600 XP/hour at level 50, 43 essence/trip**, internally consistent
(oldid 6530445). ZMI/Ourania gives a level-banded ladder to ~55k at 99; Runespan (released
2012-04-30, in scope) covers the top. RC's instant whole-pack conversion is faithful
(`RunecraftAction.kt`), so N=1 per action is correct — the cost lives entirely in the trip.
At the anchor that trip is ~33 reviews per conversion, making RC the extreme demonstration
of this whole model.

`source_blocked` for RC: the Abyss-vs-foot delta (no period rate), Law and Death standard
altars (no XP/hour quote), and the elemental template's 1.125-vs-10% Explorer's-ring
conflict.

## Open work before implementation

1. **Full trip-cost harvest** (candidate for codex-workflows fan-out): base XP/hour for
   Runecrafting (resolve the elemental ring conflict; pin the 7 oldids the recon lists),
   Crafting, Smithing, Prayer — the strong/weak skills that currently have no sourced rate.
   Cooking/Firemaking/WC/Mining/Fishing/Hunter/Thieving already have rates.
2. Wire the derived trip cost into `carried_bank_run_gate_pure` / the cadence kernel,
   replacing flat `SKILLING_BANK_RUN_REVIEWS`.
3. Implement the Agility waiver as an atomic cost-waiver path (never a gate bypass).
4. Make Agility a trainable surface (fixes the quest-validation short-circuit at
   `logic_pure.py:5436` for free) — ship atomically with the four barehand butterflies
   (75/80/85/90 Agility), Brimhaven as flagship, and the four source-closed courses.

## Provenance
- Sol rounds 1–3 (design): `/tmp/sol-agility-round{1,2,3}.md`
- Sol bank-run critique + skill audit: `/tmp/sol-agility-bankrun.md`
- RC recon: `memory-bank/source-audits/runecrafting-recon-2026-07-14.md`
- Fail-rate audit: `memory-bank/source-audits/agility-fail-rates-2026-07-13.md`
