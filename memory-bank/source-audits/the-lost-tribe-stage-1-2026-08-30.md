# The Lost Tribe stage-1 requirement audit — 2026-08-30

## Scope and cutoff

This audit replaces only the generated stage-1 sentinel for The Lost Tribe and
covers the directly adjacent start, skill, tool, and light-source gates. The
cutoff is `2012-11-20T00:00:00Z`. It does not assign meanings to intermediate
values of varbit `532`, and it does not recover stages 2–5.

## Cross-thread lead and stop marker

The Darkan thread supplied the lead through a doorbell. Its read-only evidence
file is:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/the-lost-tribe-target-contract.json`

That handoff pins baseline world commit
`e720c3e1f18960653695042b392f4d1180a07b76` and tree
`69353b61f8cd7a2783729fcf7e99df5de4ce23a4`. The
`quest_route.cellar` row says that native parent `6898` displays rubble
`6903` at stage `1`; the player mines it with Mining `17` and a pickaxe, then
squeezes through the resulting hole with Agility `13` and a lit light source.
Wrong-stage and missing-requirement attempts are inert. The contract also names
Goblin Diplomacy and Rune Mysteries as the only acceptance gates, Thieving `13`
as the later Sigmund interaction gate, a tinderbox as a carried tool, and a
lockpick as recommended rather than required.

That row remains exactly
`PARTIAL[source_blocked,conflicting_sources,missing_data]`. Its named source
block is the exact intermediate semantics of varbit `532` beyond started value
`1` and completion value `11`. Do not re-harvest or infer those intermediate
values. This slice needs no intermediate varbit mapping.

## Independently pinned RuneScape Wiki revisions

| Page | oldid | UTC timestamp | Permanent URL |
| --- | ---: | --- | --- |
| The Lost Tribe | `6534350` | `2012-11-04T20:05:19Z` | `https://runescape.wiki/w/The_Lost_Tribe?oldid=6534350` |
| Template:Questreq | `6552449` | `2012-11-13T19:50:29Z` | `https://runescape.wiki/w/Template:Questreq?oldid=6552449` |

Both revisions were fetched as literal wikitext with `curl` through the
MediaWiki API. The article revision has parent `6521105`; the template revision
has parent `6550518`.

The article's literal quest-details block states:

```text
29:|requirements =
30:{{Questreq|The Lost Tribe}}
31:{{Skillreq|Agility|13}}
32:{{Skillreq|Mining|17}}
33:{{Skillreq|Thieving|13}}
34:|items =
35:*A [[light source]] (preferably a covered source such as the [[oil lantern]])
36:*[[Pickaxe]]
37:'''Toolbelt:'''
38:*[[Tinderbox]]
39:'''Recommended:'''
40:*A [[lockpick]]
```

The pinned `Template:Questreq` switch arm resolves the article's historical
quest dependency template exactly:

```text
|The Lost Tribe=:*[[Goblin Diplomacy]]
:*[[Rune Mysteries]]
```

The article then places Mining and Agility at the cellar interaction, not at
acceptance:

```text
60:'''''Skills required:''' 17 Mining, to unblock the tunnel and 13 Agility, to squeeze through.''
62:Go down the ladder in the kitchen and look for a blocked tunnel (named ''Rubble'') and use your pickaxe on it. Make sure that your [[light source]] is illuminated, then squeeze through the tunnel.
```

Line `97` says to pickpocket Sigmund for the key. Together with the quest-details
Thieving `13` row, this places Thieving at that later route interaction. The
article lists a tinderbox, but the cellar interaction requires an already lit
source; therefore the stage gate does not require a tinderbox in addition to a
lit source. The lockpick remains recommended only.

The exact reachable lit-state set is reused from the earlier source audit
`memory-bank/source-audits/quest-light-source-gates-2026-07-16.md`. That audit
pins `Light sources` oldid `6581760`, timestamp `2012-11-19T07:45:54Z`, and
records the eleven reachable lit item states.

## Local 2011Scape check

The read-only checkout at `/Users/ArmanTarkhanian1/Downloads/game-main` contains
no concrete `TheLostTribe : Quest` implementation, so it cannot independently
supply the cellar interaction or acceptance list. Its generic start contract
uses a concrete quest's requirement list at
`game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/QuestExt.kt:84-94`.

The checkout does independently establish these limited facts:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Varbits.kt:537` names
  `THE_LOST_TRIBE_PROGRESS = 532`.
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/runetek5.plugin.kts:106`
  writes varbit `532` value `4` with comment `lumbridge underground` as a
  bootstrap value.
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/quest_tab.plugin.kts:10-12,151-152`
  says undeveloped quests are set complete and writes value `11`.
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/inter/emotes/Emote.kt:39-40`
  unlocks Goblin Bow and Goblin Salute at value `7`.

These values do not define the exact semantics of intermediate varbit `532`
states. In particular, bootstrap value `4` is not evidence that the recovered
native stage-1 cellar contract is stage `4`.

## Source agreement

