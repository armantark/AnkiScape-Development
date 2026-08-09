# Trouble Brewing medium-clue service

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **verified and implemented.**

## Period record

`Honest Jimmy's House of Stuff`, oldid `6393015`, timestamp
`2012-10-13T04:08:35Z`, states in its literal wikitext that players can talk to
Honest Jimmy to buy a `Clue scroll (medium)` for exactly `5,000` Pieces of
Eight. The shop therefore awards the clue directly; it does not invent a
physical stock row or stock-replenishment clock.

Source:
<https://runescape.wiki/w/Honest_Jimmy%27s_House_of_Stuff?oldid=6393015>

The one-clue-total rule is owned by the superseding Easy Treasure Trails audit,
not by Trouble Brewing. `Treasure Trails`, oldid `6473708`, timestamp
`2012-10-26T00:01:09Z`, permits a new clue only when none exists in inventory,
Bank, or Kingdom Management resources. Owner answer 4.5 removed the later
one-per-tier anachronism. The live rule remains centralized in
`clue_ownership_reason_pure`.

Sources:

- `memory-bank/source-audits/treasure-trails-easy-horizontal-implementation-2026-07-26.md`
- `memory-bank/design-thread-queue.md`, answer 4.5
- <https://runescape.wiki/w/Treasure_Trails?oldid=6473708>

## Item identity and art

OpenRS2 cache `544`, RuneScape revision `742`, dated `2012-11-07`, pins item
`2801` as non-stackable, non-exchangeable `Clue scroll (medium)` with option
`Read`, zero bonuses, and client model `3374`. Authentic game-main
`data/cfg/items.yml:30954-30961` and `Items.kt:2727` corroborate the identity and
trade rule.

Rev-742 items `2677` (easy), `2722` (hard), and `2801` (medium) all use exact
model `3374` without recolours or textures. The selector therefore reuses the
already normalized cutoff `activityitems/clue_scroll_hard.png` sprite, whose
source revision is dated `2010-11-02`, instead of presenting the existing 2019
OSRS medium-clue fallback as period art. This shared-model reuse supplies visual
art only; the cache and oldids above supply the item and service facts.

## AnkiScape translation

- `Clue scroll (medium)` remains owned by the canonical Combat/Treasure Trails
  item registration. Trouble Brewing adds a service row, not a duplicate item
  definition; the canonical row is enriched with exact ID `2801`, stacking,
  and trade metadata.
- The purchase reducer asks Treasure Trails' central ownership helper before it
  charges the wallet. Any held clue tier or live trail refuses without mutation.
- A successful purchase subtracts exactly `5,000` Pieces and awards one existing
  `Clue scroll (medium)`. The established Trouble Brewing direct-action path
  supplies persistence and atomic undo.
- The pure view exposes the ownership blocker. Qt only renders it, formats the
  price as `5,000 PoE`, marks a held-clue row, and explains both ownership and
  wallet shortfalls on the selector and disabled Buy button.
- Kimi K3 and Fable independently reviewed the compact shop change. Accepted
  findings add the thousands separator and explicit disabled-state guidance;
  neither review claims native Anki appearance.

## Explicit omissions

- Medium Treasure Trails remain catalog depth. The Bank already preserves the
  clue and explains that only Easy is playable; this service does not fabricate
  medium steps or rewards.
- The period page states a dialogue purchase, but no inspected source pins the
  dialogue lines or animation. The existing locationless shop command keeps the
  sourced cost, item, and ownership gate without inventing presentation state.
- `The stuff` remains the next separate Trouble Brewing depth slice.

## Verification

- Focused pure, Treasure Trails, write-through, registry, storage, equipment,
  Bank-layout, integration, undo, and asset checks: 243 tests pass.
- Focused real offscreen Qt: four checks pass for the selector, successful
  purchase, post-purchase blocker, tooltip, icon, and normalization behavior.
- Full plain discovery: 3,922 tests pass with 482 expected skips.
- Full real offscreen-Qt discovery: 3,922 tests pass with three intentional
  skips.
- Documentation: 532 Markdown and 431 HTML files pass the docs audit.
- Test quality: zero hard issues across 3,888 tests in 177 files.
- Reachability remains 1,511 actions, 2,315 reachable items, 168 known orphans,
  and 188 known blocked actions.
- Compilation, tracked JSON parsing, diff hygiene, deterministic asset
  enumeration, asset normalization, and worktree safety pass.
