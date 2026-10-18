# Slice brief — three source-faithful actions, and the predicates they satisfy

Date: 2026-09-01. Author: the orchestration seat. Consumer: one dispatched
implementation agent.

Do not start until the orchestrator tells you the Mogre and diary slices have
landed. This slice edits `data/quest_data.py`, which both of those touch.

## 0. Read this first

`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md` is binding. Read it
completely before you edit anything. Nothing here overrides it. If this brief
and the contract disagree, stop and report both texts.

Then read the harvest this slice is built on:
`memory-bank/source-audits/proof-bindings-harvest-2026-09-01.md`. Its sources
are pinned and you must not re-harvest them.

## 1. What this slice is, and what it is not

Three quests are stuck on hand-written `required_actions` that no runtime path
can emit. The queue originally recorded all three as having their mechanics
already built, so the work read as three one-line bindings. **That was wrong**,
and the design seat resized the item on 2026-09-01 (rulings ledger section 33).

The three predicates, with the exact lines they sit on:

| Quest | Stage | Predicate | Line |
| --- | ---: | --- | --- |
| `legacy_of_seergaze` | 5 | `Cast Enchant Level 2 Jewellery for the emerald preparations` | `data/quest/stage_cleanups.py:695` |
| `in_aid_of_the_myreque` | 6 | `Enchant sapphire for the Myreque preparations` | `data/quest/stage_cleanups.py:548` |
| `the_fremennik_isles` | 5 | `Make a Fremennik round shield` | `data/quest/stage_cleanups.py:409` |

## 2. Why you cannot simply bind these to what exists

This is the whole point of the slice, so do not shortcut it.

`data/magic_data.py:332-348` generates generic jewellery enchantments:
`enchant_emerald_ring`, `enchant_emerald_necklace`, `enchant_emerald_amulet`,
`enchant_emerald_bracelet`, and the matching sapphire set. A successful cast
emits `("magic", target)` through `runtime/runtime_actions_magic.py:474-498`.

Those are not the deeds. Legacy of Seergaze wants the **emerald sickle**
transformation. In Aid of the Myreque wants the **Silvthrill rod**. The proof
mechanism at `data/quest_action_proof_data.py:13-34` and
`logic_pure/quest_action_proofs.py:29-41` maps one exact
`(event_type, event_id)` pair to one proof, and it cannot tell a quest
transformation from an ordinary enchantment.

So binding the predicates to the generic actions would credit a player for
enchanting any emerald ring. **That is forbidden by the ruling and it is worse
than leaving the predicate unemittable**, because an unreachable row is visibly
incomplete while a wrongly-credited row looks finished. A row anybody completes
by accident is the inert-row failure mode inverted, and no audit in this
repository would catch it.

`Make a Fremennik round shield` has no recipe at all. `data/crafting_data.py:434-456`
is `crafting_recipes_as_dict()`, a serializer, not a recipe table. The only
`round_shield` in the tree is a level-66 oak-plank house furnishing at
`data/construction_data.py:21`, emitting `("construction", "round_shield")`.
**Do not reuse it, and do not bind to it.** It is a different object that
happens to share a word.

## 3. What you build

Three new source-faithful actions, each with its own event id, and each quest
predicate bound to its own exact action.

1. The emerald sickle enchantment, as its own Magic action.
2. The Silvthrill rod enchantment, as its own Magic action.
3. The Fremennik round shield, as its own Crafting recipe.

Then bind each predicate to exactly one of them. One predicate, one action, one
proof rule. A rule that matches more than its own action is a defect.

Follow the surrounding conventions in each file rather than inventing a shape.
Read how a neighbouring action declares itself, what it emits, and how an
existing proof rule binds, before you write anything.

## 4. Sourcing

The harvest pinned all three deeds to pre-cutoff permanent revisions. Cite these
and do not re-harvest them:

