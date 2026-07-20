# Item reachability: Thieving loot correction — 2026-07-20

## Finding

The live Thieving engine already awards the period-pinned guaranteed and
weighted loot rows in `thieving_data.THIEVING_TARGETS`, but
`tools/audit_item_reachability.py` did not include Thieving in its action
graph. This made obtainable Master Farmer seeds appear as root acquisition
gaps.

The affected live roots were:

- `Nasturtium seed`
- `Redberry seed`
- `Cadavaberry seed`

This was an audit-model omission, not missing gameplay or a source gap.

## Correction

Each non-source-blocked Thieving target with guaranteed or weighted loot is now
represented as a quantity-free reachability action. Source-blocked targets
remain excluded. Any target-local `required_items_any` gate is represented as
an alternative-input group rather than erased.

Thieving actions are appended after the ordinary skill action tables. That
preserves an already-established route when an item has several authentic
producers: for example, `Swamp toad` remains attributed to
`Utility:gather_swamp_toads`, while its Gnome pickpocket route is still known
to the graph.

## Result

- Actions: `1,344 → 1,379`
- Reachable items: `1,999 → 2,012`
- Orphan inputs: `237 → 234`
- Root/cascade split: `94/143 → 91/143`
- Blocked actions: `249 → 246`

The three seed routes resolve through
`Thieving:pickpocket_master_farmer`. No runtime, probability, UI, item
metadata, or save-state behavior changed, and no owner design gap surfaced.

## Verification

- Focused reachability and Thieving coverage passes 20 tests.
- Complete non-Qt discovery passes all 1,909 tests with 251 expected
  environment skips.
- Documentation, test-quality, compilation, diff, and worktree-safety audits
  pass.
- The regression pins all three Master Farmer routes and preserves the
  existing Swamp-toad route.
