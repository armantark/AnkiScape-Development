# Encounter gap ranking — 2026-08-26

## Purpose and measurement snapshot

This matrix ranks repairable AnkiScape content gaps at commit
`d592e7b66d302787caa13cb2fd216e2cecacad5a`. It uses the eight-input
prioritization rubric in
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/darkan-2012-content-audit-plan.md:401-414`.
The original two commissioned questions appear here as **player-visible
impact**, **dependency leverage**, and **reward/item reachability** rather than
as parallel scores.

The current fixed point measures `196` quests: `33` are completable end to end,
`163` are blocked, `155` have a direct stage blocker, and `8` are blocked only
through prerequisite or quest-point closure. The item-reachability audit at this
commit reports `1,600` actions, `2,173` reachable items, `199` orphan inputs,
and `299` unresolved actions.

## Method

### Player-visible impact: proxy for how quickly a normal player meets the gap

The primary encounter-speed proxy is the **earliest affected quest's
`release_order`**, because the shipped Quests tab defaults to Release Order and
uses `release_order`, then `release_date`, as its sort key
(`ui/ui_tab_quests.py:61-69,192-208,446-452`). Every row also keeps the earliest
quest's difficulty, length, membership, quest-point gate, skill ceiling, and
prerequisite count visible. Those fields are a progression-burden check: an
early Novice quest with no requirements should rank as earlier contact than a
late Grandmaster quest even when both are prominent. I did not collapse these
inputs into a weighted number because no play-frequency or time-to-quest
telemetry exists. The diary ledger has no defensible quest-release equivalent,
so its player-visible score is explicitly judged from its measured family/tier
spread.

### Dependency leverage and reward/item reachability

For a gap class, dependency leverage uses exact first-blocker counts and an
in-memory counterfactual through the same fixed point as
`tools/audit_item_reachability.py:463-890,901-932`. For a specific quest, it
shows both static reverse-prerequisite closure and the immediate fixed-point
delta from optimistically removing that quest's stage gates. Static descendants
are an upper bound, not a promise that all descendants become completable after
one repair. Reward/item reachability uses the same counterfactual's reachable
item and unresolved-action deltas when available; otherwise the cell says that
it was not isolated.

### Other rubric inputs and row granularity

Journey coherence, solo blocker severity, fidelity risk, upstream collision
risk, and effort/verification cost use `High` / `Medium` / `Low` judgments with
the raw reason in the same cell. They are not hidden scores. Collision risk is
narrowly scoped to equivalent work on unmerged `goal/*` branches, active dirty
worktrees, or adjacent work recently landed on `main`; local collision state was
checked through `2026-08-27 00:08 PDT`. The **Repair seam** column makes
data-only, runtime-mechanism, and mixed work explicit.

A shared repair seam is one class row. A blocked quest gets its own row when it
has at least `12` currently blocked transitive prerequisite descendants; this
produces The Lost Tribe, Recipe for Disaster: Another Cook's Quest, Gertrude's
Cat, Priest in Peril, and Underground Pass. Ritual of the Mahjarrat is an
explicit exception because its source gap makes it the clearest current
high-fidelity-risk unit. Class rows and quest rows overlap; their counts must
not be added.

A row is **Measured** when both encounter-speed inputs and downstream scope have
an exact current-tree measurement. It is **Judged** when either commissioned
axis lacks a defensible measurement. Qualitative rubric labels remain judgments
even on a Measured row. No combined weighted score is used; the rank is the
ordering judgment beside all eight raw inputs.

## Ranked matrix

| Rank | Gap | Repair seam | Dependency leverage | Player-visible impact | Journey coherence | Solo blocker severity | Reward/item reachability | Fidelity risk | Upstream collision risk | Effort and verification cost | Evidence | Basis |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Generated `Complete <Quest> stage <N> objective` gates | Mixed: source/data + runtime | **Very high:** `730` exact required-action sentinels across `143` quests; `131` quests have one as their current first blocker. Removing only these gates changes completable quests `33 → 57` and direct stage-blocked quests `155 → 123`. Resolving data gates and sentinels together gives the optimistic `175`-quest ceiling. | **High:** earliest current first blocker is Hazeel Cult, release `#27`, `2002-08-15`, Novice, Short, members, `0` quest points, no skill or quest prerequisite. | **Very high:** the same generated failure breaks otherwise unrelated quest lines across the catalogue. | **High:** the runtime requires an exact flag that no gameplay event emits; there is no player alternative. | Not isolated as a class; the combined data-plus-sentinel counterfactual makes `142` additional quests completable (`33 → 175`), but that delta must not be assigned to sentinels alone. | **High:** bulk auto-completion would erase sourced dialogue, puzzles, transformations, and fights. Each stage needs source harvesting or a proven existing emitter. | **High:** `c7c09f26` and promotion commit `029a294c` are ancestors of current `main` (`afbf483f`) but absent from the pinned baseline; `goal/scabaras-stages-2026-08-26` at `16ff8f2c` remains outside `main`. Re-measure before scheduling or promoting more work. | **Very high:** `730` stage records require source classification; many use existing `auto_actions`, but the long tail needs data and runtime work plus real-kernel progression proof. | Earliest-quest metadata at `generated/quest_catalog_generated.py:3176-3305`; generator creates the exact strings at `tools/build_pre_eoc_quest_catalog.py:2030-2065`; runtime enforces them at `logic_pure/logic_pure_quest.py:803-813`; current queue records `131` first blockers at `memory-bank/design-thread-queue.md:1818-1836`. | Measured |
| 2 | Malformed and under-modelled quest item/alternative requirements | Data/schema | **High:** `19` quests are currently first-blocked only by unreachable item requirements. The generated catalogue contains `241` unregistered `required_inventory` names in `309` uses across `105` quests; this is a review-surface upper bound, not a count of proven malformed values. Only `72` of `954` generated stage rows use `required_inventory_options`. | **Very high:** earliest item-only blocker is Ernest the Chicken, release `#5`, `2001-01-21`, Novice, Medium, free, no skill, quest-point, or prerequisite gate. | **High:** false inventory gates interrupt early standalone quests and long regional chains; flattened alternatives also make valid routes appear impossible. | **High:** an unregistered skill, location, monster, heading, or unavailable item placed in `required_inventory` is a hard solo stop. | Item-only leverage was not isolated. The broader optimistic item/tool/combat data counterfactual changes completable quests `33 → 46`. | **Very high:** the same unregistered set mixes genuine missing items with strings such as locations, spells, monsters, equipment classes, and scraped headings. Treating all `241` names as either items or junk would be equally unsafe. | **Very high:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/req-shapes-2026-08-26` is an active dirty worktree on `goal/quest-requirement-shapes-2026-08-26`, changing `data/quest_data.py`, `tools/audit_item_reachability.py`, and requirement/audit tests for this exact class; re-measure before promotion or parallel work. | **High:** requires a `954`-row source-shape review, route/source additions for genuine items, and explicit OR groups rather than parser heuristics. | Stage schema and option gate: `data/quest_data.py:946-962`, `logic_pure/logic_pure_quest.py:741-800`; generator option handling: `tools/build_pre_eoc_quest_catalog.py:2091-2102`; the census compares generated `required_inventory` mapping keys with `constants.ITEM_DEFINITIONS` storage keys; earliest-quest metadata is at `generated/quest_catalog_generated.py:362-457`. | Measured |
| 3 | Queue 5.21: achievement diary curation ledger | Data/schema + generator | **Large content surface, closure unmeasured:** `253` tasks need authored trigger rows: `146` active prerequisite proxies (`112` level-only and `34` level-plus-quest) plus `107` latent stubs. They span `10` families and `34` tiers. No quest/item fixed-point delta exists for this subsystem. | **High, judged:** the `253` rows are spread through Ardougne `26`, Falador `29`, Fremennik `23`, Karamja `32`, Lumbridge/Draynor `28`, Morytania `21`, Seers' Village `25`, Varrock `28`, Burthorpe/Taverley `38`, and Miscellaneous `3`; easy/onboarding tasks make the defect visible long before endgame, but there is no release-order proxy. | **Very high:** diaries are region-wide progression journals; false triggers break the meaning of completing a tier and the Taskmaster journey. | **Medium:** this is usually false or missing credit rather than a quest-stage hard stop, but dormant rows can block tier truth and prerequisite proxies can award credit without doing the deed. | No item-reachability delta was measured. The rows sit in reward-bearing diary tiers, but this ledger authors predicates; it does not itself prove any new item route. | **Very high:** each row needs a designed trigger, source citation, and disposition (`active`, named-system `dormant`, `swapped`, or `translated`). Prerequisites must not masquerade as deeds. | **Low:** entry 5.21 is queued, not under an equivalent active implementation branch. | **Very high:** `253` source-backed authoring decisions, cross-lineage review, owner spot-check, then generator wiring; the current model lacks disposition, future-system, and designed-trigger fields. | `memory-bank/design-thread-queue.md:2247-2262`; exact proxy split and honest-stop contract at `memory-bank/codex-briefs/pass12-owner-notes-handoff-2026-08-26.md:88-118` (originally counted on `a1c8fc90`, then re-derived unchanged at the pinned commit); schema at `data/achievement_diary_data.py:105-141`. | Judged |
| 4 | Priest in Peril stage 2: resolver-incomplete Temple guardian dog plus dropped Magic immunity | Mixed: combat data + runtime bridge | **Very high for one quest:** `10` direct and `12` transitive blocked dependents. A quest-only optimistic repair changes completable quests `33 → 34`, startable quests `98 → 100`, reachable items `2,173 → 2,186`, unresolved actions `299 → 291`, and orphan inputs `199 → 197`. | **High:** release `#48`, `2004-06-29`, Novice, Medium, members, no skill, quest-point, or prerequisite gate. | **Very high:** this is the access quest for Morytania and a prerequisite spine for twelve later quests. | **High:** stage 2 has one mandatory combat encounter and no alternate route. | `+13` reachable items and `-8` unresolved actions in the quest-only counterfactual; completion also grants Wolfbane and Morytania access. | **Very high:** `magic_damage_immune=True` is declared, but the quest-to-combat bridge forwards `poison_immune` and not Magic immunity. A stats-only repair would be playable but historically false. | **Low:** guaranteed-drop support recently landed as `660fb870`, but no active equivalent stats/immunity repair was found. | **Medium:** source resolver stats, pass the immunity flag through the existing combat contract, and prove both Magic rejection and ordinary kill completion end to end. | Declaration at `data/quest_data.py:7588-7613`; bridge at `logic_pure/logic_pure_quest.py:623-668`; first blocker and counterfactual from the current reachability fixed point. | Measured |
| 5 | Gertrude's Cat stage 5: unreachable Doogle leaves | Data-only | **Very high for one item route:** `10` direct and `12` transitive blocked dependents. A quest-only optimistic repair changes completable quests `33 → 36` (also Icthlarin's Little Helper and Smoking Kills), startable quests `98 → 103`, and reachable items `2,173 → 2,185`. | **High:** release `#43`, `2003-07-28`, Novice, Short, members, no skill, quest-point, or prerequisite gate. | **High:** restores the cat progression spine and removes a prerequisite wall affecting later cat, desert, and Slayer content. | **High:** stage 5 requires Doogle leaves and the fixed point has no reachable route. | `+12` reachable items in the quest-only counterfactual; quest rewards include Kitten, Chocolate cake, and Stew, and later stages produce Doogle sardine and Three little kittens. | **Medium:** the repair needs an authentic Doogle-leaf acquisition and must preserve the sourced kitten chain, but no new general runtime primitive is demonstrated. | **Low:** no equivalent active branch found. | **Low to medium:** one acquisition route plus focused quest and reachability proofs. | First blocker and deltas from the current reachability fixed point; the catalogue row is at `generated/quest_catalog_generated.py:5787-5882` and the item gate is enforced by `logic_pure/logic_pure_quest.py:741-762`. | Measured |
| 6 | Quest combat resolver data completeness | Data-only | **High breadth, limited immediate closure:** `92` of `293` combat rows are not resolver-ready across `48` quests, representing `159` encounter instances by quantity. Only `2` rows are current first blockers; a bounded statless-combat counterfactual changes completable quests `33 → 35` and startable quests `98 → 100`. | **High breadth:** earliest affected quest is Fight Arena, release `#26`, `2002-07-23`, Experienced, Short, members, no skill, quest-point, or prerequisite gate; affected quests extend through release `#194`. | **High:** forty-eight quest journeys contain a declared fight that cannot yet use the resolver, although ninety are hidden behind earlier gates today. | **High for 2 current rows; latent for 90:** Fight Arena and Priest in Peril are immediate hard stops. | Bounded counterfactual: reachable items `2,173 → 2,186`, unresolved actions `299 → 291`, blocked stage rows `155 → 153`, orphan inputs `199 → 197`. Neither immediate combat blocker itself declares a registered guaranteed drop. | **Very high:** classifications are `49` Darkan hitpoints-only, `15` missing resolver stats, `14` parser/variant without usable level, `7` no local source match, `6` same name at wrong Darkan level, and `1` identical Darkan payload available. Glacor proves plausible fallback stats can be absurd. | **Low to medium:** guaranteed-drop support (`660fb870`) recently landed and is adjacent; no active equivalent resolver-stat sourcing branch was found. | **Very high:** `92` source decisions, resolver payloads, loadout/combat probes, and sampled end-to-end quest fights. | Audit implementation and emitted matrix: `tools/audit_quest_combat_stat_gaps.py:23-82,176-254`; resolver readiness: `logic_pure/logic_pure_quest.py:520-562,675-688`. | Measured |
| 7 | Specific gameplay-action emitters and missing quest-event bridge | Runtime mechanism | **High:** from the `33`-quest baseline, neutralizing item/tool/combat data and generated sentinels reaches `175`; neutralizing the residual mechanism gates reaches `196`. The `21`-quest residual comprises `11` specific actions across `9` directly blocked quests plus `12` prerequisite-closure quests. | **Medium:** earliest direct quest is Mourning's End Part I, release `#77`, `2005-07-19`, Master, Long, members, `0` quest points, Ranged `60`, Thieving `50`, and `8` prerequisite quests. | **Very high:** the residual set breaks Elf, Myreque, Fremennik, Penguin, Glouphrie, and Mahjarrat chains after data repair. | **High:** each exact action remains a mandatory flag with no general gameplay-event path into `quest_stage_actions`. | Reward/item delta was not isolated from the `21`-quest mechanism ceiling. | **Very high:** the actions include spells, crafting-table construction, gathering, armour preparation, item repair, and item transformation; mapping them all to generic review progress would invent mechanics. | **Low to medium:** active stub-repair branches are adjacent but do not implement the `11` specific emitters. | **High:** requires shared event-to-quest contracts where real gameplay exists, source-backed automatic actions only where abstraction is intended, and end-to-end proofs from normally started quests. | Exact residual list at `memory-bank/design-thread-queue.md:1818-1836`; earliest-quest metadata at `generated/quest_catalog_generated.py:11620-11969`; runtime write seam at `logic_pure/logic_pure_quest.py:294-310`; current producers are scattered call sites found through `_mark_quest_stage_actions`. | Measured |
| 8 | Required-tool first blockers | Data-only | **Small but direct:** `3` quests are first-blocked only by tool checks: Holy Grail, Back to my Roots, and Smoking Kills. Their isolated completion/item delta was not measured; they are part of the item/tool/combat counterfactual `33 → 46`. | **Very high:** earliest is Holy Grail, release `#24`, `2002-07-23`, Intermediate, Medium to Long, members, `0` quest points, Attack `20`, one prerequisite quest. | **Medium:** three otherwise independent quest journeys stop on the same requirement-shape seam. | **High:** the current tool lookup cannot satisfy the declared requirement through any available inventory, equipment, or toolbelt representation. | Not isolated. | **Medium:** tool categories such as “Any woodcutting hatchet” must map to real tool families without weakening exact-item requirements. | **High:** the active `goal/quest-requirement-shapes-2026-08-26` work changes shared `required_tools` / inventory-option semantics and touches Smoking Kills; coordinate before editing these first blockers. The recently landed claim-tool gate is a different subsystem. | **Low to medium:** three source/data corrections and focused inventory/equipment/toolbelt proofs. | Holy Grail metadata at `generated/quest_catalog_generated.py:2751-2934`; tool enforcement at `logic_pure/logic_pure_quest.py:485-511,789-801`; current first-blocker classification re-derived through the reachability fixed point. | Measured |
| 9 | Underground Pass stage 1 generated gate | Mixed: source/data + runtime | **High static leverage:** `6` direct and `12` transitive blocked dependents. A quest-only optimistic repair changes completable quests `33 → 34`, startable quests `98 → 99`, and reachable items `2,173 → 2,177`. | **High:** release `#36`, `2003-03-03`, Experienced, Long, members, `0` quest points, five skill/combat requirements with a maximum of `79`, and `2` prerequisite quests. | **Very high:** this is the spine into Regicide and the later Elf/Plague chain. | **High:** stage 1 requires an impossible generated objective. | `+4` reachable items in the quest-only counterfactual; completion grants five quest points, Death runes, Fire runes, Iban's staff, and Klank's gauntlets. | **High:** a Long quest with traversal, hazards, fights, and item states cannot be truthfully collapsed into one generic stage click. | **Medium:** overlaps the broad generated-stub branches, but no exact Underground Pass branch was found. | **High:** source-backed stage map plus several runtime/action integrations and end-to-end progression. | Quest metadata and requirements at `generated/quest_catalog_generated.py:4406-4900`; sentinel mechanism at `tools/build_pre_eoc_quest_catalog.py:2030-2065` and `logic_pure/logic_pure_quest.py:803-813`; leverage re-derived from the prerequisite graph and fixed point. | Measured |
| 10 | The Lost Tribe stage 1 generated gate | Mixed: source/data + runtime | **High static leverage:** `5` direct and `13` transitive blocked dependents, the largest blocked-quest descendant closure in the current graph. A quest-only optimistic repair changes completable quests `33 → 34`, startable quests `98 → 99`, and reachable items `2,173 → 2,174`. | **Medium:** release `#74`, `2005-05-31`, Intermediate, Medium, members, `0` quest points, Agility `13`, Mining `17`, Thieving `13`, no prerequisite quest. | **Very high:** opens the Dorgeshuun quest chain, mine, bone-weapon shop, and connected cave progression. | **High:** stage 1 requires an impossible generated objective. | `+1` reachable item immediately; completion grants Ring of life and Dorgeshuun access/unlocks. | **High:** dialogue, cave investigation, and route unlocks need sourced actions rather than generic completion. | **Medium:** overlaps the broad generated-stub branches; no exact active branch found. | **Medium to high:** source-backed stage/action mapping with regional unlock proofs. | Quest metadata at `generated/quest_catalog_generated.py:11103-11267`; prerequisite closure and quest-only counterfactual re-derived at the pinned commit. | Measured |
| 11 | Recipe for Disaster: Another Cook's Quest mixed stage-1 stub/item gate | Mixed: source/data + runtime | **High static leverage:** `12` direct and `12` transitive blocked dependents, corresponding to the twelve Recipe for Disaster continuations. A quest-only optimistic repair changes completable quests `33 → 34`, startable quests `98 → 101`, and reachable items `2,173 → 2,174`. | **Medium:** release `#93`, `2006-03-15`, Special, Short, members, `0` quest points, Cooking `10`, one prerequisite quest. | **Very high:** it is the hub for the whole Recipe for Disaster chain and Culinaromancer's Chest progression. | **High:** stage 1 combines an impossible generated action with unreachable Fruit Blast and Rotten tomato requirements. | `+1` reachable item immediately; completion opens the Culinaromancer's Chest and makes three more quests startable. | **High:** both the actual feast action and the ingredient routes must be sourced; deleting only the stub leaves the item gates. | **Medium:** overlaps the broad generated-stub work, but no exact active branch found. | **Medium:** one compact quest slice, two acquisition routes, and downstream startability checks. | Quest metadata at `generated/quest_catalog_generated.py:14564-14641`; first blocker and deltas from the current fixed point; generated requirement semantics at `tools/build_pre_eoc_quest_catalog.py:2030-2102`. | Measured |
| 12 | Ritual of the Mahjarrat source-faithful implementation | Mixed: source/data + combat/runtime | **Low immediate, high unlock breadth:** `0` direct or transitive quest dependents in this catalogue. A quest-only stage-gate removal changes completable quests by `0` because the quest remains behind `25` prerequisite quests. | **Low/late:** release `#181`, `2011-09-14`, Grandmaster, Very Long, members, `0` quest points, Agility `77`, Crafting `76`, Mining `76`, and `25` prerequisite quests. | **Very high late-game coherence:** it is the capstone connecting Mahjarrat, Glacor, Armadyl, Barrows, Bane, fairy-ring, and Ritual Plateau content. | **High once reached, but not current first contact:** stage 1 is a generated gate and prerequisite closure blocks it earlier today. | Immediate fixed-point delta is `0`; the catalogue lists `11` unlock strings including Glacors, Storm of Armadyl, Armadyl runes/battlestaff, Akrisae, Bane content, and Bloodwood. | **Extreme:** no implementation-level stage map is accepted, and Glacor's available Darkan file lacks per-stat values. A fallback produced a level-475 enemy weaker than a sourced level-145 Gorak. | **Low:** no equivalent active branch found. | **Very high / source-blocked:** requires an accepted stage dossier, several combat payloads and mechanics, and broad end-to-end verification; authentic Glacor per-stat data remains a named unblock. | Catalogue metadata/unlocks at `generated/quest_catalog_generated.py:32204-32301`; Glacor sourcing failure at `memory-bank/design-thread-queue.md:2084-2103`. | Measured |
| 13 | Missing quest condition predicates: equipped clothing sets, damage type, active familiar, carried weight | Mixed: runtime schema + data | **Unknown:** the current schema has no fields for these predicates, and no complete catalogue census maps source requirements onto them. | **Unknown:** source text proves the concepts exist, but the first affected live quest and frequency were not measured. | **Potentially high:** these predicates distinguish route preparation, combat method, follower restrictions, and encumbrance-based progression. | **Unknown:** some will be mandatory hard gates and others advisory route constraints. | Unknown. | **Very high:** flattening these states into inventory possession or generic actions can certify impossible loadouts and wrong combat behavior. | **Low:** no equivalent active branch found. | **High:** add explicit pure predicates and serialized stage fields, then curate each source-backed use; do not infer affected rows from keyword matches. | Current `QuestStageRequirement` has only inventory/options, tools, actions, routes, and combat fields at `data/quest_data.py:946-962`; blocker evaluation at `logic_pure/logic_pure_quest.py:729-850` has no such state gates. | Judged |
| — | Same-stage consumption of `auto_actions` | Runtime mechanism | **No current affected row measured:** a live-catalog scan found `0` stages where the same action appears in both `required_actions` and `auto_actions`. | Not rankable as current player impact. | Latent mechanism constraint only. | Unknown. | None measured. | **High if used carelessly:** `_consume_quest_current_stage_items` marks `auto_actions` only after the current blockers have passed. | **Low:** no equivalent active branch found. | **Medium runtime change, unknown content need:** establish a real source-backed consumer before changing timing semantics. | Gate check at `logic_pure/logic_pure_quest.py:803-813`; auto-action write at `logic_pure/logic_pure_quest.py:1288-1295`; current intersection scan measured `0`. | Judged |

The matrix contains `14` rows: `13` ranked and one deliberately unranked. Its basis split is `11` Measured and `3` Judged.

## Verification and divergences

### Re-derived figures that match

- `196` quests total, `33` completable, `163` blocked, `155` directly
  stage-blocked, and `8` blocked only through prerequisite/quest-point closure.
- `730` `required_actions` strings matching `^Complete .+ stage \d+ objective$`,
  across `143` quests. This is distinct from the `194` generated catalogue quests
  that have a post-requirement completion state.
- First-blocker classes: `131` generated stub, `19` item-only, `8`
  prerequisite closure, `3` required tool, and `2` combat encounter.
- `293` quest combat rows: `201` resolver-ready and `92` not ready across
  `48` quests; the `92` rows represent `159` encounter instances by quantity.
- Optimistic item/tool/combat data repair: completable quests `33 → 46`.
- Optimistic item/tool/combat repair plus all generated objective gates:
  completable quests `33 → 175`, leaving `21` mechanism-blocked quests.
- Generated requirement alternatives: `72` of `954` generated stage rows have
  non-empty `required_inventory_options`.

The optimistic data counterfactual neutralizes required and consumed inventory,
option-group, tool, and combat gates in memory. It is a measurement ceiling, not
a proposed production repair.

### Sentinel-only divergence

Removing only the `730` generated objective requirements in memory produced
`57` completable quests, not `65`. Direct stage-blocked quests fall by `32`
(`155 → 123`), while total blocked quests fall by `24` (`163 → 139`). Eight of
the `32` newly direct-unblocked quests shift into prerequisite/quest-point-only
closure; together with the existing eight, that class grows `8 → 16`. Completion
therefore rises by `24` (`33 → 57`). The matrix uses the re-derived fixed-point
result and does not adopt the stronger interpretation.

## Limits

- This ranking has no player telemetry, elapsed play-time distribution, or UI
  click frequency. Release order plus progression burden is a proxy, not a
  measured time-to-gap.
- Static prerequisite descendants overlap and can remain blocked by their own
  gaps. They are shown beside, never instead of, dynamic counterfactuals.
- The fixed point directly measures quests, items, and actions. Downstream skill
  and activity effects remain source-based journey judgments unless a registered
  route or action delta captures them.
- The `241` unregistered generated `required_inventory` names are a
  review-surface upper bound. Some are genuine missing item identities; others
  are malformed non-items.
- Counterfactuals are optimistic gate-neutralization experiments, not claims
  that a source-faithful repair is equivalent to deleting a requirement.
- No engineering-hours dataset exists. Effort labels are judgments based on
  whether the repair is data-only, source-heavy, or needs a new runtime
  primitive and end-to-end proof.
- Content measurements are pinned to `d592e7b66d302787caa13cb2fd216e2cecacad5a`,
  which is an ancestor of current `main` (`afbf483f`). Current `main` already
  contains stage-stub repairs `c7c09f26` and `029a294c` that the baseline excludes,
  while `16ff8f2c` remains outside `main`; re-run the fixed point before execution.
