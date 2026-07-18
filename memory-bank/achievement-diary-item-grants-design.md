# Achievement, Diary, Cape, and Taskmaster Design

## Status

Owner grill closed on 2026-07-17. This replaces the former percentage-grant
stub. It is a design contract and source-audit queue, not an implementation
claim.

The prerequisite sticky-completion and owner-scoped-counter work remains
governed by `memory-bank/achievement-semantics-contract-2026-07-16.md`.

## Cutoff Evidence

The target is the live game immediately before EOC on 2012-11-20.

| Surface | Pinned evidence | What it establishes |
|---|---|---|
| Achievements | `Achievements`, oldid `6579331`, 2012-11-18 | 534 total tasks; eight diary-equipment families plus Burthorpe/Taverley; regional and miscellaneous tasks; one pinned task; 350-task music unlock; all-task Taskmaster emote |
| Capes of Distinction | `Update:Capes of Distinction`, oldid `5548903`, 2012-05-01 | Milestone capes 10-90, Max, Completionist, five-year Veteran, and their acquisition model |
| Capes of Accomplishment | `Capes of Accomplishment`, oldid `6514341`, 2012-11-01 | Skillcapes, Quest point cape, automatic irreversible trim, Dungeoneering 120 cape, shared period bonuses |
| Quest point cape | `Quest Cape`, oldid `6552492`, 2012-11-13 | All-quest gate, 99,000-coin purchase, and automatic loss of wear eligibility when the quest maximum rises |
| Max cape | `Max cape`, oldid `6549092`, 2012-11-12 | All 25 skills at 99, Dungeoneering 120 not required, and 2,475,000-coin purchase |
| Completionist capes | `Completionist cape`, oldid `6560039`, 2012-11-15 | Normal and trimmed forms, five-million-coin purchase, Dungeoneering 120, and the cutoff-era completion families |
| Taskmaster | `Task Master (emote)`, oldid `6547939`, 2012-11-11 | All 534 tasks granted Taskmaster rather than an achievement cape |
| Keepsake key | `Keepsake key`, oldid `6588542`, 2012-11-19 | The 2012 RuneCoin cosmetic override could preserve the first untrimmed cape's appearance |
| Veteran capes | `Veteran cape (5 year)`, oldid `6474681`; `Veteran cape (10 year)`, oldid `6404608` | Five- and ten-year capes and their 50,000/100,000-coin prices |

Desert Tasks and the Desert amulet released on 2013-01-21 and are outside the
cutoff. The OSRS achievement diary cape and unified Collection Log are also
post-cutoff. The broad RS3 Skills, Combat, Quest, and Completionist achievement
categories arrived with the 2017 achievement-system expansion.

## Canonical Achievement Structure

### Eight equipment families

Seven families use Easy, Medium, Hard, and Elite:

- Ardougne cloak;
- Falador shield;
- Fremennik sea boots;
- Karamja gloves;
- Morytania legs;
- Seers' headband; and
- Varrock armour.

Lumbridge/Draynor uses Beginner, Easy, Medium, and Hard for the Explorer's ring.

Each of these 32 tiers contains exactly 12 curated tasks, for 384 regional diary
tasks. Every tier has its own expected effort budget:

- first tier: 1x baseline;
- second tier: 2x;
- third tier: 3x; and
- fourth tier: 4x.

The multiplier applies to the twelve tasks in that tier, not cumulatively to
the entire family.

### Burthorpe/Taverley

Burthorpe/Taverley remains a separate Beginner-only onboarding set with its
source-shaped starter-equipment rewards. It is not expanded into a fabricated
four-tier item family.

### Miscellaneous

The fixed cutoff-era non-area task pool remains as Miscellaneous. These tasks
do not advance regional equipment. They retain their source-shaped small coin
rewards and count toward Taskmaster.

The final Burthorpe/Taverley and Miscellaneous row counts must come from the
pinned cutoff task catalog; they are not forced into twelve-row tiers.

## Task Curation Rules

- Start from the authentic pre-cutoff regional task list.
- Preserve the distinctive feat, production chain, cross-skill dependency,
  quest gate, activity, equipment interaction, and period pun-heavy name when
  the translation remains recognisable.
- Remove geography, emotes, and inventory choreography when those details do
  not change the accomplishment. A concise narrative line may retain the
  original setting.
- Prefer 9-11 distinctive translated feats per tier. Only 1-3 generic
  progression anchors may pad a tier.
