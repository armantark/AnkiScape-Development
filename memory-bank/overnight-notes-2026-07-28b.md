# Running notes — goal session resumed 2026-07-28 (afternoon)

Autonomous mode: these are the running notes; one results artifact comes at the
end. The goal is the re-issued breadth-first mechanical-completion standing goal.

## Where the board stands at session start

Seven families landed since the tranche file was written: Shattered Heart,
Troll Invasion, Mage Training Arena, Temple Trekking, Dominion Tower,
Gnome Restaurant, Mobilising Armies. The tranche board is updated and
committed (`90ff8fe8`). Remaining below breadth one: **Dungeoneering** and
**Conquest**. Bork still waits on Hunt for Surok (miniquest ledger — design
fork 3.23, owner has not answered).

## In flight (three background Sol agents)

1. **Cross-lineage verification** of Temple Trekking, Mobilising Armies,
   Gnome Restaurant, Dominion Tower — execution-driven, findings to scratchpad.
   Programme-mandated (Sol catches what Claude passes miss).
2. **Dungeoneering harvest** — pinning from Darkan's dungeoneering package,
   preferring the restoration thread's source-qualified commits (`e1cf61bf2`
   restored floor progression — exactly the floor-XP curve and death
   coefficient the AnkiScape substrate is parked on). Deliverable:
   `source-audits/dungeoneering-harvest-2026-07-28.md`.
3. **Conquest harvest** — units, commands, setup points, turn structure,
   rating, commendation payouts. Deliverable:
   `source-audits/conquest-harvest-2026-07-28.md`.

## Cross-thread note (Darkan restoration)

The Darkan thread has already restored source-qualified Dungeoneering floor
progression (`e1cf61bf2` in their repo). We consume it rather than re-deriving;
our harvest audit will carry a "what the restoration thread already
source-qualified" section so neither thread duplicates the other. Nothing we
do writes into their checkout.

## Dungeoneering implementation shape (for the briefs, once harvest lands)

The substrate is further along than the tranche board implied:
`data/dungeoneering_data.py` (sourced themes, sizes, complexities, bind ladder,
kinship classes/tier costs, Frozen bosses, door families, starter chains, Coal
bag row) and `logic/dungeoneering_logic.py` (floor gating, prestige, payout
order, replay substitution, seeded starter graph, room/death reducers) already
exist with tests. Parked only on the floor-XP curve and death coefficient.

Phases:
- **A — skill activation.** Flip `surface_state` from `planned` (registry line
  `core/skill_registry.py:305`); extend the XP curve past 99 to 120 for
  Dungeoneering only (`core/constants.py` EXP_TABLE ends at 13034431); release
  `pending_skill_exp_rewards` parked Dungeoneering XP; skillcape row and the
  25-skill Max gate then clear by construction (GOAL-BLOCKED blockers 2 and 3).
- **B — floor runtime.** Entry surface (theme/size/complexity/kinship/binds),
  persistent floor session, one room beat per review, checkpoints per the
  three-tier choice architecture, death/leave, completion payout with the
  harvested curve, prestige ledger, token wallet.
- **C — economy and rewards.** Smuggler, in-floor resource + quarantined
  Herblore chains, bind offers via the contextual action row, reward trader
  with functional Coal bag (Mining/Smithing integration), assets, cadence,
  telemetry, migrations, UI card, tests.

One agent per phase, serial merges, execution-verified — per the
two-family-briefs lesson, never two families or two heavy phases in one brief.

## Owner steer mid-session

Use dynamic workflows for orchestration (session workflow cap raised to 50
agents). Applied from the art sweep onward; the three already-running agents
were left to finish.

## Art sweep tranche 2 — running as a dynamic workflow

`tools/reresearch_period_art.py` now owns the per-asset protocol (correct
endpoint, full upload history, strictly-pre-2012-11-20 revision, sha1 of the
actually-served bytes, migration-glitch fallback across same-sha revision
URLs, shared write_png normalization, resumable JSONL rows). Smoke-tested:
Air battlestaff recovered through the fallback; Duel arena honestly absent
under its guessed title. The workflow: 30 Luna research batches (100 assets
each) with a script-side suspicion gate that requeues to Sol, a Sol title-hunt
over every absence claim, a 30-sample adversarial audit with a full re-hunt
trigger, one retry pass, and a single Sol apply step that owns
`assets_provenance.json`. Git stays with this session.

## Conquest research arriving

The harvest agent's sub-worker returned pinned command/unit tables, the
rating and commendation rules, and a corrections list (Knight range 1, not
the copy-pasted infobox 4; combat req 40; no combat triangle). Placeholder
candidates already visible: squad budget (unsourced 1000 vs implied 800),
board size (20×20 vs 22×22), rating formula, command-point income, ratio
curve. Parent agent still compiling the audit file.

## Cross-lineage verification returned: 13 defects, no family clean

