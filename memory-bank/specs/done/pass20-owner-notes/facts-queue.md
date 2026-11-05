# Pass 20 queue fact-finding

**OBSERVED — scope and evidence.** Research began at `75f33bee9b91805555ebcaa16460635e4604d945`. An external documentation commit advanced the shared checkout to `7873ba1901b45e3074c62ec87d4fbe2fb1a1c963`; `git diff --name-only` showed only Memory Bank files changed, with no changes to the production Python or test sources used below. No repository edit, commit, worktree, Anki launch, profile database access or owner-save access was performed by this research. Probe writes were restricted to `/tmp/pass20-facts/queue/`; the Python audit guard rejected write canaries outside that directory with `Write outside scratch blocked`. All Python ran with `PYTHONDONTWRITEBYTECODE=1`.

**READ — citation base.** Source references below are `file:line` within `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`. Candidate changes are inferences from the cited code, not implemented or verified fixes. Full report: [report.md](/tmp/pass20-facts/queue/report.md).

## 1. Reorder

**READ — current behavior.** The action queue has no reorder control. Its header has a fold button, Resume queue and Clear queue (`ui/ui_action_queue.py:308–328`); each row has a state label, text label and Remove button (`ui/ui_action_queue.py:349–368`). There is no drag handle, hover-only reorder affordance or context menu in this widget. The command dispatcher accepts only add, clear, resume and remove (`core/action_queue.py:359–372`). The player cannot discover a reorder action because none is implemented.

**OBSERVED — offscreen reorder attempt.** The shown menu's queue row children were only `QLabel`, `QLabel`, `QToolButton`, repeated per row; `acceptDrops()` was `False`. Dragging row 2 onto row 1 produced `DRAG_SECOND_ROW_TO_FIRST {'unchanged': True, 'commands': [('add', {'action': {'kind': 'skill', 'skill': 'Herblore', 'target': 'clean_ardrigal'}, 'count': 3})]}` and dispatched no move command. Evidence: `/tmp/pass20-facts/queue/ui_held.log`; the exact output includes the earlier Add command, with no command added by the drag.

**READ — original note.** The actual RTFD contains “Make it so you can easily reorder the queue with common UI affordances” under Pass 18. Source: `/Users/ArmanTarkhanian1/Downloads/ankiscape notes.rtfd`, extracted to `/tmp/pass20-facts/queue/owner-notes.txt:284–294`.

**READ — history.** A Pass 18 grill answer about reorder was **not found** in `memory-bank/specs/done/pass18-owner-notes/grill-decisions.md:14–142`. Its recorded questions cover exact counts, ended entries, Clear, queue height/folding, add feedback, quest supplies, dyes, woad, arrows, GE, Bank and the supply-step backlog. The adjacent answer about queue layout is: “4. Yes, I guess make it collapsible if space is truly an issue” (`grill-decisions.md:40–44`). That is not approval of a particular reorder design. The shipped spec's queue decisions likewise do not implement reorder (`spec.md:133–190`).

**READ — cause and smallest candidate change.** Reorder is absent at both the widget and command layers, rather than merely hidden. A move command plus visible Up/Down controls on pending rows is the smallest local addition suggested by these seams. This is a source-derived candidate, not a tested fix. **Player-visible choice:** whether the running first entry can move (interrupting it), or only pending entries; whether the owner wants buttons, dragging, or both. Current progress lives once at queue level (`core/action_queue.py:95–98`), so moving a running entry also needs an explicit progress rule.

## 2. Hand-started action ahead of a queue

**READ — current behavior.** “Set aside” is descriptive wording, not a separate saved state: the saved queue contains `entries`, `done`, `paused` (`core/action_queue.py:75–99`). A hand-started action does not immediately pause it. On the next review, `QueueCount` compares the running action and first entry, sets `paused=True` on mismatch, and stops counting the queue (`core/action_queue.py:445–459`). Action identity includes target (`core/action_queue.py:152–156`); starting the same skill/target as entry 1 does not create a distinct override.

