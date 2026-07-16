# Active Context

## Current Focus

The overnight fresh-eyes audit on `codex/overnight-fresh-eyes-2026-07-16`
has completed seven attributable passes. Pass 7 corrected Anki's production
bridge-filter contract, serialized deferred menu opens, replaced duplicate
profile menus, released closed modal widget trees, and removed the unsupported
`DeckBrowserContent.links` path plus its fabricated tests. Commit `09aacc2`
passes 91 focused tests, an 86-test real-Qt lifecycle/integration rerun, and the
1,273-test full suite with zero hard test-quality issues. The worktree guard
remains clean. The next pass targets registries, assets, reachability, and
remaining test-oracle integrity seams.

Agility's owner grill, source harvest, and atomic implementation are closed. The
governing product contract is
`agility-skill-contract-2026-07-15.md`, backed by the exhaustive design-family ledger
`source-audits/agility-complete-content-inventory-2026-07-15.md`. A
closed design family is not a closed historical value: candidate and
`source_blocked` rows still require the source-verification sweep named there. A
`source_blocked` value may trigger one final implementation-time search or the
smallest labeled review-native abstraction, but may never erase a period
feature. The complete design includes every audited course plus the previously
omitted Bandos route, Werewolf Skullball, Gnome Ball, Flash Powder Factory, The
Pit, Circus, incidental actions, the full ordinary/grapple shortcut registries,
cross-skill benefits, rewards/equipment/boosts, pending quest XP activation,
and target-specific run energy/actual-load weight.

Course failure consequences remain obstacle-specific rather than universal;
the contract now closes the fallback for unresolved hidden rolls at one global
20% entry chance decaying to a sourced mastery point or 5% at level 99. Existing
period consequences always override it. Brimhaven ships as the flattened hidden
5x5/eight-review chase in `agility-brimhaven-contract-2026-07-15.md`; Karamja
gloves 4 retain their sourced 25% chance to add a second ticket on a qualifying
tag. Wall-clock time and global player-location state remain forbidden
throughout. The implementation and verification record live in
`source-audits/agility-implementation-verification-2026-07-15.md`.

Cadence Phase 3 shadow observation is complete on
`codex/cadence-phase3-shadow`, based on Phase 1 at `b45aff0`. With the strict
off-by-default `ankiscape_cadence_kernel` flag enabled, Mining, Woodcutting,
Fishing, Hunter, Cooking, and Firemaking now record the kernel proposal beside
the unchanged live result. The observer covers all 175 runtime routes: 24 have
compatible pre-cutoff rates and 151 fail closed as `source_blocked`. Fixed-seed
end-to-end tests prove identical per-review gameplay bytes, XP, loot, call
sequence, and RNG state with the flag on or off; only the dedicated
`player_data["cadence_shadow"]` instrumentation namespace differs.

Phase 1 of the cadence kernel is committed on `main` at `b45aff0`.
`cadence_kernel.py` owns the pure `R = 1000` contract, exact residual
scheduling, admission/overflow declarations, and lock shapes. Storage config v34
adds only the empty route-keyed `cadence_profiles` state;
`ankiscape_cadence_kernel` is strict, off by default, and not read by review
dispatch. No skill is routed through the kernel for live mutation. The Phase 3
branch runs 1,219 tests with 187 non-Qt skips and three expected failures.

The test-signal cleanup is merged into `main` at `526f9c2`. It removed
low-signal structural tests, converted the previously uncollected pytest-style
JavaScript bridge checks to `unittest`, and added the durable quality contract
in `memory-bank/test-quality-standard.md`. The audit now collects 1,215 tests
across 65 files with zero hard issues; its five clone groups are advisory.

The Prayer/altar/urn/passive/Herblore closure is implemented, fully certified, and committed on `main` at `300c7c5`. It extends the original Prayer ship with owned gilded-altar parity, all 26 pre-EOC training-urn tiers across six skills, target-carried Bonecrusher/Ectoplasmator behavior, direct full-urn teleport with an independent bounded Anki undo stack, exact high-tier standard-Prayer Defence gates, and distinct Bonemeal/Wyvern bonemeal storage identities.

Use these as the live handoff sources:

1. `memory-bank/cadence-kernel-phase3-shadow-2026-07-13.md` — Phase 3 decisions, route coverage, verification, and manual QA.
2. `memory-bank/status-updates/cadence-kernel-phase3-shadow-plan-2026-07-13.html` — immutable pre-implementation proposal.
3. `memory-bank/status-updates/cadence-kernel-phase3-shadow-results-2026-07-13.html` — final divergence and verification handoff.
4. `memory-bank/future-work-kanban.md` — canonical forward-work board.
5. `memory-bank/pre-eoc-source-verification-standard.md` — permanent evidence contract.

The dated `completion-audit-2026-07-10.*` files remain historical snapshots; live registry and Kanban state outrank them.

## Current Truth

- `skill_registry.py` has 17 complete skill surfaces, five partial Combat-trained skills, and three planned skills.
- Complete: Mining, Woodcutting, Farming, Fishing, Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Hunter, Herblore, Prayer, Magic, Construction, Thieving, and Agility.
- Partial through unified Combat: Attack, Strength, Defence, Constitution, and Ranged.
- Planned: Summoning, Dungeoneering, and Slayer.
- Farming is shipped (`9a88c56`), not the next build.
- The 194-row quest catalog remains coverage scaffolding rather than full quest parity.
- NPC Shops are live; the fake GE remains parked until the item/acquisition universe is representative.
- The current reachability audit reports 1,106 actions, 727 consumed items, and
  278 orphan inputs (115 root, 163 cascade). Bob Barter's quantity-free decant
  routes turn the former four-dose potion roots into known-producer cascades;
  their remaining availability follows upstream herb and secondary acquisition.
  These are acquisition-program signals rather than Agility closure failures.

## Most Recent Completed Work

- Bob Barter (herbs) is a free, instantaneous Grand Exchange shop service. One
  click redistributes every eligible live non-Daemonheim vial-potion family to
  the selected period-supported 2-, 3-, or 4-dose size. Total doses and vial
  containers are conserved: a partial remainder is retained, splitting consumes
  owned empty vials, and consolidation returns excess vials. The action changes
  no review or clock state and records an independently undoable shop event.
- Anki was loading three linked worktrees beside the canonical checkout because
  all four lived directly under `addons21` as enabled packages. The linked
  worktrees now live under the sibling `Anki2/ankiscape_worktrees/` root, and
  `tools/worktree_guard.py` audits that runtime boundary and creates future
  worktrees only in the safe location.
- The deck-browser entry point replaces its own nested callbacks by stable hook
  key through Anki's production `_hooks` storage, so repeated registration or a
  reload leaves exactly one callback and one menu open per click.
- Ordinary Herblore now excludes the 54 Daemonheim-only clean, unfinished, and finished targets while preserving their item identities for old saves. A removed saved selection migrates to `clean_guam` without deleting inventory.
- The live Herblore catalog is 22 clean, 22 unfinished, and 69 finished targets.
  All 113 rows now use local RS3-provenanced artwork. The skill rail uses the
  compact OSRS `Herblore icon (detail).png`, matching the source/style family of
  the other skill icons instead of the modern RS3 `Herblore detail.png` art.

- The six Phase 3 adapters observe through the existing central action-telemetry seam exactly once per started action. They never supply an outcome to live gameplay.
- Gathering adapters advance independent exact low/high source envelopes. Cooking and Firemaking compare the already-drawn live roll to the authentic source probability and draw no second random value.
- Source ranges remain ranges; no midpoint is invented. Explicit `cap_one_action` overflow metadata covers Mining iron and the five embedded Cooking/Firemaking routes.
- Shadow residuals and aggregates sanitize without floats, round-trip through save/load, and roll back atomically with the review snapshot. A missing optional observer import cannot prevent a previously enabled save from loading after the flag is disabled.
- The catalog reporter lists current, proposed, and pinned 2012 XP/hour for every in-scope route. Ordinary gold, runite, mixed leaping fish, rocktail urn-inclusive data, and all other incompatible/missing rows remain visibly `source_blocked`.
- Prayer selection is atomic across material and method. Hosted/owned altar state is cleared only when that composite selection changes.
- Owned gilded altars accept zero, one, or two burners at 250%, 300%, or 350%; clean marrentill is consumed once per new stint and the multiplier remains frozen for that stint.
- Training urns use exact five-state physical identities, non-stackable semantics, target-carried activation, overflow-preserving charge, ten-nonempty caps, and direct full-urn teleport.
- Saved custom layouts follow a physical urn through `(r)` to active to full, so skilling and Combat bank runs do not strand a charging urn.
- Direct teleport awards the urn skill's XP, refreshes the visible Skills panel, persists immediately, and uses a separate LIFO custom undo rather than review undo.
- Bonecrusher and Ectoplasmator operate only from the selected target's carried pack; Bonecrusher also intercepts Hunter bone outputs. No acquisition route was invented.
- Chivalry, Rigour, Augury, and Piety enforce their exact Defence requirements; Knight Waves locks are visible in the Qt copy.
- Ordinary Bonemeal (source ID 4255) and Wyvern bonemeal (source ID 6810) remain distinct despite sharing a source display name. Super prayer consumes only the disambiguated Wyvern storage key.
- Bonecrusher and Ectoplasmator icons now use explicit RS3 wiki provenance instead of the fallback OSRS-first resolver.

