# Darkan quest handoff: Olaf's Quest Brine-rat access

Date: 2026-07-18  
Owner: Darkan quest-parity thread  
Consumers: Combat / Slayer Brine rats

## Current conservative behavior

Brine rats are now playable after Olaf's Quest completion with one real Spade.
The source-defined earlier permission is recorded but not guessed: Darkan
`SlayerTaskManager.java:135-139` permits assignment at Olaf's Quest stage 40.

## Requested quest-owned output

When Olaf's Quest parity is finalized, expose a stable persisted semantic state
meaning:

> The player has reached the stage-40 Brine Rat Cavern permission.

Please expose a named state or query rather than requiring Combat to depend on
generated numeric stage layout. Combat should then accept that permission or
full quest completion while retaining the non-consumed Spade entrance gate.

## Required sabre distinction

The cutoff Brine-rat page explicitly says Brine sabres drop only after full
Olaf's Quest completion. When partial access becomes live:

- ordinary Brine-rat combat and assignment may start at cavern permission;
- the `Brine sabre` 1/512 row must remain suppressed before quest completion;
- completing the quest enables that row without changing the rest of the
  ordinary selector.

Period evidence:
<https://runescape.wiki/w/Brine_rat?oldid=6555564>.

No quest stages or rewards are requested from the Combat thread.