**READ — end conditions.** A hand-started skill has no queue count or separate count limit. Herblore stops when materials, level or unlock checks fail (`runtime/runtime_actions_production.py:593–626`); a quest stops on completion (`runtime/runtime_actions_quest.py:267–276`); manual Stop goes through `core/action_queue.py:377–408`. An indefinitely renewable action has no generic completion event. A paused queue does not take over any of these stops: the stop handler returns immediately when `paused` is true (`core/action_queue.py:537–541`), so the action lands at Bankstanding instead. Resume queue explicitly restarts entry 1 with its existing progress (`core/action_queue.py:346–356`). Clear drops all entries and stops even a hand-started action (`core/action_queue.py:326–337`).

**READ — end-condition details.** The visible number box belongs only to Add to queue; Train this skill calls the skill start without reading that number (`ui/ui.py:20899–20901`, `ui/ui_action_queue.py:218–220`).

| Hand-started action ends by | Current result |
| --- | --- |
| A chosen count | No generic hand-start count exists; queue counts apply only to a running entry. |
| Supplies out / requirement lost | The next attempted action that detects the failure stops at Bankstanding; the queue stays paused. |
| Quest complete | Quest becomes permanently complete; the hand-started action stops at Bankstanding; the queue stays paused. |
| Finite activity/session end | Its automatic stop uses the same stop hook; a paused queue is ignored (`__init__.py:5142–5143`, `core/action_queue.py:537–541`). |
| Manual Stop | Stops at Bankstanding without an automatic-stop dialog, retaining the paused queue (`core/action_queue.py:377–408`). |
| No end: unlimited gathering/training | Continues indefinitely; there is no generic automatic return point. |

**OBSERVED — supplies-out and add takeover.** In the real review-handler probe, cleaning the only grimy snake weed set `paused: True` and made one Clean snake weed; the next review returned `active: 'Utilities'`, `utility: 'bankstanding'`, and `bankstanding_dialogs: ['You need 1 Grimy snake weed to make Clean snake weed.']`. A subsequent valid add returned `ADD_RESULT ''`, changed active to Mining, and set `paused: False`, retaining entry 1. Evidence: `/tmp/pass20-facts/queue/runtime_probe.log`.

**READ — remaining state transitions.** Resume queue clears pause only if starting entry 1 succeeds; a refusal leaves it paused (`core/action_queue.py:346–356`). The HUD Resume button resumes that queue entry only when the saved last action matches it; otherwise it resumes the last hand-started action (`core/action_queue.py:418–430`). Removing a pending entry preserves current progress; removing paused entry 1 resets progress for its successor; a running entry 1 cannot be removed (`core/action_queue.py:142–149`). Invalid/full/zero-count adds refuse before takeover; if every entry fails to start during a valid add, the entries are passed, an explicit “could not start” result is returned, and the previous hand-started action keeps running (`core/action_queue.py:226–268`, `302–323`).

**READ — Pass 19 add rule.** Every add starts entry 1 if the queue is new, paused or running a different action; a running queue only appends (`core/action_queue.py:301–323`). “Restart from entry 1” means run its saved remaining count, not reset `done`. The original record says: “An add now starts the queue at once, in place of whatever runs, unless the queue already runs its first entry; a paused queue, and a queue set aside by a hand-started action, restart from entry 1” (`memory-bank/specs/done/pass19-owner-notes/run-record.md:27–39`).

**READ — cause and smallest candidate change.** Manual pause and temporary hand-started override share one `paused` flag, and the automatic-stop hook deliberately ignores both. Distinguishing an override that should return automatically from an explicit Stop would permit returning on supplies-out or quest-complete without making manual Stop restart work. This is a source-derived candidate, not a tested fix. **Player-visible choice:** how to bound “Train this skill” for an action with no natural end (until supplies out, a chosen count, or until manually stopped), and whether manual Stop returns to the queue or leaves everything stopped.

## 3. Target-click and count glitches

**READ — selection path.** A target mouse click or activation checks whether the row is enabled, then calls the setter and marks the row current only if its callback does not return `False` (`ui/ui.py:5320–5336`, `5344–5355`; flat-list equivalent `5207–5221`). The selector wraps the setter in `not held_by_queue(...) and select(target)` (`ui/ui.py:5372–5375`). Without an active entry on that surface, the real Herblore callback writes `current_herblore` (`__init__.py:4154`), and the setter updates the HUD, which emits the queue refresh signal (`__init__.py:4370–4385`, `ui/ui.py:3982–3989`). Merely moving the current row updates details, not the target setter (`ui/ui.py:5344–5355`).

