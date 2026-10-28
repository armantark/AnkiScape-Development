# Pass 18 code facts

Read-only fact reports taken at main `d4f7164ac` on 2026-10-27 by three Opus 5.5 fact-finders (A: action queue, B: GE, bank grid and tab bar, C: dyes, Goblin Diplomacy and shops). Lines may have moved since. Scratch probes named below lived under `/tmp/pass18-probe-*` and are not kept. Native looks in real Anki: `/Users/armantarkhanian/Code/ankiscape-pass18/native/look-1/` (small seed) and `look-2/` (a copy of the owner's save), each with `verdict.json` and screenshots.

## Pass 18 code facts: the action queue

Source: `/Users/armantarkhanian/Code/AnkiScape`, branch `main` at `d4f7164ac`. All paths are relative to that checkout. "Probe" means a scratch script under `/tmp/pass18-probe-a/` that ran the real code; its output is in the same folder.

Owner notes in scope (`/Users/armantarkhanian/Code/ankiscape-pass18/facts/pass18-notes.txt:3,6,10`):

- "The action queue needs to just be fully expanded without a scroll bar. It's only 5. Also add better affordance when you do add to the queue"
- "The queue went and over did the actions: 30/3 goblin mail, 40/3 redberries, 280/28 onion. ..."
- "If you intentionally clear the queue it should take you back to bankstanding"

### 1. How an entry's amount becomes work, and where the overshoot comes from

### The chain, in order

| Step | Code | What it does |
|---|---|---|
| Amount stored | `core/action_queue.py:90-106` `add_queue_entry_pure` | Appends `{"action": record, "count": count}`. `count` is an `int >= 1`, or `None` for a quest. |
| Progress so far | `core/action_queue.py:60-61` `_empty_queue`, `:77-78` | The queue holds one `done` number for the current entry and `index` for which entry runs. |
| Unit of the count | `core/action_queue.py:149-157` `queue_entry_unit_pure` | `"items"` when the action has product items, `"uses"` for one used input (bones buried), `"kills"` for combat, `"reviews"` for other actions, `""` for a quest. |
| Product items | `core/action_products.py:33-50` `action_product_items_pure` | A utility's product is its `output_item` (`:35-38`). |
| One card's work | `__init__.py:5011-5027` `_spend_card_on_action` calls `runtime/runtime_actions_context.py:203-239` `spend_card_budget` | The loop runs one step per 6 ticks until the card's ticks are spent (`:218-226`). Before every step after the first it checks only `can_continue` (`:219-220`), which is "same action still selected and can start" (`__init__.py:5025-5026`). Nothing in the loop reads the queue. |
| Game speed | `logic/pace/short_timers.py:24-26` `card_ticks_pure` | One card buys `STEP_TICKS * speed` ticks (`STEP_TICKS` at `:18`). Each step costs `LIVE_COMBAT_TICKS_PER_REVIEW` (`runtime/runtime_actions_context.py:226`). So one card at 10x runs 10 steps. Speed comes from Anki config `ankiscape_review_action_multiplier` (`__init__.py:664-668`). |
| One gather step | `runtime/runtime_actions_utility.py:906-920` calls `logic_pure/logic_pure_production.py:397-433` `apply_utility_activity_pure` | One step makes one full batch: `batch_count = _max_batches_for_requirements(requirements, inventory, batch_size)` (`:413-414`), and output is `output_qty * batch_count` (`:431-432`). With no requirements, `batch_count = batch_size` (`:191-193`). |
| Progress added | `__init__.py:5148-5152` `_dispatch_review_answer` calls `core/action_queue.py:427-460` `advance_action_queue` **after the whole card** | Progress is the card's item gain of the product (`:160-175` `queue_entry_progress_pure`, items branch `:170-172`). |
| Stop condition | `core/action_queue.py:118-126` `advance_queue_pure` | `done = done + progress`; if `done < count` the entry continues, else the entry passes with its full `done` kept (`:112` writes `done` into the entry). Nothing subtracts or limits the excess. |

The queue counts **items** for these three actions (the product, `output_item`). It does not count cards or steps. The check runs **once per card, after the card**, and a card at 10x runs 10 full batches first.

### The owner's three numbers

Batch sizes are in `core/constants_parts/activity_updates.py`:

| Owner note | Action (utility id) | `batch_size` | One card at 10x | Panel text (probe) |
|---|---|---|---|---|
| 30/3 goblin mail | "Search Goblin Village crates" (`gather_goblin_mail`, `:187-196`) | 3 (`:192`) | 10 steps x 3 = 30 | `Search Goblin Village crates · 30 / 3 Goblin mail` |
| 40/3 redberries | "Pick redberries" (`pick_redberries`, `:233-245`) | 4 (`:238`) | 10 steps x 4 = 40 | `Pick redberries · 40 / 3 Redberries` |
| 280/28 onion | "Pick onions" (`pick_onions`, `:222-232`) | 28 (`:227`) | 10 steps x 28 = 280 | `Pick onions · 280 / 28 Onion` |

The "/N" is the entry's count; the first number is `done`. The panel row text comes from `core/menu_action_queue.py:216-220` `_row_text` (`"{name} · {done:,} / {count:,} {unit}"`). The count 28 for onions is the count box default for an action no Bank item limits: `CARRIED_CAPACITY = 28` (`logic/inventory_pure.py:20`, used at `core/menu_action_queue.py:208`). The owner typed 3 for the other two (inferred from the numbers, unverified).

Probe `/tmp/pass18-probe-a/probe_overshoot.py` (output `probe_overshoot.out`) queued exactly (goblin mail, 3), (redberries, 3), (onions, 28) at speed 10 from Bankstanding. Each card finished one entry: card 1 gave 30 Goblin mail, card 2 gave 40 Redberries, card 3 gave 280 Onion and switched to Bankstanding with the dialog "The queue is finished: Pick onions done." The event log read: `+30 Goblin mail`, `Queue: Search Goblin Village crates done`, `+40 Redberries`, `Queue: Pick redberries done`, `+280 Onion`, `Switched to Bankstanding · The queue is finished: Pick onions done.`

### The overshoot applies to every unit, not only gathering

- Skill actions: the step loop is the same, so a skilling entry also runs a full card. The existing test `tests/action_queue/test_queue_reviews.py:47-101` queues 1 Iron platebody at 10x and asserts 2 made (`:79`, `:99`).
- Kills: combat runs one burst per card (`runtime/runtime_actions_context.py:224-225` sets ticks to 0 for `combat`), and the burst gets `stop_after_kills` only from the Slayer task (`runtime/runtime_actions_combat.py:553`). A kills entry can therefore pass its count inside one card. By code reading only; not probed.
- Reviews: one per card, so no overshoot (`core/action_queue.py:175`).
- Quests: no count (`core/action_queue.py:98-99`).

### 2. What would have to cap the last card

No queue code limits output today. Two places carry the information a cap needs:

1. **Between steps.** `can_continue` in `__init__.py:5025-5026` is checked before every step after the first (`runtime/runtime_actions_context.py:219-220`). A check of "the entry's remainder is reached" here would end the card at a step boundary. That alone still overshoots by up to one batch: redberries make 4 per step, so a count of 3 gives 4. Goblin mail (3 per step) and onions (28 per step) would land exactly on 3 and 28.
2. **Inside one batch.** `apply_utility_activity_pure` already caps `batch_count` by a `batch_size` argument through `_max_batches_for_requirements` (`logic_pure/logic_pure_production.py:191-197`, `:413-414`). A smaller cap passed there would make an exact amount for utilities. Skill handlers each have their own per-step yield (for example Runecrafting `craft_count` at `logic_pure/logic_pure_runecrafting.py:422`); a cap there is per handler (unverified for each skill).

Existing caps at a target amount:

- **Slayer kill cap.** `logic/slayer_logic.py:306-310` `slayer_kill_limit_pure` returns the task's remaining kills; `runtime/runtime_actions_combat.py:553` passes it as `stop_after_kills`; `logic_pure/logic_pure_combat_engine.py:1030` takes it; `logic_pure/logic_pure_combat_outcome.py:302-303` stops the burst at the kill boundary (`"slayer_task_complete"`). This is the closest model for a kills entry.
- **No "make N" path exists.** A bounded search for make-X, make-all, `craft_count`, `smith_count`, `target_count`, `quantity to make` in `core logic logic_pure runtime ui` found no non-queue amount feature (only the Runecrafting local variable above). The inventory cap in `_max_batches_for_requirements` limits by materials, not by a chosen amount.

### 3. What happens to a finished entry

- **Moving on.** `advance_action_queue` (`core/action_queue.py:427-460`) adds the card's progress; when `advance_queue_pure` reports the entry full, `pass_queue_entry_pure` (`:109-115`) writes `done` into the entry and increments `index`. If another entry is left, `_run_current_entry` (`:221-236`) starts it inside the same review and logs `Queue: <name> done` (`:452-457`). If none is left, `_switch_to_bankstanding("The queue is finished: <name> done.")` runs (`:460`), which shows the Bankstanding dialog.
- **A stopped entry** (missing material, requirement) passes through `_queue_takes_over_stop` (`:463-492`) and logs `Queue: <name> stopped · <reason>`.
- **The entry stays in the list.** `_queue_entry_row` (`:185-204`) gives every entry before `index` the state `"done"` or `"stopped"`. The panel labels are `_STATE_LABELS = {"done": "Done", "stopped": "Stopped", "waiting": "Next"}` (`core/menu_action_queue.py:39`); the running entry reads "Now", "Paused" or "Waits" (`:241`). A done row reads for example `1. Done  Search Goblin Village crates · 30 / 3 Goblin mail`; a stopped row adds `· stopped: <reason>` (`:220`). Done and stopped rows show the ✕ remove button, because only the running entry is not removable (`core/action_queue.py:193`, `:203`).
- **When all are done**, the title stays `Queue: 3 of 5 entries` and the hint reads `Finished. Clear queue removes the finished entries.` (`core/menu_action_queue.py:225-226`, probe output).
- **What removes done entries now:** Clear queue; the ✕ on each row (`core/action_queue.py:129-139`); or the next add to a finished queue, which drops the old plan first (`core/action_queue.py:102-103`, pinned by `tests/action_queue/test_queue_state.py:68-79`). Done entries in a queue that still runs stay until one of these.
- Done entries take one of the 5 places while the queue still runs: `can_add` is `finished or len(rows) < 5` (`core/action_queue.py:217`).

### 4. Clear queue, and Bankstanding

### The idle state

- Bankstanding is a utility: `current_utility == "bankstanding"` with `current_skill == "Utilities"` (`UTILITY_REVIEW_ACTION_DISPLAY_NAME`, `core/action_registry.py:23`). The data row is `"bankstanding"` with `display_name` "Bankstanding" and `no_op: True` (`core/constants_parts/activity_updates.py:27-35`). `_BANKSTANDING = "bankstanding"` in `core/last_action.py:37`.
- The single transition is `_switch_to_bankstanding` (`__init__.py:1278-1321`). It logs `Switched to Bankstanding · <reason>` (`core/action_queue.py:504-505`), and when `automatic=True` it queues the Bankstanding dialog (`__init__.py:1308-1312`).
- What the player sees on the review HUD: title "Utilities", sub line "Bankstanding • <status>" (`ui/ui.py:2697`, `:2704-2709`). The status is `idle at the Bank` (`_IDLE_AT_BANK`, `core/last_action.py:45`) or `stopped: <reason>` when a last action can be resumed, with the button `Resume <name>` (`core/last_action.py:112-139`).

### What Clear does now

`clear_action_queue` (`core/action_queue.py:304-313`) always empties the queue. It switches to Bankstanding **only** when `_runs_queue_entry` (`:294-301`) is true: an entry is current, the queue is neither paused nor waiting, and the running action equals the entry's action.

| Queue state when Clear is pressed | Activity after Clear | Code / test |
|---|---|---|
| The queue runs its entry | Bankstanding, reason "The queue was cleared.", `automatic=False`, so **no dialog**. HUD: "Bankstanding • stopped: The queue was cleared." and `Resume <entry>` | `core/action_queue.py:312`; `tests/action_queue/test_queue_menu.py:77-100` asserts `active == "Utilities"`, no dialog, `("Resume Mining", "stopped: The queue was cleared.")` |
| The plan waits behind an action the player started by hand | **The hand-started action keeps running.** No Bankstanding | docstring `core/action_queue.py:307-309`; `tests/action_queue/test_queue_menu.py:102-117` asserts Woodcutting still runs |
| Paused by Stop training | Bankstanding already (Stop put the player there) | `core/action_queue.py:357-388`, `:479-481` |
| Finished | Bankstanding already (the finish switched there) | `core/action_queue.py:460`; probe: after Clear, `Utilities`, `bankstanding` |
| Running action differs from the entry, but the queue is not paused | That action keeps running | `_runs_queue_entry` `:300`; normally `advance_action_queue` pauses the queue on such a review (`:444-446`) |

So the only case in which Clear leaves the player doing something is the second and fifth rows: an action that the queue did not start. Which case the owner hit is unverified; the note matches the waiting-plan row (Pass 17 ruled that a new plan never replaces a hand-started action, `core/action_queue.py:16-18`).

After any Clear the panel hides and the footer line reads `Queue: empty. Add up to 5 actions or quests. Entries run once, top to bottom.` (`ui/ui_action_queue.py:277-279`, `core/menu_action_queue.py:234`, `:246`).

### 5. The queue panel and its scroll bar

- Widget: `ActionQueuePanel(QFrame)`, object name `actionQueuePanel`, in `ui/ui_action_queue.py:179-304`. Placed under the tabs, above the footer, in `ui/ui.py:26063-26064`; its empty line sits in the footer at `ui/ui.py:26073`.
- Cap of 5: `MAX_QUEUE_ENTRIES = 5` (`core/action_queue.py:56`); refusal in `add_queue_entry_pure` (`:104-105`); text `QUEUE_FULL_TEXT = "The queue holds 5 entries. Clear it to plan again."` (`:57`). The panel always builds 5 grid rows (`ui/ui_action_queue.py:233`).
- Height policy: the rows sit in a `QScrollArea` `actionQueueRows` (`:235-242`), horizontal bar always off (`:239`), vertical bar left at Qt's default (as needed). Its height is **fixed** at `min(rows, _VISIBLE_ROWS) * (lineSpacing + 2)` (`:291-293`) with `_VISIBLE_ROWS = 2` (`:48-49`). The comment says the box must not take height from the lists above (`:48`, `:214`).
- Why the scroll bar shows: (a) any 3rd to 5th entry passes the 2-row fixed height; (b) each hidden row's ✕ button keeps its space (`setRetainSizeWhenHidden(True)`, `:264-267`), so the 5 grid rows keep about 15 px each even when empty.
- Measured offscreen (Fusion style, test font, `lineSpacing` 15, row label 17 px; probe `/tmp/pass18-probe-a/probe_panel.py`, output `probe_panel.out`):

| Entries | Scroll area height | Rows content (sizeHint) | Vertical bar maximum |
|---|---|---|---|
| 1 | 17 | 92 | 60 |
| 2 | 34 | 109 | 45 |
| 3 | 34 | 126 | 47 |
| 4 | 34 | 143 | 49 |
| 5 | 34 | 160 | 51 |

The numbers were the same at dialog sizes 900x560, 900x900 and 1400x1200. The scroll bar therefore shows at **every** entry count and **every** dialog size, including one entry. A full queue of 5 single-line rows needs about 5 x 17 = 85 px (unverified on macOS native fonts). Row labels wrap (`:255`), so a long row is taller than one line.

### 6. Every way to add an entry, and the feedback

All adds go through `QueueAddControl` (`ui/ui_action_queue.py:97-156`: count box `queueCountBox`, button "Add to queue" `queueAddButton`, materials line `queueMaterials`) → `MenuQueue.__call__` (`:82-89`) → `apply_action_queue_command(addon, "add", ...)` (`core/action_queue.py:337-354`, wired at `__init__.py:4297`) → `add_to_action_queue` (`:279-291`).

| Entry point | Code | Record queued |
|---|---|---|
| Each skill panel, under "Train this skill", including Combat and the Utilities hub ("Start utility") | `ui/ui.py:20929` `surface_queue_control` (`ui/ui_action_queue.py:158-160`) | What that panel's Start would run (`core/menu_action_queue.py:42-59`); the gather utilities come from here |
| Activities card detail | `ui/ui.py:19564` `activity_queue_control` (`ui/ui_action_queue.py:162-164`) | The open card's utility |
| Quests tab, each quest card header | `ui/ui_tab_quests.py:358` | `{"kind": "quest", "quest_id": ...}`, no count box |

No other caller of `add_to_action_queue` or the "add" command exists (search of `__init__.py core ui runtime`). The review HUD has no add control.

Feedback when an add **succeeds**:

- The red warn label in the menu's status row (`ui/ui.py:4793-4795`) is set to `""` (`ui/ui.py:4889-4890`).
- The panel refreshes through `notify_action_queue_changed` (`ui/ui.py:3999-4001` from `update_review_hud`; `core/action_queue.py:353`). On the first entry the hidden panel appears at the bottom of the dialog; later entries add a row there, which can sit below the 2-row scroll fold (section 5), so a 3rd to 5th add can show no visible change.
- If the add starts the entry at once (player at Bankstanding, no plan running, `core/action_queue.py:269-276`), the menu's active label changes and the panel re-renders (`ui/ui.py:4891-4896`); for a utility it first asks to leave a running session (`ui/ui_action_queue.py:84-86`).
- The count box keeps the typed number (`ui/ui_action_queue.py:87-88`, `:143-144`).
- No popup, no message, no button change. The Add button's tooltip describes the add before it (`core/menu_action_queue.py:195-198`).

Feedback when an add **fails**:

| Case | What the player sees | Code |
|---|---|---|
| Queue full | Add button disabled; tooltip `The queue holds 5 entries. Clear it to plan again.` (a click cannot happen). If the command still runs, the red warn label shows the same text | `core/menu_action_queue.py:173-174`, `ui/ui_action_queue.py:151-152`; `core/action_queue.py:343-344` |
| No target chosen | Button disabled; tooltip `Choose what to do first.` | `core/menu_action_queue.py:171-172` |
| Quest complete / locked | Button disabled; tooltip `This quest is complete.` or `Requires: ...` | `core/menu_action_queue.py:177-180` |
| Count 0 (box minimum is 0, `ui/ui_action_queue.py:122`) | Red warn label `Type a count of 1 or more.` | `core/action_queue.py:344` |
| Invalid action record, or the start commit refused | Same red text `Type a count of 1 or more.`, which does not name the real cause | `core/action_queue.py:95-97`, `:286-289`, `:343-344` |
| Player declines to leave a running session | Nothing happens, no message | `ui/ui_action_queue.py:84-86` |

### 7. Save data

- Stored inside the player save dict under `ACTION_QUEUE_KEY = "action_queue"` (`core/action_queue.py:55`); the dict is saved to Anki config key `ankiscape_player_data` (`core/storage.py:16`, `:25-28`, `:81-90`).
- Format:

```
"action_queue": {
  "entries": [ {"action": {<last-action record>}, "count": int | null, "done": int?, "stopped": str?}, ... ],
  "index": int,      # current entry
  "done": int,       # progress of the current entry
  "paused": bool,
  "waiting": bool
}
```

  The action record keys per kind are in `core/last_action.py:38-44` (`skill: skill, target`; `utility: utility_id`; `quest: quest_id`; `combat: target, combat_action`). `done` and `stopped` on an entry are written when it passes (`core/action_queue.py:112-114`).
- No queue version field. The save has a global `config_version` (`CURRENT_CONFIG_VERSION = 126`, `core/storage_pure.py:364`), and no migration reads `action_queue` (search found no reference in `core/storage*.py`). The read side sanitizes instead: `action_queue_pure` drops entries this game cannot start and cuts to 5 (`core/action_queue.py:64-81`).
- Undo: every queue command is one Edit > Undo step through `commit_direct_action` (`__init__.py:747-829`).

### 8. Tests that pin the current behaviour

| Behaviour | Test |
|---|---|
| Overshoot kept in `done` (13 for count 10) | `tests/action_queue/test_queue_state.py:38` `test_an_entry_that_reaches_its_count_hands_over_to_the_next` |
| Overshoot at 10x through the real handler (1 platebody queued, 2 made; Bankstanding dialog text; done rows stay) | `tests/action_queue/test_queue_reviews.py:47` `test_mine_smelt_smith_runs_its_counts_passes_a_short_entry_and_ends_at_bankstanding` |
| Done rows stay; finished queue gives way to a new plan | `tests/action_queue/test_queue_state.py:68` `test_a_finished_queue_never_repeats_and_gives_way_to_a_new_plan` |
| Stopped row with reason | `tests/action_queue/test_queue_state.py:50` `test_an_entry_that_runs_short_is_passed_with_its_reason` |
| Cap of 5 (pure) | `tests/action_queue/test_queue_state.py:59` `test_a_sixth_entry_is_refused` |
| Cap of 5, refusal text, Clear stops the running entry, no dialog, Resume text | `tests/action_queue/test_queue_menu.py:77` `test_a_sixth_entry_is_refused_and_clear_stops_the_entry_the_queue_runs` |
| Clear leaves a hand-started action running | `tests/action_queue/test_queue_menu.py:102` `test_a_plan_waits_behind_a_hand_started_action_until_it_stops` |
| Panel: 5 entries, disabled Add tooltip, **rows scroll (`height < 5 * 18`)**, Clear hides the panel | `tests/main_menu/test_action_queue_panel.py:114` `test_the_fifth_entry_fills_the_queue_and_clear_empties_it` (assert at `:126-127`) |
| ✕ on rows that do not run | `tests/main_menu/test_action_queue_panel.py:134` `test_each_entry_that_is_not_running_has_a_remove_control` |
| Count box default and typed count kept | `tests/main_menu/test_action_queue_panel.py:82` `test_the_count_box_starts_at_what_the_bank_allows_and_keeps_a_typed_count`; `tests/action_queue/test_queue_menu.py:19,36` (`BankLimitTest`, `test_an_unlimited_action_starts_at_one_inventory`) |
| Units per kind | `tests/action_queue/test_queue_state.py:93` `test_each_entry_counts_in_its_own_unit`; `:103` `test_the_product_is_what_the_player_picked_the_action_for` |
| Bank-default smelt entry to done; bury counts bones | `tests/action_queue/test_queue_menu.py:48`, `:63` |
| Waiting plan, Start now | `tests/action_queue/test_queue_menu.py:127`; `tests/main_menu/test_action_queue_panel.py:151` |
| Add that starts an activity asks to leave a session / waits | `tests/main_menu/test_action_queue_panel.py:201`, `:210` |
| Quest card queues without a count | `tests/main_menu/test_action_queue_panel.py:230` |
| Pause, resume, stop takeover, reasons | `tests/action_queue/test_queue_reviews.py:102, 122, 142, 163, 182, 202, 234, 256, 286, 313` |
| Panel does not overlap at 720/900 wide, 560 tall (2 entries) | `tests/main_menu/test_macos_layout.py` `test_no_font_or_style_margin_makes_two_widgets_of_a_row_overlap` (`_equipment_menu` at `:73-97`) |

No test pins the Clear behaviour when the queue is finished or paused, the add feedback text on success, or the scroll bar at one entry.

The 35 queue tests (`tests.action_queue`, `tests.main_menu.test_action_queue_panel`) pass at `d4f7164ac` (`python3 run_tests.py tests.action_queue tests.main_menu.test_action_queue_panel`, run 2026-10-27 23:07 PDT).

## B: Pass 18 layout facts (GE offer panel, Bank grid, top-level tab arrows)

Source revision: AnkiScape `main` at `d4f7164ac`. All probes are read-only scratch scripts in `/tmp/pass18-probe-b/` (`probe.py`, `sweep.py`, `squeeze.py`, `bank.py`, `cells.py`, `tabarrows.py`); screenshots and JSON output are in the same folder.

Probe environments used:

| Label | Platform | Style | Qt runtime | Font |
|---|---|---|---|---|
| native | `QT_QPA_PLATFORM=cocoa`, dialog `WA_DontShowOnScreen` (no window on screen) | `macos` (QMacStyle) | 6.11.1 (`.venv-qt`), repeated on 6.11.0 from `/Applications/Anki.app` (Anki 26.5 bundle) | 13.0 pt |
| offscreen | `offscreen` | `fusion` | 6.11.1 | 9.0 pt |
| sim | `offscreen` | Pass 17 `_MacLayoutItemStyle` (Fusion + check-box trim) | 6.11.1 | 9.0 × 1.25 pt |

Anki on macOS defaults to `WidgetStyle.NATIVE` (`.venv-qt/lib/python3.13/site-packages/aqt/profiles.py:613-616`), which keeps the Qt `macos` style and sets no app stylesheet (`aqt/theme.py:245-275`). The owner's screenshot matches the native style (macOS popup button and stepper controls). AnkiScape sets no app-wide stylesheet or font (repo search for `style_did_init|app.setStyleSheet|setFont(` in `core ui runtime logic` finds only per-widget fonts).

---

### 1. Grand Exchange offer panel

### Where it is

- There is no separate class or builder function. The panel is inline code in `show_main_menu` (`ui/ui.py:4574`).
- GE tab block starts at `ui/ui.py:21467` (`ge_tab = QWidget()`, object name `grandExchangeTab`, `QVBoxLayout` margins 12, spacing 8: `ui/ui.py:21470-21474`).
- The tab page is `vertical_scroll(ge_tab)` (`ui/ui.py:22271`), a `QScrollArea` with `setWidgetResizable(True)`, no frame, horizontal bar off (`ui/ui_text_fit.py:234-241`). Tab added at `ui/ui.py:22272`.
- The offer panel is `ge_editor`, a plain `QWidget` with object name `geOfferEditor` (`ui/ui.py:21607-21614`). It has a style sheet only for its own border and background (`QWidget#geOfferEditor {...}`, `ui/ui.py:21609-21612`). Layout: `QVBoxLayout`, margins (10, 8, 10, 10), spacing 6 (`ui/ui.py:21613-21615`).
- The editor sits in `ge_body` (`QHBoxLayout`, spacing 8) beside the catalog column, both with stretch 1 (`ui/ui.py:21578-21605`, `ui/ui.py:21702`). `ge_body` has stretch 1 in the tab layout (`ui/ui.py:21703`).

### Full structure of the GE tab, top to bottom

1. Header row: "Grand Exchange" title, coin balance label `geCoinBalanceLabel`, stretch, "Collect all" `geCollectAllButton` (`ui/ui.py:21476-21490`).
2. Status label `geStatusLabel`, word wrap (`ui/ui.py:21492-21496`).
3. "Offer safety" toggle `geOfferSafetyToggle` (QToolButton, arrow) (`ui/ui.py:21498-21507`).
4. Offer safety panel `geOfferSafetyPanel`, hidden by default: "Confirm totals from" spin (Coins), "Low price below" spin (%), "High price above" spin (×), "Apply" button (`ui/ui.py:21509-21545`).
5. Six offer slots `geOfferSlot1..6`, `QGridLayout` 3 columns, each QToolButton min height 54, vertical policy Fixed (`ui/ui.py:21547-21575`).
6. Body row (`ge_body`): left = catalog search `geItemSearchInput` + item list `geItemList` (min width 250); right = offer panel `geOfferEditor` (`ui/ui.py:21577-21703`).
7. Order detail strip `geOrderDetailPanel`: detail label, "Collect", "Edit remainder", "Cancel offer" (`ui/ui.py:21705-21723`).

Offer panel (`geOfferEditor`) rows, in order (`ui/ui.py:21616-21701`):

| # | Row | Controls (object names) | Line |
|---|---|---|---|
| 0 | Item title | `QLabel` `geSelectedItemLabel`, bold ("Woad leaf") | 21616-21619 |
| 1 | Item meta | `QLabel` `geSelectedItemMeta`, word wrap, vertical policy Fixed ("Guide: 23 Coins · Buy limit per 40 cards: 100 · Bank: 0") | 21620-21628 |
| 2 | Offer side | row `QWidget` + `QHBoxLayout`: label "Offer", `QComboBox` `geOfferSideCombo` (Buy / Sell), stretch 1 | 21630-21639 |
| 3 | Quantity | row `QWidget` + `QHBoxLayout`: label `geOfferQuantityLabel` "Quantity", `QSpinBox` `geOfferQuantitySpin` (1..2147483647, stretch 1), `QPushButton` `geSellAllButton` "Sell all" (hidden on the Buy side) | 21641-21656 |
| 4 | Price | row `QWidget` + `QHBoxLayout`: label "Price each", `QSpinBox` `geOfferPriceSpin` (stretch 1) | 21658-21666 |
| 5 | Quick prices | row `QWidget` + `QHBoxLayout` spacing 4: `QPushButton` "-5%" `gePriceMinus5Button`, "Guide" `geGuidePriceButton`, "+5%" `gePricePlus5Button` | 21668-21686 |
| 6 | Stretch | `addStretch(1)` | 21695 |
| 7 | Preview | `QLabel` `geOfferPreviewLabel`, word wrap, vertical policy Fixed ("Buy 1 × 23 Coins · Total 23 Coins") | 21688-21696 |
| 8 | Submit | `QPushButton` `geSubmitOfferButton` "Place buy offer" / "Place sell offer" | 21697-21701 |

There is no slider in the code. The thin line in the screenshot's Quantity row is the `geOfferQuantitySpin` spin box squashed to a few pixels; its "1" is still visible at the left edge.

### Measured geometry (native, 900 × 560, "Woad leaf" selected)

Layout-item heights in the editor (`/tmp/pass18-probe-b/probe-cocoa-macOS-900x560.json`):

| Row | Given | Size hint | Minimum |
|---|---|---|---|
| title | 16 | 16 | 16 |
| meta | 16 | 32 | 32 |
| Offer row | 32 | 32 | 32 |
| Quantity row | 30 | 30 | 30 |
| Price row | 18 | 18 | 18 |
| Quick-price row | 32 | 32 | 32 |
| stretch | 32 | 0 | 0 |
| preview | 16 | 32 | 32 |
| submit (layout item) | 20 | 20 | 20 (widget is 32 tall) |

- Editor: 418 × 272; `minimumSizeHint().height()` 272; `sizeHint().height()` 256. GE tab 868 × 558 inside a 447 px viewport; the vertical scroll bar maximum is 111. In this state nothing is squeezed (screenshot `/tmp/pass18-probe-b/ge-editor-cocoa-macOS-900x560.png`).
- Native control sizes: spin boxes 18 tall; combo box 32; each push button 32 tall with a 20 px layout item. The macOS style reports layout-item margins for push buttons, which is why the submit button widget is 32 tall in a 20 px layout slot.
- The Quantity row is 30 tall while the Price row is 18, although both hold one spin box. The only difference is the hidden "Sell all" push button at the end of the Quantity row (`ui/ui.py:21651-21655`). Its macOS layout-item margins enlarge the row's margins (spin box placed at y = 4 inside the row). Inference from the measured numbers; the Qt source path (macOS-only effective-margin code in `QBoxLayout`) is unverified.
- Fusion offscreen: all rows at their hint (spin boxes 22, buttons 25); no squeeze.

### Why the Quantity row and the three percent buttons compress

Reproduced mechanism (`/tmp/pass18-probe-b/squeeze.py`): when the editor gets less height than its 272 px minimum, Qt's box layout shrinks the tallest rows first, to one common cap. The tallest rows are Offer (32), Quick prices (32) and Quantity (30). Price (18), labels (16) and the submit layout item (20) are under the cap and stay whole. Measured native results when the editor layout is forced to a height:

| Editor height | Offer row | Quantity row (spin box h) | Price row | Quick-price row (button h) | Submit (widget h) |
|---|---|---|---|---|---|
| 240 | 32 | 30 (18) | 18 | 32 (32) | 20 (32) |
| 220 | 24 | 25 (13) | 18 | 24 (24) | 20 (32) |
| 201 | 19 | 18 (6) | 18 | 19 (19) | 19 (31) |
| 190 | 17 | 16 (4) | 16 | 17 (17) | 16 (28) |

At 201 px the rendering (`/tmp/pass18-probe-b/squeeze-201.png`) matches the owner's screenshot: "Quantity" text cut, spin box reduced to a line with "1" at the left, "-5%", "Guide" and "+5%" squashed with cut text, "Price each" and "Place buy offer" normal. The Offer row is also squeezed (19 of 32), but the macOS popup button draws its fixed-height face centred, so it looks normal. The owner's editor measures about 200 logical px tall in the screenshot (403 image px at 2×).

What gives the editor less than its minimum in the owner's run is **unverified**. These probes did not reproduce it:

- `sweep.py`: dialog widths 720, 800, 900, 1000, 1200 × heights 420, 480, 560, 700, 900. The editor was never below its row minimums: native on Qt 6.11.1 and 6.11.0, `QT_SCALE_FACTOR` 1.1 and 1.25, always-visible (non-transient) scroll bars, and long status, order-detail and slot texts.
- With long texts, the editor got exactly its height-for-width value (240 at 900 wide), with 0 px of spare height. Any extra need that the scroll area does not see therefore goes straight into the capped rows.

Contributing design facts (all confirmed in code):

- No row has a fixed height or a minimum height of its own. Row containers are plain `QWidget`s with default size policy (`ui/ui.py:21630`, `21641`, `21658`, `21668`).
- The only protection against squeeze is the outer `vertical_scroll` (`ui/ui_text_fit.py:234-241`), which sizes the tab from minimum and height-for-width hints.
- The editor's real need depends on word-wrapped labels (`geSelectedItemMeta`, `geOfferPreviewLabel`, both Fixed vertical policy, `ui/ui.py:21622-21628`, `21690-21694`). Their minimum hint is 32 px (two lines) but they get 16 px at real width.

### Tests that cover the GE panel

- `tests/main_menu/test_macos_layout.py::MacLayoutTest::test_every_tab_keeps_its_text_whole_without_two_widgets_of_a_row_overlapping` visits every main tab, including "Grand Exchange", at 900 × 560 and 720 × 560. It runs `text_fit_defects` and a sibling-overlap check. It passes. It cannot see this bug: it uses Fusion with only the check-box trim (`tests/main_menu/test_macos_layout.py:24-28`), so no push-button layout-item margins, and the panel is never squeezed there. Sim measurement is the Fusion row in the table above.
- No test asserts GE row heights or the editor height. GE behaviour tests (values and routing, not layout) are in `tests/main_menu/test_grand_exchange.py`: `test_grand_exchange_tab_renders_period_six_slots_and_routes_an_offer` (line 86), `test_grand_exchange_sell_all_and_bank_quantities_and_compounding_nudges` (line 315), `test_grand_exchange_reclicking_current_item_resets_guide_price` (line 58), and others at lines 18, 27, 49, 72, 279, 421, 471, 542, 598, 671. `tests/main_menu/test_wheel_guard.py:118` finds the two GE spin boxes by object name.

---

### 2. Bank grid

### Where it is

- Bank tab block in `show_main_menu`. Grid scroll area: `bank_grid_scroll = _ResponsiveGridScrollArea()`, object name `bankGridScroll`, widget-resizable, horizontal bar off (`ui/ui.py:23870-23874`). The class only adds a resize callback (`ui/ui.py:1452-1462`).
- Grid host `bankGrid` (`QWidget`) with `QGridLayout` `bank_grid_layout`: margins 0, horizontal spacing 0, vertical spacing 4 (`ui/ui.py:23875-23880`).
- Cells are built in `_render_bank_surface` (`ui/ui.py:24331-24417`). Each cell is a `_BankDropButton` (`QToolButton` subclass, `ui/ui.py:1464`), object name `bankGridItem::<item>`, `setFixedSize(54, 54)`, `ToolButtonTextUnderIcon`, icon 28 × 28, quantity text such as "×1,234" (`ui/ui.py:24357-24376`). Per-cell style sheet: 1 px border (2 px when selected), radius 4, `font-size: 9px`, `padding: 1px` (`_style_bank_cell`, `ui/ui.py:24307-24314`).
- Column count: `fit_bank_grid_columns` / `bank_grid_columns` in `ui/ui_bank_grid.py:11-22` (54 px cells, up to 12 columns, the column after the last absorbs slack). With auto categories on, each category gets a header `QLabel` "— <label> —" spanning all columns (`ui/ui.py:24352-24357`) and starts a new row.
- A second set of square grids lives in the Bank tab's collapsible "Carried" pack editor: pack plan `carriedLayoutGrid<suffix>` with 28 `QPushButton` cells fixed at 44 × 44, spacing 4 (`ui/ui.py:23421-23458`), and the bank picker `carriedBankPicker<suffix>` with 44 × 44 cells (`ui/ui.py:23471-23497`, `23650-23660`). It is unverified which grid the owner means; the main grid is the most likely reading of "grid squares in the bank".

### Measured geometry

`/tmp/pass18-probe-b/bank.py` (51 items, dialog 900 × 560):

| Env | Auto categories | Cell h | Row pitch | Grid host h / min hint | Overlaps |
|---|---|---|---|---|---|
| native 6.11.1 | on | 54 | 84 (category rows), 58 (rows in one category) | 1062 / 1062 | 0 |
| native 6.11.1 | off | 54 | 58 | 384 / 344 | 0 |
| native 6.11.0 (Anki bundle) | on / off | 54 | same as above | same | 0 |
| native, always-visible scroll bars | on / off | 54 | same | same | 0 |
| offscreen Fusion | on | 54 | 83 / 58 | 1050 / 1050 | 0 |
| offscreen Fusion | off | 54 | 58 | 360 / 344 | 0 |

- Row pitch inside one category = 54 + 4 = 58, so adjacent rows have a 4 px gap. A category row pitch is header 22 (native) + 4 + 54 + 4 = 84.
- The macOS style reports no layout-item margin for these cells (`SE_ToolButtonLayoutItem` rect = the full 54 × 54).
- Carried pack-plan grid (`cells.py`, native and Fusion): 28 cells 44 × 44, pitch 48 both ways, 0 overlaps.
- Screenshot of a correct native grid: `/tmp/pass18-probe-b/bank-cocoa-macos-auto0.png`.

### Cause of vertical overlap

Reproduced mechanism (`SQUEEZE=1 bank.py`): the cells have a fixed 54 px height, but a `QGridLayout` still places rows closer together when the grid host gets less height than its minimum. Fixed-size widgets keep their size and run into the next row:

| Grid host height (6 rows, min 344) | Row pitch | Overlapping cell pairs | Overlap per pair |
|---|---|---|---|
| 300 | 50-51 | 42 | 3 px |
| 250 | 42-43 | 42 | 11 px |

This is the same failure as the GE panel: a container gets less than its minimum height and the layout squeezes rows that cannot shrink. The scroll area is the only protection. What gives the bank grid host less than its minimum in the owner's run is **unverified**. No probe reproduced overlap without forcing it. The owner's note has no screenshot, window size, auto-category state or tab.

### Tests that pin the bank layout

- `tests/main_menu/bank/test_grid.py::MainMenuWidgetTest::test_bank_frame_a_uses_twelve_54_pixel_columns_and_280_pixel_detail` (line 143): at 1280 × 752, 14 cells are 54 px wide, the first row has 12 cells with x pitch `[54] * 11`, right column 280 wide, and no horizontal scroll. It checks no vertical pitch or overlap.
- `tests/main_menu/bank/test_packs.py::MainMenuWidgetTest::test_carried_layout_grid_present_wired_and_never_geometrically_compressed` (line 86), `test_custom_pack_bank_grid_icons_quantity_menu_and_live_inventory` (line 305), `test_carried_layout_grid_reachable_without_an_active_pack_target` (line 683) cover the carried grids.
- `tests/main_menu/test_macos_layout.py::MacLayoutTest::test_every_tab_keeps_its_text_whole_without_two_widgets_of_a_row_overlapping` visits the Bank tab and checks sibling overlap, so it would catch overlapping cells in the sim environment. It passes.
- Other bank grid tests in `tests/main_menu/bank/test_grid.py` cover behaviour, not geometry: lines 23, 44, 89, 198, 217, 229, 238, 286, 333.

---

### 3. Top-level tab bar arrows

### Which bar

- The top-level bar is the main-menu `QTabWidget` named `tabs` in `show_main_menu` (`ui/ui.py:4741-4746`): `setDocumentMode(True)`, icon size 18, `tabBar().setElideMode(Qt.TextElideMode.ElideNone)`, `setExpanding(False)`, `setUsesScrollButtons(True)`. There is no subclass and no style sheet on it.
- Dialog: `QDialog`, title "AnkiScape Menu", minimum 720 × 540, layout margins 16 (`ui/ui.py:4731-4739`).
- Tab count 11. Order is fixed by `desired_tab_order` and `moveTab` (`ui/ui.py:25925-25945`): Skills, Stats, Bank, Equipment, Shop, Grand Exchange, Challenges, Quests, Achievements, Collections, Settings.

### When the arrows appear (measured at dialog 900 × 560)

| Env | Bar width | Bar size-hint width (all tabs) | Tab widths | Arrow geometry (x, y, w, h) |
|---|---|---|---|---|
| native 13 pt | 868 | 1433 | 110, 110, 109, 139, 110, 169, 141, 120, 157, 142, 126 | left (837, 0, 16, 24), right (852, 0, 16, 24) |
| offscreen QMacStyle 9 pt | 868 | 1486 | 113 … 131 | left (837, 0, 21, 24), right (847, 0, 21, 24) |
| offscreen Fusion 9 pt | 868 | 1178 | 85 … 103 | left (837, 0, 21, 34), right (847, 0, 21, 34) |

- Bar width = dialog width − 32. Arrows show whenever the bar is narrower than its hint, so natively they show for every dialog narrower than about 1465 px (1433 + 32). This is derived from the numbers above; it was not measured at that width.
- The arrows are QTabBar's built-in scroll buttons (object names `ScrollLeftButton`, `ScrollRightButton`; `QToolButton`s with left and right arrow types). Qt's base style puts both at the right end through `SE_TabBarScrollLeftButton` / `SE_TabBarScrollRightButton`.

### Options in Qt 6.11 to put one arrow at each end

1. **Proxy style that moves the left button** (tested, works). Override `subElementRect` for `SE_TabBarScrollLeftButton` to return a rect at x = 0, and move `SE_TabBarTearIndicatorLeft` to just right of it. QTabBar then offsets the tabs past the left button and still scrolls to both ends. Disposable probe `/tmp/pass18-probe-b/tabarrows.py` (600 px bar, the same 11 labels):
   - native macOS, Qt 6.11.1 and 6.11.0: left arrow (0, 0, 16, 24), right arrow (584, 0, 16, 24), first tab starts at x = 16. After scrolling fully right, the last tab ends at 583, left of the right arrow at 584. After scrolling fully left, the first tab starts at 16, right of the left arrow (right edge 15). Image: `/tmp/pass18-probe-b/tabbar-cocoa-macOS-split.png`.
   - offscreen Fusion / QMacStyle: the buttons are 21 wide, but the tab offset is 16, so the first tab and the scrolled last tab sit 5 px under the arrows. This is an offscreen-only mismatch in this probe; a product version would need to match the offset to the button width.
   - Caveat: the existing test `tests/ui_flows/test_main_menu_tab_bar.py` calls `tabs.setStyle(style)` and `bar.setStyle(style)` with a plain `macOS` style (lines 69-75). That replaces any proxy style set on the bar, so the test would not exercise the split placement unless it changes.
2. **Style sheet**: `QTabBar::scroller` sets only the scroller width, and `QTabBar QToolButton` styles the buttons. Neither moves the left button to the left end. Unverified against Qt source; not probed.
3. **Own buttons with `setUsesScrollButtons(False)`**: put `QToolButton`s at both ends, for example with `QTabWidget.setCornerWidget(button, Qt.Corner.TopLeftCorner)` and `Qt.Corner.TopRightCorner`. With built-in scrolling off and `ElideNone`, the bar can no longer scroll, so its minimum width grows to all tabs (1433 native), which breaks the 720 minimum width. These buttons can only work by changing the current tab (previous / next) or by driving the hidden built-in buttons. Not probed.
4. **Own buttons around a bar that keeps built-in scrolling, with the built-in buttons hidden**: QTabBar shows its own buttons again on each layout pass, so this needs the proxy style anyway. Unverified.

The codebase uses none of these today. A repo search for `setCornerWidget|QProxyStyle|SE_TabBar|PM_TabBarScroll` in `ui core logic` finds no matches. Product `QProxyStyle` use is zero. Tests use proxy styles (`tests/main_menu/test_macos_layout.py:24`, `tests/ui_flows/test_tree_keyboard_navigation.py:36`).

Open question for the owner: "scroll through the top-level tabs" can mean scroll the strip (built-in behaviour, option 1) or select the previous / next tab (option 3).

### Tests that pin the tab bar

- `tests/ui_flows/test_main_menu_tab_bar.py::MainMenuTabBarTest::test_macos_style_keeps_tab_names_whole_and_scrolls_to_every_tab` (line 59): at widths 720 and 980 under the `macOS` style, no tab text is elided, the right arrow is visible and enabled, and the left and right arrows scroll to the last and first tab. It finds the arrows by `arrowType()`, not by position. It does not assert where the arrows are.
- `tests/main_menu/test_macos_layout.py::MacLayoutTest::test_every_tab_keeps_its_text_whole_without_two_widgets_of_a_row_overlapping` iterates all 11 tabs, but checks tab pages, not the bar.
- No test asserts the tab order. The order is set at `ui/ui.py:25925-25945`; tests look tabs up by label (`tests/test_main_menu_widget.py:474-479`).

---

### 4. Test run

`python3 run_tests.py tests/main_menu/test_macos_layout.py tests/ui_flows/test_main_menu_tab_bar.py tests/main_menu/test_grand_exchange.py tests/main_menu/bank/test_grid.py` → `Ran 26 tests in 11.961s`, `OK` (selection count 26).

### 5. Summary of what is verified

| Note | Verified | Unverified |
|---|---|---|
| GE squeeze | Mechanism reproduced natively: the editor below its 272 px minimum shrinks the 30-32 px rows (Quantity, quick prices, Offer) to a common cap; at 201 px the rendering matches the screenshot | What takes height from the editor in the owner's run |
| Bank overlap | Fixed 54 × 54 cells overlap when the grid host is below its minimum (3 px at 300 / 344, 11 px at 250 / 344) | Which grid the owner means; the trigger in the owner's run |
| Tab arrows | Built-in QTabBar buttons at the right end; a proxy style moves the left one to x = 0 and scrolling still reaches both ends natively | The style-sheet route; the corner-widget route |

Questions that would settle the unverified items: the owner's main-menu window size, a Bank screenshot, the Bank auto-category state, and whether the macOS setting "Show scroll bars" is "Always".

## C — Dyes, Goblin Diplomacy and woad: code facts

Repo `/Users/armantarkhanian/Code/AnkiScape`, `main` at `d4f7164ac`, read on
2026-10-27. Read-only research. Scratch probes are in `/tmp/pass18-probe-c/`
(`probe1.py` to `probe10.py`). Darkan source read at
`/Users/armantarkhanian/Documents/2012scape with bots/darkan-world-server`
(HEAD `1912a55cb245cc4410e51b200f9ad4c5e480510f`).

Owner notes in scope (`/Users/armantarkhanian/Code/ankiscape-pass18/facts/pass18-notes.txt`):

- line 2: "Make it so you can buy woad from the one guy in Falador"
- line 7: "Just streamline all the stuff you need to do for Goblin Diplomacy besides having to bring the supplies. If you do or don't have the dyes mixed (or even created by Aggie) it should do it for you as a step (one for each extra action required)"
- line 9: "There's no option to click dyes on each other to mix them, and in the utilities there's only the option to mix orange dye"

Related note outside scope, line 6: the queue over-ran "30/3 goblin mail, 40/3
redberries, 280/28 onion". The Goblin Diplomacy gathering actions are part of
that report.

### 1. Dyes

### Dye items in the item registry

Probe `probe4.py` reads `item_definitions_by_storage_key(ITEM_DEFINITIONS)`.
Six dye items exist. No other item name contains "dye".

| Item | id | Stackable | Tradeable | Icon | Where the definition comes from |
| --- | ---: | --- | --- | --- | --- |
| Red dye | 1763 | No | Yes | `shopitems/red_dye.png` | `data/quest/definitions/free/goblin_diplomacy.py:61-71`; also Lletya Seamstress stock |
| Yellow dye | 1765 | No | Yes | `shopitems/yellow_dye.png` | Lletya Seamstress stock (`SHOP_EXTRA_ITEM_DATA`, `data/shop_data.py:27`) |
| Blue dye | 1767 | No | Yes | `shopitems/blue_dye.png` | Lletya Seamstress stock |
| Orange dye | 1769 | No | Yes | `shopitems/orange_dye.png` | Lletya Seamstress stock |
| Green dye | 1771 | No | Yes | `shopitems/green_dye.png` | Lletya Seamstress stock |
| Purple dye | 1773 | No | Yes | `shopitems/purple_dye.png` | Lletya Seamstress stock |

Not in the registry: Pink dye (Darkan 6955), Black mushroom ink is a separate
item (4622, `herbloreitems/black_mushroom_ink.png`, made by `grind_black_mushroom`).

The Utility row icons for the dye actions are in
`core/constants_parts/skill_catalog.py:34-37` (Red dye uses
`constructionitems/red_dye.png` there; the registry icon is
`shopitems/red_dye.png`).

### How each dye is made today

All dye recipes are Utility review actions in
`UTILITY_ACTIVITY_DATA` (`core/constants_parts/activity_updates.py:26`). Each
gives 0 XP, has `batch_size` 1, and sits in group `material_processing`, which
the Utilities list labels "Material processing" (`ui/ui.py:731`).

| Utility id | Display name | Inputs | Output | file:line |
| --- | --- | --- | --- | --- |
| `aggie_make_red_dye` | Ask Aggie to make red dye | Redberries x3, Coins x5 | Red dye x1 | `core/constants_parts/activity_updates.py:285-294` |
| `aggie_make_yellow_dye` | Ask Aggie to make yellow dye | Onion x2, Coins x5 | Yellow dye x1 | `core/constants_parts/activity_updates.py:295-304` |
| `mix_orange_dye` | Mix orange dye | Red dye x1, Yellow dye x1 | Orange dye x1 | `core/constants_parts/activity_updates.py:305-314` |
| `aggie_make_blue_dye` | Ask Aggie to make blue dye | Woad leaf x2, Coins x5 | Blue dye x1 | `core/constants_parts/activity_updates.py:315-324` |
| `dye_goblin_mail_orange` | Dye goblin mail orange | Goblin mail x1, Orange dye x1 | Orange goblin mail x1 | `core/constants_parts/activity_updates.py:325-336` |
| `dye_goblin_mail_blue` | Dye goblin mail blue | Goblin mail x1, Blue dye x1 | Blue goblin mail x1 | `core/constants_parts/activity_updates.py:337-346` |

Aggie's fee is 5 Coins for each dye. No Aggie service exists outside these
three Utility rows (no shop service, no vendor action; `probe5.py` searched
`SHOP_SERVICES` and `SHOP_VENDOR_ACTIONS` for "dye", "woad", "aggie" and found
nothing).

Other ways to get dyes today:

- Buy from the Lletya Seamstress shop (`lletya_seamstress`, NPC 2353): Red,
  Yellow, Blue, Orange, Green and Purple dye, each for 6 Coins (`probe1.py`;
  `data/shop_data.py:19`). The shop is locked until Mourning's End Part I is
  started (access rule `{"kind": "quest", "quest_id": "mournings_end_part_i",
  "stage": "started"}`, from `probe2.py`; the Lletya rules are in
  `tools/generate_npc_shop_data.py:170-172` and nearby lines).
- Grand Exchange (GE) buy offers. Period GE prices: Red dye 1402, Yellow dye
  358, Orange dye 1465, Blue dye 751, Green dye 325, Purple dye 270
  (`generated/grand_exchange_period_generated.py`, for example line 535 Green
  dye 325 and line 926 Purple dye 270). Buy limit 100 for each
  (`data/grand_exchange_period_source.json:210,665,1080,1180,1247,1829`).

### Why Utilities offers only "Mix orange dye"

`mix_orange_dye` is the only mixing recipe in data
(`core/constants_parts/activity_updates.py:305`). No `mix_green_dye` or
`mix_purple_dye` row exists. The source audit scoped the slice to the quest
chain only: "This slice ... models only the quest chain: ... red-plus-yellow
orange dye mixing" (`memory-bank/source-audits/goblin-mail-dye-chain-2026-08-30.md`,
"Scope and verdict").

