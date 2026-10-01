# Pass 15 owner notes — slice brief, 2026-09-30

Rulings: `memory-bank/design-thread-queue.md` §4.28. Every implementation agent
obeys `memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md` in full. The
orchestrator seat (Opus 5.5, session 61069f54) dispatches Opus 5.5 authors,
merges the accepted slices in one integration worktree, and runs the promotion
gate with `--remote-lanes`. The owner asked for Opus 5.5 as the main author:
"Use primarily Opus 5.5 for where it matters".

## Owner notes (verbatim, `~/Downloads/ankiscape notes.rtfd`, Pass 15, 2026-09-15 to 2026-09-30)

> 1. Good that the final hit was blocked for not wearing spiked gauntlets but this should be more obvious somehow (also the text is truncated)
> 2. I'm stuck on bank run trying to switch to tuna/swordfish fishing but I'm still getting hp:
> 3. The slashes are not accurate
> 4. I need to be able to equip silverlight as a weapon. Also, I did demon slayer and there was no combat sequence for fighting Delrith. Same with Vampyre Slayer
> 5. I don't think you should have to literlaly go through the shop UI and buy every single one. It should just be a step for each one to complete the miniquest.
> 6. I just remembered that we made many tools (like the fishing rod/nets) implicit to the toolbelt, but there's no affordance for that. We should have something, even if they're on there by default
> 7. The shops that are locked behind quests should not show up at the top in the search results and should be grayed out, and in the main list too they should be grayed out
> 8. Better, more visual confirmation that your purchase was successful. there's the green text at the bottom if you scroll but it's not very visible. I give Opus 5.5 permission to fix this
> 9. For quests that require tools, make sure it detects when it's on the toolbelt (unless it's something in the real game that specifically requires for it to be in your inventory). e.g. probably Druidic Ritual which asked me for a fishing rod. Not sure if that's actually required to be in the inventroy
> 10. Where is the search UI inside the skills actions/targets list?

Screenshots: note 1, the review HUD line "Gelatinous abomination • Finisher
blocked: no loaded Sp" cut at the card edge; note 2, "Bank run queued" over
"+80 XP · Fishing" lines; note 3, the Fishing skill guide rows "16 Catch
mackerel/cod/bass" and two "Catch slimy eel" rows; note 5, the dialog
"Alfred Grimhand's Barcrawl is blocked: Action required: Drink ... Questing has
been switched off until this is resolved."

## Constraints every slice meets

- slop-gate refuses a commit that grows any code file already above 1000
  lines (`ui/ui.py` 29293, `ui/ui_tab_shop.py` 1831, `__init__.py` 5744,
  `logic_pure/logic_pure_quest.py` 1581, `runtime/runtime_actions_production.py`
  1446, `logic_pure/logic_pure_combat_model.py` 2815,
  `tools/generate_equipment_data.py` 1460 at 2026-09-30). Hold such a file at
  net zero or below: move a nearby self-contained block into a new module in
  the same package. It also refuses cyclomatic or cognitive complexity above
  15 and Halstead difficulty above 80 in a touched function;
  `python3 tools/maintenance/function_metrics.py` measures a function exactly
  as the hook does. It refuses a new code file in a directory that already
  holds 40 (`logic/` 87, `data/` 104, `tools/` 137, `logic_pure/` 39 of 40).
- Never set `SLOP_GATE_*`, never `--no-verify`.
- A slice that changes what the player sees gets an offscreen Qt check per
  `.claude/rules/qt-offscreen-screenshots.md` at 560 px tall, with
  `text_fit_defects` clean, and one line in `memory-bank/play-checklist.md`.

## Slices

### S1 `finisher-notice` (note 1)

A worn finisher reads as worn. `combat_finisher_state_pure`
(`logic_pure/logic_pure_combat_model.py:1953-1974`) passes `worn` from
`must_be_worn` (`data/combat/slayer/slayer_creatures.py:322-327`).
`_combat_hud_status` (`logic_pure/logic_pure_combat_hud.py:93-104`) says
"Wear Spiked gauntlets to finish" for a worn finisher and keeps "Finisher
blocked: no loaded X" only for pack items. The finisher text leaves
`target_lbl` and shows on its own amber line in the combat card, in the style
of `world_notice_lbl` (`ui/ui.py:2879-2890`); every finisher message fits the
340 px card. The tooltip "No Spiked gauntlets is loaded in the combat pack."
(`ui/ui.py:7620-7622`) and the target row "· 0 loaded"
(`core/target_metadata.py:1647-1651`) use worn wording for worn finishers. The
event log gets one line per encounter when a fight ends with the enemy held at
1 LP and no automatic finisher (`result["finisher_ready"]`,
`runtime/runtime_actions_combat.py` near 560). Test: a Gelatinous abomination
scene, blocked and ready, in `tests/ui_flows/test_slayer_progress.py`, run
through `text_fit_defects`.

