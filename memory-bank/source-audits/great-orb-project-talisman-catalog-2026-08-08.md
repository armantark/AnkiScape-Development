# Great Orb Project ordinary talisman catalog

Date: `2026-08-08`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Period evidence

RuneScape Wiki `The Great Orb Project` oldid `6564759`, timestamp
`2012-11-17T03:12:07Z`, states that Wizard Elriss sells every talisman except
Death and Blood. It prices free-to-play talismans at 50 Runecrafting Guild
tokens and members-only talismans at 125 tokens:

<https://runescape.wiki/w/The_Great_Orb_Project?oldid=6564759>

The immutable Darkan source artifact preserves that exact revision at:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/great-orb-project-oldids.json`

Its stored wikitext SHA-256 is
`a30e4857ada315e1cbe4c7daf6a89b62d8ba72d8bb67d422109c122772b3b874`.

The cutoff shop therefore contains these ordinary rows:

| Price | Talismans |
| ---: | --- |
| 50 tokens | Air, Mind, Water, Earth, Fire, Body |
| 125 tokens | Cosmic, Chaos, Nature, Law |

Death and Blood remain excluded exactly as the source states. The existing
Elemental, Omni-talisman, Omni-tiara, and Pure essence rows are separate reward
families and are unchanged by this slice.

OpenRS2 revision 742 (`2012-11-07`) independently pins the ten item identities
as `1438`, `1448`, `1444`, `1440`, `1442`, `1446`, `1454`, `1452`, `1462`, and
`1458`. Each is non-stackable and exchangeable. The local authentic item table
at `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:18756-18900`
agrees on those names and identities; the file SHA-256 observed for this pass
is `4bc95333b282216b6d1a50dd60b4510aa0bbc837d5bc39b0d1b8e44d7390e4f0`.

## Live translation

All ten talismans are one-at-a-time manual purchases. A supplied quantity is
ignored, matching the existing ordinary-reward path; only Pure essence retains
Buy X. Purchases debit the exact token price and add the existing canonical
Runecrafting item, so altar access, combination runes, tiara binding, Omni
claim access, inventory, bank, discard, and undo continue through their shared
registries without a second implementation.

The existing reward selector now displays each registered item sprite in a
fixed 24-pixel slot. Every reused sprite has cutoff-qualified provenance in
`assets_provenance.json`; no new image or asset claim was added.

## Boundaries

- Master and standard Runecrafter robes were closed by their newer `2026-08-09`
  records. Talisman staves and teleport tablets retain explicit depth status
  because they add binding or teleport behavior.
- No hidden roll, source-blocked value, placeholder, wall clock, or owner design
  decision was introduced.

## Verification

Focused pure tests pin the exact ten-row catalog, all item identities and token
prices, one-at-a-time purchase semantics, registry reachability, and the
fourteen-row complete current shop projection. A real offscreen Qt test pins
the fixed icon size and a non-null icon for every ordinary talisman. The focused
closure passes 280 pure/integration/undo/registry tests and one real Qt selector
test. Full plain and real offscreen-Qt discovery each pass 3,891 tests, with 479
expected plain skips and three intentional Qt skips. Documentation audits 524
Markdown and 431 HTML files; test quality reports zero hard issues across 3,857
tests in 177 files. Compilation, tracked JSON, diff, asset-normalization, and
worktree audits pass. Reachability remains unchanged at 1,499 actions, 2,240
reachable items, 168 orphan inputs, and 188 unresolved actions.