## Decision Boundaries

- Cadence Phase 1 is architecture only: do not route a skill until its later
  migration phase, and preserve the off-path byte/RNG identity test.
- Cadence residuals are integer-only per route. Inactive routes freeze, and the
  whole `cadence_profiles` mapping rides the existing review snapshot/undo path.
- Phase 3 is observation only. `cadence_shadow` is transactional instrumentation,
  separate from dormant live `cadence_profiles`; enabling it may add observer
  bytes, but cannot change gameplay state, XP, loot, calls, or RNG.
- Missing or semantically incompatible rates always remain `source_blocked`.
  Do not substitute modern rates, midpoint a range, decompose the rocktail urn
  quote, map ordinary gold to concentrated gold, or map mixed leaping fish to a
  sturgeon-only rate.
- Full pre-EOC cutoff: `2012-11-20`.
- Do not re-grill Prayer, Magic, Construction, or Farming; their contracts are closed and implemented.
- Do not collapse source IDs 4255 and 6810 into one storage key. The earlier gap-ledger conclusion is superseded by the closure audit.
- Target-carried presence is the activation rule for urns and Prayer passives; bank ownership alone is inert.
- Review undo and direct-inventory-action undo are distinct contracts and must remain independent.
- Each wholly missing skill needs its own deep grill before implementation.
- Dungeoneering must define its temporary session inventory/equipment/reward boundary before any Daemonheim herbs or potions return to a player-facing catalog; see `dungeoneering-product-decision-deferred-2026-07-13.md`.
- Activities/minigames use Utility/Activities at the platform layer, but each family needs its own complete reward/state/source contract.
- Global level-1-to-99 balancing waits until all skills and major methods are present.

## Next Recommended Work

1. Resume the canonical Kanban rather than reopening Prayer, Thieving, or Agility: take the next owner-selected missing-skill program.
2. Close reachability roots only through authentic owning skills, activities, Combat drops, quests, shops, spawns, claims, and item actions.
3. When Darkan reaches a stable milestone, rerun parked hidden-server audits against that pinned source surface.

## Verification Contract

- Pure/data/unit/integration/end-to-end tests for behavior changes.
- Real offscreen `.venv-qt` tests for UI changes.
- Full `python3 run_tests.py` and full offscreen discovery before feature closure.
- `python3 tools/audit_item_reachability.py --json`, compilation, and `git diff --check` at closure.
- Manual real-profile QA remains an explicit owner checklist when a release candidate should touch the owner's Anki collection.
- Pre/post status artifacts for normal complex work.

## Thieving closure (2026-07-13)

Thieving is now a complete Support skill on `main`, merged at `63b0a28`. It ships the
full 2011Scape pickpocket and stall tables, exact inclusive integer rolls,
multi-pick, shared-LP damage plus one-review stun recovery, rational stall
cadence, wall safes, and the complete Menaphite lure/knockout/two-pick loop.
Fight-back starts an encounter-only Menaphite combat bridge; the default flee
path applies one sourced damage event through the shared auto-eat/death/grave
substrate. Wall safes use their distinct strict source roll and 20–60 LP trap;
all Thieving routes advance once per answered card regardless of the global
action multiplier. Desert Phoenix is a The Golem-gated, no-XP Utility activity
yielding Phoenix feather.

