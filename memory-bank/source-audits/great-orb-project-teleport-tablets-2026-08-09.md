# Great Orb Project teleport tablets

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Period evidence

RuneScape Wiki `The Great Orb Project` oldid `6564759`, timestamp
`2012-11-17T03:12:07Z`, defines the complete 14-tablet family:

<https://runescape.wiki/w/The_Great_Orb_Project?oldid=6564759>

The immutable Darkan copy is:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/great-orb-project-oldids.json`

The selected wikitext SHA-256 is
`a30e4857ada315e1cbe4c7daf6a89b62d8ba72d8bb67d422109c122772b3b874`.
The complete source-bundle SHA-256 is
`2eb976379eb698f1a57ece1cc463a1e01a5726c81214e4da159a418bacb49c2b`.

The revision states that altar tablets are stackable, single-use devices that
teleport outside the corresponding altar. The player still needs an ordinary
access item, such as a talisman, tiara, or Runecrafting staff, to enter. The
Runecrafting Guild tablet instead teleports directly inside the Guild.

| Tablet | Tokens | Members | Item ID | Period gate |
| --- | ---: | --- | ---: | --- |
| Runecrafting guild | 15 | No | 13598 | None |
| Air altar | 30 | No | 13599 | None |
| Mind altar | 32 | No | 13600 | None |
| Water altar | 34 | No | 13601 | None |
| Earth altar | 36 | No | 13602 | None |
| Fire altar | 37 | No | 13603 | None |
| Body altar | 38 | No | 13604 | None |
| Cosmic altar | 39 | Yes | 13605 | Lost City |
| Chaos altar | 40 | Yes | 13606 | None |
| Astral altar | 41 | Yes | 13611 | Lunar Diplomacy and Seal of passage |
| Nature altar | 42 | Yes | 13607 | None |
| Law altar | 43 | Yes | 13608 | No weapons or armour equipped or carried |
| Death altar | 44 | Yes | 13609 | Mourning's Ends Part II |
| Blood altar | 45 | Yes | 13610 | Legacy of Seergaze |

OpenRS2 cache ID `544`, RuneScape revision `742`, dated `2012-11-07`, pins
items `13598` through `13611`. Every row has its exact name, is stackable and
non-exchangeable, and exposes the inventory option `Break`:

`/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/runescape-742-2012-11-07-openrs2-544-disk.zip`

Its SHA-256 is
`9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`.

The authentic item table independently confirms all 14 identities and their
non-tradeable status:

`/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:156565-156649`

## Live translation

Wizard Elriss sells every tablet one at a time for its exact token price through
the existing atomic Great Orb purchase and direct-undo path. All tablets are
canonical stackable, non-tradeable items with a `Break` action in the Bank item
menu.

Breaking an altar tablet consumes one item, selects its canonical Runecrafting
target, and queues the existing Wicked-hood route seam. The next matching route
therefore omits only its outbound leg. It does not create a parallel world-map
location, skip the return or bank phases, grant altar access, or grant XP. The
Guild tablet consumes itself and records arrival inside the Guild without
queuing an altar-route waiver.

Cosmic, Astral, Death, and Blood reuse the existing quest-unlock table. Astral
also requires a Seal of passage. Law rejects combat equipment in the equipped
slots or the active Law-runecrafting carried pack; the flat Bank is storage,
not the period game's physical inventory. The zero-bonus Law talisman staff is
the sourced Entrana-safe exception.

The tablet count is reconciled against the active target's carried view when it
is consumed, so the view cannot retain a copy that no longer exists in the flat
store. Refused actions preserve the item and the pending route. Direct action
undo restores the item and route state atomically.

Fourteen source sprites are stored in `activityitems/` and registered in the
shared provenance manifest. The existing Great Orb reward selector renders
them at its fixed 24-pixel icon size. The Bank adds one context-menu command;
no new panel, dialog, scrolling region, or interaction pattern was introduced.

## Boundaries

- The members column is preserved as period catalog metadata. AnkiScape models
  the complete members game and does not add a membership toggle here.
- Tablets teleport to altar exteriors. Existing access-item and quest gates
  still own entry and crafting.
- The Guild tablet does not invent Runespan, world travel, or a persistent
  player-location substrate.
- Law checks the physical carried pack and equipped gear, not every item stored
  in the Bank.
- No wall clock, save-schema field, placeholder, or owner design decision was
  added.

## Verification contract

Focused pure, registry, runtime, hook, asset, and real offscreen-Qt tests cover
the exact 14-row catalog, prices, IDs, item semantics, cutoff provenance,
purchase, consumption, refusal preservation, carried-view reconciliation,
quest and Seal gates, the Law restriction and staff exception, Guild behavior,
altar-access preservation, route-phase integration, direct undo, context-menu
dispatch, fixed icon size, and selector reachability.

The focused pure/integration/immutability packet passes 269 tests, and the
complete real Qt widget module passes 395. Full plain and real offscreen-Qt
discovery each pass 3,908 tests, with 480 expected plain skips and three
intentional Qt skips. Documentation audits 528 Markdown and 431 HTML files;
test quality reports zero hard issues across 3,874 tests in 177 files.
Compilation, tracked JSON, diff whitespace, deterministic asset fetching,
global UI-asset normalization, and worktree safety pass. Reachability improves
to 1,511 actions and 2,284 items while the known 168 orphan inputs and 188
blocked actions remain unchanged.
