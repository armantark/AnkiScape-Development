# Fake Grand Exchange Design Checkpoint

## Purpose

The fake Grand Exchange is an optional pressure valve for the AnkiScape economy. It lets normal-mode players buy and sell tradable materials/products without turning the whole game into a forced ironman experience. Gathering, Utility/Activities, Crafting, Fletching, and future production chains should remain meaningful paths; the GE should reduce friction, not replace skilling.

This is a local AnkiScape simulation, not a multiplayer economy and not a full fake-player world.

## Product Decisions

- GE interaction is optional.
- The first implementation is strict local-only.
- The default experience may allow GE access. V1 should include a GE enabled/disabled save/config flag and setting so a self-sufficient/ironman-like playstyle can opt out, but it does not need a full account-mode ceremony yet.
- Only registered AnkiScape items are eligible for the first market. Do not import a giant OSRS item dump before the add-on can use/display those items.
- Add explicit tradability metadata anyway. Ordinary materials/products can default to tradable, while future achievement diary items, special rewards, event items, bound items, or other exceptions can opt out.
- `Coins`/GP should be a normal stackable inventory/bank item.
- The GE belongs in its own top-level main-menu section. Do not add Bank shortcuts like "Sell on GE"; that is not authentic to the real game.
- The UI should mimic the authentic core GE feel: 8 total buy/sell slots, item search over registered tradables, quantity, guide price, -5%, +5%, -20%, +20%, custom price controls, collect, cancel, and offer status.
- Do not include a "buy all you can afford" control in v1.
- Buy-offer item search should include all registered tradable items, not only items the player has previously owned or seen.
- Sell-offer item selection should show only tradable items currently owned in the player's bank/inventory.
- Sell-offer quantity should default to 1, not all owned.
- Buy-offer quantity should also default to 1.
- Placing ordinary offers should be quick, but high total-value offers or offers with extreme unit prices relative to guide price should require explicit confirmation before escrow/order placement.
- Initial confirmation thresholds: total offer value at or above 1,000,000 GP, unit price below 10% of guide price, or unit price above 10x guide price. These thresholds should be configurable.
- User-facing GE settings in v1 should be safety/UX only: GE enabled/disabled if needed, high-value confirmation threshold, and extreme-price confirmation multipliers. Market volatility, liquidity, speed, and shock frequency should remain balance data rather than normal user settings.
- GE cannot be disabled while offers are open or collectible. Require the player to cancel/collect all offers first so escrow never enters a half-disabled state.
- Show guide price only. Do not expose the hidden simulated order book.
- Do not add recipe-aware bulk buying in v1. Players should create manual GE offers like the real game; a missing-material planner can be reconsidered later if chains become too tedious.
- Completed or updated GE offers should not interrupt review with modal dialogs or toast-style popups. Show persistent green corner text in the module, such as "1 or more offers complete", until the player opens/collects from the GE.
- Avoid convenience handholding that is not present in the real game unless it is necessary to protect Anki's review flow.

## Real GE Mechanics To Preserve

Source: OSRS Wiki `Grand Exchange`.

- Players place buy or sell offers with item, quantity, and unit price.
- Buy and sell offers match when buy price is greater than or equal to sell price.
- Partial fills are valid for both buy and sell offers.
- If a buy offer crosses an older cheaper sell offer, the buyer receives a GP refund for the difference.
- If a sell offer crosses an older higher buy offer, the seller receives the higher price.
- When competing orders are otherwise equal, older orders are loosely prioritized.
- Orders persist until filled or manually cancelled.
- Open buy orders reserve GP; open sell orders reserve items.
- Completed or partially completed results remain in the GE offer slot until collected.
- A `Collect all` action should move pending Coins/items into the bank inventory.
- Players can collect completed portions from partially filled offers without cancelling the remaining quantity.
- Players can edit open offers, but changing price or quantity resets queue age/priority. Cancelling refunds only remaining escrow; completed portions remain collectible.
- Offer prices should be integer GP values with sane technical bounds. Warn on extreme prices relative to guide price, but do not hard-block valid custom prices in v1.
- No GE tax in v1.

## Market Clock

AnkiScape uses review progress as the market clock.

