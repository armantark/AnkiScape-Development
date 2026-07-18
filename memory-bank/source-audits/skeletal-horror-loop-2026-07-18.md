# Skeletal Horror Review-Native Contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-design loop closed; period phase, reward, and weekly cadence
settled. Exact Combat data remains implementation-source work.**

## Pinned period evidence

`Skeletal horror`, oldid `6278479` (`2012-09-21T20:50:07Z`), establishes:

- the `Rag and Bone Man` and `Fur 'n' Seek` wish lists gate the encounter;
- completing the latter requires Slayer 78;
- the first fight grants 10,000 Slayer XP and 7,000 Prayer XP;
- subsequent weekly fights grant 1,250 Slayer XP and 1,000 Prayer XP;
- after the first fight, asking the Odd Old Man to rebuild the creature enables
  the recurring weekly encounter;
- the boss begins at combat level 320, then drops to 260, 180, and 100 as its
  right arm, left arm, and tail are severed;
- a dropped limb that is not picked up and buried returns to the boss, healing
  it and restoring its stronger phase;
- death places the player's grave outside the encounter; and
- the repeat encounter has a 1-in-20 elite clue chance.

Source:

- <https://runescape.wiki/w/Skeletal_horror?oldid=6278479>

Exact stats for every phase, threshold values, attack-style transitions, and
drop handling remain implementation-source work.

## Review-native encounter

Skeletal Horror is one standard live Combat encounter with four explicit boss
phases: `320 → 260 → 180 → 100`. Each sourced threshold transition severs the
next limb, automatically picks it up, and buries it in the same combat-review
transaction. The result line names the severed and buried part.

This is faithful without overengineering. Burying is the only beneficial
follow-up and requires no item, skill, resource, or tradeoff. A contextual
`Bury / Ignore` prompt would manufacture a recurring choice whose second option
only reverses progress. The automatic burial preserves the real weakening
sequence without inventory clutter or a timer for limb reattachment.

The first victory's completion line also records the Odd Old Man rebuilding the
creature for future weeks; it does not add a compulsory dialogue button or
review. Repeat availability resets after seven simulated days, or 1,680
answered cards, never wall time.

Death or explicit abandonment clears only the current boss-phase state and
does not consume the weekly completion. Victory atomically grants the correct
first/repeat Slayer and Prayer XP, rolls the clue table, consumes the weekly
allowance, and participates in ordinary review undo.

## Owner-design closure

There is no remaining owner-facing product fork. Implementation needs the
phase Combat tables, threshold evidence, boss and limb assets, reward wiring,
quest gates, weekly eligibility, grave placement, and focused pure/runtime/Qt
coverage.
