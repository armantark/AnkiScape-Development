# Achievement Diaries — breadth one, 2026-07-26

## Roster closure supersession — 2026-08-03

The owner-settled curation contract now closes every regional tier at exactly
12 rows, 384 total. Authentic task identities may move only within their source
family and keep their original-tier durable IDs; 22 remaining source shortfalls
are visibly labelled progression anchors using exact same-family period skill
requirements. The 2026-07-26 empty-tier and smaller-roster notes below describe
the original breadth-one state, not the current catalog.

Branch `families/achievement-diaries`. Both lanes green: `python3 run_tests.py`
runs 3,087 tests with 357 skips and no failures; the offscreen Qt lane runs the
same 3,087 with 1 skip and no failures. Baseline before this work was 3,020 and
346.

## What the family is

Eight regional equipment families, each with four tiers, each tier handing over a
real wearable item and a sourced experience lamp. Progress is a durable
owner-scoped ledger at `player_data["achievement_diaries"]`; claiming runs
through `commit_direct_action`, so one Anki undo takes back the item, the lamp
and the ledger together.

The Achievements tab is now the Achievement Cabinet. The 168 fabricated rows and
the moving-denominator percentage are gone from every player-facing surface.

## Sources, and why this was faster than the estimate said

`breadth-next-tranche.md` carried 30-45 hours for this family, and the pass-3
audit called it unstarted with sixteen failing clauses. Both were reasoning from
the wiki. The real unlock was that **Darkan already contains the entire period
achievement system** at
`darkan-world-server/src/main/java/com/rs/game/content/achievements`:

| File | What it owns |
|---|---|
| `Achievement.java` | 1,093 task ids with their period names as enum constants |
| `<Region>Tasks.java` × 9 | the exact per-tier task-id lists, the taskmaster NPC per tier, the reward item ids, and several tier reward effects |
| `SetReward.java` | the eight family → tier → item-id table, including the Morytania legs ids that are absent from the 2011Scape item config |

Darkan does not carry per-task requirements — it reads them from the cache at
runtime — so the pinned pre-cutoff wiki revisions supply those. On five of the
eight families the two sources agree on **every tier's task count exactly**
(Ardougne 23/16/17/5, Karamja 10/19/10/8, Lumbridge 23/19/12/7, Morytania
11/20/11/9, Varrock 19/21/13/9). That agreement is what made an automated join
trustworthy rather than merely convenient.

Reproduce with:

```
python3 tools/harvest_achievement_tasks.py --out memory-bank/source-audits/achievement-diary-harvest-2026-07-26.json
python3 tools/generate_achievement_diary_data.py memory-bank/source-audits/achievement-diary-harvest-2026-07-26.json --items-yml /path/to/game-main/data/cfg/items.yml
```

Depth closure (2026-08-03): the v108 migration regression proves that a
superseded completion is removed, a source-ready deed is re-earned, and an
unrelated completion is preserved. Generation requires the explicit source
argument above instead of one developer's local path. Neither change alters the
live 384-row mechanic.

## The translation rule, and why it is a design fork

A period task is kept only when its pinned wiki row states a requirement, and
its predicate is exactly that stated requirement. Rows that state nothing
measurable are dropped rather than given an invented predicate. 171 tasks
survive.

This flattens "do the deed" into "be able to do the deed". The task's period name
and description are preserved verbatim so the feat survives as identity, but the
predicate is the period's own published gate. That is an AnkiScape abstraction,
labelled at the generator and queued as **design fork 3.8** with the alternative
(hand-translated feats) and a recommendation.

## What did not come through

Falador, Fremennik and Seers' Village use a third wiki table layout the harvester
does not read. Their tiers are real — real reward items, real taskmasters, real
lamps, from Darkan — but carry no tasks. An empty tier reads "Roster pending
harvest" and can never be claimed, so it cannot masquerade as finished. Queued as
**design fork 3.9**; the fix is self-checking, because a correct parse must match
Darkan's counts.

## Equipment

All 32 tier reward items are now registered wearable equipment with sourced
bonuses: 28 from the 2011Scape item config, and the four Morytania legs from
their own pinned pre-cutoff item revisions, because game-main has no rows for
them. Registration goes through a family-owned function, never by editing the
generated table.

The nine Milestone capes gained both halves of their repair: equipment rows, and
the all-skills wear gate. The gate is derived from `trainable_skill_definitions()`
rather than listed, so Dungeoneering joins it automatically when it becomes
trainable — listing it today would make every cape permanently unwearable, which
is the inert-row failure the repair exists to remove.

## Placeholders

One: `achievement_diaries.lamp_minimum_level`. Each family's pinned infobox
states its four lamp experience values exactly and never the skill-level floor,
so every lamp ships with no minimum.

## What the semantics contract required

Its Foundation section forbids diary gear from consuming a recalculated
percentage. Nothing in the family reads one, and the two surfaces that displayed
one are gone. The 168-row catalog stays live as the non-displayed history
substrate the contract defines, so all 21 of its clauses still hold and no save
loses its recorded past.

## Roster depth follow-up — 2026-07-27

The earlier source model was incomplete: Darkan's rev-727 `enums.txt` dump embeds
enum 3483, including every task's display name, description, difficulty and
ordinary skill/quest requirement pairs. The generator now joins that cache data
to the exact membership arrays in the nine `*Tasks.java` classes; the wiki is
corroboration rather than the requirement authority.

The shipped catalog now carries 304 evaluable tasks across ten families. All 34
shipped tiers/pools are non-empty: 260 regional tasks, 14 Burthorpe/Taverley
tasks with exact existing predicates, and 30 Miscellaneous tasks backed by
implemented activity counters or encoded requirements. Tasks without an honest
predicate remain omitted rather than becoming inert rows. Previously shipped
wiki-backed requirement rows remain when Darkan confirms their membership; cache
absence alone is not treated as evidence against them. The exact period
Miscellaneous coin curve remains placeholder-registered as
`achievement_diaries.misc_coin_reward`: the cache-proven 100-coin floor is
multiplied by the task's completion ordinal until the exact payout script is
recovered.

## Taskmaster portraits — 2026-07-27

The claim cards now keep each family taskmaster's name and chathead path together
in `DiaryFamily`, pass the paired persona through the pure Cabinet view, and render
the portrait without changing the one-click claim command. Burthorpe/Taverley now
names Major Nigel Corothers, who hands over its sourced starter kit;
Miscellaneous deliberately has no taskmaster and no portrait.

All nine portraits were fetched through `tools/fetch_assets.py --before` from the
latest upload at or before `2012-11-20T23:59:59Z`. The full MediaWiki image
history mattered: eight current file revisions are post-cutoff, but each has an
older period upload. The asset manifest and provenance tests pin every path, and
`test_every_ready_claim_taskmaster_portrait_matches_its_family` compares each
rendered Qt pixmap with that family's own registered source image. The paired
no-art test proves a named taskmaster with an empty path stays faceless instead
of inheriting another character's portrait.

## Lamp claim correction — 2026-08-01

A diary tier claim now upgrades the equipment and opens a sourced XP-lamp Bank
Claim without applying XP. The player chooses the skill from the Bank, and that
second direct action is independently undoable. Save v107 marks lamps from
pre-v107 claimed tiers as spent because those saves already received the XP
directly. The repository still has no exact per-tier minimum-level floors, so
the former blanket placeholder is split into one registered placeholder per
regional tier until those 32 values are harvested.
