# Ammo return verification, 2026-11-05

Contract: points 9–12 in `followup-grill.md`. This branch implements timed ground ammunition and the approved review-HUD pickup button. Points 1–8 keep their behavior. No landing, promotion gate, remote lane, live save or profile database was used.

Every shot has a 20% break chance. No device returns a shot automatically. Ava's attractor keeps 60% of fired ammunition; the accumulator and alerter keep 72%. The remaining unbroken shots land in the persistent pile. Each shot expires 350 game ticks after landing, including on the card that reaches the deadline. Every answered card advances six ticks times speed, including Again and noncombat cards. A target change preserves the pile.

The HUD button reads `Pick up ammo (N)`, shows only for a worn ranged weapon with compatible ammunition, and disables at zero. Pickup adds matching ammo to the worn stack and other types to the Bank, at zero cards and ticks. Review undo and direct-action pickup undo restore the pile, counts and event log. Each shooting card records one line with fired, broken and landed counts; each pickup records its count.

## Checks run

```sh
python3 run_tests.py tests.pace.test_ground_ammunition tests.pace.test_ammunition_pack tests.pace.test_ammunition_hud tests.integration_smoke.test_ammunition_undo tests.test_review_strip tests.test_review_hud tests.test_combat_logic tests.test_runtime_actions tests.integration_smoke.test_quest_combat tests.combat.test_quest_auto_flee tests.combat.test_quest_combat_placeholders tests.test_combat_quest_gate
```

```text
Ran 573 tests in 10.632s

OK
```

```sh
python3 run_tests.py tests.pace.rates.test_combat_rates tests.pace.rates.test_combat_high_band_rates tests.pace.rates.test_magic_rates tests.pace.rates.test_runecrafting_prayer_construction_rates tests.pace.test_short_timers tests.pace.test_card_budget tests.pace.test_combat_chain tests.pace.test_calendar_speed
```

```text
Ran 29 tests in 429.982s

OK
```

The rate suites compare XP per game tick at 1x and 10x. They include Combat, Magic and Prayer. Bones, runes and XP rules were not changed. The later module moves preserve the same functions; the 573-test run above covers the moved functions and the final runtime/HUD code.

## Seeded return measurement

Used the real `sample_recovery` combat-card helper from `tests/pace/test_ammunition_pack.py`, at 10x for 500 cards, seed 211, with incidental item generation off. Each case fired 7,475 arrows. The final pickup spent zero ticks and cleared the pile in every case.

| Device | Automatically returned | Measured share | Available before click | Returned by click |
|---|---:|---:|---:|---:|
| None | 0 | 0.000% | 72 | 72 |
| Ava's attractor | 4,526 | 60.548% | 11 | 11 |
| Ava's accumulator | 5,433 | 72.682% | 4 | 4 |
| Ava's alerter | 5,434 | 72.696% | 4 | 4 |

The controlled 100-shot real-fight test also proves the exact split: 20 broken in each case; 80 land without a device, 20 with the attractor, and 8 with either 72% device. The fixture clicks between cards to separate recovery from expiry.

## All-speed Ranged probe

```sh
.venv-qt/bin/python tools/maintenance/prove_ranged_pace.py
```

The continuous no-device fight uses five paired seeds and 3,600 ticks at each speed, 1 through 20. Neutral bonuses keep the enlarged-HP test enemy's XP multiplier positive. The measured mean is 46,864.73566666666 XP per hour of play at 1x and 46,864.73566666667 at 20x; the largest paired difference is below 1e-8 XP per tick. This proves speed scaling in that fixture, not a census of every loadout and target.

```text
All 20 speeds: identical paired XP per tick; 5 seeds, 3600 ticks per seed and speed.
```

## Offscreen HUD check

```sh
.venv-qt/bin/python tools/maintenance/render_ground_ammunition_hud.py --output /tmp/pass21-ammo-ui
```

The renderer sets Fusion and explicit dark/light palettes, shows the parent before resizing, and processes events before captures. It checked 1000×700 and 740×560. The final `Pick up ammo (840)` has 103px of text inside 104px of content in a 118px button in every capture. No cut text was observed in the final captures. An initial bottom-row placement clipped the new button; the final button sits beside the title and preserves the chip and Bank run row.

The Impeccable detector returned `[]`. The hook's function instruments reported no violations for `consume_ammo`, `sanitize_ground_ammo` and `pickup_ground_ammo_pure`.

## Limits

Native Anki verification and frontend-taste review remain for promotion. All player state in these checks came from fixtures. An initial throwaway whole-save rate probe produced a negative XP delta and was discarded; it is not XP-rate evidence.
