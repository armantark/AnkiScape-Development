# Darkan quest agent handoff — 2026-07-18

This Slayer slice did not implement or edit quest content.

The current generated Jungle Potion objectives still need the Darkan quest
parity pass to replace the unreachable clean-herb/blocker sequence. Existing
source work already recovered the relevant ordinary shape: Druidic Ritual and
Herblore 3 to start, five sequential herb stages, 2.5 Herblore XP per clean
herb, and 775 Herblore XP plus one quest point on completion. If the quest
runtime cannot award per-stage XP yet, add that as a quest-owned schema and
migration rather than special-casing Slayer or Combat.

## Mogre miniquest

Mogres are now source-closed on the Slayer/Combat side but intentionally remain
dependency-blocked. Please add the period Mogre miniquest as quest-owned
one-time state with the exact completion ID `skippy_and_the_mogres`.

Primary cutoff source:
`Mogre (lore activity)`, oldid `6070158`,
`2012-08-10T03:44:02Z`.
Supporting NPC source: `Skippy`, oldid `6274860`,
`2012-09-21T07:00:52Z`.

The smallest faithful review-native chain is:

1. require Cooking 20;
2. consume one Bucket of water to sober Skippy;
3. consume one Nettle tea;
4. consume one Hangover cure made from Chocolate dust, a Bucket of milk, and
   Snape grass; and
5. set `skippy_and_the_mogres` complete, granting the ability to lure and kill
   Mogres at Slayer 32.

There is no enemy, ordinary XP reward, or quest-point award in the cutoff
reward list. Do not add a Combat target or Slayer special case in the quest
patch. The complete downstream contract, exact source revisions, Darkan stats,
drops, lure transaction, and missing unique assets are recorded in
`memory-bank/source-audits/slayer-mogre-combat-2026-07-18.md`.
