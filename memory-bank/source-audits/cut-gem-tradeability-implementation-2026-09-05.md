# Cut-gem tradeability implementation

Scope: ordinary cut Jade 1611 and Red topaz 1613 only.
Source baseline: `6438d42256236992b10d921d4cca920293b55d93`.
Branch: `goal/cut-gem-tradeability-2026-09-05`.
Status: the final `tests/item_tradeability/` package passes source-bound
MacBook focus, post-edit ModuleSurface checks, and complete discovery on both
interpreters. Whole-branch full lanes, post-merge validation, and native
acceptance remain pending. This candidate is not accepted or promoted.

## Settled change

The reviewed period item records qualify both gems for player trading. Remove
their explicit false recipe flags, preserve the existing true default, and
bind the existing source-ID field. Add only the two qualified period prices,
buying limits, and nine-key provenance rows through the existing generator
writer with the complete existing maps. Preserve the global limit source,
cache values, and every other generated entry. The original source responses
and cache outputs stay intact; a measured decoder replay and qualified
provenance correction are retained separately in the source packet.

## Expected public data delta

The complete MacBook comparison confirms the approved semantic allowance below.

- `core/constants.py`: the two selected `CRAFTING_DATA` rows change only
  `tradeable` from false to true and `source_item_id` from null to 1611/1613.
  The corresponding two `ITEM_DEFINITIONS` rows change those same fields.
- `runtime/runtime_actions_carried.py` and
  `runtime/runtime_actions_activities.py`: their public reexports of those two
  objects carry exactly the same field changes.
- Root `__init__.py`: its public `CRAFTING_DATA` carries those changes;
  `GE_ITEM_CATALOG` gains only Jade and Red topaz with the qualified identities,
  guide prices 89 and 157, buying limits 1,000, and exact period provenance.

No public name, function, or signature changes. Four module-surface digest
literals are updated only after complete payload comparison and independent
review; all assertions, module entries, skips, and the Qt override remain intact.
The driver authorized only the existing exact row-count assertions to change
from 1,437 to 1,439 prices and 1,753 to 1,755 buying limits. Their equality,
catalog containment, and cutoff checks remain intact. The measured surface
comparison and driver authorization are recorded below.

## Direct consumer consequences

The unchanged Shattered Heart rule uses registry tradeability to select
replaceable outputs. It can now replace a cut Jade or Red topaz with a
Crafting strange rock. The existing hook test covers forced successful rolls
for each one-gem output and retains its original two-Logs case. The review/GE
persistence test uses the established deterministic draw of 0.5 so a random
rock cannot remove the particular gem that this transaction test must sell.
The real hook remains active in that test, and a separate authored case
covers its replacement path. Both cases passed in the focused MacBook run.

The unchanged Magic alchemy picker also requires a shop buy-price entry. Red
topaz has the existing value 200 and becomes selectable with High 120 / Low 80.
Jade has no entry in that map and remains absent. The original Qt Rune platebody readiness case is preserved byte for byte.
A separate gem-specific case checks Jade absence, the complete Red topaz row
label, its callback, and the spell readiness change after selection. No picker, pricing, or other UI code is changed.
`consumer-reconciliation.json` retains the exact source checks and limits.

## Verification contract

Reuse lean existing test modules for real Crafting output and registry-to-GE
transactions. Verify buy-limit enforcement, escrow, cancellation/collection,
and real dispatcher persistence. Prove all unrelated generated entries are
unchanged with exact before/after map comparison during generation. Product
behavioral tests run only on the driver-owned MacBook mirror. Native recipe,
GE, and persistence checks must run on the authorized disposable profile;
record them as pending until observed. This source worktree does not own that
mirror, native session, or any live profile.

## Authored result and deterministic evidence

The product diff changes two recipe lines and adds six generated rows. The
existing writer first regenerated the unchanged complete input maps to a
scratch file; its bytes matched the original generated module. It then added
only the two reviewed keys to each of the three maps. Exact dictionary
comparison confirmed every preexisting entry and the global limit source
are unchanged. The generated cache-value file was not edited.

`cut-gem-tradeability-implementation-2026-09-05/generation-provenance.json`
retains the actual generation program, source and writer hashes, before and
after output hashes, exact map counts, and comparison results. This was local
deterministic generation. No harvest or product behavioral test ran.

The cohesive `tests/item_tradeability/test_cut_gem_tradeability.py` module contains three new
methods. The two non-Qt methods pass on both MacBook interpreters; the
standalone Qt method passes under Qt and skips under plain Python:

