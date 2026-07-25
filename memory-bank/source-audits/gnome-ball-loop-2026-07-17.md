# Gnome Ball at the pre-EOC cutoff

Date: 2026-07-17

Status: **horizontal breadth level one restored and verified on 2026-07-25;
the referee reward now follows the settled carry-then-bank loop, and every
unrecovered hidden roll remains explicitly source-blocked.**

## Pinned evidence

The literal wikitext of `Gnome Ball`, oldid `6404371`,
`2012-10-14T14:19:59Z`, establishes:

- the members activity is dangerous rather than safe;
- the player wins after scoring five goals against the gnome team;
- a shot may score or miss;
- gnome tackles cause LP damage;
- passing to green-armoured winger gnomes is optional;
- throwing the ball awards Ranged XP, while goals award both Ranged and
  Agility XP;
- the first through fifth goals award `4/5/6/7/5` XP in each goal skill, and
  the fifth adds a `25 XP` completion bonus; and
- after winning, the referee supplies a gnomeball, but another is not awarded
  while the previous reward remains carried; banking it permits another.

Source:

- <https://runescape.wiki/w/Gnome_Ball?oldid=6404371>

The revision was resolved and inspected as literal wikitext with
`tools/wiki_parity.py`. It does not state the scoring probability, tackle
probability, tackle damage, pass effects, or throw XP values needed for a
complete implementation.

## Owner-settled AnkiScape grouping

A match is three successful-review beats:

1. the opening beat resolves goals one and two;
2. the middle beat resolves goals three and four; and
3. the final beat resolves goal five, the completion bonus, and the referee
   reward.

Each beat is one bounded match slice, not an NPC simulation. It may narrate
passes, missed shots, and tackles, but it stores only the current beat, current
score, and player LP effects. The slice completes its named scoring milestone
unless the player's ordinary dangerous-activity death handling aborts the
match. No teammate, opponent, pathing, possession, or field state is advanced
between reviews.

This grouping deliberately preserves a short opening, escalation, and distinct
fifth-goal payoff while avoiding both a five-review throwaway minigame and a
single opaque match roll. The source goal XP is awarded at the beat containing
that goal. Any sourced throw XP must be folded into that same bounded result
rather than creating invisible per-throw replay.

An `Again` before a successful beat advances ordinary world state but does not
invent a tackle or score. Leaving explicitly abandons the match; ordinary death
also ends it. Undo restores the prior beat, score, LP, XP, and reward state
together.

The referee's gnomeball remains a real inventory reward. It is withheld while
one is carried, while banking the existing ball permits another source-shaped
reward on a later win.

## Still open for source harvest

- Resolve or mark `source_blocked` the scoring chance, tackle chance, tackle
  damage, passing effects, and throw XP.
- Reconcile the dangerous-activity death exit and equipment restrictions
  against independent period-lineage evidence.
- Corroborate the goal XP ladder, fifth-goal bonus, and gnomeball reward
  behavior.
- Fetch the ball, activity, and result assets from period evidence.

## 2026-07-21 source closure and implementation translation

This section supersedes the open-work bullets above and the older five-
possession wording in `agility-skill-contract-2026-07-15.md`. It does not
reopen the owner-settled three-successful-review match.

The cutoff activity revision remains the authority for the five goals, exact
Agility/Ranged XP ladder, dangerous tackles, and carried-only referee reward.
The three beats therefore award `9`, `13`, and `30` base XP to **both** skills.
Each beat deterministically reaches its named goal boundary unless tackle
damage kills the player; this keeps the sourced outcome shape without claiming
that the historical server used deterministic shots.

No pinned wiki dependency, dated archive, local 2011Scape implementation, or
Darkan server implementation recovered the score, pass, throw-XP, tackle-rate,
or tackle-damage rolls. They remain `source_blocked`. The live horizontal
translation uses the owner-approved Agility hidden-roll fallback once per beat:

```text
p_tackle = 0.20 - 0.15 * clamp((agility_level - 1) / 98, 0, 1)
damage = clamp(floor(current_lifepoints * 0.10), 10, 100)
```

A survived tackle applies damage and the beat still reaches its goal boundary.
A lethal tackle awards zero beat XP, invokes the shared dangerous grave/item-
loss channel, and ends the match. This formula is disclosed AnkiScape policy,
not a recovered historical server value.

### Entry, reward, and item identity

The focused activity page supplies no level, quest, item, or currency entry
gate. It also states that only the Gnomeball can be wielded in the arena; armour
and capes remain permitted. AnkiScape therefore blocks entry only while another
weapon occupies the weapon slot. A Gnomeball in the Bank does not block the
referee reward; one in the activity's carried pack or equipped weapon slot does.

`Gnomeball`, oldid `6151390`, timestamp `2012-08-27T00:52:25Z`, establishes a
members, tradeable, equipable, nonstackable weapon weighing `0.5 kg`:

- <https://runescape.wiki/w/Gnomeball?oldid=6151390>

