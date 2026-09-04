# Pass 13 running notes — 2026-09-03 (autonomous overnight run)

Design seat compiles these into the results artifact at the end. Plan artifact:
`memory-bank/status-updates/pass13-plan-2026-09-03.html` (hosted
https://bao16xkvfzrc.postplan.dev). Brief:
`memory-bank/codex-briefs/pass13-owner-notes-handoff-2026-09-03.md`.

## 22:51 — Fish Flingers: the formula is source-true; S9 changes shape

Research (Terra, read-only, 2012 wiki revisions plus Darkan) found:

- The add-on's payout `floor(max(162, 235*level - 73) * score / 48)` is
  Darkan's restored November 2012 formula
  (`darkan-world-server/.../fishflingers/FishFlingersDomain.kt:98-140`).
- Wiki oldid 5185520 (2012-01-25): "The cap of the experience is just under
  20,000", maximised at level 62; its table gives level 50 = 8,630 XP at top
  score. Interpolated level 39 ≈ 6,930 XP. Post-24-July-2012 the score model
  changed but the XP scale did not (patch notes oldid 5983555).
- Frequency in 2012: two tickets per day, ten stored. The add-on grants two
  per 240 answered cards and stores ten (`data/fish_flingers_data.py:25-29`).
- No per-game record is persisted (score, XP, level); the event log keeps
  text only. An exact rollback of past games cannot be computed.

Ruling applied: the owner wants "the same amount of xp you'd get from a normal
fish flingers game in the real 2012 game" and no invented rates. That is what
ships today, so the formula does not change and no rollback is possible or
warranted. S9 becomes a records slice: persist each settled game (score, XP,
Fishing level, review index) so any future dispute is answerable exactly.

Owner gate for the morning (not a blocker): the perceived "insane" size comes
from the per-card skilling scale (trout 50 XP per card) against a per-game
2012 sum (about 7,000 XP at level 39). The two clocks differ by design. If the
owner wants D&D sums to feel proportionate, the lever is a design decision on
the skilling clock, not the Fish Flingers formula.

## 22:50 — Dispatch state

Running: S2 (Sol), S3 (Sol), S5 (Sol), S4 (GLM), S6 (GLM), S7 (GLM), Ardougne
creative draft (Kimi). Queued: S8 tool (Sol), S9 records (GLM), creative
drafts for the other eight regions, Fable review of every drafted row.

## 22:53 — Owner steer on S5: a quest boss is a combat instance

Owner: "it should still start a combat instance like any enemy. It's a quest
boss." Code check: `apply_quest_combat_encounter_pure`
(`logic_pure/logic_pure_quest.py:1328+`) builds a quest enemy spec, runs the
shared combat engine with review ticks, persists progress in
`quest_combat_active_encounters`, and handles death. S5 is steered to prove
that path with tests (loadout, food, prayers, death, current target shown)
and to report any gap rather than expand scope.

## 23:27 — Ardougne creative draft reviewed

Kimi drafted 28 rows in 36 minutes (7 points of the Kimi block, mostly
registry exploration). Design-seat review: 26 pass; two sent back on
difficulty (`i_wonder_what_this_does` used Dareeyak Teleport, Magic 78, in a
medium tier; `get_your_stinking_hands_off_me` used a level-3 monkey in a hard
tier). Kimi also writes `/tmp/pass13-diary/context-pack.md` so the other eight
regions read ids and taken seams instead of exploring. Two findings for S1:
`_validate_row_metadata` rejects designed text on translated rows (must be
relaxed), and the shop-diary-transaction allowlist in
`logic_pure/shop_diary_transactions.py` is closed (no new shop seams without a
code change).

## 23:39 — Reroute the remaining creative drafts off Kimi

The Kimi block is over pace (45 of a 43 pace at 23:39, reset in 22h32m); the
eight remaining regions would finish before the reset, so the drafts reroute:
GLM 5.3 Flash drafts each region from the context pack on a plain brief, and
the design seat (Fable) reviews every row and rewrites names and sentences
that miss the bar. Kimi finishes only the context pack and the two Ardougne
fixes already in flight. S3 and S5 paused with their test lanes running.

## 23:56 — S4 bones-learned on its branch

`goal/pass13-bones-learned-2026-09-03` at `ea18b54e` (GLM). Drops are
recorded before the bury step at three kill sites; a "leave" override on a
prayer material skips its burial; tests in `tests/combat/test_auto_bury_bones.py`
(new subdirectory because `tests/` sits at the gate's 40-file cap). Reverting
the burst-path reorder fails the learning test. Pre-existing: the loot filter
leaves a zeroed `"Bones": 0` key on a "leave" override; item-reachability audit
exits 1 on the untouched baseline (White lily seed, White tree sapling, Wimpy
feather). Review: Opus, pending.

## 00:02 — Varrock draft reviewed and fixed

GLM drafted 22 rows in 13 minutes on the context pack (text only). Review:
19 pass; three fixed by the design seat after the GLM resume failed with a
provider refusal: Engage now burns ten willow logs as balloon fuel (the
teleport clause duplicated Quick Turnaround); Point of En-tree cuts a yew
behind Varrock Palace (a grown spirit tree needs Farming 83); Tunnel Vision
keeps Dorgesh-Kaan with a recorded region compromise, because shortcuts have no
runtime and no Varrock-region agility course exists in the 2012 model. Flag for
the owner's spot-check: `varrock_hard_but_it_won_t_warp_you_anywhere`.

## 00:04 — S4 review (Opus): ACCEPT-WITH-FINDINGS, sent back

High: the first-sighting keep default seeds from post-bury drops, so a bone
learned under auto-bury has no default and is left once auto-bury turns off
(`runtime/runtime_actions_combat.py:594-598`). Medium: the "leave" override is
honoured only in the burial loop; urned ashes and Bonecrusher bones ignore it
(`logic_pure/logic_pure_urns.py:389-410,336-343`). Test gap: finisher path
unexercised. Verified: three kill sites are the only ones; `"Bones": 0` is
pre-existing and not user-visible; `tests/combat/` is collected by both lanes
and the test-quality audit. The S4 author re-leases the branch for the fixes.

## 00:05 — S7 glory-ge on its branch

`goal/pass13-glory-ge-2026-09-03` at `34fbf491` (GLM). Amulet of glory and
(4) tradeable (Amulet of glory oldid 6469621, 2012-10-25: noted on the GE as
"Amulet of glory" and "Amulet of glory(4)"); exchange rows regenerated through
the generator; (t1) to (t3) stay off. Plain lane 4,678 OK. Five module-surface
digest pins refreshed (derived constants moved). The generator's header wording
was changed so the gate's generated-blob exemption recognizes the file; review
checks that this is the intended mechanism, not a bypass. Review: Opus, pending.

## 00:15 — S7 review (Opus): ACCEPT-WITH-FINDINGS, two fixes sent back

Verified on primary evidence: the 2012-10-23 buy-limit table (oldid 6457777)
lists Amulet of glory, (4), (t), (t4) only; the harvested Exchange rows match
oldids 6570084 and 6570085 exactly. The gate exemption keys on
`auto-?generated|do not edit|@generated` in the first five lines
(`slop_gate.py:110-115`); the file is a generator-emitted blob, so the header
change is the intended mechanism, not a bypass. Fixes sent: (t1) to (t3) must
be untradeable too; the test must pin the two oldids.

Second-level findings (surfaced, not fixed): 106 items are `tradeable=False`
while the 2011 cache flags them exchangeable (69 summoning pouches, 37
NPC-shop clothing and misc), from `MiningBonusItem.tradeable` defaulting to
False (`data/mining_data.py:98`) and the shop generators defaulting the same
way. `ROOT_QT_DIGEST` in `tests/test_module_surface.py:29` is
checkout-path-dependent. The fleet gate drops an exempt generated file from
every check, not only the line cap (`slop_gate.py:124-132`).

## 00:19 — S4 CLOSED on its branch

`goal/pass13-bones-learned-2026-09-03` at `1a89c254`. Review findings fixed:
keep-default seeding reads the observed drop names outside the drops guard;
one shared "leave" override filter drives Bonecrusher, urn ash charging, and
auto-burial; finisher-path learning test on the desert lizard fixture. Each of
the three fixes fails exactly its own test when reverted. Full widget suite
last ran whole on the pre-review tree; the promotion gate re-runs it on the
merged tree.

## 00:20 — Karamja draft complete (20 rows)

Five review fixes applied by the drafter: lesser demons beneath the volcano
(amount 2; amount 1 is owned by a Lumbridge row), the Jungle Potion search
sentence set at its real place south of Tai Bwo Wannai, "Avast, Anchovies!"
on the Brimhaven net spot (easy), "Set in Stone" on Shilo gem rocks (Mining
40 behind the Shilo gate, medium), and "Brim Full of Tickets" earning 25
Agility Arena tickets (elite). Design seat renamed Here Be Dragons to Here Be
Demons. No Brimhaven or Shilo shop exists in the closed transaction registry.

## 00:22 — Falador draft reviewed, six rows back

GLM drafted 19; the two owner-named rows now read as real deeds (the rat-pit
champion at level 26; big-net catches off Mudskipper Point). Sent back: Family
Values (Construction 48 in easy), Pipe Dreams (Agility 1 pipe for a 26 source),
Child of Saradomin (Crafting 16 in hard), A Knight in the Darkness (one monk in
hard), Mudskips (Fishing 16 x10 is not hard; bass output instead), and the
flagged elite row Disarm and Embark (invent an elite in-region deed). Finding:
`shaikahan` resolves through bone_sources and prayer data, not
COMBAT_ENEMY_DATA. Six Falador sentences ride the rule 2 exception; each notes
field argues it.

## 00:28 — Seers draft reviewed, five rows back

GLM drafted 14. Sent back: the two elite-display rows (Beware of the Dog on
Farming-28 hops; Happy Hour on 25 beers) need real elite seams (Catherby
torstol; an invented fletching or magic-tree deed); the air battlestaff
(Crafting 66) in a medium row becomes a water battlestaff (54); the Ranging
Guild round gets a count; Dairy Air names its place. Pattern across GLM
drafts: count raises stand in for difficulty; the reviewer must reject that.
Fremennik drafting; Burthorpe and Lumbridge still drafting.

## 00:33 — Burthorpe draft accepted (14 rows)

Single beginner tier; the earlier curation had already replaced every dead
seam, so this was a text pass: seven renames (Troll Patrol, Cannonball Run,
Cut to the Chase, Feeding Frenzy, Lap of Luxury, Batch Expectations, Trout and
About) and seven kept names. Accepted without changes. Region status: Ardougne
28, Varrock 22, Karamja 20, Burthorpe 14 complete; Falador and Seers on fixes;
Lumbridge, Fremennik, Morytania+misc drafting.

## 00:36 — Falador draft complete (19 rows)

Six fixes applied: Family Values casts a silver holy symbol (Crafting 16,
easy); Pipe Dreams uses the Barbarian Outpost pipe (Agility 35); Child of
Saradomin buries five dagannoth bones (hard); A Knight in the Darkness defeats
five level-45 Monks of Zamorak; Mudskips lands five bass (Fishing 46, output
seam); Disarm and Embark becomes the invented elite "Arming the White Knights"
(forge an Adamant platebody, Smithing 88), disposition now `invented`. Regions
complete: Ardougne, Varrock, Karamja, Burthorpe, Falador (103 rows). Seers on
fixes; Lumbridge, Fremennik, Morytania+misc drafting.

## 00:38 — Fremennik draft reviewed, one row back

GLM drafted 12; one seam change accepted (Moonclan Teleport for the
hard-display row, in region). Sent back: the elite row on three pyrefiends
(level 43); a Dagannoth King, a kurask (Slayer 70), or a counted Waterbirth
dagannoth replaces it.

## 00:39 — Seers draft complete (14 rows)

Fixes applied: "Weed It and Reap" harvests grimy torstol at Catherby (Farming
85, elite); "A Long Story" strings a magic longbow (Fletching 85, elite,
disposition `invented`); water battlestaff (Crafting 54) for the medium row;
five Ranging Guild rounds; Dairy Air at the Sinclair Mansion. Regions complete:
Ardougne, Varrock, Karamja, Burthorpe, Falador, Seers (117 rows). Fremennik on
one fix; Lumbridge and Morytania+misc drafting. S8 icon sweep at its commit.

## 00:41 — S7 CLOSED on its branch

`goal/pass13-glory-ge-2026-09-03` at `05c413f7`. (t1) to (t3) untradeable
with the oldid 6457777 citation; the test pins oldids 6570084 and 6570085;
`tests/test_mining_data.py` corrected to the 2012 shape; plain lane 4,678 OK.
Closed slices: S4, S7. Branches pending: S2, S3, S5, S6, S8. S9 records slice
dispatched to GLM.

## 00:45 — Fremennik draft complete (12 rows)

"The Lighthouse Keeper": three level-92 dagannoths beneath the Lighthouse
(kurask and the Dagannoth Kings are not modelled). Design seat restored the
frozen `original_tier` on fairy_mountaineering (the drafter had set it to
hard). Regions complete: seven, 129 rows. Lumbridge (21) and Morytania+misc
(12) remain.

## 00:50 — S9 fish-flingers-records on its branch

`goal/pass13-fish-flingers-records-2026-09-03` at `6467d08e` (GLM). Each
settled game appends score, XP, Fishing level, review index, and medals to
`fish_flingers_game_log`, newest 50 kept, sanitized on load. Payout untouched.
Four tests; 21 pass in the Fish Flingers file. Review: Opus, pending.

## 00:55 — S9 review (Opus): ACCEPT-WITH-FINDINGS, three low fixes sent back

Recorded level must be clamped as the payout clamps it; the abandon path
needs a pin; the missing-key test must be a real round trip through
`migrate_loaded_data` (the storage layer has no key whitelist and calls the
sanitizer unconditionally, so no version bump is needed).

## 00:58 — S9 CLOSED on its branch

`goal/pass13-fish-flingers-records-2026-09-03` at `acdc740b` (verified on
the branch). Clamped level recorded; abandon path pinned; round-trip tests
through `migrate_loaded_data`. Closed: S4, S7, S9. Pending branches: S2, S3,
S5, S6, S8. Drafts pending: Lumbridge, Morytania+misc.

## 01:01 — S8 icon sweep on its branch; the Iron scimitar explains the wider class

`goal/pass13-icon-2012-sweep-2026-09-03` at `78fa0f83` (Sol). 135 icons
replaced with the newest RuneScape wiki revision strictly before
2012-11-20; 144 had no exact-title pre-cutoff revision (audit file lists
each; most enemy images use titles that do not exist on the RS wiki, and
"Guard.png" has only post-cutoff revisions). Design seat viewed
`smithingitems/mithril_platebody.png` before and after: the new one is the
2012 detailed design. Review: Opus, pending.

Iron scimitar (owner's Pass 8 note) was outside the sweep: its provenance is
the RS wiki title "Iron scimitar (September 2009).png", a dated historical
look, fetched 2022. So the class is wider than Old School sources: any entry
whose title is a dated historical image, or whose recorded revision is not
the newest strictly before the cutoff, shows the wrong period. A second sweep
over every RS-wiki entry with the same tool is the class fix; decide after the
S8 review.

## 01:06 — S8 review (Opus): REJECT, fixes sent back

High: 35 icons were fetched through `%21`-encoded archive URLs that the
repo's own `fetch_resolved_assets.py:118-122` documents as serving a wrong
revision; the tool shipped the bytes with the API hash. Fix: literal `!`,
re-fetch, skip on mismatch. Medium: recorded sha1 and size describe different
bytes, so reruns re-encode. Also: add `redirects=1` (17 of 75 missed titles
are capitalisation renames), drop `fetch_date`, produce the contact sheet,
simplify about 150 lines, add the missing tests. The wider sweep over every
RS-wiki entry (Iron scimitar class) waits for this to land as S8b.

## 01:11 — Lumbridge draft complete (21 rows)

Fixes: "Spin Doctor" spins wool at Lumbridge Castle (beginner); "Rune With
It" sentence set at the Wizards' Tower mine; "Come In Here and Say That"
casts Enchant Opal bolts from the tower top (Magic 4; Wind Strike is a
combat cast and not a recorded Magic target); "Bark Up the Churchyard" cuts
five yews behind Lumbridge church (Woodcutting 60, hard, invented). Eight
regions complete, 150 rows; Morytania plus the Miscellaneous row remain.

## 01:13 — Morytania reviewed from the file; S1 stage 1 dispatched

All 162 draft rows exist (merge dry run: 0 missing, 0 problems). Morytania:
8 of 12 pass; sent back a level-1 torch in a hard row (yew logs instead), a
vampyre in an elite row (Vyrewatch, abyssal demon, or gargoyle), an "any
crop" allotment (pin strawberry or watermelon), and the temple-trekking route
choice. S1 stage 1 (Sol): `text_for` and the validator require designed text
on translated and invented rows; stage 2 merges the drafts and regenerates
after Morytania's fixes land.

## 01:15 — All nine regions drafted and reviewed (162 rows)

Morytania complete: silvthril chain (Crafting 47) for the key row; yew-log
burn in the Haunted Woods (Firemaking 60); a gargoyle (Slayer 75) for the
elite row (no Vyrewatch enemy exists); watermelon pinned at Port Phasmatys;
temple trekking keeps `ramble_any` x3 (no per-route counter exists). Flagged
for the owner: `morytania_medium_izzy_wizzy_let_s_get_lizzy` displays hard on
a swamp-lizard seam (Hunter 29), the only Hunter target in Morytania;
`varrock_hard_but_it_won_t_warp_you_anywhere` on Dorgesh-Kaan. Merge dry run:
162 of 162, 0 problems. Stage 2 of S1 merges when stage 1 reports.

## 01:16 — S3 bankstand-single-notice on its branch

`goal/pass13-bankstand-notice-2026-09-03` at `49d23a5c` (Sol). Material
exhaustion routes its reason into the deferred modal; a branch that keeps a
local refusal popup suppresses the modal. Both full lanes green (plain
4,682 in 981 s; offscreen 4,682 in 1,319 s). New tests in
`tests/runtime_actions/test_bankstanding_notice.py`. Review: Opus, pending.

## 01:23 — S3 review (Opus): ACCEPT-WITH-FINDINGS, six fixes sent back

The mechanism is one seam change: a local popup clears `show_dialog` on the
pending notice (`__init__.py:1327-1329`), so the rule holds at about 150
sites, touched or not. Findings: combat classes empty `reasons` as material
(fallback unreachable); Dungeoneering "not in a session" gets a modal while
three sibling activities keep a popup; the suppression flag is sticky across
ticks on the reused context; a dropped reason; dead
`_deactivate_current_skill`; a KeyError-prone test. `tests/runtime_actions/`
is collected by `run_tests.py` and the gate lanes.

## 01:33 — S1 stage 1 committed; stage 2 dispatched

`goal/pass13-diary-deed-text-2026-09-03` at `01603bde` (Sol): `text_for`
and the validator require designed text on translated and invented rows;
160 tests pass with a temporary overlay. Stage 2 merges the 162 drafted rows
(123 translated, 39 invented), regenerates the catalog, and adds the test
that no translated or invented task carries its source name or sentence.

## 01:38 — S1 stage 2 blocked once, unblocked

The generator rejected `lumbridge_hard_a_body_in_the_sewers`: its drafted
sentence equalled the source sentence, which the new validator forbids. The
design seat found seven such rows across the drafts and reworded them
(for_fast_transactions, the_stonemasons, a_cat_is_for_life, brace_yourself,
arm_the_militia, master_of_all_i_survey, a_body_in_the_sewers). Stage 2
resumes: merge, regenerate, tests. Pending markers stay until regeneration
succeeds, per the precedent in `028df5f9` and `a0e22ade`.

## 01:39 — S3 CLOSED on its branch

`goal/pass13-bankstand-notice-2026-09-03` at `78b5767f`. All six findings
applied; 489 focused tests pass; full lanes deferred to the merged-tree gate.
Closed: S3, S4, S7, S9. Pending: S1 stage 2, S2 (status requested), S5 (Qt
lane), S6 (tests), S8 (fixes on plain lane).

## 01:47 — S1 stage 2: catalog regenerated; one more seam fixed; test relaxed to sentences

The generator rejected four drafted seams that collided with active catalog
rows (the context pack's digest covered only the ledger), then one more
(mining:gold, owned by karamja_easy_golden_shores). Design seat replaced them:
mithril ore in the Dwarven Mine, a gold ring at the Falador furnace, five
maple fires in the Haunted Woods, a lobster over the Lumbridge Swamp campfire.
Regeneration then succeeded: 162 rows, all 162 markers cleared per precedent,
no source sentence remains. The stage 2 test as briefed also forbade kept
names; 78 rows keep their source name by rubric rule 5, so the test now covers
sentences only.

## 01:56 — S6 target-level-order on its branch

`goal/pass13-target-level-order-2026-09-03` at `25d6f3d9` plus a papercuts
note at `58ed22a3` (GLM). Every row builder sets `sort_key=(level, label)`;
the tree and flat renderers sort by it; dead hand-curated orders in
Fletching and Hunter removed (they put 10 before 9). Tests in
`tests/skills/test_target_level_order.py` (851 assertions across skills).
Review: Opus, pending. Visual check: once on the merged tree with S2.

## 01:59 — S1 diary-deed-text on its branch

`goal/pass13-diary-deed-text-2026-09-03` at `e4223bec` (stage 1 `01603bde`).
162 rows merged (123 translated, 39 invented); 10 family modules regenerated;
162 of 474 task rows changed; longest sentence 86 characters; 0 pending
markers. Diary, integration, ledger, shop suites 204 passed; reproduction
test passed; offscreen UI suite 16 passed. Review: Opus, pending. Owner
spot-check of the rewritten rows is the morning gate (queue §4.22 ruling 3).

## 02:01 — S6 review (Opus): ACCEPT-WITH-FINDINGS, five fixes sent back

High: the two tree hunks regress group order for Smithing, Crafting,
Construction, and Cooking (main already sorted children by key; only the
flat hunk was needed). Medium: eight builders still lack a level-first key
(Prayer sorts by xp; five lead with a group index; Smithing inserts a flag).
Ruling recorded: every skill key is (level, label); trees keep group order
with level inside; flat lists sort by level regardless of group; the
Activities list stays alphabetical (Pass 7). Medium: the data tests were
tautological. Low: `sort_order` is now dead data in two files.

## 02:08 — S1 review (Opus): ACCEPT-WITH-FINDINGS, four rows and docs sent back

Verified: validator rules, harvest-derived source-sentence test, reproduction
of all 474 rows, exactly 162 rows changed (162 descriptions, 63 names, 39
conditions), zero anchor/active/dormant changes, 211 tests pass. Four rows
missed the rubric and are replaced by design-seat decision: Ardougne
unicorn (elite) becomes torstol at the Ardougne herb patch; the Knight attempt
(elite) becomes a Hero pickpocket; the Falador Shaikahan row re-sites to a
Black Knight at the fortress; Varrock's Oziach purchase (elite) becomes a
magic shortbow for Lowe's. README marker rule and the `translated`
definition corrected; apostrophes normalized.

## 02:13 — S8 corrected on its branch

`goal/pass13-icon-2012-sweep-2026-09-03` at `10d15b28` (over `78fa0f83`).
100 icons replaced with hash-verified pre-cutoff bytes (Mithril platebody
among them); 35 restored to their originals because the archive bytes never
matched the wiki's hash even through the literal-`!` path; 179 misses audited
(83 absent titles, 61 post-cutoff only, 35 hash). Redirects resolved none of
the 83. Plain lane 4,682 OK. Contact sheets under the pool slot's tmp dir.
Re-review of the corrective commit: Opus, pending.

## 02:17 — S8 re-review (Opus): ACCEPT-WITH-FINDINGS on documentation only

All seven prior findings fixed or applied; all 100 replaced icons hash to
their provenance; the 35 mismatched assets are byte-identical to main. Two
doc fixes sent: the audit's result line must describe the change against
main, and the 19 contact sheets go into `memory-bank/evidence/` for the
owner's eyes.

## 02:18 — S5 quest-combat-flag-removal on its branch

`goal/pass13-quest-combat-flag-2026-09-03` at `44c4e7dc` (Sol). The flag
and both messages are gone; a migration drops the key. Proofs: Delrith
spans three reviews, resumes persisted life points, uses the player's Bronze
sword, Shrimps, and Burst of Strength; a Delrith win routes through ordinary
gravestone death. Gap left open on purpose: the HUD shows the quest name
while Quests is active, not Delrith as current target (`ui/ui.py:1557-1574,
2965`). Promotion-gate test timeout 0.2 to 2.0 s (two loaded offscreen runs
raced `child.pid`). Plain lane 4,678 OK.

Owner data gap (named gate for the morning): 91 of 293 quest combat
encounters across 47 quests carry no combat stats and still refuse to
resolve. Largest: rag_and_bone_man 8, the_chosen_commander 6,
land_of_the_goblins 5, love_story 5, while_guthix_sleeps 5, the_elder_kiln
4. Full list in the S5 report (transcript) and to be copied into the results
artifact. Review: Opus, pending.

## 02:22 — S8 CLOSED on its branch

`goal/pass13-icon-2012-sweep-2026-09-03` at `c27ceb26`. Audit states the
effect against main (100 replaced; 179 unusable: 83 absent titles, 61
post-cutoff only, 35 hash mismatches); 19 contact sheets committed under
`memory-bank/evidence/icon-2012-sweep-2026-09-04/`. Closed: S3, S4, S7, S8,
S9. Pending: S1 (row fixes), S2 (commit at gate), S5 (review), S6 (fix at
gate). Second-level for the owner: the Iron scimitar class (dated historical
titles on RS-wiki entries) needs a second sweep over every RS-wiki entry.

## 02:23 — S5 review (Opus): ACCEPT-WITH-FINDINGS, five fixes sent back

Verified: no trace of the flag in executable code; migration at
CURRENT_CONFIG_VERSION 124 chained and tested; the persistence tests drive
the real dispatcher (three reviews, enemy LP carried, Bronze sword, food,
prayers, gravestone death); the 2.0 s timeout is a deflake. Findings: the
stat-less message still says "before battle support can resolve"; a
systemPatterns line and fifteen audits still describe the flag; questing
deactivates silently on two paths; the `__main__` guard sits above the new
test class; migrated saves keep an orphan `{"version": 1}` dict. Visual
check of S8: the smithing contact sheet shows the 2012 detailed designs.

## 02:25 — S1 CLOSED on its branch

`goal/pass13-diary-deed-text-2026-09-03` at `301bb9e7`. Four deeds
replaced (torstol at Ardougne, Farming 85; Hero pickpocket; five Black
Knights, since ice_giant is owned by falador_medium_ice_the_icy; magic
shortbow for Lowe's); ASCII apostrophes throughout; README corrected; 33
generated tasks changed in the fix; census unchanged. Closed: S1, S3, S4,
S7, S8, S9. Pending: S2 (commit at gate), S5 (fixes), S6 (fix at gate).

## 02:34 — S6 CLOSED; batch worktree opened

`goal/pass13-target-level-order-2026-09-03` at `8fffa205`. Tree hunks
reverted (main's group behaviour exact); seven builders now lead with level;
`sort_order` dead data removed; tests read levels from rendered labels. The
builder-local `group_order` dicts that were deleted fed only the sort key;
the tree renderer takes its group lists from the UI call sites, unchanged.
Closed: S1, S3, S4, S6, S7, S8, S9. The design seat leases a batch
worktree and merges the seven closed branches; S2 and S5 join when their
gated commits land.

## 02:41 — S5 CLOSED; eight branches in the batch; S6 visual check passed

S5 at `318ad7ae` (stat-less message now "This fight is not modelled yet
(combat stats missing): …"; `quest_combat_config` dropped entirely at v124;
player LP carryover proven; source-audit supersession index added). Batch
worktree `goal/pass13-batch-2026-09-04` (pool slot 2) holds S1, S3, S4, S5,
S6, S7, S8, S9 merged with zero conflicts, head `74c15e5d`. Offscreen
screenshots on the merged tree (`/tmp/pass13-shots/`): Herblore "Clean
herbs" reads guam 1, ardrigal 3, rogue's purse 3, sito foil 3, snake weed 3,
volencia moss 3, marrentill 5, tarromin 11; Mining reads clay 1 through
sandstone 35. No truncation inside the lists. Second-level, pre-existing: at
an 1100 px window the tab strip clips "Collections" behind a scroll arrow.
Only S2 remains, at its gated commit. S5's author flags papercuts.md past
the cleanup threshold; a papercut-fix pass is proposed in the results.

## 03:07 — S2 on its branch; all nine merged into the batch

S2 `goal/pass13-activity-one-click-2026-09-03` at `f75c3cdf` (Sol).
Reproduction: from Activities, Shooting Stars and Evil Tree armed the
target, left "Training: Mining", disabled the control as "Selected for
reviews", and never started. Now every path reaches
`_start_surface_activity` in one click. Screenshots in
`~/.t3/userdata/attachments/activity-one-click-screenshots-2026-09-04/`.
Design-seat copy fix sent: "Select active star" becomes "Mine this star",
"Select tag only" becomes "Tag this star". Review (correctness plus
frontend taste): Opus, pending. Batch head `d2992b23` holds all nine
branches, zero conflicts. Gate runs after the S2 relabel lands.

## 03:14 — S2 review (Opus): ACCEPT-WITH-FINDINGS, two high; fix pass sent

High: routing selections through `on_start_activity` bypasses
`commit_direct_action`, the undo seam, for about forty selections; fifteen
`elif not _request_utility_selection(...)` sites became unconditional, so a
declined "Leave …?" falls through. Medium: four landmark rows still arm
without starting. Tests weakened (Fist of Guthix start, circus icon). Taste:
four more "Select …" labels start now; "Selected for reviews" names a
running state; the header "Start activity" reads as a second step; Evil Tree
requirements wrap mid-pair at 900 px; disabled "Exchange stardust" reads as
an action. Copy rulings recorded in the message to S2. The batch gate waits
for this commit.
