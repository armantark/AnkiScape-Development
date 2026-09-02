# Claim record: Bar Crawl miniquest — 2026-09-02 09:41 PDT

The AnkiScape orchestration seat claims the Bar Crawl miniquest and its
harvesting, under the dual-eligible claim-first rule of
`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md` section 4.

The other project's design thread answered the doorbell with no claim and no
pinned dossier: no unit row named Bar Crawl exists in any of its 12 ledgers,
and no pinned source or contract covers it. It is a miniquest-axis gap in that
project's inventory, as `skippy_and_the_mogres` was.

Leads that thread gave, recorded as leads and not as evidence:

1. The Darkan tree implements the miniquest at
   `darkan-world-server/src/main/java/com/rs/game/content/miniquests/bar_crawl/`
   (`BarCrawl.kt`, `BarEffects.kt`, `BarbarianGuardD.kt`). It is an
   implementation reference, in the way the Zogre stages were used.
2. Two of that project's COMPLETE quest units, `quests-scorpion-catcher` and
   `quests-horror-from-the-deep`, reference the bar-crawl gate in
   runtime-verified rows in `memory-bank/audit/ledgers/quests.jsonl`. Those
   proofs are evidence that the gate works. They are not period proof of the
   miniquest's internal values, and that thread says so itself: the bar list,
   the prices and the effects are unpinned on its side.

So our harvest is the first pin of those values, and a later Darkan audit will
start from it. The other thread asked for two things when the slice lands: the
dated revisions pinned durably, and a doorbell naming the paths.

Why this unit is in front of us at all: `bar_crawl_completed` is read once at
`logic/agility_logic.py:282` and written nowhere in the tree, so Horror from
the Deep is gated behind a miniquest no player can complete. That is the
section 13 unstartable-quest defect, and the design seat ruled Bar Crawl folds
into the Horror from the Deep slice.

This file lives under `memory-bank/pending/` because a landing window was open
when it was written (ruling 38.2). It folds into the tracked record after the
window closes.
