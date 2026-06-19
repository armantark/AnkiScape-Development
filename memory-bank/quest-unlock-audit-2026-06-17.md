# Quest Unlock Audit - 2026-06-17

Purpose: inventory the implemented AnkiScape skill surface and separate content
that should be locked by quest completion from content that only looks
quest-related because a source location, quest stage, or acquisition route is
special. This is intended as a durable record for quest-lock migrations after
the Rune Mysteries pilot and full pre-EOC quest-catalog pass settled the final
pattern.

## Source Policy

- Prefer local 2011Scape source when it has the behavior.
- Use archived 2011 Knowledge Base pages for requirements and map/location
  facts that the emulator source does not model.
- Use RuneScape Wiki/Fandom only where the local source and 2011Scape archive do
  not expose a specific item acquisition rule.
- Completion unlocks are not the same thing as route locks. Do not global-gate a
  skill target just because one location or source NPC is quest-restricted, unless
  the current AnkiScape row effectively represents that route or region and would
  otherwise make a locked area playable before its logical quest precedent.
- Quest-stage recipes are not completion unlocks. They need stage-aware quest
  state before they should be copied into the normal `quest_completed_pure`
  pattern.

## Implementation Status - 2026-06-17

The broad quest catalog is now implemented in the live add-on. `quest_data.py`
builds `QUESTS` from generated `quest_catalog_generated.py` data covering 194
pre-EOC quest rows: every RuneScape quest available before the 2012-11-20
Evolution of Combat release, with Recipe for Disaster split into its 10
subquests. The generator is `tools/build_pre_eoc_quest_catalog.py`; it caches
old RuneScape Wiki revisions under `tools/.cache/`, includes quests that only
became `former` after EOC, excludes pre-EOC replacements, and records per-quest
source oldids, release order, requirements, quest-point rewards, XP rewards,
item rewards, XP lamp rewards, unlock text, and journal stages. Do not hand-edit
the generated catalog; update the generator or the override layer.

Journals are source-backed for every generated quest row. The source priority is
local 2011Scape `QuestStage` text, then RuneScape Wiki quick-guide checklist
stages, then oldid walkthrough prose when a quick guide does not exist. Black
Knights' Fortress currently uses the walkthrough-prose fallback because the wiki
has no quick-guide subpage for the historical/current title.

All quest rewards should be brought in. Direct item rewards register as
inventory items and are granted on quest completion. XP lamps are flattened into
Bank Claims with the source quantity, amount, allowed skill options, and minimum
level preserved; the UI intentionally uses one `Choose skill` flow instead of
copying every historical quest-specific lamp/chatbox interface.

The priority completion unlocks from this audit remain hand-audited overrides
layered on top of the generated catalog: Rune Mysteries, Lost City, Tai Bwo
Wannai Trio, Mourning's End Part II, Swan Song, Lunar Diplomacy, and Legacy of
Seergaze keep bespoke compact journal stages, stricter 2011-era requirements,
concrete item rewards, and unlock text.

Strong completion gates now live in a central `QUEST_UNLOCK_RULES` registry and
feed pure lock-reason helpers for Mining, Fishing, Cooking, Firemaking,
Runecrafting, and Utility/Activities. The implemented locks are:

| Quest | Targets now gated |
| --- | --- |
| Rune Mysteries | Mining `rune_essence` plus the existing global Runecrafting/Wicked hood gates |
| Lost City | Runecrafting `craft_cosmic_runes`, `bind_cosmic_tiara`, `feed_cosmic_talisman_to_hood`, `feed_cosmic_tiara_to_hood` |
| Lunar Diplomacy | Runecrafting `craft_astral_runes` |
| Mourning's End Part II | Runecrafting `craft_death_runes`, `bind_death_tiara`, `feed_death_talisman_to_hood`, `feed_death_tiara_to_hood` |
| Legacy of Seergaze | Runecrafting `craft_blood_runes`, `bind_blood_tiara`, `feed_blood_talisman_to_hood`, `feed_blood_tiara_to_hood` |
| Swan Song | Fishing `catch_monkfish` |
| Tai Bwo Wannai Trio | Fishing `catch_karambwan` |
| Shilo Village | Mining `gem_rocks` |
| Priest in Peril | Fishing `catch_slimy_eel`; Cooking `cook_slimy_eel`, `cook_thin_snail`, `cook_lean_snail`, `cook_fat_snail`; Utility `gather_thin_snails`, `gather_lean_snails`, `gather_fat_snails` |
| The Fremennik Isles | Firemaking `arctic_pine_logs`; Cooking `cook_yak`; Utility `scavenge_raw_yak_meat` |

