# AnkiScape grind-loop queue

Source: `memory-bank/codex-briefs/ankiscape-grind-loop-2026-08-03.md`.
Process one unblocked item per iteration. Move discovered design gaps to
`memory-bank/design-thread-queue.md`.

1. [x] Pass 6 item B.15 — skill-selector hybridization.
   Implement only `memory-bank/codex-briefs/pass6-b15-handoff-2026-08-03.md`.
2. [x] Design answer 3.25 — guardian coin drops.
   Remove the Dungeoneering starter Herblore coin cache and pay the registered
   guardian-room placeholder on critical-path C5+ floors.
3. [x] The 384-diary-task clause.
   Implement the 32 tiers of 12 curated tasks settled in
   `memory-bank/achievement-diary-item-grants-design.md`.
4. [ ] Depth work.
   Start with `memory-bank/breadth-next-tranche.md`, then process registered
   placeholders and player-visible data-depth debt from `activeContext.md`.
   - [x] Decode period-cache enums, structs, and params.
   - [x] Decode interface definitions.
   - [x] Re-walk client-side `source_blocked` rows; leave server-side gaps alone.
     Rev-727 Conquest NPC params retire the Foot Soldier cost conflict at 50;
     diary lamp floors and the remaining server-owned formulas stay blocked.
   - [x] Decode exact item model/recolour rows and re-walk item-identity and
     asset placeholders. Rev-727 fixes the Temple Trekking blue/yellow swap;
     rev-741 fixes all four Goblin Raids equipment IDs, trade rules, and bonus
     arrays. Dominion Tower's unknown reward IDs remain source-blocked.
   - [x] Retire the Achievement Diary's recorded depth debt. Generation now
     requires an explicit portable `--items-yml` input; the v108 regression
     proves removal, re-earning, and preservation across the migration boundary.
   - [x] Decode the rev-727/742 Frozen Dungeoneering boss NPC combat-level rows
     and revalidate the six provisional ladders. Both caches match every live
     value; server-owned stat and scaling formulas remain untouched.
   - [x] Re-walk the Daily Challenges reward-XP placeholder through the dated
     config/interface readers and existing period sources. Keep it registered
     if no client table settles the server payout.
   - [x] Re-walk the four Skeletal Horror phase-stat placeholders through dated
     NPC definitions and authentic Darkan combat records. Do not derive core
     stats from combat level.
   - [x] Re-walk the six Duel Arena cap-tier thresholds through period pages,
     dated item definitions, and any authentic server records. Keep the near-
     cutoff fallback registered unless pre-cutoff evidence settles all six.
   - [x] Re-walk Bork's Ork legion attack-style placeholder through authentic
     combat records and period pages. Preserve the distance abstraction unless
     a source settles the melee/ranged switch and accuracy penalty.
   - [x] Re-walk the Tears of Guthix green-tear chance through authentic server
     records, period captures, and the pinned source chain. Keep the derived
     rate registered if no source exposes the stream switch and catch roll.
   - [x] Re-walk the Daily Challenges eligible-pool assignment weights through
     Darkan, dated configs/interfaces, and the pinned period history. Preserve
     the uniform registered placeholder unless a server-side selector survives.
   - [x] Re-walk the Crucible rank-point thresholds through Darkan, period
     guides, and rev-727 script 6284's caller chain. Keep the server-side
     threshold placeholder if no source exposes the six promotion boundaries.
   - [x] Re-walk ordinary Crucible rank points per kill through Darkan, the
     launch update, and rev-727 script 6288's caller chain. Preserve the one-
     point placeholder unless a server award routine or exact statement survives.
   - [x] Re-walk Crucible Trophy bones per ordinary kill through Darkan, period
     article and item histories, and recovered client configs. Preserve the
     two-bone placeholder unless a server drop routine or exact statement survives.
   - [x] Re-walk the Crucible risk-expectation amount per combat level through
     Darkan, fee-interface caller chains, period article/talk histories, and
     contemporary player reports. Preserve the registered amount unless an
     authentic fee schedule survives.
   - [x] Re-walk the Crucible target-level offsets through Darkan's matcher
     history, period article/talk histories, and contemporary matchup reports.
     Preserve the registered spread unless a server matching band survives.
   - [x] Re-walk the Crucible event interval through period schedules, rev-727
     event surfaces, and the shared review-day translation. Preserve the
     half-hour-to-five-review conversion unless a stronger project cadence row
     already settles it.
   - [x] Re-walk the Goblin Raids active duration through the period event
     history and available server records. Preserve the registered 15-review
     completion window unless a real despawn duration survives.
   - [x] Re-walk the Goblin Raids ordinary-raider count through period images,
     NPC spawn records, cache maps and any surviving server implementation.
     Preserve five unless an authentic fixed or scaling count survives.
   - [x] Re-walk Commander Yodri's site-specific reward contents and selection
     rule through the dated Tip.It guide, period article history and surviving
     server records. Retire exact contents without inventing hidden weights.
   - [x] Pin the Raider chainbody and shield's explicit level-8 Defence
     requirements from the dated Tip.It guide and exercise the real equip gate.
   - [x] Close Fishing Trawler's Tiger shark row from cutoff item pages and
     rev-741 definitions, including its one-per-trip admission, Cooking chain,
     combat-food behavior, exact item semantics, and normalized sprites.
   - [x] Replace Shooting Stars' six-site breadth sample with all 43 cutoff
     crash sites, preserving live legacy events through exact-name repair.
   - [x] Replace Penguin Hide and Seek's twelve-row breadth sample with all 34
     one-point and 33 two-point cutoff location/disguise pairs.
   - [x] Complete Managing Miscellania's six cutoff resource families and keep
     unrecovered server selectors explicit in the placeholder register.
   - [x] Complete Mage Training Arena's 25-row cutoff reward catalog, canonical
     outputs, Infinity/Mages' book equipment rows, and normalized source art.
   - [x] Complete Great Orb Project's ten-row ordinary talisman catalog with
     exact free/member prices and normalized selector art. Keep standard robe,
     staff, and teleport mechanics separate.
   - [x] Complete Great Orb Project's Master Runecrafter reward/equipment/XP
     family with exact piece rates, full-set bonus, bonus cap, and source art.
   - [x] Complete Great Orb Project's three-colour standard Runecrafter robe
     family with exact prices, identities, equipment stats, activity-only XP
     scope, labeled rate placeholder, and normalized selector art.
   - [x] Complete Great Orb Project's talisman-staff family with the exact base
     purchase, twelve ordinary bindings, Korvak Omni conversion, altar access,
     Law exception, equipment stats, carried recipes, and normalized art.
   - [x] Complete Great Orb Project's cutoff teleport-tablet family with exact
     prices, identities, stackable Break actions, period gates, route-phase
     integration, direct undo, carried-view reconciliation, and normalized art.
   - [x] Complete Shades of Mort'ton's reconstructed bronze-chest catalog with
     all 23 reward identities and quantities, three live key modifiers,
     one-clue enforcement, poisoned-dagger equipment rows, and normalized art.
   - [x] Complete Trouble Brewing's 27-row naval-cosmetic and flag catalog with
     exact prices, equipment definitions, atomic purchase/undo, source art,
     selector icons, and selection-state refresh.
   - [ ] Complete Trouble Brewing's two rum teleport rewards through the
     established direct-action route/undo seam.
   - [ ] Complete Honest Jimmy's 5,000-Piece medium-clue service through the
     settled Treasure Trails one-clue-total rule.
   - [ ] Complete `The stuff` through the owning mature-ale brewing action.
