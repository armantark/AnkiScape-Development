# Werewolf Skullball at the pre-EOC cutoff

Date: 2026-07-17

Status: **period structure pinned; atomic run and route presets owner-settled;
exact decay and route-error behavior remain open.**

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
