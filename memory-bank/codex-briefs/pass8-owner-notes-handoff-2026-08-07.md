# Pass 8 implementation trace

Date: 2026-08-07
Authority: `pass8-owner-fable-decisions-2026-08-07.md`
Starting commit: `659a115c0f6be84c26eeb5cf05a1f1b60ffd0bf1`

This file is the running Pass 8 implementation trace. It does not change the
settled product or visual contracts.

## Batch 1: immediate interaction repairs

### Reproduction

- Fish Flingers entered the event on the first click but did not select it for
  reviews. The selection call was behind an `elif` branch.
- Combat answers could consume food without a player-facing event row. The
  runtime result already contained the consumed-food events.
- Help used the tab-strip corner. The unreleased AnkiWeb review prompt used the
  footer that Pass 8 reserves for Help.

### Change

- One Fish Flingers click now enters the event and selects it for reviews.
- Combat answers aggregate each consumed food item and write
  `Ate N × Item · M left` to the event log.
- Help now sits at the bottom-right of the main menu. The unreleased review
  prompt is removed.

### Automated verification

- `/opt/homebrew/bin/python3 -m unittest tests.test_runtime_actions`: 141 tests
  passed.
- `/opt/homebrew/bin/python3 -m unittest tests.test_fish_flingers`: 16 tests
  passed.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_review_strip`:
  31 tests passed.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget`:
  382 tests passed in 144.508 seconds.
- Frozen read-only checker workflow
  `18151277-e5b5-44d5-aa85-1cc2a0ab6d74` returned `accept` with no findings.

### Native Anki verification

The MacBook Pro Codex Connection used only the disposable add-on and profile
under `/tmp/ankiscape-probe2`. It did not touch the canonical add-on or the
owner's real profile.

- Fish Flingers one-click entry and selection: passed.
- Help at the bottom-right with no review prompt: passed at the normal menu
  size.
- Vanilla answer controls and card-content non-overlap: passed at the normal
  reviewer size.
- Combat food event row: the disposable deck ended before the event could
  render. The follow-up fixture run could not start because host
  `remote-control:env_e_6a684c98946c8321ba89026140dd59e4` disappeared from
  the Codex Connection. This is an external native-evidence blocker, not a
  headless-parity claim. The targeted runtime regression test remains green.

The disposable UI matched all three changed semantic regions and compiled.
Its full-file SHA-256 was
`b22a90e5119f4f46a02a6f116a92a2a25e90291bba4d302376e0666a200e840a`,
not the canonical batch SHA-256
`6b3e19cb01067d9746509686fcf6c7d2cd58b0025472c10400eb864470d99e9c`.
The native report records this unrelated fixture drift. The deployed runtime
matched the canonical SHA-256
`a75614fe222b4e96b9ff041c64d67c3d255f0328e044a6f03ec9c1e60e7a3e02`.

Remote evidence is in
`/tmp/ankiscape-pass8-safe-batch-codex-connection/report.md` on the MacBook Pro.

### Decision

Keep the three changes. Automated coverage and the independent checker accept
the frozen product diff. Native Anki accepts both changed UI surfaces. Record
the combat-log screenshot as blocked until the MacBook Pro Codex Connection is
available again.

## Batch 2: combat auto-burial cadence

### Reproduction

The checked-in combat cadence used one simulated tick for each automatic bone
or ash action. The source action in
`bone_burying.plugin.kts` calls `wait(2)` before it removes the bone and awards
Prayer XP. A frozen regression run produced four expected failures: the
constant was 1, one automatic item returned 1 tick, and two automatic items
returned 2 ticks.

### Change

`AUTO_PRAYER_TICKS_PER_ITEM` is now 2. Manual Prayer training still consumes
one item per review. Bonecrusher, ectoplasmator, and prayer-urn interceptions
do not add automatic-burial ticks.

### Verification

- `tests.test_prayer_passives`: 10 tests passed.
- `tests.test_prayer`: 21 tests passed.
- `tests.test_combat_logic`: 285 tests passed.
- Frozen checker workflow `44a2f316-3e5e-4336-aea4-54af051e5c51`
  returned `accept` with no findings. Its two coverage gaps were converted into
  explicit manual-one-item and bonecrusher-zero-tick regression tests.

### Decision

Keep the one-line production change and its source-bound regression coverage.

