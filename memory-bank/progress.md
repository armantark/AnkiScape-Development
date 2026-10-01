# Progress

This log keeps the current month. Earlier months rotate into `memory-bank/archive/` on the first session of each month; May to August 2026 is in [the May–August progress archive](archive/progress-2026-05-to-08.md), and the rotated September 2026 sections are in [the September progress archive](archive/progress-2026-09.md).

## Pass 15 owner notes — eight slices, 2026-09-30 to 2026-10-01

Ten notes from `~/Downloads/ankiscape notes.rtfd` (Pass 15, 2026-09-15 to 2026-09-30); rulings `design-thread-queue.md` §4.28, brief `codex-briefs/pass15-owner-notes-handoff-2026-09-30.md`. Opus 5.5 authored every slice at the owner's request; Kimi K3 reviewed five diffs and GPT-6.1 Sol the other three after Kimi's 5-hour limit (`403 You've reached your 5-hour usage limit`). Integration branch `goal/pass15-integration`.

- Finisher notice (`goal/pass15-finisher-notice`, 54196a1d, 416c2a86): "Wear Spiked gauntlets to finish" on its own amber HUD line; one event-log line per encounter, marked on the encounter record after the review found a missed warning on a new spawn and a repeat on Gargoyle regeneration.
- Bank trip target switch (ccba1926, e830d5b4, 01457f45): a target switch cancels a pending trip for another target.
- Fishing guide levels (a526d1b1): one guide row per fish at its own level; slimy eel 28; 2012 eel and frog spawn spots; the Lumbridge "Eel of Fortune" deed now counts a Raw cave eel.
- Silverlight and quest fights (9a2b4fc2, 9d03bf68, f244471b): every equippable quest reward is wearable (equipment count 994 to 1049); quest fights take ordinary ticks per review; Delrith needs a wielded Silverlight; the HUD names the boss.
- Barcrawl steps (a953836b): ten automatic stages at 2012 prices (208 coins); the shop drink rows and proofs are gone; quest-blocked dialogs list one reason per line.
- Belt tools (7bca9f86): the 2012 tool belt is one constant and one predicate for quests, Farming and Vinesweeper; ten bare-ground spade digs and the period exceptions stay held; the Bank Toolbelt panel lists the belt.
- Shop locks and purchase (1d401116, 5e3000e4): locked shops sort last, dim and name their reason; a purchase chip under Buy, green for success, amber for a refusal.
- Skill target search (eda7c2ed, 06fa2da4): every Skills-tab target list has the Combat search bar through `ui/ui_target_search.py`.

Merge repair (42adb030): eight module-surface digests, the root Qt digest and the equipment count re-pinned on the merged tree; the locked-shop wrap test fixed to a 240 px list because the test host's font fit the longest label (`382 not greater than 392`). First merged gate on a22202c6 failed only on those pins, that test, and three video status pages (fixed on main at 6637e281). Second gate on 231cdd1a with `--remote-lanes`: plain `Ran 5097 tests in 471.671s`, `OK (skipped=558)`; offscreen Qt `Ran 5097 tests in 686.769s`, `OK (skipped=5)`; documentation, test-quality, reachability, worktree, diff and papercut checks passed. Landed on main as 231cdd1a on 2026-10-01 01:30; the owner must restart Anki to load it.

Second level, not fixed: the combat chips line "Kills: N · Trains ..." clips at 192 px beside Bank run for aggressive and controlled styles on main today; Phoenix Lair still asks for Knife, Secateurs and Tinderbox in the bank; the flat target list clips long locked-row labels behind a horizontal scrollbar; skill guide rows dim only by level, not by quest lock; Count Draynor's garlic, Spiked gauntlets price, Do No Evil and Fremennik Isles purchase proofs, 90 of 293 quest encounters without stats.
