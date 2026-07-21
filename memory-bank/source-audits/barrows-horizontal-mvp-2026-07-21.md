# Barrows horizontal-MVP harvest

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **source-ready breadth slice implemented; exhaustive equipment catalog
and rare chest rows remain depth work.**

## Authority and pinned revisions

- Owner-settled review-native contract:
  `memory-bank/source-audits/barrows-tunnel-session-2026-07-17.md`.
- RuneScape Wiki `Barrows`, oldid `6555680`,
  `2012-11-14T21:42:58Z`.
- RuneScape Wiki `Barrows/Rewards`, oldid `5250545`,
  `2012-02-13T08:40:42Z`.
- RuneScape Wiki `Template:Barrows repair`, oldid `6555466`,
  `2012-11-14T17:27:38Z`.
- RuneScape Wiki `Barrows equipment`, revision at
  `2012-09-04T23:12:06Z`.
- Brother pages: `Ahrim the Blighted` oldid `6451174`
  (`2012-10-21T21:44:23Z`), `Dharok the Wretched` oldid `5976663`
  (`2012-07-22T15:20:46Z`), `Guthan the Infested` oldid `6303626`
  (`2012-09-27T06:13:20Z`), `Karil the Tainted` oldid `6297274`
  (`2012-09-25T21:31:08Z`), `Torag the Corrupted` oldid `5848032`
  (`2012-06-27T15:06:16Z`), `Verac the Defiled` oldid `6242041`
  (`2012-09-13T16:04:12Z`), and `Akrisae the Doomed` oldid `6274040`
  (`2012-09-20T22:57:31Z`).
- Tunnel-creature pages: `Crypt rat` oldid `6351271`
  (`2012-10-05T13:56:19Z`), `Bloodworm` oldid `5795002`
  (`2012-06-21T10:19:28Z`), `Crypt spider` oldid `5796016`
  (`2012-06-21T10:42:56Z`), `Giant crypt rat` oldid `6177521`
  (`2012-09-01T20:00:36Z`), and `Giant crypt spider` oldid `6017225`
  (`2012-07-31T06:21:37Z`). The period `Barrows` revision itself lists the
  level-77 Skeleton and all six tunnel species; its detailed Skeleton stats are
  supplied by Darkan because no distinct pre-cutoff Skeleton subpage resolves.
- Darkan world-server commit `236dafb581db522038446bd463536d6ea6e7de4e`:
  `src/main/java/com/rs/game/content/minigames/barrows/BarrowsController.java`
  and the restored brother combat handlers.
- Darkan cache-rev-742 exports:
  `developer-information/itemList.txt`, `itemListCS2.txt`,
  `npcListBonuses.txt`, and `structs.txt`.

The wiki proves the player-visible layout, persistence, brothers, equipment,
and reward shape. Darkan supplies the server-side chest formula and prayer
drain. Cache revision 742 independently pins the cutoff item identities,
bonuses, requirements, attack speeds, and condition names; it is not used to
claim a server probability.

## Period mechanics enabled

- Six original brothers are available. Akrisae joins after Ritual of the
  Mahjarrat and shares the Barrows family without replacing an original brother.
- One original brother is hidden below ground. The other available brothers
  are fought at their mounds before entering a persisted three-by-three tunnel.
- Each run starts at a random outer corner, removes one perimeter connection,
  and opens one randomly chosen central-room connection. The resulting graph
  remains connected and has one usable central door.
- Leaving before the chest suspends the exact consequential run. An interrupted
  brother returns at full lifepoints; an interrupted crypt creature preserves
  its lifepoints. Inactive runs never advance.
- One successful review advances a door and its attached encounter through the
  live six-tick Combat reducer. Casual follows the shortest revealed route;
  Advanced chooses the next mound and currently usable door.
- The central-door puzzle is narrated and resolves automatically, as the owner
  contract requires. There is no invented answer UI or failure roll.
- Dangerous death uses ordinary unsafe Combat death and loses the unfinished
  run. Familiars cannot enter; pets remain allowed.
- Prayer drain is exactly `80 + 10 × brothers slain` points per ten seconds.
  A residual carries the fractional six-tick review amount without consulting
  the wall clock.
- The six original brother effects ship: Dharok missing-lifepoints damage,
  Guthan healing, Karil Agility drain, Torag run-energy drain, Ahrim Strength
  drain, and Verac's armour/prayer-defying exchange. Akrisae rotates his
  protected combat class after each 150 damage.
- AnkiScape intentionally has no continuously simulated run-energy bar. The
  shared run-energy contract stores only credit against the next moving trip,
  which is also where period food restoration lands. Torag therefore removes
  up to four percentage points from that same bounded credit; at zero his
  special is a truthful no-op instead of inventing a second energy substrate.
- Reward potential is `110 × brothers + 73 × tunnel creatures`, capped at
  `1,012`. Roll count is `clamp(brothers + 1, 1, 7)`, and equipment denominator
  is `clamp(450 - 58 × brothers, 73, 450)`.
- The horizontal ordinary ladder includes Mind, Chaos, Death, and Blood runes,
  bolt racks, and the coin fallback with Darkan's exact thresholds, weights,
  and quantity ranges.
