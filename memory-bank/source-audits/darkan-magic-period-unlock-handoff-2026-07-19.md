# Darkan Magic period-unlock source handoff — 2026-07-19

This is a source-harvest handoff, not implementation verification.

The Darkan restoration loop supplied the last pre-cutoff `Magic` revision,
[`oldid 6545006`](https://runescape.wiki/w/Magic?oldid=6545006), timestamp
`2012-11-09T14:07:13Z`. Its immutable response is cached at
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/magic-oldid-6545006.json`,
SHA-256
`796217774f6b92cae60088b189c21e22daab40c6835babfbe228b58eff14f1a9`.

The revision corroborates these quest-owned unlock boundaries:

- Ancient Magicks follow Desert Treasure and require at least level 50 Magic;
- the Lunar spellbook follows Lunar Diplomacy, seven additional spells follow
  Dream Mentor, and eleven more follow Livid Farm;
- Storm of Armadyl follows Ritual of the Mahjarrat and requires level 77
  Magic; and
- Ardougne, Trollheim, Ape Atoll, and other special gates remain owned by
  their spell/quest contracts rather than generic Magic coverage.

Explicit omissions: this source does not prove Darkan quest variables, exact
component IDs, dialogue/state transitions, per-spell rune costs or base XP, or
cache identities for the unlocks. Existing AnkiScape spellbook implementation
must be assessed independently; no product code was changed from this
handoff.
