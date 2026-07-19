# Grand Exchange market engine

Date: `2026-07-19`

Status: **implemented settled contract; balance constants are labeled
emulator-reconstruction / AnkiScape tuning, not period facts.**

## Authority

- `memory-bank/fake-grand-exchange-design.md:90-137` settles the hidden
  true-price model, stochastic partial fills, player-favourable execution,
  lazy deterministic advancement, and the daily volume-weighted guide tracker.
- `memory-bank/fake-grand-exchange-design.md:189-198` settles review-undo as an
  atomic market rollback followed by deterministic replay.
- `memory-bank/ge-relitigation-2026-07-19.md:28-43` settles the player-impact
  cap, minimum/maximum fill nudges, simulated-hour decay, and liquidity unit.
- `memory-bank/ge-relitigation-2026-07-19.md:48-100` settles shocks as the
  hidden opportunity generator and the naturalized answered-card
  day/week/item texture.
- `memory-bank/source-audits/coin-economy-audit-2026-07-06.md:72-87` pins
  Low/High Alchemy to 40%/60% of the cache value and records High Alchemy as
  the GE's soft valuation pressure.
- `memory-bank/simulation-computation-budget-contract-2026-07-17.md:15-42`
  requires bounded reducers, no wall clock, closed-form skipped intervals,
  compact consequential state, and atomic undo.

There is no new owner fork in this slice. The older base contract's exact
formula constants are balance-time tuning; the newer amendment supplies the
impact constants and the shared computation contract bounds the remaining
naturalism coefficients.

## Emulator-reconstruction inputs

The Darkan bots repository is an implementation lead, not a historical source:

- `GEMarket.kt:97-112` supplies the logistic fill-knee, probability jitter,
  liquidity floor, partial-fill fraction, aggressiveness gain, and lumpy-fill
  shape.
- `GEMarket.kt:114-126` supplies the 5%-40% hidden-event magnitude envelope
  and bounded true-price floor/cap.
- `GEMarket.kt:231-305` demonstrates generosity-relative stochastic fills,
  buy-limit clamping, and directional fill impact.
- `FakePlayerWorld.kt:238-242` and `:9445-9448` supply the owner-adopted
  ±1,500 bps impact cap, 25-300 bps nudge, 30 bps/hour decay, and 50,000 GP
  traded-value liquidity unit.

AnkiScape deliberately replaces every wall-clock input from those leads with
the settled answered-card market clock.

## Implemented reducer

`grand_exchange_logic.py` now owns:

- deterministic per-market seeds and persisted RNG cursor;
- exact cache-derived Low/High Alchemy values plus bounded aggregate upward
  pressure below High Alchemy value; this is deliberately not a hard floor;
- formula-derived liquidity from price, item category, required level, source
  role, the 0.75x-1.25x answered-card day envelope, weekend depth, per-day
  jitter, and per-item jitter;
- closed-form mean reversion, impact decay, skipped-interval fill probability,
  and smooth sine-envelope shocks;
- partial buy/sell fills, price improvement, escrow conservation, four-hour
  buy-limit windows, compact daily trade aggregates, and ±5% daily guide
  movement;
- a hard ±15% player-impact cap with 25-300 bps per-fill movement and
  30 bps per ten-card market-hour decay; and
- work bounded by the eight player order slots. No hidden population, full
  catalog walk, replayed tick loop, background worker, or wall-clock read
  exists.

`grand_exchange_data.py` exposes the item category, required level, and derived
source role required by the formula without changing GE eligibility.

`__init__.py` advances the GE after the shared shop clock on every answered
card, including Again. The pre-answer transaction snapshot already captures
all changed GE keys plus the market RNG cursor, so Anki answer undo restores a
fill, escrow, buy-limit usage, guide/trade state, and tick atomically; answering
again replays the same deterministic outcome.

## Verification

- Pure market coverage exercises escrow conservation, partial fills, price
  improvement, directional impact, buy-limit clamping/reset, live guide use,
  day-boundary trade windows, deterministic skipped intervals, and prevention
  of pre-creation catch-up.
- Review integration coverage exercises dispatch order plus
  answer -> fill -> undo -> identical re-answer state.
- Focused GE/data/shop/storage/migration/dispatch run: `115` tests passed.
- Adjacent integration/cadence run: `105` tests passed.
- Full non-Qt discovery: `1,725` tests passed with `216` declared Qt skips.
- Test-quality audit: `1,725` tests across `75` files, `0` hard issues.
- Documentation audit: `388` Markdown and `360` HTML files passed.
- Worktree guard and `git diff --check`: clean.

Read-only Codex Workflows run
`51f1c6f8-fb8c-48ab-a86d-bb4b7efecb8c` used the repaired app-bundled
`gpt-5.6-sol` high path. The first leaf stayed alive for its full explicit
600-second timeout but never emitted `thread.started`: session ID, tokens,
tool calls, stdout, and stderr all remained empty before exit `-15`. The second
leaf reproduced the same zero-session startup signature and was caller-canceled
after 26 seconds rather than spending another ten minutes. Neither leaf read,
wrote, or reviewed repository content. Root independently performed the
economic, persistence, cadence, and undo checks described above.

The eight-slot Qt surface and Bankstanding selector remain the next settled GE
slice. No creative-direction gap was discovered.