### Green and purple dye: what exists and what is missing

- Both items exist in the registry (ids 1771 and 1773, table above). Both are
  only reachable by the Lletya shop and the GE.
- Consumers in quest data: Recipe for Disaster: Freeing the Goblin Generals
  stage 1 takes "Blue dye x1 or Purple dye x1"
  (`generated/quest_catalog_generated.py:14775`). Land of the Goblins stage 5
  requires Yellow, Blue, Orange and Purple dye x1 each
  (`generated/quest_catalog_generated.py:21855-21863`).
- Darkan source for mixing (`darkan-world-server/src/main/java/com/rs/game/content/items/Dye.kt:29-42`):
  Red + Yellow = Orange, Blue + Yellow = Green, Blue + Red = Purple, one of
  each input consumed, one output. Darkan item ids:
  `Dye.kt:13-20` (RED 1763, YELLOW 1765, BLUE 1767, ORANGE 1769, PURPLE 1773,
  GREEN 1771, PINK 6955, BLACK 4622).
- Missing to offer Green and Purple in Utilities: two `UTILITY_ACTIVITY_DATA`
  rows in the same shape as `mix_orange_dye`, and a pinned period wiki source
  for each (the existing rows cite `ORANGE_DYE_WIKI_SOURCE`,
  `data/quest/sources.py:293`; no Green or Purple dye wiki source constant
  exists, unverified beyond a grep for `GREEN_DYE`/`PURPLE_DYE`, which found
  none). Icons already exist (`shopitems/green_dye.png`,
  `shopitems/purple_dye.png`, provenance in `assets_provenance.json:39522` and
  `:41346`).

