# Pass 12 owner notes — handoff brief, 2026-08-26

Design thread: Fable, session 61069f54. Rulings ledger entry:
`memory-bank/design-thread-queue.md` §4.21. Every dispatched agent obeys
`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md` in full.

## Goal

Close the Pass 12 owner notes: honest achievement triggers across the full
diary catalog, a modal notice for automatic Bankstanding switches, the carried
grid restored on both tabs, the November 2012 Druidic Ritual, the re-pinned
clean-herb levels, the Stronghold lamp flow through Bank Claims, hidden
unmet Big Top acts, the mid-quest Hazeel choice, the Evil Tree icon, and the
stale-rune save repair.

## Owner notes (verbatim, 2026-08-26)

> Why did this get unlocked right when I got 10 defense? Also, the achievement
> doesn't even translate to Ankiscape.
> For Big Top Bonanza, the flaming poi/firebreathing/thieving magic tricks
> should only show up if the associated quest has been completed.
> Another weird untranslatable achievement that popped up when I got 15 agility
> Give me a popup when things switch to bankstanding mate
> 1. text ellipsis 2. I'd rather have a UI similar to the game where you click
> on the icon to select and confirm 3. double check what skills this specific
> lamp can be used on, and if there's a minimum level 4. when you complete this
> stronghold of player safety, it should tell you there's an xp lamp ready to
> claim (or make it go to your bank inbox, up to you) 5. make it marked as
> complete once the xp lamps are claimed
> Evil Tree has no icon under D&Ds
> Hazeel Cult seems to pop the quest branch right before you even start it; it
> should pop up as an option for you while the quest runs
> Herblore skill tab should clearly state you need to complete druidic ritual
> (double check that you need the quest to clean herbs though)
> For druidic ritual, verify that if you're meant to just get the various meats
> during the quest rather than pre-obtained
> I killed some rats and some chickens; tell me why their drops just
> immediately went to my bank without first filling up my inventory and then a
> bank run…? Never mind I see the "carried inventory" got moved to the bank
> tab for some reason, but why is it no longer a visible grid of loot+remaining
> supplies? Also, why is the 5 air + 5 mind bug still around?

Grill-round additions (2026-08-26): no latent achievement category; automatic
Bankstanding switches get a modal popup; the single-ledger carried view stands;
the carried grid lives on both the Equipment tab and the Bank tab; November
2012 quest parity for Druidic Ritual.

## Rulings

1. A deed task fires only on its deed. Level and quest prerequisites are
   access gates. The 22 labelled anchors keep level triggers. No row may be
   predicated on a deed that can never translate to AnkiScape; such rows are
   swapped for a better same-family authentic task or given a translated
   deed, now. A row whose deed awaits a plausible future AnkiScape system may
   stay dormant, but the curation ledger must already record its designed
   trigger so the row activates when its system lands. Per §4.21 (refined
   2026-08-26 23:11) and the 2026-08-03 curation contract; the ledger records
   every trigger with citation and a translation/dormant flag.
2. Automatic switches to Bankstanding show a modal popup that names the
   reason. Manual Stop is silent. Every switch writes one event-log entry.
3. One item ledger. The carried grid is a truthful view (retained loot plus
   remaining supplies), visible in both pack modes, on Equipment and Bank.
   Death sends retained carried loot to the grave; regression tests pin this
   and the other inventory consequences.
4. Druidic Ritual becomes the post-2012-01-31 rework: coin, chisel, fishing
   rod, sparkling fishing spot; no meats, no cauldron. Save migration maps
   in-progress meat-version states onto the new stage list, forward only.
   Herblore has no quest gate (Herblore oldid 6569702). Jungle Potion keeps
   its Druidic Ritual + Herblore 3 entry gate. Clean-herb levels re-pin
   against pre-cutoff pages; known drift: `clean_guam` level 3 → 1
   (Grimy guam oldid 6560041, 2.5 XP unchanged).
5. Stronghold rewards: two Antique lamps (item 12628), 500 XP each, all 25
   skills legal, minimum level 1 (Darkan `StrongholdOfSafety.java:41-64`,
   `Lamps.java`; Antique lamp oldid 6367339). Delivery is two Bank Claims
   rows. The stronghold shows COMPLETE only when the route is complete, the
   chest is claimed, and both lamp claims are claimed.
6. Big Top: The Firemaker's Curse unlocks Fire-breathing and Flaming poi;
   Some Like It Cold unlocks Thieving magic tricks (oldid 6554790). Unmet
   quest-gated acts are absent from the list, not dimmed. Suggested levels
   never gate entry.