Quest starts are strict. If a required skill is not implemented, or a
prerequisite quest is incomplete or missing, the quest is impossible to start
and the UI surfaces a concise requirement tooltip instead of allowing an
approximation. XP rewards for implemented skills are granted on completion; XP
rewards for unimplemented skills are stored in `pending_skill_exp_rewards` and
applied programmatically during save migration once the relevant skill exists.

The Quests tab is now collapsible and sortable. It defaults to real
RuneScape release order, while also exposing the live-game sort modes
Free/Members, Progress, Difficulty, Timeline, and Length. Completed quest
bodies are collapsed by default, and the active in-progress quest remains
expanded.

## Current Quest Surface

Historical note from before the implementation passes: quest state was minimal
and completion-based:

- `quest_data.py:15` defines `rune_mysteries`.
- `quest_data.py:130-145` registers Rune Mysteries as the only quest.
- `quest_data.py:42-48` defines claim requirements with default Rune Mysteries
  and Runecrafting level 5 requirements.
- `logic_pure.py:623-636` exposes `quest_state_pure()` and
  `quest_completed_pure()`.
- `logic_pure.py:777-779` makes Rune Mysteries the global Runecrafting unlock.
- `logic_pure.py:973-1011` applies the Runecrafting lock reasons; today these
  include the global Rune Mysteries check, levels, materials, altar access, and
  hood feed state, but no per-altar quest gates.

## Quest Gates Already Implemented

| Quest | Unlock | Current implementation | Verdict |
| --- | --- | --- | --- |
| Rune Mysteries | Runecrafting skill access | `runecrafting_unlocked_pure()` blocks every Runecrafting target until `quest_completed_pure(player_data, "rune_mysteries")` is true. | Keep. This matches local source and 2011 KB evidence. |
| Rune Mysteries + Runecrafting 5 | Wicked hood one-time Bank Claim | `CLAIMS` defaults require Rune Mysteries and Runecrafting 5; `claim_locked_reasons_pure()` enforces both. | Keep. This is an AnkiScape adaptation, not a direct 2011Scape quest unlock. |

Evidence:

- Local source `skills/runecrafting/runecrafting.plugin.kts:17-31` checks
  `finishedQuest(RuneMysteries)` before entering runecrafting ruins by talisman
  or tiara/varbit entry.
- 2011Scape Runecrafting basics says mining your own rune essence requires Rune
  Mysteries and lists Rune Mysteries as the entry point to rune essence access:
  https://www.2011.rs/kb/runecrafting_the_basics

## Resolved Quest-Gate Candidates

These audit candidates have been converted into completion gates. Generic route
modeling still does not exist, but route/location requirements can be flattened
to logical quest precedents when the current AnkiScape row effectively represents
that region route.