### 2. Item-on-item use

No UI lets the player use one item on another.

- Bank drag and drop (`ui/ui.py:1464-1543`, class `_BankDropButton`) moves an
  item. A drop on a cell calls `_drop_item_on_cell`
  (`ui/ui.py:24083-24095`), which calls `move_bank_item_pure` to reorder the
  Bank. It works only in manual sort mode (`ui/ui.py:24069-24081`). A drop on a
  tab moves the item to that tab (`ui/ui.py:24097`).
- Bank right-click menu (`ui/ui_bank_menu.py:470-497`, `build_bank_item_menu`)
  offers single-item verbs: Start trail, tool belt, Wicked hood, Equip,
  consume (Eat/Drink), Break tablet, Open pack, Loot impling jar, "Convert
  Rogue kit to" a submenu (`ui/ui_bank_menu.py:352-376`), Teleport urn, Set
  carried quantity, Discard X, organise. None of these takes a second item.
- `ui/ui_dnd_favourite.py` is not drag and drop. "D&D" means Distractions and
  Diversions. The file adds a star button on the Activities detail card and a
  right-click row menu on the Activities tree. Both toggle whether the
  reviewer badge watches that Distraction, through `on_favourite_dnd`
  (`ui/ui_dnd_favourite.py:1-6, 19-80`). The logic is
  `logic/dnd_favourites_logic.py`.

