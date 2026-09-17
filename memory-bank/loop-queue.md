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
   - [x] Complete Trouble Brewing's two rum teleport rewards through the
     established direct-action route/undo seam.
   - [x] Complete Honest Jimmy's 5,000-Piece medium-clue service through the
     settled Treasure Trails one-clue-total rule.
   - [x] Complete `The stuff` through the owning mature-ale brewing action.
   - [x] Close the shared Crafting/Fletching temporary-level potion substrate
     before adding further boost-dependent consumable catalog rows.
   - [x] Harvest the shared six-skill brawling-gloves constants. The period
     multipliers, identities, and five action limits are closed. Mining's
     review-action count and the unobtainable Revenant/Chaos Elemental drop
     route remain explicit implementation dependencies.
   - [x] Complete Cooking gauntlets through Family Crest conversion, remembered
     enchantment and recovery, physical target-local equipment, eight dated
     no-burn thresholds, persistence, undo, UI, assets, and cadence routing.
   - [x] Complete the three Karambwan Cooking methods with period quest gates,
     outputs, XP, normalized assets, and registered hidden-roll placeholders.
   - [x] Close brewing-input acquisition with level-1 zero-XP Barley malting
     and Blandebir's 25-Coin batchable Ale yeast service.
   - [x] Close Arctic pine and Eucalyptus Woodcutting acquisition with period
     rows, registered hidden-roll placeholders, access gates, selector art,
     reachability, persistence, and review undo. Keep Cursed magic parked on
     the missing Spirit of Summer quest substrate.
   - [x] Close the Dagannoth Kings room and Dragon-hatchet acquisition route
     through a reusable persistent boss-room substrate, the three period combat
     rows, dangerous multi-enemy pressure, Slayer integration, persistence,
     undo, Activities UI, normalized sprites, and registered hidden values.
   - [x] Close Blue-dragon-scale acquisition through the seven-spawn ordinary
     Taverley route, exact item identities, normalized period art, shared
     Utility gathering/undo, and the existing dust and Herblore chains.
   - [x] Add deterministic root-orphan leverage ranking to the reachability
     audit so data-depth BFS selection uses transitive item/action gain rather
     than intuition.
   - [x] Close Potato-cactus acquisition through the three-spawn ordinary
     first-level Kalphite-Hive route, exact item identity, normalized period
     art, established Utility gathering/undo, and the existing Magic-potion
     chain.
   - [x] Activate Tokkul across the three cutoff TzHaar shops, correct the four
     period price conflicts, enforce player-buy-only behavior, and close Uncut
     onyx acquisition through the established Shop and Crafting runtimes.
   - [x] Close Fellstalk-seed acquisition through the cutoff-proven Master
     Farmer route, register only its hidden relative weight, and replace its
     modern sprite with the normalized pre-cutoff revision.
   - [x] Close Cured-yak-hide acquisition through Thakkrad's 5-Coin stage-5
     service, preserving the pinned shop snapshot and atomic service undo.
   - [x] Close Black-mushroom acquisition through the cutoff Uzer/Goblin Cave
     ground source, and correct ink grinding to consume the required empty Vial.
   - [x] Close Unholy-mould acquisition through the cutoff Chaos-druid drop,
     preserve the mould through the existing Crafting chain, and replace the
     incorrect Holy mould sprite fallback.
   - [x] Close Long-kebbit-spike acquisition through the cutoff Razor-backed
     tracking row, registering only the hidden catch curve and reusing the
     established Hunter selector, carried-pack, and review-undo paths.
   - [x] Close Living-minerals acquisition through the level-73 Living-rock-
     remains row, with the focused cutoff bundle, registered hidden rolls,
     accurate multi-output telemetry, selector art, persistence, and review undo.
   - [x] Close Crystal-key and Uncut-dragonstone acquisition through the exact
     key-half combination, measured Crystal-chest table, Ring-of-wealth
     placeholder, GE row, Utilities selector, persistence, and review undo.
   - [x] Correct item reachability so authentic quest-start and quest-stage
     inventory grants seed the graph; prove Lost City's Dramen branch activates
     the existing Cinnamon route.
   - [x] Finish Ranging Guild closure. Full Qt found two stale Activities
     inventory assertions. The corrected suite passes 4,053 tests. All final
     quality gates pass.
   - [x] Close and re-land Wyvern-bones acquisition through the level-72
     Skeletal Wyvern Combat row. Preserve item IDs 6812, 6816, and 6810, reuse
     the sixteen existing downstream actions, register the four hidden breath
     values, and prove the full kill-to-Ectofuntus route through the real kernel.
   - [x] Add the six non-gilded Prayer altar rows as separate depth work.
     Construction already modeled all seven altar objects; the gap was that
     owned-mode Prayer always required the gilded altar at 250%. Owned mode now
     reads the highest chapel altar built (Darkan BoneAltar.java bases Oak 1.0
     through Gilded 2.5) and adds +50% per lit burner, so each of the six
     non-gilded tiers is a reachable owned Prayer rate.
   - [x] Close the Ectofuntus bone family through eight acquisition routes,
     exact bonemeal identities, the corrected Zogre Prayer XP, and one registered
     Ogre coffin selector placeholder.
   - [x] Re-land the five grimy vine-herb families through sourced Jadinko seed
     acquisition, runnable Farming crops, corrected clean levels, unfinished
     potions, and Darkan-sourced vine-herb base lives.
   - [x] Fix the one-way skill-button availability refresh in a separate slice.
     `ui/ui.py:1467-1470` enables a button when the pure result is true, but it
     does not disable the button when the result becomes false. The same pattern
     exists on neighbouring skill buttons. This defect is pre-existing.
   - [ ] Recover the Frost dragon bone ID-to-route mapping. No period source maps
     item `18830` and item `18832` one-to-one to the Asgarnian Ice Dungeon and
     Daemonheim routes. Preserve both IDs until a period source settles the pair.
5. [x] The paused goal is resumed and its blocker is repaired.
   The owner set a new goal on 2026-08-30. It makes an another-writer collision
   on canonical `main` this seat's repair work rather than a stop condition.
   Commit `324066da` adopts the verified asset-cutoff audit re-run, commit
   `732643e7` lands the previous session's records, and
   `memory-bank/GOAL-BLOCKED.md` is deleted.
6. [x] The prior papercut branches are reconciled against main.
   `63a3409c` and `b861cdec` are ancestors of main. The reachability-check
   branch's original `8f1092db` was re-created as `aa173479` and merged through
   `9d2b8d97`; none of these three remains eligible unmerged work.
7. [ ] Execute `memory-bank/goal-priority-matrix.md` under the resumed goal.
   - [x] Build the stored priority matrix from current queues and owner rulings.
   - [ ] Complete the first owner-ordered unit: dispatcher state-object
     restructure (§57/58), with all required verification and native review.
   - [x] Re-audit eligible work and preserved candidates after each promotion.
     Re-audited 2026-09-16 after three landings: documentation-gate repair
     `c4ebd277`, Bar Crawl `3a14d435`, Union Alpha trial scores `a243a62a`.
     Next eligible: cape and cut-gem tradeability, which need a rebase onto
     current main, regenerated surface pins, and a repair to the cape test
     that writes the retired `addon.player_data` attribute.
