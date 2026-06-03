# Achievement Diary Item Grants Design Stub

## Status

Stub only. This is a future design thread, not part of the Mining parity backend pass.

## Seed Idea

AnkiScape may eventually port RuneScape-style achievement diary reward items as long-term account rewards. Instead of requiring literal region diaries, AnkiScape can grant or upgrade diary-style items as the player completes a meaningful percentage of the existing achievement set.

This came up during Mining parity planning because Varrock armour has Mining bonuses, but its real acquisition route depends on Varrock Tasks. AnkiScape already has achievements, but not a diary system, regions, quests, or task lists.

## Candidate Grant Models

### Percentage Threshold Grants

Every fixed completion threshold grants a diary-style item or upgrade.

Examples to decide later:

- Every 10% of total achievements completed.
- Every 20% of total achievements completed.
- Separate thresholds per achievement difficulty tier.
- Separate thresholds per skill category, such as Gathering, Artisan, Combat, Support.

Why this may fit AnkiScape:

- It uses the existing achievement system instead of adding region diaries immediately.
- It gives achievement completion a tangible gameplay payoff.
- It can grant items before the full diary/task system exists.

### Ordered Cycle

Rewards are granted in a fixed cycle, so the player eventually receives a curated spread of diary-style items.

Open design question:

- Should the cycle be deterministic for fairness, or randomized for surprise?

### Random Grant Or Upgrade

At each threshold, choose a random eligible diary item, or upgrade an existing one.

Possible rules:

- Prefer granting a new item before upgrading duplicates.
- Once all tier-1 items are owned, upgrades begin.
- Weight rewards by achievement difficulty or account progression.

Risk:

- Randomness can feel bad if the player wants a specific utility item, such as Varrock armour for Mining.

## Difficulty Tier Mapping

The current achievement system already has difficulty labels:

- Easy
- Moderate
- Difficult
- Very Challenging

Future design should decide whether these map directly to diary reward tiers.

Possible mapping:

- Easy achievement progress unlocks tier-1 diary items.
- Moderate progress upgrades toward tier 2.
- Difficult progress upgrades toward tier 3.
- Very Challenging progress upgrades toward tier 4.

Open issue:

- Existing achievement difficulty labels may not be balanced enough to drive item progression without a pass over the achievement set.

## Item Scope

Initial candidate item families:

- Varrock armour, because it directly affects Mining.
- Other achievement diary equipment with skilling utility.

Do not add combat-only or region-specific diary rewards until the account/equipment model can support them cleanly.

## Equipment Relationship

The equipment backend now exists. Diary reward items should grant inventory items
that can be explicitly worn through `player_data["equipment"]`; Mining bonuses
only apply from worn slots, not passive ownership.

The future diary reward system should become one acquisition path for items like
Varrock armour. It should not reintroduce a separate `owned_equipment` collection.

## Design Questions For Later

- Should grants be based on total achievement completion percentage, per-tier completion, per-skill-category completion, or a hybrid?
- Should rewards be deterministic, random, or player-choice based?
- Should diary-style items upgrade automatically, or require explicit player action?
- Should powerful rewards be gated by difficulty tier rather than raw completion percentage?
- How should existing completed achievements retroactively grant items when the system launches?
- How should new achievements added later avoid unintentionally moving old accounts backward in percentage completion?
- Should this become a true diary/task system later, or stay as an achievement reward layer?

## Non-Goals For The Mining Pass

- Do not implement diary reward grants.
- Do not implement Varrock armour acquisition.
- Do not rebalance all achievement difficulties.
- Do not add diary-specific equipment UI; use the general Equipment tab once the frontend pass lands.
- Do not create region diaries or quest analogues.