| Quest | Skill | Implemented target/action IDs | Lock type | Why it should be gated |
| --- | --- | --- | --- | --- |
| Rune Mysteries | Mining | `rune_essence` | Completion unlock | `mining_data.py:129-145` exposes Rune essence and Pure essence through one target. Local Sedridor/Aubury teleport source and the 2011 KB state that essence mine access requires Rune Mysteries. |
| Lost City | Runecrafting | `craft_cosmic_runes`, `bind_cosmic_tiara`, `feed_cosmic_talisman_to_hood`, `feed_cosmic_tiara_to_hood` | Completion unlock | The cosmic altar is inside Zanaris/Lost City. The 2011 KB explicitly says cosmic runes require Lost City. |
| Lunar Diplomacy | Runecrafting | `craft_astral_runes` | Completion or route unlock | The astral altar is on Lunar Isle and the 2011 KB says Lunar Isle is reached on Lunar Diplomacy. Astral has no talisman/tiara/hood-feed rows in current data. |
| Mourning's End Part II | Runecrafting | `craft_death_runes`, `bind_death_tiara`, `feed_death_talisman_to_hood`, `feed_death_tiara_to_hood` | Completion unlock | The 2011 KB says death runes require Mourning's End Part II and locates the altar in the Temple of Light. |
| Legacy of Seergaze | Runecrafting | `craft_blood_runes`, `bind_blood_tiara`, `feed_blood_talisman_to_hood`, `feed_blood_tiara_to_hood` | Completion unlock | The 2011 KB says blood runes require Legacy of Seergaze and locates the altar beneath Castle Drakan. |
| Swan Song | Fishing | `catch_monkfish` | Completion unlock | `fishing_data.py:237-243` exposes monkfish. Raw monkfish can only be caught at Piscatoris Fishing Colony, which requires Swan Song completion. |
| Tai Bwo Wannai Trio | Fishing | `catch_karambwan` | Partial-or-completion unlock | `fishing_data.py:244-251` exposes karambwan. Wiki evidence says catching raw karambwan requires at least partial Tai Bwo Wannai Trio completion. For AnkiScape's completion-only quest model, use full completion unless stage-aware quest state exists. |
| Shilo Village | Mining | `gem_rocks` | Completion unlock | The generic AnkiScape target currently represents the useful gem-rock route. Use Shilo Village completion until a route/location model can distinguish Shilo from other gem-rock sources. |
| Priest in Peril | Fishing/Cooking/Utility | `catch_slimy_eel`, `cook_slimy_eel`, `cook_thin_snail`, `cook_lean_snail`, `cook_fat_snail`, `gather_thin_snails`, `gather_lean_snails`, `gather_fat_snails` | Logical route precedent | The current slimy eel and snail rows make Morytania swamp content playable without a route model. Priest in Peril is the stable logical gate for entering Morytania; Nature Spirit can remain a future refinement if stage/area modeling gets deeper. |
| The Fremennik Isles | Firemaking/Cooking/Utility | `arctic_pine_logs`, `cook_yak`, `scavenge_raw_yak_meat` | Logical route precedent | The current arctic pine and yak rows effectively represent Neitiznot content. Use The Fremennik Isles completion until AnkiScape has location-aware acquisition routes. |

Source links:

- Runecrafting requirements and essence access:
  https://www.2011.rs/kb/runecrafting_the_basics
- Runecrafting altar locations:
  https://www.2011.rs/kb/runecrafting_locating_the_altars
- Rune essence mine access:
  https://www.2011.rs/kb/mining_the_rune_essence_mine
- Raw monkfish:
  https://runescape.fandom.com/wiki/Raw_monkfish
- Raw karambwan:
  https://runescape.fandom.com/wiki/Raw_karambwan
- Gem rock source used by the implementation:
  https://runescape.wiki/w/Gem_rock?oldid=37044944
- Priest in Peril route source:
  https://runescape.wiki/w/Priest_in_Peril?oldid=6487728
- The Fremennik Isles route source:
  https://runescape.wiki/w/The_Fremennik_Isles?oldid=6540919

## Candidate Route Gates, Not Global Target Gates Yet

These need a location/source/acquisition model before they should be copied into
normal skill locks.

| Quest or unlock | Current content | Current verdict | Reason |
| --- | --- | --- | --- |
| Karamja Diary / Shilo Village | Extra gem mine or diary access | Future route gate | Karamja hard diary grants underground gem mine access, but AnkiScape has no diary or location model. |
| What Lies Below | Chaos altar safe tunnel | Route shortcut only | The 2011 KB describes a safe route, not chaos rune creation itself. Do not gate `craft_chaos_runes`. |

Source links:

- Shilo Village mining site:
  https://runescape.fandom.com/wiki/Shilo_Village_mining_site
- Karamja task requirements:
  https://www.2011.rs/kb/karamja

## Quest-Related Content That Should Stay Ungated Now

| Quest | Current content | Verdict |
| --- | --- | --- |
| Cook's Assistant | Cooking targets | Do not global-gate. Local source only blocks Lumbridge cook's range object `114`; AnkiScape does not model range locations. |
| Doric's Quest | Smithing targets | Do not global-gate. Local source only blocks Doric's anvil object; other anvils remain usable. |
| Druidic Ritual | Current Cooking meat rows; future Herblore | Do not gate current Cooking. The true unlock is Herblore, which is not implemented. |
| The Knight's Sword | Smithing | Do not gate. The quest awards Smithing XP and has quest interactions around blurite, but no current global Smithing target unlock was identified. |
| Fishing Contest | Fishing | Do not gate. It is a transport/shortcut quest, not a current Fishing target unlock. |
| Tai Bwo Wannai Trio | Cooking karambwan | Not implemented as a Cooking target today. If `cook_karambwan` is added later, decide whether to use completion-only or stage-aware gating. |
| Tai Bwo Wannai Trio / Barbarian Training | Poisoned spears, hastae, karambwan poison | Not implemented in Smithing/Cooking/Fishing today. Re-audit when those rows land. |
| Dorgesh-Kaan/lightorbs | Firemaking repair XP | Not implemented. This is an extra feature, not current Firemaking v1. |
| Druidic Ritual stone fish | Fishing | Not implemented. `memory-bank/source-audits/fishing-2011scape-2026-06-16.md` already records Stone fish as quest-only future content. |

