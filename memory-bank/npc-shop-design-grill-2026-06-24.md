# NPC Shop Design Grill

Status: active design grill, not implemented.
Opened: 2026-06-24.
Seed: `memory-bank/npc-shop-design-seed.md`.

## Inherited Seed Constraints

- NPC shops are separate from the parked fake Grand Exchange unless the owner
  later chooses to merge the concepts.
- The intended long-term surface is source-backed RuneScape NPC shops, not a
  generic convenience vendor.
- Shop behavior should preserve stock, price curves, buy/sell behavior, shared
  inventories, and access locks where source evidence supports them.
- State that belongs to a shared shop inventory should be persisted by shared
  stock group, not by the individual NPC or visible shop row.
- The temporary `Buy Hunter supplies` Utility/Activities bridge is not the final
  shop system; it must be migrated, removed, or rebalanced deliberately once
  NPC shops exist.

## Decision Log

1. The player-facing economy surface for v1 is a top-level `Shop` tab, not a
   broader `Market` tab.
   - Rationale: this matches the original owner seed, keeps NPC shops separate
     from the parked fake Grand Exchange, and avoids building a generalized
     economy shell before both systems exist.
   - Status: decided 2026-06-24.
2. v1 does not create a live travel/location system for shops.
   - Access should use existing quest and route-precedent locks only when a shop
     location is obviously blocked by a quest, region route, or comparable
     requirement already represented elsewhere in AnkiScape.
   - Shop data should still preserve source location/region metadata so a future
     route or travel model can consume it without re-auditing the shop.
   - Status: decided 2026-06-24.
3. Shop stock, restock, and pricing must model the real game behavior for each
   audited shop family, while staying deterministic and rollback-safe.
   - Persist mutable current stock by `shared_stock_group`, with per-row default
     quantity, current quantity, restock cadence/progress, custom price data, and
     temporary/player-stock flags where source evidence requires them.
   - Buying and selling mutate stock immediately. Restock should advance on
     AnkiScape game/action ticks, not wall-clock time, so review transactions can
     snapshot and undo the exact stock, coin, inventory, and restock-progress
     deltas.
   - Do not hardcode one OSRS-style price curve for every shop. Historical
     RuneScape and OSRS both have stock-sensitive shop-price behavior, but
     post-2007 RuneScape also split many shops into infinite/constant-price main
     stock and variable player stock. Use the strongest available source for the
     specific shop family, then record that formula/provenance with the shop
     group.
   - Support shared stock as a first-class data field. Multiple visible NPC/shop
     entries may point at the same `shared_stock_group` when source evidence says
     they share inventory. Slayer equipment/reward shops are an audit candidate,
     but the implementation should not assume every same-looking shop shares
     stock without source proof.
   - Status: decided 2026-06-24.
4. Shop sell behavior follows source policy, not a universal broad-tradeable
   rule.
   - General stores can accept broad tradeable item sales when the audited source
     defines them as general stores.
   - Specialist shops should accept only stocked items or explicitly accepted
     item classes unless source evidence says they buy broader tradeables.
   - The implementation should preserve source policy distinctions such as
     buy-none, stock-only, tradeables, all-items, buy-only, and player/general
     stock where the audited source exposes them.
   - Rationale: this preserves shop identity and prevents specialist shops from
     becoming a hidden GE-like universal liquidation path.
   - Status: decided 2026-06-24.
5. NPC shop restock uses the same answered-card AnkiScape market clock as the
   parked GE design.
   - `10 answered cards = 1 AnkiScape market hour`, `40 answered cards = 4
     market hours`, and `240 answered cards = 1 market day`.
   - The clock advances on answered cards, including unsuccessful/low-quality
     answers, so economy time follows study throughput rather than only
     XP-eligible reward events.
   - Anki undo must roll back any shop-clock tick and its resulting stock,
     restock-progress, coin, and inventory deltas. Re-answering the same card
     should replay the same deterministic shop state transition rather than
     rerolling or granting extra market time.
   - Rationale: sharing the GE market clock keeps economy systems consistent and
     avoids making shop restock speed depend on which skill or success-rate curve
     the player happens to be training.
   - Status: decided 2026-06-24.
6. The first shop implementation should target all source-backed in-game shops
   that are not mechanically redundant, not only Hunter/Fishing supply shops.
   - The shop registry should be broad from the start, using source-backed shop
     definitions across the game instead of proving the model on one small
     convenience family first.
   - Redundant shops should be collapsed when they share the same meaningful
     stock, prices, access rules, currency, sell policy, and restock behavior.
     They can appear under a generic label or shared group rather than as many
     duplicate visible rows with unique NPC/place names.
   - Collapsing must not erase mechanically relevant differences. Unique stock,
     unique access locks, unique currency, unique sell policy, unique restock or
     price behavior, or source-backed shared-stock relationships require a
     separate entry or an explicit variant.
   - Status: decided 2026-06-24.
7. Shop grouping/collapse is primarily a UI clutter-control feature, not a data
   merge rule.
   - The Shop tab should use collapsible sections similar to the existing Skills
     hub grouped target lists, so broad shop coverage stays navigable.
   - Mechanically separate shops must remain separate even when they look
     redundant. If the real strategy is to buy out the same item from multiple
     shop inventories, such as feathers from multiple fishing shops, each
     inventory must retain independent stock/restock state.
   - Collapsed UI groups may summarize or nest similar shops, but they must not
     merge stock unless source evidence says the inventory is actually shared.
   - Source shop names should remain visible in details/provenance or variant
     rows so broad coverage can still be audited.
   - Status: decided 2026-06-24.