Report: `scratchpad/sol-verification-2026-07-28.md` (session scratchpad).
Temple Trekking 1 (unregistered three-charge Druid pouch), Mobilising Armies 1
(Explore counts toward rank against the sourced exclusion), Gnome Restaurant 2
(meal granted at the first twelve-point threshold; order acceptance steals a
live activity session and the next save round-trip deletes the stolen trek),
Dominion Tower 9 (leavable uncleared matches, inert No Familiar, deleted
instead of banked armour, No Food persisting into real auto-eat config,
shot/hit weapons drained as ticks, one global Xp-book factor, per-roll instead
of per-box reward caps, unregistered three-roll constant, panel re-deriving
claimability). The fourth consecutive Sol pass to find real shipped bugs that
Claude passes cleared — the routing rule stands.

Fix-and-reverify workflow `wf_e33dcde2-bf5` is running: one Sol fixer per
family on disjoint files, independent execution reverification, refix loop
capped at two extra rounds. Git stays with this session; full-suite runs and
commits happen here after the workflow returns.

## Dungeoneering harvest landed; implementation running

`source-audits/dungeoneering-harvest-2026-07-28.md` (commit `fb3aa002`) pins
all 60 floors, complexities, prestige, tokens, binds, Kinship costs, Frozen
rooms/bosses/doors/keys, the 42-row reward catalog, Smuggler bands and starter
chains, and names nine bounded placeholder candidates. Notable: nobody has the
floor-XP curve or death coefficient — the restoration thread didn't qualify
them either, and the period death record (additive, 15-death cap, 4-70%)
contradicts Darkan's multiplicative rule. Both ship as registered placeholders
under the amended goal. The audit also flags that shipped
`resolve_floor_replay_pure` uses nearest-lower-first while restored Darkan
uses lowest-unticked-lower-first.

Workflow `wf_f088bd72-27f` is implementing: Phase A (25th trainable skill:
registry flip, 120 curve, parked-XP release, cape and Max gate by
construction — clears GOAL-BLOCKED blockers 2 and 3) → B1 (floor runtime
core) → B2 (in-floor economy), Sol xhigh implementers, execution verifiers,
refix loops, phase gates that stop the workflow rather than build on an
unverified phase. Phase C (kinship tiers, reward trader with the functional
Coal bag, period assets) is deliberately held until the art workflow's apply
stage releases `assets_provenance.json` — one writer per file.

## Pass 4 arrived (owner, evening)

Notes: `~/Downloads/ankiscape notes.rtfd`. Nine directives recorded as
design-thread section 4.13 (commit `512ad5bf`). Highlights: the merged
D&D-Farming badge is overruled back to two badges left of the XP bar; a
review-counted event-log drawer; right-click D&D favouriting; Treasure Trails
start moves to a Bank right-click; the Arachnophagia achievement fired on a
mackerel cook (screenshot-confirmed — the gnome-cooking predicate is wrong);
plus overlay-over-footnotes, equipment points display, missing cooking
options, and lag investigations.

Implementation runs as workflow `wf_ab318b58-eae` inside the guarded worktree
`ankiscape_worktrees/pass4-fixes` (branch `pass4/fixes`) so the concurrent
Dungeoneering and family-fix workflows keep sole ownership of the canonical
checkout. Merge is rebase-based after the main-branch workflows land, per the
family-merges convention.

## Done this session

- Dungeoneering shipped to A/B1/B2 (`0ac64a57`): 25th trainable skill, 120
  curve, parked-XP release, capes and Max gate by construction, the full
  Frozen starter floor loop, binds with sale-invalidated offers, Smuggler,
  both starter chains. GOAL-BLOCKED is down to the one diary-count clause.
- Pass 4 rebase-merged to main (`9c988b33`), event-log schema renumbered to
  v101; both lanes green at 3,552 tests.
- Dungeoneering phase C (kinship, trader with functional Coal bag, assets)
  running on main as `wf_aad2b78c-a75`; Conquest breadth one running in the
  `conquest` worktree (branch `conquest/breadth-one`, schema 102) as
  `wf_b1e6a35a-735`. The XP-bar sweep agent is still enumerating.

- Pass 4 implemented and verified clean on `pass4/fixes` (`24059e7e` in the
  guarded worktree), 12-agent workflow, one refix round (a hidden 200-event
  retention cap violated the expandable-indefinitely directive and is gone).
  Answers for the owner: the "missing" cooking options were build staleness
  plus tree position — the twenty gnome rows are the four collapsed groups at
  the bottom of the Cooking tree, and Anki must restart to load the merged
  code; Arachnophagia was the generated diary task's skill-level predicate,
  now a ledger-action on a real sourced Spider on a stick target. Merge onto
  main waits for the Dungeoneering workflow, per the rebase convention.

- Art tranche 2 closed (`495b48af`): 2,384 pre-EOC revisions pinned by the
  56-agent workflow, 356 evidence-backed absences, 243 honest unresolved; the
  wrong-variant desert lizard reverted by hand, the green dragon re-pinned to
  its renamed period title.

- All thirteen cross-lineage findings fixed and committed (`782cc06b`), 16-agent
  workflow, three families verified clean by execution; the one issue its final
  pass left open (staff charges counting attack opportunities) closed by hand:
  the engine now reports landed hits per slice and hit-denominated charges
  consume that count, with a pinned-seed mixed hit/miss regression.

- Tranche board refresh (`90ff8fe8`).
- Running notes started (`7db64576`).
- Period-art research tool committed and smoke-tested.
- Art tranche-2 workflow launched (research phase running).
