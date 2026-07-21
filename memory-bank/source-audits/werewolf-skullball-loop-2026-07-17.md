# Werewolf Skullball at the pre-EOC cutoff

Date: 2026-07-17

Status: **superseded by the 2026-07-21 closure below; horizontal implementation
is source-ready with one disclosed action-native scoring translation.**

## Pinned evidence

The literal wikitext of `Werewolf Skullball`, oldid `6488093`,
`2012-10-28T12:40:39Z`, establishes:

- entry requires level 25 Agility, completion of `Creature of Fenkenstrain`,
  and a worn Ring of Charos;
- the player moves a skull through ten ordered goals;
- `Tap`, `Kick`, and `Shoot` move it one, four, and nine squares respectively;
- route choice affects completion time;
- finishing in under four source minutes awards 750 Agility XP; and
- the period article describes an approximate loss of 7–8 XP for each three
  seconds beyond four minutes.

Source:

- <https://runescape.wiki/w/Werewolf_Skullball?oldid=6488093>

The revision was resolved and inspected as literal wikitext with
`tools/wiki_parity.py`. The approximate XP-decay prose is not an exact formula.
The wider Agility source ledger also records a conflicting ten-square `Shoot`
claim from the period general Agility page; this focused page's nine-square
identity remains pinned, while the conflict stays explicit.

## Owner-settled AnkiScape grouping

The entire ten-goal run resolves as one atomic successful review. It does not
persist ten goal steps or replay a source timer. Before the run the player
chooses:

- **Careful**, favoring tap/kick precision over route efficiency;
- **Fast**, favoring long shots and efficient routing; or
- **Balanced**, using a mixed route.

Casual exposes those three choices and resolves the corresponding bounded route.
Advanced may specify the exact tap/kick/shoot plan, but that plan still resolves
in one review. The result line names the route character, notable mistakes or
bounces, and final XP.

The source elapsed-time reward becomes an action-native route-efficiency score.
It may use chosen movement mix and any independently sourced route-error
outcomes, but it never reads the wall clock or treats answered cards as elapsed
seconds. The implementation must not run a hidden tile simulation; it evaluates
only the selected bounded route representation.

Only a successful review commits the run. An `Again` before resolution advances
ordinary world state but does not create a partial skullball course. Undo
reverses the entire XP and activity result together.

The source level, quest, and equipped-ring gates remain ordinary requirements.
Travel to the course is scene text inside the Activity and creates no persistent
location or transportation system.

## Still open for source harvest

- Reconcile the nine/ten-square `Shoot` conflict through independent
  period-lineage evidence.
- Resolve the exact XP-decay curve or retain it as `source_blocked`; do not turn
  the article's “about 7–8” prose into a fabricated exact table.
- Determine whether any cutoff route-error or failure roll exists. If none can
  be sourced, route presets affect efficiency only.
- Corroborate the maximum XP, entry gates, and movement distances.
- Fetch period route, skullball, and result assets.

## 2026-07-21 source closure and implementation translation

This section supersedes the older open-work bullets above. It does not reopen
the owner-settled atomic-run design.

The focused cutoff page remains the strongest activity source. Its literal
wikitext supplies the complete recommended route and two explicit alternatives,
not merely the movement distances. Those sequences produce the three bounded
presets now used by AnkiScape:

| Preset | Source-line identity | Moves | Tap / Kick / Shoot | Award |
|---|---|---:|---:|---:|
| Careful | recommended route with the slower fifth-goal kick-and-tap line | 30 | 14 / 5 / 11 | 750 XP |
| Balanced | complete recommended route | 29 | 13 / 4 / 12 | 750 XP |
| Fast | alternate tenth-goal wall-bounce line | 27 | 10 / 4 / 13 | 750 XP |

All three are described by the page as sub-four-minute routes and therefore use
the sourced maximum. The focused page's nine-square `Shoot` value is retained
because it owns the complete route table; the general Agility oldid `6477884`
ten-square summary remains an explicit unresolved source conflict rather than a
second gameplay rule.

No cutoff activity source, cache convergence, or server implementation recovered
a miss/failure roll. This is an explicit omission, not proof that a historical
player could never make a mistake. The horizontal activity therefore resolves
the selected plan deterministically and lets route efficiency, not fabricated
RNG, distinguish policies.

The cutoff page's “about 7–8 XP” per three seconds is still not an exact formula.
AnkiScape therefore labels its Advanced scoring rule as an abstraction: the
source-derived 30-move preset ceiling maps to the full 750 XP, and every selected
move beyond that ceiling removes 8 XP. The chosen upper endpoint is conservative
and disclosed. It never reads wall time, treats reviews as seconds, or simulates
tiles. This bounded translation is implementation policy, not a claim about the
historical server formula.

### Entry item and equipment evidence

`Ring of charos`, oldid `6359534`, timestamp
`2012-10-06T21:47:17Z`, establishes the wearable ring and its activated variant:

- <https://runescape.wiki/w/Ring_of_charos?oldid=6359534>

OpenRS2 caches `727` and `742` preserve item identities `4202` (Ring of charos),
`6465` (Ring of charos (a)), and `15016` (Ring of charos (a)(i)), each with the
`Wear` option. The local Darkan item-config snapshot preserves their equipment
blocks at
`/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:45018`,
`:72392`, and `:177956`; each uses equipment slot `12`, the ring slot. The
unactivated ring is already the `Creature of Fenkenstrain` reward in
`quest_catalog_generated.py:8847`.

### Period assets

`tools/fetch_werewolf_skullball_assets.py` resolved and normalized four cutoff
files to RGBA sprites no larger than 64 px. Immutable metadata is recorded in
`assets_provenance.json`:

- Werewolf Skullball icon: `2010-02-16T14:19:09Z`;
- Ring of charos: `2011-11-27T18:10:40Z`;
- Ring of charos (a): `2010-11-02T03:11:22Z`; and
- Ring of charos (a)(i): `2011-11-27T18:12:20Z`.

No result-interface screenshot is needed for the compact Activities card. The
period activity and item sprites cover every visual identity introduced by this
slice.
