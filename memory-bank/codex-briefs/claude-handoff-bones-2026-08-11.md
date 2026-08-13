# Claude handoff: Ectofuntus bone family

## Goal

Resume from the integrated Ectofuntus bone-family slice.
Keep all source limits and both registered placeholders.

## Repository state

The integration worktree is `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/bones-integrate-2026-08-13`.

The branch is `goal/bones-integrate-2026-08-13`.
The integration commit is `3709356275c3a5d78571461c211524721cc10606`;
this reconciled handoff is recorded by the later `HEAD` commit.

The legacy branch `goal/bones-2026-08-11` was not modified.
Canonical `main` remains untouched by this integration seat.
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

`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/bones-integrate-2026-08-13/memory-bank/source-audits/ectofuntus-bone-family-2026-08-11.md`

## Registered placeholders

This slice carries two genuine registered placeholders.

| ID | Live value | Source needed to close it |
| --- | --- | --- |
| `bone_sources.ogre_coffin_selector_weights` | Zogre `63`, Fayrg `14`, Raurg `6`, Ourg `3`, and non-bone `39` in `125` total slots. | A period coffin routine or a qualified cutoff sample. The source must give the hidden selector and the non-bone rows. |
| `bone_sources.frost_dragon_generated_levels` | Attack, Strength, Defence, Magic, and Ranged are all `213`. | An authentic period Frost dragon combat definition or the period server routine that gives the five core levels. |

Do not remove either marker without the source named in the table.

## Open source mapping

Frost dragon bones use period item IDs `18830` and `18832`.
No recovered source maps each ID to its route.
The two routes are Asgarnian Ice Dungeon and Daemonheim.

The live route uses tradeable item `18832`.
Keep the one-to-one mapping open until a period source settles it.

## Access gates

- Zogre requires `Zogre Flesh Eaters` to have started, matching the point at
  which the Jiggig barricade opens. Both the selector and combat kernel enforce
  the save-state gate.
- The Shaikahan requires completed `Tai Bwo Wannai Trio` and continuously
  requires `Steel spear (kp)` in the weapon slot. Both conditions are enforced
  by selector and execution tests.
- Jogre records ordinary Karamja location context and deliberately has no quest
  gate.
- Frost dragon retains its Dungeoneering level `85` requirement.

## Verification

The complete post-fix plain lane passed:

```text
Ran 4128 tests in 360.389s
OK (skipped=498)
```

The corrected audit instrument is byte-identical to main, with SHA-256:

```text
aaaf67ff50ef582a992c5755a0504c412710e3f699655c48d09360f0a6db5351
```

It measures:

```text
main:        1568 actions; 2248 reachable items; 100 orphan inputs; 103 blocked actions; 1099 seed items
integration: 1571 actions; 2266 reachable items;  84 orphan inputs;  87 blocked actions; 1104 seed items
```

The older `1556 / 2573 / 102 / 101` and `1559 / 2590 / 86 / 85`
figures came from a superseded permissive instrument and must not be reused.
The access-gate correction does not change the integration aggregate.
The audit exits `1` while unrelated graph debt remains.

The runtime check confirmed these guaranteed combat sources:

- Zogre level `44` gives Zogre bones and an Ogre coffin key after the quest-start gate.
- Jogre level `53` gives Jogre bones without a quest gate.
- The Shaikahan level `83` gives Shaikahan bones after both access gates.
- Frost dragon level `166` gives Frost dragon bones.

## Queue

Do not change `ui/ui.py` as part of this closed slice.

A separate slice must fix `ui/ui.py:1467-1470`.
The code applies skill availability as a one-way enable.
A button stays enabled after the pure result becomes false.
Neighbouring skill buttons use the same pattern.

A source pass must recover the Frost dragon bone ID mapping.
Use the exact source condition in the open mapping section.

## Safety limits

Do not change the canonical checkout before the owner selects a merge order.
Do not push.
Do not amend.
Do not use a destructive Git command.