## Batch 3: Combat hybrid selector

### Reproduction

Combat bypassed the shared target-selector builder and always rendered a
grouped tree. A focused regression expected the one-row `cockatrice mirror`
search result to use a flat list. It failed because no flat Combat selector
existed.

### Change

Combat now uses the shared hybrid rule after search and Slayer-task filtering:
fewer than 25 grouped results render flat; 25 or more render grouped. The empty
state uses the active widget type. The full catalog remains grouped.

### Verification

- Four focused offscreen Qt selector tests passed.
- The full `tests.test_main_menu_widget` module passed 382 tests in 115.700
  seconds before the final coverage-only additions.
- Two final focused tests passed for the exact 24/25 boundary, flat locked
  rows, flat saved-target highlight and scrolling, and grouped restoration.
- Frozen checker workflow `2796209b-5f8b-48ce-bbdc-bbf4973dbfe0` returned
  `accept` with no findings. Its two coverage gaps became the final focused
  tests above.

### Native evidence

Native MacBook Pro verification is externally blocked. Host
`remote-control:env_e_6a684c98946c8321ba89026140dd59e4` remains unavailable
through the Codex Connection. Do not treat offscreen Qt as native parity.

### Decision

Keep the minimal builder substitution and type-correct empty state. Capture a
native filtered-Combat screenshot when the Codex Connection returns.

## Batch 4: Grand Exchange Bank-run invariant

### Reproduction

A successful buy offer returned no `bank_run_triggered` field. The integration
test failed with `KeyError: 'bank_run_triggered'`. The callback requested a
Bank run only when the pure result contained a non-zero `coins` or `items`
field, so placing buy and sell offers bypassed the run.

### Change

Successful `place_offer`, `collect_offer`, and `collect_all` actions now request
one Bank run. Preview and settings actions do not request a run. The request
remains inside the same direct-action undo transaction.

### Verification

- Focused buy, sell, collect-one, and collect-all integration tests passed.
- The full `tests.test_integration_smoke` module passed 173 tests in 63.222
  seconds before the final coverage-only additions.
- Frozen checker workflow `bf0733dc-2b7f-41ef-b79d-2f9a70f940eb` returned
  `accept` with no findings. Its gaps became explicit checks for collect-all,
  preview and settings exclusions, and exact collection undo restoration.

### Decision

Keep the action-ID gate. It directly expresses the settled buy, sell, and
collection contract without coupling the Bank run to optional result fields.

## Batch 5: player-facing Shop tooltips

### Reproduction

The White scimitar tooltip omitted its level-10 Attack equip requirement and
printed `Darkan Shop.java ...` plus `Darkan shop JSON`. The focused Qt test
failed on the missing requirement and captured both implementation lines.

### Change

Shop stock tooltips now reuse the equipment registry's requirement formatter.
They no longer render raw source or price-source fields. Internal lock reasons
such as `currency_not_implemented` and `unknown_item` are replaced with
player-facing unavailable-item text. No consume requirement was invented: the
current audited item registries do not define a separate level-to-consume
contract.

### Verification

- The focused offscreen Qt test passed for White scimitar and a locked Tribal
  top row.
- `tests.test_shop_logic`: 44 tests passed.
- `tests.test_shop_data`: 14 tests passed.
- Frozen checker workflow `efb8e275-18b6-4012-94c1-42e7fd227a71` returned
  `accept` with no findings. Its lock-reason gap became the Tribal top check.
  Its consume-requirement gap is correctly dormant until a source-backed
  consume-requirement registry exists.

### Native evidence

The MacBook Pro Codex Connection remains unavailable. The Shop tooltip still
needs native proof; offscreen Qt is not native parity.

### Decision

Keep the presentation-only cleanup. Source audit fields remain in the backend
and disappear only at the player-facing tooltip boundary.

## Batch 6: equippable item categories

### Reproduction

White scimitar was registered as `material` even though the same row had a
weapon slot and live equipment data. The strengthened invariant found 266
equippable rows with the same material-category defect. It produced 267
expected failures, including the explicit White scimitar check.

### Change

Equipment metadata enrichment now promotes only the generic `material`
category to `equipment`. It preserves more specific owning categories such as
`smithed` and `tool`. Flat inventory storage keys do not change.

### Verification

