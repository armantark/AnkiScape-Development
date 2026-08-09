# AnkiScape grind-loop notes — 2026-08

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
- The interface search no longer dies on the first legacy IF1 archive. It
  reports all fifteen unsupported rev-742 interface IDs on standard error and
  continues searching the decoded remainder, making negative evidence honest.
- Result: `daily_challenges.reward_xp` remains registered at 100 XP per required
  level. A period server payout routine or independently stated amount is still
  required to replace it. No gameplay value changed.
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
