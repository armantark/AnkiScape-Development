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

### S1 `diary-honest-stop` — the trigger firewall (full ledger moved to §5.21)

Owner ruling 2026-08-26 23:20: the 253-row curation ledger is grinding-queue
work (design-thread-queue §5.21, kanban row), not a Pass 12 slice. Pass 12
ships only the honest-stop cut.

Root cause: `aa30c6f2:tools/generate_achievement_diary_data.py:1006-1027` converts a
task's prerequisites into its completion condition. Probe counts on
`a1c8fc90`: 474 named rows; 112 strict level-only proxies; 34 level+quest
proxies; 3 mixed rows with real deed predicates; 22 anchors; 107 latent.

**Superseded census note — 2026-08-28:** the 253-row queue estimate and the
107-latent probe category above remain exact historical figures for their
recorded states. The honest-stop catalog at
`ef860086c56a30bef05fd4f46692cb3921e38ac2` instead measures 474 named rows:
320 rows with `conditions == ()` and 154 condition-bearing rows, comprising 129
ordinary deed rows, 3 quest-deed rows, and 22 labelled anchors. The canonical
ledger therefore covers all 320 honest-stop rows, and `latent` is no longer a
current disposition.

Honest-stop scope:
1. Remove the prerequisite-as-trigger fallback in the generator. The 22
   anchors and the 3 real-predicate tasks keep firing.
2. Un-curated deed tasks present as dormant: visible, real description,
   prerequisites shown as access gates, and no completion trigger until the
   §5.21 ledger wires one. They must not fire, and they must not block the
   Taskmaster incorrectly.
3. Reference rewire, already evidenced: `falador_easy_chain_store` requires
   the Wayne's Chains purchase (`aa30c6f2:logic/shop_logic.py:1730-1766` writer,
   item 1107) plus body-slot equip; Defence 10 stays as an access gate only.
   This is the pattern the §5.21 ledger will follow.

Fix sites: `aa30c6f2:tools/generate_achievement_diary_data.py:603-1027,1309-1317`,
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
`aa30c6f2:__init__.py:378-387,1477-1486,2395-2410,5889-5895`; direct-action path
`__init__.py:1019-1083`; manual Stop `__init__.py:4482-4505` stays silent.
Automatic switches show a modal (achievement-popup style,
`ui/ui.py:4565-4597` precedent) naming the reason; the modal fires after the
review answer completes, never before the XP feedback flush
(`__init__.py:5369-5376`). One event-log entry per switch; repeated switch
while already Bankstanding is silent; guard the redundant call at
`__init__.py:2404-2408` against double-fire.
Tests: `tests/test_runtime_actions.py`, `tests/test_direct_action_undo_seam.py`,
`tests/test_integration_smoke.py:2550-2592`, `tests/test_review_strip.py`.

### S3 `carried-grid` (after S8)

Keep ownership and drop crediting unchanged (`runtime_actions_combat.py:577-639`
already folds retained loot into `carried_inventory` and banks at 28 slots).
Move the read-only Current-inventory grid below both `auto_view` and
`custom_view` (`ui/ui.py:25229-25684`); merge retained loot with
`combat_supply_loadout_summary_pure()` (`aa30c6f2:logic_pure/logic_pure_combat_engine.py:2681-2694`)
for display; Bank and Equipment copies inherit from the shared builder.
Never subtract carried quantities from Bank totals; never create a second
ledger. Pin: death routes retained loot to the grave
(`runtime_actions_combat.py:684-708`), coins stay excluded, the 28-slot bank
run clears the view, mode switches mutate nothing.
Tests: `tests/test_runtime_actions.py:2628-2736`,
`tests/test_main_menu_widget.py:3537-3809`, `tests/test_inventory_pure.py`.

### S4 `druidic-2012`

