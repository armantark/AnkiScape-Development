# NPC Shop Design Seed

Status: captured 2026-06-20, not implemented.

This is a separate economy surface from the parked fake Grand Exchange. The GE
is a local market simulation for tradable items; NPC shops are source-backed
RuneScape shop inventories with stock, prices, buy/sell behavior, and access
locks.

## Owner Intent

- Add a `Shop` surface inside the AnkiScape menu, comparable to Skills, Quests,
  Bank, Stats, Achievements, and Settings.
- Long-term target: model every source-backed in-game shop from top to bottom,
  not only convenience shops needed by current skills.
- Preserve real shop stock, item prices, and the price/stock curve where prices
  change as the player buys from or sells into the shop.
- Preserve shared inventories for shop families that use the same stock pool,
  such as shared Slayer master reward inventories.
- Support both buying and selling according to the real shop rules.
- Preserve access gates: location/route locks, quest locks, and any shop-specific
  requirements discovered during source audits.

## Source Policy

Use the AnkiScape skill-expansion source policy, but apply it to shop data:

- Prefer local 2011Scape shop definitions and related shop code when available.
- Treat the cloned local Darkan/2012scape codebase as an equal source when the
  2011Scape checkout is incomplete, especially for stock and price behavior:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots`.
- When 2011Scape and Darkan/2012scape heavily conflict, verify against
  historical RuneScape Wiki revisions from November 2012 or earlier before
  choosing the AnkiScape behavior.
- Record provenance per shop group, not only globally, because stock sharing and
  access locks are likely to vary by shop family.

## Backend-First Shape

Start with a pure data/model slice before building a large Qt shop UI.

Core data:

- stable shop id
- display name
- shop group/shared-stock id
- location/region metadata
- quest or ability requirements
- buyable stock rows
- sell policy
- price behavior model
- restock/depletion behavior
- source/provenance notes

Persisted state should be keyed by shared-stock id, not by visible NPC/shop row,
when the real game shares inventory across multiple sellers.

## Open Design Decisions

These are not settled yet and should be grilled before implementation:

- Top-level navigation: should `Shop` be one top-level section, or should
  AnkiScape eventually have a broader `Market` section with `NPC Shops` and
  `Grand Exchange` inside it?
- Location locks: AnkiScape does not currently model player location as a live
  state. Should shop access use coarse quest/route unlocks only at first, or
  should this create a real travel/location system?
- Stock time: should shop stock restock by Anki review ticks, by an AnkiScape
  day model, or only when a shop interaction happens?
- Price curves: should v1 preserve the exact source formula immediately, or
  source-record the exact formula while starting with a conservative equivalent
  for the first audited shops?
- Sell behavior: should v1 allow selling all source-tradeable items to shops, or
  only items explicitly accepted by each audited shop?
- Scope cut: should the first implementation prove the system on Hunter/Fishing
  supply shops, or should it begin with a broad shop registry import even if many
  rows are initially inaccessible/unneeded?

## Current Relationship To Hunter

`Buy Hunter supplies` is a temporary one-shot Utility/Activities bridge. It uses
source-backed shop stock for a starter/restock bundle, but it is not the final
shop system. When NPC shops exist, Hunter tools and jars should come from real
shops where possible, and the temporary bridge should be kept, removed, or
rebalanced deliberately.
