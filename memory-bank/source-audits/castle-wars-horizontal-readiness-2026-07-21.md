# Castle Wars horizontal readiness — 2026-07-21

Status: **source-ready for a mechanic-complete horizontal slice.** Hidden
opponent and hybrid-helm rolls remain data depth.

## Authority

The owning adaptation is
`source-audits/competitive-tier-adaptations-2026-07-18.md:53-55`. It settles a
team-score race with flag, barricade, repair, and live defensive-Combat duties.

The nearest useful cutoff article is RuneScape Wiki `Castle Wars`, oldid
`6528924`, timestamp `2012-11-03T13:56:56Z`:

- <https://runescape.wiki/w/Castle_Wars?oldid=6528924>

The literal wikitext proves:

- members-only entry with no skill-level requirement;
- one twenty-minute capture-the-flag match, safe death, and in-match respawn;
- two tickets for a win, one for a draw, and zero for a loss;
- a minimum ten minutes of participation for tickets and games-played credit;
- no carried food, helmets, or capes, but free in-arena bandages and tools;
- bandages restore ten percent maximum LP, cure poison, and restore about
  thirty percent run energy;
- one point per enemy standard returned to the player's own safe standard;
- barricades, catapult rocks, climbing ropes, pickaxes, tinderboxes, buckets,
  toolkits, explosive potions, collapsible tunnels, and repairable catapults;
- a ten-barricade team cap;
- ordinary ammunition and runes remain the player's supplies;
- direct early exit and automatic replacement from the waiting room;
- exact ticket-shop costs and full-ticket-value resale; and
- 500, 1,000, and 5,000-game cape milestones plus most-capture and most-kill
  capes.

OpenRS2 cache revision 742, dated `2012-11-07`, proves the representative item
identities and inventory options:

| Item | ID | Cutoff option |
|---|---:|---|
| Castle wars ticket | `4067` | Drop |
| Basic decorative platebody | `4069` | Wear |
| Basic decorative platelegs | `4070` | Wear |
| Basic decorative shield | `4072` | Wield |
| Ballista base / stack / bow / chamber / ammo | `18710`–`18714` | Destroy |
| Saradomin halo | `18745` | Wear |
| Castle wars hobbyist cape | `24162` | Wear |
| Castlewars chinchompa | `21531` | Deploy-proximity / Deploy-timer |

The immutable cache root is
`~/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache`.

## Review-native translation

The source's twenty-minute match becomes ten consequential review beats. This
is a disclosed event-scale translation: each beat represents two minutes of
the match, never two minutes of wall-clock or global answered-card time. The
literal ten-minute participation rule becomes five completed beats before a
match can award tickets or games-played credit.

Each beat resolves exactly one duty:

1. `Capture` advances or completes a standard run and can score one point.
2. `Defend` runs a live six-tick Combat slice against one period-shaped raider.
3. `Barricade` deploys or maintains the sourced ten-piece defensive cap.
4. `Repair` restores the gate/catapult pressure state with the free toolkit.
5. `Catapult` uses a free arena rock to pressure the opposing team.
6. `Support` uses a free bandage when needed, otherwise reinforces the weakest
   useful duty.

Casual mode selects the current bottleneck. Advanced mode saves one fixed duty
and a Saradomin, Zamorak, or Guthix-balanced team preference. The simulated
competent crowd advances the opposing score and both teams' non-player duties;
it never grants player Combat XP, tickets, items, or personal milestone credit.

Player death is safe: the encounter resets inside the same match, no Bank,
grave, Death Office, or item-loss path runs, and the review is still spent.
Leaving early forfeits the unresolved match and its tickets. Review undo owns
the complete duty, Combat, score, reward, and terminal-state boundary; direct
entry, policy, shop, resale, and leave actions use direct-action undo.

## Smallest complete reward graph

The horizontal shop ships one representative from every mechanically distinct
reward family rather than the exhaustive catalog:

| Family | Representative cutoff rows | Mechanic exercised |
|---|---|---|
| Decorative set | Basic body `8`, legs `6`, shield `6` tickets | one/two/three-piece `4%`/`6%`/`10%` enemy damage bonus |
| Prayer equipment | Saradomin halo `300` tickets | reduced defensive-Prayer drain |
| Match milestone | Hobbyist cape `2` tickets after `500` credited games | long-horizon match gate |
| Siege equipment | four ballista parts `2` each; `100` ammo for `4` | assemble, deploy, fire, and consume match-only ammo |
| Match consumable | three Castlewars chinchompas for `1` ticket | match-only proximity/timer deployment |

All purchased rewards remain non-tradeable and sell back for their full ticket
cost. The complete decorative tiers, alternate halos/team cosmetics, three
match-potion sets, remaining milestone capes, and equivalent colour/style
variants are catalog depth after breadth level one. Match-only item use is live
through the representative ballista/ammunition and chinchompa rows; potion-dose
families add catalog breadth to the existing Combat boost mechanic rather than
a new Castle Wars state transition.

The halo revision's affected-prayer table is more precise than its introductory
"defensive prayers" sentence. The one-third reduction applies to Burst,
Superhuman, and Ultimate Strength; Sharp, Hawk, and Eagle Eye; Mystic Will,
Lore, and Might; Chivalry, Piety, Augury, and Rigour; all four Sap curses; all
seven Leech curses; and Turmoil. It does not apply to protection overheads.

The random Hybrid-armour-helm interface is `source_blocked` on its exact win
chance. It must not silently become a guaranteed prize. Exact crowd score,
capture, sabotage, and incoming-pressure rolls are also hidden; keep their
bounded constants isolated and labeled `abstraction/source-duration` so later
evidence can replace them without changing save or UI contracts.

## Required implementation boundary

- Backend: data, persistent ten-beat session, all six duties, safe combat
  respawn, ticket settlement, match threshold, representative shop and resale,
  equipment effects, activity arbitration, cadence, telemetry, and both undo
  boundaries.
- Frontend: one compact paginated Activities card with team/mode/duty setup,
  live score/beat/LP/defence state, explicit leave, and a separate compact shop
  sheet. No nested activity-list scroll window.
- Assets: one cutoff activity image plus every visible representative reward,
  alpha-normalized and provenance-tracked.
- Verification: pure state transitions, live Combat and safe death, entry
  restrictions, ticket thresholds, shop/resale, equipment effects, migration,
  runtime/undo, activity arbitration, asset/reachability, real offscreen Qt,
  and native Anki.

No owner-facing design fork remains in this family.