- The pure GE method: for each real gem catalog row, start
  with 999 purchases in the current limit window, buy ten, advance the market,
  and require one fill with nine outstanding, followed by no further fill.
  The larger order makes the first fill discriminate the limit clamp. Collect the one bought
  gem and preserve an unrelated Logs stack.
- The review/persistence method: execute real card-show, answer-show, and
  answer handlers to cut each gem and grant its normal XP. Use the real root
  GE callback to escrow that crafted item. Save through the real storage
  adapter to a fake Anki config endpoint that copies stored values. Reload,
  cancel, collect, and reload again; require the same gem, XP, coins, and
  unrelated Logs stack. Only terminal UI effects and unrelated achievements
  are stubbed. The test uses the runtime context and profile functions to read
  player data, so it adds no dependency on the retiring root state bindings.

The driver ran both behavior selectors and three extended existing methods
before the placement repair. The new standalone Qt case checks topaz
selection and readiness while the original Rune platebody case stays intact.
The complete before/after module payload comparison shows only the approved
semantic allowance. The driver authorized four measured digest replacements;
the post-edit ModuleSurface checks now pass under their existing environment
contract. Full branch suites and native acceptance remain pending. The
two explicitly authorized census expectations count exactly the two added rows.

## Native and persistence acceptance, pending

1. Use the driver-approved disposable profile and fixture, with Crafting 99,
   13,034,431 Crafting XP, one Chisel, at least two Uncut jade, at least two
   Uncut red topaz, 10,000 coins, and seven Logs. Record the fixture and candidate
   hashes first. Do not apply fixture data to the valuable live profile.
2. Select cut Jade in Crafting. Show an Anki card, show its answer, and answer
   successfully once. Confirm one uncut input becomes one Jade and XP rises by
   20 with the normal one-action setting. Repeat for Red topaz and 25 XP. If the
   existing strange-rock rule replaces a gem, confirm the Crafting rock and
   earned XP, then repeat to produce the gem needed for the GE checks; that
   replacement is expected behavior after the tradeability change.
3. Open the existing GE sheet and search each exact cut-item name. Confirm the
   two rows are available with readable names and no truncation. On fresh
   market state, verify the qualified base guide prices are 89 and 157 and
   limits are 1,000; existing market drift after clock advancement remains
   governed by the unchanged market logic.
4. Place a one-item sell offer for each crafted gem at an explicitly entered
   unit price of 89 or 157. Confirm only that gem leaves available inventory
   and is held in the offer. Close and reopen the disposable profile. Confirm
   the open offer and escrow survive. Cancel and collect it, then reopen the
   profile again; confirm the gem returns once, coins and the unrelated Logs
   stack are unchanged, and earned Crafting XP remains.
5. Place a buy offer for each gem and observe a normal fill and collection
   through the existing review-clock flow. Confirm collected items survive a
   profile reopen. The automated pure-market case carries the exact 1,000-item
   limit boundary; do not perform 1,000 manual purchases.

6. With one Jade, one Red topaz, three Fire runes, one Nature rune, and Magic
   99 in the disposable fixture, open Magic's Alchemy bank item picker. Confirm
   `Red topaz (1; H 120 / L 80)` is readable and selectable and that selecting it
   enables Low Alchemy. Confirm Jade is absent under the unchanged shop-price
   gate. This picker check is still pending and introduces no UI change.

These native steps are instructions only. No native browser, Anki, profile,
or MacBook operation has been performed by this implementation agent.

## Static review packet

All seven changed Python files parse, including the empty package marker. The full Crafting source AST differs only
in the two authorized keyword replacements. Static test-quality audit reports
4,689 methods in 246 files, zero hard issues, and 31 existing clone groups.
Documentation audit passes with 659 Markdown and 445 HTML files. The tracked
diff whitespace check passes. These are static checks, not behavioral passes.
The code and test diff is frozen for driver inspection. The focused run and
complete surface comparison are observed. The repaired placement, discovery,
and post-edit ModuleSurface checks passed before the package move. Final package-ID focus and discovery now pass. Full branch lanes, post-merge
validation, and native acceptance remain pending.

## Independent review resolution