7. Hazeel Cult: Ceril starts the quest; the side choice appears only at
   Clivet's offer, mid-quest, and is irreversible (oldid 6579784; Darkan
   `HazeelCult.java`). Unstarted quests expose stage 0 and refuse route
   mutations.

## Slices

### S1 `diary-triggers` — the full-catalog curation

Root cause: `tools/generate_achievement_diary_data.py:1006-1027` converts a
task's prerequisites into its completion condition. Probe counts on
`a1c8fc90`: 474 named rows; 112 strict level-only proxies; 34 level+quest
proxies; 3 mixed rows with real deed predicates; 22 anchors; 107 latent.

Stages, in order:
1. Author the curation ledger: one row per task needing a trigger (146 active
   proxies + 107 latent), columns task → designed trigger (semantics-contract
   predicate) → source citation → disposition flag. Dispositions: `active`
   (trigger wired now), `dormant` (deed awaits a named plausible future
   system; designed trigger recorded, activates when the system lands),
   `swapped`/`translated` (deed can never translate; replaced now). Swaps
   stay inside the source family and keep tier and durable ID. Cross-lineage
   review of the ledger before any wiring; the owner spot-checks it.
2. Wire the ledger through the generator (never hand-edit the generated
   catalog), remove the prerequisite-as-trigger fallback, keep the anchors.
3. Reference rewire, already evidenced: `falador_easy_chain_store` requires
   the Wayne's Chains purchase (`logic/shop_logic.py:1730-1766` writer,
   item 1107) plus body-slot equip; Defence 10 stays as an access gate only.

Fix sites: `tools/generate_achievement_diary_data.py:603-1027,1309-1317`,
`data/achievement_diary_catalog.py` (generated), `core/logic.py:95-147`.
Tests: `tests/test_achievement_diaries.py`,
`tests/test_achievement_diaries_integration.py`; neighbours
`tests/test_shop_logic.py`, `tests/test_achievement_diaries_ui.py`.
Required cases: Defence 9→10 alone completes nothing; purchase alone is
incomplete; purchase plus equip completes once; catalog reproducible from the
generator.

### S2 `bankstand-popup`

`_switch_to_bankstanding()` (`__init__.py:1489-1505`) becomes the single
post-acceptance transition seam with a true-transition guard. Call sites:
`__init__.py:378-387,1477-1486,2395-2410,5889-5895`; direct-action path
`__init__.py:1019-1083`; manual Stop `__init__.py:4482-4505` stays silent.
Automatic switches show a modal (achievement-popup style,
`ui/ui.py:4549-4581` precedent) naming the reason; the modal fires after the
review answer completes, never before the XP feedback flush
(`__init__.py:5566-5573`). One event-log entry per switch; repeated switch
while already Bankstanding is silent; guard the redundant call at
`__init__.py:2404-2408` against double-fire.
Tests: `tests/test_runtime_actions.py`, `tests/test_direct_action_undo_seam.py`,
`tests/test_integration_smoke.py:2550-2592`, `tests/test_review_strip.py`.

### S3 `carried-grid` (after S8)

Keep ownership and drop crediting unchanged (`runtime_actions_combat.py:577-639`
already folds retained loot into `carried_inventory` and banks at 28 slots).
Move the read-only Current-inventory grid below both `auto_view` and
`custom_view` (`ui/ui.py:25229-25684`); merge retained loot with
`combat_supply_loadout_summary_pure()` (`logic_pure_combat_engine.py:2681-2694`)
for display; Bank and Equipment copies inherit from the shared builder.
Never subtract carried quantities from Bank totals; never create a second
ledger. Pin: death routes retained loot to the grave
(`runtime_actions_combat.py:606-630`), coins stay excluded, the 28-slot bank
run clears the view, mode switches mutate nothing.
Tests: `tests/test_runtime_actions.py:2595-2703`,
`tests/test_main_menu_widget.py:3537-3809`, `tests/test_inventory_pure.py`.

### S4 `druidic-2012`

