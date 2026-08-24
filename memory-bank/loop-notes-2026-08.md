# AnkiScape grind-loop notes — 2026-08

## Iteration 62 — Ranging Guild implementation checkpoint

- Source: reused Darkan's frozen contract, canonical commit
  `6e9bf37f85caf9c47f877d571fddc308ceffbaf4`, four cutoff wiki revisions,
  and rev-742 item identities. No duplicate harvest was performed.
- Result: effective level-40 entry, 200-Coin fee, ten supplied Bronze arrows,
  one shot per review, six exact score/XP bands, Hati-paws scope, one replay-
  safe ticket claim, six purchases, persistence, undo, Seers diary conditions,
  normalized art, review-strip Ranged state, and Activities UI are live.
- Honest boundary: `ranging_guild.hit_quality_resolver` remains the registered
  frozen bounded placeholder because the period hit-quality formula is not
  recovered. Hati-paws acquisition remains data depth.
- Review: Kimi K3 and Fable independently reviewed the UI. Accepted changes
  hide lobby progress, explain score-to-ticket conversion, label ticket units,
  distinguish claim-ready state, improve band copy, keep Purchase secondary,
  and use a theme-safe claim pill. A bounded Sol simplification leaf exhausted
  its processed-token budget without a verdict; root retained deletion review.
- Verification at final pause: focused plain coverage passes 120 tests with one
  expected Qt skip; focused real offscreen Qt passes 16 tests. Full plain
  discovery passes 4,053 tests with 494 expected skips. The first full Qt lane
  exposed two stale Activities inventory assertions. Their direct rerun passed
  after the test-only correction. Full offscreen Qt then passed 4,053 tests with
  three expected skips. Documentation, test quality, compilation, JSON,
  placeholder, asset normalization, diff, reachability, and worktree checks pass.
- Native proof: one real AnkiScape menu opened and showed the current separated
  Activities navigation. Computer Use returned `AXError.notImplemented` on the
  non-accessible Minigames row, so the native detail panel is not claimed.

## Iteration 41 — Crafting and Fletching potion runtime

- Source: game-main `PotionType.kt`/`Potion.kt`, rev-742, eight cutoff Exchange
  revisions, and Wimpy bird oldid `5936660` pin exact `+3`, item identities,
  dose chains, market rows, and the missing Hunter ingredient route.
- Result: target-local policies, temporary current levels, the shared review-
  tick restoration clock, boosted gates, Casual and Advanced carried-pack
  behavior, direct drinking, dose replacement, persistence, and undo are live
  through one shared runtime. Schema advances to 113; no wall clock exists.
- Adjacent repair: the old `catch_wimpy_bird` row's copied Stripy-feather output
  is now the sourced minimum five Wimpy feathers. Exact item ID `11525` and the
  existing normalized 2010 sprite complete the fresh-profile Fletching-potion
  acquisition chain. The Super prayer/Fletching flask-ID collision is also
  corrected.
- UI and taste: the policy stays inside each target's existing Details card.
  Fable directly reproduced and closed an invisible dark-mode indicator. Kimi
  K3 returned `SHIP` on the corrected bounded transcript after its provider
  could not read local PNG paths. Advanced targets remain locked until the
  saved layout permits a matching owned dose.
- Delegation: read-only Sol-high Workflows run
  `03fc9963-0e4b-48d3-9060-4ec3c3035031` exceeded its 80,000-byte tool-output
  budget at 92,129 bytes without a verdict. Root independently found and fixed
  pre-material dose consumption, Advanced bank reach, the Hunter output/icon
  omission, and the Advanced target-lock seam.
- Verification: full plain and real offscreen-Qt discovery each pass 3,939
  tests, with 483 plain skips and 3 Qt skips. Documentation audits cover 534
  Markdown and 431 HTML files; test quality has zero hard issues across 3,905
  tests in 178 files. Reachability is 1,537 actions and 2,333 items, with 168
  known orphans and 188 known blocked actions. Compilation, tracked JSON, diff,
  provenance, normalization, and worktree safety pass.
- Native proof: a fully restarted Anki 25.09.4 process registered one bridge;
  the real deck button dispatched one call and WindowServer listed exactly one
  `AnkiScape Menu`. macOS was locked at `loginwindow`, so no native visual
  Details-card claim is made.

## Iteration 40 — Trouble Brewing The stuff and mature ale

- Source: Brewing oldid `6447660`, The Stuff oldid `6447071`, Honest Jimmy
  oldid `6393015`, rev-742, and Darkan's reconstructed Brewery pin the recipe,
  additive purchase, item identities, level, XP, and batch outputs.
- Result: one five-Piece `The stuff` reward and two full-vat Dwarven stout
  targets are live. Both branches consume complete ingredients, return two
  buckets, award eight drinks and 215 XP, persist, and use direct undo. Ordinary
  ale is an alternate completed outcome rather than a burn.
- Honest limit: the exact mature roll is not period-recovered. The Darkan 10%
  natural / 75% additive values are registered as
  `cooking.dwarven_stout_mature_chance` until a period server routine settles
  them. No wall-clock fermentation exists; one review represents the vat.
- UI and art: the existing reward combo and grouped Cooking selector expose the
  reward and recipe without a new panel. The stuff, ale yeast, and mature stout
  use normalized cutoff sprites. Fable found no content defect after the
  corrected expanded-group capture. Kimi K3's required independent pass is
  provider-blocked by HTTP 403 despite a nominally available quota preflight;
  this is recorded without claiming approval.
- Delegation: bounded Sol-high Workflows run
  `b25b2838-eb40-40f2-a9bb-18ed27460023` exhausted its 30,000-byte tool-output
  limit on a 118,077-byte multi-path diff before a verdict. Root retained final
  review, reproduction, and verification ownership.
- Verification: 491 focused non-Qt checks and three focused real Qt checks pass.
  Full plain and real offscreen-Qt discovery each pass 3,927 tests, with 482
  plain skips and 3 Qt skips. Documentation audits pass across 533 Markdown and
  431 HTML files; test quality has zero hard issues across 3,893 tests in 177
  files. Reachability is 1,513 actions and 2,316 items, with 170 known orphans
  and 190 known blocked actions. Compilation, tracked JSON, diff, placeholder,
  normalization, and worktree safety pass.
- Native proof: after fully quitting the stale Anki process and relaunching it,
  the canonical add-on opened one menu and showed the updated Cooking prompt
  plus the two-row Brewing group. The check did not train, purchase, or mutate
  gameplay state.

## Iteration 39 — Trouble Brewing medium-clue service

- Source: Honest Jimmy oldid `6393015` pins the direct 5,000-Piece medium-clue
  purchase. Treasure Trails oldid `6473708` and superseding owner answer 4.5
  pin one clue total. Rev-742 and game-main pin readable item `2801`, stacking,
  trade rules, and the clue family's shared model `3374`.
- Result: the reducer asks Treasure Trails' central ownership helper before it
  charges, awards one canonical medium clue, and uses the existing direct undo.
  The view exposes the blocker; Qt renders the formatted price, held-clue state,
  and ownership/wallet guidance. Canonical Combat item metadata now carries the
  exact ID instead of being overwritten by a second activity registration.
- Art and taste: the surface reuses normalized 2010 hard-clue art because the
  period client proves the exact shared model; the 2019 medium fallback does not
  represent period evidence here. Kimi K3 and Fable converged on formatted
  thousands and explicit disabled-state guidance. Neither review claims native
  Anki appearance.
- Boundaries: medium trail steps/rewards remain honest catalog depth, and the
  Bank already explains the tier lock while preserving the clue. `The stuff`
  remains separate. No schema, wall clock, placeholder, or owner decision was
  added.
- Delegation: read-only Sol-high Workflows run
  `8fd4bb0f-b6b3-48a8-9148-9ac06549b094` exhausted its declared tool-output
  budget at `54,375/50,000` bytes before a verdict. Its partial artifact held no
  candidate defect; root independently reproduced the ownership seam and found
  the duplicate-item ownership hazard. This slice is GPT-family verified by
  execution.
- Verification: 243 focused non-Qt checks and four focused real Qt checks pass.
  Full plain and real offscreen-Qt discovery each pass 3,922 tests, with 482
  plain skips and 3 Qt skips. Documentation audits pass across 532 Markdown and
  431 HTML files; test quality has zero hard issues across 3,888 tests in 177
  files. Reachability remains 1,511 actions and 2,315 items; the known
  168-orphan/188-blocked ledger is unchanged. Compilation, tracked JSON, diff,
  deterministic asset enumeration, normalization, and worktree safety pass.

## Iteration 38 — Trouble Brewing rum teleports

- Source: Honest Jimmy oldid `6393015` and rum oldid `6088748` pin both
  two-Piece, one-use, same-destination rums. Rev-742 pins IDs `8940` / `8941`,
  non-stackability, non-exchangeability, `Drink`, and the recolour distinction.
- Result: both rums are canonical purchases. Bank drinking consumes one through
  direct undo, records arrival at Trouble Brewing, preserves state on refusal,
  and is disabled while the activity's temporary inventory is live. The source
  sprites are normalized and visible in the 29-row shop selector.
- Taste: Kimi K3 and Fable independently reviewed the added surfaces. Accepted
  findings enlarge the narrow bottle icon box to `24 × 24`, enable QMenu
  tooltips, state consumption explicitly, block mid-match use before click, and
  replace ambiguous scoreboard labels. Neither review claims native Anki
  appearance.
- Boundaries: exact map tile, animation, dialogue, and server handler remain
  source-omitted and unnecessary in the locationless direct-action model. The
  medium clue service and `The stuff` remain separate slices. No schema, wall
  clock, placeholder, or owner decision was added.
- Delegation: read-only Sol-high Workflows run
  `ce441532-78d4-4051-89f6-512a922793cb` exhausted its bounded output allowance
  at `169,954/120,000` bytes before findings. Root independently reproduced the
  source and cache rows. This slice is GPT-family verified by execution.
- Verification: 210 focused non-Qt checks and four focused real Qt checks pass.
  Full plain and real offscreen-Qt discovery each pass 3,919 tests, with 481
  plain skips and 3 Qt skips. Documentation audits pass across 531 Markdown and
  431 HTML files; test quality has zero hard issues across 3,885 tests in 177
  files. Reachability is 1,511 actions and 2,315 items; the known
  168-orphan/188-blocked ledger is unchanged. Compilation, tracked JSON, diff,
  deterministic asset fetching, normalization, and worktree safety pass.

## Iteration 37 — Trouble Brewing cosmetic reward catalog

- Source: corrected cutoff oldids `6579342` / `6393015` pin the complete
  27-row cosmetic catalog and exact `50`–`600` Piece prices. Rev-742 and
  game-main pin item IDs, slots, zero bonuses, flag weapon type, attack speed,
  and two-handed state. The older migrated IDs now resolve to unrelated pages.
- Result: all seven three-piece naval colour sets and six flags are canonical
  atomic purchases with direct undo, Bank/equipment behavior, normalized
  sprites, and item icons in the existing reward selector. Multi-row testing
  found and fixed stale Buy availability after selection changes.
- Taste: Kimi K3 and Fable independently requested a currency unit on every
  row. The accepted `PoE` suffix stays compact; both found the remaining icon,
  dark-mode, state-feedback, and density behavior clean. Neither review claims
  native Anki appearance.
- Boundaries: rums, the medium clue service, and `The stuff` remain three
  separate source-ready mechanic slices. No schema, wall clock, placeholder,
  or owner decision was added.
- Delegation: Workflows run `99ac32cb-3ac4-4fa4-8119-dd36e6153213` exhausted
  both leaves' skill-read output budgets before findings. Root independently
  reproduced both cutoff revisions and all 27 cache/equipment rows. This slice
  is GPT-family verified by execution.
- Verification: 141 focused non-Qt checks and four focused real Qt checks pass.
  Full plain and real offscreen-Qt discovery each pass 3,916 tests, with 480
  plain skips and 3 Qt skips. Documentation audits pass across 530 Markdown and
  431 HTML files; test quality has zero hard issues across 3,882 tests in 177
  files. Reachability is 1,511 actions and 2,313 items; the known
  168-orphan/188-blocked ledger is unchanged. Compilation, tracked JSON, diff,
  deterministic asset fetching, normalization, and worktree safety pass.

## Iteration 36 — Shades of Mort'ton bronze-chest catalog

- Source: cutoff oldid `6449451` fixes the bronze reward families and
  better-colour quality direction. Fresh Darkan iteration 399 / commit
  `4d72f80f3e7ad56a712b4e38653f01cedaeeb289` reconstructs all 23 identities,
  quantities, group sizes, three live key modifiers, and the ascending server
  group order. Hidden probabilities, Ring of Wealth behavior, and paste chance
  remain `provisional/darkan` and `source_blocked`.
- Result: the existing atomic chest action reaches all 23 rewards, rolls exact
  inclusive quantities, and uses the central one-clue filter. The ghost `Steel
  axe` is gone. Both missing poisoned daggers now have canonical equipment
  rows, cutoff art, and exact period buy limits.
- Boundaries: higher shade/key/chest tiers remain data depth. No UI, schema,
  wall clock, placeholder, design fork, or quest-parity implementation was
  added.
- Delegation: read-only Sol-high Workflows runs
  `a08a2db5-41e8-4d35-8558-4496ad556632` and
  `7749376d-7e60-4493-bc15-b833ed5e0d1e` exhausted their bounded output/token
  guards before findings. Root independently reproduced the table and server
  ordering and completed the simplification review. This slice is GPT-family
  verified by execution.