8. The first implementation may include both backend and frontend work, not a
   backend-only proof slice.
   - Backend still owns the source-backed shop registry, shared-stock state,
     access locks, price/restock formulas, transaction helpers, migrations,
     deterministic clock behavior, undo deltas, and tests.
   - Frontend can ship in the same overall feature once the backend contract is
     stable enough to render: a top-level `Shop` tab with grouped/collapsible
     sections, per-shop stock rows, buy/sell actions, lock states, prices,
     owned Coins, and provenance/detail affordances.
   - Because the owner is mobile/VNC-constrained, the implementation thread
     should lean harder on automated pure tests, offscreen Qt tests, screenshots
     or status artifacts, and direct runtime proof instead of depending on the
     owner for manual exploratory testing.
   - Status: decided 2026-06-24.
9. The `Shop` tab should use a grouped master/detail browsing shape.
   - The navigation side should group and collapse shop families, similar in
     spirit to the Skills hub's grouped target lists.
   - Selecting a shop or shop variant should show its stock table, buy/sell
     controls, lock state/reason, price, stock/restock state, owned Coins, and
     source/provenance details in the main panel.
   - HTML UI mockups should be produced during the implementation thread after
     the design grill closes, not during the remaining grill questions.
   - Status: decided 2026-06-24.
10. Shop transactions should use familiar RuneScape-style quantity controls.
    - Support buy/sell `1`, `5`, `10`, `50`, custom quantity, and buy/sell all
      where the source policy and current stock/inventory state allow it.
    - Clamp requested quantities by current shop stock, player-owned Coins or
      alternate currency, available inventory capacity, and sellable inventory
      count.
    - High-cost or very large buy-out actions should require explicit
      confirmation, especially when the purchase would spend a large share of
      the player's Coins or buy out a limited stock row.
    - Status: decided 2026-06-24.
11. v1 should model alternate currencies but only enable transactions for
    currency systems that exist in AnkiScape.
    - Coin-based shops can be live in v1 because `Coins` already exist in the
      economy.
    - The shop registry should still store currency metadata for non-coin shops,
      including currency item/point identity and source provenance.
    - Non-coin shops whose currency systems are not implemented yet should render
      locked or read-only with a clear reason such as `Currency not implemented`.
    - Do not invent Slayer points, Tokkul, loyalty points, minigame currencies,
      or other reward currencies as part of the generic NPC-shop v1 unless their
      owning gameplay system is implemented deliberately.
    - Status: decided 2026-06-24.
12. Shops must not create a new universal coin faucet.
    - Players can spend Coins that already enter through existing or future
      source-backed routes such as quest rewards, combat drops, reclaim systems,
      market systems, and other implemented gameplay.
    - Selling to shops can convert real inventory into Coins according to each
      shop's source policy and price behavior.
    - Ordinary reviews must not grant Coins merely because the Shop tab exists.
    - Status: decided 2026-06-24.
13. Player-sold temporary stock should exist where source shop policy supports
    it, adapted to AnkiScape's single-player model.
    - General stores and any other source-backed shop policies that accept
      player-sold items may add those items to the shop's mutable stock.
    - In AnkiScape, player-sold stock is visible only to the same local player
      unless a future multiplayer/shared-world model exists. Do not pretend
      other players are buying it.
    - Player-sold stock should restock back down or disappear according to the
      audited source behavior, and it must be included in deterministic
      rollback snapshots.
    - Shops whose source policy rejects an item must not expose that item as
      temporary stock.
    - Status: decided 2026-06-24.
14. Shop stock state should be initialized lazily by `shared_stock_group`.
    - Existing saves should not be migrated into a large fully materialized shop
      state for every source-backed shop.
    - Default stock should be derived from checked-in shop registry data until a
      group is opened, transacted with, restock-progressed, or otherwise
      diverges from default.
    - Persist only groups with non-default current stock, restock progress,
      player-sold temporary stock, or other state that cannot be recomputed from
      source data.
    - Status: decided 2026-06-24.
15. Never-touched shops should not be actively tracked or advanced.
    - A shop group that has never been opened or transacted with is treated as
      being at its source default stock.
    - Once a shop group is touched and diverges from default, AnkiScape should
      track and advance its restock state on the shared market clock.
    - When a touched group fully returns to default and has no temporary/player
      stock or restock-progress residue, it can be pruned back out of persisted
      state.
    - Status: decided 2026-06-24.
16. Source provenance should be available but not noisy in the normal Shop UI.
    - The player-facing Shop tab should not put source paths, conflict notes, or
      long provenance text into every visible stock row.
    - A concise details/provenance expander may show source family, source tier,
      and collapsed-shop/source-name details when the player wants to inspect
      them.
    - Full source paths, conflict resolution, redundant-shop collapse rationale,
      and audit evidence belong in generated source-audit docs and developer
      tooling.
    - Status: decided 2026-06-24.
17. Locked shops should generally remain visible in the Shop tab.
    - Shops blocked by known quest, route-precedent, skill, currency, or other
      source-backed access gates should render disabled with a concise lock
      reason.
    - Developer-invalid, unsourced, or rejected rows should be hidden from the
      player UI rather than presented as locked content.
    - Rationale: this matches the existing AnkiScape pattern of surfacing future
      or gated content while keeping actual invalid data out of the normal UI.
    - Status: decided 2026-06-24.