OpenRS2 revision `742` preserves item `751` as `Gnomeball` with `Hold` and
`drop` options, and item `752` as its note. The local Darkan-derived item config
at `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:6367` also
preserves item `751`, tradeability, and weight, but contains no equipment block
and no server-side Gnome Ball implementation. It corroborates identity only.

`Talk:Gnome Ball`, oldid `4665291`, timestamp
`2011-08-25T23:39:09Z`, independently describes the dangerous item-loss death
consequence. Talk history is corroboration rather than the primary mechanic
source:

- <https://runescape.wiki/w/Talk:Gnome_Ball?oldid=4665291>

### Period asset and implementation boundary

`agilityitems/gnomeball.png` is the period item art, timestamp
`2012-09-10T01:40:40Z`, normalized to RGBA at no more than 64 px and recorded in
`assets_provenance.json`. The same asset supplies the 28 px Activities row/card
identity; no fabricated arena screenshot or result art is introduced.

The mechanic-complete horizontal slice owns Activities-only registration,
three-beat persistence and arbitration, explicit enter/leave, dangerous tackle
and grave behavior, exact dual-skill XP, carried-only reward handling, item and
equipment identity, schema-63 migration, cadence/multiplier stopping, whole-
answer undo, telemetry, compact paginated UI, and period asset coverage. Exact
hidden rolls and exhaustive arena narration are data-depth work rather than a
missing mechanic or design question.

Because tackles can deal real LP damage, entry also uses the established
target-specific carried-pack substrate. Auto mode fills owned food in the
player's saved auto-eat order; Custom materializes the saved ordered Gnome Ball
layout. The same target is exposed through Bank/Equipment pack controls and to
review-driven follower policies. This is shared dangerous-activity plumbing,
not a new Gnome Ball-specific inventory screen.

## 2026-07-25 carried-reward breadth correction

The earlier horizontal implementation checked the carried pack correctly but
credited a newly awarded Gnomeball only to the flat Bank inventory. That made
the next win eligible immediately and contradicted the settled source rule.
The correction closes both the acquisition consequence and its end-to-end test
coverage.

### Exact period evidence

- `Gnome Ball`, oldid `6404371`, says the referee gives the player a
  Gnomeball after the fifth goal and does not give another while the previous
  reward remains in the player's inventory; banking the reward permits another.
- `Gnomeball`, oldid `6151390`, and OpenRS2 revision `742` item `751` establish
  the nonstackable, equipable item identity used by the reward.
- The exact five-goal XP ladder, fifth-goal completion bonus, dangerous tackle
  shape, and weapon-slot entry restriction remain the pinned evidence recorded
  above. This correction changes none of them.

### Labelled AnkiScape translation

- `abstraction/shared-carried-substrate`: the flat `inventory` mapping is the
  add-on's canonical ownership store, while `carried_inventory` records which
  owned items are physically in a target's pack. A referee award therefore
  increments canonical ownership and the Gnome Ball carried projection in the
  same pure transition. It is not Bank-first merely because canonical ownership
  remains represented in the flat store.
- `abstraction/direct-bank-action`: the Activities card exposes **Bank
  Gnomeball** after a completed match. The undoable direct action removes the
  reward from the carried projection without changing canonical ownership, and
  clears a saved Custom-pack Gnomeball entry so the next entry cannot silently
  carry it again. Banking is rejected during a match or while another
  Gnomeball is wielded.
- `abstraction/reward-slot-reservation`: when no Gnomeball is already carried or
  wielded, entry caps the food/custom pack at `27` of the shared `28` slots so
  the sourced referee reward can always become the final carried item. If a ball
  already blocks the reward, the full `28` slots remain available.

### `source_blocked` values

- The historical full-inventory referee dialogue and exact no-space behavior
  were not recovered. Reserving one slot is the bounded horizontal translation;
  it does not claim a historical server rule.
- Scoring chance, pass effects, throw XP, tackle chance, and tackle damage remain
  source-blocked exactly as recorded above. The disclosed level-scaled tackle
  fallback is unchanged.

### Deferred data depth

Exhaustive arena narration, exact hidden rolls, and independent reconstruction
of the historical full-inventory dialogue remain parity-depth harvest. No
settled Gnome Ball mechanic and no owner design fork remains open at breadth
level one.

### Implemented and verified closure

The final reward is now acquired in the Gnome Ball carried pack, a second win
withholds the duplicate, the direct Bank action preserves Bank ownership while
restoring reward eligibility, and a later win awards a new carried ball. The
same transition rebuilds every nested mapping it owns, remains inside the
existing whole-answer/direct-action undo boundaries, and is surfaced on the
compact Activities card. Focused pure, dispatch, runtime undo, and real
offscreen-Qt interaction tests cover the complete carry, withhold, bank, and
re-award loop, including Auto and Custom packs that begin with 28 food slots.
The canonical non-Qt lane passes all `2,718` tests with `329` expected skips;
the real offscreen-Qt lane passes all `2,718` tests with one intentional skip.