- Verification: 73 focused pure/integration/registry/asset tests and four
  focused real Qt checks pass. Full plain and real offscreen-Qt discovery each
  pass 3,914 tests, with 480 plain skips and 3 Qt skips. Documentation audits
  529 Markdown and 431 HTML files; test quality has zero hard issues across
  3,880 tests in 177 files. Reachability is 1,511 actions and 2,287 items; the
  known 168-orphan/188-blocked ledger is unchanged. Compilation, tracked JSON,
  diff, deterministic asset fetching, normalization, and worktree safety pass.

## Iteration 35 — Great Orb Project teleport tablets

- Source: Great Orb Project oldid `6564759`, timestamp
  `2012-11-17T03:12:07Z`, pins the complete 14-row shop, exact prices,
  stackable single-use exterior teleports, ordinary altar-entry requirement,
  and Cosmic/Astral/Law/Death/Blood gates. OpenRS2 cache 544, rev-742, pins
  items `13598` through `13611`, non-exchangeability, stacking, and `Break`.
- Result: all tablets are canonical one-at-a-time GOP purchases. Bank `Break`
  consumes one through direct undo. Altar tablets queue the existing Wicked-
  hood route seam and skip only the next matching outbound leg; the Guild
  tablet records Guild arrival without a route waiver. Refusals preserve the
  item, tablet use never grants altar access, and final-unit consumption now
  reconciles the carried-pack view instead of leaving a ghost copy.
- Boundaries: the Law restriction reads equipped gear and the active carried
  pack because the flat Bank is storage, not physical inventory. The sourced
  zero-bonus Law talisman staff remains allowed. Membership is period catalog
  metadata. No world-map substrate, wall clock, schema field, placeholder, or
  owner decision was added.
- Taste: Kimi's fresh five-hour quota was exhausted. Claude's supported quota
  preflight was unavailable because its endpoint was rate limited, and Fable
  remains reserved. Neither guard was bypassed. Root inspected the 14 source
  sprites together and exercised the existing fixed-size shop and Bank-menu
  surfaces through the complete 395-test real Qt widget module.
- Delegation: read-only Sol-high Workflows run
  `f4853879-99e6-4681-bf75-9c28ea58fd00` exhausted both leaves' mandatory
  bootstrap output budgets before findings. Root independently reproduced the
  sources, verified the live seam, and completed the bounded simplification
  review.
- Verification: 269 focused pure/integration/immutability tests and all 395
  real Qt widget tests pass. Full plain and real offscreen-Qt discovery each
  pass 3,908 tests, with 480 plain skips and 3 Qt skips. Documentation audits
  528 Markdown and 431 HTML files; test quality has zero hard issues across
  3,874 tests in 177 files. Reachability improves to 1,511 actions and 2,284
  items while the known 168-orphan/188-blocked ledger is unchanged.
  Compilation, tracked JSON, diff, deterministic asset fetching, UI-asset
  normalization, and worktree safety pass.

## Iteration 34 — Great Orb Project talisman staves

- Source: Runecrafting-staff oldid `6430449`, pre-EOC Air/Omni oldids
  `6080692`/`6080707`, the cutoff child identities, and rev-742 pin the
  10,000-token base staff, twelve ordinary bindings, free Korvak conversion,
  altar-access rules, Law exception, item IDs, and equipment stats. No binding
  XP is claimed because no inspected period record awards it.
- Result: the base purchase, ordinary review bindings, direct Omni conversion,
  quest-gate inheritance, shared equipment/Bank behavior, altar capacity,
  review/direct undo, and fourteen normalized sprites are live. Binding now
  declares real carried-pack recipes; this also repairs the older tiara rows'
  direct-bank bypass. Save repair now recognizes equipped Omni-tiara/staff
  outputs, closing a one-time 13,605-XP reclaim hole.
- Boundary: the sourced Abyss-eye distraction remains recorded but inert
  because AnkiScape has no Abyss substrate. Teleport tablets remain the next
  separate depth slice. No placeholder, schema migration, wall clock, or owner
  design decision was added.
- Taste: the complete 394-test real Qt widget module passes. Kimi's fresh quota
  preflight reported five-hour usage `100.0%` and weekly usage `33.0%`, so the
  K3 call failed closed; Fable remains reserved under the owner's later rule.
  This slice adds rows to existing selectors rather than a new UI pattern.
- Delegation: read-only Sol-high Workflows run
  `ccc8d0ca-9497-4dfe-bd85-8525c6fd0d85` exhausted its tool-output guard at
  `60,675` observed bytes against `50,000` after one bounded diff and returned
  no findings. Root used only the partial status, completed the simplification
  review locally, and fixed the equipped-Omni reclaim hole.
- Verification: 413 focused pure/integration tests pass. Full plain and real
  offscreen-Qt discovery each pass 3,903 tests, with 479 plain skips and 3 Qt
  skips. Documentation audits 527 Markdown and 431 HTML files; test quality
  has zero hard issues across 3,869 tests in 177 files. Reachability improves
  to 1,511 actions and 2,270 items with the known 168-orphan/188-blocked ledger
  unchanged. Compilation, tracked JSON, diff, deterministic asset fetching,
  UI asset normalization, and worktree safety pass.

## Iteration 33 — Great Orb Project standard Runecrafter robes

- Source: robes oldid `6327369`, talk oldid `5565562`, and rev-742 pin three
  colours, 12 exact 1,000-token identities, equipment slots/stats, and an
  activity-only per-piece XP effect. The unrecovered magnitude is registered
  as a bounded 0.25% per-piece placeholder, at most 1% over four slots.
- Result: all purchases, direct undo, shared inventory/Bank/equipment behavior,
  mixed-colour GOP-only XP, fractional match tracking, and normalized selector
  art are live. Nine assets are cutoff-qualified; three renamed hat sprites are
  labeled visual-only fallbacks.
- Taste: root inspected the real 1200×760 dark render. Kimi's fresh five-hour
  window was exhausted and Opus's preflight was unavailable; neither guard was
  bypassed. This extends the existing selector without a new UI pattern.
- Delegation: read-only Workflows run
  `39cf4d5c-611c-4b9a-bb6a-f46653c1c7b2` crossed its tool-output limit by 432
  bytes after two source reads and returned no findings. Root reproduced the
  evidence and reviewed the complete diff. The required diff-only
  simplification run `2bc0904b-34fc-43db-bf38-a67700d8a5a9` then left its
  five-file boundary and failed closed at 63,810 processed tokens before
  findings; root completed that bounded review locally with no valid deletion.
- Verification: full plain and real offscreen-Qt discovery each pass 3,897
  tests, with 479 plain skips and 3 Qt skips. Documentation audits 526 Markdown
  and 431 HTML files; test quality has zero hard issues across 3,863 tests.
  Reachability improves to 2,256 items with the known 168-orphan/188-blocked
  ledger unchanged. Compilation, JSON, diff, asset fetch/normalization, and
  worktree safety pass. Staves and tablets remain separate depth.

## Iteration 32 — Great Orb Project Master Runecrafter robes

- Source: Master Runecrafter robes oldid `6514332`, its four cutoff child
  revisions, and rev-742 pin four 15,000-token items, exact equipment stats,
  0.8/1.6/1.2/0.4% piece rates, the extra 1% full-set bonus, and the 700-XP
  bonus cap.
- Result: all four purchases, equipment rows, normalized source sprites, and
  shared XP behavior are live. Ordinary altar crafting and Great Orb Project
  both award the same source-defined bonus; Great Orb status, telemetry,
  persistence, and undo observe the awarded total.
- Taste: Kimi K3's ordering, number-formatting, and status-XP findings were
  reproduced and fixed. Root inspected the real 1200×760 dark render. Opus
  failed closed at its supported OAuth/quota preflight and was not bypassed.
- Delegation: Sol-high run `17f8d113-af59-44e0-a170-9acd022b70ec` exhausted its
  90,000 processed-token guard at 121,271 before findings. Root preserved the
  partial result and completed the bounded simplification review locally.
- Verification: full plain and real offscreen-Qt discovery each pass 3,895
  tests, with 479 plain skips and 3 Qt skips. Standard robes, staves, and
  tablets remain separate depth. Documentation audits 525 Markdown and 431
  HTML files; test quality has zero hard issues across 3,861 tests. Reachability
  improves to 2,244 items with the known 168-orphan/188-unresolved ledger
  unchanged. No placeholder or design gap surfaced.

## Iteration 31 — Great Orb Project ordinary talismans

- Source: Great Orb Project oldid `6564759` pins all ordinary talismans except
  Death and Blood at 50 free-to-play or 125 members tokens; rev-742 and the
  authentic item table pin the ten exact identities.
- Result: all ten ordinary rows are live, one-at-a-time atomic purchases. The
  outputs reuse the complete Runecrafting item graph and direct-action undo.
  The existing reward selector now shows their already-provenanced art at a
  fixed 24-pixel size.
- Boundary: standard robes expose an unresolved in-minigame XP effect. Master
  robes were closed in iteration 32; staves and tablets remain separate depth.
- Taste: Kimi K3 returned `NO_BLOCKER`; root inspected the real 1200×760 dark
  render. Opus failed closed at its stale quota preflight on three attempts and
  was not bypassed.
- Verification: 280 focused pure/integration/undo/registry tests and one real
  Qt selector test pass. Full discovery passes 3,891 tests in both lanes, with
  479 plain skips and 3 Qt skips. Documentation audits 524 Markdown and 431
  HTML files; test quality reports zero hard issues across 3,857 tests in 177
  files. Compilation, tracked JSON, diff, asset-normalization, and worktree
  audits pass. Reachability is unchanged at 1,499 actions, 2,240 reachable
  items, 168 orphan inputs, and 188 unresolved actions. No placeholder or
  design gap surfaced.

## Iteration 30 — Mage Training Arena reward catalog

- Source: Mage Training Arena oldid `6491109` supplies all 25 exact shop rows;
  rev-742 pins the new item/rune identities; authentic game-main definitions
  pin modeled equipment bonuses and skill requirements.
- Result: the complete cutoff catalog, canonical outputs, wand chain,
  Infinity/Mages' book equipment, source sprites, atomic purchases, existing
  persistence/undo, and both icon-bearing selectors are live. One end-to-end
  Battlestaff proof exercises all four room loops without repeating thousands
  of redundant reviews for data-only rows.
- Adjacent GE repair: registering six exchangeable outputs exposed the
  fail-closed buy-limit oracle. Regeneration recovered exact November 2012
  prices and a four-hour limit of ten for all six, and the generator now works
  through its documented direct command.
- Taste: Kimi K3 found no blocking issue and recommended item icons. Opus found
  the sole iconless Bones to Peaches row looked like a heading; its existing
  spell icon closes the defect. The final 1200×760 dark render has no truncation.
- Delegation: read-only Sol-high simplification runs
  `d8d86421-3316-4a95-821c-034416da54e3` and
  `f9634099-4ef5-476f-91cd-b8a9a90d2393` exhausted measured tool-output guards
  before producing findings. Root performed the narrow deletion review and did
  not rerun them.
- Verification: 133 focused pure/integration tests and 3 focused real-Qt tests
  pass. Full discovery passes 3,889 tests in both lanes, with 479 plain skips
  and 3 Qt skips. Documentation audits 523 Markdown and 431 HTML files; test
  quality reports zero hard issues across 3,855 tests in 177 files. Compilation,
  JSON, diff, asset normalization, and worktree audits pass. Reachability is
  1,499 actions, 2,240 reachable items, 168 orphan inputs, and 188 unresolved
  actions. No design gap or new placeholder surfaced.

## Iteration 29 — Managing Miscellania resource families

- Evidence: RuneScape Wiki `Managing Miscellania` oldid `6500793`, timestamp
  `2012-10-30T06:29:55Z`.
- Result: the live catalog now contains all six productive cutoff families:
  Mining, Wood, Flax/Herbs, Fishing, Hardwood, and Farming. Fixed quantities,
  item ranges, category totals, selectable variants, and the Maple-nest equation
  are exact. Old saves repair new allocation keys at zero without a migration,
  and atomic collection returns its exact banked output map.
- Placeholders: five `managing_miscellania.*` rows disclose the unrecovered gem,
  nest, herb-seed, herb-composition, and Farming-composition selectors. Every
  representative stays inside the source's literal ranges and totals. Fishing's
  uncounted assorted extras remain omitted rather than receiving a false count.
- UI: real-size offscreen capture exposed vertical clipping that the old panel
  test did not detect. `Kingdom` and `Resources` tabs plus two three-worker
  pages fit the 1000×560 card, preserve stable columns and focus, surface hidden
  assignments, and retain the full payout through tooltips and accessibility.
  Kimi K3 and Opus found no blocking taste defect after their concrete findings
  were reproduced and fixed.
- Verification: 338 focused plain tests and 4 focused real offscreen-Qt UI and
  asset tests pass. Full plain discovery passes 3,876 tests with 479 expected
  skips; full real offscreen-Qt discovery passes 3,876 with 3 intentional skips.
  Documentation audits 521 Markdown and 431 HTML files; test quality reports
  zero hard issues across 3,842 tests in 176 files. Compilation, JSON, diff,
  asset-normalization, and worktree audits pass. Reachability improves to 1,499
  actions, 2,234 reachable items, 168 orphan inputs, and 188 blocked actions.

