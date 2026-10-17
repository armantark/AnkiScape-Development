# AnkiScape Completion Kanban

Status: reconciled 2026-07-16. This is the product-wide parity and depth backlog; selection is in [the goal priority matrix](goal-priority-matrix.md). The 2026-07-10 completion audit is archived baseline evidence; `memory-bank/gap-backlog.json` is the closed historical record of the shipped-skill subledger; the parity ledger below owns its open rows.

Shipped cards older than 30 days rotate monthly into [the shipped-card archive](archive/kanban-shipped-2026.md).

## Label contract

- `DEEP GRILL`: owner-facing loop/UI/abstraction decisions remain.
- `SOURCE AUDIT`: design is settled, but pre-cutoff mechanics or values are incomplete/conflicting.
- `WAIT: DARKAN`: a stable high-fidelity restoration would materially reduce hidden-server guesswork; historical reconciliation still applies.
- `IMPLEMENT`: design and evidence are sufficient for a bounded backend/frontend/assets/tests slice.
- `DEPENDENCY`: another skill, activity, acquisition route, or economy surface must land first.
- `PARKED`: deliberately sequenced later, not forgotten.
- `EXCLUDED`: outside the product/cutoff boundary.

## Now — audit-backed implementation and source work

Current goal selection, next action and branch disposition:
`memory-bank/goal-priority-matrix.md`. Existing UI changes are excluded by this goal.

### README FAQ — shipped and closed 2026-10-15

The owner wrote the FAQ, and it sits in `README.md` after "What you get"
(commit `62beff7d`). Its facts were checked against the code on 2026-10-15.
Still unverified, so the FAQ makes no claim about it: which save wins when two
desktops play before an AnkiWeb sync.

### Upstream ideas from AnkiScape 3.0 — 2026-09-19

Labels: `IMPLEMENT` for the first four, `PARKED` for the rest. Owner accepted
this list on 2026-09-19 ("Alright fair enough"). Source: Wilson Yeh's
`https://github.com/wilsonhyeh/ankiscape`, cloned at `1e99e017`-era HEAD on
2026-09-19 (last upstream push 2026-09-19T21:03:08Z, 3.0.0 release prep).
Upstream is a six-skill game with hosted accounts, sync, and hiscores; its
gameplay is far behind this fork, its engineering around gameplay is not.

Take, in value order:

- Mobile catch-up from the review log. Upstream `evolved/catchup.py` scans
  Anki's `revlog` for uncredited eligible reviews (including AnkiMobile and
  AnkiDroid rows synced to desktop), awards them on the next profile load,
  and keeps a persisted frontier id so the scan is incremental (fast path
  chunk 2,000 rows; full reconciliation cap 20,000 rows, newest first). This
  fork credits live desktop reviews only; `grep -rl revlog` over
  `__init__.py core runtime logic ui` returns 0 files.
- Game save outside Anki's tables. Upstream `evolved/journal.py` keeps an
  add-on-owned SQLite at `<profile>/ankiscape-evolved/<game_uuid>/game.sqlite3`
  (WAL, 25 ms interactive busy budget, fail fast to a recovery notice). This
  fork stores the save in collection config under `ankiscape_player_data`,
  the same key the original add-on uses, so both add-ons installed together
  share one save. Upstream ships 3.0.0 under the same AnkiWeb listing
  `1808450369`, which makes that collision likely for any player who tries
  both. Moving the save off that key is the fix and is the same work.
- Export and restore of the game save. Upstream has Settings -> Export/Restore
  Game Backup. This fork has none (`grep -rn "def export\|def restore\|def
  backup"` over runtime code finds only unrelated helpers).
- Redo restores what undo retracted. This fork undoes review rewards and
  does not restore them on redo (`grep -rli redo` returns 0 files).

Specs (2026-09-25): [review-log catch-up](specs/review-log-catch-up.md),
[export and restore](specs/save-export-restore.md), and
[redo](specs/review-redo.md); each waits on its owner questions.

Check, then close or fix:

- One dialog for a multi-level gain. Upstream fixed a nineteen-dialog burst
  on 2026-09-19 (`fix(classic): summarise a multi-level gain in one dialog`).
  Confirm `level_up_check` (`__init__.py:615`) and the core check behave the
  same after a large XP change. Fixed 2026-09-25: the runtime check only
  delegates to the core one, which showed one popup per level (the Elder Kiln
  100,000 XP lamp on level-1 Attack showed 48); it now shows one popup naming
  the old and new level and still logs every level.

Release hygiene to copy when the AnkiWeb gates open:

- `docs/ASSET-RIGHTS.md`: cites Jagex Fan Content Policy v1.3 sections 6.1.3,
  8.1, and 14.1 (checked 2026-09-10 upstream) and records that Wiki
  permission does not license redistribution inside an add-on. This fork's
  release record names the rights problem but has not read the policy against
  the shipped art.
- `docs/release/3.0.0/KNOWN-LIMITATIONS.md`, `ROLLBACK.md`, and
  `RELEASE-SMOKE.md` (real-Anki journeys on the packaged `.ankiaddon`, never
  a source symlink). This fork has the release record only.
- A guide generated from the shipped rules data so tables cannot drift. This
  fork's `help_topics/` (20 files) is hand-written.

Do not take: hosted accounts, cloud sync, public hiscores (Supabase Free
tier, pauses when idle, email and password flow, most of upstream's
September went to its CI and server work); fresh-start-with-no-transfer and
two-games-per-profile, which exist only to keep that leaderboard fair.

### Tool belt source gaps — 2026-10-01

Label: `SOURCE AUDIT`. From rulings 4.29.3 and 4.29.4; `core/tool_belt.py`
holds both lists.

