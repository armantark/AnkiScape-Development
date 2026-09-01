# Shared source-harvest ledger — pointer

Date: `2026-07-25`

Status: **the canonical file is a historical pinned-result index; its live
work-in-progress coordination is retired.** Read its pinned results before any
harvest task so you never re-harvest a settled subject. Live claims on
dual-eligible units go by doorbell between the two orchestrator threads, per
the standing rule in `codex-briefs/STANDING-SLICE-CONTRACT.md` §4 (owner
ruling of 2026-08-31).

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

1. Read the canonical file before you start a harvest task.
2. Add your task to its "Work in progress" table when you start.
3. Move your task to its "Pinned results" table when you finish. Give the exact
   record path.
4. Delete your row if you abandon the task.

## 4. Why the canonical file sits in the other repository

The Darkan session works in that repository and reads its memory bank each
session. A pointer costs this session one file read. A missed ledger costs both
sessions a duplicate harvest.