Nearest existing seams for "use dye on dye":

1. A Utility recipe row (data only): add a row like `mix_orange_dye`. This is
   how the game models every item combination today.
2. The Bank right-click menu: `_add_rogue_kit`
   (`ui/ui_bank_menu.py:352-376`) is a per-item submenu that lists outputs and
   calls a handler. A "Mix with ..." submenu on a dye would follow it. Any new
   menu item changes an existing interface, so AGENTS.md needs owner approval.
3. Bank drag and drop: `_BankDropButton` already carries the source item name
   in the drop (`ITEM_MIME`, `ui/ui.py:1467`). Today the drop only reorders.

### 3. Goblin Diplomacy

### Model

- Definition: `data/quest/definitions/free/goblin_diplomacy.py:17-35`. 4
  stages, 5 quest points, reward Gold bar x1 and Crafting XP 200, free,
  Novice, no requirements, no `required_items`, `start_point` "Talk to General
  Bentnoze or General Wartface in Goblin Village."
- Journal stages: `goblin_diplomacy.py:10-15`.
- Stage requirements: `goblin_diplomacy.py:37-58`.
  - Stage 1: consumes Orange goblin mail x1 (`:39-44`).
  - Stage 2: consumes Blue goblin mail x1 (`:45-50`).
  - Stage 3: consumes Goblin mail x1 (`:51-56`).
