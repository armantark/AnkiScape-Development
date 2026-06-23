# Combat Design Grill - 2026-06-23

Status: complete design grill log. The first Combat V1 ordinary-training
implementation landed on 2026-06-23; see
`memory-bank/source-audits/combat-v1-implementation-2026-06-23.md` for the
implemented source-backed scope and remaining Combat follow-ups.

This note records only major Combat V1 design decisions made with the owner so
they do not get lost between planning and implementation. It is intentionally a
design artifact, not implementation proof: Combat V1 still requires source
audits, code, assets, tests, and runtime verification before it exists in-game.

## Decisions

1. Combat should be handled as one goal with internal checkpoints, not as a
   chain of tiny proof slices. Checkpoints may exist for recovery, tests, and
   commits, but they are not the acceptance boundary.
2. Combat V1 is a general AnkiScape combat system, not a quest-only resolver.
   Quest bosses/enemies should use the same combat engine as ordinary combat
   targets once implemented.
3. The grill should focus on major design decisions. Details that can be
   discovered from the repo or source data should be investigated directly
   instead of asked as owner questions.
4. Combat must not feel too slow in Anki review cadence. Accuracy to
   2011/2012 RuneScape is the source target, but pacing may need an
   Anki-native compression layer so a single fight does not demand too many
   separate card reviews.
5. Melvor Idle is useful as a pacing/interface reference, especially its
   interval-like combat feel and readable combat stats, but AnkiScape should
   not copy Melvor mechanics as the source of truth. RuneScape pre-EOC combat
   formulas and data remain canonical.
6. One successful review should advance a bounded burst of RuneScape-shaped
   combat time, scaled against the real 0.6-second game tick cadence, instead
   of representing only one individual attack.
7. The bounded burst default should be 50 ticks / 30 seconds, not the earlier
   100 ticks / 60 seconds candidate. Sixty seconds can allow roughly 16-25
   player attacks before the owner has another chance to react, which is too
   compressed when the player is low on hitpoints.
8. The same burst cap should apply across ordinary monsters, quest enemies, and
   bosses; combat should not fork into a separate quest/boss pacing system.
   Each successful review still has at most one kill.
9. Combat V1 should include player-facing survival automation discussions:
   prayer, configurable auto-eating under a user-defined hitpoint percentage,
   and death handling are major design decisions, not implementation details.
10. Combat should not add a separate user-defined burst setting for now because
    that creates confusing interaction with the existing `Actions per review`
    pacing control. Combat burst length derives linearly from that existing
    global pacing setting: 1x is 50 ticks / 30 seconds, 2x is 100 ticks / 60
    seconds, and so on. This deliberately makes the multiplier a real
    combat-time multiplier, so higher settings increase both progress speed and
    unattended survival risk.
11. Auto-eat is always available as a Combat setting, not gated behind an
    unlock. It exists because AnkiScape simulates a burst of combat time without
    manual click reactions. It should consume real food from inventory, use the
    player's configured hitpoint threshold, and respect source-backed healing
    values.
12. Future grill questions should stay at major architecture/design boundaries,
    not obvious implementation details.
13. Full Prayer is deferred because it implies implementing Prayer skilling and
    restore/acquisition loops. Combat V1 should still include a Prayer skeleton
    in the model so the engine has an explicit extension point for active
    prayers, drain, protection effects, and prayer bonus later. Until Prayer is
    implemented, prayer-dependent survivability should fail closed or stay
    inactive rather than being silently approximated.
14. Death should be 2012scape-shaped: keep/dropped item logic should be based on
    the pre-EOC gravestone model, but adapted to AnkiScape by risking equipped
    items only. Normal inventory, especially food, should not be dropped.
15. A non-Again review requirement is the likely AnkiScape analogue for running
    back to a gravestone. It should recover grave-held equipment through review
    progress, not punish Anki failures with card changes, XP loss, or ordinary
    inventory loss.
16. Grave recovery should require 5 non-Again reviews. If the grave expires,
    items move to Death's Office instead of being permanently deleted. Death's
    Office should charge Coins to reclaim gear and can reuse the existing Bank
    Claims-style UI pattern.
17. Combat V1 should import a broad source-backed monster/enemy registry, not
    only quest combat encounters. All sourced enemies with usable stats should
    be selectable from a Combat tab, and quest enemies should consume the same
    combat engine/monster data instead of a separate quest-only resolver.
18. Combat XP should depend on the player's equipped weapon and selected attack
    style, using RuneScape-shaped XP routing rather than a generic Combat XP
    bucket.
19. Attack style selection is global, as in RuneScape. The Combat tab selects
    the current enemy target separately from the current attack style; all
    combat reviews use the selected style until the player changes it.
20. Combat skill implementation should use one generic combat-engine pattern
    with different XP/equipment/style funnels, not separate bespoke systems for
    melee, Ranged, and Magic. Combat V1 should implement Attack, Strength,
    Defence, Constitution, Ranged, and combat Magic routing. Noncombat Magic
    actions are deferred. Prayer skilling and Prayer actions are deferred, with
    only the combat skeleton kept.
21. Magic should exist as a normal skill entry once combat Magic lands. Magic
    belongs under the Combat category even for later noncombat spell actions
    such as teleports/enchanting/alchemy; do not move those future actions to
    Artisan even though they resemble processing skills.
22. The broad enemy audit should include source-backed enemies even when they
    are not combat-ready, but the enabled runtime registry must fail closed.
    Enemies missing source-critical combat stats, drops/no-drop behavior, access
    data, or special-script handling belong in audit/backlog output with compact
    reasons, not in an attackable gameplay list and not as silent approximations.
