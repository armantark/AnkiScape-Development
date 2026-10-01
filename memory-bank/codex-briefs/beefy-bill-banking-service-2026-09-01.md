# Slice brief — the Beefy Bill banking service

Date: 2026-09-01. Author: the orchestration seat. Consumer: one dispatched
implementation agent.

Do not start this slice until the orchestrator tells you the diary wiring slice
is merged to `main`. Your regeneration depends on its generator change.

## 0. Read this first

`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md` is binding. Read it
completely before you edit anything. Nothing in this brief overrides it. If
this brief and the contract disagree, stop and report both texts.

## 1. What exists, and what does not

Beefy Bill is already in the game. Do not build him. Measured from
`data/shop_data.py`:

```
id            beefy_bills_supplies      npc_ids  (246,)
display_name  Beefy Bill's Supplies     visibility  visible
currency      Coins                     general_store  False
stock rows    14, every one with disposition "live"
```

His identity, period stock and prices come from
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops/beefy_bills_supplies.json`
and are recorded in
`memory-bank/source-audits/npc-shop-coverage-ledger-2026-07-06.json`.

What is missing is one thing only: a **banking service**, in which Beefy Bill
banks player-selected items for his period cut.

## 2. The surface is ruled

The design seat ruled this on 2026-09-01 (rulings ledger section 28.3, which
supersedes 28.2): build the service as a **new row in the existing
`SHOP_SERVICES` registry**, not as a Utility action.

Verified in the tree, so you do not have to rediscover it:

- `data/shop_data.py::SHOP_SERVICES` is a dict of 84 rows.
- `logic/shop_logic.py:616::apply_shop_service_pure` applies a row and
  dispatches on its `action_type`. Three special kinds branch there today; the
  rest fall through to `_apply_service_like`.
- The surface is the existing "Shops and service providers" list at
  `ui/ui_tab_shop.py:123`.

One correction to the ruling's framing, which changes nothing but should not
mislead you: the registry holds 84 rows across only **6 distinct providers**,
and 78 of those rows are `bogrog_pouch_exchange`. The genuine variety is 6
rows, one per provider. Do not read the registry as a rich precedent library.

Every existing row carries this key set:

```
access, action_type, batchable, currency_id, currency_implemented,
currency_item_name, currency_name, display_name, icon_item_name, id, inputs,
location, lock_reason, outputs, price, provider, source, visibility
```

## 3. The mismatch you must handle, and the gate it may reach

Every existing row has a **fixed** `inputs` list. Beefy Bill's service acts on
**player-selected** items, so it has no fixed inputs. That is the real design
work in this slice, and it is why the ruling calls for one new `action_type`
handler rather than a plain data row.

In the single-ledger carried model, "banking" means the chosen items leave the
death-loss carried view and enter the Bank proper. Keep his sourced cut.

`ui/ui_tab_shop.py:1148-1204` already branches on `action_type` for three
kinds. **Your fourth branch is expected work, not a gate.** Build the item
picker Bill's service needs as contained new-feature interface on the existing
surface. The design seat authorized exactly that (rulings ledger section 28.4),
and the orchestrator sends your new control to a frontend-taste model for
review before promotion.

**Gate, narrowed.** Stop and report only if your work would change how the
three existing service kinds render, or how the shop stock renders. Those are
settled surfaces and they are not yours. If you reach that point, report the
exact lines you would have had to change and why the new control cannot sit
beside them. Do not redesign the Shop tab.

The standard offscreen visual check of the rendered row applies. Follow
`.claude/rules/qt-offscreen-screenshots.md` exactly: show the dialog first,
then resize, then process events several times before any grab, trust widget
geometry probes over pixels, and reproduce the owner's real window size at both
the default size and roughly 560 logical points tall. Look specifically for
truncation and ellipsis in any visible text, and fix what you find.

## 4. Sourcing, which is the real work

Harvest the cut and the accepted items in the contract's evidence order:
Darkan first, then the rev-727 cache, then game-main, then the other on-disk
OpenRS2 caches, then the wiki as corroboration at a pre-cutoff `oldid`. The
cutoff is `2012-11-20T00:00:00Z`. Follow
`memory-bank/pre-eoc-source-verification-standard.md`.

The deed itself constrains you, from the diary ledger row
`lumbridge_medium_where_s_the_beef`:

```
designed_trigger  Complete when a Beefy Bill service action successfully
                  transfers at least one player-selected item into the bank.
notes             A normal bank deposit or merely owning banked items is not
                  this deed. No current bank writer records Beefy Bill as the
                  service source.
source_citation   Lumbridge achievements; oldid=6549949;
                  2012-11-12T17:54:35Z;
                  https://runescape.wiki/w/Special:PermanentLink/6549949;
                  Darkan rev-727 cache enum 3483 identity=
                  LumbridgeDraynorTasks.WHERES_THE_BEEF (source_id=111)