- Darkan's reward loop gates its equipment roll with the absolute brother
  array index for that loop iteration. The period page instead states that
  equipment chance improves with the number of brothers killed and permits
  early looting; the app therefore makes the first `brothers slain` rolls
  equipment-eligible without tying eligibility to which named brother was
  killed. This is an explicit correction of an emulator indexing defect, not
  a newly invented chance.
- Casual kills the waiting brother and claims the chest automatically.
  Advanced may claim early at the central chest with the resulting reduced
  brother count and equipment chance.

## Equipment and repair substrate

One representative weapon per brother exercises every condition and reward
mechanic without pretending that the remaining armour catalog is complete:

| brother | weapon | base item | conditioned items |
|---|---|---:|---|
| Ahrim | Ahrim's staff | `4710` | `4862–4866` |
| Dharok | Dharok's greataxe | `4718` | `4886–4890` |
| Guthan | Guthan's warspear | `4726` | `4910–4914` |
| Karil | Karil's crossbow | `4734` | `4934–4938` |
| Torag | Torag's hammers | `4747` | `4958–4962` |
| Verac | Verac's flail | `4755` | `4982–4986` |
| Akrisae | Akrisae's war mace | `21744` | `21746–21750` |

Each weapon has `90,000` combat ticks of condition and transitions from the
fully repaired unnumbered identity through `100`, `75`, `50`, `25`, and `0`.
Cache revision 742's client-facing CS2 export names the first degraded tier
`100`, while the server-value export calls that same item `(deg)`; the shared
value table aliases those identities so unsafe-death keep selection preserves
the real store value.

The existing cutoff Grand Exchange harvester was regenerated after registering
the weapons. RuneScape Wiki's period aggregate buy-limit table, oldid
`6457777` (`2012-10-23T03:28:03Z`), supplies limits of `10` for every full and
broken representative weapon except Karil's crossbow, whose period limit is
`1`. Six full weapons also resolve exact dated pre-cutoff guide prices; Torag's
hammers correctly retains the cache-value fallback while still receiving its
period limit.
The shared per-copy equipment ledger now accepts both Fist-of-Guthix 20% bands
and Barrows 25% bands. A dangerous death moves equipped Barrows gear to `0`.

Bob's UI action repairs one banked copy instantly. The weapon's `100,000` coin
full-repair price is prorated by missing condition, preserves the instance ID,
and changes the flat inventory identity atomically. This is an NPC maintenance
action, not review progress.

## Explicit bounded abstractions

- One review summarizes six live combat ticks. A door transition and the
  encounter it reveals are one atomic review beat.
- Tunnel doors without the hidden-brother roll attach one uniformly selected
  sourced crypt creature. This gives the sourced creature pool a complete
  review-native path without inventing a spatial population simulation.
- Verac's one-third Defiler exchange temporarily removes protection-prayer
  selection and makes the attack effectively certain, reproducing the sourced
  armour/prayer bypass in the shared aggregate Combat reducer.
- Akrisae begins by protecting from melee and rotates melee → ranged → magic
  after each crossed 150-damage boundary. Casual does not add a separate style
  dialog; the ordinary Combat policy remains the source of the player's style.

## Deferred depth, not missing mechanics

- The other twenty-one armour pieces are catalog depth. Adding them extends the
  already-live brother-specific reward, condition, equipment, death, trade, and
  repair paths without adding a mechanic.
- Half keys and the dragon med helm are rare ordinary-catalog depth. The
  horizontal ladder already proves thresholded ordinary rolls and fallback.
- Morytania hard-task prayer halving and doubled rune quantities remain blocked
  on the Achievement Diary reward substrate rather than being approximated.
- Exact crypt-creature spatial frequency, every brother animation, and every
  dialogue line are presentation/data depth.

## Asset provenance

`tools/fetch_barrows_assets.py` writes one activity icon and seven representative
weapon sprites through the shared alpha-cropping normalizer and records each
revision in `assets_provenance.json`. The historical file lookup is attempted
first. Where a 2005-era item image has no wiki file-history entry before the
cutoff, the current exact item sprite is used only as visual art; it supplies no
mechanic or item identity. All eight files have tight alpha bounds.

## Regression map

- `tests/test_barrows.py` covers registration, all generated topology
  combinations, Ritual unlock, Advanced atomic selection and manual-chest
  review gating, brother reset versus creature preservation, six-tick
  dangerous combat, complete prayer-drain terms, central hidden-brother
  attachment, mound-to-tunnel transition, chest formula,
  brother-order-independent early equipment rolls, full-condition reward
  instances, synthetic Combat-target cleanup on every exit path, Bob repair,
  death, migration, and runtime dispatch.
- `tests/test_equipment_instance_logic.py` continues to guard the older 20%
  Fist-of-Guthix identities while the Barrows suite proves 25% bands.
- `tests/test_main_menu_widget.py` exercises the real offscreen Qt activity
  card, including entry, selection, the complete fixed-size 3x3 tunnel map,
  repair, suspension, and the absence of a nested scroll area.
- `tests/test_skill_and_item_registry.py` pins Barrows to the Activities
  navigation surface.

No owner-facing design gap was found in this slice.
