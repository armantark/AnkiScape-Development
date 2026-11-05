# Achievement Diary Curation Ledger

Base SHA: `ef860086c56a30bef05fd4f46692cb3921e38ac2`

This directory contains the canonical deed-level curation record for the 320 Achievement Diary rows that the honest-stop catalog originally left without completion conditions, and for the 22 rows the ledger itself authors. The generator consumes its reviewed wiring clauses; the ledger remains the only canonical trigger record.

## Measured catalog census

The generated catalog contains:

- **534** designed denominator slots;
- **474** named task rows and **60** unnamed denominator slots;
- **112** named rows with `conditions == ()`, all dormant;
- **362** named rows with non-empty conditions;
- **129** ordinary deed-backed condition rows outside this ledger;
- **3** quest-deed condition rows; and
- **230** live rows in this ledger.

The canonical JSONL contains **342** rows: the 320 rows that were empty at the base SHA, and 22 authored rows.

The 342 curation rows classify as 46 `active`, 142 `translated`, 42 `invented`, 0 `swapped`, and 112 `dormant`. All 230 live rows carry compiled wiring. The checked-in catalog reflects all 184 translated and invented designs, so no ledger row carries a regeneration marker. The 112 dormant rows keep `conditions == ()`.

## Authored rows

A period family with fewer than 48 deeds leaves its twelve-task tiers short. A row with `source_id` at or above 900000 fills such a slot: it has no cache identity, and the generator takes its place in the tier, its name, its sentence, its wiring and its access gates from the ledger. The owner ruled on 2026-11-04 that no diary row is a bare level milestone (`memory-bank/specs/done/pass21-owner-notes/spec.md`). Each authored row starts from the 2012 deed that held its old level, and `notes` names that deed.

An authored `task_id` keeps its earlier `reach_level` form because saves store it, so a player who completed the row keeps the tier progress. Never rename one.

## Canonical file

`dormant-task-ledger.jsonl` is the only canonical copy of the 342 rows. It contains one JSON object per line, no comments, and preserves catalog source order; an authored row follows the source rows of its tier. Do not create checked-in partition files, generated copies, or another ledger.

Every row uses this exact key order:

1. `task_id` — durable catalog task ID.
2. `source_id` — Darkan/cache source task ID.
3. `family` — canonical catalog family ID.
4. `current_tier` — current full catalog tier ID.
5. `original_tier` — source-family tier from the harvest, or `null` when absent.
6. `designed_trigger` — reviewed human-readable completion event for the deed.
7. `wiring` — machine-readable condition JSON compiled by the generator for every live disposition, otherwise `null`.
8. `source_citation` — pinned source identity and permanent citation.
9. `disposition` — one allowed curation disposition.
10. `future_system` — one canonical future-system ID for dormant rows, otherwise `null`.
11. `notes` — source conflicts, translation boundaries, exact current seams, and unresolved evidence.
12. `designed_name` — required for `translated` and `invented`; the name emitted at regeneration.
13. `designed_description` — required for `translated` and `invented`; the description emitted at regeneration.
14. `catalog_regeneration_pending` — optional temporary `true` marker while regeneration is in progress; remove it after the generator succeeds.
15. `access_gates` — required on authored rows, absent elsewhere; the `skill_level` and `quest` conditions the row shows the player.

## Dispositions

Allowed values are exactly:

- `active`: an exact existing AnkiScape writer, action, result, or telemetry seam already fires on the deed. A same-frame result qualifies when the existing runtime reaches achievement checking immediately after that action; the row must say when no durable retroactive evidence exists. The reviewed wiring clause compiles that seam into the generated catalog.
- `dormant`: the deed has a concrete designed trigger but still needs one named future system before it can fire honestly.
- `swapped`: the source deed cannot translate, and an authentic same-family replacement is recorded. No row in this ledger currently uses this disposition.
- `translated`: the source deed's substance survives through an existing AnkiScape action; locale, surface, or seam may change while region, family, and difficulty are kept.
- `invented`: the source substance could not survive, so a deliberate, tier-proportionate replacement deed is recorded for the family and tier, with generated replacement text.

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
- `minigame_actions`
- `npc_dialogue_actions`
- `object_interaction_actions`
- `prayer_altar_actions`
- `quest_stage_actions`
- `shop_transaction_actions`
- `skill_action_telemetry`
- `spell_cast_actions`
- `world_emote_actions`

## Deed-only rule

A diary task completes only when its deed occurs. Skill levels, quest states, inventory ownership, equipment ownership, and route access are access gates unless the source deed itself requires that state at action time. They must never substitute for the deed. No row may trigger on a level.

## Citation rule

Every source-derived row cites existing repository evidence only. `source_citation` must include the source page title, pinned oldid, UTC timestamp, `https://runescape.wiki/w/Special:PermanentLink/<oldid>`, Darkan rev-727 cache enum 3483 identity, and `source_id`. An `invented` row instead cites the family, current tier, and owner ruling that authorizes the replacement; displaced source provenance stays in `notes`. Do not replace a permanent URL with a mutable wiki URL, fetch a newer source, or infer an enum identity from the display name.

## Source files

The ledger is derived from these fixed repository records:

- `data/achievement_diary_catalog.py` — the generated 474-row named catalog, current tier placement, durable task IDs, source IDs, and empty-condition census.
- `memory-bank/source-audits/achievement-diary-harvest-2026-07-26.json` — original family tier membership, Darkan classes and enum identities, task definitions, and pinned family citations.
- `memory-bank/codex-briefs/pass12-owner-notes-handoff-2026-08-26.md` — the deed-only ruling and honest-stop boundary.
- `memory-bank/design-thread-queue.md` §4.21 and §5.21 — the owner-ruling queue for the curation ledger and later wiring.
- `memory-bank/achievement-diaries-2026-07-26.md` — historical breadth-one context, retained with its supersession note.

## Records-only boundary — passed

The assembly and review slice did not run `tools/generate_achievement_diary_data.py` or edit generated data, runtime logic, UI, tools, source audits, or tests. Gate 2 lifted that boundary. Current catalog corrections are ledger-row edits followed by regeneration; `data/achievement_diary_catalog.py` is never hand-edited.

## Gates before wiring

1. **Cross-lineage review gate — passed:** the two Opus review ranges covered all 320 rows and the supporting contract, including the source-order census, dispositions, active seams, translations, citations, and dormant assignments. [The review record](cross-lineage-review.md#review-coverage) identifies both ranges; [its resolution result](cross-lineage-review.md#resolution-result) records resolution of all 19 initial and four final findings.
2. **Owner spec-conformance gate — passed:** §4.22 ruling 3 on 2026-08-31 replaces an owner read of every row with the row-by-row cross-lineage review against the settled spec. Later owner interpretation feedback is a ledger-row patch plus regeneration; it is not a new pre-wiring approval requirement.

The cross-lineage review and its resolutions are recorded in `cross-lineage-review.md`.

**Gate 2 passed by owner ruling of 2026-08-31** (`memory-bank/design-thread-queue.md` §4.22 ruling 3): conformance to the settled contracts, verified row-by-row by the gate-1 review, substitutes for an owner read of all 320 rows. Interpretation corrections land as ledger-row edits plus regeneration through `tools/generate_achievement_diary_data.py`, never hand edits of the generated catalog. Row 135 (Fire cape) uses the closer equipped-item candidate; the owner can veto it as a patch. Ledger wiring is complete for all 230 live rows. The 22 authored rows came later, under the owner ruling of 2026-11-04. The checked-in catalog is generated through its sharded package layout, and its catalog-parity test compares every task row exactly.
