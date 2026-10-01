# Achievement Diary Ledger Cross-Lineage Review

Date: 2026-08-27

Branch: `goal/diary-curation-ledger-2026-08-27`

Exact parent and review HEAD: `ef860086c56a30bef05fd4f46692cb3921e38ac2`

## Review coverage

Two independent Opus review ranges covered the canonical ledger and its supporting memory-bank changes:

1. Opus range 1: rows 1-160 of `memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl`, the README, the six edited memory-bank files, and the worktree scope.
2. Opus range 2: rows 161-320 of `memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl`, whole-file structural checks, and the worktree scope.

The exact uncommitted pre-commit diff reviewed was the branch at the parent above with these tracked paths and no other tracked path:

- `memory-bank/achievement-diaries-2026-07-26.md`
- `memory-bank/activeContext.md`
- `memory-bank/codex-briefs/pass12-owner-notes-handoff-2026-08-26.md`
- `memory-bank/future-work-kanban.md`
- `memory-bank/papercuts.md`
- `memory-bank/progress.md`

The exact untracked review inputs were:

- `memory-bank/diary-curation-ledger/README.md`
- `memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl`

At handoff, the tracked diff measured 60 insertions and 2 deletions across the six paths above. The untracked README measured 6,286 bytes, and the untracked canonical ledger measured 275,261 bytes with exactly 320 lines. No source, data, tools, logic, UI, generated, test, source-audit, or asset-report path was in the reviewed diff. The review was pre-commit; this resolution slice remains uncommitted.

## Opus range 1 findings and resolutions

### 1. Rows 53, 94, and 128: simultaneous Runecrafting output

Finding: the three equivalent single-batch rune deeds used inconsistent dispositions, and persisted telemetry stores cumulative output rather than one call's batch size.

Resolution: accepted the inconsistency, but rejected the suggested demotion of rows 53 and 94. `runtime/runtime_actions_production.py:1181-1262::handle_runecrafting_answer` computes `output_count` from the single action, calls `_record_action`, and immediately calls `check_achievements`; the README definition of `active` already permits an existing live result seam. Row 128 is now `active` with `future_system=null`, matching rows 53 and 94. All three notes now state that later wiring must inspect the same-frame `output_count`, not cumulative telemetry. The same rule is applied to rows 165 and 274.

### 2. All 25 rotated skill-type rows

Finding: `tools/generate_achievement_diary_data.py::_SKILL_TYPE_IDS` rotates source skill types 17, 18, and 19 into Woodcutting, Fletching, and Firemaking, while the deed data identifies them as Firemaking, Woodcutting, and Fletching respectively. Ledger notes silently mixed catalog labels with corrected skills.

Resolution: accepted and applied to the whole canonical file. Independent enumeration of the catalog and harvest measured 25 affected ledger rows: 13, 32, 47, 54, 62, 87, 97, 114, 119, 121, 123, 127, 157, 195, 196, 202, 222, 230, 231, 256, 263, 268, 269, 273, and 319. The count is 25, not the review follow-up's proposed 24: row 273 already carried a differently worded conflict note in addition to the 13 first-range rows and 11 newly reported rows. Every affected note now names the exact generated catalog label and the deed-proven source skill, and states that the gate label is not deed evidence. The generator defect remains a named blocker before the later wiring slice. It was not fixed here because this slice is records-only and forbids tool or generated-data changes.

### 3. Row 110: nonexistent Brimhaven symbol

Finding: the note cited `_apply_brimhaven_review`, which does not exist.

Resolution: accepted. The note now cites `logic/agility_logic.py:695::_brimhaven_review`, with the ticket award at lines 735-742, and the existing runtime telemetry handoff at `runtime/runtime_actions_activities.py:3089-3103::handle_agility_answer`.

### 4. Rows 12, 33, 49, 54, 62, and 109: rolling Farming log

Finding: `farm_event_log` is capped at 200 rows and cannot serve as durable deed evidence; the six rows did not consistently state that only the live queue result is exact.

Resolution: accepted. All six triggers and notes now use the same-frame result returned by `logic/farming_logic.py::_execute_farm_field_step_in_place` and consumed by `runtime/runtime_actions_shared.py::_apply_farming_queue_result`, which calls `check_achievements` immediately after the committed step. Each note states that `farm_event_log` is a 200-row rolling buffer and must not be used as durable evidence. Rows 12 and 33 remain `translated`; rows 49, 54, 62, and 109 remain `active`.