| Quest | oldid | UTC timestamp |
| --- | ---: | --- |
| Legacy of Seergaze | `6521668` | `2012-11-02T22:17:22Z` |
| In Aid of the Myreque | `6555220` | `2012-11-14T12:32:46Z` |
| The Fremennik Isles | `6540919` | `2012-11-07T09:46:34Z` |

The cutoff is `2012-11-20T00:00:00Z`. For any value those revisions do not
settle, follow the evidence order in the contract's sourcing section: Darkan,
then the rev-727 cache, then game-main, then the other on-disk caches, then the
wiki as corroboration at a pre-cutoff `oldid`. Follow
`memory-bank/pre-eoc-source-verification-standard.md`.

**Gate.** If a level, an input, an output or an XP value cannot be recovered,
register it in `memory-bank/placeholder-values.md` with a `PLACEHOLDER(...)`
marker in the code, and say so in your report. Do not invent a value and present
it as settled.

## 5. The size gate, which will probably stop you

`data/quest_data.py`, `data/magic_data.py` and `data/crafting_data.py` are all
far above the pre-commit gate's 1000-line ratchet, and that gate refuses any
commit that grows such a file.

**Never set `SLOP_GATE_FILE_LINES` or any other `SLOP_GATE_*` variable, for any
reason.** That gate is machinery the repository owner built, and only he can
grant an exception. An agent on another slice today described setting it to
15000 as raising a baseline; it disables the check for the whole repository, and
it is the one thing you must not do.

If the gate refuses your commit, **stop and report its exact message**. A
reported conflict is a success state. There is an owner ruling pending on this
exact question, and your report becomes part of it.

## 6. Prohibitions, which you pass verbatim to any child agent you spawn

- Do not delete any worktree, however clean it looks. This is an owner gate.
- Do not change any existing user interface. Say in your report whether any
  changed.
- Do not commit to `main`, do not push, do not change git config, do not skip
  hooks, do not use an interactive `-i` flag.
- Do not weaken a test, an audit, or a pinned baseline so your work can pass.
- Do not bind any predicate to a generic enchantment action or to the
  Construction furnishing.
- Do not ask another agent session to rule on a conflict or grant permission.

## 7. Your worktree

```
python3 tools/worktree_guard.py audit
python3 tools/worktree_guard.py lease goal/proof-binding-actions-2026-09-01 --holder proof-bindings
```

The last stdout line is JSON with `path` and `lease_id`. Work there, commit
there, then release with `release <path> --lease-id <id>`. Never call
`treehouse` directly.

## 8. Verification

**Promotion gate.** The orchestration seat runs both lanes on the merged tree.
Run the plain lane only, and say so in your report:

```
/opt/homebrew/bin/python3 run_tests.py
```

Full lanes take 850 to 1150 seconds and exceed the background-task cap, so use
shell-level detachment if you run one at all.

Prove each binding by driving the real kernel: perform the new action, and show
the quest stage move from blocked to satisfied. Then prove the negative for each
of the two enchantments, which is the more important test: perform the **generic**
emerald and sapphire enchantment and show the quest predicate is **not**
satisfied. A test that only proves the positive would have passed the wrong
design.

Also run, and report the exact output of:

```
python3 tools/audit_docs.py
python3 tools/audit_test_quality.py
python3 tools/audit_item_reachability.py
python3 tools/worktree_guard.py audit
git diff --check
```

Report the reachability numbers before and after, and the count of substantive
unemittable actions before and after; the census stood at 11 substantive
actions with 3 emitted and 8 unemittable.

## 9. Your report

Write a source audit at
`memory-bank/source-audits/proof-binding-actions-2026-09-01.md`. Update
`memory-bank/activeContext.md` and `memory-bank/progress.md`, and append a
timestamped line to `memory-bank/papercuts.md` for every piece of friction, in
the moment.

Report exact numbers, identifiers, paths and error strings verbatim, re-measured
when you write the report. Name every placeholder you registered and every
source you cited. State plainly what you did not do and why.