**OBSERVED — same-surface queued training cannot be replaced through its header.** In an offscreen 900×560 menu, an actual Qt mouse click on Clean ardrigal while the first entry trained Clean snake weed produced:

```text
MENU_AFTER_CLICK {'saved': 'clean_snake_weed', 'utility': 'search_marshy_jungle_vines', 'record': {'kind': 'skill', 'skill': 'Herblore', 'target': 'clean_ardrigal'}, 'count': 3, 'herblore_calls': [], 'utility_calls': [], 'row_text': 'Clean ardrigal (Lvl 3)', 'buttons': [('Currently training', False)]}
ADD_HELD_TARGET [('add', {'action': {'kind': 'skill', 'skill': 'Herblore', 'target': 'clean_ardrigal'}, 'count': 3})]
```

The real menu widget ran against an in-memory save and setter callbacks that mirror the production write-and-notify behavior; it did not use Anki. Evidence: `/tmp/pass20-facts/queue/ui_probe.py`, `/tmp/pass20-facts/queue/ui_held.log`, `/tmp/pass20-facts/queue/held.png`.

**READ — cause.** Holding the pick protects the running queue entry (`ui/ui_action_queue.py:230–241`), and returns `False` through the boolean wrapper, so it does not mark the clicked row current. The only header action that applies a held pick is `_set_active` (`ui/ui.py:5081–5084`), but that button is disabled whenever the skill name already equals the active skill, without comparing targets (`ui/ui.py:20863–20868`). **Smallest candidate change:** distinguish a held different target from the currently trained action when enabling Start, and distinguish a previewed queue target from a persisted current target. **Player-visible choice:** should a row click itself interrupt the queue, or should it preview the next target until an enabled Start click confirms the interruption?

**OBSERVED — Utilities has the same hold problem after its quest unlock.** Repeating the utility probe with Jungle Potion completed enabled Search jungle palm trees. The click changed the Add record to `search_jungle_palm_trees` while the saved utility remained `search_marshy_jungle_vines`, and the header still showed `('Currently active', False)`. Add then queued palm trees. Evidence: `/tmp/pass20-facts/queue/ui_utility_completed.log`. **READ — cause:** the utility selection path also holds the target while a queue entry on its surface exists (`ui/ui.py:19303–19314`), and uses the same disabled active-surface header. This confirms the hold problem independently of a locked search row.

**READ — why 0 appears.** Defaults deliberately use the Bank's current input limit; actions without input limits default to 28 (`core/menu_action_queue.py:122–138`, `170–188`). Clean snake weed requires one Grimy snake weed (`data/herblore_data.py:152`), so none in the Bank yields 0. Promised output from earlier queue entries appears in the materials line but does not increase the default (`core/menu_action_queue.py:141–158`, `183–186`). This exact zero-default behavior is asserted by the existing Smithing widget test (`tests/main_menu/test_action_queue_panel.py:121–126`).

**OBSERVED — untouched default does not update when supplies arrive.** Direct offscreen control probe output:

```text
COUNT_EMPTY_BANK 0 Grimy snake weed: 0 in Bank
COUNT_AFTER_ONE_HERB_ARRIVES {'shown': 0, 'fresh_default': 1, 'materials': 'Grimy snake weed: 1 in Bank'}
REBUILT_AFTER_ZERO_ADD {'shown': 0, 'fresh_default': 1}
```

(The live Qt label uses a nonbreaking space before “Bank”.) Evidence: `/tmp/pass20-facts/queue/ui_count.log`.

**READ — distinct causes and smallest candidate changes.** `QueueAddControl.refresh` sets the count only when the action record changes, not when its available inputs change (`ui/ui_action_queue.py:200–206`). It cannot distinguish an untouched auto-default from an intentional typed count. Tracking that distinction would allow untouched defaults to follow supply changes while preserving the player's count. Separately, `MenuQueue` remembers the requested count before knowing whether Add succeeded (`ui/ui_action_queue.py:126–130`); an unsuccessful 0 add is remembered and restored on rebuild. Remembering only accepted positive counts would prevent that persistence. **Player-visible choice:** whether 0 remains a valid visible empty-Bank default, or an addable positive default is shown even before earlier entries make the supplies; the count must still permit planning more than the current Bank holds.

