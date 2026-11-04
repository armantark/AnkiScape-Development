# 06: The rest of a card goes to the next quest fight

**What to build:** After a quest kill, if the next quest step is also a fight, the remaining ticks go to it. A stage whose only deed is the fight advances inside the card. Non-fight steps stay one card. Grill answer 15: "B, unless it's dangerous".

**Blocked by:** 05

**Status:** built; native quest-fight carry check waits for the orchestrator

- [x] Witch's House experiment forms at 10x: a kill with ticks left continues into the next form in the same card.
- [x] A kill followed by a non-fight step ends the card.
- [x] Every danger stop still ends the card.
- [x] A seeded paired comparison of deaths per quest fight, carry on and off, over the walked quests with two or more consecutive fights. The table is in the report. If the pooled rate rises by more than four standard errors of the paired difference, do not land the carry and report the table.
- [x] The cadence contract's quest boundary line changes to match.

Verification uses the real review dispatcher in `tests/quests/test_fight_carry.py` and `tools/combat/compare_quest_fight_carry.py`. The comparison covers the finished held-item walk's 12 quests with consecutive fights, 13 chains, combat levels 20/40/60, speeds 10x/20x, and seeds 20261104–20261167: 4,992 pairs. Carry off: 880 deaths / 18,239 fights; carry on: 873 / 18,233. The pooled difference is -0.0003680420361241443 deaths per fight; paired standard error, clustered by the reused seed, is 0.0008748724471732308. The gate passes. Synthetic saves hold levels fixed and stop a chain on death or danger; they are not the owner's save.

Table, raw observations, baseline handler and light/dark Review HUD PNGs: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/evidence/06/`. Native play and full integration lanes remain with the orchestrator.