23. Scripted/special encounters should not be blanket-blocked. Mechanics that
    materially affect combat outcome or resources should be modeled when source
    evidence exists: dragonfire, special attacks, immunities, required items,
    nonstandard damage scaling such as Tanglefoot's Magic secateurs/Farming
    scaling, and phases. Mechanics requiring tile manipulation, movement timing,
    safespots, or real-time positioning should be flattened into deterministic
    or contextual requirements instead of making the encounter impossible.
24. Focused special-case combat handlers are acceptable from the start when the
    source mechanic matters and a generic stat fight would be wrong.
25. Flattened movement/timing mechanics should become one-time action/stage
    requirements only when the source mechanic is an actual prerequisite or
    meaningful puzzle step. Otherwise, they are contextual assumptions inside
    the combat handler, often reflected through damage/risk, not repeated review
    micromanagement.
26. Combat V1 should include monster drops for every source-backed drop table
    that can be imported cleanly. Combat should not be XP-only. Monsters with
    usable combat stats but no trustworthy drop table may still be attackable
    for XP, but the UI/data should not invent loot.
27. Preserve full source rarity where source-backed. Rare Drop Table, gem, herb,
    seed, and other global/shared drop tables should be first-class table
    references when present in 2011Scape/Darkan source, not flattened guesses or
    simplified loot buckets. Partial or incomplete tables should be marked
    partial rather than filled in by assumption.
28. Enemy access should be locked where the source game has real access locks,
    including quest state, skill/Slayer requirements, required items, route
    unlocks, and location access. Combat V1 should not model point-to-point
    travel, but location locks still matter as eligibility gates; once access is
    unlocked, the player can select the enemy directly from the Combat tab.
29. Combat is an exclusive selected activity, not parallel background progress.
    When combat is active, successful reviews advance combat bursts. Switching to
    another AnkiScape action stops combat progression and prevents hidden
    death/food drain while the player is focused elsewhere.
30. Combat bursts should simulate individual 0.6s-tick attack events with RNG,
    attack speed, accuracy, max hits, enemy attacks, auto-eat, death checks, and
    drop rolls rather than using expected-value damage. This must stay cheap by
    bounding the burst length from `Actions per review`, only processing active
    participants/mechanics, and reserving averages for UI previews if needed.
31. One review result equals one atomic combat transaction. A successful review
    burst snapshots and commits HP, enemy HP, consumed food/ammo/runes, equipment
    risk, drops, XP, quest stage progress, death, and grave state together. If
    Anki review undo rolls the answer back, the entire burst rolls back rather
    than leaving partial combat side effects.
32. Player lifepoints persist globally between combat bursts. Switching out of
    combat to a safe noncombat skill should heal 100 lifepoints per successful
    review, capped at the player's Constitution-derived maximum. This gives a
    bank/safe-activity analogue without wall-clock healing or automatic full
    restoration.
33. Combat UI should expose compact risk/readiness before reviews advance a
    fight. Enemy rows should show access state, combat style, threat, sourced max
    hit when available, current lifepoints, auto-eat readiness, and a risk band
    such as Safe, Food advised, Death possible, or Blocked. Normal fights should
    not add confirmation friction, but targets that can realistically kill the
    player or risk equipped items should require an explicit confirmation.
34. Combat should expand and reuse the existing worn-equipment system rather than
    creating a separate loadout abstraction. Source-backed monster drops that are
    equippable in the target era should enter the item/equipment registry with
    slot, requirements, combat stats, attack speed where relevant, icon
    provenance, and normal equip/unequip behavior.
35. Combat XP should be awarded per damage dealt inside the atomic review burst,
    not only when an enemy dies. Route Attack, Strength, Defence, Ranged, Magic,
    and Constitution XP from the selected attack style and actual damage dealt;
    drops remain kill-based. Anki review undo rolls back both damage-based XP
    and any kill loot from that burst.
36. Normal monster drops should go directly to the Bank because AnkiScape does
    not model a 28-slot backpack or ground-item looting loop. Exceptions must be
    explicit: quest drops can advance a stage or enter Bank Claims when they
    require a choice, grave/death gear uses the grave or Death's Office flow, and
    stackable currencies such as Coins still land directly in Bank.
37. Ranged ammo, thrown weapons, and Magic runes are consumed by combat from the
    start. This is treated as baseline RuneScape mechanics rather than an open
    design branch: ranged/magic combat should block when required ammunition or
    runes are unavailable, and source-backed saving/recovery effects can be added
    later.
38. Leaving ordinary PvM for safe noncombat activity pauses the active encounter
    rather than resetting enemy HP. Explicit retreat, target change, death,
    Wilderness retreat, quest/route-state invalidation, or encounter-specific
    reset behavior resets according to decisions 70-72. Safe noncombat healing
    is allowed between bursts, but it does not grant drops, kill progress, or
    free attrition against targets unless the active encounter remains valid.
39. Combat V1 should include Slayer monsters in the enemy registry and enforce
    source-backed Slayer level, task-only, and required-item gates where known,
    but it should not implement Slayer task assignment, masters, points, streaks,
    rewards, or bracelets yet. Those belong to a later Slayer system.
40. Treat sourced quantity encounters and form/phase encounters as different
    shapes. Quantity rows are count queues for repeated enemies, such as
    TokTz-Ket-Dill's two Lava monsters and two Fire monsters, Desert Treasure's
    five Ice Trolls, Spirits of the Elid's three Golems, Defender of Varrock's
    six armoured zombies, Blood Runs Deep's two Dagannoth Sentinels, Elemental
    Workshop III's three Earth Elementals, and Stolen Hearts' three Mercenaries.
    Form/phase chains are source-distinct sub-encounters, such as Witch's House
    experiment forms, Shilo Village's Nazastarool zombie/skeleton/ghost forms,
    and other source-backed transformed or scripted boss forms. Quantity rows
    still obey the global kill cap; form/phase chains stop at mechanically
    meaningful boundaries.