## Iteration 28 — Penguin Hide and Seek spawn catalog

- Evidence: RuneScape Wiki `Penguin Hide and Seek/Spawn locations` oldid
  `6566231`, timestamp `2012-11-17T15:09:05Z`.
- Result: all 34 one-point and 33 two-point location/disguise pairs replace the
  twelve-row breadth sample in source order. The twelve old IDs stay stable;
  all 67 IDs are unique. A 34-week answered-card proof reaches every ordinary
  row and every invisible-penguin location.
- Boundary: location details remain tooltips in the settled flattened mechanic.
  No travel, map, roaming, trapping, community sighting, or source area gate
  becomes gameplay. No schema migration, placeholder, UI structure, or owner
  design decision was added.
- Verification: 715 focused plain tests and 16 isolated real offscreen-Qt
  Penguin, undo, integration, UI, and asset paths pass. Full plain discovery
  passes 3,871 tests with 479 expected skips; full real offscreen-Qt discovery
  passes 3,871 with 3 intentional skips. Documentation audits 520 Markdown and
  431 HTML files; test quality reports zero hard issues across 3,837 tests in
  176 files. Compilation, JSON, diff, asset-normalization, reachability, and
  worktree audits pass. Reachability remains 1,499 actions, 2,232 reachable
  items, 169 orphan inputs, and 189 blocked actions.
- Test-infrastructure note: one synthetic 715-test Qt module order entered an
  unrelated modal dialog; the 16 isolated relevant paths and canonical
  3,871-test Qt order pass, so the modal aggregate is retained only as a
  papercut rather than a product defect.
- Next: close Managing Miscellania's Harvesting, Fishing, and Farming resource
  families from its literal cutoff reward table.

## Iteration 27 — Shooting Stars crash sites

- Evidence: RuneScape Wiki Shooting Star oldid `6556329`, timestamp
  `2012-11-15T09:20:35Z`; Darkan HEAD
  `4d72f80f3e7ad56a712b4e38653f01cedaeeb289`; installed Darkan core `2.0.6`.
- Result: all 43 cutoff crash-site names replace the six-site breadth sample in
  source order. Six legacy active-event labels repair to their canonical names
  so catalog depth cannot discard a live star. Locations remain flavour only;
  no map, telescope, travel, or site gate was added.
- Negative evidence: Darkan's 33-site reconstruction conflicts with the cutoff
  table. Its `Utils.random(0, 9)` starting-tier call is upper-exclusive and
  yields `0..8`, including an invalid zero and excluding tier nine, so the
  hidden period tier distribution remains source-blocked.
- Verification: focused plain verification passes 892 tests. Relevant real
  offscreen-Qt verification passes a 436-test integration prefix and three
  direct Shooting Stars UI paths. Full plain discovery passes 3,870 tests with
  479 expected skips; full real offscreen-Qt discovery passes 3,870 with 3
  intentional skips. Documentation audits 520 Markdown and 431 HTML files;
  test quality reports zero hard issues across 3,836 tests in 176 files.
  Compilation, JSON, diff, asset-normalization, reachability, and worktree
  audits pass. Reachability remains 1,499 actions, 2,232 reachable items, 169
  orphan inputs, and 189 blocked actions.
- Next: transcribe Penguin Hide and Seek's exact 34 one-point and 33 two-point
  cutoff spawn pools without changing its settled flattened travel model.

## Iteration 26 — Fishing Trawler Tiger shark

- Evidence: RuneScape Wiki Tiger shark oldid `6448339`, timestamp
  `2012-10-21T04:48:57Z`; Raw tiger shark oldid `5992445`, timestamp
  `2012-07-26T02:12:01Z`; and rev-741 item definitions for IDs
  `21520`/`21521`/`21522`.
- Result: the exact level-95 catch row, one-per-trip cap, Cooking chain,
  item semantics, 250-LP heal, 100-LP overheal cap, and three normalized assets
  are live. The rare admission is separate from the common selector and uses
  the source's approximate one-in-five statement without claiming the hidden
  roll. Raw and cooked sprites are pre-cutoff; the burnt sprite has no period
  wiki file history and is marked visual-only.
- Placeholder: `cooking.tiger_shark_burn_endpoints` borrows the adjacent
  Rocktail curve because the cutoff page proves there is no no-burn level but
  gives no probability. The exact admission selector also remains disclosed
  data depth. No owner design gap surfaced.
- Verification: focused plain and real offscreen-Qt lanes each ran 603 tests
  successfully. Full plain discovery ran 3,869 tests: 3,390 ordinary passes
  and 479 expected environment skips. Full real offscreen-Qt discovery ran the
  same 3,869 tests: 3,866 ordinary passes and 3 intentional skips.
  Documentation audits 520 Markdown and 431 HTML files; test quality reports
  zero hard issues across 3,835 tests in 176 files. Compilation, JSON, diff,
  asset-normalization, reachability, and worktree audits pass. Reachability
  records 1,499 actions, 2,232 reachable items, 169 orphan inputs, and 189
  blocked actions. This merge is GPT-family verified.

## Iteration 25 — Raider-set level requirements

- Evidence: Tip.It Goblin Raids guide last updated `2012-10-24`, immutable
  Wayback capture `20121228205432`, retrieved HTML SHA-256
  `93154a0c8cce74e4da6c65e80bed2bf7db14e29a0a0eb56d3a80004a101d89d2`.
- Result: Raider axe requires 8 Attack; Raider chainbody and Raider shield each
  require 8 Defence. The armour's prior level-1 equip path is removed and all
  three rows now use the shared skill-requirement contract.
- Verification: 135 focused Goblin Raids, equipment, item-registry and
  placeholder tests pass. Full discovery passes 3,865 tests in both lanes, with
  479 expected plain skips and 3 real offscreen-Qt skips. Documentation audits
  520 Markdown and 431 HTML files; test quality reports zero hard issues across
  3,831 tests in 176 files; diff and worktree audits pass.

## Iteration 24 — Commander Yodri rewards and timed-out attempts

- Evidence: Tip.It Goblin Raids guide last updated `2012-10-24`, immutable
  Wayback capture `20121228205432`, retrieved HTML SHA-256
  `93154a0c8cce74e4da6c65e80bed2bf7db14e29a0a0eb56d3a80004a101d89d2`;
  release oldid `6434891`; cutoff oldid `6545250`; Darkan's current tree.
- Result: Yodri's exact potential sets are Potato/Marigold/Barley seeds,
  Logs/Oak logs, and Clay/Copper/Tin for farm, forest and mine raids. The payout
  is capped at one item for each of the ten ordinary Raiders; Hollowtoof no
  longer creates an eleventh item. A timed-out raid keeps the proportional
  payout for Raiders already killed, but does not count as cleared; a zero-kill
  timeout releases the activity and combat state instead of leaving stale live
  selection.
- Placeholder: the old table placeholder is retired. Only the unrecovered
  within-table selection distribution remains as deterministic round-robin in
  `goblin_raids.yodri_reward_selection`.
- Delegation: bounded read-only simplification run
  `3f86e88b-ae44-4329-a7d1-4cff91fd64ff` exhausted its 30,000 processed-token
  guard at 61,036 after three tool calls and returned no candidate. Root reused
  the preserved diff evidence, performed the deletion pass, and did not rerun.
- Verification: 116 focused tests pass. Full discovery passes 3,864 tests in
  both lanes, with 479 expected plain skips and 3 real offscreen-Qt skips.
  Documentation audits 520 Markdown and 431 HTML files; test quality reports
  zero hard issues across 3,830 tests in 176 files; diff and worktree audits
  pass. Reachability reports its unchanged known ledger: 1,498 actions, 2,230
  reachable items, 169 orphan inputs and 189 blocked actions.

## Iteration 23 — Goblin Raids ordinary-raider count

- Evidence: release oldid `6434891`; cutoff oldid `6545250`; Tip.It Goblin
  Raids guide last updated `2012-10-24`, Wayback capture `20121228205432`;
  release-day `File:Goblin raid.png`; Darkan's current tree; and modern wiki
  revision `35941310` as corroboration only.
- Result: Yodri's exact one-item-per-kill rule plus the period Tip.It maximum of
  ten site rewards pins ten ordinary Raiders. The release-day screenshot
  independently shows nine ordinary models with Hollowtoof separate, so the old
  value of five was contradicted even before the arithmetic closed ten. The
  live count is ten and `goblin_raids.raider_count` is retired from the
  placeholder register.
- Verification: 114 focused Goblin Raids, placeholder-register,
  direct-action-undo and
  notification-strip tests pass. A world-clock regression proves the ten
  Raiders and Hollowtoof fit the registered 15-review active window. Full
  discovery passes 3,862 tests in both lanes, with 479 expected plain skips and
  3 real offscreen-Qt skips. Documentation audits 520 Markdown and 431 HTML
  files; test quality reports zero hard issues across 3,828 tests in 176 files;
  diff and worktree audits pass.
- Next: Commander Yodri's site reward contents and selection rule.

## Iteration 22 — Goblin Raids active duration and cleared-raid lifecycle

- Evidence: release oldid `6434891`; Goblin Raids oldids `6545250` and
  `6452732`; the complete pre-cutoff article/talk histories; rev-741/742
  interface `583:87`; Darkan's current tree; and rejected post-cutoff revision
  `20647497`.
- Result: the exact active duration remains `source_blocked`. Revision
  `6452732` explicitly distinguishes the half-hourly notice from the activity's
  start, while no period/server source states a despawn. The registered
  15-review completion window therefore remains. A concrete adjacent defect is
  fixed: killing Hollowtoof now ends the active raid instead of leaving the same
  cleared encounter repeatedly joinable. Yodri's pending spoils survive that
  transition and claiming them cannot erase a later announced raid.
- Verification: 113 focused Goblin Raids, notification-strip,
  placeholder-register and direct-action-undo tests pass. Plain discovery
  passes all 3,861 tests with 479 intentional skips (3,382 ordinary passes);
  real offscreen-Qt discovery passes all 3,861 tests with 3 intentional skips
  (3,858 ordinary passes). Documentation audits 520 Markdown and 431 HTML
  files; test-quality audits 3,827 tests across 176 files with zero hard issues;
  diff-whitespace and worktree-layout audits pass.
- Next: Goblin Raids ordinary-raider count.

## Iteration 21 — Crucible Supreme Champion event clock

- Evidence: Crucible oldid `6538845`; launch-update oldid `5778674`; the
  settled 240-card world/economy day; rev-727 Crucible client surfaces; and
  Darkan's complete Crucible history.
- Result: the sourced half-hour interval already mapped exactly to five answered
  cards, but live code compared it with a private productive-review counter.
  Training elsewhere paused the schedule and re-entry restarted it. The event
  now derives from `shop_market_clock.answered_cards`; the session keeps only
  the event card and champion selected at that boundary, while sanitation drops
  the obsolete countdown fields. Champion selection does not change when a hit
  promotes the player during the event. The settled one-review duration remains
  unchanged and no design gap surfaced.
- Verification: 41 focused Crucible/register tests pass. Plain discovery passes
  all 3,860 tests with 479 intentional skips (3,381 ordinary passes); real
  offscreen-Qt discovery passes all 3,860 tests with 3 intentional skips (3,857
  ordinary passes). Documentation audits 520 Markdown and 431 HTML files;
  test-quality audits 3,826 tests across 176 files with zero hard issues;
  diff-whitespace and worktree-layout audits pass.
- Next: Goblin Raids active duration.

## Iteration 20 — Crucible target-level matching

- Evidence: Crucible oldid `6538845`; its complete pre-cutoff article and talk
  histories; rev-727 interfaces and scripts; and Darkan's complete Crucible
  history from `53122a021` onward.
- Result: the exact server matching band and its frequencies remain
  source-blocked. The old registered `-8/0/+8/+20` cycle could not reproduce
  the period criticism it cited: a minimum-eligible combat-60 entrant could
  reach only level 80, never a maxed level-138 opponent. The fourth offset is
  now `+78`, clamped to the real 3–138 combat range. The first three targets
  remain near-level, while the documented severe mismatch is reachable. Its
  one-in-four cycle position is explicitly a reachability abstraction, not a
  period frequency. No design gap surfaced.
- Verification: 39 focused Crucible/register tests pass. Full discovery runs
  3,858 tests in both lanes: plain has 3,379 ordinary passes and 479 expected
  skips; offscreen Qt has 3,855 ordinary passes and 3 expected skips. Test
  quality audits 3,824 methods across 176 files with 0 hard issues. A bounded
  GPT-family no-tools checker (`8b16c106-cd75-4e23-a51b-37e0d1792af3`)
  independently agreed that no numeric period band survives; root reproduced
  the reachable-boundary defect. Documentation, diff-hygiene, and worktree
  audits pass. This merge is GPT-family verified.
- Next: Crucible event interval.

## Iteration 19 — Crucible bounty-fee scale

- Evidence: Crucible oldid `6538845`; complete cutoff talk history through
  oldid `5909709`; launch-day report oldid `5778707`; the immutable
  `Crucible_bounty_fee_interface.png` revision uploaded
  `2012-06-24T20:37:44Z`; rev-727 interface 1298; Darkan history commit
  `684c25528`.