```

**Gate.** If the cut or the accepted item set cannot be recovered from any
source in the evidence order, do not invent one and present it as settled.
Register the unrecovered value in `memory-bank/placeholder-values.md` with a
`PLACEHOLDER(...)` marker, and say in your report which values are placeholders
and why. An unmarked reconstruction is invisible to the placeholder audit and
is a defect.

## 5. Wiring the deed, and the tier it unlocks

The service telemetry, `service_id` with `quantity`, is the ledger's designed
trigger. The deed must be distinguishable from an ordinary bank deposit.

Then, and only then:

1. Edit the row `lumbridge_medium_where_s_the_beef` in
   `memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl`. Its
   `disposition` becomes `active` and its `future_system` becomes `null`. Keep
   the exact key order the ledger README specifies, and keep the citation
   intact. Update `notes` to name the new seam.
2. Regenerate through `tools/generate_achievement_diary_data.py`.
3. Never hand-edit `data/achievement_diary_catalog.py`. The generator route is
   the condition the owner attached to the gate that authorized this work.

`lumbridge_medium` then reaches 12 of 12 and becomes the product's first
claimable tier. Measure that, do not assume it: the claimable tier count moves
from 0 of 34 to 1 of 34. If your measurement disagrees, report the measurement
rather than the expectation.

`lumbridge_easy_money_down_the_drayn` stays `dormant`. Its trigger needs a
Draynor Village bank identity, and the Bank is locationless by settled design.
Do not touch that row.

## 6. Prohibitions that apply to this workspace

Forward every one of these to any child agent you spawn.

- Do not redesign or restructure the Shop tab. You add one row, one
  `action_type` handler, and the contained item picker that handler needs.
  Changing how the three existing service kinds or the shop stock render is the
  stop-and-report gate in section 3.
- Do not change the Bank surface.
- Do not delete any worktree, however merged or clean it looks. This is an
  owner gate and it is not released to you.
- Do not commit to `main`. Only the orchestration seat merges to `main`.
- Do not push to any remote, do not change git config, do not skip hooks, do
  not use an interactive `-i` flag.
- Do not weaken a test, an audit, or a pinned baseline so your work can pass.
- Do not invent a mechanic and describe it as settled.
- Do not ask another agent session to rule on a conflict or to grant you
  permission. The orchestration seat is your only escalation route.

## 7. Your worktree

```
python3 tools/worktree_guard.py audit
python3 tools/worktree_guard.py lease goal/beefy-bill-service-2026-09-01 --holder beefy-bill
```

The last stdout line is JSON with `path` and `lease_id`. Work there, commit
there, then release with
`python3 tools/worktree_guard.py release <path> --lease-id <id>`. Run the guard
audit again at the end. Never call `treehouse` directly.

## 8. Verification

**Promotion gate.** The orchestration seat re-runs both lanes on the merged
tree. Run the plain lane only, and say in your report that you did so:

```
/opt/homebrew/bin/python3 run_tests.py
```

This repository's own record warns that full lanes take 774 to 1,036 seconds
and exceed the background-task cap, so run a long lane under shell-level
detachment rather than letting the harness void it at ten minutes.

Because you edit files other slices share, run the existing suites for
`logic/shop_logic.py` and `ui/ui_tab_shop.py` as well as your own focused
tests. That is the cheap neighbour check contract section 6 requires.

Also run, and report the exact output of:

```
python3 tools/audit_docs.py
python3 tools/audit_test_quality.py
python3 tools/audit_item_reachability.py
python3 tools/worktree_guard.py audit
git diff --check
```

Prove the behavior by driving the real kernel, not by importing the module.
Perform the service through the real runtime path, show the chosen items leave
the carried view and arrive in the Bank, show the cut taken, and show
`lumbridge_medium_where_s_the_beef` move from incomplete to complete and
`lumbridge_medium` become claimable. An ordinary deposit must not satisfy the
deed, and the test that proves that negative is worth more than three that
prove the positive.

Show that a second generator run leaves the catalog byte-identical.

## 9. Your report

Write a source audit at
`memory-bank/source-audits/beefy-bill-banking-service-2026-09-01.md`. Update
`memory-bank/activeContext.md` and `memory-bank/progress.md`. Append a
timestamped line to `memory-bank/papercuts.md` for every piece of friction you
hit, in the moment.

Report exact numbers, identifiers, paths and error strings verbatim, and
re-measure every number when you write the report. Name every source you pinned
with its dated `oldid` or file path, every placeholder you registered, the
exact rendered appearance of the new row with its offscreen check at both
sizes, and whether any existing user interface changed. State plainly what you
did not do and why.
