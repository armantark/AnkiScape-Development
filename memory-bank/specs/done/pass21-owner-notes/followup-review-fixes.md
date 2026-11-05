# Pass 21 follow-up review fixes, 2026-11-05

## Behavior

- A planned entry stores one count for its alternative products. A consumer can use that count only if it accepts every possible product. Level-gated essence resolves to its current product, and Fishing uses its eligible fish. Explicit simultaneous outputs retain their individual quantities. The reviewer’s Mining 40 / Runecrafting 1 case queues and makes 10 Air runes from 10 essence without stopping.
- Reservations use declared material costs, effective spell rune costs (including staff waivers), and declared consumed alternatives such as bait. Queue edits use the same reservation. With 10 Iron ore, 40 Fire runes and one Nature rune, an already-queued Superheat Iron bar leaves no funded extra cast. Removing a Nature-rune producer removes the second unfunded cast immediately and logs its Nature-rune shortage; the remaining cast completes.
- Shots are counted where ammo is consumed, inside a scope shared by each real review step. The card logger combines those counts once per card. Activity wrappers cannot lose the counts by discarding a combat result. Normal combat and quests use that same path. The exact Pest Control case leaves 98 Bronze arrows worn, 2 landed, and `Ammo: 2 fired · 0 broken · 2 landed`. Real Castle Wars, Fight Cave and quest cards also exercise aggregation and break counts.
- Manual ammo code is unchanged. Its existing choice includes both the worn stack and Bank stock of the marked type, matching corrected contract point 2. The ammunition-pack selection covers its existing behavior tests.

## Verification

The reviewer’s exact regressions were run before the fixes and failed with `20 != 10`, `9 != 0`, both Superheat entries surviving removal, and `[] != ['Ammo: 2 fired · 0 broken · 2 landed']`.

Command:

```sh
python3 run_tests.py tests.action_queue tests.pace.test_ground_ammunition tests.pace.test_ammunition_pack
```

Output:

```text
Ran 129 tests in 86.625s

OK
```

Final combined queue, ammunition, undo and Magic selection after the batch refactor and deterministic reservation fixture:

```sh
python3 run_tests.py tests.action_queue tests.pace.test_ground_ammunition tests.pace.test_ammunition_pack tests.integration_smoke.test_ammunition_undo tests.test_magic
```

```text
Ran 176 tests in 88.181s

OK
```

Additional real-review path checks:

```sh
python3 run_tests.py tests.pace.test_ground_ammunition.ActivityAmmunitionLogTests
```

```text
Ran 3 tests in 1.650s

OK
```

Activity combat selection:

```sh
python3 run_tests.py tests.test_runtime_actions tests.test_barbarian_assault tests.test_barrows tests.test_bork tests.test_castle_wars tests.test_clan_wars tests.test_crucible tests.test_dominion_tower tests.test_dungeoneering_logic tests.test_fight_caves tests.test_fist_of_guthix_logic tests.test_goblin_raids tests.test_pest_control tests.test_phoenix_lair tests.test_shades_of_mortton tests.test_skeletal_horror tests.test_soul_wars tests.test_stealing_creation tests.test_temple_trekking tests.test_troll_invasion tests.test_tzhaar_fight_pit
```

```text
Ran 697 tests in 15.571s

FAILED (failures=1)
```

The failure is `tests.test_bork.BorkRewardTests.test_known_varrock_elite_rows_do_not_bypass_the_twelve_task_gate`, at `tests/test_bork.py:420`, `AssertionError: True is not false`. It occurs in Bork’s diary reward gate before combat; the test and its gate code are unchanged here. Isolated confirmation:

```sh
python3 run_tests.py tests.test_bork.BorkRewardTests.test_known_varrock_elite_rows_do_not_bypass_the_twelve_task_gate
```

```text
Ran 1 test in 0.002s

FAILED (failures=1)
```

The unseeded `test_removing_a_producer_keeps_only_the_count_still_funded` failed with `29 != 30` in a focused run and in a post-hook combined run (`Ran 176 tests in 88.693s`, `FAILED (failures=1)`). The failure is separate from cost reservation: an RNG `0.0` probe reproduced `28 != 30` and logged `+28 Bronze arrows · +1 Strange rock (Fletching 1) · +1 Strange rock (Fletching 2) · −30 Bronze arrowtips · −30 Headless arrows`, followed by a queue shortage stop. Strange Rocks replace crafted items. The fixture now uses the same neutral `0.5` roll as the other reservation cases. Planning around Strange Rock replacement remains an open case; this patch does not alter that gameplay rule.

After the commit hook required a simpler input-cost function, the shared batch projection was factored once and rechecked:

```sh
python3 run_tests.py tests.action_queue.test_queue_followup tests.test_magic tests.pace.test_ground_ammunition tests.pace.test_ammunition_pack
```

```text
Ran 71 tests in 7.283s

OK
```

Native Anki, every individual activity with ranged gear, and a full test suite are not proved by these selections. No profile database or player save was opened. No remote lane or promotion gate was run.