The owner resolved two implementation-time source questions: exact 2011Scape
respawn cadence wins rounded wiki rates, and player-visible period blackjack
values may use Darkan only for the missing hidden knockout roll/combat stats,
clearly labelled provisional. Dorgesh-Kaan chests, Lletya elf, Pirates' Hideout,
and incomplete blackjack variants remain source-blocked or parked. The durable
table record is `memory-bank/source-audits/thieving-tables-2026-07-13.md`.

Closure verification is green: Python 3.12 discovery and `run_tests.py` each
pass 1,240 tests with 188 non-Qt skips and three pre-existing expected failures;
the real Anki/Qt offscreen discovery passes all 1,240 tests with the same three
expected failures and no skips. The focused closure set passes 609 tests, item
reachability reports no Thieving/Phoenix orphan, compilation and diff checks are
clean, and the result artifact is
`memory-bank/status-updates/thieving-skill-results-2026-07-13.html`.

## Agility closure (2026-07-15)

Agility is now a complete Support skill. It ships the full course/action-stage
engine, obstacle-specific failure/LP/setback behavior, lap bonuses, every audited
activity family, Brimhaven's review-native ticket chase, 68 ordinary/grapple
shortcuts, run-energy trip costs with actual carried weight, equipment and boost
effects, achievements, command undo, a grouped Qt surface, and period-provenanced
assets. Circus and every other cadence boundary derive from answered cards or
Agility actions; a static regression guard rejects wall-clock imports from the
gameplay modules.

The release-blocking live integrations are active: barehand Hunter butterflies,
Fishing double catches, Herblore consumable effects, Habitat traversal, quest and
lamp rewards, Farming east-patch travel, LP/death, inventory, equipment, storage,
and runtime dispatch. Future-owner hooks remain explicit but inert for Summoning,
Slayer, Dungeoneering, full Blast Furnace, Livid Farm, diary acquisition,
Barbarian Assault, and quest-owned stages. Exact Dorgesh route identities are
registered; still-hidden payout differences remain `source_blocked` rather than
invented. See
`memory-bank/source-audits/agility-implementation-verification-2026-07-15.md`.

## Overnight fresh-eyes pass 3 (2026-07-16)

The safe worktree branch `codex/overnight-fresh-eyes-2026-07-16` now includes
the exact lantern-state closure at `37b46c5`. Bullseye, candle, oil-lamp,
oil-lantern, sapphire, emerald, and Mining helmet states remain distinct from
production through preparation, use, equipment, shops, quests, assets, and
save migration. Lamp-oil preparation is review-native and never wall-clock
driven. Verification passes 1,265 Python tests, 179 real offscreen Qt tests,
the zero-hard-issue test-quality audit, compilation, diff checks, and the safe
worktree audit; reachability improves by 14 cascade orphans.

The next confirmed implementation seam is the generated quest pseudo-item
`Light sources`, present in three exact quest gates. Fable is at the owner's
30% weekly cap; remaining overnight reviews use Opus after the Claude session
window resets.

## Overnight fresh-eyes pass 4 (2026-07-16)

Commit `83de7e1` removes the `Light source`/`Light sources` pseudo-item from the
live quest and Dorgesh-Kaan Agility surfaces. Eight source-placed quest gates
now accept the eleven reachable exact lit states; Tears of Guthix retains its
safe bullseye and sapphire-lantern sequence, while Watchtower and Another Slice
of H.A.M. remain honestly `source_blocked` instead of receiving guessed gates.
Temple of Ikov's visible requirements and the test oracles now describe the
same real identities as runtime.

Verification passes 253 focused tests and all 1,270 tests under the established
Homebrew Python, with 183 non-Qt skips and three expected XP-parity failures.
Test quality has zero hard issues; reachability remains 1,114 actions, 264
orphan inputs, and 149 cascade orphans. Fable remains at the 30% weekly cap;
the successful reviewer was one read-only Opus workflow.

The next confirmed seam is save migration symmetry: legacy lantern/Mining
helmet keys must be migrated in carried layouts and views, grave/Death's Office
items and loadouts, and loot overrides before carried-state clamping.

## Overnight fresh-eyes pass 5 (2026-07-16)

Commit `3953b64` closes persisted item-name symmetry for the exact lantern and
Mining helmet split. Migration now renames carried views/layouts, loot
preferences, grave and Death's Office items/loadouts, and the Magic alchemy
selector before any carried-state clamp can discard the old name. Reclaiming a
legacy Mining helmet restores `Mining helmet (unlit)` as real equipment instead
of occupying the head slot with an unregistered zero-stat phantom.