41. Boss phase/form boundaries are source-meaningful stop points. Damage can
    continue into another phase only when source mechanics indicate an immediate
    continuous fight with no dialogue, item use, arena transition, or changed
    rule boundary. Otherwise the burst stops at the phase boundary and the next
    review advances the next sub-encounter.
42. Multi-combat and add mechanics should flatten positioning/pathing but preserve
    extra incoming pressure. Source-backed multi-combat areas or fights with adds
    can model multiple active attackers during a burst, with the active-attacker
    count sourced when possible or conservatively capped. Player attacks focus
    one target unless a later source-backed multi-target spell/mechanic exists.
    Allies/companions become contextual damage or risk modifiers only when source
    evidence says they help.
43. Player weapon special attacks can be included without manual review-time
    prompts by running automatically on source-shaped timed/energy gates. A worn
    weapon with a supported special can use it during combat bursts when enough
    special attack energy is available and the automatic-special setting allows
    it. Weapon-specific special costs/effects still need source-backed metadata;
    unsupported specials should fall back to ordinary attacks rather than fake
    effects.
44. Combat should include a generic temporary-buff/status engine from the start,
    even before Herblore acquisition/training exists. Stat boosts, antifire,
    antipoison, and other potion-like effects should be source-shaped,
    auto-consumed when enabled, and driven by combat settings/loadouts rather
    than review-time prompts. Food should likewise be user-selected: the player
    can add preferred foods to an auto-eat queue, and combat consumes from that
    queue according to the configured lifepoint threshold.
45. Combat supplies should use a finite loadout/belt model rather than direct
    whole-Bank access. The player configures preferred food and potion supplies
    once through Bank/Combat UI actions, and combat auto-consumes from that
    loadout during bursts. Refilling from the Bank should be automatic or
    low-friction between fights when stocked, so the player is not forced into
    manual inventory management for every flattened bank run.
46. Combat supply loadouts refill from Bank only at safe boundaries: selecting a
    target, after a kill, after leaving combat, or after grave/death-office
    recovery. They should not refill between review bursts inside the same
    active fight, so multi-review bosses cannot draw effectively infinite food or
    potions from the Bank.
47. Combat must be review-safe: no mid-review dialogs or manual prompts. Player
    choices should be configured ahead of time as rules or queues, including
    attack style, target, auto-eat threshold, food priority, potion toggles,
    automatic specials, and any future retreat rule. Source-required one-off
    actions belong before the fight as stage/action blockers or after a burst as
    phase boundaries, not inside the answer flow.
48. Combat may include an optional auto-retreat/fail-safe rule, but it should only
    trigger at review-burst boundaries. If the configured threshold is met after
    a burst, combat stops before the next review and the enemy resets according
    to the retreat rules. Death can still occur inside a burst when auto-eat and
    supplies fail, preserving risk while giving players a stress-control option.
49. Combat inherits the same review-success semantics as every other AnkiScape
    skill. `Again` gives no progress, while successful review answers advance
    the configured combat burst through the existing pacing model. Combat should
    not add answer-button-specific scaling.
50. Combat feedback should be compact by default. After a burst, show damage
    dealt/taken, supplies consumed, XP gained by skill, kills/drops, current
    lifepoints, and any stop reason such as out of food, target defeated,
    retreated, phase changed, or death. A detailed tick/roll log can exist for
    debugging or source-parity inspection, but normal review flow should not
    spam every attack roll.
51. Combat data should separate audit-visible enemies from enabled gameplay
    enemies and attackable player-state-ready enemies. Audit-visible rows may
    document missing source data with precise reasons. Enabled gameplay rows
    must have source-critical data complete, then may still appear blocked for
    player-state reasons such as quest locks, Slayer locks, missing supplies,
    missing access, grave/death state, or Wilderness opt-in. Player-facing
    filters default to currently attackable rows so the Combat tab stays usable.
52. Persistent combat statuses such as poison/disease/bleed-style effects may
    continue after leaving combat, but they advance only on review ticks, never
    wall-clock time. Safe noncombat reviews should apply configured healing and
    status damage/cure checks in a predictable order, and cure supplies can
    auto-consume from the combat supply loadout when configured. Any dangerous
    persistent status must be highly visible in the UI.
53. Source-backed combat drops should be allowed into the Bank even when their
    downstream skill use is not implemented yet. Register the item normally with
    provenance and icons where possible, and let the missing downstream action be
    a future acquisition/use gap. Quest-only contextual items remain quest-scoped
    when they have no meaningful nonquest use.
54. Enemy IDs should remain source/entity-specific, not display-name-specific,
    whenever variants differ by stats, drops, access locks, location, or special
    mechanics. The UI can group duplicate names with readable labels. If multiple
    mechanically relevant variants exist in the same selected area/context, the
    combat engine may randomly select among those variants using source-backed
    weights when available or a documented fallback when not.
55. Combat target selection should default to grouped spots/families for ordinary
    training to avoid clutter, with exact NPC variants available through
    drill-down/details for unique monsters, quest bosses, debugging, or
    source-audit inspection. Group rows can disclose possible variants and drops
    while keeping the main Combat tab readable.
56. The default Combat tab should use a `Recommended` filter driven by combat
    preview data, not raw enemy level alone. Recommended targets are attackable,
    non-boss/non-quest/non-task-only by default, risk-rated Safe or Food advised,
    and estimated to take no more than about five successful reviews per ordinary
    kill at the current pacing, gear, style, and supplies. If preview data is
    incomplete, a loose combat-level fallback can be used but should be marked
    less certain.
57. Combat recommendations should be mode-aware rather than one-size-fits-all.
    Use distinct player intents such as Train, Drops, Quests, Bosses, and Slayer
    so ordinary training targets, useful drop sources, quest fights, bosses, and
    future Slayer content do not compete in one opaque recommendation list.
