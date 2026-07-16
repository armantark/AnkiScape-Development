# Active Context

## Current Focus

Agility's owner grill and full-content design harvest are closed; implementation
belongs in a new thread. The governing product contract is
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
period consequences always override it. Brimhaven remains the flattened hidden
5x5/eight-review chase in `agility-brimhaven-contract-2026-07-15.md`; the only
ratification is Karamja gloves 4's sourced 25% chance to add a second ticket on
a qualifying tag. Wall-clock time and global player-location state are forbidden
throughout. No Agility implementation was authorized or performed in this
design thread.

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

- `skill_registry.py` has 16 complete skill surfaces, five partial Combat-trained skills, and four planned skills.
- Complete: Mining, Woodcutting, Farming, Fishing, Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Hunter, Herblore, Prayer, Magic, Construction, and Thieving.
- Partial through unified Combat: Attack, Strength, Defence, Constitution, and Ranged.
- Planned: Summoning, Agility, Dungeoneering, and Slayer.
- Farming is shipped (`9a88c56`), not the next build.
- The 194-row quest catalog remains coverage scaffolding rather than full quest parity.
- NPC Shops are live; the fake GE remains parked until the item/acquisition universe is representative.
- The current reachability audit reports 1,102 actions, 725 consumed items, and 296 orphan inputs (151 root, 145 cascade). These are acquisition-program signals, not Prayer closure failures.

## Most Recent Completed Work

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

1. Resume the canonical Kanban rather than reopening Prayer or Thieving: take the next owner-selected missing-skill program.
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