- Items Orange goblin mail 286 (not tradeable), Blue goblin mail 287 (not
  tradeable), Goblin mail 288, Red dye 1763: `goblin_diplomacy.py:60-102`.
- The runtime quest data has no `required_inventory_options`, no
  `auto_actions` and no `produced_inventory` for this quest (`probe7.py`).
- Quest progress code: `apply_quest_progress_pure`
  (`logic_pure/logic_pure_quest.py:1176`), which calls
  `_consume_quest_current_stage_items` (`logic_pure/logic_pure_quest.py:931-951`).
  The review handler is `handle_quest_answer`
  (`runtime/runtime_actions_quest.py:181`). When the stage has a missing
  item, the review switches questing off with the blocker reason
  (`runtime/runtime_actions_quest.py:203`).

Items the quest needs: Orange goblin mail x1, Blue goblin mail x1, Goblin mail
x1 (plain, brown). That is three Goblin mails in total before dyeing.

### What the player must do today, from nothing

Probe `probe8.py` and `probe9.py` ran this chain with the real data. Starting
inputs: Redberries x3, Onion x2, Woad leaf x2, Coins x15. The end state is
Orange goblin mail 1, Blue goblin mail 1, Goblin mail 1, nothing else left.
Test `tests/test_logic.py:897` asserts the same.