- `tests.test_skill_and_item_registry`: 60 tests passed.
- White scimitar is equipment; Iron scimitar remains smithed; Staff of armadyl
  remains a non-equippable material.
- A save-load regression keeps `inventory["White scimitar"] == 2` under the
  unchanged storage key.
- Frozen checker workflow `d6763c57-e5a4-4eb3-96f3-8d672dca357f` returned
  `accept` with no findings. Its storage-key gap became the save-load check.

### Native evidence

The category changes affect the current Bank grouping. Native proof remains
externally blocked with the MacBook Pro Codex Connection and will be covered by
the larger Bank surface batch.

### Decision

Keep the one-condition promotion. It fixes player-use categories without
changing the flat save model or erasing a source system's specific category.

## Batch 7: Black and White Grand Exchange equipment coverage

### Reproduction

The live catalog already contained all 22 registered White equipment rows and
22 registered Black equipment rows after Batch 6. A source-to-registry audit
found four remaining ordinary Black weapons absent from both equipment data and
the Grand Exchange: Black claws (item 3098), Black mace (1426), Black scimitar
(1327), and Black spear (4580). The Iron scimitar sprite was the OSRS-style art
called out in the owner's notes.

Regenerating the pinned Grand Exchange harvest also reproduced a stale-snapshot
gap: 55 registered items already had cutoff-safe price revisions and 56 had
buy-limit rows, but the generated snapshot predated their registration.

### Change

The four missing Black weapons now use their exact 2011Scape equipment blocks,
Attack-10 requirements, weapon types, tradeability, and flat item identities.
Their sprites carry asset provenance. Iron scimitar now uses the explicitly
historical September 2009 RuneScape sprite. The existing Grand Exchange
generator was rerun at its fixed `2012-11-20T00:00:00Z` cutoff; no prices or
limits were authored by hand.

### Verification

- `tests.test_equipment_data`, `tests.test_grand_exchange_data`, and
  `tests.test_skill_and_item_registry`: 82 tests passed.
- Black scimitar, mace, claws, and spear now render as equipment, retain their
  exact source item IDs, and have a period buy limit of 100.
- Period guide prices are 3,282 for Black scimitar, 976 for Black mace, 6,772
  for Black claws, and 283 for Black spear. The generator now tries canonical
  singular page aliases when a plural buy-limit title has no Exchange revision.
- The regenerated snapshot contains 1,414 period prices and 1,728 buy limits.
- Frozen checker workflow `1a27951e-2269-42c6-86d2-98dcf88ae673` exceeded its
  tool-output bound before a verdict. Its partial evidence contained the full
  diff but no finding. Repository-root replacement
  `abb3a659-cfbd-4a15-91d4-99e7c7d0c4c8` repeated the same scope failure.
- Frozen-packet checker workflow `dd6a469f-fbaf-4e31-89d3-90c4fc57ac8d`
  returned `accept` with no required action. It read only the 5,112-byte
  evidence packet. The disposable packet and Git directory were deleted after
  the verdict.
- Both equipment and Grand Exchange generators reproduced their committed
  outputs byte-for-byte in disposable paths.

### Native evidence

The native gate reports MacBook Pro host
`remote-control:env_e_6a684c98946c8321ba89026140dd59e4` as
`thread_list_unavailable`. Grand Exchange and Bank-category proof remains
externally blocked. Offscreen and data tests do not claim native parity.

### Decision

Keep the four-row source repair and the regenerated pinned snapshot. The audit
does not widen the product catalog beyond registered, tradeable, cache-
exchangeable identities.

## Batch 8: owner-settled top tab order

### Reproduction

The menu still opened in the old order: Skills, Shop, Grand Exchange, Quests,
Bank, Equipment, Stats, Challenges, Achievements, Collections, Settings. The
deferred builders were keyed by insertion index, so a direct tab move would
have dispatched Shop, Quests, Achievements, or Collections into the wrong page.

### Change

Deferred builders are now keyed by their page widget. After every tab exists
and before the change signal is connected, the tab bar moves the pages into the
exact owner order:

`Skills | Stats | Bank | Equipment | Shop | Grand Exchange | Challenges | Quests | Achievements | Collections | Settings`

The Gameplay action-multiplier spin also has a stable object name. Its test no
longer assumes that Qt child traversal returns it before every Grand Exchange
spin box.

