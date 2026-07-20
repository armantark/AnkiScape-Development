# Borrowed Power and Arcane capacitor implementation — 2026-07-19

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **the period-sourced Arcane capacitor lifecycle and all supported
Borrowed Power casts are live.**

## Authority

The owning design and source contract is
`source-audits/livid-farm-loop-2026-07-18.md`. This slice uses:

- `Borrowed Power`, RuneScape Wiki oldid `6587752`
  (`2012-11-19T14:23:14Z`);
- `Arcane capacitor amulet (u)`, RuneScape Wiki oldid `6587262`
  (`2012-11-19T08:44:38Z`); and
- period cache revision `742`, item ids `21513` and `21514`.

The implementation does not reopen the settled spell list, level, rune cost,
charge count, one-owned rule, manual-cast rule, or crumble behavior.

## Live lifecycle

- The 18,000-Produce wish grants one uncharged capacitor only when no
  uncharged or charged copy exists across the Bank, equipment, grave, Death's
  Office, active-familiar storage, or pending familiar cargo.
- Charging is an instantaneous, directly undoable Livid Farm command. It
  requires Magic 99, an accessible uncharged capacitor, and exactly 1,000
  times the selected standard spell's native rune bundle. Staff substitutions
  do not reduce this loading cost. An underfunded command changes nothing.
- Charging binds one supported spell, replaces the uncharged item with the
  charged item, and installs exactly 1,000 charges. The charged necklace has
  the period +10 Magic attack bonus.
- Removing charge destroys the necklace and refunds the unspent native rune
  bundle exactly. Spending the last charge also crumbles the necklace.
- Both physical states are untradeable, non-stackable equipment registry
  items with cutoff assets and provenance.

## Borrowed Power consumers

Borrowed Power remains a level-99 Lunar cast costing three Astral runes and
one capacitor charge. It bypasses only the standard-spellbook selection
boundary: native quest, target, item, encounter, and equipment requirements
still apply.

The supported noncombat wrappers preserve native XP and action behavior for
Telekinetic Grab's Wine of Zamorak route, Teleport to House, High Alchemy, and
Bones to Peaches. The supported Combat bindings are Wind, Water, Earth, and
Fire Wave, Magic Dart, Vulnerability, Enfeeble, and Entangle. Combat exposes a
single `Cast next review` action only when the matching charged capacitor is
equipped. That review performs one manual cast and then returns to the
ordinary selected autocast; Borrowed Power itself never becomes autocast.

## Player-facing surface and undo

- The Livid Farm reward panel shows capacitor ownership, the spell binding,
  exact 1,000-cast rune costs, charge count, Charge, and Remove charge without
  introducing a separate dialog or wall-clock state.
- The Combat equipment panel shows the bound spell and remaining charge count
  above an explicit `Cast once next review` control.
- Kimi K3's independent taste pass caught laptop-width overflow, stale
  equip/unequip state, a potentially contradictory loaded-spell picker, weak
  row identity, and incomplete disabled-state explanations. The accepted
  fixes use a two-line Combat row, refresh from live equipment state, select
  the actual loaded spell, name the capacitor directly, and explain Magic,
  ownership, unlock, and missing-rune blockers.
- Fable's independent pass caught the destructive charge-removal path,
  always-visible disabled protection controls in the neighboring Farming
  surface, item-name drift, missing laptop geometry proof, bare uncharged
  status copy, and singular-count grammar. Confirmed findings were fixed with
  an explicit default-No confirmation and concise contextual status/action
  copy. Kimi's final consolidated pass also moved the Combat action onto the
  panel's left scan line.
- Wish purchase, charge, and remove-charge commands use the shared
  direct-action undo transaction. Ordinary review undo covers Borrowed Power
  casts, Astral runes, capacitor charge, crumble, native outputs, XP, and
  Combat state.

## Verification

- Focused affected pure/runtime/integration: `553` tests passed.
- Focused real offscreen Qt behavior and geometry: passed.
- Full non-Qt: `1,830` methods executed, `1,595` ordinary passes and `235`
  expected environment skips.
- Full real offscreen Qt: `1,830` methods executed, `1,829` ordinary passes
  and `1` intentional skip.
- Test-quality, documentation, provenance JSON, compilation, diff,
  reachability, and guarded-worktree results are recorded in the consolidated
  closure artifact.
- Native Anki was fully quit and relaunched after the final reviewed UI pass.
  The canonical add-on opened exactly one dialog and returned cleanly to the
  deck screen without changing the user's save. Final unlocked states are
  covered by the deterministic real-Qt renderer at 900×560 and 1100×650.

## Remaining Livid Farm work

The one-use allotment patch and ten-tree protection scroll are live through
the ordinary Farming substrate. `Let it rain seeds` quantities and `Reduce The
Fish I Burn` magnitude remain explicitly source-blocked. No new owner-facing
design gap emerged in this slice.

Status artifact:

- `memory-bank/status-updates/livid-farm-reward-substrate-results-2026-07-19.html`
- <https://9adrft18vuka.postplan.dev>
