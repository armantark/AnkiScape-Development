# AnkiScape Skill Expansion Reference

## Source Audit Template

Use this table in a markdown artifact or data note for every implemented slice.

| Field | Notes |
| --- | --- |
| Skill or family | Example: Crafting / Pottery |
| Source URL | Wiki page or subpage |
| Source section | Example: Pottery table |
| Captured rows | Exact rows used for implemented targets |
| Excluded rows | Why deferred or omitted |
| Era concern | OSRS-only, RS3-only, post-2011, quest-gated, members-only |
| Open balance note | Any Anki pacing adjustment separate from base XP |

## Target Data Checklist

Each target/action should define:

- Stable target ID.
- Display name.
- Category or family.
- Required skill level, if XP-bearing.
- Base XP from source.
- Required inputs and quantities.
- Output item and quantity.
- Batch size, if not one.
- Whether it is an XP skill action or no-XP Utility/Activity.
- Asset key/path for visible outputs.
- Source note.

## Candidate Statuses

- `implemented`: exposed or ready to expose.
- `backend_ready`: implemented but intentionally hidden pending frontend.
- `deferred_dependency`: source data is known, but material loops or related systems are missing.
- `future_content`: in scope later, not part of the current slice.
- `not_applicable`: intentionally excluded from AnkiScape.

## Achievement Pattern Library

Prefer these generated patterns when the registry can support them:

- First successful action for a skill or family.
- First completed chain, such as shaped and fired pottery.
- Level milestones: 10, 30, 60, 99.
- Count milestones: 100, 1,000, 10,000 successful actions or outputs.
- Collection milestones: produce one of each implemented target in a family.
- Cross-skill milestone only when both skills are stable.

Avoid:

- Achievements requiring deferred materials.
- Achievements for unreleased UI targets.
- One-off lambdas when a registry predicate would be enough.
- Huge completionist achievements before the content list has settled.

## Asset Workflow

1. Resolve the item name and desired output path from `ITEM_DEFINITIONS`.
2. Dry-run `tools/fetch_assets.py` for ambiguous wiki titles.
3. Fetch with `--size 64` unless the UI needs a different size.
4. Use `--wiki-title` for singular/plural or variant icons.
5. Confirm `assets_provenance.json` changed.
6. Add a manifest asset existence test for the new category or items.

Example command:

```bash
uv run tools/fetch_assets.py --key "ball of wool" --wiki-title "Ball of wool" --size 64
```

## Balance Rules

- Base XP should match the audited source.
- The global XP multiplier is a gameplay setting, not source data.
- One successful card equals one action tick unless the target explicitly declares a batch.
- Batch station-like actions when real-game interaction would rapidly process inventory items.
- No-XP Utility/Activities can batch aggressively because they are material prep, not skill training.
- If a recipe creates multiple outputs in the real game, model that as output quantity rather than XP multiplier.

## Test Matrix

Backend:

- Source data constants match expected rows.
- Pure helpers do not mutate inputs.
- Batch caps stop at inventory count.
- Skill XP is multiplied exactly once.
- Utility actions award zero skill XP.
- Storage migration seeds new items and preserves unknown entries.
- Undo restores inventory, XP, levels, counters, and achievements changed by the review reward.

Frontend:

- Skill appears in the correct category.
- Utility/Activities are visibly no-XP.
- Target list shows locked/unlocked states.
- Tooltips include level, materials, batch behavior, and XP.
- Settings controls persist and reload.
- Stats/Bank/HUD include new registry-backed skills/items where applicable.

Manual Anki:

- Select the new action/skill.
- Answer a card correctly and verify XP/items.
- Press Command-Z and verify XP/items roll back.
- Answer incorrectly and verify no progress.
- Restart Anki and verify persisted state.

## Memory Bank Update Checklist

Update memory bank after:

- Adding a new skill or Utility/Activity pattern.
- Discovering source data discrepancies.
- Creating a new item category or asset folder.
- Changing XP/batch/balance policy.
- Adding an achievement generation pattern.

Usually update:

- `memory-bank/activeContext.md`
- `memory-bank/progress.md`
- `memory-bank/systemPatterns.md`
- `memory-bank/roadmap.md` if the phase sequencing changes.