- Unholy mould: no pre-cutoff source settles whether a new 2012 belt held it
  (https://runescape.wiki/w/Unholy_mould?oldid=6088663 says only that it "can
  be stored in your toolbelt"). It is a default belt tool today; move it to
  `ADDABLE_TOOL_BELT_TOOLS` if a source shows it had to be added.
- In Aid of the Myreque stage 1 and A Fairy Tale I stage 3 dig with a spade,
  and no pre-cutoff source says whether the belt spade works. Both accept the
  belt spade today; add them to `QUEST_STAGES_NEEDING_HELD_TOOLS` if a source
  says it does not.

### Pass 16 follow-ups — 2026-10-15

Sources and oldids: `memory-bank/specs/pass16-owner-notes/spec.md`, Out of Scope.

- `PARKED` One-off item uses, owner's example a water jug; >28 manual uses in
  one card "should drag it out". Bulk work such as burying stays on targets.
- `PARKED` An action queue, so a run out of resources does not end in Bankstanding.
- `IMPLEMENT` 12 missing 2012 quest choice rewards (owner approved 2026-10-15);
  the catalog parser drops choice XP not worded as a lamp.
- `IMPLEMENT` Waterbirth Island snape grass, gated on The Fremennik Trials.
- `SOURCE AUDIT` Slayer families gated on Priest in Peril for Morytania access.

### Pass 14 follow-up — 2026-09-13

Label: `IMPLEMENT`. Owner parked it: "throw it on the longer-term kanban".

- Main menu open time from the review screen. Facts (fact-finder 2026-09-13):
  a new `QDialog` per open (`ui/ui.py:4899-4904`); Skills, Grand Exchange,
  Equipment, Stats, Settings build at open (`ui/ui.py:23400-23402`); the Bank
  widget tree also builds at open and only attaches behind a placeholder
  (`ui/ui.py:24770-24781,27095-27108`); Shop, Quests, Challenges, Achievements,
  Collections are truly deferred. Last measurement about 1.2 s per open on a
  real save (`66be9ee8:memory-bank/systemPatterns.md:944-971`); no profiler in `tools/`.
  Target: under 300 ms click-to-visible on the owner's save, measured before
  and after with a profiling script against a copy of the save. Keep the
  fresh-dialog-per-open design; defer every tab including Bank.

### Pass 13 follow-ups — 2026-09-04

Labels: `SOURCE AUDIT` for the first two, `IMPLEMENT` for the rest.

- Quest combat stats: 91 of 293 encounters across 47 quests carry none and
  report "This fight is not modelled yet (combat stats missing)"; list in
  `memory-bank/pass13-running-notes-2026-09-03.md` (02:18).
- Tradeable defaults: 106 items are `tradeable=False` while the 2011 cache
  flags them exchangeable (69 summoning pouches, 37 shop clothing and misc);
  root cause `MiningBonusItem.tradeable` default at `data/mining_data.py:98`.
- Icon second sweep: RS-wiki entries whose title is a dated historical image
  (Iron scimitar "(September 2009)") or whose revision is not the newest before
  2012-11-20; `tools/fetch_2012_icons.py` is the tool.
- Quest boss as the HUD current target during a quest fight
  (`ui/ui.py:1557-1574`).
- Open owner patch feedback under §58: judge the region compromises in
  `varrock_hard_but_it_won_t_warp_you_anywhere` and
  `morytania_medium_izzy_wizzy_let_s_get_lizzy`. Apply corrections as ledger-row
  patches plus regeneration per §4.22.3; Gate 2 remains passed.

### Diary curation ledger — wiring and deed text shipped; planned dependencies remain

Labels: `DEPENDENCY` for the remaining planned-system rows. The original
320-row curation ledger is wired for its live dispositions. Pass 13 and §4.26
landed the translated/invented text and selectable-instruction corrections;
`diary-curation-ledger/README.md` is the current census and trigger contract.

- Owner-ruled 2026-08-26 (design-thread-queue §4.21 ruling 1, §5.21): every
  diary row becomes a designed achievement; no dead-end triggers; dormant
  rows carry their designed trigger in the ledger. Full spec in the Pass 12
  brief, slice S1 stage 1. Pass 12 ships only the honest-stop cut.
- Wiring blocker from the 2026-08-27 cross-lineage review:
  `tools/generate_achievement_diary_data.py::_SKILL_TYPE_IDS` rotates source
  skill types 17, 18, and 19 across Firemaking, Woodcutting, and Fletching. The
  mapping was repaired on 2026-08-30 in branch
  `goal/diary-skill-rotation-2026-08-30` and is no longer a wiring blocker.
  Gate 2 passed by §4.22 ruling 3 on 2026-08-31: the row-by-row cross-lineage
  review verifies spec-conformance. Row 135 uses the closer equipped-item
  interpretation; an owner correction is a patch, not a new approval gate.

### Existing-skill parity ledger

Labels: `SOURCE AUDIT`, then `IMPLEMENT` only when evidence closes.

- `memory-bank/gap-backlog.json` is a closed historical record, last changed 2026-08-28: 45 rows, 24 `merged`. Do not add rows, reconstruct merged cards, or re-grill settled branches.
- The 21 rows that do not say `merged` belong to these cards (2026-10-01 sweep): this ledger owns `hunter-tracking-pitfall-snare`, `hunter-grenwall-herb-table`, `fm-bonfires`, `wc-arctic-euc-cursed`, and the three cards below; Large special methods and activities owns `hunter-habitat-jadinko`, `rc-runespan`, `smith-artisan-burial`, `smith-blastfurnace-goldsmith`, `rc-zmi-gop-wickedhood`, `mine-lrc-stars`, and `fm-pyres-beacons`; Dungeoneering depth owns the Daemonheim fish left by `fish-trawler-flingers`; Explicitly excluded owns `fletch-javelin-construction` and `wc-canoe-shaping`. `cook-karambwan-family`, `artisan-skill-potion-runtime`, and `cook-cooking-gauntlets-runtime` are live and need no card.
- `SOURCE AUDIT` Runecrafting route selection and the Abyss (`rc-method-selection`, `rc-abyss`): owner ruling 2026-07-14 makes each Runecrafting method or route a player-selectable target once unlocked, with the Abyss as the fast, dangerous route to the rift ring. The design is settled; the Abyss-versus-foot throughput delta has no period rate and stays `source_blocked`.
- `SOURCE AUDIT` Herblore remainder after Overload (`herb-overload-sanfew`): Overload mixing is live; Sanfew serum stages, weapon poison+ and ++ application, and combat potion effects still need pinned pre-EOC values and a runtime owner.
- `DEPENDENCY` Barbarian Firemaking bow lighting (`fm-barbarian-bow-lighting`): the bow-on-log target behavior is settled from pinned oldid 6476330; the permanent learned flag belongs to the future Barbarian Training miniquest or activity pass.
- Grenwall's pinned period revision proves its broad reward family but not exact spike/herb probabilities; it now explicitly waits on literal period evidence or a stable reconciled Darkan milestone (`memory-bank/source-audits/grenwall-reward-source-closure-2026-07-11.md`).
- Hunter tracking, pitfalls, and rabbit snaring were re-audited after Darkan's
  July 2026 restoration. The restoration is a deterministic ceiling rather
  than the source-grade roll model the settled contract requires: Penguin
  tracking, catch curves, pitfall damage, snare/Ferret loss, and authentic
  perfect/tatty selection remain absent. The period record closes visible
  values plus approximately `1/4` perfect fur and Jim's `+2` XP, but no partial
  deterministic targets ship. The fully sourced isolated Long kebbit reward
  chain is now live through both Chisel/Fletching and Leon's Shop service;
  its spike acquisition remains blocked with Razor-backed tracking. See
  `memory-bank/source-audits/hunter-tracking-pitfall-rabbit-restoration-2026-07-19.md`.
- Bonfires and Fire spirits were re-audited against the official cutoff update,
  cutoff article/talk pages, and Darkan. Visible XP, warmth, `1/100` spirit
  appearance, `10%` Cooking XP, and reward contents are closed, but burned-hand
  odds, reward weights/log scaling, same-effect warmth refresh, and the
  review-batch translation remain blocked. Darkan also conflicts at `1/500`
  spirits and on three warmth durations plus multiple reward quantities. See
  `memory-bank/source-audits/bonfire-fire-spirit-source-boundary-2026-07-19.md`.
- Cheese-wheel churning and Slice-all are implemented from pinned cutoff
  churn/item/talk revisions. Milk and butter churn at level 48 for 40.5 XP;
  milk returns its Bucket; churns do not fill Cooking urns; and one wheel
  slices into a level-shaped 5-35 Cheese at 4 XP each. The exact slice formula
  remains source-blocked and uses the disclosed bounded sample calibration.
  See
  `memory-bank/source-audits/cheese-wheel-churning-slicing-2026-07-19.md`.
- Shrink-me-quick is restored as the cutoff level-52, 6-XP Herblore recipe
  using Tarromin potion (unf) plus Shrunk ogleroot. The recipe is material-gated;
  ogleroot acquisition and potion use remain Grim Tales/Darkan-owned rather
  than duplicated in the skill runtime. See
  `memory-bank/source-audits/herblore-shrink-me-quick-2026-07-19.md`.
- The isolated Arctic-pine splitting sub-slice is live: level 54, one carried
  Arctic pine log to one Split log, 42.5 Woodcutting XP, quest-start gating,
  processing-aware carried packs, and period GE/item/art identity. Arctic pine
  and Eucalyptus chopping are also live with sourced levels, XP, outputs, and
  access rules; their hidden tree rolls use registered nearest-level
  placeholders. Cursed magic remains dependency-blocked until Spirit of Summer
  has a live quest substrate. See
  `memory-bank/source-audits/special-woodcutting-acquisition-2026-08-09.md`.
- Evil Tree is implemented as the settled review-native D&D: seven exact
  period tier gates/XP rows, five-review availability, nurture-only entry,
  three atomic Nurture/Prepare/Fell reviews, bounded period-ceiling rewards,
  and the eligible Woodcutting blessing. The unrecovered tier/reward/nest
  formulas remain explicitly labeled abstractions; no design wait remains.
  See
  `memory-bank/source-audits/evil-tree-implementation-harvest-2026-07-19.md`.
- Big Chinchompa is implemented as the settled review-native communal Hunter
  D&D: two windows per 240-review day, exact moth tiers and reward shop,
  grouped fifteen-moth jars, seeded aggregate crowd profiles, capped event and
  Competence points, complete undo, and successful-catch-only private-ground
  ticket consumption. Four tickets have executable ordinary Hunter targets.
  Polar-kebbit ticket use remains `WAIT: SOURCE` on that ordinary tracking
  target; no design wait remains. See
  `memory-bank/source-audits/big-chinchompa-implementation-harvest-2026-07-19.md`.
- Easy Treasure Trails is harvested but not admitted. The period record closes
  its one-to-five steps, clue families, content, item identities, and reward
  membership, but the settled per-tier ownership clause conflicts with the
  cutoff's global one-clue rule. Darkan's one-to-three step roll is rejected,
  and its clue/reward selection tables lack independent pre-EOC-lineage
  corroboration. See
  `memory-bank/source-audits/treasure-trails-easy-source-boundary-2026-07-19.md`
  and `memory-bank/design-gaps-implementation-2026-07-19.md`.
- Skeletal Horror is mechanic-complete at breadth level one. It ships both
  post-quest wish-list gates, exact cadence and entry payment, continuous phase
  and limb transitions through the real Combat reducer, safe death, exact
  first/repeat rewards, elite clues, persistence, undo, period art, and a
  compact D&D card. The four phase stat blocks, shared bonuses, and
  Melee/Magic style probability remain registered data-depth placeholders. See
  `memory-bank/source-audits/skeletal-horror-implementation-harvest-2026-07-19.md`
  and `memory-bank/placeholder-values.md`.
- The next implementation slice must have a pinned pre-EOC contract for its level, XP, inputs, outputs, gates, rates, and state transitions. Split proven sub-slices from blocked families as lava eel, Overload, and cannonballs already demonstrate.
- Backend acceptance: data, pure behavior, storage/migration, dispatch, acquisition semantics, telemetry, and undo.
- Frontend acceptance: `TargetRowMetadata`, real enablement/locks, target-local settings/equipment/inventory, icons, tooltips, and offscreen Qt coverage.
- Assets acceptance: period-appropriate art, explicit `--source rs3` where applicable, provenance, and path tests.

### Reconcile partial Combat skills with the skill ledger — status contract complete

Labels: `SOURCE AUDIT`, `IMPLEMENT`, `WAIT: DARKAN` for hidden enemy/equipment behavior.

- Attack, Strength, Defence, Constitution, and Ranged use an explicit `partial` surface state with `training_source = Combat`; Magic is now a complete surface.
- Keep unified Combat selection; do not add five competing hub rows merely to make the registry count look complete.
- Quest gates and XP rewards now recognize trainable partial stats, and legacy pending Combat-stat XP migrates directly. See `memory-bank/source-audits/partial-combat-skill-registry-2026-07-11.md`.
- Continue weapon/ammo/spell/equipment/enemy breadth under `memory-bank/combat-design-grill-2026-06-23.md` rather than reopening the Combat loop design.

## Deep-grill queue — missing or incomplete skill surfaces

Each skill receives its own grill before implementation. Source-shaped facts should be resolved autonomously; grill only materially different AnkiScape choices.

### Slayer

Labels: `DESIGN CLOSED`, `WAIT: DARKAN`, `SOURCE AUDIT`, `DEPENDENCY: COMBAT/QUESTS/ACTIVITIES`.

- Reuse existing enemy Slayer metadata; add masters, assignment pools, XP, task progress, points/streaks, skips/blocks, reward shop, task-only targets, protection items, and Combat UI.
- Source sweep progress: Turael/Spria is reconciled at 23 families with a
  provisional 355-point denominator; Mazchna/Achtryn is reconciled at 27
  families with a provisional 325-point denominator; Vannaka is reconciled at
  35 families with a provisional 460-point denominator; Chaeldar is reconciled
  at 34 families with a provisional 388-point denominator; Sumona is reconciled
  at 37 families with a provisional 407-point denominator; Duradel/Lapalok are
  reconciled at 35 families with a provisional 334-point denominator; Kuradal
  is reconciled at 36 families with a provisional 322-point denominator.
  Turael, Mazchna and Vannaka are live; the other four roles stay out of
  rolls until their full pools are executable. See the dated
  `slayer-turael-spria-pool`, `slayer-mazchna-achtryn-pool`,
  `slayer-vannaka-pool`, `slayer-chaeldar-pool`, `slayer-sumona-pool`, and
  `slayer-duradel-lapalok-pool` audits, plus `slayer-kuradal-pool`.
- The bounded 2026-07-17 harvest is closed. Turael/Spria is now the first
  certified live master: all 23 assignment families have an executable
  representative, and its assignment, Combat-credit, task-filter, migration,
  undo, and management surfaces are complete. Resume the remaining masters from
  their per-family blocker identities; do not reopen owner design or expose a
  partial pool.
- Mazchna/Achtryn is now the second completely encoded pool. Stable family
  identities are separate from its 27 master-specific roll rows and provisional
  325-point denominator. `tools/audit_slayer_readiness.py` derives the live
  readiness ledger: 27/27 families are ready since Mogres landed (`adb2f935`),
  and Mazchna needs Combat 20 only. Vampyres are closed through the
  ordinary level-61 Feral vampyre with its Priest in Peril gate, guaranteed
  Vampyre dust, Holy-symbol weakness, bite effect, and losslessly normalized
  100,000-slot table. Wall beasts are closed through
  the ordinary level-49 representative with a start-only Spiny-helmet gate and
  a reconciled 100,000-slot table. Kalphites are closed
  through the ordinary level-85 Soldier with its period poison risk and exact
  128-slot drop table.
  Pyrefiends are closed through the ordinary level-43 representative with
  source-faithful magic-based-melee semantics. The role is live; stale
  prose blockers for protection,
  poison, finishers, Dogs, Grotworms, and Hobgoblin XP no longer control
  certification.
- Vannaka is now the third completely encoded pool. Its 35 master-specific
  rows preserve the provisional 460-point denominator and are live at
  35/35 readiness. Ordinary Molanisk closes Molanisks with its sourced quest,
  Slayer-bell, and real lit-source gates, exact 100,000-slot Darkan selector,
  and independent easy clue. Ordinary Brine rat closes Brine rats with its sourced
  Slayer/Olaf's-Quest/Spade gates, exact 512-slot ordinary selector, exact
  Darkan charm selector, independent clue, and generated Brine sabre equipment.
  Ordinary Ogre closes the Ogres family with its exact nested
  common-seed and tertiary-bone drops; ordinary Jelly closes Jellies with
  magic-based melee, an exact 128-slot table, and generated Mithril boots;
  ordinary Bloodveld closes Bloodvelds with the same distinct attack channel,
  another exact table, and generated Black boots; ordinary Infernal Mage adds
  one exact Darkan selector plus generated Lava battlestaff and dark Mystic
  equipment; ordinary Basilisk adds its Mirror-shield gaze contract, exact
  tables, and generated light Mystic hat; ordinary level-63 Crocodile reuses
  the live desert-heat loop while rejecting the merged level-89 drop row. The
  Lost-City-gated Otherworldly being adds its exact 128-slot table without
  duplicating quest work. The Cabin-Fever-gated Jungle horror adds guaranteed
  Bones plus Darkan's exact 100,000-slot ordinary selector. The Legends'-Quest-
  gated Shadow warrior adds one 128-slot ordinary selector and Darkan's exact
  executable charm selector. The Priest-in-Peril-gated Aberrant spectre adds
  exact stench damage/drain behavior, a 512-slot ordinary selector, four exact
  nested Darkan tables, a derived charm selector, and generated dark Mystic
  legs. Ordinary Dust devil adds the cutoff's continuous Face-mask damage
  gate, one exact 32,768-slot ordinary selector, and an independent exact
  charm selector. Earth warrior now carries the bounded 1%/250-LP Wilderness
  ambush, current kept/lost-equipment confirmation, encounter reset, and
  no-grave equipment-retention rule. Ordinary Green dragon now adds reusable
  dragonfire tiers, exact review-driven Antifire/Super-antifire durations,
  wearable Anti-dragon shield item 1540, the existing Wilderness-risk contract,
  and the pinned ordinary drop selectors. Its hidden 1/4 breath selector is
  labeled `provisional/darkan`, while charm rates remain `source_blocked`.
  Ordinary Harpie Bug Swarm adds its continuous lit-lantern shield gate,
  Firemaking 33 lighting and extinguishing chain, exact 100,000-slot ordinary
  selector, and independently derived 202-slot charm selector. Lit item 7053
  is generated equipment but is correctly excluded from cave-light gates.
  Ordinary Killerwatt adds its existing Ernest-the-Chicken access, dynamic
  magical-melee/Ranged channel, Slayer-37 Insulated-boots requirement,
  explicitly labeled additive 0–140 LP thundercloud abstraction, exact
  100,000-slot ordinary selector, and derived 303-slot charm selector.
  Ordinary Sea Snake Hatchling and Sea Snake Young add their cutoff
  combat/poison contracts, pinned sprites, Darkan ordinary/tertiary selectors,
  and independent medium clues. Royal Trouble completion is a conservative
  gate until the Darkan quest thread exposes its mid-quest dungeon-permission
  state. Ordinary Brine rat adds its Slayer/Olaf's-Quest/Spade access,
  exact ordinary/charm/clue selectors, and generated Brine sabre. Olaf's Quest
  completion is conservative until Darkan exports the sourced stage-40 cavern
  permission. Ordinary Turoth adds its Slayer-55 and exact effective-damage
  routes, source-backed Broad ammunition support, poison immunity, exact
  ordinary/charm/clue selectors, and generated rare equipment. The sole
  remaining blocker derived by `tools/audit_slayer_readiness.py` is Mogres.
  Continue from that generated ledger; do not expose or renormalize the
  partial master. See
  `source-audits/slayer-vannaka-ogre-combat-2026-07-18.md` and
  `source-audits/slayer-jelly-combat-2026-07-18.md`, plus
  `source-audits/slayer-bloodveld-combat-2026-07-18.md` and
  `source-audits/slayer-infernal-mage-combat-2026-07-18.md`, and
  `source-audits/slayer-harpie-bug-swarm-combat-2026-07-18.md`, plus
  `source-audits/slayer-killerwatt-combat-2026-07-18.md`, plus
  `source-audits/slayer-sea-snakes-combat-2026-07-18.md`, plus
  `source-audits/slayer-brine-rat-combat-2026-07-18.md`, plus
  `source-audits/slayer-molanisk-combat-2026-07-18.md`, plus
  `source-audits/slayer-turoth-combat-2026-07-18.md`, plus
  `source-audits/slayer-basilisk-combat-2026-07-18.md`, plus
  `source-audits/slayer-crocodile-combat-2026-07-18.md` and
  `source-audits/slayer-otherworldly-being-combat-2026-07-18.md` and
  `source-audits/slayer-jungle-horror-combat-2026-07-18.md` and
  `source-audits/slayer-shadow-warrior-combat-2026-07-18.md` and
  `source-audits/slayer-dust-devil-combat-2026-07-18.md` and
  `source-audits/slayer-earth-warrior-wilderness-risk-2026-07-18.md`.
- Chaeldar is now the fourth completely encoded pool. Its 34 master-specific
  rows preserve the provisional 388-point denominator and remain hidden at
  25/34 readiness. Fire giants now use the ordinary level-86 representative,
  while Blue dragons expose separate adult and baby task choices with
  source-backed dragonfire separation, exact selectors, a Summoning-99 egg
  gate, and cutoff assets. Bronze dragons now preserve metal-dragon
  dragonfire, the guaranteed bar drop, exact ordinary/charm/plate/clue
  selectors, and cutoff art. Cave horrors now preserve Cabin Fever/light
  access, class-aware Witchwood/Slayer-helmet protection, the sourced scream,
  exact selectors, the Black mask route, and cutoff art. Dagannoths now expose
  separate level-74 ranged and level-92 melee ordinary forms, one exact
  combined selector, charms, a medium clue, and distinct cutoff art. Elves now
  expose separate level-90 ranged and level-108 melee ordinary forms behind
  Regicide, one exact shared ordinary selector, charms, a hard clue, and
  distinct archived 2010 art. The nine exact blockers are Fever spiders,
  Fungal magi, Grifolapines,
  Grifolaroos, Jungle strykewyrms, Kurasks, Trolls, Vyrewatch, and Warped
  tortoises. Resume from `tools/audit_slayer_readiness.py`; do not render or
  renormalize the pool.
  Fever-spider access remains a partial Rum Deal permission seam rather than a
  false completion gate. The 2026-07-19 source pass additionally found a hard
  disease-value conflict: the cutoff requires three balm doses, while Darkan's
  disclosed severity-15/four-point reconstruction requires four, and the exact
  unprotected hit formula is not period closed. Keep Fever spiders blocked;
  this is a source dependency, not an open design fork. The Fungal-mage source
  pass likewise found Darkan's combat row explicitly marked `nostats`, with all
  five levels generated as non-real fallbacks; conflicting period
  Melee/Ranged reducers, unresolved quantity variants, and the absent canonical
  Neem-oil acquisition loop keep that family blocked without reopening design.
  The paired Grifolapine/Grifolaroo pass found the same non-real generated-stat
  boundary, plus visible LP/damage conflicts, a missing neemed
  Magic-to-Ranged transition, and two duplicated Darkan ordinary-drop stubs
  contradicting the distinct cutoff tables. Keep both families blocked.
  The Jungle-strykewyrm pass found another `nostats` target plus direct
  melee-poison, burrow-damage/poison, and ordinary-quantity conflicts; its
  three attack-conditional poison channels also exceed the current generic
  poison schema. Keep that family blocked.
  The Kurask combat row and Turoth restriction seam are source-ready, but its
  Darkan ordinary selector directly conflicts with cutoff quantities and does
  not preserve the visible drop set. Keep Kurask blocked until its selector is
  reconciled without cherry-picking.
  Stop at Trolls: the settled broad-category contract and pool audit require
  explicit stable mountain/ice/river/undead membership, while the executable
  registry declares only `("troll",)`. One generic row would falsely certify
  the category. See
  `audits/slayer-troll-registry-conflict-2026-07-19.md`; do not choose or
  collapse the variant set without resolving which authoritative record is
  wrong.
  Vyrewatch repeats that authority mismatch: the cutoff task accepts
  Vyrewatch, Vyreladies, Vyrelords, and Juvinates while the stable registry
  declares only `("vyrewatch",)`. It is also source-blocked on representative
  stats/drops and an executable allowed weapon; Legacy of Seergaze grants the
  Ivandis-flail item but it is not equipable or recognized by Combat. See
  `audits/slayer-vyrewatch-registry-conflict-2026-07-19.md` and
  `source-audits/slayer-vyrewatch-combat-2026-07-19.md`.
  Warped tortoise remains blocked on generated levels, a maximum-hit conflict,
  missing Crystal-chime execution/acquisition, and conflicting/incomplete
  drops. See
  `source-audits/slayer-warped-tortoise-combat-2026-07-19.md`.
  See
  `source-audits/slayer-chaeldar-registry-2026-07-18.md` and
  `source-audits/slayer-fever-spider-combat-2026-07-19.md` and
  `source-audits/slayer-fungal-mage-combat-2026-07-19.md` and
  `source-audits/slayer-grifolic-creatures-combat-2026-07-19.md` and
  `source-audits/slayer-jungle-strykewyrm-combat-2026-07-19.md` and
  `source-audits/slayer-kurask-combat-2026-07-19.md` and
  `source-audits/slayer-vyrewatch-combat-2026-07-19.md` and
  `source-audits/slayer-warped-tortoise-combat-2026-07-19.md` and
  `source-audits/slayer-fire-giant-combat-2026-07-18.md` and
  `source-audits/slayer-blue-dragon-family-combat-2026-07-18.md` and
  `source-audits/slayer-bronze-dragon-combat-2026-07-18.md`,
  `source-audits/slayer-cave-horror-combat-2026-07-18.md`, and
  `source-audits/slayer-dagannoth-combat-2026-07-18.md`.
- Sumona is now the fifth completely encoded pool. Its complete 37-row table
  preserves the source-settled 407-point denominator and remains hidden at
  20/37 derived readiness. The existing Abyssal-demon and Nechryael targets
  deliberately remain non-certifying until their teleport-interruption and
  Death-spawn loops are executable; Aquanites, Desert strykewyrms, Fungal magi,
  Grifolapines, Grifolaroos, Jungle strykewyrms, Kurasks, Mutated jadinkos,
  Scabarites, Spiritual mages, Spiritual warriors, Terror dogs, Trolls,
  Vyrewatch, and Warped tortoises lack a certifying target.
  Continue from `tools/audit_slayer_readiness.py`; do not expose or renormalize
  the partial master. Governing pool evidence:
  `source-audits/slayer-sumona-pool-2026-07-17.md`.
- Duradel/Lapalok is now the sixth completely encoded pool. Its complete
  35-row table preserves the provisional 334-point denominator, Combat 100,
  Slayer 50, Shilo Village access, and the While Guthix Sleeps identity swap
  while remaining hidden at 14/35 derived readiness. The 21 exact blockers
  remain visible in `tools/audit_slayer_readiness.py`; they include the
  existing Abyssal-demon and Nechryael mechanic gaps and 19 families without
  a certifying Combat target.
  Continue from that generated ledger; do not expose or renormalize the
  partial role. Governing pool evidence:
  `source-audits/slayer-duradel-lapalok-pool-2026-07-17.md`.
- Black dragon is source-closed and executable as Duradel's thirteenth ready
  family. The ordinary level-227 target preserves the cutoff LP/XP/maximum,
  shared leather-dragon dragonfire, complete lossless ordinary selector,
  quantity-three charms, independent egg/visage/clue rolls, and pre-cutoff
  asset. King Black Dragon, Queen Black Dragon, Daemonheim, and
  location-specific contexts remain separate. See
  `source-audits/slayer-black-dragon-combat-2026-07-19.md`.
- Steel dragon is source-closed and executable as Duradel/Lapalok's fourteenth
  ready family. The ordinary target preserves cutoff LP/XP/maximum, the
  settled metal-dragon dragonfire abstraction, guaranteed five-bar drop,
  exact emulator combat state, lossless quantity-three charms, all
  independent plate/visage/clue rolls, and cutoff art. Darkan's five-slot
  ordinary-selector gap is filled by the period-attested Coins x650 row at
  the matching OSRS fork's exact 5/128 rate and remains labeled
  `provisional/osrs-lineage`. See
  `source-audits/slayer-steel-dragon-combat-2026-07-19.md`.
- Suqah remains source-blocked despite a complete southern melee-only combat
  row. The cutoff article explicitly names that form as the common Slayer
  target, but its intact drop table names Grimy guam and Grimy marrentill while
  Darkan's exact 129-slot selector substitutes Grimy ranarr and Grimy irit.
  Numeric cutoff rates do not survive, so the emulator weights cannot be
  transplanted onto different items. Duradel/Lapalok remains 14/35. See
  `source-audits/slayer-suqah-combat-2026-07-19.md`.
- Mithril dragon remains source- and representation-blocked. Darkan conflicts
  with the cutoff 2,540 LP and 182-LP Ranged/Magic maxima, while its 127-slot
  ordinary selector narrows or omits period-visible quantities. The current
  fixed-style Combat schema cannot encode the settled
  Melee/Magic/Ranged/dragonfire selector or enforce the Ancient
  Cavern/Barbarian-training gate. Duradel/Lapalok remains 14/35. See
  `source-audits/slayer-mithril-dragon-combat-2026-07-19.md`.
- Skeletal Wyvern remains source- and dependency-blocked. Breath probability
  and freeze duration are missing, Darkan implements only fixed melee, and the
  current schema cannot express the settled Melee/Ranged/breath transaction.
  None of the six period-valid protective shields is live equippable
  equipment; Anti-dragon shield is explicitly invalid. Duradel/Lapalok remains
  14/35. See
  `source-audits/slayer-skeletal-wyvern-combat-2026-07-19.md`.
- Waterfiend remains source- and context-blocked. Darkan's complete 128-slot
  ordinary selector conflicts with the cutoff Coins, rune, herb, fish,
  ore/bar, and other quantities and applies a Ghorrock-only Coal row
  name-wide. The settled location-context transaction is absent, so a metadata
  flag must not falsely certify the target. The ordinary level-115 and
  level-134 Ghorrock forms remain distinct under Owner decision 20.
  Duradel/Lapalok remains 14/35. See
  `source-audits/slayer-waterfiend-combat-2026-07-19.md`.
- Dark beast remains source-, context-, and representation-blocked. Darkan's
  fixed-Melee/zero-maximum combat row cannot preserve the cutoff
  174-LP Melee/80-LP Magic conditional transaction; its ordinary selector
  conflicts on Coins, runes, herbs, equipment, and Dark-bow rate; and its
  charm algorithm gives about 8% Blue against the cutoff's direct 14%.
  The global family feature also cannot distinguish Duradel's Temple route
  from Kuradal's task-only Dungeon context. Duradel/Lapalok remains 14/35.
  See `source-audits/slayer-dark-beast-combat-2026-07-19.md`.
- Ganodermic creatures remain source- and dependency-blocked. Both combat rows
  are `nostats`; the runt has no ordinary selector; the beast's 256-slot
  selector conflicts on runes, flakes, and noted ranarr; and its fungal damage
  conflicts with the cutoff. Darkan's neem form keeps attacking rather than
  preserving temporary suppression, while the canonical Neem-oil/resource/
  context chain is absent. Duradel/Lapalok remains 14/35. See
  `source-audits/slayer-ganodermic-creatures-combat-2026-07-19.md`.
- Goraks remain source-, context-, and representation-blocked. The shared
  Fairy Tale II assignment gate is now source-closed and encoded. Darkan's
  level-149 row conflicts with the cutoff LP/maximum, while its ordinary
  selector omits Gorak claws and other rows, adds Bones, and changes five exact
  Coin quantities into a continuous range. The cutoff does not resolve its
  cadence conflict or exact random-stat drain magnitude. Current Combat lacks
  the target-native prayer-bypassing landed-hit drain transaction, and neither
  settled Fairy-ring/God-Wars route is executable. Duradel/Lapalok remains
  14/35. See `source-audits/slayer-gorak-combat-2026-07-19.md`.
- Warped terrorbirds are stopped on an authority/schema conflict. The cutoff
  says The Path of Glouphrie need only be started before assignment, while the
  current family field requires completion. Both Darkan rows are `nostats`,
  the quest-form maximum conflicts, its selector disagrees with cutoff
  quantities, and fixed-style Combat cannot preserve the mixed
  attack/morphology loop. Crystal chime is not a reachable dependency.
  Duradel/Lapalok remains 14/35. See
  `source-audits/slayer-warped-terrorbird-combat-2026-07-19.md` and
  `audits/slayer-warped-terrorbird-gate-conflict-2026-07-19.md`.
- Ice strykewyrms are stopped on an authority/schema conflict. The direct
  cutoff article and settled Kuradal audit require Tale-of-the-Muspah
  completion, while the settled Duradel/Lapalok audit and global family row
  omit it. Darkan's only combat row is `nostats`, its fixed Ranged/170 model
  and later fire-cape handler conflict with the cutoff fight, and its
  independent-drop file is incomplete. The cape, 2,000-point technique, and
  mixed-style strykewyrm transaction are not live. Duradel/Lapalok remains
  14/35. See
  `source-audits/slayer-ice-strykewyrm-combat-2026-07-19.md` and
  `audits/slayer-ice-strykewyrm-gate-conflict-2026-07-19.md`.
- Kuradal remains unencoded despite its source-closed 36-row, 322-point pool.
  The period family ledger now closes ordinary TzHaar as Ket/Xil/Mej/Hur and
  Living rock creatures as patriarch/protector/striker, explicitly excluding
  Fight Cave `Tok-` creatures from the ordinary TzHaar family. Stop before
  registry work: the current global family-gate schema cannot represent
  Kuradal-only Aquanite and Ice-strykewyrm eligibility, the
  Kuradal-Dungeon-specific Dark-beast route, or Barbarian Training master
  access without contradicting settled records. See
  `source-audits/slayer-kuradal-family-boundaries-2026-07-19.md` and
  `audits/slayer-kuradal-registry-schema-conflict-2026-07-19.md`.
- Aquanite and Desert strykewyrm remain source-blocked. Both Darkan definitions
  generate non-real levels. Aquanite lacks its prayer-negating special and has
  visible Water-rune/Seaweed/Soul-rune conflicts. Desert strykewyrm's 1/21
  burrow and unconditional double-hit implementation conflict with the period
  frequency/consequence, and its Potato-cactus/herb/Coin selector is
  incompatible. See
  `source-audits/slayer-aquanite-desert-strykewyrm-combat-2026-07-19.md`.
- Terror dogs remain source-blocked despite source-ready level-110 stats,
  Haunted Mine access, target-local one-Prayer-point-per-two-ticks drain,
  Big-bones split, and Granite-helm data. Darkan's executable 128-slot
  selector includes five Coins ×11 slots, while the complete pre-cutoff
  article history permits only ×44–200 and ×440. Do not cherry-pick that row
  away or implement a consumerless Prayer helper. See
  `source-audits/slayer-terror-dog-combat-2026-07-19.md`.
- Stop at Spiritual mages and Spiritual warriors: every settled master record
  requires four god variants plus target-local alignment context, but the
  executable registry names only a Saradomin target for each family. Do not
  let one representative certify either family and do not infer stable IDs for
  the omitted variants. See
  `audits/slayer-spiritual-families-registry-conflict-2026-07-19.md`.
- Red dragons are source-closed and executable as Sumona's twentieth ready
  family. The adult and baby representatives preserve the cutoff substitution
  rule, adult-only dragonfire, exact period maxima, Darkan selectors, and
  pre-cutoff assets. The direct period 158-LP adult maximum explicitly
  supersedes Darkan's conflicting 144-LP lead. See
  `source-audits/slayer-red-dragon-family-combat-2026-07-19.md`.
- Scabaras lancer remains source-blocked despite a complete cutoff identity,
  LP/XP/style/maximum/drop record. Darkan explicitly marks the executable row
  `nostats`, the cache proves only identity/options, and game-main contains
  spawns without Attack/Strength/Defence/Magic/Ranged levels. Do not infer
  those content values from combat level 112 or substitute another family
  representative. See
  `source-audits/slayer-scabaras-lancer-combat-2026-07-19.md`.
- Stop at Mutated jadinkos: the three settled master-pool records require baby,
  guard, and male identities with Slayer gates 80/86/91, while the executable
  registry contains only the baby and one family-level gate of 80. See
  `audits/slayer-mutated-jadinko-registry-conflict-2026-07-19.md`; do not let
  one baby target certify the family or infer a registry correction. The
  independent combat harvest also found all three Darkan rows explicitly
  `nostats` and conflicting guaranteed-drop quantities. See
  `source-audits/slayer-mutated-jadinko-combat-2026-07-19.md`.
- Iron dragon is source-closed and executable as Sumona's nineteenth ready
  family. The ordinary level-189 target preserves the period 1,650 LP and
  173.2 Slayer XP, reuses the settled metal-dragon dragonfire abstraction,
  implements the exact Darkan ordinary/charm/tertiary selectors, and includes
  its pre-cutoff target asset. See
  `source-audits/slayer-iron-dragon-combat-2026-07-19.md`.
- Abyssal-demon teleport interruption and the Nechryael Death-spawn loop have
  a dedicated follow-up harvest in
  `source-audits/slayer-abyssal-nechryael-specials-2026-07-19.md`. Do not
  implement either from qualitative prose alone. Abyssal demon still needs a
  cutoff trigger rate and owner-set reducer magnitude; Nechryael still needs a
  summon rate and finite roster lifetime. Darkan's 1/10 summon roll is a
  lower-tier lead, while its cleanup-on-summoner-death conflicts with cutoff
  strategy text and cannot be adopted.
- Darkan ordinary-drop semantics are corrected across eleven live Slayer
  targets. Sibling nonzero JSON rows now share one cumulative selector, while
  rate-zero rows, charms, and explicitly labeled period abstractions remain
  separate channels. This preserves every marginal probability and removes
  impossible sibling multi-drops. See
  `source-audits/slayer-darkan-drop-selector-correction-2026-07-18.md`.
<a id="mogre-combat"></a>
- Mogre combat is source-closed, including its atomic Fishing-explosive lure,
  poison immunity, exact 128-slot Darkan table, tertiary bones, and target
  icon. The `skippy_and_the_mogres` miniquest dependency landed at `9b933084`
  and is registered in `data/quest/ledger.py`; verify the current combat and
  Slayer-readiness gates separately before claiming the whole family complete.
  See `source-audits/slayer-mogre-combat-2026-07-18.md`.
- Cyclopes are closed through their honest Warriors' Guild boundary rather than
  a context-free row: all five token sources, entry and residual drain,
  animated armour, Cyclops combat, progressive defenders, Kamfreena showing,
  and the spawned defender-gated Cyclossus are executable. See
  `source-audits/warriors-guild-live-implementation-2026-07-18.md` and
  `status-updates/warriors-guild-results-2026-07-18.html`
  (<https://vsx8a7pxsimj.postplan.dev>). Full core and real offscreen Qt
  discovery each pass all 1,592 tests.
- Park Social Slayer unless genuine shared-player state ever exists; do not ship
  a simulated partner or solo co-op multiplier. Preserve all seven period Slayer
  master challenges in the design and source their compound objective ledgers.
- Add an explicit `Get assignment` master picker and make its NPC identity
  quest-reactive: Turael to Spria and Duradel to Lapalok after While Guthix
  Sleeps, with Achtryn replacing Mazchna only during the quest interval.
- Keep every period master role visible in the picker; disable ineligible rows
  and state their unmet combat, Slayer, quest, and activity requirements.
- Build the complete cutoff reward/unlock ledger. Required finishing items must
  gate rockslugs, desert lizards, zygomites, and gargoyles; the 400-point quick
  killing-blow unlock automates the finisher without removing the item check.
- Preserve the ring of slaying's eight-charge transport value by letting one
  charge erase a qualifying Slayer destination's abstract run-energy entry
  cost; do not add map state, travel reviews, or wall-clock delay.
- Represent only mechanically distinct Slayer areas as target-local Combat
  contexts, including Kuradal's Dungeon; collapse cosmetic duplicate locations.
- Keep Slayer management inside one Skills page with `Assignment`, `Masters`,
  and `Rewards` subviews; reuse shared search and deep-link into Combat rather
  than opening nested dialogs or duplicating the fight picker.
- Build `Smoking Kills` and every still-incomplete prerequisite quest definition
  in the Slayer program so Sumona, reward points, and the Rewards subview are
  genuinely reachable; feed those quests through the canonical missing-quest
  backlog and runtime rather than adding flags or bypasses. Stolen Hearts and
  Diamond in the Rough, Icthlarin's Little Helper, and Smoking Kills are now
  source-backed and playable. Sumona and the reward-point surface are therefore
  reachable without bypass flags. Diamond in the Rough's two optional level-80
  hidden-reward actions are separate one-time claims rather than automatic
  quest-completion XP.
- Shilo Village is now source-backed and playable. Continue the transitive
  Slayer-helmet route in dependency order: replace Jungle Potion's remaining
  generated objective buttons; build Big Chompy Bird Hunting, Zogre Flesh
  Eaters, Rum Deal, and Cabin Fever; then activate Mos Le'Harmless, Cave horrors,
  the 1/512 Black mask drop, Slayer reward purchases, the 400-point helmet
  unlock, and Crafting 55 assembly. Preserve every period quest and skill
  prerequisite rather than adding Slayer-local waivers.
- Keep cutoff-live assignment families in the completeness ledger but do not
  render implementation-missing families as locked or coming-soon rows. Derive
  runtime readiness from stable dependency identities so each family enters the
  live UI and authentic weighted roll automatically when its quest, target,
  context, acquisition, and unlock dependencies are genuinely implemented. Add
  each remaining master to the live completeness audit, which now names every
  Mazchna blocker, rejects stale blockers, prevents empty or malformed rollable
  pools, and refuses enabled partial masters. Apply the same rule to
  family-specific reward purchases when those rows land.
- Certify each Slayer master only after every ordinarily available family in its
  pinned cutoff pool has complete roll data and satisfies the owner-set variant
  coverage bar. Never ship a master whose baseline weights are silently
  renormalized around implementation gaps; apply authentic quest, reward,
  block-list, and other player-specific exclusions only after baseline
  certification. Optional special challenges do not block the ordinary pool;
  gate each offer on its own complete runtime readiness.
- Certify a baseline family once its roll data and one ordinarily available,
  end-to-end qualifying Combat variant are ready. Keep every remaining cutoff
  variant pinned and audit-visible but absent from player UI until its stable
  dependencies activate it automatically. If live variant breadth becomes hard
  to scan, allow expandable family-to-variant grouping inside the existing
  Combat picker; exact variants remain the only selectable targets. Inherently
  player-gated families certify only through their complete authentic gate chain,
  and every certifying variant must include its special kill/protection mechanics.
- Preserve sourced unprotected-combat consequences for Slayer protective gear
  and warn without blocking legal dangerous encounters. Hard-gate only literal
  source access/attack restrictions, and pin every family item's trigger,
  consequence, immunity, death/retreat behavior, and undo interaction in a
  focused audit before implementation.
- Cockatrice is the first completed protective-equipment slice: an equipped
  Mirror shield suppresses its source-reconciled fixed hit and stat drain, while
  the unprotected target remains legal and visibly warned. Banshee is also
  complete: the head-slot Earmuff/Slayer-helmet family suppresses a fixed
  maximum-LP/10 scream capped at 80 LP and a labeled flat-five drain across the
  period-proven eight skills. See
  `source-audits/slayer-protective-equipment-cockatrice-banshee-2026-07-17.md`.
- Jackal is now an executable Dogs-family representative with its cutoff
  identity, exact maximum hit, guaranteed Bones, asset, and Combat picker
  surface. This closes one family dependency for Turael/Spria and
  Mazchna/Achtryn without exposing either incomplete assignment pool. See
  `source-audits/slayer-dogs-jackal-combat-2026-07-17.md`.
- The ordinary level-13 Icefiend is now executable with its cutoff identity,
  explicit maximum hit, exact 128-slot ordinary table, asset, and Combat picker
  surface. Non-ordinary and Daemonheim variants remain separate. See
  `source-audits/slayer-icefiend-combat-2026-07-17.md`.
- Finisher-item acquisition metadata is now ready: Bag of salt, Rock hammer,
  Ice cooler, and Fungicide spray retain their source item IDs and real
  stackability in the shared registry. Desert lizard and the generic
  manual/automatic finisher engine are live with a source level gate,
  one exact ordinary drop selector, an asset, and review-native Waterskin
  supply cost. Rockslug and Gargoyle are also live with reconciled Combat/drop
  rows, period finishing windows, source-specific frozen/regeneration behavior,
  and proven assets. Both ordinary Mutated zygomites are now live behind Slayer
  57 and Lost City with distinct period rows, charged-spray preservation and
  canister reloads, reconciled drops, and proven assets. This closes every
  ordinary finishing-blow family. See
  `source-audits/slayer-finishing-blows-2026-07-15.md` and
  `source-audits/slayer-mutated-zygomite-combat-2026-07-18.md`.
- Complete the design-closure source sweep without reopening owner questions for
  source-determined behavior: close every per-master pool/weight/count/gate row,
  pin every family variant's membership/stats/Slayer-XP eligibility/context, and
  close protective, special-kill, challenge, and context state transitions.
- Turael/Spria's source pool is recorded in
  `source-audits/slayer-turael-spria-pool-2026-07-17.md`: 23 families and the
  provisional 355-point hidden-weight denominator are pinned. Its certified
  runtime closure is recorded in
  `source-audits/slayer-turael-runtime-closure-2026-07-17.md`; no target or
  special-kill blockers remain for that role. Mazchna/Achtryn, Vannaka, Chaeldar, and
  Sumona, Duradel/Lapalok, and Kuradal are now recorded in their corresponding
  dated pool audits. Continue the family/variant, protection, challenge and
  location-context ledgers before exposing any live assignment roll.
- Before that unlock, the finisher consumes its own correct review. Exclude the
  salt, ice, fungicide, and explosive shakers released in 2015.

### Summoning

Labels: `COMPLETE`, `SOURCE DEBT`, `DEPENDENCY: COMBAT/ACQUISITION`.

- **Implemented 2026-07-17:** `summoning-skill-contract-2026-07-16.md` now
  governs the live eighteenth skill surface. The full ordinary catalog,
  pouch/scroll training, follower lifecycle, points, BoB cargo,
  Familiarisation, pets, restoration potions, Bogrog, Winter Storage, and the
  source-ready boost/heal/escape effects are shipped with assets, persistence,
  UI, undo, and pure/Qt coverage.
- Remaining combat/special-scroll effects, forager tables/cadence, and ordinary
  familiar teleports stay source/dependency-blocked. Daemonheim remains wholly
  owned by Dungeoneering; do not leak its familiars or herbs into overworld
  Summoning.
- Familiar lifetime is settled to every answered card, including Again, with a
  separate short-duration conversion that preserves period ratios rather than
  reusing the six-minute calendar scale. Pinned evidence is in
  `source-audits/summoning-familiar-lifecycle-2026-07-16.md`; the cross-system
  reconciliation is `simulation-time-boundary-2026-07-16.md`.
- BoB expiry creates an independently timed familiar-cargo reclaim event rather
  than auto-banking. Gravestones and cargo events use the shared reviewer alert
  strip in `review-hud-world-alerts-contract-2026-07-16.md` with distinct art and
  behavior.
- Implement one global familiar slot with a canonical Equipment panel and synced
  Bank/reviewer/target projections. Casual target presets select best available by
  sourced familiar role and auto-pack an active BoB; Advanced pins the exact
  familiar and exposes its separate inventory grid. Target navigation alone never
  dismisses, replaces, or repacks the live global familiar; the settled safe Bank-
  boundary swap may later replace it when all preconditions hold.
- Casual Summoning-point upkeep inserts one `Visiting altar+obelisk` restoration
  on the next successful answer when needed, replacing that target action and fully
  restoring ordinary Prayer and Summoning points; Again never restores. Existing
  combat Bank-run altar stops coalesce the obelisk without a second review. Advanced
  exposes the same automation as a toggle plus a manual command.
- Casual auto-special is globally on by default but fires only on successful
  answers, consumes a matching target-carried scroll plus sourced special-move
  points, and uses catalog-backed role triggers that avoid inapplicable or wasted
  effects. Bank scrolls are never consumed implicitly.
- Classify every familiar effect as passive periodic, continuous, or
  foreground/encounter-dependent. Passive effects advance and may produce on every
  answered card including Again; commands and attacks retain their successful-action
  gates. The catalog must state the class rather than deriving it from names.
- Familiar LP takes enemy damage only through a pinned retaliation, area, enemy,
  or aggro/tanking mechanic; attacking alone creates no exposure, and source
  silence means zero damage rather than a fabricated fallback targeting roll.
- An enabled target familiar policy atomically renews or replaces from compatible
  carried pouches on successful answers, including mid-encounter replacement.
  Advanced chooses its exact pouch-slot budget; missing pouch/points leaves a
  persistent lapsed reason and never partially consumes resources or Bank stock.
- If carried pouches run out while the policy is enabled, a successful answer may
  become a one-review Bank refill/resummon detour when compatible stock exists.
  Again never banks; insufficient Bank stock leaves the policy visibly lapsed.
- A target-policy mismatch may swap safely at the next Bank boundary: deposit BoB
  cargo, verify the replacement can succeed, then dismiss and summon atomically.
  Failed preconditions preserve the old familiar and show the new policy as queued.
- Casual `Best available` falls back to the strongest owned, level-valid, in-stock
  familiar in the configured role whenever replacement is needed. It never crosses
  roles; Advanced remains pinned to its exact familiar and lapses rather than substituting.
- Restocking a stronger same-role pouch never interrupts a live Casual fallback.
  `Best available` re-resolves at renewal, expiry, death, or explicit manual switch,
  preserving the remaining value of the already-consumed pouch.
- A BoB cannot transfer supplies during consecutive successful bursts against a live
  enemy. Again disengages without withdrawing; Casual may preset-top-up at the next
  successful pre-engagement boundary, as it may before combat or after kill/retreat.
- `Off — no familiar automation` never summons, renews, replaces, or auto-specials for
  that target, but it preserves an already-live global familiar and its paid duration.
- Familiarisation is source-pinned as a once-weekly shard/focus D&D ending at 60 shards,
  zero focus, or its period time cap, followed by a shard-scaled ingredient-box or
  triple-charm choice. The2026-10-14 owner translation is four successful answers,
  15 shards per success and no focus field. Again pauses with no progress or shard gain.
- Ordinary training is source/app-pattern resolved under
  `source-audits/summoning-training-2026-07-16.md`: searchable pouch-infusion and scroll-
  creation families process one exact source unit per successful review; Wolf Whistle is
  optional; Dungeoneering rows stay out of the surface-world catalog. Exact row,
  acquisition, and route-cost harvesting remains before implementation.
- The old universal `park outside` idea is rejected. Restricted targets need a per-area
  consequence (`block_until_dismissed`, `auto_dismiss`, `summon_only_forbidden`, or
  `spirit_plane_hide`). Starting a target that must dismiss a live familiar opens a
  confirmation naming duration/pouch loss and any BoB cargo reclaim; Cancel changes
  nothing, Confirm dismisses without a review, and cargo never auto-banks. The live owner
  decision makes general manual Dismiss turn the current target policy Off by default,
  with an unchecked `Keep auto-summon` escape hatch; area-required dismissal preserves
  policy. Successful-review specials now award exact scroll-use XP in Casual and Advanced
  because every gameplay action is collapsed into automatic review resolution; Again never
  does, and only a future genuinely passive headgear-like auto-fire keeps the period zero-XP
  exception. Forager rows retain their sourced `drop_to_player` versus distinct
  `familiar_storage` delivery modes. A full carried inventory suppresses a drop roll with a
  visible log entry and no queued, banked, or owed output; storage-type familiars continue
  to their sourced capacity of 30 before suppressing later rolls.
- Familiar teleports select target-local alternate route profiles, with every source rate
  declaring its assumed route so a familiar never double-discounts a rate that already
  includes it. Spirit graahk's sourced 60-second Nature circuit replaces the slower route;
  ordinary familiar teleports use the live familiar without consuming another pouch. Void
  shifter reuses Combat retreat only when damage leaves the player alive below 10% LP, with
  no invented cooldown. Call to Arms remains tied to the future Pest Control activity.
- Magic teleports and charged jewellery share the target-local route-profile substrate.
  Magic's pure training casts remain, while a route cast consumes exact runes and awards
  exact XP once and jewellery consumes one source charge. Bank ownership alone is inert.
- Pets are restored as Summoning's tenth atomic family and close Construction's parked
  Menagerie dependency. Bank right-click **Let out**, follower-panel **Pick up**, and a
  separately confirmed **Release permanently...** keep activation distinct from Drop.
  Active pets share the follower slot and advance sourced growth/hunger on every answered
  card; stored hunger, growth, and stage persist but freeze. Casual auto-care reserves
  compatible food in real carried slots according to sourced hunger cadence and the next
  Bank boundary, then feeds and refills without Tamagotchi-style manual management. A
  high-hunger pet reuses that packing boundary and feeds before its first hunger advance.
  Cats retain staged quest and exceptional-function state.
  Exhausted food safely returns the pet home with an `Out of pet food` lapse rather than
  silently destroying it.
- Implement the source-owned pet routes in
  `source-audits/summoning-pet-acquisition-2026-07-16.md`: period pet shops/services,
  quest grants and transformations, Hunter catches, existing and missing nest/drop eggs,
  per-pet incubation/hatching, Construction Workshop creation, and activity reward shops.
  The searchable Pets log explains and links routes but never grants pets. Pin every exact
  cost, rate, XP value, timer, colour rule, and reclaim path before implementation. The
  Discontinued event pets remain compatibility-only outside the obtainable log and
  completion counts. Individual page review found no supported
  unreclaimable-one-time-pet category; Ex-ex-parrot and Broav reacquisition remain
  `source_blocked`, and their Release action cannot ship until those rows are resolved.
  Platypus **Release for reward...** belongs to its Hunter/quest location and atomically
  consumes the pet for the sourced casket/oyster roll; generic Release never grants it.
  Cat ratting is an explicit host target, Casual wily-cat retraining preserves its
  interaction-review cost, and Tooth creature auto-care cannot silently select a permanent
  adult variant. Source-timed growth that removes a capability uses the shared reviewer
  world-alert strip without pausing the transition. Mature god-bird protection is stored
  as a stage-gated faction flag but remains numerically inert until the later
  multi-enemy/God Wars grill; do not invent a generic defensive buff in the meantime.
  Unsafe death authentically destroys an active pet and any unprotected carried pet item;
  pets never enter the gravestone or Death's Office. Banked/Menagerie pets and safe-death
  contexts remain safe. Reacquisition and replacement state are source-specific.
- Rat Catchers' King Rat stage is one ordinary quest status line with the source-required
  cat item gate. Optional food, cautious retreat, LP exchange, and cat death remain
  represented scene detail; do not add a pet-combat actor, stance selector, hidden roll,
  or false mandatory food gate.
- Pack Yak Winter Storage fires at the full-pack boundary in Casual: spend one carried
  scroll and 12 special points to bank one configured eligible item only when that prevents
  the next Bank trip. Advanced may choose item priority and an earlier threshold. Route/rate
  metadata must declare whether Pack Yak use is already assumed.

### Dungeoneering depth

Labels: `IMPLEMENTED PARTIAL`, `SOURCE BLOCKED`, `DEPENDENCY: ALL SKILLS/COMBAT`.

- The owner-ratified contract remains in
  `dungeoneering-design-contract-2026-07-18.md`: seeded room graph, three-tier
  choice architecture, binds/kinship, complexity/prestige, closed economy, and
  staged shop.
- Dungeoneering is trainable. The Frozen floor runtime, Ring of Kinship tiers,
  staged reward trader, and working Coal bag are live; `core/skill_registry.py`
  records the surface as implemented and partial.
- Continue depth beyond the live Frozen slice. Keep exact generated room counts,
  skill-door failure values, and other unresolved mechanics source-blocked. The
  eight-room starter graph budget remains
  `provisional/owner-approved-review-translation`, not a historical claim.

## Wait for a stable Darkan restoration milestone

The local Darkan checkout is active restoration research input. Treat it as moving until a pinned, source-qualified milestone exists; branch distance is not fidelity evidence.

### Quest-by-quest fidelity across the complete definition catalog

Labels: `WAIT: DARKAN`, `SOURCE AUDIT`, `IMPLEMENT`.

- `generated/quest_catalog_generated.py` carries all 194 pre-cutoff quests, and
  `data/quest_data.py` materializes all 194 as `QuestDefinition` rows. Together
  with two miniquests, the live `QUESTS` and `QUESTS_BY_ID` collections contain
  196 definitions.
- Catalog and definition presence remain scaffolding. Re-audit each quest for
  authentic stages, branches, item transformations, combat, rewards, journals,
  unlocks, and missing-skill gates.
- Prioritise by what a quest unblocks. Thieving depends on The Feud,
  Death to the Dorgeshuun, and Mourning's End Part I for major methods.
- Slayer likewise owns `Smoking Kills` and every still-missing prerequisite in
  its reachable chain because the quest gates Sumona and the entire reward-point
  economy. That direct chain is now playable; the next Slayer-raised quest work
  is Jungle Potion fidelity, followed by the remaining transitive black-mask /
  Slayer-helmet route.
- Shilo Village is now source-backed and playable. The remaining route stays at
  the front of this quest program in dependency order: Jungle Potion fidelity,
  Big Chompy Bird Hunting, Zogre Flesh Eaters, Rum Deal, and Cabin Fever before
  Mos Le'Harmless, Cave horrors, the black-mask drop, and helmet assembly. The
  period quest tree is transitive, not limited to a manually named subset;
  already-playable prerequisites are reused and generated placeholders are
  replaced through the canonical runtime.
- Wait for Darkan where historical sources cannot prove hidden transitions or combat definitions; never fill gaps from modern RS3/OSRS.

### Complete pre-EOC bestiary

Labels: `SOURCE AUDIT`, `IMPLEMENT`, `WAIT: DARKAN`.

- Sized honestly 2026-07-13: `COMBAT_ENEMY_DATA` holds **130 enemies**; Darkan ships roughly **2,600 NPC combat definitions** under `data/npcs/combatdefs/`. Every attackable pre-cutoff NPC should exist.
- This was previously only a bullet under the Combat card ("continue enemy breadth"), which badly understated it.
- Skill work keeps discovering holes here — Thieving needs `market_guard` (present) for stall guards and the Menaphite thug (absent) for blackjacking, and Slayer will need the task-only roster wholesale.
- Source from Darkan combatdefs reconciled against the dated caches for NPC identity/options, then a pinned wiki revision for levels and drops.

### Large special methods and activities

Labels: `WAIT: DARKAN`, `SOURCE AUDIT`; add `DEEP GRILL` when activity flow is not already settled.

- Highest-value waits: Runespan; Bonfires/fire spirits (reconciled; hidden rolls, rewards, warmth refresh, and review-batch mapping remain blocked); Artisan's Workshop; Blast Furnace/Goldsmith; Living Rock remains; complex pyres/beacons; Gnome Restaurant; Hunter tracking/pitfall/snaring (reconciled deterministic Darkan ceiling still lacks required rolls); Habitat/Jadinkos.
- Great Orb Project is mechanic-complete as an Activities-only eight-round
  Runecrafting match. It ships the level-50 gate, bounded team score, distinct
  orb/barrier participation, round essence, ordinary rune multipliers, double
  XP, pending and majority token settlement, early-leave forfeiture,
  Casual/Advanced policy, persistence, undo, cadence, period art, and a manual
  Wizard Elriss shop with Pure essence Buy X. The shop now includes all ten
  ordinary cutoff talismans at their exact free/member prices, plus the
  Elemental talisman, first and replacement Omni-talisman claims, the exact
  one-time 13,605 Runecrafting XP, Korvak's Omni-tiara conversion, and all four
  Master Runecrafter rewards with exact equipment and capped all-Runecrafting
  XP bonuses. All 12 green, blue, and yellow standard Runecrafter pieces now
  have exact prices, identities, equipment bonuses, GOP-only per-piece XP
  behavior, and normalized art; the unrecovered rate is a registered
  placeholder. The 10,000-token Runecrafting staff, twelve ordinary talisman
  bindings, free Korvak Omni conversion, altar access, Law exception, exact
  equipment rows, carried recipes, and normalized art are also complete. All
  14 cutoff teleport tablets now have exact prices and identities, stackable
  Break actions, source art, period gates, and route-phase integration. Exact
  hidden score and essence rolls remain labeled data depth. See
  `memory-bank/source-audits/great-orb-project-horizontal-implementation-2026-07-21.md`.
- Wicked hood is mechanic-complete for its baseline horizontal graph. Manual
  essence, rune, and matching altar-teleport actions use a carried or equipped
  hood, fed access, real pack space, one non-stacking 240-answer allowance
  pool, persistent loss/reclaim state, and direct/review undo. Elemental and
  Omni feeds are reachable through Great Orb Project. Runespan outfit
  acquisition and session mechanics remain source-blocked; only the hood's
  future allowance-cap constants exist. Ourania remains source-blocked on its
  exact rune distribution. See
  `memory-bank/source-audits/gap-grill-11-runecrafting-provenance-2026-07-10.md`.
- Managing Miscellania is mechanic-complete as an Activities-only persistent
  kingdom surface. It ships the Throne/Royal Trouble gates and upgrades,
  review-day approval/salary/production clock, explicit coffer funding,
  individual worker allocation, retroactive collection, one exact Maple
  approval chore, persistence, undo, cadence, normalized period art, and the
  compact Landmarks card. The remaining resource families and hidden bonus
  selectors are catalog depth. See
  `memory-bank/source-audits/managing-miscellania-horizontal-implementation-2026-07-21.md`.
- Fishing Trawler is mechanic-complete as an Activities-only ten-review
  pressure trip. It ships the level-15 gate, source supplies and stack-aware
  28-slot activity pack, Casual urgency, Advanced duty/layout policy, fixed
  public-crew offset, leak/water/net pressure, real sinking loss, direct-banked
  level-shaped haul, 40%-ordinary Fishing XP, persistence, undo, cadence,
  normalized period art, and the compact docked/at-sea card. Exact hidden
  pressure/common-catch distributions remain labeled data-depth work. The
  level-95 Tiger shark row, one-per-trip cap, approximate one-in-five admission,
  Cooking chain, and combat-food behavior are now live; only its hidden exact
  selector and registered Cooking burn endpoints remain depth. See
  `memory-bank/source-audits/fishing-trawler-horizontal-implementation-2026-07-21.md`.
- Shooting Stars are mechanic-complete as an Activities-only communal Mining
  event with the complete 43-site cutoff crash catalog and legacy active-event
  repair. Exact hidden initial-size, first-finder, crowd, gem, and sub-200
  reward-rounding distributions remain data-depth work and do not block the
  breadth-first frontier.
- Fist of Guthix is mechanic-complete as an Activities-only safe two-round
  Combat minigame. Its tutorial, random pairing, role swap, exact six-tick
  cadence, temporary supplies, charge tactics, endpoints, token/rating economy,
  Reggie shop, per-copy condition substrate, undo, persistence, HUD, assets,
  and compact selected card are live. Opponent population, stance exposure,
  winner-token magnitude, and rating delta remain labeled data-depth
  abstractions rather than design or mechanic gaps. See
  `memory-bank/source-audits/fist-of-guthix-horizontal-mvp-harvest-2026-07-20.md`.
- Sorceress's Garden is mechanic-complete as an Activities-only seasonal
  stealth abstraction. All four gardens, exact gates/XP/fruit thresholds,
  fruit-versus-herb policy, automatic squeezing, Osman-versus-keep policy,
  juice effects, persistence, undo, cadence, assets, reachability, and compact
  card are live. Hidden herb weights remain data-depth source work and do not
  block the breadth-first frontier. See
  `memory-bank/source-audits/sorceress-garden-loop-2026-07-18.md`.
- Penguin Hide and Seek is mechanic-complete as an Activities-only weekly
  roster. It ships the base ten-spy loop, all three quest-shaped upgrades,
  direct roster selection, one-review spying, 50-point cap, exact coin/XP
  redemptions, persistence, both undo boundaries, cadence, normalized period
  art, a compact paginated card, and the complete 34 one-point plus 33 two-point
  cutoff location/disguise pools. See
  `memory-bank/source-audits/penguin-hide-and-seek-loop-2026-07-17.md`.
- Vinesweeper is mechanic-complete as an Activities-only Farming minigame. Its
  Spade/familiar entry, flag and Ogleroot economy, bounded one-roll review
  outcomes, rabbit pressure, Hunter defence XP, direct leave/refund, literal
  cutoff reward shop, Farming-XP redemption, persistence, undo, cadence,
  normalized period art, and compact card are live. Exact hidden field-outcome
  rates remain labeled data-depth work. The shop-discovered Compost potion
  chain is also reachable through all four doses, its instantaneous Utility
  conversion, and cutoff Grand Exchange rows. See
  `memory-bank/source-audits/vinesweeper-loop-2026-07-18.md`.
- TzHaar Fight Cave is mechanic-complete as a persistent Activities-only
  Combat challenge. Its exact 63 waves, engaged-target six-tick reviews,
  bounded unengaged pressure, creature mechanics, Jad telegraph/healers, safe
  death, partial TokKul, exact completion reward, follower/session gates,
  resume/leave, persistence, undo, cadence, Fire cape equipment, normalized
  art, Review HUD, and compact card are live. Hidden attack-style sequencing
  outside Jad and precise multi-NPC positional timing remain labeled data
  depth, not missing mechanics. See
  `memory-bank/source-audits/fight-caves-horizontal-mvp-2026-07-20.md`.
- Barrows is mechanic-complete as a persistent Activities-only dangerous
  Combat run. Its original brothers, Ritual-gated Akrisae, tunnel creatures,
  complete 3×3 graph, six-tick encounters, brother specials, suspension,
  dangerous death, early chest, reward-potential ladder, per-copy degrading
  weapons, Bob repair, persistence, undo, cadence, period art, reachability,
  and compact card are live. Exact exhaustive armour breadth and rare reward
  precision remain data-depth work. See
  `memory-bank/source-audits/barrows-horizontal-mvp-2026-07-21.md`.
- Flash Powder Factory is mechanic-complete as an Activities-only finite
  Agility/Thieving session. Its exact gates, eight/nine-slot run, productive
  and Again-idle circuits, scoring/cashout, strategy policies, catalyst,
  apparatus, residue, rubble, Factory/Rogue rewards, direct XP shop, Rogue-kit
  conversion, outfit Herblore effects, persistence, undo, cadence, normalized
  period art, Activity Circuit credit, and compact card are live. Exhaustive
  hidden-roll recovery remains data-depth work. See
  `memory-bank/source-audits/flash-powder-factory-horizontal-mvp-2026-07-21.md`.
- Werewolf Skullball is mechanic-complete as an Activities-only atomic Agility
  run. It ships exact entry gates, equipped Ring-of-Charos variants, three
  source-route presets, Advanced T/K/S plans, deterministic ten-goal completion,
  the disclosed move-count XP translation, persistence/migration, whole-answer
  undo, cadence, equipment integration, normalized period art, and a compact
  card. Historical route-error RNG and the exact post-four-minute server curve
  remain data-depth source gaps. See
  `memory-bank/source-audits/werewolf-skullball-loop-2026-07-17.md`.
- Gnome Ball is mechanic-complete as an Activities-only dangerous three-beat
  Agility/Ranged match. It ships exact five-goal XP grouping, weapon-only entry
  restriction, owner-approved tackle fallback, shared grave/item-loss death,
  Auto/Custom food packs, carried-only referee reward, period item/equipment
  identity, persistence, migration, multiplier stopping, undo, cadence,
  normalized art, and a compact card. Exact score/pass/throw/tackle server
  rolls remain data-depth source gaps. See
  `memory-bank/source-audits/gnome-ball-loop-2026-07-17.md`.
- Fish Flingers is mechanic-complete as an Activities-only six-review Fishing
  event. It ships answered-card ticket accrual, automatic tackle discovery,
  catches/weight/stock rotation, big fish and assists, terminal XP/tokens/
  medals, the complete outfit and tackle-box shop, ordinary-Fishing outfit
  effects, persistence, activity arbitration, undo, cadence, normalized art,
  and a compact dark-safe card. The exact post-July-2012 XP equation and hidden
  event distributions remain data-depth source gaps. See
  `memory-bank/source-audits/fish-flingers-loop-2026-07-17.md`.
- Phoenix Lair is mechanic-complete as a non-resumable Activities-only
  dangerous ritual. It ships exact quest/Slayer/tool/daily gates, one
  persistent aggregate five-guardian front, one pyre-preparation review, one
  persistent Phoenix fight, guardian Ashes, fixed completion rewards,
  dangerous death/grave handling, contextual Clap/Kick egg choice, both
  egglings and delayed level-72 hatching, persistence, undo, cadence,
  normalized period art, and a compact D&D card. Exact hidden egg odds,
  complete guardian stats/drop weights, Lesser-warrior max hit, and dust timing
  remain data-depth source gaps. See
  `memory-bank/source-audits/phoenix-lair-implementation-data-2026-07-21.md`.
- Skeletal Horror is mechanic-complete as a safe, recurring Activities-only
  boss. It ships both post-quest wish-list gates, Slayer 78, the exact
  answered-card payment and weekly two-bank cadence, four persistent Combat
  phases with continuous limb transitions and attack-style changes, buryable
  limbs, exact first/repeat rewards, elite clues, persistence, arbitration,
  direct-action undo, normalized period art, and a compact D&D card. The four
  phase stat blocks, shared bonuses, and Melee/Magic style probability remain
  data-depth placeholders. See
  `memory-bank/source-audits/skeletal-horror-implementation-harvest-2026-07-19.md`.
- Darkan should supply hidden state machines, rolls, currencies, and reward logic; period wiki/cache evidence still establishes cutoff and client identity.

### Missing skill server behavior

Labels: `WAIT: DARKAN`, after each `DEEP GRILL`.

- Prefer stable restored mechanics for still-source-blocked Agility route values,
  Thieving success/stun/loot, Slayer assignment/reward pools, Summoning familiar
  behavior, Dungeoneering floors/rooms, and still-missing special-method hidden
  state. Agility, Farming, Construction, Prayer, and Magic core loops are shipped.

## Cross-system program queue

### Fancy and fighter boots have no art — needs owner approval

Labels: `IMPLEMENT`, blocked on the owner, 2026-07-25.

Reported in the playtest as "no icon for fancy boots (maybe not fighters boots
either)". Both boots are now registered and equippable, so they leave the bank's
"Other" group, but that is a different fix: **no sprite exists on disk.**
`STRONGHOLD_OF_SECURITY_ITEM_IMAGES` is empty and `EXTRA_ITEM_IMAGES["Fancy boots"]`
resolves to `None`, so the reported symptom is unchanged in the running add-on.

Art is not invented here. The fetch pipeline under `tools/` obtains period sprites,
and the result needs the owner's eye before it ships, so this stays blocked rather
than guessed.

The coverage test that should have caught the gap was itself fixed in the same
pass — an asset-existence test that misses a missing icon is the more important
defect, and worth a look for other families it may still be blind to.

### CS2, config, and interface readers shipped

Labels: `SOURCE AUDIT` for the client-side parity re-walk.

The disassembler exists at `tools/OpenRs2Cs2Disassembler.java` and paid for itself
immediately by recovering the GE price arithmetic (see
`source-audits/ge-offer-price-controls-2026-07-24.md`). Modes: `count`,
`dump <ids>`, `scan <opNameSubstr|*> [operand|lo-hi]`, `grepstr <needle>`.

**Caveat that will bite the next user:** Jagex renumbered the CS2 opcode table in
every build after 727, so 727 is the only build on disk that decodes symbolically.
Cross-revision confirmation has to be structural — byte length plus constant
offsets — which is how script 4112 was shown stable across all six pre-EOC builds.

`tools/query_openrs2_cache_configs.sh` now counts, dumps, and searches enums,
structs, and params from either an extracted cache or immutable disk zip. It
reuses Darkan core's exact enum/struct loaders and implements the deobfuscated
client's four param opcodes directly. Exact rev-727 fixtures pin enum 3483,
struct 0, and param 0; count probes pass across builds 652, 727, 728, 729, 736,
741, and 742. `tools/query_openrs2_interfaces.sh` now wraps Darkan core's
index-3 decoder with deterministic count, component dump, and client-label
search modes; exact rev-727 Grand Exchange fixtures and cross-build component
decodes are pinned. The next step is to re-walk only client-side
`source_blocked` rows. None of this reaches server-side mechanics, which is most
of what sits `source_blocked`.

Labels: `IMPLEMENT`, queued 2026-07-25 after the GE price-button sourcing failed.

We hold seven OpenRS2 builds at `~/Library/Caches/codex/2012scape-openrs2/`,
including rev 741 (2012-11-04), sixteen days before cutoff. We read almost none
of it: `tools/query_openrs2_cache.sh` and its definition sibling cover item and
object definitions only. This paragraph is the historical pre-tool state:
enums, structs, params, and interface definitions are now readable. See
`source-audits/ge-offer-price-controls-2026-07-24.md`.

**Why this is cheap.** The deobfuscated client at
`~/Documents/2012scape with bots/darkan-client/src/main/java/com/rs/jagex/`
already contains the decoder: `CS2Instruction.java` is a complete named opcode
enum for this revision (1,042 lines), and `CS2Script.java`, `CS2Interpreter`,
`CS2Executor` and `ScriptRunner` load and run the scripts. A **disassembler** —
linear named-opcode listing per script id — reuses that decoder and needs only a
printer. Full control-flow decompilation into `if`/`while` is a bigger job and is
usually unnecessary: reading arithmetic off a linear listing is enough.

**Why it will answer real questions.** `STORE_VARP` is opcode 929, so client
scripts write varps directly. Any interface behaviour the client computes locally
is therefore recoverable as genuine Jagex data rather than reconstruction: offer
price arithmetic, display formatting and rounding, requirement text, tooltip
thresholds, client-side gating.

**Be honest about the ceiling.** This unblocks *client-side* facts only. XP
rates, drop tables, success chances, timers, loot weights and every hidden roll
lived on a server that was never released, and that is most of what sits
`source_blocked` in the parity ledger. Do not sell this as a general parity
oracle, and do not let it reopen items that are blocked for server-side reasons.

Suggested order, highest aggregate value first:

1. ~~Extend cache search to **enums, structs and params**.~~ Shipped
   2026-08-03 as `tools/query_openrs2_cache_configs.sh`.
2. **Interface definitions**: component ids, text, hidden flags. Cheap, and it
   makes every future UI-parity question answerable.
3. The **CS2 disassembler**, then harvest the GE offer interface out of rev 741
   and settle the price-button arithmetic as the first real test.
4. Re-walk the parity ledger for items marked blocked on *client-side* grounds
   and clear the ones this now reaches. Leave server-side blocks alone.

### In-product help and mechanics reference

Labels: `SHIPPED: HELP CENTER`, `SHIPPED: DETAILS`, `QA: FABLE BLOCKED`.

- The single-source Help Center from `help-system-contract-2026-07-16.md` is
  shipped: 18 offline versioned topics, contextual `?` entry from all nine
  primary pages, shared search, All topics, related links, and history.
- `CatalogFilterBar` remains the shared Qt search seam; Help owns only its
  corpus adapter and does not duplicate contextual copy or maintain an
  independent wiki.
- The separately settled optional `Details` surface is implemented against
  live target-registry rows. It is collapsed by default, supports flat and
  grouped skill targets, shows locked requirements without selecting them,
  and bounds dense Combat text in a scrollable sheet.
- Kimi K3's taste findings and native-Anki restart proof are closed. Fable
  sign-off remains an external QA/auth gate because its mandatory fresh quota
  probe cannot read Claude Code OAuth from macOS Keychain; this is not a
  product-design gap.

### Activities, minigames, D&Ds, and reward shops

Labels: `DESIGN CLOSED`, `BREADTH IN PROGRESS`, `SOURCE AUDIT`.

- Platform seed: `memory-bank/minigames-activities-design-seed.md`.
- The horizontal breadth wave has shipped Shooting Stars, Fist of Guthix,
  Sorceress's Garden, Penguin Hide and Seek, Vinesweeper, Fight Caves,
  Stealing Creation, Barrows, Flash Powder Factory, Pyramid Plunder, and
  Werewolf Skullball, Gnome Ball, Fish Flingers, Fishing Trawler, Great Orb
  Project, Managing Miscellania, Big Top Bonanza, Trouble Brewing, Castle Wars,
  Pest Control, Varrock Museum, Barbarian Assault, and Soul Wars with
  complete mechanics, persistence, undo, UI, assets, and compact period-
  qualified data sets.
- Trouble Brewing now includes all seven three-piece naval colour sets, all six
  flags, both one-use rum teleports, Honest Jimmy's medium-clue service, and
  `The stuff` through a representative full-vat Dwarven stout recipe. The
  mature/ordinary outcomes, batch containers, XP, atomic purchase/action undo,
  selector guidance, and normalized art are live. Barley malt now has its
  authentic level-1 zero-XP range conversion, and Blandebir supplies batchable
  Ale yeast for 25 Coins per Empty pot after the established The Giant Dwarf
  Keldagrim gate. The remaining ale roster and
  Metarialus's alternate five-Ecto-token yeast route are catalog depth rather
  than unimplemented mechanics.
- Soul Wars now owns the complete twelve-beat objective match, participation,
  safe-death Combat, exact Zeal, representative charm shop, persistence,
  arbitration, cadence, undo, UI, and normalized assets. Continue with the
  already-harvested Shades of Mort'ton shared integration.
- Barbarian Assault owns the complete tutorial → ten-wave → persistent
  eight-egg Queen → four-wallet settlement loop, Runner-boots purchase,
  persistence, arbitration, cadence, undo, UI, and normalized assets. Its
  remaining armour/horn/gamble catalog and source-blocked Attacker XP multiplier
  are data depth.
- Flash Powder Factory and Pyramid Plunder are closed. Tears of Guthix and Shattered Heart remain explicit
  source-readiness skips, not design questions. Continue breadth-first with the
  next settled activity whose smallest honest entry/state/reward data set is
  already source-ready; do not stall the wave on exhaustive catalogs.
- Mage Training Arena's four room economies and complete 25-row cutoff shop are
  live, including the wand chain, Infinity equipment, Mages' book, runes,
  source art, direct purchase, persistence, and undo. Hidden room-rate and roll
  values remain registered data-depth work; replace them only through
  `source-audits/mage-training-arena-source-readiness-2026-07-21.md`.
- Harvest each remaining family for entry/run state, review cost, event
  variance, currency, rewards, reward shop, persistence, expiry, and undo.
- Include the split activity rows that the closed `gap-backlog.json` records (the parity ledger names their owning cards), bosses/instances, and wider pre-EOC reward activities. Never expose individual reward stubs before they work end to end.

### Bosses and instanced Combat

Labels: `DESIGN CLOSED 2026-07-18`, `WAIT: DARKAN`, `SOURCE AUDIT`, `DEPENDENCY: COMBAT/PRAYER/SUMMONING`.

- Design is owner-settled in `boss-instance-contract-2026-07-18.md`: authentic
  entry gates, shared session substrate, multi-enemy engaged-target rooms,
  Kiln extending Fight Caves, God Wars kill-count + ambient-aggression model
  (consuming the hawk/owl protection flags), and telegraph-as-warning for
  Jad/Har'Aken. Remaining work is per-boss harvest and implementation; bosses
  never become ordinary farm-target rows.
- The Fight Cave breadth slice now proves the persistent multi-enemy substrate:
  one visible roster, one engaged target, bounded ordinary-Combat pressure from
  unengaged enemies, safe death, sealed supplies, resume, and explicit leave.
  Reuse it for the Kiln and compatible instances; do not duplicate its session
  or pressure engine inside boss-specific code.
- **Closed 2026-08-09:** Dagannoth Kings is the first dangerous persistent
  consumer of the reusable boss-room substrate. Prime, Supreme, and Rex share
  one visible roster, Casual/Advanced targeting, ordinary Combat and Slayer,
  dangerous death, review-driven respawns, persistence, undo, a paginated
  Activities card, period sprites, and the Dragon-hatchet acquisition seam.
  Attack speed, respawn delay, and the numeric hatchet rate remain registered
  reconstructions; exhaustive king drop tables remain data depth. See
  `source-audits/dagannoth-kings-room-2026-08-09.md`.

### Acquisition and item/equipment completeness

Labels: `SOURCE AUDIT`, `DEPENDENCY`, sometimes `WAIT: DARKAN`.

- Maintain `tools/audit_item_reachability.py`; the current run finds 1,549
  actions, 2,413 reachable items, and 117 orphan inputs
  across planned skills, activities, Combat/world acquisition, Farming, and
  potion-state plumbing. Bob Barter's vial decant routes and Teplin Macagan's
  vial/flask conversions make potion dose variants known-producer cascades;
  live Farming sapling, harvest, and
  tree-root routes prevent ordinary produce from appearing as false root gaps;
  the level-23 Goat now closes the Desert-goat-horn -> dust -> Combat-potion
  chain; the ordinary Stronghold gathering route now closes Swamp toad ->
  Toad's legs -> Agility potion; Cooking's singular byproduct shape now
  correctly exposes the already-live Fish-offcuts route; the player-grown
  Willow route closes Willow branch; live Thieving loot now exposes the
  Master Farmer seed routes instead of false root gaps. See the dated audits
  for method and `activeContext.md` for the live count.
- **Closed 2026-08-09:** the seven ordinary Taverley blue-dragon-scale spawns
  now run through the established zero-XP Utility gathering route. Exact item
  identities and normalized period sprites activate the existing scale → dust
  → Weapon poison/Antifire chain without a placeholder. Reachability is now
  1,548 actions, 2,377 reachable items, 137 orphan inputs, and 148 blocked
  actions. See
  `source-audits/blue-dragon-scale-acquisition-2026-08-09.md`.
- **Tooling 2026-08-09:** use
  `python3 tools/audit_item_reachability.py --rank-roots N` to rank the
  remaining authentic root-acquisition candidates by simulated transitive
  item/action recovery. The score is prioritization evidence, never period
  source evidence. See
  `audits/item-reachability-leverage-ranking-2026-08-09.md`.
- **Closed 2026-08-09:** the three ordinary first-level Kalphite-Hive Potato
  cactus spawns now run through the established zero-XP Utility gathering
  route. Exact item identity and normalized period art activate 20 downstream
  item paths and 19 actions, including the complete Magic-potion chain.
  Reachability is now 1,549 actions, 2,397 reachable items, 124 orphan inputs,
  and 129 blocked actions. See
  `source-audits/potato-cactus-acquisition-2026-08-09.md`.
- **Closed 2026-08-09:** Tokkul is now a live inventory currency across the
  three cutoff TzHaar shops. All 23 stock rows use their period tables, the
  shops are player-buy only, and one Uncut onyx costs exactly 2,700,000 Tokkul.
  This activates 16 downstream item paths and 11 actions without a placeholder
  or new UI pattern. Reachability is now 1,549 actions, 2,413 reachable items,
  117 orphan inputs, and 118 blocked actions. See
  `source-audits/tokkul-shops-uncut-onyx-acquisition-2026-08-09.md`.
- **Closed 2026-07-20:** the period player-grown Willow route now exposes
  post-health-check branches every five era-minutes to a six-branch cap,
  accepts either Secateurs variant, awards zero pruning XP, and preserves Chop
  as the primary tree action. The live graph is now 1,344 actions, 1,999
  reachable items, 237 orphan inputs, and 249 blocked actions; see
  `source-audits/farming-willow-branch-acquisition-2026-07-20.md`.
- Close every live-but-unobtainable material through authentic drops, ground spawns, shops, claims, quests, skills, activities, or transformations. Do not seed free items or fake recipe gates.
- **Closed 2026-07-20:** canonical registry metadata now marks empty vial/flask
  containers and every vial/flask potion dose unstackable, matching the
  cache-derived runtime set and the established carried-slot model. See
  `source-audits/potion-container-stackability-correction-2026-07-20.md`.
- **Closed 2026-07-20:** Teplin Macagan now fills new six-dose flasks and
  reverses eligible partial flasks after the authentic quest gate, with exact
  dose/container conservation, direct undo, complete registered potion art,
  and native-Anki UI proof. See
  `source-audits/teplin-potion-flask-decanting-2026-07-20.md`.
- **Closed 2026-07-20:** the complete empty Potion flask chain is live:
  quest-gated level-81 Red sandstone mining with a 50-success review-day cap,
  free no-XP Robust glass conversion under Utilities, and level-89/100-XP
  Potion flask glassblowing with a held pipe. Utilities and Activities are
  distinct navigation surfaces over the shared no-XP runtime. See
  `source-audits/potion-flask-acquisition-2026-07-20.md`.
- The source-backed Woodcutting nest → empty nest → crushed nest route is repaired and regression-covered.
- Finish equipment requirements, special attacks, poison, charges/degradation, set effects, jewellery, consumables, and source-specific use actions without creating fake recipes.
- **Closed 2026-07-15:** barehand butterfly catching now ships as the distinct
  Hunter 95 action with its exact Hunter and Agility XP awards and no captured
  item. The prior XP/hour-audit gap remains useful evidence that missing method
  variants must be checked separately from item identity; see
  `memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`.

### Achievement diaries, clues, collections, and one-time content

Labels: `DEEP GRILL`, `SOURCE AUDIT`, `WAIT: DARKAN` where server state is hidden.

- Build from generic achievements and Bank Claims; add diary regions/tasks/rewards, clue step/casket state, collection tracking, one-time rewards, and their UI/undo contracts.
- **Treasure Trails — design closed 2026-07-19:**
  `memory-bank/treasure-trails-design-contract-2026-07-19.md` settles one
  step per review with type-preserving flattening (gear-check beats for emote
  steps, travel-and-dig beats for maps/coordinates, source answers for
  riddles, puzzle boxes collapsed per the Barrows precedent), authentic
  one-clue-per-tier ownership, and direct-command caskets. Remaining work is
  the per-tier harvest listed in that contract.
- **Design closed 2026-07-17:** `memory-bank/achievement-diary-item-grants-design.md`
  replaces the percentage-grant stub with the cutoff-faithful eight-family
  diary structure, Burthorpe/Taverley and Miscellaneous sets, Taskmaster
  translation, cape ladder, Completionist contract, and passive Music Log.
  Implementation remains blocked on the source catalogs listed in that file.
- **Blocked on this card:** the Ardougne cloak's Thieving bonus (Darkan gives +0.1 to the blackjack knock-out roll). Switch it on when diaries land rather than rediscovering it.

### Random events and timed world content

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Use the global 240-reviews-per-day clock for world/economy cadence only.
- Decide visibility, opt-in/interrupt behavior, expiry, missed events, rewards, persistence, and undo without adding a world map.

### Road to Restoration comparator

Labels: `DESIGN AUDIT`, `MODERN LEAD ONLY`, `NO PARITY CLAIM`.

- Use `memory-bank/source-audits/road-to-restoration-design-lessons-2026-07-17.md`
  as the queue for modern first-party critiques of Aura/Loyalty lock-in,
  DailyScape, early-game balance, combat baseline viability, GE friction, UI
  discoverability, and world/asset coherence.
- Source the 2012 system first. Then adopt, adapt, or reject the modern repair
  explicitly; never import a post-cutoff value or mechanic under the label of
  parity.

## Parked sequencing gates

### Grand Exchange

Labels: `COMPLETE`, `DESIGN LOCKED`.

- Core design is locked in `memory-bank/fake-grand-exchange-design.md`; do not re-grill it.
- NPC shops are already live. Owner decision 2026-07-19: the item-breadth
  sequencing gate is removed — GE implementation may proceed now, alongside
  the ongoing item-universe work, rather than waiting for it. Prices and
  limits for not-yet-obtainable items simply stay dormant until their items
  exist.
- **Full closure shipped 2026-07-19:** cache `exchangeable` extraction,
  the registered-item catalog intersection, period-six-slot offer/escrow
  lifecycle, confirmation gates, Ironman lockout, and save migration are
  implemented.
  The period price/buy-limit harvest now supplies 1,330 direct prices and 1,640
  limits across 1,659 registered items, with 19 ambiguous identities
  fail-closed. The bounded hidden-price
  market, stochastic fills, impact/shocks, live review ticks, and deterministic
  review undo are implemented. The top-level period interface, offer editing,
  configurable safety controls, persistent completion notice, and no-XP
  Bankstanding fallback are live. `grand-exchange-slot-count-supersession-2026-07-19.md`
  supersedes the older eight-slot/±20% clauses. See
  `source-audits/grand-exchange-interface-bankstanding-2026-07-19.md`.

### Level 1-99 time and economy balance — the XP/hour invariant

Labels: `LIVE KERNEL`, `SOURCE EXPANSION`, `DEPENDENCY: REMAINING METHODS`.

**The invariant (owner-stated 2026-07-13).** One review is one unit of game
time, so the quantity that must hold across the whole game is:

```
effective XP per review  ∝  real pre-EOC XP per hour
```

Not XP per action. AnkiScape pays per review and therefore inherits XP-per-action
unless something corrects it, but XP/hour is what Jagex actually balanced.

**LIVE, 2026-07-17.** `R = 1000` now governs source-compatible foreground
routes through `cadence_live.py`; `cadence_coverage.py` fails closed when a
handler or selectable target lacks a classification. Full provenance remains
`memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`.

**Reward-XP accounting rule (design note, 2026-07-19).** The packet's 12-B
staging (XP-multiplying reward rows hidden) closes per consumer with this
rule: a sourced XP multiplier or bonus (penance horn, volatile clay tools,
Dungeoneering reward XP, Daily Challenge bonuses) applies **after** cadence
at its authentic magnitude and charge/duration budget. Because the same item
multiplied the 2012 XP/hour too, proportionality is preserved by
construction; what must never happen is an invented magnitude or an uncharged
permanent multiplier. Each first consumer extends
`tests/test_xp_hour_parity.py` with a with/without assertion before its shop
row unhides.
`tests/test_xp_hour_parity.py` now grades live exact rates, route ordering,
residual counts, and embedded-probability behavior with no expected failures.

Before the first cadence-profile version or denominator change, add an explicit
migration/reset path for incompatible persisted residuals. The current v1
validator correctly rejects impossible credit/version state; a future version
bump must not strand a route in a repeated runtime error.

**There are TWO independent defects, and a skill can have either alone.**

| Defect | Breaks | Cause | Victims |
|---|---|---|---|
| Invented adapter | *ordering* | `0.20 + 0.72·√p` (`logic_pure/logic_pure_progression.py:42-45,404-413`) inflates rare actions | Woodcutting, Fishing (Mining directionally) |
| Unmodelled dead time | *rate* | one review per action, whatever the real wait | Hunter (traps), Thieving stalls (respawn), Combat (30s burst) |

*Legacy adapter.* Its damage scales with how rare the action is: near `p=1` the square
root is nearly the identity, but a 6.3% action becomes 38%. In RuneScape a rare
action is the signature of a **money** method — that is why it was made rare — so
the adapter promotes exactly the content the period game made unattractive to
train. This remains only in explicit flag-off behavior and source-blocked routes;
source-ready live routes no longer use it.

*Dead time.* Source-ready Hunter and gathering rows now encode their cited rate
as exact residual admission rather than one catch per review. Rows lacking a
compatible period rate remain `source_blocked`; their existing action unit is a
known evidence gap, not silently promoted to parity.

*Combat.* Live Combat now advances `6 × M` immediate ticks per successful card,
persists the encounter and attack phase between cards, and ends the review at a
kill, death, flee, or bank boundary. The old 50-tick burst exists only behind
explicit cadence rollback and in deliberately separate legacy constants; it is
not the live review conversion.

**Respawn IS the model — and the inversion it produces is real** (settled
2026-07-13, grill round 3; this reverses the earlier warning on this card).
`XP ÷ respawn` makes the level-2 vegetable stall the best XP in Thieving and the
level-75 gem stall the worst. That looked like a *reductio* against the model
until both sources were checked: 2011Scape's `respawnTicks` and the period
E.P.S. column agree to within rounding on every high-level row (table on the
Thieving card). The single-stall rates really do invert. Real players world-hop,
which is a location mechanic we cannot model and must not fake — and we do not
need to, because at the levels where the inversion bites, far better Thieving
methods are already open. Model the respawn, ship the inversion.

**Remaining deliverables:**
- Sourced XP/hour + modifier provenance for the artisan skills (Smithing, Crafting,
  Fletching, Runecrafting, Herblore, Construction, Magic, Prayer).
- Preserve source base XP throughout. The correction always rides cadence or an
  explicitly-recorded invention, **never** the XP value.
- Every rate must declare what is baked into it (urns, gauntlets, familiars,
  dropping). The F2P Mining guide quotes iron at 45k *with urns*; contract on that
  and grant urns again and you land at 54k.

### Release readiness

Labels: `PARKED` until feature closure, then `IMPLEMENT`.

- **UI asset normalization closed 2026-07-19:** all 29 top-level UI PNG
  families now share the tight-alpha small-sprite invariant, the fetch pipeline
  preserves it, and Fable plus Kimi K3 approved the cross-surface result.
  Sixty-five larger/full-frame images are explicitly outside that rule. See
  `memory-bank/audits/ui-asset-normalization-2026-07-19.md`.
- **Product disposition settled 2026-07-17:** prepare a separately named public
  derivative release under
  `public-release-lineage-and-license-2026-07-17.md`; do not upload until its
  ordered go-live gates pass.
- Obtain Wilson's written acknowledgement or license clarification; add the
  explicit compatible license, durable credits, and public attribution copy.
- Synchronize the public fork to the exact candidate; create a new AnkiWeb
  listing; replace the hard-coded `1808450369` review link; declare the original
  package conflict where supported.
- Close asset redistribution provenance, migration fixtures, manual Anki review
  QA, performance/accessibility, packaging, export/recovery, documentation, and
  post-upload verification.
- **Final Fable simplification gate:** after the complete implementation diff is
  feature-closed and verified, ask Fable exactly: “how can we simplify this? How
  can we make this entire code update as minimal and elegant as possible while
  still achieving our goals?” Apply only behavior-preserving reductions, then
  rerun the affected validation before packaging the release candidate.
- When all 25 pre-EOC skill surfaces are complete or explicitly excluded,
  publish a celebratory, interactive skill-milestone postmortem before moving on
  as though it were an ordinary card. Cover the build timeline and commit
  history; skill/action/target/item/quest/achievement totals; code, test, asset,
  provenance, documentation, migration, and archive growth; source-closed versus
  `source_blocked` or invented abstractions; major architecture changes; visual
  before/afters; bugs and near-misses; owner decisions that materially shaped
  the game; and lessons for the remaining activities/economy/release program.
  Generate the statistics from repository tools and Git at milestone time rather
  than preserving hand-maintained estimates.

## Explicitly excluded

- `EXCLUDED`: standalone transportation systems, persistent world map/player location, canoes, hot-air balloons, lodestones, and comparable transport-only content.
- `EXCLUDED`: post-cutoff and OSRS-only mechanics without independent pre-EOC proof; `fletch-javelin-construction` is the canonical rejected false positive, and the Chaos Temple Wilderness bone-offering altar (OSRS-2018) joined it during the Prayer grill.
- `EXCLUDED`: visible inert target/reward rows that cannot function end to end.
- `EXCLUDED`: wall-clock minutes for ordinary skilling actions; the card clock governs background/world/economy cadence only.

## Definition of done for any card

- Backend: pinned source audit, data, pure mechanics, storage/migration, runtime dispatch, inventory/acquisition, telemetry, undo, and focused tests.
- Frontend: shared target metadata, target UI, authentic locks, settings/equipment/inventory state, Bank/Stats/HUD/achievement effects, and Qt tests.
- Assets: item/target/material art, provenance, registry coverage, and existence tests.
- Balance: source base values preserved; Anki pacing isolated and documented.
- Verification: focused unit/integration/end-to-end coverage, full `python3 run_tests.py`, full offscreen Qt suite when UI exists, and manual Anki instructions.
- Memory: update this board and the detailed audit; preserve historical source audits instead of rewriting them as current status.
