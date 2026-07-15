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

The `@99` column is a **throughput** target (see Magnitude — the ceiling is the
invariant, tiers scale under it). The per-skill *trip reduction* needed to hit it is
derived, not fixed.

| Handler | Tier | Throughput @99 | Why |
|---|---|---|---|
| Runecrafting | strong | +15% | The bank-to-altar run IS the method; Abyss vs foot is the whole story. Trip so large that +15% ≈ 32→28 walking reviews — RC feels Agility least, which is faithful (RC's real speed lever was method, not Agility) |
| Prayer | strong | +15% | Gilded altar / Ectofuntus are genuine journeys. (Owner's earlier "50% trip cut" is **superseded** by the throughput ceiling — 50% of a strong trip overshoots +15% ~6×) |
| Woodcutting | weak | ~+7% | Walk to bank, only when keep mode is on |
| Mining | weak | ~+7% | Walk to bank (Living Rock's on-site pulley would be `none`, but per-skill) |
| Fishing | weak | ~+7% | Walk to bank |
| Hunter | weak | ~+7% | Roaming for supplies/deposits; traps themselves cluster |
| Smithing | weak | ~+7% | Back-and-forth to furnace/anvil |
| Crafting | weak | ~+7% | Method-dependent; resolved to weak under per-skill ruling |
| Cooking | marginal | ~+3% | Basically at the bank |
| Firemaking | marginal | ~+3% | Basically at the bank |
| Fletching | none | 0 | You stand on the bank chest |
| Herblore | none | 0 | You stand on the bank chest |
| Combat | weak, **restock unaffected** | ~+7% | Mostly short walks; the supply refill + altar restore still cost their reviews |

## Magnitude (owner decision + empirical bound)

The run-energy *magnitude* is confirmed **un-sourceable**: the RC recon
(`source-audits/runecrafting-recon-2026-07-14.md`) found no period Abyss Nature XP/hour
anywhere (exhaustive scan back to 2010). So the slope is invented — but **bounded by real
data**: same level, same 43 essence, two different Nature routes gave **5,800 vs 11,600
XP/hour**, a 2× spread from route/walk choice alone. Run energy is only one ingredient of a
good route, so the Agility effect must be a fraction of 2×.

**Owner decisions (reconciled):**

- **Throughput ceiling is the invariant, not the trip-reduction fraction.** No skill beats
  its sourced rate by more than the tier target at 99: strong +15%, weak ~+7%, marginal
  ~+3%, none 0. The trip reduction that achieves this is *derived per skill* and differs
  wildly — a strong skill with a huge trip (RC) needs only a ~13% trip cut to reach +15%
  throughput; a weak skill with a small trip needs a larger cut for less throughput. This
  supersedes the earlier "Prayer 50% trip cut," which in throughput terms was ~+90% and
  broke the ceiling.
- **Floor = source.** Level-1 Agility runs at exactly the sourced XP/hour; Agility is pure
  upside up to the tier target. No baseline nerf to existing play. (This makes the earlier
  "derived cost is a nerf" concern moot — the derived trip cost, unified with the kernel,
  reproduces the sourced rate at the floor rather than undercutting it.)

Curve shape (Sol's form): `throughput_gain(L) = target_tier · (L−1)/98`, applied only when
a bank cost is actually due, back-solved to a trip reduction. Bags still help (they raise
N; effects are sub-additive).

## Presentation (owner decision: bursty)

The trip cost presents as **discrete travel reviews then a payout burst**, not smoothed XP
per review — faithful to the game (you walk, then convert). This is also the cheaper path:
the bank-run gate already spends reviews with zero XP, so bursty is the existing behavior
extended. RC is the extreme: ~28–32 travel reviews per conversion even at 99 Agility.

**Refinement:** travel reviews show running progress ("running to the altar, 6/32") rather
than being blank, so the stretch reads as movement, not dead air. Same burstiness, no
"nothing happened" confusion. Build this unless the owner prefers truly blank travel ticks.

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
