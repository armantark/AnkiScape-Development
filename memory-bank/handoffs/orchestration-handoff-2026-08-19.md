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

All of these have passed an independent cross-lineage review with every
blocking and major finding resolved. They need only a merge, a re-measured
reachability pin, and a green gate.

| branch | head | remaining minors |
| --- | --- | --- |
| `goal/vines-reland-2026-08-19` | `986933f0` | **NOT promotable — two majors found on the merged tree, see below** |
| `goal/herbs-reland-2026-08-19` | `c0face44` | one stale sibling docstring still citing the superseded 39-path count |
| `goal/papercuts-reland-2026-08-19` | `334214e1` | none recorded |

**The vine slice must be fixed before it lands.** Its merge, its re-measured
pins (`1586 / 2307 / 75 / 45 / 30 / 75 / 1123`) and its plain lane (4,172 tests,
502 skips) are all correct. Two majors stop it:

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
see the loop notes for why its final commit is not a refusal.

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
survives another run. It must NOT call the reachability audit with `--summary`,
which exists only on the papercuts branch; that flag silently skipped the
reachability check on two promotions before it was caught.

Do not commit to main while a gate is running. It forces a reconciliation merge
that buys nothing.

## 5. What is blocked, and by what

- **The five vine-herb seeds cannot be planted.** The habitat crops at
  `data/farming_data.py:395-399` carry
  `source_blocked=('stages','stage_minutes','yield')` and are deliberately not
  executable, so the Juju hunter potion chain stays unreachable and the Withered
  vine has no consumer. This is declared debt, not a defect, and it mirrors the
  Juju farming potion already in main.
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