**OBSERVED — ordinary clicks work; a second hold-state mismatch exists.** Without a queue, the same real ardrigal click produced `saved: 'clean_ardrigal'`, `count: 3`, `herblore_calls: ['clean_ardrigal']`, and `row_text: '✓ Clean ardrigal (Lvl 3)'` (`/tmp/pass20-facts/queue/ui_normal.log`). With a still-unpaused first Herblore entry but Mining actually active, the click instead produced `saved: 'clean_snake_weed'`, `record: {'kind': 'skill', 'skill': 'Herblore', 'target': 'clean_ardrigal'}`, `herblore_calls: []`, and `('Train this skill', True)` (`/tmp/pass20-facts/queue/ui_mismatch.log`). **READ — cause:** the hold predicate inspects queue surface and `paused`, but does not compare the actual running action (`core/menu_action_queue.py:60–71`); a manual switch is not marked paused until the next review (`core/action_queue.py:274–275`, `445–457`). **Smallest candidate change:** use the actual queue-running predicate when deciding whether to hold a target, or settle the queue's interruption at the manual start. **Player-visible choice:** whether selecting a target in an inactive panel should merely preview it or save that panel's next target.

**OBSERVED — Utilities' Jungle search rows are locked during the quest.** With Jungle Potion started at progress 2, Search jungle palm trees was disabled; its tooltip ended `Locked due to: Jungle Potion`. A real mouse click left both the saved utility and Add record at `search_marshy_jungle_vines`. This is a different reason a click cannot change the action (`/tmp/pass20-facts/queue/ui_utility.log`). **READ — cause:** these five Utilities searches deliberately require completed Jungle Potion (`data/quest/ledger.py:122–129`); the quest itself produces each grimy herb during its current repeatable stage (`data/quest/definitions/members/jungle_potion.py:59–119`). Disabled Utility clicks return before changing anything (`ui/ui.py:19376–19378`). Herblore cleaning rows likewise disable on missing materials or other requirements (`core/target_metadata.py:935–954`, `logic_pure/logic_pure_production.py:486–505`). **Smallest candidate change:** no unlock change is warranted by this observation. If locked rows should support future queue planning, separate the queue preview from training eligibility; disabled Herblore clicks already show the clicked details before refusing selection (`ui/ui.py:5326–5331`), so those details can disagree with the old Add target. **Player-visible choice:** whether a locked row can still be selected for future queue planning, while remaining unavailable to train now. A Farming-row reproduction was not run; the Utilities example satisfies that branch of the request.

## 4. Quest finished ahead of the queue

**OBSERVED — reproduced through the real review handler.** The scratch fixture used the production `on_answer_card` path with Anki modules replaced by in-memory test fakes. The queue was Mining 100 → Jungle Potion → Smithing 5; the quest was started by hand through `on_set_quest` followed by `save_skill('Quests', None)`, matching the menu's two-step selection/start (`ui/ui_tab_quests.py:353–356`). The fixture supplied one of each clean jungle herb, then reviewed until the quest completed. Output:

```text
QUEST_OVERRIDE_COMPLETED
active: Utilities; current_utility: bankstanding
quests.jungle_potion: {'started': True, 'completed': True, 'progress': 6}
action_queue: Mining 100 → Jungle Potion → Smithing 5; done: 0; paused: True
RESUME_QUEUE True
QUEST_COMPLETED_STILL_IN_RESUMED_QUEUE
active: Mining; action_queue: Mining 100 → Jungle Potion → Smithing 5; paused: False
```

This is a selected-field transcription of `/tmp/pass20-facts/queue/runtime_probe.log`; the full dictionaries are in that log.

**OBSERVED — paused entry 1 is affected too.** Stopping a first Jungle Potion entry, then starting that quest by hand and finishing it, produced `PAUSED_FIRST_QUEST_FINISHED_BY_HAND`: completed progress 6, active Bankstanding, `paused: True`, and entries still Jungle Potion → Mining 100. Evidence: `/tmp/pass20-facts/queue/runtime_probe.log`.