### S2 `bank-trip-target-switch` (note 2)

The Grand Exchange fill origin is gone since `5d7f30df`, and `0d606cfd`
stopped the HUD showing a trip for another target. Remaining defect: a target
switch leaves `skilling_bank_run_requested`, `review_bank_run_requested_target`
and `review_bank_run_requested_handler` naming the old target, so a surprise
trip fires the next time that target runs. A target switch cancels a pending
request that names a different target (`_set_values`, `__init__.py:4648-4655`).
The latest command wins. Change the pins at
`tests/runtime_actions/test_bank_run_request_target.py:28-49` and
`tests/test_runtime_actions.py:5558-5572`.

### S3 `fishing-guide-levels` (note 3)

The Stats skill guide shows one row per fish at that fish's own level, named
"Catch <fish>" (for example "16 Catch mackerel", "23 Catch cod", "46 Catch
bass"); a fish already listed is not repeated (`logic/skill_guide_logic.py:85-112`).
The target picker keeps its combined rows. Data, from pinned 2012 revisions
(Slimy eel oldid 6112771, Frog spawn oldid 6358408, Raw cave eel oldid
6359511): slimy eel is level 28 (`data/fishing_data.py:134`). Lumbridge Swamp
Caves rod and bait catches slimy eel and cave eel; Lumbridge Swamp Caves small
net catches frog spawn; Mort Myre rod and bait catches slimy eel and cave eel
behind Priest in Peril. Keep target ids `catch_slimy_eel` and
`catch_cave_eel` (`data/quest/ledger.py:129`,
`data/achievement_diaries/lumbridge.py:532`). Pins: `tests/test_fishing_data.py`,
`tests/test_skill_guide_logic.py`, `tests/test_target_metadata.py:1940`.

### S4 `silverlight-quest-fights` (note 4)

1. Every quest reward tagged `"category": "equipment"` that has an equipment
   slot in the source item data gets an equipment row; Silverlight (2402) is
   one of 48 missing (Excalibur, Wolfbane dagger, Ivandis flail, Ancient mace,
   Helm of neitiznot, Iban's staff and others). Derive the list in
   `tools/generate_equipment_data.py` instead of the hand list
   `QUEST_EQUIPMENT_ITEMS` (`:218-235`), regenerate `data/equipment_data.py`,
   and correct reward rows wrongly tagged as equipment (Bowl, Swordfish).
   Verify Silverlight's stats against the rev-727 cache per the evidence
   standard.
2. In live pacing, a quest fight uses the ordinary per-review ticks:
   `runtime/runtime_actions_production.py:1249` drops the `None` branch.
   Retire the exemption at `memory-bank/systemPatterns.md:644` and change the
   pin `tests/test_cadence_live.py:912`. Each review shows the existing
   damage line (`runtime_actions_production.py:1290`).
3. Delrith takes damage only from a wielded Silverlight (Darkan
   `DelrithBoss.java:133-141`, "You need silverlight to damage Delrith."). A
   Silverlight in the bank no longer satisfies that step. Update
   `tests/test_combat_quest_gate.py:304`.
4. During a quest fight the review HUD names the boss, not the quest
   (`ui/ui.py:1565-1569`); this closes the Pass 13 kanban follow-up.

### S5 `barcrawl-steps` (note 5)

Alfred Grimhand's Barcrawl gets ten automatic stages, one per bar, in the
order the blocker lists them today (Blue Moon Inn, Blurberry's Bar, Dead Man's
Chest, Dragon Inn, Flying Horse Inn, Forester's Arms, Jolly Boar Inn, Karamja
Wines, Rising Sun, Rusty Anchor). Each stage needs the Barcrawl card, pays the
2012 price in coins (Wiki Bar Crawl oldid 6304383: 50, 10, 15, 12, 8, 18, 10,
7, 70, 8 in that bar order; total 208), and runs as an auto action, as Fight
Arena stage 4 does (`data/quest/definitions/members/fight_arena.py:80-86`).
Remove the ten "Buy <drink>" shop rows (`tools/generate_npc_shop_data.py:219-340`,
regenerate `data/shop_data.py`) and their proof rules
(`data/quest_action_proof_data.py:11-64,90-129`). Retire
`tests/bar_crawl/test_vendor_actions.py`; update `tests/bar_crawl/test_quest_route.py`
and `tests/bar_crawl/test_quest_ui.py`. The owner's save sits at progress 2
with one proof; no migration. The "is blocked" dialog lists one reason per
line from one shared helper that replaces the two copies at
`runtime/runtime_actions_production.py:1293,1319`.

### S6 `belt-tools` (notes 6 and 9)

One constant lists the 2012 tool belt (Tool belt oldid 6538396, released
2011-12-06): general, fishing, crafting and farming groups. One predicate
answers "is this tool on the belt": always true for every listed tool except
the pickaxe and hatchet, which keep the existing attach path. Quest
`required_tools` (`logic_pure/logic_pure_quest.py:435-461`) and claims
(`logic_pure/logic_pure_claims.py:128`) use it. Quest requirements that name a
belt tool in `required_inventory` move to `required_tools`; consumed tools and
the period exceptions stay item-based (Horror from the Deep stage 5 tinderbox,
Shilo Village stage 7 chisel, Tai Bwo Wannai Trio stage 4 knife, Heroes' Quest
oiled rod, spade steps that dig bare ground). Farming spade, seed dibber and
secateurs checks (`logic/farming_logic.py:1307,1346,1362-1371,2732`) and
Vinesweeper (`logic/vinesweeper_logic.py:121-131`) use the predicate too, and
the tooltip "Carry a spade or add one to the tool belt before entering."
(`ui/ui.py:10591`) goes. The Bank "Toolbelt" panel (`ui/ui.py:27161-27225`,
rows from `bank_gear_rows_pure`) lists the belt tools by group, read-only,
tooltip "Always on your tool belt." Pins: `tests/test_logic.py:8242-8255,8395,10947,7442,12401-12498`,
`tests/test_quest_catalog.py:1878,2118`, `tests/test_main_menu_widget.py:430-433,1415-1471`.

### S7 `shop-locks-and-purchase` (notes 7 and 8)

1. A shop locked against the current save (any access rule: quest, skill,
   skill total, quest points) sorts after every open shop in the list and in
   search, dims, and names its reason, for example "Canifis General Store ·
   Requires Priest in Peril". Search sorts before the 80-row cut
   (`logic/shop_logic.py:233,206-224`); the list uses the computed
   `selector_views` (`ui/ui_tab_shop.py:660-665,1611-1650`). A dimmed shop
   still opens read-only.
2. The purchase result shows as a chip directly under the Buy controls in the
   transaction panel (`ui/ui_tab_shop.py:258-261`), green with a check mark
   for success and amber for a refused buy or sell, and hides after 4 seconds
   or on a shop or row change. It replaces `shop_toast` at the bottom of the
   scroll (`:593-621`). The owner approved this change for Opus 5.5 by name.

### S8 `skill-target-search` (note 10)

Every Skills-tab target list gets the Combat search bar. Move the body of
`_render_combat_targets` (`ui/ui.py:8591-8670`) into one shared helper beside
`_build_target_selector` (`ui/ui.py:5545`); Combat keeps its Slayer filter as
an extra filter. The search matches the row name and its group, opens the
groups that hold a match, shows "Showing N/M", never selects a hidden row, and
Escape clears it. Measure the Crafting rebuild (233 rows) per keystroke; add
the Bank's 140 ms delay only if a keystroke takes longer than 100 ms.

## Second level, recorded, not in scope

- Count Draynor's garlic adjustment (−5 Defence and Strength,
  `draynor_manor.plugin.kts:79-81`) is unmodelled.
- 90 of 293 quest encounters across 46 quests still have no stats (Pass 13
  said 91/47); harvesting belongs to the Darkan thread by doorbell.
- Spiked gauntlets cost 6 coins plus a free sample; the 2012-08 page says free.
- Do No Evil's m'amulet mould and Fremennik Isles' yak-hide cure use the same
  purchase-proof design the Barcrawl leaves.
- A raw git worktree sits at
  `addons21/ankiscape_fork/.claude/worktrees/agent-a0e9f6b63a21486d9`.
