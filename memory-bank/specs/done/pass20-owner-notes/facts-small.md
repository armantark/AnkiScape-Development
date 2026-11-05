# Pass 20 fact-finding

OBSERVED — Investigated checkout `75f33bee9b91805555ebcaa16460635e4604d945`. Initial `git status --short` was empty. Probes used in-memory seed data and stubbed persistence callbacks. No Anki application, profile database or owner save was opened. Scratch files and downloaded sources are under `/tmp/pass20-facts/small/`; Python ran with `PYTHONDONTWRITEBYTECODE=1`, and Qt ran offscreen through `.venv-qt/bin/python`.

## 1. Jungle Potion

### Current behavior and cause

READ — Player stage 1 is the snake-weed objective. The six journal states are five herb objectives followed by completion (`data/quest/definitions/members/jungle_potion.py:10–20`). A started quest at saved progress 0 or 1 is on current stage 1 (`logic_pure/quest/journal.py:18–28`). A quest review searches; it does not clean. Only handing in the clean herb advances the objective.

OBSERVED — `/tmp/pass20-facts/small/probe.py` called the real `handle_quest_answer` with the quest started at progress 1, one `Grimy snake weed` in the bank (`inventory`), and zero `Clean snake weed`:

| Herblore | Druidic Ritual complete | Handler output |
|---|---|---|
| 3 | Yes | `True stage 1 grimy 2 clean 0` |
| 2 | Yes | `True stage 1 grimy 2 clean 0` |
| 3 | No, deliberately invalid started seed | `True stage 1 grimy 2 clean 0` |

OBSERVED — Each case recorded `errors: []` and `activity: ['Jungle Potion 1/6']`. Thus there is counter feedback, but no notice explaining that another card will keep searching and that the player must switch to Herblore. The first journal line does say “find, clean, and return”; the missing explanation is in review feedback, not the journal text.

READ — Each herb row consumes its clean item, produces its grimy item, and sets `repeatable_until_consumed=True` (`data/quest/definitions/members/jungle_potion.py:61–119`). The blocker code exempts missing consumed items on repeatable rows (`logic_pure/logic_pure_quest.py:531–545`). The producer adds another grimy herb whenever the clean item is missing, even if grimy stock already exists (`logic_pure/logic_pure_quest.py:895–919`), returns success without advancing (`logic_pure/logic_pure_quest.py:1205–1209`), and the ordinary announcement prints the same counter (`runtime/runtime_actions_quest.py:166–174`). This accounts for the observed stall without a blocking notice.

### All stages, authentic acquisition, and existing rows

READ — The following table combines the live stage requirements (`data/quest/definitions/members/jungle_potion.py:61–119`), cleaning targets (`data/herblore_data.py:152–156`), and search utilities (`data/herblore_data.py:537–580`). Each hand-in needs one clean herb.

| Player stage | Needed item | Where the 2012 walkthrough obtains its grimy herb | Existing cleaning row | Existing search Utility |
|---|---|---|---|---|
| 1 | Clean snake weed | Search marshy jungle vines south-west of Tai Bwo Wannai | `clean_snake_weed` | Search marshy jungle vines |
| 2 | Clean ardrigal | Search the north-east headland's palm trees | `clean_ardrigal` | Search jungle palm trees |
| 3 | Clean sito foil | Search scorched earth at the village's southern fire remains | `clean_sito_foil` | Search scorched earth |
| 4 | Clean volencia moss | Search rocks in the south-east mine | `clean_volencia_moss` | Search jungle mine rocks |
| 5 | Clean rogue's purse | Search fungus-covered walls in the northern cavern | `clean_rogues_purse` | Search fungus-covered cavern wall |
| 6 | None | Completion; no further herb | None | None |

