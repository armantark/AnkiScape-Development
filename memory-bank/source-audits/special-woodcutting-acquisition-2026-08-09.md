# Special Woodcutting acquisition — 2026-08-09

Target cutoff: 2012-11-20, immediately before EOC.

## Result

Arctic pine and Eucalyptus are live Woodcutting gathering targets. Arctic pine
requires level 54, produces one Arctic pine log for 140.2 XP, and unlocks when
The Fremennik Isles starts. Eucalyptus requires level 58, produces one
Eucalyptus log for 165 XP, and has no quest gate. The Eucalyptus route assumes
the settled safe-spot abstraction and does not add ambient combat damage.

The established target selector, hatchet selection, carried-pack behavior,
action telemetry, XP modifiers, persistence, cadence, and review undo apply to
both rows. Existing normalized cutoff log sprites provide their selector art.

## Evidence

- RuneScape Wiki `Arctic Pine` oldid `6069429`, dated 2012-08-09, pins level
  54, 140.2 Woodcutting XP, Arctic pine logs, and the Neitiznot route.
- RuneScape Wiki `Eucalyptus tree` oldid `6491980`, dated 2012-10-28, pins
  level 58, 165 Woodcutting XP, Eucalyptus logs, and the Mobilising Armies
  route that does not depend on the partial As a First Resort... unlock.
- `memory-bank/source-audits/gap-grill-10-woodcutting-provenance-2026-07-10.md`
  records the literal archived-wikitext harvest and the settled access model.
- Rev-742 identities are Arctic pine logs `10810` and Eucalyptus logs `12581`.
- `assets_provenance.json` records the reused Arctic pine sprite at
  `2011-02-16T07:06:55Z` and the Eucalyptus sprite at
  `2011-11-20T20:29:07Z`.

## Honest source boundary

The period sources do not expose either target's success endpoints, depletion
roll, or respawn timer. The registered placeholders
`woodcutting.arctic_pine_rolls` and `woodcutting.eucalyptus_rolls` keep the
shared gathering mechanic live without presenting reconstructed constants as
period facts. Arctic pine uses the nearest-level Mahogany row; Eucalyptus uses
the nearest-level Yew row. Each value is marked beside the data and in
`memory-bank/placeholder-values.md`.

Cursed magic remains outside this slice. Its settled target-local Spirit Realm
mechanic requires Spirit of Summer completion, but that quest has no live
AnkiScape substrate. Adding the row now would create an unreachable target.
The feature remains dependency-blocked for the Darkan quest lane rather than a
new design question.

## Adjacent defect closed

Woodcutting quest locks were enforced by selector metadata but not by the
review-time gathering handler. A saved or direct target state could therefore
bypass a quest gate. The runtime now applies the same pure lock reasons before
every gathering attempt and switches Woodcutting off when an access gate is
not met. The existing dedicated no-hatchet path remains unchanged.

## Verification

- Focused pure/data/runtime/metadata/reachability checks: 416 tests passed.
- Focused review-undo checks: 2 tests passed.
- Focused real offscreen Qt selector check: 1 test passed.
- Full plain discovery: 3,992 tests passed with 487 expected skips.
- Full real offscreen Qt discovery: 3,992 tests passed with 3 skips.
- Documentation: 542 Markdown and 431 HTML files passed.
- Test quality: 3,958 methods across 180 files, zero hard issues.
- Reachability: 1,546 actions, 2,350 reachable items, 162 orphan inputs, and
  181 unresolved actions. Both new logs are reachable.
- Compilation, tracked JSON, diff, asset normalization, and worktree safety
  passed.

Native Anki interaction is not claimed. Manual acceptance in the real profile:
open Skills > Gathering > Woodcutting; confirm Arctic pine is locked before
starting The Fremennik Isles, then enabled afterward; confirm Eucalyptus is
enabled at level 58 with a usable hatchet; train each row and use Anki Undo to
restore the exact prior save.
