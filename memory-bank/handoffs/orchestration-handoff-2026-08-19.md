# Orchestration handoff — 2026-08-19

Written by the orchestration seat as the Codex weekly block ran down. This is
the resume record. Read it before selecting any work.

## 1. What landed

Main moved from `b6c24004` to the head recorded below. Every promotion ran the
full gate on the MERGED tree, never on the branch alone.

| commit | slice | why it matters |
| --- | --- | --- |
| `7fb738e5` | Skeletal Wyvern and Wyvern bones | the family and its six-shield ice-breath mechanic were finished on 2026-08-11 and never reached players |
| `2015df47` | Skill-button availability | seven Skills buttons switched on when training became possible and never switched off when it stopped |
| `4f86193c` | MacBook verification host | the laptop now runs the full corpus, and `tools/run_remote_tests.py` drives it |
| `aa106ff7` | Jungle Potion | the quest had no implementation; a strange rock could brick the save in ~4.9% of playthroughs |

## 2. Branches accepted and NOT yet merged

**[Corrected 2026-08-22]** All three branches below are now ancestors of
`main` at `968b4f61` (verified with `git merge-base --is-ancestor`). This
section is historical.

All of these have passed an independent cross-lineage review with every
blocking and major finding resolved. They need only a merge, a re-measured
reachability pin, and a green gate.

| branch | head | remaining minors |
| --- | --- | --- |
| `goal/vines-reland-2026-08-19` | see 2026-08-21 note below | **NOT promotable — still in correction; the figures once pinned here are stale** |
| `goal/herbs-reland-2026-08-19` | `c0face44` | one stale sibling docstring still citing the superseded 39-path count |
| `goal/papercuts-reland-2026-08-19` | `334214e1` | none recorded |

**[Corrected 2026-08-22]** The vine slice landed; the warning below no longer
applies. **The vine slice must be fixed before it lands.** DO NOT pin the figures in this
section — they were superseded on 2026-08-21 and are recorded here only as the
history of the correction. The figures once given as `1586 / 2307 / 75 / 45 / 30
/ 75 / 1123` with a 4,172-test plain lane were valid only for head `986933f0`.
Removing four invalid consume actions moved the branch to `1582 / 2307 / 72 / 45
/ 27 / 71 / 1123` at 4,180 tests, and the drink-semantics correction now in
flight will move it again. Re-measure on the merged tree, always.

Two majors stopped it originally:

1. It grants a drinkable `+3` Hunter boost for the Juju hunter potion, which
   Darkan `Potions.kt:522` contradicts: the row effect is only the sourced
   flavour message. The then-current placeholder ledger also rejected the
   boost, but incorrectly claimed the shared drink path refused and preserved
   the dose. Direct inspection of `Potions.kt:881-904` shows inherited
   `canDrink=true` and one-dose consumption. The correct fix is a flavour-only
   drink, not the `drinkable` refusal the prior brief requested.
2. `memory-bank/activeContext.md:114` on the merged tree carries pre-merge
   figures contradicting the baseline the same commit pins.

Neither is reachable in play today, because all four Juju hunter potion doses
are orphan inputs, but both go live the moment the vine_herb farming chain
lands. The merge work is done and reusable: `promote5/2026-08-19` holds it.

`goal/secondaries-2026-08-11` is promotable and was deliberately not started;
see the loop notes for why its final commit is not a refusal. **[Verified
2026-08-22: still unmerged — it and `promote5/2026-08-19` are not ancestors of
`main` at `968b4f61`.]**

## 3. The merge trap, which will bite again

Every one of these branches pins a reachability baseline in
`tests/test_item_reachability_audit.py`, and so does main. A merge conflicts
there every time, and **neither side describes the merged tree**. Picking a
side installs a number that measures nothing.