18. NPC shop coverage targets pre-EOC parity, using local 2011Scape and
    Darkan/2012scape as equal source inputs for shop data.
    - The shop registry should not be constrained to only the October 2011
      2011Scape snapshot when Darkan/2012scape contains valid pre-EOC shop
      coverage.
    - Use both local source trees as first-class evidence for shop stock, prices,
      restock, sell policy, access gates, and NPC/shop identity.
    - When sources conflict, resolve against historical RuneScape Wiki revisions
      or other pre-EOC evidence and record the choice in shop provenance/audit
      notes.
    - Exclude post-EOC or clearly out-of-era shop content unless the owner later
      expands the era boundary.
    - Status: decided 2026-06-24.
19. Pre-EOC reward, minigame, and special-currency shops should be included in
    the broad registry when source-backed, even if they are not transactable yet.
    - These shops should render locked or read-only until their owning gameplay
      system and currency exist in AnkiScape.
    - The registry should preserve their stock, prices/costs, currency, access
      locks, and provenance so future Slayer, minigame, Tokkul, loyalty, or
      other currency work can enable them without re-auditing from scratch.
    - Do not invent unsupported point balances or reward currencies solely to
      make these shop rows live in v1.
    - Status: decided 2026-06-24.
20. The broad shop registry should be generated from source files, not
    hand-authored wholesale.
    - Use tooling to parse/import source-backed shop data from Darkan JSON shops
      and 2011Scape shop plugin definitions where feasible.
    - Emit a checked-in Python shop data module plus an audit/collapse report so
      the generated output can be reviewed and tested.
    - Hand-authored overrides should be limited to source conflicts,
      pre-EOC/era exclusions, access gates, grouping/collapse labels, source
      corrections, and AnkiScape-specific presentation decisions.
    - Rationale: broad shop parity is too large and error-prone to maintain by
      manually transcribing every shop row.
    - Status: decided 2026-06-24.
21. Every item exposed through a live or visible shop row should exist in
    AnkiScape item data.
    - The shop generator/import pipeline should not leave shop-stock items as
      unresolved external ids when they appear in the player-facing Shop tab.
    - Missing items discovered by the shop import should be added to the item
      registry or generated item data with source identity, storage key,
      tradability, category, and asset/provenance handling appropriate to the
      item.
    - Validation should fail when a visible shop row references an unregistered
      item, rather than silently hiding the item or rendering an opaque id.
    - Deferred or out-of-era shops can remain locked/read-only, but their visible
      stock still needs item identity if it is shown to the player.
    - Status: decided 2026-06-24.
22. Complete icon coverage should not block the first shop implementation.
    - Every visible shop-stock item still needs a resolved AnkiScape item
      identity and display name.
    - Missing icons may fall back to text-only rows or existing generic
      rendering if the item data is otherwise valid.
    - The shop import/audit should report missing icon coverage so asset work can
      be batched later without hiding or invalidating source-backed shop stock.
    - Status: decided 2026-06-24.
23. Shop v1 should not model bank notes.
    - Shop transactions should use AnkiScape's existing flat inventory counts:
      buying adds item counts and selling removes item counts.
    - Do not add note/unnote mechanics or bank-note item variants as part of the
      generic shop system.
    - If a source row appears to sell a noted item, resolve it deliberately during
      source audit rather than introducing a global notes model.
    - Status: decided 2026-06-24.
24. Shop transactions use AnkiScape's existing flat inventory/bank model rather
    than RuneScape backpack-capacity shopping trips.
    - Buying should be clamped by shop stock and owned currency, not by 28-slot
      backpack capacity.
    - Selling should be clamped by the player's current flat inventory count and
      the shop's source sell policy.
    - Do not add a separate backpack/travel/loadout loop just to make shops feel
      closer to RuneScape.
    - Status: derived from existing AnkiScape inventory convention and accepted
      during grill on 2026-06-24.
25. Shop transactions happen immediately from the `Shop` tab, not as review
    actions.
    - Buying and selling are management UI commands that mutate inventory,
      currency, and shop stock when clicked.
    - Shopping does not award skill XP and does not need to wait for the next
      answered card.
    - The answered-card market clock still advances shop restock time, but
      purchases and sales themselves are explicit UI actions.
    - Status: decided 2026-06-24.
26. Shop v1 should include text search in addition to grouped/collapsible
    browsing.
    - Current AnkiScape surfaces have useful structured filters, but no general
      text search pattern to reuse.
    - Shop search should match shop names, grouped labels, NPC/shop aliases,
      stock item names, and source/location labels.
    - Search results should preserve source-backed shop separation. Searching
      for an item such as feathers should surface every distinct shop that can
      sell it, rather than collapsing mechanically separate buyout routes.
    - Keep locked/read-only shops visible in search results with concise lock
      reasons so a search answers both "where can I buy this?" and "why can't I
      use it yet?"
    - Status: decided 2026-06-24.
27. Shop search should support item-first comparison results.
    - When the query matches an item, the UI should be able to show one row per
      distinct shop stock source rather than only filtering the shop tree.
    - Comparison rows should include shop name, group/collapse label, current
      access or lock reason, current stock, buy price, restock state, and a
      click-through to the full shop detail.
    - This is especially important for source-backed multi-shop buyout routes
      such as feathers, where mechanically separate shops must remain visible.
    - Status: decided 2026-06-24.
