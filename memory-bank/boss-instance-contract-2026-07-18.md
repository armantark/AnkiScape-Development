# Boss instance contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-settled shared contract closing the DEEP GRILL boss card
(Fight Kiln, God Wars, Corporeal Beast, Nex); per-boss values are harvest
work.**

## The pattern

Every boss keeps its authentic entry gate and becomes a persistent Combat
context assembled from existing contracts — no bespoke per-boss engines:

- **Sessions** ride the shared session substrate: persistent across reviews,
  explicit Leave, no wall-clock timeout, source-authentic death handling.
- **Multi-enemy rooms** (Graardor/K'ril/Zilyana/Kree'arra bodyguards, Nex's
  minion phases, Corporeal Beast's dark core) resolve through
  `multi-enemy-encounter-contract-2026-07-18.md` (engaged target + bounded
  pressure roster).
- **Fight Kiln** extends the Fight Caves session contract verbatim: wave
  roster, live six-tick slices, explicit Leave, resumability, with its own
  harvest-pinned wave table and Har'Aken finale.
- **God Wars Dungeon**: the per-faction kill-count meter accrues through
  ordinary Combat reviews against faction troops; boss-door entry consumes the
  authentic count. Ambient faction aggression is bounded between-review
  pressure and consumes the already-defined mature Zamorak-hawk and
  Saradomin-owl protection flags (Guthix raptor intentionally supplies none),
  closing the parked Summoning substrate in
  `summoning-skill-contract-2026-07-16.md`.
- **Style telegraphs** (TzTok-Jad, Har'Aken, and any phase-signaled attack):
  the result line announces the next incoming style. The game automatically
  sets its matching protection prayer for that attack if the player has
  unlocked the prayer and has prayer points. Otherwise the attack lands
  unprotected. Supplies and damage output, including prayer points, potions,
  healers and kill speed, provide the challenge. No manual switch between
  reviews is required (owner ruling2026-10-14 at23:05 PDT).

## Harvest work

Per boss: entry gates (quests, kill counts, keys, Kiln's Fight Caves
prerequisite), wave/phase tables, stats, telegraph patterns, drop tables,
instance rules, and Summoning/familiar interactions (Corporeal Beast's
familiar consequence included), all pinned per the verification standard.
