# Evergreen sap acquisition, 2026-10-02

Authority: section 6 of the qualified packet at
`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-02/quest-action-sources-2026-10-02.md`.
No new source harvest was performed.

- [Bucket of sap, oldid 6288759](https://runescape.wiki/w/Bucket_of_sap?oldid=6288759), 2012-09-24T05:53:15Z: one empty Bucket and a retained Knife, including a tool-belt Knife, collect sap from an evergreen.
- [Evergreen, oldid 6310045](https://runescape.wiki/w/Evergreen?oldid=6310045), 2012-09-28T05:37:13Z: the output is Bucket of sap. The packet's build-727/742 cache evidence identifies item 4687. Chopping level 1 does not establish a sap skill gate or XP award.
- [The Eyes of Glouphrie, oldid 6371270](https://runescape.wiki/w/The_Eyes_of_Glouphrie?oldid=6371270), 2012-10-08T12:33:57Z, and [Questreq, oldid 6552449](https://runescape.wiki/w/Template:Questreq?oldid=6552449), 2012-11-13T19:50:29Z: Construction 5, Magic 46 and The Grand Tree are quest-start gates, not sap acquisition gates.

The packet reconciles Darkan commit `06b4e277e10c846b1a2746d9e57df723edbeb5e9`,
`/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/src/main/java/com/rs/game/content/quests/icthlarins_little_helper/IcthlarinsLittleHelper.kt:718`,
and its replacement helper at line 489 with the period item prose. The handler
replaces the empty bucket with the filled bucket and does not debit the knife.

The implementation uses the existing deterministic Utility transaction and
successful event recorder. One review consumes one Bucket and produces one
Bucket of sap, with no XP, skill gate or quest-state gate. The retained tool
availability uses the existing always-filled tool-belt Knife. Only successful `collect_evergreen_sap`
events emit `Collect a bucket of sap from an evergreen tree`; chopping does not.
Review Undo restores the transaction and proof through the existing snapshot.
The output item and its `questitems/bucket_of_sap.png` asset already exist.

The separate stage-3 generated sentinel
`Complete The Eyes of Glouphrie stage 3 objective` remains outside this slice.
The advancement fixture supplies that sentinel and a Mud rune before testing
the sap gate; it does not claim whole-quest parity.
