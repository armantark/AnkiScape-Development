# Two save-data claims, both confirmed — 2026-09-02 15:20 PDT

Measured read-only at `c39e2145`. Both reached this seat from a review that used
a stale base, so its framing was discarded and only the claims were kept. Both
are real. They need different handling, and one is an owner gate.

## 1. Migration drops a completed action, and a landed test requires it to

A save at `config_version` 121 loses every quest action proof on load.
`core/storage_pure.py:982` removes `quest_stage_actions`, and `:993` selects an
empty list for any save below version 122, never calling the conversion routine
that already exists at `logic_pure/quest_action_proofs.py:109-124`.

The consequence is permanent. A player who completed Biohazard stage 7, whose
auto-action is "Put the rotten apple in the Mourner HQ cauldron"
(`data/quest/stage_overrides/members/classic/biohazard.py:144-157`), and who has advanced past it, needs the proof
"Use the rotten apple to sabotage the mourner food stores" for Mourning's End
Part I stage 5 (`data/quest/stage_cleanups.py:87-91`). Quest progress only consumes
the current stage and moves forward (`logic_pure/logic_pure_quest.py:1459-1469`),
so stage 7 cannot be replayed and the later stage stays blocked with no route.

**This is a gate, not a defect to fix quietly.** The behaviour is asserted by a
landed test, `tests/test_quest_action_proofs.py:179-201`,
`test_old_saves_start_empty_without_telemetry_inventory_or_local_backfill`,
which discards even the two proofs the legacy save already carried in its own
`quest_action_proofs` list. The name says "without local backfill", so someone
decided this. Fixing the block means changing that decision and rewriting its
test, which this seat does not do on its own authority.

The question for the owner: should migration convert legacy `quest_stage_actions`
into proofs, or should an old save keep starting empty and accept that some
quests become unfinishable? A middle answer exists: convert only the legacy
actions that map to a known proof through `data/quest_action_proof_data.py`,
which is a bounded backfill rather than a general one.

## 2. Rolling back one shop event removes a proof another retained event earned

Confirmed with a canary. The proof store is a plain unique set of strings with
no provenance (`logic_pure/quest_action_proofs.py:14-20`), and retraction
subtracts every proof the rolled-back event emitted (`:76-86`) without checking
whether a retained event still supports it.

Sequence: a player at Fremennik Isles stage 5 with two Yak-hide, ten Coins and
one Thread calls `apply_shop_service_pure(player, "thakkrad_cure_yak_hide")`
twice, then rolls back only the second event. The canary showed the first event
and one Cured yak-hide retained, and the proof list emptied:

```
before-rollback: 0 2 ['Cure yak-hide with Thakkrad'] 2
after-rollback:  1 1 [] [('shop_evt_1', 'service', ...), ('shop_evt_2', 'service', ...), ('shop_evt_3', 'rollback', None)]
remaining-first-event: True
```

One correction to the original claim, from the measurement: the crafting action
is not blocked. The retained hide can still be crafted, but that craft no longer
earns "Cure and stitch yak-hide armour"
(`data/quest_action_proof_data.py:23-29`), so Fremennik Isles stage 5 stays
gated (`data/quest/stage_cleanups.py:396-400`). The end state matches the claim; the
mechanism does not.

No test covers two retained service events with one rolled back. The closest are
`tests/test_quest_action_proofs.py:468-489` (one purchase) and
`tests/test_shop_logic.py:539-586` (one batched event).

This one has no conflicting ruling, so it is queued as a slice behind the
standing sequence rather than jumped ahead of it. The fix is a design choice
between giving each proof its event provenance and recomputing the surviving
proofs from retained events; the second needs no schema change.
