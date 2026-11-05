# Pass 21 research facts

OBSERVED — Research revision: `cac609d0c45989210b88c9a60fdeeaa802e13369` on `main`. Repository status was empty before research and at report time. All scripts, downloaded source text, synthetic-save exports, logs and captures are in `/Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts`. No repository changes, worktrees, commits or pushes were made. No Anki process was started, profile database opened or owner save read. MacBook access was limited to reading loop item 7330 over SSH.

READ — `READ` marks source inspection or a proposed fix; `OBSERVED` marks execution. A passing synthetic probe does not establish what happened in the owner's running Anki session. In particular, the exact missing-arrow incident remains unproven. Probe scripts import `pkg_alias` before `ankiscape.*`; runtime proofs use the real `on_answer_card` and `_spend_card_on_action` through the repository's fake collection/reviewer harness. Widget proofs use real PyQt6 widgets, `QTest` clicks, `QT_QPA_PLATFORM=offscreen`, a shown dialog resized to 900 × 560 and event processing. RNG is held at `0.5` for deterministic item-path tests. All Python probe invocations set `PYTHONDONTWRITEBYTECODE=1`.

READ — Reproduce a probe with this full command, substituting only the script filename from the linked evidence:

```sh
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen "/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.venv-qt/bin/python" "/Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/widgets_probe.py"
```

READ — Raw evidence is retained alongside this report. The external [friction.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/friction.log>) records probe setup errors; corrected scripts were rerun. No papercut entry was written into the read-only repository.

## 1. Why can't I go to the sawmill to make my own planks?

READ — **Cause:** the sawmill conversion already exists under **Utilities → Material processing**, with four rows named “Convert … logs to … planks”; no row is named “Sawmill”, and the Utilities search does not search their source/NPC. The normal/oak rows identify Darkan's SawmillOperator in source metadata, not visible UI. Definitions: [core/constants_parts/activity_updates.py:60](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/constants_parts/activity_updates.py:60>). Search ranks names and groups: [ui/ui_utility_activity_list.py:162](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_utility_activity_list.py:162>). A literal search for the expected NPC/action name fails.

OBSERVED — Real Utility tree output from [planks_probe.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/planks_probe.py>) / [planks_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/planks_probe.log>):

```text
UTILITY_SEARCH {"query": "sawmill", "rows": ["No utilities match this search."]}
UTILITY_SEARCH {"query": "plank", "rows": ["Convert logs to planks", "Convert oak logs to oak planks", "Convert teak logs to teak planks", "Convert mahogany logs to mahogany planks"]}
```

OBSERVED — Complete current item-registry plank census, from [catalog_probe.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/catalog_probe.py>) / [catalog_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/catalog_probe.log>):

```text
PLANK_ITEMS ["Mahogany plank", "Oak plank", "Plank", "Teak plank"]
SAWMILL_NAMED_ACTIONS []
PLANK_SHOP_SERVICES []
```

READ — **Existing ordinary plank types and period fees:** one matching log plus the fee makes one plank. All four data rows already match these fees.

| Item | Log | Coins per plank |
|---|---|---:|
| Plank | Logs | 100 |
| Oak plank | Oak logs | 250 |
| Teak plank | Teak logs | 500 |
| Mahogany plank | Mahogany logs | 1,500 |