### 5. Row 89: Managing Miscellania mahogany collection

Finding: the note overstated durable output evidence and excluded the mixed hardwood variant.

Resolution: accepted. The trigger now keys on the committed `collect` action and captured same-frame `outputs` map inside `__init__.py:4346-4363::_apply_managing_miscellania_command::_after_apply`. Both the mahogany and mixed hardwood variants qualify. The note states that no durable per-output record exists and that retroactive inventory ownership or collection count cannot credit the deed.

### 6. Machine-specific absolute paths

Finding: canonical ledger notes embedded one checkout's absolute path.

Resolution: accepted and applied to the whole canonical file, not only the first reviewed range. All 94 occurrences across 65 rows were normalized to repository-relative paths. Final absolute-path count is zero.

### 7. Rows 38, 61, and 79: unsupported access-gate claims

Finding: the notes named quest gates absent from the catalog rows.

Resolution: accepted. Row 38 now identifies Fairy Ring context as source-side context not encoded by the catalog. Row 61 does the same for Ring of Charos context and removes the Garden of Tranquillity gate claim. Row 79 keeps only the catalog's Fremennik Trials gate.

### 8. Rows 35 and 93: wrong result field and equipment slot

Finding: row 35 claimed a nonexistent result `success` field, and row 93 named a `torso` slot that the code calls `body`.

Resolution: accepted. Row 35 now requires `allowed=True` and `result["duty"]="catapult"`, reached through the branch at `logic/castle_wars_logic.py:334`. Row 93 now requires Agile top in the `body` slot, matching `data/equipment_data.py:74-76`.

### 9. Row 135: stricter Fire-cape translation

Finding: a Fight Pit win with a Fire cape is stricter than the source deed's equip-in-TzHaar action, while an `equipped_item` expression is available.

Resolution: accepted as an owner-choice issue, not silently decided in review. The row remains `translated` with its strict Fight Pit win candidate. Its note now records both that candidate and the closer equipped-item candidate, and states that the owner must choose during the pending spot-check before wiring.

### 10. Row 2: omitted stall alternative

Finding: the active guard-pickpocket trigger covers only one of the source deed's two alternatives.

Resolution: accepted. The note now states that stall-only play is not credited because no Ardougne Market location identity ships for a stall-attempt branch. The row remains `active` on the exact guard-attempt seam.

## Opus range 2 findings and resolutions

### 11. Row 216: Camelot-to-Fremennik shortcut

Finding: the row was `active`, but `camelot_fremennik_log` is an `AGILITY_SHORTCUTS` registry row with no runtime consumer or telemetry writer.

Resolution: accepted. The row is now `dormant` with `future_system="world_transport_actions"`. Its note distinguishes the milestone-only shortcut row from the runnable `AgilityTarget` path that reaches `_finish_lap`.

### 12. Row 225: Water Obelisk grapple shortcut

Finding: the row was `active`, but `grapple_water_obelisk` is in the unconsumed grapple-shortcut registry.

Resolution: accepted. The row is now `dormant` with `future_system="world_transport_actions"`, with Strength 22, Agility 36, and Ranged 39 retained as access gates only.

### 13. Row 282: Bronze pickaxe tool-belt action

Finding: the Bronze pickaxe is present on every fresh mining tool belt, so the cited attach action cannot succeed.

Resolution: accepted. The row is now `dormant` with `future_system="equipment_state_actions"`. The note cites `data/mining_data.py:443::DEFAULT_MINING_TOOLBELT`, `core/storage_pure.py:809-815::_default_toolbelt`, and the no-op branch in `logic_pure/logic_pure_equipment.py:128-159::attach_tool_to_toolbelt_pure`.

### 14. Row 245: Stronghold second-level off-by-one

Finding: `step>=2` proves the second level was cleared, not entered.

Resolution: accepted. The trigger now fires on a transition from below 1 to at least 1. `STRONGHOLD_STEP_NAMES[0]` is Vault of War and index 1 is Catacomb of Famine, so clearing step 0 is the shipped model's proof of entering level two.

### 15. Row 165: Water-rune batch

Finding: the row was dormant even though the same live `output_count` seam makes row 274 active, and Explorer's ring does not modify the runtime action.

Resolution: accepted. Row 165 is now `active` with `future_system=null`, keyed to one `craft_water_runes` call whose live output delta is at least 100. The note states that cumulative telemetry is not used and no Explorer's-ring aid flag is needed.

