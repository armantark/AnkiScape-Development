# Thieving NPC target assets — 2026-07-19

## Scope

This audit closes the player-facing art for every live Thieving target that is
a person. It does not alter target mechanics, loot, gates, or the settled
source hierarchy in `thieving-tables-2026-07-13.md`.

Before this pass, `THIEVING_ITEM_IMAGES` projected each pickpocket's first
representative loot item, so most people displayed the same Coins sprite.
Menaphite thug and the locked Lletya elf had no image. Stalls and wall safes
are not NPCs and intentionally keep their object/output art.

## Period asset manifest

`tools/fetch_thieving_assets.py` queries RuneScape Wiki file history at or
before `2012-11-20T23:59:59Z`, normalizes visible art to a maximum 64-pixel
box, tight-crops alpha, and records each immutable file identity in
`assets_provenance.json`.

| Target ID | Historical file | Recorded revision |
|---|---|---|
| `pickpocket_man` | `Man.png` | 2012-10-06 |
| `pickpocket_farmer` | `Farmer.png` | 2011-06-26 |
| `pickpocket_female_ham` | `H.A.M. Member (female).png` | 2009-03-15 |
| `pickpocket_male_ham` | `H.A.M. Member (male).png` | 2012-10-17 |
| `pickpocket_warrior` | `Al Kharid warrior.png` | 2011-10-26 |
| `pickpocket_rogue` | `Rogue.png` | 2012-11-14 |
| `pickpocket_cave_goblin` | `Cave goblin (monster, 3).png` | 2012-04-04 |
| `pickpocket_master_farmer` | `Master Farmer.png` | 2011-11-25 |
| `pickpocket_guard` | `Guard (Varrock).png` | 2010-12-11 |
| `pickpocket_fremennik` | `Fremennik citizen.png` | 2011-01-17 |
| `pickpocket_desert_bandit` | `Bandit (Pollnivneach).png` | 2012-01-11 |
| `pickpocket_ardougne_knight` | `Knight of Ardougne.png` | 2010-09-27 |
| `pickpocket_watchman` | `Watchman (2006).png` | historical-title exception |
| `pickpocket_paladin` | `Paladin.png` | 2011-08-16 |
| `pickpocket_gnome` | `Gnome woman.png` | 2011-06-10 |
| `pickpocket_hero` | `Hero.png` | 2011-04-25 |
| `pickpocket_pompous_merchant` | `Pompous merchant chathead.png` | 2012-10-18 |
| `blackjack_menaphite_thug` | `Menaphite Thug.png` | 2011-12-14 |
| `pickpocket_lletya_elf` | `Elf warrior (Iorwerth ranger) (2010).png` | historical-title exception |

The two historical-title exceptions were uploaded after the cutoff, so their
upload timestamps are not period evidence. The file titles themselves identify
the depicted 2006 Watchman and 2010 Iorwerth models. The Watchman render matches
the red-trousered, blue-shirted model visible in the cutoff `Watchman.png`
revision; the Iorwerth render is used only on the already locked,
`source_blocked` Lletya row. Neither exception is used to infer gameplay.

## UI and normalization contract

- `THIEVING_NPC_TARGET_IDS` is the exact 17 pickpockets, Menaphite thug, and
  locked Lletya elf.
- `THIEVING_NPC_IMAGES` is existence-guarded and overrides representative loot
  art only for those IDs.
- `tools/trim_icons.py` already owns `combatenemies/`; all 19 new assets pass
  the shared tight-alpha audit without runtime cropping.
- The Qt target tree continues to render a plain `QIcon` at 28 by 28 pixels.
  Disabled/locked rows retain the ordinary Qt dimming and dark-mode-safe label
  path.

Kimi K3 and Fable independently found the first Watchman interface icon too
blocky and item-like. It was replaced by the full-body historical render.
Their remaining notes — a larger period Pompous-merchant chathead and minor
pose variance — are visible-content differences, not padded-canvas defects.
The root accepted the chathead because it is the clean pre-cutoff identity;
the available January-2013 full-body upload is post-cutoff and visibly belongs
to the newer graphical presentation.

## Verification and omissions

Coverage asserts that every person target has a distinct existing portrait,
the UI's live portrait map overrides loot art for those exact IDs, and every
small asset is alpha-tight. The integrated Qt capture was reviewed at the real
28-pixel row size. The full pure suite passes all 1,775 tests with 227
environment skips; the focused asset/metadata suite passes 68 tests and the
focused offscreen Qt Thieving surface passes both tests. The complete
offscreen Qt suite separately passes all 1,775 tests with one environment
skip.

Final acceptance used the actual macOS Anki process rather than treating the
offscreen capture as release proof. The first inspection correctly exposed a
stale, modal-blocked process still displaying Coins. After closing the modal,
fully terminating Anki, declining the unrelated add-on update prompt, and
reopening the canonical menu, all visible pickpocket rows displayed their
dedicated NPC portraits with native compositor scaling and disabled-row
dimming.

This pass does not claim:

- that the locked Lletya target's mechanics are source-closed;
- that every representative render covers every NPC ID accepted by a broad
  2011Scape family row.

Read-only Workflows run `00cec766-e4d6-4bc0-9f27-79c460fcec41` allocated a
Codex session but emitted zero tool calls and hit its explicit 900-second
timeout. The root independently reproduced the complete target and file map;
no leaf claim was used.