- Result: the old curve was an order of magnitude below every surviving period
  observation. The registered reachability curve now anchors level 60 at
  500,000 coins and level 138 at 531,200 coins: a 450,000 risk baseline,
  400 per combat level above 60, and a 50,000 abandonment component. This is
  explicitly not claimed as the unrecovered server formula. No design gap
  surfaced.
- Verification: 38 focused tests pass. Full discovery passes 3,804 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation
  audits 515 Markdown and 428 HTML files; test quality audits 3,770 tests with
  0 hard issues. Diff-hygiene and worktree audits pass.
- Next: Crucible target-level offsets.

## Iteration 18 — Crucible Trophy-bone awards

- Evidence: launch-update oldid `5778674`; the complete Crucible history through
  cutoff oldid `6538845`; Trophy bones oldid `5971782` and its complete
  29-revision pre-cutoff history; rev-727/741/742 item 24444; rev-727 scripts
  and interface 1297:125; Darkan history commit `684c25528`.
- Result: ordinary kills demonstrably award Trophy bones, but no source exposes
  the amount, so the two-bone reachability value remains registered. The four
  tutorial awards are exactly one each, so that stale placeholder is retired.
  Darkan's non-stackable metadata container is recorded as a later loot-key
  reconstruction, not period amount evidence. No design gap surfaced.
- Verification: 37 focused tests pass. Full discovery passes 3,803 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff-hygiene, and worktree audits pass.
- Next: Crucible risk-expectation amount per combat level.

## Iteration 17 — Crucible ordinary-kill rank points

- Evidence: launch-update oldid `5778674`, the complete pre-cutoff Crucible
  article history through oldid `6538845`, the cutoff talk history, Darkan
  `CrucibleController.java` and history commit `684c25528`, and rev-727 script
  6288.
- Result: ordinary target kills demonstrably award rank points, but no source
  exposes the amount. The one-point value remains a registered reachability
  placeholder and is not inferred from the separate champion-hit rule. No
  gameplay changed and no design gap surfaced.
- Verification: 37 focused tests pass. Full discovery passes 3,803 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff-hygiene, and worktree audits pass.
- Next: Crucible Trophy bones per ordinary kill.

## Iteration 16 — Crucible rank-point thresholds

- Evidence: Darkan `CrucibleController.java:28-33`,
  `Crucible.java:86-122`, history commit `684c25528`, rev-727 scripts 6284/6288,
  Crucible oldid `6538845`, and launch-update oldid `5778674`.
- Result: no source exposes the six promotion boundaries. The registered
  1/3/6/10/15/25 ladder remains, with the complete negative caller chain now
  recorded. No gameplay changed and no design gap surfaced.
- Verification: 37 focused tests pass. Full discovery passes 3,803 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff-hygiene, and worktree audits pass.
- Next: ordinary Crucible rank points per kill.

## Iteration 15 — Daily Challenge assignment weighting

- Evidence: Challenge System oldid `6579729` states one-in-four for the desired
  skill when four skills remain. Cutoff talk oldids `6555739` and `6539307`,
  Darkan, and rev-741/742 expose no within-skill selector.
- Result: replace the biased flat row draw with equal skill intervals followed
  by a within-skill draw, while consuming one RNG value. Rename the placeholder
  so only the genuinely unknown within-skill task weights remain registered.
- Regression: every eligible skill owns one equal interval even though Mining
  and Cooking have more breadth rows. No design gap surfaced.
- Verification: 47 focused unit/integration tests pass. Full discovery passes
  3,803 tests in both lanes, with 460 expected plain skips and 3 Qt skips.
  Documentation, test-quality, diff-hygiene, and worktree audits pass.
- Next: Crucible rank-point thresholds.

## Iteration 14 — Tears of Guthix green-tear probability

- Evidence: Darkan `TearsOfGuthix.kt:477-510` and its frozen target contract;
  activity oldid `6579712`; cutoff talk oldid `6539293`; rev-727/742 cache
  evidence already recorded in the source audit.
- Result: no source exposes stream rotation or catch probability. The registered
  `0.055` value remains, now explicitly described as a weak reachability anchor
  rather than an authentic rate. No gameplay changed and no design gap surfaced.
- Verification: 26 focused tests pass. Full discovery passes 3,802 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff-hygiene, and worktree audits pass.
- Next: Daily Challenges eligible-pool assignment weights.

## Iteration 13 — Bork Ork-legion style classification

- Evidence: Darkan `Bork.kt:110-111,184-205` selects melee within one tile and
  ranged otherwise.
- Result: the settled stand-near pressure route continues to use the exact
  adjacent melee branch. `bork.ork_legion_attack_style` is retired because this
  is a disclosed distance-collapse abstraction, not an unknown period value.
- Verification: 28 focused tests pass. Full discovery passes 3,802 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. GPT-family verified.

## Iteration 12 — Duellist's cap threshold closure

- Evidence: oldid `6579418`, dated `2012-11-18T23:11:12Z`, is the pre-cutoff
  parent of the previously cited post-cutoff cap page and already states all six
  ranges.
- Result: live minimums remain `0/10/100/500/2,000/5,000`, now period-pinned;
  `duel_arena_cap_thresholds` is retired from the placeholder register.
- Verification: 16 focused tests pass. Full discovery passes 3,802 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. GPT-family verified.

## Iteration 11 — Skeletal Horror phase identities

- Evidence: rev 727, rev 742, Darkan's generated NPC list, and its four
  `nostats` combat definitions agree on the form mapping 320=`9176/9177`,
  260=`9178`, 180=`9179`, and 100=`9180`.
- Result: the live weakening sequence is corrected from the shifted
  `9176 → 9177 → 9178 → 9179` to `9176 → 9178 → 9179 → 9180`.
- Honest limit: all four core-stat blocks remain registered placeholders. The
  client exposes combat level, and the authentic server definitions explicitly
  omit stats; no value was derived from combat level.
- Delegation: GPT-family Workflows run
  `5a1447db-96b4-47f7-9b47-b52860ce2f07` exhausted its tool-output budget after
  two calls and produced no synthesis. Root independently reproduced every
  accepted finding and did not rerun it.
- Verification: 20 focused tests pass. Full discovery passes 3,802 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. GPT-family verified.

## Iteration 10 — Daily Challenges reward-XP re-walk

- Rev 741 and 742 contain identical client structs for representative combat,
  Cooking, and Fishing challenges. The rows carry the full client-facing task
  definition but no XP payout field.
- Rev 742 interface 1343 is the Daily Challenges panel. Its decoded labels and
  hooks reveal no static reward amount; the two reward item definitions prove
  only the lamp and bag identities and actions.
- Later byte-level verification found that the fifteen skipped rev-742 archives
  begin with `0x03`; the first-byte gate's `if1` exception label was a false
  format classification. The checked-in reader still skips them, so continuing
  after the warnings does not make the negative search complete.
- A one-off reflective experiment bypassed the guard, decoded all 1,376 affected
  components, and found none related to Daily Challenges interface 1343.
- Result: `daily_challenges.reward_xp` remains registered at 100 XP per required
  level because the relevant structs and decoded interface 1343 contain no
  amount. A period server payout routine or independently stated amount is still
  required. No gameplay value changed.
- Verification: 51 focused Daily Challenges, real-cache reader, and placeholder
  tests pass. Full discovery passes 3,802 tests in both lanes, with 460 expected
  plain skips and 3 Qt skips. Documentation, test-quality, diff, and worktree
  audits pass.

## Iteration 9 — Frozen boss combat-level closure

- Tooling: the exact NPC definition reader now emits combat levels for requested
  IDs.
- Evidence: rev 727 and rev 742 agree on all 144 definitions in the six Frozen
  boss series. Astea's 57 rows encode three NPC forms for each of 19 levels; the
  other series encode one row per level.
- Result: every live ladder was already numerically correct. The registered
  ladder placeholder is retired; server tier selection and combat definitions
  remain honest placeholders.
- Coordination: the canonical Darkan/AnkiScape source ledger records the pinned
  cache result so the Darkan restoration loop need not repeat it.
- Verification: 13 focused cache/data/register tests plus documentation,
  test-quality, shell-syntax, diff, and worktree audits pass. Full discovery
  passes 3,801 tests in both lanes, with 460 expected plain skips and 3 Qt
  skips. GPT-family verified.

## Iteration 8 — Achievement Diary depth closure

- Generator: the Diary catalog generator now requires an explicit
  `--items-yml` source path. The hard-coded developer checkout is gone, and a
  real rev-667 regeneration remains byte-identical.
- Migration: the v108 regression already covered removal and re-earning. It now
  proves an unrelated unmet completion survives, closing the selective
  revalidation boundary without adding a duplicate test.
- Delegation: GPT-family Workflows run
  `c48d7907-2f2e-4e3c-a365-7ba95b3aec2a` stopped both read-only leaves when they
  exceeded their tool-output budgets. Root independently reproduced the two
  findings and did not rerun the leaves.
- Verification: the focused Diary/storage lane passes 168 tests; explicit-path
  regeneration is byte-identical. Full discovery passes 3,800 tests in both
  lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff, and worktree audits also pass. GPT-family verified.

## Iteration 1 — pass 6 B.15 skill-selector hybridization

- Result: complete and cross-lineage verified.
- Scope: per-skill target selectors only. Combat retains its tree-specific live
  filter and empty-state machinery; D.1 behavior remains outside this slice.
- Behavior: `<25` rows render flat; `>=25` grouped rows render as a tree; an
  ungrouped row set remains flat. Both forms use alternating rows, exact
  30-pixel item height, green current-target highlighting, and bold current
  text.
- Regression coverage: real Qt builders at the 24/25 boundary, the 25-row
  ungrouped fallback, renderer type, striping flag, row geometry, highlight,
  font weight, and the affected short Agility and Thieving surfaces.
- Verification: full plain discovery passed 3,785 tests with 459 declared
  skips in 238.080 seconds. Full offscreen-Qt discovery passed the same 3,785
  tests with 3 declared skips in 520.229 seconds from the real `.venv-qt`
  interpreter. The test count increased by two from the 3,783-test baseline.
- Independent review: Kimi K3 found no material defect. The implementation
  incorporated its concrete notes to correct four stale return annotations and
  pin the 30-pixel geometry instead of asserting only relative equality.
- Workflow note: read-only Codex Workflows run
  `3a1ea34f-0acd-467a-9cc0-bde476372763` exhausted its tool-byte budget while
  loading project memory and produced no actionable result; root independently
  reproduced the complete scope.

## Iteration 2 — Dungeoneering guardian-room coin funding

- Result: already implemented on `main`; stale queue and Memory Bank status
  reconciled without duplicating product code.
- Existing implementation: commits `6ced27e8`, `dcf41c0d`, `c5eb86c8`,
  `6e07d1bc`, and `05016790` remove the resource-room cache and split the
  registered 1,010-coin placeholder across eligible critical-path guardian
  rooms. C1-C4, incomplete Druidic Ritual, Herblore below 5, and optional
  guardians receive no funding.
- Persistence: the eligible guardian-room ids survive reload; the migration
  distinguishes a legacy resource-cache save from pre-drop and post-drop saves
  so it neither loses funding nor grants it twice.
- Verification: the same product revision passed both full 3,785-test lanes in
  iteration 1. A fresh focused plain lane and fresh focused offscreen-Qt lane
  each passed all 54 Dungeoneering data, logic, and placeholder-register tests.
- Source status: the authentic guardian-room mechanism is settled; only the
  period coin magnitude remains the registered
  `PLACEHOLDER(dungeoneering.starter_guardian_coin_drops)` pending a decoded
  Frozen guardian drop table.

## Iteration 3 — 384-task Achievement Diary roster

- Result: complete. All eight regional families now expose four tiers of
  exactly twelve tasks, for 384 regional rows. The complete catalog has 474
  rows across ten families.
- Curation: every prior task identity remains stable. A short source tier first
  draws from unused authentic rows in its own family, preserving each row's
  original tier in both its durable ID and source note. The remaining 22 slots
  use visibly labelled progression anchors whose exact skill levels already
  occur in that family's period requirements; no tier uses more than three.
- Reachability: 317 regional rows have live predicates. The other 67 authentic
  rows remain visibly unavailable instead of becoming fabricated deeds. Three
  Miscellaneous activity deeds that already have live counters now resolve
  through those counters rather than remaining latent.
- Integrity: generation rejects an unknown quest, unknown skill, anchor level
  absent from the family source, duplicate authentic requirement, misplaced
  preferred source ID, tier above three anchors, or tier other than twelve
  rows. All 422 pre-change task IDs remain present and 52 rows were added.
- Verification: 128 focused pure/integration tests and 27 focused real
  offscreen-Qt tests pass. Deterministic regeneration is byte-identical. Full
  discovery passes 3,790 tests in both lanes: plain declares 460 expected
  skips; the real Qt interpreter declares 3.
- Depth debt: the v108 diary revalidation migration still needs a targeted
  regression test, and the generator's local `ITEMS_YML` source path remains
  non-portable. Neither changes the live 384-row mechanic.

## Iteration 4 — period-cache enum, struct, and param reader

- Result: implemented the first high-leverage depth tool. One read-only wrapper
  accepts an extracted cache or disk zip and exposes `count`, `dump`, and
  case-insensitive `find` for enum, struct, and param definitions.
- Evidence boundary: enum and struct decoding reuse Darkan core 2.0.5; param
  decoding follows the rev-727 client's opcodes 1, 2, 4, and 5 and rejects an
  unknown opcode. Output is deterministic and key-sorted. This is client data,
  never evidence for server-side rolls, rates, timers, or rewards by itself.
