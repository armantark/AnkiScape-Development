# Wyvern bones acquisition audit — 2026-08-11

Status: **implemented with four registered combat placeholders**.
Cutoff: `2012-11-20T00:00:00Z`.

## Goal

The Skeletal Wyvern route now supplies one Wyvern bones item per kill.
This seed activates the existing Prayer and Herblore chains.

The implementation does not add a new downstream action.
It also omits the optional Skeletal Wyvern loot table.

## Period evidence

The following table records each pinned value and its exact source.

| Value | Exact source |
| --- | --- |
| Wyvern bones are unnoted item `6812`. The noted item is `6816`. The unnoted item has `Bury`. | OpenRS2 cache `742-2012-11-07`, item definitions `6812` and `6816`; RuneScape Wiki `Wyvern bones`, oldid `6105610`. |
| One Skeletal Wyvern kill gives exactly one Wyvern bones item. | Darkan `data/npcs/drops/skeletal_wyvern.json:1-17` at commit `ede51d1a527980f5dd732e6266fec8f60c0c5225`; RuneScape Wiki `Wyvern bones`, oldid `6105610`. |
| Burial gives `50.0` Prayer experience points. | Darkan `src/main/java/com/rs/game/content/skills/prayer/Burying.java:52,120-121` at commit `1de4da89ead0088fa7bdec11d8af6bb990f1b412`; game-main `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/prayer/burying/BoneData.kt:25`. |
| Wyvern bonemeal is item `6810`. It is not Bonemeal item `4255`. | Darkan `src/main/java/com/rs/game/content/skills/prayer/Ectofuntus.kt:193-240,250-272`; OpenRS2 cache `742-2012-11-07`, item definitions `6810` and `4255`. |
| Grinding consumes one Wyvern bones item `6812` and one Empty pot `1931`. It gives one Wyvern bonemeal item `6810`. | Darkan `src/main/java/com/rs/game/content/skills/prayer/Ectofuntus.kt:193-240,250-272`. |
| Ectofuntus worship consumes one Wyvern bonemeal item `6810` and one Bucket of slime `4286`. | Darkan `src/main/java/com/rs/game/content/skills/prayer/Ectofuntus.kt:20-31,91-132,250-279`. |
| Ectofuntus worship gives `200.0` Prayer experience points. It returns Empty bucket `1925` and Empty pot `1931`. It gives five Ecto-tokens `4278`. | Darkan `src/main/java/com/rs/game/content/skills/prayer/Ectofuntus.kt:20-31,91-132,250-279`. |
| The Skeletal Wyvern has combat level `198`, Slayer level `72`, Slayer XP `210.0`, attack speed `6`, and respawn delay `59`. | Darkan `data/npcs/combatdefs/uncategorized/skeletal_wyvern.json` at commit `9376cbc21c31f30b9f4ae1712e7324dafe29387c`; OpenRS2 rev-742 NPC definitions `3068-3071`; RuneScape Wiki `Skeletal Wyvern`, oldid `6569736`. |
| The combat stats are `2000` lifepoints, `125` Attack, `116` Strength, `120` Defence, `125` Magic, and `120` Ranged. | The same Darkan combat definition and OpenRS2 rev-742 NPC definitions `3068-3071`. |
| The defence bonuses are `140` stab, `90` slash, `90` crush, `80` Magic, and `140` Ranged. The ordinary maximum hit is `139`. | The same Darkan combat definition; RuneScape Wiki `Skeletal Wyvern`, oldid `6569736`. |
| The period attack set contains Melee, Ranged, and freezing ice breath. | RuneScape Wiki `Skeletal Wyvern`, oldid `6569736`. |
| Elemental, Mind, Body, Cosmic, Chaos, and Dragonfire shields protect against the ice breath. Anti-dragon shield and antifire potions do not protect. | RuneScape Wiki `Skeletal Wyvern`, oldid `6569736`. |
| The shielded ice-breath maximum is `150` lifepoints. Higher Magic defence lowers this maximum slightly. | RuneScape Wiki `Skeletal Wyvern`, oldid `6569736`. |
| The shield item identities are `2890`, `9731`, `18691`, `20436`, `20438`, and `11284`. | game-main `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`, items `2890`, `9731`, `18691`, `20436`, `20438`, and `11284`; OpenRS2 rev-742 item definitions. |
| The Falador hard task requires Slayer level `72` and one Skeletal Wyvern kill. | Darkan `FaladorTasks`; OpenRS2 rev-727 cache enum `3483`; RuneScape Wiki `Falador achievements`, oldid `6571459`, timestamp `2012-11-18T05:31:03Z`. |

### Recovered Grand Exchange rows

The following values are recovered period values. They are not placeholders.

| Item | Guide price | Buy limit | Source oldid |
| --- | ---: | ---: | ---: |
| Body shield | `7,165` | `100` | `6570241` |
| Chaos shield | `16,878` | `10` | `6561507` |
| Cosmic shield | `2,387` | `10` | `6111509` |
| Dragonfire shield | `3,577,833` | `10` | `6570515` |
| Mind shield | `3,195` | `100` | `6562662` |

The normalized enemy and shield sprites have durable records in
`assets_provenance.json` under these exact keys:

- `combatenemies/skeletal_wyvern.png`;
- `combatitems/elemental_shield.png`;
- `combatitems/mind_shield.png`;
- `combatitems/body_shield.png`;
- `combatitems/cosmic_shield.png`;
- `combatitems/chaos_shield.png`; and
- `combatitems/dragonfire_shield.png`.