58. Search should become a shared instant fuzzy-search pattern across skill tabs,
    Combat, Quests, and Bank. It should filter per visible surface without
    changing the active target unexpectedly, support fuzzy matching over names
    and important metadata, and remain fast enough to update on every keystroke.
59. Do not treat a modern collection-log UI as source-backed pre-EOC content.
    Local source supports NPC kill counts and boss/slayer kill-count display
    commands, while Darkan cache/source evidence shows Adventurer's Log/tutorial
    style data and drop-table extraction tooling, not a player-facing collection
    log. Combat can track kill counts as source-shaped progress telemetry; unique
    drop history can exist only as AnkiScape convenience/debug metadata, not as a
    2011-authentic feature or reward system.
60. Combat achievements may exist as AnkiScape meta-achievements, separate from
    source-authentic mechanics. Kill counts are source-shaped telemetry;
    achievements can read those counters for broad goals such as first kill,
    first boss kill, first death/reclaim, total-kill milestones, first rare drop,
    and combat-skill level milestones. Avoid monster-specific completionist
    achievements until the enemy registry and drop coverage stabilize.
61. Combat formulas should use exact pre-EOC formulas where local source exposes
    them cleanly, especially hit chance, max hit, equipment bonuses, attack
    speed, style bonuses, defence rolls, and risk/TTK previews. Formula modules
    should declare whether a path is exact, approximate, or blocked. Missing
    source-critical formulas should not be silently replaced with modern/OSRS
    guesses.
62. Combat Magic should require a selected source-backed combat spell/autocast,
    not a generic Magic attack from level alone. The spell registry should carry
    level, rune cost, max hit/effect, spellbook, and unlock gates. Standard
    combat spells come first; Ancient/Lunar combat spells are included only when
    source-backed and locked behind their source spellbook/quest access.
    Noncombat Magic actions remain a later Magic skill surface.
63. Area-of-effect attacks should work only where source-backed and where the
    current combat context has multiple active enemies. Do not model stacking,
    safespotting, or tile positioning. In multi-combat or quantity encounters,
    AoE attacks can roll against a capped number of active targets based on the
    source effect. In ordinary single-target contexts they behave as single-
    target or are blocked if the source requires a multi-target context.
64. Summoning is not part of Combat V1, but the combat engine should have explicit
    familiar/support hooks. Source-required companion effects can be modeled as
    encounter context when already present, but player-summoned combat familiars,
    beast-of-burden supplies, pouch creation, charms, points, and Summoning XP
    are deferred to a later Summoning system. Beast-of-burden supply expansion
    must stay disabled until Summoning exists.
65. Full PvP is deferred, but Wilderness-tagged combat may include a rare PKer
    ambush abstraction to preserve Wilderness risk. This is not source-static
    data and must be labeled as an AnkiScape Wilderness-risk abstraction, because
    PKer frequency depended on live player behavior. Ambushes should be rare,
    visible in risk preview, use source-era player archetypes where possible,
    resolve through the same combat burst engine, and stop/reset the current
    monster encounter if the player survives or retreats.
66. Wilderness death follows source item-retention semantics rather than normal
    PvM grave recovery. In Wilderness, an unskulled player keeps the three most
    valuable risked items, a skulled player keeps zero, Protect Item later adds
    one kept item, and no gravestone appears. Because AnkiScape currently risks
    equipped items only and has no real looter or ground-item loop, Wilderness
    risk applies to equipped items and risked items are removed/lost rather than
    moved to the normal grave or Death's Office flow. Source note: the 2011Scape
    Wilderness Manual says skull lasts 20 minutes, while Darkan code uses 30
    minutes; defer the exact skull timer until full Wilderness/PvP implementation.
67. Wilderness combat requires an explicit risk opt-in surface before first
    activation in a session, because Wilderness deaths can permanently remove
    risked equipment. The panel should show kept-on-death and lost-on-death
    equipment using the current skull/protection assumptions. Do not repeat the
    warning every review; show it again only when the risk set changes materially
    or after a new session/reset.
68. Combat XP is awarded from actual damage dealt during each successful-review
    burst, not only on kills. The chosen attack style determines which combat
    skill receives XP; kills drive kill count, drops, Slayer task progress, and
    encounter or quest completion. The review-action transaction must be
    rollback-compatible: undoing the review must undo damage, XP, supplies,
    drops, death state, and encounter progress produced by that burst. Darkan's
    player combat helper supports the source shape: XP is based on clamped hit
    damage, melee/ranged use damage / 2.5, Constitution/Hitpoints uses damage /
    7.5, combat Magic uses damage / 5 plus spell/splash handling, and controlled
    or defensive styles split XP by style.
69. Failed reviews do not advance active combat. An Again or otherwise failed
    answer produces no player attack, no enemy attack, no poison tick, no food
    use, no XP, no death, and no encounter progress. Combat advancement stays
    tied to successful reviews so it matches AnkiScape's broader progression
    contract and avoids punishing missed cards with unavoidable danger.
70. Leaving ordinary PvM combat for a safe noncombat skill pauses the current
    encounter instead of ending it. Safe successful reviews heal the player by
    100 life points each, capped at max life points, and the enemy does not heal
    unless the encounter explicitly declares regeneration. Returning to Combat
    resumes the same enemy state. Wilderness is an exception: leaving a
    Wilderness encounter counts as retreat, discards the active enemy or PKer
    state, awards no drops, and can later apply Wilderness-specific escape costs
    or cooldowns.
71. Ordinary PvM enemy health persists for the active encounter and should
    survive Anki close/reopen. It resets when the player switches target, changes
    major combat setup, the relevant quest/route state changes, the encounter
    declares regeneration/reset behavior, or Wilderness retreat rules apply.
    Boss phases may persist only inside that active encounter. This requires a
    save-safe active encounter record rather than treating paused combat as
    volatile UI state.