- Period coverage: count probes pass on all seven local caches. From build 652
  through 742, enum definitions grow 3,853→6,680, structs 1,793→14,527, and
  params 1,414→2,792. Exact rev-727 fixtures pin enum 3483 (1,096 entries),
  struct 0, and param 0.
- Delegation: GPT-family Workflows run
  `3c1610ec-a7ec-4dfc-93dd-a72bb33abd6e` exhausted both leaves' processed-token
  guards before a final response. Root reused the bounded tool evidence and did
  not rerun the leaves.
- Verification: the three real-cache integration tests pass. Full discovery
  passes 3,793 tests in both lanes: plain declares 460 expected skips; the real
  Qt interpreter declares 3. Shell syntax, Python compilation, documentation,
  and test-quality audits also pass.

## Iteration 5 — period-cache interface-definition reader

- Result: implemented the second high-leverage depth tool. One read-only
  wrapper accepts an extracted cache or disk zip and exposes deterministic
  `count`, `dump`, and client-label `find` modes for index-3 interfaces.
- Decoder: the tool reuses Darkan core 2.0.5 rather than copying the giant
  decompiled client component class. It reports stable `interface:component`
  identities, layout and hidden state, text/assets, actions, and principal
  client script hooks.
- Period coverage: count probes and interface 0 component 0 decode on every
  local cache from build 652 through 742. Rev 727 contains 1,321 interfaces and
  65,239 components; exact fixtures pin the Grand Exchange heading and travel
  action.
- Evidence boundary: interface definitions establish shipped presentation and
  client hooks only. They do not establish server validation, XP, rolls,
  timers, drops, or rewards.
- Delegation: GPT-family Workflows run
  `a5aff6a3-4f4a-4821-ba59-69edabad8e3a` exhausted its tool-output budget after
  dumping the decompiled client. Root recovered its bounded decoder evidence,
  found the existing core loader, and did not rerun the leaf.
- Verification: three real-cache integration tests pass. Full discovery passes
  3,796 tests in both lanes: plain declares 460 expected skips; the real Qt
  interpreter declares 3. Shell syntax, Python compilation, documentation,
  test-quality, diff, and worktree audits pass.

## Iteration 6 — client-side blocked-row re-walk

- Result: the Conquest Foot Soldier cost placeholder is retired. Interface
  1015 renders squad costs from NPC param 1138, CS2 script 486 maps the Foot
  Soldier to NPCs 12202/12205, and both rev-727 rows contain 50. The live value
  was already conservative, so this is an evidence correction rather than a
  gameplay change.
- Tooling: the NPC/object definition reader now supports deterministic
  `--params` output for exact IDs. A real-cache integration test pins both Foot
  Soldier variants and the period cost.
- Honest limits: no diary-lamp minimum-level table, Conquest battlefield grid,
  or starting/passive command-point rule appeared in the decoded interface,
  CS2, or definition data. Those server-owned values remain registered
  placeholders rather than inferred conventions.
- Delegation: GPT-family Workflows run
  `f6e5b815-9ee4-43ca-8d9c-f20032ac1d79` exhausted both leaves' processed-token
  guards. Root salvaged their bounded client leads, independently reproduced
  every accepted claim, and did not rerun the leaves.
- Verification: 34 focused tests pass. Full discovery passes 3,797 tests in
  both lanes: plain declares 460 expected skips; the real Qt interpreter
  declares 3. Documentation, test-quality, shell-syntax, diff, and worktree
  audits pass.

## Iteration 7 — exact item-definition depth

- Tooling: `query_openrs2_cache.sh --id` now emits deterministic exact model,
  recolour, texture, sprite-recolour, bonus, stackability, exchangeability, and
  option fields for requested item IDs.
- Temple Trekking: rev-727 model `14131` leaves item `7774` in its original
  yellow/ochre colours, recolours `7775` into the red hue band, and recolours
  `7776` into the blue band. The live blue/yellow mapping was reversed and is
  corrected to blue `7776`, yellow `7774`, red `7775`.
- Goblin Raids: rev-741 pins Goblin cower shield and Raider axe/chainbody/shield
  as `25350-25353`. All four are non-exchangeable and carry nonzero combat
  bonuses. The unrelated `202xx` identities, tradeable Raider rows, and zeroed
  bonuses are corrected.
- Placeholder result: `temple_trekking.token_color_item_ids` and
  `goblin_raids.raider_set_bonuses` are retired. Dominion Tower reward IDs stay
  source-blocked because exact-name cache searches found no identities to query.
- Delegation: GPT-family Workflows run
  `20dc70c5-2a6c-490f-8d35-25550d5659af` exhausted both bounded leaves before a
  final response. Root reused only their narrow file leads, independently
  reproduced every cache claim, and did not rerun them.
- Verification: 152 focused cache/data/registry/equipment tests and two real
  offscreen equipment-stat UI tests pass. Full discovery passes 3,799 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, shell-syntax, diff, and worktree audits also pass.
## Iteration 42 — skilling brawling-gloves source closure

- Period closure: rev-727/742 pin all six exact item identities. Cutoff pages
  pin 1.5 times XP outside, 4 times Wilderness XP for Woodcutting, Mining,
  Smithing, and Cooking, and 5 times for Fishing and Firemaking.
- Charge closure: period pages give 732 Woodcutting logs, 1,200 Firemaking
  logs, about 434 Smithing actions, about 400 Fishing catches, and 1,109
  successful cooks.
- Honest block: Mining has only a 30-minute period row and an estimate of 350
  to 800 ores. AnkiScape must use a registered review-action abstraction, not
  wall-clock time.
- Dependency: Revenants and the Chaos Elemental are the period acquisition
  routes, but neither encounter exists in AnkiScape. Exact drop rates remain
  source-blocked. No inert items or speculative combat rows were added.
- Reconstruction conflicts: game-main and Darkan disagree with each other and
  with the cutoff pages. Neither charge table is promoted as period truth.
- Delegation: GPT-family Workflows run
  `d66c60fd-e7de-4966-a12c-56e969689fad` exceeded both evidence budgets after
  three calls. Root reproduced every accepted claim from exact oldids, cache
  queries, and named implementation lines.
- Verification: both full lanes pass 3,939 tests. Plain has 483 expected skips;
  real offscreen Qt has three intentional skips. Documentation, JSON, diff,
  test-quality, and worktree audits also pass.

## Iteration 43 — Cooking gauntlets

- Result: the Family Crest gauntlet lifecycle and Cooking modifier are complete
  end to end. The slice includes all four physical equipment variants,
  conversion/re-enchantment, remembered free recovery, target-local equipment
  policy, persistence, undo, UI, assets, and cadence routing.
- Source: final pre-EOC `Cooking/Burn level` oldid `6572206` pins Trout 50,
  Tuna 63, Lobster 68, Swordfish 81, Monkfish 87, and
  Shark/Cavefish/Rocktail 94. Older oldid `6556123`, rev-667 interpolation,
  audited item definitions 775-778, and Darkan commit `4f704bd15` close the
  lifecycle and reconciliation boundary.
- Defect found before commit: capping every pre-threshold roll at 254/255 made
  Trout at level 49 worse with gauntlets than without them. The accepted policy
  preserves an already-better ordinary chance and applies exact guarantees at
  the dated thresholds.
- UI: Kimi K3 and Fable independently requested hiding the recovery action
  outside a genuine loss. The accepted pass also uses compact outcome-specific
  policy labels and one shared Bank/Equipment conversion-action builder.
- Delegation: read-only Sol-high Workflows runs
  `ad0d83b4-8629-4e80-b545-9cd152abfe75` and
  `3ae0a7da-98f3-467d-81bd-df66ab711e22` exhausted their declared evidence
  budgets without a completed finding. Root used the bounded partial evidence,
  independently reviewed the full diff, and removed the duplicated UI builder.
- Verification: focused pure/runtime/integration/cadence checks pass 562 tests;
  focused Cooking-gauntlet plain and real-Qt lanes pass 16 each. Full plain
  discovery passes 3,957 tests with 485 expected skips in 348.312 seconds; real
  offscreen Qt passes 3,957 with 3 skips in 641.305 seconds. Documentation,
  test-quality, JSON, compilation, diff, reachability-ledger, and worktree
  audits pass. Native Anki visual proof is blocked by the locked Mac.

## Iteration 46 — Karambwan Cooking

- Result: Poison karambwan, thorough Cooked karambwan, and Karambwanji are live
  as separate grouped Cooking targets. Shared runtime behavior covers materials,
  XP, failures, telemetry, persistence, and review undo.
- Source: Poison karambwan oldid `6250179`, Cooked karambwan oldid `6154936`,
  Karambwanji oldid `5838218`, Cooking oldid `6548144`, Tai Bwo Wannai Trio
  oldid `6529797`, and rev-667 item definitions pin the period rows and item
  semantics.
- Honest limits: the two hidden burn rolls remain registered placeholders.
  Darkan's internally inconsistent karambwan input/level rows were rejected;
  only its bounded Karambwanji reconstruction supports that placeholder.
- Delegation: read-only Sol-high Workflows run
  `e739d5bf-c053-4142-b732-e2db72351268` exceeded both leaves' declared evidence
  budgets without returning a usable candidate. Root independently reproduced
  all evidence and implementation behavior and did not rerun the leaves.
- Verification: 464 focused plain tests and two focused real offscreen Qt tests
  pass. Full plain and offscreen Qt discovery each pass 3,982 tests, with 486
  expected plain skips and three Qt skips. Documentation, test quality,
  compilation, JSON, diff, asset normalization, and worktree audits pass. The
  known reachability ledger improves to 1,542 actions, 2,344 reachable items,
  166 orphan inputs, and 186 unresolved actions.

## Iteration 47 — brewing input acquisition

- Result: the existing brewing family is reachable end to end. One review
  malts one Barley into one Barley malt with no failure and no XP; Blandebir's
  batchable Shop service turns each Empty pot plus 25 Coins into Ale yeast
  after the established The Giant Dwarf Keldagrim route wall.
- Source: Barley malt oldid `6207311`, Barley oldid `5434668`, and Ale yeast
  oldid `4227753` pin the complete mechanic. Darkan corroborates Empty pot
  `1931`, Ale yeast `5767`, and the 25-Coin transaction. No placeholder was
  needed.
- Adjacent defect: the shared Cooking handler displayed `+0 XP` after a valid
  zero-XP action. It now emits XP feedback only for a nonzero award, while the
  malting regression proves inventory, telemetry, persistence, and review undo.
- UI/assets: established Cooking and Shop rows reuse three normalized cutoff
  sprites. No new surface or interaction pattern was introduced, so no new
  taste pass was required.
- Verification: focused checks pass 645 plain and two real offscreen Qt tests.
  Full plain and offscreen Qt discovery each pass 3,986 tests, with 486 plain
  skips and three Qt skips. Documentation, test quality, compilation, JSON,
  deterministic shop generation, diff, asset normalization, and worktree
  audits pass. Reachability improves to 1,544 actions, 2,347 reachable items,
  164 orphan inputs, and 184 unresolved actions. Native Anki is not claimed.

## Iteration 48 — special Woodcutting acquisition

- Result: Arctic pine and Eucalyptus are live gathering targets through the
  shared Woodcutting runtime. Arctic pine uses its sourced level 54, 140.2 XP,
  log output, and The Fremennik Isles-started gate. Eucalyptus uses its sourced
  level 58, 165 XP, log output, and settled ungated safe route.
- Honest limits: oldids `6069429` and `6491980` do not expose hidden success,
  depletion, or respawn rolls. The nearest-level Mahogany and Yew rows are
  marked and registered placeholders rather than period claims.
- Adjacent defect: selector metadata enforced Woodcutting quest locks, but the
  review-time handler did not. Saved or direct target states could bypass the
  route wall. The shared handler now applies the same pure lock reasons before
  gathering while preserving the dedicated no-hatchet error path.
- UI/assets: the established selector displays both rows with existing
  normalized cutoff log sprites. No new interaction pattern was added, so no
  taste pass was required. Cursed magic stays dependency-blocked because
  Spirit of Summer has no live quest substrate.
- Verification: focused checks pass 416 core tests, two loaded-add-on undo
  checks, and one real offscreen Qt check. Full plain discovery passes 3,992
  tests with 487 expected skips; real offscreen Qt passes 3,992 with 3 skips.
  Documentation, test quality, compilation, JSON, diff, asset normalization,
  reachability, and worktree audits pass. Reachability improves to 1,546
  actions, 2,350 reachable items, 162 orphan inputs, and 181 unresolved
  actions. Native Anki is not claimed. GPT-family root verified.

## Iteration 49 — Dagannoth Kings and Dragon hatchet

- Result: Prime, Supreme, and Rex are live in one persistent dangerous boss
  room under Activities. The generic boss-room substrate owns entry/resume,
  one engaged target, pressure from every other living king, Casual/Advanced
  targeting, six-tick Combat slices, kills, review-driven respawns, explicit
  Leave, dangerous death, persistence, migration repair, and undo.
- Source: cutoff oldids `6505723`, `6457675`, and `6535937` pin the three
  level-303 combat rows, styles, lifepoints, maximum hits, Slayer XP, guaranteed
  bones/hide, and rare Dragon hatchet. Darkan combat/drop definitions provide
  the marked 59-tick respawn and independent 1/128 hatchet reconstructions.
