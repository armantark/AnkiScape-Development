# 05: Bank run, rest and grave recovery spend play time

**What to build:** A Combat bank run (ordinary and quest) takes 100 ticks, rest 180 ticks and grave recovery 300 ticks at every speed. The remaining ticks of the card pay first, and play continues in the same card. A kill that needs a bank run no longer ends its card. Combat joins the Agility travel profile at the weak tier with the weight effect and run energy credit. The bank run value is a Placeholder with the repository's marker. A saved delay in the old form finishes at the next card. The cadence contract, `systemPatterns.md` and the Agility contract's Combat line change to match. Grill answers 12, 14, 18 and 19.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] `tests/pace/rates/rate_property.py` runs Combat with banking on, and it passes at 1x and 10x.
- [x] A played fight at 1x, 10x and 20x: a 10x card spends 60 ticks across a bank run when no danger stop occurs; a 1x bank run costs 17 cards.
- [x] Agility 99 costs about 93 ticks; a due trip is the only new RNG draw; the bank transaction always completes.
- [x] Ordinary combat still ends the encounter at a bank run; quest combat still keeps enemy LP.
- [x] A queue entry handed over after a bank run gets the remaining ticks.
- [x] The report holds the XP-per-card table for the four `facts-combat.md` fixtures at 1x, 10x and 20x beside the old values, measured with the same seed and script (`/tmp/pass20-facts/combat/measure.py` adapted, kept in the evidence folder).
