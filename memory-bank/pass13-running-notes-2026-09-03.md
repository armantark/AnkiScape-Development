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
