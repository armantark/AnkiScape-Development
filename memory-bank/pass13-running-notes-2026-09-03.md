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
