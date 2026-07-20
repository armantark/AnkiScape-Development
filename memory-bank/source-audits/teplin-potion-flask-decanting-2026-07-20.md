# Teplin Macagan Potion-Flask Decanting — 2026-07-20

Target cutoff: 2012-11-20, immediately before EOC.

## Period evidence

- RuneScape Wiki `Teplin Macagan` oldid `6225976`,
  `2012-09-09T22:18:35Z`, states that the Oo'glog NPC decants ordinary
  potion vials into potion flasks and vice versa, can convert one- through
  four-dose flasks back into vials, and requires completion of
  `As a First Resort...`.
- RuneScape Wiki `Potion flask` oldid `6394714`,
  `2012-10-13T13:36:46Z`, states that a flask holds six doses, a used flask
  cannot be topped up, an empty flask can be filled when at least six ordinary
  potion doses are available, only one- through four-dose flasks may be
  decanted together, and a flask is destroyed when its potion is decanted
  out.
- Darkan `data/items/config.json` supplies the empty flask item ID `23191`
  and the exact one- through six-dose item identities already pinned in
  `potion_data.py`. Darkan
  `src/main/java/com/rs/game/content/skills/herblore/FlaskPotions.java`
  independently confirms the empty-flask and potion-family cache identities.
  It does not implement Teplin's NPC service and is not used as evidence for
  that dialogue action.

## Live translation

- Teplin appears as an Oo'glog Shop provider with two free, instantaneous,
  inventory-wide services after `as_a_first_resort` is complete:
  `Fill 6-dose potion flasks` and
  `Decant flasks into 4-dose vials`.
- Filling consumes one empty Potion flask per new six-dose flask. It pools
  eligible ordinary one- through four-dose vials and one- through four-dose
  partial flasks, moves exactly six doses per output, and never tops up or
  consumes five- or six-dose flasks. Fully emptied vials return empty Vials;
  fully emptied partial flasks are destroyed; partially emptied containers
  keep their exact lower-dose remainder.
- Reverse decanting converts every eligible one- through four-dose flask into
  as many four-dose vials as possible plus one exact smaller-dose remainder.
  The source flasks are destroyed. Five- and six-dose flasks remain untouched.
- When empty-flask supply cannot cover every family, the service resolves
  potion families in stable catalog order and preserves every unprocessed
  item. This is a deterministic UI abstraction, not a claimed period NPC
  selection order.
- Neither service advances the review-driven shop market clock or any wall
  clock. Each service creates one ordinary Shop event and can be rolled back
  independently through the existing Shop-history undo path.

## Assets and reachability

- `tools/fetch_potion_assets.py` owns the RS3 Wiki visual manifest for the
  empty Potion flask, all registered one- through four-dose vial states, and
  all registered one- through six-dose flask states. These current visual
  files establish icon identity only; they are not gameplay evidence.
- Every fetched file is registered in `assets_provenance.json`, loaded through
  the canonical item registry, and audited by the global tight-crop
  normalization test.
- The item graph now knows Teplin as the producer of each six-dose flask and
  as the reverse conversion from partial flasks to vial states. Empty Potion
  flask acquisition remains a truthful root dependency rather than being
  hidden by a fake source.

## Verification

Focused pure/integration and real offscreen Qt checks cover both access
states, dose conservation, exact container remainders, five-/six-dose
exclusion, direct undo, zero market-clock movement, icon resolution, search
copy, preview copy, and the final two-row geometry: 57 focused non-Qt tests and
one focused real-Qt test pass. Complete non-Qt discovery executes all 1,918
methods with 1,667 ordinary passes and 251 expected environment skips.
Complete real offscreen Qt discovery executes all 1,918 methods with 1,917
ordinary passes and one intentional skip. Documentation, test-quality,
compilation, JSON, diff, icon-normalization, deterministic reachability, and
worktree-safety gates pass.

Kimi K3's taste review found seven concrete presentation defects: the fill
preview omitted consumed empty flasks, singular copy used `(s)`, both actions
shared an icon, the two-row list scrolled, search called a free service
`0 Coins`, the completion toast said `1 time(s)`, and denial copy was too
mechanical. All seven are corrected and regression-covered. A fully quit and
freshly relaunched native macOS Anki process then rendered the final
96-pixel service list without a scrollbar and confirmed distinct icons, free
pricing, the quest lock, and disabled locked action in the real dark theme.

The separately required Fable taste pass remains externally blocked because
the mandatory fresh quota probe cannot read the Claude Code OAuth credential
from macOS Keychain (`security` exit 51). This is a QA/authentication gate, not
an owner design gap. No owner design gap surfaced.