- Honest limits: Prime/Rex attack speed, exact respawn delay, and numeric
  Dragon-hatchet rate are registered placeholders. The live drop catalog is
  deliberately the two guaranteed items plus the acquisition seam, not a claim
  of exhaustive king loot.
- UI/assets: Kimi K3 and Opus supplied independent read-only taste passes. The
  accepted card uses normalized period sprites, a visible alive/dead/engaged
  roster, a standalone dangerous-death warning, compact policy controls, and a
  geometry regression that prevents its action row from overlapping activity
  pagination at 900×560. Fable stayed reserved. Native Anki is not claimed.
- Review discipline: implementation/evidence Workflows run
  `180cd378-15a0-49e1-9ce6-411760219e14` and diff-only run
  `572b864b-6bb8-4a21-b39c-f4650a0b0edb` exhausted their bounded budgets without
  final findings. Root reproduced all accepted evidence and did not rerun them.
- Verification: 663 broad focused checks and one focused real offscreen Qt test
  pass. Full plain and offscreen Qt discovery each pass 4,004 tests, with 488
  expected plain skips and three Qt skips. Documentation, test quality,
  compilation, JSON, diff, asset normalization, reachability, placeholder, and
  worktree audits pass. Reachability improves to 1,547 actions, 2,354 reachable
  items, 159 orphan inputs, and 179 blocked actions.

## Iteration 50 — Blue dragon scale acquisition

- Result: the ordinary Dusty-key Taverley enclosure is live as `Gather blue
  dragon scales`, a seven-output zero-XP Utility trip through the established
  gathering, persistence, telemetry, and answer-undo path.
- Source: cutoff oldid `6169064` pins seven ordinary spawns, twelve optional
  level-60 Dungeoneering spawns, no quest gate, non-stackability, tradeability,
  and the scale-to-dust Herblore chain. The baseline needs no placeholder.
- Assets/data: cache identities 243/241 and distinct tightly cropped period
  sprites are registered for Blue dragon scale and Dragon scale dust. The
  existing selector supplies the UI, so no new interaction pattern or taste
  pass was needed.
- Verification: 314 focused tests and one focused real offscreen Qt test pass.
  Full plain and offscreen Qt discovery each pass 4,006 tests, with 488 plain
  skips and three Qt skips. The row makes 23 more items reachable and removes
  31 blocked actions, producing a 1,548-action / 2,377-reachable / 137-orphan /
  148-blocked ledger. Native Computer Use timed out twice and is not claimed.

## Iteration 51 — reachability leverage ranking

- Result: `tools/audit_item_reachability.py --rank-roots N` simulates adding
  each true root orphan independently, closes the same live action graph, and
  ranks the transitive item/action recovery. `--json` exposes exact recovered
  item lists; default output remains unchanged.
- Boundary: the score proves graph leverage only. It never claims that a source
  exists or waives period qualification. Multi-input roots may validly recover
  one item and zero actions.
- First ranking: Potato cactus +20/+19, Wyvern bones +12/+16, Uncut onyx
  +11/+11, Fellstalk seed +8/+5. Potato cactus is the next source candidate.
- Verification: two focused tests pass. Full plain discovery passes 4,007 tests
  with 488 expected skips; full real offscreen Qt passes 4,007 with three.

## Iteration 52 — Potato cactus acquisition

- Result: `Gather potato cacti` adds the three cutoff first-level
  Kalphite-Hive ground spawns through the established zero-XP Utility route.
  Persistence, telemetry, selector metadata, and answer undo remain shared.
- Source: Potato cactus oldid `6543078` and Kalphite Hive oldid `6529999`
  independently pin the three-spawn first-level route. Exchange oldid `6571111`
  pins item 3138. No placeholder is needed.
- Boundary: one-time rope setup, world travel, desert heat, poison, and hostile
  Kalphites remain collapsed route context, matching existing source-gathering
  rows. Quest-gated lower-floor spawns are not claimed.
- Leverage: reachability improves from 1,548/2,377/137/148 to
  1,549/2,397/124/129 for actions/reachable items/orphans/blocked actions.
- Verification: five focused checks and one real offscreen Qt selector test
  pass. Full plain and Qt discovery each pass 4,009 tests. Documentation, test
  quality, compilation, JSON, asset normalization, diff, and worktree audits
  pass. Workflows run `1951a8f4-904d-4e78-a010-7837aabb38ff` returned no usable
  result after both leaves exhausted bounded budgets; root did not retry it.

## Iteration 53 — Tokkul shops and Uncut onyx acquisition

- Result: Tokkul is live across the three ordinary TzHaar shops, and the Ore
  and Gem Store's one-stock Uncut onyx closes the full existing onyx Crafting
  graph for 2,700,000 Tokkul. Purchases reuse the established shop inventory,
  stock, review-restock, history, persistence, and direct undo transaction.
- Source: cutoff oldids `6570299`, `6438736`, `6393151`, and `6393148` pin the
  item, complete stock and price tables, and player-buy-only rule. Four
  cache-derived prices were corrected; no placeholder was introduced.
- Boundary: the first full generator run exposed active Darkan source drift
  (nine added and seven changed unrelated shops). Root rejected that diff and
  added deterministic currency-only regeneration against AnkiScape's pinned
  snapshot. Trading sticks and reward currencies remain untouched.
- Verification: 144 focused pure checks and one focused real Qt purchase pass.
  Full plain discovery passes 4,014 tests with 489 skips; full real offscreen
  Qt passes 4,014 with three. Documentation, test quality, compilation, JSON,
  deterministic regeneration, asset normalization, diff, and worktree audits
  pass. Reachability improves from 1,549/2,397/124/129 to
  1,549/2,413/117/118. Native Computer Use timed out and is not claimed.

## Iteration 54 — Fellstalk seed acquisition

- Result: Master Farmers can now yield one Fellstalk seed through the existing
  Thieving action. This unlocks the already-complete Farming and downstream
  potion graph without adding another player-facing surface.
- Source: Fellstalk seed oldid `6565142` and Master Farmer oldid `6565826`
  independently prove the route. The Master Farmer table pins quantity one and
  `Very Rare`; its hidden weight remains unavailable.
- Placeholder: `thieving.master_farmer_fellstalk_weight` records the smallest
  one-slot extension, taking the existing table from 2,199 to 2,200 slots.
- Asset correction: the modern 2025 seed icon is replaced with the cutoff
  `2012-11-17T05:53:59Z` revision and its exact provenance.
- Verification: 110 focused checks and two focused real Qt tests pass. Full
  plain and offscreen Qt discovery each pass 4,016 tests, with 489 expected
  plain skips and three Qt skips. Documentation, test quality, compilation,
  JSON, asset normalization, diff, and worktree audits pass. Reachability
  improves to 1,549 actions, 2,421 reachable items, 112 orphan inputs, and 113
  blocked actions.

## Iteration 55 — Cured yak-hide service

- Result: Thakkrad Sigmundson cures Yak-hide for 5 Coins each through the
  established batchable shop-service path. Quantity clamps, persistence,
  history, UI, and direct undo remain shared.
- Source: Cured yak-hide oldid `5967010`, Thakkrad oldid `6225987`, and The
  Fremennik Isles oldid `6540919` pin the conversion, price, location, and
  stage-5 access. Rev-742 pins items 10818/10820. No placeholder is needed.
- Boundary: `--services-only` preserves the 274-shop snapshot. The provider row
  reuses an existing UI pattern and its normalized 2010 sprite.
- Coordination: Emerald lens oldid `6202817`, Lunar Diplomacy oldid `6569662`,
  and rev-742 items 9064-9066 are handed to the Darkan quest lane. AnkiScape
  does not duplicate that quest change.
- Verification: 65 focused pure/integration checks and one focused real Qt
  test pass. Full plain and offscreen Qt discovery each pass 4,018 tests, with
  490 expected plain skips and three Qt skips. Documentation, test quality,
  compilation, JSON, generation, asset, diff, and worktree audits pass.
  Reachability improves to 1,550/2,423/111/111.

## Iteration 56 — Black mushroom acquisition

- Result: one zero-XP Utility pickup now supplies one Black mushroom from the
  cutoff Uzer/Goblin Cave ground source. The existing grinding action now
  consumes the required empty Vial instead of creating ink from a mushroom
  alone.
- Source: Black mushroom oldid `5513228`, Black mushroom ink oldid `6084503`,
  and rev-742 items 4620/4622 pin the source, recipe, identities, and
  non-stackable/non-exchangeable rules. No placeholder is needed.
- Assets: the cutoff 2011 mushroom and 2010 ink sprites are tightly normalized,
  registered, and pinned by exact timestamp, SHA-1, and dimension checks.
- Verification: 500 focused pure/integration tests, 131 focused
  asset/registry/reachability tests, and two focused real offscreen Qt tests
  pass. Full plain and offscreen Qt discovery each pass 4,021 tests, with 490
  expected plain skips and three Qt skips. Reachability improves to
  1,551/2,425/110/110.

## Iteration 57 — Unholy mould acquisition

- Result: the existing Chaos-druid target now supplies one Unholy mould on its
  ordinary table. A real Combat burst feeds the existing
  `silver_unstrung_emblem` reducer, which consumes one Silver bar, awards 50 XP,
  produces one Unstrung emblem, and preserves the mould.
- Source: Chaos druid oldid `6381798` and Unholy mould oldid `6088663` prove
  the route, quantity, item use, and semantics. Darkan commit
  `9a6db4df8d12a743d0318bcd524462512e838ff3` independently reconstructs item
  1594 at 1/128; rev-742 pins its client definition. No placeholder is needed.
- Asset repair: the distinct normalized 2011 sprite replaces the incorrect
  Holy mould fallback. A real offscreen Qt Bank test compares its rendered
  pixels with the registered file.
- Verification: 71 focused plain checks and one focused real Qt check pass.
  Full plain and offscreen Qt discovery each pass 4,023 tests, with 491 expected
  plain skips and three Qt skips. Documentation, test-quality, compilation,
  JSON, asset, diff, and worktree gates pass. Reachability improves to
  1,551/2,428/108/108.

## Iteration 58 — Razor-backed kebbit tracking

- Result: the level-49 grouped Hunter target now requires and preserves one
  Noose wand, collapses the four- or five-search trail into one review, awards
  348 Hunter XP, and produces Bones, Raw beast meat, and one Long kebbit spike.
- Source: Hunter oldid `6484443` pins the visible mechanic and outputs. Darkan
  commit `37957d17d62d6b14d326cd719a0ae0c239c76cf9` corroborates the route and
  tools but does not settle its hidden probability. Rev-742 pins items 10107
  and 9986.
- Placeholder: `hunter.razor_backed_kebbit_success_curve` uses the shared
  `rate1=128`, `rate99=256` fallback. Its level-49 source chance is `192/255`
  before review normalization. The earlier draft's `193/255` arithmetic was
  corrected before closure.
- Integration: the existing selector, Keep/Drop carried pack, cadence,
  telemetry, Shattered Heart, persistence, and review undo own the new row.
  Shattered Heart can replace two ordinary outputs while the chain-critical
  Long kebbit spike remains retained.
- Verification: six focused plain checks and one focused real offscreen Qt
  check pass. Full plain and offscreen Qt discovery each pass 4,026 tests, with
  491 expected plain skips and three Qt skips. Documentation, test quality,
  compilation, JSON, placeholder, asset normalization, reachability, diff, and
  worktree audits pass. Reachability improves to 1,552/2,431/107/106. Native
  Anki is not claimed. GPT-family root verified.

## Iteration 59 — Living rock remains acquisition

- Result: the level-73 Mining target now awards 25 XP and an inclusive 5–24
  Living-mineral bundle through the ordinary Mining review path.
- Source: Living rock remains oldid `6556376` pins the focused row. Living Rock
  Caverns oldid `6547876` corroborates access, level, XP, danger, and public
  corpse custody but conflicts at 5–20 minerals. Darkan commit `3e5880517`
  restores the custody mechanic and reconstructs the hidden `30/145` curve.
- Placeholder: `mining.living_rock_remains_rolls` registers the executable
  success endpoints and the uniform distribution inside the focused page's
  range. A period routine or stronger independent table would retire it.
- Integration: one review collapses the public-corpse wait without a wall
  clock or Combat prerequisite. The shared Mining reducer and telemetry now
  preserve actual primary bundle quantities. Existing single and weighted
  outputs remain unchanged.
- Verification: 485 focused plain checks and one real offscreen Qt selector
  check pass. Full plain and Qt discovery each pass 4,029 tests, with 491
  expected plain skips and three Qt skips. Documentation, test quality,
  compilation, JSON, placeholder, asset normalization, diff, reachability, and
  worktree checks pass. Reachability improves to 1,553/2,434/105/104. Native
  Anki is not claimed. GPT-family root verified.

## Iteration 60 — Crystal key and chest acquisition

- Result: Tooth and Loop halves combine into one Crystal key through the
  established level-1 zero-XP Crafting path. One Utilities review consumes the
  key and awards the guaranteed Uncut dragonstone plus one measured bonus row.
- Source: Crystal key oldid `6428315`, Crystal chest oldid `6491268`, and
  Exchange oldid `6570440` pin the combination, key consumption, twelve-row
  table, 24,786-Coin guide price, and 100-item buy limit. Rev-742 pins the item
  identities. Darkan corroborates the combination and chest but loses to the
  period table where its quantities and gender output conflict.