READ — Exact period source: [Bill / Sawmill operator, oldid 6446924](https://runescape.wiki/w/Bill?oldid=6446924), revision timestamp `2012-10-20T12:29:42Z`; the “Planks” table gives all four fees. NPC: **Bill, the Sawmill operator**, along the southern wall of Varrock's Lumber Yard. The same revision distinguishes his service from the separate nearby Sawmill training activity. Exact API payload and wikitext: [period-Bill.json](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/period-Bill.json>), [period-Bill.txt](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/period-Bill.txt>). The historical page lives under `Bill`; cutoff queries for the current `Sawmill` and `Sawmill operator` pages returned no historical revision. Discovery and fetch commands are in [fetch_period.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/fetch_period.py>) / [fetch_period.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/fetch_period.log>); curl uses retries.

OBSERVED — [planks_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/planks_probe.log>) contains four `PLANK_REVIEW` lines: each real review consumes the exact one-log fee fixture, produces one corresponding plank and reports `"errors": []`. A stocked conversion row also takes one click while another Utility queue entry runs:

```text
UTILITY_STOCKED_SINGLE {"disabled": false, "record": {"kind": "utility", "utility_id": "convert_logs_to_planks"}, "saved": "pick_onions"}
```

READ — Existing consumers include Construction's Crude wooden chair (`Plank: 2`, `Nails: 2`) and Oak chair (`Oak plank: 2`), in [data/construction_data.py:21](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/construction_data.py:21>); Dragon Slayer explicitly consumes three Planks to repair the ship, [data/quest/definitions/free/dragon_slayer.py:307](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/quest/definitions/free/dragon_slayer.py:307>). Observatory Quest, In Search of the Myreque and Cold War also contain plank requirements; their presence is printed by the probe. Quest supply recipes already include taking a plank on Entrana, [data/quest/ledger.py:149](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/quest/ledger.py:149>). Magic already has the separate Lunar Plank Make recipes and discounted fees, [data/magic_data.py:432](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/magic_data.py:432>). No new plank item or conversion engine is needed.

READ — **Smallest fix:** make the existing conversions discoverable as Sawmill/Bill (a label or search terms on existing rows), retaining the paid review-paced conversion. If choosing search aliases, extend the Utilities matcher to consume row search terms; adding metadata alone would do nothing. **Owner choice:** whether “Sawmill” should be the visible row name or a search alias; whether a distinct Sawmill training activity is wanted is a separate scope decision, not required to make planks.

## 2. Make the up and down buttons on the queue chevrons

READ — **Cause:** [ui/ui_action_queue.py:429](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_action_queue.py:429>) constructs `QPushButton("Up")` and `QPushButton("Down")`; `_move_button` uses the same word for displayed text, object name and accessible name at [ui/ui_action_queue.py:437](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_action_queue.py:437>). They are not icon/chevron controls.

OBSERVED — `QUEUE_CONTROLS` in [widgets_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/widgets_probe.log>) reports object names `actionQueueMoveUp` / `actionQueueMoveDown` and displayed text `Up` / `Down`; the first row's Up and last row's Down are disabled. The real button callbacks already send the correct zero-based positions.

READ — **Smallest fix:** keep the object names, tooltips/accessibility descriptions and callbacks; change only the displayed text to up/down chevrons (or set the native standard arrow icon). Do not derive object names from the new displayed symbol. **Owner choice:** glyph/icon appearance only; the requested direction and behavior are settled.

## 3. A new Shop query should scroll back to the top

READ — **Cause:** `shopSearchInput` rebuilds both result lists and the detail panel but never resets either list's scrollbar, [ui/ui_tab_shop.py:1781](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_tab_shop.py:1781>). The main `QListWidget` is `shopSelectionList`, [ui/ui_tab_shop.py:123](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_tab_shop.py:123>); `rewardShopTargetList` is the parallel reward list. Repopulation also restores a matching current shop selection, [ui/ui_tab_shop.py:1592](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_tab_shop.py:1592>), through [ui/ui_tab_shop_widgets.py:31](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_tab_shop_widgets.py:31>). Clearing/repopulating a QListWidget does not guarantee scroll position zero.

OBSERVED — Real shop-widget output, [shop_probe.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/shop_probe.py>) / [shop_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/shop_probe.log>):

```text
SHOP_SEARCH_BEFORE {"max": 72, "query": "rune", "rows": 80, "scroll": 72}
SHOP_SEARCH_AFTER {"max": 73, "query": "arrow", "rows": 80, "scroll": 72}
```

READ — **Smallest fix:** after the new-query rebuild and any selection restoration, explicitly scroll both result lists to the top. Scope this to a changed search query so a purchase/stock refresh can preserve its current position. **Owner choice:** none needed for the requested reset; “new query” currently means every `textChanged` keystroke, consistent with live filtering.

## 4. Purchase quantity should not carry over to a new item

READ — **Cause:** one `QSpinBox`, `shopCustomQuantitySpin`, is retained across items, [ui/ui_tab_shop.py:249](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_tab_shop.py:249>). `_select_stock_row` updates only the row ID, grid and preview, [ui/ui_tab_shop.py:913](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_tab_shop.py:913>). Selecting a search-result stock row also replaces shop/row IDs without resetting quantity, [ui/ui_tab_shop.py:1734](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_tab_shop.py:1734>). `_refresh_transaction_panel` reads the existing spinner value.

OBSERVED — Real item change from Adamant arrows to Adamant arrowtips retains 50:

```text
SHOP_QTY_FIRST {"label": "Adamant arrows · Stock 0/0 · Buy 172 Coins", "qty": 50}
SHOP_QTY_SECOND {"label": "Adamant arrowtips · Stock 200/200 · Buy 160 Coins", "qty": 50}
```

READ — **Smallest fix:** reset the quantity to 1 when the purchase identity `(shop_id, row_id)` changes, through both tile and search-result selection paths. Keep a refresh of the same selected row from resetting the player's typed quantity. **Owner choice:** 1 is the existing initial quantity and smallest consistent default; a different default would require his choice.

## 5. One click on Unfired bowl should replace the old Sapphire Add target

READ — **Cause found on current main:** material-locked rows ignore the click, leaving Add on its previous target. A mandatory double-click policy was **not found**. The flat and grouped Skills selectors connect both `itemClicked` and `itemActivated` to the same selection handler, [ui/ui.py:5141](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:5141>), [ui/ui.py:5278](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:5278>). Both reject disabled rows first. Crafting computes `enabled=not locked_reasons`, including `materials`, [core/target_metadata.py:530](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/target_metadata.py:530>), [logic_pure/logic_pure_production.py:343](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_production.py:343>).

OBSERVED — Real shown Crafting tree, queue running Sapphire, both supplies stocked: one `QTest.mouseClick` changes Add to Bowl while leaving the running Sapphire target unchanged. Double-click then makes no further change. Removing Soft clay makes the bowl disabled and one click leaves Add on Sapphire:

```text
CRAFT_BEFORE {"count": 100, "header": "Currently training", "record": {"kind": "skill", "skill": "Crafting", "target": "cut_sapphire"}, "saved": "cut_sapphire"}
CRAFT_SINGLE {"count": 100, "disabled": false, "header": "Train this skill", "record": {"kind": "skill", "skill": "Crafting", "target": "form_bowl_unfired"}, "saved": "cut_sapphire"}
CRAFT_DOUBLE {"count": 100, "header": "Train this skill", "record": {"kind": "skill", "skill": "Crafting", "target": "form_bowl_unfired"}, "saved": "cut_sapphire"}
CRAFT_EMPTY_SINGLE {"count": 100, "disabled": true, "header": "Currently training", "record": {"kind": "skill", "skill": "Crafting", "target": "cut_sapphire"}, "saved": "cut_sapphire"}
```

READ — **Pass 20 ticket 03 hold path:** [memory-bank/specs/done/pass20-owner-notes/tickets/03-target-click-and-count.md:3](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/specs/done/pass20-owner-notes/tickets/03-target-click-and-count.md:3>) requires a click to select for Add while the queue runs this skill. `held_by_queue` stores `(apply, target)` and emits the refresh signal, [ui/ui_action_queue.py:254](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_action_queue.py:254>); `_build_target_selector` wraps the ordinary setter with it, [ui/ui.py:5308](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:5308>). The held target feeds `menu_action_record_pure`, [core/menu_action_queue.py:34](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/menu_action_queue.py:34>), and the header's Start applies it. This path works in the stocked probe. It is distinct from changing the running target immediately.

READ — **Utilities:** `_on_utility_clicked` also rejects disabled rows, [ui/ui.py:19282](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:19282>); its stocked hold path calls the same `held_by_queue`, [ui/ui.py:19218](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:19218>). A stocked plank conversion takes one click; an empty-input one leaves Add on Pick onions. Exact output is in [planks_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/planks_probe.log>) and [widgets_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/widgets_probe.log>). Utilities wires `itemClicked` and `itemActivated`, [ui/ui.py:19630](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:19630>). No double-click-only requirement was found there either.

READ — **Smallest fix:** implement the already-approved missing-material planning selection in note 10, while preserving the queue hold rule. Do not change click wiring merely to add another duplicate signal. **Owner choice / unresolved fact:** if the owner's bowl had Soft clay and its row was enabled, his exact single-versus-double failure is not reproduced at this revision. The stocked offscreen proof does not establish whether his running Anki had the same code or selection state.

## 6. Remove queued action 1 simply

READ — **Cause:** the missing button is deliberate in both layers. The queue projection sets `removable` false for an unpaused, unsuspended first row, [core/action_queue.py:228](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/action_queue.py:228>). The actual button exists (`actionQueueRemove`, “✕”) but `refresh` hides it when `removable` is false, [ui/ui_action_queue.py:420](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_action_queue.py:420>), [ui/ui_action_queue.py:465](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_action_queue.py:465>). The pure removal command independently refuses a running first entry, [core/action_queue.py:155](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/action_queue.py:155>). Showing the button alone would leave a nonworking control.

OBSERVED — The real single-entry queue reports `[["Remove entry 1", false], ["Remove entry 2", false], ["Remove entry 3", false], ["Remove entry 4", false], ["Remove entry 5", false]]` in the `removes` field of `QUEUE_CONTROLS`, [widgets_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/widgets_probe.log>). The running first row is also unremovable in the real backend; a separate pure command proof is in [queue_rules.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/queue_rules.log>).

READ — **Existing rules to preserve:** a stopped/finished entry leaves the queue and its successor starts; only an empty queue ends at Bankstanding. Manual **Stop** pauses the existing entry instead of deleting it. Reordering a running top entry starts its new successor immediately, preserving the old entry's remaining count. These rules are documented at [GLOSSARY.md:25](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/GLOSSARY.md:25>) and implemented by `pass_queue_entry_pure`, `_run_current_entry`, `_commit_run`, [core/action_queue.py:136](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/action_queue.py:136>), [core/action_queue.py:316](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/action_queue.py:316>), [core/action_queue.py:344](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/action_queue.py:344>).

READ — **Smallest fix:** allow first-row removal in projection and pure removal, then have the runtime removal command atomically stop the old entry and start the new top through the existing queue-start transaction. If there is no successor, stop at Bankstanding. Reset progress for the removed top; keep existing products/XP and never refund completed work. Paused/set-aside queues should keep their existing “change order/list only” behavior; do not interrupt a hand-started action. Preserve undo. **Owner choice:** none if removal is to follow the existing skip/advance rule; pausing the successor instead would be a new rule, not existing queue behavior.

## 7. More visual confirmation when a queue entry moves

READ — **Cause:** confirmation is wired only for Add. `MenuQueue.added` is emitted by `_confirm` after an accepted add, [ui/ui_action_queue.py:143](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_action_queue.py:143>); `ActionQueuePanel` connects only that signal to the fading row band, [ui/ui_action_queue.py:409](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_action_queue.py:409>). A successful move runs the backend and redraws, but does not signal a destination-row flash. The band already supports a 1,500 ms fade, [ui/ui_action_queue.py:318](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_action_queue.py:318>).

OBSERVED — After clicking a real move control, the widget reports:

```text
MOVE_FLASH {"band": false, "state": "State.Stopped"}
```

READ — **Smallest fix:** emit a move-confirmation signal carrying the destination index after a successful move and flash that row using the existing band, after the refresh has put it in its new place. A refused/boundary move must not flash. Keep Add confirmation separate so a move does not say “Added”. **Owner choice:** whether the existing 1.5-second band is enough, or a stronger/longer highlight is desired; the missing confirmation itself is established.

## 8. HUD says “Next: Combat” while a quest is selected next

READ — **Cause reproduced:** the HUD line is an event message, not a live “next queued entry” projection. `queue_notice_view_pure` reads the most recent queue event stamped with the current answered-review number and keeps it until the next answer, [core/action_queue.py:254](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/action_queue.py:254>). The completion/stop callback formats “Next” from the action that became current at that transition, [core/action_queue.py:275](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/action_queue.py:275>). The HUD displays this string directly in `world_notice_lbl`, [ui/ui.py:2517](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:2517>). A later menu move refreshes the HUD but does not invalidate/recompute the old notice.

OBSERVED — Real review-handler completion of Pirate's Treasure starts Combat, then the real move command puts Rune Mysteries first and starts it. The real ReviewHUD still says “Next: Combat”:

```text
HUD_BEFORE_MOVE {"active": "Combat", "notice": "Pirate's Treasure complete. Next: Combat.", "quest": "pirates_treasure", "queue": {"done": 0, "entries": [{"action": {"combat_action": "attack", "kind": "combat", "target": "cow"}, "count": 100}, {"action": {"kind": "quest", "quest_id": "rune_mysteries"}, "count": null}], "paused": false, "suspended": false}, "target": "Cow"}
HUD_AFTER_MOVE {"active": "Quests", "notice": "Pirate's Treasure complete. Next: Combat.", "quest": "rune_mysteries", "queue": {"done": 0, "entries": [{"action": {"kind": "quest", "quest_id": "rune_mysteries"}, "count": null}, {"action": {"combat_action": "attack", "kind": "combat", "target": "cow"}, "count": 100}], "paused": false, "suspended": false}, "target": "Rune Mysteries"}
QUEST_NAMES {"last_action": "Rune Mysteries", "queue_entry": "Rune Mysteries"}
```

OBSERVED — Script/log/capture: [hud_probe.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/hud_probe.py>), [hud_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/hud_probe.log>), [hud-stale.png](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/hud-stale.png>).

READ — **Where the quest name is lost:** no quest-name loss was found in the entry or name helpers. `last_action_name_pure` reads the quest's `display_name`, [core/last_action.py:94](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/last_action.py:94>), and `queue_entry_name_pure` retains it, [core/action_queue.py:214](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/action_queue.py:214>). The observed quest target label is “Rune Mysteries”. The mismatch is the retained prior successor string. This establishes one concrete path matching the visible symptom, not proof of the owner's exact sequence.

READ — **Smallest fix:** prevent a menu change of the current successor/action from leaving a stale “Next” suffix visible. Clear that transient HUD notice or regenerate its current-action portion from the new action while preserving the historical Event log. **Owner choice:** whether “Next” should mean “action that just started” (current implementation) or the still-waiting queue successor. If a persistent next-entry display is desired, it needs a separate live projection rather than repurposing a past event string.

## 9. Reach Strength 37, then Strength 35 achievements

READ — **Cause:** both are intentionally invented AnkiScape progression anchors, not real 2012 tasks. Falador Easy contains `falador_easy_reach_level_37_strength`, source ID `900101`, level-only condition Strength ≥37, `curation_anchor=True`, [data/achievement_diaries/falador.py:139](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/achievement_diaries/falador.py:139>). Fremennik Easy contains `fremennik_easy_reach_level_35_strength`, source ID `900201`, Strength ≥35, same flag, [data/achievement_diaries/fremennik.py:128](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/achievement_diaries/fremennik.py:128>). Each description explicitly says “An AnkiScape curation anchor, not a period task identity.”

OBSERVED — Executing the actual diary refresh on synthetic saves gives:

```text
DIARIES {"level": 34, "new": []}
DIARIES {"level": 35, "new": [["fremennik_easy_reach_level_35_strength", "Reach Level 35 Strength"]]}
DIARIES {"level": 37, "new": [["falador_easy_reach_level_37_strength", "Reach Level 37 Strength"]]}
DIARY_ORDER [["falador_easy_reach_level_37_strength", "Reach Level 37 Strength"], ["fremennik_easy_reach_level_35_strength", "Reach Level 35 Strength"]]
```

READ — **Why 37 can precede 35:** catalog traversal lists Falador before Fremennik, [data/achievement_diary_catalog.py:43](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/achievement_diary_catalog.py:43>); the refresh appends every newly satisfied row in that order, [logic/achievement_diary_logic.py:326](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/achievement_diary_logic.py:326>). If both were unrecorded when Strength is already 37, both fire together in that order. It is not a level decrease. At sequential checks of 35 then 37, the lower anchor fires first, as the probe shows. `check_achievements` sends all new diary rows, including anchors, to the popup list without excluding `curation_anchor`, [core/logic.py:145](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/logic.py:145>).

READ — **Period distinction:** [Falador achievements, oldid 6571459](https://runescape.wiki/w/Falador_achievements?oldid=6571459), timestamp `2012-11-18T05:31:03Z`, attaches Strength 37 to **Climbing the Walls**, grappling the north Falador wall, not merely reaching the level. [Fremennik achievements, oldid 6555812](https://runescape.wiki/w/Fremennik_achievements?oldid=6555812), timestamp `2012-11-14T23:17:11Z`, attaches Strength 35 to **Fish Fingers**, catching tuna bare-handed, alongside Fishing 55 and Barbarian Training. Exact period text is in [period-Falador_achievements.txt](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/period-Falador_achievements.txt>) and [period-Fremennik_achievements.txt](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/period-Fremennik_achievements.txt>). The live catalog separately retains those named deeds, with level access gates: [data/achievement_diaries/falador.py:187](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/achievement_diaries/falador.py:187>), [data/achievement_diaries/fremennik.py:364](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/achievement_diaries/fremennik.py:364>).

READ — **Smallest fix:** if the complaint is popup noise, omit anchor rows from the popup path while keeping saved completion and the existing tier contract. Removing them from diary tiers is a broader curated-design change. Sorting popups by level only hides the ordering oddity and keeps the invented feats. **Owner choice:** retain-but-silence, remove/replace anchors, or retain them visibly. Existing glossary/design explicitly authorize anchors, [GLOSSARY.md:5](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/GLOSSARY.md:5>); this research does not repeal that decision.

## 10. Earlier queued outputs should unlock planning a later action

READ — **Cause:** “can run now” is reused as “can select for Add”. Fletching's locked-reason helper checks actual `inventory`, not promised output, and returns `materials`, [logic_pure/logic_pure_production.py:415](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_production.py:415>). `fletching_target_rows` turns any lock into a disabled row, [core/target_metadata.py:878](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/target_metadata.py:878>), so the click never reaches the hold/Add path. The backend Add refusal itself does not reject a skill entry for missing materials, [core/action_queue.py:383](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/action_queue.py:383>). This is a UI planning lock, not a queue-runtime ban on future products.

OBSERVED — The actual row metadata and actual Add-default calculation disagree for Smithing 840 arrowtips ahead of Fletching, with 840 Headless arrows in Bank and zero arrowtips:

```text
PROMISED {"view": {"enabled": true, "has_count": true, "count": 840, "unit": "Bronze arrows", "materials": "Headless arrows: 840 in Bank \u00b7 Bronze arrowtips: 0 in Bank, 840 from entry 1", "count_tooltip": "Starts at your Bank plus earlier entries.", "tooltip": ""}, "row": {"enabled": false, "reasons": ["materials"]}}
```

READ — **Pass 20 already reads promised outputs for defaults:** `_queued_makes` reads earlier queued product counts minus current progress; `_supply_count` adds them to Bank; `action_supply_limit_pure` limits the recipe and `queue_add_view_pure` floors the default at 1, [core/menu_action_queue.py:140](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/menu_action_queue.py:140>), [core/menu_action_queue.py:160](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/menu_action_queue.py:160>), [core/menu_action_queue.py:200](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/menu_action_queue.py:200>). No new promised-output count subsystem is required. This is optimistic planning: it sums matching queued products; it is not a guaranteed future-stock simulation deducting all intervening consumption or proving each producer's inputs.

OBSERVED — MacBook read-only SSH found and read `/Users/armantarkhanian/.local/state/sol-loop/ankiscape/queue/7330-queue-plan-rows-without-input/brief.md`. Exact local copy: [loop-7330.txt](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/loop-7330.txt>). Its key text, word for word:

```text
Item: let a skill target row with no input be selected for planning a queue.
Player-visible goal: with an empty Bank, a player can click a later Herblore step and add it to the queue when an earlier entry produces its input.
Product change: a row whose only lock is missing materials takes the click, the Add record and the default count. "Train this skill" stays off until the input exists. Levels, quests and other locks still lock the row.
```

READ — **Overlap:** note 10 is directly inside item 7330, whose proof expressly extends to other skills with the same lock. Avoid a second independent Herblore/Fletching fix. Pass 20's run-record answer approves the click for planning, [memory-bank/specs/done/pass20-owner-notes/run-record.md:51](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/specs/done/pass20-owner-notes/run-record.md:51>).

OBSERVED — [locks_probe.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/locks_probe.py>) executes the real row builders with an empty inventory, level 99 and completed quests. Its complete census is in [locks_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/locks_probe.log>); the missing-input behavior is broader than Herblore:

| READ/OBSERVED — affected rows | Actual lock form / relevant source |
|---|---|
| Smithing, Crafting, Fletching, Herblore, Cooking, Firemaking | `materials`; row builders disable on any lock, [core/target_metadata.py:315](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/target_metadata.py:315>) (the six corresponding builders) |
| Fishing | missing bait → `materials`; [logic_pure/logic_pure_gathering.py:494](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_gathering.py:494>) |
| Hunter | consumables → `materials`; missing reusable tools remain separate locks; [logic_pure/logic_pure_gathering.py:678](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_gathering.py:678>) |
| Woodcutting processing (split Arctic pine logs) | `missing Arctic pine logs x1`; ordinary tree chopping has no product-input lock; [logic_pure/logic_pure_gathering.py:312](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_gathering.py:312>) |
| Prayer | named input lock such as `Bones x1`; [core/target_metadata.py:371](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/target_metadata.py:371>) |
| Runecrafting | `essence` / combination and binding inputs, with access locks separate; [core/target_metadata.py:1903](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/target_metadata.py:1903>) |
| Magic | named missing rune/item quantities such as `Fire rune x3`; [logic_pure/logic_pure_magic.py:289](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_magic.py:289>) |
| Construction | named plank/nail/etc. quantities, separate house/room/workbench/wage gates; [logic_pure/logic_pure_construction.py:60](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_construction.py:60>) |
| Summoning | `Missing Pouch, Spirit shards, Gold charm, Wolf bones`; [core/target_metadata.py:79](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/target_metadata.py:79>) |
| Utilities | `materials`, including plank conversion; [core/target_metadata.py:1685](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/target_metadata.py:1685>) |

READ — Mining, ordinary tree chopping and ordinary pickpocketing do not require previous recipe products; their tool/access/equipment gates should not be relaxed as material planning. Agility and Combat also have equipment/access/supply gates; this research does not treat those as interchangeable with a production-input lock. Farming and Slayer have different panels and are not in this shared target-row census. No examined input-lock helper consumes the queue's promised-output view.

READ — **Smallest fix:** distinguish planning-selectable from runnable for rows whose *only* blocker is consumable materials. Reuse the shared row contract's existing `navigation_enabled` distinction where appropriate, [core/target_row.py:8](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/target_row.py:8>), and route selected-but-unrunnable rows to Add only. Header Start must validate the selected target's real current inputs; `TrainButton` currently enables any non-null held pick, [ui/ui_action_queue.py:300](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui_action_queue.py:300>), so merely enabling the row would violate 7330. Preserve level, quest, tool, room, unlock and equipment gates. **Owner choice:** no fresh choice is needed for 7330's stated behavior. Extending the promise calculator into an exact net-material planner would be separate scope.

## 11. I created 840 bronze arrows and they are not in my Bank

OBSERVED — **No loss reproduced.** The exact cause of the owner's incident was **not found** on the researched revision. The requested item paths retain 840 in the shared inventory ledger, preserve them through JSON save/load, and the real Bank renders a visible Bronze arrows cell with quantity 840. Nothing in these runs moves the products into the ammunition slot, loaded ammunition, or an output-only carried store.

OBSERVED — **Executed matrix, all at configured 10x.** Queue case inputs: Fletching-only starts with 840 Headless arrows and 840 Bronze arrowtips. Chain starts with 56 Bronze bars, 840 Headless arrows and **zero** Bronze arrowtips; it queues Smithing arrowtips 840 → Fletching Bronze arrows 840. Real runtime, carried overlay, queue counting, storage migration and JSON reload run normally. Direct cases hand-start Fletching with no action queue.

| OBSERVED — path | Configuration | Explicit bank run variants | Cards to make 840 | Bank after reload |
|---|---|---|---:|---:|
| Fletching entry alone | Keep, Auto pack | none requested / immediate run after completion | 6 / 6 | 840 / 840 |
| Smithing → Fletching | Keep, Auto pack | none requested / immediate run after completion | 12 / 12 | 840 / 840 |
| Fletching entry alone | Custom carried pack, Keep | none requested / immediate run after completion | 6 / 6 | 840 / 840 |
| Smithing → Fletching | Custom carried pack, Keep | none requested / immediate run after completion | 12 / 12 | 840 / 840 |
| Fletching entry alone | Saved Drop flag control | none requested / immediate run after completion | 6 / 6 | 840 / 840 |
| Smithing → Fletching | Saved Drop flag control | none requested / immediate run after completion | 12 / 12 | 840 / 840 |
| Direct Fletching, no queue | Auto pack | none requested / requested after card 3 | 6 / 6 | 840 / 840 |
| Direct Fletching, no queue | Custom carried pack | none requested / requested after card 3 | 6 / 6 | 840 / 840 |

OBSERVED — The summary script rereads every completed case and asserts the holders and result counts; its exact output:

```text
MATRIX cases=16 bank_840=16 carried_empty=16 equipment_empty=16 ammo_empty=16 errors_empty=16
BEFORE_FIRST_BANK {"bank_arrows": 150, "card": 1, "carried": {"bronze_arrows": {"Bronze arrowtips": 690, "Headless arrows": 690}}, "first_bank_card": 2}
```

READ — **“No bank run” qualification:** the unmodified runtime requires automatic banking when pack churn reaches capacity; it has no full-batch no-banking option for processing. Thus “none” above means **no explicit/manual trip**, not suppression of mandatory runtime trips. The monitored direct no-request run scheduled three automatic Fletching trips at zero travel-review cost; the Smithing chain also scheduled its ordinary Smithing trip at cost 1. The first-card observation above is a true no-trip interval: 150 new arrows are already in the Bank ledger before the first bank trip on card 2. The full 840-from-zero batch with literally zero automatic bank transactions was **not executed**, because it would require bypassing the very queue/carried rules under test. Automatic trips are counted from the real `_initialize_due_bank_trip`, not inferred from popup text.

READ — **Mode meaning:** current skilling pack controls are Auto/Custom; the saved Keep/Drop flag is a gathering choice, not a different Fletching output holder, [ui/ui.py:22835](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:22835>), [ui/ui.py:23153](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:23153>). Processing forcibly keeps its outputs regardless of that flag, [runtime/runtime_actions_carried_overlay.py:832](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions_carried_overlay.py:832>). The Drop-flag cases are negative controls, not a claimed player-selectable Fletching Drop mode.

OBSERVED — **Actual Bank widget:** the chain's persisted synthetic save was opened in the real menu. Exact output and shown-widget capture:

```text
BANK_840 {"accessible": "Bronze arrows, quantity 840", "found": true, "quantity": 840, "visible": true}
```

OBSERVED — [bank-840.png](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/bank-840.png>) visibly shows Bronze arrows ×840 in the Fletched category and the selected item's quantity 840. A stale display was not reproduced in this fresh-menu case. No owner's Bank tab/filter state was inspected.

READ — **Item path:** [data/fletching_data.py:173](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/fletching_data.py:173>) defines each lot as 15 Headless arrows + 15 Bronze arrowtips → 15 Bronze arrows. `apply_fletching_pure` credits `new_inv["Bronze arrows"]`, [logic_pure/logic_pure_production.py:439](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_production.py:439>). The runtime installs that inventory before XP/achievement/save callbacks, [runtime/runtime_actions_production.py:572](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions_production.py:572>). The processing overlay caps inputs, then reconciles input consumption while preserving outputs and deferring saves until the real inventory has been restored, [runtime/runtime_actions_carried_overlay.py:186](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions_carried_overlay.py:186>), [runtime/runtime_actions_carried_overlay.py:224](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions_carried_overlay.py:224>), [runtime/runtime_actions_carried_overlay.py:561](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/runtime/runtime_actions_carried_overlay.py:561>). It does not auto-equip or auto-load the arrows. The carried pack contains recipe inputs while making arrows; these products go straight into the shared inventory ledger. The Bank renders that ledger, [ui/ui.py:23820](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:23820>), [ui/ui.py:24223](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/ui.py:24223>).

READ — **Can this be a display/holder issue?** It remains possible but unproven for the owner's session. A selected custom Bank tab can exclude an item assigned to the main tab: new stacks default to the main tab in [logic/bank_layout_logic.py:144](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/bank_layout_logic.py:144>), and `bank_sections_pure` filters by assigned tab, [logic/bank_layout_logic.py:352](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/bank_layout_logic.py:352>). Bank search can also filter a stack. Neither filter deletes items. Loaded combat ammunition has its own quantity store; the equipment ammunition slot itself is an item-name selection, not an 840-item quantity store. The matrix inspected both and found neither holding newly made arrows.

OBSERVED — **Can a save holding the arrows recover them?** The real migration and unloading paths were tested with synthetic JSON saves:

```text
RECOVERY {"ammo": {}, "bank": 840, "carried": {}, "kind": "bank"}
RECOVERY {"ammo": {}, "bank": 840, "carried": {}, "kind": "legacy_alias"}
RECOVERY {"ammo": {}, "bank": 0, "carried": {}, "kind": "carried_only"}
RECOVERY {"ammo": {}, "bank": 840, "carried": {"bronze_arrows": {"Bronze arrows": 840}}, "kind": "bank_and_carried"}
RECOVERY {"ammo": {}, "bank": 840, "carried": {}, "kind": "loaded_ammo"}
```

READ — A valid save containing `inventory["Bronze arrows"] = 840` reloads all 840; a legacy singular `Bronze arrow` key migrates to the plural key with 840 intact. A save holding 840 in `combat_supply_loadout.ammo` can return them to Bank through the existing unload action, [logic_pure/logic_pure_combat_engine.py:1928](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic_pure/logic_pure_combat_engine.py:1928>). A carried view is an overlay on the same ledger, not extra ownership: [logic/inventory_pure.py:704](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/inventory_pure.py:704>) clamps it to Bank on load. Therefore an **inconsistent** save with only carried 840 and Bank zero loses that orphan view during normal loading; the original file could still provide recovery evidence, but normal loading does not mint missing ledger items from it. No inspected normal production path created that inconsistent state.

READ — **Can arrows really be lost?** No silent loss bug was demonstrated in these paths. The runtime does have intentional individual-output replacement by Strange rocks, [logic/shattered_heart_logic.py:350](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/shattered_heart_logic.py:350>): without a carried collection bag, each awarded rock removes one eligible produced item. That is different from all 840 disappearing, and deterministic matrix rolls suppress that random branch. This is not a proof that every possible save/state/RNG combination is loss-free. If no durable holder contains the arrows, a display fix cannot recover them, and cumulative production counts alone do not establish current ownership after later spending.

READ — **Smallest fix:** no production or save-repair change is justified by the present evidence. If a future authorized synthetic reproduction finds arrows still in `inventory`, correct only the display/filter/holder path; if it finds inventory erased, fix that mutation and test save/undo before promotion. **Owner-only choice:** whether to authorize a separate examination of an exported affected save or compensate a confirmed missing stack. This task explicitly excluded his save, and no such examination or grant was performed.

READ — **Evidence and rerun scripts:** [arrows_probe.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/arrows_probe.py>) / [arrows_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/arrows_probe.log>) (12 queued cases), [arrows_direct.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/arrows_direct.py>) / [arrows_direct.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/arrows_direct.log>) (4 direct cases, per-card holder trace), [summarize.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/summarize.py>) / [arrow-summary.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/arrow-summary.log>), [arrow-summary.json](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/arrow-summary.json>), [recovery_probe.py](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/recovery_probe.py>) / [recovery_probe.log](</Users/ArmanTarkhanian1/Documents/ankiscape-pass21/facts/recovery_probe.log>). `arrows_*.json` files in the facts directory are synthetic post-run saves only.