Resolve it by re-measuring on the merged tree with
`python3 tools/audit_item_reachability.py` and pinning exactly what it prints,
across all seven fields. On the Jungle merge the measured result was
`1581 / 2301 / 72 / 45 / 27 / 71 / 1123`, where main claimed
`1571 / 2278 / 72 / 45 / 27 / 71 / 1105` and the branch claimed
`1581 / 2289 / 84 / 46 / 38 / 87 / 1122`. Reachable items and seed items came
out ABOVE both sides, because two slices together unlock more than either does
alone. Expect that, and never resolve this conflict by arithmetic.

## 4. How to run the gate

Do not run it as a foreground tool call. A detached script has no command cap,
so the offscreen Qt lane runs in one process instead of being partitioned:

```
nohup /tmp/ankiscape_gate.sh "<promotion worktree>" > /tmp/gate.log 2>&1 &
```

That script is a session scratch file. Rewrite it in `tools/` if this pattern
survives another run. **[Superseded 2026-08-22:** the gate is now enforced by
`tools/promotion_gate.py` (`run` / `land`) rather than by the orchestrator
remembering. Use it.**]** It must NOT call the reachability audit with `--summary`,
which exists only on the papercuts branch; that flag silently skipped the
reachability check on two promotions before it was caught.

Do not commit to main while a gate is running. It forces a reconciliation merge
that buys nothing.

## 5. What is blocked, and by what

- **[Resolved 2026-08-22]** The five vine-herb seeds ARE plantable now. The
  habitat crop rows sit at `data/farming_data.py:421-425` on the merged tree
  with `blocked=()`, and `Herblore:finished_juju_hunting` exists at
  `data/herblore_data.py:285`; the chain is reachable. The merged tree measures
  `1599 / 2370 / 38 / 34 / 4 / 37 / 1123` (actions / reachable items / orphan
  inputs / root orphans / cascade orphans / blocked actions / seed items),
  re-measured with `python3 tools/audit_item_reachability.py` and pinned at
  `tests/test_item_reachability_audit.py:559-567`. The original text follows:

  The habitat crops at
  `data/farming_data.py:395-399` carried
  `source_blocked=('stages','stage_minutes','yield')` and were deliberately not
  executable, so the Juju hunter potion chain stayed unreachable and the Withered
  vine had no consumer.
- **Frost dragon bone route mapping** remains source-blocked: no period source
  maps item `18830` and item `18832` one-to-one.
- **Three registered placeholders have never been re-walked** and all three are
  source-blocked: `fish_flingers.xp_payout`,
  `bone_sources.frost_dragon_generated_levels`,
  `bone_sources.ogre_coffin_selector_weights`. The other 172 were re-walked on
  2026-08-13. Placeholder retirement is NOT open work.

## 6. One decision waiting for the owner

The Jungle Potion strange-rock exemption is a safeguard with no source behind
it. Darkan gates each search object on `questStage == requiredStage` and the
stage only advances on turn-in, so in the source a player who loses the clean
herb simply searches again. AnkiScape splits that single stage into a search
stage and a turn-in stage, which is what creates the one-shot, and the exemption
compensates for the split.

The source-faithful alternative is to keep the search reachable until the herb
is handed in, and delete the exemption. Given the standing preference for parity
over invented balance safeguards, that is likely what the owner wants, but
replacing a shipped safeguard with a parity change is his call. Recorded in
`memory-bank/design-thread-queue.md`.

## 7. Rules this run added, all now in the standing contract

- A workflow that has not notified still holds its worktree. Two agents entered
  one checkout because a follow-up round was dispatched while the first was
  still running.
- `lsof` is not a liveness test for an agent worktree. An agent between tool
  calls holds no file handles, and a live research agent lost its checkout to
  that mistake.
- The orchestrator is the only escalation route. Dispatched agents repeatedly
  asked an unrelated project's session to rule on this project's contract.
- A fix round is where invented facts enter. Told to close a gate, an agent
  produces a value that closes it. Every fix brief now says: register a
  placeholder or delete the row, never manufacture something that looks right.
- One commit per slice is the shape of a finished slice, not a cap. Correctness
  outranks the count.


## 8. Added 2026-08-21

**Landed since this file was written:** `992191ca` tooling guardrails.

