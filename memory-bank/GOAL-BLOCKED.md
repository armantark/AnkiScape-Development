# Goal blocked — 2026-09-17 09:00 PDT

Thirteen slices landed this session, main `8283ad9d` to `83c69197`, 37 commits.
A fresh measured audit at `83c69197` follows. Three units remain and none can be
advanced by this seat. Delete this file when any single item below clears.

## Audit, measured not asserted

`memory-bank/loop-queue.md` has two open entries, at lines 197 and 212.
`memory-bank/goal-priority-matrix.md` has three live rows not closed, at lines
56, 58 and 64; every other open row sits in the section the file itself labels
"Initial ordered-work audit — historical".

Twelve `goal/*` refs still hold commits main lacks. Each was checked by whether
its effect is live on main, not by its ref state:

| Check | Result |
| --- | --- |
| Six items tradeable: Spotted cape, Spottier cape, Jade, Red topaz, Crayfish, Archery ticket | live |
| `data/quest/combat_relocation.py` | live |
| Ghosts Ahoy carries both prerequisites | live |
| Skippy and the Mogres in the catalogue | live |
| Alfred Grimhand's Barcrawl in the catalogue | live |
| `goal/diary-ledger-wiring-2026-09-01` merge result | byte-identical to `main^{tree}` |

The remaining refs are `excluded_ui` or preserved-and-rejected per the branch
disposition table in the matrix. No accepted slice is unmerged.

## 1. Native acceptance, matrix rows 56 and 58

**Blocked on:** an owner decision.

The native Computer Use turn `01a07328-ea27-7391-9f2f-33f297d389ab` sits at
`waitingOnApproval` through the normal unsandboxed approval flow, and the matrix
records that no bypass is authorized.

**What I tried.** I re-measured the recorded cause. On the MacBook,
`/usr/bin/sandbox-exec -p "(version 1)(allow default)" /usr/bin/true` now exits
`0`, where the 2026-09-05 canary recorded exit `71` with
`sandbox-exec: sandbox_apply: Operation not permitted`. That does NOT clear the
blocker: line 134 of the matrix already states the failure occurred in the
native actor's tool context and does not establish OS-wide unavailability, so an
OS-level probe is the wrong measurement. I briefly mistook it for one.

**The single thing that would unblock it.** You approving or re-issuing that
native turn, or telling me a different route to native acceptance is authorized.

## 2. Emerald sickle, matrix row 64

**Blocked on:** the Myreque quest chain being playable.

**What I tried.** I implemented it. The mechanics are correct and were proven
live: fitting consumes an Emerald and a blessed silver sickle, retains the
Chisel, produces item `13155` and awards 20 Crafting experience; the standard
Level 2 Enchant then consumes `13155`, one Cosmic and three Air runes, produces
`13156` and awards 37 Magic experience at Magic 27, with Legacy of Seergaze's
own eligibility left at Magic 49.

It cannot land. Both new items are unreachable, taking orphan inputs from `163`
to `164` and unresolved actions from `249` to `251`, because Legacy of Seergaze,
The Darkness of Hallowvale, In Aid of the Myreque and In Search of the Myreque
stop at generic stage-one objectives, so no player reaches Legacy stage 6.
Landing it would add inert content, which this project treats as a defect.

The work is preserved at `refs/preserved/emerald-sickle-2026-09-17`, commit
`85c610ed`. Note it also contains a large unrequested split of
`tools/audit_item_reachability.py` which is not wanted; take the Emerald changes
only.

**The single thing that would unblock it.** Making that quest chain playable to
Legacy of Seergaze stage 6.

## 3. Source-blocked values

**Blocked on:** period evidence that does not exist in reach.

- Silvthrill rod: the item transition is unresolved among `7620`, `7637` and `7638`.
- Fremennik shield: Woodcutting is contradictory at `54` versus `56`.
- Frost dragon bones: no period source maps items `18830` and `18832`
  one-to-one to the Asgarnian Ice Dungeon and Daemonheim routes.
- Ghosts Ahoy full quest: requirements, route values, rewards and downstream
  unlocks are unrecovered. Its prerequisite is done and landed at `c276ef40`.

**The single thing that would unblock each.** A dated pre-cutoff source that
states the value. Do not accept a matching name or a cache identity alone.

## One standing lesson

Three recorded blockers dissolved on contact this session because the repository
moved underneath them: the promotion gate's Qt lane ceiling, which was correct
and simply needed the MacBook rather than the Mac Studio; a `systemPatterns.md`
passage that had been relocated rather than deleted; and a Ghosts Ahoy generator
split measured against a `2621`-line file that no longer exists. Re-measure a
blocker before trusting it, and re-measure the right thing.
