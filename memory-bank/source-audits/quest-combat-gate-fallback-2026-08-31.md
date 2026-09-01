# Quest combat gate fallback source audit — 2026-08-31

## Authority and source

The branch started from `3336d4ba6cc58452bc23d15c9378e2a414a01fe8`.
The owner's ruling in `memory-bank/design-thread-queue.md` section 4.22 item 1
reverses the enemy-level fallback: a quest encounter with no explicit
`npc_configs.minimum_player_combat` has no aggregate player-combat gate.

The read-only Darkan quest sources corroborate the only two aggregate quest
entry gates:

- Smoking Kills checks `player.skills.combatLevel >= 85` in
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/smokingkills/SmokingKills.kt:76-89`
  and refuses `startQuest()` when the requirements fail.
- Dream Mentor checks the same threshold in
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/dreammentor/DreamMentor.kt:250-261`
  and also refuses at `startQuest()`.

Both quests already carried `{"skill_id": "combat", "level": 85}` in their
quest-level `required_skills`, and the runtime already resolves that pseudo-skill
through `player_combat_level_pure`. No duplicate entry gate was added.

## Runtime and audit decision

Both runtime reads now default `minimum_player_combat` to zero:

- encounter readiness in `logic_pure/logic_pure_quest.py`;
- current-stage blocker construction in the same module.

The reachability model in `tools/audit_item_reachability.py` now uses the same
missing-field meaning. A repository-wide Python search found no other fallback
from `minimum_player_combat` to an encounter level.

The ten explicit encounter gates remain unchanged. Six Smoking Kills fights
retain gate 85. Chronozon, Bork, and Tarn's two forms retain gate 1. All four
explicit gate-1 values are now redundant, but they remain because they are
harmless and preserve the sourced record that those fights intentionally have
no aggregate player-combat requirement.

The prior sentence in
`memory-bank/source-audits/quest-smoking-kills-playable-2026-07-18.md` saying
other encounters retain an enemy-level gate is marked superseded by the owner
ruling. The miniquest ledger now records why its explicit 1 values remain.

## Measured predicate effect

A live catalog probe measured 293 encounter rows and a maximum attainable combat
level of 138.

| Predicate census | Before | After |
| --- | ---: | ---: |
| Missing resolver stats | 91 | 91 |
| Missing explicit gate and enemy level above 138 | 64 | 0 |
| In both groups | 24 | 0 as a combat gate; still blocked on stats |
| Impossible encounter union | 131 | 91 |
| Quests represented in the impossible union | 60 | 47 |

The fallback reversal therefore clears 40 of the 131 impossible encounters.
It removes the inherited combat predicate from all 64 affected rows, but the 24
rows that also lack resolver stats remain impossible. The separate 91-row stat
sourcing backlog is unchanged.

## Reachability measurements

The complete pre-change and post-change reachability JSON reports are identical.
Earlier required-action blockers stop the affected quest branches before these
combat rows, so the current fixed-point report does not yet expose the
conditional +23 quests / +39 items measured after that separate blocker family
is cleared.

| Measure | Before | After |
| --- | ---: | ---: |
| `action_count` | 1663 | 1663 |
| `reachable_item_count` | 2301 | 2301 |
| `orphan_input_count` | 165 | 165 |
| `root_orphan_count` | 32 | 32 |
| `cascade_orphan_count` | 133 | 133 |
| `unresolved_action_count` | 252 | 252 |
| `seed_item_count` | 1215 | 1215 |
| blocked quest-stage rows | 139 | 139 |
| completable quests | 51 | 51 |

No reachability pin moved.

## Coverage

`tests/test_quest_combat_gate_fallback.py` covers an ungated level-699 encounter,
all ten explicit gate boundaries, both quest-entry combat-85 gates, every
ungated catalog encounter, and a real `on_answer_card` review that defeats the
formerly impossible level-170 Sea Troll Queen. The focused combat and
reachability selection passes 64 tests. The stat-gap audit remains pinned at 91
rows with its six classifications unchanged.
