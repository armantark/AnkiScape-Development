# Cured yak-hide service audit — 2026-08-09

## Scope and verdict

This slice closes the authentic source for `Cured yak-hide`. Raw `Yak-hide`
and Coins already have live acquisition routes. The two existing yak-hide
armour recipes were blocked only by the absent curing service.

**Verdict:** Thakkrad Sigmundson cures one Yak-hide into one Cured yak-hide for
5 Coins. The service becomes available at stage 5 of The Fremennik Isles, when
the player prepares for the troll fight. The existing shop-service transaction
supports quantity selection, inventory limits, persistence, history, and
direct undo. No placeholder is necessary.

## Period evidence

### Cured yak-hide

- RuneScape Wiki `Cured yak-hide`, oldid `5967010`, timestamp
  `2012-07-20T16:33:04Z`:
  <https://runescape.wiki/w/Cured_yak-hide?oldid=5967010>.
- The cutoff page says that the player takes Yak-hide to Thakkrad Sigmundson on
  Neitiznot and pays 5 Coins for each hide.
- The same page pins one cured hide for the level-43 legs recipe, two for the
  level-46 body recipe, and 32 Crafting XP for either product. Those recipes
  were already live and are not changed here.

### Provider and access point

- RuneScape Wiki `Thakkrad Sigmundson`, oldid `6225987`, timestamp
  `2012-09-09T22:18:56Z`:
  <https://runescape.wiki/w/Thakkrad_Sigmundson?oldid=6225987>.
- The cutoff page places Thakkrad on Neitiznot and repeats the 5-Coin price.
  It says the player must reach the fight-preparation point in The Fremennik
  Isles. After quest completion, `Craft-Goods` remains available.
- RuneScape Wiki `The Fremennik Isles`, oldid `6540919`, timestamp
  `2012-11-07T09:46:34Z`, places this transaction in the stage-5 preparation:
  <https://runescape.wiki/w/The_Fremennik_Isles?oldid=6540919>.

### Item identity

OpenRS2 revision 742 pins these item definitions:

| ID | Item | State |
| ---: | --- | --- |
| 10818 | Yak-hide | Non-stackable, exchangeable, `Drop` |
| 10820 | Cured yak-hide | Non-stackable, exchangeable, `Craft`, `Drop` |

The existing normalized Cured yak-hide sprite is a period upload from
`2010-10-08T03:50:50Z`. No asset replacement is necessary.

## Product translation

- `thakkrad_cure_yak_hide` is an instantaneous, batchable shop service.
- Each unit consumes one Yak-hide and 5 Coins and produces one Cured yak-hide.
- A numeric quest-stage gate extends the existing quest access rule. Progress
  5 or quest completion unlocks the service; earlier progress remains locked.
- The generated 274-shop snapshot remains pinned. `--services-only` adds this
  service without refreshing unrelated Darkan shop data.
- The route increases the graph from 1,549 to 1,550 actions. It raises
  reachable items from 2,421 to 2,423 and reduces both orphan inputs and
  blocked actions from 112/113 to 111/111.

## Explicit omissions

- This slice does not add another Yak-hide source, alter the quest stages, or
  change the existing armour recipes.
- The instant provider transaction represents the source `Craft-Goods`
  service. It does not consume review actions or use the gameplay clock.
- The distinct quest-gated Emerald-lens route found during qualification is
  recorded in `codex-briefs/darkan-quest-handoff-emerald-lens-2026-08-09.md`.
  The Darkan quest lane owns that change.

## Acceptance contract

- Progress 4 of The Fremennik Isles must remain locked.
- Progress 5 and quest completion must unlock the service.
- Quantity must clamp to both available hides and available Coins.
- Undo must restore all input, output, and currency quantities.
- The Shop UI must show the provider, period icon, exact conversion, and live
  quantity preview.
- Reachability must name `Shop service:thakkrad_cure_yak_hide` as the route.