READ — A directly retrieved period source, [Jungle Potion oldid 6555418](https://runescape.wiki/w/Jungle_Potion?oldid=6555418), supplies the ordered searches, cleaning, and return to Trufitus for every herb. The raw source is `/tmp/pass20-facts/small/jungle-6555418.txt:40–89`. It says later herbs cannot be collected before being requested, and specifically requires wall-collected rogue's purse. The live engine checks item identity, not the individual herb's acquisition origin.

READ — Darkan independently represents these as stages 1–5, completed stage 6; object IDs 2575, 2577, 2579, 2581 and 32106 yield grimy items 1525, 1527, 1529, 1531 and 1533. Hand-in consumes the corresponding clean item and advances. Source: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/junglepotion/JunglePotion.java:28–42`, `:71–120`, `:123–171`.

READ — All five searches and cleanings fit the supply-step definition: obtain a quest-needed item without initiating combat, then clean it for the sourced XP. The walkthrough describes environmental dangers; the current owner ruling excludes optional danger from quest supply steps (`memory-bank/grill-decisions-2026-10-28.md:41–67`). Existing search Utilities are the post-quest repeatable route: the real-handler test expects them to refuse before completion (`tests/test_runtime_actions.py:3517–3520`, `:3583` onward). They should not simply be called through that locked frontend during the quest.

### Requirements and XP

OBSERVED — `/tmp/pass20-facts/small/jungle_flow_probe.py` measured unstarted quest admission and cleaning eligibility:

| Seed | Jungle Potion can start | Snake-weed cleaning blockers |
|---|---|---|
| Herblore 3, Druidic Ritual complete | `True` | `()` |
| Herblore 2, Druidic Ritual complete | `False`, `('Herblore 3',)` | `('Herblore level 3',)` |
| Herblore 3, Druidic Ritual incomplete | `False`, `('Druidic Ritual',)` | `()` |
| Herblore 1, Druidic Ritual incomplete | `False`, both requirements named | `('Herblore level 3',)` |

READ — Ordinary overworld cleaning has no general Druidic Ritual requirement. Each jungle herb requires Herblore 3 and awards 2.5 XP (`data/herblore_data.py:135–156`; `logic_pure/logic_pure_production.py:476–505`). The real Herblore handler enforces its level (`runtime/runtime_actions_production.py:593–625`). Jungle Potion separately requires Druidic Ritual and Herblore 3 at admission (`data/quest/definitions/members/jungle_potion.py:30–49`). Already-started quests bypass those admission requirements (`logic_pure/quest/eligibility.py:56–64`), explaining the deliberately below-level started seed's continuing search loop.

READ — Darkan's cleaning implementation checks the herb's level and gives its listed XP, without a quest check: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/herblore/HerbCleaning.java:95–99`, `:139–157`. Darkan's Jungle Potion start checks both Druidic Ritual and level 3 at `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/TrufitusDialog.kt:1422`. The period walkthrough gives 2.5 XP per cleaning and 775 quest XP (`/tmp/pass20-facts/small/jungle-6555418.txt:53–94`).

### Action count and smallest candidate change

OBSERVED — The real-handler route completed in **15 successful review actions**: five quest searches, five Herblore cleanings, five quest hand-ins. Output: `FLOW 15 handler calls ... completed True xp 1037.5`, starting from 250 XP. This run used `.999` RNG draws to avoid strange-rock replacement (`/tmp/pass20-facts/small/jungle_flow_probe.py` and `.log`).

READ — Following that route manually requires **10 action switches**: Quest → Herblore → Quest for each of five herbs, plus five distinct cleaning-target selections and the initial quest activation. This counts action changes, not individual menu-navigation clicks. Repeated quest reviews while waiting can continue indefinitely, producing excess grimy herbs. These are concrete sources of the flow's friction; the owner's precise emotional reason is not independently observable. A bounded search did not find the exact phrase “REALLY ANNOYING” in the memory bank.

READ — Candidate change, not implemented: make each missing-herb chain choose search, cleaning, then hand-in automatically, skipping acquisition/cleaning when the relevant item is already held; name the missing level when cleaning cannot run. Keeping the owner's one-card-per-state-change rule gives **15 review actions and zero intervening manual action switches** from an empty-herb bank, rather than five combined cards. This future count is contract arithmetic, not an executed implementation. A seed already holding the first grimy herb would skip one search.

READ — This cannot be a data-only addition to the existing Goblin Diplomacy recipes. `QuestSupplyRecipe` names a Utility (`data/quest/contract.py:94–103`); core attaches `UTILITY_ACTIVITY_DATA` (`core/constants.py:43–49`); the supply executor mutates inventory through the no-XP Utility path (`logic_pure/quest/supply_steps.py:20–31`, `:92–95`; `logic_pure/production/utility_activity.py:84–87`). It currently neither invokes the Herblore handler nor awards its XP. Also, repeatable rows suppress the missing-clean-item blocker that the supply planner needs. The smallest coherent seam is quest review-step planning/execution plus the five stage definitions, reusing the existing Herblore recipe data and behavior for level, XP and output handling.

READ — Player-visible choice: whether automatic quest cleaning retains ordinary Herblore's strange-rock replacement behavior. The current path deliberately permits it, so a clean herb can become a rock and need another search/clean cycle (`runtime/runtime_actions_shared.py:567–591`; `memory-bank/source-audits/quest-jungle-potion-playable-2026-08-13.md:167–178`). The 15-action count excludes that event.

### Other quests with this kind of silent wait

OBSERVED — A bounded scan of composed `QUEST_DATA` found eight `repeatable_until_consumed` rows: Jungle Potion 1–5, Tribal Totem 3 and 5, and Hazeel Cult 3. Only Jungle Potion's five rows produce a different item from the missing consumed item (`/tmp/pass20-facts/small/catalog_probe.log`).

READ — Tribal Totem recreates its missing Address label or Totem, so its next review can consume the same item (`data/quest/stage_overrides/members/classic/tribal_totem.py:44–71`). Hazeel's row produces Carnillean armour but also declares a separate required action (`data/quest/stage_overrides/members/classic/hazeel_cult.py:76–85`). Neither establishes the same indefinite cleaning wait. No other quest with the same data pattern was found. This is a census of this repeatable-item mechanism, not proof that every custom quest controller always gives adequate feedback.

## 2. Adamant boots

### Current behavior and cause

OBSERVED — The item is partly implemented. `/tmp/pass20-facts/small/probe.log` and `/tmp/pass20-facts/small/catalog_probe.log` show:

| Boots | Equipment definition / Defence | Registered item, GE row, icon | Live drop targets |
|---|---|---|---|
| Bronze | Yes / 1 | Not found | Cave crawler |
| Iron | Yes / 1 | Not found | Cockatrice; Cave slime |
| Steel | Yes / 5 | All present | Pyrefiend; Harpie Bug Swarm |
| Black | Yes / 10 | All present | Bloodveld |
| Mithril | Yes / 20 | All present | Jelly |
| Adamant | Yes / 30 | Not found | Gargoyle |
| Rune | Yes / 40 | Not found | Nechryael |

OBSERVED — No Smithing target or NPC shop stock reference was found for any of these seven boot metals. The probe inspected the imported catalogs; it did not infer availability from search text alone. Only `steel_boots.png`, `black_boots.png` and `mithril_boots.png` were found among these seven names under `combatitems/`.

READ — Adamant equipment stats exist at `data/equipment_data.py:10364–10377`, including source item 4129. Gargoyle's live main table includes one Adamant boots drop at 1/128 (`data/combat/slayer/slayer_finishers.py:122–151`), and the target requires Slayer 75 (`:398–402`). Thus a drop route exists in the data even though the item is absent from the registry/GE/icon layer.

READ — Equipment metadata only enriches an item already present in the merged extra-item catalog; it does not register every equipment definition (`core/constants.py:326–341`). Steel, black and mithril have explicit combat-item registrations; Adamant does not (`data/combat/items.py`, e.g. Steel at `:455–464`; observed exact-name catalog scan). GE construction iterates registered `ITEM_DEFINITIONS`, then checks tradeability, exchangeability and price (`data/grand_exchange_data.py:42–70`). Adamant boots already have a cache value of 1920 and an exchangeable-name entry (`generated/item_values_generated.py:122`, `:11915`); registration is the missing GE admission layer.

### Period evidence

READ — Direct period page [Adamant boots oldid 6007790](https://runescape.wiki/w/Adamant_armoured_boots?oldid=6007790), timestamp **2012-07-28T12:28:54Z**, lists release **2005-01-26**, members-only, tradeable, Defence 30, and no store. It names drops from **Gargoyles, Mutated bloodvelds and Giant frogs**, plus player trading, and explicitly excludes skill manufacture. Therefore they existed before 2012-11-20 and should not be added to Smithing. Raw source and revision metadata: `/tmp/pass20-facts/small/adamant-boots-6007790.txt:2–29` and `/tmp/pass20-facts/small/adamant-boots-period.json`.

READ — The independently fetched [Gargoyle oldid 6579781](https://runescape.wiki/w/Gargoyle?oldid=6579781), dated 2012-11-19 in the repository's pinned audit, lists one Adamant boots as an uncommon drop (`/tmp/pass20-facts/small/gargoyle-6579781.txt:74`; pin in `memory-bank/source-audits/slayer-rockslug-gargoyle-combat-2026-07-17.md:9–15`). The live exact 1/128 rate is Darkan reconstruction; the period page gives qualitative rarity.

### Smallest candidate change and player-visible choice

READ — Candidate, not implemented: add the missing item registration and authenticated period icon mapping, retaining the existing equipment stats, exchangeable flag, value and drop route. The directly adjacent bronze, iron and rune boot gaps have the same shape. No new Smithing recipe or NPC seller is supported by the Adamant period page.

READ — Player-visible scope choice: expose the existing Gargoyle acquisition and GE purchase first, or also restore the period page's other two drop routes. No Mutated bloodveld or Giant frog target was found by the bounded combat-data search. Their absence is a separate acquisition gap, not a reason to invent a shop or Smithing route.

## 3. Double-click search boxes

### Current behavior and complete search-input inventory

OBSERVED — Offscreen `QTest.mouseDClick` on `Stolen Hearts and bat bones` selected only `'Stolen'` in both an ordinary `QLineEdit` and the actual `CatalogFilterBar.search_input` (`/tmp/pass20-facts/small/qt_probe.py` and `.log`).

READ — Every search input found below is a **QLineEdit**. Most are created centrally at `ui/ui.py:1577` inside `CatalogFilterBar`; the skill wrapper is `ui/ui_target_search.py:136–139`. The table gives each call site, including the two separate surfaces that share one Utilities/Activities object name.

| Search surface | Object name | Source call site |
|---|---|---|
| Mining | `miningTargetSearchInput` | `ui/ui.py:5394` |
| Woodcutting | `woodcuttingTargetSearchInput` | `ui/ui.py:5411` |
| Smithing | `smithingTargetSearchInput` | `ui/ui.py:5437` |
| Crafting | `craftingTargetSearchInput` | `ui/ui.py:5455` |
| Fletching | `fletchingTargetSearchInput` | `ui/ui.py:5473` |
| Herblore | `herbloreTargetSearchInput` | `ui/ui.py:5485` |
| Summoning | `summoningTargetSearchInput` | `ui/ui.py:5497` |
| Prayer | `prayerTargetSearchInput` | `ui/ui_prayer_panel.py:76` |
| Construction | `constructionTargetSearchInput` | `ui/ui.py:5620` |
| Magic | `magicTargetSearchInput` | `ui/ui.py:6601` |
| Firemaking | `firemakingTargetSearchInput` | `ui/ui.py:6621` |
| Fishing | `fishingTargetSearchInput` | `ui/ui.py:6636` |
| Hunter | `hunterTargetSearchInput` | `ui/ui.py:6725` |
| Cooking | `cookingTargetSearchInput` | `ui/ui.py:6768` |
| Runecrafting | `runecraftingTargetSearchInput` | `ui/ui.py:7025` |
| Thieving | `thievingTargetSearchInput` | `ui/ui.py:7079` |
| Agility | `agilityTargetSearchInput` | `ui/ui.py:7301` |
| Combat | `combatTargetSearchInput` | `ui/ui.py:7527` |
| Utilities | `utilityActivityTargetSearchInput` | `ui/ui_utility_activity_list.py:90–99`, `is_activities=False` |
| Activities | `utilityActivityTargetSearchInput` | Same, `is_activities=True` |
| Quests | `questSearchInput` | `ui/ui_tab_quests.py:180–184` |
| NPC/Reward shops | `shopSearchInput` | `ui/ui_tab_shop.py:80–85` |
| Grand Exchange | `geItemSearchInput` | `ui/ui.py:21558` |
| Achievements Cabinet | `cabinetSearch` | `ui/ui_tab_achievements.py:65–68` |
| Help | `helpSearch` | `ui/ui.py:1701–1705` |
| Bank | `bankSearchInput` | Direct QLineEdit, `ui/ui.py:23752–23755` |
| Collections, including Music/selected drop family | `collectionsSearch` | Direct QLineEdit, `ui/ui_tab_collections.py:121–125` |

READ — Magic also has an editable alchemy item chooser, `magicAlchemyItemCombo`, a QComboBox with an internal line editor (`ui/ui.py:6541–6544`). It is an item selector rather than a shared catalog filter and does not call `match_rank`; include its editor if the requested double-click preference covers editable choosers too.

READ — The other direct QLineEdit constructions found are the combat preset-name input (`ui/ui_combat_setup_panel.py:632`) and Skullball plan input (`ui/ui.py:12466`); neither is a search box.

### Cause, smallest candidate change, and choice

READ — `CatalogFilterBar` installs an event filter, but it handles only Escape (`ui/ui.py:1585`, `:1603–1613`); double-click uses Qt's ordinary word-selection behavior. Pass 16 shares the text matcher in `core/search_match.py`, not a special search-input subclass.

READ — Candidate, not implemented: define one search-specific QLineEdit subclass with a double-click override that selects all, use it in CatalogFilterBar, Bank and Collections. An event-filter change only in CatalogFilterBar would miss Bank and Collections. No single existing constructor covers every search box.

READ — Player-visible choice is already specified in the note: double-click selects the whole phrase, replacing word-only selection. Single-click placement and keyboard selection need no semantic change. A search-specific class keeps this preference scoped to searches.

## 4. GE claim moves the remaining offers

### Current behavior and cause

OBSERVED — `/tmp/pass20-facts/small/ge_probe.py` placed three offers using the real pure offer function, then seeded completed/partial fill states:

```text
before [(1, 'Logs', 'complete'), (2, 'Coal', 'complete'), (3, 'Iron ore', 'partial'), None, None, None]
claim completed 1 ... after [(2, 'Coal', 'complete'), (3, 'Iron ore', 'partial'), None, None, None, None]
claim partial 3 ... after [(1, 'Logs', 'complete'), (2, 'Coal', 'complete'), (3, 'Iron ore', 'partial'), None, None, None] remaining 3
```

OBSERVED — Collecting the first completed offer moves Coal from slot 2 to slot 1 and Iron ore from slot 3 to slot 2. Their relative order remains unchanged. Collecting two ready items from the still-active partial third offer preserves all slots and its three-unit remainder.

READ — There is no separate collection-item list here: offers live in compact `ge_player_orders`. Collection transfers their ready items/coins into inventory, zeros the collectible fields, then removes completed/cancelled offers (`logic/grand_exchange_logic.py:703–738`). The projection assigns orders to slots by current list index (`:1463–1472`). The UI uses those slots directly (`ui/ui.py:21894–21917`). No sorting is needed to cause the observed movement.

### Smallest candidate change and player-visible choice

READ — Candidate, not implemented: store a stable slot index with each offer, allocate a new offer to an empty index, preserve that field during normalization/edit/cancel, and project by that index. Collection then removes the claimed completed offer without changing any other offer's slot. The affected seams are order normalization (`logic/grand_exchange_logic.py:98` onward), placement (`:493–556`), collection (`:703–738`) and projection (`:1438–1482`). A UI-only cached position would not preserve slots when the menu is reopened.

READ — In the reproduction, **Coal must stay in slot 2, Iron ore in slot 3, and slot 1 becomes empty**. Player-visible choice: absolute six-slot stability versus merely preserving relative list order. The latter already holds. Which empty slot the next offer uses is another observable detail; choosing the first empty slot is a candidate, not measured current behavior with holes.

## 5. `bat` and `198/198`

### Reproduction: Quests versus Combat

OBSERVED — The stated quest-search failure did **not** reproduce in the real current Quests menu. It **did reproduce exactly in Combat**, which also has 198 displayed targets. The counts below came from actual offscreen menu widgets (`/tmp/pass20-facts/small/qt_probe.log`, `/tmp/pass20-facts/small/combat_search_probe.log`):

| Query | Quests | Combat |
|---|---|---|
| Empty | `198/198` | — |
| `bat` | `14/198` | `198/198` |
| `Bat` | `14/198` | `198/198` |
| `ba` | `55/198` | `198/198` |
| `bats` | `6/198` | `62/198` |
| `a` | `197/198` | Not measured |
| `an` | `155/198` | Not measured |
| `the` | `184/198` | Not measured |

READ — Quests searches its title, ID, start point, requirements and unlocks (`ui/ui_tab_quests.py:115–122`), runs filtering when text changes (`:553`), and calculates the label from the filtered rows (`:519–539`). The observed Quests label is not stale and filtering is not skipped. Broad short-word results there arise from substring matches in those metadata fields. A stale loaded application revision was not tested or established as the cause of the owner's report.

READ — Combat explicitly enables `match_tooltip=True` (`ui/ui.py:7527–7535`). That adds the full tooltip and target ID to searchable text (`ui/ui_target_search.py:63–70`). Every locked or unlocked tooltip starts with the monster's name and **“combat level”** (`core/target_metadata.py:1487–1490`, `:1629–1631`). The substring `bat` is inside `combat`, so every row legitimately passes the implemented rule. This is a reproducible cause of the exact `198/198` symptom; it does not establish which panel the owner was using.

OBSERVED — The Chicken tooltip began `Chicken · combat level 1\nState: Ready · risk: Safe`. Using the same Combat rows but omitting tooltip metadata changed `bat` from **198 matches to 2**: Giant bat and Guard (battleaxe). `ba` changed from 198 to 11; `bats` changed from 62 to 3 (`/tmp/pass20-facts/small/combat_search_probe.log`).

### Exact matching rule and retained Pass 16 behavior

READ — `core/search_match.py:29–44` case-folds the query, then ranks exact name, name prefix, name substring tokens, metadata substring tokens, and finally fuzzy tokens. The decisive rules are:

```python
if all(token in text for token in tokens):
    return 3
words = re.findall(r"[^\W_]+", text)
if all(token in text or (len(token) >= 4 and any(_fuzzy_token(token, word) for word in words)) for token in tokens):
    return 4
```

READ — The fuzzy predicate is exactly:

```python
letters = iter(word)
return all(char in letters for char in token) or _one_edit(token, word)
```

READ — Therefore `bat` cannot take the fuzzy branch at all: it is three characters. For four-or-more-character tokens, the subsequence stays within a single regex word; it does not skip across arbitrary words. The separate `token in text` substring branch can include all supplied metadata.

OBSERVED — `Stolen Hearts` still ranks first: its title receives rank 0; the ten other quest matches receive rank 3. `tara` still finds `Tiara` at rank 4, including the real Crafting row `silver_tiara`, and GE tiara entries (`/tmp/pass20-facts/small/probe.log`, `/tmp/pass20-facts/small/catalog_probe.log`, `/tmp/pass20-facts/small/search_catalogs.log`).

### Other searches using the matcher

OBSERVED — The following are measured `bat` results against real row builders and their selector matching rule, with a default seed. They are catalog matches, including locked rows, not claims that every matched action is currently available. Evidence: `/tmp/pass20-facts/small/search_catalogs.py` and `.log`.

| Skills search | Matches / rows | Examples |
|---|---|---|
| Mining | 0/20 | None |
| Woodcutting | 0/15 | None |
| Smithing | 6/168 | Six metal battleaxes |
| Crafting | 5/234 | Battlestaves |
| Fletching | 0/97 | None |
| Herblore | 2/119 | Combat potion; Combat mix |
| Summoning | 3/145 | Vampyre bat pouch; Fruit bat pouch; Ophidian incubation scroll |
| Prayer | 3/61 | Three Bat bones methods |
| Construction | 6/544 | Combat-room racks and rings |
| Magic | 0/117 | None |
| Firemaking | 0/13 | None |
| Fishing | 0/20 | None |
| Hunter | 0/74 | None |
| Cooking | 5/92 | Five battas |
| Runecrafting | 0/49 | None |
| Thieving | 0/38 | None |
| Agility | 0/14 | None |
| Combat | 198/198 | Universal “combat level” metadata |

OBSERVED — Other actual widgets/pure searches returned:

| Search | `bat` result and fixture scope |
|---|---|
| Utilities | `Showing 2/176`: the two Grind bat bones rows |
| Activities | `Showing 0/12` in the default Activities view |
| GE | 38 item rows with the real GE catalog in buy mode |
| NPC shops | 69 stock/service matches, including battleaxes, battas and bat-pouch exchanges |
| Reward shops | No reward shop matches |
| Bank | `Showing 2/5` in a bank seeded with Coins, Bat bones, Battlestaff, Logs and Bucket |
| Achievements Cabinet | `Showing 15/534` |
| Collections: Music | `Showing 3/880`: Battlefield, Combat Training Camp and Conquest-battle unlock labels |
| Collections: drop-target overview | Guard (battleaxe) and Giant bat |
| Collections: selected Giant bat family | No rows before a kill; Bat bones after one seeded kill |
| Collections: selected Gargoyle family | No rows before a kill; Steel battleaxe after one seeded kill |
| Help | 10/20 topics, including Combat and topics whose prose mentions combat |

OBSERVED — Widget evidence is in `/tmp/pass20-facts/small/qt_probe.log`, `/tmp/pass20-facts/small/combat_search_probe.log` and `/tmp/pass20-facts/small/utility_probe.log`. Pure catalog evidence is in `/tmp/pass20-facts/small/catalog_probe.log` and `/tmp/pass20-facts/small/search_catalogs.log`. The first menu fixture's GE projection was empty; its zero-result GE output was discarded in favor of the explicit real-catalog run, which returned 38.

READ — These consumers use the same matcher with different searchable fields: target selectors (`ui/ui_target_search.py:63–70`), Utilities/Activities (`ui/ui_utility_activity_list.py:575–598`), GE (`ui/ui.py:21799–21808`), Bank (`ui/ui.py:23959–23972`), shops (`logic/shop_logic.py:258`, `:288`), Cabinet (`logic/achievement_diary_logic.py:708`, `:734`), Music (`logic/music_log_logic.py:204`, `:218`), drop collections (`logic/collection_log_logic.py:95–128`), and Help (`core/help_system.py:266–287`).

### Smallest candidate change and player-visible choice

READ — Candidate, not implemented: omit Combat's full tooltip from filtering. The existing `match_tooltip` option makes this a small call-site change; the probe establishes its effect without changing the matcher or losing `tara` → `tiara`.

READ — Player-visible tradeoff: searching names/groups would stop finding monsters through observed/examined drop text and other tooltip details. If that discovery behavior is wanted, supply a deliberate set of searchable drop/weakness terms instead of the entire presentation tooltip, which also contains generic combat wording and source paths. A global change to the fuzzy matcher is unnecessary to fix the demonstrated three-character `bat` failure. A Quests-specific fix has no reproduced failure at this revision.

## Adjacent findings

- OBSERVED — Both Quests and Combat have 198 rows in the tested seed. The number alone cannot identify the panel.
- OBSERVED — With tooltip metadata omitted, `bats` still matches two Giant rat variants as well as Giant bat through the shared fuzzy rule (`/tmp/pass20-facts/small/combat_search_probe.log`).
- READ — Combat searches source paths and generic status prose because the full tooltip is searchable (`core/target_metadata.py:1629–1651`; `ui/ui_target_search.py:63–70`). This creates unrelated substring matches beyond `bat`.
- OBSERVED — Bronze, iron and rune boots share Adamant's missing item registration, GE entry and icon, despite existing equipment/drop data.
- READ — The period Adamant boots page gives two additional drop targets absent from the bounded current combat search; their exact missing acquisition routes remain separate from registration.
- READ — Automatic quest cleaning must retain the sourced level/XP behavior; the existing supply executor is inventory-only. Ordinary strange-rock substitution can extend Jungle Potion beyond the measured 15-action run.
- READ — Started quest states bypass admission gates. The seeded below-level Jungle Potion probe therefore kept searching instead of stopping; a new supply-cleaning step needs its own level stop.
- OBSERVED — This investigator wrote only scratch files. Unlike the initially clean tree, the final worktree contained memory-bank changes during the investigation; exact paths are recorded in `/tmp/pass20-facts/small/final-status.log`. Those files were not edited, staged or committed by this investigator. Final revision was `7873ba1901b45e3074c62ec87d4fbe2fb1a1c963`; the compared product/test directories had no diff against the requested `75f33bee9b91805555ebcaa16460635e4604d945` (`/tmp/pass20-facts/small/product-diff-paths.log`).