| # | Step | How | Manual or automatic |
| ---: | --- | --- | --- |
| 1 | Get 3 Redberries | Utility `pick_redberries` (4 per trip, `activity_updates.py:233-245`), Farming, or GE | Manual: pick the Utility row, then reviews run it |
| 2 | Get 2 Onions | Utility `pick_onions` (28 per trip, `activity_updates.py:222-232`), Farming, or GE | Manual |
| 3 | Get 2 Woad leaves | Farming (Woad, level 25, 3 leaves per harvest, `data/farming_data.py:213`) or GE | Manual. No NPC shop sells woad (section 5) |
| 4 | Have 15 Coins | Any coin source | Manual |
| 5 | Get 3 Goblin mails | Utility `gather_goblin_mail`, "Search Goblin Village crates", 3 per trip (`activity_updates.py:187-196`); also a Goblin drop (`combat:goblin_level_11`, per the 2026-08-30 audit) | Manual |
| 6 | Red dye | Utility `aggie_make_red_dye` | Manual |
| 7 | Yellow dye | Utility `aggie_make_yellow_dye` | Manual |
| 8 | Orange dye | Utility `mix_orange_dye` | Manual |
| 9 | Blue dye | Utility `aggie_make_blue_dye` | Manual |
| 10 | Orange goblin mail | Utility `dye_goblin_mail_orange` | Manual |
| 11 | Blue goblin mail | Utility `dye_goblin_mail_blue` | Manual |
| 12 | Start the quest | Quests tab; `start_quest_pure` sets progress 0 (`logic_pure/logic_pure_quest.py:882-901`) | Manual |
| 13 | Hand in Orange goblin mail | 1 quest review (progress 0 to 2) | Automatic on review |
| 14 | Hand in Blue goblin mail | 1 quest review (progress 2 to 3) | Automatic on review |
| 15 | Hand in Goblin mail | 1 quest review (progress 3 to 4, complete) | Automatic on review |

