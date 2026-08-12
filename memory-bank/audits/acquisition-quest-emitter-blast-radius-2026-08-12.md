# Acquisition triage and quest-emitter blast radius — 2026-08-12

## Scope and outcome

This read-only acquisition slice began from the corrected reachability baseline on
`goal/acquire-2026-08-12`: 1,556 actions, 2,493 reachable items, 103 orphan
inputs, and 102 blocked actions. No product code changed.

The candidate family was Snake hide. The authentic Bush-snake route is inert for
an ordinary player because Tai Bwo Wannai Cleanup requires Jungle Potion, Jungle
Potion requires Druidic Ritual, and both quests stop on un-emitted
`required_actions`. The slice stopped before implementation as required.

## Quest-action emitter count

The live `QUEST_DATA` registry contains 196 playable entries: 194 generated
catalog quests plus two miniquests. It contains:

- 1,096 `required_actions` occurrences, 1,095 distinct strings, across 185
  quests;
- 101 `auto_actions` occurrences, 100 distinct strings;
- zero intersections between required-action and auto-action strings, globally
  or when keyed by quest;
- 783 generated placeholders matching
  `Complete X stage N objective`; and
- 313 hand-authored action occurrences.

Therefore 185 of 196 quests are directly uncompletable through ordinary runtime
progression because each reaches at least one action that no runtime path marks.
The reverse prerequisite closure adds five catalog entries whose own stages have
no required action but whose prerequisites are blocked:

- `hunt_for_surok`;
- `icthlarins_little_helper`;
- `lair_of_tarn_razorlor`;
- `shilo_village`; and
- `smoking_kills`.

The approximate completion impact is therefore 190 of 196 quests. The six not
affected by this specific dependency are `cooks_assistant`,
`diamond_in_the_rough`, `goblin_diplomacy`, `imp_catcher`, `stolen_hearts`, and
`the_knights_sword`. This does not prove that those six are free of other gates.

Of the 185 directly action-blocked quests, 175 first stop at stage 1. Ten first
stop later: `a_souls_bane`, `demon_slayer`, `dragon_slayer`, `family_crest`,
`fight_arena`, `plague_city`, `tai_bwo_wannai_trio`, `temple_of_ikov`,
`vampyre_slayer`, and `witchs_house`.

### Counting method

1. Import the assembled `core.constants.QUEST_DATA`, so catalog overrides and
   miniquests are counted.
2. Enumerate every stage's `required_actions` and `auto_actions`.
3. Classify generated placeholders with
   `^Complete .+ stage [1-9][0-9]* objective$`.
4. Compare required and emitted action IDs globally and quest-scoped.
5. Seed the prerequisite graph with the 185 directly blocked quest IDs and take
   its reverse transitive closure.

The repository's independent coverage audit reports 196 quests, 1,146 stage
rows, 994 rows with action blockers, and 185 quests with action blockers. The
runtime reads quest-scoped action flags in
`logic_pure/logic_pure_quest.py:263-311`, records `auto_actions` only after a
blocker-free stage in `logic_pure/logic_pure_quest.py:1239-1255`, and rejects
progress while any blocker remains in `logic_pure/logic_pure_quest.py:1436-1461`.
The catalog builder creates the placeholder action form at
`tools/build_pre_eoc_quest_catalog.py:2012-2047`.

A positive-control runtime probe used Druidic Ritual stage 1. Without the known
action flag, it returned `Action required: Speak to Sanfew about the ritual
ingredients`; after placing that exact action in
`quest_stage_actions["druidic_ritual"]`, the blocker disappeared. This proves
the probe can observe both states.

## Approximate completion-gated content

These are registered content targets or records, not unique reachable items:

| Category | Completion-gated population tied to action-blocked quests |
| --- | ---: |
| Combat enemies | 15 targets |
| Slayer | 17 families / 21 enemy targets |
| Magic | 56 action or spell targets |
| Explicit skill/activity unlocks | 22 rules / 36 target IDs |
| Completion-only shops | 33 shops |
| Quest-start shops downstream of affected quests | 25 shops / 190 stock rows |
| Dependent quests | 110 quests; 406 prerequisite edges target blocked quests |

Additional directly completion-gated records include nine Agility records, three
Thieving records, one Construction style, one Temple Trekking event, and one
Barrows record.

Two item bounds answer different questions:

- **80 items** is the measured graph correction already established by
  `memory-bank/audits/quest-stage-reachability-truth-2026-08-12.md`: blocked
  quest-stage production reduced the truthful reachable total from 2,573 to
  2,493.
- **398 unique item names** is a definition-level upper bound across the 185
  directly blocked quests: 131 stage-produced names plus 272 final-reward names,
  with five overlapping. It is not a reachability count because other sources
  can overlap and rewards include currency.