Opus confirmed the product diff is correct and minimal. The driver approved
the exact two-row census refresh after independently comparing the complete
generated maps. The direct Shattered Heart and alchemy consequences are now
recorded with coverage in existing methods. The buy order uses ten items so
the first fill proves the clamp; the review-chain RNG is deterministic, with
the actual replacement branch covered separately. The fake config endpoint
binds its loop-local collection explicitly. Product code is unchanged by the
review pass. The later independent evidence review supports four measured
digest replacements, which the driver explicitly authorized. Five focused
cases passed in the earlier placement. The repaired placement and post-edit
ModuleSurface checks now pass; full branch lanes and native checks remain pending.

## Source decoder qualification

The scoped source replay now binds the two selected cache rows to the loaded
core 2.0.5 JAR and rechecked archive inputs. Both replayed row outputs match
the original bytes exactly. The original run's loaded decoder is unrecorded;
the source audit and provenance now state that limit explicitly. The period
wiki item and Exchange records, generated rows, and product/test behavior
are unchanged by this source supplement.

## Driver MacBook evidence and authorized digest update

The driver ran all five supplied selectors successfully: the two new GE and
review/persistence methods, plus the existing Shattered Heart, alchemy-picker,
and generated-row census methods. The retained `mbp/focused.stderr.gz` preserves the exact stderr bytes and
reports five tests in
1.336 seconds and `OK`. This focused result predates the four digest edits.
The retained seven-file SHA-256 inventory describes that earlier placement.
The placement proof separately binds the restored baseline files and new
cohesive module; it does not claim that the earlier run tested this placement.

The complete recursive surface comparison contains 23 payloads: 11 plain and
12 Qt. Sixteen payloads are unchanged and seven change. The unchanged payloads
represent eight common modules; the independent review's phrase “eight
unchanged payloads” is corrected by the measured JSON. Changed constants and
runtime reexports contain only the two gems' tradeability and source-ID field
changes. Root contains the corresponding Crafting changes and two catalog
additions. The named-row comparison preserves all 1,772 existing catalog rows
and adds only Jade and Red topaz, yielding 1,774 rows. Their source IDs, guide
prices, 1,000-item limits, and full provenance match the qualified source rows.

The plain root snapshot could not import `aqt`; this is the existing expected
unavailable environment and is excluded from the 23 successful captures.
Independent Opus evidence review supports four literal replacements: constants,
carried actions, activity actions, and the Qt root digest. The driver approved
only those values from the complete body comparison. Reversing the four new
literals makes `tests/test_module_surface.py` byte-identical to its baseline.
No assertion, module entry, skip, digest-only invocation, or Qt override changed.

The sibling evidence directory retains `mbp/summary.json`, the focused logs,
`mbp/code-hashes.json`, `mbp/full-surface-comparison.json`, and
`mbp/catalog-comparison.json`. `surface-pin-authorization.json` binds their
hashes, the exact old/new literals, the independent review, and the remaining
gates. The review's speculation about the original decoder is not adopted;
the original loaded JAR remains unrecorded.

The driver inspected the four literal edits. Post-edit ModuleSurface checks
now pass on both interpreters under the existing skip contract. Complete
branch plain and Qt lanes, post-merge validation, and native disposable-profile
checks remain pending. No promotion or completed runtime acceptance is claimed.

The focused stderr is stored as deterministic gzip because its original Qt
warning contains a trailing space. Decompression reproduces the exact raw
bytes; the evidence record binds both compressed and decompressed hashes.

## Cohesive test placement after the commit gate

The normal commit hook rejected growth of three existing test files above
1,000 lines. No commit was created, bypassed, or amended. The repair restores
`test_grand_exchange_logic.py`, `test_integration_smoke.py`, and
`test_main_menu_widget.py` byte for byte to their complete baselines. New
coverage lives together in `tests/item_tradeability/test_cut_gem_tradeability.py`. The GE limit
and review/persistence method ASTs are preserved apart from fixture-module
qualification and the explicit exception-safe module lifecycle. The separate
Qt case checks the two gems; the original Rune platebody test remains intact.

Fixtures are reused by module alias. The Qt case composes an existing fixture instance and registers its teardown
after successful setup; it neither inherits nor exports the existing test
class. The fixture registers no unittest cleanups. The review case registers
`sys.modules` restoration before the loop and installs fresh runtime fakes
inside each gem subtest, before setting the main window or loading the add-on. `test-placement-proof.json`
records the whole-file baseline comparisons, method comparison, fixture
dependencies, and new selectors. Product data, generated rows, authorized
digests, census checks, and Shattered Heart cases are unchanged by this repair.