## Registered placeholders

The period sources do not expose four server values.
The implementation marks each reconstruction with `PLACEHOLDER(...)`.

| Placeholder | Executable value | Why the value stays unrecovered |
| --- | --- | --- |
| `skeletal_wyvern.breath_attack_weight` | The attack table gives equal weight to Melee, Ranged, and ice breath. | Oldid `6569736` proves the three attacks. It does not give their selection weights. A period server selector or a qualified period sample must replace this value. |
| `skeletal_wyvern.freeze_ticks` | Ice breath adds five Combat ticks to the next player attack. | Oldid `6569736` proves that the breath stops attacks. It does not give the duration. A period server handler or a qualified timed recording must replace this value. |
| `skeletal_wyvern.unshielded_breath_max_hit` | Unprotected damage uses a uniform value from `0` through `500` lifepoints. | Oldid `6569736` reports unshielded hits of `500` or more. It does not give the upper bound. A period server handler or a qualified damage sample must replace this value. |
| `skeletal_wyvern.magic_defence_breath_reduction` | Each `64` combined Magic-level and Magic-defence points remove one lifepoint from the shielded `150` maximum. | Oldid `6569736` proves a small reduction from Magic defence. It does not expose the curve. A period handler or a qualified multi-value damage sample must replace this value. |

No placeholder controls the bone drop, item identities, burial XP, grinding route, or Ectofuntus reward.

## Reachability result

The clean canonical baseline was:

`1556 actions; 2573 reachable items; 102 orphan inputs; 101 blocked actions.`

The implemented worktree result is:

`1556 actions; 2585 reachable items; 90 orphan inputs; 85 blocked actions.`

The seed adds `12` reachable items.
It removes `12` orphan inputs and unblocks `16` actions.
The action count does not change because all sixteen actions already existed.

The twelve unlocked items are:

- Super prayer (1);
- Super prayer (2);
- Super prayer (3);
- Super prayer (4);
- Super prayer flask (1);
- Super prayer flask (2);
- Super prayer flask (3);
- Super prayer flask (4);
- Super prayer flask (5);
- Super prayer flask (6);
- Wyvern bonemeal; and
- Wyvern bones.

## Runtime boundary

The level-72 Combat row records one guaranteed Wyvern bones drop.
The shared Combat runtime records the kill and the drop.
It also records protected and unprotected ice-breath telemetry.

The item registry preserves all three canonical identities:

- Wyvern bones item `6812`;
- noted Wyvern bones item `6816`; and
- Wyvern bonemeal item `6810`.

The Falador task now needs both level `72` Slayer and one recorded kill.
Slayer assignment readiness now includes the existing Skeletal Wyverns family.

## Separate depth candidate

Construction models all seven chapel altar objects.
Prayer exposes only the Gilded altar method.

The following six non-gilded Prayer rows remain separate depth work:

- Oak altar;
- Teak altar;
- Cloth altar;
- Mahogany altar;
- Limestone altar; and
- Marble altar.

This audit does not implement these rows.

## Owner rulings

The owner made two direct rulings on 2026-08-10.

1. This goal stays on branch `goal/breadth-2026-08-11` in the isolated worktree.
   It does not touch canonical `main` until the owner is ready to merge.
   This ruling replaces the goal clause that required one commit on canonical `main`.
2. Luna does source harvesting at maximum effort.
   Sol then does a quick sanity check instead of a second full harvest.
   Sol keeps implementation work.

## Verification

| Gate | Exact result |
| --- | --- |
| Plain lane | **FAIL**. The lane ran `4061` tests in `210.511s`: `3565` passed, `2` failed, and `494` skipped. `test_generated_equipment_contract_shape` reported `AssertionError: 701 != 695`. The Grand Exchange audit reported Dragonfire, Chaos, Mind, Cosmic, and Body shields as unexpected blocked items. |
| Offscreen Qt lane | **FAIL**. The first worktree-local command exited `127` because `.venv-qt/bin/python` does not exist. The lane then used the canonical checkout interpreter without changing canonical files. It ran `4061` tests in `557.324s`: `4056` passed, `2` failed, and `3` skipped. It found the same two failures as the plain lane. |
| Documentation audit | **PASS**. The closure audit checked `560` Markdown files and `431` HTML files. The final audit checked `561` Markdown files and `431` HTML files. Both audits found `0` issues. |
| Test quality audit | **PASS**. The audit checked `4026` tests in `184` files. It found `0` hard issues and `20` clone candidate groups. |
| Changed-module compilation | **PASS**. Python compiled `12` changed modules with `0` errors. |
| Tracked JSON parse | **PASS**. Python parsed `26` tracked JSON files with `0` errors. |
| Placeholder register | **PASS**. The lane ran `3` tests: `3` passed. |
| Asset normalization | **PASS**. The lane ran `2` tests: `2` passed. |
| Item reachability audit | **FAIL by command contract**. The audit reports `1556` actions, `2585` reachable items, `90` orphan inputs, and `85` blocked actions. It exits nonzero while known blocked actions remain. |
| Worktree guard | **PASS**. The audit found `0` unsafe worktree placements. |

No open defect remains in the Wyvern bones slice.
The two full-lane catalog assertions remain outside this documentation-only closure unit.
