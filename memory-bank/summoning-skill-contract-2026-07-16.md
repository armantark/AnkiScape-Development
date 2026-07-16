# Summoning skill contract — owner grill (2026-07-16)

Status: **owner grill active; implementation deliberately not started.** This contract
is the durable decision ledger for the complete pre-EOC Summoning surface frozen at
2012-11-20. Historical facts and AnkiScape abstractions must stay visibly distinct.

## Product boundary

Summoning is the next missing skill to design because it is a bounded skill/economy
system that can reuse Combat, target-carried inventory, equipment, death, banking,
consumables, quests, undo, and the existing card-action clock. It must close before
Dungeoneering because Daemonheim is a later temporary-economy variant of several
ordinary skills, including Summoning. Slayer may consume Summoning outputs and award
charms, but neither skill may silently own the other's core loop.

There is no wall-clock gameplay. Any period mechanic expressed in seconds or minutes
must be translated into answered-card or explicit-action state. Source ratios and
ordering are preserved where they carry gameplay meaning; the conversion magnitude is
a labeled AnkiScape abstraction.

## Atomic completion rule

Implementation is complete only when all of these families are designed, sourced, and
shipped together or explicitly parked behind a named external dependency without being
made falsely player-visible:

1. **Acquisition:** the four ordinary charm families, tertiary ingredients, empty
   pouches, spirit shards, Talon Beast charms, abyssal/quest/activity inputs, drop and
   shop ownership, Bogrog shard returns, and saved-item compatibility.
2. **Training:** pouch infusion at obelisks, level/ingredient/shard/XP rows, pouch-to-
   scroll conversion, scroll quantities, Familiarisation rewards, boosts, and any
   period alternate training routes.
3. **Resource state:** maximum and current Summoning points, summon cost, continuing
   drain, obelisk/small-obelisk restore, potions/restores, death, and undo.
4. **Familiar lifecycle:** summon, one-active-familiar rule, duration, renewal,
   dismissal, expiry, death, forbidden contexts, persistence, switching targets, and
   what happens to carried familiar inventory.
5. **Abilities:** combat familiars, healers, beasts of burden, foragers, skill boosts,
   resource gatherers, teleports, light enhancers, remote viewing, passive effects,
   right-click abilities, scroll specials, special-move points, and familiar combat XP.
6. **Inventory and banking:** target-carried versus bank activation, BoB capacity and
   restrictions, deposit/withdrawal, bank-run interaction, death recovery, full-pack
   behavior, and item conservation.
7. **Cross-system hooks:** Combat presets and encounters, skilling targets, Agility
   travel hooks, Slayer drops/tasks, quests and pending XP, equipment, achievements,
   shops, activities, and future Dungeoneering isolation.
8. **UI and assets:** a Summoning skill page, training target families, pouch/scroll/
   familiar artwork, active-familiar and point readouts, summon/dismiss/renew/special/
   inventory controls, meaningful locks, search where the catalog needs it, and no
   decorative control that lacks runtime behavior.
9. **Persistence and proof:** storage migration, sanitization, deterministic RNG,
   review undo plus command undo where appropriate, pure/unit/integration/end-to-end
   tests, real offscreen Qt coverage, item reachability, and manual QA.

Completeness means the full period catalog, not a curated subset called a first version.
Rows whose hidden values remain unprovable may use the smallest clearly labeled
abstraction after a final source search; the feature itself is not deleted for lack of a
server-side number.

## Inherited AnkiScape rules

- One answered card or explicit UI action is the only permitted unit of progression.
- Target-carried presence activates gameplay items unless this grill records a narrower
  familiar-specific rule. Bank ownership alone is inert.
- Review undo and direct UI command undo remain separate, bounded histories.
- A familiar cannot create a second live copy of an item through expiry, dismissal,
  death, switching, banking, or undo.
- Existing Combat LP/death, inventory, equipment, quest, and consumable substrates are
  extended rather than duplicated.
- Ordinary Summoning state cannot leak into Daemonheim. Dungeoneering familiars and
  items belong to the future closed-session economy.

## Period baseline established before the first question

The closest pre-cutoff wiki revisions establish that:

- A pouch summoned one familiar and was consumed; only one familiar could be active.
- Each familiar had its own duration in minutes and its own initial point cost.
- Summoning points continued to drain over the familiar's life, but reaching zero did
  not dismiss it; zero disabled right-click abilities until points were restored.
- Scroll specials were separate from those right-click abilities and did not consume
  ordinary Summoning points.
- Obelisks, small obelisks, Summoning potions, and super restores restored points.
- Familiars covered materially different roles: combat, boosts, beasts of burden,
  healing, foraging, teleporting, and other bespoke abilities.

Evidence and confidence are recorded in
`source-audits/summoning-familiar-lifecycle-2026-07-16.md`.

## Open decision ledger

### 1. Familiar lifetime clock — open

The period mechanic was global logged-in time, which cannot ship directly. The genuine
product fork is which review-native event spends a familiar's sourced duration:

- every answered card while a familiar is active;
- only successful AnkiScape gameplay actions while it is active; or
- no gradual duration, with expiry only at a session/target boundary.

Codex/Fable recommendation: **every answered card**, using one global
minutes-to-review-ticks conversion that preserves all period duration ratios. This is
the closest non-wall-clock analogue to global uptime, makes long-duration familiars and
renewal meaningful across target switches, and prevents optimal play from freezing a
familiar by selecting an ineligible action. The exact conversion magnitude remains a
labeled abstraction to be calibrated after the owner selects the clock.

## Source/open-work queue

- Harvest the complete pouch, familiar, duration, point, scroll, special-move-point,
  capacity, boost, combat, foraging, healing, teleport, and creation-XP tables.
- Reconcile pinned wiki revisions with the closest stable Darkan/2011Scape behavior for
  hidden rolls and state transitions.
- Inventory every period Summoning quest/activity/area gate and acquisition route.
- Audit existing charm, potion, quest, item, combat, inventory, death, and Agility hooks
  before asking the owner any question the repository already answers.
- Continue the owner grill one genuine design fork at a time. Each answer closes this
  ledger before the next question is asked.