The earlier root placement passed the MacBook selected run and full discovery
check below. The byte-identical package placement now passes its own focused and
discovery verification below. Full branch lanes, post-merge validation, and native
acceptance remain pending. The next commit requires the driver's inspection.

Independent placement review identified two fixture issues. The unused
`doCleanups` call was removed because this unrun fixture has no registered
cleanups and could swallow future cleanup errors. Runtime-fake installation
now occurs once per gem load, preserving the existing pristine reviewer-class
and hook contract. The assertions are unchanged, and method spacing matches
the surrounding suite. `mbp/opus-test-placement-review.txt` retains the raw
review; the placement proof records the resolved findings. The runtime and
discovery evidence below qualifies the earlier root placement; the subsequent
package move retains the test bytes and is verified separately below.

## Source-bound repair verification on the MacBook

Before the package move, the driver ran the repaired gem methods, baseline Rune platebody method,
Shattered Heart method, census method, and ModuleSurface class through the
CLI's normal discovery and selection. Plain Python reports 12 selected tests
in 14.042 seconds, with four skips; Qt reports 12 in 14.468 seconds, with one
skip. Both commands exit 0. All three new methods execute under Qt; both
non-Qt methods execute under plain Python. Each interpreter executes four
ModuleSurface methods successfully and skips the existing root-without-aqt
case under the unchanged environment contract.

The selected count includes the baseline Rune platebody method under two
module IDs. Complete discovery was captured separately for the baseline and
candidate on both interpreters. Each baseline contains 5,562 IDs; each
candidate contains 5,565. A complete multiset comparison adds exactly the
three new gem methods once each, removes no IDs, and preserves every existing
ID's multiplicity. Both Rune platebody IDs already occur in both baselines.
The repair introduces no new duplicate discovery; this statement does not
claim that the baseline has no duplicated cases.

`mbp/repair/verification.json` binds the exact invocations, exit codes, source
hashes, raw logs, and complete discovery lists. All nine recorded source
hashes matched the root-placement candidate at capture, including the 158-line
test module and the three restored baseline files. The placement proof binds
those unchanged test bytes at the new package path; the older source inventory
is preserved and does not claim that the package IDs ran; their separate capture is recorded below. The complete raw logs and lists use deterministic
gzip; decompression was compared byte for byte, and both compressed and raw
hashes are retained. The independent source and surface qualification stays
unchanged. Whole-branch full lanes, post-merge checks, and native disposable-
profile acceptance remain pending.

## Item-tradeability package boundary

The next normal commit hook rejected adding a file to the capped `tests`
directory: `tests: 238 code files (was 237)`. No commit was created, amended,
or bypassed. The unchanged 158-line gem module now lives in the cohesive
`tests/item_tradeability/` package with an empty `__init__.py`. This domain
package can hold the separate cape regression slice after promotion. No
other tests were moved.

The gem module has no path-dependent `__file__`, `ROOT`, or `Path` reference.
Its fixture imports are unchanged, and those fixtures resolve their own
paths. No source adjustment was needed. The new CLI discovery IDs begin with
`item_tradeability.test_cut_gem_tradeability.CutGemTradeabilityTest`; explicit
unittest imports add the `tests.` prefix. `test-placement-proof.json` binds
the package marker, unchanged module hash, and exact selectors. The driver
verified the three method bodies once each at the new discovery IDs before
authorizing the next new commit. The previous MacBook evidence remains a historical
root-placement capture.

## Final package verification

The separate package-placement MacBook run reports 12 selected tests in
13.960 seconds with four skips on plain Python, and 12 in 14.544 seconds with
one skip under Qt. All commands exit 0. Both non-Qt gem methods execute in
each interpreter; the alchemy method executes under Qt. The post-edit
ModuleSurface methods pass under the same existing environment contract.

Complete discovery contains 5,565 IDs in both candidates against 5,562 in each
retained baseline. A new multiset comparison adds only the three
`item_tradeability.test_cut_gem_tradeability` methods, once each. It removes
no IDs and preserves every existing ID's multiplicity. All ten captured
source hashes match the final package candidate, including the empty marker,
unchanged test body, product files, pins, and restored baseline test files.

`mbp/package-placement/verification.json` binds the separate exact commands,
exit codes, source inventory, raw logs, candidate lists, and references to the
retained full baseline lists. Raw streams use deterministic gzip with both
raw and stored hashes. The earlier root-placement captures are unchanged.
Whole-branch full lanes, post-merge checks, and native acceptance remain pending.
