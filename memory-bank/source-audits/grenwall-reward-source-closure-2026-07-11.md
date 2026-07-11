# Grenwall Reward Source Closure — 2026-07-11

## Verdict

The independent Grenwall slice is source-blocked, not implementation-ready.

Pinned RuneScape Wiki revision `6196272` (`2012-09-05T01:57:26Z`) proves the period target identity and broad reward contract: level 77 Hunter, 1,100 Hunter XP, 18–21 Grenwall spikes, bones, and random grimy herbs broadly spanning irit through dwarf weed. It does not provide the exact spike distribution or herb roll probabilities.

The candidate Darkan table was introduced much later and matches a modern RS3-shaped table. It is useful as a reconstruction lead, but it cannot establish the November 2012 probabilities by itself under `pre-eoc-source-verification-standard.md`.

## Product consequence

- Keep the existing conservative fixed reward rather than silently inventing uniform rolls.
- Do not port the candidate independent herb chances yet.
- Recheck the July–November 2012 cache set and a stable high-fidelity Darkan milestone when either exposes literal table values or executable period behavior.
- The settled Hunter target/inventory model does not need another grill; this is now only a source-evidence gate.

## Evidence

- RuneScape Wiki API old revision: `https://runescape.wiki/api.php?action=query&prop=revisions&revids=6196272&rvprop=ids%7Ctimestamp%7Ccontent&format=json`
- Reconstruction lead: `game-main:data/npcs/drops/hunter/hunter_grenwall.json`
- Evidence contract: `memory-bank/pre-eoc-source-verification-standard.md`

