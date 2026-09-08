# Player-roll preparation handoff

Status: static preparation only. P4 starts at `5888f215ee1bd6fb6cdc3e003a7dfe57a2f4c56a`. No tests, product imports, test discovery, gameplay, remote commands or commits ran. Parent review, runtime authorization, both full lanes, normal hooks, exact merged-tree gates and native programme acceptance remain open. The parent owns the shared MacBook mirror.

## Source boundary

One private helper shares the player attack roll and maximum-hit formulas. Both original formula branches match the helper AST. Initial ammo selection, enemy defence, Guild multiplier, accuracy assignment and the drain/RNG branch remain in the caller. Read-only formula dependencies permit preparing enemy defence before the grouped player calculation. The Guild multiplier is still initial-only: real Guild bursts exercise it once, and structural proof confirms it is absent from the helper and drain path. No impossible Guild-plus-drain enemy is used.

The complete baseline engine and candidate engine are retained. The full engine patch was applied forward and backward in a disposable directory; both recovered byte streams match their hashes. All tracked Python and JSON files except the candidate engine match the base. The inventory adds the new tests, probe and guard plus the fixed baseline and measuring-gate pins. It contains 877 entries. External host dependencies are not included; parent runtime must record those separately. The inventory hash is supplied through the command line from the independent manifest, rather than embedded into a probe that the inventory itself hashes.

The installed layout checker passed before this source freeze. Installed gate metric and layout ratchets passed. The burst changes from CCN 334 / cognitive 658 to CCN 332 / cognitive 651; the helper is 3 / 3. These are static measurements, not behavior evidence. Raw outputs and the exact static verification script are retained.

## Unexecuted verification

The focused selection contains five new test methods and three existing regression methods. The comparison plans twenty named whole-burst scenarios and records complete returned player/result values, formula observations, input nonmutation, RNG draws and generator state. Each case has explicit route expectations; an empty-prefix case must advance the seeded generator. Do not accept equality if its route assertions fail. The new focused tests independently check post-drain current-level reads, blocked drains, distinct Rigour factors, charged maximum hit and the caller's Guild multiplier.

Run the guard first after reviewing the product and operational packets. Its seven cases include wrong baseline, wrong candidate, wrong inventory pin, a wrong source map, `-O`, and `PYTHONOPTIMIZE=0`; each negative case must stop before product imports. The correct preflight hashes source only. Run the focused selection and comparison in both authorized host lanes, with zero focused skips, all twenty expected case labels, all equality and route flags true, and unchanged inventories. Use the parent-owned host runner; these commands describe the payload and do not grant mirror ownership.

```sh
python3 -B tools/combat/check_player_attack_rolls_guards.py --candidate-sha256 2b5a8a808f688cb179e59f882e58abefb1cb008d00cbca42e771d393d1c10ba8 --inventory-sha256 e13590b2376b4a916be9256e6d954950997561cf5fa3f0a705d8da0b3e9f620b > /tmp/ankiscape-player-roll-guards-2026-09-07.json
python3 -B -c 'import gzip; from pathlib import Path; Path("/tmp/ankiscape-player-roll-baseline-2026-09-07.py").write_bytes(gzip.decompress(Path("memory-bank/evidence/combat-player-attack-rolls-2026-09-07/baseline-engine.py.gz").read_bytes()))'
python3 -B run_tests.py --verbosity 2 CombatPlayerAttackRollsTest CombatLogicTest.test_cockatrice_drains_reduce_later_attacks_in_the_same_review CombatLogicTest.test_basilisk_prayer_blocks_unshielded_damage_but_not_random_stat_drain CombatLogicTest.test_aberrant_spectre_prayer_blocks_drain_but_not_stench_damage
python3 -B tools/combat/compare_player_attack_rolls.py --baseline /tmp/ankiscape-player-roll-baseline-2026-09-07.py --candidate-sha256 2b5a8a808f688cb179e59f882e58abefb1cb008d00cbca42e771d393d1c10ba8 --inventory memory-bank/evidence/combat-player-attack-rolls-2026-09-07/source-inventory.json.gz --inventory-sha256 e13590b2376b4a916be9256e6d954950997561cf5fa3f0a705d8da0b3e9f620b --output /tmp/ankiscape-player-roll-comparison-2026-09-07.json
```

Manual review of each retained lane must confirm the real drain/prayer/charge/Guild observations and inspect the complete output and RNG comparison. This is a backend extraction; no UI proof is claimed. Preserve all raw reports and bind them to this inventory before commit authorization. Any source correction requires a new source freeze and new runtime binding.