- Every answered review card advances GE market time, including failed/low-quality answers.
- Only successful eligible answers advance skill XP/items.
- GE orders do not progress while Anki is closed in v1. Market time is study-clock time, not wall-clock time.
- Bankstanding is a no-XP Utility/Activity that means "do nothing except let GE time pass." It advances the market at the same per-card rate as ordinary studying; it does not boost market speed.
- If the active skill/action fails because required materials are missing or source stock is empty, show one warning and auto-switch to Bankstanding/idle market progress for future cards until the user chooses another action.
- Level locks should warn but should not auto-switch to Bankstanding.
- If GE orders later fill the missing materials, do not auto-resume the old skill/target and do not show a materials-available indicator. The player manually checks their bank/GE and resumes training.

Time scale:

- 10 answered cards = 1 AnkiScape market hour.
- 40 answered cards = OSRS-like 4-hour buy-limit window.
- 240 answered cards = 1 AnkiScape market day.

## Buy Limits

Buy limits should be source-audited before implementation.

- Scrape/source OSRS buy limits for every registered tradable item included in the GE.
- Store the original OSRS buy-limit value as source data.
- Enforce the limit over the AnkiScape 40-action "4-hour" market window.
- Selling has no buy-limit equivalent.

## Hidden Market Model

The first implementation should not simulate fake players or persist a fake order book.

Engine source of truth (decided): true-price + stochastic fill model, not a persisted resting order book.

- Each tradable item has a hidden "true price" that evolves over time. This single number, plus item liquidity, is the source of truth.
- Player offers do not match against stored generated orders. Instead, each market tick computes a fill probability and filled quantity for each open player offer from how aggressive its unit price is relative to the item's hidden true price, scaled by the item's liquidity.
- A lowball buy offer has a low per-tick fill chance and sits a long time; a guide/true-price offer fills at a normal pace; an aggressive overpay fills almost immediately. The same logic mirrors for sell offers below/at/above true price.
- Partial fills fall out naturally: each tick draws a filled quantity (bounded by remaining quantity, liquidity, and buy-limit usage) rather than an all-or-nothing match.
- Price improvement/refunds are derived: execution price is the better of the player's submitted price and the prevailing true price at fill time (buyer pays no more than submitted, can pay less; seller receives no less than submitted, can receive more), matching the OSRS resting-order behavior without storing counterparties.
- Player fills exert price impact on the hidden true price, dampened by liquidity. Common high-volume items barely move; rare/illiquid items move more.

Rationale: the player can never see the order book (guide price only), so a persisted book would add storage, migration, and per-tick cost for realism nobody can observe. All perceivable realism (fill latency by aggressiveness, drift, shocks, partial fills, price impact) is a derived output of the true-price model.

Price-dynamics layer (this is where perceived realism lives):

- Random walk with drift plus mean reversion toward a seed/alchemy-anchored fair value so prices stay alive but do not run away.
- Volatility and reversion strength scale with the item's liquidity profile (low-level raw materials calm, rare/dependency-heavy items jumpy).
- Occasional hidden shocks shift the true price (for example, a simulated "yew log dump" pushes the true price down for a while). Shocks are mechanically real but unannounced.
- Event/shock effects are visible only through fills, guide prices, and price movement, never explicit news messages in v1.

Performance and determinism:

- Each answered card should fully process player-order items every tick. Background true-price drift for non-player items can be advanced lazily (only when an item becomes player-relevant or is sampled) plus a small rotating sample, so we never iterate the entire tradable universe per card.
- Persist market RNG state/seed and the market tick counter so Anki restarts do not reroll fills, shocks, or favorable outcomes. Tests should be able to inject deterministic random draws.

Market profiles should be formula-derived, not hand-authored per item:

- Inputs: item category, required level, base guide price, and source role.
- Low-level raw materials such as common logs/ores should have higher liquidity and lower volatility.
- Processed goods should have medium liquidity.
- High-level, rare, or dependency-heavy items should have lower liquidity and higher volatility.
- Manual overrides should exist for exceptions, but not be required for every item.
- Items that are used by implemented content but do not yet have player source loops should be decided case-by-case. For the current Fletching bridge, feathers and basic metal arrowtips should be GE-tradable with limited supply so arrows are playable before their full source loops exist.
- Player orders should affect recent trade history and market state, but impact is dampened by item liquidity. Common, high-volume items should barely move from ordinary player sales; rare or low-liquidity items can move more.
- GE flipping should be a legitimate money-making side activity. It can be strong if the player uses patient buy/sell prices well, but risk should come from liquidity, capital lockup, order slots, adverse guide-price movement, and stochastic market flow rather than taxes or arbitrary penalties.
- Demand should lightly use the implemented recipe graph: inputs used by current recipes get baseline buy demand, while common skilling outputs get baseline sell supply. This should not become a full fake-crafter/fake-gatherer simulation.

## Guide Price Model

The real OSRS guide-price algorithm is not public. OSRS guide prices are based on recent transaction history and volume; they update periodically and can lag behind real trading prices. AnkiScape should approximate that behavior.

Decision:

- Hidden order matching happens every market tick.
- The visible guide price updates once per AnkiScape market day: every 240 answered cards.
- Each guide-price update moves toward recent volume-weighted average matched trade price.
- Cap each guide-price update at plus or minus 5%.
- Low-volume items can lag more heavily by weighting the previous guide price more strongly.
- The guide price should be used as the default offer price in the GE UI, not as a guaranteed trade price.
- Relationship to the hidden true price: the true price carries the fast dynamics (per-tick drift, volatility, shocks) and is what fills are computed against; the guide price is the slow, ±5%-capped, 240-card tracker of realized matched trades. The guide is allowed to lag the true price (this lag is the natural source of flipping profit), but because it chases realized trades it self-corrects rather than drifting into permanent nonsense. Exact coupling constants are balance-time tuning.

## Initial Price Seeding

Use a hybrid price source.

Preferred order:

1. OSRS guide price or historical price source when the registered item cleanly maps to an OSRS tradable item.
2. Low/high alchemy values where available.
3. Formula fallback from production cost, source effort, required level, and item role.
4. Manual curated override for ambiguous or AnkiScape-specific items.

Alchemy matters:

- Future noncombat Magic should include Low Level Alchemy and High Level Alchemy action families.
- Low/high alchemy should become direct GP sources when Magic is implemented.
- High alchemy value should act as an important valuation anchor or floor-like pressure for item seed prices.
- If the GE price drifts below a sensible alchemy-influenced value, future market behavior should account for players/alchers buying cheap items and converting them to GP.
- Do not hardcode alchemy into the GE as a fake trade. Model it as item valuation data first, then as real Magic gameplay later.
- Source scraping for each registered tradable item should collect guide price seed, buy limit, low alchemy value, high alchemy value, tradability, source URL, and provenance in one audit pass.
- High alchemy is basically a floor-price pressure for many items, but not a universal hard floor: some items are profitably high-alched after accounting for Nature rune cost, and that should be handled deliberately during balance.
- Model high alchemy as emergent soft floor pressure, not a direct GE formula or hard floor. The GE should not compute prices from Nature rune cost. Alchemy values are source data and future gameplay pressure; once alchemy exists, alcher-like demand can emerge from the economy rather than a hardcoded floor rule.
- Even before Magic/alchemy gameplay exists, the fake GE may include background alcher demand as aggregate order flow. This keeps high-alch values economically relevant without requiring the player-facing Magic action family to be built first.

## Economic Philosophy

GP is a convenience currency, not a scarcity gate (decided).

- The market is the counterparty: selling conjures GP, buying destroys it. GP supply is therefore effectively unbounded.
- This is intentional. The core difficulty of AnkiScape is studying (reviewing cards), not hoarding gold.
- The real throttles on "buying your way to endgame" are buy limits (per 40-action window) and the market clock (you only get materials as fast as you study). These already prevent skipping progression in one sitting.
- Therefore v1 needs no artificial GP sinks, taxes, or faucet tightening. Flipping is allowed to be a strong moneymaker; risk comes from liquidity, capital lockup, slots, and adverse price movement, not from GP scarcity.
- Buying materials never grants XP or levels. The GE moves items only; progression still requires eligible answered reviews. This invariant must hold for every future skill.

## GP Sources

Do not grant GP passively for ordinary reviews.

