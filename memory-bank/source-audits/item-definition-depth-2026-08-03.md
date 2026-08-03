# Exact item-definition depth pass

Date: `2026-08-03`.

Scope: player-visible item identities, model recolours, and equipment bonuses
that the dated client cache can settle. This pass does not promote item configs
into evidence for server rolls, reward formulas, drop rates, or timers.

## Reader

`tools/query_openrs2_cache.sh <cache> --id <id> [id ...]` now prints the exact
item name, inventory model, model recolours, texture replacements, sprite
recolour indices, 18-cell bonus array, stackability, exchangeability, and
inventory options. It uses Darkan
core `2.0.5`, SHA-256
`bfaf99f7bb04a55418a9aeb07a01f2724034692637b435a87df4f3f4b029e3fe`,
against a read-only extracted OpenRS2 disk cache. Output preserves the requested
ID order and uses `Arrays.toString`, so empty arrays and cell order stay
explicit.

The public Darkan constants map bonus cells `0-10` to attack/defence stats,
`14` to melee Strength, `15` to Ranged Strength, `16` to Prayer, and `17` to
Magic damage. AnkiScape does not model the cache's cells `10-13` for Summoning
defence and damage absorption, so those cells remain out of the equipment
projection rather than being folded into another stat.

## Temple Trekking reward tokens

OpenRS2 build `727`, dated `2012-07-24`, contains three otherwise identically
named `Reward token` rows with model `14131` and the same Claim-reward/Destroy
options:

| ID | model recolour row | colour identity |
|---:|---|---|
| `7774` | no replacement; the model's original packed-HSL colours remain | yellow |
| `7775` | `9164,6742 -> 571,64167` | red |
| `7776` | `9164,6742 -> 42958,42460` | blue |

The colour labels are a bounded client-data inference, not a server claim. In
the client's packed-HSL layout, the two `7775` target hues sit at the red wrap
and both `7776` target hues sit in the blue band; `7774` leaves the original
yellow/ochre model untouched. The three pinned pre-cutoff file revisions in
`assets_provenance.json` independently provide the labelled red, yellow, and
blue appearances. Together they settle the one-to-one item mapping as blue
`7776`, yellow `7774`, red `7775`.

The former live mapping swapped blue and yellow. It is corrected, and
`temple_trekking.token_color_item_ids` is retired from the placeholder register.
Token scoring and reward-quantity distributions are server-owned and remain
registered placeholders.

## Goblin Raids equipment

OpenRS2 builds `741` (`2012-11-04`) and `742` (`2012-11-07`) agree on the four
near-cutoff item identities. Rev-741 exact rows pin:

| item | ID | projected nonzero bonuses |
|---|---:|---|
| Goblin cower shield | `25350` | Magic attack `-8`, Ranged attack `-2`; Stab/Slash/Crush/Magic/Ranged defence `13/15/14/-1/14` |
| Raider axe | `25351` | Stab/Slash/Crush attack `-2/18/13`; Ranged defence `-1`; melee Strength `22` |
| Raider chainbody | `25352` | Magic attack `-15`; Stab/Slash/Crush/Magic/Ranged defence `20/29/35/-3/22` |
| Raider shield | `25353` | Magic/Ranged attack `-6/-2`; Stab/Slash/Crush/Magic/Ranged defence `14/15/13/0/14` |

All four rows are non-stackable and non-exchangeable. The live rows previously
used unrelated `202xx` identities, marked the Raider set tradeable, and
flattened every bonus to zero. The IDs, trade rules, and bonus projections are
corrected. The registered `goblin_raids.raider_set_bonuses` placeholder is
retired. Acquisition order, the axe's Attack requirement, the cower shield XP
effect, reward chances, and all server mechanics remain owned by their existing
sources and contracts.

## Explicit omissions

- Dominion Tower reward identities remain source-blocked. Its prior exact-name
  search found no matching rev-742 rows, and model fields cannot recover an
  item whose ID is unknown.
- Item models do not establish a server reward selector, probability, quantity,
  trade rule, equip requirement, attack speed, or special effect.
- This pass did not render cache models or replace the already pinned period
  PNG assets. No UI or asset file changes were needed.

## Regression map

- `tests/test_openrs2_items.py` pins the rev-727 token and rev-741 Goblin
  equipment definition rows.
- `tests/test_temple_trekking.py` pins the corrected colour-to-ID mapping.
- `tests/test_goblin_raids.py` pins all four equipment IDs and complete
  AnkiScape bonus projections.
- `tests/test_placeholder_register.py` rejects either retired placeholder if it
  reappears only on one side of the code/register boundary.