### 16. Row 301: Potato harvest

Finding: the row was dormant while sibling harvest rows use the same live Farming result seam.

Resolution: accepted. Row 301 is now `active` with `future_system=null`, keyed to the same-frame successful harvest result with `crop_id="potato"` and Potato output quantity at least one. The note explicitly rejects `last_crop_id` and the rolling event log as durable evidence.

### 17. Row 220: nonexistent `data/magic_data.py::MAGIC_DATA`

Finding: `MAGIC_DATA` is exposed from `core/constants.py`, while the data module defines `MAGIC_TARGETS`.

Resolution: accepted. The note now cites `data/magic_data.py:83,108::MAGIC_TARGETS`, `core/constants_parts/skill_catalog.py:195::MAGIC_DATA`, and `runtime/runtime_actions_magic.py:417::handle_magic_answer`.

### 18. Row 266: duplicate Bork disposition and line range

Finding: the note called Misc source ID 3008 dormant even though row 316 is active, and its line range omitted the function definition.

Resolution: accepted. The note now calls the duplicate active and cites `logic/bork_logic.py:363-542::apply_bork_review_pure`, including the kill increment at line 511.

### 19. Row 223: unsupported King's Ransom gate

Finding: the catalog row contains Prayer 70 and Defence 70 gates, not King's Ransom.

Resolution: accepted. The note now names only Prayer 70 and Defence 70 as catalog access gates.

## Final independent review — 2026-08-28

The four final findings were checked against the catalog, harvest, cited symbols, and current memory-bank files before correction.

### 20. Whole-ledger rotated skill labels

Disposition: accepted, with the reported count corrected. The harvest has exactly 25 ledger rows whose requirements use source skill types 17, 18, or 19. Source deed verbs and shipped action identities consistently prove 17 as Firemaking, 18 as Woodcutting, and 19 as Fletching, while the generated catalog rotates them to Woodcutting, Fletching, and Firemaking. The final-review text mentioned both 25 affected rows and a 24-row update; direct enumeration resolves the canonical count as 25 because row 273 is additional to the 13 first-range rows and 11 later rows. All 25 notes now carry the exact catalog label, deed-proven source skill, and deed-evidence warning. The generator map remains unchanged and blocks later wiring until repaired.

Resolution — 2026-08-30: The generator is repaired on branch
`goal/diary-skill-rotation-2026-08-30`; the 25 ledger notes now state the
corrected labels without the obsolete wiring blocker.

### 21. Rows 311 and 312: unsupported Frozen qualifier

Disposition: accepted. Row 311's cited `action_id='enter'` seam proves expedition entry, not a theme predicate, and row 312's `dungeoneering.floors_completed` counter increments on floor completion without encoding a theme in the achievement predicate. The two designed triggers now say "a floor" and "a Daemonheim floor". No theme-aware condition or additional runtime claim was introduced.

### 22. Row 245: Stronghold symbol span

Disposition: accepted. `logic_pure/logic_pure_landmarks.py:42-47::STRONGHOLD_STEP_NAMES` is the exact tuple span; line 48 is blank. The ledger pin now ends at line 47.

### 23. Papercut chronology

Disposition: accepted for the ordering defect, with the observed count corrected. The received file contained one 2026-08-27 diary-workflow line after the first 2026-08-28 entries, not two. That genuine 2026-08-27 event was moved before the 2026-08-28 block without changing its date. The required persisted-output-path friction and four workflow retry stalls were then appended in 2026-08-28 order.

## Resolution result

All 19 initial findings and all four final independent findings were inspected against repository source. Every underlying issue was accepted. Two review quantities were corrected from direct evidence: the rotated-skill population is 25 rows, and the received papercut tail had one out-of-order 2026-08-27 line. One proposed initial-review correction was rejected: rows 53 and 94 were not demoted because the same-frame Runecrafting result is an existing exact seam under the README's `active` definition. The inconsistency was instead resolved by promoting rows 128 and 165 to `active` and documenting the live-result boundary on all equivalent rows.

The disposition totals remain exactly 43 `active`, 247 `dormant`, 30 `translated`, and 0 `swapped`: two Runecrafting rows and the potato-harvest row moved to `active`; two shortcut rows and the default Bronze-pickaxe row moved to `dormant`. The owner spot-check remains pending, including the row 135 Fire-cape interpretation. No generator or runtime wiring is authorized by this review.