28. Temporary supply bridges should be retired once real source-backed shops
    cover the same item route.
    - Keep existing bridge routes only until the corresponding shop path exists,
      has save-safe transactions, and has enough tests to avoid breaking current
      saves.
    - After replacement, hide or remove the bridge from normal player UI while
      leaving a migration note in project docs.
    - Do not keep bridge routes as parallel economy sources for the same item,
      because that weakens the purpose of modeling shop stock, pricing, and
      access.
    - Status: decided 2026-06-24.
29. Shop import should fail closed for live gameplay when source data cannot be
    safely resolved.
    - "Fail closed" means the player cannot transact with a row/shop until its
      required data is known and validated.
    - "Fail open" would mean letting the row/shop transact anyway by guessing or
      silently accepting missing data; do not do that for shops.
    - A row should not become live/transactable if it has an unknown item,
      unknown currency, invalid price, missing stock policy, unresolved shared
      stock group, or unresolved era/source conflict.
    - Unresolved rows may still appear in generator/audit output, and may be
      represented as read-only developer-facing audit entries, so coverage gaps
      are visible instead of silently lost.
    - Status: decided 2026-06-24.
30. Shop coverage should account for every imported source row with an explicit
    disposition.
    - The import/audit pipeline should not leave vague unresolved shop or item
      rows as an acceptable end state.
    - Every source-backed shop and stock row should be classified as one of:
      live/transactable, visible but locked/read-only, collapsed under a named
      presentation group while preserving mechanical identity, excluded for
      pre-EOC/source-policy reasons, superseded by stronger source evidence, or
      blocked by a specific missing dependency that must be fixed before the
      shop slice is considered complete.
    - The generator/audit should fail the implementation slice when any row lacks
      a disposition, item identity, currency decision, stock policy, price policy,
      shared-stock decision, and source/provenance note.
    - Status: decided 2026-06-24.
31. The first delivered shop catalog should be comprehensive, not phased by an
    arbitrary subset.
    - It is acceptable for implementation tooling to iterate internally, but the
      player-facing shop slice should not land as a random partial catalog.
    - The completion gate is a full disposition ledger for all source-backed,
      pre-EOC in-game shops in scope: live/transactable, visible but locked or
      read-only, mechanically separate but grouped for presentation, excluded by
      explicit source/era policy, or superseded by stronger evidence.
    - Missing item identities, currency decisions, stock policies, price
      policies, shared-stock decisions, access locks, and provenance notes should
      be resolved in the same broad pass rather than deferred as normal follow-up
      work.
    - Status: decided 2026-06-24.
32. Darkan should be the default winner when Darkan and 2011Scape disagree about
    the same shop, because it is closer to the pre-EOC target.
    - Preserve both source records in the audit output when they disagree.
    - Use Darkan values by default for stock, prices, restock behavior, shop
      policy, and shared-stock grouping unless stronger pre-EOC evidence or a
      hand-authored override says otherwise.
    - Do not silently discard 2011Scape mismatches; record them as conflict
      evidence so future audits can revisit the decision.
    - Status: decided 2026-06-24.
33. Shop access locks should be explicit or high-confidence inferred gates, not a
    general location simulation.
    - Generate locks from source-backed quest, skill, currency, minigame, and
      route requirements when those are encoded directly.
    - Allow high-confidence inferred region locks only when AnkiScape already
      models the gate or the requirement is obvious from pre-EOC gameplay, such
      as a quest-gated region or shop.
    - Do not infer fuzzy travel constraints from distance, geography, or the
      shop's location text alone.
    - Record inferred locks as named override rules with provenance so they can
      be audited separately from directly imported source requirements.
    - Status: decided 2026-06-24.
34. Shop provenance should be player-facing and should not feel like debug UI.
    - The normal Shop tab should not expose raw generator internals, source-file
      paths, unresolved row ids, or implementation jargon.
    - Player-facing source details should be phrased as trust and context
      information, such as source confidence, era fit, access requirement,
      grouped-shop explanation, or why a shop is locked/read-only.
    - Full source paths, conflict records, generated ids, and override internals
      belong in the audit report and tests, not the main player view.
    - A compact details/provenance expander may exist, but it should read like a
      game-facing encyclopedia note rather than a developer dump.
    - Status: decided 2026-06-24.
35. Shop restock timing internals should not be exposed in normal player UI.
    - The UI may show current stock and maximum/default stock, because those are
      visible shop facts.
    - Do not show exact countdowns such as reviews until next restock, raw market
      ticks, or internal restock progress in the player-facing Shop tab.
    - Restock progress remains backend/save state for deterministic simulation,
      tests, and rollback; audit/dev tooling can inspect it separately.
    - Status: decided 2026-06-24.
36. Shop price display should show the current transaction price, not the
    underlying formula.
    - The player-facing UI should show the exact current buy and sell price that
      applies before the click.
    - Prices should update after each purchase or sale if source-backed stock
      behavior changes the current price.
    - Do not show formula internals, price-curve equations, or future threshold
      predictions in normal UI unless a specific source UI exposed equivalent
      information.
    - Status: decided 2026-06-24.
37. Quantity purchases and sales should follow source game behavior.
    - Do not invent an AnkiScape-specific quantity preview or pricing shortcut.
    - Buy/sell quantity actions should process stock, price, currency, and item
      deltas the way the source shop behavior does for that shop family.
    - If a source shop recalculates price after each item because stock changes,
      the AnkiScape transaction should do the same for multi-item quantities.
    - If a source shop uses a constant main-stock price, multi-item quantities
      should behave as repeated source-equivalent clicks at that constant price.
    - Status: decided 2026-06-24.