**OBSERVED — control case.** When Jungle Potion was the first running queue entry, finishing it removed it and started Mining: `active: 'Mining'`, `entries: [Mining 100]`, `done: 0`, `paused: False`. Starting that same first quest by hand while the queue was already running also removed it correctly. Thus the defect depends on queue ownership/pause or position, not merely on pressing a quest Start button.

**READ — cause.** Completion only settles entry 1 through the stop hook, and that hook refuses to act on a paused queue or an action different from entry 1 (`core/action_queue.py:537–552`). Neither the queue reader nor record validation checks the persistent quest-completed flag (`core/action_queue.py:79–99`, `core/last_action.py:80–91`). The check for a completed quest in `queue_add_refusal_pure` protects new adds only (`core/action_queue.py:286–297`). A completed quest is eventually passed as “it could not start” when it reaches the front (`core/action_queue.py:226–238`, `core/last_action.py:158–160`), rather than removed at completion with a done line.

**READ — smallest candidate change.** Reconcile quest-completed state against all queue entries in the same review transaction that completes a quest, including paused entries. Keep the existing running-entry completion hook for successor startup, avoid duplicate done events, and reset the shared `done` only if removing entry 1. **Player-visible choice:** whether all duplicate entries for a permanently completed quest disappear together; whether a paused queue stays paused after pruning (separate from the temporary-override return rule in question 2).

**OBSERVED — count entries have a different meaning.** With Mining 100 → Smithing 1 queued, hand-started Smithing made an Iron bar but left the pending Smithing 1 entry unchanged and the queue paused (`MANUAL_SMITH_MADE_PENDING_COUNT` in the same log). **READ — why this is not identical to quest completion:** skills, Utilities, combat and review-count entries have no global completed flag. A count is additional work measured while its entry runs; `QueueCount` tracks only the active first entry and ignores paused queues (`core/action_queue.py:445–459`, `468–495`). Existing Bank holdings do not complete it. Automatically crediting manual output to pending entries would be a new rule, especially with duplicate matching count entries; it is not the same reconciliation as deleting a completed quest.

## 5. Ended-action and menu notices

**READ — source of the quoted quest message.** `_announce_quest_completion` emits it unconditionally after the quest stop request (`runtime/runtime_actions_quest.py:106–119`, `270–276`). Optional Bank Claims lamp information is inserted before the final sentence.

**READ — complete set found for notices that explicitly tell the player to reopen/pick through AnkiScape after stopping an action:**

| Notice | Exact message template and source | Queue continues? | Queue paused/set aside? |
| --- | --- | --- | --- |
| Quest complete | `<quest> is complete, so questing has been switched off. ` + optional lamp notice + `Open the AnkiScape menu to pick another quest.` (`runtime/runtime_actions_quest.py:114–119`) | Yes; unconditional after stop handling | Yes |
| Activity locked | `<activity> requires <requirements>, so it's been switched off. Open the AnkiScape menu to pick another activity.` (`runtime/runtime_actions_utility.py:781–787`) | Yes; no queue check | Yes |
| Activity switched off | `<activity> can't run right now, so it's been switched off. Open the AnkiScape menu to pick another activity.` (`runtime/runtime_actions_utility.py:797–803`) | Yes; no queue check | Yes |
| Wilderness confirmation required | `Combat has been switched off. Reopen AnkiScape, review the current kept/lost equipment preview, and confirm this Wilderness target.` (`runtime/runtime_actions_combat.py:501–509`) | Yes; no queue check | Yes |

**READ — related generic terminal notice.** The Bankstanding dialog is titled “Switched to Bankstanding”, shows “Now Bankstanding”, the stop reason, and “Choose a new action when you are ready to continue.” (`ui/ui.py:4422–4458`). It is not emitted when the queue successfully starts a successor: `record_bankstanding_stop` returns `None`, and the switch returns before creating a pending notice (`core/action_queue.py:571–583`, `__init__.py:1302–1312`). It can be emitted when a hand-started action ends with a paused queue. A handler's own error dialog suppresses the extra generic dialog, but not its own misleading instructions (`__init__.py:1057–1068`, `1256–1269`).

