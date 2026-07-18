# Road to Restoration — Design-Lesson Audit

Date: 2026-07-17

## Status and evidence boundary

RuneScape's 2026 Road to Restoration is **not** evidence for the
2012-11-20 content snapshot. It is a modern first-party critique of systems
that accumulated bad incentives, mandatory setup, time pressure, progression
walls, or incoherent presentation.

Use it as a design-quality comparator after period content has been sourced:

1. establish what existed at the cutoff;
2. identify whether Jagex later named a structural problem with it;
3. preserve the content and fantasy where useful;
4. remove or flatten the acknowledged bad incentive explicitly; and
5. record the result as an AnkiScape abstraction, never as period parity.

## Primary modern sources

| Source | Date/status | Relevant first-party direction |
|---|---|---|
| [The Roadmap That Changes RuneScape Forever](https://secure.runescape.com/m=news/the-roadmap-that-changes-runescape-forever) | 2026 roadmap | Remove gameplay-impacting MTX; make RuneMetrics free; reduce DailyScape; repair early-game friction, Aura pressure, combat setup, GE opacity, UI clutter, and visual incoherence |
| [Loyalty points — RuneScape Support](https://support.runescape.com/hc/en-gb/articles/206853589-Loyalty-points) | 2026 support notice | Remove the Loyalty Points system at the end of April 2026 |
| [Road to Restoration](https://runescape.wiki/w/Road_to_Restoration) | modern index/secondary summary | Tracks aura removal, DailyScape reduction, early-game rebalance, UI/world cleanup, and other integrity work |

The official roadmap describes Auras as creating time pressure and extra setup
that players feel obligated to consider before beginning an activity. Its stated
goal is to remove limited peak efficiency and return useful effects to the core
game where appropriate. The support notice separately confirms the removal of
Loyalty Points.

“New Beginnings” is a diagnosis of accumulated **modern RS3** progression
inconsistency, not a claim that the 2012 early game was uniformly too slow or
too punitive. Its changes included buffs and reductions: early pickpocketing
was made more predictable and its stun shortened, while Shrimp and Crayfish
catch rates were reduced because an earlier tripling had made those starter
fish optimal for too long. Later-system drop-table, activity-rate, and
acquisition problems were also retuned. AnkiScape must therefore treat this as
an instruction to identify concrete outliers, not as authority for a global
novice buff.

## Durable AnkiScape lessons

### 1. Authentic content does not require authentic coercion

AnkiScape can preserve a period item, activity, or reward while replacing an
external subscription gate, real-time cooldown, daily chore, or mandatory
preparation loop. The abstraction must be visible in source notes.

### 2. Never gate baseline viability behind tenure

An aura may offer an alternate build or modest advantage. Content must not be
balanced on the assumption that the player waited simulated years for the
best aura. Required success rates, boss viability, and core skilling cadence
belong to the underlying skill or encounter.

### 3. No wall-clock or cooldown anxiety

All durations and cooldowns use answered-card time. A player never needs to log
in at a particular hour, wait outside Anki, or stop studying to preserve a
timer.

### 4. Catch-up grants are legitimate repairs

When a period tenure system granted necessary gameplay power too slowly, a
bounded starter cache may preserve access to the catalog without preserving
the lock-in. The authentic earn and spend schedule can continue after that
grant.

### 5. Avoid DailyScape

Recurring rewards should accumulate to a source-bounded cap or wait for the
player. Missing a real-world day must never destroy value. Reset messaging uses
reviews until reset, not calendar pressure.

### 6. Remove “do the same thing, but better” dominance

If one modifier is always correct for an action, prefer folding the necessary
baseline into the action or making the modifier a low-friction Casual default.
Advanced choice is valuable only when alternatives create materially different
tradeoffs.

### 7. Keep modern repairs advisory

The Road to Restoration does not license importing post-cutoff stats, items,
skill caps, combat formulas, or reward routes. Each AnkiScape deviation still
requires an owner decision and an explicit abstraction note.

### 8. Budget the whole setup ritual

Preparation cost compounds across Auras, familiars, prayers, potions, urns,
equipment, inventory, and activity selection. A tolerable control on each page
can still create an intolerable start-of-session checklist.

- Casual mode should remember a last-known-good setup and automate the routine
  parts the player has authorized.
- Advanced mode may expose the individual controls without making them
  mandatory.
- Equipment-owned state remains mode-agnostic. Casual and Advanced do not
  invent separate selectors for equipment slots such as the Aura slot.
- New systems must be reviewed against the total setup burden, not only their
  local screen.

### 9. Do not create wrong-time activation anxiety

Changing a timer from minutes to reviews removes wall-clock pressure but can
still make the player feel that an Aura is being wasted on unrelated cards.
Activation and depletion therefore need an eligible-action boundary: the Aura
begins on the next action it can affect and only spends duration on eligible
actions. Cooldowns may remain in answered-card time so the Aura does not become
permanent baseline inflation.

### 10. Preserve invested value through later repairs

Every abstraction with a persistent currency, unlock, or long grind should
record how owned value survives a future redesign. Restoration work must
convert or refund existing progress instead of silently deleting it. This is a
save-integrity rule, not a promise to preserve every obsolete mechanic.

## Adopt / adapt / reject matrix

| Road initiative or diagnosis | AnkiScape disposition | Concrete rule |
|---|---|---|
| Remove Treasure Hunter and gameplay-impacting MTX | **Adopt** | Do not recreate monetisation-derived coercion merely because Squeal of Fortune existed at the cutoff. Preserve period content only through ordinary gameplay where an owner-approved translation is worthwhile. |
| Make RuneMetrics freely available | **Adopt** | Stats, progress telemetry, search, filters, and contextual help are core UI. Never gate them behind a currency, entitlement, or grind. |
| “New Beginnings” early-game repairs | **Adapt narrowly** | A candidate noob trap must be individually named and sourced, then classified as Anki-medium friction or period texture. Only the former is flattened without a separate owner decision; this is not blanket authority to rewrite period XP, drops, quests, or rates. |
| “Life After Dailies” | **Adopt** | Recurring rewards use world-review resets, accumulate to a source-shaped or explicitly designed cap, and never lose value because the player missed a real day. Show reviews until reset, never wall-clock deadlines. |
| Aura and Loyalty removal | **Adapt** | Keep the cutoff Aura catalog, slot, and spend choices. Remove subscription tenure, wrong-time activation pressure, and mandatory peak-efficiency assumptions. Do not make Auras permanent baseline buffs. |
| Combat modernization and reduced setup | **Adapt principles only** | Keep authentic pre-EOC combat. Casual presets automate an authorized coherent setup; Advanced exposes the parts. Repair genuine noob traps and redundant ritual without importing EOC abilities or modern formulas. |
| Grand Exchange repair | **Adapt when GE is designed** | Expose price freshness, order state, buy-limit logic, and useful failure feedback. Do not import modern prices, limits, or market rules as cutoff evidence. |
| Cleaner UI, stronger defaults, visual-noise control | **Adopt** | Use shared modular search/filter controls, progressive disclosure, coherent period asset sources, readable defaults, and fewer duplicative surfaces. |
| Cosmetic visibility toggles | **Mostly reject** | No avatar-fashion system currently justifies the surface. Add a toggle only when an implemented visual layer creates a concrete legibility problem. |
| Social systems and multiplayer repair | **Park** | Do not build speculative multiplayer infrastructure. Preserve only clean seams where a future social feature would otherwise require destructive rewrites. |
| Plugin/API support | **Adapt internally** | Prefer registry-driven skills, actions, assets, filters, and help surfaces. This is maintainability, not a promise of a public mod API. |
| Modern level-120 expansions and post-cutoff mechanics | **Reject** | They are neither parity evidence nor necessary repairs to an Anki-medium problem. |

## Free player-facing mechanics information

Owner decision, 2026-07-17:

- add one optional, reusable `Details` surface for targets and activities;
- make it equally available in Casual and Advanced modes;
- show effective success chance when genuinely known, expected output or
  damage range, XP, concrete failure consequences, and a readable modifier
  breakdown;
- show current player-facing shop prices and stock, but not future price or
  restock predictions;
- use qualitative language when exact mechanics remain unresolved instead of
  fabricating numerical precision; and
- never expose equations, source provenance, internal ticks, RNG state, or
  developer classifications such as `source_blocked` in ordinary player UI.

The normal row/page remains compact. `Details` is the free mechanics-reference
layer for players who want to understand an outcome, not a mandatory wall of
telemetry.

## Aura application

Pinned cutoff evidence:

- [`Members Loyalty Programme`, oldid `6514342`](https://runescape.wiki/w/Members_Loyalty_Programme?oldid=6514342),
  2012-11-01T00:47:56Z;
- first-month grant: 500 points;
- monthly grants: 3,000, 5,000, 7,000, then increments of 1,000 to 15,000;
- cumulative twelve-month total: **107,500 points**;
- one Aura slot;
- source-specific activation durations, cooldowns, tier prerequisites, effects,
  and prices.

Owner direction so far:

- retain the cutoff aura catalog and dedicated Aura slot;
- Aura selection is an ordinary Equipment operation, not a per-target,
  per-skill, Casual, or Advanced setting;
- whichever Aura is equipped automatically activates when it is available and
  the player next performs an eligible action;
- automatic activation is identical in Casual and Advanced modes;
- changing or removing the Aura uses the ordinary Equipment surface;
- grant **107,500 Loyalty Points** at account start, exactly the cumulative
  cutoff-era twelve-month amount;
- earn later points faster than the real programme;
- use only answered-card progress, never subscription tenure or wall time;
- activate on the next eligible action and deplete only on eligible actions;
  and
- keep source-shaped answered-card cooldowns so Aura choice does not collapse
  into permanent baseline inflation.

The original 500-point first month is already included in the 107,500-point
year cache. Do not add a separate welcome grant.

### Practical portfolio and ongoing cadence

The cutoff gameplay-aura catalog costs approximately **2,059,500 Loyalty
Points** after counting each upgrade chain by its cumulative top-tier price and
excluding cosmetic gaze auras. “Everything important” is narrower than every
possible effect.

The representative practical portfolio costs **1,301,000 points**:

- combat and sustain: Penance, Vampyrism, Berserker, Supreme Runic Accuracy,
  Supreme Sharpshooter, Supreme Reverence, and Supreme Invigorate;
- skilling: Jack of Trades, Wisdom, Supreme Lumberjack, Supreme Quarrymaster,
  Supreme Call of the Sea, Supreme Five-finger Discount, Supreme Tracker,
  Supreme Greenfingers, Greater Surefooted, and Resourceful.

This deliberately excludes cosmetic and mechanically duplicate Prayer-wing
auras, plus situational effects such as Poison Purge, Knock-out, Inspiration,
Equilibrium, Regeneration, Ancestor Spirits, Aegis, and Dark Magic. They remain
valid catalog purchases; they simply do not determine the target acquisition
window.

At the authentic mature rate of 15,000 points per month, a new account would
need approximately **7 years and 8 months** to acquire that practical
portfolio. Even the rejected 2× proposal would require about **3 years and
4 months** after the immediate year-one cache.

Owner-set acquisition target:

- grant **100,000 Loyalty Points per 7,200 answered cards**;
- preserve the authentic monthly lump shape and show reviews until the next
  payout;
- after twelve simulated months, the initial 107,500 points plus 1,200,000
  earned points cover the practical portfolio with 6,500 points remaining;
- this is approximately 6.7× the authentic mature monthly rate; and
- grants accumulate without expiry.

Cadence reconciliation, 2026-07-17: the `7,200` count remains exact because it
is twelve 30-day months on the independent 240-answer world calendar. It is not
derived from the foreground `R = 1000` balancing hour. Aura active duration is
an eligible-action budget and therefore depletes only when the equipped Aura can
affect the admitted action; cooldown remains an answered-card world consumer.

Aura ownership and point balance never gate Completionist. Encounter and skill
balance must not assume a high-tier aura.

## Recurring-activity carryover

Owner decision, 2026-07-17:

- replace the shared no-stacking rule for recurring **activity eligibility**;
- each recurring activity holds one current entry plus one reserve, for a
  default maximum of **two available entries**;
- only eligibility accumulates: XP, items, currency, and activity stages never
  resolve automatically;
- the player must still play each banked entry;
- show only the number of entries currently available, never an overflow,
  missed-entry, or value-lost warning;
- banked entries never become progression or Completionist requirements; and
- source-specific exceptions may use another cap only when the activity's
  structure makes the two-entry default materially unsuitable.

This is deliberately a small forgiveness buffer, not a seven-day or four-week
backlog. The answered-card world clock already means no opportunity is missed
while the player is absent from AnkiScape; the reserve only prevents ordinary
study from forcing an immediate recurring-activity detour.

This decision does **not** apply to shop stock, crop growth, resource
regeneration, item charges, or passive producers. Those remain governed by
their owning systems rather than being converted into generic activity entries.

Implementation status: design-set but not yet reconciled with the existing
shared calendar runtime, which currently resets daily and weekly eligibility
without stacking.

## Follow-up application queue

Apply the matrix to the corresponding AnkiScape contracts when those systems
are next grilled or implemented:

- Aura and Loyalty catalog, pricing, effects, and eligible-action windows;
- DailyScape and recurring-reward accumulation caps;
- named early-game friction candidates;
- cross-system Casual/Advanced setup burden;
- Grand Exchange transparency and buy-limit lessons;
- shared UI search, contextual help, and asset coherence; and
- monetisation-derived progression or convenience gates.

Each application must still state its cutoff source, its Anki abstraction, and
whether the Road lesson is adopted, adapted, rejected, or parked.