Early/current source:

- Player sells banked tradable items through GE sell orders.

Future sources:

- Combat drops from monsters.
- Thieving rewards.
- Noncombat Magic: Low Level Alchemy and High Level Alchemy.
- Other RuneScape-like money sources discovered during future skill/source audits.

No starter GP is currently required by design. Revisit only if first-run UX feels stuck.

## Undo Semantics

Anki review-undo must roll back the GE market tick, not only personal XP/item awards (decided).

- Reason: if undo left the market advanced, `undo -> re-answer` would net extra ticks per real card and let players farm market time and patient-order fills for free. The market clock must move only with genuine net review progress.
- This is made cheap by two properties:
  1. The market is fully deterministic given persisted RNG state and tick counter. Undo restores the RNG cursor and tick counter; re-answering then replays identical draws (same fills, drift, shocks). Outcomes are reproduced, never re-rolled, so undo+re-answer is a market no-op.
  2. Each tick touches only player-order items plus a small rotating sample, so the per-card rollback is a small delta (touched item true-prices, any fills, escrow/buy-limit/order-status changes), not the entire `ge_market_state`.
- Reuse the existing per-card snapshot system already built for XP/item award rollback; extend it with the GE tick delta.
- Tests must cover: undo then re-answer reproduces identical market state; undo reverses a fill (escrow restored, buy-limit usage restored, order status reverted); RNG cursor/tick counter restore correctly.

## Order Data Shape

Persist enough to resume safely across Anki restarts.

Player data should eventually include:

- `inventory["Coins"]`
- `ge_market_state`
- `ge_player_orders`
- `ge_buy_limit_usage`
- `ge_trade_history` or compact recent-trade windows for guide-price updates and logging
- `current_utility` option for Bankstanding/idle market progress

Order fields should include:

- stable order ID
- side: buy/sell
- item storage key
- original quantity
- remaining quantity
- completed quantity
- submitted unit price
- escrowed Coins/items
- collected Coins/items
- status: open, partial, complete, cancelled
- created market tick
- last updated market tick

## Matching Rules

There is no two-sided order matching against stored counterparties. Each open player offer is resolved against the item's hidden true price per tick.

For each open player offer, per market tick:

1. Advance the item's hidden true price (drift, mean reversion, liquidity-scaled volatility, any active shock).
2. Compute this tick's fill probability from offer aggressiveness vs true price, scaled by item liquidity.
3. If it fills, draw a filled quantity bounded by remaining quantity, liquidity, and remaining buy-limit allowance.
4. Set execution price to the player-favorable side of submitted price vs true price (buyer pays <= submitted, seller receives >= submitted), producing refunds/upside in collected contents.
5. Apply liquidity-dampened price impact to the item's true price from the filled quantity.
6. Record the matched trade (price, quantity, tick) into the recent-trade window for guide-price updates.
7. Preserve unfilled remainders until filled or cancelled; mark status open/partial/complete accordingly.

## Frontend Scope

Backend first:

- Item tradability metadata.
- Coins item.
- Preserve stackable/non-stackable metadata as a future economy/inventory modeling idea, but do not make GE v1 depend on noted items, inventory slots, or stack management. The current AnkiScape bank is quantity-based.
- Buy-limit source audit/scrape for registered tradables.
- Pure GE matching engine.
- Market tick/update helpers.
- Storage defaults/migrations.
- Tests for escrow, partial fills, price improvement, buy limits, guide-price caps, and restart persistence.

Frontend second:

- Top-level GE menu section.
- Eight offer slots.
- Buy/sell flow with item search over registered tradables.
- Quantity/price controls using the guide price as default.
- Offer status, collect, collect all, cancel.
- Bankstanding Utility/Activity entry if not already present.

## Open Questions

- Exact formula constants for liquidity, volatility, aggregate order volume, and shock chance.
- Exact buy-limit scraper source and data format.
- Whether to seed any starter Coins after playtesting.
- How much recent trade history to persist for logging/debugging without bloating Anki config. Do not build an in-game price history chart in v1; RuneScape-style history is external/wiki/API, not in the GE interface.
- Whether alchemy values should be scraped alongside GE guide prices, buy limits, or Magic source audit.