38. Default stock and player-sold stock presentation should follow source shop
    behavior.
    - If the source shop treats main/default stock and player/general stock as
      separate pools for price, restock, or display, AnkiScape should preserve
      that separation.
    - If the source shop merges them visually or mechanically, AnkiScape may do
      the same for that shop family.
    - Internal state must still be rich enough to replay source-equivalent buy,
      sell, restock, and rollback behavior deterministically.
    - Status: decided 2026-06-24.
39. Shared stock groups should come from source data or explicit overrides, not
    from similarity inference.
    - Do not infer shared inventory merely because two shops have identical
      names, NPC labels, stock lists, prices, or categories.
    - Use source-encoded shared stock behavior where available.
    - When the source implies shared behavior outside a machine-readable field,
      add a named hand-authored override with provenance.
    - Treat shops as mechanically separate by default unless source evidence says
      otherwise.
    - Status: decided 2026-06-24.
40. Shop browsing UI state should be remembered outside gameplay save state.
    - Lightweight state such as the last selected shop, search text, selected
      search/result mode, and expanded/collapsed groups may be remembered as UI
      preference or session state.
    - Gameplay save state should remain focused on economy state: shop stock
      deltas, player-sold stock, currency, inventory, restock progress, and
      rollback history.
    - Remembered UI state must not affect deterministic shop simulation or undo.
    - Status: decided 2026-06-24.
41. Shop transactions should produce compact player-facing history entries.
    - Record recent buys and sells in human-readable form, including action,
      item, quantity, shop name, and currency total.
    - Use the history to make inventory and currency changes understandable to
      the player, not as a debug event dump.
    - Full deterministic transaction/replay data can remain internal save and
      undo state.
    - Status: decided 2026-06-24.
42. Shop history should support both shop-local and global recent views from the
    same underlying event log.
    - Each shop detail may show recent transactions for that shop.
    - A compact global recent shop activity view may show the latest buys and
      sells across all shops.
    - Do not maintain separate history stores for these views; derive both from
      the same deterministic transaction/event record.
    - Status: decided 2026-06-25.
43. Shop persistence should keep both compact current state and reversible event
    records.
    - Persist current shop state for fast load and UI rendering, including
      per-`shared_stock_group` stock deltas, player-sold stock, and restock
      progress for shops that have diverged from defaults.
    - Persist buy, sell, restock, and clock-advance events where needed for
      rollback, compact player-facing history, and deterministic replay tests.
    - The event record can be pruned or checkpointed once it is outside the
      required undo/history window and the current state checkpoint is
      sufficient.
    - Status: decided 2026-06-25.
44. Shop restock should be evaluated lazily against the global market clock.
    - Answered cards advance the shared AnkiScape market clock.
    - Touched/diverged shop groups store the last market tick at which their
      restock state was evaluated.
    - When a shop is opened or a transaction is attempted, the backend computes
      elapsed market ticks for that shop group, applies source-equivalent
      restock deterministically, updates current shop state, and records the
      resulting restock event if needed for undo/history.
    - Do not iterate every touched shop on every answered card when lazy
      evaluation can produce the same deterministic result.
    - Status: decided 2026-06-25.
45. Open shop views should refresh restock state on meaningful UI/backend events,
    not live-tick while visible.
    - Evaluate and apply pending restock when the Shop tab opens, when a shop is
      selected, before a buy/sell transaction, and when the player explicitly
      refreshes the view if that control exists.
    - Do not continuously update visible stock tables on a timer while the player
      is looking at them.
    - AnkiScape market time advances from answered cards, so live-ticking shop UI
      would imply a real-time mechanic the game does not have.
    - Status: decided 2026-06-25.
46. Shop-like service vendors should be included with full capability.
    - Include source-backed NPC/vendor services such as sawmill plank conversion,
      tanning hides, and item-for-item exchanges when they are shop-like economy
      interactions.
    - Do not force these services into fake finite-stock rows. Model them as
      service transaction definitions with inputs, outputs, currency costs,
      access locks, quantity behavior, source policy, and provenance.
    - Service transactions should use the same standards as stock shops for item
      identity, validation, deterministic save mutation, rollback, player-facing
      history, search, and source audit coverage.
    - Services only participate in stock/restock state when the source service
      actually has stock or a stock-backed sub-shop.
    - Status: decided 2026-06-25.
47. Item-first search should include both stock shops and service outputs.
    - Searching for an item should surface source-backed stock rows that sell the
      item and service transactions that create, convert, or exchange into that
      item.
    - Results should clearly label the source type, such as `Stock shop` or
      `Service`, so the player can distinguish finite stock/restock mechanics
      from conversion or exchange mechanics.
    - Service search rows should show player-facing inputs, outputs, coin or
      item costs, access locks, and source behavior without exposing generator
      internals.
    - Status: decided 2026-06-27.
48. Service transactions may be live without a broader owning skill/activity
    system when their behavior is pure economy.
    - Pure economy services with source-backed item/currency inputs and outputs,
      such as tanning hides or sawmill plank conversion, may be implemented
      directly in the Shop tab.
    - Services should stay locked/read-only when their real behavior depends on
      an unimplemented minigame state, bespoke activity progress, combat state,
      or reward-point source.
    - Do not invent currencies, activity completion, or reward-point faucets just
      to make a dependent service transactable.
    - Status: decided 2026-06-27.
