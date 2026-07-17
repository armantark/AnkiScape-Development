# Active Context

## Current Focus

Summoning's complete owner grill is now active on `codex/summoning-grill`; no
runtime implementation has started. The governing live ledger is
`summoning-skill-contract-2026-07-16.md`, backed first by
`source-audits/summoning-familiar-lifecycle-2026-07-16.md`. The first genuine
fork is closed: every answered card spends familiar lifetime, including Again.
Again is now formally an idle/world tick with no foreground action; the broader
contract and current-system audit are in `simulation-time-boundary-2026-07-16.md`.
The active-encounter fork is also closed: Again is a world-only idle tick,
analogous to briefly clicking outside the mob area, so enemies and foreground
commands do not act while genuinely passive effects may still resolve. Renewal is
source/app-pattern resolved as a manual command plus target-policy automation that
only consumes a deliberately carried matching pouch on successful answers. BoB
cargo expiry is now a distinct
grave-like five-source-minute reclaim event; unclaimed cargo is destroyed. Both
ordinary graves and cargo events project as distinct icons in the reusable alert
strip above the reviewer XP HUD; see
`review-hud-world-alerts-contract-2026-07-16.md`. BoB storage remains a distinct
restricted inventory because flattening it would make expiry cargo arbitrary and
erase period restrictions. The familiar is one global Equipment entity with
synchronized Bank, reviewer, and target projections; target-local policy chooses
`Off`, Casual best-available by source role, or an exact Advanced familiar without
silently replacing a live familiar on target switches. Selecting a BoB is Casual's
opt-in to automatic target-preset packing of its separate inventory, while Advanced
exposes the exact slots. Casual point upkeep is also settled: when a familiar
policy lacks the Summoning points it needs, the next successful answer becomes the
unified `Visiting altar+obelisk` action instead of the selected target action, fully
restoring ordinary Prayer and Summoning points; Again never restores. Existing combat
Bank runs coalesce their free altar stop with the obelisk without spending another
review. Casual auto-special is settled on by default: it fires only on
successful answers under source-role triggers and consumes only a deliberately
carried matching scroll plus special-move points, never Bank stock. Passive familiar
effects now follow the owner's AFK boundary: every answered card, including Again,
may advance and resolve genuinely passive forage or healing, while attacks and
commands still require their foreground/encounter conditions. Period evidence
already rules out collapsing lifetime and Summoning points into one resource:
points could reach zero without dismissing the familiar. Wall-clock gameplay
remains forbidden. Familiar combat exposure is now source-gated: attacking alone
does not make a familiar targetable, and silence means zero familiar damage rather
than an invented fallback roll. Only pinned retaliation, area, enemy, or explicit
aggro/tanking mechanics can reach familiar LP. Enabled familiar policy now means
automatic maintenance: on the next successful answer after renewal, death, or expiry
needs a pouch, an atomic transaction consumes only a compatible carried pouch plus
Summoning points and may resummon mid-encounter. Advanced may reserve multiple exact
pouch slots; Bank stock is never consumed directly. Missing resources leave the policy
enabled but visibly lapsed until they return. Carried-pouch depletion now triggers an
automatic one-review Bank detour when the enabled policy can refill from owned stock;
the detour replaces the target action and may complete the resummon atomically. A
mismatched live familiar is now safely swapped at the next Bank boundary only after BoB
cargo is deposited and replacement success is guaranteed; otherwise the old familiar
remains active and the new policy stays queued. Period evidence has now corrected the
forbidden-area model: most such targets block until dismissal, while only an explicit small
set temporarily hides and later returns the familiar. The target catalog will encode that
per-area consequence. Starting a blocked target with a live familiar now opens a destructive
confirmation naming remaining duration, permanent pouch loss, and any BoB cargo reclaim;
Cancel preserves the current training, while Confirm dismisses without a review or remote
Bank deposit. The next open fork is whether a general manual Dismiss also disables an
enabled target auto-maintenance policy or allows it to resummon on the next successful
answer. Familiarisation is now a
four-answer session with 15 shards per success, three focus pips, and one lost pip/no
shards on Again. Target policy
`Off — no familiar automation` now preserves any already-live global familiar while
spending no further familiar resources. Casual already falls back
automatically within its selected role when the best pouch runs out, but newly restocked
stronger pouches never interrupt a live fallback; re-resolution waits for renewal,
expiry, death, or a manual switch. BoB combat access is source-resolved: consecutive
successful bursts cannot withdraw, while an Again disengages and permits a preset top-up
before the next successful re-engagement. Advanced remains exact. The
cross-product help architecture is owner-settled in
`help-system-contract-2026-07-16.md`: one offline searchable corpus feeds both the
full Help Center and contextual page-level `?` entries.

Familiarisation period mechanics and the delegated translation are pinned in
`source-audits/summoning-familiarisation-2026-07-16.md`: once weekly, random familiar
projection, raw-shard gathering under focus pressure, a 60-shard cap, and the choice of a
shard-scaled ingredient box or 40-seconds-per-shard triple eligible charm drops. Four
answered cards represent the run; it begins with three focus pips, grants 15 shards per
success, and Again loses a pip without gathering. No wall-clock or location state is
introduced.

Ordinary Summoning training is source/app-pattern resolved in
`source-audits/summoning-training-2026-07-16.md`: searchable **Infuse pouches** and
**Create scrolls** families process one exact source unit per successful review, while the
ordinary carried-pack/Bank-run model supplies repeated trips. Wolf Whistle is optional,
and surface-world training excludes the separately sourced Dungeoneering pouch and scroll
tables. Exact row and acquisition harvesting remains implementation-prep work, not an owner
fork.

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

1. Continue the Summoning owner grill one genuine product fork at a time; implementation remains a later thread.
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