The pinned article and pinned requirement template agree with the Darkan
contract on Goblin Diplomacy and Rune Mysteries, Agility `13`, Mining `17`,
Thieving `13`, the pickaxe, the lit light source, the tinderbox item listing,
and the recommended lockpick. The article independently states the mine-then-
squeeze sequence. The local 2011Scape checkout is silent on that interaction
but does not conflict with it.

There is no source conflict in the implemented contract. The only unresolved
area is the already named intermediate varbit-`532` semantics, which this slice
does not use.

## AnkiScape translation

- Start acceptance now requires only Goblin Diplomacy and Rune Mysteries.
- Stage `1` reuses the existing quest-stage skill blockers for Agility `13` and
  Mining `17`, the existing pickaxe tool requirement, and the existing exact
  lit-light-source alternative group.
- The generated Tinderbox gate and
  `Complete The Lost Tribe stage 1 objective` sentinel are removed.
- A successful quest review records
  `Mine the Lumbridge cellar rubble and squeeze through the resulting hole`
  only after every stage blocker passes, then advances to stage `2`.
- The misplaced generated stage-2 pickaxe and lit-source gates are removed so
  the same cellar interaction is not charged twice.
- Thieving `13` moves from quest acceptance to stage `5`, where the pinned
  walkthrough places the Sigmund pickpocket interaction.

This uses the existing skill-requirement, tool-requirement, and quest-stage
action contracts. It adds no mining or Agility minigame and no intermediate
quest-state model.

## Reachability result

| Pin | Before | After |
| --- | ---: | ---: |
| `action_count` | 1601 | 1601 |
| `reachable_item_count` | 2237 | 2237 |
| `orphan_input_count` | 190 | 190 |
| `root_orphan_count` | 39 | 39 |
| `cascade_orphan_count` | 151 | 151 |
| `unresolved_action_count` | 277 | 277 |
| `seed_item_count` | 1177 | 1177 |

`Complete The Lost Tribe stage 1 objective` has no location in
`missing_required_actions` after the repair. The audit now stops The Lost Tribe
at the still-generated stage-2 sentinel
`Complete The Lost Tribe stage 2 objective`. Therefore the completable-quest
count remains `43` before and after, with no newly completable or
no-longer-completable quest. Restoring the two acceptance prerequisites reduces
the optimistic startable-quest closure from `114` to `113`; the sole removed
quest is The Lost Tribe itself because Goblin Diplomacy is not yet completable
in that closure: its first blocked row is stage `1`, missing `Orange goblin
mail`, while Rune Mysteries is completable. This count does not come from
stage-local skills:
`_quest_completion_sets` considers only completed quest prerequisites and quest
points, while `start_quest_pure` still accepts The Lost Tribe once Goblin
Diplomacy and Rune Mysteries are complete. Mining `17` and Agility `13` gate the
stage-1 cellar interaction, and Thieving `13` gates the stage-5 Sigmund
interaction. The count change is therefore a prerequisite correction, not an
acceptance gate for those skills. The global blocked quest-stage row count
remains `146`.

## Placeholder and second-level findings

No placeholder is registered. Every concrete value shipped by this slice is
closed by the Darkan contract and the two independently pinned period wiki
revisions. The blocked intermediate meanings of varbit `532` are not assigned a
substitute value.

Two pre-existing cleanup-schema papercuts were found and left unchanged because
they are one breadth level beyond this quest repair:

- `QuestStageRequirementCleanup` declares `add_required_tools` twice; Python
  keeps the later annotation.
- `_append_stage_item_pairs` contains two consecutive `continue` statements in
  its existing-item branch.

Stages 2–5 retain generated sentinel actions. They require separate source
passes and must pair every future sentinel removal with a real auto action; an
auto action added without removing the same-stage required action can never run.

## Verification

- Accepted-slice focused: `Ran 88 tests in 74.237s` and `OK`.
- Rebased plain: `Ran 4544 tests in 381.617s` and `OK (skipped=514)`.
- Rebased offscreen Qt: `Ran 4544 tests in 680.376s` and `OK (skipped=3)`.
- Documentation: `Audited 608 Markdown and 441 HTML files.` and
  `Documentation audit passed.`
- Accepted-slice test quality: `4503 tests across 221 files`, `hard issues: 0`,
  and `structural clone candidates: 31 groups`.
- Reachability: exit `1` is the expected unresolved-global-baseline signal; the
  seven measured pins are the values above, the stage-1 sentinel has zero live
  stage-contract or `missing_required_actions` locations, the stage-2 sentinel
  remains, and there are `146` blocked stage rows. The exact stage-1 text remains
  only in the inert raw generated-catalog input, the cleanup removal key, its
  regression assertion, and audit prose.
- Quest closure: completable quests remain `43 → 43` with empty newly and
  no-longer-completable sets; startable quests move `114 → 113`.
- Worktrees: `Worktree layout safe` with the linked root at
  `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees`.
- Review: Kimi K3 returned HTTP 403 `You've reached your weekly (7-day) usage
  limit`; GLM 5.3 Flash found one order-coupled blocker assertion, which was
  replaced with kind-filtered contract assertions before the final focused run.
