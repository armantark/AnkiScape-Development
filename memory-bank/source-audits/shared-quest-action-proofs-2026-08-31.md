# Shared quest-action proofs source audit — 2026-08-31

> **Fremennik shield follow-up — 2026-10-01:** Ruling 4.29.7 adds the real
> `craft_fremennik_round_shield` Crafting action and binds its successful event
> to the stage-5 proof. The earlier stage-1 generated sentinel still prevents
> whole-quest reachability and remains a separate quest-stage parity gap.

## Authority and boundary

The branch started from `35b912a08535222282a86d80cc35e10dbc26bab5`.
The owner approved one global, durable, forward-only proof mechanism in
`memory-bank/design-thread-queue.md` section 4.22 item 4. A proof can come only
from the real successful action path. Existing telemetry, inventory, quest
history, and quest-local stage flags cannot create a proof.

The live catalog still contains 704 `required_actions` predicates: 693 generated
`Complete <Quest> stage <N> objective` sentinels and 11 hand-written actions.
This slice wires three hand-written actions. It does not change the 693 generated
sentinels or add a user interface.

## Shared mechanism

`quest_action_proofs` is a sorted, unique list in player data. Quest blockers
read this list without a current-quest or source-quest restriction. Successful
quest stage actions also enter the global store, but old `quest_stage_actions`
records do not migrate into it.

The save schema moves from config version 121 to 122. A save below version 122
loads with an empty proof list, even if it contains matching telemetry, items,
completed quests, local stage actions, or a pre-existing unversioned proof key.
A version-122 or newer save keeps its sanitized proof list. An existing save can
earn repeatable Shop and Crafting proofs after the migration. A save that already
passed Biohazard's one-time cauldron stage receives no proof and the migration
does not replay that stage; this is the owner-approved forward-only behavior.

Runtime proof bindings are declarative in `data/quest_action_proof_data.py`.
The shared review-action seam records mapped Crafting proofs only after success.
The Shop buy and service reducers record mapped proofs only after an allowed
transaction. A Shop rollback removes the proof emitted by that event together
with its item, currency, stock, and ambush state. The quest reducer records stage
actions only after all stage gates pass.

## Wired hand-written actions

### Do No Evil stage 3

The required proof is `Recover an m'amulet mould before making the monkeyspeak
amulet`. A successful purchase of row
`hamabs_crafting_emporium:3:4020` writes it.

The read-only Darkan shop file
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops/hamabs_crafting_emporium.json`
contains item ID 4020 with stock 10 for NPC 1437. The committed Shop ledger also
contains that exact row. The live AnkiScape row resolves item ID 4020 to
`M'amulet mould`.

### The Fremennik Isles stage 5

The required proof is `Cure and stitch yak-hide armour`. It needs two real
steps after landing:

1. `thakkrad_cure_yak_hide` must successfully convert Yak-hide into Cured
   yak-hide.
2. `leather_yakhide_armour_10824` or `leather_yakhide_armour` must then
   successfully craft a Yak-hide armour piece.

The generated source-backed stage text says to pay Thakkrad Sigmundson to cure
three hides, then craft one-hide chaps and a two-hide body with needle and
thread. The live Shop service enforces stage 5, consumes the hide and fee, and
produces Cured yak-hide. The two live Crafting recipes consume one or two Cured
yak-hides plus Thread and award 32 Crafting experience.

The sibling proof `Make a Fremennik round shield` comes from the dedicated
Crafting action at the Neitiznot stump. It consumes two Arctic pine logs, one
Bronze nail, and one Rope, retains a Hammer, and is gated by stage 5.

### Mourning's End Part I stage 5

The required proof is `Use the rotten apple to sabotage the mourner food
stores`. Biohazard stage 7 writes it after the actual action
`Put the rotten apple in the Mourner HQ cauldron` succeeds.

The read-only Darkan source dispatches Rotten apple item ID 1984 on the
Biohazard cauldron to `handleUseAppleOnCauldron()`. That handler consumes the
apple, advances the stage, and reports that the apple dissolves into the stew.
An end-to-end test performs this action through the real review-answer entry
while Biohazard is current, then shows that Mourning's End Part I no longer has
this required-action blocker.

## Deliberately unwired hand-written actions

The other seven hand-written actions remain blocked because the exact mechanic
is absent or the apparent generic action is not source-faithful:

- `Have Oronwen repair the mourner trousers`: no Oronwen service action.
- `Cast Telegrab for the water channel puzzle`: the live Telegrab target is Wine
  of Zamorak; the source calls for an Ancestral-key interaction.
- `Cast Crumble Undead during the boneguard fight`: the source uses a direct
  spell-on-NPC quest interaction, not the live generic combat path.
- `Enchant sapphire for the Myreque preparations`: no Silvthrill-rod enchant
  target.
- `Collect a bucket of sap from an evergreen tree`: no evergreen sap action.
- `Build the clockwork penguin on a crafting table 3`: the furniture exists,
  but the clockwork-penguin action does not.
- `Cast Enchant Level 2 Jewellery for the emerald preparations`: no
  quest-specific emerald preparation target.

## Reachability measurements

The proof-aware reachability closure derives a runtime proof only when its bound
action or source is reachable. The Hamab purchase also requires the source on
the exact M'amulet mould item; another live row in the same shop cannot prove
the purchase. The closure derives a quest-stage proof only after a startable
quest can pass the source stage. It never seeds registered proofs at time zero.

| Measure | Before | After |
| --- | ---: | ---: |
| `action_count` | 1663 | 1663 |
| `reachable_item_count` | 2301 | 2301 |
| `orphan_input_count` | 165 | 165 |
| `root_orphan_count` | 32 | 32 |
| `cascade_orphan_count` | 133 | 133 |
| `unresolved_action_count` | 252 | 252 |
| `seed_item_count` | 1215 | 1215 |
| blocked quest-stage rows | 139 | 139 |
| completable quests | 51 | 51 |

No pin moves. Earlier generated sentinels still stop the three affected quests
before the newly wired hand-written gates can change the fixed-point item
report. The audit exposes and pins `completable_quest_count`. It also exposes
the earned global proof set and pins Biohazard's Mourner-food proof, which is
only present when the cross-quest bridge runs.

## Coverage

`tests/test_quest_action_proofs.py` covers proof-store normalization,
idempotence, multi-step prerequisites, forward-only migration, global pure
quest flow, Shop failure and success, real Crafting success, inventory-only
non-credit, Shop rollback retraction, and the real Biohazard review-answer
path. The recursive production census includes root `__init__.py`, nested
modules, and generated Python. It pins every file's exact proof-name mention
count and permits proof mutations only at the successful Shop buy, Shop service,
Shop rollback, shared runtime action, and completed quest-stage seams. A
mutation probe confirms the rollback test fails without retraction and the
audit proof assertion fails without runtime and cross-quest propagation.

The exact complete lanes pass:

```text
/opt/homebrew/bin/python3 run_tests.py
Ran 4596 tests in 846.693s
OK (skipped=515)

QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
Ran 4596 tests in 1092.015s
OK (skipped=3)
```
