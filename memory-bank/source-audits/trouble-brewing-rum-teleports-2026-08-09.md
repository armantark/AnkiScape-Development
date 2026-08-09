# Trouble Brewing rum teleports

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **verified and implemented.**

## Period record

`Honest Jimmy's House of Stuff`, oldid `6393015`, timestamp
`2012-10-13T04:08:35Z`, lists two distinct `Rum (Trouble Brewing)` rows at
`2` Pieces of Eight each. The rows use the red and blue rum images and each
have stock `30`.

`Rum (Trouble Brewing)`, oldid `6088748`, timestamp
`2012-08-14T02:58:20Z`, states that:

- the rum is available only from Honest Jimmy for `2` Pieces of Eight;
- it is used to teleport back to Trouble Brewing;
- it is drunk to trigger the effect; and
- red and blue are the only two colours and have no mechanical difference.

The cutoff file pages preserve both source sprites: red oldid `6417276` and
blue oldid `6417275`, both dated `2012-10-15`. The fetched immutable image
revisions are from `2011-11-27` and therefore predate the cutoff.

Sources:

- <https://runescape.wiki/w/Honest_Jimmy%27s_House_of_Stuff?oldid=6393015>
- <https://runescape.wiki/w/Rum_(Trouble_Brewing)?oldid=6088748>
- <https://runescape.wiki/w/File:Rum_(red).png?oldid=6417276>
- <https://runescape.wiki/w/File:Rum_(blue).png?oldid=6417275>

## Item definitions

OpenRS2 cache `544`, RuneScape revision `742`, dated `2012-11-07`, pins two
non-stackable, non-exchangeable items named `Rum`: IDs `8940` and `8941`.
Both expose `Drink` and have identical zero-bonus rows. Their only decoded
difference is the bottle recolour. Preserved wiki item metadata maps `8940` to
red and `8941` to blue; the cutoff family page and files independently prove
that both colours existed. Authentic game-main `data/cfg/items.yml:96446-96457`
corroborates both IDs, their shared name, non-tradeable state, and zero weight.

## AnkiScape translation

- The Bank needs stable unique keys, so the two source items both named `Rum`
  are disambiguated as `Red rum` and `Blue rum`. This is storage/UI naming,
  not invented content.
- Buying either row uses the existing Pieces-of-Eight purchase and direct-undo
  path. Drinking consumes one bottle and records the sourced destination as
  `Trouble Brewing`; the app does not invent global tile or wall-clock state.
- A live Trouble Brewing match blocks Bank use of the bottle because the
  settled activity uses a closed temporary inventory. The Bank action is
  disabled with that reason instead of failing after a click.
- Both rows show the compact `PoE` price, a one-use teleport tooltip, and their
  normalized period sprites. The Bank action says `Drink`, names the
  destination and consumption, and uses the shared direct-action undo seam.
- Kimi K3 and Fable independently reviewed the new surfaces. Accepted findings
  add the purchase tooltip, a `24 × 24` combo icon box, visible Bank-menu
  tooltips, explicit consumption text, mid-match disabled state, and clearer
  `Packed`/`Opponent` scoreboard labels. Neither review is a native Anki
  appearance claim.

## Explicit omissions

- The source page does not pin the exact destination tile, animation, dialogue
  line selection, or server handler. Those presentation details are not needed
  in AnkiScape's locationless direct-action model.
- The death-like visual sequence is not modeled; it has no separate settled
  mechanic or persistent consequence.
- The medium-clue service was completed under its superseding 2026-08-09 audit;
  `The stuff` remains a separate queue item.

## Verification

- Focused pure, integration, registry, storage, equipment, undo, and asset
  checks: 210 tests pass.
- Focused real offscreen Qt: four checks pass for the reward selector, both Bank
  actions, tooltip visibility, active-match gating, and asset normalization.
- Full plain discovery: 3,919 tests pass with 481 expected skips.
- Full real offscreen-Qt discovery: 3,919 tests pass with three intentional
  skips.
- Documentation: 531 Markdown and 431 HTML files pass the docs audit.
- Test quality: zero hard issues across 3,885 tests in 177 files.
- Reachability: 1,511 actions, 2,315 reachable items, 168 known orphans, and
  188 known blocked actions.
- Compilation, tracked JSON parsing, diff hygiene, deterministic asset fetching,
  asset normalization, and worktree safety pass.