49. Minigame-dependent shops and services should integrate with flattened linear
    Activities, not full minigame simulations.
    - AnkiScape should not attempt to recreate complex minigames such as Stealing
      Creation as playable systems solely to support their reward shops.
    - When a shop or service depends on minigame progress or reward currency,
      model the dependency as an owning linear Activity gate/reward source once
      that Activity exists.
    - Until the owning Activity/currency exists, keep the shop or service out of
      normal player-facing UI and record its missing dependency in the
      catalog/audit output.
    - Status: decided 2026-06-27.
50. Reward/activity currencies should be defined for catalog accounting even when
    they are not yet earnable.
    - If a source-backed shop or service uses a minigame/activity currency that
      does not exist in AnkiScape yet, create the currency identity and source
      metadata needed to account for the shop row.
    - Do not create an earning path, starting balance, faucet, or player reward
      loop for that currency in the Shop pass.
    - Rows that require the currency should remain non-player-facing until the
      owning flattened Activity or reward source exists.
    - Catalog/audit output should name the missing dependency, such as
      `Requires Stealing Creation points`, without forcing a temporary locked UI
      state into the Shop tab.
    - Status: decided 2026-06-27.
51. Reward shops whose owning Activity does not exist yet should not be shown in
    normal player-facing Shop UI.
    - Account for these shops fully in generated catalog/audit output, including
      source identity, required currency, item identities, and the missing owning
      Activity dependency.
    - Keep them hidden from normal browsing and item-first search until the
      owning flattened Activity or reward source exists.
    - Rationale: showing temporary locked reward shops creates player-facing UI
      that will need to be redesigned when Activities are implemented.
    - Status: decided 2026-06-27.
52. Activity-dependent reward shops should require explicit enablement when the
    owning Activity lands.
    - The generated catalog may know which hidden reward shop or service belongs
      to which future Activity.
    - Do not automatically show a reward shop just because the catalog has an
      Activity dependency label.
    - The Activity implementation should deliberately enable the shop/service
      once the earning path, currency balance, access rules, tests, and
      player-facing wording are ready.
    - Status: decided 2026-06-29.
53. Pure service vendors should live in the same Shop tab but in distinct service
    sections.
    - Keep stock shops and service vendors under one player-facing economy
      surface so item search, history, locks, and transaction behavior are
      unified.
    - Do not make services look mechanically identical to finite/restocking stock
      shops.
    - Group services by skill/domain when natural, such as Crafting `Tanners` or
      Construction `Sawmill`, alongside stock-shop groups in the same navigation.
    - Item-first search may merge stock and service results, but each result
      should keep its source type label.
    - Status: decided 2026-06-29.
54. Service vendors should only expose actions supported by source behavior.
    - Do not add generic selling, buying, conversion, or exchange actions to a
      service vendor unless the source service supports that action.
    - A tanner tans hides; a sawmill converts logs to planks; an exchange NPC
      exchanges its source-backed inputs for outputs. They do not become general
      buyers or sellers unless the source says so.
    - If the same NPC also opens a real stock shop, model that stock shop as a
      separate source-backed transaction surface under the same player-facing
      shop/vendor entry where appropriate.
    - Status: implied by source-parity policy and recorded 2026-06-29.
55. Service and vendor-action coverage should use a source-backed manifest, not
    blind code inference.
    - Structured stock shops can be generated from structured shop source data.
    - Services and vendor actions that live in Java/Kotlin dialogue, NPC handler,
      object handler, or button handler code should be represented by a typed
      manifest entry with source file/line provenance.
    - Each manifest entry should declare action type, NPC/vendor label, inputs,
      outputs, currency/item costs, quantity behavior, access locks, source
      behavior notes, and whether it is player-facing now or audit-only.
    - Candidate discovery can use broad code scans, but live gameplay entries
      must be confirmed and typed deliberately.
    - Status: decided 2026-06-30.
56. The shop pass must account for vendor actions that do not use the stock-shop
    UI.
    - Do not define shop coverage solely as `ShopsHandler.openShop` or equivalent
      stock-shop interfaces.
    - Include source-backed direct vendor/dialogue actions such as buying beer
      from bartenders, barcrawl drinks, selling beer glasses where supported,
      buying newspapers, repairs, exchanges, conversions, and other NPC/vendor
      economy interactions.
    - These actions should use the same item identity, validation, search,
      history, rollback, source audit, and player-facing wording standards as
      stock shops and service vendors.
    - Preserve source mechanics: direct vendor buys do not gain fake stock/restock
      behavior unless the source action has stock.
    - Status: decided 2026-06-30.
57. Shop services are NPC/vendor-mediated economy actions, not ordinary
    self-directed skilling recipes.
    - Include NPC/vendor-mediated actions such as sawmill plank conversion,
      tanning hides, direct bartender buys, one-off NPC purchases, repairs, and
      exchanges.
    - Exclude self-directed skilling conversions such as smelting at a furnace,
      smithing at an anvil, cooking on a range, or other actions whose owning
      skill system already naturally models the recipe.
    - Status: implied boundary from shop/vendor scope and recorded 2026-06-30.