Local source evidence:

- `raw_food_cooking.plugin.kts:120-123` blocks only Lumbridge cook's range
  object when Cook's Assistant is incomplete.
- `smithing.plugin.kts:43-51` and `smithing.plugin.kts:74-80` special-case only
  Doric's anvil.
- `DruidicRitual.kt:11-23` describes the Herblore unlock and 250 Herblore XP
  reward; Herblore is outside the implemented skill set.

## Backend Migration Pattern To Pilot

Do this backend-first when implementing the quest locks:

1. Add missing quest definitions to `quest_data.py` with stable snake-case IDs.
2. Add a small quest-lock registry, not scattered inline checks. Suggested
   shape:

   ```python
   QuestUnlockRule(
       quest_id="lost_city",
       gate_kind="target",
       skill_id="runecrafting",
       target_ids=("craft_cosmic_runes", "bind_cosmic_tiara", "feed_cosmic_talisman_to_hood", "feed_cosmic_tiara_to_hood"),
       reason="Lost City",
       source="https://www.2011.rs/kb/runecrafting_the_basics",
   )
   ```

3. Feed that registry into pure locked-reason functions for completion gates.
4. Keep route gates out of target locks until a route/location/acquisition model
   exists, except when the current generic target effectively represents that
   locked region route and the logical quest precedent is the least misleading
   gate.
5. Keep quest-stage recipes out of completion locks until stage-aware quest
   checks are intentionally supported.
6. Add undo-safe tests for the blocked and newly-unblocked paths before touching
   Qt.

## Frontend Migration Pattern To Pilot

After backend lock reasons exist:

1. Surface quest lock reasons through the same target-row metadata path used for
   levels/materials.
2. Show quest names as lock reasons, not generic "quest".
3. For grouped Runecrafting targets, make sure standard runes, tiara binding,
   and hood feeding each show the correct quest lock independently.
4. Do not invent new UI state for unresolved route gates; when a route precedent
   is promoted into `QUEST_UNLOCK_RULES`, surface it through the same disabled
   row and concise tooltip contract as other quest locks.

## Copy-Paste Prompt For A Future Quest-Lock Skill

```text
Create a Codex skill for AnkiScape quest-lock migrations. Read
memory-bank/quest-unlock-audit-2026-06-17.md first. The skill must split backend
and frontend work, add or correct quest definitions in the generator/override
layer before gates, separate completion unlock rules from route/location gates
and quest-stage recipes, allow flattened logical precedents only when the current
generic row effectively represents the locked route, reuse `quest_completed_pure`
for completion gates,
preserve strict quest starts for unimplemented skills, route generated XP lamps
through Bank Claims, update target-row lock reasons only after pure backend
logic exists, add targeted unit/integration/Qt coverage, run the AnkiScape test
pair, update the Memory Bank, and commit.
```

## Resolved Design Decisions From This Pass

1. Quest-lock rules live centrally in `quest_data.py` via `QUEST_UNLOCK_RULES`.
2. Partial quest unlocks use completion-only locks until stage-aware quest state
   exists.
3. `gem_rocks` is globally Shilo Village-gated until AnkiScape can model
   mining routes/locations.
4. Location requirements can be flattened to logical quest precedents when the
   current generic target effectively represents the locked route: Morytania rows
   use Priest in Peril and Neitiznot/yak/arctic pine rows use The Fremennik Isles.
5. Direct quest reward items and XP lamps are part of the generated reward
   surface, not a later hand-authored LLM migration.
6. XP lamps use one flattened Bank Claim interface with preserved skill options
   and level requirements.
7. Every generated quest row should have a source-backed journal/checklist stage
   surface. Generated placeholder journals are a regression.