- No task condition or durable task ID is shared between families. The content
  budget is large enough to give every family a distinct palette.
- Preserve regional personality. Diversity is a review criterion, not a rigid
  quota of combat, gathering, artisan, quest, and activity tasks.
- Every task and all four tiers are visible from the beginning.
- Higher-tier tasks may complete and retain progress before earlier equipment
  tiers are claimed.
- Numeric or staged progress appears only where the condition has meaningful
  progress. Binary feats remain binary.
- Levels, quests, inventory ownership, activity totals, and exact persistent
  counters receive retroactive credit. Contextual feats receive retroactive
  credit only when existing telemetry proves every condition; never infer a
  feat from XP, wealth, or likely prior behaviour.

## Rewards and Claiming

- Regional tasks grant progress and a completion popup, not XP, coins, or
  individual items.
- Completing all 12 tasks changes the tier to `Ready to Claim`.
- The authentic taskmaster portrait/dialogue performs a one-click claim with no
  travel review.
- Claiming is sequential: a later equipment tier cannot be claimed before its
  predecessor even when all later tasks are complete.
- One atomic claim grants or upgrades the equipment item, presents its newly
  active effects, and creates the sourced lamp or Bank Claim with its authentic
  skill-choice and minimum-level restrictions.
- Repeatable services, daily allowances, and item effects belong to the tier
  package. Reset cadence uses the global answered-card clock.
- A tier upgrade replaces the preceding item wherever it resides without
  duplication.
- Miscellaneous tasks are the narrow exception to the no-per-task-reward rule:
  they retain their sourced coin payouts.
- Burthorpe/Taverley retains its own source-shaped set reward.

## Taskmaster

Taskmaster requires every regional, Burthorpe/Taverley, and Miscellaneous task.
AnkiScape has no emote system, so the period emote is translated into:

- a durable `Taskmaster` completion state;
- a gold Taskmaster seal in the Achievement Cabinet;
- a one-time completion presentation; and
- satisfaction of the Taskmaster requirement for Completionist.

It grants no invented achievement cape, stats, or mechanical perk.

The 2012 interface's one-task pin survives only inside the Achievements tab: the
pinned task stays at the top of the list. It does not add review-HUD clutter.

## Achievement UI

- The Achievement Cabinet is the canonical progression surface.
- It has regional-family, Burthorpe/Taverley, Miscellaneous, Capes and
  Distinctions, Taskmaster, and Completionist views.
- Use the shared modular search/filter component. Filters include family, tier,
  completion state, and requirement family.
- All task details, requirements, progress, and sourced reward previews remain
  visible.
- Equipment management remains canonical in Bank/Equipment. The Cabinet may
  claim and showcase a cape or diary item but does not maintain duplicate
  ownership state.
- There is no extensible free-floating Global Achievements list. Accomplishments
  live in regional diaries, the bounded Miscellaneous set, Capes and
  Distinctions, a specific activity/quest/boss/collection surface, or the
  Completionist lists.

## Migration

- Remove the fabricated achievement rows rather than exposing a permanent
  Legacy section.
- Preserve underlying counters and unknown save fields.
- Credit a new task only where an old completion or persistent counter proves
  the exact same condition.
- Unmatched old achievements disappear from the UI and grant no diary progress.

## Capes and Distinctions

### Skill and Quest capes

- Every level-99 skill has its cutoff-era cape, matching hood, master NPC, coin
  price, and equipment bonuses.
- Dungeoneering has both its level-99 cape and the cutoff-era level-120 master
  cape.
- A second level 99 automatically and irreversibly trims every skillcape. The
  Cabinet permanently records the first-99 identity and displays its untrimmed
  artwork.
- Do not implement Solomon's Store or RuneCoins. The display-only first-99
  keepsake preserves the meaningful cosmetic fact without importing MTX.
- While its skillcape is equipped, the corresponding skill operates at
  effective level 100 for success-rate and yield formulas. It does not unlock a
  level-gated action. This replaces repeated manual `Operate` activation.
- Casual training may auto-equip an owned, available, beneficial skillcape
  through the established equipment-automation rule. Advanced mode follows the
  player's explicit equipment.
- The Quest point cape requires every cutoff quest and costs 99,000 coins.
  Latent quest rows activate its eligibility check when their implementation
  ships.

### Milestone capes

The nine milestone capes remain Crafting actions at a loom. Cape `N` requires:

- level `N` in every skill to wear;
- Crafting level `N`;
- `N / 10` balls of wool;
- `N` Crafting XP; and
- no combat or skill perk beyond its sourced equipment bonuses.

The existing Crafting rows need their missing all-skills wear gate repaired.

### Max and Completionist

- Max requires 99 in all 25 cutoff skills, not 120 Dungeoneering, and costs
  2,475,000 coins.
- Completionist requires the frozen 2012-11-20 requirement families, translated
  only where AnkiScape flattens a mechanic, and costs 5,000,000 coins.
- Trimmed Completionist retains the exact period long-tail accomplishments and
  their enormous scale. Preserve the authentic 5,000-game Castle Wars
  requirement. The earlier `16,667`-review conversion incorrectly reused the
  six-minute world-calendar mapping for a foreground activity; its exact review
  cost remains cadence-blocked until Castle Wars declares its own activity-beat
  unit. Do not compress it to a token requirement.
- Missing authentic requirement families are latent during development and
  activate automatically when their feature ships.
- Later conveniences and post-cutoff-inspired trackers do not become cape
  requirements merely because AnkiScape adds them.
- Losing eligibility leaves the owned cape in Bank but makes it unusable and
  unequips it through the normal safe equipment path.
- Period stats and inherited item effects must be audited and implemented
  directly. Do not import the 2017 skillcape-perk system.

### Veteran and Classic

- Five-year Veteran unlocks after 438,000 answered cards and costs 50,000 coins.
- Ten-year Veteran unlocks after 876,000 answered cards and costs 100,000 coins.
- These use simulated world time only; never the wall clock.
- The live cadence kernel does not alter these counts: they derive from the
  independent 240-answer world day, not `R = 1000` foreground balancing.
- Classic cape is deliberately excluded because AnkiScape has no honest
  RuneScape Classic account-provenance predicate.
- Veteran and Classic distinctions never gate Completionist.

All purchasable capes use instantaneous authentic NPC dialogue in the Cabinet.
Eligibility and purchase consume no travel review. Milestone capes remain
player-crafted.

## Music Log

The cutoff Completionist cape required every music track, and the achievement
system unlocked `The Task at Hand` at 350 completed tasks. AnkiScape therefore
needs a passive Music Log under Collections:

- related quests, activities, enemies, and achievement milestones unlock tracks
  automatically;
- the log records track names, hints, source provenance, and completion state
  but does not need audio playback;
- 350 completed achievements unlocks `The Task at Hand`;
- collecting every cutoff-era track satisfies the Completionist music
  requirement; and
- tracks owned by unfinished features remain latent and activate with those
  features.

## Implementation Handoff

### Backend

- Pin and transcribe the cutoff regional, Burthorpe/Taverley, Miscellaneous,
  cape, Completionist, and music catalogs.
- Add stable IDs, predicates, counters, atomic tier upgrades, cape eligibility,
  simulated-age thresholds, and evidence-based migration.
- Keep review-triggered mutation undoable.

### Frontend

- Replace the fabricated achievement list with the Cabinet and shared
  search/filter component.
- Add taskmaster claim dialogue, pinned-row ordering, progress details, cape
  eligibility/purchase, Completionist requirement inspection, and Music Log.
- Keep Bank and Equipment canonical for item ownership and wearing.

### Assets

- Fetch every regional equipment tier, taskmaster portrait, cape, hood,
  Taskmaster seal, and music icon from period assets or the pinned cache.
- Record provenance and add manifest-path coverage.

### Verification

- Pure tests: catalog integrity, tier counts, predicates, retroactive evidence,
  sequential claims, item replacement, cape trim, veteran thresholds, and
  Music Log completion.
- Integration tests: review dispatch, sticky completion, item/effect grants,
  undo, save migration, and latent-requirement activation.
- Offscreen Qt tests: search/filtering, visible tiers, disabled claim paths,
  pinned-row ordering, cape purchases, dark-mode text, and Music Log.

## Remaining Source Work

Design is closed, but implementation is blocked on audited data for:

- the exact cutoff Burthorpe/Taverley and Miscellaneous rows and coin formula;
- the translated 384-task regional roster;
- the complete 2012 Completionist and trimmed-Completionist requirements;
- cape/hood item IDs, bonuses, and inherited effects;
- the cutoff music-track catalog and unlock triggers; and
- every diary item effect, lamp, allowance, and taskmaster asset.