58. The implementation should produce a checked-in shop coverage report.
    - The import/build step should generate a report listing every stock shop,
      service vendor, and direct vendor action in scope.
    - Each report row should include disposition, source evidence, item/currency
      resolution, player-facing visibility, access/lock status, shared-stock
      decision where relevant, conflict notes, and override/collapse rationale
      where relevant.
    - Tests should fail when any imported/in-scope row lacks a disposition or
      when any player-facing row references an unknown item, unknown currency,
      unresolved stock policy, unresolved price policy, or unresolved source
      conflict.
    - Rationale: broad shop parity needs a concrete completeness artifact so
      "everything is minutely accounted for" can be verified without reading the
      generated catalog by hand.
    - Status: decided 2026-06-30.
59. Vendor-action candidate discovery should use broad automated scans and may
    use subagents for source review.
    - Build discovery tooling that scans Darkan/2011Scape code for likely economy
      mutations outside structured stock-shop handlers, including patterns such
      as `removeCoins + addItem`, `deleteItem + addItem`, `addItemToInv`,
      `ShopsHandler.openShop`, bartender helpers, exchange helpers, repair
      helpers, and direct dialogue purchases.
    - Use subagents where helpful to divide source review by area, action family,
      or candidate bucket.
    - Subagents may discover, summarize, and propose classifications, but the
      final source-backed service/vendor manifest and coverage report should be
      deterministic checked-in artifacts.
    - Every candidate should be classified as included, excluded with reason,
      duplicate/superseded by another source, out-of-scope self-directed
      skilling, quest-only, future Activity-dependent, or otherwise explicitly
      dispositioned.
    - Status: decided 2026-06-30.
60. AnkiScape runtime must not depend on external source checkouts.
    - Runtime shop behavior should use checked-in generated data, source-backed
      manifests, overrides, and audit artifacts that live in the addon repo.
    - Local Darkan and 2011Scape checkouts are tooling inputs for regeneration
      and source audit work only.
    - Normal play, addon loading, and runtime tests should not require those
      external source paths to exist.
    - Status: implied by addon portability requirements and recorded
      2026-06-30.
61. Broad sell policies such as general-store behavior should follow source game
    parity, with undo handled internally.
    - If a source shop can buy broad tradeable items, model that as a source
      sell policy on the shop.
    - Do not pre-render every theoretical sellable item as default stock; the
      game does not show player-sold stock before a player sells it.
    - When the player sells an eligible item, create or update player-sold stock
      according to source behavior, including source-backed pricing, display,
      and restock/disappearance rules.
    - Undo/replay should reverse the transaction deterministically: restore the
      player's item/currency, restore or remove the player-sold stock entry, and
      roll back any related event/history state.
    - Status: decided 2026-06-30.
62. Vendor actions with no durable item output should be included in Shop only
    when they are repeatable economy actions.
    - Account for no-durable-output vendor actions in the source audit, including
      actions that remove coins/items and immediately apply an effect, travel,
      quest/activity state, or other non-inventory outcome.
    - Put repeatable player-facing economy actions in the Shop tab when they
      behave like ongoing vendor services.
    - Keep one-time quest, miniquest, or Activity state transitions owned by the
      relevant Quest/Activity flow, even if the source interaction is mediated by
      a bartender, vendor, or other NPC that takes payment.
    - Status: decided 2026-06-30.
63. Free/reclaim item interactions should be owned by claim systems, not the Shop
    tab.
    - Audit NPC/vendor-mediated free item and reclaim interactions as candidates
      so they are not missed during source review.
    - Exclude them from the Shop tab unless the source presents the interaction
      as a repeatable shop/service economy action.
    - Ordinary claims belong in claim systems; reclaims should be even less
      prominent than regular claims because they are recovery paths, not normal
      acquisition routes.
    - Reclaim UI should be hidden or tucked behind contextual claim/recovery
      affordances rather than advertised alongside normal shop or claim options.
    - Status: decided 2026-06-30.
64. Shop identity should reuse AnkiScape's existing stable-id and migration
    pattern rather than inventing a separate global identity framework.
    - Existing repo surfaces already use stable ids for skills, quests, targets,
      combat targets, and generated data, with display names treated as labels.
    - Existing save loading already has versioned migration and feature-specific
      legacy alias maps for renamed targets/items.
    - Shops should follow that pattern: stable ids for shops, shared-stock
      groups, stock rows when needed, services, vendor actions, currencies, and
      source entities; display names remain changeable labels.
    - Shop save/history entries should store stable ids plus a display-name
      snapshot where useful for human-readable history.
    - Any future shop id rename, collapse change, or generated-source correction
      should be handled through explicit alias/migration maps and tested in
      storage/shop migration tests.
    - Status: decided 2026-06-30.
65. Shop transactions should use separate pure preview and apply APIs.
    - `preview_shop_transaction_pure(...)` should compute whether a buy, sell,
      service, or vendor action is currently allowed and return player-facing
      price, quantity, lock/error, and effect summary without mutating state.
    - `apply_shop_transaction_pure(...)` should perform the deterministic state
      mutation and return updated player data plus a structured transaction event
      for rollback, history, and replay tests.
    - UI buttons can be immediate clicks, but frontend code should not reimplement
      backend pricing, quantity clamping, sell policy, access-lock, or service
      validation logic.
    - Status: decided 2026-06-30.
66. Transaction preview and confirmation UI should match source UI behavior.
    - The backend may compute previews internally for disabled states, tests, and
      deterministic transaction handling.
    - The player-facing UI should expose only the amount of price, stock,
      quantity, lock, and confirmation information that the source game UI or
      source-equivalent interaction exposed.
    - Do not add extra AnkiScape confirmation screens, future-cost previews, or
      spreadsheet-like transaction summaries unless source behavior calls for
      them.
    - Status: decided 2026-06-30.