Replace the retired meat quest with the rework per ruling 4: stage list from
the pinned rework pages plus Darkan `druidic_ritual/` (reconstruction class);
delete the meat/cauldron stages and their emitted actions; save migration
maps started meat-version saves onto the new stages, forward only, and
returns any enchanted/raw quest meats it strips to the bank. Re-pin the
clean-herb level column in `data/herblore_data.py` (known: `clean_guam` 3→1)
with one citation per changed row. No ORDINARY-overworld Herblore quest gate
exists or may be added; Jungle Potion's entry gate stays, and the Daemonheim
gate (Druidic Ritual to mix potions there, oldid 6555616, implemented in
logic/dungeoneering_logic.py) stays untouched — ruled 2026-08-27 01:06. Sourcing follows the standing evidence order; the
2026-06-22 starter-stage audit is superseded for this quest and the brief
notes it there.
Tests: `tests/test_logic.py` quest stages, `tests/test_runtime_actions.py`
fixtures at 2073-2153, `tests/test_herblore_data.py`, storage migration tests.

### S5 `lamp-flow`

Two stable Stronghold claim IDs delivered to Bank Claims on chest claim
(`logic/stronghold_player_safety_logic.py:161-197`,
`logic_pure/logic_pure_claims.py:201-286`, `aa30c6f2:data/quest_data.py:11579-11601`);
derive remaining lamps from the claim records and retire `lamps_remaining`
as a competing source of truth; migrate old counts 2/1/0 deterministically.
Shared chooser `_choose_xp_lamp_skill(parent, title, eligible_skill_ids)`
beside `_exec_selection_dialog` (`ui/ui.py:28614-28617`), icon grid via
`skill_icon_path_for` (`ui/ui.py:808-845`), explicit Claim/Cancel, returns
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
the existing unload path (`aa30c6f2:logic_pure/logic_pure_combat_engine.py:2725-2735`), return
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

## Batch trace (closure, 2026-08-27)

Landed on main as merge eb04d838 (promotion head 9ddd2b1a, base bdf7d365).
Gate: both lanes 4,506 tests green (plain 410.244s skipped=512; offscreen Qt
703.870s skipped=3); docs, test-quality, worktree, diff-check audits pass;
reachability 1600 actions / 2217 reachable (+5) / 192 orphans / 284 blocked;
quest closure 40/196 completable. Final CURRENT_CONFIG_VERSION 121 with
chained migrations 119 (Druidic), 120 (lamps, self-identifying), 121 (diary).

| Slice | Author path | Commits | Review path | Result |
|---|---|---|---|---|
| S8 rune-stale-repair | workflow + severed/steered streams, reconciled | 92f07abb + ce6edbb5 | out-of-band Opus REJECT (burst-site leak into 20 bank-sealed instances, reproduced) → fixed, mutation-proven → CLOSED-WITH-NOTES | landed |
| S4 druidic-2012 | severed predecessor + interim reviewer + finishing owner | 5a6cecee + 3bd4542d | Opus ACCEPT-WITH-FINDINGS (retired-flag record, dead disjunct, citations) → fixed | landed |
| S2 bankstand-popup | workflow author + fresh fix agent | 4dce3081 + d41f6f3f | pipeline ACCEPT-WITH-FINDINGS (double modal severe) → fixed, full lanes | landed |
| S6 bigtop-visibility | workflow author + fresh fix agent | 9b23a764 + 074226e6 | pipeline ACCEPT-WITH-FINDINGS (persistence leak) → fixed, visual check | landed |
| S3 carried-grid | workflow author + fresh fix agent | aeba8d4b + 4b94b376 | pipeline ACCEPT-WITH-FINDINGS (header truncation) → fixed with fit regression | landed |
| S7 hazeel-stage0 | crash-inherited completion | 6029e977 + 0cbe2d54 | Opus ACCEPT-WITH-FINDINGS (dead branches, stale record, gate fixture) → fixed, mutation-proven | landed |
| S5 lamp-flow | crash-inherited completion | 787e385f + 395dc48c | Opus ACCEPT-WITH-FINDINGS (version-hole merge hazard) → self-identifying migration fix by orchestrator | landed |
| S1 diary-honest-stop | wrongly-stopped author, redispatched under carve-out ruling | 13b13da3 + cede17d2 | Opus ACCEPT-WITH-FINDINGS (3 HIGH: tier unclaimability ruled transitional; instrument restored; v121 stale-completion migration) → fixed | landed |

Highest-value review catch: the S8 burst-site repair reproduced emptying a
player's food pack mid-Fight-Caves. Second: the S1 resurrection hazard for
213 stale proxy completions. Known record nuance: the ce6edbb5 commit message
overstates the safe-recovery gating (a partial pack still tops up once
instantly; only an empty pack defers to the bank-run walk).
