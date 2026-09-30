# Shared source-harvest ledger — pointer

Date: `2026-07-25`

Status: **the canonical file is a historical pinned-result index; its live
work-in-progress coordination is retired.** Read its pinned results before any
harvest task so you never re-harvest a settled subject. Live harvest claims go
by doorbell between the two orchestrator threads, per the standing rule in
`codex-briefs/STANDING-SLICE-CONTRACT.md` §4 (owner rulings of 2026-08-31 and
2026-09-25, section 3 below).

## 1. Goal

The AnkiScape session and the Darkan session run at the same time. Both read the
same sources. This pointer sends you to the file that prevents duplicate work.

## 2. Canonical file

```
/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/shared-source-harvest-ledger.md
```

The file holds one copy of the ledger. Do not copy its content here. Two copies
drift apart and then neither session can trust either one.

## 3. Rules

### Owner rulings, 2026-09-25

- The Darkan repository implements quests and miniquests in-game, including achievement task hooks. The 2026-07-18 wording "Ankiscape owns quest implementation" was never approved. The thread split covers source harvesting only (R26). Record: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/restoration-loop-contract.md`, section "Owner ruling, 2026-09-25 (direct): this repository implements quests", commit `0fedf10d`. That section says "AnkiScape writes no in-game quest code"; Darkan's `loop-state.json` `dual_eligible_claim_policy` at the same commit and at `b870c231` names one exception, "AnkiScape holds the waiver for skippy_and_the_mogres", which AnkiScape used under its 2026-08-31 waiver: that miniquest landed on main at `9b933084`.
- Deduplicate harvesting for every subject: quest, skill, item, NPC, region, minigame and system. Check the canonical ledger and the other thread's claims, doorbell the other thread, then record a claim before harvesting. The first recorded claim owns that subject's harvesting; neither thread re-harvests a subject the other pinned. The AnkiScape brief template must carry this rule for every source-harvesting slice. Darkan records: `restoration-loop-contract.md` ruling of 2026-09-25 and `loop-state.json` `dual_eligible_claim_policy`, commit `b870c231`.
- Darkan's **249 revisions** under `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/prep-2026-09-25/` are pinned; subjects are the file names. The `2026-09-25T17:05` doorbell reported about 250 revisions and 166 ledger entries at commit `6ab9346a`; the `2026-09-25T17:14` correction pins all 249. Both came from session `2012scape-with-bots-2b`; AnkiScape held no conflicting quest claim.
- Peer doorbells are part of the goal for quest claims, source pins, shared MacBook screen use and split changes. Provenance: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/orchestrator-notes-2026-09-25.md`.

Follow the 2026-09-25 procedure above; the old work-in-progress table is retired.

## 4. Why the canonical file sits in the other repository

The Darkan session works in that repository and reads its memory bank each
session. A pointer costs this session one file read. A missed ledger costs both
sessions a duplicate harvest.

## 5. AnkiScape claim — Trio Monkey / Shaikahan bones, 2026-09-29

AnkiScape claims the Tai Bwo Wannai Trio stage-3 Monkey combat binding and the normal-player Shaikahan bone route on `goal/shaikahan-route-2026-09-29`. The Darkan restoration thread answered the orchestrator's doorbell at `2026-09-29T14:08-07:00`: no claim or open work on the Trio Monkey encounter or Shaikahan, and no known source evidence for or against the `nostats` values for November 2012. This records the supplied coordination result; no author-side doorbell or new source harvest was performed.

The binding uses only the retained `darkan-world-server/data/npcs/combatdefs/uncategorized/monkey (nostats).json` snapshot at `f5f2782af855b3af8240b6f3ec91f9af12eb9f0c`. Its 60 LP, explicit zero combat levels, maximum hit 24, melee style and passive aggression are **unverified retained Darkan data, not period-verified values**. The existing period-attested Monkey identity and level remain unchanged. These values require the registered `quests.tai_bwo_wannai_trio.monkey_combat` placeholder under the breadth-phase rule, not a parity-closure claim. No Darkan repository file is changed.