The larger finding is that the blast radius extends beyond quest products.
Every combat enemy, activity, spell, shop, skill target, or later quest gated on
completion is also inert when its upstream quest cannot finish.

## Snake-hide route and stop gate

Period sources establish:

- `Snake hide?oldid=6009794`, lead and Dropping monsters sections: Bush snakes
  drop Snake hide, always, quantity 1–5.
- `Bush snake?oldid=6352282`, infobox and 100% Drops section: combat level 35,
  250 life points, melee, maximum hit 38, Stab weakness, Bones ×1, and Snake
  hide ×1–5 always.
- `Tai Bwo Wannai Cleanup?oldid=6539724`, lead, Preparation, Cutting the jungle,
  and Killing threats sections: Jungle Potion completion, a machete, Woodcutting
  10/20/35 by jungle density, and Bush snake as a threat that drops Snake hide.
- `Jungle Potion?oldid=6555418`, walkthrough and reward sections: the quest
  route itself.

The Bush-snake oldid carries a page-level `{{beta}}` marker. Its drop quantity is
independently corroborated by the in-period Snake-hide oldid, so the 1–5 value
does not rely on that marked page alone.

Darkan's
`data/npcs/drops/bush_snake.json` gives item 6287 exactly 1–1. Per-file
`git log -- data/npcs/drops/bush_snake.json` shows one supplying commit,
`c6fbe036b1743f4dd6067ec178332c69c3708856` (`Initial commit`). The Darkan
restoration thread independently confirmed that this is a genuine original
Darkan-versus-period divergence, not a reconstruction artifact. The dated period
wiki range wins: future implementation must model an always drop with quantity
1–5, not Darkan's fixed one and not a name-wide generic Snake table.

The live blocker probe confirms:

- Druidic Ritual stages 1–3 require un-emitted hand-authored actions; and
- Jungle Potion stages 1–4 require un-emitted generated placeholder actions.

`runtime/runtime_actions_production.py:1298-1389` deactivates Questing and rejects
progress when these stage blocker reasons exist. Consequently an ordinary
level-one-start player cannot complete Jungle Potion and cannot enter Tai Bwo
Wannai Cleanup. Adding Bush snake alone would create an inert acquisition route,
so no product implementation, tests, mutation run, or full test lanes were
started.

## Darkan evidence handling

Reusable rules were added to
`memory-bank/pre-eoc-source-verification-standard.md`:

1. Exclude all 85 tracked
   `src/main/java/com/rs/web/*AuditProbe.kt` files unconditionally. They are audit
   instrumentation and circular evidence by construction. A positive-control
   listing found `TaiBwoWannaiCleanupAuditProbe.kt` inside that exact set.
2. For every other Darkan file, inspect `git log -- <path>` rather than applying
   a recency cutoff. Upstream refactors can be recent; restoration commits are
   unit-scoped.
3. When a restored unit has a frozen contract under
   `memory-bank/audit/reports/`, use that contract as the authority on proof,
   inference, and deferrals. The completed unit set reported by the restoration
   thread is Crucible 425, Dominion Tower 426, Duel Arena 427, and Fist of Guthix
   428. This AnkiScape worktree does not contain those external reports, so this
   slice records the rule without claiming it read them.
4. Record the section that supports each wiki claim. Trivia, update-history,
   scam, exploit, and glitch material is historical or unclear unless separately
   proved. Check page-level markers such as `{{beta}}`.

The restoration thread also independently confirmed a second genuine divergence:
Darkan's original `Silver.java` uses Crafting 20 for the demonic sigil while the
period wiki differs. As with Bush snake, the period source wins and the departure
must be explicit.

## Search discipline

A durable positive-control rule was also added to
`memory-bank/pre-eoc-source-verification-standard.md`: a negative query is not
evidence of absence until the same probe has demonstrated a known hit. Until
then, report only that the search with the stated parameters did not find the
target.

The rule records seven concrete false negatives from one day: a nonexistent
reachability key, `getattr` against dict-form quest combat drops, branch-name
globs that could not match `breadth`, `5,000` versus `5000`, the wrong Gradle
property name, insufficient `find -maxdepth`, and an unquoted path with spaces
that resolved to the wrong sibling tree.

## Reachability and omissions

Before and after remain identical:

| Metric | Before | After |
| --- | ---: | ---: |
| Actions | 1,556 | 1,556 |
| Reachable items | 2,493 | 2,493 |
| Orphan inputs | 103 | 103 |
| Blocked actions | 102 | 102 |

No new item or route exists. No product files changed. No full test lane or
mutation proof applies because the ordinary-player accessibility gate failed
before implementation. The single unblocking action is to implement and verify
the production quest-action interaction/emitter path so Druidic Ritual and
Jungle Potion can be completed from ordinary attainable state.