### Verification

- Four focused offscreen Qt tests passed for exact order, deferred initial
  state, refresh-before-build behavior, and the named Gameplay control.
- Full `tests.test_main_menu_widget`: 385 tests passed in 117.606 seconds.
- Frozen-packet checker workflow `dffc9646-20cd-482b-ace1-f1f228a27a4f`
  returned `accept` with no required action.

### Native evidence

The MacBook Pro Codex Connection remains externally unavailable. Native tab-bar
proof at 1280 by 752 is deferred; offscreen Qt is not native parity.

### Decision

Keep the page-identity deferred map and final tab move. It changes only global
navigation order and preserves first-show construction.

## Batch 9: Bank presentation-state model

### Reproduction

The Bank had no saved tab, position, sort, category, or drop-mode state. It
could not preserve one home tab per item, and it had no review-counted MRU or
date-added values. A focused test first failed because
`logic.bank_layout_logic` did not exist.

### Change

The new pure Bank layout model sits over the unchanged flat inventory. It
stores one home tab and position for each positive item stack. New items append
to the main tab. It also stores tab names, order, owned-item icons, the selected
tab, Manual or computed sort mode, the auto-category setting, and Swap or
Insert mode.

The existing `shop_market_clock.answered_cards` value is the only time source.
A new stack records that review as its date-added and MRU value. A quantity
change updates only MRU. Reconciliation runs on load and at the shared save
boundary, so direct actions use the current answered-review number without a
wall-clock read.

### Verification

- Six focused tests pass for one-home persistence, new-item placement,
  review-only counters, Swap, Insert, tab auto-delete and explicit delete,
  rename, reorder, owned icons, all six sorts, invalid-state repair, and a
  full save/reload projection.
- `tests.test_bank_layout_logic`, `tests.test_cadence_shadow`, and
  `tests.test_skill_and_item_registry`: 73 tests passed.
- Python compilation and `git diff --check` passed.
- The first complete checker workflow
  `b4911585-22a6-4f47-bd6a-a572585146ae` found two defects: downward
  same-tab Swap used the wrong destination after removal, and an extreme saved
  position could place a new item before the main-tab tail. Both defects now
  have regression tests.
- Rechecker `04386882-c8f5-439b-b5a7-8b424d11afb7` found that a main-tab
  owned icon was accepted but not reloaded. The sanitizer now preserves and
  validates that icon. Narrow final rechecker
  `e4a4b1cc-69eb-4e50-9eec-8767760901d6` returned `accept` with no findings.

### Decision

Keep the pure presentation model and shared-save reconciliation. The model is
the tested base for the next Frame A Qt batch. It does not create a second item
store or a wall-clock counter.

## Batch 10: Bank Frame A

### Reproduction

The Bank still used one vertical list. It had no player-facing item tabs,
12-column grid, Swap or Insert controls, sort selector, auto-category control,
or selected-item column. The carried-pack editor also repeated a second Bank
picker inside the same page.

The first Frame A checker found seven defects in the initial repair. Item
selection rebuilt all cells, keyboard users could not organize items, search
counts did not use the selected tab, invalid category drops reported success,
the narrow-window path was not reachable, large quantities could clip, and the
MRU production path was not explained. The accepted repair removes the hidden
compatibility list and uses one visible-grid view model.

### Change

The Bank now uses the section 8 frame parameters: 12 columns of 54-pixel item
cells, an icon-and-short-name tab strip, and a 280-pixel right column. The right
column contains exact selected-item data, item actions, Grand Exchange access,
and the existing 4-by-7 carried-pack editor. The duplicate Bank picker inside
that editor is hidden on the Bank page and stays present on Equipment.

The tab strip supports item drop, drop-to-plus tab creation, tab drag reorder,
rename, an owned-item icon picker, explicit delete, and automatic empty-tab
delete. Item cells support Swap and Insert in Manual sort only. The computed
sorts are read-only. Auto-category headers can be enabled or disabled. Invalid
cross-category cell drops are rejected before Qt advertises or accepts them.

Every item and tab control is keyboard-focusable. Shift-F10 and the Menu key
open item and tab menus. Item menus provide Move earlier, Move later, Move to
tab, and Move to new tab commands. Earlier and later use only visible category
neighbors while auto-categories are enabled. Tab menus provide move-left and
move-right commands. Selecting an item or tab preserves the active controls.