Each Utility step needs the player to select its row; each review then
processes one batch (at speed above 1x, several batches; unverified for the
exact count per review). Steps 6 to 11 each are a separate row choice. The
action queue can chain up to 5 of them (section 6). Nothing is impossible
today, but no step happens inside the quest.

If the player starts the quest with only the raw supplies, the first quest
review cannot progress: blocker "Needs Orange goblin mail x1", and
`can_attempt_quest_review_pure` returns False (`probe8.py`). The quest then
switches off.

### 4. Quest-step automation patterns

Existing patterns a "do it for you as a step" design can follow:

1. Stage consume and produce. A quest stage can consume items and produce
   others in the same review. Example: Ernest the Chicken stage 3 "Mix fish
   food with poison for the manor fountain" consumes Fish food x1 and Poison
   x1 and produces Poisoned fish food x1
   (`data/quest/definitions/free/ernest_the_chicken.py:57-63`). The fields are
   in `_stage_req` (`data/quest/contract.py:195-213`): `consumed_inventory`,
   `produced_inventory`, `consumed_inventory_options`,
   `required_inventory_options`, `repeatable_until_consumed`, `auto_actions`.
   The runtime applies them in `_consume_quest_current_stage_items`
   (`logic_pure/logic_pure_quest.py:931-951`).
2. Item alternatives in one stage: `consumed_inventory_options`, for example
   Fishing Contest "Red vine worm or Fishing bait"
   (`data/quest/stage_overrides/members/classic/fishing_contest.py:51`). The
   runtime picks the first option the inventory holds
   (`logic_pure/logic_pure_quest.py:942-946`).
3. Conditional stage rows: Witch's House drops an acquisition from a stage
   when the player already holds the item
   (`logic_pure/quest/witchs_house.py:27-46`, `_suppress_acquisition` and
   `_conditional_stage_row`). This is the nearest pattern for "skip the Aggie
   step if you already have the dye".
4. Multi-review stage services: one journal stage that takes several reviews,
   each doing one deed (`logic_pure/quest/review_steps.py:1` "Shared review
   seam for quests whose current journal takes several reviews";
   `logic_pure/quest/review_services.py:22-86` for Oronwen, Witch's House,
   Enakhra and Watchtower). This matches "one step for each extra action".
5. `auto_actions`: strings recorded as action proofs when the stage completes
   (`logic_pure/logic_pure_quest.py:939`). They are narrative proofs; they do
   not move items.
6. Action queue quest entries: a quest entry has no count and runs until the
   quest stops (`core/action_queue.py:90-104`).

