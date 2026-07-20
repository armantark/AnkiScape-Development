# Livid Farm core implementation — 2026-07-19

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **the source-ready activity core is live. Spell consumers, Borrowed
Power charging/casting, and wishes remain separate implementation slices.**

## Authority

The owning contract is
`memory-bank/source-audits/livid-farm-loop-2026-07-18.md`. Its primary period
evidence is:

- `Livid Farm`, oldid `6569596`
  (`2012-11-17T21:40:18Z`);
- `Borrowed Power`, oldid `6587752`
  (`2012-11-19T14:23:14Z`); and
- the historical 880,000-point conflict explanation in `Livid Farm`, oldid
  `4657954` (`2011-08-23T17:45:46Z`).

This implementation does not reopen the settled cycle, cadence, policy,
progression, distraction, or pacing design.

## Live activity core

- `livid_farm_data.py` holds the five duty families, literal rune costs,
  Magic and secondary-skill XP, Produce values, entry levels, three
  distractions, and eleven cumulative unlock thresholds.
- `livid_farm_logic.py` requires Lunar Diplomacy and the unboosted
  `70 Magic / 60 Agility / 60 Crafting / 60 Farming / 50 Construction`
  entry levels. Selecting Livid Farm is the active Lunar activity under
  AnkiScape's existing implicit-spellbook model; there is no redundant
  free-floating spellbook toggle to desynchronise.
- One cadence emission resolves the complete five-round source cycle. The
  exact `6 / 5` residual emits `1, 1, 1, 1, 2` cycles over five successful
  reviews and composes with the existing review-action multiplier.
- A full Magic-91 cycle awards exactly `1,580` Produce, `3,737` Magic XP,
  `2,754` Farming XP, `546` Construction XP, `1,080` Crafting XP, and
  `509.1` Agility XP. Before each duty's Magic level, Complete retains the
  source half-Produce/no-Magic-XP/full-secondary-XP rule; Conserve omits the
  under-level duty.
- Rune costs pass through the ordinary Magic equipment substitution helper.
  Every emitted cycle in a review is funded before mutation, so an
  underfunded double emission cannot consume one cycle and strand the review
  transaction halfway through its declared batch.
- The source-blocked distraction fallback is the contract's single global
  calibration: one seeded opportunity per twelve emitted cycles, uniformly
  selecting Sick ibis, Suqah attack, or Murky Pat. An unfunded distraction is
  skipped without blocking the ordinary cycle.
- Cumulative thresholds auto-claim the first ten spells without spending
  Produce. Crossing the cutoff `850,000` capstone claims Borrowed Power,
  spends exactly `850,000`, and preserves the overshoot as the first wish
  balance.

## Storage, runtime, and undo

- Save schema `46` adds and sanitizes the routine, cadence residual,
  distraction residual, completed-cycle count, wallet, lifetime Produce,
  unlock list, and Borrowed Power claim flag.
- The Utility review handler awards all five skill outputs, records one
  successful Livid Farm action, publishes the emitted cycle count, Produce,
  distractions, and unlocks, and persists through the existing review
  transaction.
- A missing-rune boundary performs no cycle mutation and follows the standard
  material-exhaustion redirect to Bankstanding. The message reports the exact
  missing quantities.
- Existing answer snapshots cover inventory, XP, cadence residuals, wallet,
  unlocks, RNG, and target redirection, so review undo restores the complete
  batch.

## Player-facing surface and assets

- Livid Farm is registered under `Utility / Activities` in the
  `Activities / minigames` family and reuses the already normalized,
  provenance-covered Magic skill icon.
- The compact panel exposes the two settled routine policies, current
  Produce-per-cycle, banked Produce, cycle count, staff-adjusted rune cost,
  and segment-relative progress to the next spell.
- Locked fresh players see the disabled target row and exact entry blockers;
  the progress panel appears only when the activity is usable, active, or has
  saved progress.
- Fable and Kimi K3 independently reviewed the new surface. Accepted changes
  force native progress-bar text rendering, keep the policy control compact,
  make progress segment-relative, prefix the target with `Next:`, and replace
  ambiguous `wallet` copy with `banked`.
- A fully quit and relaunched macOS Anki process displayed the new
  `Activities / minigames (1)` group, disabled Livid Farm row, normalized icon,
  and revised Utility copy. The user's low-level save was not modified.
  The unlocked progress state was separately rendered and tested with real Qt
  offscreen; offscreen Qt remains a regression gate rather than evidence of
  the macOS compositor.

## Verification

- Focused pure/runtime/storage/metadata/cadence: `212` tests passed.
- Focused review-transaction integration: `1` test passed.
- Focused real-Qt Livid and mixed-Utility language: `2` tests passed.
- Full non-Qt: `1,793` tests passed with `228` expected environment skips.
- Full real-Qt offscreen: `1,793` tests passed with `1` intentional skip.
- Test-quality audit: `1,793` tests across `78` files, `0` hard issues.
- Documentation audit: `398` Markdown and `368` HTML files passed.
- Compile, diff, and worktree-layout checks passed.
- Reachability remains at the pre-existing `284` orphan inputs and `305`
  blocked actions. Livid Farm adds no item-input orphan.

## Remaining settled implementation

These are implementation dependencies, not design questions:

1. register and connect the ten ordinary Livid spell consumers through their
   owning Magic, Farming, Summoning, inventory, teleport, and multiplayer
   boundaries;
2. Arcane capacitor acquisition, binding, 1,000-cast charging, Borrowed Power
   casting, charge removal, and crumble behavior are now live; see
   `borrowed-power-arcane-capacitor-implementation-2026-07-19.md`;
3. implement the source-ready direct wish commands and their owning-system
   effects; and
4. leave `Let it rain seeds` exact quantities and `Reduce The Fish I Burn`
   magnitude source-blocked until focused evidence exists.

No new creative-direction gap surfaced in this core slice.

Results:

- `memory-bank/status-updates/livid-farm-core-results-2026-07-19.html`
- <https://psq0dddzao84.postplan.dev>