Quantities at or above 100,000 use compact cell text. Exact values stay in the
accessible name, tooltip, and selected-item panel. Search counts apply only to
the selected tab. A refresh now updates selected-item quantity, value, and
eligibility data even when the item remains visible.

### Verification

- Forty-two Bank-focused offscreen Qt tests passed after the final repairs.
- Six pure Bank model tests passed.
- Full `tests.test_main_menu_widget`: 392 tests passed in 124.453 seconds.
- Python compilation and `git diff --check` passed.
- Initial complete checker `d8680f23-6380-4440-b73b-90f734d640cf`
  rejected the first implementation. Corrected complete checker
  `000ed38a-afd7-4710-bc50-2eea335db3d5` found three remaining interaction
  defects: stale selected details, category-unsafe keyboard steps, and rebuilt
  tab focus. Narrow rechecker `03c60d13-4630-48c9-9e06-8b8cf5ab7d48`
  returned `accept` with no required action after those fixes.

### Native evidence

The regular MacBook Pro Codex Connection was checked when the final Bank build
was ready. Host `remote-control:env_e_6a684c98946c8321ba89026140dd59e4`
still reports `thread_list_unavailable`. Native 1280-by-752 proof of Frame A,
the unchanged vanilla answer bar, and card-content non-overlap remains an
external blocker. Offscreen Qt does not claim native parity.

### Decision

Keep Frame A and its keyboard organization paths. The flat inventory remains
the only item store. The saved presentation model remains the only source of
tab, position, sort, category, and drop-mode state.

## Batch 11: Stats skill guide

### Reproduction

The Stats tab had only the selected-skill metrics. It did not show registry
actions, equipment unlocks, level badges, locked rows, a current-level marker,
or current-level scroll behavior. The first pure regression failed with
`ModuleNotFoundError: No module named 'ankiscape.logic.skill_guide_logic'`.
The first Qt regression failed because `statsSkillGuideScroll` did not exist.

This batch started from
`9780fecd9a5ae3f214de2547a714ca7ceabc671e`. The checkout was fully
attributable and the worktree guard reported a safe layout before product
edits.

### Change

The Stats tab now keeps its existing metrics block and uses the full region
below it for an independent skill-guide scroll area. A Stats skill selection
rebuilds the guide. It opens at the first locked boundary so that the next
unlock is visible.

The pure projection reads only the existing target and equipment registries.
It produces Actions and Equipment sections, omits empty sections and target
rows without a level, normalizes Defence to the equipment registry's defense
identity, and does not expose source, shop, drop, or trace fields. Rows keep
their full registry names and sort by level, name, and stable row identity.

Each row puts the level badge on the left. A locked row applies 45-percent
opacity to the complete row, including its badge, icon, and name. Each mixed
section has a labeled current-level divider at its unlocked-to-locked boundary.
This per-section placement is necessary because each named section restarts
its own level ordering. Guide rows have no click controls.

Read-only Opus maker workflow `8ffec6af-0810-4d72-94e4-ebd9d0abe9db`
supplied the frontend structure and styling review. Root made all product
edits. Opus recommended the nested scroll, full-width placement, left badges,
safe deferred scroll, and text-color dimming. The independent checker later
showed that the complete locked row, including its icon, had to dim together,
so root replaced the text-only styling with a row opacity effect. No Fable or
Kimi service was used.

### Verification

- Two pure guide tests passed.
- The combined guide and registry lane passed 62 tests.
- The focused offscreen guide test passed after the whole-row opacity repair.
- All five Stats-filtered offscreen Qt tests passed after that repair.
- The full offscreen `tests.test_main_menu_widget` lane passed 393 tests in
  143.766 seconds before the final opacity-only repair.
- Python compilation, `git diff --check`, and the worktree guard passed.
- Registry audit workflow `60dfeebf-fc89-462f-9d74-df88034a8330` and checker
  workflows `ac568b8d-52e5-406d-a747-d727ef1414c7` and
  `f26cf20c-fcf1-46e2-92bb-5cafb786f15a` exceeded their declared budgets
  before a verdict. Their partial evidence did not report a product defect.
