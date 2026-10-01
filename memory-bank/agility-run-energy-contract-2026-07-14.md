# Agility run-energy model — design contract (2026-07-14)

Status: **design locked, parity fork resolved, harvest complete.** This is the durable
record of an owner grill that ran across one session. Numbers marked "invented" are
deliberate AnkiScape abstractions, labelled as such per the project rule ("never invent a
value" means never pass an invention off as period-authentic — it does not forbid a
clearly-labelled game-design abstraction, of which AnkiScape already ships several: one
review = one action, the 240-review day).

**2026-07-15 completion note:** `agility-skill-contract-2026-07-15.md` is the
governing implementation contract. The trip/weight harvest supersedes this
document's earlier per-skill-weight shorthand: use actual target load where
known, a labeled representative load otherwise, and never let weight create a
benefit on a stationary method. The complete Agility course/activity boundary
also supersedes the earlier four-course shipping shorthand below.

**2026-07-15 parity resolution (Sol, xhigh; `source-audits/run-energy-parity-2026-07-15.md`).**
The run-energy model is **drain-based** — Agility reduces run-energy drain (endurance),
not recovery only. Governing evidence is Jagex's 9 June 2009 "Run energy upgrade," which
states Agility "increases the distance you can run per run energy point," larger at levels
50–99 ([oldid 4264036](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036)).
Darkan's recovery-only model (no Agility term in drain, `Entity.java:786`) is therefore
**wrong for the freeze**, not a competing reading; game-main's Model A family is correct.
There was **no run-energy rework between 2011 and 2012-11-20** (only 2009), so revision
proximity does not favour Darkan. Run = 2 tiles/tick and walk = 1 are wiki-sourced at high
confidence ([Game tick oldid 6117417](https://runescape.wiki/w/Game_tick?oldid=6117417)).

**But the exact constants are `source_blocked` / `emulator_reconstruction`.** The period
wiki gives observations, never an equation, and game-main's `(0.7 − 0.002·L)/0.92^…` form
was itself set by a **2023** emulator commit reading the 2009 update, not a period source.
So the *shape* is sourced (Agility helps drain, weight matters, negative weight clamps,
run = 2×) and the *magnitude* is a bounded AnkiScape abstraction — exactly the owner's
original framing.

## The problem this solves

Agility in RuneScape pays off spatially: run energy (walk less) and shortcuts. AnkiScape
has no map, no movement, no run-energy concept. Sol's three-round review concluded Agility
already has a dense unlock graph (multi-pickpocket tiers, leaping-fish gates, the Herblore
Habitat patch, quests) so it is worth training — but it had no *throughput* identity. The
owner wanted a run-energy analog. This contract is that analog.

## The mechanic

AnkiScape already charges a discrete, tunable "bank run": when the 28-slot carried pack
fills (gathering) or cannot supply a recipe (processing), a review tick is spent banking
instead of acting (`inventory_pure.py:470` `carried_bank_run_gate_pure`, sole skilling
caller `runtime_actions.py:613`; combat has its own two-review gate at
`d613f891:logic_pure.py:3779`). That spent review **is** the walk to the bank.

**Agility gives a level-scaled chance/degree of reducing that bank-run cost.** Higher
Agility = you ran the trip instead of walking it. Sourced XP/hour rates are never touched.

### Hard implementation rule (from Sol's regression pass)

> Agility waives the review *cost*. It must never skip the bank *transaction*.

On a successful Agility roll the code still repacks, refills, materialises urns
(`runtime_actions.py:516`), deposits, and resets churn exactly as today — it just does not
charge a review for it. Flipping `act=True` without repacking makes processing act on an
empty pack (`runtime_actions.py:618` only repacks in the `not act` branch), silently drops
an urn charge, and immediately re-triggers churn. Combat must run its full
restock/altar/deposit transaction (`logic_pure/logic_pure_combat_supplies.py:679`) or it proceeds with no supplies
and loops. Roll only when a cost unit is actually due, or RNG streams (Fishing/Hunter/
gem/nest/Thieving/combat) drift.

## Trip cost is derived, not flat (owner decision)

The current flat `SKILLING_BANK_RUN_REVIEWS = 1` (one review per 28 actions, a made-up
3.6% overhead) is wrong in both directions: ~0 for Fletching (you stand on the bank) and
huge for Runecrafting (the walk is the whole skill). **Replace it with a per-skill trip
cost derived from the already-sourced XP/hour:** `reviews_per_action = R/actions_per_hour −
1` where `R = 1000` (`cadence_kernel.py:10`). Fractional costs resolve through the kernel's
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

The `@99` column is a **throughput** target derived as `run-speed ceiling × walk fraction`
(see Magnitude): the ~+11% Agility run-speed gain applies only to the walking portion of a
trip, so a walk-dominated skill gets nearly the full ceiling and a stationary one gets ~0.
This makes the tiers fall out of one anchored number instead of four hand-set ones. Weight
(per-skill model, below) adds a little more on heavy-gathering trips.

| Handler | Tier | Throughput @99 | Why |
|---|---|---|---|
| Runecrafting | strong | ~+11% | The bank-to-altar run IS the method (walk fraction ≈ 1), so it gets essentially the full run-speed ceiling. Trip so large that +11% ≈ 32→~29 walking reviews — RC still feels Agility least in *relative* terms, which is faithful (RC's real speed lever was method, not Agility) |
| Prayer | strong | ~+11% | Gilded altar / Ectofuntus are genuine journeys (walk fraction ≈ 1). (Owner's earlier "50% trip cut" is **superseded** — 50% of a strong trip overshoots the anchored ceiling ~5×) |
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

## Magnitude (labeled bounded abstraction — owner decision 2026-07-15)

The run-energy *magnitude* is **not sourceable** and ships as a deliberate, labeled
AnkiScape abstraction (owner-approved 2026-07-15). Two independent facts fix this:

- The exact drain constants are `source_blocked` / `emulator_reconstruction` (see the
  parity resolution above): the period wiki has observations, not an equation.
- The RC recon (`source-audits/runecrafting-recon-2026-07-14.md`) found no period Abyss
  Nature XP/hour anywhere, so the throughput slope has no citation either.

**The abstraction is bracketed by two real bounds, not free:**

- **Lower/anchor bound — the emulator reconstruction.** game-main's Model A, evaluated as a
  smoothed steady-state (`speed = (2+k)/(1+k)`, `k = drain/recovery`), gives a **~+10.85%
  run-speed gain from Agility 1→99 at 0 kg** (weight-robust: ~+9.6% at 56 kg). This is our
  best physical estimate of the run-speed ceiling. It is emulator-derived, labeled as such,
  **not** a period citation, and explicitly a smoothed approximation (the real per-tick
  behavior has a depletion penalty, so realized speed depends on toggle strategy).
- **Upper bound — route data.** Same level, same 43 essence, two Nature routes gave
  **5,800 vs 11,600 XP/hour**, a 2× spread from route/walk choice alone. Run energy is one
  ingredient of a route, so the Agility effect must stay a fraction of 2×. ~+11% clears this.

**Owner decisions (reconciled 2026-07-15):**

- **Anchor the run-speed ceiling at ~+11%** (the reconstruction figure), replacing the
  earlier hand-set +15%. Throughput per skill = `~11% × walk_fraction`, which is what makes
  the tier table (strong ~+11%, weak ~+7%, marginal ~+3%, none 0) fall out of one anchored
  number. The trip reduction that achieves this is derived per skill.
- **Floor = source.** Level-1 Agility runs at exactly the sourced XP/hour; Agility is pure
  upside up to the tier target. No baseline nerf. (The derived trip cost, unified with the
  kernel, reproduces the sourced rate at the floor rather than undercutting it.)

Curve shape (Sol's form): `throughput_gain(L) = target_tier · (L−1)/98`, applied only when
a bank cost is actually due, back-solved to a trip reduction. Bags still help (they raise
N; effects are sub-additive).

## Weight model (2026-07-15 correction: model actual target load)

Weight is modeled, not flattened. It is a second, smaller run-energy lever layered on the
Agility ceiling, and it gives the weight-reduction reward gear (the Agile set, Boots of
Lightness, capes) a real function on gathering trips. The later harvest in
`source-audits/agility-carried-weight-inputs-2026-07-15.md` governs: calculate
the actual carried/equipped target load where possible rather than persisting
one nominal scalar per skill.

Sourced facts (parity report):

- **Drain rises with positive carried weight; effective weight below 0 kg clamps to 0**
  (`max(weight, 0)`), **medium confidence** — the closest Weight page says negative = 0 kg,
  but the Energy page contradicts itself. game-main matches the better-supported reading, so
  we adopt the clamp. Net-negative weight is therefore inert: reduction gear only helps down
  to cancelling your carried load.
- **Agile set = −22 kg** (top 14936 −12, legs 14938 −10), **wiki-sourced**
  ([Weight oldid 6512729](https://runescape.wiki/w/Weight?oldid=6512729)). The earlier
  "Agile sign bug" was a misread — the +12/+10 values live only on duplicate IDs
  14937/14939 in Darkan's JSON; the primary items are correctly negative. No porting trap.
- **Boots of Lightness ≈ −4.5 kg** (Temple of Ikov reward); spotted/spottier capes
  ≈ −2.3 / −4.5 kg. RC pouches are **1.0 kg each** (a 4-pouch RC runner carries ≥4 kg;
  essence is 0 kg), so RC is light but not weightless.
- Graceful (the later restore-% set) is OSRS, introduced **2013-12-05** — post-cutoff,
  correctly absent. Agile is weight-reduction only, no restore bonus.

Magnitude of the weight lever (Model A, Agility 50): fully-loaded → unloaded (+56 → 0 kg) =
**+7.75%**; +25 → 0 = **+3.5%**; capped at net-zero. Realistically the Agile −22 kg on a
full 56 kg log load (→ 34 kg) is **~+2.8%**, and stacking Boots + a cape (~−9 more, → 25 kg)
is **~+4%**. So weight is a single-digit-% gathering bonus, biggest on heavy-load skills
(WC full logs, Mining ore) and near-zero on light ones (RC, Prayer). Per-skill nominal
carried weight to be pinned from `items.yml` / caches during the harvest; the caches decode
but do not carry a client-side weight field, so weight values come from item configs and the
period Weight page, not the client cache.

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

1. **Completed 2026-07-15:** `source-audits/agility-trip-cost-inputs-2026-07-15.md`
   resolves the elemental-ring conflict and closes target-specific RC/Crafting/
   Smithing inputs; Prayer's pure travel component remains explicitly
   `source_blocked`.
2. Wire the derived trip cost into `carried_bank_run_gate_pure` / the cadence kernel,
   replacing flat `SKILLING_BANK_RUN_REVIEWS`.
3. Implement the Agility waiver as an atomic cost-waiver path (never a gate bypass).
4. Make Agility a trainable surface and ship the complete atomic boundary in
   `agility-skill-contract-2026-07-15.md`, including all courses, activities,
   cross-skill hooks, shortcuts, rewards, UI, assets, and verification.

## Provenance
- Sol rounds 1–3 (design): `/tmp/sol-agility-round{1,2,3}.md`
- Sol bank-run critique + skill audit: `/tmp/sol-agility-bankrun.md`
- **Run-energy parity resolution (drain vs recovery, weight clamp, formulas, movement):
  `memory-bank/source-audits/run-energy-parity-2026-07-15.md`** — the load-bearing citations
  are [Run energy upgrade oldid 4264036](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036)
  (2009 rework, Agility→endurance), [Weight oldid 6512729](https://runescape.wiki/w/Weight?oldid=6512729)
  (Agile −12/−10, negative=0), [Game tick oldid 6117417](https://runescape.wiki/w/Game_tick?oldid=6117417)
  (2 tiles/tick).
- RC recon: `memory-bank/source-audits/runecrafting-recon-2026-07-14.md`
- Fail-rate audit: `memory-bank/source-audits/agility-fail-rates-2026-07-13.md`
