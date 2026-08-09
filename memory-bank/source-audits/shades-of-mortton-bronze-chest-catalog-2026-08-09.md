# Shades of Mort'ton bronze-chest catalog

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **complete bronze reward identities and quantities implemented; hidden
probabilities remain `provisional/darkan` and `source_blocked`.**

## Period record

RuneScape Wiki `Shades of Mort'ton (minigame)` oldid `6449451`, timestamp
`2012-10-21T17:37:46Z`, states that a matching chest consumes its key and
usually gives coins plus one treasure. It identifies runes, armour, clue
scrolls, occasional swamp paste, and Fine cloth as reward families. It also
states that bronze chests yield Steel through Mithril items or an easy clue,
that every chest tier can yield Fine cloth, and that better key colours improve
reward quality. The page does not expose item-level selection weights, paste
probability, or the Ring of Wealth modifier.

OpenRS2 revision 742 (`2012-11-07`) pins every reconstructed reward identity.
Two storage-name translations are explicit rather than hidden: cache item
`1141` is `Steel helm`, while AnkiScape's owning Smithing row is `Steel med
helm`; cache item `19005` is `Scroll box (easy)`, while the settled Treasure
Trails model stores the usable `Clue scroll (easy)` directly and enforces one
clue across all tiers.

## Reconstructed table

Darkan world commit `4d72f80f3e7ad56a712b4e38653f01cedaeeb289` is the
fresh iteration-399 restoration accepted by
`memory-bank/audit/handoffs/iteration-399-shades-of-mortton-minigame.md` in the
shared Darkan project.

- `ShadeChest.java:29-35` maps bronze chests to keys `3450`-`3454` and the
  `shade_bronze_chest` set.
- `ShadeChest.java:62-89` consumes one matching key and applies
  `1.0 - keyIndex × 0.05` to the reconstructed reward roll.
- `shade_bronze_chest.json:1-174` supplies unconditional `10`-`270` coins,
  the reconstructed paste row, and four `dropOne` groups of `55`, `59`, `10`,
  and `4` slots out of `128`. The 23 item rows and all variable quantity ranges
  are copied literally into AnkiScape.
- `DropList.java:51-78` sorts non-zero chance groups by ascending rate before
  assigning roll intervals. `DropList.java:120-169` applies the modifier,
  selects one group, and selects one item uniformly inside a `dropOne` group.

These probabilities are not promoted to period facts. The accepted Darkan
handoff itself classifies chest probabilities, Ring of Wealth behavior, and
equipment modifiers as `source_blocked`. AnkiScape retains the existing
`provisional/darkan` label and the already disclosed one-in-four optional-paste
abstraction because Darkan's unconditional paste contradicts the period page's
"sometimes" wording.

## Implementation

- Replaced the former four-item sample with all 23 reconstructed bronze-chest
  rewards and exact quantity ranges.
- Preserved Darkan's ascending chance-group order and the three currently live
  low-bronze key modifiers.
- Reused Treasure Trails' central clue-output filter, so a chest cannot create
  a second clue while one is held or active.
- Registered the previously missing `Black dagger (p)` and `Mithril dagger (p)`
  equipment items with exact cache IDs and normalized pre-cutoff source art.
- Regenerated the cutoff Grand Exchange table. Buying-limits oldid `6457777`
  pins both poisoned daggers at `100`, so neither joins the unresolved market
  whitelist; their guide prices continue to use the existing cache-value
  fallback because no cutoff Exchange price row survived in the harvest.
- Removed the ghost `Steel axe` output; the reconstructed row is cache item
  `1353`, `Steel hatchet`, which already has a canonical item and asset.

Higher shade, key, and chest tiers remain separate data-depth work. This slice
adds no new UI, gameplay clock, save field, design choice, or placeholder.

## Verification

- Focused pure, integration, registry, market, write-through, and asset checks:
  `73` tests pass.
- Focused real offscreen Qt: `4` tests pass on the established activity and
  asset surfaces.
- Full discovery: `3,914` tests pass in both lanes, with `480` expected plain
  skips and `3` intentional Qt skips.
- Documentation audits `529` Markdown and `431` HTML files. Test quality has
  zero hard issues across `3,880` tests in `177` files.
- Reachability remains at `1,511` actions, with `2,287` reachable items and the
  known `168` orphan inputs / `188` blocked actions. The complete bronze table
  introduces no new orphan.
- Compilation, tracked JSON, diff whitespace, deterministic asset fetching,
  asset normalization, and worktree safety pass.
