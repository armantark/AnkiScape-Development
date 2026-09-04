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
