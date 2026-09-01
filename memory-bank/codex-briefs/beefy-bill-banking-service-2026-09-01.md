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

## 2. The surface is ruled, and the other one is a gate

The design seat ruled this on 2026-09-01 (rulings ledger section 28): build a
**new contained Utility action**. Follow the precedents already in the tree.

- The registry is `UTILITY_ACTIVITY_DATA` at `core/constants.py:537`.
- `data/evil_tree_data.py` and `data/big_chinchompa_data.py` show the data
  conventions, including how each file pins its period source at the top and
  names any review-scale abstraction as an abstraction rather than as a
  recovered formula.
- `logic/review_strip_logic.py` shows how a Utility activity reaches the
  review strip.

**Gate.** Beefy Bill's existing shop surface, rendered through
`ui/ui_tab_shop.py`, is off limits. Attaching the service there would change an
existing user interface, which needs the owner's explicit approval. That option
is parked with the design seat. Do not touch it, do not prepare for it, and do
not add a seam "for later".

Your new Utility row is a new interface, so the orchestrator sends it to a
frontend-taste model for review before it is promoted. That review is the
orchestrator's job, not yours. Build the surface to the same standard as the
existing Utility rows and say in your report exactly what it renders.

## 3. Sourcing, which is the real work

Harvest the fee and the accepted items in the contract's evidence order:
Darkan first, then the rev-727 cache, then game-main, then the other on-disk
OpenRS2 caches, then the wiki as corroboration at a pre-cutoff `oldid`. The
cutoff is `2012-11-20T00:00:00Z`.

Follow `memory-bank/pre-eoc-source-verification-standard.md`.

Three things the deed itself constrains, from the diary ledger row
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

So the service must move a **player-selected** item into the bank, and it must
be distinguishable from an ordinary deposit.

**Gate.** If the fee or the accepted item set cannot be recovered from any
source in the evidence order, do not invent one and present it as settled.
Register the unrecovered value in `memory-bank/placeholder-values.md` with a
`PLACEHOLDER(...)` marker, exactly as the contract's sourcing section requires,
and say in your report which values are placeholders and why. An unmarked
reconstruction is invisible to the placeholder audit and is a defect.

## 4. Wiring the deed, and the tier it unlocks

The service's bank write records Beefy Bill as the service source, so the deed
becomes observable.

Then, and only then:

1. Edit the row `lumbridge_medium_where_s_the_beef` in
   `memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl`. Its
   `disposition` becomes `active` and its `future_system` becomes `null`. Keep
   the exact key order the ledger README specifies. Keep the citation intact.
   Update `notes` to name the new seam.
2. Regenerate through `tools/generate_achievement_diary_data.py`.
3. Never hand-edit `data/achievement_diary_catalog.py`. The owner made the
   generator route the condition of the gate that authorized this work.

`lumbridge_medium` then reaches 12 of 12 and becomes the product's first
claimable tier. Measure that, do not assume it: the claimable tier count moves
from 0 of 34 to 1 of 34. If your measurement disagrees, report the measurement
rather than the expectation.

`lumbridge_easy_money_down_the_drayn` stays `dormant`. Its trigger needs a
Draynor Village bank identity, and the Bank is locationless by settled design.
Do not touch that row.

## 5. Prohibitions that apply to this workspace

Forward every one of these to any child agent you spawn.

- Do not change an existing user interface. This includes the Shop tab and the
  Bank surface. A new contained Utility row is what you are authorized to add.
- Do not delete any worktree, however merged or clean it looks. This is an
  owner gate and it is not released to you.
- Do not commit to `main`. Only the orchestration seat merges to `main`.
- Do not push to any remote, do not change git config, do not skip hooks, do
  not use an interactive `-i` flag.
- Do not weaken a test, an audit, or a pinned baseline so your work can pass.
- Do not invent a mechanic and describe it as settled.
- Do not ask another agent session to rule on a conflict or to grant you
  permission. The orchestration seat is your only escalation route.

## 6. Your worktree

```
python3 tools/worktree_guard.py audit
python3 tools/worktree_guard.py lease goal/beefy-bill-service-2026-09-01 --holder beefy-bill
```

The last stdout line is JSON with `path` and `lease_id`. Work there, commit
there, then release with
`python3 tools/worktree_guard.py release <path> --lease-id <id>`. Run the guard
audit again at the end. Never call `treehouse` directly.

## 7. Verification

**Promotion gate.** The orchestration seat re-runs both lanes on the merged
tree. Run the plain lane only, and say in your report that you did so:

```
/opt/homebrew/bin/python3 run_tests.py
```

This repository's own record warns that full lanes take 774 to 1,036 seconds
and exceed the background-task cap, so run a long lane under shell-level
detachment rather than letting the harness void it at ten minutes.

Also run, and report the exact output of:

```
python3 tools/audit_docs.py
python3 tools/audit_test_quality.py
python3 tools/audit_item_reachability.py
python3 tools/worktree_guard.py audit
git diff --check
```

Prove the behavior by driving the real kernel, not by importing the module.
Perform the service through the real runtime path, show the item arrive in the
bank, and show `lumbridge_medium_where_s_the_beef` move from incomplete to
complete and `lumbridge_medium` become claimable. An ordinary deposit must not
satisfy the deed, and a test that proves that negative is worth more than three
that prove the positive.

Show that a second generator run leaves the catalog byte-identical.

## 8. Your report

Write a source audit at
`memory-bank/source-audits/beefy-bill-banking-service-2026-09-01.md`. Update
`memory-bank/activeContext.md` and `memory-bank/progress.md`. Append a
timestamped line to `memory-bank/papercuts.md` for every piece of friction you
hit, in the moment.

Report exact numbers, identifiers, paths and error strings verbatim, and
re-measure every number when you write the report. Name every source you pinned
with its dated `oldid` or file path, every placeholder you registered, and
exactly what your new Utility row renders. State plainly what you did not do
and why.