- Complete frozen checker `9cf6ae34-82f3-4bc7-a0aa-eaa644371963`
  correctly found that icons were not dimmed with their locked rows. Root
  replaced child-text dimming with a 45-percent row opacity effect. Its request
  for one guide-wide divider did not fit independently ordered sections.
  Narrow rechecker `0839bd3a-ccd9-4af7-800b-073ab8229fb8` accepted the
  whole-row repair and the per-section boundary interpretation with no
  simplification finding.

### Native evidence

The regular MacBook Pro Codex Connection host
`remote-control:env_e_6a684c98946c8321ba89026140dd59e4` did not appear in
the live thread list when the final guide was ready. The only visible standby
task used the Tailscale SSH host, which the owner explicitly excluded. Native
proof of the changed Stats surface, the unchanged vanilla answer bar, and
card-content non-overlap remains externally blocked. Offscreen Qt does not
claim native parity.

### Decision

Keep the registry-only guide and the per-section current-level boundaries.
The implementation does not create a second unlock database. Native evidence
remains open until the regular Codex Connection is available.

## Batch 12: Collections family and drop log

### Reproduction

Collections still showed only a four-column Music table. It exposed Source and
State columns, had no family navigation, no global total, no combat target
children, and no player-facing drop log. A focused pure test first failed with
`ModuleNotFoundError: No module named 'ankiscape.logic.collection_log_logic'`.

This batch started from
`5be00a73d49835737a6db0a5feb7ec15a92475e0`. The checkout was clean and the
worktree guard reported a safe layout.

### Change

Collections now has a fixed 244-pixel family tree and a wider right detail
panel. Music Log is first. Boss/monster drop log is second, with current combat
targets nested below it. Each family and target row shows an `n/m` count. The
header shows the global collected count. A search field filters only the
selected family or target.

The new pure view uses the current combat registry, current group order,
durable kill counts, and durable observed-drop records. It does not add a
catalog or save field. Empty-drop targets are omitted. Encounter-only targets
remain hidden until their kill record proves that the player met them. Stale
observed items outside the current target registry do not enter a denominator.

Before the first target kill, every item label is `???`, and concealed item
names cannot match search. After one kill, all registry names reveal. Observed
items count as collected and show their historical quantity. Revealed but
unobserved rows show `Not collected` and apply 58-percent opacity to the whole
row, including icon, name, and detail.

Music now renders an unlocked track name or a locked track's player-facing
hint. The old Source and State columns are gone. No source path, oldid, trace,
internal status, or debug label is rendered.

Read-only Opus maker workflow `baa6b94d-6ae6-4efe-859a-1a286d7797ab`
recommended the family tree, nested targets, one selection source, count
placement, list-row presentation, concealed search, and encounter-only guard.
Root made all product edits. Its suggestion to keep the old Music Source column
followed an obsolete test and conflicted with the later Pass 8 no-source
contract, so root removed that column and updated the regression. No Fable or
Kimi service was used.

### Verification

- Sixteen combined Music and Collections pure tests passed.
- The combined pure, migration, and observed-drop integration lane passed 19
  tests.
- Full `tests.test_capes_and_music_ui`: 12 tests passed in 31.795 seconds.
- The real deferred Collections page passed its focused 1280-by-752 offscreen
  geometry and family test.
- Full `tests.test_main_menu_widget`: 394 tests passed in 140.933 seconds.
- Python compilation, `git diff --check`, and the worktree guard passed.
- Repository checker workflow `1feac71a-7fa0-4325-a95a-ce746e69086e`
  exceeded its processed-token bound after six reads and returned no verdict.
  Its partial artifact contained no product finding.
- Frozen-packet rechecker `5a5c9bac-1ab8-40ec-af43-0a4596547312`
  returned `accept` with no simplification finding. Its disposable packet and
  Git directory were deleted after the verdict.

### Native evidence

The regular MacBook Pro Codex Connection host
`remote-control:env_e_6a684c98946c8321ba89026140dd59e4` again reported
`thread_list_unavailable` when the final Collections surface was ready. The
Tailscale SSH path was not used. Native proof of Collections, the unchanged
vanilla answer bar, and card-content non-overlap remains externally blocked.
Offscreen Qt does not claim native parity.

### Decision

Keep the registry-backed Collections family tree and drop log. The existing
observed-drop record remains the only historical ownership source. The current
combat registry remains the only drop denominator.
