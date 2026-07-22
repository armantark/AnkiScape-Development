# Soul Wars horizontal readiness

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period game spine pinned; horizontal pure mechanics implemented; shared
storage/runtime/UI integration remains pending behind the active Castle Wars
writer.**

Owning design: `source-audits/competitive-tier-adaptations-2026-07-18.md`.
That settled Soul Wars as soul-fragment gathering and obelisk-control duty beats
against bounded opposing pressure, with the avatar represented by the shared
engaged-target pattern and Zeal XP rewards hidden. This audit pins the smallest
readily available period data set needed to exercise that contract end to end.

## Period pins

| Page | Revision | Timestamp | Used for |
|---|---:|---|---|
| Soul Wars | `6492038` | `2012-10-28T23:10:20Z` | entry rules, objective chain, fragments, obelisk, avatars, safe death, supplies, activity bar, outcome rewards |
| Zeal | `6016139` | `2012-07-30T16:05:49Z` | charm costs, pets, gamble boundary |
| Reward Shop (Soul Wars) | `6556242` | `2012-11-15T04:47:44Z` | Zeal cap, XP boundary, exact charm quantities by Combat band |

All three were resolved and read through `tools/wiki_parity.py`; each timestamp
precedes the cutoff.

## Sourced mechanic spine

From Soul Wars oldid `6492038`:

- Soul Wars is members-only but has no level or quest requirement.
- Players remove their cape before entering. Food and non-combat items cannot be
  taken onto the battlefield. Familiars are allowed, but cannot damage avatars.
- A game lasts twenty minutes. Teams win by defeating the opposing avatar more
  times than their own avatar is defeated.
- Both avatars are level `525`, start behind a Slayer requirement of `100`, and
  have `10,000` lifepoints.
- Pyrefiends require Slayer `30` and drop one soul fragment; jellies require
  Slayer `52` and drop two. Players below those gates can collect fragments
  dropped on the battlefield.
- Each fragment offered at a controlled Soul Obelisk lowers the opposing
  avatar's Slayer requirement by one. The obelisk and two graveyards are
  captured by having more team members in their bounds.
- Burying a bone in a controlled graveyard has about a `50%` chance to raise the
  friendly avatar's Slayer requirement by one and restores Prayer points.
- Death is safe. A dead player becomes a ghost, respawns at a controlled
  graveyard, loses temporary bones/supplies/fragments, and has lifepoints,
  Prayer, Summoning points, special attack, and run energy restored.
- The activity bar is replenished by real participation and death. Letting it
  empty removes the player with no Zeal.
- Victory pays `3` Zeal, a draw `2`, and defeat `1`. The wallet caps at `50,000`.

From Reward Shop oldid `6556242`:

- Gold, green, crimson, and blue charm bundles cost `4`, `5`, `12`, and `30`
  Zeal respectively.
- Combat level `12` or lower cannot buy charms.
- For the seven Combat bands `13–74`, `75–82`, `83–99`, `100–108`, `109–124`,
  `125–136`, and `137+`, gold bundles contain `6/14/24/34/41/47/52`, green
  `4/9/15/22/27/31/34`, crimson `4/9/15/22/26/30/34`, and blue
  `5/9/19/22/36/41/45` charms.

The reward page also pins level-scaled Zeal XP formulae, pets, and a two-Zeal
gamble. The owner-settled contract keeps XP redemption hidden; pets already have
their Summoning acquisition contract; gamble tables remain catalog depth. Exact
charm bundles are therefore the smallest source-ready shop slice.

## Disclosed horizontal translation

The source gives a twenty-minute clock but no stable count of consequential
player actions. AnkiScape never uses the wall clock for gameplay. The live match
therefore lasts twelve answered-card beats, matching the repository's bounded
team-assault scale without claiming that twelve was an historical action count.

One review advances both teams:

- the opposing team exerts bounded obelisk, fragment, and avatar pressure;
- Casual captures an uncontrolled obelisk, then gathers/offers fragments until
  the avatar is attackable, defends a critically injured friendly avatar, or
  attacks the enemy avatar;
- Advanced keeps the selected duty and visibly loses activity when an avatar
  attack is blocked by Slayer;
- productive fragment and avatar beats include disclosed competent-team crowd
  pressure, while the player's own fragments retain the exact one/two yields and
  each offered fragment retains its exact one-level effect;
- the avatar is the engaged target for one live six-tick Combat slice; the
  rest of each team is collapsed into bounded pressure, which is explicitly
  allowed by `multi-enemy-encounter-contract-2026-07-18.md`;
- three consecutive non-participating beats empty the bounded activity bar and
  remove the player for zero Zeal; and
- the twelfth beat compares avatar defeats and pays the exact `3/2/1` outcome.

The provisional pressure values are named in `soul_wars_data.py`. They are
mechanical abstractions, not historical rate claims.

## Implemented pure boundary

`soul_wars_data.py`, `soul_wars_logic.py`, and `tests/test_soul_wars.py` now cover:

- unrestricted level/quest entry, persistent-session arbitration, cape and
  carried-food exclusions, and allowed familiars;
- Casual and Advanced policy, team selection, exact fragment gates/yields,
  obelisk control, bone defence, Prayer restoration, activity removal, and
  productive/Again advancement;
- live six-tick avatar combat, safe death, temporary-fragment loss, resource
  restoration, avatar resets and score, exact outcome Zeal, wallet cap, and
  leave forfeiture; and
- exact Combat-band charm bundle purchases using existing Summoning charm items.

Shared registry/storage/runtime/cadence/undo/UI/assets integration is intentionally
not included in this checkpoint because another writer currently owns those
files for Castle Wars. The isolated files are safe to commit independently.

## Source blocks and deferred depth

- The twelve-review budget and all team-pressure magnitudes are disclosed
  abstractions because the period page provides time and objectives, not action
  rates.
- Exact avatar attack speed and maximum hit were not recovered from the pinned
  page. The engaged-avatar enemy uses bounded Combat values and does not claim
  them as historical.
- The exact amount of Prayer restored by one buried bone was not recovered; the
  horizontal slice restores one displayed Prayer point (`10` internal units).
- Exact late-join handling, waiting-room priority, minimum team population,
  hybrid-armour chance, the full gamble distribution, every pet sacrifice, and
  Zeal XP redemption are later catalog/presentation depth rather than missing
  core match mechanics.
- No owner-design conflict surfaced.