67. Backend and frontend shop work should be split with a stable handoff contract.
    - Backend owns source import/generation, service/vendor manifest schema,
      source audit reports, item/currency validation, pure transaction preview
      and apply APIs, save/migration, rollback, restock simulation, and coverage
      tests.
    - Frontend owns the Qt Shop tab navigation, grouped/collapsible browsing,
      item-first search, stock/service detail rendering, and player-facing
      interaction polish.
    - Frontend should not duplicate pricing, eligibility, stock, restock,
      sell-policy, access-lock, or service-validation rules. It should render
      backend-provided view models and call backend transaction APIs.
    - Because the Shop interface is complex, it is acceptable and expected to
      hand frontend implementation to a separate Claude/frontend thread once the
      backend contract and fixtures are ready.
    - Status: decided 2026-06-30.
68. Backend should produce deterministic contract/data fixtures for frontend
    handoff.
    - Fixtures mean representative backend view-model outputs and transaction
      API examples, not UI modules and not runtime middleware.
    - Generate or snapshot fixtures from pure backend APIs such as
      `shop_view_model_pure(...)`, `preview_shop_transaction_pure(...)`, and
      `apply_shop_transaction_pure(...)` so the frontend can render realistic
      locked, live, service, search, history, and transaction states without
      duplicating backend rules.
    - Include fixtures for normal coin stock shops, item-first feather-style
      multi-shop search, locked/read-only shops, shared-stock shops, player-sold
      stock, tanning/sawmill-style services, bartender/direct vendor actions,
      hidden Activity-dependent reward shops, transaction errors, and compact
      history rows.
    - Treat fixtures as a versioned backend/frontend contract. Backend tests
      should fail when required schema fields disappear or when fixture outputs
      drift without an intentional update.
    - Status: decided 2026-06-30.
69. All shop mutations should flow through one structured event model.
    - Use the same event contract for buy, sell, service, direct vendor action,
      restock application, and market-clock shop effects instead of separate
      ad hoc records for history, rollback, and replay.
    - Each event should include stable ids, player-facing display snapshots,
      quantity and item/currency deltas, relevant stock before/after state,
      market tick, source/provenance reference, and enough rollback payload to
      reverse the mutation deterministically.
    - Derive compact shop-local and global history rows from this event stream
      rather than maintaining separate history stores.
    - Tests should cover replay/rollback from these events, including
      player-sold stock, shared-stock groups, direct vendor actions, and lazy
      restock application.
    - Status: decided 2026-07-05.
70. Shop undo should use simple explicit inverse deltas, with checkpoints as a
    supporting replay/recovery layer.
    - Each shop event should carry the direct inverse item, currency, stock,
      restock-progress, history, and UI-visible state deltas needed to undo that
      event without re-running shop pricing, source import, restock, or access
      logic.
    - Periodic compact checkpoints may still exist for replay tests, recovery,
      pruning old event history, and validating deterministic behavior.
    - Ordinary Anki undo should be computationally cheap and local to the events
      being undone; it should not require replaying a long event stream or
      recomputing historical source formulas.
    - Anti-cheat or exploit-hardening concerns should not drive the local
      single-player shop design. The goal is simple, deterministic, reversible
      behavior, not adversarial protection.
    - Status: decided 2026-07-05.

## Source Checkpoints From Grill

- Local 2011Scape has generic shop state with normal/infinite stock,
  stock-only/tradeable/all/no-buy policies, mutable `currentAmount`, and restock
  cycles in `/Users/ArmanTarkhanian1/Downloads/game-main/game/src/main/kotlin/gg/rsmod/game/model/shop/`.
- Local 2011Scape coin shops use `ItemCurrency`; selling items into a shop uses
  current stock to lower the price the shop pays, while ordinary shop sales use
  the row sell price or item cost unless overridden.
- Local Darkan/2012scape has a broad JSON shop catalog under
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops/`,
  mutable main/general stock, per-item restock ticks, custom prices, and generic
  buy/sell handlers in
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/engine/Shop.java`.
- Historical RuneScape references confirm stock-dependent prices existed, but
  the 2007 shop improvement split many shops into constant-price main stock and
  variable player stock. Treat this as a source-audit warning against blindly
  importing an OSRS formula into 2011-era AnkiScape.
- The parked GE design uses an AnkiScape market clock where `10 answered cards =
  1 market hour`, `40 answered cards = 4-hour buy-limit window`, and `240
  answered cards = 1 market day`; it advances on answered cards, not only
  successful skill-reward cards, and Anki undo rolls back market ticks.
- Existing repo UI has Quest-list filters, not general search: the Quests tab
  exposes Hide completed, Hide unable to start, Access, Difficulty, Length, and
  Timeline filters in `ui.py`, with tests in `tests/test_main_menu_widget.py`.
- Local Darkan has direct vendor-action examples outside stock-shop JSON:
  bartender drink purchases and beer-glass sales in
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/utils/BartenderUtils.kt`,
  inn-specific bartender dialogue in
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/world/areas/varrock/npcs/`,
  and one-off dialogue purchases such as Benny's newspaper dialogue.
- Current AnkiScape identity patterns already include stable skill ids in
  `skill_registry.py`, stable target ids in data modules such as
  `fletching_data.py`, quest ids in `quest_data.py`, review-action aliases in
  `action_registry.py`, and versioned save migration/legacy target maps in
  `storage_pure.py`.

## Open Branches

- Frontend information density and mockup variants.
