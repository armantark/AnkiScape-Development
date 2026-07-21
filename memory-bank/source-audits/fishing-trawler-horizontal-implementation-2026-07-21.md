# Fishing Trawler horizontal implementation

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Period evidence

The implementation reproduces the literal wikitext from RuneScape Wiki
`Fishing Trawler` oldid `6288357`, timestamp
`2012-09-24T04:51:16Z`:

<https://runescape.wiki/w/Fishing_Trawler?oldid=6288357>

That revision establishes:

- level 15 Fishing entry;
- a safe twelve-minute team trip at Port Khazard;
- consumable Swamp paste for leaks, consumable Rope for a torn net, and
  reusable Bailing buckets for water;
- a shared water/sinking failure state and zero haul after sinking;
- successful catches shaped by Fishing level, a deposit box beside the net,
  and Fishing XP equal to 40% of the catch's ordinary Fishing XP;
- the period reward list from Raw tuna through Raw manta ray, with Sea turtles
  at level 79 and Manta rays at level 81; and
- Khazard General Store as the source-near supplier for all three duty items.

The current structured shop corpus independently supplies the exact live rows:
Rope `954` for 18 coins, Bailing bucket `583` for 10 coins, and Swamp paste
`1941` for 31 coins. The canonical item registry correction made Rope
non-stackable and preserved its shop/cache identity.

The high-level catch XP inputs have separate cutoff evidence:

- `Raw sea turtle` oldid `6454456`,
  `2012-10-22T20:40:10Z`: level 79 and 38 ordinary Fishing XP;
  <https://runescape.wiki/w/Raw_sea_turtle?oldid=6454456>
- `Manta ray` oldid `6487890`, `2012-10-28T07:34:21Z`: level 81 and
  46 ordinary Fishing XP;
  <https://runescape.wiki/w/Manta_ray?oldid=6487890>

The smaller Tuna/Lobster/Swordfish/Shark ordinary rows come from the existing
2011Scape Fishing table in `fishing_data.py`; Raw anchovies is the smallest
already-live saltwater row at the source's level-15 entry gate.

## Disclosed AnkiScape translation

The source does not expose an exact per-trip pressure-event count, leak
distribution, crew contribution distribution, catch distribution, or hidden
haul roll. Per the owner-settled event-scaled contract, the wall-clock trip is
compressed into ten consequential review events in
`fishing_trawler_data.py`. This count and the bounded pressure values are
`provisional/oldid-6288357`, not historical claims.

Each successful review resolves atomically:

1. the next leak/net/water pressure event;
2. one fixed competent-public-crew water offset; and
3. one useful player duty selected by Casual urgency or the saved Advanced
   priority.

The source-authentic item semantics survive the compression: patching one leak
uses ten paste, repairing the net uses one Rope, and bailing requires but does
not consume a bucket. Casual survives the disclosed ten-event baseline with
the default 60 paste / 4 Rope / 1 bucket pack. A supply-starved or aggressively
mis-prioritised trip can sink for no haul.

The activity-specific pack honors the owner-approved stackability distinction:
Swamp paste occupies one stackable slot, while each Rope and bucket occupies
one non-stackable slot, capped at 28. Entering reserves the chosen available
supplies from the bank; leaving, sinking, or docking returns every unused item.

Success directly banks 8-14 level-eligible fish and returns exactly 40% of
their ordinary Fishing XP. The haul's precise species/count distribution is a
disclosed bounded horizontal dataset. The period Tiger shark row remains
`source_blocked` because this pass did not recover its exact eligibility and
ordinary-XP identity; it is data-depth work, not a missing mechanic.

## Live product surface

- `fishing_trawler_data.py`: period IDs, catch/XP rows, activity registration,
  default pack, and the ten-event disclosed schedule.
- `fishing_trawler_logic.py`: entry, pack reservation/capacity, policies,
  pressure/duties, sinking, haul/XP, persistence, leave, and view projection.
- `runtime_actions.py` and `__init__.py`: review dispatch, XP/telemetry,
  whole-answer undo, direct-action undo, save, refresh, and terminal stop.
- `storage_pure.py`: schema 65 defaults, migration, sanitization, and persistent
  activity arbitration.
- `ui.py`: compact paginated Activities card with a visible level gate,
  docked policy/pack plan, at-sea risk state, and confirmed leave.
- `activityicons/fishing_trawler.png`: normalized pre-cutoff art fetched from a
  `2012-06-17T23:02:04Z` file revision and recorded in
  `assets_provenance.json`.

Opus reviewed both rendered states because Fable is on owner-requested reserve.
The reproduced findings were fixed: boarding now atomically persists visible
plan edits; lock copy is visible without a disabled-button tooltip; dead plan
controls are hidden at sea; bucket pluralization is correct; and water/status
legibility is stronger. Kimi K3 was not called because its required fresh
quota probe lacked the rolling window; the guardrail was not bypassed.

## Explicit omissions

- No wall clock, crew actors, crew selector, background loop, manual catch
  claim, or additional review for banking exists.
- No exact historical event count, leak distribution, catch distribution, or
  Tiger shark row is claimed.
- No Dungeoneering fish were added; they remain owned by the future
  Dungeoneering session and temporary inventory.
- No new owner-design gap surfaced.

## Verification

Focused pure, migration, registry, reachability, integration/undo, asset, and
real offscreen Qt tests protect the complete loop. The first full Qt discovery
found one stale exhaustive Minigames-set assertion and, independently, the
native Anki pass exposed that the locked Trawler row could not open its visible
gate card. The catalog oracle was updated and the row now follows the existing
Gnome Ball/Skullball inspectable-while-locked pattern; both failures have direct
regression coverage.

Final closure evidence:

- `python3 run_tests.py`: 2,172 passed with 285 expected non-Qt environment
  skips;
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover -s
  tests -q`: 2,172 passed with one intentional platform skip;
- a fully quit and freshly relaunched native Anki process opened exactly one
  AnkiScape menu, showed the paginated Minigames page, and opened the level-14
  Trawler card with its visible level-15 gate without mutating training or the
  save; and
- documentation, test-quality, syntax, JSON, reachability, asset-normalization,
  diff, and worktree-safety gates passed.

Published results:
`memory-bank/status-updates/fishing-trawler-horizontal-results-2026-07-21.html`;
mobile copy: <https://t2fu1j1wdxe1.postplan.dev>.
