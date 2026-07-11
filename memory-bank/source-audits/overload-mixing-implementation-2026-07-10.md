# Overload mixing implementation — 2026-07-10

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Pinned evidence

- `Overload` oldid 6552017, 2012-11-13, explicitly gives level 96 Herblore,
  1,000 XP, one three-dose extreme attack/strength/defence/magic/ranging
  potion plus clean torstol, one Overload (3), four returned empty vials, and
  nontradeability.
- `Extreme attack` oldid 6462605, `Extreme strength` oldid 6474549,
  `Extreme defence` oldid 6462607, `Extreme magic` oldid 6462609, and
  `Extreme ranging` oldid 6462610 independently confirm the five three-dose
  ingredients, their levels and XP, and their nontradeability. The ranging
  recipe explicitly consumes five Grenwall spikes, correcting the existing
  one-spike transcription.
- The local rev-667 item configuration corroborates Overload (3) item id 15333
  and the five three-dose extreme item identities. Its tradeable flags conflict
  with every pinned period page and were therefore not used for economy state.

Literal archived wikitext was read with `tools/wiki_parity.py`. Modern RS3 and
OSRS gameplay were not used as parity evidence.

## Implemented boundary

`finished_overload` is a normal Herblore target. One successful review consumes
the six ingredients, produces one Overload (3) plus four Vials, and awards
1,000 base Herblore XP. The generic Herblore processing path now supports
source-backed byproducts, and action telemetry records both primary and
byproduct outputs. Overload and all five extreme potion products are marked
untradeable.

The Overload consumption effect is deliberately not included in this slice.
Target-local potion selection, five damage ticks, repeated boosts, expiry, and
500-LP restoration remain in the combat potion-runtime portion of the backlog.

The item icon was fetched from the RuneScape Wiki explicitly with
`tools/fetch_assets.py --source rs3`; the tool now supports source restriction
so OSRS cannot silently satisfy a period RuneScape asset request first.
