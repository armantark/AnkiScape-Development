# Penguin Hide and Seek at the pre-EOC cutoff

Date: 2026-07-17

Status: **period structure and the complete cutoff spawn catalog are pinned;
owner-settled implementation complete.**

## Pinned evidence

The literal wikitext of `Penguin Hide and Seek`, oldid `6569778`,
`2012-11-17T23:47:37Z`, establishes:

- the ordinary weekly activity tracks ten penguin spies;
- Larry, or Chuck after `Hunt for Red Raktuber`, supplies regional hints;
- the ordinary penguins use disguises and roam, while player clans and forum
  threads commonly publish sightings and help trap them;
- `Cold War` upgrades five ordinary penguins from one point to two;
- `Hunt for Red Raktuber` adds a one-point polar-bear agent;
- `Some Like It Cold`, together with the required `Desert Treasure` progress
  and ring of visibility, adds a three-point invisible penguin;
- the resulting weekly maxima are 10, 15, 16, or 19 points according to those
  quest unlocks;
- points may be redeemed for 6,500 coins each or chosen-skill XP equal to
  `25 × current skill level × points`; and
- Larry or Chuck stores at most 50 unspent points.

Source:

- <https://runescape.wiki/w/Penguin_Hide_and_Seek?oldid=6569778>

The revision was resolved and inspected as literal wikitext with
`tools/wiki_parity.py`.

## Owner-settled AnkiScape abstraction

Penguin hunting is completely flattened. At each answered-card weekly reset,
the Activity creates the source-authentic eligible roster and exposes each
penguin's current source location directly. Selecting a roster entry abstracts
all travel and starts one atomic review action; the next successful Activity
review travels to the named location, spies that penguin, awards its points,
and marks it complete.

There are no Larry/Chuck hint deductions, broad-area searches, discovery rolls,
community-sighting mode, roaming NPCs, trapping, multiplayer simulation,
persistent player location, or transport legs. The result line names the
location and disguise so the flattened action still communicates what happened.
Inactive rosters perform no work.

The weekly roster, quest gates, point values, point cap, and redemption options
remain source-shaped. Weekly eligibility follows AnkiScape's answered-card
calendar and never the wall clock. Every successful spy and redemption remains
an atomic undoable delta.

## Breadth-one implementation closure — 2026-07-20

The live implementation uses the owner-settled flattened search loop without
dropping any mechanic:

- one answered-card week is `1,680` reviews on the shared
  `shop_market_clock`; no wall clock is consulted;
- each weekly roster contains five ordinary one-point locations and five
  ordinary locations upgraded to two points by `Cold War`;
- `Hunt for Red Raktuber` adds the rotating one-point polar-bear well;
- `Some Like It Cold`, started `Desert Treasure`, and a carried or equipped
  Ring of visibility add the three-point invisible penguin;
- the player selects any unspotted roster entry, one successful Activity
  review spies exactly that entry, and review undo restores the selection,
  points, weekly progress, telemetry, and world clock atomically;
- points clamp at 50 without preventing the selected spy from being marked;
  all held points redeem directly for either `6,500 × points` coins or
  `25 × current level × points` XP in a trainable skill; and
- selection is a saved policy change, while each redemption has its own Anki
  direct-action undo entry.

The activity registry, save migration v56, cadence coverage, runtime dispatch,
paginated Activities card, dark/light-safe period icon, and
pure/integration/real-Qt coverage are live.

Current Darkan reconstruction corroborates the ten-spy count, `Cold War`
point upgrade, polar-bear completion gate, 50-point cap, all-points redemption,
`6,500 × points` coins, and `25 × level × points` XP:

- `darkan-world-server` commit
  `758b41e8c16f1ad424b98aa5812e8f9d06dab541`,
  `src/main/java/com/rs/game/content/dnds/penguins/PenguinHASController.kt`;
- commit `61c5ab917ce0632088d74be698bbdd4a1e57cc34`,
  `src/main/java/com/rs/game/content/items/Lamps.java:189-205`; and
- commit `166fced5187dd6f2539d52e23bf21a9ab92660f7`,
  `src/main/java/com/rs/game/content/world/areas/ardougne/npcs/east_ardougne/Larry.kt:130-151`.

Darkan currently gates the base activity behind completed `Cold War`, which
conflicts with the pinned pre-cutoff page and the newer owner-settled entry-gate
ledger. AnkiScape therefore keeps the base ten-point roster available and uses
`Cold War` only for the five two-point upgrades. Darkan is reconstruction
evidence here, not authority over the pinned period page.

Asset provenance:

- `activityicons/penguin_hide_and_seek.png` is the tight-alpha normalized
  `Rock (Penguin Hide and Seek).png`, timestamped `2010-10-13T03:24:23Z` in
  `assets_provenance.json` and fetched through
  `tools/fetch_penguin_hide_and_seek_assets.py` with the pre-EOC cutoff.

## Remaining data depth

- Recover a period-lineage server implementation if one survives; current
  Darkan corroboration remains reconstruction evidence and carries the base
  entry-gate conflict recorded above.

## Spawn-catalog depth closure — 2026-08-08

`Penguin Hide and Seek/Spawn locations` oldid `6566231`, timestamp
`2012-11-17T15:09:05Z`, states that the cutoff pool contains 67 ordinary spawn
locations and six polar-bear locations. Its literal tables enumerate 34
one-point location/disguise pairs and 33 two-point pairs. The live tuples now
match every heading in that oldid, in source order, while retaining the stable
IDs of all twelve breadth rows so active selections and spotted-state history
remain valid.

The weekly mechanic is unchanged: five rows rotate from each ordinary tier,
the Cold War upgrade controls their live point values, and the invisible
penguin rotates through the complete 34-location one-point pool. A source-
comparison check matches all 67 live pairs to the oldid and proves all IDs are
unique; the runtime regression walks 34 answered-card weeks and proves every
ordinary row and invisible location becomes reachable.

Location detail remains player-facing flavour under the settled flattened
model. Source area requirements, map coordinates, travel, roaming, trapping,
and community sightings do not become gameplay gates. No schema migration,
new UI structure, placeholder, or owner design decision is required.

Source:

- <https://runescape.wiki/w/Penguin_Hide_and_Seek/Spawn_locations?oldid=6566231>

Focused plain verification passes 715 tests. Sixteen isolated real offscreen-Qt
Penguin, undo, integration, UI, and asset paths pass. Full discovery passes
3,871 tests in both lanes: plain records 3,392 ordinary passes and 479 expected
environment skips; real offscreen Qt records 3,868 ordinary passes and 3
intentional skips. Documentation audits 520 Markdown and 431 HTML files; the
test-quality audit reports zero hard issues across 3,837 tests in 176 files.
Compilation, JSON, diff, asset-normalization, reachability, and worktree audits
pass. Reachability remains at 1,499 actions, 2,232 reachable items, 169 orphan
inputs, and 189 blocked actions.
