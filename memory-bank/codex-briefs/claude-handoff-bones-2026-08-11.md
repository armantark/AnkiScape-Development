# Claude handoff: Ectofuntus bone family

## Goal

Resume from the closed Ectofuntus bone-family slice.
Keep all source limits and the registered placeholder.

## Repository state

The worktree is `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/bones-2026-08-11`.

The branch is `goal/bones-2026-08-11`.
The closure commit is the `HEAD` commit that contains this file.
Run `git rev-parse HEAD` to get its exact SHA.

Canonical `main` remains untouched at `1cf43931`.
Nothing was pushed.

## Shipped scope

The slice adds acquisition routes for eight bone types.
It also adds all matching bonemeal identities and Ectofuntus routes.

The routes include these sources:

- A ground-spawn action for Burnt bones.
- Guaranteed combat drops from Zogre, Jogre, The Shaikahan, and Frost dragon.
- An Ogre coffin action for Zogre, Fayrg, Raurg, and Ourg bones.
- A Steel spear karambwan-poison action for The Shaikahan gate.

The Zogre target also gives one Ogre coffin key.
The four combat sources are live targets in `COMBAT_ENEMY_DATA`.

The slice corrects Zogre bones from `12.5` to `22.5` Prayer XP.
This was a live player-visible defect on canonical `main`.

The durable source record is:

`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/bones-2026-08-11/memory-bank/source-audits/ectofuntus-bone-family-2026-08-11.md`

## Registered placeholder

This slice adds one registered placeholder.

| ID | Live value | Source needed to close it |
| --- | --- | --- |
| `bone_sources.ogre_coffin_selector_weights` | Zogre `63`, Fayrg `14`, Raurg `6`, Ourg `3`, and non-bone `39` in `125` total slots. | A period coffin routine or a qualified cutoff sample. The source must give the hidden selector and the non-bone rows. |

Do not remove this marker without the source named in the table.

## Open source mapping

Frost dragon bones use period item IDs `18830` and `18832`.
No recovered source maps each ID to its route.
The two routes are Asgarnian Ice Dungeon and Daemonheim.

The live route uses tradeable item `18832`.
Keep the one-to-one mapping open until a period source settles it.

## Verification

The complete plain lane passed:

```text
Ran 4069 tests in 226.099s
OK (skipped=496)
```

The final reachability result is:

```text
1559 actions; 2590 reachable items; 86 orphan inputs; 85 blocked actions
```

The baseline at `1cf43931` was:

```text
1556 actions; 2573 reachable items; 102 orphan inputs; 101 blocked actions
```

The runtime check confirmed these guaranteed combat sources:

- Zogre level `44` gives Zogre bones and an Ogre coffin key.
- Jogre level `53` gives Jogre bones.
- The Shaikahan level `83` gives Shaikahan bones.
- Frost dragon level `166` gives Frost dragon bones.

## Queue

Do not change `ui/ui.py` as part of this closed slice.

A separate slice must fix `ui/ui.py:1467-1470`.
The code applies skill availability as a one-way enable.
A button stays enabled after the pure result becomes false.
Neighbouring skill buttons use the same pattern.

A source pass must recover the Frost dragon bone ID mapping.
Use the exact source condition in the open mapping section.

## Unmerged slices

Four finished slices now stand unmerged.

| Branch | Commit | Base state |
| --- | --- | --- |
| `goal/breadth-2026-08-11` | `ef3be1c6` | Based on `0071218b`; rebase before merge. |
| `goal/herbs-2026-08-11` | `d63bba84` | Based on `0071218b`; rebase before merge. |
| `goal/vines-2026-08-11` | `508a8aa2` | Based on `0071218b`; rebase before merge. |
| `goal/bones-2026-08-11` | The `HEAD` commit that contains this file. | Based on `1cf43931`. |

Rebase the first three branches before a merge.
Do not use a union merge for related branch families.

## Safety limits

Do not change the canonical checkout before the owner selects a merge order.
Do not push.
Do not amend.
Do not use a destructive Git command.
