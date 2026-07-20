# Livid Farm Farming-owned wishes implementation — 2026-07-19

Status: **implemented and fully verified.**

This record is newer than the dependency notes in
`livid-farm-wishes-implementation-2026-07-19.md` and
`borrowed-power-arcane-capacitor-implementation-2026-07-19.md`. It closes the
two Farming-owned Livid Farm wishes without changing the remaining
`source_blocked` reward rows.

## Evidence

RuneScape Wiki `Livid Farm` oldid `6569596`
(`2012-11-17T21:40:18Z`) establishes:

- `I'd Like a New Patch!` costs 18,000 Produce points, creates one allotment
  patch, and the patch remains until it is cleared for the first time;
- `Protect a Patch for me!` costs 37,000 Produce points and grants a scroll
  that protects a growing ordinary-tree or fruit-tree patch;
- only one scroll protection may be active; and
- one activation protects ten trees of the selected type.

Source: <https://runescape.wiki/w/Livid_Farm?oldid=6569596>

OpenRS2 caches `rev736`, `rev741`, and `rev742` independently expose item
`21515` as `Patch protection scroll` with the `Destroy` inventory option.
The local 2011Scape item configuration corroborates the same ID and name at:

`/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:254845`

The exact RuneScape Wiki file has no pre-cutoff upload available through the
file-history API. The normalized item sprite therefore uses the current exact
`File:Patch protection scroll.png` upload from `2016-05-02` as visual art only.
`assets_provenance.json` records that timestamp and source; it is not mechanics
evidence.

## Implemented behavior

### One-use allotment

- Buying the wish atomically spends 18,000 Produce points and activates the
  hidden-by-default `Livid Farm allotment` in the ordinary Farming sheet.
- A second purchase is rejected without spending points while the patch is
  active.
- The patch accepts the normal allotment plan, queue, compost, gardener,
  watering, cure, harvest, and preset machinery.
- Its first successful harvest or explicit clear empties and permanently hides
  the patch. Any later queued steps for that patch are removed, prepaid
  gardener materials are refunded, its plan is removed, and a stale
  Farming-spell pointer is cleared.

### Protection scroll

- Buying the wish atomically spends 37,000 Produce points and grants the real
  canonical Bank item `Patch protection scroll`.
- The player activates a scroll from an expanded ordinary-tree or fruit-tree
  patch while a healthy tree is still growing. The current tree is the first
  of ten and the persisted protection selector retains nine future uses.
- Later plantings of the selected crop type are protected automatically until
  all ten uses are consumed. A different tree type does not spend a use.
- A prepaid gardener takes precedence so the scroll is not wasted on a crop
  that already has paid protection.
- A second active selection is rejected atomically. Spare owned scrolls remain
  in the Bank for later use.
- The Farming surface exposes one contextual action and a compact remaining-use
  status. It adds no timer and never uses the wall clock.

## Persistence and UI

Storage schema 48 sanitizes the one-use patch flag, selected protected crop,
and remaining-use count. Invalid non-tree selections clear to no active
protection, and remaining uses clamp to the sourced maximum of ten.

`farmingitems/patch_protection_scroll.png` is fetched through the standard
Farming asset pipeline and joined to the canonical item registry. The live
Farming renderer keeps the one-use patch hidden until purchase and shows the
scroll action only on eligible tree and fruit-tree rows. The temporary patch
identifies itself as one-use before the location disappears.

Fable and Kimi K3 independently reviewed all new Livid, Farming, and Combat
surfaces. Accepted findings added a default-No confirmation before destructive
capacitor removal, made the protection action contextual, restored canonical
item naming and singular grammar, exposed the one-use lifecycle, removed
duplicated `Protection` copy, aligned the Borrowed Power action with the Combat
column, and fixed adjacent Warriors' Guild clipping at 900×560. Final Farming
screens were rendered at both 1000×700 and 900×560.

## Verification

- Affected Farming/Livid/Magic/Combat/storage/integration suite: 553 tests
  passed.
- Real offscreen Qt activation, confirmation, one-use identity, and
  supported-size layout checks passed.
- Full non-Qt: 1,830 tests executed with 235 expected environment skips.
- Full real offscreen Qt: 1,830 tests executed with one intentional skip.
- Asset manifest, registry join, provenance, compilation, diff integrity,
  documentation, test-quality, reachability, and guarded-worktree checks
  passed.
- Native Anki was fully quit and relaunched after the final UI changes; the
  canonical add-on opened exactly one dialog and returned cleanly to the deck
  screen without changing the user's save.

## Remaining boundaries

- `Let it rain seeds` remains `source_blocked` on exact period quantities.
- `Reduce The Fish I Burn` remains `source_blocked` on the exact period
  burn-rate magnitude.
- No new owner-facing design gap emerged from either Farming-owned wish.

Results:

- `memory-bank/status-updates/livid-farm-reward-substrate-results-2026-07-19.html`
- <https://9adrft18vuka.postplan.dev>
