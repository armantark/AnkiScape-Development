---
name: ankiscape-skill-expansion
description: Guides AnkiScape skill and action-family expansions. Use when adding or expanding AnkiScape skills, Utility/Activities, item chains, target lists, achievements, source audits, wiki scraping, asset scraping, XP balancing, or gameplay settings.
---

# AnkiScape Skill Expansion

## Task Description

AnkiScape is an Anki add-on that turns successful card reviews into lightweight RuneScape-style game progress. A skill expansion is any change that adds or expands a skill, action family, Utility/Activity, target chain, item economy slice, achievement set, XP/batch balance rule, or gameplay setting.

Use this skill before planning or implementing a skill expansion. The goal is to avoid rediscovering the same workflow each time: audit the source data, choose a playable scope, add backend data and pure mechanics, fetch assets, expose the UI, add achievements, test the review loop, and update the memory bank.

## Non-Negotiables

- Split backend and frontend work explicitly.
- Fetch and cite the relevant RuneScape wiki source before claiming XP, levels, materials, outputs, or unlocks. Do not infer these from memory.
- Keep source data honest: preserve OSRS/RS base XP in data, then apply AnkiScape pacing knobs separately.
- Use stable IDs for skills, recipes, targets, and items. Do not use display names as durable target identifiers when outputs can collide.
- Separate XP-bearing skill actions from no-XP Utility/Activities.
- Keep persisted save keys flat unless a migration is deliberately planned.
- Every review reward must remain compatible with Anki undo rollback.
- Add pre/post HTML status artifacts in `memory-bank/status-updates/` and update the memory bank when patterns change.

## Specific Instructions

Think through these steps before making code changes:

1. Audit sources:
   - Fetch the skill page and any needed subpages from OSRS/RS wiki.
   - Extract action tables: level, item/action, materials, outputs, XP, members/F2P, quest gates, tool requirements.
   - Record the exact source rows used for implemented recipes.
   - Mark uncertain or post-2011 content instead of guessing.

2. Cut scope:
   - Pick a playable slice.
   - Classify each candidate as `implemented`, `deferred_dependency`, `future_content`, or `not_applicable`.
   - Avoid normal UI entries that cannot be completed because their material source loop does not exist.
   - Prefer a small complete chain over a large dead-end list.

3. Add backend data:
   - Update `skill_registry.py` for skill identity, category, save keys, review eligibility, handler key, and visibility.
   - Update `constants.py` or a focused data module with stable target IDs, display names, level requirements, XP, inputs, outputs, batch size, and source notes.
   - Update `item_registry.py` so outputs and required materials have stable item definitions and asset paths.
   - Add storage defaults/migrations through `storage_pure.py` without deleting unknown inventory entries.

4. Fetch assets:
   - Use `tools/fetch_assets.py` for item icons where possible.
   - Prefer OSRS wiki assets first unless the project decision says otherwise.
   - Normalize PNGs, avoid overwriting unless intentional, and update `assets_provenance.json`.
   - Add tests that required manifest asset paths exist.

5. Implement mechanics:
   - Add pure logic first in `logic_pure.py`.
   - Model one successful card as one action tick by default.
   - For station-like actions, use explicit batches capped by inventory (for example, up to 28 items per successful card).
   - Apply any global XP multiplier after base XP is calculated and before level checks.
   - Keep no-XP Utility/Activities from awarding skill XP.

6. Update frontend:
   - Keep the current UI style unless a redesign is explicitly requested.
   - Add registry-driven target lists, icons, level/material gates, and concise tooltips.
   - Label Utility/Activities clearly as no-XP material prep.
   - If touching settings, preserve existing toggles and group related controls into clear sections.

7. Add achievements:
   - Prefer registry-generated achievement patterns over hand-written lambdas.
   - Add generic milestones first: first action, level 10/30/60/99, 100/1,000/10,000 outputs or actions where sensible.
   - Add only a few stable skill-flavored achievements per slice.
   - Avoid completionist achievements for content whose target list is still experimental.

8. Test:
   - Unit tests for pure logic, data integrity, source assumptions, and batch caps.
   - Integration tests for review dispatch, XP/inventory mutation, storage migration, and Anki undo rollback.
   - Offscreen Qt tests for target panels, gating, tooltips, settings controls, and registry-driven surfaces.
   - Manual Anki test instructions for runtime review flow.
   - Run `python3 run_tests.py`; for Qt behavior also run `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`.

## Tool Guidelines

- Use web fetch/search for source audits when exact wiki facts are needed.
- Use `tools/fetch_assets.py` for assets and provenance.
- Use pure tests before Anki/Qt tests when adding backend mechanics.
- Use offscreen Qt tests for UI behavior rather than restarting Anki repeatedly.
- Use status artifacts for pre/post implementation communication instead of long chat summaries.

## Handoff Format

When planning or summarizing, split work like this:

- Backend: source audit, data tables, item manifest, pure logic, storage, dispatch, achievements, tests.
- Frontend: Skills hub/Utility UI, target lists, tooltips, settings, Stats/Bank/HUD, Qt tests.
- Assets: scrape list, output folders, provenance, missing/deferred assets.
- Balance: OSRS base values, Anki batch sizes, XP multiplier implications, known pacing risks.

## Dynamic Project Context

- Current source base: Anki add-on Python package in `addons21/ankiscape_fork`.
- Current review model: one eligible successful card is one game action tick unless a target declares batching.
- Current save pattern: flat `player_data` keys stored in Anki config.
- Current source policy: OSRS wiki first unless a project decision chooses another RuneScape source.
- Current pacing policy: keep audited base XP data separate from gameplay multipliers.

For detailed templates, use [reference.md](reference.md).
