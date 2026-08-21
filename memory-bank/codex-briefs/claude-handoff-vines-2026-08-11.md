# Claude handoff: Juju vine secondaries

## Goal

Resume from the closed Common jadinko and Juju hunter potion slice. Keep all source limits and registered placeholders.

## Context

The worktree is `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/vines-2026-08-11`.

The branch is `goal/vines-2026-08-11`. The base on `main` remains commit `0071218b`.

The canonical checkout is `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`. This slice did not change that checkout.

Nothing was pushed. The closure commit is the `HEAD` commit that contains this file. Run `git rev-parse HEAD` to get its exact SHA.

## Shipped scope

The slice adds the Common jadinko Hunter route. It uses a reusable Marasamaw plant.

A success gives these results:

- 350 Hunter XP.
- One Withered vine.
- A chance to give one vine-herb seed.

The seed selector contains these items:

- Erzille seed.
- Ugune seed.
- Argway seed.
- Shengo seed.
- Samaden seed.

The slice also adds the Juju hunter potion recipe. Erzille potion (unf) plus Corrupt vine makes dose 3.

All four Juju hunter doses are live consumables. A consumed dose applies only the sourced flavour message and leaves the next lower dose; it gives no stat boost.

The period game defines the potion as an ingredient used on a Herblore Habitat flower patch, but this add-on ships no matching action or attraction effect. Bob Barter can decant the four-dose family.

Runtime telemetry records the guaranteed output and the bonus seed. Review undo uses the same output record.

The normalized assets cover all four potion doses. They also cover the Marasamaw plant, Withered vine, and five seeds.

## Source record

Read the durable audit before a related change:

`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/vines-2026-08-11/memory-bank/source-audits/juju-vine-secondaries-2026-08-11.md`

The audit records every pinned value, source conflict, placeholder, asset, and reachability result.

## Registered placeholders

| ID | Live value | Source needed to close it |
| --- | --- | --- |
| `hunter.herblore_habitat_success_curves` | Common jadinko uses `rate1=128` and `rate99=256`. | A period catch routine or a qualified measured table. |
| `hunter.common_jadinko_seed_roll` | The seed trigger is `16/256`; the selector is uniform across five seeds. | A period drop routine or a qualified capture sample. |

Do not remove a placeholder marker without the source named in this table.

## Sourced player behavior

Darkan `Potions.kt:522,881-904` registers an ordinary drink: it consumes one dose, invokes only the flavour-message effect, and applies no stat boost. Juju hunter potion oldid `6258636` corroborates the drink-attempt message, while Darkan `FarmPatch.java:338-361` separately defines the period game's flower-patch ingredient use. This add-on has no action that consumes a dose there or applies attraction.

The potion is therefore a flavour-only consumable with no Hunter-boost placeholder. Its period-game Herblore Habitat ingredient use remains unimplemented in this add-on.

## Verification

The corrected full-lane and reachability results are recorded in `memory-bank/source-audits/juju-vine-secondaries-2026-08-11.md`.

## Queue

Do not change `ui/ui.py` as part of this closed slice.

A later user-interface slice must fix `ui/ui.py` lines 1467-1470. The current code applies the skill button state in one direction only.

Inspect the neighboring skill buttons in the same slice. Apply the fix to every matching button.


## Next leverage roots

The next Ectofuntus pass can add these roots:

- Burnt bones.
- Fayrg bones.
- Frost dragon bones.
- Jogre bones.
- Ourg bones.

Each root adds two items through the Ectofuntus family.

Skip Emerald lens. It belongs to the parallel Darkan quest thread.

## Safety limits

Work only in the selected worktree and branch. Do not change the canonical checkout.

Do not push. Do not amend. Do not use a destructive Git command.

Use evidence from before 2012-11-20. Use the project evidence order.

Do not invent a value. Add a code marker and a matching placeholder-register row for each unrecovered value.
