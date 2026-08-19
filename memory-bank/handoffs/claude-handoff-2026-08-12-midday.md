# Claude handoff — 2026-08-12 midday

## Goal

Resume acquisition work from the corrected reachability measurement. Fix the production quest-action emitter mechanism before work continues on quest-gated item families.

## Session commits

This session committed these changes:

- `d2faf1d2` and `3c05da03` on `goal/secondaries-2026-08-11` added ten grindable Herblore secondaries, the reachability-audit blind spot, and a handoff.
- `db14782b` on `goal/papercuts-2026-08-11` added tooling guardrails and the worktree ownership check.
- `eba91888` and `ad5f7554` on `goal/audit-truth-2026-08-12` made the audit follow runtime blockers and added the overnight handoff.
- `9eb91701` on `goal/acquire-2026-08-12` recorded the blast radius and the evidence standard.
- `b9501d67` on `goal/acquire-2026-08-12` preserved the analysis without the unshipped Jadinko product work.
- The commit that contains this file completes the midday handoff.

## Headline finding

`tools/audit_item_reachability.py` seeded quest-stage products without checking their `required_action` blockers. The runtime rejects exactly those blockers in `runtime/runtime_actions_production.py:1298-1362`.

The corrected totals are 1,556 actions, 2,493 items, 103 orphans, and 102 blocked items. The item total fell by 80 from 2,573.

This change is a measurement correction, not a regression. Do not restore the old total.

## Production blocker

The 196 quests contain 1,096 required-action occurrences. They include 783 generated `Complete X stage N objective` placeholders and 313 hand-authored requirements.

The project contains 101 emitters. The required-action set and emitter set have zero intersection, even within one quest.

The direct and downstream effects are:

- 185 quests are directly uncompletable.
- Approximately 190 quests are uncompletable after prerequisite closure.
- Only 6 quests are unaffected.
- 15 of 15 combat targets are blocked.
- 17 of 18 Slayer families are blocked.
- 56 of 58 magic actions are blocked.
- 33 of 36 completion shops are blocked.
- All 25 started-only shops are blocked.
- 110 of 112 dependent quests are blocked.

A positive control seeded the Druidic Ritual action. Its blocker then disappeared.

Implement and verify the production quest-action emitter mechanism. This is the single action that unblocks the work.

Emitters already exist. They use the same type of prose objective string as the requirements.

First, determine whether the two sides drifted apart. The fault can be a reconciliation problem rather than a missing subsystem.

## Attempted acquisition families

### Bush snake

The family produces Snake hide. Wiki oldids `6009794` and `6352282` state an `Always` quantity of 1–5.

Tai Bwo Wannai Trio gates the route. That quest needs Jungle Potion, which needs Druidic Ritual.

The quest-action blocker prevents this family.

### Crab

A Crab non-player character produces Fresh crab claw and Fresh crab shell. The producer has level 21 and level 23 forms.

The evidence uses oldids `4905238`, `5906508`, and `6522171`. The gate `recipe_for_disaster_freeing_pirate_pete` has `req=3` and `emit=0`.

The quest-action blocker prevents this family.

### Jadinko

The family produces four vines. HEAD has no Herblore Habitat environment or state model.

The Common jadinko framework exists only on unmerged commit `508a8aa2`. The offscreen Qt lane did not become green for the attempted implementation.

The Jadinko family is not quest-blocked. Herblore Habitat oldid `6513740` states that the activity has no quest requirements.

A positive control confirms this fact in `BoxHunterType.java`. FERRET declares `Quest.EAGLES_PEAK`, while Cannibal jadinko and Guthix jadinko carry `null, null`.

## Next acquisition slice

Wait until `goal/vines-2026-08-11` merges and the project has a Habitat environment model. Then implement Shadow vine and Corrupt vine as one two-item slice.

Shadow vine needs Hunter level 71, a Noose wand, a red vine blossom, and an abandoned house. Corrupt vine needs Hunter level 78, a Noose wand, a boneyard, and a banana tree.

Neither item needs a Juju potion. Plant teeth and Guthix vine need the potion, and the potion needs Corrupt vine.

The blast-radius audit contains the full citations.

## Source method rules

`memory-bank/pre-eoc-source-verification-standard.md` now contains these rules:

- Exclude `src/main/java/com/rs/web/*AuditProbe.kt` from source evidence without exception. These files are fleet instrumentation.
- Use `git log -- <path>` instead of file recency to separate upstream Darkan work from reconstruction.
- Record the wiki section for every claim.
- Treat Trivia, update-history, scam, and glitch material as historical or unclear.
- Check page-level markers such as `{{beta}}`.
- Do not use a negative search result as absence evidence until the probe produces a known hit.

## Open owner decisions and work

The owner must decide how to fix the quest emitter mismatch. The first question is whether two existing sides only need reconciliation.

Seven branches await merge. Three of those branches need a rebase.

Two clean, locked worktrees exist under `addons21/ankiscape_fork/.claude/worktrees/`. Another session created them through agent isolation.

Those worktrees make `worktree_guard.py audit` report an error. Do not delete or change them without owner direction.

The owner must decide whether the runtime must enforce facility prerequisites. The owner must also resolve a provenance failure in the work orders.

Those work orders cited a code-review finding that the review did not issue.

## Work not done

Two implementable candidate groups remain untested for gate satisfiability:

- The Dragon impling arrowtip and dart-tip pair.
- The Spider carcass to Skewer stick chain.

Do not treat either group as ready until the gate check succeeds.
