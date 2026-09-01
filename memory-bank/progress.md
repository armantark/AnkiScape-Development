# Progress

## Goblin Diplomacy acquisition chain closed — 2026-08-30

Goblin Diplomacy consumed Orange goblin mail, Blue goblin mail, and plain Goblin
mail, but the dye and recolour products had no player-finishable producers. The
period route is now live through the established Utility contract. One review
searches the three documented Goblin Village crates. Aggie consumes three
Redberries and 5 Coins for Red dye, two Onions and 5 Coins for Yellow dye, and
two Woad leaves and 5 Coins for Blue dye. Red plus Yellow makes Orange dye, and
each coloured dye consumes one plain mail. The complete chain starts with 15
Coins and leaves one orange, one blue, and one unchanged brown mail for the
three ordered quest turn-ins.

The source audit pins six exact pre-cutoff wiki revisions, literal wikitext,
rev-727/rev-742 item definitions, rev-742 crate/NPC options, 2011Scape source
paths, and read-only Darkan paths and supplying commits. It also records the
baseline correction: the items and plain-mail combat route already existed;
the original `--names` search had inspected file names. Item identities now
preserve mail IDs `286`/`287`/`288`, dye IDs `1763`/`1765`/`1767`/`1769`, Woad
leaf `1793`, Redberries `1951`, and Onion `1957`, together with the cutoff flags
and existing provenance-pinned art. No placeholder is needed by the guaranteed
crate and deterministic recipe chain.

The seven reachability pins change from 1,601 actions, 2,237 reachable items,
190 orphan inputs, 39 root orphans, 151 cascade orphans, 277 unresolved actions,
and 1,177 seed items to 1,608 / 2,243 / 190 / 39 / 151 / 277 / 1,177. Goblin
Diplomacy clears `blocked_quest_stage_products`; blocked quest-stage rows fall
from 146 to 145. Completable quests move from 43 to 44, and startable quests
from 113 to 114. The Lost Tribe is now startable but remains non-completable at
`Complete The Lost Tribe stage 2 objective`, so this slice does not claim that
chain is closed.

Focused verification passed six plain tests and two offscreen Qt tests. Full
plain passed 4,548 tests in 407.900 seconds with 515 skips. Genuine offscreen Qt passed 4,548 tests in 697.572 seconds with three skips. The
documentation audit passed across 609 Markdown and 441 HTML files; the test
quality audit measured 4,513 tests across 221 files, zero hard issues, and 31
structural-clone candidate groups. Geometry and screenshots at default 720×540
and laptop-height 1080×560 showed no label truncation or horizontal overflow.
The final reachability command retains exit 1 only because 190 unrelated orphan
inputs remain globally, and the guarded worktree layout is safe.

## Ordinary Snake-hide acquisition route closed — 2026-08-30

The ordinary Snake hide item and its six downstream states were registered but
not reachable from any player-finishable producer. The live Combat catalog now
adds Bush snake as the period Tai Bwo Wannai Cleanup source. The target uses the
existing selector and requires completed Jungle Potion, Woodcutting 10, and a
carried or equipped Machete. It preserves the period level-35 identity, 250 LP,
38 maximum hit, Melee style, attack speed 7, guaranteed Bones, and guaranteed
1–5 ordinary hides, together with Darkan's reconstructed hidden combat levels
and respawn delay.

The evidence chain pins Bush snake oldids `6352282` and non-beta `5190727`,
Snake hide oldid `6009794`, Tai Bwo Wannai Cleanup oldid `6539724`, Jungle
Potion oldid `6555418`, OpenRS2 revision 742 NPCs `2489`/`2490` and item `6287`,
and Darkan commits `14e49a561bab1441384022421d10dc03a8d837f0` and
`c6fbe036b1743f4dd6067ec178332c69c3708856`. The hidden 1–5 quantity weighting
uses registered placeholder `combat.bush_snake_hide_quantity_distribution`,
and the absent numeric combat bonuses use
`combat.bush_snake_combat_bonuses`. The period 68-LP poison is represented by
the shared engine's nearest 70-LP tier; the rev-742 `attackDelay=3` conflict and
Darkan's fixed-one-hide conflict are recorded rather than hidden.

The ordinary item now explicitly retains item id `6287`, non-stackability, and
tradeability. Its existing 28×28 sprite remains registered. The new 48×42 Bush
snake sprite is source-period and provenance-pinned. Integration coverage kills
a real low-HP copy of the target, tans the resulting hide through the real
Utility reducer, verifies save persistence through the real review runtime,
and restores the exact pre-review state through Anki answer undo. The shown and
resized offscreen Qt row has its icon, full text, no horizontal overflow, and no
truncation.

The seven pinned reachability metrics changed from 1,600 actions, 2,217
reachable items, 192 orphan inputs, 40 root orphans, 152 cascade orphans, 284
unresolved actions, and 1,164 seed items to 1,600, 2,224, 190, 39, 151, 277,
and 1,165. Routes now resolve for ordinary Snake hide, Snakeskin, and all five
Snakeskin armour pieces. Focused non-Qt verification passed 712 tests. Full
plain passed 4,539 tests in 402.985 seconds with 514 skips; genuine offscreen Qt
passed 4,539 tests in 700.027 seconds with three skips. Documentation audited
606 Markdown and 441 HTML files. Test quality reports 4,504 tests across 221
files and zero hard issues. `Snake hide (swamp)` remains separate follow-up
work; it was not aliased to ordinary item `6287`.

## The Lost Tribe stages 2–5 are source-backed and completable — 2026-08-31

The direct Darkan Kotlin implementation now closes the intermediate varbit
`532` meanings that the older derived evidence contract could not name.
`TheLostTribeState.kt` defines all twelve states, and `TheLostTribe.kt` provides
executable transitions for the brooch, symbol book, goblin generals, tunnel
symbols, Mistag's return to Lumbridge, Sigmund's chest, silverware, treaty
delivery, and final signing.

The four remaining generated sentinels are replaced by same-stage automatic
actions. Thieving `13` remains the only stage-5 skill gate. Quest-local items
Brooch `5008`, Goblin symbol book `5009`, Sigmund's key `5010`, Silverware
`5011`, Peace treaty `5012`, and all seven H.A.M. outfit pieces remain follow-on
acquisition leads; no unavailable item was turned into a blocker and no new
interface or runtime path was added.

Re-measured reachability moves from `1608 / 2243 / 190 / 39 / 151 / 277 / 1177`
to `1608 / 2244 / 190 / 39 / 151 / 277 / 1179`. Blocked quest-stage rows fall
from `145` to `144`, and The Lost Tribe has no row in
`blocked_quest_stage_products`. Completable quests move from `44` to `45`, with
The Lost Tribe as the sole addition; its `13` transitive descendants remain
blocked by their own generated sentinels. Focused tests pass seven cases;
test quality
reports 4,516 tests across 222 files with zero hard issues, and the documentation
audit passes across 610 Markdown and 441 HTML files. Full source evidence and
the item follow-on list are in
`memory-bank/source-audits/the-lost-tribe-stages-2-5-2026-08-31.md`.

## The Lost Tribe stage-1 cellar path is source-backed — 2026-08-30

A Darkan doorbell identified the stage-1 cellar contract in the read-only target
record, baseline world commit `e720c3e1f18960653695042b392f4d1180a07b76` and
tree `69353b61f8cd7a2783729fcf7e99df5de4ce23a4`. AnkiScape independently fetched
literal historical wikitext and pinned The Lost Tribe oldid `6534350` at
`2012-11-04T20:05:19Z` and Template:Questreq oldid `6552449` at
`2012-11-13T19:50:29Z`. The article, resolved requirement template, and Darkan
contract agree on Goblin Diplomacy, Rune Mysteries, Mining `17`, Agility `13`,
Thieving `13`, the pickaxe, and the lit source. The local revision-667
2011Scape snapshot confirms varbit `532` only; its intermediate semantics remain
inside the exact
`PARTIAL[source_blocked,conflicting_sources,missing_data]` source block and were
not inferred.

The generated `Complete The Lost Tribe stage 1 objective` gate is gone. Quest
acceptance now uses only the two direct quest prerequisites. Stage `1` reuses the
existing quest skill, toolbelt, lit-source alternative, blocker, and auto-action
contracts to require Mining `17`, Agility `13`, a pickaxe, and an illuminated
source before recording the mine-then-squeeze action. Missing requirements and
stage-2 attempts leave state unchanged. The duplicate stage-2 cellar gates were
removed, and Thieving `13` moved to stage `5`. No mining or Agility minigame, UI
change, placeholder value, or intermediate varbit model was introduced.

All seven reachability pins remain `1601 / 2237 / 190 / 39 / 151 / 277 / 1177`.
The exact stage-1 sentinel has no remaining location in
`missing_required_actions`; the quest now reaches its still-generated stage-2
sentinel. Completable quests remain `43 → 43`, startable quests move
`114 → 113`, and the global blocked quest-stage count remains `146`.

Final verification passed. The accepted slice's focused lane ran 88 tests in
74.237 seconds. After rebase, the plain lane ran 4,544 tests in 381.617 seconds
with 514 skips, and the offscreen Qt lane ran 4,544 tests in 680.376 seconds
with three skips. The documentation audit passed across 608 Markdown and 441
HTML files. The accepted slice's test-quality audit measured 4,503 tests across
221 files, zero hard issues, and 31 structural-clone candidate groups. Kimi K3
was unavailable with HTTP 403
`You've reached your weekly (7-day) usage limit`; the GLM 5.3 Flash substitute
found one order-coupled test assertion, which was corrected before the final
focused pass. The reachability command retains exit 1 because 277 unrelated
actions remain globally unresolved, and the final worktree layout audit is safe.

## Doogle leaves acquisition closes the Gertrude stage blocker — 2026-08-30

The Darkan thread supplied oldid `5819038` through a doorbell, and AnkiScape
independently pinned the permanent URL
`https://runescape.wiki/w/Special:PermanentLink/5819038`. The fetched revision
is `Gertrude's Cat`, parent `5807360`, timestamp `2012-06-24T05:50:56Z`. Its
literal wikitext identifies the source behind Gertrude's house, tells the
player to pick up two Doogle leaves, and confirms that the leaves are rubbed on
a raw sardine to produce a Doogle sardine. The new source audit records the
handoff so neither project harvests the revision again.

The established Utility gathering contract now exposes
`gather_doogle_leaves`: no materials, no XP, two Doogle leaves per successful
review, and the existing period sprite. The generic Utility path owns target
persistence, runtime recording, and answer undo. OpenRS2 revisions 727 and 742
both identify Doogle leaves as item `1573` and Doogle sardine as item `1552`,
non-stackable and non-exchangeable, so the quest-item registry no longer uses
generic defaults for either item. The source states the batch quantity; there
is no hidden roll and no placeholder register entry.

Reachability moves from 1,600 actions, 2,217 reachable items, 192 orphan
inputs, 40 root orphans, 152 cascade orphans, 284 unresolved actions, and 1,164
seed items to 1,601 / 2,230 / 192 / 40 / 152 / 284 / 1,176. Gertrude's Cat
stage 5 is absent from `blocked_quest_stage_products`. The completable-quest
count rises from 40 to 43; the newly completable quests are Gertrude's Cat,
Icthlarin's Little Helper, and Smoking Kills.

The audit keeps `Stew` reachable but changes its selected route from
`shop:warrior_guild_food_shop` to `quest:gertrudes_cat`; that pre-existing
route-attribution order dependence is recorded but not changed here. Doogle
sardine also retains its pre-existing `food` category because the pinned quest
revision proves only that Fluffs consumes it; a separate item-page audit must
settle player edibility before changing the category.

Final local verification passed. Plain ran `4535 tests in 396.606s`,
`OK (skipped=513)`; offscreen Qt ran `4535 tests in 686.415s`,
`OK (skipped=3)`. The documentation audit passed across 606 Markdown and 441
HTML files. The test-quality audit measured 4,500 tests across 221 files with
zero hard issues. The required Kimi K3 review was unavailable with HTTP 403
`You've reached your weekly (7-day) usage limit`; Opus supplied the disclosed
taste substitute and GLM 5.3 Flash found no actionable issues in the final
cross-lineage check.

## Remote promotion sync excludes guarded-worktree links — 2026-08-30

Commit `b861cdecf96d729e1f46b200e6e9313fd0730cb8` created each guarded
worktree's `.venv-qt` as an absolute Mac Studio symlink, but the remote sync
used the directory-only pattern `--exclude=.venv-qt/`. Rsync `-a` copied the
symlink to `/Users/armantarkhanian/ankiscape-remote-test-host/repo/.venv-qt`.
Its target, `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.venv-qt`,
was absent. Six calls to `tests/test_promotion_gate.py:41-47` then failed with
this exact receiver-side error:

```
shutil.Error: [('/Users/armantarkhanian/ankiscape-remote-test-host/repo/.venv-qt', '/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/tmpf_2g1nbd/.venv-qt', "[Errno 2] No such file or directory: '/Users/armantarkhanian/ankiscape-remote-test-host/repo/.venv-qt'")]
```

Both failed gate lanes ran 4,529 tests and reported exactly six errors: plain
ran for 239.071 seconds with 513 skips, and Qt ran for 435.650 seconds with
three skips.

The production-built rsync command now uses the type-neutral
`--exclude=.venv-qt` and `--delete-excluded`. The first option stops a new
Studio-only symlink, and the second removes one already present on the
receiver. Deleting excluded receiver entries is safe because the target is a
dedicated code mirror; its real Qt environment lives outside the mirror at
`/Users/armantarkhanian/ankiscape-remote-test-host/.venv-qt`. The existing
`.git` and debug-log excludes were already type-neutral, and the supported
`__pycache__` entries are directories, so no other pattern changed.

The new behavioral test uses `_rsync_command` itself and runs rsync against a
fresh mirror and a mirror preloaded with a stale `.venv-qt` symlink. It failed
both cases before the fix, failed only the stale case after dropping the slash,
and passes after adding `--delete-excluded`. `copy_reachability_tree` remains
unchanged so the high-level gate continues to reject any unportable symlink
that crosses the transfer boundary. Final local verification was green: plain
ran `4529 tests in 385.436s` with `skipped=513`; Qt ran
`4529 tests in 698.524s` with `skipped=3`.

## Two accepted papercut branches landed — 2026-08-30

Canonical `main` is at `28c4984cc2858cd9b7d197b8fcd851220745750f` and clean.
Two of the three reviewed papercut branches merged cleanly into one promotion
worktree and landed by fast-forward after a fully green remote gate.

The evidence record
`.git/ankiscape-promotion-evidence/28c4984cc2858cd9b7d197b8fcd851220745750f.json`
completed at `2026-08-30T09:45:42-07:00` and records `remote_lanes: true`,
`plain_only: false`, and all eight passed checks. The plain lane ran
`Ran 4528 tests in 252.020s`, `OK (skipped=513)`. The Qt lane ran
`Ran 4528 tests in 444.751s`, `OK (skipped=3)`. Reachability held its baseline
exactly at `1600 actions; 2217 reachable items; 192 orphan inputs; 284 blocked
actions`.

The third branch, `goal/papercut-reachability-check-2026-08-30`, conflicts with
its landed sibling in `tests/test_papercut_tools.py` alone. Both branches added
tests to that one file, and both test sets are wanted. A dedicated agent rebases
it rather than resolving the conflict by textual union, which this project
forbids after three integrations broke the tree in 2026-07.
## Stale diary identities no longer affect live state — 2026-08-30

The skill-label correction renamed three progression-anchor task ids. Current
version-121 saves can therefore retain stale ids even though no migration can
reach them. The follow-up keeps the smaller live-state boundary: Miscellaneous
coin ordinals intersect `completed_tasks` with `_ACTIVE_TASK_IDS`, and diary
state sanitization clears a pin that no catalog task resolves. No rename-remap
migration was added.

The pre-fix measurement used all three stale anchor ids. A clean next task paid
100 coins while the stale save paid 400. Across the 35 coin-bearing
Miscellaneous rows, the clean synthetic total was 63,000, the stale total was
73,500, and the maximum excess was 10,500. After the fix, clean and stale next
tasks both pay 100; the two 35-row probes both pay 52,000 and the excess is 0.
The probe invokes all 35 rows directly, including 5 dormant rows; its purpose is
to bound stale-id influence, not to model a reachable completion sequence.

The payout regression failed before the fix with `AssertionError: 400 != 100`.
The stale-pin regression failed with
`AssertionError: 'falador_medium_reach_level_60_fletching' != ''`. Both pass
after the fix: `Ran 2 tests in 0.001s` / `OK`. Full plain verification reports
`Ran 4528 tests in 401.638s` / `OK (skipped=513)`, and genuine offscreen Qt
reports `Ran 4528 tests in 694.772s` / `OK (skipped=3)`. Test quality reports
`4493 tests across 221 files` and `hard issues: 0`; reachability remains at
1,600 actions, 2,217 reachable items, 192 orphan inputs, 40 root orphans, 152
cascade orphans, 284 unresolved actions, and 1,164 seed items.

`memory-bank/diary-curation-ledger/README.md` now states only that the 22
progression anchors are outside the ledger. The suggested non-hermetic test
that parses all 25 mappings from the external Darkan checkout remains declined:
it would make repository tests depend on that checkout's presence and revision.

## Achievement Diary skill rotation repaired — 2026-08-30

Branch `goal/diary-skill-rotation-2026-08-30` corrects
`tools/generate_achievement_diary_data.py` so skill types 17, 18, and 19 map to
Firemaking, Woodcutting, and Fletching. Direct reads of Darkan's
`AchievementDef.toRealSkillId()` and `Skills.SKILL_NAME` verify the chain. The
495-task harvest contains 34 affected skill requirements across 33 distinct
tasks: type 17 occurs 12 times, type 18 occurs 16 times, and type 19 occurs 6
times.

The required regeneration first stopped with exact error `falador medium
progression anchor ('fletching', 60) is not a sourced requirement in that
family`. Three source-backed progression anchors depended on the rotated labels
and are now Woodcutting 60, Fletching 65, and Fletching 80. The generated
catalog keeps 474 task rows and changes exactly 36: Arriving in Style; Almost
Made in Ardougne; Weeping Willow; Willow the Wisp of Smoke; Blinded With
Science; It Spoiled My View; Pyre At Will; They Like Me! They Really Like Me!;
I'm a Lumberjack and I'm Okay; I Sleep All Night and I Work All Day; The Roots
of All Evil; Deadwing; A Palm For Each Finger; Can Opener; Familiar Fire
Familiarity; See Yew at Five; The Short of It; Twisted Fire Starter; Engage;
Waka-Waka-Waka; I Swear I Heard It Scream; No Smoke Without Pyre; Make a Bolt
For It; The Long of It; Double Jointed; It All Adze Up; A Bolt from the Blue;
Are Yew As Fired Up As I Am?; Barking Up the Wrong Tree; Raising The Stakes;
Better Than Cursing The Darkness; Set It On Fiyr; Tai Bwo Wannai Cleanup; Reach
Level 60 Woodcutting; Reach Level 65 Fletching; and Reach Level 80 Fletching.
No task row was added or removed, and only string labels and the three
label-derived anchor identities changed.

A deed-grounded regression checks Pyre At Will, I'm a Lumberjack and I'm Okay,
and Make a Bolt For It. The corrected map passes; a negative control with the
old rotation produced three subtest failures. Exactly 25 curation-ledger notes
were corrected without changing any other field or row order. The 320-row
ledger recounts to 43 `active`, 247 `dormant`, 30 `translated`, and 0 `swapped`.

Verification passed: focused `Ran 2 tests in 2.718s` / `OK`; plain `Ran 4526
tests in 383.704s` / `OK (skipped=513)`; documentation `Audited 602 Markdown
and 441 HTML files.` / `Documentation audit passed.`; test quality `4491 tests
across 221 files` / `hard issues: 0`; Qt `Ran 4526 tests in 681.030s` /
`OK (skipped=3)`; and the guarded-worktree audit reported the canonical
checkout and linked-worktree root safe. Reachability remains at the seven
pinned values before and after: 1,600 / 2,217 / 192 / 40 / 152 / 284 /
1,164 for actions / reachable items / orphan inputs / root orphans / cascade
orphans / unresolved actions / seed items.

## Goal resumed, the another-writer collision is repaired — 2026-08-30

The owner set a new goal. Under it this seat repairs an another-writer
collision on canonical `main` rather than stopping at it, keeps a stored
priority matrix in the Memory Bank, coordinates with the Darkan thread through
doorbells, and changes no existing user interface.

The collision is repaired and `main` is clean again. Commit `324066da` adopts
the foreign asset-cutoff audit re-run after verification: `assets_provenance.json`
already pinned `hunteritems/withered_vine.png` to its archived pre-cutoff
revision, so the tracked audit row was stale rather than wrong. The file's
recomputed status counts equal its recorded summary exactly, and its assets map
holds 616 entries against a recorded 616. No Codex process was running, and the
file had been idle since `2026-08-30 01:39:46`.

Commit `732643e7` lands the previous session's clean-break records, which that
session wrote but never committed, together with
`memory-bank/handoffs/orchestrator-lessons-2026-08-30.md`.

`memory-bank/GOAL-BLOCKED.md` is deleted because its blocker no longer exists.

## Clean break — 2026-08-30

The owner requested a clean break. All active workflows and agents are complete. The sequential MacBook gate task was stopped.

Canonical `main` remains at `faa4add6cc2e03bb797af504970f9b290f3c559b`. It is not clean: `memory-bank/GOAL-BLOCKED.md` contains this session's pause record, and another writer changed `memory-bank/source-audits/post-cutoff-asset-revisions-2026-08-21.json` by three inserted lines and 32 deleted lines. Its working blob is `8ecc6d48a58b41f416a0186eac66d83d932b69f5`. This session did not stage, revert, repair, or commit the foreign change.

The unapproved menu work is removed. Commits `d5da2f3a1921f6592fd4ec32c3b86542b0ca71a6` and `03ea285df1a9b7d120179e9e5bbf5356468a3b8a` restore the owner-settled Qt menu behavior. Independent Opus review accepted the restoration. At `03ea285d`, MacBook plain and Qt each ran 4,525 tests; plain skipped 513 and Qt skipped three. Documentation, test quality, reachability, worktree, and diff checks passed. Native confirmation still needs a normal Anki restart.

The owner-settled UI rule now forbids changes to existing interfaces without explicit approval. Each new interface in approved work needs a frontend-taste model review before promotion.

Papercut remediation was a separate direct request, not an original-goal item. Triage found 14 eligible classes and verified four. Three non-UI branches are implemented, clean, and accepted by final cross-lineage review:

- `goal/papercut-test-cwd-2026-08-30` at `63a3409c0dd3b45f87548fdbcd74056bbc758e19`.
- `goal/papercut-worktree-bootstrap-2026-08-30` at `b861cdecf96d729e1f46b200e6e9313fd0730cb8`.
- `goal/papercut-reachability-check-2026-08-30` at `8f1092db1b6355fe83a02eeb32b0715c36cb9d99`.

The first branch passed the MacBook plain lane: `Ran 4526 tests in 251.013s`, `OK (skipped=513)`. The owner-requested break stopped the task before its Qt lane. The other two gates did not start. No repository test ran on the Mac Studio. No papercut branch was merged or pushed.

The preserved Collections worktree has no non-UI product correction. Its code delta is one existing-interface width change plus tests for that contract. Do not continue or delete it without a later owner decision.

`memory-bank/GOAL-BLOCKED.md` preserves the active goal verbatim. The single resume condition is a clean canonical `main` at one stable `HEAD` after the foreign asset-audit change is resolved.

Read `memory-bank/handoffs/orchestrator-lessons-2026-08-30.md` before new fan-out. It records the measured GLM failure, maximum-value-per-token rule, efficient large-fleet shape, adaptive retry rule, side-request scope rule, and current branch state.

## Historical normal-profile Anki pause — 2026-08-28

Canonical `main` is clean at
`3fd9728b6b9aeb9819ee7ff372352755e0d98b7c`. Bounded queue tooling passed the
exact MacBook Pro promotion gate at `2026-08-28T21:13:15-07:00` and landed by
fast-forward. Plain ran 4,526 tests in 245.643 seconds with 514 skips. Qt ran
4,526 tests in 452.841 seconds with three skips. All eight checks passed.

A fresh 51,814-byte queue packet has SHA-256
`eb4b85539c9beacad8b5cd42af8148bebbed56608b58fff1002e5f7acd249ef1`.
Independent Terra audit found no `implementation_ready`, accepted unmerged, or
`investigation_only` item and returned `NO UNBLOCKED REMAINDER`. Kinship and
diary interpretation are `owner_blocked`; Cooking is
`native_verification_blocked`; Runespan, Artisan's Workshop, Frost bone mapping,
and the named source ledger are `source_blocked`; the GPT queue is
`quota_blocked`; and remaining catalog debt is `deferred_data_depth`.

Collections remains `integration_blocked` in guarded worktree
`goal/collections-value-elision-final-2026-08-28`. Its 326-pixel candidate is
uncommitted and unaccepted. Four native cases remain unrun. Full-argument scans
at `2026-08-28 21:27 PDT` still found normal-profile Anki PID `85356`, mpv PID
`85362`, and QtWebEngineProcess PIDs `85360`, `85361`, and `85363`. Two separate
non-invasive waits each ended with exact output
`MacBook Anki runtime still has 5 matching processes after 540 seconds.`

The orchestrator did not stop, focus, reuse, or force-kill those processes. The
repaired native runner stops before mirror sync while any Anki-bundle process
exists. The normal-base metadata baseline has 205 lines and SHA-256
`11e497a37c2e56811b92c5190ff5c2aaa89fd04e8da41ac2f4d14f5272da0d6f`.
Final independent Opus safety review returned `ACCEPT`.

The single unblock action is: quit Anki PID `85356` normally through Anki's own
user interface on the MacBook Pro. Do not use a signal or force kill.
`memory-bank/GOAL-BLOCKED.md` preserves the active goal verbatim for resume.

## Bounded Memory Bank queue packet awaits final remote gates — 2026-08-28

Branch `goal/bounded-queue-packet-2026-08-28` adds the standard-library
`tools/memory_bank_queue_packet.py` CLI and a focused module that now contains
nine tests. It accepts one or more repository/worktree roots, preserves source
line references, emits bounded current queue signals under a 32,768-byte default
cap, and names every source truncated by intrinsic limits or omitted by the byte
cap. Two consecutive local builds produced byte-identical packets of exactly
26,089 UTF-8 bytes. Static checks also cover syntax compilation, CLI help,
reduced-cap behavior, source-category presence, explicit omission reporting,
and source-tree non-mutation.

The queue restores `rc-runespan` and `smith-artisan-burial` to
`design_settled_waiting_source`. Commit
`e3ce8722c6f644d287f4f8871f595a81b0ad83a2` had changed them to `merged` and
`implemented` without adding either implementation.

Pre-hardening MacBook support is exact focused output `Ran 5 tests in 0.010s`,
`OK`; plain `Ran 4521 tests in 246.473s`, `OK (skipped=513)`, 4,008 active; and
Qt `Ran 4521 tests in 458.932s`, `OK (skipped=3)`, 4,518 active. These runs do
not verify the current nine-test module. The final MacBook focused run passed:
`Ran 9 tests in 0.025s`, `OK`. Final exact-commit plain and Qt promotion gates
remain pending. Independent Opus review accepted the hardening delta subject to
those external gates. Promotion has not occurred.

## Native tab overflow landed; Cooking native verification is blocked — 2026-08-28

Commit `873b505e4111dd3a93e5f33b1f9af9329d3d59ed` is landed on local `main` by
fast-forward from `goal/native-tab-overflow-final-2026-08-28`. Old candidate
`1eedceb4` remains rejected and unmerged. Exact promotion evidence is the Git
common-directory record
`ankiscape-promotion-evidence/873b505e4111dd3a93e5f33b1f9af9329d3d59ed.json`,
completed at `2026-08-28T20:02:42-07:00`; it records `remote_lanes: true`,
`plain_only: false`, and all eight passed checks: plain lane, Qt lane,
`audit_docs`, `audit_test_quality`, reachability, `worktree_guard`, worktree
clean, and diff check.

The final policy uses document mode, 16x16 icons, `setExpanding(False)`,
`setUsesScrollButtons(True)`, `ElideNone`, and 1px left and right tab padding.
The 1px padding is deliberate: the 2px candidate failed the full MacBook Pro Qt
lane at 125% with exact `AssertionError: 9 not greater than or equal to 16`.
Final review resolved the WHY comment and `hint_bar` cleanup.

The isolated native process loaded `ui/ui.py` SHA-256
`d55b987a308a82e13f8a9c9b1aa3fefa9472e60403609edf0c96fa1699185d8c` and
`__init__.py` SHA-256
`842df7cffa5b1ed49380ad24c8e757eaf0ce70e6d747e3e615f06135ed2e8137`.
All four native tab cases contained the same 11 exact labels in order: `Skills`,
`Stats`, `Bank`, `Equipment`, `Shop`, `Grand Exchange`, `Challenges`, `Quests`,
`Achievements`, `Collections`, `Settings`.

Native tab case 1, normal font and wide dialog, is **PASS**. The observed wide
geometry was `1140x767`; natural-width headroom was 203 pixels, both scroll
controls were hidden and disabled, native pointer input selected Bank, no body
horizontal scrollbar appeared, and the dialog remained open. Native tab case 2,
125% font and wide dialog, is **PASS**. Its observed wide geometry was
`1145x769`; headroom was 43 pixels, both controls were hidden and disabled,
native pointer input selected Bank, no body horizontal scrollbar appeared, and
the dialog remained open. These observed sizes are native geometry caveats, not
claims that the windows measured exactly 1140x768.

Native tab case 3, normal font and narrow dialog, is **PASS**. Headroom was -284
pixels, both arrows were visible and distinct, native right scrolling exposed
the complete Settings tab, and native pointer input selected Settings. One left
action moved the strip 31 pixels and re-enabled right scroll. Native tab case 4,
125% font and narrow dialog, is **PASS**. Headroom was -382 pixels, both arrows
were visible and distinct, Settings was exposed and selected, and one left
action moved the strip 32 pixels and re-enabled right scroll. Neither narrow
case showed a body horizontal scrollbar, and both dialogs remained open.

The normal Anki base remained unchanged. The product PID exited, no child
remained, and no `Anki`, `mpv`, `QtWebEngineProcess`, or other process from the
isolated run remained. The durable evidence packet is
`memory-bank/evidence/native-tab-overflow-final-2026-08-28/`. It retains six
inspected product-only tab-strip crops and structured geometry. It excludes the
four full-dialog screenshots and the raw `.ips` crash packet. The retained
`report.md` has SHA-256
`b460ac9c1f7df2824de05ca1cb22d449e9dd22fbf09caad19061ad58ab179b3c`.
The retained `manifest.txt` has SHA-256
`9fb575f111d4c0d74db28d29c49af7a6bb4325aa3dcca1cedbc5c24345f05e47`
and verifies 23 companion files. Byte-for-byte `source_report.md` and
`source_manifest.txt` preserve source hashes
`f7af19f50febf1081b91a06b539394a3b1ba0b81304bbcfe81cbc13d07a73313` and
`5b28910056a253b488cf5642abe08e78780fc15262b93270e45b385b63865d74`.
The source manifest verifies 4,729 remote files.

Cooking is separately **native-verification-blocked**. The least-specific
supported class is a native Qt accessibility-bridge crash during a posted
accessibility update for the Skills `QTreeWidget`. Pointer activation returned
exact `Accessibility error: AXError.notImplemented`; continued keyboard
navigation returned exact `Computer Use server error -10005: App quit`. The
crash records `EXC_BAD_ACCESS`, `SIGSEGV`,
`QAccessibleCache::deleteInterface`, `QAccessible::updateAccessibility`,
`QAbstractItemView::event`, `sipQTreeWidget::event`, and `QDialog::exec`.
No AnkiScape Python frame appears, so the evidence does not prove an AnkiScape
product defect. No control run without an accessibility client exists, so it
does not prove a Qt-only defect. The process exited before the target page
opened; do not claim that the Cooking selector or persistence passed.

Focused verification passed with exact output `Ran 3 tests in 2.691s` and `OK`.
Plain run `plain-1787949374-081d77b7` completed with
`Ran 4517 tests in 245.057s`, `OK (skipped=514)`, and 4,003 active tests. Qt run
`qt-1787949632-bb622650` completed with `Ran 4517 tests in 448.447s`,
`OK (skipped=3)`, and 4,514 active tests. The 12-case offscreen visual workflow
remains supporting evidence across width, palette, font, Fusion, and native
macOS-style variants. The real `QTabWidget`-owned tab bar still rejects direct
`tabSizeHint(index)` at every index with exact
`RuntimeError: no access to protected functions or signals for objects not created from Python`; the Python-owned natural-width helper remains required.

The direct `--base` canary remains useful failure history: its mpv child used
`--config-dir=/Users/armantarkhanian/Library/Application Support/Anki2`, and
normal-base metadata changed. The final run instead used a disposable `HOME`, an
empty canary, child command-line inspection, normal-base metadata comparison,
and fail-closed staging.

The repository audit workflow counted 599 Markdown files, 441 HTML files, and
4,482 tests across 220 files. It found 0 hard issues and 31 structural clone
candidates. Reachability measured 1,600 actions, 2,217 reachable items, 192
orphan inputs, and 284 unresolved actions. One test was added and none were
deleted. Independent Opus review resolved all five initial and two delta issues.
Direct independent Kimi audit returned PASS for the tab-overflow slice and
BLOCKED for Cooking.

The tab slice is committed, promoted, and landed at
`873b505e4111dd3a93e5f33b1f9af9329d3d59ed`. Cooking retains the exact
`native-verification-blocked` class above. The remaining queue classes are
unchanged: Collections navigation
truncation is the active independent slice; Kinship, diary wiring, row 135, and
skill types 17–19 are `owner_blocked`; Snake hide, Herblore secondaries, Darkan
translation, and Frost bone mapping are `source_blocked`; deferred depth is
`deferred_data_depth`; and the GPT queue is `quota_blocked`. Collections remains
in its own guarded worktree and is not complete.

## Internal canonical-main writer identified; goal resumed — 2026-08-28

The owner did not move `main`. Fork agent `ab5d5dc6b89b21958` committed directly
in the canonical checkout. The agent transcript records its exact command at
`subagents/agent-ab5d5dc6b89b21958.jsonl:133` and the successful
`[main 60d70984]` result at line 134. The commit has parent `9ca56ff1`, author
date `2026-08-28T10:07:22-07:00`, and only one Memory Bank papercut insertion.

The agent violated its explicit no-canonical-edit and no-commit dispatch rules.
No owner or external writer changed the tree. Both active agents are stopped,
and `memory-bank/GOAL-BLOCKED.md` is removed before resume.

Candidate `goal/native-tab-overflow` commit
`1eedceb40dbdc8342ae71fa030605915daeafc09` remains unmerged and untested. It
contains the intended tab policy and focused coverage plus two unrelated
Grand Exchange process-event hunks. A fresh one-commit re-land branch must drop
those hunks before review, MacBook Pro lanes, and promotion.

## Autonomous implementation goal remains active — 2026-08-28

The prior completion claim was invalid. The exact `/goal` condition permits
complete work, deferred data depth, or an exact owner, source, dependency,
quota, or integration blocker. The synthesis schema also permitted
`investigation_only`, then returned four such rows and still declared
`no_unblocked_settled_implementation`.

The active loop must now resolve or reclassify these four gates: the Kinship
party-simulation packet, main-tab narrow-window and larger-font headroom,
Collections table value elision, and custom Cooking-row native activation. The
next audit must compare every result class directly with the exact goal clause
before it can claim completion.

The four accepted promotions remain valid. The final verified product head is
`1d461b16ba423a69488097c1e0d01365df914c48`, with exact MacBook Pro lanes and
all eight promotion checks green. The diary owner spot-check still blocks
wiring, and no remote push occurred.

The corrected active status is in
`memory-bank/status-updates/goal-closure-results-2026-08-28.html`.

## Repository papercut tooling re-land — 2026-08-19

The unmerged 2026-08-11 guardrail slice now sits on main snapshot
`689fdd4489eb646b695a3176a3d23c3ab19c3557`. Current-main review retained the
search, test-selection, lane-output, reachability-summary, generator, and
Qt-font guards. The test selector additionally normalizes exact
`tests/test_*.py` paths to discovered module IDs because that mistake recurred
after the original slice, while fuzzy module substitutions now fail closed.
The rejected advisory worktree-ownership feature was removed in full after it
broke the read-only layout audit twice. At that merged main snapshot, the tree
measures 1,571 actions / 2,278 reachable items / 72 orphan inputs / 71 blocked
actions. Full plain discovery passes 4,160 tests with 499 skips. The real
offscreen Qt lane covers the same 4,160 tests in four independent discovery
batches to remain below the 600-second command cap, with three skips in
aggregate. No gameplay data or period value changed. Full proof and historical
exclusions remain in `memory-bank/papercuts-fixed-2026-08-11.md`.

## Big Top Bonanza per-card queue — 2026-08-15

Pass 10 Batch A replaces the old one-review Circus reducer with one-trick
resolution per answered card. The persisted state now stores owner-ordered
executing and non-executing performance lists plus active performance, trick
index, payout-tier mask, score, success count, and attempted IDs. Darkan
commit `f00ca9b6dfb796858cc485c52b3f8d5e7674bfbe` is ported for the integer
success chance and half-level effective tier; no success-chance placeholder
was needed. Focused checks pass 22 Circus/runtime/integration tests, 198
adjacent pure/runtime tests, and one real offscreen Qt contract test. Review
undo restores the pre-card snapshot. The 1,680-card week derivation and
costume scoring were not changed. Results artifact:
`status-updates/pass10-batch-a-results-2026-08-15.html`.

## Oversized cadence credit recovery — 2026-08-13

Cadence `credit` is the deterministic fractional-admission residual accumulated toward a profile's denominator, so its valid range is `0` through `threshold_denominator - 1`. Immediately after the existing profile-state sanitization, the advance path clamps an oversized persisted integer to that profile-derived upper boundary. This keeps load recoverable while preserving as much earned progress as a valid state can represent; malformed types and negative values retain their existing reset-to-zero behavior. A real migration-plus-live-route regression covers Maple's denominator-10 profile with both credit `10_000` and the valid boundary `9`, proving the saved session advances successfully and retains credit `9` while consuming its opening opportunity.

## Polar kebbit quota-ticket target — 2026-08-12

Big Chinchompa's Polar kebbit quota ticket now resolves to the live
`catch_polar_kebbit` Hunter tracking target. The ordinary catch is available at
Hunter level 1; the separate Big Chinchompa reward purchase correctly requires
Hunter level 70. One review represents the sourced four- or five-search trail
and final attack, requires and preserves a Noose wand, awards 30 Hunter XP, and
produces Bones, Raw beast meat, and Polar kebbit fur. No quest or route wall was
added because the period Hunter location section lists multiple ordinary routes
to the Rellekka Hunter area and no quest gate.

Hunter oldid `6484443`, Darkan tracking commit
`37957d17d62d6b14d326cd719a0ae0c239c76cf9`, and OpenRS2 rev-742 pin the
visible mechanic and item identities. The unrecovered hidden catch curve uses
registered placeholder `hunter.polar_kebbit_success_curve` with the established
shared Hunter fallback. Reachability improves from 1,560 actions / 2,497 items /
99 orphan inputs / 102 blocked actions to 1,561 / 2,498 / 99 / 102; Polar kebbit
fur is newly reachable through `Hunter:catch_polar_kebbit`. See
`memory-bank/source-audits/polar-kebbit-tracking-acquisition-2026-08-12.md`.

## Quest-stage reachability truth correction — 2026-08-12

The audit now mirrors runtime action gating before it credits quest-stage products, keeps branch variants separate, and applies equivalent gates to quest-combat guaranteed drops. Main falls from 2,573 to 2,493 reachable items: 80 items that were previously reported reachable never were. Orphan inputs rise from 102 to 103 and blocked actions from 101 to 102. This is a measurement correction, not a gameplay regression.

The later `d2faf1d2` slice was re-derived separately. Troll thistle remains genuinely stage-reachable because Eadgar's Ruse stages 1–4 use emitted `auto_actions`; the acquisition helper supplies inventory and levels but does not manufacture `quest_stage_actions`. The same slice's Herb pouch quest-combat route is inert in normal play: Nial Swiftfling defaults to a level-156 minimum while a normal maxed player is combat level 126, and the test reaches it only with level 400 combat stats. Diamond root and Diamond root dust consequently remain unreachable. No route was repaired. Full plain discovery passes 4,059 tests with 496 expected skips; real offscreen Qt passes 4,059 with three. Durable audit: `audits/quest-stage-reachability-truth-2026-08-12.md`.

## Resumed-goal interval closure — 2026-08-10

The audit covers all work after the 2026-08-08 resume. It reviewed 52 commits
from the Crucible depth pass through the first pause handoff. The 35 grouped
implementation, source, tooling, and acquisition slices are committed and
mechanically complete for their recorded scope. Every linked worktree is clean.
The only non-ancestor branch has the same stable patch ID as work already in
`main`.

Ranging Guild was the only slice with a deferred full Qt lane. Its first run
found two stale Activities inventory assertions. The direct checks passed after
the test-only correction, and the complete offscreen Qt lane then passed all
4,053 tests with three expected skips. Full plain discovery had already passed
4,053 tests with 494 expected skips. Documentation, test quality, compilation,
tracked JSON, placeholder, asset normalization, diff, reachability, and worktree
checks pass. The goal remains paused before a new slice. No new owner/Fable
design question arose in the resumed interval. Complete handoff:
`codex-briefs/goal-pause-handoff-2026-08-10.md`.

## Quest-grant reachability correction — 2026-08-10

The live item graph now recognizes registered quest `start_inventory` and
stage `produced_inventory` as acquisition sources, in addition to final quest
rewards. This corrects audit evidence only; the quest runtime, rewards, gates,
save state, UI, and assets are unchanged.

The corrected graph exposes 134 items that the existing runtime already
grants. `Dramen branch` resolves through `quest-stage:lost_city:4`, and its
existing Utility consumer makes `Cinnamon` reachable. Reachability is now
1,555 actions / 2,570 reachable items / 103 orphan inputs / 102 unresolved
actions. Focused reachability and quest-runtime coverage passes 201 tests.
Both full discovery lanes pass 4,036 tests, with 492 expected plain skips and
three real offscreen Qt skips. Native Anki interaction is not claimed. Durable
evidence:
`source-audits/item-reachability-quest-grants-correction-2026-08-10.md`.

## Crystal key and chest acquisition — 2026-08-10

One Tooth half and one Loop half now combine into a Crystal key through the
existing level-1 zero-XP Crafting path. The established Utilities selector then
opens one Taverley Crystal chest per answered review, consumes the key, and
awards one guaranteed Uncut dragonstone plus the exact measured bonus bundle.
All outputs persist, enter telemetry and achievement progress, and roll back
atomically through Anki answer undo.

Cutoff oldids `6428315`, `6491268`, and `6570440` pin the key chain, twelve-row
measured reward table, 24,786-Coin GE price, and 100-item buy limit. Rev-742
pins the item identities. The Ring of wealth now equips in its real ring slot;
its unrecovered chest modifier is registered as a 25% better-of-two-row
placeholder that chooses only among authentic rewards. AnkiScape's flat bank
stores noted Coal/Iron rows as ordinary item quantities, and its missing gender
substrate uses one Rune platelegs output instead of granting both leg variants.

Reachability is now 1,555 actions / 2,436 reachable items / 104 orphan inputs /
103 unresolved actions. Focused verification passes 682 plain tests and one
real offscreen Qt test. Full plain and real offscreen Qt discovery each pass
4,036 tests, with 492 expected plain skips and three Qt skips. Native Anki
interaction is not claimed. Documentation passes across 555 Markdown and 431
HTML files; test quality reports 4,001 methods in 182 files with zero hard
issues. Compilation, JSON, placeholder, asset normalization, diff,
reachability, and worktree gates pass. Durable evidence:
`source-audits/crystal-key-chest-acquisition-2026-08-10.md`.

## Living rock remains acquisition — 2026-08-09

Living rock remains now supplies the previously orphaned Living minerals
through a level-73 Mining row. A successful review awards 25 XP and 5–24
minerals, records the actual bundle throughout telemetry and achievement
progress, persists it, and rolls it back with review undo. The focused cutoff
page supplies the visible range; Darkan's hidden `30/145` success curve and the
uniform range distribution remain registered as
`mining.living_rock_remains_rolls`. Existing normalized period art covers the
selector and inventory. The public-corpse delay is collapsed into one review,
with no wall clock and no artificial Combat prerequisite. Durable evidence:
`source-audits/living-rock-remains-acquisition-2026-08-09.md`.

Reachability is now 1,553 actions / 2,434 reachable items / 105 orphan inputs /
104 unresolved actions. Focused checks pass 485 plain tests and one real
offscreen Qt test. Both full discovery lanes pass 4,029 tests, with 491
expected plain skips and three Qt skips. Documentation, test-quality,
compilation, JSON, placeholder, asset-normalization, diff, reachability, and
worktree gates pass. Native Anki interaction is not claimed.

## Razor-backed kebbit tracking — 2026-08-09

Razor-backed kebbit tracking now supplies the previously orphaned Long kebbit
spike through Hunter's existing target, failure, carried-pack, cadence,
telemetry, Shattered Heart, persistence, and review-undo paths. The target
requires Hunter 49 and a reusable Noose wand, awards 348 XP, and collapses the
sourced four- or five-search trail into one review transaction. Its three
sourced outputs feed both the existing Fletching action and Leon service.

Hunter oldid `6484443` pins the visible mechanic. The unrecovered hidden catch
curve uses the registered shared Hunter fallback, which is `192/255` at level
49 before review normalization. Rev-742 pins Long kebbit spike item `10107`
and Raw beast meat item `9986`; existing normalized cutoff sprites are reused.
Reachability is now 1,552 actions / 2,431 reachable items / 107 orphan inputs /
106 unresolved actions.

Focused checks pass six plain tests and one real offscreen Qt test. Full plain
and real offscreen Qt discovery each pass 4,026 tests, with 491 expected plain
skips and three Qt skips. Documentation audits 553 Markdown and 431 HTML files;
test quality reports 3,991 tests in 181 files with zero hard issues.
Compilation, JSON, placeholder, asset normalization, diff, reachability, and
worktree safety pass. Native Anki interaction is not claimed. See
`memory-bank/source-audits/razor-backed-kebbit-tracking-acquisition-2026-08-09.md`.

## Unholy mould acquisition — 2026-08-09

Chaos druids now drop one Unholy mould on the sourced 1/128 slot. The existing
Combat target supplies the item through its normal kill, loot, carried-state,
persistence, telemetry, and undo paths. A real reducer-chain test proves that
the acquired mould and one Silver bar produce one Unstrung emblem for 50 XP
without consuming the reusable mould.

Cutoff oldids `6381798` and `6088663`, Darkan commit
`9a6db4df8d12a743d0318bcd524462512e838ff3`, and OpenRS2 rev-742 item 1594
close the route and item semantics without a placeholder. The distinct 31×27
source-period sprite replaces the incorrect Holy mould fallback and is proven
through the real offscreen Qt Bank. Reachability is now 1,551 actions / 2,428
reachable items / 108 orphan inputs / 108 unresolved actions.

Focused checks pass 71 plain tests and one real offscreen Qt test. Full plain
and real offscreen Qt discovery each pass 4,023 tests, with 491 expected plain
skips and three Qt skips. Documentation audits 552 Markdown and 431 HTML files;
test quality reports 3,988 tests in 181 files with zero hard issues.
Compilation, JSON, asset normalization, diff, and worktree safety pass. See
`memory-bank/source-audits/unholy-mould-chaos-druid-drop-2026-08-09.md`.

## Special Woodcutting acquisition — 2026-08-09

Arctic pine and Eucalyptus now have live gathering routes into their existing
Firemaking chains. Arctic pine requires level 54, awards 140.2 Woodcutting XP,
produces Arctic pine logs, and unlocks when The Fremennik Isles starts.
Eucalyptus requires level 58, awards 165 XP, produces Eucalyptus logs, and
uses the settled safe-route abstraction without a quest or ambient-combat gate.

Oldids `6069429` and `6491980` pin both visible rows. Their hidden success,
depletion, and respawn constants remain unrecovered, so nearest-level Mahogany
and Yew rows are registered as explicit placeholders. Both targets reuse
normalized cutoff log sprites. The shared runtime now enforces Woodcutting
quest locks as well as the selector, preventing saved/direct target states from
bypassing the Arctic route wall.

Focused checks pass 416 pure/data/runtime/metadata/reachability tests, two
loaded-add-on undo checks, and one real offscreen Qt selector check. Full plain
discovery passes 3,992 tests with 487 expected skips; real offscreen Qt passes
the same 3,992 with 3 skips. Documentation audits 542 Markdown and 431 HTML
files; test quality finds 3,958 methods in 180 files with zero hard issues.
Reachability improves to 1,546 actions, 2,350 reachable items, 162 known
orphans, and 181 unresolved actions. Compilation, JSON, diff, asset
normalization, and worktree safety pass. Cursed magic remains
dependency-blocked on the absent Spirit of Summer quest substrate. Native Anki
interaction is not claimed. See
`memory-bank/source-audits/special-woodcutting-acquisition-2026-08-09.md`.

## Brewing input acquisition — 2026-08-09

Barley malt and Ale yeast now have complete player-facing acquisition routes
into the already-live brewing family. At level 1, one Cooking review converts
one Barley to one Barley malt on a range, with no failure and no XP. Blandebir
fills each Empty pot for exactly 25 Coins through the existing batchable Shop
service after the established The Giant Dwarf Keldagrim route wall. Both routes
preserve materials, carried inventory, persistence, telemetry, and atomic undo.
The shared Cooking runtime now suppresses the
misleading `+0 XP` feedback event for authentic zero-XP actions.

Oldids `6207311` and `5434668` pin the malt conversion and zero XP. Ale yeast
oldid `4227753` pins Blandebir, Keldagrim, Empty pot, 25 Coins, and fill-all
batching. Period identities are Barley `6006`, Ale yeast `5767`, and Barley
malt `6008`; existing normalized cutoff sprites cover all three. Metarialus's
five-Ecto-token alternative remains later catalog depth, not a mechanical
blocker or placeholder.

Focused checks pass 645 plain tests and two real offscreen Qt tests. Full plain
discovery passes 3,986 tests in 211.266 seconds with 486 expected skips; full
real offscreen-Qt discovery passes the same 3,986 in 515.812 seconds with three
intentional skips. Documentation audits 541 Markdown and 431 HTML files; test
quality finds 3,952 methods in 180 files with zero hard issues. Reachability is
1,544 actions, 2,347 reachable items, 164 known orphans, and 184 unresolved
actions. Compilation, JSON, deterministic shop generation, diff, asset
normalization, and worktree safety pass. Native Anki interaction is not
claimed. See
`memory-bank/source-audits/brewing-input-acquisition-2026-08-09.md`.

## Make wine Cooking runtime closure — 2026-08-09

`Make wine` is live as a standard grouped Cooking target. At level 35, one
review consumes one Grapes and one Jug of water, immediately produces Jug of
wine for 200 base XP or Jug of bad wine for no XP, and uses no wall-clock or
persisted fermentation timer. The bad outcome has distinct telemetry and does
not count as an ordinary cooking burn. Anki Undo restores the complete review
transaction.

Oldid `6151933` pins the visible recipe and outcomes. Rev-742 pins identities
1937/1987/1995/1993/1991 and catches Jug of bad wine as non-exchangeable. The
hidden success curve remains registered as `cooking.wine_success_curve` from
Darkan's bounded reconstruction. The existing grouped selector displays both
outcomes and the required materials. The only missing sprite uses the oldest
available 2019 OSRS upload strictly as visual art; its exact revision is
normalized, provenance-recorded, and reproducible by the Cooking asset tool.

Focused checks pass 464 broad tests, 14 exact closure tests, and one real
offscreen Qt selector test. Full plain and real offscreen-Qt discovery each
pass 3,977 tests, with 486 expected plain skips and three intentional Qt skips.
Documentation audits 539 Markdown and 431 HTML files; test quality finds 3,943
methods in 180 files with zero hard issues. Reachability is 1,539 actions,
2,342 reachable items, 167 known orphans, and 187 unresolved actions.
Compilation, JSON, asset resolution/normalization, diff, and worktree safety
pass. The locked Mac prevents native Anki interaction, which is not claimed.
The parent backlog row now names only karambwan and karambwanji as open. See
`memory-bank/source-audits/wine-cooking-runtime-closure-2026-08-09.md`.

## Crafting and Fletching potion runtime — 2026-08-09

Crafting and Fletching potions now apply their sourced exact `+3` current-level
boost through one shared noncombat runtime. The target-local policy, temporary
levels and 100-tick residual, carried vial/flask replacement, direct Bank
drinking, Casual/Advanced pack rules, boosted gates, persistence, and undo are
live. Schema 113 stores and sanitizes the shared state. The period GE generator
now contains 1,430 prices and 1,746 buy limits, including all eight newly pinned
exchangeable states.

The closure audit found and fixed an older Hunter transcription: `Catch wimpy
bird` awarded Stripy feathers even though cutoff oldid `5936660` lists `Wimpy
feather` loot in quantities `5 - 10`. The deterministic row now awards the
sourced minimum five and reuses normalized 2010 art. This restores a fresh-
profile route through the existing Herblore recipe, Bob's decanting, Teplin's
flask services, and every consumed dose state.

Full plain and real offscreen-Qt discovery each pass 3,939 tests, with 483
expected plain skips and three intentional Qt skips. Test quality has zero hard
issues across 3,905 tests in 178 files. Documentation audits cover 534 Markdown
and 431 HTML files. Reachability is 1,537 actions, 2,333 reachable items, 168
known orphan inputs, and 188 known blocked actions. Compilation, tracked JSON,
diff, provenance, asset normalization, and worktree safety pass. Fable's direct
render pass produced the visible dark-mode checkbox; Kimi K3 returned `SHIP` on
the bounded corrected transcript. Native Anki proved one real menu dispatch and
one menu window, but the locked macOS login session prevented further visual
navigation. See
`memory-bank/source-audits/crafting-fletching-potion-runtime-2026-08-09.md`.

## Trouble Brewing The stuff and mature-ale brewing — 2026-08-09

The cutoff Brewing and The Stuff revisions pin the full-vat sequence, optional
additive, eight-glass output, level-19 Dwarven stout recipe, four Hammerstone
hops, and 215 Cooking XP. Honest Jimmy pins one `The stuff` at five Pieces of
Eight; rev-742 pins every item identity and trade/stack property. Darkan
corroborates the reconstructed item flow and supplies the registered provisional
10%/75% mature roll where period primary evidence does not expose the formula.

The reward is live through the existing atomic shop/direct-undo path. Two
Cooking rows consume the full vat with or without `The stuff`; mature and
ordinary outcomes each award eight drinks and 215 XP, and both return two empty
buckets. One review represents the full vat with no wall-clock gameplay. The
existing grouped selector and reward shop show normalized cutoff art and exact
outcome/material guidance. Fable found no material UI issue after the corrected
expanded-group capture. Kimi K3 remains explicitly unapproved because its
provider returned an HTTP 403 billing-cycle limit after preflight.

Focused checks pass 491 tests and focused real offscreen Qt passes three. Full
plain and real offscreen-Qt discovery each pass 3,927 tests, with 482 expected
plain skips and three intentional Qt skips. Documentation audits pass across
533 Markdown and 431 HTML files; test quality has zero hard issues across 3,893
tests in 177 files. Reachability is 1,513 actions, 2,316 reachable items, 170
known orphan inputs, and 190 known blocked actions. Compilation, tracked JSON,
diff, placeholder, normalization, and worktree safety pass. A fully quit and
freshly relaunched native Anki process loaded one AnkiScape menu, the updated
Cooking prompt, and the two-row Brewing group without mutating gameplay state.
See
`memory-bank/source-audits/trouble-brewing-the-stuff-brewing-2026-08-09.md`.

## Trouble Brewing medium-clue service — 2026-08-09

Honest Jimmy oldid `6393015` pins one `Clue scroll (medium)` for exactly `5,000`
Pieces of Eight. Treasure Trails oldid `6473708` and owner answer 4.5 require
one clue total across all tiers. Rev-742 and game-main pin canonical item `2801`
as non-stackable, non-exchangeable, and readable.

The shop service asks the central Treasure Trails ownership helper before
charging, awards one canonical clue, and persists through Trouble Brewing's
existing direct-action undo seam. The pure view exposes its blocker; Qt renders
the `5,000 PoE` row, a held-clue marker, and explicit ownership or wallet
shortfall guidance. Easy, medium, and hard clue definitions all use rev-742
model `3374`, so the selector reuses normalized 2010 shared-model art rather
than a post-cutoff fallback. Kimi K3 and Fable independently reviewed the new
state; their accepted findings produced the formatted price and disabled-state
guidance. Neither review claims native Anki appearance.

Focused non-Qt checks pass 243 tests and focused real offscreen Qt passes four.
Full plain and real offscreen-Qt discovery each pass 3,922 tests, with 482
expected plain skips and three intentional Qt skips. Documentation audits pass
across 532 Markdown and 431 HTML files; test quality has zero hard issues across
3,888 tests in 177 files. Reachability remains 1,511 actions, 2,315 items, 168
known orphans, and 188 known blocked actions. Compilation, tracked JSON, diff,
deterministic asset enumeration, normalization, and worktree safety pass. Medium
trail content remains catalog depth; `The stuff` is the next Trouble Brewing
slice. See
`memory-bank/source-audits/trouble-brewing-medium-clue-service-2026-08-09.md`.

## Trouble Brewing rum teleports — 2026-08-09

Honest Jimmy oldid `6393015` and rum oldid `6088748` pin red and blue rum at
`2` Pieces of Eight, the `Drink` action, one-use consumption, and the shared
Trouble Brewing destination. OpenRS2 rev-742 supplies exact IDs `8940` and
`8941`, non-stackability, non-exchangeability, and their recolour distinction.

Both rewards are live in the existing atomic shop and direct-undo paths.
Drinking consumes exactly one, records the source destination, and refuses
without mutation when missing, unknown, or inside the activity's closed
temporary inventory. The 29-row selector and Bank action show normalized
cutoff art and explicit destination/consumption guidance. Kimi K3 and Fable
taste review produced the accepted 24-pixel bottle box, visible Bank-menu
tooltips, pre-click mid-match disabled state, and unambiguous live scoreboard.
Neither review claims native Anki appearance.

Focused non-Qt checks pass 210 tests and focused real offscreen Qt passes four.
Full plain and real offscreen-Qt discovery each pass 3,919 tests, with 481
expected plain skips and three intentional Qt skips. Documentation audits pass
across 531 Markdown and 431 HTML files; test quality has zero hard issues across
3,885 tests in 177 files. Reachability is 1,511 actions, 2,315 items, 168 known
orphans, and 188 known blocked actions. Compilation, tracked JSON, diff,
deterministic asset fetching, normalization, and worktree safety pass. The
5,000-Piece medium-clue service and `The stuff` remain separate depth slices.
See `memory-bank/source-audits/trouble-brewing-rum-teleports-2026-08-09.md`.

## Trouble Brewing cosmetic reward catalog — 2026-08-09

Cutoff Honest Jimmy oldid `6393015`, timestamp `2012-10-13T04:08:35Z`, pins
seven Blue/Green/Red/Brown/Black/Purple/Grey naval sets and six flags in exact
source order at `50`–`600` Pieces of Eight. OpenRS2 rev-742 supplies identities
`8952`–`8971` and `8991`–`8997`; the authentic game-main equipment blocks pin
body/head/legs/weapon slots, zero bonuses, flag weapon type, attack speeds, and
Phasmatys's two-handed state. Correct oldids `6579342`/`6393015` replace stale
migrated references `6573931`/`6399561` for this family.

All 27 rewards now use the existing atomic purchase/direct-undo, item, Bank,
and equipment paths. Every selector row has a normalized cutoff sprite and an
explicit compact `PoE` unit. A real Qt interaction regression proves selection
changes recompute Buy availability; this fixes a dormant one-row-era UI bug.
Kimi K3 and Fable independently found the missing currency unit and otherwise
approved the bounded existing-card change. Neither review is a native Anki
appearance claim.

Focused pure/integration/write-through/equipment/registry checks pass 141
tests, and four focused real Qt checks pass. Full plain and real offscreen-Qt
discovery each pass 3,916 tests, with 480 expected plain skips and three
intentional Qt skips. Documentation audits pass across 530 Markdown and 431
HTML files; test quality has zero hard issues across 3,882 tests in 177 files.
Reachability is 1,511 actions, 2,313 items, 168 known orphans, and 188 known
blocked actions. Compilation, tracked JSON, diff, deterministic asset fetching,
asset normalization, and worktree safety pass. Rum teleports, the 5,000-Piece
medium clue service, and `The stuff` remain separate mechanic-depth slices. See
`memory-bank/source-audits/trouble-brewing-cosmetic-catalog-2026-08-09.md`.

## Shades of Mort'ton bronze-chest catalog — 2026-08-09

RuneScape Wiki `Shades of Mort'ton (minigame)` oldid `6449451`, timestamp
`2012-10-21T17:37:46Z`, fixes the bronze reward families, key consumption,
better-colour quality improvement, and occasional paste. Fresh Darkan iteration
399 pins the reconstructed 23 item identities, exact quantity ranges, four
chance-group sizes, three currently live key modifiers, and the server's
ascending chance-group order. Hidden probabilities, Ring of Wealth behavior,
and paste chance remain labeled `provisional/darkan` and `source_blocked`.

Every bronze reward is reachable through the existing atomic chest action.
Variable quantities are inclusive, the central Treasure Trails filter prevents
a second clue, and the former ghost `Steel axe` is replaced by exact cache item
`1353`, `Steel hatchet`. The two previously absent poisoned daggers are
registered as equipment with cache IDs `1233` and `1225`, normalized cutoff
sprites, and exact cutoff Grand Exchange buy limits of `100`.

Focused pure/integration/registry/asset verification passes 73 tests, and four
focused real Qt checks pass on the established surfaces. Full plain and real
offscreen-Qt discovery each pass 3,914 tests, with 480 expected plain skips and
three intentional Qt skips. Documentation audits 529 Markdown and 431 HTML
files; test quality has zero hard issues across 3,880 tests in 177 files.
Reachability is 1,511 actions, 2,287 items, 168 known orphans, and 188 known
blocked actions. Compilation, tracked JSON, diff, deterministic asset fetching,
asset normalization, and worktree safety pass. Higher shade/key/chest tiers
remain catalog depth. See
`memory-bank/source-audits/shades-of-mortton-bronze-chest-catalog-2026-08-09.md`.

## Great Orb Project teleport tablets — 2026-08-09

RuneScape Wiki `The Great Orb Project` oldid `6564759`, timestamp
`2012-11-17T03:12:07Z`, pins all 14 tablets, exact prices, stackable single-use
behavior, exterior destinations, altar-access requirement, and special gates.
OpenRS2 cache 544, revision 742, pins exact item IDs `13598` through `13611`,
non-exchangeability, stacking, and the `Break` inventory option.

All rows are live as canonical one-at-a-time Wizard Elriss purchases with
normalized source sprites. The Bank's `Break` command uses atomic direct undo.
Altar tablets consume one item, select the canonical Runecrafting target, and
queue the existing Wicked-hood route seam so only the next matching outbound
leg is skipped. The Guild tablet records arrival inside the Guild without an
altar-route waiver. Cosmic, Astral, Death, and Blood reuse existing quest gates;
Astral also needs a Seal of passage. Law rejects equipped or physically carried
combat gear while allowing the exact zero-bonus Law talisman staff. The flat
Bank is not treated as physical inventory. Tablet use never grants altar access,
and consumption reconciles the active carried view.

The complete 395-test real Qt widget module and 269 focused pure/integration/
immutability tests pass. Kimi's five-hour quota was exhausted, Claude's
supported quota preflight was rate limited, and Fable remains reserved; no
guard was bypassed. Full plain and real offscreen-Qt discovery each pass 3,908
tests, with 480 expected plain skips and three intentional Qt skips.
Documentation audits 528 Markdown and 431 HTML files; test quality has zero
hard issues across 3,874 tests in 177 files. Compilation, tracked JSON, diff,
deterministic asset fetching, UI-asset normalization, and worktree safety pass.
Reachability rises to 1,511 actions and 2,284 items while the known 168-orphan/
188-blocked ledger is unchanged. No world-map substrate, wall clock, save
schema, placeholder, or owner decision was added. See
`memory-bank/source-audits/great-orb-project-teleport-tablets-2026-08-09.md`.

## Great Orb Project talisman staves — 2026-08-09

Runecrafting-staff oldid `6430449`, pre-EOC Air/Omni oldids `6080692` and
`6080707`, the cutoff child identities, and rev-742 pin the exact 10,000-token
base staff, twelve ordinary irreversible bindings, free Wizard Korvak Omni
conversion, altar-access rules, Law exception, item IDs, and equipment stats.
No inspected period record awards binding XP, so the live binding gives zero
without registering an invented hidden value.

The family reuses the existing GOP atomic purchase/direct-undo path, the
Runecrafting review/undo path, shared inventory/Bank/equipment registries, and
the grouped target and reward selectors. Ordinary binding consumes one carried
base staff plus one carried matching talisman and inherits the matching altar's
quest gate. Wielded ordinary staves provide that altar's 28-slot capacity;
Omni supplies every modeled ordinary altar except Law, while the dedicated Law
staff keeps its exact zero-bonus row. Fourteen normalized sprites are registered
with provenance. Declaring binding recipes also repairs older tiara binding,
which had consumed directly from the bank instead of the carried pack. Save
repair recognizes equipped Omni-tiara and staff outputs, so they cannot reopen
Elriss's one-time 13,605-XP claim.

The complete 394-test real Qt widget module and 413 focused pure/integration
tests pass. Kimi's fresh preflight reported five-hour usage `100.0%` and weekly
usage `33.0%`, so the requested K3 taste call failed closed; Fable remains
reserved. Full plain and real offscreen-Qt discovery each pass 3,903 tests,
with 479 expected plain skips and three intentional Qt skips. Documentation
audits 527 Markdown and 431 HTML files; test quality has zero hard issues across
3,869 tests in 177 files. Compilation, tracked JSON, diff, deterministic asset
fetching, UI asset normalization, and worktree safety pass. Reachability rises
to 1,511 actions and 2,270 items while the known 168-orphan/188-blocked ledger
is unchanged. Abyss-eye distraction remains outside the live substrate;
teleport tablets are next. See
`memory-bank/source-audits/great-orb-project-talisman-staves-2026-08-09.md`.

## Great Orb Project standard Runecrafter robes — 2026-08-09

RuneScape Wiki oldid `6327369`, cutoff talk oldid `5565562`, and OpenRS2
rev-742 pin all three colours, 12 one-at-a-time 1,000-token purchases, exact
item identities, equipment slots, combat bonuses, and an XP effect confined to
Great Orb Project essence crafting. The live rate is the registered bounded
placeholder `0.25%` per occupied standard piece, at most 1% across four slots;
mixed colours work and ordinary altar Runecrafting remains unaffected.

The family reuses the atomic reward/direct-undo, inventory, Bank, equipment,
discard, recovery, and fixed-icon shop paths. Fractional awarded XP remains
identical across the pure result, status, persistent match tracker, runtime
award, telemetry, and undo. Nine sprites use immutable pre-cutoff file
revisions. The three renamed goggles-on hat files have no surviving pre-cutoff
revision under their current titles and are explicitly labeled visual-only
fallbacks.

Root inspected the real 1200×760 dark render. Kimi's fresh five-hour quota was
exhausted and Opus's preflight was unavailable, so neither guard was bypassed;
no new widget or interaction pattern was added. Full plain and real offscreen-
Qt discovery each pass 3,897 tests, with 479 expected plain skips and three
intentional Qt skips. Documentation audits 526 Markdown and 431 HTML files;
test quality has zero hard issues across 3,863 tests in 177 files. Compilation,
26 tracked JSON files, diff whitespace, deterministic asset fetching, all 284
Activities-item crops, and worktree safety pass. Reachability improves to 2,256
items while the known 168-orphan and 188-blocked ledger is unchanged. Talisman
staves and teleport tablets remain separate depth. See
`memory-bank/source-audits/great-orb-project-standard-runecrafter-robes-2026-08-09.md`.

## Great Orb Project Master Runecrafter robes — 2026-08-09

RuneScape Wiki oldid `6514332`, its four cutoff child revisions, and OpenRS2
rev-742 pin all four 15,000-token rewards, item identities, equipment slots and
combat bonuses, piece XP rates, full-set bonus, and the 700-XP bonus cap. The
live family uses the shared atomic shop, direct undo, inventory, Bank,
equipment, and asset registries.

Ordinary altar Runecrafting and Great Orb Project now apply the exact worn-rate
sum plus the full-set 1%, capped at 700 added XP per action. Great Orb Project
computes the bonus in its pure result so UI status, match totals, telemetry,
runtime award, persistence, and review undo agree. Four exact 2011 source
sprites are normalized and rendered in the shared fixed 24-pixel slot.

Kimi K3's three concrete ordering, number-formatting, and status-XP findings
were reproduced and fixed; root inspected the real 1200×760 dark render. Opus
failed closed at its supported OAuth/quota preflight. Full plain and real
offscreen-Qt discovery each pass 3,895 tests, with 479 expected plain skips and
3 intentional Qt skips. Documentation audits 525 Markdown and 431 HTML files;
test quality has zero hard issues across 3,861 tests. Compilation, 26 tracked
JSON files, diff, asset normalization/fetch determinism, and worktree safety
pass. Reachability improves to 2,244 items while the known 168-orphan and
188-unresolved ledger is unchanged. Standard robes, staves, and tablets remain
separate depth. No placeholder or design gap was added. See
`memory-bank/source-audits/great-orb-project-master-runecrafter-robes-2026-08-09.md`.

## Great Orb Project ordinary-talisman catalog — 2026-08-08

RuneScape Wiki `The Great Orb Project` oldid `6564759`, timestamp
`2012-11-17T03:12:07Z`, pins every ordinary talisman except Death and Blood at
50 tokens for free-to-play rows and 125 for members-only rows. The live Elriss
shop now carries Air, Mind, Water, Earth, Fire, Body, Cosmic, Chaos, Nature, and
Law talismans at those exact prices. Rev-742 and the authentic item table pin
their exact identities, non-stackability, and exchangeability.

Each talisman ignores Buy X and purchases one at a time through the existing
atomic reward command, preserving direct-action undo. The outputs are the
existing canonical Runecrafting items, so no parallel altar, binding, Omni,
inventory, Bank, or discard implementation was added. The existing reward
selector shows their already-provenanced sprites in fixed 24-pixel slots.

Kimi K3 returned `NO_BLOCKER`, and root inspected the real 1200×760 dark shop
render. Opus could not start because its supported quota preflight returned the
same stale snapshot on three attempts; the review was not bypassed through an
unsupported route. Focused verification passes 280 pure/integration/undo/
registry tests and one real offscreen Qt selector test. Full discovery passes
3,891 tests in both lanes: plain has 479 expected dependency skips and real
offscreen Qt has 3 intentional skips. Documentation audits 524 Markdown and
431 HTML files; test quality reports zero hard issues across 3,857 tests in 177
files. Compilation, tracked JSON, diff, asset normalization, and worktree
safety pass. Reachability remains at 1,499 actions, 2,240 reachable items, 168
orphan inputs, and 188 unresolved actions. No placeholder or design gap was
added.

## Papercut remediation closure — 2026-08-09

Every recorded incident through `memory-bank/papercuts.md` snapshot line 127
is accounted for in `memory-bank/audits/papercut-remediation-2026-08-09.md`.
The original incident log stays append-only. `tools/repo_search.py` prevents
unmatched-glob, stale-path, giant-generated-file, and unbounded-result repeats.
`run_tests.py` selects discovered test IDs, suggests close names, uses compact
full-suite output, and rejects focused lanes where every target skipped.
`tools/run_logged.py` retains complete output and exact exit status while
printing only a bounded tail. `tools/workflow_manifest_guard.py` rejects the
repeated invalid mode, zero budget, relative working directory, and permissive
object-schema mistakes before launch.

Direct `tools/generate_equipment_data.py` execution now installs the package
root before `pkg_alias`, and its external 2011Scape source root is explicit.
The shared status-artifact skill no longer references a nonexistent project
example. A frozen no-tools Sol-high simplification pass completed; all four
valid findings were applied. The duplicate GE direct-invocation test left by
the concurrent feature pass was removed because
`tests/test_grand_exchange_data.py` owns the same behavior.

Focused papercut and generator tests pass. Full discovery passes 3,889 tests in
both lanes: plain has 479 expected environment skips and real offscreen Qt has
3 intentional skips. Documentation audits 523 Markdown and 431 HTML files.
Test quality, compilation, and worktree safety pass.

## Mage Training Arena reward-catalog closure — 2026-08-08

RuneScape Wiki `Mage Training Arena` oldid `6491109`, timestamp
`2012-10-28T20:51:43Z`, supplies the complete 25-row reward table. Every exact
four-wallet price is live in source order. The reward router, room mechanics,
caps, persistence, and undo are unchanged; each row now has an atomic purchase
proof, and Battlestaff retains one bounded all-four-room end-to-end proof.

Rev-742 pins the Infinity set, Mages' book, and rune identities. Authentic
game-main equipment definitions pin the six new equipment rows' modeled Magic
bonuses and equip requirements. Six pre-cutoff sprites are normalized. Both
existing Goal and Reward selectors use fixed 24-pixel icons; Bones to Peaches
uses its existing spell art. Kimi K3 and Opus taste passes are closed with no
remaining blocker.

The six exchangeable equipment outputs now have exact nearest-pre-cutoff GE
prices and a four-hour buy limit of ten. This also repaired the period GE
generator's documented direct-invocation path instead of weakening the
fail-closed buy-limit oracle.

Focused verification passes 133 pure/integration tests and 3 real offscreen Qt
tests. Full discovery passes 3,889 tests in both lanes: plain has 479 expected
environment skips and real offscreen Qt has 3 intentional skips. Documentation
audits 523 Markdown and 431 HTML files; test quality reports zero hard issues
across 3,855 tests in 177 files. Compilation, JSON, diff, asset normalization,
and worktree audits pass. Reachability records 1,499 actions, 2,240 reachable
items, 168 orphan inputs, and 188 unresolved actions. No placeholder or design
gap was added.

## Managing Miscellania resource-family closure — 2026-08-08

RuneScape Wiki `Managing Miscellania` oldid `6500793`, timestamp
`2012-10-30T06:29:55Z`, supplies the complete cutoff resource table. Mining,
Wood, Flax/Herbs, Fishing, Hardwood, and Farming are now all live with their
fixed quantities, item ranges, category totals, player-selectable variants, and
Maple-nest equation. Existing saves add the three new allocations at zero and
preserve the selected old variant without a schema bump. Collection remains one
atomic command and now returns its exact output map.

The unrecovered gem, nest, herb-seed, herb-composition, and Farming-composition
selectors are registered under `managing_miscellania.*`. Every deterministic
composition remains inside the source's exact ranges and totals. Fishing's
assorted extras remain omitted because the source states no quantity. The real
1000×560 card now uses `Kingdom` and `Resources` tabs plus two compact
three-worker pages, preventing the former clipping while preserving full
tooltip and accessibility detail. Kimi K3 and Opus found no blocking taste
defect after the reproduced accessibility, alignment, focus, and copy findings
were fixed.

Focused plain verification passes 338 tests; focused real offscreen-Qt UI and
asset verification passes 4 tests. Full discovery passes 3,876 tests in both
lanes: plain records 3,397 ordinary passes and 479 expected environment skips;
real offscreen Qt records 3,873 ordinary passes and 3 intentional skips.
Documentation audits 521 Markdown and 431 HTML files; test quality reports zero
hard issues across 3,842 tests in 176 files. Compilation, JSON, diff, asset
normalization, and worktree audits pass. Reachability improves to 1,499 actions,
2,234 reachable items, 168 orphan inputs, and 188 blocked actions.

## Penguin Hide and Seek spawn-catalog closure — 2026-08-08

RuneScape Wiki `Penguin Hide and Seek/Spawn locations` oldid `6566231`,
timestamp `2012-11-17T15:09:05Z`, enumerates the complete cutoff pool: 34
one-point and 33 two-point location/disguise pairs, plus six polar-bear wells.
The live tuples now match all 67 ordinary headings in source order. Every old
breadth ID remains stable, so active selection and spotted-state history survive
the data expansion.

The weekly mechanic still rotates five rows from each ordinary tier. A 34-week
answered-card proof reaches every ordinary spawn and every location used by the
three-point invisible penguin. Location details remain tooltips under the
settled locationless translation; no travel, roaming, trapping, community
sighting, map coordinate, or area-access gate was invented. No migration,
placeholder, new UI structure, or owner design gap was needed.

Focused plain verification passes 715 tests. Sixteen isolated real offscreen-Qt
Penguin, undo, integration, UI, and asset paths pass. Full discovery passes
3,871 tests in both lanes: plain records 3,392 ordinary passes and 479 expected
environment skips; real offscreen Qt records 3,868 ordinary passes and 3
intentional skips. Documentation audits 520 Markdown and 431 HTML files; test
quality reports zero hard issues across 3,837 tests in 176 files. Compilation,
JSON, diff, asset normalization, reachability, and worktree audits pass.
Reachability remains at 1,499 actions, 2,232 reachable items, 169 orphan inputs,
and 189 blocked actions.

## Shooting Stars crash-site catalog closure — 2026-08-08

RuneScape Wiki Shooting Star oldid `6556329`, timestamp
`2012-11-15T09:20:35Z`, supplies the exact 43-site cutoff table. The live data
now carries every name in source order instead of the six-site breadth sample.
Legacy active events repair the six former labels to their exact table names,
so loading an old save preserves the communal star. The catalog remains flavour
only under the settled locationless design; no telescope, map, travel, or
per-site gate was invented.

Darkan's current 33-site reconstruction is not the cutoff catalog. Its hidden
starting-tier call also cannot replace the disclosed AnkiScape abstraction:
installed Darkan core `2.0.6` proves `Utils.random(0, 9)` is upper-exclusive,
so that call can produce invalid tier zero and cannot produce tier nine. The
server distribution therefore remains source-blocked without creating a new
placeholder or design gap.

Focused plain verification passes 892 tests. Relevant real offscreen-Qt
verification passes a 436-test integration prefix and three direct Shooting
Stars UI paths. Full discovery passes 3,870 tests in both lanes: plain records
3,391 ordinary passes and 479 expected environment skips; real offscreen Qt
records 3,867 ordinary passes and 3 intentional skips. Documentation audits 520
Markdown and 431 HTML files; test quality reports zero hard issues across 3,836
tests in 176 files. Compilation, JSON, diff, asset normalization, reachability,
and worktree audits pass. Reachability remains at 1,499 actions, 2,232 reachable
items, 169 orphan inputs, and 189 blocked actions.

## Fishing Trawler Tiger shark depth closure — 2026-08-08

RuneScape Wiki Tiger shark oldid `6448339`, Raw tiger shark oldid `5992445`,
and rev-741 item definitions close the whole high-level catch row: Fishing 95,
80 ordinary XP, at most one fish per trip, an approximate one-in-five trip
frequency, Cooking 95, 230 Cooking XP, 250 LP healing, a 100-LP overheal cap,
item IDs `21520`/`21521`/`21522`, and non-stackable/non-exchangeable semantics.

The level-95 rare admission is separate from the common-catch selector and can
replace at most one ordinary catch. Raw tiger shark now cooks or burns into its
exact identities, cooked Tiger shark uses the shared combat-food kernel with
its real overheal cap, and all three normalized sprites have provenance. Raw
and cooked art are pre-cutoff; the burnt sprite has no pre-cutoff wiki history
and is explicitly visual-only. The exact hidden admission selector remains an
honest approximation, and the unrecovered burn endpoints are registered under
`cooking.tiger_shark_burn_endpoints`. No owner design gap surfaced.

Focused plain and real offscreen-Qt verification each ran 603 tests
successfully. Full plain discovery ran 3,869 tests: 3,390 ordinary passes and
479 expected environment skips. Full real offscreen-Qt discovery ran the same
3,869 tests: 3,866 ordinary passes and 3 intentional skips. Documentation
audits 520 Markdown and 431 HTML files; test quality reports zero hard issues
across 3,835 tests in 176 files. Compilation, JSON, diff, asset normalization,
reachability, and worktree audits pass. Reachability records 1,499 actions,
2,232 reachable items, 169 orphan inputs, and 189 blocked actions.

## Raider-set requirements enforced — 2026-08-08

Tip.It's Goblin Raids guide, last updated `2012-10-24`, states the complete
Raider-set requirement table: 8 Attack for the axe and 8 Defence for both the
chainbody and shield. The narrower wiki item revisions stated only the axe's
requirement, so live armour had defaulted to level 1. All three items now pass
their exact skill tuple through the shared equipment gate. Focused verification
passes 135 tests; full plain and real offscreen-Qt discovery each pass 3,865,
with 479 and 3 expected skips respectively. No placeholder or owner design gap
remains for this value. Documentation audits 520 Markdown and 431 HTML files;
test quality reports zero hard issues across 3,831 tests in 176 files; diff and
worktree audits pass.

## Commander Yodri reward table and expiry settlement — 2026-08-08

Tip.It's Goblin Raids guide, last updated `2012-10-24` and preserved in Wayback
capture `20121228205432`, pins the location tables omitted from the live data:
farms pay Potato, Marigold and Barley seeds; forests pay Logs and Oak logs;
mines pay Clay, Copper ore and Tin ore. The guide caps the total at ten based on
ordinary Raiders killed and says a timed-out attempt can still receive a reward.

Yodri now selects from those exact sets and pays at most one item for each of the
ten ordinary Raiders. Hollowtoof no longer creates an eleventh item. If a raid
expires after progress, the proportional payout remains claimable without
incrementing `raids_cleared`; if no Raider fell, expiry cleanly releases the
activity and combat state. The exact selection distribution remains
source-blocked, so deterministic round-robin is registered under the narrower
`goblin_raids.yodri_reward_selection` placeholder. No owner design gap surfaced.

Verification passes 116 focused tests. Full discovery passes 3,864 tests in both
lanes, with 479 expected plain skips and 3 real offscreen-Qt skips.
Documentation audits 520 Markdown and 431 HTML files; test quality reports zero
hard issues across 3,830 tests in 176 files; diff and worktree audits pass. Item
reachability retains the known 1,498-action, 2,230-reachable, 169-orphan,
189-blocked dependency ledger.

## Goblin Raids ordinary-raider count closed at ten — 2026-08-08

The former five-Raider placeholder is retired. Release oldid `6434891` and
cutoff oldid `6545250` make Yodri's payout exactly one item per raid goblin
slain. Tip.It's guide, last updated `2012-10-24` and preserved in Wayback
capture `20121228205432`, says that payout scales with Raiders killed and caps
all three site kinds at ten. The release-day `File:Goblin raid.png` screenshot
independently shows nine ordinary Raider models while Hollowtoof waits apart,
directly contradicting five and fitting the ten-Raider total.

Darkan has no Goblin Raids implementation and the client caches cannot supply
server NPC spawns. The modern wiki's ten-raider line was only added in 2022, so
it corroborates rather than supplies the value. Live raids now field ten
ordinary Raiders; a world-clock regression proves they and Hollowtoof can still
finish inside the registered 15-review active window. Focused Goblin Raids,
placeholder-register, direct-action-undo and notification-strip verification
passes 114 tests. Full discovery passes 3,862 tests in both lanes, with 479
expected plain skips and 3 real offscreen-Qt skips. Documentation audits 520
Markdown and 431 HTML files; test quality reports zero hard issues across 3,828
tests in 176 files; diff and worktree audits pass. No owner design gap surfaced.

## Goblin Raids active-window re-walk and lifecycle correction — 2026-08-08

The period half-hour figure is a notice cadence, not a raid duration. Release
oldid `6434891` and cutoff article oldid `6545250` state only that the latest
incursion is announced every half hour; revision `6452732` explicitly corrects
the claim that the activity itself starts on that interval. The complete
pre-cutoff article/talk histories, rev-741/742 interface `583:87`, and Darkan
contain no server despawn. The later approximately-30-minute Yodri sentence
first appears in 2017 revision `20647497`, so it cannot retire the placeholder.
The 15-review completion window remains registered.

The re-walk exposed a player-visible lifecycle bug: after Hollowtoof died and
Yodri arrived, the cleared raid remained active and could be joined again for
duplicate rewards. Hollowtoof's death now closes the active raid. Its Yodri
claim persists across sanitation and can coexist with a later announced raid;
claiming old spoils leaves that new raid untouched. Verification passes 113
focused Goblin Raids, notification-strip, placeholder-register and
direct-action-undo tests; all 3,861 plain tests with 479 intentional skips; and
all 3,861 real offscreen-Qt tests with 3 intentional skips. Documentation audits
520 Markdown and 431 HTML files; test-quality audits 3,827 tests across 176
files with zero hard issues; diff-whitespace and worktree-layout audits pass. No
owner design gap surfaced.

## Crucible Supreme Champion world-clock correction — 2026-08-08

Cutoff Crucible oldid `6538845` states the half-hour event interval, while
launch-update oldid `5778674` separately fixes its two-and-a-half-minute shape.
The settled 240-card world/economy day maps half an hour to exactly five
answered cards. Rev-727 exposes no server event clock and Darkan implements no
Supreme Champion event, so neither overrides that translation.

The shipped constant was already five, but the runtime compared it with a
visit-local productive-review counter. Events therefore paused outside the
arena and restarted on re-entry. The live event window now reads the shared
answered-card clock that advances before foreground dispatch. Persisted sessions
keep the event card and champion chosen at that boundary; old private countdown
fields sanitize away. A regression begins a visit after three world cards,
proves the event arrives on the visit's second review, drives the real runtime,
and proves a promotion during the event cannot retroactively select the player
as champion. Verification passes 41 focused Crucible/register tests, all 3,860
plain-discovery tests with 479 intentional skips, and all 3,860 real
offscreen-Qt tests with 3 intentional skips. Documentation audits 520 Markdown
and 431 HTML files; test-quality audits 3,826 tests across 176 files with zero
hard issues; diff-whitespace and worktree-layout audits pass. No owner design
gap surfaced.

## Crucible target-level matching correction — 2026-08-08

Cutoff Crucible oldid `6538845` preserves both the intended similar-combat
match and the observed failure that a relatively low-combat player could face
a maxed opponent. Its complete pre-cutoff article and talk histories contain no
numeric pair or range. Rev-727 has no matching table or target selector, and
Darkan's complete Crucible history never assigns a target or computes a combat
band. The exact spread and frequency therefore remain source-blocked.

The old registered `-8/0/+8/+20` cycle could not reproduce that attested
failure: the combat-60 entry gate topped out at level 80. The corrected cycle
keeps three ordinary near-level opponents and uses `+78`, clamped to 3–138, so
the same combat-60 player can reach level 138. The fourth-slot frequency is a
disclosed AnkiScape reachability choice, not a period claim. A regression drives
the real target constructor and proves the ordinary and severe boundaries.
Focused Crucible/register verification passes 39 tests. Full discovery runs
3,858 tests in both lanes, with 479 expected plain skips and 3 expected Qt
skips. Test quality audits 3,824 methods across 176 files with 0 hard issues;
documentation, diff-hygiene, and worktree audits pass. No owner design gap
surfaced.

## Crucible bounty-fee scale correction — 2026-08-03

The surviving period evidence proves the prior live curve was too small by
roughly one order of magnitude. Launch-day talk oldid `5778707` reports a
combat-60 range of 50,000 coins with rune-or-better gear to 500,000 with
nothing risked. The immutable 24 June fee-interface image records total
535,362, split into 486,693 risk expectation and 48,669 abandonment, while
cutoff Crucible oldid `6538845` reports roughly 518,000 for a maxed unarmed
player after the launch hotfix. Rev-727 interface 1298 confirms the three-part
shape but exposes no calculation, and Darkan has no fee implementation.

The disclosed reachability curve now uses a 450,000 risk baseline at combat 60,
adds 400 per level above 60, and uses a 50,000 abandonment component. It yields
the sourced 500,000 launch-day boundary and 531,200 at max combat, inside the
later 518,000–535,362 observations. Both values remain registered placeholders
because this is not the recovered server formula. A regression fixes the
combat-60 boundary. The focused Crucible and placeholder-register lane passes
38 tests. Full discovery passes all 3,804 tests in both lanes, with 460 expected
plain skips and 3 Qt skips. Documentation audits 515 Markdown and 428 HTML
files; test quality audits 3,770 tests with 0 hard issues. Diff-hygiene and
worktree audits pass. No owner design gap surfaced.

## Crucible Trophy-bone depth re-walk — 2026-08-03

The ordinary-kill amount remains source-blocked. The launch update, complete
pre-cutoff Crucible history, and complete 29-revision Trophy-bones history prove
the currency route but never state the kill quantity. Rev-727/741/742 item
definitions prove item 24444 is stackable and non-exchangeable; recovered
scripts and interfaces expose no server award. Darkan's one-item metadata
container is a later loot-key reconstruction and contradicts those period item
definitions.

The adjacent tutorial award is exact: cutoff Crucible oldid `6538845` and
Trophy bones oldid `5971782` state a four-total cap and one bone from each
tutorial. Its stale placeholder marker and register row are removed. The
two-bone ordinary-kill reachability value remains disclosed. The focused
Crucible and placeholder-register lane passes 37 tests. Full discovery passes
all 3,803 tests in both lanes, with 460 expected plain skips and 3 Qt skips.
Documentation, test-quality, diff-hygiene, and worktree audits pass. No owner
design gap surfaced.

## Crucible ordinary-kill point re-walk — 2026-08-03

The ordinary-kill award remains source-blocked. Launch-update oldid `5778674`
proves that every target slain awarded points but gives no number. The complete
pre-cutoff article and talk histories add only the separate exact one-point
rule for successful hits on the Supreme Champion. Darkan never mutates its
initialized point field, while rev-727 script 6288 only renders a supplied
delta.

The source audit, code annotation, placeholder register, and shared Darkan
ledger now capture that complete negative result. The one-point ordinary-kill
award remains a disclosed reachability value. The focused Crucible and
placeholder-register lane passes 37 tests. Full discovery passes all 3,803
tests in both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
test-quality, diff-hygiene, and worktree audits pass. No gameplay changed and no
owner design gap surfaced.

## Crucible rank-threshold re-walk — 2026-08-03

The six promotion thresholds remain source-blocked. Darkan's controller
initializes `rank` and `points` but contains no award or promotion write, while
its interface bridge only forwards those values to rev-727 scripts 6284/6288.
The client scripts render an already-computed tier and point delta; neither
reads state or compares a threshold. The pinned Crucible article and launch
update say only that rank rises every few points.

The source audit and placeholder register now capture that complete negative
caller-chain result. The 1/3/6/10/15/25 ladder remains a disclosed reachability
value. The focused Crucible and placeholder-register lane passes 37 tests. Full
discovery passes all 3,803 tests in both lanes, with 460 expected plain skips
and 3 Qt skips. No gameplay changed and no owner design gap surfaced.

## Daily Challenge assignment weighting correction — 2026-08-03

Cutoff Challenge System oldid `6579729` states that, with four eligible skills,
the desired skill has a 1-in-4 assignment chance. The old flat draw across
challenge rows contradicted that evidence: Mining's three breadth rows made it
three times as likely as a one-row skill.

The assignment path now gives every eligible skill an equal interval of its
single RNG draw, then selects a challenge inside that skill. Uniform weighting
inside the chosen skill remains honestly registered as
`daily_challenges.within_skill_assignment_weights`; Darkan has no Challenge
System, and rev-741/742 plus the cutoff talk histories expose no task selector.
A regression drives every skill interval and proves row-rich skills receive no
extra top-level weight. The focused unit/integration lane passes 47 tests. Full
discovery passes all 3,803 tests in both lanes, with 460 expected plain skips
and 3 Qt skips. No owner design gap surfaced.

## Tears of Guthix green-tear probability re-walk — 2026-08-03

The registered `0.055` chance remains source-blocked. Darkan's restored
controller settles click colour and the one-update-per-tick boundary but has no
stream rotation; its frozen target contract explicitly lists cadence, selector,
collection timing, and multiplayer acceleration as unrecovered. Activity oldid
`6579712` says only "randomly quite fast" and reports 267 tears from a capped
300-tick run. Talk oldid `6539293` contains anecdotes and theories rather than a
measured rate, while rev-727/742 expose only client-side identities.

The code, register, and source audit now describe `0.055` as a weak
reachability anchor rather than an authentic probability. No gameplay changed
and no owner design gap surfaced. The focused Tears and placeholder-register
lane passes 26 tests. Full discovery passes all 3,802 tests in both lanes, with
460 expected plain skips and 3 Qt skips.

## Bork Ork-legion style classification closure — 2026-08-03

Darkan `Bork.kt:110-111,184-205` explicitly selects melee when an Ork legion is
within one tile of its target and ranged otherwise. The shipped always-melee
pressure remains correct for AnkiScape's settled stand-near, homogeneous-front
translation. It is now documented as a distance-collapse abstraction instead
of an unrecovered period value, and `bork.ork_legion_attack_style` is retired
from the placeholder register. No ranged accuracy penalty was added.

The focused Bork and placeholder-register lane passes 28 tests. Full discovery
passes all 3,802 tests in both lanes, with 460 expected plain skips and 3 Qt
skips.

## Duellist's cap threshold closure — 2026-08-03

RuneScape Wiki oldid `6579418`, dated `2012-11-18T23:11:12Z`, is the pre-cutoff
parent of the previously cited post-cutoff cap page. It already states all six
win ranges, proving live minimums `0`, `10`, `100`, `500`, `2,000`, and `5,000`.
The live values did not change; `duel_arena_cap_thresholds` is retired from the
placeholder register and the family now cites the correct period revision.

The focused Duel Arena and placeholder-register lane passes 16 tests. Full
discovery passes all 3,802 tests in both lanes, with 460 expected plain skips
and 3 Qt skips.

## Skeletal Horror phase-identity correction — 2026-08-03

Rev 727 and 742 plus Darkan's generated NPC list and four combat-definition
files agree on the exact form identities: 320=`9176/9177`, 260=`9178`,
180=`9179`, and 100=`9180`. The live weakening rows were one identity early
after the first phase and now use `9176 → 9178 → 9179 → 9180`.

The Darkan files are explicitly marked `nostats`, and the client definitions
contain combat level rather than the Attack, Strength, Defence, and Magic
values required by the shared Combat kernel. Those four blocks therefore stay
registered placeholders; no stat is inferred from combat level. The focused
Skeletal Horror and placeholder-register lane passes 20 tests. Full discovery
passes all 3,802 tests in both lanes, with 460 expected plain skips and 3 Qt
skips.

## Grind-loop iteration 10 — Daily Challenges reward XP remains source-blocked

- Recovered the rev-741/742 Daily Challenge structs and rev-742 challenge
  interface. They settle client task metadata and presentation but contain no
  XP payout field.
- Later byte-level verification corrected the interface-search diagnosis: the
  fifteen skipped rev-742 archives begin with `0x03`, so the first-byte gate's
  `if1` label did not identify a legacy or unsupported format. The checked-in
  reader still skips them.
- A one-off reflective experiment bypassed the guard and decoded all 1,376
  affected components into coherent interfaces; none related to interface 1343.
  Reproducing that complete search still requires a guard fix or byte-level
  parser. `daily_challenges.reward_xp` remains registered because the relevant
  structs and decoded interface 1343 contain no amount. No gameplay value changed.
- Full discovery passes 3,802 tests in both lanes, with 460 expected plain skips
  and 3 Qt skips.

## Frozen boss combat-level closure — 2026-08-03

`tools/query_openrs2_cache_definitions.sh` now exposes exact NPC combat levels.
The 144 rows covering Luminescent icefiend (`9912-9928`), Plane-freezer
Lakhrahnaz (`9929-9947`), Gluttonous behemoth (`9948-9964`), Astea Frostweb
(`9965-10021`, three forms per level), To'Kash (`10024-10039`), and Icy Bones
(`10040-10057`) are identical in rev 727 and rev 742.

Every decoded value matches the six shipped Frozen boss ladders, so
`dungeoneering.boss_combat_level_ladders` is retired from the placeholder
register without changing gameplay. The cache rows do not prove server tier
selection, combat stats, lifepoints, or maximum hits; those placeholders remain.
Focused cache, Dungeoneering-data, and register coverage passes 13 tests. Full
discovery passes all 3,801 tests in both lanes, with 460 expected plain skips
and 3 Qt skips. Documentation, test-quality, shell-syntax, diff, and worktree
audits also pass.

## Achievement Diary depth closure — 2026-08-03

`tools/generate_achievement_diary_data.py` no longer embeds a developer-local
2011Scape path. Its CLI requires the exact `--items-yml` input and passes that
path through the build seam; a synthetic-source regression proves the generated
equipment rows come from that explicit file. Regeneration against the local
rev-667 source is byte-identical to the checked-in 384-row catalog.

The existing v108 migration regression already exercised a superseded deed
being removed and source-ready output/shop deeds being re-earned. It now also
holds an unrelated, unmet completion across migration, proving revalidation is
selective rather than a wholesale diary reset. The focused Diary/storage lane
passes 168 tests. Full discovery passes all 3,800 tests in both lanes, with 460
expected plain skips and 3 Qt skips. Documentation, test-quality, diff, and
worktree audits also pass.

GPT-family Workflows run `c48d7907-2f2e-4e3c-a365-7ba95b3aec2a` exhausted both
read-only leaves on tool-output budgets before either produced a final. Root
used no unverified conclusion from them and independently reproduced both
boundaries. The next depth slice revalidates Frozen Dungeoneering boss combat
levels from dated NPC definitions.

## Exact item-definition depth — 2026-08-03

`tools/query_openrs2_cache.sh --id` now prints deterministic exact item model,
recolour, texture, sprite-recolour, bonus, stackability, exchangeability, and
option fields. Its first production pass corrected two player-facing data
families. Temple Trekking now maps blue/yellow/red Reward tokens to exact cache
items `7776/7774/7775`; the previous blue and yellow IDs were reversed.

Goblin cower shield and the three Raider pieces now use exact rev-741 IDs
`25350-25353`, are non-exchangeable, and project their authentic item-definition
combat bonuses. The previous rows used unrelated `202xx` IDs and flattened all
bonuses to zero. The Temple token-colour and Raider-bonus placeholders are
retired. Dominion Tower reward identities remain honestly source-blocked because
the prior near-cutoff item-name search found no matching rows.

Focused cache/data/registry/equipment coverage passes 152 tests, and two real
offscreen equipment-stat UI checks pass. Full discovery passes all 3,799 tests
in both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
test-quality, shell-syntax, diff, and worktree audits also pass.

## Client-side blocked-row re-walk — 2026-08-03

The rev-727 Conquest client resolves the Foot Soldier's 30-versus-50 setup-cost
conflict. Interface 1015 renders troop cost from NPC param 1138, CS2 script 486
maps the Foot Soldier to NPCs 12202/12205, and both rows carry 50. The registered
placeholder and code marker are removed; no runtime behavior changes because
the conservative value was already 50.

`tools/query_openrs2_cache_definitions.sh` now has a deterministic `--params`
mode for exact NPC and object IDs, backed by a real-cache regression. Diary-lamp
minimum levels, Conquest board/command-point rules, and the previously audited
Dominion Tower and Dungeoneering server formulas remain blocked: the client has
no table that settles them. Evidence is in
`source-audits/client-blocked-rewalk-2026-08-03.md`.

Focused definition, placeholder-register, and Conquest coverage passes all 34
tests. Full discovery passes all 3,797 tests in both lanes, with 460 expected
plain skips and 3 Qt skips. Documentation, test-quality, shell-syntax, diff,
and worktree audits also pass.

## Period-cache interface reader — 2026-08-03

The source toolchain can now read index-3 interface definitions without copying
the giant decompiled client decoder. `tools/query_openrs2_interfaces.sh` wraps
the installed Darkan core 2.0.5 loader and counts, dumps, or searches component
definitions from either a dated disk zip or extracted cache. Output exposes
stable component identities, client layout and visibility state, text, assets,
actions, and principal script hooks.

Count probes and one real component decode pass across all seven local builds.
Exact rev-727 fixtures pin the Grand Exchange heading and travel action. This
closes a client-data tooling gap only; client script hooks and displayed values
do not prove server behavior. The next depth pass re-walks existing
client-side-only `source_blocked` rows. Full discovery passes all 3,796 tests in
both lanes, with 460 expected plain skips and 3 Qt skips.

## Period-cache config reader — 2026-08-03

The source toolchain can now read all three previously opaque shared
configuration families. `tools/query_openrs2_cache_configs.sh` accepts a dated
disk zip or extracted cache and counts, dumps, or searches enums, structs, and
params without modifying the cache. Enum and struct output uses Darkan core's
loaders; the small param decoder follows the rev-727 deobfuscated client and
fails on an unknown opcode instead of silently drifting.

The reader passes exact rev-727 fixtures for achievement enum 3483, struct 0,
and param 0. Count probes pass across every local build from 652 through 742.
This closes only a client-data tooling gap; server-side rolls, rates, timers,
and reward logic remain source-blocked when no independent source exists. Full
discovery passes all 3,793 tests in both lanes, with 460 expected plain skips
and 3 Qt skips.

## Achievement Diary 384-task roster — 2026-08-03

All 32 regional tiers now contain exactly 12 tasks. The generator preserves
every previous durable task ID, fills short tiers from unused authentic rows in
the same family while retaining their original tier identity, and uses only 22
explicitly labelled progression anchors for the remaining source shortfall.
Each anchor reuses an exact skill-level requirement attested elsewhere in that
family and no tier contains more than three.

Generation now fails closed on unknown quest or skill keys, anchors without a
family source level, duplicate authentic requirements, misplaced preferred
source IDs, too many anchors, and tiers that do not total 12. Three existing
Miscellaneous activity counters are connected to their period deeds. The
player-facing Cabinet marks anchors and explains unavailable authentic rows at
the tier level without exposing implementation terminology.

All 422 earlier task IDs remain and 52 rows were added. Focused verification
passes 128 pure/integration tests and 27 real offscreen-Qt tests; deterministic
regeneration is byte-identical. Full discovery passes all 3,790 tests in both
lanes, with 460 expected plain skips and 3 Qt skips.

## Dungeoneering guardian-room funding reconciliation — 2026-08-03

The design-answer 3.25 implementation was already on `main` but remained in the
grind queue as parked work. Commits `6ced27e8`, `dcf41c0d`, `c5eb86c8`,
`6e07d1bc`, and `05016790` replaced the starter Herblore resource-room coin
cache with the authentic guardian-room mechanism. On C5+ floors, only players
with Druidic Ritual complete and Herblore 5 receive the registered 1,010 Rusty
coins, split across critical-path guardian rooms; optional rooms cannot dilute
or extend the payout, and C1-C4 receive none.

The room-id ledger persists the split across reloads. Its migration recognizes
legacy cache-funded, pre-drop, and completed-drop saves so it does not lose or
duplicate coins. The natural-floor Valerian potion chain remains reachable end
to end. The product revision passed both 3,785-test full lanes in iteration 1;
fresh plain and offscreen-Qt focused lanes each pass all 54 Dungeoneering data,
logic, and placeholder-register tests. No new code or source value was needed.

## Pass 6 B.15 skill-selector hybridization — 2026-08-03

Per-skill target surfaces now dispatch through one row-count-aware renderer.
Lists with fewer than 25 rows stay flat; lists with at least 25 grouped rows use
the collapsible tree; and lists without group metadata stay flat at any size.
Both forms retain the same selection callbacks and current-target semantics and
now share alternating stripes, a measured 30-pixel row height, the translucent
green current row, and bold current text.

Real widget tests cover the 24/25 boundary, the large ungrouped fallback, both
widget classes, both stripe flags, exact row height, current-row color, and font
weight. The full plain lane passes 3,785 tests with 459 declared skips, and the
full offscreen-Qt lane passes the same 3,785 tests with 3 skips. Kimi K3
performed a bounded independent UI review and found no material defect; its two
concrete low-risk notes were incorporated before closure. The other pass-6
selector concerns remain owned by D.1 and were not reopened.

## Conquest — 2026-07-30

Reached horizontal breadth level one in the `conquest/breadth-one` worktree,
schema 102.

Conquest is a safe persistent Activities match against a labelled bounded
simulated opponent. Combat level 40 gates entry. Casual uses the reconstructed
default ten-troop formation and four commands; Advanced exposes the complete
seven-unit source roster, 1,000-point budget, ten-unit placeholder cap, up to four
of all nine exact commands, and balanced/aggressive/defensive doctrines. The
persisted board uses the settled 20×20 placeholder geometry and seeded obstacle
layouts. One productive review runs one troop action for each side through the
same bounded heuristic, with exact movement, range, damage, LP, command effects,
cooldowns, normal-kill command-point income, Bombard's zero income, and Chastise's
last-troop restriction. Twenty seeded reducer matches all terminate within 60
exchanges.

Elimination and direct resignation settle into Pest Control's shared commendation
wallet. The monotone 1–10 placeholder curve uses the exact ×2/×3/×4 combat bands
and 20/30/40 caps, pays both outcomes without a win bonus, and respects the shared
500-point cap. Rating starts at 1,000, floors at zero, uses a registered
opponent-sensitive placeholder formula, and unlocks the 150-commendation Void
knight deflector purchase at 1,250. The deflector's sourced equipment row and both
period Music Log tracks are live.

Migration and repair, activity arbitration, cadence, telemetry, review/direct
undo, activity/equipment/item registration, normalized art and provenance, and
the compact three-page Activities card are integrated. The correction guard tests
pin Knight range 1, Mage range 4, Champion 500 LP, Stoicism 75 CP, and the absence
of a combat triangle or hybrid roster. Eighteen in-scope placeholders are
registered. The quest-only pest battle and Torcher candidate, staked mode,
human-only truce/disconnect flows, and Void-set substitution semantics remain
outside this slice.

Focused verification passes 137 backend tests, 3 direct/review undo integration
tests, 2 real offscreen-Qt card tests, and compilation of the affected package
surfaces. Source authority:
`source-audits/conquest-harvest-2026-07-28.md`. Results:
`status-updates/conquest-breadth-one-results-2026-07-30.html` and
<https://859ao4lbxil1.postplan.dev>.


## Gnome Restaurant and gnome cooking — 2026-07-28

Reached breadth level one in the `families/gnome-restaurant` worktree, schema 97.

**Gnome cooking is real Cooking.** Twenty period dishes ship as Cooking targets
with exact levels (6 to 42), exact XP (50 to 190) and the exact ingredient list of
both period assembly stages, consumed in one action the way the pie and pizza prep
bridges already work. Seven knife bridges turn fruit into the slices and chunks the
recipes call for. Every ingredient was already reachable: Grand Tree Groceries and
Funch's stock the dough, spice, leaves, tins, trays, moulds, shaker, glass and
spirits, King worm and Swamp toad come from pickpocketing gnomes, and Herblore
already removes toad's legs. The thirteen dishes are edible with the healing values
2011Scape's own food table gives them, and the seven cocktails are drinkable with
their sourced Strength boost and Attack drain through a new flat-level drink
consumable.

**The delivery loop.** One productive review delivers the outstanding order and
takes the next job, so the loop needs no direct action between deliveries. `Again`
never destroys an order: it spends six world minutes of the order's own source
window, and what survives becomes the chance of the good tip. Nineteen easy and
twenty hard customers ship complete with their exact quest and Magic gates, easy
jobs pay one point and hard jobs three, twelve points pay the Reward token and each
further twelve banks another free meal up to ten, and all thirty-seven sourced tip
rows are reachable — including the Gnome scarf and goggles, which only Captain
Ninto and Captain Daerkin ever hand over. The entry gate reads durable Cooking
production, so four dishes and four cocktails cooked at any time in the past open
the service without a single tutorial-only review.

Five registered placeholders cover the burn endpoints, the order-request weights,
the tip weights, the speed-to-tip curve, and the token's food draw. The presentation
fork deferred since 2026-07-17 is queued as design decision 3.19 with both layouts
drawn; the recommended one is implemented. Durable record:
`source-audits/gnome-restaurant-harvest-2026-07-28.md`.


## Current Baseline — 2026-07-16

AnkiScape now has 18 complete skill surfaces, five partial Combat-trained skills, and two planned skills. Canonical live status is in `future-work-kanban.md`; the dated 2026-07-10 completion audit is archived baseline evidence.

## Always-visible reviewer strip — 2026-07-28

Built in the `hud-strip` worktree; the last unbuilt decision from pass 3 of the
playtest notes (design-thread section 4.8).

**What the strip contains, and when.** The running activity's real skill bars
appear whenever that activity can award experience on the next review, so a live
shooting star shows Mining and the bar disappears when the star resolves; the
bars come from `ACTIVITY_TRAINED_SKILLS`, which mirrors the runtime award sites,
with the Evil Tree resolving by phase and Tears of Guthix by its least-experience
reward skill. Two bars is the cap and the rest are named in the caption. The
Grand Exchange fills drawer moved out of its tab to sit under the experience
bars, appears only while a slot is occupied, opens collapsed, and keeps pass 2's
green-for-complete and yellow-for-partial rows newest first. The Distraction and
Farming badge is the one permanent seat.

**Watching is settable.** A `★`/`☆` control on the Activities detail card's
shared control row pins one Distraction. It sits there rather than in forty-odd
bespoke card headers, which is also how the five panel-class families get it for
free. The pin commits through `commit_direct_action`, so it undoes. Schema 95
adds `dnd_favourites`, sanitized against the Distraction group plus the Evil
Tree, which has no activity spec of its own.

**Boundaries kept honest.** Combat activities and the five reward-table families
show no bar, because their skill comes from the attack style or from a payout
choice. Section 3.15 records the one fork this work found — a pin adds a badge
line and never removes one — with its recommendation implemented.

**Verification.** Both lanes green from the 3251/377 baseline, up 26 tests:
`tests/test_review_strip_logic.py` (23 pure cases), `tests/test_review_strip.py`
(15 offscreen Qt cases, replacing `test_farming_hud.py` and
`test_distraction_hud.py` with every case they pinned carried over), two pin
cases in `tests/test_main_menu_widget.py`, one relocation case for the Grand
Exchange tab, and two undo-seam cases in
`tests/test_direct_action_undo_seam.py`. A light and dark offscreen pass probes
geometry rather than pixels, per the offscreen rule.

## Tears of Guthix and Enchanted Key — 2026-07-26

Both reached breadth level one in the `families/batch-c` worktree.

**Tears of Guthix.** The July audit called the exact values source-blocked, but
almost all of them were in the revision it had already pinned. Shipped exactly as
stated: the "100,000 experience or one quest point since you last participated"
gate, the tick-per-Quest-Point cavern timer capped at three minutes, `level * 6`
capped at 180 with the stone bowl and 300 with the ornate one, the least-
*experience* reward rule, and the ornate bowl's two level-80 requirements. Where
the ornate bowl article contradicts the D&D article about "five times", the audit
records the conflict and the code ships the explicit caps. The per-tick
collection rate and the green-tear chance stayed unrecoverable and are registered
placeholders. Two things are AnkiScape abstractions and are labelled as such
everywhere: one review is six game ticks (design-thread queue 3.2), and up to two
weekly visits bank under Decision 2.

**Enchanted Key.** Darkan already implements the hunt, so the pass was
corroboration: all eleven loot rows, the Chebyshev metric, the eight temperature
bands, the melt and Erin's 500-coin replacement all agree with the pinned
Enchanted key revision. Nothing needed a placeholder. The one abstraction is the
walking, and it has a consequence the audit names rather than hides — three of
the eight temperature bands cannot fire once the search is flattened to
site-to-site, and a test pins which bands are live. The three god mjolnirs join
through a family-owned item seam.

Both families follow the Skeletal Horror shape: a pure data module, a pure logic
module owning every enable and visibility flag, a panel that only renders those
flags, runtime and storage wiring, undo through `commit_direct_action`, period
art with pinned provenance, and four layers of tests that reach every reward by
constructing the state a player would actually be in.

## TzHaar Fight Pit horizontal mechanic closure — 2026-07-22

- Added a persistent safe match against three bounded player-relative rivals,
  with Casual weakest-first and Advanced aggressive/defensive plans.
- One productive review advances one live six-tick Combat slice. Bounded rival
  attrition and late review-counted pressure close stalled rounds without wall
  time; safe defeat restores match resources and retains ordinary possessions.
- Personally defeated rivals add their exact Combat level to pending TokKul.
  Championship settles the purse, Fire cape doubles it, and explicit leave
  forfeits it.
- Added schema 81 migration/repair, activity arbitration, cadence/telemetry,
  review/direct undo, runtime and enemy registries, normalized period icon,
  provenance, and a compact Activities card.
- Focused pure, storage, runtime, registry, integration, and real offscreen-Qt
  checks pass. Native Anki and external taste review remain deferred external
  gates under the locked-session and quota holds. No design question surfaced.
- Durable audit:
  `source-audits/tzhaar-fight-pit-horizontal-readiness-2026-07-22.md`.
- The breadth goal is paused at the owner's Codex-quota boundary before
  recomputing the next source-ready family from the disposition ledger.
- Results:
  `status-updates/tzhaar-fight-pit-horizontal-results-2026-07-22.html` and
  <https://hebbv2uq7why.postplan.dev>.

## Shades of Mort'ton horizontal mechanic closure — 2026-07-22

- Integrated the completed-quest open loop: communal repair, personal sanctity,
  repair resources, altar lighting, sacred-oil and Serum 208 blessing, all ten
  pyre-log recipes, live six-tick Loar Combat, cremation, and bronze-key chest
  opening.
- Casual follows the current bottleneck; Advanced persists one fixed duty.
  Simulated population affects only communal repair, never personal rewards.
  Leaving preserves meters and restores the prior Combat target.
- Added schema 80 migration/repair, cadence and telemetry, activity ownership,
  review/direct undo, registries, hidden Loar target, normalized cutoff assets,
  provenance, reproducible fetch/render tools, and a compact Activities card.
- Focused pure, runtime, storage, integration, registry, asset, and real-Qt
  checks pass. Ordinary full discovery passes all 2,453 methods with 310
  declared skips; full real offscreen Qt passes all 2,453 methods with one
  intentional skip. Test-quality, documentation, compilation, provenance,
  diff, and worktree gates pass. Root inspected ready and active 1200×760 dark
  renders.
- The remaining shades, key/chest tiers, reward catalog, and unpinned GE buy
  limits are explicit data depth. No design question surfaced. Native Anki and
  Kimi K3/Fable taste approval remain unclaimed under the owner's quota hold;
  the Mac session remained locked for native inspection.
- Durable audit:
  `source-audits/shades-of-mortton-horizontal-readiness-2026-07-21.md`.
- The next source-ready frontier is TzHaar Fight Pit. Work pauses before that
  slice at the owner's Codex-quota boundary.
- Results:
  `status-updates/shades-of-mortton-horizontal-results-2026-07-22.html` and
  <https://whux17tpdjx6.postplan.dev>.

## Stronghold of Player Safety horizontal mechanic closure — 2026-07-22

- Added the three-review poster-to-crevice Landmark route, preserving the
  period no-combat-required path and permanent surface unlock.
- Added the atomic one-time chest package of 10,000 coins, Safety gloves, two
  independently targetable 500-XP lamps, and the Safety First emote. Glove
  reclaim checks inventory, equipment, the active grave, and Death's Office.
- Added optional Cockroach soldier entry after the lever landmark and a real
  switch to the ordinary Combat surface. Public level, life points, cadence,
  weaknesses, and maximum hit are preserved; hidden stats are disclosed
  fallbacks and unclosed drop probabilities remain absent.
- Integrated schema 78 migration/repair, Utility review dispatch,
  cadence/telemetry, direct and review undo, registry/equipment reachability,
  normalized cutoff assets/provenance, and a compact Activities card with
  deterministic route and reward renders.
- Focused mechanics, runtime, migration, registry, direct-undo, live-Combat,
  and real-Qt interaction tests pass. Ordinary full discovery executes 2,440
  tests with 308 declared dependency skips; full real offscreen Qt discovery
  executes 2,440 tests with one skip. Documentation and test-quality audits,
  provenance JSON, compilation, diff, and worktree safety pass. Native
  Anki inspection is blocked by the locked Mac; Kimi/Fable taste review remains
  deferred under the explicit quota hold. No design question surfaced.
- Durable audit:
  `source-audits/stronghold-player-safety-horizontal-2026-07-22.md`.
- Results:
  `status-updates/stronghold-player-safety-horizontal-results-2026-07-22.html`
  and <https://396na7vqe2p8.postplan.dev>.

## Barbarian Assault horizontal mechanic closure — 2026-07-22

- Integrated Captain Cain's tutorial, Casual wallet balancing, Advanced fixed
  roles, all ten waves, safe restart/leave, four Honour-point wallets, the
  persistent eight-Omega-egg Queen front, exact terminal points, and one
  non-stacking Queen credit.
- Attacker duties reuse one live six-tick Combat slice. Collector, Defender,
  and Healer resolve sourced call-following duties through the competent-team
  abstraction; `Again` idles on ordinary waves and applies bounded Queen
  pressure without advancing an egg.
- Added the exact Runner-boots four-wallet purchase and period equipment block,
  schema 77 migration/repair, shared activity ownership, generic Utility
  dispatch, cadence/telemetry, direct/review undo, registry reachability,
  normalized assets/provenance, and reproducible fetch/render tools.
- Added a compact Activities card for tutorial, plan, wallets, wave/Queen
  progress, purchase, selection, and leave. Root inspected ready and Queen
  dark-palette renders; the real offscreen interaction path passes.
- A bounded Workflows audit found two concrete pure-boundary defects: entry
  could overwrite an active Combat encounter and malformed saves could enter
  the Queen before wave 10. Both have regressions and are fixed. Focused
  cross-family verification passes 710 tests. Ordinary full discovery executes
  2,433 methods with 307 skips; real offscreen Qt executes 2,435 methods with
  one skip. Both are failure-free. Documentation, test-quality, normalization,
  compilation, diff, reachability, and worktree-safety gates pass.
- Kimi review was denied at the external-data boundary, Opus authentication
  could not refresh, Fable stayed reserved, and the native Anki control bridge
  could not start. No design question emerged.
  Remaining armour, horn, gamble, and hidden-rate rows are data depth. Durable
  audit: `source-audits/barbarian-assault-role-model-2026-07-18.md`.
  Results: `status-updates/barbarian-assault-horizontal-results-2026-07-22.html`
  and <https://rqaw2ino01ze.postplan.dev>.

## Varrock Museum horizontal mechanic closure — 2026-07-22

- Added a persistent derived Kudos ledger with fourteen quiz displays, five
  specimen exhibits, the Clean-necklace Digsite-pendant unlock, sixteen
  representable quest-story claims, Orlando's one-time XP, and all three exact
  Kudos milestone packages.
- Cleaning requires The Dig Site, worn Leather gloves and boots, and Trowel,
  Rock pick, and Specimen brush in the Museum carried pack. Dagon'hai history
  and the Prophecy tablet must likewise be brought in that pack for Minas.
- The missing period cleaning probability is not fabricated. One review
  represents enough cleaning for the next exhibit, followed by one final
  Clean-necklace discovery; this translation is disclosed in cadence coverage.
- Added schema 76 persistence, review telemetry, direct/review undo, the Magic
  target gate, period item identities, normalized assets and provenance,
  reproducible fetch/render tools, and a compact Landmark card.
- The source maximum remains 183 Kudos. Ghostly Robes and Shattered Heart own
  the currently unavailable 20 points; the live 163-point subtotal still
  reaches every threshold. Remaining cleaning distributions and ordinary
  rewards are data depth, and no design question surfaced.
- Focused unit, integration, migration, registry, Magic, asset-normalization,
  and real-Qt interaction checks pass. Current-HEAD ordinary discovery passes
  all 2,419 methods with 306 declared environment skips. The offscreen Qt
  discovery snapshot passes all 2,417 methods with one skip, and the concurrent
  Familiarisation addition separately passes its full 28-test module under
  ordinary Python and real offscreen Qt. Documentation, test-quality,
  provenance, compilation, diff, and worktree-guard checks also pass. Native
  Anki remains unclaimed while the Mac is locked, and the Kimi/Fable taste pass
  is deferred under the owner's quota hold.
- Published the self-contained closure report at
  <https://fe2ohwaibdw3.postplan.dev>.

## Pest Control horizontal mechanic closure — 2026-07-21

- Integrated the twelve-beat shared assault through schema 75, storage repair,
  activity arbitration, cadence, telemetry, review dispatch, direct commands,
  direct/review undo, and Again progression.
- Combat 40 and 70/100 lander tiers, follower exclusion, four portal fronts,
  a 2,000-LP Void Knight, crowd damage, Spinner healing, pressure relief,
  safe death, terminal loss, and explicit forfeit are live.
- Portal attacks reuse six-tick live Combat at the source half-XP rate. Casual
  chooses the best lander and bottleneck duty; Advanced persists one eligible
  lander and fixed assault, defend, or seal duty.
- Wins grant cutoff `combat level × 10` coins and `2/3/4` commendations capped
  at 500. The representative shop action buys a ten-point Void seal `(8)`;
  all eight charge/equipment states persist and are registered.
- Added normalized 2012 detailed-seal art for the activity and charged item
  family, reproducible provenance-aware fetching, a compact ready/active card,
  and a deterministic real-Qt renderer.
- Focused pure, runtime, migration, direct-undo, registry, UI, and global asset
  normalization checks pass. Root render QA found no clipping or hierarchy
  defect, and full real-Qt discovery passes all 2,407 tests with one
  intentional skip. Kimi's fresh telemetry gate and Opus authentication both
  failed closed, so no external taste approval is claimed; Fable was not used.
  Native Anki Computer Use could not start its local bridge, so no native
  detail-card claim is made.
- Remaining reward equipment, supply packs, charms, and exact hidden crowd
  rates are data depth. Durable audit:
  `source-audits/pest-control-game-model-2026-07-18.md`. Results:
  `status-updates/pest-control-horizontal-results-2026-07-21.html` and
  <https://pix53v8uzs1k.postplan.dev>.

## Castle Wars horizontal mechanic closure — 2026-07-21

- Implemented a persistent ten-review match with exact no-food/no-head/no-cape
  entry boundaries, safe death, five-review participation credit, exact 2/1/0
  tickets, explicit forfeit, Casual bottleneck selection, and Advanced fixed
  duty/team policy.
- Capture, defend, barricade, repair, catapult, and support all resolve real
  state. Defend reuses live Combat and preserves ordinary Combat XP. Support
  consumes its free bandage only when it has an effect, then falls back to the
  current bottleneck.
- Added the representative ticket shop: Basic decorative body/legs/shield set
  bonuses, exact Saradomin-halo prayer-drain list, 500-game Hobbyist cape,
  reusable four-part ballista, consumable ammunition, and Castlewars
  chinchompas, with full-ticket resale.
- Added schema 74, persistence sanitization, activity arbitration, cadence,
  telemetry, direct/review undo, item/equipment registration, reproducible
  cutoff assets and provenance, and a compact paginated Activities card and
  ticket-shop dialog.
- A bounded Sol-high Workflows review found and root reproduced two integration
  defects: Casual runtime forced the saved duty, and no-effect Support wasted a
  beat. Both are fixed with regressions. The suggested halo/cape entry
  exception was rejected as contrary to the cutoff universal entry ban.
- Full offscreen discovery passes all 2,373 tests with one intentional skip.
  Documentation, test-quality, item-reachability, registry, asset-normalization,
  diff, and worktree audits pass. Native Anki shows one launcher, one dialog,
  separate Utilities/Activities, the four-page picker, and the Castle Wars row
  with its normalized icon; native row activation was blocked by the macOS Qt
  accessibility bridge, so only real-Qt detail/shop coverage is claimed.
- Remaining reward variants, match potions, hybrid-armour chance, and hidden
  crowd/score rolls are data depth. Clan Wars dangerous-red-portal parity and
  the cutoff removal of Duel Tournaments remain source/contract conflicts in
  `design-gaps-implementation-2026-07-19.md`. Durable audit:
  `source-audits/castle-wars-horizontal-readiness-2026-07-21.md`. Results:
  `status-updates/castle-wars-horizontal-results-2026-07-21.html` and
  <https://6xzb9r97ffac.postplan.dev>.

## Big Top Bonanza horizontal mechanic closure — 2026-07-21

- Replaced the retired Agility-only Circus target with one Activities-only
  multi-skill performance system for Magic, Ranged, Agility, Fire-breathing,
  Flaming poi, and Thieving.
- Added the complete cutoff trick and XP tables, six- and ten-attempt limits,
  quest gates, zero-XP failures, once-per-level-band XP, answered-card weekly
  gates, Casual strategies, and Advanced routines.
- Added atomic review resolution, one-skill XP dispatch, representative costume
  rewards, equipment use, free reclaim, direct abandon, persistence,
  schema-72 migration, cadence coverage, telemetry, and direct/review undo.
- Added five normalized period reward sprites, one activity icon, complete
  provenance, reproducible equipment generation, and a compact card on the
  paginated Distractions and Diversions page.
- Opus found seven concrete interaction and hierarchy defects. Root fixed the
  reward-band leak, lock-state ambiguity, duplicate result copy, fixed-length
  routine editor, missing score label, weak mode names, and stale accessible
  action name. Fable stayed reserved, and Kimi's quota gate failed closed.
- Native Anki found one additional persistence defect that headless tests
  missed: an old TEXT-backed player-data row failed on save in Anki 25.09.4.
  The runtime now keeps a recovery copy, recreates the canonical BLOB row, and
  removes the recovery key only after success. A real Anki-collection test
  reproduces the exact failure and proves the repair.
- The owner profile keeps its prior Barrows selection. A byte-for-byte safety
  copy exists at
  `/tmp/ankiscape-player-config-before-type-repair-2026-07-21.anki2`.
- Hidden success and audience-score formulas and the remaining costume
  variants stay explicit data depth. No owner design gap emerged. See
  `source-audits/circus-horizontal-implementation-2026-07-21.md`.
- Verification ran all 2,322 non-Qt tests successfully with 303 declared skips.
  The 2,322-test offscreen Qt run passed 2,320, skipped one, and found one
  attributable concurrent-work oracle failure: Trouble Brewing had entered the
  activity registry before its writer updated the old exact-set UI assertion.
  Focused Circus and real Anki-storage coverage, native Anki, docs,
  test-quality, assets, diff, and worktree checks pass. Results:
  `status-updates/big-top-bonanza-horizontal-results-2026-07-21.html` and
  <https://zka07zkf8ey8.postplan.dev>.

## Mage Training Arena source-readiness harvest — 2026-07-21

- Pinned the complete four-wallet reward catalog, caps, room restrictions,
  death consequence, action checkpoints, and wand chain from RuneScape Wiki
  oldid `6491109`, independently corroborated where available by RuneHQ's
  `2012-07-01` guide state.
- Recovered period observational throughput for Telekinetic, Alchemist, and
  Graveyard from a dated 2006 Tip.It player analysis.
- Verified that Darkan implements only Arena teleports and game-main implements
  no Arena rooms. Enchantment throughput and associated Arena server cadence
  remain `source_blocked`; ordinary spell timers cannot substitute for the
  missing collection/deposit loop.
- Left product code unchanged. The settled four-wallet goal router cannot ship
  honestly until all four workloads are source-calibrated or the owner later
  authorizes a disclosed global cadence abstraction.
- Full record:
  `source-audits/mage-training-arena-source-readiness-2026-07-21.md`.

## Trouble Brewing horizontal mechanic closure — 2026-07-21

- Implemented the complete sixteen-beat team-race abstraction with authentic
  Cabin Fever/Cooking gates, three boilers, exact recipe stores, Casual and
  Advanced policy, two-way sabotage, forced repair, rum packing and spill,
  opposing score, explicit leave, and terminal Pieces-of-Eight settlement.
- Exact task and bottle XP is awarded immediately on each productive review,
  so leaving preserves earned XP while forfeiting unfinished match state and
  terminal currency. `Again` advances only the live race and opponent.
- Added schema-73 persistence, activity-session arbitration, cadence,
  telemetry, review/direct undo, normalized period activity/reward art, live
  zero-stat Blue tricorn equipment, and the compact paginated Activities card.
- Remaining reward rows and hidden source rolls are data depth. No owner design
  question surfaced. Kimi was quota-gated and Opus could not authenticate, so
  external taste signoff remains an availability follow-up; root dark-palette
  render QA passed.
- Durable evidence:
  `source-audits/trouble-brewing-horizontal-mvp-2026-07-21.md`.
- Results: `status-updates/trouble-brewing-horizontal-results-2026-07-21.html`
  and <https://r8gg5tai8i28.postplan.dev>.

## Wicked hood horizontal mechanic closure — 2026-07-21

- Added the complete manual Essence, Runes, Teleport, daily-reset, fed-access,
  one-hood, loss, and reclaim graph for a carried or equipped Wicked hood.
- Split each sourced altar route into a disclosed return, bank, and outbound
  abstraction. A charged matching teleport removes only the unspent outbound
  tail and preserves ordinary repack and action boundaries.
- Added exact baseline and Runespan-upgrade caps, Elemental and Omni feed
  effects, non-stacking 240-answer day resets, persistence, migration, direct
  undo, review undo, and durable bank-run phase metadata.
- Expanded Great Orb Project with the 125-token Elemental talisman, Elriss's
  first and replacement Omni-talisman claims, the exact one-time 13,605 XP,
  and Korvak's Omni-tiara conversion. The twelve-item first-claim gate does not
  consume the shown items.
- Registered normalized period sprites for Elemental talisman, Omni-talisman,
  and Omni-tiara. Corrected Rune and Pure essence to player-facing
  nonstackable metadata and kept the new feeds reachable through quests, the
  Grand Exchange, and the representative Great Orb shop.
- Opus's taste pass drove the hidden pre-claim state, compact grid, clearer
  hierarchy, truthful lock copy, accessible tooltips, and narrow-width fixes.
  Kimi's quota gate failed closed, and Fable stayed reserved.
- Verification: all 2,266 non-Qt tests pass with 300 expected skips and all
  2,266 real offscreen-Qt tests pass with one intentional skip. Test quality,
  docs, compilation, JSON, diff, asset normalization, reachability, native
  Anki, and worktree safety pass. Native Anki showed one menu and the expected
  Runecrafting and Great Orb locked states without changing the owner save.
- Runespan outfit acquisition and session mechanics remain source-blocked; only
  the hood's future allowance-cap constants exist. Ourania remains source-blocked
  on its exact output distribution. No owner
  design gap emerged. See
  `source-audits/gap-grill-11-runecrafting-provenance-2026-07-10.md`.
- Results: `status-updates/wicked-hood-horizontal-results-2026-07-21.html`;
  mobile copy: `https://8c7s96iiatk5.postplan.dev`.

## Phoenix Lair horizontal mechanic closure — 2026-07-21

- Implemented the complete owner-settled ritual: exact quest, Slayer, tool,
  Combat, and daily gates; one persistent aggregate five-guardian front; one
  pyre-preparation review; and one persistent Phoenix fight.
- Added guaranteed guardian Ashes, exact first/repeat XP and quill rewards,
  dangerous shared death/grave handling, non-resumable abandonment, activity
  arbitration, prior Combat-target restoration, schema 70 migration, cadence,
  telemetry, and whole-boundary undo.
- Added the contextual Clap/Kick egg choice, distinct Cute/Mean pet acquisition,
  below-72 egg banking, and instantaneous level-72 hatch actions on the Pets
  surface. The source-blocked egg chance uses a labeled `1/1000` breadth
  abstraction.
- Added three normalized period item sprites with provenance and a reproducible
  fetch helper. The Phoenix quill doubles as the activity icon, replacing the
  unsuitable modern location screenshot found by Opus.
- Opus's read-only taste pass also removed source-audit jargon, normalized the
  28 px pixel-art header, styled enemy-health progress, clarified active and
  locked states, and made the Summoning 72 hatch gate visible without hover.
  Fable stayed fully reserved.
- Exact guardian stat/drop depth, Lesser-warrior max hit, historical egg odds,
  and dust timing remain explicit source debt. No owner design gap emerged.
  See `source-audits/phoenix-lair-implementation-data-2026-07-21.md`.
- Verification: all 2,242 non-Qt tests pass with 295 expected skips and all
  2,242 real offscreen-Qt tests pass with one intentional skip. Test quality,
  docs, compilation, JSON, diff, asset normalization, dark-mode visual states,
  reachability, a fully restarted native Anki pass, and worktree safety pass.
  Native Anki showed one launcher and one menu, separate Utilities/Activities,
  and Phoenix Lair with its normalized quill icon on the paginated D&D page.
- Results: `status-updates/phoenix-lair-horizontal-results-2026-07-21.html`;
  mobile copy: `https://wpe44dlne5mx.postplan.dev`.

## Fish Flingers horizontal mechanic closure — 2026-07-21

- Implemented the complete six-review Fishing event with automatic
  50/75/100% tackle discovery, catch/weight rolls, stock rotation, big fish,
  public assists, terminal XP, tokens, medals, and completion credit.
- Added two tickets per answered-card day, a ten-ticket cap, atomic entry,
  explicit leave/forfeit, persistent activity ownership, schema-64 migration,
  cadence coverage, telemetry, whole-answer undo, and direct-action undo.
- Added the exact token formula, four medal channels, four-piece Fishing outfit,
  five cumulative-medal tackle-box upgrades, previous-box consumption, and the
  outfit's ordinary-Fishing plus event XP effects.
- Added nine normalized period reward sprites, the activity icon, reproducible
  provenance-aware fetching, item/equipment registration, asset-path coverage,
  and a compact no-nested-scroll card on the paginated D&D page.
- Opus's read-only taste pass found five concrete UI defects. Root reproduced
  and fixed the hidden disabled-purchase reason, weak state legibility,
  over-emphasized shop frame, ambiguous progress wording, and misleading fresh
  ticket-claim copy. Fable stayed reserved.
- The exact post-July-2012 XP equation and hidden event distributions remain
  clearly labeled data-depth work, not missing mechanics. No owner design gap
  emerged. See `source-audits/fish-flingers-loop-2026-07-17.md`.
- Verification: all 2,160 non-Qt tests pass with 283 expected skips and all
  2,160 real offscreen-Qt tests pass with one intentional skip. Test quality,
  docs, compilation, JSON, diff, normalized assets, reachability, a fully
  restarted native Anki dark-mode pass, and worktree safety pass. Reachability
  reports 1,438 actions, 2,128 reachable items, 168 known orphan inputs, and
  189 unresolved actions.
- Results: `status-updates/fish-flingers-horizontal-results-2026-07-21.html`;
  mobile copy: `https://t47kaw10p3pp.postplan.dev`.

## Gnome Ball horizontal mechanic closure — 2026-07-21

- Replaced the invented five-review Agility stub with the settled three-beat
  Activities match: goals `1–2`, goals `3–4`, then goal `5` and the completion
  bonus. Exact period XP awards `9`, `13`, and `30` to both Agility and Ranged.
- Added the period weapon-slot restriction, item `751` equipment identity,
  carried-only referee reward check, explicit entry/leave, persistent session
  arbitration, completion counters, telemetry, cadence stopping, schema-63
  migration, and atomic direct/review undo.
- Added one disclosed level-scaled tackle abstraction per beat. Survived tackles
  retain the score; lethal tackles award no beat XP and use the shared Auto or
  Custom food pack, LP, grave, equipment-loss, terminal-stop, and rollback
  channels.
- Added Activities-only registration, the normalized period Gnomeball sprite,
  a compact dark-safe card, visible READY/ACTIVE/LOCKED state, tackle risk and
  LP, switch/leave confirmation, and the existing four-page Activities pager.
- Opus's bounded taste pass drove theme-aware active state, concise danger and
  leave copy, visible prior results, and clearer action wording. Fable remained
  reserved; Kimi was not called after its live quota guard failed.
- Verification: all 2,146 non-Qt tests pass with 282 expected skips and all
  2,146 real offscreen-Qt tests pass with one intentional skip. Test quality,
  docs, compilation, JSON, diff, normalized assets, reachability, fully
  restarted native Anki, and worktree safety pass. Native Anki showed one menu,
  separate Utilities/Activities, the four-page pager, and Gnome Ball on the
  Minigames page. Reachability remains 1,438 actions, 2,128 reachable items,
  168 known orphan inputs, and 189 unresolved actions. No owner design gap
  emerged. See `source-audits/gnome-ball-loop-2026-07-17.md`.
- Results: `status-updates/gnome-ball-horizontal-results-2026-07-21.html`;
  mobile copy: `https://d1b1zg22hfo7.postplan.dev`.

## Pyramid Plunder horizontal mechanic closure — 2026-07-21

- Implemented the complete one-to-eight-room dangerous run with exact entry
  alternatives, room/Strength/Runecrafting gates, period object XP, exact
  artefact values, emulator object curves, rare rewards, and priority routes.
- Added shared Thieving LP damage, poison/antipoison, food, dangerous death and
  grave behavior without manufacturing Combat encounters or wall-clock state.
- Added Max XP, Balanced, and Treasure retention, real 28-slot carried pressure,
  direct protected rewards, terminal banking, Pharaoh-sceptre expulsion, and
  explicit leave. Foreground multiplication stops at terminal; Again does
  nothing.
- Added schema-61 persistence/session arbitration, runtime multi-skill XP,
  direct/review undo, cadence coverage, Activities-only registration, twenty
  reward sprites, a period activity icon, reproducible provenance-aware asset
  fetching, and a compact dark-safe card.
- Regenerated exact cutoff Grand Exchange guide prices and buy limits for the
  registered artefacts and Pharaoh's sceptres instead of leaving newly
  reachable tradeable rewards unresolved.
- Opus found and root reproduced/fixed failed entry changing the selected
  review activity. The same bounded taste pass drove clearer locked-state,
  status, priority, result, immunity, and leave-cost presentation. Fable stayed
  reserved under owner instruction; Kimi was unavailable at 4% quota.
- Exact unrecovered hazard rates and the absent Darkan golden-chest ordinary
  table remain clearly labeled data depth. No owner design gap emerged. See
  `source-audits/pyramid-plunder-horizontal-mvp-2026-07-21.md`.
- Verification: all 2,118 non-Qt tests pass with 275 expected skips and all
  2,118 real offscreen-Qt tests pass with one intentional skip. Test quality,
  docs, compilation, JSON, diff, normalized assets, focused reachability,
  fully restarted native Anki, and worktree-safety checks pass. Reachability
  reports 1,438 actions, 2,128 reachable items, 168 known orphan inputs, and
  189 unresolved actions.
- Results:
  `status-updates/pyramid-plunder-horizontal-mvp-results-2026-07-21.html`;
  mobile copy: `https://8tc4efyc7zls.postplan.dev`.

## Flash Powder Factory horizontal mechanic closure — 2026-07-21

- Implemented the complete finite factory session: exact entry gates, eight or
  nine answered-card slots, productive and Again-idle resolution, atomic
  completion/early exit, Brianpoint conversion, long-stay bonus, cap, and the
  proportionally translated published penalty curve.
- Added Max-points, Rogue-equipment, and Balanced route policies; catalyst,
  apparatus, residue, charge, obstacle delay, rubble, Rogue-piece rewards, and
  the sourced Factory outfit effects. Hidden server weights remain explicitly
  labeled data-depth abstractions.
- Added exact Agility/Thieving XP lots and Factory-piece prices plus stackable
  Rogue kits, all through instantaneous direct-action undo. Bank converts one
  kit to the chosen Chisel, Rope, Tinderbox, or Spade without a review.
- Integrated the three-piece four-dose Herblore chance and full-set unfinished
  potion XP, including period exclusions, Weapon poison special values, and
  Prayer-renewal stacking with Morytania legs 4.
- Added Activities-only registration, durable Activity Circuit completion,
  cadence coverage, normalized period assets and provenance, reachability,
  save repair, a compact paginated card, and real offscreen Qt coverage.
- Opus found and root reproduced/fixed cap-state apparatus loss, foreground
  multiplication, alternate-dispatch double loot, ignored switch rejection,
  pre-gate follower dismissal, status leakage, and potion-output telemetry.
  Fable stayed reserved under the owner's quota instruction.
- Verification: all 2,102 non-Qt tests pass with 272 expected skips and all
  2,102 real offscreen-Qt tests pass with one intentional skip. Test-quality,
  docs, compilation, JSON, diff, normalized assets, reachability, native Anki,
  and worktree-safety checks pass. No design gap emerged. See
  `source-audits/flash-powder-factory-horizontal-mvp-2026-07-21.md`.
- Results:
  `status-updates/flash-powder-factory-horizontal-mvp-results-2026-07-21.html`;
  mobile copy: `https://qo7av1788kwa.postplan.dev`.

## Barrows horizontal mechanic closure — 2026-07-21

- Implemented the complete dangerous Barrows run: the six original brothers,
  Ritual-gated Akrisae, six tunnel creatures, a persistent 3×3 graph with one
  locked perimeter door, one central approach, mound and tunnel combat,
  brother specials, early chest access, reward potential, and the ordinary
  reward ladder.
- Added Casual shortest-route/chest automation and Advanced mound/door choices.
  One successful review resolves the door plus its attached six-tick Combat
  beat; suspension preserves the exact run while death resets it.
- Registered one representative weapon for every brother as an independently
  degrading equipment instance. The 90,000-tick condition cycle,
  100/75/50/25/0 names, value aliases, combat degradation, unsafe-death state,
  and prorated Bob repair are live through Bank, Equipment, GE, persistence,
  and undo seams.
- Corrected the emulator's absolute-brother-index equipment-roll defect so an
  early chest gives exactly one eligible equipment roll per slain brother,
  independent of identity. Exit, chest, and death also restore the saved
  Combat target even when that target was empty.
- Opus's bounded final review found and closed the Advanced chest eligibility
  mismatch that could route a review into a manual-only action and deactivate
  training. Its run-energy concern was reconciled against the settled shared
  trip-credit abstraction; Torag now reports the actual credit removed and a
  truthful no-op at zero. Opus accepted the final slice.
- Added schema-60 persistence, cadence coverage, activity/item registration,
  cutoff GE prices and limits, reachability, seven weapon icons, one activity
  icon, reproducible fetch/render helpers, and the compact dark-safe Activities
  card with its complete always-visible 3×3 map and repair row.
- Native Anki proof used a full application restart and verified one launcher,
  one menu, Activities pagination, the visible Barrows row, enter/leave/resume,
  and the final READY state. Synthetic smoke state was removed through an exact
  field-scoped cleanup after Anki's own undo history was exhausted.
- Fable remained reserved under the owner's quota instruction. Kimi was not
  retried at 4% remaining quota; Opus supplied the external review lane.
- Verification: all 2,083 non-Qt tests pass with 269 expected skips and all
  2,083 real offscreen-Qt tests pass with one intentional skip. Hard
  test-quality, docs, compilation, JSON, diff, normalized assets,
  reachability, native Anki, and worktree safety pass. No design gap emerged.
  See `source-audits/barrows-horizontal-mvp-2026-07-21.md`.
- Results: `status-updates/barrows-horizontal-mvp-results-2026-07-21.html`;
  mobile copy: `https://xpd3hsr4ybb4.postplan.dev`.

## Stealing Creation horizontal mechanic closure — 2026-07-20

- Implemented one complete twenty-review safe match with five sacred-clay
  classes, exact gather/process/deposit scoring, a closed session inventory,
  temporary hatchet/scimitar/platebody/barrier, bounded opposing production,
  six-tick raiders, safe death, winner bonus and exact point conversion.
- Added Casual's complete loadout/deposit planner and Advanced duty, gathering
  route, class and kiln-recipe policy. Terminal flee/death/failure boundaries
  cannot wedge the session, and temporary Combat explicitly excludes outside
  supplies, effects, passive healing and XP.
- Added 20-point morphic and volatile tools with seven matching forms, 200% and
  220% total XP, bonus-XP charge budgets, level-40 volatile gating and random
  transformations at crossed 10% segments. Matching selected skill families
  are required, so lamps and side rewards do not spend charge.
- Added schema-59 persistence, sanitation, direct/review undo boundaries,
  item/activity registration, reachability, three normalized period assets and
  a reproducible provenance-aware fetch helper.
- Added the compact paginated Activities card, then fixed the contradiction
  found only in restarted native Anki where Casual mode displayed stale locked
  Advanced choices. The final real UI shows truthful automatic duty, route,
  class and kiln labels at 900x560 without clipping.
- Opus independently reviewed the full slice; every reproduced correctness and
  taste finding is fixed. Fable was deliberately reserved. One Kimi K3 call
  returned no response headers for roughly 25 minutes and was stopped without a
  quota-burning retry; no Kimi sign-off is claimed.
- Verification: all 2,057 non-Qt tests pass with 268 expected skips and all
  2,057 real offscreen-Qt tests pass with one intentional skip. Hard
  test-quality, docs, compilation, JSON, diff, assets, reachability, native
  Anki and worktree safety pass. No design gap emerged.
  See `source-audits/stealing-creation-horizontal-mvp-2026-07-20.md`.
- Results:
  `status-updates/stealing-creation-horizontal-mvp-results-2026-07-20.html`;
  mobile copy: `https://tougys8r35za.postplan.dev`.

## Fight Caves horizontal mechanic closure — 2026-07-20

- Implemented the exact persistent 63-wave Fight Cave with stable roster
  identities, one engaged six-tick Combat slice per successful review, Casual
  threat priority, Advanced target selection, and ordinary protection-prayer
  and Defence resolution for bounded unengaged pressure.
- Added Tz-Kih prayer drain, Tz-Kek melee recoil and split spawns, Yt-MejKot
  healing, Jad attack telegraphs and four healers, safe death, partial TokKul,
  explicit confirmed leave, and exact 16,064 TokKul plus Fire cape completion.
- Added the reusable sealed-activity constraints: one active session identity,
  follower dismissal confirmation, no mid-instance Bank trip, persistent
  resume, schema-58 migration, direct/review undo, and cadence coverage.
- Registered TokKul and Fire cape, including the cape's exact equipment stats
  and existing normalized period art. The acquisition path is included in the
  live reachability graph.
- Added the compact Activities card and Review HUD feedback. Kimi K3 and the
  completed Fable taste pass surfaced three reproducible risks; confirmed leave
  confirmation, Casual-display, and maximum-roster defects are fixed and
  regression-covered.
- Verification: all 2,040 non-Qt tests pass with 267 expected skips; all 2,040
  real offscreen-Qt tests pass with one intentional skip. A fully restarted
  native Anki process showed one menu and the unclipped READY card without
  entering the cave or changing gameplay state. Test quality, docs,
  compilation, JSON, diff, assets, reachability, and worktree safety pass. See
  `source-audits/fight-caves-horizontal-mvp-2026-07-20.md`.
- Results:
  `status-updates/fight-caves-horizontal-mvp-results-2026-07-20.html`; mobile
  copy: `https://4r52o2zq3kzv.postplan.dev`.

## Vinesweeper horizontal mechanic closure — 2026-07-20

- Implemented the complete review-driven field loop: Spade entry, familiar
  dismissal confirmation, ten free flags, bounded safe/correct/mistake/rabbit
  outcomes, Ogleroot discovery and consumption, coin/point flag refills,
  Hunter defence XP, direct leave/refund, multiplier batching, persistence,
  cadence declaration, and both undo boundaries.
- Added the literal 46-row cutoff Mrs Winkin shop with direct Farming-XP
  redemption. The interface correctly excludes Fellstalk and Morchella.
- Closed the Compost potion seam exposed by the shop: all four cache-identified
  doses, normalized period art, dose preservation, Compost-to-Supercompost
  Utility action, Vial return, and cutoff Grand Exchange prices/buy limits are
  live and reachable.
- Added the Vinesweeper card and Review HUD feedback, then changed Activities
  to an explicit master/detail flow so the paginated category catalog and rich
  cards never compete for vertical space. `Choose another activity` returns to
  the catalog, while keyboard browsing and page navigation stay in it.
- Kimi K3 and Fable independently reviewed the card. Confirmed price,
  hierarchy, clipping, accessibility, pause-reason, numeric-copy, and
  keyboard-navigation defects were fixed and regression-covered.
- No owner design gap surfaced. Exact hidden field-outcome rates remain labeled
  data-depth debt rather than missing mechanics. See
  `source-audits/vinesweeper-loop-2026-07-18.md`.
- Verification: all 2,024 non-Qt tests pass with 266 expected environment
  skips, and all 2,024 real offscreen-Qt tests pass with one intentional skip.
  The restarted native Anki process shows one launcher, one menu, the paginated
  Minigames catalog, and the unclipped Vinesweeper card without save mutation.
  Results:
  `status-updates/vinesweeper-horizontal-mvp-results-2026-07-20.html`; mobile
  copy: `https://21nc8cd2r6ok.postplan.dev`.

## Sorceress's Garden horizontal mechanic closure — 2026-07-20

- Implemented all four seasonal gardens with exact Thieving gates, fruit
  thresholds, Farming XP, Osman XP, and juice effects.
- Added the settled Fruit / Herbs / Alternate harvest policy and Osman / Keep
  completed-juice policy. Automatic squeezing preserves real fruit and juice
  inventory while treating the free beer glass and tool-belt pestle as ambient
  setup.
- Added the Diamond in the Rough entry gate and one-time introduction, review
  and direct undo, schema-55 migration, cadence coverage, HUD feedback, and a
  complete dark-mode-safe Activities card.
- Registered eight fruit/juice items, four consumables, nine normalized period
  assets with provenance, and a reproducible asset-fetch helper. Dungeoneering
  herbs remain excluded.
- Replaced the crowded Activities scroll with a one-category pager that
  preserves selection, measures content height, exposes accessible navigation,
  and leaves Utilities untouched.
- Kimi K3 and Fable independently reviewed both the Garden card and pager. All
  confirmed hierarchy, selection, clipping, false-disclosure, tradeoff-copy,
  and accessibility findings were fixed.
- Verification: 1,998 full non-Qt tests pass with 264 expected skips; the full
  offscreen-Qt universe passes 1,996 tests with one intentional skip, and the
  final delta passes nine focused real-Qt tests. A fully restarted native Anki
  process confirms one menu, the unclipped pager, and the disabled Garden row.
- Reachability now models the Garden as a producer: 1,433 actions, 2,099
  reachable items, 168 orphan inputs, and 189 unresolved actions. See
  `source-audits/sorceress-garden-loop-2026-07-18.md`.
- Results:
  `status-updates/sorceress-garden-horizontal-mvp-results-2026-07-20.html`;
  mobile copy: `https://mo77ybvazx38.postplan.dev`.

## Fist of Guthix horizontal mechanic closure — 2026-07-20

- Implemented the complete two-round safe PvP abstraction: Fiara tutorial,
  automatic random pairing, persistent opponent, randomized role order, role
  swap/restoration, exact six-tick reviews, authentic charge endpoints, and
  direct Tele-orb/forfeit controls.
- Added temporary arena-owned Bandages, generic Elemental/Catalytic runes,
  Stone of power, and Tele-orb. Consumption remains isolated from the Bank;
  all Combat XP channels are halved after the shared reducer.
- Persisted stance policy, exact charge residuals, rating, tokens, forfeit
  carryover, record, and bounded history under storage schema 54. Review and
  direct mutations use their established independent undo paths.
- Added the generic per-copy condition substrate and exercised it through
  Combat hood and Bronze gauntlets across equipment, Bank, unsafe/safe death,
  recharge, manual uncharge, migration, and undo. Corrected the hood to 10
  Defence / 20 Magic and made only its fully spent identity tradeable.
- Added a compact one-page Activities surface and live Review HUD scoreline.
  Kimi K3 and Fable shaped the stable status/charge/shop hierarchy; native Anki
  and focused offscreen Qt both verified the accepted result.
- Added three normalized provenance-tracked sprites, explicit cadence coverage,
  and match -> token -> purchase -> condition reachability. The graph reports
  1,428 actions, 2,091 reachable items, 168 orphan inputs, and 189 unresolved
  actions.
- Verification: 350 focused pure/runtime/storage/integration/registry tests,
  focused real Qt, 1,988 full non-Qt tests (262 expected skips), and 1,988 full
  offscreen-Qt tests (one intentional skip) pass. Test quality, docs,
  compilation, JSON, diff, asset normalization, and worktree safety also pass.
  See
  `source-audits/fist-of-guthix-horizontal-mvp-harvest-2026-07-20.md`.

## Shooting Stars horizontal mechanic closure — 2026-07-20

- Completed the follow-up navigation and activity-category audit: green
  compass is Achievement-only; D&D and Minigame headings use yellow and red
  compasses; Familiarisation and Big Chinchompa are D&Ds; Livid Farm remains a
  Minigame; Familiarisation now runs from its own Activities card rather than
  Equipment.
- Replaced the Bond-like Shop orb and bordered Summoning badge with period
  coin art and a clean frameless glyph. Skills now uses a period Max cape while
  Stats keeps the bar graph, preserving unique global-tab meanings.
- Replaced the remaining mixed skill art with one period highscores family for
  all 25 skills across Stats, Training, and Combat XP rows. Every source sprite
  is pinned to a pre-cutoff revision, provenance-recorded, tight-cropped, and
  rendered with one normalized pixel-art policy.
- Rebuilt Stats as the period three-column scan order in a compact left
  selector, added Dungeoneering, total level, and live `current / base`
  projection for temporary boosts/drains, and bounded the selected metrics at
  wide window sizes. Native Anki reproduced the finished grid and also closed
  the macOS branch-cell selection-color mismatch.
- Added dedicated spellbook art for all 114 Magic targets. Authentic shared
  spell families reuse one glyph across their output variants; 105 targets
  have cutoff-pinned files and nine exact visual fallbacks are labeled
  honestly in provenance. Removed the synthetic white/neutral circles from
  Combat targets, Combat XP rows, Shooting Stars, and other transparent art.
- Normalized every skill, Utility, and Activity target row through the same
  crisp DPR-aware 28-pixel scaler and 32-pixel row rhythm; hand-injected
  Landmark rows no longer bypass that policy.
- Implemented the complete settled world-event graph with all nine sourced
  layers, communal crowd depletion, first-finder tags, level waiting,
  persistent Stardust, daily manual sprite exchange, gems, and a live
  1,500-tick extra-ore reward.
- Added Casual and Advanced policies, shared world-population logic, versioned
  state migration, review/direct-action undo, cadence declarations, Review HUD
  notices, and ordinary Mining bonus integration without using wall time.
- Replaced the crowded Activities dashboard scroll with a selected
  `QStackedWidget` page. Group headers clear stale pages, live text refits page
  height, and Utilities remains a separate surface.
- Added period Star sprite and Stardust art, normalized the wider global
  navigation vocabulary, and replaced the later detailed RS3 Combat render
  with the compact legacy OSRS glyph.
- Added deterministic reachability edges for mining Stardust and exchanging
  it. The graph reports 1,415 actions, 2,082 reachable items, 168 orphan
  inputs, and 189 unresolved actions.
- Kimi K3's earlier UI passes found four concrete defects and all four are
  fixed. Kimi and Fable both returned `SHIP` for the final Magic
  spell-icon/direct-transparency delta. A fresh native-Anki restart verified
  one menu, the real dark-theme icons, and the compact Activities picker.
- The exact final state passes all 1,961 non-Qt tests with 260 expected skips
  and all 1,961 real offscreen-Qt tests with one intentional skip.
  Documentation, test quality, compilation, diff, asset, JSON, reachability,
  and worktree-safety gates pass.
- Durable record:
  `source-audits/shooting-star-implementation-harvest-2026-07-20.md`.
  Navigation record:
  `source-audits/navigation-and-activity-icon-audit-2026-07-20.md`.
- Results:
  `status-updates/shooting-stars-horizontal-mvp-results-2026-07-20.html`;
  mobile copy: `https://uhov58kni1bj.postplan.dev`.

## Woodcutting Split log processing — 2026-07-20

- Added the settled level-54 `Split Arctic pine logs` processing target: one
  carried Arctic pine log becomes one Split log for 42.5 Woodcutting XP.
- Kept the action distinct from chopping: no hatchet, nest, Inferno-adze,
  log-counter, or urn behavior.
- Added processing-aware carried-pack semantics, atomic Bank reconciliation,
  target metadata, telemetry, period art/provenance, and a generic
  `quest_started` unlock requirement used by both splitting and Arctic-pine
  Firemaking.
- Registered non-stackable tradeable Split log ID `10812`, plus its cutoff
  30-coin guide price and 1,000-item buy limit from Exchange oldid `6563176`.
- Preserved the explicit source boundary: Arctic-pine chopping still waits on
  success, depletion, and respawn evidence, so Arctic pine logs remain a
  truthful root orphan rather than receiving invented odds.
- Kimi K3 approved the row hierarchy and period icon weight after three small
  copy/tooltip corrections. The final screenshot also confirms that Utilities
  and Activities remain separate categories. Fable's required taste pass is
  externally blocked by the fresh quota probe's macOS Keychain failure
  (`security` exit 51), not by a design gap.
- The complete non-Qt and real offscreen-Qt universes each pass all 1,936
  tests (252 expected environment skips and one intentional skip
  respectively); focused coverage passes 195 tests plus the real-Qt row and
  both global asset checks. Documentation, test quality, compilation, JSON,
  diff, reachability, and worktree-safety audits pass.
- Durable record:
  `source-audits/woodcutting-split-log-implementation-2026-07-20.md`.
- Results:
  `status-updates/woodcutting-split-log-results-2026-07-20.html`; mobile copy:
  `https://g5v7ucswdk1k.postplan.dev`.

## Potion flask acquisition and no-XP surface split — 2026-07-20

- Added the authentic `As a First Resort...` chain: level-81/70-XP Red
  sandstone with Darkan's `30/145` endpoints and a 50-success review-day cap;
  free no-XP one-for-one Robust glass conversion; and
  level-89/100-XP Potion flask glassblowing with a held pipe.
- Added exact item IDs `23194`, `23193`, and `23191`, tradeability and
  non-stackable metadata, storage schema 51, successful-output-only cap
  accounting, quest gates, tooltips, reachability, normalized art, provenance,
  and focused cross-layer tests.
- Split the old combined no-XP hub into distinct Utilities and Activities
  categories while retaining the shared atomic handler, target key, telemetry,
  and undo path. Every data row has exactly one surface; special events and
  landmarks remain Activities-only; legacy active-skill saves normalize from
  the selected target.
- Added distinct surface sprites, separate copy and start actions, a bounded
  labeled event-status viewport, guaranteed picker height, a picker-local
  prompt, and consistent current-target highlighting.
- Kimi K3's six findings were corrected and its final dark/light review reports
  no remaining P0-P2 defect. The required Fable review remains externally
  blocked by the fresh quota probe's macOS Keychain failure (`security` exit
  51); no owner design gap surfaced.
- Focused checks pass 212 non-Qt and 29 offscreen-Qt tests. Both complete test
  universes execute 1,928 methods; the final hub module passes all 247 methods,
  plus three post-review targeted tests. Test quality, docs, compilation, diff,
  asset normalization, reachability, and worktree safety pass.
- Reachability now reports 1,412 actions, 2,081 reachable items, 168 orphan
  inputs (76 root and 92 cascade), and 188 unresolved actions. Red sandstone,
  Robust glass, and Potion flask each have an authentic producer route.
- Durable record:
  `source-audits/potion-flask-acquisition-2026-07-20.md`.
- Results:
  `status-updates/potion-flask-acquisition-and-surface-split-results-2026-07-20.html`;
  mobile copy: `https://56ivo4cbqqvn.postplan.dev`.

## Teplin potion-flask decanting — 2026-07-20

- Added the period Oo'glog NPC service after `As a First Resort...`: Teplin
  fills new six-dose potion flasks and decants eligible partial flasks back
  into four-dose vials plus an exact remainder.
- Preserved dose and container conservation, excluded five-/six-dose source
  flasks, returned emptied Vials, destroyed emptied flasks, and kept both
  actions instantaneous, inventory-wide, free, and directly undoable without
  advancing any gameplay clock.
- Added canonical registry art and provenance for all 151 registered
  potion-container states. The 135 newly checked-in PNGs and all 256
  Herblore item sprites pass the shared tight-alpha normalizer.
- Added source-generated service rows, quest-aware preview/application,
  deterministic reachability edges, focused pure/integration/Qt coverage, and
  native restarted-Anki proof.
- Kimi K3 found and closed seven concrete UI defects covering preview
  completeness, pluralization, icon identity, list geometry, free pricing,
  completion copy, and denial copy. The mandatory Fable pass remains
  externally blocked by the fresh quota probe's macOS Keychain failure
  (`security` exit 51); no owner design gap surfaced.
- Focused checks pass 57 non-Qt tests and one real-Qt interaction test.
  Complete non-Qt discovery executes all 1,918 methods with 251 expected
  environment skips; complete real offscreen Qt executes all 1,918 methods
  with one intentional skip. Documentation, test-quality, compilation, JSON,
  diff, normalization, reachability, and worktree-safety checks pass.
- Reachability now reports 1,409 actions, 2,012 reachable items, 235 orphan
  inputs (76 root and 159 cascade), and 276 blocked actions. Empty Potion
  flask acquisition remains the next authentic root dependency.
- Durable record:
  `source-audits/teplin-potion-flask-decanting-2026-07-20.md`.
- Results:
  `status-updates/teplin-potion-flask-decanting-results-2026-07-20.html`;
  mobile copy: `https://uryuvjirpis2.postplan.dev`.

## Farming reachability routes — 2026-07-20

- Added the existing runnable Farming sapling, harvest, and tree-root paths to
  the quantity-free item-acquisition graph.
- Removed false root-orphan reports for live produce without changing Farming
  gameplay or manufacturing fake seed/tool sources.
- Reachability improves from 1,268 actions / 1,889 reachable items / 284
  orphans / 302 blocked actions to 1,342 / 1,982 / 253 / 268.
- Focused regression coverage passes and pins representative allotment, bush,
  mushroom, fruit-tree, sapling, and root routes.
- Durable record:
  `source-audits/item-reachability-farming-routes-2026-07-20.md`.

## Easy Treasure Trails source boundary — 2026-07-19

- Pinned the one-to-five easy trail length, simple/emote/map/cryptic families,
  no-coordinate/no-combat/no-Wilderness rules, reward membership, and clue,
  casket, and scroll-box client identities.
- Rejected Darkan's conflicting one-to-three step roll.
- Stopped implementation because the settled per-tier ownership clause
  conflicts with the period global one-clue rule and because exact clue and
  reward selection rolls lack independent pre-EOC-lineage corroboration.
- Recorded the recommended period-faithful ownership resolution in
  `design-gaps-implementation-2026-07-19.md`; no product code was changed.
- Durable source record:
  `source-audits/treasure-trails-easy-source-boundary-2026-07-19.md`.

## Big Chinchompa D&D implementation — 2026-07-19

- Implemented both owner-settled event windows on the shared 240-review world
  day, with six source minutes per review, twenty source minutes of maximum
  availability, late entry, and communal early completion.
- Added all eight exact moth tiers, fifteen-moth jar circuits, the 1,500
  personal point cap, continued Hunter XP after that cap, one-for-one
  Competence conversion, and the exact 20,000-point wallet cap.
- Added the complete period reward shop, direct 5-XP-per-point purchase,
  quiet/normal/busy seeded crowd profiles, storage schema 50, telemetry, and
  atomic review/direct undo.
- Added five quota-ticket items and initially four executable private-ground
  routes. Tickets must be carried for the selected Hunter target and are
  consumed only after a successful catch. The fifth, Polar kebbit, became
  executable in the 2026-08-12 acquisition slice above.
- Added provenance-pinned period art, standard 28-pixel display boxes, a global
  Review HUD notice, a compact scroll-safe Utility card, and the contextual
  Hunter private-ground control. Fable's independent review caught and closed
  progress-text, wallet, disabled-toggle, hierarchy, copy, and laptop-height
  problems. The first Kimi K3 call was rejected with a provider-overload 429
  and was retried rather than treated as evidence; the completed retry caught
  and closed stale sibling-card state, disabled-buy guidance, carried-ticket
  consistency, renderer ordering, and dark period-icon legibility.
- Focused pure/runtime/integration verification passes 282 tests. The complete
  non-Qt runner executes 1,874 methods with 243 expected environment skips.
  Complete real offscreen Qt executes all 1,874 methods with one intentional
  skip. A fully restarted native Anki process opened exactly one menu and
  verified the dark-mode card and scroll behavior without changing the save
  before the last reviewer polish. The final native recheck was unavailable
  because the Mac was locked; focused Qt and a fresh final render verify the
  accepted tooltip, sibling-refresh, carried-ticket, and icon changes.
- The final diff audit caught and fixed a review-boundary error before closure:
  the twenty-source-minute window now exposes exactly three complete
  six-minute review opportunities, never a fourth action that would finish
  after the event ends.
- No owner-facing design gap emerged. Durable implementation record:
  `source-audits/big-chinchompa-implementation-harvest-2026-07-19.md`.

## Evil Tree D&D implementation — 2026-07-19

- Implemented the owner-settled three-review Nurture → Prepare → Fell event
  on the shared answered-card clock, including a five-review active window,
  two interactions per 240-review day, and nurture-only participation.
- Pinned all seven period tier gates and XP rows. Unrecovered tier/reward/nest
  formulas use the explicitly disclosed bounded abstractions in the source
  audit rather than fabricated parity claims.
- Added versioned storage, exact cross-skill XP, kindling, bounded rewards,
  telemetry, atomic review undo, a compact Utility card, global review-HUD
  notices, normalized art/provenance, and a repeatable Qt renderer.
- Added the post-event Woodcutting blessing: one non-chaining ordinary
  continuation, doubled nest chance, and eligible full-pack overflow banking
  without spending a review on a fake Bank trip.
- Fixed two cross-layer defects caught by the new tests: an overflow gate
  accidentally placed in Agility pack construction and world-state mutation
  occurring after review-snapshot finalization.
- Fable's independent UI pass caught and closed light-theme status contrast,
  stale inactive-HUD wording, state hierarchy, and target-selection sync
  defects. Kimi K3 independently confirmed those findings and caught the
  remaining `today` wording, which now says `this review day`.
- Focused pure/runtime/integration verification passes 287 tests. The complete
  non-Qt runner passes 1,853 methods with 239 expected environment skips, and
  complete real offscreen Qt passes all 1,853 methods with one intentional
  skip. Repository results are recorded in
  `source-audits/evil-tree-implementation-harvest-2026-07-19.md`.
- A fully restarted native Anki process opened exactly one menu and rendered
  the final dark-mode Evil Tree card with `Next review`, the normalized
  kindling art, and `this review day`; it closed without selecting an activity
  or changing the save.
- No owner-facing design gap emerged.

## Skeletal Horror breadth-one implementation — 2026-07-25

- Shipped the complete recurring-boss graph through the existing Activities,
  Combat, cadence, persistence, and direct-action undo seams.
- Added both post-quest wish-list gates, Slayer 78, the 1,680-card entry cost,
  weekly recurrence, all continuous phase and limb transitions, sourced
  attack-style changes, and safe-death recovery.
- Added the exact first-kill and repeat Slayer/Prayer rewards and the
  one-in-twenty elite clue.
- Added normalized period Skeletal Horror and elite clue art with provenance,
  plus a compact dark-mode D&D card and offscreen Qt coverage at 900 by 560.
- Registered six breadth-phase placeholders for the four missing phase stat
  blocks, shared bonuses, and Melee/Magic style probability.
- Source contract:
  `source-audits/skeletal-horror-implementation-harvest-2026-07-19.md`.

### Adversarial verification — 2026-07-26

The entry above was written before the family was verified, and three of its
claims were wrong. Corrected here rather than in place, so the two can be
compared:

- **"weekly recurrence with two-bank carryover" was an invention.** Both source
  audits say repeat availability *resets* each simulated week. Banking two
  entries is a mechanic the period did not have. `SKELETAL_HORROR_ENTRY_CAP` is
  now `1` and the test that pinned the banking was corrected toward the source.
- **"tests that reach every reward through the real review path" was not true.**
  Every mechanics test mocked `apply_combat_burst_pure`, so nothing proved the
  fight worked at all. `SkeletalHorrorRealCombatPathTests` now drives the real
  kernel from a fresh save to victory, to a repeat victory with the elite clue,
  and to a real death.
- **"No owner-only design fork emerged" was wrong.** The post-quest wish lists
  are satisfied by a free button press; that is now design-thread queue 3.1.

Also fixed: the panel re-derived the Slayer-78 gate itself instead of reading
the view, and the phase thresholds were restated in the logic layer instead of
being read from the phase table.

## Borrowed Power and Arcane capacitor — 2026-07-19

- Implemented the complete cutoff capacitor lifecycle: one-owned wish,
  Magic-99 loading, exact 1,000-cast native rune cost without staff
  substitution, one spell binding, 1,000 charges, exact remainder refund,
  +10 Magic attack equipment, and crumble on removal or final use.
- Added all twelve period-supported Borrowed Power routes. Four noncombat
  wrappers preserve native actions, XP, and gates; eight Combat spells are
  one explicitly armed manual cast and return to ordinary autocast.
- Added two compact player surfaces, direct-action/review undo coverage,
  normalized cutoff assets and provenance, generated equipment rows, and
  cross-storage ownership enforcement.
- Focused affected verification passes 553 pure/runtime/integration tests and
  focused real offscreen Qt behavior. The full non-Qt run executes 1,830
  methods with 235 expected environment skips; complete real offscreen Qt
  executes all 1,830 methods with one intentional skip.
- Kimi K3 and Fable independently reviewed every new Borrowed Power and
  capacitor surface. Confirmed laptop hierarchy, live-refresh, destructive
  confirmation, disabled-state, naming, and status-copy defects were fixed.
- Durable implementation record:
  `source-audits/borrowed-power-arcane-capacitor-implementation-2026-07-19.md`.

## Livid Farm Farming-owned wishes — 2026-07-19

- Added the hidden-by-default 53rd Farming patch. It uses the ordinary Farming
  plan and queue systems, identifies itself as one-use, and disappears after
  the first successful harvest or explicit clear while refunding stale prepaid
  gardener work.
- Added the canonical Patch protection scroll item and contextual action. One
  scroll protects the current ordinary tree or fruit tree plus the next nine
  matching plantings; other crops and prepaid gardener protection do not spend
  a use.
- Storage v48 sanitizes the patch flag, selected crop, and remaining uses.
  Assets, provenance, registry reachability, direct undo, and review undo
  remain within the existing Farming/Livid contracts.
- Fable and Kimi K3 independently reviewed the wide and laptop surfaces.
  Confirmed discoverability, naming, copy, alignment, and geometry issues were
  fixed; no owner-design decision was needed.
- Durable implementation record:
  `source-audits/livid-farm-farming-wishes-implementation-2026-07-19.md`.

## Livid Farm source-ready wishes — 2026-07-19

- Added the five value-complete direct wishes: Vial My Herbs, exact-residual
  Lunar lumber conversion, More Planks, Gimme Herbs, and Awesome Seeds.
- Kept source-blocked and dependency-owned rows visible and honest without
  inventing seed quantities, fish-burn magnitude, capacitor behavior, or
  Farming substrates.
- Added shared direct-action undo, Again-sensitive answered-card duration,
  storage v47 migration/sanitization, ordinary Plank Make integration, and a
  repaired capstone/unlock-ladder invariant.
- Fable and Kimi K3 independently reviewed the compact reward surface. The
  accepted copy, hierarchy, disabled-row, terminal-progress, countdown, and
  laptop-geometry issues were fixed.
- Final verification passes 269 focused cross-layer tests, 1,802 non-Qt tests
  with 229 expected environment skips, and 1,802 real offscreen Qt tests with
  one intentional skip. Documentation, test quality, compilation, diff,
  reachability, and guarded-worktree audits pass; native Anki also opened one
  live menu after a full process restart without modifying the locked user
  save.
- Durable implementation record:
  `source-audits/livid-farm-wishes-implementation-2026-07-19.md`.

## Thieving NPC target portraits — 2026-07-19

- Replaced representative loot/Coins icons with dedicated historical NPC art
  for all 17 pickpockets, Menaphite thug, and the locked Lletya elf.
- Kept stalls and safes on their existing object/output imagery, so the override
  remains semantic rather than global.
- Added a repeatable cutoff-aware manifest and full provenance for all 19
  portraits. The 2006 Watchman and 2010 Iorwerth files are explicit
  historical-title exceptions and infer no gameplay.
- Kimi K3 and Fable both caught the first tiny Watchman interface token; the
  root replaced it with the matching full-body historical model.
- Added pure asset-completeness, live Qt override, and shared alpha-normalization
  regressions. The actual macOS Anki process was fully restarted and the
  native panel confirmed the portraits after the stale pre-restart Coins view
  was eliminated. The pure suite passes 1,775 tests; focused asset/metadata and
  Qt coverage pass 68 and 2 tests respectively; the complete offscreen Qt suite
  also passes all 1,775 tests. No design gap emerged.

## The Pit and reviewer-context first slice — 2026-07-19

- Restricted Talent Scout invitations to the sourced nine-course set and added
  the one default-on global setting, manual familiar confirmation, safe
  weapon/shield stow, origin persistence, and origin return.
- Corrected the first-Gorilla-mask transition so later successful challenges do
  not duplicate the unique reward.
- Added the generic persisted reviewer-context projection and shared one-row
  action strip. Pit `Take XP / Gamble` now supports a conservative default,
  remembered explicit choice, one-answer grace period, direct undo, review
  undo, and RNG restore without duplicate permanent command buttons.
- Storage config version 45 sanitizes context-family preferences. Kimi K3 and
  Fable independently reviewed both new surfaces; confirmed defects were fixed
  before closure.
- Exact practice-route and remaining Pit table values stay `source_blocked`;
  no owner-facing design question remains.

## Slayer Warped-terrorbird source/authority boundary — 2026-07-19

- Pinned the ordinary level-81 and quest level-143 identities, Slayer 56,
  1,549 LP/154 XP, approximate 140 and exact 210 maxima, Melee/Ranged
  double-hit behavior, three morphology weaknesses, ear-protection cap,
  carried Crystal-chime gate, guaranteed Bones, and visible loot set.
- Stopped before implementation because the cutoff says The Path of Glouphrie
  need only be started before assignment, while current `required_quest_id`
  semantics require completion. No stage predicate was inferred.
- Kept the target source-blocked because both Darkan rows are `nostats`, the
  level-143 maximum conflicts at 140, and its 19,999/20,000 selector conflicts
  with most cutoff quantity ranges and omits visible content.
- Kept the target representation/dependency-blocked because fixed-style Combat
  cannot preserve the mixed attack/morphology loop and Crystal chime is not a
  reachable item dependency.
- Read-only Workflows run `2c6d91c5-c38c-4fa9-aea1-016e2cfbc5d5` was canceled
  without using a leaf result. It acquired a global slot but never established
  a Codex session or emitted a tool call; the root independently reproduced
  every accepted finding.
- Duradel/Lapalok remains hidden and unrenormalized at 14/35. This is an
  authority/schema stop rather than a new creative-design question. Durable
  records: `source-audits/slayer-warped-terrorbird-combat-2026-07-19.md` and
  `audits/slayer-warped-terrorbird-gate-conflict-2026-07-19.md`.

## Slayer Gorak source boundary — 2026-07-19

- Closed the level-145 Fairy-ring and level-149 God-Wars identities, 40–80
  count, Fairy Tale II completion assignment gate, 1,120/1,280 LP,
  140/165 maxima, typeless prayer bypass, random landed-hit stat drain, Stab
  weakness, guaranteed Big bones, visible loot contents, and no-charm rule.
- Encoded the independently source-closed
  `a_fairy_tale_ii_cure_a_queen` family gate and added a focused registry
  assertion. This supersedes only the older pool audit's source-blocked quest
  predicate, not the settled family or context contract.
- Kept both targets source-blocked because Darkan's level-149 row copies the
  level-145 LP/maximum, its ordinary selector omits Gorak claws and other
  period rows, adds Bones, and turns five exact Coin quantities into a
  continuous range. The cutoff cadence statements conflict and “at least one”
  does not close the exact drain magnitude.
- Kept both targets representation- and context-blocked because current Combat
  has no target-native prayer-bypassing landed-hit random-stat transaction and
  neither settled location route is player-selectable/atomic.
- Duradel/Lapalok remains hidden and unrenormalized at 14/35. No owner-facing
  design gap emerged. Durable evidence:
  `source-audits/slayer-gorak-combat-2026-07-19.md`.

## Slayer Ganodermic-creatures source boundary — 2026-07-19

- Closed the runt/beast identities, Slayer-95/Magic-60 gates, LP, XP, Magic
  attacks, maxima, fungal hazards, neem interaction, guaranteed drops, visible
  drop sets, cache forms/defences, and Polypore context.
- Kept both targets source-blocked because their Darkan rows are explicitly
  `nostats` and generate non-real combat levels.
- Kept the runt source-blocked because no Darkan ordinary-drop file exists.
  Kept the beast source-blocked because its 256-slot selector conflicts on
  runes, flakes, and noted ranarr, and its 15–28 LP fungal hazard conflicts
  with the cutoff 12–27.
- Kept both targets dependency-blocked because Darkan's neem form continues
  attacking instead of preserving cutoff suppression, while the canonical
  Neem-oil/resource/context chain is absent from AnkiScape.
- Duradel/Lapalok remains hidden and unrenormalized at 14/35. No owner-facing
  design gap emerged. Durable evidence:
  `source-audits/slayer-ganodermic-creatures-combat-2026-07-19.md`.

## Slayer Dark beast source boundary — 2026-07-19

- Closed the ordinary level-182 target's 2,200 LP, Slayer-90 gate/225.4 XP,
  six-tick conditional Melee/Magic identity, 174/80-LP maxima, real combat
  levels, exact cache defences, 59-tick respawn, Slash/Stab weakness, and
  guaranteed Big bones.
- Kept the target source-blocked because Darkan's ordinary selector conflicts
  with cutoff Coins, rune, herb, equipment, and Dark-bow rows. Its charm
  selector produces about 8% Blue against the cutoff's direct 14%.
- Kept the target representation-blocked because Darkan stores fixed Melee
  with zero maximum and current Combat cannot preserve the sourced
  Magic-opener/Melee-close transaction with distinct maxima.
- Kept the family context-blocked on the already-recorded global-schema
  conflict between Duradel's Temple-of-Light route and Kuradal's task-only
  Dungeon variant.
- Workflows run `d517a204-c3e0-44c6-b9d3-3882d1ce77cf` was canceled without
  using a leaf result. The worker held a global slot for five minutes with a
  live provider process but never established a Codex session or emitted a
  tool/progress event; the root independently reproduced every accepted
  finding.
- Duradel/Lapalok remains hidden and unrenormalized at 14/35. No owner-facing
  design gap emerged. Durable evidence:
  `source-audits/slayer-dark-beast-combat-2026-07-19.md`.

## Slayer Waterfiend source boundary — 2026-07-19

- Closed the ordinary level-115 target's 1,260 LP, 128 Slayer XP, six-tick
  Magic/magical-Ranged identity, 119-LP maximum, real combat levels, exact
  cache defences, 59-tick respawn, Crush weakness, and guaranteed Water rune.
- Kept the target source-blocked because Darkan's exact 128-slot ordinary
  selector conflicts with the cutoff Coins, rune, herb, fish, ore/bar, and
  other quantities. Its name-wide Coal row also leaks Ghorrock-only content.
- Kept the target context-blocked because the settled Ancient
  Cavern/Chaos-Tunnels/Ghorrock distinction has no player-selectable runtime
  transaction. A metadata-only flag would falsely satisfy readiness.
- Preserved the level-134 Ghorrock form as separately named implementation
  debt under Slayer Owner decision 20 rather than folding its quantity-two
  charms or location-only drops into the ordinary target.
- Duradel/Lapalok remains hidden and unrenormalized at 14/35. No owner-facing
  design gap emerged. Durable evidence:
  `source-audits/slayer-waterfiend-combat-2026-07-19.md`.

## Slayer Skeletal Wyvern source boundary — 2026-07-19

- Closed the level-198/2,000-LP identity, Slayer-72 gate/210 XP, six-tick
  Melee/Ranged/ice-breath family, 139 ordinary maximum, shielded 150 and
  unshielded 500+ breath envelopes, real combat levels, cache defences,
  respawn, guaranteed Wyvern bones, and broad drop selector.
- Kept the target source-blocked because the breath probability and freeze
  duration did not survive, while Darkan implements only fixed melee and no
  distinctive Wyvern handler.
- Kept the target dependency-blocked because none of the period-valid
  Elemental/Mind/Body/Cosmic/Chaos/Dragonfire shields is live equippable
  equipment. The Elemental Workshop I reward is only a generated item; the
  equipped Anti-dragon shield is explicitly invalid.
- Left nested herb/seed leaves and Darkan-only dragon leg/skirt tertiaries
  uncommitted pending period reconciliation.
- Duradel/Lapalok remains hidden and unrenormalized at 14/35. No
  owner-facing design gap emerged. Durable evidence:
  `source-audits/slayer-skeletal-wyvern-combat-2026-07-19.md`.

## Slayer Mithril dragon source boundary — 2026-07-19

- Pinned the cutoff level-304 target, 2,540 LP, 273 Slayer XP, six-tick
  Melee/Magic/Ranged/dragonfire identity, 289/182/182 maxima, Ancient
  Cavern/Barbarian-training gate, guaranteed Dragon bones/Mithril bars ×3,
  named drop set, and four-charm quantity.
- Closed the real 268/268/268/168/168 combat levels, exact cache defences, and
  59-tick respawn while rejecting Darkan's conflicting 2,550 LP and
  250-LP Ranged/Magic maxima.
- Kept the target source-blocked because Darkan's 127-slot ordinary selector
  narrows Runite-bolt, Rune-knife, and Rune-arrow quantities and omits several
  cutoff rows.
- Kept the target representation-blocked because the current fixed-style
  Combat schema cannot encode the settled multi-style selector or enforce the
  Ancient Cavern/Barbarian-training route.
- Workflows run `5a0150f7-23ba-4b6e-a030-db1d9e1bfd89` was canceled without
  using a leaf result. Despite two free global slots, the job remained
  `pending` with attempts `0`, no queue or slot assignment, no session, and
  zero tool/progress telemetry. This is a distinct post-start scheduler
  failure signature; the root independently reproduced every accepted
  finding.
- Duradel/Lapalok remains hidden and unrenormalized at 14/35. No
  owner-facing design gap emerged. Durable evidence:
  `source-audits/slayer-mithril-dragon-combat-2026-07-19.md`.

## Slayer Suqah source boundary — 2026-07-19

- Closed the settled single target as the cutoff southern melee-only Suqah,
  explicitly identified by the period article as the common Slayer-task form.
- Pinned level 111, 1,050 LP, 107.6 Slayer XP, six-tick attacks, the direct
  109-LP period maximum, complete real combat levels, cache defences, 29-tick
  respawn, guaranteed Big bones/Suqah hide, and tertiary leads.
- Kept the target source-blocked because Darkan's otherwise executable
  129-slot selector uses Grimy ranarr and Grimy irit while two intact cutoff
  revisions name Grimy guam and Grimy marrentill.
- Did not transplant emulator probabilities onto different item names. Charm
  and hard-clue rates remain emulator leads because their historical numeric
  dependencies were not recovered.
- Duradel/Lapalok remains hidden and unrenormalized at 14/35. No
  owner-facing design gap emerged. Durable evidence:
  `source-audits/slayer-suqah-combat-2026-07-19.md`.

## Slayer Steel dragon Combat target — 2026-07-19

- Added the ordinary level-246 Steel dragon as Duradel/Lapalok's fourteenth
  certifying family and a future Kuradal dependency.
- Preserved the exact period LP, Slayer XP, six-tick melee, 225-LP maximum,
  settled metal-dragon dragonfire abstraction, guaranteed Dragon bones/five
  Steel bars, exact emulator combat levels/defences/respawn, and all
  independent plate/visage/clue rolls.
- Closed Darkan's otherwise exact 123/128 ordinary selector with Coins x650
  at 5/128. The period page attests the item and the OSRS fork table matches
  every Darkan row before filling the exact five-slot gap; the row remains
  explicitly `provisional/osrs-lineage`.
- Added the losslessly enumerated quantity-three charm selector and the newest
  pre-cutoff target asset with provenance.
- Added source-data, selector-total, drop-RNG, asset, real-Qt picker, and
  derived Slayer-readiness regression coverage. Duradel/Lapalok remains hidden
  and unrenormalized at 14/35.
- Workflows run `e670532d-28df-4f13-b515-2691702928cc` was canceled after it
  acquired a worker slot but never established a Codex session or emitted a
  tool call; no reviewer output was used.
- Results:
  `status-updates/slayer-steel-dragon-results-2026-07-19.html`
  (<https://h9vvkp6arl98.postplan.dev>).
- Governing evidence:
  `source-audits/slayer-steel-dragon-combat-2026-07-19.md`.

## Slayer Black dragon Combat target — 2026-07-19

- Added the ordinary level-227 Black dragon as Duradel's thirteenth certifying
  family and a future Kuradal dependency.
- Preserved the exact period LP, Slayer XP, six-tick melee, 214-LP maximum,
  shared leather-dragon dragonfire seam, complete 128-slot ordinary selector,
  losslessly enumerated quantity-three charms, and independent Summoning-99
  egg, Draconic-visage, hard-clue, and elite-clue rolls.
- Added the newest pre-cutoff Black dragon target asset with complete
  provenance and exact timestamp/checksum assertions.
- Added source-data, selector-total, drop-RNG, skill-gate, asset, and derived
  Slayer-readiness regression coverage. Duradel remains hidden and
  unrenormalized at 13/35.
- Workflows run `874a9b0e-b075-4283-be39-324d782da75e` was canceled after it
  acquired a worker slot but never established a Codex session or emitted a
  tool call; no reviewer output was used.
- Governing evidence:
  `source-audits/slayer-black-dragon-combat-2026-07-19.md`.

## Slayer Kuradal registry-schema stop — 2026-07-19

- Closed the ordinary TzHaar family as Ket, Xil, Mej, and Hur and the Living
  rock creature family as patriarch, protector, and striker from cutoff
  `Slayer assignment` oldid `6303852`.
- Rejected Darkan's broad `tok-` name prefix as ordinary-family membership
  because the period contract keeps Fight Cave creatures in Kuradal's separate
  280-kill challenge.
- Stopped before registering Kuradal because global family gates cannot encode
  her master-specific Aquanite and Ice-strykewyrm requirements or
  Kuradal-Dungeon Dark-beast route, while the master model cannot encode
  Barbarian Training activity access.
- No runtime data or test oracle was changed. This is a settled-contract/code
  representation conflict, not an owner-facing design gap.
- Evidence:
  `source-audits/slayer-kuradal-family-boundaries-2026-07-19.md` and
  `audits/slayer-kuradal-registry-schema-conflict-2026-07-19.md`.

## Slayer Duradel/Lapalok hidden registry — 2026-07-19

- Encoded all 35 reconciled assignment rows with their exact family order,
  provisional weights, count ranges, and 334-point denominator.
- Added the hidden Combat-100, Slayer-50, Shilo-Village-gated master role and
  the While Guthix Sleeps Duradel-to-Lapalok presentation swap.
- Added eleven stable family definitions needed by the pool without adding
  unsupported Combat targets or pretending missing mechanics are ready.
- Derived readiness remains 12/35 with 23 exact blockers. The incomplete role
  returns no eligible families and stays absent from the live master picker.
- Added an exact full-table transcription oracle, exact blocker oracle,
  succession regression, direct-action integration check, and real offscreen
  Qt hidden-surface verification.
- Workflows review run `30379395-e4a3-4c32-b1b0-23118a5d563f` was canceled
  after it acquired a slot but never established a Codex session or emitted a
  tool call; no reviewer output was used.
- Governing evidence:
  `source-audits/slayer-duradel-lapalok-pool-2026-07-17.md`.

## Slayer Aquanite/Desert-strykewyrm source boundary — 2026-07-19

- Closed both period identities, LP, Slayer gates/XP, attack families,
  maxima, assignment rules, named drops, cache IDs/bonuses, and target-local
  special shapes.
- Kept both targets absent because their Darkan definitions explicitly
  generate non-real combat levels.
- Kept Aquanite blocked on its absent prayer-negating handler/rate and direct
  Water-rune, Seaweed, and Soul-rune quantity conflicts.
- Kept Desert strykewyrm blocked on Darkan's conflicting 1/21 burrow,
  unconditional double hit, Potato-cactus/herb/Coin quantities, and 1/512
  Focus-sight lead which does not independently close the period 1/484
  estimate.
- Sumona remains hidden and unrenormalized at 20/37; no owner-facing design
  decision was opened. Durable evidence:
  `source-audits/slayer-aquanite-desert-strykewyrm-combat-2026-07-19.md`.

## Slayer Spiritual-family authority stop — 2026-07-19

- Stopped before source-to-runtime implementation because the settled Sumona,
  Duradel/Lapalok, and Kuradal records require four god variants, while the
  supposedly complete registry names only one Saradomin target for each of the
  Spiritual-mage and Spiritual-warrior families.
- Confirmed rev-727 independently exposes four attackable identities per
  generic family. The rev-742 exact-name surface differs and therefore needs
  later source reconciliation rather than an inferred variant collapse.
- Left both families non-certifying at `combat_target`; no target-local God
  Wars context, Combat row, asset, or test was changed.
- Sumona remains hidden and unrenormalized at 20/37. Durable conflict record:
  `audits/slayer-spiritual-families-registry-conflict-2026-07-19.md`.

## Slayer Terror-dog source boundary — 2026-07-19

- Closed the ordinary level-110 identity, real combat levels, Slayer-40 gate
  and 87 XP, six-tick melee, 150 approximate maximum, Haunted Mine route,
  target-local Prayer drain, Big-bones split, Granite helm, cache IDs, and
  named drop set.
- Reproduced Darkan's exact 128-slot selector and found a material conflict:
  five slots yield Coins ×11, while every quantity-bearing pre-cutoff article
  revision permits only ×44–200 and later ×440.
- Inspected all 329 pre-cutoff article revisions plus the cutoff talk record;
  neither supplies or validates ×11. The talk page independently confirms the
  level-110 Big-bones split.
- Left `terror_dog`, its two-tick Prayer residual, Granite-helm item/asset, and
  all tests untouched rather than cherry-picking around the conflict. Sumona
  remains hidden and unrenormalized at 20/37.
- No owner-facing design decision is pending. Durable evidence:
  `source-audits/slayer-terror-dog-combat-2026-07-19.md`.

## Slayer Mutated-jadinko authority/source stop — 2026-07-19

- Stopped before implementation because all three settled master-pool records
  define baby, guard, and male variants at Slayer 80/86/91, while the runtime
  registry contains only the baby behind a family-level Slayer-80 gate.
- Confirmed the cutoff family page and both rev-727/rev-742 caches independently
  enumerate all three identities, so a baby-only readiness certificate would
  be false.
- Harvested all three cutoff LP/XP/style/speed/maximum envelopes, cache IDs,
  Darkan definitions, and drop leads without changing runtime.
- Kept every variant source-blocked: all three Darkan combat definitions are
  explicitly `nostats`, no independent implementation supplies the five
  combat levels, and Darkan's guaranteed Mutated-vine/Excrescence quantities
  conflict with the cutoff pages.
- Sumona remains hidden and unrenormalized at 20/37. This is an authority
  conflict plus a source dependency, not a creative-design fork. Evidence:
  `audits/slayer-mutated-jadinko-registry-conflict-2026-07-19.md` and
  `source-audits/slayer-mutated-jadinko-combat-2026-07-19.md`.

## Slayer Fever-spider source boundary — 2026-07-19

- Closed the source-ready Fever-spider identity, route, protection, ordinary
  drop-selector, and quest-only body boundaries.
- Reproduced a material disease conflict: the cutoff requires three Relicym's
  balm doses, while Darkan's disclosed severity-15/four-point reconstruction
  requires four. The exact unprotected hit formula is likewise not period
  closed.
- Left `fever_spider` absent rather than shipping persuasive but unsupported
  disease numbers. Chaeldar remains hidden at 25/34 with the same nine
  blockers; no design decision is pending.
- Recorded the no-session Workflows run
  `f2c763f0-4b3b-4ee7-abd6-6273dd05c186` and completed the audit independently.

## Slayer Elf warrior Combat closure — 2026-07-19

- Added separate ordinary level-90 ranged and level-108 melee Elf-warrior
  targets with exact period LP, Slayer XP, six-tick cadence, maximum hits, and
  completed-Regicide access.
- Preserved Darkan's hidden combat levels, exact defences, 39-tick respawn,
  guaranteed Bones, one 128-slot ordinary selector, the losslessly enumerated
  1,212-slot charm selector, and an independent 1/128 hard clue.
- Registered the unstackable, untradeable Crystal teleport seed and labeled
  the no-position combination of Lletya crystal drops and Elf-Camp charms as a
  location-flattening abstraction.
- Pinned distinct archived 2010 ranged and melee sprites while preserving
  their honest post-migration upload timestamps in provenance.
- Advanced Chaeldar to 25/34 while leaving its partial pool hidden and
  unrenormalized. Nine Combat-family blockers remain.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-elf-warrior-combat-2026-07-19.md`.
- Focused Combat/Slayer/metadata coverage passes 361 tests, and the focused
  real offscreen Qt picker passes.
- Full non-Qt discovery passes all 1,679 tests with 215 declared environment
  skips; full real offscreen Qt discovery passes all 1,679 tests with zero
  skips or failures. Test quality has zero hard issues across 73 files and
  1,679 methods. Reachability remains at 1,253 actions, 1,866 reachable items,
  288 orphan inputs, and 313 blocked actions.
- Documentation, compilation, provenance JSON, diff, readiness,
  declared-baseline reachability, and worktree-safety gates pass.
- Results:
  `status-updates/slayer-elf-warrior-results-2026-07-19.html`; mobile copy:
  <https://hp6p2ourxwdr.postplan.dev>.

## Slayer Dagannoth Combat closure — 2026-07-18

- Added separate ordinary level-74 ranged and level-92 melee Dagannoth targets
  with exact period LP, Slayer XP, six-tick cadence, and distinct combat
  identities.
- Preserved Darkan's exact levels, defences, 80-LP maxima, 59-tick respawn,
  and guaranteed Bones for both forms.
- Combined every nonzero generic Darkan drop row into one exact 1,100-slot
  selector: 1,086 occupied slots and 14 explicit empty slots. The independent
  selector channels preserve 68/26/212/6 charm slots out of 1,212 and a 1/128
  medium clue.
- Kept Waterbirth, Chaos-Tunnel, King, quest, and Daemonheim contexts
  separate. The baseline Slayer family does not receive a false
  Lighthouse-only quest gate.
- Pinned distinct pre-cutoff ranged and melee sprites with provenance.
- Advanced Chaeldar to 24/34 while leaving its partial pool hidden and
  unrenormalized. Ten Combat-family blockers remain.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-dagannoth-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 359 tests, and the focused
  real offscreen Qt picker passes.
- Full non-Qt and real offscreen Qt discovery each pass all 1,677 tests; the
  real Qt run has zero skips or failures. Test quality has zero hard issues
  across 73 files and 1,677 methods. Reachability remains at 1,253 actions,
  1,865 reachable items, 288 orphan inputs, and 313 blocked actions.
- Results:
  `status-updates/slayer-dagannoth-results-2026-07-18.html`; mobile copy:
  <https://vzhh6w72sawc.postplan.dev>.

## Slayer Cave horror Combat closure — 2026-07-18

- Added the ordinary level-80 Cave horror with Slayer 58, 550 LP, 55 Slayer
  XP, Cabin Fever and lit-light-source access, four-tick magical melee, and a
  90-LP ordinary maximum.
- Extended protective equipment to source-declared alternative slots and
  combat classes: close combat accepts a Witchwood icon or any Slayer-helmet
  variant, while ranged/Magic safespot loadouts do not receive a false
  equipment warning.
- Preserved the cutoff 87-LP scream endpoint and one-random-stat-by-5 drain.
  Protect/Deflect Melee blocks scream damage but not the drain.
- Preserved exact Darkan stats, zero bonuses, 39-tick respawn, one 128-slot
  ordinary selector including its empty slot, the exact variable-allotment
  nested table, a losslessly enumerated 1,212-slot charm selector,
  Long/Curved bones, 1/512 Black mask (10), and 1/128 hard clue.
- Pinned the pre-cutoff Cave horror icon and its provenance.
- Advanced Chaeldar to 23/34 while leaving its partial pool hidden and
  unrenormalized. Eleven Combat-family blockers remain.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-cave-horror-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 409 tests, and the focused
  real offscreen Qt picker passes.
- Full non-Qt and real offscreen Qt discovery each pass all 1,675 tests; the
  real Qt run has zero skips or failures. Test quality has zero hard issues
  across 73 files and 1,675 methods. Documentation, compilation, provenance
  JSON, diff, readiness, reachability, and worktree-safety gates pass.
- Results:
  `status-updates/slayer-cave-horror-results-2026-07-18.html`; mobile copy:
  <https://pmzz0dpygpxu.postplan.dev>.

## Slayer Bronze dragon Combat closure — 2026-07-18

- Added the ordinary level-131 Bronze dragon with 1,220 LP, 125 Slayer XP,
  six-tick melee plus metal-dragon dragonfire, a 123-LP melee maximum, and a
  conservative 500-LP dragonfire maximum.
- Reused shared shield/antifire protection and labeled Darkan's exact adjacent
  1/2 melee-versus-fire selector as the no-position encounter abstraction.
- Preserved exact Darkan levels, defences, respawn, guaranteed Dragon bones
  and five Bronze bars, the 128-slot ordinary selector including its empty
  slot, the losslessly enumerated 1,212-slot charm selector, independent
  1/2,048 plate drops, and 1/128 hard plus 1/500 elite clues.
- Pinned the pre-cutoff Bronze dragon sprite and its provenance.
- Advanced Chaeldar to 22/34 while leaving its partial pool hidden and
  unrenormalized. Twelve Combat-family blockers remain.
- Excluded location, route, quest-only, post-cutoff, and Dungeoneering
  contexts. No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-bronze-dragon-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 352 tests, and the focused
  real offscreen Qt picker passes.
- Full non-Qt and real offscreen Qt discovery each pass all 1,670 tests; the
  real Qt run has zero skips or failures. Test quality has zero hard issues
  across 73 files and 1,670 methods. Documentation, compilation, provenance
  JSON, diff, readiness, reachability, and worktree-safety gates pass.
- Results:
  `status-updates/slayer-bronze-dragon-results-2026-07-18.html`; mobile copy:
  <https://pbdlptcksw7s.postplan.dev>.

## Slayer Blue dragon family Combat closure — 2026-07-18

- Added the ordinary level-111 Blue dragon and level-48 Baby blue dragon as
  separate, source-backed target choices that both count for the family.
- Preserved the adult's 1,100 LP, 107.6 Slayer XP, six-tick melee, 110-LP
  melee maximum, dragonfire, exact emulator defences/respawn, guaranteed Blue
  dragonhide and Dragon bones, 128-slot ordinary table, 404-slot charm table,
  1/128 hard clue, and Summoning-99 1/2,000 egg gate.
- Kept the baby melee-only with 510 LP, 50 Slayer XP, no dragonfire, and
  guaranteed Baby dragon bones.
- Added generic player-skill gates to Combat drop tables and integration
  coverage proving a kill forwards player levels without consuming a gated
  table's RNG when locked.
- Pinned both pre-cutoff enemy sprites and their provenance.
- Advanced Chaeldar to 21/34 while leaving its partial pool hidden and
  unrenormalized. Thirteen Combat-family blockers remain.
- Excluded location, quest-route, Daemonheim, and Dungeoneering contexts. No
  owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-blue-dragon-family-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 350 tests, and the focused
  real offscreen Qt picker passes. Full non-Qt and real offscreen Qt discovery
  each pass all 1,668 tests; the real Qt run has zero skips or failures.
- Test quality has zero hard issues across 73 files and 1,668 methods.
  Documentation, compilation, provenance JSON, diff, readiness, reachability,
  and worktree-safety gates pass.
- Results:
  `status-updates/slayer-blue-dragon-family-results-2026-07-18.html`; mobile
  copy: <https://ez10f8mr9lib.postplan.dev>.

## Slayer Fire giant Combat closure — 2026-07-18

- Added the ordinary level-86 Fire giant with 1,110 LP, 111 Slayer XP,
  five-tick melee, a 116-LP maximum, period poison behavior, guaranteed Big
  bones, exact Darkan stats, and a 59-tick respawn.
- Preserved one exact 128-slot ordinary selector, including nested herb, gem,
  and standard-rare tables; losslessly enumerated Darkan's inclusive charm
  behavior into 404 slots; and kept Long/Curved bones independent at 1/400 and
  1/5,000.
- Pinned the pre-cutoff `Fire giant.png` revision and its provenance.
- Advanced Chaeldar to 20/34 while leaving its partial pool hidden and
  unrenormalized. Fourteen Combat-family blockers remain.
- Excluded location-only quest/Wilderness/Smoke-Dungeon contexts and all
  Daemonheim/Dungeoneering variants from the ordinary representative.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-fire-giant-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 347 tests, and the focused
  real offscreen Qt picker passes. Full non-Qt and real offscreen Qt discovery
  each pass all 1,665 tests; the real Qt run has zero skips or failures.
- Test quality has zero hard issues across 73 files and 1,665 methods.
  Compilation, diff, readiness, reachability, and worktree-safety audits pass
  or match their declared baseline.
- Results: `status-updates/slayer-fire-giant-results-2026-07-18.html`; mobile
  copy: <https://6v3lhweptj0p.postplan.dev>.

## Slayer Chaeldar hidden registry — 2026-07-18

- Encoded all 34 source-reconciled master rows with their exact current count
  ranges and provisional 388-point hidden denominator.
- Added seventeen stable family identities plus source-declared Slayer,
  Combat-skill, quest, protection, finisher, restricted-weapon,
  assignment-only, disease, neem-oil, and crystal-chime completeness gates.
- Registered Chaeldar at Combat 70 behind Lost City while keeping
  `runtime_enabled=False`; live master selection cannot see or renormalize the
  partial pool.
- Derived 25/34 readiness after the Fire giant, Blue dragon, Bronze dragon,
  Cave horror, Dagannoth, and Elf-warrior closures. Nine absent target identities each report one
  deterministic `combat_target` blocker, while Gargoyles and Mutated
  zygomites reuse their already-live finisher mechanics.
- Preserved the source-blocked Rum Deal stage boundary for Fever spiders
  instead of misrepresenting it as quest-completion access.
- Added focused pool, range, gate, hidden-runtime, blocker, and catalog
  integrity regressions. Slayer/Combat/metadata coverage passes 89 tests.
- Full non-Qt discovery passes all 1,663 tests with 215 declared environment
  skips; full real offscreen Qt discovery passes all 1,663 with no skips,
  failures, or errors. Documentation, test quality, compilation, diff,
  readiness, reachability, and worktree-safety checks pass.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-chaeldar-registry-2026-07-18.md`. Results:
  `status-updates/slayer-chaeldar-registry-results-2026-07-18.html`; mobile
  copy: <https://dkvu5eb3h0w8.postplan.dev>.

## Slayer Turoth Combat closure — 2026-07-18

- Added the ordinary level-83 Turoth with Slayer 55, 760 LP, 76 Slayer XP,
  passive six-tick melee, a 97-LP maximum, poison immunity, and Darkan's exact
  stats, bonuses, and 59-tick respawn.
- Enforced the period damage restriction before a review can be spent:
  Leaf-bladed spear or sword for melee, Broad arrows or Broad-tipped bolts for
  Ranged, or Magic Dart with the canonical `Slayer's staff`.
- Added source-backed Broad-arrow bow compatibility, Broad-tipped-bolt support,
  ammunition-level locks, the Rune crossbow's exact Ranged-61 item-config gate,
  and Magic-staff recognition for `Slayer's staff`.
- Preserved one exact 100,000-slot Darkan ordinary selector, the losslessly
  enumerated 1,212-slot Darkan charm selector, and an independent 1/128 hard
  clue.
- Generated the light Mystic bottom and Leaf-bladed sword, corrected the
  Leaf-bladed spear's Attack-50/Slayer-55 requirements, and pinned cutoff enemy
  and rare-drop art with provenance.
- Advanced Vannaka to 34/35 while leaving the partial pool hidden and
  unrenormalized. Mogres remain the sole quest-owned blocker.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-turoth-combat-2026-07-18.md`. Results:
  `status-updates/slayer-turoth-results-2026-07-18.html`.
- Published the mobile closure report at
  <https://gimdeversiok.postplan.dev>.
- Focused coverage passes 622 methods with 211 expected non-Qt skips. Full
  non-Qt discovery passes all 1,661 methods with 215 expected Qt-environment
  skips; full real offscreen Qt executes all 1,661 with zero skips, failures,
  or errors. Documentation, test quality, generated-data determinism,
  compilation, JSON, diff, readiness, reachability, and worktree-safety gates
  pass.

## Slayer Molanisk Combat closure — 2026-07-18

- Added the ordinary level-51 Molanisk with Slayer 39, 520 LP, 52 Slayer XP,
  six-tick passive melee, a 53-LP maximum, exact Darkan stats/bonuses, and a
  59-tick respawn.
- Reused the completed Death to the Dorgeshuun quest, live 150-coin Slayer bell,
  and existing Firemaking light-source graph. One bell is required but not
  consumed; any reachable lit source may be carried or equipped.
- Flattened the wall interaction into one visible line: each Combat encounter
  starts by ringing the bell to lure one Molanisk, with no redundant target,
  wall-clock state, or pseudo-item.
- Preserved guaranteed Bones, one exact 100,000-slot cumulative Darkan
  selector with 211 empty slots, and an independent 1/128 easy clue. Darkan
  has no Molanisk charm row, so none was invented.
- Added cache-backed Swamp weed and Mole claw identities with period art and
  pinned the cutoff Molanisk sprite.
- Advanced Vannaka to 33/35 while leaving the partial pool hidden and
  unrenormalized. Mogres and Turoth remain.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-molanisk-combat-2026-07-18.md`. Results:
  `status-updates/slayer-molanisk-results-2026-07-18.html`.
- Published the mobile closure report at
  <https://2a1t6lht0q8n.postplan.dev>.
- Focused coverage passes 602 methods with 211 expected non-Qt skips; the
  focused real offscreen Qt picker passes. Full non-Qt and real offscreen Qt
  discovery each pass all 1,657 methods, with no real-Qt skips. Documentation
  passes across 326 Markdown and 342 HTML files; test quality reports zero hard
  issues across 73 files. Compilation, JSON, diff, worktree-safety, readiness,
  and reachability audits were rerun.

## Slayer Brine rat Combat closure — 2026-07-18

- Added the ordinary level-70 Brine rat with Slayer 47, 500 LP, 50 Slayer XP,
  six-tick passive melee, a 93-LP maximum, zero bonuses, and a 59-tick respawn.
- Added a non-consumed real-Spade cavern gate. The target records the sourced
  Olaf's Quest stage-40 permission while conservatively consuming stable quest
  completion until the Darkan thread exports that semantic state.
- Preserved guaranteed Bones and Raw rat meat, one exact 512-slot cumulative
  ordinary selector including the 1/512 Brine sabre, the exact 606-slot Darkan
  charm selector, and an independent 1/128 medium clue.
- Registered Brine sabre item 11037 and generated its exact Attack-40,
  one-handed, four-tick equipment block with +7 stab, +47 slash, -2 crush, and
  +46 melee strength.
- Pinned cutoff Brine-rat and Brine-sabre assets. The underwater-only Liquefy
  special remains an explicit future Combat capability rather than a fake
  ordinary effect.
- Advanced Vannaka to 32/35 while leaving the partial pool hidden and
  unrenormalized. Mogres, Molanisks, and Turoth remain.
- Kept quest ownership clean in
  `codex-briefs/darkan-quest-handoff-brine-rat-2026-07-18.md`.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-brine-rat-combat-2026-07-18.md`. Results:
  `status-updates/slayer-brine-rat-results-2026-07-18.html`.
- Focused verification passes 614 methods. Full non-Qt discovery passes all
  1,653 methods with 215 expected Qt-environment skips; full real offscreen Qt
  discovery executes all 1,653 with zero skips, failures, or errors.
- Documentation, test-quality, generated-data, diff, readiness, reachability,
  provenance, and worktree-safety gates pass.
- Published the mobile closure report at
  <https://cf55icb0rmwe.postplan.dev>.

## Slayer Sea snakes Combat closure — 2026-07-18

- Added ordinary Sea Snake Hatchling and Sea Snake Young Combat targets with
  their cutoff levels, LP, Slayer gates/XP, melee maxima, poison consequences,
  and Royal Trouble route.
- Reconciled Darkan's generated hatchling stats, exact young-snake stats, zero
  bonuses, 59-tick respawns, complete ordinary tables, tertiary bone table,
  and independent 1/128 medium-clue rows.
- Preserved Darkan's exact cumulative 13,000-slot hatchling ordinary selector:
  11,700 Casket slots, 26 one-slot rares, and 1,274 empty slots. One kill
  cannot emit both a Casket and a rare row.
- Represented the young snake's post-quest 68-LP poison as the visible nearest
  70-LP value required by the integer old-scale poison channel. The six-tick
  cadence is labeled corroborated rather than period exact.
- Reused canonical `Broad arrows` item 4160 rather than reviving its retired
  singular storage alias, registered Edible seaweed item 403 with canonical
  inventory shape and a real item asset, and pinned both pre-cutoff enemy
  sprites.
- Kept quest ownership clean: Combat uses conservative Royal Trouble
  completion until Darkan exposes a stable mid-quest dungeon-permission state.
  The follow-up is recorded in
  `codex-briefs/darkan-quest-handoff-sea-snakes-2026-07-18.md`.
- Advanced Vannaka to 31/35 while leaving the partial pool hidden and
  unrenormalized. Brine rats, Mogres, Molanisks, and Turoth remain.
- Focused verification passes 682 tests. Full non-Qt discovery passes 1,649
  tests with 215 expected Qt-environment skips; full real offscreen Qt
  discovery executes all 1,649 with zero skips, failures, or errors.
- Documentation, test-quality, generated-data, compilation, diff, readiness,
  reachability-ledger, provenance, and worktree-safety gates pass.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-sea-snakes-combat-2026-07-18.md`. Results:
  `status-updates/slayer-sea-snakes-results-2026-07-18.html`; mobile copy:
  <https://i3lix9qo57d8.postplan.dev>.

## Slayer Killerwatt Combat closure — 2026-07-18

- Added the ordinary level-71 Killerwatt with Slayer 37, existing
  Ernest-the-Chicken access, 510 LP, 51 Slayer XP, eight-tick attacks, and a
  64-LP maximum.
- Preserved its distance-sensitive attack contract: melee play receives
  magical melee against Magic defence and Protect from Melee, while Ranged and
  Magic play receive Ranged attacks and Protect from Missiles.
- Made the same resolved channel drive Casual max-safety prayer selection.
- Preserved the non-blocking boots consequence. Insulated boots suppress the
  hazard; without them, one labeled 0–140 LP thundercloud roll is added to each
  incoming attack. This is a bounded review-native cadence abstraction.
- Restored the source's Slayer-37 Insulated-boots wear requirement in generated
  equipment data while retaining the existing 200-coin Slayer-master stock.
- Added guaranteed Impious ashes, Darkan's exact 100,000-slot ordinary
  selector, and the independently derived 303-slot charm selector.
- Made Combat enemy asset fetching cutoff-aware and fetched the 2011 Killerwatt
  sprite rather than the modern replacement.
- Advanced Vannaka to 30/35 while leaving the incomplete master hidden and
  unrenormalized. No quest/catalog work or owner-facing design fork was added.
- Focused verification passes 747 tests. Full non-Qt discovery passes 1,645
  tests with 215 expected Qt-environment skips; full real offscreen Qt
  discovery executes all 1,645 with zero skips, failures, or errors.
- Documentation, test-quality, generated-data, compilation, JSON, diff,
  readiness, reachability-ledger, and worktree-safety checks pass.
- Durable evidence:
  `source-audits/slayer-killerwatt-combat-2026-07-18.md`. Results:
  `status-updates/slayer-killerwatt-results-2026-07-18.html`; mobile copy:
  <https://4wz22cbm89jb.postplan.dev>.

## Slayer Harpie Bug Swarm Combat closure — 2026-07-18

- Added the ordinary level-46 Harpie Bug Swarm with Slayer 33, 250 LP, 25
  Slayer XP, six-tick melee, and a 60-LP maximum hit.
- Preserved the source's literal continuous damage gate: lit bug lantern item
  7053 must occupy the shield slot when every Combat review begins, including
  an already-active encounter.
- Added Firemaking 33 lighting and ungated extinguishing as zero-XP Utility
  item swaps, generated the lit lantern as wearable zero-bonus shield
  equipment, and preserved the existing 130-coin Slayer-master acquisition.
- Excluded the lit bug lantern from functional light-source gates because the
  cutoff item page explicitly says it cannot illuminate caves.
- Encoded Darkan's exact 100,000-slot ordinary selector and independently
  derived 202-slot charm selector. The cutoff wiki's different drop contents
  are recorded as a source conflict.
- Advanced Vannaka to 29/35 while leaving the incomplete master hidden and
  unrenormalized. Six missing Combat representatives remain. No owner-facing
  design fork emerged.
- Durable evidence:
  `source-audits/slayer-harpie-bug-swarm-combat-2026-07-18.md`. Results:
  `status-updates/slayer-harpie-bug-swarm-results-2026-07-18.html`
  (<https://lwn2getn9lo2.postplan.dev>).
- Verification closed with 747 focused tests, 1,640 full non-Qt tests
  (215 declared Qt-only skips), and all 1,640 tests in the real offscreen Qt
  environment with zero skips, failures, or errors. Documentation,
  test-quality, generated-data, reachability, and worktree audits were rerun.

## Slayer Green dragon Combat closure — 2026-07-18

- Added the ordinary Wilderness level-79 Green dragon with 750 LP, 75 Slayer
  XP, six-tick attacks, an 85-LP melee maximum, guaranteed Dragon bones and
  Green dragonhide, and the pinned imported drop selectors.
- Added reusable dragonfire tiers: 500 LP unprotected, 50 LP with one layer,
  and zero with complete protection. The hidden 1/4 breath frequency is
  explicitly `provisional/darkan` because game-main conflicts at 1/10.
- Registered complete Antifire and Super antifire vial/flask families,
  preserving every remaining dose and exact six-minute/600-game-tick duration.
  Combat auto-loads one bottle and can refresh it inside a long review without
  using wall-clock time.
- Generated Anti-dragon shield item 1540 as wearable shield equipment with its
  exact cache bonuses and reused the existing Dragon Slayer acquisition path.
- Combined dragonfire state and Wilderness loss consequences in one target
  preview and confirmation. Exact charm rates remain `source_blocked`.
- Advanced Vannaka to 28/35 while leaving the incomplete master hidden and
  unrenormalized. Seven missing Combat representatives remain. No owner-facing
  design fork emerged.
- Durable evidence:
  `source-audits/slayer-green-dragon-combat-2026-07-18.md`. Results:
  `status-updates/slayer-green-dragon-results-2026-07-18.html`
  (<https://blwhzxpwaa52.postplan.dev>).

## Slayer Earth warrior Wilderness-risk closure — 2026-07-18

- Applied the owner-approved 1%/250-LP bounded PKer abstraction after each
  successful Earth-warrior Combat review and reset the encounter on a trigger.
- Added separate Wilderness death semantics: three highest-value equipped items
  kept, Protect Item adds one, other equipped items permanently lost, ordinary
  inventory retained, and no new grave.
- Added a process-local risk fingerprint so Anki restart or a material
  kept/lost-set change requires fresh confirmation before any review can
  advance.
- Exposed chance, maximum hit, kept/lost counts, no-grave behavior, and the
  distinct Wilderness-risk state in the Combat target surface.
- Safe-skill reviews now discard active Wilderness encounter progress.
- Advanced Vannaka to 27/35 while keeping the incomplete pool hidden and
  unrenormalized. Eight missing Combat representatives remain. No owner-facing
  design fork emerged.
- Durable evidence:
  `source-audits/slayer-earth-warrior-wilderness-risk-2026-07-18.md`. Results:
  `status-updates/slayer-earth-warrior-wilderness-results-2026-07-18.html`
  (<https://73amt4x2o23l.postplan.dev>).

## Slayer Dust devil Combat closure — 2026-07-18

- Added the ordinary level-93 Dust devil with Slayer 65, 1,050 LP, 105 Slayer
  XP, six-tick melee, and a 90-LP maximum hit.
- Preserved the cutoff's literal damage gate: Face mask, Masked earmuffs, or
  an accepted Slayer helmet must remain equipped throughout the fight.
- Used the cutoff-attested Chaos Tunnels route rather than inventing a Desert
  Treasure quest dependency or duplicating quest work.
- Encoded Darkan's exact 32,768-slot ordinary selector, exact nested herb/gem
  tables, and independent 606-way charm selector.
- Generated Dragon chainbody item 3140 as Defence-60 body equipment and fixed
  the generator to prefer an exact drop-row source ID over ambiguous name
  fallback.
- Advanced Vannaka to 26/35 while keeping the incomplete master hidden and
  unrenormalized. Eight Combat targets plus Earth warrior's Wilderness risk
  remain. No owner-facing design fork emerged.
- Durable evidence:
  `source-audits/slayer-dust-devil-combat-2026-07-18.md`. Results:
  `status-updates/slayer-dust-devil-results-2026-07-18.html`
  (<https://dylce5d5v14s.postplan.dev>).

## Darkan ordinary-drop selector correction — 2026-07-18

- Reproduced Darkan's executable `DropList` behavior: all nonzero sibling rows
  in one NPC drop JSON share one cumulative random selector; rate-zero always
  rows and the separately invoked charm path remain distinct.
- Corrected eleven live targets: Warriors' Guild Cyclops, Cyclossus, Young
  grotworm, Desert lizard, Rockslug, Gargoyle, Mutated zygomite,
  Jungle horror, Shadow warrior, Infernal Mage, and Basilisk.
- Preserved every individual marginal probability while removing impossible
  sibling multi-drop combinations. Cyclossus's period-common Dragon defender
  and Mutated zygomite's Fungicide remain separate labeled abstractions rather
  than being passed off as Darkan rows.
- Added denominator, boundary-reachability, mutual-exclusion, charm-separation,
  generated-equipment, and real offscreen Qt regression coverage.
- Corrected the affected source audits, live Memory Bank summaries, and
  published status artifacts. No owner design input was required. Durable
  evidence is
  `source-audits/slayer-darkan-drop-selector-correction-2026-07-18.md`;
  results are in
  `status-updates/slayer-darkan-drop-selector-correction-results-2026-07-18.html`
  (<https://pk45017w1z2j.postplan.dev>).

## Slayer Shadow warrior Combat closure — 2026-07-18

- Added the ordinary level-48 Shadow warrior as a Legends'-Quest-gated Combat
  target with 670 LP, 67 Slayer XP, six-tick melee, and maximum hit 65.
- Preserved Darkan's executable ordinary-drop shape as one 128-way selector
  with 106 occupied and 22 empty slots.
- Derived the exact executable Darkan charm distribution from its inclusive
  threshold-and-uniform-selection algorithm rather than treating the four
  source numbers as independent percentages.
- Reused the existing Legends' Quest completion state without adding or
  duplicating quest stages.
- Advanced Vannaka from 23/35 to 24/35 without exposing or renormalizing the
  incomplete master. Ten missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks and the real offscreen Qt picker pass. Exact period defensive
  bonuses remain `source_blocked`; no owner design input was required. Durable
  evidence is
  `source-audits/slayer-shadow-warrior-combat-2026-07-18.md`. Results:
  `status-updates/slayer-shadow-warrior-results-2026-07-18.html`
  (<https://4c0ztjs0b4cs.postplan.dev>).

## Slayer Jungle horror Combat closure — 2026-07-18

- Added the ordinary level-70 Jungle horror as a Cabin-Fever-gated Combat
  target with 450 LP, 45 Slayer XP, six-tick melee, and maximum hit 84.
- Preserved Darkan's executable drop shape: guaranteed Bones plus one exact
  100,000-slot selector containing all 32 nonzero JSON rows.
- Reused the existing Cabin Fever completion state without adding or
  duplicating quest stages.
- Advanced Vannaka from 22/35 to 23/35 without exposing or renormalizing the
  incomplete master. Eleven missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks, the real offscreen Qt picker, and a bounded read-only
  Sol-high workflow review pass. Exact period charm distribution remains
  `source_blocked`; no owner design input was required. Durable evidence is
  `source-audits/slayer-jungle-horror-combat-2026-07-18.md`. Results:
  `status-updates/slayer-jungle-horror-results-2026-07-18.html`
  (<https://7s9qx4vwmhao.postplan.dev>).

## Slayer Otherworldly being Combat closure — 2026-07-18

- Added the ordinary level-64 Otherworldly being as a Lost-City-gated Combat
  target with 660 LP, 66 Slayer XP, six-tick melee, and maximum hit 70.
- Encoded Darkan's exact 128-slot ordinary table, including nested minor-herb
  and gem rolls plus 18 explicit empty slots.
- Reused the existing Lost City completion state without adding or duplicating
  quest stages.
- Advanced Vannaka from 21/35 to 22/35 without exposing or renormalizing the
  incomplete master. Twelve missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks and the real offscreen Qt picker pass. Durable evidence is
  `source-audits/slayer-otherworldly-being-combat-2026-07-18.md`; no owner
  design input was required. Results:
  `status-updates/slayer-otherworldly-being-results-2026-07-18.html`
  (<https://q57byaii1o36.postplan.dev>).

## Slayer Crocodile Combat closure — 2026-07-18

- Added the ordinary level-63 River Elid Crocodile as a Slayer-10 Combat target
  with 630 LP, 62 Slayer XP, five-tick melee, and maximum hit 67.
- Preserved the exact level-63 drop boundary: guaranteed Bones and no other
  table. Darkan's merged level-63/89 Bones-plus-Big-bones row is rejected.
- Reused the existing filled-Waterskin desert hazard with dose preservation,
  review-driven consumption, pack capacity, bank runs, and atomic undo.
- Advanced Vannaka from 20/35 to 21/35 without exposing or renormalizing the
  incomplete master. Thirteen missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks and the real offscreen Qt picker pass. Durable evidence is
  `source-audits/slayer-crocodile-combat-2026-07-18.md`; no owner design input
  was required. Results:
  `status-updates/slayer-crocodile-results-2026-07-18.html`
  (<https://kjy22255e4a6.postplan.dev>).

## Slayer Basilisk Combat closure — 2026-07-18

- Added the ordinary level-61 Basilisk as a Slayer-40 Combat target with 750
  LP, 75 Slayer XP, six-tick melee, maximum hit 59, and guaranteed Bones.
- Reused the equipped Mirror-shield contract while preserving Basilisk's
  distinct source behavior: Protect from Melee blocks the unshielded damage
  but not its random five-level stat drain.
- Encoded the exact 64,000-slot Darkan selector containing the 128-based
  ordinary rows, 1/512 light-Mystic row, and 1/2,000 Basilisk-head row. Charm
  distribution remains `source_blocked`.
- Registered Mystic hat (light) as generated Defence-20/Magic-20 equipment and
  corrected Basilisk head to its non-stackable, untradeable item-7977 identity.
- Advanced Vannaka from 19/35 to 20/35 without exposing or renormalizing the
  incomplete master. Fourteen missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks and the real offscreen Qt picker pass. Durable evidence is
  `source-audits/slayer-basilisk-combat-2026-07-18.md`; no owner design input
  was required. Results:
  `status-updates/slayer-basilisk-results-2026-07-18.html`
  (<https://12bv7z5x53a2.postplan.dev>).

## Slayer Infernal Mage Combat closure — 2026-07-18

- Added the ordinary level-66 Infernal Mage as a Slayer-45 Combat target with
  600 LP, 60 Slayer XP, six-tick Magic attacks, maximum hit 89, and guaranteed
  Bones.
- Preserved Darkan's executable source shape as one exact 64,000-slot
  selector containing the 128-based ordinary rows, both 1/512 dark-mystic
  rows, and the 1/1,000 Lava battlestaff row.
- Registered Lava battlestaff, dark Mystic hat, and dark Mystic boots as
  generated equipment with exact period requirements, bonuses, and weapon
  speed.
- Advanced Vannaka from 18/35 to 19/35 without exposing or renormalizing the
  incomplete master. Fifteen missing targets and Earth warrior's Wilderness
  context remain.
- Charm distribution remains explicitly `source_blocked`. Focused checks, the
  real offscreen Qt picker, and all 1,604 pure tests pass. Durable evidence is
  `source-audits/slayer-infernal-mage-combat-2026-07-18.md`; no owner design
  input was required. Results:
  `status-updates/slayer-infernal-mage-results-2026-07-18.html`
  (<https://6zhziqqts1l7.postplan.dev>).

## Slayer Bloodveld Combat closure — 2026-07-18

- Added the ordinary level-76 Bloodveld as a Slayer-50 Combat target with 1,200
  LP, 120 Slayer XP, six-tick magic-based melee, maximum hit 59, and guaranteed
  Bones.
- Encoded Darkan's 123 named ordinary slots plus five explicit empty slots at
  the exact denominator 128; no absent rare-table or herb rows were invented.
- Registered Black boots item 4125 as generated Defence-10 feet equipment with
  exact 2011Scape bonuses and an item asset.
- Advanced Vannaka from 17/35 to 18/35 without exposing or renormalizing the
  incomplete master. Sixteen missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks, the real offscreen Qt picker, and all 1,601 pure tests pass.
  Durable evidence is
  `source-audits/slayer-bloodveld-combat-2026-07-18.md`; no owner design input
  was required. Results:
  `status-updates/slayer-bloodveld-results-2026-07-18.html`
  (<https://k9ynbzcx5a8u.postplan.dev>).

## Slayer Jelly Combat closure — 2026-07-18

- Added the ordinary level-78 Jelly as a Slayer-52 Combat target with 750 LP,
  75 Slayer XP, six-tick magic-based melee, and the reconciled 60-LP maximum
  hit.
- Encoded Darkan's exact mutually exclusive 128-slot ordinary drop table and
  deliberately excluded Soul Wars' separate fragment/PvP variant.
- Registered Mithril boots item 4127 as generated Defence-20 feet equipment
  with exact 2011Scape bonuses, item identity, acquisition, and asset surface.
- Advanced the generated Vannaka ledger from 16/35 to 17/35 without exposing or
  renormalizing the incomplete master. Seventeen missing targets and Earth
  warrior's Wilderness context remain.
- Focused checks and the current 1,599-test pure suite pass; the production
  state also passed the 1,601-test real offscreen Qt suite before two redundant
  pure test methods were consolidated. Durable evidence is
  `source-audits/slayer-jelly-combat-2026-07-18.md`; no owner design input was
  required. Results: `status-updates/slayer-jelly-results-2026-07-18.html`
  (<https://qvrpp85jnouq.postplan.dev>).

## Slayer Vannaka pool and Ogre Combat closure — 2026-07-18

- Encoded all 35 cutoff Vannaka families, their reconciled weights/count
  ranges, and the provisional 460-point denominator without exposing a partial
  master or renormalizing around missing families.
- Extended the executable readiness audit to report Vannaka at 16/35 and name
  all 19 remaining target/context blockers from live registry state.
- Added the ordinary level-53 Ogre with 600 LP, 60 Slayer XP, guaranteed Big
  bones, Darkan's exact 1,000-slot common-seed subtable behind its `19/128`
  roll, independent long/curved-bone tertiary rolls, and a provenance-pinned
  pre-cutoff sprite.
- Kept quest ownership clean: Mogres still depend on the Darkan-owned
  `skippy_and_the_mogres` completion ID, and this slice adds no quest/catalog
  substitute.
- Focused checks, all 1,597 pure tests, and all 1,597 real offscreen Qt tests
  pass. Durable evidence is
  `source-audits/slayer-vannaka-ogre-combat-2026-07-18.md`; no owner design
  input was required. Results:
  `status-updates/slayer-vannaka-ogre-results-2026-07-18.html`
  (<https://o849m34h9y3r.postplan.dev>).

## Warriors' Guild and Cyclopes closure — 2026-07-18

- Implemented all five source activities and token balances, Casual/Advanced
  automation, single/multi Cyclops-room entry and exact residual drain,
  progressive defender showing/drops, multi-token benefits, and explicit room
  exit/depletion/death cleanup.
- Added source-backed Cyclops and Cyclossus Combat targets. Cyclossus spawns
  only after Rune has been shown, interrupts the ordinary target, requires a
  worn Rune or Dragon defender, and returns to Cyclops after defeat.
- Registered all eight defenders and the cosmetic Cyclopean helmet as equipment
  with period bonuses/requirements, source-shaped drops, provenance-tracked
  activity/enemy/item assets, and a compact real Qt control surface.
- Advanced live Mazchna/Achtryn readiness from 25/27 to 26/27. Mogres is now
  the sole blocker and remains correctly assigned to the Darkan quest pass for
  `skippy_and_the_mogres`; the incomplete master stays hidden.
- Exact missing rates remain explicit abstractions rather than invented parity
  claims. The complete evidence boundary is
  `source-audits/warriors-guild-live-implementation-2026-07-18.md`; no owner
  design input was required.
- Moved defender and Cyclopean-helmet registration into
  `tools/generate_equipment_data.py` after full discovery caught a brittle
  manual-tail boundary. Focused pure and Qt checks, all 1,592 core tests, all
  1,592 real offscreen Qt tests, documentation, test-quality, readiness,
  provenance, and worktree checks pass. Results:
  `status-updates/warriors-guild-results-2026-07-18.html`
  (<https://vsx8a7pxsimj.postplan.dev>).

## Slayer Kalphite Soldier Combat closure — 2026-07-18

- Added the ordinary level-85 Kalphite Soldier as an executable Combat target
  with 900 LP, 90 Slayer XP, a six-tick melee attack, an approximate 80-LP
  maximum hit, and a pre-cutoff target image.
- Encoded Darkan's exact 128-slot mutually exclusive drop table using the
  existing item registry plus shared gem and minor-herb tables; no name-only
  economy item was introduced.
- Reused the shared poison runtime and made the unavoidable magnitude
  abstraction explicit: the period page gives 48 LP, while the
  game-main-shaped integer unit can represent only ten-LP increments, so the
  target uses the nearest value of 50 LP rather than 480 or 40.
- Advanced executable Mazchna/Achtryn readiness from 22/27 to 23/27 without
  exposing the partial master. Cyclopes, Mogres, Vampyres, and Wall beasts are
  the four exact remaining Combat-target blockers.
- Focused pure and real offscreen Qt regressions pass. Full core discovery
  passes all 1,566 methods with 213 declared environment skips; full real
  offscreen Qt discovery passes all 1,566 methods without failures or skips.
  Test quality reports zero hard issues, and documentation, compilation, diff,
  readiness, and worktree checks pass. The expected reachability debt ledger
  remains 1,231 actions, 1,811 reachable items, 285 orphan inputs, and 311
  blocked actions.
- Durable evidence is
  `source-audits/slayer-kalphite-soldier-combat-2026-07-18.md`; the visual
  report is
  `status-updates/slayer-kalphite-soldier-combat-results-2026-07-18.html`
  (<https://trn4s92bn2a4.postplan.dev>). No owner design decision was required.

## Slayer Pyrefiend Combat closure — 2026-07-18

- Added the ordinary level-43 Pyrefiend as a Slayer-30 Combat target with 450
  LP, 45 Slayer XP, a 44-LP maximum hit, guaranteed Impious ashes, the exact
  128-slot ordinary drop table, and a pre-cutoff target image.
- Implemented the source's distinct magic-based-melee contract: enemy Attack
  plus stab bonus rolls against player Magic defence, while Protect from Melee
  remains the relevant protection prayer. Casual max-safety and the Combat
  picker expose the same semantics.
- Registered Steel boots item 4123 as real Defence-5 feet equipment with exact
  bonuses, source identity, asset provenance, reachability, and generated-data
  coverage.
- Advanced the executable Mazchna/Achtryn readiness ledger from 21/27 to 22/27
  without exposing a partial master. Cyclopes, Kalphites, Mogres, Vampyres, and
  Wall beasts remain the five exact Combat-target blockers.
- Focused backend and real picker regressions pass. Full core discovery passes
  all 1,565 methods with 213 declared environment skips; full real offscreen Qt
  discovery passes all 1,565 methods without failures or skips.
- Durable evidence:
  `source-audits/slayer-pyrefiend-combat-2026-07-18.md`; the visual report is
  `status-updates/slayer-pyrefiend-combat-results-2026-07-18.html`
  (<https://0ga1wxb9wpb8.postplan.dev>). No owner design decision was required.

## Slayer Mazchna/Achtryn hidden-pool readiness — 2026-07-18

- Split stable Slayer family identities from master-specific assignment rows,
  preserving Turael's live values while encoding all 27 Mazchna/Achtryn rows
  and the exact provisional 325-point denominator.
- Kept Mazchna/Achtryn runtime-disabled; Achtryn's While Guthix Sleeps interval
  remains source metadata rather than an exposed partial role.
- Added an executable readiness audit over live Combat targets, Slayer XP, and
  required poison/protection/finisher mechanics. It certifies Turael/Spria at
  23/23 and reports Mazchna/Achtryn at 22/27.
- Closed the stale Hobgoblin blocker with the pinned pre-EOC 29/49 Slayer XP.
  The only remaining Mazchna target blockers are Cyclopes, Kalphites, Mogres,
  Vampyres, and Wall beasts.
- Added pure regression coverage for master-specific rows, hidden-master
  behavior, exact blocker derivation, and catalog-integrity failures. No owner
  design question emerged.
- Full core and real offscreen Qt discovery each pass all 1,560 methods.
  Focused Slayer/Combat/runtime/integration coverage, test quality,
  documentation, compilation, JSON, diff, reachability, and worktree-safety
  checks pass.
- Published
  `status-updates/slayer-mazchna-readiness-results-2026-07-18.html`
  (<https://ir3cpm2ptnfp.postplan.dev>).

## Slayer Mutated zygomite Combat closure — 2026-07-18

- Added both ordinary Mutated zygomite variants with period Slayer/quest gates,
  LP, Slayer XP, maximum hit, sprites, and the one-line reveal interaction.
- Implemented charge-preserving Fungicide spray states `10 → 0`, canister
  reloads, manual and quick finishing parity, and capacity-safe Combat refills.
- Registered cache items `7421–7432` with non-stackable/non-tradeable inventory
  shape and shared dose-state icon fallback.
- Reconciled the Darkan selector probabilities only where period
  identity/quantity evidence allows it; unresolved rows and the 140-LP spore
  frequency remain explicit `source_blocked` omissions.
- Focused pure, runtime, registry, metadata, provenance, and reachability
  coverage passes 391 methods. Full core discovery passes all 1,557 methods
  with 213 declared environment skips; full real offscreen Qt discovery passes
  all 1,557 methods without skips or failures.
- Test-quality, documentation, JSON, reachability-route, diff, and worktree
  safety checks pass. The visual report is
  `status-updates/slayer-mutated-zygomite-results-2026-07-18.html`; mobile
  copy: <https://ujk2cg24j80q.postplan.dev>.

## Public derivative release disposition — 2026-07-17

- Settled the former personal-fork-versus-public-release question in favor of
  preparing a distinct public derivative release.
- Measured the lineage at a fixed Git snapshot: about 2.2% of current
  production code is surviving unchanged original code under a conservative
  comparison, while about 70.0% of Wilson's original production code still
  survives. This supports “radically expanded derivative fork,” not minor
  update or independent rewrite.
- Locked prominent Wilson Yeh original-creator credit, Arman Tarkhanian
  independent-maintainer identity, a new AnkiWeb listing, explicit compatible
  licensing, complete source links, and a corrected in-product review link.
- Kept publication gated on written license clarification or acknowledgement,
  public-repository synchronization, asset redistribution provenance, packaging,
  migration, real-profile, performance/accessibility, export/recovery, and
  post-upload verification.
- Durable record:
  `public-release-lineage-and-license-2026-07-17.md`.

## Shared catalog search seam — 2026-07-17

- Added one reusable `CatalogFilterBar` for Shop, Quests, Combat, and future
  large catalog surfaces. Pages own their metadata and predicates; the shared
  widget owns dark-mode-safe search chrome, clear/Escape behavior, optional
  filter placement, and count summaries.
- Added live Combat text search over exact target ids, labels, tooltips, and
  groups. Filtering preserves the persisted target, expands matching groups,
  restores the current row after clear, and renders an inert empty state.
- Added Quest text search that composes with access, difficulty, length,
  timeline, completion, and start-eligibility filters. Migrated Shop's existing
  source-backed search input onto the same component without changing backend
  result semantics.
- Kept `Current Slayer task only` out until real assignment state lands; no
  disabled placeholder or invented task state is exposed.
- Verification passes all 1,478 pure/core methods and all 1,478 real offscreen
  Qt methods with no failures or skips, plus focused interaction checks, visual
  offscreen rendering, test-quality, documentation, compilation, and
  worktree-safety gates.
- Published
  `status-updates/slayer-search-seam-results-2026-07-17.html` and its mobile-safe
  copy at <https://s1kaasu9wfmq.postplan.dev>.

## Slayer Dogs-family Combat slice — 2026-07-17

- Added the level-21 Jackal as an ordinary Combat target and the first
  executable representative of Slayer's Dogs family.
- Preserved the cutoff 270 LP, 27 Slayer XP, guaranteed Bones, aggression, and
  explicit 80 LP maximum hit. Darkan independently supplies its Attack 17,
  Strength 18, Defence 15, melee identity, and respawn row.
- Added a sourced 48px target asset and provenance, exact data/preview
  regressions, and a real offscreen Qt picker assertion covering the row,
  tooltip, and rendered icon.
- Verification passes all 1,481 core methods, 337 focused
  Combat/target/runtime/cadence methods, the real offscreen Qt picker check,
  documentation, compilation, test-quality, diff, and worktree-safety gates.
- Kept Turael/Spria and Mazchna/Achtryn hidden. This certifies one baseline
  family dependency; it does not renormalize either incomplete master pool.
- Durable evidence:
  `source-audits/slayer-dogs-jackal-combat-2026-07-17.md`.

## Slayer Icefiend Combat slice — 2026-07-17

- Added the ordinary level-13 Icefiend as an executable Slayer-family target;
  God Wars, Ghorrock, quest, Revenant, and Daemonheim variants remain distinct.
- Preserved the cutoff 150 LP, 15 Slayer XP, melee identity, passive stance,
  guaranteed Impious ashes, and explicit 20 LP maximum hit. game-main and the
  matching Darkan level-13 row converge on Attack 10, Strength 10, and Defence
  12; the cutoff page overrides game-main's conflicting 7 XP and hybrid style.
- Added game-main's exact 128-slot ordinary drop table, a sourced target asset,
  provenance, exact roster/preview regressions, and real offscreen Qt picker
  coverage.
- Verification passes all 1,482 core methods, 339 focused
  Combat/target/runtime/cadence methods, the real offscreen Qt picker check,
  documentation, compilation, test-quality, diff, and worktree-safety gates.
  Reachability remains the declared 290-orphan debt ledger rather than a green
  gate.
- Kept Turael/Spria hidden. The family dependency is ready, but the incomplete
  master pool is not renormalized or exposed.
- Durable evidence:
  `source-audits/slayer-icefiend-combat-2026-07-17.md`.

## Live cadence activation — 2026-07-17

- Made the `R = 1000` cadence kernel default-on with an explicit boolean-false
  legacy rollback.
- Added complete handler/route coverage, exact lower-endpoint residual admission
  for compatible ranged evidence, authentic embedded-probability routes, and
  source-blocked passthrough for incompatible rows.
- Changed ordinary Combat to `6 × M` immediate ticks with persistent encounter,
  prayer/curse, status, special-regeneration, and RNG phase. Again grants no
  encounter beat; terminal boundaries cannot chain another enemy.
- Preserved one collapsed quest stage per eligible review while keeping
  flag-off quest combat at its legacy 50 ticks.
- Replaced the three retired XP-parity expected failures and obsolete runtime
  shadow integration tests with live route, residual, RNG, continuity, undo,
  and coverage tests.
- Reconciled Design 2 timing decisions: Loyalty and Veteran counts remain on the
  independent 240-answer world day; Aura windows are eligible-action budgets;
  recurring entries reuse world-calendar boundaries; Tears beats are
  activity-progress actions; Castle Wars retains 5,000 games but drops the
  invalid 16,667-review calendar conversion.
- Final post-review verification passes all 1,476 core methods (1,275 ordinary
  passes and 201 environment skips) and all 1,476 real offscreen Qt methods
  with no skips. The focused
  cadence/kernel/parity/combat/runtime/Summoning/Thieving slice passes 363
  methods. Documentation, compilation, reachability, asset integrity, worktree
  safety, and test-quality gates also pass; the quality audit reports zero hard
  issues across 71 test files.
- Fixed the final independent-review blocker: successful Combat answers no
  longer mark a live encounter disengaged and therefore cannot trigger
  between-fight Dream healing mid-encounter. Again still marks disengagement,
  and the next successful slice resumes the exact combat/RNG phase.
- Published `status-updates/cadence-kernel-live-results-2026-07-17.html` and
  its mobile-safe copy at <https://nl2rgoy9pvqk.postplan.dev>.

## Summoning implementation closure — 2026-07-17

- Shipped the complete 80-familiar surface catalog, 78 pouch recipes, 67
  scroll targets, exact source XP/requirements, and the ordinary Skills-hub
  training surface.
- Added persistent summon/dismiss/renew state, separate ordinary and
  special-move points, BoB storage/reclaim, four-review Familiarisation, its
  ingredient/triple-charm rewards, and answered-card world ticks.
- Restored the 47 freeze-date pets, their shared follower slot, care/growth,
  acquisition log, death/release semantics, Menagerie dependency, UI, assets,
  migration, and undo-safe commands.
- Added exact Summoning and super-restore dose families, source-ready familiar
  boosts, Bunyip healing, Void-shifter escape, Pack yak Winter Storage, and all
  78 Bogrog pouch exchanges.
- Kept Daemonheim out of the overworld and parked unsourced combat/scroll,
  forager, and teleport mechanics without fabricated substitutes. No unresolved
  owner-level design question remains.
- Verified 1,446 core methods (1,242 ordinary passes, 201 environment skips,
  three expected failures) and 1,446 real offscreen Qt methods (1,443 ordinary
  passes, three expected failures), plus focused UI, docs, test-quality,
  compilation, JSON, generator-determinism, diff, and worktree-safety gates.
  Reachability records 1,220 actions and 290 known acquisition/dependency
  orphans (112 root, 178 cascade); it remains a debt report, not a passing gate.

## Mage Arena and Farming cure-policy closure — 2026-07-17

- Completed the sourced Mage Arena reward loop: final-form alignment, the first
  matching cape/staff, one-review god-spell attunement, one-cape statue
  replacement/reclaim, matching-loadout equipment guards, and legacy-save
  compatibility.
- Completed Charge's real combat effect. The matching attuned god spell rises
  from 200 to 300 LP maximum hit only while Charge is active and the matching
  cape/staff are worn; preview and live combat share the calculation.
- Added the three period god-cape assets and generated their exact item-config
  equipment rows. Their canonical item records now retain cache IDs,
  non-stackability, non-tradeability, cape-slot metadata, and provenance. The
  generator reproduces the equipment rows rather than relying on hand edits.
- Added Farming's per-patch two-option cure priority, preset/queue snapshots,
  execution-time fallback, and canonical Cure Plant rune/quest/XP transaction.
- Archived both resolved owner questions; no non-Summoning design gap remains
  from the grill-harvest program.
- Final verification passed all 1,388 core methods and all 1,388 real offscreen
  Qt methods. Core discovery retains 196 environment skips; Qt discovery has
  none. Both contain only the three declared XP-parity expected failures, and
  test quality reports zero hard issues across 67 files.
- Published
  `status-updates/mage-arena-farming-cure-results-2026-07-17.html` and its
  mobile-safe copy at <https://q0wso578s42a.postplan.dev>.

## Slayer Turael/Spria source harvest — 2026-07-17

- Reconciled the first complete functional-master pool at 23 families and a
  355-point provisional hidden-weight denominator.
- Restored Gelatinous abominations and Grotworms from cutoff monster/tutorial
  evidence plus emulator convergence; rejected Turael Trolls as an anonymous,
  malformed wiki-table insertion contradicted by the cutoff cross-master table
  and Darkan.
- Closed the Icefiend conflict at 10–20 from the explicit Turael correction and
  two-emulator convergence. Gelatinous ordinary count remains a labeled 15–50
  Turael-default abstraction, distinct from its sourced five-kill tutorial.
- Kept Turael/Spria out of live assignment generation because six families and
  two distinctive kill/protection mechanics remain baseline blockers.
- Fixed Cave slime's omitted source `poisonDamage = 3` and added deterministic
  Combat-state coverage.
- Durable evidence:
  `source-audits/slayer-turael-spria-pool-2026-07-17.md`.

## Slayer Mazchna/Achtryn source harvest — 2026-07-17

- Reconciled the second functional-master pool at 27 families and a provisional
  325-point hidden-weight denominator.
- Rejected the anonymous Mazchna `40–85` range in favor of the earlier
  Knowledge Base correction, cutoff Achtryn table, and Darkan convergence at
  `40–70`; preserved `30–60` Cyclopes and `10–20` Wall beasts, and used the
  repaired cutoff row span to close Grotworms at `40–70` over Darkan's
  conflicting `20–40`.
- Restored the emulator-stubbed Mogre and Wall-beast rows from cutoff master,
  cross-master, and individual monster evidence. Their 10-point hidden weights
  are labeled common-baseline abstractions, not recovered facts.
- Kept Mazchna/Achtryn out of live assignment generation because ten families,
  three existing-target mechanics, and the whole assignment-family registry
  remain runtime blockers.
- Fixed Cave crawler's omitted source `poisonDamage = 8` and added deterministic
  Combat-state coverage.
- Durable evidence:
  `source-audits/slayer-mazchna-achtryn-pool-2026-07-17.md`.

## Slayer Vannaka source harvest — 2026-07-17

- Reconciled the third functional-master pool at 35 families and a provisional
  460-point hidden-weight denominator.
- Rejected Darkan's extra Troll row because the cutoff Vannaka page omits it and
  the cutoff cross-master table assigns Trolls only to Chaeldar and Sumona.
- Restored Mogres and Sea snakes from cutoff master/cross-master evidence.
  Their 10-point weights are labeled common-baseline abstractions; game-main's
  explicit 2.17% ordinary-family rows independently round from `10 / 460`.
- Kept the single observed Grotworm count of 69 as history rather than a fake
  range, and labeled Darkan's ordinary Vannaka `60–120` range as the smallest
  explicit count abstraction.
- Kept Vannaka out of live assignment generation because 23 families, the
  stable family/variant registry, and numerous quest, protection, lure, context,
  and restricted-kill mechanics remain runtime blockers.
- Corrected the Stronghold Shade to its cutoff 3.5 Slayer XP and one-quarter
  ordinary combat/Constitution damage XP, with a deterministic live-burst
  regression.
- Corrected the earlier Turael audit: current game-main does execute its
  incomplete Slayer table through the talk-to assignment path.
- Durable evidence:
  `source-audits/slayer-vannaka-pool-2026-07-17.md`.

## Slayer Chaeldar source harvest — 2026-07-17

- Reconciled the fourth functional-master pool at 34 families and a provisional
  388-point hidden-weight denominator.
- Restored Grifolapines and Grifolaroos from direct cutoff individual pages
  despite their omission from the stale master/cross-master tables.
- Restored Shadow warriors and Mutated zygomites over Darkan's omissions with
  explicit 10-point common-baseline abstractions.
- Kept Darkan's remaining weights provisional, closed Elves at `60–90`, and
  labeled Grotworms' `72–109` as an observed-history envelope rather than a
  recovered generator range.
- Restored Chaeldar's 10/50/150 point schedule from the cutoff Slayer-points
  table, both emulators, and the master page's own long-run arithmetic.
- Corrected the accepted gates where Darkan conflicts with cutoff evidence:
  Regicide for Elves, Rum Deal route access for Fever spiders, Magic 50 for
  Fungal magi, Magic 60 for Grifolapines/Grifolaroos, and Slayer 67 plus
  Branches of Darkmeyer for Vyrewatch.
- Kept Chaeldar out of live assignment generation: end-to-end family readiness
  is 0/34, 29 families have no direct target, and Banshee/Baby-blue behavior
  requires complete protection/identity mechanics.
- Corrected the live level-8 Crawling hand from game-main's conflicting 12
  Slayer XP to the cutoff 16, with a focused source regression.
- Durable evidence:
  `source-audits/slayer-chaeldar-pool-2026-07-17.md`.

## Slayer Sumona source harvest — 2026-07-17

- Reconciled the fifth functional-master pool at 37 families and a provisional
  407-point hidden-weight denominator.
- Restored Scabarites and Terror dogs from cutoff master, cross-master, and
  individual-family evidence over Darkan's commented stubs. Their 10-point
  weights are labeled common-baseline abstractions; Darkan's other 35 rows
  contribute 387 provisional points.
- Kept cutoff Black demons, Grifolapines, Grifolaroos, and Mutated jadinkos
  despite omissions in the stale cross-master table, and corrected Darkan's
  Black-demon and Gargoyle count conflicts to `120–185`.
- Closed Sumona's Combat 85, Slayer 35, Smoking Kills, and 12/60/180 point
  gates. Preserved the Kalphite Queen challenge as a 15,000-XP, 30-point,
  one-task compound objective while leaving its exact offer rule
  `source_blocked`.
- Kept Sumona out of live assignment generation: end-to-end family readiness
  is 0/37, only four ordinary families have complete Combat targets, and the
  remaining family registry, quest, target, protection, identity, special, and
  task-credit paths are absent.
- Removed the incorrect 60 Slayer XP from temporary Death spawns and added a
  cutoff-source regression.
- Durable evidence:
  `source-audits/slayer-sumona-pool-2026-07-17.md`.

## Agility carried-risk amendment — 2026-07-17

- Integrated into `main` at `69855d9`.
- Added real target-local Auto/Custom course packs, required-item gates, ordered
  food, Bank-clamped carried/equipment weight, and a one-review supply refill.
- Routed course damage through shared auto-eat, death, grave, and review undo
  while preserving dormant target packs.
- Added the approved Wilderness 1% lap-completion ambush before reward commit;
  fatal hits forfeit the pending lap atomically.
- Added live pack/weight/risk summaries without exposing Combat-only controls.
- The final checker found and the primary fixed stale saved packs contributing
  weight after Bank disposal.
- Verified 1,353 core methods, two real offscreen Qt checks, zero hard test
  quality issues, 236 Markdown and 298 HTML files, and safe diff/worktree
  closure.

## Farming replacement and preset amendment — 2026-07-17

- Integrated into `main` at `9b65f45`.
- Added the explicit one-review `Dig up` verb for healthy mature regrowth
  crops, including differing-plan full runs that queue removal before planting.
- Added user-named whole-farm presets with selected patch inclusion, inert
  selection/application, modified-state reporting, and full CRUD management.
- Added per-plan gardener, watering, and Plant-cure policies. Full runs skip and
  report patches missing gardener goods instead of silently planting
  unprotected.
- Gardener payments are validated queue escrow: successful planting consumes
  them, while queue removal, clearing, or execution skips refund them.
- The independent final checker found and the primary fixed removable payment
  ownership and maximum-length duplicate preset names.
- Verified all 1,363 core methods (1,164 ordinary passes, 196 environment
  skips, three expected failures), all 1,363 real offscreen Qt methods (1,360
  ordinary passes, three expected failures), 84 final focused Qt tests, zero
  hard test-quality issues, and safe diff/worktree closure.

## Worktree collapse — 2026-07-16

- Reconciled all seven linked worktrees into the canonical checkout and removed
  their safe-root directories. Agility/Bank decisions, Herblore assets, test
  cleanup, Thieving, and the overnight audit were already contained in `main`.
- Integrated the previously unmerged Slayer design contract and eight focused
  source audits, preserving its complete owner-grill history while reconciling
  current Memory Bank and archive structure.
- Integrated the paused Summoning design ledger through decision 22 plus its
  lifecycle, training, Familiarisation, simulation-time, reviewer-alert, and
  Help contracts. Summoning remains an active design/source program; this does
  not claim runtime implementation.
- `git worktree list` now contains only the canonical `main` checkout, and the
  worktree-guard audit passes.
- Closure artifact:
  `status-updates/worktree-collapse-results-2026-07-16.html`.

## Documentation archive closure — 2026-07-16

- Added a Memory Bank index and explicit archive policy so current entry points,
  evidence records, and historical artifacts have distinct homes.
- Archived six superseded/completed root records plus the completion audit's JSON
  companion; copied all four approved-but-unimplemented overnight decisions to
  the canonical Kanban before archiving their resolved question ledger.
- Moved 308 old status files into monthly archives while retaining the three
  current July closure reports at the top-level status entry point.
- Extended the documentation audit to validate local HTML resources and to
  tolerate staged old paths during link-safe file moves.
- Closure verification: 215 Markdown and 295 HTML documents pass the audit;
  all 1,329 core tests pass with 193 environment skips and three declared
  expected failures; test quality has zero hard issues across 67 files. All 24
  JSON files parse, compilation/diff/worktree-safety gates pass, and Qt testing
  is not required because no runtime or UI behavior changed.
- Closure artifact:
  `status-updates/documentation-archive-results-2026-07-16.html`.

## Documentation integrity closure — 2026-07-16

- Audited all 505 project Markdown/HTML documents, including this closure's
  final results artifact. The permanent `tools/audit_docs.py` gate checks UTF-8,
  final newlines, whitespace defects, Markdown fences/local links, HTML
  doctypes, parsing, and explicit element nesting.
- Reconciled current status to 17 complete, five partial, and three planned
  skills; corrected merged-branch pointers, live acquisition/reachability
  claims, and the difference between approved design and shipped behavior.
- Preserved dated evidence instead of rewriting history. Historical contracts,
  audits, briefs, and results now carry explicit status or later-integration
  notes where their original wording could be mistaken for current state.
- Full core verification ran 1,327 methods: 1,131 ordinary passes, 193
  environment skips, and three expected failures. The test-quality audit reports
  zero hard issues across 67 files; JSON parsing, compilation, diff, and
  worktree-safety checks pass.
- Closure artifact:
  `status-updates/documentation-integrity-results-2026-07-16.html`.

Phase 1 of the cadence kernel is complete on `main` at `b45aff0`. It
adds a dormant pure scheduler, additive config-v34 route residuals, the strict
off-by-default `ankiscape_cadence_kernel` flag, and exact save/load/undo and
flag-off RNG/output regression coverage. No skill behavior is routed or changed.

Phase 3 shadow observation is merged into `main` at `6422610`. The
six in-scope adapters record current and proposed outcomes without mutating live
gameplay. The 175-route catalog has 24 source-ready routes and 151 explicit
`source_blocked` routes. Exact range envelopes, embedded Cooking/Firemaking
source rolls, overflow declarations, save/load sanitation, reporting, and
review undo are covered. Combat and the now-separately-shipped Thieving surface
remain outside the cadence experiment.

## Complete Skill Surfaces

- Gathering: Mining, Woodcutting, Farming, Fishing, Hunter.
- Artisan: Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Herblore, Construction.
- Support/combat-adjacent: Prayer, Magic, Thieving, Agility, and Summoning.

These surfaces use stable IDs, flat save state, review or background dispatch as appropriate, inventory mutation, telemetry, undo, assets/provenance, Skills-hub UI, Stats/Bank/HUD integration, and focused tests.

## Partial Combat Skills

Unified Combat trains Attack, Strength, Defence, Constitution, and Ranged. They deliberately remain `partial` because they do not own independent Skills-hub review surfaces. Magic is complete: its noncombat and combat contracts both ship.

## Implemented Partial Dungeoneering

Dungeoneering is the sixth partial trainable skill. Its Frozen floor runtime,
Ring of Kinship tiers, staged reward trader, and working Coal bag are live.
Further floor themes and depth remain program work; the registry has no planned
skill surface.

## Thieving closure

Thieving adds 17 pickpocket rows, 18 stall-family rows, one complete Menaphite
blackjack row, two visible source-blocked quest rows, exact cadence scheduling,
source-weighted loot, shared combat LP/stun/fight-back state, storage v35,
grouped Qt selection, four stable achievements, RuneScape-sourced skill and
Phoenix assets with provenance, and targeted pure/runtime/storage/Qt coverage.
Failure damage reuses Combat auto-eat/death/grave state, while encounter-only
Menaphites stay out of the ordinary Combat picker. The Feud and The Golem were
already playable in the 194-quest catalog; Thieving consumes those live
completion states.

Verification: 1,240/1,240 tests pass under Python 3.12 and under the real
offscreen Anki/Qt environment; `run_tests.py` is also green. The three expected
XP/hour parity failures predate this slice. A 609-test focused closure set,
zero Thieving/Phoenix reachability orphans, compilation, and `git diff --check`
complete the gate. See
`status-updates/archive/2026-07/thieving-skill-results-2026-07-13.html`.

## Cadence Phase 3 Closure — 2026-07-13

The cadence Phase 3 closure adds:

- one guarded central observation seam for Mining, Woodcutting, Fishing, Hunter, Cooking, and Firemaking;
- exact rational low/high source envelopes with no midpoint collapse;
- reuse of the already-consumed live roll for Cooking and Firemaking, with no RNG drift;
- a separate transactional `cadence_shadow` namespace that never seeds live `cadence_profiles`;
- complete 175-route catalog and observed-save reporters for current, proposed, and source XP/hour;
- fail-closed handling for 151 missing or semantically incompatible source rows;
- fixed-seed flag-on/off gameplay-byte, XP, loot, call-sequence, RNG, save/load, and undo proof.

The durable closure record is `cadence-kernel-phase3-shadow-2026-07-13.md`.

## Prayer Polish Closure — 2026-07-13

The Prayer polish closure adds:

- atomic material/method selection;
- owned gilded altars at 250/300/350% with once-per-stint marrentill;
- 26 five-state training-urn tiers across Mining, Cooking, Fishing, Woodcutting, Smithing, and Prayer;
- target-carried Bonecrusher and Ectoplasmator behavior;
- direct full-urn teleport with immediate persistence and independent LIFO undo;
- substitution-aware skilling and Combat repacks;
- exact Chivalry/Rigour/Augury/Piety Defence gates;
- distinct Bonemeal and Wyvern bonemeal identities plus Prayer/Super prayer restore behavior;
- explicit RS3 provenance for the two new passive icons.

The durable source/conflict record is `source-audits/prayer-altar-urn-passives-herblore-closure-2026-07-13.md`.

## Systems That Work

- Skills hub, target metadata/renderers, Stats, Bank, Equipment, HUD, settings, and achievements.
- Utility/Activities and material processing.
- Target-local carried inventory, Advanced layouts, bank runs, Keep/Drop, Combat loadouts, and undo.
- NPC Shops, shared stock, services/actions, player selling, market clock, and shop undo.
- Bank Claims and pending future-skill XP rewards.
- A 194-row pre-EOC quest catalog with stage gates and focused audited replacements; presence remains scaffolding, not full fidelity.
- Item registry, source generators, asset scraping/provenance, reachability audit, and OpenRS2 cache queries.

## Remaining Programs

- Complete the remaining breadth and depth of partial Combat and Dungeoneering.
- Full Combat/equipment/enemy/boss/instance breadth.
- Quest-by-quest fidelity across all 194 rows.
- Activities, minigames, D&Ds, reward currencies/shops, and timed events.
- GE and broad authentic acquisition closure.
- Achievement diaries, clue scrolls, collections, and one-time world rewards.
- Global level-1-to-99/economy pacing and release-readiness.

## Verification Baseline

- `/opt/homebrew/bin/python3 run_tests.py --list` discovers 4,445 tests on
  2026-08-26. Fixed pass, skip, and expected-failure totals belong in dated
  result records rather than this current summary.
- Plain and real offscreen Qt closure must use the same discovered corpus; the
  plain lane may skip tests that require `aqt`, but the Qt lane must execute them.

### Historical verification snapshots

The following figures are preserved as pre-2026-07-16 snapshots. Current runs
outrank them.

- Herblore asset, production-hook, and worktree-guard focused suites: 44 tests
  passing; focused real Qt Herblore behavior: 2 tests passing. A live Anki
  restart registers one bridge callback, one click opens one menu, and the
  corrected compact Herblore rail icon is visible.
- Compilation and `git diff --check` pass for the correction slice.

- Cadence Phase 3 focused suite: 176 tests passing, three expected failures.
- Phase 3 full non-Qt discovery: 1,219 tests passing, 187 skips, three expected failures.
- Phase 3 full real offscreen Qt discovery: 1,219 tests passing, three expected failures.
- Cadence Phase 1 targeted suite: 11 tests passing.
- Focused Prayer/passive/urn/logic/combat/Construction/runtime/storage/integration/Farming: 626 tests passing.
- Independent backend audit superset: 663 tests passing.
- `python3 run_tests.py`: 1,198 tests passing, 187 skips, 3 expected failures.
- Full real offscreen Qt discovery: 1,198 tests passing, 3 expected failures.
- Reachability: 1,102 actions, 725 consumed items, 296 orphan inputs (151 root, 145 cascade).
- Compilation and `git diff --check`: clean.

## Overnight fresh-eyes pass 4 — exact light-source identity (2026-07-16)

- Replaced the `Light source`/`Light sources` pseudo-item with eleven reachable
  exact lit states in eight source-placed quest gates and Dorgesh-Kaan Agility.
- Preserved the complete eighteen-item cutoff-era classification separately,
  without surfacing deferred Seer's headbands or expired event torches.
- Corrected the Tears of Guthix stage sequence and removed unsupported numeric
  gates from Watchtower and Another Slice of H.A.M.
- Removed Temple of Ikov's user-visible phantom requirement and repaired the
  live-vs-generated and consumed-equipment test oracles.
- Committed as `83de7e1`; 253 focused and 1,270 full tests pass, with zero hard
  test-quality issues and unchanged reachability counts.

## Overnight fresh-eyes pass 5 — persisted item-state symmetry (2026-07-16)

- Migrated legacy lantern and Mining helmet references across carried packs,
  advanced layouts, loot overrides, grave/Death's Office items and loadouts,
  and the Magic alchemy selector before carried-state sanitation.
- Prevented paid reclaim from restoring an unregistered zero-stat helmet or a
  phantom bank item during the live session.
- Reconfirmed that strung amulet identities are current items and must not be
  folded into the legacy migration map.
- Committed as `3953b64`; 312 focused and 1,272 full tests pass, with zero hard
  test-quality issues.

## Overnight fresh-eyes pass 6 — service and achievement symmetry (2026-07-16)

- Repaired Pottery Apprentice to read the canonical `Empty pot` identity and
  corrected the Monkey general stall to produce that same registered item.
- Replaced Activity Circuit's arbitrary five-key count with an exact check of
  all six live Agility activity families, including Flash Powder Factory.
- Independently cleared Bob Barter's total-dose, container, review-neutrality,
  and independent-undo paths without changing them.
- Committed as `c1ca766`; 183 focused and 1,274 full tests pass. Reachability
  remains 1,114 actions, 264 orphan inputs, and 149 cascade orphans; the test
  quality audit reports zero hard issues.

## Overnight fresh-eyes pass 7 — Qt lifecycle and bridge ownership (2026-07-16)

- Preserved upstream add-on results through Anki's tuple-valued global webview
  filter contract and consumed AnkiScape debug messages without nested tuples.
- Serialized deferred bridge opens, replaced the previous profile menu on each
  load, retained one XP popup, and marked the large main dialog for deletion on
  close.
- Removed the unreachable duplicate bridge handler and its wall-clock debounce,
  plus the unsupported `DeckBrowserContent.links` hook and four tests that
  asserted a fabricated Anki API. The real rendered-page JavaScript injector is
  unchanged and remains the sole deck-browser button path.
- Committed as `09aacc2`; 91 focused tests, 86 clean real-Qt lifecycle and
  integration tests, and 1,273 full tests pass. Compilation, diff, worktree
  safety, and the zero-hard-issue test-quality gate are clean.

## Overnight fresh-eyes pass 8 — canonical registry and graph coverage (2026-07-16)

- Repaired Adamantite Artisan and Runite Refiner to read the canonical live
  `Adamant bar` and `Rune bar` identities.
- Unified source item 4600 as `Willow blackjack` across generated equipment,
  the registry, shops, quest rewards, Thieving requirements, and equip runtime.
- Added live Magic and Prayer production to item reachability, including rune
  costs and dynamic bone inputs, and updated stale battlestaff dependency notes.
- Committed as `5ab5aee`; 78 focused, 509 integration/end-to-end, eight real
  offscreen Qt, and 1,275 full tests pass. Reachability covers 1,188 actions and
  reports 270 orphan inputs (110 root, 160 cascade); test quality remains at
  zero hard issues.

## Overnight fresh-eyes pass 9 — final quest stages and reward equipment (2026-07-16)

- Added the missing completion sentinel after every live quest's highest
  requirement, restoring the final source-backed objective in 152 generated
  quests rather than letting completion skip it.
- Generated source-config equipment records for seven obtainable quest items,
  corrected Ice arrows to the `ammunition` slot, and reclassified the
  non-equippable Staff of armadyl as quest material.
- Added catalog-wide, pure progression, runtime-handler, registry, generator,
  and level-gate regressions.
- Committed as `ceaab20`; 127 registry/shop/quest tests, 104 quest/runtime
  tests, four real offscreen Qt checks, and all 1,280 non-Qt tests pass.
  Reachability remains 1,188 actions with 270 orphan inputs, and test quality
  remains at zero hard issues.

## Overnight fresh-eyes pass 10 — Combat state and consequence symmetry (2026-07-16)

- Prioritized loaded compatible arrows over banked lower tiers, eliminating an
  ordinary-drop-triggered `out_of_ammo` stall.
- Routed Vengeance and Spellbook Swap through the finite rune loadout, persisted
  their cross-review state, kept Dream between fights, and counted reflected
  kills through the normal drop path.
- Moved filtered loot from a fatal multi-kill review into the grave and made
  Protect Item retain the highest store-value equipped item.
- Committed as `916b075`; 334 focused tests, eight real offscreen Qt checks, and
  all 1,286 tests pass. Reachability remains 1,188 actions with 270 orphan
  inputs, and test quality remains at zero hard issues.

## Overnight fresh-eyes pass 11 — ranged producer and equipment identity (2026-07-16)

- Normalized H.A.M. loot, Combat drops, and NPC shops to the canonical plural
  standard-arrow identities, with quantity-preserving save and shop-undo
  migration for legacy singular keys.
- Regenerated the equipment snapshot so all live Crafting and Fletching
  equipment outputs are accepted by the equipment engine, adding 29 missing
  rows and a synchronization oracle.
- Committed as `9273cf4`; 263 focused tests, five real offscreen Qt checks, and
  all 1,291 tests pass. Reachability remains 1,188 actions with 270 orphan
  inputs, and test quality remains at zero hard issues.

## Overnight fresh-eyes pass 12 — consumable and supply-pack state paths (2026-07-16)

- Routed Kebab through live RNG with deterministic undo and added exact Open
  and Open all actions for every registered supply pack.
- Added Juju farming potion activation with exact dose conservation and assets,
  then resolved the Magic essence mix identity conflict from pinned cache and
  emulator evidence.
- Aligned registry tradeability, Agility potion dose identities, food
  categories, assets, Bank verbs, and reachability with their live consumers.
- Committed as `f794108`; 19 focused tests, five real offscreen Qt checks, and
  all 1,302 tests pass. Reachability covers 1,200 actions with 273 orphan
  inputs, and test quality remains at zero hard issues.

## Overnight fresh-eyes pass 13 — finite Combat preset state (2026-07-16)

- Removed the owned `combat_supply_loadout` from the preset field contract, so
  saving or pinning configuration cannot snapshot real item quantities.
- Legacy presets containing the bad field are harmless on apply; the currently
  loaded finite pack remains authoritative and continues to deplete normally.
- Committed as `1fb0b64`; 271 focused tests, two real offscreen Qt checks, and
  all 1,303 tests pass. Reachability remains 1,200 actions with 273 orphan
  inputs, and test quality remains at zero hard issues.

## Overnight fresh-eyes pass 14 — atomic achievement dependencies (2026-07-16)

- Changed pure achievement dispatch to project newly satisfied completions and
  iterate until no dependent predicate becomes newly true.
- Added a catalog-backed regression proving Master Mage and Living Legend are
  returned by the same dispatch when Magic 99 closes the final ordinary gap.
- Committed as `b59c846`; 251 focused tests, one real offscreen Qt check, and
  all 1,304 tests pass with 186 skips and three expected failures. Test quality
  remains at zero hard issues; compilation, diff, and worktree safety pass.

## Overnight fresh-eyes pass 15 — production persistence and UI reachability (2026-07-16)

- Routed Shop, service, vendor, Bob Barter, and Wilderness transaction state to
  the canonical player-data save callback instead of the current-skill config
  callback, which never wrote the mutated player state.
- Added a Farming-sheet Juju potion control backed by the existing pure action
  and projection, including dose preservation and active-bonus legibility.
- Committed as `1120fb4`; 242 focused tests, all 183 real offscreen Qt tests,
  and all 1,305 core tests pass with 187 skips and three expected failures.
  Test quality remains at zero hard issues; compilation, diff, and worktree
  safety pass.

## Overnight fresh-eyes pass 16 — live skill-surface coherence (2026-07-16)

- Resolved friendly HUD target labels and equipped-blackjack readiness for the
  newest skill families.
- Made Magic, Construction, Thieving, and Agility controls refresh dependent
  state and report direct-action outcomes immediately.
- Exposed all five sourced Brimhaven XP exchanges and made target switching or
  Stop Training end the paid arena stint.
- Committed as `483eb55`; 170 focused core tests, eight real offscreen Qt
  checks, and all 1,312 core tests pass with 193 skips and three expected
  failures. Test quality remains at zero hard issues; compilation, diff, and
  worktree safety pass.

## Overnight fresh-eyes pass 17 — atomic reward consequences (2026-07-16)

- XP-lamp claims now recalculate the selected skill level before achievement
  evaluation and surface the granted XP immediately.
- Quest-bank claims and Stronghold boot/coin rewards register direct-action
  undo snapshots before mutating live state.
- Shop purchases, sales, services, and vendor actions dispatch achievements
  before the canonical save callback.
- Committed as `111b280`; 109 focused core tests and nine real offscreen Qt
  Shop checks pass. Test quality remains at zero hard issues; compilation,
  diff, and worktree safety pass. Full closure verification remains pending.

## Overnight fresh-eyes pass 18 — Combat management consequences (2026-07-16)

- Clearing the finite Combat loadout now repaints returned Bank items in the
  open dialog.
- Loadout unload and Death's Office reclaim dispatch inventory achievements
  before persistence.
- Kept automatic safe-boundary refill as the settled UI instead of reviving the
  deliberately removed manual Refill control.
- Committed as `91f0b35`; 252 focused core tests and the combat-filtered real
  offscreen Qt surface pass. Test quality remains at zero hard issues;
  compilation, diff, and worktree safety pass. Full closure remains pending.

## Overnight fresh-eyes audit closure (2026-07-16)

- Completed 18 bounded passes and 36 attributable commits in a dedicated safe
  worktree; the verified history was subsequently fast-forwarded into `main`.
- Final core: 1,314 methods in 39.163 seconds, comprising 1,118 ordinary passes,
  193 environment skips, and three expected XP-parity failures.
- Final real offscreen Qt: 1,314 methods in 543.509 seconds, comprising 1,311
  ordinary passes, no skips, and the same three expected failures.
- Test quality: zero hard issues across 66 files. Reachability: 1,200 actions,
  273 known orphans. Compilation, diff, and worktree safety checks pass.
- No confirmed defect remains queued. The four creative-direction questions in
  `memory-bank/archive/2026-07/resolved-queues/design-gaps-overnight-2026-07-16.md`
  are design-resolved, and their four pending implementations are recorded in
  `memory-bank/future-work-kanban.md`.

## Achievement semantics foundation (2026-07-16)

- Integrated into `main` at `a0f5da4` under the repository's direct-main
  workflow.
- Classified all 168 achievements and replaced 70 action-worded Bank snapshot
  predicates with durable action-owner production progress.
- Added config v37 migration from the maximum of available telemetry history and
  current relevant holdings while preserving completed achievement names.
- Kept true Hold/Own achievements live, made finished-potion holdings invariant
  across vial doses, mixes, flasks, and Bob Barter decanting, and excluded
  Runecrafting tiaras from rune production totals.
- Defined cross-skill ownership at the action surface: Magic Superheat does not
  count as Smithing production, Construction tablets remain Construction-owned,
  and Inferno-adze logs remain Woodcutting-owned.
- Added focused unit, migration, runtime, integration, end-to-end, and undo
  regressions. The core suite ran 1,323 methods: 1,127 ordinary passes, 193
  environment skips, and three documented expected failures. The real
  offscreen Qt suite ran 1,323 methods: 1,320 ordinary passes and the same three
  expected failures, with no skips.
- Test quality reports zero hard issues across 66 files. The 1,200-action
  reachability baseline remains unchanged at 273 known orphans (110 root, 163
  cascade); compilation, diff, and worktree-safety checks pass.
- Published the self-contained closure report at
  `memory-bank/status-updates/achievement-semantics-results-2026-07-16.html`.
  Diary-gear cadence and acquisition remain a separate owner grill rather than
  an implicit part of this semantics repair.

## Slayer Duradel/Lapalok source harvest (2026-07-17)

- Reconciled 35 cutoff ordinary families and a provisional 334-point hidden
  weight denominator from 34 Darkan rows plus a labeled 10-point Scabarite
  abstraction.
- Pinned Combat 100, Slayer 50, Shilo Village access, 15/75/225 points,
  Duradel-to-Lapalok succession after While Guthix Sleeps, and the 69-kill
  Slayer Tower challenge with no per-kill Slayer XP.
- Resolved Scabarites to the observed cutoff `40–79`, corrected Kalphites to
  `130–200`, and kept four late-family count ranges explicitly provisional
  where the historical generator remains source-blocked.
- Kept the master runtime-hidden at 0/35 readiness rather than renormalizing a
  partial pool around missing families and mechanics.
- Restored Abyssal-demon source quantity distributions and the global Rare
  table, and removed the Kuradal's Dungeon-only Ferocious-ring drop from the
  generic target without changing other drop probabilities.
- Added deterministic Combat regressions for the repaired quantities, Rare
  branch and context-specific exclusion. All 345 focused holdouts and all
  1,369 core methods pass, with 196 environment skips and the three declared
  XP-parity expected failures; test quality remains at zero hard issues.
  Summoning and Dungeoneering remained outside the batch.

## Slayer Kuradal source harvest (2026-07-17)

- Reconciled 36 cutoff ordinary families and a provisional 322-point hidden
  weight denominator from 35 Darkan rows plus a labeled 10-point Terror-dog
  abstraction.
- Mapped Darkan's `VOLCANIC_CREATURES` row to ordinary TzHaar, kept the
  280-kill Fight Cave challenge separate, and resolved nine count conflicts
  from the direct cutoff master ledger.
- Pinned Combat 110, Slayer 75, Ancient Cavern access, 18/90/270 points,
  Aquanite and ice-strykewyrm reward gates, Kuradal's Dungeon/Ferocious-ring
  consequences, and the no-bonus-points Fight Cave challenge.
- Kept Kuradal runtime-hidden at 0/36 readiness rather than renormalizing a
  partial pool around absent families, contexts and mechanics.
- Restored the live level-149 TzHaar-Ket's cutoff 136 Slayer XP after a focused
  regression reproduced the missing field. All 345 focused holdouts and all
  1,369 core methods pass, with 196 environment skips and the three declared
  XP-parity expected failures; test quality remains at zero hard issues.
  Summoning and Dungeoneering remained outside the batch.

## Slayer Cockatrice and Banshee protective equipment (2026-07-17)

- Pinned the cutoff Mirror-shield trigger, fixed eye-beam hit, one-quarter stat
  floor, item identity, slot, equip gate, and Slayer-shop acquisition.
- Reconciled the hidden damage function as the smallest labeled mapping:
  Darkan's maximum-LP/6 fixed hit capped at the period page's 110 LP.
- Reconciled the repeated drain from the period one-quarter floor and
  2011Scape's 25%-of-base Attack, Strength, Defence, Ranged, and Agility set.
- Added the data-driven Combat consequence, fixed-hit/prayer bypass, persistent
  current-level drains, ordinary food/death/retreat/undo integration, and a
  non-blocking target warning.
- Added Banshee's complete head-slot protection family, fixed maximum-LP/10
  scream capped at 80 LP, and the period-proven eight affected skills.
- Reconciled the unresolved drain rule as the smallest labeled abstraction:
  Darkan's flat five-level magnitude applied to the period's complete skill set,
  floored at level 1. Summoning is now implemented and no longer a dependency
  blocker.
- Verification passes 236 focused Combat/roster/metadata tests, one real
  offscreen Qt picker check, and all 1,485 current core methods with 203 skips.
  Test quality has zero hard issues and no new clone group; documentation,
  compilation, diff and worktree-safety checks pass.

## Slayer finisher-item acquisition metadata (2026-07-17)

- Reproduced a generated-data loss where shop-only items discarded their
  source item IDs and defaulted to stackable in the shared registry.
- Preserved stock-row `source_item_id` and `stackable` through the generated
  helper, including the generator template so regeneration cannot erase the
  repair.
- Pinned Bag of salt 4161 as stackable, Rock hammer 4162 as non-stackable, Ice
  cooler 6696 as stackable, and Fungicide spray 10 7421 as non-stackable.
- Passed 167 shop/registry/integration methods and three real offscreen Qt shop
  flows. Reachability remains at 1,200 actions and 273 known orphans.
- At this checkpoint all four finisher families remained hidden: target data,
  context-correct drops, enemy assets, and reachable finisher runtime were not
  yet jointly certified.

## Slayer Desert lizard and generic finisher runtime — 2026-07-17

- Added the cutoff level-24 Desert lizard with Slayer 22, 250 LP, maximum hit
  40 LP, 25 Slayer XP, reconciled Darkan stats, guaranteed Bones, and one exact
  100,000-slot source-probability drop selector.
- Added a generic loaded-finisher pack and manual action. Lethal damage holds a
  required target at 1 LP; the valid action atomically spends one Ice cooler,
  awards the kill/drops, clears the encounter, and resets to Attack.
- Added the 400-point automatic-finisher seam. It still requires and consumes
  the item, supports player-side lethal damage sources, and cannot spend a
  second item after the target is already dead.
- Flattened Desert heat into a labeled, wall-clock-free supply rule: one
  Waterskin dose per damaging Combat review. Dose remainders, eight-skin pack
  loading, carried-slot cost, depletion, and the existing two-review bank run
  are executable. Exact historical heat interval/damage remains
  `source_blocked`.
- Added a sourced 48px sprite/provenance row, tooltip and pack legibility,
  persistence migration, runtime telemetry, and real offscreen Qt action-state
  coverage.
- Kept every incomplete Slayer master hidden. This certifies Desert lizards as
  a family dependency and makes the finisher engine reusable by Rockslug,
  Gargoyle, and Mutated zygomite; it does not renormalize a master pool.
- Durable evidence:
  `source-audits/slayer-desert-lizard-combat-2026-07-17.md`.
- Final verification: 1,497 core methods (1,293 ordinary passes and 204
  expected environment skips), 1,497 real offscreen Qt ordinary passes, zero
  hard test-quality issues, and passing documentation, compilation, diff,
  item-reachability, and worktree-safety audits.

## Slayer Rockslug and Gargoyle Combat slices — 2026-07-17

- Added Rockslug with Slayer 20, 270 LP, maximum hit 41, exact 27 Slayer XP,
  the cutoff 1–39 LP Bag-of-salt finisher, and a latched 10-LP
  frozen/no-retaliation state.
- Added Gargoyle with Slayer 75, 1,050 LP, maximum hit 119, exact 105 Slayer
  XP, the cutoff below-90 LP reusable Rock-hammer action, and continuous
  regeneration represented as `12/5` LP per gameplay tick with a persisted
  integer residual.
- Reconciled one Darkan ordinary selector per target with separate 2011Scape
  charm tables. The ordinary Gargoyle target excludes the
  Kuradal's-Dungeon-only Ferocious ring.
- Corrected Combat supply refill so changing targets returns obsolete finisher
  and hazard supplies, loads one copy of a reusable non-stackable tool, and
  counts non-stackable finisher slots accurately.
- Added period RuneScape Wiki icons and changed the Combat asset fetcher to
  prefer RuneScape Wiki files over same-named OSRS fallbacks.
- Focused backend verification passes 374 methods and the real offscreen Qt
  action/picker check. The complete core suite passes 1,504 methods, with 1,300
  ordinary passes and 204 declared environment skips. All 200 real main-menu
  widget tests pass. Their harness now flushes deferred dialog deletion after
  each test, reducing the measured peak resident memory from 9.7 GB to 1.22 GB
  and removing the pathological application-style recomputation tail. The
  complete real offscreen Qt suite passes all 1,504 methods without skips or
  failures in 490.6 seconds.
- Durable evidence:
  `source-audits/slayer-rockslug-gargoyle-combat-2026-07-17.md`.
- Results artifact:
  `status-updates/slayer-rockslug-gargoyle-results-2026-07-17.html`
  (<https://887yman86rqy.postplan.dev>).

## Grill-harvest program closure (2026-07-17)

- Completed all four owner-approved post-closure amendments.
- Reconciled all seven functional Slayer-master pools and implemented every
  source-ready atomic repair found during this bounded harvest.
- Closed the remaining Slayer runtime as explicit source/dependency work
  rather than exposing incomplete masters or dead feature code.
- Final core discovery: 1,376 methods, 1,177 ordinary passes, 196 skips, and
  three expected failures.
- Final real offscreen Qt discovery: 1,376 methods, 1,373 ordinary passes, no
  skips, and three expected failures.
- Documentation, test quality, compilation, JSON, diff, reachability, and
  worktree-safety gates all pass.
- Published `status-updates/grill-harvest-results-2026-07-17.html` and its
  mobile-safe copy at <https://co9e6hzqn0pd.postplan.dev>.

## Stolen Hearts quest dependency — 2026-07-17

- Replaced all five generated objective placeholders with a playable,
  source-backed quest chain covering the Skulls infiltration, Khnum pursuit,
  three mercenary fights, temporary-item custody, rooftop/treasury traversal,
  Het's scales, the Kharid-ib, and Osman's handoff.
- Corrected the generated rewards by removing the bogus Khnum item and
  separating direct 250 Constitution XP from the three authentic 250-XP lamp
  claims; the quest now awards 2,500 coins and preserves its three quest
  points.
- Registered rev-742 item identities 25127 and 25128, added the two
  period-named quest-item icons with provenance, and removed one statless
  Combat row from the catalog debt ledger.
- Added pure, live-dispatch, source-contract, asset, and real offscreen Qt
  regressions. The complete core suite passes all 1,508 methods with 1,303
  ordinary passes and 205 declared environment skips; the complete real
  offscreen Qt suite passes all 1,508 methods without skips or failures.
  Test-quality, documentation, compilation, diff, quest-audit, asset, and
  worktree-safety gates pass. Diamond in the Rough is next.
- Published `status-updates/quest-stolen-hearts-results-2026-07-17.html` and
  its mobile-safe copy at <https://4sptl2883909.postplan.dev>.

## Diamond in the Rough quest dependency — 2026-07-17

- Replaced four generated objective placeholders with a playable chain
  covering the Heavy weight, six-enemy sundial ambush, Sundial gnomon,
  quicksand/Kalphite nursery, three retained gems, Apep/Heru finale, and Prince
  Ali rescue.
- Corrected the reward parser boundary: ordinary completion grants 250
  Agility, Constitution, and Thieving XP plus the existing Combat lamp; the two
  optional 20,000-XP level-80 fissure actions are no longer auto-awarded.
- Registered rev-742 item identities 25116 and 25118, installed their original
  September 2012 sprites with provenance, and reduced the statless quest
  Combat ledger from 102 to 98 rows.
- Added source-contract, pure full-chain, live-dispatch, asset, and real
  offscreen Qt regressions. The complete core suite passes all 1,512 methods
  with 1,306 ordinary passes and 206 declared environment skips; the complete
  real offscreen Qt suite passes all 1,512 methods without skips or failures.
  Test-quality, documentation, compilation, diff, quest-audit, asset,
  reachability, and worktree-safety gates pass. Icthlarin's Little Helper is
  next.
- Published
  `status-updates/quest-diamond-in-the-rough-results-2026-07-17.html` and its
  mobile-safe copy at <https://6vqmrgu0eo7j.postplan.dev>.

## Icthlarin's Little Helper quest dependency — 2026-07-17

- Replaced the generated placeholders and statless Combat rows with a playable
  nine-step quest chain covering hypnosis, canopic-jar custody, the Sphinx
  riddle and token, exactly one jar-bound guardian, the Sophanem ceremony, both
  quest symbols, the Possessed Priest, and the final report.
- Split the guardian and priest fights from their adjacent inventory
  transactions. The canopic jar and unholy symbol now leave the carried pack
  before Combat, while ceremony supplies are required only after the guardian
  dies.
- Preserved exact ordinary rewards: two quest points, 4,500 Thieving XP, 4,000
  Agility XP, 4,000 Woodcutting XP, and one Catspeak amulet. Priest drops remain
  explicit implementation/source debt because the quest encounter schema has
  no drop transaction and the random potion distribution is not pinned.
- Registered seven period quest-item icons with pre-cutoff provenance and
  extended the reusable asset fetcher with cutoff-aware historical file
  revision lookup.
- Added source-contract, complete pure-chain, live-dispatch, registry, asset,
  quest-debt, and real offscreen Qt regressions. The complete core suite passes
  all 1,517 methods with 1,310 ordinary passes and 207 declared environment
  skips; real offscreen Qt discovery passes all 1,517 methods without skips or
  failures. Smoking Kills is now complete; Contact! was not a cutoff
  prerequisite.
- Durable evidence:
  `source-audits/quest-icthlarins-little-helper-playable-2026-07-17.md`.
- Published
  `status-updates/quest-icthlarins-little-helper-results-2026-07-17.html` and
  its mobile-safe copy at <https://llzbgu6xic8d.postplan.dev>.

## Slayer Turael/Spria runtime closure — 2026-07-17

- Activated the first complete Slayer master role from the reconciled
  23-family Turael/Spria pool.
- Added Gelatinous abomination, Young grotworm, and Monkey as executable Combat
  representatives with period stats, Slayer XP, drops, and assets.
- Implemented the worn-only reusable Spiked-gauntlet finishing rule and
  recovered item `23035` across all eight Slayer shops even though the legacy
  item source omits it.
- Registered Coral bolts and Royal cape as source-backed equipment drops with
  their period identities, stackability, tradeability, slots, bonuses, and
  pinned sprites.
- Added assignment, Combat-credit, migration, undo, task-filter, hub, shop
  generator, and real offscreen Qt regression coverage. Complete core discovery
  passes 1,537 methods with 1,326 ordinary passes and 211 declared environment
  skips; complete real offscreen Qt discovery passes all 1,536 methods without
  skips or failures, with the latest item-only seams covered by a targeted
  holdout.
- Fable's bounded UI review found no wiring or dark-mode defects and surfaced
  two real copy problems: internal readiness jargon and a task-filter dead-end
  message. Both are fixed.
- No new design gap emerged. Smoking Kills is now complete.
- Published
  `status-updates/slayer-turael-runtime-results-2026-07-17.html`
  (<https://5k6wxpak7xkj.postplan.dev>).

## Smoking Kills playable Slayer dependency — 2026-07-18

- Replaced four generated placeholders, the malformed grouped combat parser
  row, and six bogus completion-item rewards with a playable thirteen-journal
  quest whose twelve requirements cover both tomb wings, both Mummy Warriors
  and path keys, Catolax's Masked-earmuffs transformation, the Mighty banshee
  and voice, the barrier, the Banshee Mistress, and Sumona's report.
- Kept the period half-health assassin phase visible while collapsing its four
  temporary adds into the one boss battle they actually support. Tomb waves,
  Mummy hidden stats, and the Banshee voice rate use explicit bounded
  abstractions where the period evidence is `source_blocked`.
- Added optional quest-combat `minimum_player_combat` metadata. Smoking Kills
  therefore shows its level-90 and level-111 enemies while retaining the
  quest's sourced Combat 85 player gate; every existing encounter keeps its
  prior default.
- Canonicalized the Restless Ghost reward name to the already-live
  `Ghostspeak amulet`, registered cache identities 552, 1555, 13259, 13260,
  13276, and 13277, generated real neck/head equipment rows, and pinned five
  pre-cutoff quest sprites.
- Completion grants exactly one quest point and 5,000 Slayer XP. Sumona and the
  existing reward surface become reachable, while `slayer_points` and
  `slayer_qualifying_streak` remain unchanged so no pre-quest task earns
  retroactive points.
- A bounded Fable UI/copy review approved the fixed tomb order and stage
  density, and caught the hidden Combat-111 player gate plus four presentation
  hazards. All reproduced findings were fixed; no owner-level design gap
  emerged.
- Focused catalog, pure, integration, registry, equipment, debt-ledger, and
  real offscreen Qt checks pass. Full core discovery passes 1,542 methods with
  1,330 ordinary passes and 212 declared environment skips; full real offscreen
  Qt discovery passes all 1,542 methods without skips or failures.
- Test-quality audit reports zero hard issues across 72 files. Documentation
  audit passes 279 Markdown and 315 HTML files. Reachability is 1,220 actions,
  1,789 reachable items, 288 orphan inputs, and 314 blocked actions; this batch
  introduces no orphaned Smoking Kills stage item. Compilation, provenance
  JSON, combat-debt, diff, and worktree-safety checks pass.
- Durable evidence:
  `source-audits/quest-smoking-kills-playable-2026-07-18.md`.
- Published
  `status-updates/quest-smoking-kills-results-2026-07-18.html`
  (<https://0hj7sz8kn416.postplan.dev>).
- The next Slayer implementation dependency is Shilo Village and the complete
  transitive black-mask / Slayer-helmet route.

## Shilo Village playable Slayer dependency — 2026-07-18

- Replaced seven generated objective buttons with eleven review-native
  requirements plus the completion sentinel, covering Ah Za Rhoon, Zadimus,
  Bervirius, every quest-item transformation, Rashiliyia's tomb, and her release.
- Replaced the generated single boss placeholder with ordered level-91 zombie,
  level-68 skeleton, and level-93 ghost encounters using complete Darkan
  resolver definitions.
- Registered all thirteen rev-742 quest-item identities and pre-cutoff sprites;
  Beads of the dead now generate as real neck equipment.
- Preserved the period-optional Stone-plaque without making it a progression
  gate. The collapsed temple review includes the item automatically, and the
  UI does not promise Yanni's separate post-quest sale service.
- A bounded Fable UI/copy review accepted the route and found five concrete
  seams. Optionality wording, absent-sale wording, the pre-quest supply list,
  Ah Za Rhoon geography, and the cache citation are all corrected.
- Full core discovery passes all 1,546 methods with 213 declared environment
  skips. Full real offscreen Qt discovery passes all 1,546 methods without
  skips or failures. The final 355-method focused backend set and three-method
  real Qt holdout also pass.
- Test quality reports zero hard issues across 72 files. Documentation,
  compilation, provenance JSON, combat-gap, diff, reachability, and worktree
  safety audits pass; the known reachability ledger remains 1,220 actions,
  1,789 reachable items, 288 orphan inputs, and 314 blocked actions.
- Durable evidence:
  `source-audits/quest-shilo-village-playable-2026-07-18.md`.
- Published
  `status-updates/quest-shilo-village-results-2026-07-18.html`
  (<https://tqgeemw7wsuo.postplan.dev>).
- Next: repair Jungle Potion's remaining generated stage buttons, then continue
  Big Chompy Bird Hunting → Zogre Flesh Eaters → Rum Deal → Cabin Fever before
  the Mos Le'Harmless, Cave horror, Black mask, and Slayer-helmet runtime.

## Wall beast playable Slayer target — 2026-07-18

- Added the ordinary level-49 Wall beast with cutoff combat identity, Slayer
  gate/XP, maximum hit, Darkan stats/respawn, a reconciled 100,000-slot drop
  table, and its pre-cutoff icon.
- Added a reusable start-only equipment gate. Spiny helmet is checked when a
  fight begins, not on every attack; an active beast survives a legal helmet
  swap, while the next spawn again requires the helmet.
- Enforced the cutoff poison immunity against the existing Ancient Smoke-spell
  poison effect.
- Reused every existing canonical item identity, including cache item 4544 as
  `Bullseye lantern (unf)` and item 4089 as `Mystic hat`; no parallel registry
  names were introduced.
- Mazchna/Achtryn now derives at 24/27 ready families. Cyclopes, Mogres, and
  Vampyres are the remaining exact blockers.
- Focused pure and real offscreen Qt checks pass. Complete core discovery passes
  all 1,570 methods with 213 declared environment skips; complete real
  offscreen Qt discovery passes all 1,570 methods without failures or skips.
- Durable evidence:
  `source-audits/slayer-wall-beast-combat-2026-07-18.md`.
- Published
  `status-updates/slayer-wall-beast-combat-results-2026-07-18.html`
  (<https://0aaltfsrmyrn.postplan.dev>).

## Slayer Mogre source closure and quest handoff — 2026-07-18

- Closed the ordinary level-60 Mogre combat contract from cutoff Wiki
  revisions and Darkan: Slayer 32/48 XP, atomic Fishing-explosive lure,
  poison immunity, exact melee cadence and damage, a 128-slot main drop table,
  guaranteed Big bones, and independent long/curved-bone tertiaries.
- Recovered the complete non-combat Skippy supply chain and its sole gameplay
  reward. The live Slayer family already names the correct completion ID,
  `skippy_and_the_mogres`, but the quest catalog does not implement it.
- Kept Mazchna/Achtryn at 24/27 rather than adding a permanently locked partial
  Combat target. The exact quest implementation handoff is appended to
  `codex-briefs/darkan-quest-agent-handoff-2026-07-18.md`.
- Recorded missing Mudskipper hat/Flippers identities and icons, the optional
  Super fishing explosive acquisition dependency, and the Rag and Bone Man
  context restriction without inventing routes or weights.
- No owner design decision was required. Durable evidence:
  `source-audits/slayer-mogre-combat-2026-07-18.md`.

## Feral vampyre playable Slayer target — 2026-07-18

- Added the ordinary level-61 Feral vampyre with cutoff combat identity,
  Priest in Peril access, 40 Slayer XP, 74-LP maximum hit, Darkan
  stats/respawn, a guaranteed Vampyre dust drop, and a losslessly reconciled
  100,000-slot table.
- Added data-declared weakening-equipment behavior. Wearing the existing
  ordinary Holy symbol reduces the Vampyre's enemy accuracy and maximum hit by
  20% in both preview and live Combat.
- Added the source-described occasional bite using a labeled bounded
  abstraction: 1/8 of landed damaging attacks, at most 20 LP healed, and one
  random implemented skill drained by one current level.
- Installed the pre-cutoff level-61 historical sprite with provenance and
  exposed the weakness and bite outcome on the existing Combat UI/runtime
  surfaces.
- Mazchna/Achtryn now derives at 25/27 ready families. Mogres wait on the
  Darkan-owned Skippy miniquest; Cyclopes wait on the full Warriors' Guild
  activity rather than a context-free Combat row.
- Focused pure coverage passes 332 methods and the focused real offscreen Qt
  picker surface passes. Complete core discovery passes all 1,574 methods with
  213 declared environment skips; complete real offscreen Qt discovery passes
  all 1,574 methods without failures or skips.
- Durable evidence:
  `source-audits/slayer-feral-vampyre-combat-2026-07-18.md`.
- Published
  `status-updates/slayer-feral-vampyre-results-2026-07-18.html`
  (<https://v0w3h4u00jo4.postplan.dev>).

## Aberrant spectre playable Slayer target — 2026-07-18

- Added the ordinary level-96 Aberrant spectre with its Priest in Peril and
  Slayer-60 gates, 900 LP, 90 Slayer XP, six-tick Magic cadence, and exact
  protected/unprotected hit behavior.
- Added a data-declared stench rule: Nose peg and Slayer helmets protect
  completely; otherwise max-LP/10 damage always lands while Protect from Magic
  blocks only the random five-level combat-stat drain.
- Encoded Darkan's ten weighted ordinary rows as its executable 512-slot
  mutually exclusive selector, plus exact nested herb, rare-seed, gem, and
  mega-rare tables and the independent 1,212-way charm selector.
- Generated Mystic robe bottom (dark) as real legs equipment and installed
  provenanced sprites for the target, Mystic bottom, and Vecna skull.
  Regeneration also repaired the latent Adamant spear and Black dagger (p)
  equipment rows from the preceding Shadow-warrior slice.
- Vannaka now derives at 25/35 ready families. Nine Combat targets plus Earth
  warrior's Wilderness-risk behavior remain; the master stays hidden and
  unrenormalized. No quest files were touched and no owner design gap emerged.
- Durable evidence:
  `source-audits/slayer-aberrant-spectre-combat-2026-07-18.md`.
- Focused pure/registry coverage passes 331 checks and the real offscreen Qt
  picker regression passes. Full discovery runs 1,614 methods: 1,400 ordinary
  passes and 214 declared skips.
- Published
  `status-updates/slayer-aberrant-spectre-results-2026-07-18.html`
  (<https://fr3fmom6akth.postplan.dev>).

## Slayer Fungal-mage source boundary — 2026-07-19

- Closed the cutoff-visible Fungal-mage contract: level 120, 1,200 LP,
  Slayer 1/120 XP, Magic-50 assignment gate, six-tick Magic, 114-LP maximum,
  poison immunity, 2–3-LP proximity infestation, and the roughly 20-second
  Neem-oil weakening loop.
- Pinned rev-742 NPC/item identities and Darkan's combat, infestation, oil,
  drops, cache bonuses, and exact 606-slot charm lead.
- Kept the target blocked because Darkan's `nostats` definition explicitly
  generates non-real combat levels, the period sources conflict on the exact
  Melee/Ranged reducer, the ordinary sources disagree on two quantities, and
  the canonical Neem-drupe/jug/oil acquisition chain is not live.
- Chaeldar remains hidden and unrenormalized at 25/34. No owner design fork was
  reopened. Durable evidence:
  `source-audits/slayer-fungal-mage-combat-2026-07-19.md`.

## Slayer Grifolic-creatures source boundary — 2026-07-19

- Closed the period-visible Grifolapine and Grifolaroo identities, Slayer and
  Magic gates, hybrid attacks, fungal hazards, neem transitions, client IDs,
  and named resource/drop sets.
- Kept both targets blocked because their Darkan `nostats` rows explicitly
  generate non-real combat levels; Grifolaroo also conflicts on LP/maximum,
  Grifolapine conflicts on infestation damage, and the shared handler never
  performs the cutoff Magic-to-Ranged neem transition.
- Confirmed the two Darkan ordinary-drop files are duplicated reconstruction
  stubs despite the cutoff monsters having materially different tables.
- Chaeldar remains hidden and unrenormalized at 25/34. No owner design fork was
  reopened. Durable evidence:
  `source-audits/slayer-grifolic-creatures-combat-2026-07-19.md`.

## Slayer Jungle-strykewyrm source boundary — 2026-07-19

- Closed the period-visible Jungle-strykewyrm identity, Slayer-73
  assignment-only gate, hybrid attack cadence, poison families, tunnelling
  concept, client IDs, and named drop set.
- Kept the target blocked because Darkan's `nostats` row generates non-real
  combat levels and its custom handler contradicts the cutoff melee-poison and
  burrow damage/poison consequences.
- Confirmed the ordinary-drop reconstruction conflicts with visible cutoff
  coin, Papaya-fruit, and herb quantities, while the current one-channel
  poison schema cannot represent three attack-conditional poison outcomes.
- Chaeldar remains hidden and unrenormalized at 25/34. No owner design fork was
  reopened. Durable evidence:
  `source-audits/slayer-jungle-strykewyrm-combat-2026-07-19.md`.

## Slayer Kurask source boundary — 2026-07-19

- Closed the complete real combat row, Slayer-70 gate/97 XP, aggressive
  six-tick melee, 120-LP maximum, cache bonuses, respawn, and every effective
  leaf/broad/Magic-Dart route.
- Confirmed the existing Turoth `restricted_weapon` seam can represent the
  settled Kurask kill loop without new design.
- Kept the target blocked because Darkan's ordinary selector conflicts with
  visible cutoff quantities, most clearly 20 noted Big bones against one or
  two ordinary Big bones, and fails to preserve the complete named drop set.
- Chaeldar remains hidden and unrenormalized at 25/34. No owner design fork was
  reopened. Durable evidence:
  `source-audits/slayer-kurask-combat-2026-07-19.md`.

## Slayer Troll registry stop — 2026-07-19

- Stopped before implementing Trolls because the settled broad-category
  contract and pool audit require explicit stable mountain/ice/river/undead
  membership, while `slayer_data.py` binds the complete family to only
  `("troll",)`.
- Confirmed one generic target would make readiness falsely certify the whole
  category and that Darkan's substring/name-fragment row cannot supply the
  required stable boundary.
- Made no runtime, variant, asset, or test changes. Chaeldar remains hidden and
  unrenormalized at 25/34. Durable conflict report:
  `audits/slayer-troll-registry-conflict-2026-07-19.md`.

## Slayer Vyrewatch and Warped-tortoise source boundaries — 2026-07-19

- Closed cutoff-visible identities, gates, combat concepts, restricted/chime
  interactions, cache identities, and named drops for both remaining
  independent Chaeldar families.
- Kept Vyrewatch blocked on the incomplete broad-family registry, conflicting
  level-110 maximum/drop data, uncorroborated hidden levels, and a
  quest-granted Ivandis flail which is not executable as Combat equipment.
- Kept Warped tortoise blocked on generated non-real combat levels, the
  106/120 maximum conflict, absent Crystal-chime handler/acquisition action,
  and a selector which conflicts with or omits major cutoff rows.
- Added a second durable registry-authority report for Vyrewatch rather than
  allowing one representative to falsely certify its multi-variant family.
- Read-only Workflow `338d915a-364d-4e18-aa81-8ab4531c01b8` was canceled
  without using either leaf: the Warped-tortoise leaf produced no telemetry,
  while the Vyrewatch leaf expanded to 135,162 tokens without a final report.
  The primary independently reproduced every recorded source and code finding.
- Chaeldar remains hidden and unrenormalized at 25/34. Evidence:
  `source-audits/slayer-vyrewatch-combat-2026-07-19.md`,
  `source-audits/slayer-warped-tortoise-combat-2026-07-19.md`, and
  `audits/slayer-vyrewatch-registry-conflict-2026-07-19.md`.

## Slayer Sumona hidden-pool encoding — 2026-07-19

- Encoded all 37 source-settled Sumona rows and their provisional 407-point
  denominator without activating the incomplete master.
- Added stable family identities for the 14 families first needed above
  Chaeldar, preserving Slayer gates and distinctive readiness features rather
  than allowing generic Combat rows to certify missing mechanics.
- Derived 18/37 families ready from current Combat data. Abyssal demon remains
  blocked on teleport interruption and Nechryael on Death spawns; 17 other
  families still report `combat_target`.
- Preserved Combat 85, Slayer 35, and the playable Smoking Kills completion
  gate. Eligible-family generation remains empty while Sumona is hidden, so no
  partial table can be rolled or silently renormalized.
- Added regression coverage for the complete row count, denominator, unusual
  count ranges, master gates, exact blocker ledger, and hidden-role behavior.
- Verification: `tests.test_slayer_logic` passes 17 tests; the focused
  Slayer/quest integration slice passes 19 tests; real offscreen Qt coverage
  passes 2 focused tests and the complete 1,681-test discovery suite. The core
  runner passes 1,681 tests with 215 environment skips. Documentation,
  test-quality, compile, readiness, diff, and worktree audits pass. The
  repository-wide reachability audit retains its pre-existing orphan/action
  backlog and reports no Sumona-specific item regression.
- Codex Workflows run `9e94a9cc-ea1b-448b-b432-19cce62202b5` produced no
  review result: one Sol-high leaf timed out after 540 seconds and the second
  never established a session before the 600-second run timeout. Its telemetry
  was not used as evidence; the root independently reproduced and verified the
  complete slice.
- Results artifact:
  `status-updates/slayer-sumona-hidden-pool-results-2026-07-19.html`
  ([mobile copy](https://c00hpkv6e9ws.postplan.dev)).

## Slayer Abyssal/Nechryael special-mechanic harvest — 2026-07-19

- Pinned the cutoff Abyssal teleport behavior and Nechryael/Death-spawn roster
  behavior from exact pre-EOC revisions and checked their last relevant
  pre-cutoff talk revisions.
- Kept both families non-certifying. Abyssal teleport chance and interruption
  magnitude remain source-blocked. Nechryael summon probability and spawn
  lifetime remain source-blocked.
- Recorded the emulator conflict instead of resolving it: Darkan removes Death
  spawns when the summoner dies, while the cutoff strategy text describes
  killing the Nechryael before handling or avoiding the surviving spawn.
- Located the future implementation inside the pure Combat burst transaction
  and the settled engaged-target plus pressure-roster contract. No global map,
  wall clock, partial special loop, or owner design fork was introduced.
- Read-only Workflow `3c11e193-9b94-48cd-9e02-5d6bb15c4101` was canceled
  without using either leaf. The Abyssal leaf expanded to 85,033 generated
  tokens and remained stuck in a wait without a final report; the Nechryael
  leaf never established a session and emitted no telemetry. The primary
  independently reproduced every accepted source finding.

## Slayer Iron dragon Combat target — 2026-07-19

- Added the ordinary level-189 Iron dragon as Sumona's nineteenth certifying
  family, preserving 1,650 LP, 173.2 Slayer XP, six-tick attacks, and the
  existing bounded metal-dragon dragonfire model.
- Imported Darkan's exact Combat stats, defences, 59-tick respawn, guaranteed
  Dragon bones and five Iron bars, the 128-slot ordinary selector including
  its explicit empty slot, a losslessly enumerated quantity-two charm table,
  and independent plate, visage, and hard-clue rolls.
- Added the pre-cutoff target image and provenance plus roster, selector,
  readiness, and real offscreen Qt coverage.
- Sumona now derives 19/37 families ready and remains hidden and
  unrenormalized. No owner-facing design gap emerged.
- Verification: 319 focused Slayer/Combat tests pass; the real offscreen Qt
  Combat-target/tooltip check passes; the complete core runner passes 1,683
  tests with 215 environment skips. Documentation, test-quality, compile,
  provenance JSON, readiness, diff, and worktree audits pass. The
  repository-wide reachability audit retains its known 288-orphan/313-blocked
  backlog and reports no Iron-dragon-specific regression.
- Results artifact:
  `status-updates/slayer-iron-dragon-results-2026-07-19.html`
  ([mobile copy](https://za9osdb8btx6.postplan.dev)).

## Slayer Red dragon family Combat targets — 2026-07-19

- Added the ordinary level-152 Red dragon and level-48 Baby red dragon as
  Sumona's twentieth certifying family, preserving the cutoff substitution
  relationship and adult-only dragonfire.
- Preserved the direct period adult maximum of 158 LP and recorded Darkan's
  conflicting 144-LP value as a rejected lower-tier lead rather than silently
  selecting the convenient emulator value.
- Imported exact executable combat levels, defences, respawns, guaranteed
  drops, the adult's 128-slot ordinary table with three real empty slots,
  losslessly enumerated charms, Summoning-gated egg, and hard clue.
- Added both pre-cutoff target images and provenance plus roster, selector,
  readiness, and real offscreen Qt coverage.
- Sumona now derives 20/37 families ready and remains hidden and
  unrenormalized. No owner-facing design gap emerged.
- Verification: 321 focused Slayer/Combat tests pass; the real offscreen Qt
  Combat-target/tooltip check passes; the complete core runner passes 1,685
  tests with 215 environment skips. Documentation, test-quality, compile,
  provenance JSON, readiness, diff, and worktree audits pass. Reachability
  improves from 288 orphan inputs / 313 blocked actions to 286 / 309.
- Read-only Workflow `fe36e1d0-6431-4163-88a3-938428bec3d0` was canceled
  after roughly nine minutes because both Sol-high leaves remained before
  session creation: no worker PID, provider session, stdout/stderr path,
  token, tool, or progress telemetry was ever produced. No partial result was
  used; the primary independently reproduced and verified the complete slice.
- Results artifact:
  `status-updates/slayer-red-dragon-family-results-2026-07-19.html`
  ([mobile copy](https://2365habrkscc.postplan.dev)).

## Slayer Scabaras lancer source boundary — 2026-07-19

- Pinned the cutoff level-112, 900-LP, 90-XP Scabaras lancer with melee,
  approximate 130 maximum, poison behavior, guaranteed Bones, Sumona
  assignment, and explicit Scabarites qualification.
- Confirmed the rev-742 ID and Attack option and harvested Darkan's 59-tick
  respawn, defensive bonuses, denominator-bearing drops, and hard-clue row.
- Kept the target source-blocked because Darkan explicitly marks the combat
  definition `nostats`; the cache cannot supply server levels, and game-main
  has spawn rows but no combat definition. Attack, Strength, Defence, Magic,
  and Ranged remain absent.
- Excluded the post-EOC bestiary row, which conflicts at level 77 and 2,750 LP,
  and did not infer non-roll content from combat level 112.
- Sumona remains hidden and unrenormalized at 20/37. No owner-facing design
  gap emerged.

## Slayer Ice strykewyrm source boundary — 2026-07-19

- Source-closed the ordinary cutoff identity, assignment restrictions,
  quest/cape eligibility, mixed attack families, maxima, spell interactions,
  and visible drop contents.
- Recorded an explicit authority stop: direct period evidence and the settled
  Kuradal audit require Tale-of-the-Muspah completion, while the settled
  Duradel/Lapalok audit and current global family omit it.
- Rejected Darkan's `nostats` fixed-Ranged row as a source of real combat
  levels and documented its custom selector leads, fire/cape conflicts,
  exact emulator charm enumeration, and incomplete independent-drop table.
- Added no partial target or dependency. Duradel/Lapalok remains 14/35; Kuradal
  remains unencoded. Durable evidence is
  `source-audits/slayer-ice-strykewyrm-combat-2026-07-19.md`, with the
  authority mismatch isolated in
  `audits/slayer-ice-strykewyrm-gate-conflict-2026-07-19.md`.

## Hunter tracking/pitfall/rabbit restoration audit — 2026-07-19

- Re-ran the settled Hunter card against Darkan's newly restored tracking,
  pitfall, and White-rabbit implementations plus exact cutoff Hunter, Penguin,
  Jim, and talk-page revisions.
- Closed the visible target tables, tool/item requirements, reward identities,
  authentic quest boundary, approximately `1/4` perfect-fur probability, Jim's
  `+2` Hunter XP, Rabbit-foot stringing XP, and six-bolt Long-kebbit-spike
  conversion.
- Kept the card source-blocked because Darkan provides deterministic ceilings,
  not the required hidden behavior: it omits Penguin tracking, all catch
  curves, pitfall attacks/damage, snare and Ferret loss, and perfect fur.
- Added no Hunter rows, assets, UI, storage, or runtime behavior and introduced
  no creative-design question. The exact boundary is
  `source-audits/hunter-tracking-pitfall-rabbit-restoration-2026-07-19.md`.
- Read-only Workflow `287714b0-bed1-488d-a085-91ad641ede97` was canceled
  without a usable report after one leaf spent 225,142 generated tokens on six
  broad search calls and the other emitted no tool telemetry. No partial output
  was used; the primary independently reproduced the accepted findings.

## Bonfire and Fire-spirit source audit — 2026-07-19

- Reconciled `Update:Bonfires` oldid 5590679, `Bonfire` oldid 6532063,
  `Fire spirit` oldid 6547151, both cutoff talk pages, and Darkan's executable
  Bonfire/Fire-spirit/Cooking implementation.
- Closed visible XP, the official `4%` maximum participant bonus, five-log
  warmth, level-based `1–10%` maximum LP, log durations, `10%` Cooking XP,
  `1/100` Fire-spirit appearance, and visible reward contents.
- Recorded rather than hid the numeric conflicts: the article's `5+` XP column
  computes as `5%` despite its `4%` prose, while Darkan uses `1/500` spirits,
  shortens Teak/Arctic/Mahogany warmth, and diverges from multiple period reward
  quantities.
- Activated no partial runtime because burned-hand odds, spirit reward
  weights/log scaling, same-effect warmth refresh, and the review-batch
  translation remain blocked. No owner-facing creative-design gap emerged.
- Durable evidence:
  `source-audits/bonfire-fire-spirit-source-boundary-2026-07-19.md`.
- Workflow `1a2926ee-6dcb-42bc-801c-116d3f7e5af5` returned no review: its
  bounded Sol-high leaf acquired a slot but never established a provider
  session or emitted tool telemetry before the declared 360-second timeout.
  The primary independently reproduced all accepted findings.

## Bank search/filter implementation — 2026-07-19

- Added the shared catalog search bar to Bank with item-name and category
  matching, matching-header-only rendering, visible/total counts, and a clear
  empty-result state.
- Preserved the flat inventory and ordered Custom-pack state: filtering is a
  presentation-only refresh and cannot reorder or mutate either structure.
- Added a real offscreen Qt regression that exercises name, category, no-match,
  and clear transitions while asserting inventory identity.
- Verified nine focused Bank Qt surfaces plus 163 pure inventory, storage, and
  integration-smoke tests.

## Grand Exchange backend foundation — 2026-07-19

- Extended the reproducible Darkan item-value pipeline with cache
  `canExchange()` extraction and generated 3,271 direct exchangeable identities.
  The live registered intersection currently contains 1,657 rows.
- Added source-provenance catalog construction plus pure eight-slot offer
  placement, escrow, confirmation, cancellation, collection, collect-all, and
  Ironman reducers.
- Added save-version-44 defaults and migration for deterministic market state,
  orders, settings, buy-limit usage, and compact trade-history ownership.
- Buy offers remain fail-closed without period buy-limit data; the remaining
  market tick, review undo, UI, and period harvest work is explicitly recorded
  in `source-audits/grand-exchange-foundation-boundary-2026-07-19.md`.
- Published `status-updates/grand-exchange-foundation-results-2026-07-19.html`;
  mobile copy: `https://svzfn2ylt4dw.postplan.dev`.

## Grand Exchange period price/limit harvest — 2026-07-19

- Added a resumable, retrying historical-wiki generator and committed generated
  per-item price, limit, oldid, timestamp, source date, item-ID, and cache-value
  provenance.
- The live catalog now prefers 1,328 dated period prices and exposes 1,638
  sourced limits. It keeps the cache anchor for 329 unresolved prices and
  refuses buy offers for the 19 identities that collapse multiple period
  variants.
- Recorded all nine aggregate-table versus later item-page limit conflicts and
  applied the nearest-pre-cutoff item revision.
- Durable evidence:
  `source-audits/grand-exchange-period-price-limit-harvest-2026-07-19.md`.
- Published
  `status-updates/grand-exchange-period-harvest-results-2026-07-19.html`;
  mobile copy: `https://fptne6w8pjqm.postplan.dev`.

## Grand Exchange live market reducer — 2026-07-19

- Implemented the deterministic, wall-clock-free hidden-price reducer with
  naturalized liquidity, bounded stochastic partial fills, price improvement,
  directional impact, smooth shocks, buy-limit windows, compact daily VWAP
  history, ±5% guide-price updates, and cache-derived soft High Alchemy
  pressure.
- Added category/required-level/source-role market inputs without changing the
  strict registered/cache-exchangeable eligibility boundary.
- Wired the GE immediately after the shared shop market clock on every answer.
  Existing full review snapshots now make fills, escrow, buy-limit usage,
  guide/trade state, RNG cursor, and the tick atomic under answer undo.
- Added regression coverage for economic conservation, deterministic catch-up,
  offer-creation boundaries, daily windows, dispatch order, and
  fill -> undo -> identical re-answer.
- Durable evidence:
  `source-audits/grand-exchange-market-engine-2026-07-19.md`.
- Published
  `status-updates/grand-exchange-market-engine-results-2026-07-19.html`;
  mobile copy: `https://vngdsej73c0r.postplan.dev`.

## Grand Exchange interface and Bankstanding — 2026-07-19

- Completed the player-facing market with the cutoff-faithful six offer slots,
  Guide / ±5% / custom price controls, registered-item buy search,
  owned-item-only sell search, quantity-one defaults, preview and configurable
  confirmation, queue-age-resetting offer edits, cancel, partial collect,
  collect-all, and Ironman lockout.
- Added the persistent collectible HUD notice and the no-XP Bankstanding
  Economy activity. Material/source exhaustion now warns once and redirects
  future reviews without auto-resuming when stock later arrives.
- Removed the Bankstanding callback's duplicate mid-review save so Farming
  clock advancement, fallback selection, RNG state, persistence, and answer
  undo remain one atomic transaction.
- Superseded every older eight-slot / ±20% clause under
  `grand-exchange-slot-count-supersession-2026-07-19.md`; full implementation
  evidence is
  `source-audits/grand-exchange-interface-bankstanding-2026-07-19.md`.
- Published
  `status-updates/grand-exchange-interface-bankstanding-results-2026-07-19.html`;
  mobile copy: `https://e62v7fq2zr2o.postplan.dev`.

## Cheese-wheel churning and slicing — 2026-07-19

- Implemented the level-48 milk and butter churn routes, including 40.5
  Cooking XP, milk's returned Bucket, the period eight-tick cadence, and the
  cutoff exclusion from Cooking urns.
- Implemented one-review Slice-all with 5-35 Cheese, 4 XP per actual slice,
  level-shaped variable yield, dynamic activity/telemetry output, authentic
  period art, and full answer undo.
- Closed a Kimi K3 plus Fable taste review over all five new UI surfaces in
  this implementation batch. The accepted fixes balance the six GE slots,
  remove false wall-clock/no-op claims, clarify empty and collectible states,
  improve theme contrast and control explanations, and replace the macOS
  grouped-tree gutter artifact with an explicit bold current-target marker.
- Restarted the real macOS Anki application and inspected Cooking,
  Utility/Bankstanding, and the reviewer HUD directly. The live compositor
  confirms the selection, contrast, link, and painted-HUD fixes; Fable's
  recheck of those live captures returned SHIP. The separate offscreen gates
  pass 223 focused UI tests and all 1,745 repository tests.
- The exact historical yield formula remains source-blocked. The live bounded
  model is explicitly calibrated to surviving level-57 and level-99 samples
  rather than presented as recovered game code.
- Durable evidence:
  `source-audits/cheese-wheel-churning-slicing-2026-07-19.md`.
- Published
  `status-updates/cheese-wheel-churning-slicing-results-2026-07-19.html`;
  mobile copy: `https://dcxvx0rn6jgx.postplan.dev`.

## White Tree fruit harvest and run-energy substrate — 2026-07-19

- Implemented the owner-settled post–Garden of Tranquillity White Tree card as
  a permanent special Farming patch with four-fruit capacity, 12 XP per fruit,
  full-run queue integration, and one-fruit-per-answered-card regrowth.
- Added the period 30-LP/17%-run-energy fruit effect, supercompost input, and
  the missing 20%-per-half Summer pie run-energy output.
- Added a bounded run-energy credit against the next moving travel
  transaction. It is capped, preserved across stationary actions, consumed
  atomically, and covered through full answer undo.
- Added canonical item art with explicit provenance plus focused pure, runtime,
  integration, Qt, and real-Anki visual coverage. Headless Qt is not treated as
  proof of macOS Anki rendering.
- Final verification executes 1,751 non-Qt methods with 1,528 ordinary passes
  and 223 environment skips, plus 1,751 passing offscreen Qt methods. Test
  quality, documentation, compile, JSON, diff, and worktree audits are clean;
  the known reachability ledger remains 283 orphan inputs / 304 blocked
  actions.
- Exact fruit regrowth timing remains explicitly source-blocked; diary and
  Beacon Network consequences remain with their owning systems.
- Durable audit:
  `source-audits/white-tree-fruit-harvest-2026-07-19.md`.
- Published
  `status-updates/white-tree-fruit-results-2026-07-19.html`;
  mobile copy: `https://l5sfu4d7m511.postplan.dev`.

## Shrink-me-quick and repository-wide UI asset normalization — 2026-07-19

- Implemented the period level-52, 6-XP Shrink-me-quick recipe with authentic
  item identities, inventory transaction, telemetry, undo, grouped Herblore
  row, registry coverage, and sprites. Grim Tales acquisition and use stay
  with the Darkan quest lane.
- Regenerated the period GE maps so the newly registered Shrunk ogleroot uses
  its dated 39-coin guide price and 100-item four-hour buy limit.
- The reachability ledger is 284 orphan inputs / 305 blocked actions; the one
  new row is the intentionally Darkan-owned Shrunk ogleroot acquisition path.
- Normalized 1,747 padded small sprites across every one of the 29 UI asset
  families. The operation preserves pixel art and aspect ratio; 65 large
  full-frame images remain untouched by design.
- Hardened the download pipeline and added a backend-independent full-corpus
  regression so future fetches cannot recreate padded icon canvases or skip the
  invariant when Pillow is unavailable.
- Fable and Kimi K3 independently returned `SHIP` with no family exclusions.
  A freshly relaunched real Anki process confirmed representative Skills,
  Combat, Shop, Bank, and Equipment rendering after the rewrite.
- Final verification passes 1,760 non-Qt methods (1,536 ordinary passes and 224
  environment skips) and all 1,760 offscreen Qt methods. The test-quality
  audit reports zero hard issues.
- Durable evidence:
  `source-audits/herblore-shrink-me-quick-2026-07-19.md` and
  `audits/ui-asset-normalization-2026-07-19.md`.
- Published
  `status-updates/herblore-ui-assets-results-2026-07-19.html`;
  mobile copy: `https://hhp6on3e5ci5.postplan.dev`.

## Livid Farm source-ready core — 2026-07-19

- Implemented the exact five-round cycle, `6/5` review residual, literal rune
  costs with ordinary staff substitutions, under-level Complete/Conserve
  behavior, five-skill XP, Produce wallet/lifetime accounting, cumulative
  spell unlocks, and the cutoff-correct `850,000` Borrowed Power claim.
- Added the contract's one-per-twelve source-blocked distraction fallback,
  fully seeded selection, exact rune refund/bonus rows, and no-partial-cycle
  funding boundary.
- Added save schema `46`, Utility dispatch/telemetry, review undo coverage,
  grouped target metadata, a compact progress/policy panel, real icon reuse,
  and a deterministic offscreen UI renderer.
- Fable and Kimi K3 reviewed the new surface. Accepted fixes make progress
  segment-relative, force native progress text, tighten the policy selector,
  label the next unlock explicitly, and describe Produce as banked.
- Final verification passes all `1,793` non-Qt methods with `228` expected
  environment skips and all `1,793` real-Qt offscreen methods with one
  intentional skip; test quality reports zero hard issues.
- Real macOS Anki verification confirmed the reloaded activity row and icon;
  the user save remained untouched. Full verification and the results URL are
  recorded in
  `source-audits/livid-farm-core-implementation-2026-07-19.md`.
- Published
  `status-updates/livid-farm-core-results-2026-07-19.html`;
  mobile copy: `https://psq0dddzao84.postplan.dev`.
- Spell consumers, Borrowed Power / Arcane-capacitor commands, and wishes are
  the next settled implementation slices. The two explicitly source-blocked
  wish magnitudes remain unimplemented.

## Livid Farm ordinary Magic consumers — 2026-07-19

- Added exact ordinary Lunar rows for the first ten cumulative Livid Farm
  spell unlocks, including the supported Make Leather output variants.
- Implemented direct South Falador, North Ardougne, and Trollheim Farm
  destinations, Trollheim herb-patch focus, all-patch Remote Farm curing, and
  exact five-hide Make Leather inventory transactions with answer undo.
- Kept Repair Rune Pouch, Spiritualise Food, Disruption Shield, Vengeance
  Group, and Group Trollheim visible but honestly disabled on their unresolved
  pouch, familiar, PvP, or multiplayer consumers.
- Added pure, runtime-integration, Farming-helper, target-metadata, and real
  offscreen Qt coverage. Kimi K3 and Fable reviewed the complete changed
  surface; accepted fixes cover destination/input legibility, output icons,
  disabled-copy language, shown-dialog geometry, and runtime error copy.
- The current reachability ledger is 283 orphan inputs and 300 blocked actions;
  these remain explicit dependency/source boundaries rather than fabricated
  acquisition paths.
- Durable audit:
  `source-audits/livid-farm-spell-consumers-2026-07-19.md`.
- Final verification passes 1,810 non-Qt methods with 230 expected environment
  skips and all 1,810 real offscreen Qt methods with one intentional skip.
  Published
  `status-updates/livid-farm-magic-consumers-results-2026-07-19.html`;
  mobile copy: `https://hbqtpi53phuh.postplan.dev`.

## Long kebbit bolt reward chain — 2026-07-19

- Added the level-42 Chisel route: one Long kebbit spike becomes six Long
  kebbit bolts for `7.98` Fletching XP while preserving the tool.
- Added Leon's period 40-Coin, no-XP alternative as a batchable instantaneous
  Shop service with atomic clamping and direct undo.
- Registered the bolts as level-42 ammunition with `+38` Ranged Strength and
  added exact period Exchange rows for both the bolts and spike.
- Added canonical provenance-tracked sprites and reusable real-Qt renderers
  that follow the repository's shown-dialog/laptop-height capture rule.
- Fixed generic Shop service batching/copy, generic item-conversion
  reachability, and quest-overlay loss of existing non-stackable item
  metadata.
- Fable and Kimi K3 passed the final Fletching and Leon surfaces. The full
  verification and results URL are recorded in
  `source-audits/long-kebbit-bolts-implementation-2026-07-19.md`.
- Complete verification passes all 1,838 non-Qt methods with 235 expected
  environment skips and all 1,838 real offscreen Qt methods with one
  intentional skip. A freshly relaunched macOS Anki process opened one
  AnkiScape dialog and rendered Leon's disabled missing-spike service state
  without invoking a service or review action.
- Published
  `status-updates/long-kebbit-bolts-results-2026-07-19.html`;
  mobile copy: `https://jgg95o5s47si.postplan.dev`.
- Razor-backed kebbit tracking remains source-blocked; no Hunter target or
  free acquisition shortcut was added, and no owner design gap emerged.

## In-product Help Center — 2026-07-20

- Added 18 runtime-readable Markdown topics with stable IDs, structured
  metadata, aliases, tags, related-topic links, internal anchors, and a live
  implemented-skills registry block.
- Added pure corpus validation/search/rendering plus a non-modal Qt Help panel
  shared by Skills, Shop, Grand Exchange, Quests, Bank, Equipment, Stats,
  Achievements, and Settings.
- Reused `CatalogFilterBar` for search and implemented query-preserving
  Back/Forward history, All topics, internal links, missing-ID fallback,
  `F1`, `Alt+Left`, `Alt+Right`, Down-arrow result focus, and two-stage Escape.
- Kimi K3 reviewed the complete UI and every accepted issue was corrected.
  Fable review is still pending because its required fresh quota probe cannot
  access Claude Code's macOS Keychain credential; this is a QA/auth blocker,
  not a design gap.
- A complete Anki quit/relaunch confirmed the real macOS add-on surface and
  interaction path. Full verification passes 1,884 non-Qt methods and 1,884
  offscreen Qt methods; docs, test quality, UI asset normalization, diff, and
  guarded-worktree checks are clean.
- The Help Center is implemented and committed at `b475397`; its required
  Fable sign-off remains blocked by Claude Code's macOS Keychain credential.
  The separate owner-settled target-level `Details` implementation is recorded
  below and carries the same external Fable QA/auth gate.

## Dungeoneering source-ready backend substrate — 2026-07-20

- Pinned the exact 60-floor theme bands, `2f-1` access rule, size grids and
  room maxima, complexity penalties/skill groups, bind ladder and ammo slot,
  all twelve Ring-of-kinship roles and tier costs, Frozen boss gates, door
  families, prestige substitution, and one-token-per-ten-XP rule from literal
  pre-cutoff revisions.
- Added source-backed Heim-crab and Valerian/Weak-ranged starter chains plus
  the complete Coal-bag proof-purchase contract and rev-727/rev-742 item
  identities.
- Added pure deterministic small-floor graphs, one-frontier-room progression,
  death-to-start respawn without erasing floor progress, floor/theme/bind
  helpers, same-theme replay handling, Frozen-boss eligibility, and
  explicit-input payout arithmetic. No wall clock or overworld item leakage is
  involved.
- The skill remains planned. The active/prestige floor-XP curve, death
  coefficient, exact generated room-count distribution, and skill-door
  failure rate/damage remain honestly source-blocked. The eight-room starter
  budget is an explicitly labelled owner-authorised review translation.
- The period Weak-magic row says 21 XP while the quarantined game-main row
  says 23 XP. The starter uses the independently agreeing Weak-ranged chain;
  the conflict is recorded rather than silently resolved.
- Durable evidence:
  `source-audits/dungeoneering-starter-harvest-2026-07-20.md`. No owner design
  gap emerged and no new UI was added.
- Focused verification passes 70 tests; complete non-Qt discovery passes all
  1,896 tests with 248 expected environment skips. Test quality,
  documentation, compile, diff, and guarded-worktree checks are clean. The
  reachability audit retains its intentional nonzero backlog result at 284
  orphan inputs and 302 blocked actions.
- Published
  `status-updates/dungeoneering-starter-backend-results-2026-07-20.html`;
  mobile copy: `https://pgbwaae8lohy.postplan.dev`.

## Target-level mechanics Details — 2026-07-20

- Added a collapsed `Details` disclosure to registry-backed skill targets in
  both flat and grouped selectors. It projects the live target row instead of
  duplicating or recalculating mechanics.
- Preserved provenance and implementation boundaries: source lines, audit
  classifications, equations, ticks, RNG state, and fabricated precision are
  not shown. Locked rows expose requirements without becoming selectable.
- Added a bounded scroll sheet for long Combat mechanics, same-skill open-state
  persistence, cross-skill/Farming reset, and normalized integer XP copy.
- Added pure and real-Qt coverage for provenance removal, grouped and flat
  rows, locked-row behavior, Farming reset, and the Combat height invariant.
- Kimi K3's taste pass is incorporated. A fully quit/relaunched native Anki
  process loaded one add-on dialog and verified live Cooking and locked-target
  behavior. Fable remains pending only because its mandatory fresh quota probe
  is blocked by macOS Keychain.
- Complete verification passes 1,899 non-Qt tests with 250 expected
  environment skips and 1,899 offscreen Qt tests with one intentional skip.
  See `source-audits/target-details-implementation-2026-07-20.md`.
- Published
  `status-updates/target-details-results-2026-07-20.html`;
  mobile copy: `https://0vdjdlyrmky3.postplan.dev`.

## Desert goat horn acquisition closure — 2026-07-20

- Added one source-admitted level-23 Goat Combat target with the exact
  period/Darkan-reconciled LP, maximum, passive melee behavior, guaranteed
  Bones and horn, executable combat levels, respawn, and existing desert heat.
- Closed the complete live Goat -> horn -> dust -> Combat potion chain without
  a seeded item, invented drop rate, or duplicate Billy Goat target.
- Corrected source IDs and non-stackability for Desert goat horn and Goat horn
  dust, replaced the dust's generic soft-clay fallback with period-pinned art,
  and added a normalized period Goat target sprite.
- Focused verification passes 425 tests plus the offscreen Goat-row check.
  Complete non-Qt and offscreen Qt discoveries each pass all 1,903 tests.
  A restarted native Anki smoke confirms the disabled Animals/Goat row and
  real portrait without mutating the save. Reachability is now 1,989 items
  with 247 orphan inputs and 260 unresolved actions.
- Published
  `status-updates/desert-goat-acquisition-results-2026-07-20.html`;
  mobile copy: `https://mibheiehz0uy.postplan.dev`.
- Durable evidence:
  `source-audits/desert-goat-combat-acquisition-2026-07-20.md`.

## Swamp toad acquisition closure — 2026-07-20

- Added a source-backed, no-requirement Utility collection row for intact
  Swamp toads and preserved the existing zero-XP one-to-one leg-removal action.
- Corrected the two item definitions to period IDs 2150/2152, non-stackable
  tradeable metadata, and distinct normalized pre-cutoff sprites with complete
  provenance.
- The live acquisition chain now reaches Swamp toad, Toad's legs, and Agility
  potion dose variants without a seeded item or invented shop/drop.
- Focused logic, registry, metadata, integration, asset, reachability, and Qt
  checks pass. Complete non-Qt discovery passes all 1,905 tests with 250
  environment skips, and complete real offscreen Qt discovery passes all 1,905
  tests with one intentional platform skip; docs and test quality are clean.
- A fully restarted native Anki smoke rendered exactly one enabled row and one
  menu without starting the activity or mutating the save. Kimi K3 returned a
  ship verdict. Fable remains pending only because its required live quota
  probe cannot access the Claude Code OAuth keychain credential.
- Reachability now reports 1,343 actions, 1,997 reachable items, 239 orphan
  inputs, and 250 unresolved actions.
- Published
  `status-updates/swamp-toad-acquisition-results-2026-07-20.html`;
  mobile copy: `https://jzn1gbktyze8.postplan.dev`.
- Durable evidence:
  `source-audits/swamp-toad-acquisition-2026-07-20.md`.

## Cooking byproduct reachability correction — 2026-07-20

- Fixed the deterministic item graph to include the already-live singular
  `byproduct_item` field used by the gut-leaping-fish actions.
- Fish offcuts are now correctly reachable through
  `Cooking:gut_leaping_trout`; no product behavior, probability, UI, or save
  state changed.
- The regression fails before the correction and the focused four-module run
  passes 284 tests afterward. Complete non-Qt discovery passes all 1,905 tests
  with 250 expected environment skips.
- Reachability now reports 1,998 reachable items, 238 orphan inputs
  (95 root/143 cascade), 1,343 actions, and 250 unresolved actions.
- Durable evidence:
  `source-audits/item-reachability-cooking-byproduct-correction-2026-07-20.md`.

## Willow branch acquisition — 2026-07-20

- Pinned the 2012 Willow-branch page, OpenRS2 item identities, and Darkan
  executable lineage for the health-check gate, five-minute branch interval,
  six-branch cap, tool alternatives, and zero XP.
- Implemented post-health-check branch accrual on the settled review clock,
  whole-patch pruning, regrowth, full-run queue participation, and a distinct
  contextual Farming button that leaves Chop primary.
- Corrected Willow branch, Secateurs, and Magic secateurs metadata to exact
  IDs and non-stackability.
- Added pure lifecycle, runtime queue, registry, reachability, projection, and
  real offscreen Qt regression coverage. Focused logic/integration passes 430
  tests; three targeted Qt checks pass. Complete non-Qt discovery passes all
  1,909 tests, and complete real offscreen Qt discovery passes all 1,909 tests
  with one intentional platform skip.
- Kimi K3 returned SHIP and its laptop-height geometry concern is now pinned.
  Fable remains blocked by the required live quota probe's macOS Keychain
  failure, and native-Anki restart proof remains blocked while the Mac is
  locked. These are external QA gates, not design gaps.
- The acquisition graph now reports 1,344 actions, 1,999 reachable items,
  237 orphan inputs, and 249 blocked actions.
- No owner design gap emerged. Durable record:
  `source-audits/farming-willow-branch-acquisition-2026-07-20.md`.
- Published
  `status-updates/farming-willow-branch-results-2026-07-20.html`;
  mobile copy: `https://uhyf9le1jwo1.postplan.dev`.

## Thieving loot reachability correction — 2026-07-20

- Added the live non-source-blocked Thieving loot tables to the deterministic
  acquisition graph.
- Nasturtium, Redberry, and Cadavaberry seeds now resolve through the Master
  Farmer instead of appearing as false root orphans.
- The graph improves to 1,379 actions, 2,012 reachable items, 234 orphan
  inputs (91 root/143 cascade), and 246 blocked actions.
- Focused reachability and Thieving verification passes 20 tests; complete
  non-Qt discovery passes all 1,909 tests with 251 expected environment skips.
  Documentation, test-quality, compilation, diff, and worktree-safety audits
  pass. No product behavior or UI changed.
- Durable evidence:
  `source-audits/item-reachability-thieving-loot-correction-2026-07-20.md`.

## Potion-container stackability correction — 2026-07-20

- Potion item generation now marks Vials, Potion flasks, ordinary potion
  doses, and flask doses explicitly unstackable instead of inheriting the
  registry's permissive default.
- The correction reconciles canonical item metadata with the cache-derived
  runtime stackability set and existing one-slot-per-potion carried behavior.
- Focused registry, cache-value, inventory, Combat, and Shop verification
  passes 416 tests; complete non-Qt discovery passes all 1,910 tests with 251
  expected environment skips. Documentation, test-quality, compilation, diff,
  and worktree-safety audits pass. No UI or owner-design behavior changed.
- Durable evidence:
  `source-audits/potion-container-stackability-correction-2026-07-20.md`.

## Penguin Hide and Seek horizontal MVP — 2026-07-20

- Implemented the complete weekly spy loop, quest-gated bonus spies, point
  cap, direct selection, all-points Larry redemption, persistence, review undo,
  direct-action undo, cadence registration, and the Activities UI.
- Corrected the live week source to the shared `shop_market_clock`; the first
  version's nonexistent `simulation_clock` would never have rotated in real
  Anki. Added a regression at the exact 1,680-review boundary.
- Added a normalized pre-cutoff rock-penguin activity icon with provenance and
  a reusable cutoff-safe fetch pipeline. No item sprites or item routes are
  required by this activity.
- Fable and Kimi K3 independently reviewed the new card. Confirmed issues in
  roster switching, sticky result copy, zero-point affordances, accessibility,
  hierarchy, and player-facing language were fixed and regression-covered.
- Final verification passes 2,008 non-Qt tests with 265 expected skips and
  2,008 real offscreen Qt tests with one intentional skip. Focused logic,
  integration, asset-normalization, registry, and geometry checks pass; the
  restarted native Anki process shows one menu and the complete Penguin card.
- No owner design gap surfaced. Exhaustive period spawn-location expansion is
  explicitly deferred data depth under the breadth-first program.
- Durable record:
  `source-audits/penguin-hide-and-seek-loop-2026-07-17.md`.

## Werewolf Skullball horizontal MVP — 2026-07-21

- Implemented the complete Activities-only Skullball loop: authentic entry
  gates, equipped Ring-of-Charos variants, source-route presets, Advanced
  T/K/S plans, one-review completion, XP, persistence, migration, activity
  arbitration, direct leave, cadence, telemetry, achievements, and exact undo.
- Removed the former partial Agility-course stub while preserving legacy save
  migration and historical completion counts.
- Added exact equipment metadata, normalized period art and provenance, a
  compact Activities card, registry/reachability coverage, and meaningful
  pure, runtime, integration, migration, asset, and real-Qt regressions.
- Opus supplied the independent taste pass because Fable is intentionally held
  in reserve. Confirmed contrast, sticky-input, auto-commit, enablement,
  result-legibility, and route-character issues were corrected before closure.
- Final verification passes all 2,131 non-Qt tests with 279 expected skips and
  all 2,131 real offscreen Qt tests with one intentional skip. A clean native
  Anki restart confirms one add-on menu and a selectable locked Skullball row.
  Documentation, test-quality, syntax, JSON, diff, asset-normalization, and
  worktree audits pass; reachability is unchanged and no design gap emerged.
- Durable record:
  `source-audits/werewolf-skullball-loop-2026-07-17.md`.
- Published
  `status-updates/werewolf-skullball-horizontal-results-2026-07-21.html`;
  mobile copy: `https://tbpw3iuzbn4k.postplan.dev`.

## Fishing Trawler horizontal MVP — 2026-07-21

- Implemented the complete source-shaped trip: level gate, finite persistent
  pressure, four useful duties, source supplies, stack-aware carried layout,
  Casual/Advanced policies, fixed crew offset, sinking, direct-banked haul,
  and the 40% ordinary Fishing XP rule.
- Added schema-65 persistence/arbitration, review and direct-action undo,
  cadence/telemetry, terminal stop, exact high-level XP evidence, period art,
  reachability output registration, and a compact Activities card.
- Opus's independent taste pass found and closed unsaved-board-plan loss,
  invisible lock copy, dead duplicate at-sea controls, pluralization, and risk
  legibility issues. Fable remained reserved; Kimi's incomplete fresh quota
  telemetry was not bypassed.
- Focused pure/integration/registry/reachability/asset checks pass. Full
  discovery passes 2,172 non-Qt tests with 285 expected environment skips and
  2,172 real offscreen Qt tests with one intentional skip. The live graph
  reports 1,439 actions, 2,132 reachable items, 166 orphan inputs, and 187
  unresolved actions.
- A clean native Anki restart confirms one add-on menu, paginated Minigames,
  and an inspectable locked Trawler card. This check exposed and closed a real
  disabled-row reachability gap that the first synthetic UI test missed.
- Documentation, test-quality, syntax, JSON, reachability, global asset
  normalization, diff, and worktree-safety gates pass.
- No owner design gap emerged. Exact pressure/catch distributions and Tiger
  shark are explicit data-depth work. Durable record:
  `source-audits/fishing-trawler-horizontal-implementation-2026-07-21.md`.
- Published
  `status-updates/fishing-trawler-horizontal-results-2026-07-21.html`;
  mobile copy: `https://t2fu1j1wdxe1.postplan.dev`.

## Great Orb Project horizontal MVP — 2026-07-21

- Implemented the complete eight-round review loop, level gate, team scoring,
  participation distinction, essence decisions, authentic rune output/XP,
  token settlement, early leave, persistence, undo, cadence, telemetry, and
  representative manual reward shop.
- Added Casual and Advanced policy, 28-slot temporary essence capacity,
  schema-66 migration and activity arbitration, normalized period art, a
  compact paginated Activities card, and meaningful pure/integration/Qt tests.
- Exact hidden score and essence distributions plus the full period reward
  catalog are deferred data depth. No wall clock or new design fork exists.
- Opus performed the new-UI taste pass after Kimi K3 was unavailable at its
  quota gate; all reproduced findings were corrected and Fable was not called.
- Verification: all 2,184 non-Qt methods pass with 287 expected dependency
  skips and all 2,184 real offscreen-Qt methods pass with one intentional skip.
  Docs, hard test quality, compilation, JSON, diff, global asset normalization,
  reachability, restarted native Anki, and worktree safety pass. Reachability
  is 1,440 actions, 2,132 reachable items, 166 known orphan inputs, and 187
  unresolved actions; the slice adds no new orphan.
- Durable record:
  `source-audits/great-orb-project-horizontal-implementation-2026-07-21.md`.
- Results:
  `status-updates/great-orb-project-horizontal-results-2026-07-21.html`;
  mobile copy: `https://afe87qn0iefl.postplan.dev`.

## Managing Miscellania horizontal MVP — 2026-07-21

- Implemented the complete kingdom-management substrate: quest gates and
  upgrades, 240-review days, approval, coffer salary, deferred production,
  individual subject allocation, retroactive collection, direct banking,
  saved approval work, persistence, undo, cadence, telemetry, and activity
  arbitration.
- Added a compact period-qualified catalog covering fixed output, derived
  bonus output, and player-selected sub-output through Mining, Maple, and
  Hardwood. Remaining families and hidden bonus distributions are explicit
  data depth; no mechanic is deferred.
- Added normalized period interface art, provenance/fetch tooling, the fourth
  Landmarks activity page, and meaningful pure, runtime, integration,
  migration, registry, asset, and real-Qt regressions.
- Opus's taste pass closed collection affordance, over-allocation, funding,
  clock, lock-copy, hierarchy, and geometry problems. Fable stayed reserved;
  Kimi did not pass its fresh quota gate.
- Verification passes all 2,201 non-Qt methods with 289 expected dependency
  skips and all 2,201 real offscreen-Qt methods with one intentional skip.
  Native Anki confirmed one menu, four paginated activity categories, the
  period icon, and a reachable locked card. The native pass caught and closed
  a real bottom-label overlap hidden by the initial synthetic assertion.
- Docs, hard test quality, compilation, JSON, diff, global activity-icon
  normalization, reachability, and worktree safety pass. The graph reports
  1,441 actions, 2,132 reachable items, 166 known orphan inputs, and 187
  unresolved actions; this slice adds no orphan and no design gap.
- Durable record:
  `source-audits/managing-miscellania-horizontal-implementation-2026-07-21.md`.
- Results:
  `status-updates/managing-miscellania-horizontal-results-2026-07-21.html`;
  mobile copy: `https://juwv1i05slff.postplan.dev`.

## Jade Vine horizontal MVP — 2026-07-21

- Implemented the complete health-check branch clock, saved policy triad,
  review-priced pruning, sixth-branch Wild transition, Horacio replant loop,
  persistent shared-engine Combat, dangerous failure, atomic XP/seed reward,
  and free replacement-seed recovery.
- Added schema-68 save repair, exact review/direct undo boundaries, a compact
  Jade-only policy/status surface, and pure, runtime, integration, migration,
  and real-Qt regression coverage.
- The exact Wild Vine combat stats and style/bind distributions remain
  explicit data depth behind a disclosed bounded implementation. No owner
  design question remains.
- Opus reviewed the new policy surface and runtime seams. Every reproduced
  defect was fixed, including safe migration of legacy mature vines,
  Secateurs-aware pruning, disclosed and confirmed Horacio payment, hidden
  unavailable seed recovery, both cadence entry paths, and true direct-action
  undo. Fable stayed reserved and Kimi was not used after its quota probe could
  not establish a fresh rolling window.
- Closure is green: 2,210 non-Qt methods (291 expected dependency skips), 2,209
  real offscreen-Qt methods (one intentional skip), 17 final Qt/runtime delta
  methods, docs, hard test quality, compilation, asset normalization,
  reachability, diff, worktree safety, and a fresh native-Anki singleton smoke.
- Results: `status-updates/jade-vine-horizontal-results-2026-07-21.html`;
  mobile copy: `https://rdcwhc5livaj.postplan.dev`.

## Court Cases horizontal MVP — 2026-07-21

- Implemented the complete shared Court Cases loop with three period-pinned
  cases: authentic entry gates, free starter, summons ownership/consumption,
  preparation, both legal roles, Casual/Advanced policy, decided and undecided
  verdicts, retry, give-up loss, XP, and item rewards.
- Added the exact fourteen-day Batch 2 rule as `3,360` answered cards, plus
  schema-69 persistence, review/direct undo, cadence, telemetry, Combat and
  Thieving summons filtering, normalized period art, a live zero-bonus
  wearable Rainbow afro, and a compact Activities card.
- Opus reviewed the new UI because Fable was reserved and Kimi's quota gate was
  closed. The duplicate counter, internal catalog wording, mode noise, and
  repeated starter copy were removed.
- Remaining thirteen cases, alternate winning routes, additional summons
  acquisition sources, and Barrister milestones are data depth. Daily
  Challenges is separately blocked on a newly recorded source/contract
  conflict; no design was silently reinterpreted.
- The complete non-Qt suite passes 2,227 methods with 292 expected dependency
  skips; the complete real offscreen-Qt suite passes the same 2,227 methods
  with one intentional skip. A fully restarted native Anki process showed one
  launcher, one menu, the paginated Court Cases row, and an unclipped locked
  starter card without mutating the owner save.
- Broad verification also repaired a pre-existing generated-equipment
  import-order mutation. Docs, hard test quality, compilation, JSON, diff,
  normalized assets, reachability, and worktree safety pass. Reachability is
  1,442 actions, 2,133 reachable items, 166 known orphan inputs, and 187
  unresolved actions; the slice adds no orphan.
- Durable audit:
  `source-audits/court-cases-horizontal-implementation-2026-07-21.md`.
- Results: `status-updates/court-cases-horizontal-results-2026-07-21.html`;
  mobile copy: `https://nvblmw2z0ddz.postplan.dev`.

## Soul Wars horizontal closure — 2026-07-22

- Shipped the complete twelve-review objective loop with Casual bottleneck and
  Advanced fixed duty/team policies, obelisk control, fragment offering,
  avatar defence, live six-tick avatar Combat, safe death, participation
  removal, leave forfeiture, and exact 3/2/1 Zeal settlement.
- Added the exact four-charm Combat-band shop plus schema 79 persistence,
  repair, cadence, telemetry, activity arbitration, direct/review undo,
  activity and hidden-enemy registration, normalized cutoff assets, and a
  compact Activities plan/progress/reward surface.
- Added meaningful pure, migration, runtime, direct-undo, registry, combat,
  asset, and real-Qt regressions. Root inspected ready and active 1200×760 dark
  renders.
- Ordinary and full real offscreen-Qt discovery each execute 2,448 methods;
  ordinary has 309 declared skips and Qt has one intentional skip. Docs, hard
  test quality, JSON/provenance, compilation, diff, and worktree safety pass.
  The reachability audit reports only the pre-existing 166-orphan/187-blocked
  dependency ledger.
- Native Anki remains unclaimed because the Mac is locked. Kimi K3 and Fable
  taste review remains deferred under the owner's quota hold. No design gap
  surfaced. Shades of Mort'ton is next.
- Results: `status-updates/soul-wars-horizontal-results-2026-07-22.html`;
  mobile copy: `https://7xdhzerm80g9.postplan.dev`.

## Duel Arena breadth-one closure — 2026-07-25

- Implemented the complete free challenge lifecycle: eleven configurable
  rules, deterministic bounded opponents, first-to-three review exchanges,
  safe win/loss/allowed-forfeit settlement, full stat restoration, and no coin
  path. `No Forfeit` blocks that action while the five-review bound guarantees
  completion.
- Added persisted win/result ledgers and all six Duellist's cap tiers, plus
  schema-82 migration/repair and shared persistent-activity arbitration. The
  win-threshold vector is registered as `duel_arena_cap_thresholds` because the
  readily available tier pages miss the strict cutoff by about five hours.
- Added one-exchange-per-review dispatch, central direct-action undo, an
  Activities configuration/active/result card, claim/change-look ownership and
  automatic cap upgrades, six cap item/equipment definitions, a visible
  activity icon, six cap sprites, and exact asset provenance.
- The source audit separates period facts from the opponent/scoring
  abstraction. Duel Tournaments and staking are excluded; the one registered
  placeholder is the near-cutoff cap-threshold vector.
- Final verification passes both full lanes at 2,749 tests: non-Qt with 333
  expected skips and real offscreen Qt with one intentional skip.
- Durable audit:
  `source-audits/duel-arena-horizontal-implementation-2026-07-25.md`.

## Clan Wars breadth-one closure — 2026-07-26

- Completed the interrupted Clan Wars build: three portal modes, an eight-review
  bounded match, entry gates against other persistent activities and open combat
  encounters, safe and dangerous death, teleport-escape refusal inside the red
  portal, sourced boost clamping on dangerous entry, leave/forfeit, schema-83
  persistence and migration, central direct-action undo, once-per-review
  dispatch, and an Activities card with honest locks.
- The red portal's item loss is real: no gravestone, no Death's Office, Protect
  Item saves one item. Three tests fail if the shared grave-writing path is
  restored.
- Rebalanced the match so no outcome is inert. The interrupted build could only
  ever draw `0-0`; a disclosed crossfire model makes kill, death, win, loss and
  draw all reachable through real play, each pinned to a recorded seed.
- Removed an unsourced combat-policy damage dial and three fabricated object-ID
  citations. Recovered the red-portal boost caps exactly from Darkan rather than
  registering them as a placeholder, so this family adds no placeholder.
- Final verification passes both full lanes at 2,780 tests: non-Qt with 334
  expected skips and real offscreen Qt with one intentional skip.
- Durable audit:
  `memory-bank/source-audits/clan-wars-horizontal-implementation-2026-07-26.md`.


## Slayer master chathead completion — 2026-07-26

- Added period-authentic registered chatheads for Spria, Mazchna, Achtryn,
  Vannaka, Chaeldar, Sumona, Duradel and Lapalok; Turael already had one.
- The MediaWiki upload history corrected the stale Spria assumption: canonical
  `File:Spria chathead.png` has a 2012-01-29 pre-cutoff revision, so every one
  of the nine displayable master identities has period art.
- Slayer cards now resolve the face from the exact displayed master name. The
  no-art path deliberately leaves the label without a pixmap instead of using
  another master as a fallback. Achtryn now becomes displayable when While
  Guthix Sleeps has started, matching its existing alternate-display metadata.
- Verification: `python3 run_tests.py` passed 3,022 tests with 348 skips; the
  full offscreen Qt lane passed the same 3,022 tests with one skip.

## Dominion Tower — complete, 2026-07-28

The tower ships whole: the 110-combat and twenty-of-thirty-eight quest gates read
the real quest ledger, forty-eight encounters carry the quest that unlocks them
and the class floor gate that limits them, the twenty-two handicap wheel runs
with its sourced per-round factor deltas and its nudge-and-respin rules, and all
four playable modes plus spectating work. Every reward on the achievement ladder
is reached in tests by actually killing the bosses its unlock condition names,
including the five hundred kills the gloves, dreadnip and mines all read.

Schema 98. Sources: `memory-bank/source-audits/dominion-tower-harvest-2026-07-28.md`.
Forks queued as design threads 3.19, 3.20 and 3.21.

## Dungeoneering phase C — complete, 2026-07-30

- Added between-floor Ring of Kinship class selection and all ten exact
  token-tier upgrades as undoable direct actions. Gatherer and Artisan use
  bounded live effects. Other classes expose sourced descriptions without
  invented automation.
- Rendered the complete forty-two-row reward catalog with exact costs and
  gates. Forty-one rows are visibly staged and refuse purchases. The Coal bag
  is the sole functional purchase at 4,000 tokens with Dungeoneering 35 and
  Mining 35 gates, one-owned enforcement, a twenty-seven-Coal capacity, and
  undoable manual Bank/carried fills.
- Connected Coal bag consumption to the real Smithing answer path. Smithing
  availability includes bag Coal, smelting consumes bag Coal before loose or
  carried Coal, and review undo restores the exact prior state.
- Added earned, spent, and balance token values to the Dungeoneering card.
  Entry-only Phase C controls use pure-view visibility and enable flags.
- Added exact pre-cutoff Ring of Kinship and Coal bag sprites through
  `tools/fetch_assets.py`; `assets_provenance.json` records the selected
  historical revisions. No safe pre-cutoff reward-trader image was found, so
  the trader uses the functional Coal bag row art rather than invented art.
- Extended the v100 Dungeoneering sanitizer additively. The repository config
  version remains 101.
- Verification: the requested Dungeoneering, Smithing, and placeholder module
  gate passes 53 tests; the focused dark offscreen Qt card check passes; full
  discovery passes 3,572 tests with 415 expected skips.

## Miniquest ledger — stage 1 complete, 2026-07-29

Miniquests are a flag on the existing quest ledger, not a second system: same
storage, same unlock engine, same stage and journal machinery, with their own
`Miniquests` grouping on the Quests tab that only appears when both groups are
on screen. Two rows ship, exactly the two the owner named — The Hunt for Surok,
which makes the parked Bork loop reachable, and The Lair of Tarn Razorlor,
which lights the Dominion Tower class-H encounter that already gated on this
id. No catalog sweep.

Both play end to end through the ordinary reducers. Surok gates on What Lies
Below plus Mining 42 and ends on Bork; Tarn gates on Haunted Mine plus Slayer
40 and ends on Tarn's two forms. Each awards the sourced 5,000 Slayer XP and no
quest points.

Two lessons worth keeping. First, the quest catalog builder reads the wiki's
quest release list, which carries no miniquests at all, so any miniquest row
has to be written by hand and appended to `QUESTS`. Second, an enemy's
RuneScape combat level must never be copied into its four core stats: Bork at
level 267 was both unhittable and unsurvivable until the row adopted the
already-registered 72%-of-level conversion the Dominion Tower work settled for
the same problem.

Schema 103. Sources and the recorded data-depth gaps — the whole salve amulet
chain, Tarn's diary as an item, and the still-parked Bork daily loop — are in
`memory-bank/source-audits/miniquest-ledger-2026-07-29.md`.

Stage 2 closed the sourcing: every requirement, stage and reward was re-read
against the pinned revisions and against Darkan, and nothing moved. Two
requirements were considered and deliberately left out — Prayer 43, which
Darkan's miniquest enum enforces but the same wiki table it came from annotates
"not needed to complete the quest", and Slayer 44, which appears on one page
only and gates nothing that must be killed. Darkan's Bork is level 107 with a
1,500 XP daily, both post-cutoff figures; the pre-cutoff record's 267 and 250
win. Design thread 3.23 is closed, and its claim that the Tarn boss belongs to
no glove set was re-checked and now has a test.

## Bork, the daily Chaos Tunnels encounter — 2026-07-30

The loop the 2026-07-18 audit parked is live. Bork is a Distraction and
Diversion: one kill per answered-card day, gated on the `hunt_for_surok`
miniquest the ledger just made completable, fought through the ordinary
six-tick live Combat slices. At 2,000 of his 3,000 life points he calls three
to nine Ork legions, which cannot be engaged and press from range every review,
and the lair's Dagon'hai Elite lands a 100-250 magic bolt every 33 ticks that
Protect from Magic answers. A victory pays 250 Slayer XP, 2,000-10,000 coins
and the full guaranteed bundle; the Varrock Elite tasks and a worn Ring of
Wealth each move the payout to its own sourced column.

Three findings worth keeping. The 2026-07-18 audit's `source_blocked` charm
bundle is closed: Darkan's `guaranteedDrops` reproduces the pinned page's drop
table in all four columns, so the table's 5 blue / 7 crimson / 2 green stands
and the same page's prose is simply wrong. Every kill in this loop is a repeat
kill, because the miniquest completion already pays the sourced 5,000 first-kill
Slayer XP. And a homogeneous pressure front needs no target picker at all — the
legions despawn with Bork, so there was never a choice to offer.

Sources, the omitted rateless drops and the rest of the judgements are in
`memory-bank/source-audits/bork-daily-loop-2026-07-30.md`.

## Reviewer-strip pass 5 — fixed-pending-confirmation, 2026-07-31

- Replaced card-content-dependent overlay placement with one fixed 128-pixel
  strip pinned to the live top edge of Anki's answer buttons. The four stable
  seats are D&D, Farming, XP, and `Do bank run`.
- Applied exact base document-bottom padding on each card load, retained it
  through late image growth, added temporary reserve for open drawers, and made
  floating XP follow the strip.
- Added an upward Event drawer with wrapped selectable rows and actual awarded
  skill names, including aggregate multi-skill awards. XP uses neutral text;
  GE alone owns yellow partial and green complete status.
- Stacked GE above Event, cleared hidden GE widgets, and wired each GE row to
  focus or open the existing Grand Exchange tab.
- Added one bank-run request seam. Combat delegates to the pass5-combat lane's
  exported `request_combat_bank_run_now_pure` hook; current carried-inventory
  review activities enter their established review-paced travel paths and costs.
- Focused pure-view, carried-overlay runtime, integration, and offscreen Qt
  tests pass. Qt probes show widgets, process events, cover default and
  560-pixel heights, and simulate late tall image growth.

## Pass 7 P0 progression correctness — 2026-08-03

- Proved that the reported 970 Magic XP is one authentic Big Top source band,
  not a cadence multiplier or display defect, and pinned the exact owner state.
- Corrected Constitution's level-10 starting state from zero total XP to 1,154.
  Schema 111 adds the omitted baseline once to existing saves and recalculates
  upward without discarding earned XP.
- Restored the standard level-up gate for Combat stats, preserved positive
  fractional XP in event text, and placed XP events before resulting level-up
  events without duplicate aggregate rows.
- Added the period source audit and regressions for new saves, the owner's save,
  migration idempotence, Combat level checks, fractional display, event order,
  and the Circus cash-out.
- Verification passed 434 focused non-Qt tests, 32 offscreen Qt tests, and the
  independent Codex-only frozen-packet checker.
- Accepted implementation commit: `d12b731a`.

## Pass 7 P1 review-strip correctness — 2026-08-03

- Made the D&D and Activities seats legible at the owner's 712-by-987 native
  Anki window while keeping **Bank run** usable, the vanilla answer bar
  unchanged, and card content clear of the strip.
- Reordered combat progress to lead with a complete labeled kill count.
- Replaced separate event-row widgets with one selectable document and retained
  lazy expansion.
- Removed music unlocks from the floating popup path without removing their
  durable event history or diary task popups.
- Verification passed 31 focused offscreen Qt tests, 238 focused non-Qt tests,
  a native MBP Anki pass, and an independent frozen-packet checker.

## Pass 7 P2 menu routing and world-time correctness — 2026-08-03

- Made the top-level Activities entry a stable master-list route without
  removing direct-link or selected-row detail navigation.
- Moved Minigames and Distractions and Diversions into their own icon rows
  beneath Activities in the middle Selection column, matching the owner's
  Pass 7 arrows. Activities keeps only the Warriors' Guild and Landmarks master
  groups; the two family rows show flat alphabetical lists. The wider
  250-pixel selector is scoped to Activities so other narrow category layouts
  retain their 190-pixel column.
- Moved simulated world time from the review XP strip to the main-menu status
  row and retained its answered-review-only projection.
- Verification passed 411 focused offscreen UI tests, 214 focused non-Qt tests,
  a native MBP Anki pass, and independent checker run
  `3452c9ca-5e43-4bd0-a19e-c65969a19dba`.

## Pass 7 P3 Combat selector correctness — 2026-08-03

- Added the missing post-layout restore step, so a saved Combat target is
  automatically centered when the selector opens.
- Preserved the settled distinction between green/bold saved state and blue
  transient keyboard selection, including activation-only persistence.
- Added a Qt regression for in-view restore, compact hierarchy, level sorting,
  and exact locked-target presentation.
- Verification passed five focused selector tests, 381 main-menu Qt tests, 31
  review-strip tests, a native MBP Anki pass, and independent checker run
  `808ee8a2-7993-4e41-adb2-144cfd002b56`.
- Equipment meters and Big Top queue interaction remain explicitly
  design-blocked pending the owner/Fable co-ideation brief. No speculative UI
  was implemented, and neither Fable nor Kimi was used.

## Pass 8 implementation complete; native gate open — 2026-08-07

- Applied every settled owner decision in
  `codex-briefs/pass8-owner-fable-decisions-2026-08-07.md`: top-tab order, Bank
  metadata and frame, Stats skill guide, Collections family/drop log, and the
  Shooting Star exit/watch/rejoin state machine.
- Root owned all shipped code. Bounded read-only Opus 5 workflows handled
  frontend layout and independent review. Fable and Kimi were not invoked.
- Final accepted product commit: `08597813`.
- Full non-Qt and offscreen Qt discovery each pass 3,857 tests. Documentation,
  test quality, asset checks, diff checks, and worktree safety pass. The
  reachability audit reports only its unchanged known dependency ledger.
- The remaining acceptance step is native Anki proof of the changed surfaces,
  the unchanged vanilla answer bar, and card-content non-overlap. It is blocked
  by `thread_list_unavailable` from the owner's regular MacBook Pro Codex
  Connection, despite the owner confirming that the computer is on. Tailscale
  is excluded, and headless evidence does not close this gate.
- The owner now owns that final check through a direct playtest. The local
  results artifact is `status-updates/pass8-results-2026-08-07.html`; it opened
  in Arc and includes a saved checklist plus a copyable defect report.
  Postplan hosting remains blocked because the local client has no valid API
  key and rejects inline JavaScript without authentication.
## Brawling-gloves source closure — 2026-08-09

- Closed the period identity and multiplier table for six skilling gloves.
- Closed five use limits from cutoff skill pages.
- Rejected both emulator charge tables as period truth because they conflict
  with the cutoff pages.
- Kept Mining's action count, glove drop rates, and acquisition route honest.
  The source audit records these blocks without adding inert product rows.
- Both full lanes pass 3,939 tests. Plain has 483 expected skips, and real
  offscreen Qt has three intentional skips.

## Cooking-gauntlets runtime closure — 2026-08-09

- Added the complete Family Crest gauntlet lifecycle: physical equipment,
  remembered enchantment, free first conversion, 25,000-Coin re-enchantment,
  free loss recovery, persistence, and atomic direct-action undo.
- Added target-local Casual/Advanced gear policy with safe displacement and
  restoration. Manual hands-slot choices remain authoritative.
- Applied the eight final dated no-burn thresholds without changing XP or ever
  reducing the ordinary Cooking chance. Retired Shark's cadence source block.
- Reused all four provenance-recorded normalized quest sprites. Kimi K3 and
  Fable reviewed the new target, Bank, and worn-equipment surfaces.
- Verification passes 3,957 tests in both full lanes. Plain has 485 expected
  skips; real offscreen Qt has 3. Documentation, test-quality, JSON,
  compilation, diff, reachability-ledger, and worktree gates pass. Native Anki
  visual proof remains blocked by the locked Mac.
- Evidence:
  `source-audits/cooking-gauntlets-runtime-closure-2026-08-09.md`.

## Chaos Elemental and brawling-gloves runtime closure — 2026-08-09

- Added an obtainable Chaos Elemental encounter with three combat styles,
  teleport delay, equipment removal into the carried pack, and six supported
  brawling-glove drops.
- Added physical per-copy charged equipment and sourced XP multipliers for
  Woodcutting, Firemaking, Mining, Smithing, Fishing, and Cooking.
- Added saved target-local Wilderness training with shared PKer risk, food,
  death, grave, persistence, UI, assets, and undo.
- Registered the three unrecovered period values in code and
  `placeholder-values.md`; no wall-clock gameplay or unsupported glove family
  was added.
- Kimi K3 and Fable accepted the final UI. Native Anki rendered the new Combat
  group and Chaos Elemental art. Both full test lanes pass 3,972 tests.
- Evidence:
  `source-audits/chaos-elemental-brawling-runtime-closure-2026-08-09.md`.

## Cave eel Fishing runtime closure — 2026-08-09

- Promoted Cave eel from deferred provenance into the live Fishing registry at
  its sourced level 38 with ordinary rod-and-bait behavior, Raw cave eel
  output, and 80 Fishing XP.
- Registered the unrecovered catch roll as a placeholder and rejected the
  conflicting level-28 reconstruction value. Removed the now-empty deferred
  Fishing content seam.
- Reused the normalized Raw cave eel Cooking asset and verified the existing
  selector, carried-pack, runtime, persistence, undo, and downstream Cooking
  paths without adding a new UI pattern.
- Both full test lanes pass 3,974 tests. Plain has 486 expected skips; real
  offscreen Qt has 3 intentional skips. Documentation, test quality,
  compilation, JSON, diff, reachability-ledger, and worktree gates pass.
- Evidence:
  `source-audits/cave-eel-fishing-runtime-closure-2026-08-09.md`.

## Karambwan Cooking runtime closure — 2026-08-09

- Closed all three settled Karambwan Cooking methods through the shared
  one-review Cooking runtime: poison, thorough, and Karambwanji.
- Preserved authentic quest timing, burn outputs, success-only XP, item
  tradeability and stackability, persistence, telemetry, and review undo.
- Registered only the two hidden burn curves as placeholders; no period
  content was invented and no wall-clock mechanic was added.
- Added normalized period sprites and complete data, pure, runtime,
  integration, metadata, and established-selector Qt coverage.
- Both full 3,982-test lanes pass. Plain has 486 expected skips; real offscreen
  Qt has three intentional skips. All repository closure audits pass apart
  from the known nonzero reachability dependency ledger.
- Evidence:
  `source-audits/karambwan-cooking-runtime-closure-2026-08-09.md`.

## Dagannoth Kings runtime closure — 2026-08-09

- Added a reusable persistent boss-room substrate and its first dangerous
  consumer: Prime, Supreme, and Rex together with visible roster pressure,
  Casual/Advanced targeting, ordinary Combat/Prayer/food/Slayer/drop handling,
  review-driven respawns, explicit Leave, persistence, and undo.
- Closed the minimum Dragon-hatchet acquisition route with sourced guaranteed
  bones/hide and three clearly registered hidden-value reconstructions.
- Added a compact paginated Activities card with three normalized period NPC
  sprites. Kimi K3 and Opus reviewed it; a 900×560 geometry regression guards
  the clipping defect found during rendered verification.
- Both full 4,004-test lanes pass. Plain has 488 expected skips and real
  offscreen Qt has three. All repository closure audits pass, and reachability
  improves to 1,547 actions / 2,354 reachable items / 159 orphan inputs / 179
  blocked actions. Native Anki interaction is not claimed.
- Evidence: `source-audits/dagannoth-kings-room-2026-08-09.md`.

## Blue dragon scale acquisition — 2026-08-09

- Added the sourced seven-spawn Dusty-key Taverley route through the existing
  zero-XP Utility gathering substrate, including persistence, telemetry,
  review undo, selector metadata, and real Qt coverage.
- Registered exact item identities and distinct normalized period art for Blue
  dragon scale and Dragon scale dust. No placeholder or new UI pattern was
  needed.
- The row activates the existing dust, Weapon poison, and Antifire graph:
  reachability improves to 1,548 actions / 2,377 reachable items / 137 orphan
  inputs / 148 blocked actions.
- Both full 4,006-test lanes pass. Plain has 488 expected skips and real
  offscreen Qt has three. Native Computer Use timed out twice, so native Anki
  interaction is not claimed.
- Evidence: `source-audits/blue-dragon-scale-acquisition-2026-08-09.md`.

## Item reachability leverage ranking — 2026-08-09

- Added a deterministic one-root-at-a-time simulation to the existing
  acquisition graph. `--rank-roots N` now shows the transitive item and action
  gain for each candidate without inventing an acquisition route.
- JSON output includes every newly reachable item, so BFS selection is
  reproducible and inspectable. The first ranking selects Potato cactus at
  +20 items/+19 actions.
- Focused tests and both full 4,007-test lanes pass. No runtime, save, UI, or
  content data changed.
- Evidence: `audits/item-reachability-leverage-ranking-2026-08-09.md`.

## Potato cactus acquisition — 2026-08-09

- Added the sourced three-spawn first-level Kalphite-Hive route through the
  established zero-XP Utility gathering substrate. The ordinary route is not
  quest-gated; lower-floor spawns remain catalog depth.
- Registered exact item identity 3138 and reused the normalized period Potato
  cactus sprite already shared with Summoning. No placeholder or new
  interaction pattern was introduced.
- The route activates 20 existing downstream item states and 19 actions,
  including the complete Magic-potion chain. The live graph is now 1,549
  actions / 2,397 reachable items / 124 orphan inputs / 129 blocked actions.
- Focused behavior and real Qt checks pass. Full plain and real offscreen-Qt
  discovery each pass 4,009 tests. Documentation, test quality, compilation,
  JSON, asset normalization, diff, and worktree audits pass.
- Evidence: `source-audits/potato-cactus-acquisition-2026-08-09.md`.

## Tokkul shops and Uncut onyx acquisition — 2026-08-09

- Activated item 6529 as the existing Tokkul inventory currency for the three
  TzHaar shops, preserving the pinned 274-shop AnkiScape snapshot rather than
  absorbing unrelated changes from the active Darkan checkout.
- Pinned all 23 cutoff stock rows, corrected four cache-price conflicts, and
  enforced the period player-buy-only rule. A 2,700,000-Tokkul purchase now
  closes Uncut onyx, cutting, jewellery, and downstream item paths through the
  shared shop and Crafting runtimes.
- Added generator, catalog, transaction, undo, buy-only, reachability, and real
  Qt purchase coverage. Deterministic currency-only regeneration prevents
  future source-checkout drift from contaminating a focused catalog update.
- Reachability is now 1,549 actions / 2,413 reachable items / 117 orphan inputs
  / 118 blocked actions. Full plain and real offscreen Qt discovery each pass
  4,014 tests. Documentation, test quality, compilation, JSON, asset,
  deterministic-generation, diff, and worktree gates pass.
- Evidence:
  `source-audits/tokkul-shops-uncut-onyx-acquisition-2026-08-09.md`.

## Fellstalk seed acquisition — 2026-08-09

- Added the cutoff-proven Master Farmer route for one Fellstalk seed without a
  new runtime or UI pattern. The existing 42-row table becomes 43 rows and
  2,200 slots.
- Registered the unrecovered `Very Rare` relative weight as a one-slot
  placeholder. Evil Trees, Managing Miscellania, and monster drops remain
  catalog depth; Vinesweeper still excludes Fellstalk.
- Replaced the modern Fellstalk sprite with the normalized pre-cutoff upload
  and pinned its exact timestamp and SHA-1 in behavior coverage.
- The route recovers eight existing item states and five actions. The live graph
  is now 1,549 actions / 2,421 reachable items / 112 orphan inputs / 113 blocked
  actions.
- Focused checks pass 110 tests plus two real Qt tests. Full plain and real
  offscreen-Qt discovery each pass 4,016 tests. Documentation, test-quality,
  compilation, JSON, asset, diff, and worktree gates pass.
- Evidence:
  `source-audits/fellstalk-seed-acquisition-2026-08-09.md`.

## Cured yak-hide service — 2026-08-09

- Added Thakkrad Sigmundson as an 84th generated shop service. Each selected
  unit consumes one Yak-hide and 5 Coins and produces one Cured yak-hide.
- Extended the shared shop quest gate with numeric progress checks. The source
  service opens at The Fremennik Isles stage 5 and remains open after quest
  completion.
- Preserved the pinned 274-shop snapshot through deterministic
  `--services-only` regeneration. No unrelated Darkan shop data changed.
- Reused exact rev-742 item identities and the normalized 2010 icon. No new UI
  pattern or placeholder was introduced.
- The graph is now 1,550 actions / 2,423 reachable items / 111 orphan inputs /
  111 blocked actions. Focused checks pass 65 pure/integration tests and one
  real Qt test. Both full lanes pass 4,018 tests.
- Documentation, test-quality, compilation, JSON, deterministic generation,
  asset, diff, and worktree gates pass.
- Added a source-complete Emerald-lens handoff for the Darkan quest lane rather
  than changing Lunar Diplomacy in this slice.
- Evidence: `source-audits/cured-yak-hide-service-2026-08-09.md`.

## Quest reachability truth — 2026-08-13

- Reachability figures are branch-relative: `main` at `1cf43931` reports
  1,556 actions / 2,573 reachable items / 102 orphan inputs / 101 blocked
  actions / 1,448 seeds, while `goal/acquire-2026-08-12` at `2cfac317` reports
  1,568 / 2,509 / 97 / 100 / 1,367.
- On top of that acquire tip, hard-stopping quests at the first unavailable
  required action and propagating prerequisite and quest-point failure produces
  1,568 / 2,248 / 100 / 103 / 1,099, with 54 root and 46 cascade orphans.
- Blood talisman, Jade vine seed, and Magic secateurs are the three newly
  orphaned quest rewards. Lost City's blocked Dramen branch keeps Cinnamon's
  real grind action blocked rather than seeding either item directly. The Kudos
  integrity test now records Dagon'hai history and Prophecy tablet as unavailable
  completion rewards instead of asserting that every exhibit item is reachable.
- This branch depends on `goal/acquire-2026-08-12` and must merge after it. The
  improved figures are not reproducible from `main` alone.
- Missing actions and registered unsatisfiable encounters now hard-stop quest
  stages. Inventory, tools, alternatives, routes, variants, and encounters with
  no registered guaranteed drops remain unmodelled residual debt, so 2,248 can
  be wrong in either direction and is not final acquisition truth.

## Black mushroom acquisition — 2026-08-09

- Added a one-pickup, zero-XP Utility route for the cutoff Black mushroom
  ground source near Uzer and in the Goblin Cave.
- Corrected `grind_black_mushroom` to require and consume one empty Vial, as
  both cutoff item pages require. It still yields one ink and no XP.
- Pinned rev-742 item identities and non-stackable/non-exchangeable semantics.
  Added normalized source-period icons and exact provenance coverage.
- The live graph is now 1,551 actions / 2,425 reachable items / 110 orphan
  inputs / 110 blocked actions. Focused checks pass 500 pure/integration tests,
  131 asset/registry/reachability tests, and two focused real offscreen Qt tests.
  Full plain and offscreen Qt discovery each pass 4,021 tests, with 490 expected
  plain skips and three Qt skips.
- Evidence: `source-audits/black-mushroom-acquisition-2026-08-09.md`.

## Farming Stats skill-guide source block — 2026-08-12

- Rev-727 and rev-742 establish a 110-struct Farming guide with seven filters and source-owned labels, levels, icons, categories, and gates.
- Withdrew the crop-table projection after review proved it inverted the source: it omitted non-crop unlocks, filtered period rows by implementation state, substituted internal names/icons, and discarded access gates.
- Recorded a rebuild specification that uses the period struct list as the spine and resolves each entry against its owning AnkiScape registry. No product behavior changed.
- Dungeoneering remains untouched as a separate, larger guide gap.
- Evidence: `source-audits/farming-skill-guide-2026-08-12.md`.

## Pass 9 owner repair — 2026-08-11

- Added a visible text cue and stronger fill for saved target rows across shared flat and grouped selectors.
- Added exact old-to-new values to level-up dialogs and covered multi-level gains.
- Removed all Milestone cape rows from guide projections without changing the cape systems.
- Added 105 Slayer monster-family rows to the Stats guide from the current Slayer registry.
- Audited all 25 skill guides. Farming and Dungeoneering remain the two non-combat guide gaps that need period section evidence.
- Added focused pure, integration, lifecycle, and real Qt coverage. The guide/UI lane passes 413 tests.
- Both full lanes pass 4,058 tests. Documentation, test quality, compilation, native Anki, diff, and worktree checks pass.
- Evidence: `codex-briefs/pass9-owner-notes-handoff-2026-08-11.md`.
- Results: <https://zvxa8ne0p5qz.postplan.dev>.

## Inventory direct-action seam — 2026-08-13

- Item packs and impling jars now commit through `commit_direct_action` instead of a private transaction copy, so they inherit the shared music-log refresh and complete undo snapshot, including `current_skill`.
- The application-path regression opens a Dragon impling jar, proves the pending quest track is refreshed, changes the live skill, and proves undo restores both the save and Hunter.
- Both full lanes pass 4,104 tests: plain with 498 expected Qt skips, and offscreen Qt with three skips. Reachability is unchanged at 1,568 actions / 2,248 reachable items / 100 orphan inputs / 103 blocked actions.

## Source-backed system map — 2026-08-14

- Added `status-updates/ankiscape-system-map-plan-2026-08-14.html` and the interactive completion artifact `status-updates/ankiscape-system-map-results-2026-08-14.html`.
- The owner rejected the first composition. Opus 5 then rebuilt the result artifact from scratch and Codex rejected its first render for token, label, legend, palette, and clipping failures before accepting a second composition pass.
- The final map traces review control, menu control, catalog dependency, state save, feedback projection, persisted feedback, review/world clocks, and undo restore through nine distinct structures in three zones. Payload chips appear only for the selected road; the explainer carries contracts, trace, route jumps, and exact source citations.
- Mechanical artifact checks, HTML parsing, and `git diff --check` pass. PinchTab verified the default and selected visual states, nine keyboard structures, eight keyboard roads, Escape reset, zero default payload tokens, exactly one selected-road token, and coherent node/road focus disclosure.
- The plan artifact is hosted at `https://acgrgnw1a8ig.postplan.dev`. The results artifact remains local because Postplan requires valid authentication for inline JavaScript uploads.

## Pass 10 Batch B — 2026-08-15

- Implemented Fish Flingers Darkan payout parity, outfit exclusion, and eight-review panel copy.
- Implemented atomic Big Top start flow and persisted executing/non-executing queue editing.

## Pass 10 Batch C — 2026-08-15

- Implemented the review-scoped derived Combat-level popup boundary.
- Fixed grouped Combat target saved-row painting and added a shown-widget pixel
  probe for saved, non-saved, and transient-selection colors.
- Split both reviewer activity progress bars into labels plus graphical fills;
  focused pure and offscreen Qt checks pass.


## Diamond in the Rough hidden rewards — 2026-08-22

- Added the two one-time postquest level-80 tomb claims without changing the
  ordinary quest-completion payout.
- The Scabaras claim grants 20,000 Mining XP, Scabaras mask, and Was; the
  Apmeken claim grants 20,000 Agility XP, Apmeken mask, and Ankh.
- Rev-742 objects 75775/75776 and items 25122–25125 preserve the action and
  reward identities; pinned pre-cutoff article revisions supply the level and
  XP values.

## Rune shard chain — 2026-08-26

- Added the sourced `make_rune_shards` Utility action: one Rune essence or Pure essence plus a retained Chisel or Hammer yields one Rune shards.
- Utility processing now resolves material alternatives and required tool alternatives before consuming inputs, so direct kernel calls fail atomically when either side is missing.
- A fresh-save real-kernel proof mines and sells 27 Clay, buys both tools from General Store stock, completes Rune Mysteries through its emitted stage actions, mines Rune essence, makes Rune shards, and grinds one Rune dust without writing quest state.
- Full plain discovery passes 4,442 tests with 506 expected skips. Reachability moves from 1,599 / 2,466 / 37 / 36 to 1,600 actions / 2,468 reachable items / 36 orphan inputs / 35 blocked actions.

## Reachability source gates — 2026-08-26

- Combat drops now join each branch-local reachability closure only after the target's runtime `quest_gate` and `quest_gate_state` are reachable; shop stock uses `shop_access_lock_reason_pure` against the same closure state.
- Conditional sources participate in the fixed point, so a reachable quest can unlock a source item that unlocks another quest without pooling mutually exclusive branch state.
- The audit moves from 1,600 actions / 2,468 reachable items / 36 orphan inputs / 35 blocked actions to 1,600 / 2,360 / 79 / 86. Exactly 108 items lose unsupported reachability certification.
- Runtime-lock regressions cover Gorak, Suqah, Glacor, and Baba Yaga's Astral-rune stock; the Rune essence → Rune shards → Rune dust positive control remains reachable. Full discovery passes 4,448 tests with 506 expected skips.

## Prerequisite quest progression repairs — 2026-08-27

- The Fremennik Trials now replaces all seven generated objective blockers with pinned wiki and Darkan actions, models Beer → Strange object and quest materials → Lyre, and treats the Hatchet as a tool. Its normal-start proof resolves both battles, and Lunar Diplomacy enters the completable closure.
- Priest in Peril now accepts its source combatdef's explicit zero combat levels with positive hitpoints and max hit, awards the monk's Golden key through real combat, and consumes it when Drezel's cell is unlocked. Missing combat stats without a sourced max hit remain blocked.
- Nature Spirit now follows six sequential sourced stages: the locally acquired Washing bowl and Mirror are no longer false prerequisites, Filliman converts Silver sickle → Silver sickle (b) + Druid pouch, and the three real Ghast battles occur only afterward.
- Fairy Tale I now accepts either fairy-ring staff, converts Secateurs → Magic secateurs, requires a Spade and Magic secateurs at their sourced gates, awards the Tanglefoot's Queen's secateurs through real combat, and consumes them at hand-in without duplicating Magic secateurs at completion.
- A fresh closure measurement moves from 33 to 39 completable quests out of 196. All four repaired prerequisites, Lunar Diplomacy, and Fairy Tale II are now inside the branch-local completable closure.
- Independent read-only review tightened the explicit-zero combat exception to actual zero values, removed superseded Golden-key and duplicate Fremennik gates, and refreshed the reward and combat-gap measuring pins. The four target quests retain zero generated objective blockers.
- Final targeted verification passes six normal-progression proofs and five reachability/promotion checks. Full plain discovery passes 4,469 tests with 506 expected Qt skips. Real offscreen Qt discovery passes the same 4,469 tests with three skips across the accepted contiguous A-L, M-R, and S-Z processes (2,301 + 1,107 + 1,061).
- The final branch-local audit reports 1,600 actions, 2,212 reachable items, 192 orphan inputs, and 284 blocked actions; its exit 1 remains the expected inherited orphan finding rather than a test failure.

## Quest requirement-shape promotion collision repair — 2026-08-27

- The merged cleanup table defined The Fremennik Trials twice through a constant
  alias and a literal ID, so the later stage-3-only tuple silently discarded the
  source-backed stages 1–7 repair. The table now keeps one literal-keyed combined
  tuple, matching its neighboring entries.
- An AST regression scans every direct `*_BY_ID` dict literal and resolves
  module-level string constants before comparing keys. It failed against the
  collided source and passes after the repair; the other mappings have no
  alias-resolved collision.
- Quest closure moves from 38 completable / 104 startable / 149 blocked stage
  rows to 40 / 109 / 148. The Fremennik Trials, Lunar Diplomacy, Fairy Tale II,
  and The Tale of the Muspah are all completable.
- Full discovery passes 4,474 tests in both lanes: plain skips 506 and real
  offscreen Qt skips three. The final reachability audit reports 1,600 actions,
  2,212 reachable items, 192 orphan inputs, and 284 blocked actions.

## MacBook-backed promotion evidence — 2026-08-27

- The pending UI branch's MacBook plain lane emitted `Ran 4507 tests in 247.142s` and `OK (skipped=513)`, then the old runner rejected that successful suite because 513 exceeded its absolute cap of 500. Verbose accounting confirmed that all 513 skips were legitimate.
- The same branch's MacBook Qt lane emitted `Ran 4507 tests in 444.064s` and `OK (skipped=3)`.
- Active coverage is the stable invariant: `tests - skipped` gives 3,994 active plain tests and 4,504 active Qt tests for those observations. Direct main runs measured 4,506/512 in 251.835s for plain and 4,506/3 in 446.244s for Qt, establishing discovery of 4,506 plus active floors of 3,994 plain and 4,503 Qt tests. A new Qt-only test can therefore increase plain skips without masking lost executable coverage.
- `python3 tools/promotion_gate.py run <promotion-worktree> --remote-lanes` sends only the serial plain and Qt lanes through the existing MacBook runner. Dispatches from this machine share a fixed absolute flock through sync and polling while the local process lives; the lock does not cover another machine or a detached lane after interruption or timeout. Run IDs prevent false evidence mixing, but an orphaned lane requires operator reconciliation before retry. Local audits, exact-commit evidence, locks, logs, and landing authority remain in the promotion worktree or canonical Git common directory; the unchanged landing command is `python3 tools/promotion_gate.py land <promotion-worktree>`.
- Preserved branches `goal/remote-promotion-gate-2026-08-27` at `d79e27473830fa9bd353e5a664bc32ea38d9f247` and `goal/remote-promotion-gate-revised-2026-08-27` at `faaed0895d98366d1d0db77ed1115ecc351902c5` are superseded by the final reviewed replacement, `goal/remote-promotion-gate-final-2026-08-27`. Both prior unmerged worktrees remain intact under the worktree safety rule.
- On the disposable MacBook mirror, the complete `tests.test_remote_test_host`, `tests.test_promotion_gate`, and global UI-asset normalization modules passed 37 tests in 18.305s.

## Safety gloves reclaim Bank refresh — 2026-08-27

- A successful Stronghold `reclaim_gloves` command now calls the existing gear
  refresh seam, so an already-initialized Bank grid repaints with Safety gloves
  immediately. The model action, chest claim path, lamp claims, and failed
  command path are unchanged.
- The focused MacBook Pro offscreen Qt regression first reproduced the defect:
  inventory gained Safety gloves while `_bank_grid_button()` raised
  `AssertionError: Bank grid item 'Safety gloves' not found`. After the dispatcher
  fix, the same selector passed one test in 1.039 seconds.
- MacBook Pro audits passed test quality (4,472 tests across 220 files, zero hard
  issues) and the asset cutoff audit. The required reachability JSON audit exited
  1 with 1,600 actions, 2,217 reachable items, 192 orphan inputs, and 284 blocked
  actions; this slice changes no item route or reachability data.
- Local Git-backed checks passed `git diff --check`, the documentation audit (597
  Markdown and 440 HTML files), and the guarded worktree audit. Closure is at the
  single commit on `goal/reclaim-gloves-refresh-2026-08-27`.

## Full global main-tab labels — 2026-08-27

- Historical record only: the `9f2b592` expanding-tab replacement and its
  native packet were valid for the 2026-08-27 slice, but the current
  tab-overflow authority is the 16x16 non-expanding policy and durable
  2026-08-28 evidence recorded above. The remaining bullets are not current
  commit or promotion authority.
- A real Anki 26.05 run at 1141×768 failed with `Gra...`, `Que...`, `Equi...`,
  `Cha...`, `Ach...`, `Coll...`, and no Settings label. The then-accepted product
  replacement was `9f2b59223f80b05cf3d2c42c8fbd705920f8fc7c`: set document mode,
  retain 18-pixel icons, explicitly expand the tab bar, and scope
  `min-width: 0px` plus five-pixel left/right padding to its tabs. Dialog width,
  labels, icons, settled order, lazy builders, Bank geometry, body layout, and
  narrow-window policy are unchanged.
- The focused shipping-QSS regression failed before the product change in all
  four cases: Anki had 1,146 natural pixels and -39 headroom, while Native had
  1,178 and -70; Settings exceeded the bar in both. The accepted product commit
  measured Anki light/dark at 1,080 natural pixels inside a 1,107-pixel bar and
  Native light/dark at 1,068 inside 1,108. Every case has at least 27 spare
  pixels, fills the wider bar, preserves exact labels and order, and allocates
  each rendered tab at or above its polished Qt hint.
- The final regression corrects one blocking test defect: on the MacBook
  offscreen lane, `QApplication.style().objectName()` is `fusion`, so the old
  `Native` branch reused Fusion. The test now imports `QStyleFactory` through
  `aqt.qt`, uses the current style only when non-Fusion, otherwise selects and
  asserts an available non-Fusion style, and keeps the exact Anki/Native ×
  light/dark matrix, shipping Anki QSS, order, natural-width and 16-pixel
  headroom checks, expansion, real Bank pointer click, shown dialog, and empty
  accept/reject checks.
- Cross-lineage Opus accepted that historical product floor. Its 27-pixel
  headroom concern beyond the exact 1140-pixel contract is a non-blocking narrow-window and
  larger-font follow-up; the 720-pixel minimum remains. Native appearance needs
  no product change because Computer Use evidence now exists. Offscreen Native
  reuse of Fusion was confirmed and fixed in the test. The proposed `hint_bar`
  `deleteLater()` is rejected because the local wrapper is replaced on each
  iteration and released at exit.
- Native Computer Use recorded a historical `PASS` for product commit `9f2b592` at
  `/tmp/ankiscape-tabs-ready-cu3.JBFRgu/report.md`. Loaded SHA-256 values are
  `508ff2e94c26c6fca9db4cbad77111e0f60d21a6b1adf247853f85a73466532a` for
  `ui/ui.py` and
  `842df7cffa5b1ed49380ad24c8e757eaf0ce70e6d747e3e615f06135ed2e8137` for
  `__init__.py`.
- Runtime order in both Anki and Native is `Skills`, `Stats`, `Bank`,
  `Equipment`, `Shop`, `Grand Exchange`, `Challenges`, `Quests`,
  `Achievements`, `Collections`, `Settings`. Every final pixel shows complete
  labels, full Settings at the right edge, no scroll controls, no clipping or
  overlap, and no horizontal body scrollbar. Anki screenshots are 1291×768;
  Native screenshots are 1109×768. The offscreen geometry gate remains exactly
  1140×768, and the Anki screenshot is not claimed as 1140 pixels wide. The only
  body ellipsis is the intentional `Search Bank...` placeholder.
- Accessibility Bank and pointer Bank activation both selected Bank and kept the
  dialog open. Settings then Skills caused no strip shift. A separate disposable
  helper add-on only recorded state and triggered the existing product `QAction`;
  it did not alter product style, geometry, data, or source. Final process proof
  found no Anki, mpv, audio, or sandbox target process; all exact Anki and mpv
  paths remained under `/tmp/ankiscape-tabs-ready-cu3.JBFRgu`.
- Failed attempt 1 used `/tmp/ankiscape-tabs-ready-cu.CyX5fz`: an empty `--base`
  under `nohup` detached Anki as PID `13773`, unexpectedly exposed the normal
  profile, and spawned mpv PID `13782` with
  `--config-dir=/Users/armantarkhanian/Library/Application Support/Anki2`. The
  run stopped before add-on staging, left no process, and did not inspect or
  repair live state. Failed attempt 2 used
  `/tmp/ankiscape-tabs-ready-cu2.0rOqKe`: isolation and exact source hashes
  passed, but the run falsely searched the macOS Anki application menu instead
  of the separate top-level `AnkiScape` menu.
- Final MacBook verification against the attribution worktree passes the
  corrected focused regression (`Ran 1 test in 2.462s`) and the complete
  main-menu module (`Ran 421 tests in 103.277s`). Both full lanes discover 4,516
  tests: plain has 513 skips and 4,003 active tests; offscreen Qt has three skips
  and 4,513 active tests. No test ran on the Mac Studio.
- Documentation audits 597 Markdown and 440 HTML files. Test quality reports
  4,481 tests across 220 files, zero hard issues, and 31 non-blocking structural
  clone groups. The scratch-report asset cutoff audit reports 616 post-cutoff
  assets and zero pending rows. `git diff --check` and guarded-worktree audits
  pass. Pinned reachability accepts the established raw exit 1 because its output
  matches 1,600 actions, 2,217 reachable items, 192 orphan inputs (40 root and
  152 cascade), 284 unresolved actions, and 1,164 seed items.
- Collections value elision (`at the north dock of...`, `at the Mining Guild in
  Falador...`, and `darkan-world-server c95aca409f397...`) remains a separate
  second-level table-layout follow-up.

## Main-menu restoration — 2026-08-29

- No owner request authorized the autonomous main-menu tab layout or style changes.
- Commits `d5da2f3a1921f6592fd4ec32c3b86542b0ca71a6` and `03ea285df1a9b7d120179e9e5bbf5356468a3b8a` remove those changes.
- `ui/ui.py` and `tests/test_main_menu_widget.py` now match the owner-settled `806a2f63` versions exactly.
- An independent Opus review accepted the restoration and found no valid replacement style test.
- The MacBook promotion gate passed at `03ea285df1a9b7d120179e9e5bbf5356468a3b8a`: both lanes ran 4,525 tests; plain skipped 513 and Qt skipped three. Documentation audited 602 Markdown and 441 HTML files, test quality found zero hard issues, reachability matched 1,600 actions and 2,217 reachable items, and worktree plus diff checks passed.
- Native confirmation still requires the owner to restart Anki normally.

## Big Chompy Bird Hunting completion — 2026-08-31

- Replaced stages 1–3's impossible generated objectives with pinned quest actions while retaining the quest's level, item, and battle gates; stage 3 now preserves the raw-chompy hand-off and Rantz, Fycie, and Bugs seasoning sequence.
- Added the quest-completion unlock and Utility/Activity producer for Raw chompy. The route consumes one Ogre arrow, retains the Ogre bow, renders the existing Raw chompy cooking icon, and produces the correct named out-of-materials failure through the real review-answer entry point.
- The actual delivered set is exactly Ogre bow, Raw chompy, Raw wild pie, and Wild pie. Their routes are the quest reward, `Utility:hunt_chompy_birds`, `Utility:assemble_wild_pie`, and `Cooking:cook_wild_pie`.
- The pinned instrument values remain 1,609 actions, 2,257 reachable items, 179 orphan inputs (37 root and 142 cascade), 266 unresolved actions, 1,182 seed items, 143 blocked quest-stage rows, and 46 completable quests.
- Nine additional Zogre/coffin items in that report are not player-reachable: the audit ignores required skills when computing startable quests, while runtime permanently blocks Zogre Flesh Eaters with `Combat 89 (not implemented)`. The six affected combat-category quests and the audit correction are recorded for the separate next slice.
- `EQUIPMENT_DATA` still has plural `Ogre arrows` and no Ogre bow row while item storage uses singular `Ogre arrow`; combat equipability remains a separate source-closure lead.
- The source audit records the exact pinned wiki revisions, Darkan revision `a2568b880390ef697b1b17e825fdef7868bed67f`, honest instrument limits, and both excluded follow-ons.

## Combat quest level requirements — 2026-08-31

- The quest requirement substrate now compares `combat` against the existing derived combat level.
- Boundary coverage passes below, at, and above combat 89. The unknown-skill sentinel remains live.
- Integration coverage passes for a blocked low-combat Zogre player and for all six affected quests at sufficient levels.
- The real add-on review path starts Zogre Flesh Eaters and reaches the key plus Zogre bones. Existing route tests cover the remaining seven item identities without quest completion.
- A max-player skill-filter probe produced the same full audit report. The before and after measurements remain 1,609 / 2,257 / 179 / 37 / 142 / 266 / 1,182, with 143 blocked rows and 46 completable quests.
- A catalog pin covers every quest-level and stage-level required skill ID, including the exact lowercase `combat` pseudo-skill.
- The focused combat quest test module passes six tests. Full lane results follow in the final verification record.

## The Fremennik Isles combat choices — 2026-08-31

- Replaced the stranded `combat_exp` completion row with two independent 10,000 XP lamp claims using the existing quest replacement and Bank Claims contracts.
- Pinned the four allowed skill IDs, minimum level 1, quantity 2, same-skill-twice behavior, refusal outside the choice set, the three unchanged fixed XP rewards, and the absence of pending XP after real review completion.
- Added a catalog-wide guard that every direct quest XP reward resolves to a trainable skill, plus an end-to-end review-answer and real claim-application pass.
- Existing completed saves receive both claims on load. Their old `combat_exp: 10000.0` pending record remains preserved but has no runtime consumer or visible effect, so no migration was added.
- The before and after reachability values are unchanged at 1,609 / 2,257 / 179 / 37 / 142 / 266 / 1,182, with 143 blocked quest-stage rows.
- Full discovery passes 4,566 tests in both lanes; plain skips 515 and offscreen Qt skips three.
- Source and migration evidence are recorded in `source-audits/the-fremennik-isles-combat-lamps-2026-08-31.md`.

## Vinesweeper reachability audit closure — 2026-08-31

- Added a Spade-gated repeatable Vinesweeper operation, 45 inventory reward buy nodes, and four Compost potion remainder actions to the shared reachability graph. Flag remains activity state and is not credited as an item.
- Pinned the operation gate, complete non-Flag buy catalog, Compost plus dose requirements, exact dose outputs, Wergali route, highest-priced Spirit seed route, and the absence of a Flag item route.
- Re-measured every audit baseline at 1,659 actions, 2,270 reachable items, 167 orphan inputs, 32 root orphans, 135 cascade orphans, 256 unresolved actions, 1,182 seed items, and 143 blocked quest-stage rows.
- The twelve newly reachable player items are Wergali seed, Grimy wergali, Clean wergali, Wergali potion (unf), Crafting potion (1)–(4), and Compost potion (1)–(4); the synthetic point currency is the thirteenth new graph route.
- Runtime proof forced all 170 operations into a maximum-award band, reached the 55,250-point ceiling for that sequence, and bought the 55,000-point Spirit seed. This proves attainability rather than typical pacing: ordinary play averages about 130.45 points per operation and needs roughly 424 operations to reproduce that balance.
- Forty-two of 44 seed/spore rewards have live Farming consumers. Bittercap mushroom spore has none, while Spirit seed leads only to a source-blocked Spirit tree crop; both are recorded follow-ons, not inflated into this slice.
- Focused coverage passes 74 tests. Full discovery passes 4,567 tests in each lane: plain skips 515 and real offscreen Qt skips three.
- Evidence: `source-audits/vinesweeper-loop-2026-07-18.md`.

## Early quest item roots — 2026-08-31

- Normalized all Pirate's Treasure predicates and stage actions to `Karamjan rum` while preserving the existing item and shop identity.
- Added sourced, live Utility acquisitions for Ugthanki dung, Fish food, and Insect repellent, including item `4601` and a started-The-Feud unlock for the dung route.
- Added the existing Agility stage-output shape to the reachability action table, making `Pyramid top` visible without adding a second producer.
- Replaced the completed-quest karambwan fishing gate with the existing `quest_started` target-rule form and changed Tiadeche's generator-owned shop access from completed to started.
- Added focused route, runtime production, unlock, registry, downstream cascade, a full real-runtime Agility Pyramid lap, and real review-answer coverage in `tests/test_early_quest_item_routes.py`.
- Re-pinned the rebased report from 1,659 / 2,270 / 167 / 32 / 135 / 256 / 1,182 and 143 blocked rows to 1,663 / 2,301 / 165 / 32 / 133 / 252 / 1,215 and 139 blocked rows.
- The report gains 31 routes. Twenty-one are existing quest-owned routes; the larger-than-expected cascade is measured rather than filled with duplicate producers.
- Two later combat encounters become the next visible blockers: `dealing_with_scabaras_skeletons_1` and `tai_bwo_wannai_trio_monkey`. They remain for the separate combat data slice.
- Source and visual evidence are recorded in `source-audits/early-quest-item-roots-2026-08-31.md`.

## Quest combat gate fallback — 2026-08-31

- Reversed both runtime enemy-level fallbacks and aligned the reachability model: missing `minimum_player_combat` now means no aggregate player gate.
- Confirmed Smoking Kills and Dream Mentor already carry quest-entry Combat 85 requirements, retained all ten explicit encounter gates, and documented why the four now-redundant gate-1 rows remain.
- Added catalog-wide, explicit-boundary, quest-entry, ordinary-combat, and real review-answer coverage. Updated the pre-existing Count Draynor regression to expect an ungated combat encounter rather than an inherited level gate.
- Re-measured 293 encounter rows: 91 lack resolver stats, 64 previously inherited an above-ceiling gate, and 24 are in both groups. The impossible union moves from 131 to 91, so this slice clears 40 encounters while leaving the stat-sourcing backlog unchanged.
- Reachability remains 1,663 / 2,301 / 165 / 32 / 133 / 252 / 1,215, with 139 blocked quest-stage rows and 51 completable quests. No pin moved because earlier required-action blockers still stop the affected branches before their combat rows.
- Focused verification passes 64 tests. Source and measurement evidence are recorded in `source-audits/quest-combat-gate-fallback-2026-08-31.md`.

## Shared global quest-action proofs — 2026-08-31

- Added a durable, global, forward-only proof ledger and moved quest action gates off the quest-local stage-action ledger.
- Added declarative proof rules for Do No Evil's M'amulet mould purchase, The Fremennik Isles' cure-and-stitch sequence, and Biohazard's cross-quest Mourner food sabotage.
- Added config-122 migration coverage that rejects all telemetry, inventory, completed-quest, and local-stage backfill for old saves.
- Added unit, pure-flow integration, real Shop/Crafting, Shop rollback, real review-answer, earned-proof reachability, and recursive production-writer ownership coverage.
- Kept `core/storage_pure.py`, `logic/shop_logic.py`, `logic_pure/logic_pure_quest.py`, and `tools/audit_item_reachability.py` line-neutral or smaller. Mutation probes prove the rollback and audit tests fail without their fixes.
- Added a catalog pin for 528 unique auto-action IDs, single-quest ownership, and zero cross-quest required-action overlaps. Duplicate-auto-owner and cross-quest-gate mutation probes each fail this pin.
- Deliberately left eight unsupported hand-written actions and all 693 generated sentinels. No user interface changed.
- Evidence: `source-audits/shared-quest-action-proofs-2026-08-31.md`.
- Both complete lanes pass 4,596 tests: plain skips 515 and real offscreen Qt skips three.

## Quest proof store clean break — 2026-09-01

- Removed `quest_stage_actions` from live defaults, nested player copies, quest-stage writes, and six split-module re-exports. `core/storage_pure.py` now keeps only the unconditional migration pop for old saves.
- Bumped config version 122 to 123. Pre-122 proofs remain forward-only and empty; v122 proofs sanitize and survive. The empty `RETIRED_QUEST_ACTION_PROOFS` set is subtracted whenever the loaded version is older than `CURRENT_CONFIG_VERSION`, so the shipped cohort is covered by the next schema bump.
- Added migration coverage for dropping the retired key, subtracting a retired proof, restoring the required-action blocker, preserving a non-retired proof, and retracting from the current cohort under a simulated next schema bump. Extended the production census across root and generated files with assignment, alias, mutation-method, and pop-alias probes.
- Moved all 213 old-store assertion sites to the global proof ledger or explicit migration-removal expectations. No assertion was deleted. The 18-line shared helper now compares the complete per-quest proof view, so injected over-recording fails both pure-runtime and dynamic-package integration tests.
- Re-measured unchanged reachability at 1,663 actions, 2,301 reachable items, 165 orphan inputs, 32 root orphans, 133 cascade orphans, 252 unresolved actions, 1,215 seed items, 139 blocked stage rows, and 51 completable quests.
- Re-measured unchanged reachability at 1,663 actions, 2,301 reachable items, 165 orphan inputs, 32 root orphans, 133 cascade orphans, 252 unresolved actions, 1,215 seed items, 139 blocked stage rows, and 51 completable quests. Full plain verification passes 4,601 tests in 769.861 seconds with 515 skips; real offscreen Qt passes 4,601 tests in 1,036.410 seconds with three skips. No UI code changed.
- Evidence: `source-audits/quest-proof-store-cleanup-2026-09-01.md`.
