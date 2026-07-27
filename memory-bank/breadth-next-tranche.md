# Breadth-first: the next tranche

Status: **rewritten 2026-07-26, after nine families landed.** The previous version
of this file planned batches A, B and C. Batch A is finished, batch B is two
families in, so the ordering below is what actually remains.

## Where the programme stands

`main` is clean at 3,017 tests and green in both lanes. No worktree is open and
nothing is interrupted.

Nine families reached breadth one on 2026-07-26: Skeletal Horror, Duel Arena,
Clan Wars, Daily Challenges, Treasure Trails (Easy), Tears of Guthix, Enchanted
Key, The Crucible, and Goblin Raids. All nine survived an independent Sol
verification, which found four real bugs that three earlier Claude passes had
cleared. Those are fixed and merged.

## What remains

| family | estimate | source state |
| --- | --- | --- |
| Shattered Heart | 14-20 h | no audit |
| Troll Invasion | 14-20 h | no audit |
| Mage Training Arena | 14-20 h | no audit |
| Temple Trekking | 14-20 h | no audit |
| Dominion Tower | 14-20 h | no audit |
| Gnome Restaurant | 12-18 h | no audit, and it carries design fork 3.7 territory |
| Mobilising Armies | 18-26 h | no audit |
| Achievement Diaries | 30-45 h | large; other families reference its substrate |
| Dungeoneering | 40-64 h | plus source research; its data module parks the Skills surface |
| Conquest | 20-30 h | sequenced after Dungeoneering by the programme |

**Do not plan from these estimates.** They come from a frontier audit that
predates both the placeholder rule and the parallel-agent workflow, and they are
solo human-hours. Measured against how families actually land now, they are off by
roughly an order of magnitude: nine families reached breadth one on 2026-07-26 in
a single day, several of them carrying estimates of 14-20 hours each. The owner's
own read is that Achievement Diaries is "at most an overnight run, maybe 2-4
hours". Treat the column as a rough ordering of relative size and nothing more.

**Bork is dependency-blocked, not source-blocked.** It needs the `Hunt for Surok`
miniquest and the regional Achievement Diary substrate, and neither exists. Do not
schedule it as an ordinary family. See `source-audits/bork-loop-2026-07-18.md`.

**Gnome Restaurant** still carries the presentation fork deferred in
`source-audits/gnome-restaurant-delivery-loop-2026-07-17.md`. The placeholder rule
makes its data surface approximable, so the fork is now answerable — but it is the
owner's, and it belongs in the design queue as a concrete choice once the data
shape exists.

## What every brief must carry

The failure modes below are not hypothetical. Each one shipped this week, and the
last four were caught only by execution after three review passes had cleared them.

1. **An invented mechanic advertised as settled.** Skeletal Horror banked two
   weekly entries, written into the UI, the memory bank and a test name.
2. **Tests that prove nothing.** Stubbing the system under test makes a green
   suite compatible with a feature that cannot work at all. One Skeletal Horror
   test asserted item and grave behaviour it could never observe, because it
   stubbed the reducer that produces both.
3. **An inert row.** A reward gated on a state no player reaches. The Crucible's
   Supreme helm was one until rank-point persistence was corrected.
4. **The panel re-deriving a rule the logic layer owns.** Found in Duel Arena and
   then in Skeletal Horror. The `*_view_pure` owns every enable and visibility
   decision.
5. **An unlabelled reconstruction.** The placeholder register test can only see
   values that carry a `PLACEHOLDER(...)` marker, so an invented value with no
   marker is invisible to it. Three reached a merged family this way.

## Model routing for the next run

Verify Claude-authored families with Sol, not with another Claude model. One Sol
pass found four shipped defects that three Claude passes had missed, and the
difference was lineage rather than effort.