**OBSERVED — queue continuation still emits the quoted quest dialog.** The same review that removed Jungle Potion and selected Mining recorded:

```text
errors: [('Quest complete', 'Jungle Potion is complete, so questing has been switched off. Open the AnkiScape menu to pick another quest.')]
bankstanding_dialogs: []
QUEUE_QUEST_LOG ['Jungle Potion 2/6', 'Jungle Potion 3/6', 'Jungle Potion 4/6', 'Jungle Potion 5/6', "+775 XP · Herblore · −1 Clean rogue's purse", 'Queue: Jungle Potion done', 'Jungle Potion complete']
```

Evidence: `/tmp/pass20-facts/queue/runtime_probe.log`. For the other three templates the continued/paused behavior is **READ**, not independently runtime-reproduced: each uses the same unconditional error callback after `deactivate_current_skill`.

**READ — what the queue itself emits on entry end.** A counted entry reaching its target logs `Queue: <name> done` before a successor starts; no generic Bankstanding notice is created. If there is no successor, it switches with `Queue finished after <name>.` (`core/action_queue.py:499–523`). For an automatic refusal/shortage, the stop hook logs `Queue: <name> stopped · <reason>` and starts a successor; a quest whose completed flag is true logs `done` instead (`core/action_queue.py:529–558`). When no successor remains after that kind of stop, the original stop and its own notice proceed. A paused queue is not a separate old-style waiting mode: the saved schema is `entries/done/paused`; Pass 19 removed the former waiting behavior (`core/action_queue.py:75–99`; `memory-bank/specs/done/pass19-owner-notes/run-record.md:27–39`).

**READ — cause and smallest candidate change.** Action handlers emit the same wording after stopping, without inspecting whether the queue started something else; the queue stop mechanism communicates no transition result back to the handler (`__init__.py:1064–1068`). Keep completion, blocker and lamp facts, and condition only the “switched off / open menu” instruction on the actual resulting action/queue state. This is a source-derived candidate, not a tested fix. **Player-visible choice:** whether successful completion in a continuing queue still gets a modal, or just its existing completion feedback and Event log; a real blocker must retain its reason.


## Adjacent findings

- **READ — Farming already has separate queue reorder buttons.** Its own queue has visible Up, Down and Remove controls and a `queue_move` command (`ui/ui.py:6480–6515`). These do not reorder the cross-skill action queue. This is an existing local UI convention, not a missing dependency.
- **READ — “Now” can be temporarily inaccurate.** The queue panel labels entry 1 “Now” whenever `paused` is false (`core/menu_action_queue.py:197–214`). A manual switch leaves it false until the next review, so the box can say Now while another action runs. The observed pre-review hand-start snapshot retained `paused: False` while Herblore was active and Mining was entry 1 (`/tmp/pass20-facts/queue/runtime_probe.log`).
- **READ — count defaults use Bank inputs, not promised inputs.** A queued gathering step can promise the herb, but a later cleaning control still defaults to 0 until the Bank actually holds it (`core/menu_action_queue.py:122–158`, `170–188`). This is deliberate existing behavior, distinct from the stale untouched-default defect.
- **READ — final counted entries do not get the same done log line.** `QueueCount.hand_over` writes `Queue: <name> done` only when a successor exists; the final entry instead leaves `Switched to Bankstanding · Queue finished after <name>.` (`core/action_queue.py:517–523`; the expected log in `tests/action_queue/test_queue_reviews.py:83–91`).
- **READ — same-surface queue takeovers can leave the menu's panel stale.** `queue_changed_what_runs` compares only the surface name except for Quests (`ui/ui_action_queue.py:67–73`), and the post-command callback rebuilds the panel only when that comparison succeeds (`ui/ui.py:4873–4880`). Starting another target within the same skill can therefore update saved action/queue controls without rebuilding target markings. This adjacent path was not independently runtime-reproduced.
- **READ — other “switched off” wording exists without a menu instruction.** Quest unavailable (`runtime/runtime_actions_quest.py:236–241`), quest blocked (`core/last_action.py:142–147`), and skill/tool/level notices in the production/gathering handlers share that wording class. The table in question 5 is the complete set found with an explicit menu/reopen instruction; it does not claim those other stop reasons are absent.
