# Cadence live activation verification — 2026-07-17

Status: implemented and verified in the canonical checkout.

Contract: `memory-bank/cadence-kernel-contract-2026-07-13.md`.
Owner brief: `memory-bank/codex-briefs/cadence-kernel-live-activation-2026-07-17.md`.
Evidence ledger: `memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`.

## What became live

- `R = 1000` exact integer/rational scheduling is default-on. Only an explicit
  boolean `ankiscape_cadence_kernel = false` selects the legacy handler and RNG
  path.
- All 2,197 selectable foreground routes and every implemented answer handler
  have an auditable declaration in `cadence_coverage.py`. Validation rejects a
  newly registered handler with no declaration.
- Compatible ranged XP/hour evidence uses the labeled conservative
  `lower_source_endpoint`; no midpoint is invented. Source ranges remain intact
  in `tools/sourced_xp_rates.py`.
- Compatible Mining, Woodcutting, Fishing, Hunter, Cooking, and Firemaking rows
  moved from shadow-only observation to live admission. Exact High Alchemy,
  superheat-mithril, dragonhide-body, elemental-battlestaff, and
  gilded-altar-dragon-bones rows are also live when their cited runtime
  conditions match.
- Thieving retains its already-live target scheduler with no second cadence
  gate. Failed wall-safe attempts preserve that target scheduler while true
  pre-action rejections restore the outer residual.
- Source-blocked rows remain playable through their approved existing handler.
  A cadence wait remains distinct from an authentic failed attempt.

## Evidence corrections made during activation

- Mining iron now has separate P2P 35–38k XP/hour, dropping-only evidence and
  F2P 45k XP/hour, urn-inclusive evidence. Live Drop mode uses the compatible
  P2P lower endpoint so urn XP is not counted twice.
- Barehand black warlock catching uses the sourced 140k XP/hour and 650 Hunter
  XP per catch row, including its attached 125 Agility XP.
- The mixed trout/salmon rate remains source blocked because forced admission
  does not yet preserve the source output blend.
- Hunter rows whose runtime XP per action differs from the cited row remain
  source blocked: chinchompa, black salamander, spotted kebbit, and dark kebbit.
- Shark cooking remains source blocked until the cited cooking-gauntlet burn
  behavior exists. Keep-and-bank configurations remain source blocked when the
  compatible rate explicitly includes dropping.

## Combat continuity

Ordinary Combat advances exactly `6 × M` immediate game ticks per successful
review. Encounter state now persists player/enemy attack countdowns, enemy LP,
curse ramp progress, Prayer drain phase, combat statuses and temporary effects,
special-attack regeneration residual, supplies, familiars, and RNG phase.

Terminal kill, reflection kill, death, flee, and bank boundaries end the review
without spawning a second enemy. Again advances established world/passive
consumers but no combat tick and preserves the wounded encounter for later
re-engagement. Quest combat remains one finite collapsed stage per eligible
review and cannot turn a large stage tick budget into repeatable XP or loot.

## Verification

- Focused cadence/kernel/parity/combat/runtime/Summoning/Thieving: 528 passed.
- Full pure discovery: 1,474 methods; 1,273 passed and 201 expected
  environment-only skips.
- Full real offscreen Qt discovery: 1,474 passed, zero skips.
- Test-quality audit: 1,474 tests across 71 files, zero hard issues.
- Documentation audit: 255 Markdown and 305 HTML files passed.
- Reachability regression, fetch-assets, and worktree-guard tests: 11 passed.
- `assets_provenance.json` parses and the asset tree contains no zero-byte files.
- `python3 tools/worktree_guard.py audit`: safe canonical layout.

## Manual Anki checklist

1. With no cadence config key, answer one Combat card and confirm the encounter
   advances a short slice rather than the former 50-tick burst.
2. Answer Again during a wounded encounter, then re-engage; confirm enemy LP
   and attack phase were preserved and no combat resource was spent on Again.
3. Select a source-ready rare gathering route in Drop mode; confirm cadence
   waits are labeled as waits and do not increment failure counters.
4. Undo a successful action, an authentic Thieving failure, and a combat slice;
   confirm inventory, XP, risk state, and cadence residual all return together.
5. Set `ankiscape_cadence_kernel` to boolean false and confirm the legacy
   multiplier/burst behavior returns; remove the key afterward to restore live
   cadence.

## Remaining dependency outside this activation

The Summoning contract permits Pack Yak Winter Storage at a safe boundary, but
there is not yet a target-familiar automation policy schema for automatic
pre-reengagement top-up. That is a Summoning automation implementation
dependency, not a cadence design fork, and no cadence value was invented for it.