Verification passes 312 focused storage/combat/Magic/shop/integration tests and
all 1,272 tests, with 183 non-Qt skips and three expected XP-parity failures.
Test quality remains at zero hard issues, compilation and diff checks pass, and
the safe worktree audit remains clean. There is no queued confirmed defect;
the next pass rotates to quest, shop, activity, and achievement seams.

## Overnight fresh-eyes pass 8 (2026-07-16)

Commit `5ab5aee` repairs three registry and audit seams. Smithing achievements
now consume the canonical live bar identities; source item 4600 is consistently
the obtainable and equippable `Willow blackjack`; and the acquisition graph now
models Magic and Prayer outputs, rune costs, and dynamic bone alternatives.
This removes false elemental-orb and Wine-of-zamorak roots while surfacing real
downstream Prayer and Onyx acquisition debt that was previously invisible.

Verification passes 78 focused tests, 509 integration/end-to-end tests, eight
real offscreen Qt tests, and all 1,275 non-Qt tests with 185 skips and the three
expected XP-parity failures. The test-quality audit has zero hard issues;
compilation, diff, and worktree-safety checks pass. Reachability now covers
1,188 actions, with 270 orphan inputs: 110 root and 160 cascade.

## Overnight fresh-eyes pass 9 (2026-07-16)

Commit `ceaab20` closes two quest writer/reader failures. Live quest data now
always retains a completion sentinel after the highest requirement row, so the
final sourced objective executes for all 152 affected generated quests instead
of being marked complete without evaluation. Tears of Guthix now reaches and
enforces its lit sapphire-lantern stage. Seven obtainable quest equipment items
also receive their source-config equipment records, while Staff of armadyl is
correctly retained as a non-equipment quest material.

Verification passes 127 registry/shop/quest tests, 104 quest/runtime tests,
four real offscreen Qt checks, and all 1,280 non-Qt tests with 185 skips and the
three expected XP-parity failures. Test quality has zero hard issues;
reachability remains 1,188 actions and 270 orphan inputs (110 root, 160
cascade); compilation, diff, and safe-worktree checks pass.

## Overnight fresh-eyes pass 10 (2026-07-16)

Commit `916b075` closes six Combat state and consequence failures. Loaded Ranged
ammo now wins over banked lower tiers; Vengeance and Spellbook Swap use the
finite rune loadout and persist the state that crosses reviews; reflected kills
receive ordinary kill/drop treatment; Dream cannot interrupt an active fight;
same-review fatal loot enters the grave after filtering; and Protect Item keeps
the highest-value equipped item.

Verification passes 334 focused combat/runtime/integration tests, eight real
offscreen Qt checks, and all 1,286 tests under Homebrew Python with 185 skips
and the three expected XP-parity failures. Test quality has zero hard issues;
reachability remains 1,188 actions and 270 orphan inputs (110 root, 160
cascade); compilation, diff, and safe-worktree checks pass. The system Python
is 3.9 and cannot parse the repository's supported union-type syntax, so the
authoritative full run used the established Homebrew Python 3.14 interpreter.

## Overnight fresh-eyes pass 11 (2026-07-16)

Commit `9273cf4` closes ranged item identity seams across every live producer.
Standard arrows from H.A.M. pickpockets, Combat drops, and NPC shops now enter
the canonical plural ammunition stacks accepted by equipment and combat. Save
migration merges legacy singular stacks, including persisted shop events and
their inverse deltas, without losing quantities or breaking undo.

The checked-in equipment snapshot was also regenerated from its current source
generator. Twenty-nine live Crafting and Fletching outputs that were previously
craftable but rejected by the equipment engine are now equippable, and a new
generator/snapshot synchronization oracle prevents recurrence.

Verification passes 263 focused tests, five real offscreen Qt checks, and all
1,291 tests with 185 skips and three expected XP-parity failures. Test quality
has zero hard issues; reachability remains 1,188 actions and 270 orphan inputs
(110 root, 160 cascade); compilation, diff, and safe-worktree checks pass.

## Overnight fresh-eyes pass 12 (2026-07-16)