Replace the retired meat quest with the rework per ruling 4: stage list from
the pinned rework pages plus Darkan `druidic_ritual/` (reconstruction class);
delete the meat/cauldron stages and their emitted actions; save migration
maps started meat-version saves onto the new stages, forward only, and
returns any enchanted/raw quest meats it strips to the bank. Re-pin the
clean-herb level column in `data/herblore_data.py` (known: `clean_guam` 3→1)
with one citation per changed row. No Herblore quest gate anywhere; Jungle
Potion's entry gate stays. Sourcing follows the standing evidence order; the
2026-06-22 starter-stage audit is superseded for this quest and the brief
notes it there.
Tests: `tests/test_logic.py` quest stages, `tests/test_runtime_actions.py`
fixtures at 2073-2153, `tests/test_herblore_data.py`, storage migration tests.

### S5 `lamp-flow`

Two stable Stronghold claim IDs delivered to Bank Claims on chest claim
(`logic/stronghold_player_safety_logic.py:161-197`,
`logic_pure/logic_pure_claims.py:197-282`, `data/quest_data.py:11579-11601`);
derive remaining lamps from the claim records and retire `lamps_remaining`
as a competing source of truth; migrate old counts 2/1/0 deterministically.
Shared chooser `_choose_xp_lamp_skill(parent, title, eligible_skill_ids)`
beside `_exec_selection_dialog` (`ui/ui.py:28640-28643`), icon grid via
`skill_icon_path_for` (`ui/ui.py:805-842`), explicit Claim/Cancel, returns
the stable skill id; both callers (`ui/ui.py:18060-18077`, 26506-26520)
keep their own eligibility computation. Completion per ruling 5; fix the
header clipping (`ui/ui.py:17913-17923`) and the 188px dialog title elision.
A terminal notice says the chest is ready; chest claim announces the lamps.
Tests: `tests/test_stronghold_player_safety.py`,
`tests/test_main_menu_widget.py:19370-19451,10285-10308`,
`tests/test_dialog_lifecycle.py:82-113`, `tests/test_storage_pure.py`.

### S6 `bigtop-visibility` + Evil Tree icon

Add a pure visibility projection on quest-gate completion
(`logic/circus_logic.py:425-481`); populate the combo from visible rows
(`ui/ui.py:14834-14838,15056-15096`); keep all execution checks; keep
weekly-done rows visible. Do not add the quests to the parent activity
requirements. Evil Tree: set
`icon_path=_ACTIVITY_GROUP_ICONS["distractions_and_diversions"]` on the
manual row (`ui/ui.py:20037-20046`); assert the icon is non-null.
Tests: `tests/test_circus.py:37-115`,
`tests/test_main_menu_widget.py:17596-17763,12425-12513`;
neighbour `tests/test_undo_seam_circus.py`.

### S7 `hazeel-stage0`

Unstarted quests expose stage 0 and no choices
(`logic_pure/logic_pure_quest.py:361-368`); pre-start
`apply_quest_route_choice_pure()` refuses without mutating. Correct the
tests that enshrine the pre-start choice
(`tests/test_logic.py:5782-5806,5867-5885`,
`tests/test_main_menu_widget.py:9236-9253`). Single-valued auto-step routes
stay unchanged; Shield of Arrav branch tests are the neighbour guard.

### S8 `rune-stale-repair` (before S3)

Storage repair resolves the effective combat class on load; when no encounter
is active and the persisted loadout is class-incompatible, unload it through
the existing unload path (`logic_pure_combat_engine.py:2725-2735`), return
exact quantities to the bank, and refill for the effective method. With an
active saved encounter, leave the loadout untouched and reconcile on
encounter end. Class-gate the summary projection as defense in depth.
Convert the test that asserts the stale phrase
(`tests/test_main_menu_widget.py:6904-6940`) into a repair regression.
Repair site: `core/storage_pure.py:2440-2448`.
Tests: fresh melee shows no runes; stale melee migration returns 5+5 to bank
once; magic staff + Wind Strike still loads; Vengeance stays magic-only.

## Coordination

- `ui/ui.py` is touched by S2, S3, S5, S6; hunks are distant but authors
  must declare their line ranges in the slice report.
- `core/storage_pure.py` migrations: S4, S5, S8 — serialize these three
  migrations in that landing order to keep version numbering linear.
- `tests/test_main_menu_widget.py` and `tests/test_logic.py` are shared;
  merge conflicts there are expected and mechanical.
- S8 lands before S3 (the merged grid must not display stale runes).
- S1's ledger authoring is the long pole and blocks nothing else.

## Verification

Per slice: focused suites plus neighbours, both lanes where UI changes.
Promotion: `tools/promotion_gate.py` on the merged tree, one batch, with the
five audits, after re-absorbing `main`.
