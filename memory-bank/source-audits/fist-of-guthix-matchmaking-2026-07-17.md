# Fist of Guthix matchmaking at the pre-EOC cutoff

Date: 2026-07-17

Status: **opponent selection and round-role order settled; simulated population
distribution remains an AnkiScape abstraction.**

## Pinned evidence

The literal wikitext of `Fist of Guthix`, oldid `6472973`,
`2012-10-25T21:14:22Z`, states:

- players enter a waiting room and wait for the game to match them with an
  opponent;
- the game is one-versus-one and has two rounds;
- the first-round hunter and hunted roles are assigned randomly;
- the roles swap for the second round and stats are restored; and
- players are paired randomly regardless of Combat level, including extreme
  mismatches.

Source:
<https://runescape.wiki/w/Fist_of_Guthix?oldid=6472973>, inspected as literal
wikitext with `python3 tools/wiki_parity.py content "Fist of Guthix"`.

## AnkiScape consequence

Opponent selection is not an owner design fork. Starting a match automatically
draws one simulated opponent from a period-shaped population and preserves that
opponent across both role-swapped rounds. Casual and Advanced modes cannot
choose opponent strength. The exact population distribution is not proven by
this page and must be source-audited or recorded as a labeled bounded
abstraction before implementation.
