# Slayer Fever-spider Combat audit — 2026-07-19

Status: **source-blocked; no Combat row activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass closes the source-ready identity, access, equipment, ordinary-combat,
and drop facts for the ordinary level-49 Fever spider. It does **not** activate
`fever_spider` in `COMBAT_ENEMY_DATA`. The remaining disease values conflict
across the period record and Darkan's disclosed reconstruction choices, and the
pre-EOC verification standard forbids silently choosing or inventing a timer,
severity, or cure arithmetic.

Chaeldar therefore remains hidden at **25/34** readiness. Fever spiders retain
their existing `combat_target` blocker rather than receiving a truthy
`disease_damage` completeness marker without an executable, source-closed
status effect.

## Period evidence

### Fever spider

RuneScape Wiki `Fever spider`, oldid `6469080`, timestamp
`2012-10-25T02:53:02Z`, literal wikitext establishes:

- level 49, 400 LP, Slayer 42, and 40 Slayer XP;
- non-aggressive six-tick melee attacks;
- an approximate protected maximum hit of 50 LP;
- repeated 110-LP damage without Slayer gloves, prevented by Protect from
  Melee;
- disease without Slayer gloves regardless of prayer or armour;
- three Relicym's-balm doses to cure the Fever-spider infection;
- a quest-only guaranteed Fever spider body during Rum Deal;
- uncommon Grimy kwuarm and rare Spin ticket ordinary drops; and
- an approximately four-second respawn.

Source:
<https://runescape.wiki/w/Fever_spider?oldid=6469080>.

The cutoff talk page, oldid `6101101`, timestamp
`2012-08-17T11:30:51Z`, contains player reports of no kwuarm in 100/120 kills,
5 in 150+, 7 in 166, 14 in 167 with a ring of wealth, and a Spin-ticket report.
These observations corroborate the sparse drop set but do not close exact
rates:
<https://runescape.wiki/w/Talk:Fever_spider?oldid=6101101>.

### Route

RuneScape Wiki `Braindeath Island`, oldid `5905468`, timestamp
`2012-07-08T10:26:40Z`, says the island is accessible by starting Rum Deal and
is the only Fever-spider location:
<https://runescape.wiki/w/Braindeath_Island?oldid=5905468>.

The current AnkiScape quest state already stores `started`, `progress`, and
`completed`, so the eventual Combat permission is a generic
started-or-completed route check. It must not require Rum Deal completion and
must not duplicate the Darkan quest thread's stage content. The precise
assignment-time stage predicate remains `source_blocked`, as recorded in
`slayer-chaeldar-pool-2026-07-17.md`.

### Disease and cure

RuneScape Wiki `Disease (historical)`, oldid `6025367`, timestamp
`2012-08-02T17:20:19Z`, establishes that:

- disease drains one random non-Constitution skill at a time;
- the amount drained equals the visible disease splat;
- the same skill may be selected repeatedly;
- natural skill recovery takes one minute per level;
- Relicym's balm reduces disease, and three doses cure most disease;
- Dealing-with-Scabaras disease requires four doses; and
- death clears disease.

Source:
<https://runescape.wiki/w/Disease_(historical)?oldid=6025367>.

RuneScape Wiki `Relicym's balm`, oldid `6324779`, timestamp
`2012-09-30T16:03:28Z`, supplies Herblore 8, 40 XP, the three-dose recipe, the
four-dose decanted form, and the statement that a recent infection can require
up to three doses:
<https://runescape.wiki/w/Relicym%27s_balm?oldid=6324779>.

These pages do not state the server tick interval, initial Fever-spider
severity, or per-dose numeric reduction.

## Executable and cache evidence

Pinned Darkan paths and commits:

- NPC combat row and hidden stats:
  `data/npcs/combatdefs/uncategorized/fever_spider (noanims).json`,
  commit `14e49a561bab1441384022421d10dc03a8d837f0`;
- ordinary drop row:
  `data/npcs/drops/fever_spider.json`, same pinned history;
- bonuses:
  `developer-information/npcListBonuses.txt:2852`, same pinned history;
- Rum Deal attack:
  `src/main/java/com/rs/game/content/quests/rum_deal/RumDeal.kt:396-405`
  and `RumDealState.kt:100-101`, commit `218c8b81e1`;
- disease runtime:
  `src/main/java/com/rs/game/model/entity/player/Disease.java:25-116`,
  commit `c5d020ce8c444f72cb132789ea2b17199d96a231`; and
- balm drinking:
  `src/main/java/com/rs/game/content/Potions.kt:285-288`.

Darkan supplies Attack 60, Strength 30, Defence 40, Magic/Ranged 1; defence
bonuses `20/15/10/15/15`; zero attack and Strength bonuses; a 59-tick respawn;
and one 20-slot ordinary selector with three Grimy-kwuarm slots and seventeen
empty slots. The level, LP, Slayer facts, combat channel, equipment split, and
drop set agree with the cutoff pages. The exact `3/20` kwuarm selector is
usable implementation evidence; Spin ticket remains excluded until its rare
rate is closed.

The quest-only Fever spider body is intentionally not part of ordinary Combat.
It belongs to the Darkan quest thread's Rum Deal stage.

## Blocking conflicts

1. **Unprotected hit formula.** The cutoff article reports repeated `110` LP
   and lists `110` as the unprotected maximum. Darkan implements
   `maxOf(110, normalMaxHit)`. Later correction history outside the cutoff says
   the real effect scaled with Constitution. No period implementation or
   cutoff talk row currently closes that formula. A flat 110-LP hit would
   overstate certainty.
2. **Disease magnitude and cadence.** Darkan starts Fever-spider disease at
   severity 15, drains every 30 ticks, decrements severity by one, and drains a
   random non-Constitution skill. Its own source comment explicitly labels the
   decay and balm arithmetic as implementation choices. The cutoff pages prove
   the shape, not those numeric values.
3. **Balm arithmetic.** Darkan subtracts four severity per dose, so severity 15
   needs four doses. The cutoff Fever-spider page says exactly three doses.
   Replacing 15 with 12 would reconcile the outputs but would be an invented
   non-roll value, which the source standard forbids.
4. **Respawn.** The cutoff page says about four seconds; Darkan says 59 ticks.
   This is not needed to certify the existing review-burst respawn abstraction,
   but the conflict remains recorded.

## Required unblock

Activate Fever spiders only after one of these occurs:

- a period-lineage implementation or dated server-behavior source closes the
  Fever-spider hit and disease numbers; or
- the owning Combat contract receives an explicit, newer owner-approved
  abstraction for those exact blocked values.

No new design question was created by this pass. The owner closed design on
2026-07-19; this is strictly a sourcing dependency.

## Workflow telemetry

Codex Workflows run `f2c763f0-4b3b-4ee7-abd6-6273dd05c186` was launched for
two bounded Sol-high read-only checks. After more than fifteen minutes, the
first leaf still had no provider session, tokens, tools, or progress after
`2026-07-19T08:01:23Z`; the second remained queued behind the global
four-worker limit. The root canceled the run at `2026-07-19T08:16:07Z` and
independently reproduced every finding above. This is a new no-session
bootstrap failure signature under build `0.1.0+codex.20260718224425`; no task
work was rerun solely to test the runtime.

