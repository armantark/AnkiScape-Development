# Grand Exchange relitigation

Date: `2026-07-19`

Status: **owner-settled amendment to `fake-grand-exchange-design.md`; that
document remains the base contract, this record wins where they differ.**

Bases reviewed: the locked 2026-06-24/07-07 design, and the more evolved
fake-player economy in the bots repo
(`darkan-world-server/.../FakePlayerWorld.kt`, the damped
`FakePlayerEconomy` price model and `FakeGrandExchangeDemand`).

## Kept unchanged (re-affirmed on review)

Hidden true-price + stochastic-fill engine (no fake order book); the
answered-card market clock (10/40/240-card hour/limit-window/day); guide
price as the slow ±5% daily tracker whose lag funds flipping; 8 slots, buy
limits, escrow, partial fills, price improvement; deterministic RNG with
undo-tick rollback; lazy per-item advancement; formula-derived liquidity
profiles; alchemy as soft anchor pressure; the ironman toggle; no GE tax
(now recorded as a **period fact** — the 2012 GE had none — not a v1
simplification).

## Amendment 1 (owner-settled): demand-bounded absorption

Replaces "GP effectively unbounded / commons barely move / flipping strong"
on the sell side, which together made the GE an unbounded unsourced coin
faucet:

- Buy side is unchanged: GP-as-convenience stands; friction remains buy
  limits plus the market clock.
- Every fill applies a real **minimum price impact** — no zero-impact
  exemption for commons — scaling with fill size against the item's
  liquidity profile.
- True-price drift from player impact is **hard-capped** with always-on
  decay toward the anchor value.
- Consequence: dumping crashes the price the seller receives, so mass-sell
  income is bounded per window; flipping stays legitimate but its profit
  comes from guide-lag and patience, bounded by the player's own impact.
- Seed constants come from the bots-repo model as labeled
  `emulator_reconstruction` balance-tuning values, not historical claims:
  ±15% drift cap, 25–300 bps per-fill nudge, 30 bps/simulated-hour decay,
  50,000 GP liquidity unit.
- No invented taxes or sinks. Full counterparty-wealth conservation (the
  bots repo's account ledgers) is explicitly rejected as unobservable solo
  cost per the computation-budget contract.

## Amendment 1a (owner requirement, 2026-07-19): flipping stays skillful and emergent

Demand-bounded absorption limits *scale*, never the *existence* of the edge.
The emergent-flip loop is a first-class supported behavior:

1. **Shocks are the opportunity generator.** Unannounced market shocks (the
   "yew log dump") displace the hidden true price and mean-revert over time.
   The player-impact drift cap and decay from Amendment 1 bound only
   **player-caused** impact — market-side shocks may displace prices well
   beyond ±15%, which is exactly where the big emergent opportunities live.
2. **Margin-checking is the skill instrument.** Probing with quantity-1
   aggressive offers reveals the prevailing true price through the
   execution-price-improvement rule, just like real GE margin checks; fill
   latency on patient offers is the second signal. No news feed, no shock
   announcements — discovery through play is the skill.
3. **The payoff loop:** spot a displaced item → accumulate patiently under
   the buy limit → hold through reversion → sell into recovery. Profit is
   bounded by buy limits, capital lockup, slots, the player's own impact,
   and reversion timing — never by taxes or invented penalties.
4. **Tuning acceptance criteria:** a patient, attentive flipper should
   meaningfully out-earn naive selling; a mindless buy-dump loop should not
   out-earn sourced money-makers. Balance passes test against both.

## Amendment 2 (standard-mandated sourcing corrections)

The locked design predates the verification standard and sourced from OSRS
first; the standard's order now applies:

1. **Price seeds:** prefer dated Wayback captures of the official 2012
   Grand Exchange Database (real November-2012 prices) over OSRS guide
   prices; alchemy values second; OSRS last resort with its update history
   checked.
2. **Buy limits:** prefer the period wiki's 2012 buy-limit records over an
   OSRS scrape; OSRS supplies only rows the period record lacks, flagged.
3. **Interface harvest:** pin the period GE interface at a pre-cutoff
   oldid — including whether the in-game/website price graph and trend
   indicators are attested. If attested, they are in scope per the
   full-breadth policy, superseding the earlier "no price history chart"
   clause; if not, the exclusion stands as a period fact.
