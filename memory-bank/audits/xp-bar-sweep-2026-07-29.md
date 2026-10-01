# Reviewer XP-bar verification sweep — 2026-07-29

Repository inspected read-only: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`

## Result

- Concrete reviewer activity targets checked: **58**.
- Correct: **30**.
- Documented deliberate no-bar: **22** (**17** XP-bearing combat targets + **5** payout/action-choice families).
- Defective mappings: **6** activity IDs.
- Inverse defects (bar shown for a skill the reducer never grants): **0**.

The 58-target registry universe is 51 `UTILITY_ACTIVITY_DATA` rows classified onto the Activities surface, the unregistered Evil Tree world event, three injected landmarks, and three conditional Mage Arena attunement targets. `shattered_heart` is included because it is registered, but is passive-only and cannot become the running `current_utility`. The pure probe drove the real strip logic for every applicable target, used landmark precedence, and spawned the three world-clock events with their real reducers.

## Defects

| Registry id | Reducer grants | Strip exposes | Omission | Minimal fix location |
|---|---|---|---|---|
| `livid_farm` | Magic, Farming, Construction, Crafting, Agility | Magic | Farming, Construction, Crafting, Agility | Expand the existing tuple at `logic/review_strip_logic.py:253`; source set is `logic/livid_farm_logic.py:199-205` and `data/livid_farm_data.py:30-88`. |
| `mage_training_arena` | Magic | No XP bar | Magic | Add exact-ID entry in `ACTIVITY_TRAINED_SKILLS` at `logic/review_strip_logic.py:237-254` (and its data-ID import near `:34-47`); reducer writes Magic XP at `logic/mage_training_arena_logic.py:604-687`. |
| `warriors_guild_attack_dummy` | Attack | No XP bar | Attack | Add exact-ID entry in `ACTIVITY_TRAINED_SKILLS` at `logic/review_strip_logic.py:237-254`; award is `logic/warriors_guild_logic.py:262-264`. |
| `warriors_guild_catapult` | Defence | No XP bar | Defence | Add exact-ID entry in `ACTIVITY_TRAINED_SKILLS` at `logic/review_strip_logic.py:237-254`; award is `logic/warriors_guild_logic.py:265-267`. Also fix Defence storage-key lookup at `logic/review_strip_logic.py:211-212` before exposing this bar. |
| `warriors_guild_shot_put` | Strength | No XP bar | Strength | Add exact-ID entry in `ACTIVITY_TRAINED_SKILLS` at `logic/review_strip_logic.py:237-254`; award is `logic/warriors_guild_logic.py:201-215,268-269`. |
| `warriors_guild_keg_balance` | Strength | No XP bar | Strength | Add exact-ID entry in `ACTIVITY_TRAINED_SKILLS` at `logic/review_strip_logic.py:237-254`; award is `logic/warriors_guild_logic.py:270-277`. |

## Deliberate no-bar set

The source contract is `logic/review_strip_logic.py:227-236`. These are excluded from the defect count even though their reducers can grant XP.

### XP-bearing combat targets (17)

`barbarian_assault`, `barrows`, `castle_wars`, `clan_wars`, `crucible`, `dominion_tower`, `fight_caves`, `fist_of_guthix`, `goblin_raids`, `knight_waves`, `pest_control`, `phoenix_lair`, `skeletal_horror`, `soul_wars`, `temple_trekking`, `tzhaar_fight_pit`, `warriors_guild_animated_armour`.

### Five payout/action-choice families

`big_top_bonanza`, `court_cases`, `shades_of_mortton`, `troll_invasion`, `trouble_brewing`.

`duel_arena` and `mage_arena` are combat-flavoured targets but their running reducers grant no skill XP, so the matrix counts them as ordinary correct empty rows rather than exceptions. `stealing_creation` likewise grants no skill XP during the game; its clay tools modify later skilling XP.

## Full matrix

`Strip exposes` describes the real reviewer branch: landmark targets show their finite step bar instead of calling the XP renderer; the other foreground Activity targets use `activity_xp_bars_pure`. `Reducer grants` is limited to XP awarded by the running/review reducer. Post-run direct claims (Penguin points, Stronghold lamps, Varrock Museum claims, Flash Powder redemption, Shattered Heart pair placement, Dominion reward books) are not treated as running XP. The skill-owned `dungeoneering` and Agility `the_pit` loops were inspected but are outside this registry matrix because they render through their ordinary skill HUD branches rather than the Activity/Utility strip mapping.

### activities: conditional Mage Arena attunements

| Registry id | Strip exposes | Running/review reducer grants | Verdict | Evidence |
|---|---|---|---|---|
| `mage_arena_attune:guthix` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `mage_arena_attune:saradomin` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `mage_arena_attune:zamorak` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |

### activities: distractions_and_diversions

| Registry id | Strip exposes | Running/review reducer grants | Verdict | Evidence |
|---|---|---|---|---|
| `big_chinchompa` | Hunter | Hunter | Correct | `runtime/runtime_actions_activities.py:739-783` |
| `big_top_bonanza` | No XP bar | Magic/Ranged/Agility/Firemaking/Thieving, selected performance only | Deliberate no-bar: payout/action choice | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `court_cases` | No XP bar | Attack or Defence, selected by court role | Deliberate no-bar: payout/action choice | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `enchanted_key` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `familiarisation` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `fish_flingers` | Fishing | Fishing | Correct | `runtime/runtime_actions_activities.py:1573-1613` |
| `goblin_raids` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `penguin_hide_and_seek` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `phoenix_lair` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains; Firemaking + Fletching + Crafting + Slayer on completion | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `shattered_heart` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `shooting_stars` | Mining | Mining | Correct | `runtime/runtime_actions_activities.py:786-888` |
| `skeletal_horror` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains; Slayer + Prayer on completion | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `tears_of_guthix` | One dynamic least-XP trainable skill (probe: Agility) | One dynamic least-XP trainable skill | Correct | `runtime/runtime_actions_activities_distractions.py:347-392` |
| `treasure_trail` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `troll_invasion` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains; Construction/Crafting/Firemaking in repair mode; chosen trainable skill at payout | Deliberate no-bar: payout/action choice | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |

### activities: distractions_and_diversions (unregistered world event)

| Registry id | Strip exposes | Running/review reducer grants | Verdict | Evidence |
|---|---|---|---|---|
| `evil_tree` | Woodcutting at entry/prepare; Woodcutting + Firemaking in fell; Farming when phase is nurture | Farming (nurture); Woodcutting (prepare); Woodcutting + Firemaking (fell) | Correct | `runtime/runtime_actions_activities.py:636-736` |

### activities: injected landmark targets

| Registry id | Strip exposes | Running/review reducer grants | Verdict | Evidence |
|---|---|---|---|---|
| `knight_waves` | No XP bar; finite landmark progress bar instead | Attack + Strength + Defence + Constitution on completion | Deliberate no-bar: combat | `logic_pure/logic_pure_landmarks.py:199-215` |
| `mage_arena` | No XP bar; finite landmark progress bar instead | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `stronghold_of_security` | No XP bar; finite landmark progress bar instead | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |

### activities: landmarks

| Registry id | Strip exposes | Running/review reducer grants | Verdict | Evidence |
|---|---|---|---|---|
| `managing_miscellania` | Woodcutting | Woodcutting | Correct | `runtime/runtime_actions_activities_distractions.py:704-734` |
| `stronghold_player_safety` | No XP bar; finite landmark progress bar instead | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `varrock_museum` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |

### activities: minigames

| Registry id | Strip exposes | Running/review reducer grants | Verdict | Evidence |
|---|---|---|---|---|
| `barbarian_assault` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `barrows` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `castle_wars` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `clan_wars` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `crucible` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `dominion_tower` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `duel_arena` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `fight_caves` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `fishing_trawler` | Fishing | Fishing | Correct | `runtime/runtime_actions_activities_training.py:456-496` |
| `fist_of_guthix` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `flash_powder_factory` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `gnome_ball` | Agility + Ranged | Agility + Ranged | Correct | `runtime/runtime_actions_activities_training.py:363-408` |
| `gnome_restaurant` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `great_orb_project` | Runecrafting | Runecrafting | Correct | `runtime/runtime_actions_activities_training.py:499-543` |
| `livid_farm` | Magic | Magic + Farming + Construction + Crafting + Agility | DEFECT | `logic/livid_farm_logic.py:199-205; data/livid_farm_data.py:30-88` |
| `mage_training_arena` | No XP bar | Magic | DEFECT | `logic/mage_training_arena_logic.py:604-687` |
| `mobilising_armies` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `pest_control` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `pyramid_plunder` | Thieving + Strength + Runecrafting (also-trains caption) | Thieving + Strength + Runecrafting | Correct | `runtime/runtime_actions_activities_training.py:282-327` |
| `shades_of_mortton` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains; Crafting + Firemaking + Prayer, action dependent | Deliberate no-bar: payout/action choice | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `sorceress_garden` | Farming + Thieving | Farming + Thieving | Correct | `runtime/runtime_actions_activities_distractions.py:430-475` |
| `soul_wars` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `stealing_creation` | No XP bar | No XP from the running/review reducer | Correct | `Family review/command reducer grants no XP while running` |
| `temple_trekking` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains on combat encounters | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `trouble_brewing` | No XP bar | Agility + Cooking + Crafting + Firemaking + Woodcutting, duty dependent | Deliberate no-bar: payout/action choice | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `tzhaar_fight_pit` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style; Prayer can be added by enabled kill effects where the encounter yields eligible remains | Deliberate no-bar: combat | `runtime/runtime_actions_activities.py:891-2688 (family handler); family logic reducer` |
| `vinesweeper` | Hunter | Hunter | Correct | `runtime/runtime_actions_activities_distractions.py:503-544` |
| `werewolf_skullball` | Agility | Agility | Correct | `runtime/runtime_actions_activities_training.py:330-360` |

### activities: warriors_guild

| Registry id | Strip exposes | Running/review reducer grants | Verdict | Evidence |
|---|---|---|---|---|
| `warriors_guild_animated_armour` | No XP bar | Attack/Strength/Defence/Ranged/Magic + Constitution, selected by attack style | Deliberate no-bar: combat | `logic/warriors_guild_logic.py:182-198,249-255` |
| `warriors_guild_attack_dummy` | No XP bar | Attack | DEFECT | `logic/warriors_guild_logic.py:262-264` |
| `warriors_guild_catapult` | No XP bar | Defence | DEFECT | `logic/warriors_guild_logic.py:265-267` |
| `warriors_guild_keg_balance` | No XP bar | Strength | DEFECT | `logic/warriors_guild_logic.py:270-277` |
| `warriors_guild_shot_put` | No XP bar | Strength | DEFECT | `logic/warriors_guild_logic.py:201-215,268-269` |

## Adjacent finding not counted in the six mapping defects

`skill_xp_bar_pure` derives save keys by lowercasing the display name at `logic/review_strip_logic.py:211-212`. `Defence` therefore reads `defence_level` / `defence_exp`, but canonical storage is `defense_level` / `defense_exp` (`core/skill_registry.py:315,380-384`). This already misreads Tears of Guthix whenever Defence is the least-XP skill, and it must be corrected before adding the Warriors' Guild catapult Defence bar.

## Verification notes

- Pure enumeration/probe artifacts: `activity_registry_dump.json`, `live_strip_probe.json`, and `defect_reducer_probe.json` in this scratchpad.
- The real reducer probe returned Livid Farm keys `agility`, `construction`, `crafting`, `farming`, `magic`; Mage Training Arena returned 301 Magic XP at its first XP-bearing checkpoint; and the four noncombat Warriors' Guild activities returned Attack, Defence, Strength, and Strength respectively.
- World-event probes produced Big Chinchompa → Hunter and Shooting Stars → Mining. Evil Tree produced Woodcutting at entry/prepare and Woodcutting + Firemaking in fell; the dynamic adapter also maps an explicit nurture phase to Farming (`logic/review_strip_logic.py:408-419`).
- Pyramid Plunder produced two visible bars (Thieving, Strength) plus Runecrafting in `also_trains`, matching the two-bar cap.
- No repository file was edited and no git command was run.