- Placeholder: `crystal_chest.ring_of_wealth_improvement` gives a 25% chance
  to draw a second measured row and keep the higher period-value tier. It
  selects only authentic rewards; a period routine or qualified sample would
  replace the hidden modifier.
- Integration: Ring of wealth is now real ring-slot equipment. Exact outputs
  flow through telemetry, achievements, persistence, and review undo. The
  Utilities selector displays the key gate, guaranteed reward, possible bonus,
  and normalized cutoff key art.
- Verification: 682 focused plain checks and one focused real offscreen Qt
  check pass. Both full discovery lanes pass 4,036 tests, with 492 expected
  plain skips and three Qt skips. Reachability improves to
  1,555/2,436/104/103. Documentation, test quality, compilation, JSON,
  placeholder, asset normalization, diff, reachability, and worktree checks
  pass. Native Anki is not claimed. GPT-family root verified.

## Iteration 61 — Quest-grant reachability correction

- Finding: the audit seeded final quest rewards but ignored inventory granted
  at quest start and during individual stages, so it falsely classified
  `Dramen branch` as a root orphan despite the live Lost City stage-4 grant.
- Correction: registered `start_inventory` items now use
  `quest-start:<quest_id>` routes; registered stage `produced_inventory` items
  use `quest-stage:<quest_id>:<stage>` routes. Final reward routes are
  unchanged.
- Result: the graph exposes 134 authentic existing grants. `Dramen branch`
  resolves through Lost City and `Cinnamon` through the existing Utility
  action. Reachability improves to 1,555/2,570/103/102 without a gameplay,
  quest, UI, asset, save, or placeholder change.
- Verification: the regression fails before the correction. Focused
  reachability and quest-runtime checks pass 201 tests. Both full discovery
  lanes pass 4,036 tests, with 492 expected plain skips and three real
  offscreen Qt skips. Native Anki is not claimed. GPT-family root verified.

## 2026-08-19 — resumed run, promotion of stranded slices

Resumed after deleting the stale `GOAL-BLOCKED.md`, whose named unblocker
(the `claude` daily block) had reset days earlier while main carried Pass 10 to
closure.

Verified baseline, `main` at `26ccb2a4378f3968e2f255b5f34bddd8ffe889de`:

    plain lane   Ran 4144 tests ... OK (skipped=499)
    qt lane      Ran 4144 tests in 541.966s ... OK (skipped=3)
    audit_docs   Audited 575 Markdown and 437 HTML files. Documentation audit passed.
    reachability 1571 actions; 2266 reachable items; 84 orphan inputs; 87 blocked actions

A read-only queue audit found that only ONE new implementation slice is
unblocked and owner-settled: the one-way skill-button availability refresh.
Everything else that looked open is either already landed, source-blocked, or
sitting on a `goal/*` branch that was accepted and never merged. Confirmed
independently with `git cherry main <branch>` on every goal branch:

| branch | unmerged commits | files | content |
| --- | --- | --- | --- |
| `goal/papercuts-2026-08-11` | 1 | 12 | tooling guardrails |
| `goal/breadth-2026-08-11` | 3 | 30 | Skeletal Wyvern and Wyvern bones |
| `goal/herbs-2026-08-11` | 3 | 25 | grimy herb family |
| `goal/vines-2026-08-11` | 1 | 27 | Juju vine secondaries |
| `goal/secondaries-2026-08-11` | 2 | 28 | acquisition work; its own final commit records a handoff instead of authorizing merge |
| `goal/jungle-potion-2026-08-13` | 1 | — | Jungle Potion |
| `goal/stage-satisfiability-2026-08-13` | 1 | 1 | audit-document correction only |

So the remaining goal work is mostly promotion, not authoring. Conflict pairs
that must never merge concurrently: herbs with vines, jungle with secondaries,
breadth with secondaries.

Placeholder retirement is NOT open work: only three register rows have never
been re-walked (`fish_flingers.xp_payout`,
`bone_sources.frost_dragon_generated_levels`,
`bone_sources.ogre_coffin_selector_weights`) and all three are source-blocked.
The other 172 were re-walked on 2026-08-13.

The MacBook Pro is now reachable for headless work as
`ssh armans-macbook-pro '<cmd>'`, but it has no repository copy and no Qt
environment yet.

### Wrong merge parent in two Jungle Potion records — found 2026-08-19, correction owed

The Jungle Potion re-land merge `6b5e41ac1610a782eecf46790258a5e50f9c3827` has
parents `3cbe114a3c43fd031f09fc5a5582c0d10a6a17cc` and
`6c482e617ffbe1f803b2a17fb00fb74a0d07a305`. Two durable records on that branch
instead name `26ccb2a4378f3968e2f255b5f34bddd8ffe889de` as the merge parent:

- `memory-bank/activeContext.md:5027`
- `memory-bank/source-audits/quest-jungle-potion-playable-2026-08-13.md:133`

The reachability figures those records carry are still numerically valid,
because `26ccb2a4`, `6c482e61`, `1f878577`, and `323bf390` differ only in
Memory Bank text. The wording is still wrong: a later seat checks out the
identifier, not the argument for why the identifier does not matter.

Cause is the brief, not the agent. Every re-land brief in this run quotes the
verified baseline at `26ccb2a4`, and the agent recorded the briefed identifier
rather than the one it actually merged. Check every other re-land branch for
the same substitution before promoting it: `breadth-reland`, `herbs-reland`,
`papercuts-reland`, `remote-test-host`, `skill-button-refresh`.

Resolution: this is a review finding, and the slice pipeline's resolve stage
already provides for one commit after review. No rail is relaxed by correcting
it there. Future briefs must label a quoted baseline as "measured at", and say
explicitly that the record must name the merge parent the agent actually
merged.

### Review round one: three of four slices rejected

Every slice that reached an independent Opus review on 2026-08-19 came back
with real defects. None of the rejections were style.

**Jungle Potion — REJECT.** A Shattered Heart strange rock replaces the clean
herb produced by the quest's Herblore step, because `_record_action` in
`runtime/runtime_actions_shared.py:566-575` subtracts the produced output as
the rock's replacement. Each grimy jungle herb has exactly one producer, the
already-passed search stage, so the quest becomes permanently unfinishable and
takes Shilo Village and thirteen exclusive items with it. Incidence
`1 - 0.99**5` = 4.9% of playthroughs. The accompanying test hid it by calling
`player_data.pop("shattered_heart", None)`.

**Skeletal Wyvern — REJECT.** Protect from Melee nullified the ice breath
entirely, defeating the six-shield mechanic the slice exists to ship
(`logic_pure/logic_pure_combat_engine.py:1455`).

**Tooling guardrails — REJECT.** A new root `.ignore` hid `data/shop_data.py`
and `data/construction_data.py` from every ripgrep search, including
`tools/repo_search.py --include-large`, which promises to include them. And
`tools/worktree_guard.py audit` aborted with exit 2 for any caller without
`CLAUDE_CODE_SESSION_ID` — the guard every dispatched agent depends on.

**Skill buttons — ACCEPT WITH FINDINGS.** The first commit had already been
rejected for over-disabling Crafting; that was confirmed genuinely fixed, both
paths now calling `crafting_target_locked_reasons_pure` with identical
arguments. Smithing still read a bool captured at menu-open rather than a live
predicate.

Two patterns worth keeping. Every reviewer independently re-ran a lane rather
than trusting the author's counts, and every count held: the failures were
never in the numbers, only in what the tests were pointed at. And the two worst
defects were both pinned by tests that removed or hand-fed the state that
triggers them, which is the same signature as the 2026-07-26 batch.

### Review round two, and a pattern in what the reviews keep finding

**Skeletal Wyvern — ACCEPT WITH FINDINGS.** The blocking prayer defect is
confirmed genuinely fixed and not over-corrected, proved by driving the real
kernel with controls: melee-only 8614 damage falls to 0 under Protect from
Melee, ranged-only 8335 falls to 0 under Protect from Missiles, breath-only
38643 is unchanged under both, and ordinary enemies are unaffected. The four
remaining findings are all record integrity in
`memory-bank/source-audits/wyvern-bones-acquisition-2026-08-11.md`.

**Tooling guardrails — REJECT again.** The audit abort MOVED rather than went
away: it now fires for callers that DO set `CLAUDE_CODE_SESSION_ID` while
standing in any of the 49 unmarked worktrees. Decision taken by the
orchestration seat: remove the worktree-ownership feature from the branch
entirely rather than fix it a third time. It has broken the guard twice in two
different ways, its own reviewer calls it first-come with no collision
detection, and it defends against a problem that has not occurred while `audit`
failing stops every dispatched slice before its first edit.

**Grimy herbs — REJECT.** Three majors. The worst is scope creep, not herb
work: the branch added a short-circuit to `_set_value` at `__init__.py:4557` so
it skips saving when the value is unchanged, which silently discards the
in-place mutation `_set_combat_attack_style` makes immediately before it.
Unarmed, staff, sceptre and hammer weapons are all `crush` in
`WEAPON_TYPE_UNARMED_STYLES`, so switching Accurate to Aggressive unarmed never
persists and reviews keep awarding Attack XP instead of Strength. Confirmed
against `main` that the short-circuit is branch-introduced; main's `_set_value`
always saves, so no live save is affected. Also: all five vine-herb seeds gated
at Hunter 78 when the branch's own cited Darkan source supplies them from the
Hunter 70 Common jadinko at 16/256, and an icon gate weakened from an
empty-list assertion to a seven-item allowlist.

The pattern across every rejection so far: the reported numbers were always
true, and every independent reviewer that re-ran a lane got the author's exact
counts. What the reviews catch is never a false measurement — it is a test
pointed at the wrong thing, an instrument quietly loosened, or an unrequested
change riding along inside a slice about something else.

### First promotion: Skeletal Wyvern, main at 7fb738e5

Merged `goal/breadth-reland-2026-08-19` through the full gate in worktree
`promote-2026-08-19`. Post-merge run on the merged tree, all green:

    plain lane   Ran 4152 tests in 374.657s   OK (skipped=499)
    qt lane      Ran 4152 tests in 613.858s   OK (skipped=3)     [monolithic]
    audit_docs   Audited 577 Markdown and 437 HTML files. Documentation audit passed.
    test_quality 4117 tests across 188 files; hard issues: 0
    reachability 1571 actions; 2278 reachable items; 72 orphan inputs; 71 blocked actions
    worktree_guard  layout safe
    git diff --check  clean

Reachability improves against the pre-merge baseline of `1571 / 2266 / 84 / 87`:
twelve more reachable items, twelve fewer orphan inputs, sixteen fewer blocked
actions.

The Qt lane ran monolithically at 613.858 s because a detached `nohup` script
has no tool command cap. That is the cheapest way to run the real Qt lane
without partitioning it, and it should be the default for promotion gates.

Main had advanced by one papercut commit while the gate ran, so the verified
tree absorbed it before landing; the only file differing from the gated tree
is `memory-bank/papercuts.md`. Do not commit to main while a promotion gate is
running — it forces this reconciliation every time.

### Skill-button slice accepted with two recorded non-blocking minors

`goal/skill-button-refresh-2026-08-19` at `cfe999c6` took three rounds. Final
independent verdict is accept with findings, and the reviewer confirmed by
driving the real widget that Smithing now recomputes from
`smithing_target_locked_reasons_pure` on every render rather than from a bool
captured at menu-open, and that the regression forces a real `_render_panel()`
instead of hand-feeding a value.

Two minors are deliberately NOT fixed, and are recorded here rather than
polished away while the Codex block runs down:

1. `__init__.py:787` — the availability cache fingerprint gained `"crafting"`
   but not `"smithing"`, although Smithing availability now applies
   `QUEST_UNLOCK_RULES` and `data/quest_data.py:9395` gates `forge_cannonballs`
   on `dwarf_cannon`. The reviewer could not construct a player state that
   produces a wrong output, because completing the quest grants an Ammo mould
   which is itself a tracked requirement item. An asymmetry to close, not a
   shipped defect.
2. `ui/ui.py:1465` — the seven unavailable-tooltip strings are duplicated
   verbatim between `refresh_skill_availability` and the panel render path at
   `ui/ui.py:22840-22857`, so editing one leaves the other emitting old text.
   The available branch also sets the tooltip to the bare skill name while the
   render path sets none, so an enabled button silently acquires a tooltip
   after the first refresh.

### The post-merge gate earned itself on the second promotion