**Undo-seam fan-out, seven branches, all committed, all under one cross-lineage
review:** `goal/undo-{ge,farming,mta,agility,warriors,chinchompa,star}-2026-08-21`.
Each migrates ONE `_apply_*` handler onto `commit_direct_action`.
**[Updated 2026-08-22]** the fan-out continued far past these seven and has
landed broadly: 38 distinct `goal/*` branches merged to `main` between
2026-08-21 and 2026-08-22, nearly all undo migrations. On the merged tree,
`commit_direct_action` (`__init__.py:1018`) carries 82 call sites in
`__init__.py`, and only two `_apply_*` handlers remain in
`runtime/runtime_actions_shared.py` (`_apply_brawling_actions`,
`_apply_farming_queue_result`). The "twenty-five remain" figure is stale.

The trap every one of them was warned about, and which the first attempt shipped:
`commit_direct_action` returns False for two different reasons — the pure
function refused, or `mw.col.add_custom_undo_entry` raised and nothing was
written. Collapsing them tells the player an action succeeded while nothing was
saved. Read the pre-migration handler on `main` to recover its distinct returns;
do not infer them from the migrated code.

**Ox Alpha authored all seven.** It stalls if told to run the full lanes — those
are single commands lasting four to ten minutes — and works well when given the
focused test only, with the orchestrator running the lanes as the promotion gate.
Probes confirmed it writes, commits, reads 221 KB files and carries the long
prohibitions preamble without trouble.

**The vine slice's drink semantics were wrong twice, in opposite directions.**
Darkan `Potions.kt` defines `open fun canDrink(): Boolean { return true }` and a
`drink()` that swaps in the next-lower dose, invokes the effect and prints "You
drink some of your ...". `JUJU_HUNTER_POTION` has no override, so the player DOES
drink it and DOES consume a dose; only the stat effect is absent. The Habitat
reagent behaviour lives in `FarmPatch.java:340-361`, not in `Potions.kt`. The
placeholder row that claimed otherwise is being corrected, and it is the reason
the error propagated: a brief quoted the Memory Bank summary as if it were the
source.


## 9. Correction pass, 2026-08-22

This file was audited against `main` at `968b4f61` and the stale claims above
were marked in place rather than silently rewritten. Summary of what changed:

- Sections 1 and 2 said the vine, herb and papercut branches were unmerged and
  the vine slice needed fixing first. All three branch tips are ancestors of
  `main` at `968b4f61`; the vine slice landed.
- Section 4's `/tmp/ankiscape_gate.sh` scratch script is superseded by
  `tools/promotion_gate.py`, which now enforces the promotion gate.
- Section 5 claimed the five vine-herb seeds could not be planted and that
  `Herblore:finished_juju_hunting` was blocked. Both are live:
  `data/farming_data.py:421-425` (blocked=()) and
  `data/herblore_data.py:285`. Merged-tree reachability baseline:
  `1599 / 2370 / 38 / 34 / 4 / 37 / 1123`.
- Section 8's "twenty-five of thirty-two handlers remain" was stale; see the
  in-place note there.
- Citation drift found by `tools/audit_citation_drift.py` in this file:
  `memory-bank/activeContext.md:114` (content changed) and
  `data/farming_data.py:395-399` -> now `421-425`.

Still true as of `968b4f61`: `goal/secondaries-2026-08-11` and
`promote5/2026-08-19` remain unmerged; the three source-blocked placeholders
(`fish_flingers.xp_payout`, `bone_sources.frost_dragon_generated_levels`,
`bone_sources.ogre_coffin_selector_weights`) are still registered in
`memory-bank/placeholder-values.md`; the Jungle Potion safeguard decision
(design-thread-queue 3.26) still waits for the owner.

Landed since this file was last updated, per merge history on `main` between
2026-08-21 and 2026-08-22: 38 distinct `goal/*` branches, including the
remaining undo-seam migrations, trails RNG, asset cutoff, prayer altars,
camo jadinko reward tables, clue ownership, the gate lock itself, and the
citation audit. The promotion gate is enforced by `tools/promotion_gate.py`;
the next orchestration seat should start there, not from memory.
