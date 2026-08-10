# Tokkul shops and Uncut onyx acquisition — 2026-08-09

## Scope

This slice activates Tokkul as the existing inventory currency for the three
ordinary TzHaar shops and closes the acquisition root for `Uncut onyx`. It
does not add a second shop runtime, a separate currency wallet, or an invented
onyx dispenser.

## Period evidence

RuneScape Wiki [Uncut onyx oldid
6570299](https://runescape.wiki/w/Uncut_onyx?oldid=6570299), dated
2012-11-18T03:01:05Z, identifies item `6571` as members-only, tradeable, and
non-stackable. Its ordinary purchase source is TzHaar-Hur-Lek's Ore and Gem
Store for exactly `2,700,000 Tokkul`. The same revision states that cutting it
requires level 67 Crafting and awards 167.5 Crafting XP, matching the existing
live `cut_onyx` recipe.

The final pre-EOC shop pages pin all three stock tables:

- [TzHaar-Hur-Lek oldid
  6438736](https://runescape.wiki/w/TzHaar-Hur-Lek?oldid=6438736), dated
  2012-10-18T21:45:33Z: Tin ore `30` Tokkul / stock `5`, Copper ore `30` / `5`,
  Iron ore `25` / `2`, Uncut sapphire `48` / `1`, Uncut emerald `97` / `1`,
  Uncut onyx `2,700,000` / `1`, and Onyx bolt tips `13,000` / `50`.
- [TzHaar-Hur-Tel oldid
  6393151](https://runescape.wiki/w/TzHaar-Hur-Tel?oldid=6393151), dated
  2012-10-13T04:36:48Z: the eight existing equipment rows cost `375`,
  `60,000`, `67,500`, `37,500`, `52,500`, `45,000`, `75,000`, and `90,000`
  Tokkul, each with stock `10`.
- [TzHaar-Mej-Roh oldid
  6393148](https://runescape.wiki/w/TzHaar-Mej-Roh?oldid=6393148), dated
  2012-10-13T04:35:31Z: elemental runes cost `26` Tokkul, Mind and Body runes
  cost `24`, Chaos runes cost `210`, and Death runes cost `465`, with stocks
  `1000`, `1000`, `1000`, `1000`, `1000`, `1000`, `300`, and `100`.

Every row in those shop tables says the shop does not buy the item from the
player. The cutoff Uncut onyx page independently notes that selling items to
TzHaar shops was removed in 2009. The three shops are therefore player-buy
only. The cutoff tables supersede four later cache-derived prices: Uncut
sapphire `37 → 48`, Uncut emerald `75 → 97`, Onyx bolt tips `13,500 → 13,000`,
and Mind rune `26 → 24`.

## Existing currency sources

Tokkul was already a registered stackable inventory item with live earning
routes. `TzHaar Fight Cave` oldid `6584235` pins the Fight Caves reward, and
the existing activity awards `16,064` Tokkul for a completion. `TzHaar Fight
Pit` oldid `6516239` pins its last-standing Tokkul settlement. The ordinary
TzHaar-Ket combat table also has a live `100–2,000` Tokkul drop at `69/128`
from the audited 2011Scape definition. The old shop lock therefore described
stale runtime state rather than a missing currency mechanic.

## AnkiScape translation

The generated shop catalog now treats item `6529` exactly like Coins for
currency availability, while preserving Tokkul as a normal stackable inventory
item. Only the three TzHaar shops use Tokkul, and only those three receive the
period buy-only override. Purchase, limited stock, review-driven restock,
inventory debit, history, persistence, and atomic undo all reuse the existing
shop runtime and UI.

The generator owns the four cutoff price overrides and their citations. A
focused regeneration mode applies currency activation to AnkiScape's pinned
shop snapshot without importing unrelated changes from the actively restored
Darkan checkout. This keeps the generated catalog attributable and prevents a
currency slice from silently refreshing unrelated shop content.

The existing `crafteditems/uncut_onyx.png` and `crafteditems/onyx.png` assets
are tightly cropped at `22×22` and `21×23`; no visual asset changed. The five
onyx Crafting rows no longer display their obsolete input-starved note.

## Explicit omissions

- Fight Kiln rewards and alternative rare sources are not needed to close the
  ordinary shop route and remain owned by their activity systems.
- Selling to TzHaar shops is not approximated with later game behavior.
- No wall-clock shop restock, travel duration, or persistent TzHaar location is
  added. The established review-driven shop market remains the translation.
- Trading sticks and Fist of Guthix tokens remain locked or hidden. Activating
  Tokkul does not generalize availability to every non-coin currency.
- No placeholder value is introduced.

## Verification

- One hundred forty-four focused generator, catalog, transaction, Crafting,
  registry, reachability, buy-only, and undo tests pass. A real offscreen Qt
  test searches for Uncut onyx, renders the Tokkul wallet, buys the item, and
  observes the inventory mutation.
- Reachability improves from `1,549 actions / 2,397 reachable items / 124
  orphan inputs / 129 blocked actions` to `1,549 / 2,413 / 117 / 118`: sixteen
  item paths become reachable and eleven actions stop being blocked.
- Both onyx sprites have full-canvas alpha bounds, and the complete
  `crafteditems` family reports zero trimmable small sprites.
- Full plain discovery passes `4,014` tests in `278.827` seconds with `489`
  expected environment skips. Full real offscreen Qt discovery passes the same
  `4,014` tests in `612.562` seconds with three intentional skips.
- Documentation audits `547` Markdown and `431` HTML files. Test quality finds
  zero hard issues across `3,979` tests in `181` files. Compilation, JSON,
  deterministic regeneration, diff, and worktree-safety gates pass. The
  reachability tool intentionally exits nonzero while known orphans remain;
  its exact report is the improved ledger above, not a closure failure.
- Native Anki Computer Use could not attach to the already-running app by
  either `Anki` or `net.ankiweb.launcher`; both reads returned `Computer Use
  server error -10005: timeoutReached`. No native interaction is claimed.
- Manual acceptance is to earn or seed `2,700,000 Tokkul`, open Shop, search
  `Uncut onyx`, buy the single stock item, verify Tokkul reaches zero and the
  item enters inventory, confirm Sell is unavailable at that shop, then undo
  the purchase and verify both inventory values and stock are restored.
