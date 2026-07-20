# Farming Willow branch acquisition — 2026-07-20

## Scope and cutoff

This audit closes the live acquisition route for `Willow branch` without
changing the settled Farming queue, review clock, or whole-patch harvest
model. The project cutoff remains 2012-11-20. Values below are admitted under
`pre-eoc-source-verification-standard.md`; review-native translations are
labelled separately from source facts.

## Period source

- RuneScape Wiki, `Willow branch`, oldid
  [`6092914`](https://runescape.wiki/w/Willow_branch?oldid=6092914),
  timestamp `2012-08-14T16:12:52Z`.
- The literal revision states that branches are cut from a player-grown
  Willow tree with secateurs or magic secateurs after its health has been
  checked; cutting a branch awards no experience.
- The same revision states that one branch becomes available every five
  minutes and that a maximum of six can accumulate after thirty minutes.
- OpenRS2 revision 742 item configs identify Willow branch as `5933`,
  Secateurs as `5329`, and Magic secateurs as `7409`. These are distinct,
  non-stackable items.

## Executable lineage corroboration

- Darkan commit `ee180fe6045469e491352f6451b65b8e95254ee8`,
  `FarmPatch.java`: a checked Willow increments its branch lives on each
  Farming tick and caps at six.
- The same commit, `HarvestPatch.java`: the Willow harvest product is item
  `5933`.

The executable lineage corroborates the period page's health-check gate,
bounded accumulation, and product identity. It is not used to override the
period revision.

## AnkiScape translation

- A mature Willow begins with zero branches. Time spent mature before the
  one-time health check does not backfill branches.
- The existing Farming clock maps one answered card to six era-minutes. The
  source's five-minute interval is retained exactly in that clock: after the
  health check, one answered card exposes one branch, while five answered
  cards advance thirty era-minutes and expose the full six.
- Pruning is the existing whole-patch harvest collapse. It collects all
  currently accrued branches in one queued action, awards zero Farming XP,
  and leaves the tree standing so branches can regrow.
- Either Secateurs or Magic secateurs satisfies the tool gate.
- Chop remains the primary tree action. A separate contextual
  `Queue prune N branch(es)` action exposes branch collection without
  replacing tree removal.
- A full Farming run uses the ordinary review queue. When it starts from an
  unchecked mature Willow, the health check occurs first; the following
  review advances the Farming clock before the queued prune step.
- No wall clock, free item seeding, ambient timer, or new owner decision is
  introduced.

## Metadata corrections

The prior generic registry defaults incorrectly treated Willow branch,
Secateurs, and Magic secateurs as stackable. Their item IDs and
non-stackability are now explicit. Magic secateurs remain untradeable;
ordinary Secateurs and Willow branches are tradeable.

## Verification

- Pure lifecycle coverage pins the health-check gate, exact 5/30-minute
  accumulation, six-branch cap, both tool options, zero pruning XP, and
  post-prune regrowth.
- Queue coverage pins health check → prune → chop → clear → replant ordering.
- Frontend projection coverage pins Chop as primary and pruning as a separate
  contextual action.
- Real offscreen Qt coverage clicks the branch action and proves the queued
  `harvest` mutation, dark-theme stability, readable action widths, and
  laptop-height reachability.
- Reachability now resolves `Willow branch` through `Farming:willow`.
- Focused pure/integration coverage passes 430 tests. Complete non-Qt and real
  offscreen Qt discoveries each pass all 1,909 tests; the Qt run carries one
  intentional platform skip.
- Kimi K3 returned a SHIP verdict. Its only concrete concern, reachability of
  the taller action stack at 900×560, is now an executable geometry assertion.

## Open findings

- No source value is blocked for this slice.
- No product-design gap surfaced.
- Native restarted-Anki proof is externally blocked while the Mac is locked.
- The mandatory Fable taste pass is externally blocked because its required
  fresh quota probe cannot read Claude Code's macOS Keychain credential
  (`security` exit 51). Neither external QA gate is a source or design
  question.
