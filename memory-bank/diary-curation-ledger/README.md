# Achievement Diary Curation Ledger

Base SHA: `ef860086c56a30bef05fd4f46692cb3921e38ac2`

This directory contains the canonical deed-level curation record for the Achievement Diary rows that the honest-stop catalog leaves without completion conditions. The ledger is records-only. It does not wire, generate, or activate any diary task.

## Measured catalog census

At the base SHA, the generated catalog contains:

- **534** designed denominator slots;
- **474** named task rows and **60** unnamed denominator slots;
- **320** named rows with `conditions == ()`, in catalog source order;
- **154** named rows with non-empty conditions;
- **129** ordinary deed-backed condition rows;
- **3** quest-deed condition rows; and
- **22** labelled AnkiScape progression anchors.

The 154 condition-bearing rows are the 129 ordinary deed rows, 3 quest deeds, and 22 anchors. The canonical JSONL contains only the 320 empty-condition rows. It excludes all 22 anchors.

The 320 curation proposals currently classify as 43 `active`, 247 `dormant`, 30 `translated`, and 0 `swapped`. These are ledger dispositions, not claims about current catalog wiring. Every one of the 320 source rows remains incomplete in the generated catalog until a later reviewed wiring slice changes that catalog.

## Canonical file

`dormant-task-ledger.jsonl` is the only canonical copy of the 320 rows. It contains one JSON object per line, no comments, and preserves catalog source order. Do not create checked-in partition files, generated copies, or another 320-row ledger.

Every row uses this exact key order:

1. `task_id` — durable catalog task ID.
2. `source_id` — Darkan/cache source task ID.
3. `family` — canonical catalog family ID.
4. `current_tier` — current full catalog tier ID.
5. `original_tier` — source-family tier from the harvest, or `null` when absent.
6. `designed_trigger` — concrete runtime-checkable completion event for the deed.
7. `source_citation` — pinned source identity and permanent citation.
8. `disposition` — one allowed curation disposition.
9. `future_system` — one canonical future-system ID for dormant rows, otherwise `null`.
10. `notes` — source conflicts, translation boundaries, exact current seams, and unresolved evidence.

## Dispositions

Allowed values are exactly:

- `active`: an exact existing AnkiScape writer, action, result, or telemetry seam already fires on the deed. A same-frame result qualifies when the existing runtime reaches achievement checking immediately after that action; the row must say when no durable retroactive evidence exists. This means the row can be wired later without inventing a gameplay system; it does not mean the catalog row is wired now.
- `dormant`: the deed has a concrete designed trigger but still needs one named future system before it can fire honestly.
- `swapped`: the source deed cannot translate, and an authentic same-family replacement is recorded. No row in this ledger currently uses this disposition.
- `translated`: the source deed is honestly re-expressed through an existing AnkiScape action, with the source deed and the removed or changed context recorded in `notes`.

`future_system` must be non-null only for `dormant` rows. Every dormant value must come from this canonical vocabulary:

- `activity_completion_actions`
- `bank_inventory_actions`
- `combat_encounter_actions`
- `combat_special_actions`
- `equipment_state_actions`
- `familiar_actions`
- `item_acquisition_actions`
- `item_processing_actions`
- `item_use_actions`
- `location_visit_actions`
- `minigame_actions`
- `npc_dialogue_actions`
- `object_interaction_actions`
- `prayer_altar_actions`
- `quest_stage_actions`
- `shop_transaction_actions`
- `skill_action_telemetry`
- `spell_cast_actions`
- `world_emote_actions`
- `world_transport_actions`

## Deed-only rule

A diary task completes only when its deed occurs. Skill levels, quest states, inventory ownership, equipment ownership, and route access are access gates unless the source deed itself requires that state at action time. They must never substitute for the deed. The only level-trigger exceptions are the 22 explicitly labelled progression anchors, which are outside this ledger.

## Citation rule

Every row cites existing repository evidence only. `source_citation` must include the source page title, pinned oldid, UTC timestamp, `https://runescape.wiki/w/Special:PermanentLink/<oldid>`, Darkan rev-727 cache enum 3483 identity, and `source_id`. Do not replace a permanent URL with a mutable wiki URL, fetch a newer source, or infer an enum identity from the display name.

## Source files

The ledger is derived from these fixed repository records:

- `data/achievement_diary_catalog.py` — the generated 474-row named catalog, current tier placement, durable task IDs, source IDs, empty-condition census, and anchor labels.
- `memory-bank/source-audits/achievement-diary-harvest-2026-07-26.json` — original family tier membership, Darkan classes and enum identities, task definitions, and pinned family citations.
- `memory-bank/codex-briefs/pass12-owner-notes-handoff-2026-08-26.md` — the deed-only ruling and honest-stop boundary.
- `memory-bank/design-thread-queue.md` §4.21 and §5.21 — the owner-ruling queue for the curation ledger and later wiring.
- `memory-bank/achievement-diaries-2026-07-26.md` — historical breadth-one context, retained with its supersession note.

## No-generator boundary

Do not run `tools/generate_achievement_diary_data.py` while assembling, reviewing, or owner-spot-checking this ledger. Do not edit `data/achievement_diary_catalog.py`, runtime logic, UI, tools, source audits, generated files, or tests in the records-only slice. Generator and runtime wiring are a separate later change after the gates below.

## Gates before wiring

1. **Cross-lineage review gate:** an independent reviewer must check all 320 rows, the source-order census, every disposition, every active seam, every translation, every citation, and every dormant future-system assignment. Assembly alone does not satisfy this gate.
2. **Owner spot-check gate:** the owner must spot-check the reviewed ledger and accept the deed interpretations before any generator or runtime wiring begins. No owner spot-check is claimed by this slice.

The cross-lineage review and its resolutions are recorded in `cross-lineage-review.md`.

**Gate 2 passed by owner ruling of 2026-08-31** (`memory-bank/design-thread-queue.md` §4.22 ruling 3): conformance to the settled contracts, verified row-by-row by the gate-1 review, substitutes for an owner read of all 320 rows. Interpretation corrections land as post-wiring patches: a ledger-row edit plus a regeneration through `tools/generate_achievement_diary_data.py`, never a hand edit of the generated catalog. Row 135 (Fire cape) defaults to the closer equipped-item candidate; the owner can veto it as a patch. Generator and runtime wiring may begin.