Commit `f794108` closes consumable and supply-pack state paths. Kebab now uses
live RNG with deterministic undo; all eight supply packs support exact Open and
Open all actions; Juju farming potion doses can be activated and conserved;
Magic essence potion creation emits the source-convergent mix identity; and
registry tradeability, food categories, potion-dose identities, assets, and
Bank verbs now agree with their runtime consumers.

Verification passes 19 focused tests, five real offscreen Qt checks, and all
1,302 tests with 186 skips and three expected XP-parity failures. Test quality
has zero hard issues; reachability now covers 1,200 actions with 273 orphan
inputs (110 root, 163 cascade); compilation, diff, and safe-worktree checks
pass.

## Overnight fresh-eyes pass 13 (2026-07-16)

Commit `1fb0b64` makes Combat presets configuration-only. The finite supply
loadout is no longer captured by new presets or restored from legacy preset
payloads, so a target pin cannot refill consumed food, ammunition, runes, or
potions for free or erase a newly loaded pack on the following review.

Verification passes 271 focused runtime/integration tests, two real offscreen
Qt checks, and all 1,303 tests with 186 skips and three expected XP-parity
failures. Test quality has zero hard issues; reachability remains 1,200 actions
and 273 orphan inputs (110 root, 163 cascade); compilation, diff, and
safe-worktree checks pass.

## Overnight fresh-eyes pass 14 (2026-07-16)

Commit `b59c846` makes achievement dispatch dependency-aware. When the final
ordinary achievement and Living Legend become true on the same action, the
dispatcher now evaluates to a fixed point and returns both completions
atomically rather than making Living Legend wait for another unrelated action.

Verification passes 251 focused pure/integration tests, one real offscreen Qt
achievement-surface check, and all 1,304 tests with 186 skips and three
expected XP-parity failures. Test quality has zero hard issues; compilation,
diff, and safe-worktree checks pass.

## Overnight fresh-eyes pass 15 (2026-07-16)

Commit `1120fb4` closes two production paths that green lower-level tests did
not exercise. Every Shop purchase, sale, service, vendor action, Bob Barter
decant, and Wilderness consequence now persists through `save_player_data`
immediately. The Farming sheet also exposes the accepted Juju farming potion
action, uses the fullest owned dose first, and displays its review-native active
state instead of leaving the backend-only action unreachable.

Verification passes 242 focused Farming/Shop/runtime/integration tests, all 183
real offscreen Qt tests, and all 1,305 core tests with 187 skips and three
expected XP-parity failures. Test quality has zero hard issues; compilation,
diff, and safe-worktree checks pass.

## Overnight fresh-eyes pass 16 (2026-07-16)

Commit `483eb55` closes reactive UI and target-resolution gaps across the six
newest skill surfaces. The HUD resolves their friendly target names; equipped
blackjacks satisfy Thieving gates; Magic, Construction, Thieving, and Agility
controls rerender their dependent readiness state; every sourced Brimhaven XP
bundle is selectable; Agility commands report outcomes; and paid Brimhaven
stints end on target change or Stop Training.

Verification passes 170 focused core tests, eight real offscreen Qt checks,
and all 1,312 core tests with 193 skips and three expected XP-parity failures.
Test quality has zero hard issues; compilation, diff, and safe-worktree checks
pass.

## Overnight fresh-eyes pass 17 (2026-07-16)

Commit `111b280` closes consequence-ordering and undo gaps on management
actions. XP-lamp claims update the funded skill's level before achievements,
quest-bank and Stronghold rewards participate in direct-action undo, and Shop
mutations reevaluate inventory achievements before saving.

Verification passes 109 focused core tests and nine real offscreen Qt Shop
checks. Test quality has zero hard issues; compilation, diff, and safe-worktree
checks pass. Full closure verification remains pending.

## Overnight fresh-eyes pass 18 (2026-07-16)

Commit `91f0b35` closes the remaining reproduced Combat-management consequence
gaps. Clearing the finite loadout immediately repaints returned bank items, and
both unload and Death's Office reclaim evaluate inventory achievements before
saving. The reviewer-proposed manual Refill button was rejected because the
current UI contract deliberately uses automatic safe-boundary refill.

Verification passes 252 focused core tests and the combat-filtered real
offscreen Qt surface. Test quality has zero hard issues; compilation, diff, and
safe-worktree checks pass. Full closure verification remains pending.
