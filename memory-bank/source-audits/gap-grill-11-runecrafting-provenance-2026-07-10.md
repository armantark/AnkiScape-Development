# Gap Grill 11: Runecrafting Provenance

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Pinned period evidence

- `Ourania Runecrafting Altar` oldid 6448353, 2012-10-21: Pure essence only;
  no talisman, rune-level, or quest requirement; one random rune per essence;
  twice normal rune XP; higher Runecrafting biases higher rune output; 20 runes
  per Eniola bank access; short dangerous and long safe routes. The page gives
  approximate average XP per essence at a few levels but not the complete
  server-side rune probability table.
- `Wicked hood` oldid 6564747, 2012-11-17: manual Essence, Rune, and altar
  Teleport functions; 100 baseline essence, one baseline rune withdrawal with
  an Elemental-talisman second use, and two altar teleports; Runespan outfit
  upgrades reach 175 essence, five rune withdrawals, and three teleports; fed
  talisman/tiara access, Omni pure-essence conversion, unlimited Guild/Runespan
  teleport, one-hood ownership, and reclaim preserving hood progress.
- `Talk:Wicked hood` oldid 6341451, 2012-10-03: a contemporaneous answer records
  the daily timer reset at 00:00 GMT rather than 24 hours after first use.
- `Elemental talisman` oldid 6358346, 2012-10-06: the members-only,
  tradeable talisman gives access to the Air, Water, Earth, and Fire altars.
- `Omni-talisman` oldid 6359046, 2012-10-06: Wizard Elriss requires level 50
  Runecrafting and one of each of the twelve regular talismans or tiaras. She
  does not consume them. The first claim gives 13,605 Runecrafting XP, and
  later replacement claims do not require the set again.
- `Omni-tiara` oldid 6130195, 2012-08-23: Wizard Korvak combines an
  Omni-talisman with a Tiara. The resulting Omni-tiara can feed the hood.

The daily reset is implemented against AnkiScape's existing answered-card
market clock rather than the computer clock: 240 answered cards equal one
simulated day. The hood refills to its current cap at that boundary without
stacking unused allowances; any answered card advances time and undo rolls it
back.
- `The Great Orb Project` oldid 6564759, 2012-11-17: level 50; multiplayer teams;
  sequential altar rounds; orb attraction/repulsion and barriers; participation
  meter; round essence; double-XP crafting; win/loss/tie and majority token
  awards; and a distinct token shop for outfits, talismans, staves, teleport
  tablets, and essence.

All claims were read from the literal archived wikitext with
`tools/wiki_parity.py`. Modern RS3 and OSRS behavior was not used as parity
evidence.

## Evidence boundary

The period Ourania page does not expose the exact level-weighted rune roll
table, short-route damage rolls, or Ardougne-cloak bonus probability. Those
mechanics remain source-blocked pending a literal period dependency, cache-
corroborated script, or reconciled high-fidelity server implementation.

Great Orb Project is sufficiently sourced as an activity family, but its
AnkiScape opponent/team simulation is a product-design problem and is deferred
to the separate minigame/activity pass rather than guessed inside this grill.

## Wicked hood horizontal implementation harvest (2026-07-21)

The pinned `Wicked hood` revision is sufficient for the small live data set:

- the baseline daily pool is 100 essence, one rune withdrawal, and two altar
  teleports;
- Air, Mind, Water, Earth, Fire, and Body withdrawals produce 100 runes, while
  Cosmic, Chaos, Astral, Nature, Law, Death, and Blood produce five;
- feeding an Elemental talisman unlocks the four elemental altars and adds one
  rune withdrawal;
- an Omni-talisman or Omni-tiara unlocks every altar and converts the essence
  action to Pure essence;
- each Wicked cape/top/legs upgrade adds 25 essence and one rune withdrawal,
  while the complete three-piece outfit also adds one teleport, producing caps
  of 175 essence, five rune withdrawals, and three teleports.

The oldid gives one whole training route, not separately timed return,
bank/load, and outbound legs. AnkiScape therefore preserves the already-sourced
whole-route review count, assigns one review to bank/load, divides the remaining
reviews as evenly as possible between return and outbound, and lets the hood
remove only the outbound tail. This is a labeled bounded abstraction; it does
not replace or lower the underlying route rate.

Rune and Pure essence are explicitly non-stackable in the carried-pack model.
The Darkan name-level cache dump also contains a stackable technical identity
collapsed to `Rune essence`; player-facing metadata overrides that collision so
one essence still occupies one inventory slot.

The Elemental talisman remains correctly tradeable, but its cutoff Grand
Exchange buy limit is not in the pinned GE table. It therefore joins the
explicit buy-limit-blocked catalog instead of receiving an invented limit; the
already-live Great Orb Project reward shop remains its complete acquisition
route for this horizontal slice.

The representative Great Orb reward shop now closes the remaining hood feeds.
Wizard Elriss sells the Elemental talisman for 125 tokens. The first
Omni-talisman claim checks all twelve regular access items without consuming
them and awards 13,605 Runecrafting XP exactly once. Replacement claims remain
available after the item is lost or consumed. Wizard Korvak then converts an
Omni-talisman and a Tiara into an Omni-tiara. Period quest rewards and the
Grand Exchange already provide the otherwise exceptional Death and Blood
talismans, so the claim gate is reachable without invented shortcuts.

The three Runespan outfit upgrades remain data depth because the Runespan
reward shop is not live. Their allowance effects are already represented in
the hood state and apply as soon as that period acquisition route exists. This
does not block the baseline hood, Elemental feed, Omni feed, manual resources,
teleport, daily reset, loss, or reclaim mechanics.