72. Changing combat setup during an active encounter does not reset ordinary PvM
    enemy health. Weapon, spell/autocast, ammo, attack style, armor, shield,
    food queue, potion toggles, and later prayer toggles should affect the next
    successful-review burst, matching the game feel of changing setup mid-fight.
    Reset boundaries remain target change, route/quest state change, explicit
    retreat, death, Wilderness retreat, or encounter-specific reset rules.
73. The Combat tab should use a compact explicit status model: Locked, Ready,
    Fighting, Paused, Blocked, Dead, Grave, and Wilderness risk. One-line reason
    text appears only when state needs explanation, such as missing item, locked
    location, quest requirement, active grave, death reclaim, or Wilderness
    opt-in. Detailed rolls, damage lines, drops, and debug data belong behind an
    expandable history so the combat surface does not become noisy.
74. Combat loot uses source-backed monster drop tables with AnkiScape-native
    delivery. Kills roll the relevant table, including rare drop table access
    where source-backed, then deliver items directly to the Bank or a compact
    loot inbox backed by the Bank tab. Do not model ground-item pickup, 28-slot
    inventory pressure, or manual bank runs for ordinary PvM. The Combat tab
    shows recent notable drops and a collapsible kill log. Wilderness and PKer
    deaths remain separate loss/risk events, not normal monster-loot delivery.
75. Enabled combat data must be complete. Incomplete enemy or encounter data may
    exist only in audit/backlog artifacts, not in the selectable runtime
    registry. The build/generation path should fail closed when an enabled
    combat target or quest encounter lacks source-backed critical fields:
    identity, life points, attack style, attack speed, max hit or formula inputs,
    combat/defence stats, location/quest locks, special mechanics, and drop
    table/no-drop behavior. Quest encounters must not silently auto-complete
    because combat data is missing; source the encounter before enabling it.
76. When Combat implementation begins, treat it as a full-system build rather
    than a narrow proof slice. Use checkpointed loops, source-audit artifacts,
    commits, and targeted tests so the work can resume safely, but do not ship a
    runtime Combat surface that only proves a few enemies while leaving enabled
    enemies, quest combat encounters, loot, death, or rollback as placeholders.
    Partial/incomplete content belongs in backlog/audit artifacts, not in the
    enabled gameplay registry.
77. The combat source-audit target is every source-era enemy in the game, not
    only a curated Combat-tab subset. The Combat tab itself should expose
    repeatable/farmable enemies and farmable post-quest bosses, not one-off quest
    encounters. One-off quest bosses still need complete encounter data for quest
    progression, combat, death, rollback, and rewards, but they should not become
    ordinary selectable farming targets unless the source game allows repeatable
    fighting after the quest or encounter.
78. Preserve mechanically distinct enemy variants as separate registry entries.
    Different combat level, life points, stats, attack style, attack speed, max
    hit, drop table, Slayer requirement, location lock, quest state, or special
    mechanics all justify separate entries. Pure duplicates with identical
    mechanics can collapse into one entry with multiple source locations.
79. Minigame, Dungeoneering, and instanced enemies belong in the global enemy
    registry, but they should not appear as ordinary Combat-tab farming targets
    unless their source context is available. Dungeoneering enemies live behind a
    future Dungeoneering activity. Fight Caves, Fight Kiln, Barrows, God Wars,
    and similar context-bound enemies live behind their source activity, wave,
    dungeon, or boss access rules. The Combat tab may deep-link to those
    activities later, but it must not flatten context-bound enemies into normal
    overworld farming.
80. Required combat items split into reusable source gear versus quest-flow
    items. Real reusable items or tools required to damage/survive enemies should
    be modeled as blockers or combat modifiers, such as dragonfire protection,
    Slayer protection gear, fungicide, mirror shield, or magic secateurs for
    Tanglefoot. Quest-specific one-off items generated inside a quest should not
    become global Bank requirements; the quest stage grants, assumes, or handles
    them contextually when the source flow provides them. Block only when the
    player must bring an externally obtainable item.
81. Immunities, vulnerabilities, and special damage rules must preserve parity
    with the source game. Use a shared combat-affinity layer only where it
    accurately represents source mechanics, such as normal-weapon immunity,
    poison immunity, named weapon/tool/spell requirements, damage reduction
    without protection, dragonfire protection tiers, undead/demon tags, or
    Farming-scaled Tanglefoot damage. If the shared layer cannot match the game,
    write an encounter-specific handler that still plugs into the same combat
    engine instead of bypassing combat.
82. Enemy regeneration, healing, shield phases, invulnerability windows, minion
    phases, and respawn transitions should match the source game where the enemy
    has them. Flattened AnkiScape combat may convert timing or movement
    mechanics into state checks or scripted phase transitions, but the combat
    outcome should preserve game parity as closely as the review-driven model
    allows.
83. Aggressive monsters and passive danger are context-bound. AnkiScape should
    not apply surprise background attacks while the player is doing unrelated
    skills, because it does not model continuous world movement through hostile
    tiles. Aggression matters when the player explicitly enters a combat-bearing
    context: selected Combat target, quest fight, dangerous activity, dungeon,
    minigame, or Wilderness opt-in. Inside that context, aggressive enemies can
    auto-start or auto-retaliate according to source rules.
84. Slayer as a skill loop is deferred. Combat should still carry source-backed
    Slayer metadata on enemies, such as Slayer level, protection items,
    assignment categories, and task-only flags, but it must not implement Slayer
    task assignment, Slayer XP, master pools, skips, blocks, or reward mechanics
    as part of Combat. Monsters that are source task-only stay locked until a
    future Slayer system can provide valid assignments. Monsters that require
    only Slayer level/protection may remain fightable if the future skill-gate
    model can verify the requirement.