Both branches were independently green. Wyvern passed its lanes at 4152 tests
and landed on main; the skill-button slice passed its own at 4148. Merged, the
plain lane gave `Ran 4156 tests ... FAILED (errors=3, skipped=502)`:

    File "tests/test_skeletal_wyvern.py", line 99, in _runtime_context
        return RuntimeActionContext(
    TypeError: RuntimeActionContext.__init__() got an unexpected keyword argument
    'refresh_skill_availability_partial'. Did you mean 'refresh_skill_availability'?

The skill-button slice deleted `refresh_skill_availability_partial` because a
reviewer found it had zero production callers, which was correct. The Wyvern
test helper was written before that deletion existed. Neither branch could see
the other, no review could have caught it, and only a run on the merged tree
could.

This is the argument for the goal's promotion rule in one incident: a slice
being green on its own branch says nothing about the tree it lands in. Keep
running the full gate on the merged tree, and keep landing one slice at a time
so an integration failure names its own cause.

Handling: the failed merge stays on `promote/2026-08-19` rather than being
reset, since a hard reset is forbidden here and the merge is reproducible. The
next promotion cuts a fresh promote branch from main.

### Fix rounds manufacture the next defect, and the mechanism is gate pressure

`goal/herbs-reland-2026-08-19` has been rejected three times. Each rejection was
real, each fix was correct on its own terms, and each fix introduced the next
rejection — every time by producing a plausible value to make a gate pass.

Round two found five vine seeds over-gated at Hunter 78 against the branch's own
cited Darkan source. Round three fixed the gating correctly and, in the same
commit:

- invented the item name "Common vine" for item 19971, whose period name is
  "Withered vine" per Darkan `config.json` uidName `withered_vine`. Because the
  name matches nothing in the generated tables, the item has no price and cannot
  be sold: `preview_shop_sell_pure` returns `sell_price_unresolved` for it while
  "Pungent vine" is allowed at unit price 1. The source audit recorded the
  fabricated name as sourced fact;
- satisfied the icon gate it had just been told to restore by shipping a
  1302x313, 314,693-byte "Withered vine detail" render as an inventory sprite,
  next to seven real 28x25 sprites of about 550 bytes. It renders as a ~32x8
  sliver;
- asserted `VINE_HERB_DISEASE_SLOTS = 6` as sourced from the generic Darkan
  growth selector, eleven lines above a `SHARED_DISEASE_SLOTS = 6` that carries
  `PLACEHOLDER(farming.shared_disease_slots)` for the identical number, and
  whose register row says that selector cannot settle a crop-specific value.

The pattern to carry forward: **a fix round is where invented facts enter.** The
agent is under pressure to make a named gate go green, and a plausible name,
number, or asset does that. Every fix brief should therefore say what this one
now says — when evidence does not settle something, register a placeholder or
delete the row, and never produce a value that merely looks right.

### The secondaries branch is promotable, and the caveat that looked like a gate is not one

`goal/secondaries-2026-08-11` looked self-refusing: its final commit subject is
"Avoid merging the abandoned branch by recording the verified handoff". A
read-only triage, then the orchestrator reading the record verbatim, both find
the opposite. `memory-bank/handoffs/claude-handoff-2026-08-11-evening.md:17-20`
says plainly:

> The work started on `goal/grind-2026-08-11`. It moved to
> `goal/secondaries-2026-08-11`.
>
> Merge `goal/secondaries-2026-08-11`. Do not merge the old branch. The old
> branch is abandoned and dirty.

The subject refers to the OLD branch. This one is the named merge target.

The sentence that reads like a shipping gate — "Do not ship this implementation
without connected station context" — sits under "Facility Prerequisites" and
refers to the station reference implementation left in the abandoned worktree,
not to this branch. The same handoff records that the committed tree has zero
`station` references and zero added station lines. So nothing gates this branch,
and the genuine owner decision is the separate question of whether runtime code
should enforce facility prerequisites at all.

NOT started this run, deliberately. It is a 28-file re-land needing a merge,
verification, an independent review and likely two fix rounds, and it conflicts
with the Jungle Potion branch on `data/herblore_data.py` and `data/quest_data.py`
and with the Wyvern work now on main. There is not enough Codex block left to
carry it honestly, and starting it would leave a half-verified branch. Next
session begins here with the gate question already settled.

That handoff is also worth reading for its own sake: it records five sessions
writing to one worktree in an hour, three of them rebuilding an unapproved API
from a `code-review` finding the review never issued, and work orders claiming
falsely that each session was the only writer. That is the same failure family
as today's two-writer collision, and it is why this seat now names one
escalation route and one worktree owner.

### The strange-rock interaction is a class, not two bugs — and both fixes overreached

Independent reviews found the same defect family in two unrelated slices on the
same day. A Shattered Heart strange rock replaces a produced output, and where
that output is hard to re-obtain the save is stuck.

- Jungle Potion: the rock ate the clean herb a quest step produced, and each
  grimy jungle herb had exactly one producer, the search stage already passed.
  4.9% of playthroughs.
- Juju vines: two loose Hunter rocks ate both the guaranteed Jadinko output and
  a 1/80 rare seed, and the four potion inputs are untradeable.

A cross-catalog scan on the Jungle branch found only one other quest-item
transformation through a rock-eligible handler, Heroes' Quest `cook_lava_eel`,
which is recoverable through repeatable fishing. So the exposure is now
believed closed — but both fixes had to be corrected:

- Jungle's fix is keyed on target id and never on quest state, so post-quest the
  five jungle herbs pay a rock with no output cost while every other herb pays
  one output per rock. Verified: `POST-QUEST clean sito foil = 1 rock1 = 1`
  against `ORDINARY clean guam = 0`. Post-quest they become the strictly best
  Herblore rock farm in the game.
- Vines' fix narrowed the replacement pool for every OTHER Hunter target from
  post-bonecrusher `retained_outputs` to spec-only `primary_outputs`, so a rock
  destroyed banked Bones the action never produced and telemetry stopped
  matching inventory. Seeded probe, 400 reviews, `random.Random(11)`: pre-fix
  Bones 100, post-fix Bones 98.

Both fixes were also written as hardcoded id literals duplicating a membership
the data layer already owns, so a sixth Habitat route would silently reopen the
soft-lock. Derive from the untradeable-output property instead.

### The vine slice is NOT landed, and the defect that stopped it was caused by my own finding

`goal/vines-reland-2026-08-19` merged cleanly, its re-measured pins are correct
at `1586 / 2307 / 75 / 45 / 30 / 75 / 1123`, and its gate's plain lane is green
at 4,172 tests with 502 skips. It is still not promotable, for two majors found
on the merged tree.

**1. An invented mechanic, and I caused it.** The branch now makes the Juju
hunter potion a drinkable `+3` Hunter boost. Driving the real kernel,
`apply_consumable_pure` returns `boosts={'hunter': 3}`. Darkan
`Potions.kt:522` is a flavour-message-only effect with no stat change — "You
decide that only plants are likely to enjoy the taste of this potion". The
then-current ledger correctly rejected the boost but over-read the same source
as saying the dose is not consumed. Direct inspection of `Potions.kt:881-904`
shows the row inherits `canDrink=true` and the shared path consumes a dose.

The cause was the source summary I forwarded, not removal of a valid negative
mechanic. The `drinkable` guard encoded the ledger's mistaken refusal; deleting
it exposed the separate invented `flat_skill` boost. The correct shape is the
generic dose chain with empty skills and the sourced flavour message.

The lesson is to trace an enum row through its inherited control flow before
turning a flavour line into a refusal. A row-local message does not establish
whether the shared drink path consumes the item.

**2. A known-wrong record.** `memory-bank/activeContext.md:114` on the merged
tree still says "4,159 plain tests with 499 skips" and reachability
`1,576 / 2,284 / 75 / 45 / 30 / 75 / 1,105`, contradicting the baseline the same
commit pins. Same class main already had to correct in `d1af99b2`.

Neither is blocking today, because the Juju hunter chain is unreachable — all
four doses are orphan inputs. Both go live the moment the vine_herb farming
chain lands, which is why this must be fixed before promotion rather than after.

### Undo-seam migration: the ratified shape, and why one reviewer beat six

Seven `_apply_*` handlers were migrated onto `commit_direct_action` by seven
independent agents. All seven were reviewed by ONE cross-lineage reviewer rather
than seven, and that choice found a defect no per-branch review could have:

`goal/undo-star-2026-08-21` deleted the trailing
`if __name__ == "__main__": unittest.main()` block from
`tests/test_direct_action_undo_seam.py`. Each sibling appends its tests
immediately above that guard, so `git merge-tree` across the fifteen branch pairs
showed star conflicting with ALL FIVE siblings, against six conflicts among the
other nine pairs combined. One branch's out-of-scope deletion was a merge
collision multiplier, and it is invisible unless you read the branches together.

**The ratified shape for the remaining twenty-five migrations.** `commit_direct_action`
returns False for two different reasons and they need different answers:

    accepted = False
    def _change(current):
        nonlocal accepted
        updated, info = ...pure_function...
        accepted = bool(info.get("ok"))     # capture the pure result
        return updated, accepted

    if not commit_direct_action(_change, after_apply=_after_apply):
        if accepted:                        # pure succeeded, undo entry failed
            return {"ok": False, "reason": "undo_unavailable", ...}
        return {**info, ...}                # pure refused

Branch on the CAPTURED FLAG, never on the presence, truthiness or identity of a
payload key. Three of the six diverged on this — star probed `info["reason"]`,
agility used `result.get("allowed") is False` — and both are correct today only
because every current return path happens to set a real value. Warriors and GE
used the captured flag and are the reference implementations.

Also ratified: the `"reason": "undo_unavailable"` key that Farming added and main
did not have. It is additive, it matches GE, and it makes the failure
machine-distinguishable. Carry it everywhere.

**A migration can create a failure mode rather than drop one.** On main,
MTA's `select_alignment` never created an undo entry, so it could not fail that
way. Routing it through the seam made a successful alignment choice newly
contingent on `add_custom_undo_entry`, and the first cut lost the choice silently
with no message. Check every handler for sub-actions that previously bypassed the
undo path entirely; they need a deliberate decision, not an inherited one.

### Fix-by-instance: four rounds where each fix produced the next finding

`goal/herbs-reland-2026-08-19` has now taken eight review rounds. Every finding
was real and every fix was correct, but rounds six through nine share one shape:

- round six named three Jadinko rows missing their secondary drop tables; the
  fix implemented those three;
- round seven named two rows still on a placeholder success curve when the
  branch's own audit cited the file containing their endpoints; the fix
  corrected those two;
- round eight then found three MORE rows missing their secondary tables, one of
  which (Guthix) fits the existing one-table contract exactly as two already-
  implemented rows do, so the recorded blocker never explained its omission.

Measured, not argued: 200,000 seeded catches per row gave Saradomin 1.932%
against a source 5/256 = 1.953%, and Guthix and Shadow exactly zero.

**The lesson is about the brief, not the agent.** A finding that names instances
gets instances fixed. When a defect is a class — every row of a table checked
against its source — the brief has to ask for the enumeration and require a
disposition for every member, or the next round finds the members nobody named.
Round nine asks for the sweep: a table of all ten rows, each ending in exactly
one of implement / register-with-adjacent-marker / source-gives-nothing.

Watch for the same shape elsewhere. It is cheap to produce and expensive to find:
each round looks like progress because the named thing really was fixed.

### Bound an enumeration by the source, never by the artifact under review

The herb branch's fix-by-instance cycle was broken by asking for a sweep — a
table of every jadinko row with a required disposition each. It worked: three
missing direct tables implemented, six genuinely multi-table rows given adjacent
markers, 200,000-action probes confirming 3,787 drops on each new row.

Then the reviewer found the sweep was still bounded wrongly. The brief said
"enumerate ALL ten catch/track jadinko rows". Ten was the count of rows the
BRANCH had. Darkan's `JadinkoType.kt` defines THIRTEEN jadinkos with THREE
trackers — `SHADOW`, `DISEASED`, and `CAMOUFLAGED` — and the branch has two.
`hunter_jadinko_camouflaged.json` sits in the directory the audit cites, giving
bush seeds 16/256, four vine-herb seeds 4/256, and blossom 4/256. Nothing in the
tree mentions item 19978, and the records read as complete enumerations.

So the rule is not "sweep the class" but something sharper:

**Take the enumeration set from the source, never from the artifact under
review.** A sweep bounded by what the branch already contains cannot discover
what the branch omits — it only re-confirms what is there. The brief has to name
the source of truth for the row set (here `JadinkoType.kt` plus the drop-file
directory) and require the report to list which source rows the slice does NOT
implement.

Camouflaged itself is being disclosed, not implemented: a third tracker route
with its own feature gate and produce type is new content and belongs in its own
slice, not in a herb re-land. That is the BFS boundary — found only because of
this work, so surface it rather than fix it.

- 2026-08-23 q-scb source correction: Song from the Depths oldid `6467675` awards 700 Constitution XP at completion; its additional 30,000 XP comes from two optional post-quest Ancient Walls, and reduced Queen Black Dragon damage is an unlock rather than an item. Some Like It Cold oldid `6545099` awards 40,000 Crafting, 40,000 Fishing, 10,000 Construction, and 10,000 Thieving XP plus both Rock and Pop costumes; the duplicate XP was an early-bird tome that expired on 2012-08-28, and Penguin Hide and Seek is an extension rather than an item. Rev 727 item IDs `24863` and `24864` are unnamed preloads; rev 742 names them `Rock costume` and `Pop costume`, with `Wear`/`Destroy`, `stackable=false`, and `exchangeable=false`.
- 2026-08-24 q11 quest-reward correction: Darkan `SheepHerder.kt` commit `585a1e2977be5c5c6c777eaafdb3f5f750e69166` grants only 3,100 coins in `complete()`, and Darkan `ColdWar.kt` commit `0627fcbe3f0882adb55887b1976a1f8b7f897a09` grants only the three XP rewards and unlock side effects. Darkan and game-main contain no Hunt for Red Raktuber completion implementation; pinned wiki oldids `6579802`, `6545129`, and `6579210` distinguish Penguin Hide and Seek/Chuck unlock prose and already-kept quest gear from completion item grants. Runtime replacements are therefore empty for `cold_war` and `hunt_for_red_raktuber`, and coins-only for `sheep_herder`.