### 5. Shops and woad

### NPC shop system

- Data: `data/shop_data.py` is generated by `tools/generate_npc_shop_data.py`
  (header, `data/shop_data.py:1-4`). 273 runtime shops (`SHOP_DATA`,
  `data/shop_data.py:19`), each with `stock` rows, `buy_price`, and an
  optional `access` rule.
- Buy: `preview_shop_buy_pure` and `apply_shop_buy_pure`
  (`logic/shop_logic.py:305`, `:402`). UI: the Shop tab
  (`ui/ui_tab_shop.py:60`, `build_shop_tab`) with quantity, All and Buy
  buttons (`ui/ui_tab_shop.py:255-260`).
- Services (85, `SHOP_SERVICES`, `data/shop_data.py:21`) and vendor actions (4,
  `SHOP_VENDOR_ACTIONS`, `data/shop_data.py:23`). The Shop tab shows both in
  one list with a "Use" button (`ui/ui_tab_shop.py:328`, `:679-687`).
  - Vendor actions are dialogue purchases: `bartender_buy_beer` (2 Coins,
    Beer), `benny_buy_varrock_herald` (50 Coins, Newspaper), `karim_buy_kebab`
    (1 Coin, Kebab), `bartender_sell_beer_glass`. Hand-written in
    `tools/generate_npc_shop_data.py:234-280` (`VENDOR_ACTIONS`). A vendor
    action is one interaction per use; quantity is clamped to 1 (owner
    decision 2026-07-07, `ui/ui_tab_shop.py:323-326`).
  - `item_conversion` services take an input item plus Coins and give an
    output, for example `thakkrad_cure_yak_hide` (Yak-hide + 5 Coins to Cured
    yak-hide). Source rows: `tools/npc_shop_generation/service_rows.py:20`,
    `:140`. This is the same shape as Aggie's dye service, but Aggie is
    modelled as Utility rows instead.

### Wyson and Falador Park

- Wyson is not in AnkiScape code or data. A grep for "Wyson" in code and
  data found nothing. The only repo mention is a source audit note on his
  mole-part exchanges (`memory-bank/source-audits/farming-wiki-pin-ledger-2026-07-11.md:246,254`);
  that exchange is not implemented either.
- No shop sells Woad leaf. The Falador shops in data are
  `falador_general_store` (no woad) and `garden_centre` (bagged plants and
  hedges, no woad) (`probe3.py`).
- Falador Park exists only as a Farming tree patch
  (`data/farming_data.py:569`, `_patch("falador_tree", "Falador Park tree",
  "falador_park", "tree")`) and in quest and diary text.
- Darkan source:
  `darkan-world-server/src/main/java/com/rs/game/content/world/areas/falador/npcs/Wyson.java`.
  NPC id 36 (`:14`). "Yes please, I need woad leaves." (`:38`). Offers of 5
  or 10 Coins are refused (`:44-53`). 15 Coins gives Woad leaf x1
  (`:54-67`). 20 Coins gives Woad leaf x2 (`:68-81`). Wyson also trades mole
  parts for bird nests (`:30-37`).
- Darkan's Goblin Diplomacy journal says "I can grow woad leaves from woad
  seeds or buy them" / "from Wyson the gardner in Falador park"
  (`darkan-world-server/src/main/java/com/rs/game/content/quests/goblindiplomacy/GoblinDiplomacy.java:94-95`).
- No pinned period wiki revision for Wyson exists in the repo (unverified
  beyond a grep of `memory-bank/source-audits`).

Nearest seam for "buy woad from Wyson": a `direct_purchase` vendor action in
`VENDOR_ACTIONS` (`tools/generate_npc_shop_data.py:234`), then a regenerate of
`data/shop_data.py`. The 20-Coins-for-2 price fits `outputs` quantity 2. A
Utility review row like `aggie_make_blue_dye` with requirement Coins only is
the other option (unverified that any Utility row today has only Coins as
input and an item output; `ranging_guild` takes Coins 200 but is a minigame).

### How a player gets Woad leaf today

| Route | file:line |
| --- | --- |
| Farming: Woad flower, level 25, from Woad seed, fixed yield 3 | `data/farming_data.py:213` |
| GE buy offer, period price 23, buy limit 100 | `generated/grand_exchange_period_generated.py:1425`, `:3259` |

Woad leaf registry: id 1793, stackable, tradeable
(`data/farming_data.py:710-717`). No monster drop and no Darkan-backed drop
gives Woad leaf (grep of data and generated catalogs).

Woad seed sources: Master Farmer pickpocket (`data/thieving_data.py:95`),
Managing Miscellania seed mix (`data/managing_miscellania_data.py:70`),
Vinesweeper reward (`data/vinesweeper_data.py:61`), a Slayer finisher table
(`data/combat/slayer/slayer_finishers.py:245`).

The Woad leaf value 1 in `SHOP_PLAYER_BUY_PRICES` (`data/shop_data.py:36`) is
an item value used for alchemy (`core/constants.py:505-509`). It is not a
shop stock row.

### 6. The action queue and these actions

Queue entries hold an action record of kind `skill`, `utility`, `quest` or
`combat` (`core/last_action.py:39-44`, `_RECORD_KEYS`).

| Action | Can it go in the queue today? | Why, file:line |
| --- | --- | --- |
| Aggie dye rows, `mix_orange_dye`, `dye_goblin_mail_*`, `gather_goblin_mail`, `pick_*` | Yes | They are `utility` records (`core/last_action.py:60-64`). Count unit is the product made (`core/action_queue.py:1-9`) |
| Goblin Diplomacy quest | Yes, without a count | `core/action_queue.py:98-99`; it runs until the quest stops |
| Shop buy, shop service, vendor action | No | No record kind exists for them (`core/last_action.py:39-44`); they apply at once from the Shop tab |
| GE offer | No | Same reason; offers fill over market ticks (`logic/grand_exchange_logic.py:500`, `place_ge_offer_pure`) |

The queue holds at most 5 entries (`core/action_queue.py:56`). The full
Goblin Diplomacy chain from raw supplies is 7 Utility actions plus the quest,
so it does not fit in one queue.

### 7. Tests

All five Goblin Diplomacy tests passed on this run: "Ran 5 tests in 2.094s
OK".

| Behaviour | Test |
| --- | --- |
| Full chain from raw supplies to three mails | `tests/test_logic.py:897` `TestLogic.test_goblin_diplomacy_material_chain_uses_the_exact_quest_inputs` |
| Quest stage gates and hand-ins | `tests/test_logic.py:8175` `TestLogic.test_early_darkan_quests_progress_through_source_backed_stage_gates` |
| Quest stage data | `tests/test_quest_catalog.py:875` (inside a `TestQuestCatalog` test) |
| Recipe sources, item ids, icons, provenance | `tests/test_skill_and_item_registry.py:1096` `TestSkillAndItemRegistry.test_goblin_diplomacy_chain_preserves_period_recipes_identity_and_art` |
| Utility rows show labels, inputs, no truncation | `tests/main_menu/activities/test_navigation.py:716` `MainMenuWidgetTest.test_goblin_diplomacy_processing_rows_use_the_existing_utility_contract` |
| Answer undo for each dye action | `tests/integration_smoke/test_crafting_utility_undo.py:263` `TestIntegrationSmoke.test_goblin_diplomacy_processing_actions_roll_back_on_answer_undo` |
| Reachability baseline includes the quest | `tests/reachability/test_report_baseline.py:41` |
| Stage item options (Blue or Orange dye style) | `tests/test_logic.py:7325-7349` |
| Vendor actions | `tests/test_shop_logic.py:442`, `:1031` `test_vendor_actions_are_one_per_interaction`; `tests/main_menu/test_shop_services.py:164`; `tests/ui_flows/test_shop_locks_and_purchase.py:189` |
| Shop buy | `tests/test_shop_logic.py:259` `test_buy_live_stock_records_event_and_rollback_restores_state` |
| Queue quest entry | `tests/action_queue/test_queue_reviews.py:102` `test_a_quest_entry_ends_when_its_quest_stops_and_the_next_entry_starts`; `tests/action_queue/test_queue_state.py:81` |

## Questions this suggests for the owner

1. Mixing: add Green (Blue + Yellow) and Purple (Blue + Red) as Utility rows
   only, or also add a "use item on item" control in the Bank? The Bank
   control changes an existing interface.
2. Wyson: a Shop-tab vendor action (one purchase per click, 20 Coins for 2
   leaves), or a Utility review row that repeats each review? Offer the 15
   Coins for 1 price too?
3. Goblin Diplomacy steps: when the player holds raw supplies, must each
   missing step (Red dye, Yellow dye, mix, Blue dye, dye orange mail, dye
   blue mail) cost one quest review each, with a step skipped when its
   product is already held? The pattern exists (sections 4.1, 4.3, 4.4).
4. Must the quest also search the crates for Goblin mail, or must the player
   bring three mails ("besides having to bring the supplies")?
5. Must Aggie's dye service move to the Shop-tab `item_conversion` shape, or
   stay a Utility row?