85. Equipment level and quest requirements are first-class gates. Weapons,
    armour, shields, ammunition, staves, offhands, and special combat tools need
    source-backed equip requirements such as Attack, Strength, Defence, Ranged,
    Magic, Prayer, Constitution, quest completion, or special unlock state.
    Equipping should be refused when requirements are unmet, and combat
    readiness/risk previews should read the equipped state rather than allowing
    invalid gear to contribute bonuses.
86. Equipment level requirements use base XP-derived levels, not temporary
    boosted or drained current levels. This matches 2011Scape's equip action,
    which checks `getMaxLevel(skill)` against item skill requirements, and
    Darkan's `ItemConstants.canWear`, which checks `getLevelForXp(skillId)`.
    Temporary boosts can still affect combat formulas where source formulas use
    current levels, but they must not unlock gear. If Anki undo/rollback lowers
    base XP below an already-equipped item's requirement, equipment should be
    revalidated and invalid items moved back to the inventory or Bank before
    their bonuses can apply.
87. Combat equipment data scope includes full source-backed behavior, not only
    equip requirements. Equippable combat items need slot metadata, two-handed
    behavior, attack/defence/strength/ranged/prayer/magic bonuses, ammo and
    weapon compatibility, relevant degradation or charge behavior, and relevant
    set effects. Combat formulas and risk previews should use this data directly
    rather than approximating equipment from item names or requirements.
88. Incomplete combat-equipment behavior is an error condition, not an intended
    player-facing state. The source audit/build path should prevent enabling
    combat gear when required behavior is missing. Runtime should still fail
    closed as a last line of defense: a weapon or armor piece with source
    special attacks, degradation/charges, ammo constraints, set effects, or
    required combat modifiers must not silently behave as a plain stat stick
    unless that is source-authentic.
89. Audit every pre-EOC equippable combat item, not only currently obtainable
    gear. Item definitions may exist for future drops, quest rewards, risk
    previews, and source parity, but player acquisition must still come through
    supported AnkiScape routes such as drops, quest rewards, activities, shops,
    or future trade/GE systems. Do not surface unobtainable gear in acquisition
    UI merely because it has been sourced.
90. Before a full shop system exists, Combat may use a temporary shop-backed
    Utility/Activity acquisition route for basic combat gear, runes, ammo, and
    protection gear only when source evidence shows the item was truly sold by a
    pre-EOC shop. These rows must spend coins at source-backed prices, avoid
    invented starter bundles, and be explicitly marked in code/audit notes for
    deletion or migration when real shops are implemented.
91. Temporary combat shop purchases should follow the existing Hunter supplies
    pattern: lightweight Utility/Activity rows that spend coins, add the sourced
    items to the Bank, support normal review batching/rollback, and do not model
    a full shop UI, stock, restock timers, or merchant interaction. This is a
    bridge for source-sold supplies only and must remain easy to delete or
    migrate when real shops are implemented.
92. Combat should not invent passive coin income. Coins for gear, ammo, runes,
    food, reclaim fees, and temporary source-shop purchases come from existing
    player coins, source-backed drops, quest rewards, existing AnkiScape coin
    outputs, and future shops/GE. If a temporary coin route is needed to
    bootstrap Combat, it must be explicit and source-backed rather than a hidden
    stipend. Implementation must respect existing save coins instead of assuming
    a fresh account or a fixed starting balance.
93. A Tutorial Island starter kit is the acceptable early Combat bootstrap, but
    only as an explicit one-time source-backed tutorial claim, not a hidden
    Combat gift. Local Darkan Tutorial Island source shows Vannaka gives a
    bronze sword, wooden shield, shortbow, and 50 bronze arrows; Brynna gives a
    tinderbox, bronze axe, and net; Dezzick gives a bronze pickaxe and hammer;
    Terrova gives 5 air runes and 5 mind runes for Wind Strike. Before
    implementation, re-audit exact item IDs/quantities against the best
    available local 2011-era source, then historical wiki only if local source
    is missing. The claim should deliver items through Bank/Bank Claims, be
    rollback-safe, award no tutorial XP unless Tutorial Island itself is
    modeled, and be marked for migration/deletion if a real Tutorial Island
    activity is added later.
94. Tutorial starter kit migration should avoid surprise mutation of existing
    saves. Brand-new saves can receive or be offered the source-backed Tutorial
    Island starter items automatically as part of first-run bootstrap. Existing
    saves should get an optional one-time Bank/Claims-style tutorial kit claim,
    keyed by a flat claimed flag, so current inventories and progression are not
    silently changed. The claim remains rollback-safe and should not grant
    coins, XP, or non-source tutorial items.

95. Weapon poison is bidirectional and source-backed. Player weapons/ammo that
    poison in pre-EOC (poisoned daggers, spears, throwing knives/darts, poison
    arrows, etc.) can apply poison to enemies, and enemy poison can apply to the
    player (decision 52 already governs the player-as-victim path). Poison is a
    refreshable, non-stacking status that advances only on review ticks inside a
    burst and on safe reviews afterward, never wall-clock. Use source-backed
    initial damage and the source decay/expiry curve, respect poison immunity
    (decision 81), and roll the status back with the atomic review transaction.
    Antipoison cure supplies auto-consume from the combat loadout for the player;
    enemy poison runs to its source expiry.
96. Special attack energy is a persistent, source-rate resource, not a per-burst
    pool. Energy persists globally between bursts and fights and regenerates at the
    source rate of 10% per 50 ticks. Because burst length scales linearly from
    `Actions per review` (decision 10), one successful combat review at 1x (50
    ticks) regenerates about 10%, 2x about 20%, and so on. Specials still gate on
    available energy and the automatic-special setting (decision 43). Whether
    energy also regenerates during safe non-combat reviews is resolved by the
    review-tick recovery model (see Open Major Decisions).
