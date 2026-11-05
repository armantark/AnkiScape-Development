# Pass 21 run record

The owner's notes and answers are in `spec.md`. His open questions, with what the build did by default, are in `open-questions.md`, and he asked to go over them in a grill when he asks. Worker reports, evidence and native screenshots: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass21/` on the Mac Studio.

## The 840 arrows

The owner's save held 918 Bronze arrows and 18 Iron arrows in `combat_supply_loadout.ammo`, with a Shortbow worn. The arrows were made on reviews 11607 to 11613, and a combat refill moved every compatible stack out of the Bank. Nothing was lost. Ticket 05 removes that store and migrates saves: the best type goes to the Ammunition slot, the rest returns to the Bank.

## Measurements

Real handler, Shortbow, Hill giant, 10x: 15 shots per card; the slot fell 197, 187, 176, 171, 165 over five cards, about 50% as the owner set. The rate is `/Users/ArmanTarkhanian1/Documents/ankiscape-pass21/evidence/05/recovery-rates.csv`.

## Native checks in real Anki (GPT-6.1 Terra, computer use)

`native/final-check/` and `native/check-2/` at `62cf9bbed`. Passed: queue chevrons, entry 1 remove, move highlight, the Bronze arrow plan through to 530 in the Bank, Unfired bowl with one click, Sawmill search and fee, Shop scroll and quantity, Ammunition slot count, diary deeds, 10 menu cycles. Not reached: the stale Next line, and Magic with runes in the pack, which pass through tests only. The tester lost Anki once while reopening Equipment, with no crash report and no crash output, cause unknown. The first run could not start at 02:43 ("Computer Use helper did not answer") and the retry worked by 02:52.

## Reviews

Astra found four bugs, all fixed in ticket 06: required runes counted as loot gave endless bank-only reviews; rune loot gave a restock with no travel; removal could delete an identical later entry; a non-utility successor left a minigame active. Kimi K3.1 asked for four screen fixes; three applied, and dark chevrons on a flashed row did not reproduce.

## Findings outside the tickets (not fixed)

- Long Shop card names can elide at the default width, with the full name in the tooltip.
- A Stop or hand start leaves a "Next:" HUD line until the next card.
- `tools/run_remote_tests.py` locks per Mac, so a Studio run and the MacBook loops overwrite one mirror.
- Two Opus workers ended their turn while a job ran.
