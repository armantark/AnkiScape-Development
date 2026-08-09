# Trouble Brewing cosmetic reward catalog

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **complete 27-row cosmetic and flag catalog implemented.** The two rum
teleports were completed in the superseding
`trouble-brewing-rum-teleports-2026-08-09.md` audit; medium-clue redemption and
`The stuff` remain separate mechanic-depth slices.

## Period record

The current RuneScape Wiki revision API identifies the last pre-cutoff
`Trouble Brewing` revision as oldid `6579342`, timestamp
`2012-11-18T20:43:05Z`, and the last pre-cutoff `Honest Jimmy's House of Stuff`
revision as oldid `6393015`, timestamp `2012-10-13T04:08:35Z`. Earlier project
notes used stale migrated IDs `6573931` and `6399561`; those numbers now resolve
to unrelated revisions and are superseded for this family.

Honest Jimmy oldid `6393015` lists the shop in exact source order:

- seven colour sets — Blue, Green, Red, Brown, Black, Purple, and Grey — each
  with a `100`-Piece naval shirt, `50`-Piece tricorn hat, and `100`-Piece navy
  slacks; and
- Cutthroat and Guilded smile flags at `200`, Bronze fist at `300`, Lucky shot
  at `400`, Treasure at `500`, and Phasmatys at `600` Pieces of Eight.

The same revision separately lists `The stuff` at `5` and both rums at `2`, and
states that a medium clue costs `5,000` Pieces. Those rows are real but require
their own mature-ale, teleport, and Treasure Trails action semantics, so this
catalog slice does not flatten them into inert inventory items.

Sources:

- <https://runescape.wiki/w/Trouble_Brewing?oldid=6579342>
- <https://runescape.wiki/w/Honest_Jimmy%27s_House_of_Stuff?oldid=6393015>

## Item definitions

OpenRS2 rev-742 (`2012-11-07`) pins the 27 client identities: shirts
`8952`–`8958`, hats `8959`–`8965`, flags `8966`–`8971`, and slacks
`8991`–`8997`. Every row is non-stackable and non-exchangeable, exposes Wear or
Wield, and has an all-zero 18-field bonus array.

The authentic 2011Scape `data/cfg/items.yml` independently supplies the
equipment blocks. Shirts use body slot `4`, hats head slot `0`, slacks leg slot
`7`, and flags weapon slot `3`. Flags use weapon type `14`; Guilded smile has
attack speed `2`, while the other rows use `4`; only Phasmatys carries
two-handed equip type `5`. AnkiScape translates those numeric slots into its
existing `body`, `head`, `legs`, and `weapon` names without inventing bonuses.

## Implementation boundary

- All 27 rows use the existing atomic Pieces-of-Eight purchase and direct-undo
  path. There is no stock timer or wall-clock state.
- The established reward combo remains the shop surface. Every row has a
  normalized, tight-cropped pre-cutoff sprite and shows that sprite in the
  selector; every price includes the compact `PoE` currency unit. Bank and
  equipment reuse the same item registry path.
- Expanding the one-row selector exposed a real stale-state bug: changing the
  selected reward did not recompute Buy availability. The selector now refreshes
  through the same change-boundary pattern as Castle Wars.
- No schema field, placeholder, gameplay policy, or owner design choice was
  added.

Kimi K3 and Fable independently found the same concrete taste defect: the new
multi-row selector initially showed bare price numbers. The accepted `PoE`
suffix keeps the compact row width while making all 27 prices unambiguous.
Both otherwise found the icon sizing, dark-mode behavior, control state, and
card density clean; neither review claims native Anki appearance.

## Explicit omissions

- The period rums are destination teleports, not ordinary drinks; their
  implementation is verified in the superseding rum-teleport audit.
- The medium clue is a direct shop service and must obey the settled one-clue-
  total rule.
- `The stuff` modifies mature-ale production and belongs with the brewing
  action family.

These are three separate source-ready mechanic slices, not missing values in
the cosmetic catalog.

## Verification

- Focused pure, integration, write-through, equipment, registry, and asset
  checks: 141 tests pass.
- Focused real offscreen Qt: four checks pass, including icon presence,
  selection-state refresh, and purchase/undo behavior.
- Full plain discovery: 3,916 tests pass with 480 expected skips.
- Full real offscreen-Qt discovery: 3,916 tests pass with three intentional
  skips.
- Documentation: 530 Markdown and 431 HTML files pass the docs audit.
- Test quality: zero hard issues across 3,882 tests in 177 files.
- Reachability: 1,511 actions, 2,313 reachable items, 168 known orphans, and
  188 known blocked actions.
- Compilation, tracked JSON parsing, diff hygiene, deterministic asset-fetch
  dry run, asset normalization, and worktree safety pass.