97. Stat-drain and prayer-drain enemy attacks are modeled with source parity.
    Source enemies that drain Attack, Strength, Defence, Ranged, Magic, or Prayer
    reduce the player's current/effective levels used by combat formulas, never the
    base XP-derived levels that gate equipment (decision 86), so a drain can never
    unequip gear. Drains are visible in risk preview and recover under the
    review-tick recovery model, not wall-clock. Restore/prayer-restoring supplies
    can auto-consume from the loadout where source-backed. Prayer drain plugs into
    the deferred Prayer skeleton (decision 13) and fails closed wherever Prayer is
    inactive.
98. Overheal above maximum lifepoints is allowed where source-backed. Saradomin
    brews, rocktails, and similar effects can push lifepoints above the
    Constitution-derived maximum using source values, overriding the hard cap in
    decision 32 for those specific effects only. Overheal decays toward the maximum
    under the review-tick recovery model (per tick inside a burst, per safe review
    afterward), never wall-clock. Ordinary food and the 100-lifepoint safe-review
    heal (decisions 32 and 70) still cap at the maximum.
99. Grave/death mechanics aim for full pre-EOC parity, including stacked deaths. A
    second death while a grave is still active follows source gravestone behavior:
    the existing grave is overwritten/collapsed per source rules and previously
    graved items follow the source consequence (move to Death's Office or be lost)
    rather than silently surviving. Items already in Death's Office persist
    independently and are unaffected by a new death. This extends decisions 14-16;
    Wilderness death keeps its separate item-retention semantics (decisions 66-67).
100. Prayer-impossible encounters remain selectable as opt-in suicide runs.
     Encounters that are effectively unsurvivable without the deferred Prayer system
     are not hidden or hard-blocked for that reason alone; the player may choose to
     attempt them. Risk preview must rate them Death possible/likely and they still
     require explicit confirmation (decision 33). Genuinely missing source-critical
     combat data still blocks per decisions 22 and 75; only prayer-driven
     survivability is treated as the player's risk to accept.
101. Safe healing applies to all non-combat activity uniformly. Every non-combat
     AnkiScape skill/activity counts as a safe context for the 100-lifepoint
     per-review heal and status resolution (decisions 32, 70, 52). AnkiScape does
     not model location-based skilling, Wilderness skilling, or per-location
     XP/danger variation, so there is no unsafe skilling context to exclude.
102. Combat save migration is handled additively when schema changes require it.
     New combat save fields (active-encounter record, supply loadout, grave/Death's
     Office state, special-attack energy, persistent statuses) use additive defaults
     for missing keys, never surprise-mutate existing saves, and preserve
     rollback-safety. The combat data model and enemy/encounter/drop registry schema
     are defined on the fly during implementation rather than pre-specified here,
     but implementation work must still split backend, frontend, assets, balance,
     and testing handoffs explicitly so separate agents or models can work from the
     same contract without guessing.

103. The review-tick recovery model is unified: safe non-combat reviews recover
     every wall-clock-recovering resource, not just lifepoints. One safe
     non-combat review counts as roughly 50 ticks of rest, mirroring the 1x burst
     length, so a single safe successful review restores about 10% special-attack
     energy, restores drained combat stats toward base (about 1 level per 2 safe
     reviews, source 1 level per ~100 ticks), and decays overheal toward maximum,
     all alongside the existing 100-lifepoint heal (decision 70). Inside combat
     bursts these still follow source per-tick rates (decisions 96-98). Failed or
     Again reviews recover nothing (decision 69), and recovery is rollback-safe
     with the atomic review transaction.

104. Dwarf multicannon is a source-acquired, toggleable, breakable Ranged combat
     tool, not a permanent toolbelt unlock. It is purchased through a source-backed
     route (Nulodion's dwarf cannon shop now, the Grand Exchange once a real GE/shop
     system exists), following the temporary shop-backed supply pattern in
     decisions 90-92, and operating it requires Dwarf Cannon quest completion. A
     Combat setting toggles whether the cannon is used during bursts, mirroring the
     automatic-special toggle (decision 43). When enabled it fires automatically in
     parallel with the player's weapon at its source cadence, consumes cannonballs
     as loadout ammo (decisions 37 and 46), uses the source max hit (30 in-era) and
     AoE rotation, and awards Ranged XP per damage dealt (decisions 35 and 68). AoE
     only applies in multi-target contexts (decision 63); single-target contexts get
     extra hits on the one enemy. Model source-backed breakage/overheat requiring
     repair or replacement, and loss-on-death following source retrieval rules
     (reclaim through Nulodion or a Death's Office-style fee). The cannon blocks and
     does not fire in source-restricted areas/encounters, and respects the
     review-safe contract with no mid-review prompts (decision 47).

## Open Major Decisions

- None at the current design depth. All gaps surfaced in this grill round
  (weapon poison, special-attack energy, stat/prayer drain, overheal, stacked
  grave deaths, prayer-impossible suicide runs, safe-everywhere healing, the
  unified review-tick recovery model, save migration, and the Dwarf multicannon)
  are now resolved as decisions 95-104. Continue only if implementation source
  audits reveal a real conflict or missing policy.

## Implementation Handoff

Backend:

- Start from source audits, not from this prose alone. Use local 2011Scape first
  for exact combat formulas, equipment behavior, NPC identity, drops, shops, and
  access locks. Use local Darkan/2012scape as equal implementation evidence where
  2011Scape is missing or incomplete, with historical RuneScape Wiki revisions as
  conflict checks.
- Build a source-wide enemy audit, but enable runtime combat only for rows whose
  critical fields are complete. Critical means identity, life points, combat
  stats/formula inputs, attack style, attack speed, max hit or max-hit formula,
  access locks, special mechanics, and drop-table or explicit no-drop behavior.
- Implement one generic combat engine for ordinary monsters, quest encounters,
  bosses, quantity rows, and phase/form chains. The engine simulates bounded
  0.6-second ticks, not expected-value damage.
- Keep combat as an exclusive selected activity. A successful review advances a
  burst of `50 * Actions per review` ticks, with at most one kill per review.
  Failed/Again reviews do not advance combat or recovery.
- Make each successful review one undo-safe atomic transaction covering HP,
  enemy HP, supplies, ammo/runes, statuses, XP, drops, kill counts, quest combat
  progress, death, grave state, and Death's Office state.
- Route XP by actual damage dealt and selected style: Attack, Strength, Defence,
  Ranged, combat Magic, and Constitution. Drops and kill counts remain kill-based.
- Expand the existing worn-equipment system rather than creating a second loadout
  abstraction. Combat equipment must carry full source-backed behavior, including
  requirements, bonuses, speed, ammo compatibility, specials, charges/degradation,
  set effects, and relevant protection modifiers.
- Use finite combat supply loadouts for food, potions, ammo, runes, cannonballs,
  and later prayer/restore supplies. Refill only at safe boundaries, not between
  bursts inside one active fight.
- Model death with the agreed PvM grave/Death's Office flow and separate
  Wilderness retention/loss rules. Normal inventory is not dropped; equipped gear
  is the risk surface.
- Replace the existing quest-combat threshold resolver with the real combat
  engine only when the relevant encounter has complete source-backed combat data.
  No-stats quest fights stay blocked.

Frontend:

- Add a Combat surface that keeps target selection, global attack style,
  autocast/spell selection, supply loadout, auto-eat threshold, potion toggles,
  automatic specials, optional auto-retreat, and Wilderness opt-in configured
  before reviews. No mid-review prompts.
- Use mode-aware filters such as Recommended, Train, Drops, Quests, Bosses, and
  Slayer. Recommended rows should be attackable, non-boss/non-quest/non-task-only
  by default, risk-rated Safe or Food advised, and estimated around five or fewer
  successful reviews per ordinary kill when preview data is available.
- Enemy rows should expose compact readiness and risk: Locked, Ready, Fighting,
  Paused, Blocked, Dead, Grave, or Wilderness risk, plus short reasons and a
  concise risk band. Detailed tick logs stay behind an expandable history.
- Reuse the Equipment tab and Bank/Bank Claims patterns for gear, supply
  configuration, loot inboxes, grave recovery, and Death's Office reclaim.
- Confirm dangerous or equipment-risking targets before activation, not before
  every review. Wilderness opt-in must show kept/lost equipment when risk changes
  materially or the session resets.

Assets:

- Every enabled combat enemy, drop, equipment item, spell/rune/ammo item, supply,
  grave/reclaim UI item, and temporary source-shop item needs provenance and an
  icon when an appropriate source-era or stable fallback icon exists.
- Prefer source-era item art when the icon changed materially. OSRS art remains a
  practical fallback only for unchanged 2007/2011-shared assets.
- Drop-table import should preserve full source rarities and shared table
  references where source-backed; partial tables must remain explicitly partial.

Balance:

- Use exact pre-EOC formulas where source exposes them cleanly. Formula modules
  must label paths as exact, approximate, or blocked.
- The AnkiScape pacing layer is the bounded burst: `Actions per review` linearly
  scales combat time and therefore progress speed, supply use, and survival risk.
- Safe noncombat reviews count as review-tick recovery: lifepoints heal, statuses
  resolve, overheal decays, stat drains recover, and special-attack energy
  regenerates according to the resolved review-tick policy.

Testing and manual verification:

- Unit tests: combat formulas, damage rolls, XP routing, supply consumption,
  poison/status behavior, special energy, stat drains, death/grave retention,
  drop-table rarity references, enemy readiness, and migration defaults.
- Integration tests: review dispatch, atomic rollback, one-kill cap, quest combat
  handoff, quantity/form chains, death/reclaim, safe noncombat recovery, and
  Wilderness risk.
- Qt tests: Combat tab filters, target rows, risk bands, attack style/spell
  controls, supply loadout controls, dangerous-target confirmation, loot/reclaim
  UI, and no disabled-row selection.
- Manual Anki QA: activate a safe training monster, a dangerous monster with
  auto-eat, a quest encounter, a death/reclaim path, a safe recovery path, and an
  undo rollback after a successful combat burst.

Copy-paste implementation prompt:

```text
In the AnkiScape repo, implement Combat V1 from memory-bank/combat-design-grill-2026-06-23.md. Split backend, frontend, assets, balance, and testing explicitly. Backend starts with source audits and a complete enabled enemy/equipment/drop contract, then one undo-safe 0.6s-tick combat engine shared by ordinary targets and quest encounters. Frontend starts from the backend contract: Combat tab, target filters, attack style/spell controls, risk/readiness, supply loadouts, compact feedback, grave/Death's Office flows, and Qt tests. Keep incomplete source data in audit/backlog artifacts, not enabled gameplay. Run python3 run_tests.py and QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests, then provide manual Anki QA steps.
```

## Completion Audit

- The grill has no remaining open major decisions at this design depth.
- Earlier contradictory policies on enemy visibility and combat pause/reset have
  been reconciled into the later fail-closed runtime-registry and pause/resume
  decisions.
- The handoff now preserves the project rule to split backend and frontend work
  explicitly, even though the design artifact itself is a single document.
- Remaining uncertainty is intentionally shifted to implementation source audits,
  where exact schemas, formulas, and item/enemy coverage must be proven by code
  and tests.
